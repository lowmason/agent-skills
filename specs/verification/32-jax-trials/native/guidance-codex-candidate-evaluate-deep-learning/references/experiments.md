# Neural experiment records

Load this reference when planning, recording, resuming or comparing neural runs.
Use an ordinary project document or an existing tracking backend with this
contract. It introduces no tracking service, ledger script, install dependency
or posterior-draw requirement. Keep records at the level needed to reconstruct
the stated experiment and interpret the decision.

## Record contract

| Field | Meaning and minimum useful detail |
|---|---|
| `run_id` | Unique run identifier; distinguish repetitions/seeds and evaluation reruns |
| `parent_run_id` | Predecessor/baseline record identifier, or null for an initial run |
| `hypothesis` | Claim being tested, population/metric and practical decision target |
| `change` | Exact intervention from parent/baseline; identify simultaneous changes |
| `data` | Immutable source/split identifiers or manifests/hashes; unit IDs, axes, masks/weights, preprocessing and availability/contamination policy |
| `model` | Architecture/checkpoint/tokenizer revisions and training/evaluation configuration, including precision, schedule and sampling/solver settings |
| `seed` | Initialization, data-order/augmentation and sampling seed policy; declare actual shared factors for any pairing |
| `environment` | Python/package versions, platform/backend/devices and relevant compiler/distributed configuration |
| `artifacts` | Recovery checkpoint, model export, predictions/completions and logs as applicable, with location/revision/hash and accessibility |
| `metrics` | Names/direction/units/denominators/aggregation; values by unit and run/seed where applicable, failures, uncertainty and its analysis contract |
| `budget` | Per-run/total tokens/examples/steps, measured device time or cost, sampling/inference budget and tuning effort as applicable; distinguish planned and actual |
| `status` | `planned`, `running`, `completed`, `failed` or `superseded`, with reason/coverage |
| `decision` | Observed result, useful-effect/cost policy, limitations and next action; include predictive-uncertainty assessment or explicit scope |

Use explicit unknown/null fields with reasons when information is unavailable.
A completed status means the declared run/check finished; it does not itself
establish model quality, reproducibility on another device, calibrated
predictions or a method-wide winner. Keep failed/superseded records and their
parent relationships. A new checkpoint evaluation can reference the training
record while recording its own inputs, protocol and environment.

## Artifacts serve different guarantees

A **recovery checkpoint** preserves the state required for the declared resume
boundary: model/optimizer and schedule position, randomness and data progress
as needed. Record the guarantee and reconstruction configuration; a successful
next-update restoration check is stronger than a file-save event. Use
deep-learning when implementing the recovery contract.

A **model export** packages parameters and the architecture/configuration,
preprocessing/tokenizer and version compatibility needed for inference. It can
omit optimizer/data-cursor state and therefore need not resume training.
**Predictions/completions** preserve unit IDs, targets/reference association,
masks and sampling metadata so the evaluation can be reproduced. **Logs**
preserve metrics, resource measurements, failures and check outputs. Hash or
version each applicable artifact; null with an explanation is appropriate for
an arithmetic fixture with no trained model. Neural point predictions need no
`InferenceData`, NetCDF, ELPD, LOO or ArviZ artifact. Use bayesian-workflow only
when the experiment actually performs posterior inference.

## Small completed record: canonical arithmetic fixture

This is the executed `paired-evaluation` CPU check in protocol.md. It records
synthetic outputs and supplied illustrative exposure metadata, not a trained
A/B experiment. The budget labels are retained by the check; they were not
consumed by training. A real multi-run experiment should give each actual
training run its own record and associate evaluation records with it.

```yaml
run_id: paired-evaluation-cpu-v1
parent_run_id: null
hypothesis: Valid-token reduction and held-out identity bookkeeping preserve sample/seed evidence.
change: Initial evaluation-arithmetic fixture; no model intervention.
data:
  source_id: paired-evaluation-v1-inline-literals
  split_id: synthetic-held-out-v1
  sample_ids: [trajectory-a, trajectory-b, trajectory-c]
  prediction_axes: [seed, sample, token]
  eligible_tokens_by_sample: [1, 2, 3]
  targets: zero-valued synthetic arrays
  preprocessing: none
  contamination: inapplicable to synthetic literals
model:
  architecture: no trained model; synthetic residual predictions
  checkpoint: null
  tokenizer: null
  training: none
  evaluation: float32 eligible-token pooled MSE; sample-macro MSE separately checked
seed:
  ids: [0, 1]
  policy: deterministic synthetic scales; no initialization/data-order randomness executed
  training_run_pairing: unpaired; numeric labels give no variance-reduction claim
environment:
  python: 3.13.8
  packages: {jax: 0.11.2, jaxlib: 0.11.2, numpy: 2.5.3}
  platform: macOS-26.6.2-arm64-arm-64bit-Mach-O
  backend: cpu
  devices: [CpuDevice-0]
artifacts:
  recovery_checkpoint: null # No training state exists.
  model_export: null # No learned model exists.
  predictions: inline deterministic arrays in paired-evaluation-v1
  logs: one canonical block selected/executed/passed by the CPU example runner
metrics:
  units: squared synthetic target units; lower is better
  A_sample_mse_by_seed: [[1, 4, 9], [4, 16, 36]]
  B_sample_mse_by_seed: [[0.25, 1, 2.25], [1, 4, 9]]
  A_pooled_mse_by_seed: [6, 24]
  B_pooled_mse_by_seed: [1.5, 6]
  A_sample_macro_mse_by_seed: [4.6666667, 18.6666667]
  B_minus_A_sample_mse_averaged_over_each_methods_seeds: [-1.875, -7.5, -16.875]
  checks: manual-reduction parity, changed-padding invariance, invalid-contract rejection, metadata preservation
budget:
  supplied_A_per_run: {tokens: 1000000, steps: 1000, device_seconds: null, tuning_trials: 1}
  supplied_B_per_run: {tokens: 3000000, steps: 3000, device_seconds: null, tuning_trials: 1}
  actual_training: none; exposure/step/tuning labels are illustrative metadata
  actual_check: one local CPU arithmetic fixture; training/device-time/cost unmeasured
status: completed
decision:
  result: Evaluation arithmetic and identity/record assertions passed.
  limitations: Synthetic outputs and unequal supplied budgets establish no method winner or physical efficiency.
  predictive_uncertainty: No predictive distribution or interval is supplied/evaluated.
  next_action: For a real comparison, freeze actual units/protocol, collect common-budget runs and domain checks.
```

## Comparing records

Confirm data/split/units, metric/aggregation, inference settings, tuning/selection,
budget and randomness contracts before joining score rows. Preserve each run's
values and failures; retain uncertainty at its actual unit. A parent link alone
does not certify a controlled ablation. If comparison conditions differ, name
the differing procedure and qualify the result or collect the matched contrast.
Keep the decision tied to the stated practical threshold and measured resource
tradeoff, with a concrete next discriminating test when evidence is incomplete.
