# Research notes

Authorized task: interpret the six supplied held-out errors and unequal training exposures, and recommend the next discriminating evidence. The task requests analysis; no model implementation is necessary.

## Guidance actually used

- Full evaluate-deep-learning task-specific guidance supplied by `trial_io.py start` for this trial.
- `references/protocol.md`, read exclusively with the authorized `trial_io.py readref` operation. Used the explicit example's means and A-minus-B difference, resource/selection contract, seed-pairing distinction, and separated uncertainty sources. Did not execute its canonical JAX/NumPy fixture.
- `references/experiments.md`, read exclusively with the authorized `trial_io.py readref` operation. Used its run-record contract and explicit unknown-field policy.
- Ordinary skill: `/Users/lowell/.agents/skills/verification-before-completion/SKILL.md`, read completely. Applied to checking the two saved deliverables before reporting completion, not to claiming any model result.

## Primary sources actually opened

- Bouthillier et al. (2021), Accounting for Variance in Machine Learning Benchmarks: https://arxiv.org/abs/2103.03098. Opened via web tool and read returned abstract/metadata. Supports sources of benchmarking variation and repeated comparisons. No claim is made about a universal sufficient seed count or statistical power.
- Pineau et al. (2021), Improving Reproducibility in Machine Learning Research (A Report from the NeurIPS 2019 Reproducibility Program): https://jmlr.org/papers/v22/20-303.html. Opened via web tool and read returned abstract/metadata. Supports reproducibility and inspectable experiment workflows. Did not read or claim to inspect the full PDFs.

## Nonexecution and access boundaries

No application/model code was executed. No training, JAX fixture, prediction generation, statistical resampling, confidence interval, significance test, leakage audit, model-family domain check or hardware/checkpoint validation was executed. Descriptive means and difference were provided explicitly in the authorized protocol reference and checked by direct arithmetic in reasoning. No predictive-uncertainty result is asserted. Proposed experiments remain unexecuted.

Only this trial's authorized main output, its two authorized references, the ordinary skill above, and the two named primary-source web pages were read. No other trial, scoring/rubric, implementation plan or outside new JAX skill file was inspected. No subagent was spawned or delegated. No repository files were modified. The only intended artifact mutations are `response.txt`, `research-notes.md`, and the helper's read log. File contents were written as literal Python strings in a quoted heredoc so the shell cannot execute their contents.
