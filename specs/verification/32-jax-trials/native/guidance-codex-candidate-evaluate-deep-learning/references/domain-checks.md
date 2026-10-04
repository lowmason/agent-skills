# Domain checks and interpretation

Load the sections relevant to the model family's correctness or research claim.
Each section maps a declared input/output contract to a concrete test and the
meaning of its result. Model execution remains JAX. These are evaluation recipes,
not downloaded models, benchmark implementations or evidence of accelerator
compatibility. Use deep-learning for model/training changes; use optimize-jax
when timing, memory or execution parity becomes the immediate question.

## Sequence and time-series models

Record the series/entity, information cutoff, context/window length, forecast
origin, output horizon, stride, target units and the refit/update policy. Label
prediction axes `(run, series, origin, horizon, channel)` as applicable. Declare
whether weighting is per issued forecast, target timestamp, horizon or series:
one target may recur in multiple windows. Keep horizons separate where the
usefulness or difficulty differs; prespecify any aggregate weights.

- **Causality:** construct a feature-availability audit at every origin, including
  preprocessing fit dates and publication/vintage times. Change unavailable
  future inputs and confirm predictions at that origin remain unchanged where
  the architecture promises causality. A causal mask cannot fix a future-fitted
  scaler, leaked lag construction or unavailable feature.
- **Held-out split:** use chronological train/validation/test partitions matching
  the deployment question. Audit target intervals that straddle boundaries;
  choose a purge/gap appropriate to label availability and dependence. Historic
  context from before a test origin can be legitimate; distinguish it from
  fitting on held-out outcomes or unplanned online refitting.
- **Dependence:** paired losses use the same series/origin/horizon/target IDs.
  Overlapping windows are dependent evaluation cells, not independent runs.
  Aggregate by justified entities or use temporal blocks/dependence estimates
  with stated assumptions and length sensitivity. Shared panel shocks can
  invalidate independent-series resampling. Horizon-minus-one is no universal
  dependence cutoff for arbitrary stride, seasonality or long memory.

Interpret a result as performance under that origin/horizon/refit contract.
Use protected confirmation origins when selection has consumed validation
periods. [Hyndman and Athanasopoulos, time-series cross-validation](https://otexts.com/fpp3/tscv.html)
provides the rolling-origin formulation. [Politis and Romano, stationary
bootstrap](https://statistics.stanford.edu/technical-reports/stationary-bootstrap)
addresses stationary weak dependence; its assumptions must be checked for the
actual loss process. The causality/split audit is an original contract check,
not an assertion that blocking repairs leakage.

## Images and vision

Freeze decoder, channel order, crop/resize/interpolation/antialiasing, range,
normalization and label mapping. Fit learned preprocessing only on training
inputs. Record evaluation mode, running statistics, and any test-time
augmentation. Evaluate two methods on the same decoded image IDs with their
stated preprocessing; if native pipelines differ, distinguish the full-pipeline
comparison from a controlled architecture ablation.

Split at the deployment independence level: patient, video/source, acquisition
session, camera/site or scene where those groups exist. Audit group IDs and
near duplicates across partitions. Verify labels remain aligned after geometric
augmentation, and distinguish augmentation used during training from the
frozen inference rule. For stochastic test-time augmentation, retain all draws
under its planned aggregation rather than selecting a favorable view.

Check a small known-image pipeline fixture and stratify prespecified meaningful
subgroups/domain shifts. Report task metrics and group weighting; global
accuracy can conceal a shift failure. [WILDS (Koh et al., 2021)](https://proceedings.mlr.press/v139/koh21a.html)
provides primary examples of site, time and location shifts. This checklist
requires the project's group/data evidence; a particular benchmark does not
establish another dataset's independence or deployment validity.

## Graphs, geometry, and declared symmetry

State the symmetry and representation before testing: graph/node relabeling;
SO(3) proper rotations; O(3) rotations plus reflections/inversion; SE(3)
translations plus proper rotations; or a smaller domain group. Specify how all
inputs and outputs act, including scalar, polar vector, axial vector and tensor
channels. For O(3), declare parity; an SO(3) claim alone supplies no inversion
requirement. Node outputs usually permute; graph-level aggregation is invariant.

For a transformation `g`, compare the full inference pipeline's `f(g·x)` with
`rho_out(g)·f(x)`. Transform coordinates, edge/relative features and every
covariant input consistently. Check identity, several proper rotations,
composition, relabelings, boundary cases and, when declared, translation and
inversion/reflection. Apply the same node permutation to features and edge
indices; compare node outputs with the corresponding permutation and invariant
graph outputs directly. Freeze randomness or specify a stochastic coupling.

Report absolute and scale-normalized residuals using dtype/scale-aware tolerances,
plus a known positive and deliberately symmetry-breaking negative control.
Test preprocessing, neighbor construction and readout alongside the model.
Passing finite sampled transformations is empirical evidence on tested inputs;
all-group guarantees require the architectural/construction argument and its
prerequisites. A constant-zero output can pass a symmetry test while being
useless, so assess nontrivial task behavior separately. Low loss is no proof of
commutation. [e3nn-jax irreps documentation](https://e3nn-jax.readthedocs.io/en/latest/api/irreps.html)
defines its representation/parity interface; application tests still need the
project's declared action, pipeline and output contract. No claim here requires
replacing mathematically valid existing JAX algebra with a particular library.

## Scientific models and neural differential equations

Record observation units/times and masks, interpolation, vector field, solver,
controller/tolerances, maximum steps, precision, adjoint, and training/evaluation
settings. Physics-informed or operator models also need boundary/initial
conditions, conservation/residual units, discretization/resolution and the test
regime (new parameters, forcing, geometry or resolution). Separate task error
from physical/numerical correctness.

1. **Freeze a checkpoint and sweep evaluation settings.** Save outputs at the
   same observation times. Check solve status and finite eligible outputs at
   every setting; retain failure counts and rejected/accepted step counts. A
   step count is not a function-evaluation count. Report NFE only if the actual
   evaluations are instrumented or an appropriate documented counter exists.
2. **Validate the reference.** Compare successive tolerances and/or independent
   solver/step-size refinements until changes are below the declared accuracy
   target, with a known analytic small problem as a positive control. Confirm
   actual array/parameter dtypes and x64 availability when using float64.
   Merely requesting a tiny tolerance does not create an exact solution.
3. **Audit gradients.** State whether differentiation targets the discretized
   solve or a continuous adjoint. On a fixed small case, compare parameter
   derivatives/directional gradients with an analytic result or a finite-
   difference epsilon sweep, controlling dtype and solve accuracy. Adaptive
   step changes and cancellation can affect the reference. Report norm/direction
   differences and any unconverged region instead of selecting one epsilon.
4. **Separate training and evaluation effects.** Cross-evaluate checkpoints
   trained at several settings under a validated common numerical policy.
   Repeat planned training runs and compare at stated budgets. A lower loose-
   solver test error can motivate several hypotheses; the mechanism, monotonic
   numerical error and generalization improvement are measured questions.
5. **Complete the uncertainty field.** State what uncertainty over a future
   trajectory/target is supplied and assess calibration/coverage and sharpness
   on held-out trajectories. For a deterministic model, state that no predictive
   interval/distribution was evaluated. Training-seed spread, finite-test
   uncertainty and solver sensitivity remain separately named results.

[Diffrax Solution](https://docs.kidger.site/diffrax/api/solution/) documents result
status and solve statistics; [Diffrax adjoints](https://docs.kidger.site/diffrax/api/adjoints/)
distinguishes differentiating the numerical solve from continuous-adjoint
backsolves. [JAX dtypes/x64](https://docs.jax.dev/en/latest/101/default_dtypes.html)
explains why requested float64 needs an enabled x64 policy. These contracts do
not imply the recipe, gradients or domain model were executed here. Choose
accuracy targets relative to observation scale, precision and the decision.

## Predictive uncertainty across domains

An uncertainty claim is about a future observation conditional on the inputs
and the stated model/procedure. Record the probability/distribution/quantile/
interval construction, calibration data and evaluation population. Assess
classification calibration with reliability summaries and proper scores;
assess regression/trajectory intervals with coverage at declared levels and
sharpness/width, by meaningful prespecified groups or horizons. Report finite-
sample uncertainty in these assessments and shift limits. Fit any calibrator
on a separate calibration partition and evaluate it on protected data.

Training-run standard deviation and repeated-generation spread answer different
questions. An ensemble can supply a predictive distribution only after its
construction and calibration are specified/tested; seed count alone gives no
coverage guarantee. A deterministic point predictor may honestly make no
predictive-uncertainty claim. [Guo et al. (2017), On Calibration of Modern Neural
Networks](https://proceedings.mlr.press/v70/guo17a.html) provides primary
classification-calibration evidence; the regression/trajectory assessment
contract above must be implemented for the actual task. Posterior draws are
only relevant when the model/procedure actually uses them.

## Generative models: quality, diversity, conditioning

State the data population and held-out reference set; the unit may be a condition
or prompt with nested generated samples. Freeze checkpoint, condition mapping,
sampler/solver, number of steps, noise schedule, guidance/truncation, output
shape, precision, random-seed policy and postprocessing. Compare methods under
a declared sampling-resource budget and retain complete generated sets, including
failures. Report sensitivity curves when quality/diversity changes with guidance
or compute.

Choose complementary quality/fidelity, diversity/coverage and conditioning
metrics plus useful human/task assessments. For feature-space FID or related
metrics, pin feature extractor/checkpoint, preprocessing and metric
implementation, reference statistics and sample count. Inspect group/condition
coverage and nearest-neighbor memorization checks; a favorable scalar can hide
mode loss or training-data reproduction. Repeated samples from one condition do
not create new independent conditions. Human comparisons need blinded order,
written rubric, annotation protocol and uncertainty over appropriate items.

Report held-out likelihood/objective separately from generated sample utility:
diffusion denoising loss or flow-matching loss is a training objective, not a
complete quality/diversity evaluation. [Parmar et al., aliased resizing and GAN
evaluation](https://arxiv.org/abs/2104.11222) establishes that preprocessing can
change image metric conclusions; [Kynkäänniemi et al. (2019)](https://proceedings.neurips.cc/paper/2019/hash/0234c510bc6d908b28c70ff313743079-Abstract.html)
separates feature-space quality and coverage. Such metrics depend on the chosen
representation and samples; they do not guarantee semantic quality or deployment
usefulness. No images or model weights are bundled here.

## LLM prompts, likelihood, and decoded outputs

Record model/checkpoint and tokenizer revision, vocabulary/special tokens,
chat template, prompt text, system/in-context examples, truncation/context
length, completion masking, answer extraction, decoding settings, stop rules,
max output tokens and evaluator version. Compare the same task instances;
fix prompt/example policies before test inspection. If model-native templates
are needed, declare a pipeline comparison and show template sensitivity instead
of silently claiming identical inputs. Sampling draws nest within prompt IDs.

- **Likelihood:** check causal shifts and eligible completion tokens; distinguish
  summed sequence log probability from token-mean cross entropy. Report token
  counts and units. Per-token perplexity across different tokenizers is not a
  direct common-unit comparison; use an explicitly compatible alternative or
  qualify the tokenizer-specific values.
- **Decoded utility:** score task success/quality, failure modes and diversity
  under a frozen extraction/rubric. Reward-model or model-judge scores need
  evaluator identity, prompt/order policy and bias checks against independent
  human/task evidence. A preference-training reward is not independent validation.
- **Contamination:** audit known training/validation/test overlap, near duplicates
  and prompt/example leakage. Record training provenance limits and dataset
  release/cutoff information. An absent known match does not prove unseen data;
  use independent/temporal/task variants when they answer the same question.
- **Resources:** retain input/output tokens and generation settings as well as
  measured inference cost/latency when needed. Best-of-N, longer outputs or a
  larger sampling budget changes the tested procedure.

[HELM (Liang et al., 2022)](https://arxiv.org/abs/2211.09110) motivates common
scenarios, standardized evaluation conditions and multiple metrics;
[Lee et al., Deduplicating Training Data Makes Language Models Better](https://arxiv.org/abs/2107.06499)
provides primary evidence on repeated data and train-test overlap. Apply these
contracts to the actual JAX checkpoint/tokenizer pipeline. CPU arithmetic
checks cannot certify a real tokenizer, pretrained model, contamination audit,
judge or GPU/TPU generation implementation.
