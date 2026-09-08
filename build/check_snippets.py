'''Snippet gate for skill documentation (Gate A pattern).

Tier 1 (default) parses every fenced python block with ast.parse. It catches
syntax that shipped broken; it does NOT catch API drift. Tier 1 runs over all
of skills/; tiers 2 and 3 stay scoped to skills/bayesian-workflow, whose stack
they import and execute against.

Two fence markers opt a block out, each requiring a reason so the exemption
list stays auditable: `norun` (execution only, parsing still applies) and
`noparse` (parsing too, and therefore execution). Both are reported on stderr.

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

Three tiers, cheapest first; see the root CLAUDE.md for the full invocations.
  (default)  parse every block            stdlib, instant
  --api      + resolve dotted API chains  imports the stack, ~30s
  --run      + execute the harnessed set  minutes, pinned deps

Exit 0 clean, 1 violations (stdout, one line each), 2 environment failure
with a remediation command. Advisories go to stderr prefixed WARN and never
change the exit code -- norun blocks and blocks needing a per-block fixture
are reported there so partial coverage never reads as total coverage.
'''
import argparse
import ast
import builtins
import importlib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from fences import (CodeBlock, iter_code_blocks,  # noqa: F401  (re-exported)
                    strip_fenced_blocks)
from snippet_preamble import FIXTURE_VARS, PINNED, PREAMBLE

NORUN = 'norun'
NOPARSE = 'noparse'
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
RUN_REMEDIATION = ('uv run --python 3.13 ' +
                   ' '.join(f'--with {d!r}'.replace("'", '\"')
                            for d in PINNED) +
                   ' python build/check_snippets.py --run <paths>')


def _iter_md(paths):
    '''Expand directory arguments to every .md beneath them, recursively.'''
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            yield from sorted(p.rglob('*.md'))
        elif p.suffix == '.md':
            yield p


def parse_errors(path: Path) -> list[str]:
    '''Return one message per block that fails ast.parse (empty == clean).

    `noparse` blocks are skipped -- see is_parse_exempt.'''
    out = []
    for block in iter_code_blocks(path.read_text()):
        if is_parse_exempt(block):
            continue
        try:
            ast.parse(block.code)
        except SyntaxError as e:
            out.append(f'{path}:{block.line}: SyntaxError: {e.msg} '
                       f'(block line {e.lineno})')
    return out


def _marker(block) -> str | None:
    '''The exemption marker leading the fence info string, or None.'''
    head = block.info.split(None, 1)[:1]
    return head[0] if head and head[0] in (NORUN, NOPARSE) else None


def is_exempt(block) -> bool:
    '''True when the fence info string opts the block out of execution.

    Shape: ```python norun <reason>. Exempt from EXECUTION only -- parsing
    still applies. The reason is required (test_every_norun_marker_carries_a
    _reason pins it) so the exemption list stays auditable.

    `noparse` implies this: a block that cannot be parsed cannot be executed,
    and without it --run would try one and fail confusingly.
    '''
    return _marker(block) is not None


def is_parse_exempt(block) -> bool:
    '''True for ```python noparse <reason>: exempt from PARSING as well.

    For excerpts that cannot be made valid standalone Python without losing
    their meaning -- an indented replacement fragment whose indentation shows
    where it substitutes into the block above it. Strictly narrower in intent
    than norun and strictly wider in effect, so it carries the same required
    reason (test_every_noparse_marker_carries_a_reason pins it) and the same
    stderr advisory. Reach for it only when dedenting or completing the block
    would damage what it teaches; otherwise fix the snippet.
    '''
    return _marker(block) == NOPARSE


def exempt_report(path: Path) -> list[str]:
    '''Advisory lines naming every block excluded from execution or parsing.'''
    out = []
    for b in iter_code_blocks(path.read_text()):
        m = _marker(b)
        if m is None:
            continue
        what = 'not parsed or executed' if m == NOPARSE else 'not executed'
        out.append(f'{path}:{b.line}: {what}: {b.info[len(m):].strip()}')
    return out


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


def _bound_by(tree) -> set[str]:
    '''Names a module body binds: assignments, defs, imports, parameters.'''
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.alias):
            names.add((node.asname or node.name).split('.')[0])
        elif isinstance(node, ast.arg):
            names.add(node.arg)
    return names


_PREAMBLE_NAMES = None


def _preamble_names() -> set[str]:
    global _PREAMBLE_NAMES
    if _PREAMBLE_NAMES is None:
        _PREAMBLE_NAMES = _bound_by(ast.parse(PREAMBLE)) | set(dir(builtins))
    return _PREAMBLE_NAMES


_VAR_KWARGS = ('var_names', 'var_name')
# Groups an InferenceData/DataTree exposes as attributes; a literal subscript
# on one of these names a variable the fixture must actually carry.
_IDATA_GROUPS = ('posterior', 'prior', 'observed_data', 'posterior_predictive',
                 'prior_predictive', 'log_likelihood', 'log_prior',
                 'sample_stats')


def _required_vars(tree) -> set[str]:
    '''Fixture variables a block names as STRING LITERALS.

    Two shapes reach the fixture: a var_names=/var_name= keyword, and a
    literal subscript on an idata group (idata.posterior["beta"]). Only
    literals are visible; a computed name leaves the block admitted as before.

    This is what stops name-completeness from over-promising. A block can bind
    every name it uses and still ask for `param1` -- a PLACEHOLDER standing in
    for the reader's own parameters, not a claim that `param1` exists. Running
    it would report a doc defect where there is none.
    '''
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg in _VAR_KWARGS:
            val = node.value
            if isinstance(val, ast.Constant) and isinstance(val.value, str):
                out.add(val.value)
            elif isinstance(val, (ast.List, ast.Tuple)):
                out |= {e.value for e in val.elts
                        if isinstance(e, ast.Constant) and isinstance(e.value, str)}
        elif (isinstance(node, ast.Subscript)
                and isinstance(node.value, ast.Attribute)
                and node.value.attr in _IDATA_GROUPS
                and isinstance(node.slice, ast.Constant)
                and isinstance(node.slice.value, str)):
            out.add(node.slice.value)
    return out


# numpyro primitives are only meaningful inside a model function: called at
# module level they raise, because the PRNG key comes from the enclosing
# trace. Prior catalogues are full of such fragments -- menus of alternative
# sites shown for comparison, never meant as programs.
_MODEL_PRIMITIVES = ('sample', 'factor', 'deterministic', 'param', 'plate')


def _module_level_primitive(tree) -> str | None:
    '''A numpyro primitive called outside any def -- a model-body fragment.'''
    stack = list(tree.body)
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue  # inside a def is exactly where these belong
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in _MODEL_PRIMITIVES
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == 'numpyro'):
            return f'numpyro.{node.func.attr}'
        stack.extend(ast.iter_child_nodes(node))
    return None


def _unrunnable_reason(block) -> str:
    '''Why --run cannot execute this block; empty string when it can.'''
    if is_exempt(block):
        return f'{NORUN}: {block.info[len(NORUN):].strip()}'
    try:
        tree = ast.parse(block.code)
    except SyntaxError:
        return 'does not parse'
    if any(isinstance(n, ast.Constant) and n.value is Ellipsis
           for n in ast.walk(tree)):
        return 'elided with `...`'
    primitive = _module_level_primitive(tree)
    if primitive:
        return f'model-body fragment ({primitive} outside a model handler)'
    missing = _required_vars(tree) - FIXTURE_VARS
    if missing:
        return f'needs fixture variables {sorted(missing)}'
    free = {n.id for n in ast.walk(tree)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    unbound = free - (_preamble_names() | _bound_by(tree))
    if unbound:
        return f'unbound names {sorted(unbound)}'
    return ''


def runnable(block) -> bool:
    '''Not exempt, parses, no `...` elision, name-complete, fixture-complete.

    Conservative by design: a block is admitted only when the preamble can
    actually satisfy it, so a raise in a --run report is a claim about the
    DOCUMENTATION, not about this harness.
    '''
    return _unrunnable_reason(block) == ''


def run_errors(path: Path, timeout: int = 300) -> list[str]:
    '''Execute every runnable block in an isolated temp cwd; report raises.

    Isolation is mandatory, not tidiness: blocks write model_output.nc, create
    a literal <slug>/ directory, and save PNGs. Warnings are not failures --
    the skill documents several as expected -- so this asserts "did not
    raise", never -W error.
    '''
    out = []
    for block in iter_code_blocks(path.read_text()):
        if not runnable(block):
            continue
        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, 'MPLBACKEND': 'Agg'}
            try:
                proc = subprocess.run(
                    [sys.executable, '-c', PREAMBLE + '\n' + block.code],
                    cwd=tmp, env=env, capture_output=True, text=True,
                    timeout=timeout)
            except subprocess.TimeoutExpired:
                out.append(f'{path}:{block.line}: timed out after {timeout}s')
                continue
        if proc.returncode != 0:
            tail = proc.stderr.strip().split('\n')[-1]
            out.append(f'{path}:{block.line}: raised: {tail}')
    return out


def unrunnable_report(path: Path) -> list[str]:
    '''Advisory lines for blocks --run cannot reach, each with its reason.

    The plan's "reported as advisories, never silently dropped": a gate that
    executes a subset must not read as if it covered everything. norun blocks
    are omitted here -- exempt_report already names those.
    '''
    out = []
    for b in iter_code_blocks(path.read_text()):
        if is_exempt(b):
            continue
        reason = _unrunnable_reason(b)
        if reason:
            out.append(f'{path}:{b.line}: not executed: {reason}')
    return out



def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('paths', nargs='+', help='.md files or directories')
    ap.add_argument('--api', action='store_true',
                    help='also resolve library attribute chains (imports the stack)')
    ap.add_argument('--run', action='store_true',
                    help='also execute the harnessed subset (minutes; needs the stack)')
    ap.add_argument('--timeout', type=int, default=300,
                    help='per-block execution timeout in seconds (default: 300)')
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
    if args.run:
        missing = _missing_roots({'az': 'arviz', 'numpyro': 'numpyro',
                                  'jax': 'jax'})
        if missing:
            print(f'--run needs the stack; cannot import: {", ".join(missing)}',
                  file=sys.stderr)
            print(f'  {RUN_REMEDIATION}', file=sys.stderr)
            return 2
        for md in _iter_md(args.paths):
            failures += run_errors(md, timeout=args.timeout)
            advisories += unrunnable_report(md)
    for f in failures:
        print(f)
    for line in advisories:
        print(f'WARN {line}', file=sys.stderr)
    return 1 if failures else 0

if __name__ == '__main__':
    sys.exit(main())
