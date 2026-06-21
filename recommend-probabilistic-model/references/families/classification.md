# Classification & discriminative models

**When this family fits:** The target is categorical (binary or multiclass) — a label, a turning point, a direction call (up/down) — and you want calibrated class probabilities, not just a hard label. Watch for class imbalance, which changes both the model and the metric.

## Methods & defaults

| Method | Use when | Default recommendation | PML §ref (Book 1 / Book 2) | pyprobml |
|--------|----------|------------------------|----------------------------|----------|
| Logistic / multinomial regression | Linearly separable-ish; want interpretable, calibrated probabilities | First model. L2-regularize; one-hot encode; standardize inputs | PML1 §10.2–10.3 / PML2 §15.3 | notebooks/book1/10/logreg_sklearn.ipynb |
| Bayesian logistic regression | Small data, costly decisions, need posterior uncertainty on coefficients | Use when point estimates hide risk; Laplace approx is the cheap entry point, MCMC for full posterior | PML1 §10.5 / PML2 §15.3.5 | notebooks/book1/10/logreg_laplace_demo.ipynb |
| Gaussian discriminant analysis / naive Bayes | Few examples per class, missing features, or need to add classes without retraining | Generative fallback; easy to fit by counting, handles missing inputs, but watch poor calibration from independence assumptions | PML1 §9.2–9.4 | notebooks/book1/02/iris_logreg.ipynb |
| CART (single tree) | Want a readable rule set; mixed feature types | Interpretable baseline only — high variance, prone to overfit | PML1 §18.1 | notebooks/book1/18/dtree_sensitivity.ipynb |
| Random forest / bagging | Many irrelevant features; tabular; want a strong off-the-shelf classifier | Default strong baseline; parallel, robust, OOB error replaces CV | PML1 §18.3–18.4 | notebooks/book1/18/bagging_trees.ipynb |
| Gradient boosting | Need top tabular accuracy and can fit sequentially | Best raw accuracy on tabular; tune trees + learning rate, watch overfit | PML1 §18.5 | notebooks/book1/18/spam_tree_ensemble_compare.ipynb |
| Deep ensembles | Neural-net classifier; need uncertainty + robustness | Train M nets from different seeds; cheap, well-calibrated uncertainty | — / PML2 §17.3.9 | notebooks/book1/18/bagging_trees.ipynb |

## Selection & regularization (Step 6, family-specific)
Complexity knobs: penalty strength (logreg L1/L2), tree depth / min-leaf, ensemble size + learning rate (boosting). Specializes `references/model-selection-regularization.md`. Use CV for the regularization path; for bagging/forests, **out-of-bag error** substitutes for CV (PML1 §18.3). For Bayesian logreg, prefer **LOO-ELPD** over IC. For hierarchical / multilevel classifiers (GLMMs, PML2 §15.5.1), partial pooling across groups **is** the regularizer — no separate penalty needed.

## Gotchas
- **Class imbalance.** Maximum-likelihood training optimizes a bound on 0-1 loss dominated by the majority class. Track balanced error rate / per-class recall, and consider logit adjustment rather than naive resampling (PML2 §15.3.3).
- **Calibration ≠ accuracy.** Naive Bayes and uncalibrated trees give extreme (near 0/1) probabilities; if you act on the probability, check a reliability curve (PML1 §9.4).
- **Single trees are unstable.** Dropping one example can flip the tree (PML1 §18.1). Don't ship a lone CART for prediction — ensemble it.
- **Ensembles aren't Bayesian model averaging.** Ensemble weights don't collapse to one model with more data; don't read them as posterior model probabilities (PML1 §18.3).

## Handoff
Tree ensembles and frequentist logreg → **sklearn** (`RandomForestClassifier`, `HistGradientBoostingClassifier`, `LogisticRegression`). When uncertainty on coefficients or scarce/costly-decision data points Bayesian → **bayesian-workflow**, with the C4 payload: **likelihood** = Bernoulli (binary) / categorical (multiclass) with logit link; **priors** = weakly-informative Normal on standardized coefficients (e.g. N(0, 1–2.5)), wider on the intercept; **structure** = flat, or multilevel/GLMM if grouped (PML2 §15.5.1); **regularization/selection** = prior scale as the shrinkage knob, model comparison via LOO-ELPD.
