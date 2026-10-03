"""
Calibration assessment for Bayesian models.

Computes coverage calibration, PIT ECDFs, and generates calibration plots
using ArviZ 1.0+ (arviz_plots). Supports both PPC-PIT and LOO-PIT.

Usage:
    python calibration_check.py --idata path/to/inference_data.nc
    python calibration_check.py --idata path/to/inference_data.nc --var-name obs --save-plots
    python calibration_check.py --idata path/to/inference_data.nc --loo-pit --save-plots
    python calibration_check.py --idata path/to/inference_data.nc --save-plots --plot-dir plots/
"""

import argparse
import json
import math
import os
import sys
import warnings
from typing import NoReturn

import numpy as np

try:
    import arviz_plots as azp
    import arviz_stats as azs
    import xarray as xr
    from arviz_base import convert_to_datatree
    from arviz_stats.ecdf_utils import ecdf_pit
    from scipy import stats

    # `difference_ecdf_pit` is a statistics helper; its stable home is
    # arviz_stats.ecdf_utils on arviz-stats >= 1.0 (both PyMC-5 and PyMC-6 stacks).
    # arviz_plots <= 1.0 also re-exported it under arviz_plots.plots.ppc_pit_plot,
    # but arviz_plots 1.1 removed that re-export — import from arviz_stats, and only
    # fall back to the old plots path for the older layout.
    try:
        from arviz_stats.ecdf_utils import difference_ecdf_pit
    except ImportError:  # pragma: no cover - pre-1.0 arviz_stats layout
        from arviz_plots.plots.ppc_pit_plot import difference_ecdf_pit
except ImportError:
    print(
        json.dumps(
            {
                "error": (
                    "arviz_plots and arviz_base are required. "
                    "Install with: pip install arviz-plots arviz-base"
                )
            }
        )
    )
    sys.exit(1)

warnings.filterwarnings("ignore", category=FutureWarning)

# Monte Carlo draws behind each simultaneous confidence band.
BAND_SIMULATIONS = 1000

# ArviZ's own default seed for PIT tie-breaking.
PIT_SEED = 214

# The five calibration findings, centre first.
BIASED_HIGH = "biased (predictions too high)"
BIASED_LOW = "biased (predictions too low)"
OVER_CONFIDENT = "over-confident (predictions too certain)"
UNDER_CONFIDENT = "under-confident (predictions too uncertain)"
SHAPE_MISMATCH = "shape mismatch (neither a shift nor a spread error)"
FINDINGS = (BIASED_HIGH, BIASED_LOW, OVER_CONFIDENT, UNDER_CONFIDENT, SHAPE_MISMATCH)


def pit_values(dt, var_name, use_loo, seed=PIT_SEED):
    """PIT values of `var_name`, pooled over all its observation dims into one 1-D array.

    PPC-PIT is a seeded rank PIT, randomized within its cell. With S posterior-predictive
    draws (chain × draw), an observation's rank is k = #(draws < y) + ⌊U·(#(draws = y) + 1)⌋
    and its PIT is u = (k + V)/(S + 1), where U and V are U(0, 1) draws from
    np.random.default_rng(seed). When y and its draws are exchangeable, k is uniform on
    {0, …, S}, so u is exactly U(0, 1). The floor term randomizes ties, so discrete data
    stays correct.

    A grid PIT breaks pot_c's coverage test. arviz-plots' plot_ppc_pit draws the
    empirical k/S in the centre, so when exactly S/2 of an even S draws fall below y,
    u = 0.5 and the coverage value 2|u − 0.5| is exactly 0. pot_c reads a smallest
    coverage value of 0 as impossible, and its p-value collapses on a calibrated model.
    Spreading each PIT over its 1/(S + 1) cell keeps u off 0, 0.5 and 1.

    LOO-PIT is arviz_stats.loo_pit(..., pareto_pit=True): the values plot_loo_pit draws,
    which Pareto smoothing keeps off 0 and 1.
    """
    if use_loo:
        return azs.loo_pit(dt, var_names=var_name, pareto_pit=True)[var_name].values.ravel()
    predicted = dt["posterior_predictive"][var_name]
    observed = dt["observed_data"][var_name]
    below = (predicted < observed).sum(("chain", "draw")).values.ravel()
    ties = (predicted == observed).sum(("chain", "draw")).values.ravel()
    n_draws = predicted.sizes["chain"] * predicted.sizes["draw"]
    rng = np.random.default_rng(seed)
    rank = below + np.floor(rng.uniform(size=below.shape) * (ties + 1))
    return (rank + rng.uniform(size=below.shape)) / (n_draws + 1)


def _pot_c_p_value(values):
    """The pot_c uniformity-test p-value of `values`.

    Read by index, never by unpacking: arviz-stats 1.1 returns (p, shapley) and 1.3
    returns (p, shapley, shapley_unsorted).
    """
    result = xr.DataArray(values, dims=["pit"]).azstats.uniformity_test(dim=["pit"], method="pot_c")
    return float(result[0])


def assess_pit(pit, ci_prob=0.99):
    """Judge PIT values with pot_c and name every failing calibration component.

    With α = 1 − ci_prob and coverage levels c = 2|u − 0.5|, the PIT test and the
    coverage test each pass when their pot_c p-value is at least α. Findings, centre
    first:

    1. Location. The PIT test failed and |location_t| exceeds the Student-t quantile at
       1 − α/2 on n − 1 df, where location_t = (mean(u) − 0.5)/(sd(u)/√n). A negative
       location_t means the observations sit low in their predictive: biased
       (predictions too high). A positive one: biased (predictions too low). A spread
       error leaves the mean PIT at 0.5 while a shift moves it many standard errors, and
       gating the t-test on a failed PIT test keeps it an explanation rather than a
       third test, so it adds no false-alarm rate.
    2. Spread. The coverage test failed: over-confident (predictions too certain) when
       mean_coverage_deviation = 0.5 − mean(c) is ≤ 0, so intervals cover too little;
       otherwise under-confident (predictions too uncertain). A shift also lowers
       interval coverage, to second order, and the data cannot tell that echo from
       real narrowness, so a shift and a spread error are both named.
    3. Shape. The PIT test failed and neither of the above fired: shape mismatch
       (neither a shift nor a spread error).

    well_calibrated holds when both tests pass, which is exactly when findings is empty.
    Every rule reads the value the report records (alpha, mean_pit, location_t,
    mean_coverage_deviation), so each finding re-derives from calibration.json alone.
    When sd(u) = 0 (every LOO-PIT clamped to one tail), the mean counts as a
    significant shift toward mean_pit − 0.5, and location_t is None: an infinite t is
    not valid JSON.

    Known limits:
    - A skewed predictive with the right mean and variance is not labelled shape
      mismatch. A standardized Gamma(2) predictive for N(0, 1) data reads
      over-confident, sometimes with biased (predictions too low).
    - The t-test treats PIT values as independent. Heavy posterior dependence (few
      observations per parameter) inflates it, so read a borderline biased call against
      the PIT figure.

    Raises ValueError for fewer than 2 PIT values, where the t-test is undefined.
    """
    u = np.asarray(pit, dtype=float).ravel()
    n = u.size
    if n < 2:
        raise ValueError(f"Calibration needs at least 2 PIT values; got {n}.")
    # 1 - 0.99 is 0.010000000000000009 in floating point; record the α that was asked for.
    alpha = round(1 - ci_prob, 10)
    coverage = 2 * np.abs(u - 0.5)
    pit_p_value = _pot_c_p_value(u)
    coverage_p_value = _pot_c_p_value(coverage)
    pit_test_passed = pit_p_value >= alpha
    coverage_test_passed = coverage_p_value >= alpha
    mean_pit = round(float(u.mean()), 4)
    mean_coverage_deviation = round(0.5 - float(coverage.mean()), 4)

    sd = float(u.std(ddof=1))
    if sd > 0:
        location_t = round((float(u.mean()) - 0.5) / (sd / math.sqrt(n)), 2)
        shifted = abs(location_t) > float(stats.t.ppf(1 - alpha / 2, n - 1))
        sits_low = location_t < 0
    else:
        location_t = None
        shifted = mean_pit != 0.5
        sits_low = mean_pit < 0.5

    findings = []
    if shifted and not pit_test_passed:
        findings.append(BIASED_HIGH if sits_low else BIASED_LOW)
    if not coverage_test_passed:
        findings.append(OVER_CONFIDENT if mean_coverage_deviation <= 0 else UNDER_CONFIDENT)
    if not pit_test_passed and not findings:
        findings.append(SHAPE_MISMATCH)

    return {
        "pit_p_value": pit_p_value,
        "coverage_p_value": coverage_p_value,
        "alpha": alpha,
        "pit_test_passed": pit_test_passed,
        "coverage_test_passed": coverage_test_passed,
        "mean_pit": mean_pit,
        "location_t": location_t,
        "mean_coverage_deviation": mean_coverage_deviation,
        "findings": findings,
        "well_calibrated": pit_test_passed and coverage_test_passed,
        "calibration_diagnosis": " and ".join(findings) or "well-calibrated",
    }


def _extract_ecdf_results(ds, var_name):
    """Extract ΔECDF check from a difference_ecdf_pit result Dataset.

    Returns (inside_bands, mean_delta_ecdf).
    """
    dy = ds[var_name].sel(plot_axis="y").values
    dy_lb = ds[var_name].sel(plot_axis="y_bottom").values
    dy_ub = ds[var_name].sel(plot_axis="y_top").values
    inside = bool(((dy >= dy_lb) & (dy <= dy_ub)).all())
    return inside, round(float(np.mean(dy)), 4)


def _ecdf_check(pit_vals, ci_prob=0.99, n_simulations=BAND_SIMULATIONS):
    """Compute ΔECDF and check if it stays inside simultaneous confidence bands.

    Uses arviz_stats.ecdf_pit. i.e the same computation that powers the ArviZ plots.
    Returns (inside_bands, mean_delta_ecdf).
    """
    eval_pts, ecdf_vals, ci_lb, ci_ub = ecdf_pit(
        pit_vals, ci_prob, n_simulations=n_simulations
    )
    dy = ecdf_vals - eval_pts
    dy_lb = ci_lb - eval_pts
    dy_ub = ci_ub - eval_pts
    inside = bool(((dy >= dy_lb) & (dy <= dy_ub)).all())
    return inside, round(float(np.mean(dy)), 4)


def assess_calibration(dt, var_name, use_loo, ci_prob=0.99):
    """Assess calibration using the same ΔECDF + simultaneous bands as the plots.

    For PPC-PIT, delegates to arviz_plots.difference_ecdf_pit which handles
    discrete-data randomization correctly. For LOO-PIT, uses arviz_stats.loo_pit
    (which also handles discrete data) then arviz_stats.ecdf_pit.

    "Well-calibrated" means the ΔECDF stays inside the simultaneous bands.

    The coverage direction follows ArviZ conventions (EABM reference):
        positive coverage ΔECDF → empirical > nominal → under-confident (too uncertain)
        negative coverage ΔECDF → empirical < nominal → over-confident (too certain)

    When only the PIT band fails, the verdict reads the failure as a shift — the spread
    is right but the centre is off — and takes the direction from the sign of the mean
    PIT ΔECDF (PIT is P(y_rep <= y)):
        positive PIT ΔECDF → observations fall low in their predictive → biased (predictions too high)
        negative PIT ΔECDF → observations fall high in their predictive → biased (predictions too low)
    That reading is a heuristic. A shape mismatch (a skewed predictive, a missing mode)
    can fail the PIT band alone too, and its mean ΔECDF can sit near zero with a sign
    that carries no information. A shift keeps the ΔECDF on one side of zero; one that
    crosses zero points at shape rather than location.
    A failed coverage band takes precedence: its verdict names the spread problem.
    """
    if use_loo:
        pit_vals = azs.loo_pit(dt, var_names=var_name)[var_name].values
        pit_inside, mean_pit_delta = _ecdf_check(
            pit_vals, ci_prob=ci_prob, n_simulations=BAND_SIMULATIONS
        )
        coverage_vals = 2 * np.abs(pit_vals - 0.5)
        coverage_inside, mean_cov_delta = _ecdf_check(
            coverage_vals, ci_prob=ci_prob, n_simulations=BAND_SIMULATIONS
        )
    else:
        # difference_ecdf_pit walks every observed variable and raises on one with no
        # posterior_predictive counterpart: pass only the one being assessed.
        pp_ds = dt["posterior_predictive"].dataset[[var_name]]
        obs_ds = dt["observed_data"].dataset[[var_name]]
        ds_pit = difference_ecdf_pit(
            pp_ds,
            obs_ds,
            ci_prob=ci_prob,
            coverage=False,
            n_simulations=BAND_SIMULATIONS,
        )
        pit_inside, mean_pit_delta = _extract_ecdf_results(ds_pit, var_name)
        ds_cov = difference_ecdf_pit(
            pp_ds,
            obs_ds,
            ci_prob=ci_prob,
            coverage=True,
            n_simulations=BAND_SIMULATIONS,
        )
        coverage_inside, mean_cov_delta = _extract_ecdf_results(ds_cov, var_name)

    if not coverage_inside:
        if mean_cov_delta > 0:
            calibration_diagnosis = "under-confident (predictions too uncertain)"
        else:
            calibration_diagnosis = "over-confident (predictions too certain)"
    elif not pit_inside:
        if mean_pit_delta > 0:
            calibration_diagnosis = "biased (predictions too high)"
        else:
            calibration_diagnosis = "biased (predictions too low)"
    else:
        calibration_diagnosis = "well-calibrated"

    return {
        "pit_ecdf_inside_bands": pit_inside,
        "coverage_ecdf_inside_bands": coverage_inside,
        "well_calibrated": pit_inside and coverage_inside,
        "mean_coverage_deviation": mean_cov_delta,
        "calibration_diagnosis": calibration_diagnosis,
    }


def save_pit_plot(
    dt, var_name, output_path, *, use_loo=False, coverage=False, ci_prob=0.99
):
    """Generate and save a PIT-based calibration plot.

    Uses azp.plot_loo_pit (LOO-PIT, avoids double-dipping) or
    azp.plot_ppc_pit (PPC-PIT) with optional coverage=True for the
    coverage transformation. Both produce ΔECDF plots whose simultaneous
    bounds (Säilynoja et al. 2022) are computed but not drawn — the figure
    shows the step line, a zero line, highlighted suspicious points, and
    the p-value with its α; the bounds themselves feed the
    *_inside_bands values this script writes.
    """
    plot_fn = azp.plot_loo_pit if use_loo else azp.plot_ppc_pit
    # arviz_plots 1.0 names the simultaneous-band probability `envelope_prob`;
    # passing `ci_prob` here falls through to **pc_kwargs and the backend rejects
    # it ("no active aesthetic"). The lower-level ecdf helpers still use ci_prob.
    pc = plot_fn(dt, var_names=var_name, coverage=coverage, envelope_prob=ci_prob)
    pc.savefig(output_path)
    return output_path


def _exit_with_error(message) -> NoReturn:
    """Print a JSON error object to stdout and exit with status 1."""
    print(json.dumps({"error": message}))
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Bayesian model calibration check")
    parser.add_argument(
        "--idata", required=True, help="Path to InferenceData (.nc file)"
    )
    parser.add_argument(
        "--var-name",
        default=None,
        help="Name of the observed variable (auto-detected if not specified)",
    )
    parser.add_argument("--output", default=None, help="Path to save JSON report")
    parser.add_argument(
        "--save-plots", action="store_true", help="Save calibration plots"
    )
    parser.add_argument(
        "--loo-pit",
        action="store_true",
        help="Use LOO-PIT instead of PPC-PIT (requires log_likelihood group)",
    )
    parser.add_argument(
        "--plot-dir", default=".", help="Directory for saved plots (default: .)"
    )
    parser.add_argument(
        "--ci-prob",
        type=float,
        default=0.99,
        help="Probability for simultaneous confidence bands (default: 0.99)",
    )
    args = parser.parse_args()

    try:
        dt = convert_to_datatree(args.idata)
    except Exception as e:
        _exit_with_error(f"Could not load InferenceData: {e}")

    # Validate data availability
    if "posterior_predictive" not in dt.children:
        _exit_with_error(
            "No posterior_predictive group. Generate it with Predictive(model, posterior_samples=mcmc.get_samples())(key, *args) and pass posterior_predictive=... to az.from_numpyro()."
        )

    if "observed_data" not in dt.children:
        _exit_with_error("No observed_data group. Cannot compute calibration.")

    # Auto-detect var_name if not specified
    var_name = args.var_name
    if var_name is None:
        pp_vars = set(dt["posterior_predictive"].data_vars)
        obs_vars = set(dt["observed_data"].data_vars)
        common = sorted(pp_vars & obs_vars)
        if not common:
            _exit_with_error(
                f"No common variables between posterior_predictive {sorted(pp_vars)} "
                f"and observed_data {sorted(obs_vars)}."
            )
        var_name = common[0]
        if len(common) > 1:
            print(
                f"Warning: multiple common variables found: {common}. Using '{var_name}'.",
                file=sys.stderr,
            )

    if var_name not in dt["posterior_predictive"].data_vars:
        available = list(dt["posterior_predictive"].data_vars)
        _exit_with_error(
            f"Variable '{var_name}' not found in posterior_predictive. Available: {available}"
        )

    if var_name not in dt["observed_data"].data_vars:
        _exit_with_error(
            f"No observed data for '{var_name}'. Cannot compute calibration."
        )

    # Validate LOO-PIT requirements
    if args.loo_pit and "log_likelihood" not in dt.children:
        _exit_with_error(
            "LOO-PIT requires a log_likelihood group in the InferenceData. "
            "Build it with az.from_numpyro(mcmc, log_likelihood=True, ...) "
            "(or numpyro.infer.log_likelihood) before saving the netCDF."
        )
    if args.loo_pit and "posterior" not in dt.children:
        _exit_with_error(
            "LOO-PIT requires a posterior group in the InferenceData: arviz_stats.loo_pit "
            "reads its chain/draw structure for the relative efficiency. "
            "az.from_numpyro(mcmc, ...) writes it by default; keep it when saving the netCDF."
        )

    # Assess calibration using ArviZ ΔECDF + simultaneous bands
    ci_prob = args.ci_prob
    assessment = assess_calibration(dt, var_name, use_loo=args.loo_pit, ci_prob=ci_prob)

    n_obs = len(dt["observed_data"][var_name].values)
    report = {
        "variable": var_name,
        "n_observations": n_obs,
        "pit_method": "loo_pit" if args.loo_pit else "ppc_pit",
        "assessment": assessment,
    }

    # Save plots using arviz_plots
    if args.save_plots:
        os.makedirs(args.plot_dir, exist_ok=True)
        prefix = "loo_pit" if args.loo_pit else "pit"
        report["plots"] = {
            "pit_ecdf": save_pit_plot(
                dt,
                var_name,
                os.path.join(args.plot_dir, f"{prefix}_ecdf.png"),
                use_loo=args.loo_pit,
                ci_prob=ci_prob,
            ),
            "coverage": save_pit_plot(
                dt,
                var_name,
                os.path.join(args.plot_dir, f"{prefix}_coverage.png"),
                use_loo=args.loo_pit,
                coverage=True,
                ci_prob=ci_prob,
            ),
        }

    output = json.dumps(report, indent=2)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
