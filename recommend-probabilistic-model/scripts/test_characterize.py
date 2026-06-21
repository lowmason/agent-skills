"""Tests for the modeling-signal extractor."""
import polars as pl

from characterize import (
    class_balance,
    n_over_p,
    overdispersion,
    stationarity_hint,
    stationarity_report,
    zero_fraction,
)


def test_overdispersion_flags_var_gg_mean():
    s = pl.Series([0, 0, 1, 0, 5, 0, 12, 0, 0, 30, 0, 7], dtype=pl.Int64)
    assert overdispersion(s) > 1.5  # variance ≫ mean → NB over Poisson


def test_overdispersion_none_for_floats():
    assert overdispersion(pl.Series([1.0, 2.0, 3.0])) is None


def test_zero_fraction():
    assert zero_fraction(pl.Series([0, 0, 1, 2, 0])) == 0.6


def test_n_over_p():
    assert n_over_p(400, 20) == 20.0
    assert n_over_p(10, 0) is None


def test_class_balance_imbalance_ratio():
    cb = class_balance(pl.Series(["a"] * 90 + ["b"] * 10))
    assert cb["n_classes"] == 2
    assert cb["imbalance_ratio"] == 9.0


def test_stationarity_hint_detects_trend():
    s = pl.Series([float(i) for i in range(40)])  # strong upward trend
    h = stationarity_hint(s)
    assert h["split_half_mean_shift_sd"] > 1.0
    assert h["lag1_autocorr"] > 0.9


def test_stationarity_hint_none_when_too_short():
    assert stationarity_hint(pl.Series([1.0, 2.0, 3.0])) is None


def test_stationarity_report_sorts_by_time():
    # rows are in DESCENDING time order; sorting by t must recover the upward trend (sign flips)
    t = list(range(40))
    df = pl.DataFrame({"t": t[::-1], "x": [float(i) for i in t[::-1]]})
    rep = stationarity_report(df, "t", ["x"])
    assert rep["x"]["split_half_mean_shift_sd"] > 1.0  # after sort: ascending → positive shift
    raw = stationarity_hint(df["x"])  # without the sort, the hint has the opposite sign
    assert raw["split_half_mean_shift_sd"] < -1.0


def test_stationarity_report_excludes_time_column():
    df = pl.DataFrame({"t": [float(i) for i in range(40)], "x": [1.0] * 40})
    assert "t" not in stationarity_report(df, "t", ["t", "x"])


def test_class_balance_none_for_non_categorical():
    assert class_balance(pl.Series(list(range(50)))) is None          # high cardinality
    assert class_balance(pl.Series([float(i) for i in range(5)])) is None  # float dtype
