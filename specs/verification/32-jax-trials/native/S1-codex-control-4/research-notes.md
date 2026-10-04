# Research notes

## Authorized task and scope

Executed the requested start helper exactly and read its complete output. The task was to help reproduce and diagnose a slow JAX inference loop whose jitted-call timer is small while end-to-end latency is larger and length-dependent. The helper explicitly authorized inline analysis/code delivery with no execution or new approval/design workflow required.

Only response.txt and research-notes.md were authored in this assigned trial directory. No repository files, skill collection files, other trials, rubrics, plans, or scoring were inspected or modified. No agents were spawned or delegated.

## Ordinary skills actually read and used

- `/Users/lowell/.agents/skills/systematic-debugging/SKILL.md`: separate hypotheses, establish observable signatures, instrument component boundaries, avoid speculative fixes and distinguish proposed experiments from evidence.
- `/Users/lowell/.agents/skills/clean-code/SKILL.md`: cohesive Python functions, descriptive names, named timing/model constants, no unrelated cleanup. The delivered example is new inline code; no existing Python was refactored.
- `/Users/lowell/.agents/skills/verification-before-completion/SKILL.md`: avoid any claim that application code was run, a benchmark passed, or the user's bottleneck was fixed. Verification is confined to the delivered artifact contents.

No new or task-specific JAX skill was read. No design/approval workflow was started because the task was explicitly approved for inline delivery.

## Actual primary sources consulted

All sources below were opened through the web tool as official JAX documentation. Relevant sections were read and cited in response.txt. The answer contains original prose and code rather than copied documentation examples.

1. https://docs.jax.dev/en/latest/async_dispatch.html — dispatch can return before results are ready, host inspection waits, benchmark synchronization.
2. https://docs.jax.dev/en/latest/benchmarking.html — isolate device placement, first compilation-bearing call, repeated synchronized execution.
3. https://docs.jax.dev/en/latest/jit-compilation.html — compilation reuse, static arguments, function identity and repeated temporary-function compilation.
4. https://docs.jax.dev/en/latest/profiling.html — trace context, completion inside capture, custom TraceAnnotation, XProf viewing.
5. https://docs.jax.dev/en/latest/_autosummary/jax.block_until_ready.html — synchronize all JAX array leaves of a pytree.
6. https://docs.jax.dev/en/latest/_autosummary/jax.device_put.html — device placement, asynchronous transfer, explicit device argument.
7. https://docs.jax.dev/en/latest/_autosummary/jax.device_get.html — retrieve arrays or pytrees to the host.
8. https://docs.jax.dev/en/latest/config_options.html — JAX_LOG_COMPILES and JAX_EXPLAIN_CACHE_MISSES flags and semantics.
9. https://docs.jax.dev/en/latest/aot.html — tracing, lowering, compilation, execution stages and input shape/dtype specialization.
10. https://docs.jax.dev/en/latest/_autosummary/jax.jit.html — checked the public JIT API/decorator documentation while validating the code design.
11. https://docs.jax.dev/en/latest/control-flow.html — shape/dtype tracing, Python-loop unrolling, structured JAX control flow.
12. https://docs.jax.dev/en/latest/persistent_compilation_cache.html — optional disk cache can reuse programs across process starts.

## Explicit nonexecution and verification limits

The delivered JAX inference model, reproduction, timing commands, integration snippet, and profiler code were not executed. JAX was not imported or initialized by this agent. No synthetic latency results were generated; no application fix, compilation success, hardware behavior, or speedup is claimed.

Shell execution was limited to the required start helper, reading ordinary skill files, and read-only verification of the two text artifacts. Both artifacts were read back. The two Python blocks in response.txt were syntax-checked with ast.parse, which parsed them without importing JAX or executing application code; both parsed successfully. File creation used literal apply_patch input so response contents could not execute through shell substitution.

The answer explicitly states that the root cause of the original workload is unverified, supplies discriminating experiments, distinguishes first-seen calls from pure compilation measurements, and treats optimization suggestions as conditional on the evidence.
