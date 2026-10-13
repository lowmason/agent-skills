'''`quotes`: re-grep a verifier's quotes against the files they came from
(drift spec R8.3). A quote counts only when it appears whole within one
line, the method that found 151 of 151 quotes in the 2026-10-03 refresh.
It succeeds the snapshot's check/qcheck.py.'''
from collections.abc import Iterable
from pathlib import Path


class QuoteFiles:
    '''The files under one root that quotes may name, each read once.'''

    def __init__(self, root: Path):
        self.root = root.resolve()
        self._lines: dict[str, list[str] | None] = {}

    def lines(self, name: str) -> list[str] | None:
        '''The file's lines, or None when name leaves the root or is no file.
        Bytes that are not UTF-8 read as U+FFFD, which no quote matches.'''
        if name not in self._lines:
            path = (self.root / name).resolve()
            inside = path.is_relative_to(self.root) and path.is_file()
            self._lines[name] = path.read_text(encoding='utf-8', errors='replace').split('\n') if inside else None
        return self._lines[name]

    def find(self, name: str, quote: str) -> int | None:
        '''The 1-based line of name that holds quote whole, or None. An empty
        quote is never found: it would sit inside every line.'''
        lines = self.lines(name)
        if not quote or lines is None:
            return None
        return next((n for n, line in enumerate(lines, start=1) if quote in line), None)

    def find_any(self, names: Iterable[str], quote: str) -> tuple[str, int] | None:
        '''The first of names, in order, whose line holds quote: (name, line).'''
        for name in names:
            line = self.find(name, quote)
            if line is not None:
                return name, line
        return None


def check_rows(root: Path, rows: Iterable[str]) -> tuple[list[str], bool]:
    '''R8.3: each `file<TAB>quote` row as `FOUND file:line` or `MISSING
    file`, and whether every row was found. Blank rows and `#` comments are
    skipped; a row without a tab has an empty quote, so it is MISSING.'''
    files = QuoteFiles(root)
    out: list[str] = []
    for raw in rows:
        row = raw.rstrip('\n')
        if not row.strip() or row.startswith('#'):
            continue
        name, _, quote = row.partition('\t')
        line = files.find(name, quote)
        out.append(f'MISSING {name}' if line is None else f'FOUND {name}:{line}')
    return out, not any(o.startswith('MISSING') for o in out)
