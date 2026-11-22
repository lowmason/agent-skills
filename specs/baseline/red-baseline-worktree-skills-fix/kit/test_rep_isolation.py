'''Tests for how run_reps.sh and probe.sh start `claude`, with a stub that records what it is given.

The brief (Task 1, Global Constraints, Micro-tests): "Each rep is a fresh `claude -p --model <model>
--tools "" --strict-mcp-config --setting-sources ""` under `env -i`, with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`
and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, a $0.50 cap, and its own new, empty folder outside every
repository." Without `env -i` the desktop app's messaging socket reaches the rep, and that is how a
peer turn arrives (the cause that Next-kit fixes voids). The stub in test_run_reps.py ignores its
arguments, its environment and its folder. This stub writes each of them to a file for the test to read.

The probe is checked against the same expectations: probe.sh must start `claude` the way a rep starts.
'''
import os
import subprocess
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parent
RUN_REPS = KIT / 'run_reps.sh'
PROBE = KIT / 'probe.sh'
KEEP = ('HOME', 'USER', 'LOGNAME', 'PATH', 'SHELL', 'TMPDIR', 'LANG')
DISABLE = ('CLAUDE_CODE_DISABLE_ADVISOR_TOOL', 'CLAUDE_CODE_DISABLE_AUTO_MEMORY')
SHELL_ADDED = {'PWD', 'SHLVL', '_', 'OLDPWD'}
SENTINELS = {'FAKE_PEER_SOCKET': '/tmp/peer.sock', 'CLAUDE_CODE_SESSION_ID': 'abc-123',
             'CLAUDE_CODE_ENTRYPOINT': 'desktop', 'ANTHROPIC_API_KEY': 'sk-not-real', 'LLM_WIKI_ROOT': '/wiki'}
FLAGS = ['-p', '--model', 'claude-sonnet-5-5', '--tools', '', '--strict-mcp-config', '--setting-sources', '',
         '--disable-slash-commands', '--no-session-persistence', '--output-format', 'json']
STUB = r'''#!/bin/bash
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
REPLY = '{"result": "ok", "result_index": 0, "origin": null}'


class Call:
    def __init__(self, stem: str) -> None:
        self.argv = Path(f'{stem}.argv').read_bytes().decode().split('\0')[:-1]
        self.env = dict(line.split('=', 1) for line in Path(f'{stem}.env').read_text().splitlines() if '=' in line)
        self.stdin = Path(f'{stem}.stdin').read_text()
        self.cwd = Path(f'{stem}.cwd').read_text().strip()
        self.listing = Path(f'{stem}.ls').read_text().split()
        self.git = Path(f'{stem}.git').read_text()


class World:
    def __init__(self, tmp: Path) -> None:
        self.tmp = tmp
        self.stub_dir = tmp / 'stub'
        self.stub_dir.mkdir()
        stub = self.stub_dir / 'claude'
        stub.write_text(STUB.replace('@DIR@', str(self.stub_dir)))
        stub.chmod(0o755)
        (self.stub_dir / 'reply.json').write_text(REPLY)
        self.prompt = tmp / 'prompt.txt'
        self.prompt.write_text('a prompt, line one\nline two\n')
        self.out = tmp / 'runs' / 'case-control'
        self.scratch_root = tmp / 'scratch'
        # The caller's environment: LANG and LOGNAME are left out, and every other KEEP variable that
        # this process has is passed. The planted variables must not reach a rep.
        self.env = {v: os.environ[v] for v in KEEP if v in os.environ and v not in ('LANG', 'LOGNAME')}
        self.env['PATH'] = f'{self.stub_dir}:{os.environ["PATH"]}'
        self.env.update(SENTINELS)
        self.env.update({v: '0' for v in DISABLE})
        self.env['KIT_SCRATCH_ROOT'] = str(self.scratch_root)

    def run_reps(self, first: int, last: int, *budget: str) -> subprocess.CompletedProcess:
        return subprocess.run(['bash', str(RUN_REPS), str(self.prompt), str(self.out), str(first), str(last),
                               'claude-sonnet-5-5', *budget], capture_output=True, text=True, env=self.env, cwd=KIT)

    def run_probe(self, *prompt: str) -> subprocess.CompletedProcess:
        return subprocess.run(['bash', str(PROBE), str(self.tmp / 'probe' / 'probe.json'), *prompt],
                              capture_output=True, text=True, env=self.env, cwd=KIT)

    def calls(self) -> list[Call]:
        return [Call(str(path)[:-len('.argv')]) for path in sorted(self.stub_dir.glob('call.*.argv'))]


@pytest.fixture
def world(tmp_path: Path) -> World:
    return World(tmp_path)


def started(world: World, via: str, last: int = 1, budget: tuple[str, ...] = ()) -> list[Call]:
    run = world.run_reps(1, last, *budget) if via == 'run_reps' else world.run_probe()
    assert run.returncode == 0, run.stdout + run.stderr
    return world.calls()


@pytest.mark.parametrize('via', ['run_reps', 'probe'])
def test_claude_starts_with_exactly_the_isolation_flags_and_the_default_cap(world, via):
    [call] = started(world, via)
    assert call.argv == [*FLAGS, '--max-budget-usd', '0.50']


def test_an_explicit_budget_replaces_the_default_cap(world):
    [call] = started(world, 'run_reps', budget=('0.25',))
    assert call.argv[-2:] == ['--max-budget-usd', '0.25']
    assert call.argv[:-2] == FLAGS


def test_the_prompt_file_arrives_on_stdin_of_a_rep(world):
    [call] = started(world, 'run_reps')
    assert call.stdin == 'a prompt, line one\nline two\n'


def test_the_probe_sends_isolation_probe_txt_on_stdin(world):
    [call] = started(world, 'probe')
    assert call.stdin == (KIT / 'isolation_probe.txt').read_text()


@pytest.mark.parametrize('via', ['run_reps', 'probe'])
def test_only_the_kept_variables_and_the_two_disable_variables_reach_the_rep(world, via):
    [call] = started(world, via)
    expected = {v: world.env[v] for v in KEEP if v in world.env}
    assert 'LANG' not in call.env and 'LOGNAME' not in call.env
    assert {k: call.env[k] for k in call.env if k in KEEP} == expected
    assert call.env['CLAUDE_CODE_DISABLE_ADVISOR_TOOL'] == '1'
    assert call.env['CLAUDE_CODE_DISABLE_AUTO_MEMORY'] == '1'
    assert set(call.env) <= set(KEEP) | set(DISABLE) | SHELL_ADDED
    assert not (set(SENTINELS) & set(call.env))


@pytest.mark.parametrize('via', ['run_reps', 'probe'])
def test_the_rep_starts_in_a_new_empty_folder_outside_every_repository(world, via):
    [call] = started(world, via)
    assert call.cwd.startswith(('/tmp/mt-wsf-', '/private/tmp/mt-wsf-'))
    assert call.listing == []
    assert call.git.splitlines()[-1] == 'exit 128'
    assert not Path(call.cwd).is_relative_to(KIT)


def test_two_reps_start_in_two_different_folders(world):
    calls = started(world, 'run_reps', last=2)
    assert len(calls) == 2
    assert calls[0].cwd != calls[1].cwd
    assert all(call.listing == [] for call in calls)
