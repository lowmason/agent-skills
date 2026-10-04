# Research notes

## Authorized task and scope

The first executed command was exactly:

`python3 /private/tmp/jax-skill-trials-pAYZ0t/trial_io.py start /private/tmp/jax-skill-trials-pAYZ0t/native/S2-codex-control-1`

It returned exit code 0 and the following complete task text:

> This is a sandboxed application of an already approved design and implementation plan. This is an inline code-generation application; deliver the requested analysis and complete code in the response. Execution in this session is not required. Return the requested analysis/code; do not conduct a new design approval workflow or modify the skill collection. Implement a tiny JAX autoregressive generation example using a KV cache and establish that cached generation agrees with full-prefix generation.

The substantive response is delivered verbatim in `response.txt`. No separate application/model file was created. Only the assigned response and notes files were written; the start helper maintains its own read log.

## Ordinary skills actually read

- `/Users/lowell/.agents/skills/clean-code/SKILL.md`: applied descriptive names, cohesive functions, named dimension/tolerance constants, functional cache updates, and boundary-focused assertions. No existing repository code was changed, so no clean-code fix citations were applicable.
- `/Users/lowell/.agents/skills/test-driven-development/SKILL.md`: consulted to frame the behavioral checks first. The code presents the equivalence and boundary assertions before implementation definitions. The task's explicit nonexecution constraint takes precedence over the skill's execution procedure. No red/green test cycle was performed or claimed.
- `/Users/lowell/.agents/skills/verification-before-completion/SKILL.md`: applied by separating artifact delivery from numerical verification and explicitly stating that the delivered code and assertions were not run.

No new task-specific JAX skill was read. No other trials, scoring material, rubrics, or plans were inspected. No agents were spawned or delegated to.

## Primary sources actually consulted

The following official JAX documentation was accessed with the web tool during this response:

- [jax.lax.scan](https://docs.jax.dev/en/latest/_autosummary/jax.lax.scan.html): fixed carry shapes/dtypes; scan signature and output stacking; static iteration count.
- [jax.lax.dynamic_update_slice](https://docs.jax.dev/en/latest/_autosummary/jax.lax.dynamic_update_slice.html): update/start-index API; start adjustment at array boundaries, motivating host capacity validation.
- [jax.jit](https://docs.jax.dev/en/latest/_autosummary/jax.jit.html): pure functions and array/container arguments; static arguments and recompilation; `functools.partial` decorator compatibility.
- [jax.numpy.matmul](https://docs.jax.dev/en/latest/_autosummary/jax.numpy.matmul.html): vector/matrix shape support and the `Precision.HIGHEST` parameter.
- [JAX FAQ: jit changes exact numerics](https://docs.jax.dev/en/latest/faq.html#jit-changes-the-exact-numerics-of-outputs): floating-point differences from XLA optimization. Used to distinguish allclose logits from exact token equality.
- [JAX - The Sharp Bits](https://docs.jax.dev/en/latest/notebooks/Common_Gotchas_in_JAX.html): opened during research, but the response did not derive an additional claim from this page.

No third-party technical sources or repositories were used. All code is authored for the requested toy example. The cache equivalence proof is original reasoning about that code, not a reported external experimental result.

## Nonexecution and verification status

Explicit nonexecution: no delivered application/model code was executed, imported, compiled, traced, or numerically tested. No JAX installation, environment mutation, benchmark, or generated model run occurred.

The response supplies runnable checks for per-prefix logits, independent greedy generation, masking of unwritten nonzero cache slots, one-token prompts, zero new tokens, final cache capacity, and invalid requests. No assertion pass, numerical maximum error, generated token sequence, or runtime speed is claimed as observed.

The final file check reads the two assigned artifacts and verifies their presence/content only. It is not application execution or numerical verification.
