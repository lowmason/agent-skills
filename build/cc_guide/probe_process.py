# cc-guide: subagents.frontmatter lean.model-routing @2.1.326
'''Process control for a probe run (drift spec R10.4): the environment a run
starts from, the claude command line, one run in its own process group with
stdin closed, its stop on a timeout or a signal, and the stop signals that are
held or turned into SystemExit while probes run. The stdin and process-group
facts come from the drift spec, not the guide. Two comments rest on guide
sections: SCRUBBED_ENV on subagents.frontmatter and ALIAS_REMAPS on
lean.model-routing, which the citation line names, so the drift lint tracks
them here.'''
import contextlib
import json
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Callable, NamedTuple

from probe_checks import Verdict

KILL_GRACE = 5  # seconds between SIGTERM and SIGKILL when a run is stopped, and for each reap after
# SystemExit while probes run (term_as_exit). SIGHUP and SIGQUIT are POSIX-only, and cli.py imports this
# module through probes.py for every subcommand, so a platform without them still imports it.
EXIT_SIGNALS = tuple(getattr(signal, name) for name in ('SIGTERM', 'SIGHUP', 'SIGQUIT') if hasattr(signal, name))
HELD_SIGNALS = (signal.SIGINT, *EXIT_SIGNALS)  # held while a run starts or is stopped (held_signals)
# Variables a run never inherits from the caller. CLAUDE_CODE_EFFORT_LEVEL outranks an agent's effort
# field (subagents.frontmatter), so a value in the caller's shell would decide the effort agent-model-pins reads.
SCRUBBED_ENV = frozenset({'CLAUDE_CODE_EFFORT_LEVEL'})
# Variables that decide what each model alias resolves to (guide, lean.model-routing). A run keeps them, since on
# Bedrock, Google Cloud or Foundry a remap can be the owner's own setup, and its row names each one it inherits, so a
# DIVERGES from agent-model-pins can be read against them (owner ruling, 2026-10-31).
ALIAS_REMAPS = ('ANTHROPIC_DEFAULT_OPUS_MODEL', 'ANTHROPIC_DEFAULT_SONNET_MODEL', 'ANTHROPIC_DEFAULT_HAIKU_MODEL',
                'ANTHROPIC_DEFAULT_FABLE_MODEL')
GIT_ROUTING = ('GIT_',)  # inherited names such as GIT_DIR and GIT_WORK_TREE aim git at the caller's repository
BUDGET_USD = '0.50'  # --max-budget-usd for one probe invocation
PROBE_TIMEOUT = 600  # seconds for one probe invocation


class Invocation(NamedTuple):
    name: str             # its stdout goes to <name><suffix>, its stderr to <name>.err
    argv: list[str]
    env: dict[str, str]   # added to the caller's environment, less SCRUBBED_ENV
    timeout: int          # seconds
    suffix: str = '.jsonl'
    cwd: str = '.'        # the folder it runs in, relative to the scratch directory execute is given
    sweep: bool = True    # after a normal exit, SIGKILL whatever the run left in its process group
    drop_prefixes: tuple[str, ...] = ()  # inherited names starting with one of these are dropped before env is added


# Runs one invocation from a directory, writing its stdout and stderr to the
# two paths; returns its exit code, or None when it timed out.
Execute = Callable[[Invocation, Path, Path, Path], int | None]
# Reads a run directory's file by name: its text, or None when absent.
Read = Callable[[str], str | None]


class Probe(NamedTuple):
    # (scratch directory, claude, repo) -> the invocations to run there
    prepare: Callable[[Path, str, Path], list[Invocation]]
    # (scratch directory, run directory): copy what the run left beside its streams
    collect: Callable[[Path, Path], None]
    # the verdict from the run directory's files, the same path R12.6's replay takes
    assess: Callable[[Read], Verdict]
    # run-directory file -> the fixture file it is scrubbed into (R12.6)
    fixtures: dict[str, str]
    # whether the assertion reads a Bash call's command, so its fixtures keep the text (R12.6): only guard-liveness
    reads_commands: bool = False


def inherited_env(drop_prefixes: tuple[str, ...] = ()) -> dict[str, str]:
    '''The caller's environment less SCRUBBED_ENV and less each name starting with one of drop_prefixes: what
    every run starts from.'''
    return {name: value for name, value in os.environ.items()
            if name not in SCRUBBED_ENV and not name.startswith(drop_prefixes)}


def inherited_remaps() -> list[str]:
    '''The ALIAS_REMAPS names that a run inherits with a value, in ALIAS_REMAPS order.
    Names only: a value can be a provider's model path, and the log is public. An empty
    value remaps nothing, so it is not named.'''
    env = inherited_env()
    return [name for name in ALIAS_REMAPS if env.get(name)]


def execute(inv: Invocation, cwd: Path, out: Path, err: Path) -> int | None:
    '''R10.4: the prompt goes first and stdin is /dev/null, since claude -p
    waits on a piped stdin. The run gets its own process group, so a timeout
    or a stop ends everything it started, such as the claude under Gate B's
    bash: the group gets no terminal signal of its own. A stop signal while
    the run starts is held until `proc` is bound, so it cannot orphan it.
    The run inherits the caller's environment less SCRUBBED_ENV and less
    each name starting with one of drop_prefixes, then takes what the
    invocation adds, and runs from its cwd under `cwd`. After a normal exit, a run with sweep
    set has its group swept with SIGKILL, so a background child it left
    behind does not outlive the probe.'''
    env = inherited_env(inv.drop_prefixes) | inv.env
    with out.open('wb') as stdout, err.open('wb') as stderr:
        proc = None
        try:
            with held_signals():
                proc = subprocess.Popen(inv.argv, cwd=cwd / inv.cwd, stdin=subprocess.DEVNULL, stdout=stdout,
                                        stderr=stderr, env=env, start_new_session=True)
            code = proc.wait(timeout=inv.timeout)
        except subprocess.TimeoutExpired:
            stop_group(proc)
            return None
        except BaseException:  # Ctrl-C, or term_as_exit's SystemExit
            if proc is not None:
                stop_group(proc)
            raise
    if inv.sweep:
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(proc.pid, signal.SIGKILL)
    return code


def stop_group(proc: subprocess.Popen) -> None:
    '''SIGTERM to a run's process group, which lets a script's EXIT trap
    run, then SIGKILL to whatever is left after up to KILL_GRACE seconds.
    The wait is for the group's leader, not for every member: a member that
    outlives the leader gets the SIGKILL at once. A run that exits normally
    is swept by execute instead. Stop signals are held meanwhile, so a
    second Ctrl-C cannot skip the SIGKILL. macOS answers
    EPERM for a group whose members have all exited but are not reaped. The
    reaps are bounded, since an interrupted wait can leave Popen's lock held.'''
    with held_signals():
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(proc.pid, signal.SIGTERM)
        with contextlib.suppress(subprocess.TimeoutExpired):
            proc.wait(timeout=KILL_GRACE)
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(proc.pid, signal.SIGKILL)
        with contextlib.suppress(subprocess.TimeoutExpired):
            proc.wait(timeout=KILL_GRACE)


@contextlib.contextmanager
def held_signals():
    '''Record the stop signals instead of acting on them, then act on the
    first once the block is done, through the handler in force before it.
    Starting a run and stopping one must not be cut short. A signal already
    ignored, as nohup ignores SIGHUP, stays ignored and is not recorded, so
    a stop after it is still acted on. Main thread only, as signal.signal
    requires.'''
    got: list[int] = []
    held = [s for s in HELD_SIGNALS if signal.getsignal(s) is not signal.SIG_IGN]
    previous = {s: signal.signal(s, lambda signum, frame: got.append(signum)) for s in held}
    try:
        yield
    finally:
        for s, handler in previous.items():
            signal.signal(s, handler)
        if got:
            signal.raise_signal(got[0])


@contextlib.contextmanager
def environ_without(prefixes: tuple[str, ...]):
    '''Remove every os.environ name starting with one of `prefixes` for the block, then put back exactly the ones
    that were there, removing any the block added, even on an exception or a stop. probes.run wraps every probe in
    it with GIT_ROUTING, so no setup git and no child run reads a caller's GIT_DIR.'''
    saved = {name: value for name, value in os.environ.items() if name.startswith(prefixes)}
    for name in saved:
        del os.environ[name]
    try:
        yield
    finally:
        for name in [name for name in os.environ if name.startswith(prefixes)]:
            del os.environ[name]
        os.environ.update(saved)


@contextlib.contextmanager
def term_as_exit():
    '''While probes run, SIGTERM (a stopped tool), SIGHUP (a closed
    terminal) and SIGQUIT raise SystemExit, so a stopped run still ends its
    probe's process group and removes its scratch directory: by default each
    ends Python with no except or finally. A signal already ignored, as
    nohup ignores SIGHUP, stays ignored.'''
    exits = [s for s in EXIT_SIGNALS if signal.getsignal(s) is not signal.SIG_IGN]
    previous = {s: signal.signal(s, lambda signum, frame: sys.exit(128 + signum)) for s in exits}
    try:
        yield
    finally:
        for s, handler in previous.items():
            signal.signal(s, handler)


def claude_args(claude: str, prompt: str, *, turns: int, sources: str, mode: str, allow: tuple[str, ...] = (),
                budget: str = BUDGET_USD, persist: bool = False, extra: tuple[str, ...] = ()) -> list[str]:
    '''R10.4's command line: the prompt first, raw stream-json events, only
    the setting sources the probe needs, its permission mode pinned and its
    tools pre-allowed through --settings, Sonnet at low effort, and a bounded
    turn count and spend. Sessions are not persisted unless the probe reads
    its transcript.'''
    permissions = {'defaultMode': mode, **({'allow': list(allow)} if allow else {})}
    argv = [claude, prompt, '-p', '--output-format', 'stream-json', '--verbose',
            '--setting-sources', sources, '--settings', json.dumps({'permissions': permissions}),
            '--model', 'sonnet', '--effort', 'low', '--max-turns', str(turns), '--max-budget-usd', budget, *extra]
    return argv if persist else [*argv, '--no-session-persistence']
