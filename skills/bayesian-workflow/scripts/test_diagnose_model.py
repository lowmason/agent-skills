"""Tests for diagnose_model.py — run from this directory (bare imports).

cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz \
  --with arviz-stats --with numpy --with xarray python -m pytest -q
"""

import json

import arviz as az
import numpy as np
import pytest

import check_diagnostics as cd
import diagnose_model
from diagnose_model import _json_default, check_precision, generate_report


def _idata(n_chains=4, n_draws=500, seed=0, extra=None, stats=None):
    """Synthetic InferenceData with i.i.d. unit-normal draws (ESS ~ n_chains * n_draws).

    ``stats`` replaces the default sample_stats, which hold only ``diverging``.
    """
    rng = np.random.default_rng(seed)
    post = {
        "mu": rng.normal(size=(n_chains, n_draws)),
        "beta": rng.normal(size=(n_chains, n_draws, 2)),
    }
    if extra:
        post.update(extra)
    if stats is None:
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


def _ar1(n_chains=4, n_draws=500, seed=7, rho=0.97):
    """Stationary AR(1) draws — unit marginal sd, but ESS far below n_chains * n_draws."""
    rng = np.random.default_rng(seed)
    noise = rng.normal(size=(n_chains, n_draws)) * np.sqrt(1 - rho**2)
    x = np.empty((n_chains, n_draws))
    x[:, 0] = rng.normal(size=n_chains)
    for t in range(1, n_draws):
        x[:, t] = rho * x[:, t - 1] + noise[:, t]
    return x


def test_check_precision_names_the_least_precise_parameter():
    prec = check_precision(_idata(extra={"sticky": _ar1()}))
    sticky, mu = prec["params"]["sticky"], prec["params"]["mu"]
    # rho=0.97 -> relative MCSE ~ 0.2, an order of magnitude worse than the i.i.d. params
    assert sticky["rel_mcse"] > 0.1 > mu["rel_mcse"]
    assert sticky["stable_digits"] == 0 and mu["stable_digits"] == 1
    # the *identity* of the limiting parameter, not just membership in the table
    assert prec["max_rel_mcse_param"] == "sticky"
    assert prec["min_stable_digits"] == 0


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


PASSING_PRECISION = {
    "params": {"mu": {"rel_mcse": 0.02, "stable_digits": 1}},
    "max_rel_mcse": 0.02,
    "max_rel_mcse_param": "mu",
    "min_stable_digits": 1,
}


def _stub_checks(monkeypatch, **results):
    """Stub generate_report's four checks with passing results, overridden by ``results``."""
    passing = {
        "check_convergence": {"all_ok": True},
        "check_loo": {"computed": True, "pareto_k": {"ok": True}},
        "check_posterior_predictive": {"available": True},
        "check_precision": PASSING_PRECISION,
    }
    passing.update(results)
    for name, result in passing.items():
        monkeypatch.setattr(diagnose_model, name, lambda idata, result=result: result)


def test_report_overall_passes_when_every_check_passes(monkeypatch):
    # The control: each test below changes one check from these.
    _stub_checks(monkeypatch)
    overall = generate_report(None)["overall"]
    assert overall["ok"] and overall["recommendation"] == "Model is ready for interpretation."


def test_report_overall_flags_a_failing_mcse(monkeypatch):
    _stub_checks(monkeypatch, check_precision={**PASSING_PRECISION, "max_rel_mcse": 0.058})
    overall = generate_report(None)["overall"]
    assert not overall["ok"]
    assert any("0.058 on mu" in issue for issue in overall["issues"]), overall


def test_report_overall_flags_a_loo_that_never_ran(monkeypatch):
    error = "No log_likelihood group in the InferenceData. Rebuild it with az.from_numpyro(...)."
    _stub_checks(monkeypatch, check_loo={"computed": False, "error": error})
    overall = generate_report(None)["overall"]
    assert not overall["ok"]
    assert any(issue.startswith("LOO not computed") and error in issue for issue in overall["issues"]), overall


def test_the_two_scripts_share_their_thresholds():
    assert diagnose_model.REL_MCSE_OK == cd.REL_MCSE_OK


CALM = np.zeros((4, 500), dtype=bool)
SATURATED = np.ones((4, 500), dtype=bool)


@pytest.fixture(params=[True, False], ids=["diagnose", "fallback"])
def both_paths(request, monkeypatch):
    """Run check_convergence on the arviz_stats.diagnose path, then on the manual fallback."""
    monkeypatch.setattr(diagnose_model, "HAS_DIAGNOSE", request.param)
    return request.param


@pytest.mark.parametrize("flag", ["reached_max_tree_depth", "reached_max_treedepth"], ids=["numpyro", "cmdstan"])
def test_a_saturated_run_fails_tree_depth_on_both_paths(both_paths, flag):
    conv = diagnose_model.check_convergence(_idata(stats={"diverging": CALM, flag: SATURATED}))
    assert conv["treedepth"] == {"checked": True, "ok": False, "n_max": 2000, "pct": 100.0}
    assert conv["all_ok"] is False


def test_a_calm_numpyro_run_passes_tree_depth(both_paths):
    conv = diagnose_model.check_convergence(_idata(stats={"diverging": CALM, "reached_max_tree_depth": CALM}))
    assert conv["treedepth"] == {"checked": True, "ok": True, "n_max": 0, "pct": 0.0}
    assert conv["all_ok"] is True


def test_no_tree_depth_flag_is_marked_not_checked(both_paths):
    conv = diagnose_model.check_convergence(_idata())
    assert conv["treedepth"] == {"checked": False}
    assert conv["all_ok"] is True


def test_no_energy_stat_marks_e_bfmi_not_checked(both_paths):
    assert diagnose_model.check_convergence(_idata())["bfmi"] == {"checked": False}


def test_an_energy_stat_gives_a_checked_e_bfmi_block():
    # Only the arviz_stats.diagnose path computes E-BFMI; i.i.d. energy is far above 0.3.
    energy = np.random.default_rng(1).normal(size=(4, 500))
    conv = diagnose_model.check_convergence(_idata(stats={"diverging": CALM, "energy": energy}))
    assert conv["bfmi"] == {"checked": True, "ok": True, "failed_chains": []}


def test_a_diverging_stat_gives_a_checked_divergence_block(both_paths):
    assert diagnose_model.check_convergence(_idata())["divergences"] == {
        "checked": True, "count": 0, "pct": 0.0, "ok": True,
    }


def test_no_diverging_stat_marks_divergences_not_checked(both_paths):
    conv = diagnose_model.check_convergence(_idata(stats={"lp": np.zeros((4, 500))}))
    assert conv["divergences"] == {"checked": False}
    assert conv["all_ok"] is True
