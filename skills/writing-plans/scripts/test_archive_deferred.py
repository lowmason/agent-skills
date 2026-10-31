'''Tests for archive_deferred.py — the per-item archive with a closure-note hold-back.

Every fixture is literal text, so the tests never call `git show`. The dates are
fixed: `today` is 2026-12-31 and `scan_from` is 2026-11-01, so a tick moves when
it is dated 2026-11-15 or earlier.
'''
from __future__ import annotations

import datetime as dt
import os
import stat
from collections import Counter
from pathlib import Path

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


FENCED_REMOVED = '''# Deferred items

## 9-a — 2026-12-30
- [x] j → done 2026-12-30: fixed
  ```
  → removed 2026-12-30: a quoted example
  ````
'''


def test_removed_note_quoted_in_a_fence_closed_by_a_longer_run_does_not_move_the_item():
    live, archived, _ = run(FENCED_REMOVED)
    assert '- [x] j → done 2026-12-30: fixed' in live
    assert '- [x] j' not in archived


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


# Fix round 1, finding 1: only closure notes dated on or after scan_from are read.
RESCAN = '''# Deferred items

## 12-d — 2026-09-01
- [x] a → done 2026-10-01: fixed; still worth a future item later.
      → done 2026-11-05: redone
- [x] b → done 2026-10-01: fixed
      → done 2026-11-05: redone; still worth a future item later.
- [x] c → done 2026-11-05: redone
      → done in plan 9: still worth a future item later.
- [x] e → done in plan 9: still worth a future item later.
      → done 2026-11-05: redone
'''


def test_phrase_only_in_a_note_before_scan_from_moves():
    live, archived, held = run(RESCAN)
    assert '- [x] a' not in live
    assert '- [x] a → done 2026-10-01: fixed; still worth a future item later.\n' in archived
    assert not any(': a…:' in line for line in held)


def test_phrase_in_a_note_on_or_after_scan_from_is_still_held():
    live, archived, held = run(RESCAN)
    assert '- [x] b' in live
    assert '- [x] b' not in archived
    assert held == ['  held back: 12-d: b…: → done 2026-11-05: redone; still worth a future item later.']


def test_undated_note_with_a_phrase_counts_as_older_beside_a_new_note():
    live, archived, _ = run(RESCAN)
    # After the new note and before it, an undated note is history.
    assert '- [x] c' not in live and '- [x] e' not in live
    assert '- [x] c → done 2026-11-05: redone\n' in archived
    assert '- [x] e → done in plan 9: still worth a future item later.\n' in archived


# Final review, finding 2: a blank line inside a closure note ends a scan unit, so
# a `→ item:` marker in the first paragraph does not cover the second.
PARAGRAPHS = '''# Deferred items

## 12-d — 2026-11-01
- [x] p: fix the parser
      → done 2026-11-02: fixed; the edge case is filed as a future item → item: 12-e.

      A second gap is left for later.
- [x] q: fix the lexer
      → done 2026-11-02: fixed; the edge case is filed as a future item → item: 12-e.
'''


def test_marker_in_one_paragraph_does_not_cover_the_next():
    live, archived, held = run(PARAGRAPHS)
    assert '- [x] p: fix the parser' in live
    assert '- [x] p' not in archived
    assert held == ['  held back: 12-d: p: fix the parser A second…: A second gap is left for later.']
    # Control: a one-paragraph note whose deferral is marked still moves.
    assert '- [x] q' not in live
    assert '- [x] q: fix the lexer\n' in archived


def _files(tmp_path, live: str = DRY_RUN, archived: str | None = TITLE):
    live_path, archive_path = tmp_path / 'deferred.md', tmp_path / 'archive.md'
    live_path.write_text(live, encoding='utf-8')
    if archived is not None:
        archive_path.write_text(archived, encoding='utf-8')
    return live_path, archive_path, ['--file', str(live_path), '--archive', str(archive_path)]


def _fail_replace_into(monkeypatch, targets: dict[Path, int]):
    '''Make `os.replace` raise for each target once it has had its allowed successes.'''
    real = os.replace
    calls = Counter()

    def fake(src, dst):
        dst = Path(dst)
        calls[dst] += 1
        if dst in targets and calls[dst] > targets[dst]:
            raise OSError(f'simulated failure for {dst}')
        return real(src, dst)

    monkeypatch.setattr(os, 'replace', fake)


# Fix round 1, finding 2: both files are written, or neither.
def test_failed_live_write_restores_the_archive(tmp_path, capsys, monkeypatch):
    live_path, archive_path, argv = _files(tmp_path)
    _fail_replace_into(monkeypatch, {live_path: 0})
    assert main(argv, today=TODAY) == 0
    out, err = capsys.readouterr()
    assert 'archived' not in out
    assert str(live_path) in err and 'both files are unchanged' in err
    assert live_path.read_text(encoding='utf-8') == DRY_RUN
    assert archive_path.read_text(encoding='utf-8') == TITLE
    assert sorted(path.name for path in tmp_path.iterdir()) == ['archive.md', 'deferred.md']
    monkeypatch.undo()
    assert main(argv, today=TODAY) == 0
    assert archive_path.read_text(encoding='utf-8').count('- [x] a → done 2026-01-02') == 1
    assert '- [x] a' not in live_path.read_text(encoding='utf-8')


def test_failed_live_write_removes_a_new_archive(tmp_path, capsys, monkeypatch):
    live_path, archive_path, argv = _files(tmp_path, archived=None)
    _fail_replace_into(monkeypatch, {live_path: 0})
    assert main(argv, today=TODAY) == 0
    out, err = capsys.readouterr()
    assert 'archived' not in out
    assert str(live_path) in err and 'both files are unchanged' in err
    assert not archive_path.exists()
    assert live_path.read_text(encoding='utf-8') == DRY_RUN


def test_failed_archive_write_changes_nothing(tmp_path, capsys, monkeypatch):
    live_path, archive_path, argv = _files(tmp_path)
    _fail_replace_into(monkeypatch, {archive_path: 0})
    assert main(argv, today=TODAY) == 0
    out, err = capsys.readouterr()
    assert 'archived' not in out
    assert str(archive_path) in err and 'both files are unchanged' in err
    assert live_path.read_text(encoding='utf-8') == DRY_RUN
    assert archive_path.read_text(encoding='utf-8') == TITLE


def test_failed_rollback_names_the_changed_archive(tmp_path, capsys, monkeypatch):
    live_path, archive_path, argv = _files(tmp_path)
    # The archive's first replace succeeds; the restore after the live failure does not.
    _fail_replace_into(monkeypatch, {live_path: 0, archive_path: 1})
    assert main(argv, today=TODAY) == 0
    out, err = capsys.readouterr()
    assert 'archived' not in out
    assert str(live_path) in err
    assert f'{archive_path} is changed' in err
    assert 'both files are unchanged' not in err


# Fix round 1, finding 3: a write keeps each file's mode.
@pytest.mark.parametrize('live_mode, archive_mode', [(0o644, 0o664), (0o664, 0o644)])
def test_write_keeps_both_file_modes(tmp_path, live_mode, archive_mode):
    live_path, archive_path, argv = _files(tmp_path)
    live_path.chmod(live_mode)
    archive_path.chmod(archive_mode)
    assert main(argv, today=TODAY) == 0
    assert '- [x] a' in archive_path.read_text(encoding='utf-8')
    assert stat.S_IMODE(live_path.stat().st_mode) == live_mode
    assert stat.S_IMODE(archive_path.stat().st_mode) == archive_mode


def test_new_archive_gets_the_umask_default_mode(tmp_path):
    live_path, archive_path, argv = _files(tmp_path, archived=None)
    mask = os.umask(0o022)
    try:
        assert main(argv, today=TODAY) == 0
    finally:
        os.umask(mask)
    assert stat.S_IMODE(archive_path.stat().st_mode) == 0o666 & ~0o022


# Fix round 1, finding 4: a read error names the file.
@pytest.mark.parametrize('bad', ['live', 'archive'])
def test_unreadable_file_is_named_and_nothing_changes(tmp_path, capsys, bad):
    live_path, archive_path, argv = _files(tmp_path)
    broken = live_path if bad == 'live' else archive_path
    broken.write_bytes(b'# Deferred items\n\xff\xfe\n')
    before = live_path.read_bytes(), archive_path.read_bytes()
    assert main(argv, today=TODAY) == 0
    out, err = capsys.readouterr()
    assert 'archived' not in out
    assert str(broken) in err
    assert (live_path.read_bytes(), archive_path.read_bytes()) == before


# Final review, finding 1: an archive path that is the backlog itself is refused.
def _same_file_argvs(tmp_path, monkeypatch) -> dict[str, tuple[list[str], Path]]:
    '''Each way to name the backlog as its own archive, with the file it names.'''
    monkeypatch.chdir(tmp_path)
    live_path = tmp_path / 'deferred.md'
    live_path.write_text(DRY_RUN, encoding='utf-8')
    (tmp_path / 'link.md').symlink_to(live_path)
    default_archive = tmp_path / 'specs' / 'completed' / 'deferred_items.md'
    default_archive.parent.mkdir(parents=True)
    default_archive.write_text(DRY_RUN, encoding='utf-8')
    return {
        'equal': (['--file', str(live_path), '--archive', str(live_path)], live_path),
        'relative': (['--file', 'deferred.md', '--archive', str(live_path)], live_path),
        'symlink': (['--file', str(live_path), '--archive', 'link.md'], live_path),
        'default': (['--file', 'specs/completed/deferred_items.md'], default_archive),
    }


@pytest.mark.parametrize('case', ['equal', 'relative', 'symlink', 'default'])
@pytest.mark.parametrize('dry_run', [False, True])
def test_archive_that_is_the_backlog_is_refused(tmp_path, capsys, monkeypatch, case, dry_run):
    argv, target = _same_file_argvs(tmp_path, monkeypatch)[case]
    assert main(argv + ['--dry-run'] * dry_run, today=TODAY) == 0
    out, err = capsys.readouterr()
    assert 'archived' not in out
    assert 'same file' in err and len(err.splitlines()) == 1
    assert target.read_text(encoding='utf-8') == DRY_RUN
    assert (tmp_path / 'link.md').is_symlink()
    assert sorted(path.name for path in tmp_path.iterdir()) == ['deferred.md', 'link.md', 'specs']


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
    'redone': (REDONE, TITLE), 'rescan': (RESCAN, TITLE), 'paragraphs': (PARAGRAPHS, TITLE),
}


@pytest.mark.parametrize('live, archived', FIXTURES.values(), ids=FIXTURES.keys())
def test_archive_loses_and_duplicates_nothing(live, archived):
    new_live, new_archive, _ = run(live, archived)
    assert _items(new_live) + _items(new_archive) == _items(live) + _items(archived)
    assert _body_lines(new_live) + _body_lines(new_archive) == (
        _body_lines(live) + _body_lines(archived))
    assert run(new_live, new_archive)[:2] == (new_live, new_archive)
