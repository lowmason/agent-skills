# Generative objectives and sampling

Load for VAEs, invertible flows, diffusion, flow matching, conditioning, or the
distinction between training an objective and assessing generated output.
Training/state/recovery remain in [training.md](training.md); generated quality,
diversity and comparison protocols go to evaluate-deep-learning.

## Select an objective that matches the hypothesis

| Family | Training quantity | Sampling contract |
|---|---|---|
| VAE | Negative ELBO: expected negative reconstruction log likelihood plus KL from encoder distribution to prior | Sample prior latent, then decoder likelihood; distinguish its mean from a stochastic observation |
| Invertible flow | Exact transformed density with the inverse-map Jacobian | Sample base distribution and apply the forward map |
| Diffusion | A specified noise/score/data/velocity target on a noise schedule | A matching reverse stochastic or deterministic sampler with declared steps/variance |
| Flow matching | Regression to the velocity of a chosen conditional probability path | Integrate the learned velocity from base noise to the data endpoint |

For a VAE, sum reconstruction likelihood and KL over their modeled event
dimensions, then average eligible examples. A changed KL weight changes the
objective. Choose a decoder likelihood/range that matches the observations and
use explicit reparameterization randomness. Posterior collapse can leave good
reconstruction while the latent ignores the intended structure. The primary
method is [Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114).

For an invertible flow with `x=f(z)`,
`log p(x)=log p(z)-log|det df/dz|`. Its inverse, Jacobian direction and event
reduction must agree. Test inversion and an analytically calculable affine
case before a deeper transform. A singular Jacobian or an omitted event sum
changes the density. [Normalizing flows](https://arxiv.org/abs/1505.05770)
provides the primary change-of-variables construction.

For diffusion, define
`x_t=sqrt(alpha_bar_t)*x_0 + sqrt(1-alpha_bar_t)*epsilon` and the network's
actual prediction target. Noise prediction uses a weighted or unweighted
squared error against epsilon; that choice is part of the objective.
Time/conditioning broadcast dimensions must match the sample shape. A sampler
using a different parameterization or schedule needs the corresponding
conversion, with endpoint handling and its random streams stated. The
[DDPM paper](https://arxiv.org/abs/2006.11239) is the primary noise-objective
reference. The limiting example below checks the implemented noise objective,
not an entire diffusion model or sampler.

For a simple linear conditional flow-matching path,
`x_t=(1-t)*x_noise+t*x_data` has target velocity `x_data-x_noise`. Regress the
velocity at sampled t using the declared coupling/time weighting; sampling
integrates `dx/dt=v_theta(x,t)` from 0 to 1. A reversed path reverses its
velocity/time interpretation. Other paths/couplings have different targets;
see [Flow Matching](https://arxiv.org/abs/2210.02747). Sampling solver/error and
number of model evaluations are part of an output comparison's budget.

## Canonical independent objective check

At alpha-bar=0 the noisy input equals epsilon, independently of the clean
sample. For noises `[1,-1,2,-2]`, a zero predictor has mean squared error 2.5,
an identity predictor has zero loss, and a scalar predictor's derivative is
`5*(scale-1)`. The second check uses an interior schedule value and the direct
quadratic derivative. These hand values are independent of autodiff.

```python cpu-example generative-objectives
import jax
import jax.numpy as jnp
import numpy as np

CLEAN = jnp.array([[0.2, -0.4], [0.8, 0.1]], dtype=jnp.float32)
NOISE = jnp.array([[1.0, -1.0], [2.0, -2.0]], dtype=jnp.float32)


def noisy_input(clean, noise, alpha_bar):
    return jnp.sqrt(alpha_bar) * clean + jnp.sqrt(1.0 - alpha_bar) * noise


def denoising_loss(scale, clean, noise, alpha_bar):
    noisy = noisy_input(clean, noise, alpha_bar)
    prediction = scale * noisy
    return jnp.square(prediction - noise).mean()


np.testing.assert_array_equal(noisy_input(CLEAN, NOISE, 0.0), NOISE)
np.testing.assert_allclose(denoising_loss(0.0, CLEAN, NOISE, 0.0), 2.5)
np.testing.assert_allclose(denoising_loss(1.0, CLEAN, NOISE, 0.0), 0.0, atol=0)
np.testing.assert_allclose(denoising_loss(0.3, CLEAN, NOISE, 0.0),
                           denoising_loss(0.3, CLEAN * 100, NOISE, 0.0))
for scale in (0.0, 0.3, 1.0):
    loss, gradient = jax.value_and_grad(denoising_loss)(scale, CLEAN, NOISE, 0.0)
    assert np.isfinite(float(loss)) and np.isfinite(float(gradient))
    np.testing.assert_allclose(gradient, 5.0 * (scale - 1.0), atol=1e-6)
scale, alpha_bar = 0.3, 0.6
noisy = noisy_input(CLEAN, NOISE, alpha_bar)
loss, gradient = jax.value_and_grad(denoising_loss)(scale, CLEAN, NOISE, alpha_bar)
hand_gradient = 2 * jnp.mean((scale * noisy - NOISE) * noisy)
assert np.isfinite(float(loss)) and np.isfinite(float(gradient))
np.testing.assert_allclose(gradient, hand_gradient, atol=1e-6, rtol=1e-6)
print('diffusion noise objective: independent limit and finite analytic-gradient checks pass')
```

## Conditioning and failure isolation

State whether the condition is a class, text, measurement, history or another
modality. Record its availability, preprocessing and shape, plus the model's
unconditional/null representation if condition dropout or guidance is used.
Separate condition randomness from noise/time sampling; evaluation records the
same conditioning task and its actual sampler settings.

Verify finite gradients, a fixed tiny-fixture learning path, and the family's
independent objective check. Then inspect actual samples under fixed seeds and
conditioning cases. Better ELBO, denoising MSE or velocity error is evidence
about that objective; it does not alone establish perceptual quality, diversity
or scientific constraints. Route those claims to evaluate-deep-learning with
sample count, conditioning distribution, decoding/sampling budget and baselines.
Typical failures are mismatched event reductions, learned variance without a
valid parameterization, inverted Jacobian sign, target/sampler mismatch,
endpoint singularities and comparing guidance settings under unequal budgets.
