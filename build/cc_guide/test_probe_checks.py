'''Tests for probe_checks.py: each probe's PASS, DIVERGES and ERROR cases on
hand-built events shaped like the streams recorded while planning (Claude
Code 2.1.303, 2026-10-20), and the fixture scrubber (drift spec R10.2,
R10.5, R12.6).'''
import importlib.util
import json
import re
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


def saved(payloads, logged=None):
    '''payloads.json as collect_payload writes it: by default each hook
    logged one payload for each trimmed payload of its matcher.'''
    counts = {'any': sum(p['matcher'] == pc.ANY_MATCHER for p in payloads),
              'agent': sum(p['matcher'] == pc.GUARD_MATCHER for p in payloads)}
    return {'logged': counts if logged is None else logged, 'payloads': payloads}


def payload_run(served=None, requested=None):
    '''A parent on Sonnet that dispatches the haiku control and each pinned
    built-in in one message, as PAYLOAD_PROMPT asks, each forwarding one
    message from the model given for it. requested maps an agent type to
    the model its dispatch passes instead; None passes no model.'''
    served = {agent: 'claude-haiku-5-5' for agent in pc.PAYLOAD_AGENTS} | (served or {})
    requested = {pc.CONTROL_AGENT: pc.CONTROL_MODEL} | (requested or {})
    sent = [tool_use(f'toolu_{n}', 'Agent', subagent_type=agent, prompt='p',
                     **({'model': requested[agent]} if requested.get(agent) else {}))
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
    assert pc.assess_agent_payload(events, saved(payloads)) == verdict


def test_two_payloads_of_one_type_with_different_inputs_are_error():
    payloads = [*payload_log(), {**payload_log()[0], 'model': None}]
    verdict = pc.check_payloads(payloads)
    assert verdict.outcome == ERROR and 'general-purpose' in verdict.finding


def test_two_agent_matcher_payloads_of_one_type_with_different_models_are_error():
    log = payload_log()
    extra = {**next(p for p in log if p['matcher'] == pc.GUARD_MATCHER and p['subagent_type'] == 'claude-code-guide'),
             'model': 'sonnet'}
    verdict = pc.check_payloads([*log, extra])
    assert verdict.outcome == ERROR and 'claude-code-guide' in verdict.finding and pc.GUARD_MATCHER in verdict.finding


def test_a_control_model_normalised_to_a_full_id_passes():
    payloads = payload_log({pc.CONTROL_AGENT: {'model': 'claude-haiku-5-5'}})
    assert pc.check_payloads(payloads) is None


def test_the_model_checks_read_the_agent_matcher_payload():
    '''The guard installs on the Agent matcher, so its payload decides.'''
    payloads = [p if p['matcher'] == pc.ANY_MATCHER or p['subagent_type'] != pc.CONTROL_AGENT
                else {**p, 'model': None} for p in payload_log()]
    verdict = pc.check_payloads(payloads)
    assert verdict.outcome == DIVERGES and verdict.finding.startswith('the general-purpose dispatch passed model')
    builtin = [p if p['matcher'] == pc.ANY_MATCHER or p['subagent_type'] != 'claude-code-guide'
               else {**p, 'model': 'inherit'} for p in payload_log()]
    assert pc.check_payloads(builtin).outcome == DIVERGES


def test_a_control_served_two_haiku_ids_still_matches_a_builtin_served_one():
    served = {pc.CONTROL_AGENT: 'claude-haiku-5-5', 'claude-code-guide': 'claude-haiku-5-5'}
    events = payload_run(served)
    extra = assistant({'type': 'text', 'text': 'OK'}, parent='toolu_0', model='claude-haiku-4-5')
    events = [*events[:-1], extra, events[-1]]
    assert pc.assess_agent_payload(events, saved(payload_log())).outcome == PASS


def test_trim_block_keeps_a_dispatch_model():
    block = tool_use('toolu_1', 'Agent', subagent_type='general-purpose', model='haiku', prompt='x')
    assert pc._trim_block(block)['input'] == {'subagent_type': 'general-purpose', 'model': 'haiku'}


def test_a_parent_that_skips_the_control_model_is_error_not_diverges():
    '''A payload shows what the parent sent, so a control sent with no model
    is the parent's doing, not drift.'''
    payloads = payload_log({pc.CONTROL_AGENT: {'model': None,
                                               'input_keys': ['description', 'prompt', 'subagent_type']}})
    verdict = pc.assess_agent_payload(payload_run(requested={pc.CONTROL_AGENT: None}), saved(payloads))
    assert verdict.outcome == ERROR
    assert verdict.finding.startswith('the parent session sent general-purpose with no model')


def test_a_parent_that_gives_a_builtin_a_model_is_error():
    payloads = payload_log({'claude-code-guide': {'model': 'sonnet',
                                                  'input_keys': ['description', 'model', 'prompt', 'subagent_type']}})
    verdict = pc.assess_agent_payload(payload_run(requested={'claude-code-guide': 'sonnet'}), saved(payloads))
    assert verdict.outcome == ERROR
    assert verdict.finding.startswith("the parent session sent claude-code-guide with model 'sonnet'")


def test_an_empty_trimmed_log_names_the_stage_that_dropped_it():
    dropped = pc.assess_agent_payload(payload_run(), {'logged': {'any': 2, 'agent': 2}, 'payloads': []})
    assert dropped == (ERROR, 'the PreToolUse hooks logged 4 payloads, and trim_payload kept none of them (a '
                              'renamed subagent_type, a moved tool_input, or payloads that carry agent_id)')
    nothing = pc.assess_agent_payload(payload_run(), {'logged': {'any': 0, 'agent': 0}, 'payloads': []})
    assert nothing == (ERROR, 'the PreToolUse hooks logged no subagent dispatch')


def dispatched_twice(agent):
    '''payload_run's events with a second dispatch of `agent`, sent with the model the prompt asks for.'''
    events = payload_run()
    given = {'model': pc.CONTROL_MODEL} if agent == pc.CONTROL_AGENT else {}
    return [*events[:2], assistant(tool_use('toolu_9', 'Agent', subagent_type=agent, prompt='p', **given)),
            *events[2:]]


@pytest.mark.parametrize('events, finding', [
    (payload_run(requested={pc.CONTROL_AGENT: 'sonnet'}),
     "the parent session sent general-purpose with model 'sonnet', but its prompt asks for model 'haiku'"),
    # Any model on a built-in is the parent's choice, Haiku included: the prompt passes it none.
    (payload_run(requested={'claude-code-guide': 'haiku'}),
     "the parent session sent claude-code-guide with model 'haiku', but its prompt asks for no model"),
    (dispatched_twice(pc.CONTROL_AGENT),
     'the parent session dispatched general-purpose 2 times, but its prompt asks for one dispatch of each type'),
    (dispatched_twice('claude-code-guide'),
     'the parent session dispatched claude-code-guide 2 times, but its prompt asks for one dispatch of each type'),
])
def test_a_parent_that_strays_from_its_prompt_is_error(events, finding):
    assert pc.assess_agent_payload(events, saved(payload_log())) == (ERROR, finding)


def test_the_parent_is_read_after_a_broken_run_and_before_an_empty_log():
    stray = payload_run(requested={pc.CONTROL_AGENT: None})
    assert pc.assess_agent_payload(stray[:-1], saved(payload_log())) == (ERROR, 'no result event')
    assert pc.assess_agent_payload(stray, {'logged': {'any': 2, 'agent': 2}, 'payloads': []}) == (
        ERROR, "the parent session sent general-purpose with no model, but its prompt asks for model 'haiku'")


def test_an_empty_log_counts_every_hook_and_reads_no_counts_as_none():
    '''payloads.json without counts is what assess_payload reads for a missing file.'''
    one_hook = pc.assess_agent_payload(payload_run(), {'logged': {'any': 3, 'agent': 0}, 'payloads': []})
    assert one_hook.finding.startswith('the PreToolUse hooks logged 3 payloads, and trim_payload kept none')
    assert pc.assess_agent_payload(payload_run(), {}) == (ERROR, 'the PreToolUse hooks logged no subagent dispatch')


def test_requested_models_reads_the_main_session_calls_in_stream_order():
    '''Both dispatch tool names count, a call made inside a subagent does
    not, and a call that passes no model reads None.'''
    events = [init(), assistant(tool_use('toolu_1', 'Agent', subagent_type='general-purpose', model='haiku')),
              assistant(tool_use('toolu_2', 'Task', subagent_type='general-purpose'),
                        tool_use('toolu_3', 'Agent', subagent_type='claude-code-guide', model='opus')),
              assistant(tool_use('toolu_4', 'Agent', subagent_type='claude-code-guide', model='sonnet'),
                        parent='toolu_1'),
              assistant(tool_use('toolu_5', 'Read', file_path='a.py')), result()]
    assert pc.requested_models(events) == {'general-purpose': ['haiku', None], 'claude-code-guide': ['opus']}


def test_payload_file_counts_every_logged_line_and_sorts_what_trim_payload_keeps():
    def line(agent, **given):
        return json.dumps({'tool_name': 'Agent', 'tool_input': {'subagent_type': agent, **given}})
    raw = {'agent': [line('general-purpose', model='haiku'), line('claude-code-guide')],
           'any': [line('general-purpose', model='haiku'),
                   json.dumps({'tool_name': 'Read', 'tool_input': {'file_path': 'a.py'}}), line('claude-code-guide')]}
    saved_file = pc.payload_file(raw)
    assert saved_file['logged'] == {'agent': 2, 'any': 3}
    assert [(p['matcher'], p['subagent_type']) for p in saved_file['payloads']] == [
        ('*', 'claude-code-guide'), ('*', 'general-purpose'), ('Agent', 'claude-code-guide'),
        ('Agent', 'general-purpose')]


def without_type(events, agent):
    '''events with the parent's call of `agent` sent with no subagent_type.'''
    for e in events:
        for block in e.get('message', {}).get('content', []) if not e.get('parent_tool_use_id') else []:
            if block.get('type') == 'tool_use' and block['input'].get('subagent_type') == agent:
                del block['input']['subagent_type']
    return events


NEVER = 'the parent session never dispatched {}, but its prompt asks for one dispatch of each type'
CONTROL_ONLY = [init(), assistant(tool_use('toolu_0', 'Agent', subagent_type=pc.CONTROL_AGENT, model=pc.CONTROL_MODEL,
                                           prompt='p')),
                assistant({'type': 'text', 'text': 'OK'}, parent='toolu_0', model='claude-haiku-5-5'), result()]
NO_DISPATCH = [init(), assistant(tool_use('toolu_r', 'Read', file_path='a.py')), result()]


@pytest.mark.parametrize('events, payload_file, agent', [
    # The parent skips claude-code-guide: the hooks miss nothing, so the hook check must not take the blame.
    (CONTROL_ONLY, saved([p for p in payload_log() if p['subagent_type'] == pc.CONTROL_AGENT]), 'claude-code-guide'),
    # The control sent with no subagent_type: trim_payload drops its payloads, and the stream names no type.
    (without_type(payload_run(), pc.CONTROL_AGENT),
     saved([p for p in payload_log() if p['subagent_type'] != pc.CONTROL_AGENT], logged={'any': 2, 'agent': 2}),
     pc.CONTROL_AGENT),
    # The parent dispatches nothing and calls another tool, which the * hook logs: trim_payload is not to blame.
    (NO_DISPATCH, {'logged': {'any': 1, 'agent': 0}, 'payloads': []}, pc.CONTROL_AGENT),
])
def test_a_parent_that_never_dispatches_a_type_is_error_naming_the_parent(events, payload_file, agent):
    assert pc.assess_agent_payload(events, payload_file) == (ERROR, NEVER.format(agent))


def test_a_renamed_dispatch_tool_still_diverges_though_the_stream_shows_no_agent_call():
    '''A payload of the type counts as a dispatch, so a tool Claude Code
    renames is named as drift, not as a parent that never dispatched.'''
    events = payload_run()
    for block in events[1]['message']['content']:
        block['name'] = 'Delegate'
    payloads = [{**p, 'tool_name': 'Delegate'} for p in payload_log()]
    assert pc.requested_models(events) == {}
    assert pc.assess_agent_payload(events, saved(payloads)) == (
        DIVERGES, 'a subagent dispatch reaches PreToolUse as Delegate, not Agent')


def test_a_stray_model_is_named_before_a_missing_dispatch():
    events = [init(), assistant(tool_use('toolu_0', 'Agent', subagent_type=pc.CONTROL_AGENT, model='sonnet')),
              result()]
    assert pc.assess_agent_payload(events, saved([])) == (
        ERROR, "the parent session sent general-purpose with model 'sonnet', but its prompt asks for model 'haiku'")


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
    assert pc.DISPATCH_TOOLS[0] == pc.GUARDED_TOOL == pc.GUARD_MATCHER == guard.AGENT_TOOL
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


def test_cut_body_lines_carry_their_offsets():
    for kind, filler in pc.CUT_KINDS.items():
        body = pc.cut_body(kind)
        lines = body.splitlines(keepends=True)
        assert len(body) == 32000
        assert all(len(line) == 64 and line.endswith('\n') for line in lines)
        assert lines[300].startswith('@0019200 ')
        assert lines[1] == f'@0000064 {(filler * 6)[:54]}\n'


def test_measure_cut_reads_header_kept_body_and_tail():
    body = pc.cut_body('prose')
    text = 'Base directory for this skill: /x/cut-probe-prose\n\n' + body[:19950] + '\n[truncated: see /x/SKILL.md]'
    measure = pc.measure_cut(text, body)
    assert measure['header_chars'] == 51
    assert measure['body_chars_kept'] == 19950
    assert measure['total_chars'] == 20001
    assert measure['cut'] is True
    assert measure['frontmatter_seen'] is False
    assert measure['tail'].startswith('\n[truncated')


def test_measure_cut_sees_frontmatter_and_whole_bodies():
    measure = pc.measure_cut(pc.cut_frontmatter('digit') + pc.cut_body('digit'), pc.cut_body('digit'))
    assert measure['frontmatter_seen'] is True
    assert measure['cut'] is False


def test_measure_cut_returns_none_when_the_body_is_absent():
    '''A cut inside the body's first line leaves nothing to anchor on: not found, not a crash.'''
    body = pc.cut_body('prose')
    assert pc.measure_cut('Base directory for this skill: /x\n\n' + body[:30], body) is None


# The marker Claude Code 2.1.317 put after a re-attached skill's kept text (plan 87's spike, S2).
CUT_MARKER = '\n\n\n[... skill content truncated for compaction; use Read on the skill path if you need the full text]'


def test_measure_cut_leaves_a_trailing_newline_to_the_marker():
    '''The real cut kept 19,775 body characters, the last of them just before a line's newline. The marker opens with
    a newline, which matches the body's own, so a plain common prefix counts one more than was kept.'''
    assert len(CUT_MARKER) == 101
    body = pc.cut_body('prose')
    measure = pc.measure_cut('Base directory for this skill: /x\n\n' + body[:19775] + CUT_MARKER, body)
    assert measure['body_chars_kept'] == 19775
    assert measure['cut'] is True
    assert measure['tail'] == CUT_MARKER
    whole = pc.measure_cut(pc.cut_frontmatter('prose') + body, body)
    assert (whole['body_chars_kept'], whole['cut']) == (32000, False)


def invoked_skills(*copies):
    '''A transcript's invoked_skills attachment, shaped as plan 87's spike saw it (S1, S2).'''
    return {'type': 'attachment', 'attachment': {'type': 'invoked_skills', 'skills': [
        {'name': f'cut-probe-{kind}', 'path': f'projectSettings:cut-probe-{kind}', 'content': text}
        for kind, text in copies]}}


def test_reattached_after_boundary_reads_the_invoked_skills_after_the_last_boundary():
    '''Only the invoked_skills attachment after the last boundary holds the re-attached copies. The Skill call's own
    copy comes before every boundary, an earlier compaction's copy before the last one, and the skill listing, in an
    api-request-blob entry and a skill_listing attachment, names the skills and carries the frontmatter sentinel.'''
    whole = {kind: f'Base directory for this skill: /x/cut-probe-{kind}\n\n{pc.cut_body(kind)}'
             for kind in pc.CUT_KINDS}
    cut = {kind: text[:20000 - len(CUT_MARKER)] + CUT_MARKER for kind, text in whole.items()}
    boundary = {'type': 'system', 'subtype': 'compact_boundary'}
    listing = '\n'.join(f'- cut-probe-{kind}: Use when ... {pc.CUT_SENTINEL}' for kind in pc.CUT_KINDS)
    entries = [
        {'type': 'user', 'message': {'role': 'user', 'content': [{'type': 'text', 'text': whole['prose']}]}},
        boundary, invoked_skills(('prose', whole['prose'])),
        boundary, invoked_skills(('prose', cut['prose']), ('digit', cut['digit'])),
        {'type': 'attachment', 'attachment': {'type': 'skill_listing', 'content': listing}},
        {'type': 'api-request-blob', 'blob': {'system': listing, 'skills': [
            {'name': f'cut-probe-{kind}', 'content': whole[kind]} for kind in pc.CUT_KINDS]}},
    ]
    assert pc.reattached_after_boundary(entries, pc.CUT_KINDS) == cut
    assert pc.reattached_after_boundary(entries[:1], pc.CUT_KINDS) == {}


def cut_measure(kept, cut=True, frontmatter=False):
    '''A measure_cut result for a copy that keeps `kept` body characters after a 60-character header.'''
    return {'header_chars': 60, 'body_chars_kept': kept, 'total_chars': 60 + kept, 'cut': cut,
            'frontmatter_seen': frontmatter, 'tail': ''}


COMPACT_OK = [init(), {'type': 'system', 'subtype': 'compact_boundary'}, result()]


@pytest.mark.parametrize('compact, cut, verdict', [
    (COMPACT_OK, {'prose': cut_measure(20000), 'digit': cut_measure(20000)},
     (PASS, 'compaction kept 20000 body characters of the prose probe skill '
            '(by characters; 60 characters before the body), at least the register window 20000')),
    (COMPACT_OK, {'prose': cut_measure(19940), 'digit': cut_measure(19940)},
     (DIVERGES, 'compaction keeps 19940 body characters of the prose probe skill '
                '(by characters; 60 characters before the body), fewer than the register window 20000, '
                'so a body that passes compaction-window can lose its last 60')),
    # The digit skill tells characters from tokens: kept totals more than 5 apart mean the cut counts tokens.
    (COMPACT_OK, {'prose': cut_measure(21000), 'digit': cut_measure(14000)},
     (PASS, 'compaction kept 21000 body characters of the prose probe skill '
            '(by tokens; 60 characters before the body), at least the register window 20000')),
    (COMPACT_OK, {'prose': cut_measure(32000, cut=False), 'digit': cut_measure(32000, cut=False)},
     (PASS, 'compaction kept the whole 32000-character prose body; the register window 20000 is safe')),
    (COMPACT_OK, {'prose': cut_measure(20000, frontmatter=True), 'digit': cut_measure(20000)},
     (PASS, 'compaction kept 20000 body characters of the prose probe skill '
            '(by characters; 60 characters before the body, frontmatter included), at least the register window '
            '20000')),
    # The model invoked one skill, not both: ERROR naming the missing skill, never a PASS on the other.
    (COMPACT_OK, {'prose': cut_measure(20000)},
     (ERROR, 'no re-attached copy of cut-probe-digit after the compact boundary')),
    ([init(), result()], {'prose': cut_measure(20000), 'digit': cut_measure(20000)},
     (ERROR, 'the /compact run emitted no compact_boundary event')),
    (None, {'prose': cut_measure(20000), 'digit': cut_measure(20000)},
     (ERROR, 'the /compact run broke: no stream-json events')),
])
def test_assess_compaction_cut(compact, cut, verdict):
    assert pc.assess_compaction_cut(compact, cut, 20000) == verdict


# explore-override: the project agent named Explore, the control, their marks, and the canaries a run draws, fixed
# here. The two canaries share their hex part, as a fixed token_hex gives them, and differ by their prefixes.
EXPLORE, CONTROL = 'Explore', 'canary-control'
MARKS = {EXPLORE: 'EXPLORE-OVERRIDE', CONTROL: 'CANARY-CONTROL'}
CANARIES = {'claude_md': 'cm-0a1b2c3d', 'git_status': 'gs-0a1b2c3d'}
EXPLORE_IDS = {EXPLORE: 'toolu_e', CONTROL: 'toolu_c'}


def text(words):
    return {'type': 'text', 'text': words}


def answer(agent, claude_md=True, git_status=True, mark=True):
    '''An agent's three-line answer: its mark, or its name without the mark; the CLAUDE.md canary or NONE; and the
    untracked files its git status lists, or NONE.'''
    return '\n'.join([MARKS[agent] if mark else agent, CANARIES['claude_md'] if claude_md else 'NONE',
                      f"CLAUDE.md, canaries.json, {CANARIES['git_status']}.txt" if git_status else 'NONE'])


def explore_run(explore=None, control=None, prompt='Follow your instructions.', **given):
    '''A parent that dispatches the Explore override and the control in one message, each forwarding one message:
    explore's and control's blocks, by default the answers PASS expects. given adds fields to each Agent call.'''
    explore = explore or [text(answer(EXPLORE, git_status=False))]
    control = control or [text(answer(CONTROL))]
    sent = [tool_use(tid, 'Agent', subagent_type=agent, prompt=prompt, **given) for agent, tid in EXPLORE_IDS.items()]
    forwarded = [assistant(*explore, parent=EXPLORE_IDS[EXPLORE]), assistant(*control, parent=EXPLORE_IDS[CONTROL])]
    return [init(), assistant(*sent), *forwarded, assistant(text('DONE')), result()]


def sighting(explore=None, control=None, **fields):
    '''One rep's sightings as explore_sightings gives them, by default the rep PASS expects. explore and control
    replace fields of each agent's sightings, and fields replace the rep's own.'''
    seen = {EXPLORE: {'mark': True, 'claude_md': True, 'git_status': False, **(explore or {})},
            CONTROL: {'mark': True, 'claude_md': True, 'git_status': True, **(control or {})}}
    return {'broken': None, 'leaked': False, 'tool_calls': {EXPLORE: 0, CONTROL: 0}, 'seen': seen, **fields}


def test_explore_override_passes_when_explore_reads_claude_md_and_skips_git_status():
    assert pc.assess_explore_override([sighting() for _ in range(3)]) == (
        PASS, 'Explore override read CLAUDE.md and got no git-status snapshot in 3 of 3 reps; the control got both')


@pytest.mark.parametrize('explore, finding', [
    ({'git_status': True}, 'rep 2: the Explore override got a git-status snapshot'),
    ({'claude_md': False}, 'rep 2: the Explore override did not read CLAUDE.md'),
    ({'claude_md': False, 'git_status': True},
     'rep 2: the Explore override did not read CLAUDE.md and got a git-status snapshot'),
])
def test_explore_override_diverges_when_one_valid_rep_differs(explore, finding):
    assert pc.assess_explore_override([sighting(), sighting(explore), sighting()]) == (DIVERGES, finding)


def test_a_diverging_rep_outranks_a_void_one_and_each_diverging_rep_is_named():
    void = sighting(tool_calls={EXPLORE: 1, CONTROL: 0})
    assert pc.assess_explore_override([void, sighting(), sighting({'git_status': True})]) == (
        DIVERGES, 'rep 3: the Explore override got a git-status snapshot')
    assert pc.assess_explore_override([sighting({'claude_md': False}), sighting(), sighting({'git_status': True})]) == (
        DIVERGES, 'rep 1: the Explore override did not read CLAUDE.md; rep 3: the Explore override got a git-status '
                  'snapshot')


@pytest.mark.parametrize('agent', [EXPLORE, CONTROL])
@pytest.mark.parametrize('explore', [{}, {'git_status': True}])
def test_explore_override_voids_a_rep_whose_subagent_called_a_tool(agent, explore):
    '''A subagent that read a file may have found a canary there, not in its context, so the rep proves nothing:
    ERROR, whether its sightings would pass or diverge.'''
    rep = sighting(explore, tool_calls={EXPLORE: 0, CONTROL: 0, agent: 1})
    assert pc.assess_explore_override([rep, sighting(), sighting()]) == (
        ERROR, f'rep 1: {agent} made 1 tool call(s), so its answer may not come from its context alone')


@pytest.mark.parametrize('rep, why', [
    (sighting(control={'claude_md': False}), 'the control missed the CLAUDE.md canary'),
    (sighting(control={'git_status': False}), 'the control missed the git-status canary'),
    (sighting(control={'claude_md': False, 'git_status': False}), 'the control missed the CLAUDE.md and git-status '
                                                                    'canaries'),
    (sighting({'mark': False}), 'Explore did not give its mark EXPLORE-OVERRIDE'),
    # The built-in Explore answering in the override's place gives no mark, and its NONEs prove nothing.
    (sighting({'mark': False, 'claude_md': False}), 'Explore did not give its mark EXPLORE-OVERRIDE'),
    (sighting(control={'mark': False}), 'canary-control did not give its mark CANARY-CONTROL'),
    (sighting(leaked=True), 'the parent passed a canary in an Agent call'),
    (sighting({'git_status': True}, leaked=True), 'the parent passed a canary in an Agent call'),
    (sighting(broken='no result event'), 'the run broke: no result event'),
])
def test_explore_override_is_error_when_the_control_misses_a_canary_or_a_mark_is_absent(rep, why):
    assert pc.assess_explore_override([sighting(), rep, sighting()]) == (ERROR, f'rep 2: {why}')


def test_explore_override_names_every_void_rep():
    reps = [sighting(leaked=True), sighting(), sighting(broken='no init event')]
    assert pc.assess_explore_override(reps) == (
        ERROR, 'rep 1: the parent passed a canary in an Agent call; rep 3: the run broke: no init event')


@pytest.mark.parametrize('reps', [0, 2, 4])
def test_explore_override_needs_one_sighting_for_each_rep(reps):
    '''No sightings at all, as a missing sightings.json reads, must not pass for want of a diverging rep.'''
    assert pc.assess_explore_override([sighting() for _ in range(reps)]) == (ERROR, f'expected 3 reps, found {reps}')


def parent_echo():
    '''The parent loads CLAUDE.md and the git status too, so its own text can hold both canaries and both marks.'''
    events = explore_run(explore=[text(answer(EXPLORE, claude_md=False, git_status=False))])
    return [*events[:-1], assistant(text(' '.join([*CANARIES.values(), *MARKS.values()]))), events[-1]]


def split_answer():
    '''The Explore override's answer over two forwarded messages: the mark, then the CLAUDE.md canary.'''
    events = explore_run(explore=[text(MARKS[EXPLORE])])
    return [*events[:2], assistant(text(CANARIES['claude_md']), parent=EXPLORE_IDS[EXPLORE]), *events[2:]]


def never_dispatched(agent):
    '''The parent's call of `agent` dropped; the message forwarded under its id stays, matching no dispatch.'''
    events = explore_run()
    sent = [b for b in events[1]['message']['content'] if b['input']['subagent_type'] != agent]
    return [events[0], assistant(*sent), *events[2:]]


def leaked_into(agent, canary):
    '''explore_run's events with `canary` in the prompt of the parent's call of `agent` alone; the other call says
    only "Follow your instructions."'''
    events = explore_run()
    for block in events[1]['message']['content']:
        if block['input']['subagent_type'] == agent:
            block['input']['prompt'] += f' The word is {CANARIES[canary]}.'
    return events


NO_SIGHTING = {'mark': False, 'claude_md': False, 'git_status': False}


@pytest.mark.parametrize('events, expected', [
    (explore_run(), sighting()),
    (parent_echo(), sighting({'claude_md': False})),
    (split_answer(), sighting()),
    # A canary in any field of a parent's Agent call leaks.
    (explore_run(prompt=f"Follow your instructions. The word is {CANARIES['claude_md']}."), sighting(leaked=True)),
    (explore_run(description=f"{CANARIES['git_status']}.txt"), sighting(leaked=True)),
    # Each tool_use block in an agent's forwarded messages counts; the parent's own Agent calls do not.
    (explore_run(explore=[tool_use('toolu_r1', 'Read', file_path='CLAUDE.md'),
                          tool_use('toolu_r2', 'Read', file_path='canaries.json'),
                          text(answer(EXPLORE, git_status=False))]),
     sighting(tool_calls={EXPLORE: 2, CONTROL: 0})),
    (explore_run(control=[tool_use('toolu_r', 'Read', file_path='CLAUDE.md'), text(answer(CONTROL))]),
     sighting(tool_calls={EXPLORE: 0, CONTROL: 1})),
    # A mark is matched exactly: an agent's own name is not its mark.
    (explore_run(control=[text(answer(CONTROL, mark=False))]), sighting(control={'mark': False})),
    (explore_run(explore=[text(answer(EXPLORE, git_status=False, mark=False))]), sighting({'mark': False})),
    (never_dispatched(EXPLORE), sighting(NO_SIGHTING)),
    (never_dispatched(CONTROL), sighting(control=NO_SIGHTING)),
    (explore_run()[:-1], sighting(broken='no result event')),
    (None, sighting(NO_SIGHTING, NO_SIGHTING, broken='no stream-json events')),
    # A canary in one of the two Agent calls leaks, whichever call it is.
    (leaked_into(CONTROL, 'claude_md'), sighting(leaked=True)),
    (leaked_into(EXPLORE, 'git_status'), sighting(leaked=True)),
])
def test_explore_sightings_reads_marks_canaries_and_leaks_from_the_raw_stream(events, expected):
    assert pc.explore_sightings(events, CANARIES) == expected


TEARDOWN_PASS = 'the async SessionStart hook got TERM first at teardown and was gone within 5 s'
TEARDOWN_HUP = 'the async SessionStart hook got HUP first at teardown and was gone within 5 s'
NO_SIGNAL = 'the async SessionStart hook got none of TERM, HUP, INT at teardown'
NO_TRAP = ", so notice.sh's trap never runs"
NOTICE_SH = Path(__file__).resolve().with_name('notice.sh')


def hook_response(event, outcome):
    return {'type': 'system', 'subtype': 'hook_response', 'hook_event': event, 'hook_name': f'{event}:startup',
            'outcome': outcome}


def teardown_run(*outcomes, event='SessionStart'):
    return [init(), *[hook_response(event, o) for o in outcomes], assistant({'type': 'text', 'text': 'OK'}), result()]


def test_async_teardown_passes_on_term_then_gone():
    assert pc.assess_async_teardown(teardown_run(), ['start 41', 'TERM', 'gone']) == (PASS, TEARDOWN_PASS)


@pytest.mark.parametrize('log, finding', [
    # Another signal first.
    (['start 41', 'HUP', 'gone'], TEARDOWN_HUP),
    # No catchable signal, so notice.sh's trap never runs.
    (['start 41', 'gone'], f'{NO_SIGNAL} and was gone within 5 s{NO_TRAP}'),
    # The hook outlived teardown.
    (['start 41', 'TERM', 'alive'],
     'the async SessionStart hook got TERM first at teardown and was still running 5 s after claude -p ended'),
])
def test_async_teardown_diverges(log, finding):
    assert pc.assess_async_teardown(teardown_run(), log) == (DIVERGES, finding)


def test_async_teardown_is_error_when_the_hook_never_started():
    assert pc.assess_async_teardown(teardown_run(), []) == (ERROR, 'the async SessionStart hook never started')


def test_async_teardown_reads_a_cancelled_hook_response_when_the_stream_has_one():
    log = ['start 41', 'TERM', 'gone']
    assert pc.assess_async_teardown(teardown_run('cancelled'), log) == (PASS, TEARDOWN_PASS)
    assert pc.assess_async_teardown(teardown_run('success'), log) == (
        DIVERGES, f"{TEARDOWN_PASS}; the stream's SessionStart hook_response reads success, not cancelled")
    assert pc.assess_async_teardown(teardown_run(), log) == (PASS, TEARDOWN_PASS)


@pytest.mark.parametrize('log, verdict', [
    # TERM first decides, whatever comes after it; any other signal first diverges.
    (['start 41', 'TERM', 'HUP', 'INT', 'gone'], (PASS, TEARDOWN_PASS)),
    (['start 41', 'HUP', 'TERM', 'gone'], (DIVERGES, TEARDOWN_HUP)),
    (['start 41', 'INT', 'gone'],
     (DIVERGES, 'the async SessionStart hook got INT first at teardown and was gone within 5 s')),
    # No signal and still running: the finding names both.
    (['start 41', 'alive'], (DIVERGES, f'{NO_SIGNAL} and was still running 5 s after claude -p ended{NO_TRAP}')),
])
def test_async_teardown_reads_the_first_signal_and_how_the_hook_ended(log, verdict):
    assert pc.assess_async_teardown(teardown_run(), log) == verdict


@pytest.mark.parametrize('log, finding', [
    (['gone'], 'the async SessionStart hook never started'),
    (['TERM', 'gone'], 'the async SessionStart hook never started'),
    (['start', 'TERM', 'gone'], 'the async SessionStart hook never started'),
    (['start 41'], 'the teardown log does not end in gone or alive'),
    (['start 41', 'TERM'], 'the teardown log does not end in gone or alive'),
    # A second start line means the hook ran twice, so its signals cannot be told apart.
    (['start 41', 'start 42', 'TERM', 'gone'], "the teardown log holds 'start 42' between its start line and its end"),
])
def test_async_teardown_is_error_on_a_log_of_another_shape(log, finding):
    assert pc.assess_async_teardown(teardown_run(), log) == (ERROR, finding)


def test_async_teardown_reads_every_session_start_hook_response_and_no_other():
    log = ['start 41', 'TERM', 'gone']
    assert pc.assess_async_teardown(teardown_run('success', event='Stop'), log) == (PASS, TEARDOWN_PASS)
    assert pc.assess_async_teardown(teardown_run('cancelled', 'success'), log) == (
        DIVERGES, f"{TEARDOWN_PASS}; the stream's SessionStart hook_response reads success, not cancelled")


@pytest.mark.parametrize('events, why', [(None, 'no stream-json events'), (teardown_run()[:-1], 'no result event')])
def test_async_teardown_is_error_when_the_run_broke(events, why):
    assert pc.assess_async_teardown(events, ['start 41', 'TERM', 'gone']) == (ERROR, why)


def test_the_teardown_signals_are_the_ones_notice_sh_traps():
    assert pc.TEARDOWN_SIGNALS == ('TERM', 'HUP', 'INT')
    traps = re.findall(r"^\s*trap '[^']*' ([A-Z ]+?)\s*(?:#.*)?$", NOTICE_SH.read_text(encoding='utf-8'), re.MULTILINE)
    signals = [set(t.split()) for t in traps if t.strip() != 'EXIT']
    assert signals and all(s == set(pc.TEARDOWN_SIGNALS) for s in signals)


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


def test_scrub_keeps_the_compact_boundary_and_nothing_of_its_metadata():
    '''A recorded compaction-cut run replays only if its scrubbed stream keeps the boundary event (owner ruling,
    plan 87 D12). The event's metadata carries ids and token counts, which no assertion reads.'''
    ids = [f'00000000-0000-4000-8000-00000000000{n}' for n in range(1, 6)]
    boundary = {'type': 'system', 'subtype': 'compact_boundary', 'session_id': ids[0], 'uuid': ids[1],
                'compact_metadata': {'trigger': 'manual', 'pre_tokens': 41234},
                'preserved_segment': {'head_uuid': ids[2], 'anchor_uuid': ids[3]}, 'logical_parent_uuid': ids[4]}
    events = [init(), assistant(), result(), {'type': 'system', 'subtype': 'status', 'status': 'compacting'},
              init(), boundary, result()]
    kept = pc.parse_stream(pc.scrub_events(events, []))
    assert [e for e in kept if e.get('subtype') == 'compact_boundary'] == [
        {'type': 'system', 'subtype': 'compact_boundary'}]
    measure = cut_measure(19775)
    verdict = pc.assess_compaction_cut(kept, {'prose': measure, 'digit': measure}, 20000)
    assert verdict.outcome == DIVERGES
    assert verdict == pc.assess_compaction_cut(events, {'prose': measure, 'digit': measure}, 20000)


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
