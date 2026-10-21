# cc-guide: subagents.frontmatter subagents.isolation hooks.configuration @2.1.304.3
'''`probes` and `binaries` (drift spec R10.3-R10.7). `probes` runs the
registered probes that are due, the ones --only names, or every one with
--force, against the binary --claude names. Each run starts in a fresh
temporary directory outside every repo, loads only the setting sources the
probe needs, and keeps its raw output under the cache's probes/. Its
outcome comes from probe_checks.py and goes into one row of PROBES.md in the
working tree, which nothing commits. `binaries` lists the candidate
binaries with their versions.'''
import contextlib
import getpass
import itertools
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Callable, NamedTuple

import probe_checks
from check import due_probes
from docs import version_key
from probe_checks import Verdict
from state import ERROR, MANIFEST, PASS, PROBES, SetupError, Source, is_probe_header, parse_manifest, parse_probes

VERSION_RE = re.compile(r'(\d+(?:\.\d+)+) \(Claude Code\)')
# A tool name that starts with the MCP prefix, up to white space, a quote or a closing bracket.
MCP_TOKEN_RE = re.compile(re.escape(probe_checks.MCP_PREFIX) + r'''[^\s'"`)\]}>]*''')
VERSION_TIMEOUT = 30  # seconds for `claude --version`
PROBE_TIMEOUT = 600  # seconds for one probe invocation
PINS_TIMEOUT = 1200  # agent-model-pins waits on three background agents
# claude -p stops background agents 10 minutes after the main turn unless this
# says otherwise. 15 minutes is above PROBE_TIMEOUT and below PINS_TIMEOUT, so
# claude ends its own wait before the harness stops it (plan 58, decision D4).
PINS_CEILING_MS = 900_000
KILL_GRACE = 5  # seconds between SIGTERM and SIGKILL when a run is stopped, and for each reap after
# SystemExit while probes run (term_as_exit). SIGHUP and SIGQUIT are POSIX-only, and cli.py imports this
# module for every subcommand, so a platform without them still imports it.
EXIT_SIGNALS = tuple(getattr(signal, name) for name in ('SIGTERM', 'SIGHUP', 'SIGQUIT') if hasattr(signal, name))
HELD_SIGNALS = (signal.SIGINT, *EXIT_SIGNALS)  # held while a run starts or is stopped (held_signals)
# A setup or output problem inside a probe: an ERROR row, never a crash (R10.5).
PROBE_FAILURES = (OSError, subprocess.SubprocessError, ValueError, TypeError, KeyError, AttributeError)
BUDGET_USD = '0.50'  # --max-budget-usd for one probe invocation
PINS_BUDGET_USD = '0.75'  # three agents, one of them Opus at xhigh
TOOLS_TURNS, STOP_TURNS, PINS_TURNS = 1, 6, 8
GUARD_SCRIPT = 'hooks/probe-readonly-guard.sh'
GUARD_STREAMS = 3
DESKTOP_BUNDLES = Path('Library/Application Support/Claude/claude-code')
DESKTOP_GLOB = '*/*/claude.app/Contents/MacOS/claude'
DESKTOP_NOTE = 'Desktop app bundle (observed layout, not documented)'
LOG_TEXT = '\n'.join([
    '# Probe log', '',
    'One row per probe run, appended by `cli.py probes` (drift spec R10.6), newest last.',
    'Nothing commits it for you: review the rows, then commit them. Each run keeps its raw',
    'output under `~/.cache/agent-skills/cc-guide/probes/`.', '',
    '| Date | Version | Binary | Probe | Outcome | Finding | Flags |',
    '|---|---|---|---|---|---|---|', ''])


class Invocation(NamedTuple):
    name: str             # its stdout goes to <name><suffix>, its stderr to <name>.err
    argv: list[str]
    env: dict[str, str]   # added to the caller's environment
    timeout: int          # seconds
    suffix: str = '.jsonl'


# Runs one invocation from a directory, writing its stdout and stderr to the
# two paths; returns its exit code, or None when it timed out.
Execute = Callable[[Invocation, Path, Path, Path], int | None]
# Reads a run directory's file by name: its text, or None when absent.
Read = Callable[[str], str | None]


def execute(inv: Invocation, cwd: Path, out: Path, err: Path) -> int | None:
    '''R10.4: the prompt goes first and stdin is /dev/null, since claude -p
    waits on a piped stdin. The run gets its own process group, so a timeout
    or a stop ends everything it started, such as the claude under Gate B's
    bash: the group gets no terminal signal of its own. A stop signal while
    the run starts is held until `proc` is bound, so it cannot orphan it.'''
    with out.open('wb') as stdout, err.open('wb') as stderr:
        proc = None
        try:
            with held_signals():
                proc = subprocess.Popen(inv.argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                        env={**os.environ, **inv.env}, start_new_session=True)
            return proc.wait(timeout=inv.timeout)
        except subprocess.TimeoutExpired:
            stop_group(proc)
            return None
        except BaseException:  # Ctrl-C, or term_as_exit's SystemExit
            if proc is not None:
                stop_group(proc)
            raise


def stop_group(proc: subprocess.Popen) -> None:
    '''SIGTERM to a run's process group, which lets a script's EXIT trap
    run, then SIGKILL to whatever is left after KILL_GRACE. Stop signals are
    held meanwhile, so a second Ctrl-C cannot skip the SIGKILL. macOS answers
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
    Starting a run and stopping one must not be cut short. Main thread only,
    as signal.signal requires.'''
    got: list[int] = []
    previous = {s: signal.signal(s, lambda signum, frame: got.append(signum)) for s in HELD_SIGNALS}
    try:
        yield
    finally:
        for s, handler in previous.items():
            signal.signal(s, handler)
        if got:
            signal.raise_signal(got[0])


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


def stream_of(text: str | None) -> list[dict] | None:
    return None if text is None else probe_checks.parse_stream(text)


def copy_if_there(source: Path, target: Path) -> None:
    if source.is_file():
        shutil.copy(source, target)


class Probe(NamedTuple):
    # (scratch directory, claude, repo) -> the invocations to run there
    prepare: Callable[[Path, str, Path], list[Invocation]]
    # (scratch directory, run directory): copy what the run left beside its streams
    collect: Callable[[Path, Path], None]
    # the verdict from the run directory's files, the same path R12.6's replay takes
    assess: Callable[[Read], Verdict]
    # run-directory file -> the fixture file it is scrubbed into (R12.6)
    fixtures: dict[str, str]


def prepare_guard(scratch: Path, claude: str, repo: Path) -> list[Invocation]:
    '''guard-liveness wraps hooks/probe-readonly-guard.sh in a scratch git
    repo, with user settings, since the guard is installed globally.'''
    subprocess.run(['git', 'init', '-q'], cwd=scratch, check=True, capture_output=True)
    env = {'CLAUDE_BIN': claude, 'PROBE_STREAM_DIR': str(scratch / 'streams')}
    return [Invocation('guard', ['bash', str(repo / GUARD_SCRIPT)], env, PROBE_TIMEOUT, '.txt')]


def collect_guard(scratch: Path, run_dir: Path) -> None:
    for n in range(1, GUARD_STREAMS + 1):
        copy_if_there(scratch / 'streams' / f'{n}.jsonl', run_dir / f'guard-{n}.jsonl')


def assess_guard(read: Read) -> Verdict:
    return probe_checks.assess_guard_liveness([stream_of(read(f'guard-{n}.jsonl'))
                                               for n in range(1, GUARD_STREAMS + 1)])


TOOLS_AGENTS = {'probe-with-bash': 'Read, Grep, Glob, Bash', 'probe-without-bash': 'Read, Grep, Glob'}
TOOLS_AGENT_FILE = ('---\nname: {name}\ndescription: A drift probe agent.\ntools: {tools}\nomitClaudeMd: true\n'
                    '---\n\nReply with the word OK and nothing else.\n')


def prepare_agent_tools(scratch: Path, claude: str, repo: Path) -> list[Invocation]:
    '''agent-tools runs a scratch agent that lists Bash and a control that
    does not, each through --agent, from the scratch directory's project
    agents.'''
    agents = scratch / '.claude' / 'agents'
    agents.mkdir(parents=True)
    for name, tools in TOOLS_AGENTS.items():
        (agents / f'{name}.md').write_text(TOOLS_AGENT_FILE.format(name=name, tools=tools), encoding='utf-8')
    return [Invocation(name, claude_args(claude, 'Reply with the word OK.', turns=TOOLS_TURNS, sources='project',
                                         mode='default', extra=('--agent', name)), {}, PROBE_TIMEOUT)
            for name in TOOLS_AGENTS]


def collect_nothing(scratch: Path, run_dir: Path) -> None:
    '''agent-tools leaves nothing but its streams.'''


def assess_agent_tools(read: Read) -> Verdict:
    return probe_checks.assess_agent_tools(stream_of(read('probe-with-bash.jsonl')),
                                           stream_of(read('probe-without-bash.jsonl')), sys.platform)


# The Stop hook logs stop_hook_active and blocks on its first two calls. @LOG@
# is replaced by the quoted path of its log.
STOP_HOOK = r'''#!/usr/bin/env bash
input=$(cat)
v=$(printf '%s' "$input" | grep -o '"stop_hook_active"[[:space:]]*:[[:space:]]*\(true\|false\)' | grep -o 'true\|false')
echo "${v:-missing}" >> @LOG@
n=$(wc -l < @LOG@)
if [ "$n" -le 2 ]; then echo 'Reply with the word OK once more.' >&2; exit 2; fi
exit 0
'''


def prepare_stop(scratch: Path, claude: str, repo: Path) -> list[Invocation]:
    '''stop-continuation registers its Stop hook in the scratch directory's
    project settings, which plan 58's planning spike proved load (R10.2),
    and asks for hook events in the stream.'''
    hook = scratch / 'stop-hook.sh'
    hook.write_text(STOP_HOOK.replace('@LOG@', shlex.quote(str(scratch / 'stop.log'))), encoding='utf-8')
    hook.chmod(0o755)
    settings = {'hooks': {'Stop': [{'hooks': [{'type': 'command', 'command': shlex.quote(str(hook))}]}]}}
    (scratch / '.claude').mkdir()
    (scratch / '.claude' / 'settings.json').write_text(json.dumps(settings, indent=1) + '\n', encoding='utf-8')
    return [Invocation('stop', claude_args(claude, 'Reply with the word OK.', turns=STOP_TURNS, sources='project',
                                           mode='default', extra=('--include-hook-events',)), {}, PROBE_TIMEOUT)]


def collect_stop(scratch: Path, run_dir: Path) -> None:
    copy_if_there(scratch / 'stop.log', run_dir / 'stop.log')


def assess_stop(read: Read) -> Verdict:
    return probe_checks.assess_stop_continuation(stream_of(read('stop.jsonl')), (read('stop.log') or '').split())


PINS_PROMPT = ('In one message, call the Agent tool three times: (1) subagent_type "Explore" with prompt '
               '"List the file names in {dir}. Reply with the names only."; (2) subagent_type "test-runner" with '
               'prompt "Working directory: {dir}. Run exactly this command: true. Report its exit code in one '
               'line."; (3) subagent_type "code-reviewer" with prompt "Review {dir}/a.py against this one '
               'requirement: it prints hello. Reply in one sentence.". Wait for all three results, then reply '
               'with the word DONE.')


def prepare_pins(scratch: Path, claude: str, repo: Path) -> list[Invocation]:
    '''agent-model-pins takes the production path: an auto-mode parent with
    user settings dispatches the three pinned agents with the Agent tool, in
    fork mode's background, with the background ceiling raised (owner, plan
    58 decision D4). The session is persisted, since effort is read from the
    subagents' transcripts (R10.4, as plan 58 amends it).'''
    (scratch / 'a.py').write_text("print('hello')\n", encoding='utf-8')
    argv = claude_args(claude, PINS_PROMPT.format(dir=scratch), turns=PINS_TURNS, sources='user', mode='auto',
                       allow=('Agent',), budget=PINS_BUDGET_USD, persist=True, extra=('--forward-subagent-text',))
    return [Invocation('pins', argv, {'CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS': str(PINS_CEILING_MS)}, PINS_TIMEOUT)]


def read_transcripts(projects: Path, session: str | None) -> dict[str, list[dict]]:
    '''Each subagent's transcript lines, agent type -> [{'model', 'effort'}],
    from <projects>/<project>/<session>/subagents/: each agent-*.meta.json
    names its agent type, and the agent-*.jsonl beside it holds its lines.'''
    found: dict[str, list[dict]] = {}
    if not session:
        return found
    for meta in sorted(projects.glob(f'*/{session}/subagents/agent-*.meta.json')):
        kind = json.loads(meta.read_text(encoding='utf-8')).get('agentType')
        lines = meta.with_name(meta.name.removesuffix('.meta.json') + '.jsonl')
        if not lines.is_file():
            continue
        for line in filter(str.strip, lines.read_text(encoding='utf-8').split('\n')):
            entry = json.loads(line)
            if entry.get('type') == 'assistant':
                found.setdefault(kind, []).append({'model': (entry.get('message') or {}).get('model'),
                                                   'effort': entry.get('effort')})
    return found


def collect_pins(scratch: Path, run_dir: Path) -> None:
    '''The persisted transcripts of the stream's session, kept as transcripts.json.'''
    path = run_dir / 'pins.jsonl'
    events = stream_of(path.read_text(encoding='utf-8')) if path.is_file() else None
    session = next((e.get('session_id') for e in events or [] if probe_checks.is_init(e)), None)
    transcripts = read_transcripts(Path.home() / '.claude' / 'projects', session)
    (run_dir / 'transcripts.json').write_text(json.dumps(transcripts, indent=1) + '\n', encoding='utf-8')


def assess_pins(read: Read) -> Verdict:
    return probe_checks.assess_agent_model_pins(stream_of(read('pins.jsonl')),
                                                json.loads(read('transcripts.json') or '{}'))


PROBE_RUNS = {
    'guard-liveness': Probe(prepare_guard, collect_guard, assess_guard,
                            {f'guard-{n}.jsonl': f'guard-liveness.{n}.jsonl' for n in range(1, GUARD_STREAMS + 1)}),
    'agent-tools': Probe(prepare_agent_tools, collect_nothing, assess_agent_tools,
                         {'probe-with-bash.jsonl': 'agent-tools.with-bash.jsonl',
                          'probe-without-bash.jsonl': 'agent-tools.without-bash.jsonl'}),
    'stop-continuation': Probe(prepare_stop, collect_stop, assess_stop,
                               {'stop.jsonl': 'stop-continuation.jsonl', 'stop.log': 'stop-continuation.log'}),
    'agent-model-pins': Probe(prepare_pins, collect_pins, assess_pins,
                              {'pins.jsonl': 'agent-model-pins.jsonl',
                               'transcripts.json': 'agent-model-pins.transcripts.json'}),
}


def reader(folder: Path, names: dict[str, str] | None = None) -> Read:
    '''Reads a run directory, or with `names` a fixture directory under
    each run-directory name's fixture name.'''
    def read(name: str) -> str | None:
        path = folder / (names[name] if names else name)
        return path.read_text(encoding='utf-8') if path.is_file() else None
    return read


def private_strings() -> list[str]:
    '''What a committed probe file must not show: the home directory, the
    temporary directory, each as given and resolved, and the login name
    (owner, plan 58 decision D3). A machine with no login name makes getuser
    raise, OSError on Python 3.13 and KeyError before; the login is then an
    empty string, which redact skips, so the log row is not lost after the
    probe has spent its tokens.'''
    try:
        login = getpass.getuser()
    except (OSError, KeyError):
        login = ''
    return [str(Path.home()), str(Path.home().resolve()), tempfile.gettempdir(),
            os.path.realpath(tempfile.gettempdir()), login]


def save_fixtures(run_dir: Path, pid: str, dest: Path) -> list[Path]:
    '''R12.6: turn one recorded run into the fixtures its replay test reads,
    each stream cut down and scrubbed of the home directory, the temporary
    directory and the login name, and each other file scrubbed of the same
    (owner, plan 58 decision D3).'''
    private = private_strings()
    written = []
    for name, fixture in PROBE_RUNS[pid].fixtures.items():
        text = (run_dir / name).read_text(encoding='utf-8')
        if name.endswith('.jsonl'):
            events = probe_checks.parse_stream(text)
            if events is None:
                raise SetupError(f'{run_dir / name}: not a stream-json file')
            text = probe_checks.scrub_events(events, private)
        else:
            text = probe_checks.redact(text, private)
        dest.mkdir(parents=True, exist_ok=True)
        (dest / fixture).write_text(text, encoding='utf-8')
        written.append(dest / fixture)
    return written


def inside_a_repo(path: Path) -> bool:
    proc = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], cwd=path, capture_output=True, text=True)
    return proc.returncode == 0 and proc.stdout.strip() == 'true'


def new_run_dir(parent: Path, stem: str) -> Path:
    '''A run directory of its own under parent: stem, or stem-2, stem-3 and
    so on once a run in the same second has taken it. mkdir without
    exist_ok claims a name or fails, so two runs, from two worktrees or a
    scripted loop, never share one.'''
    parent.mkdir(parents=True, exist_ok=True)
    for n in itertools.count(1):
        path = parent / (stem if n == 1 else f'{stem}-{n}')
        try:
            path.mkdir()
        except FileExistsError:
            continue
        return path


def run_probe(pid: str, claude: str, repo: Path, run_dir: Path, execute: Execute = execute) -> Verdict:
    '''One probe, from a fresh temporary directory that is removed after the
    verdict; its raw output stays in run_dir. A setup failure, a timeout or
    unreadable output is ERROR, never a pass.'''
    probe = PROBE_RUNS[pid]
    run_dir.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix=f'cc-guide-probe-{pid}-')).resolve()
    try:
        if inside_a_repo(scratch):
            return Verdict(ERROR, f'the temporary directory {scratch} is inside a git work tree')
        for inv in probe.prepare(scratch, claude, repo):
            (run_dir / f'{inv.name}.argv.json').write_text(json.dumps(inv.argv, indent=1) + '\n', encoding='utf-8')
            if execute(inv, scratch, run_dir / f'{inv.name}{inv.suffix}', run_dir / f'{inv.name}.err') is None:
                return Verdict(ERROR, f'{inv.name} timed out after {inv.timeout} s')
        probe.collect(scratch, run_dir)
        return probe.assess(reader(run_dir))
    except PROBE_FAILURES as exc:
        return Verdict(ERROR, f'{type(exc).__name__}: {exc}')
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def binary_version(claude: Path) -> str:
    '''The release label `claude --version` prints, or a SetupError.'''
    try:
        proc = subprocess.run([str(claude), '--version'], capture_output=True, text=True, stdin=subprocess.DEVNULL,
                              timeout=VERSION_TIMEOUT)
    except (OSError, subprocess.SubprocessError) as exc:
        raise SetupError(f'{claude} --version: {exc}') from None
    found = VERSION_RE.search(proc.stdout)
    if proc.returncode != 0 or found is None:
        raise SetupError(f'{claude} --version printed no Claude Code version')
    return found.group(1)


def shown_path(path: Path) -> str:
    '''A path as the log shows it, with ~ for the home directory (R10.6).'''
    home, text = str(Path.home()), str(path)
    return '~' + text[len(home):] if text == home or text.startswith(home + os.sep) else text


def cell(text: str) -> str:
    '''Text as one table cell: whitespace collapsed, pipes escaped.'''
    return ' '.join(text.split()).replace('|', '\\|')


def log_row(day: date, version: str, claude: Path, pid: str, verdict: Verdict, allow_old: bool) -> str:
    '''One log row. PROBES.md is committed to a public repo, and a finding can
    carry a home or temporary path, the login name or an MCP tool name, so
    the finding is scrubbed as a fixture is (owner, plan 58 decision D3). The
    MCP pass runs first: a private string inside an MCP name would otherwise
    become <private>, and the pass would stop at its > and leave the rest of
    the name in the log.'''
    finding = probe_checks.redact(MCP_TOKEN_RE.sub(probe_checks.MCP_MARK, verdict.finding), private_strings())
    cells = [day.isoformat(), version, shown_path(claude), pid, verdict.outcome, finding,
             '--allow-old' if allow_old else '']
    return '| ' + ' | '.join(map(cell, cells)) + ' |'


def append_row(path: Path, row: str) -> None:
    '''Append a row to PROBES.md's log table, creating the file when absent.
    The row goes right after the table's last row, so text below the table
    never splits it from its header. The new log replaces the old one whole,
    so a stop mid-write never leaves the log cut short, and the folder lock
    keeps a second run's row from being lost.'''
    with locked(path.parent):
        lines = (path.read_text(encoding='utf-8') if path.is_file() else LOG_TEXT).split('\n')
        start = next((i for i, line in enumerate(lines) if is_probe_header(line)), None)
        if start is None:
            raise SetupError(f'{PROBES}: no log table naming the date, version, probe and outcome columns')
        end = start
        while end + 1 < len(lines) and lines[end + 1].strip().startswith('|'):
            end += 1
        lines.insert(end + 1, row)
        draft = path.with_name(f'.{path.name}.new')
        try:
            draft.write_text('\n'.join(lines), encoding='utf-8')
            os.replace(draft, path)
        finally:
            draft.unlink(missing_ok=True)


@contextlib.contextmanager
def locked(folder: Path):
    '''An exclusive lock on a folder, so two probes runs in one working tree
    append to its log one at a time; flock takes a folder's descriptor on
    macOS and Linux, and leaves no lock file behind. fcntl is POSIX-only,
    so it is imported here, where only a probes run reaches it.'''
    import fcntl
    fd = os.open(folder, os.O_RDONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def run(repo: Path, cache: Path, claude: Path, *, only: list[str] | None, force: bool, allow_old: bool,
        newest: str, today: date, now: datetime, execute: Execute = execute,
        version_of: Callable[[Path], str] = binary_version) -> tuple[int, list[str]]:
    '''R10.6: run the chosen probes and append a row for each; (exit code,
    lines to print). Exit 0 when every probe passed or none was due, 1 when
    any DIVERGES or is ERROR. A setup problem raises SetupError (exit 2):
    an unknown probe, an unusable binary, or one older than `newest`, the
    newest cached changelog release, without --allow-old (R10.3).'''
    tree = Source(repo)
    manifest = parse_manifest(tree.require(MANIFEST))
    rows = parse_probes(tree.read(PROBES))
    unbuilt = sorted(set(manifest.probes) - set(PROBE_RUNS))
    if unbuilt:
        raise SetupError(f"{MANIFEST} registers {', '.join(unbuilt)}, which probes.py does not run")
    unknown = sorted(set(only or []) - set(manifest.probes))
    if unknown:
        raise SetupError(f"--only {', '.join(unknown)}: not a registered probe")
    if not (claude.is_file() and os.access(claude, os.X_OK)):
        raise SetupError(f'--claude {claude}: not an executable file')
    version = version_of(claude)
    if version_key(version) < version_key(newest) and not allow_old:
        raise SetupError(f'--claude {claude} is {version}, older than the newest changelog release {newest}: '
                         'pass --allow-old to run it anyway, and each row records the flag (R10.3)')
    chosen = only or (list(manifest.probes) if force else
                      [d['probe'] for d in due_probes(manifest, rows, newest, manifest.cadence['probe_days'], today)])
    if not chosen:
        return 0, ['probes: none due']
    lines, outcomes = [f'probes: {version} at {shown_path(claude)}'], []
    with term_as_exit():
        for pid in dict.fromkeys(chosen):
            run_dir = new_run_dir(cache / 'probes', f"{now.strftime('%Y%m%dT%H%M%S')}-{pid}")
            verdict = run_probe(pid, str(claude), repo, run_dir, execute)
            append_row(repo / PROBES, log_row(today, version, claude, pid, verdict, allow_old))
            outcomes.append(verdict.outcome)
            lines += [f'{pid}: {verdict.outcome}: {verdict.finding}', f'  raw output: {run_dir}']
    lines.append(f'appended {len(outcomes)} row(s) to {PROBES}; nothing is committed')
    return (0 if all(o == PASS for o in outcomes) else 1), lines


class Candidate(NamedTuple):
    path: Path
    target: Path
    version: str | None
    where: str


def binaries(path_env: str, home: Path, version_of: Callable[[Path], str] = binary_version) -> list[Candidate]:
    '''R10.3: each claude on PATH with its symlink target, then the Desktop
    app's bundled binaries, labelled as an observed layout.'''
    def version(path: Path) -> str | None:
        try:
            return version_of(path)
        except SetupError:
            return None
    found: list[Candidate] = []
    for folder in dict.fromkeys(filter(None, path_env.split(os.pathsep))):
        exe = Path(folder) / 'claude'
        if exe.is_file() and os.access(exe, os.X_OK):
            found.append(Candidate(exe, exe.resolve(), version(exe), 'PATH'))
    for exe in sorted((home / DESKTOP_BUNDLES).glob(DESKTOP_GLOB)):
        found.append(Candidate(exe, exe.resolve(), version(exe), DESKTOP_NOTE))
    return found


def describe(c: Candidate) -> str:
    target = '' if c.target == c.path else f' -> {shown_path(c.target)}'
    return f"{c.version or 'version unknown'}  {shown_path(c.path)}{target}  ({c.where})"
