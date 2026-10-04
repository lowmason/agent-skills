# Research notes

Authorized task: diagnose a slow JAX inference loop where an unfenced jitted-call timer is small, end-to-end latency is larger, and latency varies with input length. The helper supplied this inline analysis/code-delivery task. No implementation/design approval workflow was initiated.

## Actual sources used

Only primary JAX documentation supports technical claims. Searches returned other material, but no non-primary technical source was relied on. Official pages were opened, with targeted finds/reads where needed:

- https://docs.jax.dev/en/latest/async_dispatch.html — dispatch can precede device completion; host observation and completion waits establish timing boundaries.
- https://docs.jax.dev/en/latest/benchmarking.html — first-use compilation, synchronization, device placement, and dtype distinctions.
- https://docs.jax.dev/en/latest/jit-compilation.html — static-value specialization and stable function identity/cache reuse.
- https://docs.jax.dev/en/latest/aot.html — tracing/lowering/compilation/execution stages and signature-specialized executables.
- https://docs.jax.dev/en/latest/201/slow-compilation.html — log_compiles, explain_cache_misses, and shape/dtype/function cache-miss evidence.
- https://docs.jax.dev/en/latest/persistent_compilation_cache.html — optional compiled-executable disk cache; fresh process is not necessarily a cold persistent cache.
- https://docs.jax.dev/en/latest/profiling.html — trace completion boundaries, annotations, and XProf viewing.
- https://docs.jax.dev/en/latest/_autosummary/jax.block_until_ready.html — completion of pytree array leaves.
- https://docs.jax.dev/en/latest/_autosummary/jax.device_put.html — asynchronous placement/transfer and device commitments.
- https://docs.jax.dev/en/latest/_autosummary/jax.profiler.TraceAnnotation.html — custom profiler event context manager.
- https://docs.jax.dev/en/latest/_autosummary/jax.profiler.trace.html — trace options, exported log directory, and interactive Perfetto-link behavior.
- https://docs.jax.dev/en/latest/_autosummary/jax.lax.scan.html — rolled loop representation and fixed-shape/dtype carry requirements.

Additional official search result/reference material seen but not needed for a distinct final claim: thinking_in_jax, configuration options, control-flow documentation, and the newer compilation-cache documentation path.

## Ordinary skills actually read and applied

- /Users/lowell/.agents/skills/systematic-debugging/SKILL.md — reproduction/instrumentation before fixes; hypotheses explicitly distinguished from observed evidence; targeted changes conditional on findings.
- /Users/lowell/.agents/skills/clean-code/SKILL.md — named timing units, purpose-specific helpers, descriptive metrics and variable names. No existing application Python was modified.
- /Users/lowell/.agents/skills/verification-before-completion/SKILL.md — explicit nonexecution status; no assertion that benchmarks pass or a bottleneck is confirmed; artifact presence/content checked separately from model execution.

No task-specific new JAX skill files, other trial directories, plans, rubrics, or scoring were inspected. No delegation was performed. No repository/skill collection edits were made.

## Explicit nonexecution and artifact scope

The delivered diagnostic application/model code was not executed, imported, compiled, benchmarked, tested, or profiled. Its numerical padding assertions were authored but not run. No timing numbers were invented. Python was used only to run the authorized helper and to write/read these literal text artifacts; it did not evaluate delivered code.

Only response.txt and research-notes.md were written in this owned trial directory, in addition to any helper-maintained read log. Quoted heredoc plus Python raw string literals were used for artifact writes, so shell interpolation could not execute response contents.
