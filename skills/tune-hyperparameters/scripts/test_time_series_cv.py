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
