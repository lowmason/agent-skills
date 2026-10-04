# Research and delivery record

Task obtained by running exactly:

`python3 /private/tmp/jax-skill-trials-pAYZ0t/trial_io.py start /private/tmp/jax-skill-trials-pAYZ0t/native/D1-codex-control-1`

The helper authorized inline analysis and complete code for a small CPU JAX next-sample sine-sequence model, including training, validation, and resume checkpointing. It required no execution in this session and supplied no additional local references. No other trials, rubric, scores, plans, or new JAX skill files were inspected.

## External primary sources actually consulted

- JAX installation: https://docs.jax.dev/en/latest/installation.html — confirmed current CPU installation using `pip install --upgrade jax`.
- JAX `lax.scan`: https://docs.jax.dev/en/latest/_autosummary/jax.lax.scan.html — confirmed scanned leading axes, `(carry, output)` return contract, fixed carry shape/dtype, and suitability for compiled recurrent iteration.
- JAX automatic differentiation: https://docs.jax.dev/en/latest/automatic-differentiation.html — confirmed `value_and_grad` and differentiation through nested dictionary parameter pytrees.
- JAX configuration: https://docs.jax.dev/en/latest/config_options.html — specifically inspected the `JAX_PLATFORMS` entry to confirm selecting only CPU before backend initialization.
- JAX `random.key`: https://docs.jax.dev/en/latest/_autosummary/jax.random.key.html — confirmed typed seeded key API.
- JAX `random.split`: https://docs.jax.dev/en/latest/_autosummary/jax.random.split.html — read search-result documentation confirming splitting one initialization key into separate parameter keys.
- JAX Quickstart: https://docs.jax.dev/en/latest/notebooks/thinking_in_jax.html — read primary-source search-result context for CPU install and JAX array/compilation behavior.

Only official JAX documentation was relied upon. Search returned other pages that were not used. GRU equations, fixed-size batch packing, masked one-step objectives, Adam update formulas, NumPy JSON/NPZ checkpoint construction, and deterministic dataset/shuffle indexing were authored directly rather than copied from a third-party implementation.

## Ordinary skills actually read

- `/Users/lowell/.agents/skills/clean-code/SKILL.md` — applied descriptive naming, cohesive helpers, explicit state, and functional JAX parameter handling. No adjacent code or skill collection was modified.
- `/Users/lowell/.agents/skills/test-driven-development/SKILL.md` — consulted before drafting code. Its runtime red/green procedure was not performed because this task explicitly authorized inline generated code and prohibited execution of the delivered model/application code. The answer supplies software-contract tests but makes no TDD or passing-test claim.
- `/Users/lowell/.agents/skills/verification-before-completion/SKILL.md` — applied by verifying the delivery artifact and limiting claims to that evidence. Runtime training, convergence, and tests are expressly unverified.

## Nonexecution and verification

No delivered application or model code was run or imported. No dependencies were installed. No JAX backend was initialized during this trial. No training, inference, gradient calculation, checkpoint serialization, or supplied test was executed. Code in `response.txt` is an inline deliverable only.

A separate trusted Python orchestration snippet read `response.txt`, extracted its three Python code fences, and used only `ast.parse` to check syntax. It reported:

- Main script: syntax parsed, 393 lines, 36 top-level statements.
- Inference example: syntax parsed, 6 lines, 5 top-level statements.
- Tests: syntax parsed, 72 lines, 9 top-level statements.
- Artifact checks passed: exactly three Python blocks, balanced code fences, no drafting placeholder, explicit CPU environment setting, and `allow_pickle=False` restoration.

This was static inspection, not execution of those blocks, and does not establish numerical correctness or model convergence. The substantive response includes this limitation and commands for the user to execute independently.

## Scope of writes

Only this trial's `response.txt` and `research-notes.md` were written. The answer includes all substantive analysis and code verbatim. No repository, ordinary skill, or other trial was modified. No subagent was spawned or delegated to.
