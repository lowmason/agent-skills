# Research notes

## Task and supplied guidance

- Executed the authorized start operation for this trial and read its full output.
- Actual task: compare A errors [0.14, 0.16] at 1 million tokens per run against B errors [0.13, 0.18, 0.14, 0.12] at 3 million tokens per run, and recommend next evidence.
- Applied the complete inline evaluate-deep-learning task-specific guidance supplied by the start operation.
- Read supplied references only through trial_io.py readref for this owned trial directory:
  - references/protocol.md: comparison estimands, budget distinction, run/unit pairing, uncertainty and the example matching the supplied scores.
  - references/experiments.md: per-run reconstruction and uncertainty/resource record contract.
  - references/domain-checks.md: predictive uncertainty and domain-specific validity scope; model family is unspecified, so no family-specific checks were claimed.
- Ordinary skills used beyond the supplied evaluate-deep-learning guidance: none. The task is an authorized inline statistical interpretation, not a repository change, training implementation or posterior analysis.

## External source actually accessed

- Bouthillier et al. (2021), Accounting for Variance in Machine Learning Benchmarks, https://arxiv.org/abs/2103.03098.
- Accessed the primary-source arXiv abstract page with web tools. Used its abstract only to support the claim that data sampling, initialization and hyperparameter choices affect benchmarking variation. Did not claim to read or execute the full paper.

## Arithmetic and execution status

- Executed host-side JavaScript descriptive arithmetic on the six supplied numbers: means A 0.1500 and B 0.1425; sample SDs A 0.0141421356 and B 0.0262995564; A-minus-B mean difference 0.0075; relative reduction 0.05; ranges A [0.14, 0.16], B [0.12, 0.18]; supplied total token exposure A 2 million and B 12 million.
- Explicit nonexecution: no delivered application/model code, JAX code, reference fixture, training, inference, checkpoint evaluation, bootstrap, hypothesis test, confidence interval, numerical validation or accelerator check was executed.
- No model/data artifacts were available. All six scores were treated as reported observations, not independently reproduced measurements.
- Wrote only response.txt and research-notes.md in the owned trial directory, apart from helper-maintained read logging. No other trials, rubrics, scoring, plans or out-of-snapshot JAX skill files were inspected; no repository files were changed; no agents were spawned.
