# recommend-probabilistic-model

A Claude Code skill that turns a **modeling problem + its data** into a **recommendation memo**:
candidate methods with trade-offs, a defensible default *with reasons*, exact citations into Kevin
Murphy's *Probabilistic Machine Learning* books, links to the matching
[`pyprobml`](https://github.com/probml/pyprobml) notebooks, and a structured handoff. It is an
**advisor/selector** — it recommends and points; it does not fit, evaluate, or report on a fitted
model (that's [`bayesian-workflow`](../bayesian-workflow/)'s job, or yours for non-Bayesian methods).

## How it works

- A thin **decision-map router** ([`references/decision-map.md`](references/decision-map.md)) maps
  *task × data signal* to one of **eight deep families** (`references/families/*.md`): regression /
  GLMs / counts, hierarchical, time-series & state-space, Gaussian processes, dimensionality
  reduction & factor models, classification, mixtures & clustering, and graphical models. Anything
  off-map routes to [`references/drill-down.md`](references/drill-down.md).
- **Regularization & model selection** is a cross-cutting Step 6
  ([`references/model-selection-regularization.md`](references/model-selection-regularization.md)),
  conditional on the chosen family — not a family of its own.
- The common path is **markdown only** (no PDFs, no search) — fast and small. A thin
  [`scripts/characterize.py`](scripts/characterize.py) adds the modeling signals `explore-data`'s
  profiler omits (overdispersion, zero-fraction, n/p, class balance, stationarity).

## Citation discipline

Every `§ref` and notebook link was built through a two-gate process: **Gate A** (mechanical — the
section number and notebook path exist) and **Gate B** (semantic — the cited section actually
supports the claim). No citation was written from memory.

## Licensing

The skill is an original work (MIT). It **cites and summarizes** Murphy's books (Book 1 © 2022 MIT;
Book 2 © 2023 K. P. Murphy), which are **CC-BY-NC-ND** — summaries are in original wording, no book
prose is reproduced, and no PDFs are bundled. `pyprobml` and [`dynamax`](https://github.com/probml/dynamax)
are **MIT** and are linked. See the repo [`NOTICE`](../../NOTICE).
