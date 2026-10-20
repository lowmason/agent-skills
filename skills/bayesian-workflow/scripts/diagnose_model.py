"""
Automated Bayesian model diagnostics.

Runs convergence checks, posterior predictive checks, LOO, and a Monte Carlo
precision block (MCSE -> stable digits), and produces a structured report.

Usage:
    python diagnose_model.py --idata path/to/inference_data.nc
    python diagnose_model.py --idata path/to/inference_data.nc --output report.json
"""

import argparse
import json
import math
import sys
import warnings

import arviz as az
import numpy as np

warnings.filterwarnings("ignore", category=FutureWarning)

# arviz_stats >= 1.0.0 provides diagnose() for one-call diagnostics
try:
    import arviz_stats as azs

    HAS_DIAGNOSE = hasattr(azs, "diagnose")
except ImportError:
    HAS_DIAGNOSE = False

# The report's bar for the largest relative MCSE (references/reporting.md, Sampling and
# Convergence). check_diagnostics.py keeps a copy; test_diagnose_model.py pins the two.
REL_MCSE_OK = 0.05

# loo's sample-size Pareto-k threshold never exceeds 0.7, and above 0.7 more draws do
# not help. check_diagnostics.py keeps a copy; test_diagnose_model.py pins the two.
PARETO_K_MAX = 0.7

# The tree-depth saturation flags, NumPyro's first: az.from_numpyro writes
# reached_max_tree_depth (when num_steps is collected), while arviz_stats.diagnose
# reads only the CmdStan-style reached_max_treedepth.
TREEDEPTH_FLAGS = ("reached_max_tree_depth", "reached_max_treedepth")

# Tail ESS on the 0.05 and 0.95 quantiles. Without an explicit prob, arviz-stats 1.x
# takes the quantiles from stats.ci_prob (its 0.89 default gives 0.11 and 0.89), so a
# display setting would move the gate. Classic ArviZ 0.23 uses 0.05 and 0.95 already.
TAIL_ESS_PROB = (0.05, 0.95)


def _json_default(o):
    """Coerce stray numpy scalars/arrays so json.dumps never chokes.

    Belt-and-suspenders: check_convergence already returns primitives, but LOO
    and any future additions may carry numpy types. np.int64 in particular is
    not a Python int and is rejected by the default JSON encoder.
    """
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def _max_from_dataset(ds):
    """Best-effort scalar maximum from an xarray Dataset of diagnostic values.

    ``az.rhat`` returns the per-parameter R-hat values as an xarray Dataset (not
    JSON-serializable). We only need the scalar max for rating, so extract it
    defensively and drop the Dataset itself.
    """
    if ds is None:
        return None
    try:
        # Reduce each variable independently, then take the overall max. This is
        # robust to (a) modern xarray dropping Dataset.to_array() in favour of
        # to_dataarray(), and (b) variables with mismatched dims (scalar params
        # alongside a vector Deterministic) that break both to_array/to_dataarray.
        # An empty Dataset, or one whose maxima are all non-finite, yields None.
        data_vars = getattr(ds, "data_vars", None)
        if data_vars is not None:
            vals = [float(ds[v].max()) for v in data_vars]
        else:
            vals = [float(ds.max())]  # already a DataArray
        # Drop non-finite maxima — a NaN here would serialize as a bare `NaN`,
        # which json.dumps emits but is invalid JSON (rejected by strict parsers).
        finite = [v for v in vals if np.isfinite(v)]
        return max(finite) if finite else None
    except Exception:
        return None


def _sample_stats(idata):
    """The sample_stats group, or None when the InferenceData has none."""
    return idata.sample_stats if "sample_stats" in _group_names(idata) else None


def _divergence_block(stats):
    """Divergences from sample_stats; {"checked": False} without a diverging stat."""
    if stats is None or "diverging" not in stats:
        return {"checked": False}
    flags = stats["diverging"]
    n_div = int(flags.sum())
    return {"checked": True, "count": n_div, "pct": round(100 * n_div / int(flags.size), 2), "ok": n_div == 0}


def _treedepth_block(stats):
    """Tree-depth saturation from either TREEDEPTH_FLAGS stat; {"checked": False} without one.

    An unchecked block carries no ok key, so check_diagnostics can tell it from
    a pass, and from ok: None, which it reads as saturation.
    """
    flag = next((f for f in TREEDEPTH_FLAGS if stats is not None and f in stats), None)
    if flag is None:
        return {"checked": False}
    hits = stats[flag]
    n_max = int(hits.sum())
    return {"checked": True, "ok": n_max == 0, "n_max": n_max, "pct": round(100 * n_max / int(hits.size), 2)}


def _ess_block(idata, method, **kwargs):
    """An ESS block by variable: ok against 100 * chains, the failing names and the minimum."""
    ess = az.ess(idata, method=method, **kwargs)
    thresh = 100 * int(idata.posterior.sizes["chain"])
    mins = {str(v): float(ess[v].min()) for v in ess.data_vars}
    bad = [v for v, m in mins.items() if m < thresh]
    return {"ok": not bad, "problematic_params": bad, "min": int(min(mins.values()))}


def _bfmi_block(diagnosed):
    """E-BFMI from arviz_stats.diagnose's results; {"checked": False} when it had no energy stat."""
    if "bfmi" not in diagnosed:
        return {"checked": False}
    failed = [int(c) for c in diagnosed["bfmi"].get("failed_chains", [])]
    return {"checked": True, "ok": not failed, "failed_chains": failed}


def check_convergence(idata):
    """Run all convergence diagnostics. Returns structured results.

    Both code paths emit the SAME serializable schema so ``check_diagnostics.py``
    has a single contract to consume: ``rhat`` / ``ess_bulk`` / ``ess_tail`` each
    carry ``ok`` and ``problematic_params``. ``divergences``, ``treedepth`` and
    ``bfmi`` carry ``checked``: a block whose sample stat is missing (``diverging``;
    either of ``TREEDEPTH_FLAGS``; ``energy``) is just ``{"checked": False}``, so
    an unchecked block never reads as passed. Only the ``arviz_stats.diagnose``
    path computes E-BFMI; the fallback always marks it unchecked.
    Both paths take tail ESS on the TAIL_ESS_PROB quantiles and name failing
    variables (``beta``). The fallback's R-hat and bulk ESS come from
    ``az.summary`` and name elements (``beta[0]``).
    No numpy scalars, numpy arrays, or xarray objects leak into the dict — those
    are not JSON-serializable and would crash the report writer.
    """
    # Use arviz_stats.diagnose() if available — it covers R-hat, ESS,
    # divergences, and E-BFMI in one call. It reads tree depth only from the
    # CmdStan-style "reached_max_treedepth", while az.from_numpyro writes
    # "reached_max_tree_depth", so both paths take the treedepth block from
    # sample_stats themselves.
    if HAS_DIAGNOSE:
        # show_diagnostics=False keeps stdout clean so the JSON report can be
        # piped there when --output is omitted.
        has_errors, d = azs.diagnose(
            idata, return_diagnostics=True, show_diagnostics=False
        )
        rhat_bad = [str(p) for p in d.get("rhat", {}).get("bad_params", [])]
        # diagnose() keeps R-hat values for the flagged params only, so a clean run
        # would carry no max; compute it over every parameter, as ESS is below.
        rhat_max = _max_from_dataset(az.rhat(idata))
        # diagnose()'s d['ess']['bad_params'] keys off ess_min_ratio (ESS/N<0.001),
        # NOT the ~100*chains threshold its printed report / has_errors use. Recompute
        # ESS against 100 * chains so failing param NAMES surface.
        stats = _sample_stats(idata)
        results = {
            "method": "arviz_stats.diagnose",
            "rhat": {
                "ok": len(rhat_bad) == 0,
                "max": rhat_max,
                "problematic_params": rhat_bad,
            },
            "ess_bulk": _ess_block(idata, "bulk"),
            "ess_tail": _ess_block(idata, "tail", prob=TAIL_ESS_PROB),
            "divergences": _divergence_block(stats),
            "treedepth": _treedepth_block(stats),
            "bfmi": _bfmi_block(d),
        }
        # has_errors misses the tail ESS and NumPyro's tree-depth flag, so fold every
        # block in, as the fallback does: check_diagnostics rates "excellent" on all_ok
        # before it reads any block. An unchecked block has no ok key and counts as passing.
        all_ok = not has_errors and all(
            results[k].get("ok", True)
            for k in ["rhat", "ess_bulk", "ess_tail", "divergences", "treedepth", "bfmi"]
        )
        return {"all_ok": all_ok, **results}

    # Fallback for arviz-stats < 1.0.0 (classic ArviZ-only environments). round_to="none"
    # keeps R-hat raw: 0.23 rounds it to two decimals, so 1.0109 read as 1.01 and passed.
    summary = az.summary(idata, round_to="none")
    num_chains = int(idata.posterior.sizes["chain"])

    results = {
        "rhat": {
            "max": float(summary["r_hat"].max()),
            "ok": bool((summary["r_hat"] <= 1.01).all()),
            "problematic_params": list(summary[summary["r_hat"] > 1.01].index),
        },
        "ess_bulk": {
            "min": int(summary["ess_bulk"].min()),
            "ok": bool((summary["ess_bulk"] >= 100 * num_chains).all()),
            "problematic_params": list(
                summary[summary["ess_bulk"] < 100 * num_chains].index
            ),
        },
        "ess_tail": _ess_block(idata, "tail", prob=TAIL_ESS_PROB),
    }

    stats = _sample_stats(idata)
    results["divergences"] = _divergence_block(stats)
    results["treedepth"] = _treedepth_block(stats)
    results["bfmi"] = {"checked": False}  # E-BFMI needs arviz_stats.diagnose

    results["all_ok"] = all(
        results[k].get("ok", True)
        for k in ["rhat", "ess_bulk", "ess_tail", "divergences", "treedepth"]
    )
    results["method"] = "manual"

    return results


def _group_names(idata):
    """Group names as a set, normalized across InferenceData and DataTree.

    PyMC 5 / arviz 0.23 return an ``InferenceData`` whose ``groups`` is a
    *method* yielding bare names (``"log_likelihood"``). PyMC 6 / arviz 1.x
    return a ``DataTree`` whose ``groups`` is a *property* yielding *paths*
    (``"/log_likelihood"``). Calling ``idata.groups()`` on the latter raises
    ``'tuple' object is not callable`` — which, swallowed by check_loo's except,
    silently drops LOO on PyMC 6 even when log_likelihood is present. Normalize
    both shapes to a set of bare names.
    """
    groups = getattr(idata, "groups", None)
    if groups is None:
        return set()
    raw = groups() if callable(groups) else groups
    return {s for g in raw if (s := str(g).strip("/"))}


def _loo_field(loo, *names):
    """First present attribute among ``names`` on an ELPDData, else None.

    arviz 1.x renamed the classic ELPDData fields: ``elpd_loo`` -> ``elpd`` and
    ``p_loo`` -> ``p`` (``se`` and ``pareto_k`` are unchanged). Trying each name
    in turn makes the extractor work on arviz 0.23 and 1.x alike.
    """
    for n in names:
        if hasattr(loo, n):
            return getattr(loo, n)
    return None


def pareto_k_threshold(n_samples):
    """loo's sample-size Pareto-k threshold, min(1 - 1/log10(S), 0.7); see references/model-criticism.md.

    Computed here from S = chains x draws rather than read from the ELPDData, so
    the same idata gets the same cutoff on ArviZ 0.23 and 1.x. It is 0.7 above
    about 2,200 draws and about 0.656 at the 4 x 200 exploring size.
    """
    return min(1 - 1 / math.log10(n_samples), PARETO_K_MAX)


def summarize_pareto_k(pareto_k, n_samples):
    """The diagnostics.json pareto_k block, counted against pareto_k_threshold.

    n_bad counts each finite k above good_k, where loo calls PSIS-LOO
    unreliable; n_high counts those above 0.7, which more draws cannot fix. A
    non-finite k means PSIS could not estimate that point at all (arviz 1.x
    returns NaN there): it is counted apart in n_nonfinite, and max runs over
    the finite values only, so no bare NaN reaches the JSON (json.dumps would
    emit `NaN`, which is invalid JSON).
    """
    pareto_k = np.asarray(pareto_k, dtype=float)
    finite = pareto_k[np.isfinite(pareto_k)]
    n_nonfinite = int(pareto_k.size - finite.size)
    good_k = pareto_k_threshold(n_samples)
    n_bad = int(np.sum(finite > good_k))
    return {
        "max": float(finite.max()) if finite.size else None,
        "good_k": round(good_k, 4),
        "n_bad": n_bad,
        "n_high": int(np.sum(finite > PARETO_K_MAX)),
        "n_nonfinite": n_nonfinite,
        "ok": n_bad == 0 and n_nonfinite == 0,
    }


def check_loo(idata):
    """Run LOO-CV and check Pareto k diagnostics.

    The InferenceData must already carry a ``log_likelihood`` group. With NumPyro
    you get one by passing ``log_likelihood=True`` to ``az.from_numpyro(...)`` (or by
    calling ``numpyro.infer.log_likelihood`` and attaching it) *before* saving to
    netCDF — there is no model object to recompute it from once the .nc is on disk.
    """
    try:
        if "log_likelihood" not in _group_names(idata):
            return {
                "computed": False,
                "error": (
                    "No log_likelihood group in the InferenceData. Rebuild it with "
                    "az.from_numpyro(mcmc, log_likelihood=True, ...) (or numpyro.infer."
                    "log_likelihood) and re-save the netCDF before running diagnostics."
                ),
            }
        loo = az.loo(idata, pointwise=True)
        elpd = _loo_field(loo, "elpd_loo", "elpd")
        se = _loo_field(loo, "se")
        p_loo = _loo_field(loo, "p_loo", "p")
        n_samples = int(idata.posterior.sizes["chain"]) * int(idata.posterior.sizes["draw"])
        results = {
            "elpd": float(elpd) if elpd is not None else None,
            "se": float(se) if se is not None else None,
            "p_loo": float(p_loo) if p_loo is not None else None,
            "pareto_k": summarize_pareto_k(_loo_field(loo, "pareto_k"), n_samples),
            "computed": True,
        }
    except Exception as e:
        results = {"computed": False, "error": str(e)}

    return results


def check_posterior_predictive(idata):
    """Check if posterior predictive data exists and basic stats."""
    if not hasattr(idata, "posterior_predictive"):
        return {
            "available": False,
            "message": "No posterior predictive samples found. Generate with numpyro.infer.Predictive(model, posterior_samples=mcmc.get_samples()) and attach via az.from_numpyro(posterior_predictive=...).",
        }

    pp_vars = list(idata.posterior_predictive.data_vars)
    results = {"available": True, "variables": pp_vars}

    if hasattr(idata, "observed_data"):
        obs_vars = list(idata.observed_data.data_vars)
        results["observed_variables"] = obs_vars

    return results


def check_precision(idata):
    """Monte Carlo precision per parameter: how many significant digits of the
    posterior mean are stable under a re-run with a new seed.

    Follows Gelman et al. 2026, §11.5-11.6 in reporting the Monte Carlo standard
    error (MCSE) beside the posterior sd. The rounding rule applied here — keep
    the rounding unit above ~2 * MCSE — is this skill's; the book's own
    digit-stability reasoning runs in +/-3 * MCSE (the 99.7% range).
    The relative MCSE ``mcse_mean / sd`` maps to stable
    significant digits as ``floor(-log10(rel))``: 10% -> 1 digit, 1% -> 2.
    Parameters with a non-positive or non-finite sd or MCSE (deterministic
    quantities, constants) are skipped. Interval endpoints are usually less
    precise than the mean; check ``az.mcse(idata, method="quantile", prob=...)``
    separately before quoting a tail quantile to two digits.
    """
    # sd / mcse_mean / mcse_sd on arviz 0.23 and 1.x alike. round_to="none" keeps them raw:
    # 0.23 rounds to three decimals, which zeroes the MCSE of a parameter with sd near 0.01.
    summary = az.summary(idata, round_to="none")
    params = {}
    for name, row in summary.iterrows():
        sd = float(row["sd"])
        mcse = float(row["mcse_mean"])
        if not (np.isfinite(sd) and np.isfinite(mcse)) or sd <= 0 or mcse <= 0:
            continue
        rel = mcse / sd
        params[str(name)] = {
            "sd": sd,
            "mcse_mean": mcse,
            "mcse_sd": float(row["mcse_sd"]) if np.isfinite(row["mcse_sd"]) else None,
            "rel_mcse": round(rel, 4),
            "stable_digits": int(max(0, math.floor(-math.log10(rel)))),
        }
    if not params:
        return {
            "params": {},
            "max_rel_mcse": 0.0,
            "max_rel_mcse_param": None,
            "min_stable_digits": None,
        }
    worst = max(params, key=lambda k: params[k]["rel_mcse"])
    return {
        "params": params,
        "max_rel_mcse": params[worst]["rel_mcse"],
        "max_rel_mcse_param": worst,
        "min_stable_digits": min(p["stable_digits"] for p in params.values()),
    }


def generate_report(idata):
    """Generate complete diagnostics report."""
    report = {
        "convergence": check_convergence(idata),
        "loo": check_loo(idata),
        "posterior_predictive": check_posterior_predictive(idata),
        "precision": check_precision(idata),
    }

    # Overall assessment
    issues = []
    if not report["convergence"]["all_ok"]:
        issues.append("Convergence issues detected — results may be unreliable")
    prec = report["precision"]
    if prec["params"] and prec["max_rel_mcse"] > REL_MCSE_OK:
        issues.append(
            f"Max relative MCSE {prec['max_rel_mcse']:.3f} on {prec['max_rel_mcse_param']} "
            f"is above the {REL_MCSE_OK} bar — run more draws before reporting"
        )
    if not report["loo"].get("computed"):
        issues.append(f"LOO not computed: {report['loo'].get('error', 'no LOO result')}")
    loo_pk = report["loo"].get("pareto_k", {}) if report["loo"].get("computed") else {}
    if loo_pk and not loo_pk.get("ok", True):
        n_bad = loo_pk.get("n_bad", 0)
        n_nf = loo_pk.get("n_nonfinite", 0)
        parts = []
        if n_bad:
            parts.append(f"{n_bad} observation(s) with Pareto k above {loo_pk['good_k']:g}")
        if n_nf:
            parts.append(
                f"{n_nf} observation(s) with non-finite Pareto k (LOO could not be estimated)"
            )
        issues.append("; ".join(parts) if parts else "influential observations in LOO")
    if not report["posterior_predictive"]["available"]:
        issues.append("No posterior predictive checks available")

    report["overall"] = {
        "ok": len(issues) == 0,
        "issues": issues,
        "recommendation": "Model is ready for interpretation."
        if len(issues) == 0
        else "Address the following issues before interpreting results: "
        + "; ".join(issues),
    }

    return report


def main():
    parser = argparse.ArgumentParser(description="Bayesian model diagnostics")
    parser.add_argument(
        "--idata", required=True, help="Path to InferenceData (.nc file)"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path to save JSON report (default: print to stdout)",
    )
    args = parser.parse_args()

    try:
        idata = az.from_netcdf(args.idata)
    except Exception as e:
        print(json.dumps({"error": f"Could not load InferenceData: {e}"}))
        sys.exit(1)

    report = generate_report(idata)

    output = json.dumps(report, indent=2, default=_json_default)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
