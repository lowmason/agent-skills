'''Leakage-safe temporal cross-validation for hyperparameter tuning.

Forward-chaining (expanding-window) splitter with an embargo gap and an optional
label-horizon purge. For point-in-time targets, sklearn's
TimeSeriesSplit(gap=embargo) already suffices; reach for the purge
(label_horizon > 0) only when the target spans multiple periods so a training
row's label window [i, i+h] overlaps the validation block.

Guards TEMPORAL leakage only (train precedes val; embargo; purge). It does NOT
guard revision/vintage leakage — that belongs to the develop-testing-strategy
skill; a green temporal-CV is not, on its own, 'leakage-free' for revised series.
'''
import numpy as np


def _n_samples(X):
    return X.shape[0] if hasattr(X, 'shape') else len(X)


class PurgedTimeSeriesSplit:
    '''Expanding-window CV with embargo + optional label-horizon purge.

    train = [0, s_k - max(embargo, label_horizon)); val = [s_k, s_k + test_size).
    Yields NumPy index arrays; duck-types sklearn's splitter API (split /
    get_n_splits) so it drops into a manual Optuna objective or sklearn search.
    '''

    def __init__(self, n_splits=5, test_size=None, embargo=0, label_horizon=0,
                 min_train_size=None):
        if n_splits < 1:
            raise ValueError('n_splits must be >= 1')
        if embargo < 0 or label_horizon < 0:
            raise ValueError('embargo and label_horizon must be >= 0')
        self.n_splits = n_splits
        self.test_size = test_size
        self.embargo = embargo
        self.label_horizon = label_horizon
        self.min_train_size = min_train_size

    def get_n_splits(self, X=None, y=None, groups=None):
        return self.n_splits

    def split(self, X, y=None, groups=None):
        n = _n_samples(X)
        test_size = self.test_size or n // (self.n_splits + 1)
        if test_size < 1:
            raise ValueError('test_size resolved to 0; too few samples for n_splits')
        guard = max(self.embargo, self.label_horizon)
        for k in range(self.n_splits):
            s = n - (self.n_splits - k) * test_size
            train_end = s - guard
            if train_end <= 0:
                continue
            if self.min_train_size is not None and train_end < self.min_train_size:
                continue
            train_idx = np.arange(0, train_end)
            val_idx = np.arange(s, min(s + test_size, n))
            yield train_idx, val_idx
