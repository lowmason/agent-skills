import json
import re
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


# --- Cells that hold an escaped pipe (final review) ---

ESCAPED_HYPOTHESIS = 'p(y \\| x) depends on x'


def _unescaped_cells(row):
    return [c.strip() for c in re.split(r'(?<!\\)\|', row.strip().strip('|'))]


def test_an_escaped_pipe_stays_inside_its_cell(analysis_dir, tmp_path):
    text = _ledger_with('m-full', 'm-intercept')
    row = _row(text, 'm-intercept')
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(text.replace(row, row.replace('| h |', f'| {ESCAPED_HYPOTHESIS} |')))
    before = _row(ledger.read_text(), 'm-intercept')
    out = tmp_path / 'comparison.json'
    r = _run('--analysis-dir', str(analysis_dir), '--ledger', str(ledger), '--output', str(out))
    assert r.returncode == 0, r.stderr
    rank = {e['id']: e for e in json.loads(out.read_text())['ranking']}
    after = _row(ledger.read_text(), 'm-intercept')
    left_half = before[:before.index(ESCAPED_HYPOTHESIS) + len(ESCAPED_HYPOTHESIS)]
    assert after.startswith(left_half)                       # the human cells are byte-identical
    cells = _unescaped_cells(after)
    assert len(cells) == 11                                  # one cell per header column
    assert cells[3] == ESCAPED_HYPOTHESIS
    assert cells[4] == f"{rank['m-intercept']['elpd']:.1f}"
    assert cells[5] == f"{rank['m-intercept']['elpd_diff']:.1f}"
    assert cells[-1] == 'candidate'


def test_an_unranked_row_keeps_its_hand_written_cells(analysis_dir, tmp_path):
    # Pins decision D3: a row the comparator cannot rank keeps every cell it holds.
    text = _ledger_with('m-full', 'm-intercept', 'ridge-tuned')
    row = _row(text, 'ridge-tuned')
    written = row.replace('| h | | | | | | | candidate |',
                          '| h | -120.5 | -3.2 | 1.002 | 0 | fair | ok | candidate |')
    assert written != row
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(text.replace(row, written))
    r = _run('--analysis-dir', str(analysis_dir), '--ledger', str(ledger))
    assert r.returncode == 0, r.stderr
    assert _row(ledger.read_text(), 'ridge-tuned') == written


def test_a_row_with_more_cells_than_the_header_is_left_alone(analysis_dir, tmp_path):
    text = _ledger_with('m-full', 'm-intercept')
    row = _row(text, 'm-intercept')
    stray = row.replace('| h |', '| h | x |')                # a stray pipe splits the hypothesis
    assert stray != row
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(text.replace(row, stray))
    r = _run('--analysis-dir', str(analysis_dir), '--ledger', str(ledger))
    assert r.returncode == 0, r.stderr
    assert _row(ledger.read_text(), 'm-intercept') == stray
    notes = [ln for ln in r.stderr.splitlines()
             if ln.startswith('note: ') and 'do not line up' in ln]
    assert len(notes) == 1 and 'm-intercept' in notes[0]


# --- Hardening after plan 59's final review (plan 65 Task 1) ---

def _elpd_entry(variant_id, elpd, **extra):
    '''A ranked ELPD-mode entry with the keys update_ledger and metric_cells read.'''
    return {'id': variant_id, 'elpd': elpd, 'se': 10.0, 'elpd_diff': 0.0, 'dse': 0.0,
            'weight': 0.5, 'warning': False, 'diag_diff': '', 'diag_elpd': '',
            'max_rhat': 1.002, 'min_ess': 400.0, 'divergences': 0, 'ppc': 'fair',
            'psense': 'ok', **extra}


RANKED = [_elpd_entry('m-full', -280.4),
          _elpd_entry('m-intercept', -391.7, elpd_diff=-111.3, max_rhat=None,
                      divergences=None)]


def _stamp(ledger, ranking, not_compared=()):
    block = compare_experiments.render_comparison_block(ranking, list(not_compared))
    compare_experiments.update_ledger(ledger, block, ranking, list(not_compared))
    return ledger.read_text()


def _table_cells(text, variant_id):
    '''A Variants-table row's cells, read through the comparator's own parser.'''
    lines = text.splitlines()
    _, _, rows = compare_experiments._variants_table(lines)
    return next(cells for cells in (compare_experiments._cells(lines[i]) for i in rows)
                if cells[0] == variant_id)


def test_cells_keep_an_empty_first_cell():
    assert compare_experiments._cells('|| b |') == ['', 'b']


def test_cells_keep_an_escaped_pipe_that_ends_the_last_cell():
    assert compare_experiments._cells('| m | x \\||') == ['m', 'x \\|']


def test_winner_row_gets_its_cells_and_the_marker(tmp_path):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(_ledger_with('m-full', 'm-intercept'))
    cells = _table_cells(_stamp(ledger, RANKED), 'm-full')
    assert cells[4:] == ['-280.4', '0.0', '1.002', '0', 'fair', 'ok', '**best**']


def test_missing_diagnostics_render_as_blank_cells(tmp_path):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(_ledger_with('m-full', 'm-intercept'))
    cells = _table_cells(_stamp(ledger, RANKED), 'm-intercept')
    assert cells[4:8] == ['-391.7', '-111.3', '', '']


def test_an_empty_observation_dimension_is_refused():
    import types

    import xarray as xr
    ll = xr.Dataset({'y': (('chain', 'draw', 'obs'), np.zeros((2, 10, 0)))})
    idata = types.SimpleNamespace(log_likelihood=ll)
    with pytest.raises(ValueError, match='no observation dimension'):
        compare_experiments.pointwise_count(idata, 'm-empty')


def test_a_short_row_is_padded_and_filled(tmp_path):
    text = _ledger_with('m-full', 'm-intercept')
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(text.replace(_row(text, 'm-intercept'), '| m-intercept | m-full | drop slope |'))
    cells = _table_cells(_stamp(ledger, RANKED), 'm-intercept')
    assert len(cells) == 11
    assert (cells[2], cells[4], cells[-1]) == ('drop slope', '-391.7', '')   # padded, not invented


def test_a_header_without_status_is_not_the_variants_table():
    assert compare_experiments.ledger_ids('| id | ELPD |\n|---|---|\n| m-full | |\n') is None


def test_a_wide_top_row_note_says_no_row_carries_the_marker(tmp_path, capsys):
    text = _ledger_with('m-full', 'm-intercept')
    row = _row(text, 'm-full')
    wide = row.replace('| h |', '| h | x |')
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(text.replace(row, wide))
    out = _stamp(ledger, RANKED)
    notes = [ln for ln in capsys.readouterr().err.splitlines() if 'do not line up' in ln]
    assert len(notes) == 1 and 'no row carries the best marker' in notes[0]
    assert _row(out, 'm-full') == wide
    assert '**best' not in out


def test_a_wide_row_holding_a_stale_marker_is_named(tmp_path, capsys):
    text = _ledger_with('m-full', 'm-intercept')
    row = _row(text, 'm-intercept')
    stale = row.replace('| h |', '| h | x |').replace('| candidate |', '| **best** |')
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(text.replace(row, stale))
    out = _stamp(ledger, RANKED)
    notes = [ln for ln in capsys.readouterr().err.splitlines() if 'do not line up' in ln]
    assert len(notes) == 1 and 'still holds a best marker' in notes[0]
    assert out.count('**best**') == 2                 # the note is the remedy, not a rewrite


def test_ranked_variants_without_a_row_are_named(tmp_path, capsys):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(_ledger_with('m-intercept'))
    out = _stamp(ledger, RANKED)
    err = capsys.readouterr().err
    assert 'ranked variants with no Variants-table row: m-full.' in err
    assert 'no row carries the best marker' in err
    assert '**best' not in out


def test_a_table_with_no_matching_metric_column_is_noted(tmp_path, capsys):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text('| id | elpd | status |\n|---|---|---|\n'
                      '| m-full | | candidate |\n| m-intercept | | candidate |\n')
    _stamp(ledger, RANKED)
    assert capsys.readouterr().err.count('none of the metric columns') == 1


def test_a_missing_ledger_exits_through_error_before_any_output(tmp_path, capsys):
    out = tmp_path / 'comparison.json'
    code = compare_experiments.main(['--analysis-dir', str(tmp_path), '--ledger',
                                     str(tmp_path / 'typo.md'), '--output', str(out)])
    err = capsys.readouterr().err
    assert code == 1 and err.startswith('error: ') and 'typo.md' in err
    assert not out.exists()


@pytest.mark.parametrize('markers', [
    '<!-- COMPARISON:BEGIN -->\nstale\n',
    '<!-- COMPARISON:END -->\nstale\n<!-- COMPARISON:BEGIN -->\n',
    '<!-- COMPARISON:BEGIN -->\na\n<!-- COMPARISON:END -->\n' * 2,
])
def test_unpaired_or_repeated_markers_are_refused_before_anything_is_written(
        tmp_path, capsys, markers):
    text = _ledger_with('m-full', 'm-intercept') + markers
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(text)
    out = tmp_path / 'comparison.json'
    code = compare_experiments.main(['--analysis-dir', str(tmp_path), '--ledger', str(ledger),
                                     '--output', str(out)])
    err = capsys.readouterr().err
    assert code == 1 and err.startswith('error: ') and 'one pair of markers' in err
    assert ledger.read_text() == text
    assert not out.exists()


# --- Score mode: ranking and refusals (plan 65 Task 2; spec R13, R16, R17, R24) ---

def _scores(folder, units, criterion='cv-mse', orientation='lower'):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'scores.json').write_text(json.dumps(
        {'criterion': criterion, 'orientation': orientation, 'units': units}))
    return folder


# Hand-computed: d = b - a = [0.5, 0.0, 1.0, 0.5], so the paired difference is 0.5.
# Its sample sd (ddof=1) is sqrt(0.5 / 3), so SE = 0.2041; ddof=0 would give 0.1768.
A_UNITS = {'fold-1': 1.0, 'fold-2': 2.0, 'fold-3': 3.0, 'fold-4': 4.0}
B_UNITS = {'fold-1': 1.5, 'fold-2': 2.0, 'fold-3': 4.0, 'fold-4': 4.5}


def test_lower_is_better_ranks_the_smallest_mean_first(tmp_path):
    _scores(tmp_path / 'b', B_UNITS)
    _scores(tmp_path / 'a', A_UNITS)
    ranking, criterion, orientation = compare_experiments.compare_scores(tmp_path, None)
    assert [r['id'] for r in ranking] == ['a', 'b']
    assert (criterion, orientation) == ('cv-mse', 'lower')
    assert [r['score'] for r in ranking] == [pytest.approx(2.5), pytest.approx(3.0)]


def test_higher_is_better_ranks_the_largest_mean_first(tmp_path):
    _scores(tmp_path / 'a', A_UNITS, 'lfo-elpd', 'higher')
    _scores(tmp_path / 'b', B_UNITS, 'lfo-elpd', 'higher')
    ranking, _, orientation = compare_experiments.compare_scores(tmp_path, None)
    assert orientation == 'higher'
    assert [r['id'] for r in ranking] == ['b', 'a']
    assert ranking[1]['score_diff'] == pytest.approx(-0.5)


def test_paired_difference_and_its_se_match_the_hand_computation(tmp_path):
    _scores(tmp_path / 'a', A_UNITS)
    _scores(tmp_path / 'b', B_UNITS)
    top, other = compare_experiments.compare_scores(tmp_path, None)[0]
    assert (top['score_diff'], top['se_diff']) == (0.0, 0.0)
    assert other['score_diff'] == pytest.approx(0.5)
    assert other['se_diff'] == pytest.approx(np.sqrt(0.5 / 3) / 2)
    assert other['se_diff'] != pytest.approx(np.sqrt(0.125) / 2)    # not ddof=0
    assert other['n_units'] == 4


def _score_refusal(tmp_path, capsys, *extra):
    code = compare_experiments.main(['--analysis-dir', str(tmp_path), '--mode', 'score', *extra])
    err = capsys.readouterr().err
    assert code == 1 and err.startswith('error: ') and 'Traceback' not in err
    return err


def test_a_folder_without_scores_json_is_refused(tmp_path, capsys):
    _scores(tmp_path / 'a', A_UNITS)
    (tmp_path / 'b').mkdir()
    err = _score_refusal(tmp_path, capsys, '--folders', str(tmp_path / 'a'), str(tmp_path / 'b'))
    assert 'no scores.json in b' in err


def test_a_criterion_that_differs_across_variants_is_refused(tmp_path, capsys):
    _scores(tmp_path / 'a', A_UNITS)
    _scores(tmp_path / 'b', B_UNITS, criterion='cv-mae')
    err = _score_refusal(tmp_path, capsys)
    assert "'b': 'cv-mae'" in err and 'one criterion' in err


def test_an_orientation_that_differs_across_variants_is_refused(tmp_path, capsys):
    _scores(tmp_path / 'a', A_UNITS)
    _scores(tmp_path / 'b', B_UNITS, orientation='higher')
    err = _score_refusal(tmp_path, capsys)
    assert 'orientation differs' in err and "'b': 'higher'" in err


def test_unit_keys_that_differ_across_variants_are_refused(tmp_path, capsys):
    _scores(tmp_path / 'a', A_UNITS)
    _scores(tmp_path / 'b', {**{k: v for k, v in B_UNITS.items() if k != 'fold-4'},
                              'fold-5': 4.5})
    err = _score_refusal(tmp_path, capsys)
    assert "variant 'b'" in err and 'fold-5' in err and 'fold-4' in err


@pytest.mark.parametrize('value', [float('nan'), float('inf')])
def test_a_non_finite_score_is_refused(tmp_path, capsys, value):
    _scores(tmp_path / 'a', A_UNITS)
    _scores(tmp_path / 'b', {**B_UNITS, 'fold-2': value})
    err = _score_refusal(tmp_path, capsys)
    assert "variant 'b'" in err and 'non-finite' in err and 'fold-2' in err


def test_fewer_than_two_units_is_refused(tmp_path, capsys):
    _scores(tmp_path / 'a', {'fold-1': 1.0})
    _scores(tmp_path / 'b', {'fold-1': 1.5})
    err = _score_refusal(tmp_path, capsys)
    assert "variant 'a'" in err and 'at least 2' in err


def test_fewer_than_two_score_variants_is_refused(tmp_path, capsys):
    _scores(tmp_path / 'a', A_UNITS)
    err = _score_refusal(tmp_path, capsys)
    assert 'at least two variants' in err


# --- Score mode: the ledger (plan 65 Task 2; spec R15, R16, R24) ---

SCORE_LEDGER = '''# Experiments — county nowcast

Criterion: cv-mse

| id (slug) | parent | what changed | hypothesis | score | Δscore | SE(Δ) | status |
|---|---|---|---|---|---|---|---|
| a | — | ridge on lagged features | sets a floor | | | | candidate |
| b | a | add county effects | pooling helps | | | | candidate |

<!-- COMPARISON:BEGIN -->
<!-- COMPARISON:END -->

## Decision log
- Criterion: elpd-loo here is prose and never sets the mode.
'''
ROW_C = '| c | a | gradient boosting | nonlinearity matters | | | | candidate |\n'


def _score_ledger(tmp_path, text=SCORE_LEDGER):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(text)
    return ledger


def _with_row_c(text=SCORE_LEDGER):
    row_b = '| b | a | add county effects | pooling helps | | | | candidate |\n'
    return text.replace(row_b, row_b + ROW_C)


def test_ledger_criterion_reads_the_line_above_the_variants_table():
    assert compare_experiments.ledger_criterion(SCORE_LEDGER) == 'cv-mse'
    assert compare_experiments.ledger_criterion(LEDGER) == 'elpd-loo'
    undeclared = SCORE_LEDGER.replace('Criterion: cv-mse\n', '')
    assert compare_experiments.ledger_criterion(undeclared) == 'elpd-loo'


def test_score_mode_against_an_elpd_ledger_is_refused(tmp_path, capsys):
    ledger = _score_ledger(tmp_path, LEDGER)
    err = _score_refusal(tmp_path, capsys, '--ledger', str(ledger))
    assert 'Criterion: elpd-loo' in err and '--mode elpd' in err
    assert ledger.read_text() == LEDGER


def test_elpd_mode_against_a_score_ledger_is_refused(tmp_path, capsys):
    ledger = _score_ledger(tmp_path)
    code = compare_experiments.main(['--analysis-dir', str(tmp_path), '--ledger', str(ledger)])
    err = capsys.readouterr().err
    assert code == 1 and err.startswith('error: ')
    assert 'Criterion: cv-mse' in err and '--mode score' in err


def test_a_variant_criterion_that_differs_from_the_ledger_is_refused(tmp_path, capsys):
    runs = tmp_path / 'runs'
    _scores(runs / 'a', A_UNITS)
    _scores(runs / 'b', B_UNITS)
    ledger = _score_ledger(tmp_path, SCORE_LEDGER.replace('Criterion: cv-mse', 'Criterion: cv-mae'))
    err = _score_refusal(runs, capsys, '--ledger', str(ledger))
    assert "Criterion: line" in err and "'cv-mae'" in err and "'a': 'cv-mse'" in err


def test_score_cells_qualified_marker_and_comparison_json(tmp_path, capsys):
    runs = tmp_path / 'runs'
    _scores(runs / 'a', A_UNITS)
    _scores(runs / 'b', B_UNITS)
    ledger = _score_ledger(tmp_path, _with_row_c())
    out = tmp_path / 'comparison.json'
    code = compare_experiments.main(['--analysis-dir', str(runs), '--mode', 'score',
                                     '--ledger', str(ledger), '--output', str(out)])
    assert code == 0, capsys.readouterr().err
    assert 'ledger rows not compared: c.' in capsys.readouterr().err
    payload = json.loads(out.read_text())
    assert (payload['mode'], payload['criterion'], payload['not_compared']) == (
        'score', 'cv-mse', ['c'])
    text = ledger.read_text()
    assert _table_cells(text, 'a')[4:] == ['2.5', '0', '0', '**best among score-compared variants**']
    assert _table_cells(text, 'b')[4:] == ['3', '0.5', '0.2041', 'candidate']
    assert _table_cells(text, 'c')[4:] == ['', '', '', 'candidate']
    assert 'Not compared: c. The best marker covers the score-compared variants only.' in text
    assert 'Ranked on cv-mse (lower is better).' in text
    assert '- Criterion: elpd-loo here is prose and never sets the mode.' in text


def test_score_marker_resets_once_every_row_is_compared_and_reruns_are_idempotent(tmp_path):
    runs = tmp_path / 'runs'
    _scores(runs / 'a', A_UNITS)
    _scores(runs / 'b', B_UNITS)
    ledger = _score_ledger(tmp_path, _with_row_c())
    args = ['--analysis-dir', str(runs), '--mode', 'score', '--ledger', str(ledger)]
    assert compare_experiments.main(args) == 0
    ledger.write_text(ledger.read_text().replace(ROW_C, ''))
    assert compare_experiments.main(args) == 0
    first = ledger.read_text()
    assert compare_experiments.main(args) == 0
    assert ledger.read_text() == first
    assert _table_cells(first, 'a')[-1] == '**best**'
    assert 'score-compared' not in first


def test_elpd_comparison_json_carries_mode_and_criterion(analysis_dir, tmp_path):
    out = tmp_path / 'comparison.json'
    r = _run('--analysis-dir', str(analysis_dir), '--output', str(out))
    assert r.returncode == 0, r.stderr
    payload = json.loads(out.read_text())
    assert (payload['mode'], payload['criterion']) == ('elpd', 'elpd-loo')
