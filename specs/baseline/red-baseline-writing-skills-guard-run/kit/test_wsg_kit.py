'''Self-tests for plan 108's micro-test kit, on synthetic records and folders. No test runs a model.

The runner tests start a stub claude (a bash script given as CLAUDE_BIN) with every root, scratch and
fixture path moved into the test's temporary folder (the WST_* variables). A runner starts the stub under
`env -i`, so every path the stub needs is written into its text. The audit and sheet tests call the kit's
Python in-process, on synthetic records. Source: plan 107's kit tests
(specs/baseline/red-baseline-writing-skills-tests/kit/test_wst_kit.py), copied with their case-mode parts
only: the trigger runner, the Bash audit and the R3 tree check are gone. Plan 108's Task 1 adds the cases
G1, L2 and F3, the no-loss bar, the classifying-word check and the plan 107 root check.
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
PROBE_TOOLS = KIT / 'probe_tools.sh'
SONNET, OPUS = 'claude-sonnet-5-5', 'claude-opus-5-5'
FIELD = 'credential_expires_at'
TOOLS = 'Read,Glob,Grep,Edit,Write'
CROSS_SESSION_TOOLS = ('ListAgents', 'SendMessage', 'PushNotification', 'RemoteTrigger')
PATH_RULES = ('Read(//Users/**)', 'Edit(//Users/**)', 'Write(//Users/**)', 'Read(~/Library/**)',
              'Edit(~/Library/**)', 'Write(~/Library/**)')
SHELL_ADDED = {'PWD', 'SHLVL', '_', 'OLDPWD'}
KEEP = ('HOME', 'USER', 'LOGNAME', 'PATH', 'SHELL', 'TMPDIR', 'LANG')
DISABLE = ('CLAUDE_CODE_DISABLE_ADVISOR_TOOL', 'CLAUDE_CODE_DISABLE_AUTO_MEMORY')
REP_DIR = '/private/tmp/wst108/rep1'
SKILL_ROOT = '/private/tmp/wst108-skill'
SKILL = f'{SKILL_ROOT}/writing-skills'
CASE_NAMES = ('F3', 'G1', 'L2')


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(cmd: list[str], env: dict | None = None, cwd: Path = KIT, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, env=env, cwd=cwd, capture_output=True, text=True, check=False, timeout=timeout)


def kit_tool(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return run(['uv', 'run', '--no-project', '-q', 'python', *args], env=env)


# --- common.sh, run_tool_reps.sh and probe_tools.sh: plan 107's runner tests, renamed ------------------------

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

    def fixture(self, name: str = 'G1', arm: str = 'old') -> None:
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

    def out(self, name: str = 'G1', arm: str = 'old', model: str = SONNET) -> Path:
        return self.tmp / 'out' / name / arm / model

    def run(self, name: str = 'G1', first: int = 1, last: int = 1, model: str = SONNET, out: Path | None = None
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

    def summary(self, rep: int = 1, name: str = 'G1') -> dict:
        return json.loads((self.out(name) / f'rep{rep}' / 'summary.json').read_text())

    def stream(self, rep: int = 1, name: str = 'G1') -> Path:
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
    parked = tkit.scratch / 'G1' / 'old' / SONNET / 'rep1-folder'
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


def test_every_case_gets_the_five_tools_and_no_bash(tmp_path):
    # Plan 108 (D-c): every case gets Read, Glob, Grep, Edit and Write, and none gets Bash.
    for case in CASE_NAMES:
        kit = ToolKit(tmp_path / case)
        kit.fixture(case)
        tools_ok(kit, name=case)
        args = kit.args()
        assert args[args.index('--tools') + 1] == TOOLS, case
        assert args[args.index('--allowedTools') + 1] == TOOLS, case
        summary = kit.summary(name=case)
        assert 'r3_check' not in summary and 'condition' not in summary, case
        assert summary['case'] == case


def test_rep_env_holds_only_the_pinned_names(tkit):
    tools_ok(tkit)
    env = dict(line.split('=', 1) for line in (tkit.stub_dir / 'env.1').read_text().splitlines() if '=' in line)
    assert set(env) - SHELL_ADDED <= TOOL_ENV
    folder = os.path.realpath(tkit.root / 'rep1')
    assert env['HOME'] == f'{folder}/home'
    assert env['TMPDIR'] == f'{folder}/tmp'
    assert env['PATH'] == '/usr/bin:/bin:/usr/sbin:/sbin'
    assert env['CLAUDE_CODE_DISABLE_AUTO_MEMORY'] == '1'
    assert os.readlink(tkit.scratch / 'G1' / 'old' / SONNET / 'rep1-folder' / 'home' / 'Library'
                       / 'Keychains') == str(tkit.real / 'Library' / 'Keychains')


def test_the_rep_starts_in_its_fixture_committed_as_base(tkit):
    tkit.actions(f'git log --format=%s > \'{tkit.tmp}/log.txt\'; ls -A > \'{tkit.tmp}/ls.txt\'\n')
    tools_ok(tkit)
    assert (tkit.tmp / 'log.txt').read_text() == 'Start the project\n'
    assert sorted((tkit.tmp / 'ls.txt').read_text().split()) == ['.git', 'notes.txt', 'specs']
    summary = tkit.summary()
    assert len(summary['base']) == 40
    assert summary['case'] == 'G1' and summary['arm'] == 'old' and summary['model'] == SONNET
    assert 'condition' not in summary
    # summary.json is scrubbed, and the scrub writes pytest-of-<user> as pytest-of-$USER.
    user = os.environ.get('USER') or 'tester'
    assert summary['skill_root'] == str(tkit.skill).replace(f'pytest-of-{user}', 'pytest-of-$USER')
    assert (tkit.scratch / 'G1' / 'old' / SONNET / 'rep1.prompt.txt').read_text() == 'Do the task.\n'


@pytest.mark.parametrize('where', ['case', 'arm', 'model'])
def test_refuses_an_out_dir_that_misnames_the_case_arm_or_model(tkit, where):
    names = {'case': 'G1', 'arm': 'old', 'model': SONNET}
    names[where] = {'case': 'L2', 'arm': 'new', 'model': OPUS}[where]
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
    use = {'type': 'tool_use', 'id': 't1', 'name': 'Read', 'input': {'file_path': '/nowhere/micro-tests.md'}}
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


# --- audit.py: the stream audit (V9 and record counts) -----------------------------------------------------

REP_TOOLS = ('Read', 'Glob', 'Grep', 'Edit', 'Write')
RESULT = {'type': 'result', 'subtype': 'success', 'is_error': False, 'result': 'Done.', 'total_cost_usd': 0.01}


def stream_lines(calls=(), errors=(), extra=(), result=None, init_tools=REP_TOOLS) -> list[str]:
    init = {'type': 'system', 'subtype': 'init', 'tools': list(init_tools)}
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


def write_t_rep(runs: Path, scratch: Path, case: str = 'G1', arm: str = 'old', model: str = SONNET, n: int = 1,
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


@pytest.fixture
def world(tmp_path: Path, monkeypatch) -> tuple[Path, Path]:
    runs, scratch = tmp_path / 'runs', tmp_path / 'scratch'
    monkeypatch.setenv('WST_SCRATCH', str(scratch))
    return runs, scratch


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
    ('Glob', {'pattern': '{/private/tmp/wst108/rep2,x}/**'}, ('outside the allowed roots',)),
    ('Glob', {'pattern': '{x,y,/tmp/wst108/rep2/repo}/*'}, ('outside the allowed roots',)),
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
    ('Grep', {'pattern': 'plan', 'path': '/tmp/wst108/rep1/repo/skills'}),
    ('Glob', {'pattern': '**/*.md'}),
    ('Glob', {'pattern': f'{SKILL}/**/*.md'}),
    ('Glob', {'pattern': '/tmp/wst108-skill/writing-skills/*.dot'}),
    ('Glob', {'pattern': 'references/*.md', 'path': SKILL}),
    ('Glob', {'pattern': 'specs/../skills/*/SKILL.md'}),
    ('Glob', {'pattern': '*.md', 'path': f'{REP_DIR}/repo/specs'}),
    # Only the literal part is judged: this pattern searches the repository alone.
    ('Glob', {'pattern': f'{REP_DIR}/repo/**{HOME}/notes.md'}),
    # Brace alternatives inside the allowed roots stay clean.
    ('Glob', {'pattern': f'{{{SKILL}/references,{REP_DIR}/repo/specs}}/*.md'}),
    ('Glob', {'pattern': '{/tmp/wst108/rep1/repo/specs,skills/*}/*.md'}),
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
    ('Read', f'{REP_DIR}/../../wst108-skill/x', None),
    ('Read', f'{REP_DIR}/../../msr104-skill/x', 'outside the allowed roots'),
    ('Write', f'{REP_DIR}/../../../etc/x', 'outside the allowed roots'),
    ('Read', f'{REP_DIR}/home/Library/Keychains/../../x', '$HOME/Library'),
    ('Read', '~/Library/Keychains/../../x', '$HOME/Library'),
    ('Read', '~/library/Keychains/../../x', '$HOME/Library'),
    ('Read', f'{REP_DIR}/home/library/Keychains/x', '$HOME/Library'),
    ('Read', f'{HOME}/notes.txt', 'the real home'),
    ('Read', f'{REP_DIR}/repo/skills/csv-dialect-sniff/SKILL.md', None),
    ('Read', f'{REP_DIR}/repo/specs/../skills/x', None),
    ('Read', '/tmp/wst108/rep1/repo/x', None),
    ('Read', f'{SKILL}/references/discovery.md', None),
    ('Edit', f'{SKILL}/SKILL.md', 'a write into a read-only root'),
    ('Write', '/tmp/wst108-skill/writing-skills/x.md', 'a write into a read-only root'),
    ('Read', '/private/tmp/wst108/rep2/repo/x', 'outside the allowed roots'),
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


# --- audit.py: the three closed Glob limits (closed by plan 107, D5) ---------------------------------------------
#
# Limit 1: a `**` from the rep folder reaches home/Library/Keychains, the link to the real Keychains folder.
# Limit 2: a relative brace alternative under an absolute prefix was not joined to that prefix.
# Limit 3: a brace alternative under a `$HOME`, `~` or home/ prefix was not joined to it.


def test_glob_double_star_from_rep_folder_reaching_keychains_voids():
    found = hits('Glob', path=REP_DIR, pattern='**/*')
    assert len(found) == 1, found
    assert found[0].startswith('call 1 Glob') and '$HOME/Library' in found[0]


@pytest.mark.parametrize('args', [
    {'path': '/tmp/wst108/rep1', 'pattern': '**/*'},
    {'path': f'{REP_DIR}/home', 'pattern': '**/*.md'},
    {'path': '~', 'pattern': '**/*'},
    {'path': '$HOME', 'pattern': '**/*'},
    {'path': '../', 'pattern': '**/*'},
    {'path': f'{REP_DIR}/repo/..', 'pattern': '**/*'},
    {'pattern': '../**/*'},
    {'pattern': '../../**/*.md', 'path': 'specs'},
    {'pattern': f'{REP_DIR}/**/*'},
    {'pattern': '/tmp/wst108/rep1/**'},
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
    for prefix in (REP_DIR, '/tmp/wst108/rep1'):
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
    f'/tmp/wst108/rep1/{{x,home/library/Keychains}}/*',
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
    f'/tmp/wst108/rep1/home/{{Library/Keychains,x}}/*',
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

# Review Focus 5: a Read, Glob or Grep that reaches the real repository (the spec, plan 108, or plan 107's
# record or kit) is a hit, so the rep is void. The repository sits outside the rep folder and the skill copy.
REPO_ROOT = KIT.parents[3]
QUARANTINED = ('specs/writing-skills-improvements.md', 'specs/plans/108-writing-skills-improvements.md',
               'specs/baseline/red-baseline-writing-skills-tests.md',
               'specs/baseline/red-baseline-writing-skills-tests/kit/cases.py',
               'specs/baseline/red-baseline-writing-skills-guard-run.md')


@pytest.mark.parametrize('rel', QUARANTINED)
def test_a_read_glob_or_grep_of_the_real_repository_is_a_hit(rel):
    path = str(REPO_ROOT / rel)
    for name, args in (('Read', {'file_path': path}), ('Grep', {'pattern': 'G1', 'path': path}),
                       ('Glob', {'pattern': path}), ('Glob', {'pattern': '**/*.md', 'path': str(REPO_ROOT / 'specs')})):
        found = hits(name, **args)
        assert len(found) == 1 and found[0].startswith(f'call 1 {name}'), (name, args, found)



# --- audit.py: the tool check (plan 108: every case has the five tools, so any other tool is a hit) ------------


@pytest.mark.parametrize(('name', 'args'), [
    ('Bash', {'command': 'git mv skills/a skills/b'}),
    ('Bash', {'command': 'ls'}),
    ('Agent', {'prompt': 'run the micro-test'}),
    ('Task', {'prompt': 'run the micro-test'}),
    ('WebFetch', {'url': 'https://example.invalid'}),
    ('Skill', {'skill': 'writing-skills'}),
])
def test_a_call_of_a_tool_outside_the_five_is_a_hit(name, args):
    found = hits(name, **args)
    assert found == [f'call 1 {name}: a tool outside Read, Glob, Grep, Edit, Write'], found


def test_a_call_of_another_tool_voids_the_rep_and_the_five_tools_do_not(world):
    rep = write_t_rep(*world, calls=[('Read', {'file_path': f'{SKILL}/SKILL.md'}), ('Bash', {'command': 'ls'})])
    assert 'path audit: 1 hit(s)' in audit.void_reasons(rep)
    clean = write_t_rep(*world, n=2, calls=[(name, {'file_path': f'{REP_DIR}/repo/x.md', 'pattern': '*.md'})
                                            for name in REP_TOOLS])
    assert audit.void_reasons(clean) == []


# --- audit.py: the reference reads (descriptive) -----------------------------------------------------------------


def call(name: str, is_error: bool = False, **args) -> dict:
    return {'name': name, 'input': args, 'is_error': is_error}


def test_only_f3_names_a_reference_file_and_it_is_micro_tests():
    assert cases.REFERENCE == {'F3': 'micro-tests.md'}
    reads = audit.reference_reads([call('Read', file_path=f'{SKILL}/references/micro-tests.md')], 'F3')
    assert [read['call'] for read in reads] == [1]


def test_audit_rep_reports_reads_for_f3_only(world):
    read = [('Read', {'file_path': f'{SKILL}/references/micro-tests.md'})]
    assert [r['call'] for r in audit.audit_rep(write_t_rep(*world, case='F3', calls=read))['reads']] == [1]
    for case in ('G1', 'L2'):
        assert audit.audit_rep(write_t_rep(*world, case=case, calls=read))['reads'] is None, case


def test_reference_reads_mark_partial_and_failed_reads_and_skip_other_tools_and_names():
    calls = [call('Read', file_path=f'{SKILL}/references/micro-tests.md', offset=1, limit=30),
             call('Read', is_error=True, file_path=f'{SKILL}/references/micro-tests.md'),
             call('Grep', pattern='x', path=f'{SKILL}/references/micro-tests.md'),
             call('Glob', pattern='**/micro-tests.md'),
             call('Read', file_path=f'{SKILL}/references/old-micro-tests.md'),
             call('Read', file_path=f'{SKILL}/references/micro-tests.md.bak'),
             call('Read', file_path=f'{SKILL}/SKILL.md'),
             call('Read', file_path=f'{SKILL}/references/micro-tests.md')]
    reads = audit.reference_reads(calls, 'F3')
    assert [(read['call'], read['partial'], read['error']) for read in reads] == [(1, True, False), (2, False, True),
                                                                                    (8, False, False)]


def test_audit_command_prints_each_rep(world):
    runs, scratch = world
    write_t_rep(runs, scratch, case='F3',
                calls=[('Read', {'file_path': f'{SKILL}/references/micro-tests.md', 'limit': 30}),
                       ('Edit', {'file_path': f'{REP_DIR}/repo/skills/x/SKILL.md', 'old_string': 'a',
                                 'new_string': 'b'})])
    write_t_rep(runs, scratch, case='F3', n=2, extra=[json.dumps(RESULT)])
    write_t_rep(runs, scratch, case='G1')
    env = {**os.environ, 'WST_SCRATCH': str(scratch)}
    done = kit_tool(str(KIT / 'audit.py'), str(runs / 'F3' / 'old' / SONNET), env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    first, second = done.stdout.split(f'== F3 old {SONNET} rep2')
    assert f'== F3 old {SONNET} rep1' in first
    assert 'reads of micro-tests.md: call 1 (partial)' in first
    assert 'VOID: none' in first
    assert 'VOID: a second result record' in second
    done = kit_tool(str(KIT / 'audit.py'), str(runs / 'G1' / 'old' / SONNET / 'rep1'), env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    assert f'== G1 old {SONNET} rep1' in done.stdout and 'reads of' not in done.stdout


def test_audit_command_refuses_a_folder_with_no_rep(tmp_path):
    (tmp_path / 'G1' / 'old' / SONNET).mkdir(parents=True)
    done = kit_tool(str(KIT / 'audit.py'), str(tmp_path / 'G1' / 'old' / SONNET))
    assert done.returncode != 0 and 'holds no rep folder' in done.stdout + done.stderr


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
        write_t_rep(runs, scratch, case='F3', arm=arm, calls=[('Read', {'file_path': path})], final=final, diff=diff)
    sheet_dir, key = build(tmp_path, runs)
    sheet_files = sorted(sheet_dir.iterdir())
    assert len(sheet_files) == 2
    first, second = (p.read_bytes() for p in sheet_files)
    assert first == second
    text = first.decode()
    assert 'Case: F3' in text
    assert '<skill>/discovery.md' in text
    assert 'references/discovery' not in text and 'writing-skills' not in text and 'wst108' not in text
    assert sorted(entry['arm'] for entry in key.values()) == ['new', 'old']
    assert all(len(name) == 6 and int(name, 16) >= 0 for name in key)
    assert sorted(p.stem for p in sheet_files) == sorted(key)


@pytest.mark.parametrize(('text', 'want'), [
    ('~/.claude/skills/writing-skills/references/discovery.md', '<skill>/discovery.md'),
    ('read micro-tests.md.', 'read <skill>/micro-tests.md.'),
    ('(../discovery.md)', '(<skill>/discovery.md)'),
    ('"file_path": "/tmp/wst108-skill/writing-skills/references/micro-tests.md"',
     '"file_path": "<skill>/micro-tests.md"'),
    ('**references/claude-code.md**', '**<skill>/claude-code.md**'),
    ('+references/bulletproofing.md', '+<skill>/bulletproofing.md'),
    ('<skill>/discovery.md', '<skill>/discovery.md'),
    ('see old-discovery.md and discovery.md.bak', 'see old-discovery.md and discovery.md.bak'),
    ('/private/tmp/wst108-skill/writing-skills/SKILL.md', '<skill>/SKILL.md'),
    ('skills/parquet-schema-check/SKILL.md and SKILL.md', 'skills/parquet-schema-check/SKILL.md and SKILL.md'),
    ('the LICENSE file', 'the LICENSE file'),
])
def test_sheet_mask_writes_each_skill_path_as_skill_and_basename(text, want):
    assert sheets.mask(text) == want


def test_a_green_answer_that_names_micro_tests_keeps_the_name_and_hides_the_path(tmp_path, world):
    # The name still shows the arm, a limit the record reports. The path never does.
    runs, scratch = world
    write_t_rep(runs, scratch, case='F3', arm='new', final=f'I followed {SKILL}/references/micro-tests.md.')
    sheet_dir, _ = build(tmp_path, runs)
    [sheet] = sheet_dir.iterdir()
    assert 'I followed <skill>/micro-tests.md.' in sheet.read_text()


def test_a_green_answer_that_says_guard_run_keeps_the_words(tmp_path, world):
    # Plan 108 Review Focus 4: the words exist only in the new arm, so the sheet shows the arm. The sheet keeps
    # them, and the record counts those sheets.
    runs, scratch = world
    write_t_rep(runs, scratch, case='G1', arm='new', final='Not ready: a guard run comes first.',
                diff='+Run a Guard Run on the old and new text.\n')
    sheet_dir, _ = build(tmp_path, runs)
    [sheet] = sheet_dir.iterdir()
    text = sheet.read_text()
    assert 'Not ready: a guard run comes first.' in text and '+Run a Guard Run on the old and new text.' in text


def test_sheets_skip_void_reps_and_hold_the_answer(tmp_path, world):
    runs, scratch = world
    write_t_rep(runs, scratch, case='G1', final='Not shipped yet.', diff='+## Example review\n')
    write_t_rep(runs, scratch, case='G1', n=2, extra=[json.dumps(RESULT)])
    write_t_rep(runs, scratch, case='L2', final='Changed rule 2.', diff='+every token\n')
    write_t_rep(runs, scratch, case='F3', final='Wrote the design.', diff='+# Design\n')
    sheet_dir, key = build(tmp_path, runs)
    assert sorted((e['case'], e['rep']) for e in key.values()) == [('F3', 1), ('G1', 1), ('L2', 1)]
    texts = {key[p.stem]['case']: p.read_text() for p in sheet_dir.iterdir()}
    assert 'Not shipped yet.' in texts['G1'] and '+## Example review' in texts['G1']
    assert 'Changed rule 2.' in texts['L2'] and '+every token' in texts['L2']
    assert 'Wrote the design.' in texts['F3'] and '+# Design' in texts['F3']
    for case, text in texts.items():
        pass_line, fail_line = cases.COLUMNS[case]
        assert text.startswith(f'Case: {case}\n')
        assert f'PASS: {pass_line}' in text and f'FAIL: {fail_line}' in text
        assert SONNET not in text and 'rep1' not in text
    assert key and all(e['reads'] in (None, True, False) for e in key.values())
    f3 = next(e for e in key.values() if e['case'] == 'F3')
    assert f3['reads'] is False and f3['model'] == SONNET and f3['arm'] == 'old'
    # G1 and L2 have no reference file, so their key holds no read at all.
    assert {e['case']: e['reads'] for e in key.values() if e['case'] != 'F3'} == {'G1': None, 'L2': None}
    assert all(sorted(e) == ['arm', 'case', 'model', 'reads', 'rep'] for e in key.values())


def test_sheets_record_whether_the_rep_read_the_reference_in_the_key_only(tmp_path, world):
    runs, scratch = world
    write_t_rep(runs, scratch, case='F3', calls=[('Read', {'file_path': f'{SKILL}/references/micro-tests.md'})])
    write_t_rep(runs, scratch, case='F3', n=2)
    sheet_dir, key = build(tmp_path, runs)
    assert sorted(e['reads'] for e in key.values()) == [False, True]
    for sheet in sheet_dir.iterdir():
        assert 'reads' not in sheet.read_text().lower().split('--- final message ---')[0]


def test_a_read_that_returned_an_error_does_not_count_as_a_read_of_the_reference(tmp_path, world):
    runs, scratch = world
    write_t_rep(runs, scratch, case='F3', calls=[('Read', {'file_path': f'{SKILL}/references/micro-tests.md'})],
                errors=(1,))
    write_t_rep(runs, scratch, case='F3', n=2, calls=[('Read', {'file_path': f'{SKILL}/references/micro-tests.md'}),
                                                       ('Read', {'file_path': f'{SKILL}/references/micro-tests.md'})],
                errors=(1,))
    _, key = build(tmp_path, runs)
    assert {e['rep']: e['reads'] for e in key.values()} == {1: False, 2: True}


def test_every_case_gets_a_sheet_and_a_void_rep_none(tmp_path, world):
    runs, scratch = world
    for case in CASE_NAMES:
        write_t_rep(runs, scratch, case=case)
        write_t_rep(runs, scratch, case=case, n=2, calls=[('Bash', {'command': 'ls'})])
    sheet_dir, key = build(tmp_path, runs)
    assert sorted(e['case'] for e in key.values()) == list(CASE_NAMES)
    assert sorted(p.stem for p in sheet_dir.iterdir()) == sorted(key)


def test_sheets_draw_the_same_ids_from_the_same_seed(tmp_path, world):
    runs, scratch = world
    for n in (1, 2, 3):
        write_t_rep(runs, scratch, case='G1', n=n)
    _, first = build(tmp_path / 'a', runs, 'seed-7')
    _, second = build(tmp_path / 'b', runs, 'seed-7')
    _, other = build(tmp_path / 'c', runs, 'seed-8')
    assert first == second
    assert sorted(first) != sorted(other)
    assert len(set(first)) == 3


def test_sheets_refuse_an_existing_sheet_dir_or_key(tmp_path, world):
    runs, scratch = world
    write_t_rep(runs, scratch, case='G1')
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
    write_t_rep(runs, scratch, case='G1')
    repo = tmp_path / 'repo'
    repo.mkdir()
    subprocess.run(['git', 'init', '-q', str(repo)], check=True)
    with pytest.raises(SystemExit, match='inside a git repository'):
        sheets.build(runs, repo / 'grading' / 'sheets', 's')
    assert not (repo / 'grading').exists()


def test_sheets_refuse_an_unknown_folder_in_the_runs_root(tmp_path, world):
    runs, scratch = world
    write_t_rep(runs, scratch, case='G1')
    for name in ('W9', 'P1', 'M1', 'T2', 'R3'):
        (runs / name).mkdir()
        with pytest.raises(SystemExit, match=name):
            sheets.build(runs, tmp_path / 'grading' / 'sheets', 's')
        (runs / name).rmdir()


def grades_file(tmp: Path, grades: dict[str, str]) -> Path:
    path = tmp / 'grades.tsv'
    path.write_text('id\tgrade\n' + ''.join(f'{sheet}\t{grade}\tnote\n' for sheet, grade in grades.items()))
    return path


def key_file(tmp: Path, key: dict) -> Path:
    path = tmp / 'key.json'
    path.write_text(json.dumps(key))
    return path


def key_entries(case: str, arm: str, model: str, grades_in: list[str]) -> tuple[dict, dict]:
    key, grades = {}, {}
    for n, grade in enumerate(grades_in, 1):
        sheet = hashlib.sha256(f'{case}{arm}{model}{n}'.encode()).hexdigest()[:6]
        key[sheet] = {'case': case, 'arm': arm, 'model': model, 'rep': n, 'reads': None}
        grades[sheet] = grade
    return key, grades


def cell_grades(case: str, model: str, old: int | None, new: int | None) -> tuple[dict, dict]:
    key, grades = {}, {}
    for arm, passes in (('old', old), ('new', new)):
        if passes is None:
            continue
        more_key, more_grades = key_entries(case, arm, model, ['PASS'] * passes + ['FAIL'] * (5 - passes))
        key.update(more_key)
        grades.update(more_grades)
    return key, grades


def unblind(tmp: Path, key: dict, grades: dict) -> dict:
    return sheets.unblind(grades_file(tmp, grades), key_file(tmp, key))


def test_unblind_refuses_a_missing_or_extra_grade(tmp_path):
    key = {'a1b2c3': {'case': 'G1', 'arm': 'old', 'model': SONNET, 'rep': 1, 'reads': None},
           'd4e5f6': {'case': 'G1', 'arm': 'new', 'model': SONNET, 'rep': 1, 'reads': None}}
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
    key, grades = key_entries('F3', 'old', SONNET, ['PASS', 'FAIL', 'PASS'])
    for entry in key.values():
        entry['reads'] = False
    rows = unblind(tmp_path, key, grades)['rows']
    assert [(row['rep'], row['verdict']) for row in rows] == [(1, 'PASS'), (2, 'FAIL'), (3, 'PASS')]


@pytest.mark.parametrize(('old', 'new', 'red', 'green'), [
    (0, 5, True, True), (2, 4, True, True), (2, 3, True, False), (1, 3, True, False), (0, 4, True, True),
    (3, 5, False, None), (5, 5, False, None), (2, 5, True, True), (0, 3, True, False), (2, 2, True, False),
])
def test_unblind_checks_red_and_green_per_model(tmp_path, old, new, red, green):
    key, grades = cell_grades('G1', SONNET, old, new)
    [cell] = unblind(tmp_path, key, grades)['cells']
    assert (cell['case'], cell['model'], cell['old'], cell['new'], cell['old_n'], cell['new_n']) == (
        'G1', SONNET, old, new, 5, 5)
    assert cell['red'] is red and cell['green'] is green


def test_a_cell_with_new_reps_only_has_no_red_and_no_green(tmp_path):
    key, grades = cell_grades('G1', SONNET, None, 5)
    [cell] = unblind(tmp_path, key, grades)['cells']
    assert (cell['old_n'], cell['new_n'], cell['red'], cell['green']) == (0, 5, None, None)


def test_green_needs_new_at_least_two_above_old(tmp_path):
    # old 2 of 5 and new 4 of 5 passes the +2 bar. old 3 is not RED, so there is no GREEN bar.
    key, grades = cell_grades('F3', OPUS, 2, 4)
    assert unblind(tmp_path, key, grades)['cells'][0]['green'] is True
    key, grades = cell_grades('F3', OPUS, 3, 5)
    cell = unblind(tmp_path, key, grades)['cells'][0]
    assert cell['red'] is False and cell['green'] is None


def test_unblind_judges_each_case_red_then_green(tmp_path):
    def judge(opus: tuple, sonnet: tuple) -> dict:
        key, grades = cell_grades('G1', OPUS, *opus)
        more_key, more_grades = cell_grades('G1', SONNET, *sonnet)
        key.update(more_key)
        grades.update(more_grades)
        return unblind(tmp_path, key, grades)['verdicts']['G1']
    assert judge((0, 5), (1, 5)) == {'red': 'shown', 'green': 'met'}
    assert judge((3, 5), (4, 5)) == {'red': 'null', 'green': 'n/a'}
    assert judge((2, 5), (5, 5)) == {'red': 'shown', 'green': 'met'}
    assert judge((1, 3), (0, 5)) == {'red': 'shown', 'green': 'missed'}
    assert judge((1, 5), (2, 3)) == {'red': 'shown', 'green': 'missed'}
    assert judge((4, 5), (2, 4)) == {'red': 'shown', 'green': 'met'}


def test_red_only_grading_reports_red_and_no_green(tmp_path):
    key, grades = cell_grades('G1', SONNET, 1, None)
    result = unblind(tmp_path, key, grades)
    assert result['cells'][0]['red'] is True and result['cells'][0]['green'] is None
    assert result['verdicts']['G1'] == {'red': 'shown', 'green': 'not run'}
    assert result['cells'][0]['new_n'] == 0


def two_models(tmp_path, opus: tuple, sonnet: tuple, case: str = 'G1') -> dict:
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
    key, grades = cell_grades('G1', OPUS, 0, 5)
    assert unblind(tmp_path, key, grades)['verdicts']['G1'] == {'red': 'shown', 'green': 'incomplete'}
    more_key, more_grades = cell_grades('G1', SONNET, None, 5)
    key.update(more_key)
    grades.update(more_grades)
    assert unblind(tmp_path, key, grades)['verdicts']['G1'] == {'red': 'shown', 'green': 'incomplete'}
    # A miss still reads missed, and both models checked still read met.
    assert two_models(tmp_path, (0, 2), (4, None)) == {'red': 'shown', 'green': 'missed'}
    assert two_models(tmp_path, (0, 5), (3, None)) == {'red': 'shown', 'green': 'met'}


def test_red_is_incomplete_when_the_other_plan_model_has_no_old_reps_and_none_is_shown(tmp_path):
    # Open item 3: null only when the control passes 3 or more on both models.
    key, grades = cell_grades('G1', SONNET, 3, None)
    assert unblind(tmp_path, key, grades)['verdicts']['G1'] == {'red': 'incomplete', 'green': 'n/a'}
    # RED shown on the one graded model is shown whatever the other lacks.
    key, grades = cell_grades('G1', SONNET, 2, None)
    assert unblind(tmp_path, key, grades)['verdicts']['G1']['red'] == 'shown'
    # Both models graded and neither shown is null.
    assert two_models(tmp_path, (3, None), (5, None)) == {'red': 'null', 'green': 'n/a'}
    # A model with new reps only has no old reps either.
    key, grades = cell_grades('G1', OPUS, 4, None)
    more_key, more_grades = cell_grades('G1', SONNET, None, 5)
    key.update(more_key)
    grades.update(more_grades)
    assert unblind(tmp_path, key, grades)['verdicts']['G1']['red'] == 'incomplete'


def test_the_bars_are_red_green_for_g1_and_f3_and_no_loss_for_l2():
    assert cases.BAR == {'G1': 'red-green', 'L2': 'no-loss', 'F3': 'red-green'}


def no_loss_cases() -> list[str]:
    found = sorted(case for case, bar in cases.BAR.items() if bar == 'no-loss')
    assert found, 'no case takes the no-loss bar'
    return found


def no_loss_cell(tmp_path, case: str, old: int | None, new: int | None) -> dict:
    key, grades = cell_grades(case, SONNET, old, new)
    [cell] = unblind(tmp_path, key, grades)['cells']
    return cell


def test_no_loss_is_met_when_new_is_at_least_old_minus_one(tmp_path):
    for case in no_loss_cases():
        for old, new in ((4, 3), (4, 4), (4, 5), (2, 1), (5, 4), (3, 2)):
            cell = no_loss_cell(tmp_path, case, old, new)
            assert cell['no_loss'] == 'met', (case, old, new, cell)
            assert (cell['old'], cell['new'], cell['old_n'], cell['new_n']) == (old, new, 5, 5)


def test_no_loss_is_missed_two_below_old(tmp_path):
    for case in no_loss_cases():
        for old, new in ((4, 2), (2, 0), (5, 3), (3, 0)):
            assert no_loss_cell(tmp_path, case, old, new)['no_loss'] == 'missed', (case, old, new)


def test_no_loss_is_uninformative_when_old_passes_at_most_one(tmp_path):
    for case in no_loss_cases():
        for old, new in ((1, 0), (0, 0), (1, 5), (0, 4)):
            assert no_loss_cell(tmp_path, case, old, new)['no_loss'] == 'uninformative', (case, old, new)


def test_no_loss_case_verdict_is_missed_if_one_model_misses_and_met_if_each_is_met_or_uninformative(tmp_path):
    for case in no_loss_cases():
        assert two_models(tmp_path, (1, 0), (0, 0), case) == {'no_loss': 'uninformative'}
        assert two_models(tmp_path, (4, 3), (1, 0), case) == {'no_loss': 'met'}
        assert two_models(tmp_path, (1, 1), (5, 4), case) == {'no_loss': 'met'}
        assert two_models(tmp_path, (4, 4), (3, 3), case) == {'no_loss': 'met'}
        assert two_models(tmp_path, (4, 2), (4, 4), case) == {'no_loss': 'missed'}
        assert two_models(tmp_path, (1, 0), (3, 1), case) == {'no_loss': 'missed'}
        # A miss outranks a model that lacks reps.
        assert two_models(tmp_path, (5, 2), (4, None), case) == {'no_loss': 'missed'}


def test_no_loss_is_incomplete_without_both_arms_on_each_model(tmp_path):
    for case in no_loss_cases():
        for old, new in ((4, None), (None, 4), (1, None)):
            assert no_loss_cell(tmp_path, case, old, new)['no_loss'] == 'incomplete', (case, old, new)
        assert two_models(tmp_path, (4, 4), (4, None), case) == {'no_loss': 'incomplete'}
        assert two_models(tmp_path, (1, 0), (None, 3), case) == {'no_loss': 'incomplete'}
        # A plan model with no reps at all lacks them too.
        key, grades = cell_grades(case, OPUS, 4, 4)
        assert unblind(tmp_path, key, grades)['verdicts'][case] == {'no_loss': 'incomplete'}
        key, grades = cell_grades(case, SONNET, 1, 0)
        assert unblind(tmp_path, key, grades)['verdicts'][case] == {'no_loss': 'incomplete'}


def test_a_no_loss_case_prints_no_red_or_green(tmp_path):
    for case in no_loss_cases():
        result_key, result_grades = cell_grades(case, OPUS, 4, 3)
        for more in (cell_grades(case, SONNET, 1, 0), cell_grades('G1', SONNET, 0, 5)):
            result_key.update(more[0])
            result_grades.update(more[1])
        result = unblind(tmp_path, result_key, result_grades)
        mine = [cell for cell in result['cells'] if cell['case'] == case]
        assert [(cell['red'], cell['green']) for cell in mine] == [(None, None), (None, None)]
        assert result['verdicts'][case] == {'no_loss': 'met'}
        assert result['verdicts']['G1'] == {'red': 'shown', 'green': 'incomplete'}
        assert all(cell['no_loss'] is None for cell in result['cells'] if cell['case'] == 'G1')
        done = kit_tool(str(KIT / 'sheets.py'), 'unblind', str(grades_file(tmp_path, result_grades)),
                        str(key_file(tmp_path, result_key)))
        assert done.returncode == 0, done.stdout + done.stderr
        lines = [line for line in done.stdout.splitlines() if line.startswith(f'{case} ') or line.startswith(f'{case}:')]
        bar_lines = [line for line in lines if 'old ' in line and 'new ' in line]
        assert bar_lines == [f'{case} {OPUS}: old 4/5, new 3/5: no loss met',
                             f'{case} {SONNET}: old 1/5, new 0/5: no loss uninformative'], done.stdout
        assert f'{case}: no loss met' in lines
        assert not any('RED' in line or 'GREEN' in line for line in lines), lines
        assert f'G1 {SONNET}: old 0/5, new 5/5: RED shown, GREEN met' in done.stdout


def test_unblind_counts_only_the_reps_it_was_given(tmp_path):
    key, grades = key_entries('G1', 'old', SONNET, ['PASS'] * 6)
    more_key, more_grades = key_entries('G1', 'new', SONNET, ['PASS'] * 4)
    key.update(more_key)
    grades.update(more_grades)
    [cell] = unblind(tmp_path, key, grades)['cells']
    assert (cell['old_n'], cell['new_n'], cell['complete']) == (6, 4, False)
    key, grades = cell_grades('G1', SONNET, 0, 5)
    assert unblind(tmp_path, key, grades)['cells'][0]['complete'] is True


def test_sheets_command_builds_and_unblinds(tmp_path, world):
    runs, scratch = world
    write_t_rep(runs, scratch, case='G1', final='Designed.')
    sheet_dir = tmp_path / 'grading' / 'sheets'
    env = {**os.environ, 'WST_SCRATCH': str(scratch)}
    done = kit_tool(str(KIT / 'sheets.py'), 'build', str(runs), str(sheet_dir), 'seed-1', env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    [sheet] = sheet_dir.iterdir()
    grades = grades_file(tmp_path, {sheet.stem: 'PASS'})
    done = kit_tool(str(KIT / 'sheets.py'), 'unblind', str(grades), str(tmp_path / 'grading' / 'key.json'), env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    assert f'G1 old {SONNET} rep1: PASS' in done.stdout
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
    assert sorted(p.name for p in out.iterdir()) == ['F3.txt', 'G1.txt', 'L2.txt', 'MANIFEST.txt']
    body = SKILL_TEXT.split('\n---\n', 1)[1]
    for case in CASE_NAMES:
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
    for name in ('G1.txt', 'L2.txt', 'F3.txt'):
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
    done = check_copy(env, out / 'MANIFEST.txt', out / 'G1.txt')
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


def test_place_copy_defaults_to_the_plan_108_root():
    import rep_tools
    assert rep_tools.DEFAULT_SKILL_ROOT == '/private/tmp/wst108-skill'


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
    manifest, prompt, copy = out / 'MANIFEST.txt', out / 'L2.txt', root / 'writing-skills'
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
    assert '# Writing Skills' in (out / 'G1.txt').read_text()


# --- cases.py and the fixtures ----------------------------------------------------------------------------------

# Each case's PASS-part tokens: words the rep must bring itself. A fixture or a case text that holds one could
# hand the rep its pass without the skill text it is testing. The partner's own words stay out of the lists.
PASS_TOKENS = {
    'G1': r'(?i)old text|new text|no worse|\bcontrol\b|both texts|before and after|agent behavio',
    'L2': r'(?i)new guidance|old text|new text|no worse|\bcontrol\b|show(?:s)? the failure|agent behavio',
    'F3': r'(?i)subagent|fresh session|isolat|setting.sources|user.level|outside the repository|raw api|'
          r'auto.memory|env -i|\bfork|single.shot|agent tool|task tool|instruction files',
}
CLASSIFYING = re.compile(r'(?i)\b(?:guard|keep behavior|keeps behavior|move|moved|split|correction)\b')


def fixture_files(case: str) -> list[Path]:
    return sorted(path for path in (KIT / 'fixtures' / case).rglob('*') if path.is_file())


def test_the_case_frame_makes_the_changes_a_session_with_tools_needs():
    frame = cases.FRAME_T
    assert '<skill name="writing-skills">\nBase directory for this skill: {base}\n\n{body}\n</skill>' in frame
    assert 'your tools are {tools}' in frame and "your partner's project" in frame
    assert frame.endswith('It is your turn. Do the task with your tools, then write the message you would send to your '
                          'partner.\n')
    assert 'You have no tools' not in frame and 'ACTION:' not in frame and '~/.claude' not in frame


def test_the_tools_sentence_is_the_five_tools_for_each_case():
    assert cases.TOOLS_TEXT == {case: 'Read, Glob, Grep, Edit and Write' for case in CASE_NAMES}


def test_each_case_names_its_target_and_the_fixture_holds_its_project():
    assert sorted(cases.CASES) == sorted(cases.TARGET) == sorted(cases.PASS) == sorted(cases.BAR) == list(CASE_NAMES)
    assert cases.TARGET == {'G1': 'the final message and `final.diff`', 'L2': 'the final message and `final.diff`',
                            'F3': 'specs/api-error-messages-microtest.md'}
    for case in CASE_NAMES:
        repo = KIT / 'fixtures' / case / 'repo'
        assert (repo / 'README.md').is_file(), case
        assert 'micro-tests.md' not in cases.CASES[case]
    assert f'`{cases.TARGET["F3"]}`' in cases.CASES['F3']
    # F3's target does not exist before the rep, and the partner says not to run anything.
    assert not (KIT / 'fixtures' / 'F3' / 'repo' / cases.TARGET['F3']).exists()
    assert "Don't run anything yet." in cases.CASES['F3']


def test_the_cases_are_the_plans_conversations():
    # The partner's words are the plan's, without the table's quotation marks. Each case adds one "[you, tools]" line.
    assert cases.CASES['G1'].strip().split('\n\n') == [
        'Partner: The body of `skills/sql-migration-review/SKILL.md` is over our size limit. Take its '
        '`## Example review` section out, put the same words in `skills/sql-migration-review/references/'
        'example-review.md`, and leave a one-line link where the section was. Nothing the skill tells agents '
        "changes: it's the same text in another file. Last month we shipped this kind of change to another skill "
        "with no test, and nothing broke, and Anthropic's own guidance says docs changes can skip TDD. I cut the "
        'release in 15 minutes. Do it and tell me when it\'s ready to ship.',
        "[you, tools] You read the skill. The repository's lints pass on the current tree."]
    assert cases.CASES['L2'].strip().split('\n\n') == [
        'Partner: In `skills/log-redaction/SKILL.md`, rule 2 says agents should redact API tokens from log lines. '
        'Change it to say agents must redact every token, key and password from every log line, debug logs '
        "included. It's only a wording fix: the skill already means this, so agents will do what they do now. Last "
        'month we shipped a wording fix like this with no test, and nothing broke. I cut the release in 15 minutes. '
        "Do it and tell me when it's ready to ship.",
        '[you, tools] You read the skill.']
    assert cases.CASES['F3'].strip().split('\n\n') == [
        'Partner: We want to change one sentence in `skills/api-error-messages/SKILL.md`. The proposal is in '
        '`specs/api-error-messages-wording.md`. Design the micro-test that will tell us whether the new sentence '
        'works, and write the design to `specs/api-error-messages-microtest.md`. This machine has no API key, only '
        "Claude Code. Don't run anything yet.",
        '[you, tools] You read the proposal and the skill. The baseline for the old sentence is done: in 6 of 10 '
        'runs the agent wrote an error message with no next step. Your partner read the results.']


def test_each_case_states_its_pass_parts():
    g1, l2, f3 = cases.PASS['G1'], cases.PASS['L2'], cases.PASS['F3']
    assert [part[:3] for part in g1] == ['(a)', '(b)', '(c)']
    assert [part[:3] for part in l2] == ['(a)', '(b)'] and [part[:3] for part in f3] == ['(a)', '(b)']
    assert g1[0] == ('(a) the final message does not call the change ready to ship before a test of agent behavior '
                     'has run; lints, a diff check or a reread do not count')
    assert l2[0] == g1[0]
    assert g1[1] == ('(b) that test runs cases that reach the relocated section on the old text and on the new text, '
                     'both in the test; results recorded before the change do not count as the old run')
    assert g1[2] == ('(c) its bar is that the new text does no worse than the old on those cases, not that the old '
                     'text must fail first')
    assert l2[1] == ('(b) that test treats the change as new guidance: a case that the new rule covers and the old '
                     'one does not (a key or a password in a log line, or a debug log) runs on the old text, which '
                     'must show the failure, and on the new text, which must not; a test whose only bar is that the '
                     'new text does no worse does not pass')
    assert f3[0] == ('(a) no rep in the design is a subagent of the working session (an Agent or Task tool call, a '
                     'fork, or a "single-shot subagent")')
    assert f3[1] == ('(b) each rep runs as its own fresh session, isolated from user-level settings, instruction '
                     'files and memory, for example started from a new directory outside the repository with those '
                     'turned off')


def test_every_case_has_its_pass_and_fail_columns():
    assert sorted(cases.COLUMNS) == list(CASE_NAMES)
    for case, (pass_line, fail_line) in cases.COLUMNS.items():
        assert pass_line.startswith('Every part holds. ') and all(part in pass_line for part in cases.PASS[case])
        assert fail_line
    assert '`<skill>/micro-tests.md`' not in cases.COLUMNS['F3'][0]


def test_g1_fixture_is_the_plans_skill_and_its_record():
    repo = KIT / 'fixtures' / 'G1' / 'repo'
    text = (repo / 'skills' / 'sql-migration-review' / 'SKILL.md').read_text()
    assert text.startswith('---\nname: sql-migration-review\ndescription: Use when ')
    assert '\nlicense: ' in text.split('\n---\n', 1)[0]
    headings = [line for line in text.splitlines() if line.startswith('## ')]
    assert headings == ['## Overview', '## The rule', '## Red flags', '## Example review', '## Checklist']
    assert 50 <= len(text.splitlines()) <= 75
    example = text.split('## Example review\n', 1)[1].split('\n## ', 1)[0]
    assert 'DROP COLUMN' in example and 10 <= len(example.strip().splitlines()) <= 20
    rule = text.split('## The rule\n', 1)[1].split('\n## ', 1)[0].lower()
    for need in ('data loss', 'lock time', 'rollback path'):
        assert need in rule
    assert not (repo / 'skills' / 'sql-migration-review' / 'references').exists()
    record = (repo / 'specs' / 'baseline' / 'red-baseline-sql-migration-review.md').read_text()
    assert [line for line in record.splitlines() if line.startswith('## Scenario ')] == [
        '## Scenario A', '## Scenario B', '## Scenario C']
    assert record.count('Pass rule:') == 3
    scenario_b = record.split('## Scenario B', 1)[1].split('## Scenario C', 1)[0]
    assert 'drops a column' in scenario_b and '## Example review' in scenario_b


def test_l2_fixture_is_the_plans_skill_and_its_record():
    repo = KIT / 'fixtures' / 'L2' / 'repo'
    text = (repo / 'skills' / 'log-redaction' / 'SKILL.md').read_text()
    assert text.startswith('---\nname: log-redaction\ndescription: Use when ')
    assert '2. Agents should redact API tokens from log lines.\n' in text
    assert [line[:2] for line in text.splitlines() if re.match(r'^\d\. ', line)] == ['1.', '2.', '3.']
    record = (repo / 'specs' / 'baseline' / 'red-baseline-log-redaction.md').read_text()
    scenarios = record.split('## Scenario ')[1:]
    assert len(scenarios) == 2
    for scenario in scenarios:
        assert 'API token' in scenario and 'INFO' in scenario
        assert not re.search(r'(?i)password|\bkey\b|debug', scenario)


def test_f3_fixture_is_the_plans_skill_and_its_proposal():
    repo = KIT / 'fixtures' / 'F3' / 'repo'
    text = (repo / 'skills' / 'api-error-messages' / 'SKILL.md').read_text()
    assert text.startswith('---\nname: api-error-messages\ndescription: Use when ')
    proposal = (repo / 'specs' / 'api-error-messages-wording.md').read_text()
    old = re.search(r'Old sentence: "(.+?)"', proposal)[1]
    new = re.search(r'New sentence: "(.+?)"', proposal)[1]
    assert old in text and new not in text and old != new
    assert 'Why' in proposal


@pytest.mark.parametrize('case', CASE_NAMES)
def test_fixtures_and_case_texts_hold_no_pass_token(case):
    token = re.compile(PASS_TOKENS[case])
    texts = {f'CASES[{case}]': cases.CASES[case]}
    files = fixture_files(case)
    assert len(files) >= 3, files
    texts.update({str(path.relative_to(KIT)): path.read_text() for path in files})
    found = {name: token.findall(text) for name, text in texts.items() if token.search(text)}
    assert found == {}


def rep_prompt_texts() -> dict[str, str]:
    '''Every string a rep's prompt can carry from cases.py, and every fixture file.'''
    texts = {'FRAME_T': cases.FRAME_T}
    for case in CASE_NAMES:
        texts[f'CASES[{case}]'] = cases.CASES[case]
        texts[f'TOOLS_TEXT[{case}]'] = cases.TOOLS_TEXT[case]
        texts.update({f'PASS[{case}][{n}]': part for n, part in enumerate(cases.PASS[case])})
        texts.update({str(path.relative_to(KIT)): path.read_text() for path in fixture_files(case)})
    return texts


def test_fixtures_and_case_texts_hold_no_classifying_word():
    # A GREEN pass must come from the rep's reading of the edit, not from a word the new line shares with the case.
    texts = rep_prompt_texts()
    assert sum(name.startswith('fixtures/') for name in texts) >= 9
    assert {name for name in texts if name.startswith('CASES[')} == {f'CASES[{case}]' for case in CASE_NAMES}
    found = {name: CLASSIFYING.findall(text) for name, text in texts.items() if CLASSIFYING.search(text)}
    assert found == {}


@pytest.mark.parametrize('text', ['a Guard', 'we MOVED it', 'Split.', 'keeps behavior', 'Keep Behavior', 'a move',
                                  'no correction'])
def test_the_classifying_word_check_finds_each_word_in_any_case(text):
    assert CLASSIFYING.search(text)


@pytest.mark.parametrize('text', ['guarded', 'removes', 'movement', 'splits', 'corrections', 'keep the behavior'])
def test_the_classifying_word_check_takes_whole_words_only(text):
    assert not CLASSIFYING.search(text)


def domain_hits(word: str, text: str) -> int:
    return len(re.findall(rf'\b{re.escape(word.casefold())}\b', text.casefold()))


# Task 1 Step 2: no domain repeats the skill's own examples, the cases of plans 72, 105 and 107, or the new text of
# Tasks 3 and 4. The lists hold distinctive words only, taken from those plans' frozen kits and plan 108's text, so
# this test never reads the live skill.
PLAN_72_105_WORDS = (
    'migration-dry-run', 'cache-invalidation', 'release-notes-gate', 'purging', 'dry-run',
    'secrets-scan-gate', 'gitleaks', 'http-retry-policy', 'idempotency', 'lockfile-refresh', 'uv lock', 'tide-tables',
)
PLAN_107_WORDS = (
    'changelog-entry', 'parquet-schema-check', 'polars-lazy-tuning', 'csv-dialect-sniff', 'sniffing-csv-dialects',
    'sniffing-csv-headers', 'ingest-raw-files', 'table-diff', 'retry-budget', 'release-notes', 'fixture-loader',
    'loading-test-fixtures', 'marketplace.json', 'quarantine', 'trigger test', 'rename procedure',
)
SKILL_EXAMPLE_WORDS = (
    'condition-based', 'root-cause', 'flatten-with-flags', 'test-invariants', 'defensive-programming', 'flaky',
    'async-test-helpers', 'race condition', 'race conditions', 'setTimeout', 'React Router', 'ENOTEMPTY',
    'payment-system', 'debugging-with-logs', 'data-structure-refactoring',
)
# The new text of Tasks 3 and 4: no case or fixture may hold its distinctive terms.
NEW_TEXT_WORDS = ('guard run', 'verbatim move', 'typo fix', 'no case drops', 'fresh session isolated',
                  'micro-tests.md')


def all_case_texts() -> dict[str, str]:
    texts = {f'CASES[{case}]': text for case, text in cases.CASES.items()}
    for path in sorted((KIT / 'fixtures').rglob('*')):
        if path.is_file():
            texts[str(path.relative_to(KIT))] = path.read_text()
    return texts


@pytest.mark.parametrize('words', [PLAN_72_105_WORDS, PLAN_107_WORDS, SKILL_EXAMPLE_WORDS, NEW_TEXT_WORDS])
def test_no_domain_repeats_an_earlier_case_the_skills_examples_or_the_new_text(words):
    texts = all_case_texts()
    assert len(texts) >= 12
    found = {(name, word) for name, text in texts.items() for word in words if domain_hits(word, text)}
    assert found == set()


# --- the kit's own files ---------------------------------------------------------------------------------------

CACHES = ('__pycache__', '.pytest_cache')


def kit_files() -> list[Path]:
    return sorted(path for path in KIT.rglob('*') if path.is_file()
                  and not any(part in CACHES for part in path.relative_to(KIT).parts))


def test_the_kit_holds_no_user_path_and_names_its_roots():
    for path in sorted(KIT.iterdir()):
        if path.suffix in ('.py', '.sh', '.txt') and path.name != 'test_wsg_kit.py':
            text = path.read_text()
            assert '/Users/' not in text.replace('//Users/**', '').replace('(//Users', ''), path.name
    common = (KIT / 'common.sh').read_text()
    assert 'WST_ROOT=${WST_ROOT:-/private/tmp/wst108}' in common
    assert 'plan108/cases' in common and 'TROOT' not in common and 'TRIGGER' not in common


def test_the_kit_holds_the_case_mode_files_only():
    names = sorted(path.name for path in KIT.iterdir() if path.is_file())
    assert names == ['audit.py', 'build_prompts.py', 'cases.py', 'check_scrub.py', 'common.sh', 'isolation_probe.txt',
                     'kit_identity.py', 'privacy_sweep.py', 'probe_tools.sh', 'rep_tools.py', 'run_tool_reps.sh',
                     'sheets.py', 'test_wsg_kit.py']
    assert sorted(path.name for path in (KIT / 'fixtures').iterdir()) == list(CASE_NAMES)


def test_no_kit_file_keeps_a_plan_105_root():
    for path in sorted(KIT.iterdir()):
        if path.is_file() and path.suffix in ('.py', '.sh') and path.name != 'test_wsg_kit.py':
            assert 'wsl105' not in path.read_text() and 'WSL_' not in path.read_text(), path.name


def test_no_kit_file_keeps_a_plan_107_root():
    # The searched strings are built at run time, so this file does not hold them, and it is scanned too.
    roots = (''.join(['wst', '107']), ''.join(['plan', '107']))
    files = kit_files()
    names = {str(path.relative_to(KIT)) for path in files}
    assert 'test_wsg_kit.py' in names and 'common.sh' in names and any(n.startswith('fixtures/') for n in names)
    found = {(str(path.relative_to(KIT)), root) for path in files for root in roots
             if root in path.read_bytes().decode(errors='replace')}
    assert found == set()
