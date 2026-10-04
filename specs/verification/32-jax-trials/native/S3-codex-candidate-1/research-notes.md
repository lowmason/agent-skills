# Research notes

Task: investigate/fix scalar-triggered recompilation in a non-learning JAX simulation; inline analysis and complete runnable code delivery.

## Task-specific material actually read

- Full supplied optimize-jax main guidance returned by the required trial_io start operation.
- Supplied references/profiling.md, read only through the required trial_io readref operation. No other supplied reference was needed.

## Ordinary skills actually read and applied

- systematic-debugging: /Users/lowell/.agents/skills/systematic-debugging/SKILL.md. Used to distinguish suspected causes from confirmed application diagnoses, instrument before changing behavior, and recommend one supported change at a time.
- clean-code: /Users/lowell/.agents/skills/clean-code/SKILL.md. Used for descriptive names, cohesive functions, explicit constants, and domain boundary checks in the delivered Python harness.
- verification-before-completion: /Users/lowell/.agents/skills/verification-before-completion/SKILL.md. Used to limit completion claims to delivery/static validation and label all runtime outcomes pending.

## Primary sources actually consulted

Official JAX documentation was opened using the web tool, because these are niche technical details and API behavior can change:

- https://docs.jax.dev/en/latest/jit-compilation.html — static arguments, control flow, tracing and JIT cache reuse.
- https://docs.jax.dev/en/latest/_autosummary/jax.jit.html — hashable static arguments, callable weak reference and sharding signature contract.
- https://docs.jax.dev/en/latest/201/slow-compilation.html — compile/cache-miss diagnostics, target-function attribution and callable recreation.
- https://docs.jax.dev/en/latest/config_options.html — jax_log_compiles, jax_explain_cache_misses, jax_enable_compilation_cache, and related flags.
- https://docs.jax.dev/en/latest/benchmarking.html — asynchronous dispatch, completion barriers, data-placement boundary and precision comparability.
- https://docs.jax.dev/en/latest/aot.html — trace/lower/compile stages and fixed executable signature.
- https://docs.jax.dev/en/latest/_autosummary/jax.lax.fori_loop.html — fixed carry and static/dynamic loop-bound behavior.
- https://docs.jax.dev/en/latest/profiling.html — warmed annotated capture with device work complete inside capture.
- https://docs.jax.dev/en/latest/101/default_dtypes.html — float32/float64 policy and x64 flag.
- https://docs.jax.dev/en/latest/101/type_promotion.html — scalar weak typing/type-promotion semantics.
- https://docs.jax.dev/en/latest/501/compilation-cache.html — persistent compilation cache as a distinct reuse experiment.

The older https://docs.jax.dev/en/latest/type_promotion.html path was also opened but did not supply substantive content; it is not relied on.

## Explicit nonexecution and limits

- No delivered simulation, JAX model/application code, correctness checks, compilation experiment, timer, profiler, or numerical reference calculation was executed in this session.
- No JAX installation or hardware compatibility validation was attempted.
- No original application source/input sequence was provided, so the actual root cause is unknown. Static dt is an explicitly illustrative controlled cause with conditional application advice.
- No measured recompilation count, maximum numerical error, timing distribution, speedup, memory result, or distributed result is claimed.
- No other trial, rubric, plan, scoring material, or new JAX skill file outside the supplied snapshot was inspected.
- No child agent was spawned and no shared repository files were changed.
- Only response.txt and research-notes.md were written by this agent, besides the helper-managed read log.

## Artifact verification

The complete single Python code block in response.txt was parsed with Python ast.parse after the response was written. Parsing succeeded. This performs syntax validation without importing JAX or executing any delivered code and does not establish runtime correctness. The final delivery status is complete analysis/code artifact delivery; numerical/runtime verification remains pending.
