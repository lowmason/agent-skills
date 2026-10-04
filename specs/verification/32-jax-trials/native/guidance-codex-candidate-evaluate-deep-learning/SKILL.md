---
name: evaluate-deep-learning
description: >
  Use when benchmarking neural models, comparing checkpoints or methods,
  designing ablations, selecting models, or assessing deep-learning research
  claims — including held-out metrics, contamination, leakage, unequal compute
  budgets, variation across seeds, generative quality, or domain correctness.
license: MIT
metadata:
  author: Lowell Mason
---

# Evaluate Deep Learning

A neural comparison answers a stated question about a population, evaluation
procedure, and resource policy. Produce an inspectable protocol, the measured
results with their variation and limits, and a decision supported by those
results. Keep sample, training-run, sampling, and numerical uncertainty visible
as different quantities. Preserve useful inconclusive results: the next
measurement can be the main outcome.

## Boundary and reference selection

This skill owns benchmarking, held-out comparison, ablation, checkpoint
selection, domain correctness, and the neural experiment record. Model
implementation, learning diagnostics, and training changes belong to
**deep-learning**. Compilation, memory, sharding, synchronized timing, and
inference/cache performance belong to **optimize-jax**. For mixed work, use the
skill responsible for the immediate decision and add the other when its
responsibility arises. Model execution stays JAX; host-side NumPy arithmetic
and artifact bookkeeping can support the evaluation.

Tabular prediction is outside this version. Sequences, scientific models,
images, graphs/3D, generative models, and LLMs are included. A point estimate
neural run can have predictions and checkpoints without posterior draws. If
the task actually concerns posterior inference, use **bayesian-workflow**;
when choosing between neural and probabilistic alternatives, use
**recommend-probabilistic-model**. Ordinary neural evaluation needs no
`InferenceData`, NetCDF, ELPD, LOO, or ArviZ artifact.

Load [protocol.md](references/protocol.md) for a comparison, ablation, uncertainty
calculation, or selection decision. It contains the canonical `paired-evaluation`
CPU fixture. Load [domain-checks.md](references/domain-checks.md) for the relevant
model family's input, output, numerical, or generation claims. Load
[experiments.md](references/experiments.md) when planning, recording, resuming,
or comparing runs. These references supply the detail; read the relevant
sections before choosing a metric or implementing the check.

## 1. Establish the evaluation contract

Write the question in operational terms: the deployment/research population,
unit, target, and intended decision. A unit might be an independent trajectory,
a forecast origin with specified horizons, an image group, a whole graph, or a
prompt with repeated sampled completions. Name all axes and the nesting or
dependence among units. Record immutable data/split identifiers, the eligible
mask, evaluation mode, preprocessing and target availability, and exact
held-out input IDs. State what the test population leaves out.

Protect evaluation inputs from training, preprocessing fitting, prompt or
checkpoint selection, and tuning. Audit duplicates, group membership, temporal
information availability, and known pretraining overlap where relevant. If
training provenance is unavailable, record contamination as unresolved and
qualify the interpretation. A resampling procedure cannot repair a leaked or
repeatedly selected test set. Use **validate-data** for applicable input and
conclusion QA, with these neural/domain contracts supplied.

## 2. Prespecify metrics, comparison, and resources

Choose a primary metric, direction, units, denominator, and aggregation before
interpreting scores. Separate token-pooled, sample-macro, group, and horizon
weighting. Retain per-unit results so aggregation and failures are auditable.
Add secondary metrics that expose meaningful tradeoffs; label later metrics
exploratory. For generative tasks, connect quality, diversity/coverage, and
conditioning measurements to the actual intended use.

Choose meaningful baselines and document the architecture/checkpoint,
training configuration, optimizer/schedule, selection rule, and comparable
search effort. Fix a practical difference or cost/quality rule that would
justify the decision, plus stopping and failed-run handling. Use
**tune-hyperparameters** for search design with the appropriate neural objective
and splits, and **develop-testing-strategy** for a permanent invariant test plan.
Their whole-skill handoffs do not transfer posterior or table-specific artifacts.

Record per-run tokens/examples/steps and measured device time, FLOPs or money
when those resources matter. Tokens express training exposure; unspecified
architectures can spend different physical compute per token. Compare at
common budgets or show budget-performance curves and their schedule policy.
Distinguish an endpoint checkpoint comparison from a claim about the method.
For an ablation, state the intervention and control shared data, tuning,
training, and inference resources enough to identify that intervention.

## 3. Check units, variation, and domain behavior

Evaluate methods on identical held-out units where available, with explicit
identity/order checks and consistent masks/weights. Pair unit-level comparisons
on the same samples or justified clusters. Pair training runs only when the
experimental design actually shares compatible random factors; numeric seed
labels alone establish no pairing. Keep every planned run, its seed policy,
failures, and per-run score. Unequal run counts affect precision and design;
use the comparison appropriate to the actual sampling rather than dropping
runs to manufacture symmetry.

Report observed scores and differences before any inference. For uncertainty,
state the population, sampling unit, dependence assumptions, estimator, and
what is held fixed. Use cluster or temporal blocks when the data contract
requires them; repeat the complete nonlinear metric on resampled units.
Small seed counts constrain estimation even when a formula is available.
Interpret an interval for the actual difference; non-detection alone supplies
no equivalence conclusion. Numerical output is a result only after execution.

Complete a separate predictive-uncertainty slot: what distribution, probability,
or interval the model supplies, how calibration/coverage and sharpness are
assessed on held-out units, or why the model makes no predictive-uncertainty
claim. Variation across training seeds describes repeated training; it is not
by itself a calibrated distribution over a future target. Keep finite-test,
sampling, and solver/precision sensitivity distinct as well.

Apply the selected domain checks. Temporal windows need causality and
origin/horizon/stride contracts. Image evaluation needs preprocessing,
augmentation, and group policies. Graph/3D claims need relabeling and declared
transformation tests. Scientific claims need validated solver and gradient
references. Generative/LLM comparisons need frozen conditioning, prompt,
tokenizer, decoding, metric implementation, and contamination policies.

## 4. Deliver the comparison and decision

Return the following in order, using a table where several methods are compared:

| Output slot | Required content |
|---|---|
| Evaluation population | Unit/axes/dependence, held-out IDs, split/preprocessing/mask policy |
| Prespecified protocol | Primary/secondary metrics, weighting, baselines, ablations, tuning/selection, budgets and seed policy |
| Validity checks | Leakage/contamination findings, applicable domain checks, predictive-uncertainty assessment or explicit scope |
| Results | Per-run and per-unit evidence, observed difference, named uncertainty/sensitivity and executed-check status |
| Decision | Practical threshold/resource tradeoff, supported conclusion, limitations, and the next discriminating test |
| Run record | Run/parent/configuration/environment, artifacts, budget, status and decision from experiments.md |

A provisional operational choice can use constraints and observed evidence while
leaving method superiority unresolved. Name the evidence needed to change that
choice, such as balanced common-budget replications, a protected confirmation
set, a causal ablation, or a converged numerical cross-check. State which
proposed checks remain unexecuted and which hardware/checkpoint combinations
were actually tested.

## Common mistakes

| Symptom | Repair |
|---|---|
| Lower endpoint score gets a method-wide verdict | Identify the resource/selection contract and collect common-budget evidence |
| One collapsed average hides failures or long sequences dominate silently | Retain sample/seed axes, masks, denominators and failed runs |
| Shared seed IDs are called paired randomness | Declare shared random factors or use an unpaired run-level design |
| Every overlapping token/window becomes an independent replicate | Aggregate/resample actual independent units or justified blocks |
| Loose solver loss or low task loss becomes a correctness proof | Measure numerical convergence and declared transformation residuals separately |
| Seed spread is the only uncertainty field | Assess predictive probabilities/intervals separately or state their absence |
| Best-looking generations substitute for a sampling comparison | Freeze the sampling/conditioning protocol and inspect complete scored outputs |
