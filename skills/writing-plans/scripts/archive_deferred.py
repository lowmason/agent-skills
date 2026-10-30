#!/usr/bin/env python3
# /// script
# requires-python = '>=3.11'
# dependencies = []
# ///
'''Move old ticked items from specs/deferred_items.md to its archive file.

An item leaves the live backlog only by a move to the archive file
`specs/completed/deferred_items.md` (spec section 5, D4, D8, D11). A ticked item
moves when its tick is more than 45 days old. A ticked item with a `→ removed`
note moves at any age.

- The tick date is the latest date on the item's `→ done`, `→ retired` or
  `→ removed` notes. When none of those notes has a date, or the item has none of
  them, the tick date is the section date. A ticked item with no tick date (an
  undated section and undated notes) stays.
- An item is the same span `deferred_stats.parse_items` reads: its column-0
  checkbox line and every indented line after it, across blank lines, up to the
  next item, heading or column-0 line. Its lines move byte for byte.
- A moved item goes to the end of its section in the archive, matched by the
  whole heading line. A heading the archive lacks is created in date order, and
  undated headings sort last. A heading may stand in both files while its section
  drains.
- When a section's last item leaves, the whole section leaves the live file: its
  heading, its preamble and any prose between its items. That prose goes to the
  archive with the items, in its original order, so nothing is lost. A section
  that never held an item, such as the acknowledgement log, never drains.
- The hold-back (spec D7): each `→ done`, `→ retired` or `→ removed` note runs
  from its arrow to the next such note or the item's end. The deferral scan reads
  each of those notes dated on or after `SCAN_FROM`. An item with an unmarked
  candidate in one of them stays live and is reported. Undated notes and notes
  dated before `SCAN_FROM` are history: the scan never reads them, so an old
  item is never held back or rewritten for its history.

When nothing moves, both texts come back unchanged. When something moves, both
files are re-spaced: one blank line between sections, one final newline.

Usage:
    uv run <this-skill-dir>/scripts/archive_deferred.py --dry-run
    uv run <this-skill-dir>/scripts/archive_deferred.py \\
        --file path/to/deferred_items.md --archive path/to/archive.md

Prints `archived <n> item(s), held back <k>:` and then one line per held item.
Always exits 0; a failure prints a message that names the file on stderr. A
missing backlog file means nothing to archive. A missing archive file starts as
the `# Deferred items` title line. Both files are written through temporary
files and renames, archive first. When the second rename fails, the archive is
put back, so both files change or neither does, and the count line prints only
after both are in place. Each file keeps its mode; a new archive gets the mode
a plain `open` would give it.
'''

from __future__ import annotations

import argparse
import datetime as dt
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from deferral_scan import unmarked
from deferred_stats import (
    DEFAULT_AGED_DAYS,
    DEFAULT_ARCHIVE_PATH,
    DEFAULT_PATH,
    ITEM_RE,
    SECTION_RE,
    Item,
    Note,
    _find_notes,
    _mask_code,
    _parse_date,
    first_words,
    parse_items,
)

# The day this script landed. Closure notes dated before it are history and are
# never held back (spec section 5).
SCAN_FROM = dt.date(2026, 10, 30)
CLOSURE_KINDS = frozenset({'done', 'retired', 'removed'})
ARCHIVE_TITLE = '# Deferred items\n'


@dataclass
class Segment:
    '''A run of raw lines in a section body: one item, or prose and blank lines.'''

    lines: list[str]
    item: Item | None = None


@dataclass
class Section:
    heading: str
    segments: list[Segment] = field(default_factory=list)

    @property
    def key(self) -> str:
        return _content(self.heading).rstrip()

    @property
    def sort_key(self) -> tuple[int, dt.date]:
        match = SECTION_RE.match(_content(self.heading))
        date = _parse_date(match.group('date')) if match else None
        return (1, dt.date.max) if date is None else (0, date)

    def lines(self) -> list[str]:
        return [line for segment in self.segments for line in segment.lines]


def _content(line: str) -> str:
    '''The line without its line break.'''
    parts = line.splitlines()
    return parts[0] if parts else ''


def _blank(line: str) -> bool:
    return not line.strip()


def _segments(heading: str, body: list[str]) -> list[Segment]:
    '''Split a section body by `parse_items`' rules, keeping every raw line.

    A blank line does not end an item: it is held until the next non-blank line
    shows whether the item goes on (an indented line) or has ended.
    '''
    segments: list[Segment] = []
    item_lines: list[str] = []
    prose: list[str] = []
    pending: list[str] = []

    def close_item() -> None:
        if item_lines:
            parsed = parse_items(heading + ''.join(item_lines))
            if len(parsed) != 1:
                raise ValueError(f'item span disagrees with parse_items: {item_lines[0]!r}')
            segments.append(Segment(list(item_lines), parsed[0]))
            item_lines.clear()

    def close_prose() -> None:
        if prose:
            segments.append(Segment(list(prose)))
            prose.clear()

    for line in body:
        text = _content(line)
        if ITEM_RE.match(text):
            close_item()
            prose.extend(pending)
            pending.clear()
            close_prose()
            item_lines.append(line)
        elif not item_lines:
            prose.append(line)
        elif _blank(text):
            pending.append(line)
        elif text[0].isspace():
            item_lines.extend(pending)
            pending.clear()
            item_lines.append(line)
        else:
            close_item()
            prose.extend(pending)
            pending.clear()
            prose.append(line)
    close_item()
    prose.extend(pending)
    close_prose()
    return segments


def _parse(text: str) -> tuple[list[str], list[Section]]:
    '''The lines before the first heading, then each section with its segments.'''
    head: list[str] = []
    raw: list[tuple[str, list[str]]] = []
    for line in text.splitlines(keepends=True):
        if SECTION_RE.match(_content(line)):
            raw.append((line if line.endswith(('\n', '\r')) else line + '\n', []))
        elif raw:
            raw[-1][1].append(line)
        else:
            head.append(line)
    return head, [Section(heading, _segments(heading, body)) for heading, body in raw]


def _ended(line: str) -> str:
    return line if _content(line) != line else line + '\n'


def _strip_blank_edges(lines: list[str], leading: bool = False) -> list[str]:
    end = len(lines)
    while end and _blank(lines[end - 1]):
        end -= 1
    start = 0
    while leading and start < end and _blank(lines[start]):
        start += 1
    return lines[start:end]


def _render(head: list[str], sections: list[Section]) -> str:
    '''Join the parts with one blank line between sections and a final newline.'''
    blocks = []
    if _strip_blank_edges(head):
        blocks.append(_strip_blank_edges(head))
    for section in sections:
        blocks.append([section.heading] + _strip_blank_edges(section.lines()))
    out: list[str] = []
    for block in blocks:
        if out:
            out.append('\n')
        out.extend(_ended(line) for line in block)
    return ''.join(out)


def _closure_notes(item: Item) -> list[tuple[int, Note]]:
    '''Each `done`, `retired` or `removed` note with its offset in `item.text`.'''
    return [(start, note) for start, _, note in _find_notes(item.text, _mask_code(item.text))
            if note.kind in CLOSURE_KINDS]


def _closure_date(item: Item) -> dt.date | None:
    '''The latest date on the item's closure notes, or None when none is dated.'''
    dates = [note.date for _, note in _closure_notes(item) if note.date is not None]
    return max(dates) if dates else None


def _new_closure_texts(item: Item, scan_from: dt.date) -> list[str]:
    '''The closure notes dated on or after `scan_from`, each up to the next one.

    A closure note runs from its arrow to the next closure note or the item's end.
    An undated note and a note dated before `scan_from` are history and are left
    out, wherever they stand.
    '''
    notes = _closure_notes(item)
    ends = [start for start, _ in notes[1:]] + [len(item.text)]
    return [item.text[start:end] for (start, note), end in zip(notes, ends)
            if note.date is not None and note.date >= scan_from]


def _eligible(item: Item, today: dt.date, days: int) -> bool:
    if not item.checked:
        return False
    if any(note.kind == 'removed' for note in item.notes):
        return True
    tick = _closure_date(item) or item.section_date
    return tick is not None and (today - tick).days > days


def _held_line(item: Item, scan_from: dt.date) -> str | None:
    '''The report line when a new closure note holds an unmarked candidate.'''
    for text in _new_closure_texts(item, scan_from):
        candidates = unmarked(text)
        if candidates:
            return f'  held back: {item.section}: {first_words(item)}…: {candidates[0].text}'
    return None


def _drop_item(segments: list[Segment], index: int) -> None:
    '''Remove one item segment without leaving a doubled or leading blank line.'''
    del segments[index]
    before_blank = index == 0 or _blank(segments[index - 1].lines[-1])
    if before_blank and index < len(segments):
        following = segments[index]
        if following.item is None and following.lines and _blank(following.lines[0]):
            del following.lines[0]
            if not following.lines:
                del segments[index]


def _archive_section(sections: list[Section], source: Section) -> Section:
    '''The archive section for `source`'s heading, created in date order if absent.'''
    for section in reversed(sections):
        if section.key == source.key:
            return section
    created = Section(source.heading)
    position = next((i for i, section in enumerate(sections)
                     if section.sort_key > source.sort_key), len(sections))
    sections.insert(position, created)
    return created


def _append(target: Section, lines: list[str]) -> None:
    existing = _strip_blank_edges(target.lines())
    added = _strip_blank_edges(lines, leading=bool(existing))
    target.segments = [Segment(existing + [_ended(line) for line in added])]


def archive(
    live: str,
    archived: str,
    today: dt.date,
    scan_from: dt.date = SCAN_FROM,
    days: int = DEFAULT_AGED_DAYS,
) -> tuple[str, str, list[str]]:
    '''Move eligible ticked items; return the new live text, archive text and held lines.'''
    live_head, live_sections = _parse(live)
    archive_head, archive_sections = _parse(archived)
    held: list[str] = []
    moved = 0
    kept: list[Section] = []
    for section in live_sections:
        had_items = any(segment.item for segment in section.segments)
        original = section.lines()
        leaving: list[Segment] = []
        index = 0
        while index < len(section.segments):
            item = section.segments[index].item
            if item is None or not _eligible(item, today, days):
                index += 1
                continue
            report = _held_line(item, scan_from)
            if report:
                held.append(report)
                index += 1
                continue
            leaving.append(section.segments[index])
            _drop_item(section.segments, index)
        moved += len(leaving)
        drained = had_items and not any(segment.item for segment in section.segments)
        if drained:
            _append(_archive_section(archive_sections, section), original)
            continue
        kept.append(section)
        for segment in leaving:
            _append(_archive_section(archive_sections, section), segment.lines)
    if not moved:
        return live, archived, held
    return _render(live_head, kept), _render(archive_head, archive_sections), held


def _default_mode() -> int:
    '''The mode a plain `open(path, 'w')` gives a new file under the current umask.'''
    mask = os.umask(0)
    os.umask(mask)
    return 0o666 & ~mask


def _stage(path: Path, data: bytes) -> str:
    '''Write `data` to a temporary file beside `path`, with the mode `path` has or would get.'''
    handle, temp = tempfile.mkstemp(dir=path.parent, prefix=f'.{path.name}.', suffix='.tmp')
    try:
        with os.fdopen(handle, 'wb') as out:
            out.write(data)
        if path.exists():
            shutil.copymode(path, temp)
        else:
            os.chmod(temp, _default_mode())
    except BaseException:
        Path(temp).unlink(missing_ok=True)
        raise
    return temp


def _replace(temp: str, path: Path) -> None:
    try:
        os.replace(temp, path)
    except BaseException:
        Path(temp).unlink(missing_ok=True)
        raise


def _write_both(live_path: Path, live: str, archive_path: Path, archived: str) -> str | None:
    '''Replace the archive, then the live file, or neither; return a failure message.

    Both temporary files are written before either rename. When the live rename
    fails after the archive's, the archive gets its old bytes back, or is removed
    when it did not exist before, so a re-run never moves an item twice.
    '''
    made_folder = not archive_path.parent.exists()
    failing, staged = archive_path, []
    try:
        before = archive_path.read_bytes() if archive_path.exists() else None
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        staged.append(_stage(archive_path, archived.encode('utf-8')))
        failing = live_path
        staged.append(_stage(live_path, live.encode('utf-8')))
        failing = archive_path
        _replace(staged.pop(0), archive_path)
    except OSError as error:
        for temp in staged:
            Path(temp).unlink(missing_ok=True)
        if made_folder:
            _remove_folder(archive_path.parent)
        return f'{failing}: cannot write: {error}; both files are unchanged'
    try:
        _replace(staged.pop(0), live_path)
        return None
    except OSError as error:
        failure = f'{live_path}: cannot write: {error}'
    try:
        if before is None:
            archive_path.unlink()
            if made_folder:
                _remove_folder(archive_path.parent)
        else:
            _replace(_stage(archive_path, before), archive_path)
    except OSError as error:
        return (f'{failure}; the archive could not be restored ({error}): '
                f'{archive_path} is changed and holds the moved items, '
                f'{live_path} is unchanged')
    return f'{failure}; both files are unchanged'


def _remove_folder(folder: Path) -> None:
    try:
        folder.rmdir()
    except OSError:
        pass


def main(argv: list[str] | None = None, today: dt.date | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        '--file', type=Path, default=DEFAULT_PATH,
        help='backlog file (default: specs/deferred_items.md, relative to CWD)',
    )
    parser.add_argument(
        '--archive', type=Path, default=DEFAULT_ARCHIVE_PATH,
        help='archive file (default: specs/completed/deferred_items.md, relative to CWD; '
             'created when absent)',
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='print what would move and write nothing')
    args = parser.parse_args(argv)

    try:
        live = args.file.read_text(encoding='utf-8')
    except FileNotFoundError:
        print(f'{args.file}: not found, nothing to archive', file=sys.stderr)
        print('archived 0 item(s), held back 0:')
        return 0
    except (OSError, UnicodeDecodeError) as error:
        print(f'{args.file}: cannot read: {error}; nothing archived', file=sys.stderr)
        return 0
    try:
        archived = (args.archive.read_text(encoding='utf-8')
                    if args.archive.exists() else ARCHIVE_TITLE)
    except (OSError, UnicodeDecodeError) as error:
        print(f'{args.archive}: cannot read: {error}; nothing archived', file=sys.stderr)
        return 0

    try:
        new_live, new_archive, held = archive(live, archived, today or dt.date.today())
    except ValueError as error:
        print(f'nothing archived: {error}', file=sys.stderr)
        return 0
    if not args.dry_run and new_live != live:
        failure = _write_both(args.file, new_live, args.archive, new_archive)
        if failure:
            print(failure, file=sys.stderr)
            return 0
    moved = len(parse_items(live)) - len(parse_items(new_live))
    print(f'archived {moved} item(s), held back {len(held)}:')
    for line in held:
        print(line)
    return 0


if __name__ == '__main__':
    sys.exit(main())
