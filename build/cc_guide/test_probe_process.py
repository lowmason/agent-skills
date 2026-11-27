'''Tests for probe_process.py: the environment a probe run starts from, and a run in its own
process group that a timeout or a stop signal ends whole (drift spec R10.4). Every
command here is a shell stub, so no test spends a token.'''
import contextlib
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

import probe_process
from test_probes import executable, written


# Prints the effort override, or "unset", then the variable its invocation adds.
ENV_ECHO = '#!/bin/sh\nprintf "%s %s" "${CLAUDE_CODE_EFFORT_LEVEL-unset}" "${PROBE_ADDED-unset}"\n'


def test_a_run_never_inherits_the_effort_override(tmp_path, monkeypatch):
    '''CLAUDE_CODE_EFFORT_LEVEL outranks an agent's effort field
    (subagents.frontmatter), so one set in the caller's shell would decide
    the effort that agent-model-pins reads. A run goes without it, and still
    gets what its invocation adds.'''
    monkeypatch.setenv('CLAUDE_CODE_EFFORT_LEVEL', 'low')
    inv = probe_process.Invocation('echo', [str(executable(tmp_path / 'echo', ENV_ECHO))], {'PROBE_ADDED': 'yes'}, 30)
    assert probe_process.execute(inv, tmp_path, tmp_path / 'echo.out', tmp_path / 'echo.err') == 0
    assert (tmp_path / 'echo.out').read_text(encoding='utf-8') == 'unset yes'


def test_a_run_keeps_an_inherited_alias_remap(tmp_path, monkeypatch):
    '''Owner ruling, 2026-10-31: record a remap, never scrub it. On Bedrock, Google Cloud or Foundry it can be the
    owner's own setup, so the probe tests the model the owner runs.'''
    monkeypatch.setenv('ANTHROPIC_DEFAULT_HAIKU_MODEL', 'a-model')
    echo = executable(tmp_path / 'echo', '#!/bin/sh\nprintf "%s" "${ANTHROPIC_DEFAULT_HAIKU_MODEL-unset}"\n')
    inv = probe_process.Invocation('echo', [str(echo)], {}, 30)
    assert probe_process.execute(inv, tmp_path, tmp_path / 'echo.out', tmp_path / 'echo.err') == 0
    assert (tmp_path / 'echo.out').read_text(encoding='utf-8') == 'a-model'
    assert not set(probe_process.ALIAS_REMAPS) & probe_process.SCRUBBED_ENV


# A run whose leader starts a child, as Gate B's bash starts claude. It writes "<leader> <child>" to $1.
SLOW = '#!/bin/sh\nsleep 300 &\necho "$$ $!" > "$1"\nsleep 300\n'
# The same, but the leader and its child ignore SIGTERM, as a stuck claude might, so only SIGKILL ends them.
STUBBORN = "#!/bin/sh\ntrap '' TERM\nsleep 300 &\necho \"$$ $!\" > \"$1\"\nwait\n"


def gone(pid: int, wait: float = 5) -> bool:
    '''Whether the process ends within `wait` seconds.'''
    deadline = time.monotonic() + wait
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(0.05)
    return False


@pytest.fixture
def pids(tmp_path):
    '''The pid file a SLOW or STUBBORN run writes. Teardown kills what is
    left of its process group, so a failing test leaks no sleep.'''
    path = tmp_path / 'pids'
    yield path
    if path.is_file() and path.read_text(encoding='utf-8').split():
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(int(path.read_text(encoding='utf-8').split()[0]), signal.SIGKILL)


def child_of(path: Path) -> int:
    return int(path.read_text(encoding='utf-8').split()[1])


def test_a_timeout_stops_everything_the_run_started(tmp_path, pids):
    '''Gate B runs claude under bash: a timeout must stop the grandchild too,
    not only the bash that started it.'''
    inv = probe_process.Invocation('slow', [str(executable(tmp_path / 'slow', SLOW)), str(pids)], {}, 3)
    assert probe_process.execute(inv, tmp_path, tmp_path / 'slow.out', tmp_path / 'slow.err') is None
    assert written(pids), 'the run was stopped before it started its child'
    assert gone(child_of(pids))


# A run whose leader starts a child and exits 0 at once, leaving the child in its process group.
LEAVER = '#!/bin/sh\nsleep 60 &\necho "$$ $!" > "$1"\n'


def test_a_normal_exit_sweeps_what_the_run_left_in_its_group(tmp_path, pids):
    '''A run that ends normally can still leave a background child in its group; execute ends it.'''
    inv = probe_process.Invocation('leaver', [str(executable(tmp_path / 'leaver', LEAVER)), str(pids)], {}, 30)
    assert probe_process.execute(inv, tmp_path, tmp_path / 'leaver.out', tmp_path / 'leaver.err') == 0
    assert gone(child_of(pids))


def test_an_invocation_with_sweep_off_leaves_its_group_alone(tmp_path, pids):
    '''async-teardown reads whether claude itself ended its hook, so its run is not swept.'''
    inv = probe_process.Invocation('leaver', [str(executable(tmp_path / 'leaver', LEAVER)), str(pids)], {}, 30,
                                   sweep=False)
    assert probe_process.execute(inv, tmp_path, tmp_path / 'leaver.out', tmp_path / 'leaver.err') == 0
    child = child_of(pids)
    try:
        assert not gone(child, 0.3)
    finally:
        with contextlib.suppress(ProcessLookupError):
            os.kill(child, signal.SIGKILL)


def test_a_sweep_of_a_group_already_gone_or_refused_still_returns_the_exit_code(tmp_path, monkeypatch):
    '''The sweep suppresses what stop_group suppresses: no group left, and the EPERM macOS gives for a group of
    unreaped members.'''
    script = executable(tmp_path / 'three', '#!/bin/sh\nexit 3\n')
    inv = probe_process.Invocation('three', [str(script)], {}, 30)
    for failure in (ProcessLookupError, PermissionError):
        sent = []

        def refuse(pgid, signum, failure=failure):
            sent.append(signum)
            raise failure
        monkeypatch.setattr(probe_process.os, 'killpg', refuse)
        assert probe_process.execute(inv, tmp_path, tmp_path / 'three.out', tmp_path / 'three.err') == 3
        assert sent == [signal.SIGKILL]


def test_an_interrupt_stops_everything_the_run_started_and_still_propagates(tmp_path, pids, monkeypatch):
    '''Ctrl-C while a probe runs: its own process group gets no SIGINT from
    the terminal, so execute stops the group itself before re-raising.'''
    real_wait = subprocess.Popen.wait

    def interrupted(proc, timeout=None):
        if timeout == 30:  # the probe's own wait, once its child is running
            assert written(pids), 'the run never started its child'
            raise KeyboardInterrupt
        return real_wait(proc, timeout)
    monkeypatch.setattr(subprocess.Popen, 'wait', interrupted)
    inv = probe_process.Invocation('slow', [str(executable(tmp_path / 'slow', SLOW)), str(pids)], {}, 30)
    with pytest.raises(KeyboardInterrupt):
        probe_process.execute(inv, tmp_path, tmp_path / 'slow.out', tmp_path / 'slow.err')
    assert gone(child_of(pids))


def test_a_stop_while_the_run_starts_still_stops_it(tmp_path, pids, monkeypatch):
    '''A SIGTERM that lands while Popen starts the run is held until proc
    is bound, so the run is stopped, not orphaned.'''
    real_popen, leaders = subprocess.Popen, []

    def starting(*args, **kwargs):
        proc = real_popen(*args, **kwargs)
        leaders.append(proc.pid)
        os.kill(os.getpid(), signal.SIGTERM)
        return proc
    monkeypatch.setattr(subprocess, 'Popen', starting)
    inv = probe_process.Invocation('slow', [str(executable(tmp_path / 'slow', SLOW)), str(pids)], {}, 30)
    with pytest.raises(SystemExit):
        with probe_process.term_as_exit():
            probe_process.execute(inv, tmp_path, tmp_path / 'slow.out', tmp_path / 'slow.err')
    assert gone(leaders[0])


def test_a_second_signal_during_the_grace_still_ends_with_sigkill(tmp_path, pids, monkeypatch):
    '''Ctrl-C while stop_group waits out SIGTERM's grace is held, so the
    SIGKILL still goes out, and the interrupt is raised after it.'''
    monkeypatch.setattr(probe_process, 'KILL_GRACE', 1)
    proc = subprocess.Popen([str(executable(tmp_path / 'stubborn', STUBBORN)), str(pids)], start_new_session=True)
    assert written(pids)
    threading.Timer(0.3, os.kill, (os.getpid(), signal.SIGINT)).start()
    with pytest.raises(KeyboardInterrupt):
        probe_process.stop_group(proc)
    assert gone(child_of(pids))


# Run in a child Python, so a signal left at its default ends the child, not pytest.
STOP_CHECK = """
import os, signal, sys, time
import probe_process
signum = int(sys.argv[1])
before = signal.getsignal(signum)
try:
    with probe_process.term_as_exit():
        os.kill(os.getpid(), signum)
        time.sleep(5)
except SystemExit:
    assert signal.getsignal(signum) is before
    raise
"""


@pytest.mark.parametrize('signum', [signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT])
def test_a_stop_signal_while_probes_run_exits_through_the_cleanup_path(signum):
    '''SIGTERM (a stopped tool), SIGHUP (a closed terminal) and SIGQUIT end
    Python with no except or finally by default; while probes run each one
    raises SystemExit instead, and the old handler comes back after. A
    negative exit code means the signal ended the child unhandled.'''
    proc = subprocess.run([sys.executable, '-c', STOP_CHECK, str(int(signum))], cwd=Path(__file__).parent,
                          capture_output=True, text=True, timeout=30)
    assert (proc.returncode, proc.stderr) == (128 + signum, '')


def test_a_hangup_ignored_by_nohup_stays_ignored():
    before = signal.signal(signal.SIGHUP, signal.SIG_IGN)
    try:
        with probe_process.term_as_exit():
            assert signal.getsignal(signal.SIGHUP) is signal.SIG_IGN
    finally:
        signal.signal(signal.SIGHUP, before)


def test_held_signals_act_once_the_block_is_done():
    reached = []
    with pytest.raises(SystemExit):
        with probe_process.term_as_exit():
            with probe_process.held_signals():
                os.kill(os.getpid(), signal.SIGTERM)
                time.sleep(0.2)
                reached.append('end of block')
    assert reached == ['end of block']


# Run in a child Python, started as nohup starts it: SIGHUP ignored.
HELD_CHECK = """
import os, signal, time
import probe_process
signal.signal(signal.SIGHUP, signal.SIG_IGN)
acted = []
signal.signal(signal.SIGTERM, lambda signum, frame: acted.append(signum))
with probe_process.held_signals():
    os.kill(os.getpid(), signal.SIGHUP)
    os.kill(os.getpid(), signal.SIGTERM)
    time.sleep(0.2)
print(acted, signal.getsignal(signal.SIGHUP) is signal.SIG_IGN)
"""


def test_an_ignored_signal_is_not_held_so_a_stop_after_it_is_acted_on_once():
    '''A SIGHUP that nohup ignores, landing in a held window, is not
    recorded: the SIGTERM after it is acted on once when the window ends,
    and SIGHUP stays ignored.'''
    proc = subprocess.run([sys.executable, '-c', HELD_CHECK], cwd=Path(__file__).parent,
                          capture_output=True, text=True, timeout=30)
    assert (proc.returncode, proc.stdout, proc.stderr) == (0, f'[{int(signal.SIGTERM)}] True\n', '')
