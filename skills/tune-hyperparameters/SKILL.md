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

# Tune Hyperparameters

## Overview

Hyperparameters are the knobs set *before* the fit — regularization strength,
tree depth, learning rate, a sampler's `target_accept`. Tuning is the loop above
a single fit: propose a value, score it, keep the best. Two things break that
loop: tuning the wrong *kind* of knob against the wrong objective (a held-out
metric for a sampler setting overfits the approximation), and scoring on data the
model shouldn't have seen yet (temporal leakage inflates every candidate equally,
so the winner is an artifact).

Core principle: **classify the regime first, then tune the right objective with
the right leakage guard.**

## Step 0 — classify the regime

- **Regime A — predictive search.** You're choosing a knob that trades bias for
  variance on *held-out prediction*: `alpha`/`C` (regularization), tree depth /
  `min_child_weight`, learning rate + `n_estimators` for a boosting/tabular
  model, `k` for kNN. Evaluate on a held-out metric. Leakage is the enemy.
- **Regime B — inference / optimization diagnostic.** You're setting a knob that
  controls whether the *fit itself* is trustworthy: NUTS `target_accept` /
  `max_tree_depth`, SVI learning rate / steps, a dynamax optax schedule.
  Evaluate on convergence diagnostics, **not** on a held-out predictive metric.

The stakes of getting this wrong: a regime-B knob tuned to a held-out score
overfits the inference approximation to your validation split — you get a
sampler that looks good on one metric and is miscalibrated everywhere else.

## Regime A — leakage-safe predictive search

**The trap.** Naive k-fold shuffles rows, so most folds train on data that
comes *after* the validation block. For anything time-ordered — a nowcast, a
panel, any series — that leaks the future into training and every candidate's
score comes back over-optimistic. You can't compare knobs on a corrupted metric.

**The CV protocol.** Use forward-chaining (expanding-window) splits where train
always precedes validation.

- **Point-in-time target** (label known at the row's own timestamp): sklearn's
  `TimeSeriesSplit(gap=embargo)` already suffices. Add an **embargo** — a gap of
  a few periods between train and val — to absorb autocorrelation bleed at the
  boundary.
- **Multi-period target** (label at row `i` spans `[i, i+h]`, e.g. an
  `h`-period-ahead return or a rolling outcome): the naive split still leaks,
  because a train row near the boundary has a label window reaching *into* the
  validation block. You must **purge** those rows. Reach for this skill's
  `scripts/time_series_cv.py`:

```python
from time_series_cv import PurgedTimeSeriesSplit
# embargo always; purge only when the label spans h>1 periods.
cv = PurgedTimeSeriesSplit(n_splits=5, embargo=2, label_horizon=h)
```

It yields expanding-window `(train_idx, val_idx)` with `train = [0, s_k -
max(embargo, label_horizon))` — embargo and purge carve the same pre-val region,
so the binding one is `max`, not the sum. It duck-types sklearn's splitter API,
so it drops straight into the objective below.

**The search — a manual Optuna objective** (verified against Optuna 4.9.0). Keep
the objective explicit: suggest the knobs, loop over `cv.split(X)`, return the
mean CV score. A seeded `TPESampler` makes the run reproducible.

```python
import numpy as np, optuna
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error

def objective(trial):
    alpha = trial.suggest_float('alpha', 1e-3, 1e3, log=True)
    scores = []
    for tr, va in cv.split(X):
        model = Ridge(alpha=alpha).fit(X[tr], y[tr])
        scores.append(mean_squared_error(y[va], model.predict(X[va])))
    return float(np.mean(scores))

study = optuna.create_study(direction='minimize',
                            sampler=optuna.samplers.TPESampler(seed=0))
study.optimize(objective, n_trials=50)
study.best_params, study.best_value
```

Prefer the manual objective over `OptunaSearchCV` (moved to the separate
`optuna-integration` package, deprecation churn). Optuna's store is local — an
in-memory study by default, or `storage='sqlite:///study.db'` to persist. If you
persist it, `.gitignore` the store; it's a local artifact, not source.

**Guard against validation-set overfitting.** A large search over one held-out
split finds a knob that flatters *that split*. For big searches or high-stakes
decisions, wrap it in nested CV — an outer forward-chaining split whose training
half runs the whole study — so the reported score comes from folds the search
never touched.

### When not to tune

- **Fold-to-fold variance swamps the effect** — if the metric's spread across
  folds exceeds the gap between candidates, you're tuning noise; ship a default.
- **A prior already pins it** — if regularization is set by a domain prior (or
  is *part of* a Bayesian model), tune the model, not a CV knob.
- **A coarse grid is already flat** — a flat landscape on one pass is a valid
  stopping condition.

### Graduation

A tuning study answers "best knob for *this* model family." When a tuned model
becomes a contender you want to compare against structurally different models,
it graduates to one variant row in `track-model-experiments`' `experiments.md`
(`what changed` = "tuned `<class>` via Optuna, `<n>` trials, `<space>`"). The
trial history stays in Optuna's store (`optuna-dashboard` to browse); the ledger
records only the winner and why it earned a seat.

## Regime B — inference hyperparameters

These are convergence knobs, not predictive ones. Tune each to its diagnostic
and stop there — do **not** tune them to a held-out predictive metric.

| Knob | Objective | Stopping rule | Owned by |
|---|---|---|---|
| NUTS `target_accept` | eliminate divergences | 0 divergences, healthy E-BFMI | `bayesian-workflow` diagnostics |
| NUTS `max_tree_depth` | avoid tree saturation | no `reached_max_treedepth` warnings | `bayesian-workflow` |
| SVI learning rate / `num_steps` | ELBO convergence | ELBO plateaus, stable across seeds | `bayesian-workflow` |
| dynamax optax learning rate | training-loss convergence | loss plateaus, no divergence | `bayesian-workflow` |

The mechanics and thresholds live in `bayesian-workflow` — this table is the
router, not the doctrine.

## Boundary

- `model-selection-regularization.md` (in `recommend-probabilistic-model`) —
  *what* to tune and *why* (which knobs matter, how regularization trades bias
  for variance).
- `develop-testing-strategy` — leakage as a *permanent test invariant* (a
  no-future-leakage assertion that guards the pipeline forever).
- `bayesian-workflow` — inference diagnostics (regime B's mechanics).
- **This skill** — the *search loop*: the CV protocol, regime classification,
  the Optuna objective, and graduation.

## Scope caveat

`PurgedTimeSeriesSplit` guards **temporal** leakage only — train precedes val,
embargo, purge. For a **revised** series (GDP, employment, most macro data),
revision leakage is often bigger: training on the *final* vintage of a number
that was only available as a noisier *first* release uses data that didn't exist
as-of the decision date, and a green temporal-CV won't catch it. That's
`develop-testing-strategy` territory — model features as-of, not final.
