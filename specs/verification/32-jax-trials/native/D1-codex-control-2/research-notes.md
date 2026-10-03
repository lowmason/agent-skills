# Research notes

The authorized task was obtained by executing exactly:

`python3 /private/tmp/jax-skill-trials-pAYZ0t/trial_io.py start /private/tmp/jax-skill-trials-pAYZ0t/native/D1-codex-control-2`

The output requested inline complete analysis/code for a small CPU JAX model predicting the next sample in variable-length synthetic sine sequences, including training, validation, and resumable checkpoints. It specified that model execution was not required and that no new design approval workflow or skill-collection modifications were needed. No task-specific JAX skill or local reference guidance was supplied or read.

## Ordinary skills actually read and used

- `/Users/lowell/.agents/skills/clean-code/SKILL.md`: naming, cohesive functions, explicit data/state structures, and focused boundary checks.
- `/Users/lowell/.agents/skills/verification-before-completion/SKILL.md`: distinguished artifact/syntax verification from runtime verification; did not claim training, runtime, or tests passed.

No skill reference files were read. No other trial outputs, scoring rubrics, plans, or new JAX skill files were inspected. No agents were spawned.

## External sources actually consulted

Only primary documentation supports the implementation details:

- https://docs.jax.dev/en/latest/_autosummary/jax.lax.scan.html — scan carry fixed shape/dtype, scan over the leading time axis, and rolled loop behavior.
- https://docs.jax.dev/en/latest/installation.html — standard `pip install jax` CPU installation; used this rather than an assumed CPU extra.
- https://docs.jax.dev/en/latest/config_options.html — `JAX_PLATFORMS` / `jax_platforms` for CPU backend selection.
- https://docs.jax.dev/en/latest/jax.random.html — explicit typed keys, splitting, and conversion between typed keys and serializable raw bits.
- https://docs.jax.dev/en/latest/101/random.html — typed-key and nonreuse guidance returned by the initial search.
- https://docs.jax.dev/en/latest/_autosummary/jax.random.wrap_key_data.html — restoration with an explicit PRNG implementation.
- https://numpy.org/doc/stable/reference/generated/numpy.savez_compressed.html — keyed arrays, file-object writing, NPZ representation, and loading without pickle.

The initial broad web search also returned descriptions of gradient checkpointing, transfer guards, API indexes, a JAX source file, distributed data loading, discussions, and nonprimary sources. These additional results were not relied on for code or claims. Gradient rematerialization is unrelated to the persisted training-state checkpoint required here.

## Nonexecution and verification

The delivered application/model code, training, inference, and self-tests were not run, imported, or evaluated. No dependencies were installed. Verification was limited to reading the written artifacts and parsing the Python code fences with `ast.parse`, which does not execute the code. All modifications were literal file writes within the assigned trial directory. Runtime behavior and numerical performance remain unverified.
