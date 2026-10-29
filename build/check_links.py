'''Fail on a relative Markdown link whose target is missing.

Usage, from the repository root: python build/check_links.py [<dir> ...]
Scans every *.md file under each <dir> (default: skills). A link is [text](target) or
![alt](target), with an optional title in double quotes, single quotes or parentheses,
or a reference definition [label]: target, all outside fenced code blocks and inline
code spans. A target with a URL scheme (https:, mailto:) or one that starts with # is
skipped; a target's own #anchor or ?query is dropped and %XX escapes are decoded before
the check, which resolves the target from the linking file's directory and compares
each name case-sensitively, as Linux CI does, even on a case-insensitive Mac. Prints
one line per broken link, then a summary; exits 1 when a link is broken or no link was
checked, and 2 when a named directory does not exist. A move one directory deeper
breaks relative links silently (plan 71), so this runs as a commit lint.
'''
import os
import re
import sys
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parent.parent
TITLE = r'''(?:\s+(?:"[^"]*"|'[^']*'|\([^)]*\)))?'''
LINK = re.compile(r'!?\[[^\]\n]*\]\(\s*<?([^)\s>]+)>?' + TITLE + r'\s*\)')
REF_DEF = re.compile(r'^ {0,3}\[(?!\^)[^\]\n]+\]:\s*<?([^\s>]+)>?' + TITLE + r'\s*$')
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
        line = CODE_SPAN.sub('', line)
        for link in LINK.finditer(line):
            yield n, link.group(1)
        if ref := REF_DEF.match(line):
            yield n, ref.group(1)


def case_differs(root: Path, target: Path) -> bool:
    '''True when an existing target's path below root differs in case from the names on disk.'''
    try:
        parts = target.relative_to(root).parts
    except ValueError:
        return False
    parent = root
    for name in parts:
        if name not in os.listdir(parent):
            return True
        parent = parent / name
    return False


def broken_links(root: Path, dirs: list[Path]) -> tuple[list[str], int]:
    '''Return (one message per broken link, number of relative links checked).'''
    problems, checked = [], 0
    for md in sorted(p for d in dirs for p in (root / d).rglob('*.md')):
        for n, target in links(md.read_text(encoding='utf-8')):
            if SCHEME.match(target) or target.startswith('#'):
                continue
            checked += 1
            path = Path(os.path.normpath(md.parent / unquote(re.split(r'[#?]', target, maxsplit=1)[0])))
            if path.exists() and not case_differs(root, path):
                continue
            note = ' (a name differs in case)' if path.exists() else ''
            problems.append(f'{md.relative_to(root).as_posix()}:{n}: broken link {target!r}: '
                            f'no file at {Path(os.path.relpath(path, root)).as_posix()}{note}')
    return problems, checked


def main(argv: list[str] | None = None) -> int:
    dirs = [Path(a) for a in (sys.argv[1:] if argv is None else argv)] or [Path('skills')]
    missing = [d for d in dirs if not (REPO / d).is_dir()]
    if missing:
        for d in missing:
            print(f'no such directory: {d.as_posix()}')
        return 2
    problems, checked = broken_links(REPO, dirs)
    for p in problems:
        print(p)
    if not checked:
        print('0 relative link(s) checked: nothing to check')
        return 1
    print(f'{checked} relative link(s) checked, {len(problems)} broken')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
