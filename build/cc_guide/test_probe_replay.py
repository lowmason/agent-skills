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

import probes
from cc_fixtures import isolated_home  # noqa: F401
from state import DIVERGES, ERROR, PASS, parse_probes

FIXTURES = Path(__file__).resolve().parent / 'probe_streams'
PROBES_LOG = Path(__file__).resolve().parent / 'PROBES.md'
LOG_ROW_RE = re.compile(r'^\| \d{4}-\d{2}-\d{2} \|', re.MULTILINE)
PRIVATE_RE = re.compile(r'/Users/|/home/|/private/|/var/folders/|/tmp/|toolu_0|mcp__|'
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


@pytest.mark.parametrize('pid', list(probes.PROBE_RUNS))
def test_the_recorded_run_passes(pid):
    assert replay(pid).outcome == PASS


def with_tools(*added):
    def edit(event):
        if event.get('subtype') == 'init':
            event['tools'] = sorted({*event['tools'], *added})
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


def explore_ids() -> dict[str, str]:
    probe = probes.PROBE_RUNS['agent-model-pins']
    events = probes.stream_of(probes.reader(FIXTURES, probe.fixtures)('pins.jsonl'))
    return {tid: 'claude-sonnet-5-5' for tid, kind in probes.probe_checks.dispatches(events).items()
            if kind == 'Explore'}


def unmarked(event):
    for block in (event.get('message') or {}).get('content') or []:
        if block.get('type') == 'tool_result':
            block['content'] = '<output>'
    return event


# Each ERROR case names its finding, so a missing fixture, which is ERROR for
# another reason, cannot pass it.
@pytest.mark.parametrize('pid, changes, outcome, finding', [
    ('agent-tools', lambda: edited('agent-tools', 'probe-with-bash.jsonl', with_tools('Grep', 'Glob')), DIVERGES,
     None),
    ('agent-tools', lambda: edited('agent-tools', 'probe-without-bash.jsonl', drop('init')), ERROR,
     'the agent without Bash: no init event'),
    ('stop-continuation', lambda: {'stop.log': 'false\nfalse\ntrue\n'}, DIVERGES, None),
    ('stop-continuation', lambda: {'stop.log': ''}, ERROR, 'the Stop hook never logged a call'),
    ('agent-model-pins', lambda: edited('agent-model-pins', 'pins.jsonl', model_of(explore_ids())), DIVERGES, None),
    ('agent-model-pins', lambda: {'transcripts.json': '{}'}, ERROR, 'no transcript lines for Explore'),
    ('guard-liveness', lambda: edited('guard-liveness', 'guard-2.jsonl', unmarked), DIVERGES, None),
    ('guard-liveness', lambda: edited('guard-liveness', 'guard-3.jsonl', drop('init')), ERROR,
     'check 3: no init event'),
])
def test_a_changed_behaviour_diverges_and_a_broken_run_is_an_error(pid, changes, outcome, finding):
    verdict = replay(pid, changes())
    assert verdict.outcome == outcome
    assert finding is None or verdict.finding == finding


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
