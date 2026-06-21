# Time series & state-space models

**When this family fits:** Data carries a time index and observations are serially dependent (autocorrelation, trend, seasonality, regime shifts) or you want to infer a latent state that evolves over time and forecast it forward.

## Methods & defaults

| Method | Use when | Default recommendation | PML §ref (Book 1 / Book 2) | pyprobml |
|--------|----------|------------------------|----------------------------|----------|
| Linear-Gaussian SSM + Kalman filter/smoother | Continuous latent state, linear dynamics, Gaussian noise; tracking, denoising, online state estimation | Start here for continuous state — exact closed-form filtering/smoothing, cheap and well-understood | — / PML2 §8.2 | — |
| Structural time series (STS) / dynamic linear model | Univariate forecasting with interpretable local-level/trend/seasonal/regression components | Default for decomposable forecasting — additive components each an LG-SSM; only variances need learning | — / PML2 §29.12 | notebooks/book2/29/sts.ipynb |
| Hidden Markov model (HMM) | Discrete latent regime/state; segmentation, changepoints, labeling | Default when the state is categorical; use forward-backward for inference, Baum-Welch/EM to learn | — / PML2 §29.2 | notebooks/book2/29/supplementary/hmm_poisson_changepoint_jax.ipynb |
| Extended/Unscented Kalman filter | Nonlinear transition/observation, still roughly unimodal-Gaussian belief | EKF if mild nonlinearity; UKF/sigma-point for stronger nonlinearity without Jacobians | — / PML2 §8.3, §8.4 | — |
| RNN / LSTM (seq models) | Long, complex sequences where flexibility beats interpretability; large data | Use when you need a learned nonlinear memory and don't need a calibrated latent state | PML1 §15.2 / PML2 §29.13.2 | notebooks/book1/15/lstm_jax.ipynb |

## Selection & regularization (Step 6, family-specific)
Complexity knobs: latent-state dimension `Nz` (LG-SSM/STS), which STS components to include (trend order, seasonal periods, regression covariates), number of HMM states `K`, and the process/observation noise variances (`Q`, `σ²`) that act as smoothing strength — small `Q` = stiffer, more-regularized latent path. For `K` (HMM) and component choice (STS), select by predictive accuracy: time-series cross-validation (rolling-origin / forward-chaining, never random k-fold — it leaks future into past) or marginal likelihood / information criteria. A Bayesian HMM (PML2 §29.4.4) regularizes `K` via priors on transitions rather than a hard count. Defer the post-fit LOO/ELPD comparison to `bayesian-workflow`; here specify the candidate set and the rolling-CV plan. See `references/model-selection-regularization.md`.

## Gotchas
- Random k-fold CV is invalid for serially correlated data — use rolling-origin/blocked splits so every validation point is forecast from its past only.
- Check stationarity first. Trend/seasonality must be modeled (STS component, differencing) not ignored; fitting a stationary model to drifting data gives biased, overconfident forecasts.
- The Kalman filter is exact *only* for linear-Gaussian models. Nonlinearity or heavy tails break it — reach for EKF/UKF, particle filters (PML2 §13.2), or an HMM with non-Gaussian emissions.
- Forecast uncertainty must widen with horizon. A model whose predictive intervals stay flat far out is mis-specified (often a missing trend/random-walk component).

## Handoff
Hand to `bayesian-workflow` for STS/Bayesian HMM fitting (or `statsmodels` for classical SARIMAX/state-space MLE). C4 payload the memo must carry: **likelihood family** (Gaussian for LG-SSM/STS; categorical/Poisson emissions for HMM; Student-t for heavy tails); **candidate priors** (half-Normal/half-Cauchy on `Q` and `σ_y` scales, Dirichlet on HMM transition rows, priors on regression `β`); **structure** (latent-state dimension, STS components — local level/trend/seasonal/regression — or `K` discrete states; temporal dependence is the core structure); **regularization/selection plan** (component/`K` candidate set + rolling-origin CV or marginal-likelihood criterion from Step 6).
