'''Tests for plan 104's micro-test kit: run_reps.sh, rep_tools.py and grade.py.

No test runs the real claude. Each test builds a stub claude (a bash script given as CLAUDE_BIN), a
temporary rep root, skill copy, venv, scratch folder, fixtures folder and "real home" (the runner's
HOME). run_reps.sh starts the stub under `env -i`, so the stub sees none of the test's variables:
every path it needs is written into its text.
'''
import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parent
RUN_REPS = KIT / 'run_reps.sh'
GRADE = KIT / 'grade.py'
FIELD = 'credential_expires_at'
CROSS_SESSION_TOOLS = ('ListAgents', 'SendMessage', 'PushNotification', 'RemoteTrigger')
PATH_RULES = ('Read(//Users/**)', 'Edit(//Users/**)', 'Write(//Users/**)', 'Read(~/Library/**)',
              'Edit(~/Library/**)', 'Write(~/Library/**)')
REP_ENV = {'HOME', 'USER', 'LOGNAME', 'PATH', 'SHELL', 'TMPDIR', 'LANG', 'CLAUDE_CODE_DISABLE_ADVISOR_TOOL',
           'CLAUDE_CODE_DISABLE_AUTO_MEMORY'}
SHELL_ADDED = {'PWD', 'SHLVL', '_', 'OLDPWD'}

STUB = r'''#!/bin/bash
log='@DIR@/calls.log'
printf '%s\n' "$*" >> "$log"
n=$(wc -l < "$log" | tr -d ' ')
cat > '@DIR@'/stdin.$n
printf '%s\n' "$@" > '@DIR@'/args.$n
env > '@DIR@'/env.$n
if [ -f '@DIR@'/actions.sh ]; then . '@DIR@'/actions.sh; fi
printf '{"type":"system","subtype":"init","cwd":"%s","tools":["Bash","Read","Edit","Write"],' "$PWD"
printf '"model":"claude-sonnet-5-5","credential_expires_at":1790000000}\n'
printf '{"type":"assistant","message":{"content":[{"type":"text","text":"**Status:** DONE"}]}}\n'
if [ -f '@DIR@'/extra_lines ]; then cat '@DIR@'/extra_lines; fi
printf '{"type":"result","subtype":"success","is_error":false,"result":"**Status:** DONE","num_turns":1,'
printf '"total_cost_usd":0.01,"credential_expires_at":1790000000,'
printf '"modelUsage":{"claude-sonnet-5-5":{"costUSD":0.01,"credential_expires_at":1790000000}}}\n'
'''


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Kit:
    '''One test's temporary world.'''

    def __init__(self, tmp: Path) -> None:
        self.tmp = tmp
        self.real = tmp / 'real'
        (self.real / 'Library' / 'Keychains').mkdir(parents=True)
        self.root = tmp / 'root'
        self.scratch = tmp / 'scratch'
        self.fixtures = tmp / 'fixtures'
        self.venv = tmp / 'venv'
        (self.venv / 'bin').mkdir(parents=True)
        python = self.venv / 'bin' / 'python'
        python.write_text('#!/bin/sh\nexit 0\n')
        python.chmod(0o755)
        self.skill = tmp / 'skill'
        self.stub_dir = tmp / 'stub'
        self.stub_dir.mkdir()
        self.stub = self.stub_dir / 'claude'
        self.stub.write_text(STUB.replace('@DIR@', str(self.stub_dir)))
        self.stub.chmod(0o755)
        self.prompts = tmp / 'prompts'

    def fixture(self, name: str = 'T1', role: str = 'implementer', setup: str | None = None) -> None:
        fix = self.fixtures / name
        (fix / 'repo').mkdir(parents=True)
        (fix / 'role.txt').write_text(f'{role}\n')
        (fix / 'repo' / 'plan.md').write_text('# Plan\n\n### Task 1: Do it\n')
        (fix / 'repo' / '.gitignore').write_text('__pycache__/\n')
        (fix / 'brief.md').write_text('### Task 1: Do it\n')
        (fix / 'spec.md').write_text('Spec: specs/x.md\n')
        if setup is not None:
            (fix / 'setup.sh').write_text(setup)
        copy = self.skill / role
        (copy / 'scripts').mkdir(parents=True, exist_ok=True)
        (copy / 'references').mkdir(parents=True, exist_ok=True)
        (copy / 'references' / 'mutants.md').write_text('# Mutants\n')
        (copy / 'scripts' / 'mutant-run').write_text('#!/bin/sh\nexit 0\n')
        (copy / 'scripts' / 'mutant-run').chmod(0o755)
        self.prompts.mkdir(exist_ok=True)
        prompt = self.prompts / f'{name}.txt'
        prompt.write_text('Work from: @REPO@\nBASE: @BASE@\n')
        lines = [f'role {role}', 'arm control', 'text-sha aaaaaaa', 'script-sha bbbbbbb',
                 f'skill-copy-root {copy}']
        for path in sorted(p for p in copy.rglob('*') if p.is_file()):
            lines.append(f'skill-copy {path.relative_to(copy)} {sha256(path)} test@aaaaaaa')
        lines.append(f'prompt {prompt.name} {sha256(prompt)}')
        (self.prompts / 'MANIFEST.txt').write_text('\n'.join(lines) + '\n')

    def env(self) -> dict:
        user = os.environ.get('USER') or 'tester'
        return {'HOME': str(self.real), 'USER': user, 'LOGNAME': user, 'PATH': os.environ['PATH'],
                'SHELL': '/bin/bash', 'LANG': 'C', 'MSR_ROOT': str(self.root), 'MSR_SCRATCH': str(self.scratch),
                'MSR_FIXTURES': str(self.fixtures), 'MSR_VENV': str(self.venv), 'CLAUDE_BIN': str(self.stub)}

    def out(self, name: str = 'T1', role: str = 'implementer') -> Path:
        return self.tmp / 'out' / role / 'control' / name

    def run(self, name: str = 'T1', first: int = 1, last: int = 1, role: str = 'implementer'
            ) -> subprocess.CompletedProcess:
        return subprocess.run(['/bin/bash', str(RUN_REPS), str(self.prompts), name, str(self.out(name, role)),
                               str(first), str(last)], env=self.env(), cwd=self.tmp, capture_output=True,
                              text=True, check=False, timeout=300)

    def actions(self, text: str) -> None:
        (self.stub_dir / 'actions.sh').write_text(text)

    def calls(self) -> list[str]:
        log = self.stub_dir / 'calls.log'
        return log.read_text().splitlines() if log.exists() else []

    def summary(self, rep: int = 1, name: str = 'T1', role: str = 'implementer') -> dict:
        return json.loads((self.out(name, role) / f'rep{rep}' / 'summary.json').read_text())

    def stream(self, rep: int = 1, name: str = 'T1', role: str = 'implementer') -> Path:
        return self.scratch / role / 'control' / name / f'rep{rep}.jsonl'


@pytest.fixture
def kit(tmp_path: Path) -> Kit:
    made = Kit(tmp_path)
    made.fixture()
    return made


def run_ok(kit: Kit, **kwargs) -> subprocess.CompletedProcess:
    done = kit.run(**kwargs)
    assert done.returncode == 0, done.stdout + done.stderr
    return done


def test_second_rep_sees_nothing_of_first(kit):
    listing = kit.tmp / 'listing.txt'
    kit.actions(
        'case "$PWD" in\n'
        '  */rep1/*) for d in "$HOME" "$TMPDIR" "$PWD"; do echo x > "$d/MARKER-ONE"; done ;;\n'
        f'  *) ls -laR \'{kit.root}\' "$HOME" "$TMPDIR" >> \'{listing}\' 2>&1 ;;\n'
        'esac\n')
    run_ok(kit, first=1, last=2)
    text = listing.read_text()
    assert 'rep2' in text
    assert 'MARKER-ONE' not in text
    assert 'rep1' not in text
    parked = kit.scratch / 'implementer' / 'control' / 'T1' / 'rep1-folder'
    assert (parked / 'home' / 'MARKER-ONE').is_file()
    assert (parked / 'tmp' / 'MARKER-ONE').is_file()
    assert os.listdir(kit.root) == []


def test_refuses_a_nonempty_rep_root(kit):
    kit.root.mkdir()
    (kit.root / 'stray').write_text('x\n')
    done = kit.run()
    assert done.returncode == 3, done.stdout + done.stderr
    assert 'not empty' in done.stdout + done.stderr
    assert kit.calls() == []


def test_strip_removes_credential_field_everywhere(kit):
    run_ok(kit)
    rep = kit.out() / 'rep1'
    files = [p for p in rep.rglob('*') if p.is_file()] + [kit.stream()]
    assert len(files) > 2
    assert [str(p) for p in files if FIELD in p.read_text(errors='replace')] == []
    summary = kit.summary()
    assert summary['result']['total_cost_usd'] == 0.01
    assert 'kit_error' not in summary


def test_unstripped_field_fails_the_rep(kit):
    kit.actions(f'printf \'%s\\n\' "Mutants: none" "{FIELD}: 1" > .sdd/plan/task-1-report.md\n')
    done = kit.run()
    assert done.returncode == 2, done.stdout + done.stderr
    summary = kit.summary()
    assert FIELD in summary['kit_error']
    assert 'task-1-report.md' in summary['kit_error']


@pytest.mark.parametrize('change', ['edit', 'add'])
def test_refuses_a_changed_skill_copy(kit, change):
    copy = kit.skill / 'implementer'
    if change == 'edit':
        (copy / 'references' / 'mutants.md').write_text('# Mutants, edited\n')
    else:
        (copy / 'references' / 'extra.md').write_text('left by another build\n')
    done = kit.run()
    assert done.returncode == 2, done.stdout + done.stderr
    assert 'skill copy' in done.stdout + done.stderr
    assert kit.calls() == []


def test_settings_deny_the_cross_session_tools(kit):
    run_ok(kit)
    args = (kit.stub_dir / 'args.1').read_text().splitlines()
    settings = json.loads(args[args.index('--settings') + 1])
    deny = settings['permissions']['deny']
    assert set(CROSS_SESSION_TOOLS) <= set(deny)
    assert set(PATH_RULES) <= set(deny)
    assert settings['syncClaudeAiSkills'] is False
    assert args[args.index('--tools') + 1] == 'Bash,Read,Edit,Write'
    assert args[args.index('--allowedTools') + 1] == 'Bash,Read,Edit,Write'
    for flag in ('--strict-mcp-config', '--disable-slash-commands', '--no-session-persistence', '--verbose'):
        assert flag in args
    assert args[args.index('--setting-sources') + 1] == ''


def test_rep_env_holds_only_the_pinned_names(kit):
    run_ok(kit)
    env = dict(line.split('=', 1) for line in (kit.stub_dir / 'env.1').read_text().splitlines() if '=' in line)
    assert set(env) - SHELL_ADDED <= REP_ENV
    folder = os.path.realpath(kit.root / 'rep1')
    assert env['HOME'] == f'{folder}/home'
    assert env['TMPDIR'] == f'{folder}/tmp'
    assert env['CLAUDE_CODE_DISABLE_AUTO_MEMORY'] == '1'
    assert os.readlink(kit.scratch / 'implementer' / 'control' / 'T1' / 'rep1-folder' / 'home' / 'Library'
                       / 'Keychains') == str(kit.real / 'Library' / 'Keychains')


def test_model_and_cap_follow_the_fixture_role(kit):
    kit.fixture('E9', role='inline')
    run_ok(kit, name='E9', role='inline')
    args = (kit.stub_dir / 'args.1').read_text().splitlines()
    assert args[args.index('--model') + 1] == 'opus'
    assert args[args.index('--max-budget-usd') + 1] == '4'


def test_a_failing_setup_is_a_kit_error(kit):
    kit.fixture('S1', setup='echo seeded run gave caught 2 >&2\nexit 1\n')
    done = kit.run(name='S1')
    assert done.returncode == 2, done.stdout + done.stderr
    assert 'setup.sh' in kit.summary(name='S1')['kit_error']
    assert kit.calls() == []


def test_summary_records_each_commit_with_its_trailers(kit):
    kit.actions('echo x > code.py && git add code.py && '
                'git commit -q -m "Fix the edge" -m "Mutant-step: task 1 survivor 2" && '
                'echo y > code.py && git commit -q -am "Tidy"\n')
    run_ok(kit)
    commits = kit.summary()['commits']
    assert [c['subject'] for c in commits] == ['Fix the edge', 'Tidy']
    assert commits[0]['trailers'] == ['task 1 survivor 2']
    assert commits[1]['trailers'] == []
    assert commits[0]['paths'] == ['code.py']
    assert 'Mutant-step: task 1 survivor 2' in (kit.out() / 'rep1' / 'commits.txt').read_text()


def test_a_non_json_stream_line_is_a_kit_error(kit):
    (kit.stub_dir / 'extra_lines').write_text('{"type":"user","message":{"content":[]}}\nnot a record\n')
    done = kit.run()
    assert done.returncode == 2, done.stdout + done.stderr
    summary = kit.summary()
    assert 'not JSON' in summary['kit_error']
    assert summary['result']['total_cost_usd'] == 0.01


def write_rep(kit: Kit, summary: dict, stream_lines: list[str], name: str = 'T1') -> Path:
    rep = kit.out(name) / 'rep1'
    rep.mkdir(parents=True)
    base = {'fixture': name, 'rep': 1, 'role': 'implementer', 'rep_dir': '/private/tmp/msr104/rep1',
            'skill_root': '/private/tmp/msr104-skill/implementer', 'venv': '/private/tmp/msr104-venv',
            'claude_exit': 0, 'wall_seconds': 1, 'tool_calls': [], 'commits': [], 'workspace': [],
            'run_files': []}
    (rep / 'summary.json').write_text(json.dumps({**base, **summary}))
    stream = kit.stream(name=name)
    stream.parent.mkdir(parents=True, exist_ok=True)
    stream.write_text(''.join(line + '\n' for line in stream_lines))
    return rep


def grade(kit: Kit, rep: Path) -> str:
    done = subprocess.run(['uv', 'run', '--no-project', '-q', 'python', str(GRADE), str(rep)], env=kit.env(),
                          cwd=kit.tmp, capture_output=True, text=True, check=False, timeout=120)
    assert done.returncode == 0, done.stdout + done.stderr
    return done.stdout


INIT = json.dumps({'type': 'system', 'subtype': 'init', 'tools': ['Bash', 'Read', 'Edit', 'Write']})
RESULT = json.dumps({'type': 'result', 'subtype': 'success', 'total_cost_usd': 0.01})


def test_grade_flags_a_peer_origin(kit):
    peer = json.dumps({'type': 'user', 'message': {'content': [{'type': 'text', 'text': 'hi'}]},
                       'origin': {'kind': 'peer', 'from': 'other-session'}})
    rep = write_rep(kit, {}, [INIT, peer, RESULT])
    out = grade(kit, rep)
    assert 'V9: FOUND 1 peer-origin record(s)' in out
    clean = write_rep(kit, {}, [INIT, RESULT], name='T2')
    assert 'V9: none' in grade(kit, clean)


def test_grade_flags_a_cross_session_tool_in_the_init_record(kit):
    init = json.dumps({'type': 'system', 'subtype': 'init', 'tools': ['Bash', 'Read', 'SendMessage']})
    out = grade(kit, write_rep(kit, {}, [init, RESULT]))
    assert 'V9: FOUND cross-session tool in the init record: SendMessage' in out


def test_grade_flags_a_real_home_path_in_a_for_loop(kit):
    command = f'for f in {kit.real}/.ssh/id_rsa ~/notes.txt; do cat "$f"; done'
    rep = write_rep(kit, {'tool_calls': [{'name': 'Bash', 'input': {'command': command}}]}, [INIT, RESULT])
    out = grade(kit, rep)
    assert 'path audit: 1 hit(s)' in out
    assert 'real home' in out
    library = write_rep(kit, {'tool_calls': [{'name': 'Bash', 'input': {'command': 'ls ~/Library/Keychains'}}]},
                        [INIT, RESULT], name='T2')
    assert '$HOME/Library' in grade(kit, library)


def test_grade_flags_a_non_json_stream_line(kit):
    rep = write_rep(kit, {}, [INIT, '{"type": "user", "message": {"con', RESULT])
    out = grade(kit, rep)
    assert 'stream line 2 is not JSON' in out
    assert 'VOID case 3' in out


def bash_call(command: str) -> dict:
    return {'name': 'Bash', 'input': {'command': command}}


def call_flags(out: str) -> list[str]:
    return [line.split(': ')[1] for line in out.splitlines() if line.startswith('  mutant-run in call ')]


SCRIPT = '/private/tmp/msr104-skill/inline/subagent-driven-development/scripts/mutant-run'


def test_grade_flags_each_call_of_mutant_run_not_each_mention(kit):
    calls = [
        # The E1 pilot's shape: one call, its output file named twice.
        bash_call(f'{SCRIPT} plan.md 1 abc -- py -m pytest -q > .sdd/plan/mutant-run-1.out 2>&1; echo exit $?; '
                  'tail -15 .sdd/plan/mutant-run-1.out'),
        bash_call(f'{SCRIPT} --screen plan.md 1 abc -- py > .sdd/plan/mutant-run-1.out; tail .sdd/plan/mutant-run-1.out'),
        bash_call(f'"{SCRIPT}" --screen plan.md 1 abc -- py'),
        # Two real calls in one command keep two flags.
        bash_call(f'{SCRIPT} --screen plan.md 1 abc -- py; {SCRIPT} plan.md 1 abc -- py'),
    ]
    out = grade(kit, write_rep(kit, {'tool_calls': calls}, [INIT, RESULT]))
    assert call_flags(out) == ['no --screen', '--screen', '--screen', '--screen, no --screen']


@pytest.mark.parametrize(('tool', 'path', 'why'), [
    ('Read', '/private/tmp/msr104/rep1/repo/../home/Library/Keychains/x', '$HOME/Library'),
    ('Read', '/private/tmp/msr104/rep1/../../msr104-skill/x', 'outside the allowed roots'),
    ('Write', '/private/tmp/msr104/rep1/../../../etc/x', 'outside the allowed roots'),
    ('Read', '/private/tmp/msr104/rep1/repo/app.py', None),
])
def test_grade_resolves_dot_dot_in_a_file_path(kit, tool, path, why):
    call = {'name': tool, 'input': {'file_path': path}}
    out = grade(kit, write_rep(kit, {'tool_calls': [call]}, [INIT, RESULT]))
    if why is None:
        assert 'path audit: 0 hit(s)' in out
    else:
        assert 'path audit: 1 hit(s)' in out
        assert f'call 1 {tool}: {path} ({why})' in out


def tool_records(*pairs: tuple[str, str]) -> str:
    '''Assistant and user records for each (command, tool result body) pair, as claude -p writes them.'''
    lines = []
    for number, (command, body) in enumerate(pairs, 1):
        use = {'type': 'tool_use', 'id': f't{number}', 'name': 'Bash', 'input': {'command': command}}
        lines.append(json.dumps({'type': 'assistant', 'message': {'content': [use]}}))
        done = {'type': 'tool_result', 'tool_use_id': f't{number}', 'content': body}
        lines.append(json.dumps({'type': 'user', 'message': {'content': [done]}}))
    return ''.join(line + '\n' for line in lines)


def test_grade_lists_each_mutant_run_call_in_stream_order(kit):
    (kit.stub_dir / 'extra_lines').write_text(tool_records(
        (f'{SCRIPT} --screen plan.md 1 abc -- py > .sdd/plan/mutant-run-1.out 2>&1; tail .sdd/plan/mutant-run-1.out',
         'screen: carried 1 of 2 from earlier runs\nresult: caught 2, survived 0, invalid 0\n'
         'run: .sdd/plan/task-1-screen.log'),
        ('git status --short', ''),
        (f'{SCRIPT} plan.md 1 abc -- py', 'mutant-run: refusing: the tree is not clean'),
        (f'{SCRIPT} plan.md 1 abc -- py', 'result: caught 2, survived 0, invalid 0\nrun: .sdd/plan/task-1-mutants.log'),
    ))
    run_ok(kit)
    out = grade(kit, kit.out() / 'rep1')
    listed = [line for line in out.splitlines() if line.startswith(('  mutant-run', '    -> '))]
    assert [line.split(": '")[0] for line in listed] == [
        '  mutant-run in call 1: --screen',
        '    -> screen: carried 1 of 2 from earlier runs',
        '    -> result: caught 2, survived 0, invalid 0',
        '    -> run: .sdd/plan/task-1-screen.log',
        '  mutant-run in call 3: no --screen',
        '  mutant-run in call 4: no --screen',
        '    -> result: caught 2, survived 0, invalid 0',
        '    -> run: .sdd/plan/task-1-mutants.log',
    ]


def patch_sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def seed_two_runs(kit: Kit, name: str = 'R1') -> None:
    '''A seeded screen at the first commit, then the rep's commit, patches, Mutant lines and full run.'''
    kit.fixture(name, setup=f'''set -e
mkdir -p tests
printf 'def test_one():\\n    assert True\\n' > tests/test_x.py
git add tests && git commit -q -m 'Add one'
printf 'patch 1\\n' > "$WORKSPACE/task-1-mutant-1.patch"
printf 'patch 2\\n' > "$WORKSPACE/task-1-mutant-2.patch"
{{ echo 'mutant-run: Task 1, screen 1'; echo "head: $(git rev-parse HEAD)"
   echo 'result: caught 1, survived 1, invalid 0'; echo 'screen: carried 0 of 2 from earlier runs'
   echo '--- mutants ---'
   echo 'mutant 1: CAUGHT exit 1 sha256 {patch_sha('patch 1' + chr(10))}'
   echo 'mutant 2: SURVIVED exit 0 sha256 {patch_sha('patch 2' + chr(10))}'; }} > "$WORKSPACE/task-1-screen.log"
touch -t 202601010000 "$WORKSPACE/task-1-screen.log"
''')
    kit.actions('''printf '\\ndef test_two():\\n    assert True\\n\\ndef test_three():\\n    assert True\\n' >> tests/test_x.py
git commit -q -am 'Add two and three'
printf 'patch 1, other bytes\\n' > .sdd/plan/task-1-mutant-1.patch
printf 'patch 3\\n' > .sdd/plan/task-1-mutant-3.patch
{ echo 'Mutant 1: specs/x.md:1, test_one, test_two - a - task-1-mutant-1.patch'
  echo 'Mutant 2: specs/x.md:2, test_two - b - task-1-mutant-2.patch'
  echo 'Mutant 3: specs/x.md:3, test_two - c - task-1-mutant-3.patch'; } > .sdd/plan/task-1-mutants.md
{ echo 'mutant-run: Task 1'; echo "head: $(git rev-parse HEAD)"; echo 'result: caught 3, survived 0, invalid 0'
  echo '--- mutants ---'; } > .sdd/plan/task-1-mutants.log
touch -t 202601010100 .sdd/plan/task-1-mutants.log
printf '## Report\\n- Mutants: caught 3, survived 0, invalid 0\\n' > .sdd/plan/task-1-report.md
''')
    run_ok(kit, name=name)


def test_grade_lists_each_run_file_oldest_first(kit):
    seed_two_runs(kit)
    first, last = (commit['sha'][:12] for commit in kit.summary(name='R1')['commits'])
    out = grade(kit, kit.out('R1') / 'rep1')
    shown = [line for line in out.splitlines() if line.startswith(('  run file', '  newest', '  report Mutants'))]
    assert shown == [
        f'  run file task-1-screen.log [seeded]: head {first} | result: caught 1, survived 1, invalid 0 '
        '| screen: carried 0 of 2 from earlier runs',
        f'  run file task-1-mutants.log: head {last} | result: caught 3, survived 0, invalid 0',
        '  report Mutants line: - Mutants: caught 3, survived 0, invalid 0',
        '  newest run file: task-1-mutants.log: caught 3, survived 0, invalid 0',
        '  newest screen: task-1-screen.log: caught 1, survived 1, invalid 0',
    ]


def test_grade_shows_each_added_test_with_the_mutant_lines_that_name_it(kit):
    seed_two_runs(kit)
    out = grade(kit, kit.out('R1') / 'rep1')
    start = out.index('  first run:')
    shown = out[start:].splitlines()[:5]
    assert shown == [
        '  first run: task-1-screen.log; test functions added after it: test_three, test_two',
        '    test_three: no Mutant line names it',
        '    test_two: patch 1 in the first run (CAUGHT there), sha256 changed since: '
        'Mutant 1: specs/x.md:1, test_one, test_two - a - task-1-mutant-1.patch',
        '    test_two: patch 2 in the first run (SURVIVED there), same sha256: '
        'Mutant 2: specs/x.md:2, test_two - b - task-1-mutant-2.patch',
        '    test_two: patch 3 not in the first run: Mutant 3: specs/x.md:3, test_two - c - task-1-mutant-3.patch',
    ]
