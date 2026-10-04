# Mesh, placement and distributed state

Load for placement errors, unexpected resharding/collectives, model/optimizer
memory partitioning or distributed checkpoint restore. Start with logical
array/state contracts and single-device parity, then test the real topology.
The runnable block verifies one-device placement only.

## Define the placement contract

A mesh names axes over an arrangement of physical devices. A `PartitionSpec`
assigns those named axes to logical array dimensions; `None` leaves that
dimension unpartitioned. `NamedSharding` combines mesh and spec. Define global
shape/dtype and intended replication/partitioning for every relevant input,
parameter, activation, optimizer slot and output. Check dimension divisibility
and how the partition maps to available devices.
[JAX sharding](https://docs.jax.dev/en/latest/201/sharding.html).

Use `jax.device_put` for explicit placement and `jax.jit` input/output sharding
contracts for compiled boundaries. Inspect actual `array.sharding` and
`addressable_shards`; logical shape remains global even when each device holds
a smaller shard. An axis named `data` does not automatically make every array
data-parallel. Keep placements consistent across the operation graph to avoid
unintended resharding. Explicit versus automatic mesh-axis policies and manual
`shard_map` are different contracts; select from the installed JAX version's
supported APIs instead of assuming older `pjit` recipes are interchangeable.

## One-device API check

`jax-placement` uses the existing CPU profile. The mesh contains exactly one
actual CPU device and its data dimension therefore has one partition. It checks
named input/output placement and the logical numerical result. It exercises no
inter-device collective, distributed memory saving, network topology, throughput
scaling or multi-host recovery.

```python cpu-example jax-placement
import json

import jax
from jax.sharding import Mesh, NamedSharding, PartitionSpec
import numpy as np

cpu_device = jax.devices('cpu')[0]
mesh = Mesh(np.asarray([cpu_device], dtype=object), ('data',))
placement = NamedSharding(mesh, PartitionSpec('data', None))
host = np.arange(24, dtype=np.float32).reshape(6, 4) / np.float32(8)
placed = jax.device_put(host, placement)
jax.block_until_ready(placed)
transform = jax.jit(lambda x: x * x + np.float32(1),
                    in_shardings=placement, out_shardings=placement)
output = transform(placed)
jax.block_until_ready(output)
assert output.shape == host.shape
assert output.sharding.is_equivalent_to(placement, ndim=2)
assert len(output.addressable_shards) == 1
np.testing.assert_allclose(jax.device_get(output), host * host + np.float32(1))
print(json.dumps({'scope': 'one-device CPU placement only',
                  'jax': jax.__version__, 'mesh_shape': dict(mesh.shape),
                  'global_shape': list(output.shape), 'sharding': str(output.sharding)}))
```

## Distributed model and update state

Choose placement from the workload and communication/memory profile. Data
parallelism partitions examples and generally replicates parameters; tensor or
model parallelism partitions model dimensions and can require communication
within layers. Sharded optimizer state must match each slot's logical parameter
semantics; scalar step counters and global reductions need explicit contracts.
Record gradient aggregation and valid-token/example normalization so device
count changes do not alter the objective. Compare a small distributed update
against a trusted single-device update with the same global batch and randomness
before interpreting performance.

Model-state frameworks still require their transformations. In NNX, preserve
state/graph semantics through graph-aware transforms or an explicit functional
split/merge boundary. A sharding tree is not permission to discard mutable
statistics, PRNG state, optimizer slots, step/schedule state or cache cursors.
[NNX transforms](https://flax.readthedocs.io/en/stable/guides/transforms.html).

For multi-process runs, initialize `jax.distributed.initialize` before querying
devices or performing computations. Distinguish `jax.devices` (global) from
`jax.local_devices`/addressable shards (local). All participating controllers
must execute compatible distributed operations in the same order. Host branches
around collectives can hang the run. Establish coordinated process identities,
local input ownership and global-array construction from local shards rather
than assuming one host can place every shard. Check that the dataset is
partitioned once, not duplicated on every controller.
[JAX multi-controller guide](https://docs.jax.dev/en/latest/multi_process.html).

## Checkpoints and performance evidence

A distributed restore contract includes global shapes/dtypes, target mesh and
shardings, model/optimizer/mutable state, counters, randomness and data progress
required for the claimed resume. Orbax restore target information describes the
new destination rather than blindly trusting serialized device identifiers.
Wait for asynchronous checkpoint completion before shutdown or consuming the
artifact; checkpoint bytes alone do not establish an equivalent resumed update.
[Orbax checkpoint guide](https://orbax.readthedocs.io/en/latest/guides/checkpoint/orbax_checkpoint_101.html).
Use **deep-learning** for the complete training/recovery workflow.

Compare the same global workload and numerical policy on the stated topology.
Report batch/sequence shapes, process and accelerator counts, interconnect,
compile/warm policy, collective/resharding profile, memory and synchronization
boundary. A larger local batch or changed precision is a changed experiment,
not a pure sharding speed comparison. Load the optional MaxText route in
[inference](inference.md) only when scale justifies its actual model/hardware
prerequisites.

No multi-host/accelerator recipe is executed by this portable CPU gate: it has
one CPU device and no coordinated controllers, interconnect or pretrained
checkpoint. The missing test would establish distributed collective correctness,
real memory/performance, restore/resharding behavior and hardware compatibility.
Document those as pending before claiming a scale result.
