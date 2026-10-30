'''Tests for archive_deferred.py — the per-item archive with a closure-note hold-back.

Every fixture is literal text, so the tests never call `git show`. The dates are
fixed: `today` is 2026-12-31 and `scan_from` is 2026-11-01, so a tick moves when
it is dated 2026-11-15 or earlier.
'''
from __future__ import annotations

import datetime as dt
from collections import Counter

import pytest

from archive_deferred import archive, main
from deferred_stats import SECTION_RE, parse_items

TODAY = dt.date(2026, 12, 31)
SCAN_FROM = dt.date(2026, 11, 1)
TITLE = '# Deferred items\n'


def run(live: str, archived: str = TITLE) -> tuple[str, str, list[str]]:
    return archive(live, archived, TODAY, scan_from=SCAN_FROM)


OLD_TICK = '''# Deferred items

## 9-a — 2026-09-01
- [x] a → done 2026-10-01 (plan 9)
- [ ] keep open

## 10-b — 2026-09-05
- [ ] other
'''


def test_tick_older_than_45_days_moves():
    live, archived, held = run(OLD_TICK)
    assert live == '''# Deferred items

## 9-a — 2026-09-01
- [ ] keep open

## 10-b — 2026-09-05
- [ ] other
'''
    assert archived == '''# Deferred items

## 9-a — 2026-09-01
- [x] a → done 2026-10-01 (plan 9)
'''
    assert held == []


AGE_EDGE = '''# Deferred items

## 9-a — 2026-09-01
- [x] c → retired 2026-11-16: superseded
- [x] d → retired 2026-11-15: superseded
'''


def test_tick_45_days_old_or_newer_stays():
    live, archived, _ = run(AGE_EDGE)
    assert '- [x] c → retired 2026-11-16: superseded' in live
    assert '- [x] c' not in archived
    # The control, 46 days old, moves.
    assert '- [x] d' not in live
    assert '- [x] d → retired 2026-11-15: superseded' in archived


UNDATED_TICKS = '''# Deferred items

## 9-a — 2026-10-01
- [x] e → done in plan 9

## 11-c — 2026-12-01
- [x] f → done in plan 9
'''


def test_undated_tick_falls_back_to_section_date():
    live, archived, _ = run(UNDATED_TICKS)
    assert '- [x] e' not in live
    assert '## 9-a — 2026-10-01\n- [x] e → done in plan 9\n' in archived
    assert '## 11-c — 2026-12-01\n- [x] f → done in plan 9\n' in live
    assert '- [x] f' not in archived


UNDATED_SECTION = '''# Deferred items

## notes
- [x] g → done in plan 9

## 9-a — 2026-01-01
- [x] control → done 2026-01-02
'''


def test_undated_tick_in_undated_section_stays(tmp_path):
    live, archived, _ = run(UNDATED_SECTION)
    assert '## notes\n- [x] g → done in plan 9\n' in live
    assert '- [x] g' not in archived
    assert '- [x] control' not in live
    live_path, archive_path = tmp_path / 'deferred.md', tmp_path / 'archive.md'
    live_path.write_text(UNDATED_SECTION, encoding='utf-8')
    archive_path.write_text(TITLE, encoding='utf-8')
    assert main(['--file', str(live_path), '--archive', str(archive_path)], today=TODAY) == 0
    assert '- [x] g → done in plan 9' in live_path.read_text(encoding='utf-8')
    assert '- [x] control' in archive_path.read_text(encoding='utf-8')


OPEN_ITEM = '''# Deferred items

## 9-a — 2026-01-01
- [ ] h → done 2026-01-02: an open item with a stray done note
- [x] control → done 2026-01-02
'''


def test_open_item_never_moves():
    live, archived, _ = run(OPEN_ITEM)
    assert '- [ ] h → done 2026-01-02' in live
    assert '- [ ] h' not in archived
    assert '- [x] control' not in live


REMOVED = '''# Deferred items

## 66-r — 2026-12-30
- [x] b → removed 2026-12-30: skill archived
- [x] i → done 2026-12-30: fixed
'''


def test_removed_item_moves_at_any_age():
    live, archived, _ = run(REMOVED)
    assert '- [x] b' not in live
    assert '## 66-r — 2026-12-30\n- [x] b → removed 2026-12-30: skill archived\n' in archived
    # The control: a one-day-old done tick waits.
    assert '- [x] i → done 2026-12-30: fixed' in live


MIXED_SECTION = '''# Deferred items

## 9-a — 2026-09-01
- [x] a → done 2026-10-01 (plan 9)
- [ ] still open
'''


def test_heading_in_both_files_while_section_drains():
    live, archived, _ = run(MIXED_SECTION)
    assert live == '''# Deferred items

## 9-a — 2026-09-01
- [ ] still open
'''
    assert archived == '''# Deferred items

## 9-a — 2026-09-01
- [x] a → done 2026-10-01 (plan 9)
'''


PREAMBLE_SECTION = '''# Deferred items

## 9-a — 2026-09-01
Preamble line about the section.
- [x] a → done 2026-10-01 (plan 9)

## 10-b — 2026-09-05
- [ ] other
'''


def test_live_heading_and_preamble_go_with_last_item():
    live, archived, _ = run(PREAMBLE_SECTION)
    assert live == '''# Deferred items

## 10-b — 2026-09-05
- [ ] other
'''
    assert archived == '''# Deferred items

## 9-a — 2026-09-01
Preamble line about the section.
- [x] a → done 2026-10-01 (plan 9)
'''


DATE_ORDER_LIVE = '''# Deferred items

## 8-m — 2026-08-01
- [x] p → done 2026-08-02

## 10-n — 2026-10-01
- [x] q → done 2026-10-02
'''

DATE_ORDER_ARCHIVE = '''# Deferred items

## 7-j — 2026-07-01
- [x] old j → done 2026-07-02

## 9-k — 2026-09-01
- [x] old k → done 2026-09-02

## log
- [x] undated log entry
'''


def test_new_heading_lands_in_date_order():
    live, archived, _ = run(DATE_ORDER_LIVE, DATE_ORDER_ARCHIVE)
    assert live == TITLE
    assert archived == '''# Deferred items

## 7-j — 2026-07-01
- [x] old j → done 2026-07-02

## 8-m — 2026-08-01
- [x] p → done 2026-08-02

## 9-k — 2026-09-01
- [x] old k → done 2026-09-02

## 10-n — 2026-10-01
- [x] q → done 2026-10-02

## log
- [x] undated log entry
'''


EXISTING_LIVE = '''# Deferred items

## 9-a — 2026-09-01

- [x] new → done 2026-10-01
- [ ] open
'''

EXISTING_ARCHIVE = '''# Deferred items

## 9-a — 2026-09-01
- [x] old → done 2026-09-02
      a continuation line

## 10-b — 2026-09-05
- [x] other → done 2026-09-06
'''


def test_existing_archive_heading_gains_the_item_at_its_end():
    live, archived, _ = run(EXISTING_LIVE, EXISTING_ARCHIVE)
    assert live == '''# Deferred items

## 9-a — 2026-09-01

- [ ] open
'''
    assert archived == '''# Deferred items

## 9-a — 2026-09-01
- [x] old → done 2026-09-02
      a continuation line
- [x] new → done 2026-10-01

## 10-b — 2026-09-05
- [x] other → done 2026-09-06
'''


HELD = '''# Deferred items

## 12-d — 2026-11-01
- [x] j: fix the parser
      → done 2026-11-02: fixed; the edge case is still worth a future item later.
- [x] k → done 2026-11-02: fixed cleanly
- [x] l: raised as a future item in review
      → done 2026-11-02: fixed
'''


def test_closure_note_with_unmarked_candidate_is_held_back():
    live, archived, held = run(HELD)
    assert '- [x] j: fix the parser' in live
    assert '- [x] j' not in archived
    assert held == [
        '  held back: 12-d: j: fix the parser…: '
        '→ done 2026-11-02: fixed; the edge case is still worth a future item later.'
    ]
    # Controls: a clean closure note moves, and so does an item whose own text,
    # not its closure note, holds the phrase.
    assert '- [x] k' not in live
    assert '- [x] l' not in live
    assert '- [x] l: raised as a future item in review\n      → done 2026-11-02: fixed\n' in archived


OLD_NOTE = '''# Deferred items

## 12-d — 2026-09-01
- [x] j: fix the parser
      → done 2026-10-01: fixed; the edge case is still worth a future item later.
'''


def test_closure_note_before_scan_from_is_not_held_back():
    live, archived, held = run(OLD_NOTE)
    assert held == []
    assert '- [x] j' not in live
    assert '→ done 2026-10-01: fixed; the edge case is still worth a future item later.' in archived


# The section date is after scan_from and more than 45 days before today, so the
# undated note's fallback age moves it, and the fallback date must not pull it
# into the hold-back.
UNDATED_NOTE = '''# Deferred items

## 12-d — 2026-11-10
- [x] j: fix the parser
      → done in plan 9: fixed; the edge case is still worth a future item later.
'''


def test_undated_closure_note_counts_as_older():
    live, archived, held = run(UNDATED_NOTE)
    assert held == []
    assert '- [x] j' not in live
    assert '→ done in plan 9: fixed; the edge case is still worth a future item later.' in archived


DRY_RUN = '''# Deferred items

## 9-a — 2026-01-01
- [x] a → done 2026-01-02
- [ ] keep
'''


def test_dry_run_writes_nothing(tmp_path, capsys):
    live_path, archive_path = tmp_path / 'deferred.md', tmp_path / 'archive.md'
    live_path.write_text(DRY_RUN, encoding='utf-8')
    archive_path.write_text(TITLE, encoding='utf-8')
    assert main(['--file', str(live_path), '--archive', str(archive_path), '--dry-run'],
                today=TODAY) == 0
    assert capsys.readouterr().out == 'archived 1 item(s), held back 0:\n'
    assert live_path.read_text(encoding='utf-8') == DRY_RUN
    assert archive_path.read_text(encoding='utf-8') == TITLE


# Column-0 prose between items, a blank line inside an item, a column-0 plain
# bullet that closes an item, an itemless log section, and a section that drains
# at the end of the file.
TRICKY = '''# Deferred items

## Aged-backlog acknowledgements
- 2026-09-08 — finished x with 1 item aged >45d.

## 13-w — 2026-07-22
Deferred from the audit (preamble).

Robustness:
- [x] m → done 2026-08-01: fixed
      continued line

      after a blank, still m
Cosmetic:
- [ ] n stays open
- plain bullet closes n

## 14-z — 2026-07-23
- [x] o → done 2026-08-02
'''


def test_second_run_moves_nothing():
    first_live, first_archive, first_held = run(TRICKY + HELD.removeprefix(TITLE + '\n'))
    assert first_held
    second_live, second_archive, second_held = run(first_live, first_archive)
    assert (second_live, second_archive) == (first_live, first_archive)
    assert second_held == first_held


def test_item_span_keeps_blank_continuations_and_stops_at_column_zero_prose():
    live, archived, _ = run(TRICKY)
    assert live == '''# Deferred items

## Aged-backlog acknowledgements
- 2026-09-08 — finished x with 1 item aged >45d.

## 13-w — 2026-07-22
Deferred from the audit (preamble).

Robustness:
Cosmetic:
- [ ] n stays open
- plain bullet closes n
'''
    assert archived == '''# Deferred items

## 13-w — 2026-07-22
- [x] m → done 2026-08-01: fixed
      continued line

      after a blank, still m

## 14-z — 2026-07-23
- [x] o → done 2026-08-02
'''


REPEATED_LIVE = '''# Deferred items

## 9-a — 2026-09-01
- [x] first → done 2026-10-01

## 10-b — 2026-09-05
- [ ] other

## 9-a — 2026-09-01
- [x] second → done 2026-10-02
- [ ] open
'''

REPEATED_ARCHIVE = '''# Deferred items

## 9-a — 2026-09-01
- [x] zeroth → done 2026-09-02
'''


def test_repeated_live_section_lands_under_one_archive_heading():
    live, archived, _ = run(REPEATED_LIVE, REPEATED_ARCHIVE)
    assert live == '''# Deferred items

## 10-b — 2026-09-05
- [ ] other

## 9-a — 2026-09-01
- [ ] open
'''
    assert archived == '''# Deferred items

## 9-a — 2026-09-01
- [x] zeroth → done 2026-09-02
- [x] first → done 2026-10-01
- [x] second → done 2026-10-02
'''


CUT_SPACING = '''# Deferred items

## 9-a — 2026-09-01
- [x] first → done 2026-10-01

Group one:

- [x] middle → done 2026-10-01

Group two:
- [ ] open
'''


def test_cut_leaves_no_doubled_or_leading_blank():
    live, _, _ = run(CUT_SPACING)
    assert live == '''# Deferred items

## 9-a — 2026-09-01
Group one:

Group two:
- [ ] open
'''


DRAIN_SPACED_LIVE = '''# Deferred items

## 9-a — 2026-09-01

- [x] later → done 2026-10-01
'''


def test_drained_section_appends_without_a_leading_blank():
    _, archived, _ = run(DRAIN_SPACED_LIVE, REPEATED_ARCHIVE)
    assert archived == '''# Deferred items

## 9-a — 2026-09-01
- [x] zeroth → done 2026-09-02
- [x] later → done 2026-10-01
'''


REDONE = '''# Deferred items

## 9-a — 2026-09-01
- [x] r → done 2026-10-01: first pass
      → done 2026-12-01: redone after a regression
- [x] s → done 2026-10-01: once
'''


def test_tick_date_is_the_latest_closure_note():
    live, archived, _ = run(REDONE)
    assert '- [x] r → done 2026-10-01: first pass' in live
    assert '- [x] r' not in archived
    assert '- [x] s' not in live


ODD_SPACING ='- [x] before any heading\n\n\n## 11-c — 2026-12-01\n- [x] f → done in plan 9\n\n\n## log\n- [ ] x'


def test_nothing_to_move_returns_both_texts_unchanged():
    live, archived, held = run(ODD_SPACING, DATE_ORDER_ARCHIVE)
    assert (live, archived, held) == (ODD_SPACING, DATE_ORDER_ARCHIVE, [])


def test_missing_live_file_exits_zero(tmp_path, capsys):
    missing = tmp_path / 'absent.md'
    assert main(['--file', str(missing), '--archive', str(tmp_path / 'archive.md')]) == 0
    assert capsys.readouterr().out == 'archived 0 item(s), held back 0:\n'
    assert not missing.exists()


def test_missing_archive_file_is_created_with_the_title(tmp_path, capsys):
    live_path, archive_path = tmp_path / 'deferred.md', tmp_path / 'completed' / 'archive.md'
    live_path.write_text(DRY_RUN, encoding='utf-8')
    assert main(['--file', str(live_path), '--archive', str(archive_path)], today=TODAY) == 0
    assert capsys.readouterr().out == 'archived 1 item(s), held back 0:\n'
    assert archive_path.read_text(encoding='utf-8') == (
        '# Deferred items\n\n## 9-a — 2026-01-01\n- [x] a → done 2026-01-02\n')


def test_cli_prints_one_line_per_held_item(tmp_path, capsys):
    live_path, archive_path = tmp_path / 'deferred.md', tmp_path / 'archive.md'
    live_path.write_text(HELD, encoding='utf-8')
    archive_path.write_text(TITLE, encoding='utf-8')
    argv = ['--file', str(live_path), '--archive', str(archive_path), '--dry-run']
    assert main(argv, today=TODAY) == 0
    assert capsys.readouterr().out.splitlines() == [
        'archived 2 item(s), held back 1:',
        '  held back: 12-d: j: fix the parser…: '
        '→ done 2026-11-02: fixed; the edge case is still worth a future item later.',
    ]


def _items(text: str) -> Counter:
    return Counter((item.section, item.checked, item.text) for item in parse_items(text))


def _body_lines(text: str) -> Counter:
    return Counter(line for line in text.splitlines()
                   if line.strip() and not SECTION_RE.match(line))


FIXTURES = {
    'old_tick': (OLD_TICK, TITLE), 'age_edge': (AGE_EDGE, TITLE),
    'undated_ticks': (UNDATED_TICKS, TITLE), 'undated_section': (UNDATED_SECTION, TITLE),
    'open_item': (OPEN_ITEM, TITLE), 'removed': (REMOVED, TITLE),
    'mixed_section': (MIXED_SECTION, TITLE), 'preamble_section': (PREAMBLE_SECTION, TITLE),
    'date_order': (DATE_ORDER_LIVE, DATE_ORDER_ARCHIVE),
    'existing': (EXISTING_LIVE, EXISTING_ARCHIVE), 'held': (HELD, TITLE),
    'old_note': (OLD_NOTE, TITLE), 'undated_note': (UNDATED_NOTE, TITLE),
    'dry_run': (DRY_RUN, TITLE), 'tricky': (TRICKY, TITLE),
    'repeated': (REPEATED_LIVE, REPEATED_ARCHIVE), 'odd_spacing': (ODD_SPACING, DATE_ORDER_ARCHIVE),
    'cut_spacing': (CUT_SPACING, TITLE), 'drain_spaced': (DRAIN_SPACED_LIVE, REPEATED_ARCHIVE),
    'redone': (REDONE, TITLE),
}


@pytest.mark.parametrize('live, archived', FIXTURES.values(), ids=FIXTURES.keys())
def test_archive_loses_and_duplicates_nothing(live, archived):
    new_live, new_archive, _ = run(live, archived)
    assert _items(new_live) + _items(new_archive) == _items(live) + _items(archived)
    assert _body_lines(new_live) + _body_lines(new_archive) == (
        _body_lines(live) + _body_lines(archived))
    assert run(new_live, new_archive)[:2] == (new_live, new_archive)
