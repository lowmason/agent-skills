# Research notes

Authorized task was read in full by executing the supplied `trial_io.py start` command. It requested inline analysis and complete code for a small CPU JAX next-sample sine model with synthetic variable-length data, training, validation, and resumable checkpoints. No task-specific reference files were supplied in the output or present in the owned directory's file listing, so no `readref` calls were needed.

## Ordinary skills actually read and applied

- `/Users/lowell/.agents/skills/clean-code/SKILL.md`: descriptive names, cohesive functions, pure JAX updates, and focused boundary checks. This is new supplied code, so no existing-code cleanup or fix citations were applicable.
- `/Users/lowell/.agents/skills/verification-before-completion/SKILL.md`: constrained claims to actual evidence; response explicitly says the delivered model and tests were not executed. Artifact creation is verified separately from application behavior.

No new JAX skill files, other trial directories, rubrics, scoring, or plans were inspected. No delegates were spawned.

## External primary sources actually consulted

- https://docs.jax.dev/en/latest/installation.html — standard CPU JAX installation and supported platform distinction.
- https://docs.jax.dev/en/latest/_autosummary/jax.lax.scan.html — recurrence over the leading axis, fixed carry shape/dtype, output/carry contract.
- https://docs.jax.dev/en/latest/_autosummary/jax.jit.html — pure function contract, array/container arguments, compilation.
- https://docs.jax.dev/en/latest/random-numbers.html — explicit PRNG keys, split discipline, typed versus legacy keys.
- https://docs.jax.dev/en/latest/config_options.html#jax-platforms — `JAX_PLATFORMS` selects initialized/default platforms; code forces CPU before import.
- https://docs.jax.dev/en/latest/_autosummary/jax.random.key_data.html — checkpoint extraction of typed key backing data.
- https://docs.jax.dev/en/latest/_autosummary/jax.random.wrap_key_data.html — typed key reconstruction with explicit implementation.
- https://numpy.org/doc/stable/reference/generated/numpy.savez_compressed.html — named arrays in a compressed NPZ and file-like output.
- https://numpy.org/doc/stable/reference/generated/numpy.load.html — NPZ context manager and disabling pickle loading.

Sources were accessed with the web tool. No third-party tutorials were used. The architecture, manual Adam update, synthetic generator, masking, checkpoint schema, and tests were authored for this task.

## Explicit nonexecution

The delivered application/model code and tests were not executed, imported, traced, compiled by JAX, trained, or benchmarked. No JAX or NumPy application dependency installation was performed. Only task-start/file listing, ordinary-skill reads, primary-documentation reads, artifact writes, and static text inspection were performed. A helper used Python's `ast.parse` on the three Python code fences to check syntax without executing them; all parsed successfully. There are no observed numerical validation results or test pass claims.
