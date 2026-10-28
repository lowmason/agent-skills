'''Tests for probe_checks.py: each probe's PASS, DIVERGES and ERROR cases on
hand-built events shaped like the streams recorded while planning (Claude
Code 2.1.303, 2026-10-20), and the fixture scrubber (drift spec R10.2,
R10.5, R12.6).'''
import importlib.util
import json
from pathlib import Path

import pytest

import probe_checks as pc
from cc_fixtures import isolated_home  # noqa: F401
from state import DIVERGES, ERROR, PASS

GUARD = Path(__file__).resolve().parents[2] / 'hooks' / 'dispatch-model-guard.py'


def init(tools=('Read', 'Bash'), model='claude-sonnet-5-5'):
    return {'type': 'system', 'subtype': 'init', 'tools': list(tools), 'model': model, 'session_id': 's-1'}


def result(is_error=False):
    return {'type': 'result', 'subtype': 'error_during_execution' if is_error else 'success', 'is_error': is_error}


def assistant(*blocks, parent=None, model='claude-sonnet-5-5'):
    return {'type': 'assistant', 'parent_tool_use_id': parent, 'message': {'model': model, 'content': list(blocks)}}


def tool_use(tid, name, **given):
    return {'type': 'tool_use', 'id': tid, 'name': name, 'input': given}


def tool_result(tid, text, is_error=False, parent=None):
    return {'type': 'user', 'parent_tool_use_id': parent,
            'message': {'content': [{'type': 'tool_result', 'tool_use_id': tid, 'is_error': is_error,
                                     'content': [{'type': 'text', 'text': text}]}]}}


def stop_response(code):
    return {'type': 'system', 'subtype': 'hook_response', 'hook_event': 'Stop', 'hook_name': 'Stop',
            'exit_code': code, 'outcome': 'error' if code else 'success'}


def test_a_stream_skips_merged_stderr_text_and_a_bad_json_line_breaks_it():
    text = 'a warning on stderr\n' + json.dumps(init()) + '\n\n' + json.dumps(result()) + '\n'
    assert [e['type'] for e in pc.parse_stream(text)] == ['system', 'result']
    assert pc.parse_stream(json.dumps(init()) + '\n{"type": \n') is None
    assert pc.parse_stream('[1, 2]\n') == []


@pytest.mark.parametrize('events, why', [
    (None, 'no stream-json events'),
    ([], 'no stream-json events'),
    ([result()], 'no init event'),
    ([init()], 'no result event'),
    # A run that waits on background agents writes a result per turn; an error in any of them counts.
    ([init(), result(), init(), result(is_error=True)], 'a result event is an error (error_during_execution)'),
    ([init(), result(), init(), result()], None),
])
def test_a_run_is_broken_without_init_or_result_or_with_an_error_result(events, why):
    assert pc.broken(events) == why


def tools_run(*tools):
    return [init(tools), assistant({'type': 'text', 'text': 'OK'}), result()]


@pytest.mark.parametrize('with_bash, without_bash, platform, verdict', [
    (('Read', 'Bash'), ('Read', 'Grep', 'Glob'), 'darwin',
     (PASS, 'with Bash: Bash, Read; without Bash: Glob, Grep, Read')),
    (('Read', 'Grep', 'Glob', 'Bash'), ('Read', 'Grep', 'Glob'), 'linux',
     (DIVERGES, 'with Bash: Bash, Glob, Grep, Read; without Bash: Glob, Grep, Read')),
    (('Read', 'Bash'), ('Read', 'Grep'), 'darwin', (DIVERGES, 'with Bash: Bash, Read; without Bash: Grep, Read')),
    (('Read', 'Bash'), ('Read',), 'darwin', (ERROR, 'the control agent lists neither Grep nor Glob')),
    (('Read', 'Bash', 'Agent'), ('Read', 'Grep', 'Glob'), 'darwin',
     (ERROR, 'the agent with Bash did not get its own tool list: Agent, Bash, Read')),
    (('Read', 'Bash'), ('Read', 'Bash', 'Grep'), 'darwin',
     (ERROR, 'the control agent did not get its own tool list: Bash, Grep, Read')),
    (('Read', 'Bash'), ('Read', 'Grep', 'Glob'), 'win32',
     (ERROR, 'the guide states this rule for macOS, Linux and WSL; this run is on win32')),
])
def test_agent_tools(with_bash, without_bash, platform, verdict):
    assert pc.assess_agent_tools(tools_run(*with_bash), tools_run(*without_bash), platform) == verdict


def test_agent_tools_names_the_broken_run():
    assert pc.assess_agent_tools(tools_run('Read', 'Bash'), [init()], 'darwin') == (
        ERROR, 'the agent without Bash: no result event')


def stop_run(*codes):
    return [init(), *[stop_response(c) for c in codes], result()]


@pytest.mark.parametrize('events, log, verdict', [
    (stop_run(2, 2, 0), ['false', 'true', 'true'], (PASS, 'stop_hook_active read false, true, true')),
    (stop_run(2, 2, 0), ['false', 'false', 'true'], (DIVERGES, 'stop_hook_active read false, false, true')),
    (stop_run(2), ['false'], (DIVERGES, 'stop_hook_active read false')),
    (stop_run(2, 2, 0), ['missing', 'missing', 'missing'],
     (DIVERGES, 'stop_hook_active read missing, missing, missing')),
    (stop_run(), [], (ERROR, 'the Stop hook never logged a call')),
    (stop_run(), ['false', 'true', 'true'],
     (ERROR, 'stop_hook_active read false, true, true, but the stream shows Stop hook exits []')),
    ([init()], ['false', 'true', 'true'], (ERROR, 'no result event')),
])
def test_stop_continuation(events, log, verdict):
    assert pc.assess_stop_continuation(events, log) == verdict


def pins_run(models=None, drop=()):
    '''A parent that dispatches the three pinned agents, each forwarding one
    message from the model given for it.'''
    models = {'Explore': 'claude-haiku-5-5', 'test-runner': 'claude-haiku-5-5', 'code-reviewer': 'claude-opus-5-5',
              **(models or {})}
    sent = [tool_use(f'toolu_{n}', 'Agent', subagent_type=agent, prompt='p')
            for n, agent in enumerate(pc.PIN_AGENTS) if agent not in drop]
    forwarded = [assistant({'type': 'text', 'text': 'done'}, parent=f'toolu_{n}', model=models[agent])
                 for n, agent in enumerate(pc.PIN_AGENTS) if agent not in drop]
    return [init(), *[assistant(block) for block in sent], *forwarded, result(), init(), result()]


TRANSCRIPTS = {'Explore': [{'model': 'claude-haiku-5-5', 'effort': 'low'}],
               'test-runner': [{'model': 'claude-haiku-5-5', 'effort': 'low'}],
               'code-reviewer': [{'model': 'claude-opus-5-5', 'effort': 'xhigh'}] * 2}


@pytest.mark.parametrize('events, transcripts, verdict', [
    (pins_run(), TRANSCRIPTS,
     (PASS, 'Explore and test-runner served claude-haiku-5-5; code-reviewer effort xhigh')),
    (pins_run({'Explore': 'claude-sonnet-5-5'}), TRANSCRIPTS, (DIVERGES, 'Explore served claude-sonnet-5-5')),
    (pins_run(), {**TRANSCRIPTS, 'code-reviewer': [{'model': 'claude-opus-5-5', 'effort': 'low'}]},
     (DIVERGES, 'code-reviewer effort low')),
    (pins_run(drop=('test-runner',)), TRANSCRIPTS, (ERROR, 'test-runner was never dispatched')),
    (pins_run(), {k: v for k, v in TRANSCRIPTS.items() if k != 'Explore'}, (ERROR, 'no transcript lines for Explore')),
    (pins_run()[:-2] + [result(is_error=True)], TRANSCRIPTS,
     (ERROR, 'a result event is an error (error_during_execution)')),
    # Claude Code records a message it made itself, such as an API error, as model <synthetic>: the run broke.
    (pins_run(), {**TRANSCRIPTS, 'code-reviewer': [*TRANSCRIPTS['code-reviewer'], {'model': '<synthetic>'}]},
     (ERROR, 'code-reviewer hit an API error: a message from model <synthetic>')),
    (pins_run({'Explore': '<synthetic>'}), TRANSCRIPTS,
     (ERROR, 'Explore hit an API error: a message from model <synthetic>')),
    # A field missing from the undocumented transcript layout is a broken mechanism, never a divergence (R10.5).
    (pins_run({'Explore': None}), TRANSCRIPTS, (ERROR, 'Explore forwarded a message with no model field')),
    (pins_run(), {**TRANSCRIPTS, 'code-reviewer': [{'model': 'claude-opus-5-5'}]},
     (ERROR, 'a code-reviewer transcript line has no effort field')),
])
def test_agent_model_pins(events, transcripts, verdict):
    assert pc.assess_agent_model_pins(events, transcripts) == verdict


def test_agent_model_pins_needs_a_forwarded_message_for_each_agent():
    events = [e for e in pins_run() if e.get('parent_tool_use_id') != 'toolu_2']
    assert pc.assess_agent_model_pins(events, TRANSCRIPTS) == (ERROR, 'code-reviewer forwarded no message')


def payload_log(changes=None):
    '''Both logging hooks' trimmed payloads for the control and each pinned
    built-in, as collect_payload writes them; changes maps an agent type to
    the fields that replace its payloads'.'''
    log = []
    for matcher in (pc.ANY_MATCHER, pc.GUARD_MATCHER):
        for agent in pc.PAYLOAD_AGENTS:
            model = pc.CONTROL_MODEL if agent == pc.CONTROL_AGENT else None
            keys = sorted(['description', 'prompt', 'subagent_type', *(['model'] if model else [])])
            log.append({'matcher': matcher, 'tool_name': 'Agent', 'input_keys': keys, 'subagent_type': agent,
                        'model': model, **(changes or {}).get(agent, {})})
    return log


def payload_run(served=None):
    '''A parent on Sonnet that dispatches the haiku control and each pinned
    built-in in one message, each forwarding one message from the model
    given for it.'''
    served = {agent: 'claude-haiku-5-5' for agent in pc.PAYLOAD_AGENTS} | (served or {})
    sent = [tool_use(f'toolu_{n}', 'Agent', subagent_type=agent, prompt='p')
            for n, agent in enumerate(pc.PAYLOAD_AGENTS)]
    forwarded = [assistant({'type': 'text', 'text': 'OK'}, parent=f'toolu_{n}', model=served[agent])
                 for n, agent in enumerate(pc.PAYLOAD_AGENTS)]
    return [init(), assistant(*sent), *forwarded, result()]


@pytest.mark.parametrize('events, payloads, verdict', [
    (payload_run(), payload_log(),
     (PASS, 'dispatches reach PreToolUse as Agent, with no model when unset; claude-code-guide served '
            'claude-haiku-5-5, as the haiku control was')),
    # A renamed tool still reaches the hook that matches every tool, so the rename is named, not an ERROR.
    (payload_run(), [{**p, 'tool_name': 'Task'} for p in payload_log()],
     (DIVERGES, 'a subagent dispatch reaches PreToolUse as Task, not Agent')),
    (payload_run(), [p for p in payload_log() if p['subagent_type'] != 'claude-code-guide'],
     (ERROR, 'no PreToolUse payload dispatches claude-code-guide')),
    (payload_run(), [p for p in payload_log() if p['matcher'] != pc.GUARD_MATCHER],
     (DIVERGES, 'the Agent matcher did not fire for general-purpose, claude-code-guide')),
    (payload_run(), payload_log({'general-purpose': {
        'model': None, 'input_keys': ['description', 'model_name', 'prompt', 'subagent_type']}}),
     (DIVERGES, "the general-purpose dispatch passed model 'haiku', but its payload holds model None "
                '(tool_input keys: description, model_name, prompt, subagent_type)')),
    # The guard reads tool_input.get('model'): a value on a dispatch sent without one lets every such call through.
    (payload_run(), payload_log({'claude-code-guide': {'model': 'inherit'}}),
     (DIVERGES, "a dispatch sent with no model (claude-code-guide) arrives with model 'inherit', so the guard "
                'would pass a model-less dispatch of any type')),
    (payload_run()[:-1], payload_log(), (ERROR, 'no result event')),
    (payload_run(), [], (ERROR, 'the PreToolUse hooks logged no subagent dispatch')),
    ([init(model=None), *payload_run()[1:]], payload_log(), (ERROR, 'the init event names no session model')),
    ([e for e in payload_run() if e.get('parent_tool_use_id') != 'toolu_1'], payload_log(),
     (ERROR, 'claude-code-guide forwarded no message')),
    (payload_run({'claude-code-guide': '<synthetic>'}), payload_log(),
     (ERROR, 'claude-code-guide hit an API error: a message from model <synthetic>')),
    (payload_run({'general-purpose': None}), payload_log(),
     (ERROR, 'general-purpose forwarded a message with no model field')),
    # Under a remap that sends haiku to the session model, a pin and inheritance look the same.
    (payload_run({'general-purpose': 'claude-sonnet-5-5'}), payload_log(),
     (ERROR, 'the general-purpose control with model haiku was served the session model claude-sonnet-5-5, '
             'so a pin cannot be told from it')),
    (payload_run({'claude-code-guide': 'claude-sonnet-5-5'}), payload_log(),
     (DIVERGES, 'claude-code-guide was served the session model claude-sonnet-5-5')),
    # A pin that moves off Haiku also breaks the guard's purpose: an exempt built-in on Opus runs a tier nobody chose.
    (payload_run({'claude-code-guide': 'claude-opus-5-5'}), payload_log(),
     (DIVERGES, 'claude-code-guide was served claude-opus-5-5, not the claude-haiku-5-5 the haiku control was '
                'served')),
])
def test_agent_payload(events, payloads, verdict):
    assert pc.assess_agent_payload(events, payloads) == verdict


def test_trim_payload_keeps_a_main_session_dispatch_and_drops_the_rest():
    '''The kept fields hold no path, id or prompt text, so payloads.json is
    committed as save_fixtures copies it, with no scrub of its own.'''
    main = {'session_id': '364e6342-a957-4e26-a308-caa9e4b4bc69', 'cwd': '/private/tmp/cc-guide-probe-x',
            'transcript_path': '/Users/someone/.claude/projects/x/364e6342.jsonl', 'hook_event_name': 'PreToolUse',
            'tool_name': 'Agent', 'tool_use_id': 'toolu_01AbC',
            'tool_input': {'description': 'd', 'prompt': 'List /Users/someone', 'subagent_type': 'claude-code-guide',
                           'run_in_background': False}}
    kept = pc.trim_payload(main, '*')
    assert kept == {'matcher': '*', 'tool_name': 'Agent', 'subagent_type': 'claude-code-guide', 'model': None,
                    'input_keys': ['description', 'prompt', 'run_in_background', 'subagent_type']}
    for leak in ('364e6342', '/private/', '/Users/', 'toolu_', 'List'):
        assert leak not in json.dumps(kept)
    assert pc.trim_payload({**main, 'agent_id': 'a5287d9d575e'}, '*') is None  # made inside a subagent
    assert pc.trim_payload({**main, 'tool_name': 'Read', 'tool_input': {'file_path': '/Users/someone/a'}}, '*') is None
    assert pc.trim_payload({**main, 'tool_input': 'not an object'}, '*') is None
    assert pc.trim_payload(['not', 'a', 'payload'], '*') is None


def test_the_payload_probe_checks_what_the_dispatch_guard_reads():
    '''The guard's tool name and its pinned built-ins, loaded as
    check_frontmatter.load_pinned_roster loads its roster. A built-in added
    to BUILTIN_PINNED needs a dispatch in this probe as well.'''
    spec = importlib.util.spec_from_file_location('dispatch_model_guard', GUARD)
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    assert guard.AGENT_TOOL == pc.GUARDED_TOOL == pc.GUARD_MATCHER
    assert guard.BUILTIN_PINNED == frozenset(pc.HAIKU_BUILTINS)


DENIAL = 'PreToolUse:Bash hook error: readonly-agent-guard: the Explore agent is read-only on this checkout'


def guard_run(command, output, model='claude-haiku-5-5', failed=False):
    return [init(('Read', 'Bash'), model), assistant(tool_use('toolu_g', 'Bash', command=command)),
            tool_result('toolu_g', output, is_error=failed or pc.GUARD_MARKER in output), result()]


def guard_streams(first='(Bash completed with no output)', second=DENIAL, third=DENIAL):
    return [guard_run(cmd, out) for (cmd, _), out in zip(pc.GUARD_CHECKS, (first, second, third))]


def retried_fetch():
    '''The agent runs git fetch twice: the guard denies the first, and the second runs.'''
    command = 'git fetch --dry-run origin'
    return [init(('Read', 'Bash')), assistant(tool_use('toolu_g1', 'Bash', command=command)),
            tool_result('toolu_g1', DENIAL, is_error=True), assistant(tool_use('toolu_g2', 'Bash', command=command)),
            tool_result('toolu_g2', 'Would fetch from origin'), result()]


@pytest.mark.parametrize('streams, verdict', [
    (guard_streams(), (PASS, 'git status passed; git fetch and git config --global were denied')),
    (guard_streams(second='Would fetch from origin'), (DIVERGES, 'git fetch --dry-run origin was not denied')),
    (guard_streams(first=DENIAL, third='user.name=x'),
     (DIVERGES, 'git status --porcelain was denied; git config --global --list was not denied')),
    (guard_streams()[:2], (ERROR, 'expected 3 streams, found 2')),
    ([*guard_streams()[:2], None], (ERROR, 'check 3: no stream-json events')),
    ([*guard_streams()[:2], [init(), assistant({'type': 'text', 'text': 'I will not run that.'}), result()]],
     (ERROR, 'check 3: the agent never ran git config --global --list, or its result is missing')),
    # A control that fails with no guard marker proves nothing about the guard: ERROR, never a pass.
    ([guard_run('git status --porcelain', 'Permission denied', failed=True), *guard_streams()[1:]],
     (ERROR, 'check 1: git status --porcelain failed without the guard marker')),
    # A denied fetch that the agent then retries successfully was not denied.
    ([guard_streams()[0], retried_fetch(), guard_streams()[2]],
     (DIVERGES, 'git fetch --dry-run origin was not denied')),
])
def test_guard_liveness(streams, verdict):
    assert pc.assess_guard_liveness(streams) == verdict


def test_redact_replaces_the_longest_string_first_and_skips_an_empty_one():
    # Shortest first would leave '<private>/work' for the first path.
    assert pc.redact('/home/me/work and /home/me', ['/home/me', '/home/me/work', '']) == '<private> and <private>'
    assert pc.redact('abc', ['']) == 'abc'


def test_scrub_masks_an_mcp_tool_name_in_a_hook_name():
    '''A PreToolUse hook with an mcp__ matcher in the owner's user settings
    is named for the tool it matched, which names an installed server.'''
    hook = {'type': 'system', 'subtype': 'hook_response', 'hook_event': 'PreToolUse',
            'hook_name': 'PreToolUse:mcp__mine__search', 'exit_code': 0, 'outcome': 'success'}
    text = pc.scrub_events([init(), hook, result()], [])
    assert 'mcp__' not in text and 'mine' not in text
    assert pc.parse_stream(text)[1]['hook_name'] == f'PreToolUse:{pc.MCP_MARK}'


def test_scrub_keeps_what_the_assertions_read_and_drops_private_text():
    home, scratch = '/Users/someone', '/private/var/folders/xy/T/cc-guide-probe-pins-abc'
    events = [
        {**init(('Read', 'Bash', 'mcp__mine__search')), 'cwd': scratch, 'memory_paths': [f'{home}/.claude'],
         'mcp_servers': [{'name': 'mine'}], 'session_id': '364e6342-a957-4e26-a308-caa9e4b4bc69', 'plugins': ['x']},
        {'type': 'system', 'subtype': 'task_started', 'prompt': f'List {scratch}'},
        assistant(tool_use('toolu_01AbC', 'Agent', subagent_type='Explore', prompt=f'List {scratch}')),
        assistant({'type': 'text', 'text': f'{home} holds secrets'}, parent='toolu_01AbC', model='claude-haiku-5-5'),
        tool_result('toolu_01AbC', f'drwx someone staff {scratch}/a.py'),
        tool_result('toolu_02', DENIAL + f'\nsee {home}/x', is_error=True),
        assistant(tool_use('toolu_03', 'mcp__mine__search', query='x')),
        stop_response(2),
        {**result(), 'total_cost_usd': 0.2, 'modelUsage': {}, 'session_id': '364e6342-a957-4e26-a308-caa9e4b4bc69'},
    ]
    text = pc.scrub_events(events, [home, scratch, 'someone'])
    for leak in (home, scratch, 'someone', '364e6342', 'toolu_01AbC', 'mine', 'mcp__', 'secrets', 'List'):
        assert leak not in text
    kept = pc.parse_stream(text)
    assert [e.get('subtype', e['type']) for e in kept] == [
        'init', 'assistant', 'assistant', 'user', 'user', 'assistant', 'hook_response', 'success']
    assert kept[0] == {'type': 'system', 'subtype': 'init', 'tools': ['Read', 'Bash'], 'model': 'claude-sonnet-5-5',
                       'claude_code_version': None}
    assert pc.dispatches(kept) == {'toolu_fixture1': 'Explore'}
    assert pc.forwarded_models(kept, {'toolu_fixture1'}) == {'claude-haiku-5-5'}
    assert pc.tool_result_text(kept, 'toolu_fixture2') == DENIAL
    assert pc.tool_result_text(kept, 'toolu_fixture1') == '<output>'
