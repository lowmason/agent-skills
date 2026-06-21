# Probabilistic graphical models (broadly)

**When this family fits:** Many variables whose dependency structure is unknown or itself the question, and you want to encode conditional-independence assumptions explicitly — or the data is network-structured (nodes + edges) rather than tabular.

## Methods & defaults

| Method | Use when | Default recommendation | PML §ref (Book 1 / Book 2) | pyprobml |
|--------|----------|------------------------|----------------------------|----------|
| Multivariate Gaussian / precision matrix | Continuous variables, dependence is roughly linear | Start here; zeros in the precision matrix Λ=Σ⁻¹ ARE conditional independencies, so it doubles as a structure model | PML1 §3.2 / PML2 §4.3.5 | notebooks/book1/03/gauss_infer_2d.ipynb |
| Directed graphical model (DAG / Bayes net) | A plausible generative/causal ordering exists; mix of variable types | Factor p(x)=∏ p(xᵢ\|pa(i)); good when domain knowledge gives edge directions | PML1 §3.6 / PML2 §4.2 | — |
| Undirected graphical model (MRF / GGM) | Symmetric dependencies, no natural direction (spatial, relational) | Pairwise MRF; for continuous data the Gaussian MRF = sparse precision matrix | — / PML2 §4.3 | notebooks/book2/09/ugm_inf_autodiff.ipynb |
| Structure learning | The graph itself is the deliverable (which edges exist) | Learn G from data; for GGMs use sparse-precision estimation (graphical lasso) | — / PML2 §30.3 | — |
| Graph neural network | Node/edge features on a known graph; prediction, not density | Use when you have graph-structured inputs and want a learned representation, not explicit CI semantics | PML1 §23.4 / PML2 §16.3.6 | notebooks/book1/23/gnn_graph_classification_jraph.ipynb |

## Selection & regularization (Step 6, family-specific)
The complexity knob is **edge count / graph density**. For Gaussian graphical models, an L1 penalty on the off-diagonal precision entries (graphical lasso) controls sparsity — tune the penalty by CV or by an information criterion (AIC/BIC) on held-out log-likelihood. For learned DAGs, score-based search penalizes the number of parameters (BIC-style). Prefer cross-validated / LOO predictive log-likelihood when the graph is used for prediction; prefer a stability/edge-recovery criterion when the graph itself is the answer. Specializes `references/model-selection-regularization.md`.

## Gotchas
- A sparse **covariance** matrix is not a sparse **precision** matrix — marginal independence ≠ conditional independence. Decide which you actually mean before regularizing.
- Edge direction in a DAG is not causal by default; "Bayesian network" implies nothing Bayesian and nothing causal without interventional assumptions.
- Structure learning over many variables is statistically hard: with D nodes you have O(D²) potential edges, so it needs strong regularization or it overfits spurious edges.
- GNNs give you predictions on a graph but discard the explicit conditional-independence semantics — don't reach for them when the goal is an interpretable dependency structure.

## Handoff
If the recommendation is to *fit* a specified graphical model with priors → **bayesian-workflow**. C4 payload the memo must carry: **likelihood family** (e.g. multivariate Gaussian for a GGM, or per-node conditionals for a DAG); **candidate priors** (e.g. graphical-lasso / horseshoe shrinkage on precision entries or edge-inclusion indicators); **structure** (directed vs undirected, fixed graph vs graph-to-be-learned, any plated/hierarchical sharing); **regularization & selection plan** (sparsity penalty + CV/IC criterion above). Route to **specialized** for heavy GNN training or large-scale causal-discovery pipelines.
