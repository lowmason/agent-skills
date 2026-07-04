# pyprobml notebook index

Runnable companions for each family, from [`pyprobml`](https://github.com/probml/pyprobml) (MIT,
probml). Built from the **real repo listing** (C5) — notebooks live under
`notebooks/book1/<ch>/` and `notebooks/book2/<ch>/` with descriptive names, so paths do **not**
follow §-numbers; always list/grep rather than construct. To extend this index, see
`drill-down.md` (the `gh api … | grep` recipe).

All paths below are Gate-A-verified to exist on the `master` branch. Open via:
`https://github.com/probml/pyprobml/blob/master/<path>`.

## By family

### regression-glm
- `notebooks/book1/11/linreg_2d_bayes_demo.ipynb` — Bayesian linear regression
- `notebooks/book1/11/linregRobustDemoCombined.ipynb` — robust (Student/Laplace) regression
- `notebooks/book1/12/poisson_regression_insurance.ipynb` — Poisson GLM

### hierarchical
- `notebooks/book2/15/linreg_hierarchical_numpyro.ipynb` — hierarchical linear regression (NumPyro)
- `notebooks/book2/15/linreg_hierarchical_non_centered_numpyro.ipynb` — non-centered parameterization
- `notebooks/book2/03/hierarchical_binom_rats.ipynb` — hierarchical binomial (classic rats example)

### timeseries-statespace
- `notebooks/book2/29/sts.ipynb` — structural time series
- `notebooks/book2/29/supplementary/hmm_poisson_changepoint_jax.ipynb` — HMM Poisson changepoint (JAX)
- `notebooks/book1/15/lstm_jax.ipynb` — LSTM sequence model (JAX)
- *(Execution library: [dynamax](https://github.com/probml/dynamax) for JAX HMM/LG-SSM; [sts-jax](https://github.com/probml/sts-jax) for STS.)*

### gaussian-processes
- `notebooks/book1/17/gp_kernel_plot.ipynb` — GP kernels
- `notebooks/book2/18/gpr_demo_ard.ipynb` — GP regression with ARD
- `notebooks/book2/18/gpc_demo_2d.ipynb` — GP classification
- `notebooks/book2/29/gp_mauna_loa.ipynb` — GP time-series forecasting

### factor-models
- `notebooks/book1/20/pca.ipynb` — PCA
- `notebooks/book1/20/pcaEmStepByStep.ipynb` — PCA/FA via EM
- `notebooks/book1/20/mixPpcaDemo.ipynb` — mixture of PPCA
- `notebooks/book2/29/sts.ipynb` — dynamic factor / structural-TS (latent signal over time)

### classification
- `notebooks/book1/10/logreg_sklearn.ipynb` — logistic regression
- `notebooks/book1/10/logreg_laplace_demo.ipynb` — Bayesian logistic (Laplace)
- `notebooks/book1/18/bagging_trees.ipynb`, `.../spam_tree_ensemble_compare.ipynb` — trees / ensembles

### mixtures-clustering
- `notebooks/book1/03/gmm_2d.ipynb` — Gaussian mixture
- `notebooks/book2/10/gmm_vb_em.ipynb` — variational-Bayes GMM
- `notebooks/book1/21/kmeans_silhouette.ipynb` — K-means + silhouette
- `notebooks/book2/31/dp_mixgauss_cluster.ipynb` — Dirichlet-process mixture (auto-K)

### graphical-models
- `notebooks/book1/03/gauss_infer_2d.ipynb` — multivariate Gaussian / precision
- `notebooks/book2/09/ugm_inf_autodiff.ipynb` — undirected graphical model inference
- `notebooks/book1/23/gnn_graph_classification_jraph.ipynb` — graph neural network (jraph)
