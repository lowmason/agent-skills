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
- An underscore with a character other than a letter or digit on either side
  is emphasis and is blanked before matching, so `_the fix is deferred_` is
  read like `the fix is deferred`, and an emphasized negation is exempt exactly
  when the same text without the underscores is. An underscore between two
  letters or digits is part of the word (`is_deferred`).
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
  marker (`-`, `*`, `+`, `N.` or `N)`), any `>` quote markers and any run of
  `*` (so `*Nothing is deferred.*` and `**Nothing is deferred.**` are exempt,
  and an emphasis `_` is already blanked). It also opens after one of `. ! ?`
  and `;`, or after one of the conjunctions `and`, `but`, `so`, `because`,
  `since`, `when` and `if`. After one of `: , ( —` only `nothing` or `none`
  opens a clause, not `no`, so `Known gap: no backoff is deferred` stays a
  candidate. Nothing else opens a clause. A bare `and`, with none of `, ; : .
  ! ? ( —` before it, does not open a clause when `else` or `other` follows
  the negation word: `the scorecard and nothing else is deferred` and `X and
  no other work is deferred` name `X` as the deferred work, so they stay
  candidates. None of the up-to-three words may be `but`, `except`, `besides`,
  `beyond`, `apart`, `aside`, `save` or `other than`, so `nothing but the
  scorecard is deferred` stays a candidate. The exemption also ends on an
  exception after the verb, read two ways. First, the text right after the
  verb, past optional whitespace (a line break included) and one optional
  comma, starts with `except`, `but`, `other than`, `apart from`, `aside from`,
  `besides`, `save` or `unless`. Second, the rest of the sentence holds `except`,
  `excepting`, `excluding`, `other than`, `apart from`, `aside from`,
  `barring`, or `with` then `the`, `one`, `a` or `an`, an optional `sole`,
  `only` or `single`, and `exception`, as whole words. The sentence ends at a
  `.`, `!` or `?`, then any closing `* _ ) ]` or quotes, then whitespace and a
  capital letter, or at the end of the unit. So a line break does not end it,
  and neither does a period inside a token (`install.py`, `v2.1`, `i.e.
  today`). So `nothing is deferred except the scorecard`, `nothing is deferred
  here except the scorecard`, `nothing is deferred (except the scorecard)`,
  `nothing is deferred in v2.1 except retry`, `nothing is deferred in this plan`
  with `except the scorecard` on the next line, and `nothing is deferred, with
  one exception: retry` stay candidates, while `nothing is deferred, with no
  exceptions` and `**Nothing is deferred.** Except for style, all is done`
  stay exempt. When in doubt the scan flags, so `with no tests is deferred`,
  `the gap that no test covers is deferred`, `such as no backoff`, a spaced
  hyphen, a line break right before the subject and a later exception word in a
  second clause (`nothing is deferred; all tests pass except the flaky one`)
  all leave a candidate. Known gaps remain, each still exempt: an `and` clause
  with one of those marks before it (`X, and nothing else is deferred`), a bare `no` after
  `;` or a full stop (`Known gap; no backoff is deferred.`, `Known gap. No
  backoff is deferred.`), an exception word after the verb that is in neither
  list, such as `beyond` or `, only`, and an exception word after an
  abbreviation that a capital follows, which reads as a sentence end (`nothing
  is deferred, e.g. Task 3, except retry`).

A phrase may wrap across lines of one unit. Each line that a match starts on is
reported once.

Usage:
    uv run <this-skill-dir>/scripts/deferral_scan.py scan <file>...
    uv run <this-skill-dir>/scripts/deferral_scan.py lint --baseline <file> [--root <dir>]

`scan` prints `<file>:<line>: <stripped line>` for each unmarked candidate and
always exits 0. It is advisory: the caller decides what each hit needs.

`lint` is a commit lint. It reads every `*.md` file under
`<root>/specs/completed/` and `<root>/specs/plans/completed/`, subfolders
included, whose path relative to `<root>` (default: the current directory) is
not a line of the baseline file. The match is exact and case-sensitive, on
POSIX paths such as `specs/completed/x.md`; blank baseline lines are ignored.
A baselined file is never opened. A directory whose name ends in `.md` is not
a file and is skipped, though the files inside it are read. A dangling
symlink, such as an Emacs lock file `.#x.md`, has no text and is skipped. Other
files are never read. `lint` prints `scan`'s lines, with paths relative to `<root>`,
then `deferral lint: <n> unmarked candidate(s) in <m> file(s); add a → item:
or → dropped: marker in each one's paragraph` and exits 1, or prints
`deferral lint: clean` and exits 0. It fails closed: a file it must read but
cannot (not valid UTF-8, no permission) gets a
`<path>: cannot read: <error>` line on stderr, then a `deferral lint: <k>
file(s) could not be read` line, and exit 1, so `clean` is never printed for
a file that was not scanned. A baseline file that cannot be read is exit 1
too.
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
# of the unit (after an optional list marker, `>` quote markers and any run of
# `*`; an emphasis `_` is already blanked to a space), after
# `. ! ? ;`, or after one of the conjunctions below. After `: , ( —` only
# `nothing` or `none` opens one, because `Known gap: no backoff is deferred` is
# an appositive that names deferred work. Anything else does not open a clause:
# a preposition or verb (`with no backoff is deferred`, `has no owner and is
# deferred`), a relative `that` or `such as` (`the gap that no test covers is
# deferred`), a spaced hyphen, or a line break. Those stay candidates. No subject
# word is an exception word, so `nothing but the scorecard is deferred` stays a
# candidate too.
NEGATED_SUBJECT = re.compile(
    r'(?:(?:^\s*(?:(?:[-*+]|\d+[.)])\s+)?(?:>\s*)*\**'
    r'|[.!?;]'
    r'|\b(?:and|but|so|because|since|when|if))'
    r'\s*\b(?:nothing|none|no)'
    r'|[:,(—]\s*\b(?:nothing|none))'
    r'(?:\s+(?!(?:but|except|besides|beyond|apart|aside|save|other\s+than)\b)[\w-]+){0,3}'
    r'\s+$',
    re.IGNORECASE,
)
# A noun joined to the negation by a bare `and` is itself the deferred work:
# `the scorecard and nothing else is deferred`, `X and no other work is deferred`.
# Only `else` or `other` right after the negation word marks this form, and only
# when none of `, ; : . ! ? ( —` comes right before the `and` and its whitespace:
# `every task landed and nothing is deferred`, `every task
# landed, and nothing else is deferred` and `all landed. And nothing else is
# deferred` join two clauses.
NOUN_AND_NOTHING_ELSE = re.compile(
    r'(?<![,;:.!?(—\s])\s+and\s+(?:nothing|none|no)\s+(?:else|other)(?:\s+[\w-]+){0,2}\s+$',
    re.IGNORECASE,
)
# An exception right after a negated PASSIVE match names the deferred work:
# `nothing is deferred except the scorecard`, `, except for`, `but the scorecard`,
# `save the scorecard`, `unless retry counts`. Its `\s*` crosses a line break, so
# `nothing is deferred` and `except the scorecard` on the next line of the unit
# are read as one. `beyond` and `only` are left out: right after the verb they
# also name a scope or a manner (`beyond this plan`, `, only reordered`).
EXCEPTION_TAIL = re.compile(
    r'\s*,?\s*(?:except|but|other\s+than|apart\s+from|aside\s+from|besides|save|unless)\b',
    re.IGNORECASE,
)
# The end of the sentence a negated PASSIVE match stands in: `.`, `!` or `?`,
# then any closing `* _ ) ]` or quotes, then whitespace and a capital letter, or
# the end of the unit. A period inside a token (`install.py`, `v2.1`, `i.e. today`)
# is not followed by whitespace and a capital, so it does not end the sentence. A
# line break does not end it either.
SENTENCE_END = re.compile(r'[.!?][*_)\]"\'”’]*(?:\s+(?=[A-Z])|\s*\Z)')
# An exception word later in the same sentence names the deferred work too:
# `nothing is deferred here except the scorecard`, `nothing is deferred (except
# the scorecard)`, `nothing is deferred in this plan` and `except the scorecard`
# on the next line, `nothing is deferred, with one exception: retry`. The letter
# lookarounds keep `exceptional` and `exceptions` out, so `with no exceptions` is
# not one. `but`, `besides` and the like are left out here, because later in a
# sentence they mostly join a second, true clause.
SENTENCE_EXCEPTION = re.compile(
    r'(?<![A-Za-z])'
    r'(?:except|excepting|excluding|other\s+than|apart\s+from|aside\s+from'
    r'|with\s+(?:the|one|a|an)\s+(?:(?:sole|only|single)\s+)?exception|barring)'
    r'(?![A-Za-z])',
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
# An underscore with a non-alphanumeric character on either side opens or closes
# emphasis (`_the fix is deferred_`); one between two letters or digits is part of
# a word (`is_deferred`). `\b` counts `_` as a word character, so emphasis
# underscores are blanked before matching.
EMPHASIS_UNDERSCORE = re.compile(r'(?<![^\W_])_|_(?![^\W_])')


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
    if EXCEPTION_TAIL.match(prose, match.end()):
        return False
    end = SENTENCE_END.search(prose, match.end())
    if SENTENCE_EXCEPTION.search(prose, match.end(), end.start() if end else len(prose)):
        return False
    # The whole unit before the match, so `^` is the unit's start.
    before = prose[:match.start()]
    if NOUN_AND_NOTHING_ELSE.search(before):
        return False
    return bool(NEGATED_SUBJECT.search(before))


def unmarked(text: str) -> list[Candidate]:
    '''Return each deferral line with no marker in its unit (1-based line numbers).'''
    lines = text.splitlines()
    candidates: list[Candidate] = []
    for unit in _units(lines, _readable_lines(lines)):
        unit_lines = [_without_exempt(lines[i]) for i in unit]
        prose = EMPHASIS_UNDERSCORE.sub(' ', _blank_code_spans('\n'.join(unit_lines)))
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


# The folders `lint` reads, relative to its root: where documents retire.
COMPLETED_FOLDERS = ('specs/completed', 'specs/plans/completed')


def _completed_markdown(root: Path) -> list[str]:
    '''Return the root-relative POSIX path of each `.md` file under the completed folders.'''
    found = []
    for folder in COMPLETED_FOLDERS:
        base = root / folder
        if not base.is_dir():
            continue
        for path in base.rglob('*'):
            dangling = path.is_symlink() and not path.exists()
            if path.suffix == '.md' and not path.is_dir() and not dangling:
                found.append(path.relative_to(root).as_posix())
    return sorted(found)


def _lint(baseline: str, root: str) -> int:
    try:
        listed = Path(baseline).read_text(encoding='utf-8').splitlines()
    except (OSError, UnicodeDecodeError) as error:
        print(f'deferral lint: cannot read baseline {baseline}: {error}', file=sys.stderr)
        return 1
    frozen = {line for line in listed if line}
    root_path = Path(root)
    hits, files_hit, unreadable = 0, 0, 0
    for rel in _completed_markdown(root_path):
        if rel in frozen:
            continue
        try:
            text = (root_path / rel).read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError) as error:
            print(f'{rel}: cannot read: {error}', file=sys.stderr)
            unreadable += 1
            continue
        candidates = unmarked(text)
        for candidate in candidates:
            print(f'{rel}:{candidate.line}: {candidate.text}')
        hits += len(candidates)
        files_hit += bool(candidates)
    if hits:
        print(f'deferral lint: {hits} unmarked candidate(s) in {files_hit} file(s); '
              "add a → item: or → dropped: marker in each one's paragraph")
    if unreadable:
        print(f'deferral lint: {unreadable} file(s) could not be read')
    if hits or unreadable:
        return 1
    print('deferral lint: clean')
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest='command', required=True)
    scan = commands.add_parser('scan', help='list unmarked deferral lines; always exits 0')
    scan.add_argument('files', nargs='+', metavar='file')
    lint = commands.add_parser(
        'lint', help='fail on unmarked deferral lines in completed documents off the baseline')
    lint.add_argument('--baseline', required=True, metavar='file',
                      help='repo-relative paths, one per line, that the lint skips')
    lint.add_argument('--root', default='.', metavar='dir',
                      help='the tree to read (default: the current directory)')
    args = parser.parse_args(argv)
    if args.command == 'lint':
        return _lint(args.baseline, args.root)
    return _scan(args.files)


if __name__ == '__main__':
    sys.exit(main())
