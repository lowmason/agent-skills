#!/usr/bin/env python3
"""Profile a Polars-readable dataset: shape, schema, nulls, cardinality, numeric/categorical
summaries, date ranges & gaps, duplicate-key detection, vintage/as-of checks, and quality flags.

Scans lazily where it can (so a multi-GB parquet glob never lands in RAM whole) and only
collects the small frames needed for each summary. Pass --candidate-keys to test uniqueness of
a key, and --vintage-cols to check as-of/vintage correctness on revised time series.

Usage:
    uv run --python 3.13 --with polars python ~/.claude/skills/explore-data/scripts/profile.py data/qcew/qcew_estimates.parquet
    uv run --python 3.13 --with polars python ~/.claude/skills/explore-data/scripts/profile.py "data/qcew/*.parquet" --candidate-keys series_id,ref_date,vintage_date
    uv run --python 3.13 --with polars python ~/.claude/skills/explore-data/scripts/profile.py payroll.parquet --candidate-keys client_id,ref_date \
        --panel-entity client_id --panel-period ref_date
    uv run --python 3.13 --with polars python ~/.claude/skills/explore-data/scripts/profile.py raw_scrape.csv --vintage-cols series_id,ref_date,vintage_date --json out.json

The output is a concise text profile by default; --json also writes a machine-readable summary
you can diff between vintages or feed to a report.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import polars as pl

# Sentinels that masquerade as data. The string set covers BLS/QCEW disclosure & suppression
# markers ("." = not disclosable, "N" = not available) alongside the usual CSV/scrape junk.
# The numeric set covers classic "missing as a number" codes. These are FLAGGED, not dropped —
# a column where -1 is legitimate (a diff) should not be silently rewritten.
STRING_SENTINELS = {"", " ", "na", "n/a", "n.a.", "null", "none", "nan", "-", ".", "n", "*", "#n/a"}
NUMERIC_SENTINELS = [-1.0, -9.0, -99.0, -999.0, -9999.0, 9999.0, 99999.0, 999999.0, -999999.0, 9999.9]


def scan(path: str) -> pl.LazyFrame:
    """Lazily scan parquet/csv/ndjson by extension; supports glob patterns for partitioned data."""
    lower = path.lower()
    # Match parquet by suffix (or a glob, for partitioned data) — not a loose substring, which would
    # misroute e.g. /data/snapshot.parquet.d/file.csv into scan_parquet.
    if lower.endswith((".parquet", ".pq")) or "*" in path or "?" in path:
        return pl.scan_parquet(path)
    if lower.endswith((".csv", ".tsv", ".txt")):
        sep = "\t" if lower.endswith(".tsv") else ","
        # infer_schema_length=None scans the whole file: raw scrapes mix types in late rows.
        return pl.scan_csv(path, separator=sep, infer_schema_length=None)
    if lower.endswith((".ndjson", ".jsonl")):
        return pl.scan_ndjson(path)
    raise ValueError(f"Unsupported extension for {path!r}; use parquet, csv/tsv, or ndjson.")


def column_profile(lf: pl.LazyFrame, n_rows: int, schema: pl.Schema) -> list[dict[str, Any]]:
    """Per-column null %, n_unique, and a sample value — computed in one lazy pass."""
    names = list(schema.names())
    null_df = lf.select([pl.col(c).null_count().alias(c) for c in names]).collect()
    nunq_df = lf.select([pl.col(c).n_unique().alias(c) for c in names]).collect()
    sample = lf.select(names).head(5).collect()

    rows: list[dict[str, Any]] = []
    for c in names:
        nulls = int(null_df[c][0])
        nunq = int(nunq_df[c][0])
        non_null = sample[c].drop_nulls()
        example = non_null[0] if non_null.len() else None
        rows.append(
            {
                "column": c,
                "dtype": str(schema[c]),
                "null_pct": round(100 * nulls / n_rows, 2) if n_rows else 0.0,
                "n_unique": nunq,
                "example": str(example),
            }
        )
    return rows


def numeric_summary(lf: pl.LazyFrame, schema: pl.Schema) -> pl.DataFrame | None:
    """min/max/mean/std/quantiles for numeric columns via explicit lazy aggregations.

    Avoids LazyFrame.describe() — its quantile handling has shifted across Polars releases and
    it materializes more than we need. Explicit aggregations keep one predictable lazy pass.
    """
    num = [c for c in schema.names() if schema[c].is_numeric()]
    if not num:
        return None
    aggs: list[pl.Expr] = []
    for c in num:
        col = pl.col(c)
        aggs += [
            col.min().alias(f"{c}__min"),
            # Explicit interpolation="linear" for all three quartiles: the default ("nearest") would
            # disagree with the .median()-based p50 and with the numpy/pandas convention analysts expect.
            col.quantile(0.25, interpolation="linear").alias(f"{c}__p25"),
            col.quantile(0.5, interpolation="linear").alias(f"{c}__p50"),
            col.quantile(0.75, interpolation="linear").alias(f"{c}__p75"),
            col.max().alias(f"{c}__max"),
            col.mean().alias(f"{c}__mean"),
            col.std().alias(f"{c}__std"),
        ]
    flat = lf.select(aggs).collect().row(0, named=True)
    stat_names = ["min", "p25", "p50", "p75", "max", "mean", "std"]
    cols = [pl.Series("column", num, dtype=pl.String)]
    # Force Float64: min/max of an integer column are ints while mean/std are floats; mixing them
    # in one Series makes Polars infer Int64 and then reject the float. Stats are all real-valued.
    for s in stat_names:
        cols.append(pl.Series(s, [flat[f"{c}__{s}"] for c in num], dtype=pl.Float64, strict=False))
    return pl.DataFrame(cols)


def top_categoricals(lf: pl.LazyFrame, schema: pl.Schema, k: int = 5) -> dict[str, list[tuple[str, int]]]:
    """Top-k value_counts for each string/categorical/bool column.

    Reported for every such column; high-cardinality ones (e.g. series_id) still show their k most
    frequent values, which is a useful smell test for skew and stray codes.
    """
    cats = [c for c in schema.names() if schema[c] in (pl.String, pl.Categorical, pl.Boolean)]
    out: dict[str, list[tuple[str, int]]] = {}
    for c in cats:
        vc = (
            lf.select(pl.col(c))
            .drop_nulls()  # null is not a "top value": skip it so an all-null column reports nothing
            .group_by(c)
            .agg(pl.len().alias("count"))
            .sort("count", descending=True)
            .head(k)
            .collect()
        )
        if vc.height == 0:  # no non-null values (e.g. an all-null or empty column): nothing to report
            continue
        out[c] = [(str(v), int(n)) for v, n in zip(vc[c], vc["count"])]
    return out


def date_ranges(lf: pl.LazyFrame, schema: pl.Schema) -> dict[str, dict[str, Any]]:
    """Min/max and a monthly-gap check for Date/Datetime columns."""
    dates = [c for c in schema.names() if schema[c] in (pl.Date, pl.Datetime)]
    out: dict[str, dict[str, Any]] = {}
    for c in dates:
        rng = lf.select(pl.col(c).min().alias("lo"), pl.col(c).max().alias("hi")).collect()
        lo, hi = rng["lo"][0], rng["hi"][0]
        info: dict[str, Any] = {"min": str(lo), "max": str(hi)}
        if lo is not None and hi is not None:
            present = lf.select(pl.col(c).cast(pl.Date)).unique().collect()[c]
            expected = pl.date_range(lo, hi, interval="1mo", eager=True)
            missing = expected.filter(~expected.is_in(present.implode()))
            info["expected_monthly_periods"] = expected.len()
            info["present_periods"] = present.n_unique()
            info["missing_monthly_periods"] = missing.len()
            if 0 < missing.len() <= 12:
                info["missing_examples"] = [str(d) for d in missing.to_list()]
        out[c] = info
    return out


def duplicate_check(lf: pl.LazyFrame, keys: list[str], schema: pl.Schema) -> dict[str, Any]:
    """Is `keys` a unique key? Report duplicate-group count and a worst-offender example."""
    missing = [k for k in keys if k not in schema.names()]
    if missing:
        return {"keys": keys, "error": f"columns not in data: {missing}"}
    dups = (
        lf.group_by(keys)
        .agg(pl.len().alias("n"))
        .filter(pl.col("n") > 1)
        .sort("n", descending=True)
        .collect()
    )
    result = {
        "keys": keys,
        "is_unique": dups.height == 0,
        "duplicate_groups": dups.height,
        "extra_rows": int(dups["n"].sum() - dups.height) if dups.height else 0,
    }
    if dups.height:
        result["worst_example"] = dups.head(1).to_dicts()[0]
    return result


def vintage_check(lf: pl.LazyFrame, cols: list[str], schema: pl.Schema) -> dict[str, Any]:
    """As-of / vintage correctness for revised series.

    cols = [series_id..., ref_date, vintage_date]: the last two are the period and the
    vintage. Flags whether a (series, period) appears across multiple vintages (expected for
    revised data), and whether (series, period, vintage) is a clean key (it must be — two rows
    for the same series/period/vintage is a real bug that double-counts a revision).
    """
    missing = [c for c in cols if c not in schema.names()]
    if missing:
        return {"cols": cols, "error": f"columns not in data: {missing}"}
    *id_cols, period, vintage = cols
    if not id_cols:
        id_cols = []
    per_key = id_cols + [period]
    full_key = id_cols + [period, vintage]

    n_vintages = lf.select(pl.col(vintage).n_unique()).collect().item()
    multi = (
        lf.group_by(per_key)
        .agg(pl.col(vintage).n_unique().alias("n_vint"))
        .select((pl.col("n_vint") > 1).sum().alias("revised"), pl.len().alias("total"))
        .collect()
        .row(0, named=True)
    )
    full_dups = (
        lf.group_by(full_key).agg(pl.len().alias("n")).filter(pl.col("n") > 1).collect()
    )
    return {
        "cols": cols,
        "n_vintages": int(n_vintages),
        "period_keys_with_multiple_vintages": int(multi["revised"]),
        "total_period_keys": int(multi["total"]),
        "vintage_key_is_unique": full_dups.height == 0,
        "vintage_key_duplicate_groups": full_dups.height,
    }


def panel_balance(lf: pl.LazyFrame, entity: str, period: str, schema: pl.Schema) -> dict[str, Any]:
    """Panel balance: entities, periods, balanced share, and entry/exit at the endpoints."""
    for c in (entity, period):
        if c not in schema.names():
            return {"entity": entity, "period": period, "error": f"{c} not in data"}
    n_periods = lf.select(pl.col(period).n_unique()).collect().item()
    per_entity = (
        lf.group_by(entity)
        .agg(pl.col(period).n_unique().alias("n_obs"))
        .collect()
    )
    n_entities = per_entity.height
    balanced = int((per_entity["n_obs"] == n_periods).sum())
    # Entry/exit at the panel endpoints: entities first/last seen mid-panel.
    bounds = lf.select(pl.col(period).min().alias("lo"), pl.col(period).max().alias("hi")).collect()
    lo, hi = bounds["lo"][0], bounds["hi"][0]
    span = (
        lf.group_by(entity)
        .agg(pl.col(period).min().alias("first"), pl.col(period).max().alias("last"))
        .collect()
    )
    return {
        "entity": entity,
        "period": period,
        "n_entities": n_entities,
        "n_periods": int(n_periods),
        "balanced_entities": balanced,
        "balanced_pct": round(100 * balanced / n_entities, 2) if n_entities else 0.0,
        "entered_after_start": int((span["first"] > lo).sum()),
        "exited_before_end": int((span["last"] < hi).sum()),
    }


def quality_flags(
    col_rows: list[dict[str, Any]],
    n_rows: int,
    lf: pl.LazyFrame,
    schema: pl.Schema,
) -> list[str]:
    """Heuristic quality flags: high-null, constant, suspicious sentinels."""
    flags: list[str] = []
    for r in col_rows:
        if r["null_pct"] >= 50:
            flags.append(f"HIGH NULL: {r['column']} is {r['null_pct']}% null")
        if r["n_unique"] <= 1 and n_rows > 1:
            flags.append(f"CONSTANT: {r['column']} has {r['n_unique']} distinct value(s)")
    # Sentinel scan: string columns against STRING_SENTINELS, numeric against NUMERIC_SENTINELS.
    for c in schema.names():
        dt = schema[c]
        if dt == pl.String:
            hit = (
                lf.select(
                    pl.col(c)
                    .str.strip_chars()
                    .str.to_lowercase()
                    .is_in(pl.Series(list(STRING_SENTINELS)).implode())
                    .sum()
                    .alias("h")
                )
                .collect()
                .item()
            )
            if hit:
                flags.append(f"SENTINEL: {c} has {hit} sentinel-like string value(s) ({sorted(STRING_SENTINELS)[:6]}...)")
        elif dt.is_numeric():
            # Cast to Float64 so the int/float sentinel list compares cleanly against any numeric dtype.
            hit = (
                lf.select(pl.col(c).cast(pl.Float64).is_in(pl.Series(NUMERIC_SENTINELS).implode()).sum().alias("h"))
                .collect()
                .item()
            )
            if hit:
                flags.append(f"SENTINEL?: {c} has {hit} value(s) matching numeric sentinels (-1/9999/...) — verify they are real")
    return flags


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="parquet/csv/ndjson file or glob")
    ap.add_argument("--candidate-keys", help="comma-separated columns to test for uniqueness")
    ap.add_argument("--vintage-cols", help="comma-separated [id..., period, vintage] for as-of check")
    ap.add_argument("--panel-entity", help="entity column for panel-balance check")
    ap.add_argument("--panel-period", help="period column for panel-balance check")
    ap.add_argument("--json", help="also write machine-readable summary to this path")
    args = ap.parse_args()

    lf = scan(args.path)
    schema = lf.collect_schema()
    n_rows = lf.select(pl.len()).collect().item()

    col_rows = column_profile(lf, n_rows, schema)
    nums = numeric_summary(lf, schema)
    cats = top_categoricals(lf, schema)
    dates = date_ranges(lf, schema)
    flags = quality_flags(col_rows, n_rows, lf, schema)

    print(f"\n=== PROFILE: {args.path} ===")
    print(f"shape: {n_rows:,} rows x {len(schema.names())} cols\n")

    print("per-column:")
    print(f"  {'column':<24}{'dtype':<12}{'null%':>8}{'n_unique':>12}  example")
    for r in col_rows:
        print(f"  {r['column']:<24}{r['dtype']:<12}{r['null_pct']:>8}{r['n_unique']:>12}  {r['example'][:30]}")

    if nums is not None:
        print("\nnumeric summary:")
        with pl.Config(tbl_rows=-1, tbl_cols=-1, float_precision=3):
            print(nums)

    if cats:
        print("\ntop categorical values:")
        for c, vals in cats.items():
            joined = ", ".join(f"{v}={n}" for v, n in vals)
            print(f"  {c}: {joined}")

    if dates:
        print("\ndate ranges:")
        for c, info in dates.items():
            extra = ""
            if info.get("missing_monthly_periods"):
                extra = f"  [GAP: {info['missing_monthly_periods']} missing monthly periods]"
            print(f"  {c}: {info['min']} -> {info['max']}{extra}")

    summary: dict[str, Any] = {
        "path": args.path,
        "n_rows": n_rows,
        "n_cols": len(schema.names()),
        "columns": col_rows,
        "dates": dates,
        "flags": flags,
    }

    if args.candidate_keys:
        keys = [k.strip() for k in args.candidate_keys.split(",")]
        dup = duplicate_check(lf, keys, schema)
        summary["duplicate_check"] = dup
        print(f"\nduplicate check on {keys}:")
        print(f"  {dup}")

    if args.vintage_cols:
        vcols = [c.strip() for c in args.vintage_cols.split(",")]
        vc = vintage_check(lf, vcols, schema)
        summary["vintage_check"] = vc
        print(f"\nvintage / as-of check on {vcols}:")
        print(f"  {vc}")

    if args.panel_entity and args.panel_period:
        pb = panel_balance(lf, args.panel_entity, args.panel_period, schema)
        summary["panel_balance"] = pb
        print(f"\npanel balance ({args.panel_entity} x {args.panel_period}):")
        print(f"  {pb}")

    print("\nquality flags:")
    if flags:
        for f in flags:
            print(f"  - {f}")
    else:
        print("  (none)")
    print()

    if args.json:
        Path(args.json).write_text(json.dumps(summary, indent=2, default=str))
        print(f"wrote {args.json}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
