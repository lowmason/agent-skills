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

Measured against the skill on 2026-10-03 (re-measure whenever this file or
the skill changes; a stale coverage claim is worse than none): 78 fenced
python blocks, all 78 parse. 4 are norun-exempt and 40 are advisory --
18 name-incomplete, 9 naming variables outside the fixtures, 7 model-body
fragments, 6 elided with `...`. That leaves 34 blocks that --run executes,
5 of them through the `comparison` fixture. 3 of the 34 are def-only: they
define functions they never call, so they show only that the definitions
compile (diagnostics.md's run_diagnostics, hierarchical.md's centered,
model-criticism.md's expected_calibration_error and ranked_probability_score).

THIS FILE IS A SECOND SOURCE OF TRUTH and can go green wrongly: a fixture
simpler than the doc's example can make a doc-level error pass. Keep the
fixtures shaped like the skill's running example, and edit this file whenever
a snippet's assumed context changes.

FIXTURE_VARS is the honesty half. It names every variable the fixture's
InferenceData carries, in any group: the posterior sites `beta` and `sigma`,
the observed site `y_obs`, and `diverging`, which the MCMC run records into
sample_stats through extra_fields. check_snippets.runnable() refuses any block
naming a variable outside it, so a snippet written against a DIFFERENT
running example (`param1`, `alpha`/`delta`, `tau`/`theta`) is reported as
needing its own fixture rather than executed and blamed for the mismatch.
`param1`/`param2` are placeholders for the reader's own parameters and are
never added. Widen the fixture and this set together, never one alone;
test_every_fixture_var_is_carried_by_the_fixture_idata pins the set against
the fixture.

NAMED_FIXTURES holds per-block fixtures for blocks written against more than
the running example. A block opts in with `fixture=<name>` in its fence info
string (```python fixture=comparison); its code runs between PREAMBLE and the
block. A name not defined here fails the gate at every tier.
'''

from typing import NamedTuple


class Fixture(NamedTuple):
    '''A per-block fixture a block selects with `fixture=<name>` in its fence
    info string. `code` runs after PREAMBLE, so it may use every name the
    preamble binds. `variables` are the fixture variables it adds to
    FIXTURE_VARS -- the same honesty rule: widen the code and the set together.'''
    code: str
    variables: frozenset


FIXTURE_VARS = frozenset({'beta', 'sigma', 'y_obs', 'diverging'})

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
posterior_samples = mcmc.get_samples()   # {site: (draws, ...)}, as log_likelihood takes it
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

COMPARISON_FIXTURE = '''
# Two more fits of the running example, differing only in the prior on beta
# or in the likelihood, so every site keeps its shape and the preamble's
# coords/dims still apply. model-comparison.md compares three such fits.
def model_wide(x=x, y=None):
    beta = numpyro.sample("beta", dist.Normal(0, 10).expand([x.shape[1]]).to_event(1))
    sigma = numpyro.sample("sigma", dist.HalfNormal(1))
    with numpyro.plate("obs", x.shape[0]):
        numpyro.sample("y_obs", dist.Normal(x @ beta, sigma), obs=y)

def model_robust(x=x, y=None):
    beta = numpyro.sample("beta", dist.Normal(0, 1).expand([x.shape[1]]).to_event(1))
    sigma = numpyro.sample("sigma", dist.HalfNormal(1))
    with numpyro.plate("obs", x.shape[0]):
        numpyro.sample("y_obs", dist.StudentT(4, x @ beta, sigma), obs=y)

def fit(variant, key):
    run = MCMC(NUTS(variant), num_warmup=100, num_samples=200, num_chains=1,
               progress_bar=False)
    run.run(key, x, y=y)
    return run

mcmc_1 = mcmc
mcmc_2 = fit(model_wide, jax.random.PRNGKey(1))
mcmc_3 = fit(model_robust, jax.random.PRNGKey(2))
idata_1, idata_2, idata_3 = (
    az.from_numpyro(run, log_likelihood=True, coords=coords, dims=dims)
    for run in (mcmc_1, mcmc_2, mcmc_3))
models = {"m1": idata_1, "m2": idata_2, "m3": idata_3}

# Deliberately shape-agnostic aliases: visualize.md's pointwise-ELPD block
# only diffs the per-observation ELPD of two fits over the same observations,
# so any two of these fits satisfy what it assumes.
idata_m2, idata_m3 = idata_2, idata_3
'''

# Per-block fixtures, keyed by the name a block selects. Only the blocks that
# select one pay for its extra fits; the shared PREAMBLE stays fast.
NAMED_FIXTURES: dict[str, Fixture] = {
    'comparison': Fixture(code=COMPARISON_FIXTURE, variables=frozenset()),
}

PINNED = (
    # Verified resolving 2026-09-08. Refresh deliberately and re-record.
    'arviz==1.3.0', 'arviz-base', 'arviz-stats==1.3.2', 'arviz-plots==1.3.1',
    'numpyro==0.21.0', 'jax==0.11.1', 'numpy', 'matplotlib',
)
