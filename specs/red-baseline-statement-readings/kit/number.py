'''Number a spec's sentences, S1 to Sn, for the statement-readings probe (plan 83, PD4).

Usage, from the repository root:
  uv run python <kit>/number.py <spec.md>   prints the numbered text
  uv run python <kit>/number.py selftest    checks the rules on a fixed sample
One line-by-line scan, fence-aware as extract.py is: a heading or a table row inside a fence is text.
1. A heading line is no sentence. It becomes the `heading` of the sentences below it.
2. A fenced block is one sentence, its fence lines included.
3. A table row is one sentence, the header row included. The separator row is none.
4. Other lines join with single spaces into a block, which ends at a blank line, a heading, a fence, a table
   row or a new list item. A block splits after `.`, `!` or `?`, and any closing `*`, backtick, `"`, `'`, `)`
   or `]`, when whitespace and then a character other than a lowercase letter follow.
5. A block does not split after a label such as `R2.1.`, `D3.` or `A11.`, after a bold run-in title that opens
   the block, alone or after its label, after `e.g.`, `i.e.`, `etc.` or `vs.`, or after a list marker such as
   `1.` at the start of the block.
'''
import re
import sys
from dataclasses import dataclass

FENCE = '`' * 3
FENCE_RE = re.compile(r'^\s*(`{3,}|~{3,})(.*)$')
HEADING_RE = re.compile(r'^#{1,6}\s')
LIST_ITEM_RE = re.compile(r'^\s*(?:[-*+]|\d+[.)])\s+')
SEPARATOR_RE = re.compile(r'^\|?(?:\s*:?-+:?\s*\|)+\s*(?::?-+:?\s*)?$')
SPLIT_RE = re.compile(r'[.!?][*`"\')\]]*(?=\s+[^a-z\s])')
LABEL_RE = re.compile(r'(?:^|[\s(*])[A-Z]+\d+(?:\.\d+)*\.$')
ABBREVIATIONS = ('e.g.', 'i.e.', 'etc.', 'vs.')
OPENING_RE = re.compile(r'^(?:(?:[-*+]|\d+[.)])\s+)?(?:[A-Z]+\d+(?:\.\d+)*\.?\s+)?(?:\*\*[^*]+\*\*)?')
LIST_MARKER_RE = re.compile(r'^\d+[.)]')
QUOTES = '`\'"‘’“”*'
DASHES = {'–': '-', '—': '-'}


@dataclass(frozen=True)
class Sentence:
    n: int
    heading: str
    text: str
    lines: tuple[int, int]


def flatten(text: str) -> str:
    '''Lowercase, en and em dashes to `-`, backticks, quote marks and `*` removed, whitespace collapsed.'''
    text = text.lower()
    for dash, plain in DASHES.items():
        text = text.replace(dash, plain)
    text = ''.join(ch for ch in text if ch not in QUOTES)
    return ' '.join(text.split())


def _protected(block: str, end: int) -> bool:
    '''True when a split candidate that ends at `end` falls under PD4 rule 5.'''
    head = block[:end].rstrip('*`"\')]')
    if LABEL_RE.search(head):
        return True
    if any(head.endswith(a) and (len(head) == len(a) or not head[-len(a) - 1].isalnum()) for a in ABBREVIATIONS):
        return True
    opening = OPENING_RE.match(block)
    if opening and opening.group(0) and end <= opening.end():
        return True
    marker = LIST_MARKER_RE.match(block)
    return bool(marker and end == marker.end())


def _split(block: str) -> list[tuple[int, int]]:
    '''The (start, end) character spans of the block's sentences.'''
    spans, start = [], 0
    for match in SPLIT_RE.finditer(block):
        if _protected(block, match.end()):
            continue
        spans.append((start, match.end()))
        start = match.end()
        while start < len(block) and block[start].isspace():
            start += 1
    if block[start:].strip():
        spans.append((start, len(block)))
    return spans


def _line_at(offsets: list[tuple[int, int]], pos: int) -> int:
    '''The source line (1-based) of character `pos` in a joined block.'''
    line = offsets[0][1]
    for start, number in offsets:
        if start <= pos:
            line = number
    return line


def number(text: str) -> list[Sentence]:
    '''The spec's sentences, in order (PD4). The same text always gives the same sentences.'''
    lines = text.split('\n')
    found: list[tuple[str, str, tuple[int, int]]] = []
    heading = ''
    block: list[tuple[int, str]] = []

    def flush() -> None:
        if not block:
            return
        joined, offsets = '', []
        for number_, content in block:
            if joined:
                joined += ' '
            offsets.append((len(joined), number_))
            joined += content
        for start, end in _split(joined):
            found.append((heading, joined[start:end].strip(),
                          (_line_at(offsets, start), _line_at(offsets, end - 1))))
        block.clear()

    i = 0
    while i < len(lines):
        line = lines[i]
        fence = FENCE_RE.match(line)
        if fence:
            flush()
            opener, start = fence.group(1), i
            i += 1
            while i < len(lines):
                close = FENCE_RE.match(lines[i])
                if close and close.group(1)[0] == opener[0] and len(close.group(1)) >= len(opener) \
                        and not close.group(2).strip():
                    break
                i += 1
            end = min(i, len(lines) - 1)
            found.append((heading, '\n'.join(lines[start:end + 1]), (start + 1, end + 1)))
        elif HEADING_RE.match(line):
            flush()
            heading = line.rstrip()
        elif not line.strip():
            flush()
        elif line.lstrip().startswith('|'):
            flush()
            if not SEPARATOR_RE.match(line.strip()):
                found.append((heading, line.strip(), (i + 1, i + 1)))
        else:
            if LIST_ITEM_RE.match(line):
                flush()
            block.append((i + 1, line.strip()))
        i += 1
    flush()
    return [Sentence(n, h, t, span) for n, (h, t, span) in enumerate(found, 1)]


def numbered_text(sentences: list[Sentence]) -> str:
    '''Each heading line once, where it changes, then one `S<n>. <text>` item for each sentence.'''
    out, heading = [], None
    for s in sentences:
        if s.heading != heading:
            heading = s.heading
            if heading:
                out.extend(['', heading] if out else [heading])
        out.append(f'S{s.n}. {s.text}')
    return ''.join(f'{line}\n' for line in out)


SAMPLE = '\n'.join([
    '### R2. Synced outputs', '',
    'The first sentence wraps', 'over two lines. The second', 'ends here.', '',
    '| Key | Default |', '|---|---|', "| `pythons` | `['3.13']` |", '',
    f'{FENCE}toml', '[python]', "dev = '3.13'", FENCE, '',
    'R2.1. **`sync`.** It writes three files.', '',
    'Floors cover runtime backends (e.g. `h5netcdf` for NetCDF) as well.', '',
    '1. `uv run` respects the cutoff. It gave 0.12.0.'])


def selftest() -> None:
    s = number(SAMPLE)
    assert [x.text for x in s] == [
        'The first sentence wraps over two lines.', 'The second ends here.',
        '| Key | Default |', "| `pythons` | `['3.13']` |", f"{FENCE}toml\n[python]\ndev = '3.13'\n{FENCE}",
        'R2.1. **`sync`.** It writes three files.',
        'Floors cover runtime backends (e.g. `h5netcdf` for NetCDF) as well.',
        '1. `uv run` respects the cutoff.', 'It gave 0.12.0.'], [x.text for x in s]
    assert [x.lines for x in s[:2]] == [(3, 4), (4, 5)] and s[4].lines == (11, 14), [x.lines for x in s]
    assert {x.heading for x in s} == {'### R2. Synced outputs'}
    assert number(SAMPLE) == s
    assert flatten('A “Quoted” – `x`  **y**') == 'a quoted - x y'
    print('number selftest ok')


def main() -> None:
    args = sys.argv[1:]
    if args == ['selftest']:
        selftest()
    elif len(args) == 1:
        with open(args[0], encoding='utf-8') as f:
            print(numbered_text(number(f.read())), end='')
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
