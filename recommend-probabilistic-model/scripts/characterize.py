"""Modeling-relevant data signals that explore-data's profile.py does NOT compute.

profile.py already reports null %, cardinality (n_unique), dtypes, quartiles, key-uniqueness,
and panel balance. This script adds the signals that drive a *modeling* decision and nothing
more (DRY with explore-data): overdispersion, zero-fraction, n/p ratio, class balance, and a
dependency-light stationarity hint. Output JSON feeds the recommend-probabilistic-model
procedure (Step 2: Characterize the data). Polars + stdlib only.
"""
from __future__ import annotations

import argparse
import json

import polars as pl


def overdispersion(s: pl.Series):
    """var/mean for a count-like (non-negative integer) column; None if not count-like.

    var > mean (ratio > ~1) points away from Poisson toward NegativeBinomial.
    """
    if not s.dtype.is_integer():
        return None
    s = s.drop_nulls()
    if s.len() == 0 or (s < 0).any():
        return None
    m = s.mean()
    return None if not m else round(float(s.var() / m), 3)


def zero_fraction(s: pl.Series) -> float:
    """Fraction of exact zeros — high values point to zero-inflated / hurdle models."""
    s = s.drop_nulls()
    return 0.0 if s.len() == 0 else round(float((s == 0).sum() / s.len()), 4)


def n_over_p(n_rows: int, n_predictors: int):
    """Rows per predictor; low values point to regularization / sparsity."""
    return None if not n_predictors else round(n_rows / n_predictors, 2)


def class_balance(s: pl.Series):
    """For a categorical/low-cardinality target: class count + min/max frequency + imbalance."""
    s = s.drop_nulls()
    if s.len() == 0:
        return None
    vc = s.value_counts(sort=True)
    fr = [c / s.len() for c in vc[vc.columns[-1]].to_list()]
    return {
        "n_classes": len(fr),
        "min_class_frac": round(min(fr), 4),
        "max_class_frac": round(max(fr), 4),
        "imbalance_ratio": round(max(fr) / min(fr), 2) if min(fr) else None,
    }


def stationarity_hint(s: pl.Series):
    """Dependency-light trend/persistence hint: split-half mean shift (std units) + lag-1 autocorr.

    Large |shift| or near-1 autocorr point to nonstationarity → state-space / differencing.
    """
    s = s.drop_nulls().cast(pl.Float64)
    if s.len() < 8:
        return None
    h, sd = s.len() // 2, s.std()
    shift = round(float((s[h:].mean() - s[:h].mean()) / sd), 3) if sd else 0.0
    x0, x1 = s[:-1], s[1:]
    ac1 = (
        round(float(((x0 - x0.mean()) * (x1 - x1.mean())).sum() / ((x0 - x0.mean()) ** 2).sum()), 3)
        if x0.std()
        else None
    )
    return {"split_half_mean_shift_sd": shift, "lag1_autocorr": ac1}


def _read(path: str) -> pl.DataFrame:
    if path.endswith((".csv", ".tsv")):
        return pl.read_csv(path, separator="\t" if path.endswith(".tsv") else ",")
    return pl.read_parquet(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("data", help="path to a csv/tsv/parquet dataset")
    ap.add_argument("--target", help="target/outcome column")
    ap.add_argument("--predictors", help="comma-separated predictor columns (default: all but target)")
    ap.add_argument("--time", help="treat numeric predictors as time series for a stationarity hint")
    ap.add_argument("--json", help="write JSON here instead of stdout")
    a = ap.parse_args()

    df = _read(a.data)
    preds = a.predictors.split(",") if a.predictors else [c for c in df.columns if c != a.target]
    out = {"n_rows": df.height, "n_predictors": len(preds), "n_over_p": n_over_p(df.height, len(preds))}
    if a.target and a.target in df.columns:
        t = df[a.target]
        out["target"] = {
            "name": a.target,
            "overdispersion": overdispersion(t),
            "zero_fraction": zero_fraction(t),
            "class_balance": class_balance(t),
        }
    if a.time:
        out["stationarity"] = {
            c: stationarity_hint(df[c]) for c in preds if c in df.columns and df[c].dtype.is_numeric()
        }
    js = json.dumps(out, indent=2)
    if a.json:
        with open(a.json, "w") as fh:
            fh.write(js)
    else:
        print(js)


if __name__ == "__main__":
    main()
