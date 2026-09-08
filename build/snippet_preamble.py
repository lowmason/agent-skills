'''Fixture context for executing bayesian-workflow snippet fragments.

Binds 23 names. Measured against the skill on 2026-09-08: of 78 fenced python
blocks, all 78 parse, 4 are norun-exempt, and of the remaining 74 this
preamble makes 38 name-complete -- 36 of which are also elision-free and so
actually execute under --run. The other 38 need per-block fixtures and are
out of scope; they are reported, never silently dropped. Re-measure these
numbers whenever this preamble or the skill changes; they are a claim about
coverage, and a stale claim is worse than none.

Sized to be fast: the MCMC here is 1 chain x 50 draws, purely so `mcmc` and
`idata` exist -- it is NOT a model worth interpreting.

THIS FILE IS A SECOND SOURCE OF TRUTH and can go green wrongly: a fixture
simpler than the doc's example can make a doc-level error pass. Keep the
fixtures shaped like the skill's running example, and edit this file whenever
a snippet's assumed context changes.
'''
PREAMBLE = '''
import os
import numpy as np
import jax, jax.numpy as jnp
import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS, Predictive
import arviz as az
import arviz_stats as azs
import arviz_plots as azp
import matplotlib.pyplot as plt

rng_key = jax.random.PRNGKey(0)
x = np.linspace(0, 1, 40)
y = 2.0 * x + np.random.default_rng(0).normal(0, 0.1, 40)
coords = {"obs": np.arange(40)}
dims = {"y": ["obs"]}

def model(x=x, y=None):
    a = numpyro.sample("a", dist.Normal(0, 1))
    b = numpyro.sample("b", dist.Normal(0, 1))
    numpyro.sample("y", dist.Normal(a + b * x, 0.1), obs=y)

mcmc = MCMC(NUTS(model), num_warmup=50, num_samples=50, num_chains=1,
            progress_bar=False)
mcmc.run(rng_key, x=x, y=y)
idata = az.from_numpyro(mcmc)
'''

PINNED = (
    # Verified resolving 2026-09-08. Refresh deliberately and re-record.
    'arviz==1.3.0', 'arviz-base', 'arviz-stats==1.3.2', 'arviz-plots==1.3.1',
    'numpyro==0.21.0', 'jax==0.11.1', 'numpy', 'matplotlib',
)
