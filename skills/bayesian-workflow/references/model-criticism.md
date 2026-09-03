# Model Criticism

Model criticism answers: "Is this model any good?" Convergence diagnostics (references/diagnostics.md) only tell you the sampler worked -- they say nothing about whether the model is appropriate for the data.

## Contents
- Posterior predictive checks (PPC)
- Leave-one-out cross-validation (LOO-CV)
- Calibration assessment
- Simulation-based calibration checking (SBC)
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

A sharper calibration check. If the model is calibrated, PIT values should be uniform, so the
difference these plots draw — empirical CDF minus that uniform reference — should wander close to
the dashed zero line. No band is drawn around it: `plot_ppc_pit` and `plot_loo_pit` both default to
`method="pot_c"`, which instead annotates the panel with a uniformity-test p-value and the α it is
judged against, and recolours the worst-offending stretch of the step line as *suspicious points*
when that test rejects. Calibrated therefore reads as: nothing highlighted, p above α. The same
furniture appears with `coverage=True`. See [this section](https://arviz-devs.github.io/EABM/Chapters/Prior_posterior_predictive_checks.html#pit-ecdfs).

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
- Flat histogram, or a Δ-ECDF (raw or coverage) staying near zero with nothing highlighted and the
  annotated p above α → well-calibrated

Avoid the word "frown" for these plots — it means ∩, which collides with the ∪ of the too-narrow
histogram case and is the source of a long-standing contradiction in this skill's references.

## Simulation-based calibration checking (SBC)

SBC checks that the whole pipeline — prior, data model, NumPyro code, and sampler — is *coherent*: draw parameters from the prior, simulate data, fit, and the posterior draws should be exchangeable with the parameter that generated the data, so its rank among the posterior draws is uniform (Gelman et al. 2026, §14.1; Modrák et al. 2025). A single fit to simulated data with one "known truth" cannot do this job: a posterior is calibrated only *on average over the prior*, so one truth landing in a tail — or a bimodal posterior straddling it — proves nothing either way (§14). SBC is the standard for validating a new model implementation; it needs many fits, so run it once per model specification when you have doubts.

**Mechanics** (Talts et al. 2018; Modrák et al. 2025; Gelman et al. 2026, §14.1): for each of `S` replications, draw `θ̃` from the prior, simulate `ỹ`, fit to get `L` (thinned, ~independent) posterior draws, and record the rank of `θ̃` among them. More generally, rank a *test quantity* `T(θ̃, ỹ)` among `T(θ_l, ỹ)` — functions of parameters *and* data catch bugs a single parameter's rank misses. If everything is correct the ranks are uniform on `{0, …, L}`. When draws can tie the truth exactly (discrete quantities), break ties at random.

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

L = 100
ranks = np.array([sbc_rank(jax.random.PRNGKey(i), model, "beta", x, L=L) for i in range(200)])
```

**Read the ranks as a Δ-ECDF, not a histogram** (§14.2; Säilynoja, Bürkner & Vehtari 2022). Histogram shapes depend on the binning; the ECDF-difference plot with its simultaneous confidence band is the sharper instrument, and the same band yields a numerical pass/fail — the γ statistic, the tail probability of the most extreme ECDF deviation — for models with too many parameters to inspect by eye. In ArviZ, map ranks to PIT values and use `plot_ecdf_pit`, whose default group is `prior_sbc`:

```python
import arviz as az, arviz_plots as azp

pit = (ranks + 0.5) / (L + 1)                                   # ranks in [0, L] -> PIT in (0, 1)
sbc_dt = az.from_dict({"prior_sbc": {"beta": pit[None, :]}})     # (chain=1, draw=S)
azp.plot_ecdf_pit(sbc_dt, var_names=["beta"])                    # Δ-ECDF, zero line, uniformity p-value
```

**What that call actually draws** (arviz-plots 1.3.1): the Δ-ECDF step line and a dashed zero line — there is no shaded band on the figure. The test is reported as text instead: the p-value of the uniformity test run by the default `method="pot_c"`, annotated in the corner of the panel with the threshold it is judged against (`p=0.16(α=0.01)`). That α is `1 - envelope_prob`, and `envelope_prob` falls back to `rcParams["stats.envelope_prob"] = 0.99`, so α = 0.01 unless you pass your own. When the test rejects, the stretch of the step line contributing most to the departure from uniformity is redrawn in a second colour as *suspicious points*; when it passes, nothing is highlighted. A band-drawing variant does exist — `method="envelope"`, the simultaneous-band construction of Säilynoja, Bürkner & Vehtari 2022 — but it warns that it is slated for replacement by `pot_c`, whose advantage is staying valid when the PIT values are *not* independent. That advantage is beside the point in SBC: each replication contributes one PIT value from its own fit, so independence holds by construction, and the band is the instrument §14.2 itself reasons in. The objection here is to the current implementation, not to the method — on this stack `method="envelope"` raised a `TypeError` on the `from_dict` input above. Until that is fixed, read the p-value and the highlighting, not a picture of the band.

| Δ-ECDF shape (default threshold α = 0.01) | Rank histogram equivalent | Meaning |
|---|---|---|
| step line staying near zero, nothing highlighted, p > α | flat | pipeline coherent for this quantity |
| positive hump (ECDF runs ahead of uniform) | ranks pile at the low end | posterior *overestimates* — truth sits low among the draws |
| negative hump | ranks pile at the high end | posterior *underestimates* |
| + then − (crosses zero mid-way) | both ends piled | posterior *too narrow* — over-confident |
| − then + | middle piled | posterior *too wide* — under-confident |
| mostly flat, one edge running away and highlighted as suspicious points | a spike at one end | a subset of simulated datasets the model or sampler cannot handle — look at those reps |

Avoid "cup"/"cap"/"frown" for these shapes; the histogram and the Δ-ECDF invert each other's vocabulary (see the PIT section above).

**Fitting SBC into the workflow** (§14.3):

- **SBC over the whole prior can waste runs.** A prior that is weakly informative for *parameters* is often wild for *data* — a logistic regression with `Normal(0, 100)` coefficients pushes the success probability to one extreme or the other, so a simulated dataset comes back with every response identical, and checking calibration there tells you nothing about the region you care about. Either tighten the prior (joint priors where independent ones are the problem — priors.md → Sparsity priors) or **rejection-sample the prior predictive**: discard a simulated dataset by a criterion that depends only on *data* (a maximum count above some cap, an outcome sd below some floor) and redraw. A data-only criterion leaves the posterior unchanged, so SBC stays valid.
- **Posterior SBC** (Säilynoja, Schmitt et al. 2026): once you have real data, fit the model to it and run SBC with that *posterior* as the generating distribution — a check aimed at the region of parameter space that actually holds the posterior mass rather than at the whole prior. What it detects is a posterior computation that fails to update coherently on the new data — an implementation mistake, or a sampler that never explores the whole posterior. What it cannot detect is a discrepancy *between* the generative model and the posterior-density implementation, since the same implementation sits on both sides — one inference algorithm samples both the posterior and the augmented-data posterior, so any mismatch between them is applied to both sides and never surfaces. Catching that needs the separate generator in the software-testing bullet below.
- **Too slow for hundreds of replications?** A handful still catch gross bugs: any rank of exactly `0` or `L` is already a red flag; per-rep z-scores of the truth flag the same thing; and SBC on a fast sub-model first localises the problem. A few simulations beat none.
- **SBC as software testing.** Run it on a model whose posterior the algorithm ought to handle accurately, and bad calibration points at the software: the target log density is mis-specified, or the algorithm doing the inference is itself buggy. Testing a *model* implementation is a separate setup — the sketch above uses `Predictive(model)` to simulate, so it tests the *sampler* against the model as coded and a mis-coded likelihood stays invisible, the same code generating and fitting. When the likelihood is non-trivial, write an independent NumPy simulator from the *equations* and feed its data to the NumPyro model; rank uniformity then also certifies that the two codes define the same model.

**When to run SBC**: developing a new model you'll reuse; complex hierarchical models where bugs are easy to introduce; custom likelihoods; any hand-written marginalization (state-space.md). Not necessary for routine analyses with standard model families.

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
