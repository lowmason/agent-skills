'''R12.6: each probe's assertion replayed against the streams recorded from
our own probe runs, kept under probe_streams/ after save_fixtures cut them
down and scrubbed them. The recorded run passes; the same run with the
observed behaviour changed diverges; and a run whose mechanism never fired
is ERROR. No fixture may hold a path or an id from the machine it was
recorded on (owner, plan 58 decision D3).'''
import json
import re
from pathlib import Path

import pytest

import probe_checks
import probes
from cc_fixtures import isolated_home  # noqa: F401
from state import DIVERGES, ERROR, MANIFEST, PASS, parse_manifest, parse_probes

REPO = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / 'probe_streams'
PROBES_LOG = Path(__file__).resolve().parent / 'PROBES.md'
LOG_ROW_RE = re.compile(r'^\| \d{4}-\d{2}-\d{2} \|', re.MULTILINE)
# A message id and a request id (msg_, req_) are the API's, and a raw stream carries them as it does a tool-use id.
PRIVATE_RE = re.compile(r'/Users/|/home/|/private/|/var/folders/|/tmp/|toolu_0|msg_|req_|mcp__|'
                        r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


def replay(pid: str, changes: dict[str, str] | None = None):
    '''The probe's verdict on its fixtures, with some fixture texts replaced.'''
    probe = probes.PROBE_RUNS[pid]
    read = probes.reader(FIXTURES, probe.fixtures)
    return probe.assess(lambda name: (changes or {}).get(name, read(name)))


def edited(pid: str, name: str, edit) -> dict[str, str]:
    '''A fixture stream with `edit` applied to each event.'''
    text = (FIXTURES / probes.PROBE_RUNS[pid].fixtures[name]).read_text(encoding='utf-8')
    return {name: ''.join(json.dumps(edit(json.loads(line))) + '\n' for line in text.split('\n') if line)}


def test_every_registered_probe_has_its_fixtures():
    for pid, probe in probes.PROBE_RUNS.items():
        for fixture in probe.fixtures.values():
            assert (FIXTURES / fixture).is_file(), f'{pid}: {fixture} is missing; record it with save_fixtures'


def test_the_worktree_probe_backs_its_section_and_its_two_skills():
    '''The manifest entry the owner chose (plan 115, Task 8): a worktree DIVERGES sends /cc-guide verify to the
    guide's worktrees section and /cc-guide files to the two skills that act on it.'''
    manifest = parse_manifest((REPO / MANIFEST).read_text(encoding='utf-8'))
    assert manifest.probes['worktree-isolation'] == (
        ['subagents.worktrees'],
        ['skills/using-git-worktrees/SKILL.md', 'skills/finishing-a-development-branch/SKILL.md'])


@pytest.mark.parametrize('pid', list(probes.PROBE_RUNS))
def test_the_recorded_run_passes(pid):
    assert replay(pid).outcome == PASS


def with_tools(*added):
    def edit(event):
        if event.get('subtype') == 'init':
            event['tools'] = sorted({*event['tools'], *added})
        return event
    return edit


def without_tools(*dropped):
    def edit(event):
        if event.get('subtype') == 'init':
            event['tools'] = [t for t in event['tools'] if t not in dropped]
        return event
    return edit


def model_of(parent_model: dict[str, str]):
    def edit(event):
        if event.get('type') == 'assistant' and event.get('parent_tool_use_id') in parent_model:
            event['message']['model'] = parent_model[event['parent_tool_use_id']]
        return event
    return edit


def drop(kind: str):
    return lambda event: {} if event.get('subtype') == kind else event


def pin_ids(agent: str) -> dict[str, str]:
    '''Each dispatch of `agent` in the recorded pins stream, mapped to the session model.'''
    probe = probes.PROBE_RUNS['agent-model-pins']
    events = probes.stream_of(probes.reader(FIXTURES, probe.fixtures)('pins.jsonl'))
    return {tid: 'claude-sonnet-5-5' for tid, kind in probe_checks.dispatches(events).items() if kind == agent}


def with_result(text: str):
    '''An edit that replaces the text of each tool result.'''
    def edit(event):
        for block in (event.get('message') or {}).get('content') or []:
            if block.get('type') == 'tool_result':
                block['content'] = text
        return event
    return edit


unmarked = with_result('<output>')
marked = with_result(f'{probe_checks.GUARD_MARKER} denied')


def transcripts_with(edit) -> dict[str, str]:
    '''The recorded transcripts.json with `edit` applied to it.'''
    probe = probes.PROBE_RUNS['agent-model-pins']
    saved = json.loads((FIXTURES / probe.fixtures['transcripts.json']).read_text(encoding='utf-8'))
    return {'transcripts.json': json.dumps(edit(saved))}


def reviewing_at(effort: str):
    def edit(saved):
        saved[probe_checks.REVIEWER] = [{**line, 'effort': effort} for line in saved[probe_checks.REVIEWER]]
        return saved
    return edit


def payloads_with(edit) -> dict[str, str]:
    '''The recorded payloads.json with `edit` applied to each payload; an edit that returns None drops the payload.
    The logged counts stay as recorded.'''
    probe = probes.PROBE_RUNS['agent-payload']
    saved = json.loads((FIXTURES / probe.fixtures['payloads.json']).read_text(encoding='utf-8'))
    kept = [p for p in (edit(dict(q)) for q in saved['payloads']) if p is not None]
    return {'payloads.json': json.dumps({**saved, 'payloads': kept})}


def requesting(agent: str, model: str | None):
    '''An edit that makes the parent's dispatch of `agent` pass `model`, or no model for None.'''
    def edit(event):
        if event.get('type') == 'assistant' and not event.get('parent_tool_use_id'):
            for block in event['message']['content']:
                if block.get('type') == 'tool_use' and block['input'].get('subagent_type') == agent:
                    block['input'].pop('model', None)
                    block['input'].update({'model': model} if model else {})
        return event
    return edit


def without_dispatch(*agents: str):
    '''An edit that drops the parent's calls of each of `agents`.'''
    def edit(event):
        if event.get('type') == 'assistant' and not event.get('parent_tool_use_id'):
            event['message']['content'] = [b for b in event['message']['content'] if not (
                b.get('type') == 'tool_use' and b['input'].get('subagent_type') in agents)]
        return event
    return edit


def served_by(agent: str, model: str) -> dict[str, str]:
    '''The recorded dispatch stream with each message that `agent` forwarded served by `model`.'''
    probe = probes.PROBE_RUNS['agent-payload']
    events = probes.stream_of(probes.reader(FIXTURES, probe.fixtures)('dispatch.jsonl'))
    ids = {tid: model for tid, kind in probe_checks.dispatches(events).items() if kind == agent}
    return edited('agent-payload', 'dispatch.jsonl', model_of(ids))


def cut_measures(edit) -> dict[str, str]:
    '''The recorded compaction-cut measures with `edit` applied to them.'''
    probe = probes.PROBE_RUNS['compaction-cut']
    saved = json.loads((FIXTURES / probe.fixtures['cut.json']).read_text(encoding='utf-8'))
    return {'cut.json': json.dumps(edit(saved))}


def keeping(chars: int):
    def edit(measures):
        measures['prose']['body_chars_kept'] = chars
        return measures
    return edit


def without_digit(measures):
    return {kind: measure for kind, measure in measures.items() if kind != 'digit'}


def sightings_with(rep: int, agent: str, **seen) -> dict[str, str]:
    '''The recorded explore-override sightings.json with `seen` replacing fields of `agent`'s sightings in rep `rep`,
    counted from 1.'''
    probe = probes.PROBE_RUNS['explore-override']
    saved = json.loads((FIXTURES / probe.fixtures['sightings.json']).read_text(encoding='utf-8'))
    saved[rep - 1]['seen'][agent].update(seen)
    return {'sightings.json': json.dumps(saved)}


# The register's window, which compaction-cut reads; the first case keeps one character fewer.
def teardown_log_with(old: str, new: str) -> dict[str, str]:
    '''The recorded async-teardown log with each `old` line replaced by `new`.'''
    probe = probes.PROBE_RUNS['async-teardown']
    lines = (FIXTURES / probe.fixtures['teardown.log']).read_text(encoding='utf-8').splitlines()
    return {'teardown.log': ''.join(f'{new if line == old else line}\n' for line in lines)}


def outcome(value: str):
    def edit(event):
        if event.get('subtype') == 'hook_response':
            event['outcome'] = value
        return event
    return edit


def exiting(code: int):
    '''An edit that gives each Stop hook_response the exit code `code`.'''
    def edit(event):
        if event.get('subtype') == 'hook_response' and event.get('hook_event') == 'Stop':
            event['exit_code'] = code
        return event
    return edit


def worktrees_with(part: str, step: str | None = None, **seen) -> dict[str, str]:
    '''The recorded worktree-isolation sightings with `seen` replacing fields of run `part`, or of its step `step`.'''
    probe = probes.PROBE_RUNS['worktree-isolation']
    saved = json.loads((FIXTURES / probe.fixtures['worktrees.json']).read_text(encoding='utf-8'))
    (saved[part] if step is None else saved[part]['steps'][step]).update(seen)
    return {'worktrees.json': json.dumps(saved)}


CUT_WINDOW = probes.register_window()


# Each case names its finding. An ERROR case does so because a missing fixture, which is ERROR for another reason,
# cannot then pass it, and a DIVERGES case because the divergence must be the one the edit made.
@pytest.mark.parametrize('pid, changes, outcome, finding', [
    ('agent-tools', lambda: edited('agent-tools', 'probe-with-bash.jsonl', with_tools('Grep', 'Glob')), DIVERGES,
     'with Bash: Bash, Glob, Grep, Read; without Bash: Glob, Grep, Read'),
    # The control half of the rule: the agent without Bash must get Grep and Glob both.
    ('agent-tools', lambda: edited('agent-tools', 'probe-without-bash.jsonl', without_tools('Glob')), DIVERGES,
     'with Bash: Bash, Read; without Bash: Grep, Read'),
    # A control that gains Bash did not get its own tool list, so it proves nothing about the rule: ERROR, not drift.
    ('agent-tools', lambda: edited('agent-tools', 'probe-without-bash.jsonl', with_tools('Bash')), ERROR,
     'the control agent did not get its own tool list: Bash, Glob, Grep, Read'),
    ('agent-tools', lambda: edited('agent-tools', 'probe-without-bash.jsonl', drop('init')), ERROR,
     'the agent without Bash: no init event'),
    ('stop-continuation', lambda: {'stop.log': 'false\nfalse\ntrue\n'}, DIVERGES,
     'stop_hook_active read false, false, true'),
    ('stop-continuation', lambda: {'stop.log': ''}, ERROR, 'the Stop hook never logged a call'),
    # The log is the recorded one, so the stream's exit codes alone are wrong.
    ('stop-continuation', lambda: edited('stop-continuation', 'stop.jsonl', exiting(0)), ERROR,
     'stop_hook_active read false, true, true, but the stream shows Stop hook exits [0, 0, 0]'),
    ('agent-model-pins', lambda: edited('agent-model-pins', 'pins.jsonl', model_of(pin_ids('Explore'))), DIVERGES,
     'Explore served claude-sonnet-5-5'),
    ('agent-model-pins', lambda: edited('agent-model-pins', 'pins.jsonl', model_of(pin_ids('test-runner'))), DIVERGES,
     'test-runner served claude-sonnet-5-5'),
    ('agent-model-pins', lambda: transcripts_with(reviewing_at('high')), DIVERGES, 'code-reviewer effort high'),
    ('agent-model-pins', lambda: {'transcripts.json': '{}'}, ERROR, 'no transcript lines for Explore'),
    ('guard-liveness', lambda: edited('guard-liveness', 'guard-2.jsonl', unmarked), DIVERGES,
     'git fetch --dry-run origin was not denied'),
    # Check 1's command is the read-only one, which the guard must pass.
    ('guard-liveness', lambda: edited('guard-liveness', 'guard-1.jsonl', marked), DIVERGES,
     'git status --porcelain was denied'),
    ('guard-liveness', lambda: edited('guard-liveness', 'guard-3.jsonl', drop('init')), ERROR,
     'check 3: no init event'),
    # agent-payload's cases pin their findings, DIVERGES included.
    ('agent-payload', lambda: payloads_with(lambda p: {**p, 'tool_name': 'Task'}), DIVERGES,
     'a subagent dispatch reaches PreToolUse as Task, not Agent'),
    ('agent-payload', lambda: payloads_with(lambda p: None if p['matcher'] == 'Agent' else p), DIVERGES,
     'the Agent matcher did not fire for general-purpose, claude-code-guide'),
    ('agent-payload', lambda: payloads_with(lambda p: {**p, 'model': p['model'] or 'inherit'}), DIVERGES,
     "a dispatch sent with no model (claude-code-guide) arrives with model 'inherit', so the guard would pass a "
     'model-less dispatch of any type'),
    ('agent-payload', lambda: served_by('claude-code-guide', 'claude-sonnet-5-5'), DIVERGES,
     'claude-code-guide was served the session model claude-sonnet-5-5'),
    ('agent-payload', lambda: served_by('claude-code-guide', 'claude-opus-5-5'), DIVERGES,
     'claude-code-guide was served claude-opus-5-5, not the claude-haiku-5-5 the haiku control was served'),
    ('agent-payload', lambda: served_by('general-purpose', 'claude-sonnet-5-5'), ERROR,
     'the general-purpose control with model haiku was served the session model claude-sonnet-5-5, so a pin '
     'cannot be told from it'),
    ('agent-payload', lambda: {'payloads.json': json.dumps({'logged': {'any': 0, 'agent': 0}, 'payloads': []})},
     ERROR, 'the PreToolUse hooks logged no subagent dispatch'),
    ('agent-payload', lambda: {'payloads.json': None}, ERROR, 'the PreToolUse hooks logged no subagent dispatch'),
    ('agent-payload', lambda: payloads_with(lambda p: None), ERROR,
     'the PreToolUse hooks logged 4 payloads, and trim_payload kept none of them (a renamed subagent_type, a moved '
     'tool_input, or payloads that carry agent_id)'),
    # A parent that does not send what its prompt asks is ERROR, never drift: the payloads would show its choice.
    ('agent-payload', lambda: edited('agent-payload', 'dispatch.jsonl', requesting('general-purpose', None)), ERROR,
     "the parent session sent general-purpose with no model, but its prompt asks for model 'haiku'"),
    ('agent-payload', lambda: edited('agent-payload', 'dispatch.jsonl', requesting('claude-code-guide', 'sonnet')),
     ERROR, "the parent session sent claude-code-guide with model 'sonnet', but its prompt asks for no model"),
    # A parent that never dispatches a type is named, not the hooks or trim_payload.
    ('agent-payload', lambda: {**edited('agent-payload', 'dispatch.jsonl', without_dispatch('claude-code-guide')),
                               **payloads_with(lambda p: None if p['subagent_type'] == 'claude-code-guide' else p)},
     ERROR, 'the parent session never dispatched claude-code-guide, but its prompt asks for one dispatch of each type'),
    ('agent-payload', lambda: {
        **edited('agent-payload', 'dispatch.jsonl', without_dispatch(*probe_checks.PAYLOAD_AGENTS)),
        'payloads.json': json.dumps({'logged': {'any': 1, 'agent': 0}, 'payloads': []})},
     ERROR, 'the parent session never dispatched general-purpose, but its prompt asks for one dispatch of each type'),
    # compaction-cut's cases pin their findings too. The recorded run, a header of 159 characters, kept more than the window.
    ('compaction-cut', lambda: cut_measures(keeping(CUT_WINDOW - 1)), DIVERGES,
     f'compaction keeps {CUT_WINDOW - 1} body characters of the prose probe skill (by characters; 159 characters '
     f'before the body), fewer than the register window {CUT_WINDOW}, so a body that passes compaction-window '
     'can lose its last 1'),
    ('compaction-cut', lambda: cut_measures(without_digit), ERROR,
     'no re-attached copy of cut-probe-digit after the compact boundary'),
    ('compaction-cut', lambda: edited('compaction-cut', 'cut.jsonl', drop('compact_boundary')), ERROR,
     'the /compact run emitted no compact_boundary event'),
    # explore-override's cases pin their findings: a valid rep where the override got a git-status snapshot, and a
    # rep that proves nothing, since the control missed the CLAUDE.md canary.
    ('explore-override', lambda: sightings_with(2, 'Explore', git_status=True), DIVERGES,
     'rep 2: the Explore override got a git-status snapshot'),
    ('explore-override', lambda: sightings_with(3, 'canary-control', claude_md=False), ERROR,
     'rep 3: the control missed the CLAUDE.md canary'),
    # async-teardown's cases pin their findings: another signal first, a hook that never started, and the recorded
    # SessionStart hook_response finalized as something other than cancelled.
    ('async-teardown', lambda: teardown_log_with('TERM', 'HUP'), DIVERGES,
     'the async SessionStart hook got HUP first at teardown and was gone within 5 s'),
    ('async-teardown', lambda: {'teardown.log': ''}, ERROR, 'the async SessionStart hook never started'),
    ('async-teardown', lambda: edited('async-teardown', 'teardown.jsonl', outcome('success')), DIVERGES,
     "the async SessionStart hook got TERM first at teardown and was gone within 5 s; the stream's SessionStart "
     'hook_response reads success, not cancelled'),
    # worktree-isolation's cases pin one finding for each of the guide's four facts, and a run that broke. The edits
    # change the recorded sightings, and the assessor reads only those.
    ('worktree-isolation', lambda: worktrees_with('isolation', 'git_subshell', refused=False, marked=False), DIVERGES,
     'isolation: git_subshell was not refused'),
    ('worktree-isolation', lambda: worktrees_with('isolation', locked_after=True), DIVERGES,
     'isolation: the worktree was still locked after ExitWorktree'),
    ('worktree-isolation', lambda: worktrees_with('noop', exit_refused=False, exit_marked=False), DIVERGES,
     'noop: ExitWorktree was not refused'),
    ('worktree-isolation', lambda: worktrees_with('base-failed-fetch', has_unpushed=True), DIVERGES,
     'base-failed-fetch kept the unpushed commit'),
    ('worktree-isolation', lambda: worktrees_with('isolation', broken='no result event'), ERROR,
     'isolation: the run broke: no result event'),
])
def test_a_changed_behaviour_diverges_and_a_broken_run_is_an_error(pid, changes, outcome, finding):
    verdict = replay(pid, changes())
    assert verdict.outcome == outcome
    assert verdict.finding == finding


def test_no_fixture_holds_a_path_or_an_id_from_the_recording_machine():
    for path in sorted(FIXTURES.iterdir()):
        found = PRIVATE_RE.search(path.read_text(encoding='utf-8'))
        assert found is None, f'{path.name} holds {found.group(0)!r}: re-record it through save_fixtures'


def test_the_committed_probe_log_holds_no_private_text_and_is_one_table():
    '''PROBES.md is public like the fixtures. parse_probes reads only the rows under the log table's header, so a
    blank line inside the table would hide every later row from the due check without any error.'''
    text = PROBES_LOG.read_text(encoding='utf-8')
    found = PRIVATE_RE.search(text)
    assert found is None, f'{PROBES_LOG.name} holds {found.group(0)!r}'
    rows, parsed = len(LOG_ROW_RE.findall(text)), len(parse_probes(text))
    assert parsed == rows, f'{rows} log rows, but parse_probes reads {parsed}: a row sits outside the log table'
