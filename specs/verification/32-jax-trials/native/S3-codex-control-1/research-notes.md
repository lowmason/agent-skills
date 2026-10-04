# Research notes

Authorized task was read by executing only the required helper start command:

`python3 /private/tmp/jax-skill-trials-pAYZ0t/trial_io.py start /private/tmp/jax-skill-trials-pAYZ0t/native/S3-codex-control-1`

The brief asks how to investigate and fix a non-learning JAX simulation that recompiles for different scalar inputs. It authorizes inline analysis/code delivery without execution or a new approval workflow. No actual simulation source or log was supplied, so response.txt explicitly leaves the actual root cause unconfirmed and makes fixes conditional on evidence.

## Ordinary skills read and used

- `/Users/lowell/.agents/skills/systematic-debugging/SKILL.md`: evidence gathering, minimal reproducible call sequence, and one hypothesis/change at a time before selecting a fix. Because the task expressly forbids application execution, the response delivers the procedure rather than claiming an investigation has run.
- `/Users/lowell/.agents/skills/clean-code/SKILL.md`: descriptive function names, cohesive host normalization/compiled core/diagnostic responsibilities, named dtype and integer bound. Authored inline example only; no existing application code was edited.
- `/Users/lowell/.agents/skills/verification-before-completion/SKILL.md`: distinguish verified artifact delivery from unexecuted code and unproven runtime behavior.

No new task-specific JAX skill file was opened, searched, or used. No other trials, rubrics, plans, or scoring files were inspected. No subagents were spawned.

## Primary sources actually consulted

All technical reliance is on the JAX project's official documentation:

- https://docs.jax.dev/en/latest/_autosummary/jax.jit.html — dynamic/default versus static arguments, static value cache keys, pure-function requirement and function weak reference.
- https://docs.jax.dev/en/latest/201/jit.html — shape/dtype/function identity cache keys, recreated lambdas/partials, cache-miss diagnostics, warm-up and asynchronous dispatch. Also supplied navigation to updated documentation paths.
- https://docs.jax.dev/en/latest/config_options.html — `jax_log_compiles`, `jax_explain_cache_misses`, and configuration details.
- https://docs.jax.dev/en/latest/_autosummary/jax.log_compiles.html — compilation logging context manager (initial search output).
- https://docs.jax.dev/en/latest/201/slow-compilation.html — tracing versus compilation, fresh callable identity, changing shapes/dtypes, Python loop unrolling.
- https://docs.jax.dev/en/latest/101/type_promotion.html — Python scalar weak typing and explicit dtype producing strong typing.
- https://docs.jax.dev/en/latest/101/default_dtypes.html — X64 precision policy and program-start configuration.
- https://docs.jax.dev/en/latest/_autosummary/jax.lax.fori_loop.html — dynamic bounds, static versus dynamic lowering, fixed carry types and autodiff limits.
- https://docs.jax.dev/en/latest/_autosummary/jax.lax.while_loop.html — dynamic condition, fixed carry shapes/dtypes and reverse-mode limitations.
- https://docs.jax.dev/en/latest/201/control-flow.html — structured control flow, fixed-length scan and data-dependent control flow (initial official search result).
- https://docs.jax.dev/en/latest/_autosummary/jax.eval_shape.html — abstract shape/dtype inspection API.
- https://docs.jax.dev/en/latest/_autosummary/jax.block_until_ready.html — completion blocking across result pytrees.
- https://docs.jax.dev/en/latest/201/profiling.html — timing placement, first call versus warmed execution, asynchronous dispatch blocking.
- https://docs.jax.dev/en/latest/501/compilation-cache.html — cache-miss diagnostics and cross-process persistent caching (initial official search result).

Search results also surfaced third-party sources; none were relied on. Opens of legacy/mistyped `type_promotion.html`, `101/type-promotion.html`, and `201/benchmarking.html` did not return usable page content; official navigation resolved the correct current paths above.

## Nonexecution and verification scope

No delivered JAX application, simulation, or test code was executed. JAX was not imported in a local runtime. No dependency installation, tracing, lowering, compilation, device benchmark, or numerical test was performed. No repository or skill-collection files were modified.

Only response.txt and this research-notes.md were created using a literal apply_patch operation, in addition to the helper's authorized read log. Artifact verification is limited to reading these two files and checking their existence/content; it does not imply the supplied runtime checks pass.
