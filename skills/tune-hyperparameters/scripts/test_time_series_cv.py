import numpy as np
import pytest

from time_series_cv import PurgedTimeSeriesSplit


def test_no_future_leakage_and_embargo():
    X = np.arange(100).reshape(-1, 1)
    cv = PurgedTimeSeriesSplit(n_splits=5, embargo=3)
    folds = list(cv.split(X))
    assert len(folds) == 5
    for tr, va in folds:
        assert tr.max() < va.min()                 # train strictly before val
        assert va.min() - tr.max() - 1 >= 3        # embargo gap respected


def test_expanding_window_and_n_splits():
    X = np.arange(120).reshape(-1, 1)
    cv = PurgedTimeSeriesSplit(n_splits=4)
    sizes = [len(tr) for tr, _ in cv.split(X)]
    assert sizes == sorted(sizes)                  # non-decreasing train size
    assert cv.get_n_splits() == 4
    assert len(sizes) == 4


def test_purge_is_conditional_on_horizon():
    X = np.arange(100).reshape(-1, 1)
    # horizon=0 keeps the pre-val rows; horizon=3 purges the 3 rows before val.
    f0 = list(PurgedTimeSeriesSplit(n_splits=5, embargo=0, label_horizon=0).split(X))
    f3 = list(PurgedTimeSeriesSplit(n_splits=5, embargo=0, label_horizon=3).split(X))
    assert len(f0) == len(f3)
    for (tr0, va0), (tr3, va3) in zip(f0, f3):
        s = int(va0.min())
        assert (s - 1) in tr0                      # horizon=0: overlapping row present
        for i in range(s - 3, s):
            assert i not in tr3                    # horizon=3: purged
        assert (s - 4) in tr3                      # exactly h rows purged, NOT more
        assert tr3.max() < va3.min()


def test_min_train_size_skips_short_folds():
    X = np.arange(60).reshape(-1, 1)
    cv = PurgedTimeSeriesSplit(n_splits=5, min_train_size=25)
    folds = list(cv.split(X))
    assert folds                                   # at least one fold survives
    for tr, _ in folds:
        assert len(tr) >= 25
    # split() prunes short early folds, yielding FEWER than the requested count.
    assert len(folds) < cv.get_n_splits()          # no X: reports the request
    assert cv.get_n_splits(X) == len(folds)        # with X: realized == yielded


def test_zero_folds_raises():
    # A config where the guard swallows every fold must fail loudly, not yield
    # an empty CV (whose np.mean([]) would be a silent nan best-value).
    X = np.arange(100).reshape(-1, 1)
    with pytest.raises(ValueError, match='no folds'):
        list(PurgedTimeSeriesSplit(n_splits=5, embargo=200).split(X))


def test_sklearn_search_contract_with_dropped_folds():
    # The reviewer's concrete failure: GridSearchCV(cv=splitter) raised
    # "cv.split and cv.get_n_splits return inconsistent results" when
    # min_train_size pruned folds. get_n_splits(X) now reports the realized
    # count, so the sklearn contract holds and the search fits.
    pytest.importorskip('sklearn')
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import GridSearchCV

    rng = np.random.default_rng(0)
    n = 120
    X = rng.normal(size=(n, 2))
    y = X @ np.array([1.0, -1.0]) + rng.normal(scale=0.3, size=n)
    cv = PurgedTimeSeriesSplit(n_splits=5, embargo=1, min_train_size=40)
    realized = len(list(cv.split(X)))
    assert realized < cv.n_splits                  # folds are actually dropped
    assert cv.get_n_splits(X) == realized          # contract holds with X
    gs = GridSearchCV(Ridge(), {'alpha': [0.1, 1.0, 10.0]}, cv=cv)
    gs.fit(X, y)                                    # must NOT raise inconsistent-splits
    assert gs.best_params_['alpha'] in (0.1, 1.0, 10.0)


def test_rejects_bad_args():
    with pytest.raises(ValueError):
        PurgedTimeSeriesSplit(n_splits=0)
    with pytest.raises(ValueError):
        PurgedTimeSeriesSplit(embargo=-1)


def test_optuna_manual_objective_integration():
    optuna = pytest.importorskip('optuna')
    from sklearn.linear_model import Ridge
    from sklearn.metrics import mean_squared_error

    rng = np.random.default_rng(0)
    n = 200
    X = rng.normal(size=(n, 3))
    beta = np.array([1.5, -2.0, 0.5])
    y = X @ beta + rng.normal(scale=0.5, size=n)
    cv = PurgedTimeSeriesSplit(n_splits=4, embargo=2)

    def objective(trial):
        alpha = trial.suggest_float('alpha', 1e-3, 1e3, log=True)
        scores = []
        for tr, va in cv.split(X):
            model = Ridge(alpha=alpha).fit(X[tr], y[tr])
            scores.append(mean_squared_error(y[va], model.predict(X[va])))
        return float(np.mean(scores))

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction='minimize',
                                sampler=optuna.samplers.TPESampler(seed=0))
    study.optimize(objective, n_trials=15)
    assert np.isfinite(study.best_value)
    assert 1e-3 <= study.best_params['alpha'] <= 1e3


def _panel_periods(n_entities=3, n_periods=20, entity_major=False):
    '''Each row's period in a long-format panel of n_entities series.

    Period-major rows run (t0 e0, t0 e1, ...); entity-major rows run
    (e0 t0, e0 t1, ...), so the labels are not sorted.
    '''
    periods = np.arange(n_periods)
    if entity_major:
        return np.tile(periods, n_entities)
    return np.repeat(periods, n_entities)


@pytest.mark.parametrize('entity_major', [False, True])
@pytest.mark.parametrize('embargo', [0, 1, 2])
def test_panel_folds_split_whole_periods(embargo, entity_major):
    period = _panel_periods(entity_major=entity_major)
    X = np.zeros((period.size, 1))
    folds = list(PurgedTimeSeriesSplit(n_splits=5, embargo=embargo).split(X, groups=period))
    assert len(folds) == 5
    for tr, va in folds:
        assert not set(period[tr]) & set(period[va])                # no period on both sides
        assert period[va].min() - period[tr].max() - 1 >= embargo   # the gap counts whole periods
        assert len(va) == 3 * len(set(period[va]))                  # val holds every row of its periods


def test_panel_sizes_count_periods():
    period = _panel_periods(n_periods=20)
    X = np.zeros((period.size, 1))
    cv = PurgedTimeSeriesSplit(n_splits=4, test_size=2, min_train_size=13)
    folds = list(cv.split(X, groups=period))
    assert len(folds) == 3                                   # the fold with 12 train periods is pruned
    for tr, va in folds:
        assert len(set(period[va])) == 2                     # test_size counts periods
        assert len(set(period[tr])) >= 13                    # min_train_size counts periods
    assert cv.get_n_splits(X, groups=period) == len(folds)   # get_n_splits forwards groups


def test_one_row_per_period_matches_row_mode():
    X = np.arange(100).reshape(-1, 1)
    cv = PurgedTimeSeriesSplit(n_splits=5, embargo=2, label_horizon=3, min_train_size=10)
    rows = list(cv.split(X))
    periods = list(cv.split(X, groups=np.arange(100)))
    assert len(rows) == len(periods)
    for (tr_r, va_r), (tr_p, va_p) in zip(rows, periods):
        np.testing.assert_array_equal(tr_r, tr_p)
        np.testing.assert_array_equal(va_r, va_p)


def test_groups_length_must_match_rows():
    X = np.zeros((10, 1))
    with pytest.raises(ValueError, match='groups'):
        list(PurgedTimeSeriesSplit(n_splits=2).split(X, groups=np.arange(9)))


def test_sklearn_search_with_panel_groups():
    pytest.importorskip('sklearn')
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import GridSearchCV

    rng = np.random.default_rng(0)
    period = _panel_periods(n_periods=40)
    X = rng.normal(size=(period.size, 2))
    y = X @ np.array([1.0, -1.0]) + rng.normal(scale=0.3, size=period.size)
    cv = PurgedTimeSeriesSplit(n_splits=5, embargo=1, min_train_size=15)
    realized = len(list(cv.split(X, groups=period)))
    assert realized == 4                                     # 9 train periods < 15: pruned
    assert cv.get_n_splits(X, groups=period) == realized
    gs = GridSearchCV(Ridge(), {'alpha': [0.1, 1.0, 10.0]}, cv=cv)
    gs.fit(X, y, groups=period)                              # sklearn hands groups to split()
    assert gs.n_splits_ == realized
