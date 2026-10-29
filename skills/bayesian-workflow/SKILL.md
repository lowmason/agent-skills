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
  BlackJAX, ArviZ, InferenceData, DataTree, credible intervals, HDI, posterior
  distributions, shrinkage, or posterior uncertainty. NumPyro only; Pyro/PyTorch fits go
  elsewhere.
license: MIT
compatibility: Requires uv to run bundled scripts (dependencies are declared inline); Python 3.12+.
effort: xhigh
metadata:
  author: "Alexandre Andorra (https://alexandorra.github.io/)"
  adapted_by: Lowell Mason
  version: "2.1"
# cc-guide: skills.frontmatter @2.1.306
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

## Scope and sibling skills

This skill fits by NUTS posterior inference; SVI is a warm start, or the final fit only under the checks in [references/svi.md](references/svi.md). Bayesian neural networks are in scope when posterior inference is the task.

- Upstream: explore-data profiles the data; recommend-probabilistic-model picks the model family; recommend-causal-design picks the design and the estimand for a causal question.
- Downstream: validate-data gates a result before it leaves; track-model-experiments keeps the ledger of fitted model variants and compares them.
- Not here: point-estimate neural training (deep-learning) and JAX speed, memory or compilation problems (optimize-jax).

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
- **Use `scripts/check_diagnostics.py` to interpret diagnostics, not hand-rolled prose.** Pipe the JSON outputs of `diagnose_model.py` and `calibration_check.py` (and optionally `psense_summary`) into `check_diagnostics.py` to get per-section qualitative ratings and an ordered, actionable Suggested Next Steps list. Use those outputs verbatim in the report's Assessment lines; expand only with problem-specific context.
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
oos_pred = az.from_dict(   # `np` imported in the model template below
    {'posterior_predictive': {'y_obs': np.asarray(oos['y_obs'])[None, ...]}},
    coords=coords_new,
    dims=dims_new,
)
```

- **Check model identifiability before interpreting components.** If two model components always appear together in the likelihood (e.g., a league intercept and a home advantage term when every observation is from home perspective), their individual posteriors reflect prior assumptions, not data signal — only their sum is identified. Use `az.plot_pair()` to check for strong posterior correlations between components. If correlation is near ±1, the components are not separately identifiable — either merge them or restructure the data.

## Common gotchas

These are battle-tested lessons that save hours of debugging:

- **`az.from_numpyro` does not compute `log_prior`, and `log_likelihood` is off by default.** Pass `log_likelihood=True` to get the LOO group. For prior sensitivity (`psense_summary`) you additionally need a `log_prior` group, which NumPyro never produces — compute it by tracing the model at each posterior draw and attach it (full `add_log_prior` recipe in [references/sensitivity.md](references/sensitivity.md)).
- **`plot_energy` needs `extra_fields`.** NumPyro only stores the energy statistic if you ask for it: `mcmc.run(..., extra_fields=("energy", "diverging", "num_steps", "accept_prob"))`. Divergences (`diverging`) are stored by default, but energy is not — without it `az.plot_energy(idata)` raises `AttributeError: ... has no attribute 'energy'`.
- **Divergences are marked automatically in ArviZ 1.x plots.** `az.plot_pair(idata, var_names=[...])` and `az.plot_parallel(idata)` highlight divergent draws by default (control with `visuals={"divergence": ...}`). The old `divergences=True` kwarg is ArviZ-0.23-only.
- **Convert to NumPy before `az.loo`.** `idata.map_over_datasets(lambda ds: ds.as_numpy())` (or reload from netCDF). PSIS-LOO (Pareto-smoothed importance sampling leave-one-out cross-validation) does in-place array updates that JAX arrays reject.
- **Python conditionals don't work inside a NumPyro model** (`if x > 0`). Use `jax.numpy.where` (`jnp.where`) — JAX traces the function, so data-dependent Python branches won't execute.
- **Heavy-tailed or near-flat priors on scale parameters** worsen funnels in hierarchical models. `HalfCauchy` is *proper* — the classic weakly-informative choice (Gelman 2006), not an improper flat prior — but its heavy tail lets the scale run very large (~6% of its mass sits above 10× the scale, versus effectively none for `HalfNormal`), which stretches the funnel, and its nonzero density at 0 does nothing to exclude the neck. Genuinely improper flat priors are worse still. Use `Gamma(2, ...)`, `HalfNormal`, or `Exponential` — but for the right reason: `HalfNormal`/`Exponential` help by cutting the tail (both actually have *more* mass near 0 than `HalfCauchy`, not less), while `Gamma(2, ...)` is the one that vanishes at 0 and so actively pushes the scale off the neck. If there's no group-level variation to detect, you don't need the hierarchy. (`HalfCauchy` remains correct for horseshoe `tau`/`lam` — see [references/priors.md](references/priors.md).)
- **Non-centering is one line in NumPyro.** Wrap the model with `numpyro.handlers.reparam(model, config={"a": LocScaleReparam(0)})` instead of hand-coding the offset. The reparameterized site is named `a_decentered` in the trace; the original `a` becomes a deterministic. See [references/hierarchical.md](references/hierarchical.md).
- **Forgetting to standardize predictors** makes shared priors inappropriate and slows sampling. Always standardize before fitting, then back-transform for interpretation.
- **Horseshoe priors create a double-funnel geometry** that standard NUTS can struggle with. Always use the **regularized (Finnish) horseshoe** (Piironen & Vehtari, 2017), which adds a slab component that smooths the geometry. Set `target_accept_prob=0.95` or higher. If you see divergences with a horseshoe model, this is almost certainly the cause.
- **`np.median` on posterior predictive probabilities is a silent bug.** It does not produce the Bayesian predictive distribution and can yield probabilities that don't sum to 1 across categories. Always use `np.mean` over the posterior samples dimension.
- **Discrete latents: marginalize or enumerate, don't plug in.** NUTS cannot sample discrete variables. Prefer a **true mixture likelihood** via `dist.MixtureSameFamily` (exact, O(K) per observation, NUTS-compatible), or enumerate with `numpyro.contrib.funsor.config_enumerate` (requires `pip install funsor`) plus `infer_discrete`. For Gibbs-style updates use `DiscreteHMCGibbs` or `MixedHMC`. Plugging a soft relaxation (soft-min/argmax, or `E[z]`) into a nonlinear function is mathematically wrong: it is not the marginal and can return out-of-bounds values. Any mixture also needs an identification constraint (e.g. `ordered` components) or chains will label-switch.
- **Overlapping data subsets in a likelihood double-count.** When a likelihood is assembled from per-subset terms, the subsets must partition the data *disjointly* — an observation that lands in two terms is counted twice, silently over-shrinking the posterior. Partition disjointly, or model the overlap explicitly.

## Stack compatibility (NumPyro + ArviZ)

The inline examples target the ArviZ ≥ 1.0 stack. Before you port code to ArviZ
0.23, or when an ArviZ call raises, read
[references/stack-compatibility.md](references/stack-compatibility.md).

## NumPyro model template

Start every model from the canonical template in
[references/model-template.md](references/model-template.md); read it before you
write model code.

## Samplers

Native NumPyro NUTS is the default and BlackJAX the co-equal alternative. Read
[references/samplers.md](references/samplers.md) before you set up MCMC: both
samplers, chain counts, and run sizes for exploration and the final run.

## Common model families

For each problem type's data model, typical priors and reference file, read
[references/model-families.md](references/model-families.md).

## Utility scripts

Three scripts check a saved run in order (diagnostics, calibration, then ratings
and next steps). Read [references/utility-scripts.md](references/utility-scripts.md)
for the commands before you write `report.md`.

## When things go wrong

Read [references/troubleshooting.md](references/troubleshooting.md) when you see
divergences, low ESS, R-hat above 1.01, a failing predictive check, or a missing
`log_likelihood` or `log_prior` group.
