# Research notes

Authorized task: Compare supplied A/B held-out errors and training exposures, and identify the next useful evidence. Deliver an inline analysis; no new design/approval workflow and no model execution.

## Actual sources consulted

- Main task and complete task-specific `evaluate-deep-learning` guidance, obtained by the required `trial_io.py start` operation for this trial.
- Supplied `references/protocol.md`, obtained only through `trial_io.py readref`. Used its exposure-versus-physical-cost distinction, explicit arithmetic for this exact A/B example, actual-random-factor pairing rule, separate uncertainty units, practical decision rule, and common-budget/schedule guidance.
- Supplied `references/experiments.md`, obtained only through `trial_io.py readref`. Used its per-run record contract, explicit unknown fields, artifact guarantees, and separation of completed runs from method-quality claims.
- Ordinary skill `/Users/lowell/.agents/skills/validate-data/SKILL.md`, read via `cat`. Applied analysis QA to the six supplied numbers and the scope of supported conclusions. Its code/pipeline rerun requirements do not constitute execution authorization here; the task explicitly requests nonexecution. Its report is included below within this authorized artifact rather than creating another file.
- Ordinary skill `/Users/lowell/.agents/skills/verification-before-completion/SKILL.md`, read via `cat`. Applied to verifying that the requested delivery files exist and contain the intended substantive answer and notes, without claiming model/tests passed.

No web browsing or external paper lookup occurred. Papers linked inside the supplied protocol were not opened or relied upon as independently inspected sources. No other trial, scoring/rubric, plan, or new JAX skill file was inspected. No domain reference was loaded because no model family is supplied. No subagent was spawned.

## Explicit nonexecution

No delivered application/model code was executed. No model was trained, no checkpoint was loaded or evaluated, and no JAX fixture, test suite, bootstrap, confidence-interval code, or hardware benchmark was run. Only authorized helper reads, ordinary skill reads, literal delivery-file writes, and delivery-file verification were performed. Descriptive means and differences are simple arithmetic on the user-supplied scores and are also explicitly present in the supplied protocol. The response makes no numerical inferential interval or executed-check claim. No application code was requested by the underlying question, so none was added.

# Validation Report — supplied A/B comparison

- **Mode:** analysis QA
- **Validated:** six scores and per-run exposures supplied by the task (hash/vintage: no external data artifact or release supplied)
- **Validator:** Codex trial agent   **Date:** 2026-10-03   **Verdict:** PASS-WITH-WARNINGS for descriptive analysis only; experiment validity remains unverified

## 1. Schema & integrity
- Schema contract: PASS by inspection of supplied text — A has seed/score pairs 0/0.14, 1/0.16 at 1M tokens; B has 0/0.13, 1/0.18, 2/0.14, 3/0.12 at 3M tokens.
- Nulls / uniqueness / duplicates: PASS for supplied run labels by inspection — 2 unique A labels and 4 unique B labels; no missing supplied aggregate scores. Underlying samples, excluded runs, and failures remain unknown.
- Value ranges & cardinality: PASS for supplied finite positive values by inspection; true metric domain not provided.

## 2. Reproducibility & determinism
- Re-run parity: N-A for this authorized nonexecuted analysis; training/evaluation cannot be reproduced from the summary.
- Seeds fixed & descriptive: WARN — numeric seed labels supplied, random-stream policies and actual shared factors absent.
- Inputs pinned / vintaged: WARN — no immutable dataset, split, prediction or configuration artifacts supplied.
- As-of / no future leakage: WARN — training/test provenance and model family absent; leakage/contamination cannot be certified.

## 3. Accuracy
- Benchmark reconciliation: PASS for mean/gap arithmetic against the separately read supplied protocol; no independent confirmation of original training/evaluation scores.
- Units / scale / sign: WARN — lower-is-better assumed from “error”; exact metric, units, aggregation and denominator absent. No percentage-point interpretation invented.
- Edge periods: N-A — no temporal data supplied. All six runs retained, including B's 0.18.

## 4. Methodology & bias
- Conclusions supported: PASS — only observed endpoint mean advantage claimed; repeatable superiority, equivalence and physical efficiency withheld.
- Within vs composition: N-A — no decomposition requested; method effects cannot be separated from exposure with these endpoints.
- Coverage / selection / survivorship / revision: WARN — held-out population, selection/tuning history, all attempted runs, domain coverage and data provenance unknown. These are named as evidence to collect.

## 5. Fail-loud audit
- Silent fallbacks / fill_null on denominators / swallowed errors: N-A — no pipeline executed or implementation inspected. Unknown fields remain explicit and no plausible replacement measurements invented.

## Blocking issues
1. No issue blocks the limited descriptive answer. Missing common-budget evidence and evaluation provenance block a method-wide superiority, equivalence, or physical-efficiency verdict.

## Warnings (non-blocking)
1. Two A runs and four B runs offer limited information about training-run variation; unequal counts alone do not justify discarding data.
2. Finite-test uncertainty cannot be estimated from aggregate seed scores without unit-level evidence and a dependence contract.
3. Predictive probabilities/intervals are absent; seed variability is not predictive calibration.
4. Proposed training, statistical, domain, confirmation-set and hardware checks remain unexecuted.
