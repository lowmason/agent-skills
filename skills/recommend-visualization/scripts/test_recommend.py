"""Golden cases for the chart recommender.

These ARE the skill's Iron-Law test (a reference/technique skill is verified by retrieval +
application, not pressure scenarios). Each case is written to FAIL against a plausible-but-wrong
mapping — scatter on large n, pie on high cardinality, a spaghetti multi-line on many series, a
pooled histogram where a grouped view is wanted — so a green run means the recommender encodes the
(intent x data-signal) logic, not just intent -> chart. The contract tests at the end keep
chart-selection.md and recommend.py in lockstep (the doc advertises this).
"""
import re
from pathlib import Path

import polars as pl
import pytest

import recommend as R
from recommend import (
    Field,
    fields_from_profile,
    kind_from_dtype,
    outlier_ratio,
    overplot_risk,
    recommend,
    skewness,
    top_n_coverage,
)

CHART_SELECTION = Path(__file__).resolve().parent.parent / 'references' / 'chart-selection.md'


def top(intent, fields, n_rows, **kw):
    cands = recommend(intent, fields, n_rows, **kw)
    assert cands, 'recommend returned no candidates'
    return cands[0]


# ---- intent x signal -> chart (the differentiator) -----------------------------------------------

def test_temporal_plus_one_series_is_a_line():
    c = top('trend-over-time', [Field('month', 'temporal'), Field('emp', 'quantitative')], 120)
    assert c.chart == 'line' and c.mark == 'line'
    assert c.encodings['x'] == 'month' and c.encodings['y'] == 'emp'


def test_many_series_facets_not_spaghetti():
    # 24 series: a single color-encoded multi-line is unreadable — must facet into small multiples.
    fields = [Field('month', 'temporal'), Field('emp', 'quantitative'),
              Field('industry', 'categorical', n_unique=24)]
    c = top('trend-over-time', fields, 24 * 120)
    assert c.chart == 'small_multiples_line'
    assert c.encodings.get('facet') == 'industry'
    assert 'color' not in c.encodings  # the spaghetti encoding is explicitly avoided


def test_few_series_uses_color_not_facet():
    fields = [Field('month', 'temporal'), Field('emp', 'quantitative'),
              Field('region', 'categorical', n_unique=4)]
    c = top('trend-over-time', fields, 4 * 120)
    assert c.chart == 'line'
    assert c.encodings.get('color') == 'region'
    assert 'facet' not in c.encodings


def test_high_cardinality_categorical_plus_count_is_top_n_horizontal_bar():
    fields = [Field('industry', 'categorical', n_unique=320), Field('emp', 'quantitative')]
    c = top('ranking', fields, 320)
    assert c.chart == 'horizontal_bar_top_n' and c.mark == 'bar'
    assert c.encodings['y'] == 'industry' and c.encodings['x'] == 'emp'
    assert c.transform and 'top_n' in c.transform and 'other' in c.transform


def test_low_cardinality_comparison_is_vertical_bar():
    fields = [Field('region', 'categorical', n_unique=5), Field('emp', 'quantitative')]
    c = top('comparison', fields, 5)
    assert c.chart == 'bar' and c.mark == 'bar'
    assert c.encodings['x'] == 'region' and c.encodings['y'] == 'emp'


def test_two_quantitative_small_n_is_scatter():
    fields = [Field('wage', 'quantitative'), Field('hours', 'quantitative')]
    c = top('correlation', fields, 300)
    assert c.chart == 'scatter' and c.mark == 'point'
    assert set(c.encodings.values()) >= {'wage', 'hours'}


def test_two_quantitative_large_n_is_density_not_scatter():
    fields = [Field('wage', 'quantitative'), Field('hours', 'quantitative')]
    cands = recommend('correlation', fields, 50_000)
    assert cands[0].chart == 'density_heatmap'          # overplotting -> 2D density
    assert cands[0].chart != 'scatter'
    # scatter must still be offered, but demoted below density
    charts = [c.chart for c in cands]
    assert 'scatter' in charts and charts.index('density_heatmap') < charts.index('scatter')


def test_medium_n_scatter_gets_opacity_caveat():
    fields = [Field('wage', 'quantitative'), Field('hours', 'quantitative')]
    c = top('correlation', fields, 2_000)
    assert c.chart == 'scatter'
    assert any('opacity' in cv.lower() for cv in c.caveats)


def test_relationship_is_alias_for_correlation():
    fields = [Field('a', 'quantitative'), Field('b', 'quantitative')]
    assert top('relationship', fields, 300).chart == 'scatter'


def test_distribution_low_skew_is_plain_histogram():
    c = top('distribution', [Field('emp', 'quantitative', skew=0.2)], 5_000)
    assert c.chart == 'histogram' and c.transform == 'bin'
    assert c.encodings['x'] == 'emp'
    assert not any('log' in cv.lower() for cv in c.caveats)


def test_distribution_high_skew_flags_log_scale():
    c = top('distribution', [Field('wage', 'quantitative', skew=4.5)], 5_000)
    assert c.chart == 'histogram'
    assert any('log' in cv.lower() for cv in c.caveats)  # skew > threshold -> log-scale flag


def test_distribution_across_a_few_groups_facets():
    # a grouping is present and the point is to COMPARE across it -> faceted, not a pooled histogram
    c = top('distribution', [Field('wage', 'quantitative'), Field('region', 'categorical', n_unique=4)], 5_000)
    assert c.chart == 'faceted_histogram'
    assert c.encodings.get('facet') == 'region' and c.encodings['x'] == 'wage'


def test_distribution_across_many_groups_is_violin():
    c = top('distribution', [Field('wage', 'quantitative'), Field('dept', 'categorical', n_unique=30)], 5_000)
    assert c.chart == 'violin'
    assert c.encodings['x'] == 'dept' and c.encodings['y'] == 'wage'


def test_part_to_whole_never_pie_above_six():
    fields = [Field('sector', 'categorical', n_unique=11), Field('share', 'quantitative')]
    cands = recommend('part-to-whole', fields, 11)
    assert cands[0].chart != 'pie'
    assert 'pie' not in [c.chart for c in cands]      # 11 > PIE_MAX -> pie not even an alternative


def test_part_to_whole_pie_allowed_at_low_cardinality():
    fields = [Field('sector', 'categorical', n_unique=4), Field('share', 'quantitative')]
    cands = recommend('part-to-whole', fields, 4)
    assert cands[0].chart != 'pie'                    # bar still preferred (position > angle)
    assert 'pie' in [c.chart for c in cands]          # but pie is an acceptable alternative here


def test_two_period_ranking_is_slope():
    # An entity ranked across exactly two periods -> slope/dumbbell, not two bar charts.
    fields = [Field('industry', 'categorical', n_unique=30),
              Field('year', 'temporal', n_unique=2),
              Field('emp', 'quantitative')]
    c = top('ranking', fields, 60)
    assert c.chart in {'slope', 'dumbbell'}


def test_geographic_states_required_encoding():
    # A profile can't surface geometry/lat-lon; recommend the family and say what's needed.
    c = top('geographic', [Field('state', 'categorical', n_unique=51),
                           Field('rate', 'quantitative')], 51)
    assert c.chart in {'choropleth', 'symbol_map'}
    assert any(('geo' in cv.lower() or 'lat' in cv.lower() or 'shape' in cv.lower()
                or 'boundar' in cv.lower()) for cv in c.caveats)


def test_flow_states_required_encoding():
    c = top('flow', [Field('source', 'categorical'), Field('target', 'categorical'),
                     Field('value', 'quantitative')], 200)
    assert c.chart in {'sankey', 'chord'}
    assert any(('source' in cv.lower() and 'target' in cv.lower()) for cv in c.caveats)


def test_null_rate_surfaces_a_caveat():
    fields = [Field('month', 'temporal'), Field('emp', 'quantitative', null_pct=18.0)]
    c = top('trend-over-time', fields, 120)
    assert any(('null' in cv.lower() or 'missing' in cv.lower()) for cv in c.caveats)


def test_unknown_intent_raises():
    with pytest.raises(ValueError):
        recommend('make-it-pretty', [Field('x', 'quantitative')], 10)


def test_every_candidate_carries_an_encoding_map():
    # The thesis: recommendation ~= spec. No candidate may be a bare chart name.
    for c in recommend('comparison', [Field('region', 'categorical', n_unique=5),
                                      Field('emp', 'quantitative')], 5):
        assert isinstance(c.encodings, dict) and c.encodings
        assert c.rationale and isinstance(c.score, float)


# ---- adapter: profile JSON (dtype is a STRING) -> normalized kinds -------------------------------

def test_kind_from_dtype_strings():
    assert kind_from_dtype('Int64') == 'quantitative'
    assert kind_from_dtype('Float64') == 'quantitative'
    assert kind_from_dtype('Date') == 'temporal'
    assert kind_from_dtype("Datetime(time_unit='us', time_zone=None)") == 'temporal'
    assert kind_from_dtype('String') == 'categorical'
    assert kind_from_dtype('Categorical') == 'categorical'
    assert kind_from_dtype('Boolean') == 'boolean'


def test_fields_from_profile():
    profile = {
        'n_rows': 1000,
        'columns': [
            {'column': 'month', 'dtype': 'Date', 'null_pct': 0.0, 'n_unique': 120, 'example': '2020-01-01'},
            {'column': 'emp', 'dtype': 'Int64', 'null_pct': 2.5, 'n_unique': 900, 'example': '1234'},
            {'column': 'industry', 'dtype': 'Categorical', 'null_pct': 0.0, 'n_unique': 24, 'example': '00'},
        ],
    }
    fields = {f.name: f for f in fields_from_profile(profile)}
    assert fields['month'].kind == 'temporal'
    assert fields['emp'].kind == 'quantitative' and fields['emp'].null_pct == 2.5
    assert fields['industry'].kind == 'categorical' and fields['industry'].n_unique == 24


# ---- signal helpers (the characterize.py analog: signals the profile JSON omits) -----------------

def test_skewness_detects_right_skew():
    sym = pl.Series([float(x) for x in range(-50, 51)])
    right = pl.Series([1.0] * 90 + [50.0, 80.0, 120.0, 200.0, 500.0] * 2)
    assert abs(skewness(sym)) < 0.2
    assert skewness(right) > 1.0


def test_outlier_ratio_flags_a_heavy_tail():
    clean = pl.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    heavy = pl.Series([1.0, 2.0, 3.0, 4.0, 5.0, 1000.0])
    assert outlier_ratio(heavy) > outlier_ratio(clean)


def test_top_n_coverage():
    s = pl.Series(['a'] * 95 + ['b', 'c', 'd', 'e', 'f'])
    assert top_n_coverage(s, 1) == pytest.approx(0.95)
    assert top_n_coverage(s, 6) == pytest.approx(1.0)


def test_overplot_risk_thresholds():
    assert overplot_risk(300) == 'low'
    assert overplot_risk(2_000) == 'medium'
    assert overplot_risk(50_000) == 'high'


# ---- contract: chart-selection.md and recommend.py must stay in lockstep -------------------------

def _emitted_chart_names():
    """Every canonical chart name recommend() can emit, driven across all intents and signal regimes."""
    F = lambda name, kind, n=None: Field(name, kind, n_unique=n)  # noqa: E731
    battery = [
        ('trend-over-time', [F('m', 'temporal'), F('y', 'quantitative')], 120),
        ('trend-over-time', [F('m', 'temporal'), F('y', 'quantitative'), F('g', 'categorical', 24)], 2880),
        ('trend-over-time', [F('m', 'temporal'), F('y', 'quantitative'), F('g', 'categorical', 4)], 480),
        ('comparison', [F('c', 'categorical', 5), F('y', 'quantitative')], 5),
        ('comparison', [F('c', 'categorical', 12), F('y', 'quantitative')], 12),
        ('comparison', [F('c', 'categorical', 300), F('y', 'quantitative')], 300),
        ('comparison', [F('c', 'categorical', 30), F('p', 'temporal', 2), F('y', 'quantitative')], 60),
        ('ranking', [F('c', 'categorical', 300), F('y', 'quantitative')], 300),
        ('ranking', [F('c', 'categorical', 10), F('y', 'quantitative')], 10),
        ('distribution', [F('q', 'quantitative')], 5000),
        ('distribution', [F('q', 'quantitative'), F('g', 'categorical', 4)], 5000),
        ('distribution', [F('q', 'quantitative'), F('g', 'categorical', 30)], 5000),
        ('correlation', [F('a', 'quantitative'), F('b', 'quantitative')], 300),
        ('correlation', [F('a', 'quantitative'), F('b', 'quantitative')], 50000),
        ('part-to-whole', [F('c', 'categorical', 4), F('y', 'quantitative')], 4),
        ('part-to-whole', [F('c', 'categorical', 12), F('y', 'quantitative')], 12),
        ('part-to-whole', [F('c', 'categorical', 20), F('y', 'quantitative')], 20),
        ('part-to-whole', [F('m', 'temporal'), F('c', 'categorical', 5), F('y', 'quantitative')], 600),
        ('geographic', [F('c', 'categorical', 51), F('y', 'quantitative')], 51),
        ('flow', [F('s', 'categorical'), F('t', 'categorical'), F('y', 'quantitative')], 200),
    ]
    names = set()
    for intent, fields, n in battery:
        names.update(c.chart for c in recommend(intent, fields, n))
    return names


def _declared_canonical_names():
    text = CHART_SELECTION.read_text()
    section = text.split('## Canonical names')[1].split('\n## ')[0]
    return set(re.findall(r'`([a-z_]+)`', section))


def test_every_emitted_chart_is_declared_in_chart_selection():
    emitted, declared = _emitted_chart_names(), _declared_canonical_names()
    missing = emitted - declared
    assert not missing, f'charts emitted by recommend() but absent from chart-selection.md canonical list: {sorted(missing)}'


def test_threshold_table_matches_constants():
    text = CHART_SELECTION.read_text()
    for name in ('LOW_CARD_MAX', 'BAR_CARD_MAX', 'PIE_MAX', 'OVERPLOT_MEDIUM',
                 'OVERPLOT_HIGH', 'MANY_SERIES_MAX', 'SKEW_LOG'):
        m = re.search(rf'`{name}`\s*\|\s*([0-9.]+)', text)
        assert m, f'{name} not found in the chart-selection.md threshold table'
        assert float(m.group(1)) == float(getattr(R, name)), \
            f'{name}: doc says {m.group(1)} but recommend.py constant is {getattr(R, name)}'
