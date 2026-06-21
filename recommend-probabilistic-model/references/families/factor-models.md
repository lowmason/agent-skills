# Dimensionality reduction & factor models

**When this family fits:** Many correlated indicators that you suspect are driven by a few shared latent signals — collapse them to a low-dimensional common factor. If those indicators are observed over time and you want to track/forecast the latent signal (multi-indicator nowcasting), use the dynamic (state-space) variant.

## Methods & defaults

| Method | Use when | Default recommendation | PML §ref (Book 1 / Book 2) | pyprobml |
|--------|----------|------------------------|----------------------------|----------|
| PCA | Quick linear compression, viz, or whitening; no generative model needed | First pass for orthogonal directions of max variance; standardize columns first | PML1 §20.1 / — | notebooks/book1/20/pca.ipynb |
| Factor analysis (FA) | Indicators with differing noise scales; want a probabilistic low-rank-plus-diagonal Gaussian | Default over PCA when you need a likelihood: `Cov[x]=WWᵀ+Ψ`, Ψ diagonal so each indicator keeps its own noise | PML1 §20.2 / PML2 §28.3.1 | notebooks/book1/20/pcaEmStepByStep.ipynb |
| PPCA | Want PCA's parsimony but a proper likelihood (CV, missing data, mixtures) | FA with isotropic noise Ψ=σ²I; closed-form MLE, enables principled model selection | PML1 §20.2.2 / PML2 §28.3.2 | notebooks/book1/20/mixPpcaDemo.ipynb |
| Dynamic factor / LG-SSM (LDS) | Correlated indicators over time → one latent state driving all series; nowcasting/forecasting | Linear-Gaussian state-space model: latent zₜ evolves (Fₜ), loads onto many yₜ via Hₜ; Kalman filter/smoother for the common signal | — / PML2 §29.6 (forecast §29.7.4) | notebooks/book2/29/sts.ipynb |

## Selection & regularization (Step 6, family-specific)
The knob is the latent dimension **L**. Plain PCA is *not* a proper generative model, so test-set reconstruction error keeps dropping as L grows — there is no U-shaped curve to minimize (PML1 §20.1.4). So: for plain PCA fall back to heuristics — scree plot or the profile-likelihood elbow (PML1 §20.1.4). For PPCA/FA, prefer the probabilistic route: pick L by cross-validated / LOO-ELPD held-out marginal log-likelihood, which penalizes over-complex models honestly. Specializes `references/model-selection-regularization.md`.

## Gotchas
- **PCA reconstruction error never U-turns on test data** — don't pick L by minimizing it (PML1 §20.1.4). Use PPCA/FA likelihood or a scree elbow.
- **FA loadings are rotation/permutation unidentifiable** (PML1 §20.2.4): W and WR (R orthogonal) give the same fit, so individual loadings are not interpretable without a constraint (e.g. lower-triangular W) or post-hoc rotation.
- **Standardize first.** PCA/FA are scale-sensitive; an indicator in large units will dominate the leading factor unless columns are centered and scaled.
- **Dynamic factor ≠ stacking PCA over time.** Static FA ignores temporal correlation; use the LG-SSM (PML2 §29.6) when the latent signal has its own dynamics, and don't smuggle covariates in via the input uₜ expecting regression weights (PML2 §29.7.4 footnote).

## Handoff
Default to **sklearn** for plain PCA/FA/PPCA point estimates and fast L-screening. Hand to **bayesian-workflow** when you need uncertainty on the latent factor, missing-data handling, or non-Gaussian indicators. C4 payload for the memo: **likelihood** = Gaussian, observation covariance Ψ diagonal (FA) or isotropic σ²I (PPCA); **structure** = latent dimension L (plus temporal transition Fₜ if dynamic factor / LG-SSM); **candidate priors** = weakly-informative on loading matrix W and on µ (ARD/shrinkage per-column to auto-prune unused factors), positive priors on noise scales; **regularization/selection plan** = CV or LOO-ELPD on held-out log-likelihood to choose L; scree/profile-likelihood as the non-probabilistic fallback.
