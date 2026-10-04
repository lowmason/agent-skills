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

### Task 5: Narrow Bayesian discovery and verify the catalog boundaries

**Files:** Modify only the description in `skills/bayesian-workflow/SKILL.md`;
create `specs/verification/32-bayesian-routing.md`.

**Interfaces:**
- Consumes the complete three-skill catalog, R7, and the existing Bayesian
  description. Produces a minimally narrowed description and routing evidence.
- Preserve `NumPyro (JAX)`, BlackJAX, MCMC/NUTS, posterior terminology, and the
  Bayesian body/license/metadata. No Bayesian precision policy is generalized.

- [ ] **Step 1: Run the current-description selection baseline.**

Use a realistic full catalog with the current Bayesian description and the new
three descriptions. In fresh contexts ask which guidance to load, then let the
agent retrieve it and explain the choice. Use at least five samples per
current/candidate condition for these prompt families:

1. "Train an NNX sequence model in JAX using synthetic data."
2. "Compare neural checkpoints trained with different budgets and seeds."
3. "Fix recompilation in a non-learning JAX calculation."
4. "Infer a Bayesian neural-network posterior with NumPyro and NUTS."
5. "Use BlackJAX to sample a posterior distribution."
6. "Improve generation speed while checking KV-cache correctness."

Expected primary choices, withheld from test context: deep-learning, evaluation,
optimization, Bayesian, Bayesian, optimization respectively. Record actual
selected/read skills, rationale, and whether a runtime's real auto-loading was
observed or this was a catalog-selection simulation. Do not call a literal
substring test or `build/smoke_test.py` a routing test.

- [ ] **Step 2: Apply the approved minimal textual narrowing.**

Replace this exact description substring:

```text
Pyro, JAX, BlackJAX, ArviZ, InferenceData
```

with:

```text
Pyro, BlackJAX, ArviZ, InferenceData
```

This removes only the standalone JAX trigger; `NumPyro (JAX)` still identifies
the Bayesian stack. If controls already choose correctly, record that result:
the approved spec still narrows the textual trigger, but there is no measured
over-trigger improvement to claim. Add no larger wording rule without an
observed gap and the authoring gate.

- [ ] **Step 3: Repeat matched candidate selection and compatibility checks.**

Run the same prompt families against the edited catalog, five fresh samples
each. Read every output, verify preservation of posterior discovery and absence
of Bayesian loading solely from bare JAX in ordinary neural/execution work.
If selection still fails, isolate the conflicting trigger before proposing a
broader change; record any necessary spec deviation explicitly.

Run frontmatter lint and the parse gate for `skills/bayesian-workflow/`. No body
or executable Bayesian example changed, so a full MCMC snippet run is not needed
for this metadata edit. Commit the description and evidence with message
`fix(skills): narrow Bayesian JAX discovery trigger`.

**Checkpoint:** Catalog tests distinguish learning, evaluation, execution, and
actual posterior inference, with honest limits on auto-loading evidence.
