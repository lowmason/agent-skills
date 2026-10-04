# Research notes

Task supplied by the isolated trial's trial_io.py start operation. The substantive response is in response.txt.

## Supplied guidance actually used

- Full optimize-jax main guidance supplied by start.
- references/profiling.md, read in full through the authorized trial_io.py readref operation.
- No inference or sharding reference was loaded. No generation or distributed change was made.

## Ordinary skills actually used

- systematic-debugging: /Users/lowell/.agents/skills/systematic-debugging/SKILL.md, read in full. Used root-cause-first investigation, component-boundary instrumentation, and conditional single-cause experiments.
- clean-code: /Users/lowell/.agents/skills/clean-code/SKILL.md, read in full. Used explicit names/constants and cohesive functions for the delivered Python probe.
- No additional ordinary skill references were read.
- No new approval/design workflow was started: the supplied task explicitly authorized complete inline analysis/code delivery.

## Primary sources actually consulted

All web information gathering used official JAX documentation:

1. https://docs.jax.dev/en/latest/async_dispatch.html — asynchronous submission and host consumption/readiness.
2. https://docs.jax.dev/en/latest/benchmarking.html — placement, compilation and completed-call benchmarking boundaries.
3. https://docs.jax.dev/en/latest/aot.html — trace, lower, compile, executable specialization.
4. https://docs.jax.dev/en/latest/profiling.html — warmed traces, completion during capture and TraceAnnotation.
5. https://docs.jax.dev/en/latest/jit-compilation.html — dynamic versus static specialization and stable function identity/caching.
6. https://docs.jax.dev/en/latest/config_options.html — jax_explain_cache_misses and jax_enable_compilation_cache.
7. https://docs.jax.dev/en/latest/_autosummary/jax.block_until_ready.html — entire PyTree readiness.
8. https://docs.jax.dev/en/latest/501/compilation-cache.html — persistent cache configuration and reuse.
9. https://docs.jax.dev/en/latest/transfer_guard.html — implicit versus explicit transfers and CPU guard limits.
10. https://docs.jax.dev/en/latest/_autosummary/jax.profiler.trace.html — trace export and create_perfetto_trace.

The small projection/NumPy reference and measurement boundaries follow the supplied profiling guidance; the delivered multi-mode probe is a synthesized adaptation. No external code or claims of measured performance were imported.

## Explicit nonexecution and scope

- Did not execute delivered application/model code, import JAX locally, run the probe, benchmark kernels, compile model code, capture a trace, or assert that tests passed.
- All hardware timings, target compile events, actual reference errors, before/after effects and peak-memory results are pending.
- Only authorized helper start/readref operations, ordinary skill reads, primary-source browsing and literal writes of response.txt and this file were performed.
- Did not inspect other trials, rubrics, plans, scoring, repository code, or new JAX skill files outside the supplied snapshot.
- Did not mutate the skill collection or shared application files.
- Did not spawn or delegate.
