# Bayesian model test scaffolds (NumPyro / PyMC)

You cannot assert an exact posterior. These four falsifiable checks replace "it sampled" as the
definition of a tested model: determinism, parameter recovery (SBC-lite), shapes/dims, and
golden-master parity. Full MCMC stays behind `@pytest.mark.slow` with a `TINY` config.

```python
# tests/model_fixtures.py
import numpy as np
import pytest

# Tiny config so slow tests are tens of seconds, not minutes. Mirrors nfp_model's TINY.
TINY = dict(num_samples=40, num_warmup=40, num_chains=2)

SEED = sum(map(ord, "model-tests"))     # descriptive, reproducible — never a bare 42
```

## 1. Determinism under a fixed seed (NumPyro)

The cheapest, highest-value model test. Same `PRNGKey` + same data → identical draws.

```python
import jax
import numpy as np
import pytest
from my_model import fit_model
from synthetic import make_synthetic_data

def test_fit_is_deterministic():
    data = make_synthetic_data(seed=SEED)
    a = fit_model(data, seed=SEED, **TINY)
    b = fit_model(data, seed=SEED, **TINY)
    for site in a.posterior:
        np.testing.assert_array_equal(
            np.asarray(a.posterior[site]), np.asarray(b.posterior[site]),
            err_msg=f"nondeterministic draws for {site} — look for an unseeded init/transform",
        )
```

PyMC equivalent — pass `random_seed` and assert equality of the posterior arrays:

```python
import pymc as pm
import numpy as np

def test_pymc_fit_is_deterministic(model_factory, data):
    with model_factory(data):
        idata1 = pm.sample(draws=40, tune=40, chains=2, random_seed=SEED, progressbar=False)
    with model_factory(data):
        idata2 = pm.sample(draws=40, tune=40, chains=2, random_seed=SEED, progressbar=False)
    for v in idata1.posterior.data_vars:
        np.testing.assert_array_equal(idata1.posterior[v].values, idata2.posterior[v].values)
```

## 2. Parameter recovery — SBC-lite (`@pytest.mark.slow`)

Simulate from the model with known parameters, fit, assert the truth lands in the posterior. A
sign error, a mislinked prior, or a broadcasting bug fails this; a smoke test does not.

```python
import numpy as np
import numpyro
import numpyro.distributions as dist
import jax

@pytest.mark.slow
def test_recovers_slope_and_intercept():
    rng = np.random.default_rng(SEED)
    true_alpha, true_beta, true_sigma = 1.5, -0.8, 0.3
    x = rng.normal(size=200)
    y = true_alpha + true_beta * x + rng.normal(scale=true_sigma, size=200)

    fit = fit_model({"x": x, "y": y}, seed=SEED, num_warmup=500, num_samples=500, num_chains=2)

    for name, truth in [("alpha", true_alpha), ("beta", true_beta), ("sigma", true_sigma)]:
        draws = np.asarray(fit.posterior[name]).reshape(-1)
        lo, hi = np.quantile(draws, [0.03, 0.97])        # 94% interval
        assert lo <= truth <= hi, f"{name}: truth {truth} outside 94% CI [{lo:.3f}, {hi:.3f}]"
```

Tighten or loosen via "within k posterior SDs of the mean" when an interval is awkward:

```python
        mean, sd = draws.mean(), draws.std()
        assert abs(mean - truth) <= 4 * sd, f"{name}: |mean-truth| = {abs(mean-truth):.3f} > 4 SD"
```

Run this on a single parameter set in CI's slow tier. Full rank-uniformity SBC (many simulated
datasets, asserting the rank histogram is uniform) is a heavier offline validation, not a per-run
test — keep it in a script, not pytest.

## 3. Shapes / dims / coords and finiteness

Cheap, runs in the fast tier with `TINY`. Mirrors the nfp_model smoke pattern: assert layout,
reconstruct deterministics from their sites, assert finiteness.

```python
@pytest.mark.slow      # uses TINY sampling; promote individual shape asserts to fast if you cache a fit
class TestPosteriorLayout:
    @pytest.fixture(scope="class")
    def fit(self):
        return fit_model(make_synthetic_data(seed=SEED), seed=SEED, **TINY)

    def test_shapes(self, fit):
        post = fit.posterior
        C, D, T = 2, 40, 40                       # chains, draws, time
        assert post["tau"].shape == (C, D)
        assert post["mu_g_era"].shape == (C, D, 2)
        assert post["g_total_sa"].shape == (C, D, T)

    def test_all_finite(self, fit):
        for name, arr in fit.posterior.items():
            assert np.all(np.isfinite(np.asarray(arr))), name

    def test_deterministic_matches_its_sites(self, fit):
        """A deterministic must equal the formula it is built from — catches reshape/broadcast bugs."""
        post = fit.posterior
        recomputed = post["phi_0"][:, :, None] + post["sigma_bd"][:, :, None] * post["xi_bd"]
        np.testing.assert_allclose(np.asarray(recomputed), np.asarray(post["bd"]),
                                   rtol=1e-10, atol=1e-12)
```

## 4. Golden-master parity within tolerance (`@pytest.mark.slow`)

Freeze reference summaries from a trusted version; assert a new fit matches within tolerance —
never exact equality. Guards a port (PyMC→NumPyro), a refactor, or a dependency bump.

```python
import json
from pathlib import Path
import numpy as np

GOLDEN = Path(__file__).parent / "golden" / "asof_2025-07-12_summary.json"
# Document provenance in the file: which vintage/store/code version produced it.

@pytest.mark.slow
def test_parity_against_golden():
    golden = json.loads(GOLDEN.read_text())          # {"nowcast_mean": .., "nowcast_sd": .., ...}
    data = load_fixture_inputs("asof_2025-07-12")     # pinned inputs, committed or in golden store
    fit = fit_model(data, seed=SEED, num_warmup=1000, num_samples=1000, num_chains=4)
    summary = nowcast_summary(fit.posterior)

    np.testing.assert_allclose(summary["nowcast_mean"], golden["nowcast_mean"], rtol=2e-2)
    np.testing.assert_allclose(summary["nowcast_sd"],   golden["nowcast_sd"],   rtol=5e-2)
```

Notes on golden masters:
- Store the heavy reference (full idata or many fixtures) outside the repo (e.g. a golden bucket)
  and commit only a small manifest; re-run *one* fixture in pytest as a reproducibility guard,
  and keep the full N-fixture run in `scripts/run_*_parity.py` behind an opt-in env flag.
- A golden computed on one data vintage will diverge from a rebuilt store. Record the vintage in
  the fixture and skip with a clear message when the configured store does not match, rather than
  failing on expected data drift.
- Tolerances are not magic: pick `rtol` large enough to absorb MCMC Monte-Carlo error at your
  chain length, small enough to catch a real regression. Widen for SD/tail quantities.

## Marker placement recap

```python
pytestmark = [pytest.mark.slow]                       # whole module: full sampling
pytestmark = [pytest.mark.slow, pytest.mark.real_store]   # also reads the real vintage store
```

CI default: `pytest -m "not slow and not network and not real_store"` runs determinism and
shape checks (with a cached or TINY fit) in milliseconds. Recovery and parity run in the slow
tier nightly or pre-merge.
