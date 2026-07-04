# Model Comparison

## Contents
- When to compare models
- Getting the log-likelihood for each model
- LOO-CV comparison
- Stacking weights
- Pointwise comparison
- WAIC (and why LOO)
- Reporting comparisons

## When to compare models

Compare models when you have genuinely different modeling assumptions — not for variable selection. Bayesian model comparison answers: "Which model predicts unseen data better?" LOO-CV works across different data models — they do not need to share the same observation distribution (see [CV-FAQ](https://users.aalto.fi/~ave/CV-FAQ.html#differentmodels)).

For variable selection, prefer projection-predictive methods or a BART-style model over hard selection by information criterion (Gelman et al. 2020, §8.3).

Common comparison scenarios:
- Linear vs. nonlinear trend
- Different hierarchical structures (varying intercepts vs. varying slopes)
- Different covariate sets guided by domain knowledge

Fit *several* models to **understand** each one, not just to crown a winner; if conclusions are stable across the models that pass your checks, deciding which is "best" matters less (the multiverse view, Gelman et al. 2020, §8).

## Getting the log-likelihood for each model

LOO needs a pointwise `log_likelihood` group in each model's InferenceData. With NumPyro, the
simplest path is to request it at conversion time:

```python
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

```python
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
- `warning`: True if high Pareto k values exist

**Interpreting differences**:
- If `elpd_diff` < 2×`dse` → Models are practically indistinguishable. Prefer the simpler one.
- If `elpd_diff` > 4×`dse` → Strong evidence for the better model.
- Between 2–4×`dse` → Moderate evidence. Consider domain knowledge.

## Stacking weights

`az.compare` uses **stacking** by default (`method="stacking"`). Stacking minimizes expected log predictive density loss and combines predictions:

```python
comparison = az.compare(models, method="stacking")
# The 'weight' column gives optimal combination weights
```

Stacking often outperforms selecting a single best model, and it is preferred over Bayesian model averaging (BMA), whose weights can depend strongly on aspects of the model that barely affect predictions (Gelman et al. 2020, §8.2). Heterogeneous stacking weights are also a hint that a *hierarchical* model could combine the components better. Report stacking weights alongside ELPD differences — they give a more nuanced picture.

## Pointwise comparison

To see *which observations* drive a model difference (the Gabry et al. 2019 Fig. 10a view), diff
the per-observation ELPD from two `pointwise=True` LOO objects and plot it against an informative
predictor or index:

```python
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
4. Note any high Pareto k warnings, what they mean, and what to do about it
5. The substantive interpretation — what does the better model imply about the phenomenon? Be careful to NOT make causal claims based on model comparison -- it only tells us about predictive accuracy.

Template:

```markdown
## Model comparison

| Model | ELPD (LOO) | SE | ΔELPD | ΔSE | Weight |
|-------|------------|-----|-------|------|--------|
| Model 1 | -234.5 | 12.3 | 0.0 | — | 0.72 |
| Model 2 | -241.2 | 11.8 | -6.7 | 3.1 | 0.28 |

Model 1 is slightly preferred by LOO (ΔELPD = 6.7, ~2.2× the SE of the difference),
suggesting moderate evidence. Consider domain knowledge to choose one model,
or use stacking weights to combine predictions.
No observations had Pareto k > 0.7.
```
