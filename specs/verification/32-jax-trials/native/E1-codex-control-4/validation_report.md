# Validation Report — unequal-budget method comparison

- **Mode:** analysis QA
- **Validated:** supplied inline task read by the trial helper (hash: not available; vintage: task supplied 2026-10-03)
- **Validator:** Codex application agent **Date:** 2026-10-03 **Verdict:** PASS-WITH-WARNINGS

## 1. Schema & integrity
- Schema contract: PASS — six supplied error observations, indexed by method and seed, with method-specific token budgets.
- Nulls / uniqueness / duplicates: PASS — no missing supplied values; each method-seed key is unique. Raw run records were not supplied.
- Value ranges & cardinality: PASS — A has two values from 0.14 to 0.16; B has four values from 0.12 to 0.18. Metric meaning beyond lower-is-better is assumed explicitly.

## 2. Reproducibility & determinism
- Re-run parity: WARN — no training or analysis code executed; original artifacts and hashes unavailable.
- Seeds fixed & descriptive: WARN — seed labels supplied, stream definitions and coupling unavailable.
- Inputs pinned / vintaged: WARN — only inline summaries supplied; data, code and configuration identities unavailable.
- As-of / no future leakage: N-A for descriptive arithmetic; WARN for model evaluation because held-out data provenance and selection history are unavailable.

## 3. Accuracy
- Benchmark reconciliation: WARN — original training logs or independent metrics unavailable; supplied numbers treated as inputs, not externally confirmed results.
- Units / scale / sign: PASS — mean gap 0.0075 in error units; percentage-point interpretation explicitly conditional on errors being proportions. Per-run token ratio 3; total reported token ratio 6.
- Edge periods: N-A — no time series. PASS — all six runs, including B's 0.18 result, retained in summaries.

## 4. Methodology & bias
- Conclusions supported: PASS — response limits conclusion to observed endpoints and identifies insufficient evidence for superiority or equivalence.
- Within vs composition: PASS — common-seed subset reverses observed ranking; no budget effect or seed effect estimated causally.
- Coverage / selection / survivorship / revision: WARN — run selection, tuning history and test-set representativeness unavailable. Equal-budget replication and untouched confirmation proposed.

## 5. Fail-loud audit
- Silent fallbacks / fill_null on denominators / swallowed errors: N-A — no data pipeline executed. PASS — missing information is explicitly stated rather than assumed verified.

## Blocking issues
1. No blocking issue for delivering descriptive arithmetic and an evidence-collection recommendation. A definitive superiority claim would be unsupported until matched-budget and uncertainty evidence is collected.

## Warnings (non-blocking)
1. Descriptive values depend on supplied summaries; reproducibility was not verified.
2. Small unequal sample counts and unequal training budgets prevent a reliable winner declaration.
3. The standard-error calculation is illustrative and assumes independent runs; it is not an inferential decision rule for these observations.
