# Hierarchical (Multilevel) Models

## Contents
- When to use hierarchical models
- Partial pooling intuition
- Centered vs. non-centered parameterization
- Common hierarchical structures
- Diagnostics specific to hierarchical models
- Identifiability checks

## When to use hierarchical models

Use hierarchical models when data has **grouped structure** — observations nested within units (students in schools, games in seasons, patients in hospitals, items in categories). Careful: time series data is not hierarchical because timestamps are not interchangeable (they have an order). Tell users that if they have time series data, they should use time series models instead.

The [NumPyro Bayesian hierarchical linear regression tutorial](https://num.pyro.ai/en/stable/tutorials/bayesian_hierarchical_linear_regression.html) and the [eight-schools example](https://num.pyro.ai/en/stable/examples/baseball.html) are good references.

The key question: Do groups share information? If group-level parameters are related (e.g., batting averages across players), hierarchical models borrow strength across groups through partial pooling.

## Partial pooling intuition

Three approaches to grouped data:

- **Complete pooling**: Ignore groups, fit one model. Misses group-level variation. Maximum bias.
- **No pooling**: Fit separate models per group. Overfits small groups. Maximum variance.
- **Partial pooling** (hierarchical): Groups share a common distribution. Small groups shrink toward the global mean; large groups retain their own estimate and influence the global population. Trades off worse in-sample coverage for better out-of-sample performance.

Partial pooling is almost always the right choice. It naturally handles imbalanced group sizes.

## Centered vs. non-centered parameterization

This is the most common source of divergences in hierarchical models. In NumPyro, the data
(`group_idx`, `y`) are function arguments, and group structure is expressed with `numpyro.plate`.

```python
import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist

# CENTERED — works well when groups have lots of data
def centered(group_idx, y=None, n_groups=None):
    mu_global = numpyro.sample("mu_global", dist.Normal(0, 10))
    sigma_global = numpyro.sample("sigma_global", dist.Gamma(2, 2))
    with numpyro.plate("group", n_groups):
        mu_group = numpyro.sample("mu_group", dist.Normal(mu_global, sigma_global))
    sigma_obs = numpyro.sample("sigma_obs", dist.Gamma(2, 2))
    with numpyro.plate("obs", group_idx.shape[0]):
        numpyro.sample("y_obs", dist.Normal(mu_group[group_idx], sigma_obs), obs=y)
```

```python
# NON-CENTERED — works well when groups have little data.
# Two equivalent ways. (a) explicit offset:
def noncentered(group_idx, y=None, n_groups=None):
    mu_global = numpyro.sample("mu_global", dist.Normal(0, 10))
    sigma_global = numpyro.sample("sigma_global", dist.Gamma(2, 2))
    with numpyro.plate("group", n_groups):
        mu_raw = numpyro.sample("mu_raw", dist.Normal(0, 1))
    mu_group = numpyro.deterministic("mu_group", mu_global + mu_raw * sigma_global)
    sigma_obs = numpyro.sample("sigma_obs", dist.Gamma(2, 2))
    with numpyro.plate("obs", group_idx.shape[0]):
        numpyro.sample("y_obs", dist.Normal(mu_group[group_idx], sigma_obs), obs=y)

# (b) reparam wrapper — keep `centered` above and let NumPyro do the offset:
from numpyro.infer.reparam import LocScaleReparam
from numpyro.handlers import reparam
noncentered = reparam(centered, config={"mu_group": LocScaleReparam(0)})
# the trace then contains `mu_group_decentered ~ Normal(0,1)`; `mu_group` becomes deterministic.
```

**Rule of thumb**: Start with non-centered. Switch to centered only if non-centered shows poor ESS AND groups have substantial data (50+ observations each).

## Common hierarchical structures

### Varying intercepts

Each group has its own baseline, partially pooled toward a global mean.

```python
with numpyro.plate("group", n_groups):
    mu_group = numpyro.sample("mu_group", dist.Normal(mu_global, sigma_global))
with numpyro.plate("obs", group_idx.shape[0]):
    numpyro.sample("obs", dist.Normal(mu_group[group_idx], sigma_obs), obs=y)
```

### Varying intercepts and slopes

Each group has its own baseline AND its own effect of a predictor. Use `LKJCholesky` for the
correlation between intercept and slope.

```python
import jax.numpy as jnp

# correlated varying effects (preferred). n=2 => intercept + one slope.
L_omega = numpyro.sample("L_omega", dist.LKJCholesky(2, concentration=2.0))
sd = numpyro.sample("sd", dist.Exponential(jnp.ones(2)))
scale_tril = sd[..., None] * L_omega                       # Cholesky of the 2x2 covariance

mu_intercept = numpyro.sample("mu_intercept", dist.Normal(0.0, 5.0))
mu_slope = numpyro.sample("mu_slope", dist.Normal(0.0, 1.0))
loc = jnp.stack([mu_intercept, mu_slope])

with numpyro.plate("group", n_groups):
    effects = numpyro.sample("effects", dist.MultivariateNormal(loc, scale_tril=scale_tril))
# effects[:, 0] are intercepts, effects[:, 1] are slopes
# expected value per obs:
# mu = effects[group_idx, 0] + effects[group_idx, 1] * slope_data
```

For a non-centered version of correlated effects, sample `z ~ Normal(0, 1)` of shape `(n_groups, 2)`
and set `effects = loc + z @ scale_tril.T` inside a `numpyro.deterministic`.

### Nested hierarchy

Groups within groups (students in classrooms in schools). Don't go overboard — models become unwieldy and hard to sample and interpret with too many hierarchies.

```python
with numpyro.plate("school", n_schools):
    mu_school = numpyro.sample("mu_school", dist.Normal(mu_global, sigma_global))
with numpyro.plate("class", n_classes):
    mu_class = numpyro.sample("mu_class", dist.Normal(mu_school[school_idx], sigma_school))
with numpyro.plate("obs", class_idx.shape[0]):
    numpyro.sample("y", dist.Normal(mu_class[class_idx], sigma_student), obs=data)
```

## Diagnostics specific to hierarchical models

In addition to standard diagnostics (references/diagnostics.md), check:

1. **Shrinkage plot**: Visualize how much each group is pulled toward the global mean
2. **Group-level SD posterior**: If `sigma_group` or `sigma_global` posterior piles up near zero, the data may not support group-level variation (partial pooling → complete pooling)
3. **Funnel plot**: Plot group-level means vs. group-level SD. Funnels indicate centered parameterization problems — view with `az.plot_pair(idata, var_names=["mu_group", "sigma_global"])` (divergences are marked automatically).

```python
import matplotlib.pyplot as plt

# Shrinkage plot (work from the xarray-backed InferenceData)
group_means_posterior = idata.posterior["mu_group"].mean(dim=["chain", "draw"]).to_numpy()
group_means_obs = [y[group_idx == g].mean() for g in range(n_groups)]

plt.scatter(group_means_obs, group_means_posterior)
plt.plot([min(group_means_obs), max(group_means_obs)],
         [min(group_means_obs), max(group_means_obs)], "r--", label="No pooling")
plt.axhline(np.mean(y), color="gray", linestyle=":", label="Complete pooling")
plt.xlabel("Observed group mean")
plt.ylabel("Posterior group mean")
plt.legend()
plt.title("Shrinkage toward global mean")
```

---

## Identifiability checks

A model component is **identifiable** only if the data can distinguish its effect from other components. In hierarchical models, identifiability failures are common and subtle — the model samples fine, diagnostics pass, but individual component posteriors reflect prior assumptions, not data signal.

### Common identifiability traps

1. **Separate intercept + offset when the offset is always active**: If every observation has a characteristic (e.g., every match row is from the home team's perspective), you cannot separately estimate a "baseline" intercept and a "home advantage" offset — only their sum is identified. Merge them into a single intercept.

2. **Overparameterized intercepts**: Group-level intercepts + a global intercept without a sum-to-zero constraint creates a "trading" pattern where the global intercept can shift arbitrarily as group intercepts compensate. Use `dist.ZeroSumNormal(scale, event_shape=(n_groups,))` for group intercepts, or drop the global intercept.

3. **Collinear covariates at the group level**: If a group-level predictor is nearly constant within groups (e.g., all teams in a league share the same league-level feature), it is confounded with the group intercept.

### How to detect

```python
# Check posterior correlations between suspect components.
# In ArviZ 1.x divergences are marked automatically; `marginal=True` shows the diagonal.
az.plot_pair(idata, var_names=["alpha", "delta"], marginal=True)
# If correlation is near ±1 → components are not separately identifiable
```

### What to do

- **Merge confounded components** into a single term (honest about what the data can tell you)
- **Add identifying variation** to the data (e.g., include away-team observations to separate home advantage from league baseline)
- **Accept the constraint**: if you need both components for interpretability, acknowledge that their individual posteriors are prior-driven and report only their sum
