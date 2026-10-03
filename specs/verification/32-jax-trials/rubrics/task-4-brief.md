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

### Task 4: Deliver and verify JAX execution and generation guidance

**Files:** Create `skills/optimize-jax/SKILL.md`, its three references in File
Structure, and `specs/verification/32-optimize-jax.md`. Modify `NOTICE`,
`CLAUDE.md`, and `README.md` for this third new original skill.

**Interfaces:**
- Consumes R1, R6–R8, Task 1's runner, and Task 2's CPU profile.
- Produces a reproduction/profiling/correctness procedure and the example IDs
  `jax-timing` and `cached-decode`.
- Supports non-learning JAX execution without requiring neural training.

- [ ] **Step 1: Record fresh no-optimization-skill controls.**

Use five S1 samples and fresh S2/S3 applications, withholding the rubric.

| ID | Verbatim prompt | Manual scoring |
|---|---|---|
| S1 | "My JAX inference loop is slow. A timer around a jitted call reports a very small time, but end-to-end latency is much larger and changes with input length. Help reproduce and diagnose this." | Separates compile/warm/end-to-end work and synchronization; checks shape/static-value recompilation and transfers; profiles before recommending a change; measures stated workload/hardware and numerical parity. |
| S2 | "Implement a tiny JAX autoregressive generation example using a KV cache and establish that cached generation agrees with full-prefix generation." | Explicit prefill/decode, masks/positions/capacity, cache state and termination; full/cached logits and greedy parity; seeded sampling and padding checks; no claimed real-LLM correctness from only a toy fixture. |
| S3 | "A non-learning JAX simulation recompiles for different scalar inputs. How should I investigate and fix it?" | Correct tracing/static-versus-dynamic reasoning, observed recompilation evidence and output parity; no imposed training or Bayesian inference workflow. |

- [ ] **Step 2: Author the entry point and profiling/sharding references.**

Initial frontmatter:

```yaml
---
name: optimize-jax
description: >
  Use when JAX code has tracing errors, unexpected recompilation, memory
  pressure, slow execution, or distributed placement problems, or when
  improving inference and generation — including profiling, precision,
  sharding, asynchronous timing, prefill/decode, and KV caches.
license: MIT
metadata:
  author: Lowell Mason
---
```

Main output contract: reproduce the execution problem → establish a workload
and correct reference → separate compile/runtime/transfer costs → profile →
change one measured cause → check outputs/gradients and resource/performance
effects → report hardware, workload, results and limits.

`profiling.md` covers traced/static values, PyTrees/NNX state, shape buckets,
compilation, transfers, vectorization/loops, rematerialization, precision and
memory. `jax-timing` compiles a small JAX function, synchronizes before reading
timers, records compile and warm timings separately, and checks equivalent
outputs. It has no assertion that a tiny CPU optimization must be faster.

`sharding.md` explains mesh/partition/placement contracts and distributed
model/optimizer/checkpoint state using the resolved JAX APIs and primary docs.
A one-device CPU demonstration is labeled as such; do not call it multi-host
verification. Mark any actual multi-host/accelerator recipe with the explicit
reason it cannot run in the CPU gate.

- [ ] **Step 3: Author and execute the generation reference.**

`inference.md` starts with JAX-native research generation. `cached-decode`
implements tiny causal attention with fixed cache arrays, explicit positions
and valid lengths, prefill and decode state, capacity checks, and EOS/termination.
Its independent full-prefix reference verifies logits and greedy tokens across
several prompt lengths and padding patterns; fixed-key sampling reproduces its
own result. Cover zero/short/near-capacity boundaries and prevent cache writes
beyond capacity. This is a cache/math fixture, not evidence that an arbitrary
converted pretrained checkpoint is correct.

Document supported Tunix generation and optional MaxText scale paths through
primary sources, with model conversion/logit parity and hardware prerequisites.
Do not introduce a default PyTorch model execution path or a production hosting
workflow.

```bash
uv run --python 3.13 python build/check_snippets.py skills/optimize-jax/
JAX_PLATFORMS=cpu uv run --python 3.13 --with-requirements specs/verification/32-jax-cpu.txt python build/check_jax_examples.py skills/optimize-jax/
```

Expected: parse/execution exit 0; both required IDs and every selected CPU
example pass. Record actual timings, environment and hashes without promising
speed on other devices.

- [ ] **Step 4: Run WITH-skill micro/application and retrieval checks.**

Use matched S1 conditions for five candidate samples, plus fresh S2/S3
applications. Ask a retrieval question distinguishing a loss/convergence problem
from a cache/recompilation problem. Read and score actual outputs, refine the
guidance from failures, and rerun affected numerical/application checks.

- [ ] **Step 5: Complete attribution/docs and commit.**

Append `optimize-jax/` to NOTICE and its bare name to CLAUDE.md's originals
list; recompute the written count from NOTICE (one additional original in this
task). Add the README original credit and row:

```markdown
| [`optimize-jax`](skills/optimize-jax/) | Reproduce, profile, and improve JAX execution: tracing, compilation, memory, precision, sharding, and generation/cache performance, with measured changes and correctness parity. |
```

Finalize the Orchestra inspiration paragraph for all three original skills;
describe inspiration by reference only when no third-party text/code was
reproduced. Preserve the Bayesian attribution and original license inventory.
Run frontmatter/provenance, parse and dependency-drift checks. Commit this skill,
evidence and docs with message `feat(skills): add verified JAX optimization and inference`.

**Checkpoint:** All three skills are individually verified. Performance claims
have measured workloads, and generation guidance has a tested cache contract.
