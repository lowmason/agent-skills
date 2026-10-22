---
name: track-model-experiments
description: >
  Use when iterating over several model variants and losing track of them — Bayesian
  variants that try different priors, likelihoods, or hierarchical structure, or
  tabular-CV and forecast-backtest variants scored on one shared criterion — and
  unable to reconstruct what changed or why one won. Trigger on: keeping an
  experiment log or ledger of model runs, "which model fits best", ranking variants
  by ELPD/LOO, ranking variants by cross-validation fold scores or backtest scores,
  leave-future-out (LFO) comparison of forecasting models, comparing variants against
  a naive or seasonal-naive benchmark baseline, recording what changed between model
  versions, deciding which variant to ship, or knowing when to stop iterating. Sits
  above per-variant analysis folders and complements bayesian-workflow's model
  comparison. Not for tuning continuous hyperparameters (that is
  tune-hyperparameters). Not for neural runs or checkpoints (that is
  evaluate-deep-learning).
license: MIT
compatibility: Requires uv to run bundled scripts (dependencies are declared inline); Python 3.12+.
metadata:
  author: Lowell Mason
  version: "1.0"
# cc-guide: lean.session-hygiene @2.1.306
---

# Track Model Experiments

## Overview

`bayesian-workflow` fits, criticizes, and reports on one model. Real analyses
rarely stop at one: a different prior, a swapped likelihood, an added
hierarchical level — each attempt lands in its own slug folder
(`churn-logistic-v1/`, `-v2/`, `-v3/`, ...). Past three or four variants,
memory fails: you can rank them by eye but can't say what changed between v2
and v3, or why v5 was abandoned.

The same holds for a cross-validated regression that gains a feature set, or a
forecaster that meets a rival in a backtest.

This skill is the iteration layer above single-model work. Core principle: one
file records *what changed and why* (a human-authored ledger); one script
records *which won* (a comparator that ranks variants and stamps the result
back into the ledger). The comparator has two modes, and a ledger uses one:

- **ELPD mode** ranks Bayesian fits by PSIS-LOO from each variant's
  `inference_data.nc`.
- **Score mode** ranks any variants (tabular cross-validation, forecast
  backtests, or Bayesian fits scored by leave-future-out) from each variant's
  `scores.json`: one score per fold or forecast origin, on one shared
  criterion. `references/predictive-evaluation.md` holds the protocol and the
  file's contract.

## When to use

- Lost track of which of a dozen variants tried what, or can't reconstruct
  why v7 beat v6.
- Starting variant #2 of a model and want the comparison trail set up before
  forking, not after.
- Deciding which variant to ship and want the decision recorded, not just
  remembered.
- Ranking cross-validated or backtested variants of any model class on one
  criterion (fold MSE, log-loss, CRPS, leave-future-out ELPD) — score mode.
- A hyperparameter search in `tune-hyperparameters` produced a winner worth
  comparing against structurally different models — graduate it to a variant
  row here (`what changed` = "tuned `<class>` via Optuna"), with a
  `scores.json` on the ledger's criterion. A non-Bayesian winner has no
  `inference_data.nc`, so it ranks only in a score ledger. To compare it with
  the variants of an existing `elpd-loo` ledger, first re-declare that
  ledger's criterion as a score criterion. Each Bayesian variant then writes
  `scores.json` on the same units, for example a per-fold log score or the MSE
  of the posterior-predictive mean. Until that is done, the comparator names
  the new row as not compared.

Not for:
- **A single model, no iteration** — follow `bayesian-workflow` alone;
  there's nothing to track yet.
- **Tuning continuous ML hyperparameters** (learning rate, tree depth,
  regularization) — that's `tune-hyperparameters`, a search over a continuous
  space rather than discrete, hypothesis-driven model variants.
- **Neural runs or checkpoints** — `evaluate-deep-learning` owns their
  experiment record.

## The ledger (experiments.md)

One `experiments.md` per analysis, next to the variant slug folders. The
human fills the left half of the table when opening a new variant; the
comparator fills the right half after every run.

```markdown
# Experiments — <analysis-name>

All variants below are fit to the SAME observations (required for ELPD
comparison — the comparator refuses to compare variants with different
observation counts).

| id (slug) | parent | what changed | hypothesis | ELPD | ΔELPD | max R̂ | div | PPC | psense | status |
|---|---|---|---|---|---|---|---|---|---|---|
| churn-logistic-v1 | — | baseline logistic, flat priors | establishes a floor | | | | | | | candidate |
| churn-logistic-v2 | v1 | Normal(0,1.5) priors on coeffs | v1's priors were too wide, hurting shrinkage | | | | | | | candidate |
| churn-logistic-v3 | v2 | added varying intercept by region | region-level pooling should improve ELPD | | | | | | | candidate |

<!-- COMPARISON:BEGIN -->
(populated by compare_experiments.py)
<!-- COMPARISON:END -->

## Decision log
- <date>: shipped churn-logistic-v3 — best ELPD, stable under prior sensitivity,
  no divergences. v2 rejected: region pooling in v3 explained residual
  clustering v2 missed.
```

`id`, `parent`, `what changed`, `hypothesis`, and `status` are yours to write —
the reasoning trail no script can reconstruct after the fact. `ELPD` through
`psense` are metric columns the comparator overwrites each run; don't
hand-edit them. The comparator finds this table by its header (the first one that starts
with `id` and has a `status` column), fills a column only under the names
shown here (case and symbols included; a note says when none match), and moves
the best marker in `status`. The Decision log is free-form prose: record the
call and the reason, not just the winner.

**One criterion per ledger.** A ledger declares its criterion in one
`Criterion: <name>` line above the Variants table. A ledger without that line
reads as `elpd-loo`, so the ELPD ledger above needs none. The comparator
refuses a run whose mode does not match the criterion, and a variant whose
`scores.json` names another criterion. A score ledger swaps the ELPD metric
columns for `score`, `Δscore` and `SE(Δ)`:

```markdown
# Experiments — county-nowcast

Criterion: backtest-mse-h1

All variants below are scored on the SAME 24 forecast origins (required for the
paired difference — the comparator refuses variants with different unit keys).

| id (slug) | parent | what changed | hypothesis | score | Δscore | SE(Δ) | status |
|---|---|---|---|---|---|---|---|
| naive-last | — | last value carried forward | the floor every variant must beat | | | | candidate |
| ridge-lags | naive-last | ridge on 12 lags | lags carry the signal | | | | candidate |
| gbm-tuned | ridge-lags | tuned `HistGradientBoostingRegressor` via Optuna | lag effects are nonlinear | | | | candidate |

<!-- COMPARISON:BEGIN -->
(populated by compare_experiments.py --mode score)
<!-- COMPARISON:END -->
```

## The comparator

`scripts/compare_experiments.py` ranks the variants and (optionally) rewrites
the ledger's `<!-- COMPARISON -->` block in place. ELPD mode, the default,
loads each variant's `inference_data.nc` and ranks with `az.compare`. Score
mode (`--mode score`) loads each variant's `scores.json`, ranks by mean score
with the file's orientation, and reports each variant's paired difference from
the top variant (Δscore) with its standard error (SE(Δ)).

```bash
uv run <this-skill-dir>/scripts/compare_experiments.py \
  --analysis-dir <analysis-dir> --ledger <analysis-dir>/experiments.md --output comparison.json
uv run <this-skill-dir>/scripts/compare_experiments.py --mode score \
  --analysis-dir <analysis-dir> --ledger <analysis-dir>/experiments.md --output comparison.json
```

Without uv, run the same path with `python3` in an environment that has the
dependencies listed in the script's header. The header declares the
`h5netcdf`/`h5py` pair because `az.from_netcdf` needs a netCDF backend that
does not install transitively with `arviz`.

Run `--help` for the rest (`--folders` compares an explicit subset instead of
auto-discovering every `*/inference_data.nc`, or every `*/scores.json` in
score mode, under `--analysis-dir`). `comparison.json` records the `mode` and
the `criterion` beside the ranking.

Guardrails in both modes, before any ranking and before anything is written:
- **A `--ledger` path that is not a file**, or a ledger whose COMPARISON
  markers are unpaired, repeated or out of order → refused. The comparator
  rewrites the text from one BEGIN marker to the next END marker, so a stray
  marker would overwrite the ledger's prose.
- **A mode that does not match the ledger's criterion** → refused, naming the
  mode to run.

ELPD-mode guardrails:
- **A folder with no `inference_data.nc`** (named in `--folders`) → error
  naming it; ELPD mode ranks Bayesian fits only, and a variant without a fit
  belongs in a score ledger.
- **Missing `log_likelihood` group** → hard error naming the variant and the
  fix (refit with `az.from_numpyro(..., log_likelihood=True)`).
- **A log-likelihood that LOO cannot leave terms out of** → refused, with the
  remedy. One summed `numpyro.factor` has no observation dimension: store one
  term per time step. Several log-likelihood variables (one per source) must
  become one pointwise variable, summed over one shared observation dimension.
  `bayesian-workflow/references/state-space.md` shows both.
- **Mismatched observation counts across variants** → refused outright; LOO
  only compares predictions of the *same* held-out observations. The count is
  the number of pointwise log-likelihood terms.

Score-mode guardrails, each through `error:` with the variant and the fix:
- a folder with no `scores.json` (named in `--folders`);
- a `criterion` that differs from the ledger's or from another variant's;
- an `orientation` that differs across variants;
- unit keys that differ across variants (the paired difference compares the
  same folds or origins);
- a non-finite value, or fewer than two units.

After ranking:
- **High Pareto-k / other `az.compare` diagnostic warnings** (ELPD mode) →
  surfaced as a `warning` flag per variant in `comparison.json` and a `⚠` in
  the ledger table, not silently dropped.
- **A ledger row the comparator did not rank** (no fit or no `scores.json`, or
  left out of `--folders`) → named on stderr, in `comparison.json`'s
  `not_compared` list and under the COMPARISON table. The list is filled only
  when you pass `--ledger`. While one exists, the top row's status reads
  `**best among ELPD-compared variants**` (score mode:
  `**best among score-compared variants**`), not `**best**`.
- **A ranked variant with no ledger row, a row with more cells than the
  header, or a table with none of the mode's metric columns** → a note on
  stderr says so, and what it means for the best marker.

## Fresh session per variant

Each variant wraps a full `bayesian-workflow` fit/diagnose/report loop — long,
and it accumulates in your session. Once a variant's row is stamped by the
comparator and its decision-log entry written, the ledger holds everything the
next variant needs: what every prior variant changed, why, and how it scored.
Carrying the prior variant's fitting conversation forward re-reads that history
every turn and buys nothing.

So iterate one variant per session: when a variant's ledger row and decision log
are current, `/clear` and start the next variant fresh, resuming by reading
`experiments.md` (and the parent variant's slug folder when forking from it) —
not the prior conversation. **Update the ledger and decision log BEFORE you
clear**, in that order: after `/clear` the reasoning in your head is gone, and
the ledger is the only durable record of what changed and why.

## Stopping rule

Stop iterating — don't keep chasing the criterion — when any of these holds:

- **|ΔELPD| < 4** between the top variants — a small difference (`diag_diff`
  flags it); ship the simpler one. Above 4, weigh ΔELPD against dSE only with
  more than 100 observations and no badly misspecified variant.
- **Score mode: |Δscore| < 2·SE(Δ)** between the top variants — the
  difference is noise; ship the simpler one. The plain SE(Δ) is optimistic:
  training sets overlap across folds and origins, and h-step forecast errors
  are autocorrelated. For a high-stakes call, apply the corrections in
  `references/predictive-evaluation.md`.
- **Conclusions are stable across every variant that passes its diagnostics**
  — the multiverse view (Gelman et al. 2026, §9.3 and §9.5): once the story
  doesn't change across passing models, which one is "best" matters less.

A long ledger flatters its winner: picking the best of many variants by ELPD
carries a selection-induced bias (McLatchie & Vehtari 2024). With a few
variants it is usually negligible; with many, estimate it (nested CV, or
their order-statistics correction) before claiming the winner beats a close
runner-up.

For the interpretation rule itself (|ΔELPD| < 4, the conditions on dSE, when to
prefer stacking over selection), see
`bayesian-workflow/references/model-comparison.md` — this skill points at
that doctrine rather than restating it.

## Relationship to bayesian-workflow

- **`track-model-experiments`** (this skill) owns the *iteration ledger* —
  what changed between variants, why, and which one was chosen.
- **`bayesian-workflow`'s `model-comparison.md`** owns the *statistics* — what
  ELPD/LOO/stacking weights mean and how to read them.
- **`bayesian-workflow`'s `reporting.md`** owns the *per-variant slug folder*
  — the fixed-shape artifact set (`inference_data.nc`, `report.md`, etc.) that
  each row of the ledger points to.
- **`references/predictive-evaluation.md`** (this skill) owns the *score-mode
  protocol*: backtests, the `scores.json` contract, the paired difference and
  its limits, benchmark baselines and proper scores. `bayesian-workflow`'s
  `model-comparison.md` shows how a Bayesian variant writes leave-future-out
  or blocked K-fold scores for it.
- **`tune-hyperparameters`** owns the *search* inside one model class; its
  winner graduates to a row here. **`evaluate-deep-learning`** owns neural
  runs and their experiment record.
