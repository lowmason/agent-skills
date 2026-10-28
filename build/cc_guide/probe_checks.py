# cc-guide: subagents.frontmatter subagents.tools subagents.models hooks.events hooks.exit-codes hooks.patterns @2.1.306
'''The probe assertions (drift spec R10.2, R10.5): pure functions over a probe
run's raw stream-json events and the side files the run leaves, each giving
an outcome and a one-line finding. They read event fields, never the model's
prose. Tests replay them against streams recorded from our own probe runs
(R12.6), cut down and scrubbed by scrub_events before they are committed.

PASS means the behaviour matches the guide. DIVERGES means it does not.
ERROR means the probe's mechanism never fired or the run broke, and it is
never a pass.'''
import json
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
DISPATCH_TOOLS = ('Agent', 'Task')  # the subagent tool's name, and its older one
HAIKU_AGENTS = ('Explore', 'test-runner')
REVIEWER, REVIEWER_EFFORT = 'code-reviewer', 'xhigh'
PIN_AGENTS = (*HAIKU_AGENTS, REVIEWER)
# agent-payload: what hooks/dispatch-model-guard.py reads from a dispatch's PreToolUse payload. Its matcher and
# decide() take the tool's name, decide() reads tool_input's model and subagent_type, and it lets a model-less call
# through for the built-ins in its BUILTIN_PINNED. test_probe_checks.py holds these to the hook's own constants.
GUARDED_TOOL = 'Agent'  # the hook's AGENT_TOOL
HAIKU_BUILTINS = ('claude-code-guide',)  # the hook's BUILTIN_PINNED: plan 63 saw each run on Haiku with no model passed
CONTROL_AGENT, CONTROL_MODEL = 'general-purpose', 'haiku'  # dispatched beside them, passing its model
PAYLOAD_AGENTS = (CONTROL_AGENT, *HAIKU_BUILTINS)
ANY_MATCHER, GUARD_MATCHER = '*', 'Agent'  # the two logging hooks; the second is hooks/README.md's install matcher
SYNTHETIC = '<synthetic>'  # the model Claude Code records on a message it made itself, such as an API error
GUARD_MARKER = 'readonly-agent-guard:'
# hooks/probe-readonly-guard.sh's three checks: the command each asks for, and
# whether the guard must deny it.
GUARD_CHECKS = (('git status --porcelain', False), ('git fetch --dry-run origin', True),
                ('git config --global --list', True))
UUID_RE = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
TOOL_ID_RE = re.compile(r'toolu_[A-Za-z0-9]+')
MCP_PREFIX = 'mcp__'
MCP_MARK = '<mcp-tool>'
# A tool name that starts with the MCP prefix, up to white space, a quote or a closing bracket.
MCP_TOKEN_RE = re.compile(re.escape(MCP_PREFIX) + r'''[^\s'"`)\]}>]*''')
PRIVATE_MARK = '<private>'


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
        if not isinstance(event, dict):
            return None
        events.append(event)
    return events


def is_init(event: dict) -> bool:
    return event.get('type') == 'system' and event.get('subtype') == 'init'


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
    failed = next((r for r in results if r.get('is_error')), None)
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


def dispatches(events: list[dict]) -> dict[str, str]:
    '''The main session's subagent calls: tool-use id -> subagent type.'''
    out = {}
    for e in events:
        if e.get('type') != 'assistant' or e.get('parent_tool_use_id'):
            continue
        for block in (e.get('message') or {}).get('content') or []:
            if block.get('type') == 'tool_use' and block.get('name') in DISPATCH_TOOLS:
                out[block.get('id')] = (block.get('input') or {}).get('subagent_type')
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


def first_by_type(payloads: list[dict], matcher: str) -> dict[str, dict]:
    '''The first payload of each subagent type that the hook with this matcher logged.'''
    found: dict[str, dict] = {}
    for p in payloads:
        if p.get('matcher') == matcher:
            found.setdefault(p.get('subagent_type'), p)
    return found


def check_payloads(payloads: list[dict]) -> Verdict | None:
    '''The payload half of agent-payload: a verdict when the payloads decide
    one, else None. A dispatch that reaches PreToolUse under another tool
    name, or that the Agent matcher misses, never reaches the guard. A
    control payload without its model, or a model on a dispatch sent with
    none, changes what decide() reads.'''
    if not payloads:
        return Verdict(ERROR, 'the PreToolUse hooks logged no subagent dispatch')
    seen = first_by_type(payloads, ANY_MATCHER)
    renamed = sorted({str(p.get('tool_name')) for p in seen.values()} - {GUARDED_TOOL})
    if renamed:
        return Verdict(DIVERGES, f"a subagent dispatch reaches PreToolUse as {', '.join(renamed)}, not {GUARDED_TOOL}")
    for agent in PAYLOAD_AGENTS:
        if agent not in seen:
            return Verdict(ERROR, f'no PreToolUse payload dispatches {agent}')
    matched = first_by_type(payloads, GUARD_MATCHER)
    missed = [agent for agent in PAYLOAD_AGENTS if agent not in matched]
    if missed:
        return Verdict(DIVERGES, f"the {GUARD_MATCHER} matcher did not fire for {', '.join(missed)}")
    control = seen[CONTROL_AGENT]
    if control.get('model') != CONTROL_MODEL:
        keys = ', '.join(control.get('input_keys') or [])
        return Verdict(DIVERGES, f"the {CONTROL_AGENT} dispatch passed model {CONTROL_MODEL!r}, but its payload holds "
                                 f"model {control.get('model')!r} (tool_input keys: {keys})")
    for agent in HAIKU_BUILTINS:
        if seen[agent].get('model'):
            return Verdict(DIVERGES, f"a dispatch sent with no model ({agent}) arrives with model "
                                     f"{seen[agent]['model']!r}, so the guard would pass a model-less dispatch of "
                                     'any type')
    return None


def assess_agent_payload(events: list[dict] | None, payloads: list[dict]) -> Verdict:
    '''agent-payload: hooks/dispatch-model-guard.py's inputs stay as plan 63
    saw them on Claude Code 2.1.304. `payloads` holds the main session's
    dispatch payloads, cut by trim_payload, from two PreToolUse hooks: one
    matches every tool, the other matches Agent as the guard's install
    does. check_payloads reads them first, so a renamed tool is named
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
        elif served[agent] != served[CONTROL_AGENT]:
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


def _trim_block(block: dict) -> dict | None:
    kind = block.get('type')
    if kind == 'tool_use':
        kept = {k: v for k, v in (block.get('input') or {}).items() if k in ('subagent_type', 'command')}
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


def _trim_event(event: dict) -> dict | None:
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
    if kind == 'result':
        return {k: event.get(k) for k in ('type', 'subtype', 'is_error', 'num_turns')}
    if kind in ('assistant', 'user'):
        message = event.get('message') or {}
        content = message.get('content')
        blocks = [_trim_block(b) for b in content if isinstance(b, dict)] if isinstance(content, list) else []
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


def scrub_events(events: list[dict], private: list[str]) -> str:
    '''A recorded stream as a committable fixture (R12.6; owner, plan 58
    decision D3): cut to the fields the assertions read, so text blocks and
    tool output lose their text, and stripped of what must stay out of a
    public repo: MCP tool names leave the init tool list and become
    <mcp-tool> in a tool call and in a hook's name, each string in
    `private` (home and scratch paths, the login name), longest first,
    becomes <private>, and uuids and tool-use ids become stable
    placeholders.'''
    kept = [t for t in map(_trim_event, events) if t is not None]
    text = redact('\n'.join(json.dumps(e, ensure_ascii=False) for e in kept) + '\n', private)
    ids: dict[str, str] = {}
    text = TOOL_ID_RE.sub(lambda m: ids.setdefault(m.group(0), f'toolu_fixture{len(ids) + 1}'), text)
    uuids: dict[str, str] = {}
    return UUID_RE.sub(lambda m: uuids.setdefault(m.group(0), f'uuid-{len(uuids) + 1}'), text)
