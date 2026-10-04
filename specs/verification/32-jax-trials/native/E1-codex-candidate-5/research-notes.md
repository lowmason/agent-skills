# Research notes

## Authorized task and task-specific guidance

- Read the full output of the required `trial_io.py start` invocation for this trial. The authorized question asks which method is better from A errors [0.14, 0.16] at 1 million training tokens per run and B errors [0.13, 0.18, 0.14, 0.12] at 3 million, and which evidence to collect next.
- Applied the complete supplied evaluate-deep-learning main guidance in the startup output. No outside/new JAX skill files or other trials were inspected.
- Read the supplied `references/protocol.md` exclusively through the authorized `trial_io.py readref` operation. Used its resource-contract, unequal-run, actual-pairing, evaluation-unit and uncertainty guidance. It contains the exact descriptive example; no fixture was executed.
- Read the supplied `references/experiments.md` exclusively through the authorized `trial_io.py readref` operation. Used the run record contract and explicit unknown/status conventions. Its completed synthetic fixture record is not evidence of execution in this trial.
- Did not load domain-checks.md because no model family is specified; the response identifies unresolved domain requirements rather than inventing a domain.

## Ordinary skills used

- verification-before-completion: read `/Users/lowell/.agents/skills/verification-before-completion/SKILL.md`. Applied only to verifying the two text deliverables and matching claims to actual evidence. This does not override the explicit nonexecution task scope, and no model/code test success is claimed.
- No Bayesian, posterior-inference, model implementation, tuning implementation, or code-writing workflow was invoked. The user asks for a decision and evidence plan, so the substantive deliverable is analysis rather than unsolicited application code.

## Primary sources actually consulted

- Bouthillier et al. (2021), Accounting for Variance in Machine Learning Benchmarks: https://arxiv.org/abs/2103.03098 . Opened the primary-source abstract via the web tool. Supports the narrow claim that benchmark variation includes data sampling, initialization, augmentation and hyperparameter choices. The proposed budget grid and decision threshold are analysis recommendations grounded in supplied guidance, not claims that this abstract proves a fixed run count sufficient.
- Pineau et al. (2021), Improving Reproducibility in Machine Learning Research: https://jmlr.org/papers/v22/20-303.html . Opened the journal's primary-source abstract via the web tool. Supports the narrow reproducibility claim concerning code/data and robust reporting/workflows.
- Both are cited by ordinary Markdown links near the corresponding substantive claims in response.txt. No full-paper results beyond the inspected abstracts are represented as independently reviewed.

## Arithmetic and explicit nonexecution

- Descriptive arithmetic: A mean = (0.14 + 0.16)/2 = 0.15; B mean = (0.13 + 0.18 + 0.14 + 0.12)/4 = 0.1425; A-minus-B = 0.0075. Ranges are A [0.14, 0.16] and B [0.12, 0.18]. Supplied total exposure is A 2 million tokens and B 12 million tokens.
- The response does not equate training tokens with physical compute/cost, infer paired training randomness from seed labels, discard unequal extra runs, claim equivalence from non-detection, fabricate finite-test uncertainty, or report predictive calibration from seed spread.
- No delivered application/model code, canonical JAX fixture, training, interval/bootstrap procedure, checkpoint evaluation, solver or hardware test was executed. Only helper startup/reference reads, an ordinary skill read, source browsing, literal text writes, and deliverable inspection were performed.
- Model family, evaluation units, held-out IDs, contamination, preprocessing/selection, metric units, environment, measured physical budgets and underlying run verification remain explicitly unknown.

## Artifact verification

- Verify response.txt and research-notes.md are nonempty, readable UTF-8 text with the expected answer and source/nonexecution statements. Artifact verification is distinct from model or statistical validation.
- Mutations are limited to these two assigned text files and the helper-managed reference-read log.
