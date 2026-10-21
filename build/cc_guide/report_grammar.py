'''The verifier report's grammar, which settle.py reads (drift spec R8.4-R8.8):
the report formats, and how a report's lines split into rows.

A row's fields are split on `|`. A quote field that opens with `"` runs to
the first `"` followed by `|` or the end of the line, so a quote may hold `|`
and `"`; the last field takes the rest of the line. In verify, audit and
files, a row's second field, its claim, may hold `|` too: when the fields
after it do not fit, it runs to the first `|` after which they do (a verdict
and a doc reference, or a cited section, a quote and a verdict), and with no
such `|` the plain split stands. A files row may give a range of lines,
`file:first-last`. `-` marks an empty field. A `<section> | none` line says
`none` and nothing else, since prose is never read as none. A leading list
marker and a Markdown table's outer pipes are no part of a row, and a line
without `|` is prose, never a row. report_lines drops these lines too, so
settle never lists them and they never move its exit to 1:
- separator rows: a line of only `|`, `-`, `:` and spaces;
- header rows, in any letter case: a line whose first field is a header
  word (HEADERS), or whose every field is a column name (COLUMNS). The
  second takes in a table's own header row and an echoed template, among
  them a C row whose only text is one column name (`C | statement`) and a
  B row shaped like the template
  (`B | version | one line | changelog.md:line`).
'''
import re
from collections.abc import Callable

from docs import CHANGELOG

# The report formats, as the verifier's contract (.claude/agents/cc-guide-verifier.md)
# and the skill's references/formats.md state them; a test pins all three together.
TRIAGE_ROW = 'item | TOUCHES / NOISE / UNSURE | section | guide line | "guide quote" | "source quote" | why'
COVERAGE_ROW = 'release | sections touched, or none'
VERIFY_ROW = ('L<line> | claim ≤12 words | CONFIRMED / STALE / WRONG / PARTIAL / NOT FOUND / JUDGMENT | doc:line'
              ' | "verbatim quote ≤25 words" | proposed wording')
CHANGELOG_ROW = 'B | version | one line | changelog.md:line'
OMISSION_ROW = 'C | omission'
FILES_ROW = 'file:line | statement | section | "verbatim guide quote" | consistent / contradicts / not covered'
NONE_ROW = 'section | none'
FORMATS = (TRIAGE_ROW, COVERAGE_ROW, VERIFY_ROW, CHANGELOG_ROW, OMISSION_ROW, FILES_ROW, NONE_ROW)
# Each row's quote fields, by index: only these may hold `|` and `"`.
TRIAGE_QUOTES = (4, 5)
VERIFY_QUOTES = (4,)
FILES_QUOTES = (3,)

LIST_ITEM_RE = re.compile(r'[ \t]*(?:[-*+]|\d+[.)])[ \t]')
CLOSE_QUOTE_RE = re.compile(r'"[ \t]*(?:\||$)')
SEPARATOR_RE = re.compile(r'^[\s|:-]+$')
LINE_REF_RE = re.compile(r'L(\d+)')
DOC_REF_RE = re.compile(r'(.+):(\d+)')
# A files row's `file:line`, or a range of lines, `file:first-last`.
FILE_REF_RE = re.compile(r'(.+):(\d+)(?:-\d+)?')
CHANGELOG_REF_RE = re.compile(re.escape(CHANGELOG) + r':[1-9][0-9]*')
HEADERS = ('item', 'release', 'l<line>', 'file:line', 'file line', 'section')
# Column names: the report formats' own, less `none`, and a table header's usual ones. A line whose every field
# is one is a header, as an echoed B or C template and a table's own header row are; no row is such a line.
COLUMNS = frozenset(f.strip().strip('"').lower() for form in FORMATS for f in form.split('|')) - {'none'} | {
    'line', 'claim', 'verdict', 'doc', 'quote', 'wording', 'file'}


def split_row(line: str, count: int, quoted: tuple[int, ...] = (),
              fits: Callable[[list[str]], bool] | None = None) -> list[str] | None:
    '''A report row's first `count` fields, or None when it has fewer. A
    field at a `quoted` index that opens with `"` runs to the first `"`
    followed by `|` or the end of the line; any other field ends at the next
    `|`. The last field takes the rest of the line. With `fits`, the second
    field, a claim, may hold `|` too: when the fields after the claim do not
    fit, the claim runs to the first `|` after which they do, and with none
    the plain split stands. A claim without `|` thus splits as before.'''
    s = line.strip()
    s = s[1:] if s.startswith('|') else s
    s = s[:-1] if s.endswith('|') else s
    row = fields(s, count, quoted)
    if fits is None or (row is not None and fits(row[2:])):
        return row
    first = s.find('|')
    end = s.find('|', first + 1) if first >= 0 else -1
    while end >= 0:
        rest = fields(s[end + 1:], count - 2, tuple(q - 2 for q in quoted))
        if rest is not None and fits(rest):
            return [s[:first].strip(), s[first + 1:end].strip(), *rest]
        end = s.find('|', end + 1)
    return row


def fields(s: str, count: int, quoted: tuple[int, ...]) -> list[str] | None:
    '''split_row's split of a row whose outer pipes are already dropped.'''
    out: list[str] = []
    i = 0
    while len(out) < count - 1:
        while i < len(s) and s[i] in ' \t':
            i += 1
        if len(out) in quoted and s.startswith('"', i):
            m = CLOSE_QUOTE_RE.search(s, i + 1)
            if m is None:
                return None
            out.append(s[i:m.start() + 1])
            i = m.end()
        else:
            j = s.find('|', i)
            if j < 0:
                return None
            out.append(s[i:j].strip())
            i = j + 1
    out.append(s[i:].strip())
    return out


def unquote(field: str) -> str:
    '''A quote field's text: its outer double quotes dropped; `-` or nothing
    is no quote.'''
    if len(field) >= 2 and field[0] == field[-1] == '"':
        return field[1:-1]
    return '' if field in ('', '-') else field


def given(field: str) -> str:
    '''A field's text, or '' when it is empty or `-`, the empty-field mark.'''
    return '' if field.strip() in ('', '-') else field.strip()


def report_lines(text: str) -> list[str]:
    '''The report's lines that may be rows: those holding `|`, each less a
    leading list marker, less table separators and header rows.'''
    out = []
    for raw in text.split('\n'):
        marker = LIST_ITEM_RE.match(raw)
        line = raw[marker.end():] if marker else raw
        if '|' not in line or SEPARATOR_RE.match(line):
            continue
        first = (split_row(line, 2) or [''])[0].lower()
        if first not in HEADERS and not header_row(line):
            out.append(line.strip())
    return out


def header_row(line: str) -> bool:
    '''Whether every field of a line, its outer pipes dropped, is a column
    name.'''
    s = line.strip()
    s = s[1:] if s.startswith('|') else s
    s = s[:-1] if s.endswith('|') else s
    return all(f.strip().strip('"').lower() in COLUMNS for f in s.split('|'))


def none_line(line: str) -> bool:
    '''Whether a `<section> | none` line says none.'''
    return split_row(line, 2)[1].strip().lower() == 'none'
