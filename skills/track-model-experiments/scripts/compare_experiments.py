'''Rank Bayesian model variants from their saved InferenceData.

Sits above bayesian-workflow's per-variant slug folders; defers the ELPD
statistics to bayesian-workflow/references/model-comparison.md. Run --help
for usage.
'''
import argparse
import json
import sys
from pathlib import Path

import arviz as az


def discover_variants(analysis_dir: Path) -> list[Path]:
    return sorted(p.parent for p in analysis_dir.glob('*/inference_data.nc'))


def load_idata(folder: Path):
    idata = az.from_netcdf(str(folder / 'inference_data.nc'))
    # PSIS-LOO does in-place updates that JAX arrays reject; reloading from
    # netCDF already yields NumPy, but map defensively for in-session idata.
    if hasattr(idata, 'map_over_datasets'):
        idata = idata.map_over_datasets(lambda ds: ds.as_numpy())
    return idata


def _group_names(idata):
    groups = idata.groups
    return groups() if callable(groups) else groups


def check_log_likelihood(idata, name: str) -> None:
    names = [g.split('/')[-1] for g in _group_names(idata)]
    if 'log_likelihood' not in names:
        raise ValueError(
            f'variant {name!r} has no log_likelihood group; LOO needs it. '
            f'Refit with az.from_numpyro(..., log_likelihood=True) '
            f'(see bayesian-workflow/references/model-comparison.md).')


def observation_count(idata) -> int:
    obs = idata.observed_data
    ds = obs.to_dataset() if hasattr(obs, 'to_dataset') else obs
    var = next(iter(ds.data_vars.values()))
    return int(var.size)


def _elpd_column(comparison):
    # ArviZ 1.x names it 'elpd'; classic 0.23 uses 'elpd_loo'.
    for col in ('elpd', 'elpd_loo'):
        if col in comparison.columns:
            return col
    raise KeyError(f'no elpd column in az.compare output: {list(comparison.columns)}')


def run_comparison(models: dict):
    comparison = az.compare(models)
    col = _elpd_column(comparison)
    if col != 'elpd':
        comparison = comparison.rename(columns={col: 'elpd'})
    return comparison


def _has_warning(row) -> bool:
    # Classic ArviZ (<=0.23) exposes a boolean 'warning' column directly.
    # ArviZ 1.x replaced it with two string diagnostic columns ('diag_diff',
    # 'diag_elpd') that are empty strings when there is no issue.
    if 'warning' in row.index:
        return bool(row['warning'])
    diag_diff = row.get('diag_diff', '') or ''
    diag_elpd = row.get('diag_elpd', '') or ''
    return bool(str(diag_diff).strip()) or bool(str(diag_elpd).strip())


def build_ranking(comparison) -> list[dict]:
    ranking = []
    for variant_id, row in comparison.iterrows():
        ranking.append({
            'id': str(variant_id),
            'elpd': float(row['elpd']),
            'se': float(row.get('se', float('nan'))),
            'elpd_diff': float(row.get('elpd_diff', 0.0)),
            'dse': float(row.get('dse', 0.0)),
            'weight': float(row.get('weight', float('nan'))),
            'warning': _has_warning(row),
        })
    return ranking


def compare(analysis_dir: Path, folders: list[Path] | None):
    variants = folders or discover_variants(analysis_dir)
    if len(variants) < 2:
        raise SystemExit('need at least two variants to compare '
                         f'(found {len(variants)} in {analysis_dir}).')
    models, counts = {}, {}
    for folder in variants:
        name = folder.name
        idata = load_idata(folder)
        check_log_likelihood(idata, name)
        models[name] = idata
        counts[name] = observation_count(idata)
    distinct = set(counts.values())
    if len(distinct) > 1:
        raise SystemExit(
            'variants were fit to different numbers of observations '
            f'{counts}; LOO compares predictions of the SAME observations, '
            'so this comparison is invalid.')
    comparison = run_comparison(models)
    return build_ranking(comparison), comparison


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--analysis-dir', type=Path, required=True,
                    help='directory containing the variant slug folders')
    ap.add_argument('--folders', type=Path, nargs='*', default=None,
                    help='explicit variant folders (overrides discovery)')
    ap.add_argument('--ledger', type=Path, default=None,
                    help='experiments.md to update (COMPARISON block + best marker)')
    ap.add_argument('--output', type=Path, default=None,
                    help='write comparison.json here')
    args = ap.parse_args(argv)

    ranking, comparison = compare(args.analysis_dir, args.folders)
    print(comparison.to_string())
    payload = {'ranking': ranking}
    if args.output:
        args.output.write_text(json.dumps(payload, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
