# recommend-visualization

A Claude Code skill that turns a **dataset + an intent** into a **chart recommendation and the code
to render it**. It is the visualization sibling of
[`recommend-probabilistic-model`](../recommend-probabilistic-model/): that one maps *task × data
signal* to a **model** and points; this one maps *intent × data signal* to a **view** — and, because
for a chart the recommendation (a mark plus encodings keyed to field types) is nearly the spec,
**carries through to code**.

## How it works

- **Phase 0 — handoff.** Consumes an [`explore-data`](../explore-data/) profile (`profile.py --json`)
  and keys off the exact fields it emits. The four signals the profile JSON omits — skew, outliers,
  top-N coverage, overplot risk — are computed in [`scripts/recommend.py`](scripts/recommend.py), the
  way `recommend-probabilistic-model`'s `characterize.py` adds modeling signals.
- **Phase 1 — recommend.** A thin **(intent × data-signal) router**
  ([`references/chart-selection.md`](references/chart-selection.md)) grounded in perceptual theory
  ([`references/encoding-principles.md`](references/encoding-principles.md)). `recommend.py` is the
  pure, unit-tested version: `(intent, fields, n_rows)` → ranked **chart candidates**, each with a
  rationale and an **encoding map** (field → channel).
- **Phase 2 — code.** Routes by purpose to **Altair** (exploratory/declarative, Polars-native),
  **matplotlib** (publication/static), or **plotly** (interactive/dashboard) — each reference carries
  the Polars→library boundary, the gotcha, and verified templates.

## Design notes

- **Polars-first.** All aggregation/reshaping is lazy Polars; only the small plot-ready frame is
  materialized at the render boundary. This is also what keeps Altair under its 5000-row
  `MaxRowsError`.
- **Library gotchas were verified, not transcribed** against the installed versions (Polars 1.42,
  Altair 6.2, matplotlib 3.11, plotly 6.8) — e.g. plotly-express now reads Polars frames directly via
  narwhals, so the old "`.to_pandas()` first" advice is a fallback, not the default.

## Licensing

Original work (MIT). It **cites** standard visualization literature (Cleveland & McGill 1984; Tufte
1983; Munzner 2014; Wilke 2019; Satyanarayan et al. 2017) by author-year — summarized in original
wording, nothing reproduced. See the repo [`NOTICE`](../NOTICE).
