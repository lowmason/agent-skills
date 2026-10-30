'''Tests for deferred_stats.py — the deferred-backlog health reporter.'''
from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

from deferred_stats import (
    Note,
    aging_state,
    carry_used,
    compute_stats,
    format_report,
    main,
    parse_items,
    path_is_live,
)

SCRIPT = Path(__file__).with_name('deferred_stats.py')
TODAY = dt.date(2026, 9, 8)
NINETY_DAYS_AGO = TODAY - dt.timedelta(days=90)
# Later than every note date the carry tests write, so the items there are aged.
LATER = dt.date(2026, 12, 1)

SAMPLE = '''# Deferred items

## 11-delegation-frontmatter-rollout — 2026-07-19
- [x] Shipped item, done in plan 12.
- [ ] Open and old: needs a prod decision.
      Continuation line that is not an item.

## 26-distill-sessions-hardening — 2026-09-04
- [ ] Open and fresh.
- [ ] Also open and fresh.
- [x] Closed here.
'''


def one_section(body: str, date: dt.date = NINETY_DAYS_AGO, name: str = '9-test') -> str:
    '''A backlog with a single dated section holding `body` (its items, as text).'''
    return f'# Deferred items\n\n## {name} — {date.isoformat()}\n{body}\n'


def live(_path: str) -> bool:
    return True


def retired(_path: str) -> bool:
    return False


def test_parse_items_carry_section_and_checkbox():
    items = parse_items(SAMPLE)
    assert [i.section for i in items] == [
        '11-delegation-frontmatter-rollout',
        '11-delegation-frontmatter-rollout',
        '26-distill-sessions-hardening',
        '26-distill-sessions-hardening',
        '26-distill-sessions-hardening',
    ]
    assert items[0].section_date == dt.date(2026, 7, 19)
    assert items[2].section_date == dt.date(2026, 9, 4)
    by_section = Counter((i.section, i.checked) for i in items)
    assert by_section[('11-delegation-frontmatter-rollout', False)] == 1
    assert by_section[('11-delegation-frontmatter-rollout', True)] == 1
    assert by_section[('26-distill-sessions-hardening', False)] == 2
    assert by_section[('26-distill-sessions-hardening', True)] == 1


def test_preamble_and_continuation_lines_are_not_items():
    stats = compute_stats(parse_items(SAMPLE), TODAY)
    assert stats['total'] == 5


def test_undated_section_counts_items_but_not_age():
    text = SAMPLE + '\n## Aged-backlog acknowledgements\n- 2026-09-08 — carried 1 item.\n'
    text += '\n## Hand-written section with no date\n- [ ] Undated open item.\n'
    stats = compute_stats(parse_items(text), TODAY)
    assert stats['undated_open'] == 1
    assert stats['open'] == 4
    # The acknowledgement bullet is not a checkbox, so it never enters the counts.
    assert stats['total'] == 6


def test_closure_rate_and_empty_backlog():
    stats = compute_stats(parse_items(SAMPLE), TODAY)
    assert stats['closed'] == 2
    assert stats['closure_rate'] == 0.4
    empty = compute_stats(parse_items('# Deferred items\n'), TODAY)
    assert empty['total'] == 0
    assert empty['closure_rate'] is None


def test_aged_open_uses_section_date():
    stats = compute_stats(parse_items(SAMPLE), TODAY, aged_days=45)
    assert stats['aged_open'] == 1
    assert stats['aged_days'] == 45
    loose = compute_stats(parse_items(SAMPLE), TODAY, aged_days=90)
    assert loose['aged_open'] == 0


def test_oldest_open_reports_days_and_section():
    stats = compute_stats(parse_items(SAMPLE), TODAY)
    assert stats['oldest_open_days'] == 51
    assert stats['oldest_open_section'] == '11-delegation-frontmatter-rollout'


def test_step_4b_review_section_is_dated():
    # finishing-a-development-branch Step 4b writes `## <name> Step 4b review — <date>`,
    # where <name> may be a branch name rather than a plan.
    text = '# Deferred items\n\n## claude/fix-thing Step 4b review — 2026-07-01\n- [ ] Carried finding.\n'
    items = parse_items(text)
    assert items[0].section == 'claude/fix-thing Step 4b review'
    assert items[0].section_date == dt.date(2026, 7, 1)
    stats = compute_stats(items, TODAY, aged_days=45)
    assert stats['aged_open'] == 1
    assert stats['oldest_open_days'] == 69


def test_age_histogram_buckets_open_items_only():
    stats = compute_stats(parse_items(SAMPLE), TODAY)
    buckets = {b['label']: b['count'] for b in stats['age_histogram']}
    assert buckets['0-14d'] == 2
    assert buckets['46-90d'] == 1
    assert sum(b['count'] for b in stats['age_histogram']) == 3


def test_missing_file_reports_absent(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), '--file', str(tmp_path / 'nope.md'), '--json'],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload['exists'] is False
    assert payload['open'] == 0


def test_json_output_carries_the_full_contract(tmp_path):
    target = tmp_path / 'deferred_items.md'
    target.write_text(SAMPLE, encoding='utf-8')
    result = subprocess.run(
        [sys.executable, str(SCRIPT), '--file', str(target), '--json'],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    for key in (
        'exists', 'open', 'closed', 'total', 'closure_rate', 'aged_days',
        'aged_open', 'undated_open', 'oldest_open_days', 'oldest_open_section',
        'age_histogram',
    ):
        assert key in payload, f'missing contract key: {key}'
    assert payload['exists'] is True


def test_format_report_names_the_two_thresholds():
    stats = compute_stats(parse_items(SAMPLE), TODAY)
    report = format_report(stats)
    assert '3 open' in report
    assert '40%' in report
    assert 'aged >45d: 1' in report


def test_calendar_invalid_date_is_treated_as_undated():
    text = '# Deferred items\n\n## 27-typo — 2026-09-31\n- [ ] Item under an impossible date.\n'
    items = parse_items(text)
    assert items[0].section_date is None
    stats = compute_stats(items, TODAY)
    assert (stats['open'], stats['undated_open'], stats['aged_open']) == (1, 1, 0)
    assert sum(b['count'] for b in stats['age_histogram']) == 0


def test_future_dated_section_is_not_reported_as_oldest():
    text = SAMPLE + '\n## 28-future — 2026-10-01\n- [ ] Typed next month by mistake.\n'
    stats = compute_stats(parse_items(text), TODAY)
    assert stats['undated_open'] == 1
    assert {b['label']: b['count'] for b in stats['age_histogram']}['91d+'] == 0
    assert stats['oldest_open_days'] == 51


def test_invalid_date_does_not_break_the_exit_contract(tmp_path):
    target = tmp_path / 'deferred_items.md'
    target.write_text('# Deferred items\n\n## 27-typo — 2026-02-30\n- [ ] One item.\n', encoding='utf-8')
    result = subprocess.run(
        [sys.executable, str(SCRIPT), '--file', str(target), '--json'],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['undated_open'] == 1


def test_continuation_notes_belong_to_their_item():
    text = one_section(
        '- [ ] First item.\n'
        '      → held 2026-10-01: vendor fix\n'
        '- [ ] Second item.'
    )
    first, second = parse_items(text)
    assert first.notes == [Note('held', dt.date(2026, 10, 1), 'vendor fix')]
    assert second.notes == []


def test_nested_bullet_stays_in_its_item():
    text = one_section(
        '- [ ] First item.\n'
        '  - sub point → held 2026-10-01: x\n'
        '- [ ] Second item.'
    )
    items = parse_items(text)
    assert len(items) == 2
    assert items[0].notes == [Note('held', dt.date(2026, 10, 1), 'x')]
    assert items[1].notes == []


def test_note_form_in_backticks_sets_no_state():
    text = one_section(
        '- [ ] Work item that quotes `→ held <date>: <condition>` and\n'
        '      `→ triggered 2026-01-01: x` as examples.'
    )
    (item,) = parse_items(text)
    assert item.notes == []
    assert aging_state(item, retired) == ('work', NINETY_DAYS_AGO)
    stats = compute_stats([item], TODAY, is_live=retired)
    assert (stats['aged_open'], stats['watching']) == (1, 0)


def test_open_item_with_done_note_stays_open_and_warns():
    text = one_section(
        '- [ ] x → done 2026-10-01 (plan 9)\n'
        '- [x] y → done 2026-10-01 (plan 9)'
    )
    stats = compute_stats(parse_items(text), TODAY)
    assert (stats['open'], stats['closed']) == (1, 1)
    warnings = [line for line in format_report(stats).splitlines() if 'Warning' in line]
    # Only the unticked item warns; a ticked item with a done note is the normal case.
    assert warnings == ['  Warning: open item has a → done note: 9-test: x…']


def test_triggered_item_ages_from_note_date():
    text = one_section(
        '- [ ] Gate on a vendor fix.\n'
        '      Revisit if: the vendor ships.\n'
        '      → triggered 2026-10-01: it broke',
        date=dt.date(2026, 6, 1),
    )
    today = dt.date(2026, 12, 1)
    (item,) = parse_items(text)
    assert aging_state(item, retired) == ('triggered', dt.date(2026, 10, 1))
    stats = compute_stats([item], today)
    assert stats['aged_open'] == 1
    assert stats['oldest_open_days'] == 61
    assert stats['watching'] == 0


def test_held_item_is_not_aged_and_counts_as_watching():
    text = one_section(
        '- [ ] Work item.\n'
        '      Done when: the upstream fix lands.\n'
        '      → held 2026-09-01: upstream'
    )
    stats = compute_stats(parse_items(text), TODAY)
    assert stats['open'] == 1
    assert stats['aged_open'] == 0
    assert stats['watching'] == 1
    assert stats['oldest_open_days'] is None
    assert sum(b['count'] for b in stats['age_histogram']) == 0


def test_latest_state_note_wins():
    held_then_triggered = one_section(
        '- [ ] Item.\n'
        '      → held 2026-09-01: x\n'
        '      → triggered 2026-10-01: y'
    )
    triggered_then_held = one_section(
        '- [ ] Item.\n'
        '      → triggered 2026-09-01: y\n'
        '      → held 2026-10-01: x'
    )
    # "Latest" means the latest date, even when the lines sit out of order.
    out_of_order = one_section(
        '- [ ] Item.\n'
        '      → held 2026-10-01: x\n'
        '      → triggered 2026-09-01: y'
    )
    (a,) = parse_items(held_then_triggered)
    (b,) = parse_items(triggered_then_held)
    (c,) = parse_items(out_of_order)
    assert aging_state(a, retired) == ('triggered', dt.date(2026, 10, 1))
    assert aging_state(b, retired) == ('held', None)
    assert aging_state(c, retired) == ('held', None)


def test_planned_item_with_live_file_is_not_aged_or_watching():
    text = one_section(
        '- [ ] Item.\n'
        '      → planned 2026-10-01: specs/plans/9-x.md'
    )
    asked: list[str] = []

    def is_live(path: str) -> bool:
        asked.append(path)
        return True

    stats = compute_stats(parse_items(text), TODAY, is_live=is_live)
    assert asked == ['specs/plans/9-x.md']
    assert (stats['aged_open'], stats['watching'], stats['planned']) == (0, 0, 1)
    assert stats['open'] == 1


def test_planned_item_whose_file_retired_ages_from_section_date():
    text = one_section(
        '- [ ] Item.\n'
        '      → planned 2026-10-01: specs/plans/9-x.md'
    )
    stats = compute_stats(parse_items(text), TODAY, is_live=retired)
    assert (stats['aged_open'], stats['watching'], stats['planned']) == (1, 0, 0)


def test_watch_item_is_not_aged():
    text = one_section(
        '- [ ] Item.\n'
        '      Revisit if: the vendor ships a fix.'
    )
    stats = compute_stats(parse_items(text), TODAY)
    assert (stats['aged_open'], stats['watching']) == (0, 1)


def test_item_with_both_closure_lines_ages_as_work():
    text = one_section(
        '- [ ] Item.\n'
        '      Done when: the check passes. Revisit if: the vendor ships.'
    )
    stats = compute_stats(parse_items(text), TODAY)
    assert (stats['aged_open'], stats['watching']) == (1, 0)


def test_owner_only_note_does_not_stop_aging():
    text = one_section(
        '- [ ] Item.\n'
        '      Done when: the owner runs it.\n'
        '      → owner-only 2026-09-01: run it'
    )
    stats = compute_stats(parse_items(text), TODAY)
    assert (stats['aged_open'], stats['watching']) == (1, 0)


def test_first_summary_line_shape_unchanged():
    shape = re.compile(
        r'^Deferred backlog: \d+ open, \d+ ever closed '
        r'\(closure rate (\d+%|n/a)\), aged >\d+d: \d+\.$'
    )
    watch = one_section('- [ ] Item.\n      Revisit if: later.\n- [ ] Plain item.')
    for text in (SAMPLE, watch, '# Deferred items\n'):
        stats = compute_stats(parse_items(text), TODAY, is_live=live)
        first = format_report(stats).splitlines()[0]
        assert shape.match(first), first


def test_watching_and_planned_lines():
    text = one_section(
        '- [ ] Watch item.\n'
        '      Revisit if: the vendor ships.\n'
        '- [ ] Held item.\n'
        '      Done when: fixed.\n'
        '      → held 2026-09-01: upstream\n'
        '- [ ] Planned item.\n'
        '      → planned 2026-09-02: specs/plans/9-x.md\n'
        '- [ ] Aged work item.'
    )
    lines = format_report(compute_stats(parse_items(text), TODAY, is_live=live)).splitlines()
    watching = '  Watching: 2 (Revisit-if or held; not aged).'
    planned = '  Planned: 1 (in a live plan or spec; not aged).'
    assert lines.index(watching) == 1
    assert lines.index(planned) == 2
    assert lines[3].startswith('  Oldest open:')
    # Both lines are left out when their counts are zero.
    plain = format_report(compute_stats(parse_items(SAMPLE), TODAY))
    assert 'Watching:' not in plain
    assert 'Planned:' not in plain


def test_default_is_live_needs_an_existing_path_outside_completed(tmp_path):
    plans = tmp_path / 'specs' / 'plans'
    retired_dir = plans / 'completed'
    retired_dir.mkdir(parents=True)
    (plans / '9-x.md').write_text('plan\n', encoding='utf-8')
    (retired_dir / '8-y.md').write_text('plan\n', encoding='utf-8')
    assert path_is_live(str(plans / '9-x.md')) is True
    assert path_is_live(str(retired_dir / '8-y.md')) is False
    assert path_is_live(str(plans / '7-gone.md')) is False


def test_archived_items_count_as_closed_never_open():
    backlog = one_section('- [ ] Fresh open item.', date=TODAY - dt.timedelta(days=10))
    archive = one_section(
        '- [x] First archived item. → done 2026-06-12: shipped\n'
        '- [x] Second archived item. → done 2026-06-12: shipped',
        name='7-old',
    )
    stats = compute_stats(parse_items(backlog), TODAY, archived=parse_items(archive))
    assert (stats['open'], stats['closed'], stats['total']) == (1, 2, 3)
    assert stats['closure_rate'] == round(2 / 3, 4)
    # The archive's section is 90 days old. None of that age reaches the open figures.
    assert stats['aged_open'] == 0
    assert stats['oldest_open_days'] == 10
    assert sum(b['count'] for b in stats['age_histogram']) == 1


def test_unticked_item_in_the_archive_still_counts_as_closed():
    # Spec section 5: archived items never count as open or aged. A hand-moved item
    # that lost its tick is closed all the same, and nothing in it is read for a warning.
    archive = one_section(
        '- [ ] Unticked archived item.\n'
        '      → done 2026-06-12: shipped\n'
        '      → acknowledged 2026-09-01 (b): reason'
    )
    stats = compute_stats([], TODAY, archived=parse_items(archive))
    assert (stats['open'], stats['closed'], stats['aged_open']) == (0, 1, 0)
    assert stats['open_with_done_note'] == []
    assert stats['aged_acknowledged'] == []


def test_removed_items_count_as_closed_and_are_reported():
    backlog = one_section('- [ ] Open item.', date=TODAY - dt.timedelta(days=10))
    archive = one_section('- [x] y → removed 2026-10-27: skill archived', name='7-old')
    stats = compute_stats(parse_items(backlog), TODAY, archived=parse_items(archive))
    assert stats['removed'] == 1
    assert (stats['open'], stats['closed']) == (1, 1)
    assert '  Removed: 1 (counted as closed).' in format_report(stats).splitlines()
    # With no removal the line is left out.
    plain = compute_stats(parse_items(backlog), TODAY)
    assert plain['removed'] == 0
    assert 'Removed:' not in format_report(plain)


def test_removed_note_counts_only_on_a_closed_item():
    # A ticked item not yet moved to the archive is still a removal, so archiving it
    # changes no number. An unticked item stays open: the checkbox decides.
    backlog = one_section(
        '- [x] Ticked, still in the live file. → removed 2026-10-27: gone\n'
        '- [ ] Unticked with a removed note. → removed 2026-10-27: gone'
    )
    stats = compute_stats(parse_items(backlog), TODAY)
    assert (stats['open'], stats['closed'], stats['removed']) == (1, 1, 1)


def test_missing_archive_file_is_fine(tmp_path, capsys):
    backlog = tmp_path / 'deferred_items.md'
    backlog.write_text(SAMPLE, encoding='utf-8')
    assert main(['--file', str(backlog), '--archive', str(tmp_path / 'nope.md')]) == 0
    first = capsys.readouterr().out.splitlines()[0]
    assert first.startswith('Deferred backlog: 3 open, 2 ever closed')


def test_archive_flag_reads_the_archive_file(tmp_path, capsys):
    backlog = tmp_path / 'deferred_items.md'
    backlog.write_text(SAMPLE, encoding='utf-8')
    archive = tmp_path / 'archive.md'
    archive.write_text(one_section('- [x] A.\n- [x] B.', name='7-old'), encoding='utf-8')
    assert main(['--file', str(backlog), '--archive', str(archive), '--json']) == 0
    payload = json.loads(capsys.readouterr().out)
    assert (payload['open'], payload['closed'], payload['total']) == (3, 4, 7)


def test_carry_used_after_latest_state_note():
    text = one_section(
        '- [ ] Alpha work item.\n'
        '      Done when: it ships.\n'
        '      → acknowledged 2026-10-20 (feat/x): reason',
        name='s1',
    )
    (item,) = parse_items(text)
    assert carry_used(item) is True
    stats = compute_stats([item], LATER)
    assert stats['aged_open'] == 1
    assert stats['aged_acknowledged'] == [
        {'section': 's1', 'first_words': 'Alpha work item. Done when: it'}
    ]


def test_acknowledgement_before_triggered_note_is_not_a_used_carry():
    text = one_section(
        '- [ ] Gate item.\n'
        '      → acknowledged 2026-09-01 (b): r\n'
        '      → triggered 2026-10-01: z'
    )
    (item,) = parse_items(text)
    assert carry_used(item) is False
    stats = compute_stats([item], LATER)
    # The item is aged, so only the order of the two notes keeps it off the list.
    assert stats['aged_open'] == 1
    assert stats['aged_acknowledged'] == []


def test_acknowledgement_on_the_state_note_day_is_not_after_it():
    same_day = one_section(
        '- [ ] Item.\n'
        '      → triggered 2026-10-01: z\n'
        '      → acknowledged 2026-10-01 (b): r'
    )
    next_day = one_section(
        '- [ ] Item.\n'
        '      → triggered 2026-10-01: z\n'
        '      → acknowledged 2026-10-02 (b): r'
    )
    assert carry_used(parse_items(same_day)[0]) is False
    assert carry_used(parse_items(next_day)[0]) is True


def test_undated_notes_never_break_the_carry_comparison():
    undated_ack = one_section('- [ ] Item.\n      → acknowledged (b): r')
    undated_state = one_section(
        '- [ ] Item.\n'
        '      → triggered: z\n'
        '      → acknowledged 2026-09-01 (b): r'
    )
    undated_section = (
        '# Deferred items\n\n## No date\n'
        '- [ ] Item.\n      → acknowledged 2026-09-01 (b): r\n'
    )
    assert carry_used(parse_items(undated_ack)[0]) is False
    # An undated `triggered` note ages from the section date, so that date is the baseline.
    assert carry_used(parse_items(undated_state)[0]) is True
    assert carry_used(parse_items(undated_section)[0]) is False


def test_used_carry_on_an_item_that_is_not_aged_is_not_reported():
    fresh = one_section(
        '- [ ] Fresh item.\n'
        '      → acknowledged 2026-09-05 (b): r',
        date=TODAY - dt.timedelta(days=10),
    )
    held = one_section(
        '- [ ] Held item.\n'
        '      → held 2026-07-01: upstream\n'
        '      → acknowledged 2026-09-05 (b): r'
    )
    for text in (fresh, held):
        (item,) = parse_items(text)
        assert carry_used(item) is True
        stats = compute_stats([item], TODAY)
        assert (stats['aged_open'], stats['aged_acknowledged']) == (0, [])


def test_carry_line_names_section_and_first_words():
    text = (
        '# Deferred items\n\n'
        '## s1 — 2026-06-10\n'
        '- [ ] alpha beta gamma delta epsilon zeta eta theta\n'
        '      → acknowledged 2026-09-01 (a): r\n\n'
        '## s2 — 2026-06-11\n'
        '- [ ] one two three four five six seven\n'
        '      → acknowledged 2026-09-02 (b): r\n'
    )
    lines = format_report(compute_stats(parse_items(text), TODAY)).splitlines()
    assert (
        '  Carry used (only /deferred clears): '
        's1: alpha beta gamma delta epsilon zeta…; s2: one two three four five six…'
    ) in lines
    plain = format_report(compute_stats(parse_items(SAMPLE), TODAY))
    assert 'Carry used' not in plain


def test_new_lines_print_in_the_contract_order():
    backlog = one_section(
        '- [ ] Watch item.\n'
        '      Revisit if: later.\n'
        '- [ ] Planned item.\n'
        '      → planned 2026-09-02: specs/plans/9-x.md\n'
        '- [ ] Carried item.\n'
        '      → acknowledged 2026-09-01 (b): r\n'
        '- [ ] Noted item.\n'
        '      → done 2026-09-01 (plan 9)'
    )
    archive = one_section('- [x] Gone item. → removed 2026-10-27: why', name='7-old')
    stats = compute_stats(
        parse_items(backlog), TODAY, is_live=live, archived=parse_items(archive),
    )
    prefixes = (
        'Deferred backlog:', '  Watching:', '  Planned:', '  Carry used', '  Removed:',
        '  Warning:', '  Oldest open:',
    )
    lines = format_report(stats).splitlines()
    assert [p for line in lines for p in prefixes if line.startswith(p)] == list(prefixes)


def test_json_output_carries_the_new_keys(tmp_path, capsys):
    backlog = tmp_path / 'deferred_items.md'
    backlog.write_text(SAMPLE, encoding='utf-8')
    assert main(['--file', str(backlog), '--archive', str(tmp_path / 'nope.md'), '--json']) == 0
    payload = json.loads(capsys.readouterr().out)
    for key in (
        'exists', 'open', 'closed', 'total', 'closure_rate', 'aged_days',
        'aged_open', 'undated_open', 'open_with_done_note', 'oldest_open_days',
        'oldest_open_section', 'age_histogram',
        'watching', 'planned', 'aged_acknowledged', 'removed',
    ):
        assert key in payload, f'missing contract key: {key}'
    assert (payload['watching'], payload['planned'], payload['removed']) == (0, 0, 0)
    assert payload['aged_acknowledged'] == []


def test_absent_backlog_json_carries_the_new_keys(tmp_path, capsys):
    missing = str(tmp_path / 'nope.md')
    assert main(['--file', missing, '--archive', missing, '--json']) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload['exists'] is False
    for key in ('watching', 'planned', 'aged_acknowledged', 'removed'):
        assert key in payload, f'missing contract key: {key}'
