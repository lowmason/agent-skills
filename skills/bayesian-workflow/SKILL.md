---
name: bayesian-workflow
description: >
  Use when building, fitting, diagnosing, comparing, or reporting on Bayesian/probabilistic
  models with NumPyro (JAX) and ArviZ — consult BEFORE writing any Bayesian model code, not
  after. Trigger on: prior elicitation or choosing priors, MCMC/NUTS inference, convergence
  diagnostics (divergences, R-hat, ESS), model comparison (LOO-CV, ELPD, stacking weights),
  hierarchical/multilevel models, count regressions, logistic regression with uncertainty,
  state-space or latent time-series models, prior sensitivity analysis, calibration
  (PIT/LOO-PIT), presenting Bayesian results to non-technical audiences, or mentions of NumPyro,
  Pyro, JAX, BlackJAX, ArviZ, InferenceData, DataTree, credible intervals, HDI, posterior
  distributions, shrinkage, or uncertainty quantification.
license: MIT
effort: xhigh
metadata:
  author: "Alexandre Andorra (https://alexandorra.github.io/)"
  adapted_by: Lowell Mason
  version: "2.1"
---

# Bayesian Workflow

## Workflow overview

Every Bayesian analysis follows this sequence. Do not skip steps -- especially model criticism.

1. **Formulate** — Define the generative story. What underlying process, that we're precisely trying to model, created the data? Start from a known template and plan to iterate — most models are throwaway steps toward a useful one (Gelman et al. 2026, §2.1).
2. **Specify priors** — See [references/priors.md](references/priors.md)
3. **Implement in NumPyro** — Write the model as a Python function with `numpyro.sample` / `numpyro.plate` / `numpyro.deterministic`. Prefer the latest NumPyro. Use `numpyro.plate` for batch dimensions and pass `coords`/`dims` to ArviZ at conversion time.
4. **Run prior predictive checks** — `numpyro.infer.Predictive(model, num_samples=500)(key, *args)`. Verify priors produce plausible data ranges before fitting. See [references/visualize.md](references/visualize.md)
5. **Inference** — `MCMC(NUTS(model), ...)` in JAX (already JIT-compiled; runs on CPU/GPU/TPU). Set `num_chains=4` and `numpyro.set_host_device_count(4)` so chains run in parallel. See **Samplers** below.
6. **Diagnose convergence** — Use `arviz_stats.diagnose(idata)` as the first check (requires arviz-stats >= 1.0.0). It covers R-hat, ESS, and divergences in one call. See [references/diagnostics.md](references/diagnostics.md)
7. **Criticize the model** — See [references/model-criticism.md](references/model-criticism.md)
8. **Check prior sensitivity** — Run `psense_summary(idata)` to verify conclusions are robust to prior choices. Visualize with `plot_psense_dist(idata)` from `arviz_plots`. Requires `log_likelihood` and `log_prior` groups in the InferenceData — NumPyro does not produce a `log_prior` group automatically, so compute and attach it (recipe in [references/sensitivity.md](references/sensitivity.md)).
9. **Compare models** (if applicable) — See [references/model-comparison.md](references/model-comparison.md). When iterating over many variants, track them with the track-model-experiments skill (ledger + comparator over the slug folders); model-comparison.md remains the statistics.
10. **Report results** — Generate `<slug>/report.md` using the canonical template in [references/reporting.md](references/reporting.md). Run `scripts/check_diagnostics.py` to turn raw diagnostics into qualitative ratings + an ordered next-steps list, and use that output to fill the Assessment lines and Suggested Next Steps section. When the user mentions a non-technical audience or is new to Bayesian stats, additionally adapt the prose to plain language and include a glossary — but keep the canonical report structure as the audit trail.

For the visual side of every step above — EDA, prior predictive, MCMC diagnostics, posterior predictive, calibration, model comparison — see [references/visualize.md](references/visualize.md), which translates the Gabry et al. (2019) *Visualization in Bayesian workflow* paper into ArviZ.

Before step 3 (fit), set the numerics policy: JAX defaults to **float32**, and `numpyro.enable_x64()` must run before the first JAX op or a float64 cast at the array boundary is silently discarded. This matters most for latent-process models — filtering recursions, covariance updates, log-determinants — where single precision degrades accuracy without producing a visible error. Division guards, nonfinite checks, and device/platform selection are covered in [references/jax-numerics.md](references/jax-numerics.md).

## Installation

NumPyro and JAX install cleanly from pip. A typical environment:

```bash
pip install numpyro jax arviz arviz-stats arviz-plots arviz-base preliz
# netCDF backend for idata.to_netcdf(...) — pick one:
pip install h5netcdf h5py        # or:  pip install netcdf4
# optional:
pip install graphviz             # model-graph rendering (also needs the system `dot` binary)
pip install blackjax             # the co-equal alternative JAX NUTS sampler (see Samplers)
pip install funsor               # only if you enumerate discrete latents
```

- For **GPU/TPU**, install the matching JAX wheel (e.g. `pip install "jax[cuda12]"`); the NumPyro code is identical.
- `arviz` 1.x is the umbrella that re-exports `arviz-base` (data), `arviz-stats` (statistics), and `arviz-plots` (plotting). See **Stack compatibility** below for the ArviZ 0.23 vs 1.x notes.

## Stack compatibility (NumPyro + ArviZ)

The inline examples here target the **modern ArviZ ≥ 1.0 stack**: the `arviz` 1.x umbrella plus
the split packages `arviz-base` (data), `arviz-stats` (statistics), and `arviz-plots` (plotting).
Install them in one line — `pip install "arviz>=1.0" arviz-base arviz-stats arviz-plots` — and they
coexist with a classic `arviz` 0.23 install (they even read 0.23-written netCDF), so you do not
have to uninstall an existing 0.23 environment to use this skill.

The **NumPyro modeling code is version-independent** — only the ArviZ analysis/plotting layer
differs. The right column below is a **porting reference**, not a promise that the inline code runs
unchanged on 0.23: the examples assume ArviZ 1.x, and the 1.x idioms here *will raise* on a
0.23-only environment unless you apply these translations.

| Task | Modern (ArviZ 1.x: `arviz_stats` / `arviz_plots`) | Classic ArviZ 0.23 equivalent (for porting) |
|---|---|---|
| NumPyro → InferenceData | `az.from_numpyro(...)` returns an xarray **`DataTree`** | same call, but returns an **`InferenceData`** |
| JAX→NumPy conversion | `idata.map_over_datasets(lambda ds: ds.as_numpy())` (DataTree method) | `idata.map(lambda ds: ds.as_numpy())` — and it is unnecessary: 0.23 `from_numpyro` already returns NumPy-backed arrays |
| Posterior-predictive plot | `arviz_plots.plot_ppc_dist(idata)` (imported as `azp`) | `az.plot_ppc(idata)` (removed from the ArviZ 1.x umbrella) |
| Calibration (PPC-PIT / LOO-PIT) | `azp.plot_ppc_pit(idata)` and **separately** `azp.plot_loo_pit(idata)` | `az.plot_loo_pit(idata, ecdf=True)` |
| Test-statistic PPC | `azp.plot_ppc_tstat(idata, t_stat="median")` | `az.plot_ppc(idata, ...)` + manual |
| Trace / rank plot | `az.plot_trace(idata, var_names=[...])`; rank `az.plot_rank(idata, var_names=[...])` — **pass `var_names`** (ArviZ 1.x errors when the auto-selected set exceeds its subplot cap, e.g. a vector `Deterministic` like `mu` over an `obs` dim). Returns a `PlotCollection` — `.savefig(...)` to save | `az.plot_trace(idata, kind="rank_vlines")` (the `kind=` arg is 0.23-only); returns a NumPy array of Matplotlib `Axes` — save via `plt.gcf().savefig(...)`, not `.savefig` on the return |
| Summary interval | `az.summary(idata, ci_prob=0.94, ci_kind="hdi")` | `az.summary(idata, hdi_prob=0.94)` |
| Prior sensitivity | `az.psense_summary(idata)` (on the 1.x umbrella) | not on the 0.23 umbrella — use `arviz_stats.psense_summary(idata)` |
| Pointwise LOO field | `loo.elpd_i` (and `loo.elpd` / `loo.p`) | `loo.loo_i` (and `loo.elpd_loo` / `loo.p_loo`) |
| Groups accessor | `idata.groups` is a tuple of paths | `idata.groups()` is a **method** — call it |
| Model comparison | `az.loo`, `az.compare` — unchanged. **WAIC was removed from ArviZ 1.x** — use LOO | `az.waic` exists on 0.23 only |
| Sampler output type | xarray `DataTree` | `InferenceData` |

`arviz_plots` (`azp`) and `arviz_stats` (`azs`) install alongside either umbrella, so leading with
`azp.*` / `azs.*` is the most portable plotting/stats choice. The genuinely version-stable calls are
`az.summary` (modulo the `ci_prob`/`hdi_prob` kwarg above), `az.compare`, and `idata.to_netcdf()`;
everything else in the table differs by version, so run the inline examples on the modern stack they
are written for.

## NumPyro model template

```python
import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS, Predictive
import arviz as az

numpyro.set_host_device_count(4)   # MUST precede the first JAX op (e.g. PRNGKey) or it silently no-ops

RANDOM_SEED = sum(map(ord, "churn-logistic-v1"))
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
idata.to_netcdf("model_output.nc")
```

## Samplers

NumPyro models are sampled by NUTS implemented in JAX, which is JIT-compiled and runs on
CPU/GPU/TPU. There are two first-class, co-equal choices. The canonical template uses native
NUTS; everything downstream (`az.from_numpyro` or `az.from_dict`, diagnostics, plots) is
identical once you have an InferenceData.

**1. Native NumPyro NUTS (default).** Idiomatic, the least code, and already fast.

```python
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

```python
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

**Why not nutpie?** The PyMC-ecosystem sampler nutpie compiles **PyMC and Stan** models, not
NumPyro — there is no NumPyro entry point. With NumPyro you do not need it: native NUTS is
already JAX-JIT-compiled, and BlackJAX is the genuine "swap the sampler" alternative.

**Chains.** Unlike PyMC, NumPyro requires you to set `num_chains` explicitly (default is 1).
Use **at least 4** and call `numpyro.set_host_device_count(num_chains)` so `chain_method="parallel"`
actually runs them on separate CPU devices. Running more chains is a cheap way to cut Monte
Carlo variance and to surface multimodality (Gelman et al. 2026, §11.4). `chain_method="vectorized"`
runs all chains in one `vmap` (fast, single device, no host-count needed); `"sequential"` is the
low-memory fallback. Size the run to the phase: exploration fits at `num_warmup=200, num_samples=200` accept R-hat ≤ 1.1; the 1000/1000 template default is the *final* run (Gelman et al. 2026, §11.4, §12.1 — see diagnostics.md → Exploration runs vs. the final run).

## Critical rules

- **Always run prior predictive checks** before sampling, with `Predictive(model, num_samples=500)(key, *args)` (call the model with `obs=None`, i.e. don't pass `y`). If prior predictions span implausible ranges, fix priors first. If you have doubts about some parameters, use the [PreliZ](https://preliz.readthedocs.io/en/latest/) package to elicit priors from the user (PreliZ is framework-agnostic — translate its distribution choices into `numpyro.distributions`).
- **Always check convergence** before interpreting results. R-hat > 1.01 or ESS < 100 * nbr_chains means the results are unreliable.
- **Always run posterior predictive checks**. A model that fits well numerically but cannot reproduce the data is useless.
- **Always run calibration checks** (PIT / coverage). Use `arviz_plots.plot_ppc_pit` (and `plot_loo_pit` for the LOO version) — they handle all data types (continuous, binary, count) correctly. See [references/model-criticism.md](references/model-criticism.md).
- **Document every prior choice** with a brief justification in a code comment.
- **Never report point estimates alone**. Always include credible intervals — a 94% HDI is a fine default, but no interval width is magic (see [references/reporting.md](references/reporting.md)).
- **Use `arviz_stats.diagnose(idata)` as the first diagnostic on every model** (arviz-stats >= 1.0.0). It checks R-hat, ESS, and divergences in one call. Follow up with `az.plot_trace(idata, var_names=[...])` for visual inspection, or `az.plot_rank(idata, var_names=[...])` for rank-based convergence views (both available on either stack — see **Stack compatibility** for the return-type/save differences). Pass `var_names` to focus on the parameters — ArviZ 1.x errors if the auto-selected set (e.g. a vector `Deterministic` over an `obs` dim) exceeds its subplot cap. For energy diagnostics you must request `extra_fields=("energy", ...)` in `mcmc.run(...)` (see gotchas).
- **Set `num_chains` to at least 4** and call `numpyro.set_host_device_count(num_chains)` **before the first JAX operation** — any `PRNGKey` or `jnp` call initializes the XLA backend, after which the call silently no-ops and chains run sequentially. NumPyro defaults to a single chain — one chain cannot diagnose convergence. This is the NumPyro counterpart to PyMC's "let the sampler pick"; here you pick, and 4 is the floor.
- **Use reproducible, descriptive seeds.** Never use magic numbers like `42`. Derive a seed from the analysis name: `RANDOM_SEED = sum(map(ord, "my-analysis-name"))`. Feed it through JAX: `rng_key = jax.random.PRNGKey(RANDOM_SEED)`, split with `jax.random.split`, and seed NumPy via `rng = np.random.default_rng(RANDOM_SEED)`. Every `Predictive(...)` call and `mcmc.run(...)` takes a `PRNGKey`.
- **Save InferenceData immediately after sampling** with `idata.to_netcdf("model_output.nc")`. Late crashes or kernel restarts can destroy valid MCMC results — save before any post-processing. (Needs an h5netcdf+h5py or netcdf4 backend installed.)
- **Convert JAX arrays to NumPy after `az.from_numpyro`** with `idata = idata.map_over_datasets(lambda ds: ds.as_numpy())`. NumPyro stores results as JAX arrays; a few ArviZ routines (notably `az.loo`'s PSIS) do in-place updates that JAX arrays reject. Reloading from netCDF also yields NumPy, so the scripts (which load `.nc`) are unaffected.
- **Use ArviZ for all plots and calibration.** Don't write custom plotting code when ArviZ already handles it — including for binary data, count data, and calibration. ArviZ developers have thought through edge cases so you don't have to. See [references/visualize.md](references/visualize.md).
- **Prefer xarray over numpy for InferenceData operations.** `InferenceData` and `DataTree` objects are backed by xarray — use xarray's labeled indexing (`.sel()`, `.mean(dim=...)`, etc.) instead of converting to numpy arrays. This preserves dimension labels, avoids shape bugs, and makes code more readable. Fall back to numpy only when xarray can't do what you need.
- **Always map the observed variable in `dims`.** When calling `az.from_numpyro(..., dims=...)`, include the likelihood site (e.g. `dims={"y_obs": ["obs"]}`). If you omit it, ArviZ invents an anonymous dimension and posterior-predictive plots (`plot_ppc_dist`, `plot_ppc_pit`) error on dimension inference.
- **Always generate `<slug>/report.md` after a full analysis run.** Store the full artifact set from [references/reporting.md](references/reporting.md) → Output structure (`inference_data.nc`, `trace.png`, `diagnostics.json`, `prior_predictive.png`, `pit_coverage.png`, and the rest — that list is canonical) in a slug-named results folder, and produce `report.md` from the canonical template in [references/reporting.md](references/reporting.md). Code without an interpreted, fixed-shape report is incomplete.
- **Use `scripts/check_diagnostics.py` to interpret diagnostics, not hand-rolled prose.** Pipe the JSON outputs of `diagnose_model.py` (and optionally `calibration_check.py` and `psense_summary`) into `check_diagnostics.py` to get per-section qualitative ratings and an ordered, actionable Suggested Next Steps list. Use those outputs verbatim in the report's Assessment lines; expand only with problem-specific context.
- **Always use the posterior mean (not median) for predictive probabilities.** The proper Bayesian predictive distribution averages over the posterior: `P(Y=k|x) = (1/S) Σ P(Y=k|x,θₛ)`. This is the mean, not the median. The median does not correspond to the posterior predictive distribution, can violate probability coherence (probabilities may not sum to 1), and biases calibration due to Jensen's inequality. In code: use `np.mean(probs, axis=sample_axis)`, never `np.median(...)`.
- **For out-of-sample predictions, re-run `Predictive` with new data arguments.** NumPyro has no `pm.set_data` — the data are just function arguments, so you swap them by calling the model with new inputs. Don't manually extract posterior samples and recompute predictions by hand — let `Predictive` propagate uncertainty:

```python
# After fitting the model, predict for new predictors:
predictive = Predictive(model, posterior_samples=mcmc.get_samples())
oos = predictive(jax.random.split(rng_key)[1], x_new)   # same model fn, new args; derived key, not a magic number

# `Predictive` returns bare arrays with no trace, so `az.from_numpyro(posterior_predictive=oos, ...)`
# raises `sample_dims must be provided if posterior is None`; passing `mcmc` instead fails whenever
# `x_new` differs in length from `x`, because the fitted `obs` dim collides with `coords_new`.
# Assemble the group explicitly, with a leading chain axis for the default sample_dims.
oos_pred = az.from_dict(   # `np` imported at the top of this workflow
    {'posterior_predictive': {'y_obs': np.asarray(oos['y_obs'])[None, ...]}},
    coords=coords_new,
    dims=dims_new,
)
```

- **Check model identifiability before interpreting components.** If two model components always appear together in the likelihood (e.g., a league intercept and a home advantage term when every observation is from home perspective), their individual posteriors reflect prior assumptions, not data signal — only their sum is identified. Use `az.plot_pair()` to check for strong posterior correlations between components. If correlation is near ±1, the components are not separately identifiable — either merge them or restructure the data.

## Common model families

NumPyro uses scipy-style distribution arguments (`loc`/`scale`, `concentration`/`rate`). See
[references/priors.md](references/priors.md) for the full PyMC→NumPyro distribution map. For
time-series / state-space models, settle **marginalize the latent path vs. sample it** first — see
[references/state-space.md](references/state-space.md).

| Problem | Data model (`numpyro.distributions`) | Typical priors | Reference |
|---|---|---|---|
| Continuous outcome | `Normal` / `StudentT` | `Normal`, `Gamma`/`HalfNormal` avoiding 0 for positive-constrained parameters | [references/priors.md](references/priors.md) |
| Binary outcome | `Bernoulli` (or `Binomial` if aggregated); pass `logits=` for the logit link | `Normal(0, 1.5)` on coeffs | [references/priors.md](references/priors.md) |
| Count data | `Poisson` / `NegativeBinomial2(mean, concentration)` | `Gamma`/`HalfNormal` on rate, avoiding 0 | [references/priors.md](references/priors.md) |
| Count data with excess zeros | `ZeroInflatedPoisson(gate, rate)` / `ZeroInflatedNegativeBinomial2` | `Gamma` on rate; `Beta`/`Normal+logit` on the `gate` (= P(structural zero)) | [references/priors.md](references/priors.md) |
| Positive count data (no zeros) | Hurdle: `Bernoulli` zero-gate + truncated count component (build manually) | Separate gate and count components | [references/priors.md](references/priors.md) |
| Ordinal outcome | `OrderedLogistic(predictor, cutpoints)` | `Normal` on coeffs; ordered-transformed `Normal` on cutpoints | [references/priors.md](references/priors.md) |
| Censored data (survival, limits of detection) | `numpyro.factor` with explicit log-CDF terms (no built-in `Censored`) | Same as uncensored, applied to the underlying distribution | [references/priors.md](references/priors.md) |
| Truncated data | `TruncatedNormal(loc, scale, low, high)` / `TruncatedDistribution(base, low, high)` | Same as underlying distribution | [references/priors.md](references/priors.md) |
| High-dimensional / sparse regression | `Normal` / `StudentT` with sparsity prior on coefficients | Regularized Horseshoe or R2-D2 on coeffs | [references/priors.md](references/priors.md) |
| Hierarchical / multilevel | Varies | See partial pooling + `LocScaleReparam` | [references/hierarchical.md](references/hierarchical.md) |
| Time series / state space | Latent path via `scan` (non-Gaussian/non-linear) or Kalman marginalization (linear-Gaussian) | Non-centered innovations; stationary init | [references/state-space.md](references/state-space.md) |
| Gaussian processes | GP prior over the latent function | Kernel hyperpriors (lengthscale, amplitude) | [references/priors.md](references/priors.md) |

## Utility scripts

Run these in order — each script's output feeds the next. They operate on the saved
`inference_data.nc` (backend-agnostic), so they are identical for native-NUTS and BlackJAX runs.

```bash
# 1. Run convergence + LOO + PPC checks (writes diagnostics.json)
python scripts/diagnose_model.py --idata <slug>/inference_data.nc --output <slug>/diagnostics.json

# 2. Run calibration check (writes calibration.json + pit_ecdf.png + pit_coverage.png)
python scripts/calibration_check.py --idata <slug>/inference_data.nc --output <slug>/calibration.json --save-plots --plot-dir <slug>/

# 3. Interpret the JSON outputs into qualitative ratings + suggested next steps
python scripts/check_diagnostics.py --diagnostics <slug>/diagnostics.json --calibration <slug>/calibration.json --output <slug>/check_report.json
```

Step 3 is what powers the `report.md` Assessment lines and Suggested Next Steps section — never hand-roll those interpretations from raw R-hat / ESS / pareto-k numbers when the harness can produce them consistently.

See [scripts/](scripts/) for all available utilities.

## Common gotchas

These are battle-tested lessons that save hours of debugging:

- **`az.from_numpyro` does not compute `log_prior`, and `log_likelihood` is off by default.** Pass `log_likelihood=True` to get the LOO group. For prior sensitivity (`psense_summary`) you additionally need a `log_prior` group, which NumPyro never produces — compute it by tracing the model at each posterior draw and attach it (full `add_log_prior` recipe in [references/sensitivity.md](references/sensitivity.md)).
- **`plot_energy` needs `extra_fields`.** NumPyro only stores the energy statistic if you ask for it: `mcmc.run(..., extra_fields=("energy", "diverging", "num_steps", "accept_prob"))`. Divergences (`diverging`) are stored by default, but energy is not — without it `az.plot_energy(idata)` raises `AttributeError: ... has no attribute 'energy'`.
- **Divergences are marked automatically in ArviZ 1.x plots.** `az.plot_pair(idata, var_names=[...])` and `az.plot_parallel(idata)` highlight divergent draws by default (control with `visuals={"divergence": ...}`). The old `divergences=True` kwarg is ArviZ-0.23-only.
- **Convert to NumPy before `az.loo`.** `idata.map_over_datasets(lambda ds: ds.as_numpy())` (or reload from netCDF). PSIS-LOO does in-place array updates that JAX arrays reject.
- **Python conditionals don't work inside a NumPyro model** (`if x > 0`). Use `jax.numpy.where` (`jnp.where`) — JAX traces the function, so data-dependent Python branches won't execute.
- **Heavy-tailed or near-flat priors on scale parameters** worsen funnels in hierarchical models. `HalfCauchy` is *proper* — the classic weakly-informative choice (Gelman 2006), not an improper flat prior — but its heavy tail lets the scale run very large (~6% of its mass sits above 10× the scale, versus effectively none for `HalfNormal`), which stretches the funnel, and its nonzero density at 0 does nothing to exclude the neck. Genuinely improper flat priors are worse still. Use `Gamma(2, ...)`, `HalfNormal`, or `Exponential` — but for the right reason: `HalfNormal`/`Exponential` help by cutting the tail (both actually have *more* mass near 0 than `HalfCauchy`, not less), while `Gamma(2, ...)` is the one that vanishes at 0 and so actively pushes the scale off the neck. If there's no group-level variation to detect, you don't need the hierarchy. (`HalfCauchy` remains correct for horseshoe `tau`/`lam` — see [references/priors.md](references/priors.md).)
- **Non-centering is one line in NumPyro.** Wrap the model with `numpyro.handlers.reparam(model, config={"a": LocScaleReparam(0)})` instead of hand-coding the offset. The reparameterized site is named `a_decentered` in the trace; the original `a` becomes a deterministic. See [references/hierarchical.md](references/hierarchical.md).
- **Forgetting to standardize predictors** makes shared priors inappropriate and slows sampling. Always standardize before fitting, then back-transform for interpretation.
- **Horseshoe priors create a double-funnel geometry** that standard NUTS can struggle with. Always use the **regularized (Finnish) horseshoe** (Piironen & Vehtari, 2017), which adds a slab component that smooths the geometry. Set `target_accept_prob=0.95` or higher. If you see divergences with a horseshoe model, this is almost certainly the cause.
- **`np.median` on posterior predictive probabilities is a silent bug.** It does not produce the Bayesian predictive distribution and can yield probabilities that don't sum to 1 across categories. Always use `np.mean` over the posterior samples dimension.
- **Discrete latents: marginalize or enumerate, don't plug in.** NUTS cannot sample discrete variables. Prefer a **true mixture likelihood** via `dist.MixtureSameFamily` (exact, O(K) per observation, NUTS-compatible), or enumerate with `numpyro.infer.config_enumerate` from `numpyro.contrib.funsor` (requires `pip install funsor`) plus `infer_discrete`. For Gibbs-style updates use `DiscreteHMCGibbs` or `MixedHMC`. Plugging a soft relaxation (soft-min/argmax, or `E[z]`) into a nonlinear function is mathematically wrong: it is not the marginal and can return out-of-bounds values. Any mixture also needs an identification constraint (e.g. `ordered` components) or chains will label-switch.
- **Overlapping data subsets in a likelihood double-count.** When a likelihood is assembled from per-subset terms, the subsets must partition the data *disjointly* — an observation that lands in two terms is counted twice, silently over-shrinking the posterior. Partition disjointly, or model the overlap explicitly.

## When things go wrong

| Symptom | Likely cause | Fix |
|---|---|---|
| Divergences | Posterior geometry issue | ≤ ~1% of transitions: raise `target_accept_prob` to 0.95–0.99. More than that: don't — reparameterize (non-centered via `LocScaleReparam`), center predictors, check `az.plot_pair`; see diagnostics.md → Failure signatures (Gelman et al. 2026, §12.3) |
| Low ESS | High autocorrelation | More warmup/draws, reparameterize, reduce correlations |
| R-hat > 1.01 | Chains haven't mixed | More draws, better init (`init_strategy=init_to_median`), check for multimodality |
| Prior pred. looks wrong | Bad priors | Tighten or shift priors, use domain knowledge / PreliZ |
| Post. pred. misses data | Model misspecification | Add complexity (varying slopes, different data model, interaction terms) |
| `log_likelihood` missing | `from_numpyro` defaults to `log_likelihood=False` | Pass `log_likelihood=True` (or call `numpyro.infer.log_likelihood`) before saving |
| `log_prior` missing (psense fails) | NumPyro never stores it | Attach it with the `add_log_prior` recipe in [references/sensitivity.md](references/sensitivity.md) |
| `az.loo` raises "JAX arrays are immutable" | JAX-backed InferenceData | `idata.map_over_datasets(lambda ds: ds.as_numpy())` or reload from netCDF |
| `plot_energy` AttributeError | energy not collected | `mcmc.run(..., extra_fields=("energy", ...))` |
| Slow / poor warmup | Bad starting point or geometry | Try `init_strategy=init_to_median`, `dense_mass=True`, or warm-start NUTS from an SVI `AutoNormal` fit / `blackjax.pathfinder` |
| Prior sensitivity flag | Prior-data conflict or strong prior | Check `psense_summary(idata)` — see [references/sensitivity.md](references/sensitivity.md). Justify or revise the flagged prior |

For the fuller catalog of failure signatures — improper posterior, unused parameter, aliasing, uncentered predictors, multimodality, overflow at init, varying curvature, funnel, unconstrained scale — and what each looks like in the diagnostics, see [references/diagnostics.md](references/diagnostics.md) → Failure signatures.
