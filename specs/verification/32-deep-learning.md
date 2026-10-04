# Deep-learning skill verification

Status: application gate complete for the stable refined skill; six canonical
CPU examples have unchanged verified source hashes. Final repository checks
and the scoped commit are recorded below. Task 2 of the approved
[JAX deep-learning spec](../completed/jax-deep-learning-skills.md) and
[implementation plan](../plans/completed/32-jax-deep-learning-skills.md).

## Baseline and wording dispositions

The controller completed the eight matched controls before this skill was
created. The durable [manual control scoring](32-jax-trials/D-control-scoring.md)
reads all five D1 responses and the D2–D4 responses against the withheld rubric.
Trial prompts explicitly allowed complete code without session execution; the
baseline scores assess delivered artifacts, not execution. Matched runtime
conditions are fresh Claude sessions, requested Sonnet/medium, read-only tools;
actual records include Sonnet and Opus for D1/D2/D4 and Sonnet for D3. The
separate native D1 supplement is informative and excluded from matched counts.

| Observation | Authoring disposition |
|---|---|
| All five D1 controls correctly shift targets, reduce over valid timesteps, use coherent plain-JAX transforms, distinguish evaluation, and save optimizer/step/RNG | Preserve useful explanations and compatible existing-framework paths; no fabricated masking, NNX, or weights-only failure. |
| All five omit explicit finite-gradient and fixed tiny-fixture learning assertions | Required output/check slots in the correctness run. Gradients/learning were not observed to fail. |
| All five omit or only partly propose recovery-next-update parity/configuration validation | Required recovery guarantee and next-loss/parameters/optimizer/step/RNG/data-progress comparison. Preserve actual saved state and honest epoch/save-best limits. |
| D2 uses global timestamp membership instead of per-trajectory observations | Conditional observation-grid/mask contract with hand-checkable shape/count and unobserved-value invariance. Preserve Equinox/Diffrax, adjoint, gradient-reference, and tolerance checks. |
| D3 has valid direct-JAX scalar/vector algebra and proper-rotation checks | Preserve mathematical validity; supply native e3nn reference coverage and conditional inversion/permutation checks for the claimed symmetry/aggregation. |
| D4 gives useful SFT shifts/reductions and DPO math, but contradicts its SFT-reference identity and rejects legitimate initial LoRA gradients | Conditional immutable-reference identity and selected-update/frozen-parameter checks, plus a concrete supported checkpoint/tokenizer/hardware recipe. Preserve correct masks and the policy=reference zero point. |

These are omissions and observable conditional errors. The skill uses positive
contracts and conditional instructions. It adds no pressure rationalization
rules or prohibitions inferred from successful controls. The controller subsequently supplied five fresh D1 candidate samples and
D2–D4/retrieval checks with complete independent scoring. The preserved first
round and the refined native cohort are described separately below.

## Numerical test strategy (recorded before checks)

This applies develop-testing-strategy to neural examples by stating invariants
first. Tests use complete original canonical Markdown blocks and the Task 1
runner without a hidden preamble, repository fixtures, checkpoint downloads, or
network. The smallest falsifying layer is an isolated CPU subprocess per block.
No new pytest marker is needed: the explicit `cpu-example` marker selects the
opt-in numerical gate; existing process-contract pytest tests remain fast and
independent of the scientific stack.

| ID | Structural/relational/bounds/reproducibility invariants | Fixture and assertion plan |
|---|---|---|
| `nnx-sequence-training` | Eligible targets follow next-step shift; valid-unit weighting is explicit; padding is inert; empty eligible batches are rejected before update; losses/gradients are finite; fixed data can be learned; evaluation is deterministic | Original small variable-length sine waves, two causal lag features, an NNX MLP and Optax. Hand losses `[[1,100,100],[3,5,100]]` with mask `[[1,0,0],[1,1,0]]` give 3; change padded losses and retain 3. Assert all gradient leaves finite and fixed-fixture final loss below 20% of initial loss after a bounded tiny run. Use independent fixed validation phases; dropout/state policy explicit. |
| `nnx-checkpoint-resume` | Full recovery has next-update parity, static configuration agreement, optimizer/schedule progression, PRNG progression and next-data cursor agreement | Separate complete NNX sine-lag fixture with Adam/schedule and stochastic input augmentation; temporary absolute Orbax directory. Save all dynamic model/optimizer state plus training key/cursor and original configuration. Wait for async completion, reconstruct static model/optimizer, restore public State APIs. Compare pre-update recovery and next loss/parameters/all optimizer leaves/step/schedule/key/cursor; same platform/pins, allclose 1e-6 for floating leaves and exact integer/key/cursor equality. |
| `scientific-solver` | Per-trajectory observation mask/count is correct; values at unobserved times are inert; solver outputs/gradients are finite; analytic dynamics and gradient agree; tighter tolerances preserve fitted predictions | Tiny Equinox scalar rate field and Diffrax exponential ODE, two irregular observation sets on one grid, explicit SaveAt/Tsit5/PID/RecursiveCheckpointAdjoint. Hand mask/count and changed-unobserved checks. Float64 is selected for this analytic numerical fixture only. Compare objective derivative to closed-form derivative (absolute/relative <= 2e-5 for initial solve, <= 2e-7 for tighter solve); fit rate on fixed observations and check final loss <1% of initial, fitted rate near truth and tight-solve predictions within 2e-5. |
| `geometric-equivariance` | Declared even scalar and polar vector follow O(3) rotation/inversion behavior; global aggregation is permutation-invariant; finite gradients preserve learnability | Original point cloud, documented e3nn Equinox Linear from `1o` to `1o`, invariant radial weights and scalar head. Several explicit proper rotations, inversion, and permutation; compare at float32 tolerances 1e-5; require nontrivial scalar/vector and finite gradient leaves. |
| `generative-objectives` | Denoising objective matches an independent limiting value; perfect predictor has zero loss; parameter gradients are finite and agree with a hand expression | Original small diffusion noise/clean arrays, alpha-bar=0 noise limit and scalar velocity-free noise predictor. Assert constant-zero predictor loss equals hand-computed 2.5, exact predictor loss is zero, and derivative agrees with analytic scalar expression; cover conditioning shape in prose. |
| `llm-token-masks` | Causal shift picks next tokens; padding/prompt masks do not count; empty shifted completions are explicit; completion CE pools valid tokens; preference sequences use sums; policy=reference gives log(2); improving chosen/rejected margin lowers DPO loss; frozen base leaves stay equal | Synthetic tiny logits/tokens with unequal completion lengths and padding, chosen/rejected pairs, immutable reference log-probabilities. Hand-computable uniform-logit CE and explicitly favored next-token logits; changed-padded/prompt logits are inert. Original two-factor LoRA fixture shows dA=0 with B=0, dB nonzero, selected update changes B and leaves base weights fixed. |

The exact gate, run from the checkout root, is:

```bash
JAX_PLATFORMS=cpu uv run --python 3.13 --with-requirements specs/verification/32-jax-cpu.txt python build/check_jax_examples.py skills/deep-learning/
```

The [nine-name input](32-jax-cpu.in) and [compiled full profile](32-jax-cpu.txt)
record exact resolution. Parser, finite-gradient, mathematical-reference,
learning, and recovery gates answer different questions; an import smoke test
or parser success does not replace these numerical checks. Tolerances are tied
to the small fixture's dtype and analytic/parity references, not widened to
suppress a failing example.

## Authoring and deployment checklist

- [x] Approved scope/spec/plan and maintainer guide read; designated worktree clean.
- [x] No-skill controls and complete manual dispositions read before authoring.
- [x] Numerical strategy and smallest fixtures recorded before check code.
- [x] Initial discovery frontmatter; navigational body and eight own references.
- [x] Exact profile compiled and all six canonical blocks executed unchanged.
- [x] Primary sources refreshed; hardware/checkpoint limits explicit.
- [x] Five D1 candidates, D2–D4, retrieval/application/gap evidence supplied and scored.
- [x] Refine observed first-round gaps, rerun affected numerical gates, and complete fresh native application rechecks.
- [x] NOTICE/originals/README and command documentation updated.
- [x] Final required checks and full self-review; scoped Task 2 commit contains this record, with no push/merge.

## Execution record

Baseline: `uv run --python 3.13 --with pytest python -m pytest -q
 test_check_jax_examples.py`, from `build/`, exit 0: 37 passed in 0.41s.
This confirms Task 1's existing process-contract suite before Task 2 edits.
Profile resolution, canonical hashes, actual runtime and output records follow.
Large model loading and accelerator recipes are outside this CPU gate and
remain explicitly unverified locally.

## Stable CPU candidate record — 2026-10-03 20:27:48 UTC

The profile was compiled from exactly the nine requested names: exit 0,
39 exact compatible packages. No family split or dependency change was needed.
Actual API preflight and canonical execution used Python 3.13.8,
macOS-26.6.2-arm64-arm-64bit-Mach-O, one `CpuDevice(id=0)`,
`JAX_PLATFORMS=cpu`. Direct versions: JAX/JAXlib 0.11.2; Flax 0.12.10;
Optax 0.2.8; Orbax checkpoint 0.12.6; Equinox 0.13.8; Diffrax 0.7.2;
e3nn-jax 0.21.0; NumPy 2.5.3. Full transitive pins are in
[32-jax-cpu.txt](32-jax-cpu.txt), SHA-256 `c8bd73640ca1d2cd1f86a211554e9ceac244054d629370a931738a8b5b10258c`.

The public API probe confirmed Optimizer.update takes `(model, grads)`,
State replacement mutates/returns None, StandardCheckpointer supports
`save(directory, state)`/`restore(directory, target=...)`, and e3nn's
Equinox Linear accepts keyword-only irreps/key arguments. This was API
preflight, distinct from the numerical assertions below.

| Gate, from checkout root unless noted | Actual result |
|---|---|
| `uv pip compile --python-version 3.13 specs/verification/32-jax-cpu.in --output-file specs/verification/32-jax-cpu.txt` | Exit 0, 39 packages resolved |
| `uv run --python 3.13 python build/check_snippets.py skills/deep-learning/` | Exit 0, no parser errors (during each example family iteration) |
| Pinned runner on `references/training.md` | Exit 0, 2 selected/executed/passed |
| Pinned runner on `references/scientific.md references/geometric.md` | Exit 0, 2 selected/executed/passed |
| Pinned runner on `references/generative.md references/llm.md` | Exit 0, 2 selected/executed/passed |
| Full exact CPU gate printed above on `skills/deep-learning/` | Exit 0, 6 selected/executed/passed, every required ID present |
| `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py` | Standalone exit 0 |
| `uv run --python 3.13 python build/check_provenance.py` | Standalone exit 0 |
| `uv run --python 3.13 python build/check_snippets.py skills/` | Standalone exit 0, only five existing Bayesian/testing-strategy advisory exemptions |
| From `build/`: `uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py` | Exit 0, 62 passed; includes declared dependency drift |
| `uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check` | Exit 0, generated adapters unchanged |
| `git diff --check` | Exit 0 |

All six canonical blocks passed on their first numerical execution and again
together. No failing numerical check was exempted, suppressed or widened.
The runner executed complete extracted Markdown source without a preamble.
Source location and hashes below identify that exact candidate. The main body
has 1169 words and the description has 300 characters.
Own reference links and trailing whitespace were also checked, exit 0.

| ID | Canonical path:line | Exact extracted-source SHA-256 |
|---|---|---|
| `generative-objectives` | `skills/deep-learning/references/generative.md:58` | `f5551e6acefa5e89786a4beb1e7027e80aaab485d3dd2c9016b0bfef921174d4` |
| `geometric-equivariance` | `skills/deep-learning/references/geometric.md:63` | `e151b0960af09a23427229cf699ca4ce964d84df9ad2296eaa49f1fbc4849bcc` |
| `llm-token-masks` | `skills/deep-learning/references/llm.md:94` | `8c05c220ddc67768d0977f41ff1f96fc81efb5266a3e00bc29f34ce1fe67bd0b` |
| `scientific-solver` | `skills/deep-learning/references/scientific.md:64` | `c47c532c7cb6d16dddf3b8fcbdab18e778ed65f2f0cda99074fa94c95dbe94f9` |
| `nnx-sequence-training` | `skills/deep-learning/references/training.md:59` | `dc4bdf75f0098e7e6dcccb36b22b5e0f200767b4668313d10a270c49b2dc8156` |
| `nnx-checkpoint-resume` | `skills/deep-learning/references/training.md:187` | `9f91b2b042ba5812c2ea6bab686b983d2f1624e7e911b1edb8cd62d6c3e6d5e5` |

| Source | SHA-256 |
|---|---|
| `skills/deep-learning/SKILL.md` | `4a3a195ef1d26a76a1ac13790906406fb7db2eb595b630ca739e566866836b0a` |
| `skills/deep-learning/references/frameworks.md` | `47b458e1b8f3c9285e43dec18f74bc5c3d7b44027ab90c4d87ddebc371bebdf2` |
| `skills/deep-learning/references/generative.md` | `6f9cf63e3bd2d737c735e5ea1ac494eb1e6705ca1aa681b937f1c849edf9ff3f` |
| `skills/deep-learning/references/geometric.md` | `ea30fbaab10b8cb9cce0882cd3bf1152bc5434225deac92d1095ee302e710e7d` |
| `skills/deep-learning/references/llm.md` | `cd2cb928ff1d79887479eb5becdb1223bd6b134fbe14a2fd484eed5aa2497e01` |
| `skills/deep-learning/references/scientific.md` | `3f155a60fbfb3b7cba12c4c4efa7b597b369857e093a6da41f5e743e2297a54a` |
| `skills/deep-learning/references/sequences.md` | `1d5a46913ffb1ff1754efb4defdc4b03d2abe4a4374dac9ba27833b4799af4e4` |
| `skills/deep-learning/references/training.md` | `9ce708a572990ca068060bc9125d8f5dafcbb4b09e159cc1f0fde881939537b3` |
| `skills/deep-learning/references/vision.md` | `4fb0d0c790f5c92146fbfc5967f2be0ab1215476e7f1b6e36505ac197eabefef` |


### Primary-source review and claim limits

Primary documentation/papers were refreshed on 2026-10-03 and are linked near
the claims in each reference: Flax NNX basics/optimizer/transforms/recurrent
and ViT tutorial; Linen; Optax MultiSteps; JAX randomness; Orbax checkpointing;
Equinox filtered transforms; Diffrax neural ODE/CDE, SaveAt and adjoints;
e3nn Equinox/Linen/irreps/IrrepsArray; archived Jraph; Transformer/Mamba, PINN,
FNO, VAE, flow, DDPM, flow-matching, LoRA/QLoRA and DPO papers; Tunix
models/algorithms/rollout and concrete PEFT/DPO examples; Qwix; Transformers
v5 migration; MaxText conversion/inference. A guessed ViT URL did not resolve;
the authored reference was corrected to the actual linked primary tutorial
`https://flax.readthedocs.io/en/stable/examples/vit_training.html` before this
candidate. The e3nn documentation's older banner is reported separately from
the actually executed 0.21.0 API. No external prose or code was adapted.

The sequence check demonstrates a two-causal-lag sine model at one frequency;
it is not a long-memory architecture benchmark. Recovery compares the next
training update with original configuration, generated cursor batch, explicit
augmentation/dropout keys and full dynamic model/Adam/schedule state on the
same CPU/profile. The scientific example establishes its observation count,
analytic derivative and exponential fit, not latent identifiability or stiff
solver generality. The geometric example establishes its stated point-cloud
O(3)/permutation behavior at a fixed origin; no translation claim is made.
Generative and LLM blocks check objective/update math with original synthetic
fixtures, not output quality, real attention/tokenizers or checkpoint loaders.

No Tunix/Qwix package, checkpoint, dataset, GPU or TPU was loaded locally.
Recipe prerequisites are explicitly attributed to sources: Tunix GPU
Llama 3.1-8B PEFT with source 16 GB+ QLoRA / 24 GB+ LoRA guidance; Tunix
Gemma 3-1B DPO with source v6e-1/32 GB HBM testing; MaxText CPU conversion
of a supported mapping with real RAM/disk/checkpoint needs; MaxText's linked
v6e-8 TPU inference setup. Those are documented paths/prerequisites and local
verification limits, not accelerator or loading results.

## Historical first-round candidate/application handoff

This handoff records the earlier checkpoint; its pending application work is
now complete in the separately dated finalization record below.

The nine skill Markdown files are stable for immutable snapshots. Candidate
runs and independent manual scoring belong to the controller. Required next
records: five fresh matched D1 candidates; D2, D3 and D4 applications; the
reference-retrieval query and any genuine gap variants; actual conditions,
Read/source logs and immutable source identities; complete manual scoring
with control/candidate dispositions. No task commit occurs until those
records are supplied, integrated and any observed gaps refined/rechecked.


## Round-1 refinement strategy — recorded before edits

The controller requested one refinement batch after independent review of the
immutable first candidate snapshot. The partial scoring record was read in
full; the D2/D4 delivered responses and their actual Read logs were inspected.
Complete scoring/archive records remain controller-owned and pending, so these
are observed artifact gaps rather than new numerical execution results.
Preserve D1-4's complete next-update coverage and D3's complete symmetry checks.
Keep their successful existing-framework/default/native paths and honest
execution limits. No change to geometric/generative/vision/sequence guidance is
required by this batch.

| Observed gap | Positive/conditional refinement and falsifying invariant |
|---|---|
| D1-1 compares next loss/key/external step but omits post-update model/all optimizer trees | Require explicit post-update model tree and every optimizer leaf, including moments and internal schedule counts, alongside loss/step/key/cursor/schedule output. Keep the canonical full-state equality helper and name each compared tree. |
| D1-2 writes multiple checkpoints to one existing Orbax directory; reconstructs data/objective from caller config before discarding loaded config | Exercise two completed saves in unique progress-specific directories, select/restore the latest completed progress, and compare full next-update parity. Load and validate one authoritative saved configuration before resumed model/optimizer/data/objective/loader factories; all resumed construction consumes it. |
| D1-3 compares losses on changing cursor batches and adds an integer to a typed key | Compare initial/final losses on the same bounded fixture under one declared evaluation/randomness policy. Derive typed keys with split/fold_in; arithmetic on integer seeds occurs before key creation. Make this visible in canonical initialization/restoration. |
| D1-2/4 imply any failed check means package mismatch | Require isolation from the actual exception/assertion, inputs/state and a minimal reproducer; inspect versions/signatures for API errors and math/state for failed numerical checks. |
| D2 reserves an unobserved union-grid entry and asserts four held-out units where two are observed; omits adjoint and computes un-compared tighter gradients | Select held-out targets from each trajectory/channel's observed entries, assert actual entries/counts and disjointness. Name the adjoint. Compare fixed-model predictions and differentiated gradient values directly across tolerances and against the analytic reference, with fixture-derived tolerances. |
| D4 passes an nnx.Module to plain jax.grad for an initial derivative | Use NNX-aware differentiation for each direct-module check/update, or a functional graph/state split/merge boundary. Preserve plain jax.grad for array/PyTree objective math in the canonical LLM block. |

Before changing the recovery check, retain the same CPU/profile/configuration
and float/integer parity tolerances. Two saves at progress 3 and 5 must complete;
the selected latest save must restore progress 5 and produce the same update 6
as uninterrupted execution, including every model/optimizer leaf, internal
scheduler count, external step, generated batch, key progression and cursor.
A fold-in-derived reconstruction key produces a deliberately different fresh
initialization without typed-key arithmetic. The sequence learning check keeps
its fixed fixture and threshold but measures both endpoints in deterministic
evaluation mode.

Before changing the scientific check, keep the six hand-checked observation
units and construct held-out membership from actual observed entries, with two
held-out units and four fit units. Fit only the four eligible training units;
compare both tolerance gradients and predictions at the same initial model to
the analytic solution/reference and each other. Preserve solver/adjoint/dtype,
learning threshold, rate tolerance and prediction tolerances; report any actual
failure rather than relaxing them. The affected gate will execute the complete
training and scientific Markdown blocks unchanged under the pinned CPU
profile. No trial/archive source or frozen first-round snapshot is edited.


Additional pre-edit disposition from the complete cohort overview: D1-5's
recovery comparison advances the mutable model/optimizer but leaves the main
run's key/cursor stale before continuation. A training transition owns the
model, optimizer, returned key and returned cursor together. Require driver
assignment of the returned progress; isolate the parity fixture or carry its
complete post-update state into continuation. The canonical recovery fixture
is isolated, and its final named key/cursor assignment will make the complete
state transition visible. This is an artifact/driver gap, not a numerical
failure observed in the canonical examples. D4 attention-contract details are
still pending the controller's precise report and will be evaluated before the
next stable snapshot.


Final pre-edit D4 disposition: the synthetic objective has correct shifted
completion eligibility and honest scope, but its real-recipe plan omits the
model-facing causal/nonpadding attention relation, same-segment rule when
packing, and positional reset policy. Require an explicit recipe-specific
attention/position contract separate from the completion loss mask. The chosen
real path's tiny perturbation check must leave eligible logits/loss invariant
to padding or other packed-segment changes. This is a supported-recipe planning
requirement; no transformer/checkpoint/loader/attention kernel will be added or
run here, and the canonical array math will retain its limited claim. The
unexecuted checkpoint/tokenizer/Tunix/Qwix/hardware limits remain unchanged.


Further pre-edit D4/RD dispositions from completed independent review: equal
DPO margins give log(2) even when the individual policy/reference completion
log-probabilities differ. Preserve the forward implication (equal policies give
log(2)) as an objective sanity check; require separate immutable SFT
checkpoint/adapter/manifest identity and individual chosen/rejected
log-probability comparisons against the frozen SFT snapshot. Add an original
array counterexample to the canonical LLM block: shift both reference
completion sums by the same offset, assert individual values differ, and
assert the DPO objective still equals log(2). Existing causal/LoRA/DPO checks
and the profile are retained; rerun the changed complete LLM block in the full
six-example gate. RD's routing/reference retrieval is complete; explicitly
state that native framework choices are preferred starting points while valid
existing plain-JAX paths can retain their contracts/checks. No extra mandatory
library/installation rule is introduced.

For attention perturbation checks, hold the queried segment, target labels,
masks and positions fixed; compare only its eligible logits/loss after changing
padding/other segments. For a future-token perturbation, compare earlier query
logits and unchanged targets only. Changing a target label legitimately changes
its likelihood loss and must not be mistaken for an attention failure.


Complete durable round-1 scoring was subsequently read from
[the controller archive](32-jax-trials/D-candidate-scoring.md) committed as
`d16bf3b`. It retains all five D1 scores (11, 11, 9, 12, 11 out of 12),
D2=9/12, D3=10/10, D4=10/12 and RD=8/8; these are unexecuted artifact
coverage, with actual requested/used models and successful Read logs recorded.
One further source-supported explanation error is now explicit in that final
record: Diffrax `throw=True` raises if any vmapped solve fails; `throw=False`
with per-result inspection is also valid. Before prose refinement, preserve
both valid status strategies and the canonical throwing implementation. Refresh
the primary diffeqsolve documentation and clarify the conditional status
contract; no new solver/failure test or numerical source change is required.


## Refined CPU candidate — 2026-10-03 21:12:38 UTC

All accepted round-1 refinements are implemented in SKILL.md and the training,
frameworks, scientific and LLM references. Strategy/dispositions above were
recorded before each edit. The original first-round source/hash tables and
controller-owned frozen snapshot remain unchanged. The geometric, sequences,
generative and vision files remain byte-identical to the original candidate;
D1-4's contrary complete deterministic recovery remains valid guidance.

Recovery now performs two completed progress-specific saves at steps 3 and 5,
selects the latest, validates its single configuration before resumed factories,
uses split/fold_in typed initialization keys and compares every post-update
model/optimizer leaf plus internal schedule counts, external step, schedule
output, key/cursor after update 6. The returned progress is assigned as part of
the complete transition. Fixed learning compares the same fixture in eval mode.
Scientific fitting uses four observed units with two actual observed held-out
units; the named adjoint and direct fixed-model predictions/gradient values are
checked at both tolerances against the analytic reference and each other.
LLM guidance covers the actual NNX differentiation boundary, recipe-specific
attention/positions and fixed-target perturbation checks. Its original array
math now also demonstrates that distinct completion probabilities with equal
margins can yield DPO log(2); separate SFT identity evidence remains required.
Native paths are preferred while valid existing plain-JAX contracts are retained.

| Refinement command/check | Actual result |
|---|---|
| Initial bare `python -` strategy write | Exit 127: shell has no `python`; no write occurred. Retried via `uv run --python 3.13 python -`, exit 0. |
| `uv run --python 3.13 python build/check_snippets.py skills/deep-learning/` | Exit 0 after training/scientific and final LLM edits, no parser errors |
| `JAX_PLATFORMS=cpu uv run --python 3.13 --with-requirements specs/verification/32-jax-cpu.txt python build/check_jax_examples.py skills/deep-learning/references/training.md skills/deep-learning/references/scientific.md` | Exit 0: 3 selected/executed/passed |
| Full exact CPU gate on `skills/deep-learning/` | Exit 0: 6 selected/executed/passed; repeated after new DPO counterexample, again 6/6 |
| `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py` | Standalone exit 0 |
| `uv run --python 3.13 python build/check_provenance.py` | Standalone exit 0 |
| `git diff --check` | Exit 0 |
| Source inventory/own links/whitespace/limits/unchanged-source check | Exit 0: nine Markdown files, six expected IDs, all own links resolve, no trailing spaces, 1378 main-body words and 300 description characters |

No numerical/API assertion failed, no check was exempted, and no tolerance or
learning threshold changed. The final solve-status clarification was prose
only; its extracted numerical source matches the already passed hash below.
The pinned Python/platform/direct-version environment remains the same as the
first candidate; profile SHA-256 remains `c8bd73640ca1d2cd1f86a211554e9ceac244054d629370a931738a8b5b10258c`. Current primary
Flax transformation/attention, JAX typed-key, Diffrax adjoint/diffeqsolve sources
were refreshed for the new boundary/status claims. All code/prose is original.
Real checkpoint/tokenizer/attention/Tunix/Qwix/GPU/TPU paths remain unexecuted;
the documented checks/prerequisites are not portrayed as synthetic CPU proof.

| ID | Canonical path:line | Exact extracted-source SHA-256 |
|---|---|---|
| `generative-objectives` | `skills/deep-learning/references/generative.md:58` | `f5551e6acefa5e89786a4beb1e7027e80aaab485d3dd2c9016b0bfef921174d4` |
| `geometric-equivariance` | `skills/deep-learning/references/geometric.md:63` | `e151b0960af09a23427229cf699ca4ce964d84df9ad2296eaa49f1fbc4849bcc` |
| `llm-token-masks` | `skills/deep-learning/references/llm.md:126` | `0048357bd03ff8992c163b6f6aa4cdefc5e0d1a4e57aa371811aa9eb8842dc9d` |
| `scientific-solver` | `skills/deep-learning/references/scientific.md:76` | `56ff0fd597a64d27f367911fa6dc5f612b54371f852a13ca752b24460e48fb05` |
| `nnx-sequence-training` | `skills/deep-learning/references/training.md:73` | `e3a952f9e33f3e9f0d7f22dfb37ceb4e1be4a80543af5de38f14d747c746f977` |
| `nnx-checkpoint-resume` | `skills/deep-learning/references/training.md:214` | `d5b45ea5548136a824c7e07ff3a3741aac31f47d8702276661ec6e3b4aefe119` |

| Source | SHA-256 |
|---|---|
| `skills/deep-learning/SKILL.md` | `ece0ac27eaf8b9ca8de149fc27ec408d6ab975e58ba9cfa132c47d765b14fdbf` |
| `skills/deep-learning/references/frameworks.md` | `86bf7d4be22899bffc75aeaad33ee5986a4b572c6cb924425214998a1097dc47` |
| `skills/deep-learning/references/generative.md` | `6f9cf63e3bd2d737c735e5ea1ac494eb1e6705ca1aa681b937f1c849edf9ff3f` |
| `skills/deep-learning/references/geometric.md` | `ea30fbaab10b8cb9cce0882cd3bf1152bc5434225deac92d1095ee302e710e7d` |
| `skills/deep-learning/references/llm.md` | `4d5e193c9376d05af7ac402cd7994df450f74c3c5c0275cd567523d30e1659f2` |
| `skills/deep-learning/references/scientific.md` | `aeecdd5ea8bdb1b44652918586564900091465b68524b61ca303d18e0e643b97` |
| `skills/deep-learning/references/sequences.md` | `1d5a46913ffb1ff1754efb4defdc4b03d2abe4a4374dac9ba27833b4799af4e4` |
| `skills/deep-learning/references/training.md` | `dc2e7ccc657d6b438796a0f44b38e06648564e7ff8fdd6d38c58bca835d80970` |
| `skills/deep-learning/references/vision.md` | `4fb0d0c790f5c92146fbfc5967f2be0ab1215476e7f1b6e36505ac197eabefef` |


At this refined milestone the nine skill files were stable for the controller's
new immutable snapshot. The pending fresh application records were supplied
later and integrated in the finalization record below. The complete historical
first-round scoring and D3/RD successes remain preserved. Trial archival/scoring
stays with the controller.

## Complete application evidence and finalization — 2026-10-03

The historical [Claude control scoring](32-jax-trials/D-control-scoring.md) and
[round-1 candidate scoring](32-jax-trials/D-candidate-scoring.md) were both read
completely, including all nine candidate findings and contrary successes.
Those controls predate skill authoring. The refined source incorporated the
recorded positive/conditional refinements above; its six canonical numerical
blocks were rerun after the applicable source changes and passed 6/6.
The round-1 snapshot remains preserved at
[guidance-candidate-deep-learning](32-jax-trials/guidance-candidate-deep-learning/source-hashes.json).
The table below describes artifact coverage, with no additional pass threshold.

| Historical Claude scenario | Pre-authoring control | First candidate | Finding and disposition |
|---|---:|---:|---|
| D1, five samples | 35/60 (five 7/12) | 54/60 (11, 11, 9, 12, 11/12) | Preserve correct shifts/transforms/mode and candidate 4's complete deterministic recovery. Clarify unchanged-fixture learning, every post-update state/schedule leaf, two-save lifecycle, authoritative reconstruction config, typed-key derivation and complete key/cursor continuation. |
| D2 | 10/12 | 9/12 | Preserve native solver/gradient checks and repaired observation membership. Repair actual observed held-out selection/count, declare adjoint and compare fixed-model predictions/gradients across tolerances. Correct the explanation of vmapped throw status. |
| D3 | 5/10 | 10/10 | Preserve valid plain-JAX symmetry math and proper rotations. Native e3nn coverage and declared inversion/permutation tests are supplied; no additional library prohibition is added. |
| D4 | 7/12 | 10/12 | Preserve valid shifted reductions, immutable SFT reference and zero-B LoRA math. Declare real attention/positions, consistently use NNX-aware direct-module derivatives, and check individual SFT reference identity separately from DPO log(2). |
| Shared D1–D4 | 57/94 | 83/94 | Coverage totals do not erase the specific first-round defects. |
| RD, separate retrieval | No matched RD control | 8/8 | Both requested references were actually read; clarify preferred native paths while retaining valid existing frameworks. |

Historical trials requested Sonnet/medium with read-only Read/WebSearch/WebFetch
in fresh sessions. Actual usage includes claude-sonnet-5 and claude-opus-5 in
D1/D2/D4 controls and candidates; D3 and RD candidates report Sonnet only.
The controls used final-result JSON and candidates verbose tool logging.
Successful candidate Reads and failed probes are recorded in the complete
scoring/conditions; no WebSearch/WebFetch or application execution occurred in
the historical candidates. The full main body was supplied to system context,
with references available from the immutable snapshot. This tests supplied
application/retrieval rather than automatic catalog discovery.

The owner then chose built-in Codex agents for all remaining trials. The
[durable runtime correction](../plans/completed/32-jax-deep-learning-skills.md#execution-runtime-correction--owner-decision-2026-10-03)
records that automatic approval review rejected the external refined launch
because destination-specific export authorization was absent. That rejected
launch executed no process or trial. No further external trial launch occurred.
The historical and native cohorts are separate; their scores do not establish
a matched between-runtime effect.

The controller archived the complete native cohort at commit `597318a`.
Its [native controls](32-jax-trials/native/D-native-control-scoring.md) comprise
five fresh D1 samples and D2/D3/D4. These controls postdate the refined source,
with the new guidance withheld. All eight control first reads preceded the
first candidate guidance exposure; the last control answer and first candidate
application overlapped in scheduling. The [native refined candidates](32-jax-trials/native/D-native-candidate-scoring.md)
comprise five fresh D1 samples plus D2/D3/D4/RD, each independently read fully
and scored against the original rubric. No demonstrated static defect was found.

| Native scenario | Withheld-guidance control | Refined candidate | Evidence-based disposition |
|---|---:|---:|---|
| D1, five samples | 46/60 (9, 10, 8, 9, 10/12) | 60/60 (five 12/12) | All candidates deliver finite-gradient, bounded fixed-fixture learning and immediate full-state next-update checks. Preserve all controls' correct masking/mode/transforms and four complete recovery checks; omitted checks are not demonstrated failed learning or restoration. |
| D2 | 12/12 | 12/12 | Both scientific artifacts cover the original rubric. Retain the full control success; the native candidate does not justify inventing a scientific discipline failure. |
| D3 | 7/10 | 10/10 | The plain-JAX control is mathematically valid with correct rotations/permutations. Named e3nn coverage and an explicit test for its declared inversion claim were absent; the candidate supplies both. |
| D4 | 12/12 | 12/12 | Both artifacts cover the original rubric. Preserve the supported pinned legacy-Flax control as contrary success; candidate Tunix/Qwix planning remains unexecuted. |
| Shared D1–D4 | 77/94 | 94/94 | Descriptive coverage of eight fresh applications in each native condition. |
| RD, separate retrieval | No matched native RD control | 8/8 | Actual scientific/geometric/framework reads and correct native routing; separate from the matched totals. |

Native agents used default type, fork_turns=none and unique fresh identities.
Model/effort were inherited; exact identifiers are not exposed by the
collaboration API and are not inferred from provider aliases. They received
realistic scenario/runtime/ordinary-skill context, withheld scoring/design
records, and a read-only information policy. Candidates received the complete
refined main in their first recorded helper read and read references on demand.
Actual official source/ordinary-skill reads, unsuccessful probes, response
hashes and permitted nonexecution are recorded per conditions/research notes.
At most two application children were active. A thread-limit scheduling retry
is preserved in the scoring record and does not alter grades.

| Native candidate group | Actual unique reference reads |
|---|---|
| All five D1 | frameworks.md, sequences.md, training.md |
| D2 | frameworks.md, scientific.md, training.md |
| D3 | frameworks.md, geometric.md, training.md |
| D4 | frameworks.md, llm.md, training.md |
| RD | frameworks.md, geometric.md, scientific.md |

All nine source hashes match the
[refined immutable snapshot](32-jax-trials/native/guidance-codex-candidate-r2-deep-learning/source-hashes.json).
A fresh metadata-only audit verifies all 17 unique native identities, complete
first prompt reads, nonempty answers/notes, answer hashes/line counts and every
actual reference hash. Fresh archive checks verify the
[45-file control manifest](32-jax-trials/native/D-control-archive.json) and
[61-file candidate/helper/snapshot manifest](32-jax-trials/native/D-candidate-r2-archive.json).
No raw answer, archive helper, scoring or archive attribute was changed.

The finalizer read all nine live Markdown files and the complete old/native
scoring records. No new source defect or missing application variant was
identified. No skill wording, numerical code, profile pin or tolerance was
changed during finalization. The 1378-word main and 300-character discovery
text meet the stated bounds and have no model/fork pin. Whole-skill handoffs
stay bare and own relative links resolve; domain framework/data/objective/state
contracts, provenance and the current authoritative 17-original count agree.
The six extracted source hashes and profile hash match the refined 6/6 execution
record above, so unchanged numerical evidence is reused; no new numerical run
or application-code execution is claimed here.

A first finalizer metadata audit used a broad directory glob that also matched
the guidance snapshot; it failed with FileNotFoundError for that directory's
nonexistent conditions.json. The explicit 17-trial enumeration corrected the
audit scope and exited 0 without any payload edit. The underlying source/archive
checks exited 0. This was an audit-selection error, separate from an application
or numerical defect.

Application scores establish supplied-artifact/retrieval coverage for these
samples. They do not establish automatic loading, production compatibility,
executed learning/recovery, hardware performance or real checkpoint/tokenizer
behavior. The canonical CPU checks establish only the six stated local
contracts under their recorded profile. All real Tunix/Qwix, attention/packing,
quantized, checkpoint conversion, GPU/TPU and MaxText paths retain their explicit
unexecuted prerequisites/limits. No new run-success metric is inferred.

### Final required gates

All commands below ran in the assigned worktree with Python 3.13; only the
runtime test command uses its `build/` working directory. Every actual exit
was inspected. No source changed after the application snapshot; the historical
6/6 refined CPU execution and its exact source/profile identities are reused.

| Final command | Actual exit and output |
|---|---|
| `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py` | 0; no output |
| `uv run --python 3.13 python build/check_provenance.py` | 0; no output |
| `uv run --python 3.13 python build/check_snippets.py skills/` | 0; five existing advisory exemptions (Bayesian four-chain run, optional BlackJAX, SBC, Dynamax sketch and testing-strategy replacement lines); no new exemption or parser error |
| From `build/`: `uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py` | 0; 62 passed in 1.68s, including dependency drift |
| `uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check` | 0; no output, generated adapters unchanged |
| `uv run --python 3.13 --with pyyaml python /private/tmp/task2-finalization-audit.py` | 0; six exact extracted-source hashes and profile unchanged, nine stable Markdown sources, 1378 main words, 300 description characters, 29 local links resolve, 17 originals agree, 45+61 archived files and 17 unique native trial identities/read/response/reference hashes verified; no application/numerical execution |
| `git diff --check` | 0; no output |

The temporary audit is a finalizer bookkeeping helper, not a bundled skill
script or new numerical fixture. The full implementer report preserves command
outputs, historical/refined source identities, application dispositions and
commit verification. Only the nine skill Markdown files, CPU input/pins, this
verification record, NOTICE, CLAUDE.md and README.md are included in the scoped
`feat(skills): add verified JAX deep-learning workflow` commit. The controller
performs the separate task review; no push, merge or global installation was
performed.
