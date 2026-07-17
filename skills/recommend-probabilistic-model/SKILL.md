---
name: recommend-probabilistic-model
description: >
  Use when choosing a modeling approach for a problem and its data — "which model/method should I
  use", "what approach fits this dataset", "recommend a model", "is this Poisson or negative
  binomial", "how do I handle overdispersion / zero-inflation / panel data / many predictors".
  Covers regression / GLMs / counts, classification, hierarchical/multilevel, time series &
  state-space, Gaussian processes, dimensionality reduction & (dynamic) factor models, mixtures &
  clustering, and probabilistic graphical models, grounded in Kevin Murphy's Probabilistic
  Machine Learning (PML) books. Trigger on model selection, "which method for X", recommending an
  approach before fitting, or deciding between Poisson/NB/zero-inflated, pooled vs hierarchical,
  GP vs parametric, PCA vs factor model, HMM vs state-space. Consult BEFORE fitting a model — not
  for executing the fit itself.
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
  sources: >
    Cites Kevin P. Murphy, Probabilistic Machine Learning (Book 1 © 2022 MIT; Book 2 © 2023
    K. P. Murphy) under CC-BY-NC-ND (summarized, not reproduced). Links pyprobml and dynamax (MIT).
---

# Recommend a Probabilistic Model

Given a **modeling problem** and (optionally) **its data**, diagnose the task, characterize the data,
and produce a **recommendation memo**: candidate methods with trade-offs, a defensible default *with
reasons*, verified PML §refs + pyprobml notebooks, and a structured handoff. This skill **recommends
and points — it does not fit, evaluate, or report on a fitted model.**

## This skill vs. its siblings

- **`explore-data`** *discovers* the data's shape (nulls, cardinality, distributions) — upstream of here.
- **`recommend-probabilistic-model`** (this) turns *shape × task* into a modeling **decision**.
- **`bayesian-workflow`** *executes* when the recommendation is "fit a Bayesian model" (NumPyro/JAX).
- **`bls-data-context`** supplies official-statistics / benchmark data that informs priors & pooling.
- **`validate-data`** *gates* the downstream result.

## Procedure (8 steps)

1. **Frame the problem.** Task type (regression / classification / counts / clustering / dim-reduction
   / time-series / structured / decision) **and the question** (point prediction vs. uncertainty /
   inference vs. causal vs. sequential decision).
2. **Characterize the data.** Profile the primary dataset (`explore-data`; then `scripts/characterize.py`
   for modeling signals it omits — overdispersion, zero-fraction, n/p, class balance, stationarity).
   **Inventory external/auxiliary information** (official statistics, benchmarks, related series,
   constraints) — see [references/external-data-and-priors.md](references/external-data-and-priors.md).
3. **Route.** Match (task × signal) in [references/decision-map.md](references/decision-map.md) → a
   family file in `references/families/`. Off-map problems → [references/drill-down.md](references/drill-down.md).
4. **Weigh 2–3 candidates** from the family file — assumptions, fit to the data, uncertainty, compute,
   interpretability — grounded in the profile, not generic.
5. **Recommend a default + WHY.** Explicit assumptions; state how external data informs priors/pooling/structure.
6. **Specify regularization & model selection (conditional on the chosen family).** Its complexity
   knob + the selection criterion — see [references/model-selection-regularization.md](references/model-selection-regularization.md).
   (Pre-fit specification; post-fit LOO/ELPD comparison is `bayesian-workflow`'s job.)
7. **Point & hand off.** Exact §refs + pyprobml links ([references/pyprobml-index.md](references/pyprobml-index.md))
   + the handoff payload.
8. **Persist.** Write `<slug>/recommendation.md` from [references/reporting.md](references/reporting.md).

## Which book (C3)

Topics in both books: **Book 1 = standard treatment** (default pointer); **Book 2 = advanced/extended**
(point when the problem needs the extension). Family files name both where both exist.

## Handoff interface (C4)

A Bayesian recommendation must carry — in `recommendation.md` §6 — everything `bayesian-workflow`
needs to start cold: **likelihood family, candidate priors (incl. any from external data), structure
(pooling/hierarchy/temporal), and the regularization/selection plan.** State-space / dynamic-factor
recommendations target **[dynamax](https://github.com/probml/dynamax)** (JAX SSMs); Bayesian fitting
goes to `bayesian-workflow` (NumPyro/BlackJAX).

Because the memo starts `bayesian-workflow` cold, this recommendation session's
own context — data profiling, candidate weighing, §ref hunting — is dead weight
downstream. Once `recommendation.md` is written (Step 8), recommend the user
`/clear` and invoke `bayesian-workflow` in a fresh session against the memo:
fitting then carries none of this consult's history and runs on its own model
default.

## Reference map

| File | Role |
|------|------|
| [references/decision-map.md](references/decision-map.md) | thin router: task × signal → family |
| `references/families/*.md` | per-family depth (8): methods, defaults, §refs, notebooks, gotchas, handoff |
| [references/model-selection-regularization.md](references/model-selection-regularization.md) | cross-cutting Step 6 |
| [references/pyprobml-index.md](references/pyprobml-index.md) | verified notebook map |
| [references/external-data-and-priors.md](references/external-data-and-priors.md) | external info → priors/pooling/constraints |
| [references/drill-down.md](references/drill-down.md) | long-tail navigation of the books + pyprobml |
| [references/reporting.md](references/reporting.md) | the `recommendation.md` template (handoff interface) |
| [scripts/characterize.py](scripts/characterize.py) | modeling signals `explore-data` omits |

## Stack notes

- The skill is **markdown** — the common path needs no PDFs and no extra tooling.
- `scripts/characterize.py` needs `polars` (Python ≥ 3.9).
- The drill-down path (rare) uses `pdftotext`/`pdftoppm` (poppler) only if the book PDFs are present
  locally; otherwise it falls back to pyprobml + the public book site.

## Attribution

Murphy's books are cited under **CC-BY-NC-ND** (summarized in original wording, never reproduced; PDFs
not bundled). `pyprobml`, `dynamax`, and `pml-book` materials are **MIT** (linked). See the repo
[`NOTICE`](../../NOTICE).
