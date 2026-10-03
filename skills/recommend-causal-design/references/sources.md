# Sources and workflow provenance

Verified on 2026-10-03. This is a bibliography and adaptation record, not bundled
source material. Method summaries and the memo contract are newly written.
No book/paper prose, figures, PDFs, or upstream estimator code is redistributed.

## Workflow adaptation

| Source | Pinned source | Adapted portion |
|---|---|---|
| Robson Tigre, `causal-planner`, MIT | [SKILL.md at 5317ebc](https://github.com/RobsonTigre/everyday-causal-skills/blob/5317ebc8affd36a7132739d480ccfae22f4bb3ad/skills/causal-planner/SKILL.md) | Interview about assignment, compare designs, record a conditional recommendation and implementation handoff |
| Alexandre Andorra, `causal-inference`, MIT, Learning Bayesian Statistics | [SKILL.md at 18ab0de](https://github.com/Learning-Bayesian-Statistics/baygent-skills/blob/18ab0de9b63b5bb03caa96146235e8f1534d45d4/causal-inference/SKILL.md) | Thinking phase: define estimand, draw DAG, establish identification, choose design |

Both public HEAD/main commits were resolved with `git ls-remote`; each LICENSE
was checked at that exact commit. Full MIT notices are retained inside this
skill in [LICENSE](../LICENSE), also recorded in the repository's
`LICENSE-causal-design-sources` and attribution in `NOTICE`.

Changes from those sources: recommendation-only endpoint; explicit
requested/supported estimand and status fields; self-contained references;
source-backed candidate checks; selection/time-varying-confounding gates;
structured nine-section memo; software-independent identification with a
NumPyro/JAX Bayesian handoff. Upstream decision-tree heuristics, fitting
instructions, estimator code, numeric causal-language grades and repeated
mandatory approval checkpoints were not imported.

## Primary methodology

| Citation | Verified primary source | Used for |
|---|---|---|
| Hernán, Miguel A., and James M. Robins (2020). *Causal Inference: What If*. | [Author's book page](https://miguelhernan.org/whatifbook) | Estimands, consistency, exchangeability, positivity, selection, intervention regimes and longitudinal treatment/confounder feedback. Part III addresses complex longitudinal data. |
| Perković, Emilija; Johannes Textor; Markus Kalisch; Marloes H. Maathuis (2018). *Complete Graphical Characterization and Construction of Adjustment Sets in Markov Equivalence Classes of Ancestral Graphs*. | [JMLR 18, paper 16-319](https://jmlr.org/papers/v18/16-319.html) | Graphical adjustment criteria; restrictions on adjustment sets. |
| Imbens, Guido W., and Joshua D. Angrist (1994). *Identification and Estimation of Local Average Treatment Effects*. | [NBER technical paper t0118](https://www.nber.org/papers/t0118) | IV/complier estimands and identifying assumptions. The linked record includes the published 1994 article. |
| Imbens, Guido W., and Thomas Lemieux (2008). *Regression Discontinuity Designs: A Guide to Practice*. | [NBER technical paper t0337](https://www.nber.org/papers/t0337) | RD threshold identification, local targets and implementation/validity issues. |
| Callaway, Brantly, and Pedro H. C. Sant'Anna (2021). *Difference-in-Differences with Multiple Time Periods*. | [Author-submitted paper, arXiv:1803.09015](https://arxiv.org/abs/1803.09015) | Group/time ATT, staggered adoption, conditional parallel trends and aggregation. |
| Sun, Liyang, and Sarah Abraham (2021). *Estimating Dynamic Treatment Effects in Event Studies with Heterogeneous Treatment Effects*. | [Author-submitted paper, arXiv:1804.05785](https://arxiv.org/abs/1804.05785) | Contamination of conventional event-study coefficients with heterogeneous effects. |
| Abadie, Alberto (2021). *Using Synthetic Controls: Feasibility, Data Requirements, and Methodological Aspects*. | [Journal of Economic Literature article](https://www.aeaweb.org/articles?id=10.1257%2Fjel.20191450) | Donor feasibility, support, counterfactual construction and design limitations. |
| Lopez Bernal, James; Steven Cummins; Antonio Gasparrini (2017). *Interrupted time series regression for the evaluation of public health interventions: a tutorial*. | [Full article, PMC5407170](https://pmc.ncbi.nlm.nih.gov/articles/PMC5407170/) | Impact model specification, seasonality, autocorrelation and concurrent/time-varying confounding. |

These works are cited by author-year/topic in original wording. Links to public
texts are reading pointers; access does not confer redistribution permission.
Use their publishers' or authors' terms for any proposed reuse.

## Official implementation pointers

These are optional downstream destinations. This skill does not import their
software or require their installation. Check the current documentation and
its assumptions before specifying an implementation.

| Project/document | Official source | Appropriate use and limit |
|---|---|---|
| DoWhy, *Estimating Causal Effects* | [PyWhy guide](https://www.pywhy.org/dowhy/main/user_guide/causal_tasks/estimating_causal_effects/index.html) | Graph/estimand identification before estimation and refutation. Refutations cannot certify untestable assumptions. |
| EconML, *Orthogonal/Double Machine Learning* | [PyWhy DML guide](https://www.pywhy.org/EconML/spec/estimation/dml.html) | Nuisance estimation/orthogonalization under explicit identifying assumptions; observed-confounder design still needs exchangeability and support. |
| rdrobust, *Robust Local Polynomial Methods for RD Designs* | [RD Packages repository](https://github.com/rdpackages/rdrobust) | Specialized local RD estimation, bandwidth selection and robust inference; no automatic national extrapolation. |
| did, *Introduction to DiD with Multiple Time Periods* | [Callaway/Sant'Anna vignette](https://bcallaway11.github.io/did/articles/multi-period-did.html) | Practical group/time ATT assumptions, comparisons and aggregation with multiple periods. |

## Adding sources

Verify the title/authors/year and claim support on a primary paper, author book
site, or official documentation page. If the source is unavailable, record that
limitation and use another verified source. A DOI/link existing is not proof that
it supports the proposed claim. Citation locators should name the actual topic;
omit guessed book section numbers. New methods outside this map require a
fresh primary-source check, not a fabricated default.
