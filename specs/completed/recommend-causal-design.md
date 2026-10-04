# Recommend Causal Design

**Status: COMPLETE (2026-10-03)** — implemented by plan 33; nothing deferred.

Approved scope: the user approved the recommendation in this chat on 2026-10-03.

## Purpose and boundary

Add `recommend-causal-design`, a recommendation-only counterpart to
`recommend-probabilistic-model`. Given a causal question and optional data, it
produces `<analysis-slug>/recommendation.md` for another analyst to start cold.
It selects a defensible research design before estimator or likelihood choice.
It does not estimate effects, fit models, run refutations, or certify causation.

## Decision procedure

Define the requested estimand (intervention/comparator, outcome, population,
horizon, effect scale, and ATE/ATT/ITT/local effect); inventory assignment,
timing, clustering, missingness, and available evidence; construct an explicit
causal diagram with confounders, mediators, colliders, and unobserved variables;
establish identification; compare two or three credible designs; recommend a
conditional default; specify required diagnostics and sensitivity analyses;
write the memo and implementation handoff.

Use three statuses for the requested estimand: `plausibly identified`,
`conditional`, and `not identified`. These are design assessments under
explicit assumptions, never empirical proof. Keep the requested estimand
separate from any local or alternative estimand the available design supports.
When identification fails, document a descriptive/bounds option and a feasible
evidence-collection plan. Do not silently replace the requested effect.

## Coverage

Experiments; adjustment, matching, weighting and doubly robust estimation;
instrumental variables; sharp/fuzzy regression discontinuity;
difference-in-differences/event studies with staggered adoption; synthetic
control; interrupted time series; longitudinal treatments/time-varying
confounding. Heterogeneous effects are a secondary estimand/estimation layer.
Mediation, causal discovery, transportability and interference receive scoped
specialist routes, not automatic recipes.

## Packaging and stack

- Markdown-only skill: short `SKILL.md`, focused `references/`, and `README.md`.
- No estimator scripts, bundled papers/books, numerical grading thresholds,
  PyMC dependency, or generated runtime-adapter changes.
- Method recommendations are software-independent. Data profiling hands off
  to `explore-data`; a specified Bayesian estimation model hands off to
  `bayesian-workflow` using NumPyro/JAX. Polars is the profiling default.
- Cross-skill handoffs use bare names; the skill is self-contained and reads
  no sibling files. Installer dependency tables need no new edge.
- Adapt only the planning workflow from Robson Tigre's `causal-planner` and
  Alexandre Andorra's `causal-inference`; retain both MIT license notices and
  pin upstream commits. Method prose, routing and report template are newly
  written and scholarly sources are cited, never reproduced.

## Memo contract

Required fields: requested question and estimand; design status and rationale;
data/assignment inventory with known/assumed/unknown facts; causal diagram and
adjustment rationale; identification assumptions/evidence/gaps; candidate
comparison and estimand compatibility; primary design or non-identification
decision; diagnostic/falsification/sensitivity plan; executable handoff
specification (without implementing it); verified references and unresolved
questions. Include a worked recommendation illustrating an estimand mismatch.

## Validation and completion

Run fresh no-guidance application samples before writing the skill. Record
observed omissions, use required template slots for output-shape failures,
then run five fresh guidance samples of the same focal scenario. Test missing
overlap, staggered adoption, and time-varying confounding as additional
application cases. Review all outputs manually; report measured limitations.
Run repository frontmatter/provenance/snippet lints and the frontmatter,
provenance, and runtime-support tests. Independently review method claims,
license attribution, memo usability and installation portability. Register
README/CLAUDE/NOTICE attribution and verify single-skill installation. Complete
and retire this spec and its plan after required checks and review pass.
