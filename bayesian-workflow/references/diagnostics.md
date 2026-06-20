# Convergence Diagnostics

## Contents
- Quick diagnostic checklist
- R-hat
- Effective sample size (ESS)
- Divergences
- When sampling fails: the escalation ladder
- Trace plots and rank plots
- Energy diagnostics
- Automated diagnostics workflow

## Quick diagnostic checklist

Run this immediately after sampling. If any check fails, do NOT interpret results.

```python
# you just ran this (and requested energy for the energy plot):
# mcmc.run(rng_key, x, y=y, extra_fields=("energy", "diverging", "num_steps", "accept_prob"))
# idata = az.from_numpyro(mcmc, log_likelihood=True, coords=coords, dims=dims)
# idata = idata.map_over_datasets(lambda ds: ds.as_numpy())

import arviz as az
import arviz_stats as azs

# 1. One-call diagnostics: R-hat, ESS, divergences
# Prints a human-readable summary and returns True if any check failed.
# Defaults already enforce our thresholds (rhat_max=1.01, ESS ratio, etc.).
has_errors = azs.diagnose(idata)

# 2. If you need the detailed breakdown programmatically:
has_errors, diagnostics = azs.diagnose(idata, return_diagnostics=True, show_diagnostics=False)
# diagnostics contains: "divergent", "ess", "rhat"

# 3. Visual check — pass var_names; ArviZ 1.x caps the subplot count
az.plot_trace(idata, var_names=["param1", "param2"])
```

`arviz_stats.diagnose` (>= 1.0.0) checks **R-hat, ESS, and divergences** in one call. (Earlier
PyMC-stack guidance mentioned tree-depth and E-BFMI here; the current `arviz_stats.diagnose`
returns the `rhat`/`ess`/`divergent` triple. Inspect tree-depth/energy separately — see Energy
diagnostics below and `idata.sample_stats["tree_depth"]` / `reached_max_tree_depth`.) If
`azs.diagnose` is not available (arviz-stats < 1.0.0), fall back to the manual checks below.

## R-hat

Measures agreement across chains. Uses the rank-normalized split-R-hat (ArviZ default).

| R-hat | Interpretation | Action |
|---|---|---|
| ≤ 1.01 | Chains have converged | Proceed |
| 1.01–1.05 | Possibly not converged | Run longer, investigate |
| > 1.05 | Not converged | Do NOT use results. Diagnose |

**Common causes of high R-hat**:
- Insufficient warmup (increase `num_warmup`)
- Multimodal posterior (reparameterize or use different init)
- Model misspecification creating ridges/funnels

## Effective sample size (ESS)

The number of independent-equivalent draws. Two flavors matter:

- **ESS bulk**: Reliability of central tendency estimates (mean, median)
- **ESS tail**: Reliability of tail estimates (credible intervals, quantiles)

| ESS | Interpretation | Action |
|---|---|---|
| ≥ 100 * number of chains per chain | Sufficient for most summaries | Proceed |
| 100–100 * number of chains | Marginal | Run longer or reparameterize |
| < 100 | Unreliable | Diagnose autocorrelation, reparameterize |

**Improving ESS**:
- Increase `num_samples` (and run ≥ 4 chains)
- Reparameterize (non-centered for hierarchical models)
- Reduce posterior correlations
- Increase `target_accept_prob` (trades speed for better exploration)

## Divergences

Divergent transitions indicate the sampler encountered regions of high curvature it could not navigate. Even a few divergences (starting from 10+) can bias results. NumPyro stores them in `sample_stats["diverging"]` by default.

```python
# Count divergences
n_div = int(idata.sample_stats["diverging"].sum())

# Visualize where divergences occur. In ArviZ 1.x, divergent draws are marked AUTOMATICALLY
# (green/highlighted) — no `divergences=True` kwarg (that was ArviZ 0.23). Control via
# visuals={"divergence": ...}. Sometimes, for high-dimensional models, the full pair plot is
# unwieldy and you want to check just a few potentially problematic pairs (e.g. a population
# standard deviation in a hierarchical model).
az.plot_pair(idata, var_names=["param1", "param2"])
```

**Fix divergences in this order**:

1. **Increase `target_accept_prob`**: `NUTS(model, target_accept_prob=0.95)` — try up to 0.99
2. **Reparameterize**: Non-centered parameterization for hierarchical models. NumPyro does this with one wrapper — no hand-coded offsets:

```python
from numpyro.infer.reparam import LocScaleReparam
from numpyro.handlers import reparam

# CENTERED (can cause funnel divergences):
def model(...):
    mu = numpyro.sample("mu", dist.Normal(mu_global, sigma_group))   # funnel-prone

# NON-CENTERED (usually fixes the funnel) — wrap the SAME model:
model_nc = reparam(model, config={"mu": LocScaleReparam(0)})
# now sample `model_nc`; the trace gains `mu_decentered ~ Normal(0,1)` and `mu` becomes a deterministic.
```

3. **Stronger priors on scale parameters**: A tight prior on a group-level SD can eliminate the funnel, especially avoiding the region near 0 (if there is no group-level variation, you don't need to model it). Replace `HalfCauchy`/flat priors with `Gamma(2, ...)`, `HalfNormal`, or `Exponential`.
4. **Marginalize discrete parameters**: If possible, integrate out discrete variables analytically (use `dist.MixtureSameFamily` for mixtures), since NUTS cannot sample them.

## When sampling fails: the escalation ladder

When sampling is broken — persistent divergences, R-hat > 1.01, low ESS, or stuck/separated chains — escalate in this order, **re-checking diagnostics after each rung and stopping at the first that fixes it.** Don't jump to a model rewrite when a sampler setting would do, and don't re-run an unchanged model hoping it converges. (For divergences *specifically*, the targeted fixes above are the first thing to try; the ladder is the general path when problems persist or aren't divergence-specific.) This is the "folk theorem of statistical computing": when you have computational problems, often there's a problem with your model (Gelman et al. 2020, §5).

1. **Raise `target_accept_prob` (→ 0.95, then 0.99).** Smaller steps, fewer divergences. *Check:* divergences fall toward zero — a handful remaining with healthy R-hat/ESS is often acceptable.
2. **Change the init strategy: `NUTS(model, init_strategy=init_to_median)`** (`from numpyro.infer import init_to_median`; also `init_to_sample`, `init_to_value(values={...})`, `init_to_feasible`). Helps when a bad starting point is the failure. *Check:* chains start in-distribution (no long drift in the rank plots).
3. **Sample longer: more `num_warmup` and `num_samples`.** If ESS is the *only* failure (good R-hat, no divergences), the chain simply needs more iterations. *Check:* ESS_bulk and ESS_tail clear 100 × n_chains.
4. **Better mass matrix / warm-start.** Try `NUTS(model, dense_mass=True)` for correlated posteriors. For a warm start, fit a quick `SVI` `AutoNormal` (or `AutoLaplaceApproximation`) guide and seed NUTS from its mean via `init_to_value`, or run `blackjax.pathfinder` and use its draws. Keep NUTS as the actual sampler (these are approximations). *Check:* faster, in-distribution start; divergences/R-hat improved.
5. **Non-centered reparameterization.** The funnel fix for hierarchical models (`LocScaleReparam`, above). *Check:* funnel gone in the pairs plot; divergences cleared.
6. **Scope down to isolate the problem.** Fit a single group, drop an interaction, or simplify the likelihood to find *which* component breaks sampling. *Check:* the reduced model samples cleanly — if so, the dropped piece is the culprit; add it back deliberately.
7. **Architectural inversion — rethink the generative structure.** Re-marginalize discrete latents, re-order a mixture for identification, change the likelihood family, or restructure the hierarchy. **Pause and confirm with the user before this rung** — it changes the model's *meaning*, not just its sampling, and that decision is the user's.

If you reach rung 7 without resolution, the problem is usually identifiability, not sampling — consult the identifiability guidance and report the model as not yet trustworthy rather than interpreting a non-converged posterior.

## Trace plots and rank plots

```python
# Rank plots (preferred over raw trace plots) — pass var_names; ArviZ 1.x caps subplots
az.plot_rank(idata, var_names=["param1", "param2"])   # both stacks; ArviZ 0.23 alt: az.plot_trace(idata, kind="rank_vlines")

# What to look for:
# - Rank plots should look uniform (no spikes or gaps)
# - Traces should be "well-mixed" — all chains overlapping
# - No chains stuck in different regions
# - No obvious trends or slow drift
```

## Energy diagnostics

Energy plots detect problems the other diagnostics may miss (e.g., incomplete exploration of the typical set). **NumPyro only stores the energy statistic if you ask for it** — request it in `mcmc.run`:

```python
# at sampling time:
mcmc.run(rng_key, x, y=y, extra_fields=("energy", "diverging", "num_steps", "accept_prob"))
# ...then:
az.plot_energy(idata)

# What to look for:
# - Marginal energy and energy transition distributions should overlap
# - Large gap between them indicates poor exploration
```

Without `extra_fields=("energy", ...)`, `az.plot_energy(idata)` raises `AttributeError: ... has no attribute 'energy'`.

## Automated diagnostics workflow

The recommended approach is `arviz_stats.diagnose()` (see Quick diagnostic checklist above). It checks R-hat, ESS, and divergences in one call — with sensible defaults that match our thresholds.

For a script-based workflow, use `diagnose_model.py`:

```bash
python scripts/diagnose_model.py --idata model_output.nc
```

Or inline (this last approach doesn't require `arviz_stats.diagnose()`):

```python
def run_diagnostics(idata):
    """Run all convergence diagnostics. Returns dict of results."""
    summary = az.summary(idata)
    num_chains = int(idata.posterior.sizes["chain"])
    results = {
        "rhat_max": float(summary["r_hat"].max()),
        "rhat_ok": bool((summary["r_hat"] <= 1.01).all()),
        "ess_bulk_min": int(summary["ess_bulk"].min()),
        "ess_tail_min": int(summary["ess_tail"].min()),
        "ess_ok": bool((summary["ess_bulk"] >= 100 * num_chains).all() and (summary["ess_tail"] >= 100 * num_chains).all()),
        "n_divergences": int(idata.sample_stats["diverging"].sum()),
        "divergences_ok": int(idata.sample_stats["diverging"].sum()) == 0,
    }
    results["all_ok"] = results["rhat_ok"] and results["ess_ok"] and results["divergences_ok"]
    return results
```
