#!/usr/bin/env python3
# /// script
# requires-python = '>=3.12'
# dependencies = [
#   'arviz>=1.0',
#   'h5netcdf>=1.0',
#   'h5py>=3.0',
# ]
# ///
'''Rank model variants and stamp the result into their experiments ledger.

ELPD mode (--mode elpd, the default) ranks Bayesian fits by PSIS-LOO from each
variant's inference_data.nc and defers the ELPD statistics to
bayesian-workflow/references/model-comparison.md. Score mode (--mode score)
ranks any variants by the per-unit scores in each variant's scores.json (CV
folds or forecast origins); references/predictive-evaluation.md gives the
file's contract. A ledger declares one criterion, and a run in the other mode
is refused. A ledger row the comparator cannot rank is reported, never dropped
in silence. Run --help for usage.
'''
import argparse
import json
import math
import re
import statistics
import sys
from pathlib import Path

import arviz as az

# The status cell of the top-ranked Variants-table row. While a ledger row went
# uncompared, the marker says the ranking covers the compared rows only.
BEST = '**best**'
QUALIFIED_BEST = '**best among ELPD-compared variants**'
SCORE_QUALIFIED_BEST = '**best among score-compared variants**'
MARKERS = (BEST, QUALIFIED_BEST, SCORE_QUALIFIED_BEST)
BLOCK_BEGIN = '<!-- COMPARISON:BEGIN -->'
BLOCK_END = '<!-- COMPARISON:END -->'
MODES = ('elpd', 'score')
# A ledger without a Criterion: line reads as this, so ELPD ledgers need none.
ELPD_CRITERION = 'elpd-loo'
SCORE_FILE = 'scores.json'
ORIENTATIONS = ('higher', 'lower')
# The paired difference needs a spread, so a variant needs two units at least.
MIN_UNITS = 2
# The sample dimensions of a log-likelihood variable; every other dimension is an observation.
SAMPLE_DIMS = ('chain', 'draw')


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


def pointwise_count(idata, name: str) -> int:
    '''How many pointwise terms the variant's one log-likelihood variable holds.

    LOO leaves out one term at a time, so it needs exactly one variable with an
    observation dimension. bayesian-workflow's state-space routes can give
    neither: a summed numpyro.factor stores one term per draw, and a
    multi-source model stores one variable per source. The count comes from the
    log-likelihood, not observed_data: a per-step numpyro.factor, the remedy,
    has an empty observed_data entry.
    '''
    ll = idata.log_likelihood
    ds = ll.to_dataset() if hasattr(ll, 'to_dataset') else ll
    names = list(ds.data_vars)
    if len(names) != 1:
        raise ValueError(
            f'variant {name!r} has {len(names)} log-likelihood variables '
            f'({", ".join(names)}); the comparator ranks one, and ranking a '
            'multi-source model on one source would mislead. Sum the sources\' '
            'terms for each observation into one pointwise variable and drop the '
            'rest. The sources must share one observation dimension, or the sum '
            'builds a grid of terms. A factor that is a penalty or a Jacobian, not '
            'data, leaves the group instead (see '
            'bayesian-workflow/references/state-space.md).')
    var = ds[names[0]]
    obs_dims = [d for d in var.dims if d not in SAMPLE_DIMS]
    count = math.prod(var.sizes[d] for d in obs_dims)
    if not obs_dims or count == 0:
        raise ValueError(
            f'variant {name!r} stores {names[0]!r} with no observation dimension, '
            'so LOO has no pointwise terms to leave out. Store one term per '
            'observation (per time step for a state-space model), not one summed '
            'numpyro.factor (see bayesian-workflow/references/state-space.md).')
    return count


def _elpd_column(comparison):
    # ArviZ 1.x names it 'elpd'; classic 0.23 uses 'elpd_loo'.
    for col in ('elpd', 'elpd_loo'):
        if col in comparison.columns:
            return col
    raise KeyError(f'no elpd column in az.compare output: {list(comparison.columns)}')


def run_comparison(models: dict):
    try:
        comparison = az.compare(models)
    except TypeError as exc:
        cause = f' ({exc.__cause__})' if exc.__cause__ else ''
        raise ValueError(f'az.compare could not rank the variants: {exc}{cause}') from exc
    col = _elpd_column(comparison)
    if col != 'elpd':
        comparison = comparison.rename(columns={col: 'elpd'})
    return comparison


def _diag_str(value) -> str:
    # ArviZ 1.x diag columns are '' when clean; guard against a NaN float
    # (str(np.nan) == 'nan' is truthy and would read as a spurious warning).
    if isinstance(value, float) and math.isnan(value):
        return ''
    return str(value)


def _has_warning(row) -> bool:
    # Classic ArviZ (<=0.23) exposes a boolean 'warning' column directly.
    # ArviZ 1.x replaced it with two string diagnostic columns ('diag_diff',
    # 'diag_elpd') that are empty strings when there is no issue.
    # Note: this 'warning' is deliberately broader than classic Pareto-k —
    # it also fires on ArviZ 1.2.0's 'diag_diff' (similar predictions / N<100),
    # not just 'diag_elpd' (the true Pareto-k analog). comparison.json surfaces
    # the two raw diag strings separately (see build_ranking) for transparency.
    if 'warning' in row.index:
        return bool(row['warning'])
    return (bool(_diag_str(row.get('diag_diff', '')).strip())
            or bool(_diag_str(row.get('diag_elpd', '')).strip()))


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
            'diag_diff': _diag_str(row.get('diag_diff', '')).strip(),
            'diag_elpd': _diag_str(row.get('diag_elpd', '')).strip(),
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


def _convergence_reads(diag: dict) -> tuple:
    '''(max R-hat, min ESS, divergence count) from diagnose_model.py's convergence section.

    Each is None when the section does not carry it: a missing block, a null
    rhat.max (written before diagnose_model.py computed it on clean runs), an ESS
    block without its min, or a divergence block marked checked: false.
    '''
    conv = diag.get('convergence') or {}
    max_rhat = (conv.get('rhat') or {}).get('max')
    ess = [(conv.get(k) or {}).get('min') for k in ('ess_bulk', 'ess_tail')]
    min_ess = None if None in ess else min(ess)
    divergences = (conv.get('divergences') or {}).get('count')
    return max_rhat, min_ess, divergences


def extract_diagnostics(idata, folder: Path) -> dict:
    diag = _read_json(folder, 'diagnostics.json') or {}
    max_rhat, min_ess, divergences = _convergence_reads(diag)
    if max_rhat is None or min_ess is None:
        summary = az.summary(idata)
        if max_rhat is None and 'r_hat' in summary.columns:
            max_rhat = float(summary['r_hat'].max())
        ess_cols = [c for c in summary.columns if c.startswith('ess_')]
        if min_ess is None and ess_cols:
            min_ess = float(min(summary[c].min() for c in ess_cols))
    if divergences is None:
        names = [g.split('/')[-1] for g in _group_names(idata)]
        if 'sample_stats' in names and 'diverging' in idata.sample_stats:
            divergences = int(idata.sample_stats['diverging'].sum())
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


def metric_cells(r: dict) -> dict[str, str]:
    '''One ranked variant's metrics, keyed by the ledger's column names.'''
    return {
        'ELPD': f"{r['elpd']:.1f}",
        'ΔELPD': f"{r['elpd_diff']:.1f}",
        'max R̂': '' if r.get('max_rhat') is None else f"{r['max_rhat']:.3f}",
        'div': '' if r.get('divergences') is None else str(r['divergences']),
        'PPC': r['ppc'],
        'psense': r['psense'],
    }


def score_cells(r: dict) -> dict[str, str]:
    '''One score-ranked variant's metrics, keyed by a score ledger's column names.'''
    return {
        'score': f"{r['score']:.4g}",
        'Δscore': f"{r['score_diff']:.4g}",
        'SE(Δ)': f"{r['se_diff']:.4g}",
    }


def render_comparison_block(ranking: list[dict], not_compared: list[str]) -> str:
    header = '| id | ELPD | ΔELPD | dSE | weight | max R̂ | div | warn |'
    sep = '|---|---|---|---|---|---|---|---|'
    rows = []
    for r in ranking:
        m = metric_cells(r)
        rows.append(
            f"| {r['id']} | {m['ELPD']} | {m['ΔELPD']} | "
            f"{r['dse']:.1f} | {r['weight']:.2f} | {m['max R̂']} | "
            f"{m['div']} | {'⚠' if r['warning'] else ''} |")
    table = '\n'.join([header, sep, *rows])
    if not_compared:
        table += (f'\n\nNot compared: {", ".join(not_compared)}. '
                  'The best marker covers the ELPD-compared variants only.')
    return f'{BLOCK_BEGIN}\n{table}\n{BLOCK_END}'


def render_score_table(ranking: list[dict], criterion: str, orientation: str) -> str:
    rows = []
    for r in ranking:
        m = score_cells(r)
        rows.append(f"| {r['id']} | {m['score']} | {m['Δscore']} | {m['SE(Δ)']} | "
                    f"{r['n_units']} |")
    return '\n'.join([f'Ranked on {criterion} ({orientation} is better).', '',
                      '| id | score | Δscore | SE(Δ) | units |',
                      '|---|---|---|---|---|', *rows])


def render_score_block(ranking: list[dict], not_compared: list[str], criterion: str,
                       orientation: str) -> str:
    table = render_score_table(ranking, criterion, orientation)
    if not_compared:
        table += (f'\n\nNot compared: {", ".join(not_compared)}. '
                  'The best marker covers the score-compared variants only.')
    return f'{BLOCK_BEGIN}\n{table}\n{BLOCK_END}'


_BLOCK_RE = re.compile(f'{re.escape(BLOCK_BEGIN)}.*?{re.escape(BLOCK_END)}', re.S)
_CRITERION_RE = re.compile(r'Criterion:\s*(\S(?:.*\S)?)')


def _cells(line: str) -> list[str]:
    '''The row's cells. A pipe splits cells only when no backslash escapes it.

    Exactly one outer pipe comes off each end, so an empty first cell and an
    escaped pipe that ends the last cell survive.
    '''
    row = line.strip()
    if row.startswith('|'):
        row = row[1:]
    if row.endswith('|') and not row.endswith('\\|'):
        row = row[:-1]
    return [c.strip() for c in re.split(r'(?<!\\)\|', row)]


def _variants_table(lines: list[str]) -> tuple[int, list[str], list[int]] | None:
    '''The Variants table's header line number, header cells and data-row line numbers.

    It is the first table outside the COMPARISON block whose header starts with
    an id column and has a status column; None when the ledger has none.
    '''
    in_block = False
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped == BLOCK_BEGIN:
            in_block = True
        elif stripped == BLOCK_END:
            in_block = False
        elif not in_block and stripped.startswith('|'):
            start = i
            while i < len(lines) and lines[i].strip().startswith('|'):
                i += 1
            names = [c.lower() for c in _cells(lines[start])]
            if names[0].startswith('id') and 'status' in names:
                return start, _cells(lines[start]), list(range(start + 2, i))
            continue
        i += 1
    return None


def ledger_ids(text: str) -> list[str] | None:
    '''The ids of the ledger's Variants-table rows in table order; None without the table.'''
    lines = text.splitlines()
    table = _variants_table(lines)
    if table is None:
        return None
    return [_cells(lines[i])[0] for i in table[2]]


def ledger_criterion(text: str) -> str:
    '''The criterion the ledger declares above its Variants table; elpd-loo without one.

    Only a line outside the COMPARISON block and above the table counts, so a
    Criterion: line in the Decision log or in the block never sets the mode.
    Without a table, the scan stops at the first level-2 heading.
    '''
    lines = text.splitlines()
    table = _variants_table(lines)
    if table:
        end = table[0]
    else:
        end = next((i for i, ln in enumerate(lines) if ln.startswith('## ')), len(lines))
    in_block = False
    for line in lines[:end]:
        stripped = line.strip()
        if stripped == BLOCK_BEGIN:
            in_block = True
        elif stripped == BLOCK_END:
            in_block = False
        elif not in_block and (m := _CRITERION_RE.fullmatch(stripped)):
            return m.group(1)
    return ELPD_CRITERION


def ledger_problem(ledger_path: Path) -> str | None:
    '''Why the comparator cannot update this ledger safely; None when it can.'''
    if not ledger_path.is_file():
        return f'no ledger file at {ledger_path}; check the --ledger path.'
    text = ledger_path.read_text()
    begins, ends = text.count(BLOCK_BEGIN), text.count(BLOCK_END)
    if (begins, ends) == (0, 0):
        return None
    if (begins, ends) != (1, 1) or text.index(BLOCK_BEGIN) > text.index(BLOCK_END):
        return (f'{ledger_path} holds {begins} {BLOCK_BEGIN} and {ends} {BLOCK_END} '
                'markers. The comparator rewrites the text from a BEGIN marker to the '
                'next END marker, so an unpaired or repeated marker would overwrite the '
                "ledger's prose. Leave one pair of markers, or none, and rerun.")
    return None


def mode_problem(mode: str, criterion: str, ledger_path: Path) -> str | None:
    '''Why --mode cannot fill a ledger on this criterion; None when it can.'''
    wanted = 'elpd' if criterion == ELPD_CRITERION else 'score'
    if mode == wanted:
        return None
    return (f'{ledger_path} reads as Criterion: {criterion} (a ledger without a '
            f'Criterion: line reads as {ELPD_CRITERION}), which --mode {mode} cannot '
            f'rank. Run --mode {wanted}, or re-declare the ledger\'s criterion: a '
            'ledger holds one criterion.')


def _wide_row_note(cells: list[str], width: int, top_id: str) -> str:
    note = (f'note: ledger row {cells[0]} has {len(cells)} cells against {width} in the '
            'header, so its cells do not line up with the header and the row was left '
            'unchanged. Escape a literal pipe in a cell as \\|.')
    is_top = cells[0] == top_id
    has_marker = any(c in MARKERS for c in cells)
    if is_top and has_marker:
        note += (' It is the top-ranked variant and keeps its best marker, but its '
                 'metric cells were not updated.')
    elif is_top:
        note += ' It is the top-ranked variant, so no row carries the best marker.'
    elif has_marker:
        note += ' It still holds a best marker, so the ledger can show two.'
    return note


def update_ledger(ledger_path: Path, block: str, ranking: list[dict],
                  not_compared: list[str], mode: str = 'elpd') -> None:
    '''Rewrite the COMPARISON block, fill the metric cells and move the best marker.

    Only the COMPARISON block (replaced, or appended if absent) and the Variants
    table's metric and status cells change; human prose and the table's left
    half are preserved. Each ranked row is re-joined with '| '/' |' spacing, so
    its cell padding is normalized — this is intentional. An unranked row keeps
    its cells, except that a stale best marker returns to candidate. A row with
    more cells than the header does not line up with it, so it is left as it is
    and a note names it. Notes also name ranked variants that have no row, and a
    table with none of the mode's metric columns.
    '''
    text = ledger_path.read_text()
    if _BLOCK_RE.search(text):
        text = _BLOCK_RE.sub(lambda _: block, text)
    else:
        text = text.rstrip() + '\n\n' + block + '\n'
    lines = text.splitlines()
    table = _variants_table(lines)
    if table is not None:
        _, header, rows = table
        status = [c.lower() for c in header].index('status')
        ranked = {r['id']: r for r in ranking}
        top_id = ranking[0]['id']
        cells_of = score_cells if mode == 'score' else metric_cells
        qualified = SCORE_QUALIFIED_BEST if mode == 'score' else QUALIFIED_BEST
        marker = qualified if not_compared else BEST
        columns = list(cells_of(ranking[0]))
        if not set(columns) & set(header):
            print(f'note: the Variants table has none of the metric columns '
                  f'{", ".join(columns)}. Names match exactly, case and symbols '
                  'included, so no metric cell was written.', file=sys.stderr)
        table_ids = set()
        for i in rows:
            cells = _cells(lines[i])
            table_ids.add(cells[0])
            if len(cells) > len(header):
                print(_wide_row_note(cells, len(header), top_id), file=sys.stderr)
                continue
            cells += [''] * (len(header) - len(cells))
            entry = ranked.get(cells[0])
            if entry is None and cells[status] not in MARKERS:
                continue
            if cells[status] in MARKERS:
                cells[status] = 'candidate'
            if entry is not None:
                for column, value in cells_of(entry).items():
                    if column in header:
                        cells[header.index(column)] = value
                if entry['id'] == top_id:
                    cells[status] = marker
            lines[i] = '| ' + ' | '.join(cells) + ' |'
        missing = [r['id'] for r in ranking if r['id'] not in table_ids]
        if missing:
            consequence = (' The top-ranked variant is among them, so no row carries '
                           'the best marker.' if top_id in missing else '')
            print(f'note: ranked variants with no Variants-table row: '
                  f'{", ".join(missing)}. Add a row for each to record it.{consequence}',
                  file=sys.stderr)
    ledger_path.write_text('\n'.join(lines) + ('\n' if text.endswith('\n') else ''))


def compare(analysis_dir: Path, folders: list[Path] | None):
    variants = folders or discover_variants(analysis_dir)
    missing = [f.name for f in variants if not (f / 'inference_data.nc').is_file()]
    if missing:
        raise ValueError(
            f'no inference_data.nc in {", ".join(missing)}; ELPD mode ranks Bayesian '
            'fits only. To rank a non-Bayesian variant, give every variant a '
            'scores.json on one criterion and run --mode score against a score '
            'ledger; do not park the variant in the Decision log.')
    if len(variants) < 2:
        raise ValueError('need at least two variants to compare '
                         f'(found {len(variants)} in {analysis_dir}).')
    models, counts = {}, {}
    for folder in variants:
        name = folder.name
        idata = load_idata(folder)
        check_log_likelihood(idata, name)
        models[name] = idata
        counts[name] = pointwise_count(idata, name)
    distinct = set(counts.values())
    if len(distinct) > 1:
        raise ValueError(
            'variants were fit to different numbers of observations '
            f'{counts}; LOO compares predictions of the SAME observations, '
            'so this comparison is invalid.')
    comparison = run_comparison(models)
    ranking = build_ranking(comparison)
    for entry in ranking:
        folder = next(f for f in variants if f.name == entry['id'])
        entry.update(extract_diagnostics(models[entry['id']], folder))
    return ranking, comparison


def discover_score_variants(analysis_dir: Path) -> list[Path]:
    return sorted(p.parent for p in analysis_dir.glob(f'*/{SCORE_FILE}'))


def load_scores(folder: Path) -> dict:
    '''A variant's scores.json, checked against the contract in references/predictive-evaluation.md.'''
    name, path = folder.name, folder / SCORE_FILE
    if not path.is_file():
        raise ValueError(
            f'no {SCORE_FILE} in {name}; score mode ranks each variant from it. Write '
            '{"criterion": ..., "orientation": "higher" or "lower", "units": {unit: score}} '
            'from its CV folds or forecast origins (references/predictive-evaluation.md).')
    try:
        data = json.loads(path.read_text())
    except ValueError as exc:
        raise ValueError(f'{name}/{SCORE_FILE} is not valid JSON: {exc}') from exc
    if not isinstance(data, dict):
        raise ValueError(f'{name}/{SCORE_FILE} must hold a JSON object.')
    criterion, orientation, units = (data.get(k) for k in ('criterion', 'orientation', 'units'))
    if not isinstance(criterion, str) or not criterion.strip():
        raise ValueError(f'{name}/{SCORE_FILE} has no criterion string; name the score '
                         'and its protocol, for example cv-mse or lfo-elpd.')
    if orientation not in ORIENTATIONS:
        raise ValueError(f'{name}/{SCORE_FILE} has orientation {orientation!r}; write '
                         '"higher" or "lower", whichever is better for this score.')
    if not isinstance(units, dict):
        raise ValueError(f'{name}/{SCORE_FILE} has no units object; map each fold or '
                         'forecast origin to its score.')
    bad = sorted(str(k) for k, v in units.items()
                 if isinstance(v, bool) or not isinstance(v, int | float)
                 or not math.isfinite(v))
    if bad:
        raise ValueError(f'variant {name!r} has a non-finite or non-numeric score for '
                         f'units {", ".join(bad)}; every unit needs one finite number. '
                         'Fix or rerun those units.')
    if len(units) < MIN_UNITS:
        raise ValueError(f'variant {name!r} has {len(units)} unit(s); the paired '
                         f'difference needs at least {MIN_UNITS} folds or forecast origins.')
    return {'criterion': criterion, 'orientation': orientation,
            'units': {str(k): float(v) for k, v in units.items()}}


def compare_scores(analysis_dir: Path, folders: list[Path] | None,
                   declared: str | None = None) -> tuple[list[dict], str, str]:
    '''Rank variants by mean score, with each one's paired difference from the top.

    `declared` is the ledger's criterion, when a ledger is given. Returns the
    ranking, the criterion and the orientation. A variant's
    score_diff is the mean over units of its score minus the top variant's, and
    se_diff is that difference's sample standard deviation over the square root
    of the number of units.
    '''
    variants = folders or discover_score_variants(analysis_dir)
    scores = {f.name: load_scores(f) for f in variants}
    if len(scores) < 2:
        raise ValueError('need at least two variants to compare '
                         f'(found {len(scores)} {SCORE_FILE} in {analysis_dir}).')
    criterion = declared or next(iter(scores.values()))['criterion']
    source = 'the ledger\'s Criterion: line' if declared else 'the first variant'
    wrong = {n: s['criterion'] for n, s in scores.items() if s['criterion'] != criterion}
    if wrong:
        raise ValueError(f'criterion {criterion!r} (from {source}) differs in {wrong}; '
                         'a ledger ranks one criterion. Rescore those variants on '
                         f'{criterion!r}, or start a ledger for the other criterion.')
    orientations = {n: s['orientation'] for n, s in scores.items()}
    if len(set(orientations.values())) > 1:
        raise ValueError(f'orientation differs across variants {orientations}; one '
                         'criterion has one orientation. Fix the files that are wrong.')
    names = list(scores)
    keys = set(scores[names[0]]['units'])
    for n in names[1:]:
        other = set(scores[n]['units'])
        if other != keys:
            raise ValueError(
                f'variant {n!r} has different units from {names[0]!r} (only in {n}: '
                f'{sorted(other - keys)}; only in {names[0]}: {sorted(keys - other)}). '
                'Score every variant on the same folds or forecast origins.')
    orientation = orientations[names[0]]
    means = {n: statistics.fmean(s['units'].values()) for n, s in scores.items()}
    order = sorted(names, key=means.__getitem__, reverse=orientation == 'higher')
    top = scores[order[0]]['units']
    ranking = []
    for n in order:
        d = [scores[n]['units'][u] - top[u] for u in sorted(keys)]
        ranking.append({
            'id': n,
            'score': means[n],
            'score_diff': statistics.fmean(d),
            'se_diff': statistics.stdev(d) / math.sqrt(len(d)),
            'n_units': len(d),
        })
    return ranking, criterion, orientation


def _not_compared_note(not_compared: list[str], mode: str) -> str:
    if mode == 'score':
        remedy = ('give each a scores.json on the ledger\'s criterion to rank it.')
        compared = 'score-compared'
    else:
        remedy = ('a variant with no inference_data.nc ranks only in a score ledger '
                  '(--mode score), where every variant writes scores.json.')
        compared = 'ELPD-compared'
    return (f'note: ledger rows not compared: {", ".join(not_compared)}. The ranking and '
            f'the best marker cover the {compared} variants only; {remedy}')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--analysis-dir', type=Path, required=True,
                    help='directory containing the variant slug folders')
    ap.add_argument('--folders', type=Path, nargs='*', default=None,
                    help='explicit variant folders (overrides discovery)')
    ap.add_argument('--mode', choices=MODES, default='elpd',
                    help='elpd: rank Bayesian fits by PSIS-LOO from inference_data.nc; '
                         'score: rank any variants from scores.json (default: elpd)')
    ap.add_argument('--ledger', type=Path, default=None,
                    help='experiments.md to update (COMPARISON block, metric cells, best marker)')
    ap.add_argument('--output', type=Path, default=None,
                    help='write comparison.json here')
    args = ap.parse_args(argv)

    criterion = ELPD_CRITERION
    if args.ledger:
        problem = ledger_problem(args.ledger)
        if problem is None:
            criterion = ledger_criterion(args.ledger.read_text())
            problem = mode_problem(args.mode, criterion, args.ledger)
        if problem:
            print(f'error: {problem}', file=sys.stderr)
            return 1
    try:
        if args.mode == 'score':
            ranking, criterion, orientation = compare_scores(
                args.analysis_dir, args.folders, criterion if args.ledger else None)
            print(render_score_table(ranking, criterion, orientation))
        else:
            ranking, comparison = compare(args.analysis_dir, args.folders)
            print(comparison.to_string())
    except ValueError as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1
    not_compared = []
    if args.ledger:
        ids = ledger_ids(args.ledger.read_text())
        if ids is None:
            print(f'note: {args.ledger} has no Variants table (a header that starts '
                  'with id and has a status column), so no metric cell or best '
                  'marker was written.', file=sys.stderr)
        ranked = {r['id'] for r in ranking}
        not_compared = [i for i in ids or [] if i not in ranked]
        if not_compared:
            print(_not_compared_note(not_compared, args.mode), file=sys.stderr)
    payload = {'mode': args.mode, 'criterion': criterion, 'ranking': ranking,
               'not_compared': not_compared}
    if args.output:
        args.output.write_text(json.dumps(payload, indent=2))
    if args.ledger:
        if args.mode == 'score':
            block = render_score_block(ranking, not_compared, criterion, orientation)
        else:
            block = render_comparison_block(ranking, not_compared)
        update_ledger(args.ledger, block, ranking, not_compared, args.mode)
    return 0


if __name__ == '__main__':
    sys.exit(main())
