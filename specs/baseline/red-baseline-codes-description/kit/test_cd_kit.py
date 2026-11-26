'''Self-tests for plan 111's trigger-test kit, on a stub claude and on synthetic records. No test runs a model.

The runner tests start a stub claude (a bash script given as CLAUDE_BIN) with every root, scratch, fixture and
repository path moved into the test's temporary folder (the CD_* variables). The runner starts the stub under
`env -i`, so every path the stub needs is written into its text. The audit, tally and prompt tests call the
kit's Python in-process, on synthetic records. Sources: plan 107's kit tests
(specs/baseline/red-baseline-writing-skills-tests/kit/test_wst_kit.py), cut to the trigger runner and its
reader, with the tests that plan 111's Task 3 adds: the deny list with Bash and the read fence, the scrub of
`origin`, rule 4 before the scrub, rules 3 and 5, the listing of this repository's three codes skills, and the
PASS rule.
'''
import json
import os
import re
import subprocess
from pathlib import Path

import pytest

import audit
import cases
import rep_tools
import trigger_prompts
import triggers

KIT = Path(__file__).resolve().parent
REPO_ROOT = KIT.parents[3]
PLAN107_PROBE = KIT.parents[1] / 'red-baseline-writing-skills-tests' / 'kit' / 'isolation_probe.txt'
RUN_TRIGGERS = KIT / 'run_trigger_reps.sh'
SONNET, OPUS = 'claude-sonnet-5-5', 'claude-opus-5-5'
FIELD = 'credential_expires_at'
TRIGGER_TOOLS = 'Read,Glob,Grep,Skill'
CROSS_SESSION_TOOLS = ('ListAgents', 'SendMessage', 'PushNotification', 'RemoteTrigger')
SHELL_ADDED = {'PWD', 'SHLVL', '_', 'OLDPWD'}
KEEP = ('HOME', 'USER', 'LOGNAME', 'PATH', 'SHELL', 'TMPDIR', 'LANG')
DISABLE = ('CLAUDE_CODE_DISABLE_ADVISOR_TOOL', 'CLAUDE_CODE_DISABLE_AUTO_MEMORY')
REP_ENV = set(KEEP) | set(DISABLE)
LISTED = ('classification-codes', 'geographic-codes', 'bls-data-context')
TREP_DIR = '/private/tmp/cd111t/rep1'
PLAN = 'specs/plans/111-codes-and-bls-reference-skills.md'


def run(cmd: list[str], env: dict | None = None, cwd: Path = KIT, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, env=env, cwd=cwd, capture_output=True, text=True, check=False, timeout=timeout)


def kit_tool(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return run(['uv', 'run', '--no-project', '-q', 'python', *args], env=env)


# --- run_trigger_reps.sh, on a stub claude ----------------------------------------------------------------------

STUB = r'''#!/bin/bash
log='@DIR@/calls.log'
printf '%s\n' "$*" >> "$log"
n=$(wc -l < "$log" | tr -d ' ')
cat > '@DIR@'/stdin.$n
printf '%s\n' "$@" > '@DIR@'/args.$n
env > '@DIR@'/env.$n
if [ -f '@DIR@'/actions.sh ]; then . '@DIR@'/actions.sh; fi
printf '{"type":"system","subtype":"init","cwd":"%s","tools":["Read","Glob","Grep","Skill"],' "$PWD"
printf '"skills":["bls-data-context","classification-codes","geographic-codes","writing-plans"],'
printf '"model":"claude-sonnet-5-5","credential_expires_at":1790000000}\n'
printf '{"type":"assistant","message":{"content":[{"type":"tool_use","id":"s1","name":"Skill",'
printf '"input":{"skill":"classification-codes"}}]}}\n'
printf '{"type":"user","message":{"content":[{"type":"tool_result","tool_use_id":"s1","content":"Launching"}]}}\n'
if [ -f '@DIR@'/extra_lines ]; then cat '@DIR@'/extra_lines; fi
if [ -f '@DIR@'/result_line ]; then cat '@DIR@'/result_line; else
printf '{"type":"result","subtype":"success","is_error":false,"result":"Done.","num_turns":2,"result_index":0,'
printf '"total_cost_usd":0.01,"credential_expires_at":1790000000,'
printf '"modelUsage":{"claude-sonnet-5-5":{"costUSD":0.01,"credential_expires_at":1790000000}}}\n'
fi
'''


class TriggerKit:
    '''One test's temporary world for the trigger runner: a source repository with skills/, the fixture, a stub.'''

    def __init__(self, tmp: Path) -> None:
        self.tmp = tmp
        self.real = tmp / 'real'
        (self.real / 'Library' / 'Keychains').mkdir(parents=True)
        self.troot = tmp / 'troot'
        self.tscratch = tmp / 'tscratch'
        self.fixtures = tmp / 'fixtures'
        trigger = self.fixtures / 'trigger'
        (trigger / 'repo').mkdir(parents=True)
        (trigger / 'repo' / 'README.md').write_text('A fixture project.\n')
        (trigger / 'listing.txt').write_text((KIT / 'fixtures' / 'trigger' / 'listing.txt').read_text())
        self.repo = tmp / 'srcrepo'
        for name in LISTED + ('writing-plans',):
            (self.repo / 'skills' / name).mkdir(parents=True)
            (self.repo / 'skills' / name / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: Use when {name}\n---\n')
        (self.repo / 'specs').mkdir()
        (self.repo / 'specs' / 'plan.md').write_text('the plan, which no rep may read\n')
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        self.commit('start')
        self.sha = self.head()
        self.stub_dir = tmp / 'stub'
        self.stub_dir.mkdir()
        self.stub = self.stub_dir / 'claude'
        self.stub.write_text(STUB.replace('@DIR@', str(self.stub_dir)))
        self.stub.chmod(0o755)

    def commit(self, message: str) -> None:
        git = ['git', '-C', str(self.repo), '-c', 'user.name=t', '-c', 'user.email=t@example.invalid',
               '-c', 'commit.gpgsign=false']
        subprocess.run(git + ['add', '-A'], check=True)
        subprocess.run(git + ['commit', '-q', '-m', message], check=True)

    def head(self) -> str:
        return subprocess.run(['git', '-C', str(self.repo), 'rev-parse', 'HEAD'], capture_output=True, text=True
                              ).stdout.strip()

    def env(self) -> dict:
        user = os.environ.get('USER') or 'tester'
        return {'HOME': str(self.real), 'USER': user, 'LOGNAME': user, 'PATH': os.environ['PATH'],
                'SHELL': '/bin/bash', 'LANG': 'C', 'CD_TROOT': str(self.troot),
                'CD_TRIGGER_SCRATCH': str(self.tscratch), 'CD_FIXTURES': str(self.fixtures),
                'CD_REPO': str(self.repo), 'CLAUDE_BIN': str(self.stub)}

    def out(self, prompt: str = 'P1', arm: str = 'old', model: str = SONNET) -> Path:
        return self.tmp / 'out' / prompt / arm / model

    def run(self, prompt: str = 'P1', arm: str = 'old', first: int | str = 1, last: int | str = 1, model: str = SONNET,
            ref: str | None = None, out: Path | None = None, env: dict | None = None, extra: tuple = ()
            ) -> subprocess.CompletedProcess:
        out = out or self.out(prompt, arm, model)
        return run(['/bin/bash', str(RUN_TRIGGERS), ref or self.sha, arm, prompt, str(out), str(first), str(last),
                    model, *extra], env=env or self.env(), cwd=self.tmp)

    def actions(self, text: str) -> None:
        (self.stub_dir / 'actions.sh').write_text(text)

    def calls(self) -> list[str]:
        log = self.stub_dir / 'calls.log'
        return log.read_text().splitlines() if log.exists() else []

    def args(self, n: int = 1) -> list[str]:
        return (self.stub_dir / f'args.{n}').read_text().splitlines()

    def rep_env(self, n: int = 1) -> dict:
        text = (self.stub_dir / f'env.{n}').read_text()
        return dict(line.split('=', 1) for line in text.splitlines() if '=' in line)

    def summary_path(self, rep: int = 1, prompt: str = 'P1', arm: str = 'old', model: str = SONNET) -> Path:
        return self.out(prompt, arm, model) / f'rep{rep}' / 'summary.json'

    def summary(self, rep: int = 1, prompt: str = 'P1', arm: str = 'old', model: str = SONNET) -> dict:
        return json.loads(self.summary_path(rep, prompt, arm, model).read_text())

    def stream(self, rep: int = 1, prompt: str = 'P1', arm: str = 'old', model: str = SONNET) -> Path:
        return self.tscratch / prompt / arm / model / f'rep{rep}.jsonl'

    def void_reasons(self, rep: int = 1, prompt: str = 'P1', arm: str = 'old', model: str = SONNET) -> list[str]:
        # The trig fixture points CD_TRIGGER_SCRATCH at self.tscratch for the in-process audit.
        return audit.void_reasons(self.summary_path(rep, prompt, arm, model).parent)


@pytest.fixture
def trig(tmp_path: Path, monkeypatch) -> TriggerKit:
    monkeypatch.setenv('CD_TRIGGER_SCRATCH', str(tmp_path / 'tscratch'))
    return TriggerKit(tmp_path)


def trigger_ok(trig: TriggerKit, **kwargs) -> subprocess.CompletedProcess:
    done = trig.run(**kwargs)
    assert done.returncode == 0, done.stdout + done.stderr
    return done


def snapshot_home(trig: TriggerKit) -> None:
    trig.actions(f'cp "$HOME/.claude/settings.json" \'{trig.tmp}/settings.json\'\n'
                 f'ls "$HOME/.claude/skills" > \'{trig.tmp}/skills.txt\'\n'
                 f'ls -A > \'{trig.tmp}/repo.txt\'\n')


def test_each_rep_is_one_claude_call_in_a_new_folder_with_its_own_home_and_scratch(trig):
    # Rule 1 and rule 2's single claude -p call per rep: rep 2 starts in a new folder, with a new HOME and TMPDIR,
    # and sees nothing that rep 1 left there.
    # The stub sets $n, its call number, before it sources the actions.
    trig.actions(f'ls -A "$HOME" "$TMPDIR" > \'{trig.tmp}\'/listing.$n\n'
                 'touch "$HOME/left-by-a-rep" "$TMPDIR/left-by-a-rep"\n')
    trigger_ok(trig, first=1, last=2)
    assert len(trig.calls()) == 2
    homes = [trig.rep_env(n)['HOME'] for n in (1, 2)]
    tmps = [trig.rep_env(n)['TMPDIR'] for n in (1, 2)]
    assert homes == [f'{os.path.realpath(trig.troot)}/rep{n}/home' for n in (1, 2)]
    assert tmps == [f'{os.path.realpath(trig.troot)}/rep{n}/tmp' for n in (1, 2)]
    assert 'left-by-a-rep' not in (trig.tmp / 'listing.2').read_text()
    assert os.listdir(trig.troot) == []


def test_runner_refuses_a_rep_root_inside_a_git_repository(trig):
    env = {**trig.env(), 'CD_TROOT': str(trig.repo / 'troot')}
    done = trig.run(env=env)
    assert done.returncode == 2 and 'inside a git repository' in done.stdout + done.stderr
    assert trig.calls() == []


def test_rep_settings_deny_bash_and_home_reads_and_block_reads_outside_the_working_directory(trig):
    snapshot_home(trig)
    trigger_ok(trig)
    settings = json.loads((trig.tmp / 'settings.json').read_text())
    deny = settings['permissions']['deny']
    assert 'Bash' in deny and 'Read(~/**)' in deny
    assert set(CROSS_SESSION_TOOLS) <= set(deny)
    assert settings['permissions']['blockReadsOutsideWorkingDirectories'] is True
    assert settings['syncClaudeAiSkills'] is False
    assert settings['skillListingBudgetFraction'] == 0.05
    assert 'skillListingMaxDescChars' not in settings


def test_runner_flags_and_env(trig):
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
    # The listing is what the test reads, so neither flag may hide it.
    assert '--disable-slash-commands' not in args and '--settings' not in args
    env = trig.rep_env()
    assert set(env) - SHELL_ADDED <= REP_ENV
    assert env['CLAUDE_CODE_DISABLE_AUTO_MEMORY'] == '1' and env['PATH'] == '/usr/bin:/bin:/usr/sbin:/sbin'
    assert (trig.stub_dir / 'stdin.1').read_text() == trigger_prompts.PROMPTS['P1'] + '\n'


def test_rep_home_lists_the_refs_skills_and_nothing_else_of_the_repository(trig):
    snapshot_home(trig)
    trigger_ok(trig)
    assert (trig.tmp / 'skills.txt').read_text().split() == sorted(LISTED + ('writing-plans',))
    assert sorted((trig.tmp / 'repo.txt').read_text().split()) == ['.git', 'README.md']


def test_runner_places_the_ref_it_was_given(trig):
    trig.actions(f'cat "$HOME/.claude/skills/geographic-codes/SKILL.md" > \'{trig.tmp}/geo.txt\'\n')
    (trig.repo / 'skills' / 'geographic-codes' / 'SKILL.md').write_text('---\nname: geographic-codes\ndescription: changed\n---\n')
    trig.commit('second')
    trigger_ok(trig)
    assert 'changed' not in (trig.tmp / 'geo.txt').read_text()


@pytest.mark.parametrize('name', LISTED)
def test_runner_refuses_a_ref_whose_skills_lack_a_listed_skill(trig, name):
    subprocess.run(['git', '-C', str(trig.repo), 'rm', '-rq', f'skills/{name}'], check=True)
    trig.commit(f'drop {name}')
    done = trig.run(ref='HEAD')
    assert done.returncode == 2 and f'skills/{name}' in done.stdout + done.stderr
    assert trig.calls() == []
    assert trig.run(ref=trig.sha).returncode == 0


@pytest.mark.parametrize('what', ['arm', 'prompt', 'model', 'out', 'ref', 'first', 'order'])
def test_runner_refuses_bad_arguments(trig, what):
    kwargs = {'arm': {'arm': 'control'}, 'prompt': {'prompt': 'P9'}, 'model': {'model': 'claude-haiku-5-5'},
              'ref': {'ref': 'no-such-ref'}, 'first': {'first': 'x'}, 'order': {'first': 2, 'last': 1},
              'out': {'out': trig.tmp / 'out' / 'P1' / 'new' / SONNET}}[what]
    done = trig.run(**kwargs)
    assert done.returncode == 2, done.stdout + done.stderr
    assert trig.calls() == []


def test_runner_refuses_plan_107s_condition_argument(trig):
    # Plan 107's form: <ref> <arm> <condition> <prompt-id> <out-dir> <first> <last> <model>.
    out = trig.tmp / 'out' / 'P1' / 'old' / 'full' / SONNET
    done = run(['/bin/bash', str(RUN_TRIGGERS), trig.sha, 'old', 'full', 'P1', str(out), '1', '1', SONNET],
               env=trig.env(), cwd=trig.tmp)
    assert done.returncode == 2 and 'usage' in done.stdout + done.stderr
    assert trig.calls() == []


def test_runner_refuses_a_non_empty_root(trig):
    trig.troot.mkdir()
    (trig.troot / 'stray').write_text('x\n')
    done = trig.run()
    assert done.returncode == 3 and 'not empty' in done.stdout + done.stderr
    assert trig.calls() == []


def test_runner_refuses_a_rep_that_exists_in_the_out_folder_or_in_scratch(trig):
    trigger_ok(trig)
    done = trig.run()
    assert done.returncode == 2 and 'exists' in done.stdout + done.stderr
    subprocess.run(['rm', '-rf', str(trig.out() / 'rep1')], check=True)
    done = trig.run()
    assert done.returncode == 2 and 'rep1 exists' in done.stdout + done.stderr
    assert len(trig.calls()) == 1


def test_runner_removes_the_rep_folder_and_keeps_only_the_summary_and_the_stream(trig):
    trigger_ok(trig)
    assert os.listdir(trig.troot) == []
    assert sorted(os.listdir(trig.tscratch / 'P1' / 'old' / SONNET)) == ['rep1.err', 'rep1.jsonl', 'rep1.prompt.txt']
    assert os.listdir(trig.out() / 'rep1') == ['summary.json']
    # Nothing of the rep folder (its HOME with claude's own state files) is kept anywhere under either root.
    kept = sorted(str(p.relative_to(trig.tmp)) for root in (trig.tscratch, trig.tmp / 'out') for p in root.rglob('*'))
    assert kept == ['out/P1', 'out/P1/old', f'out/P1/old/{SONNET}', f'out/P1/old/{SONNET}/rep1',
                    f'out/P1/old/{SONNET}/rep1/summary.json', 'tscratch/P1', 'tscratch/P1/old',
                    f'tscratch/P1/old/{SONNET}', f'tscratch/P1/old/{SONNET}/rep1.err',
                    f'tscratch/P1/old/{SONNET}/rep1.jsonl', f'tscratch/P1/old/{SONNET}/rep1.prompt.txt']


def test_runner_strips_the_credential_field_and_every_origin_from_the_saved_files(trig):
    # Rule 3, and rule 4's scrub: the stub writes the field at the top and nested, and an origin that is not a peer's.
    own = {'type': 'user', 'origin': {'kind': 'human', 'title': 'own-title-x'},
           'message': {'content': [{'type': 'text', 'text': 'hi', 'meta': {'origin': None}}]}}
    (trig.stub_dir / 'extra_lines').write_text(json.dumps(own) + '\n')
    trigger_ok(trig)
    for path in (trig.summary_path(), trig.stream()):
        text = path.read_text()
        assert FIELD not in text and '"origin"' not in text and 'own-title-x' not in text, path
    assert trig.summary()['peer_check'] == []
    assert trig.void_reasons() == []


def test_runner_records_a_peer_origin_before_the_scrub(trig):
    deep = {'type': 'user', 'message': {'content': [
        {'type': 'text', 'text': 'hi', 'meta': {'via': [{'origin': {'kind': 'peer', 'title': 'peer-title-x'}}]}}]}}
    (trig.stub_dir / 'extra_lines').write_text(json.dumps(deep) + '\n')
    trigger_ok(trig)
    found = trig.summary()['peer_check']
    assert len(found) == 1 and 'peer origin' in found[0]
    for path in (trig.summary_path(), trig.stream()):
        text = path.read_text()
        assert '"origin"' not in text and 'peer-title-x' not in text, path
    assert any(reason.startswith('rule 4') for reason in trig.void_reasons())


def test_runner_records_a_result_index_above_0(trig):
    result = {'type': 'result', 'subtype': 'success', 'is_error': False, 'result': 'Reply to a peer.',
              'result_index': 1, 'total_cost_usd': 0.01}
    (trig.stub_dir / 'result_line').write_text(json.dumps(result) + '\n')
    trigger_ok(trig)
    found = trig.summary()['peer_check']
    assert len(found) == 1 and 'result_index 1' in found[0]
    assert any(reason.startswith('rule 4') for reason in trig.void_reasons())


def test_a_field_left_in_a_saved_file_is_a_kit_error(trig):
    trig.actions(f"printf '{FIELD}: 1\\n' >&2\n")
    done = trig.run()
    assert done.returncode == 2, done.stdout + done.stderr
    assert 'the strip left' in trig.summary_path().read_text()
    assert any(reason.startswith('kit error') for reason in trig.void_reasons())


def test_an_origin_key_left_in_a_saved_file_is_a_kit_error(trig):
    # The strip keeps the bytes of a stream line that is not JSON, so a cut-off record leaves its origin key there.
    (trig.stub_dir / 'extra_lines').write_text('{"type":"user","origin":{"kind":"human","title":"t"}\n')
    done = trig.run()
    assert done.returncode == 2, done.stdout + done.stderr
    assert 'the strip left' in trig.summary_path().read_text()
    assert any(reason.startswith('kit error') for reason in trig.void_reasons())


def test_a_stub_stream_with_a_skill_call_loads_and_its_root_tallies(trig):
    trigger_ok(trig)
    rep = trig.out() / 'rep1'
    assert triggers.is_load(triggers.load_records(rep)) is True
    env = {**os.environ, 'CD_TRIGGER_SCRATCH': str(trig.tscratch)}
    done = kit_tool(str(KIT / 'triggers.py'), 'tally', str(trig.tmp / 'out'), env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    assert f'P1 old {SONNET}: 1 of 1 (void 0)' in done.stdout and 'verdict: incomplete' in done.stdout


def test_the_probe_runs_as_a_trigger_rep_does(trig):
    trigger_ok(trig)
    trigger_ok(trig, prompt='probe', arm='pilot')
    assert trig.args(2) == trig.args(1)
    assert (trig.stub_dir / 'stdin.2').read_text() == (KIT / 'isolation_probe.txt').read_text()


# --- audit.py: the VOID reasons, on synthetic reps ------------------------------------------------------------------

RESULT = {'type': 'result', 'subtype': 'success', 'is_error': False, 'result': 'Done.', 'result_index': 0,
          'total_cost_usd': 0.01}
LISTING = ('classification-codes', 'geographic-codes', 'bls-data-context', 'writing-plans')


def stream_lines(calls=(), errors=(), extra=(), result=None, init_tools=('Read', 'Glob', 'Grep', 'Skill'),
                 skills=LISTING, no_results=()) -> list[str]:
    init = {'type': 'system', 'subtype': 'init', 'tools': list(init_tools)}
    if skills is not None:
        init['skills'] = list(skills)
    lines = [json.dumps(init)]
    for number, (name, args) in enumerate(calls, 1):
        use = {'type': 'tool_use', 'id': f't{number}', 'name': name, 'input': args}
        lines.append(json.dumps({'type': 'assistant', 'message': {'content': [use]}}))
        if number in no_results:
            continue
        done = {'type': 'tool_result', 'tool_use_id': f't{number}', 'content': 'ok', 'is_error': number in errors}
        lines.append(json.dumps({'type': 'user', 'message': {'content': [done]}}))
    lines += list(extra)
    if result is not False:
        lines.append(json.dumps(result or RESULT))
    return lines


def write_rep(runs: Path, tscratch: Path, prompt: str = 'P1', arm: str = 'old', model: str = SONNET, n: int = 1,
              calls=(), errors=(), extra=(), result=None, skills=LISTING, init_tools=('Read', 'Glob', 'Grep', 'Skill'),
              summary: dict | None = None, lines: list[str] | None = None, no_results=()) -> Path:
    rep = runs / prompt / arm / model / f'rep{n}'
    rep.mkdir(parents=True)
    base = {'prompt': prompt, 'arm': arm, 'model': model, 'rep': n, 'rep_dir': TREP_DIR, 'final_message': 'Done.',
            'peer_check': []}
    (rep / 'summary.json').write_text(json.dumps({**base, **(summary or {})}))
    stream = tscratch / prompt / arm / model / f'rep{n}.jsonl'
    stream.parent.mkdir(parents=True, exist_ok=True)
    if lines is None:
        lines = stream_lines(calls, errors, extra, result, init_tools, skills, no_results)
    stream.write_text(''.join(line + '\n' for line in lines))
    return rep


@pytest.fixture
def world(tmp_path: Path, monkeypatch) -> tuple[Path, Path]:
    monkeypatch.setenv('CD_TRIGGER_SCRATCH', str(tmp_path / 'tscratch'))
    return tmp_path / 'runs', tmp_path / 'tscratch'


def skill_use(name: str) -> tuple[str, dict]:
    return 'Skill', {'skill': name}


def test_a_clean_rep_has_no_void_reason(world):
    rep = write_rep(*world, calls=[skill_use('classification-codes'), ('Read', {'file_path': f'{TREP_DIR}/repo/README.md'})])
    assert audit.stream_path(rep).parent.parts[-3:] == ('P1', 'old', SONNET)
    assert audit.void_reasons(rep) == []


def test_rule_3_voids_a_credential_field_left_in_the_summary_or_the_stream(world):
    rep = write_rep(*world, summary={'init': {FIELD: 1}})
    assert [r for r in audit.void_reasons(rep) if r.startswith('rule 3')] == [f'rule 3: {FIELD} left in summary.json']
    other = write_rep(*world, n=2, extra=[json.dumps({'type': 'user', 'usage': {FIELD: 1}})])
    assert [r for r in audit.void_reasons(other) if r.startswith('rule 3')] == [f'rule 3: {FIELD} left in rep2.jsonl']


@pytest.mark.parametrize('value', [1, 2, '1', '0', True, False, 1.5, 0.0, None])
def test_rule_4_voids_a_result_index_that_is_not_0(world, value):
    rep = write_rep(*world, result={**RESULT, 'result_index': value})
    assert any(reason.startswith('rule 4') and 'result_index' in reason for reason in audit.void_reasons(rep))


@pytest.mark.parametrize('result', [{**RESULT, 'result_index': 0}, {**RESULT, 'result_index': -1},
                                    {k: v for k, v in RESULT.items() if k != 'result_index'}])
def test_rule_4_keeps_a_whole_result_index_of_0_or_below_or_none_given(world, result):
    rep = write_rep(*world, result=result)
    assert audit.void_reasons(rep) == []


def test_rule_4_reads_a_result_index_in_any_record_at_any_depth(world):
    rep = write_rep(*world, extra=[json.dumps({'type': 'user', 'message': {'meta': {'result_index': 1}}})])
    assert any(reason.startswith('rule 4') for reason in audit.void_reasons(rep))


def test_rule_4_voids_a_peer_origin_at_any_depth_in_the_saved_stream(world):
    deep = {'type': 'user', 'message': {'content': [{'type': 'text', 'meta': {'via': [{'origin': {'kind': 'peer'}}]}}]}}
    rep = write_rep(*world, extra=[json.dumps(deep)])
    assert any(reason.startswith('rule 4') and 'peer origin' in reason for reason in audit.void_reasons(rep))
    top = write_rep(*world, n=2, extra=[json.dumps({'type': 'user', 'origin': {'kind': 'peer'}})])
    assert any(reason.startswith('rule 4') for reason in audit.void_reasons(top))


@pytest.mark.parametrize('origin', [{'kind': 'human'}, {'kind': 'task-notification'}, None, {'title': 'peer'}])
def test_rule_4_keeps_an_origin_whose_kind_is_not_peer(world, origin):
    rep = write_rep(*world, extra=[json.dumps({'type': 'user', 'origin': origin})])
    assert not any(reason.startswith('rule 4') for reason in audit.void_reasons(rep))


def test_rule_4_reads_the_check_that_the_runner_ran_before_the_scrub(world):
    rep = write_rep(*world, summary={'peer_check': ['record 4: a peer origin']})
    assert 'rule 4: record 4: a peer origin (before the scrub)' in audit.void_reasons(rep)


def test_a_summary_without_the_runners_peer_check_is_a_kit_error(world):
    rep = write_rep(*world)
    summary = json.loads((rep / 'summary.json').read_text())
    del summary['peer_check']
    (rep / 'summary.json').write_text(json.dumps(summary))
    assert 'kit error: no peer_check in summary.json' in audit.void_reasons(rep)


@pytest.mark.parametrize(('tool', 'args'), [
    ('Read', {'file_path': f'/work/{PLAN}'}),
    ('Read', {'file_path': '/work/specs/baseline/red-baseline-codes-description.md'}),
    ('Read', {'file_path': '/work/specs/baseline/red-baseline-codes-description/kit/cases.py'}),
    ('Read', {'file_path': '/work/specs/DEFERRED_ITEMS.md'}),
    ('Grep', {'pattern': 'IND', 'path': '/work/specs/deferred_items.md'}),
    ('Glob', {'pattern': '**/red-baseline-codes-description/**'}),
    ('Glob', {'pattern': '*.md', 'path': '/work/specs/plans/111-codes-and-bls-reference-skills.md'}),
])
def test_rule_5_voids_a_call_that_read_a_quarantined_file(world, tool, args):
    rep = write_rep(*world, calls=[(tool, args)])
    assert [r for r in audit.void_reasons(rep) if r.startswith('rule 5')] == [
        f'rule 5: call 1 {tool} names a quarantined file']


@pytest.mark.parametrize(('tool', 'args'), [
    ('Read', {'file_path': '/work/specs/plans/110-other-plan.md'}),
    ('Read', {'file_path': '/work/specs/baseline/red-baseline-writing-skills-tests.md'}),
    ('Read', {'file_path': '/work/specs/deferred_items.txt'}),
    ('Grep', {'pattern': 'deferred_items.md', 'path': '/work/repo'}),
    ('Skill', {'skill': 'red-baseline-codes-description'}),
])
def test_rule_5_keeps_a_call_that_names_no_quarantined_file(world, tool, args):
    rep = write_rep(*world, calls=[(tool, args)])
    assert not any(reason.startswith('rule 5') for reason in audit.void_reasons(rep))


def test_rule_5_keeps_a_refused_read_and_a_call_with_no_result(world):
    rep = write_rep(*world, calls=[('Read', {'file_path': f'/work/{PLAN}'})], errors=(1,))
    assert not any(reason.startswith('rule 5') for reason in audit.void_reasons(rep))
    rep = write_rep(*world, n=2, calls=[('Read', {'file_path': f'/work/{PLAN}'})], no_results=(1,))
    assert not any(reason.startswith('rule 5') for reason in audit.void_reasons(rep))


@pytest.mark.parametrize(('result', 'reason'), [
    ({**RESULT, 'subtype': 'error_during_execution'}, 'error result: subtype error_during_execution'),
    ({**RESULT, 'is_error': True}, 'error result: is_error true'),
])
def test_an_error_result_voids(world, result, reason):
    rep = write_rep(*world, result=result)
    assert reason in audit.void_reasons(rep)


@pytest.mark.parametrize('subtype', ['error_max_turns', 'error_max_budget_usd'])
def test_a_turn_or_budget_stop_is_a_normal_end(world, subtype):
    rep = write_rep(*world, calls=[skill_use('classification-codes')], result={**RESULT, 'subtype': subtype, 'is_error': True})
    assert audit.void_reasons(rep) == []
    assert triggers.is_load(triggers.load_records(rep)) is True


@pytest.mark.parametrize('missing', LISTED)
def test_a_listing_that_lacks_a_listed_skill_voids(world, missing):
    rep = write_rep(*world, skills=[name for name in LISTING if name != missing])
    assert f'listing lacks {missing}' in audit.void_reasons(rep)


def test_the_listing_check_matches_names_exactly_and_reads_both_shapes(world):
    rep = write_rep(*world, skills=('classification-codes-old', 'plugin:geographic-codes', 'bls-data-context'))
    assert 'listing lacks classification-codes, geographic-codes' in audit.void_reasons(rep)
    rep = write_rep(*world, n=2, skills=None)
    assert 'listing lacks classification-codes, geographic-codes, bls-data-context' in audit.void_reasons(rep)
    rep = write_rep(*world, n=3, skills=[{'name': name} for name in LISTED])
    assert audit.void_reasons(rep) == []


def test_a_stream_with_no_init_record_lists_nothing_and_voids(world):
    rep = write_rep(*world, lines=[json.dumps(RESULT)])
    assert 'listing lacks classification-codes, geographic-codes, bls-data-context' in audit.void_reasons(rep)


@pytest.mark.parametrize(('kwargs', 'reason'), [
    ({'lines': [json.dumps({'type': 'system', 'subtype': 'init', 'skills': list(LISTED)}), 'not json',
                json.dumps(RESULT)]}, 'kit error: stream line(s) 2 not JSON'),
    ({'lines': [json.dumps({'type': 'system', 'subtype': 'init', 'skills': list(LISTED)}), '[1, 2]',
                json.dumps(RESULT)]}, 'kit error: stream line(s) 2 not JSON'),
    ({'result': False}, 'kit error: no result record'),
    ({'extra': [json.dumps(RESULT)]}, 'kit error: a second result record'),
    ({'summary': {'kit_error': 'setup failed'}}, 'kit error: setup failed'),
])
def test_a_stream_that_cannot_be_read_whole_is_a_kit_error(world, kwargs, reason):
    rep = write_rep(*world, **kwargs)
    assert reason in audit.void_reasons(rep)


def test_a_missing_stream_or_summary_is_a_kit_error(world):
    rep = write_rep(*world)
    audit.stream_path(rep).unlink()
    assert 'kit error: no saved stream' in audit.void_reasons(rep)
    other = write_rep(*world, n=2)
    (other / 'summary.json').unlink()
    assert 'kit error: no summary.json' in audit.void_reasons(other)


def test_plan_107s_path_and_bash_audits_void_nothing(world):
    # Plan 111 registers no VOID reason for them: rule 2's deny list and read fence refuse those calls instead.
    rep = write_rep(*world, calls=[('Bash', {'command': 'ls ~'}), ('Read', {'file_path': '/private/etc/hosts'}),
                                   ('Glob', {'pattern': '**/*', 'path': TREP_DIR})], errors=(1, 2, 3))
    assert audit.void_reasons(rep) == []


def test_audit_command_prints_each_rep(world):
    runs, tscratch = world
    write_rep(runs, tscratch, calls=[skill_use('classification-codes')])
    write_rep(runs, tscratch, n=2, skills=('geographic-codes',))
    env = {**os.environ, 'CD_TRIGGER_SCRATCH': str(tscratch)}
    done = kit_tool(str(KIT / 'audit.py'), str(runs / 'P1' / 'old' / SONNET), env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    assert f'== P1 old {SONNET} rep1' in done.stdout and f'== P1 old {SONNET} rep2' in done.stdout
    assert 'loads classification-codes: yes' in done.stdout and 'VOID: none' in done.stdout
    assert 'VOID: listing lacks classification-codes, bls-data-context' in done.stdout
    assert kit_tool(str(KIT / 'audit.py'), str(runs), env=env).returncode != 0


# --- rep_tools.py: the scrub and the check before it -----------------------------------------------------------


def test_strip_removes_the_credential_field_and_origin_at_any_depth_and_keeps_the_rest():
    record = {'a': 1, FIELD: 2, 'origin': {'kind': 'peer'}, 'b': [{FIELD: 3, 'c': 4, 'origin': None}],
              'd': {'e': {'origin': 'x', 'f': 'origin'}}}
    assert rep_tools.strip(record) == {'a': 1, 'b': [{'c': 4}], 'd': {'e': {'f': 'origin'}}}


def test_strip_file_rewrites_a_jsonl_stream_and_keeps_a_line_that_is_not_json(tmp_path):
    path = tmp_path / 'rep1.jsonl'
    lines = [json.dumps({'type': 'user', 'origin': {'kind': 'peer'}}), 'not json origin credential_expires_at',
             json.dumps({'type': 'result', FIELD: 1, 'text': 'a b'}), json.dumps({'type': 'assistant'})]
    path.write_text('\n'.join(lines) + '\n')
    rep_tools.strip_file(path)
    out = path.read_text().split('\n')
    assert json.loads(out[0]) == {'type': 'user'}
    assert out[1] == 'not json origin credential_expires_at'
    assert json.loads(out[2]) == {'type': 'result', 'text': 'a b'}
    assert out[3] == lines[3] and out[4] == ''


def test_strip_file_rewrites_a_json_file(tmp_path):
    path = tmp_path / 'summary.json'
    path.write_text(json.dumps({'origin': {'kind': 'peer'}, 'x': {FIELD: 1, 'y': 2}}))
    rep_tools.strip_file(path)
    assert json.loads(path.read_text()) == {'x': {'y': 2}}


def test_strip_command_strips_each_file(tmp_path):
    files = [tmp_path / 'a.json', tmp_path / 'b.jsonl']
    files[0].write_text(json.dumps({FIELD: 1, 'k': 1}))
    files[1].write_text(json.dumps({'origin': {}, 'k': 2}) + '\n')
    done = kit_tool(str(KIT / 'rep_tools.py'), 'strip', *map(str, files))
    assert done.returncode == 0, done.stderr
    assert json.loads(files[0].read_text()) == {'k': 1}
    assert json.loads(files[1].read_text().strip()) == {'k': 2}


def test_peer_check_names_each_record_and_never_copies_the_origin():
    records = [{'type': 'system'}, {'type': 'user', 'origin': {'kind': 'peer', 'title': 'peer-title-x'}},
               {'type': 'result', 'result_index': 2}, {'type': 'user', 'origin': {'kind': 'human'}},
               {'type': 'result', 'result_index': 0}]
    found = rep_tools.peer_check(records)
    assert found == ['record 2: a peer origin', 'record 3: result_index 2']
    assert 'peer-title-x' not in ' '.join(found)


# --- triggers.py: loads, listing and tally -----------------------------------------------------------------------


def test_load_counts_a_skill_call_naming_classification_codes(world):
    rep = write_rep(*world, calls=[skill_use('classification-codes')])
    assert triggers.is_load(triggers.load_records(rep)) is True


def test_load_counts_a_later_skill_call(world):
    rep = write_rep(*world, calls=[skill_use('geographic-codes'), ('Read', {'file_path': f'{TREP_DIR}/repo/README.md'}),
                                   skill_use('classification-codes')])
    records = triggers.load_records(rep)
    assert triggers.is_load(records) is True
    assert triggers.skill_calls(records) == ['geographic-codes', 'classification-codes']


def test_no_skill_call_or_another_skill_is_no_load(world):
    rep = write_rep(*world, calls=[('Read', {'file_path': f'{TREP_DIR}/repo/README.md'})])
    assert triggers.is_load(triggers.load_records(rep)) is False
    rep = write_rep(*world, n=2, calls=[skill_use('geographic-codes'), skill_use('bls-data-context')])
    assert triggers.is_load(triggers.load_records(rep)) is False


@pytest.mark.parametrize('name', ['classification-codes-old', 'my-classification-codes', 'plugin:classification-codes',
                                  'Classification-Codes', 'classification_codes', ''])
def test_a_load_needs_the_exact_skill_name(world, name):
    rep = write_rep(*world, calls=[skill_use(name)])
    assert triggers.is_load(triggers.load_records(rep)) is False


def test_only_a_tool_use_named_skill_is_a_load(world):
    text = {'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': 'Skill classification-codes'}]}}
    other = {'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'id': 'x', 'name': 'Read',
                                                           'input': {'skill': 'classification-codes'}}]}}
    rep = write_rep(*world, extra=[json.dumps(text), json.dumps(other)])
    assert triggers.is_load(triggers.load_records(rep)) is False


def test_triggers_loads_and_listing_commands(world):
    rep = write_rep(*world, calls=[skill_use('geographic-codes'), skill_use('classification-codes')])
    none = write_rep(*world, n=2)
    env = {**os.environ, 'CD_TRIGGER_SCRATCH': str(world[1])}
    done = kit_tool(str(KIT / 'triggers.py'), 'loads', str(rep), env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    assert done.stdout.split('\n')[0] == 'load' and 'geographic-codes, classification-codes' in done.stdout
    assert kit_tool(str(KIT / 'triggers.py'), 'loads', str(none), env=env).stdout.split('\n')[0] == 'no-load'
    assert kit_tool(str(KIT / 'triggers.py'), 'listing', str(rep), env=env).stdout.split() == list(LISTING)
    assert kit_tool(str(KIT / 'triggers.py'), 'nonsense', env=env).returncode != 0


def grid(old: dict | None = None, new: dict | None = None, models=(SONNET, OPUS), reps: int = 3) -> dict:
    '''Every prompt, arm and model with `reps` reps; `old` and `new` map (prompt, model) to loads. By default a
    should-load prompt loads in 2 reps and a near miss in 1.'''
    cells = {}
    for prompt in trigger_prompts.PROMPTS:
        default = 2 if prompt in trigger_prompts.SHOULD_LOAD else 1
        for arm, given in (('old', old or {}), ('new', new or {})):
            for model in models:
                cells[(prompt, arm, model)] = {'reps': reps, 'void': 0, 'loads': given.get((prompt, model), default)}
    return cells


def bar(result: dict, kind: str, model: str) -> dict:
    [found] = [b for b in result['bars'] if (b['kind'], b['model']) == (kind, model)]
    return found


def test_equal_counts_pass_on_every_bar():
    result = triggers.judge(grid())
    assert len(result['bars']) == 6 and all(b['ok'] for b in result['bars'])
    assert (bar(result, 'ind', SONNET)['old'], bar(result, 'ind', SONNET)['new']) == (4, 4)
    assert (bar(result, 'should-load', OPUS)['old'], bar(result, 'should-load', OPUS)['new']) == (10, 10)
    assert (bar(result, 'near-miss', OPUS)['old'], bar(result, 'near-miss', OPUS)['new']) == (4, 4)
    assert result['complete'] is True and triggers.verdict(result) == 'pass'


@pytest.mark.parametrize(('new', 'kind', 'model'), [
    ({('N4', SONNET): 2}, 'near-miss', SONNET),
    ({('N1', OPUS): 3}, 'near-miss', OPUS),
    ({('P1', OPUS): 1, ('P3', OPUS): 3}, 'ind', OPUS),
    ({('P2', SONNET): 1, ('P5', SONNET): 3}, 'ind', SONNET),
    ({('P3', SONNET): 1}, 'should-load', SONNET),
    ({('P5', OPUS): 1}, 'should-load', OPUS),
])
def test_one_missed_bar_on_one_model_fails(new, kind, model):
    result = triggers.judge(grid(new=new))
    assert bar(result, kind, model)['ok'] is False
    other = OPUS if model == SONNET else SONNET
    assert all(b['ok'] for b in result['bars'] if b['model'] == other)
    assert triggers.verdict(result) == 'fail'


def test_a_drop_on_p1_and_p2_fails_even_when_the_should_load_total_holds():
    result = triggers.judge(grid(new={('P1', SONNET): 1, ('P4', SONNET): 3}))
    assert bar(result, 'should-load', SONNET)['ok'] is True and bar(result, 'ind', SONNET)['ok'] is False
    assert triggers.verdict(result) == 'fail'


@pytest.mark.parametrize('new', [
    {('P1', SONNET): 3},
    {('N2', OPUS): 0},
    {('P2', SONNET): 3, ('P4', SONNET): 1},
    {('P1', OPUS): 3, ('P2', OPUS): 3, ('P3', OPUS): 3, ('P4', OPUS): 3, ('P5', OPUS): 3, ('N1', OPUS): 0},
])
def test_a_gain_on_the_should_load_prompts_or_a_drop_on_the_near_misses_passes(new):
    assert triggers.verdict(triggers.judge(grid(new=new))) == 'pass'


def test_an_old_arm_that_loads_more_on_the_near_misses_leaves_room():
    result = triggers.judge(grid(old={('N3', SONNET): 3}, new={('N3', SONNET): 2, ('N4', SONNET): 2}))
    assert bar(result, 'near-miss', SONNET) == {'kind': 'near-miss', 'model': SONNET, 'old': 6, 'new': 6, 'ok': True}
    assert triggers.verdict(result) == 'pass'


def test_a_run_is_incomplete_without_three_valid_reps_in_every_cell():
    cells = grid()
    cells[('P3', 'new', OPUS)]['reps'] = 2
    assert triggers.judge(cells)['complete'] is False and triggers.verdict(triggers.judge(cells)) == 'incomplete'
    cells = grid()
    cells[('N4', 'old', SONNET)]['reps'] = 4
    assert triggers.judge(cells)['complete'] is False
    cells = grid()
    del cells[('N2', 'old', SONNET)]
    assert triggers.judge(cells)['complete'] is False
    assert triggers.judge(grid(models=(SONNET,)))['complete'] is False
    assert triggers.verdict(triggers.judge({})) == 'incomplete'
    # Incomplete governs even when a bar also fails.
    cells = grid(new={('N4', SONNET): 3})
    cells[('P1', 'old', OPUS)]['reps'] = 2
    assert triggers.verdict(triggers.judge(cells)) == 'incomplete'


def test_tally_counts_loads_per_cell_and_skips_void_reps(world):
    runs, tscratch = world
    write_rep(runs, tscratch, calls=[skill_use('classification-codes')])
    write_rep(runs, tscratch, n=2, calls=[skill_use('geographic-codes')])
    write_rep(runs, tscratch, n=3, calls=[skill_use('classification-codes')], skills=('classification-codes',))
    write_rep(runs, tscratch, n=4, calls=[skill_use('classification-codes')],
              result={**RESULT, 'subtype': 'error_max_turns', 'is_error': True})
    write_rep(runs, tscratch, n=5, calls=[skill_use('classification-codes')], result={**RESULT, 'result_index': 1})
    write_rep(runs, tscratch, prompt='N4', arm='new', model=OPUS, calls=[skill_use('classification-codes')])
    result = triggers.tally(runs)
    assert result['cells'][('P1', 'old', SONNET)] == {'reps': 3, 'loads': 2, 'void': 2}
    assert result['cells'][('N4', 'new', OPUS)] == {'reps': 1, 'loads': 1, 'void': 0}
    assert [line for line in result['voids'] if 'rep3' in line and 'listing' in line]
    assert [line for line in result['voids'] if 'rep5' in line and 'rule 4' in line]


@pytest.mark.parametrize('stray', [('P9',), ('probe',), ('P1', 'pilot'), ('P1', 'old', 'claude-haiku-5-5'), ('notes.txt',)])
def test_tally_refuses_a_folder_or_file_outside_the_run(world, stray):
    runs, tscratch = world
    write_rep(runs, tscratch)
    path = runs.joinpath(*stray)
    if path.suffix:
        path.write_text('x\n')
    else:
        path.mkdir(parents=True, exist_ok=True)
    with pytest.raises(SystemExit, match=re.escape(stray[-1])):
        triggers.tally(runs)


def write_full_run(runs: Path, tscratch: Path, loads: dict) -> None:
    '''Every cell with 3 reps; loads[(prompt, arm, model)] reps of a cell (the first ones) load the skill.'''
    for prompt in trigger_prompts.PROMPTS:
        for arm in ('old', 'new'):
            for model in (SONNET, OPUS):
                for n in (1, 2, 3):
                    calls = [skill_use('classification-codes')] if n <= loads.get((prompt, arm, model), 0) else []
                    write_rep(runs, tscratch, prompt=prompt, arm=arm, model=model, n=n, calls=calls)


def test_tally_command_prints_the_counts_the_bars_and_the_verdict(world):
    runs, tscratch = world
    loads = {(prompt, arm, model): 2 for prompt in trigger_prompts.SHOULD_LOAD for arm in ('old', 'new')
             for model in (SONNET, OPUS)}
    write_full_run(runs, tscratch, loads)
    env = {**os.environ, 'CD_TRIGGER_SCRATCH': str(tscratch)}
    done = kit_tool(str(KIT / 'triggers.py'), 'tally', str(runs), env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    assert f'P1 new {OPUS}: 2 of 3 (void 0)' in done.stdout and f'N4 old {SONNET}: 0 of 3 (void 0)' in done.stdout
    assert f'bar near-miss {SONNET}: old 0, new 0, ok' in done.stdout
    assert done.stdout.rstrip().endswith('verdict: pass')
    loads[('N4', 'new', SONNET)] = 1
    runs2 = runs.parent / 'runs2'
    write_full_run(runs2, tscratch.parent / 'tscratch2', loads)
    env = {**os.environ, 'CD_TRIGGER_SCRATCH': str(tscratch.parent / 'tscratch2')}
    done = kit_tool(str(KIT / 'triggers.py'), 'tally', str(runs2), env=env)
    assert f'bar near-miss {SONNET}: old 0, new 1, MISSED' in done.stdout
    assert done.stdout.rstrip().endswith('verdict: fail')


# --- trigger_prompts.py -----------------------------------------------------------------------------------------


def test_the_trigger_prompts_are_the_nine_of_the_plan():
    assert list(trigger_prompts.PROMPTS) == ['P1', 'P2', 'P3', 'P4', 'P5', 'N1', 'N2', 'N3', 'N4']
    assert trigger_prompts.SHOULD_LOAD == ('P1', 'P2', 'P3', 'P4', 'P5')
    assert trigger_prompts.IND == ('P1', 'P2')
    assert trigger_prompts.NEAR_MISS == ('N1', 'N2', 'N3', 'N4')
    assert trigger_prompts.PROMPTS == {
        'P1': ('Our CPS extract has an IND column with values like 7860 and 0770. What industries are those, and which '
               'NAICS codes do they cover?'),
        'P2': ('I need to join ACS PUMS records coded with 2017 Census industry codes to QCEW data keyed by NAICS. How '
               'do I map one to the other?'),
        'P3': 'What is the 2022 NAICS title for 541511, and did that code change from 2017?',
        'P4': 'Map these SOC 2010 codes to SOC 2018: 15-1132 and 15-1133.',
        'P5': 'Our ACS file has OCCP 1021. Which occupation is that?',
        'N1': 'Which counties are in the Austin-Round Rock CBSA?',
        'N2': 'How does the CES birth-death model feed into the monthly payroll estimate?',
        'N3': 'How do I compute an unemployment rate from CPS microdata with the PWSSWGT weight?',
        'N4': 'Write a Polars function that drops duplicate rows keyed on series_id and ref_date.',
    }


def test_the_trigger_prompts_command_prints_one_prompt_or_the_probe():
    done = kit_tool(str(KIT / 'trigger_prompts.py'), 'N3')
    assert done.returncode == 0, done.stderr
    assert done.stdout == trigger_prompts.PROMPTS['N3'] + '\n'
    done = kit_tool(str(KIT / 'trigger_prompts.py'), 'probe')
    assert done.returncode == 0, done.stderr
    assert done.stdout == (KIT / 'isolation_probe.txt').read_text()
    assert trigger_prompts.PROBE not in trigger_prompts.PROMPTS
    assert kit_tool(str(KIT / 'trigger_prompts.py'), 'P9').returncode != 0


# --- the kit's own files ------------------------------------------------------------------------------------------


def test_the_probe_is_plan_107s_eight_question_probe():
    assert (KIT / 'isolation_probe.txt').read_bytes() == PLAN107_PROBE.read_bytes()


def test_the_case_names_the_skill_the_listing_and_the_quarantine():
    assert cases.SKILL == 'classification-codes' and triggers.SKILL == cases.SKILL
    assert cases.REQUIRED_LISTING == LISTED
    assert cases.MODELS == (OPUS, SONNET) and cases.ARMS == ('old', 'new') and cases.REPS_PER_CELL == 3
    assert cases.QUARANTINE == ('111-codes-and-bls-reference-skills', 'red-baseline-codes-description',
                                'deferred_items.md')


def test_the_trigger_fixture_is_a_neutral_project_beside_the_listing():
    trigger = KIT / 'fixtures' / 'trigger'
    assert sorted(str(p.relative_to(trigger)) for p in trigger.rglob('*') if p.is_file()) == ['listing.txt',
                                                                                             'repo/README.md']
    assert (trigger / 'listing.txt').read_text() == ''.join(name + '\n' for name in LISTED)
    readme = (trigger / 'repo' / 'README.md').read_text()
    for word in ('classification', 'geographic', 'bls', 'naics', 'soc', 'census', 'cps', 'acs', 'qcew', 'ind', 'occ',
                 'industry', 'occupation', 'county', 'skill'):
        assert not re.search(rf'\b{word}', readme, re.I), word


def test_this_repositorys_head_holds_each_listed_skill():
    for name in LISTED:
        found = subprocess.run(['git', '-C', str(REPO_ROOT), 'ls-tree', '--name-only', 'HEAD', f'skills/{name}/SKILL.md'],
                               capture_output=True, text=True)
        assert found.stdout.strip() == f'skills/{name}/SKILL.md', name


def kit_files() -> list[Path]:
    return sorted(p for p in KIT.rglob('*') if p.is_file() and '__pycache__' not in p.parts
                  and '.pytest_cache' not in p.parts and p.name != 'test_cd_kit.py')


def test_no_kit_file_keeps_a_plan_107_name_or_a_user_path():
    names = ('wst107', 'WST_', 'plan107', 'cut150', 'skill-creator', 'skill-development', 'competitor')
    for path in kit_files():
        text = path.read_text()
        for name in names:
            assert name.lower() not in text.lower(), (path.name, name)
        if path.name != 'isolation_probe.txt':
            assert 'writing-skills' not in text.replace('red-baseline-writing-skills-tests', ''), path.name
        assert '/Users/' not in text.replace('//Users/**', ''), path.name


def test_common_sh_names_the_pinned_roots():
    common = (KIT / 'common.sh').read_text()
    assert 'CD_TROOT=${CD_TROOT:-/private/tmp/cd111t}' in common
    assert 'CD_TRIGGER_SCRATCH=${CD_TRIGGER_SCRATCH:-$HOME/.cache/agent-skills/scratch/plan111/triggers}' in common
    assert audit.DEFAULT_SCRATCH == '.cache/agent-skills/scratch/plan111/triggers'
