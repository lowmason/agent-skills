# Gaussian processes

**When this family fits:** Smooth nonlinear response where you need calibrated predictive uncertainty, especially with small-to-moderate n. A GP places a prior directly over functions, so it interpolates the data and reports honest error bars that widen away from observations.

## Methods & defaults

| Method | Use when | Default recommendation | PML §ref (Book 1 / Book 2) | pyprobml |
|--------|----------|------------------------|----------------------------|----------|
| GP regression (RBF/SE kernel) | Smooth 1D–few-D continuous target, Gaussian noise | Start here: SE kernel + observation-noise term; fit length-scale, signal & noise variance by maximizing marginal likelihood | PML1 §17.2 / PML2 §18.3 | notebooks/book1/17/gp_kernel_plot.ipynb |
| Matérn / ARD kernels | Response is rougher than SE assumes, or inputs differ in relevance | Matérn-3/2 or 5/2 for less-smooth functions; per-dimension ARD length-scales to down-weight uninformative inputs | PML1 §17.1.2 / PML2 §18.2.1 | notebooks/book2/18/gpr_demo_ard.ipynb |
| GP classification / non-Gaussian likelihood | Binary/multiclass labels, counts (Poisson/Cox) | Swap the Gaussian likelihood; posterior is non-conjugate so use Laplace/VI/MCMC approximation | — / PML2 §18.4 | notebooks/book2/18/gpc_demo_2d.ipynb |
| Compositional / structured kernels | Trend + seasonality + noise (e.g. time series) | Build additive/product kernels (SE × Periodic + linear); automatic search can propose structure | — / PML2 §18.6.4 | notebooks/book2/29/gp_mauna_loa.ipynb |
| Sparse / scalable GP | n more than ~a few thousand (exact GP is O(n³)) | Inducing-point (SVGP) approximation, O(nm²); use GPyTorch for GPU MVM-based inference | — / PML2 §18.5.3 | notebooks/book2/18/gpr_demo_ard.ipynb |

## Selection & regularization (Step 6, family-specific)
The kernel and its hyperparameters (length-scale, signal variance, noise variance) ARE the complexity knobs. Specializes `references/model-selection-regularization.md`: GPs select hyperparameters by maximizing the log marginal likelihood (empirical Bayes), which has a built-in data-fit vs. complexity tradeoff — no separate CV is needed (PML1 §17.2.6, PML2 §18.6.1). This is the key advantage over kernel regression, which must tune bandwidth by cross-validation (PML1 §17.2.3). For full uncertainty over kernel hyperparameters, put priors on them and marginalize via MCMC rather than point-estimating (PML2 §18.6.2). Choose between competing kernel structures by comparing marginal likelihood or LOO-ELPD.

## Gotchas
- Marginal-likelihood optimization is non-convex: multiple restarts help, and a too-large fitted noise variance signals an underfit kernel (over-smoothing) rather than genuine noise.
- Default kernels assume stationarity and a constant output scale; standardize inputs/outputs and consider non-stationary or compositional kernels when the function's wiggliness varies across the domain.
- Exact GPs scale O(n³) in time and O(n²) in memory — cross the few-thousand-point mark and you must move to inducing-point / variational approximations (PML2 §18.5.3–18.5.4).
- The SE kernel encodes very strong smoothness (infinitely differentiable sample paths); for real-world rough signals Matérn usually fits better and gives more honest uncertainty.

## Handoff
Route to **bayesian-workflow / GPyTorch** for fitting (GPyTorch for scalable GPU inference; PyMC/NumPyro for fully-Bayesian hyperparameter treatment). C4 memo payload if Bayesian:
- **Likelihood family:** Gaussian for regression; Bernoulli/Categorical or Poisson (Cox) for classification/counts (PML2 §18.4).
- **Candidate priors:** GP prior over f via chosen mean + kernel; weakly-informative priors on length-scale, signal variance, and noise variance (and a deep-kernel feature extractor if signals are high-dimensional, PML2 §18.6.6).
- **Structure:** kernel choice (SE / Matérn / ARD / additive-compositional) encoding smoothness, relevance, periodicity, trend.
- **Regularization/selection plan:** empirical Bayes (marginal likelihood) or full MCMC over hyperparameters; inducing-point/SVGP approximation when n is large.
