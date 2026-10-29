# When things go wrong

Read this when sampling or a check fails.

| Symptom | Likely cause | Fix |
|---|---|---|
| Divergences | Posterior geometry issue | ≤ ~1% of transitions: raise `target_accept_prob` to 0.95–0.99. More than that: don't — first `az.plot_pair` the flagged scale against one of its children, then apply the matching Failure-signatures fix (funnel → non-centered `LocScaleReparam`; ridge → identifiability; uncentered predictors → center them); see diagnostics.md → Failure signatures (Gelman et al. 2026, §12.3) |
| Low ESS | High autocorrelation | More warmup/draws, reparameterize, reduce correlations |
| R-hat > 1.01 | Chains haven't mixed | More draws, better init (`init_strategy=init_to_median`), check for multimodality |
| Prior pred. looks wrong | Bad priors | Tighten or shift priors, use domain knowledge / PreliZ |
| Post. pred. misses data | Model misspecification | Add complexity (varying slopes, different data model, interaction terms) |
| `log_likelihood` missing | `from_numpyro` defaults to `log_likelihood=False` | Pass `log_likelihood=True` (or call `numpyro.infer.log_likelihood`) before saving |
| `log_prior` missing (psense fails) | NumPyro never stores it | Attach it with the `add_log_prior` recipe in [sensitivity.md](sensitivity.md) |
| `az.loo` raises "JAX arrays are immutable" | JAX-backed InferenceData | `idata.map_over_datasets(lambda ds: ds.as_numpy())` or reload from netCDF |
| `plot_energy` AttributeError | energy not collected | `mcmc.run(..., extra_fields=("energy", ...))` |
| Slow / poor warmup | Bad starting point or geometry | Try `init_strategy=init_to_median`, `dense_mass=True`, or warm-start NUTS from an SVI `AutoNormal` fit / `blackjax.pathfinder` |
| Prior sensitivity flag | Prior-data conflict or strong prior | Check `psense_summary(idata)` — see [sensitivity.md](sensitivity.md). Justify or revise the flagged prior |

For the fuller catalog of failure signatures — improper posterior, unused parameter, aliasing, uncentered predictors, multimodality, overflow at init, varying curvature, funnel, unconstrained scale — and what each looks like in the diagnostics, see [diagnostics.md](diagnostics.md) → Failure signatures.
