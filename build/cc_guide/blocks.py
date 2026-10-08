'''Docs pages as hashed blocks (drift spec R3).

A page becomes one block per ATX heading, holding the heading's own text up to
the next heading of any level, plus one block per table row. The leading
"Documentation Index" blockquote is dropped first. Blocks are keyed by heading
path and hashed after normalization; baseline.json stores each key as its
hash too (R2.3). A group watches the blocks its pages' marks and its sections'
terms select.
'''
import hashlib
import re
from collections.abc import Iterable
from typing import NamedTuple

SEP = ' › '
INTRO = '(intro)'
EMPTY_CELL = '(row)'
# Each key component is capped like R3.6's terms, which keeps printed keys
# short. baseline.json commits only each key's key_hash() (R2.3).
KEY_PART_MAX = 60

FENCE_OPEN_RE = re.compile(r'^[ \t]*(`{3,}|~{3,})')
ATX_RE = re.compile(r'^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$')
LINK_RE = re.compile(r'\]\([^)\n]*\)')
SEPARATOR_RE = re.compile(r'^\|?[ \t]*:?-+:?[ \t]*(?:\|[ \t]*:?-+:?[ \t]*)*\|?$')
CELL_SPLIT_RE = re.compile(r'(?<!\\)\|')


class _Opener(NamedTuple):
    char: str     # ` or ~
    length: int   # the opening run's length
    line: int     # 0-based index of the opening line
    info: str     # the info string


def fence_spans(lines: list[str]) -> list[tuple[int, int | None, str]]:
    '''Each fenced code block as (open, close, info): 0-based line indexes,
    close None when the fence never closes (R3.1). A fence opens on three or
    more backticks or tildes at any indentation, and closes only on a line
    holding nothing but a run of the same character at least as long. As in
    CommonMark, a backtick opener's info string holds no backtick.'''
    spans: list[tuple[int, int | None, str]] = []
    fence: _Opener | None = None
    for i, line in enumerate(lines):
        if fence is None:
            m = FENCE_OPEN_RE.match(line)
            info = line[m.end():] if m else ''
            if m and not (m.group(1)[0] == '`' and '`' in info):
                fence = _Opener(m.group(1)[0], len(m.group(1)), i, info.strip())
            continue
        s = line.strip()
        if s and set(s) == {fence.char} and len(s) >= fence.length:
            spans.append((fence.line, i, fence.info))
            fence = None
    if fence is not None:
        spans.append((fence.line, None, fence.info))
    return spans


def fenced_lines(lines: list[str]) -> set[int]:
    '''0-based indexes of the lines that open, close or sit inside a fenced
    code block. An unclosed fence runs to the end.'''
    last = len(lines) - 1
    return {i for start, close, _ in fence_spans(lines)
            for i in range(start, (last if close is None else close) + 1)}


def normalize(text: str) -> str:
    '''R3.5 steps 1-3: empty every link target, collapse whitespace runs,
    strip each line, and drop empty lines.'''
    lines = (' '.join(line.split()) for line in LINK_RE.sub(']()', text).split('\n'))
    return '\n'.join(line for line in lines if line)


def block_hash(text: str) -> str:
    '''R3.5 step 4: the first 16 hex characters of SHA-256 over the
    normalized text, as UTF-8.'''
    return hashlib.sha256(normalize(text).encode('utf-8')).hexdigest()[:16]


def key_hash(key: str) -> str:
    '''A block key as baseline.json stores it (R2.3), so the repo holds no
    docs text: R3.5 step 4's hash over the key as it is, since key_part has
    already normalized it.'''
    return hashlib.sha256(key.encode('utf-8')).hexdigest()[:16]


def key_names(keys: Iterable[str]) -> dict[str, str]:
    '''Key hash -> key over `keys`, to name baselined blocks.'''
    return {key_hash(k): k for k in keys}


def key_part(text: str) -> str:
    '''One component of a block key: R3.5's link and whitespace steps, cut to
    KEY_PART_MAX characters.'''
    part = ' '.join(LINK_RE.sub(']()', text).split())
    return part if len(part) <= KEY_PART_MAX else part[:KEY_PART_MAX - 1] + '…'


def strip_preamble(lines: list[str]) -> list[str]:
    '''R3.2: drop the leading "Documentation Index" blockquote, the `>` lines
    at the top of a page that point to llms.txt.'''
    n = 0
    while n < len(lines) and lines[n].startswith('>'):
        n += 1
    if n and any('llms.txt' in line for line in lines[:n]):
        return lines[n:]
    return lines


def first_cell(row: str) -> str:
    '''A table row's first cell, split on unescaped pipes only.'''
    s = row.strip()
    if s.startswith('|'):
        s = s[1:]
    return CELL_SPLIT_RE.split(s, 1)[0].strip()


def is_table_start(lines: list[str], i: int, fenced: set[int]) -> bool:
    '''A header row: a `|` line followed by a separator row.'''
    return (i + 1 < len(lines) and i + 1 not in fenced
            and lines[i].lstrip().startswith('|') and '|' in lines[i + 1]
            and SEPARATOR_RE.match(lines[i + 1].strip()) is not None)


def page_blocks(text: str) -> dict[str, str]:
    '''A docs page's blocks (R3.2-R3.4) as key -> normalized text, in page
    order. A heading's block runs to the next heading of any level, less its
    table rows, which become blocks keyed by the heading path and the row's
    first cell; header and separator rows stay in the heading's block. Text
    before the first heading is the (intro) block, dropped when empty. A
    repeated key gets an ordinal suffix (#2, #3, ...).'''
    lines = strip_preamble(text.split('\n'))
    fenced = fenced_lines(lines)
    current: list[str] = []
    raw: list[tuple[str, list[str]]] = [(INTRO, current)]
    path: list[tuple[int, str]] = []
    block_key = INTRO
    i = 0
    while i < len(lines):
        line = lines[i]
        if i not in fenced:
            m = ATX_RE.match(line)
            if m:
                level = len(m.group(1))
                path = [p for p in path if p[0] < level] + [(level, key_part(m.group(2) or ''))]
                block_key = SEP.join(p[1] for p in path)
                current = [line]
                raw.append((block_key, current))
                i += 1
                continue
            if is_table_start(lines, i, fenced):
                current.extend(lines[i:i + 2])
                i += 2
                while i < len(lines) and i not in fenced and lines[i].lstrip().startswith('|'):
                    cell = key_part(first_cell(lines[i])) or EMPTY_CELL
                    raw.append((block_key + SEP + cell, [lines[i]]))
                    i += 1
                continue
        current.append(line)
        i += 1
    blocks: dict[str, str] = {}
    seen: dict[str, int] = {}
    for key, block_lines in raw:
        body = normalize('\n'.join(block_lines))
        if key == INTRO and not body:
            continue
        n = seen.get(key, 0) + 1
        final = key if n == 1 else f'{key}#{n}'
        while final in blocks:
            n += 1
            final = f'{key}#{n}'
        seen[key] = n
        blocks[final] = body
    return blocks


def contains_term(key: str, text: str, terms: Iterable[str]) -> bool:
    '''Case-sensitive substring match of any term in a block's key or text.'''
    return any(t in key or t in text for t in terms)


def select(blocks: dict[str, str], mark: str, terms: set[str]) -> list[str]:
    '''R3.7: the keys a group watches on one page. Every block of an `all`
    page counts; on a `terms` page, a block counts when its key or normalized
    text contains one of the group's terms.'''
    if mark == 'all':
        return list(blocks)
    return [k for k, text in blocks.items() if contains_term(k, text, terms)]


def candidates(key: str, text: str, section_terms: dict[str, set[str]]) -> list[str]:
    '''R3.7: the group's sections whose terms the block contains, in group
    order, or every section of the group when none match.'''
    hits = [sid for sid, terms in section_terms.items() if contains_term(key, text, terms)]
    return hits or list(section_terms)
