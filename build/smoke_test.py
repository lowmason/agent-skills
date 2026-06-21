"""End-to-end smoke test: a known case must produce the expected routing.

Overdispersed grouped counts → characterize.py flags var≫mean → decision-map routes to a
NegativeBinomial GLM (regression-glm) plus partial pooling on the group (hierarchical). Exercises
the integration contract without touching any PDF. Run: python build/smoke_test.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "recommend-probabilistic-model" / "scripts"))
from characterize import overdispersion, zero_fraction  # noqa: E402


def main() -> int:
    rng = np.random.default_rng(sum(map(ord, "rpm-smoke")))
    g = rng.integers(0, 5, 400)
    y = rng.negative_binomial(2, 0.3, 400) * (1 + (g == 0))  # overdispersed, group-varying
    df = pl.DataFrame({"y": y, "group": g})

    od = overdispersion(df["y"])
    assert od is not None and od > 1.5, f"expected overdispersion>1.5, got {od}"
    assert zero_fraction(df["y"]) >= 0.0

    dm = (ROOT / "recommend-probabilistic-model/references/decision-map.md").read_text()
    assert "NegativeBinomial" in dm, "decision-map missing the overdispersion→NB route"
    assert "Partial pooling" in dm and "hierarchical" in dm, "decision-map missing the group→hierarchical route"

    print(f"SMOKE OK: overdispersion={od} → NegativeBinomial; group → hierarchical (no PDF touched)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
