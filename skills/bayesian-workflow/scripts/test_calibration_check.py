"""Tests for calibration_check.py — run from this directory (bare imports).

cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz \
  --with arviz-stats --with numpy --with xarray python -m pytest -q

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

import json
import sys

import arviz_stats as azs
import numpy as np
import pytest
from arviz_base import from_dict
from scipy import stats

import calibration_check
from calibration_check import assess_calibration

N_OBS, N_CHAIN, N_DRAW = 200, 2, 500
TRUE_SCALE = 1.0
OVER_CONFIDENT_SCALE = 0.3  # predictive far narrower than the data
UNDER_CONFIDENT_SCALE = 3.0  # predictive far wider than the data
# Right spread, biased centre: the PIT band fails. The coverage fold is only second-order
# sensitive to a shift, so it holds at SEED (and on most seeds, not all).
LOCATION_SHIFT = 0.4
COMPOUND_NARROW_SCALE = 0.7  # paired with LOCATION_SHIFT: a shift and a spread error at once
COMPOUND_WIDE_SCALE = 1.5
POSTERIOR_SD_OF_MEAN = 0.05
PER_OBSERVATION_PRIOR_SD = 0.7
# A calibrated model is still flagged at ci_prob=0.99 on ~2-3% of seeds (3 of seeds
# 0-99, on both paths): each of the two simultaneous bands has its own false-alarm
# rate. Both the data and arviz-stats' band simulation are seeded, so the outcome
# for this seed is deterministic.
SEED = 0

REPORT_KEYS = {
    'pit_ecdf_inside_bands',
    'coverage_ecdf_inside_bands',
    'well_calibrated',
    'mean_coverage_deviation',
    'calibration_diagnosis',
}

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


def _normal_model(loc, scale, *, drop=()):
    """DataTree for y ~ N(0, TRUE_SCALE) under a predictive N(mu, scale), mu ~ N(loc, POSTERIOR_SD_OF_MEAN).

    `drop` names groups to leave out, to exercise the CLI's group validation.
    """
    rng = np.random.default_rng(SEED)
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
def test_report_carries_exactly_the_five_documented_keys(use_loo):
    assert set(_assess(0.0, TRUE_SCALE, use_loo)) == REPORT_KEYS


@PIT_PATHS
def test_calibrated_predictive_is_inside_both_bands(use_loo):
    report = _assess(0.0, TRUE_SCALE, use_loo)
    assert report['pit_ecdf_inside_bands'] is True
    assert report['coverage_ecdf_inside_bands'] is True
    assert report['well_calibrated'] is True
    assert report['calibration_diagnosis'] == 'well-calibrated'


@PIT_PATHS
def test_too_narrow_predictive_is_diagnosed_over_confident(use_loo):
    report = _assess(0.0, OVER_CONFIDENT_SCALE, use_loo)
    assert report['coverage_ecdf_inside_bands'] is False
    assert report['well_calibrated'] is False
    # Empirical coverage below nominal: the coverage ΔECDF runs negative.
    assert report['mean_coverage_deviation'] < 0
    assert report['calibration_diagnosis'].startswith('over-confident')


@PIT_PATHS
def test_too_wide_predictive_is_diagnosed_under_confident(use_loo):
    report = _assess(0.0, UNDER_CONFIDENT_SCALE, use_loo)
    assert report['coverage_ecdf_inside_bands'] is False
    assert report['well_calibrated'] is False
    # Empirical coverage above nominal: the coverage ΔECDF runs positive.
    assert report['mean_coverage_deviation'] > 0
    assert report['calibration_diagnosis'].startswith('under-confident')


@PIT_PATHS
def test_location_shift_fails_the_pit_band_alone_and_is_not_well_calibrated(use_loo):
    report = _assess(LOCATION_SHIFT, TRUE_SCALE, use_loo)
    assert report['pit_ecdf_inside_bands'] is False
    assert report['coverage_ecdf_inside_bands'] is True
    assert report['well_calibrated'] is False


def test_ppc_pit_needs_no_log_likelihood_group():
    no_log_likelihood = _normal_model(0.0, TRUE_SCALE, drop=('log_likelihood',))
    assert assess_calibration(no_log_likelihood, 'y', use_loo=False)['well_calibrated'] is True


def test_loo_pit_clears_the_double_dipping_that_ppc_pit_flags():
    # Every theta_i is fit to its own y_i, so every PPC-PIT is pulled toward 0.5 and
    # reads as under-confident. Exact leave-one-out gives the prior predictive
    # N(0, tau^2 + sigma^2), which is the data-generating process, so a correct LOO-PIT
    # is uniform. PSIS k-hat exceeds 0.7 on a few extreme-|y| points (6 of 200 at
    # SEED); both assertions held on every one of seeds 0-9.
    data = _per_observation_model()
    in_sample = assess_calibration(data, 'y', use_loo=False)
    assert in_sample['coverage_ecdf_inside_bands'] is False
    assert in_sample['calibration_diagnosis'].startswith('under-confident')
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
    assert report['calibration_diagnosis'] == f'biased (predictions {direction})'


def _run_cli(monkeypatch, capsys, data, *flags):
    """Run main() on in-memory data; only the netCDF load is replaced. Returns (exit code, JSON)."""
    monkeypatch.setattr(calibration_check, 'convert_to_datatree', lambda _path: data)
    monkeypatch.setattr(sys, 'argv', ['calibration_check.py', '--idata', 'in-memory.nc', *flags])
    try:
        calibration_check.main()
        exit_code = 0
    except SystemExit as exited:
        exit_code = exited.code
    return exit_code, json.loads(capsys.readouterr().out)


@pytest.mark.parametrize('missing', ['posterior', 'log_likelihood'])
def test_loo_pit_cli_names_a_missing_required_group(monkeypatch, capsys, missing):
    data = _normal_model(0.0, TRUE_SCALE, drop=(missing,))
    exit_code, output = _run_cli(monkeypatch, capsys, data, '--loo-pit')
    assert exit_code == 1
    assert missing in output['error']


def test_loo_pit_cli_reports_on_data_with_every_required_group(monkeypatch, capsys):
    exit_code, output = _run_cli(monkeypatch, capsys, _normal_model(0.0, TRUE_SCALE), '--loo-pit')
    assert exit_code == 0
    assert output['pit_method'] == 'loo_pit'
    assert output['assessment']['well_calibrated'] is True


@PIT_PATHS
def test_ci_prob_sets_the_band_level(use_loo):
    # A 1% simultaneous band admits a calibrated ΔECDF about 1% of the time, so the
    # fixture inside both bands at 0.99 falls outside both. Held on seeds 0-9.
    report = assess_calibration(_normal_model(0.0, TRUE_SCALE), 'y', use_loo=use_loo, ci_prob=0.01)
    assert report['pit_ecdf_inside_bands'] is False
    assert report['coverage_ecdf_inside_bands'] is False


def test_cli_passes_ci_prob_to_the_assessment(monkeypatch, capsys):
    data = _normal_model(0.0, TRUE_SCALE)
    exit_code, output = _run_cli(monkeypatch, capsys, data, '--ci-prob', '0.01')
    assert exit_code == 0
    assert output['assessment']['pit_ecdf_inside_bands'] is False
    assert output['assessment']['coverage_ecdf_inside_bands'] is False


def _coverage_levels(data, use_loo):
    """Each observation's coverage level 2|u - 0.5|, from PIT values computed independently."""
    if use_loo:
        pit = azs.loo_pit(data, var_names='y')['y'].values
    else:
        pit = (data['posterior_predictive']['y'] <= data['observed_data']['y']).mean(('chain', 'draw')).values
    return 2 * np.abs(pit - 0.5)


@PIT_PATHS
@pytest.mark.parametrize('loc, scale', FIXTURES.values(), ids=FIXTURES.keys())
def test_mean_coverage_deviation_is_the_mean_gap_between_coverage_ecdf_and_nominal(use_loo, loc, scale):
    # On the evaluation grid 0, 1/N, ..., 1 the mean of ECDF(c) - x is 0.5 - mean(c) up
    # to 1/(N_OBS + 1); the report rounds to 4 dp. The gap is under 0.00503.
    data = _normal_model(loc, scale)
    expected = 0.5 - _coverage_levels(data, use_loo).mean()
    report = assess_calibration(data, 'y', use_loo=use_loo)
    assert report['mean_coverage_deviation'] == pytest.approx(expected, abs=0.006)


def _model_with_pit_values(pit):
    """PPC-only DataTree whose PIT values are exactly `pit`: y = 0 and P(y_rep <= 0) = pit_i."""
    n_draws = N_CHAIN * N_DRAW
    quantiles = (np.arange(n_draws) + 0.5) / n_draws
    y_rep = (quantiles[:, None] - np.asarray(pit)[None, :]).reshape(N_CHAIN, N_DRAW, -1)
    return from_dict(
        {'posterior_predictive': {'y': y_rep}, 'observed_data': {'y': np.zeros(len(pit))}},
        dims={'y': ['obs']},
    )


def test_coverage_band_failing_alone_is_not_well_calibrated():
    # An even PIT grid plus a tenth of the points exactly at their predictive median: the
    # PIT ECDF stays inside its band, while the coverage ECDF starts 0.1 too high, which
    # its band cannot absorb. No random draws are involved.
    n_centred = N_OBS // 10
    grid = (np.arange(N_OBS - n_centred) + 0.5) / (N_OBS - n_centred)
    report = assess_calibration(
        _model_with_pit_values(np.concatenate([grid, np.full(n_centred, 0.5)])), 'y', use_loo=False
    )
    assert report['pit_ecdf_inside_bands'] is True
    assert report['coverage_ecdf_inside_bands'] is False
    assert report['well_calibrated'] is False
    assert report['calibration_diagnosis'].startswith('under-confident')


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
