# tune-hyperparameters — Design Spec

**Status: IN PROGRESS** — approved 2026-07-05; plan pending.

## Motivation — the gap

The user has no hyperparameter-tuning discipline in place ("nothing yet"). Two
failure modes go uncovered, and they are *different skills wearing one name*:

- **Regime A — predictive HP search** (regularization strength, tree depth,
  learning rate for sklearn/boosting nowcasting models). You search a held-out
  predictive metric. The danger is **leakage**: naive k-fold trains on the
  future, so the CV metric is over-optimistic and the tuned HP nowcasts worse
  than CV promised. The temporal fix — forward-chaining + an embargo gap +
  (for multi-horizon targets) purge — is only partly in sklearn.
- **Regime B — inference HP** (NUTS `target_accept`/`max_tree_depth`, SVI
  learning rate/steps/guide, dynamax optax SGD). These are **not** a
  validation-metric search: `target_accept` goes *up to kill divergences* (a
  diagnostic target), SVI steps tune *to ELBO convergence*. Tuning inference
  settings to a held-out predictive metric is an anti-pattern that overfits the
  approximation.

Existing skills cover neighbors but not this:
- `recommend-probabilistic-model/references/model-selection-regularization.md`
  says *what* to tune and *why* (conceptual, per-family) — not the operational
  loop.
- `develop-testing-strategy` owns **leakage as a permanent test invariant**
  (as-of/vintage correctness, future leakage) — the CI guardrail, not the
  interactive tuning protocol.
- `bayesian-workflow` owns **inference diagnostics** (divergences, R-hat, ELBO).
- `track-model-experiments` compares model *classes*; it does not search within
  one.

Tooling covers even less of the core: **Optuna** performs the search and stores
trials locally, but ships **no** temporal-CV/leakage guard and **no** regime
concept. **MLflow** *tracks* runs but does none of it (see the MLflow analysis
in the session that produced this spec: it provides the tracking layer only,
zero leakage protection, and does not perform the search).

`tune-hyperparameters` is the operational tuning **loop**: classify the regime,
give the correct objective + stopping rule + leakage guard per regime, ship the
one piece nothing else provides (a purged/embargoed temporal-CV splitter), defer
the search to Optuna, and graduate a tuned winner to `track-model-experiments`.

## Goal

A regime-classifying decision skill for HP tuning. It (1) makes you classify the
regime before tuning, (2) documents the correct objective/stopping/leakage guard
for each, (3) ships a leakage-safe temporal-CV splitter (the one tested artifact)
that feeds a manual Optuna objective, and (4) graduates the study winner to
`track-model-experiments`' `experiments.md`. Correctness lives in a splitter you
verify by **running** it on a small seeded synthetic series — no subagent
pressure scenarios — so it ships regardless of subagent availability.

## Non-goals

- **Not a search engine** — Optuna proposes/prunes configurations; this skill
  defers to it (E2).
- **Not the conceptual what-to-tune** — that stays in
  `model-selection-regularization.md`.
- **Not revision/vintage-leakage handling, nor a permanent test suite** — those
  are `develop-testing-strategy`'s turf. This skill guards **temporal** leakage
  only; see E6.
- **Not inference diagnostics** — regime B points to `bayesian-workflow`.
- **Not a universal `tune.py`** — "both flavors" is heterogeneous; a one-shape
  search wrapper would be a thin wrapper around well-documented mechanics
  (writing-skills: don't skill standard practices). The splitter is the reusable
  artifact.

## Design decisions (approved)

- **E1 — regime-first classification.** Every use starts by answering "am I
  searching a predictive metric, or setting an inference/diagnostic knob?"
  (decision-first, like `bayesian-workflow`'s marginalize-vs-sample).
- **E2 — Optuna first-class, local, manual objective.** Optuna is the default
  search engine (`pip install optuna`, pure-Python, local; in-memory or a local
  SQLite/JournalStorage file, which is `.gitignore`'d as a binary blob). The
  documented pattern is the **manual objective** (`trial.suggest_*` + a loop over
  `splitter.split(X)` returning the mean CV score), **not** `OptunaSearchCV`
  (which moved to the separate `optuna-integration` package and has deprecation
  churn — verify against the installed version before using it). Seed the sampler
  (`TPESampler(seed=...)`) for reproducibility.
- **E3 — the splitter adds purge to forward-chaining + embargo.** sklearn's
  `TimeSeriesSplit(gap=embargo)` already gives forward-chaining + the embargo gap
  and is enough for **point-in-time** targets — the SKILL.md says so. The custom
  splitter earns its existence as the **purge**-adding, horizon-aware piece:
  it drops training rows whose label window `[i, i+h]` overlaps the validation
  block (needs the label horizon `h`, which sklearn does not model). Embargo is
  always-on; purge is keyed to `label_horizon` (`h=0` → point-in-time, no purge).
  SKILL.md leads with embargo; both the embargo and purge paths are tested.
- **E4 — regime B is thin.** A decision table (`knob → objective → stopping rule
  → where it lives`) + the anti-pattern warning, then a pointer to
  `bayesian-workflow`. No rebuild of inference diagnostics.
- **E5 — graduation at study-summary granularity.** The study winner writes **one
  row** to `track-model-experiments`' `experiments.md`
  (`what changed` = "tuned `<class>` via Optuna, `<n>` trials, `<space>`"); the
  trials stay in Optuna's local store (a `optuna-dashboard` pointer for
  browsing). Do not mirror 200 trials into the ledger.
- **E6 — temporal leakage only; revision leakage is out of scope and named.**
  The splitter guards *temporal* leakage (train strictly precedes val; embargo;
  purge). It does **not** guard *revision* leakage — for revised BLS series the
  revision (using a later vintage's value than was available at the as-of date)
  is often the bigger leak, and it belongs to `develop-testing-strategy`. The
  SKILL.md states this in one sentence so a green temporal-CV is not misread as
  "leakage-free."

## Architecture

Two components plus wiring.

### Component 1 — SKILL.md (the decision skill)

Sections (house voice — lean, decision-first):
- **Overview** — the tuning loop above single-fit workflow; core principle:
  classify the regime, then tune the right objective with the right leakage guard.
- **Step 0: classify the regime** — a short decision block: predictive search
  (regime A) vs inference/diagnostic knob (regime B). Name the stakes: applying
  regime-A search to regime-B knobs overfits the approximation.
- **Regime A — leakage-safe predictive search:**
  - The leakage trap (naive k-fold on temporal data), with the honest note that
    for point-in-time targets `TimeSeriesSplit(gap=embargo)` suffices and the
    purged splitter is for multi-horizon targets.
  - The manual Optuna objective (E2) with the splitter as `cv`, seeded sampler,
    and a nested-CV / held-out note to avoid validation-set overfitting.
  - When *not* to tune (small data, dominant regularization already set by a
    prior, or the metric variance across folds swamps the HP effect).
  - Graduation (E5) to `track-model-experiments`.
- **Regime B — inference HP (thin):** the decision table (knobs → objective →
  stopping → where it lives) + anti-pattern warning + `bayesian-workflow` pointer.
- **The three-way boundary** (E-below) stated explicitly.
- **The revision-leakage caveat** (E6), one sentence, pointing to
  `develop-testing-strategy`.

Frontmatter `description` is trigger-only ("Use when…"), third-person, ≤ 1024
chars, no workflow summary.

### Component 2 — scripts/time_series_cv.py (the splitter)

A sklearn-compatible cross-validator:

```
PurgedTimeSeriesSplit(n_splits=5, test_size=None, embargo=0, label_horizon=0,
                      min_train_size=None)
  .split(X, y=None, groups=None) -> yields (train_idx, val_idx) ndarrays
  .get_n_splits(X=None, y=None, groups=None) -> int
```

Mechanics (assumes rows are time-ordered; index i is the time position):
- **Forward-chaining, expanding window.** Fold k validates on a block of
  `test_size` rows starting at `s_k`; train is `[0, s_k)` before guards.
- **Embargo (gap `g`).** Remove the `g` rows immediately preceding the val block
  from train: `train_end <= s_k - g`. (Equivalent to sklearn `TimeSeriesSplit`'s
  `gap`.)
- **Purge (horizon `h`).** Drop training rows whose label window overlaps the val
  block: row `i` is purged when `i + h >= s_k`, i.e. `i >= s_k - h`. Combined with
  embargo, `train = [0, min(s_k - g, s_k - h))`. `h=0` disables purge.
- **`min_train_size`** guards folds with too little history (skip or raise).

Pure NumPy indexing; no pandas dependency required (accepts anything with a
length / 2-D array). Single quotes, 4-space indent, Python 3.13.

### Component 3 — scripts/test_time_series_cv.py (run-to-verify)

- **No future leakage** (embargo/point-in-time fixture): for every fold,
  `max(train_idx) < min(val_idx)` and the gap `min(val_idx) - max(train_idx) - 1
  >= embargo`.
- **Purge path** (explicit `label_horizon=h>1` fixture — this branch MUST be
  exercised, per the plan-8 untested-path lesson): assert that training rows with
  `i >= s_k - h` are absent from `train_idx`, and that with `h=0` they are
  present (purge is genuinely conditional).
- **Fold structure**: `get_n_splits` matches the yielded count; expanding train
  sizes are non-decreasing; `min_train_size` respected.
- **Fast Optuna integration**: a manual objective over `Ridge(alpha)` with the
  splitter as `cv`, `TPESampler(seed=0)`, ~15 trials on a seeded synthetic
  series; assert it returns a finite best value and a best `alpha` in range.
  Deterministic; keep it to a trivial estimator so the suite stays fast. Written
  against the **installed** Optuna version (verify the API at implementation
  time; use the manual objective, not `OptunaSearchCV`).

## Wiring into existing skills

- `track-model-experiments/SKILL.md` — one pointer: a tuned winner from
  `tune-hyperparameters` graduates to a variant row here (bare skill name).
- `recommend-probabilistic-model/references/model-selection-regularization.md` —
  one pointer: for the *operational* tuning loop + leakage-safe CV, use
  `tune-hyperparameters` (this file stays the *what/why*).
- `develop-testing-strategy` gets a pointer *from* this skill (E6), not the other
  way around, to keep the leakage-invariant ownership clear.
- All cross-references use **bare skill names**.

## Provenance

`tune-hyperparameters` is a new **original** work by Lowell Mason (MIT). Register
in `NOTICE` (originals list) and `README` (Mine table + "My original skills"
line). **Optuna** and **scikit-learn** are documented `uv --with optuna --with
scikit-learn` dependencies — **not bundled**; the skill cites their APIs and
reproduces no code from them. `build/check_frontmatter.py` and
`build/check_provenance.py` must both pass.

## Global constraints

- Python style: single quotes; 4-space indent; target Python 3.13.
- Stack: scikit-learn + Optuna for regime A; NumPyro/JAX (via `bayesian-workflow`)
  for regime B. No repo-wide `pyproject`; run via `uv run --python 3.13 --with …`.
  Tests use bare imports, run from inside `skills/tune-hyperparameters/scripts/`.
- Optuna's local store (`*.db` / journal) is `.gitignore`'d — the git-tracked
  artifact is the `experiments.md` graduation row.
- Cross-skill references use bare skill names.
- No bundled third-party code; no PDFs; no book prose.

## Testing strategy (how it ships now)

`test_time_series_cv.py` is the RED→GREEN gate, run by execution, not subagents:
verify no-future-leakage, the embargo gap, the **purge path with an h>1 fixture**,
fold structure, and a fast seeded Optuna integration. Run under
`uv run --python 3.13 --with pytest --with numpy --with scikit-learn --with optuna
python -m pytest -q` from the scripts directory. Because correctness is verified
by running the splitter (reference/tooling content, exempt from the
no-guidance-control micro-test requirement), the skill ships even if subagent
dispatch is unavailable. The SKILL.md prose failure mode is "omits regime
classification / uses naive CV," which writing-skills routes to a structural
decision block, not a discipline rationalization table.

## Execution note

Per the prior session, the `opus-4-8` classifier flapped and cost repeated
dispatch retries. At Task 1, check dispatch health; if it is flapping, fall
straight to inline TDD (as the plan-8 hardening batch did) rather than re-fighting
it. The design is deliberately inline-verifiable.

## Out of scope / future

- A worked **regime-B** end-to-end example (SVI lr sweep) — the table + pointer
  is enough for v1; a full example can follow if the thin section proves
  insufficient.
- Auto-graduation tooling (a script that writes the `experiments.md` row) — v1
  documents the row format; automate later only if hand-writing it chafes.
