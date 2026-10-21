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

import compare_experiments

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


# The convergence section of a diagnostics.json written by diagnose_model.py (the
# bayesian-workflow writer), copied verbatim from its run on this file's m-full fit
# (2026-10-19; arviz 1.3.0, arviz-stats 1.3.3). compare_experiments reads only it.
DIAGNOSE_MODEL_CONVERGENCE = {
    'all_ok': True,
    'method': 'arviz_stats.diagnose',
    'rhat': {'ok': True, 'max': 1.0050849087659606, 'problematic_params': []},
    'ess_bulk': {'ok': True, 'problematic_params': [], 'min': 280},
    'ess_tail': {'ok': True, 'problematic_params': [], 'min': 235},
    'divergences': {'checked': True, 'count': 0, 'pct': 0.0, 'ok': True},
    'treedepth': {'checked': False},
    'bfmi': {'checked': False},
}


def test_diagnose_model_output_is_read_not_recomputed(tmp_path, monkeypatch):
    (tmp_path / 'diagnostics.json').write_text(
        json.dumps({'convergence': DIAGNOSE_MODEL_CONVERGENCE}))

    def recompute(*args, **kwargs):
        raise AssertionError('recomputed although diagnostics.json carries the values')

    monkeypatch.setattr(compare_experiments.az, 'summary', recompute)
    diag = compare_experiments.extract_diagnostics(None, tmp_path)
    assert diag['max_rhat'] == 1.0050849087659606
    assert diag['min_ess'] == 235.0      # the smaller of ess_bulk.min and ess_tail.min
    assert diag['divergences'] == 0


def test_a_null_or_unchecked_diagnostic_is_recomputed(analysis_dir, tmp_path):
    # rhat.max is null in files written before diagnose_model.py computed it on clean
    # runs; a divergence block marked checked: false carries no count.
    conv = {**DIAGNOSE_MODEL_CONVERGENCE,
            'rhat': {'ok': True, 'max': None, 'problematic_params': []},
            'divergences': {'checked': False}}
    (tmp_path / 'diagnostics.json').write_text(json.dumps({'convergence': conv}))
    idata = compare_experiments.load_idata(analysis_dir / 'm-full')
    diag = compare_experiments.extract_diagnostics(idata, tmp_path)
    assert diag['max_rhat'] is not None and diag['max_rhat'] < 1.1   # from az.summary
    assert diag['divergences'] == 0                                  # from sample_stats
    assert diag['min_ess'] == 235.0                                  # still read


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


def test_compare_raises_valueerror_not_systemexit(tmp_path):
    # compare() is a reusable interface — a library caller must be able to catch
    # its guard failures. The <2-variants guard must raise ValueError, not SystemExit.
    empty = tmp_path / 'empty'
    empty.mkdir()
    with pytest.raises(ValueError, match='at least two'):
        compare_experiments.compare(empty, None)


def test_has_warning_nan_guarded():
    import pandas as pd
    # ArviZ 1.2.0 emits '' (not NaN) for clean diag columns, but guard anyway:
    # str(np.nan) == 'nan' is truthy, which would read a NaN as a spurious warning.
    clean = pd.Series({'diag_diff': float('nan'), 'diag_elpd': float('nan')})
    assert compare_experiments._has_warning(clean) is False
    dirty = pd.Series({'diag_diff': '', 'diag_elpd': 'high pareto k'})
    assert compare_experiments._has_warning(dirty) is True


def test_diag_strings_surfaced_in_output(analysis_dir, tmp_path):
    # comparison.json exposes the raw ArviZ diag strings per variant for
    # transparency (the single `warning` boolean deliberately over-folds them).
    out = tmp_path / 'comparison.json'
    r = _run('--analysis-dir', str(analysis_dir), '--output', str(out))
    assert r.returncode == 0, r.stderr
    top = json.loads(out.read_text())['ranking'][0]
    assert 'diag_diff' in top and 'diag_elpd' in top


def test_update_ledger_appends_when_no_markers(analysis_dir, tmp_path):
    # A ledger with no <!-- COMPARISON --> markers takes update_ledger's append
    # branch; assert the block is appended and a second run is idempotent.
    ledger = tmp_path / 'experiments.md'
    ledger.write_text('# Experiments\n\n| id | status |\n|---|---|\n'
                      '| m-full | candidate |\n')
    args = ('--analysis-dir', str(analysis_dir), '--ledger', str(ledger))
    assert _run(*args).returncode == 0
    first = ledger.read_text()
    assert '<!-- COMPARISON:BEGIN -->' in first        # appended
    assert _run(*args).returncode == 0
    assert ledger.read_text() == first                 # idempotent on rerun


# --- Rows the comparator cannot rank (audit-3-10-26 G1) ---

def _ledger_with(*rows):
    head = ('# Experiments — churn\n\n'
            '| id (slug) | parent | what changed | hypothesis | ELPD | ΔELPD | max R̂ | div | PPC | psense | status |\n'
            '|---|---|---|---|---|---|---|---|---|---|---|\n')
    body = ''.join(f'| {r} | — | {r} | h | | | | | | | candidate |\n' for r in rows)
    return head + body + '\n## Decision log\n- prose\n'


def _row(text, variant_id):
    return next(ln for ln in text.splitlines() if ln.startswith(f'| {variant_id} '))


def test_folder_without_inference_data_exits_through_error(analysis_dir, tmp_path):
    ridge = tmp_path / 'ridge-tuned'
    ridge.mkdir()
    r = _run('--analysis-dir', str(analysis_dir),
             '--folders', str(analysis_dir / 'm-full'), str(ridge))
    assert r.returncode == 1
    assert r.stderr.startswith('error: ')
    assert 'Traceback' not in r.stderr
    assert 'ridge-tuned' in r.stderr and 'Decision log' in r.stderr


def test_uncompared_ledger_row_is_reported_and_best_is_qualified(analysis_dir, tmp_path):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(_ledger_with('m-full', 'm-intercept', 'ridge-tuned'))
    out = tmp_path / 'comparison.json'
    r = _run('--analysis-dir', str(analysis_dir), '--ledger', str(ledger), '--output', str(out))
    assert r.returncode == 0, r.stderr
    assert 'ridge-tuned' in r.stderr                          # reported, not silent
    assert json.loads(out.read_text())['not_compared'] == ['ridge-tuned']
    text = ledger.read_text()
    assert '**best among ELPD-compared variants**' in _row(text, 'm-full')
    assert _row(text, 'ridge-tuned').endswith('| candidate |')
    assert 'Not compared: ridge-tuned' in text
    assert text.count('**best') == 1


def test_qualified_marker_resets_once_every_row_is_compared(analysis_dir, tmp_path):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(_ledger_with('m-full', 'm-intercept', 'ridge-tuned'))
    args = ('--analysis-dir', str(analysis_dir), '--ledger', str(ledger))
    assert _run(*args).returncode == 0
    assert '**best among ELPD-compared variants**' in _row(ledger.read_text(), 'm-full')
    ledger.write_text('\n'.join(ln for ln in ledger.read_text().splitlines()
                                if not ln.startswith('| ridge-tuned ')) + '\n')
    r = _run(*args)
    assert r.returncode == 0, r.stderr
    text = ledger.read_text()
    assert '**best**' in _row(text, 'm-full')
    assert 'ELPD-compared' not in text
    assert 'Not compared' not in text
    assert text.count('**best') == 1


def test_az_compare_type_error_becomes_value_error(analysis_dir, monkeypatch):
    def fail(models):
        raise TypeError('Encountered error trying to compute ELPD from model m-full.')

    monkeypatch.setattr(compare_experiments.az, 'compare', fail)
    with pytest.raises(ValueError, match='az.compare'):
        compare_experiments.compare(analysis_dir, None)


def test_ledger_ids_read_only_the_variants_table():
    text = (_ledger_with('m-full', 'm-intercept')
            + '\n| other | table |\n|---|---|\n| x | y |\n'
            + '<!-- COMPARISON:BEGIN -->\n| id | ELPD |\n|---|---|\n| m-old | 1.0 |\n'
            '<!-- COMPARISON:END -->\n')
    assert compare_experiments.ledger_ids(text) == ['m-full', 'm-intercept']


def test_ledger_without_a_variants_table_is_noted(analysis_dir, tmp_path):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text('# Experiments\n\nprose, no table\n')
    r = _run('--analysis-dir', str(analysis_dir), '--ledger', str(ledger))
    assert r.returncode == 0, r.stderr
    assert 'no Variants table' in r.stderr
    assert '<!-- COMPARISON:BEGIN -->' in ledger.read_text()


# --- The metric cells (G1 part e) ---

def test_metric_cells_are_filled_from_the_ranking(analysis_dir, tmp_path):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(LEDGER)
    out = tmp_path / 'comparison.json'
    r = _run('--analysis-dir', str(analysis_dir), '--ledger', str(ledger), '--output', str(out))
    assert r.returncode == 0, r.stderr
    rank = {e['id']: e for e in json.loads(out.read_text())['ranking']}
    cells = [c.strip() for c in _row(ledger.read_text(), 'm-intercept').strip('|').split('|')]
    elpd, d_elpd, rhat, div, ppc, psense = cells[4:10]
    assert elpd == f"{rank['m-intercept']['elpd']:.1f}"
    assert d_elpd == f"{rank['m-intercept']['elpd_diff']:.1f}"
    assert rhat == f"{rank['m-intercept']['max_rhat']:.3f}"
    assert div == str(rank['m-intercept']['divergences'])
    assert (ppc, psense) == ('unknown', 'unknown')       # no check_report.json in the fixture
    assert cells[2:4] == ['drop slope', 'slope noise']   # the human half is untouched


# --- Log-likelihood shapes from bayesian-workflow's state-space routes (G3) ---

def _summed_factor(x, y=None):
    a = numpyro.sample('a', dist.Normal(0, 5))
    sigma = numpyro.sample('sigma', dist.HalfNormal(2))
    numpyro.factor('ll', dist.Normal(a, sigma).log_prob(y).sum())


def _per_step_factor(x, y=None):
    a = numpyro.sample('a', dist.Normal(0, 5))
    b = numpyro.sample('b', dist.Normal(0, 5))
    sigma = numpyro.sample('sigma', dist.HalfNormal(2))
    numpyro.factor('ll', dist.Normal(a + b * x, sigma).log_prob(y))


def _fit_factor(folder, model, x, y, seed, dims=None):
    mcmc = MCMC(NUTS(model), num_warmup=200, num_samples=200, num_chains=2,
                chain_method='sequential', progress_bar=False)
    mcmc.run(jax.random.PRNGKey(seed), x, y)
    idata = az.from_numpyro(mcmc, log_likelihood=True,
                            coords={'obs': np.arange(len(y))}, dims=dims or {})
    folder.mkdir(parents=True, exist_ok=True)
    idata.to_netcdf(str(folder / 'inference_data.nc'))


def test_summed_factor_is_refused_with_its_remedy(data, tmp_path):
    x, y = data
    _fit_factor(tmp_path / 'f-a', _summed_factor, x, y, seed=5)
    _fit_factor(tmp_path / 'f-b', _summed_factor, x, y, seed=6)
    r = _run('--analysis-dir', str(tmp_path))
    assert r.returncode == 1
    assert r.stderr.startswith('error: ')
    assert 'observation dimension' in r.stderr and 'numpyro.factor' in r.stderr


def test_per_step_factor_terms_are_ranked(data, tmp_path):
    x, y = data
    _fit_factor(tmp_path / 'f-full', _per_step_factor, x, y, seed=7, dims={'ll': ['obs']})
    _make_variant(tmp_path / 'm-intercept', _intercept, x, y, seed=2)
    out = tmp_path / 'comparison.json'
    r = _run('--analysis-dir', str(tmp_path), '--output', str(out))
    assert r.returncode == 0, r.stderr
    ranking = json.loads(out.read_text())['ranking']
    assert ranking[0]['id'] == 'f-full'
    assert ranking[0]['se'] > 0                       # 200 pointwise terms, not one


def _two_source_variant(folder, n_draws=100, seed=0):
    rng = np.random.default_rng(seed)
    obs = np.arange(50)
    idata = az.from_dict({
        'posterior': {'a': rng.normal(size=(2, n_draws))},
        'log_likelihood': {'y_a': rng.normal(-1, 0.1, size=(2, n_draws, 50)),
                           'y_b': rng.normal(-1, 0.1, size=(2, n_draws, 50))},
        'observed_data': {'y_a': rng.normal(size=50), 'y_b': rng.normal(size=50)},
    }, coords={'obs': obs}, dims={'y_a': ['obs'], 'y_b': ['obs']})
    folder.mkdir(parents=True, exist_ok=True)
    idata.to_netcdf(str(folder / 'inference_data.nc'))


def test_several_log_likelihood_variables_are_refused(tmp_path):
    _two_source_variant(tmp_path / 's-1', seed=1)
    _two_source_variant(tmp_path / 's-2', seed=2)
    with pytest.raises(ValueError, match='2 log-likelihood variables') as exc:
        compare_experiments.compare(tmp_path, None)
    assert 'y_a' in str(exc.value) and 'one pointwise variable' in str(exc.value)
