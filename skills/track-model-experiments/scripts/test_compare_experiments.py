import json
import subprocess
import sys
from pathlib import Path

import arviz as az
import jax
import numpy as np
import numpyro
import numpyro.distributions as dist
import pytest
from numpyro.infer import MCMC, NUTS

SCRIPT = Path(__file__).parent / 'compare_experiments.py'


def _fit(model, x, y, seed, with_ll=True):
    mcmc = MCMC(NUTS(model), num_warmup=200, num_samples=200, num_chains=2,
                chain_method='sequential', progress_bar=False)
    mcmc.run(jax.random.PRNGKey(seed), x, y)
    idata = az.from_numpyro(mcmc, log_likelihood=with_ll,
                            coords={'obs': np.arange(len(y))},
                            dims={'y_obs': ['obs']})
    return idata.map_over_datasets(lambda ds: ds.as_numpy())


def _full(x, y=None):
    a = numpyro.sample('a', dist.Normal(0, 5))
    b = numpyro.sample('b', dist.Normal(0, 5))
    sigma = numpyro.sample('sigma', dist.HalfNormal(2))
    with numpyro.plate('obs', x.shape[0]):
        numpyro.sample('y_obs', dist.Normal(a + b * x, sigma), obs=y)


def _intercept(x, y=None):
    a = numpyro.sample('a', dist.Normal(0, 5))
    sigma = numpyro.sample('sigma', dist.HalfNormal(2))
    with numpyro.plate('obs', x.shape[0]):
        numpyro.sample('y_obs', dist.Normal(a, sigma), obs=y)


def _make_variant(folder: Path, model, x, y, seed, with_ll=True):
    folder.mkdir(parents=True, exist_ok=True)
    idata = _fit(model, x, y, seed, with_ll=with_ll)
    idata.to_netcdf(str(folder / 'inference_data.nc'))


@pytest.fixture(scope='module')
def data():
    rng = np.random.default_rng(0)
    x = rng.normal(size=200)
    y = 2.0 + 1.5 * x + rng.normal(size=200)   # real slope => full model wins
    return x, y


@pytest.fixture(scope='module')
def analysis_dir(tmp_path_factory, data):
    x, y = data
    d = tmp_path_factory.mktemp('churn')
    _make_variant(d / 'm-full', _full, x, y, seed=1)
    _make_variant(d / 'm-intercept', _intercept, x, y, seed=2)
    return d


def _run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True)


def test_ranks_better_model_on_top(analysis_dir, tmp_path):
    out = tmp_path / 'comparison.json'
    r = _run('--analysis-dir', str(analysis_dir), '--output', str(out))
    assert r.returncode == 0, r.stderr
    ranking = json.loads(out.read_text())['ranking']
    assert ranking[0]['id'] == 'm-full'
    assert ranking[0]['elpd'] >= ranking[1]['elpd']


def test_missing_log_likelihood_errors(data, tmp_path):
    x, y = data
    d = tmp_path / 'a'
    _make_variant(d / 'm-full', _full, x, y, seed=1)
    _make_variant(d / 'm-noll', _full, x, y, seed=3, with_ll=False)
    r = _run('--analysis-dir', str(d))
    assert r.returncode != 0
    assert 'log_likelihood' in (r.stderr + r.stdout)


def test_mismatched_observations_refuses(data, tmp_path):
    x, y = data
    d = tmp_path / 'b'
    _make_variant(d / 'm-full', _full, x, y, seed=1)
    _make_variant(d / 'm-short', _full, x[:150], y[:150], seed=4)
    r = _run('--analysis-dir', str(d))
    assert r.returncode != 0
    assert 'observation' in (r.stderr + r.stdout).lower()


def test_fewer_than_two_variants_message(data, tmp_path):
    x, y = data
    d = tmp_path / 'c'
    _make_variant(d / 'm-full', _full, x, y, seed=1)
    r = _run('--analysis-dir', str(d))
    assert r.returncode != 0
    assert 'at least two' in (r.stderr + r.stdout).lower()


def test_diagnostics_in_output(analysis_dir, tmp_path):
    out = tmp_path / 'comparison.json'
    r = _run('--analysis-dir', str(analysis_dir), '--output', str(out))
    assert r.returncode == 0, r.stderr
    top = json.loads(out.read_text())['ranking'][0]
    for key in ('max_rhat', 'min_ess', 'divergences'):
        assert key in top
    assert top['max_rhat'] < 1.1   # fixture converges


LEDGER = '''# Experiments — churn

| id (slug) | parent | what changed | hypothesis | ELPD | ΔELPD | max R̂ | div | PPC | psense | status |
|---|---|---|---|---|---|---|---|---|---|---|
| m-full | — | full | slope matters | | | | | | | candidate |
| m-intercept | m-full | drop slope | slope noise | | | | | | | candidate |

<!-- COMPARISON:BEGIN -->
old stale content
<!-- COMPARISON:END -->

## Decision log
- prior human prose that must survive
'''


def test_ledger_update_is_idempotent(analysis_dir, tmp_path):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(LEDGER)
    args = ('--analysis-dir', str(analysis_dir), '--ledger', str(ledger))
    assert _run(*args).returncode == 0
    first = ledger.read_text()
    assert _run(*args).returncode == 0
    second = ledger.read_text()
    assert first == second                       # idempotent
    assert 'prior human prose that must survive' in second
    assert 'old stale content' not in second
    assert '<!-- COMPARISON:BEGIN -->' in second
    # best marker lands on the winning row, only once
    assert second.count('**best**') == 1
    best_row = [ln for ln in second.splitlines() if ln.startswith('| m-full ')][0]
    assert '**best**' in best_row


def test_diagnostics_read_interpreted_check_report(data, tmp_path):
    # A prior version stamped psense='flagged' on mere psense.json presence and read
    # a nonexistent 'ppc' key (so the interpreted rating was never honored). Assert the
    # real check_report.json schema (calibration.rating / psense.flagged_params) is read.
    x, y = data
    d = tmp_path / 'interp'
    _make_variant(d / 'm-full', _full, x, y, seed=1)
    _make_variant(d / 'm-intercept', _intercept, x, y, seed=2)
    # m-full: a CLEAN sensitivity check (no flagged params) + a 'fair' calibration.
    (d / 'm-full' / 'check_report.json').write_text(json.dumps({
        'posterior_predictive': {'available': True},
        'calibration': {'rating': 'fair', 'diagnosis': ''},
        'psense': {'rating': 'low sensitivity', 'flagged_params': []},
    }))
    # m-intercept: a genuinely flagged sensitivity check.
    (d / 'm-intercept' / 'check_report.json').write_text(json.dumps({
        'psense': {'rating': 'strong sensitivity', 'flagged_params': ['sigma']},
    }))
    out = tmp_path / 'comparison.json'
    r = _run('--analysis-dir', str(d), '--output', str(out))
    assert r.returncode == 0, r.stderr
    rank = {e['id']: e for e in json.loads(out.read_text())['ranking']}
    assert rank['m-full']['psense'] == 'ok'            # clean check => 'ok', NOT 'flagged'
    assert rank['m-full']['ppc'] == 'fair'             # interpreted calibration rating
    assert rank['m-intercept']['psense'] == 'flagged'  # flagged_params non-empty
