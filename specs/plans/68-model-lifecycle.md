# Model-lifecycle Stage 3: thin routes and rpm's "Runs next" — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

> Roadmap: specs/model-lifecycle-roadmap.md, Stage 3 — on plan completion, tick the stage and re-validate later stages against what shipped.

**Goal:** develop-testing-strategy, validate-data and recommend-visualization each route model evaluation to the skill that owns it, and rpm's memo template names tune-hyperparameters, then track-model-experiments, as the non-Bayesian next step.

**Architecture:** Body text only, plus three entries in a build test. Each of the three skills gets one routing line that names `track-model-experiments/references/predictive-evaluation.md` by its full path and names `bayesian-workflow` and `evaluate-deep-learning` by bare name. The full path makes the dependency-drift scanner record one new edge per skill, and each edge is declared soft in `SOFT_REFERENCES` (R29). rpm's `references/reporting.md` changes one option in its "Runs next" line (R28). No `description` changes, so no micro-test.

**Tech Stack:** Markdown; Python 3.13 via `uv` for the drift test and the commit lints.

**Spec:** `specs/model-lifecycle.md` — § Stage C (R25–R29), § Verification V3 (Stage C), § Coordination (plans 63 and 64).

**Base commit:** `c35dbfb` (origin/main when this plan was written; it contains plan 67's merge `9e71e54`). The spec's anchors are at `7612c6e`. From there to `c35dbfb`, `skills/develop-testing-strategy/` is unchanged. `skills/validate-data/SKILL.md` and `skills/recommend-visualization/SKILL.md` changed only in their `description` (plan 63). `references/reporting.md` gained only the `Iterate` line at :56 (plan 64). Every anchor this plan uses still holds at `c35dbfb`.

**Plan-time replay.** Every Old block below was applied in order to a copy of `c35dbfb` and matched exactly once. On the result, every check command in Tasks 1–3 gave its stated output, and `build/run_commit_lints.sh` passed. Task 3's `"$BASE" HEAD` diffs ran against the working tree (`git diff "$BASE" --`), because the replay made no commits.

## Global Constraints

- **Scope.** The Stage 3 entry's Spec refs only: § Stage C (R25–R29), § Verification V3 (Stage C), § Coordination. This is the roadmap's last stage, and its `Produces` is "none for later stages".
- **Leave alone:**
  - Every `description` in the three skills (spec Non-goals; roadmap Exit). Task 3 checks that their frontmatter is byte-identical to `c35dbfb`.
  - develop-testing-strategy's "three code kinds" framing (`SKILL.md:32-35`).
  - validate-data's §6 report template (`SKILL.md:268-312`). R26 adds no section to it.
  - recommend-visualization's `VALID_INTENTS` (`scripts/recommend.py:56`) and its existing `bayesian-workflow` sibling bullet (`SKILL.md:40-43`). That bullet is the source of the existing soft pair `recommend-visualization → bayesian-workflow`.
  - rpm's `references/reporting.md` `Iterate` line (:56), and rpm's `references/model-selection-regularization.md`. Its stale Output paragraph is deferred in `specs/deferred_items.md` section `67-model-lifecycle` (plan 67's Handoff), and it is not Stage 3 scope.
  - `skills/tune-hyperparameters/` and `skills/track-model-experiments/` (Stages 1 and 2 shipped them).
- **No micro-test.** Spec § Stage C: "Body text only. No description changes … needs no micro-test." V3 (Stage C) is the dependency-drift test and the commit lints. V1 does not apply to this stage.
- **R29 path form.** A route line names track's reference as the exact string `track-model-experiments/references/predictive-evaluation.md`. tune already uses this form. The scanner (`build/test_runtime_support.py`, `referenced_dependencies`) matches it as an edge to `skill:track-model-experiments`. A spec-style phrase such as "track's reference" makes no edge, and the new soft pair then fails with `a soft reference is gone; drop it`.
- **Bare names for the other routes.** Name `bayesian-workflow`, `evaluate-deep-learning`, `tune-hyperparameters` and `track-model-experiments` (outside the path above) by bare name only. The scanner records an edge for a skill name followed by a file name, a `references/` or `scripts/` path or a `§`, or by a possessive and a capitalized word (`deep-learning's Training`). The text in this plan was checked against the scanner at plan time: it adds exactly three edges, all to `skill:track-model-experiments`.
- **Compaction window.** `check_conformance.py`'s `compaction-window` check fails a SKILL.md whose body (the text after the frontmatter) is over 20,000 characters. At `c35dbfb` the bodies are: develop-testing-strategy 17,460; validate-data 18,406; recommend-visualization 5,741. Task 1 adds about 300–335 characters to each (17,795, 18,731 and 6,036 after it, in the plan-time replay). If a body goes over 20,000, stop and ask your human partner.
- **Provenance.** develop-testing-strategy, validate-data, recommend-visualization and rpm are the owner's originals (`NOTICE`). The new lines are newly written. No NOTICE change.
- **Public repo.** `specs/` is public. Write no private-repo detail.
- **Long commands.** Give the build suite and `build/run_commit_lints.sh` the 10-minute timeout.
- Every commit passes `build/run_commit_lints.sh`, which the pre-commit hook runs. If a commit is refused, fix the cause. Never pass `--no-verify`.
- Commit messages end with the executing session's attribution trailer.

## Decisions

- **D1** (owner, plan review, 2026-10-23): Accept defaults 1-6 below as the plan states them. Applied in: Tasks 1-3 (default 1), Task 1 (defaults 2-5), Task 2 (default 6).

**Defaults this plan settles (settled at plan review by D1):**

1. **Task shape.** Three tasks: the three routes with their soft pairs (one drift-test cycle), R28, and the stage gates. A per-skill split would give three reviews of a five-line edit each, under one spec section and one test.
2. **R25 placement.** The line goes directly under the Step 4 heading (`SKILL.md:140`), before "You cannot assert an exact posterior". A reader with a model that is not Bayesian sees the route before Step 4's Bayesian-only checks. The alternative is a closing paragraph before Step 5.
3. **R26 "the report records which producer checked it".** The Analysis QA bullet tells the analyst to name the producer on §4's existing "Conclusions supported" line. The §6 template stays byte-identical, as R26 requires.
4. **R27 placement and reach.** A new bullet in "This skill vs. its siblings", directly after the `bayesian-workflow` bullet, which stays byte-identical. Note: `predictive-evaluation.md` and `evaluate-deep-learning` have no chart guidance; only bayesian-workflow has a `visualize.md`. The line keeps the spec's "go to" and routes the evaluation behind such a chart to its owner. It does not claim that those files draw charts.
5. **R29 entries.** Three pairs, each with a one-line reason saying the source skill works without track installed. Each goes in alphabetical order by source: `develop-testing-strategy` after `derive-roadmap → writing-plans`, `recommend-visualization` after its `recommend-probabilistic-model` pair, and `validate-data` after `tune-hyperparameters → track-model-experiments`.
6. **R28 wording.** The line becomes `<bayesian-workflow | tune-hyperparameters, then track-model-experiments (score mode) | drill-down>`. The `Iterate` line below it (plan 64) also names both skills. It stays, because it also covers the Bayesian branch.

---

## File Structure

| File | Change | Responsibility |
|---|---|---|
| `skills/develop-testing-strategy/SKILL.md` | Modify (Task 1) | R25: route under Step 4 |
| `skills/validate-data/SKILL.md` | Modify (Task 1) | R26: route in Analysis QA |
| `skills/recommend-visualization/SKILL.md` | Modify (Task 1) | R27: route in the siblings list |
| `build/test_runtime_support.py` | Modify (Task 1) | R29: three `SOFT_REFERENCES` entries |
| `skills/recommend-probabilistic-model/references/reporting.md` | Modify (Task 2) | R28: "Runs next" |

Each edit below is an exact replacement: find the "Old" block in the file (it occurs once), and replace it with the "New" block. Use the Edit tool with the text as given.

**Coordination.** Plan 63 (#112) and plan 64 (#111) are both merged, so § Coordination's gate and rebase point are met. Plan 66 (`specs/plans/66-package-versions.md`) is live and shares no file with this plan: its Task 11 records the `Polars 1.42` claims in `build/versions_check.py` and does not edit `recommend-visualization/SKILL.md`. Its `--python 3.<n>` sweep (Task 13) matches none of this plan's files. Before Task 1, re-run `uv run skills/writing-plans/scripts/entry_check.py` from the repo root. If it reports a shared file, stop and ask.

---

### Task 1: Three thin routes and their soft pairs (R25, R26, R27, R29)

**Files:**
- Modify: `skills/develop-testing-strategy/SKILL.md` (Step 4 heading, :140)
- Modify: `skills/validate-data/SKILL.md` (Analysis QA bullet, :43-45)
- Modify: `skills/recommend-visualization/SKILL.md` (siblings list, after :40-43)
- Modify: `build/test_runtime_support.py` (`SOFT_REFERENCES`)

**Interfaces:**
- Consumes: `skills/track-model-experiments/references/predictive-evaluation.md` (Stage 1, unchanged since).
- Produces: three dependency edges, `skill:develop-testing-strategy`, `skill:validate-data` and `skill:recommend-visualization` to `skill:track-model-experiments`, each declared soft. Task 3 reads them.

- [ ] **Step 1: Confirm the baseline**

```bash
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies; cd ..
grep -c 'predictive-evaluation' skills/develop-testing-strategy/SKILL.md skills/validate-data/SKILL.md skills/recommend-visualization/SKILL.md
```

Expected: the drift tests pass. Each file prints `0`.

- [ ] **Step 2: Add develop-testing-strategy's route (R25)**

In `skills/develop-testing-strategy/SKILL.md`, Old:

```markdown
## Step 4 — Bayesian models (NumPyro / PyMC)

You cannot assert an exact posterior
```

New:

```markdown
## Step 4 — Bayesian models (NumPyro / PyMC)

A model that is not Bayesian (sklearn, boosting, statsmodels, a neural net) applies Step 1's
invariant groups like any other unit. Its evaluation protocol — cross-validation, backtests,
benchmark comparison — belongs to `track-model-experiments/references/predictive-evaluation.md`,
or to `evaluate-deep-learning` for a neural model.

You cannot assert an exact posterior
```

- [ ] **Step 3: Add validate-data's route (R26)**

In `skills/validate-data/SKILL.md`, Old:

```markdown
  trigger: a nowcast, a provider-vs-official comparison, anything headed for a slide or a doc.
```

New:

```markdown
  trigger: a nowcast, a provider-vs-official comparison, anything headed for a slide or a doc.
  A model result's evaluation is checked by its producer — `bayesian-workflow` for a Bayesian
  fit, `track-model-experiments/references/predictive-evaluation.md` for CV or backtest scores,
  `evaluate-deep-learning` for a neural model — and the report's §4 "Conclusions supported"
  line names the producer that checked it.
```

- [ ] **Step 4: Add recommend-visualization's route (R27)**

In `skills/recommend-visualization/SKILL.md`, Old:

```markdown
  thing you're plotting is a fitted model's draws; use this one for the data.
```

New:

```markdown
  thing you're plotting is a fitted model's draws; use this one for the data.
- **Model-output charts** (intervals, CV metrics, calibration curves) go to the skill that owns
  the evaluation: `bayesian-workflow` for posterior draws,
  `track-model-experiments/references/predictive-evaluation.md` for CV folds and backtests, and
  `evaluate-deep-learning` for neural runs.
```

- [ ] **Step 5: Run the drift test to see the three new edges (the failing check)**

```bash
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies; cd ..
```

Expected: `test_declared_dependencies_match_skill_and_command_text` FAILS at `assert declared == referenced - SOFT_REFERENCES`. The set diff lists exactly these three extra items, and no other:

```text
('skill:develop-testing-strategy', 'skill:track-model-experiments')
('skill:recommend-visualization', 'skill:track-model-experiments')
('skill:validate-data', 'skill:track-model-experiments')
```

If a pair is missing, its line did not match the scanner: check the path string. If any other pair appears, a bare name was followed by a file, a path, a `§` or a possessive and a capitalized word. Fix the wording, not the test.

- [ ] **Step 6: Declare the three soft pairs (R29)**

In `build/test_runtime_support.py`, Old:

```python
  # Likens a stage to writing-plans' Scope Check; an analogy, not a step.
  ('skill:derive-roadmap', 'skill:writing-plans'),
```

New:

```python
  # Likens a stage to writing-plans' Scope Check; an analogy, not a step.
  ('skill:derive-roadmap', 'skill:writing-plans'),
  # Routes a model package's evaluation protocol to track's predictive-evaluation
  # reference; the test plan never reads it.
  ('skill:develop-testing-strategy', 'skill:track-model-experiments'),
```

Old:

```python
  # Likens its extra signals to characterize.py's; never runs it.
  ('skill:recommend-visualization', 'skill:recommend-probabilistic-model'),
```

New:

```python
  # Likens its extra signals to characterize.py's; never runs it.
  ('skill:recommend-visualization', 'skill:recommend-probabilistic-model'),
  # Routes CV and backtest charts to track's predictive-evaluation reference;
  # never reads it.
  ('skill:recommend-visualization', 'skill:track-model-experiments'),
```

Old:

```python
  ('skill:tune-hyperparameters', 'skill:track-model-experiments'),
```

New:

```python
  ('skill:tune-hyperparameters', 'skill:track-model-experiments'),
  # Names track's predictive-evaluation reference as the producer that checks a
  # CV or backtest result; the QA pass runs without it.
  ('skill:validate-data', 'skill:track-model-experiments'),
```

- [ ] **Step 7: Run the drift test and the conformance lint (passing)**

```bash
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies; cd ..
uv run --python 3.13 --with pyyaml python build/check_conformance.py
cd build && uv run -q --python 3.13 --with pyyaml python -c "
import check_conformance as c, pathlib
for s in ['develop-testing-strategy', 'validate-data', 'recommend-visualization']:
    print(s, len(c.skill_body(pathlib.Path('../skills/' + s + '/SKILL.md').read_text())[0]))
"; cd ..
```

Expected: the drift tests pass with the same count as Step 1 (+0 tests). `check_conformance.py` exits 0. Each body is under 20,000 characters (the plan-time replay printed 17,795, 18,731 and 6,036).

- [ ] **Step 8: Commit**

```bash
git add skills/develop-testing-strategy/SKILL.md skills/validate-data/SKILL.md skills/recommend-visualization/SKILL.md build/test_runtime_support.py
git commit -m "docs: route model evaluation from three skills to its owners" -m "develop-testing-strategy (R25), validate-data (R26) and recommend-visualization (R27) each gain one body line that sends model evaluation to bayesian-workflow, track-model-experiments' predictive-evaluation reference or evaluate-deep-learning. Each line names the reference by its full path, so the drift scanner records an edge to track; SOFT_REFERENCES declares the three edges soft (R29). No description changes."
```

---

### Task 2: rpm's "Runs next" (R28)

**Files:**
- Modify: `skills/recommend-probabilistic-model/references/reporting.md:54`

**Interfaces:**
- Consumes: nothing from Task 1.
- Produces: nothing a later task reads.

- [ ] **Step 1: Confirm the anchor (the failing check)**

```bash
grep -c 'sklearn/other' skills/recommend-probabilistic-model/references/reporting.md
grep -c 'then track-model-experiments (score mode)' skills/recommend-probabilistic-model/references/reporting.md
```

Expected: `1`, then `0`.

- [ ] **Step 2: Edit the line**

In `skills/recommend-probabilistic-model/references/reporting.md`, Old:

```markdown
- **Runs next:** <bayesian-workflow | sklearn/other | drill-down>
```

New:

```markdown
- **Runs next:** <bayesian-workflow | tune-hyperparameters, then track-model-experiments (score mode) | drill-down>
```

- [ ] **Step 3: Check the edit and that it adds no edge**

```bash
grep -c 'sklearn/other' skills/recommend-probabilistic-model/references/reporting.md
grep -c 'then track-model-experiments (score mode)' skills/recommend-probabilistic-model/references/reporting.md
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies; cd ..
```

Expected: `0`, then `1`. The drift tests pass: the line names both skills by bare name, so it adds no edge.

- [ ] **Step 4: Commit**

```bash
git add skills/recommend-probabilistic-model/references/reporting.md
git commit -m "docs(rpm): name tune then track as the non-Bayesian next step" -m "The memo template's Runs next line replaces sklearn/other with tune-hyperparameters, then track-model-experiments (score mode) (spec R28)."
```

---

### Task 3: Stage gates

**Files:** none changed, unless a gate fails.

- [ ] **Step 1: Run the V3 Stage C gates**

```bash
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies; cd ..
build/run_commit_lints.sh
```

Expected: both exit 0.

- [ ] **Step 2: Check the scope fence and the roadmap Exit**

```bash
git fetch -q origin
BASE="$(git merge-base origin/main HEAD)"
for s in develop-testing-strategy validate-data recommend-visualization; do f=skills/$s/SKILL.md; diff <(git show "${BASE}:$f" | awk 'NR==1||/^---$/{c++} c<2') <(awk 'NR==1||/^---$/{c++} c<2' $f) && echo "$s frontmatter unchanged"; done
git diff --stat "$BASE" HEAD -- skills/tune-hyperparameters skills/track-model-experiments skills/recommend-probabilistic-model/references/model-selection-regularization.md skills/recommend-visualization/scripts
git diff --name-only "$BASE" HEAD -- skills build
git diff "$BASE" HEAD -- skills/validate-data/SKILL.md | grep '^[-+]' | grep -v '^[-+][-+]'
```

`BASE` is where this branch left main (`c35dbfb` unless the branch was rebased), so the diffs show this branch's own commits only.

Expected:
- Three `… frontmatter unchanged` lines.
- The `--stat` command prints nothing.
- The name list is exactly `build/test_runtime_support.py`, `skills/develop-testing-strategy/SKILL.md`, `skills/recommend-probabilistic-model/references/reporting.md`, `skills/recommend-visualization/SKILL.md` and `skills/validate-data/SKILL.md`.
- The validate-data diff shows only the four added lines of Task 1 Step 3 (no `-` line), so §6 is unchanged.

Check each item of the roadmap's Stage 3 Exit, and write the evidence into the execution ledger:
- the dependency-drift test passes with the R29 soft pairs (Step 1; Task 1 Step 5 showed that the three pairs are real edges);
- `build/run_commit_lints.sh` passes (Step 1);
- no description in the three skills changed (the three `frontmatter unchanged` lines).

- [ ] **Step 3: Run the Plan Completion Protocol (writing-plans)**

This is the roadmap's last stage, so three parts of the protocol differ from Stages 1 and 2:
- **Step 5 (retire).** Retire the plan only. Leave `specs/model-lifecycle.md` and `specs/model-lifecycle-roadmap.md` in place, even though no other live plan implements the spec. The roadmap's § Completion has derive-roadmap re-run the gap rubric over R1–R29 and V1–V3 first, and only then retire both.
- **Step 3a (Handoff).** `## Handoff to later stages` reads `None: last stage.`
- **Step 3a (stamp).** The stamp keeps only its first sentence, because the Handoff section reads `None`:

  ```
  > Stage 3: COMPLETE (YYYY-MM-DD) — implemented by plan 68 (specs/plans/completed/68-model-lifecycle.md).
  > Next: resume the roadmap.
  ```

Step 3's ticking pass is expected to tick nothing: the spec's § Done when items were ticked in earlier stages. At plan time, a grep of `specs/deferred_items.md` for `sklearn/other`, `Runs next`, `G9`, `reporting.md` and the three skill names found two items that name R28's line or the G9 routes (section `audit-3-10-26 routing`: the O1–O3 owner calls and the lifecycle-spec item), and both are already ticked. The open hits are not closed by R25–R28: the P2-tier owner pick (the item that starts "Owner picks the keepers from audit_1_3_26's never-logged P2 tier") and the item about rpm's `model-selection-regularization.md` Output paragraph (section `67-model-lifecycle`). Both stay open.
