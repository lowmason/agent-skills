# Model-lifecycle Stage 1: track score mode and predictive evaluation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

> Roadmap: specs/model-lifecycle-roadmap.md, Stage 1 — on plan completion, tick the stage and re-validate later stages against what shipped.

**Goal:** `track-model-experiments` ranks score-criterion variants from `scores.json` beside the unchanged ELPD mode, with a predictive-evaluation reference, a time-series section in bayesian-workflow, and a micro-tested description.

**Architecture:** `compare_experiments.py` gains `--mode score`. Score mode loads one `scores.json` per variant folder, ranks variants by mean score, and reports each variant's paired difference from the top variant with its standard error. The ledger declares one criterion on a `Criterion:` line, and a run in the other mode is refused. The comparator is hardened first (plan 59's leftovers), with ELPD behaviour proven unchanged against the base-commit tests. New docs: track's `references/predictive-evaluation.md`, and a time-series section in bayesian-workflow's `model-comparison.md` whose LFO and blocked K-fold snippets run under snippet Tier 3 through a new named fixture.

**Tech Stack:** Python 3.13 via `uv`, pytest, ArviZ 1.3.0 / arviz-stats 1.3.3 / NumPyro 0.22.0 / JAX 0.12.0 (snippet pins), `claude -p` 2.1.304 for the V1 micro-test.

**Spec:** `specs/model-lifecycle.md` — § Stage B (R13–R24), § Verification V1 (track arm) and V3 (Stage B), § Coordination, § Provenance and public-repo rules. Also the deferred item "Harden `skills/track-model-experiments/scripts/compare_experiments.py` after plan 59's final review", parts (a)–(f), and part (a) of "Two doc nits left by plan 59's final review", both in `specs/deferred_items.md` section `59-model-skill-comparator-and-cv-fixes`.

**Base commit:** `7603e69` (origin/main when this plan was written). Every "existing test" below means the test file at that commit.

## Global Constraints

- Python style: single quotes, f-strings, 4-space indent, Python 3.13 through `uv run --python 3.13`. The comparator's existing idiom `f"{r['elpd']:.1f}"` (a double-quoted f-string around single-quoted keys) stays where the surrounding code uses it.
- **R18.** "ELPD mode keeps its behaviour, refusals and output. Every existing test in `test_compare_experiments.py` passes without edits." Applied through D1: the base-commit test file runs unedited against the final comparator (Task 6, Step 1).
- **R13 contract**, exactly: `{"criterion": "cv-mse", "orientation": "lower", "units": {"fold-1": 0.42, "fold-2": 0.39}}`. `criterion` is a free string, `orientation` is `higher` or `lower`, `units` maps a fold id or forecast origin to one finite number.
- **R15.** `experiments.md` carries one `Criterion: <name>` line above the Variants table. A ledger without that line reads as `elpd-loo`. A score ledger's metric columns are `score`, `Δscore` and `SE(Δ)`.
- **R16.** `--mode {elpd,score}`, default `elpd`. `comparison.json` gains `mode` and `criterion` keys.
- **Paired Δ** (spec § Terms): the mean over units of the per-unit score difference. `SE(Δ) = sd(d) / √K`, with `sd` the sample standard deviation (ddof = 1), `d` the per-unit differences, `K` the number of units.
- **R24.** The score-mode tests use no NetCDF fixtures.
- **R14 sources** (Gneiting & Raftery 2007; Diebold & Mariano 1995; Bengio & Grandvalet 2004) are cited by idea only, with no prose copied.
- **R19** is original text that cites the loo LFO vignette and the CV-FAQ by URL. Its snippets use arviz-stats and pass snippet Tiers 1–3 against the pins in `build/snippet_preamble.py` (`PINNED`).
- **R20.** track's `description`: third person, at most 1,024 characters, starts "Use when". It ships only after the V1 track arm passes.
- **Public repo.** `specs/` is public. Examples use generic nowcast and panel names, with no private-repo detail.
- **Leave alone in this plan:** every file under `skills/tune-hyperparameters/` (Stage 2), the Stage C files (`develop-testing-strategy`, `validate-data`, `recommend-visualization`, rpm's `references/reporting.md`), and `time_series_cv.py`. The deferred item "Three nits in the splitter's tests" is out of scope.
- **Plan 64 coordination** (`specs/plans/64-bayesian-rpm-routing.md`, merged to main as a plan, not yet executed). It also edits four places this plan edits: `build/snippet_preamble.py`'s coverage docstring, NOTICE's bayesian-workflow paragraph, `build/test_runtime_support.py`'s `SOFT_REFERENCES`, and bayesian-workflow's `SKILL.md` (this plan does not touch that file). This plan anchors each edit by content, never by line number. Whichever plan executes second re-reads those places after syncing with main, and re-measures the coverage counts.
- Every commit passes `build/run_commit_lints.sh`. The pre-commit hook (`core.hooksPath` is set to `build/githooks`) runs it. If a commit is refused, fix the cause. Never pass `--no-verify`.
- Commit messages end with the executing session's attribution trailer.

## Decisions

- **D1** (owner, planning session, 2026-10-21): deferred item part (f) against the roadmap Exit's "every existing test unedited": prove, then tidy. The existing tests stay unedited until Task 6. Task 6 first runs the base-commit test file (`7603e69`) unedited against the final comparator and records the result. That run is how the Exit line is met. Then it makes the (f) edits to existing helpers and tests. Applied in: Global Constraints (R18), Task 6.
- **D2** (owner, planning session, 2026-10-21): hardening part (b), "make the note say so, or pick a rule": the note says so. A row with more cells than the header stays byte-identical. Its one-line note adds the consequence: it is the top-ranked variant, so no row carries the best marker, or it still holds a best marker, so the ledger can show two. Applied in: Task 1.
- **D3** (owner, planning session, 2026-10-21): an unterminated `COMPARISON:BEGIN` is refused. A scratch run on the base comparator showed the data loss: the first run appends a block, and the second run rewrites everything from the stray BEGIN to the appended END, so the Decision log is deleted. Before ranking and before `--output` is written, the comparator refuses a ledger whose BEGIN and END markers are unpaired, repeated or out of order, through `error:`. This adds one ELPD-mode refusal, on malformed ledgers only. Applied in: Task 1.

**Defaults this plan settles (for the owner's review at plan review):**

- **Δscore sign.** `score_diff` is the variant's score minus the top variant's score, averaged over units. Its sign shows the orientation: at or above 0 when lower is better, at or below 0 when higher is better. The top row shows `0` for Δscore and `0` for SE(Δ).
- **Score-mode qualified marker.** `**best among score-compared variants**`. ELPD mode keeps `**best among ELPD-compared variants**` (R18). `update_ledger` treats all three marker strings as stale markers.
- **Where `Criterion:` is read.** Only from a line outside the COMPARISON block and above the Variants table, matched in full (`Criterion: <name>`). A `Criterion:` line in the Decision log or in the block never sets the mode.
- **Pre-flight order.** The `--ledger` path, then its markers, then the mode against the criterion. All three run before any ranking and before `--output` is written.
- **R19 fixture.** The LFO and blocked K-fold blocks share one AR(1) setup block. A named fixture `time_series` in `build/snippet_preamble.py` copies that block verbatim, and a test pins the two equal. This follows the preamble's `add_log_prior` pattern. Without a fixture, the gate would only WARN on the two route blocks and never run them.
- **R19 joint score.** `azs.loo_kfold` scores each held-out step on its own (checked in arviz-stats 1.3.3's `_compute_kfold_results`). So the snippet adds one step that computes each block's joint log score from `save_fits=True`.
- **NOTICE.** The bayesian-workflow paragraph already lists per-file additions to `model-comparison.md`, so the spec's condition holds and Task 4 adds a line. The loo R package's licence is "GPL (≥ 3)" (CRAN page, checked 2026-10-21), and nothing from it is reproduced.
- **R22 edges.** Confirmed by the scanner at plan time: today the only track edges are track → bayesian-workflow and tune → track. Task 3 makes the first one soft. Task 4's link to `../../track-model-experiments/references/predictive-evaluation.md` creates bayesian-workflow → track, and Task 4 adds it as soft in the same commit.

---

## File Structure

| File | Change | Responsibility |
|---|---|---|
| `skills/track-model-experiments/scripts/compare_experiments.py` | Modify (Tasks 1, 2) | hardening; score mode; mode/criterion pre-flight |
| `skills/track-model-experiments/scripts/test_compare_experiments.py` | Modify (append in Tasks 1, 2; edit existing in Task 6) | R24 tests, hardening tests, (f) gaps |
| `skills/track-model-experiments/references/predictive-evaluation.md` | Create (Task 3) | R14: backtests, the `scores.json` contract, paired Δ and its limits, baselines, proper scores |
| `skills/track-model-experiments/SKILL.md` | Modify (body Task 3, description Task 5) | R21, R20 |
| `README.md` | Modify (Task 3) | R23: track's row |
| `install.py` | Modify (Task 3) | R22: drop track → bayesian-workflow |
| `build/test_runtime_support.py` | Modify (Tasks 3, 4) | R22 soft references; the install-closure case |
| `skills/bayesian-workflow/references/model-comparison.md` | Modify (Task 4) | R19 section and Contents entry |
| `build/snippet_preamble.py` | Modify (Task 4) | the `time_series` fixture; coverage docstring |
| `build/test_check_snippets.py` | Modify (Task 4) | pin tests for the fixture and the two route blocks |
| `NOTICE` | Modify (Task 4) | the R19 provenance line |
| `specs/verification/65-track-description-microtest.md` | Create (Task 5) | the V1 track record |

The kit for V1 lives outside the repo at `~/.cache/agent-skills/scratch/plan65-micro/`.

---

### Task 1: Harden the comparator (ELPD mode)

Closes deferred item parts (a)–(e), D2 and D3, and adds the (f) gap tests that need no edit to an existing test.

**Files:**
- Modify: `skills/track-model-experiments/scripts/compare_experiments.py` (constants after `QUALIFIED_BEST`; `render_comparison_block`'s return; everything from `_BLOCK_RE = ...` through the end of `update_ledger`; `main()` after `parse_args`)
- Test: `skills/track-model-experiments/scripts/test_compare_experiments.py` (append only)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces (Task 2 relies on these exact names):
  - constants `MARKERS: tuple[str, ...]`, `BLOCK_BEGIN = '<!-- COMPARISON:BEGIN -->'`, `BLOCK_END = '<!-- COMPARISON:END -->'`
  - `_variants_table(lines: list[str]) -> tuple[int, list[str], list[int]] | None` — now returns `(header_line_index, header_cells, data_row_line_indices)`
  - `ledger_problem(ledger_path: Path) -> str | None`
  - `_wide_row_note(cells: list[str], width: int, top_id: str) -> str`
  - `update_ledger(ledger_path, block, ranking, not_compared) -> None` (Task 2 adds a `mode` keyword)
  - test helpers `_elpd_entry`, `RANKED`, `_stamp`, `_table_cells(text, variant_id) -> list[str]`

- [ ] **Step 1: Write the failing tests**

Append to the end of `test_compare_experiments.py`:

```python


# --- Hardening after plan 59's final review (plan 65 Task 1) ---

def _elpd_entry(variant_id, elpd, **extra):
    '''A ranked ELPD-mode entry with the keys update_ledger and metric_cells read.'''
    return {'id': variant_id, 'elpd': elpd, 'se': 10.0, 'elpd_diff': 0.0, 'dse': 0.0,
            'weight': 0.5, 'warning': False, 'diag_diff': '', 'diag_elpd': '',
            'max_rhat': 1.002, 'min_ess': 400.0, 'divergences': 0, 'ppc': 'fair',
            'psense': 'ok', **extra}


RANKED = [_elpd_entry('m-full', -280.4),
          _elpd_entry('m-intercept', -391.7, elpd_diff=-111.3, max_rhat=None,
                      divergences=None)]


def _stamp(ledger, ranking, not_compared=()):
    block = compare_experiments.render_comparison_block(ranking, list(not_compared))
    compare_experiments.update_ledger(ledger, block, ranking, list(not_compared))
    return ledger.read_text()


def _table_cells(text, variant_id):
    '''A Variants-table row's cells, read through the comparator's own parser.'''
    lines = text.splitlines()
    _, _, rows = compare_experiments._variants_table(lines)
    return next(cells for cells in (compare_experiments._cells(lines[i]) for i in rows)
                if cells[0] == variant_id)


def test_cells_keep_an_empty_first_cell():
    assert compare_experiments._cells('|| b |') == ['', 'b']


def test_cells_keep_an_escaped_pipe_that_ends_the_last_cell():
    assert compare_experiments._cells('| m | x \\||') == ['m', 'x \\|']


def test_winner_row_gets_its_cells_and_the_marker(tmp_path):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(_ledger_with('m-full', 'm-intercept'))
    cells = _table_cells(_stamp(ledger, RANKED), 'm-full')
    assert cells[4:] == ['-280.4', '0.0', '1.002', '0', 'fair', 'ok', '**best**']


def test_missing_diagnostics_render_as_blank_cells(tmp_path):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(_ledger_with('m-full', 'm-intercept'))
    cells = _table_cells(_stamp(ledger, RANKED), 'm-intercept')
    assert cells[4:8] == ['-391.7', '-111.3', '', '']


def test_an_empty_observation_dimension_is_refused():
    import types

    import xarray as xr
    ll = xr.Dataset({'y': (('chain', 'draw', 'obs'), np.zeros((2, 10, 0)))})
    idata = types.SimpleNamespace(log_likelihood=ll)
    with pytest.raises(ValueError, match='no observation dimension'):
        compare_experiments.pointwise_count(idata, 'm-empty')


def test_a_short_row_is_padded_and_filled(tmp_path):
    text = _ledger_with('m-full', 'm-intercept')
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(text.replace(_row(text, 'm-intercept'), '| m-intercept | m-full | drop slope |'))
    cells = _table_cells(_stamp(ledger, RANKED), 'm-intercept')
    assert len(cells) == 11
    assert (cells[2], cells[4], cells[-1]) == ('drop slope', '-391.7', '')   # padded, not invented


def test_a_header_without_status_is_not_the_variants_table():
    assert compare_experiments.ledger_ids('| id | ELPD |\n|---|---|\n| m-full | |\n') is None


def test_a_wide_top_row_note_says_no_row_carries_the_marker(tmp_path, capsys):
    text = _ledger_with('m-full', 'm-intercept')
    row = _row(text, 'm-full')
    wide = row.replace('| h |', '| h | x |')
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(text.replace(row, wide))
    out = _stamp(ledger, RANKED)
    notes = [ln for ln in capsys.readouterr().err.splitlines() if 'do not line up' in ln]
    assert len(notes) == 1 and 'no row carries the best marker' in notes[0]
    assert _row(out, 'm-full') == wide
    assert '**best' not in out


def test_a_wide_row_holding_a_stale_marker_is_named(tmp_path, capsys):
    text = _ledger_with('m-full', 'm-intercept')
    row = _row(text, 'm-intercept')
    stale = row.replace('| h |', '| h | x |').replace('| candidate |', '| **best** |')
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(text.replace(row, stale))
    out = _stamp(ledger, RANKED)
    notes = [ln for ln in capsys.readouterr().err.splitlines() if 'do not line up' in ln]
    assert len(notes) == 1 and 'still holds a best marker' in notes[0]
    assert out.count('**best**') == 2                 # the note is the remedy, not a rewrite


def test_ranked_variants_without_a_row_are_named(tmp_path, capsys):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(_ledger_with('m-intercept'))
    out = _stamp(ledger, RANKED)
    err = capsys.readouterr().err
    assert 'ranked variants with no Variants-table row: m-full.' in err
    assert 'no row carries the best marker' in err
    assert '**best' not in out


def test_a_table_with_no_matching_metric_column_is_noted(tmp_path, capsys):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text('| id | elpd | status |\n|---|---|---|\n'
                      '| m-full | | candidate |\n| m-intercept | | candidate |\n')
    _stamp(ledger, RANKED)
    assert capsys.readouterr().err.count('none of the metric columns') == 1


def test_a_missing_ledger_exits_through_error_before_any_output(tmp_path, capsys):
    out = tmp_path / 'comparison.json'
    code = compare_experiments.main(['--analysis-dir', str(tmp_path), '--ledger',
                                     str(tmp_path / 'typo.md'), '--output', str(out)])
    err = capsys.readouterr().err
    assert code == 1 and err.startswith('error: ') and 'typo.md' in err
    assert not out.exists()


@pytest.mark.parametrize('markers', [
    '<!-- COMPARISON:BEGIN -->\nstale\n',
    '<!-- COMPARISON:END -->\nstale\n<!-- COMPARISON:BEGIN -->\n',
    '<!-- COMPARISON:BEGIN -->\na\n<!-- COMPARISON:END -->\n' * 2,
])
def test_unpaired_or_repeated_markers_are_refused_before_anything_is_written(
        tmp_path, capsys, markers):
    text = _ledger_with('m-full', 'm-intercept') + markers
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(text)
    out = tmp_path / 'comparison.json'
    code = compare_experiments.main(['--analysis-dir', str(tmp_path), '--ledger', str(ledger),
                                     '--output', str(out)])
    err = capsys.readouterr().err
    assert code == 1 and err.startswith('error: ') and 'one pair of markers' in err
    assert ledger.read_text() == text
    assert not out.exists()
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `uv run --python 3.13 python build/run_suites.py track-model-experiments -- -k "cells_keep or winner_row or missing_diagnostics or empty_observation or short_row or header_without or wide_ or ranked_variants or no_matching or missing_ledger or unpaired" -rf`

Expected: `13 failed, 2 passed`. The two that pass are coverage pins of behaviour that is already right (`test_an_empty_observation_dimension_is_refused`, `test_a_header_without_status_is_not_the_variants_table`). Three of the failures (`winner_row`, `missing_diagnostics`, `short_row`) are also coverage pins. They fail only because `_table_cells` unpacks the three-item return that this task gives `_variants_table` (`ValueError: not enough values to unpack`). Read each failure and check that it is one of these causes.

- [ ] **Step 3: Implement**

In `compare_experiments.py`:

(1) After the line `QUALIFIED_BEST = '**best among ELPD-compared variants**'`, add:

```python
MARKERS = (BEST, QUALIFIED_BEST)
BLOCK_BEGIN = '<!-- COMPARISON:BEGIN -->'
BLOCK_END = '<!-- COMPARISON:END -->'
```

(2) In `render_comparison_block`, replace

```python
    return f'<!-- COMPARISON:BEGIN -->\n{table}\n<!-- COMPARISON:END -->'
```

with

```python
    return f'{BLOCK_BEGIN}\n{table}\n{BLOCK_END}'
```

(3) Replace everything from the line `_BLOCK_RE = re.compile(r'<!-- COMPARISON:BEGIN -->.*?<!-- COMPARISON:END -->', re.S)` through the last line of `update_ledger` (the `ledger_path.write_text(...)` line just above `def compare(`) with:

```python
_BLOCK_RE = re.compile(f'{re.escape(BLOCK_BEGIN)}.*?{re.escape(BLOCK_END)}', re.S)


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


def _wide_row_note(cells: list[str], width: int, top_id: str) -> str:
    note = (f'note: ledger row {cells[0]} has {len(cells)} cells against {width} in the '
            'header, so its cells do not line up with the header and the row was left '
            'unchanged. Escape a literal pipe in a cell as \\|.')
    if cells[0] == top_id:
        note += ' It is the top-ranked variant, so no row carries the best marker.'
    if any(c in MARKERS for c in cells):
        note += ' It still holds a best marker, so the ledger can show two.'
    return note


def update_ledger(ledger_path: Path, block: str, ranking: list[dict],
                  not_compared: list[str]) -> None:
    '''Rewrite the COMPARISON block, fill the metric cells and move the best marker.

    Only the COMPARISON block (replaced, or appended if absent) and the Variants
    table's metric and status cells change; human prose and the table's left
    half are preserved. Each ranked row is re-joined with '| '/' |' spacing, so
    its cell padding is normalized — this is intentional. An unranked row keeps
    its cells, except that a stale best marker returns to candidate. A row with
    more cells than the header does not line up with it, so it is left as it is
    and a note names it. Notes also name ranked variants that have no row, and a
    table with none of the metric columns.
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
        marker = QUALIFIED_BEST if not_compared else BEST
        columns = list(metric_cells(ranking[0]))
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
                for column, value in metric_cells(entry).items():
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
```

(4) In `main()`, replace

```python
    args = ap.parse_args(argv)

    try:
```

with

```python
    args = ap.parse_args(argv)

    problem = ledger_problem(args.ledger) if args.ledger else None
    if problem:
        print(f'error: {problem}', file=sys.stderr)
        return 1
    try:
```

- [ ] **Step 4: Run the whole suite to verify it passes**

Run: `uv run --python 3.13 python build/run_suites.py track-model-experiments`
Expected: every test passes, 15 more than before this task (the 26 existing tests plus 15 new; the scratch run at plan time gave `41 passed`). If an existing test fails, stop: R18 forbids editing it, so the implementation is wrong.

- [ ] **Step 5: Commit**

```bash
git add skills/track-model-experiments/scripts/compare_experiments.py skills/track-model-experiments/scripts/test_compare_experiments.py
git commit -m "fix(track): harden the comparator's ledger handling" -m "Closes plan 59's hardening parts (a)-(e): one outer pipe per side in _cells, a note for an over-wide row's marker consequence (D2), a note naming ranked variants with no row, an error: exit for a missing --ledger path, and a note when no metric column matches. Refuses unpaired COMPARISON markers before anything is written (D3), and adds the (f) gap tests that need no edit to an existing test."
```

---

### Task 2: Score mode in the comparator

Implements R13, R15 (parsing), R16, R17, the script half of R21, and R24.

**Files:**
- Modify: `skills/track-model-experiments/scripts/compare_experiments.py`
- Test: `skills/track-model-experiments/scripts/test_compare_experiments.py` (append only)

**Interfaces:**
- Consumes (Task 1): `MARKERS`, `BLOCK_BEGIN`, `BLOCK_END`, `_variants_table` (three-item return), `ledger_problem`, `update_ledger`, test helpers `_table_cells`, `_ledger_with`, `_row`, `LEDGER`, `_run`, fixture `analysis_dir`.
- Produces:
  - constants `SCORE_QUALIFIED_BEST = '**best among score-compared variants**'`, `MODES = ('elpd', 'score')`, `ELPD_CRITERION = 'elpd-loo'`, `SCORE_FILE = 'scores.json'`, `ORIENTATIONS = ('higher', 'lower')`, `MIN_UNITS = 2`
  - `load_scores(folder: Path) -> dict` with keys `criterion`, `orientation`, `units`
  - `compare_scores(analysis_dir: Path, folders: list[Path] | None, declared: str | None = None) -> tuple[list[dict], str, str]` returning `(ranking, criterion, orientation)`. Each ranking entry has `id`, `score`, `score_diff`, `se_diff`, `n_units`.
  - `ledger_criterion(text: str) -> str`, `mode_problem(mode, criterion, ledger_path) -> str | None`
  - `score_cells(r) -> dict[str, str]` keyed `score`, `Δscore`, `SE(Δ)`
  - `render_score_table(ranking, criterion, orientation) -> str`, `render_score_block(ranking, not_compared, criterion, orientation) -> str`
  - `update_ledger(..., mode: str = 'elpd')`
  - CLI: `--mode {elpd,score}`. `comparison.json` keys `mode`, `criterion`, `ranking`, `not_compared`.
  - Task 3 documents these names, and Task 4's snippets write `scores.json` files that `load_scores` accepts.

- [ ] **Step 1: Write the failing tests**

Append to the end of `test_compare_experiments.py`:

```python


# --- Score mode: ranking and refusals (plan 65 Task 2; spec R13, R16, R17, R24) ---

def _scores(folder, units, criterion='cv-mse', orientation='lower'):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'scores.json').write_text(json.dumps(
        {'criterion': criterion, 'orientation': orientation, 'units': units}))
    return folder


# Hand-computed: d = b - a = [0.5, 0.0, 1.0, 0.5], so the paired difference is 0.5.
# Its sample sd (ddof=1) is sqrt(0.5 / 3), so SE = 0.2041; ddof=0 would give 0.1768.
A_UNITS = {'fold-1': 1.0, 'fold-2': 2.0, 'fold-3': 3.0, 'fold-4': 4.0}
B_UNITS = {'fold-1': 1.5, 'fold-2': 2.0, 'fold-3': 4.0, 'fold-4': 4.5}


def test_lower_is_better_ranks_the_smallest_mean_first(tmp_path):
    _scores(tmp_path / 'b', B_UNITS)
    _scores(tmp_path / 'a', A_UNITS)
    ranking, criterion, orientation = compare_experiments.compare_scores(tmp_path, None)
    assert [r['id'] for r in ranking] == ['a', 'b']
    assert (criterion, orientation) == ('cv-mse', 'lower')
    assert [r['score'] for r in ranking] == [pytest.approx(2.5), pytest.approx(3.0)]


def test_higher_is_better_ranks_the_largest_mean_first(tmp_path):
    _scores(tmp_path / 'a', A_UNITS, 'lfo-elpd', 'higher')
    _scores(tmp_path / 'b', B_UNITS, 'lfo-elpd', 'higher')
    ranking, _, orientation = compare_experiments.compare_scores(tmp_path, None)
    assert orientation == 'higher'
    assert [r['id'] for r in ranking] == ['b', 'a']
    assert ranking[1]['score_diff'] == pytest.approx(-0.5)


def test_paired_difference_and_its_se_match_the_hand_computation(tmp_path):
    _scores(tmp_path / 'a', A_UNITS)
    _scores(tmp_path / 'b', B_UNITS)
    top, other = compare_experiments.compare_scores(tmp_path, None)[0]
    assert (top['score_diff'], top['se_diff']) == (0.0, 0.0)
    assert other['score_diff'] == pytest.approx(0.5)
    assert other['se_diff'] == pytest.approx(np.sqrt(0.5 / 3) / 2)
    assert other['se_diff'] != pytest.approx(np.sqrt(0.125) / 2)    # not ddof=0
    assert other['n_units'] == 4


def _score_refusal(tmp_path, capsys, *extra):
    code = compare_experiments.main(['--analysis-dir', str(tmp_path), '--mode', 'score', *extra])
    err = capsys.readouterr().err
    assert code == 1 and err.startswith('error: ') and 'Traceback' not in err
    return err


def test_a_folder_without_scores_json_is_refused(tmp_path, capsys):
    _scores(tmp_path / 'a', A_UNITS)
    (tmp_path / 'b').mkdir()
    err = _score_refusal(tmp_path, capsys, '--folders', str(tmp_path / 'a'), str(tmp_path / 'b'))
    assert 'no scores.json in b' in err


def test_a_criterion_that_differs_across_variants_is_refused(tmp_path, capsys):
    _scores(tmp_path / 'a', A_UNITS)
    _scores(tmp_path / 'b', B_UNITS, criterion='cv-mae')
    err = _score_refusal(tmp_path, capsys)
    assert "'b': 'cv-mae'" in err and 'one criterion' in err


def test_an_orientation_that_differs_across_variants_is_refused(tmp_path, capsys):
    _scores(tmp_path / 'a', A_UNITS)
    _scores(tmp_path / 'b', B_UNITS, orientation='higher')
    err = _score_refusal(tmp_path, capsys)
    assert 'orientation differs' in err and "'b': 'higher'" in err


def test_unit_keys_that_differ_across_variants_are_refused(tmp_path, capsys):
    _scores(tmp_path / 'a', A_UNITS)
    _scores(tmp_path / 'b', {**{k: v for k, v in B_UNITS.items() if k != 'fold-4'},
                              'fold-5': 4.5})
    err = _score_refusal(tmp_path, capsys)
    assert "variant 'b'" in err and 'fold-5' in err and 'fold-4' in err


@pytest.mark.parametrize('value', [float('nan'), float('inf')])
def test_a_non_finite_score_is_refused(tmp_path, capsys, value):
    _scores(tmp_path / 'a', A_UNITS)
    _scores(tmp_path / 'b', {**B_UNITS, 'fold-2': value})
    err = _score_refusal(tmp_path, capsys)
    assert "variant 'b'" in err and 'non-finite' in err and 'fold-2' in err


def test_fewer_than_two_units_is_refused(tmp_path, capsys):
    _scores(tmp_path / 'a', {'fold-1': 1.0})
    _scores(tmp_path / 'b', {'fold-1': 1.5})
    err = _score_refusal(tmp_path, capsys)
    assert "variant 'a'" in err and 'at least 2' in err


def test_fewer_than_two_score_variants_is_refused(tmp_path, capsys):
    _scores(tmp_path / 'a', A_UNITS)
    err = _score_refusal(tmp_path, capsys)
    assert 'at least two variants' in err


# --- Score mode: the ledger (plan 65 Task 2; spec R15, R16, R24) ---

SCORE_LEDGER = '''# Experiments — county nowcast

Criterion: cv-mse

| id (slug) | parent | what changed | hypothesis | score | Δscore | SE(Δ) | status |
|---|---|---|---|---|---|---|---|
| a | — | ridge on lagged features | sets a floor | | | | candidate |
| b | a | add county effects | pooling helps | | | | candidate |

<!-- COMPARISON:BEGIN -->
<!-- COMPARISON:END -->

## Decision log
- Criterion: elpd-loo here is prose and never sets the mode.
'''
ROW_C = '| c | a | gradient boosting | nonlinearity matters | | | | candidate |\n'


def _score_ledger(tmp_path, text=SCORE_LEDGER):
    ledger = tmp_path / 'experiments.md'
    ledger.write_text(text)
    return ledger


def _with_row_c(text=SCORE_LEDGER):
    row_b = '| b | a | add county effects | pooling helps | | | | candidate |\n'
    return text.replace(row_b, row_b + ROW_C)


def test_ledger_criterion_reads_the_line_above_the_variants_table():
    assert compare_experiments.ledger_criterion(SCORE_LEDGER) == 'cv-mse'
    assert compare_experiments.ledger_criterion(LEDGER) == 'elpd-loo'
    undeclared = SCORE_LEDGER.replace('Criterion: cv-mse\n', '')
    assert compare_experiments.ledger_criterion(undeclared) == 'elpd-loo'


def test_score_mode_against_an_elpd_ledger_is_refused(tmp_path, capsys):
    ledger = _score_ledger(tmp_path, LEDGER)
    err = _score_refusal(tmp_path, capsys, '--ledger', str(ledger))
    assert 'Criterion: elpd-loo' in err and '--mode elpd' in err
    assert ledger.read_text() == LEDGER


def test_elpd_mode_against_a_score_ledger_is_refused(tmp_path, capsys):
    ledger = _score_ledger(tmp_path)
    code = compare_experiments.main(['--analysis-dir', str(tmp_path), '--ledger', str(ledger)])
    err = capsys.readouterr().err
    assert code == 1 and err.startswith('error: ')
    assert 'Criterion: cv-mse' in err and '--mode score' in err


def test_a_variant_criterion_that_differs_from_the_ledger_is_refused(tmp_path, capsys):
    runs = tmp_path / 'runs'
    _scores(runs / 'a', A_UNITS)
    _scores(runs / 'b', B_UNITS)
    ledger = _score_ledger(tmp_path, SCORE_LEDGER.replace('Criterion: cv-mse', 'Criterion: cv-mae'))
    err = _score_refusal(runs, capsys, '--ledger', str(ledger))
    assert "Criterion: line" in err and "'cv-mae'" in err and "'a': 'cv-mse'" in err


def test_score_cells_qualified_marker_and_comparison_json(tmp_path, capsys):
    runs = tmp_path / 'runs'
    _scores(runs / 'a', A_UNITS)
    _scores(runs / 'b', B_UNITS)
    ledger = _score_ledger(tmp_path, _with_row_c())
    out = tmp_path / 'comparison.json'
    code = compare_experiments.main(['--analysis-dir', str(runs), '--mode', 'score',
                                     '--ledger', str(ledger), '--output', str(out)])
    assert code == 0, capsys.readouterr().err
    assert 'ledger rows not compared: c.' in capsys.readouterr().err
    payload = json.loads(out.read_text())
    assert (payload['mode'], payload['criterion'], payload['not_compared']) == (
        'score', 'cv-mse', ['c'])
    text = ledger.read_text()
    assert _table_cells(text, 'a')[4:] == ['2.5', '0', '0', '**best among score-compared variants**']
    assert _table_cells(text, 'b')[4:] == ['3', '0.5', '0.2041', 'candidate']
    assert _table_cells(text, 'c')[4:] == ['', '', '', 'candidate']
    assert 'Not compared: c. The best marker covers the score-compared variants only.' in text
    assert 'Ranked on cv-mse (lower is better).' in text
    assert '- Criterion: elpd-loo here is prose and never sets the mode.' in text


def test_score_marker_resets_once_every_row_is_compared_and_reruns_are_idempotent(tmp_path):
    runs = tmp_path / 'runs'
    _scores(runs / 'a', A_UNITS)
    _scores(runs / 'b', B_UNITS)
    ledger = _score_ledger(tmp_path, _with_row_c())
    args = ['--analysis-dir', str(runs), '--mode', 'score', '--ledger', str(ledger)]
    assert compare_experiments.main(args) == 0
    ledger.write_text(ledger.read_text().replace(ROW_C, ''))
    assert compare_experiments.main(args) == 0
    first = ledger.read_text()
    assert compare_experiments.main(args) == 0
    assert ledger.read_text() == first
    assert _table_cells(first, 'a')[-1] == '**best**'
    assert 'score-compared' not in first


def test_elpd_comparison_json_carries_mode_and_criterion(analysis_dir, tmp_path):
    out = tmp_path / 'comparison.json'
    r = _run('--analysis-dir', str(analysis_dir), '--output', str(out))
    assert r.returncode == 0, r.stderr
    payload = json.loads(out.read_text())
    assert (payload['mode'], payload['criterion']) == ('elpd', 'elpd-loo')
```

- [ ] **Step 2: Run the suite to verify the new tests fail**

Run: `uv run --python 3.13 python build/run_suites.py track-model-experiments -- -rf`
Expected: the 18 new tests fail and every earlier test passes (`18 failed, 41 passed` at plan time). Causes: `compare_scores` and `ledger_criterion` do not exist (`AttributeError`), `--mode` is not an argument (`SystemExit: 2` from argparse), and `comparison.json` has no `mode` key (`KeyError`).

- [ ] **Step 3: Implement**

In `compare_experiments.py`:

(1) Replace the module docstring (the first `'''…'''` block) with:

```python
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
```

(2) Replace `import re\nimport sys\n` with `import re\nimport statistics\nimport sys\n`.

(3) Replace

```python
# The status cell of the top-ranked Variants-table row. While a ledger row went
# uncompared, the marker says the ranking covers the ELPD-compared rows only.
BEST = '**best**'
QUALIFIED_BEST = '**best among ELPD-compared variants**'
MARKERS = (BEST, QUALIFIED_BEST)
BLOCK_BEGIN = '<!-- COMPARISON:BEGIN -->'
BLOCK_END = '<!-- COMPARISON:END -->'
```

with

```python
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
```

(4) Directly after `metric_cells`, add:

```python
def score_cells(r: dict) -> dict[str, str]:
    '''One score-ranked variant's metrics, keyed by a score ledger's column names.'''
    return {
        'score': f"{r['score']:.4g}",
        'Δscore': f"{r['score_diff']:.4g}",
        'SE(Δ)': f"{r['se_diff']:.4g}",
    }
```

(5) Directly after `render_comparison_block`, add:

```python
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
```

(6) Directly after the `_BLOCK_RE = ...` line, add:

```python
_CRITERION_RE = re.compile(r'Criterion:\s*(\S(?:.*\S)?)')
```

(7) Directly after `ledger_ids`, add:

```python
def ledger_criterion(text: str) -> str:
    '''The criterion the ledger declares above its Variants table; elpd-loo without one.

    Only a line outside the COMPARISON block and above the table counts, so a
    Criterion: line in the Decision log or in the block never sets the mode.
    '''
    lines = text.splitlines()
    table = _variants_table(lines)
    in_block = False
    for line in lines[:table[0] if table else len(lines)]:
        stripped = line.strip()
        if stripped == BLOCK_BEGIN:
            in_block = True
        elif stripped == BLOCK_END:
            in_block = False
        elif not in_block and (m := _CRITERION_RE.fullmatch(stripped)):
            return m.group(1)
    return ELPD_CRITERION
```

(8) Directly after `ledger_problem`, add:

```python
def mode_problem(mode: str, criterion: str, ledger_path: Path) -> str | None:
    '''Why --mode cannot fill a ledger on this criterion; None when it can.'''
    wanted = 'elpd' if criterion == ELPD_CRITERION else 'score'
    if mode == wanted:
        return None
    return (f'{ledger_path} reads as Criterion: {criterion} (a ledger without a '
            f'Criterion: line reads as {ELPD_CRITERION}), which --mode {mode} cannot '
            f'rank. Run --mode {wanted}, or re-declare the ledger\'s criterion: a '
            'ledger holds one criterion.')
```

(9) In `update_ledger`:
- change the signature line `                  not_compared: list[str]) -> None:` to `                  not_compared: list[str], mode: str = 'elpd') -> None:`;
- in its docstring, change `table with none of the metric columns.` to `table with none of the mode's metric columns.`;
- replace

```python
        marker = QUALIFIED_BEST if not_compared else BEST
        columns = list(metric_cells(ranking[0]))
```

with

```python
        cells_of = score_cells if mode == 'score' else metric_cells
        qualified = SCORE_QUALIFIED_BEST if mode == 'score' else QUALIFIED_BEST
        marker = qualified if not_compared else BEST
        columns = list(cells_of(ranking[0]))
```

- and replace `                for column, value in metric_cells(entry).items():` with `                for column, value in cells_of(entry).items():`.

(10) In `compare()`, replace the missing-file error

```python
            f'no inference_data.nc in {", ".join(missing)}; the comparator ranks '
            'Bayesian fits by ELPD only. Until a non-ELPD mode exists, record a '
            "non-Bayesian winner and its CV score in the ledger's Decision log.")
```

with

```python
            f'no inference_data.nc in {", ".join(missing)}; ELPD mode ranks Bayesian '
            'fits only. To rank a non-Bayesian variant, give every variant a '
            'scores.json on one criterion and run --mode score against a score '
            'ledger; do not park the variant in the Decision log.')
```

The new text keeps the substring `Decision log`, which the existing test `test_folder_without_inference_data_exits_through_error` asserts (R18).

(11) Directly before `def main(`, add:

```python
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
```

(12) Replace the whole of `main()` (from `def main(argv=None):` to its `return 0`, leaving the `if __name__ == '__main__':` guard) with:

```python
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
```

- [ ] **Step 4: Run the whole suite and the script's help**

Run: `uv run --python 3.13 python build/run_suites.py track-model-experiments`
Expected: every test passes, 18 more than after Task 1 (`59 passed` at plan time).

Run: `grep -n 'until a non-ELPD mode exists' skills/track-model-experiments/scripts/compare_experiments.py`
Expected: no output (R21's last bullet).

Run: `uv run skills/track-model-experiments/scripts/compare_experiments.py --help`
Expected: the new docstring, then `--mode {elpd,score}` in the usage line.

- [ ] **Step 5: Commit**

```bash
git add skills/track-model-experiments/scripts/compare_experiments.py skills/track-model-experiments/scripts/test_compare_experiments.py
git commit -m "feat(track): add the comparator's score mode" -m "Ranks variants from each folder's scores.json by mean score with the file's orientation, and reports each variant's paired difference from the top variant and its standard error (spec R13, R16). Refuses the R17 inputs, reads the ledger's Criterion: line (R15) and refuses a mode that does not match it, and adds mode and criterion to comparison.json. ELPD mode is unchanged."
```

---

### Task 3: Predictive-evaluation reference, track's body, README row and install dependency

Implements R14, R21 (body), R22 (track → bayesian-workflow) and R23. R23 also closes part (a) of the plan-59 doc-nits item.

**Files:**
- Create: `skills/track-model-experiments/references/predictive-evaluation.md`
- Modify: `skills/track-model-experiments/SKILL.md` (body only: Overview, When to use, The ledger, The comparator, Stopping rule, Relationship section. Leave the frontmatter and "Fresh session per variant" alone.)
- Modify: `README.md` (the `track-model-experiments` row)
- Modify: `install.py` (`DEPENDENCIES`)
- Modify: `build/test_runtime_support.py` (`SOFT_REFERENCES`; the track case in `test_skill_brings_its_hard_dependencies`)

**Interfaces:**
- Consumes (Task 2): the CLI flags, the R17 refusals, the marker strings and the column names, exactly as Task 2 implements them.
- Produces: the path `skills/track-model-experiments/references/predictive-evaluation.md` and its section names. Task 4 links to it. Stage 2 (R7, R11) and Stage 3 (R25–R27) point to it.

- [ ] **Step 1: Write the failing check**

The installer test pins the closure. Change the track case in `build/test_runtime_support.py`'s `test_skill_brings_its_hard_dependencies` parametrize list from

```python
    ('claude', 'track-model-experiments', (), {
      '.claude/skills/track-model-experiments',
      '.claude/skills/bayesian-workflow',
    }),
```

to

```python
    # Score mode works without bayesian-workflow, so it is a soft reference (R22).
    ('claude', 'track-model-experiments', (), {
      '.claude/skills/track-model-experiments',
    }),
```

Run: `cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k "hard_dependencies and track"`
Expected: FAIL. The installed set still includes `.claude/skills/bayesian-workflow`.

- [ ] **Step 2: Move the dependency to a soft reference**

In `install.py`, delete the line

```python
  'skill:track-model-experiments': ('skill:bayesian-workflow',),
```

In `build/test_runtime_support.py`'s `SOFT_REFERENCES`, add this entry directly above the `# Quotes an @-path as an example of what not to write.` entry, keeping the set's alphabetical order by source:

```python
  # ELPD mode reads bayesian-workflow's model-comparison doctrine; score mode
  # works without it.
  ('skill:track-model-experiments', 'skill:bayesian-workflow'),
```

Run: `cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py`
Expected: PASS, the drift test `test_declared_dependencies_match_skill_and_command_text` included.

- [ ] **Step 3: Create the predictive-evaluation reference**

Create `skills/track-model-experiments/references/predictive-evaluation.md`:

````markdown
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
````

- [ ] **Step 4: Rewrite track's body (R21)**

Make these replacements in `skills/track-model-experiments/SKILL.md`. Each old text is quoted exactly from the file at the base commit.

(1) Replace the second paragraph of `## Overview`:

```markdown
This skill is the iteration layer above single-model workflow. Core
principle: one file records *what changed and why* (a human-authored ledger);
one script records *which won* (an ArviZ-based comparator that ranks variants
and stamps the result back into the ledger).
```

with

```markdown
The same holds for a cross-validated regression that gains a feature set, or a
forecaster that meets a rival in a backtest.

This skill is the iteration layer above single-model work. Core principle: one
file records *what changed and why* (a human-authored ledger); one script
records *which won* (a comparator that ranks variants and stamps the result
back into the ledger). The comparator has two modes, and a ledger uses one:

- **ELPD mode** ranks Bayesian fits by PSIS-LOO from each variant's
  `inference_data.nc`.
- **Score mode** ranks any variants (tabular cross-validation, forecast
  backtests, or Bayesian fits scored by leave-future-out) from each variant's
  `scores.json`: one score per fold or forecast origin, on one shared
  criterion. `references/predictive-evaluation.md` holds the protocol and the
  file's contract.
```

(2) Replace the fourth bullet of `## When to use`:

```markdown
- A hyperparameter search in `tune-hyperparameters` produced a winner worth
  comparing against structurally different models — graduate it to a variant
  row here (`what changed` = "tuned `<class>` via Optuna"). Until a non-ELPD
  mode exists, a non-Bayesian winner (no `inference_data.nc` to rank) goes in
  the Decision log with its CV score instead.
```

with

```markdown
- Ranking cross-validated or backtested variants of any model class on one
  criterion (fold MSE, log-loss, CRPS, leave-future-out ELPD) — score mode.
- A hyperparameter search in `tune-hyperparameters` produced a winner worth
  comparing against structurally different models — graduate it to a variant
  row here (`what changed` = "tuned `<class>` via Optuna"), with a
  `scores.json` on the ledger's criterion. A non-Bayesian winner has no
  `inference_data.nc`, so it ranks only in a score ledger. To compare it with
  the variants of an existing `elpd-loo` ledger, first re-declare that
  ledger's criterion as a score criterion. Each Bayesian variant then writes
  `scores.json` on the same units, for example a per-fold log score or the MSE
  of the posterior-predictive mean. Until that is done, the comparator names
  the new row as not compared.
```

(3) In `Not for:`, after the `**Tuning continuous ML hyperparameters**` bullet (it ends `discrete, hypothesis-driven model variants.`), add:

```markdown
- **Neural runs or checkpoints** — `evaluate-deep-learning` owns their
  experiment record.
```

(4) In `## The ledger (experiments.md)`, replace the paragraph after the example:

```markdown
`id`, `parent`, `what changed`, `hypothesis`, and `status` are yours to write —
the reasoning trail no script can reconstruct after the fact. `ELPD` through
`psense` are metric columns the comparator overwrites each run; don't
hand-edit them. The comparator finds this table by its header (the first one that starts
with `id` and has a `status` column), fills a column only under the names
shown here, and moves the best marker in `status`. The Decision log is
free-form prose: record the call and the reason, not just the winner.
```

with

````markdown
`id`, `parent`, `what changed`, `hypothesis`, and `status` are yours to write —
the reasoning trail no script can reconstruct after the fact. `ELPD` through
`psense` are metric columns the comparator overwrites each run; don't
hand-edit them. The comparator finds this table by its header (the first one that starts
with `id` and has a `status` column), fills a column only under the names
shown here (case and symbols included; a note says when none match), and moves
the best marker in `status`. The Decision log is free-form prose: record the
call and the reason, not just the winner.

**One criterion per ledger.** A ledger declares its criterion in one
`Criterion: <name>` line above the Variants table. A ledger without that line
reads as `elpd-loo`, so the ELPD ledger above needs none. The comparator
refuses a run whose mode does not match the criterion, and a variant whose
`scores.json` names another criterion. A score ledger swaps the ELPD metric
columns for `score`, `Δscore` and `SE(Δ)`:

```markdown
# Experiments — county-nowcast

Criterion: backtest-mse-h1

All variants below are scored on the SAME 24 forecast origins (required for the
paired difference — the comparator refuses variants with different unit keys).

| id (slug) | parent | what changed | hypothesis | score | Δscore | SE(Δ) | status |
|---|---|---|---|---|---|---|---|
| naive-last | — | last value carried forward | the floor every variant must beat | | | | candidate |
| ridge-lags | naive-last | ridge on 12 lags | lags carry the signal | | | | candidate |
| gbm-tuned | ridge-lags | tuned `HistGradientBoostingRegressor` via Optuna | lag effects are nonlinear | | | | candidate |

<!-- COMPARISON:BEGIN -->
(populated by compare_experiments.py --mode score)
<!-- COMPARISON:END -->
```
````

(5) Replace the whole `## The comparator` section (from its heading to the line before `## Fresh session per variant`) with:

````markdown
## The comparator

`scripts/compare_experiments.py` ranks the variants and (optionally) rewrites
the ledger's `<!-- COMPARISON -->` block in place. ELPD mode, the default,
loads each variant's `inference_data.nc` and ranks with `az.compare`. Score
mode (`--mode score`) loads each variant's `scores.json`, ranks by mean score
with the file's orientation, and reports each variant's paired difference from
the top variant (Δscore) with its standard error (SE(Δ)).

```bash
uv run <this-skill-dir>/scripts/compare_experiments.py \
  --analysis-dir <analysis-dir> --ledger <analysis-dir>/experiments.md --output comparison.json
uv run <this-skill-dir>/scripts/compare_experiments.py --mode score \
  --analysis-dir <analysis-dir> --ledger <analysis-dir>/experiments.md --output comparison.json
```

Without uv, run the same path with `python3` in an environment that has the
dependencies listed in the script's header. The header declares the
`h5netcdf`/`h5py` pair because `az.from_netcdf` needs a netCDF backend that
does not install transitively with `arviz`.

Run `--help` for the rest (`--folders` compares an explicit subset instead of
auto-discovering every `*/inference_data.nc`, or every `*/scores.json` in
score mode, under `--analysis-dir`). `comparison.json` records the `mode` and
the `criterion` beside the ranking.

Guardrails in both modes, before any ranking and before anything is written:
- **A `--ledger` path that is not a file**, or a ledger whose COMPARISON
  markers are unpaired, repeated or out of order → refused. The comparator
  rewrites the text from one BEGIN marker to the next END marker, so a stray
  marker would overwrite the ledger's prose.
- **A mode that does not match the ledger's criterion** → refused, naming the
  mode to run.

ELPD-mode guardrails:
- **A folder with no `inference_data.nc`** (named in `--folders`) → error
  naming it; ELPD mode ranks Bayesian fits only, and a variant without a fit
  belongs in a score ledger.
- **Missing `log_likelihood` group** → hard error naming the variant and the
  fix (refit with `az.from_numpyro(..., log_likelihood=True)`).
- **A log-likelihood that LOO cannot leave terms out of** → refused, with the
  remedy. One summed `numpyro.factor` has no observation dimension: store one
  term per time step. Several log-likelihood variables (one per source) must
  become one pointwise variable, summed over one shared observation dimension.
  `bayesian-workflow/references/state-space.md` shows both.
- **Mismatched observation counts across variants** → refused outright; LOO
  only compares predictions of the *same* held-out observations. The count is
  the number of pointwise log-likelihood terms.

Score-mode guardrails, each through `error:` with the variant and the fix:
- a folder with no `scores.json` (named in `--folders`);
- a `criterion` that differs from the ledger's or from another variant's;
- an `orientation` that differs across variants;
- unit keys that differ across variants (the paired difference compares the
  same folds or origins);
- a non-finite value, or fewer than two units.

After ranking:
- **High Pareto-k / other `az.compare` diagnostic warnings** (ELPD mode) →
  surfaced as a `warning` flag per variant in `comparison.json` and a `⚠` in
  the ledger table, not silently dropped.
- **A ledger row the comparator did not rank** (no fit or no `scores.json`, or
  left out of `--folders`) → named on stderr, in `comparison.json`'s
  `not_compared` list and under the COMPARISON table. The list is filled only
  when you pass `--ledger`. While one exists, the top row's status reads
  `**best among ELPD-compared variants**` (score mode:
  `**best among score-compared variants**`), not `**best**`.
- **A ranked variant with no ledger row, a row with more cells than the
  header, or a table with none of the mode's metric columns** → a note on
  stderr says so, and what it means for the best marker.
````

(6) In `## Stopping rule`, replace

```markdown
Stop iterating — don't keep chasing ELPD — when either holds:
```

with

```markdown
Stop iterating — don't keep chasing the criterion — when any of these holds:
```

and after the `**|ΔELPD| < 4**` bullet (it ends `no badly misspecified variant.`), add:

```markdown
- **Score mode: |Δscore| < 2·SE(Δ)** between the top variants — the
  difference is noise; ship the simpler one. The plain SE(Δ) is optimistic:
  training sets overlap across folds and origins, and h-step forecast errors
  are autocorrelated. For a high-stakes call, apply the corrections in
  `references/predictive-evaluation.md`.
```

(7) At the end of `## Relationship to bayesian-workflow`, after the `reporting.md` bullet, add:

```markdown
- **`references/predictive-evaluation.md`** (this skill) owns the *score-mode
  protocol*: backtests, the `scores.json` contract, the paired difference and
  its limits, benchmark baselines and proper scores. `bayesian-workflow`'s
  `model-comparison.md` shows how a Bayesian variant writes leave-future-out
  or blocked K-fold scores for it.
- **`tune-hyperparameters`** owns the *search* inside one model class; its
  winner graduates to a row here. **`evaluate-deep-learning`** owns neural
  runs and their experiment record.
```

Run: `grep -n 'non-ELPD mode' skills/track-model-experiments/SKILL.md`
Expected: no output.

- [ ] **Step 5: Rewrite track's README row (R23)**

In `README.md`, replace the whole line that starts `| [\`track-model-experiments\`](skills/track-model-experiments/) |` with:

```markdown
| [`track-model-experiments`](skills/track-model-experiments/) | Keep a ledger of model variants for each analysis, and rank the variants on one declared criterion. A human-written `experiments.md` records *what changed and why* across `v1 → v2 → v3`. A bundled `compare_experiments.py` ranks the variants and stamps the winner back into the ledger. ELPD mode loads each Bayesian variant's saved InferenceData, ranks the variants with `az.compare`, and extracts convergence diagnostics. Score mode ranks any variants (tabular cross-validation, forecast backtests, or Bayesian leave-future-out) from each variant's `scores.json` of per-fold or per-origin scores. It reports each variant's paired difference from the top variant and its standard error. The comparator refuses the inputs that make a comparison silently wrong. In ELPD mode, it refuses variants fit to different observations, a missing `log_likelihood` group, several log-likelihood variables (one per source in a multi-source model), or a log-likelihood with no pointwise terms. In score mode, it refuses mixed criteria or orientations, unit sets that differ, non-finite scores, or fewer than two units. In both modes, it refuses a mode that does not match the ledger's criterion. It names each ledger row that it could not rank. `references/predictive-evaluation.md` holds the backtest protocol, the paired-difference rule and its limits, benchmark baselines, and proper scores. The skill owns the variant ledger and the stopping rule. `bayesian-workflow`'s `model-comparison.md` owns the ELPD statistics. Neural runs stay with `evaluate-deep-learning`. |
```

- [ ] **Step 6: Run the gates**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_snippets.py skills/track-model-experiments/
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py; cd ..
uv run --python 3.13 --with pyyaml python build/check_conformance.py
uv run --python 3.13 python build/cc_guide/cli.py lint
```

Expected: every command exits 0. `check_frontmatter.py` confirms that the backticked `references/predictive-evaluation.md` exists. The scan of track edges prints the R22 set:

```bash
cd build && uv run --python 3.13 --with pytest --with pyyaml python -c "import test_runtime_support as t; print(sorted(e for e in t.referenced_dependencies() if 'skill:track-model-experiments' in e))"; cd ..
```

Expected: `[('skill:track-model-experiments', 'skill:bayesian-workflow'), ('skill:tune-hyperparameters', 'skill:track-model-experiments')]`. If the scan prints another edge, the new text has a path or a named-section reference that the plan did not intend. Reword it to a bare skill name, or stop and report it.

- [ ] **Step 7: Commit**

```bash
git add skills/track-model-experiments/references/predictive-evaluation.md skills/track-model-experiments/SKILL.md README.md install.py build/test_runtime_support.py
git commit -m "docs(track): add the predictive-evaluation reference and describe score mode" -m "Adds references/predictive-evaluation.md (spec R14), rewrites track's body for both modes (R21), and rewrites its README row, which now names the refusal of several log-likelihood variables (R23, plan-59 doc-nits part a). Moves track -> bayesian-workflow from install.py's DEPENDENCIES to SOFT_REFERENCES (R22)."
```

---

### Task 4: Time-series comparison in bayesian-workflow (R19)

**Files:**
- Modify: `skills/bayesian-workflow/references/model-comparison.md` (Contents list; a new section before `## Predictive accuracy on one model`)
- Modify: `build/snippet_preamble.py` (a `TIME_SERIES_FIXTURE` before the `# Per-block fixtures, keyed by the name a block selects.` comment; a `NAMED_FIXTURES` entry; the coverage paragraph that starts `Measured against the skill on`)
- Modify: `build/test_check_snippets.py` (append two tests)
- Modify: `build/test_runtime_support.py` (`SOFT_REFERENCES`)
- Modify: `NOTICE` (bayesian-workflow paragraph)

**Interfaces:**
- Consumes: Task 3's path `skills/track-model-experiments/references/predictive-evaluation.md`. The new section links to it. No lint checks links in reference files (`check_frontmatter.py` reads `SKILL.md` prose only), so Step 6 checks the target with `test -f`. Also Task 2's `scores.json` contract, which the blocks write.
- Produces: the section title "Time-series and forecast comparison". Task 3's reference already cites that title.

- [ ] **Step 1: Write the failing tests**

Append to `build/test_check_snippets.py`:

```python


TIME_SERIES_BLOCKS = (
    ('references/model-comparison.md', 'lfo = azs.lfo_cv(idata_ts'),
    ('references/model-comparison.md', 'kf = azs.loo_kfold(idata_ts'),
)


def test_the_time_series_fixture_copies_the_doc_setup_block():
    '''The time_series fixture embeds model-comparison.md's AR(1) setup block
    verbatim, so the LFO and K-fold blocks run against the documented wrapper.
    The setup block also runs on its own, without the fixture.'''
    from snippet_preamble import NAMED_FIXTURES
    block = _skill_block('references/model-comparison.md', 'class AR1Wrapper')
    assert block.code.strip() == NAMED_FIXTURES['time_series'].code.strip(), (
        'snippet_preamble.TIME_SERIES_FIXTURE drifted from model-comparison.md')
    assert check_snippets.fixture_name(block) is None
    assert check_snippets.runnable(block), check_snippets._unrunnable_reason(block)


def test_the_time_series_blocks_select_the_time_series_fixture():
    '''A block the gate cannot admit only gets a WARN, so pin that both route
    blocks are admitted through the fixture and --run executes them.'''
    for relpath, needle in TIME_SERIES_BLOCKS:
        block = _skill_block(relpath, needle)
        assert check_snippets.fixture_name(block) == 'time_series', needle
        assert check_snippets.runnable(block), check_snippets._unrunnable_reason(block)
```

Run: `cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q test_check_snippets.py -k time_series; cd ..`
Expected: `2 failed`, each with `StopIteration` (no block holds the needle yet).

- [ ] **Step 2: Add the section to `model-comparison.md`**

In the `## Contents` list, after `- Pointwise comparison`, add the line `- Time-series and forecast comparison: LFO and blocked K-fold`.

Insert this section directly before the line `## Predictive accuracy on one model: \`loo_expectations\`, \`loo_metrics\`, \`loo_r2\``, with one blank line after it:

````markdown
## Time-series and forecast comparison

PSIS-LOO leaves out one observation and predicts it from all the others, past and future
alike. That is the right question for interpolation and for structure: which likelihood, which
hierarchy, which covariates explain the data. It is the wrong question for a forecast
decision. A nowcast model predicts the next period from the past only, and LOO lets it lean on
neighbours from a future it will not have.

Rank forecasting variants by one of two routes:

- **Leave-future-out (LFO).** Fit on the data up to a forecast origin, score the next
  `forecast_horizon` observations, move the origin forward, repeat (Bürkner, Gabry & Vehtari
  2020; the loo package's LFO vignette, https://mc-stan.org/loo/articles/loo2-lfo.html).
  `azs.lfo_cv` with `method="approx"` carries the last fit forward by PSIS and refits only
  when Pareto k passes `k_threshold`.
- **Blocked K-fold with a joint log score.** Leave out one contiguous block of time at a
  time, refit on the rest, and score each block as a whole. `azs.loo_kfold` with a `folds`
  array does the refits. It scores each held-out step on its own, so the joint score of a
  block takes one more step (below). It suits a model whose dependence is short-range, so
  that a block's neighbours on both sides leak little (CV-FAQ,
  https://users.aalto.fi/~ave/CV-FAQ.html).

Both routes refit the model, so both need a `SamplingWrapper`: four methods that tell ArviZ
how to split the data, refit, convert a fit, and score held-out terms. This one wraps an AR(1)
model. Each of its log-likelihood terms scores `y[t]` given the observed `y[t-1]`, so a refit
can leave out any set of steps:

```python
# An AR(1) series and a wrapper that refits it on a subset of time steps.
# Each term scores y[t] given the observed y[t-1], so a refit can leave out any
# set of steps; lfo_cv and loo_kfold both call these four methods.
T = 80
rng_ts = np.random.default_rng(1)
series = np.zeros(T)
for t in range(1, T):
    series[t] = 0.7 * series[t - 1] + rng_ts.normal(0, 0.5)
y_lag, y_now = series[:-1], series[1:]
steps = np.arange(1, T)                      # the time coordinate of each term

def ar1(y_lag, y=None):
    mu = numpyro.sample("mu", dist.Normal(0, 2))
    phi = numpyro.sample("phi", dist.Uniform(-1, 1))
    s = numpyro.sample("s", dist.HalfNormal(1))
    with numpyro.plate("time", y_lag.shape[0]):
        numpyro.sample("y", dist.Normal(mu + phi * (y_lag - mu), s), obs=y)

def fit_ar1(y_lag, y, key=jax.random.PRNGKey(3)):
    run = MCMC(NUTS(ar1), num_warmup=200, num_samples=200, num_chains=1, progress_bar=False)
    run.run(key, y_lag, y=y)
    return run

idata_ts = az.from_numpyro(fit_ar1(y_lag, y_now), log_likelihood=True,
                           coords={"time": steps}, dims={"y": ["time"]})

class AR1Wrapper(azs.SamplingWrapper):
    def sel_observations(self, idx):
        idx = np.asarray(idx)
        keep = np.setdiff1d(np.arange(y_now.size), idx)
        return ({"y_lag": y_lag[keep], "y": y_now[keep]},
                {"y_lag": y_lag[idx], "y": y_now[idx], "time": steps[idx]})

    def sample(self, train):
        return fit_ar1(train["y_lag"], train["y"])

    def get_inference_data(self, run):
        return az.from_numpyro(run)

    def log_likelihood__i(self, test, idata_i):
        post = idata_i.posterior
        mu, phi, s = (post[name].values[:, :, None] for name in ("mu", "phi", "s"))
        mean = mu + phi * (test["y_lag"] - mu)
        ll = dist.Normal(mean, s).log_prob(test["y"])        # (chain, draw, n_test)
        return xr.DataArray(np.asarray(ll), dims=["chain", "draw", "time"],
                            coords={"time": test["time"]})

wrapper = AR1Wrapper(model=ar1, idata_orig=idata_ts)
```

Leave-future-out, one step ahead from origin 50 on. Each forecast origin is one unit:

```python fixture=time_series
import json
from pathlib import Path

lfo = azs.lfo_cv(idata_ts, wrapper, min_observations=50, forecast_horizon=1,
                 pointwise=True)
print(lfo.elpd, lfo.se, lfo.n_refits)        # n_refits: origins where PSIS gave out

units = {f"origin-{t}": float(v)
         for t, v in zip(lfo.elpd_i["time"].values, lfo.elpd_i.values)}
Path("ar1").mkdir(exist_ok=True)
Path("ar1/scores.json").write_text(json.dumps(
    {"criterion": "lfo-elpd-h1", "orientation": "higher", "units": units}))
```

With `forecast_horizon` above 1, `lfo_cv` scores the next steps jointly, each one given the
observed steps before it. Its docstring names the other convention, which simulates those
steps instead; results from the two do not compare.

Blocked K-fold, five contiguous blocks. Each block is one unit:

```python fixture=time_series
import json
from pathlib import Path

from scipy.special import logsumexp

folds = np.repeat(np.arange(1, 6), int(np.ceil(y_now.size / 5)))[: y_now.size]
kf = azs.loo_kfold(idata_ts, wrapper, folds=folds, save_fits=True)

# loo_kfold scores each step on its own. The joint log score of a block sums the
# block's terms under each draw, then averages the likelihood over draws.
units = {}
for k, saved in kf.fold_fits.items():
    _, test = wrapper.sel_observations(saved["test_indices"])
    per_draw = wrapper.log_likelihood__i(test, saved["fit"]).values.sum(axis=-1).ravel()
    units[f"block-{k}"] = float(logsumexp(per_draw) - np.log(per_draw.size))
Path("ar1").mkdir(exist_ok=True)
Path("ar1/scores.json").write_text(json.dumps(
    {"criterion": "kfold5-joint-elpd", "orientation": "higher", "units": units}))
```

**Ranking the variants.** `az.compare` ranks PSIS-LOO results only. To rank LFO or
blocked-K-fold variants in an experiments ledger, write each variant's per-unit scores to its
own `scores.json`, as both blocks above do, and rank them with track-model-experiments' score
mode. [track-model-experiments/references/predictive-evaluation.md](../../track-model-experiments/references/predictive-evaluation.md)
gives the file's contract, the paired-difference rule, and its limits. Every variant in one
ledger uses the same origins or blocks and the same criterion string.
````

Do not write `values[..., None]` in the setup block: the gate reads any `...` as an elision and would skip the block (found at plan time).

- [ ] **Step 3: Add the `time_series` fixture**

In `build/snippet_preamble.py`, directly before the line `# Per-block fixtures, keyed by the name a block selects. Only the blocks that`, add the fixture below. Its body is the setup block's code from Step 2, character for character. The pin test from Step 1 compares the two, so if you edit one, edit the other.

```python
# Copied VERBATIM from references/model-comparison.md (the AR(1) setup block of
# "Time-series and forecast comparison"); the LFO and blocked K-fold blocks select
# it, and test_the_time_series_fixture_copies_the_doc_setup_block pins the two equal.
TIME_SERIES_FIXTURE = '''
# An AR(1) series and a wrapper that refits it on a subset of time steps.
# Each term scores y[t] given the observed y[t-1], so a refit can leave out any
# set of steps; lfo_cv and loo_kfold both call these four methods.
T = 80
rng_ts = np.random.default_rng(1)
series = np.zeros(T)
for t in range(1, T):
    series[t] = 0.7 * series[t - 1] + rng_ts.normal(0, 0.5)
y_lag, y_now = series[:-1], series[1:]
steps = np.arange(1, T)                      # the time coordinate of each term

def ar1(y_lag, y=None):
    mu = numpyro.sample("mu", dist.Normal(0, 2))
    phi = numpyro.sample("phi", dist.Uniform(-1, 1))
    s = numpyro.sample("s", dist.HalfNormal(1))
    with numpyro.plate("time", y_lag.shape[0]):
        numpyro.sample("y", dist.Normal(mu + phi * (y_lag - mu), s), obs=y)

def fit_ar1(y_lag, y, key=jax.random.PRNGKey(3)):
    run = MCMC(NUTS(ar1), num_warmup=200, num_samples=200, num_chains=1, progress_bar=False)
    run.run(key, y_lag, y=y)
    return run

idata_ts = az.from_numpyro(fit_ar1(y_lag, y_now), log_likelihood=True,
                           coords={"time": steps}, dims={"y": ["time"]})

class AR1Wrapper(azs.SamplingWrapper):
    def sel_observations(self, idx):
        idx = np.asarray(idx)
        keep = np.setdiff1d(np.arange(y_now.size), idx)
        return ({"y_lag": y_lag[keep], "y": y_now[keep]},
                {"y_lag": y_lag[idx], "y": y_now[idx], "time": steps[idx]})

    def sample(self, train):
        return fit_ar1(train["y_lag"], train["y"])

    def get_inference_data(self, run):
        return az.from_numpyro(run)

    def log_likelihood__i(self, test, idata_i):
        post = idata_i.posterior
        mu, phi, s = (post[name].values[:, :, None] for name in ("mu", "phi", "s"))
        mean = mu + phi * (test["y_lag"] - mu)
        ll = dist.Normal(mean, s).log_prob(test["y"])        # (chain, draw, n_test)
        return xr.DataArray(np.asarray(ll), dims=["chain", "draw", "time"],
                            coords={"time": test["time"]})

wrapper = AR1Wrapper(model=ar1, idata_orig=idata_ts)
'''

```

`xr` comes from the preamble (`import xarray as xr`), as do `np`, `jax`, `numpyro`, `dist`, `MCMC`, `NUTS`, `az` and `azs`.

In `NAMED_FIXTURES`, after the `'comparison'` entry, add:

```python
    'time_series': Fixture(code=TIME_SERIES_FIXTURE, variables=frozenset()),
```

`variables` is empty because no block names a fixture variable as a string literal on an InferenceData group.

- [ ] **Step 4: Run the tests and snippet Tiers 1–3**

```bash
cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml --with "arviz>=1.0" --with arviz-base --with arviz-stats --with arviz-plots --with numpyro --with jax --with matplotlib python -m pytest -q test_check_snippets.py; cd ..
uv run --python 3.13 python build/check_snippets.py skills/
uv run --python 3.13 --with "arviz>=1.0" --with arviz-base --with arviz-stats --with arviz-plots --with numpyro --with jax python build/check_snippets.py --api skills/bayesian-workflow/
uv run --python 3.13 --with 'arviz==1.3.0' --with arviz-base --with 'arviz-stats==1.3.3' --with 'arviz-plots==1.3.2' --with 'numpyro==0.22.0' --with 'jax==0.12.0' --with numpy --with matplotlib python build/check_snippets.py --run skills/bayesian-workflow/
```

Expected: the pytest run passes, including the two new tests and `test_every_named_fixture_var_is_carried_by_the_fixtures_idata[time_series]` (53 passed in the plan-time scratch run, 2 more than before). Each `check_snippets.py` run exits 0. On the Tier 3 run, no `WARN` line names a `model-comparison.md` line inside the new section. The two remaining `model-comparison.md` WARNs are the existing `loo_expectations` and `bayes_factor` blocks. In zsh, write each `--with` on the command line as shown. Never put the flags in a variable: zsh does not word-split `$VAR`, and uv then rejects the run.

- [ ] **Step 5: Re-measure the preamble's coverage claim**

Write this to `/tmp/p65-measure/measure.py` (outside the repo):

```python
'''Re-measure snippet_preamble.py's coverage claim for skills/bayesian-workflow.'''
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1] + '/build')
import check_snippets as c

paths = sorted(Path(sys.argv[1], 'skills/bayesian-workflow').rglob('*.md'))
blocks = [b for p in paths for b in c.iter_code_blocks(p.read_text())]
reasons = collections.Counter()
fixture_runs = collections.Counter()
for b in blocks:
    reason = c._unrunnable_reason(b)
    if not reason:
        fixture_runs[c.fixture_name(b) or '(preamble only)'] += 1
    elif c.is_exempt(b):
        reasons['norun/noparse-exempt'] += 1
    else:
        reasons[re.sub(r' \[.*| \(.*|: .*', '', reason)] += 1
print('blocks', len(blocks), '| parse errors', sum(len(c.parse_errors(p)) for p in paths))
print('runs', sum(fixture_runs.values()), dict(fixture_runs))
print('not run', dict(reasons))
```

Run: `REPO="$(git rev-parse --show-toplevel)" && cd /tmp/p65-measure && uv run --python 3.13 python measure.py "$REPO"; cd -`

Expected at plan time (base `7603e69` plus this task): `blocks 83 | parse errors 0`, `runs 39 {'(preamble only)': 32, 'comparison': 5, 'time_series': 2}`, `not run {'elided with `...`': 6, 'unbound names': 18, 'norun/noparse-exempt': 4, 'needs fixture variables': 9, 'model-body fragment': 7}`. If plan 64 landed first, the numbers differ: use the script's numbers.

In `build/snippet_preamble.py`'s docstring, replace the paragraph that starts `Measured against the skill on 2026-10-19` and ends `model-criticism.md's expected_calibration_error and ranked_probability_score).` with this text, with the measured numbers and today's date:

```text
Measured against the skill on <YYYY-MM-DD> (re-measure whenever this file or
the skill changes; a stale coverage claim is worse than none): 83 fenced
python blocks, all 83 parse. 4 are norun-exempt and 40 are advisory --
18 name-incomplete, 9 naming variables outside the fixtures, 7 model-body
fragments, 6 elided with `...`. That leaves 39 blocks that --run executes,
5 of them through the `comparison` fixture and 2 through `time_series`. 3 of
the 39 are def-only: they define functions they never call, so they show only
that the definitions compile (diagnostics.md's run_diagnostics,
hierarchical.md's centered, model-criticism.md's expected_calibration_error
and ranked_probability_score).
```

- [ ] **Step 6: Add the soft reference and the NOTICE line**

In `build/test_runtime_support.py`'s `SOFT_REFERENCES`, add this entry directly above the `# Says where the plan-completion protocol retires specs; never runs it.` entry (the first entry, so the set stays in order by source):

```python
  # Points a forecast ranking at track's score-mode reference; the time-series
  # section's snippets run without track installed.
  ('skill:bayesian-workflow', 'skill:track-model-experiments'),
```

In `NOTICE`, in the bayesian-workflow paragraph, insert these lines directly before the line `    The skill cites Gelman, Vehtari, McElreath et al. (2026), "Bayesian`:

```text
    references/model-comparison.md's "Time-series and forecast
    comparison" section is original text. It documents arviz_stats'
    lfo_cv and loo_kfold as established by running them against
    arviz-stats 1.3.3, and it cites by URL only the loo R package's
    leave-future-out vignette (Bürkner, Gabry and Vehtari; the package
    is licensed GPL (>= 3)) and the CV-FAQ. It reproduces no text or
    code from either.
```

Run:

```bash
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py; cd ..
uv run --python 3.13 python build/check_provenance.py
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
test -f skills/bayesian-workflow/references/../../track-model-experiments/references/predictive-evaluation.md && echo link-ok
```

Expected: the first three exit 0, and the last prints `link-ok`. The drift test now finds `('skill:bayesian-workflow', 'skill:track-model-experiments')` and excuses it.

- [ ] **Step 7: Commit**

```bash
git add skills/bayesian-workflow/references/model-comparison.md build/snippet_preamble.py build/test_check_snippets.py build/test_runtime_support.py NOTICE
git commit -m "docs(bayesian-workflow): add time-series and forecast comparison" -m "Adds the R19 section to model-comparison.md: PSIS-LOO for interpolation and structure, LFO or blocked K-fold with a joint log score for forecast decisions, with arviz-stats snippets that write scores.json for track's score mode. A time_series named fixture copies the AR(1) setup block so snippet Tier 3 runs both route blocks, and two tests pin it. Records the provenance in NOTICE and the bayesian-workflow -> track soft reference (R22)."
```

---

### Task 5: track's description and its micro-test (R20, V1 track arm)

The description ships only after the V1 track arm passes. Until then, the edit stays uncommitted in the working tree.

**Files:**
- Modify: `skills/track-model-experiments/SKILL.md` (frontmatter `description` only)
- Create: `specs/verification/65-track-description-microtest.md`
- Kit (outside the repo): `~/.cache/agent-skills/scratch/plan65-micro/`

**Interfaces:**
- Consumes: Tasks 2–4 (the description names what they built).
- Produces: nothing a later task reads.

- [ ] **Step 1: Write the draft description**

Replace the frontmatter `description: >` block (the folded lines under it, up to `license: MIT`) with:

```yaml
description: >
  Use when iterating over several model variants and losing track of them — Bayesian
  variants that try different priors, likelihoods, or hierarchical structure, or
  tabular-CV and forecast-backtest variants scored on one shared criterion — and
  unable to reconstruct what changed or why one won. Trigger on: keeping an
  experiment log or ledger of model runs, "which model fits best", ranking variants
  by ELPD/LOO, ranking variants by cross-validation fold scores or backtest scores,
  leave-future-out (LFO) comparison of forecasting models, comparing variants against
  a naive or seasonal-naive benchmark baseline, recording what changed between model
  versions, deciding which variant to ship, or knowing when to stop iterating. Sits
  above per-variant analysis folders and complements bayesian-workflow's model
  comparison. Not for tuning continuous hyperparameters (that is
  tune-hyperparameters). Not for neural runs or checkpoints (that is
  evaluate-deep-learning).
```

(959 characters once folded, under the 1,024 cap.)

Run: `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`
Expected: exit 0. Do not commit yet.

- [ ] **Step 2: Build the kit**

Record the CLI version: `claude --version` (2.1.304 at plan time). Write `~/.cache/agent-skills/scratch/plan65-micro/run_microtest.py`:

```python
#!/usr/bin/env python3
# /// script
# requires-python = '>=3.12'
# dependencies = ['pyyaml>=6.0']
# ///
'''Plan 65 V1, track arm: a decision-only routing micro-test of track's description.

Each rep is one `claude -p` call with no tools, no MCP servers and no advisor, run
from its own new folder under /tmp/p65micro/. The system prompt lists five skills
by name and description, in name order. The control arm gives track's description
at the base commit, and the variant arm gives the working tree's draft. The four
probes' descriptions come from the base commit in both arms.

Usage: uv run run_microtest.py "$REPO" <arm: control|variant|pilot> [--reps N]
'''
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

KIT = Path(__file__).resolve().parent
BASE = '7603e69'
TARGET = 'track-model-experiments'
PROBES = ('bayesian-workflow', 'evaluate-deep-learning', 'recommend-probabilistic-model',
          'tune-hyperparameters')
PROMPTS = {
    'T1-cv-ledger': (
        "I've fit five variants for a county-level employment panel: two ridge "
        'regressions and three gradient-boosting models, each scored with the same '
        '5-fold GroupKFold MSE. I keep forgetting which feature set each one used and '
        'why I dropped two of them. I want one record of the variants, ranked on those '
        'fold scores, so I can decide which to ship.'),
    'T2-bayes-lfo': (
        'I have three NumPyro state-space nowcast models: local level, local linear '
        'trend, and AR(2) errors. I want to rank them by their leave-future-out log '
        'score at a one-month horizon and keep a record of what each variant changed.'),
    'T3-elpd-variants': (
        "I'm on variant 6 of a hierarchical NumPyro model of weekly store sales. Each "
        "variant changed a prior or the pooling, and I've lost track of what v3 changed "
        'and why v4 was dropped. I want the variants ranked by ELPD with the reasons '
        'written down.'),
    'N-bayesian-workflow': (
        'I fitted one hierarchical NumPyro model of store sales. Max R-hat is 1.04 and '
        '30 of 4000 transitions diverged. How do I check this fit and report it?'),
    'N-evaluate-deep-learning': (
        'I trained three transformer checkpoints for demand forecasting with different '
        'random seeds. I want to compare them on a held-out test period and decide '
        'which checkpoint to ship.'),
    'N-tune-hyperparameters': (
        'I need to choose the learning rate, max depth and L2 penalty for a '
        'gradient-boosting nowcast. I plan an Optuna search with rolling-origin '
        'cross-validation and must not leak future data.'),
    'N-recommend-probabilistic-model': (
        'I have monthly counts of business births by county. They are overdispersed '
        'and a third are zero. Which kind of model should I fit?'),
}


def _description(text: str) -> str:
    front = text.split('---\n')[1]
    return ' '.join(yaml.safe_load(front)['description'].split())


def base_description(repo: Path, name: str) -> str:
    show = subprocess.run(['git', '-C', str(repo), 'show', f'{BASE}:skills/{name}/SKILL.md'],
                          capture_output=True, text=True, check=True)
    return _description(show.stdout)


def system_prompt(repo: Path, arm: str) -> str:
    target = (_description((repo / 'skills' / TARGET / 'SKILL.md').read_text())
              if arm == 'variant' else base_description(repo, TARGET))
    listing = {TARGET: target, **{n: base_description(repo, n) for n in PROBES}}
    lines = [f'- {n}: {listing[n]}' for n in sorted(listing)]
    return ('You are a coding agent deciding which skill to load for a task. '
            'Available skills:\n' + '\n'.join(lines) + '\nReply with only the name of '
            'the one skill you would load first, or none.')


def run_rep(system: Path, prompt: str, folder: Path) -> dict:
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    env = {**os.environ, 'CLAUDE_CODE_DISABLE_ADVISOR_TOOL': '1'}
    proc = subprocess.run(
        ['claude', '-p', '--model', 'sonnet', '--tools', '', '--strict-mcp-config',
         '--no-session-persistence', '--system-prompt-file', str(system),
         '--output-format', 'stream-json', '--verbose', prompt],
        cwd=folder, env=env, capture_output=True, text=True, timeout=300)
    rec = {'returncode': proc.returncode, 'raw': proc.stdout}
    for line in proc.stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get('type') == 'system' and event.get('subtype') == 'init':
            rec.update(tools=event.get('tools'), mcp=event.get('mcp_servers'),
                       model=event.get('model'))
        if event.get('type') == 'result':
            usage = event.get('usage') or {}
            rec.update(answer=(event.get('result') or '').strip(),
                       cost=event.get('total_cost_usd'),
                       iterations=[i.get('type') for i in usage.get('iterations') or []])
    return rec


def routed(answer: str) -> bool:
    return answer.strip().strip('`*. ').lower() == TARGET


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('repo', type=Path)
    ap.add_argument('arm', choices=('control', 'variant', 'pilot'))
    ap.add_argument('--reps', type=int, default=5)
    args = ap.parse_args()
    arm = 'control' if args.arm == 'pilot' else args.arm
    system = KIT / f'system-{arm}.txt'
    system.write_text(system_prompt(args.repo, arm))
    prompts = dict(list(PROMPTS.items())[:1]) if args.arm == 'pilot' else PROMPTS
    reps = 1 if args.arm == 'pilot' else args.reps
    results, voids = [], 0
    for pid, prompt in prompts.items():
        for rep in range(1, reps + 1):
            for attempt in range(3):
                rec = run_rep(system, prompt, Path('/tmp/p65micro') / f'{args.arm}-{pid}-{rep}')
                if rec['returncode'] == 0 and rec.get('answer') is not None:
                    break
                voids += 1
            clean = rec.get('tools') == [] and rec.get('mcp') == [] and all(
                i == 'message' for i in rec.get('iterations', []))
            (KIT / 'raw').mkdir(exist_ok=True)
            (KIT / 'raw' / f'{args.arm}-{pid}-{rep}.jsonl').write_text(rec.pop('raw'))
            results.append({'arm': args.arm, 'prompt': pid, 'rep': rep, 'clean': clean,
                            'routed': routed(rec.get('answer', '')), **rec})
            print(f"{args.arm} {pid} {rep}: {rec.get('answer')!r} clean={clean}")
    (KIT / f'results-{args.arm}.json').write_text(json.dumps(
        {'voids': voids, 'results': results}, indent=2))
    print('cost', round(sum(r.get('cost') or 0 for r in results), 3), 'voids', voids)
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

The prompts and the pass rule are fixed here, before any arm runs. The trigger prompts follow spec V1 (a CV-ranked tabular ledger, a Bayesian LFO ranking, ELPD variants). There is one near-miss for each probe.

- [ ] **Step 3: Pilot the isolation, then run both arms**

```bash
REPO="$(git rev-parse --show-toplevel)"
cd ~/.cache/agent-skills/scratch/plan65-micro && uv run run_microtest.py "$REPO" pilot
```

Expected: one line ending `clean=True`. `results-pilot.json` shows `"tools": []` and `"mcp": []`. If `clean` is False, stop: the run is not isolated (see the memory note on micro-test isolation channels), so fix the flags before spending more.

Then check that the four probe descriptions at HEAD still equal those at the base commit:

```bash
for n in bayesian-workflow evaluate-deep-learning recommend-probabilistic-model tune-hyperparameters; do git diff --quiet 7603e69 HEAD -- skills/$n/SKILL.md && echo "$n same" || echo "$n CHANGED"; done
```

Record the result in the record's Design section. A `CHANGED` line means plan 64 (or another change) moved a probe description. The kit still uses the base text, as the spec asks ("taken from the files at plan time"). Note the drift in the record.

```bash
uv run run_microtest.py "$REPO" control
uv run run_microtest.py "$REPO" variant
```

Expected: 35 reps per arm, about $0.02 each (about $1.50 in total at plan time).

- [ ] **Step 4: Grade by hand against the pre-registered rule**

Read every answer in `results-control.json` and `results-variant.json`. The script's `routed` flag is a convenience. Grade each answer yourself, and quote any answer that is more than a bare skill name.

Pass rule (spec V1, fixed before the runs):
1. On each trigger prompt (T1–T3), the variant's count of answers that route to `track-model-experiments` is at least the control's count minus 1.
2. On each near-miss prompt (N-…), the variant's count that routes to `track-model-experiments` is at most the control's count: no near-miss newly routes to the target.
3. Every rep is clean (`tools` and `mcp` empty, only `message` iterations). A rep that is not clean is void: rerun it and count it.

If the variant fails, reword the description once. Aim at the failing prompt and keep every R20 trigger. Then rerun the variant arm only, and record both runs. If the second run also fails, stop and bring both runs to your human partner. The description does not ship on a failed run.

- [ ] **Step 5: Write the record**

Create `specs/verification/65-track-description-microtest.md` in the shape of `specs/verification/59-regime-b-router-microtest.md`:

- the title `# Plan 65 micro-test: track-model-experiments' description (V1, track arm)`;
- a header line with the date, the model from the init record, the CLI version, the kit path and the total cost;
- **Design:** the isolation flags, the base commit, the arms, the listing (five skills in name order), the probe-drift check from Step 3, and the pass rule quoted from Step 4;
- **Prompts:** the seven prompts, quoted in full;
- **Results:** a table of prompt × arm with the routed count out of 5, and whether each rule held;
- **Per rep:** a table with arm, prompt, rep and answer (an answer is a skill name, so quote it whole);
- **Verdict:** pass or fail, with any rewording and its rerun.

Use generic wording only. The prompts are already public-safe.

- [ ] **Step 6: Commit**

Commit only when the record's verdict is pass:

```bash
git add skills/track-model-experiments/SKILL.md specs/verification/65-track-description-microtest.md
git commit -m "docs(track): widen the description to score-mode variants" -m "Rewrites track-model-experiments' description for Bayesian, tabular-CV and backtest variants on one criterion (spec R20). The V1 track arm passed against the base description; the record is specs/verification/65-track-description-microtest.md."
```

---

### Task 6: Prove R18, then tidy the existing tests (deferred part (f))

**Files:**
- Modify: `skills/track-model-experiments/scripts/test_compare_experiments.py` (existing helpers and tests)

**Interfaces:**
- Consumes: the final comparator (Task 2) and the Task 1 helper `_table_cells`.
- Produces: nothing a later task reads.

- [ ] **Step 1: Run the base-commit tests against the final comparator (R18, D1)**

```bash
rm -rf /tmp/p65-r18 && mkdir -p /tmp/p65-r18
cp skills/track-model-experiments/scripts/compare_experiments.py /tmp/p65-r18/
git show 7603e69:skills/track-model-experiments/scripts/test_compare_experiments.py > /tmp/p65-r18/test_compare_experiments.py
cd /tmp/p65-r18 && uv run --python 3.13 --with pytest --with numpy --with polars --with arviz --with numpyro --with h5netcdf --with h5py python -m pytest -q -p no:cacheprovider test_compare_experiments.py; cd -
```

Expected: every base-commit test passes, with none skipped (26 tests at plan time). The test file sits next to the final script because it locates the script with `Path(__file__).parent`. Record the summary line for Task 7. If any test fails, stop: ELPD behaviour changed, and Tasks 1–2 must be fixed first.

- [ ] **Step 2: Make the (f) edits to existing helpers and tests**

(1) Replace `_row`:

```python
def _row(text, variant_id):
    return next(ln for ln in text.splitlines() if ln.startswith(f'| {variant_id} '))
```

with

```python
def _row(text, variant_id):
    '''A Variants-table row, read from the table itself, so a COMPARISON block or
    another table above it cannot shadow the row.'''
    lines = text.splitlines()
    _, _, rows = compare_experiments._variants_table(lines)
    return next(lines[i] for i in rows if compare_experiments._cells(lines[i])[0] == variant_id)
```

(2) Replace `_table_cells`'s body so that it reuses `_row`:

```python
def _table_cells(text, variant_id):
    '''A Variants-table row's cells, read through the comparator's own parser.'''
    return compare_experiments._cells(_row(text, variant_id))
```

(3) Delete the helper `_unescaped_cells` (the `def _unescaped_cells(row):` function and its two blank lines after it). In `test_an_escaped_pipe_stays_inside_its_cell`, replace `    cells = _unescaped_cells(after)` with `    cells = compare_experiments._cells(after)`.

(4) Make the file's f-strings single-quoted. Replace these lines:

```python
    assert elpd == f"{rank['m-intercept']['elpd']:.1f}"
    assert d_elpd == f"{rank['m-intercept']['elpd_diff']:.1f}"
    assert rhat == f"{rank['m-intercept']['max_rhat']:.3f}"
```

with

```python
    assert elpd == f'{rank["m-intercept"]["elpd"]:.1f}'
    assert d_elpd == f'{rank["m-intercept"]["elpd_diff"]:.1f}'
    assert rhat == f'{rank["m-intercept"]["max_rhat"]:.3f}'
```

and these:

```python
    assert cells[4] == f"{rank['m-intercept']['elpd']:.1f}"
    assert cells[5] == f"{rank['m-intercept']['elpd_diff']:.1f}"
```

with

```python
    assert cells[4] == f'{rank["m-intercept"]["elpd"]:.1f}'
    assert cells[5] == f'{rank["m-intercept"]["elpd_diff"]:.1f}'
```

Run: `grep -n 'f"' skills/track-model-experiments/scripts/test_compare_experiments.py`
Expected: no output.

(5) At the end of `test_a_row_with_more_cells_than_the_header_is_left_alone`, add:

```python
    full = compare_experiments._cells(_row(ledger.read_text(), 'm-full'))
    assert full[-1] == '**best**'                            # the other row still gets the marker
    assert full[4] and full[5]                               # and its metric cells
```

- [ ] **Step 3: Run the suite**

Run: `uv run --python 3.13 python build/run_suites.py track-model-experiments`
Expected: every test passes, with the same count as after Task 2 (this task adds no test).

- [ ] **Step 4: Commit**

```bash
git add skills/track-model-experiments/scripts/test_compare_experiments.py
git commit -m "test(track): tidy the comparator tests (plan 59 part f)" -m "Scopes _row to the Variants table, reuses the comparator's _cells instead of a copied regex, single-quotes the f-strings, and asserts that an over-wide row leaves the other rows' marker and metric cells in place. The base-commit test file passed unedited against the final comparator before these edits (D1)."
```

---

### Task 7: Stage gates

**Files:** none changed, unless a gate fails.

- [ ] **Step 1: Run every V3 Stage B gate and the commit lints**

```bash
uv run --python 3.13 python build/run_suites.py track-model-experiments
uv run --python 3.13 python build/run_suites.py build --extras
uv run --python 3.13 python build/check_snippets.py skills/
uv run --python 3.13 --with "arviz>=1.0" --with arviz-base --with arviz-stats --with arviz-plots --with numpyro --with jax python build/check_snippets.py --api skills/bayesian-workflow/
uv run --python 3.13 --with 'arviz==1.3.0' --with arviz-base --with 'arviz-stats==1.3.3' --with 'arviz-plots==1.3.2' --with 'numpyro==0.22.0' --with 'jax==0.12.0' --with numpy --with matplotlib python build/check_snippets.py --run skills/bayesian-workflow/
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies; cd ..
uv run --python 3.13 --with pyyaml python build/check_conformance.py
build/run_commit_lints.sh
```

Expected: each exits 0. The `build` suite may skip four `test_verify_citations.py` tests for the missing `build/.scratch/`, as its notes say.

- [ ] **Step 2: Check the scope fence and the roadmap Exit**

```bash
git diff --stat 7603e69 HEAD -- skills/tune-hyperparameters skills/develop-testing-strategy skills/validate-data skills/recommend-visualization skills/recommend-probabilistic-model
```

Expected: no output.

Check each item of the roadmap's Stage 1 Exit, and write the evidence into the execution ledger:
- the track suite passes, and the base-commit tests passed unedited (Task 6, Step 1), plus the R24 tests and a test for each hardening part (a)–(e);
- snippet Tiers 1–3 pass on `model-comparison.md`;
- the dependency-drift test, `check_conformance.py` and `build/run_commit_lints.sh` pass;
- `specs/verification/65-track-description-microtest.md` exists with a pass verdict;
- the deferred-item ticks are left to the Plan Completion Protocol (step 3). It ticks the hardening item (`→ done in plan 65`) and adds a progress note to the doc-nits item: part (a) is done in plan 65, and the item stays open for part (b), which Stage 2 closes.

Then run the Plan Completion Protocol (writing-plans). Its step 3a writes `## Handoff to later stages` for Stage 2 (R7's pointer path and the R11 `scores.json` contract as built) and Stage 3 (the reference path).
