# model-lifecycle — Design Spec

**Status: COMPLETE (2026-10-23)** — implemented by plans 65, 67 and 68 (`specs/plans/completed/`)
through the roadmap `specs/completed/model-lifecycle-roadmap.md`, and retired here. R3 was
amended at the completion review (owner, 2026-10-23).

> For agentic workers: REQUIRED NEXT SKILL: derive-roadmap — do not plan
> this spec directly and do not split it into per-subsystem plans.

**Status:** approved by the owner on 2026-10-21: the design section by section in a
brainstorming session, then the written spec. Next step: run
derive-roadmap against this file in a fresh session. It stages the work into the three
stages in § Staging, and each stage then gets its own writing-plans cycle.

**Source.** The open deferred item "Write the model-lifecycle spec: re-scope
tune-hyperparameters as the model-agnostic search loop and draw its boundaries"
(`specs/deferred_items.md`, section `audit-3-10-26 routing`). It covers audit-3-10-26 G5–G9
and the criterion half of G3 (`specs/completed/audit-3-10-26.md`, § G-B and Appendix B). It
also takes two open items from section `59-model-skill-comparator-and-cv-fixes`:

- tune-hyperparameters' frontmatter `description` still triggers on "dynamax optax SGD".
- Part (b) of "Two doc nits left by plan 59's final review".

**Settled owner calls (2026-10-21, in conversation; recorded in `specs/deferred_items.md`):**

- **O1 (ii).** `track-model-experiments` covers Bayesian variants plus a tabular-CV mode. It
  ranks variants by fold scores in the same ledger. Neural records stay with
  `evaluate-deep-learning`. JAX spec R7 holds for track
  (`specs/completed/jax-deep-learning-skills.md:162-167`, `:187-200`).
- **O2 (b).** A predictive-evaluation reference, owned by `track-model-experiments`, covers
  the backtest protocol, the paired per-fold difference against its SE, and benchmark
  comparison. `tune-hyperparameters` keeps the search loop.
- **O3.** R7 stands. `develop-testing-strategy`, `validate-data` and
  `recommend-visualization` get thin routing lines to the owning skills. Their scope does not
  widen.

**Design decisions (owner, this brainstorming session, 2026-10-21):**

- **D1.** One spec, staged by derive-roadmap into three stages (A, B, C below), which land in the order B, A, C.
- **D2.** The comparator ranks non-ELPD variants from one keyed per-unit score file
  (`scores.json`). One mechanism serves tabular-CV folds and Bayesian leave-future-out (LFO)
  origins. The PSIS-LOO path does not change.
- **D3.** One criterion per ledger. `experiments.md` declares its criterion, and the
  comparator refuses a run that does not match it. A Bayesian variant joins a score ledger by
  writing its own `scores.json`.
- **D4.** tune-hyperparameters owns the optax learning-rate knob for non-neural point fits.
  The description drops "dynamax optax SGD".

## Terms

- **ELPD**: expected log pointwise predictive density, the score that PSIS-LOO estimates.
- **PSIS-LOO**: Pareto-smoothed importance-sampling leave-one-out cross-validation.
- **LFO**: leave-future-out cross-validation, which scores each forecast origin only on data
  after it.
- **Unit**: one fold of a CV run, or one forecast origin of a backtest.
- **Paired Δ**: the mean over units of the per-unit score difference between two variants.
  `SE(Δ) = sd(d) / √K`, where `d` is the vector of per-unit differences and `K` is the number
  of units.
- **Score mode**: the new comparator mode that ranks from `scores.json`. **ELPD mode** is
  today's mode.
- **rpm**: `recommend-probabilistic-model`.

## Staging

The stages land in the order B, A, C. The letters follow the skill order of the audit, not
the landing order.

| Order | Stage | Covers | Description micro-test | Lands after |
|---|---|---|---|---|
| 1 | B | R13–R24: score mode, predictive-evaluation reference, G3 time-series section, track's scope (G8), install dependencies, track's README row | track | — |
| 2 | A | R1–R12b: tune's re-scope (G5, G6, G7, D4), rpm knob rows, causal sibling line, tune's README row | tune | B: R7 points to B's reference, and R11 sends winners to B's `scores.json` |
| 3 | C | R25–R29: G9 thin routes, rpm "Runs next" | none (body text only) | B, and plan 63 |

## Stage A — tune-hyperparameters as the model-agnostic search loop

**R1 — Description.** Rewrite tune's frontmatter `description`
(`skills/tune-hyperparameters/SKILL.md:3-11`). It starts with "Use when…", stays in the third
person, and has at most 1,024 characters. It must do these things:

- Trigger on tuning any model's knobs.
- Name the producers: sklearn and boosting, statsmodels, NumPyro and dynamax, and neural nets
  from deep-learning.
- Keep the temporal, rolling-origin, purged and embargoed CV triggers as one branch.
- Add triggers for structural choices (number of mixture components, factors or HMM states,
  AR order, spline knots, kernel form).
- Add triggers for early stopping, pruning and trial budget.
- Keep "when NOT to tune", graduation, and the revision-leakage pointer to
  develop-testing-strategy.
- Drop "for a nowcasting/tabular model" and "dynamax optax SGD" (D4).

**R2 — Regime C.** Step 0 (`:35-55`) gains a third regime for structural choices: mixture
K, factor count, HMM states, kernel form, spline knots and AR order.

- Criteria: type-II marginal likelihood, BIC or AIC, LOO or LFO over a discrete index, and
  rolling-CV log score.
- Division of labour: tune runs the sweep. When the candidate set is small and each candidate
  carries a hypothesis, track records the candidates as ledger rows.
- One sentence states that GP hyperparameters fit by type-II marginal likelihood are set
  inside the fit. Regime C covers the choice of kernel form.
- The Step 0 rule sentence (`:37-40`) is restated so that each knob falls in exactly one of
  the three regimes.

**R3 — Step 0b, splitter by dependence structure.** Add a table before the Regime A CV
protocol:

| Data | Splitter |
|---|---|
| i.i.d. | `KFold`, or `StratifiedKFold` for classes |
| Grouped, or predicting new entities | `GroupKFold` or `LeaveOneGroupOut` |
| Spatial | `GroupKFold` over spatial blocks |
| Temporal | the bundled `PurgedTimeSeriesSplit` (existing text, `:65-100`) |
| Random forests, independent rows only | out-of-bag error |

No new splitter code.

**R4 — Nested CV snippet.** Replace the nested-CV prose (`:132-136`) with a short runnable
snippet. An outer forward-chaining split runs the whole Optuna study on each training half
and scores the winner on the outer validation fold. It passes snippet Tier 1.

**R5 — Early-stopping rule.** One rule in Regime A: early stopping takes its stopping split
from inside the training fold, never from the CV validation fold.

**R6 — Objective table.** A table keyed by what the model emits:

| Model emits | Objective |
|---|---|
| Point predictions | MSE or MAE, or a loss that matches the decision |
| Predictive distributions | log score or CRPS (strictly proper) |
| Class probabilities | log-loss or Brier, never accuracy alone |
| Forecasts | per-origin loss differences |

**R7 — Paired noise rule.** Replace "Fold-to-fold variance swamps the effect" (`:140-141`).
The new rule: compute the paired per-fold Δ between candidates. When |Δ| is under 2·SE(Δ), the
difference is noise, and the default ships. The rule uses the plain `SE(Δ) = sd(d) / √K`
from § Terms. It is a screening rule. R14's corrections (overlapping training sets, a HAC SE
for h-step forecasts) make it more conservative, and they apply only to high-stakes calls.
Tune states the rule in one sentence. It points to track's
`references/predictive-evaluation.md` (R14) for the protocol and the SE's limits. That
pointer is a soft reference in `SOFT_REFERENCES`, with the reason "tune states the rule
itself". This stage adds the entry, so the dependency-drift test passes on its first commit.

**R8 — Neural search (G6).** A short section on the generic loop that deep-learning and
evaluate-deep-learning already hand to tune (`skills/deep-learning/SKILL.md:144-145`,
`skills/evaluate-deep-learning/SKILL.md:85-86`, its `references/protocol.md:15-17`). It
covers:

- the trial budget
- Optuna pruners (median or successive halving)
- early stopping inside the training fold (R5)
- replicating the finalists over seeds before choosing

Boundary: deep-learning owns schedule and state mechanics. evaluate-deep-learning owns
comparable-budget rules and the experiment record. A neural learning rate stays Regime A.

**R9 — Regime B optax row (D4).** The optax row (`:168`) names this skill as its owner and
covers optax-fit point estimates such as dynamax MLE. Its stopping rule: the training loss
plateaus, and restarts from several initializations reach the same optimum within a stated
tolerance. The sentence "The optax row has no owner" (`:171-172`) is removed.

**R10 — Producers router.** A table that names each producing skill with the regime and the
objective it uses. Rows: rpm, bayesian-workflow, deep-learning, evaluate-deep-learning and
recommend-causal-design (nuisance learners only, R12).

**R11 — Graduation (plan-59 nit (b)).** Rewrite Graduation (`:147-156`). A tuned winner that
becomes a contender graduates to a track ledger row. It writes `scores.json` (R13) on the
ledger's criterion. The text "until a non-ELPD mode exists… goes in the ledger's Decision
log" is removed. The `what changed` example and the next sentence then agree.

An existing `elpd-loo` ledger cannot rank a non-Bayesian winner (D3). To compare it with the
Bayesian variants, re-declare the ledger's criterion as a score criterion. Each Bayesian
variant then writes `scores.json` on the same units, for example a per-fold log score or the
MSE of the posterior-predictive mean. Until that is done, the comparator names the new row as
not compared. It never drops the row in silence.

**R12 — Causal boundary (G7).** tune's Boundary (`:174-183`) gains one bullet. Predictive CV
is the right objective for nuisance learners (propensity and outcome models) tuned inside
cross-fitting folds. It never selects the design, the adjustment set, an RD bandwidth,
synthetic-control weights or the effect estimate. `skills/recommend-causal-design/SKILL.md`
Scope and siblings (`:33-46`) gains a sibling line: use tune-hyperparameters only for
nuisance-learner tuning inside cross-fitting. These are bare-name handoffs.

**R12a — rpm knob rows.** Add spline-knot and AR-order rows to rpm's per-family knob table
(`skills/recommend-probabilistic-model/references/model-selection-regularization.md:39-50`).
A row cites only a PML section that `build/verify_citations.py` Gate A resolves, or it gives
no § reference. No book prose.

**R12b — tune's README row.** The root `README.md` row for `tune-hyperparameters` (`:63`)
describes the new scope: three regimes, the splitter table, the neural search loop, and
graduation to a score-mode ledger.

## Stage B — track-model-experiments: score mode and predictive evaluation

**R13 — The `scores.json` contract.** In score mode, each variant folder holds `scores.json`:

```json
{"criterion": "cv-mse", "orientation": "lower", "units": {"fold-1": 0.42, "fold-2": 0.39}}
```

- `criterion`: a free string that names the score and the protocol, for example `cv-mse`,
  `cv-logloss` or `lfo-elpd`.
- `orientation`: `higher` or `lower` is better.
- `units`: a map from a fold id or forecast origin to one finite number.

**R14 — Predictive-evaluation reference.** New file
`skills/track-model-experiments/references/predictive-evaluation.md`. It covers:

- **Backtest protocol.** Rolling origin, a refit at each origin, and a stated forecast
  horizon. As-of features are left to develop-testing-strategy (a bare-name handoff).
- **The R13 contract**, and how to write `scores.json` from a CV loop or from a Bayesian LFO
  run.
- **The paired Δ and its limits.** Rolling-origin training sets overlap, so SE(Δ) is
  optimistic. Few units give a rough SE. For h-step forecasts the per-origin differences are
  autocorrelated, which calls for a Diebold–Mariano test with a HAC (autocorrelation-robust)
  SE.
- **Benchmark comparison.** A naive or seasonal-naive baseline in every backtest ledger, and
  a skill score relative to that baseline.
- **Proper scoring.** The log score and CRPS for predictive distributions.

Sources (Gneiting & Raftery 2007; Diebold & Mariano 1995; Bengio & Grandvalet 2004) are cited
by idea only, with no prose copied.

**R15 — Ledger criterion line (D3).** `experiments.md` carries one `Criterion: <name>` line
above the Variants table. A ledger without that line reads as `elpd-loo`, so existing ledgers
and tests keep working. A score ledger's Variants table has the metric columns `score`,
`Δscore` and `SE(Δ)` in place of the ELPD columns.

**R16 — Comparator score mode.** `skills/track-model-experiments/scripts/compare_experiments.py`
gains `--mode {elpd,score}`. The default is `elpd`.

- With `--ledger`, a mode that does not match the ledger's criterion is refused.
- Score mode discovers `*/scores.json` under `--analysis-dir`, or reads `--folders`.
- It ranks by mean score, with the orientation applied.
- For each variant it reports the paired Δ against the top variant and SE(Δ).
- It fills `score`, `Δscore` and `SE(Δ)` by column name and moves the best marker.
- `not_compared` and the qualified best marker work as they do today.
- `comparison.json` gains `mode` and `criterion` keys.

**R17 — Score-mode refusals.** Each one exits through the script's `error:` path with a
message that names the variant and the fix:

- a variant folder with no `scores.json`
- a `criterion` that differs from the ledger's, or from another variant's
- an `orientation` that differs across variants
- unit key sets that differ across variants
- a non-finite value
- fewer than two units

**R18 — ELPD mode unchanged.** ELPD mode keeps its behaviour, refusals and output. Every
existing test in `test_compare_experiments.py` passes without edits.

**R19 — G3 time-series section.** `skills/bayesian-workflow/references/model-comparison.md`
gains a section and a Contents entry:

- PSIS-LOO is right for interpolation and structure questions.
- Forecast decisions rank by LFO or by blocked K-fold with a joint log score.
- A snippet for each route uses arviz-stats. The plan checks `lfo_cv` and `loo_kfold`
  against the pinned arviz-stats 1.3.3 (`build/snippet_preamble.py`, `PINNED`) before it
  writes them. Snippet Tiers 1–3 pass.
- To rank such variants in track, write the per-origin pointwise ELPD into `scores.json`
  (R13), with `orientation: higher`.

The section is original text. It cites the loo LFO vignette and the CV-FAQ by URL.

**R20 — track's description (G8).** Rewrite track's `description`
(`skills/track-model-experiments/SKILL.md:3-13`). Third person, at most 1,024 characters.

- Scope: Bayesian variants ranked by ELPD, plus tabular-CV and backtest variants ranked on a
  shared criterion.
- Keep the ledger, ELPD/LOO, "which model fits best" and stopping triggers.
- Add triggers for ranking variants by CV or backtest scores, LFO, and a benchmark baseline.
- Drop "NumPyro/ArviZ" as the only producers and the churn-logistic example.
- Keep "Not for neural runs or checkpoints (evaluate-deep-learning)". Keep "Not for tuning
  continuous hyperparameters (tune-hyperparameters)".

**R21 — track's body.**

- Overview and the comparator section describe both modes.
- The ledger section shows the Criterion line and both column sets.
- When to use (`:46-50`), plan-59 nit (b): a non-Bayesian winner gets a variant row with
  `scores.json`, not a Decision-log entry. In an existing `elpd-loo` ledger, the ledger first
  re-declares its criterion, with the same rule as R11.
- Stopping rule: score mode ships the simpler variant when the paired |Δ| is under 2·SE(Δ).
- Relationship section names `references/predictive-evaluation.md`.
- The comparator's docstring and its `error:` and `note:` texts that say "until a non-ELPD
  mode exists" (`compare_experiments.py:10-16`, `:351-355`, `:409-412`) are rewritten to name
  score mode.

**R22 — Install dependencies.** Each path is classified, and
`build/test_runtime_support.py`'s dependency-drift test passes:

- `skill:track-model-experiments` → `skill:bayesian-workflow` (`install.py:65`) moves from
  `DEPENDENCIES` to `SOFT_REFERENCES`. Reason: ELPD mode reads its doctrine, and score mode
  works without it.
- bayesian-workflow → track's reference or score mode (R19) is soft. Reason: it names where
  the score is ranked.

If the drift test classifies a path otherwise, the plan follows the test and records why.

tune's soft reference to track's reference lands with Stage A (R7).

**R23 — track's README row.** The root `README.md` row for `track-model-experiments` (`:62`)
describes the new scope. tune's row changes in Stage A (R12b). The track row also names the
refusal
of several log-likelihood variables, which closes part (a) of the plan-59 doc-nits item.

**R24 — Tests.** New tests in `test_compare_experiments.py` for score mode:

- ranking with each orientation
- Δ and SE(Δ) against a hand-computed fixture
- each R17 refusal
- a ledger criterion line that does not match `--mode`
- score-cell fill, the best marker and `not_compared`

They use no NetCDF fixtures.

## Stage C — thin routes and rpm's "Runs next"

Body text only. No description changes. This keeps Stage C off plan 63's lines and needs no
micro-test.

**R25 — develop-testing-strategy.** One routing line in the body, near Step 4
(`skills/develop-testing-strategy/SKILL.md:140`). Model packages that are not Bayesian apply
Step 1's invariant groups. Their evaluation protocol belongs to track's
`predictive-evaluation.md`, or to evaluate-deep-learning for neural models. The description
(`:3-…`) and the "three code kinds" framing (`:32-35`) do not change.

**R26 — validate-data.** One routing line in Analysis QA. The producer checks a model result's
evaluation: bayesian-workflow, track's predictive-evaluation reference or
evaluate-deep-learning. The report records which producer checked it. The report template
(`skills/validate-data/SKILL.md:297-300`) gets no new section.

**R27 — recommend-visualization.** One routing line in the body. Model-output charts
(intervals, CV metrics, calibration curves) go to bayesian-workflow for posterior draws, to
track's reference for CV and backtests, and to evaluate-deep-learning for neural runs.
`VALID_INTENTS` (`scripts/recommend.py:56`) does not change.

**R28 — rpm "Runs next".** `skills/recommend-probabilistic-model/references/reporting.md:54`
changes "sklearn/other" to "tune-hyperparameters, then track-model-experiments (score mode)".

**R29 — Path references.** A Stage C line that names track's reference file is a soft
reference with a reason in `SOFT_REFERENCES`. Other routes use bare skill names.

## Verification

**V1 — Description micro-tests (planned here, not run).** Follow writing-skills' Iron Law for
the two changed descriptions (R1, R20).

- **Isolation.** Decision-only `claude -p --tools "" --strict-mcp-config` with
  `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, run from a fresh `/tmp` subdirectory. Pilot the init
  record's `tools` list first.
- **Arms.** The control arm uses the current description. The variant arm uses the draft.
  Each prompt runs 5 reps per arm. The system prompt is a skill listing with the target and
  its probes, by name and description, taken from the files at plan time.
- **tune prompts.** Three triggers: a grouped-CV search, a mixture-K sweep and a neural
  early-stopping budget. Near-misses for each probe. Probes: creative-thinking, rpm,
  deep-learning, evaluate-deep-learning and track-model-experiments.
- **track prompts.** Three triggers: a CV-ranked tabular ledger, a Bayesian LFO ranking and
  ELPD variants. Near-misses for each probe. Probes: bayesian-workflow, evaluate-deep-learning,
  tune-hyperparameters and rpm.
- **Pass rule.** No prompt's share drops by more than one rep against the control, and no
  near-miss newly routes to the target. Read every answer by hand. A failed description is
  reworded and re-run. It does not ship on a failed run.

**V2 — Noise-rule probe (Stage A).** The audit's fixture: all 5 paired fold differences share
a sign, and mean/SE is 2.8. An agent that loads the new tune text must call the difference
real. That verdict follows from R7's pinned rule, because 2.8 is above the threshold of 2. The
control (today's `:140-141`) is expected to call it noise. Same isolation as V1.

**V3 — Gates for each stage.**

- **Stage A:** `check_frontmatter.py`, snippet Tier 1, the tune suite (existing
  `test_time_series_cv.py` unchanged), `verify_citations.py` Gate A for R12a, the
  dependency-drift test (R7's soft reference), and `build/run_commit_lints.sh`.
- **Stage B:** the track suite (R18, R24), snippet Tiers 1–3 on `model-comparison.md`, the
  dependency-drift test, `check_conformance.py` and the commit lints.
- **Stage C:** the dependency-drift test and the commit lints.

## Coordination

- **Plan 63** (`specs/plans/63-conformance-gaps.md`, branch
  `claude/plan-35-conformance-gaps-427f5e`) rewrites the descriptions of validate-data,
  recommend-visualization and explore-data. Stage C changes only the bodies of validate-data
  and recommend-visualization, and it lands after plan 63 merges.
- **Plan 64** (bayesian-workflow and rpm routing, drafting on branch
  `claude/plan-bw-rpm-routing-2dd1a6`) edits rpm's sibling list and memo template
  (`references/reporting.md:36-40`), and adds a siblings block to bayesian-workflow's
  `SKILL.md`. R19 and R28 touch neighbouring files and lines. The plan that lands second
  rebases onto the other and re-reads the anchors.
- Anchors in this spec are at commit `7612c6e`. Each stage's plan restates them.

## Provenance and public-repo rules

- tune-hyperparameters, track-model-experiments, rpm, develop-testing-strategy, validate-data
  and recommend-visualization are the owner's originals (`NOTICE`). No NOTICE change.
- recommend-causal-design adapts MIT sources. R12's sibling line is newly written. No NOTICE
  change.
- bayesian-workflow is adapted from Alexandre Andorra's skill (`LICENSE-andorra`). R19 is new
  original text that cites its sources by URL. The plan checks whether NOTICE lists changes
  for this skill, and adds a line if it does.
- rpm's R12a rows cite PML by § number only and pass Gate A.
- `specs/` is public. Examples use generic nowcast and panel names, with no private-repo
  detail.

## Non-goals

- A shared ledger spine with evaluate-deep-learning (O1 (i), declined).
- New `VALID_INTENTS` or new chart-selection sections in recommend-visualization.
- rpm's model-agnostic §6 handoff payload.
- Description changes to develop-testing-strategy, validate-data or recommend-visualization.
- Ranking ELPD and score variants together in one run (D3).

## Done when

Each of R1–R29 is implemented as specified, V1 and V2 are recorded under `specs/verification/`,
and the V3 gates pass for each stage. The deferred items below are then ticked:

- the lifecycle-spec item
- the optax-description item
- part (b) of the plan-59 doc-nits item (and part (a), through R23)
