'''`settle`: the deterministic half of a /cc-guide run (drift spec R8.4
steps 4-6, R8.8 steps 1-4, R8.10). It reads a packet's index.json beside
the verifier's report.md, parses the report's rows, re-greps every quote
(quotes.py), and prints what follows. It writes nothing but a settled
triage's settled.json in the packet; `baseline` records the outcome. Each
rebaseline it prints ends with --head and the packet's head, so `baseline`
refuses it once a later fetch has moved latest/.

- triage fails safe: a block the report leaves out, a release with no
  coverage line and a row whose quote fails all become UNSURE, handled as
  TOUCHES, and a block row's failed quote takes every candidate of its
  block with it. A source quote counts only within its own item's text. A
  line that does not parse still flags each section it names and each
  candidate of a block it names, and sends a bullet it names to its hints;
  one whose first field names a release, however it marks the label up, is
  a coverage line and leaves each release it names uncovered, and a row
  that does not parse and names no section, block or bullet sends every
  section in the packet. It names the sections for verify, and
  prints the rebaseline and advance commands for the rest; a group's
  blocks wait while a section a row for one of them flagged, in any group,
  is flagged. An owner item stops the advance below its release.
- verify, audit and files discard a row whose quote fails, a quote a row
  need not give included, and list it as unverified. Surviving corrections
  are listed to apply; JUDGMENT, NOT FOUND, omissions and not-covered rows
  are the owner's call. Each section in scope, or each cited section in
  files, needs a surviving row or a `<section> | none` line. A section is
  held, neither advanced nor audited, when it is left out, when a discarded
  row would have changed it, when a correction to it is left for the owner,
  when its triage held it, or when `--hold` names it; a file is held, not
  cited, the same way, and when the file in the checkout settle runs from
  no longer matches the packet's copy, which the verifier read, apart from
  its citation's stamp, the one thing `baseline cite` rewrites: a changed
  list of cited sections holds it too. So settle a files report before
  fixing a contradiction it lists, and run the cite it printed then: a
  settle after the fix holds the file. A row outside the packet's sections
  holds nothing: the run neither reviews nor advances that section, and its
  triage may have advanced it already. A row whose guide line is in no
  section, past the guide's last line included, holds every section in the
  packet. A hold keeps `accept`, for the text the run changed.

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
without `|` is prose, never a row. Settle drops these lines without listing
them, so they never move the exit to 1:
- separator rows: a line of only `|`, `-`, `:` and spaces;
- header rows, in any letter case: a line whose first field is a header
  word (HEADERS), or whose every field is a column name (COLUMNS). The
  second takes in a table's own header row and an echoed template, among
  them a C row whose only text is one column name (`C | statement`) and a
  B row shaped like the template
  (`B | version | one line | changelog.md:line`);
- in verify and audit, a well-formed `<section> | none` line for a section
  outside the packet.
Any other line holding `|` that is no row is listed as unparseable.
'''
import json
import re
import shlex
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import NamedTuple

from blocks import fenced_lines
from docs import CHANGELOG, LABEL_RE, version_key
from guide import CITE_SHAPED_RE, STAMP_PATTERN, sections
from lint import CLI
from packets import BLOCKS, GUIDE, INDEX, REPORT, SETTLED, section_lines
from quotes import QuoteFiles
from state import SetupError, Source, default_cache, read_utf8

# The checkout this file sits in, as cli.py's REPO: the one whose files `baseline cite` stamps.
REPO = Path(__file__).resolve().parents[2]
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

TRIAGE_VERDICTS = ('TOUCHES', 'NOISE', 'UNSURE')
CORRECTIONS = ('STALE', 'WRONG', 'PARTIAL')
MECHANISM = 'JUDGMENT (mechanism STALE)'
VERIFY_VERDICTS = ('CONFIRMED', *CORRECTIONS, 'NOT FOUND', 'JUDGMENT', MECHANISM)
FILES_VERDICTS = ('consistent', 'contradicts', 'not covered')
TODO = 'TODO(owner)'
LIST_ITEM_RE = re.compile(r'[ \t]*(?:[-*+]|\d+[.)])[ \t]')
# A line that opens a Markdown block of its own ends a list item's lazy continuation.
BLOCK_START_RE = re.compile(r'[ \t]*(?:[-*+][ \t]|\d+[.)][ \t]|#{1,6}[ \t]|```|~~~|>|<)')
CLOSE_QUOTE_RE = re.compile(r'"[ \t]*(?:\||$)')
SEPARATOR_RE = re.compile(r'^[\s|:-]+$')
LINE_REF_RE = re.compile(r'L(\d+)')
DOC_REF_RE = re.compile(r'(.+):(\d+)')
# A files row's `file:line`, or a range of lines, `file:first-last`.
FILE_REF_RE = re.compile(r'(.+):(\d+)(?:-\d+)?')
CHANGELOG_REF_RE = re.compile(re.escape(CHANGELOG) + r':[1-9][0-9]*')
# A broken triage line's words that may name a section, a block, a bullet (`2.1.297#3`, never its release) or a release.
NAME_RE = re.compile(r'[\w.#-]+')
HEADERS = ('item', 'release', 'l<line>', 'file:line', 'file line', 'section')
# Column names: the report formats' own, less `none`, and a table header's usual ones. A line whose every field
# is one is a header, as an echoed B or C template and a table's own header row are; no row is such a line.
COLUMNS = frozenset(f.strip().strip('"').lower() for form in FORMATS for f in form.split('|')) - {'none'} | {
    'line', 'claim', 'verdict', 'doc', 'quote', 'wording', 'file'}
LEFT_OUT = 'left out (no surviving row, no none line)'


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


class Packet(NamedTuple):
    folder: Path
    index: dict
    report: str
    guide: str
    ids: list[str]  # the guide's section IDs, in guide order
    spans: dict[str, tuple[int, int]]  # each section's guide lines, 1-based, never past the guide's last line


def read_packet(folder: Path) -> Packet:
    '''A packet's index, its guide copy and the verifier's report.md.'''
    for name in (INDEX, GUIDE, REPORT):
        if not (folder / name).is_file():
            raise SetupError(f'{folder / name}: not found; save the verifier\'s report as {REPORT} in the packet'
                             if name == REPORT else f'{folder / name}: not found; not a packet')
    index = json.loads((folder / INDEX).read_text(encoding='utf-8'))
    guide = (folder / GUIDE).read_text(encoding='utf-8')
    last = len(guide.splitlines())
    spans = {sid: (first, min(end, last)) for sid, (first, end) in section_lines(guide).items()}
    return Packet(folder, index, (folder / REPORT).read_text(encoding='utf-8'), guide,
                  [s.id for s in sections(guide) if s.id], spans)


def command(p: Packet, *words: str) -> str:
    '''A cli.py command for the packet. One built on a cache other than the
    default names it, as the root option --cache, before the subcommand.'''
    cache = p.index.get('cache')
    root = ('--cache', cache) if cache and Path(cache).resolve() != default_cache().resolve() else ()
    return CLI + ' ' + ' '.join(shlex.quote(w) for w in (*root, *words))


CONFORMANCE = 'uv run --python 3.13 --with pyyaml python build/check_conformance.py'


class Settled(NamedTuple):
    lines: list[str]   # what settle prints
    clean: bool        # every row parsed and every quote was found, nothing discarded or left out
    saved: dict | None  # settled.json, for a triage


# ---- triage (R8.4 steps 4-6) ----------------------------------------------

class Tally:
    '''A triage report read row by row: the sections each item sends to
    verify, why, and what the report got wrong or left out.'''

    def __init__(self, p: Packet):
        self.p = p
        self.files = QuoteFiles(p.folder)
        self.blocks = {b['item']: b for b in p.index['blocks']}
        self.releases = {r['label']: r for r in p.index['releases']}
        self.bullets = {b['item']: b for r in p.index['releases'] for b in r['bullets']}
        self.release_of = {b['item']: r['label'] for r in p.index['releases'] for b in r['bullets']}
        self.flags: dict[str, list[str]] = {}     # section -> why it goes to verify, as settle prints it
        self.evidence: dict[str, list[str]] = {}  # section -> the same, with each row and item, for the verify packet
        # (release or None, text): an owner item with a release caps the advance below it
        self.owner: list[tuple[str | None, str]] = [(None, o) for o in p.index['owner']]
        self.notes: list[str] = []
        self.answered: set[str] = set()
        self.covered: dict[str, list[str]] = {}
        self.failed = self.unparseable = 0
        # The sections in the packet: every block's candidates and every section a release is untriaged for.
        within = {sid for b in p.index['blocks'] for sid in b['candidates']} | {
            sid for r in p.index['releases'] for sid in r['pending']}
        self.scope = [sid for sid in p.ids if sid in within]
        self.by_block: dict[str, set[str]] = {}  # block item -> the sections its rows flagged, in any group
        self.broken_blocks: list[tuple[str, str, str]] = []  # (block, why, detail): a broken line names the block
        self.spoiled: set[str] = set()  # releases a broken line names, never covered
        self.stray: list[str] = []  # broken rows that name no section, block or bullet

    def named(self, item: str) -> str:
        if item in self.blocks:
            return f"{item}, block {self.blocks[item]['ref']}"
        return f"{item}, bullet \"{self.bullets[item]['text']}\""

    def flag(self, sid: str, why: str, detail: str, item: str | None = None) -> None:
        self.flags.setdefault(sid, []).append(why)
        self.evidence.setdefault(sid, []).append(detail)
        if item in self.blocks:
            self.by_block.setdefault(item, set()).add(sid)

    def candidates(self, item: str, why: str, detail: str) -> None:
        '''Every candidate of a block whose row fails safe goes to verify.'''
        for sid in self.blocks[item]['candidates']:
            self.flag(sid, why, detail, item)

    def broken(self, line: str, kind: str) -> None:
        '''A line that does not parse is listed, and still fails safe on what
        it names: each section goes to verify; each block's candidates do too
        once a row answers that block (one with no row goes as `no row`); a
        bullet falls back to its hints. A line whose first field names a
        release is a coverage line, however it marks the label up, and every
        release it names stays uncovered; a release a broken row mentions only
        after its first field does not. A row that names no section, block or
        bullet holds the whole packet.'''
        self.notes.append(f'unparseable {kind}: {line}')
        self.unparseable += 1
        names = {name.rstrip('.') for name in NAME_RE.findall(line)}
        first = (split_row(line, 2) or [''])[0]
        sids = [sid for sid in self.p.ids if sid in names]
        blocks = [item for item in self.blocks if item in names]
        bullets = [item for item in self.bullets if item in names]
        lead = {name.rstrip('.') for name in NAME_RE.findall(first)}
        coverage = any(label in lead for label in self.releases)
        releases = [label for label in self.releases if label in names] if coverage else []
        if not (sids or blocks or bullets or releases):
            self.stray.append(line)
            return
        known = first in self.blocks or first in self.bullets or first in self.releases
        why = f'{first}: its {kind} does not parse' if known else f'a {kind} that does not parse names it'
        for sid in sids:
            self.flag(sid, why, f'{why}: {line}')
        for item in blocks:
            self.by_block.setdefault(item, set()).update(sids)
            said = why if item == first else f'{item}: a {kind} that does not parse names it'
            self.broken_blocks.append((item, said, f'{said}: {line}'))
        for item in bullets:
            self.fallback(item, 'its row does not parse' if item == first else f'a {kind} that does not parse '
                          'names it', line)
        self.spoiled.update(releases)

    def fallback(self, item: str, why: str, line: str) -> None:
        '''A bullet whose row says nothing safe goes to verify for each
        section its terms hint at, or is an owner item when they hit none.'''
        hints = self.bullets[item]['hints']
        for hint in hints:
            self.flag(hint, f'{item}: {why}', f'{self.named(item)}: {why}: {line}')
        if not hints:
            self.owner.append((self.release_of[item], f"{item}: {why}, and its bullet hits no section's terms"))

    def source_found(self, item: str, quote: str) -> bool:
        '''A source quote counts only within its own item: a block's text in
        blocks.md, by the lines its index entry names, or a bullet's text.'''
        if not quote:
            return False
        if item in self.bullets:
            return quote in self.bullets[item]['text']
        lines = self.files.lines(BLOCKS) or []
        return any(quote in lines[n - 1] for first, last in self.blocks[item]['lines']
                   for n in range(first, min(last, len(lines)) + 1))

    def coverage(self, label: str, line: str) -> None:
        rest = split_row(line, 2)[1]
        listed = [s.strip() for s in rest.split(',')] if rest.strip().lower() != 'none' else []
        if '|' in rest or any(s not in self.p.ids for s in listed):
            self.broken(line, 'coverage line')  # its release stays uncovered (fail_safe)
            return
        self.covered[label] = listed
        for sid in listed:
            self.flag(sid, f'{label}: its coverage line names it', f'{label}: its coverage line names it')

    def row(self, item: str, line: str) -> None:
        row = split_row(line, 7, TRIAGE_QUOTES) if item in self.blocks or item in self.bullets else None
        verdict = row[1].upper() if row else ''
        sid = given(row[2]) if row else ''
        if not (row is not None and verdict in TRIAGE_VERDICTS
                and (sid in self.p.ids or (verdict == 'NOISE' and not sid))
                and (verdict != 'NOISE' or given(row[6]))):
            self.broken(line, 'row')  # a broken bullet row falls back to the bullet's hints
            return
        self.answered.add(item)
        guide_ok = self.files.find_any(self.p.index['quotes']['guide'], unquote(row[4])) is not None
        source_ok = self.source_found(item, unquote(row[5]))
        if verdict == 'NOISE':
            # A NOISE row's failed quote, its source quote or a guide quote it
            # gives, never clears its item: UNSURE for its section and every
            # candidate or hint.
            if not source_ok or (unquote(row[4]) and not guide_ok):
                self.failed += 1
                self.notes.append(f'quote not found, NOISE becomes UNSURE: {line}')
                why = f"its NOISE row's {'guide' if source_ok else 'source'} quote was not found"
                if sid:
                    self.flag(sid, f'{item}: {why}', f'{self.named(item)}: {why}: {line}', item)
                if item in self.blocks:
                    self.candidates(item, f'{item}: {why}', f'{self.named(item)}: {why}: {line}')
                elif not sid or self.bullets[item]['hints']:
                    self.fallback(item, why, line)
            return
        ok = guide_ok and source_ok
        if not ok:
            self.failed += 1
            self.notes.append(f'quote not found, {verdict} becomes UNSURE: {line}')
        why = f'{item}: {verdict}' + ('' if ok else ', quote not found')
        self.flag(sid, why, f'{self.named(item)}: {line}', item)
        if not ok and item in self.blocks:  # a failed quote clears none of the block's candidates either
            self.candidates(item, why, f'{self.named(item)}: {line}')

    def fail_safe(self) -> list[str]:
        '''Silence never counts as NOISE: each block with no row and each
        release with no coverage line, or none that parses, goes to verify,
        and so does each candidate of an answered block a broken line names.
        A broken line that names nothing holds the whole packet. Returns the
        blocks and releases left out.'''
        for label in self.spoiled:
            self.covered.pop(label, None)
        for item, b in self.blocks.items():
            if item not in self.answered:
                for sid in b['candidates']:
                    self.flag(sid, f'{item}: no row', f'{self.named(item)}: no row')
        for item, why, detail in self.broken_blocks:
            if item in self.answered:
                self.candidates(item, why, detail)
        for label, r in self.releases.items():
            if label in self.covered:
                continue
            why = f'{label}: ' + ('its coverage line does not parse' if label in self.spoiled else 'no coverage line')
            for sid in r['hits']:
                hinting = '; '.join(f"\"{b['text']}\"" for b in r['bullets'] if sid in b['hints'])
                self.flag(sid, why, f'{why}; its bullets that hint at it: {hinting}')
            if not r['hits']:
                self.owner.append((label, f"{why}, and its bullets hit no section's terms"))
        why = 'a row that does not parse names no section, block or bullet'
        for line in self.stray:
            for sid in self.scope:
                self.flag(sid, why, f'{why}: {line}')
        return [i for i in self.blocks if i not in self.answered] + [r for r in self.releases if r not in self.covered]


def settle_triage(p: Packet) -> Settled:
    t = Tally(p)
    for line in report_lines(p.report):
        first = (split_row(line, 2) or [''])[0]
        if first in t.releases:
            t.coverage(first, line)
        else:
            t.row(first, line)
    omitted = t.fail_safe()
    index, order = p.index, p.ids
    verify = sorted(t.flags, key=order.index)
    held = set(index['held'])
    capped = [release for release, _ in t.owner if release is not None]
    labels = sorted(t.releases, key=version_key)
    if capped:
        oldest = min(capped, key=version_key)
        labels = [label for label in labels if version_key(label) < version_key(oldest)]
    target = labels[-1] if labels else None
    advance = [sid for sid in order if sid not in t.flags and sid not in held
               and any(sid in t.releases[label]['pending'] for label in labels)]
    # A group's blocks also wait while a section a row for one of them flagged,
    # in any group, is flagged: another group's verify packet never carries them.
    crossing = {b['group'] for b in index['blocks'] if any(s in t.flags for s in t.by_block.get(b['item'], ()))}
    rebaseline = {gid: [b['ref'] for b in index['blocks'] if b['group'] == gid]
                  for gid, sids in index['groups'].items()
                  if any(b['group'] == gid for b in index['blocks'])
                  and not any(s in t.flags or s in held for s in sids) and gid not in crossing}
    cleared = [sid for sid in t.scope if sid not in t.flags and sid not in held]

    out = [f'cc-guide settle: triage, {p.folder}',
           f'report: {len(t.answered)} item(s) answered, {len(t.covered)} of {len(t.releases)} release(s) covered; '
           f'{t.failed} quote(s) not found; {t.unparseable} unparseable line(s); {len(omitted)} left out']
    out += [f'  {n}' for n in t.notes]
    out += [f'UNSURE or TOUCHES {sid}: ' + '; '.join(dict.fromkeys(t.flags[sid])) for sid in verify]
    out += [f'owner: {o}' for _, o in t.owner]
    if held:
        out.append(f"held, never advanced here: {' '.join(sorted(held, key=order.index))}")
    steps = [command(p, 'baseline', 'rebaseline', gid, *refs, '--head', index['head'])
             for gid, refs in rebaseline.items()]
    if advance and target:
        steps.append(command(p, 'baseline', 'advance', *advance, '--to', target))
    if steps:
        out.append('then, in this order (R8.8):')
        out += [f'  {s}' for s in [*steps, command(p, 'baseline', 'stamp'), command(p, 'lint'), CONFORMANCE]]
    else:
        out.append('nothing to record')
    if verify:
        out.append(f"verify: /cc-guide verify {' '.join(verify)}; or defer it, and those sections do not advance, "
                   'so the next triage shows them again')
    if index.get('next_through'):
        out.append('next range, once these commands are run: '
                   + command(p, 'packets', '--triage', '--through', index['next_through']))
    saved = {'mode': 'triage', 'advance_to': target, 'verify': verify, 'cleared': cleared,
             'held': sorted(held, key=order.index),
             'rows': {sid: list(dict.fromkeys(t.evidence[sid])) for sid in verify}}
    return Settled(out, not t.failed and not t.unparseable and not omitted, saved)


# ---- verify and audit (R8.5, R8.6, R8.8) ------------------------------------

def section_at(p: Packet, line: int) -> str | None:
    '''The section whose lines hold a guide line, by the ranges the packet
    gives its verifier; None before the first section or past the guide's
    last line.'''
    return next((sid for sid, (first, last) in p.spans.items() if first <= line <= last), None)


def todo_reaches(guide: str) -> list[tuple[int, int]]:
    '''R8.5: each TODO(owner)'s reach, 1-based and inclusive. The guide's
    one TODO names "the first bullet below", so a TODO reaches from its own
    line through the first list item after it outside fenced code, with its
    continuation lines and nested content, or to the end of its section when
    no list item follows; never past its section. A TODO in fenced code is
    an example, not one.'''
    lines = guide.split('\n')
    fenced = fenced_lines(lines)  # 0-based
    spans = list(section_lines(guide).values())
    out = []
    for n, text in enumerate(lines, start=1):
        if TODO not in text or n - 1 in fenced:
            continue
        end = next((e for s, e in spans if s <= n <= e), None)
        if end is None:
            continue
        item = next((m for m in range(n + 1, end + 1)
                     if m - 1 not in fenced and LIST_ITEM_RE.match(lines[m - 1])), None)
        if item is None:
            out.append((n, end))
            continue
        indent = len(lines[item - 1]) - len(lines[item - 1].lstrip())
        last, blank = item, False
        for m in range(item + 1, end + 1):
            s = lines[m - 1]
            if not s.strip():
                blank = True
                continue
            deeper = len(s) - len(s.lstrip()) > indent
            if not (deeper or (not blank and not BLOCK_START_RE.match(s))):
                break
            last, blank = m, False
        out.append((n, last))
    return out


def review_verdict(field: str) -> str:
    '''A verify or audit row's verdict, in VERIFY_VERDICTS' letter case.'''
    return field.upper().replace('(MECHANISM STALE)', '(mechanism STALE)')


def review_fits(rest: list[str]) -> bool:
    '''Whether a verify or audit row's fields after its claim open with a
    verdict and a doc reference, or `-` for none.'''
    return review_verdict(rest[0]) in VERIFY_VERDICTS and (not given(rest[1]) or bool(DOC_REF_RE.fullmatch(rest[1])))


def settle_review(p: Packet, hold: tuple[str, ...]) -> Settled:
    '''verify and audit: R8.5's A/B/C report under R8.8's discard rule.'''
    index = p.index
    scope, cleared = index['sections'], index.get('cleared', [])
    files = QuoteFiles(p.folder)
    docs = [QuoteFiles(Path(root)) for root in index['quotes']['docs']]
    reaches = todo_reaches(p.guide)

    def found(ref_field: str, quote: str) -> bool:
        '''A doc quote counts in the packet's changelog.md or a page of the
        snapshot, never in the report, the guide copy or the index.'''
        ref = DOC_REF_RE.fullmatch(ref_field)
        if ref is None or not quote:
            return False
        if ref.group(1) in index['quotes']['changelog']:
            return files.find(ref.group(1), quote) is not None
        return any(d.find(ref.group(1), quote) is not None for d in docs)

    corrections, owner, unverified, changelog = [], [], [], []
    confirmed = 0
    held = set(index.get('held', [])) | set(hold)
    answered: set[str] = set()
    whole_held = False

    def hold_inside(sid: str) -> None:
        '''A row holds its section only inside the packet's sections: the run
        neither reviews nor advances any other, and its triage may have
        advanced it already.'''
        if sid in scope:
            held.add(sid)

    for line in report_lines(p.report):
        first = (split_row(line, 2) or [''])[0]
        if first == 'B':
            row = split_row(line, 4)
            if row is None or not (LABEL_RE.fullmatch(given(row[1])) and given(row[2])
                                   and CHANGELOG_REF_RE.fullmatch(row[3])):
                unverified.append(f'unparseable: {line}')
            else:
                changelog.append(' | '.join(row[1:]))
            continue
        if first == 'C':
            omission = given(split_row(line, 2)[1])
            if omission:
                owner.append(f'omission: {omission}')
            else:
                unverified.append(f'unparseable: {line}')
            continue
        if first in p.ids:  # `<section> | none`: the section holds no checkable claim
            if not none_line(line):
                unverified.append(f'unparseable: {line}')
                hold_inside(first)
            elif first in scope:
                answered.add(first)
            # one for a section outside the packet's sections says nothing this run reviews, so it holds nothing
            continue
        m = LINE_REF_RE.fullmatch(first)
        row = split_row(line, 6, VERIFY_QUOTES, review_fits) if m else None
        verdict = review_verdict(row[2]) if row else ''
        n = int(m.group(1)) if m else 0
        sid = section_at(p, n) if m else None
        if row is None or verdict not in VERIFY_VERDICTS or sid is None:
            unverified.append(f'unparseable: {line}')
            if sid is None:
                whole_held = True
            else:
                hold_inside(sid)
            continue
        quote, wording = unquote(row[4]), given(row[5])
        if (quote or verdict not in ('NOT FOUND', 'JUDGMENT')) and not found(row[3], quote):
            unverified.append(f'quote not found, discarded: {line}')
            if verdict in (*CORRECTIONS, MECHANISM):
                hold_inside(sid)
            continue
        if verdict in CORRECTIONS and not wording:
            unverified.append(f'no proposed wording, discarded: {line}')
            hold_inside(sid)
            continue
        answered.add(sid)
        where = f'L{n} {sid} {verdict}'
        near = any(a <= n <= b for a, b in reaches)
        if verdict == 'CONFIRMED':
            confirmed += 1
        elif verdict in CORRECTIONS and sid not in scope:
            owner.append(f"{where} (outside this packet's sections, so it holds nothing; /cc-guide verify {sid} "
                         f'reviews it): {row[1]} → {wording}')
        elif verdict in CORRECTIONS and not near:
            corrections.append((sid, f'{where}: {row[1]} → {wording} ({row[3]}: "{quote}")'))
        elif verdict in CORRECTIONS:  # listed for the owner, so it holds its section
            owner.append(f'{where} (next to a TODO(owner), report-only): {row[1]} → {wording}')
            held.add(sid)
        else:
            owner.append(f'{where}: {row[1]}' + (f' ({row[3]}: "{quote}")' if quote else ''))
            if verdict == MECHANISM:  # a judgment whose mechanism moved waits for the owner
                hold_inside(sid)
    if whole_held:
        held |= set(scope)
    left = [sid for sid in scope if sid not in answered]
    held |= set(left)
    fixed = list(dict.fromkeys(sid for sid, _ in corrections))
    resolved = {sid for sid in [*scope, *cleared] if sid not in held}
    ready = [b for b in index['blocks'] if set(b['candidates']) <= resolved]
    # baseline rebaselines a page's changed and missing blocks together, so a
    # page that keeps one unresolved waits whole (R7)
    waiting = {b['page'] for b in index['blocks'] if b['kind'] != 'new' and b not in ready}
    refs = [b['ref'] for b in ready if b['page'] not in waiting]
    mode = index['mode']
    out = [f"cc-guide settle: {mode} {index['group']}, {p.folder}",
           f'report: {confirmed} confirmed, {len(corrections)} correction(s), {len(owner)} owner\'s call, '
           f'{len(unverified)} unverified']
    out += ['corrections, to apply to the guide in the working tree:'] + [f'  {c}' for _, c in corrections]
    out += ["owner's call, never applied:"] + [f'  {o}' for o in owner]
    out += ['unverified, discarded:'] + [f'  {u}' for u in unverified]
    out += ['changelog items (B):'] + [f'  {c}' for c in changelog]
    if left:
        out.append(f"{LEFT_OUT}, so held: {' '.join(left)}")
    shown = [sid for sid in scope if sid in held]
    if shown:
        out.append(f"held, neither advanced nor audited: {' '.join(shown)}")
    steps = []
    if fixed:
        steps.append(command(p, 'baseline', 'accept', *fixed, '--substantive') + '   # only the sections you changed')
    if refs:
        steps.append(command(p, 'baseline', 'rebaseline', index['group'], *refs, '--head', index['head']))
    # a section checked past the triage's target is not advanced backwards
    target, checked = index.get('advance_to'), index.get('checked', {})
    advance = [sid for sid in scope if sid not in held
               and not (target and sid in checked and version_key(checked[sid]) > version_key(target))]
    if mode == 'audit' and not any(sid in held for sid in scope):
        steps.append(command(p, 'baseline', 'audited', index['group'], '--to', index['head']))
    elif mode == 'verify' and target and advance:
        steps.append(command(p, 'baseline', 'advance', *advance, '--to', target))
    steps += [command(p, 'baseline', 'stamp'), command(p, 'lint'), CONFORMANCE]
    out.append('then, in this order (R8.8), once every correction is applied; for one you leave for the owner, '
               'settle again with --hold <section>, which holds the section and keeps its accept:')
    out += [f'  {s}' for s in steps]
    out.append('a correction that resolves a conformance gap removes its [[exception]] from '
               'build/cc_guide/conformance.toml in the same change; lint\'s STALE lines then name the citing files '
               'of each section whose `changed` moved')
    return Settled(out, not unverified and not left, None)


# ---- files (R8.7, R8.8) -----------------------------------------------------

STAMP_RE = re.compile(rf'@{STAMP_PATTERN}')


def unstamped(text: str) -> list[str]:
    '''A file's lines, each citation-shaped line's stamp masked: the one
    thing `baseline cite` rewrites.'''
    return [STAMP_RE.sub('@', line) if CITE_SHAPED_RE.match(line) else line for line in text.split('\n')]


def same_file(p: Packet, repo: Path) -> bool:
    '''Whether the file in the checkout at repo is still the packet's copy,
    which the verifier read, apart from its citation's stamp.'''
    copy = p.folder / p.index['copy']
    text = Source(repo).read(p.index['file'])
    return copy.is_file() and text is not None and unstamped(text) == unstamped(read_utf8(copy))


def settle_files(p: Packet, hold: tuple[str, ...], repo: Path) -> Settled:
    index = p.index
    files = QuoteFiles(p.folder)
    path = index['file']
    fixes, owner, unverified = [], [], []
    consistent = 0
    answered: set[str] = set()
    discarded = False

    def fits(rest: list[str]) -> bool:
        '''Whether a row's fields after its statement are a section the file
        cites, a quote and a verdict.'''
        return rest[0] in index['sections'] and rest[2].strip().lower() in FILES_VERDICTS

    for line in report_lines(p.report):
        first = (split_row(line, 2) or [''])[0]
        if first in index['sections']:  # `<section> | none`: no statement in the file rests on it
            if none_line(line):
                answered.add(first)
            else:
                unverified.append(f'unparseable: {line}')
                discarded = True
            continue
        row = split_row(line, 5, FILES_QUOTES, fits)
        ref = FILE_REF_RE.fullmatch(row[0]) if row else None
        verdict = row[4].strip().lower() if row else ''
        if ref is None or ref.group(1) != path or verdict not in FILES_VERDICTS or row[2] not in index['sections']:
            unverified.append(f'unparseable: {line}')
            discarded = True
            continue
        quote = unquote(row[3])
        if (quote or verdict != 'not covered') and files.find_any(index['quotes']['guide'], quote) is None:
            unverified.append(f'quote not found, discarded: {line}')
            discarded = discarded or verdict == 'contradicts'
            continue
        answered.add(row[2])
        if verdict == 'consistent':
            consistent += 1
        elif verdict == 'contradicts':
            fixes.append(f'{row[0]} ({row[2]}): {row[1]} (guide: "{quote}")')
        else:
            owner.append(f'{row[0]} ({row[2]}, not covered; a coverage gap?): {row[1]}')
    left = [sid for sid in index['sections'] if sid not in answered]
    reasons = (['a discarded or unparseable row might have changed it'] if discarded else []) + (
        ['a cited section was left out'] if left else []) + (['held by --hold'] if hold else []) + (
        [] if same_file(p, repo) else ['the file changed after its packet was built'])
    out = [f'cc-guide settle: files {path}, {p.folder}',
           f'report: {consistent} consistent, {len(fixes)} contradiction(s), {len(owner)} not covered, '
           f'{len(unverified)} unverified']
    out += [f'contradictions, to fix in {path} in the working tree:'] + [f'  {f}' for f in fixes]
    out += ["owner's call, never applied:"] + [f'  {o}' for o in owner]
    out += ['unverified, discarded:'] + [f'  {u}' for u in unverified]
    if left:
        out.append(f"{LEFT_OUT}: {' '.join(left)}")
    steps = [command(p, 'lint'), CONFORMANCE]
    if reasons:
        out.append(f"held, not cited: {path}: {'; '.join(reasons)}")
    else:
        steps.insert(0, command(p, 'baseline', 'cite', path))
    out.append(f'then, in this order (R8.8), once every contradiction is fixed in {path}, unless '
               'build/cc_guide/conformance.toml records it as a deviation, which stays as it is; for one you leave '
               f'for the owner, settle again with --hold {path}, which skips its cite:')
    out += [f'  {s}' for s in steps]
    return Settled(out, not unverified and not left, None)


def settle(folder: Path, hold: Iterable[str] = (), repo: Path | None = None) -> Settled:
    '''Settle the packet in folder against its report.md. A triage also
    writes settled.json there, which `packets --verify --from` reads.
    `hold` names the sections, or the file, the session leaves for the
    owner: they are held as a discarded correction holds them. A files
    packet's copy is compared with its file in the checkout at repo,
    REPO by default.'''
    p = read_packet(folder)
    mode = p.index.get('mode')
    hold = tuple(dict.fromkeys(hold))
    if mode == 'triage':
        if hold:
            raise SetupError('--hold goes with a verify, audit or files packet')
        result = settle_triage(p)
        (folder / SETTLED).write_text(json.dumps(result.saved, indent=1) + '\n', encoding='utf-8')
        return result
    if mode in ('verify', 'audit'):
        unknown = [h for h in hold if h not in p.index['sections']]
        if unknown:
            raise SetupError(f"--hold {' '.join(unknown)}: not a section this packet reviews "
                             f"({', '.join(p.index['sections'])})")
        return settle_review(p, hold)
    if mode == 'files':
        other = [h for h in hold if h != p.index['file']]
        if other:
            raise SetupError(f"--hold {' '.join(other)}: a files packet holds only its file, {p.index['file']}")
        return settle_files(p, hold, repo or REPO)
    raise SetupError(f'{folder / INDEX}: unknown mode {mode!r}')
