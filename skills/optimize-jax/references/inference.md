# JAX-native research generation and cache correctness

Load for autoregressive prefill/decode, KV caches, sampling, generation capacity
or checkpoint-dependent generation changes. Start with a small JAX-native math
fixture and a trusted full-prefix reference, then profile and scale a verified
model path. The fixture has no pretrained weights or language-quality claim.

## State and prediction alignment

Causal attention uses queries against preceding/current keys and weighted values;
a KV cache stores actual projected keys and values so decode can reuse the
prefix. It is not a recurrent hidden-state substitute. The
[attention paper](https://arxiv.org/abs/1706.03762) supplies the mathematical
context; the implementation and NumPy oracle here are original.

Declare these contracts before implementation:

| Item | Meaning in this fixture |
|---|---|
| Effective prompt | Masked physical padding is removed; valid tokens retain order and receive contiguous absolute positions starting at 0 |
| BOS/empty | An empty effective prompt is rejected; caller explicitly supplies BOS token 0 if desired |
| Cache | Fixed key/value arrays `(capacity,width)` and int32 valid length; cursor equals the next unwritten absolute position |
| Prefill | Consume each valid prompt token once; final logits predict the first new token |
| Decode | Sample/select a token from current logits, consume it once, then predict the following token |
| Mask | Attend only to written prefix including the current token; unwritten slots have zero probability |
| Capacity | Prompt length plus requested new count must fit; every append is checked before the private jitted write |
| Termination | New count is a hard bound; emitted EOS is included and consumed, then stop; zero-new consumes only the prompt |
| Randomness | A separate sampling key is split once per emitted categorical token; initialization seed has a different purpose |

This compaction policy is suitable for one sequence's synthetic test. A batched
model retaining physical left/right padding needs explicit valid lengths,
per-example position IDs and attention masks. Match the tokenizer/checkpoint
position convention; do not infer correctness from this compaction alone.

## Independent cache/math fixture

`cached-decode` uses a tiny untrained single-head attention layer with absolute
embeddings, residual output projection and vocabulary logits. The cached JAX
path processes one token against fixed arrays. The NumPy oracle recomputes the
complete Q/K/V matrices and triangular causal attention for every full prefix;
it never calls the cached helper. Tests compare every consumed-prefix logit and
every generation prediction vector, then exact greedy emitted tokens, across
multiple lengths/padding patterns and boundary counts. Fixed-key stochastic
replay is a separate actual categorical-generation test.

```python cpu-example cached-decode
import json
from operator import index

import jax
import jax.numpy as jnp
import numpy as np

CAPACITY = 8
WIDTH = 6
VOCABULARY = 9
BOS = 0
PAD = -999
RTOL = 2e-5
ATOL = 2e-5
rng = np.random.default_rng(sum(map(ord, 'cache-parameters')))
shapes = {
    'embedding': (VOCABULARY, WIDTH), 'position': (CAPACITY, WIDTH),
    'query': (WIDTH, WIDTH), 'key': (WIDTH, WIDTH),
    'value': (WIDTH, WIDTH), 'output': (WIDTH, WIDTH),
    'vocabulary': (WIDTH, VOCABULARY),
}
host_params = {name: (rng.normal(size=shape) * 0.25).astype(np.float32)
               for name, shape in shapes.items()}
params = jax.device_put(host_params)
jax.block_until_ready(params)


def full_prefix(tokens):
    # Independent all-prefix NumPy attention; no cache/state/helper reuse.
    tokens = np.asarray(tokens, dtype=np.int32)
    hidden = host_params['embedding'][tokens] + host_params['position'][:len(tokens)]
    queries = hidden @ host_params['query']
    keys = hidden @ host_params['key']
    values = hidden @ host_params['value']
    scores = queries @ keys.T / np.sqrt(np.float32(WIDTH))
    causal = np.tri(len(tokens), dtype=bool)
    scores = np.where(causal, scores, -np.inf)
    weights = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
    weights /= np.sum(weights, axis=-1, keepdims=True)
    residual = hidden + (weights @ values) @ host_params['output']
    return residual @ host_params['vocabulary']


def empty_cache():
    return {'key': jnp.zeros((CAPACITY, WIDTH), dtype=jnp.float32),
            'value': jnp.zeros((CAPACITY, WIDTH), dtype=jnp.float32),
            'length': jnp.asarray(0, dtype=jnp.int32)}


@jax.jit
def cached_step(model_params, cache, token):
    # Private kernel: append() proves its write-position/token preconditions.
    position = cache['length']
    hidden = model_params['embedding'][token] + model_params['position'][position]
    query = hidden @ model_params['query']
    keys = cache['key'].at[position].set(hidden @ model_params['key'])
    values = cache['value'].at[position].set(hidden @ model_params['value'])
    length = position + jnp.asarray(1, dtype=jnp.int32)
    valid = jnp.arange(CAPACITY) < length
    scores = keys @ query / jnp.sqrt(jnp.asarray(WIDTH, dtype=jnp.float32))
    weights = jax.nn.softmax(jnp.where(valid, scores, -jnp.inf))
    residual = hidden + (weights @ values) @ model_params['output']
    logits = residual @ model_params['vocabulary']
    return {'key': keys, 'value': values, 'length': length}, logits


def append(cache, token):
    position = int(jax.device_get(cache['length']))
    token = index(token)
    if not 0 <= position < CAPACITY:
        raise ValueError('cache append exceeds capacity')
    if not 0 <= token < VOCABULARY:
        raise ValueError('token outside vocabulary')
    return cached_step(params, cache, jnp.asarray(token, dtype=jnp.int32))


def valid_prompt(tokens, mask, new_count):
    tokens = np.asarray(tokens)
    mask = np.asarray(mask)
    if tokens.ndim != 1 or mask.shape != tokens.shape or mask.dtype != np.bool_:
        raise ValueError('one-dimensional tokens and matching boolean mask required')
    if not np.issubdtype(tokens.dtype, np.integer):
        raise ValueError('integer tokens required')
    if isinstance(new_count, (bool, np.bool_)):
        raise ValueError('integer generation count required')
    new_count = index(new_count)
    prompt = tokens[mask]
    if not len(prompt):
        raise ValueError('empty effective prompt; supply BOS explicitly')
    if np.any(prompt < 0) or np.any(prompt >= VOCABULARY):
        raise ValueError('valid prompt token outside vocabulary')
    if new_count < 0 or len(prompt) + new_count > CAPACITY:
        raise ValueError('invalid generation count or request exceeds capacity')
    return prompt.astype(np.int32), new_count


def prefill(prompt):
    cache = empty_cache()
    logits = None
    for token in prompt:
        cache, logits = append(cache, int(token))
    return cache, logits


def generate(tokens, mask, new_count, sampling_key=None, eos_id=None):
    prompt, new_count = valid_prompt(tokens, mask, new_count)
    if eos_id is not None and not 0 <= index(eos_id) < VOCABULARY:
        raise ValueError('EOS outside vocabulary')
    cache, logits = prefill(prompt)
    emitted = []
    predictions = []
    for _ in range(new_count):
        predictions.append(np.asarray(jax.device_get(logits)))
        if sampling_key is None:
            token = int(jax.device_get(jnp.argmax(logits)))
        else:
            sampling_key, token_key = jax.random.split(sampling_key)
            token = int(jax.device_get(jax.random.categorical(token_key, logits)))
        emitted.append(token)
        cache, logits = append(cache, token)
        if eos_id is not None and token == eos_id:
            break
    prediction_array = np.asarray(predictions, dtype=np.float32).reshape(-1, VOCABULARY)
    return np.asarray(emitted, dtype=np.int32), prediction_array, cache


def full_greedy(prompt, new_count, eos_id=None):
    prefix = list(map(int, prompt))
    emitted = []
    for _ in range(new_count):
        token = int(np.argmax(full_prefix(prefix)[-1]))
        emitted.append(token)
        prefix.append(token)
        if eos_id is not None and token == eos_id:
            break
    return np.asarray(emitted, dtype=np.int32)


def padding_variants(prompt):
    raw = np.asarray(prompt, dtype=np.int32)
    interspersed = np.full(2 * len(raw) + 1, PAD, dtype=np.int32)
    interspersed[1::2] = raw
    return [
        (raw, np.ones(len(raw), dtype=bool)),
        (np.concatenate(([PAD, PAD], raw)), np.array([False, False] + [True] * len(raw))),
        (np.concatenate((raw, [PAD])), np.array([True] * len(raw) + [False])),
        (interspersed, interspersed != PAD),
    ]


max_error = 0.0
logit_checks = 0


def check_logits(actual, expected):
    global max_error, logit_checks
    actual = np.asarray(jax.device_get(actual))
    np.testing.assert_allclose(actual, expected, rtol=RTOL, atol=ATOL)
    assert np.isfinite(actual).all()
    max_error = max(max_error, float(np.max(np.abs(actual - expected))))
    logit_checks += 1


prompts = [[BOS], [2, 4, 3], [3, 5, 4, 2, 6], [2, 3, 4, 5, 6, 7, 2],
           [2, 3, 4, 5, 6, 7, 2, 3]]
greedy_cases = 0
for prompt in prompts:
    cache = empty_cache()
    for position, token in enumerate(prompt):
        cache, logits = append(cache, token)
        check_logits(logits, full_prefix(prompt[:position + 1])[-1])
        assert int(cache['length']) == position + 1
    hidden = host_params['embedding'][prompt] + host_params['position'][:len(prompt)]
    np.testing.assert_allclose(np.asarray(cache['key'])[:len(prompt)],
                               hidden @ host_params['key'], rtol=RTOL, atol=ATOL)
    np.testing.assert_allclose(np.asarray(cache['value'])[:len(prompt)],
                               hidden @ host_params['value'], rtol=RTOL, atol=ATOL)
    remaining = CAPACITY - len(prompt)
    counts = sorted({0, min(1, remaining), min(2, remaining), remaining})
    for count in counts:
        expected_tokens = full_greedy(prompt, count)
        for physical, mask in padding_variants(prompt):
            emitted, predictions, cache = generate(physical, mask, count)
            np.testing.assert_array_equal(emitted, expected_tokens)
            assert len(predictions) == count
            assert int(cache['length']) == len(prompt) + count
            assert cache['key'].shape == cache['value'].shape == (CAPACITY, WIDTH)
            consumed = prompt + emitted.tolist()
            hidden = (host_params['embedding'][consumed]
                      + host_params['position'][:len(consumed)])
            np.testing.assert_allclose(np.asarray(cache['key'])[:len(consumed)],
                                       hidden @ host_params['key'], rtol=RTOL, atol=ATOL)
            np.testing.assert_allclose(np.asarray(cache['value'])[:len(consumed)],
                                       hidden @ host_params['value'], rtol=RTOL, atol=ATOL)
            for step, actual in enumerate(predictions):
                prefix = prompt + emitted[:step].tolist()
                check_logits(actual, full_prefix(prefix)[-1])
            greedy_cases += 1

# Dirty unwritten slots test cache masking; prompt padding above is a different test.
cache, _ = prefill([2, 4])
dirty = {'key': cache['key'].at[2:].set(1000.0),
         'value': cache['value'].at[2:].set(-1000.0), 'length': cache['length']}
_, clean_logits = append(cache, 3)
_, dirty_logits = append(dirty, 3)
check_logits(dirty_logits, full_prefix([2, 4, 3])[-1])
np.testing.assert_array_equal(dirty_logits, clean_logits)

sampling_key = jax.random.key(sum(map(ord, 'cache-sampling')))
physical, mask = padding_variants([2, 4, 3])[0]
first_sample, first_logits, _ = generate(physical, mask, 3, sampling_key)
second_sample, second_logits, _ = generate(physical, mask, 3, sampling_key)
np.testing.assert_array_equal(first_sample, second_sample)
np.testing.assert_array_equal(first_logits, second_logits)
for padded, padded_mask in padding_variants([2, 4, 3])[1:]:
    sample, prediction, _ = generate(padded, padded_mask, 3, sampling_key)
    np.testing.assert_array_equal(sample, first_sample)
    np.testing.assert_array_equal(prediction, first_logits)
for step, actual in enumerate(first_logits):
    check_logits(actual, full_prefix([2, 4, 3] + first_sample[:step].tolist())[-1])

eos_id = int(np.argmax(full_prefix([2])[-1]))
emitted, predictions, cache = generate([2], [True], 5, eos_id=eos_id)
np.testing.assert_array_equal(emitted, full_greedy([2], 5, eos_id))
assert emitted.tolist() == [eos_id]
assert predictions.shape == (1, VOCABULARY) and int(cache['length']) == 2
check_logits(predictions[0], full_prefix([2])[-1])

rejected = 0
invalid_requests = [([], [], 0), ([PAD], [False], 1), ([2], [True], -1),
                    ([2] * CAPACITY, [True] * CAPACITY, 1),
                    ([2] * (CAPACITY + 1), [True] * (CAPACITY + 1), 0),
                    ([VOCABULARY], [True], 0), ([2], [1], 0),
                    ([2], [True, False], 0)]
for tokens, mask, count in invalid_requests:
    try:
        generate(np.asarray(tokens, dtype=np.int32), np.asarray(mask), count)
    except ValueError:
        rejected += 1
    else:
        raise AssertionError('invalid request was accepted')
full_cache, _ = prefill([2] * CAPACITY)
try:
    append(full_cache, 3)
except ValueError:
    rejected += 1
else:
    raise AssertionError('append beyond final slot was accepted')
assert int(full_cache['length']) == CAPACITY

print(json.dumps({'scope': 'tiny single-head cache/math fixture',
                  'backend': jax.default_backend(), 'jax': jax.__version__,
                  'capacity': CAPACITY, 'width': WIDTH, 'vocabulary': VOCABULARY,
                  'dtype': 'float32', 'greedy_padding_cases': greedy_cases,
                  'logit_checks': logit_checks, 'rejected_requests': rejected,
                  'fixed_key_sample': first_sample.tolist(), 'eos_tokens': emitted.tolist(),
                  'max_reference_error': max_error, 'rtol': RTOL, 'atol': ATOL}, sort_keys=True))
```

These host guards are intentionally outside jit; the private fixed-shape kernel
assumes valid state produced by the wrapper. A compiled batched generation loop
needs the same preconditions and fixed carry structure, with per-example done
flags, valid lengths/positions and inactive-row masking. The reference's growing
prefix shapes are acceptable for correctness checks and are not its performance
baseline. This single-layer fixture proves neither multi-layer/RoPE/GQA cache
logic nor tokenizer/chat-template/checkpoint conversion, quantization quality or
accelerator speed. Approximate logits do not guarantee identical argmax near a
tie on every backend; exact token tests here apply to the actual fixed fixture.

## GPU generation loop

For GPU deployment, use the supported model's compiled sampler or a compiled
fixed-carry decode loop. Keep cache, positions, keys, per-example done flags and
inactive-row masks on device. Validate prompt/capacity inputs before entry;
avoid reading the cache cursor or each selected token back into Python to
drive the next step. Batch or deliberately stream host output according to the
request contract, and include required synchronization in end-to-end timing.
The host-controlled loop above is an inspectable correctness fixture; it is
not the default implementation for GPU generation. Check the compiled path
against full-prefix logits and the same EOS/padding/capacity cases on the target
GPU, with precision-specific tolerances, before measuring prefill/decode.

## Profile the established research path

Measure prefill completion, time to first emitted token and warm decode latency
with their distinct input/output boundaries. Record prompt/new-token length
distributions, batch size, capacity, precision, sampling policy and hardware.
Keep tokenizer, host synchronization and EOS handling in the request boundary
when they affect the target. Fixed arrays avoid growing cache shapes but compute
may still span allocated slots. A fresh full attention matrix for every growing
prefix has a cumulative cubic attention term; one-query cached attention has a
quadratic cumulative term when work follows valid length. This fixture uses
fixed-capacity score arrays and makes no empirical speed claim.

## Supported Tunix native generation

For an existing compatible Tunix model, use its documented native sampler/vanilla
rollout path. The [vanilla rollout documentation](https://tunix.readthedocs.io/en/latest/rollout.html#vanilla)
uses in-process JAX/Flax NNX, compiled prefill/decode and an explicit KV capacity.
It documents `RolloutConfig.kv_cache_size` covering maximum prompt plus generated
length, configurable EOS tokens, and `top_p=None` for greedy decoding. New
prompt/batch/generation shapes can trigger compilation. Check these semantics
against the installed version rather than copying another engine's knobs.

Match architecture and loader in the [Tunix models list](https://tunix.readthedocs.io/en/latest/models.html),
then establish checkpoint revision/license, parameter mapping, tokenizer IDs,
BOS/EOS/chat template, masks, positions and precision. Compare known prompts'
full-prefix logits against trusted checkpoint outputs before cached generation;
then apply per-step cache/greedy/padding/boundary/replay checks to that model.
Adapter/fine-tuned parameter synchronization and train/eval state also belong to
the compatibility contract. Use **deep-learning** when the task becomes training
or post-training quality.

This CPU profile contains no Tunix/model/checkpoint. The recipe is verified by
current primary documentation only; actual loader/sampler execution, checkpoint
logits, hardware memory and supported model/device combination remain pending.
No large download or engine installation is required for the local math gate.

## Optional MaxText scale route

Use MaxText when an established JAX model needs its documented scale/placement
path. The current [offline inference guide](https://maxtext.readthedocs.io/en/latest/tutorials/inference.html#offline-inference)
uses the MaxText model implementation through its vLLM adapter and host sampling/
orchestration; it explicitly assumes a v6e-8 VM. Selecting the MaxText architecture
and compatible adapter matters to the JAX model path, grounded in the
[MaxText JAX architecture](https://maxtext.readthedocs.io/en/latest/reference/architecture/jax_ai_libraries_chosen.html).
The guide's separate server workflow is outside this research scope.

The [checkpoint conversion guide](https://maxtext.readthedocs.io/en/latest/guides/checkpointing_solutions/convert_checkpoint.html)
lists supported mappings and scan/unscan format constraints. Conversion is not
validated merely because files load: compare tokenizer conventions, parameter
layout and forward logits on known prompts at a declared precision/tolerance,
then cache logits and generation. Some upstream conversion-check recipes use a
separate original-framework checker; it is not the default model execution path
or a dependency of these fixtures. Use trusted reference logits where available
and record how they were obtained.

No MaxText/adapter, TPU mesh, conversion or real checkpoint is executed here.
Choose a pinned compatible MaxText environment and actual hardware separately;
validate distributed placement/recovery and memory as described in
[sharding](sharding.md), then measure the real prefill/decode workload. Model
support in a source table and tiny cache parity are not evidence of arbitrary
checkpoint compatibility or performance.
