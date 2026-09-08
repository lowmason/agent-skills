'''Snippet gate for skill documentation (Gate A pattern).

Tier 1 (default) parses every fenced python block with ast.parse. It catches
syntax that shipped broken; it does NOT catch API drift.

Scope honesty, since the motivating backlog item overstates it: of audit
12-audit_7_20_26's three findings, only C1 is reachable by executing a
snippet. D2 lived in markdown bullets and needs the --api tier. C2 was a
lexical contradiction between two prose files and no mechanical gate catches
it. Do not describe this gate as covering all three.

Run: uv run --python 3.13 python build/check_snippets.py skills/bayesian-workflow/
Exit 0 if clean; exit 1 with one line per violation.
'''
import argparse
import ast
import sys
from pathlib import Path

from fences import CodeBlock, iter_code_blocks  # noqa: F401  (re-exported)

NORUN = 'norun'


def _iter_md(paths):
    '''Expand directory arguments to every .md beneath them, recursively.'''
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            yield from sorted(p.rglob('*.md'))
        elif p.suffix == '.md':
            yield p


def parse_errors(path: Path) -> list[str]:
    '''Return one message per block that fails ast.parse (empty == clean).'''
    out = []
    for block in iter_code_blocks(path.read_text()):
        try:
            ast.parse(block.code)
        except SyntaxError as e:
            out.append(f'{path}:{block.line}: SyntaxError: {e.msg} '
                       f'(block line {e.lineno})')
    return out


def is_exempt(block) -> bool:
    '''True when the fence info string opts the block out of execution.

    Shape: ```python norun <reason>. Exempt from EXECUTION only -- parsing
    still applies. The reason is required (test_every_norun_marker_carries_a
    _reason pins it) so the exemption list stays auditable.
    '''
    return block.info.split(None, 1)[:1] == [NORUN]


def exempt_report(path: Path) -> list[str]:
    '''Advisory lines naming every block excluded from execution.'''
    return [f'{path}:{b.line}: not executed: {b.info[len(NORUN):].strip()}'
            for b in iter_code_blocks(path.read_text()) if is_exempt(b)]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('paths', nargs='+', help='.md files or directories')
    args = ap.parse_args(argv)
    failures = [e for md in _iter_md(args.paths) for e in parse_errors(md)]
    for f in failures:
        print(f)
    for md in _iter_md(args.paths):
        for line in exempt_report(md):
            print(f'WARN {line}', file=sys.stderr)
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
