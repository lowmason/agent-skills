'''The guide: its anchored sections, their text hashes and terms, the stamp
region, and the citations that point at its sections (drift spec R1, R2.3,
R3.6, R4).'''
import ast
import hashlib
import re
import warnings
from pathlib import PurePosixPath
from typing import NamedTuple

from blocks import fenced_lines
from docs import version_key

# A ## or ### ATX heading. The guide's sections are exactly these (R1.1).
HEADING_RE = re.compile(r'^(#{2,3})[ \t]')
# A section ID: two or more dot-separated [a-z0-9-] segments (R1.1).
ID_RE = re.compile(r'[a-z0-9-]+(?:\.[a-z0-9-]+)+')
ANCHOR_RE = re.compile(rf'^<!-- cc: ({ID_RE.pattern}) -->$')
# What text_hash returns.
TEXT_HASH_RE = re.compile(r'sha256:[0-9a-f]{64}')
# Anything meant as an anchor, well-formed or not. The stamp markers do not
# match: `cc` must be followed by `:`.
ANCHOR_LIKE_RE = re.compile(r'^<!--\s*cc:')
STAMP_OPEN = '<!-- cc-guide:stamp -->'
STAMP_CLOSE = '<!-- /cc-guide:stamp -->'
# What a guide without a stamp region lacks, as lint and `baseline stamp` say it.
NO_STAMP = f'needs one stamp region, a {STAMP_OPEN} line then a {STAMP_CLOSE} line'
BACKTICKS_RE = re.compile(r'`+')
TERM_MIN, TERM_MAX = 3, 60
# R3.6's generic words: its four examples, plus each single lowercase word or
# bare extension among the guide's terms that appeared in at least 5% of the
# blocks on the 2.1.288 snapshot's `terms` pages (measured 2026-10-04).
STOP_TERMS = frozenset({
    '.md', 'agent', 'auto', 'background', 'command', 'default', 'false', 'local',
    'low', 'model', 'name', 'paths', 'plan', 'project', 'prompt', 'run', 'settings',
    'shell', 'skills', 'tools', 'true', 'user',
})


class Section(NamedTuple):
    line: int            # 1-based line of the heading
    heading: str         # the heading line, stripped
    parent: str | None   # the enclosing ## heading line of a ###, else None
    id: str | None       # the anchor's ID, or None without a well-formed anchor
    text: str            # heading through the section's last line, anchor line excluded
    prose: str           # the same lines less fenced ones, for terms


class AnchorProblem(NamedTuple):
    line: int        # 1-based line the problem is on
    id: str | None   # the repeated anchor's ID; None for every other problem
    message: str     # the problem, without its line


def scan(text: str) -> tuple[list[Section], list[AnchorProblem]]:
    '''R1.1's grammar, read once for both this package and
    build/check_conformance.py: the guide's ## and ### headings outside fenced
    code, each with its anchor's ID and its text, and every anchor problem.
    A ## section runs to its first ###; the last section runs to the end of
    the file. A repeated anchor IDs only its first heading, since every
    reader keys sections by ID.'''
    lines = text.split('\n')
    fenced = fenced_lines(lines)
    starts = [i for i, line in enumerate(lines) if i not in fenced and HEADING_RE.match(line)]
    found: list[Section] = []
    problems: list[AnchorProblem] = []
    under: set[int] = set()
    first: dict[str, int] = {}
    parent = None
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        heading = lines[start].strip()
        is_sub = lines[start].startswith('###')
        if not is_sub:
            parent = heading
        nxt = lines[start + 1] if start + 1 < end else ''
        anchor = ANCHOR_RE.match(nxt)
        sid = None
        if anchor:
            under.add(start + 1)
            if anchor.group(1) in first:
                problems.append(AnchorProblem(start + 2, anchor.group(1),
                                              f'anchor {anchor.group(1)} repeats line {first[anchor.group(1)]}'))
            else:
                first[anchor.group(1)] = start + 2
                sid = anchor.group(1)
        elif ANCHOR_LIKE_RE.match(nxt):
            under.add(start + 1)
            problems.append(AnchorProblem(start + 2, None, f'malformed anchor {nxt.strip()!r}'))
        else:
            problems.append(AnchorProblem(start + 1, None, f'heading {heading!r} has no anchor on its next line'))
        body = [i for i in range(start, end) if not (anchor and i == start + 1)]
        found.append(Section(start + 1, heading, parent if is_sub else None, sid,
                             '\n'.join(lines[i] for i in body),
                             '\n'.join(lines[i] for i in body if i not in fenced)))
    problems += [AnchorProblem(i + 1, None, 'anchor is not directly under a heading')
                 for i, line in enumerate(lines)
                 if i not in fenced and i not in under and ANCHOR_LIKE_RE.match(line)]
    return found, problems


def sections(text: str) -> list[Section]:
    '''The guide's sections (R1.1), as scan reads them.'''
    return scan(text)[0]


def anchor_problems(text: str) -> list[str]:
    '''R1.1 as the lint states it: every heading has exactly one well-formed
    anchor on its next line, and no anchor repeats or stands anywhere else.'''
    return [f'guide line {p.line}: {p.message}' for p in scan(text)[1]]


def text_hash(section_text: str) -> str:
    '''R2.3: `sha256:` over the section's text with every whitespace run
    collapsed to one space, so a rewrap changes nothing.'''
    collapsed = ' '.join(section_text.split())
    return 'sha256:' + hashlib.sha256(collapsed.encode('utf-8')).hexdigest()


def code_spans(line: str) -> list[str]:
    '''The inline code spans of one line, matched CommonMark-style: a run of
    n backticks closes on the next run of exactly n, and an unmatched run is
    literal. One space comes off each end when both ends have one.'''
    runs = list(BACKTICKS_RE.finditer(line))
    spans: list[str] = []
    i = 0
    while i < len(runs):
        size = len(runs[i].group())
        j = next((j for j in range(i + 1, len(runs)) if len(runs[j].group()) == size), None)
        if j is None:
            i += 1
            continue
        content = line[runs[i].end():runs[j].start()]
        if content.startswith(' ') and content.endswith(' ') and content.strip():
            content = content[1:-1]
        spans.append(content)
        i = j + 1
    return spans


def section_terms(section: Section, extra=(), exclude=()) -> set[str]:
    '''R3.6: the section's backticked spans outside fenced code, paired first
    and kept at 3-60 characters afterwards, minus STOP_TERMS, plus its
    extra_terms, minus its exclude_terms.'''
    spans = {span for line in section.prose.split('\n') for span in code_spans(line)}
    kept = {s for s in spans if TERM_MIN <= len(s) <= TERM_MAX} - STOP_TERMS
    return (kept | set(extra)) - set(exclude)


def stamp_bounds(text: str) -> tuple[int, int] | None:
    '''0-based line indexes of the stamp region's two markers, or None unless
    each appears once outside fenced code, open before close.'''
    lines = text.split('\n')
    fenced = fenced_lines(lines)
    opens = [i for i, line in enumerate(lines) if i not in fenced and line.strip() == STAMP_OPEN]
    closes = [i for i, line in enumerate(lines) if i not in fenced and line.strip() == STAMP_CLOSE]
    if len(opens) != 1 or len(closes) != 1 or closes[0] < opens[0]:
        return None
    return opens[0], closes[0]


def stamp_content(text: str) -> str | None:
    '''The lines between the stamp markers, or None without a region.'''
    bounds = stamp_bounds(text)
    if bounds is None:
        return None
    return '\n'.join(text.split('\n')[bounds[0] + 1:bounds[1]])


def with_stamp(text: str, content: str) -> str:
    '''The guide with its stamp region's content replaced (R1.2).'''
    bounds = stamp_bounds(text)
    if bounds is None:
        raise ValueError('the guide has no stamp region')
    lines = text.split('\n')
    return '\n'.join(lines[:bounds[0] + 1] + content.split('\n') + lines[bounds[1]:])


def render_stamp(section_states: dict[str, dict]) -> str:
    '''R1.2's generated sentence, from baseline.json's sections: the oldest
    `checked` (by release, then date) and the oldest `audited` (by date, then
    release). Both dates are the day the check or audit was done.'''
    checked = min((s['checked'] for s in section_states.values()),
                  key=lambda c: (version_key(c['release']), c['date']))
    audited = min((s['audited'] for s in section_states.values()),
                  key=lambda a: (a['date'], version_key(a['release'])))
    return (f"> Checked against the Claude Code docs and changelog through {checked['release']} "
            f"on {checked['date']}; oldest full re-verification {audited['date']}, "
            f"at {audited['release']}.")


# R5's citation-shaped line: after indentation, `#` or `<!--`, then
# `cc-guide:`. Looser than R4.1's two forms, so a near-miss is still read.
CITE_SHAPED_RE = re.compile(r'^[ \t]*(?:#|<!--)[ \t]*cc-guide:')
# R2.4's stamp: a three-part release, plus the fourth part `baseline accept` adds.
# A shorter one would lint clean and then crash baseline.next_changed.
STAMP_PATTERN = r'[0-9]+\.[0-9]+\.[0-9]+(?:\.[0-9]+)?'
CITE_BODY = rf'cc-guide: (?P<ids>{ID_RE.pattern}(?: {ID_RE.pattern})*) @(?P<stamp>{STAMP_PATTERN})'
HASH_CITE_RE = re.compile(rf'# {CITE_BODY}')
HTML_CITE_RE = re.compile(rf'<!-- {CITE_BODY} -->')
HASH_FORM = '`# cc-guide: <id> [<id> …] @<version>`'
HTML_FORM = '`<!-- cc-guide: <id> [<id> …] @<version> -->`'
FRONTMATTER = '---'
PEP723_OPEN, PEP723_CLOSE = '# /// script', '# ///'
# R4.1's first row: these kinds cite inside a frontmatter that opens the file,
# so an HTML-form citation on line 1 would push their frontmatter down.
FRONTMATTER_KINDS = ('skills/*/SKILL.md', '.claude/skills/*/SKILL.md', 'agents/*.md', '.claude/agents/*.md',
                     'commands/*.md', 'rules/*.md')
# R4.1: the Markdown a skill loads on demand carries no citation, since its
# SKILL.md's covers it; a README or INSTALL file loads nowhere, so it cites itself.
SKILL_MARKDOWN = ('skills/*/**/*.md', '.claude/skills/*/**/*.md')
SELF_CITED = ('SKILL.md', 'README.md', 'INSTALL.md')


class Citation(NamedTuple):
    path: str              # repo-relative
    line: int              # 1-based
    ids: tuple[str, ...]   # as written
    stamp: str             # the release the file was last reviewed against


class Slot(NamedTuple):
    '''Where R4.1 lets one file carry its citation.'''
    lines: frozenset[int]  # 0-based lines the citation may sit on
    form: re.Pattern       # HASH_CITE_RE or HTML_CITE_RE
    shape: str             # the form, as messages print it
    place: str             # the rule, as messages print it


def first_code(lines: list[str]) -> int:
    '''The first line that is neither blank nor a `#` comment, or len(lines).'''
    return next((i for i, line in enumerate(lines)
                 if line.strip() and not line.lstrip().startswith('#')), len(lines))


def pep723_lines(lines: list[str]) -> set[int]:
    '''The lines of each PEP 723 block, markers included; an unclosed one
    runs to the end.'''
    out: set[int] = set()
    start = None
    for i, line in enumerate(lines):
        if start is None and line.rstrip() == PEP723_OPEN:
            start = i
        elif start is not None and line.rstrip() == PEP723_CLOSE:
            out.update(range(start, i + 1))
            start = None
    if start is not None:
        out.update(range(start, len(lines)))
    return out


def python_lines(lines: list[str]) -> frozenset[int] | str:
    '''The lines before a Python file's first line of code, less its module
    docstring and any PEP 723 block; or why the file cannot be read.'''
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', SyntaxWarning)
            body = ast.parse('\n'.join(lines)).body
    except SyntaxError as exc:
        return f'does not parse as Python ({exc.msg})'
    doc = range(0)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
            and isinstance(body[0].value.value, str):
        doc = range(body[0].lineno - 1, body[0].end_lineno)
        body = body[1:]
    first = len(lines)
    if body:
        first = min([body[0].lineno] + [d.lineno for d in getattr(body[0], 'decorator_list', [])]) - 1
    block = pep723_lines(lines)
    return frozenset(i for i in range(first) if i not in doc and i not in block)


def citation_slot(path: str, lines: list[str]) -> Slot | str:
    '''R4.1's placement for the file at path, or why it can carry no
    citation. Markdown with frontmatter (skills, agents, commands, rules)
    takes a YAML comment as the frontmatter's last line, and those kinds
    always open with one; other Markdown an HTML comment on its first line,
    except the Markdown a skill loads on demand; TOML, shell and Python a `#`
    line before the first key or line of code.'''
    name = path.rsplit('/', 1)[-1]
    if name.endswith('.md'):
        kind = PurePosixPath(path)
        if name not in SELF_CITED and any(kind.full_match(g) for g in SKILL_MARKDOWN):
            return "its skill loads it on demand, so the skill's SKILL.md citation covers it"
        if lines[0] != FRONTMATTER:
            if any(kind.full_match(g) for g in FRONTMATTER_KINDS):
                return 'its kind cites as the last line of a frontmatter that opens the file'
            return Slot(frozenset({0}), HTML_CITE_RE, HTML_FORM, 'the first line')
        close = next((i for i in range(1, len(lines)) if lines[i] == FRONTMATTER), None)
        if close is None:
            return 'its frontmatter never closes'
        return Slot(frozenset({close - 1} - {0}), HASH_CITE_RE, HASH_FORM, 'the last line inside the frontmatter')
    if name.endswith('.toml'):
        return Slot(frozenset(range(first_code(lines))), HASH_CITE_RE, HASH_FORM, 'a line before the first key or table')
    if name.endswith('.py'):
        found = python_lines(lines)
        if isinstance(found, str):
            return found
        return Slot(found, HASH_CITE_RE, HASH_FORM,
                    'a line before the first line of code, outside the docstring and any PEP 723 block')
    if name.endswith('.sh') or lines[0].startswith('#!'):
        return Slot(frozenset(range(first_code(lines))), HASH_CITE_RE, HASH_FORM, 'a line before the first line of code')
    return 'R4.1 gives this kind of file no citation'


def file_citation(path: str, text: str) -> tuple[Citation | None, list[str]]:
    '''R4.1 and R5 for one file: its citation, and every problem with its
    citation-shaped lines. The citation is None unless the file has exactly
    one such line, well-formed, at column 0, where R4.1 puts it.'''
    lines = text.split('\n')
    shaped = [i for i, line in enumerate(lines) if CITE_SHAPED_RE.match(line)]
    if not shaped:
        return None, []
    slot = citation_slot(path, lines)
    problems = [f'{path}:{i + 1}: a second citation; a file carries one' for i in shaped[1:]]
    i = shaped[0]
    where = f'{path}:{i + 1}'
    if isinstance(slot, str):
        return None, [f'{where}: no citation can go here: {slot}'] + problems
    if i not in slot.lines:
        return None, [f'{where}: a citation goes on {slot.place} (R4.1)'] + problems
    match = slot.form.fullmatch(lines[i])
    if match is None:
        indented = slot.form.fullmatch(lines[i].strip()) is not None
        return None, [f'{where}: an indented citation; it starts at column 0' if indented
                      else f'{where}: malformed citation; the form is {slot.shape}'] + problems
    ids = tuple(match['ids'].split(' '))
    twice = sorted({sid for sid in ids if ids.count(sid) > 1})
    if twice:
        problems.insert(0, f"{where}: cites {', '.join(twice)} twice")
    if problems:
        return None, problems
    return Citation(path, i + 1, ids, match['stamp']), []


def read_citations(files: dict[str, str]) -> tuple[list[Citation], list[str]]:
    '''Each file's citation and problems (R4.1, R5), in path order.'''
    citations: list[Citation] = []
    problems: list[str] = []
    for path in sorted(files):
        citation, found = file_citation(path, files[path])
        problems += found
        if citation is not None:
            citations.append(citation)
    return citations, problems


def by_section(citations: list[Citation]) -> dict[str, list[Citation]]:
    '''Each cited section's citations, in the citations' order.'''
    out: dict[str, list[Citation]] = {}
    for citation in citations:
        for sid in citation.ids:
            out.setdefault(sid, []).append(citation)
    return out
