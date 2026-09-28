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


def _calibration(diagnosis, mean_coverage_deviation, *, pit_inside, coverage_inside):
    """calibration_check.py-shaped input."""
    return {
        "variable": "y",
        "pit_method": "ppc_pit",
        "assessment": {
            "pit_ecdf_inside_bands": pit_inside,
            "coverage_ecdf_inside_bands": coverage_inside,
            "well_calibrated": pit_inside and coverage_inside,
            "mean_coverage_deviation": mean_coverage_deviation,
            "calibration_diagnosis": diagnosis,
        },
    }


def _calibration_step(steps):
    hits = [s for s in steps if s.startswith("Calibration")]
    assert len(hits) == 1, steps
    return hits[0]


@pytest.mark.parametrize("direction", ["too high", "too low"])
def test_biased_calibration_points_at_the_mean_structure(direction):
    # Right spread, off-centre: the coverage deviation is small, so the rating is "fair".
    cal = _calibration(f"biased (predictions {direction})", -0.0255, pit_inside=False, coverage_inside=True)
    step = _calibration_step(suggest_next_steps(check_diagnostics(calibration=cal)))
    assert f"biased (predictions {direction})" in step
    assert "mean structure" in step
    assert "heavier-tailed" not in step


def test_over_confident_calibration_keeps_its_likelihood_advice():
    cal = _calibration(
        "over-confident (predictions too certain)", -0.3126, pit_inside=False, coverage_inside=False
    )
    step = _calibration_step(suggest_next_steps(check_diagnostics(calibration=cal)))
    assert "likelihood is too narrow" in step
