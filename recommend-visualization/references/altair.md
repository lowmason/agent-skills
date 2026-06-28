# Altair — declarative / exploratory (the default)

Altair is the default for exploration and for anything declarative: the encoding map from
[chart-selection.md](chart-selection.md) is almost a one-to-one translation into a Vega-Lite spec
(mark + channels). Verified on **Altair 6.2, Polars 1.42, narwhals 2.x**.

## The Polars → Altair boundary (one rule)

**Aggregate and reshape lazily in Polars; materialize the small, plot-ready frame; hand it to
`alt.Chart`.** Altair consumes a Polars frame *directly* (via narwhals) — no `.to_pandas()`. Keep
transform separate from render: the chart spec should only encode columns that already exist.

```python
import polars as pl
import altair as alt

# transform (Polars, lazy) — collect only the plot-ready frame
region_month = (
    panel.lazy()
    .group_by('region', 'month')
    .agg(pl.col('employment').mean().alias('employment'))
    .sort('month')
    .collect()
)

# render (Altair reads the Polars frame as-is)
alt.Chart(region_month).mark_line().encode(
    x='month:T', y='employment:Q', color='region:N',
)
```

**Channel type suffixes carry the field kind** straight from the recommendation: `:Q` quantitative,
`:N` nominal/categorical, `:O` ordinal, `:T` temporal. Get them right or Altair mis-infers the scale.

**Fast path:** Polars' `.plot` namespace is Altair-backed and covers the four common marks —
`df.plot.line(x=..., y=...)`, `.bar`, `.point`, `.scatter`. Use it for a quick look; drop to
`alt.Chart(df)` the moment you need a mark it doesn't expose (histogram, rect/heatmap, facet) or
fine control.

## The gotcha: `MaxRowsError` at 5000 rows (still true in Altair 6)

Altair embeds the data in the spec, so it refuses frames over 5000 rows. **This fires at exactly the
overplotting threshold** (`OVERPLOT_HIGH`), which is the hint: by the time you'd hit it, you should be
plotting a *summary*, not raw rows. Three escapes, in order of preference:

1. **Pre-aggregate in Polars** (the house idiom) — bin, group, or sample to a plot-ready frame.
   A 2D density never needs raw rows:

   ```python
   # 2D density as a Polars-binned grid -> mark_rect (stays far under the row cap)
   NX = NY = 40
   hl, hh = big['hours'].min(), big['hours'].max()
   pl_, ph = big['pay'].min(), big['pay'].max()
   density = (
       big.lazy()
       .with_columns(
           ((pl.col('hours') - hl) / (hh - hl) * (NX - 1)).round().cast(pl.Int32).alias('hx'),
           ((pl.col('pay')   - pl_) / (ph - pl_) * (NY - 1)).round().cast(pl.Int32).alias('hy'),
       )
       .group_by('hx', 'hy').agg(pl.len().alias('count'))
       .collect()
   )
   alt.Chart(density).mark_rect().encode(x='hx:O', y='hy:O', color='count:Q')
   ```

2. **Lift the cap** when a mark genuinely needs the raw rows (boxplot, violin, raw scatter):
   `alt.data_transformers.enable('default', max_rows=None)`. You can't pre-aggregate a boxplot —
   it computes its quartiles from the rows — so this (or option 3) is the only path past 5000.
3. **VegaFusion** for large raw data with server-side transforms: `alt.data_transformers.enable('vegafusion')`
   (needs `pip install vegafusion`). Altair then pushes binning/aggregation to Rust and the cap lifts.

## Templates

```python
# Ranking: top-N horizontal bar (pre-aggregate + 'other' bucket in Polars, then sort on the channel)
TOP_N = 15
totals = panel.group_by('industry').agg(pl.col('employment').sum().alias('employment')) \
              .sort('employment', descending=True)
ranked = pl.concat([
    totals.head(TOP_N),
    pl.DataFrame({'industry': ['other'], 'employment': [totals['employment'][TOP_N:].sum()]}),
])
alt.Chart(ranked).mark_bar().encode(x='employment:Q', y=alt.Y('industry:N', sort='-x'))

# Distribution: histogram (binning is an Altair encoding transform; raw rows < 5000)
alt.Chart(wages).mark_bar().encode(alt.X('wage:Q', bin=alt.Bin(maxbins=40)), y='count()')

# Small multiples: one panel per series — the answer for > 7 series
ind_month = panel.group_by('industry', 'month').agg(pl.col('employment').mean().alias('employment'))
alt.Chart(ind_month).mark_line().encode(x='month:T', y='employment:Q') \
   .properties(width=120, height=80).facet('industry:N', columns=6)
```

## More chart families

```python
# Composition over time: stacked area (parts sum to the whole each period)
alt.Chart(ind_month).mark_area().encode(x='month:T', y='employment:Q', color='industry:N')

# Distribution across groups: box (needs RAW rows -> lift the cap above 5000, see the gotcha)
alt.data_transformers.enable('default', max_rows=None)
alt.Chart(panel.select('region', 'employment')).mark_boxplot().encode(x='region:N', y='employment:Q')

# ECDF: exact quantiles, bin-width-free
alt.Chart(wages).transform_window(ecdf='cume_dist()', sort=[{'field': 'wage'}]) \
   .mark_line(interpolate='step-after').encode(x='wage:Q', y='ecdf:Q')

# Slope: two periods, one line per entity (unpivot to long form in Polars first)
alt.Chart(slope_long).mark_line(point=True).encode(
    x='period:O', y='employment:Q', color='industry:N', detail='industry:N')
```

For a **choropleth**, use `mark_geoshape()` with a topojson layer (e.g. `vega_datasets`' `us_10m`)
keyed to your region id — Altair has the mark, but it needs the geometry the profile can't supply.
**Sankey/chord** have no native Altair mark — use [plotly](plotly.md) (`go.Sankey`).

## Saving

`chart.save('fig.html')` is dependency-free (the HTML embeds the JS). **Static export
(`.png` / `.svg` / `.pdf`) needs `vl-convert-python`** (`pip install vl-convert-python`), then
`chart.save('fig.svg')`. For a quick interactive look, `chart.show()` opens a browser tab.
