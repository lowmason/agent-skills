# Regression, GLMs & count models

**When this family fits:** The target is continuous or an integer count and you want its (link-transformed) mean as a linear function of inputs. Route here on counts (`var ≫ mean` → NegBinom over Poisson; high zero-fraction → zero-inflated), or continuous targets with heavy-tailed noise / outliers → StudentT or Laplace likelihood. (Binary/categorical targets are the logistic GLM case — see `classification.md`.)

## Methods & defaults

| Method | Use when | Default recommendation | PML §ref (Book 1 / Book 2) | pyprobml |
|--------|----------|------------------------|----------------------------|----------|
| OLS / Gaussian linear regression | Continuous target, roughly symmetric homoskedastic noise | First model. Standardize inputs; it's the GLM with identity link, Gaussian likelihood | PML1 §11.2 / PML2 §15.2 | notebooks/book1/11/linreg_2d_bayes_demo.ipynb |
| Robust regression (StudentT / Laplace likelihood) | Heavy tails or outliers wreck the OLS fit | Swap Gaussian for a heavy-tailed likelihood so outliers get high likelihood without bending the line; StudentT(ν) with small ν, or Laplace (ℓ1) | PML1 §11.6 / PML2 §15.2 | notebooks/book1/11/linregRobustDemoCombined.ipynb |
| Bayesian linear regression | Small data, need posterior uncertainty on coefficients & predictions | Gaussian prior on weights → full posterior p(w\|D); ridge is its MAP special case | PML1 §11.7 / PML2 §15.2 | notebooks/book1/11/linreg_2d_bayes_demo.ipynb |
| Poisson regression | Integer counts, mean ≈ variance | GLM with log link, Poisson likelihood: `Poi(y\|exp(wᵀx))`. The count baseline | PML1 §12.2.3 / PML2 §15.1.1 | notebooks/book1/12/poisson_regression_insurance.ipynb |
| Negative-binomial regression | Counts with **overdispersion** (`var ≫ mean`) | Default over Poisson when counts are dispersed; NegBinom decouples mean & variance (Poisson is its r→∞ limit) | — / PML2 §2.2.1.4 | notebooks/book1/12/poisson_regression_insurance.ipynb |
| Zero-inflated (ZIP) / hurdle | Excess zeros beyond what Poisson/NB predicts | Mixture of a spike-at-0 and a count model; hurdle is the two-part alternative (separate "any?" and "how many?" stages) | — / PML2 §15.1.1 | notebooks/book1/12/poisson_regression_insurance.ipynb |

## Selection & regularization (Step 6, family-specific)
Complexity knobs: which features enter and how hard their coefficients shrink. Specializes `references/model-selection-regularization.md`. Frequentist: ridge (L2) / lasso (L1) strength tuned by **CV**. Bayesian: the prior *is* the shrinkage — Gaussian (ridge), Laplace/Bayesian lasso, horseshoe, or ARD for sparsity (PML2 §15.2). Pick the count likelihood (Poisson vs. NB vs. ZIP) from dispersion/zero diagnostics, then compare candidates post-fit by **LOO-ELPD**, not an IC. For grouped/panel data, partial pooling (GLMMs, PML2 §15.5.1) replaces an explicit penalty.

## Gotchas
- **Don't default to Poisson.** Poisson forces `var = mean`; real counts are usually overdispersed. Check the dispersion ratio first — if `var ≫ mean`, Poisson SEs are too small and you want NegBinom (PML2 §2.2.1.4).
- **Excess zeros ≠ overdispersion.** A pile of zeros (sold out vs. unpopular) needs a zero-inflated/hurdle structure, not just a fatter-tailed count likelihood (PML2 §15.1.1).
- **Log link is multiplicative.** In Poisson/NB regression coefficients act on `exp(wᵀx)`; a unit change in x scales the rate, it doesn't add to it. Interpret and set priors on the log scale.
- **Outliers vs. heteroskedasticity.** Heavy-tailed likelihoods (StudentT/Laplace) absorb a few outliers (PML1 §11.6); they do not fix variance that grows with the mean — model that directly.

## Handoff
Frequentist OLS / ridge / lasso / GLM → **sklearn** (`LinearRegression`, `Ridge`, `Lasso`, `PoissonRegressor`). Uncertainty, dispersed/zero-heavy counts, or scarce data → **bayesian-workflow**, with the C4 payload: **likelihood** = Gaussian (or StudentT/Laplace if heavy-tailed) for continuous; Poisson / NegBinom / zero-inflated for counts, with the appropriate link (identity or log); **priors** = weakly-informative Normal on standardized coefficients (sparsity → Laplace/horseshoe), prior on the dispersion/overdispersion parameter for counts; **structure** = flat, or multilevel/GLMM if grouped (PML2 §15.5.1); **regularization/selection** = prior scale as the shrinkage knob, likelihood chosen by dispersion/zero diagnostics, candidates compared via LOO-ELPD.
