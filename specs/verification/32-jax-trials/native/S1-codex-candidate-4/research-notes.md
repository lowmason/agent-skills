# Research notes

## Task and scope

- Ran the required trial_io start operation and read its full supplied task/main guidance.
- Applied the supplied optimize-jax guidance to the S1 request about misleading JIT timing and length-dependent inference latency.
- Read only the relevant supplied reference through the authorized helper operation: references/profiling.md. No inference or sharding implementation change was made, so those references were not loaded.
- Delivered complete inline Python code and diagnostic analysis in response.txt. No repository files, skills, runtime adapters, models, or other trial directories were inspected or modified.

## Ordinary skills actually read and used

- /Users/lowell/.agents/skills/systematic-debugging/SKILL.md: investigation before fixes; no application cause or speedup claimed without reproduction/log/profile evidence.
- /Users/lowell/.agents/skills/clean-code/SKILL.md: descriptive names, cohesive helpers, named tolerances/dimensions, independent boundary assertions for the delivered Python fixture. No existing application Python was edited, and no cleanup fixes are claimed.
- /Users/lowell/.agents/skills/verification-before-completion/SKILL.md: explicit separation between delivered checks and unexecuted results; no claim of passing tests or an established performance fix.

## Primary sources actually consulted using web tools

All are official JAX documentation. No secondary technical sources were used.

1. https://docs.jax.dev/en/latest/benchmarking.html — readiness, warm-up, dtype and transfer boundaries.
2. https://docs.jax.dev/en/latest/async_dispatch.html — submission versus completion and host reads.
3. https://docs.jax.dev/en/latest/jit-compilation.html — static arguments, caching and recreated callables.
4. https://docs.jax.dev/en/latest/aot.html — trace/lower/compile stages and signature-specific executables.
5. https://docs.jax.dev/en/latest/profiling.html — completed trace captures and custom TraceAnnotation events.
6. https://docs.jax.dev/en/latest/501/compilation-cache.html — persistent-cache attribution and cache-miss diagnostics.
7. https://docs.jax.dev/en/latest/transfer_guard.html — explicit/implicit transfers, logging policies and CPU caveat.
8. https://docs.jax.dev/en/latest/_autosummary/jax.block_until_ready.html — full-PyTree barrier API.
9. https://docs.jax.dev/en/latest/_autosummary/jax.tree_util.tree_flatten_with_path.html — path/structure metadata API.
10. https://docs.jax.dev/en/latest/config_options.html#enable-compilation-cache — compilation-cache configuration.

The sources were opened and relevant page text searched. response.txt links the sources supporting its explanations; additional API pages informed code delivery. No citations imply executed measurements.

## Explicit nonexecution and limits

The delivered application/model code was not imported, executed, benchmarked, traced, compiled, or tested in this session. No JAX environment was installed or changed. All numerical parity results, maximum error, timing distributions, compile events, traces, application root cause, before/after effect, and memory impact are pending user-side execution. Only task/helper reads, skill-file reads, official documentation browsing, literal artifact writes, and artifact delivery checks were performed.

The script's frozen toy workload demonstrates evidence collection and correctness assertions; it does not validate a real model/checkpoint, generation/cache policy, accelerator transfer performance, distributed execution, or production concurrency. No optimization is reported as measured.

## Artifact verification

Read both delivered artifacts, confirmed required evidence/nonexecution content, and parsed the embedded Python with ast.parse. Syntax parsing passed for the 365-line program. This static parse did not import or execute the delivered code and does not establish runtime/API compatibility or numerical/performance results.
