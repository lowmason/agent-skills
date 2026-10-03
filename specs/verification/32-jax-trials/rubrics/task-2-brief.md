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

### Task 2: Deliver and verify the deep-learning skill and its domain references

**Files:** Create `skills/deep-learning/SKILL.md` and all eight training
references in File Structure. Create `specs/verification/32-deep-learning.md`,
`32-jax-cpu.in`, and `32-jax-cpu.txt`. Modify `NOTICE`, `CLAUDE.md`, and
`README.md` for this first new original skill and its verification command.

**Interfaces:**
- Consumes Task 1's CPU marker/runner contract and the approved spec R1–R4,
  R7–R8. Native scientific/geometric paths are exceptions to the default stack.
- Produces the training entry point, six domain reference areas, a pinned CPU
  requirements file, and verified example IDs `nnx-sequence-training`,
  `nnx-checkpoint-resume`, `scientific-solver`, `geometric-equivariance`,
  `generative-objectives`, and `llm-token-masks`.
- Whole-skill handoffs name `evaluate-deep-learning`, `optimize-jax`,
  `develop-testing-strategy`, `validate-data`, `tune-hyperparameters`, and
  `recommend-probabilistic-model` only when their responsibility arises. Do not
  make training depend on another skill's private file or named section.

- [ ] **Step 1: Run and record the no-new-skill application baseline.**

Create the evidence directory and record fresh responses to these verbatim
prompts before creating the skill files. Use five samples for D1; use a fresh
reference/application variation for D2–D4. These are baseline scenarios, not
instructions to implement an application into this repository.

| ID | Verbatim prompt | Manual scoring, withheld from the test agent |
|---|---|---|
| D1 | "Build a small JAX model that predicts the next sample in variable-length sine sequences. Include training, validation, and a checkpoint that lets me resume. Use synthetic data and CPU." | Correct valid-token/example reduction; compatible NNX transforms and optimizer; explicit train/eval and randomness; finite gradients; meaningful tiny-data learning; recovery beyond weights, including next-update parity and stated data progress. |
| D2 | "I want a learnable continuous-time model for irregularly observed trajectories in JAX. Show a small example and explain how to establish that the gradients and fitted behavior are reliable." | Appropriate Equinox/Diffrax path; observation/interpolation contract; solver/tolerances/adjoint; gradient reference; sensitivity under tighter tolerances; no unconditional Bayesian x64 policy. |
| D3 | "Construct a small JAX model on 3D points whose scalar output is invariant to rotations and whose vector output rotates with the input. Show how to validate that claim." | Correct representation/parity/output contracts; e3nn native integration; rotation/inversion checks matching the stated symmetry; permutation tests when aggregation is used; no promise of an undocumented NNX integration. |
| D4 | "Plan JAX adapter fine-tuning followed by preference optimization for a language model. Explain model loading, the data format and loss, and the checks needed before a substantial run." | Supported model/checkpoint/tokenizer mapping; SFT/completion and attention masks; frozen/trainable selection; chosen/rejected semantics and reference log-probabilities; valid-token reductions; no Transformers-v5 FlaxAutoModel promise or assumed TPU access. |

Classify observed gaps before adding guidance. For behavior changes, create a
positive output contract or conditional instruction matching the failure type
and apply the five-sample micro-test protocol. When the controls already satisfy
a criterion, keep its useful reference explanation without adding a new
discipline prohibition. The evidence record distinguishes those dispositions.

- [ ] **Step 2: Resolve the CPU environment used for actual examples.**

Create `specs/verification/32-jax-cpu.in` with these exact package names:

```text
jax
jaxlib
flax
optax
orbax-checkpoint
equinox
diffrax
e3nn-jax
numpy
```

Run from the checkout root:

```bash
uv pip compile --python-version 3.13 specs/verification/32-jax-cpu.in --output-file specs/verification/32-jax-cpu.txt
```

Expected: resolution succeeds and the output records exact compatible versions.
It becomes a verified environment only after Step 5 executes the examples.
If resolution fails, isolate the package/version conflict, choose versions
supported by primary sources, compile again, and record the actual change.
Split by example family only if a reproduced incompatibility requires it; update
every affected command/evidence record rather than claiming one environment
verified all families. Keep Tunix checkpoint/accelerator recipes out of this
small CPU dependency profile unless an actual executable example needs Tunix.

- [ ] **Step 3: Author the main decision procedure and shared references.**

Use this exact frontmatter as the initial discovery candidate:

```yaml
---
name: deep-learning
description: >
  Use when designing, implementing, training, fine-tuning, post-training, or
  diagnosing neural models in JAX, Flax NNX, or Equinox — including sequence,
  scientific, vision, geometric, generative, and language models; custom losses,
  masking, optimizer behavior, unstable learning, or training recovery.
license: MIT
metadata:
  author: Lowell Mason
---
```

The body presents this ordered positive contract, refined only on recorded
application failures:

1. Establish the task/hypothesis, data and compute constraints, baseline,
   objective, evaluation target, and stop condition.
2. Select the domain reference and framework path; preserve an existing project's
   framework when migration does not serve the task.
3. Establish shape/dtype/split/preprocessing/tokenization/mask contracts.
4. Establish parameter/state/randomness/optimizer/schedule/accumulation contracts.
5. Run small structural/numerical and tiny-data learning checks before scaling.
6. Save recovery state with the declared resume guarantee; route comparative
   claims to evaluation and reproduced execution problems to optimization.

`frameworks.md` gives a short decision table: default NNX+Optax+Orbax; native
Equinox/Diffrax scientific path; documented e3nn Linen/Equinox path; supported
Tunix/Qwix adaptation; existing Linen projects retained. Cite primary sources
and label compatibility assumptions rather than cataloging libraries.

`training.md` explains finite inputs/losses/gradients, explicit valid-unit
reduction, train/eval state, RNG progression, optimizer/schedule state,
accumulation/clipping, dtype policy, and checkpoint recovery versus export.
Its two canonical examples meet these concrete contracts:

| Example ID | Required executable checks |
|---|---|
| `nnx-sequence-training` | Small synthetic sequence task with an NNX model and Optax optimizer; use the resolved API's `wrt=nnx.Param` and `update(model, grads)` conventions. For losses `[[1, 100, 100], [3, 5, 100]]` and valid mask `[[1, 0, 0], [1, 1, 0]]`, valid-unit loss is 3. Padding changes do not change it. Test finite gradients and reduction of training loss on a fixed tiny fixture; validation and dropout/state policy are explicit. Treat a batch with no eligible units explicitly rather than interpreting it as perfect performance. |
| `nnx-checkpoint-resume` | Save and restore via the resolved Orbax API using a temporary absolute path and wait for asynchronous save completion. Compare the next loss, parameters, optimizer/step/schedule state, RNG progression, and stated data cursor against an uninterrupted run. Reconstruct static graph/configuration explicitly; a parameter-only equality check is insufficient. |

Do not copy the same example into a script: its canonical code remains in the
Markdown reference. Show complete source there, with the CPU marker and local
imports/fixtures, and execute it unchanged using Task 1.

- [ ] **Step 4: Author all six domain references with explicit loading conditions.**

Each reference starts with when to load it, provides architecture/objective
selection criteria and implementation contracts, names domain failure modes,
and cites primary sources. Keep deeper comparison checks in the evaluation
handoff; the current skill still owns its training correctness checks.

| File | Required reference content and executable coverage |
|---|---|
| `sequences.md` | Recurrent/transformer/state-space choices; forecast horizon and causal inputs; variable lengths, padding, temporal splits; objective/reduction and train/eval behavior. Link to the canonical training example rather than duplicate it. |
| `scientific.md` | Neural ODE/CDE, physics-informed, and neural-operator choices; observation completeness, time/interpolation, solver/tolerances/precision/adjoint and differentiation contracts. `scientific-solver` uses a tiny Equinox vector field with Diffrax, specifies SaveAt/controller/adjoint, checks a finite gradient against an analytic or finite-difference reference and repeats under tighter tolerances. |
| `vision.md` | CNN/ViT selection and shape conventions; classification/segmentation/reconstruction objectives; augmentation fitted/applied on the correct split; normalization, train/eval state, input resolution and validation units. Link to verified primary implementations for scale, without claiming every pretrained vision model has a JAX loader. |
| `geometric.md` | Graph/message-passing versus symmetry-constrained models; scalar/vector parity, irreducible representations, compatible nonlinearities, invariant/equivariant outputs, neighbor/aggregation contracts. `geometric-equivariance` uses a documented e3nn integration and checks declared rotation/inversion behavior and permutation behavior if graph aggregation is present. Describe archived Jraph as compatibility context. |
| `generative.md` | VAE ELBO, invertible-flow density/Jacobian, diffusion denoising, and flow-matching velocity objectives; conditioning and sampling; objective versus output-quality comparison. `generative-objectives` demonstrates a small original JAX objective with an independently calculable limiting case and finite gradients. Other families can be concise equations/contracts and authoritative pointers, avoiding a model zoo. |
| `llm.md` | Autoregressive shifts and masks, tokenizer/special-token/chat-template/checkpoint compatibility; pretraining versus SFT/PEFT/preference/reward choices; supported Tunix/Qwix paths; frozen/reference models, selected trainable leaves, rewards/rollout/advantages, hardware prerequisites. `llm-token-masks` uses synthetic logits/labels and chosen/rejected sequence fixtures to check shift, valid-token/completion reduction, and preference/reference semantics without loading a real checkpoint. Real Tunix/MaxText recipes state their model/accelerator requirements and local verification limits. |

- [ ] **Step 5: Execute syntax/numerical checks, then application checks.**

```bash
uv run --python 3.13 python build/check_snippets.py skills/deep-learning/
JAX_PLATFORMS=cpu uv run --python 3.13 --with-requirements specs/verification/32-jax-cpu.txt python build/check_jax_examples.py skills/deep-learning/
```

Expected: parse and execution exits 0, at least the six specified example IDs
appear, and every selected CPU block passes. Inspect all outputs. Fix API,
assertion, and numerical failures in the example; do not suppress them through
an exemption or loose tolerance. Record actual environment/pins/source hashes.

Run fresh WITH-skill D1–D4 applications using the same conditions as controls.
For behavior guidance, five candidate samples plus the full application gate
are required. Test retrieval with a question asking which reference supports
irregular continuous-time data and which supports equivariant outputs. Add
targeted variants for genuine missing information/gaps, then refine and rerun
the affected checks. A narrative review does not substitute for application.

- [ ] **Step 6: Complete attribution/docs and commit this verified skill.**

Append `deep-learning/` to NOTICE's originals block. Add a provenance paragraph
recording Lowell's original prose/examples and Orchestra coverage inspiration
with its URL; retain third-party license/attribution if actual adaptation occurs.
Append `deep-learning` to CLAUDE.md's single-line originals list and recompute
the written count from NOTICE (one additional original in this task).
Add this README Mine-table row and its original-skill
credit:

```markdown
| [`deep-learning`](skills/deep-learning/) | Design, implement, train, fine-tune, and diagnose neural models in JAX. Uses Flax NNX, Optax, and Orbax by default, with focused sequence, scientific, vision, geometric, generative, and LLM references. |
```

Document the pinned CPU-gate invocation in CLAUDE.md Commands and link the
requirements file from the evidence record. Run frontmatter/provenance lints,
the parse gate, and dependency drift before committing. Commit this skill,
the pin/evidence files, and those documentation changes with message
`feat(skills): add verified JAX deep-learning workflow`.

**Checkpoint:** The entire first skill is application-tested, all six domain
areas are covered, and provenance/discovery checks pass before Task 3 begins.
