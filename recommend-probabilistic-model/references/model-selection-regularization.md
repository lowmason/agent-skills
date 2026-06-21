# Model selection & regularization (cross-cutting — procedure Step 6)

This is **not a method family**. It is the complexity-control layer applied *within* whichever
family the router selected. Run it as Step 6, *after* the family is fixed, and specialize it to that
family's knobs (each `families/<x>.md` has a "Selection & regularization" subsection).

Boundary: this skill does the **pre-fit specification** — name the complexity knob and the selection
criterion. The **post-fit** comparison of fitted models (LOO/ELPD, stacking weights) is
`bayesian-workflow`'s job. Don't duplicate it here.

## The one idea

Every model has a complexity dial. Too simple → underfit (bias); too complex → overfit (variance).
Model selection picks the dial setting that generalizes; regularization *is* turning the dial down by
penalizing complexity. The Bayesian view unifies them: a prior is a regularizer, and the marginal
likelihood already penalizes complexity (Occam's razor) — PML1 §5.2.

## Choosing the criterion

| Criterion | Use when | PML §ref |
|-----------|----------|----------|
| **Cross-validation** (held-out predictive accuracy) | The model is for prediction; you can afford refits. Use **rolling-origin / blocked** CV for time series — never random k-fold (it leaks future into past). | PML1 §11.3.3 (CV to choose the regularizer) |
| **Information criteria** (AIC/BIC) | Fast comparison across a candidate set; penalizes parameter count | PML1 §5.2 |
| **Marginal likelihood / empirical Bayes** | Bayesian model comparison; hyperparameters (e.g. GP kernel) tuned by evidence | PML1 §5.2 / PML2 §18.3.5 |
| **LOO-ELPD** (pointwise out-of-sample predictive density) | Default for Bayesian models; gives per-point diagnostics | (compute in `bayesian-workflow`) |

## Regularization = encoding the penalty

| Form | Effect | PML §ref |
|------|--------|----------|
| **Ridge (L2)** | Shrinks coefficients toward 0; keeps all predictors | PML1 §11.3 |
| **Lasso (L1)** | Shrinks *and* selects (sparse) — sets coefficients exactly to 0 | PML1 §11.4 |
| **Elastic net** | L1+L2 — sparsity with grouped-correlated stability | PML1 §11.4.8 |
| **Horseshoe / sparsity priors** | Bayesian shrinkage; strong sparsity with a heavy tail (use the *regularized* horseshoe) | (see `bayesian-workflow`) |
| **Partial pooling** | Hierarchical shrinkage toward a group mean — the regularizer *is* the model | (see `families/hierarchical.md`) |

## Per-family knobs (specialize Step 6 here)

| Family | Complexity knob | Regularizer / selection |
|--------|-----------------|-------------------------|
| `regression-glm` | which predictors; penalty λ | ridge/lasso/elastic-net/horseshoe; CV or LOO-ELPD |
| `hierarchical` | which effects vary; pooling strength | partial pooling is intrinsic; LOO-ELPD + prior-sensitivity |
| `timeseries-statespace` | latent dim, STS components, HMM `K`; `Q`/`σ²` | noise variances as smoothing; **rolling-origin** CV / marginal lik |
| `gaussian-processes` | kernel form; ARD lengthscales | marginal-likelihood (empirical Bayes); compositional-kernel search |
| `factor-models` | number of factors `L` | ARD on loadings; CV/LOO-ELPD held-out loglik (scree elbow if PCA) — PML1 §20.1.4 |
| `classification` | features; penalty; tree depth | L1/L2; tree pruning / boosting shrinkage; CV |
| `mixtures-clustering` | number of components `K` | BIC / LOO; Dirichlet-process mixture auto-selects `K` — PML1 §21.3.7 |
| `graphical-models` | edge count / density | graphical lasso (L1 on precision); CV/IC, or edge-stability if the graph is the deliverable |

## Output (feeds reporting.md §5 and the C4 handoff)

State two things explicitly: the **knob** (what controls complexity for this family) and the
**criterion** (how you'll set it). That pair is what `bayesian-workflow` (or the user) executes.
