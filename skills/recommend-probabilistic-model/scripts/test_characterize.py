"""Tests for the modeling-signal extractor."""
import json
from datetime import date

import polars as pl
import pytest

from characterize import (
    class_balance,
    main,
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


def _write(tmp_path, **cols):
    path = tmp_path / "data.parquet"
    pl.DataFrame(cols).write_parquet(path)
    return str(path)


def test_main_boolean_target_is_characterized_not_a_crash(tmp_path, capsys):
    """A Boolean target raised NotImplementedError in zero_fraction (Boolean has no eq operator)."""
    path = _write(tmp_path, y=[True, False, False, False, True, False], x1=[1, 2, 3, 4, 5, 6])
    main([path, "--target", "y"])
    target = json.loads(capsys.readouterr().out)["target"]
    assert target["zero_fraction"] == pytest.approx(0.6667)  # the share of False
    assert target["overdispersion"] is None  # not count-like
    assert target["class_balance"]["n_classes"] == 2


def test_zero_fraction_counts_false_in_a_boolean_series():
    assert zero_fraction(pl.Series([True, False, False, None])) == pytest.approx(0.6667)


def test_main_categorical_target_is_characterized_not_a_crash(tmp_path, capsys):
    """A Categorical target raised "cannot compare categorical with i64" in zero_fraction."""
    labels = pl.Series(["a", "b", "b", "c", "b", "a"], dtype=pl.Categorical)
    path = _write(tmp_path, y=labels, x1=[1, 2, 3, 4, 5, 6])
    assert pl.read_parquet(path)["y"].dtype == pl.Categorical  # the premise: parquet keeps it
    main([path, "--target", "y"])
    target = json.loads(capsys.readouterr().out)["target"]
    assert target["zero_fraction"] is None  # labels have no zeros to count
    assert target["overdispersion"] is None  # not count-like
    assert target["class_balance"]["n_classes"] == 3


@pytest.mark.parametrize(
    "series",
    [
        pl.Series(["a", "b", "a"], dtype=pl.Categorical),
        pl.Series(["a", "b", "a"], dtype=pl.Enum(["a", "b"])),
        pl.Series(["a", "b", "a"]),  # returned 0.0, a share of zeros among labels
        pl.Series([date(2020, 1, 1)] * 3),
    ],
    ids=["categorical", "enum", "string", "date"],
)
def test_zero_fraction_is_none_for_a_non_numeric_series(series):
    assert zero_fraction(series) is None


@pytest.mark.parametrize(
    "flag, value, message",
    [
        ("--target", "y_typo", "y_typo"),
        ("--predictors", "x1,nope", "nope"),
        ("--time", "when_typo", "when_typo"),
    ],
)
def test_main_rejects_an_unknown_column_name(tmp_path, capsys, flag, value, message):
    """A misspelled column used to exit 0 with the target block missing (or `nope` counted as a predictor)."""
    path = _write(tmp_path, y=[1, 2, 3, 4], x1=[1.0, 2.0, 3.0, 4.0])
    with pytest.raises(SystemExit) as exc:
        main([path, "--target", "y", flag, value] if flag != "--target" else [path, flag, value])
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert message in err and flag in err


def test_main_with_known_columns_still_reports_the_target_and_time_block(tmp_path, capsys):
    path = _write(
        tmp_path,
        y=[0, 1, 0, 2, 0, 3, 0, 4, 0, 5],
        t=list(range(10)),
        x1=[float(i) for i in range(10)],
    )
    main([path, "--target", "y", "--predictors", "t,x1", "--time", "t"])
    out = json.loads(capsys.readouterr().out)
    assert out["n_predictors"] == 2
    assert out["target"]["name"] == "y"
    assert list(out["stationarity"]) == ["x1"]
