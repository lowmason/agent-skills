# Framework paths

Load this reference when choosing a new project's framework, preserving an
existing implementation, or checking a native scientific/geometric/LLM path.
Model computation and differentiation remain JAX in every row.

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

Use `nnx.jit`/`nnx.value_and_grad` when passing NNX modules directly. At a
plain-JAX transformation boundary, explicitly split into GraphDef/state,
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

## Version and verification boundary

The six `cpu-example` blocks are verified together under a compiled profile:
JAX/JAXlib 0.11.2, Flax 0.12.10, Optax 0.2.8, Orbax checkpoint 0.12.6,
Equinox 0.13.8, Diffrax 0.7.2, e3nn-jax 0.21.0, NumPy 2.5.3, Python 3.13.8.
These are the examples' tested versions, not a prescription to replace an
existing project's lockfile. The e3nn docs currently display an older version
banner; the Equinox Linear call is additionally exercised against the pinned
package. Tunix/Qwix and scale implementations are linked recipes outside this
CPU profile. Refresh APIs deliberately and rerun the affected assertions after
a dependency change.
