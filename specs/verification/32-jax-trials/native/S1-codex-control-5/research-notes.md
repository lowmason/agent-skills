# Research notes

## Authorized task and nonexecution

The start helper was run exactly as requested and supplied the approved inline analysis/code task: reproduce and diagnose a slow JAX inference loop whose jitted-call timer is small, end-to-end latency is larger, and latency varies by input length.

No delivered application/model code was executed. No JAX import, compilation, numerical test, benchmark, installation, profiler capture, or model inference was performed in this session. The response explicitly labels runtime diagnosis and speedups unverified. Only response.txt, research-notes.md, and the helper-owned read log are task artifacts. No other trials, rubrics, plans, scoring materials, or new JAX skill files were inspected. No agents were spawned.

## Ordinary skills actually read and applied

- `/Users/lowell/.agents/skills/systematic-debugging/SKILL.md`: evidence-first reproduction and component-boundary instrumentation; hypotheses distinguished from confirmed causes; no speculative production fix.
- `/Users/lowell/.agents/skills/clean-code/SKILL.md`: descriptive Python measurement names, cohesive functions, explicit units, single reused inference callable.
- `/Users/lowell/.agents/skills/verification-before-completion/SKILL.md`: verify delivery files and avoid runtime-success claims because execution was excluded.

No new or task-specific JAX skill was read.

## Actual primary sources consulted

All sources below are JAX project documentation. They were searched/read through the web tool during this session. Search discovery was followed by direct page reads; relevant JIT, transfer, readiness, and profiling passages were retrieved explicitly.

1. https://docs.jax.dev/en/latest/async_dispatch.html
   - Arrays can return before completion; host inspection synchronizes; dispatch-only timing undercounts completed work.
2. https://docs.jax.dev/en/latest/benchmarking.html
   - Separate compilation, warm execution, data transfer, and dtype differences when benchmarking.
3. https://docs.jax.dev/en/latest/201/jit.html
   - Shapes/dtypes, static values, and function identity affect caching; temporary functions can recompile; compile/cache-miss logging; padding/bucketing variable shapes.
4. https://docs.jax.dev/en/latest/_autosummary/jax.jit.html
   - Pure-function/pytree interface, function cache identity, static arguments, and recompilation on changed static values.
5. https://docs.jax.dev/en/latest/_autosummary/jax.device_put.html
   - Explicit placement and asynchronous transfer; readiness required for completed-transfer timing.
6. https://docs.jax.dev/en/latest/_autosummary/jax.block_until_ready.html
   - Readiness operation supports all JAX-array leaves in a pytree.
7. https://docs.jax.dev/en/latest/transfer_guard.html
   - Implicit/explicit transfer distinction; `log` permits and logs implicit traffic while explicit transfers remain allowed.
8. https://docs.jax.dev/en/latest/profiling.html
   - Capture via `jax.profiler.trace`; ensure output readiness inside capture; annotations; XProf trace viewing.

Other search results were not used as authorities. The diagnostic harness is original code drafted for the task, rather than a verbatim documentation example. No numerical timing claims were invented.

## Delivery verification

The response includes a self-contained script, diagnostic and timing run commands, first-visit/revisit lengths, exact-shape warmup, device-resident completed calls, deliberately fenced stage attribution, separate unfenced end-to-end host-response measurement, median/p95 summaries, compilation evidence, conditional follow-up experiments, transfer diagnosis, and profiler capture code.

Literal heredoc writes and a literal apply_patch edit were used for artifact content so response text could not undergo shell substitution. Read-only file-size/completeness checks do not execute the delivered Python.

Verification performed: read-only `wc -l -c` confirmed both files were nonempty, and `tail -n 3 response.txt` confirmed the substantive answer ended with its explicit unverified-runtime statement. Source-derived prose was tightened afterward; the final read-only delivery check confirms both files remain present and nonempty. Runtime behavior remains unexecuted and unverified.
