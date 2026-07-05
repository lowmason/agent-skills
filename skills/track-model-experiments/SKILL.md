---
name: track-model-experiments
description: >
  Use when iterating over multiple Bayesian/probabilistic model variants and losing
  track of them — trying different priors, likelihoods, distribution parameters, or
  hierarchical structure across churn-logistic → v2 → v3 and unable to reconstruct
  what changed or why one won. Trigger on: comparing many NumPyro/ArviZ model
  versions, "which model fits best", keeping an experiment log or ledger of model
  runs, ranking variants by ELPD/LOO, recording what changed between model versions,
  deciding which variant to ship, or knowing when to stop iterating. Sits above a
  per-variant analysis folder and complements bayesian-workflow's model comparison.
  Not for tuning continuous ML hyperparameters (that is tune-hyperparameters).
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
---

# Track Model Experiments

## Overview

`bayesian-workflow` fits, criticizes, and reports on one model. Real analyses
rarely stop at one: a different prior, a swapped likelihood, an added
hierarchical level — each attempt lands in its own slug folder
(`churn-logistic-v1/`, `-v2/`, `-v3/`, ...). Past three or four variants,
memory fails: you can rank them by eye but can't say what changed between v2
and v3, or why v5 was abandoned.

This skill is the iteration layer above single-model workflow. Core
principle: one file records *what changed and why* (a human-authored ledger);
one script records *which won* (an ArviZ-based comparator that ranks variants
and stamps the result back into the ledger).

## When to use

- Lost track of which of a dozen variants tried what, or can't reconstruct
  why v7 beat v6.
- Starting variant #2 of a model and want the comparison trail set up before
  forking, not after.
- Deciding which variant to ship and want the decision recorded, not just
  remembered.
- A hyperparameter search in `tune-hyperparameters` produced a winner worth
  comparing against structurally different models — graduate it to a variant
  row here (`what changed` = "tuned `<class>` via Optuna").

Not for:
- **A single model, no iteration** — follow `bayesian-workflow` alone;
  there's nothing to track yet.
- **Tuning continuous ML hyperparameters** (learning rate, tree depth,
  regularization) — that's `tune-hyperparameters`, a search over a continuous
  space rather than discrete, hypothesis-driven model variants.

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
hand-edit them. The Decision log is free-form prose: record the call and the
reason, not just the winner.

## The comparator

`scripts/compare_experiments.py` loads each variant's `inference_data.nc`,
ranks them with `az.compare`, and (optionally) rewrites the ledger's
`<!-- COMPARISON -->` block in place.

```bash
uv run --python 3.13 --with numpyro --with arviz --with arviz-stats --with numpy \
  --with h5netcdf --with h5py python scripts/compare_experiments.py \
  --analysis-dir <analysis-dir> --ledger <analysis-dir>/experiments.md --output comparison.json
```

Run `--help` for the rest (`--folders` compares an explicit subset instead of
auto-discovering every `*/inference_data.nc` under `--analysis-dir`). The
`h5netcdf`/`h5py` pair is required — `az.from_netcdf` needs a netCDF backend
that does not install transitively with `arviz`.

Three guardrails, enforced before any ranking happens:
- **Missing `log_likelihood` group** → hard error naming the variant and the
  fix (refit with `az.from_numpyro(..., log_likelihood=True)`).
- **Mismatched observation counts across variants** → refused outright; LOO
  only compares predictions of the *same* held-out observations.
- **High Pareto-k / other `az.compare` diagnostic warnings** → surfaced as a
  `warning` flag per variant in `comparison.json` and a `⚠` in the ledger
  table, not silently dropped.

## Stopping rule

Stop iterating — don't keep chasing ELPD — when either holds:

- **ΔELPD < 2×dSE** between the top variants — statistically
  indistinguishable; ship the simpler one.
- **Conclusions are stable across every variant that passes its diagnostics**
  — the multiverse view (Gelman et al. 2020, §8): once the story doesn't
  change across passing models, which one is "best" matters less.

For the interpretation thresholds themselves (the 2×/4×dSE bands, when to
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
