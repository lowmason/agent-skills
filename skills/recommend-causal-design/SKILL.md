---
name: recommend-causal-design
description: >
  Use when choosing a research design for a causal question before estimation:
  policy impact, treatment effects, ATE/ATT/ITT/LATE, confounding, identification,
  DAGs, experiments, difference-in-differences, instrumental variables,
  regression discontinuity, synthetic control, matching/weighting, interrupted
  time series, or time-varying treatments. Trigger on "did X cause Y", "which
  causal method", or "can these data identify this effect".
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
  sources: >
    Planning workflow selectively adapted from Robson Tigre's causal-planner
    and Alexandre Andorra's causal-inference (MIT). Method guidance and memo
    template are newly written; scholarly sources are cited, not reproduced.
---

# Recommend a Causal Design

Given a causal question and optional data, write
`<analysis-slug>/causal-design.md`: a defensible research design, its identifying
assumptions, alternatives, and a specification another analyst can implement.
**Identification precedes estimator choice.** A flexible model, Bayesian prior,
large sample, or successful diagnostic cannot create identifying variation.

This skill recommends and specifies. Estimation, model fitting, numerical
diagnostics, and causal-effect reporting belong to the subsequent analysis.
Data inspection may establish feasibility; label diagnostic plans as planned,
not as passed.

## Scope and siblings

- Use `explore-data` when data need profiling; metadata alone can support a
  provisional design memo. Data distributions do not establish assignment.
- Use `recommend-probabilistic-model` for likelihood/model choice after the
  causal design and estimand are settled, or for a predictive question. It
  writes `<analysis-slug>/recommendation.md` beside this memo, and chooses the
  likelihood unless this memo already fixes one.
- Hand a fully specified Bayesian estimation model to `bayesian-workflow`
  (NumPyro/JAX). That handoff must include identification assumptions as well
  as likelihood, priors, and structure: pass this memo, plus
  `recommendation.md` when `recommend-probabilistic-model` chose the model.
- Use `develop-testing-strategy` for downstream computational/model tests;
  use `validate-data` for data/result QA.

The common path is intervention-effect evaluation. Causal discovery, mediation,
transportability, and interference may require specialist designs; acknowledge
their additional assumptions instead of forcing them into ordinary adjustment.

## Procedure

1. **Define the requested estimand.** State the intervention and comparator,
   outcome and scale, target population, time zero/follow-up horizon, and effect
   summary (ATE, ATT, ITT, complier/local effect, or treatment regime contrast).
   Separate the effect of offering/eligibility from actually receiving treatment.
   If key facts are user-held, ask a compact batch of questions. Proceed with
   clearly labeled assumptions where possible; unresolved facts belong in the
   memo. Confirm material reinterpretations of the question before treating
   them as the requested target.
2. **Inventory the design and data.** Record how and when treatment was assigned,
   what was measured before/after it, sampling/selection, missing outcomes,
   noncompliance, treatment reversals, clusters, spillovers, and concurrent
   events. Classify statements as **known**, **assumed**, or **unknown**. If
   data are available, profile units, periods, support, and measurement quality;
   sample shape determines feasibility, not identification.
3. **Make the causal structure explicit.** Draw a small DAG in Mermaid or an
   edge list with timing and variable definitions. Include plausible unobserved
   confounding, selection/response, and pathways excluded by the design. Name
   the proposed adjustment set and justify inclusions/exclusions. Where feedback
   occurs over time, use time-indexed nodes. Mark disputed edges and how a
   changed graph changes the recommendation. Consult
   [identification.md](references/identification.md).
4. **Assess identification for the requested target.** Use one of:
   **plausibly identified** (a design can identify this estimand under defended
   assumptions), **conditional** (specific material facts/evidence remain
   unresolved), or **not identified** (available variation/support cannot
   identify it). These are pre-estimation design judgments, not causal proof.
   Pair each identifying assumption with supporting evidence, planned
   challenges, and what remains untestable. A local effect is a separate target;
   it does not silently replace a population ATE.
5. **Compare 2–3 credible candidates.** Read
   [design-map.md](references/design-map.md) and select by assignment and
   assumptions, not by outcome type or library convenience. For each candidate
   state the estimand it can identify, assumptions, data requirements, principal
   threat, and feasibility. When only one design is credible, say so; compare it
   with a bounds/descriptive or new-data option rather than inventing a second
   identifying strategy.
6. **Recommend a primary design and a fallback.** Explain why it answers the
   question, the condition that would change the choice, and its weakest
   assumption. For `conditional`, specify what evidence is needed to proceed.
   For `not identified`, write a useful memo: descriptive/bounds analysis where
   justified, a separately labeled alternative estimand if useful, and a feasible
   identification/data-collection plan. Do not upgrade missing support to
   identification through DML, doubly robust estimation, or stronger priors.
7. **Specify verification and estimation, without doing them.** Plan design
   diagnostics, falsification/negative controls, sensitivity analyses, missingness
   handling, inference at the assignment level, and failure actions. Separate
   testable implications from untestable assumptions. Passing placebo, balance,
   density or pretrend checks is supporting evidence, not certification.
8. **Persist and hand off.** Use the complete contract in
   [reporting.md](references/reporting.md); every field receives content or
   an explicit `unknown/not applicable` with a reason. Include verified primary
   sources from [sources.md](references/sources.md) next to the relevant claims.
   End with the exact target, sample, variable roles, design/estimator
   specification, inference, diagnostic/sensitivity plan, and unresolved gates.
   Recommend a fresh implementation session against the memo.

## Quick reference

| Observable design fact | First design to assess | Key gate |
|---|---|---|
| Random assignment | Experiment/ITT | Randomization, outcome observation, interference |
| Plausible sufficient pretreatment covariates | Adjustment/weighting | Exchangeability and overlap for target population |
| Exogenous encouragement/instrument | IV | Exclusion, independence, relevance; local target |
| Treatment changes at a score threshold | Sharp/fuzzy RDD | Continuity or defended local randomization; local target |
| Treated/comparison units before and after adoption | DiD/event study | Parallel untreated trends, timing and comparison eligibility |
| Treated unit(s) with credible untreated donor histories | Synthetic control | Uncontaminated donors, support, counterfactual fit assumptions |
| Intervention in an observed time series | Interrupted time series | Credible untreated trajectory, concurrent events |
| Treatment/confounders evolve and affect each other | Longitudinal g-method design | Sequential exchangeability and history-specific positivity |

These are candidates, not automatic routes. Several may fail or identify
different populations. Heterogeneous effects/DML describe an estimation layer
conditional on a valid design; they do not form a shortcut around this table.

## Common mistakes

- **National ATE requested, local effect available:** keep both targets visible;
  state that transport/extrapolation needs additional evidence and assumptions.
- **A variable predicts the outcome, so adjust for it:** use causal role and
  measurement timing; avoid total-effect adjustment for mediators/colliders.
- **Rich panel or many observations, so DiD is credible:** document assignment,
  untreated comparison trends, concurrent shocks, and composition.
- **A nonsignificant diagnostic proves an assumption:** explain what the test
  can challenge and what it cannot establish; record power/design limitations.
- **Missing outcomes or post-treatment participation disappear in cleaning:**
  keep selection in the causal structure and specify the missingness assumptions.
- **Prediction quality chooses the causal design:** choose identification first;
  nuisance-model selection and effect inference are downstream specifications.

## References and attribution

The main procedure is self-contained; the linked references live inside this
skill. No estimator runtime or sibling-file dependency is required. See
[worked-example.md](references/worked-example.md) for a cutoff-policy memo.

Workflow adaptation sources, pinned commits, and primary literature are in
[sources.md](references/sources.md). Upstream MIT notices are bundled in
[LICENSE](LICENSE), and recorded in the repository's
`LICENSE-causal-design-sources` and `NOTICE`. No upstream code,
automated causal grading, book prose, figures, or document copies are bundled.
