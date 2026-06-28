# matplotlib — publication / static

Reach for matplotlib when the figure is the deliverable: a report or methodology figure, a
multi-panel layout, precise control, and vector export (PDF/SVG/EPS). Verified on **matplotlib 3.11,
Polars 1.42**.

## The Polars → matplotlib boundary (one rule)

matplotlib speaks NumPy. **Convert at the render boundary with `.to_numpy()`** (whole frame) or
`df['col'].to_numpy()` (one column); reach for `.to_pandas()` only when handing the frame to
**seaborn**. Do all aggregation in Polars first — matplotlib won't group for you.

```python
import polars as pl
import matplotlib.pyplot as plt

agg = (panel.lazy().group_by('region', 'month')
       .agg(pl.col('employment').mean().alias('employment')).sort('month').collect())
x = agg.filter(pl.col('region') == 'NE')['month'].to_numpy()   # datetime64 — matplotlib dates work
```

## House conventions

Set a style block once, then build figures explicitly (`fig, ax = plt.subplots()` — never the
implicit `pyplot` state machine in a script). Use a reproducible seed for any jitter/sample.

```python
plt.rcParams.update({
    'figure.figsize': (7, 4.3), 'figure.dpi': 120, 'savefig.dpi': 300,
    'savefig.bbox': 'tight', 'font.size': 11, 'axes.titlesize': 13,
    'axes.spines.top': False, 'axes.spines.right': False,   # data-ink: drop the top/right spines
    'axes.grid': True, 'grid.alpha': 0.3,
})
```

## The gotcha: it's imperative — you draw each group yourself

There is no `color='region'`; you **loop** and plot one series per group, then label directly (a
legend is the fallback). This is verbose but total control.

```python
fig, ax = plt.subplots()
for reg in agg['region'].unique().to_list():
    d = agg.filter(pl.col('region') == reg).sort('month')
    ax.plot(d['month'].to_numpy(), d['employment'].to_numpy(), label=reg)
ax.set_ylabel('employment'); ax.legend(title='region', frameon=False)
```

## Templates

```python
# Ranking: top-N horizontal bar (sort ascending so the largest lands on top)
r = ranked.sort('employment')                       # `ranked` = top-N + 'other', built in Polars
fig, ax = plt.subplots()
ax.barh(r['industry'].to_list(), r['employment'].to_numpy())
ax.set_xlabel('employment')

# Distribution: histogram
fig, ax = plt.subplots()
ax.hist(wages['wage'].to_numpy(), bins=40)
ax.set_xlabel('wage'); ax.set_ylabel('count')
# skewed? ax.set_xscale('log') — carry the log-scale flag from the recommendation onto the axis

# Correlation at large n: hexbin (the matplotlib answer to scatter overplotting)
fig, ax = plt.subplots()
hb = ax.hexbin(big['hours'].to_numpy(), big['pay'].to_numpy(), gridsize=40, cmap='viridis')
fig.colorbar(hb, label='count')

# Small multiples: a grid of axes sharing scales
fig, axes = plt.subplots(4, 6, figsize=(12, 8), sharex=True, sharey=True)
for ax, ind in zip(axes.flat, sorted(panel['industry'].unique().to_list())):
    d = ind_month.filter(pl.col('industry') == ind).sort('month')
    ax.plot(d['month'].to_numpy(), d['employment'].to_numpy()); ax.set_title(ind, fontsize=8)
fig.tight_layout()
```

## More chart families

```python
import numpy as np

# Composition over time: stacked area (one row per period, one y-series per part)
wide = ind_month.pivot('industry', index='month', values='employment').sort('month')
ys = [wide[c].to_numpy() for c in wide.columns if c != 'month']
fig, ax = plt.subplots(); ax.stackplot(wide['month'].to_numpy(), *ys, labels=wide.columns[1:])

# Distribution across groups: box / violin (one array per group)
groups = [panel.filter(pl.col('region') == r)['employment'].drop_nulls().to_numpy()
          for r in panel['region'].unique().to_list()]
fig, ax = plt.subplots(); ax.violinplot(groups)        # or ax.boxplot(groups)

# ECDF: sort, then step
v = np.sort(wages['wage'].to_numpy()); y = np.arange(1, v.size + 1) / v.size
fig, ax = plt.subplots(); ax.step(v, y, where='post'); ax.set_ylabel('cumulative share')

# Lollipop: a higher-data-ink ranking (stems + dots)
r = ranked.sort('employment')
fig, ax = plt.subplots()
ax.hlines(y=r['industry'].to_list(), xmin=0, xmax=r['employment'].to_numpy())
ax.plot(r['employment'].to_numpy(), r['industry'].to_list(), 'o')
```

A **choropleth** is a `geopandas` job (`gdf.plot(column=...)`); a **slope** graph is two x-positions
with a line per entity (loop `ax.plot([0, 1], [first, last])`). **Sankey** is awkward in matplotlib —
use [plotly](plotly.md).

## Saving

Vector for publication, raster for the web: `fig.savefig('fig.pdf')`, `.svg`, `.eps`, or
`.png` (`dpi=300`). `savefig.bbox='tight'` (in the rcParams above) trims the margins. Close figures
in loops (`plt.close(fig)`) so a batch doesn't leak memory.
