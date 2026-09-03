"""Tests for diagnose_model.py — run from this directory (bare imports).

cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz \
  --with arviz-stats --with numpy --with xarray python -m pytest -q
"""

import json

import arviz as az
import numpy as np

from diagnose_model import _json_default, check_precision, generate_report


def _idata(n_chains=4, n_draws=500, seed=0, extra=None):
    """Synthetic InferenceData with i.i.d. unit-normal draws (ESS ~ n_chains * n_draws)."""
    rng = np.random.default_rng(seed)
    post = {
        "mu": rng.normal(size=(n_chains, n_draws)),
        "beta": rng.normal(size=(n_chains, n_draws, 2)),
    }
    if extra:
        post.update(extra)
    stats = {"diverging": np.zeros((n_chains, n_draws), dtype=bool)}
    # arviz 1.x from_dict takes ONE dict of groups (the 0.23 kwargs form raises TypeError)
    return az.from_dict({"posterior": post, "sample_stats": stats})


def test_check_precision_iid_draws_give_one_stable_digit():
    prec = check_precision(_idata())
    mu = prec["params"]["mu"]
    # 2000 independent draws -> relative MCSE ~ 1/sqrt(2000) ~ 0.022 -> floor(-log10) == 1
    assert 0.01 < mu["rel_mcse"] < 0.05
    assert mu["stable_digits"] == 1
    assert mu["sd"] > 0 and mu["mcse_mean"] > 0 and mu["mcse_sd"] > 0
    # vector params are flattened the way az.summary labels them
    assert {"beta[0]", "beta[1]"} <= set(prec["params"])
    assert prec["max_rel_mcse_param"] in prec["params"]
    assert prec["min_stable_digits"] == 1


def test_check_precision_skips_constant_params():
    const = {"fixed": np.ones((4, 500))}
    prec = check_precision(_idata(extra=const))
    assert "fixed" not in prec["params"]
    assert "mu" in prec["params"]


def test_check_precision_empty_when_nothing_usable():
    prec = check_precision(az.from_dict({"posterior": {"fixed": np.ones((4, 500))}}))
    assert prec["params"] == {}
    assert prec["max_rel_mcse"] == 0.0
    assert prec["max_rel_mcse_param"] is None
    assert prec["min_stable_digits"] is None


def test_generate_report_carries_precision_and_serializes():
    report = generate_report(_idata())
    assert "precision" in report
    assert report["precision"]["params"]["mu"]["stable_digits"] == 1
    json.dumps(report, default=_json_default)  # must not raise
