# Prior Selection Guide

## Contents
- Philosophy: why priors matter
- PyMC → NumPyro distribution map
- Weakly informative priors (the default)
- Prior families by parameter type
- Sparsity priors (high-dimensional regression)
- Prior predictive checking workflow
- Common mistakes

## Philosophy: why priors matter

Priors encode domain knowledge and constrain the model to plausible regions of parameter space. The goal is NOT to be "non-informative" — it is to be **honestly informative** while avoiding undue influence on the posterior when data is sufficient.

Every prior should have a justification. If you cannot articulate why a prior is reasonable, it is not a good prior.

Think of priors as a ladder rather than a binary "informative vs. non-informative": flat (improper) → super-vague proper → very weakly informative → generic weakly informative → specific informative. Choosing a prior is choosing how much subject-matter information to include (Gelman et al. 2020, §7.3). And a prior can only be understood **in the context of the likelihood** — reason about the *joint* prior over all parameters, not one marginal at a time, and as the model grows, tighten priors so a fixed information budget isn't spread too thin.

## PyMC → NumPyro distribution map

NumPyro uses **scipy-style** arguments (`loc`/`scale`, `concentration`/`rate`) and lives in
`numpyro.distributions` (imported as `dist`). A model site is `numpyro.sample("name", dist.X(...))`,
with `obs=` for the likelihood. There is no `pm.Data` container — data are function arguments.

| PyMC | NumPyro | Notes |
|---|---|---|
| `pm.Normal("x", mu, sigma)` | `dist.Normal(mu, sigma)` | `loc`, `scale` (same order) |
| `pm.HalfNormal("x", sigma)` | `dist.HalfNormal(sigma)` | `scale` |
| `pm.Gamma("x", alpha, beta)` | `dist.Gamma(alpha, beta)` | `concentration`, `rate` |
| `pm.Exponential("x", lam)` | `dist.Exponential(lam)` | `rate` |
| `pm.Beta("x", alpha, beta)` | `dist.Beta(alpha, beta)` | `concentration1`, `concentration0` |
| `pm.StudentT("x", nu, mu, sigma)` | `dist.StudentT(nu, mu, sigma)` | `df`, `loc`, `scale` |
| `pm.Cauchy` / `pm.HalfCauchy` | `dist.Cauchy` / `dist.HalfCauchy` | |
| `pm.LogNormal("x", mu, sigma)` | `dist.LogNormal(mu, sigma)` | |
| `pm.Bernoulli("x", p)` | `dist.Bernoulli(probs=p)` | use `logits=` for the logit link |
| `pm.Binomial("x", n, p)` | `dist.Binomial(total_count=n, probs=p)` | `logits=` for logit link |
| `pm.Poisson("x", mu)` | `dist.Poisson(mu)` | `rate` |
| `pm.NegativeBinomial("x", mu, alpha)` | `dist.NegativeBinomial2(mean=mu, concentration=alpha)` | mean/dispersion form; `GammaPoisson` is the rate/conc form |
| `pm.ZeroInflatedPoisson("x", psi, mu)` | `dist.ZeroInflatedPoisson(gate=1-psi, rate=mu)` | **`gate` = P(structural zero)**, the complement of PyMC's `psi` |
| `pm.ZeroInflatedNegativeBinomial(...)` | `dist.ZeroInflatedNegativeBinomial2(gate, mean, concentration)` | or `dist.ZeroInflatedDistribution(base, gate=...)` generically |
| `pm.OrderedLogistic("x", eta, cutpoints)` | `dist.OrderedLogistic(eta, cutpoints)` | `predictor`, `cutpoints` |
| `pm.Truncated(d, lower, upper)` | `dist.TruncatedNormal(loc, scale, low, high)` or `dist.TruncatedDistribution(base, low, high)` | base limited to Normal/StudentT/Cauchy/Laplace/Logistic |
| `pm.Censored(d, lower, upper)` | no built-in — add log-CDF mass with `numpyro.factor` | see Censoring note below |
| `pm.MvNormal("x", mu, chol=L)` | `dist.MultivariateNormal(mu, scale_tril=L)` | also `covariance_matrix=` / `precision_matrix=` |
| `pm.LKJCholeskyCov(...)` | `dist.LKJCholesky(dim, eta)` + separate scales | combine into `scale_tril` (see below) |
| `pm.ZeroSumNormal("x", sigma, dims)` | `dist.ZeroSumNormal(scale, event_shape=(k,))` | enforces sum-to-zero over the last `event_shape` |
| `pm.Dirichlet("x", a)` | `dist.Dirichlet(a)` | |
| `pm.Deterministic("x", expr)` | `numpyro.deterministic("x", expr)` | stored in the trace |
| `pm.math.switch` / `pt.where` | `jax.numpy.where` (`jnp.where`) | no Python `if` on traced values |

**Censoring** has no one-liner in NumPyro. Add the censored-observation log-mass by hand:
for a right-censored point at `c`, the contribution is `log P(Y > c) = log(1 - cdf(c))`, added
with `numpyro.factor("censored", base_dist.log_prob(...))` or an explicit survival term. For
**truncation**, prefer the built-in `TruncatedNormal` / `TruncatedDistribution`.

## Weakly informative priors (the default)

When in doubt, use weakly informative priors. These place most mass on plausible values while still allowing the data to dominate.

**Principle**: A good weakly informative prior rules out nonsense values but does not strongly favor any particular reasonable value.

The [PreliZ package](https://preliz.readthedocs.io/en/latest/) is your friend when it comes to choosing priors. PreliZ is framework-agnostic — it helps you pick distributions and parameters, which you then translate into `numpyro.distributions` using the map above.

Here are some general rules of thumb:

### Regression coefficients

```python
# if you standardize predictors first -- makes priors comparable
beta = numpyro.sample("beta", dist.Normal(0, 2.5))   # on standardized scale

# if on raw scale with known range: scale ≈ expected_range / 4
beta_raw = numpyro.sample("beta_raw", dist.Normal(0, (plausible_max - plausible_min) / 4))
```

### Scale parameters (standard deviations)

```python
# Gamma avoiding near-zero values: good default
sigma = numpyro.sample("sigma", dist.Gamma(2, 2))      # concentration=2, rate=2

# HalfNormal / Exponential: when you want to favor smaller values
sigma = numpyro.sample("sigma", dist.HalfNormal(1))
sigma = numpyro.sample("sigma", dist.Exponential(1))
```

### Intercepts

```python
# Center on observed data mean when possible
intercept = numpyro.sample("intercept", dist.Normal(y_mean, 2 * y_std))
```

### Correlation matrices (hierarchical models)

NumPyro samples a Cholesky factor of the correlation matrix with `LKJCholesky`, then scales it:

```python
import jax.numpy as jnp

# eta=1 is uniform over correlation matrices; eta=2 pulls toward identity
L_omega = numpyro.sample("L_omega", dist.LKJCholesky(k, concentration=2.0))
sd = numpyro.sample("sd", dist.Exponential(jnp.ones(k)))          # per-dimension scales
scale_tril = sd[..., None] * L_omega                              # Cholesky of the covariance
# use as: dist.MultivariateNormal(mu, scale_tril=scale_tril)
```

## Prior families by parameter type

| Parameter type | Recommended prior | Why |
|---|---|---|
| Location (unbounded) | `Normal` | Symmetric, well-understood |
| Location (positive) | `LogNormal`, `Gamma` | Naturally positive |
| Scale / SD | `Gamma`, `HalfNormal`, `Exponential` | Positive, controls spread |
| Proportion (0–1) | `Beta` | Bounded, flexible shape |
| Correlation matrix | `LKJCholesky` | Proper prior on correlation structure |
| Count rate | `Gamma`, `LogNormal` | Positive, flexible |
| Degrees of freedom (StudentT) | `Gamma(2, 0.1)` or `Exponential(1/30)` + shift | Keeps ν reasonable (not too low, not → ∞) |
| Ordinal cutpoints | `Normal` with ordered transform | Maintains ordering (`dist.TransformedDistribution` with an `OrderedTransform`, or `numpyro.distributions.transforms.OrderedTransform`) |
| Categorical predictors or Group-level intercepts | `ZeroSumNormal` | Ensures sum to zero and avoids over-parametrization. Similar to reference-encoding but more appropriate when no obvious placebo/reference category exists |

## Sparsity priors (high-dimensional regression)

When you have many features and expect only a subset to be relevant, use a sparsity-inducing prior instead of a shared Normal. These adaptively shrink irrelevant coefficients toward zero while preserving signal from important ones.

### When to use sparsity priors

| Situation | Prior recommendation |
|-----------|---------------------|
| Few features (< ~10), all plausibly relevant | `Normal(0, σ)` — sparsity is overkill |
| Many features, expected sparsity | Regularized Horseshoe or R2-D2 |
| Many features, want interpretable R² | R2-D2 |
| Variable selection (hard zeros) | Use a BART-style model or projection-predictive selection instead — spike-and-slab is rarely worth the complexity |

### Regularized Horseshoe (Finnish Horseshoe)

The go-to sparsity prior. Shrinks irrelevant features toward zero ("spike") while allowing strong signals through ("slab"). Always use the **regularized** variant (Piironen & Vehtari, 2017) — the original horseshoe has a double-funnel geometry that causes divergences.

```python
import jax.numpy as jnp

D = X.shape[1]   # number of features
N = X.shape[0]   # number of observations
p0 = 5           # prior guess for number of relevant features

# Global shrinkage — controls overall sparsity
tau = numpyro.sample("tau", dist.HalfCauchy(p0 / (D - p0) / jnp.sqrt(N)))

# Local shrinkage — per-feature (vectorized over D via the batch shape)
lam = numpyro.sample("lam", dist.HalfCauchy(jnp.ones(D)))

# Slab — regularizes large coefficients (prevents the double-funnel)
c2 = numpyro.sample("c2", dist.InverseGamma(1, 1))

# Effective shrinkage
lam_tilde = jnp.sqrt(c2 * lam**2 / (c2 + tau**2 * lam**2))

# Coefficients (non-centered)
beta_raw = numpyro.sample("beta_raw", dist.Normal(jnp.zeros(D), 1))
beta = numpyro.deterministic("beta", beta_raw * tau * lam_tilde)
```

`dist.HalfCauchy` is the textbook horseshoe choice for `tau`/`lam`; for the exact half-Student-t
of Piironen & Vehtari, use a left-truncated StudentT (`dist.TruncatedDistribution(dist.StudentT(nu, 0., s), low=0.)`).

Key hyperparameter: `p0` (expected number of relevant features). This controls the global shrinkage `tau`. Be honest about your prior belief — setting `p0` too high defeats the purpose of sparsity.

**Practical tip**: With horseshoe models, always use `target_accept_prob=0.95` or higher on the NUTS kernel.

**Feature importance with horseshoe**: After fitting, compute `P(|β| > threshold)` per feature to rank practical significance:

```python
beta_samples = idata.posterior["beta"].values   # (chains, draws, D)
threshold = 0.05                                 # adjust based on scale
prob_relevant = (np.abs(beta_samples) > threshold).mean(axis=(0, 1))
```

### R2-D2 prior

An alternative where you specify prior beliefs about the total R² (variance explained) rather than per-feature shrinkage. More interpretable when you have a prior sense of overall model fit.

```python
import jax.numpy as jnp

# Prior on R² (proportion of variance explained)
R2 = numpyro.sample("R2", dist.Beta(1, 1))            # uniform on [0, 1] — adjust based on domain

# Concentration across features (Dirichlet allocates the explained variance)
phi = numpyro.sample("phi", dist.Dirichlet(jnp.ones(D)))

# Coefficient variances derived from R²
sigma2_y = numpyro.sample("sigma2_y", dist.HalfNormal(1))   # residual variance
tau2 = R2 / (1 - R2) * sigma2_y * phi

beta = numpyro.sample("beta", dist.Normal(jnp.zeros(D), jnp.sqrt(tau2)))
```

Use R2-D2 when:
- You have domain knowledge about how much variance the model should explain
- You want a more interpretable parameterization than the horseshoe
- The horseshoe's funnel causes persistent divergences even with regularization

## Prior predictive checking workflow

This is mandatory. Never skip it. Run the model through `Predictive` **without** observed data
(so the likelihood site draws `y`), then visualize.

```python
import arviz as az
import arviz_plots as azp
import numpy as np
from numpyro.infer import Predictive

prior_pred = Predictive(model, num_samples=500)(jax.random.PRNGKey(0), x)   # no y => draws y_obs

# `az.from_numpyro` cannot be used here: with no MCMC trace it cannot tell the observed site
# apart from the latent ones, so it raises `sample_dims must be provided if posterior is None`
# and — once that is silenced — emits only a `prior` group, never `prior_predictive`. Assemble
# the groups explicitly, adding a leading chain axis so ArviZ 1.x's default
# `sample_dims=('chain', 'draw')` applies.
pp = {k: np.asarray(v)[None, ...] for k, v in prior_pred.items()}
idata_prior = az.from_dict(
    {'prior': {k: v for k, v in pp.items() if k != 'y_obs'},
     'prior_predictive': {'y_obs': pp['y_obs']}},
    coords=coords,
    dims={'y_obs': ['obs']},
)

# Visualize (group='prior_predictive'); az.plot_ppc was removed from the ArviZ 1.x umbrella.
# Deliberately supply no `observed_data` group: plot_ppc_dist overlays it when present, and a
# prior check is judged against domain knowledge, not against the data. ArviZ still emits a
# "This plot always uses the `observed_data` group" UserWarning — expected here, safe to ignore.
azp.plot_ppc_dist(idata_prior, group='prior_predictive')   # one curve per simulated dataset

# Check: do simulated datasets look plausible?
# - Are values in a reasonable range?
# - Is the spread of outcomes reasonable?
# - Are there impossible values (negative counts, proportions > 1)?
```

A prior leads to a **weakly informative joint data-generating process** if its prior predictive
draws could represent any dataset you might plausibly observe — with some mass on extreme-but-possible
data and none on the clearly impossible (Gabry et al. 2019). Judge the prior predictive against
domain knowledge, **not** against the observed data.

**Decision rule**:
- If >10% of prior predictive samples are clearly implausible → tighten priors
- If prior predictions are extremely narrow → priors may be too informative, consider loosening
- If prior predictions are reasonable → proceed to inference

## Common mistakes

1. **Flat / diffuse priors** (e.g., `Normal(0, 1000)`): These are NOT "non-informative". They place excessive mass on extreme, implausible values and can cause sampling issues. Use weakly informative priors instead. Note that "vague" priors on parameters can be wildly informative on the *observable* scale — always check on the data scale.

2. **Ignoring scale**: A `Normal(0, 10)` prior means very different things depending on the scale of the data. Always consider the units.

3. **Forgetting to standardize predictors**: Without standardization, coefficients live on different scales, making shared priors inappropriate and slowing sampling. This is not always true, but it is a common mistake.

4. **No prior predictive check**: The single most common source of modeling errors. Always visualize what your priors imply before fitting.

5. **Informative priors without justification**: If you use a tight prior, you need a clear reason (previous study, physical constraint, domain expertise). Document it.
