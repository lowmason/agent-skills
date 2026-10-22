# Model Comparison

## Contents
- When to compare models
- Getting the log-likelihood for each model
- LOO-CV comparison
- Stacking weights
- Pointwise comparison
- Time-series and forecast comparison: LFO and blocked K-fold
- Predictive accuracy on one model: `loo_expectations`, `loo_metrics`, `loo_r2`
- Bayes factors (and the reference-value trap)
- WAIC (and why LOO)
- Reporting comparisons

## When to compare models

Compare models when you have genuinely different modeling assumptions — not for variable selection. Bayesian model comparison answers: "Which model predicts unseen data better?" LOO-CV works across different data models — they do not need to share the same observation distribution (see [CV-FAQ](https://users.aalto.fi/~ave/CV-FAQ.html#differentmodels)).

For variable selection, prefer projection-predictive methods or a BART-style model over hard selection by information criterion (Gelman et al. 2026, §9.6; worked example in Ch 28).

Common comparison scenarios:
- Linear vs. nonlinear trend
- Different hierarchical structures (varying intercepts vs. varying slopes)
- Different covariate sets guided by domain knowledge

Fit *several* models to **understand** each one, not just to crown a winner; if conclusions are stable across the models that pass your checks, deciding which is "best" matters less (the multiverse view, Gelman et al. 2026, §9.3 and §9.5).

## Getting the log-likelihood for each model

LOO needs a pointwise `log_likelihood` group in each model's InferenceData. With NumPyro, the
simplest path is to request it at conversion time:

```python fixture=comparison
idata_1 = az.from_numpyro(mcmc_1, log_likelihood=True, coords=coords, dims=dims).map_over_datasets(lambda ds: ds.as_numpy())
idata_2 = az.from_numpyro(mcmc_2, log_likelihood=True, coords=coords, dims=dims).map_over_datasets(lambda ds: ds.as_numpy())
```

If you already have an InferenceData without it (e.g. a BlackJAX run), compute it explicitly and
attach it:

```python
from numpyro.infer import log_likelihood
ll = log_likelihood(model, posterior_samples, x, y=y)         # {"y_obs": (samples, N)}
# reshape to (chain, draw, N) and add as the "log_likelihood" group via az.from_dict / xr.DataTree
```

## LOO-CV comparison

The primary comparison tool. Uses PSIS-LOO via ArviZ.

```python fixture=comparison
# Fit multiple models, store InferenceData for each (each with a log_likelihood group)
models = {"m1": idata_1, "m2": idata_2, "m3": idata_3}

# Compare
comparison = az.compare(models)
print(comparison)

# Visualize
import arviz_plots as azp
azp.plot_compare(comparison)
```

**Reading the comparison table**:
- `elpd_loo` (ArviZ 1.x names this column `elpd`): Higher is better (less negative = better predictive accuracy)
- `se`: Standard error of ELPD estimate
- `elpd_diff`: Difference from best model
- `dse`: Standard error of the difference
- `weight`: Stacking weight (see below)
- `diag_elpd` / `diag_diff`: Diagnostic strings — empty when clean, otherwise a short
  human-readable reason. `diag_elpd` is the ArviZ 1.x successor to the old boolean `warning`
  column (high Pareto k); `diag_diff` flags conditions that make the *difference* untrustworthy:
  `N < 100` with fewer than 100 observations (it then shows only that), else `|elpd_diff| < 4`
  (verified: with 60 observations it reports `N < 100`; empty at 400). Print them rather than
  testing for a specific string. **ArviZ 0.23 and earlier had `warning` instead — it no longer
  exists, so don't branch on it.**

**Interpreting differences** (the CV-FAQ rule, from Sivula et al. 2025; `diag_diff` applies it):

`elpd_diff` is reported **relative to the top-ranked model, so it is ≤ 0** (the best model's is
`0.0`). Compare magnitudes — `abs(elpd_diff)` — or the tests below invert:

- If `abs(elpd_diff)` < 4 → the difference is small: the models predict about equally well
  (`diag_diff` shows `|elpd_diff| < 4`). Prefer the simpler one. `dse` adds nothing here: when
  models predict alike the normal approximation can fail, and the difference is small either way.
- If `abs(elpd_diff)` > 4 → compare it with `dse`. `dse` is a reliable guide only when there are
  more than 100 observations and no model is badly misspecified (check with PPC and LOO-PIT);
  with fewer, `diag_diff` shows `N < 100`, and `dse` tends to be too small. Under those
  conditions a difference many times `dse` is clear; one near `dse` is not.
- Choosing the best of **many** models by ELPD flatters the winner (selection-induced bias,
  McLatchie & Vehtari 2024). With a few models the bias is usually negligible; with many, it
  can be large enough to matter.

## Stacking weights

`az.compare` uses **stacking** by default (`method="stacking"`). Stacking minimizes expected log predictive density loss and combines predictions:

```python fixture=comparison
comparison = az.compare(models, method="stacking")
# The 'weight' column gives optimal combination weights
```

Stacking often outperforms selecting a single best model, and it is preferred over Bayesian model averaging (BMA), whose weights can depend strongly on aspects of the model that barely affect predictions (Gelman et al. 2026, §9.6). Heterogeneous stacking weights are also a hint that a *hierarchical* model could combine the components better. Report stacking weights alongside ELPD differences — they give a more nuanced picture.

## Pointwise comparison

To see *which observations* drive a model difference (the Gabry et al. 2019 Fig. 10a view), diff
the per-observation ELPD from two `pointwise=True` LOO objects and plot it against an informative
predictor or index:

```python fixture=comparison
import matplotlib.pyplot as plt

loo_a = az.loo(idata_1, pointwise=True)
loo_b = az.loo(idata_2, pointwise=True)
elpd_diff = loo_a.elpd_i.values - loo_b.elpd_i.values     # per observation; >0 favors model 1

plt.axhline(0, color="0.6", lw=1)
plt.scatter(np.arange(elpd_diff.size), elpd_diff, s=12)
plt.xlabel("observation"); plt.ylabel("ELPD(m1) − ELPD(m2)")
```

A few observations dominating the difference is a signal to inspect those points (often outliers
or high-leverage cases). Pair with `az.plot_khat(loo_a)` to see which points are influential.

## Time-series and forecast comparison

PSIS-LOO leaves out one observation and predicts it from all the others, past and future
alike. That is the right question for interpolation and for structure: which likelihood, which
hierarchy, which covariates explain the data. It is the wrong question for a forecast
decision. A nowcast model predicts the next period from the past only, and LOO lets it lean on
neighbours from a future it will not have.

Rank forecasting variants by one of two routes:

- **Leave-future-out (LFO).** Fit on the data up to a forecast origin, score the next
  `forecast_horizon` observations, move the origin forward, repeat (Bürkner, Gabry & Vehtari
  2020; the loo package's LFO vignette, https://mc-stan.org/loo/articles/loo2-lfo.html).
  `azs.lfo_cv` with `method="approx"` carries the last fit forward by PSIS and refits only
  when Pareto k passes `k_threshold`.
- **Blocked K-fold with a joint log score.** Leave out one contiguous block of time at a
  time, refit on the rest, and score each block as a whole. `azs.loo_kfold` with a `folds`
  array does the refits. It scores each held-out step on its own, so the joint score of a
  block takes one more step (below). It suits a model whose dependence is short-range, so
  that a block's neighbours on both sides leak little (CV-FAQ,
  https://users.aalto.fi/~ave/CV-FAQ.html).

Both routes refit the model, so both need a `SamplingWrapper`: four methods that tell ArviZ
how to split the data, refit, convert a fit, and score held-out terms. This one wraps an AR(1)
model. Each of its log-likelihood terms scores `y[t]` given the observed `y[t-1]`. A refit
drops the held-out steps and the step after each block, because that step is scored given a
held-out value:

```python
# An AR(1) series and a wrapper that refits it on a subset of time steps.
# Each term scores y[t] given the observed y[t-1]. A refit drops the held-out
# steps and the step after each block, because that step is scored given a
# held-out value; lfo_cv and loo_kfold both call these four methods.
T = 80
rng_ts = np.random.default_rng(1)
series = np.zeros(T)
for t in range(1, T):
    series[t] = 0.7 * series[t - 1] + rng_ts.normal(0, 0.5)
y_lag, y_now = series[:-1], series[1:]
steps = np.arange(1, T)                      # the time coordinate of each term

def ar1(y_lag, y=None):
    mu = numpyro.sample("mu", dist.Normal(0, 2))
    phi = numpyro.sample("phi", dist.Uniform(-1, 1))
    s = numpyro.sample("s", dist.HalfNormal(1))
    with numpyro.plate("time", y_lag.shape[0]):
        numpyro.sample("y", dist.Normal(mu + phi * (y_lag - mu), s), obs=y)

def fit_ar1(y_lag, y, key=jax.random.PRNGKey(3)):
    run = MCMC(NUTS(ar1), num_warmup=200, num_samples=200, num_chains=1, progress_bar=False)
    run.run(key, y_lag, y=y)
    return run

idata_ts = az.from_numpyro(fit_ar1(y_lag, y_now), log_likelihood=True,
                           coords={"time": steps}, dims={"y": ["time"]})

class AR1Wrapper(azs.SamplingWrapper):
    def sel_observations(self, idx):
        idx = np.asarray(idx)
        keep = np.setdiff1d(np.arange(y_now.size), np.concatenate([idx, idx + 1]))
        return ({"y_lag": y_lag[keep], "y": y_now[keep]},
                {"y_lag": y_lag[idx], "y": y_now[idx], "time": steps[idx]})

    def sample(self, train):
        return fit_ar1(train["y_lag"], train["y"])

    def get_inference_data(self, run):
        return az.from_numpyro(run)

    def log_likelihood__i(self, test, idata_i):
        post = idata_i.posterior
        mu, phi, s = (post[name].values[:, :, None] for name in ("mu", "phi", "s"))
        mean = mu + phi * (test["y_lag"] - mu)
        ll = dist.Normal(mean, s).log_prob(test["y"])        # (chain, draw, n_test)
        return xr.DataArray(np.asarray(ll), dims=["chain", "draw", "time"],
                            coords={"time": test["time"]})

wrapper = AR1Wrapper(model=ar1, idata_orig=idata_ts)
```

Leave-future-out, one step ahead from origin 50 on. Each forecast origin is one unit:

```python fixture=time_series
import json
from pathlib import Path

lfo = azs.lfo_cv(idata_ts, wrapper, min_observations=50, forecast_horizon=1,
                 pointwise=True)
print(lfo.elpd, lfo.se, lfo.n_refits)        # n_refits: origins where PSIS gave out

units = {f"origin-{t}": float(v)
         for t, v in zip(lfo.elpd_i["time"].values, lfo.elpd_i.values)}
Path("ar1").mkdir(exist_ok=True)
Path("ar1/scores.json").write_text(json.dumps(
    {"criterion": "lfo-elpd-h1", "orientation": "higher", "units": units}))
```

With `forecast_horizon` above 1, `lfo_cv` scores the next steps jointly, each one given the
observed steps before it. Its docstring names the other convention, which simulates those
steps instead; results from the two do not compare.

Blocked K-fold, five contiguous blocks. Each block is one unit:

```python fixture=time_series
import json
from pathlib import Path

from scipy.special import logsumexp

folds = np.repeat(np.arange(1, 6), int(np.ceil(y_now.size / 5)))[: y_now.size]
kf = azs.loo_kfold(idata_ts, wrapper, folds=folds, save_fits=True)

# loo_kfold scores each step on its own. The joint log score of a block sums the
# block's terms under each draw, then averages the likelihood over draws.
units = {}
for k, saved in kf.fold_fits.items():
    _, test = wrapper.sel_observations(saved["test_indices"])
    per_draw = wrapper.log_likelihood__i(test, saved["fit"]).values.sum(axis=-1).ravel()
    units[f"block-{k}"] = float(logsumexp(per_draw) - np.log(per_draw.size))
Path("ar1").mkdir(exist_ok=True)
Path("ar1/scores.json").write_text(json.dumps(
    {"criterion": "kfold5-joint-elpd", "orientation": "higher", "units": units}))
```

**Ranking the variants.** The two blocks above are alternative routes. Both write
`ar1/scores.json`, so pick one route per ledger. `az.compare` runs PSIS-LOO on InferenceData.
It also ranks precomputed `lfo_cv(..., pointwise=True)` results that share one
`forecast_horizon` and `min_observations`. It cannot take the joint block scores of the
blocked-K-fold route, because they are plain numbers and not `ELPDData`. It cannot mix model
classes, and it cannot stamp an experiments ledger. For those cases, write each variant's
per-unit scores to its own `scores.json`, as both blocks above do, and rank them with
track-model-experiments' score mode. [track-model-experiments/references/predictive-evaluation.md](../../track-model-experiments/references/predictive-evaluation.md)
gives the file's contract, the paired-difference rule, and its limits. Every variant in one
ledger uses the same origins or blocks and the same criterion string.

## Predictive accuracy on one model: `loo_expectations`, `loo_metrics`, `loo_r2`

`az.compare` ranks models against each other. These three answer a different question —
*how well does this one model predict?* — on the LOO scale, so the answer is not inflated by
in-sample fit. All three live in `arviz_stats` and are re-exported by the `arviz` umbrella,
so `azs.` and `az.` both work (verified on arviz 1.3.0 / arviz-stats 1.3.1).

**All three require a `posterior_predictive` group.** `az.from_numpyro(mcmc,
log_likelihood=True)` does *not* create one, and the failure is a `ValueError: Can not
extract posterior_predictive` at call time:

```python
from numpyro.infer import Predictive
import arviz as az, arviz_stats as azs

pp = Predictive(model, mcmc.get_samples())(jax.random.PRNGKey(1), x)
idata = az.from_numpyro(mcmc, posterior_predictive=pp, log_likelihood=True)
```

```python
# Pointwise LOO predictive expectation - one value per observation.
# kind='mean' | 'var' | 'quantile' (with probs=[...])
azs.loo_expectations(idata, kind='mean')      # -> DataArray, shape (n_obs,)

# Scalar accuracy with a standard error. kind='rmse' | 'mae' | 'mse'
azs.loo_metrics(idata, kind='rmse')           # -> rmse(mean=0.75, se=0.049)

# LOO R^2 with an interval. NOTE: var_name is REQUIRED and positional-ish.
azs.loo_r2(idata, var_name='y')               # -> loo_R2(mean=0.87, eti_lb=0.83, eti_ub=0.9)
```

`loo_r2(idata)` without `var_name` raises `TypeError: missing 1 required positional
argument`. Pass the name of the observed variable.

Use these to report predictive accuracy in units a reader understands — an RMSE in payroll
jobs is more legible than an ELPD difference — while keeping `az.compare` for the ranking
itself.

## Bayes factors (and the reference-value trap)

`azs.bayes_factor` computes a Savage-Dickey density ratio and **requires a `prior` group**,
which means sampling the prior explicitly:

```python
prior = Predictive(model, num_samples=2000)(jax.random.PRNGKey(2), x)
idata = az.from_numpyro(mcmc, prior=prior, log_likelihood=True)

azs.bayes_factor(idata, var_names=['b'], ref_vals=0)
# -> Dataset with bf_type ('BF10', 'BF01')
```

**The trap — verified, and it fails silently.** Savage-Dickey needs the *posterior density
at the reference value*. When the posterior has no mass there, that density is estimated by
KDE extrapolation into a region containing zero draws, and the returned number is
meaningless without any warning.

Measured on a fit where the true slope is 2.1 and the posterior is `mean=2.05, sd=0.074`
with **0 of 1200 draws** within ±0.5 of zero, `bayes_factor(..., ref_vals=0)` returned
`BF10 = 0.50` — nominally *evidence for* the null. The intercept, equally decisively
non-zero, returned `BF10 = 0.51`. Near-identical near-1 values for two parameters that the
data resolves overwhelmingly: the estimator has degenerated, not measured anything.

**Check before trusting it:** count the posterior draws near `ref_val`. If there are
essentially none, the Bayes factor is not interpretable — and the fact that the posterior
excludes the reference value is itself the answer you were looking for.

Prefer LOO comparison for model choice. Bayes factors are also far more sensitive to prior
width than LOO is, which is the deeper reason this workflow does not lead with them.

## WAIC (and why LOO)

WAIC (Widely Applicable Information Criterion) is asymptotically equivalent to LOO but less robust in practice — and **`az.waic` was removed from the ArviZ 1.x umbrella** (it remains in classic ArviZ 0.23 if you are pinned to it). Use LOO:

- LOO provides the Pareto k diagnostic (you know when to trust it)
- WAIC can silently give unreliable results with no warning
- LOO is better calibrated for small samples

PSIS-LOO is rarely computationally infeasible, so there is almost no reason to reach for WAIC on the modern stack.

## Reporting comparisons

When reporting model comparisons, always include:

1. Table of ELPD values with standard errors
2. ELPD differences with their standard errors
3. Stacking weights
4. Note any diagnostics ArviZ surfaced — check the `diag_elpd` and `diag_diff` columns (non-empty
   means something fired; `diag_elpd` covers high Pareto k) — what they mean, and what to do about it
5. The substantive interpretation — what does the better model imply about the phenomenon? Be careful to NOT make causal claims based on model comparison -- it only tells us about predictive accuracy.

Template:

```markdown
## Model comparison

| Model | ELPD (LOO) | SE | ΔELPD | ΔSE | Weight |
|-------|------------|-----|-------|------|--------|
| Model 1 | -234.5 | 12.3 | 0.0 | — | 0.72 |
| Model 2 | -241.2 | 11.8 | -6.7 | 3.1 | 0.28 |

Model 1 is preferred by LOO. ΔELPD = 6.7 is above 4, and with 250 observations
(`diag_diff` is empty) and neither model badly misspecified (the PPC and LOO-PIT checks
show no bad misfit), the SE of the difference (3.1) is a fair guide: the difference is about 2.2× its SE, clear but not overwhelming.
Consider domain knowledge to choose one model, or use stacking weights to combine predictions.
No observations had Pareto k > `good_k` (min(1 − 1/log10 S, 0.7); 0.7 at 4,000 draws).
```
