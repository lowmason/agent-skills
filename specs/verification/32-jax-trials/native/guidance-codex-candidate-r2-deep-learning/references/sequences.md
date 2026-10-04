# Sequences and time-series

Load when forecasting, classifying sequences, choosing recurrent/transformer/
state-space architectures, or handling causal inputs and variable lengths.
Use [training.md](training.md) for the canonical NNX training example and
recovery check; this reference adds the sequence contract without duplicating
that source.

## Choose information flow before architecture

Start with persistence, seasonal persistence or a small causal lag model for
forecasting. Define the forecast origin, context length and prediction horizon.
One-step teacher-forced error, direct multi-horizon error and autoregressive
rollout error answer different questions. Future covariates are usable only
when they will actually be known at the origin.

| Choice | Useful when | Contract to establish |
|---|---|---|
| GRU/LSTM or causal recurrence | Streaming state, modest contexts, limited compute | State initialization/reset, scan axis, carry shape, truncation and boundary policy |
| Causal transformer | Content-dependent access across a context warrants attention cost | Causal + padding attention, positions, context capacity, token/target shift |
| State-space architecture | Long contexts and recurrent execution motivate structured state | Discretization/input dependence, state reset, parallel/serial parity, actual JAX implementation availability |
| Causal lag network | A small local-history baseline can express the task | Feature/target alignment and each lag's availability |

The original [Transformer paper](https://arxiv.org/abs/1706.03762) establishes
attention-based sequence modeling. [Mamba](https://arxiv.org/abs/2312.00752)
provides a selective state-space design; a paper's hardware performance does
not establish a local JAX kernel/checkpoint path. For implemented recurrent
primitives, consult the
[NNX recurrent API](https://flax.readthedocs.io/en/stable/api_reference/flax.nnx/nn/recurrent.html).

## Shapes, splits and masks

Record `(batch, time, channels)` or the chosen alternative and transform axes
explicitly. A sequence of length L has L-1 one-lag next-step targets, or L-2
when the first target requires two preceding samples. The canonical fixture
uses two causal lags with one shared frequency and independent sine phases;
it tests this local forecast path, not arbitrary long-memory behavior.

Keep all windows from one subject/trajectory in its assigned split unless the
deployment protocol deliberately permits within-series temporal forecasting.
For temporal forecasting, training ends before validation origins; account for
overlapped context and target horizons. Fit scaling on the training split.
When validation rolls forward, identify when observed values become available
and when predictions feed back. Use evaluate-deep-learning for comparisons
across horizons, seeds, and rolling-origin designs.

Right-padding a causal model places padding after the useful prefix. In a
bidirectional encoder or noncausal attention model, valid output positions
still need attention/padding control. Loss masking alone cannot prevent padded
inputs or future targets from entering a representation. Derive target masks
from actual lengths/availability, and choose pooled timestep weighting versus
equal trajectory weighting explicitly.

At chunk boundaries, reset recurrence for independent sequences; carry it only
for the same stream with declared truncation and gradient policy. If a padded
scan computes extra steps, keep the required final state at the last valid
index or mask the carry update. If examples pack multiple sequences, use
boundary-aware attention/positions and exclude cross-boundary targets.

## Training diagnostics

Use finite loss/gradient checks and fixed tiny-data learning from training.md.
Declare dropout and normalization behavior during training and evaluation;
evaluation starts from the state the deployment protocol will have. Inspect
per-horizon error and the persistence baseline before interpreting the average.
A low teacher-forced loss can coexist with unstable rollouts. A context-length
increase changes both information and compute, so compare it under an explicit
protocol through evaluate-deep-learning.

Typical failures are an off-by-one target mask, a hidden state shared across
independent series, a normalization fit on future data, packed-sequence leakage,
and validation that silently feeds future truths to a claimed rollout forecast.
Construct tiny fixtures around the actual boundary to isolate each one.
