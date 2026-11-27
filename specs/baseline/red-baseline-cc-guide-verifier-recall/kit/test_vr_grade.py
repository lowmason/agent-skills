'''No-model tests of plan 102's grader (Task 7), on hand-written streams,
transcripts, reports and fixtures.

Every test runs with HOME, common.R and common.KIT under pytest's temporary
folder (the autouse fixture checks them before the test body runs), so
common.k_dir() is temporary too. No test reads a docs file, the real $K or
a real transcript under ~/.claude/projects/. The V2 path tests name rep
folders under /private/tmp/vrtest/, which no test creates: V2 only resolves
paths there, it never reads or writes a file.'''
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import common
import grade
import settle

ARM_WORDS = ('control', 'changed')
SID = '0a1b2c3d-0000-4000-8000-000000000001'
BODY = {'control': 'Arm one contract body.', 'changed': 'Arm two contract body, with listed items.'}
ROOT = '/private/tmp/vrtest/r001/work'  # a V2 root under /private/tmp, as a real rep's is
LAUNCH = 'Async agent launched successfully.\nagentId: a1 (internal ID)'
# A foreground dispatch's finished Agent result in the held binary when the verifier hands back, in the pilot rep
# r004's real shape: it points at the hand-back and holds no report. A background dispatch gets LAUNCH instead.
COMPLETION = ('  This agent\'s report was delivered to you as a message from "a1" (its SubagentHandback call). Read it '
              'there; it is not repeated here.\n  \nagentId: a1\n<usage>subagent_tokens: 270599\ntool_uses: 64\n'
              'duration_ms: 663846</usage>')
DOC_LINE = 'Set `deniedModels` in managed settings to block a model.'
ALLOW_LINE = 'The `availableModels` list limits the picker.'

GUIDE = '\n'.join([
    '# Guide',  # 1
    '',
    '## Models',  # 3
    '<!-- cc: models.routing -->',
    'Limit the picker with `availableModels`.',  # 5
    'Pick a model with `/model`.',  # 6
    '',
    '## Cache',  # 8
    '<!-- cc: models.cache -->',
    'The cache lasts five minutes.',  # 10
    '',
])
LISTED = [{'item': '2.1.283#1', 'line': 1288, 'sections': ['models.routing'], 'lacks': ['deniedModels'], 'text': 'a'},
          {'item': '2.1.250#1', 'line': 1702, 'sections': ['models.routing'], 'lacks': [], 'text': 'b'},
          {'item': '2.1.200#1', 'line': 224, 'sections': ['models.routing'], 'lacks': [], 'text': 'c'},
          {'item': '2.1.190#4', 'line': 500, 'sections': ['models.cache'], 'lacks': [], 'text': 'd'}]
AUDIT_INDEX = {'mode': 'audit', 'inputs': 'the working tree', 'head': '2.1.300', 'group': 'models',
               'sections': ['models.routing', 'models.cache'],
               'lines': {'models.routing': [3, 7], 'models.cache': [8, 11]}, 'docs': '/gone/master/docs',
               'releases': [], 'held': [],
               'quotes': {'guide': ['guide.md'], 'changelog': ['changelog.md'], 'docs': ['/gone/master/docs']},
               'blocks': []}
AUDIT_REPORT = '\n'.join([
    '# Report',
    'L5 | the picker list limits models | PARTIAL | settings.md:1 | "Set `deniedModels` in managed settings to '
    'block a model." | Add that managed `deniedModels` blocks a model the allow list permits.',
    'L6 | /model picks a model | CONFIRMED | settings.md:2 | "The `availableModels` list limits the picker." | -',
    'L10 | the cache lasts five minutes | STALE | settings.md:2 | "a quote the docs lack" | The cache lasts an hour.',
    'L10 | the cache is per model | WRONG | settings.md:2 | "The `availableModels` list limits the picker." | -',
    'B | 2.1.283 | x | changelog.md:1288',
    'B | 2.1.250 | effort | changelog.md:1702',
    'B | 2.1.180 | other | changelog.md:77',
    'B | not-a-label | broken | changelog.md:9',
    '2.1.200#1 | none',
    'C | deniedModels blocks a model that availableModels permits',
    'C | an omission about the cache',
    '',
])

FILES_GUIDE = '\n'.join([
    '# Guide',
    '',
    '## Events',  # 3
    '<!-- cc: hooks.events -->',
    "A hook's exit code 2 blocks the call.",  # 5
    '',
    '## Description',  # 7
    '<!-- cc: skills.description -->',
    'Write the description in third person.',  # 9
    '',
])
README_INDEX = {'mode': 'files', 'file': 'hooks/README.md', 'copy': 'cited_README.md', 'stamp': '2.1.219',
                'sections': ['hooks.events'], 'lines': {'hooks.events': [3, 6]}, 'quotes': {'guide': ['guide.md']},
                'covered': {}}
README_REPORT = '\n'.join([
    'hooks/README.md:89 | exit 1 blocks the call | hooks.events | "A hook\'s exit code 2 blocks the call." '
    '| contradicts',
    'hooks/README.md:85-88 | hooks run in order | hooks.events | "A hook\'s exit code 2 blocks the call." '
    '| consistent',
    'hooks/README.md:93-99 | exit 3 blocks | hooks.events | "a quote the guide lacks" | contradicts',
    'hooks/README.md:40 | the event list | hooks.events | "A hook\'s exit code 2 blocks the call." | contradicts',
    'hooks/README.md:94 | late line | hooks.events | "A hook\'s exit code 2 blocks the call." | consistent',
    '',
])
PRECISION_INDEX = {'mode': 'files', 'file': 'skills/x/SKILL.md', 'copy': 'cited_SKILL.md', 'stamp': '2.1.326',
                   'sections': ['skills.description'], 'lines': {'skills.description': [7, 10]},
                   'quotes': {'guide': ['guide.md']},
                   'covered': {'skills/x/references/a.md': 'covered/references/a.md',
                               'skills/x/references/b.md': 'covered/references/b.md'}}
PRECISION_REPORT = '\n'.join([
    'skills/x/SKILL.md:12-14 | write it in second person | skills.description | "Write the description in third '
    'person." | contradicts',
    'skills/x/references/a.md:3 | describe in first person | skills.description | "Write the description in third '
    'person." | contradicts',
    'skills/x/references/a.md:9 | third person | skills.description | "Write the description in third person." '
    '| consistent',
    'skills/x/SKILL.md:30 | a lost quote | skills.description | "no such guide text" | contradicts',
    '',
])
KEY = '# file:line\tsection\tguide line\twhy\nskills/x/SKILL.md:13\tskills.description\t9\tsecond person\n' \
      'skills/x/references/b.md:1-4\tskills.description\t9\tanother\n'


# --- the sandbox and the fakes ------------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def sandbox(tmp_path, tmp_path_factory, monkeypatch):
    '''HOME, R and KIT under pytest's temporary folder, checked before any test body runs.'''
    base = tmp_path_factory.getbasetemp().resolve()
    home = tmp_path / 'home'
    home.mkdir()
    monkeypatch.setenv('HOME', str(home))
    monkeypatch.setattr(common, 'R', tmp_path / 'R')
    monkeypatch.setattr(common, 'KIT', tmp_path / 'kitfiles')
    assert_sandboxed(base)
    return base


def assert_sandboxed(base: Path) -> None:
    for path in (Path(os.environ['HOME']), common.R, common.k_dir(), common.KIT):
        assert path.resolve().is_relative_to(base), path


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
    return path


def write_json(path: Path, obj) -> Path:
    return write(path, json.dumps(obj, indent=1) + '\n')


def write_jsonl(path: Path, records: list[dict]) -> Path:
    return write(path, ''.join(json.dumps(r) + '\n' for r in records))


@pytest.fixture
def kit(sandbox):
    '''$K with the arms, the fixtures (both audit copies, the docs, readme and
    precision) and the precision key. The audit copies' index names docs that
    do not exist, as the master's path would on another machine.'''
    k = common.k_dir()
    for arm, body in BODY.items():
        write(k / 'arms' / f'{arm}.md', f'---\nname: cc-guide-verifier\n---\n\n{body}\n')
    fx = k / 'fixtures'
    write_json(fx / 'audit-control' / 'index.json', AUDIT_INDEX)
    write_json(fx / 'audit-changed' / 'index.json', AUDIT_INDEX | {'listed': LISTED})
    write(fx / 'audit-changed' / 'listed.md', 'listed\n')
    for name in ('audit-control', 'audit-changed'):
        write(fx / name / 'guide.md', GUIDE)
        write(fx / name / 'changelog.md', 'changelog\n')
    write(fx / 'docs' / 'settings.md', f'{DOC_LINE}\n{ALLOW_LINE}\n')
    for name, index in (('readme', README_INDEX), ('precision', PRECISION_INDEX)):
        write_json(fx / name / 'index.json', index)
        write(fx / name / 'guide.md', FILES_GUIDE)
        write(fx / name / index['copy'], 'copy\n')
    write(k / 'precision-key.tsv', KEY)
    return k


def plan(*reps: tuple, batch: str = 'b') -> None:
    '''Add reps to plan.json and the batch file: (rid, packet, arm), (rid, packet, arm, role) or
    (rid, packet, arm, role, replaces).'''
    k = common.k_dir()
    path = k / 'plan.json'
    data = json.loads(path.read_text()) if path.exists() else {'reps': []}
    for rid, packet, arm, *more in reps:
        data['reps'].append({'rid': rid, 'batch': batch, 'packet': packet, 'arm': arm,
                             'role': more[0] if more else 'counted'}
                            | ({'replaces': more[1]} if len(more) > 1 else {}))
    write_json(path, data)
    (k / 'batches').mkdir(parents=True, exist_ok=True)
    with (k / 'batches' / f'{batch}.txt').open('a') as f:
        f.writelines(r[0] + '\n' for r in reps)


def dispatch(rid: str, packet: str) -> str:
    mode = common.PACKETS[packet]['mode']
    return common.DISPATCH.format(mode=mode, packet=common.R / rid / 'work' / 'packet')


def agent_call(rid: str, packet: str, uid: str = 'toolu_main1', **extra) -> dict:
    inp = {'description': 'Verify the packet', 'subagent_type': 'cc-guide-verifier', 'model': 'sonnet',
           'prompt': dispatch(rid, packet)} | extra
    return {'type': 'tool_use', 'id': uid, 'name': 'Agent', 'input': inp}


def assistant(*blocks: dict, parent: str | None = None, model: str = 'claude-opus-5-5') -> dict:
    return {'type': 'assistant', 'parent_tool_use_id': parent, 'session_id': SID,
            'message': {'model': model, 'content': list(blocks)}}


def tool_result(uid: str, text, error: bool = False, parent: str | None = None) -> dict:
    return {'type': 'user', 'parent_tool_use_id': parent,
            'message': {'role': 'user', 'content': [{'type': 'tool_result', 'tool_use_id': uid, 'content': text,
                                                     'is_error': error}]}}


def result_record(**changes) -> dict:
    return {'type': 'result', 'subtype': 'success', 'is_error': False, 'total_cost_usd': 3.25, 'duration_ms': 1000,
            'terminal_reason': 'completed', 'result': 'the main reply',
            'subagent_stats': {'failed': 0, 'killed': {'parent': 0, 'user': 0, 'system': 0},
                               'refused': {'depth_limit': 0, 'budget': 0}}} | changes


def stream(rid: str, packet: str, calls: list[dict] | None = None, agent_text: str = LAUNCH,
           results: list[dict] | None = None) -> list[dict]:
    calls = [agent_call(rid, packet)] if calls is None else calls
    events = [{'type': 'system', 'subtype': 'init', 'session_id': SID, 'tools': ['Agent']}, assistant(*calls)]
    events += [tool_result(c['id'], agent_text) for c in calls if c.get('type') == 'tool_use']
    return events + ([result_record()] if results is None else results)


def att(kind: str, **fields) -> dict:
    return {'type': 'attachment', 'attachment': {'type': kind} | fields}


def vassistant(*blocks: dict, model: str = 'claude-sonnet-5-5', effort='xhigh', version='2.1.327') -> dict:
    return {'type': 'assistant', 'effort': effort, 'version': version, 'message': {'model': model,
                                                                                   'content': list(blocks)}}


def use(uid: str, name: str, **inp) -> dict:
    return {'type': 'tool_use', 'id': uid, 'name': name, 'input': inp}


def verifier(rid: str, arm: str, report: str | None, *, snapshots: list[list[str]] | None = None,
             advisor: bool = True, extra: tuple = (), **settings) -> list[dict]:
    '''A verifier transcript: its snapshots, advisor, a Read of its own
    packet, any extra records, and a SubagentHandback of the report.'''
    work = str(common.R / rid / 'work')
    recs = [att('prompt_snapshot', systemPrompt=parts) for parts in
            (snapshots if snapshots is not None else [[BODY[arm], 'Environment part.', 'Date part.']])]
    if advisor:
        recs.append(att('advisor_tool', available=True, model='claude-opus-5-5', toolChange='add'))
    recs += [att('session_context', context={'note': 'not a repo'}),
             vassistant(use('toolu_v1', 'Read', file_path=f'{work}/packet/index.json'), **settings),
             tool_result('toolu_v1', '{"mode": "audit"}'), *extra]
    if report is not None:
        recs += [vassistant(use('toolu_v9', 'SubagentHandback', message=report), **settings),
                 tool_result('toolu_v9', 'Report delivered to your caller.')]
    return recs


def rep_files(rid: str, packet: str, arm: str, report: str | None, *, events: list[dict] | None = None,
              transcripts: list[list[dict]] | None = None, status: dict | None = None,
              main: list[dict] | None = None, write_result: bool = True) -> Path:
    '''What run.py leaves for a rep: stream.jsonl, result.json, status.json,
    the session's files under project/, and the moved rep folder in homes/.'''
    k = common.k_dir()
    res = k / 'results' / rid
    events = stream(rid, packet) if events is None else events
    write_jsonl(res / 'stream.jsonl', events)
    results = [e for e in events if e.get('type') == 'result']
    if write_result and results:
        write_json(res / 'result.json', results[-1])
    write_json(res / 'status.json', {'exit': 0, 'timed_out': False, 'interrupted': False, 'seconds': 321.4,
                                     'strip_ok': True} | (status or {}))
    slug = res / 'project' / ('-private-tmp-vr102-' + rid + '-work')
    write_jsonl(slug / f'{SID}.jsonl', main if main is not None else [att('skill_listing', content='none')])
    transcripts = [verifier(rid, arm, report)] if transcripts is None else transcripts
    for i, recs in enumerate(transcripts):
        write_json(slug / SID / 'subagents' / f'agent-a{i}.meta.json', {'agentType': 'cc-guide-verifier'})
        write_jsonl(slug / SID / 'subagents' / f'agent-a{i}.jsonl', recs)
    write(k / 'homes' / rid / 'work' / 'docs' / 'settings.md', 'moved docs\n')
    return res


def sheet(rid: str) -> str:
    return (common.k_dir() / 'sheets' / f'{rid}.txt').read_text(encoding='utf-8')


def section(text: str, heading: str) -> list[str]:
    '''The indented lines under a sheet heading.'''
    lines = text.splitlines()
    start = lines.index(heading)
    out = []
    for line in lines[start + 1:]:
        if not line.startswith('  '):
            break
        out.append(line.strip())
    return out


def check_line(text: str, name: str) -> str:
    return next(line for line in text.splitlines() if line.startswith(name + ': '))


def no_arm_named(text: str) -> bool:
    lowered = text.lower()
    return not any(w in lowered for w in ARM_WORDS) and 'arms/' not in lowered


def pilot_json(**fields) -> None:
    write_json(common.k_dir() / 'pilot.json', fields)


def one_rep(rid='r001', packet='audit', arm='changed', report=AUDIT_REPORT, batch='b', role='counted', **kw) -> str:
    plan((rid, packet, arm, role), batch=batch)
    rep_files(rid, packet, arm, report, **kw)
    assert grade.main([batch]) == 0
    return sheet(rid)


# --- the plan's tests ---------------------------------------------------------------------------------------


def test_v1_allows_model_sonnet_and_voids_another_tool_call():
    prompt = dispatch('r001', 'audit')
    assert grade.check_v1(stream('r001', 'audit'), 1, prompt).status == 'ok'
    bash = use('toolu_b', 'Bash', command='ls')
    got = grade.check_v1(stream('r001', 'audit', [agent_call('r001', 'audit'), bash]), 1, prompt)
    assert got.status == 'void' and 'Bash' in got.detail
    opus = grade.check_v1(stream('r001', 'audit', [agent_call('r001', 'audit', model='opus')]), 1, prompt)
    assert opus.status == 'void' and "'opus'" in opus.detail


def test_v2_voids_an_outside_read_that_returned_and_logs_a_refused_one():
    records = [vassistant(use('t1', 'Read', file_path=f'{ROOT}/packet/index.json'),
                          use('t2', 'Read', file_path='/System/Volumes/Data/private/tmp/vrtest/r001/work/docs/a.md'),
                          use('t3', 'Read', file_path='/Users/someone/secret.md'),
                          use('t4', 'Read', file_path='../../r002/work/packet/report.md')),
               tool_result('t1', '{}'), tool_result('t2', 'docs'),
               tool_result('t3', 'Permission denied', error=True), tool_result('t4', 'their report')]
    void, refused = grade.check_v2(records, ROOT)
    assert void.status == 'void'
    assert '../../r002/work/packet/report.md' in void.detail
    assert 'index.json' not in void.detail and 'docs/a.md' not in void.detail and 'secret' not in void.detail
    assert refused == ['Read /Users/someone/secret.md']


def test_v5_voids_a_snapshot_whose_first_part_is_not_the_arm_body():
    body = BODY['control']
    good = [att('prompt_snapshot', systemPrompt=[body, 'p1']), att('prompt_snapshot', systemPrompt=[body, 'p2'])]
    assert grade.check_v5(good, body).status == 'ok'
    bad = good + [att('prompt_snapshot', systemPrompt=[BODY['changed'], 'p1'])]
    got = grade.check_v5(bad, body)
    assert got.status == 'void' and body not in got.detail and BODY['changed'] not in got.detail
    assert grade.check_v5([att('model', identity={})], body).status == 'void'


def test_v7_compares_model_effort_and_version_with_the_pilot():
    pilot = {'effort': 'xhigh', 'version': '2.1.327'}
    assert grade.check_v7([vassistant()], pilot, False).status == 'ok'
    assert grade.check_v7([vassistant(effort='high')], pilot, False).status == 'void'
    assert grade.check_v7([vassistant(version='2.1.326')], pilot, False).status == 'void'
    assert grade.check_v7([vassistant(model='claude-opus-5-5')], pilot, False).status == 'void'
    assert grade.check_v7([vassistant()], None, False).status == 'pending'
    assert grade.check_v7([vassistant(effort='high', version='2.1.326')], None, True).status == 'ok'


def test_v8_follows_the_production_advisor():
    on = [att('advisor_tool', available=True, model='claude-opus-5-5')]
    assert grade.check_v8(on, {'advisor': True}).status == 'ok'
    assert grade.check_v8([], {'advisor': True}).status == 'void'
    assert grade.check_v8([], {'advisor': False}).status == 'ok'
    assert grade.check_v8(on, {'advisor': False}).status == 'void'
    assert grade.check_v8(on, None).status == 'pending'


def test_an_audit_sheet_lists_p11_and_p8_candidates_and_the_listed_counts(kit):
    text = one_rep()
    assert not (common.R / 'r001').exists()  # the rep folder has moved to homes/
    b_rows = section(text, 'B rows on changelog.md:1288, :1702 or :224:')
    assert '[B kept] B | 2.1.283 | x | changelog.md:1288' in b_rows
    assert '[B kept] B | 2.1.250 | effort | changelog.md:1702' in b_rows
    denied = section(text, 'rows naming deniedModels:')
    assert '[C kept] C | deniedModels blocks a model that availableModels permits' in denied
    kept = section(text, 'kept corrections and C rows (P1 to P14 candidates):')
    assert any(line.startswith('[A L5 models.routing PARTIAL kept] L5 |') for line in kept)
    copy = common.k_dir().parent / 'check-copy'
    import shutil
    shutil.copytree(common.k_dir() / 'fixtures' / 'audit-changed', copy)
    index = json.loads((copy / 'index.json').read_text())
    index['docs'], index['quotes']['docs'] = str(common.k_dir() / 'fixtures' / 'docs'), [
        str(common.k_dir() / 'fixtures' / 'docs')]
    write_json(copy / 'index.json', index)
    write(copy / 'report.md', AUDIT_REPORT)
    want = next(line for line in settle.settle(copy).lines if line.startswith('listed items: '))
    assert check_line(text, 'listed items') == want
    assert want == 'listed items: 2 answered by a B row, 1 answered none, 1 unanswered'


def test_a_files_sheet_lists_kept_contradictions_and_covered_rows(kit):
    plan(('r001', 'readme', 'control'), ('r002', 'precision', 'changed'))
    rep_files('r001', 'readme', 'control', README_REPORT)
    rep_files('r002', 'precision', 'changed', PRECISION_REPORT)
    assert grade.main(['b']) == 0
    readme, precision = sheet('r001'), sheet('r002')
    assert section(readme, 'kept contradicts rows:') == [
        '[F hooks/README.md:89 hooks.events, contradicts] hooks/README.md:89 | exit 1 blocks the call | hooks.events '
        '| "A hook\'s exit code 2 blocks the call." | contradicts',
        '[F hooks/README.md:40 hooks.events, contradicts] hooks/README.md:40 | the event list | hooks.events '
        '| "A hook\'s exit code 2 blocks the call." | contradicts']
    near = section(readme, 'rows on hooks/README.md lines 85 to 93:')
    assert [line.split('] ')[0] for line in near] == ['[F contradicts kept', '[F consistent kept',
                                                       '[F contradicts quote not found']
    assert check_line(readme, 'a kept row names a covered file') == 'a kept row names a covered file: no'
    kept = section(precision, 'kept contradicts rows:')
    assert [line.split('] ')[0] for line in kept] == [
        '[F skills/x/SKILL.md:12-14 skills.description, contradicts, on key',
        '[F skills/x/references/a.md:3 skills.description, contradicts, covered file, not on key']
    assert check_line(precision, 'a kept row names a covered file') == 'a kept row names a covered file: yes'
    assert [line.split('] ')[0] for line in section(precision, 'a kept row names a covered file: yes')] == [
        '[F contradicts kept', '[F consistent kept']
    assert section(precision, 'rows on hooks/README.md lines 85 to 93:') == ['none']


def test_no_sheet_names_an_arm(kit):
    plan(('r001', 'audit', 'control'), ('r002', 'audit', 'changed'), ('r003', 'readme', 'control'),
         ('r004', 'precision', 'changed'), ('r005', 'audit', 'changed', 'pilot'))
    rep_files('r001', 'audit', 'control', AUDIT_REPORT)
    rep_files('r002', 'audit', 'changed', None)  # void: no report
    rep_files('r003', 'readme', 'control', README_REPORT)
    rep_files('r004', 'precision', 'changed', PRECISION_REPORT)
    rep_files('r005', 'audit', 'changed', AUDIT_REPORT)
    assert grade.main(['b']) == 0
    for rid in ('r001', 'r002', 'r003', 'r004', 'r005'):
        assert no_arm_named(sheet(rid)), rid


def test_one_audit_report_gives_the_same_sheet_in_either_arm(kit):
    plan(('r001', 'audit', 'control'), ('r002', 'audit', 'changed'))
    rep_files('r001', 'audit', 'control', AUDIT_REPORT)
    rep_files('r002', 'audit', 'changed', AUDIT_REPORT)
    assert grade.main(['b']) == 0
    assert sheet('r001').replace('r001', 'rXXX') == sheet('r002').replace('r002', 'rXXX')
    assert check_line(sheet('r001'), 'V5') == 'V5: ok'


def test_stop_prints_no_count_per_arm(kit, capsys):
    verdict_reps([('r001', 'control', True, 'yes', 'yes'), ('r002', 'control', True, 'yes', 'no'),
                  ('r003', 'changed', True, 'yes', 'yes'), ('r004', 'changed', True, 'no', 'yes')])
    assert grade.main(['stop', 'gateA1']) == 0
    out, err = capsys.readouterr()
    assert out == 'stop: UNSETTLED\n' and err == ''


def test_unblind_refuses_before_every_verdict_is_in(kit, capsys):
    verdict_reps([('r001', 'control', True, 'yes', 'yes'), ('r002', 'changed', True, 'yes', 'yes')])
    lines = (common.k_dir() / 'RESULTS.md').read_text().splitlines()
    write(common.k_dir() / 'RESULTS.md', '\n'.join(line for line in lines if line != 'r002 P8 yes') + '\n')
    assert grade.main(['unblind', 'A']) == 1
    out, err = capsys.readouterr()
    assert out == '' and 'r002' in err and 'r001' not in err and no_arm_named(err)


# --- verdict helpers ----------------------------------------------------------------------------------------


def stub_sheet(rid: str, packet: str, **measures) -> None:
    '''A sheet and its measures file, as grade.py writes them, for stop and unblind.'''
    k = common.k_dir()
    write(k / 'sheets' / f'{rid}.txt', f'== {rid} {packet}\n')
    write_json(k / 'sheets' / f'{rid}.json', {'rid': rid, 'packet': packet, 'void': [], 'pending': [], 'volume': 4,
                                              'b_rows': 3, 'b_unparseable': 0, 'listed': None, 'cost': 1.0,
                                              'seconds': 10.0} | measures)


def verdict_reps(reps: list[tuple], batch: str = 'gateA1', extra: str = '') -> None:
    '''Audit reps (rid, arm, valid, P11, P8[, hits[, unsupported[, role[, replaces]]]]) with sheets and
    RESULTS.md lines.'''
    lines = ['# Plan 102 hand verdicts', '']
    for rid, arm, valid, p11, p8, *rest in reps:
        hits = rest[0] if len(rest) > 0 else 'none'
        unsupported = rest[1] if len(rest) > 1 else 0
        role = rest[2] if len(rest) > 2 else 'counted'
        plan((rid, 'audit', arm, role, *rest[3:4]), batch=batch)
        stub_sheet(rid, 'audit')
        if valid:
            lines += [f'{rid} valid', f'{rid} P11 {p11}', f'{rid} P8 {p8}', f'{rid} hits {hits}',
                      f'{rid} unsupported {unsupported}']
        else:
            lines.append(f'{rid} void')
    path = common.k_dir() / 'RESULTS.md'
    old = path.read_text() if path.exists() else ''
    write(path, old + '\n'.join(lines) + '\n' + extra)


def files_reps(reps: list[tuple], batch: str = 'gateF') -> None:
    '''Files reps (rid, packet, arm, valid, verdicts) with sheets and RESULTS.md lines.'''
    lines = []
    for rid, packet, arm, valid, verdicts in reps:
        plan((rid, packet, arm), batch=batch)
        stub_sheet(rid, packet)
        lines += [f'{rid} valid' if valid else f'{rid} void'] + ([f'{rid} {v}' for v in verdicts] if valid else [])
    path = common.k_dir() / 'RESULTS.md'
    old = path.read_text() if path.exists() else ''
    write(path, old + '\n'.join(lines) + '\n')


def run_stop(capsys, batch='gateA1') -> str:
    assert grade.main(['stop', batch]) == 0
    out, err = capsys.readouterr()
    assert err == ''
    return out


def run_unblind(capsys, gate: str) -> list[str]:
    assert grade.main(['unblind', gate]) == 0
    out, err = capsys.readouterr()
    assert err == ''
    return out.splitlines()



# --- input shapes the rules cover (mutant step 2) -------------------------------------------------------------


def test_v2_follows_a_symlink_out_of_and_into_the_folder(tmp_path):
    root = tmp_path / 'R' / 'r001' / 'work'
    (root / 'packet').mkdir(parents=True)
    (tmp_path / 'elsewhere').mkdir()
    (root / 'link').symlink_to(tmp_path / 'elsewhere')
    (tmp_path / 'alias').symlink_to(root)
    assert grade.outside('link/x.md', str(root)) is True
    assert grade.outside(str(tmp_path / 'alias' / 'packet' / 'x.md'), str(root)) is False
    assert grade.outside(str(root / 'packet' / 'x.md'), str(root)) is False


B_REPORT = '\n'.join([
    'L5 | deniedModels limits the picker | STALE | settings.md:1 | "a quote the docs lack" | Name deniedModels.',
    'B | 2.1.200 | max | changelog.md:224',
    'B | bad-label | x | changelog.md:1288',
    'B | 2.1.180 | other | changelog.md:77',
    'B | 2.1.170 | other | changelog.md:1703',
    '',
])


def test_the_audit_sheet_lists_b_rows_on_224_and_every_row_naming_denied_models(kit):
    text = one_rep(report=B_REPORT)
    assert section(text, 'B rows on changelog.md:1288, :1702 or :224:') == [
        '[B kept] B | 2.1.200 | max | changelog.md:224', '[B unparseable] B | bad-label | x | changelog.md:1288']
    assert section(text, 'rows naming deniedModels:') == [
        '[A L5 models.routing STALE quote not found] L5 | deniedModels limits the picker | STALE | settings.md:1 '
        '| "a quote the docs lack" | Name deniedModels.']
    assert section(text, 'kept corrections and C rows (P1 to P14 candidates):') == ['none']
    assert check_line(text, 'B rows') == 'B rows: 3 kept, 1 unparseable'


WINDOW_REPORT = '\n'.join([
    'hooks/README.md:80-86 | starts before | hooks.events | "A hook\'s exit code 2 blocks the call." | consistent',
    'hooks/README.md:84 | just before | hooks.events | "A hook\'s exit code 2 blocks the call." | consistent',
    'hooks/README.md:93-99 | ends after | hooks.events | "A hook\'s exit code 2 blocks the call." | consistent',
    'hooks/README.md:94 | just after | hooks.events | "A hook\'s exit code 2 blocks the call." | consistent',
    'hooks/README.md:70-100 | spans it | hooks.events | "A hook\'s exit code 2 blocks the call." | consistent',
    '',
])
REACH_REPORT = '\n'.join([
    'skills/x/references/b.md:2 | lost | skills.description | "no such guide text" | contradicts',
    'skills/x/SKILL.md:5 | fine | skills.description | "Write the description in third person." | consistent',
    '',
])


def test_the_readme_window_takes_overlapping_ranges_and_reach_takes_kept_rows_only(kit):
    readme = one_rep(packet='readme', report=WINDOW_REPORT)
    assert [line.split(' | ')[0] for line in section(readme, 'rows on hooks/README.md lines 85 to 93:')] == [
        '[F consistent kept] hooks/README.md:80-86', '[F consistent kept] hooks/README.md:93-99',
        '[F consistent kept] hooks/README.md:70-100']
    precision = one_rep(rid='r002', packet='precision', report=REACH_REPORT)
    assert check_line(precision, 'a kept row names a covered file') == 'a kept row names a covered file: no'
    assert section(precision, 'kept contradicts rows:') == ['none']


ARM_REFUSAL = 'grade.py: refused: an arm file is missing or unreadable\n'


def assert_nothing_graded() -> None:
    k = common.k_dir()
    assert not [p for p in (k / 'sheets', k / 'reports', k / 'settle') if p.exists() and any(p.iterdir())]


@pytest.mark.parametrize('arm', ['control', 'changed'])
def test_an_unreadable_arm_file_refuses_the_whole_batch(kit, capfd, arm):
    plan(('r001', 'readme', 'control'), ('r002', 'readme', 'changed'))
    rep_files('r001', 'readme', 'control', README_REPORT)
    rep_files('r002', 'readme', 'changed', README_REPORT)
    path = common.k_dir() / 'arms' / f'{arm}.md'
    path.chmod(0)
    try:
        assert grade.main(['b']) == 1
    finally:
        path.chmod(0o644)
    assert capfd.readouterr() == ('', ARM_REFUSAL)
    assert_nothing_graded()


def test_an_arm_file_that_is_not_utf8_refuses_the_whole_batch(kit, capfd):
    plan(('r001', 'readme', 'control'))
    rep_files('r001', 'readme', 'control', README_REPORT)
    (common.k_dir() / 'arms' / 'changed.md').write_bytes(b'---\nname: x\n---\n\xff\xfe body\n')
    assert grade.main(['b']) == 1
    assert capfd.readouterr() == ('', ARM_REFUSAL)
    assert_nothing_graded()


def test_rows_whose_claim_or_statement_holds_a_pipe_read_as_settle_reads_them(kit):
    audit = 'L5 | the list | limits models | PARTIAL | settings.md:1 | "Set `deniedModels` in managed settings to ' \
            'block a model." | Add the deny list.\n'
    text = one_rep(report=audit)
    assert [line.split('] ')[0] for line in section(text, 'kept corrections and C rows (P1 to P14 candidates):')] == [
        '[A L5 models.routing PARTIAL kept']
    files = 'skills/x/SKILL.md:13 | second | person | skills.description | "Write the description in third ' \
            'person." | contradicts\n'
    text = one_rep(rid='r002', packet='precision', report=files)
    assert [line.split('] ')[0] for line in section(text, 'kept contradicts rows:')] == [
        '[F skills/x/SKILL.md:13 skills.description, contradicts, on key']


def test_only_the_verifier_transcript_feeds_v1_to_v8(kit):
    other = [vassistant(use('x1', 'Read', file_path='/etc/hosts'), model='claude-haiku-4-5'), tool_result('x1', 'h'),
             att('nested_memory', content='deniedModels')]
    plan(('r001', 'readme', 'changed'))
    rep_files('r001', 'readme', 'changed', README_REPORT,
              transcripts=[verifier('r001', 'changed', README_REPORT), other])
    meta = next((common.k_dir() / 'results' / 'r001' / 'project').rglob('agent-a1.meta.json'))
    write_json(meta, {'agentType': 'Explore'})
    pilot_json(effort='xhigh', version='2.1.327', advisor=True)
    assert grade.main(['b']) == 0
    text = sheet('r001')
    assert [check_line(text, f'V{n}') for n in range(1, 9)] == [f'V{n}: ok' for n in range(1, 9)]


def test_a_transcript_record_holding_a_line_separator_is_read_whole(kit):
    '''Claude Code writes U+2028 and U+2029 raw inside JSON strings, so a
    transcript splits into records at newlines only.'''
    extra = (vassistant({'type': 'text', 'text': 'a quote\u2028with a line separator'},
                        use('t5', 'Read', file_path='/opt/y.md')), tool_result('t5', 'one\u2029two\x85three'))
    plan(('r001', 'readme', 'changed'))
    rep_files('r001', 'readme', 'changed', README_REPORT,
              transcripts=[verifier('r001', 'changed', README_REPORT, extra=extra)])
    path = next((common.k_dir() / 'results' / 'r001' / 'project').rglob('agent-a0.jsonl'))
    recs = verifier('r001', 'changed', README_REPORT, extra=extra)
    write(path, ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in recs))
    assert '\u2028' in path.read_text(encoding='utf-8')
    assert grade.main(['b']) == 0
    assert check_line(sheet('r001'), 'V2') == 'V2: void: Read /opt/y.md'


def test_the_report_skips_a_blank_result_and_another_subagents_result():
    records = verifier('r001', 'control', 'handback report')
    blank = stream('r001', 'readme', agent_text=' \n')
    assert grade.report_of(blank, records) == 'handback report'
    other = stream('r001', 'readme', [agent_call('r001', 'readme', subagent_type='Explore')], agent_text='explore text')
    assert grade.report_of(other, records) == 'handback report'


def test_usage_errors_print_the_usage_line_and_an_unplanned_rep_fails(kit, capfd):
    assert grade.USAGE == 'usage: grade.py <batch> | stop <batch> | unblind A|F'
    for argv in (['stop'], ['unblind'], ['unblind', 'B'], ['stop', 'b', 'x'], []):
        assert grade.main(argv) == 2
        assert capfd.readouterr().err == grade.USAGE + '\n'
    plan(('r001', 'readme', 'control'))
    with (common.k_dir() / 'batches' / 'b.txt').open('a') as f:
        f.write('r009\n')
    rep_files('r001', 'readme', 'control', README_REPORT)
    assert grade.main(['b']) == 1
    out, err = capfd.readouterr()
    assert err == 'grade.py: r009: not in plan.json\n' and 'r001: sheets/r001.txt' in out


def test_unblind_a_leaves_a_void_reps_measures_out(kit, capsys):
    gate_a(PASS_CONTROL + [None], PASS_CHANGED)
    stub_sheet('r006', 'audit', volume=50, b_rows=99)  # a void rep that ran and got a sheet
    lines = run_unblind(capsys, 'A')
    assert 'r006 control void' in lines
    assert not [line for line in lines if line.startswith('r006 control:')]
    assert 'corrections (DF21) | control | median 4, total 20' in lines
    assert lines[-1] == 'result: PASS'


def test_unblind_refuses_a_gate_with_no_reps(kit, capfd):
    files_reps([('r001', 'readme', 'control', True, ['readme89 no', 'unsupported 0'])])
    assert grade.main(['unblind', 'A']) == 1
    out, err = capfd.readouterr()
    assert (out, err) == ('', 'grade.py: refused: gate A has no reps yet\n')


def test_v2_reads_a_listed_path_at_the_start_of_a_result_line_only():
    '''Grep content lines hold raw file text; a form feed, U+2028 or U+0085
    in a matched line does not start a new listed path.'''
    text = (f'{ROOT}/packet/guide.md:5:see\x0c/etc/x\n{ROOT}/packet/guide.md:9:and\u2028/etc/y\n'
            f'{ROOT}/packet/guide.md:12:also\x85~/z\x0b../w')
    records = [vassistant(use('g1', 'Grep', pattern='see', path=f'{ROOT}/packet', output_mode='content')),
               tool_result('g1', text)]
    void, refused = grade.check_v2(records, ROOT)
    assert (void.status, void.detail, refused) == ('ok', '', [])


PROJECTS = '/Users/someone/.claude/projects'
SLUG = '-private-tmp-vrtest-r001-work'
OWN = f'{PROJECTS}/{SLUG}/{SID}/tool-results'  # the rep's own session's tool-results folder (plan 45's ruling 6)
OTHER_SID = '0a1b2c3d-0000-4000-8000-000000000002'


@pytest.mark.parametrize('path, void', [
    (f'{OWN}/toolu_01.txt', False),
    (OWN, False),
    (f'{OWN}/sub/toolu_02.txt', False),
    (f'{OWN}/../subagents/agent-a0.jsonl', True),
    (f'{PROJECTS}/{SLUG}/{OTHER_SID}/tool-results/toolu_01.txt', True),
    (f'{PROJECTS}/{SLUG}/{SID}/subagents/agent-a0.jsonl', True),
    (f'{PROJECTS}/{SLUG}/{SID}.jsonl', True),
    (f'{PROJECTS}/-private-tmp-vrtest-r002-work/{SID}/tool-results/toolu_01.txt', True),
    (f'{OWN}-old/toolu_01.txt', True),
])
def test_v2_treats_the_reps_own_tool_results_folder_as_inside(path, void):
    records = [vassistant(use('t1', 'Read', file_path=path)), tool_result('t1', 'text')]
    got, refused = grade.check_v2(records, ROOT, (OWN,))
    assert (got.status, got.detail, refused) == (('void', f'Read {path}') if void else ('ok', '')) + ([],)
    assert grade.check_v2(records, ROOT)[0].status == 'void'  # no exemption unless given


def test_v2_screens_grep_and_glob_against_the_own_tool_results_folder():
    records = [vassistant(use('g1', 'Grep', pattern='x', path=OWN), use('g2', 'Glob', pattern=f'{OWN}/*.txt'),
                          use('g3', 'Grep', pattern='y', path=f'{ROOT}/packet')),
               tool_result('g1', f'{OWN}/toolu_01.txt'), tool_result('g2', f'{OWN}/toolu_01.txt'),
               tool_result('g3', f'{OWN}/toolu_01.txt\n{PROJECTS}/{SLUG}/{OTHER_SID}/tool-results/t.txt')]
    got, _ = grade.check_v2(records, ROOT, (OWN,))
    assert got.detail == f'Grep result lists {PROJECTS}/{SLUG}/{OTHER_SID}/tool-results/t.txt'



@pytest.mark.parametrize('where, ok', [('own', True), ('other session', False), ('other slug', False),
                                       ('own subagents', False), ('own transcript', False)])
def test_a_sheet_exempts_the_reps_own_session_tool_results_only(kit, where, ok):
    projects = Path(os.environ['HOME']) / '.claude' / 'projects'
    slug = '-private-tmp-vr102-r001-work'  # where rep_files puts the session's own transcript
    path = {'own': projects / slug / SID / 'tool-results' / 'toolu_big.txt',
            'other session': projects / slug / OTHER_SID / 'tool-results' / 'toolu_big.txt',
            'other slug': projects / '-private-tmp-vr102-r009-work' / SID / 'tool-results' / 'toolu_big.txt',
            'own subagents': projects / slug / SID / 'subagents' / 'agent-a0.jsonl',
            'own transcript': projects / slug / f'{SID}.jsonl'}[where]
    for each in (slug + '/' + SID, slug + '/' + OTHER_SID, '-private-tmp-vr102-r009-work/' + SID):
        write(projects / each / 'tool-results' / 'toolu_big.txt', 'saved grep output\n')  # all three on disk
    extra = (vassistant(use('t5', 'Read', file_path=str(path))), tool_result('t5', 'saved grep output'))
    text = one_rep(packet='readme', report=README_REPORT,
                   transcripts=[verifier('r001', 'changed', README_REPORT, extra=extra)])
    assert check_line(text, 'V2') == ('V2: ok' if ok else f'V2: void: Read {path}')


@pytest.mark.parametrize('reps, named', [
    ([('r001', 'control', True, 'yes', 'yes'), ('r002', 'control', False, '', ''),
      ('r003', 'changed', True, 'yes', 'yes'), ('r004', 'changed', True, 'yes', 'yes')], 'r002'),
    ([('r001', 'control', True, 'no', 'yes'), ('r002', 'control', True, 'no', 'yes'),
      ('r003', 'changed', True, 'no', 'yes'), ('r004', 'changed', False, '', '')], 'r004'),
    ([('r001', 'changed', True, 'no', 'no'), ('r002', 'control', False, '', ''),
      ('r003', 'control', True, 'yes', 'yes'), ('r004', 'changed', False, '', '')], 'r002, r004'),
    ([('r001', 'control', False, '', ''), ('r002', 'control', False, '', ''),
      ('r003', 'changed', True, 'yes', 'yes'), ('r004', 'changed', True, 'yes', 'yes'),
      ('r005', 'control', True, 'yes', 'yes', 'none', 0, 'spare', 'r001')], 'r002'),
    ([('r001', 'control', True, 'yes', 'yes'), ('r002', 'control', False, '', ''),
      ('r003', 'changed', False, '', ''), ('r004', 'changed', True, 'yes', 'yes'),
      ('r005', 'control', False, '', '', 'none', 0, 'spare', 'r002')], 'r002, r003, r005'),
    ([('r001', 'control', False, '', ''), ('r002', 'control', False, '', ''),
      ('r003', 'changed', True, 'yes', 'yes'), ('r004', 'changed', True, 'yes', 'yes'),
      ('r005', 'control', False, '', '', 'none', 0, 'spare', 'r002'),
      ('r006', 'control', True, 'yes', 'yes', 'none', 0, 'spare', 'r005')], 'r001'),
])
def test_stop_refuses_while_a_side_is_short_and_names_void_reps_without_a_valid_spare(kit, capfd, reps, named):
    verdict_reps(reps)
    assert grade.main(['stop', 'gateA1']) == 1
    out, err = capfd.readouterr()
    assert (out, err) == ('', f'grade.py: refused: gateA1: these void reps have no valid spare yet: {named}\n')


def test_stop_reads_a_spare_chain_and_refuses_a_batch_too_small_for_the_first_wave(kit, capfd):
    verdict_reps([('r001', 'control', True, 'yes', 'yes'), ('r002', 'control', False, '', ''),
                  ('r003', 'changed', True, 'yes', 'yes'), ('r004', 'changed', True, 'yes', 'yes'),
                  ('r005', 'control', False, '', '', 'none', 0, 'spare', 'r002'),
                  ('r006', 'control', True, 'no', 'yes', 'none', 0, 'spare', 'r005')])
    assert grade.main(['stop', 'gateA1']) == 0
    assert capfd.readouterr().out == 'continue\n'
    verdict_reps([('r007', 'control', True, 'yes', 'yes'), ('r008', 'changed', True, 'yes', 'yes'),
                  ('r009', 'changed', True, 'yes', 'yes')], batch='gateA2')
    assert grade.main(['stop', 'gateA2']) == 1
    out, err = capfd.readouterr()
    assert (out, err) == ('', 'grade.py: refused: gateA2: too few valid reps for the first-wave rules\n')


def transcript_of(rid: str, name: str = 'agent-a0.jsonl') -> Path:
    return next((common.k_dir() / 'results' / rid / 'project').rglob(name))


@pytest.mark.parametrize('shape, want', [
    ('cut', 'V6: void: 1 transcript line(s) do not parse'),
    ('utf8', 'V6: void: 1 transcript line(s) do not parse'),
    ('array', 'V6: void: 1 transcript line(s) do not parse'),
    ('string', 'V6: void: 1 transcript line(s) do not parse'),
    ('null', 'V6: void: 1 transcript line(s) do not parse'),
    ('two', 'V6: void: 2 transcript line(s) do not parse'),
    ('blank', 'V6: ok'),
])
def test_a_verifier_transcript_line_that_does_not_parse_voids_the_rep(kit, shape, want):
    extra = (vassistant(use('t5', 'Read', file_path='/etc/hosts')), tool_result('t5', 'hosts'))
    plan(('r001', 'readme', 'changed'))
    rep_files('r001', 'readme', 'changed', README_REPORT,
              transcripts=[verifier('r001', 'changed', README_REPORT, extra=extra)])
    path = transcript_of('r001')
    lines = path.read_bytes().split(b'\n')
    i = next(n for n, line in enumerate(lines) if b'/etc/hosts' in line and b'"assistant"' in line)
    match shape:
        case 'cut':  # the reproduction: the outside Read was dropped silently, so V2 read ok
            lines[i] = lines[i][:lines[i].rindex(b'}')]
        case 'utf8':
            lines[i] = lines[i].replace(b'/etc/hosts', b'/etc/ho\xffsts')
        case 'array' | 'string' | 'null':
            lines.insert(i + 1, {'array': b'[1, 2]', 'string': b'"text"', 'null': b'null'}[shape])
        case 'two':
            lines[i] = lines[i][:lines[i].rindex(b'}')]
            lines.insert(i + 1, b'{not json')
        case 'blank':
            lines[i + 1:i + 1] = [b'', b'   ', b'\r']
    path.write_bytes(b'\n'.join(lines))
    assert grade.main(['b']) == 0
    text = sheet('r001')
    assert check_line(text, 'V6') == want
    assert 'V6' in check_line(text, 'void') or want == 'V6: ok'


def test_only_the_verifier_transcripts_lines_are_counted(kit):
    other = [vassistant(use('x1', 'Read', file_path='/tmp/x'), model='claude-haiku-4-5')]
    plan(('r001', 'readme', 'changed'))
    rep_files('r001', 'readme', 'changed', README_REPORT,
              transcripts=[verifier('r001', 'changed', README_REPORT), other])
    write_json(transcript_of('r001', 'agent-a1.meta.json'), {'agentType': 'Explore'})
    with transcript_of('r001', 'agent-a1.jsonl').open('ab') as f:
        f.write(b'{not json\n')
    main = next((common.k_dir() / 'results' / 'r001' / 'project').glob(f'*/{SID}.jsonl'))
    with main.open('ab') as f:
        f.write(b'[1]\n')
    assert grade.main(['b']) == 0
    assert check_line(sheet('r001'), 'V6') == 'V6: ok'


VALID_AUDIT = ['valid', 'P11 yes', 'P8 yes', 'hits none', 'unsupported 0']


def hand_verdicts(*lines: str) -> None:
    path = common.k_dir() / 'RESULTS.md'
    write(path, (path.read_text() if path.exists() else '') + ''.join(f'{line}\n' for line in lines))


@pytest.mark.parametrize('check', ['V1', 'V2', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9'])
@pytest.mark.parametrize('kind', ['void', 'pending'])
def test_a_valid_verdict_on_a_sheet_with_a_void_or_pending_check_is_refused(kit, capfd, check, kind):
    plan(('r001', 'audit', 'control'), batch='gateA1')
    stub_sheet('r001', 'audit', **{kind: [check]})
    hand_verdicts(*(f'r001 {v}' for v in VALID_AUDIT))
    for argv in (['stop', 'gateA1'], ['unblind', 'A']):
        assert grade.main(argv) == 1
        out, err = capfd.readouterr()
        assert out == '' and err == ('grade.py: refused: these reps are not ready: r001 (a valid verdict, but its '
                                     'sheet has a void or pending check)\n')


def test_a_v3_line_does_not_block_and_a_void_verdict_needs_no_clean_sheet(kit, capsys):
    plan(('r001', 'audit', 'control'), ('r002', 'audit', 'changed'), batch='gateA1')
    stub_sheet('r001', 'audit', void=['V3'])  # V3 stays a hand check
    stub_sheet('r002', 'audit')  # an ok sheet that the reader voids by hand
    hand_verdicts(*(f'r001 {v}' for v in VALID_AUDIT), 'r002 void')
    assert run_unblind(capsys, 'A')[-1] == 'result: UNSETTLED (too few valid reps: control 1 of 5, changed 0 of 5)'


def test_a_valid_verdict_needs_the_sheets_measures_file(kit, capfd):
    plan(('r001', 'audit', 'control'), batch='gateA1')
    stub_sheet('r001', 'audit')
    (common.k_dir() / 'sheets' / 'r001.json').unlink()
    hand_verdicts(*(f'r001 {v}' for v in VALID_AUDIT))
    assert grade.main(['unblind', 'A']) == 1
    assert capfd.readouterr().err == 'grade.py: refused: these reps are not ready: r001 (no sheet)\n'


def test_stop_and_unblind_refuse_a_valid_verdict_on_a_graded_void_or_pending_sheet(kit, capfd):
    plan(('r001', 'audit', 'control'), ('r002', 'audit', 'changed'), batch='gateA1')
    rep_files('r001', 'audit', 'control', None)  # no report: the sheet shows void: V6
    rep_files('r002', 'audit', 'changed', AUDIT_REPORT)  # graded before pilot.json: pending: V7, V8
    assert grade.main(['gateA1']) == 0
    assert check_line(sheet('r001'), 'void') == 'void: V6'
    assert check_line(sheet('r002'), 'pending') == 'pending: V7, V8'
    capfd.readouterr()
    hand_verdicts(*(f'{rid} {v}' for rid in ('r001', 'r002') for v in VALID_AUDIT))
    want = ('grade.py: refused: these reps are not ready: r001 (a valid verdict, but its sheet has a void or pending '
            'check); r002 (a valid verdict, but its sheet has a void or pending check)\n')
    for argv in (['stop', 'gateA1'], ['unblind', 'A']):
        assert grade.main(argv) == 1
        assert capfd.readouterr() == ('', want)
    pilot_json(effort='xhigh', version='2.1.327', advisor=True)
    assert grade.main(['gateA1']) == 0  # the controller regrades once the pilot record exists
    capfd.readouterr()
    assert grade.main(['unblind', 'A']) == 1
    assert capfd.readouterr().err == ('grade.py: refused: these reps are not ready: r001 (a valid verdict, but its '
                                      'sheet has a void or pending check)\n')


def test_a_rep_that_fails_prints_its_error_type_not_its_message(kit, capfd):
    '''A copy of the audit fixture that cannot be read fails the rep with a
    message that holds the fixture's path, which names an arm.'''
    plan(('r001', 'audit', 'control'), ('r002', 'readme', 'changed'))
    rep_files('r001', 'audit', 'control', AUDIT_REPORT)
    rep_files('r002', 'readme', 'changed', README_REPORT)
    index = common.k_dir() / 'fixtures' / 'audit-changed' / 'index.json'
    index.chmod(0)
    try:
        assert grade.main(['b']) == 1
    finally:
        index.chmod(0o644)
    out, err = capfd.readouterr()
    assert err == 'grade.py: r001: not graded (Error)\n' and 'r002: sheets/r002.txt' in out
    assert no_arm_named(out + err)


def test_unblind_a_short_after_the_spares_is_unsettled_not_fail(kit, capfd):
    '''The reproduction: the control is down to 1 valid rep after two void
    spares, and the changed arm misses P11 in its 2 (plan:171).'''
    verdict_reps([('r001', 'control', True, 'yes', 'yes'), ('r002', 'control', False, '', ''),
                  ('r003', 'changed', True, 'no', 'yes'), ('r004', 'changed', True, 'no', 'yes'),
                  ('r005', 'control', False, '', '', 'none', 0, 'spare', 'r002'),
                  ('r006', 'control', False, '', '', 'none', 0, 'spare', 'r005')])
    assert grade.main(['stop', 'gateA1']) == 1
    assert capfd.readouterr().err == ('grade.py: refused: gateA1: these void reps have no valid spare yet: '
                                      'r002, r005, r006\n')
    assert grade.main(['unblind', 'A']) == 0
    out, err = capfd.readouterr()
    assert err == '' and out.splitlines()[-1] == 'result: UNSETTLED (too few valid reps: control 1 of 5, changed 2 of 5)'


Y, N = ('yes', 'yes', 'none', 0), ('no', 'yes', 'none', 0)  # P11 met; P11 missed
NO_P8 = ('yes', 'no', 'none', 0)


@pytest.mark.parametrize('control, changed, want', [
    ([Y, None], [N, N], 'UNSETTLED (too few valid reps: control 1 of 5, changed 2 of 5)'),
    ([Y, None], [NO_P8, NO_P8], 'UNSETTLED (too few valid reps: control 1 of 5, changed 2 of 5)'),
    ([Y, Y], [N, None], 'UNSETTLED (first wave: the control meets P11 in 2 valid reps)'),
    ([Y, Y, None], [N, N], 'UNSETTLED (first wave: the control meets P11 in 2 valid reps)'),
    ([N, N], [N, N], 'FAIL (first wave: the changed arm misses P11 or P8 in 2 valid reps)'),
    ([N, N], [NO_P8, NO_P8], 'FAIL (first wave: the changed arm misses P11 or P8 in 2 valid reps)'),
    ([N, N], [N, None], 'UNSETTLED (too few valid reps: control 2 of 5, changed 1 of 5)'),
    ([Y, N, N, N, None], [N, N, None, None, None],
     'FAIL (first wave: the changed arm misses P11 or P8 in 2 valid reps)'),
    ([Y, N, N, N, None], [Y, Y, None, None, None], 'UNSETTLED (too few valid reps: control 4 of 5, changed 2 of 5)'),
])
def test_unblind_a_applies_the_first_wave_fail_only_with_two_valid_reps_in_each_arm(kit, capsys, control, changed,
                                                                                      want):
    gate_a(control, changed)
    assert run_unblind(capsys, 'A')[-1] == f'result: {want}'

# --- the plan's values ----------------------------------------------------------------------------------------


def test_the_constants_hold_the_plans_values():
    assert grade.MODEL == 'claude-sonnet-5-5'
    assert grade.ADVISOR_MODEL == 'claude-opus-5-5'
    assert grade.AGENT_KEYS == {'description', 'subagent_type', 'prompt', 'model'}
    assert grade.AGENT_MODEL == 'sonnet'
    assert grade.FENCED_TOOLS == ('Read', 'Grep', 'Glob')
    assert grade.TMP_ALIASES == ('/tmp', '/System/Volumes/Data/private/tmp')
    assert grade.CHANGELOG_LINES == (1288, 1702, 224)
    assert grade.DENIED == 'deniedModels'
    assert (grade.README_FILE, grade.README_LINES) == ('hooks/README.md', (85, 93))
    assert (grade.A_HITS_MIN, grade.A_CONTROL_P11_MAX, grade.STOP_COUNT) == (4, 1, 2)
    assert (grade.DF7_MARGIN, grade.UNSUPPORTED_MAX, grade.DF8_SLACK, grade.REACH_MIN) == (3, 2, 1, 2)
    assert grade.RETENTION == ('P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P9', 'P13', 'P14')
    assert grade.SECONDARY == ('P7', 'P10', 'P12')
    assert grade.GATES == {'A': ('audit',), 'F': ('readme', 'precision')}
    assert grade.GATE_ROLES == ('counted', 'spare')
    assert common.MARKERS == ('deniedModels', 'availableModels', 'effortLevel', 'README.md:89')
    assert {p: common.PACKETS[p]['reps'] for p in ('audit', 'readme', 'precision')} == {
        'audit': 5, 'readme': 3, 'precision': 3}


# --- V1 -------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('calls, verifiers, extra, want', [
    ('none', 1, (), '0 Agent calls'),
    ('two', 1, (), '2 Agent calls'),
    ('type', 1, (), "subagent_type 'general-purpose'"),
    ('prompt', 1, (), 'the dispatch prompt differs'),
    ('background', 1, (), 'Agent parameters: run_in_background'),
    ('background', 1, ('run_in_background',), ''),
    ('no-model', 1, (), ''),
    ('task', 1, (), ''),
    ('advisor', 1, (), ''),
    ('forwarded', 1, (), ''),
    ('ok', 0, (), '0 verifier transcripts'),
    ('ok', 2, (), '2 verifier transcripts'),
])
def test_v1_input_shapes(calls, verifiers, extra, want):
    rid, packet = 'r001', 'readme'
    call = agent_call(rid, packet)
    shapes = {
        'none': [], 'two': [call, agent_call(rid, packet, uid='toolu_main2')],
        'type': [agent_call(rid, packet, subagent_type='general-purpose')],
        'prompt': [agent_call(rid, packet, prompt=dispatch(rid, packet) + ' Be quick.')],
        'background': [agent_call(rid, packet, run_in_background=True)],
        'no-model': [{**call, 'input': {k: v for k, v in call['input'].items() if k != 'model'}}],
        'task': [{**call, 'name': 'Task'}], 'ok': [call],
        'advisor': [call, {'type': 'server_tool_use', 'id': 'srv1', 'name': 'advisor', 'input': {}}],
        'forwarded': [call],
    }
    events = stream(rid, packet, shapes[calls])
    if calls == 'forwarded':  # the verifier's own calls, forwarded into the stream, are not the main session's
        events.insert(2, assistant(use('toolu_v1', 'Read', file_path='/x'), parent='toolu_main1'))
    got = grade.check_v1(events, verifiers, dispatch(rid, packet), extra)
    assert (got.status, got.detail) == (('void', want) if want else ('ok', ''))
    if calls == 'prompt':
        assert 'Be quick' not in got.detail


# --- V2 -------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('path, out', [
    (f'{ROOT}/packet/index.json', False),
    ('packet/guide.md', False),
    (ROOT, False),
    ('/tmp/vrtest/r001/work/docs/a.md', False),
    ('/System/Volumes/Data/private/tmp/vrtest/r001/work/docs/a.md', False),
    ('/private/tmp/vrtest/r001/work/../../r002/work/x', True),
    ('../x', True),
    ('packet/../../tmp/x', True),
    ('/private/tmp/vrtest/r001/workshop/x', True),
    ('/tmpfoo/vrtest/r001/work/x', True),
    ('~/notes.md', True),
    ('/Users/someone/x', True),
    ('/private/tmp/vrtest/r001/tmp/scratch.txt', True),
])
def test_v2_resolves_each_path_shape(path, out):
    assert grade.outside(path, ROOT) is out


def test_v2_maps_both_tmp_aliases_to_private_tmp():
    assert grade.resolve('/tmp/vrtest/a', ROOT) == '/private/tmp/vrtest/a'
    assert grade.resolve('/System/Volumes/Data/private/tmp/vrtest/a', ROOT) == '/private/tmp/vrtest/a'
    assert grade.resolve('docs/../packet/x', ROOT) == f'{ROOT}/packet/x'
    assert grade.resolve('~/a', ROOT) == str(Path(os.environ['HOME']).resolve() / 'a')


def test_v2_screens_grep_and_glob_calls_and_their_listed_paths():
    records = [vassistant(use('g1', 'Grep', pattern='x', path='/Users/someone'),
                          use('g2', 'Glob', pattern='/Users/someone/**/*.md'),
                          use('g3', 'Grep', pattern='deniedModels'),
                          use('g4', 'Glob', pattern='**/*.md', path=f'{ROOT}/docs'),
                          use('g5', 'Grep', pattern='y', path=f'{ROOT}/packet', output_mode='content'),
                          use('g6', 'Glob', pattern='../**/*.md'),
                          use('g7', 'Grep', pattern='z', path='/opt/elsewhere')),
               tool_result('g1', 'Found 0 files'), tool_result('g2', 'No files found'),
               tool_result('g3', f'Found 2 files\n{ROOT}/docs/a.md\n/private/tmp/vrtest/r002/work/docs/b.md'),
               tool_result('g4', f'{ROOT}/docs/a.md\n{ROOT}/docs/sub/c.md'),
               tool_result('g5', f'{ROOT}/packet/guide.md:5:text\n~/x.md:3:more'),
               tool_result('g6', '../other/x.md'),
               tool_result('g7', 'refused', error=True)]
    void, refused = grade.check_v2(records, ROOT)
    parts = void.detail.split('; ')
    assert parts == ['Grep /Users/someone', 'Glob /Users/someone/', 'Grep result lists /private/tmp/vrtest/r002/'
                     'work/docs/b.md', 'Grep result lists ~/x.md', 'Glob ../', 'Glob result lists ../other/x.md']
    assert refused == ['Grep /opt/elsewhere']


def test_v2_a_call_with_no_result_counts_as_returned():
    void, refused = grade.check_v2([vassistant(use('t1', 'Read', file_path='/etc/hosts'))], ROOT)
    assert (void.status, void.detail, refused) == ('void', 'Read /etc/hosts', [])
    assert grade.check_v2([vassistant(use('t1', 'Write', file_path='/etc/hosts'))], ROOT)[0].status == 'ok'


# --- V3 and V4 ------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('marker', common.MARKERS)
def test_v3_screens_every_marker_in_an_attachment(marker):
    got = grade.check_v3([att('nested_memory', content=f'see {marker} here')])
    assert got.status == 'hits' and f'attachment nested_memory: {marker}' in got.detail


def test_v3_skips_the_contract_body_and_tool_results_but_screens_the_rest():
    records = [att('prompt_snapshot', systemPrompt=['contract naming deniedModels', 'environment']),
               tool_result('t1', 'docs text with deniedModels and effortLevel'),
               vassistant(use('t2', 'Grep', pattern='availableModels'))]
    assert grade.check_v3(records) == grade.Check('ok')
    later = [att('prompt_snapshot', systemPrompt=['contract', 'a later part naming effortLevel'])]
    assert grade.check_v3(later).detail.startswith('attachment prompt_snapshot: effortLevel')
    system = [{'type': 'system', 'subtype': 'note', 'content': 'availableModels'}]
    assert 'system record: availableModels' in grade.check_v3(system).detail
    rendered = [{'type': 'attachment', 'attachment': {'type': 'hook_success'}, 'rendered': [{'content': 'deniedModels'}]}]
    assert 'attachment hook_success: deniedModels' in grade.check_v3(rendered).detail


@pytest.mark.parametrize('records, want', [
    ([att('session_context', context={'note': 'none'})], ''),
    ([att('instructions', content='CLAUDE.md text')], 'an instructions attachment'),
    ([att('session_context', context={'gitStatus': 'Current branch: main'})], 'a session_context that holds gitStatus'),
    ([{'type': 'attachment', 'attachment': {'type': 'session_context', 'context': {}},
       'rendered': [{'content': '# gitStatus\nbranch'}]}], 'a session_context that holds gitStatus'),
])
def test_v4_input_shapes(records, want):
    got = grade.check_v4(records)
    assert (got.status, got.detail) == (('void', want) if want else ('ok', ''))


# --- V5 -------------------------------------------------------------------------------------------------------


def test_v5_reads_the_arm_body_without_its_frontmatter():
    assert grade.arm_body('---\nname: x\ntools: Read\n---\n\nBody line.\nSecond.\n') == 'Body line.\nSecond.'
    assert grade.arm_body('No frontmatter.\n') == 'No frontmatter.'
    one = [att('prompt_snapshot', systemPrompt=['Body line.\nSecond.', 'env'])]
    assert grade.check_v5(one, grade.arm_body('---\nname: x\n---\n\nBody line.\nSecond.\n')).status == 'ok'
    assert grade.check_v5([att('prompt_snapshot', systemPrompt=[])], 'Body').status == 'void'
    assert grade.check_v5([att('prompt_snapshot', systemPrompt=['Body plus more'])], 'Body').status == 'void'


# --- V6 and the report ----------------------------------------------------------------------------------------


GOOD_STATUS = {'exit': 0, 'timed_out': False, 'interrupted': False, 'seconds': 5.0, 'strip_ok': True}


@pytest.mark.parametrize('case, want', [
    ('ok', ''),
    ('no stream', 'the stream does not parse'),
    ('no result', 'no result record'),
    ('error', 'a result is an error'),
    ('earlier error', 'a result is an error'),
    ('budget subtype', 'a budget stop'),
    ('budget reason', 'a budget stop'),
    ('budget refused', 'a budget stop'),
    ('failed', 'a subagent failed or was killed'),
    ('killed', 'a subagent failed or was killed'),
    ('failed true', 'a subagent failed or was killed'),
    ('budget true', 'a budget stop'),
    ('timeout', 'timed out'),
    ('interrupted', 'interrupted'),
    ('exit null', 'no exit code'),
    ('exit 1', 'exit 1'),
    ('strip', 'credential_expires_at survived the strip'),
    ('left', 'credential_expires_at remains in 1 file(s)'),
    ('no status', 'no status.json'),
    ('no report', 'no report: neither a finished Agent result nor a handback'),
])
def test_v6_input_shapes(tmp_path, case, want):
    events = stream('r001', 'readme')
    result, status, report = result_record(), dict(GOOD_STATUS), 'a report | x'
    match case:
        case 'no stream':
            events = None
        case 'no result':
            events, result = [e for e in events if e['type'] != 'result'], None
        case 'error':
            result = result_record(is_error=True, subtype='error_during_execution')
            events[-1] = result
        case 'earlier error':
            events.insert(-1, result_record(is_error=True))
        case 'budget subtype':
            result = events[-1] = result_record(subtype='error_max_budget_usd')
        case 'budget reason':
            result = events[-1] = result_record(terminal_reason='max_budget_reached')
        case 'budget refused':
            result = events[-1] = result_record(subagent_stats={'failed': 0, 'killed': {}, 'refused': {'budget': 1}})
        case 'failed':
            result = events[-1] = result_record(subagent_stats={'failed': 1, 'killed': {}, 'refused': {}})
        case 'failed true':
            result = events[-1] = result_record(subagent_stats={'failed': True, 'killed': {}, 'refused': {}})
        case 'budget true':
            result = events[-1] = result_record(subagent_stats={'failed': 0, 'killed': {}, 'refused': {'budget': True}})
        case 'killed':
            result = events[-1] = result_record(subagent_stats={'failed': 0, 'killed': {'system': 1}, 'refused': {}})
        case 'timeout':
            status |= {'exit': None, 'timed_out': True}
        case 'interrupted':
            status |= {'exit': None, 'interrupted': True}
        case 'exit null':
            status |= {'exit': None}
        case 'exit 1':
            status |= {'exit': 1}
        case 'strip':
            status |= {'strip_ok': False}
        case 'left':
            write(tmp_path / 'res' / 'project' / 'x.jsonl', '{"credential_expires_at": 1}\n')
        case 'no status':
            status = None
        case 'no report':
            report = None
    (tmp_path / 'res').mkdir(exist_ok=True)
    got = grade.check_v6(events, result, status, tmp_path / 'res', report)
    assert (got.status, got.detail) == (('void', want) if want else ('ok', ''))


def test_the_report_is_a_finished_agent_result_or_else_the_handback():
    events = stream('r001', 'readme')
    records = verifier('r001', 'control', 'handback report')
    assert grade.report_of(events, records) == 'handback report'
    finished = stream('r001', 'readme', agent_text='finished report')
    assert grade.report_of(finished, records) == 'finished report'
    error = stream('r001', 'readme')
    error[2] = tool_result('toolu_main1', 'agent failed', error=True)
    assert grade.report_of(error, records) == 'handback report'
    two = records + [vassistant(use('toolu_v10', 'SubagentHandback', message='second handback'))]
    assert grade.report_of(events, two) == 'second handback'
    last_text = verifier('r001', 'control', None) + [vassistant({'type': 'text', 'text': 'my last words | x'})]
    assert grade.report_of(events, last_text) is None  # never the verifier's own last text, nor result.result


def test_the_report_skips_the_completion_notice_for_the_handback():
    '''The completion notice, with its leading spaces and its usage tail or
    without them, is no report: the verifier's hand-back is.'''
    records = verifier('r001', 'changed', 'handback report')
    assert grade.report_of(stream('r001', 'audit', agent_text=COMPLETION), records) == 'handback report'
    assert grade.report_of(stream('r001', 'audit', agent_text=COMPLETION.lstrip()), records) == 'handback report'


def test_a_completion_notice_with_no_handback_leaves_no_report():
    events = stream('r001', 'audit', agent_text=COMPLETION)
    assert grade.report_of(events, verifier('r001', 'changed', None)) is None


def test_a_notice_counts_only_at_the_start_of_the_result():
    '''A notice is known by its start, after any leading white space. A
    finished result that opens with other text is the report, even when a
    notice's words come later in it.'''
    records = verifier('r001', 'changed', 'handback report')
    assert grade.report_of(stream('r001', 'audit', agent_text='\n\t ' + COMPLETION), records) == 'handback report'
    for text in ('finished report', 'A finished report.\n' + COMPLETION, 'A finished report.\n' + LAUNCH):
        assert grade.report_of(stream('r001', 'audit', agent_text=text), records) == text


def test_the_report_skips_each_notice_an_error_and_a_blank_result():
    records = verifier('r001', 'changed', 'handback report')
    for text in (COMPLETION, LAUNCH, '  ' + LAUNCH, ' \n', ''):
        assert grade.report_of(stream('r001', 'audit', agent_text=text), records) == 'handback report', repr(text)
    error = stream('r001', 'audit')
    error[2] = tool_result('toolu_main1', 'agent failed', error=True)
    assert grade.report_of(error, records) == 'handback report'


def test_the_last_handback_is_the_report_after_a_completion_notice():
    two = verifier('r001', 'changed', 'first handback') + [
        vassistant(use('toolu_v10', 'SubagentHandback', message='second handback'))]
    assert grade.report_of(stream('r001', 'audit', agent_text=COMPLETION), two) == 'second handback'


# --- V7 and V8 ------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('records, pilot, is_pilot, want', [
    ([vassistant(), vassistant()], {'effort': 'xhigh', 'version': '2.1.327'}, False, ('ok', '')),
    ([vassistant(), vassistant(model='<synthetic>')], {'effort': 'xhigh', 'version': '2.1.327'}, False,
     ('void', 'model <synthetic>')),
    ([vassistant(model='claude-haiku-4-5')], None, False, ('void', 'model claude-haiku-4-5')),
    ([vassistant(effort='max')], {'effort': 'xhigh', 'version': '2.1.327'}, False,
     ('void', 'effort max where the pilot had xhigh')),
    ([vassistant(version='2.1.330')], {'effort': 'xhigh', 'version': '2.1.327'}, False,
     ('void', 'version 2.1.330 where the pilot had 2.1.327')),
    ([vassistant()], {'effort': 'xhigh'}, False, ('pending', 'pilot.json gives no effort and version yet')),
    ([vassistant()], None, False, ('pending', 'pilot.json gives no effort and version yet')),
    ([vassistant(), vassistant()], None, True, ('ok', 'effort xhigh, version 2.1.327')),
    ([vassistant(), vassistant(effort='high')], None, True, ('void', 'effort or version varies: high, xhigh; 2.1.327')),
    ([vassistant(model='claude-opus-5-5')], None, True, ('void', 'model claude-opus-5-5')),
    ([], {'effort': 'xhigh', 'version': '2.1.327'}, False, ('void', 'no assistant record')),
])
def test_v7_input_shapes(records, pilot, is_pilot, want):
    got = grade.check_v7(records, pilot, is_pilot)
    assert (got.status, got.detail) == want


@pytest.mark.parametrize('records, pilot, want', [
    ([att('advisor_tool', available=True, model='claude-opus-5-5')] * 2, {'advisor': True}, ('ok', '')),
    ([att('advisor_tool', available=False, model='claude-opus-5-5')], {'advisor': True},
     ('void', 'an advisor attachment is unavailable or not claude-opus-5-5')),
    ([att('advisor_tool', available=True, model='claude-sonnet-5-5')], {'advisor': True},
     ('void', 'an advisor attachment is unavailable or not claude-opus-5-5')),
    ([att('advisor_tool', available=True, model='claude-opus-5-5'), att('advisor_tool', available=False)],
     {'advisor': True}, ('void', 'an advisor attachment is unavailable or not claude-opus-5-5')),
    ([], {'advisor': True}, ('void', 'no advisor attachment, where production had one')),
    ([att('advisor_tool', available=True, model='claude-opus-5-5')], {'advisor': False},
     ('void', 'an advisor attachment, where production had none')),
    ([att('model', identity={})], {'advisor': False}, ('ok', '')),
    ([], {'effort': 'xhigh'}, ('pending', 'pilot.json gives no production advisor fact yet')),
])
def test_v8_input_shapes(records, pilot, want):
    got = grade.check_v8(records, pilot)
    assert (got.status, got.detail) == want


def test_v7_and_v8_read_pilot_json_on_the_sheet(kit):
    plan(('r001', 'readme', 'control'), ('r002', 'readme', 'changed'), ('r003', 'audit', 'changed', 'pilot'))
    rep_files('r001', 'readme', 'control', README_REPORT)
    rep_files('r002', 'readme', 'changed', README_REPORT,
              transcripts=[verifier('r002', 'changed', README_REPORT, effort='high')])
    rep_files('r003', 'audit', 'changed', AUDIT_REPORT)
    assert grade.main(['b']) == 0
    assert check_line(sheet('r001'), 'V7') == 'V7: pending: pilot.json gives no effort and version yet'
    assert check_line(sheet('r001'), 'V8') == 'V8: pending: pilot.json gives no production advisor fact yet'
    assert check_line(sheet('r001'), 'pending') == 'pending: V7, V8'
    assert check_line(sheet('r003'), 'V7') == 'V7: ok: effort xhigh, version 2.1.327'
    pilot_json(effort='xhigh', version='2.1.327', advisor=True)
    assert grade.main(['b']) == 0
    assert check_line(sheet('r001'), 'V7') == 'V7: ok'
    assert check_line(sheet('r001'), 'V8') == 'V8: ok'
    assert check_line(sheet('r001'), 'void') == 'void: none'
    assert check_line(sheet('r001'), 'pending') == 'pending: none'
    assert check_line(sheet('r002'), 'V7') == 'V7: void: effort high where the pilot had xhigh'
    assert check_line(sheet('r002'), 'void') == 'void: V7'
    pilot_json(effort='xhigh', version='2.1.327', advisor=False)
    assert grade.main(['b']) == 0
    assert check_line(sheet('r001'), 'V8') == 'V8: void: an advisor attachment, where production had none'


def test_v1_reads_the_pilots_agent_parameter_ruling(kit):
    plan(('r001', 'readme', 'control'))
    events = stream('r001', 'readme', [agent_call('r001', 'readme', run_in_background=True)])
    rep_files('r001', 'readme', 'control', README_REPORT, events=events)
    assert grade.main(['b']) == 0
    assert check_line(sheet('r001'), 'V1') == 'V1: void: Agent parameters: run_in_background'
    pilot_json(effort='xhigh', version='2.1.327', advisor=True, agent_params=['run_in_background'])
    assert grade.main(['b']) == 0
    assert check_line(sheet('r001'), 'V1') == 'V1: ok'


# --- V9 (D5: a peer session) ----------------------------------------------------------------------------------

FOREIGN = {'kind': 'peer', 'name': 'another-session', 'fromSession': 'Another session',
           'from': '/private/tmp/vrtest-messaging/other.sock', 'body': 'a message from another session'}
TASK_NOTE = {'kind': 'task-notification', 'producer': 'session-task', 'runId': 'run-1'}
NOT_HANDBACK = "V9: void: 1 peer-origin record(s) that are not the verifier's hand-back"


def handback(agent='a0', **changes) -> dict:
    '''A subagent's background hand-back, in the shape the probe rep's stream
    and main transcript held it.'''
    return {'kind': 'peer', 'from': agent, 'senderTaskId': agent, 'name': 'cc-guide-verifier',
            'body': 'the report', 'handback': True, 'handbackReportText': 'the report'} | changes


def user_with(origin) -> dict:
    return {'type': 'user', 'origin': origin, 'message': {'role': 'user', 'content': 'a message'}}


def init_record(tools=('Agent', 'Read', 'Grep', 'Glob')) -> dict:
    return {'type': 'system', 'subtype': 'init', 'session_id': SID, 'tools': list(tools)}


def v9_sheet(*, events=(), main=(), extra=(), init=None, files=()) -> str:
    '''Grade r001 (audit, changed, after the pilot) and return its sheet. The
    stream gets `events` after its first result and `init` in place of its
    init record; the main transcript gets `main`, the verifier transcript
    `extra`. `files` are paths under the session's project folder to create
    (a trailing / makes a folder).'''
    plan(('r001', 'audit', 'changed'), batch='gateA1')
    stream_events = stream('r001', 'audit', results=[result_record(result_index=0), *events])
    if init is not None:
        stream_events[0] = init
    res = rep_files('r001', 'audit', 'changed', AUDIT_REPORT, events=stream_events,
                    main=[att('skill_listing', content='none'), *main],
                    transcripts=[verifier('r001', 'changed', AUDIT_REPORT, extra=tuple(extra))])
    slug = res / 'project' / '-private-tmp-vr102-r001-work'
    for name in files:
        if name.endswith('/'):
            (slug / name).mkdir(parents=True)
        else:
            write(slug / name, '{}\n')
    pilot_json(effort='xhigh', version='2.1.327', advisor=True)
    assert grade.main(['gateA1']) == 0
    return sheet('r001')


def test_v9_passes_the_probe_reps_real_shapes(kit):
    '''The probe rep's shapes, synthetic: the init record lists no
    cross-session tool and comes again each turn; the verifier's background
    hand-back reaches the stream as a result at result_index 1 and the main
    transcript as a user record; a task-notification result at result_index 2
    with an empty result ends the run; a classifier context holds a null
    `origin`.'''
    null_origin = {'type': 'user', 'serverClassifierContext': {'context': {'git_state': {'visibility': {
        'origin': None}}}}}
    text = v9_sheet(events=[init_record(), result_record(result_index=1, result='the report', origin=handback()),
                            init_record(), result_record(result_index=2, result='', origin=TASK_NOTE)],
                    main=[user_with(handback()), user_with(TASK_NOTE), null_origin], extra=[null_origin])
    assert check_line(text, 'V9') == 'V9: ok'
    assert [line.split(':')[0] for line in text.splitlines()[1:10]] == [f'V{n}' for n in range(1, 10)]
    assert check_line(text, 'void') == 'void: none'


def test_v9_passes_a_task_notification_result_at_result_index_2(kit):
    text = v9_sheet(events=[result_record(result_index=2, result='', origin=TASK_NOTE)])
    assert check_line(text, 'V9') == 'V9: ok'


@pytest.mark.parametrize('where', ['stream result', 'stream user', 'stream deep', 'main', 'verifier'])
def test_v9_voids_a_foreign_peer_message_in_any_record_the_grader_reads(kit, where):
    deep = {'type': 'user', 'message': {'role': 'user', 'content': [{'type': 'text', 'text': 'x',
                                                                     'meta': {'origin': FOREIGN}}]}}
    place = {'stream result': {'events': [result_record(result_index=1, origin=FOREIGN)]},
             'stream user': {'events': [user_with(FOREIGN)]}, 'stream deep': {'events': [deep]},
             'main': {'main': [user_with(FOREIGN)]}, 'verifier': {'extra': [user_with(FOREIGN)]}}[where]
    text = v9_sheet(**place)
    assert check_line(text, 'V9') == NOT_HANDBACK
    assert check_line(text, 'void') == 'void: V9'


@pytest.mark.parametrize('origin, files', [
    (handback('a7'), ()),
    (handback(handback=False), ()),
    (handback(handback=1), ()),
    ({key: value for key, value in handback().items() if key != 'handback'}, ()),
    (handback() | {'from': 'a1'}, (f'{SID}/subagents/agent-a1.jsonl',)),
    (handback(''), (f'{SID}/subagents/agent-.jsonl',)),
    (handback(['a0']), ()),
    (handback('a5'), (f'{SID}/subagents/agent-a5.jsonl/',)),
    (handback('b0'), (f'{OTHER_SID}/subagents/agent-b0.jsonl',)),
], ids=['no transcript file', 'handback false', 'handback 1', 'no handback key', 'senderTaskId is not from',
        'empty senderTaskId', 'senderTaskId not a string', 'a folder, not a file', "another session's transcript"])
def test_v9_exempts_only_the_verifiers_own_handback(kit, origin, files):
    '''The hand-back: handback is True, senderTaskId is a non-empty string
    equal to from, and agent-<senderTaskId>.jsonl is a file in the rep's own
    session's subagents/ folder. Fail any one, and the peer origin voids.'''
    text = v9_sheet(events=[result_record(result_index=1, origin=origin)], files=files)
    assert check_line(text, 'V9') == NOT_HANDBACK


def test_v9_counts_records_not_origins_and_reads_only_origin_objects(kit):
    twice = user_with(FOREIGN) | {'message': {'role': 'user', 'content': [{'type': 'text', 'text': 'x',
                                                                           'origin': FOREIGN}]}}
    no_signal = {'type': 'user', 'source': {'kind': 'peer'}, 'origin': 'peer', 'message': {'content': 'x'}}
    text = v9_sheet(events=[twice, result_record(result_index=1, origin=FOREIGN), no_signal])
    assert check_line(text, 'V9') == "V9: void: 2 peer-origin record(s) that are not the verifier's hand-back"


@pytest.mark.parametrize('tool', ['ListAgents', 'SendMessage', 'PushNotification', 'RemoteTrigger'])
def test_v9_voids_a_cross_session_tool_in_the_init_record(kit, tool):
    text = v9_sheet(init=init_record(('Agent', 'Read', tool, 'Glob')))
    assert check_line(text, 'V9') == f'V9: void: cross-session tool in the init record: {tool}'
    assert check_line(text, 'void') == 'void: V9'


def test_v9_names_each_cross_session_tool_of_a_later_init_record_in_order(kit):
    later = init_record(('RemoteTrigger', 'Agent', 'SendMessage', 'PushNotification', 'ListAgents'))
    text = v9_sheet(events=[later, result_record(result_index=1)])
    assert check_line(text, 'V9') == ('V9: void: cross-session tool in the init record: ListAgents, SendMessage, '
                                      'PushNotification, RemoteTrigger')


@pytest.mark.parametrize('init', [
    {'type': 'system', 'subtype': 'init', 'session_id': SID},
    init_record(('Agent', 'Read', 'mcp__srv__SendMessage', 'SendMessages', 'listagents')),
], ids=['no tools', 'names that only resemble one'])
def test_v9_passes_an_init_record_without_a_cross_session_tool(kit, init):
    assert check_line(v9_sheet(init=init), 'V9') == 'V9: ok'


def test_v9_gives_both_reasons_and_prints_no_origin_content(kit, capfd):
    loud = {'kind': 'peer', 'name': 'changed', 'fromSession': 'the control session',
            'from': '/private/tmp/arms/changed.md.sock', 'body': 'control and changed: arms/control.md'}
    text = v9_sheet(init=init_record(('Agent', 'SendMessage')), events=[result_record(result_index=1, origin=loud)],
                    main=[user_with(loud)], extra=[user_with(loud)])
    assert check_line(text, 'V9') == ("V9: void: 3 peer-origin record(s) that are not the verifier's hand-back; "
                                      'cross-session tool in the init record: SendMessage')
    out, err = capfd.readouterr()
    assert no_arm_named(text + out + err), text + out + err


@pytest.mark.parametrize('stream_text, v6', [
    ('', 'V6: void: no report: neither a finished Agent result nor a handback'),
    ('{not json\n', 'V6: void: the stream does not parse; no report: neither a finished Agent result nor a handback'),
], ids=['no init record', 'a stream that does not parse'])
def test_v9_passes_a_stream_it_cannot_read_and_other_checks_void_the_rep(kit, stream_text, v6):
    '''With no init record there is no session, so no transcript is read:
    V1 and V6 void the rep, and V9 has nothing to screen.'''
    plan(('r001', 'audit', 'changed'), batch='gateA1')
    res = rep_files('r001', 'audit', 'changed', AUDIT_REPORT)
    path = res / 'stream.jsonl'
    path.write_text(stream_text or ''.join(json.dumps(e) + '\n' for e in stream('r001', 'audit')[1:]))
    pilot_json(effort='xhigh', version='2.1.327', advisor=True)
    assert grade.main(['gateA1']) == 0
    text = sheet('r001')
    assert check_line(text, 'V9') == 'V9: ok'
    assert check_line(text, 'V6') == v6
    assert check_line(text, 'void') == 'void: V1, V5, V6, V7, V8'


@pytest.mark.parametrize('line', ['plain text from stderr', '[1, 2]'], ids=['text', 'json-not-object'])
def test_v6_voids_a_stream_with_a_line_that_is_no_json_object(kit, line):
    '''A stream line that is no JSON object makes the stream not parse, though every
    other line is a good record; a blank line still does not count.'''
    plan(('r001', 'audit', 'changed'), batch='gateA1')
    res = rep_files('r001', 'audit', 'changed', AUDIT_REPORT)
    events = stream('r001', 'audit')
    path = res / 'stream.jsonl'
    path.write_text(''.join(json.dumps(e) + '\n' for e in events[:2]) + line + '\n\n'
                    + ''.join(json.dumps(e) + '\n' for e in events[2:]))
    pilot_json(effort='xhigh', version='2.1.327', advisor=True)
    assert grade.main(['gateA1']) == 0
    assert check_line(sheet('r001'), 'V6').startswith('V6: void: the stream does not parse')


def test_v6_passes_a_stream_whose_only_odd_line_is_blank(kit):
    plan(('r001', 'audit', 'changed'), batch='gateA1')
    res = rep_files('r001', 'audit', 'changed', AUDIT_REPORT)
    path = res / 'stream.jsonl'
    path.write_text(path.read_text() + '\n  \n')
    pilot_json(effort='xhigh', version='2.1.327', advisor=True)
    assert grade.main(['gateA1']) == 0
    assert check_line(sheet('r001'), 'V6') == 'V6: ok'


def test_a_valid_verdict_on_a_graded_v9_void_sheet_is_refused(kit, capfd):
    assert check_line(v9_sheet(events=[user_with(FOREIGN)]), 'void') == 'void: V9'
    capfd.readouterr()
    hand_verdicts(*(f'r001 {v}' for v in VALID_AUDIT))
    for argv in (['stop', 'gateA1'], ['unblind', 'A']):
        assert grade.main(argv) == 1
        assert capfd.readouterr() == ('', 'grade.py: refused: these reps are not ready: r001 (a valid verdict, but '
                                          'its sheet has a void or pending check)\n')


# --- sheets ---------------------------------------------------------------------------------------------------


def test_an_audit_sheet_holds_the_counts_cost_duration_and_settle_lines(kit):
    text = one_rep()
    assert text.splitlines()[0] == '== r001 audit counted'
    assert check_line(text, 'B rows') == 'B rows: 3 kept, 1 unparseable'
    assert check_line(text, 'cost') == 'cost: $3.25'
    assert check_line(text, 'duration') == 'duration: 321 s'
    assert check_line(text, 'report') == 'report: reports/r001.md'
    assert (common.k_dir() / 'reports' / 'r001.md').read_text() == AUDIT_REPORT
    lines = section(text, 'settle:')
    assert lines[0] == 'cc-guide settle: audit models, <packet copy>'
    assert lines[1] == "report: 1 confirmed, 1 correction(s), 2 owner's call, 3 unverified"
    assert not [line for line in lines if line.startswith('then, in this order') or 'baseline' in line]
    assert str(common.k_dir()) not in text and str(common.R) not in text
    kept = section(text, 'kept corrections and C rows (P1 to P14 candidates):')
    assert [line.split('] ')[0] for line in kept] == ['[A L5 models.routing PARTIAL kept', '[C kept', '[C kept']
    b_rows = section(text, 'B rows on changelog.md:1288, :1702 or :224:')
    assert len(b_rows) == 2
    denied = section(text, 'rows naming deniedModels:')
    assert [line.split('] ')[0] for line in denied] == ['[A L5 models.routing PARTIAL kept', '[C kept']
    measures = json.loads((common.k_dir() / 'sheets' / 'r001.json').read_text())
    assert measures == {'rid': 'r001', 'packet': 'audit', 'role': 'counted', 'void': [], 'pending': ['V7', 'V8'],
                        'cost': 3.25, 'seconds': 321.4, 'volume': 1, 'b_rows': 3, 'b_unparseable': 1,
                        'listed': 'listed items: 2 answered by a B row, 1 answered none, 1 unanswered'}


def test_an_audit_rep_settles_against_the_listed_copy_and_the_fixtures_docs(kit):
    shutil_rmtree(common.k_dir() / 'fixtures' / 'audit-control')  # neither arm reads it
    text = one_rep(arm='control')
    assert check_line(text, 'listed items') == 'listed items: 2 answered by a B row, 1 answered none, 1 unanswered'
    index = json.loads((common.k_dir() / 'settle' / 'r001' / 'packet' / 'index.json').read_text())
    docs = str(common.k_dir() / 'fixtures' / 'docs')
    assert (index['docs'], index['quotes']['docs']) == (docs, [docs])
    assert (common.k_dir() / 'settle' / 'r001' / 'packet' / 'report.md').read_text() == AUDIT_REPORT


def shutil_rmtree(path: Path) -> None:
    import shutil
    shutil.rmtree(path)


def test_a_void_rep_still_gets_a_sheet(kit):
    text = one_rep(report=None, status={'exit': None, 'timed_out': True})
    assert check_line(text, 'V6') == 'V6: void: timed out; no report: neither a finished Agent result nor a handback'
    assert check_line(text, 'void') == 'void: V6'
    assert check_line(text, 'report') == 'report: none'
    assert section(text, 'settle:') == ['no report, so nothing to settle']
    assert 'B rows on changelog.md:1288, :1702 or :224:' not in text


def test_a_sheet_takes_the_handback_when_the_agent_result_is_the_completion_notice(kit):
    text = one_rep(events=stream('r001', 'audit', agent_text=COMPLETION))
    assert (common.k_dir() / 'reports' / 'r001.md').read_text(encoding='utf-8') == AUDIT_REPORT
    assert check_line(text, 'report') == 'report: reports/r001.md'
    assert check_line(text, 'V6') == 'V6: ok'
    assert 'no report' not in text
    assert check_line(text, 'listed items') == 'listed items: 2 answered by a B row, 1 answered none, 1 unanswered'
    assert no_arm_named(text)


def test_a_sheet_has_no_report_when_the_completion_notice_has_no_handback(kit):
    text = one_rep(report=None, events=stream('r001', 'audit', agent_text=COMPLETION))
    assert check_line(text, 'V6') == 'V6: void: no report: neither a finished Agent result nor a handback'
    assert check_line(text, 'report') == 'report: none'
    assert not (common.k_dir() / 'reports' / 'r001.md').exists()
    assert no_arm_named(text)


def test_a_sheet_logs_refused_calls_and_main_session_hits(kit):
    extra = (vassistant(use('t5', 'Read', file_path='/Users/someone/x.md'),
                        use('t6', 'Read', file_path='/opt/y.md')),
             tool_result('t5', 'denied', error=True), tool_result('t6', 'text'),
             att('nested_memory', content='availableModels'))
    text = one_rep(packet='readme', report=README_REPORT,
                   transcripts=[verifier('r001', 'changed', README_REPORT, extra=extra)],
                   main=[att('claude_md', content='uses availableModels')])
    assert check_line(text, 'V2') == 'V2: void: Read /opt/y.md'
    assert check_line(text, 'V2 refused (logged, not void)') == 'V2 refused (logged, not void): Read /Users/someone/x.md'
    assert check_line(text, 'V3') == 'V3: hits: attachment nested_memory: availableModels (trace each by hand)'
    assert check_line(text, 'V3 main session (recorded only)') == (
        'V3 main session (recorded only): attachment claude_md: availableModels')
    assert check_line(text, 'void') == 'void: V2'


def test_a_precision_sheet_without_a_key_says_so_and_a_readme_sheet_has_no_key_note(kit):
    (common.k_dir() / 'precision-key.tsv').unlink()
    text = one_rep(packet='precision', report=PRECISION_REPORT)
    assert section(text, 'kept contradicts rows:')[0].startswith(
        '[F skills/x/SKILL.md:12-14 skills.description, contradicts, key missing] ')
    readme = one_rep(rid='r002', packet='readme', report=README_REPORT)
    assert 'on key' not in readme and 'key missing' not in readme


@pytest.mark.parametrize('key, note', [
    ('skills/x/SKILL.md:12\ts\t9\tw\n', 'on key'),
    ('skills/x/SKILL.md:14\ts\t9\tw\n', 'on key'),
    ('skills/x/SKILL.md:10-12\ts\t9\tw\n', 'on key'),
    ('skills/x/SKILL.md:14-20\ts\t9\tw\n', 'on key'),
    ('skills/x/SKILL.md:11\ts\t9\tw\n', 'not on key'),
    ('skills/x/SKILL.md:15-16\ts\t9\tw\n', 'not on key'),
    ('skills/x/references/a.md:13\ts\t9\tw\n', 'not on key'),
    ('# skills/x/SKILL.md:13\ts\t9\tw\n\n', 'not on key'),
])
def test_the_key_overlap_takes_lines_and_ranges(kit, key, note):
    write(common.k_dir() / 'precision-key.tsv', key)
    text = one_rep(packet='precision', report=PRECISION_REPORT)
    assert section(text, 'kept contradicts rows:')[0].split('] ')[0].endswith(f', {note}')


def test_a_rep_without_results_gets_no_sheet_and_an_unknown_batch_is_refused(kit, capsys):
    plan(('r001', 'readme', 'control'), ('r002', 'readme', 'changed'))
    rep_files('r002', 'readme', 'changed', README_REPORT)
    assert grade.main(['b']) == 0
    out, _ = capsys.readouterr()
    assert 'r001: no results yet' in out and 'r002: sheets/r002.txt' in out
    assert not (common.k_dir() / 'sheets' / 'r001.txt').exists()
    assert grade.main(['nosuch']) == 2
    assert grade.main([]) == 2 and grade.main(['unblind', 'B']) == 2


@pytest.mark.parametrize('arm', ['control', 'changed'])
def test_a_missing_arm_file_refuses_the_whole_batch(kit, capfd, arm):
    plan(('r001', 'readme', 'control'), ('r002', 'readme', 'changed'))
    rep_files('r001', 'readme', 'control', README_REPORT)
    rep_files('r002', 'readme', 'changed', README_REPORT)
    (common.k_dir() / 'arms' / f'{arm}.md').unlink()
    assert grade.main(['b']) == 1
    assert capfd.readouterr() == ('', ARM_REFUSAL)  # no rep id, no arm, and no rep line on stdout
    assert_nothing_graded()


def test_the_probe_gets_a_short_sheet(kit):
    write(common.k_dir() / 'canary.txt', 'tok123\n')
    plan(('r001', 'probe', 'control', 'probe'), batch='probe')
    calls = [use('toolu_b', 'Bash', command='for d in ~/a; do ls $d; done'),
             use('toolu_r', 'Read', file_path='/home/x/canary.txt'), agent_call('r001', 'readme')]
    events = stream('r001', 'readme', calls)
    events[2:5] = [tool_result('toolu_b', 'denied', error=True), tool_result('toolu_r', 'denied', error=True),
                   tool_result('toolu_main1', 'probe agent: Read, Grep, Glob')]
    probe_agent = [vassistant(use('p1', 'Read', file_path='/home/x/canary.txt')), tool_result('p1', 'no', error=True),
                   vassistant(use('p2', 'Read', file_path=f'{common.R}/r001/work/docs/a.md')), tool_result('p2', 'ok')]
    rep_files('r001', 'probe', 'control', None, events=events, transcripts=[probe_agent])
    assert grade.main(['probe']) == 0
    text = sheet('r001')
    assert text.splitlines()[0] == '== r001 probe'
    assert 'main Bash for d in ~/a; do ls $d; done: refused' in text
    assert 'main Read /home/x/canary.txt: refused' in text
    assert 'cc-guide-verifier Read /home/x/canary.txt: refused' in text
    assert 'canary token seen in: none' in text
    write(common.k_dir() / 'results' / 'r001' / 'stderr.txt', 'tok123\n')
    assert grade.main(['probe']) == 0
    assert 'canary token seen in: stderr.txt' in sheet('r001')
    write(common.k_dir() / 'results' / 'r001' / 'project' / 'x' / 'agent-a9.jsonl', '{"t": "tok123"}\n')
    assert grade.main(['probe']) == 0
    assert 'canary token seen in: project/x/agent-a9.jsonl, stderr.txt' in sheet('r001')


# --- stop -----------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('c11', [0, 1, 2])
@pytest.mark.parametrize('x11', [0, 1, 2])
@pytest.mark.parametrize('x8', [0, 1, 2])
def test_stop_truth_table(kit, capsys, c11, x11, x8):
    reps = [('r001', 'control', True, 'yes' if c11 >= 1 else 'no', 'yes'),
            ('r002', 'control', True, 'yes' if c11 >= 2 else 'no', 'no'),
            ('r003', 'changed', True, 'no' if x11 >= 1 else 'yes', 'no' if x8 >= 1 else 'yes'),
            ('r004', 'changed', True, 'no' if x11 >= 2 else 'yes', 'no' if x8 >= 2 else 'yes')]
    verdict_reps(reps)
    want = 'stop: UNSETTLED' if c11 >= 2 else 'stop: FAIL' if x11 >= 2 or x8 >= 2 else 'continue'
    assert run_stop(capsys) == want + '\n'


@pytest.mark.parametrize('reps, want', [
    ([('r001', 'control', True, 'yes', 'yes'), ('r002', 'control', False, '', ''),
      ('r003', 'changed', True, 'yes', 'yes'), ('r004', 'changed', True, 'yes', 'yes'),
      ('r005', 'control', True, 'yes', 'no', 'none', 0, 'spare')], 'stop: UNSETTLED'),
    ([('r001', 'control', True, 'no', 'yes'), ('r002', 'control', True, 'no', 'yes'),
      ('r003', 'changed', True, 'no', 'no'), ('r004', 'changed', False, '', ''),
      ('r005', 'changed', True, 'no', 'yes', 'none', 0, 'spare')], 'stop: FAIL'),
    ([('r001', 'control', True, 'yes', 'yes'), ('r002', 'control', True, 'yes', 'yes'),
      ('r003', 'changed', True, 'no', 'no'), ('r004', 'changed', True, 'no', 'no')], 'stop: UNSETTLED'),
])
def test_stop_counts_valid_reps_only(kit, capsys, reps, want):
    verdict_reps(reps)
    assert run_stop(capsys) == want + '\n'


def test_stop_refuses_until_every_sheet_has_its_verdicts(kit, capfd):
    verdict_reps([('r001', 'control', True, 'yes', 'yes'), ('r002', 'changed', True, 'yes', 'yes'),
                  ('r003', 'control', True, 'no', 'yes')])
    (common.k_dir() / 'sheets' / 'r002.txt').unlink()
    assert grade.main(['stop', 'gateA1']) == 1
    out, err = capfd.readouterr()
    assert out == '' and 'r002' in err and 'r001' not in err
    stub_sheet('r002', 'audit')
    plan(('r004', 'audit', 'changed'), batch='gateA1')  # held at the ceiling: no sheet and no verdict yet
    assert grade.main(['stop', 'gateA1']) == 1
    assert 'r004' in capfd.readouterr().err
    with (common.k_dir() / 'RESULTS.md').open('a') as f:
        f.write('r004 void\n')  # a rep that never ran is void, and needs no sheet
    assert grade.main(['stop', 'gateA1']) == 1  # but it needs a valid spare
    assert capfd.readouterr().err == 'grade.py: refused: gateA1: these void reps have no valid spare yet: r004\n'
    verdict_reps([('r005', 'changed', True, 'yes', 'yes', 'none', 0, 'spare', 'r004')])
    assert grade.main(['stop', 'gateA1']) == 0
    assert capfd.readouterr().out == 'continue\n'


def test_stop_refuses_a_files_batch_and_an_unknown_batch(kit, capfd):
    files_reps([(rid, 'readme', arm, True, ['readme89 no', 'unsupported 0'])
                for rid, arm in (('r001', 'control'), ('r002', 'changed'), ('r003', 'control'), ('r004', 'changed'))])
    assert grade.main(['stop', 'gateF']) == 1
    assert grade.main(['stop', 'nosuch']) == 1
    out, err = capfd.readouterr()
    assert out == '' and err == ('grade.py: refused: gateF: stop reads a gate A batch, of counted and spare audit '
                                 'reps only\ngrade.py: refused: no batch nosuch; run build.py first\n')


@pytest.mark.parametrize('line, why', [
    ('r001 P11 maybe', 'line 3'),
    ('r001 hits P11', 'line 3'),
    ('r001 hits P1 P99', 'line 3'),
    ('r001 unsupported many', 'line 3'),
    ('r001: valid', 'line 3'),
    ('r001 hits P1 P1', 'line 3'),
    ('r001 P11 yes', 'twice'),
])
def test_a_malformed_or_repeated_verdict_is_refused(kit, capfd, line, why):
    write(common.k_dir() / 'RESULTS.md', f'# Verdicts\n\n{line}\n')
    verdict_reps([('r001', 'control', True, 'yes', 'yes')])
    assert grade.main(['stop', 'gateA1']) == 1
    out, err = capfd.readouterr()
    assert out == '' and why in err and no_arm_named(err)


def test_verdict_lines_may_carry_a_list_marker_and_prose_is_skipped(kit, capsys):
    plan(('r001', 'audit', 'control'), ('r002', 'audit', 'changed'), ('r003', 'audit', 'control'),
         ('r004', 'audit', 'changed'), ('r005', 'audit', 'changed', 'spare', 'r002'), batch='gateA1')
    for rid in ('r001', 'r002', 'r003', 'r004', 'r005'):
        stub_sheet(rid, 'audit')
    plain = [f'{rid} {v}' for rid in ('r003', 'r004', 'r005')
             for v in ('valid', 'P11 no' if rid == 'r003' else 'P11 yes', 'P8 yes', 'hits none', 'unsupported 0')]
    write(common.k_dir() / 'RESULTS.md', '\n'.join([
        '# Hand verdicts', 'Some prose about rep reading.', '- r001 valid', '- r001 P11 yes', '* r001 P8 no',
        'r001 hits P1 P14', 'r001 unsupported 2', 'r002 void', *plain, '']))
    assert run_stop(capsys) == 'continue\n'


# --- unblind --------------------------------------------------------------------------------------------------


def gate_a(control: list[tuple], changed: list[tuple]) -> None:
    '''Gate A reps: each tuple (P11, P8, hits, unsupported), or None for a void rep.'''
    reps, n = [], 0
    for arm, rows in (('control', control), ('changed', changed)):
        for row in rows:
            n += 1
            rid = f'r{n:03d}'
            reps.append((rid, arm, False, '', '') if row is None else (rid, arm, True, *row))
    verdict_reps(reps)


def table(lines: list[str], clause: str, arm: str) -> str:
    return next(line for line in lines if line.startswith(f'{clause} | {arm} |'))


PASS_CONTROL = [('yes', 'yes', 'P1 P2 P9', 1), ('no', 'yes', 'P1 P2', 0), ('no', 'no', 'P1 P13 P7', 0),
                ('no', 'yes', 'P14', 2), ('no', 'yes', 'none', 0)]
PASS_CHANGED = [('yes', 'yes', 'P1 P2 P9', 1), ('yes', 'yes', 'P1', 2), ('yes', 'yes', 'P13 P10', 1),
                ('yes', 'no', 'P14 P2', 2), ('no', 'yes', 'none', 0)]


def test_unblind_a_passes_and_prints_each_clause_per_arm(kit, capsys):
    gate_a(PASS_CONTROL, PASS_CHANGED)
    lines = run_unblind(capsys, 'A')
    assert 'r001 control valid' in lines and 'r006 changed valid' in lines
    assert table(lines, 'P11', 'changed') == 'P11 | changed | at least 4 of 5 valid reps | 4 of 5 | met'
    assert table(lines, 'P8', 'changed') == 'P8 | changed | at least 4 of 5 valid reps | 4 of 5 | met'
    assert table(lines, 'P11', 'control') == 'P11 | control | at most 1 of 5 valid reps | 1 of 5 | met'
    assert table(lines, 'DF7 total', 'changed') == 'DF7 total | changed | at most the control\'s 3 + 3 | 6 | met'
    assert table(lines, 'DF7 per rep', 'changed') == 'DF7 per rep | changed | no rep above 2 | at most 2 | met'
    assert table(lines, 'DF8 P1', 'changed') == 'DF8 P1 | changed | at least the control\'s 3 - 1 | 2 | met'
    assert table(lines, 'P7', 'control') == 'P7 | control | reported | 1 of 5 | -'
    assert table(lines, 'P10', 'changed') == 'P10 | changed | reported | 1 of 5 | -'
    assert lines[-1] == 'result: PASS'


@pytest.mark.parametrize('change, clause', [
    (lambda c, x: x.__setitem__(1, ('no', 'yes', 'P1', 2)), 'P11 | changed'),
    (lambda c, x: x.__setitem__(1, ('yes', 'no', 'P1', 2)), 'P8 | changed'),
    (lambda c, x: c.__setitem__(1, ('yes', 'yes', 'P1 P2', 0)), 'P11 | control'),
    (lambda c, x: x.__setitem__(4, ('no', 'yes', 'none', 1)), 'DF7 total | changed'),
    (lambda c, x: x.__setitem__(slice(1, 5), [('yes', 'yes', 'P1', 0), ('yes', 'yes', 'P13 P10', 0),
                                              ('yes', 'no', 'P14 P2', 2), ('no', 'yes', 'none', 3)]),
     'DF7 per rep | changed'),
    (lambda c, x: x.__setitem__(1, ('yes', 'yes', 'none', 2)), 'DF8 P1 | changed'),
])
def test_unblind_a_fails_on_each_clause(kit, capsys, change, clause):
    control, changed = list(PASS_CONTROL), list(PASS_CHANGED)
    change(control, changed)
    gate_a(control, changed)
    lines = run_unblind(capsys, 'A')
    assert next(line for line in lines if line.startswith(clause + ' |')).endswith('| not met')
    assert [line for line in lines if line.endswith('| not met')] == [
        next(line for line in lines if line.startswith(clause + ' |'))]
    assert lines[-1] == 'result: FAIL'


@pytest.mark.parametrize('control, changed, want', [
    ([('yes', 'yes', 'none', 0), ('yes', 'yes', 'none', 0)], [('no', 'no', 'none', 0), ('no', 'no', 'none', 0)],
     'result: UNSETTLED (first wave: the control meets P11 in 2 valid reps)'),
    ([('no', 'yes', 'none', 0), ('yes', 'yes', 'none', 0)], [('no', 'yes', 'none', 0), ('no', 'yes', 'none', 0)],
     'result: FAIL (first wave: the changed arm misses P11 or P8 in 2 valid reps)'),
    ([('no', 'yes', 'none', 0), ('no', 'yes', 'none', 0)], [('yes', 'no', 'none', 0), ('yes', 'no', 'none', 0)],
     'result: FAIL (first wave: the changed arm misses P11 or P8 in 2 valid reps)'),
    ([('no', 'yes', 'none', 0), ('no', 'yes', 'none', 0)], [('yes', 'yes', 'none', 0), ('yes', 'yes', 'none', 0)],
     'result: UNSETTLED (too few valid reps: control 2 of 5, changed 2 of 5)'),
    (PASS_CONTROL[:4] + [None], PASS_CHANGED, 'result: UNSETTLED (too few valid reps: control 4 of 5)'),
])
def test_unblind_a_short_of_valid_reps_applies_the_first_wave_rules(kit, capsys, control, changed, want):
    gate_a(control, changed)
    assert run_unblind(capsys, 'A')[-1] == want


def test_unblind_a_reports_the_measures_per_rep_and_arm(kit, capsys):
    gate_a(PASS_CONTROL, PASS_CHANGED)
    stub_sheet('r001', 'audit', volume=2, b_rows=7, listed='listed items: 0 answered by a B row, 0 answered none, '
                                                           '4 unanswered')
    lines = run_unblind(capsys, 'A')
    assert 'r001 control: B rows 7 kept, 0 unparseable; listed items: 0 answered by a B row, 0 answered none, ' \
           '4 unanswered; corrections 2' in lines
    assert 'corrections (DF21) | control | median 4, total 18' in lines
    assert 'corrections (DF21) | changed | median 4, total 20' in lines


F_PASS = [('r001', 'readme', 'control', True, ['readme89 yes', 'unsupported 3']),
          ('r002', 'readme', 'control', True, ['readme89 no', 'unsupported 0']),
          ('r003', 'readme', 'control', True, ['readme89 yes', 'unsupported 1']),
          ('r004', 'readme', 'changed', True, ['readme89 no', 'unsupported 2']),
          ('r005', 'readme', 'changed', True, ['readme89 no', 'unsupported 0']),
          ('r006', 'readme', 'changed', True, ['readme89 no', 'unsupported 1']),
          ('r007', 'precision', 'control', True, ['reach no', 'keymiss 0', 'unsupported 4']),
          ('r008', 'precision', 'control', True, ['reach yes', 'keymiss 1', 'unsupported 1']),
          ('r009', 'precision', 'control', True, ['reach no', 'keymiss 0', 'unsupported 0']),
          ('r010', 'precision', 'changed', True, ['reach yes', 'keymiss 0', 'unsupported 2']),
          ('r011', 'precision', 'changed', True, ['reach yes', 'keymiss 2', 'unsupported 1']),
          ('r012', 'precision', 'changed', True, ['reach no', 'keymiss 0', 'unsupported 0'])]


def test_unblind_f_passes_and_reports_precision_for_both_arms(kit, capsys):
    files_reps(F_PASS)
    lines = run_unblind(capsys, 'F')
    assert table(lines, 'readme89', 'changed') == (
        'readme89 | changed | no valid readme rep keeps a contradicts row on hooks/README.md:89 | 0 of 3 | met')
    assert table(lines, 'readme unsupported', 'changed') == ('readme unsupported | changed | no rep above 2 | '
                                                              'total 3, at most 2 | met')
    assert table(lines, 'readme unsupported', 'control') == ('readme unsupported | control | reported | '
                                                              'total 4, at most 3 | -')
    assert table(lines, 'precision unsupported', 'changed') == ('precision unsupported | changed | no rep above 2 | '
                                                                 'total 3, at most 2 | met')
    assert table(lines, 'reach', 'control') == 'reach | control | reported | 1 of 3 | -'
    assert table(lines, 'reach', 'changed') == 'reach | changed | at least 2 of 3 valid precision reps | 2 of 3 | met'
    assert table(lines, 'precision unsupported', 'control') == ('precision unsupported | control | reported | '
                                                                 'total 5, at most 4 | -')
    assert table(lines, 'keymiss', 'control') == 'keymiss | control | reported | total 1 | -'
    assert table(lines, 'keymiss', 'changed') == 'keymiss | changed | reported | total 2 | -'
    assert table(lines, 'readme89', 'control') == 'readme89 | control | reported | 2 of 3 | -'
    assert 'r007 precision control valid' in lines
    assert lines[-1] == 'result: PASS'


@pytest.mark.parametrize('rid, verdicts, clause', [
    ('r004', ['readme89 yes', 'unsupported 2'], 'readme89 | changed'),
    ('r005', ['readme89 no', 'unsupported 3'], 'readme unsupported | changed'),
    ('r011', ['reach yes', 'keymiss 2', 'unsupported 3'], 'precision unsupported | changed'),
    ('r011', ['reach no', 'keymiss 2', 'unsupported 1'], 'reach | changed'),
])
def test_unblind_f_fails_on_each_clause(kit, capsys, rid, verdicts, clause):
    files_reps([(r, p, a, v, verdicts if r == rid else vs) for r, p, a, v, vs in F_PASS])
    lines = run_unblind(capsys, 'F')
    assert [line for line in lines if line.endswith('| not met')] == [
        next(line for line in lines if line.startswith(clause + ' |'))]
    assert lines[-1] == 'result: FAIL'


def test_unblind_f_short_of_valid_reps_is_unsettled(kit, capsys):
    files_reps([(r, p, a, r != 'r012', vs) for r, p, a, v, vs in F_PASS])
    assert run_unblind(capsys, 'F')[-1] == 'result: UNSETTLED (too few valid reps: precision changed 2 of 3)'


def test_unblind_refuses_without_a_sheet_or_reps_and_names_rep_ids_only(kit, capfd):
    assert grade.main(['unblind', 'F']) == 1
    files_reps(F_PASS)
    (common.k_dir() / 'sheets' / 'r010.txt').unlink()
    assert grade.main(['unblind', 'F']) == 1
    out, err = capfd.readouterr()
    assert out == '' and 'r010' in err and no_arm_named(err)


def test_unblind_takes_counted_and_spare_reps_of_the_gates_packets_only(kit, capsys):
    gate_a(PASS_CONTROL, PASS_CHANGED)
    plan(('r020', 'audit', 'changed', 'pilot'), batch='pilot')  # no sheet, no verdict: not a gate rep
    files_reps([('r021', 'readme', 'control', True, ['readme89 no', 'unsupported 0'])])
    lines = run_unblind(capsys, 'A')
    assert lines[-1] == 'result: PASS' and not [line for line in lines if 'r020' in line or 'r021' in line]


# --- blind reading across every command -----------------------------------------------------------------------


def test_no_output_names_an_arm_in_any_path(kit, capfd):
    plan(('r001', 'audit', 'control'), ('r002', 'audit', 'changed'), ('r003', 'readme', 'changed'),
         ('r004', 'precision', 'control'), batch='gateA1')
    for rid, packet, arm, report in (('r001', 'audit', 'control', AUDIT_REPORT), ('r002', 'audit', 'changed', None),
                                     ('r003', 'readme', 'changed', README_REPORT),
                                     ('r004', 'precision', 'control', PRECISION_REPORT)):
        rep_files(rid, packet, arm, report)
    pilot_json(effort='xhigh', version='2.1.327', advisor=True)  # so r001's sheet has no pending check
    assert grade.main(['gateA1']) == 0
    assert grade.main(['stop', 'gateA1']) == 1  # no verdicts yet
    write(common.k_dir() / 'RESULTS.md', 'r001 valid\nr001 P11 yes\nr001 P8 yes\nr001 hits none\n'
                                         'r001 unsupported 0\nr002 void\n')
    assert grade.main(['unblind', 'A']) == 0
    capfd.readouterr()  # unblind's success path names arms by design; read and drop it
    assert grade.main(['unblind', 'F']) == 1
    write(common.k_dir() / 'RESULTS.md', 'r001 P11 perhaps\n')
    assert grade.main(['stop', 'gateA1']) == 1
    (common.k_dir() / 'fixtures' / 'audit-changed').rename(common.k_dir() / 'moved-away')
    assert grade.main(['gateA1']) == 1  # the audit reps fail by id; the files reps are graded
    (common.k_dir() / 'arms' / 'changed.md').unlink()
    assert grade.main(['gateA1']) == 1  # a missing arm file refuses the whole batch
    assert grade.main(['nosuch']) == 2
    assert grade.main(['stop']) == 2
    out, err = capfd.readouterr()
    assert out.strip() and err.strip()
    assert no_arm_named(out + err), out + err
    assert 'Traceback' not in err and 'fixtures/' not in err


DRIVER = '''import os, sys
from pathlib import Path
base, kit, root, kitfiles = sys.argv[1:5]
if not os.environ['HOME'].startswith(base) or not root.startswith(base):
    sys.exit(97)
sys.path.insert(0, kit)
import common, grade
common.R = Path(root)
common.KIT = Path(kitfiles)
sys.exit(grade.main(sys.argv[5:]))
'''


def test_the_entry_point_prints_no_traceback_and_no_arm_path(kit, tmp_path, sandbox):
    plan(('r001', 'audit', 'control'))
    rep_files('r001', 'audit', 'control', AUDIT_REPORT)
    write(common.k_dir() / 'plan.json', '{"reps": [{"rid": "r001", "batch": "b", "packet": "audit", '
                                        '"arm": "control"}]}')  # no role: a KeyError deep in the grader
    driver = write(tmp_path / 'driver.py', DRIVER)
    for args in (['b'], ['stop', 'b'], ['unblind', 'A']):
        assert_sandboxed(sandbox)
        proc = subprocess.run([sys.executable, str(driver), str(sandbox), str(Path(grade.__file__).parent),
                               str(common.R), str(common.KIT), *args], env=dict(os.environ), capture_output=True,
                              text=True)
        assert proc.returncode in (1, 2), (args, proc.stdout, proc.stderr)
        assert 'Traceback' not in proc.stderr and no_arm_named(proc.stdout + proc.stderr), proc.stderr
        if args[0] != 'b':
            assert proc.stderr == 'grade.py: failed (KeyError)\n'

