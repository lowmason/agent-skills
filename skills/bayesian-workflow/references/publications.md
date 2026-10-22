# Workflow references (cited, not bundled)

The skill cites these by author-year and, for the book, by chapter/section number.
None are redistributed here (see the repo-root NOTICE).

- Gelman, Vehtari, McElreath, Simpson, Margossian, Yao, Kennedy, Gabry, Bürkner, Modrák &
  Leos Barajas (2026), *Bayesian Workflow* — Chapman & Hall/CRC. Cited as
  "Gelman et al. 2026, §x.y" using the book's section numbers.
  Website: https://avehtari.github.io/Bayesian-Workflow/ (electronic edition for
  non-commercial use only). The companion code repository carries no license file, so
  its R/Stan case studies are cited by chapter and not ported.
- Gelman et al. (2020), *Bayesian Workflow* — arXiv:2011.01808. The open-access preprint
  the book grew from; use it when a reader cannot access the book. Its section numbers
  differ from the book's (e.g. the folk theorem is paper §5, book §12.4).
- Betancourt (2020), *Towards a Principled Bayesian Workflow* —
  https://betanalpha.github.io/assets/case_studies/principled_bayesian_workflow.html (CC BY-NC 4.0)
- Bürkner, Gabry & Vehtari (2021), *Efficient leave-one-out cross-validation for Bayesian
  non-factorized normal and Student-t models*, Computational Statistics 36(2), pp. 1243–1261 —
  doi:10.1007/s00180-020-01045-4 / arXiv:1810.10559. Cited as "Bürkner, Gabry and Vehtari 2021"
  for the closed-form leave-one-out densities of a joint Gaussian, the route to pointwise LOO for
  the exact GP (gaussian-processes.md).
- Gabry et al. (2019), *Visualization in Bayesian workflow*, JRSS-A 182(2) —
  doi:10.1111/rssa.12378 / arXiv:1709.01449
- Magnusson, Riis Andersen, Jonasson & Vehtari (2019), *Bayesian leave-one-out
  cross-validation for large data*, ICML 2019, PMLR 97:4244–4253 — arXiv:1904.10679. Cited as
  "Magnusson et al. 2019" for PSIS-LOO with an approximate posterior (svi.md).
- McLatchie & Vehtari (2024), *Efficient estimation and correction of selection-induced bias
  with order statistics*, Statistics and Computing 34(4), article 132 —
  doi:10.1007/s11222-024-10442-4. Cited as "McLatchie & Vehtari 2024" for the selection-induced
  bias of picking the best of many models by ELPD.
- Modrák, Moon, Kim, Bürkner, Huurre, Faltejsková, Gelman & Vehtari (2025),
  *Simulation-based calibration checking for Bayesian computation: The choice of test
  quantities shapes sensitivity*, Bayesian Analysis 20, pp. 461–488. Cited as
  "Modrák et al. 2025" for SBC test quantities.
- Riutort-Mayol, Bürkner, Andersen, Solin & Vehtari (2023), *Practical Hilbert space
  approximate Bayesian Gaussian processes for probabilistic programming*, Statistics and
  Computing 33(1), article 17 — doi:10.1007/s11222-022-10167-2 / arXiv:2004.11408. Cited as
  "Riutort-Mayol et al. 2023" for HSGP's boundary and basis-size settings (gaussian-processes.md).
- Säilynoja, Bürkner & Vehtari (2022), *Graphical test for discrete uniformity and its
  applications in goodness-of-fit evaluation and multiple sample comparison*,
  Statistics and Computing 32(32). The Δ-ECDF simultaneous-band construction behind
  ArviZ's PIT-ECDF plots (`plot_ecdf_pit(..., method="envelope")`).
- Säilynoja, Schmitt, Bürkner & Vehtari (2026), *Posterior SBC: Simulation-based
  calibration checking conditional on data*, Statistics and Computing 36(78). Cited as
  "Säilynoja, Schmitt et al. 2026".
- Sivula, Magnusson, Matamoros & Vehtari (2025), *Uncertainty in Bayesian leave-one-out
  cross-validation based model comparison*, Bayesian Analysis (advance publication) —
  doi:10.1214/25-BA1569 / arXiv:2008.10296. Cited as "Sivula et al. 2025" for when `dse` describes
  the uncertainty of an ELPD difference (|Δ| > 4, n > 100, no badly misspecified model).
- Solin & Särkkä (2020), *Hilbert space methods for reduced-rank Gaussian process regression*,
  Statistics and Computing 30(2), pp. 419–446 — doi:10.1007/s11222-019-09886-w /
  arXiv:1401.5508. Cited as "Solin and Särkkä 2020" for the Hilbert-space basis-function
  approximation behind HSGP (gaussian-processes.md).
- Talts, Betancourt, Simpson, Vehtari & Gelman (2018), *Validating Bayesian inference
  algorithms with simulation-based calibration* — arXiv:1804.06788. Cited as "Talts et al.
  2018" after the preprint year; the book's reference list dates it 2020 and links the authors'
  unpublished PDF at sites.stat.columbia.edu/gelman/research/unpublished/sbc.pdf, not arXiv.
- Tesso & Vehtari (2026), *LOO-PIT predictive model checking* — arXiv:2603.02928. Cited as
  "Tesso & Vehtari 2026" for the `pot_c` uniformity test behind ArviZ's default PIT plots
  (`plot_ppc_pit`, `plot_loo_pit`, `plot_ecdf_pit`) and `scripts/calibration_check.py`'s verdicts.
- Yao, Vehtari, Simpson & Gelman (2018), *Yes, but did it work?: Evaluating variational
  inference*, ICML 2018, PMLR 80:5581–5590 — arXiv:1802.02538. Cited as "Yao et al. 2018" for
  VSBC, the check behind NumPyro's `vsbc_diagnostic` (svi.md).
