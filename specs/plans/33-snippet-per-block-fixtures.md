# Snippet Per-Block Fixtures Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Raise the number of `skills/bayesian-workflow` snippets that the snippet gate's `--run` tier executes, by binding what the shared fixture already carries and adding a per-block named-fixture mechanism with one `comparison` fixture.

**Architecture:** `build/check_snippets.py --run` executes a block only when the shared preamble in `build/snippet_preamble.py` binds every name it uses and carries every variable it asks for (`FIXTURE_VARS`). Task 1 widens that shared fixture where it is free: `diverging` is already in the fixture's `sample_stats`, and `posterior_samples` is one line from the existing `mcmc`. Task 2 adds the mechanism: a block opts into a named fixture with `fixture=<name>` in its fence info string (```` ```python fixture=comparison ````), and the named fixture's code runs between the preamble and the block, so only the blocks that need extra fits pay for them. Task 3 adds the `comparison` fixture (two more fits of the running-example model), annotates the five blocks that compare fitted variants, and re-measures coverage.

**Tech Stack:** Python 3.13 stdlib (`ast`, `re`, `subprocess`), pytest; the pinned ArviZ / NumPyro / JAX stack (the `PINNED` tuple in `build/snippet_preamble.py`) for Tier 3 and the stack-gated tests.

**Source:** `specs/deferred_items.md` § `29-snippet-execution-gate — 2026-09-08`, item "Per-block fixtures for the 34 blocks `--run` cannot reach" (Size: plan), selected for a plan at the 2026-10-03 `/deferred` pass. There is no spec. Its closure condition: "either the executed count rises with `FIXTURE_VARS` and the preamble widened together, or a per-block fixture mechanism exists and the advisory count for 'unbound names' falls." This plan meets both halves.

## Global Constraints

- Python style: single quotes, f-strings, 4-space indent; target Python 3.13; Polars over pandas (no new `import pandas`).
- `FIXTURE_VARS` and the fixture code widen together, never one alone (`build/snippet_preamble.py` docstring). From Task 1 on, `FIXTURE_VARS` means "names the fixture's InferenceData carries, in any group", not only posterior sites.
- Placeholders are never satisfied: `param1` / `param2` stand for the reader's own parameters, so they never enter `FIXTURE_VARS` or a fixture.
- A fixture is shaped like the documentation's own example. Never simplify a fixture to make a block pass; the preamble docstring calls the fixture "a second source of truth" that "can go green wrongly".
- If a newly admitted block raises under `--run`, that is a finding. Fix the snippet if the documentation is wrong, or fix the fixture if it misshapes what the documentation assumes. Never mark a block `norun` to get green (CLAUDE.md snippet-gate notes; plan 29 Task 5 Step 6).
- A def-only block (it defines a function and calls nothing) is executed but tests only that the definition compiles. Report def-only blocks separately wherever coverage is stated.
- Skill files change only by adding `fixture=<name>` to a fence info string — no prose edits. Before committing a skill change, run the frontmatter and provenance lints, Tier 1 of the snippet gate, and the dependency-drift check (root CLAUDE.md "Commands").
- State test-count changes as deltas (`+N`), never as absolute totals; the executor re-measures totals.
- The pinned stack is `PINNED` in `build/snippet_preamble.py`. Do not refresh it in this plan.
- Coverage claims (the preamble docstring and the root CLAUDE.md Tier 3 line) are re-measured from a real `--run` at the end of Task 3, never edited by arithmetic.

## Measured baseline (2026-10-03, Tier 3 at 7c8b04c)

78 fenced python blocks in `skills/bayesian-workflow/`. `--run` executes 27. The 51 advisories are 4 `norun`, 6 elided with `...`, 7 model-body fragments, 10 "needs fixture variables" and 24 "unbound names".

This plan admits seven of the 34 reachable blocks:

| Block | Blocked by today | Admitted in |
|---|---|---|
| `references/diagnostics.md` — `def run_diagnostics(idata)` (def-only) | needs fixture variables `['diverging']` | Task 1 |
| `references/model-comparison.md` — `log_likelihood(model, posterior_samples, x, y=y)` | unbound `posterior_samples` | Task 1 |
| `references/model-comparison.md` — `idata_1 = az.from_numpyro(mcmc_1, …)` | unbound `mcmc_1`, `mcmc_2` | Task 3 |
| `references/model-comparison.md` — `models = {"m1": idata_1, …}` | unbound `idata_1..3` | Task 3 |
| `references/model-comparison.md` — `az.compare(models, method="stacking")` | unbound `models` | Task 3 |
| `references/model-comparison.md` — `loo_a = az.loo(idata_1, pointwise=True)` | unbound `idata_1`, `idata_2` | Task 3 |
| `references/visualize.md` — `loo2 = az.loo(idata_m2, pointwise=True)` | unbound `idata_m2`, `idata_m3` | Task 3 |

Expected end state: 34 executed (one of them def-only) and 44 advisories, with "unbound names" falling from 24 to 18 and "needs fixture variables" from 10 to 9. The hierarchical-model blocks (`mu`/`tau`/`theta`, `alpha`/`delta`, `group`), the `param1` placeholders and the heterogeneous tail stay advisories. Each would need its own named fixture shaped to its own document's example, and that is follow-up work for the mechanism this plan builds.

---

### Task 1: Bind what the shared fixture already carries

**Files:**
- Modify: `build/snippet_preamble.py` (docstring; `FIXTURE_VARS`; one line in `PREAMBLE`)
- Test: `build/test_check_snippets.py`

**Interfaces:**
- Consumes: `check_snippets.runnable(block) -> bool`, `check_snippets._unrunnable_reason(block) -> str`, `check_snippets.iter_code_blocks(text) -> list[CodeBlock]` (all existing).
- Produces: `FIXTURE_VARS == frozenset({'beta', 'sigma', 'y_obs', 'diverging'})`; `PREAMBLE` binds `posterior_samples`; the test helper `_skill_block(relpath, needle) -> CodeBlock`, which Task 3 reuses.

- [ ] **Step 1: Write the failing tests**

Append to `build/test_check_snippets.py`:

```python
def _skill_block(relpath, needle):
    '''The bayesian-workflow block whose code contains `needle`. Found by
    content, not line number, so prose edits above it do not break the test.'''
    doc = (Path(__file__).resolve().parent.parent
           / 'skills/bayesian-workflow' / relpath).read_text()
    return next(b for b in check_snippets.iter_code_blocks(doc) if needle in b.code)


def test_blocks_the_shared_fixture_already_carries_are_admitted():
    '''diagnostics.md's run_diagnostics reads sample_stats["diverging"], which the
    preamble's MCMC records via extra_fields; model-comparison.md's
    log_likelihood call needs posterior_samples, which the preamble's mcmc
    already holds.'''
    for relpath, needle in (
            ('references/diagnostics.md', 'def run_diagnostics(idata)'),
            ('references/model-comparison.md',
             'log_likelihood(model, posterior_samples')):
        block = _skill_block(relpath, needle)
        assert check_snippets.runnable(block), check_snippets._unrunnable_reason(block)


@requires_stack
def test_every_fixture_var_is_carried_by_the_fixture_idata():
    '''FIXTURE_VARS is the honesty half of the fixture: every name in it must be
    a variable the preamble's idata carries, in some group.'''
    import os
    import subprocess
    import sys

    from snippet_preamble import FIXTURE_VARS, PREAMBLE
    check = (
        '\ncarried = {name for node in idata.children.values()'
        ' for name in node.data_vars}\n'
        f'missing = [n for n in {sorted(FIXTURE_VARS)!r} if n not in carried]\n'
        'assert not missing, missing\n')
    proc = subprocess.run([sys.executable, '-c', PREAMBLE + check],
                          capture_output=True, text=True, timeout=300,
                          env={**os.environ, 'MPLBACKEND': 'Agg'})
    assert proc.returncode == 0, proc.stderr[-2000:]
```

- [ ] **Step 2: Run the tests to verify the first fails**

Run: `cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest test_check_snippets.py -q -k "already_carries or every_fixture_var"`
Expected: `test_blocks_the_shared_fixture_already_carries_are_admitted` FAILS with `needs fixture variables ['diverging']` (the first block in the loop). `test_every_fixture_var_is_carried_by_the_fixture_idata` SKIPS, since this command does not install the stack.

- [ ] **Step 3: Widen `FIXTURE_VARS` and the preamble together**

In `build/snippet_preamble.py`, change the `FIXTURE_VARS` line to:

```python
FIXTURE_VARS = frozenset({'beta', 'sigma', 'y_obs', 'diverging'})
```

In `PREAMBLE`, directly after the line `post_pred = Predictive(model, mcmc.get_samples())(k_post, x)`, add:

```python
posterior_samples = mcmc.get_samples()   # {site: (draws, ...)}, as log_likelihood takes it
```

In the module docstring, replace the paragraph that begins `FIXTURE_VARS is the honesty half.` with:

```text
FIXTURE_VARS is the honesty half. It names every variable the fixture's
InferenceData carries, in any group: the posterior sites `beta` and `sigma`,
the observed site `y_obs`, and `diverging`, which the MCMC run records into
sample_stats through extra_fields. check_snippets.runnable() refuses any block
naming a variable outside it, so a snippet written against a DIFFERENT
running example (`param1`, `alpha`/`delta`, `tau`/`theta`) is reported as
needing its own fixture rather than executed and blamed for the mismatch.
`param1`/`param2` are placeholders for the reader's own parameters and are
never added. Widen the fixture and this set together, never one alone;
test_every_fixture_var_is_carried_by_the_fixture_idata pins the set against
the fixture.
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest test_check_snippets.py -q -k "already_carries or every_fixture_var"`
Expected: 1 passed, 1 skipped.

Then the stack-gated test with the stack:
Run: `cd build && uv run --python 3.13 --with pytest --with 'arviz==1.3.0' --with arviz-base --with 'arviz-stats==1.3.2' --with 'arviz-plots==1.3.1' --with 'numpyro==0.21.0' --with 'jax==0.11.1' --with numpy --with polars --with pyyaml --with matplotlib python -m pytest test_check_snippets.py -q -k "already_carries or every_fixture_var"`
Expected: 2 passed. If `diverging` is reported missing, the ArviZ conversion renamed the field: read the actual `sample_stats` names from the failure message, and put the carried name in both `FIXTURE_VARS` and this docstring. Never drop the test.

- [ ] **Step 5: Run Tier 3 and confirm both blocks execute clean**

Run (repo root):
```bash
uv run --python 3.13 --with 'arviz==1.3.0' --with arviz-base \
  --with 'arviz-stats==1.3.2' --with 'arviz-plots==1.3.1' \
  --with 'numpyro==0.21.0' --with 'jax==0.11.1' --with numpy --with matplotlib \
  python build/check_snippets.py --run skills/bayesian-workflow/ \
  2> /tmp/snippet-tier3-task1.err; echo "exit $?"; grep -c '^WARN' /tmp/snippet-tier3-task1.err
```
Expected: `exit 0` and `49` (51 advisories less the two admitted blocks). A raise on the `log_likelihood` block is a finding; resolve it under the Global Constraints rule.

- [ ] **Step 6: Commit**

```bash
git add build/snippet_preamble.py build/test_check_snippets.py
git commit -m "feat(build): bind diverging and posterior_samples in the snippet fixture"
```

Test delta for this task: +2 (one of them stack-gated).

---

### Task 2: Per-block named fixtures

**Files:**
- Modify: `build/snippet_preamble.py` (add `Fixture`, `NAMED_FIXTURES`)
- Modify: `build/check_snippets.py` (import; new `FIXTURE_RE`, `fixture_name`, `_fixture`, `_fixture_names`, `fixture_errors`; changes to `_unrunnable_reason`, `run_errors`, `main`; module docstring)
- Test: `build/test_check_snippets.py`

**Interfaces:**
- Consumes: `snippet_preamble.PREAMBLE`, `snippet_preamble.FIXTURE_VARS`; `check_snippets._bound_by(tree) -> set[str]`, `check_snippets._preamble_names() -> set[str]` (existing).
- Produces:
  - `snippet_preamble.Fixture` — a `NamedTuple` with fields `code: str` (runs after `PREAMBLE`) and `variables: frozenset` (fixture variable names it adds to `FIXTURE_VARS`).
  - `snippet_preamble.NAMED_FIXTURES: dict[str, Fixture]`. It is empty in this task, and Task 3 adds `'comparison'`.
  - `check_snippets.fixture_name(block) -> str | None` — the name in `fixture=<name>`, or `None`.
  - `check_snippets.fixture_errors(path) -> list[str]` — one failure line per block naming an unknown fixture.
  - `check_snippets.main` fails (exit 1) on an unknown fixture at every tier.

- [ ] **Step 1: Write the failing tests**

Append to `build/test_check_snippets.py`:

```python
def _annotated_block(tmp_path, info, code):
    '''A one-block markdown file whose fence info string is `python <info>`.'''
    path = tmp_path / 'block.md'
    path.write_text(f'```python {info}\n{code}\n```\n')
    return check_snippets.iter_code_blocks(path.read_text())[0], path


def test_a_named_fixture_binds_names_for_the_block_that_selects_it(tmp_path, monkeypatch):
    from snippet_preamble import Fixture
    monkeypatch.setitem(check_snippets.NAMED_FIXTURES, 'tiny',
                        Fixture(code='tiny_name = 1\n', variables=frozenset()))
    selected, _ = _annotated_block(tmp_path, 'fixture=tiny', 'print(tiny_name)')
    assert check_snippets.runnable(selected), check_snippets._unrunnable_reason(selected)
    plain, _ = _annotated_block(tmp_path, '', 'print(tiny_name)')
    assert 'unbound names' in check_snippets._unrunnable_reason(plain)


def test_a_named_fixture_widens_the_variables_a_block_may_ask_for(tmp_path, monkeypatch):
    from snippet_preamble import Fixture
    monkeypatch.setitem(check_snippets.NAMED_FIXTURES, 'tiny',
                        Fixture(code='', variables=frozenset({'tau'})))
    code = 's = az.summary(idata, var_names=["tau"])'
    selected, _ = _annotated_block(tmp_path, 'fixture=tiny', code)
    assert check_snippets.runnable(selected), check_snippets._unrunnable_reason(selected)
    plain, _ = _annotated_block(tmp_path, '', code)
    assert 'needs fixture variables' in check_snippets._unrunnable_reason(plain)


def test_an_unknown_fixture_fails_the_gate(tmp_path):
    _, path = _annotated_block(tmp_path, 'fixture=no_such_fixture', 'x = 1')
    errors = check_snippets.fixture_errors(path)
    assert len(errors) == 1 and 'no_such_fixture' in errors[0], errors
    assert check_snippets.main([str(path)]) == 1


@requires_stack
def test_a_named_fixture_runs_between_the_preamble_and_the_block(tmp_path, monkeypatch):
    '''The fixture can use what the preamble binds (N = 40), and the block can
    use what the fixture binds (tiny_name).'''
    from snippet_preamble import Fixture
    monkeypatch.setitem(check_snippets.NAMED_FIXTURES, 'tiny',
                        Fixture(code='tiny_name = N + 1\n', variables=frozenset()))
    _, path = _annotated_block(tmp_path, 'fixture=tiny', 'assert tiny_name == 41')
    assert check_snippets.run_errors(path, timeout=300) == []
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest test_check_snippets.py -q -k "named_fixture or unknown_fixture"`
Expected: the three non-stack tests FAIL. The two `monkeypatch` tests fail on `AttributeError: module 'check_snippets' has no attribute 'NAMED_FIXTURES'`, or on `ImportError: cannot import name 'Fixture'`. `test_an_unknown_fixture_fails_the_gate` fails on `fixture_errors` missing. The stack test SKIPS.

- [ ] **Step 3: Add `Fixture` and `NAMED_FIXTURES` to the preamble module**

In `build/snippet_preamble.py`, directly after the module docstring and before `FIXTURE_VARS`, add:

```python
from typing import NamedTuple


class Fixture(NamedTuple):
    '''A per-block fixture a block selects with `fixture=<name>` in its fence
    info string. `code` runs after PREAMBLE, so it may use every name the
    preamble binds. `variables` are the fixture variables it adds to
    FIXTURE_VARS -- the same honesty rule: widen the code and the set together.'''
    code: str
    variables: frozenset
```

After `PREAMBLE` (before `PINNED`), add:

```python
# Per-block fixtures, keyed by the name a block selects. Only the blocks that
# select one pay for its extra fits; the shared PREAMBLE stays fast.
NAMED_FIXTURES: dict[str, Fixture] = {}
```

In the module docstring, add a paragraph after the `FIXTURE_VARS` paragraph:

```text
NAMED_FIXTURES holds per-block fixtures for blocks written against more than
the running example. A block opts in with `fixture=<name>` in its fence info
string (```python fixture=comparison); its code runs between PREAMBLE and the
block. A name not defined here fails the gate at every tier.
```

- [ ] **Step 4: Teach `check_snippets.py` to select and validate fixtures**

Change the import line `from snippet_preamble import FIXTURE_VARS, PINNED, PREAMBLE` to:

```python
from snippet_preamble import FIXTURE_VARS, NAMED_FIXTURES, PINNED, PREAMBLE
```

After the `TICK_NAME_RE = …` line, add:

```python
FIXTURE_RE = re.compile(r'(?:^|\s)fixture=(\S+)')
```

Directly after the `exempt_report` function, add:

```python
def fixture_name(block) -> str | None:
    '''The named fixture a block selects with `fixture=<name>`, or None.'''
    m = FIXTURE_RE.search(block.info)
    return m.group(1) if m else None


def _fixture(block):
    '''The block's named fixture; None when it selects none, or an unknown one
    (fixture_errors fails that).'''
    name = fixture_name(block)
    return NAMED_FIXTURES.get(name) if name else None


def _fixture_names(fixture) -> set[str]:
    '''Names a named fixture binds; empty when the block selects none.'''
    return _bound_by(ast.parse(fixture.code)) if fixture else set()


def fixture_errors(path: Path) -> list[str]:
    '''One failure per block selecting a fixture snippet_preamble lacks. A
    typo must fail, not quietly drop the block from execution.'''
    out = []
    for block in iter_code_blocks(path.read_text()):
        name = fixture_name(block)
        if name and name not in NAMED_FIXTURES:
            known = ', '.join(sorted(NAMED_FIXTURES)) or 'none'
            out.append(f'{path}:{block.line}: unknown fixture {name!r} '
                       f'(known: {known})')
    return out
```

`_fixture_names` calls `_bound_by`, which is defined further down the module. That is fine: the name resolves when `_fixture_names` is called, not when it is defined.

In `_unrunnable_reason`, replace the block from `missing = _required_vars(tree) - FIXTURE_VARS` through `return ''` with:

```python
    fixture = _fixture(block)
    known_vars = FIXTURE_VARS | (fixture.variables if fixture else frozenset())
    missing = _required_vars(tree) - known_vars
    if missing:
        return f'needs fixture variables {sorted(missing)}'
    free = {n.id for n in ast.walk(tree)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    bound = _preamble_names() | _fixture_names(fixture) | _bound_by(tree)
    unbound = free - bound
    if unbound:
        return f'unbound names {sorted(unbound)}'
    return ''
```

Replace the whole `run_errors` function with:

```python
def run_errors(path: Path, timeout: int = 300) -> list[str]:
    '''Execute every runnable block in an isolated temp cwd; report raises.

    Isolation is mandatory, not tidiness: blocks write model_output.nc, create
    a literal <slug>/ directory, and save PNGs. Warnings are not failures --
    the skill documents several as expected -- so this asserts "did not
    raise", never -W error. A block's named fixture runs between the preamble
    and the block.
    '''
    out = []
    for block in iter_code_blocks(path.read_text()):
        if not runnable(block):
            continue
        fixture = _fixture(block)
        program = '\n'.join([PREAMBLE, fixture.code if fixture else '', block.code])
        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, 'MPLBACKEND': 'Agg'}
            try:
                proc = subprocess.run(
                    [sys.executable, '-c', program],
                    cwd=tmp, env=env, capture_output=True, text=True,
                    timeout=timeout)
            except subprocess.TimeoutExpired:
                out.append(f'{path}:{block.line}: timed out after {timeout}s')
                continue
        if proc.returncode != 0:
            tail = proc.stderr.strip().split('\n')[-1]
            out.append(f'{path}:{block.line}: raised: {tail}')
    return out
```

In `main`, replace

```python
    failures = [e for md in _iter_md(args.paths) for e in parse_errors(md)]
```

with

```python
    failures = [e for md in _iter_md(args.paths)
                for e in parse_errors(md) + fixture_errors(md)]
```

In the module docstring, after the paragraph about the `norun` and `noparse` markers, add:

```text
A third fence token, `fixture=<name>`, opts a block into a per-block fixture
from snippet_preamble.NAMED_FIXTURES, run between the preamble and the block.
It exempts nothing. An unknown name fails at every tier, since a typo would
otherwise quietly drop the block from --run.
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest test_check_snippets.py -q`
Expected: all pass except the stack-gated tests, which skip. Then run the whole file with the stack command from Task 1 Step 4. Expected: all pass, including `test_a_named_fixture_runs_between_the_preamble_and_the_block`.

- [ ] **Step 6: Confirm Tier 1 and Tier 3 are unchanged**

Run: `uv run --python 3.13 python build/check_snippets.py skills/`
Expected: exit 0. No skill selects a fixture yet, so `fixture_errors` finds nothing.
Run the Tier 3 command from Task 1 Step 5.
Expected: `exit 0` and `49` advisories, the same as after Task 1.

- [ ] **Step 7: Commit**

```bash
git add build/snippet_preamble.py build/check_snippets.py build/test_check_snippets.py
git commit -m "feat(build): per-block named fixtures for the snippet gate"
```

Test delta for this task: +4 (one of them stack-gated).

---

### Task 3: The comparison fixture, its blocks, and the re-measure

**Files:**
- Modify: `build/snippet_preamble.py` (add `COMPARISON_FIXTURE`; register it; docstring coverage paragraph)
- Modify: `skills/bayesian-workflow/references/model-comparison.md` (fence info strings of four blocks only)
- Modify: `skills/bayesian-workflow/references/visualize.md` (fence info string of one block only)
- Modify: `CLAUDE.md` (Tier 3 coverage line; build-suite test counts)
- Test: `build/test_check_snippets.py`

**Interfaces:**
- Consumes: `Fixture`, `NAMED_FIXTURES`, `fixture_name`, `runnable`, `_unrunnable_reason`, `_bound_by` (Task 2); `_skill_block` (Task 1).
- Produces: `NAMED_FIXTURES['comparison']`, whose code binds `mcmc_1`, `mcmc_2`, `mcmc_3`, `idata_1`, `idata_2`, `idata_3`, `models`, `idata_m2`, `idata_m3`.

- [ ] **Step 1: Write the failing tests**

Append to `build/test_check_snippets.py`:

```python
COMPARISON_BLOCKS = (
    ('references/model-comparison.md', 'idata_1 = az.from_numpyro(mcmc_1'),
    ('references/model-comparison.md', 'models = {"m1": idata_1'),
    ('references/model-comparison.md', 'az.compare(models, method="stacking")'),
    ('references/model-comparison.md', 'loo_a = az.loo(idata_1'),
    ('references/visualize.md', 'loo2 = az.loo(idata_m2'),
)


def test_the_comparison_fixture_binds_every_name_its_blocks_use():
    import ast

    from snippet_preamble import NAMED_FIXTURES
    bound = check_snippets._bound_by(ast.parse(NAMED_FIXTURES['comparison'].code))
    assert {'mcmc_1', 'mcmc_2', 'mcmc_3', 'idata_1', 'idata_2', 'idata_3',
            'models', 'idata_m2', 'idata_m3'} <= bound


def test_the_comparison_blocks_select_the_comparison_fixture():
    '''Every bayesian-workflow block that compares fitted variants is admitted
    through the comparison fixture. Blocks are found by content, not line.'''
    for relpath, needle in COMPARISON_BLOCKS:
        block = _skill_block(relpath, needle)
        assert check_snippets.fixture_name(block) == 'comparison', needle
        assert check_snippets.runnable(block), check_snippets._unrunnable_reason(block)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest test_check_snippets.py -q -k comparison`
Expected: both FAIL. The first fails with `KeyError: 'comparison'`. The second fails on its first needle, because `fixture_name` returns `None`.

- [ ] **Step 3: Add the comparison fixture**

In `build/snippet_preamble.py`, after `PREAMBLE` and before the `NAMED_FIXTURES` comment, add:

```python
COMPARISON_FIXTURE = '''
# Two more fits of the running example, differing only in the prior on beta
# or in the likelihood, so every site keeps its shape and the preamble's
# coords/dims still apply. model-comparison.md compares three such fits.
def model_wide(x=x, y=None):
    beta = numpyro.sample("beta", dist.Normal(0, 10).expand([x.shape[1]]).to_event(1))
    sigma = numpyro.sample("sigma", dist.HalfNormal(1))
    with numpyro.plate("obs", x.shape[0]):
        numpyro.sample("y_obs", dist.Normal(x @ beta, sigma), obs=y)

def model_robust(x=x, y=None):
    beta = numpyro.sample("beta", dist.Normal(0, 1).expand([x.shape[1]]).to_event(1))
    sigma = numpyro.sample("sigma", dist.HalfNormal(1))
    with numpyro.plate("obs", x.shape[0]):
        numpyro.sample("y_obs", dist.StudentT(4, x @ beta, sigma), obs=y)

def fit(variant, key):
    run = MCMC(NUTS(variant), num_warmup=100, num_samples=200, num_chains=1,
               progress_bar=False)
    run.run(key, x, y=y)
    return run

mcmc_1 = mcmc
mcmc_2 = fit(model_wide, jax.random.PRNGKey(1))
mcmc_3 = fit(model_robust, jax.random.PRNGKey(2))
idata_1, idata_2, idata_3 = (
    az.from_numpyro(run, log_likelihood=True, coords=coords, dims=dims)
    for run in (mcmc_1, mcmc_2, mcmc_3))
models = {"m1": idata_1, "m2": idata_2, "m3": idata_3}

# Deliberately shape-agnostic aliases: visualize.md's pointwise-ELPD block
# only diffs the per-observation ELPD of two fits over the same observations,
# so any two of these fits satisfy what it assumes.
idata_m2, idata_m3 = idata_2, idata_3
'''
```

Then register it, replacing `NAMED_FIXTURES: dict[str, Fixture] = {}` with:

```python
NAMED_FIXTURES: dict[str, Fixture] = {
    'comparison': Fixture(code=COMPARISON_FIXTURE, variables=frozenset()),
}
```

The variant fits carry exactly the running example's sites, so the fixture adds no variables.

- [ ] **Step 4: Annotate the five blocks — fence info strings only**

For each block in `COMPARISON_BLOCKS`, change its opening fence from ```` ```python ```` to ```` ```python fixture=comparison ````. Change nothing else in either file. Find each fence by its needle:

```bash
grep -n 'idata_1 = az.from_numpyro(mcmc_1\|models = {"m1": idata_1\|az.compare(models, method="stacking")\|loo_a = az.loo(idata_1' skills/bayesian-workflow/references/model-comparison.md
grep -n 'loo2 = az.loo(idata_m2' skills/bayesian-workflow/references/visualize.md
```

Each fence is the nearest ```` ```python ```` line above the printed line.

- [ ] **Step 5: Run the tests to verify they pass**

Run: `cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest test_check_snippets.py -q -k comparison`
Expected: 2 passed.

- [ ] **Step 6: Run Tier 3 and resolve every raise**

Run the Tier 3 command from Task 1 Step 5, writing to `/tmp/snippet-tier3-task3.err`:
```bash
uv run --python 3.13 --with 'arviz==1.3.0' --with arviz-base \
  --with 'arviz-stats==1.3.2' --with 'arviz-plots==1.3.1' \
  --with 'numpyro==0.21.0' --with 'jax==0.11.1' --with numpy --with matplotlib \
  python build/check_snippets.py --run skills/bayesian-workflow/ \
  2> /tmp/snippet-tier3-task3.err; echo "exit $?"
grep -c '^WARN' /tmp/snippet-tier3-task3.err
grep -c 'unbound names' /tmp/snippet-tier3-task3.err
grep -c 'needs fixture variables' /tmp/snippet-tier3-task3.err
```
Expected: `exit 0`, then `44`, `18`, `9`. If a newly admitted block raises (stdout names `file:line: raised: …`), apply the Global Constraints rule. If the documentation is wrong, fix the snippet; that is a skill prose edit, so record it as a `> Deviation:` and run the skill lints in Step 8. If the fixture misshapes what the documentation assumes, fix the fixture. Never `norun` it.

- [ ] **Step 7: Re-measure and write the coverage claims**

Count the blocks from this run, never by arithmetic:
```bash
uv run --python 3.13 python -c "import sys; sys.path.insert(0, 'build'); from pathlib import Path; from fences import iter_code_blocks; print(sum(len(iter_code_blocks(p.read_text())) for p in Path('skills/bayesian-workflow').rglob('*.md')))"
```
Expected: `78`. Executed = 78 − the `WARN` count from Step 6.

In `build/snippet_preamble.py`'s docstring, replace the paragraph that begins `Measured against the skill on 2026-09-08` with the measured figures, in this shape:

```text
Measured against the skill on <YYYY-MM-DD> (re-measure whenever this file or
the skill changes; a stale coverage claim is worse than none): 78 fenced
python blocks, all 78 parse. 4 are norun-exempt and <N> are advisory --
<n_unbound> name-incomplete, <n_vars> naming variables outside the fixtures,
7 model-body fragments, 6 elided with `...`. That leaves <E> blocks that
--run executes, <C> of them through the `comparison` fixture and 1 of them
def-only (diagnostics.md's run_diagnostics, which compiles but never runs).
```

In the root `CLAUDE.md` Tier 3 comment, replace `27 of 78 blocks` with `<E> of 78 blocks`, and `The other 51 are advisory` with `The other <78−E> are advisory`. Use the measured values.

Then re-measure the build suite's test counts and update the two `CLAUDE.md` lines that state them (the "Full build-directory tests" line and its "reports … passed, … skipped" note):
```bash
cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q 2>&1 | tail -1
```
The plan's test delta across all three tasks is +8, two of them stack-gated. Write the measured totals, not this delta added to the old ones.

- [ ] **Step 8: Run the skill-change gates**

Run each from the repo root:
```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py
uv run --python 3.13 python build/check_snippets.py skills/
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies
```
Expected: every command exits 0.

- [ ] **Step 9: Commit**

```bash
git add build/snippet_preamble.py build/test_check_snippets.py \
  skills/bayesian-workflow/references/model-comparison.md \
  skills/bayesian-workflow/references/visualize.md CLAUDE.md
git commit -m "feat(build): comparison fixture admits five model-comparison snippets"
```

Test delta for this task: +2.
