# cc-guide: subagents.frontmatter subagents.isolation hooks.configuration @2.1.326
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
import secrets
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import tomllib
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Callable, NamedTuple, Sequence

import probe_checks
import probe_worktrees
from check import due_probes
from docs import version_key
from probe_checks import Verdict
from probe_process import (PROBE_TIMEOUT, Execute, Invocation, Probe, Read, claude_args, execute, inherited_remaps,
                           term_as_exit)
from state import ERROR, MANIFEST, PASS, PROBES, SetupError, Source, is_probe_header, parse_manifest, parse_probes

VERSION_RE = re.compile(r'(\d+(?:\.\d+)+) \(Claude Code\)')
VERSION_TIMEOUT = 30  # seconds for `claude --version`
PINS_TIMEOUT = 1200  # agent-model-pins waits on three background agents
# claude -p stops background agents 10 minutes after the main turn unless this
# says otherwise. 15 minutes is above PROBE_TIMEOUT and below PINS_TIMEOUT, so
# claude ends its own wait before the harness stops it (plan 58, decision D4).
PINS_CEILING_MS = 900_000
# agent-payload's two dispatches may run in the background too. This ceiling sits under PROBE_TIMEOUT, so claude
# ends its own wait before the harness stops the run.
PAYLOAD_CEILING_MS = 300_000
# A setup or output problem inside a probe: an ERROR row, never a crash (R10.5).
PROBE_FAILURES = (OSError, subprocess.SubprocessError, ValueError, TypeError, KeyError, AttributeError,
                  SetupError)
PINS_BUDGET_USD = '0.75'  # three agents, one of them Opus at xhigh
TOOLS_TURNS, STOP_TURNS, PINS_TURNS, PAYLOAD_TURNS = 1, 6, 8, 6
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


def stream_of(text: str | None) -> list[dict] | None:
    return None if text is None else probe_checks.parse_stream(text)


def copy_if_there(source: Path, target: Path) -> None:
    if source.is_file():
        shutil.copy(source, target)


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
TOOLS_AGENT_FILE = ('---\nname: {name}\ndescription: A drift probe agent.\ntools: {tools}\n'
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
    user settings dispatches the three pinned agents with the Agent tool.
    They start in the background, so the background ceiling is raised (owner,
    plan 58 decision D4). The session is persisted, since effort is read from the
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


# Each PreToolUse payload goes to a file of its own in the folder the hook is
# given, since the two hooks, and two dispatches in one message, can run at once.
PAYLOAD_HOOK = '#!/usr/bin/env bash\ncat > "$(mktemp "$1/payload.XXXXXX")"\n'
PAYLOAD_PROMPT = ('In one message, call the Agent tool twice: (1) subagent_type "general-purpose" with model "haiku" '
                  'and prompt "Reply with the word OK and nothing else. Use no tools."; (2) subagent_type '
                  '"claude-code-guide", passing no model, with prompt "Reply with the word OK and nothing else. Use '
                  'no tools.". Wait for both results, then reply with the word DONE.')


def prepare_payload(scratch: Path, claude: str, repo: Path) -> list[Invocation]:
    '''agent-payload logs every PreToolUse payload through two hooks in the
    scratch directory's project settings, one matching every tool and one
    matching Agent as hooks/README.md installs the guard, while the parent
    dispatches the haiku control and each pinned built-in. Only project
    settings load, so the owner's own hooks and agents stay out of the run,
    and the session is not persisted, since the stream holds each model.'''
    hook = scratch / 'payload-hook.sh'
    hook.write_text(PAYLOAD_HOOK, encoding='utf-8')
    hook.chmod(0o755)
    groups = []
    for folder, matcher in probe_checks.PAYLOAD_LOGS.items():
        log = scratch / 'payloads' / folder
        log.mkdir(parents=True)
        command = f'{shlex.quote(str(hook))} {shlex.quote(str(log))}'
        groups.append({'matcher': matcher, 'hooks': [{'type': 'command', 'command': command}]})
    (scratch / '.claude').mkdir()
    settings = {'hooks': {'PreToolUse': groups}}
    (scratch / '.claude' / 'settings.json').write_text(json.dumps(settings, indent=1) + '\n', encoding='utf-8')
    argv = claude_args(claude, PAYLOAD_PROMPT, turns=PAYLOAD_TURNS, sources='project', mode='default',
                       allow=('Agent',), extra=('--forward-subagent-text',))
    return [Invocation('dispatch', argv, {'CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS': str(PAYLOAD_CEILING_MS)},
                       PROBE_TIMEOUT)]


def collect_payload(scratch: Path, run_dir: Path) -> None:
    '''Each hook's log, raw, as payloads-<folder>.raw.jsonl, one payload a
    line, to read by hand, then payloads.json from those copies
    (rebuild_payloads).'''
    for folder in probe_checks.PAYLOAD_LOGS:
        texts = [path.read_text(encoding='utf-8').strip()
                 for path in sorted((scratch / 'payloads' / folder).glob('payload.*'))]
        (run_dir / f'payloads-{folder}.raw.jsonl').write_text(''.join(f'{t}\n' for t in texts), encoding='utf-8')
    rebuild_payloads(run_dir)


def rebuild_payloads(run_dir: Path) -> None:
    '''payloads.json, the one file the assessment and its fixture read,
    from run_dir's payloads-<folder>.raw.jsonl alone, so a past run's raw
    logs can be read again under a changed trim. Each line is one payload,
    an empty one included. A payload that is not JSON raises ValueError,
    which run_probe reports as ERROR.'''
    raw = {}
    for folder in probe_checks.PAYLOAD_LOGS:
        text = (run_dir / f'payloads-{folder}.raw.jsonl').read_text(encoding='utf-8')
        raw[folder] = text.removesuffix('\n').split('\n') if text else []
    (run_dir / 'payloads.json').write_text(json.dumps(probe_checks.payload_file(raw), indent=1) + '\n',
                                           encoding='utf-8')


def assess_payload(read: Read) -> Verdict:
    return probe_checks.assess_agent_payload(stream_of(read('dispatch.jsonl')),
                                             json.loads(read('payloads.json') or '{}'))


PAYLOAD_PROBE = Probe(prepare_payload, collect_payload, assess_payload,
                      {'dispatch.jsonl': 'agent-payload.jsonl', 'payloads.json': 'agent-payload.payloads.json'})


# compaction-cut: one claude process takes three messages on stdin, since a /compact in a resumed process
# re-attaches nothing (plan 87's spike, setup B). The first invokes both probe skills, the second compacts, and the
# third is one more turn after it.
CUT_PROMPT = 'Invoke the skill cut-probe-prose with the Skill tool, then the skill cut-probe-digit. Then reply DONE.'
CUT_MESSAGES = (CUT_PROMPT, '/compact', 'Reply OK.')
CUT_TURNS = 8
CUT_BUDGET_USD = '0.75'
CONFORMANCE = Path(__file__).resolve().with_name('conformance.toml')
WINDOW_CHECK = 'compaction-window'


def register_window() -> int:
    '''The register's compaction window in characters, from its
    compaction-window check: tokens times chars_per_token, less
    reserve_chars when the check sets it. A register without the check
    raises KeyError, which run_probe reports as ERROR.'''
    register = tomllib.loads(CONFORMANCE.read_text(encoding='utf-8'))
    check = {c.get('id'): c for c in register.get('check') or []}[WINDOW_CHECK]
    return check['tokens'] * check['chars_per_token'] - check.get('reserve_chars', 0)


def relay_to_result(stdout, out) -> dict | None:
    '''Copy the process's stdout to ours a line at a time, up to a result
    event, which it returns, or to the end of the stream: None.'''
    for line in stdout:
        out.write(line)
        out.flush()
        events = probe_checks.parse_stream(line.decode('utf-8', errors='replace')) or []
        result = next((e for e in events if e.get('type') == 'result'), None)
        if result is not None:
            return result
    return None


def drive_cut(argv: list[str]) -> int:
    '''Run `argv`, a claude -p command line with --input-format stream-json
    and no prompt, and feed it CUT_MESSAGES on its stdin, one JSON line
    each, each only once the previous one's result event is read. Every
    stdout line is copied to ours as it comes. Nothing more is sent after
    an error result, a closed stdin or the end of its stdout. Then its
    stdin is closed, its stdout copied to the end and its exit code
    returned, on a failure too, so it is never left running. stderr is
    inherited and not piped, so it cannot fill a pipe nobody reads. It
    starts no session of its own, so the stop signal that execute sends to
    this process's group reaches claude too.'''
    proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out = sys.stdout.buffer
    try:
        for message in CUT_MESSAGES:
            line = json.dumps({'type': 'user', 'message': {'role': 'user', 'content': message}}) + '\n'
            try:
                proc.stdin.write(line.encode('utf-8'))
                proc.stdin.flush()
            except BrokenPipeError:
                break
            result = relay_to_result(proc.stdout, out)
            if result is None or result.get('is_error'):
                break
    finally:
        with contextlib.suppress(OSError):
            proc.stdin.close()
        for line in proc.stdout:
            out.write(line)
        out.flush()
        code = proc.wait()
    return code


def prepare_cut(scratch: Path, claude: str, repo: Path) -> list[Invocation]:
    '''compaction-cut writes both probe skills to the scratch directory's
    project skills and names the session ahead in a session-id file, so
    collect can find its transcript. The invocation is this file's
    drive-cut entry point, which runs claude and feeds it CUT_MESSAGES;
    claude's command line goes without the prompt, which drive_cut sends
    first, and keeps its session, since collect reads the transcript.'''
    for kind in probe_checks.CUT_KINDS:
        skill = scratch / '.claude' / 'skills' / f'cut-probe-{kind}'
        skill.mkdir(parents=True)
        (skill / 'SKILL.md').write_text(probe_checks.cut_frontmatter(kind) + probe_checks.cut_body(kind),
                                        encoding='utf-8')
    session = str(uuid.uuid4())
    (scratch / 'session-id').write_text(f'{session}\n', encoding='utf-8')
    argv = claude_args(claude, CUT_PROMPT, turns=CUT_TURNS, sources='project', mode='default', allow=('Skill',),
                       budget=CUT_BUDGET_USD, persist=True,
                       extra=('--input-format', 'stream-json', '--session-id', session))
    driver = [sys.executable, str(Path(__file__).resolve()), 'drive-cut', json.dumps([argv[0], *argv[2:]])]
    return [Invocation('cut', driver, {}, PROBE_TIMEOUT)]


def collect_cut(scratch: Path, run_dir: Path) -> None:
    '''The session's transcript, found by the id in the session-id file,
    copied raw as transcript.raw.jsonl, to read by hand, and each kind's
    re-attached copy measured into cut.json, the one file the assessment
    and its fixture read. No transcript leaves cut.json empty, which the
    assessment reports as ERROR.'''
    session = (scratch / 'session-id').read_text(encoding='utf-8').strip()
    found = sorted((Path.home() / '.claude' / 'projects').glob(f'*/{session}.jsonl'))
    cut = {}
    if found:
        shutil.copy(found[0], run_dir / 'transcript.raw.jsonl')
        text = found[0].read_text(encoding='utf-8')
        entries = [json.loads(line) for line in filter(str.strip, text.split('\n'))]
        copies = probe_checks.reattached_after_boundary(entries, probe_checks.CUT_KINDS)
        cut = {kind: probe_checks.measure_cut(copy, probe_checks.cut_body(kind)) for kind, copy in copies.items()}
    (run_dir / 'cut.json').write_text(json.dumps(cut, indent=1) + '\n', encoding='utf-8')


def assess_cut(read: Read) -> Verdict:
    return probe_checks.assess_compaction_cut(stream_of(read('cut.jsonl')), json.loads(read('cut.json') or '{}'),
                                              register_window())


CUT_PROBE = Probe(prepare_cut, collect_cut, assess_cut,
                  {'cut.jsonl': 'compaction-cut.stream.jsonl', 'cut.json': 'compaction-cut.cut.json'})


# explore-override: a project agent named Explore, overriding the built-in, and a custom control. Each may not read,
# search or run anything, and answers from its context alone; probe_checks.explore_sightings reads the answers.
EXPLORE_FILES = {'explore': probe_checks.EXPLORE_AGENT, 'canary-control': probe_checks.CANARY_AGENT}  # stem -> name
EXPLORE_AGENT_FILE = ('---\nname: {name}\ndescription: A drift probe agent.\n'
                      'disallowedTools: Read, Grep, Glob, Bash, Edit, Write\n---\n\n'
                      'Use no tools. Answer from your context alone, in exactly three lines:\n'
                      '1. {mark}\n'
                      "2. The canary word that this project's CLAUDE.md gives, or NONE if your context holds no "
                      'CLAUDE.md.\n'
                      '3. The untracked file names that your git status lists, or NONE if your context holds no git '
                      'status.\n')
EXPLORE_PROMPT = ('In one message, call the Agent tool twice: (1) subagent_type "Explore" with prompt "Follow your '
                  'instructions."; (2) subagent_type "canary-control" with prompt "Follow your instructions.". Wait '
                  'for both results, then reply with the word DONE.')
CANARY_BYTES = 4  # secrets.token_hex bytes in each canary: eight hex digits


def prepare_explore(scratch: Path, claude: str, repo: Path) -> list[Invocation]:
    '''explore-override draws two canaries, kept in canaries.json: the
    word CLAUDE.md gives, and the name of an untracked file, which only a
    git-status snapshot lists, in a fresh git repo. The two agents are
    project agents, and only project settings load, so this repo's
    installed agents/explore.md, a user agent, stays out, as in
    agent-payload; each agent's mark shows which definition served. The
    parent names neither canary. Each of the EXPLORE_REPS reps is its own
    invocation from the same scratch directory, and its dispatches may run
    in the background, as agent-payload's may.'''
    subprocess.run(['git', 'init', '-q'], cwd=scratch, check=True, capture_output=True)
    canaries = {'claude_md': f'cm-{secrets.token_hex(CANARY_BYTES)}',
                'git_status': f'gs-{secrets.token_hex(CANARY_BYTES)}'}
    (scratch / 'canaries.json').write_text(json.dumps(canaries, indent=1) + '\n', encoding='utf-8')
    (scratch / 'CLAUDE.md').write_text(f"The canary word for this project is {canaries['claude_md']}.\n",
                                       encoding='utf-8')
    (scratch / f"{canaries['git_status']}.txt").write_text('An untracked file.\n', encoding='utf-8')
    agents = scratch / '.claude' / 'agents'
    agents.mkdir(parents=True)
    for stem, name in EXPLORE_FILES.items():
        (agents / f'{stem}.md').write_text(EXPLORE_AGENT_FILE.format(name=name, mark=probe_checks.EXPLORE_MARKS[name]),
                                           encoding='utf-8')
    argv = claude_args(claude, EXPLORE_PROMPT, turns=PAYLOAD_TURNS, sources='project', mode='default',
                       allow=('Agent',), extra=('--forward-subagent-text',))
    env = {'CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS': str(PAYLOAD_CEILING_MS)}
    return [Invocation(f'explore-{n}', argv, env, PROBE_TIMEOUT) for n in range(1, probe_checks.EXPLORE_REPS + 1)]


def collect_explore(scratch: Path, run_dir: Path) -> None:
    '''canaries.json, copied beside the streams, and sightings.json, the
    one file the assessment and its fixture read: one entry a rep, read
    from its stream with those canaries. A missing stream is a broken rep.'''
    shutil.copy(scratch / 'canaries.json', run_dir / 'canaries.json')
    canaries = json.loads((run_dir / 'canaries.json').read_text(encoding='utf-8'))
    sightings = []
    for n in range(1, probe_checks.EXPLORE_REPS + 1):
        path = run_dir / f'explore-{n}.jsonl'
        events = stream_of(path.read_text(encoding='utf-8')) if path.is_file() else None
        sightings.append(probe_checks.explore_sightings(events, canaries))
    (run_dir / 'sightings.json').write_text(json.dumps(sightings, indent=1) + '\n', encoding='utf-8')


def assess_explore(read: Read) -> Verdict:
    return probe_checks.assess_explore_override(json.loads(read('sightings.json') or '[]'))


# async-teardown: an async SessionStart hook that logs `start <pid>`, then the name of each TEARDOWN_SIGNALS signal
# it gets, and keeps running, since each trap only logs. `sleep 1 & wait $!` lets a trap run at once, not once a sleep
# ends, and the loop ends by itself within TEARDOWN_LIFETIME seconds, so the hook never runs unbounded; it then logs
# TEARDOWN_EXPIRED, which the assessment reads as ERROR. It writes nothing to stdout or stderr, so a pipe that claude
# closes cannot end it with SIGPIPE.
TEARDOWN_WAIT = probe_checks.TEARDOWN_WAIT  # seconds collect_teardown waits for the hook to go
TEARDOWN_POLL = 0.1  # seconds between two looks for the hook
TEARDOWN_LIFETIME = probe_checks.TEARDOWN_LIFETIME  # seconds the hook runs at most
TEARDOWN_TURNS = 1
TEARDOWN_LOG = 'teardown.log'
TEARDOWN_SCRIPT = 'teardown-hook.sh'
TEARDOWN_TRAP = '''trap 'printf "{name}\\n" >> "$log"' {name}'''
TEARDOWN_HOOK = '\n'.join(['#!/bin/sh', 'log=$1', 'echo "start $$" >> "$log"',
                           *(TEARDOWN_TRAP.format(name=name) for name in probe_checks.TEARDOWN_SIGNALS),
                           'n=0', f'while [ "$n" -lt {TEARDOWN_LIFETIME} ]; do', '    sleep 1 & wait $!',
                           '    n=$((n + 1))', 'done', f'echo {probe_checks.TEARDOWN_EXPIRED} >> "$log"', ''])


def prepare_teardown(scratch: Path, claude: str, repo: Path) -> list[Invocation]:
    '''async-teardown registers its hook in the scratch directory's
    project settings as an async SessionStart command hook on the startup
    matcher, as .claude/settings.json registers notice.sh's refresh, and
    asks for hook events in the stream, where claude -p may finalize the
    hook as cancelled. The reply takes one turn, so the hook is still
    running when the run ends. The run is not swept, so collect_teardown
    sees whether claude itself ended the hook.'''
    hook = scratch / TEARDOWN_SCRIPT
    hook.write_text(TEARDOWN_HOOK, encoding='utf-8')
    hook.chmod(0o755)
    command = f'{shlex.quote(str(hook))} {shlex.quote(str(scratch / TEARDOWN_LOG))}'
    settings = {'hooks': {'SessionStart': [{'matcher': 'startup',
                                            'hooks': [{'type': 'command', 'command': command, 'async': True}]}]}}
    (scratch / '.claude').mkdir()
    (scratch / '.claude' / 'settings.json').write_text(json.dumps(settings, indent=1) + '\n', encoding='utf-8')
    argv = claude_args(claude, 'Reply with the word OK.', turns=TEARDOWN_TURNS, sources='project', mode='default',
                       extra=('--include-hook-events',))
    return [Invocation('teardown', argv, {}, PROBE_TIMEOUT, sweep=False)]


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding='utf-8').splitlines() if path.is_file() else []


def running(pid: int) -> bool:
    '''Whether a process has the pid. PermissionError means one does,
    though not one this user may signal.'''
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def is_hook(pid: int, hook: Path) -> bool:
    '''Whether the process with the pid runs the hook script: its command
    line, as `ps -o args=` shows it, holds the script's path. A pid alone is
    not a process identity, since the OS may reuse a gone hook's pid. A ps
    that fails, as it does for a pid no process holds, is False.'''
    try:
        proc = subprocess.run(['ps', '-o', 'args=', '-p', str(pid)], capture_output=True, text=True)
    except OSError:
        return False
    return proc.returncode == 0 and str(hook) in proc.stdout


def hook_pids(lines: list[str]) -> list[int]:
    '''The pid on each start line of the hook's log, less those os.kill
    must never get: 0, which is the caller's own process group, 1, which is
    init, and this process.'''
    found = [int(m.group(1)) for m in map(probe_checks.TEARDOWN_START_RE.fullmatch, lines) if m]
    return [pid for pid in found if pid > 1 and pid != os.getpid()]


def collect_teardown(scratch: Path, run_dir: Path) -> None:
    '''The hook's log as teardown.log, with gone or alive added: whether
    each pid on its start lines was gone within TEARDOWN_WAIT seconds of
    claude -p's end. Each one still there after the wait, or when the wait
    is cut short, gets SIGKILL, which no trap catches, so the hook never
    outlives the probe. A pid counts as there only while it runs the hook
    (is_hook): a process that took a gone hook's pid reads as gone and is
    never signalled. The log is read again after the wait, so a signal
    the hook logs late still counts. A log with no start line is copied as
    it is, and an absent one as empty: the assessment reads either as
    ERROR.'''
    log, hook = scratch / TEARDOWN_LOG, scratch / TEARDOWN_SCRIPT
    pids, end = hook_pids(read_lines(log)), []

    def there(pid: int) -> bool:
        return running(pid) and is_hook(pid, hook)
    try:
        deadline = time.monotonic() + TEARDOWN_WAIT
        while any(map(there, pids)) and time.monotonic() < deadline:
            time.sleep(TEARDOWN_POLL)
        if pids:
            end = [probe_checks.TEARDOWN_ALIVE if any(map(there, pids)) else probe_checks.TEARDOWN_GONE]
    finally:
        for pid in filter(there, pids):
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.kill(pid, signal.SIGKILL)
    (run_dir / TEARDOWN_LOG).write_text(''.join(f'{line}\n' for line in [*read_lines(log), *end]), encoding='utf-8')


def assess_teardown(read: Read) -> Verdict:
    return probe_checks.assess_async_teardown(stream_of(read('teardown.jsonl')),
                                              (read(TEARDOWN_LOG) or '').splitlines())


PROBE_RUNS = {
    'guard-liveness': Probe(prepare_guard, collect_guard, assess_guard,
                            {f'guard-{n}.jsonl': f'guard-liveness.{n}.jsonl' for n in range(1, GUARD_STREAMS + 1)},
                            reads_commands=True),
    'agent-tools': Probe(prepare_agent_tools, collect_nothing, assess_agent_tools,
                         {'probe-with-bash.jsonl': 'agent-tools.with-bash.jsonl',
                          'probe-without-bash.jsonl': 'agent-tools.without-bash.jsonl'}),
    'stop-continuation': Probe(prepare_stop, collect_stop, assess_stop,
                               {'stop.jsonl': 'stop-continuation.jsonl', 'stop.log': 'stop-continuation.log'}),
    'agent-model-pins': Probe(prepare_pins, collect_pins, assess_pins,
                              {'pins.jsonl': 'agent-model-pins.jsonl',
                               'transcripts.json': 'agent-model-pins.transcripts.json'}),
    'agent-payload': PAYLOAD_PROBE,
    'compaction-cut': CUT_PROBE,
    'explore-override': Probe(prepare_explore, collect_explore, assess_explore,
                              {'sightings.json': 'explore-override.sightings.json'}),
    'async-teardown': Probe(prepare_teardown, collect_teardown, assess_teardown,
                            {'teardown.jsonl': 'async-teardown.jsonl', 'teardown.log': 'async-teardown.log'}),
    'worktree-isolation': probe_worktrees.WORKTREE_PROBE,
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
    directory and the login name, and each other file scrubbed of the same,
    and of each one's JSON-escaped forms, since a side file is JSON text
    (owner, plan 58 decision D3). A stream keeps a Bash command only when
    the probe reads commands.'''
    probe, private = PROBE_RUNS[pid], private_strings()
    written = []
    for name, fixture in probe.fixtures.items():
        text = (run_dir / name).read_text(encoding='utf-8')
        if name.endswith('.jsonl'):
            events = probe_checks.parse_stream(text)
            if events is None:
                raise SetupError(f'{run_dir / name}: not a stream-json file')
            text = probe_checks.scrub_events(events, private, keep_commands=probe.reads_commands)
        else:
            text = probe_checks.redact(text, probe_checks.private_forms(private))
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
    unreadable output is ERROR, never a pass, and so is a run directory or
    a scratch directory that cannot be made.'''
    probe, scratch = PROBE_RUNS[pid], None
    try:
        run_dir.mkdir(parents=True, exist_ok=True)
        scratch = Path(tempfile.mkdtemp(prefix=f'cc-guide-probe-{pid}-')).resolve()
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
        if scratch is not None:
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
    '''A path as the log shows it, with ~ for the home directory, as given
    or resolved (R10.6).'''
    text = str(path)
    for home in (str(Path.home()), str(Path.home().resolve())):
        if text == home or text.startswith(home + os.sep):
            return '~' + text[len(home):]
    return text


def cell(text: str) -> str:
    '''Text as one table cell: whitespace collapsed, pipes escaped.'''
    return ' '.join(text.split()).replace('|', '\\|')


def public_finding(verdict: Verdict) -> str:
    '''The finding with each MCP tool name and each private string hidden
    (owner, plan 58 decision D3). The MCP pass runs first: a private string
    inside an MCP name would otherwise become <private>, and the pass would
    stop at its > and leave the rest of the name in the text.'''
    return probe_checks.redact(probe_checks.MCP_TOKEN_RE.sub(probe_checks.MCP_MARK, verdict.finding),
                               private_strings())


def log_row(day: date, version: str, claude: Path, pid: str, verdict: Verdict, allow_old: bool,
            remaps: Sequence[str] = ()) -> str:
    '''One log row. PROBES.md is committed to a public repo, and a finding can
    carry a home or temporary path, the login name or an MCP tool name, so
    the finding is scrubbed as a fixture is (public_finding), and the Binary
    cell, past its ~, is scrubbed of the same private strings. The Flags
    cell holds `--allow-old` when used, then the names of the alias remaps
    the run inherited (inherited_remaps).'''
    flags = [*(['--allow-old'] if allow_old else []), *remaps]
    binary = probe_checks.redact(shown_path(claude), private_strings())
    cells = [day.isoformat(), version, binary, pid, verdict.outcome, public_finding(verdict), ' '.join(flags)]
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
    log = tree.read(PROBES)
    if log is not None and not any(is_probe_header(line) for line in log.splitlines()):
        raise SetupError(f'{PROBES}: no probe log table, so every probe would read as due and a row could not be '
                         'appended: restore the header row naming the date, version, probe and outcome columns')
    rows = parse_probes(log)
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
    remaps = inherited_remaps()
    with term_as_exit():
        for pid in dict.fromkeys(chosen):
            run_dir = new_run_dir(cache / 'probes', f"{now.strftime('%Y%m%dT%H%M%S')}-{pid}")
            verdict = run_probe(pid, str(claude), repo, run_dir, execute)
            append_row(repo / PROBES, log_row(today, version, claude, pid, verdict, allow_old, remaps))
            outcomes.append(verdict.outcome)
            lines += [f'{pid}: {verdict.outcome}: {public_finding(verdict)}', f'  raw output: {run_dir}']
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


if __name__ == '__main__':
    if sys.argv[1:2] != ['drive-cut'] or len(sys.argv) != 3:
        sys.exit('usage: probes.py drive-cut <claude command line as a JSON list>')
    sys.exit(drive_cut(json.loads(sys.argv[2])))
