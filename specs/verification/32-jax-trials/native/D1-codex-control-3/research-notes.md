# Research notes

Authorized task: the full output of `trial_io.py start` requested an inline complete JAX model for next-sample prediction in variable-length sine sequences, synthetic data, CPU execution, training, validation, and resumable checkpointing. The output specified that execution was not required and that the already-approved design should not trigger a new approval workflow. No task-specific reference file was supplied or read.

## Ordinary skill actually read and applied

- `/Users/lowell/.agents/skills/clean-code/SKILL.md` (bare skill name `clean-code`): descriptive names, cohesive helpers, explicit side effects, useful intent comments, boundary verification code. The code is new inline delivery; no existing repository code was edited, so the adjacent-code confirmation gate did not apply.

## External primary sources actually consulted

- https://docs.jax.dev/en/latest/config_options.html — CPU backend via `JAX_PLATFORMS`, configuration before initialization.
- https://docs.jax.dev/en/latest/installation.html — current CPU pip installation guidance.
- https://docs.jax.dev/en/latest/_autosummary/jax.lax.scan.html — time-major scan and fixed-shape carry semantics.
- https://docs.jax.dev/en/latest/201/control-flow.html — scan's fixed-loop and differentiation context (search result).
- https://docs.jax.dev/en/latest/automatic-differentiation.html — differentiating parameter dictionaries and scalar losses (search result).
- https://docs.jax.dev/en/latest/101/transformations.html — value_and_grad and transformed pure computations (search result).
- https://docs.jax.dev/en/latest/_autosummary/jax.value_and_grad.html — official API page.
- https://docs.jax.dev/en/latest/_autosummary/jax.tree_util.tree_flatten.html — state pytree flattening API page.
- https://docs.jax.dev/en/latest/jax.random.html — random key API page.
- https://optax.readthedocs.io/en/latest/getting_started.html — explicit init/update/apply_updates and chained gradient clipping with Adam.
- https://optax.readthedocs.io/en/latest/api/optimizers.html — Adam API inventory.
- https://optax.readthedocs.io/en/latest/api/transformations.html — clipping transformation API page.

The general web search returned other domains as well; they were not relied on. The implementation, masking conventions, data generation, checkpoint format, and included self-tests are original delivery decisions for this task.

## Execution status and boundaries

No delivered application/model code was executed. No JAX imports, training, validation, inference, self-tests, dependency installation, or numerical benchmarks were run. Only task-helper execution, read-only skill reading, primary-source web research, literal artifact writes, and an optional Python AST syntax parse of the delivered code were used. Any AST parse is static syntax validation and does not execute or import the delivered code.

No other trials, scoring rubrics, plans, or new JAX skill files were inspected. No repository or skill collection files were changed. Artifacts were written only under the owned trial directory.

Static verification result: `ast.parse` accepted the 476-line delivered Python script. No runtime checks were executed.
