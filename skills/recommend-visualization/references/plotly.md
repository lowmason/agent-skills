# plotly — interactive / dashboard

Reach for plotly when interactivity is the point: hover tooltips, zoom/pan, selection, and HTML
embedding in a dashboard or notebook. Verified on **plotly 6.8, Polars 1.42, narwhals 2.x**.

## The Polars → plotly boundary (one rule)

**`plotly.express` accepts a Polars frame directly** in current plotly (≥ ~5.25, and all of 6.x) —
it speaks narwhals. No conversion at the boundary:

```python
import plotly.express as px
fig = px.line(region_month, x='month', y='employment', color='region')
```

> **Gotcha (the brief's was stale).** Older guidance says "plotly express is pandas-oriented, call
> `.to_pandas()` first." That's no longer the default — `px` reads Polars natively now. Keep
> `.to_pandas()` only as a *fallback* for an old plotly version, or for a niche `px` feature that
> still requires a pandas index. For `graph_objects`, extract columns with `.to_list()`.

Still do the aggregation in Polars and pass `px` the plot-ready frame — `px` will gladly aggregate,
but Polars is faster and keeps transform separate from render.

## express vs. graph_objects

- **`plotly.express`** — concise, the default. One call maps columns to channels (`color=`, `facet_col=`,
  `size=`, `hover_data=`).
- **`graph_objects` (`go`)** — full control (mixed trace types, custom hovertemplates, secondary
  axes) and the home for marks `px` lacks (Sankey). Feed it arrays via `.to_list()` / `.to_numpy()`.

## Templates

```python
import plotly.express as px
import plotly.graph_objects as go

# Ranking: top-N horizontal bar (`ranked` = top-N + 'other', built in Polars)
px.bar(ranked.sort('employment'), x='employment', y='industry', orientation='h')

# Distribution: histogram (px bins for you; carry a log flag with log_x=True)
px.histogram(wages, x='wage', nbins=40)            # px.histogram(wages, x='wage', log_x=True) if skewed

# Small multiples: facet a line chart
px.line(ind_month.sort('month'), x='month', y='employment', facet_col='industry', facet_col_wrap=6)

# Correlation at large n: density heatmap straight from raw rows
# (plotly bins internally — there is NO MaxRows limit like Altair's)
px.density_heatmap(big, x='hours', y='pay', nbinsx=40, nbinsy=40)

# Correlation at very large n: Scattergl (WebGL) renders millions of points the SVG path can't
go.Figure(go.Scattergl(x=big['hours'].to_list(), y=big['pay'].to_list(),
                       mode='markers', marker=dict(opacity=0.2)))
```

## More chart families

```python
# Composition over time: stacked area
px.area(ind_month, x='month', y='employment', color='industry')

# Distribution across groups: box / violin
px.violin(panel.drop_nulls('employment'), x='region', y='employment')   # or px.box(...)

# ECDF (px has it natively)
px.ecdf(wages, x='wage')

# Geographic: choropleth — self-contained for US states / ISO countries (no external geojson)
px.choropleth(state_rates, locations='state', locationmode='USA-states', color='rate', scope='usa')
# arbitrary regions: px.choropleth(df, geojson=geo, featureidkey='properties.id', locations='id', color='val')

# Flow: Sankey (graph_objects — px has no Sankey). Encode the edge list as index arrays.
labels = nodes['name'].to_list()
idx = {n: i for i, n in enumerate(labels)}
go.Figure(go.Sankey(
    node=dict(label=labels),
    link=dict(source=[idx[s] for s in edges['source'].to_list()],
              target=[idx[t] for t in edges['target'].to_list()],
              value=edges['value'].to_list())))
```

## House conventions & saving

Set a template once (`fig.update_layout(template='plotly_white')`) for a clean, low-ink frame; title
axes explicitly. **Interactive HTML is dependency-free:** `fig.write_html('fig.html')` (or
`fig.to_html(full_html=False)` to embed in a page). **Static export (`.png`/`.svg`/`.pdf`) needs
Kaleido** (`pip install kaleido`), then `fig.write_image('fig.png', scale=2)` — if you only need a
static image, matplotlib is the simpler tool.
