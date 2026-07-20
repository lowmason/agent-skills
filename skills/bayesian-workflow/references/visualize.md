# Visualization in the Bayesian Workflow

This guide translates **Gabry, Simpson, Vehtari, Betancourt & Gelman (2019), "Visualization in
Bayesian workflow"** (*J. R. Statist. Soc. A*, 182:389–402) into ArviZ. The paper's thesis: the
*same* visualization tools belong at *every* stage of an analysis — exploration, prior checking,
computation, model checking, and comparison — not just at the end. Its figures are made with the
R package **bayesplot**; below, each is mapped to its ArviZ 1.x equivalent.

The running example in the paper estimates global PM₂.₅ air-pollution exposure by calibrating
sparse ground monitors against a satellite product, building a small **network of models**
(Model 1: pooled linear regression; Models 2 & 3: multilevel by WHO super-region / by clustered
region). Keep that framing in mind: visualization is how you *navigate* the network of models.

## bayesplot → ArviZ correspondence (quick reference)

| Paper figure | Purpose | bayesplot | ArviZ 1.x |
|---|---|---|---|
| Fig 1, 3 | EDA: data + per-group structure | (ggplot2) | matplotlib/seaborn + `az.plot_dist` |
| Fig 4 | Prior predictive realizations | `ppc_dens_overlay` (prior) | `azp.plot_ppc_dist(idata, group="prior_predictive")` |
| Fig 5a, 11a | Bivariate scatter marking divergences | `mcmc_scatter` | `az.plot_pair(idata, var_names=[...])` (divergences auto-marked) |
| Fig 5b, 11b | Parallel-coordinates of divergences | `mcmc_parcoord` | `az.plot_parallel(idata, var_names=[...])` |
| Fig 6 | Posterior predictive density overlay | `ppc_dens_overlay` | `azp.plot_ppc_dist(idata)` |
| Fig 7 | Test-statistic histogram (skew) | `ppc_stat` | `azp.plot_ppc_tstat(idata, t_stat=...)` |
| Fig 8 | Test statistic within groups | `ppc_stat_grouped` | `azp.plot_ppc_tstat(idata, coords={...})` per group |
| Fig 9 | LOO-PIT calibration overlay | `ppc_loo_pit` | `azp.plot_loo_pit(idata)` |
| Fig 10a | Pointwise ELPD difference | (loo + ggplot2) | diff `loo.elpd_i`, plot manually |
| Fig 10b | Pareto-k̂ per observation | (loo) | `az.plot_khat(loo)` |

Assumes the standard objects from the workflow: an `idata` from `az.from_numpyro(..., log_likelihood=True)`
(NumPy-converted via `idata.map_over_datasets(lambda ds: ds.as_numpy())`), with `prior`,
`prior_predictive`, `posterior_predictive`, and `observed_data` groups attached. `azp` is `arviz_plots`.

---

## 1. Exploratory data analysis goes beyond just plotting the data (§2)

EDA is not just "plot the data" — it is how you build a **network of increasingly complex models**
that can capture the heterogeneity in the data (Gelman 2004). In the paper, plotting per-region
regression lines (Fig 3) revealed that a single linear trend is insufficient and risks **Simpson's
paradox** (a trend that reverses once data are grouped) — which is what motivated the multilevel
models.

ArviZ focuses on the *model* side, so EDA is mostly plain matplotlib/seaborn plus a few ArviZ helpers:

```python
import numpy as np
import matplotlib.pyplot as plt
import arviz as az

# Raw relationship, colored by candidate grouping (Fig 1b / 3)
for grp in np.unique(group_idx):
    m = group_idx == grp
    plt.scatter(x[m], y[m], s=8, label=str(grp))
    # fit + draw a per-group line to expose heterogeneity / Simpson's paradox

# Marginal distribution of an observed variable
az.plot_dist(observed_values)            # ArviZ density of the raw outcome
```

**What to look for / do:** structure that a single pooled model would miss (per-group slopes that
differ, sparse groups that need borrowing of strength). Let it define a *small network* of models
to carry forward — not one "final" model.

## 2. Fake data can be almost as valuable as real data: prior predictive checks (§3, Fig 4)

A model with proper priors is **generative**: it implies a prior marginal distribution over data.
Simulate from it and check the *implied data* against domain knowledge — **not** against the
observed data. A prior is *weakly informative in the joint sense* if its prior predictive draws
could be any dataset you might plausibly see, with some mass on extreme-but-possible data and none
on the impossible.

```python
import arviz as az
import arviz_plots as azp
import numpy as np
from numpyro.infer import Predictive

prior_pred = Predictive(model, num_samples=500)(jax.random.PRNGKey(0), x)   # obs=None => draws y

# Pre-fit there is no model trace, so `az.from_numpyro` cannot separate the observed site from
# the latent ones and never emits a `prior_predictive` group. Build the groups explicitly; the
# leading chain axis makes ArviZ 1.x's default `sample_dims=('chain', 'draw')` apply, which is
# also what lets the flip book below index `.isel(chain=..., draw=...)`.
pp = {k: np.asarray(v)[None, ...] for k, v in prior_pred.items()}
idata_prior = az.from_dict(
    {'prior': {k: v for k, v in pp.items() if k != 'y_obs'},
     'prior_predictive': {'y_obs': pp['y_obs']}},
    coords=coords,
    dims={'y_obs': ['obs']},
)

# Fig 4: realizations from the prior — one density per simulated dataset. No `observed_data`
# group is supplied, since plot_ppc_dist would overlay it and the prior is judged against domain
# knowledge, not the data; ArviZ's "always uses the `observed_data` group" warning is expected.
azp.plot_ppc_dist(idata_prior, group='prior_predictive')
```

The paper contrasts **vague** priors (`β ~ N(0,100)`, `τ² ~ Inv-Gamma(1,100)`), which generate
physically impossible data, with **weakly informative** priors centered on a calibrated satellite
model — far more plausible, yet still able to produce more-extreme-than-expected data. Reproduce
that comparison by overlaying two prior predictive runs.

**The "flip book."** The paper recommends flipping through many individual simulated datasets to
feel the variability and multivariate structure of the prior. Loop over draws and plot each:

```python
ypp = idata_prior.prior_predictive["y_obs"]          # (chain, draw, obs)
for d in range(8):
    plt.figure(); plt.hist(ypp.isel(chain=0, draw=d).values, bins=30)
```

**Decision rule:** if simulated data are routinely impossible → tighten priors; if they can never
reach plausible extremes → priors too tight. (See also [references/priors.md](priors.md).)

## 3. Graphical MCMC diagnostics: moving beyond trace plots (§4, Fig 5; supplement Fig 11)

Trace plots help *after* a numerical summary (R̂, ESS) flags a problem, but for HMC/NUTS you can do
much better: **divergences localize the geometry the sampler can't explore.** A *cluster* of
divergences in a region of parameter space signals high curvature (a funnel); scattered divergences
with no pattern are often false positives.

In ArviZ 1.x, divergent draws are highlighted **automatically** (no `divergences=True` kwarg — that
was ArviZ 0.23). Request divergences are stored by default in NumPyro's `sample_stats["diverging"]`.

```python
import arviz as az

# Fig 5a / 11a — bivariate scatter marking divergences (bayesplot mcmc_scatter).
# Plot a scale parameter against a level parameter; for a funnel, view tau on the log scale.
az.plot_pair(idata, var_names=["tau", "theta"])           # divergences auto-marked

# Fig 5b / 11b — parallel coordinates of divergent trajectories (bayesplot mcmc_parcoord).
az.plot_parallel(idata, var_names=["theta", "tau"])

# Supporting numerical-summary visuals:
az.plot_trace(idata, var_names=["mu", "tau"])             # mixing
az.plot_rank(idata, var_names=["mu", "tau"])              # rank uniformity (preferred over raw trace)
az.plot_energy(idata)                                     # needs extra_fields=("energy", ...) at run time
```

**The funnel and its fix (supplement, 8-schools).** When divergences pile up where a hierarchical
scale `τ → 0` and the group effects `θ_j` flatten, that is the centered-parameterization funnel.
Re-parameterize non-centered — one line in NumPyro: `reparam(model, config={"theta": LocScaleReparam(0)})`.
After the fix, the cluster of divergences in `plot_pair`/`plot_parallel` should disappear. (See
[references/diagnostics.md](diagnostics.md) and [references/hierarchical.md](hierarchical.md).)

**What to look for:** a *concentration* of divergences in a neighborhood (real geometric pathology,
needs reparameterization or stronger priors) vs. divergences distributed like the non-divergent
draws (likely false positives).

## 4. Posterior predictive checks are vital for model evaluation (§5, Figs 6–9)

Once fitted, a good model should generate data that resemble what you observed. PPCs are mostly
**qualitative**, and most powerful when the checked feature is **not** one the model fits directly.

### 4a. Density overlay (Fig 6) — bayesplot `ppc_dens_overlay`

Overlay the observed outcome density against many posterior-predictive replications.

```python
import arviz_plots as azp
azp.plot_ppc_dist(idata)        # observed density vs. predictive replications
```

In the paper, this immediately shows the multilevel models (2, 3) reproduce the `log(PM₂.₅)`
distribution far better than the pooled model (1).

### 4b. Test-statistic checks (Fig 7) — bayesplot `ppc_stat`

Compare a test statistic `T(y_rep)` to the observed `T(y)`. The paper checks **skewness** for a
Gaussian model (a feature the model does *not* directly fit, so the check has power).

```python
azp.plot_ppc_tstat(idata, var_names="y_obs", t_stat="std")      # spread
azp.plot_ppc_tstat(idata, var_names="y_obs", t_stat="median")   # center
# t_stat accepts the named stats "mean"/"std"/"median"/"min"/"max" and a quantile string ("0.25").
# (Pass var_names to restrict to the observed variable; otherwise group-dim deterministics in the
#  posterior_predictive group can break the reduction.)

# Fig 7 checks SKEWNESS — a custom statistic that plot_ppc_tstat's built-ins don't cover.
# Compute it directly: the skew of each predictive replication vs. the observed skew.
import scipy.stats, matplotlib.pyplot as plt
yrep = idata.posterior_predictive["y_obs"].stack(sample=("chain", "draw")).values   # (obs, sample)
skew_rep = scipy.stats.skew(yrep, axis=0)
skew_obs = scipy.stats.skew(idata.observed_data["y_obs"].values)
plt.hist(skew_rep, bins=40); plt.axvline(skew_obs, color="k", lw=2, label="observed")
plt.xlabel("skew(y_rep)"); plt.legend()
```

Choose statistics **orthogonal to the model parameters** — a statistic tied to a fitted parameter
(e.g. the mean for a Gaussian location model) has little power to detect misfit.

### 4c. Grouped test statistics (Fig 8) — bayesplot `ppc_stat_grouped`

Check a statistic *within* levels of a grouping variable (the paper checks medians within region).
Subset the InferenceData by group and check each:

```python
for grp in idata.observed_data["group"].values:        # if a group coord exists
    azp.plot_ppc_tstat(idata.sel(group=grp), t_stat="median")
# or pass coords=... to restrict the plot to one group's observations.
```

The two multilevel models fit the within-group medians markedly better than the pooled model.

### 4d. LOO-PIT calibration (Fig 9) — bayesplot `ppc_loo_pit`

Leave-one-out PIT values are asymptotically uniform for a calibrated model. Compare their ECDF to
the uniform with simultaneous bands:

```python
azp.plot_loo_pit(idata)                 # LOO-PIT ECDF vs uniform (needs log_likelihood)
azp.plot_loo_pit(idata, coverage=True)  # same idea in coverage units
azp.plot_ppc_pit(idata)                 # the non-LOO (PPC) version
```

**The shape is meaningful** (and the paper reads it directly): a "frown" / ∪ in the deviation means
the univariate predictive distributions are **too broad** (over-dispersed) — exactly what Models 2
and 3 show, suggesting further sub-division of regions would help. (Edge effects near 0 and 1 from
the density estimator can be discounted.) See [references/model-criticism.md](model-criticism.md).

## 5. Pointwise plots for predictive model comparison (§6, Fig 10)

Visual PPCs also surface **unusual observations** — outliers (hard to predict) and high-leverage
points (influential). Both are diagnosed pointwise from LOO.

### 5a. Pointwise ELPD difference (Fig 10a)

Diff the per-observation ELPD of two models and plot it (color by group, as the paper does for WHO
clusters). Positive values favor the first model.

```python
loo2 = az.loo(idata_m2, pointwise=True)
loo3 = az.loo(idata_m3, pointwise=True)
elpd_diff = loo3.elpd_i.values - loo2.elpd_i.values        # >0 => Model 3 better for that point

plt.axhline(0, color="0.6", lw=1)
plt.scatter(np.arange(elpd_diff.size), elpd_diff, s=12)
plt.xlabel("observation"); plt.ylabel("ELPD(M3) − ELPD(M2)")
```

In the paper, Model 3 edges out Model 2, especially on hard observations like the lone Mongolian
monitor.

### 5b. Pareto-k̂ influence diagnostic (Fig 10b)

The PSIS-LOO k̂ per observation flags points whose left-out predictive distribution is very different
from the full-data one — i.e. **highly influential** observations.

```python
loo = az.loo(idata, pointwise=True)
az.plot_khat(loo)                       # pass the LOO object, not the InferenceData
# points with k̂ > 0.7 (or > loo.good_k) are influential / unreliable for LOO
```

The paper's Model 2 flags the single Mongolian observation (k̂ large); under the better-resolved
Model 3 its k̂ drops to ~0.5. Investigating such points is "a critical part of any statistical
workflow" — they hint at what the model is missing (nonlinearity, heavier tails).

---

## Discussion: visualization as workflow glue (§7)

The paper closes by noting that visualization lets you **set priors, check computation, evaluate
fit, compare models, and iteratively improve** — while guarding against the risk of "using the data
twice." Two disciplines it recommends, which this skill enforces elsewhere:

- **Prior predictive checks** should aim for a data-generating process *broader* than the observed
  data (don't cleave priors to the data) — see [references/priors.md](priors.md).
- **Posterior predictive checks** should be paired with careful checks for influential points and
  with model extensions that are *weakly informative extensions centered on the previous model* —
  see [references/model-criticism.md](model-criticism.md) and [references/model-comparison.md](model-comparison.md).

Use these plots at *every* stage, not only to present a finished model.
