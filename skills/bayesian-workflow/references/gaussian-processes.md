# Gaussian Processes

## Contents
- When to use which GP
- Priors on the length-scale and amplitude
- Exact GP template
- Hilbert-space approximation (HSGP)
- Off-stack GP libraries

## When to use which GP

A GP puts a prior on an unknown smooth function. Pick the implementation by the number of
observations n and the input dimension D:

| Case | Use | Cost |
|---|---|---|
| n up to about 1,000 to 2,000 | Exact GP: `MultivariateNormal` over the n points | O(n³) per gradient |
| Larger n, D = 1 to 3 | HSGP from `numpyro.contrib.hsgp.approximation` | O(n·m^D), m basis functions per dimension |
| Larger n and D above 3 | Neither scales well: reduce D, or see Off-stack GP libraries | — |

Standardize the outcome and centre the inputs before either. Set the numerics policy first:
GP covariance algebra loses accuracy in float32 (see [jax-numerics.md](jax-numerics.md)).

## Priors on the length-scale and amplitude

- **Length-scale.** The data cannot inform length-scales shorter than the smallest gap between
  inputs or longer than the input range. Put most prior mass between those two numbers. An
  `InverseGamma` has light left and right tails there; choose its two parameters so that about
  1% of the mass falls below the smallest gap and about 1% above the range, and check with a
  prior predictive draw of functions.
- **Amplitude** (the marginal standard deviation of f). On a standardized outcome, `HalfNormal(1)`
  is a sound default. Shrink it when f should explain only part of the variance.
- **Noise.** `HalfNormal` on the observation scale, as for any regression.
- Fix the kernel family before fitting: squared exponential for very smooth functions, Matérn
  3/2 or 5/2 (`hsgp_matern`, `nu=1.5` or `nu=2.5`) for rougher ones, periodic for seasonal terms.
  Compare kernel families with LOO ([model-comparison.md](model-comparison.md)).

## Exact GP template

```python
import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS

numpyro.enable_x64()  # GP covariance algebra loses accuracy in float32

rng = np.random.default_rng(0)
x_gp = np.sort(rng.uniform(0, 10, 30))
y_gp = np.sin(x_gp) + rng.normal(0, 0.2, x_gp.shape[0])


def rbf_kernel(xa, xb, amplitude, length_scale):
    sq_dist = (xa[:, None] - xb[None, :]) ** 2
    return amplitude**2 * jnp.exp(-0.5 * sq_dist / length_scale**2)


def gp_model(x, y=None):
    length_scale = numpyro.sample('length_scale', dist.InverseGamma(5.0, 5.0))
    amplitude = numpyro.sample('amplitude', dist.HalfNormal(1.0))
    noise = numpyro.sample('noise', dist.HalfNormal(0.5))
    cov = rbf_kernel(x, x, amplitude, length_scale) + (noise**2 + 1e-6) * jnp.eye(x.shape[0])
    numpyro.sample('y_gp', dist.MultivariateNormal(jnp.zeros(x.shape[0]), covariance_matrix=cov), obs=y)


gp_mcmc = MCMC(NUTS(gp_model), num_warmup=300, num_samples=300, num_chains=1, progress_bar=False)
gp_mcmc.run(jax.random.PRNGKey(1), x_gp, y=y_gp)
gp_draws = gp_mcmc.get_samples()
```

The `1e-6` jitter keeps the Cholesky factorization stable. Replace the `InverseGamma(5.0, 5.0)`
with one tuned to your input spacing and range (see the priors section). The template uses one
chain to stay short; a real fit uses four (SKILL.md, step 5).

## Hilbert-space approximation (HSGP)

HSGP replaces the n×n covariance with m basis functions per input dimension on a box
[-L, L] around the centred inputs (Solin and Särkkä 2020; Riutort-Mayol et al. 2023). Two
settings control it:

- **Boundary `ell`** (L): a factor c times the largest absolute centred input. Use c of at least
  1.2; 1.5 is a safe start.
- **Basis size `m`**: more functions are needed as the length-scale gets shorter relative to L.
  Check the choice by refitting with a larger `m`: if the posterior of f or the length-scale
  moves, `m` was too small.

```python
import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
from numpyro.contrib.hsgp.approximation import hsgp_squared_exponential
from numpyro.infer import MCMC, NUTS, Predictive

numpyro.enable_x64()  # in float32 this fit diverges on most draws

rng = np.random.default_rng(0)
x_big = np.sort(rng.uniform(0, 10, 2000))
y_big = np.sin(x_big) + rng.normal(0, 0.2, x_big.shape[0])
x_shift = x_big.mean()
x_center = x_big - x_shift  # HSGP's box is centred on 0
boundary = 1.5 * float(np.abs(x_center).max())  # c = 1.5


def hsgp_model(x, y=None, ell=boundary, m=30):
    length_scale = numpyro.sample('length_scale', dist.InverseGamma(5.0, 5.0))
    amplitude = numpyro.sample('amplitude', dist.HalfNormal(1.0))
    noise = numpyro.sample('noise', dist.HalfNormal(0.5))
    f = hsgp_squared_exponential(x=x, alpha=amplitude, length=length_scale, ell=ell, m=m)
    numpyro.deterministic('f', f)
    with numpyro.plate('obs_gp', x.shape[0]):
        numpyro.sample('y_hsgp', dist.Normal(f, noise), obs=y)


hsgp_mcmc = MCMC(NUTS(hsgp_model), num_warmup=500, num_samples=300, num_chains=1, progress_bar=False)
hsgp_mcmc.run(jax.random.PRNGKey(2), x_center, y=y_big, extra_fields=('diverging',))
n_divergent = int(hsgp_mcmc.get_extra_fields()['diverging'].sum())
assert n_divergent == 0, n_divergent

# Predict at new inputs: apply the same shift, and keep `ell` and `m` unchanged.
x_new = np.linspace(0, 10, 50) - x_shift
f_new = Predictive(hsgp_model, hsgp_mcmc.get_samples())(jax.random.PRNGKey(3), x_new)['f']
assert f_new.shape == (300, 50), f_new.shape  # f recomputed at x_new, not reused
```

For a Matérn kernel use `hsgp_matern(x=x, nu=1.5, alpha=amplitude, length=length_scale,
ell=ell, m=m)`. For D > 1, pass `x` with shape (n, D) and a list for `ell` and `m`. The
functions sample an internal site named `beta` (the basis weights), so do not name a site of
your own `beta` in the same model.

## Off-stack GP libraries

GPyTorch (PyTorch) and tinygp (JAX) are outside this skill's stack: name them only when the
user's project already uses them. Sparse variational GPs (inducing points) are not covered here.
