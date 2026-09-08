# Snippet Execution Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mechanize the correctness of `bayesian-workflow`'s inline code against the stack `SKILL.md:59` declares, so executable and API claims cannot go stale silently.

**Architecture:** Four gates of increasing cost, sharing one CommonMark-correct block extractor in `build/`, following the repo's established Gate-A idiom (`verify_citations.py`): a CLI taking paths-or-dirs, failures on stdout, advisories on stderr, exit 0/1/2. Gate order is deliberately cheapest-first — parse (stdlib, milliseconds), API-surface (imports only, ~30 s), execution (harnessed subset, minutes). A `norun` fence marker lets a block opt out and travels with the block rather than living in a `file:line` manifest.

**Tech Stack:** Python 3.13, stdlib `ast` + `importlib` + `subprocess`; ArviZ 1.x / NumPyro / JAX resolved through `uv run --with`. No CI exists — every gate is a pre-commit command in the root `CLAUDE.md` Commands block.

## Global Constraints

- **The motivating premise in `specs/deferred_items.md` is wrong; do not inherit it.** The item claims this gate "would have caught all three" of audit `12-audit_7_20_26`'s C1/C2/D2. Verified against `git show a2f2f96`: **C1 only** is snippet-executable (it raises). **D2** lived in markdown bullets — zero lines inside a ```` ```python ```` fence — and is caught only by the Task 4 API-surface check. **C2** was a purely lexical prose contradiction between two files; the audit's own resolution note records that `check_diagnostics.py` "reads a numeric sign from `calibration_check.py`, never the prose". No mechanical gate catches C2. Say this honestly in the runner docstring.
- **Python 3.13**, single quotes, 4-space indent in `build/` (match `check_frontmatter.py`; note `skills/llm-wiki/scripts/` uses 2-space — `build/` does not).
- **Directory-scoped tests, bare imports.** New tests live in `build/` and run via `cd build && uv run --python 3.13 --with pytest ... python -m pytest -q`. A repo-root collection fails outright.
- **State test counts as `+N` deltas, never absolute totals.** The `build/` suite is 47 tests at authoring time; a fresh session's baseline may differ.
- **`build/.scratch/` is gitignored and must never be committed.** Nothing in this plan touches it.
- **Do not hand-edit any deployed copy** under `~/research-wiki/` or elsewhere; this plan touches the repo only.
- **Exit contract, every gate:** `0` clean, `1` violations found, `2` environment/precondition failure with a printed remediation command. Failures to stdout, advisories to stderr prefixed `WARN `.

---

## File Structure

| File | Responsibility |
|---|---|
| `build/fences.py` | **Create.** CommonMark-correct fence handling, shared. `strip_fenced_blocks` (moved verbatim from `check_frontmatter.py`) plus `iter_code_blocks`. |
| `build/test_fences.py` | **Create.** Extractor tests, including the nested-fence trap. |
| `build/check_frontmatter.py` | **Modify.** Import `strip_fenced_blocks` from `fences` instead of defining it. No behaviour change. |
| `build/check_snippets.py` | **Create.** The gate CLI: parse-only (Task 2), API-surface (Task 4), execution (Task 5). |
| `build/test_check_snippets.py` | **Create.** Tests for all three tiers. |
| `build/snippet_preamble.py` | **Create.** The 24-name harness preamble for Task 5. |
| `skills/bayesian-workflow/references/diagnostics.md` | **Modify.** Fix the shipped SyntaxError at the block starting line 117. |
| `skills/bayesian-workflow/references/state-space.md` | **Modify.** Mark the HANDOFF SKETCH block `norun`. |
| `skills/bayesian-workflow/SKILL.md` | **Modify.** Mark the blackjax block `norun`; mark the 4-chain MCMC block `norun slow`. |
| `skills/bayesian-workflow/references/model-criticism.md` | **Modify.** Mark the 200-replicate SBC block `norun slow`; add the missing pandas import or drop the `pd.` usage. |
| `CLAUDE.md` | **Modify.** Add the gate to the Commands block with its `+N` test delta. |

---

### Task 1: Shared CommonMark fence extractor

**Files:**
- Create: `build/fences.py`
- Create: `build/test_fences.py`
- Modify: `build/check_frontmatter.py:45-76` (delete `FENCE_OPEN_RE` + `strip_fenced_blocks`, import them instead)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `strip_fenced_blocks(text: str) -> str` — unchanged contract, moved verbatim.
  - `iter_code_blocks(text: str, langs=('python', 'py')) -> list[CodeBlock]` where `CodeBlock` is a `NamedTuple` with fields `lang: str`, `info: str` (everything on the fence line after the language word, stripped — `''` when absent), `line: int` (1-based line number of the fence opener), `code: str`.
  - Tasks 2, 4 and 5 all consume `iter_code_blocks`. Only blocks at the OUTERMOST fence level are returned — a ```` ```python ```` fence nested inside a ````` ````markdown ````` fence is content, not a block.

- [ ] **Step 1: Write the failing test**

Create `build/test_fences.py`:

```python
'''Tests for fences.py. Stdlib + pytest only.'''
import fences


def test_extracts_a_simple_python_block():
    text = '# T\n\n```python\nx = 1\n```\n'
    blocks = fences.iter_code_blocks(text)
    assert len(blocks) == 1, blocks
    assert blocks[0].lang == 'python'
    assert blocks[0].code == 'x = 1\n'
    assert blocks[0].line == 3
    assert blocks[0].info == ''


def test_nested_python_fence_inside_markdown_fence_is_not_a_block():
    '''The trap check_frontmatter.py documents: a naive non-greedy regex closes
    on the FIRST ``` and reports the inner fence as real. skills/writing-plans/
    SKILL.md has exactly this shape, and its true python-block count is 0.'''
    text = '````markdown\n```python\nx = 1\n```\n````\n'
    assert fences.iter_code_blocks(text) == []


def test_info_suffix_is_captured():
    text = '```python norun needs dynamax\ny = 2\n```\n'
    blocks = fences.iter_code_blocks(text)
    assert blocks[0].info == 'norun needs dynamax', blocks


def test_py_alias_and_language_filter():
    text = '```py\na = 1\n```\n\n```bash\necho hi\n```\n'
    blocks = fences.iter_code_blocks(text)
    assert [b.lang for b in blocks] == ['py'], blocks


def test_strip_fenced_blocks_still_works():
    '''Moved verbatim from check_frontmatter.py; pinned here so the move is
    provably behaviour-preserving.'''
    assert fences.strip_fenced_blocks('a\n```\nb\n```\nc') == 'a\nc'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd build && uv run --python 3.13 --with pytest python -m pytest test_fences.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'fences'`

- [ ] **Step 3: Write minimal implementation**

Create `build/fences.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd build && uv run --python 3.13 --with pytest python -m pytest test_fences.py -q`
Expected: PASS, 5 tests.

- [ ] **Step 5: Point check_frontmatter.py at the shared helper**

In `build/check_frontmatter.py`, delete the `FENCE_OPEN_RE` assignment and the whole `strip_fenced_blocks` function (currently lines 50-75), and add to the imports at the top of the file:

```python
from fences import strip_fenced_blocks
```

- [ ] **Step 6: Verify no regression in the existing gate**

Run: `cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q`
Expected: PASS with a **+5** delta over the pre-task baseline (47 → 52 if `build/.scratch/` is present).

Run: `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`
Expected: exit 0, no output — identical to before the move.

- [ ] **Step 7: Commit**

```bash
git add build/fences.py build/test_fences.py build/check_frontmatter.py
git commit -m "refactor(build): hoist CommonMark fence handling into fences.py"
```

---

### Task 2: Parse-only gate, and the SyntaxError it finds

**Files:**
- Create: `build/check_snippets.py`
- Create: `build/test_check_snippets.py`
- Modify: `skills/bayesian-workflow/references/diagnostics.md` (the block opening at line 117)

**Interfaces:**
- Consumes: `fences.iter_code_blocks` from Task 1.
- Produces:
  - `parse_errors(path: Path) -> list[str]` — one message per unparseable block, formatted `f'{path}:{block.line}: SyntaxError: {msg}'`.
  - `main(argv) -> int` with the Global-Constraints exit contract. Tasks 4 and 5 add `--api` and `--run` flags to this same CLI; default (no flag) is parse-only.

**Context the implementer needs:** `references/diagnostics.md` ships a block containing `def model(...):`, which is not valid Python (`...` is an expression, not a parameter). Confirmed 2026-09-08: `ast.parse` raises `SyntaxError: invalid syntax` at that line. The block is illustrative — it contrasts a centered and a non-centered model — so the fix is to give the placeholder a real signature, not to delete the block. **The gate must ship green**, so this content fix lands in the same task as the gate that finds it.

- [ ] **Step 1: Write the failing test**

Create `build/test_check_snippets.py`:

```python
'''Tests for check_snippets.py. Stdlib + pytest only.'''
from pathlib import Path

import check_snippets


def test_flags_an_unparseable_block(tmp_path):
    p = tmp_path / 'bad.md'
    p.write_text('# T\n\n```python\ndef model(...):\n    pass\n```\n')
    errs = check_snippets.parse_errors(p)
    assert len(errs) == 1, errs
    assert 'SyntaxError' in errs[0] and ':3:' in errs[0], errs


def test_clean_block_passes(tmp_path):
    p = tmp_path / 'good.md'
    p.write_text('```python\nx = 1\n```\n')
    assert check_snippets.parse_errors(p) == []


def test_fragment_with_free_names_still_parses(tmp_path):
    '''Most blocks are fragments referencing undefined names. Parsing is a
    syntax check, not a name check -- these must NOT be flagged.'''
    p = tmp_path / 'frag.md'
    p.write_text('```python\nidata = az.from_numpyro(mcmc)\n```\n')
    assert check_snippets.parse_errors(p) == []


def test_bayesian_workflow_parses_clean():
    '''The gate must ship green: every shipped block parses.'''
    root = Path(__file__).resolve().parent.parent / 'skills/bayesian-workflow'
    errs = [e for md in sorted(root.rglob('*.md'))
            for e in check_snippets.parse_errors(md)]
    assert errs == [], errs
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd build && uv run --python 3.13 --with pytest python -m pytest test_check_snippets.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'check_snippets'`

- [ ] **Step 3: Write minimal implementation**

Create `build/check_snippets.py`:

```python
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

from fences import iter_code_blocks

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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('paths', nargs='+', help='.md files or directories')
    args = ap.parse_args(argv)
    failures = [e for md in _iter_md(args.paths) for e in parse_errors(md)]
    for f in failures:
        print(f)
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 4: Run the gate against the real skill to see it find the shipped defect**

Run: `uv run --python 3.13 python build/check_snippets.py skills/bayesian-workflow/`
Expected: exit 1, one line naming `references/diagnostics.md` and `SyntaxError: invalid syntax`.

- [ ] **Step 5: Fix the shipped snippet**

In `skills/bayesian-workflow/references/diagnostics.md`, in the block that opens at line 117, replace the invalid placeholder signature so the contrast still reads:

```python
# CENTERED (can cause funnel divergences):
def model(y, group_idx):
    mu = numpyro.sample("mu", dist.Normal(mu_global, sigma_group))   # funnel-prone
```

Leave the surrounding `LocScaleReparam` / `reparam` lines untouched — only the `def model(...):` line changes.

- [ ] **Step 6: Run test and gate to verify both pass**

Run: `cd build && uv run --python 3.13 --with pytest python -m pytest test_check_snippets.py -q`
Expected: PASS, 4 tests.

Run: `uv run --python 3.13 python build/check_snippets.py skills/bayesian-workflow/`
Expected: exit 0, no output.

- [ ] **Step 7: Commit**

```bash
git add build/check_snippets.py build/test_check_snippets.py \
        skills/bayesian-workflow/references/diagnostics.md
git commit -m "feat(build): parse-only snippet gate; fix shipped SyntaxError in diagnostics.md"
```

---

### Task 3: The `norun` marker convention

**Files:**
- Modify: `build/check_snippets.py` (add `is_exempt` + advisory reporting)
- Modify: `build/test_check_snippets.py` (append)
- Modify: `skills/bayesian-workflow/references/state-space.md` (the HANDOFF SKETCH block at line 77)
- Modify: `skills/bayesian-workflow/SKILL.md` (the blackjax block at line 185; the 4-chain MCMC block at line 96)
- Modify: `skills/bayesian-workflow/references/model-criticism.md` (the 200-replicate SBC block at line 158)

**Interfaces:**
- Consumes: `CodeBlock.info` from Task 1, `_iter_md` from Task 2.
- Produces: `is_exempt(block) -> bool` (True when `block.info` starts with `norun`), and `exempt_report(path) -> list[str]` returning advisory lines. Tasks 4 and 5 both skip exempt blocks.

**Why an info-string suffix and not a manifest:** a `file:line` exemption list is brittle against every future edit, and this repo has already been bitten by coordinate-anchored bookkeeping. The marker travels with the block. ```` ```python norun <reason> ```` still renders as a python block in every CommonMark renderer, and `iter_code_blocks` matches on the first info word, so `lang` is still `python`.

- [ ] **Step 1: Write the failing test**

Append to `build/test_check_snippets.py`:

```python
def test_norun_block_is_exempt(tmp_path):
    p = tmp_path / 'x.md'
    p.write_text('```python norun needs dynamax\nbuild_params()\n```\n')
    blocks = check_snippets.iter_code_blocks(p.read_text())
    assert check_snippets.is_exempt(blocks[0]) is True


def test_plain_block_is_not_exempt(tmp_path):
    p = tmp_path / 'y.md'
    p.write_text('```python\nx = 1\n```\n')
    blocks = check_snippets.iter_code_blocks(p.read_text())
    assert check_snippets.is_exempt(blocks[0]) is False


def test_norun_still_parses_and_is_still_reported_as_advisory(tmp_path):
    '''Exempt from EXECUTION, not from parsing -- a norun block with broken
    syntax is still a defect, and the advisory keeps the gap visible.'''
    p = tmp_path / 'z.md'
    p.write_text('```python norun sketch\ndef f(...):\n    pass\n```\n')
    assert check_snippets.parse_errors(p) != []
    assert check_snippets.exempt_report(p) != []


def test_every_norun_marker_carries_a_reason():
    '''A bare `norun` with no reason is how an exemption list rots.'''
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent / 'skills/bayesian-workflow'
    bare = [f'{md}:{b.line}'
            for md in sorted(root.rglob('*.md'))
            for b in check_snippets.iter_code_blocks(md.read_text())
            if b.info.strip() == 'norun']
    assert bare == [], bare
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd build && uv run --python 3.13 --with pytest python -m pytest test_check_snippets.py -q`
Expected: FAIL — `AttributeError: module 'check_snippets' has no attribute 'is_exempt'`

- [ ] **Step 3: Write minimal implementation**

Add to `build/check_snippets.py`, after `parse_errors`:

```python
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
```

Re-export the extractor so tests can reach it through one module — add to the imports:

```python
from fences import CodeBlock, iter_code_blocks  # noqa: F401  (re-exported)
```

And in `main`, after printing failures, print advisories to stderr:

```python
    for md in _iter_md(args.paths):
        for line in exempt_report(md):
            print(f'WARN {line}', file=sys.stderr)
```

- [ ] **Step 4: Mark the four blocks that cannot or must not run**

`skills/bayesian-workflow/references/state-space.md`, the block opening at line 77 — change its fence line to:

````
```python norun HANDOFF SKETCH; dynamax is not a bayesian-workflow dependency
````

`skills/bayesian-workflow/SKILL.md`, the blackjax block at line 185:

````
```python norun blackjax is optional (SKILL.md:52), not a declared dependency
````

`skills/bayesian-workflow/SKILL.md`, the 4-chain MCMC block at line 96:

````
```python norun slow: 4 chains x 2000 draws, minutes -- not a pre-commit gate
````

`skills/bayesian-workflow/references/model-criticism.md`, the SBC block at line 158:

````
```python norun slow: 200 SBC replicates x 600 draws -- not a pre-commit gate
````

- [ ] **Step 5: Run tests and the gate**

Run: `cd build && uv run --python 3.13 --with pytest python -m pytest test_check_snippets.py -q`
Expected: PASS, 8 tests.

Run: `uv run --python 3.13 python build/check_snippets.py skills/bayesian-workflow/ 2>&1 1>/dev/null`
Expected: exactly four `WARN ... not executed: ...` lines on stderr, each with a reason; exit 0.

- [ ] **Step 6: Commit**

```bash
git add build/check_snippets.py build/test_check_snippets.py skills/bayesian-workflow/
git commit -m "feat(build): norun fence marker with a required reason"
```

---

### Task 4: API-surface check — the tier that would have caught D2

**Files:**
- Modify: `build/check_snippets.py` (add `api_errors` + `--api` flag)
- Modify: `build/test_check_snippets.py` (append)

**Interfaces:**
- Consumes: `iter_code_blocks`, `is_exempt`, `_iter_md`.
- Produces: `api_errors(path, modules) -> list[str]`, where `modules` maps an alias to an import name (`{'az': 'arviz', 'azs': 'arviz_stats', 'azp': 'arviz_plots', 'numpyro': 'numpyro', 'jax': 'jax'}`). Resolves each dotted attribute chain via `getattr` and reports unresolvable ones.

**Why this tier exists:** D2 was `references/model-comparison.md:67` telling agents to read an `az.compare` `warning` column that ArviZ 1.x removed. It lived in a **prose bullet**, so no snippet executor could ever have caught it. This tier reads dotted names from code AND from backticked prose, which is the only way that class is mechanically reachable. It imports the stack but runs no model, so it costs ~30 s and is deterministic.

**Known false-positive source:** backticked identifiers that are user code, not library API (`model`, `idata.posterior`). Restrict resolution to chains whose ROOT is a known alias in `modules`; everything else is ignored. That is why `modules` is an explicit dict, not inference.

- [ ] **Step 1: Write the failing test**

Append to `build/test_check_snippets.py`:

```python
import pytest

MODULES = {'az': 'arviz'}


def test_missing_attribute_is_flagged(tmp_path):
    p = tmp_path / 'a.md'
    p.write_text('```python\naz.definitely_not_a_real_function(x)\n```\n')
    errs = check_snippets.api_errors(p, MODULES)
    assert any('definitely_not_a_real_function' in e for e in errs), errs


def test_real_attribute_passes(tmp_path):
    p = tmp_path / 'b.md'
    p.write_text('```python\nidata = az.from_numpyro(mcmc)\n```\n')
    assert check_snippets.api_errors(p, MODULES) == []


def test_backticked_prose_identifier_is_checked(tmp_path):
    '''D2 lived in a markdown bullet, not a code block. If this tier only read
    code it would have missed the finding that motivates it.'''
    p = tmp_path / 'c.md'
    p.write_text('- `az.no_such_thing`: gone in ArviZ 1.x\n')
    assert check_snippets.api_errors(p, MODULES) != []


def test_non_library_roots_are_ignored(tmp_path):
    '''`idata.posterior` and `model.foo` are user code, not library API.'''
    p = tmp_path / 'd.md'
    p.write_text('```python\nidata.posterior.mean()\nmodel.whatever()\n```\n')
    assert check_snippets.api_errors(p, MODULES) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd build && uv run --python 3.13 --with pytest --with "arviz>=1.0" --with arviz-base --with arviz-stats python -m pytest test_check_snippets.py -q -k api or backticked or non_library or real_attribute`
Expected: FAIL — `AttributeError: module 'check_snippets' has no attribute 'api_errors'`

- [ ] **Step 3: Write minimal implementation**

Add to `build/check_snippets.py`:

```python
import importlib
import re

TICK_NAME_RE = re.compile(r'`([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+)')


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


def _resolve(dotted: str, modules: dict) -> str | None:
    '''Return an error message if the chain does not resolve, else None.'''
    root, *rest = dotted.split('.')
    if root not in modules:
        return None
    try:
        obj = importlib.import_module(modules[root])
    except ImportError as e:
        return f'cannot import {modules[root]}: {e}'
    walked = root
    for attr in rest:
        if not hasattr(obj, attr):
            return f'{dotted}: {walked} has no attribute {attr!r}'
        obj = getattr(obj, attr)
        walked += f'.{attr}'
    return None


def api_errors(path: Path, modules: dict) -> list[str]:
    '''Unresolvable library attribute chains, from code blocks AND prose.'''
    text = path.read_text()
    names = set()
    for block in iter_code_blocks(text):
        if not is_exempt(block):
            names |= _dotted_from_code(block.code)
    names |= set(TICK_NAME_RE.findall(strip_fenced_blocks(text)))
    out = []
    for dotted in sorted(names):
        msg = _resolve(dotted, modules)
        if msg:
            out.append(f'{path}: {msg}')
    return out
```

Import `strip_fenced_blocks` alongside the others at the top of the file, and add the flag in `main`:

```python
    ap.add_argument('--api', action='store_true',
                    help='also resolve library attribute chains (imports the stack)')
```

with, after the parse pass:

```python
    if args.api:
        mods = {'az': 'arviz', 'azs': 'arviz_stats', 'azp': 'arviz_plots',
                'numpyro': 'numpyro', 'jax': 'jax', 'dist': 'numpyro.distributions'}
        failures += [e for md in _iter_md(args.paths) for e in api_errors(md, mods)]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd build && uv run --python 3.13 --with pytest --with "arviz>=1.0" --with arviz-base --with arviz-stats python -m pytest test_check_snippets.py -q`
Expected: PASS, 12 tests.

- [ ] **Step 5: Run against the real skill and triage what it finds**

Run:
```bash
uv run --python 3.13 --with "arviz>=1.0" --with arviz-base --with arviz-stats \
  --with arviz-plots --with numpyro --with jax \
  python build/check_snippets.py --api skills/bayesian-workflow/
```
Expected: a list of unresolvable chains. **Each one is either a real staleness finding (fix the doc) or a false positive (extend the ignore rule).** Do not suppress wholesale. Record the triage verdict per finding in the commit body. A known one to expect: `references/model-criticism.md` uses `pd.DataFrame` with no pandas import anywhere in the skill — `pd` is not in `modules`, so it will not be flagged here; fix it or drop it as a separate content commit.

- [ ] **Step 6: Commit**

```bash
git add build/check_snippets.py build/test_check_snippets.py
git commit -m "feat(build): API-surface tier; the class D2 belonged to"
```

---

### Task 5: Harnessed execution, two-tier pinned/floating

**Files:**
- Create: `build/snippet_preamble.py`
- Modify: `build/check_snippets.py` (add `run_errors` + `--run` flag)
- Modify: `build/test_check_snippets.py` (append)

**Interfaces:**
- Consumes: everything above.
- Produces: `runnable(block) -> bool` (not exempt, parses, no `...` elision, all free names bound by the preamble) and `run_errors(path, timeout) -> list[str]`.

**Measured coverage, so nobody expects more:** of 77 parsing blocks in the skill, a 24-name preamble makes 42 name-complete and 31 both name-complete and elision-free. The remaining 35 need per-block fixtures and are **out of scope** — they are reported as advisories, never silently dropped.

**Isolation is mandatory, not optional.** Blocks write `model_output.nc`, create a literal `<slug>/` directory, and save PNGs. Every block runs in a subprocess with `cwd` set to a fresh temp dir and `MPLBACKEND=Agg`.

**Warnings are not failures.** The repo already documents expected warnings (`priors.md:229` "safe to ignore"; `CLAUDE.md:68` "4 arviz RuntimeWarnings ... expected and not silenced"). Assert "did not raise", never `-W error`.

**Pinned vs floating — the tension, resolved two-tier.** Pinning is reproducible but goes blind to exactly the upstream drift audit Theme 1 is about; floating catches drift but makes the gate's verdict non-reproducible. So: the **pinned** run is the hard gate (exit 1); a **floating** run is advisory (stderr, exit 0). Pinned set verified 2026-09-08 — `arviz==1.3.0`, `arviz-stats==1.3.2`, `arviz-plots==1.3.1`, `numpyro==0.21.0`, `jax==0.11.1`. Record that provenance line beside the constant and refresh it deliberately.

- [ ] **Step 1: Write the failing test**

Append to `build/test_check_snippets.py`:

```python
def test_elided_block_is_not_runnable(tmp_path):
    p = tmp_path / 'e.md'
    p.write_text('```python\nmodel = ...\n...\n```\n')
    b = check_snippets.iter_code_blocks(p.read_text())[0]
    assert check_snippets.runnable(b) is False


def test_block_with_unbound_name_is_not_runnable(tmp_path):
    p = tmp_path / 'f.md'
    p.write_text('```python\nresult = totally_unbound_thing(1)\n```\n')
    b = check_snippets.iter_code_blocks(p.read_text())[0]
    assert check_snippets.runnable(b) is False


def test_preamble_bound_block_is_runnable(tmp_path):
    p = tmp_path / 'g.md'
    p.write_text('```python\nsummary = az.summary(idata)\n```\n')
    b = check_snippets.iter_code_blocks(p.read_text())[0]
    assert check_snippets.runnable(b) is True


def test_raising_block_is_reported(tmp_path):
    p = tmp_path / 'h.md'
    p.write_text('```python\nraise ValueError("boom")\n```\n')
    errs = check_snippets.run_errors(p, timeout=60)
    assert any('boom' in e for e in errs), errs


def test_block_side_effects_do_not_touch_cwd(tmp_path, monkeypatch):
    '''Blocks write model_output.nc and a literal <slug>/ dir. The runner must
    execute elsewhere or the gate pollutes the repo it guards.'''
    p = tmp_path / 'i.md'
    p.write_text('```python\nopen("sentinel.txt", "w").write("x")\n```\n')
    monkeypatch.chdir(tmp_path)
    check_snippets.run_errors(p, timeout=60)
    assert not (tmp_path / 'sentinel.txt').exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd build && uv run --python 3.13 --with pytest python -m pytest test_check_snippets.py -q -k runnable or raising or side_effects`
Expected: FAIL — `AttributeError: module 'check_snippets' has no attribute 'runnable'`

- [ ] **Step 3: Write the preamble**

Create `build/snippet_preamble.py`:

```python
'''Fixture context for executing bayesian-workflow snippet fragments.

Binds the 24 names that make 42 of the skill's 77 parsing blocks
name-complete. Sized to be fast: the MCMC here is 1 chain x 50 draws, purely
so `mcmc` and `idata` exist -- it is NOT a model worth interpreting.

THIS FILE IS A SECOND SOURCE OF TRUTH and can go green wrongly: a fixture
simpler than the doc's example can make a doc-level error pass. Keep the
fixtures shaped like the skill's running example, and edit this file whenever
a snippet's assumed context changes.
'''
PREAMBLE = '''
import os
import numpy as np
import jax, jax.numpy as jnp
import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS, Predictive
import arviz as az
import arviz_stats as azs
import arviz_plots as azp
import matplotlib.pyplot as plt

rng_key = jax.random.PRNGKey(0)
x = np.linspace(0, 1, 40)
y = 2.0 * x + np.random.default_rng(0).normal(0, 0.1, 40)
coords = {"obs": np.arange(40)}
dims = {"y": ["obs"]}

def model(x=x, y=None):
    a = numpyro.sample("a", dist.Normal(0, 1))
    b = numpyro.sample("b", dist.Normal(0, 1))
    numpyro.sample("y", dist.Normal(a + b * x, 0.1), obs=y)

mcmc = MCMC(NUTS(model), num_warmup=50, num_samples=50, num_chains=1,
            progress_bar=False)
mcmc.run(rng_key, x=x, y=y)
idata = az.from_numpyro(mcmc)
'''

PINNED = (
    # Verified resolving 2026-09-08. Refresh deliberately and re-record.
    'arviz==1.3.0', 'arviz-base', 'arviz-stats==1.3.2', 'arviz-plots==1.3.1',
    'numpyro==0.21.0', 'jax==0.11.1', 'numpy', 'matplotlib',
)
```

- [ ] **Step 4: Write the runner**

Add to `build/check_snippets.py`:

```python
import builtins
import subprocess
import tempfile

from snippet_preamble import PREAMBLE

_PREAMBLE_NAMES = None


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


def _preamble_names() -> set[str]:
    global _PREAMBLE_NAMES
    if _PREAMBLE_NAMES is None:
        _PREAMBLE_NAMES = _bound_by(ast.parse(PREAMBLE)) | set(dir(builtins))
    return _PREAMBLE_NAMES


def runnable(block) -> bool:
    '''Not exempt, parses, no `...` elision, every free name bound.'''
    if is_exempt(block):
        return False
    try:
        tree = ast.parse(block.code)
    except SyntaxError:
        return False
    if any(isinstance(n, ast.Constant) and n.value is Ellipsis
           for n in ast.walk(tree)):
        return False
    bound = _preamble_names() | _bound_by(tree)
    free = {n.id for n in ast.walk(tree)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    return free <= bound


def run_errors(path: Path, timeout: int = 300) -> list[str]:
    '''Execute every runnable block in an isolated temp cwd; report raises.'''
    out = []
    for block in iter_code_blocks(path.read_text()):
        if not runnable(block):
            continue
        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, 'MPLBACKEND': 'Agg'}
            proc = subprocess.run(
                [sys.executable, '-c', PREAMBLE + '\n' + block.code],
                cwd=tmp, env=env, capture_output=True, text=True,
                timeout=timeout)
        if proc.returncode != 0:
            tail = proc.stderr.strip().split('\n')[-1]
            out.append(f'{path}:{block.line}: raised: {tail}')
    return out
```

Add `import os` at the top, and the `--run` flag in `main` mirroring `--api`.

- [ ] **Step 5: Run test to verify it passes**

Run: `cd build && uv run --python 3.13 --with pytest --with "arviz>=1.0" --with arviz-base --with arviz-stats --with arviz-plots --with numpyro --with jax --with numpy --with matplotlib python -m pytest test_check_snippets.py -q`
Expected: PASS, 17 tests.

- [ ] **Step 6: Run the pinned gate against the skill**

Run:
```bash
uv run --python 3.13 --with 'arviz==1.3.0' --with arviz-base \
  --with 'arviz-stats==1.3.2' --with 'arviz-plots==1.3.1' \
  --with 'numpyro==0.21.0' --with 'jax==0.11.1' --with numpy --with matplotlib \
  python build/check_snippets.py --run skills/bayesian-workflow/
```
Expected: exit 0. **If a block raises, that is a real finding — fix the snippet, do not mark it `norun` to get green.** `norun` is for blocks that cannot run by design, never for blocks that fail.

- [ ] **Step 7: Commit**

```bash
git add build/snippet_preamble.py build/check_snippets.py build/test_check_snippets.py
git commit -m "feat(build): harnessed snippet execution with pinned deps"
```

---

### Task 6: Wire the gate into the repo's documented commands

**Files:**
- Modify: `CLAUDE.md` (the Commands block)

**Interfaces:**
- Consumes: the three tiers' invocations from Tasks 2, 4, 5.
- Produces: nothing consumed by later tasks.

- [ ] **Step 1: Add the gate to the Commands block**

In the root `CLAUDE.md`, immediately after the frontmatter/provenance lint entries, add:

````markdown
```bash
# Snippet gate for bayesian-workflow. Three tiers, cheapest first.
# Tier 1 (parse-only, stdlib, instant):
uv run --python 3.13 python build/check_snippets.py skills/bayesian-workflow/
# Tier 2 (+ API-surface; imports the stack, ~30s; the tier that catches drift
# like audit D2's removed `az.compare` warning column):
uv run --python 3.13 --with "arviz>=1.0" --with arviz-base --with arviz-stats \
  --with arviz-plots --with numpyro --with jax \
  python build/check_snippets.py --api skills/bayesian-workflow/
# Tier 3 (+ execute the harnessed subset against PINNED deps; minutes).
# `norun` blocks are advisory on stderr, never silent.
uv run --python 3.13 --with 'arviz==1.3.0' --with arviz-base \
  --with 'arviz-stats==1.3.2' --with 'arviz-plots==1.3.1' \
  --with 'numpyro==0.21.0' --with 'jax==0.11.1' --with numpy --with matplotlib \
  python build/check_snippets.py --run skills/bayesian-workflow/
```
````

- [ ] **Step 2: Update the build/ test-count line**

The `build/` suite entry in `CLAUDE.md` currently records 47 tests. This plan adds `test_fences.py` (5) and `test_check_snippets.py` (17) — a **+22** delta. Update the count and its parenthetical, and note that `test_check_snippets.py`'s API and execution tests need the ArviZ/NumPyro chain (`-q` without it will error on import).

- [ ] **Step 3: Verify the documented commands actually run**

Run each of the three commands exactly as written in `CLAUDE.md`.
Expected: tiers 1 and 2 exit 0; tier 3 exits 0 with `WARN ... not executed:` advisories on stderr for the four `norun` blocks.

Run: `cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q`
Expected: the non-ArviZ subset passes; confirm the count matches the number written into `CLAUDE.md`.

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: record the snippet gate's three tiers in Commands"
```

---

## Notes for the executor

- **Do not widen scope to other skills.** Repo-wide *execution* is a category error: `clean-code`'s blocks are before/after pairs whose "before" half is deliberately bad, and `test-driven-development`'s are RED examples that are supposed to fail. Repo-wide *parse-only* (Tier 1) would be safe, but it is not in this plan's scope — propose it separately if wanted.
- **`dynamax` and `blackjax` are not dependencies.** Any block importing them is `norun` by construction.
- **There is no network or GPU hazard.** Verified: no block fetches anything; every one builds data from `np.random`/`jax.random`. Do not engineer for hazards that are not there.
- **If a tier finds nothing on the real skill, say so plainly** rather than manufacturing a finding. Tier 1 is expected to find exactly one defect (fixed in Task 2); Tiers 2 and 3 may legitimately come up clean.
