'''CommonMark-correct fenced-block handling, shared by build/ gates.

An opener is any run of leading spaces, then three or more backticks or three
or more tildes, then the info string. A fence closes only on a line of the same
fence character whose run length is >= the opener's, with nothing else on the
line but whitespace. A body line loses up to the opener's indent in leading
spaces. A naive non-greedy regex closes on the FIRST ``` it sees, which
desynchronizes on nested fences (e.g. a ````markdown fence wrapping a literal
```python fence). All three functions share one scanner, so they agree.
'''
import re
from typing import Iterator, NamedTuple

FENCE_OPEN_RE = re.compile(r'^( *)(`{3,}|~{3,})(.*)$')


class CodeBlock(NamedTuple):
    lang: str
    info: str
    line: int
    code: str


class _Fence(NamedTuple):
    start: int
    end: int | None  # None when the fence is never closed
    info: str
    body: list[str]


def _closes(line: str, char: str, length: int) -> bool:
    stripped = line.strip()
    return stripped.startswith(char * length) and set(stripped) == {char}


def _scan(text: str) -> Iterator[_Fence]:
    '''Yield each outermost fence; an unclosed fence runs to the end.'''
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        m = FENCE_OPEN_RE.match(lines[i])
        if not m:
            i += 1
            continue
        indent, run, info = len(m.group(1)), m.group(2), m.group(3)
        if run[0] == '`' and '`' in info:
            i += 1  # CommonMark: a backtick info string holds no backtick
            continue
        body: list[str] = []
        j = i + 1
        while j < len(lines) and not _closes(lines[j], run[0], len(run)):
            line = lines[j]
            body.append(line[min(indent, len(line) - len(line.lstrip(' '))):])
            j += 1
        yield _Fence(i + 1, j + 1 if j < len(lines) else None, info, body)
        i = j + 1


def strip_fenced_blocks(text: str) -> str:
    '''Remove fenced code blocks, honoring CommonMark fence-matching rules.'''
    lines = text.split('\n')
    drop = fenced_lines(text)
    return '\n'.join(l for n, l in enumerate(lines, start=1) if n not in drop)


def iter_code_blocks(text: str,
                     langs: tuple[str, ...] = ('python', 'py')) -> list[CodeBlock]:
    '''Outermost-level fenced blocks whose info string opens with one of langs.

    Nested fences are content, never blocks: a ```python inside a ````markdown
    wrapper is template text. An unclosed fence is not a block. Returns blocks
    in document order.
    '''
    out: list[CodeBlock] = []
    for fence in _scan(text):
        parts = fence.info.strip().split(None, 1)
        word = parts[0] if parts else ''
        if fence.end is None or word not in langs:
            continue
        rest = parts[1].strip() if len(parts) > 1 else ''
        code = '\n'.join(fence.body) + '\n' if fence.body else ''
        out.append(CodeBlock(word, rest, fence.start, code))
    return out


def fenced_lines(text: str) -> set[int]:
    '''1-based numbers of the lines that open, close, or sit inside a fenced block.

    Same matching rule as strip_fenced_blocks; an unclosed fence runs to the end.
    '''
    n_lines = len(text.split('\n'))
    out: set[int] = set()
    for fence in _scan(text):
        out.update(range(fence.start, (fence.end or n_lines) + 1))
    return out
