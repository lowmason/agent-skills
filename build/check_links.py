'''Fail on a relative Markdown link whose target is missing.

Usage, from the repository root: python build/check_links.py [<dir> ...]
Scans every *.md file under each <dir> (default: skills). A link is [text](target) or
![alt](target) outside fenced code blocks and inline code spans. A target with a URL
scheme (https:, mailto:) or one that starts with # is skipped; a target's own #anchor
or ?query is dropped before the check, which resolves the target from the linking
file's directory. Prints one line per broken link, then a summary; exits 1 when a
link is broken. A move one directory deeper breaks relative links silently (plan 71),
so this runs as a commit lint.
'''
import os
import re
import sys
from collections.abc import Iterator
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LINK = re.compile(r'!?\[[^\]\n]*\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)')
FENCE = re.compile(r'^\s*(`{3,}|~{3,})(.*)$')
CODE_SPAN = re.compile(r'(`+).+?\1')
SCHEME = re.compile(r'^[a-z][a-z0-9+.-]*:', re.I)


def links(text: str) -> Iterator[tuple[int, str]]:
    '''Yield (line number, target) for each link outside fences and code spans.'''
    fence = ''
    for n, line in enumerate(text.splitlines(), 1):
        m = FENCE.match(line)
        if not fence:
            if m:
                fence = m.group(1)
                continue
        elif m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and not m.group(2).strip():
            fence = ''
            continue
        if fence:
            continue
        for link in LINK.finditer(CODE_SPAN.sub('', line)):
            yield n, link.group(1)


def broken_links(root: Path, dirs: list[Path]) -> tuple[list[str], int]:
    '''Return (one message per broken link, number of relative links checked).'''
    problems, checked = [], 0
    for md in sorted(p for d in dirs for p in (root / d).rglob('*.md')):
        for n, target in links(md.read_text(encoding='utf-8')):
            if SCHEME.match(target) or target.startswith('#'):
                continue
            checked += 1
            path = re.split(r'[#?]', target, maxsplit=1)[0]
            if not (md.parent / path).exists():
                problems.append(f'{md.relative_to(root).as_posix()}:{n}: broken link {target!r}: '
                                f'no file at {Path(os.path.relpath(md.parent / path, root)).as_posix()}')
    return problems, checked


def main(argv: list[str] | None = None) -> int:
    dirs = [Path(a) for a in (sys.argv[1:] if argv is None else argv)] or [Path('skills')]
    problems, checked = broken_links(REPO, dirs)
    for p in problems:
        print(p)
    print(f'{checked} relative link(s) checked, {len(problems)} broken')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
