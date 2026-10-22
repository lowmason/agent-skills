# model-lifecycle — Roadmap

> For agentic workers: REQUIRED SKILL: derive-roadmap — resume via its
> reconcile step; route each unticked stage per its ROUTING line; never plan
> this document wholesale.

**Source:** `specs/model-lifecycle.md` (approved 2026-10-21, merged to main as 94d1786).
**Partition approved** by the owner on 2026-10-21, in conversation.

The roadmap numbers stages 1–3 in landing order. The spec letters them A, B, C in audit
order. Stage 1 is spec Stage B, Stage 2 is spec Stage A, and Stage 3 is spec Stage C. This
order is the spec's own (D1). The dependency order gives the same result, because spec
Stage A consumes spec Stage B's reference and `scores.json`.

## Gap analysis

Evidence was read at 94d1786. `git diff 7612c6e HEAD -- skills README.md install.py build`
is empty, so the spec's line anchors still hold.

| Req | Verdict | Evidence | Note |
|---|---|---|---|
| R1 | implemented-differently | `skills/tune-hyperparameters/SKILL.md:3-11` | still has "nowcasting/tabular" and "dynamax optax SGD" |
| R2 | missing | tune `SKILL.md:35-55` | two regimes only |
| R3 | missing | tune `SKILL.md:65-100` | the temporal protocol only; no splitter table |
| R4 | missing | tune `SKILL.md:132-136` | prose only |
| R5 | missing | grep of tune `SKILL.md` | no early-stopping rule |
| R6 | missing | tune `SKILL.md:108-125` | the snippet uses MSE; no objective table |
| R7 | implemented-differently | tune `SKILL.md:140-141`; `build/test_runtime_support.py:500` | the rule compares spread with gap. The soft pair tune → track already exists (reason "a next step"), and the drift test keys on skill pairs, so Stage 2 rewrites the reason rather than adding an entry |
| R8 | missing | grep of tune `SKILL.md` | no neural section |
| R9 | implemented-differently | tune `SKILL.md:168`, `:171-172` | the row reads "no skill owns this yet" |
| R10 | missing | grep of tune `SKILL.md` | no producers table |
| R11 | implemented-differently | tune `SKILL.md:147-156` | sends a non-Bayesian winner to the Decision log |
| R12 | missing | tune `SKILL.md:174-183`; `skills/recommend-causal-design/SKILL.md` | no causal bullet; causal names no tune line |
| R12a | missing | `skills/recommend-probabilistic-model/references/model-selection-regularization.md:39-50` | no spline-knot or AR-order row |
| R12b | implemented-differently | `README.md:63` | describes two regimes |
| R13 | missing | `skills/track-model-experiments/` | no `scores.json` |
| R14 | missing | `skills/track-model-experiments/` | no `references/` dir |
| R15 | missing | track `SKILL.md` | no Criterion line |
| R16 | missing | `compare_experiments.py:10` | ranks by ELPD only |
| R17 | missing | `compare_experiments.py` | no score-mode refusals |
| R18 | implemented-as-specified | `test_compare_experiments.py` | must still hold after Stage 1 |
| R19 | missing | `skills/bayesian-workflow/references/model-comparison.md` | no LFO or K-fold section. The pin `arviz-stats==1.3.3` is met (`build/snippet_preamble.py:201`) |
| R20 | implemented-differently | track `SKILL.md:3-13` | Bayesian-only; churn-logistic example |
| R21 | implemented-differently | track `SKILL.md:46-50`; `compare_experiments.py:351-355`, `:409-412` | "until a non-ELPD mode exists" text |
| R22 | implemented-differently | `install.py:65` | track → bayesian-workflow is still a hard dependency |
| R23 | implemented-differently | `README.md:62` | omits the refusal of several log-likelihood variables |
| R24 | missing | `test_compare_experiments.py` | no score-mode tests |
| R25 | missing | `skills/develop-testing-strategy/SKILL.md` | no route to track or evaluate-deep-learning |
| R26 | missing | `skills/validate-data/SKILL.md` | no route |
| R27 | missing | `skills/recommend-visualization/SKILL.md` | no route |
| R28 | implemented-differently | `skills/recommend-probabilistic-model/references/reporting.md:54` | reads "sklearn/other" |
| R29 | missing | `build/test_runtime_support.py` | no pairs from the three skills to track |
| V1 | missing | `specs/verification/` | no tune or track record |
| V2 | missing | `specs/verification/` | no noise-rule record |
| V3 | gates exist | CLAUDE.md § Commands | each stage plan applies its gates |

No behaviour in code is outside the spec.

**Deferred items read** (`specs/deferred_items.md`, section
`59-model-skill-comparator-and-cv-fixes`):

- "Harden `compare_experiments.py` after plan 59's final review", parts (a)–(f): folded into
  Stage 1 by the owner (2026-10-21). It edits the same `_cells`, `update_ledger` and
  column-name lookup that R16 rewrites.
- "Two doc nits": part (a) closes in Stage 1 (R23). Part (b) closes across Stage 1 (R21) and
  Stage 2 (R11), so the item ticks in Stage 2.
- tune's "dynamax optax SGD" description item: ticks in Stage 2 (R1, R9).
- "Watch tune's Regime B router wording": Stage 2 edits that router table (R9), so its plan
  reads this item.
- "Three nits in the splitter's tests": left out. Its trigger is an edit to
  `time_series_cv.py`, and R3 adds no splitter code.

## Stages

- [x] Stage 1 (spec Stage B): track score mode and predictive evaluation
      Objective: track ranks score-criterion variants from `scores.json` beside the unchanged ELPD mode.
      Spec: § Stage B (R13–R24); § Verification V1 (track arm), V3 (Stage B); § Coordination (plan 64); deferred item "Harden `compare_experiments.py`" (a)–(f), section `59-model-skill-comparator-and-cv-fixes`
      Gap closed: R13–R24; V1 track; the comparator-hardening item; doc-nits part (a)
      Consumes: the arviz-stats 1.3.3 pin (met). Plan 64 is a rebase point for R19, not a gate
      Produces: the R13 `scores.json` contract; `skills/track-model-experiments/references/predictive-evaluation.md`; `--mode score`; the ledger Criterion line; the R22 soft-reference reasons
      Exit: the track suite passes with every existing test unedited, plus the R24 tests and a test for each hardening part (a)–(e); snippet Tiers 1–3 pass on `model-comparison.md`; the dependency-drift test, `check_conformance.py` and `build/run_commit_lints.sh` pass; the V1 track record is under `specs/verification/`; the hardening item and doc-nits part (a) are ticked, and the doc-nits item stays open for part (b)
      ROUTING: writing-plans
      > Stage 1: COMPLETE (2026-10-22) — implemented by plan 65 (specs/plans/completed/65-model-lifecycle.md). Its Handoff section names what Stage 2 and Stage 3 consume.
      > Next: resume the roadmap.

- [x] Stage 2 (spec Stage A): tune-hyperparameters as the model-agnostic search loop
      Objective: tune covers three regimes, any producer's knobs and graduation to a score-mode ledger.
      Spec: § Stage A (R1–R12b); § Verification V1 (tune arm), V2, V3 (Stage A); R7's soft reference per the R7 row above
      Gap closed: R1–R12b; V1 tune; V2; the optax-description item; doc-nits part (b)
      Consumes: Stage 1's `predictive-evaluation.md` path (R7) and `scores.json` contract (R11)
      Produces: tune's new description and body; rpm's knob rows; causal's sibling line
      Exit: `check_frontmatter.py`, snippet Tier 1, the tune suite with `test_time_series_cv.py` unchanged, `verify_citations.py` Gate A, the dependency-drift test and `build/run_commit_lints.sh` pass; the V1 tune and V2 records are under `specs/verification/`; the optax and doc-nits items are ticked
      ROUTING: writing-plans
      > Stage 2: COMPLETE (2026-10-22) — implemented by plan 67 (specs/plans/completed/67-model-lifecycle.md). Its Handoff section names what Stage 3 consumes.
      > Next: resume the roadmap.

- [ ] Stage 3 (spec Stage C): thin routes and rpm's "Runs next"
      Objective: three skills route model evaluation to its owners, and rpm names tune then track.
      Spec: § Stage C (R25–R29); § Verification V3 (Stage C); § Coordination (plans 63, 64)
      Gap closed: R25–R29
      Consumes: Stage 1's `predictive-evaluation.md` path; plan 63 merged to main (hard gate)
      Produces: none for later stages
      Exit: the dependency-drift test passes with the R29 soft pairs; `build/run_commit_lints.sh` passes; no description in the three skills changed (`git diff` of their frontmatter is empty)
      ROUTING: writing-plans

## Stage-spec stamp

No stage has its own stage spec. Each stage plan's header carries:

> Roadmap: specs/model-lifecycle-roadmap.md, Stage N — on plan completion, tick the
> stage and re-validate later stages against what shipped.

## Completion

When every stage is ticked, re-run the gap rubric over R1–R29 and V1–V3 against the
accumulated system, with evidence for each verdict. Confirm that the spec's § Done when items
are ticked: the optax-description and plan-59 doc-nits items tick in Stage 2, and the
lifecycle-spec item was ticked when the spec was approved (2026-10-21). An unmet
requirement becomes a new stage or a written deferral. Then retire this roadmap and the spec
to `specs/completed/`.
