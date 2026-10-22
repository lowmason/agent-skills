# Predictive evaluation

The protocol behind score mode: how to produce per-unit scores worth ranking, the file
the comparator reads, and how far to trust the difference it reports.

## Contents
- When this file applies
- The backtest protocol
- The `scores.json` contract
- Writing `scores.json`
- The paired difference and its limits
- Benchmark comparison
- Proper scoring rules

## When this file applies

A score ledger ranks variants on one shared criterion from per-unit scores. A unit is
one fold of a cross-validation run, or one forecast origin of a backtest. Any model class
can join: a tabular regression, a boosting model, a statsmodels forecaster, or a Bayesian
fit that writes its own scores. ELPD mode (PSIS-LOO from `inference_data.nc`) does not use
this file. Its statistics live in `bayesian-workflow`'s `model-comparison.md`.

## The backtest protocol

For a forecast decision, evaluate the way the model will be used:

1. Choose the forecast origins: every period from a minimum training length up to the
   last period that still has `h` periods after it.
2. At each origin, refit on the data up to that origin and on nothing after it. State
   whether the window expands or rolls.
3. Forecast at a stated horizon `h`, or over steps 1 to `h` with a joint score.
4. Score the forecast against what happened, and record one score per origin.

Every feature must be as-of its origin. A revised series or a vintage store needs the
as-of checks in develop-testing-strategy. This file covers the scoring, not the leakage
audit. For a cross-validation that is not temporal, the unit is the fold. Choosing the
splitter for the data's dependence structure is tune-hyperparameters' job.

## The `scores.json` contract

Each variant folder holds one `scores.json`:

```json
{"criterion": "cv-mse", "orientation": "lower", "units": {"fold-1": 0.42, "fold-2": 0.39}}
```

- `criterion`: a free string that names the score and the protocol, for example `cv-mse`,
  `cv-logloss`, `lfo-elpd-h1` or `backtest-crps-h3`. Every variant in a ledger writes the
  same string, and it matches the ledger's `Criterion:` line.
  Do not name a score criterion `elpd-loo`. That name is reserved for ELPD mode, and a
  ledger that declares it, or declares no criterion, always runs in ELPD mode.
- `orientation`: `higher` or `lower`, whichever is better for this score.
- `units`: a map from each fold id or forecast origin to one finite number. Every variant
  uses the same keys.

The comparator refuses a variant folder with no `scores.json`, a criterion that differs
from the ledger's or from another variant's, mixed orientations, unit keys that differ
across variants, a non-finite value, and fewer than two units.

## Writing `scores.json`

One helper serves every producer:

```python
import json
from pathlib import Path


def write_scores(folder, criterion, orientation, units):
    '''Write a variant's scores.json in the shape the comparator reads.'''
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    payload = {'criterion': criterion, 'orientation': orientation,
               'units': {str(k): float(v) for k, v in units.items()}}
    (folder / 'scores.json').write_text(json.dumps(payload, indent=2))
```

From a cross-validation loop. Build the splitter once, with a fixed seed where it takes
one, and pass the same splitter and data to every variant, so that the folds match:

```python
import numpy as np
from sklearn.linear_model import Ridge

units = {}
for k, (train, test) in enumerate(splitter.split(X, y, groups), start=1):
    fit = Ridge(alpha=1.0).fit(X[train], y[train])
    units[f'fold-{k}'] = float(np.mean((fit.predict(X[test]) - y[test]) ** 2))
write_scores('ridge-lags', 'cv-mse', 'lower', units)
```

From a Bayesian leave-future-out run. bayesian-workflow's
`references/model-comparison.md` (section "Time-series and forecast comparison") builds
`lfo` with `azs.lfo_cv(..., pointwise=True)`, and its blocked K-fold route builds one joint
score per block in the same way:

```python
units = {f'origin-{t}': v for t, v in zip(lfo.elpd_i['time'].values, lfo.elpd_i.values)}
write_scores('ar1', 'lfo-elpd-h1', 'higher', units)
```

To put a Bayesian variant on a ledger whose criterion is a point loss, score its
posterior-predictive mean on the same folds, for example the per-fold MSE.

## The paired difference and its limits

For each variant, the comparator reports the paired difference from the top variant:

- `d_u` is the variant's score on unit `u` minus the top variant's score on the same unit.
- Δscore is the mean of `d` over the `K` units.
- SE(Δ) is `sd(d) / √K`, with the sample standard deviation.

The screening rule: when |Δscore| is under 2·SE(Δ), treat the difference as noise and ship
the simpler variant. It is a screen, not a test. The plain SE is too small in each of these
cases:

- **Overlapping training sets.** Folds and rolling origins share most of their training
  data, so the per-unit differences are correlated. No unbiased estimator of the variance
  of a K-fold cross-validation estimate exists (Bengio & Grandvalet 2004), so treat the SE
  as optimistic.
- **Few units.** With 5 folds, `sd(d)` itself rests on 4 degrees of freedom, so 2·SE is
  rough. Before a close call, add units: repeat the cross-validation with new seeds, or
  add forecast origins.
- **Forecasts `h` steps ahead.** Forecasts from neighbouring origins share `h − 1` periods,
  so `d` is autocorrelated up to lag `h − 1`. Use a Diebold–Mariano test: the mean of `d`
  over an autocorrelation-robust (HAC) standard error (Diebold & Mariano 1995). At `h = 1`
  with no serial correlation it equals the plain rule. With few origins, the normal
  reference is too liberal.

```python
import numpy as np


def dm_statistic(d, h):
    '''Diebold–Mariano statistic for per-origin loss differences d at horizon h.

    The variance of the mean uses a Newey–West (Bartlett) sum over lags 1 to h - 1,
    since forecasts h steps ahead from neighbouring origins share h - 1 periods.
    '''
    d = np.asarray(d, dtype=float)
    k = d.size
    dc = d - d.mean()
    var = dc @ dc / k
    for lag in range(1, h):
        var += 2 * (1 - lag / h) * (dc[lag:] @ dc[:-lag]) / k
    return d.mean() / np.sqrt(var / k)
```

Apply the correction that fits on any high-stakes call, such as a forecast that replaces a
published one, and say in the ledger's Decision log which correction you applied.

## Benchmark comparison

Every backtest ledger carries a naive baseline as a variant row: the last value carried
forward, or the seasonal naive forecast (the value one season back). It writes its own
`scores.json` on the same origins. Report each variant's skill against it:

- For a loss (lower is better): skill = 1 − mean loss(variant) / mean loss(baseline).
  Positive means better than the baseline.
- For a log score (higher is better): report the difference from the baseline's score.

A variant that does not beat the naive baseline by more than the noise rule allows is no
forecasting gain, however well it ranks against the other variants.

## Proper scoring rules

A scoring rule is proper when a forecaster gets its best expected score by reporting its
true predictive distribution. It is strictly proper when that best score is unique
(Gneiting & Raftery 2007). Rank predictive distributions on a strictly proper score:

- **Log score.** The log predictive density of the realized value. It is the score behind
  `lfo-elpd` and the joint block score. It weighs the tails heavily.
- **CRPS** (continuous ranked probability score). It compares the whole predictive
  distribution with the realized value, in the units of the data. Lower is better.

```python
import numpy as np


def crps_from_draws(draws, y):
    '''CRPS of one realized value y under a predictive sample; lower is better.'''
    draws = np.asarray(draws, dtype=float)
    spread = np.abs(draws[:, None] - draws[None, :]).mean()
    return np.abs(draws - y).mean() - 0.5 * spread
```

Point losses score a point forecast only: MSE targets the mean, MAE the median. For class
probabilities, use log-loss or the Brier score. Accuracy alone is not proper.
