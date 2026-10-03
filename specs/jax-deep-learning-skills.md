# Compact JAX Deep-Learning Skills — Design Spec

**Status: APPROVED (2026-10-03).**
The owner approved both the three-skill design and this written spec after a
brainstorming pass. Implementation is planned in
`specs/plans/32-jax-deep-learning-skills.md`; the skills have not been implemented.

## Purpose and scope

Add a compact set of research skills whose model implementations, gradients,
training steps, and inference run in JAX. Cover general neural-network methods,
sequences and time-series, scientific learning, vision, geometric learning, and
generative/LLM research. The depth lives in references loaded when relevant;
there are exactly three new skill entry points.

The [Orchestra AI Research Skills suite](https://github.com/Orchestra-Research/AI-Research-SKILLs)
is coverage inspiration. This collection uses workflow boundaries and original
JAX guidance and examples; it does not reproduce that suite's library catalog.

Tabular prediction is outside this first version. Arrays, node attributes, and
MLPs remain useful components of the included domains; their representation
does not make them excluded tabular-prediction tasks.

## Decisions and alternatives

1. **Three workflow skills:** `deep-learning`, `evaluate-deep-learning`, and
   `optimize-jax`. A single umbrella skill has an overly broad trigger. A fourth
   `llm-post-training` entry point is unnecessary initially: its specialized
   procedure belongs in a focused reference under `deep-learning`.
2. **A shared default stack:** JAX, Flax NNX, Optax, and Orbax. Use Equinox with
   Diffrax for scientific patterns where their native integration is suitable;
   use e3nn-jax's documented Linen or Equinox integrations for equivariant
   patterns. Existing projects retain their framework unless the task requires
   a justified migration. All these model paths remain JAX.
3. **LLM adaptation through Tunix:** use documented model loaders and algorithms,
   with Qwix where the PEFT recipe requires it. Treat compatibility as a checked
   property of the model, checkpoint, package versions, algorithm, and hardware.
4. **Examples demonstrate reusable patterns:** small executable examples support
   the guidance. The deliverable is a skill collection, not a model zoo,
   application, training framework, benchmark service, or vendored API manual.
5. **Research generation is in scope:** explain sampling and cache correctness,
   then profile and scale an established implementation. MaxText can be an
   optional scale reference. Production hosting and cloud provisioning are
   outside this design.

## Skill boundaries

| Entry point | Trigger | Ownership and output |
|---|---|---|
| `deep-learning` | Designing, implementing, training, fine-tuning, post-training, or diagnosing the learning behavior of a neural model in JAX | A concrete experiment contract and model/training implementation: hypothesis, architecture rationale, objective, data and masking contract, optimizer/schedule, model state, randomness, checkpoint recovery, and learning diagnostics. |
| `evaluate-deep-learning` | Benchmarking, ablation, comparing checkpoints or methods, selecting a neural model, or assessing a research claim | An explicit evaluation protocol and evidence-based comparison: metrics, held-out inputs, contamination/leakage checks, baselines, comparable budgets, seed variation, domain checks, and limitations. |
| `optimize-jax` | Tracing errors, recompilation, memory pressure, slow execution, distributed execution, or generation/inference performance | A reproduced execution problem, profiling evidence, a measured change, and correctness parity. Owns compilation, precision/performance trade-offs, memory, sharding, and generation/cache mechanics. |

For a mixed task, route by the immediate decision and load another skill when
its responsibility arises. A non-learning JAX execution problem can trigger
`optimize-jax`; it does not require the deep-learning workflow. Training quality
and systems performance are evaluated separately even when one change affects
both.

## Requirements

### R1 — Compact packaging and discovery

- Create the three directories under `skills/`, each with `SKILL.md` and
  focused `references/`. Keep main bodies navigational and aim for roughly
  800–1,500 words each; move substantial domain/API detail into references.
- Frontmatter follows `writing-skills`: bare skill names, descriptions beginning
  with "Use when", concrete triggers, and the enforced 1,024-character
  description cap. Guidance stays in the main agent context; do not add model
  pins or `context: fork`.
- Each main body has an explicit boundary, a decision procedure, a quick
  reference, common mistakes, and links to its own supporting references.
  References state when to load them and identify authoritative sources.
- Do not add a separate skill for every domain or library. Add executable
  helpers only when application testing demonstrates a reusable need.

### R2 — Shared training workflow

`deep-learning` establishes the task, compute budget, hypothesis, baseline,
objective, evaluation target, and stopping conditions before a substantial run.
Its training guidance covers:

- Input shapes/dtypes, preprocessing fitted only on training data, split policy,
  tokenization where relevant, and padding/attention/loss masks.
- Correct loss reduction over valid examples or tokens, mutable model state,
  explicit randomness, train/eval behavior, gradients, optimizer state,
  schedules, accumulation, and clipping where justified.
- A small correctness run, tiny-data learning check, finite losses/gradients,
  and diagnostics that distinguish implementation faults from optimization or
  data limitations.
- Recovery state containing model/optimizer state, step/schedule position,
  randomness, and data progress where needed for the stated resume guarantee.
  Distinguish recovery checkpoints from portable model exports.
- Deliberate precision and device choices. Do not inherit an unconditional x64
  default from Bayesian latent-process inference.

The main executable example uses NNX and Optax on a small included-domain task.
Checkpoint guidance uses Orbax's supported APIs and tests the recovery contract.

### R3 — Focused domain references

The training skill has focused coverage of the following families. Teach
selection criteria, implementation contracts, important failure modes, and a
small JAX pattern where useful; do not promise a pretrained implementation of
every named architecture.

| Reference area | Required coverage |
|---|---|
| Sequences and time-series | Recurrent models, transformers, state-space architectures, forecasting objectives, causality, variable lengths, and temporal splits. |
| Scientific learning | Neural ODEs/CDEs, physics-informed models, and neural operators. Use Equinox/Diffrax for the solver-coupled pattern; record observation times, interpolation, solver, tolerance, precision, and adjoint choices. |
| Vision | CNNs/ViTs, task-specific objectives, preprocessing/augmentation and train/eval distinctions, and image-aware validation. |
| Geometric learning | Graph/message-passing models, symmetry and invariant/equivariant output contracts, irreducible representations, parity, and compatible operations through e3nn-jax. Jraph is an existing-project compatibility note, not a new default dependency. |
| Generative learning | VAEs, normalizing flows, diffusion and flow matching; distinguish their objectives and sampling procedures. Cover conditioning and the difference between optimizing a proxy loss and evaluating generated output. |
| LLM pretraining and post-training | Autoregressive objectives, tokenizer/checkpoint compatibility, SFT, LoRA/QLoRA, preference optimization, and reward-based post-training. Use Tunix's documented capabilities with explicit model/hardware prerequisites. |

Scientific and geometric references explain their native framework path rather
than silently switching the default for unrelated tasks. Full domain-specific
correctness and comparison protocols live in the evaluation skill, referenced
by bare skill name.

### R4 — LLM correctness and compatibility

- Check supported architecture and checkpoint mappings before loading a model.
  Hugging Face remains a source of artifacts/tokenizers, but Transformers v5's
  removed JAX/Flax backend is not a supported default execution path.
- Verify tokenizer/special-token/chat-template conventions, token shifts,
  attention and completion masks, sequence log-probability reductions, and
  frozen/trainable parameter selections for the chosen objective.
- Explain when SFT, preference optimization, or reward-based training addresses
  the research objective. Preference references establish chosen/rejected
  semantics and reference-model behavior; reward references establish rollout,
  reward, baseline/advantage, and evaluation contracts.
- Treat CPU/GPU/TPU recipe support separately from local verification. A
  documented algorithm is not evidence that every model/hardware combination
  works. Use small local math/fixture checks without downloading large models;
  identify what a real checkpoint or accelerator test would additionally prove.

### R5 — Evaluation and experiment records

`evaluate-deep-learning` defines the evaluation unit, held-out inputs, metrics,
comparison protocol, seed/budget policy, and decision criterion. It covers
contamination and leakage, meaningful baselines, ablations, comparable tuning
budgets, and uncertainty in differences. A single favorable run is not a
universal performance claim.

Its domain checks include temporal causality, image preprocessing/augmentation,
graph permutation and specified rotation/inversion behavior, solver-tolerance
sensitivity, generative quality/diversity, and LLM prompt/tokenizer/decoding
comparability. Distinguish predictive uncertainty from variation across runs.

Use a small backend-neutral experiment-record contract: run/parent identity,
hypothesis/change, data/split and model configuration, seed/environment,
checkpoint/artifact locations, metrics/budget, status, and decision. Do not
require ArviZ, `InferenceData`, ELPD/LOO, or posterior artifacts for neural runs.
This first version documents the contract without adding a new tracking service
or generalizing the existing Bayesian ledger scripts.

### R6 — JAX performance and inference

`optimize-jax` reproduces and profiles the relevant execution before recommending
a change. Cover traced/static values, PyTrees and model-state transformations,
shape-dependent compilation, data movement, batching, rematerialization,
precision, and sharding/distributed state.

Timing separates compilation from steady-state execution and synchronizes
asynchronous JAX work. Compare the stated workload and hardware before/after,
including memory when it motivates the change. Validate outputs and gradients
where the optimized path trains; use tolerances appropriate to the precision.

Generation guidance covers prefill/decode, explicit KV-cache state, masks,
positions, capacity, termination, randomness, and shape-dependent recompilation.
Start with a small JAX-native research path; introduce supported MaxText scale
patterns when the workload warrants them. Model execution remains JAX even when
host-side artifact loading, tokenization, or orchestration uses other libraries.

### R7 — Existing skill integration and routing

- Use `develop-testing-strategy` for permanent test-plan design,
  `validate-data` for applicable input/conclusion QA, and `tune-hyperparameters`
  for appropriate search discipline. Supply neural/domain-specific checks;
  do not blindly transfer Bayesian or table-specific assumptions.
- Use `recommend-probabilistic-model` when comparing a neural proposal against
  probabilistic alternatives. Route actual posterior inference to
  `bayesian-workflow`.
- Narrow `bayesian-workflow`'s standalone JAX trigger so ordinary neural or JAX
  execution work does not load Bayesian guidance solely because JAX is named.
  Preserve discovery for NumPyro, BlackJAX, and explicit posterior-inference
  tasks, including Bayesian neural networks when inference is the task.
- Keep `track-model-experiments`' Bayesian artifact/comparator contract intact.
- Use whole-skill handoffs by bare name. If authored text requires another
  skill's file or named section, update `install.py`'s `DEPENDENCIES` or the
  justified `SOFT_REFERENCES` entry and pass dependency-drift verification.
- The deferred DL/NLP methodology-template extension in
  `specs/deferred_items.md` remains outside this design: it requires a concrete
  methodology target, not merely the addition of DL guidance.

### R8 — Provenance and repository documentation

Write original prose and code grounded in primary documentation/papers. Record
the Orchestra inspiration and the new original skills in `NOTICE`; update the
originals list/count in `CLAUDE.md` and the skill/credits descriptions in
`README.md`. The existing Bayesian skill retains its attribution.

The Orchestra suite is MIT licensed. Any directly adapted material must retain
the applicable upstream copyright/license and state its modifications. Do not
vendor manuals, papers, model weights, datasets, or documentation dumps. A
library's code license does not establish a checkpoint or dataset's license.

No canonical agent or command changes are required, so no generated runtime
adapter changes are expected.

## Validation and acceptance

Follow `writing-skills` for each skill separately. Complete its baseline,
authoring, application checks, and refinement before moving to the next skill.
Reference retrieval/application checks do not need discipline pressure tests;
behavior-shaping additions use the required no-guidance controls and wording
micro-tests. Preserve durable evidence under `specs/` following repo conventions.

Application scenarios collectively exercise:

1. An NNX training task with state/randomness/masking and a resumable checkpoint.
2. A scientific solver-coupled task with meaningful tolerance/gradient checks.
3. A geometric task with the specified invariance/equivariance behavior.
4. An LLM adaptation task with checkpoint/tokenizer, objective, mask, and
   reference/trainable-state contracts.
5. A model comparison where leakage, seed variation, or unequal budgets could
   invalidate the conclusion.
6. A JAX performance/inference task with compilation, synchronization, cache
   correctness, and numerical parity.
7. Routing counterexamples: bare JAX/non-Bayesian training versus actual
   posterior inference, and evaluation/performance requests versus training.

Every bundled runnable example is exercised against recorded package versions.
Use small CPU fixtures for portable checks. Parsing alone does not establish API
or numerical correctness. Additional GPU/TPU or real-checkpoint checks are
reported with their actual scope; unavailable hardware must not be represented
as verified. Integrate a focused execution harness with the existing build
tooling if needed; do not widen its Bayesian-only API/run gate by assertion.

Before completion, run and inspect:

- `build/check_frontmatter.py` with the repository's Python 3.13/PyYAML command.
- `build/check_provenance.py`.
- Parse-only `build/check_snippets.py skills/`.
- Directory-scoped runtime-support tests, including declared dependency drift,
  and `build/sync_runtime_assets.py --check`.
- The new examples' execution/application checks and any changed build tests.
- `git diff --check`.

Acceptance requires exactly three discoverable skills with distinct routing,
coverage of all included domain areas, correctly executed JAX examples, passing
repository checks, recorded application evidence, and explicit limits on claims
that require untested hardware/checkpoints. Apply the existing plan-completion
protocol when implementation finishes.

## Sources and verification notes

Primary sources reviewed during design on 2026-10-03; package pins are chosen
and recorded during implementation, not inferred from unversioned docs.

- [Orchestra suite](https://github.com/Orchestra-Research/AI-Research-SKILLs) and
  [MIT license](https://github.com/Orchestra-Research/AI-Research-SKILLs/blob/main/LICENSE).
- [Flax](https://flax.readthedocs.io/en/stable/) recommends NNX for new users and
  retains Linen support; [NNX basics](https://flax.readthedocs.io/en/stable/nnx_basics.html).
- [Optax](https://optax.readthedocs.io/en/latest/) and
  [Orbax checkpointing](https://orbax.readthedocs.io/en/latest/guides/checkpoint/orbax_checkpoint_101.html).
- [Equinox](https://docs.kidger.site/equinox/), Diffrax
  [neural ODE](https://docs.kidger.site/diffrax/examples/neural_ode/),
  [neural CDE](https://docs.kidger.site/diffrax/examples/neural_cde/), and
  [adjoint guidance](https://docs.kidger.site/diffrax/api/adjoints/).
- [e3nn-jax](https://github.com/e3nn/e3nn-jax), its
  [Flax integration](https://e3nn-jax.readthedocs.io/en/latest/api/flax.html), and
  [equivariance checks](https://e3nn-jax.readthedocs.io/en/latest/api/utils.html).
  [Jraph](https://github.com/google-deepmind/jraph) is archived.
- Tunix [algorithms](https://tunix.readthedocs.io/en/latest/algorithms.html),
  [models](https://tunix.readthedocs.io/en/latest/models.html),
  [rollout/generation](https://tunix.readthedocs.io/en/latest/rollout.html), and
  [GPU PEFT example](https://tunix.readthedocs.io/en/latest/_collections/examples/qlora_llama3_gpu.html);
  [Qwix](https://github.com/google/qwix).
- [Transformers v5 migration](https://github.com/huggingface/transformers/blob/main/MIGRATION_GUIDE_V5.md)
  documents removal of its JAX/Flax backend. MaxText documents
  [checkpoint conversion](https://maxtext.readthedocs.io/en/maxtext-v0.2.4/guides/checkpointing_solutions/convert_checkpoint.html)
  and [inference](https://maxtext.readthedocs.io/en/latest/tutorials/inference.html);
  the documented scale/hardware assumptions are not local verification.
- Tabular is excluded despite recent progress:
  [TabPFN-3.5 report](https://priorlabs.ai/technical-reports/tabpfn-3-5) and its
  [current PyTorch implementation](https://github.com/PriorLabs/TabPFN).
