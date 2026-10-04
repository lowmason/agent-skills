# Worked recommendation: training eligibility at a score cutoff

This is a hypothetical pre-estimation memo. No dataset has been inspected and
no diagnostics or effects are reported as computed. It demonstrates the memo
contract in [reporting.md](reporting.md); sources are in [sources.md](sources.md).

## 1. Decision and requested estimand

**Result:** the requested national effect is not identified by this design.
The next step is an assignment and outcome-response audit; a local
eligibility-policy analysis is the conditional design that may follow it.

- **Requested causal question:** taking training versus not taking it; earnings
  12 months after assignment, with assignment as time zero; a national
  population; a mean difference. The precise population, training version,
  earnings definition and outcome scale require confirmation. The decision the
  effect informs is `unknown`: it has not been stated (§9).
- **Requested estimand:** the national ATE of actually taking training: the
  difference in mean 12-month earnings if everyone in the population took
  training versus if no one did.
- **Design status for that estimand:** `not identified` by the stated cutoff
  design. Ineligible people cannot take training, so receipt has no support
  below the cutoff, and the cutoff only supplies local assignment variation.
- **Supported alternative estimand:** an eligibility-policy effect at score 60;
  conditionally, a local complier receipt effect under fuzzy-RD assumptions.
  Both are distinct from the national ATE and do not answer it. Both remain
  `conditional` because 20% lack follow-up earnings and the response mechanism
  is unresolved.
- **Recommendation-changing condition:** recovered outcomes, or a defended
  response model, would remove the outcome-observation gate on the local
  effects; sorting at the cutoff or another policy using it would rule the
  design out. Estimation should wait for the audit.

Sources: Imbens and Lemieux (2008); Hernán and Robins (2020).

## 2. Design and data inventory

| Fact | Known/assumed/unknown | Evidence/source | Implication/action |
|---|---|---|---|
| Eligibility uses a published score cutoff of 60 | Known | Scenario description | Verify direction, ties at 60, overrides, appeals, timing and other programs using the score |
| Eligibility means score >= 60 | Assumed | None yet | Confirm before specifying the cohort and rule |
| Eligible applicants may decline; ineligible applicants cannot enroll | Known | Scenario description | One-sided noncompliance; audit enforcement and other enrollment routes |
| Score, receipt, age, region, baseline earnings, follow-up earnings and a response indicator exist | Known | Scenario description | Obtain field definitions, measurement dates, keys and the full applicant cohort |
| About 20% of outcomes are missing near the cutoff; response may depend on eligibility | Rate known; mechanism unknown | Scenario description | Recover or link outcomes and document selection; response rates alone are insufficient |
| A pilot density test was nonsignificant | Known; test output unavailable | Scenario description; pilot output not seen | Obtain method, sample, score resolution and uncertainty; draw no validity verdict |
| National coverage, unit/cluster counts, training timing and concurrent services | Unknown | None | Determine sampling and support, inference, and the plausibility of exclusion |

No data were inspected: every fact comes from the scenario description, and the
second row is an assumption, not an observation. Field roles: score S
(baseline), eligibility Z (set by S), receipt D, baseline covariates X (age,
region, baseline earnings; timing to confirm), 12-month earnings Y and response
indicator R. Applicant keys, the earnings definition and the full cohort are
required additional data.

## 3. Causal structure and adjustment

Provisional edge list, with S=baseline score, X=baseline covariates,
Z=eligibility, D=receipt, Y=12-month earnings, R=outcome observed,
U=unobserved ability/motivation:

- X -> S, X -> D, X -> Y; U -> S, U -> D, U -> Y.
- S -> Z, S -> Y; Z -> D; D -> Y.
- Z -> R, D -> R and Y -> R are plausible, disputed response pathways.
- Z -> Y outside D is an **absent-edge assumption for the receipt effect**;
  counseling/benefits/job-search responses could add it. The policy effect
  permits those eligibility pathways.

Age, region and baseline earnings are predetermined candidates for precision
and diagnostic checks; confirm their timing. The running variable is part of
the local RD specification. This is not national exchangeability given S/X.
R is a post-treatment selection node, and a complete-case analysis conditions
on it: do not condition away R without a defended observation model. Local
continuity of potential outcomes and lack of problematic sorting must be
defended beyond this diagram. Sources: Imbens and Lemieux (2008); Hernán and
Robins (2020).

## 4. Identification assumptions and evidence

| Assumption | Why needed | Supporting evidence | Planned challenge/sensitivity | Untestable remainder or unresolved gate |
|---|---|---|---|---|
| Continuity at 60: no problematic sorting and no other policy at the cutoff | Any local effect at the cutoff | Published cutoff; pilot density result, output not seen | Scoring and appeal audit; density, heaping and covariate checks (§6) | Continuity of potential outcomes is untestable; checks can only fail to find sorting |
| Consistency: one training version and one earnings measure | Every target | None yet | Confirm training versions and the earnings definition | Gate until confirmed |
| Local support around 60 | Any local effect | Scores near 60 exist in the scenario; density and resolution unknown | Inspect local support, score resolution and heaping | Gate if the score is coarse or support near 60 is thin |
| Outcome observation: outcomes recoverable, or response ignorable given eligibility, receipt and defended baseline covariates (no direct Y -> R), with a positive response probability in every such stratum on each side of 60 | Any local outcome effect | 20% missing near the cutoff; mechanism unresolved | Administrative recovery first; otherwise missing-outcome sensitivity or bounds | Gate: without recovery or a defended observation model, local effects are not point-identified; a stratum with no responses near 60 needs recovery or an explicit estimand restriction |
| No interference between applicants | Every target | Unknown | Ask about cohorts, sites and spillovers | Unknown; it changes the estimand |
| First stage: take-up just above 60 is bounded away from zero | Receipt effect only | Receipt is impossible below 60, so the jump is the take-up rate in the limit just above the cutoff; take-up further above 60 does not establish it | Estimate the receipt discontinuity in the full cohort | Gate: if take-up just above 60 tends to zero, the receipt effect is not identified; a small positive jump needs weak-identification-robust inference |
| Exclusion: eligibility affects earnings only through receipt | Receipt effect only; the policy effect permits other pathways | None; concurrent services or job-search responses could violate it | Audit services tied to eligibility | Untestable; if it fails, report only the policy effect |
| Monotonicity: no defiers | Receipt effect only | Ineligible applicants cannot enroll, so no one takes training only when ineligible | Audit enforcement and other enrollment routes | Holds by design if enforcement is complete; an enrollment route below 60 is a gate |

The first five rows identify the local eligibility effect at 60; the last three
add the local complier receipt effect. No row reaches the national ATE. These
are identification conditions, not precision: a valid design with few
applicants near 60 still gives wide intervals. No assumption is declared
empirically verified.

## 5. Candidate comparison and primary choice

| Candidate | Identified estimand | Match to requested target | Critical assumptions | Required data | Main threat | Feasibility/failure action |
|---|---|---|---|---|---|---|
| Eligibility RD | Effect of eligibility at score 60 | Local policy effect; not the national receipt ATE | Continuity, local support, outcome observation | Full cohort: score, eligibility, earnings, response | Sorting, another cutoff policy, selective response | Feasible after the audit; sorting rules it out; a separate program at 60 rules it out unless a bundled-policy estimand is agreed; selective response calls for recovery or bounds |
| Fuzzy receipt RD | Receipt effect for compliers at 60 | Local complier effect; not the national ATE | RD assumptions plus first stage, exclusion and monotonicity | As above, plus receipt records | Exclusion failure from concurrent services; weak first stage | If exclusion fails, retain the policy target separately; a weak first stage needs specialized inference, and an absent one leaves the receipt effect unidentified |
| Broader randomized rollout or encouragement | Offer effect in the rollout population | Closer to the target population; a receipt ATE still needs additional assumptions | Randomization, coverage and follow-up | New assignment and follow-up data | Noncompliance and generalization gaps | Needs a new study; keep assignment and receipt targets distinct |

Primary choice: the local policy design, as a conditional next analysis if it
is useful to the decision; seek agreement before changing the requested target.
Weakest assumption: outcome observation, until outcomes are recovered.
Fallback: if sorting or selective response cannot be addressed, report
descriptive local contrasts and bounds with their own targets. For the national
ATE, design additional coverage and identifying variation. Sources: Hernán and
Robins (2020); Imbens and Angrist (1994).

## 6. Diagnostic, falsification and sensitivity plan

Every check below is planned; none has been performed.

| Check | Data needed | Assumption it can challenge | Limitation | Action if it fails |
|---|---|---|---|---|
| Scoring, override and appeal audit | Scoring rules, appeal and override records, timing | No sorting; assignment as described | Cannot reveal undocumented manipulation | Restrict claims; collect assignment evidence before any estimation |
| Concurrent-services audit | Services and programs triggered at 60 | Exclusion; a single policy at the cutoff | Missing records do not prove there were no services | Services bundled with training eligibility: report only the eligibility-policy effect, defined to include them. A separate program that also starts at 60: the cutoff identifies only the combined effect, so stop, or agree a bundled-policy estimand with the decision-maker |
| Density and heaping at 60 | Full-cohort scores at their recorded resolution | No precise sorting | A smooth density does not prove continuity of potential outcomes | Treat the RD as unsupported; investigate before estimation |
| Predetermined covariates at 60 (age, region, baseline earnings) | Covariates with confirmed pre-assignment timing | Continuity | Balance on observed covariates says nothing about unobserved ones | Investigate sorting; report the imbalance and restrict claims |
| Placebo cutoffs away from 60 | Full-cohort scores and outcomes | Continuity: no jumps where nothing changes | Clean placebos do not prove continuity at 60, and missing outcomes affect them too | Investigate other score-based rules and the outcome specification; restrict claims |
| Receipt discontinuity | Receipt records for the full cohort | First stage | Its strength depends on the local sample | Use weak-identification-robust inference; if its interval for the receipt effect is unbounded, report only the policy effect |
| Response discontinuity | Response indicator for the full cohort | Ignorable outcome observation | Equal response rates do not establish ignorable response | Prioritize outcome recovery; otherwise sensitivity analysis or bounds |
| Bandwidth and local-specification sensitivity | Full cohort | Stability of the local estimate | Agreement across bandwidths does not validate identification | Report the range and flag instability as a limitation |
| Missing-outcome sensitivity or bounds | Response indicator; any recovered outcomes | Outcome observation | Bounds may be wide and have their own target | Report bounds with stated outcome/selection assumptions; do not mechanically divide selected-population bounds by the overall first stage |

Passing these checks would be supporting evidence, not proof of continuity or
exclusion. If attrition cannot be handled defensibly, point identification of
local outcome effects remains unresolved.

## 7. Implementation handoff

Carry §1's estimands, population, time zero and horizon, §2's data, keys and
field roles, and §4's gates into the implementation session. In addition:

Obtain the full cohort/data dictionary and verify assignment and horizon first.
Specify a local-linear RD, justified bandwidth selection, robust bias-corrected
inference, support/discreteness checks and assignment-compatible dependence
handling; use the official rdrobust documentation as a starting pointer. Report
eligibility, receipt first stage, response process and conditional receipt effect
separately. Final outcome-observation strategy, clusters and weak-identification
inference remain gates. Do not fit a national ATE from these cutoff data.

Stop and return to evidence collection if the audit finds sorting, or a separate
program at 60 with no agreed bundled-policy estimand. If outcome observation
cannot be defended, proceed only to the bounds analysis in §6. Bayesian
execution is `not applicable`: the recommended estimator is a local-linear RD
with robust bias-corrected inference.

## 8. Sources

Imbens and Lemieux (2008), Imbens and Angrist (1994), Hernán and Robins (2020),
and official rdrobust documentation: verified links and titles in
[sources.md](sources.md). No unverified chapter locators are used.

## 9. Open questions and next action

| Question | Who/what can answer | Effect on recommendation |
|---|---|---|
| Which decision does the effect inform, and does a local policy effect at 60 answer it? | Domain expert or decision-maker | If not, the recommendation becomes new identifying variation (the rollout) |
| Cutoff direction, ties and overrides; other services triggered at 60 | Domain expert, from the program rules the analyst obtains | Sorting or other services rule out the RD or the receipt effect |
| Can follow-up earnings be recovered or linked? | Analyst, with the data owner | Recovery removes the outcome-observation gate; otherwise sensitivity analysis or bounds |
| Training versions and the earnings definition | Domain expert | Several versions split the target or need a defined composite |
| Spillovers between applicants | Domain expert | Interference changes the estimand and the inference |
| Sample coverage, cluster structure and score precision | Analyst | They set support and the inference method, and decide whether a local design is feasible |

Next: audit and revise this conditional memo, then start implementation in a
fresh session against the completed memo.
