'''Self-tests for plan 107's micro-test kit, on synthetic records and folders. No test runs a model.

The runner tests start a stub claude (a bash script given as CLAUDE_BIN) with every root, scratch and
fixture path moved into the test's temporary folder (the WST_* variables). A runner starts the stub under
`env -i`, so every path the stub needs is written into its text. The audit, sheet and trigger tests call
the kit's Python in-process, on synthetic records. Sources: plan 105's kit tests
(specs/baseline/red-baseline-writing-skills-layout/kit/test_wsl_kit.py), renamed, with the tests that
plan 107's Task 1 adds: the three closed Glob limits, the Bash audit, the trigger runner and its reader,
the R3 tree check, the reference reads and the plan 107 bars.
'''
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

import pytest

import audit
import cases
import sheets

KIT = Path(__file__).resolve().parent
PLAN104_PROBE = KIT.parents[1] / 'red-baseline-mutant-screen-runs' / 'kit' / 'isolation_probe.txt'
RUN_TOOLS = KIT / 'run_tool_reps.sh'
RUN_TRIGGERS = KIT / 'run_trigger_reps.sh'
PROBE_TOOLS = KIT / 'probe_tools.sh'
SONNET, OPUS = 'claude-sonnet-5-5', 'claude-opus-5-5'
FIELD = 'credential_expires_at'
TOOLS = 'Read,Glob,Grep,Edit,Write'
R3_TOOLS = 'Read,Glob,Grep,Edit,Write,Bash'
R3_ALLOWED = 'Read,Glob,Grep,Edit,Write,Bash(git mv *)'
TRIGGER_TOOLS = 'Read,Glob,Grep,Skill'
CROSS_SESSION_TOOLS = ('ListAgents', 'SendMessage', 'PushNotification', 'RemoteTrigger')
PATH_RULES = ('Read(//Users/**)', 'Edit(//Users/**)', 'Write(//Users/**)', 'Read(~/Library/**)',
              'Edit(~/Library/**)', 'Write(~/Library/**)')
SHELL_ADDED = {'PWD', 'SHLVL', '_', 'OLDPWD'}
KEEP = ('HOME', 'USER', 'LOGNAME', 'PATH', 'SHELL', 'TMPDIR', 'LANG')
DISABLE = ('CLAUDE_CODE_DISABLE_ADVISOR_TOOL', 'CLAUDE_CODE_DISABLE_AUTO_MEMORY')
REP_DIR = '/private/tmp/wst107/rep1'
SKILL_ROOT = '/private/tmp/wst107-skill'
SKILL = f'{SKILL_ROOT}/writing-skills'
TREP_DIR = '/private/tmp/wst107t/rep1'
COMPETITORS = ('skill-development', 'skill-creator')


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(cmd: list[str], env: dict | None = None, cwd: Path = KIT, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, env=env, cwd=cwd, capture_output=True, text=True, check=False, timeout=timeout)


def kit_tool(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return run(['uv', 'run', '--no-project', '-q', 'python', *args], env=env)


# --- common.sh, run_tool_reps.sh and probe_tools.sh: plan 105's runner tests, renamed ------------------------

TOOL_STUB = r'''#!/bin/bash
log='@DIR@/calls.log'
printf '%s\n' "$*" >> "$log"
n=$(wc -l < "$log" | tr -d ' ')
cat > '@DIR@'/stdin.$n
printf '%s\n' "$@" > '@DIR@'/args.$n
env > '@DIR@'/env.$n
if [ -f '@DIR@'/actions.sh ]; then . '@DIR@'/actions.sh; fi
printf '{"type":"system","subtype":"init","cwd":"%s","tools":["Read","Glob","Grep","Edit","Write"],' "$PWD"
printf '"skills":["writing-skills","skill-development","skill-creator"],'
printf '"model":"claude-sonnet-5-5","credential_expires_at":1790000000}\n'
printf '{"type":"assistant","message":{"content":[{"type":"text","text":"Done."}]}}\n'
if [ -f '@DIR@'/extra_lines ]; then cat '@DIR@'/extra_lines; fi
printf '{"type":"result","subtype":"success","is_error":false,"result":"Done.","num_turns":1,'
printf '"total_cost_usd":0.01,"credential_expires_at":1790000000,'
printf '"modelUsage":{"claude-sonnet-5-5":{"costUSD":0.01,"credential_expires_at":1790000000}}}\n'
'''
TOOL_ENV = set(KEEP) | set(DISABLE)


class ToolKit:
    '''One test's temporary world for the case runner.'''

    def __init__(self, tmp: Path) -> None:
        self.tmp = tmp
        self.real = tmp / 'real'
        (self.real / 'Library' / 'Keychains').mkdir(parents=True)
        self.root = tmp / 'root'
        self.scratch = tmp / 'scratch'
        self.fixtures = tmp / 'fixtures'
        self.skill = tmp / 'skill'
        self.stub_dir = tmp / 'stub'
        self.stub_dir.mkdir()
        self.stub = self.stub_dir / 'claude'
        self.stub.write_text(TOOL_STUB.replace('@DIR@', str(self.stub_dir)))
        self.stub.chmod(0o755)
        self.prompts = tmp / 'prompts'

    def fixture(self, name: str = 'T2', arm: str = 'old') -> None:
        repo = self.fixtures / name / 'repo'
        (repo / 'specs').mkdir(parents=True)
        (repo / 'notes.txt').write_text('first line\n')
        (repo / 'specs' / '.gitkeep').write_text('')
        copy = self.skill / 'writing-skills'
        (copy / 'references').mkdir(parents=True, exist_ok=True)
        (copy / 'SKILL.md').write_text('# Writing Skills\n')
        (copy / 'references' / 'flowcharts.md').write_text('# Flowcharts\n')
        self.prompts.mkdir(exist_ok=True)
        prompt = self.prompts / f'{name}.txt'
        prompt.write_text('Do the task.\n')
        lines = ['ref aaaaaaa', f'arm {arm}', f'skill-copy-root {self.skill}']
        for path in sorted(p for p in self.skill.rglob('*') if p.is_file()):
            rel = path.relative_to(self.skill)
            lines.append(f'skill-copy {rel} {sha256(path.read_bytes())} skills/{rel}@aaaaaaa')
        lines.append(f'prompt {prompt.name} {sha256(prompt.read_bytes())}')
        (self.prompts / 'MANIFEST.txt').write_text('\n'.join(lines) + '\n')

    def env(self) -> dict:
        user = os.environ.get('USER') or 'tester'
        return {'HOME': str(self.real), 'USER': user, 'LOGNAME': user, 'PATH': os.environ['PATH'],
                'SHELL': '/bin/bash', 'LANG': 'C', 'WST_ROOT': str(self.root), 'WST_SCRATCH': str(self.scratch),
                'WST_FIXTURES': str(self.fixtures), 'CLAUDE_BIN': str(self.stub)}

    def out(self, name: str = 'T2', arm: str = 'old', model: str = SONNET) -> Path:
        return self.tmp / 'out' / name / arm / model

    def run(self, name: str = 'T2', first: int = 1, last: int = 1, model: str = SONNET, out: Path | None = None
            ) -> subprocess.CompletedProcess:
        return run(['/bin/bash', str(RUN_TOOLS), str(self.prompts), name, str(out or self.out(name, model=model)),
                    str(first), str(last), model], env=self.env(), cwd=self.tmp)

    def probe(self, model: str = SONNET) -> subprocess.CompletedProcess:
        return run(['/bin/bash', str(PROBE_TOOLS), model, str(self.tmp / 'probes' / 'probe.jsonl')], env=self.env(),
                   cwd=self.tmp)

    def actions(self, text: str) -> None:
        (self.stub_dir / 'actions.sh').write_text(text)

    def calls(self) -> list[str]:
        log = self.stub_dir / 'calls.log'
        return log.read_text().splitlines() if log.exists() else []

    def args(self, n: int = 1) -> list[str]:
        return (self.stub_dir / f'args.{n}').read_text().splitlines()

    def summary(self, rep: int = 1, name: str = 'T2') -> dict:
        return json.loads((self.out(name) / f'rep{rep}' / 'summary.json').read_text())

    def stream(self, rep: int = 1, name: str = 'T2') -> Path:
        return self.scratch / name / 'old' / SONNET / f'rep{rep}.jsonl'


@pytest.fixture
def tkit(tmp_path: Path) -> ToolKit:
    made = ToolKit(tmp_path)
    made.fixture()
    return made


def tools_ok(tkit: ToolKit, **kwargs) -> subprocess.CompletedProcess:
    done = tkit.run(**kwargs)
    assert done.returncode == 0, done.stdout + done.stderr
    return done


def test_second_rep_sees_nothing_of_first(tkit):
    listing = tkit.tmp / 'listing.txt'
    tkit.actions(
        'case "$PWD" in\n'
        '  */rep1/*) for d in "$HOME" "$TMPDIR" "$PWD"; do echo x > "$d/MARKER-ONE"; done ;;\n'
        f'  *) ls -laR \'{tkit.root}\' "$HOME" "$TMPDIR" >> \'{listing}\' 2>&1 ;;\n'
        'esac\n')
    tools_ok(tkit, first=1, last=2)
    text = listing.read_text()
    assert 'rep2' in text
    assert 'MARKER-ONE' not in text
    assert 'rep1' not in text
    parked = tkit.scratch / 'T2' / 'old' / SONNET / 'rep1-folder'
    assert (parked / 'home' / 'MARKER-ONE').is_file()
    assert (parked / 'tmp' / 'MARKER-ONE').is_file()
    assert os.listdir(tkit.root) == []


def test_refuses_a_nonempty_rep_root(tkit):
    tkit.root.mkdir()
    (tkit.root / 'stray').write_text('x\n')
    done = tkit.run()
    assert done.returncode == 3, done.stdout + done.stderr
    assert 'not empty' in done.stdout + done.stderr
    assert tkit.calls() == []


def test_strip_removes_credential_field_everywhere(tkit):
    tools_ok(tkit)
    rep = tkit.out() / 'rep1'
    files = [p for p in rep.rglob('*') if p.is_file()] + [tkit.stream()]
    assert len(files) > 2
    assert [str(p) for p in files if FIELD in p.read_text(errors='replace')] == []
    summary = tkit.summary()
    assert summary['result']['total_cost_usd'] == 0.01
    assert 'kit_error' not in summary


def test_a_field_left_in_a_written_file_is_a_kit_error(tkit):
    # The strip rewrites JSON only, so a rep that writes the field into its repository leaves it in final.diff.
    tkit.actions(f"printf '{FIELD}: 1790000000\\n' >> notes.txt\n")
    done = tkit.run(first=1, last=2)
    assert done.returncode == 2, done.stdout + done.stderr
    error = tkit.summary()['kit_error']
    assert f'the strip left {FIELD} in:' in error and 'final.diff' in error, error
    assert len(tkit.calls()) == 1
    assert 'kit error, so the batch stops' in done.stdout


@pytest.mark.parametrize('change', ['edit', 'add'])
def test_runner_refuses_a_changed_skill_copy(tkit, change):
    copy = tkit.skill / 'writing-skills'
    if change == 'edit':
        (copy / 'references' / 'flowcharts.md').write_text('# Flowcharts, edited\n')
    else:
        (copy / 'references' / 'extra.md').write_text('left by another build\n')
    done = tkit.run()
    assert done.returncode == 2, done.stdout + done.stderr
    assert 'skill copy' in done.stdout + done.stderr
    assert tkit.calls() == []


@pytest.mark.parametrize('model', [SONNET, OPUS])
def test_settings_deny_the_cross_session_tools(tkit, model):
    tools_ok(tkit, model=model, out=tkit.out(model=model))
    args = tkit.args()
    settings = json.loads(args[args.index('--settings') + 1])
    deny = settings['permissions']['deny']
    assert set(CROSS_SESSION_TOOLS) <= set(deny)
    assert set(PATH_RULES) <= set(deny)
    assert settings['syncClaudeAiSkills'] is False
    assert args[args.index('--tools') + 1] == TOOLS
    assert args[args.index('--allowedTools') + 1] == TOOLS
    assert args[args.index('--model') + 1] == model
    assert args[args.index('--max-budget-usd') + 1] == '1.50'
    assert args[args.index('--output-format') + 1] == 'stream-json'
    for flag in ('--strict-mcp-config', '--disable-slash-commands', '--no-session-persistence', '--verbose', '-p'):
        assert flag in args
    assert args[args.index('--setting-sources') + 1] == ''


def test_r3_reps_get_bash_limited_to_git_mv_and_the_other_cases_do_not(tmp_path):
    for case, tools, allowed in (('R3', R3_TOOLS, R3_ALLOWED), ('M1', TOOLS, TOOLS), ('T2', TOOLS, TOOLS)):
        kit = ToolKit(tmp_path / case)
        kit.fixture(case)
        tools_ok(kit, name=case)
        args = kit.args()
        assert args[args.index('--tools') + 1] == tools, case
        assert args[args.index('--allowedTools') + 1] == allowed, case


def test_an_r3_summary_holds_the_tree_check_of_the_finished_repository_and_no_other_case_does(tmp_path):
    for verdict, extra in (('PASS', ''), ('FAIL', 'echo csv-dialect-sniff > left.txt;')):
        kit = ToolKit(tmp_path / verdict)
        kit.fixture('R3')
        kit.actions('mkdir -p skills/sniffing-csv-dialects; '
                    'printf -- "---\\nname: sniffing-csv-dialects\\n---\\n" > skills/sniffing-csv-dialects/SKILL.md; '
                    + extra + '\n')
        tools_ok(kit, name='R3')
        check = kit.summary(name='R3')['r3_check']
        assert check['verdict'] == verdict, check
        assert (check['problems'] == []) == (verdict == 'PASS')
    other = ToolKit(tmp_path / 'other')
    other.fixture('M1')
    tools_ok(other, name='M1')
    assert 'r3_check' not in other.summary(name='M1')


def test_rep_env_holds_only_the_pinned_names(tkit):
    tools_ok(tkit)
    env = dict(line.split('=', 1) for line in (tkit.stub_dir / 'env.1').read_text().splitlines() if '=' in line)
    assert set(env) - SHELL_ADDED <= TOOL_ENV
    folder = os.path.realpath(tkit.root / 'rep1')
    assert env['HOME'] == f'{folder}/home'
    assert env['TMPDIR'] == f'{folder}/tmp'
    assert env['PATH'] == '/usr/bin:/bin:/usr/sbin:/sbin'
    assert env['CLAUDE_CODE_DISABLE_AUTO_MEMORY'] == '1'
    assert os.readlink(tkit.scratch / 'T2' / 'old' / SONNET / 'rep1-folder' / 'home' / 'Library'
                       / 'Keychains') == str(tkit.real / 'Library' / 'Keychains')


def test_the_rep_starts_in_its_fixture_committed_as_base(tkit):
    tkit.actions(f'git log --format=%s > \'{tkit.tmp}/log.txt\'; ls -A > \'{tkit.tmp}/ls.txt\'\n')
    tools_ok(tkit)
    assert (tkit.tmp / 'log.txt').read_text() == 'Start the project\n'
    assert sorted((tkit.tmp / 'ls.txt').read_text().split()) == ['.git', 'notes.txt', 'specs']
    summary = tkit.summary()
    assert len(summary['base']) == 40
    assert summary['case'] == 'T2' and summary['arm'] == 'old' and summary['model'] == SONNET
    assert 'condition' not in summary
    # summary.json is scrubbed, and the scrub writes pytest-of-<user> as pytest-of-$USER.
    user = os.environ.get('USER') or 'tester'
    assert summary['skill_root'] == str(tkit.skill).replace(f'pytest-of-{user}', 'pytest-of-$USER')
    assert (tkit.scratch / 'T2' / 'old' / SONNET / 'rep1.prompt.txt').read_text() == 'Do the task.\n'


@pytest.mark.parametrize('where', ['case', 'arm', 'model'])
def test_refuses_an_out_dir_that_misnames_the_case_arm_or_model(tkit, where):
    names = {'case': 'T2', 'arm': 'old', 'model': SONNET}
    names[where] = {'case': 'M1', 'arm': 'new', 'model': OPUS}[where]
    done = tkit.run(out=tkit.tmp / 'out' / names['case'] / names['arm'] / names['model'])
    assert done.returncode == 2, done.stdout + done.stderr
    assert tkit.calls() == []


def test_refuses_a_model_outside_the_plan(tkit):
    done = tkit.run(model='claude-haiku-5-5', out=tkit.out(model='claude-haiku-5-5'))
    assert done.returncode == 2, done.stdout + done.stderr
    assert tkit.calls() == []


def test_a_non_json_stream_line_is_a_kit_error(tkit):
    (tkit.stub_dir / 'extra_lines').write_text('{"type":"user","message":{"content":[]}}\nnot a record\n')
    done = tkit.run()
    assert done.returncode == 2, done.stdout + done.stderr
    summary = tkit.summary()
    assert 'not JSON' in summary['kit_error']
    assert summary['result']['total_cost_usd'] == 0.01


@pytest.mark.parametrize('line', ['[1, 2]', '3', '"text"', 'null'])
def test_a_stream_line_that_is_json_but_not_an_object_is_a_kit_error(tkit, line):
    (tkit.stub_dir / 'extra_lines').write_text(line + '\n')
    done = tkit.run()
    assert done.returncode == 2, done.stdout + done.stderr
    assert 'not JSON' in tkit.summary()['kit_error']


def test_final_diff_holds_new_and_changed_files_against_base(tkit):
    tkit.actions('echo second line >> notes.txt; printf "# Design\\n" > specs/new-design.md\n')
    tools_ok(tkit)
    diff = (tkit.out() / 'rep1' / 'final.diff').read_text()
    assert '+second line' in diff
    assert 'specs/new-design.md' in diff and '+# Design' in diff
    assert tkit.summary()['status_porcelain'] != []


def test_summary_marks_each_failed_tool_call(tkit):
    use = {'type': 'tool_use', 'id': 't1', 'name': 'Read', 'input': {'file_path': '/nowhere/discovery.md'}}
    done = {'type': 'tool_result', 'tool_use_id': 't1', 'content': 'File does not exist.', 'is_error': True}
    (tkit.stub_dir / 'extra_lines').write_text(
        json.dumps({'type': 'assistant', 'message': {'content': [use]}}) + '\n'
        + json.dumps({'type': 'user', 'message': {'content': [done]}}) + '\n')
    tools_ok(tkit)
    [call] = tkit.summary()['tool_calls']
    assert call['name'] == 'Read' and call['is_error'] is True


def test_probe_tools_runs_claude_as_a_rep_does(tkit):
    tools_ok(tkit)
    done = tkit.probe()
    assert done.returncode == 0, done.stdout + done.stderr
    assert tkit.args(2) == tkit.args(1)
    assert (tkit.stub_dir / 'stdin.2').read_text() == (KIT / 'isolation_probe.txt').read_text()
    assert FIELD not in (tkit.tmp / 'probes' / 'probe.jsonl').read_text()
    assert os.listdir(tkit.root) == []


def test_the_probe_is_plan_104s_eight_question_probe():
    assert (KIT / 'isolation_probe.txt').read_bytes() == PLAN104_PROBE.read_bytes()


# --- run_trigger_reps.sh --------------------------------------------------------------------------------------

TRIGGER_SKILLS = ('writing-skills', 'table-diff')


class TriggerKit(ToolKit):
    '''One test's temporary world for the trigger runner: a repository with skills/, two competitor folders.'''

    def __init__(self, tmp: Path) -> None:
        super().__init__(tmp)
        self.troot = tmp / 'troot'
        self.tscratch = tmp / 'tscratch'
        self.repo = tmp / 'srcrepo'
        for name in TRIGGER_SKILLS:
            (self.repo / 'skills' / name).mkdir(parents=True)
            (self.repo / 'skills' / name / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: Use when {name}\n---\n')
        (self.repo / 'specs').mkdir()
        (self.repo / 'specs' / 'plan.md').write_text('the plan, which no rep may read\n')
        git = ['git', '-C', str(self.repo), '-c', 'user.name=t', '-c', 'user.email=t@example.invalid',
               '-c', 'commit.gpgsign=false']
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        subprocess.run(git + ['add', '-A'], check=True)
        subprocess.run(git + ['commit', '-q', '-m', 'start'], check=True)
        self.sha = subprocess.run(['git', '-C', str(self.repo), 'rev-parse', 'HEAD'], capture_output=True, text=True
                                  ).stdout.strip()
        self.comp = {}
        for name in COMPETITORS:
            folder = tmp / 'plugins' / name
            (folder / 'references').mkdir(parents=True)
            (folder / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: Competitor {name}\n---\n')
            (folder / 'references' / 'more.md').write_text('more\n')
            self.comp[name] = folder
        fixture = self.fixtures / 'trigger' / 'repo'
        (fixture / 'skills' / 'table-diff').mkdir(parents=True)
        (fixture / 'skills' / 'table-diff' / 'SKILL.md').write_text('---\nname: table-diff\ndescription: d\n---\n')
        (fixture / 'README.md').write_text('A fixture project.\n')

    def env(self) -> dict:
        return {**super().env(), 'WST_TROOT': str(self.troot), 'WST_TRIGGER_SCRATCH': str(self.tscratch),
                'WST_REPO': str(self.repo), 'WST_COMPETITOR_PLUGIN_DEV': str(self.comp['skill-development']),
                'WST_COMPETITOR_SKILL_CREATOR': str(self.comp['skill-creator'])}

    def tout(self, prompt: str = 'P1', arm: str = 'old', condition: str = 'full', model: str = SONNET) -> Path:
        return self.tmp / 'tout' / prompt / arm / condition / model

    def trun(self, prompt: str = 'P1', arm: str = 'old', condition: str = 'full', first: int = 1, last: int = 1,
             model: str = SONNET, ref: str | None = None, out: Path | None = None, env: dict | None = None
             ) -> subprocess.CompletedProcess:
        out = out or self.tout(prompt, arm, condition, model)
        return run(['/bin/bash', str(RUN_TRIGGERS), ref or self.sha, arm, condition, prompt, str(out), str(first),
                    str(last), model], env=env or self.env(), cwd=self.tmp)


@pytest.fixture
def trig(tmp_path: Path) -> TriggerKit:
    return TriggerKit(tmp_path)


def trigger_ok(trig: TriggerKit, **kwargs) -> subprocess.CompletedProcess:
    done = trig.trun(**kwargs)
    assert done.returncode == 0, done.stdout + done.stderr
    return done


def snapshot_home(trig: TriggerKit) -> None:
    trig.actions(f'cp "$HOME/.claude/settings.json" \'{trig.tmp}/settings.json\'\n'
                 f'ls "$HOME/.claude/skills" > \'{trig.tmp}/skills.txt\'\n'
                 f'ls "$HOME/.claude" > \'{trig.tmp}/claude.txt\'\n'
                 f'ls -A > \'{trig.tmp}/repo.txt\'\n')


@pytest.mark.parametrize('condition', ['full', 'cut150'])
def test_trigger_runner_writes_cut150_settings(trig, condition):
    snapshot_home(trig)
    trigger_ok(trig, condition=condition)
    settings = json.loads((trig.tmp / 'settings.json').read_text())
    assert settings['skillListingBudgetFraction'] == 0.05
    assert settings['syncClaudeAiSkills'] is False
    assert set(PATH_RULES) <= set(settings['permissions']['deny'])
    assert set(CROSS_SESSION_TOOLS) <= set(settings['permissions']['deny'])
    if condition == 'cut150':
        assert settings['skillListingMaxDescChars'] == 150
    else:
        assert 'skillListingMaxDescChars' not in settings
    assert '"skillListingBudgetFraction": 0.05' in (trig.tmp / 'settings.json').read_text() \
        or '"skillListingBudgetFraction":0.05' in (trig.tmp / 'settings.json').read_text()


def test_trigger_runner_refuses_non_empty_root(trig):
    trig.troot.mkdir()
    (trig.troot / 'stray').write_text('x\n')
    done = trig.trun()
    assert done.returncode == 3, done.stdout + done.stderr
    assert 'not empty' in done.stdout + done.stderr
    assert trig.calls() == []


def test_trigger_runner_lists_the_arms_skills_and_both_competitors(trig):
    snapshot_home(trig)
    trigger_ok(trig)
    assert (trig.tmp / 'skills.txt').read_text().split() == ['skill-creator', 'skill-development', 'table-diff',
                                                             'writing-skills']
    # `git archive <ref> skills/` lands in .claude/, so there is no .claude/skills/skills.
    assert 'skills' in (trig.tmp / 'claude.txt').read_text().split()
    parked = trig.tscratch / 'P1' / 'old' / 'full' / SONNET / 'rep1-folder'
    assert (parked / 'home' / '.claude' / 'skills' / 'writing-skills' / 'SKILL.md').is_file()
    assert not (parked / 'home' / '.claude' / 'skills' / 'skills').exists()
    assert (parked / 'home' / '.claude' / 'skills' / 'skill-creator' / 'references' / 'more.md').is_file()
    # Only skills/ of the ref reaches the rep: no specs/ file.
    assert not any('plan.md' in str(p) for p in parked.rglob('*'))


def test_trigger_runner_places_the_ref_it_was_given(trig):
    (trig.repo / 'skills' / 'table-diff' / 'SKILL.md').write_text('---\nname: table-diff\ndescription: changed\n---\n')
    subprocess.run(['git', '-C', str(trig.repo), '-c', 'user.name=t', '-c', 'user.email=t@example.invalid',
                    '-c', 'commit.gpgsign=false', 'commit', '-qam', 'second'], check=True)
    trigger_ok(trig)
    parked = trig.tscratch / 'P1' / 'old' / 'full' / SONNET / 'rep1-folder'
    assert 'changed' not in (parked / 'home' / '.claude' / 'skills' / 'table-diff' / 'SKILL.md').read_text()


def test_trigger_runner_flags_and_env(trig):
    trigger_ok(trig, model=OPUS)
    args = trig.args()
    assert args[args.index('--tools') + 1] == TRIGGER_TOOLS
    assert args[args.index('--allowedTools') + 1] == TRIGGER_TOOLS
    assert args[args.index('--setting-sources') + 1] == 'user'
    assert args[args.index('--max-turns') + 1] == '3'
    assert args[args.index('--max-budget-usd') + 1] == '0.25'
    assert args[args.index('--output-format') + 1] == 'stream-json'
    assert args[args.index('--model') + 1] == OPUS
    for flag in ('--strict-mcp-config', '--no-session-persistence', '--verbose', '-p'):
        assert flag in args
    # The listing is the condition under test, so neither flag may hide it.
    assert '--disable-slash-commands' not in args and '--settings' not in args
    env = dict(line.split('=', 1) for line in (trig.stub_dir / 'env.1').read_text().splitlines() if '=' in line)
    assert set(env) - SHELL_ADDED <= TOOL_ENV
    assert env['CLAUDE_CODE_DISABLE_AUTO_MEMORY'] == '1'
    folder = os.path.realpath(trig.troot / 'rep1')
    assert env['HOME'] == f'{folder}/home' and env['PATH'] == '/usr/bin:/bin:/usr/sbin:/sbin'
    prompt = (trig.stub_dir / 'stdin.1').read_text()
    import trigger_prompts
    assert prompt == trigger_prompts.PROMPTS['P1'] + '\n' or prompt == trigger_prompts.PROMPTS['P1']


def test_trigger_rep_starts_in_the_trigger_fixture_and_writes_a_summary(trig):
    snapshot_home(trig)
    trigger_ok(trig, condition='cut150', prompt='N2')
    assert sorted((trig.tmp / 'repo.txt').read_text().split()) == ['.git', 'README.md', 'skills']
    summary = json.loads((trig.tout('N2', condition='cut150') / 'rep1' / 'summary.json').read_text())
    assert summary['case'] == 'N2' and summary['condition'] == 'cut150' and summary['arm'] == 'old'
    assert summary['model'] == SONNET and len(summary['base']) == 40
    stream = trig.tscratch / 'N2' / 'old' / 'cut150' / SONNET / 'rep1.jsonl'
    assert stream.is_file() and FIELD not in stream.read_text()
    assert os.listdir(trig.troot) == []


@pytest.mark.parametrize('how', ['unset-dev', 'unset-creator', 'no-folder-dev', 'no-folder-creator',
                                 'no-skill-md-dev', 'no-skill-md-creator'])
def test_trigger_runner_refuses_a_missing_competitor_before_it_makes_anything(trig, how):
    variable = 'WST_COMPETITOR_PLUGIN_DEV' if how.endswith('dev') else 'WST_COMPETITOR_SKILL_CREATOR'
    name = 'skill-development' if how.endswith('dev') else 'skill-creator'
    env = trig.env()
    if how.startswith('unset'):
        del env[variable]
    elif how.startswith('no-folder'):
        env[variable] = str(trig.tmp / 'no-such-folder')
    else:
        (trig.comp[name] / 'SKILL.md').unlink()
    done = trig.trun(env=env)
    text = done.stdout + done.stderr
    assert done.returncode == 2 and 'refusing' in text and variable in text, text
    if how.startswith('unset'):
        assert 'is not set' in text
    else:
        assert 'holds no SKILL.md' in text
    assert trig.calls() == []
    assert not (trig.tout() / 'rep1').exists() and not (trig.tmp / 'tout' / 'competitors.txt').exists()
    assert not trig.troot.exists() or os.listdir(trig.troot) == []


def test_trigger_runner_refuses_a_ref_whose_skills_hold_a_competitors_name(trig):
    (trig.repo / 'skills' / 'skill-creator').mkdir()
    (trig.repo / 'skills' / 'skill-creator' / 'SKILL.md').write_text('---\nname: skill-creator\n---\n')
    git = ['git', '-C', str(trig.repo), '-c', 'user.name=t', '-c', 'user.email=t@example.invalid',
           '-c', 'commit.gpgsign=false']
    subprocess.run(git + ['add', '-A'], check=True)
    subprocess.run(git + ['commit', '-q', '-m', 'collide'], check=True)
    done = trig.trun(ref='HEAD')
    assert done.returncode == 2 and 'collides' in done.stdout + done.stderr
    assert trig.calls() == [] and not (trig.tout() / 'rep1').exists()
    # The earlier commit, which has no such skill, still runs.
    assert trig.trun(ref=trig.sha).returncode == 0


@pytest.mark.parametrize('what', ['condition', 'prompt', 'arm', 'model', 'out', 'ref'])
def test_trigger_runner_refuses_bad_arguments(trig, what):
    kwargs = {'condition': {'condition': 'cut100'}, 'prompt': {'prompt': 'P9'}, 'arm': {'arm': 'control'},
              'model': {'model': 'claude-haiku-5-5'}, 'ref': {'ref': 'no-such-ref'},
              'out': {'out': trig.tmp / 'tout' / 'P1' / 'new' / 'full' / SONNET}}[what]
    done = trig.trun(**kwargs)
    assert done.returncode == 2, done.stdout + done.stderr
    assert trig.calls() == []


def test_trigger_runner_refuses_an_existing_rep(trig):
    trigger_ok(trig)
    done = trig.trun()
    assert done.returncode == 2 and 'exists' in done.stdout + done.stderr
    assert len(trig.calls()) == 1


def test_trigger_runner_refuses_a_rep_that_exists_in_the_out_folder_or_in_scratch_alone(trig):
    trigger_ok(trig)
    scratch = trig.tscratch / 'P1' / 'old' / 'full' / SONNET
    # Only the out folder's rep1 is left: its summary folder alone refuses the run.
    for leftover in scratch.iterdir():
        subprocess.run(['rm', '-rf', str(leftover)], check=True)
    done = trig.trun()
    assert done.returncode == 2 and f'{trig.tout()}/rep1 exists' in done.stdout + done.stderr
    # Only the scratch stream is left: the raw stream alone refuses it.
    subprocess.run(['rm', '-rf', str(trig.tout() / 'rep1')], check=True)
    (scratch / 'rep1.jsonl').write_text('{}\n')
    done = trig.trun()
    assert done.returncode == 2 and 'rep1 exists' in done.stdout + done.stderr
    assert len(trig.calls()) == 1


def test_trigger_runner_records_the_competitor_hashes_once_in_the_runs_root(trig):
    trigger_ok(trig)
    root = trig.tmp / 'tout'
    notes = (root / 'competitors.txt').read_text().split('\n')
    want = sorted(f'{name} {sha256((trig.comp[name] / "SKILL.md").read_bytes())}' for name in COMPETITORS)
    assert sorted(line for line in notes if line) == want
    assert not (trig.tout() / 'competitors.txt').exists()


def test_trigger_runner_compares_every_batch_with_the_runs_root_file(trig):
    # The old and the new batch of a pair write to different folders, so a refresh between them must still be seen.
    trigger_ok(trig, arm='old')
    (trig.comp['skill-development'] / 'SKILL.md').write_text('---\nname: skill-development\ndescription: new\n---\n')
    for kwargs in ({'arm': 'new'}, {'arm': 'old', 'first': 2, 'last': 2}, {'prompt': 'N1', 'arm': 'new', 'condition': 'cut150'}):
        done = trig.trun(**kwargs)
        assert done.returncode == 2 and 'competitor' in done.stdout + done.stderr, kwargs
    assert len(trig.calls()) == 1
    assert not (trig.tout(arm='new') / 'rep1').exists()
    # The same hashes in another batch of the same runs root are accepted.
    (trig.comp['skill-development'] / 'SKILL.md').write_text('---\nname: skill-development\ndescription: Competitor skill-development\n---\n')
    assert trig.trun(arm='new').returncode == 0


def test_trigger_runner_a_field_left_in_the_summary_is_a_kit_error(trig):
    trig.actions(f"printf '{FIELD}: 1\\n' >> README.md\n")
    done = trig.trun()
    assert done.returncode == 2, done.stdout + done.stderr
    assert 'the strip left' in (trig.tout() / 'rep1' / 'summary.json').read_text()


# --- audit.py: the stream audit (V9 and record counts) -----------------------------------------------------

REP_TOOLS = ('Read', 'Glob', 'Grep', 'Edit', 'Write')
RESULT = {'type': 'result', 'subtype': 'success', 'is_error': False, 'result': 'Done.', 'total_cost_usd': 0.01}
LISTING = ('writing-skills', 'skill-development', 'skill-creator', 'table-diff')


def stream_lines(calls=(), errors=(), extra=(), result=None, init_tools=REP_TOOLS, init_skills=None) -> list[str]:
    init = {'type': 'system', 'subtype': 'init', 'tools': list(init_tools)}
    if init_skills is not None:
        init['skills'] = list(init_skills)
    lines = [json.dumps(init)]
    for number, (name, args) in enumerate(calls, 1):
        use = {'type': 'tool_use', 'id': f't{number}', 'name': name, 'input': args}
        lines.append(json.dumps({'type': 'assistant', 'message': {'content': [use]}}))
        done = {'type': 'tool_result', 'tool_use_id': f't{number}', 'content': 'ok', 'is_error': number in errors}
        lines.append(json.dumps({'type': 'user', 'message': {'content': [done]}}))
    lines += list(extra)
    if result is not False:
        lines.append(json.dumps(result or RESULT))
    return lines


def write_t_rep(runs: Path, scratch: Path, case: str = 'T2', arm: str = 'old', model: str = SONNET, n: int = 1,
                calls=(), errors=(), extra=(), result=None, init_tools=REP_TOOLS, final: str = 'Done.',
                diff: str = '', summary: dict | None = None, lines: list[str] | None = None) -> Path:
    rep = runs / case / arm / model / f'rep{n}'
    rep.mkdir(parents=True)
    base = {'case': case, 'arm': arm, 'model': model, 'rep': n, 'rep_dir': REP_DIR, 'skill_root': SKILL_ROOT,
            'final_message': final, 'skill_copy_changed': []}
    (rep / 'summary.json').write_text(json.dumps({**base, **(summary or {})}))
    (rep / 'final.diff').write_text(diff)
    stream = scratch / case / arm / model / f'rep{n}.jsonl'
    stream.parent.mkdir(parents=True, exist_ok=True)
    if lines is None:
        lines = stream_lines(calls, errors, extra, result, init_tools)
    stream.write_text(''.join(line + '\n' for line in lines))
    return rep


def write_trigger_rep(runs: Path, tscratch: Path, prompt: str = 'P1', arm: str = 'old', condition: str = 'full',
                      model: str = SONNET, n: int = 1, calls=(), result=None, skills=LISTING,
                      extra=(), summary: dict | None = None, lines: list[str] | None = None) -> Path:
    rep = runs / prompt / arm / condition / model / f'rep{n}'
    rep.mkdir(parents=True)
    base = {'case': prompt, 'arm': arm, 'condition': condition, 'model': model, 'rep': n, 'rep_dir': TREP_DIR,
            'skill_root': None, 'final_message': 'Done.', 'skill_copy_changed': []}
    (rep / 'summary.json').write_text(json.dumps({**base, **(summary or {})}))
    (rep / 'final.diff').write_text('')
    stream = tscratch / prompt / arm / condition / model / f'rep{n}.jsonl'
    stream.parent.mkdir(parents=True, exist_ok=True)
    if lines is None:
        lines = stream_lines(calls, (), extra, result, ('Read', 'Glob', 'Grep', 'Skill'), skills)
    stream.write_text(''.join(line + '\n' for line in lines))
    return rep


@pytest.fixture
def world(tmp_path: Path, monkeypatch) -> tuple[Path, Path]:
    runs, scratch = tmp_path / 'runs', tmp_path / 'scratch'
    monkeypatch.setenv('WST_SCRATCH', str(scratch))
    monkeypatch.setenv('WST_TRIGGER_SCRATCH', str(tmp_path / 'tscratch'))
    return runs, scratch


@pytest.fixture
def twin(world, tmp_path: Path) -> tuple[Path, Path]:
    return world[0], tmp_path / 'tscratch'


def test_a_clean_rep_has_no_void_reason(world):
    rep = write_t_rep(*world, calls=[('Read', {'file_path': f'{SKILL}/SKILL.md'})])
    assert audit.void_reasons(rep) == []


def test_stream_audit_flags_peer_origin_at_any_depth(world):
    deep = {'type': 'user', 'message': {'content': [
        {'type': 'text', 'text': 'hi', 'meta': {'via': [{'origin': {'kind': 'peer', 'from': 'other-session'}}]}}]}}
    rep = write_t_rep(*world, extra=[json.dumps(deep)])
    found = audit.stream_audit(audit.stream_path(rep))
    assert found['peers'] == 1
    assert [r for r in audit.void_reasons(rep) if r.startswith('V9')] == ['V9: 1 peer-origin record(s)']
    top = write_t_rep(*world, n=2, extra=[json.dumps({'type': 'user', 'origin': {'kind': 'peer'}})])
    assert audit.stream_audit(audit.stream_path(top))['peers'] == 1
    other = write_t_rep(*world, n=3, extra=[json.dumps({'type': 'user', 'origin': {'kind': 'human'}})])
    assert audit.void_reasons(other) == []


def test_stream_audit_flags_cross_session_tool_in_init(world):
    rep = write_t_rep(*world, init_tools=('Read', 'Glob', 'SendMessage'))
    assert audit.stream_audit(audit.stream_path(rep))['cross_tools'] == ['SendMessage']
    assert 'V9: cross-session tool in the init record: SendMessage' in audit.void_reasons(rep)


def test_stream_audit_voids_a_second_result_record(world):
    rep = write_t_rep(*world, extra=[json.dumps(RESULT)])
    found = audit.stream_audit(audit.stream_path(rep))
    assert found['results'] == 2
    assert 'a second result record' in audit.void_reasons(rep)


@pytest.mark.parametrize(('kwargs', 'reason'), [
    ({'lines': [json.dumps({'type': 'system', 'subtype': 'init', 'tools': list(REP_TOOLS)}), 'not json',
                json.dumps(RESULT)]}, 'stream line(s) 2 not JSON'),
    ({'result': {**RESULT, 'subtype': 'error_max_budget_usd', 'is_error': True}}, 'subtype error_max_budget_usd'),
    ({'result': {**RESULT, 'subtype': 'error_during_execution'}}, 'a run error: subtype error_during_execution'),
    ({'result': {**RESULT, 'is_error': True}}, 'a run error: is_error true'),
    ({'result': False}, 'no result record'),
    ({'summary': {'kit_error': 'setup failed'}}, 'kit error: setup failed'),
    ({'summary': {'skill_copy_changed': ['skill copy file changed: x']}}, 'skill copy changed during the rep'),
    ({'calls': [('Read', {'file_path': '/private/etc/hosts'})]}, 'path audit: 1 hit(s)'),
])
def test_void_reasons_cover_each_void_case(world, kwargs, reason):
    rep = write_t_rep(*world, **kwargs)
    assert reason in audit.void_reasons(rep)


def test_a_missing_stream_or_summary_is_a_kit_error(world):
    rep = write_t_rep(*world)
    audit.stream_path(rep).unlink()
    assert 'kit error: no raw stream' in audit.void_reasons(rep)
    other = write_t_rep(*world, n=2)
    (other / 'summary.json').unlink()
    assert 'kit error: no summary.json' in audit.void_reasons(other)


# --- audit.py: the path audit ------------------------------------------------------------------------------

HOME = str(Path.home())


def hits(name: str, **args) -> list[str]:
    return audit.Audit({'rep_dir': REP_DIR, 'skill_root': SKILL_ROOT}).hits([{'name': name, 'input': args}])


@pytest.mark.parametrize(('name', 'args', 'whys'), [
    ('Grep', {'pattern': 'plan', 'path': f'{HOME}/Projects'}, ('the real home',)),
    ('Grep', {'pattern': 'plan', 'path': '/private/tmp'}, ('outside the allowed roots',)),
    ('Grep', {'pattern': 'plan', 'path': f'{REP_DIR}/repo/../../rep2'}, ('outside the allowed roots',)),
    ('Grep', {'pattern': 'plan', 'path': '~/Library/Keychains'}, ('$HOME/Library',)),
    ('Grep', {'pattern': 'plan', 'path': 'specs/../../..'}, ('outside the allowed roots',)),
    ('Glob', {'pattern': str(Path.home().parent) + '/**/specs/*.md'}, ('the real home', 'outside the allowed roots')),
    ('Glob', {'pattern': f'{HOME}/**/*.md'}, ('the real home',)),
    ('Glob', {'pattern': '/private/tmp/**/*.md'}, ('outside the allowed roots',)),
    ('Glob', {'pattern': '../../**/*.md'}, ('outside the allowed roots',)),
    ('Glob', {'pattern': '**/*.md', 'path': '/private/tmp'}, ('outside the allowed roots',)),
    ('Glob', {'pattern': '**/*.md', 'path': '../..'}, ('outside the allowed roots',)),
    ('Glob', {'pattern': '**/../../../etc/*'}, ('a `..` after a wildcard',)),
    # A brace alternative is a path of its own: each one, nested or comma-split, is judged.
    ('Glob', {'pattern': f'{{{HOME}/p/specs,none}}/*.md'}, ('the real home',)),
    ('Glob', {'pattern': '{/private/tmp/wst107/rep2,x}/**'}, ('outside the allowed roots',)),
    ('Glob', {'pattern': '{x,y,/tmp/wst107/rep2/repo}/*'}, ('outside the allowed roots',)),
    ('Glob', {'pattern': 'specs/{a,{b,/private/etc}}/*'}, ('outside the allowed roots',)),
    ('Glob', {'pattern': '{../x,specs}/*.md'}, ('a `..` in a brace alternative',)),
    ('Glob', {'pattern': '{~/Library/Keychains,specs}/*'}, ('$HOME/Library',)),
    ('Glob', {'pattern': '{$HOME/Library/Keychains,specs}/*'}, ('$HOME/Library',)),
])
def test_path_audit_flags_grep_and_glob_outside_roots(name, args, whys):
    found = hits(name, **args)
    assert len(found) == 1, found
    assert any(f'({why})' in found[0] for why in whys), found
    assert found[0].startswith(f'call 1 {name}')


@pytest.mark.parametrize(('name', 'args'), [
    ('Grep', {'pattern': 'plan'}),
    ('Grep', {'pattern': 'plan', 'path': 'specs'}),
    ('Grep', {'pattern': 'Liking', 'path': SKILL}),
    ('Grep', {'pattern': 'plan', 'path': '/tmp/wst107/rep1/repo/skills'}),
    ('Glob', {'pattern': '**/*.md'}),
    ('Glob', {'pattern': f'{SKILL}/**/*.md'}),
    ('Glob', {'pattern': '/tmp/wst107-skill/writing-skills/*.dot'}),
    ('Glob', {'pattern': 'references/*.md', 'path': SKILL}),
    ('Glob', {'pattern': 'specs/../skills/*/SKILL.md'}),
    ('Glob', {'pattern': '*.md', 'path': f'{REP_DIR}/repo/specs'}),
    # Only the literal part is judged: this pattern searches the repository alone.
    ('Glob', {'pattern': f'{REP_DIR}/repo/**{HOME}/notes.md'}),
    # Brace alternatives inside the allowed roots stay clean.
    ('Glob', {'pattern': f'{{{SKILL}/references,{REP_DIR}/repo/specs}}/*.md'}),
    ('Glob', {'pattern': '{/tmp/wst107/rep1/repo/specs,skills/*}/*.md'}),
    ('Glob', {'pattern': 'skills/{csv-dialect-sniff,{ingest-raw-files,x}}/SKILL.md'}),
    ('Glob', {'pattern': f'{SKILL}/{{references,scripts}}/*'}),
    # The clean neighbors of the closed limits: a `**` or braces from the rep's repository stay clean.
    ('Glob', {'pattern': '**/*.md', 'path': f'{REP_DIR}/repo'}),
    ('Glob', {'pattern': '{a,b}/*.md', 'path': f'{REP_DIR}/repo'}),
    ('Glob', {'pattern': '{a,b}/*.md'}),
    ('Glob', {'pattern': '**/*.md', 'path': f'{REP_DIR}/tmp'}),
    ('Glob', {'pattern': '*/*.md', 'path': REP_DIR}),
    # A pattern that ends above home/Library (survivor 11): `*` lists the rep folder, `h*` its home only.
    ('Glob', {'pattern': '*', 'path': REP_DIR}),
    ('Glob', {'pattern': 'h*', 'path': REP_DIR}),
    ('Glob', {'pattern': 'repo/**/*.md', 'path': REP_DIR}),
    ('Glob', {'pattern': f'{REP_DIR}/{{repo,tmp}}/**/*.md'}),
])
def test_path_audit_passes_grep_and_glob_inside_roots(name, args):
    assert hits(name, **args) == []


@pytest.mark.parametrize(('tool', 'path', 'why'), [
    ('Read', f'{REP_DIR}/repo/../home/Library/Keychains/x', '$HOME/Library'),
    ('Read', f'{REP_DIR}/../../wst107-skill/x', None),
    ('Read', f'{REP_DIR}/../../msr104-skill/x', 'outside the allowed roots'),
    ('Write', f'{REP_DIR}/../../../etc/x', 'outside the allowed roots'),
    ('Read', f'{REP_DIR}/home/Library/Keychains/../../x', '$HOME/Library'),
    ('Read', '~/Library/Keychains/../../x', '$HOME/Library'),
    ('Read', '~/library/Keychains/../../x', '$HOME/Library'),
    ('Read', f'{REP_DIR}/home/library/Keychains/x', '$HOME/Library'),
    ('Read', f'{HOME}/notes.txt', 'the real home'),
    ('Read', f'{REP_DIR}/repo/skills/csv-dialect-sniff/SKILL.md', None),
    ('Read', f'{REP_DIR}/repo/specs/../skills/x', None),
    ('Read', '/tmp/wst107/rep1/repo/x', None),
    ('Read', f'{SKILL}/references/discovery.md', None),
    ('Edit', f'{SKILL}/SKILL.md', 'a write into a read-only root'),
    ('Write', '/tmp/wst107-skill/writing-skills/x.md', 'a write into a read-only root'),
    ('Read', '/private/tmp/wst107/rep2/repo/x', 'outside the allowed roots'),
])
def test_path_audit_resolves_dot_dot_in_a_file_path(tool, path, why):
    found = hits(tool, file_path=path)
    if why is None:
        assert found == []
    else:
        assert found == [f'call 1 {tool}: {path} ({why})']


@pytest.mark.parametrize(('tool', 'path', 'why'), [
    ('Edit', 'skills/csv-dialect-sniff/SKILL.md', None),
    ('Read', 'specs/../pyproject.toml', None),
    ('Read', '../../rep2/repo/x', 'outside the allowed roots'),
    ('Write', '../../../etc/x', 'outside the allowed roots'),
    ('Read', '../home/Library/Keychains/x', '$HOME/Library'),
])
def test_path_audit_joins_a_relative_file_path_to_the_repository(tool, path, why):
    found = hits(tool, file_path=path)
    assert found == ([] if why is None else [f'call 1 {tool}: {path} ({why})'])


# --- audit.py: the three closed Glob limits (plan 107, D5) -----------------------------------------------------
#
# Limit 1: a `**` from the rep folder reaches home/Library/Keychains, the link to the real Keychains folder.
# Limit 2: a relative brace alternative under an absolute prefix was not joined to that prefix.
# Limit 3: a brace alternative under a `$HOME`, `~` or home/ prefix was not joined to it.


def test_glob_double_star_from_rep_folder_reaching_keychains_voids():
    found = hits('Glob', path=REP_DIR, pattern='**/*')
    assert len(found) == 1, found
    assert found[0].startswith('call 1 Glob') and '$HOME/Library' in found[0]


@pytest.mark.parametrize('args', [
    {'path': '/tmp/wst107/rep1', 'pattern': '**/*'},
    {'path': f'{REP_DIR}/home', 'pattern': '**/*.md'},
    {'path': '~', 'pattern': '**/*'},
    {'path': '$HOME', 'pattern': '**/*'},
    {'path': '../', 'pattern': '**/*'},
    {'path': f'{REP_DIR}/repo/..', 'pattern': '**/*'},
    {'pattern': '../**/*'},
    {'pattern': '../../**/*.md', 'path': 'specs'},
    {'pattern': f'{REP_DIR}/**/*'},
    {'pattern': '/tmp/wst107/rep1/**'},
    {'pattern': '~/**/*'},
    {'pattern': '$HOME/**/*'},
    {'pattern': '**/Keychains/*', 'path': REP_DIR},
    {'pattern': '**/*', 'path': f'{REP_DIR}/HOME'.replace('HOME', 'home')},
    # A single `*` reaches it too: `*` matches `home`, then `Library` is spelled out.
    {'pattern': '*/Library/Keychains/*', 'path': REP_DIR},
    {'pattern': '*/*/Keychains/*', 'path': REP_DIR},
    {'pattern': '*/Keychains/*', 'path': f'{REP_DIR}/home'},
    {'pattern': '{x,**}/*', 'path': REP_DIR},
    {'pattern': f'{REP_DIR}/h*/Library/Keychains/*'},
    {'pattern': f'{REP_DIR}/home/L*/*'},
])
def test_a_wildcard_search_that_can_reach_home_library_voids(args):
    found = hits('Glob', **args)
    assert len(found) == 1 and found[0].startswith('call 1 Glob'), (args, found)


def test_the_judged_path_of_a_glob_path_is_in_the_hit_line():
    found = hits('Glob', path=REP_DIR, pattern='**/*')
    assert 'Glob pattern: **/*' in found[0]


def test_relative_brace_alternative_joins_its_absolute_prefix():
    for prefix in (REP_DIR, '/tmp/wst107/rep1'):
        found = hits('Glob', pattern=f'{prefix}/{{home/Library/Keychains,x}}/*')
        assert len(found) == 1, (prefix, found)
        assert '$HOME/Library' in found[0]
    clean = hits('Glob', pattern=f'{REP_DIR}/{{repo/skills,repo/specs}}/*.md')
    assert clean == []


@pytest.mark.parametrize('pattern', [
    f'{REP_DIR}/{{home,x}}/Library/Keychains/*',
    f'{REP_DIR}/{{home/Library,x}}/Keychains/*',
    f'{REP_DIR}/{{home,tmp}}/{{Library,y}}/*',
    f'{REP_DIR}/{{x,{{home/Library,y}}}}/*',
    f'/tmp/wst107/rep1/{{x,home/library/Keychains}}/*',
])
def test_a_brace_group_and_its_suffix_are_judged_together(pattern):
    found = hits('Glob', pattern=pattern)
    assert len(found) == 1 and '$HOME/Library' in found[0], (pattern, found)


def test_brace_alternative_under_home_library_prefix_voids():
    for prefix in ('$HOME', '~'):
        found = hits('Glob', pattern=f'{prefix}/Library/{{Keychains,Caches}}/*')
        assert len(found) == 1, (prefix, found)
        assert '$HOME/Library' in found[0]


@pytest.mark.parametrize('pattern', [
    '$HOME/{Library,x}/Keychains/*',
    '~/{Library,x}/Keychains/*',
    '$HOME/{Library/Keychains,x}/*',
    '~/{Library/Keychains,x}/*',
    '${HOME}/{Library,x}/Keychains/*',
    '$HOME/{x,{y,Library}}/Keychains/*',
    '$HOME/{lib,Library}/{Caches,Keychains}/*',
    f'{REP_DIR}/home/{{Library,x}}/Keychains/*',
    f'/tmp/wst107/rep1/home/{{Library/Keychains,x}}/*',
    '{$HOME,x}/Library/Keychains/*',
    '{~,x}/Library/Keychains/*',
])
def test_a_relative_brace_alternative_under_a_home_prefix_voids(pattern):
    found = hits('Glob', pattern=pattern)
    assert len(found) == 1 and '$HOME/Library' in found[0], (pattern, found)


def test_a_brace_alternative_under_a_home_prefix_outside_library_is_clean():
    assert hits('Glob', pattern='$HOME/{notes,x}/*.md') == []
    assert hits('Glob', pattern='~/{tmp,repo}/**/*.md') == []
    assert hits('Glob', pattern=f'{REP_DIR}/home/{{docs,x}}/*') == []


def test_too_many_brace_alternatives_are_a_hit():
    pattern = 'a/' + ''.join(f'{{x{i},y{i}}}' for i in range(12)) + '/*.md'
    found = hits('Glob', pattern=pattern)
    assert len(found) == 1 and 'brace' in found[0]
    small = hits('Glob', pattern='a/' + ''.join(f'{{x{i},y{i}}}' for i in range(3)) + '/*.md')
    assert small == []


def test_one_glob_call_gives_one_hit_line():
    found = hits('Glob', path=REP_DIR, pattern='{**/*,/private/etc/*}')
    assert len(found) == 1


# --- audit.py: the Bash audit (plan 107's R3: one git mv inside the rep's repository) -----------------------


@pytest.mark.parametrize('command', [
    'ls', 'ls -la', 'rm -rf x', 'git mv a b && ls', 'git mv a b; rm c', 'git mv a b | cat', 'git mv a b\nls',
    'git status', 'git rm -r skills/a', 'git mv', 'git mv a', 'git mv a b c', 'git mv -f a b', 'git mv -k a b',
    'git  mv a b && true', 'git mv $(pwd)/a b', 'git mv `pwd`/a b', 'git mv a "b"', "git mv a 'b'",
    'git mv a b > out.txt', 'git mv a b &', 'git mv skills/* b', 'git mv ~/a b', 'git mv a $HOME/b',
    'cat ~/notes', 'sh -c "git mv a b"', 'env git mv a b', 'cd .. && git mv a b', 'git -C .. mv a b', '',
    'git mv a{b,c} d', 'git mv a b #c', 'git mv a\\ b c',
])
def test_bash_other_than_git_mv_voids(command):
    found = hits('Bash', command=command)
    assert len(found) == 1 and found[0].startswith('call 1 Bash'), (command, found)


@pytest.mark.parametrize('command', [
    'git mv skills/a /private/tmp/elsewhere/a',
    'git mv /private/tmp/elsewhere/a skills/b',
    'git mv skills/a ../b',
    'git mv skills/a ../../rep2/repo/b',
    'git mv skills/a ../home/Library/Keychains/b',
    f'git mv skills/a {HOME}/b',
    f'git mv {REP_DIR}/repo/skills/a {REP_DIR}/home/b',
    f'git mv {REP_DIR}/repo/skills/a {REP_DIR}/repo/../b',
    'git mv skills/a /tmp/wst107/rep2/repo/b',
    f'git mv {REP_DIR}/repo/skills/a {REP_DIR}/repo',
    'git mv skills/a .',
    'git mv skills/a ./',
    'git mv . skills/b',
])
def test_git_mv_outside_rep_voids(command):
    found = hits('Bash', command=command)
    assert len(found) == 1 and found[0].startswith('call 1 Bash'), (command, found)


@pytest.mark.parametrize('command', [
    'git mv skills/a skills/b',
    'git mv skills/csv-dialect-sniff skills/sniffing-csv-dialects',
    f'git mv {REP_DIR}/repo/skills/a {REP_DIR}/repo/skills/b',
    f'git mv /tmp/wst107/rep1/repo/skills/a /tmp/wst107/rep1/repo/skills/b',
    'git mv skills/a/SKILL.md skills/a/OLD.md',
    'git mv skills/../commands/a.md commands/b.md',
    '  git mv skills/a skills/b  ',
    'git mv skills/a skills/b\n',
])
def test_git_mv_inside_rep_is_clean(command):
    assert hits('Bash', command=command) == []


def test_a_bash_call_is_judged_with_the_others(world):
    rep = write_t_rep(*world, case='R3', calls=[('Bash', {'command': 'git mv skills/a skills/b'}),
                                                ('Bash', {'command': 'ls'})])
    assert 'path audit: 1 hit(s)' in audit.void_reasons(rep)
    clean = write_t_rep(*world, case='R3', n=2, calls=[('Bash', {'command': 'git mv skills/a skills/b'})])
    assert audit.void_reasons(clean) == []


# --- audit.py: the reference reads (descriptive) and the R3 tree check ------------------------------------------


def call(name: str, is_error: bool = False, **args) -> dict:
    return {'name': name, 'input': args, 'is_error': is_error}


@pytest.mark.parametrize(('case', 'name'), [('M1', 'micro-tests.md'), ('T2', 'discovery.md'), ('R3', 'discovery.md')])
def test_each_case_names_the_reference_file_it_reads(case, name):
    assert cases.REFERENCE[case] == name
    reads = audit.reference_reads([call('Read', file_path=f'{SKILL}/references/{name}')], case)
    assert [read['call'] for read in reads] == [1]


def test_reference_reads_mark_partial_and_failed_reads_and_skip_other_tools_and_names():
    calls = [call('Read', file_path=f'{SKILL}/references/discovery.md', offset=1, limit=30),
             call('Read', is_error=True, file_path=f'{SKILL}/references/discovery.md'),
             call('Grep', pattern='x', path=f'{SKILL}/references/discovery.md'),
             call('Glob', pattern='**/discovery.md'),
             call('Read', file_path=f'{SKILL}/references/old-discovery.md'),
             call('Read', file_path=f'{SKILL}/references/discovery.md.bak'),
             call('Read', file_path=f'{SKILL}/SKILL.md'),
             call('Read', file_path=f'{SKILL}/references/discovery.md')]
    reads = audit.reference_reads(calls, 'T2')
    assert [(read['call'], read['partial'], read['error']) for read in reads] == [(1, True, False), (2, False, True),
                                                                                    (8, False, False)]


def make_r3_tree(tmp: Path, **changes) -> Path:
    repo = tmp / 'repo'
    (repo / 'skills' / 'sniffing-csv-dialects').mkdir(parents=True)
    (repo / 'skills' / 'sniffing-csv-dialects' / 'SKILL.md').write_text(
        '---\nname: sniffing-csv-dialects\ndescription: Use when sniffing\n---\n\nBody.\n')
    (repo / 'skills' / 'ingest-raw-files').mkdir()
    (repo / 'skills' / 'ingest-raw-files' / 'SKILL.md').write_text('Use sniffing-csv-dialects first.\n')
    (repo / 'AGENTS.md').write_text('Run sniffing-csv-dialects.\n')
    (repo / '.claude').mkdir()
    (repo / '.claude' / 'settings.json').write_text('{"skillOverrides": {"sniffing-csv-dialects": "name-only"}}\n')
    (repo / '.git').mkdir()
    (repo / '.git' / 'config').write_text('[remote]\n\turl = csv-dialect-sniff\n')
    return repo


def test_r3_check_passes_the_finished_rename(tmp_path):
    found = audit.r3_check(make_r3_tree(tmp_path))
    assert found['verdict'] == 'PASS' and found['problems'] == []


def test_r3_check_finds_old_name_in_untracked_file(tmp_path):
    repo = make_r3_tree(tmp_path)
    (repo / 'notes-untracked.txt').write_text('see csv-dialect-sniff\n')
    found = audit.r3_check(repo)
    assert found['verdict'] == 'FAIL'
    assert any('notes-untracked.txt' in problem for problem in found['problems'])


def test_r3_check_finds_old_name_in_a_tracked_file_a_hidden_file_and_a_nested_folder(tmp_path):
    for where in ('AGENTS.md', '.claude/settings.json', 'skills/ingest-raw-files/SKILL.md', 'deep/er/x.md',
                  '.hidden/csv-dialect-sniff-note.txt', 'skills/sniffing-csv-headers/SKILL.md', '.env',
                  'skills/ingest-raw-files/.note', 'commands/.hidden.md'):
        repo = make_r3_tree(tmp_path / where.replace('/', '_'))
        path = repo / where
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('Use csv-dialect-sniff here.\n')
        found = audit.r3_check(repo)
        assert found['verdict'] == 'FAIL', where
        assert any(where in problem for problem in found['problems']), (where, found)


def test_r3_check_finds_old_name_in_a_gitignored_file_and_ignores_only_dot_git(tmp_path):
    repo = make_r3_tree(tmp_path)
    (repo / '.gitignore').write_text('ignored.txt\n')
    (repo / 'ignored.txt').write_text('csv-dialect-sniff\n')
    subprocess.run(['git', 'init', '-q', str(repo)], check=True)
    found = audit.r3_check(repo)
    assert found['verdict'] == 'FAIL' and any('ignored.txt' in problem for problem in found['problems'])
    (repo / 'ignored.txt').unlink()
    # The .git folder holds the old name in its config, and it does not count.
    assert audit.r3_check(repo)['verdict'] == 'PASS'


def test_r3_check_fails_a_leftover_old_folder_a_missing_new_skill_and_a_wrong_name(tmp_path):
    repo = make_r3_tree(tmp_path / 'a')
    (repo / 'skills' / 'csv-dialect-sniff').mkdir()
    found = audit.r3_check(repo)
    assert found['verdict'] == 'FAIL' and any('csv-dialect-sniff/' in problem for problem in found['problems'])
    repo = make_r3_tree(tmp_path / 'b')
    (repo / 'skills' / 'sniffing-csv-dialects' / 'SKILL.md').unlink()
    assert audit.r3_check(repo)['verdict'] == 'FAIL'
    repo = make_r3_tree(tmp_path / 'c')
    (repo / 'skills' / 'sniffing-csv-dialects' / 'SKILL.md').write_text('---\nname: sniffing-csv-dialect\n---\n')
    found = audit.r3_check(repo)
    assert found['verdict'] == 'FAIL' and any('name' in problem for problem in found['problems'])
    repo = make_r3_tree(tmp_path / 'd')
    (repo / 'skills' / 'sniffing-csv-dialects' / 'SKILL.md').write_text('no frontmatter\n')
    assert audit.r3_check(repo)['verdict'] == 'FAIL'


def test_r3_check_reads_a_binary_file_and_a_quoted_name(tmp_path):
    repo = make_r3_tree(tmp_path / 'a')
    (repo / 'blob.bin').write_bytes(b'\xff\xfe csv-dialect-sniff \x00')
    assert audit.r3_check(repo)['verdict'] == 'FAIL'
    repo = make_r3_tree(tmp_path / 'b')
    (repo / 'x.md').write_text('"name": "csv-dialect-sniff"\n')
    assert audit.r3_check(repo)['verdict'] == 'FAIL'


def test_r3_check_leaves_the_near_collision_alone(tmp_path):
    repo = make_r3_tree(tmp_path)
    (repo / 'skills' / 'sniffing-csv-headers').mkdir()
    (repo / 'skills' / 'sniffing-csv-headers' / 'SKILL.md').write_text('---\nname: sniffing-csv-headers\n---\n')
    assert audit.r3_check(repo)['verdict'] == 'PASS'


def test_audit_rep_scores_r3_from_the_parked_tree_and_the_other_cases_not_at_all(world, tmp_path):
    runs, scratch = world
    rep = write_t_rep(runs, scratch, case='R3', calls=[('Bash', {'command': 'git mv skills/a skills/b'})])
    parked = scratch / 'R3' / 'old' / SONNET / 'rep1-folder'
    make_r3_tree(parked)
    found = audit.audit_rep(rep)
    assert found['r3']['verdict'] == 'PASS' and found['void'] == []
    (parked / 'repo' / 'late.txt').write_text('csv-dialect-sniff\n')
    assert audit.audit_rep(rep)['r3']['verdict'] == 'FAIL'
    other = write_t_rep(runs, scratch, case='T2')
    assert audit.audit_rep(other)['r3'] is None


def test_audit_rep_marks_whether_an_r3_rep_flagged_the_near_collision(world):
    runs, scratch = world
    first = write_t_rep(*world, case='R3', final='I left `sniffing-csv-headers` alone; it sounds close.')
    second = write_t_rep(*world, case='R3', n=2, final='Renamed.')
    assert audit.audit_rep(first)['flagged'] is True
    assert audit.audit_rep(second)['flagged'] is False
    assert audit.audit_rep(write_t_rep(*world, case='T2'))['flagged'] is None


def test_audit_command_prints_each_rep(world):
    runs, scratch = world
    write_t_rep(runs, scratch, calls=[('Read', {'file_path': f'{SKILL}/references/discovery.md', 'limit': 30}),
                                      ('Edit', {'file_path': f'{REP_DIR}/repo/skills/x/SKILL.md', 'old_string': 'a',
                                                'new_string': 'b'})])
    write_t_rep(runs, scratch, n=2, extra=[json.dumps(RESULT)])
    done = kit_tool(str(KIT / 'audit.py'), str(runs / 'T2' / 'old' / SONNET),
                    env={**os.environ, 'WST_SCRATCH': str(scratch)})
    assert done.returncode == 0, done.stdout + done.stderr
    first, second = done.stdout.split(f'== T2 old {SONNET} rep2')
    assert f'== T2 old {SONNET} rep1' in first
    assert 'reads of discovery.md: call 1 (partial)' in first
    assert 'VOID: none' in first
    assert 'VOID: a second result record' in second


def test_audit_command_refuses_a_folder_with_no_rep(tmp_path):
    (tmp_path / 'M1' / 'old' / SONNET).mkdir(parents=True)
    done = kit_tool(str(KIT / 'audit.py'), str(tmp_path / 'M1' / 'old' / SONNET))
    assert done.returncode != 0 and 'holds no rep folder' in done.stdout + done.stderr


def test_audit_command_prints_the_r3_check_and_a_trigger_rep(world, twin):
    runs, scratch = world
    write_t_rep(runs, scratch, case='R3')
    make_r3_tree(scratch / 'R3' / 'old' / SONNET / 'rep1-folder')
    write_trigger_rep(*twin, calls=[('Skill', {'skill': 'writing-skills'})])
    env = {**os.environ, 'WST_SCRATCH': str(scratch), 'WST_TRIGGER_SCRATCH': str(twin[1])}
    done = kit_tool(str(KIT / 'audit.py'), str(runs / 'R3' / 'old' / SONNET), env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    assert 'r3 check: PASS' in done.stdout and 'VOID: none' in done.stdout
    done = kit_tool(str(KIT / 'audit.py'), str(twin[0] / 'P1' / 'old' / 'full' / SONNET), env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    assert f'== P1 old full {SONNET} rep1' in done.stdout and 'VOID: none' in done.stdout


# --- trigger reps: the audit's layout, listing and subtype rules ------------------------------------------------


def test_a_clean_trigger_rep_has_no_void_reason(twin):
    rep = write_trigger_rep(*twin, calls=[('Skill', {'skill': 'writing-skills'})])
    assert audit.stream_path(rep).parent.parts[-4:] == ('P1', 'old', 'full', SONNET)
    assert audit.void_reasons(rep) == []


@pytest.mark.parametrize('skills', [
    ('skill-development', 'skill-creator', 'table-diff'),
    ('writing-skills', 'skill-creator', 'table-diff'),
    ('writing-skills', 'skill-development', 'table-diff'),
    (),
])
def test_listing_without_competitors_voids(twin, skills):
    rep = write_trigger_rep(*twin, skills=skills)
    assert any(reason.startswith('listing') for reason in audit.void_reasons(rep)), audit.void_reasons(rep)


def test_a_missing_skills_field_in_the_init_record_voids(twin):
    rep = write_trigger_rep(*twin, lines=stream_lines(init_tools=('Read', 'Skill'), init_skills=None))
    assert any(reason.startswith('listing') for reason in audit.void_reasons(rep))


def test_listing_matches_names_exactly(twin):
    rep = write_trigger_rep(*twin, skills=('writing-skills-old', 'my:skill-development', 'skill-creator-2'))
    assert any(reason.startswith('listing') for reason in audit.void_reasons(rep))
    rep = write_trigger_rep(*twin, n=2, skills=({'name': 'writing-skills'}, {'name': 'skill-development'},
                                                 {'name': 'skill-creator'}))
    assert audit.void_reasons(rep) == []


@pytest.mark.parametrize('subtype', ['error_max_turns', 'error_max_budget_usd'])
def test_trigger_rep_max_turns_stop_is_not_void(twin, subtype):
    from triggers import is_load, load_records
    result = {**RESULT, 'subtype': subtype, 'is_error': True}
    rep = write_trigger_rep(*twin, calls=[('Skill', {'skill': 'writing-skills'})], result=result)
    assert audit.void_reasons(rep) == []
    assert is_load(load_records(rep)) is True


def test_trigger_rep_budget_stop_is_not_void(twin):
    result = {**RESULT, 'subtype': 'error_max_budget_usd', 'is_error': False}
    rep = write_trigger_rep(*twin, calls=[('Skill', {'skill': 'writing-skills'})], result=result)
    assert audit.void_reasons(rep) == []
    # The case reps keep the rule: a budget stop voids them.
    case_rep = write_t_rep(*twin[:1], twin[1].parent / 'scratch', result={**result, 'is_error': True})
    assert 'subtype error_max_budget_usd' in audit.void_reasons(case_rep)


def test_a_trigger_rep_with_another_run_error_is_void(twin):
    rep = write_trigger_rep(*twin, result={**RESULT, 'subtype': 'error_during_execution'})
    assert 'a run error: subtype error_during_execution' in audit.void_reasons(rep)
    rep = write_trigger_rep(*twin, n=2, result={**RESULT, 'is_error': True})
    assert 'a run error: is_error true' in audit.void_reasons(rep)


def test_a_trigger_rep_gets_the_path_audit_too(twin):
    rep = write_trigger_rep(*twin, calls=[('Read', {'file_path': '/private/etc/hosts'}),
                                          ('Glob', {'pattern': '**/*', 'path': TREP_DIR})])
    assert 'path audit: 2 hit(s)' in audit.void_reasons(rep)
    clean = write_trigger_rep(*twin, n=2, calls=[('Read', {'file_path': f'{TREP_DIR}/home/.claude/skills/table-diff/SKILL.md'})])
    assert audit.void_reasons(clean) == []


# --- triggers.py: loads, listing and tally ------------------------------------------------------------------


def skill_use(name: str) -> tuple[str, dict]:
    return 'Skill', {'skill': name}


def test_load_counts_a_skill_call_naming_writing_skills(twin):
    import triggers
    rep = write_trigger_rep(*twin, calls=[skill_use('writing-skills')])
    assert triggers.is_load(triggers.load_records(rep)) is True


def test_load_counts_a_later_skill_call(twin):
    import triggers
    rep = write_trigger_rep(*twin, calls=[skill_use('skill-creator'), ('Read', {'file_path': f'{TREP_DIR}/repo/README.md'}),
                                         skill_use('writing-skills')])
    records = triggers.load_records(rep)
    assert triggers.is_load(records) is True
    assert triggers.skill_calls(records) == ['skill-creator', 'writing-skills']


def test_no_skill_call_is_no_load(twin):
    import triggers
    rep = write_trigger_rep(*twin, calls=[('Read', {'file_path': f'{TREP_DIR}/repo/README.md'})])
    assert triggers.is_load(triggers.load_records(rep)) is False
    assert triggers.skill_calls(triggers.load_records(rep)) == []


def test_other_skill_call_is_no_load(twin):
    import triggers
    rep = write_trigger_rep(*twin, calls=[skill_use('skill-creator'), skill_use('table-diff')])
    assert triggers.is_load(triggers.load_records(rep)) is False


@pytest.mark.parametrize('name', ['writing-skills-old', 'my-writing-skills', 'plugin:writing-skills', 'Writing-Skills',
                                  ''])
def test_a_load_needs_the_exact_skill_name(twin, name):
    import triggers
    rep = write_trigger_rep(*twin, calls=[skill_use(name)])
    assert triggers.is_load(triggers.load_records(rep)) is False


def test_only_a_tool_use_named_skill_is_a_load(twin):
    import triggers
    text = {'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': 'Skill writing-skills'}]}}
    other = {'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'id': 'x', 'name': 'Read',
                                                           'input': {'skill': 'writing-skills'}}]}}
    rep = write_trigger_rep(*twin, extra=[json.dumps(text), json.dumps(other)])
    assert triggers.is_load(triggers.load_records(rep)) is False


def test_listing_reads_the_init_record(twin):
    import triggers
    rep = write_trigger_rep(*twin, skills=('writing-skills', 'skill-development', 'x'))
    assert triggers.listing(triggers.load_records(rep)) == ['writing-skills', 'skill-development', 'x']
    rep = write_trigger_rep(*twin, n=2, skills=({'name': 'a'}, 'b'))
    assert triggers.listing(triggers.load_records(rep)) == ['a', 'b']
    assert triggers.listing([{'type': 'assistant'}]) == []


def test_triggers_loads_and_listing_commands(twin):
    rep = write_trigger_rep(*twin, calls=[skill_use('skill-creator'), skill_use('writing-skills')])
    none = write_trigger_rep(*twin, n=2)
    env = {**os.environ, 'WST_TRIGGER_SCRATCH': str(twin[1])}
    done = kit_tool(str(KIT / 'triggers.py'), 'loads', str(rep), env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    assert done.stdout.split('\n')[0] == 'load'
    assert 'skill-creator' in done.stdout and 'writing-skills' in done.stdout
    done = kit_tool(str(KIT / 'triggers.py'), 'loads', str(none), env=env)
    assert done.stdout.split('\n')[0] == 'no-load'
    other = write_trigger_rep(*twin, n=3, calls=[skill_use('skill-creator')])
    done = kit_tool(str(KIT / 'triggers.py'), 'loads', str(other), env=env)
    assert done.stdout.split('\n')[0] == 'no-load' and 'skill-creator' in done.stdout
    done = kit_tool(str(KIT / 'triggers.py'), 'listing', str(rep), env=env)
    assert done.stdout.split() == list(LISTING)
    assert kit_tool(str(KIT / 'triggers.py'), 'nonsense', env=env).returncode != 0


def full_cells(arm_loads: dict, reps: int = 3) -> dict:
    '''Synthetic tally cells: arm_loads[(prompt, arm, condition, model)] = loads of reps.'''
    return {key: {'reps': reps, 'loads': loads, 'void': 0} for key, loads in arm_loads.items()}


def grid(old: dict | None = None, new: dict | None = None, models=(SONNET, OPUS), conditions=('full', 'cut150')) -> dict:
    '''Every prompt, arm, condition and model, 3 reps each; `old` and `new` map (prompt, condition, model) to loads.'''
    import trigger_prompts
    cells = {}
    for prompt in trigger_prompts.PROMPTS:
        should = prompt in trigger_prompts.SHOULD_LOAD
        for arm, given in (('old', old or {}), ('new', new or {})):
            for condition in conditions:
                for model in models:
                    cells[(prompt, arm, condition, model)] = {
                        'reps': 3, 'void': 0, 'loads': given.get((prompt, condition, model), 2 if should else 0)}
    return cells


def test_the_trigger_prompts_are_the_eight_of_the_plan():
    import trigger_prompts
    assert list(trigger_prompts.PROMPTS) == ['P1', 'P2', 'P3', 'P4', 'P5', 'N1', 'N2', 'N3']
    assert trigger_prompts.SHOULD_LOAD == ('P1', 'P2', 'P3', 'P4', 'P5')
    assert trigger_prompts.TESTING == ('P1', 'P2', 'P3') and trigger_prompts.CORE == ('P4', 'P5')
    assert trigger_prompts.NEAR_MISS == ('N1', 'N2', 'N3')
    assert trigger_prompts.PROMPTS['P1'] == ('The `table-diff` skill never gets picked up, even when I ask it to compare '
                                             'two tables. Can you sort that out?')
    assert trigger_prompts.PROMPTS['P2'] == ('`retry-budget` keeps loading on every HTTP question, even unrelated '
                                             'ones. Make it stop.')
    assert trigger_prompts.PROMPTS['P3'] == ('I reworded the core rule in `release-notes`. Before I ship it, check that '
                                             'the new wording actually changes what agents do.')
    assert trigger_prompts.PROMPTS['P4'] == 'Make a new skill that teaches agents how we load test fixtures.'
    assert trigger_prompts.PROMPTS['P5'] == 'Rename the `fixture-loader` skill to `loading-test-fixtures`.'
    assert trigger_prompts.PROMPTS['N1'] == ('Package the skills in this repo as a Claude Code plugin with a '
                                             'marketplace.json.')
    assert trigger_prompts.PROMPTS['N2'] == ("Write an implementation plan for adding a timeout to `retry-budget`'s "
                                             'HTTP client.')
    assert trigger_prompts.PROMPTS['N3'] == 'Write a CLAUDE.md for this repo.'


def test_the_trigger_prompts_command_prints_one_prompt():
    import trigger_prompts
    done = kit_tool(str(KIT / 'trigger_prompts.py'), 'P4')
    assert done.returncode == 0, done.stderr
    assert done.stdout == trigger_prompts.PROMPTS['P4'] + '\n'
    assert kit_tool(str(KIT / 'trigger_prompts.py'), 'P9').returncode != 0


def test_floor_and_bars_pass_when_new_loses_nothing():
    import triggers
    result = triggers.judge(grid(old={}, new={}))
    assert result['floor'] == {SONNET: {'old_loads': 10, 'ok': True}, OPUS: {'old_loads': 10, 'ok': True}}
    assert all(bar['ok'] for bar in result['bars']) and len(result['bars']) == 8
    assert result['ok'] is True and result['complete'] is True


def test_the_floor_needs_eight_old_should_load_loads_in_full_per_model():
    import triggers
    low = {(p, 'full', SONNET): 1 for p in ('P1', 'P2', 'P3', 'P4', 'P5')}
    result = triggers.judge(grid(old=low))
    assert result['floor'][SONNET] == {'old_loads': 5, 'ok': False}
    assert result['floor'][OPUS]['ok'] is True and result['ok'] is False
    edge = {(p, 'full', SONNET): n for p, n in zip(('P1', 'P2', 'P3', 'P4', 'P5'), (2, 2, 2, 1, 1))}
    assert triggers.judge(grid(old=edge, new=edge))['floor'][SONNET] == {'old_loads': 8, 'ok': True}
    # A cut150 cell never feeds the floor.
    cut = {(p, 'cut150', SONNET): 0 for p in ('P1', 'P2', 'P3', 'P4', 'P5')}
    assert triggers.judge(grid(old=cut, new=cut))['floor'][SONNET]['ok'] is True


def test_the_floor_is_missed_by_one_load_below_eight():
    import triggers
    seven = {(p, 'full', SONNET): n for p, n in zip(('P1', 'P2', 'P3', 'P4', 'P5'), (2, 2, 1, 1, 1))}
    assert triggers.judge(grid(old=seven, new=seven))['floor'][SONNET] == {'old_loads': 7, 'ok': False}
    nine = {(p, 'full', SONNET): n for p, n in zip(('P1', 'P2', 'P3', 'P4', 'P5'), (2, 2, 2, 2, 1))}
    assert triggers.judge(grid(old=nine, new=nine))['floor'][SONNET] == {'old_loads': 9, 'ok': True}


@pytest.mark.parametrize(('new_total', 'ok'), [(8, True), (7, False), (10, True), (0, False)])
def test_the_should_load_bar_is_new_at_least_old_minus_two(new_total, ok):
    import triggers
    old = {(p, 'full', SONNET): n for p, n in zip(('P1', 'P2', 'P3', 'P4', 'P5'), (2, 2, 2, 2, 2))}
    new = {(p, 'full', SONNET): 0 for p in ('P1', 'P2', 'P3', 'P4', 'P5')}
    left = new_total
    for prompt in ('P1', 'P2', 'P3', 'P4', 'P5'):
        take = min(3, left)
        new[(prompt, 'full', SONNET)] = take
        left -= take
    result = triggers.judge(grid(old=old, new=new))
    [bar] = [b for b in result['bars'] if (b['kind'], b['model'], b['condition']) == ('should-load', SONNET, 'full')]
    assert (bar['old'], bar['new'], bar['ok']) == (10, new_total, ok)


@pytest.mark.parametrize(('new_total', 'ok'), [(0, True), (1, True), (2, False), (3, False)])
def test_the_near_miss_bar_is_new_at_most_old_plus_one(new_total, ok):
    import triggers
    new = {}
    left = new_total
    for prompt in ('N1', 'N2', 'N3'):
        take = min(3, left)
        new[(prompt, 'cut150', OPUS)] = take
        left -= take
    result = triggers.judge(grid(new=new))
    [bar] = [b for b in result['bars'] if (b['kind'], b['model'], b['condition']) == ('near-miss', OPUS, 'cut150')]
    assert (bar['old'], bar['new'], bar['ok']) == (0, new_total, ok)
    assert result['ok'] is ok
    old = {(p, 'cut150', OPUS): 1 for p in ('N1', 'N2', 'N3')}
    [bar] = [b for b in triggers.judge(grid(old=old, new={(p, 'cut150', OPUS): 1 for p in ('N1', 'N2')}))['bars']
             if (b['kind'], b['model'], b['condition']) == ('near-miss', OPUS, 'cut150')]
    assert (bar['old'], bar['new'], bar['ok']) == (3, 2, True)


def test_the_cut150_prediction_is_descriptive_and_never_fails_the_verdict():
    import triggers
    old = {(p, 'cut150', SONNET): 3 for p in ('P1', 'P2', 'P3')}
    new = {(p, 'cut150', SONNET): 2 for p in ('P1', 'P2', 'P3')}
    # New gains on P4 and P5, so the should-load bar (new >= old - 2) holds and only the prediction fails.
    new.update({(p, 'cut150', SONNET): 3 for p in ('P4', 'P5')})
    result = triggers.judge(grid(old=old, new=new))
    assert result['prediction'][SONNET] == {'old': 9, 'new': 6, 'holds': False}
    assert result['prediction'][OPUS] == {'old': 6, 'new': 6, 'holds': True}
    assert result['ok'] is True


def test_a_verdict_is_incomplete_without_the_planned_reps_in_each_cell():
    import triggers
    cells = grid()
    cells[('P3', 'new', 'cut150', OPUS)]['reps'] = 2
    assert triggers.judge(cells)['complete'] is False
    cells = grid()
    del cells[('N2', 'old', 'full', SONNET)]
    assert triggers.judge(cells)['complete'] is False
    assert triggers.judge(grid(models=(SONNET,)))['complete'] is False
    assert triggers.judge({})['complete'] is False


def test_tally_counts_loads_per_cell_and_skips_void_reps(twin):
    import triggers
    runs, tscratch = twin
    write_trigger_rep(runs, tscratch, calls=[skill_use('writing-skills')])
    write_trigger_rep(runs, tscratch, n=2, calls=[skill_use('skill-creator')])
    write_trigger_rep(runs, tscratch, n=3, calls=[skill_use('skill-creator'), skill_use('writing-skills')])
    write_trigger_rep(runs, tscratch, n=4, calls=[skill_use('writing-skills')], skills=('writing-skills',))
    write_trigger_rep(runs, tscratch, n=5, calls=[skill_use('writing-skills')],
                      result={**RESULT, 'subtype': 'error_max_turns', 'is_error': True})
    write_trigger_rep(runs, tscratch, arm='new', condition='cut150', model=OPUS, calls=[skill_use('writing-skills')])
    result = triggers.tally(runs)
    assert result['cells'][('P1', 'old', 'full', SONNET)] == {'reps': 4, 'loads': 3, 'void': 1}
    assert result['cells'][('P1', 'new', 'cut150', OPUS)] == {'reps': 1, 'loads': 1, 'void': 0}
    assert [line for line in result['voids'] if 'rep4' in line and 'listing' in line]


def test_tally_command_prints_the_counts_and_the_verdict(twin):
    runs, tscratch = twin
    write_trigger_rep(runs, tscratch, calls=[skill_use('writing-skills')])
    write_trigger_rep(runs, tscratch, n=2)
    env = {**os.environ, 'WST_TRIGGER_SCRATCH': str(tscratch)}
    done = kit_tool(str(KIT / 'triggers.py'), 'tally', str(runs), env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    assert f'P1 old full {SONNET}: 1 of 2' in done.stdout
    assert 'floor' in done.stdout and 'incomplete' in done.stdout


def test_the_verdict_is_uninformative_below_the_floor_fail_on_a_bar_and_incomplete_without_the_reps():
    import triggers
    low = {(p, 'full', SONNET): 1 for p in ('P1', 'P2', 'P3', 'P4', 'P5')}
    assert triggers.verdict(triggers.judge(grid(old=low, new=low))) == 'uninformative (below the floor)'
    # The floor governs even when a bar also fails.
    assert triggers.verdict(triggers.judge(grid(old=low))) == 'uninformative (below the floor)'
    bad = {(p, 'cut150', OPUS): 0 for p in ('P1', 'P2', 'P3', 'P4', 'P5')}
    assert triggers.verdict(triggers.judge(grid(new=bad))) == 'fail'
    assert triggers.verdict(triggers.judge(grid())) == 'pass'
    cells = grid(old=low)
    cells[('P3', 'new', 'cut150', OPUS)]['reps'] = 2
    assert triggers.verdict(triggers.judge(cells)) == 'incomplete'
    assert triggers.verdict(triggers.judge({})) == 'incomplete'


def test_tally_command_prints_the_uninformative_verdict(twin):
    runs, tscratch = twin
    import trigger_prompts
    for prompt in trigger_prompts.PROMPTS:
        for arm in ('old', 'new'):
            for condition in ('full', 'cut150'):
                for model in (SONNET, OPUS):
                    for n in (1, 2, 3):
                        write_trigger_rep(runs, tscratch, prompt=prompt, arm=arm, condition=condition, model=model, n=n,
                                          calls=[skill_use('writing-skills')] if (prompt == 'P1' and n == 1) else [])
    env = {**os.environ, 'WST_TRIGGER_SCRATCH': str(tscratch)}
    done = kit_tool(str(KIT / 'triggers.py'), 'tally', str(runs), env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    assert 'verdict: uninformative (below the floor)' in done.stdout


def test_tally_reads_the_runs_root_that_the_trigger_runner_wrote(trig):
    trigger_ok(trig)
    root = trig.tmp / 'tout'
    assert (root / 'competitors.txt').is_file()
    env = {**os.environ, 'WST_TRIGGER_SCRATCH': str(trig.tscratch)}
    done = kit_tool(str(KIT / 'triggers.py'), 'tally', str(root), env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    assert f'P1 old full {SONNET}: ' in done.stdout and 'verdict: ' in done.stdout


def test_tally_skips_competitors_txt_and_no_other_stray_file(twin):
    import triggers
    runs, tscratch = twin
    write_trigger_rep(runs, tscratch)
    (runs / 'competitors.txt').write_text('skill-creator abc\n')
    assert triggers.tally(runs)['cells'][('P1', 'old', 'full', SONNET)]['reps'] == 1
    for stray in ('notes.txt', 'competitors.txt.bak'):
        (runs / stray).write_text('x\n')
        with pytest.raises(SystemExit, match=stray.replace('.', r'\.')):
            triggers.tally(runs)
        (runs / stray).unlink()
    (runs / 'competitors.txt').unlink()
    (runs / 'competitors.txt').mkdir()
    with pytest.raises(SystemExit, match='competitors'):
        triggers.tally(runs)


def test_tally_refuses_an_unknown_folder(twin):
    import triggers
    runs, tscratch = twin
    write_trigger_rep(runs, tscratch)
    (runs / 'P9').mkdir()
    with pytest.raises(SystemExit, match='P9'):
        triggers.tally(runs)


# --- sheets.py ---------------------------------------------------------------------------------------------


def build(tmp: Path, runs: Path, seed: str = 'seed-1') -> tuple[Path, dict]:
    sheet_dir = tmp / 'grading' / 'sheets'
    sheets.build(runs, sheet_dir, seed)
    return sheet_dir, json.loads((tmp / 'grading' / 'key.json').read_text())


def test_sheets_hide_the_arm(tmp_path, world):
    runs, scratch = world
    # Two answers that differ only in the path under the skill copy: its root, its spelling and its folder.
    spellings = {'old': f'{SKILL}/references/discovery.md', 'new': 'writing-skills/references/discovery.md'}
    for arm, path in spellings.items():
        final = f'I read `{path}`. See [{path}]({path}) and {path}.'
        diff = f'+Design after {path}, as\n+{path} says.\n'
        write_t_rep(runs, scratch, case='M1', arm=arm, calls=[('Read', {'file_path': path})], final=final, diff=diff)
    sheet_dir, key = build(tmp_path, runs)
    sheet_files = sorted(sheet_dir.iterdir())
    assert len(sheet_files) == 2
    first, second = (p.read_bytes() for p in sheet_files)
    assert first == second
    text = first.decode()
    assert 'Case: M1' in text
    assert '<skill>/discovery.md' in text
    assert 'references/discovery' not in text and 'writing-skills' not in text and 'wst107' not in text
    assert sorted(entry['arm'] for entry in key.values()) == ['new', 'old']
    assert all(len(name) == 6 and int(name, 16) >= 0 for name in key)
    assert sorted(p.stem for p in sheet_files) == sorted(key)


@pytest.mark.parametrize(('text', 'want'), [
    ('~/.claude/skills/writing-skills/references/discovery.md', '<skill>/discovery.md'),
    ('read micro-tests.md.', 'read <skill>/micro-tests.md.'),
    ('(../discovery.md)', '(<skill>/discovery.md)'),
    ('"file_path": "/tmp/wst107-skill/writing-skills/references/micro-tests.md"',
     '"file_path": "<skill>/micro-tests.md"'),
    ('**references/claude-code.md**', '**<skill>/claude-code.md**'),
    ('+references/bulletproofing.md', '+<skill>/bulletproofing.md'),
    ('<skill>/discovery.md', '<skill>/discovery.md'),
    ('see old-discovery.md and discovery.md.bak', 'see old-discovery.md and discovery.md.bak'),
    ('/private/tmp/wst107-skill/writing-skills/SKILL.md', '<skill>/SKILL.md'),
    ('skills/parquet-schema-check/SKILL.md and SKILL.md', 'skills/parquet-schema-check/SKILL.md and SKILL.md'),
    ('the LICENSE file', 'the LICENSE file'),
])
def test_sheet_mask_writes_each_skill_path_as_skill_and_basename(text, want):
    assert sheets.mask(text) == want


def test_a_green_answer_that_names_micro_tests_keeps_the_name_and_hides_the_path(tmp_path, world):
    # Review Focus 5: the name still shows the arm, a limit the record reports. The path never does.
    runs, scratch = world
    write_t_rep(runs, scratch, case='M1', arm='new', final=f'I followed {SKILL}/references/micro-tests.md.')
    sheet_dir, _ = build(tmp_path, runs)
    [sheet] = sheet_dir.iterdir()
    assert 'I followed <skill>/micro-tests.md.' in sheet.read_text()


def test_sheets_skip_void_reps_and_hold_the_answer(tmp_path, world):
    runs, scratch = world
    write_t_rep(runs, scratch, case='T2', final='Rewrote it.', diff='+prompts that should load\n')
    write_t_rep(runs, scratch, case='T2', n=2, extra=[json.dumps(RESULT)])
    write_t_rep(runs, scratch, case='M1', final='Wrote the design.', diff='+# Design\n')
    sheet_dir, key = build(tmp_path, runs)
    assert sorted((e['case'], e['rep']) for e in key.values()) == [('M1', 1), ('T2', 1)]
    texts = {key[p.stem]['case']: p.read_text() for p in sheet_dir.iterdir()}
    assert 'Rewrote it.' in texts['T2'] and '+prompts that should load' in texts['T2']
    assert 'Wrote the design.' in texts['M1'] and '+# Design' in texts['M1']
    for case, text in texts.items():
        pass_line, fail_line = cases.COLUMNS[case]
        assert text.startswith(f'Case: {case}\n')
        assert f'PASS: {pass_line}' in text and f'FAIL: {fail_line}' in text
        assert SONNET not in text and 'rep1' not in text
    assert key and all(e['reads'] in (None, True, False) for e in key.values())
    m1 = next(e for e in key.values() if e['case'] == 'M1')
    assert m1['reads'] is False and m1['model'] == SONNET and m1['arm'] == 'old'


def test_sheets_record_whether_the_rep_read_the_reference_in_the_key_only(tmp_path, world):
    runs, scratch = world
    write_t_rep(runs, scratch, case='T2', calls=[('Read', {'file_path': f'{SKILL}/references/discovery.md'})])
    write_t_rep(runs, scratch, case='T2', n=2)
    sheet_dir, key = build(tmp_path, runs)
    assert sorted(e['reads'] for e in key.values()) == [False, True]
    for sheet in sheet_dir.iterdir():
        assert 'reads' not in sheet.read_text().lower().split('--- final message ---')[0]


def test_a_read_that_returned_an_error_does_not_count_as_a_read_of_the_reference(tmp_path, world):
    runs, scratch = world
    write_t_rep(runs, scratch, case='T2', calls=[('Read', {'file_path': f'{SKILL}/references/discovery.md'})],
                errors=(1,))
    write_t_rep(runs, scratch, case='T2', n=2, calls=[('Read', {'file_path': f'{SKILL}/references/discovery.md'}),
                                                       ('Read', {'file_path': f'{SKILL}/references/discovery.md'})],
                errors=(1,))
    _, key = build(tmp_path, runs)
    assert {e['rep']: e['reads'] for e in key.values()} == {1: False, 2: True}


def test_r3_reps_get_no_sheet_and_carry_the_mechanical_verdict_in_the_key(tmp_path, world):
    runs, scratch = world
    write_t_rep(runs, scratch, case='R3', calls=[('Bash', {'command': 'git mv skills/a skills/b'})])
    make_r3_tree(scratch / 'R3' / 'old' / SONNET / 'rep1-folder')
    write_t_rep(runs, scratch, case='R3', n=2)
    bad = make_r3_tree(scratch / 'R3' / 'old' / SONNET / 'rep2-folder')
    (bad / 'AGENTS.md').write_text('csv-dialect-sniff\n')
    write_t_rep(runs, scratch, case='M1')
    sheet_dir, key = build(tmp_path, runs)
    assert len(list(sheet_dir.iterdir())) == 1
    r3 = {e['rep']: e for e in key.values() if e['case'] == 'R3'}
    assert r3[1]['mechanical'] == 'PASS' and r3[2]['mechanical'] == 'FAIL'
    assert next(e for e in key.values() if e['case'] == 'M1')['mechanical'] is None


def test_sheets_skip_a_void_r3_rep_and_an_r3_rep_without_its_parked_tree_is_an_error(tmp_path, world):
    runs, scratch = world
    write_t_rep(runs, scratch, case='R3', calls=[('Bash', {'command': 'ls'})])
    make_r3_tree(scratch / 'R3' / 'old' / SONNET / 'rep1-folder')
    write_t_rep(runs, scratch, case='R3', n=2)
    with pytest.raises(SystemExit, match='rep2'):
        build(tmp_path, runs)


def test_sheets_draw_the_same_ids_from_the_same_seed(tmp_path, world):
    runs, scratch = world
    for n in (1, 2, 3):
        write_t_rep(runs, scratch, case='M1', n=n)
    _, first = build(tmp_path / 'a', runs, 'seed-7')
    _, second = build(tmp_path / 'b', runs, 'seed-7')
    _, other = build(tmp_path / 'c', runs, 'seed-8')
    assert first == second
    assert sorted(first) != sorted(other)
    assert len(set(first)) == 3


def test_sheets_refuse_an_existing_sheet_dir_or_key(tmp_path, world):
    runs, scratch = world
    write_t_rep(runs, scratch, case='M1')
    (tmp_path / 'grading' / 'sheets').mkdir(parents=True)
    with pytest.raises(SystemExit, match='refusing'):
        sheets.build(runs, tmp_path / 'grading' / 'sheets', 's')
    (tmp_path / 'other').mkdir()
    (tmp_path / 'other' / 'key.json').write_text('{}')
    with pytest.raises(SystemExit, match='refusing'):
        sheets.build(runs, tmp_path / 'other' / 'sheets', 's')
    assert not (tmp_path / 'other' / 'sheets').exists()


def test_sheets_refuse_a_sheet_dir_inside_a_repository(tmp_path, world):
    runs, scratch = world
    write_t_rep(runs, scratch, case='M1')
    repo = tmp_path / 'repo'
    repo.mkdir()
    subprocess.run(['git', 'init', '-q', str(repo)], check=True)
    with pytest.raises(SystemExit, match='inside a git repository'):
        sheets.build(runs, repo / 'grading' / 'sheets', 's')
    assert not (repo / 'grading').exists()


def test_sheets_refuse_an_unknown_folder_in_the_runs_root(tmp_path, world):
    runs, scratch = world
    write_t_rep(runs, scratch, case='M1')
    (runs / 'W9').mkdir()
    with pytest.raises(SystemExit, match='W9'):
        sheets.build(runs, tmp_path / 'grading' / 'sheets', 's')
    (runs / 'W9').rmdir()
    (runs / 'P1').mkdir()
    with pytest.raises(SystemExit, match='P1'):
        sheets.build(runs, tmp_path / 'grading' / 'sheets', 's')


def grades_file(tmp: Path, grades: dict[str, str]) -> Path:
    path = tmp / 'grades.tsv'
    path.write_text('id\tgrade\n' + ''.join(f'{sheet}\t{grade}\tnote\n' for sheet, grade in grades.items()))
    return path


def key_file(tmp: Path, key: dict) -> Path:
    path = tmp / 'key.json'
    path.write_text(json.dumps(key))
    return path


def key_entries(case: str, arm: str, model: str, grades_in: list[str], mechanical: bool = False) -> tuple[dict, dict]:
    key, grades = {}, {}
    for n, grade in enumerate(grades_in, 1):
        sheet = hashlib.sha256(f'{case}{arm}{model}{n}'.encode()).hexdigest()[:6]
        key[sheet] = {'case': case, 'arm': arm, 'model': model, 'rep': n, 'reads': None,
                      'mechanical': grade if mechanical else None}
        if not mechanical:
            grades[sheet] = grade
    return key, grades


def cell_grades(case: str, model: str, old: int | None, new: int | None, mechanical: bool = False
                ) -> tuple[dict, dict]:
    key, grades = {}, {}
    for arm, passes in (('old', old), ('new', new)):
        if passes is None:
            continue
        more_key, more_grades = key_entries(case, arm, model, ['PASS'] * passes + ['FAIL'] * (5 - passes), mechanical)
        key.update(more_key)
        grades.update(more_grades)
    return key, grades


def unblind(tmp: Path, key: dict, grades: dict) -> dict:
    return sheets.unblind(grades_file(tmp, grades), key_file(tmp, key))


def test_unblind_refuses_a_missing_or_extra_grade(tmp_path):
    key = {'a1b2c3': {'case': 'M1', 'arm': 'old', 'model': SONNET, 'rep': 1, 'reads': None, 'mechanical': None},
           'd4e5f6': {'case': 'M1', 'arm': 'new', 'model': SONNET, 'rep': 1, 'reads': None, 'mechanical': None}}
    with pytest.raises(SystemExit, match='d4e5f6'):
        sheets.unblind(grades_file(tmp_path, {'a1b2c3': 'PASS'}), key_file(tmp_path, key))
    with pytest.raises(SystemExit, match='ffffff'):
        sheets.unblind(grades_file(tmp_path, {'a1b2c3': 'PASS', 'd4e5f6': 'PASS', 'ffffff': 'FAIL'}),
                       key_file(tmp_path, key))
    with pytest.raises(SystemExit, match='MAYBE'):
        sheets.unblind(grades_file(tmp_path, {'a1b2c3': 'PASS', 'd4e5f6': 'MAYBE'}), key_file(tmp_path, key))
    path = tmp_path / 'twice.tsv'
    path.write_text('a1b2c3\tPASS\na1b2c3\tFAIL\nd4e5f6\tPASS\n')
    with pytest.raises(SystemExit, match='twice'):
        sheets.unblind(path, key_file(tmp_path, key))


def test_unblind_takes_the_grade_as_the_verdict_and_the_read_check_never_scores(tmp_path):
    key, grades = key_entries('T2', 'old', SONNET, ['PASS', 'FAIL', 'PASS'])
    for entry in key.values():
        entry['reads'] = False
    rows = unblind(tmp_path, key, grades)['rows']
    assert [(row['rep'], row['verdict']) for row in rows] == [(1, 'PASS'), (2, 'FAIL'), (3, 'PASS')]


def test_unblind_scores_an_r3_rep_by_its_mechanical_check_without_a_grade(tmp_path):
    key, grades = cell_grades('R3', SONNET, 2, 5, mechanical=True)
    assert grades == {}
    result = unblind(tmp_path, key, grades)
    assert [row['verdict'] for row in result['rows'] if row['arm'] == 'old'] == ['PASS', 'PASS', 'FAIL', 'FAIL', 'FAIL']
    # A grade for a mechanical rep is an extra grade.
    extra = next(iter(key))
    with pytest.raises(SystemExit, match=extra):
        unblind(tmp_path, key, {extra: 'PASS'})


@pytest.mark.parametrize(('old', 'new', 'red', 'green'), [
    (0, 5, True, True), (2, 4, True, True), (2, 3, True, False), (1, 3, True, False), (0, 4, True, True),
    (3, 5, False, None), (5, 5, False, None), (2, 5, True, True), (0, 3, True, False), (2, 2, True, False),
])
def test_unblind_checks_red_and_green_per_model(tmp_path, old, new, red, green):
    key, grades = cell_grades('M1', SONNET, old, new)
    [cell] = unblind(tmp_path, key, grades)['cells']
    assert (cell['case'], cell['model'], cell['old'], cell['new'], cell['old_n'], cell['new_n']) == (
        'M1', SONNET, old, new, 5, 5)
    assert cell['red'] is red and cell['green'] is green


def test_a_cell_with_new_reps_only_has_no_red_and_no_green(tmp_path):
    key, grades = cell_grades('M1', SONNET, None, 5)
    [cell] = unblind(tmp_path, key, grades)['cells']
    assert (cell['old_n'], cell['new_n'], cell['red'], cell['green']) == (0, 5, None, None)


def test_green_needs_new_at_least_two_above_old(tmp_path):
    # old 2 of 5 and new 4 of 5 passes the +2 bar. old 3 is not RED, so there is no GREEN bar.
    key, grades = cell_grades('T2', OPUS, 2, 4)
    assert unblind(tmp_path, key, grades)['cells'][0]['green'] is True
    key, grades = cell_grades('T2', OPUS, 3, 5)
    cell = unblind(tmp_path, key, grades)['cells'][0]
    assert cell['red'] is False and cell['green'] is None


def test_unblind_judges_each_case_red_then_green(tmp_path):
    def judge(opus: tuple, sonnet: tuple) -> dict:
        key, grades = cell_grades('M1', OPUS, *opus)
        more_key, more_grades = cell_grades('M1', SONNET, *sonnet)
        key.update(more_key)
        grades.update(more_grades)
        return unblind(tmp_path, key, grades)['verdicts']['M1']
    assert judge((0, 5), (1, 5)) == {'red': 'shown', 'green': 'met'}
    assert judge((3, 5), (4, 5)) == {'red': 'null', 'green': 'n/a'}
    assert judge((2, 5), (5, 5)) == {'red': 'shown', 'green': 'met'}
    assert judge((1, 3), (0, 5)) == {'red': 'shown', 'green': 'missed'}
    assert judge((1, 5), (2, 3)) == {'red': 'shown', 'green': 'missed'}
    assert judge((4, 5), (2, 4)) == {'red': 'shown', 'green': 'met'}


def test_red_only_grading_reports_red_and_no_green(tmp_path):
    key, grades = cell_grades('M1', SONNET, 1, None)
    result = unblind(tmp_path, key, grades)
    assert result['cells'][0]['red'] is True and result['cells'][0]['green'] is None
    assert result['verdicts']['M1'] == {'red': 'shown', 'green': 'not run'}
    assert result['cells'][0]['new_n'] == 0


def two_models(tmp_path, opus: tuple, sonnet: tuple, case: str = 'M1') -> dict:
    key, grades = cell_grades(case, OPUS, *opus)
    more_key, more_grades = cell_grades(case, SONNET, *sonnet)
    key.update(more_key)
    grades.update(more_grades)
    return unblind(tmp_path, key, grades)['verdicts'][case]


def test_green_is_incomplete_when_a_model_where_red_is_shown_has_no_new_reps(tmp_path):
    # Open item 4: new >= 4 of 5 on each model where RED was shown. Opus alone passing is not enough.
    assert two_models(tmp_path, (0, 5), (1, None)) == {'red': 'shown', 'green': 'incomplete'}
    assert two_models(tmp_path, (1, None), (0, 5)) == {'red': 'shown', 'green': 'incomplete'}
    # A model where RED is not shown needs no new reps.
    assert two_models(tmp_path, (0, 5), (4, None)) == {'red': 'shown', 'green': 'met'}
    # A miss on a graded model is a miss, whatever the other model lacks.
    assert two_models(tmp_path, (0, 2), (1, None)) == {'red': 'shown', 'green': 'missed'}
    # With no new reps on any such model, nothing ran.
    assert two_models(tmp_path, (0, None), (1, None)) == {'red': 'shown', 'green': 'not run'}


def test_green_is_incomplete_when_a_plan_model_was_never_checked_for_red(tmp_path):
    # Open item 4: new >= 4 on each model where RED was shown. A model with no old reps was never checked.
    key, grades = cell_grades('M1', OPUS, 0, 5)
    assert unblind(tmp_path, key, grades)['verdicts']['M1'] == {'red': 'shown', 'green': 'incomplete'}
    more_key, more_grades = cell_grades('M1', SONNET, None, 5)
    key.update(more_key)
    grades.update(more_grades)
    assert unblind(tmp_path, key, grades)['verdicts']['M1'] == {'red': 'shown', 'green': 'incomplete'}
    # A miss still reads missed, and both models checked still read met.
    assert two_models(tmp_path, (0, 2), (4, None)) == {'red': 'shown', 'green': 'missed'}
    assert two_models(tmp_path, (0, 5), (3, None)) == {'red': 'shown', 'green': 'met'}


def test_red_is_incomplete_when_the_other_plan_model_has_no_old_reps_and_none_is_shown(tmp_path):
    # Open item 3: null only when the control passes 3 or more on both models.
    key, grades = cell_grades('M1', SONNET, 3, None)
    assert unblind(tmp_path, key, grades)['verdicts']['M1'] == {'red': 'incomplete', 'green': 'n/a'}
    # RED shown on the one graded model is shown whatever the other lacks.
    key, grades = cell_grades('M1', SONNET, 2, None)
    assert unblind(tmp_path, key, grades)['verdicts']['M1']['red'] == 'shown'
    # Both models graded and neither shown is null.
    assert two_models(tmp_path, (3, None), (5, None)) == {'red': 'null', 'green': 'n/a'}
    # A model with new reps only has no old reps either.
    key, grades = cell_grades('M1', OPUS, 4, None)
    more_key, more_grades = cell_grades('M1', SONNET, None, 5)
    key.update(more_key)
    grades.update(more_grades)
    assert unblind(tmp_path, key, grades)['verdicts']['M1']['red'] == 'incomplete'


def test_unblind_counts_only_the_reps_it_was_given(tmp_path):
    key, grades = key_entries('M1', 'old', SONNET, ['PASS'] * 6)
    more_key, more_grades = key_entries('M1', 'new', SONNET, ['PASS'] * 4)
    key.update(more_key)
    grades.update(more_grades)
    [cell] = unblind(tmp_path, key, grades)['cells']
    assert (cell['old_n'], cell['new_n'], cell['complete']) == (6, 4, False)
    key, grades = cell_grades('M1', SONNET, 0, 5)
    assert unblind(tmp_path, key, grades)['cells'][0]['complete'] is True


def test_sheets_command_builds_and_unblinds(tmp_path, world):
    runs, scratch = world
    write_t_rep(runs, scratch, case='M1', final='Designed.')
    sheet_dir = tmp_path / 'grading' / 'sheets'
    env = {**os.environ, 'WST_SCRATCH': str(scratch)}
    done = kit_tool(str(KIT / 'sheets.py'), 'build', str(runs), str(sheet_dir), 'seed-1', env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    [sheet] = sheet_dir.iterdir()
    grades = grades_file(tmp_path, {sheet.stem: 'PASS'})
    done = kit_tool(str(KIT / 'sheets.py'), 'unblind', str(grades), str(tmp_path / 'grading' / 'key.json'), env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    assert f'M1 old {SONNET} rep1: PASS' in done.stdout
    assert 'RED' in done.stdout


# --- build_prompts.py, rep_tools.py place-copy and check-copy -----------------------------------------------

SKILL_TEXT = '---\nname: writing-skills\ndescription: Use when testing the kit\n---\n\n# Writing Skills\n\nBody.\n'


def make_repo(tmp: Path) -> tuple[Path, str]:
    repo = tmp / 'repo'
    skill = repo / 'skills' / 'writing-skills'
    (skill / 'references').mkdir(parents=True)
    (skill / 'scripts').mkdir()
    (skill / 'SKILL.md').write_text(SKILL_TEXT)
    (skill / 'references' / 'discovery.md').write_text('# Discovery\n')
    (skill / 'references' / 'flowcharts.md').write_text('# Flowcharts\n')
    (skill / 'scripts' / 'render_graphs.py').write_text('print(1)\n')
    (skill / 'scripts' / 'render_graphs.py').chmod(0o755)
    (repo / 'specs' / 'plans').mkdir(parents=True)
    (repo / 'specs' / 'plans' / 'plan.md').write_text('the plan, which no rep may read\n')
    git = ['git', '-C', str(repo), '-c', 'user.name=t', '-c', 'user.email=t@example.invalid', '-c', 'commit.gpgsign=false']
    subprocess.run(['git', 'init', '-q', str(repo)], check=True)
    subprocess.run(git + ['add', '-A'], check=True)
    subprocess.run(git + ['commit', '-q', '-m', 'start'], check=True)
    sha = subprocess.run(['git', '-C', str(repo), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    return repo, sha


@pytest.fixture
def repo_env(tmp_path: Path) -> tuple[dict, Path, str]:
    repo, sha = make_repo(tmp_path)
    env = {**os.environ, 'WST_REPO': str(repo), 'WST_SKILL_ROOT': str(tmp_path / 'skill-root')}
    return env, tmp_path / 'skill-root', sha


def build_prompts(env: dict, *args: str) -> subprocess.CompletedProcess:
    return kit_tool(str(KIT / 'build_prompts.py'), *args, env=env)


def place_copy(env: dict, ref: str = 'HEAD') -> subprocess.CompletedProcess:
    return kit_tool(str(KIT / 'rep_tools.py'), 'place-copy', ref, env=env)


def check_copy(env: dict, manifest: Path, *prompt: Path) -> subprocess.CompletedProcess:
    return kit_tool(str(KIT / 'rep_tools.py'), 'check-copy', str(manifest), *map(str, prompt), env=env)


def manifest_lines(out: Path) -> list[str]:
    return (out / 'MANIFEST.txt').read_text().splitlines()


def test_build_prompts_refuses_existing_out_dir(tmp_path, repo_env):
    env, _, _ = repo_env
    out = tmp_path / 'prompts-old'
    out.mkdir()
    done = build_prompts(env, 'HEAD', 'old', str(out))
    assert done.returncode != 0
    assert 'refusing' in done.stdout + done.stderr
    assert list(out.iterdir()) == []


def test_build_prompts_refuses_an_unknown_arm(tmp_path, repo_env):
    env, _, _ = repo_env
    done = build_prompts(env, 'HEAD', 'control', str(tmp_path / 'prompts'))
    assert done.returncode != 0 and 'refusing' in done.stdout + done.stderr
    assert not (tmp_path / 'prompts').exists()


@pytest.mark.parametrize('arm', ['old', 'new', 'pilot'])
def test_build_prompts_writes_three_prompts_and_the_manifest(tmp_path, repo_env, arm):
    env, root, sha = repo_env
    out = tmp_path / f'prompts-{arm}'
    done = build_prompts(env, 'HEAD', arm, str(out))
    assert done.returncode == 0, done.stdout + done.stderr
    assert sorted(p.name for p in out.iterdir()) == ['M1.txt', 'MANIFEST.txt', 'R3.txt', 'T2.txt']
    body = SKILL_TEXT.split('\n---\n', 1)[1]
    for case in ('M1', 'T2', 'R3'):
        text = (out / f'{case}.txt').read_text()
        assert f'<skill name="writing-skills">\nBase directory for this skill: {root}/writing-skills\n\n# Writing Skills' in text
        assert cases.CASES[case].strip() in text
        assert cases.TOOLS_TEXT[case] in text
    lines = manifest_lines(out)
    assert lines[:2] == [f'ref {sha}', f'arm {arm}']
    assert f'body-sha256 {sha256(body.encode())}' in lines
    assert f'skill-copy-root {root}' in lines
    copies = sorted(line.split()[1] for line in lines if line.startswith('skill-copy '))
    assert copies == ['writing-skills/SKILL.md', 'writing-skills/references/discovery.md',
                      'writing-skills/references/flowcharts.md', 'writing-skills/scripts/render_graphs.py']
    assert f'skill-copy writing-skills/SKILL.md {sha256(SKILL_TEXT.encode())} skills/writing-skills/SKILL.md@{sha}' in lines
    for name in ('M1.txt', 'T2.txt', 'R3.txt'):
        assert f'prompt {name} {sha256((out / name).read_bytes())}' in lines
    # The repository's specs/ reaches no prompt and no skill copy line.
    assert all('the plan, which no rep may read' not in p.read_text() for p in out.iterdir())
    assert not any('specs/' in line for line in lines)


def test_place_copy_puts_the_archive_under_writing_skills(tmp_path, repo_env):
    env, root, _ = repo_env
    out = tmp_path / 'prompts-new'
    assert build_prompts(env, 'HEAD', 'new', str(out)).returncode == 0
    done = place_copy(env)
    assert done.returncode == 0, done.stdout + done.stderr
    assert sorted(str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()) == [
        'writing-skills/SKILL.md', 'writing-skills/references/discovery.md', 'writing-skills/references/flowcharts.md',
        'writing-skills/scripts/render_graphs.py']
    assert os.access(root / 'writing-skills' / 'scripts' / 'render_graphs.py', os.X_OK)
    assert (root / 'writing-skills' / 'SKILL.md').read_text() == SKILL_TEXT
    done = check_copy(env, out / 'MANIFEST.txt', out / 'M1.txt')
    assert done.returncode == 0, done.stdout + done.stderr


def test_place_copy_refuses_non_empty_root(repo_env):
    env, root, _ = repo_env
    root.mkdir()
    (root / 'stray.md').write_text('left by another arm\n')
    done = place_copy(env)
    assert done.returncode == 3, done.stdout + done.stderr
    assert 'not empty' in done.stdout + done.stderr
    assert sorted(p.name for p in root.iterdir()) == ['stray.md']


def test_place_copy_refuses_a_leftover_empty_folder(repo_env):
    env, root, _ = repo_env
    (root / 'writing-skills').mkdir(parents=True)
    done = place_copy(env)
    assert done.returncode == 3, done.stdout + done.stderr
    assert list((root / 'writing-skills').iterdir()) == []


def test_place_copy_defaults_to_the_plan_107_root():
    import rep_tools
    assert rep_tools.DEFAULT_SKILL_ROOT == '/private/tmp/wst107-skill'


def test_build_prompts_refuses_an_out_dir_that_is_a_file(tmp_path, repo_env):
    env, _, _ = repo_env
    out = tmp_path / 'prompts-old'
    out.write_text('not a folder\n')
    done = build_prompts(env, 'HEAD', 'old', str(out))
    assert done.returncode != 0 and 'refusing' in done.stdout + done.stderr
    assert out.read_text() == 'not a folder\n'


def test_place_copy_refuses_an_unknown_ref(repo_env):
    env, root, _ = repo_env
    done = place_copy(env, 'no-such-ref')
    assert done.returncode != 0
    assert not (root / 'writing-skills').exists()


def test_check_copy_refuses_changed_copy(tmp_path, repo_env):
    env, root, _ = repo_env
    out = tmp_path / 'prompts-old'
    assert build_prompts(env, 'HEAD', 'old', str(out)).returncode == 0
    assert place_copy(env).returncode == 0
    manifest, prompt, copy = out / 'MANIFEST.txt', out / 'T2.txt', root / 'writing-skills'
    assert check_copy(env, manifest, prompt).returncode == 0
    (copy / 'references' / 'discovery.md').write_text('# Discovery, edited\n')
    done = check_copy(env, manifest, prompt)
    assert done.returncode == 1 and 'skill copy file changed' in done.stdout
    (copy / 'references' / 'discovery.md').unlink()
    done = check_copy(env, manifest, prompt)
    assert done.returncode == 1 and 'skill copy file missing' in done.stdout
    (copy / 'references' / 'discovery.md').write_text('# Discovery\n')
    (root / 'plan.md').write_text('a stray file beside the copy\n')
    done = check_copy(env, manifest, prompt)
    assert done.returncode == 1 and 'does not list' in done.stdout
    (root / 'plan.md').unlink()
    prompt.write_text(prompt.read_text() + 'one more line\n')
    done = check_copy(env, manifest, prompt)
    assert done.returncode == 1 and 'prompt changed' in done.stdout


def test_build_prompts_reads_this_repository(tmp_path):
    env = {**os.environ, 'WST_SKILL_ROOT': str(tmp_path / 'skill-root')}
    env.pop('WST_REPO', None)
    out = tmp_path / 'prompts-pilot'
    done = build_prompts(env, 'HEAD', 'pilot', str(out))
    assert done.returncode == 0, done.stdout + done.stderr
    lines = manifest_lines(out)
    copies = [line.split()[1] for line in lines if line.startswith('skill-copy ')]
    assert 'writing-skills/SKILL.md' in copies
    assert all(rel.startswith('writing-skills/') for rel in copies)
    assert '# Writing Skills' in (out / 'M1.txt').read_text()


# --- cases.py, trigger_prompts.py and the fixtures ---------------------------------------------------------------

# Each case's PASS-part tokens. A fixture or a case text that holds one could hand the rep its pass
# without the skill text it is testing.
PASS_TOKENS = {
    'M1': r'(?i)raw api|setting.sources|isolat|quarantin|blind|fresh (?:directory|context)|new subagent|\bmodels?\b|'
          r'user.level|auto.memory|pass rule|fail rule',
    'T2': r'(?i)should not load|near.miss|negative (?:prompt|example)|trigger test|old description|new description|'
          r'with the skill (?:on|off)',
}


def test_the_case_frame_makes_the_changes_a_session_with_tools_needs():
    frame = cases.FRAME_T
    assert '<skill name="writing-skills">\nBase directory for this skill: {base}\n\n{body}\n</skill>' in frame
    assert 'your tools are {tools}' in frame and "your partner's project" in frame
    assert frame.endswith('It is your turn. Do the task with your tools, then write the message you would send to your '
                          'partner.\n')
    assert 'You have no tools' not in frame and 'ACTION:' not in frame and '~/.claude' not in frame


def test_the_tools_sentence_follows_the_case():
    assert cases.TOOLS_TEXT['M1'] == cases.TOOLS_TEXT['T2'] == 'Read, Glob, Grep, Edit and Write'
    assert 'Bash' in cases.TOOLS_TEXT['R3'] and 'git mv' in cases.TOOLS_TEXT['R3']
    assert cases.TOOLS_TEXT['R3'].startswith('Read, Glob, Grep, Edit and Write')


def test_each_case_names_its_target_and_the_fixture_holds_its_project():
    assert sorted(cases.CASES) == sorted(cases.TARGET) == sorted(cases.PASS) == sorted(cases.REFERENCE) == [
        'M1', 'R3', 'T2']
    assert cases.TARGET['M1'] == 'specs/changelog-entry-microtest.md'
    assert cases.TARGET['T2'] == 'skills/parquet-schema-check/SKILL.md'
    assert cases.TARGET['R3'] == 'the rep\'s repository'
    for case, text in cases.CASES.items():
        repo = KIT / 'fixtures' / case / 'repo'
        assert repo.is_dir()
        assert cases.REFERENCE[case] not in text
        if case != 'R3':
            assert f'`{cases.TARGET[case]}`' in text
    assert (KIT / 'fixtures' / 'M1' / 'repo' / 'skills' / 'changelog-entry' / 'SKILL.md').is_file()
    assert (KIT / 'fixtures' / 'M1' / 'repo' / 'specs' / 'changelog-entry-wording.md').is_file()
    assert (KIT / 'fixtures' / 'T2' / 'repo' / 'skills' / 'parquet-schema-check' / 'SKILL.md').is_file()
    assert (KIT / 'fixtures' / 'T2' / 'repo' / 'skills' / 'polars-lazy-tuning' / 'SKILL.md').is_file()
    # M1's target does not exist before the rep, and the partner says not to run anything.
    assert not (KIT / 'fixtures' / 'M1' / 'repo' / cases.TARGET['M1']).exists()
    assert "Don't run anything yet." in cases.CASES['M1']


def test_the_cases_are_the_plans_conversations():
    # The partner's words are the plan's. Each case adds one "[you, tools]" line that says the earlier steps are done.
    assert cases.CASES['M1'].strip().split('\n\n')[0] == (
        'Partner: We want to change one line in `skills/changelog-entry/SKILL.md`. The proposal is in '
        '`specs/changelog-entry-wording.md`. Before I merge it, design the micro-test that will tell us whether the '
        'new wording works. Write the design to `specs/changelog-entry-microtest.md`. Don\'t run anything yet.')
    assert cases.CASES['T2'].strip().split('\n\n')[0] == (
        'Partner: Agents never load our `parquet-schema-check` skill, even when they\'re about to write a parquet '
        'file that breaks the schema. Fix it.')
    assert cases.CASES['R3'].strip().split('\n\n')[0] == (
        'Partner: Rename our `csv-dialect-sniff` skill to `sniffing-csv-dialects`.')
    for case in ('M1', 'T2', 'R3'):
        parts = cases.CASES[case].strip().split('\n\n')
        assert len(parts) == 2 and parts[1].startswith('[you, tools] '), case


def test_the_you_tools_lines_state_the_earlier_steps_without_handing_over_a_pass_part():
    t2 = cases.CASES['T2'].strip().split('\n\n')[1]
    assert t2 == ('[you, tools] You ran the baseline earlier. Your partner read the results. The skill is '
                  '`skills/parquet-schema-check/SKILL.md`.')
    assert not re.search(r'\d+ of \d+|\bwithout loading\b|\bruns?\b.*\bloa', t2.replace('ran the baseline', ''))
    # M1 keeps its line, and R3 says the needed earlier step is done, in the same form.
    assert 'in 7 of 10 runs' in cases.CASES['M1']
    r3 = cases.CASES['R3'].strip().split('\n\n')[1]
    assert r3.startswith('[you, tools] ') and 'earlier' in r3 and 'read' in r3
    assert 'discovery' not in r3 and 'grep' not in r3.lower()


def test_each_case_states_its_pass_parts():
    assert len(cases.PASS['M1']) == 3 and len(cases.PASS['T2']) == 2
    joined = ' '.join(cases.PASS['M1'])
    for need in ('raw API call', 'fixes the pass and fail rule before any reply is read', 'at least two models'):
        assert need in joined
    joined = ' '.join(cases.PASS['T2'])
    assert 'at least three prompts that should load the skill' in joined and 'at least one that should not' in joined
    assert 'old description' in joined and 'new one' in joined
    assert 'csv-dialect-sniff' in ' '.join(cases.PASS['R3']) and len(cases.PASS['R3']) == 3
    assert cases.COLUMNS['M1'][0].count('(') >= 3


def test_every_graded_case_has_its_pass_and_fail_columns():
    assert sorted(cases.COLUMNS) == ['M1', 'T2']
    for pass_line, fail_line in cases.COLUMNS.values():
        assert pass_line and fail_line
    assert '`<skill>/micro-tests.md`' not in cases.COLUMNS['M1'][0]


def test_r3_fixture_is_the_plans_repository():
    repo = KIT / 'fixtures' / 'R3' / 'repo'
    assert (repo / 'skills' / 'csv-dialect-sniff' / 'SKILL.md').is_file()
    assert 'name: csv-dialect-sniff' in (repo / 'skills' / 'csv-dialect-sniff' / 'SKILL.md').read_text()
    assert '**REQUIRED SUB-SKILL:** Use csv-dialect-sniff' in (repo / 'skills' / 'ingest-raw-files' / 'SKILL.md').read_text()
    assert (repo / 'skills' / 'sniffing-csv-headers' / 'SKILL.md').is_file()
    assert 'csv-dialect-sniff' in (repo / 'commands' / 'ingest.md').read_text()
    assert 'csv-dialect-sniff' in (repo / 'AGENTS.md').read_text()
    assert json.loads((repo / '.claude' / 'settings.json').read_text()) == {
        'skillOverrides': {'csv-dialect-sniff': 'name-only'}}
    # The checker finds the old name in every file the plan lists, and the near collision is not the old name.
    holders = sorted(str(p.relative_to(repo)) for p in repo.rglob('*') if p.is_file()
                     and 'csv-dialect-sniff' in p.read_text())
    assert holders == ['.claude/settings.json', 'AGENTS.md', 'commands/ingest.md',
                       'skills/csv-dialect-sniff/SKILL.md', 'skills/ingest-raw-files/SKILL.md']
    assert 'csv-dialect-sniff' not in (repo / 'skills' / 'sniffing-csv-headers' / 'SKILL.md').read_text()


def test_the_trigger_fixture_holds_the_four_skills_and_a_readme():
    repo = KIT / 'fixtures' / 'trigger' / 'repo'
    assert sorted(p.name for p in (repo / 'skills').iterdir()) == ['fixture-loader', 'release-notes', 'retry-budget',
                                                                   'table-diff']
    for name in ('fixture-loader', 'release-notes', 'retry-budget', 'table-diff'):
        text = (repo / 'skills' / name / 'SKILL.md').read_text()
        assert text.startswith(f'---\nname: {name}\ndescription: ')
    assert (repo / 'README.md').is_file()


@pytest.mark.parametrize('case', ['M1', 'T2'])
def test_fixtures_and_case_texts_hold_no_pass_token(case):
    token = re.compile(PASS_TOKENS[case])
    texts = {f'CASES[{case}]': cases.CASES[case]}
    for path in sorted((KIT / 'fixtures' / case).rglob('*')):
        if path.is_file():
            texts[str(path.relative_to(KIT))] = path.read_text()
    found = {name: token.findall(text) for name, text in texts.items() if token.search(text)}
    assert found == {}


def test_trigger_fixture_and_prompts_hold_no_writing_skills_name():
    import trigger_prompts
    repo = KIT / 'fixtures' / 'trigger' / 'repo'
    texts = list(trigger_prompts.PROMPTS.values()) + [p.read_text() for p in repo.rglob('*') if p.is_file()]
    assert all('writing-skills' not in text and 'micro-test' not in text.lower() for text in texts)


def domain_hits(word: str, text: str) -> int:
    return len(re.findall(rf'\b{re.escape(word.casefold())}\b', text.casefold()))


# Task 1 Step 4: no domain repeats the skill's own examples, plan 72's cases or plan 105's cases. The lists hold
# distinctive words only, taken from those plans' frozen kits, so this test never reads the live skill.
PLAN_72_105_WORDS = (
    'migration-dry-run', 'cache-invalidation', 'release-notes-gate', 'purging', 'dry-run',
    'secrets-scan-gate', 'gitleaks', 'http-retry-policy', 'idempotency', 'lockfile-refresh', 'uv lock', 'tide-tables',
)
SKILL_EXAMPLE_WORDS = (
    'condition-based', 'root-cause', 'flatten-with-flags', 'test-invariants', 'defensive-programming', 'flaky',
    'async-test-helpers', 'race condition', 'race conditions', 'setTimeout', 'React Router', 'ENOTEMPTY',
    'payment-system', 'debugging-with-logs', 'data-structure-refactoring',
)
# The new text of Tasks 3 to 5: no case or fixture may hold its distinctive terms.
NEW_TEXT_WORDS = ('micro-tests.md', 'quarantine', 'trigger test', 'rename procedure')


def all_case_texts() -> dict[str, str]:
    import trigger_prompts
    texts = {f'CASES[{case}]': text for case, text in cases.CASES.items()}
    texts.update({f'PROMPTS[{name}]': text for name, text in trigger_prompts.PROMPTS.items()})
    for path in sorted((KIT / 'fixtures').rglob('*')):
        if path.is_file():
            texts[str(path.relative_to(KIT))] = path.read_text()
    return texts


@pytest.mark.parametrize('words', [PLAN_72_105_WORDS, SKILL_EXAMPLE_WORDS, NEW_TEXT_WORDS])
def test_no_domain_repeats_an_earlier_case_the_skills_examples_or_the_new_text(words):
    found = {(name, word) for name, text in all_case_texts().items() for word in words if domain_hits(word, text)}
    assert found == set()


# --- the kit's own files ---------------------------------------------------------------------------------------


def test_the_kit_holds_no_user_path_and_names_its_roots():
    for path in sorted(KIT.iterdir()):
        if path.suffix in ('.py', '.sh', '.txt') and path.name != 'test_wst_kit.py':
            text = path.read_text()
            assert '/Users/' not in text.replace('//Users/**', '').replace('(//Users', ''), path.name
    common = (KIT / 'common.sh').read_text()
    assert '/private/tmp/wst107' in common and 'plan107/cases' in common
    assert '/private/tmp/wst107t' in (RUN_TRIGGERS).read_text() or 'wst107t' in common
    assert 'plan107/triggers' in common or 'plan107/triggers' in RUN_TRIGGERS.read_text()


def test_no_kit_file_keeps_a_plan_105_root():
    for path in sorted(KIT.iterdir()):
        if path.is_file() and path.suffix in ('.py', '.sh') and path.name != 'test_wst_kit.py':
            assert 'wsl105' not in path.read_text() and 'WSL_' not in path.read_text(), path.name
