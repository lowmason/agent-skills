# Model Criticism

Model criticism answers: "Is this model any good?" Convergence diagnostics (references/diagnostics.md) only tell you the sampler worked -- they say nothing about whether the model is appropriate for the data.

## Contents
- Posterior predictive checks (PPC)
- Leave-one-out cross-validation (LOO-CV)
- Calibration assessment
- Simulation-based calibration (SBC)
- Residual analysis
- Classification and ordinal model evaluation
- Temporal and out-of-sample evaluation
- Feature importance for shrinkage models
- Decision workflow

## Posterior predictive checks (PPC)

The most important model criticism tool. Simulate data from the fitted model and compare to observed data.

```python
import arviz as az
import arviz_plots as azp
from numpyro.infer import Predictive

post_pred = Predictive(model, posterior_samples=mcmc.get_samples())(jax.random.PRNGKey(1), x)
idata = az.from_numpyro(mcmc, posterior_predictive=post_pred, coords=coords, dims={"y_obs": ["obs"]})
idata = idata.map_over_datasets(lambda ds: ds.as_numpy())

# Visual check: do simulated datasets resemble the real data?
# az.plot_ppc was removed from the ArviZ 1.x umbrella — use arviz_plots:
azp.plot_ppc_dist(idata)
```

**What to look for**:
- Posterior predictive distribution should envelop the observed data
- Check shape, spread, and key features (skewness, multimodality, tails)
- Systematic departures indicate model misspecification

**Targeted / test-statistic PPCs** — Check specific data features the model should capture with
`arviz_plots.plot_ppc_tstat`, which compares a test statistic `T(y_rep)` to the observed `T(y)`:

```python
azp.plot_ppc_tstat(idata, t_stat="std")      # does the model capture the observed spread?
azp.plot_ppc_tstat(idata, t_stat="median")   # ...the center?
# t_stat also accepts "mean", "min", "max", a quantile in (0,1), or a callable.
```

Choose test statistics relevant to your problem and, ideally, **orthogonal to the model
parameters** — a statistic tied to a fitted parameter (e.g. the mean for a Gaussian location
model) has little power to detect misfit (Gabry et al. 2019). For count data, `azp.plot_ppc_rootogram(idata)`
is a sharp display of over/under-prediction by count.

## Leave-one-out cross-validation (LOO-CV)

Estimates out-of-sample predictive accuracy using Pareto-smoothed importance sampling (PSIS-LOO). This is the primary tool for model comparison but also useful for single-model criticism. It needs a `log_likelihood` group — pass `log_likelihood=True` to `az.from_numpyro(...)`.

```python
loo = az.loo(idata, pointwise=True)
print(loo)
```

**Key outputs** (ArviZ 1.x field names):
- `elpd` (a.k.a. `elpd_loo`): Expected log pointwise predictive density. Higher (less negative) is better.
- `p`: Effective number of parameters. If `p` >> actual parameter count, the model may be misspecified or the priors are too weak.
- `pareto_k`: Per-observation diagnostic. Flags influential or poorly-fit observations.
- `elpd_i`: Per-observation ELPD (a DataArray) — the basis for pointwise model comparison.

**Pareto k diagnostic** — Critical for trusting LOO results:

| Pareto k | Interpretation | Action |
|---|---|---|
| < 0.5 | Reliable | Trust LOO estimate |
| 0.5–0.7 | Marginally reliable | Investigate flagged observations |
| > 0.7 (or > `loo.good_k`) | Unreliable for that observation | Use K-fold CV or moment matching |

```python
# Find problematic observations
pareto_k = loo.pareto_k.values
bad_obs = np.where(pareto_k > 0.7)[0]
print(f"Observations with high Pareto k: {bad_obs}")

# Visualize (pass the LOO object, not the InferenceData)
az.plot_khat(loo)
```

High Pareto k observations are often outliers or observations the model fits poorly. Investigate them — they may reveal model misspecification.

## Calibration assessment

Calibration is mandatory for every model, not optional. A well-calibrated model's X% credible intervals should contain the true value about X% of the time. Run this even for binary and count data — ArviZ handles all data types correctly.

### How to run calibration

Always use ArviZ for calibration plots. Don't write custom calibration code — ArviZ's PIT plots
handle continuous, binary, and count data correctly out of the box. **Note the API:**
`plot_ppc_pit` and `plot_loo_pit` are *separate functions* (there is no `loo_pit=` argument):

```python
import arviz_plots as azp

# PPC-PIT: compares posterior predictive to observed
azp.plot_ppc_pit(idata)

# LOO-PIT: leave-one-out calibration (more robust, preferred when log_likelihood is available)
azp.plot_loo_pit(idata)

# Coverage view (same idea in coverage units) — add coverage=True to either:
azp.plot_ppc_pit(idata, coverage=True)
azp.plot_loo_pit(idata, coverage=True)
```

Refer to [this guide](https://arviz-devs.github.io/EABM/Chapters/Prior_posterior_predictive_checks.html#coverage) for detailed coverage interpretation — it's a treasure trove for the whole Bayesian workflow.

### Coverage calibration

**Interpretation**:
- If empirical coverage ≈ nominal → well-calibrated
- If the difference is positive, the model is under-confident: the predictions have a wider spread than the data – they are too uncertain.
- If the difference is negative, the model is over-confident: the predictions have a narrower spread than the data – they are too certain.
- This positive/negative rule holds **only in coverage units** (`coverage=True`, i.e. after the `2|PIT−0.5|` transform), where the deviation is single-signed. The raw PIT ΔECDF has no global sign — see the patterns below.

### PIT histograms / ECDFs (probability integral transform)

A sharper calibration check. If the model is calibrated, PIT values should be uniform; the ECDF
should fall within the simultaneous confidence bands. See [this section](https://arviz-devs.github.io/EABM/Chapters/Prior_posterior_predictive_checks.html#pit-ecdfs).

**Patterns** (the shape of the miscalibration is meaningful — but it only reads the same way if you
know which plot you are looking at; the mapping below is verified by simulation):
- **PIT histogram** — ∪-shaped (spikes at both ends) → underdispersed predictive (intervals too
  narrow / over-confident). ∩-shaped (mound at 0.5) → overdispersed (too wide / under-confident).
- **Raw PIT ΔECDF** (what `plot_loo_pit` / `plot_ppc_pit` draw by default) — neither miscalibration
  is a cup or a cap here; both trace a sign-flipping slope that integrates to ≈0. Read the
  half-plane sign instead: above zero in the lower half and below it in the upper half →
  too narrow; the mirror image → too broad.
- **Coverage ΔECDF** (`coverage=True`) — the deviation becomes single-signed, and only here does a
  single cup/cap word apply: below zero → over-confident, above zero → under-confident.
- Skewed → systematic bias in location
- Uniform / inside the simultaneous bands → well-calibrated

Avoid the word "frown" for these plots — it means ∩, which collides with the ∪ of the too-narrow
histogram case and is the source of a long-standing contradiction in this skill's references.

## Simulation-based calibration (SBC)

SBC validates that the entire inference pipeline is correct — priors, data model, sampler, and code. It simulates data from the prior, fits the model, and checks that posterior rank statistics are uniform. It is the gold standard for validating a new model implementation; run it once per model specification when you have doubts, since it is computationally expensive.

**Mechanics** (Talts et al. 2018; Betancourt, *Principled Bayesian Workflow* §1.2): for each of
many replications, draw a parameter `θ̃` from the prior, simulate data `ỹ` from the likelihood at
`θ̃`, fit the model to `ỹ` to get `L` (thinned, ~independent) posterior draws, and compute the
**rank** of `θ̃` among those draws. If computation is correct, the ranks are **uniform**.

A NumPyro sketch (roll your own; `simuk` from arviz-devs can also help):

```python
from numpyro.infer import Predictive, MCMC, NUTS
import jax, numpy as np

def sbc_rank(key, model, param, *model_args, L=100, idx=0):
    k_prior, k_fit = jax.random.split(key)
    # 1. draw one ground-truth parameter set + simulated data from the prior
    sim = Predictive(model, num_samples=1)(k_prior, *model_args)
    theta_true = np.asarray(sim[param][0])   # np.asarray needed to index a JAX array
    y_sim = sim["y_obs"][0]
    # 2. fit the model to the simulated data
    mcmc = MCMC(NUTS(model), num_warmup=500, num_samples=L, num_chains=1, progress_bar=False)
    mcmc.run(k_fit, *model_args, y=y_sim)
    draws = np.asarray(mcmc.get_samples()[param])
    # 3. rank of the truth within the posterior draws — pick one scalar component (idx)
    #    so the rank stays in [0, L]; a vector param would otherwise sum over all components
    return int((draws[..., idx] < theta_true[idx]).sum())

ranks = [sbc_rank(jax.random.PRNGKey(i), model, "beta", x) for i in range(200)]
# histogram `ranks`; compare to the uniform expectation (with a binomial variation band)
```

**Interpretation of the rank histogram**:
- **Uniform** → inference pipeline is correct
- **∪-shaped (spikes at both ends)** → posterior too narrow / over-confident (underdispersed)
- **Spike at one end** → posterior is biased (direction depends on the ranking convention)
- **∩-shaped / ramp** → over-dispersed or persistently biased (Talts et al. 2018)
- Systematic patterns → implementation bug, wrong prior, or sampler failure — fix before interpreting results

**When to run SBC**: developing a new model you'll reuse; complex hierarchical models where bugs are easy to introduce; custom likelihoods. Not necessary for routine analyses with standard model families.

## Residual analysis

For regression-style models, check residuals for patterns (work from the xarray-backed InferenceData):

```python
import matplotlib.pyplot as plt

# Posterior predictive mean
pp_mean = idata.posterior_predictive["y_obs"].mean(dim=["chain", "draw"]).to_numpy()
residuals = y_obs - pp_mean

# Residuals vs. fitted
plt.scatter(pp_mean, residuals, alpha=0.5)
plt.axhline(0, color="red", linestyle="--")
plt.xlabel("Fitted values")
plt.ylabel("Residuals")
plt.title("Residuals vs. Fitted")

# Residuals vs. predictors (check for missed nonlinearity)
for j, name in enumerate(predictor_names):
    plt.figure()
    plt.scatter(X[:, j], residuals, alpha=0.5)
    plt.axhline(0, color="red", linestyle="--")
    plt.xlabel(name)
    plt.ylabel("Residuals")
```

Look for: trends (missed nonlinearity), fans (heteroscedasticity), clusters (missing grouping variable).

## Classification and ordinal model evaluation

Standard PPC and calibration checks apply to classification models — **always run `plot_ppc_pit` / `plot_loo_pit` first** (see Calibration assessment above). The metrics below supplement PIT with classification-specific numeric summaries. Note: `sklearn.metrics.brier_score_loss` exists but is binary-only; there is no standard package for multiclass ECE or categorical RPS, so we provide lightweight helpers:

### Metrics for categorical/ordinal outcomes

```python
def expected_calibration_error(pred_probs, actuals, n_bins=10):
    """Confidence-based ECE: are predicted probabilities well-calibrated?"""
    # Standard ECE: bin on the model's confidence (max predicted probability),
    # compare to accuracy within each bin.
    confidences = np.max(pred_probs, axis=1)
    predictions = np.argmax(pred_probs, axis=1)
    accuracies = (predictions == actuals).astype(float)
    bin_edges = np.linspace(0, 1, n_bins + 1)
    # np.digitize assigns every point a bin; passing only the interior edges keeps
    # confidence == 1.0 in the last bin instead of dropping it (a strict `< 1.0` upper
    # edge would silently exclude perfectly-confident predictions).
    bin_idx = np.digitize(confidences, bin_edges[1:-1])
    ece = 0
    for i in range(n_bins):
        in_bin = bin_idx == i
        if in_bin.sum() > 0:
            avg_confidence = confidences[in_bin].mean()
            avg_accuracy = accuracies[in_bin].mean()
            ece += np.abs(avg_confidence - avg_accuracy) * in_bin.sum()
    return ece / len(actuals)

def ranked_probability_score(pred_probs, actuals, n_classes):
    """RPS: gold standard for ordinal outcomes. Penalizes being 'far off' more than Brier."""
    rps = 0
    for i, actual in enumerate(actuals):
        pred_cum = np.cumsum(pred_probs[i])
        actual_cum = np.zeros(n_classes)
        actual_cum[int(actual):] = 1
        rps += np.sum((pred_cum - actual_cum) ** 2)
    return rps / len(actuals)
```

Remember: build `pred_probs` as the **posterior mean** of the per-class probabilities (`np.mean`
over the posterior-sample dimension), never the median.

### Per-class calibration plots

For classification models, always check calibration **per class**, not just overall. A model can be well-calibrated on average but poorly calibrated for specific outcomes (e.g., good at predicting home wins but overconfident on draws).

```python
fig, axes = plt.subplots(1, n_classes, figsize=(5 * n_classes, 4))
for k, ax in enumerate(axes):
    pred_k = pred_probs[:, k]
    actual_k = (actuals == k).astype(float)
    # Bin predictions and compute observed frequency
    bin_edges = np.linspace(0, 1, 11)
    bin_centers, bin_means = [], []
    for i in range(10):
        mask = (pred_k >= bin_edges[i]) & (pred_k < bin_edges[i + 1])
        if mask.sum() > 5:
            bin_centers.append(pred_k[mask].mean())
            bin_means.append(actual_k[mask].mean())
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3)
    ax.scatter(bin_centers, bin_means)
    ax.set_title(f"Class {k}")
    ax.set_xlabel("Predicted P")
    ax.set_ylabel("Observed frequency")
```

### Key metrics summary

| Metric | Use when | Interpretation |
|--------|----------|---------------|
| Brier score | Any categorical model | Lower is better. Random: ~0.67 (3-class) |
| RPS | Ordinal outcomes | Lower is better. Penalizes "far off" predictions more |
| ECE | Need calibration number | Lower is better. 0 = perfectly calibrated |
| Per-class calibration | Always for classification | Points should track the diagonal |
| Accuracy | Stakeholder communication only | Ignores probability quality — never use alone |

## Temporal and out-of-sample evaluation

For panel data or time-series-adjacent data (e.g., multiple seasons), always evaluate **per time period**:

```python
for period in sorted(data_oos["season"].unique()):
    mask = data_oos["season"] == period
    period_metrics = evaluate(pred_probs[mask], actuals[mask])
    print(f"{period}: {period_metrics}")
```

This reveals **temporal degradation** — a model that works well on 2020 but poorly on 2023 may be overfitting to historical patterns. If you see degradation, consider whether the data-generating process has changed (concept drift) or whether the training window needs expanding.

## Feature importance for shrinkage models

When using sparsity priors (horseshoe, R2-D2), summarize feature relevance via **probability of practical significance**:

```python
beta_samples = idata.posterior["beta"].stack(samples=("chain", "draw")).values
threshold = 0.05  # on the standardized coefficient scale

importance = pd.DataFrame({
    "feature": features,
    "posterior_mean": beta_samples.mean(axis=-1),
    "posterior_sd": beta_samples.std(axis=-1),
    "P(|beta|>threshold)": (np.abs(beta_samples) > threshold).mean(axis=-1),
}).sort_values("P(|beta|>threshold)", ascending=False)
```

This is more informative than just looking at posterior means — it tells you the **probability that each feature has a practically meaningful effect**, which is the natural Bayesian answer to "which features matter?"

## Decision workflow

After running diagnostics:

```
1. Convergence OK?  (references/diagnostics.md)
   NO  → Fix sampler issues first. Do NOT proceed.
   YES ↓

2. Posterior predictive check pass?
   NO  → Model misspecification. Revise data model or add complexity.
   YES ↓

3. LOO-CV: any high Pareto k?
   YES → Investigate flagged observations. Consider K-fold CV.
   NO  ↓

4. Calibration OK?  (coverage + PIT)
   NO  → Model is mis-calibrated. Check priors, data model, missing predictors.
   YES ↓

5. Residual patterns?
   YES → Missing structure. Add predictors, nonlinearity, or hierarchical effects.
   NO  ↓

→ Model is ready for interpretation and reporting.
```
