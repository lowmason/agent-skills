# Common model families

Read this to pick the data model and priors for a problem type.

NumPyro uses scipy-style distribution arguments (`loc`/`scale`, `concentration`/`rate`). See
[priors.md](priors.md) for the full PyMC→NumPyro distribution map. For
time-series / state-space models, settle **marginalize the latent path vs. sample it** first — see
[state-space.md](state-space.md).

| Problem | Data model (`numpyro.distributions`) | Typical priors | Reference |
|---|---|---|---|
| Continuous outcome | `Normal` / `StudentT` | `Normal`, `Gamma`/`HalfNormal` avoiding 0 for positive-constrained parameters | [priors.md](priors.md) |
| Binary outcome | `Bernoulli` (or `Binomial` if aggregated); pass `logits=` for the logit link | `Normal(0, 1.5)` on coeffs | [priors.md](priors.md) |
| Count data | `Poisson` / `NegativeBinomial2(mean, concentration)` | `Gamma`/`HalfNormal` on rate, avoiding 0 | [priors.md](priors.md) |
| Count data with excess zeros | `ZeroInflatedPoisson(gate, rate)` / `ZeroInflatedNegativeBinomial2` | `Gamma` on rate; `Beta`/`Normal+logit` on the `gate` (= P(structural zero)) | [priors.md](priors.md) |
| Count data, zeros from a separate process | Hurdle: `HurdlePoisson(gate, rate)` / `HurdleNegativeBinomial2` (NumPyro ≥ 0.22); `gate` = P(zero), and every zero is structural | Separate gate and count components | [priors.md](priors.md) |
| Positive count data (zero cannot occur) | Zero-truncated count likelihood, built by hand (`TruncatedDistribution` rejects discrete bases) | `Gamma`/`HalfNormal` on rate, avoiding 0 | [priors.md](priors.md) |
| Ordinal outcome | `OrderedLogistic(predictor, cutpoints)` | `Normal` on coeffs; ordered-transformed `Normal` on cutpoints | [priors.md](priors.md) |
| Bounded outcome (a proportion strictly inside 0–1, or k successes out of n) | `BetaProportion(mean, concentration)` with `mean` through `expit`; `BetaBinomial(concentration1, concentration0, total_count)` for an overdispersed k-of-n count | `Normal` on coeffs (logit scale); `Gamma`/`Exponential` on `concentration`, avoiding 0 | [priors.md](priors.md) |
| One quantile of the outcome (e.g. the 90th percentile) | `AsymmetricLaplaceQuantile(loc, scale, quantile=τ)` with `loc` the τ-quantile predictor | `Normal` on coeffs; `HalfNormal` on `scale` | [priors.md](priors.md) |
| Censored data (survival, limits of detection) | `RightCensoredDistribution(base, censored=flag)` / `LeftCensoredDistribution` / `IntervalCensoredDistribution` | Same as uncensored, applied to the underlying distribution | [priors.md](priors.md) |
| Truncated data | `TruncatedNormal(loc, scale, low, high)` / `TruncatedDistribution(base, low, high)` | Same as underlying distribution | [priors.md](priors.md) |
| High-dimensional / sparse regression | `Normal` / `StudentT` with sparsity prior on coefficients | Regularized Horseshoe or R2-D2 on coeffs | [priors.md](priors.md) |
| Hierarchical / multilevel | Varies | See partial pooling + `LocScaleReparam` | [hierarchical.md](hierarchical.md) |
| Time series / state space | Latent path via `scan` (non-Gaussian/non-linear) or Kalman marginalization (linear-Gaussian) | Non-centered innovations; stationary init | [state-space.md](state-space.md) |
| Gaussian processes | Exact GP (`MultivariateNormal` over the inputs) for small n; HSGP (`numpyro.contrib.hsgp.approximation`) for large n in 1–3 input dims | `InverseGamma` on the length-scale, `HalfNormal` on the amplitude | [gaussian-processes.md](gaussian-processes.md) |
