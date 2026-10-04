# Scientific learning and continuous time

Load for irregular trajectories, neural ODE/CDEs, physics-informed objectives,
neural operators, or solver-dependent gradients. The native path here is
Equinox + Diffrax + Optax; it is an exception serving solver-coupled models,
not a framework switch for unrelated training.

## Choose the scientific contract

| Family | Useful hypothesis | Inputs and failure modes |
|---|---|---|
| Neural ODE | A learned vector field evolves a state between observations | An observed state must support the assumed dynamics; missing channels may require latent state/encoder. Record the actual initial time/state. |
| Neural CDE | An evolving hidden state responds to an irregular observed input path | Time and observations define an interpolation/control path. Record missing-value handling and causal interpolation at prediction time. |
| Physics-informed network | Data plus differential/boundary constraints identify a solution | Derivative coordinates/units, boundary/initial conditions, collocation distribution and residual weights define the objective. |
| Neural operator | A learned map transfers between input/output fields across problem instances | Mesh/grid representation, physical domain, boundary conditions, resolution and function-space normalization define the claim. |

[Diffrax's neural ODE](https://docs.kidger.site/diffrax/examples/neural_ode/)
discusses complete observation versus latent dynamics. Its
[neural CDE](https://docs.kidger.site/diffrax/examples/neural_cde/) explains a
control path with time as a channel. [Physics-informed learning](https://arxiv.org/abs/1711.10561)
and the [Fourier neural operator](https://arxiv.org/abs/2010.08895) provide
primary method references. A low physics residual on sampled points does not
by itself verify boundary conditions or extrapolation; a new-resolution
operator claim needs evaluation at that resolution.

## Observation and differentiation contract

Write each trajectory's observed timestamps, channels and mask. If a shared
union grid is used, construct membership per trajectory, then assert shape
`(trajectories, grid_times[, channels])`, hand-checked entries and count.
Reduce only observed eligible units. Changing values at unobserved positions
must leave the objective unchanged. Solver interpolation supplies predictions
at requested times; it does not supply additional measured targets. Training
and held-out observation masks have an explicit disjointness/split rule.

Keep the original initial time separate from requested output times. If an
extrapolation grid starts later, integrate from the original initial condition
or continue from the correct previously evolved state. Assigning the original
state to that later time changes the scientific model. For input interpolation,
record method, endpoint handling, missing-data policy and which observations
are available when a forecast is made.

Record solver, initial step, controller, rtol/atol, maximum steps, SaveAt,
precision, adjoint and failure status. The
[SaveAt API](https://docs.kidger.site/diffrax/api/saveat/)
specifies where predictions are retained. The
[adjoint guide](https://docs.kidger.site/diffrax/api/adjoints/)
recommends RecursiveCheckpointAdjoint for common reverse-mode training;
continuous backsolve computes a different approximate adjoint and is not a
automatic accuracy improvement. Check gradients against an analytic or
finite-difference reference on a simple fixture and repeat fixed-model
predictions/gradients under tighter tolerances. Report measured sensitivity
without assuming monotonic convergence or inferring its cause from one delta.

## Canonical solver/observation check

A learnable Equinox scalar rate field has the analytic dynamics
`y(t)=y0*exp(rate*t)`. Two trajectories have different observation times. The
fixture verifies their actual objective, analytic gradient and fitted behavior.
Float64 is selected for this small tight-tolerance reference, independently of
the general neural dtype policy. A richer MLP field needs additional capacity,
stability and identifiability checks; this one tests the solver-coupled path.

```python cpu-example scientific-solver
import diffrax
import equinox as eqx
import jax
import jax.numpy as jnp
import numpy as np
import optax

jax.config.update('jax_enable_x64', True)
TIMES = jnp.array([0.0, 0.2, 0.5, 0.8, 1.0], dtype=jnp.float64)
OBSERVED_TIMES = jnp.array([[0.0, 0.2, 0.8], [0.0, 0.5, 1.0]])
INITIAL = jnp.array([1.0, 2.0], dtype=jnp.float64)
TRUE_RATE = -0.7
MASK = jnp.any(TIMES[None, :, None] == OBSERVED_TIMES[:, None, :], axis=-1)
np.testing.assert_array_equal(MASK, [[True, True, False, True, False],
                                    [True, False, True, False, True]])
assert MASK.shape == (2, 5)
assert int(MASK.sum()) == 6
TARGETS = INITIAL[:, None] * jnp.exp(TRUE_RATE * TIMES[None, :])
OBSERVATIONS = jnp.where(MASK, TARGETS, 0.0)


class RateField(eqx.Module):
    rate: jax.Array

    def __call__(self, t, y, args):
        return self.rate * y


def predict(field, tolerance):
    def one_trajectory(initial):
        solution = diffrax.diffeqsolve(
            diffrax.ODETerm(field), diffrax.Tsit5(),
            t0=0.0, t1=1.0, dt0=0.05, y0=initial,
            saveat=diffrax.SaveAt(ts=TIMES),
            stepsize_controller=diffrax.PIDController(rtol=tolerance,
                                                       atol=tolerance * 0.1),
            adjoint=diffrax.RecursiveCheckpointAdjoint(), max_steps=256,
            throw=True)
        assert solution.ys.shape == TIMES.shape
        return solution.ys

    return jax.vmap(one_trajectory)(INITIAL)


def objective(field, observations, tolerance):
    squared_error = jnp.square(predict(field, tolerance) - observations)
    return jnp.where(MASK, squared_error, 0.0).sum() / MASK.sum()


def analytic_gradient(rate):
    predicted = INITIAL[:, None] * jnp.exp(rate * TIMES[None, :])
    derivative = 2 * (predicted - TARGETS) * TIMES[None, :] * predicted
    return jnp.where(MASK, derivative, 0.0).sum() / MASK.sum()


field = RateField(jnp.array(-0.4, dtype=jnp.float64))
changed_missing = jnp.where(MASK, OBSERVATIONS, 10000.0)
np.testing.assert_allclose(objective(field, OBSERVATIONS, 1e-6),
                           objective(field, changed_missing, 1e-6))
for tolerance, gradient_tolerance in ((1e-6, 2e-5), (1e-9, 2e-7)):
    loss, gradient = eqx.filter_value_and_grad(objective)(
        field, OBSERVATIONS, tolerance)
    assert np.isfinite(float(loss))
    assert np.isfinite(float(gradient.rate))
    np.testing.assert_allclose(gradient.rate, analytic_gradient(field.rate),
                               rtol=gradient_tolerance, atol=gradient_tolerance)
    analytic = INITIAL[:, None] * jnp.exp(field.rate * TIMES[None, :])
    np.testing.assert_allclose(predict(field, tolerance), analytic,
                               rtol=gradient_tolerance, atol=gradient_tolerance)

optimizer = optax.sgd(0.4)
optimizer_state = optimizer.init(eqx.filter(field, eqx.is_inexact_array))


@eqx.filter_jit
def fit_step(field, optimizer_state):
    loss, gradients = eqx.filter_value_and_grad(objective)(field, OBSERVATIONS, 1e-6)
    updates, optimizer_state = optimizer.update(gradients, optimizer_state, field)
    return eqx.apply_updates(field, updates), optimizer_state, loss, gradients.rate


initial_loss = float(objective(field, OBSERVATIONS, 1e-6))
for _ in range(80):
    field, optimizer_state, loss, gradient = fit_step(field, optimizer_state)
    assert np.isfinite(float(loss)) and np.isfinite(float(gradient))
final_loss = float(objective(field, OBSERVATIONS, 1e-6))
assert final_loss < 0.01 * initial_loss, (initial_loss, final_loss)
np.testing.assert_allclose(field.rate, TRUE_RATE, atol=2e-3, rtol=0)
coarse_prediction = predict(field, 1e-6)
tight_prediction = predict(field, 1e-9)
np.testing.assert_allclose(coarse_prediction, tight_prediction, atol=2e-5, rtol=2e-5)
assert np.isfinite(np.asarray(tight_prediction)).all()
print(f'rate {float(field.rate):.6f}; loss {initial_loss:.6f} -> {final_loss:.6f}')
```

This verifies a correct observed-unit objective and the local exponential fit.
It does not establish the correct latent representation, solver suitability for
stiff dynamics, or a scientific generalization claim. Use evaluate-deep-learning
for held-out times/trajectories, constraints, identifiability and extrapolation
comparisons; use optimize-jax for a reproduced solver execution bottleneck.
