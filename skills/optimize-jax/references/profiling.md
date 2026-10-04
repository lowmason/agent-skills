# Profiling, specialization and numerical trade-offs

Load for misleading timers, tracing errors, unexpected compilation, host/device
movement, Python dispatch, or precision/memory changes. The procedure applies to
non-learning numerical programs as well as neural models. Sources describe the
APIs; the fixture below establishes compatibility only on its recorded CPU pins.

## Measurements and evidence boundaries

A resident latency measurement starts with ready input/parameter arrays and ends
when every returned array is ready. First encounter includes specialization and
execution. Warm the exact signature before steady-state measurements and finish
one repetition before starting the next for serialized latency. A throughput
measurement instead controls queue depth and waits at its declared batch end.
State which was measured. [JAX benchmarking](https://docs.jax.dev/en/latest/benchmarking.html)
explains asynchronous completion, input placement and dtype comparability.

AOT can time `jit(...).trace(...)`, `traced.lower()` and `lowered.compile()`
separately, then execute the compiled callable. These intervals include Python
and compiler bookkeeping; the compile interval can include loading or reuse.
An AOT executable accepts only its specialized signature, and transformations
such as differentiation belong before compilation.
[JAX AOT](https://docs.jax.dev/en/latest/aot.html) documents these stages.

For a cold claim, use a fresh process and report whether the persistent cache is
disabled, empty, or reused. A cache hit, already lowered function or warmed
signature cannot establish cold compilation. Persistent caching is a separate
experiment with recorded cache configuration and miss/hit evidence.
[JAX persistent cache](https://docs.jax.dev/en/latest/501/compilation-cache.html).

A host timestamp immediately after the call measures submission, including any
synchronous tracing/compilation work. The subsequent completion barrier measures
remaining wait. Execution may overlap both intervals; their difference is not
kernel time. To attribute placement/fetch, wait after placement and after the
full computation and record host fetch/consumption separately. Those barriers
change overlap. Measure the normal request from host preprocessing through
host-consumed result independently. CPU movement may share memory; do not read
CPU placement time as PCIe transfer performance.

## Specialization and traced values

Use compile logging (`jax_log_compiles`) and cache diagnostics
(`jax_explain_cache_misses`) in a diagnostic pass, then disable logging for the
comparison timings. Save function-specific messages alongside shape, dtype,
weak-type, PyTree structure, static values, callable identity and placement.
Replay A,A,B,B,A before warming every distinct signature. A Python trace counter
is evidence of tracing, not by itself proof of a backend executable compilation.
[JAX JIT](https://docs.jax.dev/en/latest/jit-compilation.html).

Default dynamic scalar values specialize by abstract type rather than numerical
value. For a non-learning Euler simulation, unnecessarily static `dt` is one
possible cause: reproduce the original static variant on A,A,B,B,A, then the
stable dynamic variant on the same sequence. Save target compilation/miss logs,
not only duration or a set of signatures. Compare both results against the
independent discrete recurrence (for constant linear decay, `(1-rate*dt)**steps`
times the initial value), including zero steps/rate/dt. Keep the integration
method and precision unchanged. Do this only when the actual source/logs confirm
the static cause; callable recreation or mixed scalar types needs a different
before/after reproduction.

Python branching on a traced value can raise a tracer conversion error. Use JAX
control flow for a dynamic predicate with compatible branch/carry shapes.
Value-dependent array allocation remains a shape problem; a conditional does
not allow arbitrary runtime-dependent array sizes. Distinguish numerical dynamic
scalars from limited static shape/algorithm configuration. Normalize incoming
scalar rank/dtype deliberately; changing dtype can change numerical semantics.

PyTree leaves carry arrays; auxiliary structure participates in transformations.
In NNX, use `nnx.jit`/other graph-aware transforms or a deliberate split/merge
functional boundary. Keep the model graph/state structure stable; adding and
removing substate can cause recompilation or violate fixed scan carry. Pass
changing state through the transform rather than mutating a closed-over object.
[Flax NNX transforms](https://flax.readthedocs.io/en/stable/guides/transforms.html).

## Profile a warmed request

Capture a representative completed workload using `jax.profiler.trace` and
`TraceAnnotation`, with the completion barrier inside the trace. Include real
preprocessing, placement and host consumption when the target is request latency;
a warmed kernel-only capture answers a narrower question. Inspect host gaps,
compilation, copies, kernels and collectives before proposing a change.
[JAX profiling](https://docs.jax.dev/en/latest/profiling.html) documents capture
and trace annotations. This CPU gate does not validate accelerator tracing,
CUPTI availability, XProf analysis or the user's bottleneck.

Audit implicit movement caused by host NumPy conversions, scalar reads,
printing/logging and repeated placement. Use transfer guard in a separate
diagnostic scope; distinguish explicit placement from accidental transfer.
[JAX transfer guard](https://docs.jax.dev/en/latest/transfer_guard.html).

| Evidence | Candidate experiment | Correctness/resource check |
|---|---|---|
| New shape/static/type specialization | Stable incoming types/callables or a finite workload-derived bucket set | Original valid outputs, masks/positions/reduction denominators; padding work and compile distribution |
| Host gaps/repeated tiny dispatches | Outer jit, `vmap` for independent work, fixed-carry `lax.scan` for recurrence | Same ordering/state/randomness; compile size and dispatch count |
| Expensive kernel or poor arithmetic intensity | Algorithm/layout/batching change | Output/gradient parity, throughput and latency under actual batch sizes |
| Repeated transfer/host synchronization | Resident state, less frequent host consumption or staged input pipeline | Same externally visible result; natural request time and memory |
| Training residual memory peak | Selective rematerialization | Loss/gradient/update parity, peak memory and recomputation cost |

`vmap` is not a general substitute for a dependent recurrence. Python loops
inside jit can unroll and increase compilation; scan preserves a fixed carry
contract. Bucketing is a trade-off: nearly doubling sequence length can nearly
quadruple a quadratic attention term. Change a measured cause and rerun the
reference, rather than choosing buckets solely from a generic rounding rule.

## Precision and memory

Record parameter/storage dtype, activation/compute dtype, accumulation dtype,
matmul precision and x64 setting separately. A storage cast and a matmul
precision policy are different changes. Compare sensitive reductions, softmax,
losses and gradients at tolerances justified by the workload; use float32
accumulation when that is the validated policy. Preserve x64 for a simulation
that demonstrably needs it; neural tasks do not inherit it automatically.
[JAX default dtypes](https://docs.jax.dev/en/latest/101/default_dtypes.html) and
[matmul precision](https://docs.jax.dev/en/latest/201/precision.html).

Rematerialization changes which forward residuals are stored versus recomputed
during reverse-mode differentiation. Place `jax.checkpoint` at meaningful
subcomputations and measure the actual trade-off; wrapping an entire objective
is not a guaranteed memory saving.
[JAX checkpointing](https://docs.jax.dev/en/latest/gradient-checkpointing.html).

For memory diagnosis, identify live arrays/executables, optimizer/model/cache
state, retained Python references, allocator reservation and activation peaks.
A device-memory snapshot answers live allocations at that point, not every
transient peak or complete process RSS. Compiler memory analysis is an estimate.
[JAX memory profiling](https://docs.jax.dev/en/latest/device_memory_profiling.html).
Donation can permit buffer reuse when its input is dead afterward; validate
ownership and state recovery, and do not reuse donated buffers. No memory
reduction or precision speedup is established by the timing fixture below.

## Runnable timing fixture

`jax-timing` is a float32 pointwise tanh projection with token and pooled outputs,
lengths 7/13/7, width 16->8, ready parameters, 20 serialized warm repetitions and a
host-list-to-host-checksum request. The checksum consumes results; independent
NumPy allclose assertions establish parity separately. Persistent compilation
cache is disabled, but the AOT interval is still labeled compile-or-load because
backend reuse/bookkeeping is not independently separated. No speed assertion.

```python cpu-example jax-timing
import json
import platform
from time import perf_counter

import jax
import jax.numpy as jnp
import jaxlib
import numpy as np

jax.config.update('jax_enable_compilation_cache', False)
WIDTH = 16
OUTPUT_WIDTH = 8
REPEATS = 20
rng = np.random.default_rng(sum(map(ord, 'timing-parameters')))
host_params = {
    'weight': (rng.normal(size=(WIDTH, OUTPUT_WIDTH)) * 0.1).astype(np.float32),
    'bias': np.linspace(-0.1, 0.1, OUTPUT_WIDTH, dtype=np.float32),
}
params = jax.device_put(host_params)
jax.block_until_ready(params)


def make_forward():
    def forward(model_params, inputs):
        token = jnp.tanh(inputs @ model_params['weight'] + model_params['bias'])
        return {'token': token, 'pooled': jnp.mean(token, axis=0)}
    return forward


def reference(inputs):
    token = np.tanh(inputs @ host_params['weight'] + host_params['bias'])
    return {'token': token, 'pooled': np.mean(token, axis=0)}


def completed_call(function, inputs):
    jax.block_until_ready((params, inputs))
    start = perf_counter()
    output = function(params, inputs)
    submitted = perf_counter()
    jax.block_until_ready(output)
    completed = perf_counter()
    return output, {
        'submit_ms': (submitted - start) * 1000,
        'remaining_wait_ms': (completed - submitted) * 1000,
        'completed_call_ms': (completed - start) * 1000,
    }


forward = jax.jit(make_forward())
visits = []
outputs = []
for length in [7, 13, 7]:
    host_input = np.linspace(-1, 1, length * WIDTH, dtype=np.float32).reshape(length, WIDTH)
    inputs = jax.device_put(host_input)
    jax.block_until_ready(inputs)
    output, duration = completed_call(forward, inputs)
    visits.append({'length': length, **duration})
    outputs.append((host_input, output))

# A separate callable/stage path; this is not the first-encounter interval above.
aot = jax.jit(make_forward())
start = perf_counter()
traced = aot.trace(params, inputs)
trace_ms = (perf_counter() - start) * 1000
start = perf_counter()
lowered = traced.lower()
lower_ms = (perf_counter() - start) * 1000
start = perf_counter()
compiled = lowered.compile()
compile_or_load_ms = (perf_counter() - start) * 1000
aot_output, first_aot = completed_call(compiled, inputs)
outputs.append((host_input, aot_output))
samples = [completed_call(compiled, inputs)[1]['completed_call_ms'] for _ in range(REPEATS)]

raw_request = host_input.tolist()
start = perf_counter()
request_input = np.asarray(raw_request, dtype=np.float32)
request_output = forward(params, jax.device_put(request_input))
host_output = jax.device_get(request_output)
checksum = float(np.sum(host_output['pooled']))
request_ms = (perf_counter() - start) * 1000

start = perf_counter()
placed = jax.device_put(request_input)
jax.block_until_ready(placed)
after_placement = perf_counter()
placed_output = forward(params, placed)
jax.block_until_ready(placed_output)
after_model = perf_counter()
fetched = jax.device_get(placed_output)
float(np.sum(fetched['pooled']))
after_fetch = perf_counter()

max_error = 0.0
for original, output in outputs:
    expected = reference(original)
    actual = jax.device_get(output)
    for name in expected:
        assert actual[name].shape == expected[name].shape
        assert actual[name].dtype == np.float32
        np.testing.assert_allclose(actual[name], expected[name], rtol=2e-5, atol=2e-5)
        max_error = max(max_error, float(np.max(np.abs(actual[name] - expected[name]))))

print(json.dumps({
    'python': platform.python_version(), 'platform': platform.platform(),
    'jax': jax.__version__, 'jaxlib': jaxlib.__version__, 'numpy': np.__version__,
    'backend': jax.default_backend(), 'devices': [str(d) for d in jax.devices()],
    'device_kinds': [d.device_kind for d in jax.devices()],
    'dtype': 'float32', 'x64': bool(jax.config.jax_enable_x64),
    'matmul_precision': str(jax.config.jax_default_matmul_precision),
    'persistent_cache': False, 'width': WIDTH, 'output_width': OUTPUT_WIDTH,
    'visits': visits, 'trace_ms': trace_ms, 'lower_ms': lower_ms,
    'compile_or_load_ms': compile_or_load_ms, 'first_aot': first_aot,
    'warm_repeats': REPEATS, 'warm_median_ms': float(np.median(samples)),
    'warm_p95_ms': float(np.percentile(samples, 95)),
    'host_result_request_ms': request_ms, 'checksum': checksum,
    'fenced_placement_ms': (after_placement - start) * 1000,
    'fenced_model_ms': (after_model - after_placement) * 1000,
    'fenced_fetch_consume_ms': (after_fetch - after_model) * 1000,
    'max_reference_error': max_error,
}, sort_keys=True))
```

Startup/import/device initialization and workload construction are excluded from
these timers. First visit to each signature is recorded before the AOT/warm path;
the third visit reuses length 7. Separate logs/profile of the actual application
are still needed to establish its cause. The tiny CPU median/p95 estimate is
illustrative, and request/stage overlap and accelerator behavior remain outside
this fixture's performance evidence.
