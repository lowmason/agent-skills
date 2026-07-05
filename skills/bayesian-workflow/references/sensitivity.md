# Prior/Likelihood Sensitivity Analysis

Power-scaling sensitivity analysis checks whether your posterior conclusions are robust to reasonable changes in prior (or likelihood) strength — without refitting the model. It uses Pareto-smoothed importance sampling (PSIS) to simulate what would happen if you made your priors stronger or weaker.

## Contents
- Requirements
- Computing the `log_prior` group in NumPyro (the key step)
- Running sensitivity checks
- Interpreting results
- A caveat for reparameterized models
- Which variables to check
- Visual diagnostics
- Key principle

## Requirements

The InferenceData object must contain both a `log_likelihood` group and a `log_prior` group.

- **`log_likelihood`**: pass `log_likelihood=True` to `az.from_numpyro(...)` (or compute it with `numpyro.infer.log_likelihood` and attach it).
- **`log_prior`**: NumPyro does **not** produce this group, and `az.from_numpyro` has no option for it. You must compute it yourself — see the next section.

```python
assert "log_likelihood" in [g.strip("/") for g in idata.groups], \
    "Missing log_likelihood — pass log_likelihood=True to az.from_numpyro(...)"
assert "log_prior" in [g.strip("/") for g in idata.groups], \
    "Missing log_prior — attach it with add_log_prior(...) below"
```

## Computing the `log_prior` group in NumPyro (the key step)

The prior log-density of each latent site, evaluated at every posterior draw, is exactly what
power-scaling needs. Re-trace the model with each posterior draw substituted in, read each
sample site's `log_prob` (skipping the observed/likelihood sites), and attach the result as a
`log_prior` group. `jax.vmap` makes this fast.

```python
import numpy as np
import jax
import xarray as xr
from numpyro.handlers import trace, substitute

def add_log_prior(idata, model, mcmc, *model_args, **model_kwargs):
    """Attach a `log_prior` group so power-scaling sensitivity (psense) can run.

    For each posterior draw, substitute the latent values into the model, trace it, and
    record each *non-observed* sample site's prior log-density. Dims are reused from the
    posterior group so the new group aligns for psense.
    """
    samples = mcmc.get_samples(group_by_chain=True)          # {site: (chain, draw, ...)}
    chains, draws = next(iter(samples.values())).shape[:2]
    flat = {k: v.reshape((chains * draws,) + v.shape[2:]) for k, v in samples.items()}

    def per_draw(params):
        tr = trace(substitute(model, params)).get_trace(*model_args, **model_kwargs)
        return {name: site["fn"].log_prob(site["value"])
                for name, site in tr.items()
                if site["type"] == "sample" and not site.get("is_observed", False)}

    lp = jax.vmap(per_draw)(flat)
    post = idata["posterior"].dataset
    data_vars = {}
    for name, v in lp.items():
        if name not in post:
            continue
        arr = np.asarray(v).reshape((chains, draws) + v.shape[1:])
        # log_prob reduces over event dims, so multivariate sites (MVN, LKJ,
        # Dirichlet) yield ONE log-prior value per batch element — pair the
        # array with the leading posterior dims only.
        data_vars[name] = (post[name].dims[:arr.ndim], arr)
    idata["log_prior"] = xr.DataTree(
        xr.Dataset(data_vars, coords={"chain": post.chain, "draw": post.draw})
    )
    return idata

# Use the SAME model function and the SAME data you fitted with:
idata = add_log_prior(idata, model, mcmc, x, y=y)
```

The recipe is exact: per-site `log_prob` matches `scipy.stats.*.logpdf` to floating-point
precision. For multivariate sites it is the site's joint log-density (reduced over event
dims) — one value per batch element, which is exactly what psense needs. For a BlackJAX run (no `mcmc` object), pass the constrained posterior samples
through the same `trace(substitute(...))` loop — the mechanism is identical.

## Running sensitivity checks

```python
import arviz as az

summary = az.psense_summary(idata)   # also available as arviz_stats.psense_summary
summary
```

This returns a per-variable table with prior and likelihood power-scaling sensitivity values
(based on the Cumulative Jensen-Shannon / power-scaling diagnostic). Values above the threshold
(default 0.05) flag sensitivity — roughly a noticeable shift in the posterior under a small
change in prior or likelihood strength. Scope it with `var_names` to get tidy per-parameter rows:

```python
az.psense_summary(idata, var_names=["beta", "sigma"])
```

## Interpreting results

Four diagnostic patterns:

| Pattern | Prior | Likelihood | What it means | What to do |
|---------|-------|------------|---------------|------------|
| **Low sensitivity** | < 0.05 | < 0.05 | Posterior is robust to prior/likelihood changes | Nothing — this is the ideal outcome |
| **Prior-data conflict** | > 0.05 | > 0.05 | Prior and data pull in different directions | Investigate whether the prior reflects genuine domain knowledge or is just wrong. Consider empirically-scaled priors (e.g., `β ~ Normal(0, 2.5 * sd_y / sd_x)`) |
| **Strong prior / weak likelihood** | > 0.05 | < 0.05 | Prior dominates the posterior | Check if this is intentional (e.g., strong domain constraint). If not, weaken the prior or collect more data |
| **Likelihood-driven** | < 0.05 | > 0.05 | Data dominates the posterior | Usually fine — note in report for transparency |

## A caveat for reparameterized models

When you non-center with `LocScaleReparam`, the *sample site* in the trace is the standardized
`*_decentered ~ Normal(0, 1)`, and the interpretable group effect becomes a `deterministic`. The
`add_log_prior` recipe therefore power-scales the **decentered** `Normal(0, 1)` prior — which is
exactly the prior the model literally specifies, but it is *not* the centered `Normal(mu, sigma)`
your intuition attaches to the group effect. Two consequences:

- Sensitivity rows appear under the `*_decentered` names, not the original parameter name.
- To assess sensitivity of the *centered* hierarchical prior (e.g. the group-level SD), power-scale
  the top-level hyperpriors (`sigma_global`, `mu_global`) — those are the meaningful knobs.

This is a feature, not a bug: psense reports the prior the sampler actually used. Just be explicit
about it when you interpret the table.

## Which variables to check

Not every parameter needs sensitivity analysis. Focus on what matters:

- **Check**: interpretable coefficients, effect sizes, predictions, derived quantities (e.g., Bayesian R², contrasts)
- **Skip**: group-specific parameters in hierarchical models (power-scale only the top-level hyperpriors), spline/GP basis coefficients, variance components you don't interpret directly

For hierarchical models, sensitivity of the hyperprior (e.g., the group-level standard deviation) is more informative than sensitivity of individual group effects.

```python
# Check only specific variables
summary = az.psense_summary(idata, var_names=["beta", "sigma"])
```

## Visual diagnostics

### `plot_psense_dist` — How the posterior shifts

Shows posterior marginals at several power-scaling levels. Use this to see the *direction and magnitude* of the shift, not just whether it exceeds the threshold.

```python
from arviz_plots import plot_psense_dist

plot_psense_dist(idata, var_names=["beta"])
```

Requires `arviz-plots` (`pip install arviz-plots`).

### `plot_psense_quantities` — Sensitivity of derived quantities

Shows how predictions or summary statistics shift under perturbation. Use this when you care more about predictive robustness than individual parameter sensitivity.

```python
from arviz_plots import plot_psense_quantities

plot_psense_quantities(idata)
```

## Key principle

**Sensitivity warnings are not automatic problems.** An intentionally informative prior — grounded in domain knowledge or previous studies — will legitimately flag as sensitive. That's expected: if you have a strong prior and modest data, the prior *should* matter.

The correct response to a sensitivity flag is:
1. **Document** the flag and its magnitude
2. **Justify** why the prior is appropriate (or acknowledge it isn't)
3. **Report** the sensitivity transparently — readers should know which conclusions depend on prior choices

Do not reflexively loosen priors to silence diagnostics. A well-justified informative prior that flags sensitivity is better science than a vague prior that passes all checks but encodes no knowledge.
