# Samplers

Read this before you set up MCMC.

NumPyro models are sampled by NUTS implemented in JAX, which is JIT-compiled and runs on
CPU/GPU/TPU. There are two first-class, co-equal choices. The canonical template uses native
NUTS; everything downstream (`az.from_numpyro` or `az.from_dict`, diagnostics, plots) is
identical once you have an InferenceData.

**1. Native NumPyro NUTS (default).** Idiomatic, the least code, and already fast.

```python norun slow: 4 chains x 2000 draws, minutes -- not a pre-commit gate
numpyro.set_host_device_count(4)                 # required for parallel CPU chains; MUST precede the first JAX op
mcmc = MCMC(NUTS(model, target_accept_prob=0.9),
            num_warmup=1000, num_samples=1000, num_chains=4, chain_method="parallel")
mcmc.run(rng_key, x, y=y, extra_fields=("energy", "diverging", "num_steps", "accept_prob"))
idata = az.from_numpyro(mcmc, log_likelihood=True, coords=coords, dims=dims)
```

**2. BlackJAX NUTS (co-equal alternative).** A standalone JAX sampler with explicit, composable
warmup (window adaptation) and access to variants (e.g. `blackjax.pathfinder` for warm-starts).
Use it when you want fine control over adaptation or a second independent sampler to cross-check.
You drive a NumPyro model through it via its log-density, then assemble the InferenceData
yourself with `az.from_dict`:

```python norun blackjax is optional (SKILL.md:63), not a declared dependency
import blackjax
from numpyro.infer.util import initialize_model

init = initialize_model(rng_key, model, model_args=(x,), model_kwargs={"y": y}, dynamic_args=False)
logdensity = lambda position: -init.potential_fn(position)

def run_chain(key, init_pos, n_warmup=1000, n_samples=1000):
    wk, sk = jax.random.split(key)
    warmup = blackjax.window_adaptation(blackjax.nuts, logdensity, target_acceptance_rate=0.9)
    (state, params), _ = warmup.run(wk, init_pos, num_steps=n_warmup)
    kernel = blackjax.nuts(logdensity, **params)
    @jax.jit
    def step(s, k):
        s, info = kernel.step(k, s)
        return s, (s.position, info)
    _, (positions, infos) = jax.lax.scan(step, state, jax.random.split(sk, n_samples))
    return positions, infos

n_chains = 4
keys = jax.random.split(rng_key, n_chains)
init_pos = jax.tree.map(lambda v: jnp.broadcast_to(v, (n_chains,) + v.shape), init.param_info.z)
positions, infos = jax.vmap(run_chain)(keys, init_pos)              # leaves: (chain, draw, ...)

# unconstrained -> constrained (incl. deterministics) via the model's postprocess_fn
constrained = jax.vmap(jax.vmap(init.postprocess_fn))(positions)
idata = az.from_dict(
    {
        "posterior": {k: np.asarray(v) for k, v in constrained.items()},
        "sample_stats": {
            "diverging": np.asarray(infos.is_divergent),
            "energy": np.asarray(infos.energy),
            "n_steps": np.asarray(infos.num_integration_steps),
            "acceptance_rate": np.asarray(infos.acceptance_rate),
        },
        "observed_data": {"y_obs": y},
    },
    coords=coords, dims=dims,
)
```

(Compute `log_likelihood` and posterior predictive for BlackJAX runs with `numpyro.infer.log_likelihood`
and `Predictive(model, posterior_samples=...)`, then add them as groups — see model-comparison.md.)

**SVI as the final fit.** When SVI (stochastic variational inference) replaces NUTS rather than
warm-starting it, check it before you trust it: a flat ELBO (evidence lower bound) trace that every
seed reaches, PSIS-LOO for the approximation, and VSBC (variational simulation-based calibration).
See [svi.md](svi.md).

**Why not nutpie?** The PyMC-ecosystem sampler nutpie compiles **PyMC and Stan** models, not
NumPyro — there is no NumPyro entry point. With NumPyro you do not need it: native NUTS is
already JAX-JIT-compiled, and BlackJAX is the genuine "swap the sampler" alternative.

**Chains.** Unlike PyMC, NumPyro requires you to set `num_chains` explicitly (default is 1).
Use **at least 4** and call `numpyro.set_host_device_count(num_chains)` so `chain_method="parallel"`
actually runs them on separate CPU devices. Running more chains is a cheap way to cut Monte
Carlo variance and to surface multimodality (Gelman et al. 2026, §11.4). `chain_method="vectorized"`
runs all chains in one `vmap` (fast, single device, no host-count needed); `"sequential"` is the
low-memory fallback. Size the run to the phase: exploration fits at
`num_warmup=200, num_samples=200` accept R-hat ≤ 1.1 — a threshold for the keep/change/discard
decision only, never for numbers that get reported; the 1000/1000 template default is the *final*
run (Gelman et al. 2026, §11.4, §12.1 — see diagnostics.md → Exploration runs vs. the final run).
