# Convergence Diagnostics

## Contents
- Quick diagnostic checklist
- Exploration runs vs. the final run
- R-hat
- Effective sample size (ESS)
- Divergences
- Failure signatures
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
# diagnostics contains: "divergent", "ess", "rhat", "bfmi"  (bfmi present because the flow above requested energy)

# 3. Visual check — pass var_names; ArviZ 1.x caps the subplot count
az.plot_trace(idata, var_names=["param1", "param2"])
```

`arviz_stats.diagnose` (>= 1.0.0) checks **R-hat, ESS, divergences, AND E-BFMI (energy)** in one
call whenever the `energy` sample stat is present — which our sampling flow guarantees via
`extra_fields=("energy", ...)`. So you do NOT need a separate manual E-BFMI inspection on this
path; a clean `azs.diagnose` result already covers energy. (Earlier PyMC-stack guidance also
mentioned tree-depth here. Tree-depth is the one check `diagnose` skips on the
numpyro/`az.from_numpyro` path: it looks for a `reached_max_treedepth` sample stat, but
`az.from_numpyro` emits `reached_max_tree_depth` instead, so the tree-depth branch never fires.
Inspect tree-depth separately via `idata.sample_stats["tree_depth"]` — see Energy diagnostics
below.) If `azs.diagnose` is not available (arviz-stats < 1.0.0), fall back to the manual checks
below.

## Exploration runs vs. the final run

Most fits in a workflow are provisional: a good many will look like bad choices once you know more, and there is no route to the model you keep that skips them (Gelman et al. 2026, §2.1). Size each run to the question you are asking of it (§11.4, §12.1, §12.4):

| Phase | Settings | Accept when |
|---|---|---|
| **Exploring** — does this model fit at all? does the new component break sampling? | `num_warmup=200, num_samples=200, num_chains=4` (raise to 500/500 only if warmup is visibly unfinished) | R-hat ≤ 1.1, no chain stuck or drifting, divergences ≤ ~1% — enough to decide *keep / change / discard* |
| **Final** — the numbers go in the report | `num_warmup=1000, num_samples=1000, num_chains=4` (the template default) | R-hat ≤ 1.01, ESS_bulk and ESS_tail ≥ 100 × n_chains, zero divergences, **and** relative MCSE small enough for the digits you will report (`diagnostics.json → precision`; see reporting.md → Reporting principles 6) |

This is the "fit fast, fail fast" rule (§12.1): a model that is slow or badly behaved at 200 draws will not be rescued by 2000, and long chains on a model you are still debugging spend compute on a posterior you will throw away. When a big model is slow, the book's own advice (§12.4) is to fit on simulated data, build up from a smaller model, run few iterations, fit on a subset of the data, and stop leaving the coefficient and group-level-scale priors vague (a little information in each is enough) — *then* run long. Report numbers only from a final-phase run; if a report has to be built from an exploration run, say so in it.

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
| ≥ 100 * number of chains | Sufficient for most summaries | Proceed |
| < 100 * number of chains | Unreliable | Run longer, reparameterize, or diagnose autocorrelation |

**Improving ESS**:
- Increase `num_samples` (and run ≥ 4 chains)
- Reparameterize (non-centered for hierarchical models)
- Reduce posterior correlations
- Increase `target_accept_prob` (trades speed for better exploration) — for divergence-driven ESS loss only, and only when divergences are ≤ ~1% of transitions (see the gate below)

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

1. **Only when divergences are ≤ ~1% of post-warmup transitions, increase `target_accept_prob`**: `NUTS(model, target_accept_prob=0.95)` — try up to 0.99. Above ~1% a smaller step size trades a fast wrong fit for a slow wrong fit (Gelman et al. 2026, §12.3) — the next action is `az.plot_pair` on the flagged scale and one of its children (above), and the Failure signatures table then picks among 2–4.
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

3. **Stronger priors on scale parameters**: A tight prior on a group-level SD can eliminate the funnel, (if there is no group-level variation, you don't need to model it). Replace `HalfCauchy` — proper, but heavy-tailed enough to let the scale run very large — or a genuinely improper flat prior with `Gamma(2, ...)`, `HalfNormal`, or `Exponential`. `HalfNormal`/`Exponential` help by cutting the tail rather than by avoiding 0 (both actually carry more mass near 0 than `HalfCauchy`); `Gamma(2, ...)` is the one whose density vanishes at 0.
4. **Marginalize discrete parameters**: If possible, integrate out discrete variables analytically (use `dist.MixtureSameFamily` for mixtures), since NUTS cannot sample them.

## Failure signatures

What the diagnostics look like for the common ways a fit goes wrong, what each usually means, and where to look in a NumPyro model (Gelman et al. 2026, §12.3). Read this table before touching a sampler setting: the fix is almost always in the model.

| Signature | Usual cause | Check / fix in NumPyro |
|---|---|---|
| Chains drift to ±1e20, R-hat ≈ 3, most transitions hit max tree depth (read that one yourself from `idata.sample_stats["tree_depth"]` — it is the check `azs.diagnose` skips on the `from_numpyro` path, above) | **Improper or near-improper posterior** — a site under `dist.ImproperUniform`, or a `Normal(0, 100)`-class prior on a logistic coefficient whose classes are separated | Give every site a proper prior on the scale the parameter actually lives on (`Normal(0, 2.5)` for a standardized logistic coefficient). Raising `max_tree_depth` never helps here |
| One site's marginal is indistinguishable from its prior — no shrinkage, no correlation with anything — while everything else converges; only under an improper prior (`dist.ImproperUniform`) does it random-walk without bound | **Unused parameter** — sampled but never reaches the likelihood (a typo, or a branch that never uses it), so nothing but its prior constrains it | `numpyro.render_model(model, model_args=...)` shows the orphan node with no path to `y_obs`; delete the site or wire it in |
| Sampling slow (many leapfrog steps), ESS lower than expected, *no* warnings; pair plot shows a straight-line ridge with correlation ≈ ±1 | **Aliased parameters** — two sites play one role: an intercept plus a constant predictor column; item ability vs. item difficulty with no anchor; mixture components that swap labels (K! equivalent modes), or mixture weights identified only through their sum until the components separate | Only a sum, a ratio, or an unordered set is identified. Drop one, anchor a reference level, use a sum-to-zero contrast, or add a prior that separates them — see the identifiability rule in SKILL.md |
| Slow, bulk-ESS in the low hundreds where thousands are expected, strong intercept–slope correlation | **Uncentered predictors** — the intercept means "outcome at x = 0", far outside the data | Center (and scale) predictors before the fit; the book's own regression example gains ~3× ESS and >20× speed from centering alone. `dense_mass=True` is the second-best fix |
| R-hat ≫ 1 on a location parameter with **tail-ESS far above bulk-ESS**, bimodal histogram, chains flat at different values | **Multimodal posterior** — chains stuck in separate modes (mixture, non-log-concave likelihood, heavy-tailed prior) | More chains from dispersed inits to map the modes; then decide whether the extra modes carry mass (stack chains by LOO weight — Yao, Vehtari & Gelman 2022) or are artifacts to exclude by inits or priors. An `ordered` constraint fixes mixture label switching |
| Two chains fine, two stuck at their initial values; `-inf`/NaN log-density at init | **Overflow at initialization** — NumPyro's default `init_to_uniform` (radius 2 on the unconstrained scale) plus predictors far from unit scale gives `exp(huge)` | Scale predictors to unit scale, or `NUTS(model, init_strategy=init_to_median)` / `init_to_value(values={...})` / `init_to_uniform(radius=0.1)`. Not a step-size problem |
| R-hat near threshold, low ESS, and slow mixing with *no* other warning; rank histograms visibly uneven | **Varying curvature** — thick-tailed priors on unconstrained parameters (`Cauchy` on a regression coefficient), or a thin-tailed posterior | Use `Normal` or `StudentT` with moderate `df` on unconstrained parameters. `HalfCauchy` on a *positive* scale is fine *for curvature* — the log transform NumPyro applies tames the tail — but the fix-list above still objects to it for a different reason (it lets the scale run large) |
| Divergences cluster where a group-level scale → 0; `log(sigma)` vs a group mean is a funnel | **Funnel** — hierarchical prior with a weak per-group likelihood | Non-centered `LocScaleReparam` (Divergences, above). If per-group data are *strong*, non-centering hurts — keep centered; mixed strength → per-group choice |
| NaN log-density or a failed initialization (`Cannot find valid initial parameters`), some divergences — no warning text, because NumPyro's default `validate_args=False` lets a negative scale through silently | **Scale parameter left unconstrained** — a `Normal` prior on `sigma` instead of `HalfNormal`/`LogNormal`/`Exponential` | NumPyro derives the constraint from the *prior's support*, so the fix is the prior family, never a manual `jnp.abs` |

Moves that help regardless of signature (§12.4): a **weak-prior probe** (`Normal(0, 100)` on everything shows what blows up when nothing holds it), a **strong-prior probe** (pin parameters near plausible values, then loosen one at a time), **simplify from both ends** (fit models simpler than yours until one works and more complex than the working one until it breaks — the bug lives in between), and the **fake-data check** (simulate from known parameters, refit, recover — model-criticism.md → SBC).

## When sampling fails: the escalation ladder

When sampling is broken — persistent divergences, R-hat > 1.01, low ESS, or stuck/separated chains — first match the symptoms against the Failure signatures table, then escalate in this order, **re-checking diagnostics after each rung and stopping at the first that fixes it.** Don't jump to a model rewrite when a sampler setting would do, and don't re-run an unchanged model hoping it converges. This is the "folk theorem of statistical computing": computational trouble is usually a symptom of a modelling problem, not a call for more compute (Gelman et al. 2026, §12.4).

1. **Read the divergence fraction before touching the sampler.** `pct = 100 * n_div / (num_chains * num_samples)`. **If `pct` ≤ 1 and R-hat/ESS are otherwise healthy** → raise `target_accept_prob` (→ 0.95, then 0.99): smaller steps clear a few divergences at a curvature edge. *Check:* divergences fall toward zero — a handful remaining with healthy R-hat/ESS is often acceptable. **If `pct` > 1, or the divergences come with R-hat > 1.05 or ESS far below threshold** → do not raise `target_accept_prob` and do not raise `max_tree_depth`: at that level the geometry or the identification is wrong, and a smaller step only makes the wrong posterior slower to sample (Gelman et al. 2026, §12.3). **Next action — one plot, before any refit:** `az.plot_pair(idata, var_names=["<flagged scale>", "<one of its children>"])` (divergent draws are marked automatically; if no neck shows, plot the log of the scale). Then match the picture to the Failure signatures table and apply that row's fix — a neck → rung 5, a straight ridge → the aliasing row, no shape → rung 6. The printed summary cannot settle whether the per-group likelihood is strong enough to keep the centered form; the plot can — so plot before you decide.
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
