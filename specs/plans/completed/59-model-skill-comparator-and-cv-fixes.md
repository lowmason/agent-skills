# Model-Skill Comparator and CV Fixes Implementation Plan

**Status: COMPLETE (2026-10-21)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix four audited defects in the model-lifecycle skills: track-model-experiments' comparator drops non-Bayesian winners in silence and mis-ranks or crashes on state-space log-likelihoods, tune-hyperparameters' purged splitter leaks on panels, and tune's Regime B router contradicts bayesian-workflow.

**Architecture:** Two bundled scripts change test-first, and the skill text that describes them changes with them. `time_series_cv.py` splits sorted unique periods when `split()` gets one period label per row. `compare_experiments.py` names the ledger rows it could not rank, qualifies its best marker while one exists, fills the ledger's metric cells, and refuses log-likelihoods that LOO cannot use. bayesian-workflow gains a short SVI-convergence reference and a state-space warning. tune's Step 0 gets a classification rule, and its Regime B rows point at bayesian-workflow's files. A micro-test against a no-guidance control checks the new router wording.

**Tech Stack:** Python 3.13 through `uv run`, NumPy, ArviZ 1.x (arviz-base, arviz-stats) with the h5netcdf/h5py pair, NumPyro and JAX in the tests, scikit-learn and Optuna in tune's extras, pytest through `build/run_suites.py`, and `claude -p` on Sonnet for the micro-test.

**Spec:** none. The four backlog items carry their own fixes: `specs/deferred_items.md`, section `audit-3-10-26 routing (no plan; re-verification pass, branch claude/quizzical-hermann-814d89) — 2026-10-18`, the items that open "Stop the experiment comparator from dropping non-Bayesian winners in silence" (G1), "Make tune-hyperparameters' purged splitter split periods, not rows" (G2), "Guard the experiment comparator against bayesian-workflow's state-space shapes" (G3, its guards half) and "Align tune-hyperparameters' Regime B router with bayesian-workflow" (G4). The findings are in `specs/completed/audit-3-10-26.md`, section "G-A. Plannable now: true under any design answer".

## Global Constraints

Every task's requirements include these.

- **Scope fence: the four items only.** G1 parts (a)–(e), G2, G3's guards half and G4. Out of scope: G3's criterion half (leave-future-out or blocked K-fold for forecast decisions, and a precomputed-score mode for the comparator), the model-lifecycle spec, and everything gated on the owner calls O1–O3 (track's scope, and who evaluates models that are neither Bayesian nor neural), including G5's graduation clause and both skills' descriptions. X7 (the audit finding that the comparator read diagnostics keys `diagnose_model.py` never writes), which the audit's G-A plan also took, closed on 2026-10-19 in commit `4326341`.
- **Leave these alone:** `specs/deferred_items.md` (only the plan completion protocol edits it, and plans 60 and 61 edit it too), the frontmatter `description` of every skill, `skills/bayesian-workflow/references/model-comparison.md`, `install.py`'s `DEPENDENCIES` (DF4) and `CLAUDE.md`.
- **One shared file.** Plan 61 (hook-template fixes) also edits the root `README.md`, in its hook rows (`ruff-check.sh`, "first-token heuristic"). This plan edits only the track-model-experiments and tune-hyperparameters rows, so the two merge cleanly. Whichever plan lands second re-reads `README.md` on the new base before its README step.
- **Red first.** Write each task's tests, run them, and read each failure reason before you write code. Each task lists its expected failures and their reasons. A red run that fails for another reason stops the task.
- **Test counts are deltas** from these baselines, measured on 2026-10-21 at `0fd27b6`: track-model-experiments `13 passed`, and tune-hyperparameters `6 passed, 2 skipped`, or `8 passed` with `--extras`.
- **Simple commands.** Each command stands alone, with no `cd … &&`, pipe or loop, because a worktree-isolated session refuses compound shell. Run suites through `build/run_suites.py` from the repo root, and the build tests with `uv run --directory build`. Use absolute paths or `git -C` in a parallel shell call.
- **Find text, not line numbers.** Each replace block quotes the exact text to find. It occurs once in its file at that point of the plan. The replay below checked each one.
- **Match each file's style.** Both scripts and their tests use single quotes. bayesian-workflow's Markdown code uses double quotes. New prose follows the repo's plain-technical-English rule (`rules/write-with-asd-ste100.md`).
- **Cross-skill paths.** Write a backticked path into another skill in full (`bayesian-workflow/references/state-space.md`): `check_frontmatter.py` resolves a bare `references/…` path inside the citing skill. A new path from one skill into another needs an `install.py` `DEPENDENCIES` entry or a `SOFT_REFERENCES` entry in `build/test_runtime_support.py`. Task 6 adds the only new edge.
- **Commit lints.** When the pre-commit hook is on (`git config core.hooksPath` prints a path that ends in `build/githooks`), each commit runs the nine commit lints. When it is off, run `bash build/run_commit_lints.sh` before each commit. Task 7 runs it once more.
- **Commit trailer.** Each commit message ends with the executing session's own `Co-Authored-By:` line. Subagent-authored commits keep that same line. Check with `git log -1 --format=%B`.
- **Micro-test isolation (Task 6).** Each rep is a decision-only `claude -p --tools ""` call from its own new folder under `/tmp/p59micro/`, never the repo and never `/tmp` itself. The kit lives outside the repo, at `~/.cache/agent-skills/scratch/plan59-micro/`. The micro-test costs about $10–15.
- **Push or merge nothing** without the owner's go-ahead.

## Decisions

- **D1** (owner, brief, 2026-10-21): in a `/deferred` pass the owner selected four items with disposition Plan, to be planned without a spec and named for the theme: G1, G2, G3's guards half and G4. Applied in: Global Constraints (the scope fence) and Tasks 1–6.
- **D2** (owner, plan review, 2026-10-21): the best marker, the option "Label it": "DF1. The top row reads '**best among ELPD-compared variants**' and the run exits 0 with a note naming the unranked rows. A new row waiting for its first fit does not block the run." Applied in: Task 2, unchanged.
- **D3** (owner, plan review, 2026-10-21): the metric cells, the option "Fill the cells": "DF2. The comparator writes ELPD, ΔELPD, max R̂, div, PPC and psense into each ranked row, by the template's exact column names. Unranked rows keep their cells." Applied in: Task 3, unchanged.
- **D4** (owner, plan review, 2026-10-21): the SVI reference, the option "Write svi.md": "DF3. Task 5 adds bayesian-workflow/references/svi.md: a flat ELBO trace across seeds, loo_approximate_posterior and vsbc_diagnostic, with a block that Tier 3 runs. The optax row reads 'no skill owns this yet'." Applied in: Tasks 5 and 6, unchanged.
- **D5** (owner, plan review, 2026-10-21): the rest of the plan, the option "Approve as written": "The other defaults (DF4–DF12) stand: the soft tune → bayesian-workflow edge, period labels as groups, the micro-test on Sonnet, no NOTICE change, and the rest." The question named Task 6's micro-test as 75 `claude -p` calls on Sonnet, about $10–15. Applied in: Tasks 1–7, unchanged.

---

## Planning record

### Facts measured while planning (2026-10-21, at `0fd27b6`)

- **The anchors moved, but the defects did not.** Commit `4326341` (2026-10-19) and plan 53 (portability, executed and merged) edited `compare_experiments.py`, track's SKILL.md and tune's SKILL.md after the 2026-10-18 re-verification. Every defect below is still present. The tasks find text, so they cite no line numbers.
- **G1, reproduced.** A ledger with two NumPyro variants and a row for a tuned Ridge model: auto-discovery exits 0, stamps `**best**` on the Bayesian winner and never names the Ridge row. `--folders bayes-v2 ridge-tuned` ends in a raw `FileNotFoundError` traceback from h5py. After either run every metric cell in the Variants table is still empty, because `update_ledger` changes only the status cell and the COMPARISON block. Track's SKILL.md still says "the comparator fills the right half after every run".
- **G2, reproduced** on 3 entities × 10 periods, sorted by period. Folds that share a period: 4 of 5 at `embargo=0` and 2 of 5 at `embargo=1`. At `embargo=2` no fold shares a period, but the whole-period gap is 0 in every fold.
- **G3, reproduced.** A summed `numpyro.factor` gives a log-likelihood variable with dims `('chain', 'draw')` only. `az.compare` ranks two such variants with SE 0 and weights 1.0 and 0.0, and the comparator exits 0. arviz-stats only warns that "the point-wise LOO is the same with the sum LOO". Two observed sites raise `TypeError: Encountered error trying to compute ELPD from model t-full.`, whose cause reads "Found several log likelihood arrays ['y_obs', 'z_obs'], var_name cannot be None".
- **A trap in G3's remedy.** A per-step `numpyro.factor`, which is the remedy, gives a log-likelihood with a time dimension, but its `observed_data` entry has shape `(T, 0)`, so its size is 0. `observation_count` reads `observed_data`, so today it refuses the remedy beside a normal variant: `{'f-full': 0, 'm-intercept': 200}`. The count must come from the log-likelihood variable (DF7).
- **The multi-source remedy works.** `ll = idata["log_likelihood"]` and then `idata["log_likelihood"] = (ll["y_obs"] + ll["z_obs"]).to_dataset(name="y")` leave one variable over `obs`, and the comparator ranks the pair (SE 9.9 and 11.0). `dims={"ll": ["time"]}` names a factor's axis `time` when ArviZ converts it.
- **G4's SVI tools exist on the pins.** NumPyro 0.22.0 ships `numpyro.infer.calibration.vsbc_diagnostic`. Its `ks_pvalues` is a dict keyed by site name, and on a generative model it needs `observed_sites` named. arviz-stats 1.3.3 ships `loo_approximate_posterior(data, log_p, log_q, ...)`. The three checks run in about 4 s on the snippet preamble's running example.
- **The new tune → bayesian-workflow edge is detected.** A path to `bayesian-workflow/references/diagnostics.md` in tune's SKILL.md fails the dependency-drift test with `('skill:tune-hyperparameters', 'skill:bayesian-workflow')` until a `SOFT_REFERENCES` entry exists.
- **A lint catches a bare cross-skill path.** "bayesian-workflow's `references/state-space.md`" in track's SKILL.md failed `check_frontmatter.py` with "referenced path does not exist". The full path passes.
- **The micro-test kit works.** One decision-only call (arm A, scenario S4) ran on `claude-sonnet-5-5` through Claude Code 2.1.304 and cost $0.15. It was a smoke call, outside the measured set.

### Prototype and replay

On 2026-10-21, Tasks 1–6 (all but the micro-test runs) were written test-first in a scratch clone of `0fd27b6`. A script then replayed this plan's blocks in a fresh clone of `0fd27b6`, one step at a time in task order, with one commit per task:

- Each find block matched its file exactly once, both as the replay applied it and as this plan renders it.
- Each red run printed the failures its step lists, and each green run printed its count.
- Snippet Tiers 1, 2 and 3 exited 0, and Tier 3 executed the new `svi.md` block (no `WARN` line names it).
- All nine commit lints passed at the end.
- The replayed files came out byte-identical to the prototype.

The micro-test's measured runs (Task 6, Steps 4, 5, 9 and 10) have not happened: planning ran only the one smoke call above. Task 6's scenarios, grading rules and pass bars are the micro-test's pre-registration.

### Settled defaults (the owner approved these at plan review: D2–D5)

- **DF1, the best marker is labelled, not frozen** (G1 a). While a ledger row went uncompared, the top row's status reads `**best among ELPD-compared variants**`, and the run exits 0 with a note on stderr. The alternative is to refuse to move `**best**` at all. Refusing would block every run while a newly opened row waits for its first fit, which the ledger's own workflow creates.
- **DF2, the comparator fills the metric cells** (G1 e), matched by the template's exact column names (`ELPD`, `ΔELPD`, `max R̂`, `div`, `PPC`, `psense`). The alternative is to correct track's SKILL.md to say the comparator writes only the COMPARISON block and the marker. A row the comparator did not rank keeps its cells.
- **DF3, bayesian-workflow gets a short SVI reference** (G4 b, Task 5), and the dynamax optax row reads "no skill owns this yet". The alternative marks both the SVI and the optax rows "no skill owns this yet" and drops Task 5.
- **DF4, the new tune → bayesian-workflow edge is soft:** a `SOFT_REFERENCES` entry, not a hard `DEPENDENCIES` entry. Regime A, the search loop, runs without bayesian-workflow. The Regime B rows only say where that doctrine lives.
- **DF5, `main()` reads the ledger's ids, through `ledger_ids()`.** The item says `compare()` reads them. `compare()` also runs with no ledger, so it keeps its signature and its two-value return.
- **DF6, the Variants table is found by its header:** the first table outside the COMPARISON block whose header starts with `id` and has a `status` column. The old code toggled the marker on any table row. A ledger without such a table gets a note on stderr, so the narrower match cannot fail in silence.
- **DF7, the observation count comes from the one log-likelihood variable**, not from `observed_data` (the trap above).
- **DF8, the splitter takes period labels as `groups` at `split()` time** (sklearn's convention: `GridSearchCV.fit(X, y, groups=...)` passes them on), not a constructor argument. Without `groups` the folds are unchanged, and a test pins that.
- **DF9, the micro-test runs on Sonnet**, decision-only: 5 scenarios × 3 arms × 5 reps, 75 calls.
- **DF10, `state-space.md` does not claim exact LOO.** It says the per-step terms of a marginalized model are one-step-ahead densities, so PSIS-LOO over them is not exact leave-one-out. The forecast criterion stays with the open lifecycle item.
- **DF11, documentation follows the code:** the root `README.md` rows for track and tune and the bayesian-workflow README's file tree change where this plan makes them wrong.
- **DF12, no NOTICE change.** `svi.md` is original prose. It documents NumPyro's `vsbc_diagnostic` and arviz-stats' `loo_approximate_posterior` from executing them, and it cites Yao et al. 2018 and Magnusson et al. 2019 by author and year, in `publications.md`. NOTICE itemizes a bayesian-workflow reference only when it adapts third-party content (model-comparison.md, jax-numerics.md), and the original `state-space.md` has no line either.

### Expected leftovers for the completion protocol

- tune's description still triggers on "dynamax optax SGD", which no skill owns after Task 6. Descriptions are G5 work, gated on O1–O3, so defer this there.
- G3's criterion half stays in the lifecycle-spec item. This plan ticks only G3's guards half.

## File structure

| File | Change | Tasks |
|---|---|---|
| `skills/tune-hyperparameters/scripts/time_series_cv.py` | `split(X, y, groups)` splits periods | 1 |
| `skills/tune-hyperparameters/scripts/test_time_series_cv.py` | panel, back-compat and sklearn tests | 1 |
| `skills/tune-hyperparameters/SKILL.md` | CV protocol (panel, import), Graduation, Step 0, Regime B | 1, 2, 6 |
| `skills/track-model-experiments/scripts/compare_experiments.py` | unranked rows, marker, metric cells, log-likelihood guards | 2, 3, 4 |
| `skills/track-model-experiments/scripts/test_compare_experiments.py` | 10 new tests | 2, 3, 4 |
| `skills/track-model-experiments/SKILL.md` | When to use, the ledger, guardrails | 2, 3, 4 |
| `skills/bayesian-workflow/references/state-space.md` | comparison warning and gotcha | 4 |
| `skills/bayesian-workflow/references/svi.md` | new: SVI convergence checks | 5 |
| `skills/bayesian-workflow/references/publications.md` | two citations | 5 |
| `skills/bayesian-workflow/SKILL.md`, `skills/bayesian-workflow/README.md` | one pointer, one tree line | 5 |
| `build/test_runtime_support.py` | one `SOFT_REFERENCES` entry | 6 |
| `README.md` | the track and tune rows | 1, 2, 4, 6 |
| `specs/verification/59-regime-b-router-microtest.md` | new: the micro-test record | 6 |

---

### Task 1: Split periods, not rows, in the purged splitter (G2)

**Files:**
- Modify: `skills/tune-hyperparameters/scripts/time_series_cv.py`
- Test: `skills/tune-hyperparameters/scripts/test_time_series_cv.py`
- Modify: `skills/tune-hyperparameters/SKILL.md` (Regime A: the CV protocol and the objective)
- Modify: `README.md` (the tune-hyperparameters row)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: `PurgedTimeSeriesSplit.split(X, y=None, groups=None)` and `get_n_splits(X=None, y=None, groups=None)`. `groups` holds one period label per row, of any sortable type. `test_size`, `embargo`, `label_horizon` and `min_train_size` count periods. Without `groups` each row is one period, so the folds are unchanged. A `groups` whose length differs from the row count raises `ValueError`. A private helper `_period_index(n, groups) -> (np.ndarray, int)` gives each row's period index and the period count.

- [x] **Step 1: Write the failing tests**

Append this block to the end of `skills/tune-hyperparameters/scripts/test_time_series_cv.py`, with two blank lines between the file's last line and the block:

```python
def _panel_periods(n_entities=3, n_periods=20, entity_major=False):
    '''Each row's period in a long-format panel of n_entities series.

    Period-major rows run (t0 e0, t0 e1, ...); entity-major rows run
    (e0 t0, e0 t1, ...), so the labels are not sorted.
    '''
    periods = np.arange(n_periods)
    if entity_major:
        return np.tile(periods, n_entities)
    return np.repeat(periods, n_entities)


@pytest.mark.parametrize('entity_major', [False, True])
@pytest.mark.parametrize('embargo', [0, 1, 2])
def test_panel_folds_split_whole_periods(embargo, entity_major):
    period = _panel_periods(entity_major=entity_major)
    X = np.zeros((period.size, 1))
    folds = list(PurgedTimeSeriesSplit(n_splits=5, embargo=embargo).split(X, groups=period))
    assert len(folds) == 5
    for tr, va in folds:
        assert not set(period[tr]) & set(period[va])                # no period on both sides
        assert period[va].min() - period[tr].max() - 1 >= embargo   # the gap counts whole periods
        assert len(va) == 3 * len(set(period[va]))                  # val holds every row of its periods


def test_panel_sizes_count_periods():
    period = _panel_periods(n_periods=20)
    X = np.zeros((period.size, 1))
    cv = PurgedTimeSeriesSplit(n_splits=4, test_size=2, min_train_size=13)
    folds = list(cv.split(X, groups=period))
    assert len(folds) == 3                                   # the fold with 12 train periods is pruned
    for tr, va in folds:
        assert len(set(period[va])) == 2                     # test_size counts periods
        assert len(set(period[tr])) >= 13                    # min_train_size counts periods
    assert cv.get_n_splits(X, groups=period) == len(folds)   # get_n_splits forwards groups


def test_one_row_per_period_matches_row_mode():
    X = np.arange(100).reshape(-1, 1)
    cv = PurgedTimeSeriesSplit(n_splits=5, embargo=2, label_horizon=3, min_train_size=10)
    rows = list(cv.split(X))
    periods = list(cv.split(X, groups=np.arange(100)))
    assert len(rows) == len(periods)
    for (tr_r, va_r), (tr_p, va_p) in zip(rows, periods):
        np.testing.assert_array_equal(tr_r, tr_p)
        np.testing.assert_array_equal(va_r, va_p)


def test_groups_length_must_match_rows():
    X = np.zeros((10, 1))
    with pytest.raises(ValueError, match='groups'):
        list(PurgedTimeSeriesSplit(n_splits=2).split(X, groups=np.arange(9)))


def test_sklearn_search_with_panel_groups():
    pytest.importorskip('sklearn')
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import GridSearchCV

    rng = np.random.default_rng(0)
    period = _panel_periods(n_periods=40)
    X = rng.normal(size=(period.size, 2))
    y = X @ np.array([1.0, -1.0]) + rng.normal(scale=0.3, size=period.size)
    cv = PurgedTimeSeriesSplit(n_splits=5, embargo=1, min_train_size=15)
    realized = len(list(cv.split(X, groups=period)))
    assert realized == 4                                     # 9 train periods < 15: pruned
    assert cv.get_n_splits(X, groups=period) == realized
    gs = GridSearchCV(Ridge(), {'alpha': [0.1, 1.0, 10.0]}, cv=cv)
    gs.fit(X, y, groups=period)                              # sklearn hands groups to split()
    assert gs.n_splits_ == realized
```

- [x] **Step 2: Run them and check that they fail for the stated reasons**

Run (scikit-learn and Optuna come with `--extras`):

```bash
uv run --python 3.13 python build/run_suites.py tune-hyperparameters --extras -- -rf --tb=line
```

Expected: 9 of the 10 new tests fail, and the baseline's tests still pass (`9 failed, 9 passed` at `0fd27b6`). Without `groups` support, `split()` ignores the labels and splits rows:
- `test_panel_folds_split_whole_periods[0-False]`: a period sits on both sides (`assert not ({0, 1, 2, 3} & {3, 4, 5, 6})`).
- `[1-False]` and `[2-False]`: the whole-period gap is 0 (`assert ((3 - 2) - 1) >= 1`, and `>= 2`).
- `[0-True]`, `[1-True]`, `[2-True]` (entity-major rows): each validation fold holds 10 rows of 10 periods, not every row of its periods (`assert 10 == (3 * 10)`).
- `test_panel_sizes_count_periods`: `assert 4 == 3` (no fold is pruned, because sizes count rows).
- `test_groups_length_must_match_rows`: `Failed: DID NOT RAISE ValueError`.
- `test_sklearn_search_with_panel_groups`: `assert 5 == 4`.

`test_one_row_per_period_matches_row_mode` passes now and must still pass after Step 3: it pins that the change leaves row mode alone.

- [x] **Step 3: Split periods**

In `skills/tune-hyperparameters/scripts/time_series_cv.py`, find:

```python
Forward-chaining (expanding-window) splitter with an embargo gap and an optional
label-horizon purge. For point-in-time targets, sklearn's
TimeSeriesSplit(gap=embargo) already suffices; reach for the purge
(label_horizon > 0) only when the target spans multiple periods so a training
row's label window [i, i+h] overlaps the validation block.
```

Replace it with:

```python
Forward-chaining (expanding-window) splitter with an embargo gap and an optional
label-horizon purge, all counted in periods. Without groups each row is one
period, which fits a single series. For a long-format panel (several series
observed at the same periods), pass each row's period as groups: the folds then
split whole periods, so no period lands in both train and validation.

For a single series with a point-in-time target, sklearn's
TimeSeriesSplit(gap=embargo) already suffices. It splits rows, so on a panel it
leaks the way this splitter does without groups. Reach for the purge
(label_horizon > 0) only when the target spans multiple periods so a training
row's label window [i, i+h] overlaps the validation block.
```

In `skills/tune-hyperparameters/scripts/time_series_cv.py`, find:

```python
def _n_samples(X):
    return X.shape[0] if hasattr(X, 'shape') else len(X)
```

Replace it with:

```python
def _n_samples(X):
    return X.shape[0] if hasattr(X, 'shape') else len(X)


def _period_index(n, groups):
    '''Each row's position among the sorted unique periods, and the period count.

    Without groups each row is its own period, in row order.
    '''
    if groups is None:
        return np.arange(n), n
    labels = np.asarray(groups)
    if labels.shape[0] != n:
        raise ValueError(f'groups has {labels.shape[0]} labels for {n} rows')
    periods, index = np.unique(labels, return_inverse=True)
    return index.ravel(), len(periods)
```

In `skills/tune-hyperparameters/scripts/time_series_cv.py`, find:

```python
    '''Expanding-window CV with embargo + optional label-horizon purge.

    train = [0, s_k - max(embargo, label_horizon)); val = [s_k, s_k + test_size).
    Yields NumPy index arrays; duck-types sklearn's splitter API (split /
    get_n_splits) so it drops into a manual Optuna objective or sklearn search.
    '''
```

Replace it with:

```python
    '''Expanding-window CV with embargo + optional label-horizon purge.

    In periods: train = [0, s_k - max(embargo, label_horizon)); val = [s_k,
    s_k + test_size). test_size, embargo, label_horizon and min_train_size all
    count periods; split(X, groups=period) maps them back to rows, and without
    groups each row is one period. Yields NumPy row-index arrays; duck-types
    sklearn's splitter API (split / get_n_splits) so it drops into a manual
    Optuna objective or sklearn search (GridSearchCV.fit(X, y, groups=period)).
    '''
```

In `skills/tune-hyperparameters/scripts/time_series_cv.py`, find:

```python
        if X is None:
            return self.n_splits
        return sum(1 for _ in self.split(X))

    def split(self, X, y=None, groups=None):
        n = _n_samples(X)
        test_size = self.test_size or n // (self.n_splits + 1)
        if test_size < 1:
            raise ValueError('test_size resolved to 0; too few samples for n_splits')
```

Replace it with:

```python
        if X is None:
            return self.n_splits
        return sum(1 for _ in self.split(X, y, groups))

    def split(self, X, y=None, groups=None):
        period, n_periods = _period_index(_n_samples(X), groups)
        test_size = self.test_size or n_periods // (self.n_splits + 1)
        if test_size < 1:
            raise ValueError('test_size resolved to 0; too few periods for n_splits')
```

In `skills/tune-hyperparameters/scripts/time_series_cv.py`, find:

```python
            s = n - (self.n_splits - k) * test_size
```

Replace it with:

```python
            s = n_periods - (self.n_splits - k) * test_size
```

In `skills/tune-hyperparameters/scripts/time_series_cv.py`, find:

```python
            train_idx = np.arange(0, train_end)
            val_idx = np.arange(s, min(s + test_size, n))
            yield train_idx, val_idx
```

Replace it with:

```python
            train_idx = np.flatnonzero(period < train_end)
            val_idx = np.flatnonzero((period >= s) & (period < s + test_size))
            yield train_idx, val_idx
```

In `skills/tune-hyperparameters/scripts/time_series_cv.py`, find:

```python
                f'no folds could be formed (n={n}, n_splits={self.n_splits}, '
```

Replace it with:

```python
                f'no folds could be formed (periods={n_periods}, n_splits={self.n_splits}, '
```

- [x] **Step 4: Run the tests and check that they pass**

```bash
uv run --python 3.13 python build/run_suites.py tune-hyperparameters --extras -- -rf --tb=line
```

Expected: +10 passed over the baseline (`18 passed` at `0fd27b6`). Then without the extras:

```bash
uv run --python 3.13 python build/run_suites.py tune-hyperparameters
```

Expected: +9 passed and +1 skipped over the bare baseline (`15 passed, 3 skipped` at `0fd27b6`). The new sklearn test skips without scikit-learn.

- [x] **Step 5: Make the skill text match the code**

The point-in-time bullet now says what it covers (a single series), a panel bullet says how to split one, and the import resolves from outside `scripts/`.

In `skills/tune-hyperparameters/SKILL.md`, find:

```markdown
- **Point-in-time target** (label known at the row's own timestamp): sklearn's
  `TimeSeriesSplit(gap=embargo)` already suffices. Add an **embargo** — a gap of
  a few periods between train and val — to absorb autocorrelation bleed at the
  boundary.
```

Replace it with:

```markdown
- **Point-in-time target, single series** (one row per period, label known at
  the row's own timestamp): sklearn's `TimeSeriesSplit(gap=embargo)` already
  suffices. Add an **embargo** — a gap of a few periods between train and val —
  to absorb autocorrelation bleed at the boundary.
- **Panel** (several series observed at the same periods, one row per series
  and period): split periods, not rows. `TimeSeriesSplit` splits rows, so the
  same period lands in both train and validation. Use this skill's splitter
  (below) and pass each row's period: `cv.split(X, groups=period)`.
```

In `skills/tune-hyperparameters/SKILL.md`, find:

````markdown
```python
from time_series_cv import PurgedTimeSeriesSplit
````

Replace it with:

````markdown
```python
import sys
sys.path.insert(0, '<this-skill-dir>/scripts')   # or copy time_series_cv.py beside your code
from time_series_cv import PurgedTimeSeriesSplit
````

In `skills/tune-hyperparameters/SKILL.md`, find:

```markdown
so the binding one is `max`, not the sum. It duck-types sklearn's splitter API,
so it drops straight into the objective below.
```

Replace it with:

```markdown
so the binding one is `max`, not the sum. `test_size`, `embargo`,
`label_horizon` and `min_train_size` all count periods: on a panel, pass
`groups=period` to `split` (and to `GridSearchCV.fit`), and without it each row
is one period. It duck-types sklearn's splitter API, so it drops straight into
the objective below.
```

In `skills/tune-hyperparameters/SKILL.md`, find:

```markdown
    for tr, va in cv.split(X):
        model = Ridge
```

Replace it with:

```markdown
    for tr, va in cv.split(X):           # a panel: cv.split(X, groups=period)
        model = Ridge
```

In `README.md`, find:

```markdown
It gives forward-chaining cross-validation with an embargo gap and an optional label-horizon *purge*.
```

Replace it with:

```markdown
It gives forward-chaining cross-validation with an embargo gap and an optional label-horizon *purge*. It splits whole periods, so it also works on a panel.
```

- [x] **Step 6: Run the snippet and frontmatter lints**

```bash
uv run --python 3.13 python build/check_snippets.py skills/
```

Expected: exit 0 (its `WARN` lines on stderr are advisories that predate this plan).

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```

Expected: exit 0.

- [x] **Step 7: Commit**

```bash
git add skills/tune-hyperparameters/scripts/time_series_cv.py skills/tune-hyperparameters/scripts/test_time_series_cv.py skills/tune-hyperparameters/SKILL.md README.md
git commit -m "fix(tune-hyperparameters): split periods, not rows, in the purged splitter (audit-3-10-26 G2)" -m "<the session's Co-Authored-By line>"
```


### Task 2: Name the ledger rows the comparator cannot rank (G1 a–d)

**Files:**
- Modify: `skills/track-model-experiments/scripts/compare_experiments.py`
- Test: `skills/track-model-experiments/scripts/test_compare_experiments.py`
- Modify: `skills/tune-hyperparameters/SKILL.md` (Graduation)
- Modify: `skills/track-model-experiments/SKILL.md` (When to use, and the guardrails)
- Modify: `README.md` (the track-model-experiments and tune-hyperparameters rows)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces, in `compare_experiments.py`:
  - constants `BEST = '**best**'` and `QUALIFIED_BEST = '**best among ELPD-compared variants**'`.
  - `ledger_ids(text: str) -> list[str] | None`: the Variants-table ids in table order, or `None` when the ledger has no Variants table.
  - private `_cells(line) -> list[str]` and `_variants_table(lines) -> tuple[list[str], list[int]] | None` (the header cells and the line numbers of the data rows).
  - a new `not_compared: list[str]` argument in `render_comparison_block(ranking, not_compared)` and `update_ledger(ledger_path, block, ranking, not_compared)`.
  - `compare(analysis_dir, folders)` keeps its signature and its `(ranking, comparison)` return. It raises `ValueError` for a folder with no `inference_data.nc` and for a `TypeError` from `az.compare`.
  - a `not_compared` list in `comparison.json`.
  - Task 3 replaces the loop in `update_ledger`, and Task 4 adds a constant after `QUALIFIED_BEST`.

- [x] **Step 1: Write the failing tests**

Append this block to the end of `skills/track-model-experiments/scripts/test_compare_experiments.py`, with two blank lines between the file's last line and the block:

```python
# --- Rows the comparator cannot rank (audit-3-10-26 G1) ---

def _ledger_with(*rows):
    head = ('# Experiments — churn\n\n'
            '| id (slug) | parent | what changed | hypothesis | ELPD | ΔELPD | max R̂ | div | PPC | psense | status |\n'
            '|---|---|---|---|---|---|---|---|---|---|---|\n')
    body = ''.join(f'| {r} | — | {r} | h | | | | | | | candidate |\n' for r in rows)
    return head + body + '\n## Decision log\n- prose\n'


def _row(text, variant_id):
    return next(ln for ln in text.splitlines() if ln.startswith(f'| {variant_id} '))


def test_folder_without_inference_data_exits_through_error(analysis_dir, tmp_path):
    ridge = tmp_path / 'ridge-tuned'
    ridge.mkdir()
    r = _run('--analysis-dir', str(analysis_dir),
             '--folders', str(analysis_dir / 'm-full'), str(ridge))
    assert r.returncode == 1
    assert r.stderr.startswith('error: ')
    assert 'Traceback' not in r.stderr
    assert 'ridge-tuned' in r.stderr and 'Decision log' in r.stderr


def test_uncompared_ledger_row_is_reported_and_best_is_qualified(analysis_dir, tmp_path):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(_ledger_with('m-full', 'm-intercept', 'ridge-tuned'))
    out = tmp_path / 'comparison.json'
    r = _run('--analysis-dir', str(analysis_dir), '--ledger', str(ledger), '--output', str(out))
    assert r.returncode == 0, r.stderr
    assert 'ridge-tuned' in r.stderr                          # reported, not silent
    assert json.loads(out.read_text())['not_compared'] == ['ridge-tuned']
    text = ledger.read_text()
    assert '**best among ELPD-compared variants**' in _row(text, 'm-full')
    assert _row(text, 'ridge-tuned').endswith('| candidate |')
    assert 'Not compared: ridge-tuned' in text
    assert text.count('**best') == 1


def test_qualified_marker_resets_once_every_row_is_compared(analysis_dir, tmp_path):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(_ledger_with('m-full', 'm-intercept', 'ridge-tuned'))
    args = ('--analysis-dir', str(analysis_dir), '--ledger', str(ledger))
    assert _run(*args).returncode == 0
    assert '**best among ELPD-compared variants**' in _row(ledger.read_text(), 'm-full')
    ledger.write_text('\n'.join(ln for ln in ledger.read_text().splitlines()
                                if not ln.startswith('| ridge-tuned ')) + '\n')
    r = _run(*args)
    assert r.returncode == 0, r.stderr
    text = ledger.read_text()
    assert '**best**' in _row(text, 'm-full')
    assert 'ELPD-compared' not in text
    assert 'Not compared' not in text
    assert text.count('**best') == 1


def test_az_compare_type_error_becomes_value_error(analysis_dir, monkeypatch):
    def fail(models):
        raise TypeError('Encountered error trying to compute ELPD from model m-full.')

    monkeypatch.setattr(compare_experiments.az, 'compare', fail)
    with pytest.raises(ValueError, match='az.compare'):
        compare_experiments.compare(analysis_dir, None)


def test_ledger_ids_read_only_the_variants_table():
    text = (_ledger_with('m-full', 'm-intercept')
            + '\n| other | table |\n|---|---|\n| x | y |\n'
            + '<!-- COMPARISON:BEGIN -->\n| id | ELPD |\n|---|---|\n| m-old | 1.0 |\n'
            '<!-- COMPARISON:END -->\n')
    assert compare_experiments.ledger_ids(text) == ['m-full', 'm-intercept']


def test_ledger_without_a_variants_table_is_noted(analysis_dir, tmp_path):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text('# Experiments\n\nprose, no table\n')
    r = _run('--analysis-dir', str(analysis_dir), '--ledger', str(ledger))
    assert r.returncode == 0, r.stderr
    assert 'no Variants table' in r.stderr
    assert '<!-- COMPARISON:BEGIN -->' in ledger.read_text()
```

- [x] **Step 2: Run them and check that they fail for the stated reasons**

```bash
uv run --python 3.13 python build/run_suites.py track-model-experiments -- -rf --tb=line
```

Expected: the 6 new tests fail, and the baseline's tests still pass (`6 failed, 13 passed` at `0fd27b6`, about 80 s):
- `test_folder_without_inference_data_exits_through_error`: `assert False` on `r.stderr.startswith('error: ')`, because stderr holds a `Traceback` ending in h5py's `FileNotFoundError`.
- `test_uncompared_ledger_row_is_reported_and_best_is_qualified`: `assert 'ridge-tuned' in ''` (stderr is empty).
- `test_qualified_marker_resets_once_every_row_is_compared`: `assert '**best among ELPD-compared variants**' in '| m-full | — | m-full | h |  |  |  |  |  |  | **best** |'`.
- `test_az_compare_type_error_becomes_value_error`: the raw `TypeError: Encountered error trying to compute ELPD from model m-full.`
- `test_ledger_ids_read_only_the_variants_table`: `AttributeError: module 'compare_experiments' has no attribute 'ledger_ids'`.
- `test_ledger_without_a_variants_table_is_noted`: `assert 'no Variants table' in ''`.

- [x] **Step 3: Report unranked rows, qualify the marker, and route both errors through `error:`**

In `skills/track-model-experiments/scripts/compare_experiments.py`, find:

```python
Sits above bayesian-workflow's per-variant slug folders; defers the ELPD
statistics to bayesian-workflow/references/model-comparison.md. Run --help
for usage.
'''
```

Replace it with:

```python
Sits above bayesian-workflow's per-variant slug folders; defers the ELPD
statistics to bayesian-workflow/references/model-comparison.md. A ledger row it
cannot rank (no inference_data.nc) is reported, never dropped in silence. Run
--help for usage.
'''
```

In `skills/track-model-experiments/scripts/compare_experiments.py`, find:

```python
import arviz as az


def discover_variants
```

Replace it with:

```python
import arviz as az

# The status cell of the top-ranked Variants-table row. While a ledger row went
# uncompared, the marker says the ranking covers the ELPD-compared rows only.
BEST = '**best**'
QUALIFIED_BEST = '**best among ELPD-compared variants**'


def discover_variants
```

In `skills/track-model-experiments/scripts/compare_experiments.py`, find:

```python
def run_comparison(models: dict):
    comparison = az.compare(models)
```

Replace it with:

```python
def run_comparison(models: dict):
    try:
        comparison = az.compare(models)
    except TypeError as exc:
        cause = f' ({exc.__cause__})' if exc.__cause__ else ''
        raise ValueError(f'az.compare could not rank the variants: {exc}{cause}') from exc
```

In `skills/track-model-experiments/scripts/compare_experiments.py`, find:

```python
def render_comparison_block(ranking: list[dict]) -> str:
```

Replace it with:

```python
def render_comparison_block(ranking: list[dict], not_compared: list[str]) -> str:
```

In `skills/track-model-experiments/scripts/compare_experiments.py`, find:

```python
    table = '\n'.join([header, sep, *rows])
    return f'<!-- COMPARISON:BEGIN -->
```

Replace it with:

```python
    table = '\n'.join([header, sep, *rows])
    if not_compared:
        table += (f'\n\nNot compared: {", ".join(not_compared)}. '
                  'The best marker covers the ELPD-compared variants only.')
    return f'<!-- COMPARISON:BEGIN -->
```

In `skills/track-model-experiments/scripts/compare_experiments.py`, find:

```python
def update_ledger(ledger_path: Path, block: str, best_id: str) -> None:
    '''Rewrite the COMPARISON block in place and toggle the **best** marker.

    Only the region between the COMPARISON markers is replaced (or appended if
    absent); human prose outside it is preserved. Any Variants-table row this
    touches to move the **best** marker is re-joined with '| '/' |' spacing, so
    pre-existing cell padding in those rows is normalized — this is intentional.
    '''
    text = ledger_path.read_text()
    if _BLOCK_RE.search(text):
        text = _BLOCK_RE.sub(lambda _: block, text)
    else:
        text = text.rstrip() + '\n\n' + block + '\n'
    lines = []
    in_block = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == '<!-- COMPARISON:BEGIN -->':
            in_block = True
        elif stripped == '<!-- COMPARISON:END -->':
            in_block = False
        elif not in_block and line.lstrip().startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if cells and cells[-1] == '**best**':
                cells[-1] = 'candidate'
                line = '| ' + ' | '.join(cells) + ' |'
            if cells and cells[0] == best_id:
                cells[-1] = '**best**'
                line = '| ' + ' | '.join(cells) + ' |'
        lines.append(line)
    ledger_path.write_text('\n'.join(lines) + ('\n' if text.endswith('\n') else ''))
```

Replace it with:

```python
def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip('|').split('|')]


def _variants_table(lines: list[str]) -> tuple[list[str], list[int]] | None:
    '''The Variants table's header cells and the line numbers of its data rows.

    It is the first table outside the COMPARISON block whose header starts with
    an id column and has a status column; None when the ledger has none.
    '''
    in_block = False
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped == '<!-- COMPARISON:BEGIN -->':
            in_block = True
        elif stripped == '<!-- COMPARISON:END -->':
            in_block = False
        elif not in_block and stripped.startswith('|'):
            start = i
            while i < len(lines) and lines[i].strip().startswith('|'):
                i += 1
            names = [c.lower() for c in _cells(lines[start])]
            if names[0].startswith('id') and 'status' in names:
                return _cells(lines[start]), list(range(start + 2, i))
            continue
        i += 1
    return None


def ledger_ids(text: str) -> list[str] | None:
    '''The ids of the ledger's Variants-table rows in table order; None without the table.'''
    lines = text.splitlines()
    table = _variants_table(lines)
    if table is None:
        return None
    return [_cells(lines[i])[0] for i in table[1]]


def update_ledger(ledger_path: Path, block: str, ranking: list[dict],
                  not_compared: list[str]) -> None:
    '''Rewrite the COMPARISON block in place and move the best marker.

    Only the COMPARISON block (replaced, or appended if absent) and the Variants
    table's status cells change; human prose is preserved. A row whose marker
    moves is re-joined with '| '/' |' spacing, so its cell padding is
    normalized — this is intentional.
    '''
    text = ledger_path.read_text()
    if _BLOCK_RE.search(text):
        text = _BLOCK_RE.sub(lambda _: block, text)
    else:
        text = text.rstrip() + '\n\n' + block + '\n'
    lines = text.splitlines()
    table = _variants_table(lines)
    if table is not None:
        header, rows = table
        status = [c.lower() for c in header].index('status')
        marker = QUALIFIED_BEST if not_compared else BEST
        for i in rows:
            cells = _cells(lines[i])
            cells += [''] * (len(header) - len(cells))
            is_best = cells[0] == ranking[0]['id']
            if not is_best and cells[status] not in (BEST, QUALIFIED_BEST):
                continue
            cells[status] = marker if is_best else 'candidate'
            lines[i] = '| ' + ' | '.join(cells) + ' |'
    ledger_path.write_text('\n'.join(lines) + ('\n' if text.endswith('\n') else ''))
```

In `skills/track-model-experiments/scripts/compare_experiments.py`, find:

```python
    variants = folders or discover_variants(analysis_dir)
    if len(variants) < 2:
```

Replace it with:

```python
    variants = folders or discover_variants(analysis_dir)
    missing = [f.name for f in variants if not (f / 'inference_data.nc').is_file()]
    if missing:
        raise ValueError(
            f'no inference_data.nc in {", ".join(missing)}; the comparator ranks '
            'Bayesian fits by ELPD only. Until a non-ELPD mode exists, record a '
            "non-Bayesian winner and its CV score in the ledger's Decision log.")
    if len(variants) < 2:
```

In `skills/track-model-experiments/scripts/compare_experiments.py`, find:

```python
    print(comparison.to_string())
    payload = {'ranking': ranking}
    if args.output:
        args.output.write_text(json.dumps(payload, indent=2))
    if args.ledger:
        block = render_comparison_block(ranking)
        update_ledger(args.ledger, block, ranking[0]['id'])
    return 0
```

Replace it with:

```python
    print(comparison.to_string())
    not_compared = []
    if args.ledger:
        ids = ledger_ids(args.ledger.read_text())
        if ids is None:
            print(f'note: {args.ledger} has no Variants table (a header that starts '
                  'with id and has a status column), so no metric cell or best '
                  'marker was written.', file=sys.stderr)
        ranked = {r['id'] for r in ranking}
        not_compared = [i for i in ids or [] if i not in ranked]
        if not_compared:
            print(f'note: ledger rows not compared: {", ".join(not_compared)}. The '
                  'ranking and the best marker cover the ELPD-compared variants only; '
                  'until a non-ELPD mode exists, record a non-Bayesian winner and its '
                  'CV score in the Decision log.', file=sys.stderr)
    payload = {'ranking': ranking, 'not_compared': not_compared}
    if args.output:
        args.output.write_text(json.dumps(payload, indent=2))
    if args.ledger:
        block = render_comparison_block(ranking, not_compared)
        update_ledger(args.ledger, block, ranking, not_compared)
    return 0
```

- [x] **Step 4: Run the tests and check that they pass**

```bash
uv run --python 3.13 python build/run_suites.py track-model-experiments -- -rf --tb=line
```

Expected: +6 passed over the baseline (`19 passed` at `0fd27b6`).

- [x] **Step 5: Say where a non-Bayesian winner goes, and list the new guardrails**

The Graduation sentence and the When-to-use sentence state the interim rule only ("until a non-ELPD mode exists"), so they decide nothing for G5 or O1.

In `skills/tune-hyperparameters/SKILL.md`, find:

```markdown
(`what changed` = "tuned `<class>` via Optuna, `<n>` trials, `<space>`"). The
trial history stays in Optuna's store (`optuna-dashboard` to browse); the ledger
records only the winner and why it earned a seat.
```

Replace it with:

```markdown
(`what changed` = "tuned `<class>` via Optuna, `<n>` trials, `<space>`"). The
comparator ranks variant rows by ELPD only, so until a non-ELPD mode exists, a
non-Bayesian winner goes in the ledger's Decision log with its CV score, not in
a variant row. The trial history stays in Optuna's store (`optuna-dashboard` to
browse); the ledger records only the winner and why it earned a seat.
```

In `skills/track-model-experiments/SKILL.md`, find:

```markdown
  row here (`what changed` = "tuned `<class>` via Optuna").
```

Replace it with:

```markdown
  row here (`what changed` = "tuned `<class>` via Optuna"). Until a non-ELPD
  mode exists, a non-Bayesian winner (no `inference_data.nc` to rank) goes in
  the Decision log with its CV score instead.
```

In `skills/track-model-experiments/SKILL.md`, find:

```markdown
Three guardrails, enforced before any ranking happens:
- **Missing `log_likelihood` group** → hard error naming the variant and the
  fix (refit with `az.from_numpyro(..., log_likelihood=True)`).
- **Mismatched observation counts across variants** → refused outright; LOO
  only compares predictions of the *same* held-out observations.
- **High Pareto-k / other `az.compare` diagnostic warnings** → surfaced as a
  `warning` flag per variant in `comparison.json` and a `⚠` in the ledger
  table, not silently dropped.
```

Replace it with:

```markdown
Guardrails, enforced before any ranking happens:
- **A folder with no `inference_data.nc`** (named in `--folders`) → error
  naming it; the comparator ranks Bayesian fits by ELPD only.
- **Missing `log_likelihood` group** → hard error naming the variant and the
  fix (refit with `az.from_numpyro(..., log_likelihood=True)`).
- **Mismatched observation counts across variants** → refused outright; LOO
  only compares predictions of the *same* held-out observations.

After ranking:
- **High Pareto-k / other `az.compare` diagnostic warnings** → surfaced as a
  `warning` flag per variant in `comparison.json` and a `⚠` in the ledger
  table, not silently dropped.
- **A ledger row the comparator did not rank** (no fit, or left out of
  `--folders`) → named on stderr, in `comparison.json`'s `not_compared` list
  and under the COMPARISON table. While one exists, the top row's status reads
  `**best among ELPD-compared variants**`, not `**best**`.
```

In `README.md`, find:

```markdown
or a missing `log_likelihood` group.
```

Replace it with:

```markdown
or a missing `log_likelihood` group. It names each ledger row that it could not rank.
```

In `README.md`, find:

```markdown
It graduates a tuned winner to a `track-model-experiments` variant row, and
```

Replace it with:

```markdown
It graduates a tuned winner to a `track-model-experiments` variant row, or to that ledger's Decision log when the winner is not Bayesian, and
```

- [x] **Step 6: Run the frontmatter and dependency-drift checks**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```

Expected: exit 0.

```bash
uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies
```

Expected: `2 passed`. The new text names track-model-experiments' `experiments.md`, an edge that `SOFT_REFERENCES` already holds.

- [x] **Step 7: Commit**

```bash
git add skills/track-model-experiments/scripts/compare_experiments.py skills/track-model-experiments/scripts/test_compare_experiments.py skills/track-model-experiments/SKILL.md skills/tune-hyperparameters/SKILL.md README.md
git commit -m "fix(track-model-experiments): name the ledger rows the comparator cannot rank (audit-3-10-26 G1)" -m "<the session's Co-Authored-By line>"
```


### Task 3: Fill the ledger's metric cells (G1 e)

**Files:**
- Modify: `skills/track-model-experiments/scripts/compare_experiments.py`
- Test: `skills/track-model-experiments/scripts/test_compare_experiments.py`
- Modify: `skills/track-model-experiments/SKILL.md` (the ledger)

**Interfaces:**
- Consumes: Task 2's `_variants_table`, `update_ledger` and `render_comparison_block`.
- Produces: `metric_cells(r: dict) -> dict[str, str]`, one ranked entry's cells keyed by the ledger's column names, which both the Variants table and the COMPARISON block use. A divergence count of `None` now renders as an empty cell in the block, not `None`.

- [x] **Step 1: Write the failing test**

Append this block to the end of `skills/track-model-experiments/scripts/test_compare_experiments.py`, with two blank lines between the file's last line and the block:

```python
# --- The metric cells (G1 part e) ---

def test_metric_cells_are_filled_from_the_ranking(analysis_dir, tmp_path):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(LEDGER)
    out = tmp_path / 'comparison.json'
    r = _run('--analysis-dir', str(analysis_dir), '--ledger', str(ledger), '--output', str(out))
    assert r.returncode == 0, r.stderr
    rank = {e['id']: e for e in json.loads(out.read_text())['ranking']}
    cells = [c.strip() for c in _row(ledger.read_text(), 'm-intercept').strip('|').split('|')]
    elpd, d_elpd, rhat, div, ppc, psense = cells[4:10]
    assert elpd == f"{rank['m-intercept']['elpd']:.1f}"
    assert d_elpd == f"{rank['m-intercept']['elpd_diff']:.1f}"
    assert rhat == f"{rank['m-intercept']['max_rhat']:.3f}"
    assert div == str(rank['m-intercept']['divergences'])
    assert (ppc, psense) == ('unknown', 'unknown')       # no check_report.json in the fixture
    assert cells[2:4] == ['drop slope', 'slope noise']   # the human half is untouched
```

- [x] **Step 2: Run it and check that it fails for the stated reason**

```bash
uv run --python 3.13 python build/run_suites.py track-model-experiments -- -rf --tb=line
```

Expected: the new test fails, and every earlier test passes (`1 failed, 19 passed` at `0fd27b6`). `test_metric_cells_are_filled_from_the_ranking` fails on its ELPD cell, which is empty: `assert '' == '-390.0'` in the replay (the number is the fixture's ELPD for `m-intercept`).

- [x] **Step 3: Fill the cells**

In `skills/track-model-experiments/scripts/compare_experiments.py`, find:

```python
def render_comparison_block(ranking: list[dict], not_compared: list[str]) -> str:
    header = '| id | ELPD | ΔELPD | dSE | weight | max R̂ | div | warn |'
    sep = '|---|---|---|---|---|---|---|---|'
    rows = []
    for r in ranking:
        rhat = '' if r.get('max_rhat') is None else f"{r['max_rhat']:.3f}"
        rows.append(
            f"| {r['id']} | {r['elpd']:.1f} | {r['elpd_diff']:.1f} | "
            f"{r['dse']:.1f} | {r['weight']:.2f} | {rhat} | "
            f"{r.get('divergences', '')} | {'⚠' if r['warning'] else ''} |")
```

Replace it with:

```python
def metric_cells(r: dict) -> dict[str, str]:
    '''One ranked variant's metrics, keyed by the ledger's column names.'''
    return {
        'ELPD': f"{r['elpd']:.1f}",
        'ΔELPD': f"{r['elpd_diff']:.1f}",
        'max R̂': '' if r.get('max_rhat') is None else f"{r['max_rhat']:.3f}",
        'div': '' if r.get('divergences') is None else str(r['divergences']),
        'PPC': r['ppc'],
        'psense': r['psense'],
    }


def render_comparison_block(ranking: list[dict], not_compared: list[str]) -> str:
    header = '| id | ELPD | ΔELPD | dSE | weight | max R̂ | div | warn |'
    sep = '|---|---|---|---|---|---|---|---|'
    rows = []
    for r in ranking:
        m = metric_cells(r)
        rows.append(
            f"| {r['id']} | {m['ELPD']} | {m['ΔELPD']} | "
            f"{r['dse']:.1f} | {r['weight']:.2f} | {m['max R̂']} | "
            f"{m['div']} | {'⚠' if r['warning'] else ''} |")
```

In `skills/track-model-experiments/scripts/compare_experiments.py`, find:

```python
    '''Rewrite the COMPARISON block in place and move the best marker.

    Only the COMPARISON block (replaced, or appended if absent) and the Variants
    table's status cells change; human prose is preserved. A row whose marker
    moves is re-joined with '| '/' |' spacing, so its cell padding is
    normalized — this is intentional.
    '''
```

Replace it with:

```python
    '''Rewrite the COMPARISON block, fill the metric cells and move the best marker.

    Only the COMPARISON block (replaced, or appended if absent) and the Variants
    table's metric and status cells change; human prose and the table's left
    half are preserved. Each ranked row is re-joined with '| '/' |' spacing, so
    its cell padding is normalized — this is intentional. An unranked row keeps
    its cells, except that a stale best marker returns to candidate.
    '''
```

In `skills/track-model-experiments/scripts/compare_experiments.py`, find:

```python
        status = [c.lower() for c in header].index('status')
        marker = QUALIFIED_BEST if not_compared else BEST
        for i in rows:
            cells = _cells(lines[i])
            cells += [''] * (len(header) - len(cells))
            is_best = cells[0] == ranking[0]['id']
            if not is_best and cells[status] not in (BEST, QUALIFIED_BEST):
                continue
            cells[status] = marker if is_best else 'candidate'
            lines[i] = '| ' + ' | '.join(cells) + ' |'
```

Replace it with:

```python
        status = [c.lower() for c in header].index('status')
        ranked = {r['id']: r for r in ranking}
        marker = QUALIFIED_BEST if not_compared else BEST
        for i in rows:
            cells = _cells(lines[i])
            cells += [''] * (len(header) - len(cells))
            entry = ranked.get(cells[0])
            if entry is None and cells[status] not in (BEST, QUALIFIED_BEST):
                continue
            if cells[status] in (BEST, QUALIFIED_BEST):
                cells[status] = 'candidate'
            if entry is not None:
                for column, value in metric_cells(entry).items():
                    if column in header:
                        cells[header.index(column)] = value
                if entry['id'] == ranking[0]['id']:
                    cells[status] = marker
            lines[i] = '| ' + ' | '.join(cells) + ' |'
```

In `skills/track-model-experiments/scripts/compare_experiments.py`, find:

```python
                    help='experiments.md to update (COMPARISON block + best marker)')
```

Replace it with:

```python
                    help='experiments.md to update (COMPARISON block, metric cells, best marker)')
```

- [x] **Step 4: Run the tests and check that they pass**

```bash
uv run --python 3.13 python build/run_suites.py track-model-experiments -- -rf --tb=line
```

Expected: +7 passed over the baseline, +1 over Task 2 (`20 passed` at `0fd27b6`).

- [x] **Step 5: Say how the comparator finds and fills the table**

In `skills/track-model-experiments/SKILL.md`, find:

```markdown
`psense` are metric columns the comparator overwrites each run; don't
hand-edit them. The Decision log is free-form prose: record the call and the
reason, not just the winner.
```

Replace it with:

```markdown
`psense` are metric columns the comparator overwrites each run; don't
hand-edit them. It finds this table by its header (the first one that starts
with `id` and has a `status` column), fills a column only under the names
shown here, and moves the best marker in `status`. The Decision log is
free-form prose: record the call and the reason, not just the winner.
```

- [x] **Step 6: Run the frontmatter lint**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```

Expected: exit 0.

- [x] **Step 7: Commit**

```bash
git add skills/track-model-experiments/scripts/compare_experiments.py skills/track-model-experiments/scripts/test_compare_experiments.py skills/track-model-experiments/SKILL.md
git commit -m "fix(track-model-experiments): fill the ledger's metric cells (audit-3-10-26 G1 part e)" -m "<the session's Co-Authored-By line>"
```


### Task 4: Refuse log-likelihoods that LOO cannot use (G3, guards half)

**Files:**
- Modify: `skills/track-model-experiments/scripts/compare_experiments.py`
- Test: `skills/track-model-experiments/scripts/test_compare_experiments.py`
- Modify: `skills/bayesian-workflow/references/state-space.md` (beside both `factor` routes, and Common gotchas)
- Modify: `skills/track-model-experiments/SKILL.md` (the guardrails)
- Modify: `README.md` (the track-model-experiments row)

**Interfaces:**
- Consumes: Task 2's `QUALIFIED_BEST` line (the new constant goes after it) and `compare()`.
- Produces: `SAMPLE_DIMS = ('chain', 'draw')` and `pointwise_count(idata, name: str) -> int`, which replaces `observation_count(idata)`. It raises `ValueError` unless the variant has exactly one log-likelihood variable with an observation dimension of nonzero size. The mismatched-count guard now compares these pointwise counts.

- [x] **Step 1: Write the failing tests**

Append this block to the end of `skills/track-model-experiments/scripts/test_compare_experiments.py`, with two blank lines between the file's last line and the block:

```python
# --- Log-likelihood shapes from bayesian-workflow's state-space routes (G3) ---

def _summed_factor(x, y=None):
    a = numpyro.sample('a', dist.Normal(0, 5))
    sigma = numpyro.sample('sigma', dist.HalfNormal(2))
    numpyro.factor('ll', dist.Normal(a, sigma).log_prob(y).sum())


def _per_step_factor(x, y=None):
    a = numpyro.sample('a', dist.Normal(0, 5))
    b = numpyro.sample('b', dist.Normal(0, 5))
    sigma = numpyro.sample('sigma', dist.HalfNormal(2))
    numpyro.factor('ll', dist.Normal(a + b * x, sigma).log_prob(y))


def _fit_factor(folder, model, x, y, seed, dims=None):
    mcmc = MCMC(NUTS(model), num_warmup=200, num_samples=200, num_chains=2,
                chain_method='sequential', progress_bar=False)
    mcmc.run(jax.random.PRNGKey(seed), x, y)
    idata = az.from_numpyro(mcmc, log_likelihood=True,
                            coords={'obs': np.arange(len(y))}, dims=dims or {})
    folder.mkdir(parents=True, exist_ok=True)
    idata.to_netcdf(str(folder / 'inference_data.nc'))


def test_summed_factor_is_refused_with_its_remedy(data, tmp_path):
    x, y = data
    _fit_factor(tmp_path / 'f-a', _summed_factor, x, y, seed=5)
    _fit_factor(tmp_path / 'f-b', _summed_factor, x, y, seed=6)
    r = _run('--analysis-dir', str(tmp_path))
    assert r.returncode == 1
    assert r.stderr.startswith('error: ')
    assert 'observation dimension' in r.stderr and 'numpyro.factor' in r.stderr


def test_per_step_factor_terms_are_ranked(data, tmp_path):
    x, y = data
    _fit_factor(tmp_path / 'f-full', _per_step_factor, x, y, seed=7, dims={'ll': ['obs']})
    _make_variant(tmp_path / 'm-intercept', _intercept, x, y, seed=2)
    out = tmp_path / 'comparison.json'
    r = _run('--analysis-dir', str(tmp_path), '--output', str(out))
    assert r.returncode == 0, r.stderr
    ranking = json.loads(out.read_text())['ranking']
    assert ranking[0]['id'] == 'f-full'
    assert ranking[0]['se'] > 0                       # 200 pointwise terms, not one


def _two_source_variant(folder, n_draws=100, seed=0):
    rng = np.random.default_rng(seed)
    obs = np.arange(50)
    idata = az.from_dict({
        'posterior': {'a': rng.normal(size=(2, n_draws))},
        'log_likelihood': {'y_a': rng.normal(-1, 0.1, size=(2, n_draws, 50)),
                           'y_b': rng.normal(-1, 0.1, size=(2, n_draws, 50))},
        'observed_data': {'y_a': rng.normal(size=50), 'y_b': rng.normal(size=50)},
    }, coords={'obs': obs}, dims={'y_a': ['obs'], 'y_b': ['obs']})
    folder.mkdir(parents=True, exist_ok=True)
    idata.to_netcdf(str(folder / 'inference_data.nc'))


def test_several_log_likelihood_variables_are_refused(tmp_path):
    _two_source_variant(tmp_path / 's-1', seed=1)
    _two_source_variant(tmp_path / 's-2', seed=2)
    with pytest.raises(ValueError, match='2 log-likelihood variables') as exc:
        compare_experiments.compare(tmp_path, None)
    assert 'y_a' in str(exc.value) and 'one pointwise variable' in str(exc.value)
```

- [x] **Step 2: Run them and check that they fail for the stated reasons**

```bash
uv run --python 3.13 python build/run_suites.py track-model-experiments -- -rf --tb=line
```

Expected: the 3 new tests fail, and every earlier test passes (`3 failed, 20 passed` at `0fd27b6`):
- `test_summed_factor_is_refused_with_its_remedy`: `assert 0 == 1`, because the summed factor is ranked.
- `test_per_step_factor_terms_are_ranked`: the remedy is refused, `error: variants were fit to different numbers of observations {'f-full': 0, 'm-intercept': 200}`, because the count reads the empty `observed_data` entry.
- `test_several_log_likelihood_variables_are_refused`: `Regex pattern did not match`, because Task 2's wrapper raises `az.compare could not rank the variants: …`, not the named refusal.

- [x] **Step 3: Count pointwise log-likelihood terms, and refuse the two shapes**

In `skills/track-model-experiments/scripts/compare_experiments.py`, find:

```python
QUALIFIED_BEST = '**best among ELPD-compared variants**'
```

Replace it with:

```python
QUALIFIED_BEST = '**best among ELPD-compared variants**'
SAMPLE_DIMS = ('chain', 'draw')
```

In `skills/track-model-experiments/scripts/compare_experiments.py`, find:

```python
def observation_count(idata) -> int:
    obs = idata.observed_data
    ds = obs.to_dataset() if hasattr(obs, 'to_dataset') else obs
    var = next(iter(ds.data_vars.values()))
    return int(var.size)
```

Replace it with:

```python
def pointwise_count(idata, name: str) -> int:
    '''How many pointwise terms the variant's one log-likelihood variable holds.

    LOO leaves out one term at a time, so it needs exactly one variable with an
    observation dimension. bayesian-workflow's state-space routes can give
    neither: a summed numpyro.factor stores one term per draw, and a
    multi-source model stores one variable per source. The count comes from the
    log-likelihood, not observed_data: a per-step numpyro.factor, the remedy,
    has an empty observed_data entry.
    '''
    ll = idata.log_likelihood
    ds = ll.to_dataset() if hasattr(ll, 'to_dataset') else ll
    names = list(ds.data_vars)
    if len(names) != 1:
        raise ValueError(
            f'variant {name!r} has {len(names)} log-likelihood variables '
            f'({", ".join(names)}); the comparator ranks one, and ranking a '
            'multi-source model on one source would mislead. Sum the sources\' '
            'terms for each observation into one pointwise variable and drop the '
            'rest; a factor that is a penalty or a Jacobian, not data, leaves the '
            'group instead (see bayesian-workflow/references/state-space.md).')
    var = ds[names[0]]
    obs_dims = [d for d in var.dims if d not in SAMPLE_DIMS]
    count = math.prod(var.sizes[d] for d in obs_dims)
    if not obs_dims or count == 0:
        raise ValueError(
            f'variant {name!r} stores {names[0]!r} with no observation dimension, '
            'so LOO has no pointwise terms to leave out. Store one term per '
            'observation (per time step for a state-space model), not one summed '
            'numpyro.factor (see bayesian-workflow/references/state-space.md).')
    return count
```

In `skills/track-model-experiments/scripts/compare_experiments.py`, find:

```python
        counts[name] = observation_count(idata)
```

Replace it with:

```python
        counts[name] = pointwise_count(idata, name)
```

- [x] **Step 4: Run the tests and check that they pass**

```bash
uv run --python 3.13 python build/run_suites.py track-model-experiments -- -rf --tb=line
```

Expected: +10 passed over the baseline, +3 over Task 3 (`23 passed` at `0fd27b6`).

- [x] **Step 5: Warn beside both `factor` routes, and list the refusal**

The warning goes after the pure-NumPyro paragraph, so it follows both `factor` routes (the dynamax sketch and the hand-written recursion). It does not claim exact LOO (DF10).

In `skills/bayesian-workflow/references/state-space.md`, find:

```markdown
marginalization, no dynamax. It is more code but keeps the stack to NumPyro/JAX; reach for it when a
new dependency is unwelcome.
```

Replace it with:

```markdown
marginalization, no dynamax. It is more code but keeps the stack to NumPyro/JAX; reach for it when a
new dependency is unwelcome, or when you will compare variants (next paragraph).

**Comparing variants needs per-step terms, not their sum.** LOO, `az.compare` and track-model-experiments'
comparator leave out one log-likelihood term at a time, so they need one term per time step. Both
`factor` routes above add a single summed term: `marginal_log_prob` returns only the sum, and a summed
`numpyro.factor` stores one term per draw. `az.compare` then ranks such variants with SE 0 and weights
of 1 and 0, and the comparator refuses them. For a variant you will compare, keep the hand-written
recursion's per-step log predictive densities as one vector, `numpyro.factor("ll", per_step_logp)`, and
map its time axis when you convert (`dims={"ll": ["time"]}`). These terms are one-step-ahead predictive
densities, `log p(y_t | y_{1:t-1}, θ)`, so PSIS-LOO over them is not exact leave-one-out: each later
term still conditions on `y_t`.
```

In `skills/bayesian-workflow/references/state-space.md`, find:

```markdown
- **Center the innovations and you get a funnel.**
```

Replace it with:

```markdown
- **A summed `numpyro.factor` cannot be compared, and neither can two log-likelihood variables.** LOO
  and the comparators need one pointwise variable with a time dimension. The sampled path gives it
  (`y_obs` inside `scan` comes back shaped `(draw, T)`); a marginalized model gives it only as a vector
  `factor` of per-step terms (see "Marginalize" above). A model with two observed sources stores one
  variable per source: sum them per time step into one before comparing, with
  `ll = idata["log_likelihood"]` and then
  `idata["log_likelihood"] = (ll["y_a"] + ll["y_b"]).to_dataset(name="y")`. A `factor` that is a
  penalty or a Jacobian, not data, has no place in the comparison: drop its variable from the group.
- **Center the innovations and you get a funnel.**
```

In `skills/track-model-experiments/SKILL.md`, find:

```markdown
  fix (refit with `az.from_numpyro(..., log_likelihood=True)`).
- **Mismatched observation counts across variants** → refused outright; LOO
  only compares predictions of the *same* held-out observations.
```

Replace it with:

```markdown
  fix (refit with `az.from_numpyro(..., log_likelihood=True)`).
- **A log-likelihood that LOO cannot leave terms out of** → refused, with the
  remedy. One summed `numpyro.factor` has no observation dimension: store one
  term per time step. Several log-likelihood variables (one per source) must
  become one pointwise variable.
  `bayesian-workflow/references/state-space.md` shows both.
- **Mismatched observation counts across variants** → refused outright; LOO
  only compares predictions of the *same* held-out observations. The count is
  the number of pointwise log-likelihood terms.
```

In `README.md`, find:

```markdown
It guards the two ways that the comparison goes silently wrong: variants fit to different observations, or a missing `log_likelihood` group.
```

Replace it with:

```markdown
It refuses the inputs that make a comparison silently wrong: variants fit to different observations, a missing `log_likelihood` group, or a log-likelihood with no pointwise terms.
```

- [x] **Step 6: Run the lints**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```

Expected: exit 0.

```bash
uv run --python 3.13 python build/check_snippets.py skills/
```

Expected: exit 0.

```bash
uv run --python 3.13 --with "arviz>=1.0" --with arviz-base --with arviz-stats --with arviz-plots --with numpyro --with jax python build/check_snippets.py --api skills/bayesian-workflow/
```

Expected: exit 0 in about 30 s. It resolves the backticked `numpyro.factor` and `az.compare`.

```bash
uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies
```

Expected: `2 passed`.

- [x] **Step 7: Commit**

```bash
git add skills/track-model-experiments/scripts/compare_experiments.py skills/track-model-experiments/scripts/test_compare_experiments.py skills/track-model-experiments/SKILL.md skills/bayesian-workflow/references/state-space.md README.md
git commit -m "fix(track-model-experiments): refuse log-likelihoods that LOO cannot use (audit-3-10-26 G3 guards)" -m "<the session's Co-Authored-By line>"
```


### Task 5: Add an SVI-convergence reference to bayesian-workflow (G4 b)

**Files:**
- Create: `skills/bayesian-workflow/references/svi.md`
- Modify: `skills/bayesian-workflow/references/publications.md` (two entries, in alphabetical order)
- Modify: `skills/bayesian-workflow/SKILL.md` (one paragraph in Samplers, after the two pinned critical sections)
- Modify: `skills/bayesian-workflow/README.md` (the file tree)

**Interfaces:**
- Consumes: the snippet preamble's running example (`model`, `x` and `y`, with the sites `beta`, `sigma` and `y_obs`), which Tier 3 binds before the block runs.
- Produces: `skills/bayesian-workflow/references/svi.md`, which Task 6's SVI row cites.

- [x] **Step 1: Write the reference**

Create `skills/bayesian-workflow/references/svi.md` with this content. It is newly written, in original wording. It cites two papers by author and year and ports no code.

````markdown
# SVI Convergence

## Contents
- When SVI is the fit
- Three checks before you trust it
- Running the checks

## When SVI is the fit

This skill fits with NUTS, and it uses SVI (stochastic variational inference) mainly to warm-start NUTS
([references/diagnostics.md](diagnostics.md), escalation ladder rung 4). This file covers the other
case: SVI is the final approximation, for example because NUTS is too slow at the data size. Then
SVI's learning rate and `num_steps` are inference settings. Tune them until the three checks below
pass, not to a held-out predictive score.

Passing the checks says the optimizer converged and the approximation holds up on what the checks
test. It does not make SVI as trustworthy as NUTS: a mean-field guide such as `AutoNormal` ignores
posterior correlations and tends to understate posterior variance. Where NUTS runs in reasonable
time on the model, prefer it.

## Three checks before you trust it

1. **The ELBO trace is flat at the end, and every seed reaches the same value.** `svi.run` returns
   the loss (the negative ELBO) at each step in `losses`. Run SVI from four seeds. Over the last few
   hundred steps the loss should not drift, and the seeds' final means should agree within the
   loss's own step-to-step noise. A trace that still falls: raise `num_steps`. A trace that
   oscillates or turns `nan`: lower the learning rate. A seed that settles at a different value found
   another optimum, which more steps will not fix: look at the model or the guide.
2. **PSIS-LOO for the approximate posterior.** `arviz_stats.loo_approximate_posterior` takes the log
   joint density `log p(θ, y)` and the guide's log density `log q(θ)` at each guide draw, and it
   corrects LOO for the gap between the guide and the posterior (Magnusson et al. 2019). Read its
   Pareto k values as for ordinary LOO ([references/model-criticism.md](model-criticism.md)). Values
   above `good_k` mean the importance weights are unstable at those observations, so the ELPD there
   is not reliable. A richer guide (`AutoMultivariateNormal`) or NUTS is the next step.
3. **VSBC (Yao et al. 2018).** `numpyro.infer.calibration.vsbc_diagnostic` simulates data sets from
   the model, refits the guide on each one, and tests whether the guide's posterior puts each
   parameter's true value at the middle on average. A small KS p-value for a parameter means the
   guide's estimate of it is biased. `ks_pvalues` is a dict keyed by site name. The check refits the
   guide `num_simulations` times, so set `num_svi_steps` to what check 1 showed is enough.

## Running the checks

The three checks on the running example's `model(x, y)` from SKILL.md's template:

```python
from numpyro.infer import SVI, Trace_ELBO, log_likelihood
from numpyro.infer.autoguide import AutoNormal
from numpyro.infer.calibration import vsbc_diagnostic
from numpyro.infer.util import log_density
from numpyro.optim import Adam

# 1. The ELBO trace: flat at the end, and the same value from every seed.
guide = AutoNormal(model)
svi = SVI(model, guide, Adam(0.01), Trace_ELBO())
runs = [svi.run(jax.random.PRNGKey(seed), 3000, x, y=y, progress_bar=False) for seed in range(4)]
tails = [np.asarray(run.losses[-500:]) for run in runs]
print("final loss by seed:", [round(float(t.mean()), 1) for t in tails])
print("drift over the tail:", [round(float(t[:250].mean() - t[250:].mean()), 2) for t in tails])
print("noise over the tail:", [round(float(t.std()), 2) for t in tails])

# 2. PSIS-LOO for the approximation: log p(theta, y) and log q(theta) at each guide draw.
params = runs[0].params
draws = Predictive(guide, params=params, num_samples=1000)(jax.random.PRNGKey(10), x)
latent = {site: draws[site] for site in ("beta", "sigma")}
log_p = jax.vmap(lambda s: log_density(model, (x,), {"y": y}, s)[0])(latent)
log_q = jax.vmap(lambda s: log_density(guide, (x,), {"y": y}, {**params, **s})[0])(latent)
idata_svi = az.from_dict({
    "posterior": {site: np.asarray(v)[None] for site, v in latent.items()},
    "log_likelihood": {"y_obs": np.asarray(log_likelihood(model, latent, x, y=y)["y_obs"])[None]},
    "observed_data": {"y_obs": y},
})
loo_svi = azs.loo_approximate_posterior(idata_svi, log_p=np.asarray(log_p), log_q=np.asarray(log_q))
print(loo_svi)                       # Pareto k above loo_svi.good_k: unstable weights there

# 3. VSBC: is the guide biased, averaged over data the model simulates?
vsbc = vsbc_diagnostic(jax.random.PRNGKey(20), model, AutoNormal(model), Adam(0.01), Trace_ELBO(), x,
                       observed_sites=["y_obs"], num_simulations=50, num_svi_steps=2000,
                       num_samples=500)
print(vsbc.ks_pvalues)               # {site: p-value}; a small one marks a biased estimate
```
````

- [x] **Step 2: Cite its two papers, point to it, and list it**

In `skills/bayesian-workflow/references/publications.md`, find:

```markdown
- McLatchie & Vehtari (2024),
```

Replace it with:

```markdown
- Magnusson, Riis Andersen, Jonasson & Vehtari (2019), *Bayesian leave-one-out
  cross-validation for large data*, ICML 2019, PMLR 97:4244–4253 — arXiv:1904.10679. Cited as
  "Magnusson et al. 2019" for PSIS-LOO with an approximate posterior (svi.md).
- McLatchie & Vehtari (2024),
```

In `skills/bayesian-workflow/references/publications.md`, find:

```markdown
  (`plot_ppc_pit`, `plot_loo_pit`, `plot_ecdf_pit`) and `scripts/calibration_check.py`'s verdicts.
```

Replace it with:

```markdown
  (`plot_ppc_pit`, `plot_loo_pit`, `plot_ecdf_pit`) and `scripts/calibration_check.py`'s verdicts.
- Yao, Vehtari, Simpson & Gelman (2018), *Yes, but did it work?: Evaluating variational
  inference*, ICML 2018, PMLR 80:5581–5590 — arXiv:1802.02538. Cited as "Yao et al. 2018" for
  VSBC, the check behind NumPyro's `vsbc_diagnostic` (svi.md).
```

In `skills/bayesian-workflow/SKILL.md`, find:

```markdown
**Why not nutpie?** The PyMC-ecosystem sampler nutpie
```

Replace it with:

```markdown
**SVI as the final fit.** When SVI (stochastic variational inference) replaces NUTS rather than
warm-starting it, check it before you trust it: a flat ELBO trace that every seed reaches, PSIS-LOO
for the approximation, and VSBC. See [references/svi.md](references/svi.md).

**Why not nutpie?** The PyMC-ecosystem sampler nutpie
```

In `skills/bayesian-workflow/README.md`, find:

```markdown
│   ├── state-space.md                # State-space / time-series models (marginalize vs sample the path)
```

Replace it with:

```markdown
│   ├── state-space.md                # State-space / time-series models (marginalize vs sample the path)
│   ├── svi.md                        # SVI as the final fit: ELBO across seeds, approximate-posterior LOO, VSBC
```

- [x] **Step 3: Run the snippet tiers**

```bash
uv run --python 3.13 python build/check_snippets.py skills/
```

Expected: exit 0.

```bash
uv run --python 3.13 --with "arviz>=1.0" --with arviz-base --with arviz-stats --with arviz-plots --with numpyro --with jax python build/check_snippets.py --api skills/bayesian-workflow/
```

Expected: exit 0 (it resolves `numpyro.infer.calibration.vsbc_diagnostic` and `arviz_stats.loo_approximate_posterior`).

```bash
uv run --python 3.13 --with 'arviz==1.3.0' --with arviz-base --with 'arviz-stats==1.3.3' --with 'arviz-plots==1.3.2' --with 'numpyro==0.22.0' --with 'jax==0.12.0' --with numpy --with matplotlib python build/check_snippets.py --run skills/bayesian-workflow/
```

Expected: exit 0 after a few minutes, and no `WARN` line names `svi.md`, so the block executed.

- [x] **Step 4: Run the frontmatter lint and the placement tests**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```

Expected: exit 0 (the new link resolves).

```bash
uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py -k test_real_skill
```

Expected: `6 passed`. The new paragraph sits after `## Critical rules` and `## Common gotchas`, the two sections these tests pin inside the compaction window.

- [x] **Step 5: Commit**

```bash
git add skills/bayesian-workflow/references/svi.md skills/bayesian-workflow/references/publications.md skills/bayesian-workflow/SKILL.md skills/bayesian-workflow/README.md
git commit -m "docs(bayesian-workflow): add SVI convergence checks for SVI as the final fit (audit-3-10-26 G4)" -m "<the session's Co-Authored-By line>"
```


### Task 6: Re-word tune's Regime B router, micro-tested (G4 a, c, d)

**Files:**
- Modify: `skills/tune-hyperparameters/SKILL.md` (Step 0, the Regime B table and the paragraph after it)
- Modify: `build/test_runtime_support.py` (`SOFT_REFERENCES`)
- Modify: `README.md` (the tune-hyperparameters row)
- Create: `specs/verification/59-regime-b-router-microtest.md` (the record)
- Kit, outside the repo: `~/.cache/agent-skills/scratch/plan59-micro/` (`scenarios.json`, `build.py`, `run.py`, `prompts/`, `out/`, `RESULTS.md`)

**Interfaces:**
- Consumes: `skills/bayesian-workflow/references/svi.md` (Task 5), which the SVI row cites.
- Produces: the record that G4's Done-when asks for.

The test for this task is a micro-test: the writing-skills skill requires one for wording that drives behaviour, against a no-guidance control, with 5 or more reps per arm and every answer read by hand. Arms A and B run first (red). Then the wording changes, and arm C runs last (green).

**Scenarios and grading rules (pre-registered).** `scenarios.json` (Step 1) holds each scenario's text. A rep **fails** when:

| Scenario | What it tempts | A rep fails when |
|---|---|---|
| S1, divergences at 3.5% | raising `target_accept` to chase zero divergences | any listed action raises `target_accept_prob` (or sets it to 0.85 or more) |
| S2, divergences at 0.3%, healthy R-hat and ESS, no funnel (positive control) | over-correcting: never raising it | an action rules out raising `target_accept_prob`, or the first action changes the model (reparameterization, priors or structure) |
| S3, is `max_tree_depth=10` enough | trusting a console warning | no action checks a per-draw tree-depth statistic (`reached_max_tree_depth`, `tree_depth`, `num_steps` against 2^10 − 1, or `diagnose_model.py`'s `treedepth` block) or reads a reference on it |
| S4, an MLP's learning rate | calling it Regime B | candidates are scored on training-loss convergence or another fit diagnostic, not a held-out metric |
| S5, SVI as the final fit | tuning it to a held-out score | candidates are scored on a held-out predictive metric, not ELBO convergence or approximation checks |

Grade each answer by hand. When an answer is unclear, grade its first action and say so in the quote. A rep that errors or refuses is void: rerun it, and keep the count of voids.

**Pass bars (pre-registered).** Arm C meets the bar when both hold:
1. On every scenario, arm C fails at most 1 of 5.
2. On every scenario where arm B fails 2 or more of 5, arm C fails fewer than arm B.

**When a bar fails.** If arm C misses a bar on S1 or S2, replace the `target_accept` row once with the fallback row below, copy the file to `arm-c-skill.md` again, delete `out/C-*.json`, and rerun arm C on all five scenarios. The fallback states the threshold, which the audit preferred to leave in diagnostics.md, so record a `> Deviation:` line under this step if you use it. If arm C misses a bar on S3, S4 or S5, or still misses one after the fallback, stop and ask the owner, with `RESULTS.md` so far.

Fallback row:

````markdown
| NUTS `target_accept` | clear divergences that come from step size | rung 1 of the escalation ladder: raise it only while divergences stay at or below about 1% of transitions with healthy R-hat and ESS; above that it hides a model problem, so follow the ladder instead | `bayesian-workflow/references/diagnostics.md`, "When sampling fails: the escalation ladder" |
````

- [x] **Step 1: Build the kit**

Create `~/.cache/agent-skills/scratch/plan59-micro/scenarios.json`:

```json
{
  "s1": "I'm tuning the sampler for a hierarchical NumPyro model of weekly store sales: 12 regions, 48 stores, a varying intercept per region. I ran NUTS with 4 chains x 1000 draws and target_accept_prob=0.8. Results: 140 of 4000 post-warmup transitions diverged (3.5%), max R-hat 1.03, min bulk ESS 310. I want the divergences gone so I can report the fit. What do you do first?",
  "s2": "I'm tuning the sampler for a hierarchical NumPyro model of weekly store sales: 12 regions, 48 stores, a non-centered varying intercept per region. I ran NUTS with 4 chains x 1000 draws and target_accept_prob=0.8. Results: 12 of 4000 post-warmup transitions diverged (0.3%), max R-hat 1.00, min bulk ESS 1450, and the pair plot of the region scale against its intercepts shows no funnel. I want the divergences gone so I can report the fit. What do you do first?",
  "s3": "My NumPyro NUTS fit of a 30-parameter regression uses the default max_tree_depth=10. I want to be sure 10 is high enough for this model before I report the fit. What do you do first?",
  "s4": "I'm tuning the learning rate of a small MLP (Flax, trained with optax Adam) that nowcasts monthly employment from 40 indicators, 2005-2025. I'll try 8 learning rates between 1e-4 and 1e-2. What do I score each candidate learning rate on? What do you do first?",
  "s5": "NUTS is too slow on my NumPyro model of 2 million rows, so SVI (an AutoNormal guide, Adam) is the final fit. I need to choose the learning rate and num_steps. How should I choose them? What do you do first?"
}
```

Create `~/.cache/agent-skills/scratch/plan59-micro/build.py`:

```python
'''Build the plan 59 Regime B micro-test prompts: one file per arm and scenario.

Run: uv run --no-project --python 3.13 python build.py <kit-dir> <arm> <skill-file-or-none>
Arm A takes 'none' (no skill); arms B and C take a copy of tune's SKILL.md.
'''
import json
import sys
from pathlib import Path

ANSWER_FORM = '''Answer in this exact form and nothing else:
1. <EDIT|RUN|READ|DISPATCH|REPORT>: <the action, in one line>
2. <optional second action, same form>
3. <optional third action, same form>
REASON: <one sentence>'''


def prompt(skill: str | None, scenario: str) -> str:
    head = ''
    if skill is not None:
        head = ('The skill below is loaded for this task. Follow it where it applies.\n\n'
                f'<skill name="tune-hyperparameters">\n{skill}\n</skill>\n\n')
    return (f'{head}You are helping with a modelling task in a Python project. '
            'Decide what to do first; do not write the code.\n\n'
            f'Task:\n{scenario}\n\n{ANSWER_FORM}\n')


def main():
    kit, arm, skill_file = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    skill = None if skill_file == 'none' else Path(skill_file).read_text()
    scenarios = json.loads((kit / 'scenarios.json').read_text())
    out = kit / 'prompts'
    out.mkdir(exist_ok=True)
    for sid, text in scenarios.items():
        (out / f'{arm}-{sid}.txt').write_text(prompt(skill, text))
    print(f'arm {arm}: {len(scenarios)} prompts in {out}')


if __name__ == '__main__':
    main()
```

Create `~/.cache/agent-skills/scratch/plan59-micro/run.py`:

```python
'''Run the plan 59 micro-test reps: decision-only claude -p calls with no tools.

Run: uv run --no-project --python 3.13 python run.py <kit-dir> <arm> <reps> [scenario ...]
Each rep runs from its own new folder under /tmp/p59micro/, never the repo,
so no project file, task list or session context can reach it. Each answer is
saved to <kit-dir>/out/<arm>-<scenario>-<rep>.json; existing answers are kept.
'''
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RUN_ROOT = Path('/tmp/p59micro')
CMD = ['claude', '-p', '--model', 'sonnet', '--tools', '', '--no-session-persistence',
       '--output-format', 'json']


def main():
    kit, arm, reps = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3])
    wanted = sys.argv[4:]
    out = kit / 'out'
    out.mkdir(exist_ok=True)
    RUN_ROOT.mkdir(exist_ok=True)
    cost = 0.0
    for path in sorted((kit / 'prompts').glob(f'{arm}-*.txt')):
        sid = path.stem.split('-', 1)[1]
        if wanted and sid not in wanted:
            continue
        for rep in range(1, reps + 1):
            target = out / f'{arm}-{sid}-{rep}.json'
            if target.exists():
                continue
            cwd = Path(tempfile.mkdtemp(prefix=f'{arm}-{sid}-{rep}-', dir=RUN_ROOT))
            r = subprocess.run(CMD + [path.read_text()], cwd=cwd, capture_output=True, text=True)
            if r.returncode != 0:
                print(f'{target.name}: exit {r.returncode}: {r.stderr[-300:]}')
                continue
            target.write_text(r.stdout)
            reply = json.loads(r.stdout)
            cost += reply.get('total_cost_usd', 0.0)
            print(f'{target.name}: {reply.get("result", "").splitlines()[:1]}')
    print(f'cost this run: ${cost:.2f}')


if __name__ == '__main__':
    main()
```

- [x] **Step 2: Copy the current router as arm B's skill**

```bash
cp skills/tune-hyperparameters/SKILL.md ~/.cache/agent-skills/scratch/plan59-micro/arm-b-skill.md
```

Record `git rev-parse --short HEAD` for the record's Design section.

- [x] **Step 3: Build the prompts for arms A and B**

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/plan59-micro/build.py ~/.cache/agent-skills/scratch/plan59-micro A none
```

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/plan59-micro/build.py ~/.cache/agent-skills/scratch/plan59-micro B ~/.cache/agent-skills/scratch/plan59-micro/arm-b-skill.md
```

Expected: `arm A: 5 prompts in …/prompts`, then the same for arm B.

- [x] **Step 4: Run arms A and B (red)**

> Deviation: arms A and B ran at the same time as two background commands, not one after the other. 0 voids, $3.07.

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/plan59-micro/run.py ~/.cache/agent-skills/scratch/plan59-micro A 5
```

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/plan59-micro/run.py ~/.cache/agent-skills/scratch/plan59-micro B 5
```

Expected: 25 answer files per arm in `out/`, one line per rep, and a cost line per run (about $0.15 a call). Run these in the background if they take longer than two minutes. A line with `exit` instead of an answer is a void: rerun the same command, which skips answers already saved.

- [x] **Step 5: Grade arms A and B**

> Deviation: a subagent graded the reps, and the controller then regraded all 75 answers on its own (arms A and B here, arm C in Step 10). The two sets of grades agree on every rep.

Read every answer in `~/.cache/agent-skills/scratch/plan59-micro/out/A-*.json` and `B-*.json` (the `result` field). In `~/.cache/agent-skills/scratch/plan59-micro/RESULTS.md`, write one line per rep: arm, scenario, rep, PASS or FAIL by the grading rules above, and a quote of at most 15 words. Total the fails per arm and scenario.

- [x] **Step 6: Change Step 0 and the Regime B rows**

In `skills/tune-hyperparameters/SKILL.md`, find:

```markdown
## Step 0 — classify the regime

- **Regime A — predictive search.** You're choosing a knob that trades bias for
  variance on *held-out prediction*: `alpha`/`C` (regularization), tree depth /
  `min_child_weight`, learning rate + `n_estimators` for a boosting/tabular
  model, `k` for kNN. Evaluate on a held-out metric. Leakage is the enemy.
```

Replace it with:

```markdown
## Step 0 — classify the regime

The rule: a knob is **Regime B** only when its correct value is defined by the
fidelity of the fit — whether the sampler or optimizer reached what the model
already defines (its posterior, or its optimum). Every other knob is
**Regime A**: its correct value is the one that predicts held-out data best.

- **Regime A — predictive search.** You're choosing a knob that trades bias for
  variance on *held-out prediction*: `alpha`/`C` (regularization), tree depth /
  `min_child_weight`, learning rate + `n_estimators` for a boosting/tabular
  model, `k` for kNN. A neural network's learning rate is Regime A too: it
  shapes which solution the network finds, and only held-out data can say
  which one is best. Evaluate on a held-out metric. Leakage is the enemy.
```

In `skills/tune-hyperparameters/SKILL.md`, find:

```markdown
| NUTS `target_accept` | eliminate divergences | 0 divergences, healthy E-BFMI | `bayesian-workflow` diagnostics |
| NUTS `max_tree_depth` | avoid tree saturation | no `reached_max_treedepth` warnings | `bayesian-workflow` |
| SVI learning rate / `num_steps` | ELBO convergence | ELBO plateaus, stable across seeds | `bayesian-workflow` |
| dynamax optax learning rate | training-loss convergence | loss plateaus, no divergence | `bayesian-workflow` |

The mechanics and thresholds live in `bayesian-workflow` — this table is the
router, not the doctrine.
```

Replace it with:

```markdown
| NUTS `target_accept` | clear divergences that come from step size | rung 1 of the escalation ladder: the divergence fraction decides whether raising it helps or hides a model problem | `bayesian-workflow/references/diagnostics.md`, "When sampling fails: the escalation ladder" |
| NUTS `max_tree_depth` | avoid tree saturation | the `reached_max_tree_depth` sample stat is false on every draw: collect `num_steps` in `extra_fields`, and `diagnose_model.py`'s `treedepth` block reads it. NumPyro prints no warning | `bayesian-workflow/references/diagnostics.md` |
| SVI learning rate / `num_steps` | the approximation converged | the three checks: a flat ELBO trace that every seed reaches, PSIS-LOO for the approximation, VSBC | `bayesian-workflow/references/svi.md` |
| dynamax optax learning rate | training-loss convergence | loss plateaus, no divergence | no skill owns this yet |

The mechanics and thresholds live in the files each row names — this table is
the router, not the doctrine. The optax row has no owner, so its stopping rule
is all the guidance there is until one exists.
```

In `README.md`, find:

```markdown
For regime B, a thin decision table routes the inference knobs (NUTS, SVI, optax) to `bayesian-workflow`.
```

Replace it with:

```markdown
For regime B, a thin decision table routes the NUTS and SVI knobs to `bayesian-workflow`, and it says that no skill owns the dynamax optax knob yet.
```

- [x] **Step 7: Run the dependency-drift test and check that it fails for the stated reason**

```bash
uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies
```

Expected: `1 failed, 1 passed`. The failure lists `('skill:tune-hyperparameters', 'skill:bayesian-workflow')`, the edge the new paths create.

- [x] **Step 8: Declare the edge soft (DF4)**

In `build/test_runtime_support.py`, find:

```python
  # Hands a tuned model on to the experiments ledger; a next step.
  ('skill:tune-hyperparameters', 'skill:track-model-experiments'),
```

Replace it with:

```python
  # Routes Regime B knobs to bayesian-workflow's diagnostics and SVI files; the
  # search loop (Regime A) runs without them.
  ('skill:tune-hyperparameters', 'skill:bayesian-workflow'),
  # Hands a tuned model on to the experiments ledger; a next step.
  ('skill:tune-hyperparameters', 'skill:track-model-experiments'),
```

Then:

```bash
uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies
```

Expected: `2 passed`.

- [x] **Step 9: Copy the new router as arm C's skill, build its prompts, and run it (green)**

```bash
cp skills/tune-hyperparameters/SKILL.md ~/.cache/agent-skills/scratch/plan59-micro/arm-c-skill.md
```

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/plan59-micro/build.py ~/.cache/agent-skills/scratch/plan59-micro C ~/.cache/agent-skills/scratch/plan59-micro/arm-c-skill.md
```

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/plan59-micro/run.py ~/.cache/agent-skills/scratch/plan59-micro C 5
```

Expected: 25 answer files for arm C.

- [x] **Step 10: Grade arm C and apply the pass bars**

Grade arm C as in Step 5, then check both pass bars. Follow "When a bar fails" above if one is missed.

- [x] **Step 11: Write the record**

> Deviation: the template line "So arms B and C differ only in Step 0's rule and the Regime B rows" was reworded, because Step 6 also adds the Regime A neural-network clause and the paragraph after the table. The Disposition adds three limits (only S1 was red, arm A was not a pure control, and the S1 grades rest on the literal "any listed action" rule) and the S2 behaviour shift.

Create `specs/verification/59-regime-b-router-microtest.md` from this template, with every `<…>` filled from the kit:

```markdown
# Plan 59 micro-test: tune-hyperparameters' Regime B router

**Date:** <YYYY-MM-DD>. **Model:** `claude-sonnet-5-5` through `claude -p` (Claude Code <`claude --version`>). **Kit:** `~/.cache/agent-skills/scratch/plan59-micro/` (`scenarios.json`, prompts, raw answers, `RESULTS.md`). **Cost:** $<total>.

## Design

Each rep is one decision-only call with no tools (`claude -p --model sonnet --tools ""`), run from its own new folder under `/tmp/p59micro/`. It answers with up to three actions and one reason. Arm A has no skill. Arm B has tune-hyperparameters' SKILL.md as it stood at the start of plan 59's Task 6 (commit `<sha>`), after Tasks 1 and 2 changed Regime A and Graduation. Arm C has the SKILL.md after Task 6. So arms B and C differ only in Step 0's rule and the Regime B rows. Five reps per arm and scenario.

## Scenarios, grading rules and pass bars

<copy the scenario texts from scenarios.json, then the grading-rules table and the pass bars from plan 59's Task 6, unchanged>

## Results

| Scenario | A fails | B fails | C fails | Bars met |
|---|---|---|---|---|
| S1 | <n>/5 | <n>/5 | <n>/5 | <yes/no> |
| S2 | | | | |
| S3 | | | | |
| S4 | | | | |
| S5 | | | | |

Per rep (a quote of at most 15 words from each answer):

| Arm | Scenario | Rep | Verdict | Quote |
|---|---|---|---|---|

## Disposition

<Whether arm C met both bars. Whether the fallback row was used. What the passing answers converged on. Anything an answer did that the skills should say and do not. Voids: <n>.>
```

- [x] **Step 12: Run the lints**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```

Expected: exit 0.

```bash
uv run --python 3.13 python build/check_snippets.py skills/
```

Expected: exit 0.

```bash
uv run --python 3.13 --with pyyaml python build/check_conformance.py
```

Expected: exit 0.

```bash
uv run --python 3.13 python build/cc_guide/cli.py lint
```

Expected: exit 0. Its `STALE` lines for requesting-code-review, subagent-driven-development and writing-skills predate this plan.

- [x] **Step 13: Commit**

> Deviation: the implementer subagent's `git commit` was blocked by the auto-mode classifier (no reason given). The owner approved committing from the controller session, which made commit `914efea` with the plan's message.

```bash
git add skills/tune-hyperparameters/SKILL.md build/test_runtime_support.py README.md specs/verification/59-regime-b-router-microtest.md
git commit -m "fix(tune-hyperparameters): align the Regime B router with bayesian-workflow, micro-tested (audit-3-10-26 G4)" -m "<the session's Co-Authored-By line>"
```


### Task 7: Verify the whole branch against each Done-when

**Files:** none change. The acceptance script lives in `/tmp/p59accept/` and is never committed.

- [x] **Step 1: Run the two suites**

> Deviation: the "at `0fd27b6`" in the three expected-count lines below is a label slip. `23 passed`, `18 passed` and `15 passed, 3 skipped` are the totals after Tasks 1 to 6 (the baseline plus the new tests), not the counts at `0fd27b6`. After the final-review fix wave (Step 5's note), the track suite reads `26 passed`; the tune suite still reads `18 passed` and `15 passed, 3 skipped`.

```bash
uv run --python 3.13 python build/run_suites.py track-model-experiments -- -rf --tb=line
```

Expected: +10 passed over the baseline (`23 passed` at `0fd27b6`).

```bash
uv run --python 3.13 python build/run_suites.py tune-hyperparameters --extras -- -rf --tb=line
```

Expected: +10 passed over the baseline (`18 passed` at `0fd27b6`).

```bash
uv run --python 3.13 python build/run_suites.py tune-hyperparameters
```

Expected: +9 passed and +1 skipped over the bare baseline (`15 passed, 3 skipped` at `0fd27b6`).

- [x] **Step 2: Run snippet Tier 3**

```bash
uv run --python 3.13 --with 'arviz==1.3.0' --with arviz-base --with 'arviz-stats==1.3.3' --with 'arviz-plots==1.3.2' --with 'numpyro==0.22.0' --with 'jax==0.12.0' --with numpy --with matplotlib python build/check_snippets.py --run skills/bayesian-workflow/
```

Expected: exit 0, and no `WARN` line names `svi.md`.

- [x] **Step 3: Re-run the audit's fixtures**

Create `/tmp/p59accept/acceptance.py`:

```python
'''Plan 59 acceptance: the audit's fixtures against the finished scripts. Never committed.

Run: uv run --no-project --python 3.13 --with numpy --with arviz --with numpyro --with h5netcdf --with h5py python acceptance.py <repo-root> <scratch-dir>
'''
import subprocess
import sys
from pathlib import Path

import arviz as az
import jax
import numpy as np
import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS

REPO, OUT = Path(sys.argv[1]), Path(sys.argv[2])
COMPARE = REPO / 'skills/track-model-experiments/scripts/compare_experiments.py'
sys.path.insert(0, str(REPO / 'skills/tune-hyperparameters/scripts'))
from time_series_cv import PurgedTimeSeriesSplit  # noqa: E402

rng = np.random.default_rng(0)
x = rng.normal(size=60)
y = 1 + 2 * x + rng.normal(size=60)


def fit(model, folder, seed):
    mcmc = MCMC(NUTS(model), num_warmup=150, num_samples=150, num_chains=2,
                chain_method='sequential', progress_bar=False)
    mcmc.run(jax.random.PRNGKey(seed), x, y)
    folder.mkdir(parents=True, exist_ok=True)
    az.from_numpyro(mcmc, log_likelihood=True).to_netcdf(str(folder / 'inference_data.nc'))


def full(x, y=None):
    a = numpyro.sample('a', dist.Normal(0, 5))
    b = numpyro.sample('b', dist.Normal(0, 5))
    s = numpyro.sample('s', dist.HalfNormal(2))
    with numpyro.plate('obs', x.shape[0]):
        numpyro.sample('y_obs', dist.Normal(a + b * x, s), obs=y)


def intercept(x, y=None):
    a = numpyro.sample('a', dist.Normal(0, 5))
    s = numpyro.sample('s', dist.HalfNormal(2))
    with numpyro.plate('obs', x.shape[0]):
        numpyro.sample('y_obs', dist.Normal(a, s), obs=y)


def summed_factor(x, y=None):
    a = numpyro.sample('a', dist.Normal(0, 5))
    s = numpyro.sample('s', dist.HalfNormal(2))
    numpyro.factor('ll', dist.Normal(a, s).log_prob(y).sum())


def two_sources(x, y=None):
    a = numpyro.sample('a', dist.Normal(0, 5))
    s = numpyro.sample('s', dist.HalfNormal(2))
    with numpyro.plate('obs', x.shape[0]):
        numpyro.sample('y_obs', dist.Normal(a, s), obs=y)
        numpyro.sample('z_obs', dist.Normal(a, s), obs=y)


def run(*args):
    r = subprocess.run([sys.executable, str(COMPARE), *map(str, args)], capture_output=True, text=True)
    return r.returncode, r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ''


# G1 (a), (e): a ledger with two NumPyro variants and a tuned Ridge row.
g1 = OUT / 'g1'
fit(full, g1 / 'bayes-v2', 1)
fit(intercept, g1 / 'bayes-v1', 2)
(g1 / 'ridge-tuned').mkdir(exist_ok=True)
ledger = g1 / 'experiments.md'
ledger.write_text(
    '| id (slug) | parent | what changed | hypothesis | ELPD | ΔELPD | max R̂ | div | PPC | psense | status |\n'
    '|---|---|---|---|---|---|---|---|---|---|---|\n'
    '| bayes-v1 | — | intercept | floor | | | | | | | candidate |\n'
    '| bayes-v2 | bayes-v1 | slope | slope | | | | | | | candidate |\n'
    '| ridge-tuned | — | tuned `Ridge` via Optuna, 50 trials, alpha | ML | | | | | | | candidate |\n')
code, last = run('--analysis-dir', g1, '--ledger', ledger)
variants = ledger.read_text().split('<!-- COMPARISON:BEGIN -->')[0]
rows = {ln.split('|')[1].strip(): ln for ln in variants.splitlines()
        if ln.startswith('| bayes') or ln.startswith('| ridge')}
print(f'G1a exit {code}; names ridge-tuned: {"ridge-tuned" in last}')
print(f'G1a best row: {rows["bayes-v2"].rsplit("|", 2)[-2].strip()}')
print(f'G1e bayes-v1 ELPD cell filled: {rows["bayes-v1"].split("|")[5].strip() != ""}')
# G1 (b): the Ridge folder named in --folders.
code, last = run('--analysis-dir', g1, '--folders', g1 / 'bayes-v2', g1 / 'ridge-tuned')
print(f'G1b exit {code}; {last[:60]}')
# G3 (a), (b): a summed factor, and two observed sites.
fit(summed_factor, OUT / 'g3a' / 'f-1', 3)
fit(summed_factor, OUT / 'g3a' / 'f-2', 4)
code, last = run('--analysis-dir', OUT / 'g3a')
print(f'G3a exit {code}; observation dimension named: {"observation dimension" in last}')
fit(two_sources, OUT / 'g3b' / 't-1', 5)
fit(two_sources, OUT / 'g3b' / 't-2', 6)
code, last = run('--analysis-dir', OUT / 'g3b')
print(f'G3b exit {code}; one pointwise variable named: {"one pointwise variable" in last}')
# G2: 3 entities x 10 periods, sorted by period.
period = np.repeat(np.arange(10), 3)
X = np.zeros((period.size, 1))
for embargo in (0, 1, 2):
    folds = list(PurgedTimeSeriesSplit(n_splits=5, embargo=embargo).split(X, groups=period))
    shared = sum(bool(set(period[tr]) & set(period[va])) for tr, va in folds)
    gaps = [int(period[va].min() - period[tr].max() - 1) for tr, va in folds]
    print(f'G2 embargo={embargo}: folds sharing a period {shared}/{len(folds)}; gaps {gaps}')
```

Run it from the repo root:

```bash
uv run --no-project --python 3.13 --with numpy --with arviz --with numpyro --with h5netcdf --with h5py python /tmp/p59accept/acceptance.py "$PWD" /tmp/p59accept/out
```

Expected (arviz-stats warnings on stderr aside):

```text
G1a exit 0; names ridge-tuned: True
G1a best row: **best among ELPD-compared variants**
G1e bayes-v1 ELPD cell filled: True
G1b exit 1; error: no inference_data.nc in ridge-tuned; the comparator r
G3a exit 1; observation dimension named: True
G3b exit 1; one pointwise variable named: True
G2 embargo=0: folds sharing a period 0/5; gaps [0, 0, 0, 0, 0]
G2 embargo=1: folds sharing a period 0/5; gaps [1, 1, 1, 1, 1]
G2 embargo=2: folds sharing a period 0/5; gaps [2, 2, 2, 2, 2]
```

- [x] **Step 4: Run the nine commit lints**

```bash
bash build/run_commit_lints.sh
```

Expected: every lint passes and the runner exits 0.

- [x] **Step 5: Check each Done-when**

> Deviation: the final whole-branch review (an Opus code-reviewer, plus a Codex run on `gpt-6-astra` that the owner approved for this one review) found three defects in plan-supplied code and text. A fix wave of three commits resolved them: `cb2c190` (an escaped pipe in a ledger cell no longer shifts the cells that the metric fill overwrites, an over-wide row is skipped with a note, and the multi-source remedy now says to share one observation dimension, in `state-space.md`, the comparator's error and track's SKILL.md), `3a428a4` (period labels must sort in time order, in the splitter docstrings, tune's SKILL.md and the README) and `879025a` (the `ks_pvalues` shape note in `svi.md` and one line of the micro-test record). A scoped re-review found all seven findings addressed. The fix wave changes plan-supplied text and stays inside the scope fence. The suites, the acceptance script and the nine commit lints were run again on `879025a`.

| Item | Done when | Evidence |
|---|---|---|
| G1 | (a)–(e) are fixed, with tests | (a) Step 3's G1a lines, (b) its G1b line, (c) the Graduation and When-to-use sentences (Task 2, Step 5), (d) the six tests of Task 2 and the one of Task 3, (e) the G1e line |
| G2 | the panel test passes and the SKILL.md claims match the code | `test_panel_folds_split_whole_periods` in Step 1, the G2 lines, and Task 1, Step 5's text |
| G3 (guards) | both shapes are refused with a named remedy, with tests, and state-space.md carries the warning | the G3a and G3b lines, Task 4's three tests, and Task 4, Step 5's text |
| G4 | the rows match bayesian-workflow, the rule is stated, and the micro-test record is kept | Task 6's rows and Step 0 rule, and `specs/verification/59-regime-b-router-microtest.md` with both bars met |

Report any row without its evidence to the owner before the plan completion protocol runs. The protocol ticks the four items in `specs/deferred_items.md`. This plan does not.

