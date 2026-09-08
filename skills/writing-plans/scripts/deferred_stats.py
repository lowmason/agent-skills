#!/usr/bin/env python3
'''Report deferred-backlog health from specs/deferred_items.md.

Parses the append-only backlog into per-section items, then reports open and
ever-closed counts, closure rate, an age histogram, and the aged tail. Age comes
from each item's ``## <plan> — <YYYY-MM-DD>`` section header, which the Plan
Completion Protocol has always written, so every existing item already carries
one and no backfill is needed.

Sections whose heading carries no parseable date (for example the
``## Aged-backlog acknowledgements`` log) still contribute to the open/closed
counts but are excluded from every age figure and reported as ``undated_open``.

Usage:
    python3 ~/.claude/skills/writing-plans/scripts/deferred_stats.py
    python3 ~/.claude/skills/writing-plans/scripts/deferred_stats.py --json
    python3 ~/.claude/skills/writing-plans/scripts/deferred_stats.py \\
        --file path/to/deferred_items.md --aged-days 60

Always exits 0. This is a reporter, not a gate: the caller decides what to do
with ``aged_open``, so a large backlog never fails a script invocation.
'''

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

DEFAULT_AGED_DAYS = 45
VOLUME_THRESHOLD = 20
DEFAULT_PATH = Path('specs/deferred_items.md')

SECTION_RE = re.compile(r'^##\s+(?P<name>.+?)(?:\s+—\s+(?P<date>\d{4}-\d{2}-\d{2}))?\s*$')
ITEM_RE = re.compile(r'^- \[(?P<mark>[ xX])\]')

AGE_BUCKETS: tuple[tuple[str, int, int | None], ...] = (
    ('0-14d', 0, 14),
    ('15-30d', 15, 30),
    ('31-45d', 31, 45),
    ('46-90d', 46, 90),
    ('91d+', 91, None),
)


def parse_sections(text: str) -> list[dict]:
    '''Split the backlog into sections, counting checkbox items in each.

    Lines before the first ``##`` heading are preamble and are ignored. Only
    lines starting at column 0 with ``- [ ]`` or ``- [x]`` count as items, so
    indented continuation lines of a wrapped item are not double-counted.
    '''
    sections: list[dict] = []
    current: dict | None = None
    for line in text.splitlines():
        heading = SECTION_RE.match(line)
        if heading:
            raw_date = heading.group('date')
            current = {
                'name': heading.group('name').strip(),
                'date': dt.date.fromisoformat(raw_date) if raw_date else None,
                'open': 0,
                'closed': 0,
            }
            sections.append(current)
            continue
        item = ITEM_RE.match(line)
        if item and current is not None:
            key = 'open' if item.group('mark') == ' ' else 'closed'
            current[key] += 1
    return sections


def _bucket_label(days: int) -> str:
    for label, low, high in AGE_BUCKETS:
        if days >= low and (high is None or days <= high):
            return label
    return AGE_BUCKETS[-1][0]


def compute_stats(
    sections: list[dict],
    today: dt.date,
    aged_days: int = DEFAULT_AGED_DAYS,
) -> dict:
    '''Aggregate parsed sections into the reporting contract.

    ``closure_rate`` is closed / (open + closed) — items are never deleted from
    the backlog, so currently-closed equals ever-closed. It is ``None`` for an
    empty backlog rather than 0.0, so "nothing here yet" reads differently from
    "nothing ever closed".
    '''
    open_count = sum(s['open'] for s in sections)
    closed_count = sum(s['closed'] for s in sections)
    total = open_count + closed_count

    histogram = {label: 0 for label, _, _ in AGE_BUCKETS}
    aged_open = 0
    undated_open = 0
    oldest_days: int | None = None
    oldest_section: str | None = None

    for section in sections:
        if not section['open']:
            continue
        if section['date'] is None:
            undated_open += section['open']
            continue
        days = (today - section['date']).days
        histogram[_bucket_label(days)] += section['open']
        if days > aged_days:
            aged_open += section['open']
        if oldest_days is None or days > oldest_days:
            oldest_days = days
            oldest_section = section['name']

    return {
        'exists': True,
        'open': open_count,
        'closed': closed_count,
        'total': total,
        'closure_rate': round(closed_count / total, 4) if total else None,
        'aged_days': aged_days,
        'aged_open': aged_open,
        'undated_open': undated_open,
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
        '--aged-days', type=int, default=DEFAULT_AGED_DAYS,
        help=f'aged-tail horizon in days (default: {DEFAULT_AGED_DAYS})',
    )
    parser.add_argument('--json', action='store_true', help='emit the raw contract as JSON')
    args = parser.parse_args(argv)

    if not args.file.is_file():
        stats = absent_stats(args.aged_days)
    else:
        text = args.file.read_text(encoding='utf-8')
        stats = compute_stats(parse_sections(text), dt.date.today(), args.aged_days)

    print(json.dumps(stats, indent=2) if args.json else format_report(stats))
    return 0


if __name__ == '__main__':
    sys.exit(main())
