# Recommendation memo contract

Write `<analysis-slug>/causal-design.md` with these sections, in this order.
Use concrete variable names if known; otherwise label the missing definitions.
Every required field receives a value or `unknown/not applicable` plus a reason.
Do not invent data, successful diagnostics, implementation results, or references
to make the memo look complete. It must be usable in a fresh analysis session.

## 1. Decision and requested estimand

Start with the primary recommendation or the precise non-identification result.
Required fields:

- **Requested causal question:** intervention/comparator, outcome, population,
  time zero and horizon, contrast/scale, and decision the effect informs.
- **Requested estimand:** name and a plain-language definition; notation if useful.
- **Design status for that estimand:** `plausibly identified`, `conditional`, or
  `not identified`, with a reason tied to assignment, support, or assumptions.
- **Supported alternative estimand:** separately defined, including its local
  population/horizon. State whether it answers the original question.
- **Recommendation-changing condition:** the fact or evidence that would change
  the choice, including whether estimation should wait.

## 2. Design and data inventory

Provide a table of **fact**, **known/assumed/unknown**, **evidence/source**, and
**implication/action**. Cover assignment and receipt; unit/cluster; adoption or
cutoff/encouragement rules; measurement timing; comparison eligibility;
sampling/coverage; outcome observation; interference/concurrent events;
data access, unit/period counts and support when known.

State profiling performed and actual observations, or that no data were inspected.
Provide field roles/times, keys, outcome definitions and required additional data.
Separate design assumptions from empirical observations.

## 3. Causal structure and adjustment

Include an actual Mermaid DAG or labeled edge list, node definitions and timing,
unobserved variables, and observation/selection processes. Required fields:

- Target pathways and proposed adjustment set, with inclusion/exclusion reasons.
- Mediators/colliders and post-treatment measurements relevant to this target.
- Disputed edges and explicit absent-edge assumptions; their effect on the design.
- Design restrictions the graph does not encode, such as continuity/parallel trends.

If domain knowledge is insufficient, include a provisional graph with labeled
unknowns and the questions needed to distinguish alternatives. Merely promising
to draw a DAG during implementation does not satisfy this section.

## 4. Identification assumptions and evidence

Use a ledger: **assumption**, **why needed**, **supporting evidence**, **planned
challenge/sensitivity**, **untestable remainder or unresolved gate**. Include
consistency, exchangeability/design restriction, support/positivity, selection/
missingness and interference as applicable. State the target identified under
those assumptions and distinguish identification from statistical precision.

## 5. Candidate comparison and primary choice

Compare 2–3 credible designs using columns **candidate**, **identified estimand**,
**match to requested target**, **critical assumptions**, **required data**,
**main threat**, and **feasibility/failure action**. If only one design is
credible, a descriptive/bounds or new-data option can supply the honest comparison.

Explain the primary choice, weakest assumption, and fallback. An alternative
estimand remains explicitly separate even when it is the most useful next step.
For non-identification, give a concrete evidence-collection plan and distinguish
associations/bounds from point-identified effects.

## 6. Diagnostic, falsification and sensitivity plan

For each item specify **check**, **data needed**, **assumption it can challenge**,
**limitation**, and **action if it fails**. Label checks as planned, performed,
or unavailable. Include design-specific checks, negative controls/placebos where
credible, missingness sensitivity, support failures, and plausible alternative
causal structures. State what passed diagnostics cannot prove.

## 7. Implementation handoff

Carry these fields together:

- Final requested and proposed analysis estimands, population/sample restrictions,
  intervention/comparator, outcome/scale, time zero and follow-up horizon.
- Data files/access, unit/time/cluster keys, field roles/timing, assignment/receipt
  rules, missingness handling and required external evidence.
- Design and identifying assumptions; provisional gates and when to stop.
- Estimator specification: local RD/window/bandwidth approach; DiD comparison
  groups/aggregation; IV instrument/endogenous variables; weighting/adjustment
  set and target; or time-series/donor/regime construction as relevant.
- Uncertainty/inference compatible with assignment/dependence, small-cluster or
  weak-instrument limitations, multiplicity and sensitivity/robustness plan.
- Implementation destination and verified official documentation. Data profiling
  defaults to Polars. Bayesian execution uses NumPyro/JAX when justified: either
  give `bayesian-workflow` the likelihood, candidate priors, pooling/temporal
  structure and model checks, or name `recommend-probabilistic-model` to choose
  them in its own `recommendation.md` beside this memo. A prior does not resolve
  identification by itself.
- Output specification: effects/uncertainty to report, diagnostic artifacts,
  claim limits, and distinction between local and target-population effects.

For `not identified`, the handoff is evidence collection, bounds or descriptive
work with its own assumptions, not an instruction to fit the unsupported effect.

## 8. Sources

List the primary papers/author texts supporting the chosen design and the
official implementation references. Link sources next to substantive claims
as well as here. Verify a newly added source before citing it. Use exact book
chapter/section numbers only when checked against the cited edition; author-year
plus an accurate topic is sufficient. Do not use a skill catalog as methodological
authority. Record source uncertainty rather than inventing a locator.

## 9. Open questions and next action

List material unknowns with **question**, **who/what can answer**, and
**effect on recommendation**. Ask for user-held facts where required; assign
data checks to the subsequent analysis. End with the next concrete action and
recommend a fresh session using this memo as the implementation input.
