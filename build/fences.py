'''CommonMark-correct fenced-block handling, shared by build/ gates.

A fence closes only on a line of the same fence character whose run length is
>= the opener's, with nothing else on the line but whitespace. A naive
non-greedy regex closes on the FIRST ``` it sees, which desynchronizes on
nested fences (e.g. a ````markdown fence wrapping a literal ```python fence).
'''
import re
from typing import NamedTuple

FENCE_OPEN_RE = re.compile(r'^(`{3,})(.*)$')


class CodeBlock(NamedTuple):
    lang: str
    info: str
    line: int
    code: str


def strip_fenced_blocks(text: str) -> str:
    '''Remove fenced code blocks, honoring CommonMark fence-matching rules.'''
    kept: list[str] = []
    open_len: int | None = None
    for line in text.split('\n'):
        if open_len is None:
            m = FENCE_OPEN_RE.match(line)
            if m:
                open_len = len(m.group(1))
                continue
            kept.append(line)
        else:
            stripped = line.strip()
            if stripped.startswith('`' * open_len) and set(stripped) == {'`'}:
                open_len = None
    return '\n'.join(kept)


def iter_code_blocks(text: str,
                     langs: tuple[str, ...] = ('python', 'py')) -> list[CodeBlock]:
    '''Outermost-level fenced blocks whose info string opens with one of langs.

    Nested fences are content, never blocks: a ```python inside a ````markdown
    wrapper is template text. Returns blocks in document order.
    '''
    out: list[CodeBlock] = []
    open_len: int | None = None
    info_word = ''
    info_rest = ''
    start = 0
    body: list[str] = []
    for i, line in enumerate(text.split('\n'), start=1):
        if open_len is None:
            m = FENCE_OPEN_RE.match(line)
            if m:
                open_len = len(m.group(1))
                parts = m.group(2).strip().split(None, 1)
                info_word = parts[0] if parts else ''
                info_rest = parts[1].strip() if len(parts) > 1 else ''
                start = i
                body = []
            continue
        stripped = line.strip()
        if stripped.startswith('`' * open_len) and set(stripped) == {'`'}:
            if info_word in langs:
                out.append(CodeBlock(info_word, info_rest, start,
                                     '\n'.join(body) + '\n' if body else ''))
            open_len = None
            continue
        body.append(line)
    return out
