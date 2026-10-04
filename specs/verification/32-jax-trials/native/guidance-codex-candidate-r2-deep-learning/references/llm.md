# Language-model training and post-training

Load for autoregressive pretraining, SFT, LoRA/QLoRA, preference optimization,
reward-based updates, or checkpoint/tokenizer/model compatibility. Neural model
execution stays JAX. This reference supplies small objective/state contracts;
large checkpoint loading and accelerator recipes have separate verification
limits.

## Establish a supported loading path

Record exact architecture/configuration, artifact revision and format, tokenizer
revision/vocabulary, special-token IDs, chat template, dtype and device mesh.
Match embedding/output dimensions, tied weights, parameter layout and positional
conventions. Run a small forward/logit comparison to the source checkpoint under
identical tokens before adaptation. A vocabulary match alone cannot establish
chat-template or positional compatibility.

[Tunix's supported model table and AutoModel loader](https://tunix.readthedocs.io/en/latest/models.html)
cover selected Gemma/Llama/Qwen variants. Its documented
`AutoModel.from_pretrained` accepts a supported model identity and JAX mesh;
check that exact mapping. Hugging Face can supply artifacts/tokenizers while
JAX executes the model. The
[Transformers v5 migration guide](https://github.com/huggingface/transformers/blob/main/MIGRATION_GUIDE_V5.md)
records removal of its JAX backend; a current generic FlaxAutoModel promise
would not supply a supported loading path.

## Select the objective and trainable state

| Stage | Data/objective contract | State to record |
|---|---|---|
| Pretraining/continued pretraining | Next-token likelihood on the intended corpus; document/packing boundaries, token budget and split contamination | All selected model leaves, optimizer/schedule, data progress and random streams |
| SFT | Prompt/response or messages with the intended chat template; completion-only or explicitly full-sequence CE | Initial checkpoint, selected leaves, truncation/masks and recovery |
| LoRA/QLoRA | The selected adaptation objective, low-rank target projections and any quantized frozen base representation | Adapter rank/scale, named trainable leaves, quantization recipe and immutable base |
| DPO/preference optimization | Common-prompt chosen/rejected pairs and a declared immutable reference policy | Initial policy, reference checkpoint/adapter identity or cached log-probability manifest, beta, masks and pair units |
| Reward-based training | On-policy completions plus a declared reward, baseline/advantage and regularization rule | Rollout-policy version, old/reference log-probabilities, reward/baseline state, generation and optimizer state |

[Tunix algorithms](https://tunix.readthedocs.io/en/latest/algorithms.html)
provide SFT/PEFT, DPO and reward-based paths. Choose the stage according to the
research objective and available supervision. Keep reward scoring separate
from held-out task success: increasing a proxy reward can exploit that proxy.
[LoRA](https://arxiv.org/abs/2106.09685) trains low-rank updates;
[QLoRA](https://arxiv.org/abs/2305.14314) additionally uses a quantized frozen
base. [Qwix](https://github.com/google/qwix) is the JAX tooling used by the
linked Tunix PEFT recipe.

Verify trainable selection through actual updates and unchanged frozen
parameters. Optimizer-frozen parameters may have nonzero raw gradients. If
LoRA B starts at zero, A's initial gradient can be zero while B's gradient and
first update are nonzero. The fixture below tests this exact condition.
If the policy/adapter is passed directly as an NNX module, use `nnx.grad` or
`nnx.value_and_grad` for the initial SFT/DPO derivative check as well as each
training update, with the intended leaf filter. The
[NNX transformation contract](https://flax.readthedocs.io/en/stable/guides/transforms.html)
preserves its graph/state semantics; a functional split/merge boundary can
instead expose array state to plain JAX. The canonical array-only objective
math below uses `jax.grad` at that valid boundary.

## Shifts, attention and preference semantics

For logits at position t, the next-token label is token t+1. Shift both target
availability and completion membership to that target position. Padding masks,
causal attention/position masks, packing boundaries and loss masks have
separate jobs. A completion-only loss still allows attention to the prompt.
After truncation/shifting, require eligible completion tokens or mark the
example/pair excluded; an empty shifted mask is not a successful zero loss.
State BOS/EOS policy and whether EOS contributes to the response objective.

For the selected real recipe, write the model-facing attention/position
contract. An eligible autoregressive query q can attend to nonpadding keys k
with k <= q; packed data additionally requires matching query/key segment IDs.
Apply any architecture-specific local window. Record position IDs, padding
positions and whether positions/cache reset at segment boundaries, preserving
the checkpoint/recipe convention. Completion-loss eligibility alone does not
supply this relation. [Flax's attention API](https://flax.readthedocs.io/en/stable/api_reference/flax.nnx/nn/attention.html)
distinguishes attention masks, causality and input positions; map the relation
to the chosen recipe's actual interfaces. If segment-isolated packing is not
supported by that recipe, the first run can use one document per example.

Require a tiny forward check on that real path: under deterministic evaluation,
perturb only padding or a different packed segment; the unchanged segment's
eligible logits/loss must stay equal within declared dtype tolerance. Retain
its target labels, masks and position IDs. For causal isolation, perturb future
tokens and compare earlier query logits/loss at unchanged target positions.
Use a hand-checked query/key relation and a two-segment fixture when packing.
This remains a real-path prerequisite; the synthetic array block below does
not execute or verify attention, packing or positional behavior.

For SFT, divide pooled completion NLL by actual eligible-token count. For
standard DPO, sum completion log-probabilities within each response, then
average the preference loss over eligible pairs. Length normalization defines
a changed objective and needs consistent policy/reference treatment. With
`Delta = (log pi(chosen)-log pi(rejected))
- (log ref(chosen)-log ref(rejected))`, minimize
`-log sigmoid(beta*Delta)`. If policy equals reference, loss is log(2).
The primary objective is [DPO](https://arxiv.org/abs/2305.18290). Equal margins
can also give log(2) for distinct policies: this sanity value alone cannot
establish reference identity. When initializing from SFT, validate the immutable
checkpoint/adapter/manifest and compare individual chosen and rejected
completion log-probabilities against the frozen SFT snapshot under identical
tokens/masks. Check those identities separately from the DPO loss value.

When the reference is the SFT policy, preserve its trained adapter in an
immutable reference, merge it into that reference, or cache its log-probabilities
with checkpoint/tokenizer/mask identities. Disabling the trained SFT adapter
yields the base policy; use that only when the declared reference is the base.
A shared prompt, chosen/rejected ordering and the same masking/tokenization
contract are required to interpret the log-ratio.

For reward-based updates, define who generated each rollout, sampling settings,
termination, reward scale/eligibility, old-policy likelihoods, reference KL and
the baseline/advantage estimator. Group-relative methods need multiple valid
completions per prompt and explicit handling of zero reward variance. PPO-like
methods need the configured value/baseline and clipping contract. The
[Tunix rollout documentation](https://tunix.readthedocs.io/en/latest/rollout.html)
describes its native JAX generation path. Generation/cache execution issues go
to optimize-jax; task/preference/reward comparisons go to evaluate-deep-learning.

## Canonical token/preference/update checks

The vocabulary is synthetic: 0 is padding, 1 a start token, and 2–4 ordinary
symbols. Two examples contain one and two completion targets. No checkpoint,
real tokenizer or attention implementation is loaded. This establishes shift,
loss-mask, log-probability/reference and update-selection math; real attention,
packing, chat templates and converted logits need their own small checks.

```python cpu-example llm-token-masks
import jax
import jax.numpy as jnp
import numpy as np
import optax

VOCABULARY = 5
TOKENS = jnp.array([[1, 2, 3, 0, 0], [1, 4, 2, 3, 0]], dtype=jnp.int32)
ATTENTION = jnp.array([[True, True, True, False, False],
                       [True, True, True, True, False]])
COMPLETION = jnp.array([[False, False, True, False, False],
                        [False, False, True, True, False]])


def target_mask(attention, completion):
    return attention[:, :-1] & attention[:, 1:] & completion[:, 1:]


def require_completions(mask):
    if not np.asarray(mask).any(axis=1).all():
        raise ValueError('each included sequence needs a shifted completion target')


def token_statistics(logits, tokens, attention, completion):
    mask = target_mask(attention, completion)
    log_probabilities = jax.nn.log_softmax(logits[:, :-1, :], axis=-1)
    target_log_probabilities = jnp.take_along_axis(
        log_probabilities, tokens[:, 1:, None], axis=-1)[..., 0]
    sequence_sums = jnp.where(mask, target_log_probabilities, 0.0).sum(axis=1)
    token_loss = -sequence_sums.sum() / mask.sum()
    return token_loss, sequence_sums, mask


mask = target_mask(ATTENTION, COMPLETION)
require_completions(mask)
np.testing.assert_array_equal(mask, [[False, True, False, False],
                                    [False, True, True, False]])
assert int(mask.sum()) == 3
uniform = jnp.zeros((2, 5, VOCABULARY), dtype=jnp.float32)
loss, sequence_sums, _ = token_statistics(uniform, TOKENS, ATTENTION, COMPLETION)
np.testing.assert_allclose(loss, np.log(VOCABULARY), rtol=1e-6)
np.testing.assert_allclose(sequence_sums,
                           [-np.log(VOCABULARY), -2 * np.log(VOCABULARY)], rtol=1e-6)
favored = uniform.at[:, :-1, :].add(3.0 * jax.nn.one_hot(TOKENS[:, 1:], VOCABULARY))
favored_loss = token_statistics(favored, TOKENS, ATTENTION, COMPLETION)[0]
wrong_shift = uniform.at[:, :-1, :].add(
    3.0 * jax.nn.one_hot(TOKENS[:, :-1], VOCABULARY))
assert float(favored_loss) < 0.4 * float(loss)
assert float(favored_loss) < float(token_statistics(
    wrong_shift, TOKENS, ATTENTION, COMPLETION)[0])
source_mask = jnp.concatenate((mask, jnp.zeros((2, 1), dtype=bool)), axis=1)
changed_ineligible = jnp.where(source_mask[:, :, None], favored,
                               jnp.array([-20.0, 10.0, 30.0, -10.0, 5.0]))
np.testing.assert_allclose(token_statistics(changed_ineligible, TOKENS,
                                            ATTENTION, COMPLETION)[0], favored_loss)
only_first_token = jnp.zeros_like(COMPLETION).at[:, 0].set(True)
try:
    require_completions(target_mask(ATTENTION, only_first_token))
except ValueError:
    pass
else:
    raise AssertionError('shifted-empty completion was accepted')
sft_gradients = jax.grad(lambda logits: token_statistics(
    logits, TOKENS, ATTENTION, COMPLETION)[0])(favored)
assert np.isfinite(np.asarray(sft_gradients)).all()
np.testing.assert_array_equal(np.asarray(sft_gradients)[~np.asarray(source_mask)], 0.0)

CHOSEN = jnp.array([[1, 2, 3, 0, 0], [1, 2, 3, 3, 0]], dtype=jnp.int32)
REJECTED = jnp.array([[1, 2, 4, 0, 0], [1, 2, 4, 4, 0]], dtype=jnp.int32)
reference_logits = uniform.at[:, :, 3].set(0.5)
reference_chosen = jax.lax.stop_gradient(token_statistics(
    reference_logits, CHOSEN, ATTENTION, COMPLETION)[1])
reference_rejected = jax.lax.stop_gradient(token_statistics(
    reference_logits, REJECTED, ATTENTION, COMPLETION)[1])
reference_gap = reference_chosen - reference_rejected
np.testing.assert_allclose(reference_gap[1], 2 * reference_gap[0], rtol=1e-6)
assert float(reference_gap[0]) > 0


def preference_loss(chosen, rejected, ref_chosen, ref_rejected, beta=0.2):
    margin = (chosen - rejected) - (ref_chosen - ref_rejected)
    return -jax.nn.log_sigmoid(beta * margin).mean()


np.testing.assert_allclose(preference_loss(reference_chosen, reference_rejected,
                                           reference_chosen, reference_rejected),
                           np.log(2), rtol=1e-6)
# Equal gaps need not mean equal policies or individual log-probabilities.
same_gap_chosen = reference_chosen - 0.4
same_gap_rejected = reference_rejected - 0.4
assert not np.array_equal(reference_chosen, same_gap_chosen)
assert not np.array_equal(reference_rejected, same_gap_rejected)
np.testing.assert_allclose(preference_loss(reference_chosen, reference_rejected,
                                           same_gap_chosen, same_gap_rejected),
                           np.log(2), rtol=1e-6)
policy_logits = uniform.at[:, :, 3].set(1.5)
policy_chosen = token_statistics(policy_logits, CHOSEN, ATTENTION, COMPLETION)[1]
policy_rejected = token_statistics(policy_logits, REJECTED, ATTENTION, COMPLETION)[1]
better_loss = preference_loss(policy_chosen, policy_rejected,
                               reference_chosen, reference_rejected)
assert float(better_loss) < np.log(2)
assert float(preference_loss(policy_rejected, policy_chosen,
                             reference_rejected, reference_chosen)) > np.log(2)


def policy_objective(logits):
    chosen = token_statistics(logits, CHOSEN, ATTENTION, COMPLETION)[1]
    rejected = token_statistics(logits, REJECTED, ATTENTION, COMPLETION)[1]
    return preference_loss(chosen, rejected, reference_chosen, reference_rejected)


assert np.isfinite(np.asarray(jax.grad(policy_objective)(policy_logits))).all()
parameters = {
    'base': jnp.array([[0.4, -0.2], [0.1, 0.3]], dtype=jnp.float32),
    'a': jnp.array([[0.2], [-0.5]], dtype=jnp.float32),
    'b': jnp.zeros((1, 2), dtype=jnp.float32),
}
features = jnp.array([[1.0, 2.0], [-1.0, 0.5]], dtype=jnp.float32)


def adapter_objective(parameters):
    prediction = features @ (parameters['base'] + parameters['a'] @ parameters['b'])
    return jnp.square(prediction - 1.0).mean()


gradients = jax.grad(adapter_objective)(parameters)
assert all(np.isfinite(np.asarray(leaf)).all() for leaf in jax.tree.leaves(gradients))
np.testing.assert_array_equal(gradients['a'], 0.0)
assert float(jnp.linalg.norm(gradients['b'])) > 0
assert float(jnp.linalg.norm(gradients['base'])) > 0
labels = {'base': 'frozen', 'a': 'adapter', 'b': 'adapter'}
optimizer = optax.multi_transform(
    {'frozen': optax.set_to_zero(), 'adapter': optax.sgd(0.1)}, labels)
updates, _ = optimizer.update(gradients, optimizer.init(parameters), parameters)
updated = optax.apply_updates(parameters, updates)
np.testing.assert_array_equal(updated['base'], parameters['base'])
np.testing.assert_array_equal(updated['a'], parameters['a'])
assert not np.array_equal(updated['b'], parameters['b'])
print('LLM math: causal shift, completion counts, SFT/DPO, immutable reference and selected LoRA updates pass')
```

## Real recipe prerequisites and verification limits

Use these as starting points after the small contract checks. Record the
recipe's actual commit/packages and inspect available devices/memory before
allocating a model. Artifact and dataset access/licenses are specific to the
chosen source; library licensing does not establish those permissions.

| Recipe | Concrete prerequisites | Local evidence and next verification |
|---|---|---|
| [Tunix GPU PEFT](https://tunix.readthedocs.io/en/latest/_collections/examples/qlora_llama3_gpu.html) | Llama 3.1-8B checkpoint/tokenizer and JAX CUDA + Tunix/Qwix environment; source guidance is 16 GB+ GPU VRAM for 4-bit QLoRA, 24 GB+ recommended for LoRA | Source inspected, not executed. These are recipe recommendations, not measured local minima. Its CUDA/package setup differs from this CPU profile; validate loader/logits, target projections, masks, updates and peak memory on the chosen GPU. |
| [Tunix DPO example](https://tunix.readthedocs.io/en/latest/_collections/examples/dpo_gemma.html) | Gemma 3-1B instruction checkpoint, matching Gemma 3 tokenizer, prompt/chosen/rejected data and Tunix/Qwix; source reports testing on v6e-1 TPU with 32 GB HBM | Source inspected, not executed locally. Adapting that recipe to an SFT-derived reference needs the immutable SFT identity above; test a tiny pair batch and recovery before a substantial run. |
| [MaxText conversion](https://maxtext.readthedocs.io/en/maxtext-v0.2.4/guides/checkpointing_solutions/convert_checkpoint.html) | Source MaxText installation, an explicitly supported model mapping (for example qwen3-4b), real checkpoint/tokenizer, CPU RAM/disk sized for conversion | Conversion can run on CPU per its guide; no checkpoint was converted here. Compare actual converted logits with the source and preserve tokenizer/scan/dtype settings. |
| [MaxText inference](https://maxtext.readthedocs.io/en/latest/tutorials/inference.html) | The linked tutorial assumes v6e-8 TPU VM and `maxtext[tpu-post-train]` adapter setup, plus supported model/checkpoint | Source inspected, no TPU test here. Select a JAX execution backend and verify token/cache/position correctness before profiling; use optimize-jax for execution and evaluate-deep-learning for output comparisons. |

The CPU block proves its synthetic math/update contracts only. It does not
verify real tokenizer rendering, causal attention/packing, checkpoint
conversion, Tunix trainer interfaces, quantized kernels, accelerator memory,
rollout rewards or end-to-end preference quality. Those are explicit small
preflight checks for the selected real recipe, followed by the stated
held-out evaluation and recovery guarantees.
