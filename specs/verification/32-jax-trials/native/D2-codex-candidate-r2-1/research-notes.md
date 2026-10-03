# Sources and execution boundary

- Started this trial with the exact required trial_io start command and read its full output.
- Applied the supplied main deep-learning guidance as the complete task-specific authority.
- Read only the supplied relevant references via trial_io readref: references/frameworks.md, references/scientific.md, references/training.md.
- Did not inspect other trials, evaluation rubrics, scoring, design plans, or any new JAX skill files outside the supplied guidance.
- No other ordinary skill files were opened or used. No repository files were changed. No subagents were spawned or delegated.

Primary external documentation actually opened using web tools:

1. https://docs.kidger.site/diffrax/examples/neural_ode/ — native Equinox/Diffrax/Optax path and complete-state Markov assumption.
2. https://docs.kidger.site/diffrax/api/adjoints/ — RecursiveCheckpointAdjoint, numerical-solution differentiation, reverse-mode boundary, and approximate continuous backsolve gradients.
3. https://docs.kidger.site/diffrax/api/diffeqsolve/ — solve signature, explicit t0/t1 and dt0, maximum steps, throw=True, vmapped failure policy.
4. https://docs.kidger.site/diffrax/api/saveat/ — requested output times.
5. https://docs.kidger.site/equinox/api/transformations/ — filtered JIT/value-and-gradient behavior for mixed PyTrees.
6. https://docs.kidger.site/equinox/api/serialisation/ — leaf serialization and reconstruction against a like tree.
7. https://optax.readthedocs.io/en/latest/api/optimizers.html — optimizer API inventory; Adam and schedule references were visible, but not independently executed.

The scalar exponential fixture, analytic gradient, observation mask checks, and solver thresholds are adapted from the supplied scientific reference. The delivered code adds a deterministic scheduled Adam fit, a separate trajectory, causal persistence comparisons, post-fit numerical checks, future-only prediction parity, and Equinox full-state next-update recovery with two saves.

Explicit nonexecution: No delivered application/model code was executed, imported, compiled, traced, trained, differentiated, or tested in this session. No package installation or installed-version inspection was performed. Claimed package profile belongs to the supplied guidance, not a locally verified environment. Actual runtime numerical/learning/recovery results remain unmeasured. Only the trial helper's required start/reference reads, read-only external documentation retrieval, literal artifact writes, and read-only artifact verification were performed.
