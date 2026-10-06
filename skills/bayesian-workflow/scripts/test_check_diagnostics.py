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
