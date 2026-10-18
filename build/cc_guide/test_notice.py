'''Tests for notice.py: the notice's line for each outcome (drift spec R9.4,
R12.2's R9 bullet) and the files check --hook leaves for notice.sh.'''
import hashlib
import json
import re
from datetime import date, datetime, timedelta, timezone

import notice

NOW = datetime(2026, 10, 17, 9, 0, tzinfo=timezone.utc)
EPOCH = int(NOW.timestamp())
TODAY = date(2026, 10, 17)


def report(findings=(), lint=0, changelog=None, probes=(), audit=None):
    '''A report holding what due_message reads: `due`, and one block finding
    per tuple of candidate sections.'''
    due = {'lint': lint, 'blocks': len(findings), 'changelog': changelog, 'probes': list(probes),
           'audit': audit or {'group': 'alpha', 'due': False}}
    return {'due': due, 'findings': {'alpha': [{'kind': 'changed', 'candidates': list(c)} for c in findings]},
            'errors': []}


def test_the_spec_example_line():
    '''R9.4's own example, item for item.'''
    got = notice.due_message(report(
        findings=[('hooks.events',), ('rules.settings',)],
        changelog={'releases': 9, 'oldest': '2.1.300', 'oldest_date': '2026-10-09', 'due': True},
        probes=[{'probe': 'p1'}, {'probe': 'p2'}],
        audit={'group': 'hooks', 'due': True}), TODAY)
    assert got == ('cc-guide · 2 docs blocks changed (hooks.events, rules.settings) · '
                   '9 releases untriaged (oldest 8 d) · probes due 2 · audit due: hooks → /cc-guide')


def test_only_due_items_are_named_and_lint_comes_first():
    got = notice.due_message(report(
        lint=1, changelog={'releases': 3, 'oldest': '2.1.300', 'oldest_date': '2026-10-15', 'due': False}), TODAY)
    assert got == 'cc-guide · 1 lint violation → /cc-guide'


def test_nothing_due_is_no_message():
    assert notice.due_message(report(), TODAY) is None


def test_sections_are_named_most_often_first_then_by_id():
    got = notice.due_message(report(findings=[('b.two', 'a.one'), ('b.two',), ('c.three',)]), TODAY)
    assert got == 'cc-guide · 3 docs blocks changed (b.two, a.one, c.three) → /cc-guide'


def test_a_report_at_todays_scale_stays_under_the_limit_and_counts_what_it_left_out():
    '''About 170 findings over 38 sections, as check reported on 2026-10-17.'''
    sections = [f'group{g}.section-{s:02d}' for g in range(6) for s in range(7)][:38]
    findings = [tuple(sections[(i + k) % 38] for k in range(3)) for i in range(172)]
    got = notice.due_message(report(
        findings=findings, lint=2,
        changelog={'releases': 4, 'oldest': '2.1.299', 'oldest_date': '2026-10-14', 'due': True},
        audit={'group': 'overview', 'due': True}), date(2026, 10, 21))
    assert len(got) < notice.LIMIT
    assert got.startswith('cc-guide · 2 lint violations · 172 docs blocks changed (')
    assert got.endswith(' more) · 4 releases untriaged (oldest 7 d) · audit due: overview → /cc-guide')
    named = re.search(r'changed \((.*), \+(\d+) more\)', got)
    assert len(named.group(1).split(', ')) + int(named.group(2)) == 38


def test_a_name_that_fills_the_line_is_named_and_one_a_character_longer_is_counted():
    '''The last character of room: a section name that brings the line to
    LIMIT - 1 characters is named in full, and one a character longer goes
    into "+N more".'''
    empty = 'cc-guide · 2 docs blocks changed (a.one, ) → /cc-guide'
    fills = 'b.' + 'x' * (notice.LIMIT - 1 - len(empty) - len('b.'))
    exact = notice.due_message(report(findings=[('a.one',), (fills,)]), TODAY)
    assert exact == f'cc-guide · 2 docs blocks changed (a.one, {fills}) → /cc-guide'
    assert len(exact) == notice.LIMIT - 1
    over = notice.due_message(report(findings=[('a.one',), (fills + 'x',)]), TODAY)
    assert over == 'cc-guide · 2 docs blocks changed (a.one, +1 more) → /cc-guide'
    assert len(over) <= notice.LIMIT - 1


def test_the_error_line_names_the_reason_and_the_age_of_the_last_good_check():
    assert notice.error_message('https://example.invalid/changelog.md: timed out',
                                EPOCH - 3 * notice.DAY - 5, EPOCH) == (
        'cc-guide · check failed: https://example.invalid/changelog.md: timed out · '
        'last good check 3 d ago → run build/cc_guide/cli.py check')
    assert notice.error_message('boom', None, EPOCH) == (
        'cc-guide · check failed: boom · no good check yet → run build/cc_guide/cli.py check')


def test_a_long_reason_is_cut_to_keep_the_line_under_the_limit():
    assert notice.LIMIT == 300   # R9.4: "under 300 characters"
    got = notice.error_message('x' * 1000 + '\nsecond line', None, EPOCH)
    assert len(got) == notice.LIMIT - 1
    assert '\n' not in got
    assert '… · no good check yet' in got


def test_the_notice_is_one_ascii_json_line_written_before_its_digest(tmp_path, monkeypatch):
    order = []
    real = notice.os.replace

    def replace(src, dst):
        order.append(dst.name)
        real(src, dst)
    monkeypatch.setattr(notice.os, 'replace', replace)
    notice.write_notice(tmp_path, 'cc-guide · x → /cc-guide')
    text = (tmp_path / notice.NOTICE).read_text(encoding='utf-8')
    assert text.isascii() and text.count('\n') == 1
    assert json.loads(text) == {'systemMessage': 'cc-guide · x → /cc-guide'}
    assert (tmp_path / notice.DIGEST).read_text() == hashlib.sha256(text.encode()).hexdigest() + '\n'
    assert order == [notice.NOTICE, notice.DIGEST]
    assert sorted(p.name for p in tmp_path.iterdir()) == [notice.DIGEST, notice.NOTICE]


def test_nothing_due_writes_an_empty_notice(tmp_path):
    notice.write_notice(tmp_path, None)
    assert (tmp_path / notice.NOTICE).read_text() == ''
    assert (tmp_path / notice.DIGEST).read_text() == hashlib.sha256(b'').hexdigest() + '\n'


def test_a_good_check_records_itself_and_a_failed_one_keeps_the_last_good_check(tmp_path):
    first = notice.record_check(tmp_path, 1, NOW, 'r1')
    assert (first['run'], first['exit'], first['ok_epoch']) == ('r1', 1, EPOCH)
    failed = notice.record_check(tmp_path, 2, NOW + timedelta(hours=30), 'r2')
    assert (failed['run'], failed['exit'], failed['ok_at'], failed['ok_epoch']) == ('r2', 2, first['ok_at'], EPOCH)
    assert json.loads((tmp_path / notice.LAST_CHECK).read_text()) == failed
    assert notice.last_ok(tmp_path) == EPOCH


def test_a_first_failure_records_no_good_check(tmp_path):
    record = notice.record_check(tmp_path, 2, NOW, None)
    assert (record['ok_at'], record['ok_epoch'], notice.last_ok(tmp_path)) == (None, None, None)


def test_the_record_keeps_the_two_lines_notice_sh_reads(tmp_path):
    '''notice.sh reads last-check.json with sed and grep, not a JSON parser:
    ok_epoch alone on its line, and the run ID as "run": "<id>".'''
    notice.record_check(tmp_path, 0, NOW, '123.456')
    text = (tmp_path / notice.LAST_CHECK).read_text()
    assert re.search(rf'^ *"ok_epoch": {EPOCH},?$', text, re.M)
    assert '"run": "123.456"' in text


def test_after_check_writes_the_notice_for_each_exit_then_the_record(tmp_path):
    due = report(changelog={'releases': 2, 'oldest': '2.1.901', 'oldest_date': '2026-10-10', 'due': True})
    notice.after_check(tmp_path, 1, due, NOW, TODAY, 'r1')
    assert json.loads((tmp_path / notice.NOTICE).read_text())['systemMessage'] == (
        'cc-guide · 2 releases untriaged (oldest 7 d) → /cc-guide')
    notice.after_check(tmp_path, 0, report(), NOW, TODAY, 'r2')
    assert (tmp_path / notice.NOTICE).read_text() == ''
    failing = dict(report(), errors=['https://example.invalid/llms.txt: HTTP 503'])
    notice.after_check(tmp_path, 2, failing, NOW + timedelta(days=2), date(2026, 10, 19), 'r3')
    assert json.loads((tmp_path / notice.NOTICE).read_text())['systemMessage'] == (
        'cc-guide · check failed: https://example.invalid/llms.txt: HTTP 503 · '
        'last good check 2 d ago → run build/cc_guide/cli.py check')
    assert notice.read_last_check(tmp_path)['run'] == 'r3'


def test_after_failure_writes_the_error_line_and_records_an_exit_two(tmp_path):
    notice.after_failure(tmp_path, 'RuntimeError: boom', NOW, 'r9')
    assert json.loads((tmp_path / notice.NOTICE).read_text())['systemMessage'] == (
        'cc-guide · check failed: RuntimeError: boom · no good check yet'
        ' → run build/cc_guide/cli.py check')
    record = notice.read_last_check(tmp_path)
    assert (record['run'], record['exit']) == ('r9', 2)
