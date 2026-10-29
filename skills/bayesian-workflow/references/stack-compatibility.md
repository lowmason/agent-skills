# Stack compatibility (NumPyro + ArviZ)

Read this before you port code to ArviZ 0.23 or when an ArviZ call raises.

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
| Test-statistic PPC | `azp.plot_ppc_tstat(idata, t_stat="median")` | `az.plot_ppc(idata, ...)` (removed from the ArviZ 1.x umbrella) + manual |
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
