# Polars pipeline test scaffolds (→ parquet)

The contract of a pipeline is its output. These helpers assert the contract against tiny
in-memory fixtures, so they run in milliseconds and read cleanly in review. Reuse the
assertion helpers across pipelines; keep the fixtures hand-written and small.

## 1. Reusable contract assertions

```python
# tests/asserts.py
from datetime import date, timedelta
import polars as pl


def assert_schema(df: pl.DataFrame, expected: dict[str, pl.DataType]) -> None:
    """Exact columns AND dtypes. Catches renames, drops, adds, and silent dtype drift."""
    assert dict(df.schema) == expected, f"schema drift:\n got {dict(df.schema)}\n want {expected}"


def assert_unique_keys(df: pl.DataFrame, keys: list[str]) -> None:
    """No duplicate keys — the fan-out-join guard."""
    dupes = df.filter(df.select(keys).is_duplicated())
    assert dupes.height == 0, f"{dupes.height} duplicate rows on {keys}:\n{dupes.head()}"


def assert_row_band(df: pl.DataFrame, lo: int, hi: int) -> None:
    """Row count in a plausible band, not an exact brittle number."""
    assert lo <= df.height <= hi, f"row count {df.height} outside [{lo}, {hi}]"


def assert_null_rate_below(df: pl.DataFrame, col: str, max_rate: float) -> None:
    rate = df[col].null_count() / max(df.height, 1)
    assert rate <= max_rate, f"{col} null rate {rate:.3f} > {max_rate}"


def assert_fresh(df: pl.DataFrame, period_col: str, asof: date, max_lag: timedelta) -> None:
    """Latest period present is within max_lag of the as-of date. Stale data passes all else."""
    latest = df[period_col].max()
    assert latest is not None, f"{period_col} is all null"
    assert asof - latest <= max_lag, f"stale: latest {latest} is > {max_lag} before {asof}"
```

## 2. Hand-written tiny fixtures, real transform

Construct the smallest frame that exercises the case, run the **real** transform, assert the
contract. Do not recompute the expected output the way the transform does.

```python
import polars as pl
from datetime import date, timedelta
from tests.asserts import (
    assert_schema, assert_unique_keys, assert_row_band,
    assert_null_rate_below, assert_fresh,
)
from my_pipeline.transform import normalize_ces

EXPECTED_SCHEMA = {
    "series_id": pl.Utf8,
    "period":    pl.Date,
    "value":     pl.Float64,
}


def _raw_ces() -> pl.DataFrame:
    # crafted to include a boundary date and a value to coerce; 4 rows is enough
    return pl.DataFrame({
        "series_id": ["CES0000000001", "CES0000000001", "CES0500000001", "CES0500000001"],
        "period":    ["2026-01", "2026-02", "2026-01", "2026-02"],   # Utf8 on purpose
        "value":     ["153000", "153120", "131900", "132010"],
    })


def test_normalize_ces_schema():
    assert_schema(normalize_ces(_raw_ces()), EXPECTED_SCHEMA)


def test_normalize_ces_keys_unique():
    out = normalize_ces(_raw_ces())
    assert_unique_keys(out, ["series_id", "period"])


def test_normalize_ces_row_band():
    assert_row_band(normalize_ces(_raw_ces()), lo=4, hi=4)   # normalization preserves rows


def test_normalize_ces_no_unexpected_nulls():
    assert_null_rate_below(normalize_ces(_raw_ces()), "value", max_rate=0.0)
```

## 3. Catch the fan-out join explicitly

The single most common Polars pipeline bug: a join key that is not unique on the right side,
silently multiplying rows. Make a fixture that *would* fan out and assert it does not.

```python
def test_join_does_not_fan_out():
    facts = pl.DataFrame({"series_id": ["A", "B"], "value": [1.0, 2.0]})
    # a lookup with a duplicate key — the bug we are guarding against
    lookup = pl.DataFrame({"series_id": ["A", "A", "B"], "industry": ["x", "x", "y"]})
    out = join_industry(facts, lookup)            # the real function under test
    assert_unique_keys(out, ["series_id"])        # fails loudly if join_industry fans out
    assert_row_band(out, lo=2, hi=2)
```

## 4. tmp_path round trip — only when testing I/O itself

Use `tmp_path` to test the parquet writer/reader contract (schema survives the round trip,
partitioning is correct). Do not write parquet just to test a pure transform.

```python
def test_parquet_round_trip_preserves_schema(tmp_path):
    out = normalize_ces(_raw_ces())
    path = tmp_path / "ces.parquet"
    out.write_parquet(path)
    reread = pl.read_parquet(path)
    assert_schema(reread, EXPECTED_SCHEMA)
    assert reread.equals(out)


def test_freshness_against_asof():
    asof = date(2026, 3, 15)
    out = pl.DataFrame({"period": [date(2026, 1, 1), date(2026, 2, 1)], "value": [1.0, 2.0]})
    assert_fresh(out, "period", asof=asof, max_lag=timedelta(days=45))   # Feb present by mid-Mar
```

## 5. Property tests for complex transforms

When a transform is intricate, assert classes of behavior rather than single examples. A small
`hypothesis` strategy that builds random valid frames is worth the dependency for core pipelines.

```python
from hypothesis import given, strategies as st
from hypothesis import HealthCheck, settings

@settings(suppress_health_check=[HealthCheck.too_slow])
@given(st.lists(st.tuples(st.text(min_size=1, max_size=4),
                          st.integers(2020, 2030),
                          st.integers(1, 12)), min_size=1, max_size=50))
def test_dedup_is_idempotent(rows):
    df = pl.DataFrame(rows, schema=["series_id", "year", "month"], orient="row")
    once = dedup_periods(df)
    twice = dedup_periods(once)
    assert once.equals(twice)               # dedup(dedup(x)) == dedup(x)
    assert_unique_keys(once, ["series_id", "year", "month"])
```
