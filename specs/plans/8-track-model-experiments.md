# track-model-experiments Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development to implement this plan task-by-task (or executing-plans if subagent dispatch is unavailable). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a standalone `track-model-experiments` skill — a per-analysis `experiments.md` ledger plus a `compare_experiments.py` comparator that ranks Bayesian model variants from their saved InferenceData and stamps the winner back into the ledger.

**Architecture:** The comparator is a thin CLI over ArviZ: it discovers variant slug folders, loads each `inference_data.nc`, guards the two correctness preconditions (every variant has a `log_likelihood` group; all variants share the same observation count), runs `az.compare`, extracts each variant's convergence diagnostics, and idempotently rewrites a marker-delimited block in the ledger. The SKILL.md documents the ledger schema and the comparator, and defers the ELPD statistics to `bayesian-workflow/references/model-comparison.md`.

**Tech Stack:** Python 3.13, NumPyro + JAX, ArviZ 1.x (`arviz` umbrella + `arviz-stats`), NumPy. Tests run under `uv run --python 3.13`. Markdown for the skill and ledger.

## Global Constraints

- **Python style:** single quotes; 4-space indent; target Python 3.13.
- **Bayesian stack:** NumPyro + JAX for models; ArviZ 1.x for analysis. Handle the ArviZ 1.x `elpd` vs classic-0.23 `elpd_loo` column-name difference. Convert JAX→NumPy (`map_over_datasets(lambda ds: ds.as_numpy())`) before any PSIS-LOO op.
- **No external runtime deps** beyond the NumPyro/ArviZ stack `bayesian-workflow` already assumes. No repo-wide `pyproject`; run everything via `uv run --python 3.13 --with …`. Tests use bare imports and are directory-scoped (run pytest from inside `skills/track-model-experiments/scripts/`).
- **Cross-skill references use bare skill names** (`bayesian-workflow`, `track-model-experiments`), never a plugin namespace.
- **Frontmatter description** is trigger-only ("Use when…"), third-person, ≤ 1024 chars, and MUST NOT summarize the workflow (writing-skills SDO doctrine).
- **Provenance:** new original work by Lowell Mason (MIT); `build/check_frontmatter.py` and `build/check_provenance.py` must both pass.
- **No PDFs, no book prose, no bundled external material.**

---

### Task 1: Comparator core + test fixtures (TDD)

Build the comparator's discovery/load/guard/compare path and the shared NumPyro fixtures the whole suite reuses. Deliverable: `compare_experiments.py` ranks a set of variant folders and writes `comparison.json`, erroring on the two correctness preconditions.

**Files:**
- Create: `skills/track-model-experiments/scripts/compare_experiments.py`
- Test: `skills/track-model-experiments/scripts/test_compare_experiments.py`

**Interfaces:**
- Produces (consumed by Task 2 and Task 3):
  - CLI: `python compare_experiments.py --analysis-dir DIR [--folders A B …] [--ledger LEDGER.md] [--output comparison.json]`
  - `discover_variants(analysis_dir: Path) -> list[Path]` — sorted subfolders containing `inference_data.nc`.
  - `load_idata(folder: Path)` — load `.nc`, map to NumPy, return InferenceData.
  - `check_log_likelihood(idata, name: str) -> None` — raise `ValueError` naming the fix if no `log_likelihood` group.
  - `observation_count(idata) -> int` — length of the observed variable.
  - `run_comparison(models: dict[str, object]) -> "pandas.DataFrame"` — `az.compare`, with an `elpd` column normalized across ArviZ versions; index is the variant id, row order is best-first.

- [ ] **Step 1: Write the failing tests**

```python
# skills/track-model-experiments/scripts/test_compare_experiments.py
import json
import subprocess
import sys
from pathlib import Path

import arviz as az
import jax
import numpy as np
import numpyro
import numpyro.distributions as dist
import pytest
from numpyro.infer import MCMC, NUTS

SCRIPT = Path(__file__).parent / 'compare_experiments.py'


def _fit(model, x, y, seed, with_ll=True):
    mcmc = MCMC(NUTS(model), num_warmup=200, num_samples=200, num_chains=2,
                chain_method='sequential', progress_bar=False)
    mcmc.run(jax.random.PRNGKey(seed), x, y)
    idata = az.from_numpyro(mcmc, log_likelihood=with_ll,
                            coords={'obs': np.arange(len(y))},
                            dims={'y_obs': ['obs']})
    return idata.map_over_datasets(lambda ds: ds.as_numpy())


def _full(x, y=None):
    a = numpyro.sample('a', dist.Normal(0, 5))
    b = numpyro.sample('b', dist.Normal(0, 5))
    sigma = numpyro.sample('sigma', dist.HalfNormal(2))
    with numpyro.plate('obs', x.shape[0]):
        numpyro.sample('y_obs', dist.Normal(a + b * x, sigma), obs=y)


def _intercept(x, y=None):
    a = numpyro.sample('a', dist.Normal(0, 5))
    sigma = numpyro.sample('sigma', dist.HalfNormal(2))
    with numpyro.plate('obs', x.shape[0]):
        numpyro.sample('y_obs', dist.Normal(a, sigma), obs=y)


def _make_variant(folder: Path, model, x, y, seed, with_ll=True):
    folder.mkdir(parents=True, exist_ok=True)
    idata = _fit(model, x, y, seed, with_ll=with_ll)
    idata.to_netcdf(str(folder / 'inference_data.nc'))


@pytest.fixture(scope='module')
def data():
    rng = np.random.default_rng(0)
    x = rng.normal(size=200)
    y = 2.0 + 1.5 * x + rng.normal(size=200)   # real slope => full model wins
    return x, y


@pytest.fixture(scope='module')
def analysis_dir(tmp_path_factory, data):
    x, y = data
    d = tmp_path_factory.mktemp('churn')
    _make_variant(d / 'm-full', _full, x, y, seed=1)
    _make_variant(d / 'm-intercept', _intercept, x, y, seed=2)
    return d


def _run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True)


def test_ranks_better_model_on_top(analysis_dir, tmp_path):
    out = tmp_path / 'comparison.json'
    r = _run('--analysis-dir', str(analysis_dir), '--output', str(out))
    assert r.returncode == 0, r.stderr
    ranking = json.loads(out.read_text())['ranking']
    assert ranking[0]['id'] == 'm-full'
    assert ranking[0]['elpd'] >= ranking[1]['elpd']


def test_missing_log_likelihood_errors(data, tmp_path):
    x, y = data
    d = tmp_path / 'a'
    _make_variant(d / 'm-full', _full, x, y, seed=1)
    _make_variant(d / 'm-noll', _full, x, y, seed=3, with_ll=False)
    r = _run('--analysis-dir', str(d))
    assert r.returncode != 0
    assert 'log_likelihood' in (r.stderr + r.stdout)


def test_mismatched_observations_refuses(data, tmp_path):
    x, y = data
    d = tmp_path / 'b'
    _make_variant(d / 'm-full', _full, x, y, seed=1)
    _make_variant(d / 'm-short', _full, x[:150], y[:150], seed=4)
    r = _run('--analysis-dir', str(d))
    assert r.returncode != 0
    assert 'observation' in (r.stderr + r.stdout).lower()


def test_fewer_than_two_variants_message(data, tmp_path):
    x, y = data
    d = tmp_path / 'c'
    _make_variant(d / 'm-full', _full, x, y, seed=1)
    r = _run('--analysis-dir', str(d))
    assert r.returncode != 0
    assert 'at least two' in (r.stderr + r.stdout).lower()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd skills/track-model-experiments/scripts && uv run --python 3.13 --with pytest --with numpyro --with arviz --with arviz-stats --with numpy python -m pytest -q`
Expected: FAIL — `compare_experiments.py` does not exist (collection error / all tests error).

- [ ] **Step 3: Write the comparator core**

```python
# skills/track-model-experiments/scripts/compare_experiments.py
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
            'warning': bool(row.get('warning', False)),
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd skills/track-model-experiments/scripts && uv run --python 3.13 --with pytest --with numpyro --with arviz --with arviz-stats --with numpy python -m pytest -q`
Expected: PASS — 4 tests (ranking, missing-ll error, mismatched-obs refusal, <2 message).

- [ ] **Step 5: Commit**

```bash
git add skills/track-model-experiments/scripts/compare_experiments.py skills/track-model-experiments/scripts/test_compare_experiments.py
git commit -m "feat(track-model-experiments): comparator core + fixtures"
```

---

### Task 2: Diagnostics columns + idempotent ledger update (TDD)

Extend the comparator to (a) extract each variant's convergence diagnostics and PPC/psense flags, surfacing them in `comparison.json`, and (b) when handed a ledger, idempotently rewrite the `<!-- COMPARISON -->` block and set the `best` marker without touching human prose.

**Files:**
- Modify: `skills/track-model-experiments/scripts/compare_experiments.py`
- Modify: `skills/track-model-experiments/scripts/test_compare_experiments.py`

**Interfaces:**
- Consumes: `build_ranking`, `compare`, `load_idata` from Task 1.
- Produces:
  - `extract_diagnostics(idata, folder: Path) -> dict` — `{'max_rhat', 'min_ess', 'divergences', 'ppc', 'psense'}`; reads `diagnostics.json` / `check_report.json` / `calibration.json` / `psense.json` in the folder when present, else computes `max_rhat`/`min_ess`/`divergences` from the idata and marks PPC/psense as unknown.
  - `render_comparison_block(ranking: list[dict]) -> str` — a markdown table between `<!-- COMPARISON:BEGIN -->` and `<!-- COMPARISON:END -->`.
  - `update_ledger(ledger_path: Path, block: str, best_id: str) -> None` — replace the marker-delimited region (idempotent); set `**best**` in the `status` column of `best_id`'s row and clear any previous `**best**`.

- [ ] **Step 1: Write the failing tests (append)**

```python
def test_diagnostics_in_output(analysis_dir, tmp_path):
    out = tmp_path / 'comparison.json'
    r = _run('--analysis-dir', str(analysis_dir), '--output', str(out))
    assert r.returncode == 0, r.stderr
    top = json.loads(out.read_text())['ranking'][0]
    for key in ('max_rhat', 'min_ess', 'divergences'):
        assert key in top
    assert top['max_rhat'] < 1.1   # fixture converges


LEDGER = '''# Experiments — churn

| id (slug) | parent | what changed | hypothesis | ELPD | ΔELPD | max R̂ | div | PPC | psense | status |
|---|---|---|---|---|---|---|---|---|---|---|
| m-full | — | full | slope matters | | | | | | | candidate |
| m-intercept | m-full | drop slope | slope noise | | | | | | | candidate |

<!-- COMPARISON:BEGIN -->
old stale content
<!-- COMPARISON:END -->

## Decision log
- prior human prose that must survive
'''


def test_ledger_update_is_idempotent(analysis_dir, tmp_path):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(LEDGER)
    args = ('--analysis-dir', str(analysis_dir), '--ledger', str(ledger))
    assert _run(*args).returncode == 0
    first = ledger.read_text()
    assert _run(*args).returncode == 0
    second = ledger.read_text()
    assert first == second                       # idempotent
    assert 'prior human prose that must survive' in second
    assert 'old stale content' not in second
    assert '<!-- COMPARISON:BEGIN -->' in second
    # best marker lands on the winning row, only once
    assert second.count('**best**') == 1
    best_row = [ln for ln in second.splitlines() if ln.startswith('| m-full ')][0]
    assert '**best**' in best_row
```

- [ ] **Step 2: Run to verify the new tests fail**

Run: `cd skills/track-model-experiments/scripts && uv run --python 3.13 --with pytest --with numpyro --with arviz --with arviz-stats --with numpy python -m pytest -q -k "diagnostics or ledger"`
Expected: FAIL — `max_rhat` absent from output; `--ledger` is not written.

- [ ] **Step 3: Implement diagnostics extraction + ledger update**

Add to `compare_experiments.py`:

```python
import math
import re

import arviz.stats as azs   # arviz-stats >= 1.0


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
    if divergences is None and 'sample_stats' in [g.split('/')[-1] for g in _group_names(idata)]:
        ss = idata.sample_stats
        if 'diverging' in ss:
            divergences = int(ss['diverging'].sum())
    check = _read_json(folder, 'check_report.json') or {}
    ppc = check.get('ppc') if 'ppc' in check else ('ran' if (folder / 'calibration.json').exists() else 'unknown')
    psense = 'flagged' if (_read_json(folder, 'psense.json')) else 'unknown'
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
    for line in text.splitlines():
        if line.lstrip().startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if cells and cells[-1] == '**best**':
                cells[-1] = 'candidate'
                line = '| ' + ' | '.join(cells) + ' |'
            if cells and cells[0] == best_id:
                cells[-1] = '**best**'
                line = '| ' + ' | '.join(cells) + ' |'
        lines.append(line)
    ledger_path.write_text('\n'.join(lines) + ('\n' if text.endswith('\n') else ''))
```

Wire the diagnostics into `compare()` (merge into each ranking entry) and call the ledger updater from `main()`:

```python
# in compare(): after build_ranking, before return, enrich with diagnostics
    ranking, comparison = build_ranking(comparison), comparison
    for entry in ranking:
        folder = next(f for f in variants if f.name == entry['id'])
        entry.update(extract_diagnostics(models[entry['id']], folder))
    return ranking, comparison
```

```python
# in main(): after computing ranking, before return 0
    if args.ledger:
        block = render_comparison_block(ranking)
        update_ledger(args.ledger, block, ranking[0]['id'])
```

(Adjust `compare()` so it returns the enriched `ranking`; keep `build_ranking` pure so Task 1's tests still pass.)

- [ ] **Step 4: Run the full test file to verify pass**

Run: `cd skills/track-model-experiments/scripts && uv run --python 3.13 --with pytest --with numpyro --with arviz --with arviz-stats --with numpy python -m pytest -q`
Expected: PASS — all 6 tests (4 from Task 1 + diagnostics + idempotent-ledger).

- [ ] **Step 5: Commit**

```bash
git add skills/track-model-experiments/scripts/compare_experiments.py skills/track-model-experiments/scripts/test_compare_experiments.py
git commit -m "feat(track-model-experiments): diagnostics columns + idempotent ledger update"
```

---

### Task 3: SKILL.md — overview, ledger template, stopping rule

Write the skill document. Trigger-only frontmatter; inline ledger template; comparator usage (one invocation + `--help`); stopping rule by pointer to `model-comparison.md`; cross-references by bare name.

**Files:**
- Create: `skills/track-model-experiments/SKILL.md`

**Interfaces:**
- Consumes: the CLI from Tasks 1–2 (`--analysis-dir`, `--ledger`, `--output`).

- [ ] **Step 1: Write SKILL.md**

Frontmatter (trigger-only; no workflow summary):

```yaml
---
name: track-model-experiments
description: >
  Use when iterating over multiple Bayesian/probabilistic model variants and losing
  track of them — trying different priors, likelihoods, distribution parameters, or
  hierarchical structure across churn-logistic → v2 → v3 and unable to reconstruct
  what changed or why one won. Trigger on: comparing many NumPyro/ArviZ model
  versions, "which model fits best", keeping an experiment log or ledger of model
  runs, ranking variants by ELPD/LOO, recording what changed between model versions,
  deciding which variant to ship, or knowing when to stop iterating. Sits above a
  per-variant analysis folder and complements bayesian-workflow's model comparison.
  Not for tuning continuous ML hyperparameters (that is tune-hyperparameters).
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
---
```

Body sections (write in the house voice — lean prose, concrete):
- `# Track Model Experiments`
- `## Overview` — the loop above single-model workflow; you keep a per-analysis ledger and rank variants with a script. Core principle: one file records *what changed and why*; one script records *which won*.
- `## When to use` — bullets with symptoms ("lost track of 12 variants", "can't say why v7 won"); when NOT to use (single model → just bayesian-workflow; ML hyperparameters → tune-hyperparameters).
- `## The ledger (experiments.md)` — the inline template (copy the spec's canonical block: header with the **same-observations** note, the Variants table with human vs script columns labeled, the COMPARISON markers, the Decision log). State D2 (human authors *what changed*/*hypothesis*; the script fills metrics).
- `## The comparator` — the one common invocation; note `--help` for the rest; the three guardrails (missing `log_likelihood`, mismatched observations, high Pareto k) in one line each.
- `## Stopping rule` — `ΔELPD < 2·dSE` → indistinguishable, prefer simpler; conclusions stable across passing models → multiverse view (Gelman et al. 2020, §8). Point to `bayesian-workflow/references/model-comparison.md` for the interpretation thresholds rather than restating them as new doctrine.
- `## Relationship to bayesian-workflow` — this skill owns the *iteration ledger*; `model-comparison.md` owns the *statistics*; `reporting.md` owns the *per-variant slug folder*. Bare names only.

- [ ] **Step 2: Verify frontmatter lint passes and description is trigger-only**

Run: `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`
Expected: exit 0, `track-model-experiments` scanned and clean.
Then manually confirm: description ≤ 1024 chars, starts with "Use when", no workflow summary. `wc -w skills/track-model-experiments/SKILL.md` — keep the body concise (< ~500 words of prose beyond the template).

- [ ] **Step 3: Commit**

```bash
git add skills/track-model-experiments/SKILL.md
git commit -m "docs(track-model-experiments): SKILL.md — ledger template, comparator, stopping rule"
```

---

### Task 4: Wire pointers into bayesian-workflow

Add two one-line pointers so the new skill is discoverable from the workflow that produces its inputs. Pointer-edits only — no attribution change.

**Files:**
- Modify: `skills/bayesian-workflow/SKILL.md` (Step 9 line)
- Modify: `skills/bayesian-workflow/references/reporting.md` ("append a version" note)

**Interfaces:**
- Consumes: the skill name `track-model-experiments` (Task 3).

- [ ] **Step 1: Edit bayesian-workflow Step 9**

In `skills/bayesian-workflow/SKILL.md`, the workflow-overview Step 9 currently reads:
`9. **Compare models** (if applicable) — See [references/model-comparison.md](references/model-comparison.md)`
Append a clause:
`When iterating over many variants, track them with the track-model-experiments skill (ledger + comparator over the slug folders); model-comparison.md remains the statistics.`

- [ ] **Step 2: Edit reporting.md's version note**

In `skills/bayesian-workflow/references/reporting.md`, the "Results folder naming" note says: *"When iterating on the same problem, append a version: `churn-logistic-v2/`."* Append:
`To index those versions and rank them, use the track-model-experiments skill.`

- [ ] **Step 3: Verify links resolve and lints still pass**

Run: `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && uv run --python 3.13 python build/check_provenance.py`
Expected: exit 0 for both. Confirm no `../` link breakage introduced (bare skill-name references only — no new file links).

- [ ] **Step 4: Commit**

```bash
git add skills/bayesian-workflow/SKILL.md skills/bayesian-workflow/references/reporting.md
git commit -m "docs(bayesian-workflow): point Step 9 + reporting.md to track-model-experiments"
```

---

### Task 5: Provenance, install, and full sweep

Register the skill in `NOTICE` and `README`, symlink it into `~/.claude/skills/`, and run the whole test/lint battery green.

**Files:**
- Modify: `NOTICE`
- Modify: `README.md`

**Interfaces:**
- Consumes: the skill directory `skills/track-model-experiments/` (Tasks 1–3).

- [ ] **Step 1: Add to NOTICE**

In `NOTICE`, add `track-model-experiments/` to the "original works by Lowell Mason, MIT licensed" list (the block beginning at `develop-testing-strategy/`), keeping the list's alphabetical-ish grouping.

- [ ] **Step 2: Add to README**

In `README.md`: add a row to the **Mine** table (`| [`track-model-experiments`](skills/track-model-experiments/) | … |` — one dense sentence: a per-analysis ledger + `az.compare` comparator that ranks Bayesian model variants and records what changed and why; the iteration layer above `bayesian-workflow`), and append `track-model-experiments` to the "My original skills" line (~146).

- [ ] **Step 3: Run the provenance + frontmatter lints**

Run:
```bash
uv run --python 3.13 python build/check_provenance.py
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```
Expected: both exit 0 (provenance now matches the NOTICE entry; frontmatter clean).

- [ ] **Step 4: Run the skill's test suite once more (regression)**

Run: `cd skills/track-model-experiments/scripts && uv run --python 3.13 --with pytest --with numpyro --with arviz --with arviz-stats --with numpy python -m pytest -q`
Expected: PASS — all 6 tests.

- [ ] **Step 5: Install the skill (symlink) and confirm it resolves**

```bash
ln -sfn /Users/lowell/Projects/agent-skills/skills/track-model-experiments ~/.claude/skills/track-model-experiments
test -f ~/.claude/skills/track-model-experiments/SKILL.md && echo OK
```
Expected: `OK`.

- [ ] **Step 6: Commit**

```bash
git add NOTICE README.md
git commit -m "docs(track-model-experiments): register in NOTICE + README; install"
```

---

## Verification (whole plan)

After all tasks:

```bash
# Skill test suite (6 tests)
cd skills/track-model-experiments/scripts && \
  uv run --python 3.13 --with pytest --with numpyro --with arviz --with arviz-stats --with numpy python -m pytest -q && cd -

# Lints (both must find the new skill and pass)
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py

# Existing suites unaffected (build tooling)
cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q && cd -

# Install resolves
test -f ~/.claude/skills/track-model-experiments/SKILL.md && echo INSTALL-OK
```

Then run the plan-completion protocol (writing-plans § Plan Completion Protocol): resolve-before-defer gate → markup → deferred items → retire plan 8 (+ spec `track-model-experiments.md`, since no other live plan implements it) to `completed/`. Finish the branch (finishing-a-development-branch): merge / PR / cleanup.

## Self-Review notes

- **Spec coverage:** ledger (Task 3) ✓; comparator core + guards (Task 1) ✓; diagnostics + idempotent ledger write, D4 (Task 2) ✓; stopping rule (Task 3) ✓; wiring (Task 4) ✓; provenance + install (Task 5) ✓; run-the-script testing (Tasks 1–2) ✓; D1 (per-analysis, no global registry) is realized by the ledger living in the analysis dir — no code enforces it, correct. D3 (Bayesian-only, generic core columns) realized by the ledger's `id/parent/what changed/status` columns being metric-agnostic ✓.
- **Type consistency:** `compare()` returns `(ranking, comparison)` in both tasks; `build_ranking` stays pure (Task 1 tests depend on it); diagnostics merged into ranking dicts in Task 2. `_group_names` handles the ArviZ `.groups` method-vs-property difference once.
- **Known risk:** `az.summary` column names (`r_hat`, `ess_bulk`/`ess_tail`) and `az.compare` column names (`elpd`/`elpd_loo`, `dse`, `weight`, `warning`) are version-sensitive; the code guards elpd and reads others with `.get(...)` defaults. If a fixture's ArviZ version names ESS differently, Step-4 diagnostics assertion (`max_rhat < 1.1`) still holds because it only touches `r_hat`. Flag any column-name surprise to the human rather than silently defaulting.
