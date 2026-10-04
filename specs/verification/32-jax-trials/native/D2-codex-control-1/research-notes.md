# Research notes

Task source: executed exactly `python3 /private/tmp/jax-skill-trials-pAYZ0t/trial_io.py start /private/tmp/jax-skill-trials-pAYZ0t/native/D2-codex-control-1` as the first action. Read the complete output. It authorized inline complete analysis/code generation for a learnable continuous-time JAX model and explanation of gradient and fitted-behavior reliability. No task-specific reference filenames or additional guidance were supplied in that output, so no supplied-reference read was performed.

## Ordinary skills actually read and applied

- `/Users/lowell/.agents/skills/develop-testing-strategy/SKILL.md`: read completely; informed invariant-based tests, separating solver/gradient tests from synthetic recovery and fit validation, fixed seeds, and avoiding smoke-test-only claims. Its normal plan/implementation handoff was superseded by the explicit instruction to deliver an already-authorized inline complete analysis and code without a new approval/design workflow. The durable invariant/check plan is included in response.txt.
- `/Users/lowell/.agents/skills/clean-code/SKILL.md`: read completely; informed cohesive pure functions, descriptive names, explicit constants, and host-side data validation outside transformed JAX code.

## Primary external sources actually used

Accessed with the web tool during this trial:

1. https://docs.kidger.site/diffrax/api/saveat/ — saved observation times, dense/interpolated output API.
2. https://docs.kidger.site/diffrax/api/diffeqsolve/ — ODETerm/args, solve signature, default adjoint, max_steps, failure handling, vmap throw behavior.
3. https://docs.kidger.site/diffrax/api/adjoints/ — checkpointed discrete reverse differentiation, forward-mode restriction, ForwardMode option, and BacksolveAdjoint limitations.
4. https://docs.kidger.site/diffrax/api/stepsize_controller/ — PIDController tolerance arguments, ConstantStepSize, and step statistics.
5. https://docs.kidger.site/diffrax/usage/how-to-choose-a-solver/ — Tsit5 for non-stiff systems and precision warning for tight tolerances.
6. https://docs.jax.dev/en/latest/101/default_dtypes.html — default 32-bit behavior and global jax_enable_x64 setting.
7. https://docs.jax.dev/en/latest/notebooks/autodiff_cookbook.html — grad/value_and_grad and directional finite-difference checks.
8. https://optax.readthedocs.io/en/latest/getting_started.html — optimizer init/update/apply_updates pattern.

Initial discovery searches also returned Diffrax neural-ODE material and Equinox examples/FAQ, but the answer's delivered model uses a pure JAX parameter array and does not depend on Equinox. Non-primary search hits were not used as technical evidence. The attempted older JAX URL https://docs.jax.dev/en/latest/default_dtypes.html yielded no substantive content; the valid /101/ URL above was used instead.

## Delivery and nonexecution

Delivered a complete example for learnable damped rotation on different irregular observation grids, with noisy synthetic data, Optax fitting, exact-solution forward checks, fixed-step finite-difference checks, adaptive-gradient comparisons against an analytic objective, parameter recovery, held-out initial conditions and times, and tolerance sensitivity. Explained neural-vector-field extension, ragged/missing observations, uncertain initial states, and deterministic-model assumptions.

The delivered application/model code was NOT executed, imported, traced, compiled, or trained. No JAX environment was installed. All fit results, gradient errors, numerical assertions, and thresholds are proposed checks rather than claimed observed outcomes. Text editing of response.txt was performed with a literal shell heredoc and a Python text-only replacement; this did not execute any delivered model code. Final verification was a readback of artifact text and file sizes only.

Did not inspect other trial directories, rubrics, plans, scoring, or new JAX skill files. Did not spawn or delegate. Mutated only response.txt and research-notes.md inside the owned trial directory; the start helper may record its authorized read. No repository or skill-collection changes were made.
