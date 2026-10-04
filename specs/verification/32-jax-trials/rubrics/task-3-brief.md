## Global Constraints

Every task includes these constraints. Read `CLAUDE.md` completely and use
`writing-skills` before changing a skill. At execution start use
`using-git-worktrees` and start from the local commit containing this plan and
the spec: the remote default branch may not contain these local commits.
Commands below run from the execution checkout root unless a working directory
is explicitly given. Existing line numbers are orientation; edit by text anchor.

- "there are exactly three new skill entry points."
- "Tabular prediction is outside this first version."
- "All these model paths remain JAX."
- "Guidance stays in the main agent context; do not add model pins or `context: fork`."
- "Keep main bodies navigational and aim for roughly 800–1,500 words each; move substantial domain/API detail into references."
- "Every bundled runnable example is exercised against recorded package versions."
- "Use small CPU fixtures for portable checks."
- "The depth lives in references loaded when relevant" — preserve this structure
  rather than adding modality/library skills.
- Main descriptions start with "Use when" and stay within 1,024 characters.
  Use bare whole-skill handoffs. Do not invent dependencies for those handoffs.
- Python uses single quotes, four-space indentation, and original prose/code.
  Read `build/CLAUDE.md` before modifying build tooling. Do not alter canonical
  agents/commands or generated runtime adapters for this plan.
- Record baseline agent outputs before skill authoring. Behavior guidance needs
  an observed control failure and the `writing-skills` wording/application gates.
  A pure reference uses retrieval/application/gap checks. Do not turn successful
  control behavior into an invented discipline rule.
- Baseline/test agents receive their scenario and realistic runtime/catalog
  context, not this plan, the spec, scoring rubric, or earlier responses. Keep
  those records outside their supplied context. Record actual model, context,
  sources/tools, and trial conditions; do not claim provider aliases ran unless
  the active runtime supports them.
- The methodology-template deferred item remains outside this plan. Do not
  generalize Bayesian experiment-tracking scripts or impose posterior artifacts
  on neural experiments.
- No large checkpoint/dataset downloads or cloud deployment are needed for the
  CPU/application gate. Hardware-dependent recipe support is documented with
  its actual verification limits.
- Other work can land concurrently. Preserve unrelated edits, and calculate
  inventory counts from the current NOTICE block rather than overwriting a
  concurrent addition. This plan adds three originals; its design baseline had
  sixteen, but the written total need not remain nineteen if other skills land.

### Task 3: Deliver and verify neural evaluation and experiment records

**Files:** Create `skills/evaluate-deep-learning/SKILL.md`, the three evaluation
references in File Structure, and `specs/verification/32-evaluate-deep-learning.md`.
Modify `NOTICE`, `CLAUDE.md`, and `README.md` for this second new original skill.

**Interfaces:**
- Consumes R1, R5, R7–R8, Task 1's gate, and Task 2's verified CPU profile.
- Produces a comparison protocol, domain-check map, a documented neural-run
  record, and the executable example ID `paired-evaluation`.
- Does not alter `track-model-experiments` or require Bayesian artifacts.

- [ ] **Step 1: Record fresh no-evaluation-skill controls.**

Use five samples of E1 and fresh variations E2/E3; withhold the rubric.

| ID | Verbatim prompt | Manual scoring |
|---|---|---|
| E1 | "Method A has held-out errors 0.14 and 0.16 for seeds 0 and 1, each trained for one million tokens. Method B has errors 0.13, 0.18, 0.14 and 0.12 for seeds 0–3, each trained for three million tokens. Which method is better, and what evidence should I collect next?" | Identifies unequal budgets and seed/sample comparability; distinguishes observed score from a defensible superiority claim; proposes matched evaluation/ablation; records decision limits instead of using posterior ELPD/ArviZ machinery. |
| E2 | "Compare two sequence models evaluated on overlapping forecast windows. Explain the evaluation units and how I can avoid overstating confidence in the difference." | Temporal split/leakage and dependence; horizon/window definition; appropriate aggregation/resampling units; metrics fixed before interpreting the result. |
| E3 | "A neural ODE's error improves with loose solver settings, and a 3D model is called rotation-equivariant because its loss is low. What checks would substantiate these claims?" | Solver-tolerance/gradient sensitivity and explicit transformation tests; loss alone is not a symmetry proof; predictive uncertainty and run variability remain distinct. |

- [ ] **Step 2: Author the main entry point and protocol.**

Initial frontmatter:

```yaml
---
name: evaluate-deep-learning
description: >
  Use when benchmarking neural models, comparing checkpoints or methods,
  designing ablations, selecting models, or assessing deep-learning research
  claims — including held-out metrics, contamination, leakage, unequal compute
  budgets, variation across seeds, generative quality, or domain correctness.
license: MIT
metadata:
  author: Lowell Mason
---
```

Main output contract: evaluation unit and held-out inputs → metric and
comparison/budget/seed policy → leakage/contamination and domain checks →
results with variation/limitations → evidence-supported decision and next test.
`protocol.md` covers meaningful baselines, comparable tuning budgets, paired
held-out inputs where available, dependent observations, ablations and
prespecified decision criteria. It routes applicable input/conclusion QA to
`validate-data` and search/test-plan responsibilities by bare skill name.

`paired-evaluation` is a self-contained JAX/NumPy fixture with explicitly named
sample and seed axes. It checks valid-token reduction against a manual result,
invariance to changed padding, comparison on identical held-out units, and
preservation of per-seed scores and budget metadata. It does not assert a
universal winner or compute confidence by treating dependent tokens as runs.

- [ ] **Step 3: Author domain checks and the neural-run record.**

`domain-checks.md` maps temporal causality/window dependence; image preprocessing,
augmentation and group splits; graph permutation and declared rotation/inversion
behavior; solver accuracy/gradient sensitivity; generative quality/diversity and
conditioning; and LLM prompt/tokenizer/decoding/contamination comparability to
concrete checks and interpretations. Reference task-specific primary sources.

`experiments.md` uses this documented record schema, with meanings and a small
completed example record rather than a new service or script:

```text
run_id: unique run identifier
parent_run_id: predecessor identifier or null
hypothesis: claim being tested
change: change from parent/baseline
data: immutable source/split identifiers and evaluation units
model: architecture/checkpoint/tokenizer and training configuration
seed: initialization/data/sampling seed policy
environment: Python/packages/platform/backend/devices
artifacts: recovery checkpoint, export, predictions and logs as applicable
metrics: metric names, units, aggregation and values by sample/seed as applicable
budget: tokens/examples/steps, device time and tuning budget as applicable
status: planned, running, completed, failed or superseded
decision: result, limitations and next action
```

Distinguish recovery/export/prediction artifacts. A run without posterior draws
does not need `InferenceData`, NetCDF, ELPD, LOO, or ArviZ.

- [ ] **Step 4: Execute the example and fresh WITH-skill applications.**

```bash
uv run --python 3.13 python build/check_snippets.py skills/evaluate-deep-learning/
JAX_PLATFORMS=cpu uv run --python 3.13 --with-requirements specs/verification/32-jax-cpu.txt python build/check_jax_examples.py skills/evaluate-deep-learning/
```

Expected: exit 0, `paired-evaluation` passes, and all additional selected
examples pass. Record environment/hashes/results. Apply the E1 micro-test and
E1–E3 application criteria; add a generative/LLM comparison retrieval case to
ensure coverage is not limited to supervised scalar scores. Refine from actual
failures and rerun affected checks before the deployment step.

- [ ] **Step 5: Complete attribution/docs and commit.**

Append the new original skill in NOTICE and CLAUDE.md; recompute the written
count from NOTICE (one additional original in this task); append its README
original credit and this Mine-table row:

```markdown
| [`evaluate-deep-learning`](skills/evaluate-deep-learning/) | Evaluate neural models and research claims with explicit held-out inputs, metrics, leakage checks, comparable budgets, seed variation, domain checks, and experiment records. |
```

Run frontmatter/provenance, parse, and dependency-drift checks. Commit this
skill, its evidence, and its docs with message
`feat(skills): add verified deep-learning evaluation`.

**Checkpoint:** Evaluation produces a comparable protocol and honest decision,
with a neural-run record independent of Bayesian posterior artifacts.
