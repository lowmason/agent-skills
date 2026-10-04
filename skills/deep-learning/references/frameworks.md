# Framework paths

Load this reference when choosing a new project's framework, preserving an
existing implementation, or checking a native scientific/geometric/LLM path.
Model computation and differentiation remain JAX in every row. Native paths
are preferred starting points; a valid existing plain-JAX implementation can
retain its mathematical/state contract and checks.

| Situation | Path | Compatibility contract |
|---|---|---|
| New general neural training | Flax NNX + Optax + Orbax | Use NNX-aware transforms on object graphs; differentiate selected parameters; save dynamic state and reconstruct configuration. |
| Existing Linen project | Retain Linen | Keep its apply/variable-collection/mutable-state contract. A requested migration needs its own parity check. |
| Solver-coupled scientific model | Equinox + Diffrax + Optax | Filter differentiable floating leaves, use solver-native terms/controllers/adjoints, and verify observation/gradient contracts. |
| e3nn symmetry model | Documented Equinox or Linen integration | Specify irreps/parity at its native API boundary; validate the declared transformations. NNX interoperation is a separate compatibility question. |
| Supported LLM adaptation | Tunix, with Qwix for the selected PEFT/quantization recipe | Check exact architecture, checkpoint, tokenizer, algorithm, package and accelerator combination before loading. |

[Flax basics](https://flax.readthedocs.io/en/stable/nnx_basics.html) describes
NNX's graph/state separation; [Linen documentation](https://flax-linen.readthedocs.io/en/latest/)
remains the source for existing Linen projects. The canonical examples here
use `nnx.Optimizer(model, tx, wrt=nnx.Param)` and
`optimizer.update(model, grads)` as documented by the
[NNX optimizer API](https://flax.readthedocs.io/en/stable/api_reference/flax.nnx/training/optimizer.html).
Their tested signatures come from execution, not an assumption that older
optimizer tutorials match the installed version.

Use `nnx.jit` and `nnx.grad`/`nnx.value_and_grad` when passing NNX modules
directly. This applies to initial-gradient assertions and diagnostic derivatives
as well as compiled training updates. Choose the differentiation filter for the
intended leaves. Pure array/PyTree objectives can use `jax.grad`; a direct NNX
object needs the graph-aware boundary. At a plain-JAX transformation boundary,
explicitly split into GraphDef/state,
merge inside, and return/update state as needed. The
[NNX transformation guide](https://flax.readthedocs.io/en/stable/guides/transforms.html)
explains that boundary. Equinox's
[filtered transforms](https://docs.kidger.site/equinox/api/transformations/)
handle mixed array/static PyTrees; their native solver example is the
[Diffrax neural ODE](https://docs.kidger.site/diffrax/examples/neural_ode/).

The [e3nn Equinox API](https://e3nn-jax.readthedocs.io/en/latest/api/equinox.html)
and [Linen API](https://e3nn-jax.readthedocs.io/en/latest/api/flax.html) are
explicit supported integration points. This skill's executable geometric
example uses the former. Preserve valid direct-JAX symmetry constructions in
an existing model; their algebra and validation determine correctness.

[Tunix's model table and loader](https://tunix.readthedocs.io/en/latest/models.html)
cover selected Gemma, Llama and Qwen configurations. The
[Qwix project](https://github.com/google/qwix) supplies JAX quantization tooling;
using it is conditional on a documented recipe, not a prerequisite for every
neural model. See [llm.md](llm.md) for concrete loading prerequisites and local
verification limits.

## GPU target and local verification

GPU is the usual target for new neural training and inference code. Preserve a
specified CPU/TPU target or an existing project's hardware contract. Before a
GPU run, inspect the GPU vendor/model/count/VRAM, operating system and driver,
then use the project's accelerator lockfile or resolve a separate environment
from [JAX installation](https://docs.jax.dev/en/latest/installation.html).
For NVIDIA, select the CUDA wheel family compatible with that GPU, driver and
JAX version; AMD requires its documented ROCm path. Do not use this repository's
CPU-only verification profile as the GPU deployment environment or carry
`JAX_PLATFORMS=cpu` into a GPU job. Check `jax.devices('gpu')` and actual array
placement before expensive work; a missing requested GPU is a setup error,
not an invitation to silently run training on CPU. When the authoring machine
has no GPU, deliver target-run commands and assertions with execution pending.

Compile the training/update boundary using the framework's native transforms.
Keep parameters, optimizer state, PRNG streams and recurrent/KV state resident
on the GPU; place batches deliberately and aggregate metrics before scheduled
host logging. Avoid per-step NumPy conversion, Python scalar reads and host
assertions in the hot path. Stage suitable fixed-shape recurrence with native
JAX/framework control flow; retain host input validation and small independent
correctness checks outside the timed compiled loop.

Choose a measured precision policy for the selected GPU: bfloat16 compute can
be appropriate on supporting hardware, with float32 sensitive reductions and
optimizer/master state where required. Preserve scientific accuracy needs;
validate loss, gradients and one update against a trusted higher-precision
reference. Record compute/storage/accumulation dtypes and matmul precision
separately. Use [JAX GPU performance guidance](https://docs.jax.dev/en/latest/gpu_performance_tips.html)
and optimize-jax for workload-specific profiling, batch/length choices,
rematerialization, buffer donation and sharding after correctness. Do not copy
version-dependent XLA/NCCL flags as universal defaults.

Run a small smoke case on the intended GPU before scaling. Check finite
loss/gradients and update/recovery parity with justified tolerances, then measure
synchronized throughput/latency and peak memory at representative shapes.
CPU passes remain useful portable checks; they do not validate GPU kernels,
precision, allocator behavior, distributed collectives or performance.

## Version and verification boundary

The six `cpu-example` blocks are verified together under a compiled profile:
JAX/JAXlib 0.11.2, Flax 0.12.10, Optax 0.2.8, Orbax checkpoint 0.12.6,
Equinox 0.13.8, Diffrax 0.7.2, e3nn-jax 0.21.0, NumPy 2.5.3, Python 3.13.8.
These are the examples' tested versions, not a prescription to replace an
existing project's lockfile. The e3nn docs currently display an older version
banner; the Equinox Linear call is additionally exercised against the pinned
package. Tunix/Qwix and scale implementations are linked recipes outside this
CPU profile. Refresh APIs deliberately and rerun the affected assertions after
a dependency change. When an API call fails, isolate the exception and inspect
its installed signature/version. When a mask, gradient or recovery assertion
fails, isolate that computation and state transition; the profile alone cannot
determine the cause.
