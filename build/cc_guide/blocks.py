'''Docs pages as hashed blocks (drift spec R3).

A page becomes one block per ATX heading, holding the heading's own text up to
the next heading of any level, plus one block per table row. An MDX page is
first rewritten as the docs site's Markdown export renders it, and the leading
"Documentation Index" blockquote is dropped. Blocks are keyed by heading path
and hashed after normalization; baseline.json stores each key as its hash too
(R2.3). A group watches the blocks its pages' marks and its sections' terms
select.
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
# block_hash and key_hash keep this many hex characters of SHA-256 (R3.5).
HASH_CHARS = 16
HASH_RE = re.compile(rf'[0-9a-f]{{{HASH_CHARS}}}')

FENCE_OPEN_RE = re.compile(r'^[ \t]*(`{3,}|~{3,})')
ATX_RE = re.compile(r'^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$')
LINK_RE = re.compile(r'\]\([^)\n]*\)')
SEPARATOR_RE = re.compile(r'^\|?[ \t]*:?-+:?[ \t]*(?:\|[ \t]*:?-+:?[ \t]*)*\|?$')
CELL_SPLIT_RE = re.compile(r'(?<!\\)\|')

# R3.2's MDX rewrite (owner, 2026-10-20). Until about 14:00 on 2026-10-20 the
# docs site exported every page as MDX; since then code.claude.com exports
# Markdown, while platform.claude.com and the older snapshots stay MDX. These
# components are rewritten as the Markdown export renders them: a callout or a
# QUOTED container becomes a blockquote under a marker or title line, a TITLED
# one a bold title line, and an UNWRAPPED one leaves only its contents. Any
# other tag stays as it is, so a new component shows as drift.
CALLOUTS = {'Note': 'NOTE', 'Info': 'NOTE', 'Tip': 'TIP', 'Warning': 'WARNING', 'Danger': 'CAUTION'}
QUOTED = {'Accordion', 'Card', *CALLOUTS}
TITLED = {'Tab', 'Step'}
UNWRAPPED = {'Tabs', 'Steps', 'CardGroup', 'AccordionGroup', 'CodeGroup', 'Frame', 'Callout'}
COMPONENTS = QUOTED | TITLED | UNWRAPPED
TAG_OPEN_RE = re.compile(r'<([A-Z][A-Za-z]*)\b([^>]*)>')
TAG_CLOSE_RE = re.compile(r'</([A-Z][A-Za-z]*)>$')
SELF_CLOSING_RE = re.compile(r'<([A-Z][A-Za-z]*)\b[^>]*/>$')
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')
HTML_HEADING_RE = re.compile(r'<h([1-6])\b[^>]*>(.*?)(?:</h\1>)?$')
MEDIA_RE = re.compile(r'<(img|video)\b.*?/?>$')
# The dark-mode copy of a light and dark image or video pair.
DARK_RE = re.compile(r'className="[^"]*\bdark:block\b')
MEDIA_STYLE_RE = re.compile(r'\s(?:className|data-path)="[^"]*"|\sstyle=\{\{.*?\}\}')
ANCHOR_RE = re.compile(r'<(?:span|a) id="[^"]*"\s*/>')
BREAK_RE = re.compile(r'<br\s*/?>')
DIV_RE = re.compile(r'</?div\b[^>]*>$')
EXPORT_RE = re.compile(r'export const (\w+)')
EXPORT_END = ('}', '};')


class _Opener(NamedTuple):
    char: str     # ` or ~
    length: int   # the opening run's length
    line: int     # 0-based index of the opening line
    info: str     # the info string


def opens_fence(line: str, i: int) -> _Opener | None:
    '''The fence line i opens (R3.1), or None: three or more backticks or
    tildes at any indentation. As in CommonMark, a backtick opener's info
    string holds no backtick.'''
    m = FENCE_OPEN_RE.match(line)
    if not m:
        return None
    info = line[m.end():]
    if m.group(1)[0] == '`' and '`' in info:
        return None
    return _Opener(m.group(1)[0], len(m.group(1)), i, info.strip())


def closes_fence(fence: _Opener, line: str) -> bool:
    '''R3.1: a line holding nothing but a run of the fence's character at
    least as long as its opener.'''
    s = line.strip()
    return bool(s) and set(s) == {fence.char} and len(s) >= fence.length


def fence_spans(lines: list[str]) -> list[tuple[int, int | None, str]]:
    '''Each fenced code block as (open, close, info): 0-based line indexes,
    close None when the fence never closes (R3.1).'''
    spans: list[tuple[int, int | None, str]] = []
    fence: _Opener | None = None
    for i, line in enumerate(lines):
        if fence is None:
            fence = opens_fence(line, i)
        elif closes_fence(fence, line):
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


class _MdxRewrite:
    '''One pass of R3.2's MDX rewrite over a page's lines; as_markdown runs it.'''

    def __init__(self, lines: list[str]):
        self.lines = lines
        self.out: list[tuple[str, int]] = []
        self.stack: list[list] = []      # the open components, as [tag, steps numbered so far]
        self.exported: set[str] = set()  # the components the page's scripts define

    def put(self, text: str, src: int) -> None:
        '''One output line, quoted once for each open QUOTED component.'''
        depth = sum(1 for tag, _ in self.stack if tag in QUOTED)
        self.out.append((('> ' * depth + text).rstrip(), src))

    def keep(self, line: str, src: int) -> None:
        '''A line no rule rewrites: unchanged outside every component, else
        dedented into it.'''
        if self.stack:
            self.put(line.strip(), src)
        else:
            self.out.append((line, src))

    def open(self, tag: str, attrs: dict[str, str], src: int) -> None:
        title = attrs.get('title', '')
        if tag == 'Step':
            steps = next((e for e in reversed(self.stack) if e[0] == 'Steps'), None)
            if steps is not None:
                steps[1] += 1
            title = f'{steps[1] if steps else 1}. {title}'
        if tag in TITLED:
            self.put(f'**{title}**', src)
        self.stack.append([tag, 0])
        if tag in CALLOUTS:
            self.put(f'[!{CALLOUTS[tag]}]', src)
        elif tag == 'Card' and 'href' in attrs:
            self.put(f'**[{title}]({attrs["href"]})**', src)
        elif tag in QUOTED:
            self.put(f'**{title}**', src)
        if tag in QUOTED:
            self.put('', src)

    def close(self, tag: str) -> None:
        if any(e[0] == tag for e in self.stack):
            while self.stack.pop()[0] != tag:
                pass

    def export_end(self, i: int) -> int | None:
        '''The last line of the script an `export const` line i opens: the
        line itself when it ends in `;`, else the next `}` or `};` line.'''
        if self.lines[i].rstrip().endswith(';'):
            return i
        return next((j for j in range(i + 1, len(self.lines)) if self.lines[j].rstrip() in EXPORT_END), None)

    def heading(self, level: str, title: str, i: int) -> int:
        '''Puts an HTML heading as an ATX one; returns the next line to read.
        A heading whose title is not on its own line takes the lines up to
        its closing tag.'''
        nxt = i + 1
        if not title:
            parts = []
            while nxt < len(self.lines) and not self.lines[nxt].strip().startswith(f'</h{level}'):
                parts.append(self.lines[nxt].strip())
                nxt += 1
            nxt += 1
            title = ' '.join(p for p in parts if p)
        self.put('#' * int(level) + ' ' + title, i)
        return nxt

    def media(self, text: str, src: int) -> None:
        '''An image as Markdown, a video without its styling, and neither
        when it is the dark-mode copy.'''
        if DARK_RE.search(text):
            return
        if text.startswith('<img'):
            attrs = dict(ATTR_RE.findall(text))
            alt = attrs.get('alt', '').replace('*', '\\*')
            self.put(f'![{alt}]({attrs.get("src", "")})', src)
        else:
            self.put(MEDIA_STYLE_RE.sub('', text), src)

    def components(self, line: str, text: str, src: int, rewritten: bool) -> None:
        '''A line's opening and closing component tags, and the text between.'''
        tagged = False
        while (o := TAG_OPEN_RE.match(text)) and o.group(1) in COMPONENTS:
            tag = o.group(1)
            self.open(tag, dict(ATTR_RE.findall(o.group(2))), src)
            if o.group(2).rstrip().endswith('/'):
                self.close(tag)
            text, tagged = text[o.end():].strip(), True
        closed = []
        while (c := TAG_CLOSE_RE.search(text)) and c.group(1) in COMPONENTS:
            closed.append(c.group(1))
            text, tagged = text[:c.start()].strip(), True
        if text and (tagged or rewritten):
            self.put(text, src)
        elif not tagged:
            self.keep(line, src)
        for tag in closed:
            self.close(tag)

    def run(self) -> list[tuple[str, int]]:
        fence: _Opener | None = None
        i = 0
        while i < len(self.lines):
            src, line = i, self.lines[i]
            i += 1
            if fence is not None:
                self.keep(line, src)
                if closes_fence(fence, line):
                    fence = None
                continue
            fence = opens_fence(line, src)
            if fence is not None:
                self.keep(line, src)
                continue
            script = EXPORT_RE.match(line)
            end = None if script is None else self.export_end(src)
            if end is not None:
                self.exported.add(script.group(1))
                i = end + 1
                continue
            s = line.strip()
            text = BREAK_RE.sub(' ', ANCHOR_RE.sub('', s)).strip()
            if s and not text:
                continue
            h = HTML_HEADING_RE.match(text)
            used = SELF_CLOSING_RE.match(text)
            if h:
                i = self.heading(h.group(1), h.group(2).strip(), src)
            elif MEDIA_RE.match(text):
                self.media(text, src)
            elif not (DIV_RE.match(text) or (used and used.group(1) in self.exported)):
                self.components(line, text, src, text != s)
        return self.out


def as_markdown(lines: list[str]) -> list[tuple[str, int]]:
    '''R3.2: a page's MDX components rewritten as the docs site's Markdown
    export renders them, each output line paired with the 0-based index of
    the line it came from. A line outside every component that no rule
    rewrites comes back unchanged, so a Markdown page comes back line for
    line. Fenced code is never read as MDX: inside a component it is only
    dedented and, in a QUOTED one, quoted. The rules:
    - a callout opens a blockquote under its `[!KIND]` marker, an Accordion
      under its bold title, a Card under its bold title linked to its href;
    - a Tab becomes its bold title, a Step its bold, numbered title;
    - an UNWRAPPED component, a `<div>` line and an anchor tag leave nothing
      but their contents, and a `<br />` becomes a space;
    - an `<hN>` heading becomes an ATX heading of level N;
    - an image becomes `![alt](src)`, a `*` in alt escaped; a video loses its
      styling; the dark-mode copy of a light and dark pair goes;
    - an `export const` script goes, and so does a self-closing tag of a
      component it defines.'''
    return _MdxRewrite(lines).run()


def normalize(text: str) -> str:
    '''R3.5 steps 1-3: empty every link target, collapse whitespace runs,
    strip each line, and drop empty lines.'''
    lines = (' '.join(line.split()) for line in LINK_RE.sub(']()', text).split('\n'))
    return '\n'.join(line for line in lines if line)


def block_hash(text: str) -> str:
    '''R3.5 step 4: the first 16 hex characters of SHA-256 over the
    normalized text, as UTF-8.'''
    return hashlib.sha256(normalize(text).encode('utf-8')).hexdigest()[:HASH_CHARS]


def key_hash(key: str) -> str:
    '''A block key as baseline.json stores it (R2.3), so the repo holds no
    docs text: R3.5 step 4's hash over the key as it is, since key_part has
    already normalized it.'''
    return hashlib.sha256(key.encode('utf-8')).hexdigest()[:HASH_CHARS]


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


class Block(NamedTuple):
    key: str
    text: str               # normalized (R3.5 steps 1-3)
    lines: tuple[int, ...]  # 0-based indexes of the page lines it was cut from, in order


def cut_page(text: str, rewrite_mdx: bool = True) -> list[Block]:
    '''A docs page's blocks (R3.2-R3.4), in page order. A heading's block
    runs to the next heading of any level, less its table rows, which become
    blocks keyed by the heading path and the row's first cell; header and
    separator rows stay in the heading's block. Text before the first heading
    is the (intro) block, dropped when empty. A repeated key gets an ordinal
    suffix (#2, #3, ...). rewrite_mdx=False skips R3.2's MDX rewrite, cutting
    the page as the parser before it did, for `baseline rehash`.'''
    page = text.split('\n')
    pairs = as_markdown(page) if rewrite_mdx else list(zip(page, range(len(page))))
    lines = strip_preamble([line for line, _ in pairs])
    origin = [src for _, src in pairs[len(pairs) - len(lines):]]
    fenced = fenced_lines(lines)
    current: list[int] = []
    raw: list[tuple[str, list[int]]] = [(INTRO, current)]
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
                current = [i]
                raw.append((block_key, current))
                i += 1
                continue
            if is_table_start(lines, i, fenced):
                current.extend((i, i + 1))
                i += 2
                while i < len(lines) and i not in fenced and lines[i].lstrip().startswith('|'):
                    cell = key_part(first_cell(lines[i])) or EMPTY_CELL
                    raw.append((block_key + SEP + cell, [i]))
                    i += 1
                continue
        current.append(i)
        i += 1
    out: list[Block] = []
    taken: set[str] = set()
    seen: dict[str, int] = {}
    for key, indexes in raw:
        body = normalize('\n'.join(lines[j] for j in indexes))
        if key == INTRO and not body:
            continue
        n = seen.get(key, 0) + 1
        final = key if n == 1 else f'{key}#{n}'
        while final in taken:
            n += 1
            final = f'{key}#{n}'
        seen[key] = n
        taken.add(final)
        out.append(Block(final, body, tuple(origin[j] for j in indexes)))
    return out


def page_blocks(text: str) -> dict[str, str]:
    '''A docs page's blocks (cut_page) as key -> normalized text, in page
    order.'''
    return {b.key: b.text for b in cut_page(text)}


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
