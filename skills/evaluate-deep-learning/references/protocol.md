# Comparison protocol and paired evaluation

Load this reference for benchmarks, ablations, checkpoint selection, uncertainty
in differences, or implementing the evaluation reduction. It describes a
research comparison contract and one executable arithmetic fixture; it does
not supply a universal statistical test or model-ranking service.

## Question, baseline, and decision

Specify the population and intended generalization: a frozen checkpoint on a
fixed test set; expected performance of repeated training under a stated
budget; robustness to new domains; or a controlled intervention. The claim
determines what repeats. Include an inexpensive meaningful baseline (for
example seasonal persistence for forecasting) and a strong relevant baseline
with comparable access to data and search. Record selection and early-stopping
rules, search space/trials, training exposure, measured resources, and all
planned failures. **Use tune-hyperparameters** when designing the search.

Declare the primary metric, aggregation, useful effect threshold, cost rule,
stopping policy and confirmation data before viewing the final comparison.
Ablate a named component against its matched baseline and show remaining
confounds; multiple interventions require additional contrasts. A checkpoint
sweep chosen on the test set becomes exploratory evidence and needs independent
confirmation. **Use validate-data** for applicable input/conclusion QA and
**use develop-testing-strategy** to turn stable invariants into permanent tests.
These are whole-skill handoffs; bring the neural units/metrics into their scope.

Training tokens, optimizer steps, examples, time, FLOPs and money are different
budget dimensions. For unknown architectures, 3M tokens versus 1M tokens
establishes an exposure mismatch, not a measured threefold cost. Common-budget
checkpoints need an explicit schedule policy: a prefix of a longer schedule
may answer a different question than a separately planned short-budget run.
Compare method-by-budget curves with equalized tuning opportunities, then state
whether the decision prioritizes exposure, physical cost, latency or quality.

For errors A=[0.14,0.16] at 1M tokens and B=[0.13,0.18,0.14,0.12] at 3M,
means 0.15 and 0.1425 describe the supplied runs. The observed A-minus-B gap is
0.0075 in the given error units. The endpoint budgets and tiny unequal samples
leave repeatable method superiority and equivalence unresolved. Keep all six
runs. Next evidence is a common-budget grid/curves, balanced planned
replications, comparable tuning/selection, shared held-out IDs and a practical
decision rule. Same numeric seed labels require an actual random-factor mapping
before paired-run inference.

Sources: [Bouthillier et al. (2021), Accounting for Variance in Machine Learning
Benchmarks](https://arxiv.org/abs/2103.03098) motivates reporting multiple
sources of benchmarking variation; [Pineau et al. (2021), reproducibility
program report](https://jmlr.org/papers/v22/20-303.html) supports inspectable
experiment configurations and results. The resource/decision contract here is
original guidance, not a guarantee that a fixed run count suffices.

## Units, pairing, and uncertainty

Write prediction/target axes before reducing: seed, sample or group, time/token,
horizon, channel and stochastic draw as appropriate. Define eligibility and
whether long samples receive more weight. Token-pooled MSE sums eligible squared
errors divided by eligible token count; macro MSE averages sample MSEs. Both
are meaningful for different populations and generally differ. Reject empty
units or define their documented exclusion before comparison. Retain counts,
per-unit values and failures. Confirm identical held-out identities, order,
labels, weights and eligibility before a paired contrast.

Separate these estimands:

| Quantity | Repetition and interpretation |
|---|---|
| Training-run variability | Repeat initialization/data order/augmentation/search as declared; keep each run's full test score and configuration |
| Finite-test uncertainty | Resample independent evaluation units or whole justified clusters with both methods aligned; conditional on fitted models unless the design also repeats training |
| Generation Monte Carlo variability | Repeat sampled outputs for fixed prompt/condition/model; draws are nested within prompts and do not create extra independent prompts |
| Predictive uncertainty | Evaluate model probabilities/distributions/intervals against future held-out targets, including calibration/coverage and sharpness |
| Numerical sensitivity | Re-evaluate fixed parameters across solver/dtype/settings; this measures numerical dependence rather than data or predictive uncertainty |

Same seed integers need not share initialization or data randomness across
architectures. A blocked design can share data splits/order or augmentation
where meaningful while keeping independent streams for unrelated operations.
Document exactly which factors pair. Shared evaluation samples are a separate
pairing contract. Preserve unpaired extra runs; unequal counts alone do not
invalidate an appropriate unpaired estimate.

For iid independent units, a paired bootstrap or test can analyze differences
under its stated assumptions. For grouped data, sample whole groups; for
ordered dependent errors, choose a block/dependence procedure justified by the
actual series and inspect block-length sensitivity. Forecast horizon alone
does not determine dependence length. Nonstationarity, shared shocks and few
clusters can limit these procedures. Recompute corpus/nonlinear metrics on
each replicate rather than averaging an unrelated per-cell surrogate.
[Koehn (2004)](https://aclanthology.org/W04-3250/) provides paired resampling for
translation evaluation; [Politis and Romano, The Stationary Bootstrap](https://statistics.stanford.edu/technical-reports/stationary-bootstrap)
addresses weakly dependent stationary observations. Applicability and finite
sample adequacy remain properties of the chosen data/design.

Report the estimated difference and its uncertainty with named units and
conditioning; inspect arithmetic and actually run interval code before printing
values. Separate intervals for each method do not replace the interval/test for
the difference. Failure to detect a difference is not equivalence: that needs
prespecified meaningful bounds and a design precise enough to address them.
Show exploratory contrasts and selection limits. No resampling repairs leakage.

## Canonical CPU fixture: paired-evaluation

Axes are explicitly `(seed, sample, token)`; held-out samples have one, two,
and three eligible tokens. Per-sample MSE at seed 0 is `[1,4,9]`; pooled MSE
is `(1+8+27)/6 = 6`, while macro MSE is `14/3`. Seed 1 doubles residuals,
giving pooled MSE 24. Method B halves A's synthetic residuals, at a different
stated training exposure. The arrays simulate predictions without training a
model. The held-out-unit contrast averages each method over its own seeds;
run randomness is explicitly unpaired and no uncertainty estimate is computed.

The host checks validate eligibility/identity before the JAX reduction.
Padding is selected out before residual arithmetic, including nonfinite padding;
this is an evaluation-only fixture, not a gradient-safety claim for an upstream
network. [JAX where documentation](https://docs.jax.dev/en/latest/_autosummary/jax.numpy.where.html)
explains the selection API and separate gradient caveats. The fixture uses
float32 and hand-result tolerances 1e-6, not a neural x64 default.

```python cpu-example paired-evaluation
import jax.numpy as jnp
import numpy as np


def score_predictions(predictions, targets, valid_tokens):
    predictions = jnp.asarray(predictions, dtype=jnp.float32)
    targets = jnp.asarray(targets, dtype=jnp.float32)
    valid_tokens = np.asarray(valid_tokens)
    if predictions.ndim != 3 or targets.shape != predictions.shape[1:]:
        raise ValueError('Expected predictions (seed, sample, token) and targets (sample, token)')
    if predictions.shape[0] == 0 or predictions.shape[1] == 0:
        raise ValueError('Need nonempty seed and sample axes')
    if valid_tokens.dtype != np.bool_ or valid_tokens.shape != targets.shape:
        raise ValueError('Eligibility must be a boolean (sample, token) mask')
    counts = valid_tokens.sum(axis=1)
    if np.any(counts == 0):
        raise ValueError('Every sample needs an eligible target')
    if not np.isfinite(np.asarray(targets)[valid_tokens]).all():
        raise ValueError('Nonfinite eligible target')
    if not np.isfinite(np.asarray(predictions)[:, valid_tokens]).all():
        raise ValueError('Nonfinite eligible prediction')
    mask = jnp.asarray(valid_tokens)
    safe_predictions = jnp.where(mask[None, :, :], predictions, 0.0)
    safe_targets = jnp.where(mask, targets, 0.0)
    squared_errors = jnp.square(safe_predictions - safe_targets[None, :, :])
    sample_sums = squared_errors.sum(axis=2)
    sample_mse = sample_sums / jnp.asarray(counts)[None, :]
    pooled_mse = sample_sums.sum(axis=1) / counts.sum()
    return np.asarray(sample_mse), np.asarray(pooled_mse)


def held_out_difference(left, right):
    if left['sample_ids'] != right['sample_ids']:
        raise ValueError('Held-out identity/order mismatch')
    if left['valid_tokens'] != right['valid_tokens']:
        raise ValueError('Held-out eligibility mismatch')
    # Means over each method's runs are descriptive; run randomness is unpaired.
    return np.mean(right['sample_mse'], axis=0) - np.mean(left['sample_mse'], axis=0)


def expect_value_error(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError('Expected the invalid evaluation contract to fail')


sample_ids = ('trajectory-a', 'trajectory-b', 'trajectory-c')
valid_tokens = np.array([[True, False, False], [True, True, False], [True, True, True]])
targets = jnp.zeros((3, 3), dtype=jnp.float32)
residuals = jnp.array([[1.0, 99.0, 99.0], [2.0, 2.0, 99.0], [3.0, 3.0, 3.0]])
predictions_a = jnp.stack([residuals, 2.0 * residuals])
predictions_b = 0.5 * predictions_a
sample_a, pooled_a = score_predictions(predictions_a, targets, valid_tokens)
sample_b, pooled_b = score_predictions(predictions_b, targets, valid_tokens)
np.testing.assert_allclose(sample_a, [[1, 4, 9], [4, 16, 36]], rtol=1e-6, atol=1e-6)
np.testing.assert_allclose(pooled_a, [6, 24], rtol=1e-6, atol=1e-6)
np.testing.assert_allclose(sample_a.mean(axis=1), [14 / 3, 56 / 3], rtol=1e-6, atol=1e-6)
np.testing.assert_allclose(pooled_b, [1.5, 6], rtol=1e-6, atol=1e-6)

changed_predictions = jnp.where(jnp.asarray(valid_tokens)[None, :, :], predictions_a, jnp.inf)
changed_targets = jnp.where(jnp.asarray(valid_tokens), targets, jnp.nan)
changed_sample, changed_pooled = score_predictions(changed_predictions, changed_targets, valid_tokens)
np.testing.assert_array_equal(changed_sample, sample_a)
np.testing.assert_array_equal(changed_pooled, pooled_a)
expect_value_error(lambda: score_predictions(predictions_a.at[0, 0, 0].set(jnp.nan), targets, valid_tokens))
expect_value_error(lambda: score_predictions(predictions_a, targets, valid_tokens.astype(np.int32)))
empty_sample = valid_tokens.copy()
empty_sample[0] = False
expect_value_error(lambda: score_predictions(predictions_a, targets, empty_sample))

budget_a = {'tokens_per_run': 1_000_000, 'steps_per_run': 1000,
            'device_seconds_per_run': None, 'tuning_trials': 1}
budget_b = {'tokens_per_run': 3_000_000, 'steps_per_run': 3000,
            'device_seconds_per_run': None, 'tuning_trials': 1}
records = {}
for name, sample_scores, run_scores, budget in (
    ('A', sample_a, pooled_a, budget_a), ('B', sample_b, pooled_b, budget_b),
):
    records[name] = {
        'sample_ids': sample_ids, 'valid_tokens': valid_tokens.tolist(),
        'seed_ids': (0, 1), 'seed_policy': 'synthetic outputs; no paired training randomness',
        'axes': ('seed', 'sample', 'token'), 'sample_mse': sample_scores.tolist(),
        'seed_pooled_mse': run_scores.tolist(), 'budget': dict(budget),
    }
np.testing.assert_array_equal(records['A']['seed_pooled_mse'], [6, 24])
np.testing.assert_array_equal(records['B']['seed_pooled_mse'], [1.5, 6])
assert records['A']['budget'] == budget_a and records['B']['budget'] == budget_b
assert records['A']['seed_ids'] == (0, 1) and records['A']['axes'] == ('seed', 'sample', 'token')
np.testing.assert_allclose(held_out_difference(records['A'], records['B']),
                           [-1.875, -7.5, -16.875], rtol=1e-6, atol=1e-6)
reordered = dict(records['B'], sample_ids=sample_ids[::-1])
expect_value_error(lambda: held_out_difference(records['A'], reordered))
changed_eligibility = dict(records['B'], valid_tokens=empty_sample.tolist())
expect_value_error(lambda: held_out_difference(records['A'], changed_eligibility))
print('paired-evaluation: valid reductions, padding invariance, shared units, per-seed records passed')
```

Preserve prediction/label and preprocessing/split hashes in a real comparison;
this tiny fixture shares target arrays directly. Its valid tokens are reduction
weights, not independent training runs. Passing it establishes these local
arithmetic/contract checks under the recorded CPU profile. It provides no
statistical coverage, model-quality, physical-efficiency or superiority claim.
