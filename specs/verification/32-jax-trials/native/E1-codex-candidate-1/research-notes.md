# Sources and execution record

## Supplied task-specific guidance actually read

- Full evaluate-deep-learning main guidance supplied by `trial_io.py start` for this trial. It established the evaluation contract, separate uncertainty categories, resource comparability, required output slots and explicit nonexecution status.
- `references/protocol.md`, read exclusively through `trial_io.py readref`. This includes the exact supplied A/B example, the means 0.15 and 0.1425, A-minus-B gap 0.0075, unequal-token caveat, seed-pairing requirements and common-budget schedule policy. Its canonical CPU fixture was read as reference text and was not executed or copied into the answer.
- `references/experiments.md`, read exclusively through `trial_io.py readref`. Used for the run-record fields, explicit unknowns, per-run artifacts and distinction between reported completion and established quality.
- `references/domain-checks.md` was not read because the task identifies no model family or input/output domain. The answer explicitly marks family-specific checks as unresolved and does not claim domain validation.

## Primary web sources actually opened

- Bouthillier et al. (2021), *Accounting for Variance in Machine Learning Benchmarks*: https://arxiv.org/abs/2103.03098. Opened and read the abstract/landing page, not the full paper. Supports the limited statement that benchmark variation can arise from data sampling, augmentation, initialization and hyperparameter choices. No fixed sample-size claim, power calculation or statistical coverage guarantee was attributed to it.
- Pineau et al. (2021), *Improving Reproducibility in Machine Learning Research (A Report from the NeurIPS 2019 Reproducibility Program)*: https://jmlr.org/papers/v22/20-303.html. Opened and read the abstract/landing page, not the full paper. Supports the broad emphasis on reproducible research workflows; the specific record contract comes from supplied experiments.md.

## Ordinary skills actually used

- `verification-before-completion`, read at `/Users/lowell/.agents/skills/verification-before-completion/SKILL.md`. Applied only to verifying existence and full written contents of the two requested deliverables before reporting completion. It did not authorize or trigger model/application execution.
- No other ordinary skill was loaded. No new JAX skill files outside the supplied snapshot, other trials, rubrics, scoring files or plans were inspected.

## Nonexecution and artifact scope

- No delivered application/model code was executed. No JAX fixture, training run, evaluation, bootstrap, statistical interval, model inference or hardware test was run.
- Descriptive means and the 0.0075 gap were available in the supplied reference and checked by direct arithmetic. The relative improvement is 0.0075 / 0.15 = 0.05. No inferential numerical output is reported.
- Tools used for information gathering were the authorized trial helper, a read of the ordinary verification skill and read-only web browsing of the two primary sources above.
- Only response.txt and research-notes.md were intentionally written; the supplied helper may also update its authorized read log. No repository or skill-collection files were modified. No agents were spawned or delegated to.
- response.txt contains the full substantive answer verbatim. No code implementation was requested by the task itself, so the answer delivers the comparison and next-evidence protocol without an unnecessary executable example.
