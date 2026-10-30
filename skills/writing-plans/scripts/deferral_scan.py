#!/usr/bin/env python3
# /// script
# requires-python = '>=3.11'
# dependencies = []
# ///
'''Find deferral sentences in a Markdown file that no marker resolves.

A plan or spec that says some work is put off has to say where that work went,
or the work is lost when the document retires. This script reads a Markdown
file, finds each line that holds a deferral phrase (the `PHRASES` constant), and
reports the ones whose unit carries no marker. The two markers are
`→ item: <section heading>` (a backlog item exists for the work) and
`→ dropped: <why>` (the work will not be done).

A unit is a run of non-blank lines. A line that starts a list item (`-`, `*` or
`N.` after any indent, then a space) also starts a new unit, and a heading is a
unit of its own. A marker answers only the candidates in its own unit.

The scan reads prose only:

- Fenced code blocks are skipped. A fence opens on three or more backticks or
  tildes after any indent, and closes only on a run of the same character at
  least as long as the opener, with nothing after it. A shorter run inside a
  longer fence is content. An unclosed fence runs to the end of the file. Fence
  lines are not blank, so a fence does not end the unit around it; its lines are
  simply not read.
- Inline code spans are blanked before matching. A run of N backticks closes
  only on a run of exactly N, and a span may wrap a line. So a note form or a
  quoted phrase in backticks neither flags nor marks anything.
- Two forms of the Plan Completion Protocol are exempt. Its status header
  (`deferred items in specs/deferred_items.md` or `nothing deferred`) is exempt
  as a whole line. Its `> Skipped: <why> → deferred` note, which the protocol
  always files as an item, is exempt from the line start through the first
  `→ deferred`, plus an optional parenthetical, final period and closing bold
  marker (`> **Skipped: … → deferred (reason).**`). Any text after that is read,
  so a second deferral on the same line is still found.
- A passive deferral whose subject is a negation is a statement that nothing
  was put off, so it is not a candidate. The subject is `nothing`, `none` or
  `no` and up to three more words, right before the verb, and it must open its
  clause. A clause opens at the start of the unit, after an optional list
  marker (`-`, `*`, `+`, `N.` or `N)`), any `>` quote markers and an optional
  `**`. It also opens after one of `. ! ? ; : , ( —`, or after one of the
  conjunctions `and`, `but`, `so`, `because`, `since`, `when` and `if`. Nothing
  else opens a clause. When in doubt the scan flags, so `with no tests is
  deferred`, `the gap that no test covers is deferred`, `such as no backoff`, a
  spaced hyphen and a line break inside a sentence all leave a candidate.

A phrase may wrap across lines of one unit. Each line that a match starts on is
reported once.

Usage:
    uv run <this-skill-dir>/scripts/deferral_scan.py scan <file>...

`scan` prints `<file>:<line>: <stripped line>` for each unmarked candidate and
always exits 0. It is advisory: the caller decides what each hit needs.
'''
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# A passive deferral: `the T6 gap is deferred`; not `is deferred items`. Named,
# because a negated subject before it (NEGATED_SUBJECT) cancels the match.
PASSIVE = re.compile(
    r'\b(?:is|are|was|were|be|been|stays?|remains?)\s+deferred\b(?![\s-]*items?\b)',
    re.IGNORECASE,
)
# `nothing else is deferred`, `none of this is deferred`, `, and no new work is
# deferred`: a subject of `nothing`, `none` or `no` and up to three more words,
# right before PASSIVE's verb, that opens its clause. A clause opens at the start
# of the unit (after an optional list marker, `>` quote markers and `**`), after
# `. ! ? ; : , ( —`, or after one of the conjunctions below. Anything else does
# not open one: a preposition or verb (`with no backoff is deferred`, `has no
# owner and is deferred`), a relative `that` or `such as` (`the gap that no test
# covers is deferred`), a spaced hyphen, or a line break. Those stay candidates.
NEGATED_SUBJECT = re.compile(
    r'(?:^\s*(?:(?:[-*+]|\d+[.)])\s+)?(?:>\s*)*(?:\*\*)?'
    r'|[.!?;:,(—]'
    r'|\b(?:and|but|so|because|since|when|if))'
    r'\s*\b(?:nothing|none|no)(?:\s+[\w-]+){0,3}\s+$',
    re.IGNORECASE,
)

# Deferral phrases, matched case-insensitively. `\s+` between words lets a phrase
# wrap across lines. Bare `defer` and `deferred` are left out on purpose: in plans
# and specs most of their hits name the backlog file, an existing item or the
# `/deferred` command, not new work being put off.
PHRASES = (
    # work handed to a later moment: `deferred to a future plan`, `deferred until v2`
    re.compile(r'\bdeferred\s+(?:to|until)\b', re.IGNORECASE),
    PASSIVE,
) + tuple(re.compile(pattern, re.IGNORECASE) for pattern in (
    # work named for a later unit of work: `worth a future item`, `a follow-up plan`
    r'\b(?:future|follow-?up)\s+(?:item|plan|task|pass|pr)\b',
    # a hazard named but not filed: `a separate, unrecorded item`
    r'\bunrecorded\s+item\b',
    # a gap left open on purpose: `Standing gap, not closed`
    r'\bstanding\s+gap\b',
    # an arrow note outside the exempt Skipped line: `H2 → deferred`; not a flow
    # step that names the backlog, as in `gate → deferred items → retire`
    r'→\s*deferred\b(?![\s-]*items?\b)',
    # a candidate named but not filed: `deferred-item candidate`
    r'\bdeferred[\s-]+item\s+candidate\b',
    # work parked for later: `left for later`, `left for a follow-up`
    r'\bleft\s+for\s+(?:a\s+)?(?:later|future|follow-?up)\b',
))

MARKER = re.compile(r'→\s*(?:item|dropped):')
STATUS_HEADER = re.compile(
    r'^\*\*Status: COMPLETE \([^)]*\)\*\* — .*'
    r'(?:deferred items in specs/deferred_items\.md|nothing deferred)\s*$'
)
# The exempt part of a Skipped note; the rest of its line is read as prose.
SKIPPED_NOTE = re.compile(
    r'^\s*>\s*(?:\*\*)?Skipped:.*?→\s*deferred\b(?:\s*\([^)]*\))?\.?(?:\*\*)?'
)
FENCE_OPEN = re.compile(r'^\s*(`{3,}|~{3,})(.*)$')
LIST_ITEM = re.compile(r'^\s*(?:[-*]|\d+\.)\s')
HEADING = re.compile(r'^\s{0,3}#{1,6}(?:\s|$)')
BACKTICK_RUN = re.compile(r'`+')


@dataclass
class Candidate:
    line: int
    text: str


def _readable_lines(lines: list[str]) -> list[bool]:
    '''Mark each line True when it is outside every fenced code block.'''
    readable = []
    fence_char, fence_len = '', 0
    for line in lines:
        if fence_char:
            stripped = line.strip()
            closes = (len(stripped) >= fence_len
                      and stripped == fence_char * len(stripped))
            if closes:
                fence_char, fence_len = '', 0
            readable.append(False)
            continue
        opener = FENCE_OPEN.match(line)
        if opener and not (opener.group(1)[0] == '`' and '`' in opener.group(2)):
            fence_char, fence_len = opener.group(1)[0], len(opener.group(1))
            readable.append(False)
            continue
        readable.append(True)
    return readable


def _units(lines: list[str], readable: list[bool]) -> list[list[int]]:
    '''Group the readable line indexes into scan units.'''
    units: list[list[int]] = []
    current: list[int] = []
    for index, line in enumerate(lines):
        if not readable[index]:
            continue
        if not line.strip():
            if current:
                units.append(current)
            current = []
            continue
        if HEADING.match(line):
            if current:
                units.append(current)
            units.append([index])
            current = []
            continue
        if LIST_ITEM.match(line) and current:
            units.append(current)
            current = []
        current.append(index)
    if current:
        units.append(current)
    return units


def _blank_code_spans(text: str) -> str:
    '''Replace each inline code span with spaces, keeping offsets and newlines.'''
    chars = list(text)
    runs = list(BACKTICK_RUN.finditer(text))
    used: set[int] = set()
    for i, opener in enumerate(runs):
        if i in used:
            continue
        width = len(opener.group())
        for j in range(i + 1, len(runs)):
            if len(runs[j].group()) == width:
                for k in range(opener.start(), runs[j].end()):
                    if chars[k] != '\n':
                        chars[k] = ' '
                used.update(range(i, j + 1))
                break
    return ''.join(chars)


def _without_exempt(line: str) -> str:
    '''Blank the protocol's exempt text in a line, keeping its length.'''
    if STATUS_HEADER.match(line.strip()):
        return ' ' * len(line)
    note = SKIPPED_NOTE.match(line)
    if note:
        return ' ' * note.end() + line[note.end():]
    return line


def _negated(prose: str, match: re.Match[str]) -> bool:
    # The whole unit before the match, so `^` is the unit's start.
    return bool(NEGATED_SUBJECT.search(prose[:match.start()]))


def unmarked(text: str) -> list[Candidate]:
    '''Return each deferral line with no marker in its unit (1-based line numbers).'''
    lines = text.splitlines()
    candidates: list[Candidate] = []
    for unit in _units(lines, _readable_lines(lines)):
        unit_lines = [_without_exempt(lines[i]) for i in unit]
        prose = _blank_code_spans('\n'.join(unit_lines))
        if MARKER.search(prose):
            continue
        starts = [0]
        for unit_line in unit_lines[:-1]:
            starts.append(starts[-1] + len(unit_line) + 1)
        hit_rows: set[int] = set()
        for phrase in PHRASES:
            for match in phrase.finditer(prose):
                if phrase is PASSIVE and _negated(prose, match):
                    continue
                row =max(r for r, start in enumerate(starts) if start <= match.start())
                hit_rows.add(row)
        for row in sorted(hit_rows):
            index = unit[row]
            candidates.append(Candidate(index + 1, lines[index].strip()))
    return candidates


def _scan(paths: list[str]) -> int:
    for path in paths:
        try:
            text = Path(path).read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError) as error:
            print(f'{path}: cannot read: {error}', file=sys.stderr)
            continue
        for candidate in unmarked(text):
            print(f'{path}:{candidate.line}: {candidate.text}')
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest='command', required=True)
    scan = commands.add_parser('scan', help='list unmarked deferral lines; always exits 0')
    scan.add_argument('files', nargs='+', metavar='file')
    args = parser.parse_args(argv)
    return _scan(args.files)


if __name__ == '__main__':
    sys.exit(main())
