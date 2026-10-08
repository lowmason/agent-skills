'''The guide: its anchored sections, their text hashes and terms, and the
stamp region (drift spec R1, R2.3, R3.6).'''
import hashlib
import re
from typing import NamedTuple

from blocks import fenced_lines
from docs import version_key

# A ## or ### ATX heading. The guide's sections are exactly these (R1.1).
HEADING_RE = re.compile(r'^(#{2,3})[ \t]')
ANCHOR_RE = re.compile(r'^<!-- cc: ([a-z0-9-]+(?:\.[a-z0-9-]+)+) -->$')
# Anything meant as an anchor, well-formed or not. The stamp markers do not
# match: `cc` must be followed by `:`.
ANCHOR_LIKE_RE = re.compile(r'^<!--\s*cc:')
STAMP_OPEN = '<!-- cc-guide:stamp -->'
STAMP_CLOSE = '<!-- /cc-guide:stamp -->'
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
