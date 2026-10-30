#!/usr/bin/env python3
# /// script
# requires-python = '>=3.11'
# dependencies = []
# ///
'''Report deferred-backlog health from specs/deferred_items.md and its archive.

Parses the backlog into items. An item is a column-0 checkbox line
plus every line after it up to the next item or `##` heading, so the dated notes
on its continuation lines belong to it. The report gives open and ever-closed
counts, closure rate, an age histogram, and the aged tail. An item ages from its
`## <plan> — <YYYY-MM-DD>` section header, which the Plan Completion Protocol
has always written, so every existing item already carries one and no backfill
is needed.

Notes start with `→`, a lowercase word and an optional ISO date. A note inside an
inline code span is a quotation and sets nothing. The checkbox alone decides open
or closed: an open item with a `→ done` note stays open and the report warns.
For an open item only `→ held`, `→ triggered` and `→ planned` set the aging
state, and the latest of those wins. The first rule that matches decides:

1. `triggered`: ages from the note's date, not the section's date.
2. `held`: not aged, counted as watching.
3. `planned`: not aged, counted as planned, while the file the note names is
   live (it exists and no path part is `completed`). A gone file falls through.
4. `watch`: the text has `Revisit if:` and no `Done when:`. Not aged, counted as
   watching.
5. `work`: everything else, including an item with an `→ owner-only` note. It
   ages from the section date.

Watching and planned items count as open but stay out of the aged tail, the
age histogram and the oldest-open figures.

An item leaves the live file only by a move to the archive file
`specs/completed/deferred_items.md` (spec D4), so the archive is read too. Every
archived item counts as closed and never as open or aged. A closed item with a
`→ removed` note is also reported as removed: it left the backlog without being
done or retired, and it still counts as closed. A missing archive file is fine.

An aged item has spent its one carry when it has an `→ acknowledged` note dated
after its latest `held`, `triggered` or `planned` note, or after its section
date when it has none (spec D10). The report names those items by section and
first words, since only `/deferred` can clear them.

Sections whose heading carries no usable date still contribute to the
open/closed counts but are excluded from every age figure and reported as
``undated_open``. That covers three cases: no date at all (for example the
``## Aged-backlog acknowledgements`` log), a date that is not a real calendar
date (``2026-09-31``), and a date in the future — the last two being typos in a
hand-written header rather than ages. The count covers only items that would
otherwise age, so a watch item in an undated section is not reported.

Usage:
    python3 <this-skill-dir>/scripts/deferred_stats.py
    python3 <this-skill-dir>/scripts/deferred_stats.py --json
    python3 <this-skill-dir>/scripts/deferred_stats.py \\
        --file path/to/deferred_items.md --archive path/to/archive.md --aged-days 60

Always exits 0. This is a reporter, not a gate: the caller decides what to do
with ``aged_open``, so a large backlog never fails a script invocation.
'''

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_AGED_DAYS = 45
VOLUME_THRESHOLD = 20
FIRST_WORDS_COUNT = 6
DEFAULT_PATH = Path('specs/deferred_items.md')
DEFAULT_ARCHIVE_PATH = Path('specs/completed/deferred_items.md')

SECTION_RE = re.compile(r'^##\s+(?P<name>.+?)(?:\s+—\s+(?P<date>\d{4}-\d{2}-\d{2}))?\s*$')
ITEM_RE = re.compile(r'^- \[(?P<mark>[ xX])\]')
NOTE_RE = re.compile(
    r'→[ \t]*(?P<kind>[a-z]+(?:-[a-z]+)*)(?![\w-])'
    r'(?:[ \t]+(?P<date>\d{4}-\d{2}-\d{2})(?!\d))?'
)
CODE_SPAN_RE = re.compile(r'(`+).+?\1', re.DOTALL)
MD_PATH_RE = re.compile(r'[\w./-]+\.md(?!\w)')

STATE_KINDS = frozenset({'held', 'triggered', 'planned'})
WATCH_LINE = 'Revisit if:'
WORK_LINE = 'Done when:'

AGE_BUCKETS: tuple[tuple[str, int, int | None], ...] = (
    ('0-14d', 0, 14),
    ('15-30d', 15, 30),
    ('31-45d', 31, 45),
    ('46-90d', 46, 90),
    ('91d+', 91, None),
)


@dataclass
class Note:
    '''One `→ <kind> <date>: <rest>` note, cut at the end of its line.'''

    kind: str
    date: dt.date | None
    rest: str


@dataclass
class Item:
    '''A checkbox item. `text` is everything after the checkbox, notes included.'''

    section: str
    section_date: dt.date | None
    checked: bool
    text: str
    notes: list[Note] = field(default_factory=list)


def _parse_date(raw: str | None) -> dt.date | None:
    '''Header or note date, or None when there is no usable one.

    SECTION_RE and NOTE_RE only match the date's *shape*, so `2026-09-31` reaches
    here and ``fromisoformat`` rejects it. These dates are hand-typed by whoever
    ran the Plan Completion Protocol, so that typo is the expected failure — and
    parsing is a single pass before any output, so letting it raise would suppress
    every other section's counts and exit non-zero, breaking the always-exits-0
    contract both callers rely on. Losing one section's age is the cheaper loss.
    '''
    if raw is None:
        return None
    try:
        return dt.date.fromisoformat(raw)
    except ValueError:
        return None


def path_is_live(path: str) -> bool:
    '''True when `path` exists and no part of it is a `completed` folder.'''
    target = Path(path)
    return target.exists() and 'completed' not in target.parts


def _mask_code(text: str) -> str:
    '''Blank every inline code span (newlines kept), so offsets stay valid.

    A note form quoted in backticks is prose about the protocol, not a note.
    '''
    return CODE_SPAN_RE.sub(lambda span: re.sub(r'[^\n]', ' ', span.group(0)), text)


def _find_notes(text: str, masked: str) -> list[tuple[int, int, Note]]:
    '''Every note outside a code span, as (start, end, note).

    A note ends at its line's end or at the next note, whichever comes first.
    `masked` is `_mask_code(text)`; offsets are shared.
    '''
    matches = list(NOTE_RE.finditer(masked))
    found = []
    for index, match in enumerate(matches):
        line_end = text.find('\n', match.end())
        end = len(text) if line_end == -1 else line_end
        if index + 1 < len(matches):
            end = min(end, matches[index + 1].start())
        rest = text[match.end():end].lstrip(' \t:').rstrip()
        note = Note(match.group('kind'), _parse_date(match.group('date')), rest)
        found.append((match.start(), end, note))
    return found


def _cut(text: str, spans: list[tuple[int, int]]) -> str:
    pieces, cursor = [], 0
    for start, end in spans:
        pieces.append(text[cursor:start])
        cursor = end
    pieces.append(text[cursor:])
    return ''.join(pieces)


def _body(item: Item) -> tuple[str, str]:
    '''The item's text with every note cut out, plain and with code spans masked.'''
    masked = _mask_code(item.text)
    spans = [(start, end) for start, end, _ in _find_notes(item.text, masked)]
    return _cut(item.text, spans), _cut(masked, spans)


def first_words(item: Item) -> str:
    '''The first words of the item's own text, notes left out.'''
    return ' '.join(_body(item)[0].split()[:FIRST_WORDS_COUNT])


def parse_items(text: str) -> list[Item]:
    '''Split the backlog into items, each with its continuation lines and notes.

    Lines before the first ``##`` heading are preamble and are ignored. Only a
    line starting at column 0 with ``- [ ]`` or ``- [x]`` begins an item. Any
    other line joins the open item, which keeps a wrapped line or an indented
    nested bullet, and its notes, with its item. A non-blank line at column 0
    that is neither a heading nor an item (such as a bullet in the
    ``## Aged-backlog acknowledgements`` log) closes the open item.
    '''
    items: list[Item] = []
    heading: tuple[str, dt.date | None] | None = None
    checked = False
    lines: list[str] = []

    def close() -> None:
        if lines and heading is not None:
            body = '\n'.join(lines)
            notes = [note for _, _, note in _find_notes(body, _mask_code(body))]
            items.append(Item(heading[0], heading[1], checked, body, notes))
        lines.clear()

    for line in text.splitlines():
        section = SECTION_RE.match(line)
        if section:
            close()
            heading = (section.group('name').strip(), _parse_date(section.group('date')))
            continue
        start = ITEM_RE.match(line)
        if start and heading is not None:
            close()
            checked = start.group('mark') != ' '
            lines.append(line[start.end():].strip())
            continue
        if not lines or not line.strip():
            continue
        if line[0].isspace():
            lines.append(line.strip())
        else:
            close()
    close()
    return items


def _latest_state_note(notes: list[Note]) -> Note | None:
    '''The `held`, `triggered` or `planned` note with the latest date.

    An undated note sorts before any dated one. A tie goes to the note written
    later, since the backlog is append-only.
    '''
    state_notes = [(note.date or dt.date.min, position, note)
                   for position, note in enumerate(notes) if note.kind in STATE_KINDS]
    return max(state_notes)[2] if state_notes else None


def carry_used(item: Item) -> bool:
    '''True when the item has spent its one carry past the aged-backlog gate.

    A carry is used when an `→ acknowledged` note is dated strictly after the
    item's latest `held`, `triggered` or `planned` note, or after its section date
    when it has none (spec D10). The latest state note counts even when a
    `planned` file has since retired, since writing it was a state change. A state
    note with no date falls back to the section date, as `aging_state` does for a
    `triggered` note. An undated acknowledgement, or an item with no date to
    compare against, never counts as a used carry: no order can be shown.

    Whether the item is aged is not decided here. `compute_stats` lists only
    aged items.
    '''
    latest = _latest_state_note(item.notes)
    baseline = item.section_date
    if latest is not None and latest.date is not None:
        baseline = latest.date
    if baseline is None:
        return False
    return any(
        note.kind == 'acknowledged' and note.date is not None and note.date > baseline
        for note in item.notes
    )


def _has_note(item: Item, kind: str) -> bool:
    return any(note.kind == kind for note in item.notes)


def _planned_file_is_live(note: Note, is_live: Callable[[str], bool]) -> bool:
    path = MD_PATH_RE.search(note.rest)
    return path is not None and is_live(path.group(0))


def aging_state(
    item: Item,
    is_live: Callable[[str], bool] = path_is_live,
) -> tuple[str, dt.date | None]:
    '''The item's aging state and the date it ages from.

    The state is one of `triggered`, `held`, `planned`, `watch` or `work`, decided
    by the first rule of the module docstring that matches. The date is None for
    a state that does not age, and for `work` or `triggered` when there is no
    usable date to age from. A `triggered` note with no date ages from the
    section date.
    '''
    latest = _latest_state_note(item.notes)
    if latest is not None:
        if latest.kind == 'triggered':
            return 'triggered', latest.date or item.section_date
        if latest.kind == 'held':
            return 'held', None
        if _planned_file_is_live(latest, is_live):
            return 'planned', None
    flat = ' '.join(_body(item)[1].split())
    if WATCH_LINE in flat and WORK_LINE not in flat:
        return 'watch', None
    return 'work', item.section_date


def _bucket_label(days: int) -> str:
    for label, low, high in AGE_BUCKETS:
        if days >= low and (high is None or days <= high):
            return label
    return AGE_BUCKETS[-1][0]


def compute_stats(
    items: list[Item],
    today: dt.date,
    aged_days: int = DEFAULT_AGED_DAYS,
    is_live: Callable[[str], bool] = path_is_live,
    archived: Sequence[Item] = (),
) -> dict:
    '''Aggregate parsed items into the reporting contract.

    ``items`` are the live file's items and ``archived`` the archive file's. Every
    archived item counts as closed whatever its checkbox says, and it is never
    aged, never warned about and never listed as a carry (spec section 5).

    ``closure_rate`` is closed / (open + closed), where closed adds the live
    file's ticked items to the archive's items. An item can leave the live file,
    by a move to the archive or by a removal (spec D4), but it stays counted as
    closed, so closed is still ever-closed. It is ``None`` for an empty backlog
    rather than 0.0, so "nothing here yet" reads differently from "nothing ever
    closed".

    ``removed`` counts the closed items, in either file, that carry a
    `→ removed` note. They are part of ``closed`` too. An unticked item with that
    note is open, since the checkbox decides.

    ``watching`` counts `held` and `watch` items and ``planned`` counts `planned`
    items. Both are open, and neither enters ``aged_open``, the histogram or the
    oldest-open figures. ``open_with_done_note`` lists the open items that carry
    a `→ done` note, for the report's warning. ``aged_acknowledged`` lists the
    aged open items whose carry is used (see ``carry_used``), as section and
    first words.
    '''
    open_items = [item for item in items if not item.checked]
    closed_items = [item for item in items if item.checked] + list(archived)
    open_count = len(open_items)
    closed_count = len(closed_items)
    total = open_count + closed_count

    histogram = {label: 0 for label, _, _ in AGE_BUCKETS}
    aged_open = 0
    undated_open = 0
    watching = 0
    planned = 0
    aged_acknowledged: list[dict[str, str]] = []
    oldest_days: int | None = None
    oldest_section: str | None = None

    for item in open_items:
        state, since = aging_state(item, is_live)
        if state in ('held', 'watch'):
            watching += 1
            continue
        if state == 'planned':
            planned += 1
            continue
        days = None if since is None else (today - since).days
        if days is None or days < 0:
            # No date, or dated in the future: a typo, not an age. Bucketing it
            # would put a phantom item in the oldest bucket (_bucket_label's
            # fallback), so it degrades exactly like an unparseable date.
            undated_open += 1
            continue
        histogram[_bucket_label(days)] += 1
        if days > aged_days:
            aged_open += 1
            if carry_used(item):
                aged_acknowledged.append(
                    {'section': item.section, 'first_words': first_words(item)}
                )
        if oldest_days is None or days > oldest_days:
            oldest_days = days
            oldest_section = item.section

    return {
        'exists': True,
        'open': open_count,
        'closed': closed_count,
        'total': total,
        'closure_rate': round(closed_count / total, 4) if total else None,
        'aged_days': aged_days,
        'aged_open': aged_open,
        'undated_open': undated_open,
        'watching': watching,
        'planned': planned,
        'aged_acknowledged': aged_acknowledged,
        'removed': sum(1 for item in closed_items if _has_note(item, 'removed')),
        'open_with_done_note': [
            {'section': item.section, 'first_words': first_words(item)}
            for item in open_items if _has_note(item, 'done')
        ],
        'oldest_open_days': oldest_days,
        'oldest_open_section': oldest_section,
        'age_histogram': [
            {'label': label, 'count': histogram[label]} for label, _, _ in AGE_BUCKETS
        ],
    }


def absent_stats(aged_days: int = DEFAULT_AGED_DAYS) -> dict:
    '''The contract shape for a backlog file that does not exist yet.'''
    stats = compute_stats([], dt.date.today(), aged_days)
    stats['exists'] = False
    return stats


def format_report(stats: dict) -> str:
    '''One-screen human summary. The caller pastes this into its own report.'''
    if not stats['exists']:
        return 'Deferred backlog: no specs/deferred_items.md in this repo — nothing deferred.'

    rate = stats['closure_rate']
    rate_text = 'n/a' if rate is None else f'{rate * 100:.0f}%'
    lines = [
        f'Deferred backlog: {stats["open"]} open, {stats["closed"]} ever closed '
        f'(closure rate {rate_text}), aged >{stats["aged_days"]}d: {stats["aged_open"]}.',
    ]
    if stats['watching']:
        lines.append(f'  Watching: {stats["watching"]} (Revisit-if or held; not aged).')
    if stats['planned']:
        lines.append(f'  Planned: {stats["planned"]} (in a live plan or spec; not aged).')
    if stats['aged_acknowledged']:
        carried = '; '.join(
            f'{used["section"]}: {used["first_words"]}…' for used in stats['aged_acknowledged']
        )
        lines.append(f'  Carry used (only /deferred clears): {carried}')
    if stats['removed']:
        lines.append(f'  Removed: {stats["removed"]} (counted as closed).')
    for flagged in stats['open_with_done_note']:
        lines.append(
            f'  Warning: open item has a → done note: '
            f'{flagged["section"]}: {flagged["first_words"]}…'
        )
    if stats['oldest_open_days'] is not None:
        lines.append(
            f'  Oldest open: {stats["oldest_open_days"]}d '
            f'({stats["oldest_open_section"]}).'
        )
    if stats['undated_open']:
        lines.append(
            f'  {stats["undated_open"]} open item(s) in undated sections — age unknown.'
        )
    spread = '  '.join(
        f'{b["label"]}: {b["count"]}' for b in stats['age_histogram'] if b['count']
    )
    if spread:
        lines.append(f'  Age spread — {spread}')
    if stats['open'] >= VOLUME_THRESHOLD:
        lines.append(
            f'  At or above the {VOLUME_THRESHOLD}-item volume threshold.'
        )
    return '\n'.join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        '--file', type=Path, default=DEFAULT_PATH,
        help='backlog file (default: specs/deferred_items.md, relative to CWD)',
    )
    parser.add_argument(
        '--archive', type=Path, default=DEFAULT_ARCHIVE_PATH,
        help='archive file of items that left the backlog '
             '(default: specs/completed/deferred_items.md, relative to CWD; may be absent)',
    )
    parser.add_argument(
        '--aged-days', type=int, default=DEFAULT_AGED_DAYS,
        help=f'aged-tail horizon in days (default: {DEFAULT_AGED_DAYS})',
    )
    parser.add_argument('--json', action='store_true', help='emit the raw contract as JSON')
    args = parser.parse_args(argv)

    if not args.file.is_file():
        stats = absent_stats(args.aged_days)
    else:
        text = args.file.read_text(encoding='utf-8')
        archived = []
        if args.archive.is_file():
            archived = parse_items(args.archive.read_text(encoding='utf-8'))
        stats = compute_stats(
            parse_items(text), dt.date.today(), args.aged_days, archived=archived,
        )

    print(json.dumps(stats, indent=2) if args.json else format_report(stats))
    return 0


if __name__ == '__main__':
    sys.exit(main())
