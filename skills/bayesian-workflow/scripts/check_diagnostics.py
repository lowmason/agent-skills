#!/usr/bin/env python3
# /// script
# requires-python = '>=3.11'
# dependencies = []
# ///
"""
Interpret Bayesian model diagnostics and suggest next steps.

Reads structured outputs from ``diagnose_model.py`` and ``calibration_check.py``
and produces qualitative per-section assessments for the diagnostic report,
plus an ordered list of suggested next steps.

This script does not re-run diagnostics — it interprets what is already there.
Run ``diagnose_model.py`` and ``calibration_check.py`` first to produce the JSON
inputs, then this script to turn the numbers into human-readable ratings and
actionable recommendations.

Usage:
    python check_diagnostics.py --diagnostics diagnostics.json
    python check_diagnostics.py --diagnostics diagnostics.json --calibration calibration.json
    python check_diagnostics.py --diagnostics diagnostics.json --psense psense.json --output report.json

The ``diagnostics.json`` is the output of ``diagnose_model.py``.
The ``calibration.json`` is the output of ``calibration_check.py``.
The ``psense.json`` (optional) is a JSON dump of ``psense_summary(idata)``.
"""

import argparse
import json
import sys


# House thresholds — internal reference levels for qualitative interpretation.
# These are NOT exposed in reports — use the qualitative labels instead.
RHAT_OK = 1.01
DIVERGENCE_OK = 0
DIVERGENCE_FAIR = 0.005  # < 0.5% of post-warmup draws
DIVERGENCE_GATE_PCT = 1.0  # percent; above this, raising target_accept_prob rarely helps (Gelman et al. 2026, §12.3)
COVERAGE_DEVIATION_OK = 0.02
COVERAGE_DEVIATION_FAIR = 0.05
PSENSE_OK = 0.05
PSENSE_FAIR = 0.10

# The report's own published bar for the largest relative MCSE (references/reporting.md,
# Sampling and Convergence), so unlike the levels above it is quoted in the next step.
# diagnose_model.py keeps a copy for its overall verdict; test_diagnose_model.py pins the two.
REL_MCSE_OK = 0.05

# loo's sample-size Pareto-k threshold (good_k, which diagnose_model.py writes) never
# exceeds 0.7, and above 0.7 more draws do not help. A copy, pinned like REL_MCSE_OK.
PARETO_K_MAX = 0.7

# The checks the all-clear requires: report section, label, and the ratings that pass.
REQUIRED_CHECKS = (
    ("convergence", "convergence", ("excellent", "good")),
    ("precision", "Monte Carlo precision", ("excellent",)),
    ("loo", "LOO", ("excellent",)),
    ("calibration", "calibration", ("excellent",)),
)
PSENSE_REMEDY = (
    "run psense_summary(idata) and pass it with --psense, before publication if any "
    "conclusion is policy-relevant"
)

# problematic_params entries that are sampler flags, not parameter names.
NON_PARAM_TOKENS = ("divergence", "e-bfmi", "treedepth", "=")

# The sampler-stat blocks diagnose_model.py marks {"checked": False} when their stat is
# missing: block key, the label the report uses, and how to get the stat.
SAMPLER_CHECKS = (
    ("treedepth", "tree depth",
     "collect num_steps in extra_fields so az.from_numpyro writes reached_max_tree_depth"),
    ("bfmi", "E-BFMI", "collect energy in extra_fields; the check needs arviz-stats >= 1.0"),
    ("divergences", "divergences", "the InferenceData has no diverging sample stat"),
)

# calibration_check.FINDINGS labels, routed by prefix. This is a copy, not an import:
# importing calibration_check would pull the ArviZ stack into this pure-JSON reader.
# test_calibration_check.py's contract test keeps the two in step.
BIASED_PREFIX = "biased ("
OVER_CONFIDENT_PREFIX = "over-confident ("
UNDER_CONFIDENT_PREFIX = "under-confident ("
SHAPE_MISMATCH_PREFIX = "shape mismatch ("


def _split_flags(problematic: list) -> tuple[list[str], list[str]]:
    """Split problematic_params into (parameter names, sampler flags)."""
    named, flags = [], []
    for p in problematic:
        (flags if any(tok in str(p).lower() for tok in NON_PARAM_TOKENS) else named).append(str(p))
    return named, flags


def _flag_phrase(named: list[str], flags: list[str]) -> str:
    """'flags on a, b; max treedepth saturation': parameter names first, then sampler flags."""
    return "; ".join(([f"flags on {', '.join(named[:3])}"] if named else []) + flags)


def _unchecked_sampler_checks(conv: dict) -> list[str]:
    """Labels of the sampler checks that never ran.

    A block marked checked: false, or no block at all, never ran. A block with
    no checked key comes from a diagnostics.json written before the key existed,
    and counts as checked.
    """
    return [
        label for key, label, _ in SAMPLER_CHECKS
        if not conv.get(key, {}).get("checked", key in conv)
    ]


def _rate_convergence(conv: dict) -> tuple[str, list[str]]:
    """Return (rating, problematic_param_names) for the convergence section.

    Consumes the unified schema emitted by ``diagnose_model.check_convergence``
    — both the ``arviz_stats.diagnose`` and manual fallback paths share it, so
    real parameter names flow through (no opaque placeholder). An absent or empty
    section never ran, so it rates "not computed", not "excellent".
    """
    if not conv:
        return "not computed", []
    if conv.get("all_ok"):
        return "excellent", []

    issues: list[str] = []

    rhat = conv.get("rhat", {})
    ess_b = conv.get("ess_bulk", {})
    ess_t = conv.get("ess_tail", {})
    div = conv.get("divergences", {})
    bfmi = conv.get("bfmi", {})
    td = conv.get("treedepth", {})

    if not rhat.get("ok", True):
        issues.extend(rhat.get("problematic_params", []))
    if not ess_b.get("ok", True):
        issues.extend(ess_b.get("problematic_params", []))
    if not ess_t.get("ok", True):
        issues.extend(ess_t.get("problematic_params", []))
    if not div.get("ok", True):
        issues.append(f"divergences={div.get('count', 0)}")
    if not bfmi.get("ok", True):
        issues.append("low E-BFMI")
    if not td.get("ok", True):
        issues.append("max treedepth saturation")

    issues = list(dict.fromkeys(issues))  # dedupe, preserve order

    n_div = div.get("count", 0) if div else 0
    div_pct = div.get("pct", 0.0) if div else 0.0
    rhat_max = rhat.get("max") if rhat else None

    if n_div > 0 and div_pct > DIVERGENCE_FAIR * 100:
        rating = "poor"
    elif rhat_max is not None and rhat_max > 1.05:
        rating = "poor"
    elif issues:
        rating = "fair"
    else:
        rating = "good"

    return rating, issues


def _high_pareto_k(pk: dict) -> int:
    """Finite k > 0.7. A file written before good_k had no n_high, and its n_bad meant this."""
    return pk.get("n_high", pk.get("n_bad", 0))


def _rate_loo(loo: dict) -> str:
    """Return a qualitative rating for the LOO Pareto-k diagnostic.

    Rated from diagnose_model.py's counts against loo's sample-size threshold
    good_k: poor for any k > 0.7 or non-finite k, which more draws cannot fix;
    fair when every flagged k lies between good_k and 0.7, which more draws can.
    """
    if not loo or not loo.get("computed"):
        return "not computed"

    pk = loo.get("pareto_k", {})
    # Any bad point caps the rating — a low max over the *remaining* points
    # doesn't redeem an unreliable observation. max is None only when every
    # point is non-finite.
    if _high_pareto_k(pk) > 0 or pk.get("n_nonfinite", 0) > 0:
        return "poor"
    if pk.get("max") is None:
        return "not computed"
    if pk.get("n_bad", 0) > 0:
        return "fair"
    return "excellent"


def _rate_calibration(cal: dict) -> tuple[str, str]:
    """Return (rating, diagnosis) for calibration."""
    if not cal:
        return "not computed", ""

    assessment = cal.get("assessment", {})
    diagnosis = assessment.get("calibration_diagnosis", "")
    well_cal = assessment.get("well_calibrated", False)
    mean_dev = abs(assessment.get("mean_coverage_deviation", 0.0))

    if well_cal:
        return "excellent", diagnosis
    if mean_dev <= COVERAGE_DEVIATION_FAIR:
        return "fair", diagnosis
    return "poor", diagnosis


def _calibration_findings(cal: dict) -> list[str]:
    """Return the calibration findings, in calibration_check.py's order.

    A calibration.json written before findings existed falls back to its one
    diagnosis, unless that is empty or reads well-calibrated.
    """
    assessment = cal.get("assessment", {})
    if "findings" in assessment:
        return list(assessment["findings"])
    diagnosis = assessment.get("calibration_diagnosis", "")
    if not diagnosis or diagnosis == "well-calibrated":
        return []
    return [diagnosis]


def _rate_psense(ps: dict) -> tuple[str, list[str]]:
    """Return (rating, flagged_params) for prior sensitivity."""
    if not ps:
        return "not computed", []

    # psense_summary(idata).to_dict() is column-oriented:
    #   {"prior": {param: cjs, ...}, "likelihood": {...}, "diagnosis": {...}}
    flagged: list[str] = []
    max_prior_cjs = 0.0

    prior_map = ps.get("prior", ps)
    if isinstance(prior_map, dict):
        for param, prior in prior_map.items():
            try:
                prior = float(prior)
            except (TypeError, ValueError):
                continue
            max_prior_cjs = max(max_prior_cjs, prior)
            if prior > PSENSE_OK:
                flagged.append(param)

    if max_prior_cjs <= PSENSE_OK:
        return "low sensitivity", flagged
    if max_prior_cjs <= PSENSE_FAIR:
        return "moderate sensitivity", flagged
    return "strong sensitivity", flagged


def _rate_precision(prec: dict | None) -> dict:
    """Rate Monte Carlo precision against REL_MCSE_OK.

    "not computed" when diagnostics.json has no precision block, or one with no
    usable parameter: check_precision then reports max_rel_mcse 0.0, which
    would otherwise pass.
    """
    if not prec or not prec.get("params"):
        return {"rating": "not computed"}
    worst = float(prec.get("max_rel_mcse", 0.0))
    return {
        "rating": "excellent" if worst <= REL_MCSE_OK else "poor",
        "max_rel_mcse": worst,
        "max_rel_mcse_param": prec.get("max_rel_mcse_param"),
    }


def check_diagnostics(
    diagnostics: dict | None = None,
    calibration: dict | None = None,
    psense: dict | None = None,
) -> dict:
    """Interpret diagnostic JSON outputs into qualitative assessments.

    Parameters
    ----------
    diagnostics : dict, optional
        Output of ``diagnose_model.generate_report()``. Provides
        ``convergence``, ``loo``, ``posterior_predictive`` and ``precision``
        sub-reports.
    calibration : dict, optional
        Output of ``calibration_check.py``.
    psense : dict, optional
        Output of ``psense_summary(idata).to_dict()`` or equivalent.

    Returns
    -------
    dict
        Structured assessment with sections: ``convergence``, ``loo``,
        ``posterior_predictive``, ``precision``, ``calibration``, ``psense``,
        plus ``summary`` (one-line per section).
    """
    report: dict = {}

    if diagnostics is not None:
        conv_in = diagnostics.get("convergence", {})
        conv_rating, conv_issues = _rate_convergence(conv_in)
        report["convergence"] = {
            "rating": conv_rating,
            "problematic_params": conv_issues,
            # percent of post-warmup transitions that diverged; drives the
            # target_accept_prob gate in suggest_next_steps
            "divergence_pct": float((conv_in.get("divergences") or {}).get("pct", 0.0) or 0.0),
            # the blocks the tree-depth and E-BFMI steps quote
            "treedepth": conv_in.get("treedepth", {}),
            "bfmi": conv_in.get("bfmi", {}),
            "unchecked": _unchecked_sampler_checks(conv_in),
        }
        loo_in = diagnostics.get("loo", {})
        report["loo"] = {
            "rating": _rate_loo(loo_in),
            # carry the Pareto-k breakdown so suggest_next_steps can tell k above
            # good_k, k > 0.7 and non-finite (could-not-estimate) points apart.
            "pareto_k": loo_in.get("pareto_k", {}),
            # diagnose_model.py's reason when LOO did not run; the next step quotes it
            "error": loo_in.get("error", ""),
        }
        ppc = diagnostics.get("posterior_predictive", {})
        report["posterior_predictive"] = {
            "available": bool(ppc.get("available", False)),
        }
        report["precision"] = _rate_precision(diagnostics.get("precision"))

    if calibration is not None:
        cal_rating, cal_diagnosis = _rate_calibration(calibration)
        report["calibration"] = {
            "rating": cal_rating,
            "diagnosis": cal_diagnosis,
            "findings": _calibration_findings(calibration),
        }

    if psense is not None:
        ps_rating, ps_flagged = _rate_psense(psense)
        report["psense"] = {
            "rating": ps_rating,
            "flagged_params": ps_flagged,
        }

    report["summary"] = _build_summary(report)
    return report


def _build_summary(report: dict) -> dict:
    """One short sentence per section, suitable for the report's Assessment lines."""
    s: dict = {}

    if "convergence" in report:
        r = report["convergence"]
        named, flags = _split_flags(r["problematic_params"])
        unchecked = r.get("unchecked", [])
        if r["rating"] == "not computed":
            s["convergence"] = "Convergence diagnostics: not computed."
        elif r["rating"] == "excellent":
            passed = "R-hat ≤ 1.01, ESS adequate" + ("" if "divergences" in unchecked else ", no divergences")
            if unchecked:
                s["convergence"] = (
                    f"Convergence diagnostics that ran passed ({passed}); "
                    f"not checked: {', '.join(unchecked)}."
                )
            else:
                s["convergence"] = f"All convergence diagnostics passed ({passed})."
        elif r["rating"] == "good":
            s["convergence"] = "Convergence diagnostics broadly pass; minor flags worth noting."
        elif r["rating"] == "fair":
            flagged = _flag_phrase(named, flags) or "flags on some parameters"
            s["convergence"] = f"Convergence is fair — {flagged}. Inspect before trusting the posterior."
        else:
            flagged = _flag_phrase(named, flags) or "flags on multiple parameters"
            s["convergence"] = f"Poor convergence — {flagged}. Posterior should not be interpreted until resolved."

    if "precision" in report:
        r = report["precision"]
        if r["rating"] == "not computed":
            s["precision"] = "Monte Carlo precision: not computed."
        else:
            s["precision"] = (
                f"Monte Carlo precision: {r['rating']} (max relative MCSE "
                f"{r['max_rel_mcse']:.3f} on {r['max_rel_mcse_param']}; bar ≤ {REL_MCSE_OK})."
            )

    if "loo" in report:
        s["loo"] = f"LOO Pareto-k: {report['loo']['rating']}."

    if "calibration" in report:
        r = report["calibration"]
        diag = r.get("diagnosis", "")
        s["calibration"] = (
            f"Calibration is {r['rating']}" + (f" — {diag}." if diag else ".")
        )

    if "psense" in report:
        r = report["psense"]
        flagged = ", ".join(r["flagged_params"]) if r["flagged_params"] else "none"
        s["psense"] = f"Prior sensitivity: {r['rating']} (flagged: {flagged})."

    return s


def _spread_step(finding: str, rating: str) -> str:
    """The spread step: the direction's full remedy when poor, a milder form when fair."""
    over = finding.startswith(OVER_CONFIDENT_PREFIX)
    if rating != "poor":
        if over:
            return (
                "Calibration is fair but not excellent and slightly over-confident — "
                "consider a heavier-tailed or more dispersed likelihood, or a missing "
                "variance component such as group-level variation."
            )
        return (
            "Calibration is fair but not excellent and slightly under-confident — "
            "consider tighter, better-informed priors, or a missing predictor that "
            "would explain the remaining spread."
        )
    if over:
        return (
            "Calibration is over-confident — likelihood is too narrow for the "
            "data. Consider StudentT for continuous outcomes with heavy tails, "
            "NegBinomial for overdispersed counts, or hierarchical structure if "
            "groups have distinct variance."
        )
    return (
        "Calibration is under-confident — predictions are too uncertain. "
        "Tighten priors that are dominating the likelihood, or check whether "
        "the model is overcomplicated for the data."
    )


def _calibration_steps(cal: dict) -> list[str]:
    """One next step per calibration finding, in findings order (centre first)."""
    steps: list[str] = []
    shifted = False
    for finding in cal.get("findings", []):
        if finding.startswith(BIASED_PREFIX):
            shifted = True
            steps.append(
                f"Calibration is {finding} — the predictive's centre is off, so check "
                "the mean structure before the likelihood: a missing predictor or "
                "group effect, a wrong link or offset, or an intercept prior pulling "
                "the centre. Compare posterior-predictive means with observed means "
                "by group."
            )
        elif finding.startswith(OVER_CONFIDENT_PREFIX) and shifted:
            # A shift alone lowers interval coverage, so this may be its echo.
            steps.append(
                "Calibration is also over-confident, but a shift alone lowers interval "
                "coverage — fix the centre first, re-run calibration_check.py, and act "
                "on the spread only if the over-confidence remains."
            )
        elif finding.startswith((OVER_CONFIDENT_PREFIX, UNDER_CONFIDENT_PREFIX)):
            # A shift cannot cause under-confidence, so it keeps its spread step.
            steps.append(_spread_step(finding, cal.get("rating", "")))
        elif finding.startswith(SHAPE_MISMATCH_PREFIX):
            steps.append(
                "Calibration fails the PIT test, but neither a shift nor a spread "
                "error explains it — read the highlighted points on the PIT figure "
                "beside a posterior-predictive density overlay (azp.plot_ppc_dist), and "
                "consider a likelihood with the right shape: skewed, mixture, "
                "zero-inflated or hurdle."
            )
        else:
            steps.append(
                "Calibration check failed — re-examine the likelihood and the "
                "prior predictive range before interpreting posteriors."
            )
    return steps


def _not_checked(report: dict) -> list[str]:
    """'check (how to run it)' for each optional check that did not run."""
    unchecked = report.get("convergence", {}).get("unchecked", [])
    missing = [f"{label} ({remedy})" for _, label, remedy in SAMPLER_CHECKS if label in unchecked]
    if report.get("psense", {}).get("rating", "not computed") == "not computed":
        missing.append(f"prior sensitivity ({PSENSE_REMEDY})")
    return missing


def _closing_steps(report: dict) -> list[str]:
    """The all-clear when every required check ran and passed; otherwise what blocks it.

    Reached only when no other step was added, so a required section that is
    missing, or that did not pass without adding a step of its own, still
    blocks the all-clear.
    """
    unresolved = [
        f"{label} ({report.get(key, {}).get('rating', 'not run')})"
        for key, label, passing in REQUIRED_CHECKS
        if report.get(key, {}).get("rating", "not run") not in passing
    ]
    if unresolved:
        return [
            "No specific next step applies, but not every required check ran and passed: "
            f"{', '.join(unresolved)}. Resolve these before interpreting the posterior."
        ]
    steps = [
        "All diagnostics are within acceptable bounds — proceed to "
        "interpretation. Translate posteriors into decision-relevant terms "
        "and document the model assumptions in the report."
    ]
    missing = _not_checked(report)
    if missing:
        steps.append(f"Not checked: {'; '.join(missing)}. Say so in the report.")
    return steps


def suggest_next_steps(report: dict) -> list[str]:
    """Combine the interpreted report into an ordered, actionable list.

    Most-critical issues first. Returns generic guidance — extend with
    problem-specific context when filling in the report.
    """
    steps: list[str] = []

    # ── Convergence (highest priority) ────────────────────────────────
    conv = report.get("convergence", {})
    if conv.get("rating") in ("poor", "fair"):
        params = conv.get("problematic_params", [])
        has_divergences = any("divergence" in str(p).lower() for p in params)
        # Non-parameter flags (divergences, E-BFMI, treedepth) are surfaced
        # separately — keep them out of the per-parameter R-hat/ESS message so
        # it never interpolates a flag phrase where a parameter name belongs.
        named_params, _ = _split_flags(params)

        if has_divergences:
            pct = float(conv.get("divergence_pct", 0.0) or 0.0)
            if pct > DIVERGENCE_GATE_PCT:
                steps.append(
                    f"Divergences are {pct:.1f}% of post-warmup transitions — above the ~1% level "
                    "at which a smaller step size stops helping (Gelman et al. 2026, §12.3). "
                    "Do not raise target_accept_prob or max_tree_depth. Next action — one plot, "
                    "before any refit: az.plot_pair(idata, var_names=['<flagged scale>', "
                    "'<one of its children>']) (divergent draws are marked automatically). Then "
                    "match the picture to the Failure signatures table in references/diagnostics.md "
                    "— a neck → non-centered numpyro.infer.reparam.LocScaleReparam; a straight "
                    "ridge → an identifiability problem, so drop or anchor one of the aliased "
                    "sites; no shape → scope the model down to isolate the component that breaks "
                    "sampling."
                )
            else:
                steps.append(
                    f"Divergences are {pct:.2f}% of transitions (≤ 1%) — raise target_accept_prob "
                    "to 0.95–0.99 on the NUTS kernel first; if any remain, reparameterize the "
                    "affected component (non-centered via numpyro.infer.reparam.LocScaleReparam "
                    "for hierarchical scales) or replace HalfCauchy with Gamma(2, ...) on scale "
                    "priors."
                )
        if named_params:
            preview = ", ".join(named_params[:3])
            steps.append(
                f"R-hat or ESS flags on {preview} — run more draws/warmup, try "
                "init_strategy=numpyro.infer.init_to_median, or warm-start NUTS from an SVI "
                "AutoNormal fit (or blackjax.pathfinder). "
                "Check for multimodality with az.plot_rank(idata) (runs on both ArviZ stacks)."
            )
        td = conv.get("treedepth", {})
        if not td.get("ok", True):
            steps.append(
                f"Tree depth hit max_tree_depth on {td.get('pct', 0.0):.1f}% of transitions "
                f"({td.get('n_max', 0)}) — those trajectories were cut short, so the sampler "
                "explores slowly. Saturation is an efficiency warning, not a validity failure, "
                "but check the geometry before raising max_tree_depth on the NUTS kernel: an "
                "improper or near-improper posterior saturates every transition, and a higher "
                "limit never helps there (references/diagnostics.md, Failure signatures)."
            )
        bfmi = conv.get("bfmi", {})
        if not bfmi.get("ok", True):
            chains = ", ".join(str(c) for c in bfmi.get("failed_chains", []))
            steps.append(
                f"E-BFMI is low on chain(s) {chains} — those chains explore the energy "
                "distribution poorly, often because of heavy tails or a funnel. Plot "
                "az.plot_energy(idata), then work the escalation ladder in "
                "references/diagnostics.md, starting from its Failure signatures table."
            )
    elif conv.get("rating") == "not computed":
        steps.append(
            "Convergence was not checked — diagnostics.json has no convergence section, so "
            "R-hat, ESS and the sampler checks never ran. Re-run diagnose_model.py, which "
            "writes it, before interpreting the posterior."
        )

    # ── Monte Carlo precision ─────────────────────────────────────────
    prec = report.get("precision", {})
    if prec.get("rating") == "poor":
        steps.append(
            f"Monte Carlo precision is short of the report's bar: max relative MCSE "
            f"{prec['max_rel_mcse']:.3f} on {prec['max_rel_mcse_param']}, above {REL_MCSE_OK} "
            "(references/reporting.md, Sampling and Convergence). Run more draws before "
            "reporting — halving the MCSE costs about four times the draws — and round each "
            "reported value to its stable_digits in diagnostics.json → precision."
        )
    elif prec.get("rating") == "not computed":
        steps.append(
            "Monte Carlo precision was not checked — diagnostics.json has no precision block "
            "with a usable parameter. Re-run diagnose_model.py, which writes it, before filling "
            "the report's MCSE row."
        )

    # ── Calibration ───────────────────────────────────────────────────
    if "calibration" not in report:
        steps.append(
            "Calibration was not checked — run calibration_check.py and pass its JSON with "
            "--calibration. Calibration is mandatory for every model "
            "(references/model-criticism.md), and the report's all-clear depends on it "
            "(references/reporting.md)."
        )
    steps.extend(_calibration_steps(report.get("calibration", {})))

    # ── LOO ───────────────────────────────────────────────────────────
    loo = report.get("loo", {})
    loo_rating = loo.get("rating", "not computed")
    loo_pk = loo.get("pareto_k", {})
    n_high = _high_pareto_k(loo_pk)
    n_nonfinite = loo_pk.get("n_nonfinite", 0)
    if loo_rating == "poor":
        if n_high:
            steps.append(
                f"LOO Pareto-k > {PARETO_K_MAX} for {n_high} observation(s) — PSIS-LOO is "
                "unreliable there, and more draws will not fix it. Inspect them with "
                "az.plot_khat(loo) (often outliers or high-leverage points) and consider a "
                "more robust likelihood (StudentT). For exact values at those points, refit "
                "with azs.reloo (one refit per flagged point) or azs.loo_kfold (K refits) "
                "through an azs.SamplingWrapper subclass for your model, or run "
                "azs.loo_moment_match with your model's log-density functions (it builds "
                "them itself only for PyMC and Bambi)."
            )
        if n_nonfinite:
            steps.append(
                f"LOO could not be estimated for {n_nonfinite} observation(s) "
                "(non-finite Pareto-k — degenerate importance weights). This usually "
                "co-occurs with sampling problems, so fix convergence first; then "
                "inspect those points and consider a more robust likelihood (StudentT)."
            )
    elif loo_rating == "fair":
        steps.append(
            f"LOO Pareto-k is above the sample-size threshold {loo_pk.get('good_k', PARETO_K_MAX):g} "
            f"but at most {PARETO_K_MAX} for {loo_pk.get('n_bad', 0)} observation(s) — PSIS-LOO "
            "is not reliable there yet, but more draws may fix it: the threshold rises to "
            f"{PARETO_K_MAX} at about 2,200 draws in total (loo's Pareto-k diagnostic). Re-run "
            "with more draws before trusting or comparing LOO."
        )
    elif loo_rating == "not computed" and "loo" in report:
        reason = loo.get("error") or (
            "diagnostics.json has no LOO result; re-run diagnose_model.py on an "
            "InferenceData with a log_likelihood group."
        )
        steps.append(f"LOO was not computed, so the Pareto-k check never ran — {reason}")

    # ── PPC availability ──────────────────────────────────────────────
    if not report.get("posterior_predictive", {}).get("available", True):
        steps.append(
            "No posterior_predictive group found — generate it with "
            "`Predictive(model, posterior_samples=mcmc.get_samples())(key, *args)`, attach via "
            "`az.from_numpyro(posterior_predictive=...)`, and re-run diagnostics. "
            "Models without PPC cannot be model-criticized."
        )

    # ── Prior sensitivity ─────────────────────────────────────────────
    ps = report.get("psense", {})
    if ps.get("rating") == "strong sensitivity":
        flagged = ", ".join(ps.get("flagged_params", []))
        steps.append(
            f"Strong prior sensitivity on {flagged} — either justify the "
            "informative prior explicitly with domain knowledge, or widen it "
            "and refit. Report both versions if the substantive conclusion changes."
        )
    elif ps.get("rating") == "moderate sensitivity":
        flagged = ", ".join(ps.get("flagged_params", []))
        steps.append(
            f"Moderate prior sensitivity on {flagged} — note in the report. "
            "Conclusions for those parameters depend partly on the prior."
        )

    # ── Closing: the all-clear only when every required check ran and passed ──
    if not steps:
        steps.extend(_closing_steps(report))

    return steps


def _load_optional(path: str | None) -> dict | None:
    if path is None:
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {path} not found — skipping.", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Warning: could not parse {path} ({e}) — skipping.", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Interpret Bayesian diagnostics and suggest next steps"
    )
    parser.add_argument(
        "--diagnostics",
        required=True,
        help="Path to diagnostics JSON (output of diagnose_model.py)",
    )
    parser.add_argument(
        "--calibration",
        default=None,
        help="Path to calibration JSON (output of calibration_check.py)",
    )
    parser.add_argument(
        "--psense",
        default=None,
        help="Path to prior sensitivity JSON (psense_summary output)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path to save full JSON report (default: print to stdout)",
    )
    args = parser.parse_args()

    diagnostics = _load_optional(args.diagnostics)
    if diagnostics is None:
        print(
            json.dumps(
                {"error": f"Could not load required diagnostics file: {args.diagnostics}"}
            )
        )
        sys.exit(1)

    calibration = _load_optional(args.calibration)
    psense = _load_optional(args.psense)

    report = check_diagnostics(
        diagnostics=diagnostics,
        calibration=calibration,
        psense=psense,
    )
    next_steps = suggest_next_steps(report)
    report["next_steps"] = next_steps

    print("=== Per-Section Assessment ===")
    for section, line in report.get("summary", {}).items():
        print(f"  {section}: {line}")
    print("==============================\n")

    print("=== Suggested Next Steps ===")
    for i, step in enumerate(next_steps, 1):
        print(f"  {i}. {step}")
    print("============================\n")

    output = json.dumps(report, indent=2)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
