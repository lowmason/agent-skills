# Research notes

## Authorized task and scope

The exact requested start command was executed:

`python3 /private/tmp/jax-skill-trials-pAYZ0t/trial_io.py start /private/tmp/jax-skill-trials-pAYZ0t/native/D1-codex-control-5`

Its complete output authorized inline code delivery for a small JAX model predicting the next sample in variable-length synthetic sine sequences, with training, validation, CPU use, and a resumable checkpoint. It explicitly stated that execution was not required and that no new design approval workflow or skill-collection modification should occur. No supplied reference filenames appeared in that output, so no `readref` operation was needed.

## Ordinary skills actually read

- `/Users/lowell/.agents/skills/clean-code/SKILL.md`: readable names, cohesive functions, meaningful comments, and functional JAX state.
- `/Users/lowell/.agents/skills/develop-testing-strategy/SKILL.md`: invariant-driven checks for alignment, padding, causality, shapes, finite values, and reproducible save/load continuation. Its separate planning/handoff workflow was superseded by the explicit inline complete-delivery authorization. No new workflow approval was requested.
- `/Users/lowell/.agents/skills/verification-before-completion/SKILL.md`: no runtime or passing-test claims without fresh execution evidence. Only artifact existence/content was checked; model execution was prohibited by the conductor instructions and is explicitly disclaimed in the response.

No new JAX skill files, other trials, rubrics, scoring, or plans were read. No agents were spawned or delegated to.

## External primary sources actually used

A broad search was used to locate primary documentation. Search snippets for secondary sources were returned incidentally but were not used to substantiate the response. The following official JAX pages were opened and queried directly:

1. https://docs.jax.dev/en/latest/_autosummary/jax.lax.scan.html
   - Fixed carry shape and dtype, leading-axis iteration, single loop lowering, static iteration count.
2. https://docs.jax.dev/en/latest/jit-compilation.html
   - JIT transformation of pure functions; keep I/O and logging outside transformed functions.
3. https://docs.jax.dev/en/latest/config_options.html#platforms
   - Set `JAX_PLATFORMS=cpu` before JAX backend initialization.
4. https://docs.jax.dev/en/latest/installation.html
   - CPU installation using `pip install --upgrade jax`.

Documentation was accessed read-only through `web__run`; no remote code was downloaded or executed.

## Implementation choices and limitations

- Small 32-unit GRU in plain JAX, residual next-sample readout, functional Adam and global gradient clipping.
- Fixed shapes, valid-time masks, warmup scoring mask, ghost-row masking for final batches.
- Separate seed-derived synthetic training/validation datasets; no training-time JAX randomness.
- Latest completed-epoch checkpoint saves model, Adam moments, optimizer step, complete configuration, shuffle generator state, versions, and metric history.
- Atomic replacement through a flushed same-directory temporary NPZ; non-pickle JSON metadata.
- Resume means epoch-boundary continuation; unfinished epochs are replayed.
- Includes user-runnable contract checks and measured validation/baseline reporting, but does not claim a numerical result or guaranteed cross-machine bitwise equivalence.

## Explicit nonexecution

No delivered application/model code was executed. No Python import of JAX, model initialization, optimizer step, synthetic dataset generation from the delivered program, training, inference, or delivered self-test was run. No packages were installed. Shell commands were used only for helper invocation, ordinary-skill reads, literal response/notes writes, and text-artifact verification. All requested substantive output is in `response.txt`.
