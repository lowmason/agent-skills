'''Leakage-safe temporal cross-validation for hyperparameter tuning.

Forward-chaining (expanding-window) splitter with an embargo gap and an optional
label-horizon purge, all counted in periods. Without groups each row is one
period, which fits a single series. For a long-format panel (several series
observed at the same periods), pass each row's period as groups: the folds then
split whole periods, so no period lands in both train and validation.

The splitter orders the periods by sorting the labels in groups, so the labels
must sort in time order. Integers, datetime64, pandas Period and zero-padded ISO
strings such as '2020-09' do. '2020-9' does not: it sorts after '2020-12', so a
fold would train on later periods than it validates on. Embargo, label_horizon
and the sizes count the periods present in groups, not calendar periods. A
missing calendar period leaves a wider real gap.

For a single series with a point-in-time target, sklearn's
TimeSeriesSplit(gap=embargo) already suffices. It splits rows, so on a panel it
leaks the way this splitter does without groups. Reach for the purge
(label_horizon > 0) only when the target spans multiple periods so a training
row's label window [i, i+h] overlaps the validation block.

Guards TEMPORAL leakage only (train precedes val; embargo; purge). It does NOT
guard revision/vintage leakage — that belongs to the develop-testing-strategy
skill; a green temporal-CV is not, on its own, 'leakage-free' for revised series.
'''
import numpy as np


def _n_samples(X):
    return X.shape[0] if hasattr(X, 'shape') else len(X)


def _period_index(n, groups):
    '''Each row's position among the sorted unique periods, and the period count.

    Without groups each row is its own period, in row order.
    '''
    if groups is None:
        return np.arange(n), n
    labels = np.asarray(groups)
    if labels.shape[0] != n:
        raise ValueError(f'groups has {labels.shape[0]} labels for {n} rows')
    periods, index = np.unique(labels, return_inverse=True)
    return index.ravel(), len(periods)


class PurgedTimeSeriesSplit:
    '''Expanding-window CV with embargo + optional label-horizon purge.

    In periods: train = [0, s_k - max(embargo, label_horizon)); val = [s_k,
    s_k + test_size). test_size, embargo, label_horizon and min_train_size all
    count periods present in groups, not calendar periods; split(X,
    groups=period) maps them back to rows, and without groups each row is one
    period. The groups labels must sort in time order (integers, datetime64,
    pandas Period and zero-padded ISO strings such as '2020-09' do; '2020-9'
    does not), because the splitter orders periods by sorting the labels. A
    missing calendar period leaves a wider real gap. Yields NumPy row-index
    arrays; duck-types sklearn's splitter API (split / get_n_splits) so it
    drops into a manual Optuna objective or sklearn search
    (GridSearchCV.fit(X, y, groups=period)).
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
        '''Number of folds this splitter will actually yield.

        With X given, returns the REALIZED fold count: min_train_size and small
        samples prune short early folds, so it can be less than the requested
        n_splits. Passing X keeps sklearn's splitter contract
        (get_n_splits(X) == len(list(split(X)))), so GridSearchCV /
        cross_validate work despite pruning. With X=None there is no data to
        measure against, so it falls back to the requested n_splits. It forwards
        groups to split, so pass the same groups that split gets.
        '''
        if X is None:
            return self.n_splits
        return sum(1 for _ in self.split(X, y, groups))

    def split(self, X, y=None, groups=None):
        period, n_periods = _period_index(_n_samples(X), groups)
        test_size = self.test_size or n_periods // (self.n_splits + 1)
        if test_size < 1:
            raise ValueError('test_size resolved to 0; too few periods for n_splits')
        guard = max(self.embargo, self.label_horizon)
        yielded = 0
        for k in range(self.n_splits):
            s = n_periods - (self.n_splits - k) * test_size
            train_end = s - guard
            if train_end <= 0:
                continue
            if self.min_train_size is not None and train_end < self.min_train_size:
                continue
            yielded += 1
            train_idx = np.flatnonzero(period < train_end)
            val_idx = np.flatnonzero((period >= s) & (period < s + test_size))
            yield train_idx, val_idx
        # A config that yields NO fold is a misconfiguration, not a silent
        # empty CV: without this, a manual objective's np.mean([]) returns a
        # nan best-value with no signal. Partial pruning (some folds dropped by
        # min_train_size) stays silent — that is the feature.
        if yielded == 0:
            raise ValueError(
                f'no folds could be formed (periods={n_periods}, n_splits={self.n_splits}, '
                f'test_size={test_size}, guard={guard}, '
                f'min_train_size={self.min_train_size}); '
                'lower min_train_size/embargo/label_horizon or add data.')
