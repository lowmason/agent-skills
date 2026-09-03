# JAX Numerics: Precision and Stability

## Contents
- Why this file is short
- Precision policy: enable x64 before the first JAX op
- The silent-downcast trap at the Polars → JAX boundary
- Guard divisions and normalizations
- Surface nonfinite values early
- Device/platform selection (author locally, run elsewhere)

## Why this file is short

A measured baseline (`specs/completed/red-baseline-jax-numerics-2026-08-26.md`) ran
five fresh agents on a pooled local-level state-space model in NumPyro and checked
which numerics practices they applied unprompted. Three were universal and are
**not** documented here:

| Behaviour | Result | Disposition |
|---|---|---|
| `numpyro.set_host_device_count(n)` before the first JAX op | **5/5** | already known — omitted |
| `scan` for the time recursion (via `numpyro.contrib.control_flow` or `lax`) | **5/5** | already known — omitted |
| Explicit PRNG key threading / `random.split` | **5/5** | already known — omitted |
| **Enabling x64** | **1/5** | documented below |
| **Explicit dtype at the array boundary** | **1/5** | documented below |
| **Guarding a division by a variance** | **0/5** | documented below |
| **Checking for nonfinite values** | **1/5** | documented below |

The omissions matter as much as the inclusions: NumPyro's API forces PRNG discipline, and
agents reach for `scan` and `set_host_device_count` on their own. Documenting those would
spend context on the already-done.

## Precision policy: enable x64 before the first JAX op

JAX defaults to **float32**. For MCMC over a latent process — anything with a recursion,
a covariance update, or a log-determinant — single precision quietly costs you accuracy
long before it produces a visible error.

```python
import numpyro

numpyro.enable_x64()                 # NumPyro-idiomatic
# or, equivalently, before any JAX array exists:
# import jax; jax.config.update('jax_enable_x64', True)
```

**Ordering is load-bearing.** Like `set_host_device_count`, this must run before the first
JAX operation. Called later it silently does nothing to arrays already created.

**Why this is in the file at all.** In the baseline, four of five agents ran float32 while
writing exactly the numerics that punishes it — two implemented Kalman recursions with 60
sequential covariance updates. One validated its filter against a closed-form MVN density
and reported agreement "to ~4e-7 relative, i.e. float32 precision" — it *observed* the
precision and treated it as the tolerance rather than as a decision. Nothing in those
implementations would surface the issue: the tests pass, R-hat is 1.00, and parameter
recovery looks fine.

Decide precision deliberately. float32 is a legitimate choice for a large hierarchical GLM
where speed dominates; it is a poor default for a filtering recursion.

## The silent-downcast trap at the Polars → JAX boundary

A float64 cast on the host is **discarded** if x64 is not enabled:

```python
# Looks like double precision. Is not, unless x64 was enabled first.
x = df.select(cols).to_numpy().astype(np.float64)
x = jnp.asarray(x)          # -> float32, silently
```

This exact pattern appeared in the baseline: an agent deliberately cast to `np.float64` at
the boundary, having never enabled x64, and the intent was erased one line later. The cast
reads as care and delivers nothing.

```python
# Do: set the policy once, then assert it where the data enters.
numpyro.enable_x64()
...
x = jnp.asarray(df.select(cols).to_numpy())
assert x.dtype == jnp.float64, f'expected float64 at the model boundary, got {x.dtype}'
```

An assert at the boundary is cheap and turns a silent precision loss into a loud failure.
This pairs with the Polars-side rules on freezing row order and column selection before
array export.

## Guard divisions and normalizations

**0 of 5 baseline agents guarded any division**, including two dividing by a predicted
variance in a Kalman gain (`gain = predicted_var / obs_var`). In float32 those denominators
can underflow; the result is `inf` or `nan` propagating into the log-density, which NUTS
reports as a divergence or a rejected proposal rather than as the arithmetic fault it is.

```python
# Do: make the floor explicit rather than hoping the variance stays positive.
safe_var = jnp.maximum(obs_var, 1e-12)
gain = predicted_var / safe_var
```

For normalizations where zero is genuinely possible, prefer `jnp.where` so the guard is
visible at the call site:

```python
den = jnp.where(den == 0.0, 1.0, den)
out = num / den
```

Do not reach for a guard where an invariant already rules zero out — but state the
invariant if you are relying on it.

## Surface nonfinite values early

A `nan` inside a traced kernel does not raise; it flows into the log-density and reappears
as a sampler pathology far from its cause. Check at the boundary, where a Python exception
is still possible:

```python
if not np.isfinite(x).all():
    raise ValueError(f'{np.isfinite(x).sum()} of {x.size} model inputs are finite')
```

Inside traced code, use `jax.debug.print` or the `checkify` transform — not a Python `if`,
which sees a tracer rather than a value.

## Device/platform selection (author locally, run elsewhere)

When a model is written on one machine and run on another, make the backend an explicit
runtime choice rather than an ambient one:

```python
def main(argv=None):
    args = parser.parse_args(argv)
    jax.config.update('jax_platform_name', args.device)   # 'cpu' | 'gpu' | 'tpu'
    numpyro.enable_x64()
    return run(args)
```

Keep this inline in `main()`. It is startup configuration, not an architectural boundary —
wrapping two config calls in a resolver class or a config dataclass makes the policy harder
to audit and easier to apply after the first JAX op, which is the one way it can fail.

**Untested caveat:** unlike the four rules above, this one was not exercised by the
baseline — no fixture spanned two machines. It is carried on the source's reasoning and on
the local-authoring / remote-execution split being real for this stack. Treat it as the
least-verified guidance here.
