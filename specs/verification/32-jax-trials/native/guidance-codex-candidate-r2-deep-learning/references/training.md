# Training, state and recovery

Load for an objective/update implementation, unstable learning, explicit model
state/randomness, numerical correctness, or resumable checkpoints. Domain
contracts are in the neighboring references; comparative evidence belongs to
evaluate-deep-learning.

## Loss and update contract

Choose the eligible unit before reducing. Pooled token/timestep MSE is
`sum(valid errors) / count(valid targets)`; averaging sequence means instead
gives equal trajectory weight. For loss rows `[1,100,100]` and `[3,5,100]` with
only positions 0, 0 and 1 eligible, the pooled loss is 3. The padding values
carry no statistical weight. An empty eligible batch needs an explicit rejected
or skipped-update status and is excluded from metric denominators; a zero from
a denominator clamp does not mean perfect performance.

Check finite eligible inputs, predictions, loss, and differentiated gradient
leaves in the small correctness run. Sanitizing undefined targets before differentiation
can be necessary: masking a NaN after a nonlinear operation can still produce
NaN gradients. The examples below require finite arrays, including padding,
and reject empty batches at the host boundary. Production compiled rejection
can use an explicit checked/status path consistent with its data loader.

Separate parameters from mutable statistics, recurrent state and PRNG streams.
Evaluation fixes parameters, disables dropout, and uses the declared fitted
normalization state. NNX-aware transforms propagate legal state mutations;
[the optimizer API](https://flax.readthedocs.io/en/stable/api_reference/flax.nnx/training/optimizer.html)
selects leaves through `wrt` and accepts the model in `update(model, grads)`.
[JAX random-number guidance](https://docs.jax.dev/en/latest/random-numbers.html)
explains independent key splitting. Derive typed keys with `jax.random.split`
or `jax.random.fold_in`; any arithmetic on integer seeds occurs before calling
`jax.random.key`. [Typed-key documentation](https://docs.jax.dev/en/latest/jax.random.html)
describes why key buffers are not ordinary integer arrays. Record stream
progression for data order, augmentation, dropout and generation. A driver's
training transition includes assigning the returned key/cursor as well as the
mutated model/optimizer. Keep a recovery comparison isolated, or continue with
its complete post-update state; a stale key/cursor repeats progress with
already-updated parameters.

For the tiny learning assertion, retain the same bounded batch/fixture for
initial and final loss and declare its evaluation/randomness policy. A loader
cursor can advance during training; compare learning on a separately fixed
fixture at both endpoints. Comparing the loss at cursor 0 with the loss at
cursor N measures different inputs and does not establish fixed-fixture
learning. The sequence example evaluates both endpoints deterministically.

Record schedule units as optimizer updates or data units. With accumulation,
combine loss numerators and eligible-unit counts across microbatches before
normalizing their accumulated gradients; unequal-length microbatches are not
equal-weight batches by default. Advance optimizer/schedule once per effective
update. Apply global-norm clipping to the intended accumulated gradient, with
a measured threshold and its clipped fraction. Optax's
[MultiSteps wrapper](https://optax.readthedocs.io/en/latest/api/optimizer_wrappers.html#optax.MultiSteps)
provides accumulation mechanics; its configured averaging must match the loss
weighting contract.

Select precision for the workload: inputs, parameter/master storage, compute,
reductions and optimizer moments can have different dtypes. Float32 is the
small neural-fixture default here; a scientific derivative reference separately
chooses float64. Confirm finite gradients and reference agreement before a
mixed-precision change, then measure its performance through optimize-jax.

## Canonical sequence correctness example

This is a two-lag next-sample model for fixed-frequency sine sequences with
variable lengths and independent phases. It supplies a causal small baseline,
not a long-context architecture. There is no dropout or normalization state;
`train()`/`eval()` declare mode, and evaluation is deterministic. Validation
uses its own fixed phase stream. The bounded fixed-training run tests
learnability; its loss reduction is not a generalization claim.

```python cpu-example nnx-sequence-training
import jax
import jax.numpy as jnp
import numpy as np
import optax
from flax import nnx

SEED = sum(map(ord, 'sequence-correctness'))
TRAIN_STEPS = 150


def require_units(mask):
    if not np.asarray(mask).any():
        raise ValueError('batch has no eligible targets')


def valid_mean(values, mask):
    return jnp.where(mask, values, 0.0).sum() / mask.sum()


hand_losses = jnp.array([[1.0, 100.0, 100.0], [3.0, 5.0, 100.0]])
hand_mask = jnp.array([[True, False, False], [True, True, False]])
np.testing.assert_allclose(valid_mean(hand_losses, hand_mask), 3.0)
changed_padding = jnp.where(hand_mask, hand_losses, -999.0)
np.testing.assert_allclose(valid_mean(changed_padding, hand_mask), 3.0)
try:
    require_units(jnp.zeros_like(hand_mask))
except ValueError:
    pass
else:
    raise AssertionError('empty eligible batch was accepted')


def sine_fixture(key, lengths):
    time = jnp.arange(12, dtype=jnp.float32)[None, :]
    phase = jax.random.uniform(key, (len(lengths), 1), maxval=2 * jnp.pi)
    waves = jnp.sin(phase + 0.25 * time)
    waves = jnp.where(time < lengths[:, None], waves, 0.0)
    features = jnp.stack((waves[:, :-2], waves[:, 1:-1]), axis=-1)
    targets = waves[:, 2:]
    mask = jnp.arange(10)[None, :] < lengths[:, None] - 2
    require_units(mask)
    assert features.shape == (len(lengths), 10, 2)
    assert targets.shape == mask.shape
    assert np.isfinite(np.asarray(features)).all()
    assert np.isfinite(np.asarray(targets)).all()
    return features, targets, mask


class LagForecaster(nnx.Module):
    def __init__(self, rngs):
        self.hidden = nnx.Linear(2, 16, rngs=rngs)
        self.output = nnx.Linear(16, 1, rngs=rngs)

    def __call__(self, features):
        return self.output(jnp.tanh(self.hidden(features)))[..., 0]


def objective(model, features, targets, mask):
    return valid_mean(jnp.square(model(features) - targets), mask)


@nnx.jit
def train_step(model, optimizer, features, targets, mask):
    loss, grads = nnx.value_and_grad(objective)(model, features, targets, mask)
    finite = jnp.isfinite(loss)
    for leaf in jax.tree.leaves(grads):
        finite = finite & jnp.isfinite(leaf).all()
    optimizer.update(model, grads)
    return loss, finite


train_key, validation_key, model_key = jax.random.split(jax.random.key(SEED), 3)
lengths = jnp.array([5, 7, 9, 12], dtype=jnp.int32)
training = sine_fixture(train_key, lengths)
validation = sine_fixture(validation_key, lengths)
assert int(training[2].sum()) == 25
model = LagForecaster(nnx.Rngs(params=model_key))
optimizer = nnx.Optimizer(model, optax.adam(0.02), wrt=nnx.Param)
model.eval()
initial = float(objective(model, *training))
model.train()
for _ in range(TRAIN_STEPS):
    loss, finite = train_step(model, optimizer, *training)
    assert bool(finite), 'nonfinite loss or gradient'
model.eval()
final = float(objective(model, *training))
assert final < 0.2 * initial, (initial, final)
assert int(optimizer.step[...]) == TRAIN_STEPS
validation_loss = float(objective(model, *validation))
assert np.isfinite(validation_loss)
np.testing.assert_array_equal(model(validation[0]), model(validation[0]))
changed_targets = jnp.where(training[2], training[1], 999.0)
np.testing.assert_allclose(objective(model, *training),
                           objective(model, training[0], changed_targets, training[2]))
print(f'train {initial:.6f} -> {final:.6f}; validation {validation_loss:.6f}')
```

When this fixture fails, isolate mask/target alignment, selected gradient leaves,
actual parameter updates, mode and scales before increasing the workload.
A project can keep its own working model: these are required check contracts,
not an obligation to replace it with this two-lag network.

## Recovery versus export

A recovery checkpoint includes dynamic model statistics and parameters,
optimizer moments, update/schedule position, required random streams and data
progress. Declare its boundary: last successful step, next epoch or saved best.
Reconstruct/validate architecture, optimizer and dataset/preprocessing/tokenizer
configuration, plus the relevant package environment. Load and validate one
saved reconstruction configuration before constructing resumed data, objective,
loader, model or optimizer; use that configuration for all those factories.
After the next update, compare the full model tree and every optimizer leaf,
including Adam moments and internal scheduler counts, in addition to loss,
external step, schedule output, key and data cursor. Equal next loss and step
alone do not establish equal parameter updates.

For periodic saves, select unique progress-specific directories or declare the
checkpoint manager/replacement policy. Test two completed saves followed by
restore-latest, including its saved configuration and progress. Inference
export needs portable model weights/configuration and its preprocessing contract.

[Orbax's checkpoint guide](https://orbax.readthedocs.io/en/latest/guides/checkpoint/orbax_checkpoint_101.html)
documents PyTree save/restore and asynchronous completion. The pattern below
uses `StandardCheckpointer`, two absolute progress-specific paths and
`wait_until_finished()`. It saves pure dynamic NNX state; a JSON companion
stores the original static configuration. Public NNX State replacement mutates
the target state in place before `nnx.update`.

## Canonical next-update recovery example

The next batch is a deterministic function of a saved cursor; stochastic input
augmentation and dropout consume a saved typed JAX key. The model contains no
running normalization statistics and has no hidden recurrent carry. Dropout
receives its key explicitly. The guarantee is the next training update on this
same CPU/profile/configuration, including the generated batch and randomness.
Two completed saves at steps 3 and 5 exercise periodic checkpointing; restoring
the latest selects step 5. The optimizer's internal schedule count and external
step are both compared after update 6, along with every model/optimizer leaf.
A different loader needs its own order/epoch/within-epoch cursor guarantee.

```python cpu-example nnx-checkpoint-resume
import json
from pathlib import Path
import tempfile

import jax
import jax.numpy as jnp
import numpy as np
import optax
import orbax.checkpoint as ocp
from flax import nnx

SEED = sum(map(ord, 'sequence-recovery'))
CONFIG = {
    'seed': SEED,
    'width': 8,
    'frequency': 0.25,
    'length': 7,
    'learning_rate': 0.01,
    'final_learning_rate': 0.001,
    'transition_steps': 20,
    'dropout_rate': 0.1,
    'input_noise': 0.02,
    'rng_impl': 'threefry2x32',
    'dtype': 'float32',
    'data': 'original-sine-phases-cursor-v1',
}


class StochasticLagModel(nnx.Module):
    def __init__(self, config, rngs):
        self.hidden = nnx.Linear(2, config['width'], rngs=rngs)
        self.dropout = nnx.Dropout(rate=config['dropout_rate'])
        self.output = nnx.Linear(config['width'], 1, rngs=rngs)

    def __call__(self, features, dropout_key):
        hidden = jnp.tanh(self.hidden(features))
        hidden = self.dropout(hidden, rngs=dropout_key)
        return self.output(hidden)[..., 0]


def make_training(config, initialization_key):
    model = StochasticLagModel(config, nnx.Rngs(params=initialization_key))
    schedule = optax.linear_schedule(config['learning_rate'],
                                     config['final_learning_rate'],
                                     config['transition_steps'])
    optimizer = nnx.Optimizer(model, optax.adam(schedule), wrt=nnx.Param)
    model.train()
    return model, optimizer, schedule


def batch_at(config, cursor):
    time = jnp.arange(config['length'], dtype=jnp.float32)[None, :]
    phases = jnp.array([0.15, 0.8], dtype=jnp.float32)[:, None] + 0.07 * cursor
    waves = jnp.sin(phases + config['frequency'] * time)
    lengths = jnp.array([5, 7], dtype=jnp.int32)
    waves = jnp.where(time < lengths[:, None], waves, 0.0)
    features = jnp.stack((waves[:, :-2], waves[:, 1:-1]), axis=-1)
    mask = jnp.arange(config['length'] - 2)[None, :] < lengths[:, None] - 2
    assert bool(mask.any())
    return features, waves[:, 2:], mask


@nnx.jit
def train_step(model, optimizer, features, targets, mask, dropout_key):
    def objective(model):
        errors = jnp.square(model(features, dropout_key) - targets)
        return jnp.where(mask, errors, 0.0).sum() / mask.sum()

    loss, grads = nnx.value_and_grad(objective)(model)
    finite = jnp.isfinite(loss)
    for leaf in jax.tree.leaves(grads):
        finite = finite & jnp.isfinite(leaf).all()
    optimizer.update(model, grads)
    return loss, finite


def advance(model, optimizer, key, cursor, config):
    next_key, augmentation_key, dropout_key = jax.random.split(key, 3)
    features, targets, mask = batch_at(config, cursor)
    features = features + config['input_noise'] * jax.random.normal(
        augmentation_key, features.shape)
    loss, finite = train_step(model, optimizer, features, targets, mask, dropout_key)
    assert bool(finite)
    return float(loss), next_key, cursor + 1


def snapshot(model, optimizer, key, cursor):
    return {
        'model': nnx.state(model).to_pure_dict(),
        'optimizer': nnx.state(optimizer).to_pure_dict(),
        'key_data': jax.random.key_data(key),
        'cursor': jnp.array(cursor, dtype=jnp.int32),
    }


def restore_nnx(obj, pure_state):
    state = nnx.state(obj)
    state.replace_by_pure_dict(pure_state)
    nnx.update(obj, state)


def assert_same_tree(left, right):
    assert jax.tree.structure(left) == jax.tree.structure(right)
    for before, after in zip(jax.tree.leaves(left), jax.tree.leaves(right)):
        if np.issubdtype(np.asarray(before).dtype, np.inexact):
            np.testing.assert_allclose(before, after, rtol=1e-6, atol=1e-6)
        else:
            np.testing.assert_array_equal(before, after)


initialization_key, key = jax.random.split(
    jax.random.key(CONFIG['seed'], impl=CONFIG['rng_impl']))
model, optimizer, schedule = make_training(CONFIG, initialization_key)
cursor = 0
with tempfile.TemporaryDirectory(prefix='nnx-resume-') as directory:
    root = Path(directory).resolve()
    with ocp.StandardCheckpointer() as checkpointer:
        for checkpoint_step in (3, 5):
            while cursor < checkpoint_step:
                _, key, cursor = advance(model, optimizer, key, cursor, CONFIG)
            progress = root / f'step-{int(optimizer.step[...]):08d}'
            progress.mkdir()
            (progress / 'config.json').write_text(json.dumps(CONFIG, sort_keys=True))
            saved = snapshot(model, optimizer, key, cursor)
            checkpointer.save(progress / 'state', saved)
            checkpointer.wait_until_finished()
        completed = sorted(root.glob('step-*'), key=lambda path: int(path.name[5:]))
        assert [int(path.name[5:]) for path in completed] == [3, 5]
        latest = completed[-1]
        loaded_config = json.loads((latest / 'config.json').read_text())
        assert loaded_config == CONFIG  # Validate before all resumed factories.
        reconstruction_key = jax.random.fold_in(jax.random.key(
            loaded_config['seed'], impl=loaded_config['rng_impl']), 999)
        restored_model, restored_optimizer, restored_schedule = make_training(
            loaded_config, reconstruction_key)
        target = snapshot(restored_model, restored_optimizer,
                          jax.random.key(0, impl=loaded_config['rng_impl']), 0)
        loaded = checkpointer.restore(latest / 'state', target=target)
        restore_nnx(restored_model, loaded['model'])
        restore_nnx(restored_optimizer, loaded['optimizer'])
        restored_key = jax.random.wrap_key_data(loaded['key_data'],
                                               impl=loaded_config['rng_impl'])
        restored_cursor = int(loaded['cursor'])
        assert_same_tree(saved, snapshot(restored_model, restored_optimizer,
                                         restored_key, restored_cursor))
        assert restored_cursor == 5
        np.testing.assert_allclose(schedule(optimizer.step[...]),
                                   restored_schedule(restored_optimizer.step[...]))
        next_loss, next_key, next_cursor = advance(model, optimizer, key, cursor, CONFIG)
        resumed_loss, resumed_key, resumed_cursor = advance(
            restored_model, restored_optimizer, restored_key, restored_cursor,
            loaded_config)
        np.testing.assert_allclose(next_loss, resumed_loss, rtol=1e-6, atol=1e-6)
        uninterrupted = snapshot(model, optimizer, next_key, next_cursor)
        resumed = snapshot(restored_model, restored_optimizer, resumed_key, resumed_cursor)
        assert_same_tree(uninterrupted['model'], resumed['model'])
        # All optimizer leaves: moments, internal schedule count and external step.
        assert_same_tree(uninterrupted['optimizer'], resumed['optimizer'])
        assert_same_tree(uninterrupted['key_data'], resumed['key_data'])
        assert next_cursor == resumed_cursor == 6
        assert int(optimizer.step[...]) == int(restored_optimizer.step[...]) == 6
        np.testing.assert_allclose(schedule(optimizer.step[...]),
                                   restored_schedule(restored_optimizer.step[...]))
        assert not np.array_equal(jax.random.key_data(key),
                                  jax.random.key_data(next_key))
        key, cursor = next_key, next_cursor
        restored_key, restored_cursor = resumed_key, resumed_cursor
print('recovery: next loss, model, Adam/schedule, step, RNG and cursor agree')
```

This establishes same-environment next-update parity. It does not establish
cross-version recovery, a different device topology, or distributed loader
progress. Sharded restoration, multi-host save participation and recovery after
a hardware change require a tested target/sharding and data-state contract.
