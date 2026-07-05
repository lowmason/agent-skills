'''Rank Bayesian model variants from their saved InferenceData.

Sits above bayesian-workflow's per-variant slug folders; defers the ELPD
statistics to bayesian-workflow/references/model-comparison.md. Run --help
for usage.
'''
import argparse
import json
import re
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
    # Note: this 'warning' is deliberately broader than classic Pareto-k —
    # it also fires on ArviZ 1.2.0's 'diag_diff' (similar predictions / N<100),
    # not just 'diag_elpd' (the true Pareto-k analog).
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


def _read_json(folder: Path, name: str):
    p = folder / name
    if p.exists():
        try:
            return json.loads(p.read_text())
        except (ValueError, OSError):
            return None
    return None


def extract_diagnostics(idata, folder: Path) -> dict:
    diag = _read_json(folder, 'diagnostics.json') or {}
    summary = az.summary(idata)
    max_rhat = diag.get('max_rhat')
    if max_rhat is None and 'r_hat' in summary.columns:
        max_rhat = float(summary['r_hat'].max())
    ess_cols = [c for c in summary.columns if c.startswith('ess_')]
    min_ess = diag.get('min_ess')
    if min_ess is None and ess_cols:
        min_ess = float(min(summary[c].min() for c in ess_cols))
    divergences = diag.get('divergences')
    names = [g.split('/')[-1] for g in _group_names(idata)]
    if divergences is None and 'sample_stats' in names:
        ss = idata.sample_stats
        if 'diverging' in ss:
            divergences = int(ss['diverging'].sum())
    check = _read_json(folder, 'check_report.json') or {}
    # PPC column: prefer the interpreted calibration rating from check_report.json
    # (the real predictive-check quality signal — 'excellent'/'fair'/'poor'); fall
    # back to whether a posterior-predictive check was available, then to raw-file
    # presence. bayesian-workflow's check_diagnostics.py writes these keys.
    cal = check.get('calibration') or {}
    pp = check.get('posterior_predictive')
    if cal.get('rating') and cal['rating'] != 'not computed':
        ppc = cal['rating']
    elif pp is not None:
        ppc = 'ran' if pp.get('available') else 'unavailable'
    elif (folder / 'calibration.json').exists():
        ppc = 'ran'
    else:
        ppc = 'unknown'
    # psense column: 'flagged' ONLY when the interpreted report lists flagged
    # params. A clean sensitivity check (low sensitivity, no flags) is 'ok' — the
    # mere presence of psense.json means psense RAN, not that it flagged anything.
    ps = check.get('psense')
    if ps is not None:
        psense = 'flagged' if ps.get('flagged_params') else 'ok'
    elif _read_json(folder, 'psense.json'):
        psense = 'ran'
    else:
        psense = 'unknown'
    return {
        'max_rhat': None if max_rhat is None else float(max_rhat),
        'min_ess': None if min_ess is None else float(min_ess),
        'divergences': divergences,
        'ppc': ppc,
        'psense': psense,
    }


def render_comparison_block(ranking: list[dict]) -> str:
    header = '| id | ELPD | ΔELPD | dSE | weight | max R̂ | div | warn |'
    sep = '|---|---|---|---|---|---|---|---|'
    rows = []
    for r in ranking:
        rhat = '' if r.get('max_rhat') is None else f"{r['max_rhat']:.3f}"
        rows.append(
            f"| {r['id']} | {r['elpd']:.1f} | {r['elpd_diff']:.1f} | "
            f"{r['dse']:.1f} | {r['weight']:.2f} | {rhat} | "
            f"{r.get('divergences', '')} | {'⚠' if r['warning'] else ''} |")
    table = '\n'.join([header, sep, *rows])
    return f'<!-- COMPARISON:BEGIN -->\n{table}\n<!-- COMPARISON:END -->'


_BLOCK_RE = re.compile(r'<!-- COMPARISON:BEGIN -->.*?<!-- COMPARISON:END -->', re.S)


def update_ledger(ledger_path: Path, block: str, best_id: str) -> None:
    text = ledger_path.read_text()
    if _BLOCK_RE.search(text):
        text = _BLOCK_RE.sub(lambda _: block, text)
    else:
        text = text.rstrip() + '\n\n' + block + '\n'
    lines = []
    in_block = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == '<!-- COMPARISON:BEGIN -->':
            in_block = True
        elif stripped == '<!-- COMPARISON:END -->':
            in_block = False
        elif not in_block and line.lstrip().startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if cells and cells[-1] == '**best**':
                cells[-1] = 'candidate'
                line = '| ' + ' | '.join(cells) + ' |'
            if cells and cells[0] == best_id:
                cells[-1] = '**best**'
                line = '| ' + ' | '.join(cells) + ' |'
        lines.append(line)
    ledger_path.write_text('\n'.join(lines) + ('\n' if text.endswith('\n') else ''))


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
    ranking = build_ranking(comparison)
    for entry in ranking:
        folder = next(f for f in variants if f.name == entry['id'])
        entry.update(extract_diagnostics(models[entry['id']], folder))
    return ranking, comparison


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

    try:
        ranking, comparison = compare(args.analysis_dir, args.folders)
    except ValueError as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1
    print(comparison.to_string())
    payload = {'ranking': ranking}
    if args.output:
        args.output.write_text(json.dumps(payload, indent=2))
    if args.ledger:
        block = render_comparison_block(ranking)
        update_ledger(args.ledger, block, ranking[0]['id'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
