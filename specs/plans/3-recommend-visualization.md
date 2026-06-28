# Plan 3 — `recommend-visualization` skill

Execution plan for the kickoff brief (the brief is the spec; not duplicated here). Sibling of
`recommend-probabilistic-model`: one recommends a *model*, this recommends a *view* — and, unlike
its sibling, carries through to code, because for a chart the recommendation (mark + encodings keyed
to field types) is nearly the spec.

## Handoff contract (Phase 0) — keyed to what `explore-data/scripts/profile.py` actually emits

`profile.py --json` writes: `n_rows`, `n_cols`, `columns[]` = `{column, dtype(str), null_pct,
n_unique, example}`, `dates{}`, `flags[]`, and optional `duplicate_check` / `vintage_check` /
`panel_balance{n_entities,n_periods,...}`. **`dtype` is a string** (`"Int64"`, `"Date"`,
`"Categorical"`), so dtype→kind parsing lives in a thin adapter, never in the pure core.

Signals the profile JSON does **not** carry (quartiles are printed but omitted from JSON) and that
`recommend.py` computes from the raw frame — the `characterize.py` analog: **skew** (→ log scale,
hist vs box/violin), **outlier ratio** (→ log scale), **top-N coverage** (→ top-N + "other"),
**overplot risk** = f(n_rows) (→ hexbin/density vs raw scatter).

## Phase 1 — recommend  (intent × data-signal → chart). The differentiator.

Intents: `trend-over-time`, `comparison`, `distribution`, `correlation`/`relationship`,
`part-to-whole`, `ranking`, `geographic`, `flow`. Condition each on profile signals
(cardinality, n_rows, skew/outliers, panel structure, null rates).

`geographic` / `flow`: a standard profile can't surface lat/lon or source→target. Recommend the
chart family and **state the required encoding** rather than fabricating a signal — don't drop them,
don't over-build.

## Phase 2 — code (route library by purpose), informed by probes on installed versions

- polars 1.42 `.plot` → only `bar/line/point/scatter`, Altair-backed (fast path); else `alt.Chart(df)`.
- Altair 6.2.2: `alt.Chart(polars_df)` direct (narwhals); **MaxRowsError still at 5000** — pre-aggregate
  in Polars (house idiom) / `enable("default", max_rows=None)` / `enable("vegafusion")` (2.0.3 present).
- plotly 6.8 express **accepts Polars directly** (narwhals) — `.to_pandas()` is the *legacy* fallback,
  not the default. `graph_objects` via `df["c"].to_list()`.
- matplotlib 3.11: `.to_numpy()` boundary; rcParams block; PDF/SVG/EPS export.

## `recommend.py` API (pure core + adapter + signal helpers)

```python
KIND = quantitative | temporal | categorical | boolean
@dataclass Field(name, kind, n_unique=None, null_pct=0.0, skew=None, outlier_ratio=None)
@dataclass ChartCandidate(chart, mark, encodings:{channel->field}, rationale, score,
                          transform=None, caveats=[])     # encodings = the spec Phase 2 consumes
# signal helpers (pl.Series/DataFrame -> signal): skewness, outlier_ratio, top_n_coverage, overplot_risk
# adapter: kind_from_dtype(str)->KIND ; fields_from_profile(dict)->[Field]
def recommend(intent, fields:[Field], n_rows, *, top_n=15) -> [ChartCandidate]  # ranked
```

Thresholds (module constants, documented): LOW_CARD_MAX=7, BAR_CARD_MAX=15, PIE_MAX=6,
OVERPLOT_MEDIUM=1000, OVERPLOT_HIGH=5000 (ties to Altair's cap), MANY_SERIES_MAX=7,
SKEW_LOG=2.0.

## Files

```
recommend-visualization/
  SKILL.md  README.md
  references/{chart-selection,encoding-principles,altair,matplotlib,plotly}.md
  scripts/{recommend.py,test_recommend.py}
```

## Build / verify

- TDD: write discriminating golden cases in `test_recommend.py` first (each fails against a
  plausible-wrong mapping: scatter-on-large-n, pie-on-high-card, spaghetti-on-many-series), then
  implement `recommend.py` green.
- End-to-end (done-when): sample frame → `profile.py --json` → `recommend.py` → run the recommended
  chart in **all three** libraries via `uv run`.
- Doc↔code contract lives in the skill's own `test_recommend.py` (bidirectional canonical-name +
  threshold checks against chart-selection.md). `build/` stays rpm-only per CLAUDE.md — not extended.
- Python style per CLAUDE.md: single quotes, run via `uv run --python 3.13`.
- `verify_citations.py` passes (no PML-pattern strings introduced); citations are light inline
  author-year (Cleveland & McGill 1984; Wilke 2019; Munzner 2014; Satyanarayan et al. 2017; Tufte 1983).

## Integration (order matters — symlink target only exists post-merge)

1. `explore-data/SKILL.md`: one-line pointer (after profiling → hand off to recommend-visualization).
2. README "Mine" table row; NOTICE originals list.
3. Verify all checks. 4. Merge branch → main. 5. Symlink from `~/Projects/agent-skills`. 6. Remove worktree.
```
