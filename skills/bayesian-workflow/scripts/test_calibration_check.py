"""Tests for calibration_check.py — run from this directory (bare imports).

cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz \
  --with arviz-stats --with numpy --with xarray python -m pytest -q

The figure-rendering test skips unless matplotlib is installed (add --with matplotlib).
The pre-registered acceptance sweep runs only with CALIBRATION_SWEEP=1 set (seeds 0-99
on both PIT paths, a minute or two); add -s to see the counts it records.

The rule tests feed assess_pit exact-quantile PIT arrays: the PIT of N(0, 1)'s exact
quantiles under a N(loc, scale) predictive, so they involve no sampling. Most other
fixtures are a normal model of y ~ N(0, 1) whose predictive distribution is
deliberately right, too narrow, too wide, or shifted. Both PIT paths are
exercised: PPC-PIT reads posterior_predictive directly; LOO-PIT reweights it
through a log_likelihood group consistent with the same predictive. In those
fixtures mu is not fit to y, so LOO-PIT is nearly PPC-PIT: the loo_pit cases
exercise the branch and the coverage fold, not the PSIS reweighting. One
per-observation model separates the two paths: PPC-PIT double-dips on it, and
LOO-PIT does not.
"""

import functools
import json
import operator
import os
import sys
from collections import Counter

import arviz_stats as azs
import numpy as np
import pytest
from arviz_base import from_dict
from scipy import stats

import calibration_check
import check_diagnostics
from calibration_check import assess_calibration

N_OBS, N_CHAIN, N_DRAW = 200, 2, 500
TRUE_SCALE = 1.0
OVER_CONFIDENT_SCALE = 0.3  # predictive far narrower than the data
UNDER_CONFIDENT_SCALE = 3.0  # predictive far wider than the data
# Right spread, biased centre: the PIT test fails. The coverage fold is only second-order
# sensitive to a shift, so its test holds at SEED (and on most seeds, not all).
LOCATION_SHIFT = 0.4
COMPOUND_NARROW_SCALE = 0.7  # paired with LOCATION_SHIFT: a shift and a spread error at once
COMPOUND_WIDE_SCALE = 1.5
POSTERIOR_SD_OF_MEAN = 0.05
PER_OBSERVATION_PRIOR_SD = 0.7
DISCRETE_RATE = 3.0
# A calibrated model is still flagged at ci_prob=0.99 on a few percent of seeds: each of
# the two pot_c tests has its own false-alarm rate. The data and the PIT randomization
# are both seeded, and pot_c is deterministic given the PIT values, so the outcome for
# this seed is deterministic.
SEED = 0

# The five finding labels, verbatim; calibration_check.FINDINGS must hold exactly these.
HIGH = 'biased (predictions too high)'
LOW = 'biased (predictions too low)'
OVER = 'over-confident (predictions too certain)'
UNDER = 'under-confident (predictions too uncertain)'
SHAPE = 'shape mismatch (neither a shift nor a spread error)'

ASSESSMENT_KEYS = {
    'pit_p_value',
    'coverage_p_value',
    'alpha',
    'pit_test_passed',
    'coverage_test_passed',
    'mean_pit',
    'location_t',
    'mean_coverage_deviation',
    'findings',
    'well_calibrated',
    'calibration_diagnosis',
}

PIT_PATHS = pytest.mark.parametrize('use_loo', [False, True], ids=['ppc_pit', 'loo_pit'])


def _normal_logpdf(x, loc, scale):
    return -0.5 * np.log(2 * np.pi) - np.log(scale) - 0.5 * ((x - loc) / scale) ** 2


def _normal_model(loc, scale, *, seed=SEED, drop=()):
    """DataTree for y ~ N(0, TRUE_SCALE) under a predictive N(mu, scale), mu ~ N(loc, POSTERIOR_SD_OF_MEAN).

    `drop` names groups to leave out, to exercise the CLI's group validation.
    """
    rng = np.random.default_rng(seed)
    y = rng.normal(0.0, TRUE_SCALE, size=N_OBS)
    mu = rng.normal(loc, POSTERIOR_SD_OF_MEAN, size=(N_CHAIN, N_DRAW, 1))
    y_rep = rng.normal(mu, scale, size=(N_CHAIN, N_DRAW, N_OBS))
    groups = {
        'posterior': {'mu': mu[..., 0]},
        'posterior_predictive': {'y': y_rep},
        'observed_data': {'y': y},
        'log_likelihood': {'y': _normal_logpdf(y, mu, scale)},
    }
    kept = {name: group for name, group in groups.items() if name not in drop}
    return from_dict(kept, dims={'y': ['obs']})


def _per_observation_model():
    """Correctly specified y_i ~ N(theta_i, 1), theta_i ~ N(0, 0.7): one parameter per point.

    Each theta_i's posterior is fit to its own y_i, so the in-sample predictive hugs
    the data and PPC-PIT reads it as under-confident; leaving y_i out removes that.
    """
    rng = np.random.default_rng(SEED)
    theta = rng.normal(0.0, PER_OBSERVATION_PRIOR_SD, size=N_OBS)
    y = rng.normal(theta, TRUE_SCALE)
    shrink = PER_OBSERVATION_PRIOR_SD**2 / (PER_OBSERVATION_PRIOR_SD**2 + TRUE_SCALE**2)
    theta_draws = rng.normal(shrink * y, np.sqrt(shrink) * TRUE_SCALE, size=(N_CHAIN, N_DRAW, N_OBS))
    return from_dict(
        {
            'posterior': {'theta': theta_draws},
            'posterior_predictive': {'y': rng.normal(theta_draws, TRUE_SCALE)},
            'observed_data': {'y': y},
            'log_likelihood': {'y': _normal_logpdf(y, theta_draws, TRUE_SCALE)},
        },
        dims={'y': ['obs'], 'theta': ['obs']},
    )


def _assess(loc, scale, use_loo):
    return assess_calibration(_normal_model(loc, scale), 'y', use_loo=use_loo)


@PIT_PATHS
def test_report_carries_exactly_the_eleven_documented_keys(use_loo):
    assert set(_assess(0.0, TRUE_SCALE, use_loo)) == ASSESSMENT_KEYS


@PIT_PATHS
def test_calibrated_predictive_passes_both_tests(use_loo):
    report = _assess(0.0, TRUE_SCALE, use_loo)
    assert report['pit_test_passed'] is True
    assert report['coverage_test_passed'] is True
    assert report['well_calibrated'] is True
    assert report['calibration_diagnosis'] == 'well-calibrated'


@PIT_PATHS
def test_too_narrow_predictive_is_diagnosed_over_confident(use_loo):
    report = _assess(0.0, OVER_CONFIDENT_SCALE, use_loo)
    assert report['coverage_test_passed'] is False
    assert report['well_calibrated'] is False
    # Empirical coverage below nominal: the coverage ΔECDF runs negative.
    assert report['mean_coverage_deviation'] < 0
    assert report['findings'] == [OVER]


@PIT_PATHS
def test_too_wide_predictive_is_diagnosed_under_confident(use_loo):
    report = _assess(0.0, UNDER_CONFIDENT_SCALE, use_loo)
    assert report['coverage_test_passed'] is False
    assert report['well_calibrated'] is False
    # Empirical coverage above nominal: the coverage ΔECDF runs positive.
    assert report['mean_coverage_deviation'] > 0
    assert report['findings'] == [UNDER]


@PIT_PATHS
def test_location_shift_fails_the_pit_test_alone_and_is_not_well_calibrated(use_loo):
    report = _assess(LOCATION_SHIFT, TRUE_SCALE, use_loo)
    assert report['pit_test_passed'] is False
    assert report['coverage_test_passed'] is True
    assert report['well_calibrated'] is False


def test_ppc_pit_needs_no_log_likelihood_group():
    no_log_likelihood = _normal_model(0.0, TRUE_SCALE, drop=('log_likelihood',))
    assert assess_calibration(no_log_likelihood, 'y', use_loo=False)['well_calibrated'] is True


def test_loo_pit_clears_the_double_dipping_that_ppc_pit_flags():
    # Every theta_i is fit to its own y_i, so every PPC-PIT is pulled toward 0.5 and
    # reads as under-confident. Exact leave-one-out gives the prior predictive
    # N(0, tau^2 + sigma^2), which is the data-generating process, so a correct LOO-PIT
    # is uniform. PSIS k-hat exceeds 0.7 on a few extreme-|y| points (6 of 200 at SEED).
    data = _per_observation_model()
    in_sample = assess_calibration(data, 'y', use_loo=False)
    assert in_sample['coverage_test_passed'] is False
    assert in_sample['findings'] == [UNDER]
    assert assess_calibration(data, 'y', use_loo=True)['well_calibrated'] is True


FIXTURES = {
    'calibrated': (0.0, TRUE_SCALE),
    'too_narrow': (0.0, OVER_CONFIDENT_SCALE),
    'too_wide': (0.0, UNDER_CONFIDENT_SCALE),
    'shifted_up': (LOCATION_SHIFT, TRUE_SCALE),
    'shifted_down': (-LOCATION_SHIFT, TRUE_SCALE),
}


@PIT_PATHS
@pytest.mark.parametrize('loc, scale', FIXTURES.values(), ids=FIXTURES.keys())
def test_diagnosis_reads_well_calibrated_exactly_when_the_report_is(use_loo, loc, scale):
    report = _assess(loc, scale, use_loo)
    assert (report['calibration_diagnosis'] == 'well-calibrated') is report['well_calibrated']


@PIT_PATHS
@pytest.mark.parametrize(
    'loc, direction',
    [(LOCATION_SHIFT, 'too high'), (-LOCATION_SHIFT, 'too low')],
    ids=['shifted_up', 'shifted_down'],
)
def test_location_shift_is_diagnosed_as_bias_in_its_direction(use_loo, loc, direction):
    report = _assess(loc, TRUE_SCALE, use_loo)
    assert report['findings'] == [f'biased (predictions {direction})']


def _run_cli(monkeypatch, capsys, data, *flags):
    """Run main() on in-memory data; only the netCDF load is replaced.

    Returns (exit code, the JSON on stdout, stderr).
    """
    monkeypatch.setattr(calibration_check, 'convert_to_datatree', lambda _path: data)
    monkeypatch.setattr(sys, 'argv', ['calibration_check.py', '--idata', 'in-memory.nc', *flags])
    try:
        calibration_check.main()
        exit_code = 0
    except SystemExit as exited:
        exit_code = exited.code
    captured = capsys.readouterr()
    return exit_code, json.loads(captured.out), captured.err


@pytest.mark.parametrize('missing', ['posterior', 'log_likelihood'])
def test_loo_pit_cli_names_a_missing_required_group(monkeypatch, capsys, missing):
    data = _normal_model(0.0, TRUE_SCALE, drop=(missing,))
    exit_code, output, _ = _run_cli(monkeypatch, capsys, data, '--loo-pit')
    assert exit_code == 1
    assert missing in output['error']


def test_loo_pit_cli_reports_on_data_with_every_required_group(monkeypatch, capsys):
    exit_code, output, _ = _run_cli(monkeypatch, capsys, _normal_model(0.0, TRUE_SCALE), '--loo-pit')
    assert exit_code == 0
    assert output['pit_method'] == 'loo_pit'
    assert output['assessment']['well_calibrated'] is True


@PIT_PATHS
def test_ci_prob_sets_the_test_level(use_loo):
    # At α = 0.99 a test passes only with p >= 0.99, so the calibrated fixture that passes
    # both tests at ci_prob = 0.99 fails both.
    report = assess_calibration(_normal_model(0.0, TRUE_SCALE), 'y', use_loo=use_loo, ci_prob=0.01)
    assert report['alpha'] == 0.99
    assert report['pit_test_passed'] is False
    assert report['coverage_test_passed'] is False


def test_cli_passes_ci_prob_to_the_assessment(monkeypatch, capsys):
    data = _normal_model(0.0, TRUE_SCALE)
    exit_code, output, _ = _run_cli(monkeypatch, capsys, data, '--ci-prob', '0.01')
    assert exit_code == 0
    assert output['assessment']['alpha'] == 0.99
    assert output['assessment']['pit_test_passed'] is False
    assert output['assessment']['coverage_test_passed'] is False


@PIT_PATHS
@pytest.mark.parametrize('loc, scale', FIXTURES.values(), ids=FIXTURES.keys())
def test_mean_coverage_deviation_is_the_mean_gap_between_coverage_ecdf_and_nominal(use_loo, loc, scale):
    # The mean of ECDF(c) - x over [0, 1] is 0.5 - mean(c), rounded to 4 dp, on the same
    # PIT values the verdict reads.
    data = _normal_model(loc, scale)
    coverage = 2 * np.abs(calibration_check.pit_values(data, 'y', use_loo) - 0.5)
    report = assess_calibration(data, 'y', use_loo=use_loo)
    assert report['mean_coverage_deviation'] == round(0.5 - float(coverage.mean()), 4)


def _model_with_pit_values(pit):
    """PPC-only DataTree whose PIT values are exactly `pit`: y = 0 and P(y_rep <= 0) = pit_i."""
    n_draws = N_CHAIN * N_DRAW
    quantiles = (np.arange(n_draws) + 0.5) / n_draws
    y_rep = (quantiles[:, None] - np.asarray(pit)[None, :]).reshape(N_CHAIN, N_DRAW, -1)
    return from_dict(
        {'posterior_predictive': {'y': y_rep}, 'observed_data': {'y': np.zeros(len(pit))}},
        dims={'y': ['obs']},
    )


def test_coverage_test_failing_alone_is_not_well_calibrated():
    # An even PIT grid plus a tenth of the points exactly at their predictive median: the
    # PIT test passes, while those points' coverage values all sit within 1/(S + 1) of 0,
    # which the coverage test cannot absorb. No sampling; the PIT randomization is seeded.
    n_centred = N_OBS // 10
    grid = (np.arange(N_OBS - n_centred) + 0.5) / (N_OBS - n_centred)
    report = assess_calibration(
        _model_with_pit_values(np.concatenate([grid, np.full(n_centred, 0.5)])), 'y', use_loo=False
    )
    assert report['pit_test_passed'] is True
    assert report['coverage_test_passed'] is False
    assert report['well_calibrated'] is False
    assert report['findings'] == [UNDER]


@PIT_PATHS
def test_an_observed_only_variable_does_not_disturb_the_assessed_one(use_loo):
    # The CLI's auto-detect intersects posterior_predictive with observed_data, so an
    # observed variable with no predictive counterpart is expected, not an error.
    base = _normal_model(0.0, TRUE_SCALE)
    groups = {name: {'y': base[name]['y'].values} for name in ('posterior_predictive', 'log_likelihood')}
    groups['observed_data'] = {'y': base['observed_data']['y'].values, 'x_covariate': np.arange(float(N_OBS))}
    groups['posterior'] = {'mu': base['posterior']['mu'].values}
    data = from_dict(groups, dims={'y': ['obs'], 'x_covariate': ['obs']})
    assert assess_calibration(data, 'y', use_loo=use_loo) == assess_calibration(base, 'y', use_loo=use_loo)


def _exact_pit(loc, scale, n=N_OBS):
    """PIT values of N(0, 1)'s exact quantiles under a N(loc, scale) predictive: no sampling."""
    y = stats.norm.ppf((np.arange(n) + 0.5) / n)
    return stats.norm.cdf((y - loc) / scale)


def _shape_pit(n):
    """The shape fixture recorded in specs/deferred_items.md (the calibration-labels item).

    Coverage levels c = (i + 0.5)/n sit above the predictive median (u = 0.5 + c/2) when
    c < 0.25 or c >= 0.75 and below it (u = 0.5 - c/2) otherwise: the mean PIT is exactly
    0.5 and the coverage levels exactly uniform, yet the PIT values are far from uniform.
    """
    c = (np.arange(n) + 0.5) / n
    return np.where((c < 0.25) | (c >= 0.75), 0.5 + c / 2, 0.5 - c / 2)


EXACT_RULES = {
    'calibrated': (_exact_pit(0.0, TRUE_SCALE), []),
    'shifted_up': (_exact_pit(LOCATION_SHIFT, TRUE_SCALE), [HIGH]),
    'shifted_down': (_exact_pit(-LOCATION_SHIFT, TRUE_SCALE), [LOW]),
    'too_narrow': (_exact_pit(0.0, OVER_CONFIDENT_SCALE), [OVER]),
    'too_wide': (_exact_pit(0.0, UNDER_CONFIDENT_SCALE), [UNDER]),
    'shifted_and_narrow': (_exact_pit(LOCATION_SHIFT, COMPOUND_NARROW_SCALE), [HIGH, OVER]),
    'shifted_and_wide': (_exact_pit(LOCATION_SHIFT, COMPOUND_WIDE_SCALE), [HIGH, UNDER]),
    'shape_200': (_shape_pit(200), [SHAPE]),
    'shape_400': (_shape_pit(400), [SHAPE]),
    'shape_1000': (_shape_pit(1000), [SHAPE]),
}


def test_findings_constant_holds_the_five_labels_centre_first():
    assert calibration_check.FINDINGS == (HIGH, LOW, OVER, UNDER, SHAPE)


@pytest.mark.parametrize('pit, expected', EXACT_RULES.values(), ids=EXACT_RULES.keys())
def test_every_failing_component_is_named_centre_first(pit, expected):
    assert calibration_check.assess_pit(pit)['findings'] == expected


@pytest.mark.parametrize('pit', [pit for pit, _ in EXACT_RULES.values()], ids=EXACT_RULES.keys())
def test_the_report_is_consistent_with_itself(pit):
    report = calibration_check.assess_pit(pit)
    coverage = 2 * np.abs(pit - 0.5)
    assert set(report) == ASSESSMENT_KEYS
    assert (report['findings'] == []) is report['well_calibrated']
    assert (report['calibration_diagnosis'] == 'well-calibrated') is report['well_calibrated']
    assert report['calibration_diagnosis'] == (' and '.join(report['findings']) or 'well-calibrated')
    assert report['pit_test_passed'] is (report['pit_p_value'] >= report['alpha'])
    assert report['coverage_test_passed'] is (report['coverage_p_value'] >= report['alpha'])
    assert report['mean_coverage_deviation'] == round(0.5 - float(coverage.mean()), 4)
    # Valid JSON: plain bools and floats, no NaN.
    assert json.loads(json.dumps(report)) == report


def test_alpha_is_one_minus_ci_prob_without_float_noise():
    pit = _exact_pit(0.0, TRUE_SCALE)
    assert calibration_check.assess_pit(pit)['alpha'] == 0.01
    assert calibration_check.assess_pit(pit, ci_prob=0.95)['alpha'] == 0.05


def test_location_t_is_the_one_sample_t_of_the_mean_pit():
    pit = _exact_pit(LOCATION_SHIFT, TRUE_SCALE)
    report = calibration_check.assess_pit(pit)
    t = (pit.mean() - 0.5) / (pit.std(ddof=1) / np.sqrt(len(pit)))
    assert report['location_t'] == round(float(t), 2)
    assert report['mean_pit'] == round(float(pit.mean()), 4)


def test_fewer_than_two_pit_values_raise():
    with pytest.raises(ValueError, match='at least 2'):
        calibration_check.assess_pit([0.3])


@pytest.mark.parametrize('value, shift', [(0.9375, LOW), (0.0625, HIGH)], ids=['upper_tail', 'lower_tail'])
def test_zero_spread_pit_reads_as_a_shift_with_a_null_t(value, shift):
    # Every LOO-PIT clamped to one tail. These values are exact in binary, so sd(u) is
    # exactly 0; every coverage value is 0.875, so the coverage test fails as well.
    report = calibration_check.assess_pit(np.full(N_OBS, value))
    assert report['location_t'] is None
    assert report['findings'] == [shift, OVER]
    assert json.loads(json.dumps(report)) == report


def _two_dimensional_model():
    """_normal_model's calibrated draws, reshaped into a (20, 10) observed variable."""
    flat = _normal_model(0.0, TRUE_SCALE)
    shape = (20, 10)
    return from_dict(
        {
            'posterior_predictive': {'y': flat['posterior_predictive']['y'].values.reshape(N_CHAIN, N_DRAW, *shape)},
            'observed_data': {'y': flat['observed_data']['y'].values.reshape(shape)},
        },
        dims={'y': ['row', 'col']},
    )


def _draws_below(data):
    return (data['posterior_predictive']['y'] < data['observed_data']['y']).sum(('chain', 'draw')).values


def test_ppc_pit_values_sit_strictly_inside_the_unit_interval_and_repeat_for_a_seed():
    # A too-narrow predictive leaves observations with every draw on one side of them,
    # where a grid PIT reads exactly 0 or 1.
    data = _normal_model(0.0, OVER_CONFIDENT_SCALE)
    below = _draws_below(data)
    assert (below == 0).any() and (below == N_CHAIN * N_DRAW).any()
    pit = calibration_check.pit_values(data, 'y', use_loo=False)
    assert pit.min() > 0 and pit.max() < 1
    assert calibration_check.PIT_SEED == 214
    np.testing.assert_array_equal(pit, calibration_check.pit_values(data, 'y', use_loo=False))
    reseeded = calibration_check.pit_values(data, 'y', use_loo=False, seed=calibration_check.PIT_SEED + 1)
    assert not np.array_equal(pit, reseeded)


def test_a_pit_at_the_predictive_median_does_not_break_the_coverage_test():
    # An odd centred grid holds one PIT of exactly 0.5, so one observation has exactly S/2
    # of the S = 1000 draws below it. The grid PIT k/S puts it at u = 0.5, coverage 0, and
    # pot_c's coverage test collapses on this calibrated fixture.
    data = _model_with_pit_values((np.arange(N_OBS - 1) + 0.5) / (N_OBS - 1))
    n_draws = N_CHAIN * N_DRAW
    below = _draws_below(data)
    assert np.sum(below == n_draws // 2) == 1
    assert calibration_check.assess_pit(below / n_draws)['coverage_test_passed'] is False
    pit = calibration_check.pit_values(data, 'y', use_loo=False)
    assert not np.any(pit == 0.5)
    assert calibration_check.assess_pit(pit)['coverage_test_passed'] is True


def test_discrete_pit_values_land_inside_their_rank_cell():
    # Poisson data under a Poisson predictive, so draws tie with y. The rank k spreads
    # over {below, ..., below + ties}, so u lands in [below, below + ties + 1) / (S + 1).
    rng = np.random.default_rng(SEED)
    y = rng.poisson(DISCRETE_RATE, size=N_OBS)
    y_rep = rng.poisson(DISCRETE_RATE, size=(N_CHAIN, N_DRAW, N_OBS))
    data = from_dict({'posterior_predictive': {'y': y_rep}, 'observed_data': {'y': y}}, dims={'y': ['obs']})
    draws = y_rep.reshape(-1, N_OBS)
    below, ties = (draws < y).sum(axis=0), (draws == y).sum(axis=0)
    assert (ties > 0).sum() > N_OBS // 2
    n_draws = N_CHAIN * N_DRAW
    pit = calibration_check.pit_values(data, 'y', use_loo=False)
    assert np.all(pit >= below / (n_draws + 1))
    assert np.all(pit < (below + ties + 1) / (n_draws + 1))


def test_a_two_dimensional_observed_variable_is_pooled():
    # The same draws, as a (20, 10) variable and as a flat 200: the same values in the same order.
    np.testing.assert_array_equal(
        calibration_check.pit_values(_two_dimensional_model(), 'y', use_loo=False),
        calibration_check.pit_values(_normal_model(0.0, TRUE_SCALE), 'y', use_loo=False),
    )


def test_loo_pit_values_are_arviz_pareto_smoothed_loo_pit():
    data = _normal_model(0.0, TRUE_SCALE)
    np.testing.assert_array_equal(
        calibration_check.pit_values(data, 'y', use_loo=True),
        azs.loo_pit(data, var_names='y', pareto_pit=True)['y'].values,
    )


def test_cli_reports_too_few_observations_as_a_json_error(monkeypatch, capsys):
    rng = np.random.default_rng(SEED)
    data = from_dict(
        {'posterior_predictive': {'y': rng.normal(size=(N_CHAIN, N_DRAW, 1))}, 'observed_data': {'y': np.zeros(1)}},
        dims={'y': ['obs']},
    )
    exit_code, output, _ = _run_cli(monkeypatch, capsys, data)
    assert exit_code == 1
    assert 'at least 2' in output['error']


def test_n_observations_counts_every_pooled_pit_value(monkeypatch, capsys):
    exit_code, output, _ = _run_cli(monkeypatch, capsys, _two_dimensional_model())
    assert exit_code == 0
    assert output['n_observations'] == N_OBS


@pytest.mark.parametrize('binary', [True, False], ids=['binary', 'continuous'])
def test_binary_observations_warn_toward_plot_ppc_pava(monkeypatch, capsys, binary):
    rng = np.random.default_rng(SEED)
    if binary:
        y = rng.integers(0, 2, size=N_OBS)
        y_rep = rng.integers(0, 2, size=(N_CHAIN, N_DRAW, N_OBS))
        data = from_dict({'posterior_predictive': {'y': y_rep}, 'observed_data': {'y': y}}, dims={'y': ['obs']})
    else:
        data = _normal_model(0.0, TRUE_SCALE)
    exit_code, _, stderr = _run_cli(monkeypatch, capsys, data)
    assert exit_code == 0
    if binary:
        assert 'plot_ppc_pava' in stderr
    else:
        assert stderr == ''


def _record_figures(monkeypatch):
    """Replace azp.plot_ecdf_pit with a recorder. Returns its list of (tree, kwargs) calls."""
    calls = []

    class _Figure:
        def savefig(self, _path):
            pass

    def record(tree, **kwargs):
        calls.append((tree, kwargs))
        return _Figure()

    monkeypatch.setattr(calibration_check.azp, 'plot_ecdf_pit', record)
    return calls


@PIT_PATHS
def test_both_figures_draw_the_pit_values_the_json_judged(monkeypatch, capsys, tmp_path, use_loo):
    calls = _record_figures(monkeypatch)
    data = _normal_model(0.0, TRUE_SCALE)
    flags = ['--save-plots', '--plot-dir', str(tmp_path), '--ci-prob', '0.95'] + (['--loo-pit'] if use_loo else [])
    exit_code, output, _ = _run_cli(monkeypatch, capsys, data, *flags)
    assert exit_code == 0
    pit = calibration_check.pit_values(data, 'y', use_loo)
    assert output['assessment'] == calibration_check.assess_pit(pit, ci_prob=0.95)
    assert [kwargs['coverage'] for _, kwargs in calls] == [False, True]
    for tree, kwargs in calls:
        np.testing.assert_array_equal(tree['ecdf_pit']['y'].values, pit)
        assert kwargs['method'] == 'pot_c'
        assert kwargs['envelope_prob'] == 0.95
    prefix = 'loo_pit' if use_loo else 'pit'
    assert output['plots'] == {
        'pit_ecdf': str(tmp_path / f'{prefix}_ecdf.png'),
        'coverage': str(tmp_path / f'{prefix}_coverage.png'),
    }


def test_each_figure_prints_the_p_value_its_json_verdict_records(monkeypatch, tmp_path):
    matplotlib = pytest.importorskip('matplotlib')
    matplotlib.use('Agg')
    from matplotlib.text import Text

    drawn = []
    draw = calibration_check.azp.plot_ecdf_pit

    def draw_and_keep(*args, **kwargs):
        drawn.append(draw(*args, **kwargs))
        return drawn[-1]

    monkeypatch.setattr(calibration_check.azp, 'plot_ecdf_pit', draw_and_keep)
    # The per-observation LOO-PIT prints two distinct p-values (0.18 and 0.09), so a
    # figure showing the other test's p-value would fail here.
    pit = calibration_check.pit_values(_per_observation_model(), 'y', use_loo=True)
    report = calibration_check.assess_pit(pit)
    for coverage, key in ((False, 'pit_p_value'), (True, 'coverage_p_value')):
        calibration_check.save_pit_plot(pit, tmp_path / f'{key}.png', var_name='y', coverage=coverage)
        figure = drawn[-1].viz['figure'].item()
        printed = [text.get_text() for text in figure.findobj(Text) if text.get_text().startswith('p=')]
        assert len(printed) == 1
        assert printed[0].startswith(f'p={report[key]:.2f}(α={report["alpha"]:.2f})')
        matplotlib.pyplot.close('all')


@pytest.mark.parametrize('label', calibration_check.FINDINGS)
def test_every_finding_reaches_a_specific_next_step(label):
    # check_diagnostics.py keeps its own copy of the labels, since importing
    # calibration_check would pull the ArviZ stack into a pure-JSON reader. A label it
    # cannot route falls through to the generic step. A |deviation| above 0.05 rates
    # calibration poor, so the spread labels take their specific steps.
    calibration = {
        'assessment': {
            'findings': [label],
            'well_calibrated': False,
            'calibration_diagnosis': label,
            'mean_coverage_deviation': -0.3,
        }
    }
    report = check_diagnostics.check_diagnostics(calibration=calibration)
    steps = [step for step in check_diagnostics.suggest_next_steps(report) if step.startswith('Calibration')]
    assert len(steps) == 1, steps
    assert 'Calibration check failed' not in steps[0]


SWEEP = pytest.mark.skipif(
    os.environ.get('CALIBRATION_SWEEP') != '1',
    reason='pre-registered acceptance sweep: set CALIBRATION_SWEEP=1 (seeds 0-99, both paths)',
)
SWEEP_SEEDS = range(100)
MILDLY_NARROW_SCALE = 0.8
SMALL_SHIFT = 0.25
SKEWED_SHAPE = 2.0  # Gamma(2), standardized to mean 0 and sd 1: right-skewed
AT_LEAST, AT_MOST = operator.ge, operator.le


def _named(label):
    return lambda findings: label in findings


def _exactly(*labels):
    return lambda findings: findings == list(labels)


def _any_biased(findings):
    return HIGH in findings or LOW in findings


# The spec's pre-registered thresholds (specs/calibration-check-verdicts.md, "Acceptance"),
# set from the 2026-10-03 probe before implementation. A miss is a finding for the owner,
# never a reason to edit a threshold. "Named" counts any finding list that holds the label.
SWEEP_THRESHOLDS = {
    'calibrated': ((0.0, TRUE_SCALE), [('well-calibrated', _exactly(), AT_LEAST, 95)]),
    'too_narrow': ((0.0, OVER_CONFIDENT_SCALE), [('exactly [over-confident]', _exactly(OVER), AT_LEAST, 95)]),
    'too_wide': ((0.0, UNDER_CONFIDENT_SCALE), [('exactly [under-confident]', _exactly(UNDER), AT_LEAST, 95)]),
    'mildly_narrow': (
        (0.0, MILDLY_NARROW_SCALE),
        [('over-confident named', _named(OVER), AT_LEAST, 80), ('any biased named', _any_biased, AT_MOST, 5)],
    ),
    'shift_up': (
        (LOCATION_SHIFT, TRUE_SCALE),
        [('biased (predictions too high) named', _named(HIGH), AT_LEAST, 95),
         ('biased (predictions too low) named', _named(LOW), AT_MOST, 0)],
    ),
    'shift_down': (
        (-LOCATION_SHIFT, TRUE_SCALE),
        [('biased (predictions too low) named', _named(LOW), AT_LEAST, 95),
         ('biased (predictions too high) named', _named(HIGH), AT_MOST, 0)],
    ),
    'small_shift': ((SMALL_SHIFT, TRUE_SCALE), [('biased (predictions too high) named', _named(HIGH), AT_LEAST, 60)]),
    'shift_and_narrow': (
        (LOCATION_SHIFT, COMPOUND_NARROW_SCALE),
        [('exactly [biased (predictions too high), over-confident]', _exactly(HIGH, OVER), AT_LEAST, 95)],
    ),
    'shift_and_wide': (
        (LOCATION_SHIFT, COMPOUND_WIDE_SCALE),
        [('exactly [biased (predictions too high), under-confident]', _exactly(HIGH, UNDER), AT_LEAST, 95)],
    ),
}


def _skewed_model(*, seed):
    """y ~ N(0, 1) under a standardized Gamma(2) predictive: the right mean and spread, the wrong shape."""
    rng = np.random.default_rng(seed)
    y = rng.normal(0.0, TRUE_SCALE, size=N_OBS)
    mu = rng.normal(0.0, POSTERIOR_SD_OF_MEAN, size=(N_CHAIN, N_DRAW, 1))
    gamma = rng.gamma(SKEWED_SHAPE, 1.0, size=(N_CHAIN, N_DRAW, N_OBS))
    y_rep = mu + (gamma - SKEWED_SHAPE) / np.sqrt(SKEWED_SHAPE)
    return from_dict({'posterior_predictive': {'y': y_rep}, 'observed_data': {'y': y}}, dims={'y': ['obs']})


def _sweep(build, use_loo):
    """The findings for each sweep seed of the fixture `build(seed=...)` builds."""
    return [assess_calibration(build(seed=seed), 'y', use_loo=use_loo)['findings'] for seed in SWEEP_SEEDS]


@SWEEP
@PIT_PATHS
def test_acceptance_sweep_meets_the_pre_registered_thresholds(use_loo):
    path = 'loo_pit' if use_loo else 'ppc_pit'
    misses = []
    for fixture, ((loc, scale), checks) in SWEEP_THRESHOLDS.items():
        runs = _sweep(functools.partial(_normal_model, loc, scale), use_loo)
        for what, holds, compare, bound in checks:
            count = sum(1 for findings in runs if holds(findings))
            print(f'{path} {fixture}: {what} {count}/{len(runs)}')
            if not compare(count, bound):
                misses.append(f'{fixture}: {what} {count}, needs {compare.__name__} {bound}')
    if not use_loo:
        # PPC only: PSIS fails on observations outside the predictive's support in every draw.
        split = Counter(' and '.join(findings) or 'well-calibrated' for findings in _sweep(_skewed_model, use_loo))
        print(f'{path} skewed (a known limit, recorded with no threshold): {dict(split.most_common())}')
    assert not misses, misses
