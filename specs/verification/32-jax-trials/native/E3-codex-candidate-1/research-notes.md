# Research notes

Task: E3-codex-candidate-1. The substantive response is in response.txt.

## Supplied guidance actually used

- The full evaluate-deep-learning main guidance was supplied by the trial_io start operation.
- references/protocol.md, read through trial_io readref: evaluation contract, actual units, separate uncertainty sources, resource/selection fairness, paired units versus unpaired training randomness.
- references/domain-checks.md, read through trial_io readref: Scientific models and neural differential equations; Graphs, geometry, and declared symmetry; Predictive uncertainty across domains.
- references/experiments.md, read through trial_io readref: planned run status, parent/configuration/data/environment/artifact/budget/decision records.

## Ordinary skills actually read and used

- /Users/lowell/.agents/skills/clean-code/SKILL.md: descriptive names, cohesive functions, explicit contracts, control fixtures. No adjacent repository code was edited.
- /Users/lowell/.agents/skills/verification-before-completion/SKILL.md: distinguish fresh artifact verification from model/test execution; no claim that unexecuted numerical or symmetry checks passed.

No ordinary skill required additional user approval for this authorized inline analysis/code delivery.

## Primary sources actually consulted

- https://docs.kidger.site/diffrax/api/solution/ — Solution.ys/result/stats and RESULTS.successful/failure status.
- https://docs.kidger.site/diffrax/api/diffeqsolve/ — call signature, SaveAt, controller, max_steps and throw=False.
- https://docs.kidger.site/diffrax/api/adjoints/ — RecursiveCheckpointAdjoint differentiates the numerical solution; BacksolveAdjoint continuous-adjoint approximations and target distinction.
- https://docs.kidger.site/diffrax/api/stepsize_controller/ — step-size controller API, PID tolerance context.
- https://docs.jax.dev/en/latest/101/default_dtypes.html — explicit x64 policy for float64.
- https://e3nn-jax.readthedocs.io/en/latest/api/irreps.html — degree/parity and representation matrices for O(3)/SO(3).

The answer uses original evaluation reasoning and code; the primary documentation supports the cited API and representation facts. The QR-generated rotations are checked for orthogonality and determinant, and are not claimed to be a uniform Haar sample. Fixture thresholds and numerical settings are illustrative, not empirically validated prescriptions for an unknown model.

## Explicit nonexecution and scope

- Did not execute delivered application/model code, including JAX/Diffrax fixtures, gradients, solver sweeps, rotation checks, training, benchmarking, or device compatibility checks.
- Did not inspect other trials, rubrics, scoring, plans, or new JAX skill files outside the supplied snapshot.
- Did not spawn or delegate.
- Did not edit the skill collection or repository.
- Mutations limited to response.txt, research-notes.md, and the authorized helper read log.
- Final verification is limited to reading and checking these text artifacts, including optional syntax parsing without execution; it cannot establish runtime correctness or any model claim.
