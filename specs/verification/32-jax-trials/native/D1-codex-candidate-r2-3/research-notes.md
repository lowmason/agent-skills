# Research notes

## Scope and execution boundary
- Received the full authorized inline task by running exactly:
  python3 /private/tmp/jax-skill-trials-pAYZ0t/trial_io.py start /private/tmp/jax-skill-trials-pAYZ0t/native/D1-codex-candidate-r2-3
- Task: deliver analysis and complete code for a small CPU JAX sine-sequence next-sample model with training, validation, and resume checkpoint.
- Did not execute delivered application/model code. No JAX training, validation, inference, finite-gradient checks, checkpoint saves/restores, dependency installs, AST/compile checks, or performance measurements were run.
- No subagents were spawned. No other trials, scoring materials, plans, rubrics, or new JAX skill files were inspected.
- Wrote only response.txt and research-notes.md in this assigned trial directory. The trial_io helper recorded permitted supplied-reference reads.

## Supplied task-specific guidance read
- Main deep-learning guidance from trial_io start.
- references/frameworks.md through trial_io readref.
- references/sequences.md through trial_io readref.
- references/training.md through trial_io readref.
- Chosen default stack and canonical signatures: Flax NNX, Optax, Orbax; nnx.Optimizer(model, tx, wrt=nnx.Param); optimizer.update(model, grads); StandardCheckpointer; NNX pure-state replacement.
- Adapted the supplied fixed-frequency two-lag neural model and recovery pattern into one complete script with variable lengths, online training batches, held-out validation, CLI resume, exact reconstruction metadata, completed-save selection, and isolated correctness checks.
- Dependency pins in the response are the supplied reference profile, not versions verified by executing locally.

## Ordinary skill used
- clean-code: /Users/lowell/.agents/skills/clean-code/SKILL.md
- Read the entire main skill. Applied descriptive names, cohesive model/data/checkpoint functions, named stream/save/check constants, explicit side-effect names, and boundary checks.
- No other ordinary skill files or referenced clean-code subfiles were read.
- The inline task was already authorized and supplied complete guidance, so no new design/approval workflow was introduced.

## External primary sources actually accessed
Accessed read-only with web__run on 2026-10-03:
1. https://flax.readthedocs.io/en/stable/api_reference/flax.nnx/training/optimizer.html
   - Verified current documented Optimizer(model, tx, *, wrt, graph=None), optimizer.update(model, grads), NNX gradient examples, and step/optimizer-state semantics.
2. https://orbax.readthedocs.io/en/latest/guides/checkpoint/orbax_checkpoint_101.html
   - Verified documented StandardCheckpointer PyTree save/restore, nonexisting checkpoint path requirement, and completion waiting in checkpoint patterns.
3. https://docs.jax.dev/en/latest/random-numbers.html
   - Read typed-key and explicit key-splitting guidance; additionally used web find for split.
4. https://optax.readthedocs.io/en/latest/api/optimizer_schedules.html
   - Verified documented linear_schedule and schedule semantics; additionally used web find for linear_schedule.

These were the only external sources used. No quotes copied from external documentation. The inline answer links sources beside the associated APIs.

## Static review and reported status
- Manually reviewed causal feature/target shifts, right-padding mask i < L - 2, pooled MSE unit, finite-array assumptions, separate streams, saved configuration before reconstruction factories, all-state recovery comparison, and literal artifact writes.
- Hand arithmetic recorded: lengths [5,7,9,12] yield 3+5+7+10 = 25 targets; eligible losses 1,3,5 yield 3.
- The response explicitly labels all runtime results/checks unexecuted and does not invent loss values, timing, validation improvement, or checkpoint parity.

