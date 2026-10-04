# Graphs and geometric symmetry

Load for graph/message-passing models, point clouds, or scalar/vector outputs
that must respect permutations, rotations or inversion. Use the documented
e3nn-jax Equinox or Linen path when representation-aware layers serve the task.
Existing direct-JAX constructions can be valid: establish their algebra and
check the same transformation contract.

## Choose the required structure

Graph message passing encodes relations and permutation behavior; unconstrained
node features do not automatically supply 3D rotation equivariance. A
symmetry-constrained model chooses representations and permitted operations.
Define the group and output action first: SO(3) covers proper rotations, O(3)
also covers inversion/reflections, and translation is a separate claim.

An even scalar is `0e`; a pseudoscalar is `0o`. A polar vector such as relative
position is `1o`; an axial vector is `1e`. Under inversion a polar vector
changes sign, while an axial vector does not. Higher angular degrees transform
through their corresponding irreducible representations. The
[e3nn irreps documentation](https://e3nn-jax.readthedocs.io/en/latest/api/irreps.html)
and [IrrepsArray API](https://e3nn-jax.readthedocs.io/en/latest/api/irreps_array.html)
define these types and transformations.

Use invariant scalar gates or compatible tensor products/nonlinearities for
non-scalar channels. Applying an arbitrary componentwise activation to a vector
generally breaks its representation. Choose the output irrep and parity based
on the measured quantity, not merely its array length. The documented
[Equinox Linear](https://e3nn-jax.readthedocs.io/en/latest/api/equinox.html)
requires its key/input/output irreps at initialization; the
[Linen integration](https://e3nn-jax.readthedocs.io/en/latest/api/flax.html)
is a separate supported path.

## Neighbors and aggregation contract

State directed/undirected edges, sender/receiver convention, periodic images,
cutoff and tie handling, self edges, padding masks and aggregation unit. A
rotation-invariant distance cutoff is compatible with rotations; an
axis-aligned neighbor rule can change graph topology. Node relabeling must
permute node outputs or preserve a global output as declared. When changing
neighbor order, aggregation should follow the claimed order independence.

Use relative coordinates if translation behavior is required. A sum can
represent an extensive global quantity; a mean changes size scaling. If a
model claims O(3), check inversion as well as proper rotations. If aggregation
claims permutation invariance/equivariance, permute both features and edge
indices consistently and test that action. These checks belong to training
correctness; broader dataset/symmetry generalization claims go to
evaluate-deep-learning.

[Jraph](https://github.com/google-deepmind/jraph) was archived in May 2025.
Its GraphsTuple/padding/aggregation contract remains compatibility context for
existing projects; it is outside this skill's CPU profile and is not a new
default dependency.

## Canonical native symmetry example

The origin is fixed. Radial weights are invariant, an e3nn Equinox Linear maps
`1o` to `1o`, and global summation gives an even scalar and polar vector. The
example claims O(3) plus permutation invariance of global outputs. It makes no
translation claim and no NNX integration claim.

```python cpu-example geometric-equivariance
import e3nn_jax as e3nn
import equinox as eqx
import jax
import jax.numpy as jnp
import numpy as np

SEED = sum(map(ord, 'geometric-contract'))


class PointModel(eqx.Module):
    vector_layer: e3nn.equinox.Linear
    radial_scale: jax.Array
    scalar_bias: jax.Array

    def __init__(self, key):
        self.vector_layer = e3nn.equinox.Linear(
            irreps_in=e3nn.Irreps('1o'), irreps_out=e3nn.Irreps('1o'), key=key)
        self.radial_scale = jnp.array(0.4, dtype=jnp.float32)
        self.scalar_bias = jnp.array(0.1, dtype=jnp.float32)

    def __call__(self, points):
        radius_squared = jnp.square(points).sum(axis=-1)
        weights = jax.nn.sigmoid(self.radial_scale * radius_squared)
        vectors = e3nn.IrrepsArray('1o', points * weights[:, None])
        transformed = self.vector_layer(vectors)
        assert transformed.irreps == e3nn.Irreps('1o')
        scalar = self.scalar_bias + self.radial_scale * radius_squared.sum()
        vector = transformed.array.sum(axis=0)
        return scalar, vector


def rotation(axis, angle):
    cosine, sine = jnp.cos(angle), jnp.sin(angle)
    if axis == 'x':
        return jnp.array([[1.0, 0.0, 0.0], [0.0, cosine, -sine],
                          [0.0, sine, cosine]], dtype=jnp.float32)
    return jnp.array([[cosine, -sine, 0.0], [sine, cosine, 0.0],
                      [0.0, 0.0, 1.0]], dtype=jnp.float32)


points = jnp.array([[1.0, 0.2, -0.3], [-0.4, 0.8, 0.1],
                    [0.3, -0.2, 0.5], [0.5, 0.9, -0.4]], dtype=jnp.float32)
model = PointModel(jax.random.key(SEED))
scalar, vector = model(points)
assert scalar.shape == () and vector.shape == (3,)
assert abs(float(scalar)) > 1e-4 and float(jnp.linalg.norm(vector)) > 1e-4
for matrix in (rotation('x', 0.7), rotation('z', -1.1),
               rotation('x', 0.4) @ rotation('z', 0.9)):
    np.testing.assert_allclose(matrix.T @ matrix, jnp.eye(3), atol=1e-6)
    np.testing.assert_allclose(jnp.linalg.det(matrix), 1.0, atol=1e-6)
    rotated_scalar, rotated_vector = model(points @ matrix.T)
    np.testing.assert_allclose(rotated_scalar, scalar, atol=1e-5, rtol=1e-5)
    np.testing.assert_allclose(rotated_vector, vector @ matrix.T, atol=1e-5, rtol=1e-5)
inverted_scalar, inverted_vector = model(-points)
np.testing.assert_allclose(inverted_scalar, scalar, atol=1e-5, rtol=1e-5)
np.testing.assert_allclose(inverted_vector, -vector, atol=1e-5, rtol=1e-5)
permuted_scalar, permuted_vector = model(points[jnp.array([2, 0, 3, 1])])
np.testing.assert_allclose(permuted_scalar, scalar, atol=1e-5, rtol=1e-5)
np.testing.assert_allclose(permuted_vector, vector, atol=1e-5, rtol=1e-5)


def objective(model):
    scalar, vector = model(points)
    return jnp.square(scalar) + jnp.square(vector).sum()


gradients = eqx.filter_grad(objective)(model)
assert all(np.isfinite(np.asarray(leaf)).all() for leaf in jax.tree.leaves(gradients))
print('native e3nn: nontrivial scalar/vector, rotations, inversion, permutation and gradients pass')
```

This is a reusable minimal native path. A deeper graph needs tests of its
actual neighbor construction, parity channels and aggregation, rather than
reusing these passed point-cloud checks as proof of the full graph model.
