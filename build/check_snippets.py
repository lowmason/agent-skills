'''Snippet gate for skill documentation (Gate A pattern).

Tier 1 (default) parses every fenced python block with ast.parse. It catches
syntax that shipped broken; it does NOT catch API drift.

Scope honesty, since the motivating backlog item overstates it. Of audit
12-audit_7_20_26's three findings this gate reaches exactly ONE: C1, whose
recipe raises when executed (--run). C2 was a lexical contradiction between
two prose files. D2 was an `az.compare` output column named `warning` -- a
DOTLESS field name in prose, which TICK_NAME_RE cannot match, on a call that
resolves fine. Neither is mechanically reachable, by --api or anything else
here. Do not describe this gate as covering all three, and do not describe
--api as 'the tier that would have caught D2' -- it would not have.

What --api does catch is the adjacent class: a dotted library path that no
longer resolves. On its first run against skills/bayesian-workflow/ it found
SKILL.md naming `numpyro.infer.config_enumerate`, which lives in
numpyro.contrib.funsor and has never been on numpyro.infer.

Run: uv run --python 3.13 python build/check_snippets.py skills/bayesian-workflow/
Exit 0 if clean; exit 1 with one line per violation.
'''
import argparse
import ast
import importlib
import re
import sys
from pathlib import Path

from fences import (CodeBlock, iter_code_blocks,  # noqa: F401  (re-exported)
                    strip_fenced_blocks)

NORUN = 'norun'
TICK_NAME_RE = re.compile(r'`([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+)')
# Optional per SKILL.md:50-53 -- absent from a clean env by design, so an
# unimportable chain rooted in one of these is an advisory, never a failure.
# Same standing as the blackjax/dynamax norun blocks.
OPTIONAL_MODULES = frozenset({'funsor', 'blackjax', 'dynamax'})
# Prose may name an API precisely to say it is GONE (the 0.23 porting table in
# SKILL.md, the WAIC removal notes). Keyed by NAME, not file:line, so it
# survives every prose edit -- and each entry carries its reason, exactly as a
# `norun` marker does. PROSE ONLY: the same name inside a code block is an
# assertion that it runs, and stays checked.
DOCUMENTED_ABSENT = {
    'az.plot_ppc': 'removed from the ArviZ 1.x umbrella; SKILL.md porting table',
    'az.waic': 'removed from ArviZ 1.x, use LOO; SKILL.md:84, model-comparison.md',
}
API_REMEDIATION = ('uv run --python 3.13 --with "arviz>=1.0" --with arviz-base '
                   '--with arviz-stats --with arviz-plots --with numpyro '
                   '--with jax python build/check_snippets.py --api <paths>')


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


def _dotted_from_code(code: str) -> set[str]:
    '''Every attribute chain in the block, as dotted strings rooted at a Name.'''
    out = set()
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return out
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        parts, cur = [], node
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            out.add('.'.join([cur.id] + list(reversed(parts))))
    return out


def _resolve(dotted: str, modules: dict) -> tuple[str, bool] | None:
    '''(message, fatal) if the chain does not resolve, else None.

    hasattr alone is not enough: a package does not bind its submodules until
    something imports them, so numpyro.contrib.control_flow reads as missing
    on a fresh interpreter. Try importing each prefix before concluding the
    attribute is gone. An import that fails on an OPTIONAL_MODULES segment is
    an advisory (fatal=False) -- the dependency is absent by design.
    '''
    root, *rest = dotted.split('.')
    if root not in modules:
        return None
    obj = importlib.import_module(modules[root])
    walked = modules[root]
    for attr in rest:
        if hasattr(obj, attr):
            obj = getattr(obj, attr)
            walked += f'.{attr}'
            continue
        try:
            obj = importlib.import_module(f'{walked}.{attr}')
        except ImportError as e:
            optional = OPTIONAL_MODULES & set(f'{walked}.{attr}'.split('.'))
            if optional:
                return (f'{dotted}: optional dependency '
                        f'{sorted(optional)[0]} not installed', False)
            if isinstance(e, ModuleNotFoundError) and e.name == f'{walked}.{attr}':
                # Not a submodule either -- the attribute simply is not there.
                return (f'{dotted}: {walked} has no attribute {attr!r}', True)
            return (f'{dotted}: cannot import {walked}.{attr} ({e})', True)
        walked += f'.{attr}'
    return None


def _missing_roots(modules: dict) -> list[str]:
    '''Root modules the current interpreter cannot import at all.'''
    out = []
    for name in sorted(set(modules.values())):
        try:
            importlib.import_module(name)
        except ImportError:
            out.append(name)
    return out


def _api_findings(path: Path, modules: dict) -> list[tuple[str, bool]]:
    '''(message, fatal) per unresolvable chain, from code blocks AND prose.

    Prose names on DOCUMENTED_ABSENT are skipped; code names never are.
    '''
    text = path.read_text()
    code_names = set()
    for block in iter_code_blocks(text):
        if not is_exempt(block):
            code_names |= _dotted_from_code(block.code)
    prose_names = set(TICK_NAME_RE.findall(strip_fenced_blocks(text)))
    prose_names -= set(DOCUMENTED_ABSENT)
    out = []
    for dotted in sorted(code_names | prose_names):
        found = _resolve(dotted, modules)
        if found:
            msg, fatal = found
            out.append((f'{path}: {msg}', fatal))
    return out


def api_errors(path: Path, modules: dict) -> list[str]:
    '''Unresolvable library attribute chains that fail the gate.'''
    return [m for m, fatal in _api_findings(path, modules) if fatal]


def api_advisories(path: Path, modules: dict) -> list[str]:
    '''Chains unresolvable only because an optional dependency is absent.'''
    return [m for m, fatal in _api_findings(path, modules) if not fatal]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('paths', nargs='+', help='.md files or directories')
    ap.add_argument('--api', action='store_true',
                    help='also resolve library attribute chains (imports the stack)')
    args = ap.parse_args(argv)
    failures = [e for md in _iter_md(args.paths) for e in parse_errors(md)]
    advisories = [ln for md in _iter_md(args.paths) for ln in exempt_report(md)]
    if args.api:
        mods = {'az': 'arviz', 'azs': 'arviz_stats', 'azp': 'arviz_plots',
                'numpyro': 'numpyro', 'jax': 'jax', 'dist': 'numpyro.distributions'}
        missing = _missing_roots(mods)
        if missing:
            print(f'--api needs the stack; cannot import: {", ".join(missing)}',
                  file=sys.stderr)
            print(f'  {API_REMEDIATION}', file=sys.stderr)
            return 2
        for md in _iter_md(args.paths):
            for msg, fatal in _api_findings(md, mods):
                (failures if fatal else advisories).append(msg)
    for f in failures:
        print(f)
    for line in advisories:
        print(f'WARN {line}', file=sys.stderr)
    return 1 if failures else 0

if __name__ == '__main__':
    sys.exit(main())
