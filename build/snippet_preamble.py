'''Fixture context for executing bayesian-workflow snippet fragments.

Shaped after the skill's own running example (SKILL.md:95): a vector `beta`
over a `feature` dim plus a scalar `sigma`, observed site `y_obs` over an
`obs` dim, with the InferenceData carrying the groups the docs assume --
log_likelihood, prior, posterior_predictive, and sample_stats.energy. The
variable NAMES are load-bearing, not decoration: priors.md reads
idata.posterior["beta"].values as (chains, draws, D), so `beta` must be a
vector, and sensitivity.md and reporting.md ask for `beta`/`sigma` by name.

Sized to be fast: 1 chain, 100 warmup / 200 draws, purely so `mcmc` and
`idata` exist with realistic structure -- it is NOT a model worth
interpreting. 200 draws is chosen to keep LOO's Pareto-k estimates sane.

Measured against the skill on 2026-09-08 (re-measure whenever this file or
the skill changes; a stale coverage claim is worse than none): 78 fenced
python blocks, all 78 parse. 4 are norun-exempt and 47 are advisory --
24 name-incomplete, 10 naming variables outside FIXTURE_VARS, 7 model-body
fragments, 6 elided with `...`. That leaves 54 preamble-bound names carrying
27 blocks that --run actually executes.

THIS FILE IS A SECOND SOURCE OF TRUTH and can go green wrongly: a fixture
simpler than the doc's example can make a doc-level error pass. Keep the
fixtures shaped like the skill's running example, and edit this file whenever
a snippet's assumed context changes.

FIXTURE_VARS is the honesty half. check_snippets.runnable() refuses any block
naming a variable outside it, so a snippet written against a DIFFERENT
running example (`param1`, `alpha`/`delta`, `tau`/`theta`) is reported as
needing its own fixture rather than executed and blamed for the mismatch.
Widen the fixture and this set together, never one alone.
'''
FIXTURE_VARS = frozenset({'beta', 'sigma', 'y_obs'})

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
k_prior, k_mcmc, k_post = jax.random.split(rng_key, 3)

N, D = 40, 3
rng = np.random.default_rng(0)
x = rng.normal(size=(N, D))
beta_true = np.array([1.0, -0.5, 0.25])
y = x @ beta_true + rng.normal(0, 0.1, N)
features = ["f0", "f1", "f2"]
coords = {"obs": np.arange(N), "feature": features}
dims = {"beta": ["feature"], "y_obs": ["obs"]}

def model(x=x, y=None):
    beta = numpyro.sample("beta", dist.Normal(0, 1).expand([x.shape[1]]).to_event(1))
    sigma = numpyro.sample("sigma", dist.HalfNormal(1))
    with numpyro.plate("obs", x.shape[0]):
        numpyro.sample("y_obs", dist.Normal(x @ beta, sigma), obs=y)

prior_pred = Predictive(model, num_samples=200)(k_prior, x)
mcmc = MCMC(NUTS(model), num_warmup=100, num_samples=200, num_chains=1,
            progress_bar=False)
mcmc.run(k_mcmc, x, y=y,
         extra_fields=("energy", "diverging", "num_steps", "accept_prob"))
post_pred = Predictive(model, mcmc.get_samples())(k_post, x)
idata = az.from_numpyro(mcmc, prior=prior_pred, posterior_predictive=post_pred,
                        log_likelihood=True, coords=coords, dims=dims)

# Copied VERBATIM from references/sensitivity.md (the `add_log_prior` block);
# test_preamble_add_log_prior_matches_the_doc pins the two equal.
# NumPyro emits no log_prior group and az.from_numpyro has no option for it,
# so the skill documents this helper -- and the fixture uses the documented
# one rather than reimplementing it, which means running the gate also
# exercises this block of the docs. Keep in sync with sensitivity.md.
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

idata = add_log_prior(idata, model, mcmc, x, y=y)
'''

PINNED = (
    # Verified resolving 2026-09-08. Refresh deliberately and re-record.
    'arviz==1.3.0', 'arviz-base', 'arviz-stats==1.3.2', 'arviz-plots==1.3.1',
    'numpyro==0.21.0', 'jax==0.11.1', 'numpy', 'matplotlib',
)
