# Research notes

Task source: executed only the instructed first-read helper command:
`python3 /private/tmp/jax-skill-trials-pAYZ0t/trial_io.py start /private/tmp/jax-skill-trials-pAYZ0t/native/E3-codex-control-1`.
It supplied an authorized inline question concerning neural ODE solver error and a 3D rotation-equivariance claim.

## Ordinary skills actually read

- `/Users/lowell/.agents/skills/develop-testing-strategy/SKILL.md`: applied invariant-first design, reproducibility, shape checks, and independent controls. The authorized task requires inline delivery and forbids extra artifacts; no separate approval or plan workflow was introduced.
- `/Users/lowell/.agents/skills/verification-before-completion/SKILL.md`: distinguished delivery/static verification from empirical passing evidence. The answer explicitly reports model/diagnostic code as unexecuted.
- `/Users/lowell/.agents/skills/clean-code/SKILL.md`: used descriptive names and separated solving, observation scoring, numerical checks, and group actions.

No new task-specific JAX guidance, other trials, evaluation rubric, scoring, or plan files were inspected. No agents were spawned or delegated.

## External primary sources actually consulted

All accessed through the web tool; no remote application/model code was downloaded or executed.

- https://docs.kidger.site/diffrax/api/stepsize_controller/ — local error control, tolerances, constant-step and adaptive controllers.
- https://docs.kidger.site/diffrax/usage/how-to-choose-a-solver/ — precision and stiff/nonstiff solver selection.
- https://docs.kidger.site/diffrax/api/adjoints/ — discrete differentiation versus continuous adjoints and checkpoint reverse-mode support.
- https://docs.kidger.site/diffrax/api/diffeqsolve/ — solve signature, arguments, `max_steps`, failure handling and `throw=False`.
- https://docs.kidger.site/diffrax/api/solution/ — result object and statistics context; search for `num_accepted_steps` on this page found no match. The code records the actual statistics dictionary generically and uses documented `num_steps` for gradient diagnostics.
- https://docs.kidger.site/diffrax/further_details/faq/ — work-precision comparisons, precision and tolerance comparability.
- https://docs.jax.dev/en/latest/101/default_dtypes.html — x64 configuration before arrays and actual dtype checks.
- https://docs.jax.dev/en/latest/automatic-differentiation.html — numerical directional-gradient checks and `value_and_grad`.
- https://docs.jax.dev/en/latest/benchmarking.html — compilation warm-up and synchronization for timings.
- https://docs.jax.dev/en/latest/jax.random.html — explicit keys and splitting random streams.
- https://papers.neurips.cc/paper/2020/file/15231a7ce4ba789d13b722cc5c955834-Paper.pdf — original SE(3)-Transformer primary paper; Section 2.3 defines equivariance, Section 4 reports a separate transformed-output residual.

Search results additionally exposed these official pages, used for orientation rather than separately quoted: JAX configuration options, arrays, asynchronous dispatch; Diffrax getting started; the original paper's arXiv page. No secondary sources were relied on.

## Nonexecution and verification

No delivered application/model code was run, including `diagnostic_controls`; there are no empirical solver results, gradient results, training comparisons, or model-equivariance results. No dependency installation or runtime test was performed. The delivered Python block is a diagnostic harness to connect to actual model/data adapters, with independent analytic and symmetry controls. Checks of output-file existence, content and Python syntax via AST parsing are static delivery verification only, and do not establish runtime correctness.

Only `response.txt` and `research-notes.md` were written in the owned trial directory, aside from the instructed helper's first-read log. The repository and other trials were not mutated.
