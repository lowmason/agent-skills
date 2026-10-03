# CPU sine predictor test strategy

This implements the approved small JAX example. The data are clean sine waves
with random amplitude, phase, angular frequency, and context length. One target
per sequence is the sample immediately after its final real input.

| Invariant | Fixture and layer | Marker |
| --- | --- | --- |
| Inputs have `(batch, max_length)` shape, float32 values, integer lengths in the inclusive configured interval, and zero padding | Seeded synthetic batch | fast |
| The target immediately follows the real sequence | Fixed frequency and amplitude; independent sine recurrence oracle | fast |
| The same data key produces identical inputs, lengths, and targets | Two seeded batches | fast |
| Padding cannot change a prediction or contribute gradients | Perturb masked values in a mixed-length batch and extend padded width | fast |
| Prediction is one finite scalar per sequence, and gradient leaves are finite | Small mixed-length batch | fast |
| Saving and loading restores parameters, Adam moments, random key, configuration, and step | NPZ round trip at a temporary path | fast |
| Split training with a checkpoint produces the same final state as uninterrupted training | Two short deterministic CPU runs, same config | fast |
| Training improves independent validation error and beats last-sample persistence | Fixed training seed, 600 updates, fixed independent 512-example validation batch | slow |

Fast checks: `.venv/bin/python -m pytest -m 'not slow' -q`.
Full checks: `.venv/bin/python -m pytest -q`.
There are no network tests or external datasets. A `slow` marker is registered,
and unknown markers are errors. Training/validation quality is measured on the
declared synthetic distribution; it does not establish extrapolation quality.

The implementation stays in this sandbox, following the request to implement
the already approved plan without a new approval or session handoff.
