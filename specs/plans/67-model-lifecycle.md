# Model-lifecycle Stage 2: tune-hyperparameters as the model-agnostic search loop — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

> Roadmap: specs/model-lifecycle-roadmap.md, Stage 2 — on plan completion, tick the stage and re-validate later stages against what shipped.

**Goal:** `tune-hyperparameters` covers three regimes, any producer's knobs, and graduation to a score-mode ledger, with a micro-tested description and a probed noise rule.

**Architecture:** Documentation only, plus one comment in a build test. tune's `SKILL.md` gains a third regime (structural choices), a splitter table, an objective table, an early-stopping rule, a runnable nested-CV snippet, a neural-search section, a paired noise rule, a producers router, an owned optax row, a rewritten Graduation and a causal boundary. recommend-causal-design gains one sibling line, rpm's knob table gains two rows, and the root README's tune row is rewritten. Two `claude -p` micro-tests check the result: V2 checks the noise rule, and V1 checks the new description against the current one.

**Tech Stack:** Markdown; Python 3.13 via `uv` for the lints; Optuna 5.0.0 and scikit-learn 1.9.1 (the versions the R4 snippet ran against at plan time); `claude -p` 2.1.304 for the micro-tests.

**Spec:** `specs/model-lifecycle.md` — § Stage A (R1–R12b), § Verification V1 (tune arm), V2 and V3 (Stage A), and R7's soft reference as the R7 row of the roadmap's gap table describes it (`specs/model-lifecycle-roadmap.md`). Also three items in `specs/deferred_items.md` section `59-model-skill-comparator-and-cv-fixes`: part (b) of "Two doc nits left by plan 59's final review", the tune `description` "dynamax optax SGD" item, and "Watch tune's Regime B router wording for over-deferral" (read by R9; it stays open).

**Base commit:** `7a8fbaa` (origin/main when this plan was written; plan 65 merged as lowmason/agent-skills#115). The spec's line anchors for tune, recommend-causal-design and rpm's `references/model-selection-regularization.md` still hold at this commit, because none of those files changed after the spec's evidence commit `94d1786`.

**Plan-time replay.** Every Old block below was applied in order to a scratch copy of `7a8fbaa` and matched exactly once. On the result, every check command in Tasks 1, 2, 4 and 6 gave its stated output, and `build/run_commit_lints.sh` passed. The micro-tests were not run.

## Global Constraints

- **Scope.** The Stage 2 entry's Spec refs only. Do not plan or do Stage 3 (spec § Stage C: develop-testing-strategy, validate-data, recommend-visualization, rpm's `references/reporting.md`).
- **Leave alone:** `skills/tune-hyperparameters/scripts/` (both files). The roadmap Exit requires `test_time_series_cv.py` unchanged, and R3 adds no splitter code. The deferred item "Three nits in the splitter's tests" stays open. Also leave alone `skills/track-model-experiments/` (Stage 1 shipped it) and every other skill's `description`, except tune's.
- **R1.** tune's `description` starts "Use when", is third person, and has at most 1,024 characters. It ships only after the V1 tune arm passes.
- **R7.** The rule uses the plain `SE(Δ) = sd(d) / √K` (spec § Terms: `d` is the vector of per-fold differences, `K` the number of folds, `sd` the sample standard deviation). When |Δ| is under 2·SE(Δ), the difference is noise and the default ships. tune states the rule in one sentence and points to track's `references/predictive-evaluation.md` for the protocol and the SE's limits.
- **R11, R13 contract** as built by plan 65: `scores.json` is `{"criterion": ..., "orientation": "higher"|"lower", "units": {<fold or origin id>: <finite number>}}`. A score criterion must not be named `elpd-loo`. A ledger declares its criterion on one `Criterion: <name>` line above its Variants table, and a score ledger's metric columns are `score`, `Δscore` and `SE(Δ)`.
- **R12a.** A knob row cites only a PML section that `build/verify_citations.py` Gate A resolves, or gives no § reference. No book prose. Write every reference with its book prefix (`PML1 §11.5.2, PML1 §11.5.3`): Gate A's pattern `\bPML([12])\s*§` skips a bare `§11.5.3`, so an unprefixed reference is never checked.
- **Bare-name handoffs.** In tune and in causal's sibling line, name another skill by its bare name only. The dependency-drift scanner (`build/test_runtime_support.py`, `referenced_dependencies`) records a new edge for a skill name followed by a file name, a `references/` or `scripts/` path or a `§`, or by a possessive and a capitalized word (`deep-learning's Training`, `tune-hyperparameters' Boundary`). The plan's text was checked against the scanner at plan time. Run the drift test after every edit to a skill file.
- **Compaction window.** `check_conformance.py`'s `compaction-window` check fails a SKILL.md whose body (the text after the frontmatter) is over 20,000 characters (5,000 tokens at 4 characters each). It is a commit lint, and tune has no waiver. tune's body is 9,616 characters at the base commit, 12,820 after Task 1 and 16,237 after Task 2 in the plan-time scratch run. If a task's edit takes it over 20,000, stop and ask your human partner. Do not move text to a new `references/` file on your own. Keep the words `STOP`, `Red Flags`, `Critical`, `Gotchas`, `Iron Law`, `Hard Gate` and `Warning` out of headings.
- **Watch item (R9).** The `NUTS target_accept` row of the Regime B table and the sentence "The mechanics and thresholds live in the files each row names — this table is the router, not the doctrine." stay byte-identical. Plan 59's router micro-test (`specs/verification/59-regime-b-router-microtest.md`) graded that text, and the deferred watch item rests on it.
- **Provenance.** tune, rpm and track are the owner's originals. recommend-causal-design adapts MIT sources, and its NOTICE paragraph already says that "routing" is newly written, so R12's sibling line needs no NOTICE change. No book prose is copied into rpm.
- **Public repo.** `specs/` is public. Prompts and examples use generic nowcast, panel and store names, with no private-repo detail.
- **Long commands.** The Bash tool's default timeout is 2 minutes. Run each micro-test arm in the background and wait for its completion notice. Give the build suite and `build/run_commit_lints.sh` the 10-minute timeout.
- Every commit passes `build/run_commit_lints.sh`, which the pre-commit hook runs. If a commit is refused, fix the cause. Never pass `--no-verify`.
- Commit messages end with the executing session's attribution trailer.

## Decisions

- **D1** (owner, plan review, 2026-10-22): Leave plan 64's survival row for rpm's knob table out of this plan. It stays in `specs/deferred_items.md` section `64-bayesian-rpm-routing`. Applied in: Task 4.
- **D2** (owner, plan review, 2026-10-22): Accept defaults 1-11 and 13 below as the plan states them. Applied in: Task 2 (defaults 1-5), Tasks 1-2 (default 7), Task 1 (default 8), Task 3 (default 9), Task 4 (defaults 6 and 13), Task 5 (defaults 10 and 11).
- **D3** (owner, plan review, 2026-10-22): Default 12 stands at 4 of 5 repetitions, not 5 of 5, for both `V2-real` and `V2-noise`. Applied in: Task 3.

**Defaults this plan settles (settled at plan review by D2 and D3):**

1. **R7's soft reference already exists.** The spec says Stage 2 "adds the entry", but the pair `('skill:tune-hyperparameters', 'skill:track-model-experiments')` is already in `SOFT_REFERENCES`, and the drift test keys on skill pairs. Task 2 rewrites the entry's reason and adds no entry. This follows the test, as R22's clause allows ("If the drift test classifies a path otherwise, the plan follows the test and records why").
2. **R7's pointer is a full path.** tune writes `track-model-experiments/references/predictive-evaluation.md`. The scanner matches it, so the tune → track pair stays referenced even if a later edit drops Graduation's `experiments.md` mention.
3. **Regime C's rule.** A knob is Regime C when it picks the structure of a probabilistic model from a discrete set (components, factors, states, lags, kernel or basis form). A knob that sets one predictor's flexibility stays Regime A even when its values are discrete (a penalty, tree depth, `k` for kNN). The optax learning rate of a non-neural point fit is Regime B (D4). A neural learning rate stays Regime A (R8). GP hyperparameters fit by type-II marginal likelihood are set inside the fit, so no regime tunes them.
4. **R9's extent.** The edit changes the optax row and Step 0's Regime B bullet, and deletes the "The optax row has no owner…" sentence with no replacement. The row's "Owned by" cell says "this skill". The `target_accept` row and the router sentence stay byte-identical (Task 2 checks this). The watch item's trigger has not fired, so it stays open with a progress note.
5. **R11's re-declare step swaps the columns.** tune's Graduation also says to swap the ELPD columns for `score`, `Δscore` and `SE(Δ)`, which R15 requires of a score ledger. track's own When to use omits that step. That is plan 65's deferred "Track doc polish" part (a), which stays with that item.
6. **R12a's citations.** The spline row cites PML1 §11.5.2 and PML1 §11.5.3. Both resolve under Gate A. A plan-time Gate B read found that §11.5.2 says more knots eventually overfit and the count can be chosen by model selection such as cross-validation, and that §11.5.3 keeps a knot at every point with an ℓ2 penalty. The AR-order row gives no § reference. The PML section titles show no section on choosing an AR order, and §29.11.2 and §29.12.2 discuss AR terms without selection.
7. **Placement in tune.** Step 0b (the splitter table), "What to score" (R6), the early-stopping rule (R5), the nested-CV snippet (R4) and "Neural search" (R8) go inside the Regime A section. "Regime C — structural choices" and "Producers" (R10) go after Regime B and before Boundary.
8. **R4's snippet** uses the bundled `PurgedTimeSeriesSplit` for both the outer and the inner split, so it works on a panel with `groups`. It ran at plan time against Optuna 5.0.0 and scikit-learn 1.9.1 on synthetic data. The text names both versions.
9. **V2's fixtures.** The audit records only the probe's shape (all 5 paired differences share a sign, mean/SE 2.8), not its numbers, and no audit kit survives. So this plan builds them. The `V2-real` fixture has per-fold differences 0.02, 0.06, 0.01, 0.08, 0.02 (mean 0.038, SE 0.0136, mean/SE 2.80). The default's fold-to-fold standard deviation is 0.233, so today's rule (spread against gap) calls it noise. A second fixture, `V2-noise`, has differences 0.04, −0.03, 0.05, 0.01, 0.03 (mean/SE 1.41), so a rule that calls every gain real fails.
10. **V1's design.** The listing has six skills: tune and its five probes (spec V1). Three triggers: a grouped-CV search, a mixture-K sweep and a neural trial budget. One near-miss for each probe. Control descriptions come from `7a8fbaa`.
11. **Description wording.** The draft says "grouped, spatial, or independent rows", not "i.i.d.". The `description-person` lint reads the "i" in "i.i.d." as a first-person pronoun and fails it (plan-time run).
12. **V2's bar.** Spec V2 says the agent "must" call the difference real. This plan reads that as at least 4 of 5 reps, after plan 59's bars, and adds the same bar for the `V2-noise` fixture. A stricter reading is 5 of 5.
13. **Gate A in a worktree.** `verify_citations.py` reads `build/.scratch/` beside itself, and that directory exists only in the main checkout. Task 4 copies it into the worktree (a real copy, never a symlink) and never commits it.

**Open question for plan review (settled by D1):** plan 64 deferred "Add a survival row to rpm's per-family knob table" (`specs/deferred_items.md` section `64-bayesian-rpm-routing`), because R12a owns that table. That row is outside the Stage 2 Spec refs, so this plan leaves it out by default. Fold it into Task 4?

---

## File Structure

| File | Change | Responsibility |
|---|---|---|
| `skills/tune-hyperparameters/SKILL.md` | Modify (body Tasks 1–2, description Task 5) | R1–R12 (tune side) |
| `build/test_runtime_support.py` | Modify (Task 2) | R7: the soft pair's reason |
| `skills/recommend-causal-design/SKILL.md` | Modify (Task 4) | R12: the sibling line |
| `skills/recommend-probabilistic-model/references/model-selection-regularization.md` | Modify (Task 4) | R12a: two knob rows |
| `README.md` | Modify (Task 4) | R12b: tune's row |
| `specs/verification/67-tune-noise-rule-probe.md` | Create (Task 3) | V2 record |
| `specs/verification/67-tune-description-microtest.md` | Create (Task 5) | V1 tune record |

The micro-test kit lives outside the repo at `~/.cache/agent-skills/scratch/plan67-micro/`.

Each edit below is an exact replacement: find the "Old" block in the file (it occurs once), and replace it with the "New" block. Use the Edit tool with the text as given. Outer fences are four backticks where a block holds a code fence.

---

### Task 1: tune's regimes and the Regime A protocol (R2 rule, R3, R4, R5, R6)

**Files:**
- Modify: `skills/tune-hyperparameters/SKILL.md` (Overview, Step 0, Regime A)

**Interfaces:**
- Consumes: nothing.
- Produces: the Step 0 bullet "**Regime C — structural choice.**", which ends "(Regime C, below)". Task 2 adds the `## Regime C — structural choices` section it points to. The `### Step 0b — choose the splitter by dependence structure` heading and the early-stopping paragraph, which Task 2's "Neural search" calls "(above)".

- [ ] **Step 1: Confirm the anchors (the failing check)**

```bash
grep -c -F 'Tuning is the loop above' skills/tune-hyperparameters/SKILL.md
grep -c -F 'The rule: a knob is **Regime B** only when' skills/tune-hyperparameters/SKILL.md
grep -c -F 'a dynamax optax schedule.' skills/tune-hyperparameters/SKILL.md
grep -c -F 'wrap it in nested CV' skills/tune-hyperparameters/SKILL.md
grep -c 'Regime C\|Step 0b\|What to score\|Early stopping' skills/tune-hyperparameters/SKILL.md
```

Expected: each of the first four lines prints `1`. The last command prints `0`: none of the new text exists yet.

- [ ] **Step 2: Name the producers in the Overview**

Old:

```markdown
tree depth, learning rate, a sampler's `target_accept`. Tuning is the loop above
a single fit: propose a value, score it, keep the best. Two things break that
```

New:

```markdown
tree depth, learning rate, a sampler's `target_accept`, the number of mixture
components. Tuning is the loop above a single fit: propose a value, score it,
keep the best. The loop is the same for any producer: sklearn and boosting,
statsmodels, NumPyro, dynamax or a neural net. Two things break that
```

- [ ] **Step 3: Restate Step 0's rule (R2)**

Old:

```markdown
The rule: a knob is **Regime B** only when its correct value is defined by the
fidelity of the fit — whether the sampler or optimizer reached what the model
already defines (its posterior, or its optimum). Every other knob is
**Regime A**: its correct value is the one that predicts held-out data best.
```

New:

```markdown
The rule puts each knob in exactly one regime. A knob is **Regime B** when its
correct value is defined by the fidelity of the fit — whether the sampler or
optimizer reached what the model already defines (its posterior, or its
optimum). A knob is **Regime C** when it picks the structure of a probabilistic
model from a discrete set: how many components, factors, states or lags the
model has, or the form of its kernel or basis. Every other knob is
**Regime A**: its correct value is the one that predicts held-out data best.
A knob that sets one predictor's flexibility (a penalty, tree depth, `k` for
kNN) is Regime A, even when its values are discrete.
```

- [ ] **Step 4: Move optax into Regime B's bullet and add Regime C's bullet (R2, D4)**

Old:

```markdown
  controls whether the *fit itself* is trustworthy: NUTS `target_accept` /
  `max_tree_depth`, SVI learning rate / steps, a dynamax optax schedule.
  Evaluate on convergence diagnostics, **not** on a held-out predictive metric.
```

New:

```markdown
  controls whether the *fit itself* is trustworthy: NUTS `target_accept` /
  `max_tree_depth`, SVI learning rate / steps, the optax learning rate of a
  non-neural point fit such as a dynamax MLE.
  Evaluate on convergence diagnostics, **not** on a held-out predictive metric.
- **Regime C — structural choice.** You're choosing among model structures:
  the number of mixture components `K`, of factors or of HMM states, the AR
  order, spline knots, a GP kernel form. Each candidate is a separate model,
  so score it on a criterion that compares whole models (Regime C, below).
```

- [ ] **Step 5: Add Step 0b, the splitter table (R3)**

Old:

```markdown
## Regime A — leakage-safe predictive search

**The trap.**
```

New:

```markdown
## Regime A — leakage-safe predictive search

### Step 0b — choose the splitter by dependence structure

Validation rows must be as independent of the training rows as new data will
be. Pick the splitter from how the rows depend on each other:

| Data | Splitter |
|---|---|
| i.i.d. | `KFold`, or `StratifiedKFold` for classes |
| Grouped, or predicting new entities | `GroupKFold` or `LeaveOneGroupOut` |
| Spatial | `GroupKFold` over spatial blocks |
| Temporal | the bundled `PurgedTimeSeriesSplit` (the protocol below) |
| Random forests | out-of-bag error |

All but the temporal splitter are sklearn's. A panel is temporal: use the
bundled splitter with `groups=period`. The rest of this section is the temporal
protocol.

**The trap.**
```

- [ ] **Step 6: Add the objective table before the search (R6)**

Old:

```markdown
**The search — a manual Optuna objective** (verified against Optuna 5.0.0). Keep
```

New:

```markdown
**What to score.** Match the objective to what the model emits:

| Model emits | Objective |
|---|---|
| Point predictions | MSE or MAE, or a loss that matches the decision |
| Predictive distributions | log score or CRPS (strictly proper) |
| Class probabilities | log-loss or Brier, never accuracy alone |
| Forecasts | per-origin loss differences |

**The search — a manual Optuna objective** (verified against Optuna 5.0.0). Keep
```

- [ ] **Step 7: Add the early-stopping rule (R5) and replace the nested-CV prose with a snippet (R4)**

Old:

```markdown
**Guard against validation-set overfitting.** A large search over one held-out
split finds a knob that flatters *that split*. For big searches or high-stakes
decisions, wrap it in nested CV — an outer forward-chaining split whose training
half runs the whole study — so the reported score comes from folds the search
never touched.
```

New:

````markdown
**Early stopping.** Take the stopping split from inside the training fold (the
last periods of `tr` for temporal data), never from the CV validation fold. A
fit that stops on the validation fold has seen it, so that fold's score is no
longer held out.

**Guard against validation-set overfitting.** A large search over one set of
folds finds a knob that flatters *those folds*. For big searches or high-stakes
decisions, nest it: an outer forward-chaining split runs the whole study on
each training half and scores the winner on the outer validation fold, which
the search never touched (verified against Optuna 5.0.0 and scikit-learn
1.9.1):

```python
outer = PurgedTimeSeriesSplit(n_splits=4, embargo=2)
outer_scores = []
for tr, te in outer.split(X):            # a panel: outer.split(X, groups=period)
    X_tr, y_tr = X[tr], y[tr]
    inner = PurgedTimeSeriesSplit(n_splits=5, embargo=2)

    def objective(trial):
        alpha = trial.suggest_float('alpha', 1e-3, 1e3, log=True)
        scores = []
        for fit, va in inner.split(X_tr):  # a panel: groups=period[tr]
            model = Ridge(alpha=alpha).fit(X_tr[fit], y_tr[fit])
            scores.append(mean_squared_error(y_tr[va], model.predict(X_tr[va])))
        return float(np.mean(scores))

    study = optuna.create_study(direction='minimize',
                                sampler=optuna.samplers.TPESampler(seed=0))
    study.optimize(objective, n_trials=50)
    winner = Ridge(**study.best_params).fit(X_tr, y_tr)
    outer_scores.append(mean_squared_error(y[te], winner.predict(X[te])))
float(np.mean(outer_scores))             # report this, not study.best_value
```
````

The snippet reuses the imports of the two code blocks above it (`PurgedTimeSeriesSplit`, `np`, `optuna`, `Ridge`, `mean_squared_error`).

- [ ] **Step 8: Check the size, the snippet gate and the lints**

```bash
python3 -c "t=open('skills/tune-hyperparameters/SKILL.md').read(); print(len(t.split('---\n',2)[2]))"
uv run --python 3.13 python build/check_snippets.py skills/
uv run --python 3.13 --with pyyaml python build/check_conformance.py
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies; cd ..
```

Expected: the body is about 12,820 characters (under 20,000). Each command exits 0. The snippet check may print its two existing WARN lines (`state-space.md`, `model-tests.md`), and none names tune.

- [ ] **Step 9: Run the R4 snippet once on synthetic data**

```bash
rm -rf /tmp/p67-r4 && mkdir -p /tmp/p67-r4
cp skills/tune-hyperparameters/scripts/time_series_cv.py /tmp/p67-r4/
python3 - <<'EOF'
import re
text = open('skills/tune-hyperparameters/SKILL.md').read()
block = next(b for b in re.findall(r'```python\n(.*?)```', text, re.S) if 'outer_scores' in b)
head = ('import numpy as np, optuna\n'
        'from sklearn.linear_model import Ridge\n'
        'from sklearn.metrics import mean_squared_error\n'
        'from time_series_cv import PurgedTimeSeriesSplit\n'
        'optuna.logging.set_verbosity(optuna.logging.WARNING)\n'
        'rng = np.random.default_rng(0)\n'
        'X = rng.normal(size=(240, 6)); y = X @ rng.normal(size=6) + rng.normal(size=240)\n')
open('/tmp/p67-r4/run.py', 'w').write(head + block.replace('float(np.mean(outer_scores))', 'print(float(np.mean(outer_scores)))'))
EOF
cd /tmp/p67-r4 && uv run --python 3.13 --with 'optuna==5.0.0' --with 'scikit-learn==1.9.1' --with numpy python run.py; cd -
```

Expected: one float near 1.1 (1.13 in the plan-time run of this exact harness). A traceback means the snippet is wrong: fix the snippet in the SKILL.md, not the harness.

- [ ] **Step 10: Commit**

```bash
git add skills/tune-hyperparameters/SKILL.md
git commit -m "docs(tune): add Regime C, the splitter and objective tables, and nested CV" -m "Restates Step 0 so each knob falls in one of three regimes, adds the structural-choice regime, a splitter table by dependence structure, an objective table, the early-stopping rule and a runnable nested-CV snippet (spec R2-R6)."
```

---

### Task 2: tune's search loop, noise rule, Regime B row, Regime C, producers, Graduation and boundary (R7–R12)

**Files:**
- Modify: `skills/tune-hyperparameters/SKILL.md` (Regime A's later subsections, Regime B, two new sections, Boundary)
- Modify: `build/test_runtime_support.py` (one `SOFT_REFERENCES` comment)

**Interfaces:**
- Consumes: Task 1's Step 0 bullet "(Regime C, below)", and its early-stopping paragraph.
- Produces: the R7 rule sentence that Task 3 probes, and the final tune body that Task 5's description summarizes.

- [ ] **Step 1: Confirm the anchors (the failing check)**

```bash
grep -c 'Fold-to-fold variance swamps the effect' skills/tune-hyperparameters/SKILL.md
grep -c 'until a non-ELPD mode exists' skills/tune-hyperparameters/SKILL.md
grep -c 'no skill owns this yet' skills/tune-hyperparameters/SKILL.md
grep -c 'The optax row has no owner' skills/tune-hyperparameters/SKILL.md
grep -c 'predictive-evaluation.md\|## Producers\|## Regime C' skills/tune-hyperparameters/SKILL.md
git show 7a8fbaa:skills/tune-hyperparameters/SKILL.md | grep -F '| NUTS `target_accept` |' > /tmp/p67-row-base.txt
```

Expected: `1`, `1`, `1`, `1`, then `0`.

- [ ] **Step 2: Add the neural-search section (R8) and replace the noise rule (R7)**

Old:

```markdown
### When not to tune

- **Fold-to-fold variance swamps the effect** — if the metric's spread across
  folds exceeds the gap between candidates, you're tuning noise; ship a default.
```

New:

```markdown
### Neural search

deep-learning and evaluate-deep-learning hand a neural search to this loop. A
neural learning rate stays Regime A.

- **Trial budget.** Fix the number of trials, and the epochs each trial may
  use, before the search starts.
- **Pruners.** Stop weak trials early with `optuna.pruners.MedianPruner`, or
  `SuccessiveHalvingPruner` for successive halving. The objective calls
  `trial.report(score, epoch)` each epoch and raises `optuna.TrialPruned()`
  when `trial.should_prune()` is true.
- **Early stopping** takes its split from inside the training fold (above).
- **Seeds.** One seed per trial ranks luck as much as the knob. Re-run the
  finalists over several seeds before you choose.

deep-learning owns schedule and state mechanics. evaluate-deep-learning owns
comparable-budget rules and the experiment record.

### When not to tune

- **The paired difference is noise** — score both candidates on the same folds
  and take the per-fold differences d. When |Δ|, the absolute mean of d, is
  under 2·SE(Δ) = 2·sd(d)/√K over K folds, ship the default. This is a screen.
  The protocol, and the corrections that widen the SE for high-stakes calls,
  are in `track-model-experiments/references/predictive-evaluation.md`.
```

(The pruner names and `trial.report`, `trial.should_prune` and `optuna.TrialPruned` were checked against Optuna 5.0.0 at plan time.)

- [ ] **Step 3: Rewrite Graduation (R11)**

Old:

```markdown
(`what changed` = "tuned `<class>` via Optuna, `<n>` trials, `<space>`"). The
comparator ranks variant rows by ELPD only, so until a non-ELPD mode exists, a
non-Bayesian winner goes in the ledger's Decision log with its CV score, not in
a variant row. The trial history stays in Optuna's store (`optuna-dashboard` to
browse); the ledger records only the winner and why it earned a seat.
```

New:

```markdown
(`what changed` = "tuned `<class>` via Optuna, `<n>` trials, `<space>`"). Its
variant folder holds a `scores.json` on the ledger's criterion, with one score
for each fold or origin that every other variant uses, and the comparator
ranks it in score mode.

An `elpd-loo` ledger cannot rank a non-Bayesian winner. To compare the winner
with the Bayesian variants, re-declare the ledger's `Criterion:` line as a
score criterion, and swap its ELPD columns for `score`, `Δscore` and `SE(Δ)`.
Each Bayesian variant then writes `scores.json` on the same units, for example
a per-fold log score or the MSE of the posterior-predictive mean. Until that is
done, the comparator names the new row as not compared. It never drops the
row in silence. The trial history stays in Optuna's store (`optuna-dashboard`
to browse); the ledger records only the winner and why it earned a seat.
```

- [ ] **Step 4: Give the optax row an owner (R9)**

Old:

```markdown
| dynamax optax learning rate | training-loss convergence | loss plateaus, no divergence | no skill owns this yet |
```

New:

```markdown
| optax learning rate of a non-neural point fit (dynamax MLE) | the optimizer reached the optimum | the training loss plateaus, and restarts from several initializations reach the same optimum within a stated tolerance | this skill |
```

Then delete the "no owner" sentence. Old:

```markdown
the router, not the doctrine. The optax row has no owner, so its stopping rule
is all the guidance there is until one exists.
```

New:

```markdown
the router, not the doctrine.
```

- [ ] **Step 5: Add the Regime C section and the producers router (R2, R10)**

Old:

```markdown
## Boundary
```

New:

```markdown
## Regime C — structural choices

Score each candidate on one of these criteria, on the same data, folds or
origins for every candidate:

- the type-II marginal likelihood, where it is exact (a GP kernel form);
- BIC or AIC, a quick screen of point fits;
- LOO, or LFO for forecasts, over the discrete index (`K = 1, 2, 3, …`);
- a rolling-CV log score.

This skill runs the sweep: a loop over the index, not an Optuna study. When
the candidate set is small and each candidate carries its own hypothesis (two
regimes or three, a seasonal term or none), record the candidates as rows in
track-model-experiments' ledger instead, so each one keeps its reason.

GP hyperparameters fit by type-II marginal likelihood (lengthscales,
amplitude, noise) are set inside the fit, not tuned. Regime C covers only the
choice of kernel form.

## Producers

The loop is the same whoever produced the model. The regime and the
objective change:

| Producer | Regime | Objective |
|---|---|---|
| recommend-probabilistic-model | A or C: it names the knob and its criterion | the criterion it names |
| bayesian-workflow | B for sampler and SVI knobs; C for structure | convergence diagnostics; LOO, or LFO for forecasts |
| deep-learning | A | a held-out loss or metric (Neural search, above) |
| evaluate-deep-learning | A, under its comparable-budget rules | its declared primary metric |
| recommend-causal-design | A, for nuisance learners only | predictive CV inside cross-fitting folds (Boundary, below) |

## Boundary
```

- [ ] **Step 6: Add the causal boundary (R12, tune side)**

Old:

```markdown
- `bayesian-workflow` — inference diagnostics (regime B's mechanics).
- **This skill** — the *search loop*: the CV protocol, regime classification,
  the Optuna objective, and graduation.
```

New:

```markdown
- `bayesian-workflow` — inference diagnostics (regime B's mechanics).
- `recommend-causal-design` — the design, the adjustment set, an RD bandwidth,
  synthetic-control weights and the effect estimate. Predictive CV is the
  right objective only for nuisance learners (propensity and outcome models)
  tuned inside cross-fitting folds, and it never selects any of those.
- **This skill** — the *search loop*: regime classification, the splitter, the
  CV protocol, the Optuna objective, structural sweeps, neural search, and
  graduation.
```

- [ ] **Step 7: Rewrite the soft pair's reason (R7)**

In `build/test_runtime_support.py`, Old:

```python
  # Hands a tuned model on to the experiments ledger; a next step.
  ('skill:tune-hyperparameters', 'skill:track-model-experiments'),
```

New:

```python
  # Graduates a tuned winner to the experiments ledger and points to its
  # predictive-evaluation reference for the protocol; tune states the paired
  # noise rule itself, so the search loop runs without either.
  ('skill:tune-hyperparameters', 'skill:track-model-experiments'),
```

- [ ] **Step 8: Check the edits, the size, the watch-item text and the lints**

```bash
grep -c 'Fold-to-fold variance swamps\|until a non-ELPD mode exists\|no skill owns this yet\|The optax row has no owner' skills/tune-hyperparameters/SKILL.md
grep -F '| NUTS `target_accept` |' skills/tune-hyperparameters/SKILL.md | diff - /tmp/p67-row-base.txt && echo 'target_accept row unchanged'
grep -c -F 'The mechanics and thresholds live in the files each row names — this table is' skills/tune-hyperparameters/SKILL.md
python3 -c "t=open('skills/tune-hyperparameters/SKILL.md').read(); print(len(t.split('---\n',2)[2]))"
uv run --python 3.13 python build/check_snippets.py skills/
uv run --python 3.13 --with pyyaml python build/check_conformance.py
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies; cd ..
```

Expected: `0`; `target_accept row unchanged`; `1`; a body of about 16,237 characters (under 20,000); each lint exits 0, and the drift test reports `2 passed`. If the drift test fails with a new pair, a cross-skill mention in the new text matched the scanner: reword it to a bare name (see Global Constraints) rather than adding an entry.

- [ ] **Step 9: Commit**

```bash
git add skills/tune-hyperparameters/SKILL.md build/test_runtime_support.py
git commit -m "docs(tune): own the optax knob, add neural search and the paired noise rule" -m "Adds the neural-search loop, the paired per-fold noise rule with a pointer to track's predictive-evaluation reference, the Regime C section and a producers router; gives the optax row an owner and a stopping rule; rewrites Graduation for score-mode ledgers; adds the causal boundary (spec R7-R12). The target_accept row and the router sentence are unchanged."
```

---

### Task 3: V2, the noise-rule probe

Run this right after Task 2, so that a failed rule is reworded before the description work.

**Files:**
- Create: `specs/verification/67-tune-noise-rule-probe.md`
- Kit (outside the repo): `~/.cache/agent-skills/scratch/plan67-micro/`

**Interfaces:**
- Consumes: tune's `SKILL.md` at HEAD after Task 2 (the variant arm), and at `7a8fbaa` (the control arm).
- Produces: `run_microtest.py` in the kit, which Task 5 reuses for V1.

- [ ] **Step 1: Build the kit**

Record the CLI version: `claude --version` (2.1.304 at plan time). Write `~/.cache/agent-skills/scratch/plan67-micro/run_microtest.py`:

```python
#!/usr/bin/env python3
# /// script
# requires-python = '>=3.12'
# dependencies = ['pyyaml>=6.0']
# ///
'''Plan 67 micro-tests: V1 (tune arm, routing) and V2 (the paired noise rule).

Each rep is one `claude -p` call with no tools, no MCP servers and no advisor, run
from its own new folder under /tmp/p67micro/.

V1 lists six skills by name and description, in name order. The control arm gives
tune's description at the base commit, and the variant arm gives the working tree's
draft. The five probes' descriptions come from the base commit in both arms.

V2 loads tune's whole SKILL.md as the system prompt: the base commit's file in the
control arm, the working tree's file in the variant arm.

Usage: uv run run_microtest.py "$REPO" <v1-pilot|v1-control|v1-variant|v2-control|v2-variant> [--reps N]
'''
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

KIT = Path(__file__).resolve().parent
BASE = '7a8fbaa'
TARGET = 'tune-hyperparameters'
PROBES = ('creative-thinking', 'deep-learning', 'evaluate-deep-learning',
          'recommend-probabilistic-model', 'track-model-experiments')
V1_PROMPTS = {
    'T1-grouped-cv': (
        "I'm tuning a LightGBM model that predicts weekly sales for stores we have not "
        'opened yet. Rows from the same store are correlated. I want to search the '
        'learning rate, num_leaves and min_child_samples with Optuna without an '
        'optimistic CV score. How should I set up the search?'),
    'T2-mixture-k': (
        "I've settled on a Gaussian mixture for county wage-growth profiles. Now I need "
        'to pick the number of components, somewhere between 2 and 8, without '
        'overfitting. How do I run that sweep?'),
    'T3-neural-budget': (
        "I'm searching the learning rate and dropout of a small Flax MLP nowcaster. Each "
        'trial trains for up to 200 epochs, and I can afford about 60 trials. How do I '
        'set the trial budget, prune bad trials early, and use early stopping without '
        'leaking the validation fold?'),
    'N-creative-thinking': (
        "There is something interesting in this county employment panel, but I can't "
        'say what I should even be estimating. Help me work out what the target of the '
        'analysis should be.'),
    'N-recommend-probabilistic-model': (
        'I have monthly counts of business births by county. They are overdispersed '
        'and a third are zero. Which kind of model should I fit?'),
    'N-deep-learning': (
        'My Flax NNX training loss goes NaN after about 2,000 steps with a cosine '
        'schedule and warmup. How do I find the cause and resume training from the '
        'last good checkpoint?'),
    'N-evaluate-deep-learning': (
        'I trained three transformer checkpoints for demand forecasting with different '
        'random seeds. I want to compare them on a held-out test period and decide '
        'which checkpoint to ship.'),
    'N-track-model-experiments': (
        "I've fit five variants for a county-level employment panel: two ridge "
        'regressions and three gradient-boosting models, each scored with the same '
        '5-fold GroupKFold MSE. I keep forgetting which feature set each one used. I '
        'want one record of the variants, ranked on those fold scores.'),
}
V2_FORMAT = ('Reply with REAL or NOISE alone on the first line, then one sentence that '
             'gives the reason.')
V2_PROMPTS = {
    'V2-real': (
        'I tuned the Ridge alpha of a monthly county employment nowcast with Optuna and '
        '5-fold forward-chaining CV. Validation MSE for folds 1 to 5: the default '
        'alpha=1.0 scored 1.20, 0.85, 1.45, 0.95, 1.10. The tuned alpha=8.3 scored '
        '1.18, 0.79, 1.44, 0.87, 1.08. Is the tuned alpha better, or is the '
        'difference noise, so that I should ship the default? ' + V2_FORMAT),
    'V2-noise': (
        'I tuned the Ridge alpha of a monthly county employment nowcast with Optuna and '
        '5-fold forward-chaining CV. Validation MSE for folds 1 to 5: the default '
        'alpha=1.0 scored 1.20, 0.85, 1.45, 0.95, 1.10. The tuned alpha=8.3 scored '
        '1.16, 0.88, 1.40, 0.94, 1.07. Is the tuned alpha better, or is the '
        'difference noise, so that I should ship the default? ' + V2_FORMAT),
}


def _description(text: str) -> str:
    front = text.split('---\n')[1]
    return ' '.join(yaml.safe_load(front)['description'].split())


def base_file(repo: Path, name: str) -> str:
    show = subprocess.run(['git', '-C', str(repo), 'show', f'{BASE}:skills/{name}/SKILL.md'],
                          capture_output=True, text=True, check=True)
    return show.stdout


def v1_system(repo: Path, arm: str) -> str:
    target = (_description((repo / 'skills' / TARGET / 'SKILL.md').read_text())
              if arm == 'variant' else _description(base_file(repo, TARGET)))
    listing = {TARGET: target, **{n: _description(base_file(repo, n)) for n in PROBES}}
    lines = [f'- {n}: {listing[n]}' for n in sorted(listing)]
    return ('You are a coding agent deciding which skill to load for a task. '
            'Available skills:\n' + '\n'.join(lines) + '\nReply with only the name of '
            'the one skill you would load first, or none.')


def v2_system(repo: Path, arm: str) -> str:
    skill = ((repo / 'skills' / TARGET / 'SKILL.md').read_text()
             if arm == 'variant' else base_file(repo, TARGET))
    return ('You are a coding agent helping a user. You have loaded this skill, and you '
            'follow it:\n\n' + skill)


def run_rep(system: Path, prompt: str, folder: Path) -> dict:
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    env = {**os.environ, 'CLAUDE_CODE_DISABLE_ADVISOR_TOOL': '1'}
    proc = subprocess.run(
        ['claude', '-p', '--model', 'sonnet', '--tools', '', '--strict-mcp-config',
         '--no-session-persistence', '--system-prompt-file', str(system),
         '--output-format', 'stream-json', '--verbose', prompt],
        cwd=folder, env=env, capture_output=True, text=True, timeout=300)
    rec = {'returncode': proc.returncode, 'raw': proc.stdout}
    for line in proc.stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get('type') == 'system' and event.get('subtype') == 'init':
            rec.update(tools=event.get('tools'), mcp=event.get('mcp_servers'),
                       model=event.get('model'))
        if event.get('type') == 'result':
            usage = event.get('usage') or {}
            rec.update(answer=(event.get('result') or '').strip(),
                       cost=event.get('total_cost_usd'),
                       iterations=[i.get('type') for i in usage.get('iterations') or []])
    return rec


def verdict(test: str, answer: str) -> str:
    '''V1: the routed skill name. V2: the first line, REAL or NOISE.'''
    if test == 'v1':
        return answer.strip().strip('`*. ').lower()
    first = answer.strip().splitlines()[0] if answer.strip() else ''
    return first.strip('`*. ').upper()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('repo', type=Path)
    ap.add_argument('arm', choices=('v1-pilot', 'v1-control', 'v1-variant',
                                    'v2-control', 'v2-variant'))
    ap.add_argument('--reps', type=int, default=5)
    args = ap.parse_args()
    test, arm = args.arm.split('-')
    pilot = arm == 'pilot'
    arm = 'control' if pilot else arm
    system = KIT / f'system-{test}-{arm}.txt'
    system.write_text(v1_system(args.repo, arm) if test == 'v1' else v2_system(args.repo, arm))
    prompts = V1_PROMPTS if test == 'v1' else V2_PROMPTS
    if pilot:
        prompts = dict(list(prompts.items())[:1])
    reps = 1 if pilot else args.reps
    results, voids = [], 0
    for pid, prompt in prompts.items():
        for rep in range(1, reps + 1):
            for attempt in range(3):
                rec = run_rep(system, prompt, Path('/tmp/p67micro') / f'{args.arm}-{pid}-{rep}')
                if rec['returncode'] == 0 and rec.get('answer') is not None:
                    break
                voids += 1
            clean = rec.get('tools') == [] and rec.get('mcp') == [] and all(
                i == 'message' for i in rec.get('iterations', []))
            (KIT / 'raw').mkdir(exist_ok=True)
            (KIT / 'raw' / f'{args.arm}-{pid}-{rep}.jsonl').write_text(rec.pop('raw'))
            results.append({'arm': args.arm, 'prompt': pid, 'rep': rep, 'clean': clean,
                            'verdict': verdict(test, rec.get('answer', '')), **rec})
            print(f"{args.arm} {pid} {rep}: {rec.get('answer')!r} clean={clean}")
    (KIT / f'results-{args.arm}.json').write_text(json.dumps(
        {'voids': voids, 'results': results}, indent=2))
    print('cost', round(sum(r.get('cost') or 0 for r in results), 3), 'voids', voids)
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

The prompts, the fixtures and the pass rules are fixed here, before any arm runs. The kit's prompt builders were checked at plan time (the V1 listing is six skills in name order; the V2 control system prompt is 10,541 characters).

The fixtures, as per-fold differences d = default − tuned (lower MSE is better):

| Prompt | d | mean(d) | SE(Δ) | mean/SE | Default's fold sd |
|---|---|---|---|---|---|
| `V2-real` | 0.02, 0.06, 0.01, 0.08, 0.02 | 0.038 | 0.0136 | 2.80 | 0.233 |
| `V2-noise` | 0.04, −0.03, 0.05, 0.01, 0.03 | 0.020 | 0.0141 | 1.41 | 0.233 |

- [ ] **Step 2: Pilot the isolation**

Run each micro-test command from the worktree root, as one self-contained command (shell state does not carry across Bash calls, and the script finds its kit from its own path):

```bash
uv run ~/.cache/agent-skills/scratch/plan67-micro/run_microtest.py "$(git rev-parse --show-toplevel)" v1-pilot
```

Expected: one line ending `clean=True`, and `results-v1-pilot.json` shows `"tools": []` and `"mcp": []`. If `clean` is False, stop: the run is not isolated, so fix the flags before you spend more.

- [ ] **Step 3: Run both V2 arms**

```bash
uv run ~/.cache/agent-skills/scratch/plan67-micro/run_microtest.py "$(git rev-parse --show-toplevel)" v2-control
uv run ~/.cache/agent-skills/scratch/plan67-micro/run_microtest.py "$(git rev-parse --show-toplevel)" v2-variant
```

Run each arm in the background and wait for its completion notice. Expected: 10 reps per arm, about $0.6 for both arms.

- [ ] **Step 4: Grade by hand against the pre-registered rule**

Read every answer in `results-v2-control.json` and `results-v2-variant.json`. The script's `verdict` field is a convenience: grade each first line yourself.

Pass rule (fixed before the runs):
1. The variant answers `REAL` on `V2-real` in at least 4 of 5 reps (spec V2).
2. The variant answers `NOISE` on `V2-noise` in at least 4 of 5 reps.
3. Every rep is clean (`tools` and `mcp` empty, only `message` iterations). A rep that is not clean is void: rerun it and count it.

The control is expected to answer `NOISE` on `V2-real` (spec V2). Record its count. It is not a pass condition. If the control also answers `REAL` in 4 or more reps, write in the record that the fixture did not separate the arms.

If the variant fails, reword the R7 sentence in `SKILL.md` once, keeping the pinned rule (2·SE(Δ), the plain SE). Rerun the variant arm only, record both runs, and commit the rewording on its own (`docs(tune): reword the noise rule after V2`). If the second run also fails, stop and bring both runs to your human partner.

- [ ] **Step 5: Write the record**

Create `specs/verification/67-tune-noise-rule-probe.md` in the shape of `specs/verification/65-track-description-microtest.md`:

- the title `# Plan 67 probe: tune-hyperparameters' paired noise rule (V2)`;
- a header line with the date, the model from the init record, the CLI version, the kit path and the total cost;
- **Design:** the isolation flags, the base commit, the two arms (the whole SKILL.md at `7a8fbaa` against HEAD), the fixture table from Step 1, and the pass rule quoted from Step 4;
- **Prompts:** both prompts, quoted in full;
- **Results:** a table of prompt × arm with the counts of `REAL` and `NOISE` out of 5, and whether each rule held;
- **Per rep:** arm, prompt, rep, the first line, and a quote of at most 15 words from the reason;
- **Verdict:** pass or fail, with any rewording and its rerun.

- [ ] **Step 6: Commit**

Commit only when the record's verdict is pass:

```bash
git add specs/verification/67-tune-noise-rule-probe.md
git commit -m "test(tune): record the V2 noise-rule probe" -m "An agent that loads the new tune text calls the paired 2.8-SE fixture real and the 1.4-SE fixture noise; the record has the control arm beside it (spec V2)."
```

---

### Task 4: The causal sibling line, rpm's knob rows and tune's README row (R12, R12a, R12b)

**Files:**
- Modify: `skills/recommend-causal-design/SKILL.md` (Scope and siblings)
- Modify: `skills/recommend-probabilistic-model/references/model-selection-regularization.md` ("Per-family knobs" table)
- Modify: `README.md` (the `tune-hyperparameters` row)

**Interfaces:**
- Consumes: Tasks 1–2 (the README row describes them).
- Produces: nothing a later task reads.

- [ ] **Step 1: Confirm the anchors (the failing check)**

```bash
grep -c 'tune-hyperparameters' skills/recommend-causal-design/SKILL.md
grep -c 'spline terms\|AR terms' skills/recommend-probabilistic-model/references/model-selection-regularization.md
grep -c 'no skill owns the dynamax optax knob yet' README.md
```

Expected: `0`, `0`, `1`.

- [ ] **Step 2: Add causal's sibling line (R12)**

In `skills/recommend-causal-design/SKILL.md`, Old:

```markdown
- Use `develop-testing-strategy` for downstream computational/model tests;
  use `validate-data` for data/result QA.
```

New:

```markdown
- Use `develop-testing-strategy` for downstream computational/model tests;
  use `validate-data` for data/result QA.
- Use `tune-hyperparameters` only to tune nuisance learners (propensity and
  outcome models) inside cross-fitting folds. Predictive CV never selects the
  design, the adjustment set, an RD bandwidth, synthetic-control weights or
  the effect estimate.
```

- [ ] **Step 3: Add rpm's spline-knot and AR-order rows (R12a)**

In `skills/recommend-probabilistic-model/references/model-selection-regularization.md`, Old:

```markdown
| `regression-glm` | which predictors; penalty λ | ridge/lasso/elastic-net/horseshoe; CV or LOO-ELPD |
```

New:

```markdown
| `regression-glm` | which predictors; penalty λ | ridge/lasso/elastic-net/horseshoe; CV or LOO-ELPD |
| `regression-glm` (spline terms) | number and placement of knots | more knots fit closer, then overfit: choose the count by CV or LOO-ELPD, or put a knot at every point and add an ℓ2 penalty (smoothing spline) — PML1 §11.5.2, PML1 §11.5.3 |
```

Old:

```markdown
| `timeseries-statespace` | latent dim, STS components, HMM `K`; `Q`/`σ²` | noise variances as smoothing; **rolling-origin** CV / marginal lik |
```

New:

```markdown
| `timeseries-statespace` | latent dim, STS components, HMM `K`; `Q`/`σ²` | noise variances as smoothing; **rolling-origin** CV / marginal lik |
| `timeseries-statespace` (AR terms) | AR order `p` | rolling-origin CV or LFO over `p = 0, 1, 2, …`; AIC/BIC as a quick screen of point fits |
```

- [ ] **Step 4: Rewrite tune's README row (R12b)**

In `README.md`, replace the whole line that starts `| [`tune-hyperparameters`](skills/tune-hyperparameters/) |` with:

```markdown
| [`tune-hyperparameters`](skills/tune-hyperparameters/) | Tune any model's knobs without leakage or overfitting: sklearn, boosting, statsmodels, NumPyro, dynamax and neural models. First classify the *regime*: predictive search (regime A), inference diagnostic (regime B) or structural choice (regime C), such as the number of mixture components or an AR order. Then tune the right objective with the right guard. For regime A, a table picks the cross-validation splitter from the data's dependence structure: independent, grouped, spatial or temporal. For temporal data, the skill bundles a `PurgedTimeSeriesSplit` (`time_series_cv.py`). It gives forward-chaining cross-validation with an embargo gap and an optional label-horizon *purge*. Given each row's period, it splits whole periods, so it also works on a panel. It feeds a manual, seeded **Optuna** objective (verified against the installed version), with nested cross-validation for large searches and a neural search loop: a trial budget, pruners, early stopping inside the training fold, and seed replication. A paired per-fold rule says when a gain is noise. For regime B, a thin decision table routes the NUTS and SVI knobs to `bayesian-workflow`, and the skill owns the optax learning rate of non-neural point fits. The skill guards **temporal** leakage only. It graduates a tuned winner to a `track-model-experiments` variant row with a `scores.json` that the comparator ranks in score mode, and it leaves revision and vintage leakage to `develop-testing-strategy`. |
```

- [ ] **Step 5: Run Gate A and the lints**

`verify_citations.py` reads `build/.scratch/` beside itself, and that directory exists only in the main checkout. Copy it in (a real copy, never a symlink), then check that git ignores it:

```bash
MAIN_ROOT="$(git worktree list --porcelain | head -1 | cut -d' ' -f2)"
[ -d build/.scratch ] || cp -R "$MAIN_ROOT/build/.scratch" build/.scratch
git status --porcelain build/
uv run --python 3.13 python build/verify_citations.py skills/recommend-probabilistic-model/
uv run --python 3.13 --with pyyaml python build/check_conformance.py
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies; cd ..
```

Expected: `git status` prints nothing for `build/`. `verify_citations.py` exits 0. It prints two existing chapter-fallback WARN lines for `families/regression-glm.md` (PML1 §13.2.4.4, PML2 §14.3.2.1, plan 64's deferred item), and no line names `model-selection-regularization.md`. The other two lints exit 0. If the main checkout has no `build/.scratch/`, stop and ask: rebuilding it needs the owner's local PDFs.

- [ ] **Step 6: Commit**

```bash
git add skills/recommend-causal-design/SKILL.md skills/recommend-probabilistic-model/references/model-selection-regularization.md README.md
git commit -m "docs: route causal nuisance tuning to tune, add rpm knob rows, rewrite tune's README row" -m "recommend-causal-design names tune-hyperparameters for nuisance learners inside cross-fitting only (spec R12). rpm's per-family knob table gains spline-knot and AR-order rows; the spline row cites PML1 sections that Gate A resolves (R12a). The README's tune row describes three regimes, the splitter table, neural search and graduation to a score-mode ledger (R12b)."
```

---

### Task 5: tune's description and its micro-test (R1, V1 tune arm)

The description ships only after the V1 tune arm passes. Until then, the edit stays uncommitted in the working tree. The commit in Step 5 belongs to this task's dispatch: a commit approved later by message has been refused before.

**Files:**
- Modify: `skills/tune-hyperparameters/SKILL.md` (frontmatter `description` only)
- Create: `specs/verification/67-tune-description-microtest.md`
- Kit: `~/.cache/agent-skills/scratch/plan67-micro/run_microtest.py` (Task 3)

**Interfaces:**
- Consumes: Tasks 1–2 (the description names what they built), Task 3's kit.
- Produces: nothing a later task reads.

- [ ] **Step 1: Write the draft description**

Replace the frontmatter `description: >` block (the folded lines under it, up to `license: MIT`) with:

```yaml
description: >
  Use when tuning any model's knobs without leaking or overfitting — sklearn and
  boosting models, statsmodels, NumPyro and dynamax fits, or neural nets from
  deep-learning. Trigger on: "which hyperparameters", searching regularization
  strength, tree depth, or learning rate; grid/random/Optuna search; choosing a
  CV splitter for grouped, spatial, or independent rows; temporal data —
  rolling-origin / walk-forward / purged / embargoed CV and future leakage;
  structural choices such as the number of mixture components, factors, or HMM
  states, AR order, spline knots, or kernel form; inference knobs (NUTS
  target_accept / max_tree_depth, SVI learning rate/steps); early stopping,
  pruning, or a trial budget; when NOT to tune; or graduating a tuned winner to
  a compared variant. Guards temporal leakage; revision/vintage leakage belongs
  to develop-testing-strategy.
```

(860 characters once folded, under the 1,024 cap. It drops "for a nowcasting/tabular model" and "dynamax optax SGD", per R1 and D4.)

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 --with pyyaml python build/check_conformance.py
```

Expected: both exit 0 (`check_frontmatter.py` may print its existing WARN for `writing-skills`). Do not commit yet.

- [ ] **Step 2: Check that the probes have not moved, then run both V1 arms**

```bash
for n in creative-thinking deep-learning evaluate-deep-learning recommend-probabilistic-model track-model-experiments; do git diff --quiet 7a8fbaa HEAD -- skills/$n/SKILL.md && echo "$n same" || echo "$n CHANGED"; done
```

Record the result in the record's Design section. A `CHANGED` line means another change moved a probe description since the base. The kit still uses the base text, as the spec asks ("taken from the files at plan time"); note the drift in the record.

```bash
uv run ~/.cache/agent-skills/scratch/plan67-micro/run_microtest.py "$(git rev-parse --show-toplevel)" v1-control
uv run ~/.cache/agent-skills/scratch/plan67-micro/run_microtest.py "$(git rev-parse --show-toplevel)" v1-variant
```

Run each arm in the background (40 calls in a row) and wait for its completion notice. Expected: 40 reps per arm, about $0.02 each (about $1.60 in total).

- [ ] **Step 3: Grade by hand against the pre-registered rule**

Read every answer in `results-v1-control.json` and `results-v1-variant.json`. Grade each answer yourself, and quote any answer that is more than a bare skill name.

Pass rule (spec V1, fixed before the runs):
1. On each trigger prompt (`T1`–`T3`), the variant's count of answers that route to `tune-hyperparameters` is at least the control's count minus 1.
2. On each near-miss prompt (`N-…`), the variant's count that routes to `tune-hyperparameters` is at most the control's count: no near-miss newly routes to the target.
3. Every rep is clean (`tools` and `mcp` empty, only `message` iterations). A rep that is not clean is void: rerun it and count it.

If the variant fails, reword the description once. Aim at the failing prompt, and keep every R1 trigger. Rerun the variant arm only, and record both runs. If the second run also fails, stop and bring both runs to your human partner. The description does not ship on a failed run.

- [ ] **Step 4: Write the record**

Create `specs/verification/67-tune-description-microtest.md` in the shape of `specs/verification/65-track-description-microtest.md`:

- the title `# Plan 67 micro-test: tune-hyperparameters' description (V1, tune arm)`;
- a header line with the date, the model from the init record, the CLI version, the kit path and the total cost;
- **Design:** the isolation flags, the base commit, the arms, the listing (six skills in name order), the probe-drift check from Step 2, and the pass rule quoted from Step 3;
- **Prompts:** the eight prompts, quoted in full;
- **Results:** a table of prompt × arm with the routed count out of 5, and whether each rule held;
- **Per rep:** arm, prompt, rep and answer (an answer is a skill name, so quote it whole);
- **Verdict:** pass or fail, with any rewording and its rerun.

- [ ] **Step 5: Commit**

Commit only when the record's verdict is pass:

```bash
git add skills/tune-hyperparameters/SKILL.md specs/verification/67-tune-description-microtest.md
git commit -m "docs(tune): widen the description to any model's knobs" -m "Rewrites tune-hyperparameters' description for any producer, the splitter choice, structural choices, early stopping and trial budgets, and drops 'dynamax optax SGD' (spec R1, D4). The V1 tune arm passed against the base description; the record is specs/verification/67-tune-description-microtest.md."
```

---

### Task 6: Stage gates

**Files:** none changed, unless a gate fails.

- [ ] **Step 1: Run every V3 Stage A gate and the commit lints**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_snippets.py skills/
uv run --python 3.13 python build/run_suites.py tune-hyperparameters --extras
git diff --quiet 7a8fbaa HEAD -- skills/tune-hyperparameters/scripts/ && echo 'tune scripts unchanged'
uv run --python 3.13 python build/verify_citations.py skills/recommend-probabilistic-model/
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies; cd ..
build/run_commit_lints.sh
```

Expected: each exits 0. The tune suite passes with the same count as on the base commit (this plan adds no test, +0), and `tune scripts unchanged` prints. Gate A prints only its two existing WARN lines.

- [ ] **Step 2: Check the scope fence and the roadmap Exit**

```bash
git fetch -q origin
git diff --stat origin/main...HEAD -- skills/track-model-experiments skills/develop-testing-strategy skills/validate-data skills/recommend-visualization skills/recommend-probabilistic-model/references/reporting.md skills/tune-hyperparameters/scripts
f=skills/recommend-causal-design/SKILL.md; diff <(git show 7a8fbaa:$f | awk 'NR==1||/^---$/{c++} c<2') <(awk 'NR==1||/^---$/{c++} c<2' $f) && echo 'causal frontmatter unchanged'
git diff --name-only origin/main...HEAD -- 'skills/*/SKILL.md'
```

Expected: the first command prints nothing, and the second prints `causal frontmatter unchanged`. The third lists only `skills/recommend-causal-design/SKILL.md` and `skills/tune-hyperparameters/SKILL.md`; tune's is the one description this plan changes. The three-dot form diffs this branch's own commits only.

Check each item of the roadmap's Stage 2 Exit, and write the evidence into the execution ledger:
- `check_frontmatter.py`, snippet Tier 1, the tune suite with `test_time_series_cv.py` unchanged, Gate A, the dependency-drift test and `build/run_commit_lints.sh` pass (Step 1);
- `specs/verification/67-tune-description-microtest.md` (V1 tune) and `specs/verification/67-tune-noise-rule-probe.md` (V2) exist with a pass verdict;
- the deferred-item ticks are left to the Plan Completion Protocol (step 3), in section `59-model-skill-comparator-and-cv-fixes`: tick the optax-description item (`→ done in plan 67`); tick "Two doc nits left by plan 59's final review" (part (a) was done in plan 65, part (b) in plan 67: tune's Graduation now agrees with track's When to use); add a progress note to "Watch tune's Regime B router wording" (the `target_accept` row and the router sentence are byte-identical, so the item stays open). "Three nits in the splitter's tests" stays open.

Then run the Plan Completion Protocol (writing-plans). At its step 5, retire the plan only: leave `specs/model-lifecycle.md` in place. Stage 3 still implements that spec, and the roadmap's § Completion retires it after the last stage. Its step 3a writes `## Handoff to later stages` for Stage 3, which consumes only `skills/track-model-experiments/references/predictive-evaluation.md`. That path is unchanged by this stage, so its bullet is expected to say that nothing differs.
