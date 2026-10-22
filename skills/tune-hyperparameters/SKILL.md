---
name: tune-hyperparameters
description: >
  Use when tuning any model's knobs without leaking or overfitting — sklearn and
  boosting models, statsmodels, NumPyro and dynamax fits, or neural nets from
  deep-learning. Trigger on: "which hyperparameters", searching regularization
  strength, tree depth, or learning rate; grid/random/Optuna search; choosing a
  CV splitter for grouped, spatial, or independent rows; temporal data —
  rolling-origin / walk-forward / purged / embargoed CV and future leakage;
  structural choices such as the number of mixture components, factors, or HMM
  states, AR order, spline knots, or kernel form; inference knobs (NUTS
  target_accept / max_tree_depth, SVI learning rate/steps); early stopping,
  pruning, or a trial budget; when NOT to tune; or graduating a tuned winner to
  a compared variant. Guards temporal leakage; revision/vintage leakage belongs
  to develop-testing-strategy.
license: MIT
effort: xhigh
metadata:
  author: Lowell Mason
  version: "1.0"
# cc-guide: skills.frontmatter @2.1.306
---

# Tune Hyperparameters

## Overview

Hyperparameters are the knobs set *before* the fit — regularization strength,
tree depth, learning rate, a sampler's `target_accept`, the number of mixture
components. Tuning is the loop above a single fit: propose a value, score it,
keep the best. The loop is the same for any producer: sklearn and boosting,
statsmodels, NumPyro, dynamax or a neural net. Two things break that
loop: tuning the wrong *kind* of knob against the wrong objective (a held-out
metric for a sampler setting overfits the approximation), and scoring on data the
model shouldn't have seen yet (temporal leakage inflates every candidate equally,
so the winner is an artifact).

Core principle: **classify the regime first, then tune the right objective with
the right leakage guard.**

## Step 0 — classify the regime

The rule puts each knob in exactly one regime. A knob is **Regime B** when its
correct value is defined by the fidelity of the fit — whether the sampler or
optimizer reached what the model already defines (its posterior, or its
optimum). A knob is **Regime C** when it picks the structure of a probabilistic
model from a discrete set: how many components, factors, states or lags the
model has, or the form of its kernel or basis. Every other knob is
**Regime A**: its correct value is the one that predicts held-out data best.
A knob that sets one predictor's flexibility (a penalty, tree depth, `k` for
kNN) is Regime A, even when its values are discrete.

- **Regime A — predictive search.** You're choosing a knob that trades bias for
  variance on *held-out prediction*: `alpha`/`C` (regularization), tree depth /
  `min_child_weight`, learning rate + `n_estimators` for a boosting/tabular
  model, `k` for kNN. A neural network's learning rate is Regime A too: it
  shapes which solution the network finds, and only held-out data can say
  which one is best. Evaluate on a held-out metric. Leakage is the enemy.
- **Regime B — inference / optimization diagnostic.** You're setting a knob that
  controls whether the *fit itself* is trustworthy: NUTS `target_accept` /
  `max_tree_depth`, SVI learning rate / steps, the optax learning rate of a
  non-neural point fit such as a dynamax MLE.
  Evaluate on convergence diagnostics, **not** on a held-out predictive metric.
- **Regime C — structural choice.** You're choosing among model structures:
  the number of mixture components `K`, of factors or of HMM states, the AR
  order, spline knots, a GP kernel form. Each candidate is a separate model,
  so score it on a criterion that compares whole models (Regime C, below).

The stakes of getting this wrong: a regime-B knob tuned to a held-out score
overfits the inference approximation to your validation split — you get a
sampler that looks good on one metric and is miscalibrated everywhere else.

## Regime A — leakage-safe predictive search

### Step 0b — choose the splitter by dependence structure

Validation rows must be as independent of the training rows as new data will
be. Pick the splitter from how the rows depend on each other:

| Data | Splitter |
|---|---|
| i.i.d. | `KFold`, or `StratifiedKFold` for classes |
| Grouped, or predicting new entities | `GroupKFold` or `LeaveOneGroupOut` |
| Spatial | `GroupKFold` over spatial blocks |
| Temporal | the bundled `PurgedTimeSeriesSplit` (the protocol below) |
| Random forests | out-of-bag error |

All but the temporal splitter are sklearn's. A panel is temporal: use the
bundled splitter with `groups=period`. The rest of this section is the temporal
protocol.

**The trap.** Naive k-fold ignores time order, so most folds train on rows that
come *after* the validation block (shuffling makes it worse, but plain
`KFold` already does it). For anything time-ordered — a nowcast, a panel, any
series — that leaks the future into training and every candidate's score comes
back over-optimistic. You can't compare knobs on a corrupted metric.

**The CV protocol.** Use forward-chaining (expanding-window) splits where train
always precedes validation.

- **Point-in-time target, single series** (one row per period, label known at
  the row's own timestamp): sklearn's `TimeSeriesSplit(gap=embargo)` already
  suffices. Add an **embargo** — a gap of a few periods between train and val —
  to absorb autocorrelation bleed at the boundary.
- **Panel** (several series observed at the same periods, one row per series
  and period): split periods, not rows. `TimeSeriesSplit` splits rows, so the
  same period lands in both train and validation. Use this skill's splitter
  (below) and pass each row's period: `cv.split(X, groups=period)`. The period
  labels must sort in time order, because the splitter sorts them. Integers,
  dates and zero-padded strings such as `'2020-09'` do. `'2020-9'` does not.
- **Multi-period target** (label at row `i` spans `[i, i+h]`, e.g. an
  `h`-period-ahead return or a rolling outcome): the naive split still leaks,
  because a train row near the boundary has a label window reaching *into* the
  validation block. You must **purge** those rows. Reach for this skill's
  `scripts/time_series_cv.py`:

```python
import sys
sys.path.insert(0, '<this-skill-dir>/scripts')   # or copy time_series_cv.py beside your code
from time_series_cv import PurgedTimeSeriesSplit
# embargo always; purge only when the label spans h>1 periods.
cv = PurgedTimeSeriesSplit(n_splits=5, embargo=2, label_horizon=h)
```

It yields expanding-window `(train_idx, val_idx)` with `train = [0, s_k -
max(embargo, label_horizon))` — embargo and purge carve the same pre-val region,
so the binding one is `max`, not the sum. `test_size`, `embargo`,
`label_horizon` and `min_train_size` all count periods: on a panel, pass
`groups=period` to `split` (and to `GridSearchCV.fit`), and without it each row
is one period. The labels in `groups` must sort in time order, and the sizes
count the periods present in `groups`, so a missing calendar period leaves a
wider real gap. It duck-types sklearn's splitter API, so it drops straight into
the objective below.

**What to score.** Match the objective to what the model emits:

| Model emits | Objective |
|---|---|
| Point predictions | MSE or MAE, or a loss that matches the decision |
| Predictive distributions | log score or CRPS (strictly proper) |
| Class probabilities | log-loss or Brier, never accuracy alone |
| Forecasts | per-origin loss differences |

**The search — a manual Optuna objective** (verified against Optuna 5.0.0). Keep
the objective explicit: suggest the knobs, loop over `cv.split(X)`, return the
mean CV score. A seeded `TPESampler` reproduces a run within one Optuna
version, not across versions: 5.0 changed the sampler's defaults (among them
`constant_liar=True`), so record the version beside the seed.

```python
import numpy as np, optuna
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error

def objective(trial):
    alpha = trial.suggest_float('alpha', 1e-3, 1e3, log=True)
    scores = []
    for tr, va in cv.split(X):           # a panel: cv.split(X, groups=period)
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

**Early stopping.** Take the stopping split from inside the training fold (the
last periods of `tr` for temporal data), never from the CV validation fold. A
fit that stops on the validation fold has seen it, so that fold's score is no
longer held out.

**Guard against validation-set overfitting.** A large search over one set of
folds finds a knob that flatters *those folds*. For big searches or high-stakes
decisions, nest it: an outer forward-chaining split runs the whole study on
each training half and scores the winner on the outer validation fold, which
the search never touched (verified against Optuna 5.0.0 and scikit-learn
1.9.1):

```python
outer = PurgedTimeSeriesSplit(n_splits=4, embargo=2)
outer_scores = []
for tr, te in outer.split(X):            # a panel: outer.split(X, groups=period)
    X_tr, y_tr = X[tr], y[tr]
    inner = PurgedTimeSeriesSplit(n_splits=5, embargo=2)

    def objective(trial):
        alpha = trial.suggest_float('alpha', 1e-3, 1e3, log=True)
        scores = []
        for fit, va in inner.split(X_tr):  # a panel: groups=period[tr]
            model = Ridge(alpha=alpha).fit(X_tr[fit], y_tr[fit])
            scores.append(mean_squared_error(y_tr[va], model.predict(X_tr[va])))
        return float(np.mean(scores))

    study = optuna.create_study(direction='minimize',
                                sampler=optuna.samplers.TPESampler(seed=0))
    study.optimize(objective, n_trials=50)
    winner = Ridge(**study.best_params).fit(X_tr, y_tr)
    outer_scores.append(mean_squared_error(y[te], winner.predict(X[te])))
float(np.mean(outer_scores))             # report this, not study.best_value
```

### Neural search

deep-learning and evaluate-deep-learning hand a neural search to this loop. A
neural learning rate stays Regime A.

- **Trial budget.** Fix the number of trials, and the epochs each trial may
  use, before the search starts.
- **Pruners.** Stop weak trials early with `optuna.pruners.MedianPruner`, or
  `SuccessiveHalvingPruner` for successive halving. The objective calls
  `trial.report(score, epoch)` each epoch and raises `optuna.TrialPruned()`
  when `trial.should_prune()` is true.
- **Early stopping** takes its split from inside the training fold (above).
- **Seeds.** One seed per trial ranks luck as much as the knob. Re-run the
  finalists over several seeds before you choose.

deep-learning owns schedule and state mechanics. evaluate-deep-learning owns
comparable-budget rules and the experiment record.

### When not to tune

- **The paired difference is noise** — score both candidates on the same folds
  and take the per-fold differences d. When |Δ|, the absolute mean of d, is
  under 2·SE(Δ) = 2·sd(d)/√K over K folds, ship the default. This is a screen.
  The protocol, and the corrections that widen the SE for high-stakes calls,
  are in `track-model-experiments/references/predictive-evaluation.md`.
- **A prior already pins it** — if regularization is set by a domain prior (or
  is *part of* a Bayesian model), tune the model, not a CV knob.
- **A coarse grid is already flat** — a flat landscape on one pass is a valid
  stopping condition.

### Graduation

A tuning study answers "best knob for *this* model family." When a tuned model
becomes a contender you want to compare against structurally different models,
it graduates to one variant row in `track-model-experiments`' `experiments.md`
(`what changed` = "tuned `<class>` via Optuna, `<n>` trials, `<space>`"). Its
variant folder holds a `scores.json` on the ledger's criterion, with one score
for each fold or origin that every other variant uses, and the comparator
ranks it in score mode.

An `elpd-loo` ledger cannot rank a non-Bayesian winner. To compare the winner
with the Bayesian variants, re-declare the ledger's `Criterion:` line as a
score criterion, and swap its ELPD columns for `score`, `Δscore` and `SE(Δ)`.
Each Bayesian variant then writes `scores.json` on the same units, for example
a per-fold log score or the MSE of the posterior-predictive mean. Until that is
done, the comparator names the new row as not compared. It never drops the
row in silence. The trial history stays in Optuna's store (`optuna-dashboard`
to browse); the ledger records only the winner and why it earned a seat.

## Regime B — inference hyperparameters

These are convergence knobs, not predictive ones. Tune each to its diagnostic
and stop there — do **not** tune them to a held-out predictive metric.

| Knob | Objective | Stopping rule | Owned by |
|---|---|---|---|
| NUTS `target_accept` | clear divergences that come from step size | rung 1 of the escalation ladder: the divergence fraction decides whether raising it helps or hides a model problem | `bayesian-workflow/references/diagnostics.md`, "When sampling fails: the escalation ladder" |
| NUTS `max_tree_depth` | avoid tree saturation | the `reached_max_tree_depth` sample stat is false on every draw: collect `num_steps` in `extra_fields`, and `diagnose_model.py`'s `treedepth` block reads it. NumPyro prints no warning | `bayesian-workflow/references/diagnostics.md` |
| SVI learning rate / `num_steps` | the approximation converged | the three checks: a flat ELBO trace that every seed reaches, PSIS-LOO for the approximation, VSBC | `bayesian-workflow/references/svi.md` |
| optax learning rate of a non-neural point fit (dynamax MLE) | the optimizer reached the optimum | the training loss plateaus, and restarts from several initializations reach the same optimum within a stated tolerance | this skill |

The mechanics and thresholds live in the files each row names — this table is
the router, not the doctrine.

## Regime C — structural choices

Score each candidate on one of these criteria, on the same data, folds or
origins for every candidate:

- the type-II marginal likelihood, where it is exact (a GP kernel form);
- BIC or AIC, a quick screen of point fits;
- LOO, or LFO for forecasts, over the discrete index (`K = 1, 2, 3, …`);
- a rolling-CV log score.

This skill runs the sweep: a loop over the index, not an Optuna study. When
the candidate set is small and each candidate carries its own hypothesis (two
regimes or three, a seasonal term or none), record the candidates as rows in
track-model-experiments' ledger instead, so each one keeps its reason.

GP hyperparameters fit by type-II marginal likelihood (lengthscales,
amplitude, noise) are set inside the fit, not tuned. Regime C covers only the
choice of kernel form.

## Producers

The loop is the same whoever produced the model. The regime and the
objective change:

| Producer | Regime | Objective |
|---|---|---|
| recommend-probabilistic-model | A or C: it names the knob and its criterion | the criterion it names |
| bayesian-workflow | B for sampler and SVI knobs; C for structure | convergence diagnostics; LOO, or LFO for forecasts |
| deep-learning | A | a held-out loss or metric (Neural search, above) |
| evaluate-deep-learning | A, under its comparable-budget rules | its declared primary metric |
| recommend-causal-design | A, for nuisance learners only | predictive CV inside cross-fitting folds (Boundary, below) |

## Boundary

- `model-selection-regularization.md` (in `recommend-probabilistic-model`) —
  *what* to tune and *why* (which knobs matter, how regularization trades bias
  for variance).
- `develop-testing-strategy` — leakage as a *permanent test invariant* (a
  no-future-leakage assertion that guards the pipeline forever).
- `bayesian-workflow` — inference diagnostics (regime B's mechanics).
- `recommend-causal-design` — the design, the adjustment set, an RD bandwidth,
  synthetic-control weights and the effect estimate. Predictive CV is the
  right objective only for nuisance learners (propensity and outcome models)
  tuned inside cross-fitting folds, and it never selects any of those.
- **This skill** — the *search loop*: regime classification, the splitter, the
  CV protocol, the Optuna objective, structural sweeps, neural search, and
  graduation.

## Scope caveat

`PurgedTimeSeriesSplit` guards **temporal** leakage only — train precedes val,
embargo, purge. For a **revised** series (GDP, employment, most macro data),
revision leakage is often bigger: training on the *final* vintage of a number
that was only available as a noisier *first* release uses data that didn't exist
as-of the decision date, and a green temporal-CV won't catch it. That's
`develop-testing-strategy` territory — model features as-of, not final.
