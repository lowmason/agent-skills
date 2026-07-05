# tune-hyperparameters Implementation Plan

**Status: COMPLETE (2026-07-05)** — executed via inline TDD; nothing deferred. Final whole-branch review (opus) landed one Important + one Minor fix in commit `7527ed6` (post-Task-5 hardening); all reconciled.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development to implement this plan task-by-task (or executing-plans / inline TDD if subagent dispatch is unavailable — check dispatch health at Task 1). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a standalone `tune-hyperparameters` skill — a regime-classifying HP-tuning decision skill whose one tested artifact is a purged/embargoed temporal-CV splitter (`PurgedTimeSeriesSplit`) feeding a manual Optuna objective, graduating winners to `track-model-experiments`.

**Architecture:** `time_series_cv.py` provides a sklearn-style forward-chaining splitter that adds an embargo gap and optional label-horizon purge to expanding-window CV. The SKILL.md classifies the tuning regime (predictive search vs inference diagnostic), documents leakage-safe search with a verified manual Optuna objective for regime A, and a thin decision table pointing to `bayesian-workflow` for regime B. It guards temporal leakage only; revision leakage is named and deferred to `develop-testing-strategy`.

**Tech Stack:** Python 3.13, NumPy (splitter), scikit-learn + Optuna (regime-A search + integration test), NumPyro/JAX via `bayesian-workflow` (regime B, referenced only). Tests under `uv run --python 3.13`.

## Global Constraints

- **Python style:** single quotes; 4-space indent; target Python 3.13.
- **Splitter is pure NumPy** — no pandas/sklearn import required in `time_series_cv.py` itself (it yields index arrays; sklearn compatibility is by duck-typing `split`/`get_n_splits`).
- **Optuna pattern = manual objective** (`trial.suggest_*` + a loop over `splitter.split(X)` returning the mean CV score) with a **seeded** `TPESampler`. Do NOT use `OptunaSearchCV` (moved to `optuna-integration`, deprecation churn) unless verified clean on the installed version. Verify the Optuna API against the installed version — do not transcribe from memory.
- **The splitter must be honest about scope:** temporal leakage only (train precedes val; embargo; purge). Revision/vintage leakage → `develop-testing-strategy`.
- **The purge branch (`label_horizon > 0`) MUST be exercised by a test.** A point-in-time-only fixture leaves purge untested.
- **No repo-wide `pyproject`;** run via `uv run --python 3.13 --with …`; tests use bare imports, run from `skills/tune-hyperparameters/scripts/`.
- **Cross-skill references use bare skill names.** Frontmatter `description` trigger-only ("Use when…"), third-person, ≤ 1024 chars, no workflow summary.
- **Provenance:** new original work by Lowell Mason (MIT); Optuna/sklearn are documented `--with` deps, not bundled; `build/check_frontmatter.py` and `build/check_provenance.py` must pass.

---

### Task 1: `PurgedTimeSeriesSplit` + unit tests (TDD)

The leakage-safe splitter and its correctness tests (no-future-leakage, embargo gap, the conditional purge path, fold structure).

**Files:**
- Create: `skills/tune-hyperparameters/scripts/time_series_cv.py`
- Test: `skills/tune-hyperparameters/scripts/test_time_series_cv.py`

**Interfaces:**
- Produces (consumed by Task 2 and Task 3):
  - `PurgedTimeSeriesSplit(n_splits=5, test_size=None, embargo=0, label_horizon=0, min_train_size=None)`
  - `.split(X, y=None, groups=None)` → yields `(train_idx, val_idx)` NumPy arrays; train strictly precedes val; `train = [0, s_k - max(embargo, label_horizon))`; val = `[s_k, s_k + test_size)`.
  - `.get_n_splits(X=None, y=None, groups=None)` → `int`.

- [x] **Step 1: Write the failing unit tests**

```python
# skills/tune-hyperparameters/scripts/test_time_series_cv.py
import numpy as np
import pytest

from time_series_cv import PurgedTimeSeriesSplit


def test_no_future_leakage_and_embargo():
    X = np.arange(100).reshape(-1, 1)
    cv = PurgedTimeSeriesSplit(n_splits=5, embargo=3)
    folds = list(cv.split(X))
    assert len(folds) == 5
    for tr, va in folds:
        assert tr.max() < va.min()                 # train strictly before val
        assert va.min() - tr.max() - 1 >= 3        # embargo gap respected


def test_expanding_window_and_n_splits():
    X = np.arange(120).reshape(-1, 1)
    cv = PurgedTimeSeriesSplit(n_splits=4)
    sizes = [len(tr) for tr, _ in cv.split(X)]
    assert sizes == sorted(sizes)                  # non-decreasing train size
    assert cv.get_n_splits() == 4
    assert len(sizes) == 4


def test_purge_is_conditional_on_horizon():
    X = np.arange(100).reshape(-1, 1)
    # horizon=0 keeps the pre-val rows; horizon=3 purges the 3 rows before val.
    f0 = list(PurgedTimeSeriesSplit(n_splits=5, embargo=0, label_horizon=0).split(X))
    f3 = list(PurgedTimeSeriesSplit(n_splits=5, embargo=0, label_horizon=3).split(X))
    assert len(f0) == len(f3)
    for (tr0, va0), (tr3, va3) in zip(f0, f3):
        s = int(va0.min())
        assert (s - 1) in tr0                      # horizon=0: overlapping row present
        for i in range(s - 3, s):
            assert i not in tr3                    # horizon=3: purged
        assert tr3.max() < va3.min()


def test_min_train_size_skips_short_folds():
    X = np.arange(60).reshape(-1, 1)
    cv = PurgedTimeSeriesSplit(n_splits=5, min_train_size=25)
    folds = list(cv.split(X))
    assert folds                                   # at least one fold survives
    for tr, _ in folds:
        assert len(tr) >= 25


def test_rejects_bad_args():
    with pytest.raises(ValueError):
        PurgedTimeSeriesSplit(n_splits=0)
    with pytest.raises(ValueError):
        PurgedTimeSeriesSplit(embargo=-1)
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `cd skills/tune-hyperparameters/scripts && uv run --python 3.13 --with pytest --with numpy python -m pytest -q`
Expected: FAIL — `time_series_cv.py` does not exist (import error).

- [x] **Step 3: Implement the splitter**

```python
# skills/tune-hyperparameters/scripts/time_series_cv.py
'''Leakage-safe temporal cross-validation for hyperparameter tuning.

Forward-chaining (expanding-window) splitter with an embargo gap and an optional
label-horizon purge. For point-in-time targets, sklearn's
TimeSeriesSplit(gap=embargo) already suffices; reach for the purge
(label_horizon > 0) only when the target spans multiple periods so a training
row's label window [i, i+h] overlaps the validation block.

Guards TEMPORAL leakage only (train precedes val; embargo; purge). It does NOT
guard revision/vintage leakage — that belongs to the develop-testing-strategy
skill; a green temporal-CV is not, on its own, 'leakage-free' for revised series.
'''
import numpy as np


def _n_samples(X):
    return X.shape[0] if hasattr(X, 'shape') else len(X)


class PurgedTimeSeriesSplit:
    '''Expanding-window CV with embargo + optional label-horizon purge.

    train = [0, s_k - max(embargo, label_horizon)); val = [s_k, s_k + test_size).
    Yields NumPy index arrays; duck-types sklearn's splitter API (split /
    get_n_splits) so it drops into a manual Optuna objective or sklearn search.
    '''

    def __init__(self, n_splits=5, test_size=None, embargo=0, label_horizon=0,
                 min_train_size=None):
        if n_splits < 1:
            raise ValueError('n_splits must be >= 1')
        if embargo < 0 or label_horizon < 0:
            raise ValueError('embargo and label_horizon must be >= 0')
        self.n_splits = n_splits
        self.test_size = test_size
        self.embargo = embargo
        self.label_horizon = label_horizon
        self.min_train_size = min_train_size

    def get_n_splits(self, X=None, y=None, groups=None):
        return self.n_splits

    def split(self, X, y=None, groups=None):
        n = _n_samples(X)
        test_size = self.test_size or n // (self.n_splits + 1)
        if test_size < 1:
            raise ValueError('test_size resolved to 0; too few samples for n_splits')
        guard = max(self.embargo, self.label_horizon)
        for k in range(self.n_splits):
            s = n - (self.n_splits - k) * test_size
            train_end = s - guard
            if train_end <= 0:
                continue
            if self.min_train_size is not None and train_end < self.min_train_size:
                continue
            train_idx = np.arange(0, train_end)
            val_idx = np.arange(s, min(s + test_size, n))
            yield train_idx, val_idx
```

- [x] **Step 4: Run the tests to verify they pass**

Run: `cd skills/tune-hyperparameters/scripts && uv run --python 3.13 --with pytest --with numpy python -m pytest -q`
Expected: PASS — 5 tests.

> Deviation: the final suite is **8** tests, not 5. Advisor + final review added an over-purge guard (`s-4` survives), a `get_n_splits(X)` realized-count contract assertion, a zero-folds `ValueError` test, and an empirical sklearn `GridSearchCV` integration test. See commits `0b735d4`, `7527ed6`.

- [x] **Step 5: Commit**

```bash
git add skills/tune-hyperparameters/scripts/time_series_cv.py skills/tune-hyperparameters/scripts/test_time_series_cv.py
git commit -m "feat(tune-hyperparameters): PurgedTimeSeriesSplit + unit tests"
```

---

### Task 2: Optuna integration test (verify the manual objective on the installed version)

Validate that the splitter plugs into a real Optuna study via the manual
objective. The passing objective code becomes the verified snippet for the
SKILL.md (Task 3). This task de-risks the Optuna API (advisor: do not transcribe
from memory).

**Files:**
- Modify: `skills/tune-hyperparameters/scripts/test_time_series_cv.py`

**Interfaces:**
- Consumes: `PurgedTimeSeriesSplit` from Task 1.
- Produces: the verified `objective(trial)` pattern (manual `suggest_float` + loop over `cv.split(X)` + mean CV score) used verbatim in the SKILL.md.

- [x] **Step 1: Write the failing integration test**

```python
def test_optuna_manual_objective_integration():
    optuna = pytest.importorskip('optuna')
    from sklearn.linear_model import Ridge
    from sklearn.metrics import mean_squared_error

    rng = np.random.default_rng(0)
    n = 200
    X = rng.normal(size=(n, 3))
    beta = np.array([1.5, -2.0, 0.5])
    y = X @ beta + rng.normal(scale=0.5, size=n)
    cv = PurgedTimeSeriesSplit(n_splits=4, embargo=2)

    def objective(trial):
        alpha = trial.suggest_float('alpha', 1e-3, 1e3, log=True)
        scores = []
        for tr, va in cv.split(X):
            model = Ridge(alpha=alpha).fit(X[tr], y[tr])
            scores.append(mean_squared_error(y[va], model.predict(X[va])))
        return float(np.mean(scores))

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction='minimize',
                                sampler=optuna.samplers.TPESampler(seed=0))
    study.optimize(objective, n_trials=15)
    assert np.isfinite(study.best_value)
    assert 1e-3 <= study.best_params['alpha'] <= 1e3
```

- [x] **Step 2: Run it to verify it fails without the deps, then with**

Run (no optuna): `cd skills/tune-hyperparameters/scripts && uv run --python 3.13 --with pytest --with numpy python -m pytest -q -k optuna`
Expected: SKIPPED (via `importorskip`) — confirms the guard works.
Run (with deps): `uv run --python 3.13 --with pytest --with numpy --with scikit-learn --with optuna python -m pytest -q -k optuna`
Expected: PASS. **If the Optuna API differs on the installed version, adapt the test to the installed API (keep the manual-objective shape) and note the exact version + any change in the commit message.**

- [x] **Step 3: Commit**

```bash
git add skills/tune-hyperparameters/scripts/test_time_series_cv.py
git commit -m "test(tune-hyperparameters): Optuna manual-objective integration (installed-version verified)"
```

---

### Task 3: SKILL.md — regime classifier, regime A, regime B, boundary

Write the skill document. Trigger-only frontmatter; regime-first decision block;
regime A with the **verified** Optuna snippet from Task 2; regime B thin table +
`bayesian-workflow` pointer; the three-way boundary; the revision-leakage caveat.

**Files:**
- Create: `skills/tune-hyperparameters/SKILL.md`

**Interfaces:**
- Consumes: the splitter API (Task 1) and the verified Optuna objective (Task 2).

- [x] **Step 1: Write SKILL.md**

Frontmatter (trigger-only; no workflow summary):

```yaml
---
name: tune-hyperparameters
description: >
  Use when tuning model hyperparameters and unsure how to do it without leaking or
  overfitting — searching regularization strength, tree depth, or learning rate for
  a nowcasting/tabular model, or setting inference knobs (NUTS target_accept /
  max_tree_depth, SVI learning rate/steps, dynamax optax SGD). Trigger on: cross-
  validation for time-series/temporal data, rolling-origin / walk-forward / purged /
  embargoed CV, "which hyperparameters", grid/random/Optuna search, avoiding future
  leakage in CV, when NOT to tune, or graduating a tuned model to a compared variant.
  Guards temporal leakage; revision/vintage leakage belongs to develop-testing-strategy.
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
---
```

Body (house voice — lean, decision-first):
- `# Tune Hyperparameters`
- `## Overview` — the tuning loop above a single fit; core principle: classify the regime, then tune the right objective with the right leakage guard.
- `## Step 0 — classify the regime` — a short decision block. Regime A = searching a held-out predictive metric (regularization/tree/lr for sklearn/boosting). Regime B = setting an inference/optimization knob (NUTS/SVI/optax). Name the stakes: applying regime-A search to regime-B knobs overfits the approximation.
- `## Regime A — leakage-safe predictive search`
  - The leakage trap (naive k-fold trains on the future → over-optimistic HP). Honest note: for **point-in-time** targets, `TimeSeriesSplit(gap=embargo)` suffices; reach for `PurgedTimeSeriesSplit` (this skill's `scripts/time_series_cv.py`) only when the target spans h>1 periods (purge). Embargo always; purge keyed to `label_horizon`.
  - The **verified manual Optuna objective** (copy the Task-2 `objective` shape: `trial.suggest_*` + loop over `cv.split(X)` + mean CV score; `TPESampler(seed=...)`; `direction='minimize'`). One line that Optuna's local store (`sqlite:///…` / journal) is `.gitignore`'d.
  - Nested-CV / held-out note (avoid validation-set overfitting when the search is large).
  - `### When not to tune` — small data, dominant regularization already set by a prior, or fold-to-fold metric variance swamps the HP effect.
  - `### Graduation` — the study winner becomes ONE variant row in `track-model-experiments`' `experiments.md` (`what changed` = "tuned `<class>` via Optuna, `<n>` trials, `<space>`"); trials stay in Optuna's store (`optuna-dashboard` to browse).
- `## Regime B — inference hyperparameters` — a decision table:

  | Knob | Objective | Stopping rule | Owned by |
  |---|---|---|---|
  | NUTS `target_accept` | eliminate divergences | 0 divergences, good E-BFMI | `bayesian-workflow` diagnostics |
  | NUTS `max_tree_depth` | avoid tree saturation | no `reached_max_treedepth` | `bayesian-workflow` |
  | SVI lr / num_steps | ELBO convergence | ELBO plateaus | `bayesian-workflow` |
  | dynamax optax lr | training-loss convergence | loss plateaus, stable | `bayesian-workflow` |

  Anti-pattern warning: **do not** tune these to a held-out predictive metric — that overfits the approximation. Then point to `bayesian-workflow`.
- `## Boundary` — `model-selection-regularization.md` = what to tune & why; `develop-testing-strategy` = leakage as a permanent test invariant; `bayesian-workflow` = inference diagnostics; **this skill** = the search loop + the CV protocol + regime classification + graduation. Bare names.
- `## Scope caveat` — one sentence: guards temporal leakage only; for revised series, revision leakage (using a later vintage than was available as-of) is often the bigger leak and belongs to `develop-testing-strategy`.

- [x] **Step 2: Verify frontmatter lint + trigger-only description**

Run: `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`
Expected: exit 0, `tune-hyperparameters` clean. Confirm description ≤ 1024 chars, starts with "Use when", no workflow summary. `wc -w skills/tune-hyperparameters/SKILL.md` — keep prose concise (< ~600 words beyond the tables/snippet).

> Deviation: SKILL.md prose is ~884 words, above the soft "< ~600 beyond tables/snippet" guideline. The two-regime scope (leakage taxonomy + regime A search + regime-B table + graduation + revision caveat) needed the room; every section is load-bearing and it's level with its sibling `track-model-experiments`. All hard caps (description 655 ≤ 1024 chars, trigger-only) are satisfied.

- [x] **Step 3: Commit**

```bash
git add skills/tune-hyperparameters/SKILL.md
git commit -m "docs(tune-hyperparameters): SKILL.md — regime classifier, leakage-safe CV, regime-B table"
```

---

### Task 4: Wire pointers into sibling skills

Two one-line pointers so the skill is discoverable from its neighbors. Pointer-edits only.

**Files:**
- Modify: `skills/track-model-experiments/SKILL.md`
- Modify: `skills/recommend-probabilistic-model/references/model-selection-regularization.md`

**Interfaces:**
- Consumes: the skill name `tune-hyperparameters` (Task 3).

- [x] **Step 1: Edit track-model-experiments**

In `skills/track-model-experiments/SKILL.md`, in the "When to use" or graduation-relevant spot, add a bare-name pointer: a tuned winner from the `tune-hyperparameters` skill graduates to a variant row here. Keep it one sentence, bare skill name, no new file link.

- [x] **Step 2: Edit model-selection-regularization.md**

In `skills/recommend-probabilistic-model/references/model-selection-regularization.md`, add one sentence: for the *operational* tuning loop and leakage-safe CV, use the `tune-hyperparameters` skill (this file stays the *what/why*). Bare name.

- [x] **Step 3: Verify lints + no broken links**

Run:
```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py
```
Expected: both exit 0. Confirm no `../` link breakage (bare skill names only). Note: `check_provenance.py` will fail until Task 5 adds the NOTICE entry **if** the SKILL.md already exists — if so, that failure is expected here and resolved in Task 5; re-run provenance after Task 5. (Frontmatter must pass now.)

- [x] **Step 4: Commit**

```bash
git add skills/track-model-experiments/SKILL.md skills/recommend-probabilistic-model/references/model-selection-regularization.md
git commit -m "docs: point track-model-experiments + model-selection-regularization to tune-hyperparameters"
```

---

### Task 5: Provenance, install, and full sweep

Register in `NOTICE` + `README`, symlink into `~/.claude/skills/`, run the whole battery green.

**Files:**
- Modify: `NOTICE`
- Modify: `README.md`

**Interfaces:**
- Consumes: `skills/tune-hyperparameters/` (Tasks 1–3).

- [x] **Step 1: Add to NOTICE**

Add `tune-hyperparameters/` to the "original works by Lowell Mason, MIT licensed" list in `NOTICE`.

- [x] **Step 2: Add to README**

Add a row to the **Mine** table (`| [`tune-hyperparameters`](skills/tune-hyperparameters/) | … |` — one dense sentence: regime-classifying HP tuning; a purged/embargoed temporal-CV splitter feeding a manual Optuna objective; leakage-safe search that graduates winners to `track-model-experiments`; guards temporal leakage, defers revision leakage to `develop-testing-strategy`), and append `tune-hyperparameters` to the "My original skills" line (~146).

- [x] **Step 3: Run the provenance + frontmatter lints**

Run:
```bash
uv run --python 3.13 python build/check_provenance.py
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```
Expected: both exit 0.

- [x] **Step 4: Run the skill's test suite (regression)**

Run: `cd skills/tune-hyperparameters/scripts && uv run --python 3.13 --with pytest --with numpy --with scikit-learn --with optuna python -m pytest -q`
Expected: PASS — 6 tests (5 splitter unit + 1 Optuna integration).

> Deviation: final suite is **8** tests (7 splitter unit + 1 Optuna) after review hardening — see the Task 1 Step 4 note. scikit-learn is now a genuine test dep (the `GridSearchCV` contract test), already in this command.

- [x] **Step 5: Install the skill (symlink) + confirm**

```bash
ln -sfn /Users/lowell/Projects/agent-skills/skills/tune-hyperparameters ~/.claude/skills/tune-hyperparameters
test -f ~/.claude/skills/tune-hyperparameters/SKILL.md && echo INSTALL-OK
```

- [x] **Step 6: Commit**

```bash
git add NOTICE README.md
git commit -m "docs(tune-hyperparameters): register in NOTICE + README; install"
```

---

## Verification (whole plan)

```bash
# Skill suite (6 tests)
cd skills/tune-hyperparameters/scripts && \
  uv run --python 3.13 --with pytest --with numpy --with scikit-learn --with optuna python -m pytest -q && cd -

# Lints (both find the new skill and pass)
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py

# Existing build-tooling suite unaffected
cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q && cd -

# Install resolves
test -f ~/.claude/skills/tune-hyperparameters/SKILL.md && echo INSTALL-OK
```

Then run the plan-completion protocol (writing-plans § Plan Completion Protocol): resolve-before-defer gate → markup → deferred items → retire plan 9 (+ spec `tune-hyperparameters.md`, since no other live plan implements it) to `completed/`. Finish the branch (finishing-a-development-branch): merge / PR / cleanup.

## Self-Review notes

- **Spec coverage:** splitter with embargo+purge (Task 1) ✓; purge path tested with h>1 fixture, per E3/advisor (Task 1 `test_purge_is_conditional_on_horizon`) ✓; Optuna manual objective verified against installed version, per E2/advisor (Task 2) ✓; regime classifier + regime A + regime B table + boundary + revision caveat, E1/E4/E6 (Task 3) ✓; graduation E5 (Task 3 doc) ✓; wiring (Task 4) ✓; provenance + install (Task 5) ✓.
- **Type consistency:** `PurgedTimeSeriesSplit` signature identical across Tasks 1–3; the Task-2 `objective` shape is reused verbatim in the SKILL.md snippet.
- **Known risks:** (1) Optuna API drift — Task 2 Step 2 explicitly verifies against the installed version and permits adaptation. (2) `check_provenance.py` ordering — same as plan 8: it fails once the SKILL.md exists without a NOTICE entry, so Task 4's provenance check may report red until Task 5; called out inline. (3) sklearn `mean_squared_error` is stable across versions; no `squared=` kwarg used (deprecated in newer sklearn) — the test takes the plain MSE.
