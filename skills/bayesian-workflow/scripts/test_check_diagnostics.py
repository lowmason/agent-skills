"""Tests for check_diagnostics.py — run from this directory (bare imports).

cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz \
  --with arviz-stats --with numpy --with xarray python -m pytest -q
"""

import pytest

from check_diagnostics import DIVERGENCE_GATE_PCT, check_diagnostics, suggest_next_steps


def _diagnostics(n_div, pct):
    """Minimal diagnose_model-shaped input: only divergences are flagged."""
    return {
        "convergence": {
            "all_ok": False,
            "method": "manual",
            "rhat": {"ok": True, "max": 1.003, "problematic_params": []},
            "ess_bulk": {"ok": True, "min": 900, "problematic_params": []},
            "ess_tail": {"ok": True, "min": 900, "problematic_params": []},
            "divergences": {"count": n_div, "pct": pct, "ok": False},
        },
        "loo": {"computed": False, "error": "no log_likelihood group"},
        "posterior_predictive": {"available": False},
    }


def _divergence_step(steps):
    hits = [s for s in steps if "ivergence" in s]
    assert len(hits) == 1, steps
    return hits[0]


def test_gate_constant_is_one_percent():
    assert DIVERGENCE_GATE_PCT == 1.0


def test_report_carries_divergence_pct():
    report = check_diagnostics(diagnostics=_diagnostics(320, 8.0))
    assert report["convergence"]["divergence_pct"] == 8.0


def test_many_divergences_do_not_suggest_raising_target_accept():
    step = _divergence_step(suggest_next_steps(check_diagnostics(diagnostics=_diagnostics(320, 8.0))))
    assert "8.0%" in step
    assert "Do not raise target_accept_prob" in step
    assert "plot_pair" in step and "Failure signatures" in step


def test_few_divergences_suggest_raising_target_accept_first():
    step = _divergence_step(suggest_next_steps(check_diagnostics(diagnostics=_diagnostics(3, 0.08))))
    assert "raise target_accept_prob to 0.95" in step
    assert "Do not raise" not in step


def test_gate_boundary_at_one_percent_still_raises_target_accept():
    # The gate is a strict `>`, so pct == DIVERGENCE_GATE_PCT is *not* above it.
    step = _divergence_step(suggest_next_steps(check_diagnostics(diagnostics=_diagnostics(40, 1.0))))
    assert "raise target_accept_prob to 0.95" in step
    assert "Do not raise" not in step


def test_no_divergences_no_divergence_step():
    diag = _diagnostics(0, 0.0)
    diag["convergence"]["divergences"]["ok"] = True
    diag["convergence"]["all_ok"] = True
    assert not [s for s in suggest_next_steps(check_diagnostics(diagnostics=diag)) if "ivergence" in s]


HIGH = "biased (predictions too high)"
OVER = "over-confident (predictions too certain)"
UNDER = "under-confident (predictions too uncertain)"
SHAPE = "shape mismatch (neither a shift nor a spread error)"
POOR_OVER, POOR_UNDER = -0.3126, 0.3126  # |deviation| > 0.05 rates calibration poor
FAIR_OVER, FAIR_UNDER = -0.0255, 0.0255  # |deviation| <= 0.05 rates it fair


def _calibration(findings, mean_coverage_deviation):
    """calibration_check.py-shaped input: the four assessment keys this script reads."""
    return {
        "variable": "y",
        "pit_method": "ppc_pit",
        "assessment": {
            "findings": findings,
            "well_calibrated": not findings,
            "mean_coverage_deviation": mean_coverage_deviation,
            "calibration_diagnosis": " and ".join(findings) or "well-calibrated",
        },
    }


def _legacy_calibration(diagnosis, mean_coverage_deviation):
    """A calibration.json written before findings existed: one diagnosis, no findings key."""
    well_calibrated = diagnosis == "well-calibrated"
    return {
        "variable": "y",
        "pit_method": "ppc_pit",
        "assessment": {
            "pit_ecdf_inside_bands": well_calibrated,
            "coverage_ecdf_inside_bands": well_calibrated,
            "well_calibrated": well_calibrated,
            "mean_coverage_deviation": mean_coverage_deviation,
            "calibration_diagnosis": diagnosis,
        },
    }


def _calibration_steps(cal):
    return [s for s in suggest_next_steps(check_diagnostics(calibration=cal)) if s.startswith("Calibration")]


@pytest.mark.parametrize("direction", ["too high", "too low"])
def test_biased_calibration_points_at_the_mean_structure(direction):
    # Right spread, off-centre: the coverage deviation is small, so the rating is "fair".
    (step,) = _calibration_steps(_calibration([f"biased (predictions {direction})"], FAIR_OVER))
    assert f"biased (predictions {direction})" in step
    assert "mean structure" in step
    assert "heavier-tailed" not in step


def test_over_confident_calibration_keeps_its_likelihood_advice():
    (step,) = _calibration_steps(_calibration([OVER], POOR_OVER))
    assert "likelihood is too narrow" in step


def test_under_confident_calibration_keeps_its_prior_advice():
    (step,) = _calibration_steps(_calibration([UNDER], POOR_UNDER))
    assert "predictions are too uncertain" in step


def test_a_fair_over_confident_finding_gets_a_milder_widening_step():
    # Over-confident: the predictive is too narrow, so every remedy must widen it.
    (step,) = _calibration_steps(_calibration([OVER], FAIR_OVER))
    assert "fair but not excellent" in step
    assert "heavier-tailed" in step
    assert "variance component" in step
    assert "tightening priors" not in step
    assert "Tighten" not in step


def test_a_fair_under_confident_finding_gets_a_milder_tightening_step():
    # Under-confident: the predictive is too wide, so every remedy must narrow it.
    (step,) = _calibration_steps(_calibration([UNDER], FAIR_UNDER))
    assert "fair but not excellent" in step
    assert "tighter" in step
    assert "missing predictor" in step
    assert "heavier-tailed" not in step
    assert "StudentT" not in step


def test_over_confidence_after_a_shift_is_re_checked_not_treated():
    # A shift alone lowers interval coverage, so the spread step waits for a re-run.
    biased_step, spread_step = _calibration_steps(_calibration([HIGH, OVER], POOR_OVER))
    assert "mean structure" in biased_step
    assert "re-run calibration_check.py" in spread_step
    assert "likelihood is too narrow" not in spread_step


def test_under_confidence_after_a_shift_keeps_its_spread_step():
    # A shift cannot make intervals too wide, so the spread step stands.
    biased_step, spread_step = _calibration_steps(_calibration([HIGH, UNDER], POOR_UNDER))
    assert "mean structure" in biased_step
    assert "predictions are too uncertain" in spread_step


def test_shape_mismatch_points_at_the_likelihood_shape():
    (step,) = _calibration_steps(_calibration([SHAPE], FAIR_OVER))
    assert "posterior-predictive density overlay" in step
    assert "zero-inflated" in step


def test_an_unknown_finding_gets_the_generic_step():
    # Fair-rated, so it cannot fall into the fair spread step either.
    (step,) = _calibration_steps(_calibration(["a label from a newer calibration_check.py"], FAIR_OVER))
    assert step.startswith("Calibration check failed")


def test_a_well_calibrated_report_adds_no_calibration_step():
    assert _calibration_steps(_calibration([], 0.0012)) == []


def test_findings_are_carried_into_the_report():
    report = check_diagnostics(calibration=_calibration([HIGH, OVER], POOR_OVER))
    assert report["calibration"]["findings"] == [HIGH, OVER]


@pytest.mark.parametrize(
    "diagnosis, findings",
    [(HIGH, [HIGH]), ("well-calibrated", []), ("", [])],
    ids=["one_finding", "well_calibrated", "empty"],
)
def test_a_legacy_calibration_file_falls_back_to_its_diagnosis(diagnosis, findings):
    report = check_diagnostics(calibration=_legacy_calibration(diagnosis, FAIR_OVER))
    assert report["calibration"]["findings"] == findings


def test_a_legacy_over_confident_file_keeps_its_likelihood_advice():
    (step,) = _calibration_steps(_legacy_calibration(OVER, POOR_OVER))
    assert "likelihood is too narrow" in step


def _clean_diagnostics():
    """diagnose_model.py output in which every check ran and passed."""
    return {
        "convergence": {
            "all_ok": True,
            "method": "arviz_stats.diagnose",
            "rhat": {"ok": True, "max": None, "problematic_params": []},
            "ess_bulk": {"ok": True, "min": 1800, "problematic_params": []},
            "ess_tail": {"ok": True, "min": 1700, "problematic_params": []},
            "divergences": {"checked": True, "count": 0, "pct": 0.0, "ok": True},
            "treedepth": {"checked": True, "ok": True, "n_max": 0, "pct": 0.0},
            "bfmi": {"checked": True, "ok": True, "failed_chains": []},
        },
        "loo": {
            "computed": True,
            "elpd": -120.4,
            "se": 6.2,
            "p_loo": 3.1,
            "pareto_k": {"max": 0.31, "good_k": 0.7, "n_bad": 0, "n_high": 0, "n_nonfinite": 0, "ok": True},
        },
        "posterior_predictive": {"available": True},
        "precision": {
            "params": {"mu": {"rel_mcse": 0.021, "stable_digits": 1}},
            "max_rel_mcse": 0.021,
            "max_rel_mcse_param": "mu",
            "min_stable_digits": 1,
        },
    }


WELL_CALIBRATED = _calibration([], 0.0012)
LOW_PSENSE = {"prior": {"mu": 0.01}, "likelihood": {"mu": 0.02}}


def _steps(diagnostics, calibration=WELL_CALIBRATED, psense=LOW_PSENSE):
    return suggest_next_steps(
        check_diagnostics(diagnostics=diagnostics, calibration=calibration, psense=psense)
    )


def _one_step(steps, prefix):
    hits = [s for s in steps if s.startswith(prefix)]
    assert len(hits) == 1, steps
    return hits[0]


def _proceeds(steps):
    return any("proceed to interpretation" in s for s in steps)


def test_a_clean_report_gets_the_all_clear_alone():
    # The control: each test below changes one input from these.
    steps = _steps(_clean_diagnostics())
    assert len(steps) == 1 and _proceeds(steps), steps


def test_a_failing_mcse_gets_a_precision_step_not_the_all_clear():
    diag = _clean_diagnostics()
    diag["precision"].update(max_rel_mcse=0.058, max_rel_mcse_param="beta[1]")
    steps = _steps(diag)
    step = _one_step(steps, "Monte Carlo precision")
    assert "0.058 on beta[1]" in step and "0.05" in step
    assert not _proceeds(steps)


def test_an_mcse_at_the_bar_passes():
    diag = _clean_diagnostics()
    diag["precision"]["max_rel_mcse"] = 0.05
    assert _proceeds(_steps(diag))


@pytest.mark.parametrize(
    "precision",
    [None, {"params": {}, "max_rel_mcse": 0.0, "max_rel_mcse_param": None, "min_stable_digits": None}],
    ids=["no_block", "no_usable_param"],
)
def test_precision_that_never_ran_is_named_not_passed(precision):
    diag = _clean_diagnostics()
    if precision is None:
        del diag["precision"]
    else:
        diag["precision"] = precision
    steps = _steps(diag)
    assert "diagnose_model.py" in _one_step(steps, "Monte Carlo precision was not checked")
    assert not _proceeds(steps)


@pytest.mark.parametrize("loo", ["error", "no_section"])
def test_a_loo_that_never_ran_quotes_its_remedy(loo):
    diag = _clean_diagnostics()
    if loo == "error":
        diag["loo"] = {
            "computed": False,
            "error": "No log_likelihood group in the InferenceData. Rebuild it with "
            "az.from_numpyro(mcmc, log_likelihood=True, ...) and re-save the netCDF.",
        }
    else:
        del diag["loo"]
    steps = _steps(diag)
    assert "log_likelihood" in _one_step(steps, "LOO was not computed")
    assert not _proceeds(steps)


def test_without_calibration_there_is_no_all_clear():
    steps = _steps(_clean_diagnostics(), calibration=None)
    assert "--calibration" in _one_step(steps, "Calibration was not checked")
    assert not _proceeds(steps)


@pytest.mark.parametrize("psense", [None, {}], ids=["not_passed", "empty"])
def test_the_all_clear_names_prior_sensitivity_when_it_did_not_run(psense):
    steps = _steps(_clean_diagnostics(), psense=psense)
    assert _proceeds(steps)
    assert "prior sensitivity" in _one_step(steps, "Not checked:")


def test_a_rating_that_did_not_pass_blocks_the_all_clear_even_without_a_step():
    # A legacy calibration file that rates fair but names no finding adds no step.
    steps = _steps(_clean_diagnostics(), calibration=_legacy_calibration("", FAIR_OVER))
    assert "calibration (fair)" in _one_step(steps, "No specific next step applies")
    assert not _proceeds(steps)


def test_no_diagnostics_means_no_all_clear():
    steps = _steps(None)
    assert "convergence (not run)" in _one_step(steps, "No specific next step applies")
    assert not _proceeds(steps)


def _report_and_steps(diag):
    report = check_diagnostics(diagnostics=diag, calibration=WELL_CALIBRATED, psense=LOW_PSENSE)
    return report, suggest_next_steps(report)


@pytest.mark.parametrize("convergence", [None, {}], ids=["no_section", "empty_section"])
def test_convergence_that_never_ran_is_named_not_passed(convergence):
    # diagnose_model.py always writes the section; a hand-edited or foreign file may not.
    diag = _clean_diagnostics()
    if convergence is None:
        del diag["convergence"]
    else:
        diag["convergence"] = convergence
    report, steps = _report_and_steps(diag)
    assert report["convergence"]["rating"] == "not computed"
    assert report["summary"]["convergence"] == "Convergence diagnostics: not computed."
    assert "diagnose_model.py" in _one_step(steps, "Convergence was not checked")
    assert not _proceeds(steps)


def test_tree_depth_saturation_gets_a_step_not_the_all_clear():
    diag = _clean_diagnostics()
    diag["convergence"].update(all_ok=False, treedepth={"checked": True, "ok": False, "n_max": 8000, "pct": 100.0})
    report, steps = _report_and_steps(diag)
    step = _one_step(steps, "Tree depth hit max_tree_depth")
    assert "100.0%" in step and "8000" in step
    assert "treedepth saturation" in report["summary"]["convergence"]
    assert "some parameters" not in report["summary"]["convergence"]
    assert not _proceeds(steps)


def test_low_e_bfmi_gets_a_step_not_the_all_clear():
    diag = _clean_diagnostics()
    diag["convergence"].update(all_ok=False, bfmi={"checked": True, "ok": False, "failed_chains": [0, 2]})
    report, steps = _report_and_steps(diag)
    step = _one_step(steps, "E-BFMI is low")
    assert "chain(s) 0, 2" in step and "plot_energy" in step
    assert "low E-BFMI" in report["summary"]["convergence"]
    assert not _proceeds(steps)


@pytest.mark.parametrize(
    "block, label",
    [("treedepth", "tree depth"), ("bfmi", "E-BFMI"), ("divergences", "divergences")],
)
def test_a_sampler_check_that_never_ran_is_named_not_passed(block, label):
    diag = _clean_diagnostics()
    diag["convergence"][block] = {"checked": False}
    report, steps = _report_and_steps(diag)
    assert _proceeds(steps)
    assert label in _one_step(steps, "Not checked:")
    assert f"not checked: {label}" in report["summary"]["convergence"]


def test_a_missing_sampler_block_counts_as_not_checked():
    diag = _clean_diagnostics()
    del diag["convergence"]["treedepth"]
    assert "tree depth" in _one_step(_steps(diag), "Not checked:")


def test_a_sampler_block_without_a_checked_key_counts_as_checked():
    # A diagnostics.json written before checked existed.
    diag = _clean_diagnostics()
    diag["convergence"]["treedepth"] = {"ok": True, "n_max": 0, "pct": 0.0}
    steps = _steps(diag)
    assert len(steps) == 1 and _proceeds(steps), steps


def test_an_unchecked_divergence_count_is_not_reported_as_zero():
    diag = _clean_diagnostics()
    diag["convergence"]["divergences"] = {"checked": False}
    assert "no divergences" not in check_diagnostics(diagnostics=diag)["summary"]["convergence"]


def test_the_convergence_summary_names_parameters_and_sampler_flags():
    diag = _clean_diagnostics()
    diag["convergence"].update(
        all_ok=False,
        rhat={"ok": False, "max": 1.02, "problematic_params": ["a"]},
        treedepth={"checked": True, "ok": False, "n_max": 4000, "pct": 100.0},
    )
    report, _ = _report_and_steps(diag)
    assert "flags on a; max treedepth saturation" in report["summary"]["convergence"]


def _with_pareto_k(**pareto_k):
    diag = _clean_diagnostics()
    diag["loo"]["pareto_k"] = pareto_k
    return diag


def test_pareto_k_between_good_k_and_0_7_asks_for_more_draws():
    # good_k is about 0.656 at S = 800 draws, loo's exploring size here.
    report, steps = _report_and_steps(
        _with_pareto_k(max=0.68, good_k=0.6555, n_bad=3, n_high=0, n_nonfinite=0, ok=False)
    )
    assert report["loo"]["rating"] == "fair"
    step = _one_step(steps, "LOO Pareto-k is above the sample-size threshold 0.6555")
    assert "3 observation(s)" in step and "more draws" in step
    assert not _proceeds(steps)


def test_the_pareto_k_threshold_is_printed_unrounded():
    # good_k is 0.6971 at S = 2,000 (4 x 500): "0.70" would put a point at k 0.699 above 0.70.
    report, steps = _report_and_steps(
        _with_pareto_k(max=0.699, good_k=0.6971, n_bad=1, n_high=0, n_nonfinite=0, ok=False)
    )
    assert report["loo"]["rating"] == "fair"
    step = _one_step(steps, "LOO Pareto-k is above the sample-size threshold 0.6971")
    assert "1 observation(s)" in step
    assert not _proceeds(steps)


def test_pareto_k_above_0_7_names_the_remedies():
    report, steps = _report_and_steps(
        _with_pareto_k(max=0.92, good_k=0.7, n_bad=2, n_high=2, n_nonfinite=0, ok=False)
    )
    assert report["loo"]["rating"] == "poor"
    step = _one_step(steps, "LOO Pareto-k > 0.7 for 2 observation(s)")
    for remedy in ("azs.reloo", "azs.loo_kfold", "azs.loo_moment_match", "azs.SamplingWrapper"):
        assert remedy in step


def test_the_retired_0_5_band_no_longer_flags():
    report, steps = _report_and_steps(
        _with_pareto_k(max=0.62, good_k=0.7, n_bad=0, n_high=0, n_nonfinite=0, ok=True)
    )
    assert report["loo"]["rating"] == "excellent"
    assert len(steps) == 1 and _proceeds(steps), steps


def test_a_diagnostics_file_without_good_k_reads_n_bad_as_above_0_7():
    # Written before good_k existed: n_bad then counted only k > 0.7.
    report, steps = _report_and_steps(
        _with_pareto_k(max=0.81, n_bad=1, n_marginal=2, n_nonfinite=0, ok=False)
    )
    assert report["loo"]["rating"] == "poor"
    assert "azs.reloo" in _one_step(steps, "LOO Pareto-k > 0.7 for 1 observation(s)")
