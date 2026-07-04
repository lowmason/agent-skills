# Chart selection (router) — intent × data-signal → chart

The runtime entry point. **Name the intent → read the data signal off the profile → match the row →
take the primary chart and its encoding map.** Off-the-shelf advice maps *intent → chart*; this maps
*(intent × signal) → chart*, because the same intent wants a different view once the data's
cardinality, row count, skew, or panel shape is known. The logic here is mirrored in
[`scripts/recommend.py`](../scripts/recommend.py) — change one, change the other
([`scripts/test_recommend.py`](../scripts/test_recommend.py) asserts they agree: a contract test
drives `recommend()` over every intent and checks each emitted chart name and threshold against this
file).

Ground every choice in [encoding-principles.md](encoding-principles.md): **position > length >
angle/area > color**. When two charts both fit, prefer the one that puts the value being judged on
the higher-ranked channel.

## Phase 0 — the handoff signals (what to read, and what to compute)

Key the recommendation off what `explore-data`'s `profile.py --json` actually emits — don't invent
fields:

| Signal | From the profile | Drives |
|--------|------------------|--------|
| **kind** (quantitative / temporal / categorical / boolean) | `columns[].dtype` (a **string**: `"Int64"`, `"Date"`, `"Categorical"`) | which channel a field can occupy |
| **cardinality** | `columns[].n_unique` | bar vs. horizontal-bar vs. top-N vs. slope |
| **row count** | `n_rows` | scatter vs. density (overplotting) |
| **null rate** | `columns[].null_pct` | a missingness caveat, never a silent drop |
| **panel / time structure** | the series field's `columns[].n_unique` (with `dates{}` / `panel_balance.n_entities` for context) | single line vs. many-series small multiples |

Four signals the **profile JSON omits** (it prints quartiles but doesn't store them) — compute them
from the raw frame, exactly as `recommend-probabilistic-model`'s `characterize.py` adds modeling
signals. They live in `recommend.py` as `skewness`, `outlier_ratio`, `top_n_coverage`,
`overplot_risk`:

- **skew / outliers** → log-scale flag; histogram vs. box vs. ECDF.
- **modality** → violin/ECDF over a box (a box hides bimodality).
- **top-N coverage** → does the top-k cover most of the mass? then top-N + an "other" bucket.
- **overplot risk** = f(`n_rows`) → raw points vs. opacity vs. 2D density.

## Thresholds (mirror `recommend.py` constants)

| Constant | Value | Meaning |
|----------|------:|---------|
| `LOW_CARD_MAX` | 7 | ≤ this many categories: vertical bar reads cleanly |
| `BAR_CARD_MAX` | 15 | ≤ this many: one bar per category (horizontal for label room); above → top-N |
| `PIE_MAX` | 6 | never a pie above this many slices |
| `OVERPLOT_MEDIUM` | 1000 | scatter starts to clot → opacity/size |
| `OVERPLOT_HIGH` | 5000 | scatter is a blob → 2D density/hexbin (also where Altair's `MaxRowsError` fires) |
| `MANY_SERIES_MAX` | 7 | > this many series → small multiples, not a spaghetti multi-line |
| `SKEW_LOG` | 2.0 | \|skew\| above this → flag a log scale |

## The matrix

Each row: the signal that decides the choice → **primary** chart → alternatives → the encoding
(field → channel). "C" = a categorical field, "Q" = quantitative, "T" = temporal.

### trend-over-time  (need a temporal axis + a quantitative measure)
| Signal | Primary | Alternatives | Encoding |
|--------|---------|--------------|----------|
| one series | **line** | area (if volume reading matters, ≥0) | x=T, y=Q |
| ≤ 7 series (a C) | **line, one per series, direct-labelled** | small multiples | x=T, y=Q, color=C |
| > 7 series | **small multiples (facet)** | colored multi-line (occludes) | x=T, y=Q, facet=C |

*Composition over time (a stacked area) is a part-to-whole question — route it through the
`part-to-whole` intent ("over time" row), not `trend-over-time`.*

### comparison  (a categorical dimension vs. a quantitative measure)
| Signal | Primary | Alternatives | Encoding |
|--------|---------|--------------|----------|
| ≤ 7 categories | **vertical bar** | grouped bar (+2nd C as color) | x=C, y=Q |
| 8–15 categories | **horizontal bar, sorted** | lollipop | y=C, x=Q |
| > 15 categories | **top-N horizontal bar + "other"** | lollipop | y=C, x=Q |
| two periods, many entities | **slope graph** | dumbbell | x=period, y=Q, color/detail=entity |

### ranking  (order is the message)
| Signal | Primary | Alternatives | Encoding |
|--------|---------|--------------|----------|
| ≤ 15 items | **sorted horizontal bar** | lollipop | y=C, x=Q, sort desc |
| > 15 items | **top-N horizontal bar + "other"** | lollipop | y=C, x=Q, top-N + other |
| change in rank across 2 periods | **slope / dumbbell** | bump chart | x=period, y=Q, color=entity |

### distribution  (shape of one quantitative)
| Signal | Primary | Alternatives | Encoding |
|--------|---------|--------------|----------|
| roughly symmetric | **histogram** | ECDF; box | x=Q (binned) |
| skewed / heavy-tailed (\|skew\|>2) | **histogram on a log scale** | ECDF; box | x=Q (log) |
| across a grouping C (≤ 7 groups) | **faceted histograms** | violin; pooled histogram; ECDF | x=Q, facet=C |
| compare many groups (> 7) | **violin** | box (hides modality); faceted histograms | x=C, y=Q |

### correlation / relationship  (two quantitative)
| Signal | Primary | Alternatives | Encoding |
|--------|---------|--------------|----------|
| n < 1000 | **scatter** | + trend line | x=Q, y=Q (color=C) |
| 1000 ≤ n < 5000 | **scatter, low opacity + small marks** | 2D density | x=Q, y=Q |
| n ≥ 5000 | **2D density / hexbin** | sampled scatter | x=Q, y=Q, color=count |

### part-to-whole  (parts of one total)
| Signal | Primary | Alternatives | Encoding |
|--------|---------|--------------|----------|
| ≤ 7 parts | **bar of shares (sorted)** | pie *(only ≤ 6)*; 100%-stacked bar | x=C, y=Q(%) |
| 8–15 parts | **horizontal bar of shares** | 100%-stacked bar | y=C, x=Q(%) |
| > 15 parts | **top-N bar + "other"** | treemap | y=C, x=Q(%) |
| over time | **stacked area** | 100%-stacked area | x=T, y=Q, color=C |

### geographic  (a profile can't see geometry — name the family, state what's needed)
| Signal | Primary | Alternatives | Encoding | Needs |
|--------|---------|--------------|----------|-------|
| region-level magnitude | **choropleth** | cartogram | shape=region, color=Q | region boundaries (GeoJSON/TopoJSON) keyed to the id |
| point events / magnitude | **proportional-symbol map** | dot density | lon, lat, size=Q | lat-lon coordinates |

Map a **rate**, not a raw count — choropleths bias toward large/low-density areas.

### flow  (movement between nodes — needs an edge list a flat profile won't surface)
| Signal | Primary | Alternatives | Encoding | Needs |
|--------|---------|--------------|----------|-------|
| flows with magnitude, few stages | **Sankey** | alluvial | source, target, value | source→target pairs + magnitude |
| many-to-many among one node set | **chord** | arc diagram | source, target, value | a square flow matrix |

## Anti-patterns (the recommender refuses these — say why)

- **Pie above ~6 slices.** Humans compare angle/area poorly; a sorted bar puts the same data on
  position. The recommender never emits a pie above `PIE_MAX`, and prefers a bar even below it.
- **Spaghetti multi-line.** More than ~7 lines on one axis occlude into noise → small multiples.
- **Raw scatter at large n.** Overplotting hides density and exaggerates the extremes → 2D density /
  hexbin / opacity. (At ≥ 5000 rows you'll also hit Altair's `MaxRowsError` — see [altair.md](altair.md).)
- **3D charts.** Perspective distorts position and length, the two channels you most want to read
  accurately. There is essentially no 2D-data case where 3D helps.
- **Dual y-axes.** Two scales on one frame invite spurious "correlation" and arbitrary alignment;
  use two stacked panels sharing an x-axis, or index both series to a common base. If unavoidable,
  label both axes unambiguously.
- **Stacked bars with many series.** Only the bottom segment sits on a common baseline; the rest
  float and can't be compared → small multiples or a line per series.
- **A truncated bar baseline.** Bars encode by length; cutting the axis lies about ratios. (A line
  chart *may* zoom the y-range — it encodes position, not length.)
- **Rainbow/jet color ramps & a non-zero sequential scale.** Use a perceptually-uniform ramp
  (viridis) and a colorblind-safe categorical palette — see [encoding-principles.md](encoding-principles.md).

## Canonical names (the contract with `recommend.py`)

The matrix above uses readable names; [`scripts/recommend.py`](../scripts/recommend.py) emits these
canonical identifiers (the `chart` field). They are the shared vocabulary the skill's tests check —
[`test_recommend.py`](../scripts/test_recommend.py) drives `recommend()` over every intent and
asserts each emitted name appears here — to keep doc and code in lockstep:

`line` · `area` · `small_multiples_line` · `bar` · `horizontal_bar` · `horizontal_bar_top_n` ·
`lollipop` · `slope` · `dumbbell` · `scatter` · `scatter_with_trend` · `density_heatmap` · `hexbin` ·
`histogram` · `ecdf` · `box` · `violin` · `faceted_histogram` · `stacked_area` · `treemap` · `pie` ·
`choropleth` · `symbol_map` · `sankey` · `chord`.

## Output of this phase

Ranked **chart candidates**, each with a one-line rationale and an **encoding map** (field →
channel) — the near-spec that [altair.md](altair.md) / [matplotlib.md](matplotlib.md) /
[plotly.md](plotly.md) turn into code. Carry any caveat (log scale, missingness, sampling) into the
figure; don't drop it.
