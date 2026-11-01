# NumPyro model template

Start every model from this template; read it before you write model code.

```python
import os
import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS, Predictive
import arviz as az

numpyro.set_host_device_count(4)   # MUST precede the first JAX op (e.g. PRNGKey) or it silently no-ops

results_dir = "churn-logistic-v1"  # the <slug> folder of references/reporting.md
RANDOM_SEED = sum(map(ord, results_dir))
rng = np.random.default_rng(RANDOM_SEED)
rng_key = jax.random.PRNGKey(RANDOM_SEED)

# NumPyro has no Data container: data flows in as function arguments. Use `numpyro.plate`
# for batch dims, and map those dims to coords/dims when converting to ArviZ.
coords = {"obs": np.arange(len(df))}

def model(x, y=None):
    # --- Priors (NumPyro uses scipy-style loc/scale) ---
    # Always document WHY each prior was chosen
    mu = numpyro.sample("mu", dist.Normal(0, 10))      # weakly informative: allows wide range
    sigma = numpyro.sample("sigma", dist.HalfNormal(1))

    # --- Data model ---
    with numpyro.plate("obs", x.shape[0]):
        numpyro.sample("y_obs", dist.Normal(mu, sigma), obs=y)   # obs=None at prior-pred time

x = df["x"].to_numpy()
y = df["y"].to_numpy()
k_prior, k_mcmc, k_post = jax.random.split(rng_key, 3)

# --- Prior predictive check ---
prior_pred = Predictive(model, num_samples=500)(k_prior, x)         # no y => draws y_obs

# --- Inference (native NUTS; see Samplers for BlackJAX) ---
mcmc = MCMC(NUTS(model, target_accept_prob=0.9),
            num_warmup=1000, num_samples=1000, num_chains=4, chain_method="parallel")
mcmc.run(k_mcmc, x, y=y,
         extra_fields=("energy", "diverging", "num_steps", "accept_prob"))  # energy => plot_energy

# --- Posterior predictive check ---
post_pred = Predictive(model, posterior_samples=mcmc.get_samples())(k_post, x)

# --- Convert to ArviZ. ALWAYS map the observed/predicted variable in `dims`. ---
idata = az.from_numpyro(
    mcmc,
    prior=prior_pred,
    posterior_predictive=post_pred,
    log_likelihood=True,                       # builds the log_likelihood group (needed for LOO)
    coords=coords,
    dims={"y_obs": ["obs"]},
)
# NumPyro returns JAX arrays; convert once so in-session ArviZ ops (e.g. az.loo) don't trip
# over JAX immutability. (Reloading from netCDF also yields NumPy.)
idata = idata.map_over_datasets(lambda ds: ds.as_numpy())

# --- Compute log_prior for sensitivity checks (NumPyro does not store it). See sensitivity.md ---
idata = add_log_prior(idata, model, mcmc, x, y=y)   # helper defined in references/sensitivity.md

# --- Save immediately after sampling ---
# Late crashes can destroy valid results. Save to disk before any post-processing.
os.makedirs(results_dir, exist_ok=True)
idata.to_netcdf(os.path.join(results_dir, "inference_data.nc"))   # the path reporting and comparison read
```
