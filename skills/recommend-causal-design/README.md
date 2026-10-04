# recommend-causal-design

Choose a causal research design before estimation and write a memo another
analyst can implement. The skill separates the requested effect from the
effect the available design identifies, makes causal structure and assumptions
explicit, and offers an evidence plan when identification fails.

Example invocation:

> Use recommend-causal-design to assess whether our eligibility policy changed
> earnings. Compare credible designs, keep the requested population ATE separate
> from any cutoff-local effect, and write training-policy/causal-design.md.

Coverage: experiments, observational adjustment/weighting, IV, RDD, DiD/event
studies, synthetic control, interrupted time series and longitudinal regimes.
The skill produces a recommendation; it does not fit a model or run causal
diagnostics. No extra Python packages are required for the recommendation path.

See [SKILL.md](SKILL.md) for the procedure,
[reporting.md](references/reporting.md) for the memo contract, and
[worked-example.md](references/worked-example.md) for a cutoff-policy example.
Identification is software-independent; optional profiling uses Polars and
a Bayesian handoff uses NumPyro/JAX.

The planning workflow is selectively adapted from Robson Tigre's
`causal-planner` and Alexandre Andorra's `causal-inference`, both MIT licensed.
Pinned source records and verified primary literature are in
[sources.md](references/sources.md). The method guidance and memo template are
newly written; no upstream estimators, book/paper copies or automated causal
grading are included. Retained upstream MIT notices are bundled in
[LICENSE](LICENSE); repository-level attribution is also recorded in `NOTICE`
and `LICENSE-causal-design-sources`.
