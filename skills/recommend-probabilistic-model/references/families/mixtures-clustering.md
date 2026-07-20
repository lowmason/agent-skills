# Mixture & latent-variable models / clustering

**When this family fits:** The data looks like a blend of sub-populations — multimodal marginals, regimes/breaks/segments, or unlabeled groups to discover. You want soft membership (a per-point probability over components), not just a hard partition.

## Methods & defaults

| Method | Use when | Default recommendation | PML §ref (Book 1 / Book 2) | pyprobml |
|--------|----------|------------------------|----------------------------|----------|
| K-means | Quick baseline, roughly spherical equal-size clusters, K guessable | Start here for a sanity check; it is the hard-assignment, equal-isotropic-covariance limit of GMM-EM. Use K-means++ init. | PML1 §21.3 / — | notebooks/book1/21/kmeans_silhouette.ipynb |
| Gaussian mixture (GMM), EM | Continuous features, elliptical/overlapping clusters, want soft responsibilities + density | Default mixture model. Fit by EM; let covariances be full unless data is scarce (then diagonal/tied). | PML1 §21.4.1 / PML2 §28.2.1 | notebooks/book1/03/gmm_2d.ipynb |
| Bernoulli mixture | Binary / count-of-binary features (e.g. clustering bit-vectors, MNIST pixels) | GMM analogue for binary data; same EM machinery. | PML1 §21.4.2 / PML2 §28.2.2 | notebooks/book1/03/mix_bernoulli_em_mnist.ipynb |
| Bayesian GMM (VI / MCMC) | Want posterior over params + K, uncertainty on assignments, principled regularization | Use when point-estimate EM overfits or you need credible intervals; ADVI or Gibbs. Hands off to bayesian-workflow. | PML1 §21.4.1 / PML2 §28.2.1 | notebooks/book2/10/gmm_vb_em.ipynb |
| Dirichlet-process mixture | K unknown and you want the model to infer it; nonparametric "infinite" mixture | Reach for this instead of scanning K when component count is the question, not a nuisance. | — / PML2 §31 | notebooks/book2/31/dp_mixgauss_cluster.ipynb |

## Selection & regularization (Step 6, family-specific)
The main complexity knob is **K** (number of components) and the **covariance structure** (full / diagonal / tied / spherical — fewer free params = stronger regularization when data is scarce). For non-Bayesian fits, choose K by scanning candidates and comparing **distortion (elbow), silhouette score, or BIC** (PML1 §21.3.7); BIC penalizes the extra component parameters and is the most principled of the three. For Bayesian fits, prefer **CV / LOO-ELPD** over IC, or let a **Dirichlet-process prior** infer K directly (partial pooling across components is the regularizer — sparse-weight priors shrink unused components toward zero). See references/model-selection-regularization.md for the general criteria.

## Gotchas
- **Label switching / unidentifiability**: components are exchangeable, so posterior means of per-cluster params are meaningless without a relabeling step — summarize cluster *assignments* or impose an ordering (PML2 §28.2.6).
- **EM finds local optima**: the GMM likelihood is multimodal; use K-means++ or multiple random restarts and keep the best ELBO/log-lik.
- **Singular covariances**: a component can collapse onto one point (variance → 0, likelihood → ∞). Add a covariance floor / conjugate prior, or shrink to diagonal.
- **K-means ≠ clusters**: it imposes spherical equal-size groups; elliptical or unequal clusters need a full-covariance GMM. Don't read K-means failure as "no structure."

## Handoff
- **sklearn** for fast EM baselines: `KMeans`, `GaussianMixture`, `BayesianGaussianMixture` (the last gives a DP-style automatic-K via a weight-concentration prior).
- **bayesian-workflow** when you need a posterior over K, uncertainty on assignments, or hierarchical/DP structure. C4 memo payload: **likelihood** = mixture of Gaussians (or Bernoulli/other exp-family per component); **priors** = Dirichlet on mixing weights (or DP/stick-breaking for unknown K), Normal-Inverse-Wishart on (μ, Σ); **structure** = latent indicator zₙ per observation, optional group-level hierarchy; **regularization/selection** = component-count prior + sparse weights, validate by LOO-ELPD; flag label-switching for any post-hoc summary.
