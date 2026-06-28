# State-Space and Dynamic Models

## Contents
- When to use state-space models
- The core decision: marginalize the latent path vs. sample it
- Marginalize: the Kalman filter and the dynamax handoff
- Sample the path: scan + non-centered innovations
- Common state-space structures
- Choosing the inference method
- Common gotchas

## When to use state-space models

Use a state-space model when an **ordered** latent process generates the data: a continuous
state `x_t` evolves over time and you observe a noisy function of it. Tracking, denoising,
nowcasting, and decomposable forecasting (level + trend + seasonal) are all state-space problems
(PML2 §8.2, PML2 §29.12).

Time series are **not** hierarchical — timestamps have an order and are not interchangeable, so the
partial-pooling machinery in [references/hierarchical.md](hierarchical.md) does not apply.
What *does* carry over is the parameterization lesson: the centered-vs-non-centered choice there is
the same fork you face here, one level up — see the core decision below.

The [NumPyro time series tutorial](https://num.pyro.ai/en/stable/tutorials/time_series_forecasting.html)
and the `numpyro.contrib.control_flow.scan` primitive are the entry points for the sampled-path route;
[dynamax](https://github.com/probml/dynamax) is the entry point for the marginalized route.

**Discrete latent state?** If the latent process is a regime label rather than a continuous value
(segmentation, changepoints, regime-switching), you want a hidden Markov model (PML2 §29.2), not a
Gaussian state space. Marginalize the discrete states with `config_enumerate` /
`MixtureSameFamily` — the same "marginalize or enumerate, don't plug in" rule the main SKILL.md
states for discrete latents. The changepoint notebook
`notebooks/book2/29/supplementary/hmm_poisson_changepoint_jax.ipynb` is a worked JAX example.

## The core decision: marginalize the latent path vs. sample it

A state-space model has `T` latent states `x_1..x_T` plus a handful of static parameters `θ`
(noise scales, transition coefficients, loadings). **The single biggest mistake is putting all `T`
latent states into the sampler when you don't have to.** The path is a long, highly autocorrelated
chain — exactly the funnel-prone geometry NUTS handles worst — and for a linear-Gaussian model you
never need to sample it: the Kalman filter integrates it out in closed form, leaving NUTS to explore
only the low-dimensional `θ`.

So the fork is: **is the model linear and Gaussian?**

```python
# MARGINALIZE — when transition AND observation are linear-Gaussian.
# The Kalman filter returns log p(y | θ) exactly (prediction-error decomposition);
# NUTS samples only the static θ. The T states are integrated out — never in the sampler.
# (See "Marginalize: the Kalman filter and the dynamax handoff".)

# SAMPLE THE PATH — when a non-Gaussian likelihood or non-linear transition rules out Kalman.
# Build the path with scan, and NON-CENTER the innovations so the geometry stays sane.
# (See "Sample the path: scan + non-centered innovations".)
```

**Rule of thumb**: Marginalize whenever the latent dynamics *and* the observation are linear-Gaussian
— this is the default, and it does not get worse as `T` grows because the states are never sampled.
Sample the path only when a non-Gaussian likelihood (counts, binary, heavy tails) or a non-linear
transition forces it. The discriminator is **categorical (is it linear-Gaussian?), not a magnitude** —
`T` decides how much sampling the path *hurts*, not which arm is correct.

## Marginalize: the Kalman filter and the dynamax handoff

For a linear-Gaussian state space the marginal likelihood `p(y | θ)` is available in closed form: the
Kalman filter factorizes it as a product of one-step-ahead predictive Gaussians (the prediction-error
decomposition). You put priors on `θ`, hand the filter the data, and add its log marginal likelihood
to the model with `numpyro.factor` — NUTS then samples `θ` alone.

The recommended machinery is **[dynamax](https://github.com/probml/dynamax)** (JAX-native SSMs), which
this skill's sibling `recommend-probabilistic-model` routes linear-Gaussian SSM recommendations to.
`LinearGaussianSSM.marginal_log_prob(params, emissions)` runs the filter and returns the scalar log
marginal likelihood, ready to drop into a NumPyro model:

```python
# HANDOFF SKETCH — dynamax must be installed separately (`pip install dynamax`); it is not a
# bayesian-workflow dependency. The marginal_log_prob CALL below is the verified API; the params
# CONTAINER is a dynamax ParamsLGSSM pytree whose construction is dynamax-version-specific — build
# it per the dynamax docs (https://probml.github.io/dynamax/), not from memory.
from dynamax.linear_gaussian_ssm import LinearGaussianSSM

lgssm = LinearGaussianSSM(state_dim=1, emission_dim=1)

def model(y):
    # --- Priors on the STATIC params only (sample on a stable reparam — see below) ---
    sigma_level = numpyro.sample("sigma_level", dist.HalfNormal(1))
    sigma_obs = numpyro.sample("sigma_obs", dist.HalfNormal(1))

    params = build_lgssm_params(lgssm, sigma_level, sigma_obs)   # -> dynamax ParamsLGSSM (per docs)

    # Kalman filter integrates out x_1..x_T and returns log p(y | θ); NUTS sees only θ.
    numpyro.factor("ll", lgssm.marginal_log_prob(params, y[:, None]))
```

Unlike the sampled-path model in the next section, this snippet **cannot be run inside this skill's
environment** — dynamax is not installed here — so treat it as the integration shape, not battle-tested
glue. The one verified, exact piece is `lgssm.marginal_log_prob(params, emissions) -> scalar`;
`lgssm.filter(...)` and `lgssm.smoother(...)` return the filtered / smoothed state posteriors if you
need state estimates afterward.

**Pure-NumPyro alternative (no dependency):** you can also write the Kalman recursion yourself inside
`scan`, accumulating the per-step log predictive density and adding it with `numpyro.factor` — same
marginalization, no dynamax. It is more code but keeps the stack to NumPyro/JAX; reach for it when a
new dependency is unwelcome.

**Sample θ on a stable reparameterization**, never raw matrix entries:

- **Covariance / noise matrices** — sample a Cholesky factor (`dist.LKJCholesky` for correlation plus
  positive scales), not the raw entries, so the matrix stays positive-definite by construction.
- **Autoregressive coefficients** — enforce stationarity by keeping the companion-matrix eigenvalues
  inside the unit circle (for AR(1), just `|phi| < 1`). Sample `phi` on `(-1, 1)` (e.g.
  `2 * dist.Beta(...) - 1`); for higher orders use a partial-autocorrelation (PACF) parameterization
  rather than priors on raw lag coefficients.

The Kalman filter is exact *only* for linear-Gaussian models. Mild non-linearity → extended/unscented
Kalman filters (PML2 §8.3, PML2 §8.4); strong non-linearity or heavy tails → particle filters (PML2 §13.2).
Past that point you are sampling the path anyway, so go to the next section.

## Sample the path: scan + non-centered innovations

When the model is not linear-Gaussian, build the latent path explicitly with
`numpyro.contrib.control_flow.scan`. The transition function has signature `(carry, x_t) -> (carry, y_t)`;
the observations ride in as scan's iterate so each step sees its own `y_t`, and a `length` fallback lets
the *same* model serve prior-predictive (`y=None`) and inference.

The geometry lesson from hierarchical models applies directly: **non-center the innovations.** Sample
each step's shock as `eps_t ~ Normal(0, 1)` and form the state deterministically as
`x_t = x_{t-1} + sigma * eps_t`. The centered alternative (`x_t ~ Normal(x_{t-1}, sigma)`) funnels for
the same reason centered hierarchical models do.

```python
import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
from numpyro.contrib.control_flow import scan
from numpyro.infer import MCMC, NUTS, Predictive
import arviz as az

numpyro.set_host_device_count(4)   # MUST precede the first JAX op (e.g. PRNGKey) or it silently no-ops

RANDOM_SEED = sum(map(ord, "local-level-nowcast"))
rng_key = jax.random.PRNGKey(RANDOM_SEED)

# LOCAL LEVEL — random walk in the level plus observation noise.
def local_level(y=None, T=None):
    sigma_level = numpyro.sample("sigma_level", dist.HalfNormal(1))   # innovation scale
    sigma_obs = numpyro.sample("sigma_obs", dist.HalfNormal(1))       # measurement scale
    x0 = numpyro.sample("x0", dist.Normal(0, 5))

    def transition(x_prev, y_t):
        eps = numpyro.sample("eps", dist.Normal(0, 1))                # NON-CENTERED innovation
        x = x_prev + sigma_level * eps                                # state, built deterministically
        numpyro.sample("y_obs", dist.Normal(x, sigma_obs), obs=y_t)   # obs=None => draws at prior time
        return x, x

    length = T if y is None else None     # y rides in as xs at fit time; length drives prior-predictive
    _, x_path = scan(transition, x0, y, length=length)
    return x_path
```

The sample sites inside the transition pick up a leading time axis automatically — `eps` and `y_obs`
come back shaped `(draw, T)` — so map the time dimension when you convert to ArviZ (it is **`["time"]`,
not `["obs"]`):

```python
k_prior, k_mcmc = jax.random.split(rng_key)

# Prior predictive: no y, so length drives the scan.
prior_pred = Predictive(local_level, num_samples=500)(k_prior, y=None, T=len(y_data))

mcmc = MCMC(NUTS(local_level), num_warmup=1000, num_samples=1000, num_chains=4,
            chain_method="parallel")
mcmc.run(k_mcmc, y=y_data, T=None)

idata = az.from_numpyro(mcmc, prior=prior_pred, coords={"time": np.arange(len(y_data))},
                        dims={"y_obs": ["time"]})
idata = idata.map_over_datasets(lambda ds: ds.as_numpy())
```

A few hard JAX rules inside the transition:

- **Use `jnp.where`, never a Python `if`** for data-dependent branches — JAX traces the function once,
  so a Python conditional won't execute per-step.
- **The carry must be a JAX type** (a scalar, array, or tuple of them). A tuple threads a multi-state
  vector cleanly — see local linear trend below.

## Common state-space structures

### Local level

Random walk in an unobserved level plus measurement noise — the workhorse nowcasting model above. One
latent state, two scales.

### Local linear trend

Level and slope both drift; the slope feeds the level. The carry is a `(level, slope)` tuple — a 2-D
state with no extra machinery — and each component gets its own non-centered innovation.

```python
def local_linear_trend(y=None, T=None):
    sigma_level = numpyro.sample("sigma_level", dist.HalfNormal(1))
    sigma_trend = numpyro.sample("sigma_trend", dist.HalfNormal(1))
    sigma_obs = numpyro.sample("sigma_obs", dist.HalfNormal(1))
    level0 = numpyro.sample("level0", dist.Normal(0, 5))
    slope0 = numpyro.sample("slope0", dist.Normal(0, 1))

    def transition(carry, y_t):
        level_prev, slope_prev = carry
        eps_level = numpyro.sample("eps_level", dist.Normal(0, 1))
        eps_slope = numpyro.sample("eps_slope", dist.Normal(0, 1))
        slope = slope_prev + sigma_trend * eps_slope
        level = level_prev + slope_prev + sigma_level * eps_level
        numpyro.sample("y_obs", dist.Normal(level, sigma_obs), obs=y_t)
        return (level, slope), level

    length = T if y is None else None
    _, level_path = scan(transition, (level0, slope0), y, length=length)
    return level_path
```

Add seasonal and regression components the same way (each an additive block in the state) to build a
full structural time series / dynamic linear model (PML2 §29.12). The `notebooks/book2/29/sts.ipynb`
notebook is the worked structural-TS example.

### Dynamic factor (a nod)

A few latent factors `f_t` evolve over time and drive many observed series through a loadings matrix
`Λ` (`y_t = Λ f_t + noise`). This is identifiable only with constraints: fix the **loadings to be
lower-triangular with positive diagonal entries** and the **factor innovation variance to 1**,
otherwise factors and loadings trade off freely (rotation, scale, and a surviving sign/reflection flip)
and the sampler wanders. This is the temporal cousin of
the identifiability traps in [references/hierarchical.md](hierarchical.md).

## Choosing the inference method

| Method | When | What it samples / geometry | Relative cost |
|---|---|---|---|
| **Marginalize + NUTS on θ** (Kalman) | Linear-Gaussian | Only the static `θ`; states integrated out — best geometry | Cheapest; sampling cost flat in `T` (each Kalman pass is O(`T`)) — **default** |
| **NUTS on the path** (`scan` + non-centered innovations) | Non-linear or non-Gaussian | `θ` plus the `T` innovations; non-centering tames the funnel | Moderate; scales with `T` |
| **Gibbs + FFBS** (Carter & Kohn 1994; Frühwirth-Schnatter 1994) | Conditionally linear-Gaussian blocks | Alternates: forward-filter backward-sample the whole path given `θ`, then `θ` given the path | Classical; largely superseded by NUTS in this stack |
| **Smoother per θ draw** (RTS) | You marginalized but still need state estimates | For each posterior `θ`, run the RTS smoother to recover `p(x \| y, θ)` | Cheap add-on; one smoother pass per draw |

Default to the first row. Drop to the second only when the likelihood or transition is not Gaussian.
The third is the classical recipe and worth recognizing in older code, but you should not reach for it
here — NUTS over the marginal (row 1) or the non-centered path (row 2) dominates it. The fourth is how
you get latent-state credible intervals *after* marginalizing: run `lgssm.smoother(...)` per draw.

## Common gotchas

- **Don't NUTS the path when you can marginalize.** This is the #1 mistake. If the model is
  linear-Gaussian, integrate the states out with the Kalman filter (`numpyro.factor` + dynamax or a
  hand-written recursion) and sample only `θ`. Sampling `T` correlated states is slower and funnels.
- **Center the innovations and you get a funnel.** Sample `eps_t ~ Normal(0, 1)` and build
  `x_t = x_{t-1} + sigma * eps_t` deterministically; do not write `x_t ~ Normal(x_{t-1}, sigma)`. Same
  pathology, same fix as centered hierarchical models. Check the usual sampler diagnostics —
  divergences and low ESS ([references/diagnostics.md](diagnostics.md)).
- **Sample θ on a stable reparameterization, not raw entries.** Cholesky factors for covariance
  matrices (stays positive-definite); roots-inside-the-unit-circle for AR coefficients (stays
  stationary). Priors on raw matrix entries or raw lag coefficients put mass on invalid models.
- **Put a stationary / informative prior on the initial state for short series.** With few timepoints
  the data barely constrain `x_0`; a diffuse `x0` prior then dominates the early path. For a stationary
  model, initialize from the stationary distribution rather than a flat prior.
- **Missing or ragged observations.** When sampling the path, pass a masked likelihood so absent
  timepoints contribute no `obs` term (e.g. `numpyro.handlers.mask`); when marginalizing, the Kalman
  filter simply skips the measurement update at missing steps. Don't impute zeros — that injects fake
  data.
- **Use `jnp.where`, not a Python `if`, inside the transition.** JAX traces `scan` once; a Python
  branch on a traced value won't execute per step.
- **The scan time axis is `["time"]`, not `["obs"]`.** Sites inside the transition come back shaped
  `(draw, T)`; map that dimension when converting (`dims={"y_obs": ["time"]}`) or ArviZ invents an
  anonymous dim and posterior-predictive plots error.
- **Dynamic-factor identifiability needs constraints.** Lower-triangular loadings (positive diagonal)
  and unit factor innovation variance, or factors and loadings rotate/rescale/sign-flip against each
  other and chains wander.

## Further reading

- Särkkä, *Bayesian Filtering and Smoothing* — the standard reference for Kalman/EKF/UKF and particle
  filtering, JAX-friendly in presentation.
- Durbin & Koopman, *Time Series Analysis by State Space Methods* — the canonical structural-time-series
  and DLM treatment.
- Carter & Kohn (1994) and Frühwirth-Schnatter (1994) — the original forward-filter backward-sample
  (FFBS) papers behind the Gibbs row above.
- [dynamax documentation](https://probml.github.io/dynamax/) — current API for `LinearGaussianSSM`,
  including `marginal_log_prob`, `filter`, and `smoother`.
