# Decision map (router)

The runtime entry point. **Classify the task → match the observed data signal → open that family's
`families/<slug>.md`** for the depth (methods, defaults, §refs, notebooks, gotchas, handoff). This
table is deliberately thin; it routes, it doesn't explain. Nothing here needs the PDFs.

If a problem doesn't fit any row, it's the long tail → `drill-down.md`.

## 1. Task type → family

| The task is… | Family | Open |
|--------------|--------|------|
| Predict a continuous / count outcome from predictors | Regression, GLMs & counts | `families/regression-glm.md` |
| Predict a categorical outcome / probability | Classification & discriminative | `families/classification.md` |
| Outcome with grouped / nested / repeated structure | Hierarchical / multilevel | `families/hierarchical.md` |
| Outcome indexed by time; forecast / latent state | Time series & state-space | `families/timeseries-statespace.md` |
| Smooth nonlinear function, small-n, need uncertainty | Gaussian processes | `families/gaussian-processes.md` |
| Many correlated variables → compress / common signal | Dimensionality reduction & factor models | `families/factor-models.md` |
| Discover unlabeled groups / regimes / density | Mixtures & clustering | `families/mixtures-clustering.md` |
| Dependency structure among variables / network data | Graphical models | `families/graphical-models.md` |
| RL, deep generative, causal discovery, exotic kernels… | *(route-only)* | `drill-down.md` |

## 2. Data signal → the choice *within* a family

The signal (from `characterize.py` / `explore-data`) usually decides *which member* of a family:

| Observed signal | Points to | Family |
|-----------------|-----------|--------|
| Count target, `var ≈ mean` | Poisson GLM | regression-glm |
| Count target, `var ≫ mean` (overdispersion) | NegativeBinomial | regression-glm |
| Count target, high zero-fraction | Zero-inflated / hurdle | regression-glm |
| Continuous target, heavy tails / outliers | Robust (Student-t) regression | regression-glm |
| `p` large vs `n`; many candidate predictors | Sparse / regularized (lasso/horseshoe) | regression-glm + Step 6 |
| Group / panel columns; few obs per group | Partial pooling | hierarchical |
| Time index + autocorrelation / trend | LG-SSM / structural TS | timeseries-statespace |
| Time index + discrete regimes / changepoints | HMM | timeseries-statespace |
| Many correlated indicators → one latent driver | (Dynamic) factor model | factor-models |
| Categorical target, class imbalance | Logistic + class weighting / calibration | classification |
| Unlabeled, suspected sub-populations / regimes | GMM / mixture (or DP for unknown K) | mixtures-clustering |
| Many variables, dependency structure is the question | Gaussian graphical model / structure learning | graphical-models |

## 3. Always then do Step 6

Once the family + member is chosen, specify **regularization & model selection** for it
(`model-selection-regularization.md`) — the complexity knob + the selection criterion. That pair is
part of the handoff (`reporting.md` §5–6).

## 4. External information

In parallel, inventory official statistics / benchmarks / domain constraints
(`external-data-and-priors.md`) — they often set the prior, the pooling target, or a constraint.
