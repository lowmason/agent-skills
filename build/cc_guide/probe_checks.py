# cc-guide: subagents.frontmatter subagents.tools subagents.models hooks.events hooks.exit-codes hooks.patterns @2.1.326
'''The probe assertions (drift spec R10.2, R10.5): pure functions over a probe
run's raw stream-json events and the side files the run leaves, each giving
an outcome and a one-line finding. They read event fields, never the model's
prose, with one exception: the explore-override probe reads the canary tokens
and marks that each subagent echoes from its own context, never free prose.
Tests replay them against streams recorded from our own probe runs
(R12.6), cut down and scrubbed by scrub_events before they are committed.

PASS means the behaviour matches the guide. DIVERGES means it does not.
ERROR means the probe's mechanism never fired or the run broke, and it is
never a pass.'''
import json
import os.path
import re
from typing import NamedTuple

from state import DIVERGES, ERROR, PASS

GREP_GLOB = frozenset({'Grep', 'Glob'})
WITH_BASH_TOOLS = frozenset({'Read', 'Bash'}) | GREP_GLOB
WITHOUT_BASH_TOOLS = frozenset({'Read'}) | GREP_GLOB
# The guide states the Grep and Glob rule for macOS, Linux and WSL (subagents.tools).
SUPPORTED_PLATFORMS = ('darwin', 'linux')
STOP_LOG = ['false', 'true', 'true']
STOP_EXITS = [2, 2, 0]
HAIKU_AGENTS = ('Explore', 'test-runner')
REVIEWER, REVIEWER_EFFORT = 'code-reviewer', 'xhigh'
PIN_AGENTS = (*HAIKU_AGENTS, REVIEWER)
# agent-payload: what hooks/dispatch-model-guard.py reads from a dispatch's PreToolUse payload. Its matcher and
# decide() take the tool's name, decide() reads tool_input's model and subagent_type, and it lets a model-less call
# through for the built-ins in its BUILTIN_PINNED. test_probe_checks.py holds these to the hook's own constants.
GUARDED_TOOL = 'Agent'  # the hook's AGENT_TOOL
DISPATCH_TOOLS = (GUARDED_TOOL, 'Task')  # the subagent tool's name, and its older one
HAIKU_BUILTINS = ('claude-code-guide',)  # the hook's BUILTIN_PINNED: plan 63 saw each run on Haiku with no model passed
CONTROL_AGENT, CONTROL_MODEL = 'general-purpose', 'haiku'  # dispatched beside them, passing its model
PAYLOAD_AGENTS = (CONTROL_AGENT, *HAIKU_BUILTINS)
ANY_MATCHER, GUARD_MATCHER = '*', GUARDED_TOOL  # the two logging hooks; the second is hooks/README.md's install matcher
PAYLOAD_LOGS = {'any': ANY_MATCHER, 'agent': GUARD_MATCHER}  # each hook's log folder -> its matcher
SYNTHETIC = '<synthetic>'  # the model Claude Code records on a message it made itself, such as an API error
GUARD_MARKER = 'readonly-agent-guard:'
# hooks/probe-readonly-guard.sh's three checks: the command each asks for, and
# whether the guard must deny it.
GUARD_CHECKS = (('git status --porcelain', False), ('git fetch --dry-run origin', True),
                ('git config --global --list', True))
ERROR_SUBTYPE_PREFIX = 'error'  # a result event's subtype for a run that ended in error, such as error_max_turns
UUID_RE = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
TOOL_ID_RE = re.compile(r'toolu_[A-Za-z0-9]+')
MCP_PREFIX = 'mcp__'
MCP_MARK = '<mcp-tool>'
# A tool name that starts with the MCP prefix, up to white space, a quote, a closing bracket or one of `,;:`.
MCP_TOKEN_RE = re.compile(re.escape(MCP_PREFIX) + r'''[^\s'"`)\]}>,;:]*''')
PRIVATE_MARK = '<private>'
# A scratch folder: tempfile.mkdtemp's prefix, cc-guide-probe-<probe id>-, then the eight characters it adds, from
# lowercase letters, digits and underscore. A probe id is lowercase words joined by hyphens, and several end in a word
# of eight letters (guard-liveness), so the id takes as much as leaves a suffix of exactly eight characters, and the
# name ends at one more character that a name cannot hold, so a path segment after it stays.
SCRATCH_MARK = '<scratch>'
SCRATCH_RE = re.compile(r'cc-guide-probe-[a-z]+(?:-[a-z]+)*-[a-z0-9_]{8}(?![A-Za-z0-9_])')
# compaction-cut: two probe skills whose bodies differ only in their filler. Text and digits split into tokens at
# different rates, so the two cuts tell a limit in characters from one in tokens. The names have the same
# length, so the two headers do too.
CUT_KINDS = {'prose': 'the cat sat on the mat while the dog ran past the gate ', 'digit': '0123456789'}
CUT_LINE_CHARS = 64  # a line's length with its newline
CUT_BODY_LINES = 500  # a 32,000-character body
CUT_SENTINEL = 'FRONTMATTER-SENTINEL'
CUT_TAIL_CHARS = 200
CUT_UNIT_SLACK = 5  # the most that two kinds' kept totals may differ by and still count in characters


class Verdict(NamedTuple):
    outcome: str
    finding: str


def parse_stream(text: str) -> list[dict] | None:
    '''A stream-json file's events, one JSON object a line. A line that does
    not open with `{` is stderr text the guard probe merges into its stream,
    and is skipped; one that opens with `{` but does not parse makes the
    whole stream None, so the run reads as broken.'''
    events = []
    for line in text.split('\n'):
        if not line.startswith('{'):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            return None
        events.append(event)
    return events


def is_init(event: dict) -> bool:
    return event.get('type') == 'system' and event.get('subtype') == 'init'


def is_error_result(event: dict) -> bool:
    '''Whether a result event reports an error: is_error is set, or its
    subtype names one, as `error_max_turns` does with is_error false.'''
    return bool(event.get('is_error')) or str(event.get('subtype')).startswith(ERROR_SUBTYPE_PREFIX)


def broken(events: list[dict] | None) -> str | None:
    '''Why a run broke, or None. A print-mode run that waits on background
    agents writes an init and a result event for each turn, so every result
    is read, not only the last line.'''
    if not events:
        return 'no stream-json events'
    if not any(map(is_init, events)):
        return 'no init event'
    results = [e for e in events if e.get('type') == 'result']
    if not results:
        return 'no result event'
    failed = next((r for r in results if is_error_result(r)), None)
    if failed is not None:
        return f"a result event is an error ({failed.get('subtype')})"
    return None


def init_tools(events: list[dict]) -> frozenset[str]:
    return frozenset(next(e for e in events if is_init(e)).get('tools') or [])


def assess_agent_tools(with_bash: list[dict] | None, without_bash: list[dict] | None, platform: str) -> Verdict:
    '''agent-tools: an agent that lists Bash gets neither Grep nor Glob, and
    one that lists them without Bash gets both, read from each run's init
    event. A run whose tool list is not its agent's, or a control that lists
    neither Grep nor Glob, is ERROR.'''
    if platform not in SUPPORTED_PLATFORMS:
        return Verdict(ERROR, f'the guide states this rule for macOS, Linux and WSL; this run is on {platform}')
    for name, events in (('with Bash', with_bash), ('without Bash', without_bash)):
        why = broken(events)
        if why:
            return Verdict(ERROR, f'the agent {name}: {why}')
    tools, control = init_tools(with_bash), init_tools(without_bash)
    if 'Bash' not in tools or not tools <= WITH_BASH_TOOLS:
        return Verdict(ERROR, f"the agent with Bash did not get its own tool list: {', '.join(sorted(tools))}")
    if 'Read' not in control or not control <= WITHOUT_BASH_TOOLS:
        return Verdict(ERROR, f"the control agent did not get its own tool list: {', '.join(sorted(control))}")
    if not control & GREP_GLOB:
        return Verdict(ERROR, 'the control agent lists neither Grep nor Glob')
    shown = f"with Bash: {', '.join(sorted(tools))}; without Bash: {', '.join(sorted(control))}"
    if tools & GREP_GLOB or not GREP_GLOB <= control:
        return Verdict(DIVERGES, shown)
    return Verdict(PASS, shown)


def assess_stop_continuation(events: list[dict] | None, log: list[str]) -> Verdict:
    '''stop-continuation: a Stop hook that blocks on its first two calls logs
    stop_hook_active as false, true, true, and the stream's Stop hook
    responses exit 2, 2 and 0. An empty log means the hook never ran.'''
    why = broken(events)
    if why:
        return Verdict(ERROR, why)
    if not log:
        return Verdict(ERROR, 'the Stop hook never logged a call')
    shown = f"stop_hook_active read {', '.join(log)}"
    if log != STOP_LOG:
        return Verdict(DIVERGES, shown)
    exits = [e.get('exit_code') for e in events if e.get('type') == 'system'
             and e.get('subtype') == 'hook_response' and e.get('hook_event') == 'Stop']
    if exits != STOP_EXITS:
        return Verdict(ERROR, f'{shown}, but the stream shows Stop hook exits {exits}')
    return Verdict(PASS, shown)


def dispatch_blocks(events: list[dict]) -> list[dict]:
    '''The main session's subagent calls, as tool_use blocks in stream order.'''
    return [block for e in events if e.get('type') == 'assistant' and not e.get('parent_tool_use_id')
            for block in (e.get('message') or {}).get('content') or []
            if block.get('type') == 'tool_use' and block.get('name') in DISPATCH_TOOLS]


def dispatches(events: list[dict]) -> dict[str, str]:
    '''The main session's subagent calls: tool-use id -> subagent type.'''
    return {block.get('id'): (block.get('input') or {}).get('subagent_type') for block in dispatch_blocks(events)}


def requested_models(events: list[dict]) -> dict[str, list[str | None]]:
    '''The main session's subagent calls: subagent type -> the model input of
    each call of that type, None for a call that passes none, in stream order.'''
    out: dict[str, list[str | None]] = {}
    for block in dispatch_blocks(events):
        given = block.get('input') or {}
        out.setdefault(given.get('subagent_type'), []).append(given.get('model'))
    return out


def forwarded_models(events: list[dict], ids: set[str]) -> set[str]:
    '''The models that served the forwarded messages of the given dispatches.'''
    return {(e.get('message') or {}).get('model') for e in events
            if e.get('type') == 'assistant' and e.get('parent_tool_use_id') in ids}


def assess_agent_model_pins(events: list[dict] | None, transcripts: dict[str, list[dict]]) -> Verdict:
    '''agent-model-pins: dispatched from an auto-mode parent, Explore and
    test-runner are served Haiku, and code-reviewer keeps `effort: xhigh`.
    Each subagent's model is read from its forwarded messages; its effort,
    which the stream lacks, from its transcript lines (R10.5). A message of
    model <synthetic>, in either, means an API error broke the run: ERROR.
    So does a forwarded message with no model, or a code-reviewer line with
    no effort: the transcript layout is undocumented, so a missing field is
    a broken mechanism, not a divergence. `transcripts` maps an agent type
    to its lines, each {'model': ..., 'effort': ...}.'''
    why = broken(events)
    if why:
        return Verdict(ERROR, why)
    sent = dispatches(events)
    models: dict[str, set[str]] = {}
    for agent in PIN_AGENTS:
        ids = {tid for tid, kind in sent.items() if kind == agent}
        if not ids:
            return Verdict(ERROR, f'{agent} was never dispatched')
        forwarded = forwarded_models(events, ids)
        if not forwarded:
            return Verdict(ERROR, f'{agent} forwarded no message')
        if not transcripts.get(agent):
            return Verdict(ERROR, f'no transcript lines for {agent}')
        if SYNTHETIC in forwarded | {line.get('model') for line in transcripts[agent]}:
            return Verdict(ERROR, f'{agent} hit an API error: a message from model {SYNTHETIC}')
        if None in forwarded:
            return Verdict(ERROR, f'{agent} forwarded a message with no model field')
        models[agent] = forwarded
    efforts = {line.get('effort') for line in transcripts[REVIEWER]}
    if None in efforts:
        return Verdict(ERROR, f'a {REVIEWER} transcript line has no effort field')
    wrong = [f"{agent} served {', '.join(sorted(map(str, models[agent])))}" for agent in HAIKU_AGENTS
             if not all('haiku' in str(m) for m in models[agent])]
    if efforts != {REVIEWER_EFFORT}:
        wrong.append(f"{REVIEWER} effort {', '.join(sorted(map(str, efforts)))}")
    if wrong:
        return Verdict(DIVERGES, '; '.join(wrong))
    served = ', '.join(sorted(models['Explore'] | models['test-runner']))
    return Verdict(PASS, f'Explore and test-runner served {served}; {REVIEWER} effort {REVIEWER_EFFORT}')


def trim_payload(payload, matcher: str) -> dict | None:
    '''A logged PreToolUse payload cut to what assess_agent_payload reads,
    tagged with the matcher of the hook that logged it. None for one it
    never reads: not an object, made inside a subagent (it carries
    agent_id), or dispatching no subagent. What is kept holds no path, id
    or prompt text, so the file needs no scrub to be committed (R12.6).'''
    if not isinstance(payload, dict) or 'agent_id' in payload:
        return None
    tool_input = payload.get('tool_input')
    if not isinstance(tool_input, dict) or 'subagent_type' not in tool_input:
        return None
    return {'matcher': matcher, 'tool_name': payload.get('tool_name'), 'input_keys': sorted(tool_input),
            'subagent_type': tool_input['subagent_type'], 'model': tool_input.get('model')}


def payload_file(raw: dict[str, list[str]]) -> dict:
    '''payloads.json, from each log folder's raw lines, one payload a line:
    how many payloads each hook logged, and the main session's dispatches
    cut by trim_payload, by matcher and then subagent type. The counts tell
    hooks that logged nothing from payloads that trim_payload dropped. A
    line that is not JSON raises ValueError.'''
    kept = [p for folder, lines in raw.items()
            for p in (trim_payload(json.loads(line), PAYLOAD_LOGS[folder]) for line in lines) if p is not None]
    kept.sort(key=lambda p: (p['matcher'], str(p['subagent_type'])))
    return {'logged': {folder: len(lines) for folder, lines in raw.items()}, 'payloads': kept}


def check_parent(events: list[dict]) -> Verdict | None:
    '''ERROR when the parent session did not send what probes.PAYLOAD_PROMPT
    asks: the control with model CONTROL_MODEL, each built-in in
    HAIKU_BUILTINS with no model, and each type once. A payload then holds
    the parent's choice, not Claude Code's, so the payload checks would
    report the parent as drift. None when the parent obeyed.'''
    sent = requested_models(events)
    for agent in PAYLOAD_AGENTS:
        models = sent.get(agent, [])
        if len(models) > 1:
            return Verdict(ERROR, f'the parent session dispatched {agent} {len(models)} times, but its prompt '
                                  'asks for one dispatch of each type')
        wanted = CONTROL_MODEL if agent == CONTROL_AGENT else None
        if models and models[0] != wanted:
            got = 'no model' if models[0] is None else f'model {models[0]!r}'
            asked = 'no model' if wanted is None else f'model {wanted!r}'
            return Verdict(ERROR, f'the parent session sent {agent} with {got}, but its prompt asks for {asked}')
    return None


def check_dispatched(events: list[dict], payloads: list[dict]) -> Verdict | None:
    '''ERROR when the parent session never dispatched a type in
    PAYLOAD_AGENTS: no main-session call of the stream names it, and no
    payload does. A payload counts, so a dispatch tool Claude Code renames,
    which the stream's calls no longer show, still reaches check_payloads
    as drift. None when each type was dispatched.'''
    sent = set(requested_models(events)) | {p.get('subagent_type') for p in payloads}
    for agent in PAYLOAD_AGENTS:
        if agent not in sent:
            return Verdict(ERROR, f'the parent session never dispatched {agent}, but its prompt asks for one '
                                  'dispatch of each type')
    return None


def by_type(payloads: list[dict], matcher: str) -> dict[str | None, list[dict]]:
    '''Each subagent type's payloads that the hook with this matcher logged, in order.'''
    found: dict[str | None, list[dict]] = {}
    for p in payloads:
        if p.get('matcher') == matcher:
            found.setdefault(p.get('subagent_type'), []).append(p)
    return found


def check_payloads(payloads: list[dict]) -> Verdict | None:
    '''The payload half of agent-payload: a verdict when the payloads decide
    one, else None. A dispatch that reaches PreToolUse under another tool
    name, or that the Agent matcher misses, never reaches the guard. Two
    payloads of one type with different models, under one matcher, leave no
    payload to read: ERROR. The model checks read the Agent matcher's
    payloads, the ones the guard gets. A control payload without a model,
    or a model on a dispatch sent with none, changes what decide() reads.
    check_parent has already shown that the parent sent those models.'''
    seen = by_type(payloads, ANY_MATCHER)
    renamed = sorted({str(p.get('tool_name')) for group in seen.values() for p in group} - {GUARDED_TOOL})
    if renamed:
        return Verdict(DIVERGES, f"a subagent dispatch reaches PreToolUse as {', '.join(renamed)}, not {GUARDED_TOOL}")
    for agent in PAYLOAD_AGENTS:
        if agent not in seen:
            return Verdict(ERROR, f'no PreToolUse payload dispatches {agent}')
    matched = by_type(payloads, GUARD_MATCHER)
    missed = [agent for agent in PAYLOAD_AGENTS if agent not in matched]
    if missed:
        return Verdict(DIVERGES, f"the {GUARD_MATCHER} matcher did not fire for {', '.join(missed)}")
    for matcher, groups in ((ANY_MATCHER, seen), (GUARD_MATCHER, matched)):
        for agent in PAYLOAD_AGENTS:
            models = {p.get('model') for p in groups[agent]}
            if len(models) > 1:
                return Verdict(ERROR, f'the {matcher} hook logged {len(groups[agent])} {agent} payloads with '
                                      f"different models ({', '.join(sorted(map(str, models)))}), so none is first")
    control = matched[CONTROL_AGENT][0]
    if not control.get('model'):
        keys = ', '.join(control.get('input_keys') or [])
        return Verdict(DIVERGES, f"the {CONTROL_AGENT} dispatch passed model {CONTROL_MODEL!r}, but its payload holds "
                                 f"model {control.get('model')!r} (tool_input keys: {keys})")
    for agent in HAIKU_BUILTINS:
        if matched[agent][0].get('model'):
            return Verdict(DIVERGES, f"a dispatch sent with no model ({agent}) arrives with model "
                                     f"{matched[agent][0]['model']!r}, so the guard would pass a model-less dispatch "
                                     'of any type')
    return None


def assess_agent_payload(events: list[dict] | None, payload_file: dict) -> Verdict:
    '''agent-payload: hooks/dispatch-model-guard.py's inputs stay as plan 63
    saw them on Claude Code 2.1.304. `payload_file` is payloads.json:
    `logged` counts the payloads each of two PreToolUse hooks logged, one
    matching every tool, the other matching Agent as the guard's install
    does, and `payloads` holds the main session's dispatch payloads among
    them, cut by trim_payload. check_parent reads the stream's Agent calls
    first, so a parent that did not send what its prompt asks is ERROR, not
    drift, and check_dispatched then names a type the parent never
    dispatched. An empty `payloads` is ERROR, named by whether the hooks
    logged anything. check_payloads reads them next, so a renamed tool is named
    before any message is looked for. Then each subagent's model is read
    from its forwarded messages. The control, which passes model haiku,
    must not be served the session model (the init event's), or a pin
    cannot be told from inheritance: ERROR. Each built-in in
    HAIKU_BUILTINS must be served neither the session model (it inherits,
    so its exemption lets the session model run) nor anything but what the
    control is served (its pin moved): DIVERGES. A model of <synthetic>, a
    message with no model and a dispatch with no forwarded message are
    ERROR, as in agent-model-pins.'''
    why = broken(events)
    if why:
        return Verdict(ERROR, why)
    payloads = payload_file.get('payloads') or []
    verdict = check_parent(events) or check_dispatched(events, payloads)
    if verdict:
        return verdict
    if not payloads:
        logged = sum((payload_file.get('logged') or {}).values())
        if logged:
            return Verdict(ERROR, f'the PreToolUse hooks logged {logged} payloads, and trim_payload kept none of '
                                  'them (a renamed subagent_type, a moved tool_input, or payloads that carry agent_id)')
        return Verdict(ERROR, 'the PreToolUse hooks logged no subagent dispatch')
    verdict = check_payloads(payloads)
    if verdict:
        return verdict
    session = next(e for e in events if is_init(e)).get('model')
    if not session:
        return Verdict(ERROR, 'the init event names no session model')
    sent = dispatches(events)
    served: dict[str, set[str]] = {}
    for agent in PAYLOAD_AGENTS:
        forwarded = forwarded_models(events, {tid for tid, kind in sent.items() if kind == agent})
        if not forwarded:
            return Verdict(ERROR, f'{agent} forwarded no message')
        if SYNTHETIC in forwarded:
            return Verdict(ERROR, f'{agent} hit an API error: a message from model {SYNTHETIC}')
        if None in forwarded:
            return Verdict(ERROR, f'{agent} forwarded a message with no model field')
        served[agent] = forwarded
    control = ', '.join(sorted(served[CONTROL_AGENT]))
    if session in served[CONTROL_AGENT]:
        return Verdict(ERROR, f'the {CONTROL_AGENT} control with model {CONTROL_MODEL} was served the session model '
                              f'{session}, so a pin cannot be told from it')
    wrong = []
    for agent in HAIKU_BUILTINS:
        if session in served[agent]:
            wrong.append(f'{agent} was served the session model {session}')
        elif not served[agent] <= served[CONTROL_AGENT]:
            wrong.append(f"{agent} was served {', '.join(sorted(served[agent]))}, not the {control} the "
                         f'{CONTROL_MODEL} control was served')
    if wrong:
        return Verdict(DIVERGES, '; '.join(wrong))
    return Verdict(PASS, f"dispatches reach PreToolUse as {GUARDED_TOOL}, with no model when unset; "
                         f"{', '.join(HAIKU_BUILTINS)} served {control}, as the {CONTROL_MODEL} control was")


def bash_calls(events: list[dict]) -> list[tuple[str, str]]:
    '''(tool-use id, command) for each Bash call in the stream.'''
    return [(block.get('id'), (block.get('input') or {}).get('command') or '')
            for e in events if e.get('type') == 'assistant'
            for block in (e.get('message') or {}).get('content') or []
            if block.get('type') == 'tool_use' and block.get('name') == 'Bash']


def result_body(block: dict) -> str:
    '''A tool_result block's text, whether its content is a string or a list of text blocks.'''
    body = block.get('content')
    if isinstance(body, list):
        return '\n'.join(b.get('text', '') for b in body if isinstance(b, dict))
    return str(body or '')


def tool_result_text(events: list[dict], tool_use_id: str) -> str | None:
    '''The text of a tool call's result, or None when the stream has none.'''
    for e in events:
        content = (e.get('message') or {}).get('content') if e.get('type') == 'user' else None
        for block in content if isinstance(content, list) else []:
            if (isinstance(block, dict) and block.get('type') == 'tool_result'
                    and block.get('tool_use_id') == tool_use_id):
                return result_body(block)
    return None


def tool_result_errors(events: list[dict], tool_use_ids: list[str]) -> list[bool]:
    '''Whether each result of the given tool calls is flagged is_error.'''
    return [bool(block.get('is_error')) for e in events if e.get('type') == 'user'
            for block in (e.get('message') or {}).get('content') or []
            if isinstance(block, dict) and block.get('type') == 'tool_result'
            and block.get('tool_use_id') in tool_use_ids]


def assess_guard_liveness(streams: list[list[dict] | None]) -> Verdict:
    '''guard-liveness: hooks/probe-readonly-guard.sh's three checks, read from
    the three streams it keeps. The read-only command must pass, and git
    fetch and git config --global must come back denied with the guard's
    marker on every attempt: a denied command that the agent then retries
    successfully was not denied. A check whose agent never ran its command is
    ERROR: the hook had nothing to judge. So is a read-only command whose
    result is an error without the marker: it failed for another reason, so
    the missing marker does not show that the guard let it through.'''
    if len(streams) != len(GUARD_CHECKS):
        return Verdict(ERROR, f'expected {len(GUARD_CHECKS)} streams, found {len(streams)}')
    failed = []
    for n, (events, (command, denied)) in enumerate(zip(streams, GUARD_CHECKS), start=1):
        why = broken(events)
        if why:
            return Verdict(ERROR, f'check {n}: {why}')
        calls = [tid for tid, cmd in bash_calls(events) if command in cmd]
        results = [tool_result_text(events, tid) for tid in calls]
        if not results or None in results:
            return Verdict(ERROR, f'check {n}: the agent never ran {command}, or its result is missing')
        marked = [GUARD_MARKER in r for r in results]
        if denied and not all(marked):
            failed.append(f'{command} was not denied')
        elif not denied and any(marked):
            failed.append(f'{command} was denied')
        elif not denied and any(tool_result_errors(events, calls)):
            return Verdict(ERROR, f'check {n}: {command} failed without the guard marker')
    if failed:
        return Verdict(DIVERGES, '; '.join(failed))
    return Verdict(PASS, 'git status passed; git fetch and git config --global were denied')


def cut_frontmatter(kind: str) -> str:
    return (f'---\nname: cut-probe-{kind}\n'
            f'description: Use when the compaction-cut probe asks for cut-probe-{kind}. {CUT_SENTINEL}\n---\n')


def cut_body(kind: str) -> str:
    '''CUT_BODY_LINES lines of CUT_LINE_CHARS characters each, newline
    included. A line is `@`, its offset in the body as seven digits and a
    space, then the kind's filler repeated and cut to fill the line, so a
    cut leaves a line that says where it fell.'''
    filler = CUT_KINDS[kind]
    lines = []
    for n in range(CUT_BODY_LINES):
        head = f'@{n * CUT_LINE_CHARS:07d} '
        room = CUT_LINE_CHARS - len(head) - 1
        lines.append(f'{head}{(filler * room)[:room]}\n')
    return ''.join(lines)


def measure_cut(text: str, body: str) -> dict | None:
    '''Where a re-attached skill text stops. `body`'s first line anchors the
    body's start, so a copy cut inside that line is not found: None. The
    header is what comes before the body, `body_chars_kept` how much of the
    body follows it unchanged, and `tail` what follows that: the cut's own
    marker, which the probe keeps to see how the cut is worded. The marker
    opens with a newline, which a body line's own newline at the cut can
    match, so a cut copy whose kept text ends with a newline leaves that
    newline to the tail: the count can be one low, never one high.'''
    start = text.find(body.split('\n', 1)[0])
    if start < 0:
        return None
    kept = len(os.path.commonprefix([text[start:start + len(body)], body]))
    cut = kept < len(body)
    if cut and body[kept - 1] == '\n':
        kept -= 1
    after = start + kept
    return {'header_chars': start, 'body_chars_kept': kept, 'total_chars': start + kept,
            'cut': cut, 'frontmatter_seen': CUT_SENTINEL in text,
            'tail': text[after:after + CUT_TAIL_CHARS]}


def reattached_after_boundary(entries: list[dict], kinds) -> dict[str, str]:
    '''The text of each kind's re-attached copy: the content of the
    cut-probe-<kind> item in an invoked_skills attachment after the last
    compact boundary. Nothing else counts. The Skill call's own copy comes
    before the boundary, and the skill listing after it, in an
    api-request-blob entry and in skill_listing attachments, names each
    skill and holds CUT_SENTINEL. A kind with no such item is absent, and
    so is every kind when the entries hold no boundary.'''
    bounds = [n for n, entry in enumerate(entries) if is_compact_boundary(entry)]
    copies: dict[str, str] = {}
    for entry in entries[bounds[-1] + 1:] if bounds else []:
        attachment = entry.get('attachment') if entry.get('type') == 'attachment' else None
        if not isinstance(attachment, dict) or attachment.get('type') != 'invoked_skills':
            continue
        for skill in attachment.get('skills') or []:
            if isinstance(skill, dict) and isinstance(skill.get('content'), str):
                copies.setdefault(skill.get('name'), skill['content'])
    return {kind: copies[f'cut-probe-{kind}'] for kind in kinds if f'cut-probe-{kind}' in copies}


def is_compact_boundary(event: dict) -> bool:
    return event.get('type') == 'system' and event.get('subtype') == 'compact_boundary'


def assess_compaction_cut(compact: list[dict] | None, cut: dict[str, dict] | None, window: int) -> Verdict:
    '''compaction-cut: where compaction cuts a re-attached skill, against
    the register's window (the compaction-window check's, in characters).
    The prose copy decides: it must keep at least `window` body characters,
    or a body that passes the register can lose its last ones. The digit
    copy only names the unit: kept totals (header and body) within
    CUT_UNIT_SLACK of each other mean the cut counts characters, else
    tokens. A /compact run with no boundary event, or a kind with no
    measured copy, is ERROR: the model invoked one skill, not both, or the
    copy is gone, and the other skill alone shows nothing.'''
    why = broken(compact)
    if why:
        return Verdict(ERROR, f'the /compact run broke: {why}')
    if not any(map(is_compact_boundary, compact)):
        return Verdict(ERROR, 'the /compact run emitted no compact_boundary event')
    measures = {kind: (cut or {}).get(kind) for kind in CUT_KINDS}
    for kind, measure in measures.items():
        if not measure:
            return Verdict(ERROR, f'no re-attached copy of cut-probe-{kind} after the compact boundary')
    prose, digit = measures['prose'], measures['digit']
    kept = prose['body_chars_kept']
    if not prose['cut']:
        return Verdict(PASS, f'compaction kept the whole {kept}-character prose body; '
                             f'the register window {window} is safe')
    unit = 'characters' if abs(prose['total_chars'] - digit['total_chars']) <= CUT_UNIT_SLACK else 'tokens'
    frontmatter = ', frontmatter included' if prose['frontmatter_seen'] else ''
    where = f"by {unit}; {prose['header_chars']} characters before the body{frontmatter}"
    seen = f'{kept} body characters of the prose probe skill ({where})'
    if kept < window:
        return Verdict(DIVERGES, f'compaction keeps {seen}, fewer than the register window {window}, so a body '
                                 f'that passes compaction-window can lose its last {window - kept}')
    return Verdict(PASS, f'compaction kept {seen}, at least the register window {window}')


# explore-override: a project agent named Explore, which overrides the built-in, and a custom control agent, each
# told to answer from its context alone with its mark, the CLAUDE.md canary word and the files its git status lists.
# A mark shows which definition served, and a canary, drawn per run, can reach an answer only through the agent's
# context (owner ruling B2, 2026-10-20; Stage 5 probe candidate (a)).
EXPLORE_AGENT, EXPLORE_MARK = 'Explore', 'EXPLORE-OVERRIDE'
CANARY_AGENT, CANARY_MARK = 'canary-control', 'CANARY-CONTROL'
EXPLORE_MARKS = {EXPLORE_AGENT: EXPLORE_MARK, CANARY_AGENT: CANARY_MARK}
EXPLORE_REPS = 3
# A CLI may have its subagents answer through a tool call, as SubagentHandback appears in the agent-model-pins
# recording (2.1.330). Such a call reads nothing, and its input holds the subagent's answer.
HANDBACK_TOOLS = frozenset({'SubagentHandback'})
HANDBACK_FIELD = 'message'
CANARY_NAMES = {'claude_md': 'CLAUDE.md', 'git_status': 'git-status'}  # canaries.json key -> its name in a finding


def spoken_text(block: dict) -> str:
    '''What a subagent's content block says: a text block's text, or the
    HANDBACK_FIELD of a HANDBACK_TOOLS call when that is a string.'''
    if block.get('type') == 'text':
        return str(block.get('text') or '')
    if block.get('type') == 'tool_use' and block.get('name') in HANDBACK_TOOLS:
        message = (block.get('input') or {}).get(HANDBACK_FIELD)
        return message if isinstance(message, str) else ''
    return ''


def reads_a_file(block: dict) -> bool:
    '''Whether a subagent's content block is a tool call that may read a file: any tool_use but a hand-back.'''
    return block.get('type') == 'tool_use' and block.get('name') not in HANDBACK_TOOLS


def explore_sightings(events: list[dict] | None, canaries: dict[str, str]) -> dict:
    '''One explore-override rep, read from its raw stream: why the run
    broke, or None; whether a canary leaked into an input of the parent's
    Agent calls; and, for each agent, how many tool_use blocks its forwarded
    messages hold and whether what it said holds its mark and each canary.
    A hand-back call (HANDBACK_TOOLS) is not counted, and its message is
    what the agent said, as its text blocks are. The parent loads CLAUDE.md
    and the git status too, so only the messages forwarded under a dispatch
    of that agent's type count. An agent the parent never dispatched has no
    text, so it sees nothing.'''
    stream = events or []
    leaked = any(value in json.dumps(block.get('input') or {}) for block in dispatch_blocks(stream)
                 for value in canaries.values())
    sent = dispatches(stream)
    tool_calls, seen = {}, {}
    for agent, mark in EXPLORE_MARKS.items():
        ids = {tid for tid, kind in sent.items() if kind == agent}
        blocks = [block for e in stream if e.get('type') == 'assistant' and e.get('parent_tool_use_id') in ids
                  for block in (e.get('message') or {}).get('content') or [] if isinstance(block, dict)]
        said = '\n'.join(filter(None, map(spoken_text, blocks)))
        tool_calls[agent] = sum(map(reads_a_file, blocks))
        seen[agent] = {'mark': mark in said, **{key: canaries[key] in said for key in CANARY_NAMES}}
    return {'broken': broken(events), 'leaked': leaked, 'tool_calls': tool_calls, 'seen': seen}


def explore_void(sighting: dict) -> str | None:
    '''Why a rep proves nothing, or None: the run broke, a canary leaked
    into the parent's Agent call, an agent called a tool other than a
    hand-back (it may have read the canary instead of being given it), an
    agent gave no mark (another definition served, or it ignored its
    instructions), or the control missed a canary, so a canary the override
    missed proves nothing.'''
    if sighting.get('broken'):
        return f"the run broke: {sighting['broken']}"
    if sighting.get('leaked'):
        return 'the parent passed a canary in an Agent call'
    calls, seen = sighting.get('tool_calls') or {}, sighting.get('seen') or {}
    for agent in EXPLORE_MARKS:
        if calls.get(agent):
            return f'{agent} made {calls[agent]} tool call(s), so its answer may not come from its context alone'
    for agent, mark in EXPLORE_MARKS.items():
        if not (seen.get(agent) or {}).get('mark'):
            return f'{agent} did not give its mark {mark}'
    missed = [name for key, name in CANARY_NAMES.items() if not seen[CANARY_AGENT].get(key)]
    if missed:
        return f"the control missed the {' and '.join(missed)} {'canary' if len(missed) == 1 else 'canaries'}"
    return None


def explore_differences(seen: dict) -> list[str]:
    '''How the override's sightings differ from what 2.1.304 showed:
    CLAUDE.md read, as custom agents read it, and no git-status snapshot,
    as the built-in gets none.'''
    return [*([] if seen.get('claude_md') else ['did not read CLAUDE.md']),
            *(['got a git-status snapshot'] if seen.get('git_status') else [])]


def assess_explore_override(sightings: list[dict]) -> Verdict:
    '''explore-override: in every rep the override reads CLAUDE.md and gets
    no git-status snapshot, while the control gets both. DIVERGES when a
    valid rep differs, naming each such rep; else ERROR when a rep is void
    (explore_void), naming each; else PASS. A count of sightings other than
    EXPLORE_REPS, none included, is ERROR, never a pass.'''
    if len(sightings) != EXPLORE_REPS:
        return Verdict(ERROR, f'expected {EXPLORE_REPS} reps, found {len(sightings)}')
    void, differ = [], []
    for n, sighting in enumerate(sightings, start=1):
        why = explore_void(sighting)
        if why:
            void.append(f'rep {n}: {why}')
            continue
        wrong = explore_differences(sighting['seen'][EXPLORE_AGENT])
        if wrong:
            differ.append(f"rep {n}: the Explore override {' and '.join(wrong)}")
    if differ:
        return Verdict(DIVERGES, '; '.join(differ))
    if void:
        return Verdict(ERROR, '; '.join(void))
    return Verdict(PASS, f'Explore override read CLAUDE.md and got no git-status snapshot in {EXPLORE_REPS} of '
                         f'{EXPLORE_REPS} reps; the control got both')


# async-teardown: an async SessionStart hook still running when claude -p ends, registered as notice.sh's refresh is.
# The refresh traps HUP, INT and TERM, so the signal claude sends such a hook first decides whether that trap runs
# (owner ruling on the G7 gap, 2026-10-20; Stage 5 probe candidate (b)). PASS encodes what 2.1.304 showed: TERM
# first, and the hook gone soon after.
TEARDOWN_SIGNALS = ('TERM', 'HUP', 'INT')  # the probe hook's traps, each of which only logs its name
TEARDOWN_FIRST = 'TERM'
TEARDOWN_WAIT = 5  # seconds probes.collect_teardown waits for the hook to go once claude -p has ended
TEARDOWN_START_RE = re.compile(r'start ([0-9]+)')  # the hook's first log line, with its pid
TEARDOWN_GONE, TEARDOWN_ALIVE = 'gone', 'alive'  # the line collect_teardown adds after its wait
TEARDOWN_LIFETIME = 120  # seconds the probe hook runs at most: its loop's one-second sleeps
TEARDOWN_EXPIRED = 'expired'  # the hook's last line when its lifetime ran out
CANCELLED = 'cancelled'  # the outcome claude -p finalizes such a hook with (guide, hooks.pitfalls)
NO_TRAP_RUNS = ", so notice.sh's trap never runs"  # a hook that got none of TEARDOWN_SIGNALS


def assess_async_teardown(events: list[dict] | None, log: list[str]) -> Verdict:
    '''async-teardown: the hook's log holds its start line, then each
    signal it got, in order, then gone or alive. PASS when TERM came first
    and the hook was gone within TEARDOWN_WAIT seconds, and no SessionStart
    hook_response in the stream has an outcome other than cancelled; a
    stream with none is no finding. A broken run, a log with no start line,
    and a log that holds another line or does not end in gone or alive are
    ERROR. A log that holds expired is ERROR before any other reading: the
    hook ended by itself, so the log shows nothing about claude's
    teardown.'''
    if TEARDOWN_EXPIRED in log:
        return Verdict(ERROR, f'the async SessionStart hook ran out its {TEARDOWN_LIFETIME} s lifetime before '
                              'claude -p ended, so its log shows nothing about teardown')
    why = broken(events)
    if why:
        return Verdict(ERROR, why)
    if not log or not TEARDOWN_START_RE.fullmatch(log[0]):
        return Verdict(ERROR, 'the async SessionStart hook never started')
    if log[-1] not in (TEARDOWN_GONE, TEARDOWN_ALIVE):
        return Verdict(ERROR, 'the teardown log does not end in gone or alive')
    signals, gone = log[1:-1], log[-1] == TEARDOWN_GONE
    stray = next((line for line in signals if line not in TEARDOWN_SIGNALS), None)
    if stray is not None:
        return Verdict(ERROR, f'the teardown log holds {stray!r} between its start line and its end')
    got = f'got {signals[0]} first' if signals else f"got none of {', '.join(TEARDOWN_SIGNALS)}"
    end = f'was gone within {TEARDOWN_WAIT} s' if gone else f'was still running {TEARDOWN_WAIT} s after claude -p ended'
    shown = f"the async SessionStart hook {got} at teardown and {end}{'' if signals else NO_TRAP_RUNS}"
    other = [e.get('outcome') for e in events if e.get('type') == 'system' and e.get('subtype') == 'hook_response'
             and e.get('hook_event') == 'SessionStart' and e.get('outcome') != CANCELLED]
    if other:
        shown += f"; the stream's SessionStart hook_response reads {' and '.join(map(str, other))}, not {CANCELLED}"
    if signals[:1] == [TEARDOWN_FIRST] and gone and not other:
        return Verdict(PASS, shown)
    return Verdict(DIVERGES, shown)


DISPATCH_INPUT_KEYS = ('subagent_type', 'model')  # the input fields the dispatch checks read
COMMAND_KEY = 'command'  # a Bash call's input field, which only assess_guard_liveness reads


def _trim_block(block: dict, keep_commands: bool = True) -> dict | None:
    kind = block.get('type')
    if kind == 'tool_use':
        keys = (*DISPATCH_INPUT_KEYS, COMMAND_KEY) if keep_commands else DISPATCH_INPUT_KEYS
        kept = {k: v for k, v in (block.get('input') or {}).items() if k in keys}
        name = block.get('name')
        if isinstance(name, str) and name.startswith(MCP_PREFIX):
            name = MCP_MARK  # a call to an MCP tool names a server the recording machine has installed
        return {'type': kind, 'id': block.get('id'), 'name': name, 'input': kept}
    if kind == 'tool_result':
        marked = [line for line in result_body(block).split('\n') if GUARD_MARKER in line]
        return {'type': kind, 'tool_use_id': block.get('tool_use_id'), 'is_error': block.get('is_error'),
                'content': '\n'.join(marked) if marked else '<output>'}
    if kind == 'text':
        return {'type': kind, 'text': '<text>'}
    return None


def _trim_event(event: dict, keep_commands: bool = True) -> dict | None:
    kind, sub = event.get('type'), event.get('subtype')
    if is_init(event):
        # An MCP tool's name names a server the recording machine has installed.
        tools = [t for t in event.get('tools') or [] if not t.startswith(MCP_PREFIX)]
        return {'type': kind, 'subtype': sub, 'tools': tools, 'model': event.get('model'),
                'claude_code_version': event.get('claude_code_version')}
    if kind == 'system' and sub == 'hook_response':
        kept = {k: event.get(k) for k in ('type', 'subtype', 'hook_event', 'hook_name', 'exit_code', 'outcome')}
        if isinstance(kept['hook_name'], str):
            # A hook's name carries what it matched, so a hook matched on an MCP tool names an installed server.
            kept['hook_name'] = MCP_TOKEN_RE.sub(MCP_MARK, kept['hook_name'])
        return kept
    if is_compact_boundary(event):
        # compaction-cut reads only that the boundary is there; its metadata holds ids and token counts (plan 87, D12).
        return {'type': kind, 'subtype': sub}
    if kind == 'result':
        return {k: event.get(k) for k in ('type', 'subtype', 'is_error', 'num_turns')}
    if kind in ('assistant', 'user'):
        message = event.get('message') or {}
        content = message.get('content')
        blocks = ([_trim_block(b, keep_commands) for b in content if isinstance(b, dict)]
                  if isinstance(content, list) else [])
        trimmed = {'content': [b for b in blocks if b]}
        if kind == 'assistant':
            trimmed['model'] = message.get('model')
        return {'type': kind, 'parent_tool_use_id': event.get('parent_tool_use_id'), 'message': trimmed}
    return None


def redact(text: str, private: list[str]) -> str:
    '''`text` with each string in `private` replaced by <private>, longest
    first, so a string that holds another is replaced whole. An empty string
    is skipped, since it matches between every two characters.'''
    for value in sorted(filter(None, private), key=len, reverse=True):
        text = text.replace(value, PRIVATE_MARK)
    return text


def json_escaped(value: str, *, ensure_ascii: bool = False) -> str:
    '''`value` as it reads inside a JSON string: a quote or a backslash gets a backslash before it, and with
    ensure_ascii, which json.dumps does by default, a non-ASCII character becomes a \\u escape.'''
    return json.dumps(value, ensure_ascii=ensure_ascii)[1:-1]


def private_forms(private: list[str]) -> list[str]:
    '''Each string in `private` as given and as it reads inside a JSON string written with ensure_ascii False and
    with True, so a value with a quote, a backslash or a non-ASCII character is found in either kind of file.'''
    return [form for value in private
            for form in (value, json_escaped(value), json_escaped(value, ensure_ascii=True))]


def scrub_events(events: list[dict], private: list[str], *, keep_commands: bool = True) -> str:
    '''A recorded stream as a committable fixture (R12.6; owner, plan 58
    decision D3): cut to the fields the assertions read, so text blocks and
    tool output lose their text, and stripped of what must stay out of a
    public repo: MCP tool names leave the init tool list and become
    <mcp-tool> in a tool call and in a hook's name, each string in
    `private` (home and scratch paths, the login name) and its forms inside
    a JSON string, longest first, becomes <private>, a scratch folder's
    name becomes <scratch>, and uuids and tool-use ids become stable
    placeholders. A Bash call keeps its command only with `keep_commands`,
    which a probe that reads commands sets (Probe.reads_commands).'''
    kept = [t for t in (_trim_event(e, keep_commands) for e in events) if t is not None]
    text = redact('\n'.join(json.dumps(e, ensure_ascii=False) for e in kept) + '\n', private_forms(private))
    text = SCRATCH_RE.sub(SCRATCH_MARK, text)
    ids: dict[str, str] = {}
    text = TOOL_ID_RE.sub(lambda m: ids.setdefault(m.group(0), f'toolu_fixture{len(ids) + 1}'), text)
    uuids: dict[str, str] = {}
    return UUID_RE.sub(lambda m: uuids.setdefault(m.group(0), f'uuid-{len(uuids) + 1}'), text)
