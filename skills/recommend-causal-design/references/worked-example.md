# Worked recommendation: training eligibility at a score cutoff

This is a hypothetical pre-estimation memo. No dataset has been inspected and
no diagnostics or effects are reported as computed. It demonstrates the memo
contract in [reporting.md](reporting.md); sources are in [sources.md](sources.md).

## 1. Decision and requested estimand

**Requested:** the national ATE of actually taking training on earnings 12 months
after assignment. The precise population, training version, earnings definition
and outcome scale require confirmation. **Design status: not identified** by
the stated cutoff design. Ineligible people cannot take training, and the cutoff
only supplies local assignment variation.

**Proposed alternative:** an eligibility-policy effect at score 60; conditionally,
a local complier receipt effect under fuzzy-RD assumptions. Both are distinct
from the national ATE. Local outcome effects remain **conditional** because
20% lack follow-up earnings and the response mechanism is unresolved. Recommend
an assignment/response audit and outcome recovery before choosing a point-effect
analysis. Sources: Imbens and Lemieux (2008); Hernán and Robins (2020).

## 2. Design and data inventory

| Fact | Status | Evidence/action |
|---|---|---|
| Eligibility uses a published score cutoff of 60 | Known from scenario | Verify direction, equality/overrides, appeals, timing and other programs |
| Assume eligibility means score >= 60 | Assumed | Confirm before specifying the cohort/rule |
| Eligible applicants may decline; ineligible cannot enroll | Known from scenario | Audit enforcement and other enrollment routes |
| Score, receipt, age, region, baseline earnings, follow-up earnings and response indicator are available | Known from scenario | Obtain field definitions, measurement dates and full applicant cohort |
| About 20% missing outcomes near cutoff; response may depend on eligibility | Known/unresolved mechanism | Recover/link outcomes and document selection; response rates alone are insufficient |
| Density test nonsignificant in pilot | Known from scenario; test output unavailable | Obtain method, sample, score resolution and uncertainty; no validity verdict |
| National coverage, unit/cluster counts, training timing and concurrent services | Unknown | Determine sampling/support, inference and exclusion plausibility |

## 3. Causal structure and adjustment

Provisional edge list, with S=baseline score, X=baseline covariates,
Z=eligibility, D=receipt, Y=12-month earnings, R=outcome observed,
U=unobserved ability/motivation:

- X -> S, X -> D, X -> Y; U -> S, U -> D, U -> Y.
- S -> Z, S -> Y; Z -> D; D -> Y.
- Z -> R and Y -> R are plausible, disputed response pathways.
- Z -> Y outside D is an **absent-edge assumption for the receipt effect**;
  counseling/benefits/job-search responses could add it. The policy effect
  permits those eligibility pathways.

Age, region and baseline earnings are predetermined candidates for precision
and diagnostic checks; confirm their timing. The running variable is part of
the local RD specification. This is not national exchangeability given S/X.
Do not condition away R without a defended observation model. Local continuity
of potential outcomes and lack of problematic sorting must be defended beyond
this diagram. Sources: Imbens and Lemieux (2008); Hernán and Robins (2020).

## 4. Identification assumptions and evidence

Continuity/no problematic sorting requires scoring/appeal rules and local support;
the pilot density result cannot prove it. A receipt effect additionally needs
a meaningful first stage, exclusion, and monotonicity; the one-sided enrollment
rule supports monotonicity if enforced, while concurrent services threaten
exclusion. Outcome observation needs its own assumptions: administrative recovery
is preferable; response weighting/imputation would require a defended ignorable
observation model and response support. Otherwise use explicit sensitivity or
defensible bounds. Interference, treatment consistency and cluster dependence
remain unknown. No assumption is declared empirically verified.

## 5. Candidate comparison and primary choice

| Candidate | Target/match | Key requirement | Threat/failure action |
|---|---|---|---|
| Eligibility RD | Local policy effect; not national receipt ATE | Continuity/assignment and outcome observation | Sorting, another cutoff policy or selection: recover evidence, restrict claims |
| Fuzzy receipt RD | Local complier effect; not national ATE | RD plus first stage/exclusion/monotonicity | Exclusion failure: retain policy target separately; weak first stage: specialized inference |
| Broader randomized rollout or encouragement | A target-population offer effect; receipt ATE still needs additional assumptions | Coverage, assignment, follow-up and a precise target | Noncompliance/generalization gaps: keep assignment/receipt targets distinct |

Choose the local policy design as a conditional next analysis if it is useful
to the decision; seek agreement before changing the requested target. For the
national ATE, design additional coverage and identifying variation. Sources:
Hernán and Robins (2020); Imbens and Angrist (1994).

## 6. Diagnostic, falsification and sensitivity plan

All checks are planned: audit scoring/manipulation and concurrent services;
inspect local support/heaping, density and predetermined covariates; examine
receipt and response discontinuities in the full cohort; plan bandwidth/local
specification sensitivity and missing-outcome sensitivity. Document limitations
and stop actions for each. If attrition cannot be handled defensibly, point
identification of local outcome effects remains unresolved. Bounds require
stated outcome/selection assumptions and their own target; do not mechanically
divide selected-population bounds by the overall first stage.

## 7. Implementation handoff

Obtain the full cohort/data dictionary and verify assignment and horizon first.
Specify a local-linear RD, justified bandwidth selection, robust bias-corrected
inference, support/discreteness checks and assignment-compatible dependence
handling; use the official rdrobust documentation as a starting pointer. Report
eligibility, receipt first stage, response process and conditional receipt effect
separately. Final outcome-observation strategy, clusters and weak-identification
inference remain gates. Do not fit a national ATE from these cutoff data.

## 8. Sources

Imbens and Lemieux (2008), Imbens and Angrist (1994), Hernán and Robins (2020),
and official rdrobust documentation: verified links and titles in
[sources.md](sources.md). No unverified chapter locators are used.

## 9. Open questions and next action

The analyst obtains data/rules, outcome-recovery options, sample coverage,
score precision and dependence information. The domain expert resolves cutoff
direction/other services, treatment versions, spillovers and whether a local
policy effect answers the decision. Next: audit and revise this conditional
memo, then start implementation in a fresh session against the completed memo.
