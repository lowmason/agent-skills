---
name: recommend-visualization
description: >
  Use when you need to choose — and then build — the right chart for a dataset: "which chart should
  I use", "how do I visualize this", "what's the best plot for X", "recommend a visualization", or
  building a figure in Altair / matplotlib / plotly. Trigger on a visualization intent (trend over
  time, comparison, distribution, correlation / relationship, part-to-whole, ranking, geographic,
  flow) and on the symptoms of a bad chart choice: "too many slices for a pie", an overplotted
  scatter / blob of points, a spaghetti multi-line, a skewed distribution that needs a log scale,
  "top-N with an other bucket", small multiples / faceting, dual-axis or 3D temptations, a
  colorblind-safe palette, direct labels vs. a legend, or deciding between Altair, matplotlib, and
  plotly. Also when turning an explore-data profile into a chart, or picking encodings (which field
  maps to x / y / color / facet / size). Polars-first.
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
  sources: >
    Cites standard visualization literature by author-year only (Cleveland & McGill 1984; Tufte
    1983; Munzner 2014; Wilke 2019; Satyanarayan et al. 2017) — summarized, nothing reproduced.
---

# Recommend a Visualization

Given a **dataset** (ideally an `explore-data` profile) and an **intent**, recommend the chart that
fits the data's *signals* — not just the intent — then write the code in your stack. The
differentiator over an off-the-shelf intent→chart lookup: this conditions on cardinality, row count,
skew/outliers, panel shape, and null rates, and ships the **encoding map** (field → channel), which
is nearly the spec. Unlike its sibling `recommend-probabilistic-model` (which recommends and points
but does not fit), this one **carries through to code** — for a chart, the recommendation *is* almost
the implementation.

## This skill vs. its siblings

- **`explore-data`** *profiles* the dataset (shape, nulls, cardinality, keys) — upstream of here.
- **`recommend-probabilistic-model`** turns *shape × task* into a **model**; **this** turns
  *shape × intent* into a **view**. Both consume the same `explore-data` profile; one recommends and
  points, this one recommends *and renders*.
- **`bayesian-workflow`** has its own `references/visualize.md` — that's visualization *inside* a
  Bayesian analysis (prior/posterior predictive, MCMC diagnostics, LOO-PIT) in ArviZ. This skill is
  general chart selection for any tabular dataset. Use that one when the thing you're plotting is a
  fitted model's draws; use this one for the data.
- **`validate-data`** *gates* the result downstream.

## Procedure

### Phase 0 — Take the handoff from `explore-data`
Run `explore-data`'s `profile.py --json` (or read an existing profile). The recommender keys off the
exact fields it emits — `n_rows`, `columns[].{dtype, n_unique, null_pct}`, `dates{}`,
`panel_balance` — and computes the four signals the profile JSON omits (skew, outliers, top-N
coverage, overplot risk). The contract and these signals are spelled out in
[references/chart-selection.md](references/chart-selection.md) (Phase 0).

### Phase 1 — Recommend (intent × data-signal → chart)
Name the intent (trend-over-time / comparison / distribution / correlation / part-to-whole / ranking
/ geographic / flow), read the signal, and match the row in
[references/chart-selection.md](references/chart-selection.md). Decide ties with the perceptual
hierarchy in [references/encoding-principles.md](references/encoding-principles.md)
(**position > length > angle/area > color**). [`scripts/recommend.py`](scripts/recommend.py) does
this programmatically — a pure, unit-tested function from `(intent, fields, n_rows)` to **ranked
chart candidates**, each with a rationale and an **encoding map**. Output: the candidates + the
encoding map, which is the input to Phase 2.

```bash
# profile -> ranked recommendation (signals like skew computed from the raw frame)
uv run --python 3.13 --with polars python \
    ~/.claude/skills/explore-data/scripts/profile.py data.parquet --json profile.json
uv run --python 3.13 --with polars python \
    ~/.claude/skills/recommend-visualization/scripts/recommend.py data.parquet \
    --profile profile.json --intent correlation
```

### Phase 2 — Code (route the library by purpose)
The encoding map from Phase 1 is a near-direct spec. Pick the library by where the figure is going:

| Purpose | Library | Reference |
|---------|---------|-----------|
| exploratory / declarative (default) | **Altair** (Polars-native) | [references/altair.md](references/altair.md) |
| publication / static (PDF/SVG, multi-panel) | **matplotlib** | [references/matplotlib.md](references/matplotlib.md) |
| interactive / dashboard (hover, zoom, HTML) | **plotly** | [references/plotly.md](references/plotly.md) |

Each reference carries the single Polars→library conversion boundary, the house conventions, the
one gotcha that bites, and **verified, runnable templates** for the common families (line, bar /
top-N, histogram, scatter/density, small multiples) plus the long-tail (stacked area, box/violin,
ECDF, slope, lollipop, choropleth, Sankey) in whichever library is idiomatic — choropleth and Sankey
live in plotly. A mark with no template in your chosen library is still fully specified by the Phase-1
encoding map; render it with that library's standard idioms.

## House idiom

**Do all aggregation and reshaping lazily in Polars** (`.group_by().agg()`, `.filter()`, top-N +
"other"); materialize only the small, plot-ready frame at the render boundary. Keep transform
separate from render. Reproducible seeds for any jitter/sampling. This is also what keeps Altair
under its 5000-row `MaxRowsError` cap — pre-aggregate rather than embedding raw rows.

## Anti-patterns (the recommender refuses these — see chart-selection.md)

No pie above ~6 categories (compare angles poorly → bar); never 3D; no dual y-axes without both
clearly labelled (prefer stacked panels); no spaghetti multi-line (→ small multiples); no raw
scatter at large n (→ 2D density/hexbin); bars start at zero; sort by value; colorblind-safe palette,
viridis for sequential.

## Stack notes

- The skill is **markdown** — Phase 0/1 need only `polars` (and `recommend.py`, Python ≥ 3.9).
- Phase 2 needs whichever library you route to: `altair` (+ `vl-convert-python` for static export,
  `vegafusion` for large raw data), `matplotlib`, or `plotly` (+ `kaleido` for static export). All
  three accept Polars frames either directly (Altair, plotly-express via narwhals) or via
  `.to_numpy()` (matplotlib).
- Verified on Polars 1.42, Altair 6.2, matplotlib 3.11, plotly 6.8.

## Attribution

Original work (MIT). Cites standard visualization literature by author-year only (Cleveland & McGill
1984; Tufte 1983; Munzner 2014; Wilke 2019; Satyanarayan et al. 2017) — summarized, never reproduced.
See the repo [`NOTICE`](../NOTICE).
