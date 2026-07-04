#!/usr/bin/env python3
"""Profile + intent -> ranked chart candidates, each carrying its encoding map.

The sibling of recommend-probabilistic-model's recommender: that one maps (task x data-signal) to a
*model*; this one maps (intent x data-signal) to a *view*. The differentiator over an off-the-shelf
intent->chart lookup is that every recommendation is conditioned on the data's signals — cardinality,
row count, skew/outliers, panel structure, null rates — and ships the field->channel **encoding map**,
which is nearly the Vega-Lite/matplotlib spec the Phase-2 code consumes.

Architecture (so the logic stays unit-testable):
  * pure core: `recommend(intent, fields, n_rows)` conditions only on normalized `kind`s + signals
    and returns ranked `ChartCandidate`s. No Polars, no I/O — golden-testable.
  * adapter: `fields_from_profile` / `kind_from_dtype` parse explore-data's profile JSON, whose
    `dtype` is a STRING ('Int64', 'Date', 'Categorical'), into normalized kinds.
  * signal helpers: `skewness`, `outlier_ratio`, `top_n_coverage`, `overplot_risk` — the signals
    profile.py prints but does NOT put in its JSON (the characterize.py analog).

Handoff contract — fields keyed off what explore-data/scripts/profile.py --json actually emits:
  n_rows, columns[]={column, dtype(str), null_pct, n_unique, example}, dates{}, flags[], and
  optional duplicate_check / vintage_check / panel_balance.

Usage:
    python recommend.py data.parquet --profile profile.json --intent correlation
    python recommend.py data.csv --intent distribution --fields wage
    python recommend.py --profile profile.json --intent ranking --fields industry,emp --json out.json
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

# --- thresholds (documented; mirror chart-selection.md) ------------------------------------------
LOW_CARD_MAX = 7        # <= this many categories: vertical bar reads cleanly (also the pie ceiling-ish)
BAR_CARD_MAX = 15       # <= this many: one bar per category (horizontal for labels); above -> top-N
PIE_MAX = 6             # never a pie above this many slices (angle/area compare poorly)
OVERPLOT_MEDIUM = 1000  # scatter starts to clot: reduce opacity/size
OVERPLOT_HIGH = 5000    # scatter is a blob: 2D density/hexbin (also where Altair's MaxRowsError fires)
MANY_SERIES_MAX = 7     # > this many series/groups: small multiples, not a spaghetti multi-line
SKEW_LOG = 2.0          # |skew| above this: flag a log scale
MISSING_CAVEAT_PCT = 5.0  # a used field this % null gets a surface-the-missingness caveat

VALID_INTENTS = {
    'trend-over-time', 'comparison', 'distribution', 'correlation',
    'part-to-whole', 'ranking', 'geographic', 'flow',
}
INTENT_ALIASES = {'relationship': 'correlation', 'trend': 'trend-over-time'}

QUANTITATIVE, TEMPORAL, CATEGORICAL, BOOLEAN = 'quantitative', 'temporal', 'categorical', 'boolean'


@dataclass
class Field:
    """A column reduced to what a chart choice needs: a normalized kind + the signals that route it."""
    name: str
    kind: str                       # quantitative | temporal | categorical | boolean
    n_unique: int | None = None
    null_pct: float = 0.0
    skew: float | None = None       # distribution-shape signal (profile JSON omits it)
    outlier_ratio: float | None = None


@dataclass
class ChartCandidate:
    chart: str                      # canonical name, e.g. 'horizontal_bar_top_n'
    mark: str                       # vega-lite-ish mark: bar/line/point/area/boxplot/rect/arc/geoshape/link
    encodings: dict[str, str]       # channel -> field name: the spec Phase 2 consumes
    rationale: str                  # one line: WHY, tied to the signal
    score: float                    # 1.0 = primary; alternatives lower
    transform: str | None = None    # Polars-side reshape the chart needs, e.g. 'top_n(x,15,other=True)'
    caveats: list[str] = field(default_factory=list)


def CC(chart, mark, encodings, rationale, score, transform=None, caveats=None):
    return ChartCandidate(chart, mark, encodings, rationale, score, transform, list(caveats or []))


# --- signal helpers (the characterize.py analog: what the profile JSON leaves out) ----------------

def _to_float(s):
    import polars as pl
    return s.drop_nulls().cast(pl.Float64)


def skewness(s) -> float | None:
    """Fisher-Pearson (moment) skewness. > 0 right-tailed, < 0 left-tailed; |skew| > ~2 -> log scale."""
    s = _to_float(s)
    if s.len() < 3:
        return None
    m, sd = s.mean(), s.std(ddof=0)
    if not sd:
        return 0.0
    return round(float((((s - m) / sd) ** 3).mean()), 3)


def outlier_ratio(s) -> float | None:
    """max / p75 — a cheap heavy-tail flag (a max orders of magnitude above p75 hints at a log scale
    or a leaked aggregation level, per explore-data's outlier flag)."""
    s = _to_float(s)
    if s.len() < 2:
        return None
    p75 = s.quantile(0.75, interpolation='linear')
    if not p75:
        return None
    return round(float(s.max() / p75), 3)


def top_n_coverage(s, n: int) -> float | None:
    """Share of rows falling in the n most frequent categories — high coverage justifies a top-N
    chart with an 'other' bucket instead of plotting every category."""
    s = s.drop_nulls()
    total = s.len()
    if total == 0:
        return None
    vc = s.value_counts(sort=True)
    counts = vc[vc.columns[-1]].head(n)     # last column is the count
    return round(float(counts.sum() / total), 4)


def overplot_risk(n_rows: int) -> str:
    """Row count -> scatter overplotting risk: low (raw points) / medium (opacity) / high (2D density)."""
    if n_rows >= OVERPLOT_HIGH:
        return 'high'
    if n_rows >= OVERPLOT_MEDIUM:
        return 'medium'
    return 'low'


# --- adapter: explore-data profile JSON (dtype is a STRING) -> normalized kinds -------------------

def kind_from_dtype(dtype_str: str) -> str:
    """Map a Polars dtype rendered as a string ('Int64', "Datetime(time_unit='us', ...)", ...) to a
    normalized channel kind. The profile JSON stores str(dtype), not a dtype object."""
    d = dtype_str.strip().lower()
    if d.startswith(('date', 'datetime', 'time', 'duration')):
        return TEMPORAL
    if d.startswith('bool'):
        return BOOLEAN
    if d.startswith(('int', 'uint', 'float', 'decimal')):
        return QUANTITATIVE
    return CATEGORICAL          # string / categorical / enum / list / struct -> treat as categorical


def fields_from_profile(profile: dict) -> list[Field]:
    """Build Fields from an explore-data profile dict (the --json output of profile.py)."""
    out: list[Field] = []
    for col in profile.get('columns', []):
        out.append(Field(
            name=col['column'],
            kind=kind_from_dtype(col['dtype']),
            n_unique=col.get('n_unique'),
            null_pct=float(col.get('null_pct', 0.0) or 0.0),
        ))
    return out


def fields_from_frame(df) -> list[Field]:
    """Build Fields directly from a Polars frame when no profile JSON is on hand."""
    n = df.height
    return [
        Field(
            name=c,
            kind=kind_from_dtype(str(df.schema[c])),
            n_unique=df[c].n_unique(),
            null_pct=round(100 * df[c].null_count() / n, 2) if n else 0.0,
        )
        for c in df.columns
    ]


# --- pure core ------------------------------------------------------------------------------------

def _by_kind(fields: list[Field], kind: str) -> list[Field]:
    return [f for f in fields if f.kind == kind]


def _two_period(fields: list[Field]):
    """Detect a two-period comparison: a temporal/categorical field with exactly 2 distinct values,
    alongside a higher-cardinality categorical entity and a quantitative value -> slope/dumbbell."""
    period = next((f for f in fields if f.kind in (TEMPORAL, CATEGORICAL) and f.n_unique == 2), None)
    if not period:
        return None
    entity = next((f for f in _by_kind(fields, CATEGORICAL) if f is not period and (f.n_unique or 0) > 2), None)
    quants = _by_kind(fields, QUANTITATIVE)
    if entity and quants:
        return period, entity, quants[0]
    return None


def _slope_dumbbell(period: Field, entity: Field, value: Field) -> list[ChartCandidate]:
    return [
        CC('slope', 'line', {'x': period.name, 'y': value.name, 'detail': entity.name, 'color': entity.name},
           f"Two periods ({period.name}) across {entity.n_unique} items -> slope graph; each line's tilt is who rose/fell.", 1.0),
        CC('dumbbell', 'point', {'y': entity.name, 'x': value.name, 'color': period.name},
           'Dumbbell (two dots per item joined by a line) when the gap size matters more than rank change.', 0.8),
    ]


def _trend(fields, n_rows, top_n):
    temps, quants, cats = _by_kind(fields, TEMPORAL), _by_kind(fields, QUANTITATIVE), _by_kind(fields, CATEGORICAL)
    x = temps[0] if temps else (cats[0] if cats else None)
    y = quants[0] if quants else None
    series = next((c for c in cats if x is None or c.name != x.name), None)
    if not (x and y):
        return []
    if series:
        n_series = series.n_unique or (MANY_SERIES_MAX + 1)
        if n_series > MANY_SERIES_MAX:
            return [
                CC('small_multiples_line', 'line', {'x': x.name, 'y': y.name, 'facet': series.name},
                   f'{n_series} series -> small multiples (one panel per {series.name}); a single multi-line would be unreadable spaghetti.', 1.0),
                CC('line', 'line', {'x': x.name, 'y': y.name, 'color': series.name},
                   'A colored multi-line only if you must overlay — expect occlusion above ~7 series.', 0.5),
            ]
        return [
            CC('line', 'line', {'x': x.name, 'y': y.name, 'color': series.name},
               f'{n_series} series -> one line each, direct-labelled (color is fine at this few series).', 1.0),
            CC('small_multiples_line', 'line', {'x': x.name, 'y': y.name, 'facet': series.name},
               'Facet into small multiples if the lines cross enough to occlude.', 0.7),
        ]
    return [
        CC('line', 'line', {'x': x.name, 'y': y.name},
           'A single series over time -> line (slope reads as rate of change).', 1.0),
        CC('area', 'area', {'x': x.name, 'y': y.name},
           'Area only if the magnitude/volume reading matters and the series stays >= 0.', 0.6),
    ]


def _comparison(fields, n_rows, top_n):
    tp = _two_period(fields)
    if tp:
        return _slope_dumbbell(*tp)
    cats, quants = _by_kind(fields, CATEGORICAL), _by_kind(fields, QUANTITATIVE)
    cat = cats[0] if cats else None
    val = quants[0] if quants else None
    extra = cats[1] if len(cats) > 1 else None
    if not (cat and val):
        return [CC('bar', 'bar', {'x': (cat.name if cat else 'category'), 'y': (val.name if val else 'value')},
                   'Default bar comparison.', 0.6)]
    card = cat.n_unique or (BAR_CARD_MAX + 1)
    out: list[ChartCandidate] = []
    if card <= LOW_CARD_MAX:
        enc = {'x': cat.name, 'y': val.name}
        if extra:
            enc['color'] = extra.name
        out.append(CC('bar', 'bar', enc,
                      f'{card} categories compare cleanly as vertical bars (length on a common baseline)'
                      + (f'; group by {extra.name} via color.' if extra else '.'), 1.0))
    elif card <= BAR_CARD_MAX:
        out.append(CC('horizontal_bar', 'bar', {'y': cat.name, 'x': val.name},
                      f'{card} categories -> horizontal bars so labels stay readable; sort by value.', 1.0, transform='sort:desc'))
    else:
        out.append(CC('horizontal_bar_top_n', 'bar', {'y': cat.name, 'x': val.name},
                      f"{card} categories is too many to compare at once -> show the top {top_n}, bucket the rest as 'other'.",
                      1.0, transform=f'top_n({cat.name},{top_n},other=True); sort:desc'))
    if card > LOW_CARD_MAX:
        out.append(CC('lollipop', 'point', {'y': cat.name, 'x': val.name},
                      'Lollipop = the same ranking with a higher data-ink ratio when bars get dense.', 0.75,
                      transform=out[0].transform))
    return out


def _ranking(fields, n_rows, top_n):
    tp = _two_period(fields)
    if tp:
        return _slope_dumbbell(*tp)
    cats, quants = _by_kind(fields, CATEGORICAL), _by_kind(fields, QUANTITATIVE)
    cat = cats[0] if cats else None
    val = quants[0] if quants else None
    if not (cat and val):
        return []
    card = cat.n_unique or (BAR_CARD_MAX + 1)
    if card > BAR_CARD_MAX:
        primary = CC('horizontal_bar_top_n', 'bar', {'y': cat.name, 'x': val.name},
                     f"Ranking {card} items -> sorted horizontal bars, top {top_n} with an 'other' bucket (position is the most accurate channel).",
                     1.0, transform=f'top_n({cat.name},{top_n},other=True); sort:desc')
    else:
        primary = CC('horizontal_bar', 'bar', {'y': cat.name, 'x': val.name},
                     'Ranking -> sorted horizontal bars (position/length, labels readable).', 1.0, transform='sort:desc')
    return [primary,
            CC('lollipop', 'point', {'y': cat.name, 'x': val.name},
               'Lollipop conveys the same ranking with less ink when the bar count is high.', 0.75, transform=primary.transform)]


def _distribution(fields, n_rows, top_n):
    quants, cats = _by_kind(fields, QUANTITATIVE), _by_kind(fields, CATEGORICAL)
    q = quants[0] if quants else None
    if not q:
        return []
    cav: list[str] = []
    if q.skew is not None and abs(q.skew) > SKEW_LOG:
        cav.append(f"skew={q.skew}: heavy tail — put {q.name} on a log scale (or clip) so the bulk isn't squashed.")
    histogram = CC('histogram', 'bar', {'x': q.name}, 'Shape of one quantitative variable -> histogram (counts per bin).',
                   1.0, transform='bin', caveats=cav)
    ecdf = CC('ecdf', 'line', {'x': q.name},
              'ECDF reads medians/quantiles exactly and is bin-width-free — pair it with the histogram.', 0.8, caveats=cav)
    if not cats:
        return [histogram, ecdf,
                CC('box', 'boxplot', {'y': q.name},
                   "Boxplot for a compact five-number summary; it hides modality, so don't use it alone.", 0.6, caveats=cav)]
    # a grouping is present: the point is to COMPARE the distribution across it, so the grouped view leads
    g = cats[0]
    n_groups = g.n_unique or (MANY_SERIES_MAX + 1)
    faceted = CC('faceted_histogram', 'bar', {'x': q.name, 'facet': g.name},
                 f'Compare the distribution across {g.name} -> small-multiple histograms on shared axes.', 0.0, transform='bin', caveats=cav)
    violin = CC('violin', 'area', {'x': g.name, 'y': q.name},
                f'Compare {n_groups} groups compactly -> violins (a box hides modality; a violin keeps the shape).', 0.0, caveats=cav)
    if n_groups <= MANY_SERIES_MAX:
        faceted.score, violin.score = 1.0, 0.8
        histogram.rationale = 'Pooled histogram if only the marginal shape matters, not the per-group differences.'
        histogram.score = 0.6
        return [faceted, violin, ecdf, histogram]
    violin.score, faceted.score = 1.0, 0.6
    box = CC('box', 'boxplot', {'x': g.name, 'y': q.name},
             'Box is even more compact than a violin but hides modality — use when groups are very many.', 0.8, caveats=cav)
    return [violin, box, faceted]


def _correlation(fields, n_rows, top_n):
    quants, cats = _by_kind(fields, QUANTITATIVE), _by_kind(fields, CATEGORICAL)
    if len(quants) < 2:
        return _distribution(fields, n_rows, top_n)
    xq, yq = quants[0], quants[1]
    enc = {'x': xq.name, 'y': yq.name}
    scatter_enc = {**enc, 'color': cats[0].name} if cats else dict(enc)
    risk = overplot_risk(n_rows)
    if risk == 'high':
        return [
            CC('density_heatmap', 'rect', {**enc, 'color': 'count()'},
               f'n={n_rows:,} -> raw points overplot into a blob; bin to a 2D density and encode count by color.', 1.0, transform='bin2d'),
            CC('hexbin', 'rect', {**enc, 'color': 'count()'},
               'Hex-binned density — the hexagonal alternative to a rectangular heatmap.', 0.8, transform='hexbin'),
            CC('scatter', 'point', scatter_enc,
               'Raw scatter only after sampling to a few thousand rows.', 0.6,
               caveats=['Sample (reproducible seed) before plotting raw points at this n.']),
        ]
    if risk == 'medium':
        return [
            CC('scatter', 'point', scatter_enc,
               f'n={n_rows:,} -> scatter still works with care: drop opacity and shrink marks to reveal density.', 1.0,
               caveats=['Moderate overplotting: reduce point opacity (~0.3) and size.']),
            CC('density_heatmap', 'rect', {**enc, 'color': 'count()'},
               "Switch to a 2D density if opacity still doesn't reveal the structure.", 0.75, transform='bin2d'),
        ]
    return [
        CC('scatter', 'point', scatter_enc, f'n={n_rows:,} -> a plain scatter reads the relationship directly.', 1.0),
        CC('scatter_with_trend', 'point', scatter_enc,
           'Add a loess/linear trend line to assert the direction of the relationship.', 0.7, transform='trend'),
    ]


def _part_to_whole(fields, n_rows, top_n):
    cats, quants, temps = _by_kind(fields, CATEGORICAL), _by_kind(fields, QUANTITATIVE), _by_kind(fields, TEMPORAL)
    cat = cats[0] if cats else None
    val = quants[0] if quants else None
    out: list[ChartCandidate] = []
    if temps and cat and val:
        out.append(CC('stacked_area', 'area', {'x': temps[0].name, 'y': val.name, 'color': cat.name},
                      'Composition over time -> stacked area (the parts sum to the whole at each period).', 1.0, transform='aggregate:sum'))
    if cat and val:
        card = cat.n_unique or (BAR_CARD_MAX + 1)
        score = 0.9 if out else 1.0
        if card > BAR_CARD_MAX:
            out.append(CC('horizontal_bar_top_n', 'bar', {'y': cat.name, 'x': val.name},
                          f"{card} parts is too many to read as a whole -> rank the top {top_n} as bars (position), bucket the rest as 'other'.",
                          score, transform=f'top_n({cat.name},{top_n},other=True); normalize:%'))
            out.append(CC('treemap', 'rect', {'size': val.name, 'color': cat.name},
                          'Treemap packs many parts into area — space-efficient, but area is read less precisely than length.', 0.6))
        else:
            orient = 'bar' if card <= LOW_CARD_MAX else 'horizontal_bar'
            enc = {'x': cat.name, 'y': val.name} if orient == 'bar' else {'y': cat.name, 'x': val.name}
            out.append(CC(orient, 'bar', enc,
                          'Parts of a whole compare best as bars (position/length beats angle/area); show shares as % and sort by size.',
                          score, transform='normalize:%'))
        if card <= PIE_MAX:
            out.append(CC('pie', 'arc', {'theta': val.name, 'color': cat.name},
                          f'Pie is acceptable at <= {PIE_MAX} slices, but a bar still compares more precisely — use it only when the part-of-whole framing matters more than the comparison.', 0.5))
    if not out and val:
        out.append(CC('bar', 'bar', {'x': (cat.name if cat else 'category'), 'y': val.name}, 'Default bar.', 0.6))
    return out


def _geographic(fields, n_rows, top_n):
    cats, quants = _by_kind(fields, CATEGORICAL), _by_kind(fields, QUANTITATIVE)
    region = cats[0].name if cats else 'region'
    val = quants[0].name if quants else 'value'
    needs = ("A profile can't see geometry: supply region boundaries (GeoJSON/TopoJSON) keyed to the "
             'region id, or lat-lon point coordinates.')
    return [
        CC('choropleth', 'geoshape', {'shape': region, 'color': val},
           'Region-level magnitude on a map -> choropleth (fill each area by value). Use a sequential scale.', 1.0,
           caveats=[needs, 'Choropleths bias toward large/low-density areas — map a rate (per-capita), not a raw count, and consider a cartogram.']),
        CC('symbol_map', 'point', {'longitude': 'lon', 'latitude': 'lat', 'size': val},
           'Proportional-symbol map when you have lat-lon and want magnitude without area distortion.', 0.8, caveats=[needs]),
    ]


def _flow(fields, n_rows, top_n):
    cats, quants = _by_kind(fields, CATEGORICAL), _by_kind(fields, QUANTITATIVE)
    val = quants[0].name if quants else 'value'
    s = cats[0].name if len(cats) >= 1 else 'source'
    t = cats[1].name if len(cats) >= 2 else 'target'
    needs = (f'Needs an edge list — source->target pairs with a flow magnitude ({s} -> {t}, {val}); '
             "a flat column profile won't surface the linkage.")
    return [
        CC('sankey', 'link', {'source': s, 'target': t, 'value': val},
           'Flows between nodes with magnitude -> Sankey (band width = volume). Best for a few stages.', 1.0, caveats=[needs]),
        CC('chord', 'arc', {'source': s, 'target': t, 'value': val},
           'Chord diagram for many-to-many flows among one set of nodes (e.g. region-to-region migration).', 0.8, caveats=[needs]),
    ]


_HANDLERS = {
    'trend-over-time': _trend,
    'comparison': _comparison,
    'distribution': _distribution,
    'correlation': _correlation,
    'part-to-whole': _part_to_whole,
    'ranking': _ranking,
    'geographic': _geographic,
    'flow': _flow,
}


def recommend(intent: str, fields: Iterable[Field], n_rows: int, *, top_n: int = 15) -> list[ChartCandidate]:
    """Rank chart candidates for (intent x the data's signals). Primary first.

    `fields` carry normalized kinds + signals; `n_rows` drives overplotting. Raises on unknown intent.
    """
    intent = INTENT_ALIASES.get(intent, intent)
    if intent not in VALID_INTENTS:
        raise ValueError(f'unknown intent {intent!r}; expected one of {sorted(VALID_INTENTS)} '
                         f'(or aliases {sorted(INTENT_ALIASES)})')
    fields = list(fields)
    cands = _HANDLERS[intent](fields, n_rows or 0, top_n)
    # post-process: surface missingness on any field a candidate actually encodes.
    fmap = {f.name: f for f in fields}
    for c in cands:
        for nm in set(c.encodings.values()):
            f = fmap.get(nm)
            if f and f.null_pct and f.null_pct >= MISSING_CAVEAT_PCT:
                c.caveats.append(f"{nm} is {f.null_pct}% null — surface or handle the missingness; don't silently drop rows.")
    cands.sort(key=lambda c: c.score, reverse=True)   # stable: primary already highest
    return cands


# --- CLI ------------------------------------------------------------------------------------------

def _read(path: str):
    import polars as pl
    if path.lower().endswith(('.csv', '.tsv', '.txt')):
        return pl.read_csv(path, separator='\t' if path.lower().endswith('.tsv') else ',', infer_schema_length=None)
    return pl.read_parquet(path)


def _enrich_signals(fields: list[Field], df) -> None:
    """Fill the viz signals the profile omits (skew, outlier ratio) from the raw frame, in place."""
    for f in fields:
        if f.kind == QUANTITATIVE and f.name in df.columns:
            f.skew = skewness(df[f.name])
            f.outlier_ratio = outlier_ratio(df[f.name])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('data', nargs='?', help='raw csv/tsv/parquet — used to compute viz signals the profile omits')
    ap.add_argument('--profile', help='explore-data profile JSON (profile.py --json)')
    ap.add_argument('--intent', required=True, help='one of: ' + ', '.join(sorted(VALID_INTENTS)))
    ap.add_argument('--fields', help='comma-separated columns to consider, in role order (default: all)')
    ap.add_argument('--top-n', type=int, default=15)
    ap.add_argument('--json', help='write the ranked candidates here as JSON')
    a = ap.parse_args()

    df = _read(a.data) if a.data else None
    if a.profile:
        prof = json.loads(Path(a.profile).read_text())
        fields = fields_from_profile(prof)
        n_rows = prof.get('n_rows') or (df.height if df is not None else 0)
    elif df is not None:
        fields = fields_from_frame(df)
        n_rows = df.height
    else:
        ap.error('provide --profile and/or a data path')

    if a.fields:
        want = [s.strip() for s in a.fields.split(',')]
        fmap = {f.name: f for f in fields}
        missing = [w for w in want if w not in fmap]
        if missing:
            ap.error(f'--fields not in data: {missing}')
        fields = [fmap[w] for w in want]

    if df is not None:
        _enrich_signals(fields, df)

    cands = recommend(a.intent, fields, n_rows, top_n=a.top_n)

    print(f'\n=== chart recommendations: intent={a.intent}, n_rows={n_rows:,} ===')
    print('fields: ' + ', '.join(f'{f.name}({f.kind}'
          + (f', n_unique={f.n_unique}' if f.n_unique is not None else '')
          + (f', skew={f.skew}' if f.skew is not None else '') + ')' for f in fields))
    for i, c in enumerate(cands, 1):
        tag = 'PRIMARY' if i == 1 else f'alt {i-1}'
        print(f'\n[{tag}] {c.chart}  (mark={c.mark}, score={c.score})')
        print(f'  encodings: {c.encodings}')
        if c.transform:
            print(f'  transform: {c.transform}')
        print(f'  why: {c.rationale}')
        for cv in c.caveats:
            print(f'  ! {cv}')
    print()

    if a.json:
        payload = [vars(c) for c in cands]
        Path(a.json).write_text(json.dumps(payload, indent=2))
        print(f'wrote {a.json}\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
