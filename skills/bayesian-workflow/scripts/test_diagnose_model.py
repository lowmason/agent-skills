"""Tests for diagnose_model.py — run from this directory (bare imports).

cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz \
  --with arviz-stats --with numpy --with xarray python -m pytest -q
"""

import json
import math

import arviz as az
import numpy as np
import pytest

import check_diagnostics as cd
import diagnose_model
from diagnose_model import _json_default, check_precision, generate_report
# The reader's inputs, shared with its own tests; check_diagnostics reads only the assessment.
from test_check_diagnostics import LOW_PSENSE, WELL_CALIBRATED

# Only the arviz_stats.diagnose path computes E-BFMI, so its tests skip without it.
needs_diagnose = pytest.mark.skipif(
    not diagnose_model.HAS_DIAGNOSE, reason="E-BFMI needs arviz_stats.diagnose (arviz-stats >= 1.0)"
)

CLASSIC_ARVIZ = az.__version__.startswith("0.")


def _from_groups(groups):
    """InferenceData from a dict of groups, on classic ArviZ 0.23 and on 1.x alike.

    arviz 1.x from_dict takes ONE dict of groups. 0.23 takes each group as a keyword
    and reads a positional dict as the posterior, which gives an object-dtype array.
    """
    if CLASSIC_ARVIZ:
        return az.from_dict(**groups)
    return az.from_dict(groups)


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
    return _from_groups({"posterior": post, "sample_stats": stats})


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


def _posterior_only(post):
    """InferenceData holding only ``post``, on classic ArviZ 0.23 and on 1.x alike."""
    return _from_groups({"posterior": post})


def test_check_precision_keeps_a_small_scale_parameter():
    # Classic ArviZ 0.23's az.summary rounds to three decimals by default, so sd 0.01
    # showed mcse_mean 0.000 and the parameter was skipped. Run on both stacks.
    small = 0.01 * np.random.default_rng(0).normal(size=(4, 500))
    prec = check_precision(_posterior_only({"small": small}))
    assert "small" in prec["params"], prec
    assert 0.009 < prec["params"]["small"]["sd"] < 0.011
    # 2000 i.i.d. draws: relative MCSE ~ 1/sqrt(2000), the same digit as a unit-scale parameter
    assert 0.01 < prec["params"]["small"]["rel_mcse"] < 0.05
    assert prec["params"]["small"]["stable_digits"] == 1


def test_check_precision_empty_when_nothing_usable():
    prec = check_precision(_posterior_only({"fixed": np.ones((4, 500))}))
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


def test_report_overall_prints_the_pareto_k_threshold_unrounded(monkeypatch):
    # good_k is 0.6971 at S = 2,000 (4 x 500): ":.2f" printed it as 0.70.
    pareto_k = {"ok": False, "good_k": 0.6971, "n_bad": 1, "n_nonfinite": 0}
    _stub_checks(monkeypatch, check_loo={"computed": True, "pareto_k": pareto_k})
    overall = generate_report(None)["overall"]
    assert not overall["ok"]
    assert any("1 observation(s) with Pareto k above 0.6971" in issue for issue in overall["issues"]), overall


def test_the_two_scripts_share_their_thresholds():
    assert diagnose_model.REL_MCSE_OK == cd.REL_MCSE_OK
    assert diagnose_model.PARETO_K_MAX == cd.PARETO_K_MAX


CALM = np.zeros((4, 500), dtype=bool)
SATURATED = np.ones((4, 500), dtype=bool)


@pytest.fixture(params=[True, False], ids=["diagnose", "fallback"])
def both_paths(request, monkeypatch):
    """Run check_convergence on the arviz_stats.diagnose path, then on the manual fallback.

    The diagnose param skips where the module found no arviz_stats.diagnose (classic ArviZ 0.23).
    """
    if request.param and not diagnose_model.HAS_DIAGNOSE:
        pytest.skip("the diagnose path needs arviz_stats.diagnose (arviz-stats >= 1.0)")
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


@needs_diagnose
def test_an_energy_stat_gives_a_checked_e_bfmi_block():
    # Only the arviz_stats.diagnose path computes E-BFMI; i.i.d. energy is far above 0.3.
    energy = np.random.default_rng(1).normal(size=(4, 500))
    conv = diagnose_model.check_convergence(_idata(stats={"diverging": CALM, "energy": energy}))
    assert conv["bfmi"] == {"checked": True, "ok": True, "failed_chains": []}


@needs_diagnose
def test_a_random_walk_energy_fails_e_bfmi_on_its_chain():
    # A random-walk energy on chain 0 gives E-BFMI about 0.02, far below 0.3.
    rng = np.random.default_rng(1)
    energy = rng.normal(size=(4, 500))
    energy[0] = np.cumsum(rng.normal(size=500))
    conv = diagnose_model.check_convergence(_idata(stats={"diverging": CALM, "energy": energy}))
    assert conv["bfmi"] == {"checked": True, "ok": False, "failed_chains": [0]}
    assert conv["all_ok"] is False


def test_no_sample_stats_group_marks_every_sampler_check_not_checked(both_paths):
    conv = diagnose_model.check_convergence(_posterior_only({"mu": np.random.default_rng(2).normal(size=(4, 500))}))
    assert conv["divergences"] == conv["treedepth"] == conv["bfmi"] == {"checked": False}
    assert conv["rhat"]["ok"] and conv["ess_bulk"]["ok"] and conv["ess_tail"]["ok"]
    assert conv["all_ok"] is True


def test_a_clean_run_carries_its_max_r_hat_on_both_paths(both_paths):
    # arviz_stats.diagnose keeps only the flagged parameters' R-hat values, so on a
    # clean run the writer must compute the maximum itself for the report's row.
    rhat = diagnose_model.check_convergence(_idata())["rhat"]
    assert rhat["ok"] is True and rhat["problematic_params"] == []
    assert isinstance(rhat["max"], float) and 0.99 < rhat["max"] <= 1.01, rhat


def _offset_chains(offset=0.15, seed=0):
    """Unit-normal chains centred, then shifted by +/-``offset``: raw R-hat 1.0113."""
    z = np.random.default_rng(seed).normal(size=(4, 500))
    z -= z.mean(axis=1, keepdims=True)
    return z + offset * np.array([1.0, -1.0, 1.0, -1.0])[:, None]


def test_an_r_hat_just_above_1_01_fails_on_the_fallback_path(monkeypatch):
    # Classic ArviZ 0.23's az.summary rounds R-hat to two decimals, so 1.0113 read as
    # 1.01 and passed the <= 1.01 gate. ArviZ 1.x's summary is unrounded already, so
    # only the 0.23 run (the pinned command in the commit) fails without round_to="none".
    monkeypatch.setattr(diagnose_model, "HAS_DIAGNOSE", False)
    idata = _posterior_only({"drift": _offset_chains()})
    raw = float(az.rhat(idata)["drift"])
    assert 1.01 < raw < 1.015, raw  # the premise: two-decimal rounding gives 1.01
    rhat = diagnose_model.check_convergence(idata)["rhat"]
    assert rhat["ok"] is False and rhat["problematic_params"] == ["drift"], rhat
    assert rhat["max"] == pytest.approx(raw), rhat


def test_a_diverging_stat_gives_a_checked_divergence_block(both_paths):
    assert diagnose_model.check_convergence(_idata())["divergences"] == {
        "checked": True, "count": 0, "pct": 0.0, "ok": True,
    }


def test_no_diverging_stat_marks_divergences_not_checked(both_paths):
    conv = diagnose_model.check_convergence(_idata(stats={"lp": np.zeros((4, 500))}))
    assert conv["divergences"] == {"checked": False}
    assert conv["all_ok"] is True


def _complete_idata(**stats):
    """An InferenceData on which every check runs and passes: LOO, PPC and all three
    sampler checks. A keyword replaces one sample stat; None drops it."""
    rng = np.random.default_rng(3)
    y = rng.normal(size=20)
    mu = rng.normal(size=(4, 500))
    sample_stats = {"diverging": CALM, "reached_max_tree_depth": CALM, "energy": rng.normal(size=(4, 500))}
    sample_stats.update(stats)
    return _from_groups({
        "posterior": {"mu": mu},
        "sample_stats": {k: v for k, v in sample_stats.items() if v is not None},
        # a narrow log-likelihood keeps every Pareto k small
        "log_likelihood": {"y": -0.5 * (y - 0.1 * mu[..., None]) ** 2 - 0.5 * np.log(2 * np.pi)},
        "posterior_predictive": {"y": rng.normal(size=(4, 500, 20))},
        "observed_data": {"y": y},
    })


def _read_back(idata):
    """diagnose_model's report read by check_diagnostics, as step 3 of SKILL.md's pipeline does."""
    report = cd.check_diagnostics(diagnostics=generate_report(idata), calibration=WELL_CALIBRATED, psense=LOW_PSENSE)
    return report, cd.suggest_next_steps(report)


def test_a_complete_clean_run_reads_back_as_the_all_clear():
    # The control for the two tests below.
    _, steps = _read_back(_complete_idata())
    assert len(steps) == 1 and "proceed to interpretation" in steps[0], steps


def test_a_complete_clean_run_on_the_fallback_path_reads_back_with_e_bfmi_not_checked(monkeypatch):
    # The manual path end to end: writer, then reader. It never computes E-BFMI,
    # so the all-clear must name it as not checked rather than pass it.
    monkeypatch.setattr(diagnose_model, "HAS_DIAGNOSE", False)
    report, steps = _read_back(_complete_idata())
    assert report["convergence"]["rating"] == "excellent"
    assert "proceed to interpretation" in steps[0], steps
    assert len(steps) == 2 and steps[1].startswith("Not checked: E-BFMI"), steps


def test_a_saturated_numpyro_run_reads_back_as_saturation():
    report, steps = _read_back(_complete_idata(reached_max_tree_depth=SATURATED))
    assert any(s.startswith("Tree depth hit max_tree_depth on 100.0%") for s in steps), steps
    assert not any("proceed to interpretation" in s for s in steps)
    assert "treedepth saturation" in report["summary"]["convergence"]


def test_a_run_without_the_tree_depth_flag_reads_back_as_not_checked():
    report, steps = _read_back(_complete_idata(reached_max_tree_depth=None))
    assert "proceed to interpretation" in steps[0]
    assert any(s.startswith("Not checked: tree depth") for s in steps), steps
    assert "not checked: tree depth" in report["summary"]["convergence"]


def _bursty_tail_draws(n_chains=4, n_draws=500, seed=26, share=0.1, length=20, shift=4.0):
    """Draws whose extremes come in bursts while the centre mixes freely.

    A two-state Markov chain switches bursts on (stationary share ``share``, mean
    length ``length``). Each draw in a burst is a unit normal pushed out by
    ``shift`` times an i.i.d. random sign. The sign keeps the bulk ESS near
    n_chains * n_draws, and the bursts pull the tail ESS under 100 * n_chains.
    At the defaults bulk ESS is 2177, tail ESS 306 and R-hat 1.0031 (seed 26),
    with tail ESS on the 0.05 and 0.95 quantiles. On the 0.11 and 0.89 quantiles,
    arviz-stats 1.3.3's unpinned default, the tail ESS would be 729 and pass.
    """
    rng = np.random.default_rng(seed)
    leave = 1 / length
    enter = share * leave / (1 - share)
    in_burst = np.zeros((n_chains, n_draws))
    in_burst[:, 0] = rng.random(n_chains) < share
    u = rng.random((n_chains, n_draws))
    for t in range(1, n_draws):
        in_burst[:, t] = np.where(in_burst[:, t - 1] == 1, u[:, t] >= leave, u[:, t] < enter)
    sign = rng.choice([-1.0, 1.0], size=(n_chains, n_draws))
    return rng.normal(size=(n_chains, n_draws)) + shift * in_burst * sign


def test_low_tail_ess_with_passing_bulk_ess_fails_all_ok_on_both_paths(both_paths):
    idata = _idata(extra={"bursty": _bursty_tail_draws()})
    if both_paths:
        # The premise: arviz_stats.diagnose rates this run clean, so only the tail ESS block can fail it.
        has_errors, _ = diagnose_model.azs.diagnose(idata, return_diagnostics=True, show_diagnostics=False)
        assert not has_errors
    conv = diagnose_model.check_convergence(idata)
    # R-hat must pass too, or all_ok below could fail on R-hat instead of the tail ESS.
    assert conv["rhat"]["ok"] is True
    assert conv["ess_bulk"]["ok"] is True
    assert conv["ess_tail"]["ok"] is False
    assert conv["ess_tail"]["problematic_params"] == ["bursty"]
    assert conv["all_ok"] is False
    # check_diagnostics rates "excellent" on all_ok, so the writer's flag must not stay True.
    diagnostics = generate_report(_complete_idata())
    diagnostics["convergence"] = conv
    report = cd.check_diagnostics(diagnostics=diagnostics, calibration=WELL_CALIBRATED, psense=LOW_PSENSE)
    steps = cd.suggest_next_steps(report)
    assert not any("proceed to interpretation" in s for s in steps), steps
    assert any(s.startswith("R-hat or ESS flags on bursty") for s in steps), steps


@pytest.mark.parametrize("ci_prob", [0.89, 0.94])
def test_tail_ess_reads_the_5_and_95_percent_quantiles_whatever_the_ci_prob(both_paths, ci_prob):
    # Without a prob, arviz-stats 1.3.3 takes the tail quantiles from stats.ci_prob:
    # 0.89 gave 0.11 and 0.89, and 0.94 gave 0.06 and 0.94. A display setting must not
    # move the gate. 0.95 is left out: unpinned, it already gave 0.05 and 0.95.
    idata = _idata(extra={"bursty": _bursty_tail_draws()})
    expected = min(float(az.ess(idata, method="quantile", prob=q)["bursty"]) for q in (0.05, 0.95))
    with az.rc_context({"stats.ci_prob": ci_prob}):
        conv = diagnose_model.check_convergence(idata)
    assert conv["ess_tail"]["min"] == int(expected), conv["ess_tail"]
    assert conv["ess_tail"]["problematic_params"] == ["bursty"], conv["ess_tail"]


def test_the_pareto_k_threshold_follows_loo():
    assert diagnose_model.pareto_k_threshold(4000) == 0.7
    assert diagnose_model.pareto_k_threshold(800) == pytest.approx(1 - 1 / math.log10(800))
    assert 0.655 < diagnose_model.pareto_k_threshold(800) < 0.656


def test_pareto_k_counts_against_the_sample_size_threshold():
    k = [0.2, 0.68, 0.9, float("nan")]
    assert diagnose_model.summarize_pareto_k(k, 800) == {
        "max": 0.9, "good_k": 0.6555, "n_bad": 2, "n_high": 1, "n_nonfinite": 1, "ok": False,
    }
    assert diagnose_model.summarize_pareto_k(k, 4000) == {
        "max": 0.9, "good_k": 0.7, "n_bad": 1, "n_high": 1, "n_nonfinite": 1, "ok": False,
    }


def test_check_loo_carries_good_k_and_drops_the_0_5_band():
    pareto_k = diagnose_model.check_loo(_complete_idata())["pareto_k"]
    assert pareto_k["good_k"] == round(diagnose_model.pareto_k_threshold(2000), 4)
    assert "n_high" in pareto_k and "n_marginal" not in pareto_k
