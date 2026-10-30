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
    compute_stats,
    format_report,
    parse_items,
    path_is_live,
)

SCRIPT = Path(__file__).with_name('deferred_stats.py')
TODAY = dt.date(2026, 9, 8)
NINETY_DAYS_AGO = TODAY - dt.timedelta(days=90)

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
