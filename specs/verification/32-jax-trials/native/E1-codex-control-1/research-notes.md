# Research and execution notes

## Authorized task and boundaries

The first tool action executed exactly:

`python3 /private/tmp/jax-skill-trials-pAYZ0t/trial_io.py start /private/tmp/jax-skill-trials-pAYZ0t/native/E1-codex-control-1`

Its full output supplied the authorized inline task: compare A's two reported errors at one million training tokens per run with B's four reported errors at three million tokens per run, and recommend next evidence. The supplied task requested analysis rather than application or model implementation, so no application/model code was needed or delivered.

Only this trial directory was written. No other trials, rubrics, plans, scoring files, or new JAX guidance files were inspected. No agent was spawned or delegated to. The skill collection and repository files were not modified.

## External primary sources actually consulted

- Jesse Dodge et al. (2019), *Show Your Work: Improved Reporting of Experimental Results*. Search result and ACL Anthology landing page/abstract read using the web tool: https://aclanthology.org/D19-1224/. Used to support the recommendation to report and compare performance relative to training/search computation budgets. The answer's concrete experiment design is my application to the supplied numbers, not a quoted prescription from the paper.
- Xavier Bouthillier et al. (2021), *Accounting for Variance in Machine Learning Benchmarks*. Search result and authors' arXiv landing page/abstract read using the web tool: https://arxiv.org/abs/2103.03098. Used to support accounting for data sampling, initialization, and hyperparameter variation. The answer's pilot size and decision rule are my proposed design, not numerical thresholds taken from this paper.

Searches also returned other pages. Those were not used as substantive evidence. No full-text PDFs or paper code were downloaded or executed.

## Ordinary skill sources actually read

- `/Users/lowell/.agents/skills/track-model-experiments/SKILL.md` was read in full to assess applicability. Its workflow concerns Bayesian structural model variants, experiment ledgers, and ELPD/LOO comparison. It was not applied to these generic held-out error rates; no ArviZ comparison or ELPD threshold was imported into the answer.
- `/Users/lowell/.agents/skills/develop-testing-strategy/SKILL.md` was read in full to assess applicability. Its workflow concerns automated data-science correctness tests and CI plans. It was not applied because this task asks for comparative experimental evidence, not a repository test suite. No design approval or implementation handoff was introduced.
- `/Users/lowell/.agents/skills/verification-before-completion/SKILL.md` was read in full and applied only to verifying the saved answer and source notes before declaring the delivery complete. Verification consisted of read-only file inspection, not application/model execution.

## Calculations and interpretation

Arithmetic was worked out directly from the supplied values without running analytical/model code:

- A mean: `(0.14 + 0.16) / 2 = 0.15`.
- B mean: `(0.13 + 0.18 + 0.14 + 0.12) / 4 = 0.1425`.
- A sample variance: `0.0002`; sample SD approximately `0.014142`.
- B sum of squared deviations: `0.002075`; sample variance `0.002075 / 3`; sample SD approximately `0.026300`.
- Observed mean(A) − mean(B): `0.0075`; relative reduction versus A: `0.0075 / 0.15 = 0.05`.
- Conditional independent-run standard-error estimate: `sqrt(0.0002 / 2 + (0.002075 / 3) / 4)`, approximately `0.01652`. Explicitly conditional on independent runs and excluding finite-test-set uncertainty; not used to claim a definitive statistical result.
- Reported total training tokens: A `2 × 1 million = 2 million`; B `4 × 3 million = 12 million`. Tokens are not asserted to equal FLOPs or wall time.
- Shared labels give B − A differences `−0.01` and `+0.02`; these were treated as descriptive, not guaranteed valid pairs.

## Explicit nonexecution

No delivered application code, JAX code, training, model evaluation, statistical fitting, bootstrap, power-analysis script, or test suite was executed. The only Python execution was the required trial task helper. Other tools read ordinary skill files and primary-source pages, wrote literal artifact text, and inspected the resulting artifacts. No new JAX skill was read.
