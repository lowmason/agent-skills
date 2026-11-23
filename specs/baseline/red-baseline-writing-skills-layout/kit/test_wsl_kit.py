'''Self-tests for plan 105's guard kit, on synthetic records and folders. No test runs a model.

The runner tests start a stub claude (a bash script given as CLAUDE_BIN, or found on PATH) with every
root, scratch and fixture path moved into the test's temporary folder (the WSL_* variables and
KIT_SCRATCH_ROOT). A runner starts the stub under `env -i`, so every path the stub needs is written into
its text. The audit, sheet and read-check tests call the kit's Python in-process, on synthetic records.
Sources: plan 103's postprocess and runner tests (specs/baseline/red-baseline-worktree-skills-fix/kit/),
plan 104's runner and audit tests (specs/baseline/red-baseline-mutant-screen-runs/kit/test_msr_kit.py),
adapted to this kit's names, and the tests that plan 105's Task 3 names.
'''
import hashlib
import importlib.util
import itertools
import json
import os
import re
import subprocess
from pathlib import Path

import pytest

import audit
import cases
import sheets
from postprocess import postprocess

KIT = Path(__file__).resolve().parent
PLAN72_CASES = KIT.parents[1] / 'red-baseline-writing-skills-split' / 'kit' / 'cases.py'
PLAN104_PROBE = KIT.parents[1] / 'red-baseline-mutant-screen-runs' / 'kit' / 'isolation_probe.txt'
RUN_JSON = KIT / 'run_json_reps.sh'
PROBE_JSON = KIT / 'probe_json.sh'
RUN_TOOLS = KIT / 'run_tool_reps.sh'
PROBE_TOOLS = KIT / 'probe_tools.sh'
SONNET, OPUS = 'claude-sonnet-5-5', 'claude-opus-5-5'
FIELD = 'credential_expires_at'
TOOLS = 'Read,Glob,Grep,Edit,Write'
CROSS_SESSION_TOOLS = ('ListAgents', 'SendMessage', 'PushNotification', 'RemoteTrigger')
PATH_RULES = ('Read(//Users/**)', 'Edit(//Users/**)', 'Write(//Users/**)', 'Read(~/Library/**)',
              'Edit(~/Library/**)', 'Write(~/Library/**)')
SHELL_ADDED = {'PWD', 'SHLVL', '_', 'OLDPWD'}
DISABLE = ('CLAUDE_CODE_DISABLE_ADVISOR_TOOL', 'CLAUDE_CODE_DISABLE_AUTO_MEMORY')
REP_DIR = '/private/tmp/wsl105/rep1'
SKILL_ROOT = '/private/tmp/wsl105-skill'
SKILL = f'{SKILL_ROOT}/writing-skills'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(cmd: list[str], env: dict | None = None, cwd: Path = KIT, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, env=env, cwd=cwd, capture_output=True, text=True, check=False, timeout=timeout)


def kit_tool(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return run(['uv', 'run', '--no-project', '-q', 'python', *args], env=env)


# --- postprocess.py: plan 103's tests, copied -----------------------------------------------------------


def test_a_peer_turn_voids_the_rep():
    # A message sent to a busy no-tools rep arrives as an extra turn. The JSON `result` is then the
    # reply to that message, and `result_index` is 1.
    rep = postprocess({'result': 'a reply to a peer', 'result_index': 1, 'origin': None})
    assert rep['void'] is True
    assert rep['reason'] == 'result_index'


def test_an_origin_voids_the_rep():
    rep = postprocess({'result': 'a reply to a peer', 'result_index': 0, 'origin': {'kind': 'peer'}})
    assert rep['void'] is True
    assert rep['reason'] == 'origin'


def test_a_clean_rep_is_kept_without_origin_or_credential_expiry():
    rep = postprocess({'result': 'ok', 'result_index': 0, 'origin': None, 'credential_expires_at': 1790000000})
    assert rep['void'] is False
    assert 'origin' not in rep
    assert 'credential_expires_at' not in rep
    assert rep['result'] == 'ok'


# Plan 103's postprocess shapes (test_postprocess_shapes.py), copied. The fake home is /home-for-test/zed,
# not a path under the real home's parent, so the privacy sweep reads no home in this file.
CLEAN = {'result': 'ok', 'result_index': 0, 'origin': None}


def test_a_later_peer_turn_voids_whatever_the_index():
    assert postprocess({**CLEAN, 'result_index': 2})['reason'] == 'result_index'


def test_index_zero_with_no_origin_is_kept():
    rep = postprocess(dict(CLEAN))
    assert rep['void'] is False
    assert rep['result_index'] == 0


def test_a_rep_with_no_result_index_or_origin_key_is_kept():
    assert postprocess({'result': 'ok'}) == {'void': False, 'result': 'ok'}


@pytest.mark.parametrize('origin', [{}, {'kind': 'peer', 'session_title': 'x'}, 'peer'])
def test_any_origin_that_is_not_null_voids_the_rep(origin):
    assert postprocess({**CLEAN, 'origin': origin}) == {'void': True, 'reason': 'origin'}


@pytest.mark.parametrize('index', ['0', 0.0, 1.0, True, False, None, [0]])
def test_a_result_index_that_is_not_a_whole_number_voids_the_rep(index):
    assert postprocess({**CLEAN, 'result_index': index}) == {'void': True, 'reason': 'result_index'}


def test_result_index_is_named_first_when_both_fields_show_a_peer_turn():
    assert postprocess({'result': 'x', 'result_index': 3, 'origin': {'kind': 'peer'}})['reason'] == 'result_index'


def test_the_private_keys_go_at_any_depth():
    raw = {'result': 'ok', 'result_index': 0, 'origin': None, 'session_id': 's', 'uuid': 'u',
           'credential_expires_at': 1,
           'modelUsage': {'claude-sonnet-5-5': {'costUSD': 0.01, 'credential_expires_at': 2}},
           'iterations': [{'type': 'message', 'origin': {'kind': 'x'}, 'uuid': 'u2'}]}
    assert postprocess(raw) == {'void': False, 'result': 'ok', 'result_index': 0,
                                'modelUsage': {'claude-sonnet-5-5': {'costUSD': 0.01}},
                                'iterations': [{'type': 'message'}]}


def test_every_string_is_scrubbed_home_tmpdir_and_identity(monkeypatch):
    import postprocess as module
    monkeypatch.setenv('HOME', '/home-for-test/zed')
    monkeypatch.setenv('TMPDIR', '/var/folders/ab/cd/T/')
    monkeypatch.setattr(module.kit_identity, 'forms', lambda: [('Dana Quill', '<USER-NAME>')])
    raw = {'result': 'Dana Quill wrote /home-for-test/zed/notes.md in /private/var/folders/ab/cd/T/run1',
           'modelUsage': {'Dana Quill': {'note': ['see /var/folders/ab/cd/T/x']}}}
    rep = postprocess(raw)
    assert rep['result'] == '<USER-NAME> wrote ~/notes.md in $TMPDIR/run1'
    assert rep['modelUsage'] == {'<USER-NAME>': {'note': ['see $TMPDIR/x']}}


@pytest.mark.parametrize('raw_text', [None, '', 'not json', '[1, 2]'])
def test_the_postprocess_command_voids_an_unreadable_raw_file(tmp_path, capsys, raw_text):
    import postprocess as module
    raw = tmp_path / 'raw.json'
    if raw_text is not None:
        raw.write_text(raw_text)
    dest, note = tmp_path / 'rep1.json', tmp_path / 'rep1.VOID'
    assert module.main([str(raw), str(dest), str(note)]) == 0
    assert capsys.readouterr().out.strip() == 'unreadable'
    assert note.read_text().startswith('VOID:')
    assert not dest.exists()


# --- run_json_reps.sh and probe_json.sh: plan 103's runner tests, adapted ----------------------------------

JSON_STUB = r'''#!/bin/bash
id="$(mktemp '@DIR@/call.XXXXXX')"
printf '%s\0' "$@" > "$id.argv"
env > "$id.env"
cat > "$id.stdin"
pwd -P > "$id.cwd"
ls -A > "$id.ls"
git rev-parse --show-toplevel > "$id.git" 2>&1
echo "exit $?" >> "$id.git"
cat '@DIR@/reply.json'
'''
KEEP = ('HOME', 'USER', 'LOGNAME', 'PATH', 'SHELL', 'TMPDIR', 'LANG')
SENTINELS = {'FAKE_PEER_SOCKET': '/tmp/peer.sock', 'CLAUDE_CODE_SESSION_ID': 'abc-123',
             'CLAUDE_CODE_ENTRYPOINT': 'desktop', 'ANTHROPIC_API_KEY': 'sk-not-real', 'LLM_WIKI_ROOT': '/wiki'}


def json_flags(model: str) -> list[str]:
    return ['-p', '--model', model, '--tools', '', '--strict-mcp-config', '--setting-sources', '',
            '--disable-slash-commands', '--no-session-persistence', '--output-format', 'json',
            '--max-budget-usd', '0.50']


class JsonCall:
    def __init__(self, stem: str) -> None:
        self.argv = Path(f'{stem}.argv').read_bytes().decode().split('\0')[:-1]
        self.env = dict(line.split('=', 1) for line in Path(f'{stem}.env').read_text().splitlines() if '=' in line)
        self.stdin = Path(f'{stem}.stdin').read_text()
        self.cwd = Path(f'{stem}.cwd').read_text().strip()
        self.listing = Path(f'{stem}.ls').read_text().split()
        self.git = Path(f'{stem}.git').read_text()


class JsonWorld:
    def __init__(self, tmp: Path) -> None:
        self.tmp = tmp
        self.stub_dir = tmp / 'stub'
        self.stub_dir.mkdir()
        stub = self.stub_dir / 'claude'
        stub.write_text(JSON_STUB.replace('@DIR@', str(self.stub_dir)))
        stub.chmod(0o755)
        self.reply({'result': 'ok', 'result_index': 0, 'origin': None})
        self.prompt = tmp / 'W1.txt'
        self.prompt.write_text('a prompt, line one\nline two\n')
        self.runs = tmp / 'runs'
        self.scratch_root = tmp / 'scratch'
        # The caller's environment: LANG and LOGNAME are left out, so the test can see that a rep gets
        # only what the caller has. The planted variables must not reach a rep.
        self.env = {v: os.environ[v] for v in KEEP if v in os.environ and v not in ('LANG', 'LOGNAME')}
        self.env['PATH'] = f'{self.stub_dir}:{os.environ["PATH"]}'
        self.env.update(SENTINELS)
        self.env.update({v: '0' for v in DISABLE})
        self.env['KIT_SCRATCH_ROOT'] = str(self.scratch_root)

    def reply(self, data: dict) -> None:
        (self.stub_dir / 'reply.json').write_text(json.dumps(data))

    def out(self, case: str = 'W1', arm: str = 'old', model: str = SONNET) -> Path:
        return self.runs / case / arm / model

    def raw(self, case: str = 'W1', arm: str = 'old', model: str = SONNET) -> Path:
        return self.scratch_root / 'plan105' / 'json' / case / arm / model

    def run_reps(self, first: int = 1, last: int = 1, case: str = 'W1', model: str = SONNET
                 ) -> subprocess.CompletedProcess:
        return run(['bash', str(RUN_JSON), str(self.prompt), str(self.out(case, model=model)), str(first), str(last),
                    model], env=self.env)

    def run_probe(self, model: str = SONNET) -> subprocess.CompletedProcess:
        return run(['bash', str(PROBE_JSON), model, str(self.tmp / 'probe' / 'probe.json')], env=self.env)

    def calls(self) -> list[JsonCall]:
        return [JsonCall(str(path)[:-len('.argv')]) for path in sorted(self.stub_dir.glob('call.*.argv'))]


@pytest.fixture
def jworld(tmp_path: Path) -> JsonWorld:
    return JsonWorld(tmp_path)


def json_started(world: JsonWorld, via: str, model: str = SONNET) -> list[JsonCall]:
    done = world.run_reps(model=model) if via == 'run' else world.run_probe(model)
    assert done.returncode == 0, done.stdout + done.stderr
    return world.calls()


@pytest.mark.parametrize('model', [SONNET, OPUS])
@pytest.mark.parametrize('via', ['run', 'probe'])
def test_json_rep_and_probe_start_claude_with_the_isolation_flags(jworld, via, model):
    [call] = json_started(jworld, via, model)
    assert call.argv == json_flags(model)
    expected = (KIT / 'isolation_probe.txt').read_text() if via == 'probe' else 'a prompt, line one\nline two\n'
    assert call.stdin == expected


@pytest.mark.parametrize('via', ['run', 'probe'])
def test_json_rep_env_holds_only_the_kept_variables(jworld, via):
    [call] = json_started(jworld, via)
    expected = {v: jworld.env[v] for v in KEEP if v in jworld.env}
    assert {k: call.env[k] for k in call.env if k in KEEP} == expected
    assert call.env['CLAUDE_CODE_DISABLE_ADVISOR_TOOL'] == '1'
    assert call.env['CLAUDE_CODE_DISABLE_AUTO_MEMORY'] == '1'
    assert set(call.env) <= set(KEEP) | set(DISABLE) | SHELL_ADDED
    assert not (set(SENTINELS) & set(call.env))


@pytest.mark.parametrize('via', ['run', 'probe'])
def test_json_rep_starts_in_a_new_empty_folder_outside_every_repository(jworld, via):
    [call] = json_started(jworld, via)
    assert call.cwd.startswith(('/tmp/plan105-rep-', '/private/tmp/plan105-rep-'))
    assert call.listing == []
    assert call.git.splitlines()[-1] == 'exit 128'


def test_json_probe_refuses_a_model_outside_the_plan(jworld):
    done = jworld.run_probe('claude-haiku-5-5')
    assert done.returncode == 2
    assert jworld.calls() == []


def test_json_scratch_keeps_each_case_arm_and_model_apart(jworld):
    # Task 6 writes W reps to runs/<case>/<arm>/<model>/. Two cases with the same arm and model must not
    # share a scratch folder, or the overwrite guard refuses the second case's rep1.
    jworld.reply({'result': 'ok', 'result_index': 0, 'origin': None, 'credential_expires_at': 1, 'session_id': 's'})
    for case in ('W1', 'W2'):
        done = jworld.run_reps(case=case)
        assert done.returncode == 0, done.stdout + done.stderr
        assert json.loads((jworld.raw(case) / 'rep1.json').read_text())['credential_expires_at'] == 1
        kept = (jworld.out(case) / 'rep1.json').read_text()
        assert json.loads(kept)['result'] == 'ok'
        assert 'credential_expires_at' not in kept and 'session_id' not in kept


def test_a_void_json_rep_gets_a_note_and_no_json_and_the_batch_exits_3(jworld):
    jworld.reply({'result': 'a reply to a peer', 'result_index': 1, 'origin': None})
    done = jworld.run_reps()
    assert done.returncode == 3, done.stdout + done.stderr
    assert 'rep1 VOID (void result_index)' in done.stdout
    assert (jworld.out() / 'rep1.VOID').read_text().startswith('VOID: result_index')
    assert not (jworld.out() / 'rep1.json').exists()
    assert json.loads((jworld.raw() / 'rep1.json').read_text())['result'] == 'a reply to a peer'


# --- common.sh, run_tool_reps.sh and probe_tools.sh: plan 104's runner tests, adapted ------------------------

TOOL_STUB = r'''#!/bin/bash
log='@DIR@/calls.log'
printf '%s\n' "$*" >> "$log"
n=$(wc -l < "$log" | tr -d ' ')
cat > '@DIR@'/stdin.$n
printf '%s\n' "$@" > '@DIR@'/args.$n
env > '@DIR@'/env.$n
if [ -f '@DIR@'/actions.sh ]; then . '@DIR@'/actions.sh; fi
printf '{"type":"system","subtype":"init","cwd":"%s","tools":["Read","Glob","Grep","Edit","Write"],' "$PWD"
printf '"model":"claude-sonnet-5-5","credential_expires_at":1790000000}\n'
printf '{"type":"assistant","message":{"content":[{"type":"text","text":"Done."}]}}\n'
if [ -f '@DIR@'/extra_lines ]; then cat '@DIR@'/extra_lines; fi
printf '{"type":"result","subtype":"success","is_error":false,"result":"Done.","num_turns":1,'
printf '"total_cost_usd":0.01,"credential_expires_at":1790000000,'
printf '"modelUsage":{"claude-sonnet-5-5":{"costUSD":0.01,"credential_expires_at":1790000000}}}\n'
'''
TOOL_ENV = set(KEEP) | set(DISABLE)


class ToolKit:
    '''One test's temporary world for the tools runner.'''

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

    def fixture(self, name: str = 'T1', arm: str = 'old') -> None:
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
                'SHELL': '/bin/bash', 'LANG': 'C', 'WSL_ROOT': str(self.root), 'WSL_SCRATCH': str(self.scratch),
                'WSL_FIXTURES': str(self.fixtures), 'CLAUDE_BIN': str(self.stub)}

    def out(self, name: str = 'T1', arm: str = 'old', model: str = SONNET) -> Path:
        return self.tmp / 'out' / name / arm / model

    def run(self, name: str = 'T1', first: int = 1, last: int = 1, model: str = SONNET, out: Path | None = None
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

    def summary(self, rep: int = 1, name: str = 'T1') -> dict:
        return json.loads((self.out(name) / f'rep{rep}' / 'summary.json').read_text())

    def stream(self, rep: int = 1, name: str = 'T1') -> Path:
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
    parked = tkit.scratch / 'T1' / 'old' / SONNET / 'rep1-folder'
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


def test_rep_env_holds_only_the_pinned_names(tkit):
    tools_ok(tkit)
    env = dict(line.split('=', 1) for line in (tkit.stub_dir / 'env.1').read_text().splitlines() if '=' in line)
    assert set(env) - SHELL_ADDED <= TOOL_ENV
    folder = os.path.realpath(tkit.root / 'rep1')
    assert env['HOME'] == f'{folder}/home'
    assert env['TMPDIR'] == f'{folder}/tmp'
    assert env['PATH'] == '/usr/bin:/bin:/usr/sbin:/sbin'
    assert env['CLAUDE_CODE_DISABLE_AUTO_MEMORY'] == '1'
    assert os.readlink(tkit.scratch / 'T1' / 'old' / SONNET / 'rep1-folder' / 'home' / 'Library'
                       / 'Keychains') == str(tkit.real / 'Library' / 'Keychains')


def test_the_rep_starts_in_its_fixture_committed_as_base(tkit):
    tkit.actions(f'git log --format=%s > \'{tkit.tmp}/log.txt\'; ls -A > \'{tkit.tmp}/ls.txt\'\n')
    tools_ok(tkit)
    assert (tkit.tmp / 'log.txt').read_text() == 'Start the project\n'
    assert sorted((tkit.tmp / 'ls.txt').read_text().split()) == ['.git', 'notes.txt', 'specs']
    summary = tkit.summary()
    assert len(summary['base']) == 40
    assert summary['case'] == 'T1' and summary['arm'] == 'old' and summary['model'] == SONNET
    # summary.json is scrubbed, and the scrub writes pytest-of-<user> as pytest-of-$USER.
    user = os.environ.get('USER') or 'tester'
    assert summary['skill_root'] == str(tkit.skill).replace(f'pytest-of-{user}', 'pytest-of-$USER')
    assert (tkit.scratch / 'T1' / 'old' / SONNET / 'rep1.prompt.txt').read_text() == 'Do the task.\n'


@pytest.mark.parametrize('where', ['case', 'arm', 'model'])
def test_refuses_an_out_dir_that_misnames_the_case_arm_or_model(tkit, where):
    names = {'case': 'T1', 'arm': 'old', 'model': SONNET}
    names[where] = {'case': 'T2', 'arm': 'new', 'model': OPUS}[where]
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


def test_final_diff_holds_new_and_changed_files_against_base(tkit):
    tkit.actions('echo second line >> notes.txt; printf "# Scenarios\\n" > specs/new-scenarios.md\n')
    tools_ok(tkit)
    diff = (tkit.out() / 'rep1' / 'final.diff').read_text()
    assert '+second line' in diff
    assert 'specs/new-scenarios.md' in diff and '+# Scenarios' in diff
    assert tkit.summary()['status_porcelain'] != []


def test_summary_marks_each_failed_tool_call(tkit):
    use = {'type': 'tool_use', 'id': 't1', 'name': 'Read', 'input': {'file_path': '/nowhere/persuasion-principles.md'}}
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


def test_both_probes_send_plan_104s_eight_question_probe():
    assert (KIT / 'isolation_probe.txt').read_bytes() == PLAN104_PROBE.read_bytes()


# --- audit.py: the stream audit (V9 and record counts) -----------------------------------------------------

REP_TOOLS = ('Read', 'Glob', 'Grep', 'Edit', 'Write')
RESULT = {'type': 'result', 'subtype': 'success', 'is_error': False, 'result': 'Done.', 'total_cost_usd': 0.01}


def stream_lines(calls=(), errors=(), extra=(), result=None, init_tools=REP_TOOLS) -> list[str]:
    lines = [json.dumps({'type': 'system', 'subtype': 'init', 'tools': list(init_tools)})]
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


@pytest.fixture
def world(tmp_path: Path, monkeypatch) -> tuple[Path, Path]:
    runs, scratch = tmp_path / 'runs', tmp_path / 'scratch'
    monkeypatch.setenv('WSL_SCRATCH', str(scratch))
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
    ('Glob', {'pattern': '{/private/tmp/wsl105/rep2,x}/**'}, ('outside the allowed roots',)),
    ('Glob', {'pattern': '{x,y,/tmp/wsl105/rep2/repo}/*'}, ('outside the allowed roots',)),
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
    ('Grep', {'pattern': 'plan', 'path': '/tmp/wsl105/rep1/repo/skills'}),
    ('Glob', {'pattern': '**/*.md'}),
    ('Glob', {'pattern': f'{SKILL}/**/*.md'}),
    ('Glob', {'pattern': '/tmp/wsl105-skill/writing-skills/*.dot'}),
    ('Glob', {'pattern': 'references/*.md', 'path': SKILL}),
    ('Glob', {'pattern': 'specs/../skills/*/SKILL.md'}),
    ('Glob', {'pattern': '*.md', 'path': f'{REP_DIR}/repo/specs'}),
    # Only the literal part is judged: this pattern searches the repository alone.
    ('Glob', {'pattern': f'{REP_DIR}/repo/**{HOME}/notes.md'}),
    # The recorded Glob limit (Kit, Grep and Glob): a relative brace alternative under an absolute prefix
    # is not joined to it, so this spelling of $HOME/Library/Keychains is no hit, like a `**` from the
    # rep folder. The Keychains link holds neither the spec nor the plan.
    ('Glob', {'pattern': f'{REP_DIR}/{{home/Library/Keychains,x}}/*'}),
    # Brace alternatives inside the allowed roots stay clean.
    ('Glob', {'pattern': f'{{{SKILL}/references,{REP_DIR}/repo/specs}}/*.md'}),
    ('Glob', {'pattern': '{/tmp/wsl105/rep1/repo/specs,skills/*}/*.md'}),
    ('Glob', {'pattern': 'skills/{secrets-scan-gate,{http-retry-policy,x}}/SKILL.md'}),
    ('Glob', {'pattern': f'{SKILL}/{{references,scripts}}/*'}),
])
def test_path_audit_passes_grep_and_glob_inside_roots(name, args):
    assert hits(name, **args) == []


@pytest.mark.parametrize(('tool', 'path', 'why'), [
    ('Read', f'{REP_DIR}/repo/../home/Library/Keychains/x', '$HOME/Library'),
    ('Read', f'{REP_DIR}/../../wsl105-skill/x', None),
    ('Read', f'{REP_DIR}/../../msr104-skill/x', 'outside the allowed roots'),
    ('Write', f'{REP_DIR}/../../../etc/x', 'outside the allowed roots'),
    ('Read', f'{REP_DIR}/home/Library/Keychains/../../x', '$HOME/Library'),
    ('Read', '~/Library/Keychains/../../x', '$HOME/Library'),
    ('Read', '~/library/Keychains/../../x', '$HOME/Library'),
    ('Read', f'{REP_DIR}/home/library/Keychains/x', '$HOME/Library'),
    ('Read', f'{HOME}/notes.txt', 'the real home'),
    ('Read', f'{REP_DIR}/repo/skills/secrets-scan-gate/SKILL.md', None),
    ('Read', f'{REP_DIR}/repo/specs/../skills/x', None),
    ('Read', '/tmp/wsl105/rep1/repo/x', None),
    ('Read', f'{SKILL}/references/persuasion-principles.md', None),
    ('Edit', f'{SKILL}/SKILL.md', 'a write into a read-only root'),
    ('Write', f'/tmp/wsl105-skill/writing-skills/x.md', 'a write into a read-only root'),
    ('Read', '/private/tmp/wsl105/rep2/repo/x', 'outside the allowed roots'),
])
def test_path_audit_resolves_dot_dot_in_a_file_path(tool, path, why):
    found = hits(tool, file_path=path)
    if why is None:
        assert found == []
    else:
        assert found == [f'call 1 {tool}: {path} ({why})']


@pytest.mark.parametrize(('tool', 'path', 'why'), [
    ('Edit', 'skills/secrets-scan-gate/SKILL.md', None),
    ('Read', 'specs/../pyproject.toml', None),
    ('Read', '../../rep2/repo/x', 'outside the allowed roots'),
    ('Write', '../../../etc/x', 'outside the allowed roots'),
    ('Read', '../home/Library/Keychains/x', '$HOME/Library'),
])
def test_path_audit_joins_a_relative_file_path_to_the_repository(tool, path, why):
    found = hits(tool, file_path=path)
    assert found == ([] if why is None else [f'call 1 {tool}: {path} ({why})'])


def test_path_audit_flags_a_real_home_path_in_a_bash_command():
    found = hits('Bash', command=f'for f in {HOME}/.ssh/id_rsa ~/notes.txt; do cat "$f"; done')
    assert len(found) == 1 and 'real home' in found[0]
    assert '$HOME/Library' in hits('Bash', command='ls ~/Library/Keychains')[0]


# --- audit.py: the read check (the reading rule's Read part) ------------------------------------------------

T2_MOVED_OLD = f'{SKILL}/persuasion-principles.md'
T2_MOVED_NEW = f'{SKILL}/references/persuasion-principles.md'
T2_TARGET = f'{REP_DIR}/repo/skills/secrets-scan-gate/SKILL.md'


def call(name: str, is_error: bool = False, **args) -> dict:
    return {'name': name, 'input': args, 'is_error': is_error}


def test_read_before_write_passes_read_then_edit():
    calls = [call('Read', file_path=f'{SKILL}/references/bulletproofing.md'), call('Read', file_path=T2_MOVED_OLD),
             call('Edit', file_path=T2_TARGET, old_string='a', new_string='b')]
    check = audit.read_check(calls, 'T2', REP_DIR)
    assert check['verdict'] == 'PASS'
    assert [read['call'] for read in check['reads']] == [2]
    assert check['first_write'] == 3


def test_read_before_write_fails_edit_then_read():
    calls = [call('Edit', file_path=T2_TARGET, old_string='a', new_string='b'), call('Read', file_path=T2_MOVED_NEW)]
    check = audit.read_check(calls, 'T2', REP_DIR)
    assert check['verdict'] == 'FAIL'
    assert [read['call'] for read in check['reads']] == [2]
    assert check['first_write'] == 1
    # Only the first write of the target counts, so a read between two writes does not pass.
    later = audit.read_check(calls + [call('Write', file_path=T2_TARGET, content='x')], 'T2', REP_DIR)
    assert later['first_write'] == 1 and later['verdict'] == 'FAIL'


def test_read_before_write_passes_read_without_write():
    check = audit.read_check([call('Read', file_path=T2_MOVED_NEW)], 'T2', REP_DIR)
    assert check['verdict'] == 'PASS'
    assert check['first_write'] is None
    assert audit.read_check([call('Read', file_path=f'{SKILL}/SKILL.md')], 'T2', REP_DIR)['verdict'] == 'FAIL'
    assert audit.read_check([], 'T2', REP_DIR)['verdict'] == 'FAIL'


def test_read_of_a_longer_name_does_not_count():
    for path in (f'{SKILL}/old-persuasion-principles.md', f'{SKILL}/persuasion-principles.md.bak',
                 f'{SKILL}/references/mypersuasion-principles.md'):
        calls = [call('Read', file_path=path), call('Edit', file_path=T2_TARGET, old_string='a', new_string='b')]
        check = audit.read_check(calls, 'T2', REP_DIR)
        assert check['reads'] == [], path
        assert check['verdict'] == 'FAIL', path


def test_grep_or_glob_of_the_moved_file_does_not_count():
    calls = [call('Grep', pattern='Liking', path=T2_MOVED_OLD), call('Glob', pattern='**/persuasion-principles.md'),
             call('Read', file_path=f'{SKILL}/references/bulletproofing.md')]
    check = audit.read_check(calls, 'T2', REP_DIR)
    assert check['reads'] == []
    assert check['verdict'] == 'FAIL'


def test_partial_read_is_marked_partial():
    calls = [call('Read', file_path=T2_MOVED_NEW, offset=1, limit=40), call('Read', file_path=T2_MOVED_NEW, limit=20),
             call('Read', file_path=T2_MOVED_NEW, offset=0), call('Read', file_path=T2_MOVED_NEW),
             call('Write', file_path=T2_TARGET, content='x')]
    check = audit.read_check(calls, 'T2', REP_DIR)
    assert [read['partial'] for read in check['reads']] == [True, True, True, False]
    assert check['verdict'] == 'PASS'
    only = audit.read_check(calls[:1] + calls[-1:], 'T2', REP_DIR)
    assert only['verdict'] == 'PASS' and only['reads'][0]['partial'] is True


def test_a_failed_read_is_marked_and_does_not_count():
    calls = [call('Read', is_error=True, file_path=T2_MOVED_NEW), call('Edit', file_path=T2_TARGET)]
    check = audit.read_check(calls, 'T2', REP_DIR)
    assert check['reads'][0]['error'] is True
    assert check['verdict'] == 'FAIL'
    assert audit.read_check(calls[:1], 'T2', REP_DIR)['verdict'] == 'FAIL'
    again = audit.read_check([calls[0], call('Read', file_path=T2_MOVED_NEW), calls[1]], 'T2', REP_DIR)
    assert [read['error'] for read in again['reads']] == [True, False]
    assert again['verdict'] == 'PASS'


def test_a_failed_write_of_the_target_still_counts_as_the_first_write():
    for name in ('Edit', 'Write'):
        calls = [call(name, is_error=True, file_path=T2_TARGET), call('Read', file_path=T2_MOVED_NEW),
                 call(name, file_path=T2_TARGET)]
        check = audit.read_check(calls, 'T2', REP_DIR)
        assert check['first_write'] == 1, name
        assert check['verdict'] == 'FAIL', name


@pytest.mark.parametrize(('case', 'moved', 'target'), [
    ('T1', 'testing-skills-with-subagents.md', 'specs/lockfile-refresh-scenarios.md'),
    ('T2', 'persuasion-principles.md', 'skills/secrets-scan-gate/SKILL.md'),
    ('T3', 'graphviz-conventions.dot', 'skills/http-retry-policy/SKILL.md'),
])
def test_the_target_is_the_case_file_in_the_rep_repository_only(case, moved, target):
    read = call('Read', file_path=f'{SKILL}/{moved}')
    for path, first in ((f'{REP_DIR}/repo/{target}', 2), (f'/tmp/wsl105/rep1/repo/{target}', 2),
                        (f'{REP_DIR}/repo/./{target}', 2), (f'{REP_DIR}/repo/old/{target}', None),
                        (f'{REP_DIR}/repo/{target}.bak', None), (f'/private/tmp/wsl105/rep2/repo/{target}', None)):
        check = audit.read_check([read, call('Write', file_path=path)], case, REP_DIR)
        assert check['first_write'] == first, path
        assert check['verdict'] == 'PASS'
    late = audit.read_check([call('Write', file_path=f'{REP_DIR}/repo/{target}'), read], case, REP_DIR)
    assert late['verdict'] == 'FAIL'


def test_a_relative_write_of_the_target_counts_as_the_first_write():
    relative = 'skills/secrets-scan-gate/SKILL.md'
    late = audit.read_check([call('Write', file_path=relative), call('Read', file_path=T2_MOVED_NEW)], 'T2', REP_DIR)
    assert late['first_write'] == 1 and late['verdict'] == 'FAIL'
    early = audit.read_check([call('Read', file_path=T2_MOVED_NEW), call('Edit', file_path=f'./{relative}')], 'T2',
                             REP_DIR)
    assert early['first_write'] == 2 and early['verdict'] == 'PASS'
    other = audit.read_check([call('Write', file_path=f'old/{relative}')], 'T2', REP_DIR)
    assert other['first_write'] is None


def test_audit_command_prints_each_rep(world):
    runs, scratch = world
    write_t_rep(runs, scratch, calls=[('Read', {'file_path': T2_MOVED_NEW, 'limit': 30}),
                                      ('Edit', {'file_path': T2_TARGET, 'old_string': 'a', 'new_string': 'b'})])
    write_t_rep(runs, scratch, n=2, extra=[json.dumps(RESULT)])
    done = kit_tool(str(KIT / 'audit.py'), str(runs / 'T2' / 'old' / SONNET),
                    env={**os.environ, 'WSL_SCRATCH': str(scratch)})
    assert done.returncode == 0, done.stdout + done.stderr
    first, second = done.stdout.split(f'== T2 old {SONNET} rep2')
    assert f'== T2 old {SONNET} rep1' in first
    assert 'reads of persuasion-principles.md: call 1 (partial)' in first
    assert 'read check: PASS' in first and 'VOID: none' in first
    assert 'VOID: a second result record' in second


# --- sheets.py ---------------------------------------------------------------------------------------------


def write_w_rep(runs: Path, case: str = 'W1', arm: str = 'old', model: str = SONNET, n: int = 1,
                result: str = 'ACTION: read x\n', void: bool = False, run: dict | None = None) -> None:
    folder = runs / case / arm / model
    folder.mkdir(parents=True, exist_ok=True)
    if void:
        (folder / f'rep{n}.VOID').write_text('VOID: result_index showed a peer turn.\n')
    else:
        kept = {'type': 'result', 'subtype': 'success', 'is_error': False, 'result': result, 'total_cost_usd': 0.01}
        (folder / f'rep{n}.json').write_text(json.dumps({**kept, **(run or {})}))


def build(tmp: Path, runs: Path, seed: str = 'seed-1') -> tuple[Path, dict]:
    sheet_dir = tmp / 'grading' / 'sheets'
    sheets.build(runs, sheet_dir, seed)
    return sheet_dir, json.loads((tmp / 'grading' / 'key.json').read_text())


def test_sheets_hide_the_arm(tmp_path, world):
    runs, scratch = world
    for arm, rel in (('old', 'persuasion-principles.md'), ('new', 'references/persuasion-principles.md')):
        path = f'{SKILL}/{rel}'
        final = f'I read `{path}`. See [{rel}]({rel}) and {rel}.'
        diff = f'+Principles from {rel}, as\n+{rel} says.\n'
        write_t_rep(runs, scratch, arm=arm, calls=[('Read', {'file_path': path})], final=final, diff=diff)
    sheet_dir, key = build(tmp_path, runs)
    sheet_files = sorted(sheet_dir.iterdir())
    assert len(sheet_files) == 2
    first, second = (p.read_bytes() for p in sheet_files)
    assert first == second
    text = first.decode()
    assert 'Case: T2' in text
    assert '<skill>/persuasion-principles.md' in text
    assert 'references/persuasion' not in text and 'writing-skills' not in text
    assert sorted(entry['arm'] for entry in key.values()) == ['new', 'old']
    assert all(len(name) == 6 and int(name, 16) >= 0 for name in key)
    assert sorted(p.stem for p in sheet_files) == sorted(key)


@pytest.mark.parametrize(('text', 'want'), [
    ('~/.claude/skills/writing-skills/references/discovery.md', '<skill>/discovery.md'),
    ('read graphviz-conventions.dot.', 'read <skill>/graphviz-conventions.dot.'),
    ('(../persuasion-principles.md)', '(<skill>/persuasion-principles.md)'),
    ('"file_path": "/tmp/wsl105-skill/writing-skills/testing-skills-with-subagents.md"',
     '"file_path": "<skill>/testing-skills-with-subagents.md"'),
    ('**references/flowcharts.md**', '**<skill>/flowcharts.md**'),
    ('+references/bulletproofing.md', '+<skill>/bulletproofing.md'),
    ('<skill>/persuasion-principles.md', '<skill>/persuasion-principles.md'),
    ('see old-persuasion-principles.md and persuasion-principles.md.bak',
     'see old-persuasion-principles.md and persuasion-principles.md.bak'),
    ('/private/tmp/wsl105-skill/writing-skills/SKILL.md', '<skill>/SKILL.md'),
    ('skills/secrets-scan-gate/SKILL.md and SKILL.md', 'skills/secrets-scan-gate/SKILL.md and SKILL.md'),
    ('the LICENSE file', 'the LICENSE file'),
])
def test_sheet_mask_writes_each_skill_path_as_skill_and_basename(text, want):
    assert sheets.mask(text) == want


def test_sheets_skip_void_reps_and_hold_the_answer(tmp_path, world):
    runs, scratch = world
    write_w_rep(runs, result='ACTION: read ~/.claude/skills/writing-skills/references/discovery.md\nHello.\n')
    write_w_rep(runs, n=2, void=True)
    write_t_rep(runs, scratch, case='T3', final='Added the chart.', diff='+```dot\n+digraph x {}\n')
    write_t_rep(runs, scratch, case='T3', n=2, extra=[json.dumps(RESULT)])
    sheet_dir, key = build(tmp_path, runs)
    assert sorted((e['case'], e['rep']) for e in key.values()) == [('T3', 1), ('W1', 1)]
    texts = {key[p.stem]['case']: p.read_text() for p in sheet_dir.iterdir()}
    assert 'ACTION: read <skill>/discovery.md\nHello.' in texts['W1']
    assert 'Added the chart.' in texts['T3'] and '+digraph x {}' in texts['T3']
    for case, text in texts.items():
        pass_line, fail_line = cases.COLUMNS[case]
        assert text.startswith(f'Case: {case}\n')
        assert f'PASS: {pass_line}' in text and f'FAIL: {fail_line}' in text
        assert SONNET not in text and 'rep1' not in text
    t3 = next(e for e in key.values() if e['case'] == 'T3')
    assert t3['read'] == 'FAIL' and t3['model'] == SONNET and t3['arm'] == 'old'


def test_sheets_skip_a_w_rep_whose_run_errored_and_its_replacement_keeps_five(tmp_path, world):
    runs, scratch = world
    for case, model, arm in itertools.product(('W1', 'W2', 'W3', 'T1', 'T2', 'T3'), (SONNET, OPUS), ('old', 'new')):
        for n in range(1, 6):
            if case.startswith('W'):
                write_w_rep(runs, case=case, arm=arm, model=model, n=n)
            else:
                write_t_rep(runs, scratch, case=case, arm=arm, model=model, n=n,
                            calls=[('Read', {'file_path': f'{SKILL}/{cases.MOVED[case]}'})])
    # Two W1 runs errored, one by its subtype and one by is_error, so reps 6 and 7 replace them.
    write_w_rep(runs, n=3, run={'subtype': 'error_during_execution', 'is_error': False})
    write_w_rep(runs, n=5, run={'subtype': 'success', 'is_error': True})
    write_w_rep(runs, n=6)
    write_w_rep(runs, n=7)
    _, skipped = sheets.collect(runs)
    assert skipped == [f'W1 old {SONNET} rep3: a run error: subtype error_during_execution',
                       f'W1 old {SONNET} rep5: a run error: is_error true']
    _, key = build(tmp_path, runs)
    assert sorted(e['rep'] for e in key.values() if (e['case'], e['arm'], e['model']) == ('W1', 'old', SONNET)) \
        == [1, 2, 4, 6, 7]
    result = sheets.unblind(grades_file(tmp_path, {sheet: 'PASS' for sheet in key}), key_file(tmp_path, key))
    assert result['guard'] == 'PASS'


def test_sheets_draw_the_same_ids_from_the_same_seed(tmp_path, world):
    runs, scratch = world
    for n in (1, 2, 3):
        write_w_rep(runs, n=n)
    _, first = build(tmp_path / 'a', runs, 'seed-7')
    _, second = build(tmp_path / 'b', runs, 'seed-7')
    _, other = build(tmp_path / 'c', runs, 'seed-8')
    assert first == second
    assert sorted(first) != sorted(other)
    assert len(set(first)) == 3


def test_sheets_refuse_an_existing_sheet_dir_or_key(tmp_path, world):
    runs, _ = world
    write_w_rep(runs)
    (tmp_path / 'grading' / 'sheets').mkdir(parents=True)
    with pytest.raises(SystemExit, match='refusing'):
        sheets.build(runs, tmp_path / 'grading' / 'sheets', 's')
    (tmp_path / 'other').mkdir()
    (tmp_path / 'other' / 'key.json').write_text('{}')
    with pytest.raises(SystemExit, match='refusing'):
        sheets.build(runs, tmp_path / 'other' / 'sheets', 's')
    assert not (tmp_path / 'other' / 'sheets').exists()


def test_sheets_refuse_a_sheet_dir_inside_a_repository(tmp_path, world):
    runs, _ = world
    write_w_rep(runs)
    repo = tmp_path / 'repo'
    repo.mkdir()
    subprocess.run(['git', 'init', '-q', str(repo)], check=True)
    with pytest.raises(SystemExit, match='inside a git repository'):
        sheets.build(runs, repo / 'grading' / 'sheets', 's')
    assert not (repo / 'grading').exists()


def test_sheets_refuse_an_unknown_folder_in_the_runs_root(tmp_path, world):
    runs, _ = world
    write_w_rep(runs)
    (runs / 'W9').mkdir()
    with pytest.raises(SystemExit, match='W9'):
        sheets.build(runs, tmp_path / 'grading' / 'sheets', 's')


def grades_file(tmp: Path, grades: dict[str, str]) -> Path:
    path = tmp / 'grades.tsv'
    path.write_text('id\tgrade\n' + ''.join(f'{sheet}\t{grade}\tnote\n' for sheet, grade in grades.items()))
    return path


def key_file(tmp: Path, key: dict) -> Path:
    path = tmp / 'key.json'
    path.write_text(json.dumps(key))
    return path


def test_unblind_refuses_a_missing_or_extra_grade(tmp_path):
    key = {'a1b2c3': {'case': 'W1', 'arm': 'old', 'model': SONNET, 'rep': 1, 'read': None},
           'd4e5f6': {'case': 'W1', 'arm': 'new', 'model': SONNET, 'rep': 1, 'read': None}}
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


def key_entries(case: str, arm: str, model: str, verdicts: list[tuple[str | None, str]]) -> tuple[dict, dict]:
    key, grades = {}, {}
    for n, (read, grade) in enumerate(verdicts, 1):
        sheet = hashlib.sha256(f'{case}{arm}{model}{n}'.encode()).hexdigest()[:6]
        key[sheet] = {'case': case, 'arm': arm, 'model': model, 'rep': n, 'read': read}
        grades[sheet] = grade
    return key, grades


def test_unblind_scores_t_reps_by_read_and_use(tmp_path):
    key, grades = key_entries('T2', 'old', SONNET, [('PASS', 'PASS'), ('FAIL', 'PASS'), ('PASS', 'FAIL')])
    rows = sheets.unblind(grades_file(tmp_path, grades), key_file(tmp_path, key))['rows']
    assert [(row['rep'], row['verdict']) for row in rows] == [(1, 'PASS'), (2, 'FAIL'), (3, 'FAIL')]


@pytest.mark.parametrize(('case', 'old', 'new', 'meets'), [
    ('T2', 3, 2, True), ('T2', 3, 1, False), ('T2', 0, 0, True),
    ('W1', 5, 4, True), ('W1', 4, 3, False), ('W1', 3, 5, True), ('W1', 5, 3, False),
])
def test_unblind_checks_the_bars(tmp_path, case, old, new, meets):
    read = 'PASS' if case.startswith('T') else None
    key, grades = {}, {}
    for arm, passes in (('old', old), ('new', new)):
        more_key, more_grades = key_entries(case, arm, SONNET, [(read, 'PASS')] * passes + [(read, 'FAIL')] * (5 - passes))
        key.update(more_key)
        grades.update(more_grades)
    result = sheets.unblind(grades_file(tmp_path, grades), key_file(tmp_path, key))
    [cell] = result['bars']
    assert (cell['case'], cell['model'], cell['old'], cell['new'], cell['meets']) == (case, SONNET, old, new, meets)
    assert result['guard'] == 'incomplete'


def full_run(old_passes: dict | None = None, new_passes: dict | None = None, skip: tuple | None = None
             ) -> tuple[dict, dict]:
    '''A key and grades for all 12 cells, 5 reps per arm, with the pass counts given per (case, model).'''
    key, grades = {}, {}
    for case in ('T1', 'T2', 'T3', 'W1', 'W2', 'W3'):
        read = 'PASS' if case.startswith('T') else None
        for model in (SONNET, OPUS):
            if (case, model) == skip:
                continue
            for arm, passes in (('old', old_passes or {}), ('new', new_passes or {})):
                count = passes.get((case, model), 5)
                more_key, more_grades = key_entries(case, arm, model, [(read, 'PASS')] * count
                                                    + [(read, 'FAIL')] * (5 - count))
                key.update(more_key)
                grades.update(more_grades)
    return key, grades


def test_unblind_judges_the_guard_over_all_twelve_cells(tmp_path):
    def guard(key: dict, grades: dict) -> str:
        return sheets.unblind(grades_file(tmp_path, grades), key_file(tmp_path, key))['guard']
    assert guard(*full_run()) == 'PASS'
    assert guard(*full_run(new_passes={('W3', OPUS): 3})) == 'FAIL'
    assert guard(*full_run(old_passes={('T3', SONNET): 4}, new_passes={('T3', SONNET): 2})) == 'FAIL'
    assert guard(*full_run(old_passes={('T1', SONNET): 4}, new_passes={('T1', SONNET): 3})) == 'PASS'
    assert guard(*full_run(skip=('T2', OPUS))) == 'incomplete'


def test_unblind_calls_the_guard_incomplete_without_five_and_five(tmp_path):
    key, grades = key_entries('W2', 'old', SONNET, [(None, 'PASS')] * 5)
    more_key, more_grades = key_entries('W2', 'new', SONNET, [(None, 'PASS')] * 4)
    result = sheets.unblind(grades_file(tmp_path, {**grades, **more_grades}), key_file(tmp_path, {**key, **more_key}))
    assert result['guard'] == 'incomplete'
    # All 12 cells are there and meet their bars, but one arm of one cell is a rep short.
    key, grades = full_run()
    [short] = [sheet for sheet, entry in key.items()
               if (entry['case'], entry['arm'], entry['model'], entry['rep']) == ('T3', 'new', OPUS, 5)]
    del key[short], grades[short]
    assert sheets.unblind(grades_file(tmp_path, grades), key_file(tmp_path, key))['guard'] == 'incomplete'
    # Or a rep over.
    key, grades = full_run()
    more_key, more_grades = key_entries('W1', 'old', SONNET, [(None, 'PASS')] * 6)
    key.update(more_key)
    grades.update(more_grades)
    assert sheets.unblind(grades_file(tmp_path, grades), key_file(tmp_path, key))['guard'] == 'incomplete'


def test_sheets_command_builds_and_unblinds(tmp_path, world):
    runs, scratch = world
    write_w_rep(runs, result='ACTION: read references/discovery.md\n')
    sheet_dir = tmp_path / 'grading' / 'sheets'
    env = {**os.environ, 'WSL_SCRATCH': str(scratch)}
    done = kit_tool(str(KIT / 'sheets.py'), 'build', str(runs), str(sheet_dir), 'seed-1', env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    [sheet] = sheet_dir.iterdir()
    grades = grades_file(tmp_path, {sheet.stem: 'PASS'})
    done = kit_tool(str(KIT / 'sheets.py'), 'unblind', str(grades), str(tmp_path / 'grading' / 'key.json'), env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    assert f'W1 old {SONNET} rep1: PASS' in done.stdout


# --- build_prompts.py, rep_tools.py place-copy and check-copy -----------------------------------------------

SKILL_TEXT = '---\nname: writing-skills\ndescription: Use when testing the kit\n---\n\n# Writing Skills\n\nBody.\n'


def make_repo(tmp: Path) -> tuple[Path, str]:
    repo = tmp / 'repo'
    skill = repo / 'skills' / 'writing-skills'
    (skill / 'references').mkdir(parents=True)
    (skill / 'scripts').mkdir()
    (skill / 'SKILL.md').write_text(SKILL_TEXT)
    (skill / 'persuasion-principles.md').write_text('# Persuasion\n')
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
    env = {**os.environ, 'WSL_REPO': str(repo), 'WSL_SKILL_ROOT': str(tmp_path / 'skill-root')}
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


def plan72_cases():
    spec = importlib.util.spec_from_file_location('plan72_cases', PLAN72_CASES)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('arm', ['old', 'new', 'pilot'])
def test_build_prompts_writes_six_prompts_and_the_manifest(tmp_path, repo_env, arm):
    env, root, sha = repo_env
    out = tmp_path / f'prompts-{arm}'
    done = build_prompts(env, 'HEAD', arm, str(out))
    assert done.returncode == 0, done.stdout + done.stderr
    assert sorted(p.name for p in out.iterdir()) == ['MANIFEST.txt', 'T1.txt', 'T2.txt', 'T3.txt', 'W1.txt', 'W2.txt',
                                                     'W3.txt']
    body = SKILL_TEXT.split('\n---\n', 1)[1]
    plan72 = plan72_cases()
    assert (out / 'W2.txt').read_text() == plan72.FRAME.format(body=body.strip('\n'),
                                                              conversation=plan72.CASES['W2'].strip())
    t2 = (out / 'T2.txt').read_text()
    assert f'<skill name="writing-skills">\nBase directory for this skill: {root}/writing-skills\n\n# Writing Skills' in t2
    assert cases.CASES_T['T2'].strip() in t2
    lines = manifest_lines(out)
    assert lines[:2] == [f'ref {sha}', f'arm {arm}']
    assert f'body-sha256 {sha256(body.encode())}' in lines
    assert f'skill-copy-root {root}' in lines
    copies = sorted(line.split()[1] for line in lines if line.startswith('skill-copy '))
    assert copies == ['writing-skills/SKILL.md', 'writing-skills/persuasion-principles.md',
                      'writing-skills/references/flowcharts.md', 'writing-skills/scripts/render_graphs.py']
    assert f'skill-copy writing-skills/SKILL.md {sha256(SKILL_TEXT.encode())} skills/writing-skills/SKILL.md@{sha}' in lines
    for name in ('W1.txt', 'T3.txt'):
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
        'writing-skills/SKILL.md', 'writing-skills/persuasion-principles.md', 'writing-skills/references/flowcharts.md',
        'writing-skills/scripts/render_graphs.py']
    assert os.access(root / 'writing-skills' / 'scripts' / 'render_graphs.py', os.X_OK)
    assert (root / 'writing-skills' / 'SKILL.md').read_text() == SKILL_TEXT
    done = check_copy(env, out / 'MANIFEST.txt', out / 'T1.txt')
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
    (copy / 'persuasion-principles.md').write_text('# Persuasion, edited\n')
    done = check_copy(env, manifest, prompt)
    assert done.returncode == 1 and 'skill copy file changed' in done.stdout
    (copy / 'persuasion-principles.md').unlink()
    done = check_copy(env, manifest, prompt)
    assert done.returncode == 1 and 'skill copy file missing' in done.stdout
    (copy / 'persuasion-principles.md').write_text('# Persuasion\n')
    (root / 'plan.md').write_text('a stray file beside the copy\n')
    done = check_copy(env, manifest, prompt)
    assert done.returncode == 1 and 'does not list' in done.stdout
    (root / 'plan.md').unlink()
    prompt.write_text(prompt.read_text() + 'one more line\n')
    done = check_copy(env, manifest, prompt)
    assert done.returncode == 1 and 'prompt changed' in done.stdout


def test_build_prompts_reads_this_repository(tmp_path):
    env = {**os.environ, 'WSL_SKILL_ROOT': str(tmp_path / 'skill-root')}
    env.pop('WSL_REPO', None)
    out = tmp_path / 'prompts-pilot'
    done = build_prompts(env, 'HEAD', 'pilot', str(out))
    assert done.returncode == 0, done.stdout + done.stderr
    lines = manifest_lines(out)
    copies = [line.split()[1] for line in lines if line.startswith('skill-copy ')]
    assert 'writing-skills/SKILL.md' in copies
    assert all(rel.startswith('writing-skills/') for rel in copies)
    assert '# Writing Skills' in (out / 'T1.txt').read_text()


# --- cases.py and the fixtures -----------------------------------------------------------------------------

# Each T case's marker tokens. A fixture or a case text that holds one could hand the rep its "use"
# without the moved file.
MARKER_TOKENS = {
    'T1': r'(?m)^\s*\**[A-D][).:]\s|\bChoose [A-D]\b|\b[A-D], [A-D],? (?:or|and) [A-D]\b',
    'T2': r'(?i)\b(?:authority|commitment|social proof|liking|reciprocity|scarcity|unity)\b',
    'T3': r'(?i)plaintext|octagon|```dot|digraph|\bshape\s*=',
}


def test_w_frame_and_cases_are_plan_72s_byte_for_byte():
    plan72 = plan72_cases()
    assert cases.FRAME_W == plan72.FRAME
    assert cases.CASES_W == plan72.CASES


def test_t_frame_makes_the_three_changes():
    frame = cases.FRAME_T
    assert '<skill name="writing-skills">\nBase directory for this skill: {base}\n\n{body}\n</skill>' in frame
    assert 'Read, Glob, Grep, Edit and Write' in frame and "your partner's project" in frame
    assert frame.endswith('It is your turn. Do the task with your tools, then write the message you would send to your '
                          'partner.\n')
    assert 'You have no tools' not in frame and 'ACTION:' not in frame and '~/.claude' not in frame
    plan72 = plan72_cases()
    assert frame.startswith(plan72.FRAME.split('\n', 1)[0])


def test_each_t_case_names_its_target_and_the_fixture_holds_its_project():
    assert sorted(cases.CASES_T) == sorted(cases.TARGET) == sorted(cases.MOVED) == sorted(cases.MARKER) == [
        'T1', 'T2', 'T3']
    for case, text in cases.CASES_T.items():
        assert f'`{cases.TARGET[case]}`' in text
        assert cases.MOVED[case] not in text
        repo = KIT / 'fixtures' / case / 'repo'
        assert repo.is_dir()
        assert (repo / cases.TARGET[case]).is_file() == (case != 'T1')
    assert (KIT / 'fixtures' / 'T1' / 'repo' / 'specs').is_dir()
    for name in ('pyproject.toml', 'uv.lock'):
        assert (KIT / 'fixtures' / 'T1' / 'repo' / name).is_file()
    for case, spec in (('T2', 'secrets-scan-gate-baseline.md'), ('T3', 'http-retry-policy-baseline.md')):
        assert (KIT / 'fixtures' / case / 'repo' / 'specs' / spec).is_file()


@pytest.mark.parametrize('case', ['T1', 'T2', 'T3'])
def test_fixtures_and_case_texts_hold_no_marker(case):
    import re
    token = re.compile(MARKER_TOKENS[case])
    texts = {f'CASES_T[{case}]': cases.CASES_T[case]}
    for path in sorted((KIT / 'fixtures' / case).rglob('*')):
        if path.is_file():
            texts[str(path.relative_to(KIT))] = path.read_text()
    found = {name: token.findall(text) for name, text in texts.items() if token.search(text)}
    assert found == {}


# Task 3 Step 4: no domain repeats the skill's own examples or plan 72's W cases. The lists hold distinctive
# words only, and the test reads plan 72's frozen cases.py, never the live skill, so an unrelated edit to the
# skill cannot fail it.
T_DOMAIN_WORDS = {
    'T1': ('lockfile', 'pyproject', 'uv.lock', 'tide-tables'),
    'T2': ('gitleaks', 'secrets-scan-gate'),
    'T3': ('idempotency', 'curl', 'http-retry-policy'),
}
W_DOMAIN_WORDS = ('migration', 'dry run', 'dry-run', 'cache-invalidation', 'purging', 'changelog', 'release-notes-gate')


def domain_hits(word: str, text: str) -> int:
    return len(re.findall(rf'\b{re.escape(word.casefold())}\b', text.casefold()))


@pytest.mark.parametrize('case', ['T1', 'T2', 'T3'])
def test_no_t_domain_repeats_plan_72s_cases(case):
    plan72 = PLAN72_CASES.read_text()
    text = cases.CASES_T[case] + ''.join(
        path.read_text() for path in sorted((KIT / 'fixtures' / case).rglob('*')) if path.is_file())
    for word in T_DOMAIN_WORDS[case]:
        assert domain_hits(word, plan72) == 0, word
        assert domain_hits(word, text) > 0, word
    assert all(domain_hits(word, plan72) for word in W_DOMAIN_WORDS)
    assert {word: domain_hits(word, text) for word in W_DOMAIN_WORDS if domain_hits(word, text)} == {}


# The domains of the skill's own worked examples. Chosen once, on 2026-11-22 at commit 8619445, from
# skills/writing-skills/SKILL.md (lines 79, 82, 178, 233 and 425), references/discovery.md (lines 86-121,
# 170-175 and 194-200) and testing-skills-with-subagents.md (line 167). Frozen here, so this test never reads the
# live skill. Distinctive terms only: generic words such as `timeout` or `production` are left out.
SKILL_EXAMPLE_WORDS = (
    'condition-based', 'root-cause', 'flatten-with-flags', 'test-invariants', 'defensive-programming', 'flaky',
    'async-test-helpers', 'race condition', 'race conditions', 'setTimeout', 'React Router', 'ENOTEMPTY',
    'payment-system', 'debugging-with-logs', 'data-structure-refactoring',
)


@pytest.mark.parametrize('case', ['T1', 'T2', 'T3'])
def test_no_t_domain_repeats_the_skills_own_examples(case):
    texts = {f'CASES_T[{case}]': cases.CASES_T[case]}
    for path in sorted((KIT / 'fixtures' / case).rglob('*')):
        if path.is_file():
            texts[str(path.relative_to(KIT))] = path.read_text()
    found = {(name, word) for name, text in texts.items() for word in SKILL_EXAMPLE_WORDS if domain_hits(word, text)}
    assert found == set()


def test_every_case_has_its_pass_and_fail_columns():
    assert sorted(cases.COLUMNS) == ['T1', 'T2', 'T3', 'W1', 'W2', 'W3']
    for case, (pass_line, fail_line) in cases.COLUMNS.items():
        assert pass_line and fail_line
    for case in ('W1', 'W2', 'W3'):
        target, reference = cases.W_TARGET[case], cases.W_REFERENCE[case]
        assert f'`{target}`' in cases.COLUMNS[case][0]
        assert f'`<skill>/{reference.rsplit("/", 1)[-1]}`' in cases.COLUMNS[case][0]
