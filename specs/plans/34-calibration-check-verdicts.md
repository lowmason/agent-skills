# calibration_check Verdicts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `skills/bayesian-workflow/scripts/calibration_check.py` computes its PIT values once, judges them with the `pot_c` uniformity test its saved figures print, draws both figures from the same values, and names every failing calibration component; `check_diagnostics.py` routes one next step per named component.

**Architecture:** A pure rule function, `assess_pit(pit, ci_prob)`, judges a 1-D PIT array with `pot_c` on the PIT and on its coverage fold, plus a t-test on the mean PIT that only explains a failed PIT test, and returns the eleven-key assessment (Task 1). `pit_values(dt, var_name, use_loo)` owns the PIT: a seeded, cell-randomized rank PIT for PPC and `loo_pit(pareto_pit=True)` for LOO (Task 2). `main()` computes the PIT once and hands the same array to `assess_pit` and to both `save_pit_plot` calls, which draw with public `azp.plot_ecdf_pit`; the envelope band goes (Task 3). `check_diagnostics.py` reads `findings` and emits one step per finding (Task 4). An env-gated sweep checks the spec's pre-registered thresholds (Task 5), and the references and root `CLAUDE.md` follow (Task 6).

**Tech Stack:** Python 3.13; arviz-stats (the `.azstats.uniformity_test` accessor, `loo_pit`), arviz-plots (`plot_ecdf_pit`), arviz-base, xarray, numpy, scipy (`stats.t`); pytest. The suite command below resolved arviz 1.3.0, arviz-stats 1.3.3, arviz-plots 1.3.2 and arviz-base 1.3.1 on 2026-10-03, with no matplotlib.

**Source:** [specs/calibration-check-verdicts.md](../calibration-check-verdicts.md), approved 2026-10-03 (commits 8e54154, cac1138). Its Decisions, Design, Testing and Planning handoff sections are binding. It closes two items in [specs/deferred_items.md](../deferred_items.md); see Completion.

**Where:** the worktree `/Users/lowell/Projects/agent-skills/.claude/worktrees/deferred-triage-2026-10-03`, branch `worktree-deferred-triage-2026-10-03`. The spec and the live plans 32 and 33 exist only on this branch. Run every command from the worktree root unless a step says otherwise.

## Global Constraints

The labels, keys, seed, floors and sweep thresholds are copied verbatim from the spec. The other lines restate the spec's Design and Planning handoff, and the repo's conventions.

- **The five finding labels**, held in the module constant `FINDINGS` of `calibration_check.py`, in this order (centre first):
  1. `biased (predictions too high)`
  2. `biased (predictions too low)`
  3. `over-confident (predictions too certain)`
  4. `under-confident (predictions too uncertain)`
  5. `shape mismatch (neither a shift nor a spread error)`
- **The eleven assessment keys**, which replace the five in `report["assessment"]`, in this order: `pit_p_value`, `coverage_p_value`, `alpha`, `pit_test_passed`, `coverage_test_passed`, `mean_pit`, `location_t`, `mean_coverage_deviation`, `findings`, `well_calibrated`, `calibration_diagnosis`. The top-level `variable`, `n_observations`, `pit_method` and `plots` keys stay. Removed: `pit_ecdf_inside_bands` and `coverage_ecdf_inside_bands`. `n_observations` becomes the number of pooled PIT values.
- **`PIT_SEED = 214`**, arviz's own default seed for PIT tie-breaking.
- **Rounding:** p-values are unrounded; `mean_pit` and `mean_coverage_deviation` round to 4 dp, and `location_t` to 2 dp.
- **Version floors:** arviz-stats ≥ 1.1 and arviz-plots ≥ 1.1.
  - Read the `uniformity_test` p-value by index (element `[0]`), never by unpacking: it returns `(p, shapley)` on arviz-stats 1.1 and `(p, shapley, shapley_unsorted)` on 1.3.
  - The guarantee is figure = JSON within one stack.
  - Removed: the pre-1.0 `difference_ecdf_pit` import fallback.
  - scipy, used for the t quantile, is already an arviz-stats dependency.
  - Planning-time finding F1 bears on this floor. It stays as written unless the owner answers Q1 by amending the spec.
- **Acceptance-sweep thresholds:** seeds 0–99 on both PIT paths at `ci_prob` = 0.99. "Named" counts any finding list that contains the label.

  | Fixture (loc, scale) | Pass condition, per path, of 100 |
  |---|---|
  | calibrated (0, 1) | `well-calibrated` ≥ 95 |
  | too narrow (0, 0.3) | exactly `[over-confident]` ≥ 95 |
  | too wide (0, 3.0) | exactly `[under-confident]` ≥ 95 |
  | mildly narrow (0, 0.8) | `over-confident` named ≥ 80; any `biased` named ≤ 5 |
  | shift up (0.4, 1) and down (−0.4, 1) | right-direction `biased` named ≥ 95; wrong direction 0 |
  | small shift (0.25, 1) | `biased (predictions too high)` named ≥ 60 |
  | shift + narrow (0.4, 0.7) | exactly `[biased (predictions too high), over-confident]` ≥ 95 |
  | shift + wide (0.4, 1.5) | exactly `[biased (predictions too high), under-confident]` ≥ 95 |
  | skewed predictive, PPC only | recorded, no threshold: a known limit |

  **At execution, a missed threshold is a finding for the owner, never a threshold edit.**
- **No envelope band remains in the script:** `difference_ecdf_pit`, `ecdf_pit` and the band-simulation count go.
- **`save_pit_plot` calls public `azp.plot_ecdf_pit`**, passing `coverage=coverage`, `envelope_prob=ci_prob` and `method='pot_c'`. The method is explicit, never left to the default.
- **`check_diagnostics.py` must not import `calibration_check.py`:** that would pull the arviz stack into a pure-JSON reader. The label strings are duplicated, and a contract test keeps the two copies in step.
- **The script imports no arviz internals:** not `warn_if_binary`, and not `arviz_plots.plots.utils_ppc.get_ppc_pit`.
- **No python code fence is added, removed or edited in any skill file.** This keeps plan 33's hard-coded snippet counts true whichever plan lands first. Plan 33 also edits root `CLAUDE.md` (the build-suite and Tier 3 lines), so re-read `CLAUDE.md` before editing it.
- **Unchanged:**
  - `skills/bayesian-workflow/SKILL.md`, `references/visualize.md` and `README.md`;
  - the gated SBC paragraph in `references/model-criticism.md` ("What that call actually draws");
  - the pins in `build/snippet_preamble.py`;
  - `NOTICE`. Per the spec's Provenance section, `calibration_check.py` stays part of the skill adapted from Alexandre Andorra's PyMC skill (MIT). The rewrite keeps that attribution, and cites `pot_c` author-year in original wording, with no text reproduced.
- **Out of scope:**
  - filing upstream issues for the two arviz-plots defects, which is the owner's call;
  - `prit_c`, `piet_c`, and any envelope band.
- **Test counts** are stated as deltas (`+N`), never as absolute totals; the executor re-measures totals. The figure-rendering test skips without matplotlib, and the sweep skips without `CALIBRATION_SWEEP=1`.
- **Each new test carries a predicted RED reason** in its task. Confirm each failure happens for that reason, not vacuously. A test the task marks as a guard passes before the change by design.
- **Gates for the skill edits** (root `CLAUDE.md`, "Commands"): the frontmatter and provenance lints, Tier 1 of the snippet gate, and the dependency-drift check.
- **Do not tick the two deferred items during the tasks.** The completion protocol does it; see Completion.
- **Python style:** match each file's existing quote style (decision D1). Use 4-space indents and target Python 3.13.

## Decisions this plan makes

The spec leaves these open. Each is pinned by a test or by a comment, so a reviewer can check it.

- **D1 — Quote style follows the file.**
  - `calibration_check.py`, `check_diagnostics.py` and `test_check_diagnostics.py` use double quotes; `test_calibration_check.py` uses single quotes. New code matches its file.
  - This follows plan 20's precedent for these scripts, though the always-on Python rule asks for single quotes.
- **D2 — The rules read the recorded values.** The spec says every finding traces to a number in the record, so:
  - location fires on the recorded (2 dp) `location_t`;
  - the spread direction reads the recorded `mean_coverage_deviation`;
  - the sd = 0 direction reads the recorded `mean_pit`;
  - both tests compare their p-values with the recorded `alpha`.

  `alpha = round(1 - ci_prob, 10)`, because `1 - 0.99` is `0.010000000000000009` in floating point and the spec's example records `0.01`. A test pins it.
- **D3 — The mean-structure step names its own finding, and drops "spread fits but".**
  - Today the step interpolates `cal['diagnosis']` and says "the predictive's spread fits but its centre is off".
  - Beside a spread finding, both parts would be false: the diagnosis is a compound, and the spread does not fit.
  - The step now interpolates the finding and reads "the predictive's centre is off".
- **D4 — The figure's sample dim is `<var>_dim_0`.**
  - A 1-D variable named like its own dim becomes a coordinate, not a data variable. Measured: `xr.Dataset({'obs': (('obs',), …)})` has no data variables.
  - NumPyro models often name the observed site `obs`.
- **D5 — `save_pit_plot` passes `visuals={'xlabel': {'text': 'ETI %' if coverage else 'PIT'}, 'ylabel': {}}`, as `plot_ppc_pit` does.** `plot_ecdf_pit` leaves the "Δ ECDF" y-label off by default, and `plot_ppc_pit` turns it on with `ylabel: {}`. Both labels are set explicitly rather than left to `plot_ecdf_pit`'s defaults. F7 notes that the saved PNG cuts the x-label off, exactly as today's figures do.
- **D6 — Two pieces of adjacent text change with the code.**
  - The import-error message names the floors.
  - `--ci-prob`'s help text no longer mentions bands.

  Neither is in the spec, but the change makes both stale.
- **D7 — No commit makes a forward reference.**
  - Task 1 states the skewed-predictive limit in the `assess_pit` docstring without counts; Task 5 adds a pointer to the sweep that records them. Numbers in code would go stale.
  - Task 1's `FINDINGS` comment gains its routing note in Task 4, once `check_diagnostics.py` holds the copy.
- **D8 — `check_diagnostics.py` routes by label prefix.**
  - Its copy of the labels is the four prefixes `biased (`, `over-confident (`, `under-confident (` and `shape mismatch (`.
  - "Non-generic" in the contract test means the step does not start with `Calibration check failed`.
- **D9 — An unknown label gets the generic step at any rating,** per the spec's "anything else" row. Today a fair-rated unknown label gets the fair step.
- **D10 — The rendering test uses a fixture whose two p-values differ at 2 dp.** The per-observation LOO-PIT gives p = 0.18 and 0.09, so a figure that prints the other test's p-value fails the test.

## Planning-time findings (2026-10-03)

These were measured while building the whole end state in scratch: every task's RED and GREEN, the sweep, and both stacks. Nothing from that scratch run is committed.

- **F1 — arviz-stats below 1.3.1 raises on super-uniform PIT values.**
  - On arviz-stats 1.1.0, 1.2.0 and 1.3.0, `pot_c` raises `ValueError: Cannot compute truncated Cauchy combination test. No p-values below 0.5 found.`
  - Those versions average only the order statistics with p < 0.5, and raise when there are none. That happens on exact quantile grids, on near-perfect PITs, and on typical n = 2 or 3 arrays.
  - arviz-stats 1.3.1 and later zero-fill those terms instead (Tesso & Vehtari 2026, Eq. 24) and return p = 0.5. The changed formula is the likely source of the spec's "0.14 vs 0.17" across versions, though that was not measured.
  - arviz-plots 1.3.2 requires arviz-stats ≥ 1.3.3.
  - On an affected stack, `main()` turns the error into its JSON error exit, because it catches `ValueError` from `assess_pit`. `--save-plots` then never runs.
  - On the 1.1.0 floor, the 10 tests that Task 3 Step 6 deselects fail for exactly this reason, and every other test passes. On arviz-stats 1.3.1 with arviz-plots 1.3.1, the whole calibration suite passes with nothing deselected.
  - The plan keeps the spec's floor. Q1 asks the owner.
- **F2 — The paper has two authors.**
  - arXiv:2603.02928, *LOO-PIT predictive model checking*, is by Herman Tesso and Aki Vehtari (v1 3 March 2026, v2 13 May 2026).
  - arviz-plots 1.3.2's docstrings cite "Tesso et al."; arviz-stats 1.3.3's cite "Tesso and Vehtari (2026)".
  - The plan writes "Tesso & Vehtari (2026)", following `publications.md`'s full-author-list convention. Q2 asks the owner, who may prefer the spec's "Tesso et al.".
- **F3 — The one other reader of `calibration.json` is unaffected.**
  - `skills/track-model-experiments/scripts/compare_experiments.py` reads `check_report.json`'s `calibration.rating`, whose rule is unchanged, and otherwise only checks that `calibration.json` exists.
  - A grep of `skills/`, `build/`, `commands/`, `agents/` and `runtimes/` found no other reader of the removed keys, `difference_ecdf_pit`, `BAND_SIMULATIONS` or `save_pit_plot`.
- **F4 — The suite environment has no matplotlib,** so the rendering test skips under the root command. Task 3 therefore runs its RED and GREEN twice, the second time with matplotlib.
- **F5 — The scratch prototype met every threshold** on the live stack. These counts are expectations, not thresholds and not the execution record; Task 5 measures and records its own.

  | Fixture | PPC | LOO |
  |---|---|---|
  | calibrated | 97 | 98 |
  | too narrow | 99 | 99 |
  | too wide | 99 | 99 |
  | mildly narrow: `over-confident` named / any `biased` named | 88 / 1 | 87 / 1 |
  | shift up / shift down, right direction | 100 / 99 | 100 / 99 |
  | small shift | 69 | 69 |
  | shift + narrow / shift + wide | 100 / 100 | 100 / 100 |

  Wrong-direction `biased` was 0 everywhere. The skewed fixture (PPC) read `over-confident` 84, `biased (predictions too low) and over-confident (predictions too certain)` 12, `under-confident` 2, and `biased (predictions too low) and under-confident (predictions too uncertain)` 2; `shape mismatch` 0.
- **F6 — The suite gets faster.** It ran in about 24 s; the end state runs in about 5 s, because the 1000-draw band simulations are gone.
- **F7 — Saved figures cut off their x-label, today and after this plan.**
  - The end state's figures do set the x-label (`PIT` or `ETI %`), but arviz-plots' default matplotlib layout puts it below the figure's bottom edge (measured at y = −15 to −1 px), so `pc.savefig` crops it.
  - Today's `plot_ppc_pit` figures are cropped identically, so the plan keeps parity, as the spec's "as `plot_ppc_pit` sets them" asks.
  - Q3 offers the one-line fix.

## Owner questions (answer before execution)

- **Q1 — Version floor (F1).**
  - **Keep** the spec's arviz-stats ≥ 1.1 and arviz-plots ≥ 1.1 (the plan's default), and record the old-stack error as a deferred item at completion.
  - **Or amend** the spec to arviz-stats ≥ 1.3.1 and arviz-plots ≥ 1.3.1.

  Amending touches the floor line in Global Constraints, the module docstring and import-error message in Task 3 Step 3 (edits 3.1 and 3.2), Task 3 Step 6 (pin the new floor and drop `--deselect`), and Completion's third new item (dropped).
- **Q2 — Citation (F2).** "Tesso & Vehtari (2026)" (the plan's default) or the spec's "Tesso et al.". The choice touches edit 3.1 (the module docstring) and edit 6.6 (the `publications.md` entry).
- **Q3 — Cropped x-label (F7).**
  - **Keep** parity with today's figures (the plan's default).
  - **Or fix** it: in edit 3.4, `save_pit_plot` calls `pc.savefig(output_path, bbox_inches="tight")` instead of `pc.savefig(output_path)`.
    - Checked at planning on arviz-plots 1.3.2 and on the 1.1.0 floor: the keyword passes through to matplotlib, and the label shows. The PNG goes from 640 × 257 to about 588 × 282 px.
    - No test changes.

## File map

| File | Change | Tasks |
|---|---|---|
| `skills/bayesian-workflow/scripts/calibration_check.py` | `FINDINGS`, `assess_pit`, `pit_values`; the envelope code goes; `assess_calibration`, `save_pit_plot` and `main()` rewired | 1–5 |
| `skills/bayesian-workflow/scripts/test_calibration_check.py` | rule, PIT, CLI and figure tests; the contract test; the sweep | 1–5 |
| `skills/bayesian-workflow/scripts/check_diagnostics.py` | `findings` in the report; one step per finding | 4 |
| `skills/bayesian-workflow/scripts/test_check_diagnostics.py` | the routing rows, the legacy fallback, the helper on the new contract | 4 |
| `skills/bayesian-workflow/references/reporting.md` | lines 36–37, 74–75, 165, 171 | 6 |
| `skills/bayesian-workflow/references/model-criticism.md` | one sentence after the fence that closes at line 110 | 6 |
| `skills/bayesian-workflow/references/publications.md` | the Tesso & Vehtari entry after Talts et al. | 6 |
| `CLAUDE.md` | the bayesian-workflow test-suite line | 6 |

**Test deltas:**

| Task | Delta | Note |
|---|---|---|
| 1 | +26 | |
| 2 | +5 | |
| 3 | +7 | one skips without matplotlib |
| 4 | +18 | 5 in `test_calibration_check.py`, 13 in `test_check_diagnostics.py` |
| 5 | +2 | skipped without `CALIBRATION_SWEEP=1` |

**The suite command**, used by every task (run from the worktree root):

```bash
cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray python -m pytest -q
```

"With matplotlib" means the same command with `--with matplotlib` added after `--with xarray`.

**Edit notation.** Edits are numbered N.M; the scratch build applied them in this order.

- **Replace X with Y** is an exact Edit-tool edit: `old_string` is X and `new_string` is Y, verbatim.
- **Insert above or below a named line** is an Edit whose `old_string` is that line and whose `new_string` is the line with the block added on the named side. Each insert states the blank lines to leave between the block and its line.
- **Replace a region** means everything from its first named line up to, but not including, its second.
- **Append** adds the block at the end of the file, after two blank lines.

---

### Task 1: `assess_pit` names every failing component

**Files:**
- Modify: `skills/bayesian-workflow/scripts/calibration_check.py`. Edits 1.1–1.4: imports, a `FINDINGS` block, and `_pot_c_p_value` and `assess_pit` above `_extract_ecdf_results`.
- Test: `skills/bayesian-workflow/scripts/test_calibration_check.py`. Edits 1.5–1.9.

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces, in `calibration_check.py`:
  - `FINDINGS`, a 5-tuple of the Global Constraints labels, and the constants `BIASED_HIGH`, `BIASED_LOW`, `OVER_CONFIDENT`, `UNDER_CONFIDENT` and `SHAPE_MISMATCH`;
  - `_pot_c_p_value(values) -> float`;
  - `assess_pit(pit, ci_prob=0.99) -> dict`, returning the eleven keys. It raises `ValueError` (message containing `at least 2`) for fewer than 2 values.
- Produces, in the test file, for Tasks 3–5:
  - the constants `HIGH`, `LOW`, `OVER`, `UNDER`, `SHAPE`, `ASSESSMENT_KEYS`, `COMPOUND_NARROW_SCALE` and `COMPOUND_WIDE_SCALE`;
  - the helpers `_exact_pit(loc, scale, n=N_OBS)` and `_shape_pit(n)`.

- [ ] **Step 1: Write the failing tests**

Edit 1.5, the test module docstring:

In `test_calibration_check.py`, replace:

```python
Most fixtures are a normal model of y ~ N(0, 1) whose predictive distribution is
```

with:

```python
The rule tests feed assess_pit exact-quantile PIT arrays: the PIT of N(0, 1)'s exact
quantiles under a N(loc, scale) predictive, so they involve no sampling. Most other
fixtures are a normal model of y ~ N(0, 1) whose predictive distribution is
```

Edit 1.6, scipy for the exact quantiles:

In `test_calibration_check.py`, replace:

```python
from arviz_base import from_dict
```

with:

```python
from arviz_base import from_dict
from scipy import stats
```

Edit 1.7, two scales for the compound fixtures:

In `test_calibration_check.py`, replace:

```python
LOCATION_SHIFT = 0.4
```

with:

```python
LOCATION_SHIFT = 0.4
COMPOUND_NARROW_SCALE = 0.7  # paired with LOCATION_SHIFT: a shift and a spread error at once
COMPOUND_WIDE_SCALE = 1.5
```

Edit 1.8, which adds the labels and the eleven keys. The old five-key `REPORT_KEYS` set stays until Task 3.

In `test_calibration_check.py`, insert directly above the line `PIT_PATHS = pytest.mark.parametrize('use_loo', …)`, leaving one blank line between the block and that line:

```python
# The five finding labels, verbatim; calibration_check.FINDINGS must hold exactly these.
HIGH = 'biased (predictions too high)'
LOW = 'biased (predictions too low)'
OVER = 'over-confident (predictions too certain)'
UNDER = 'under-confident (predictions too uncertain)'
SHAPE = 'shape mismatch (neither a shift nor a spread error)'

ASSESSMENT_KEYS = {
    'pit_p_value',
    'coverage_p_value',
    'alpha',
    'pit_test_passed',
    'coverage_test_passed',
    'mean_pit',
    'location_t',
    'mean_coverage_deviation',
    'findings',
    'well_calibrated',
    'calibration_diagnosis',
}
```

Edit 1.9, the rule tests. They feed exact-quantile PIT arrays, so no sampling is involved.
- `_shape_pit` is the three-segment fixture recorded in the `:1396` deferred item.
- The `0.9375` and `0.0625` constants are exact in binary, so sd(u) is exactly 0.
- A non-dyadic constant such as `0.999` leaves sd ≈ 1e-16, and the t-statistic comes out finite.

Append to the end of `test_calibration_check.py`, two blank lines after the last definition:

```python
def _exact_pit(loc, scale, n=N_OBS):
    """PIT values of N(0, 1)'s exact quantiles under a N(loc, scale) predictive: no sampling."""
    y = stats.norm.ppf((np.arange(n) + 0.5) / n)
    return stats.norm.cdf((y - loc) / scale)


def _shape_pit(n):
    """The shape fixture recorded in specs/deferred_items.md (the calibration-labels item).

    Coverage levels c = (i + 0.5)/n sit above the predictive median (u = 0.5 + c/2) when
    c < 0.25 or c >= 0.75 and below it (u = 0.5 - c/2) otherwise: the mean PIT is exactly
    0.5 and the coverage levels exactly uniform, yet the PIT values are far from uniform.
    """
    c = (np.arange(n) + 0.5) / n
    return np.where((c < 0.25) | (c >= 0.75), 0.5 + c / 2, 0.5 - c / 2)


EXACT_RULES = {
    'calibrated': (_exact_pit(0.0, TRUE_SCALE), []),
    'shifted_up': (_exact_pit(LOCATION_SHIFT, TRUE_SCALE), [HIGH]),
    'shifted_down': (_exact_pit(-LOCATION_SHIFT, TRUE_SCALE), [LOW]),
    'too_narrow': (_exact_pit(0.0, OVER_CONFIDENT_SCALE), [OVER]),
    'too_wide': (_exact_pit(0.0, UNDER_CONFIDENT_SCALE), [UNDER]),
    'shifted_and_narrow': (_exact_pit(LOCATION_SHIFT, COMPOUND_NARROW_SCALE), [HIGH, OVER]),
    'shifted_and_wide': (_exact_pit(LOCATION_SHIFT, COMPOUND_WIDE_SCALE), [HIGH, UNDER]),
    'shape_200': (_shape_pit(200), [SHAPE]),
    'shape_400': (_shape_pit(400), [SHAPE]),
    'shape_1000': (_shape_pit(1000), [SHAPE]),
}


def test_findings_constant_holds_the_five_labels_centre_first():
    assert calibration_check.FINDINGS == (HIGH, LOW, OVER, UNDER, SHAPE)


@pytest.mark.parametrize('pit, expected', EXACT_RULES.values(), ids=EXACT_RULES.keys())
def test_every_failing_component_is_named_centre_first(pit, expected):
    assert calibration_check.assess_pit(pit)['findings'] == expected


@pytest.mark.parametrize('pit', [pit for pit, _ in EXACT_RULES.values()], ids=EXACT_RULES.keys())
def test_the_report_is_consistent_with_itself(pit):
    report = calibration_check.assess_pit(pit)
    coverage = 2 * np.abs(pit - 0.5)
    assert set(report) == ASSESSMENT_KEYS
    assert (report['findings'] == []) is report['well_calibrated']
    assert (report['calibration_diagnosis'] == 'well-calibrated') is report['well_calibrated']
    assert report['calibration_diagnosis'] == (' and '.join(report['findings']) or 'well-calibrated')
    assert report['pit_test_passed'] is (report['pit_p_value'] >= report['alpha'])
    assert report['coverage_test_passed'] is (report['coverage_p_value'] >= report['alpha'])
    assert report['mean_coverage_deviation'] == round(0.5 - float(coverage.mean()), 4)
    # Valid JSON: plain bools and floats, no NaN.
    assert json.loads(json.dumps(report)) == report


def test_alpha_is_one_minus_ci_prob_without_float_noise():
    pit = _exact_pit(0.0, TRUE_SCALE)
    assert calibration_check.assess_pit(pit)['alpha'] == 0.01
    assert calibration_check.assess_pit(pit, ci_prob=0.95)['alpha'] == 0.05


def test_location_t_is_the_one_sample_t_of_the_mean_pit():
    pit = _exact_pit(LOCATION_SHIFT, TRUE_SCALE)
    report = calibration_check.assess_pit(pit)
    t = (pit.mean() - 0.5) / (pit.std(ddof=1) / np.sqrt(len(pit)))
    assert report['location_t'] == round(float(t), 2)
    assert report['mean_pit'] == round(float(pit.mean()), 4)


def test_fewer_than_two_pit_values_raise():
    with pytest.raises(ValueError, match='at least 2'):
        calibration_check.assess_pit([0.3])


@pytest.mark.parametrize('value, shift', [(0.9375, LOW), (0.0625, HIGH)], ids=['upper_tail', 'lower_tail'])
def test_zero_spread_pit_reads_as_a_shift_with_a_null_t(value, shift):
    # Every LOO-PIT clamped to one tail. These values are exact in binary, so sd(u) is
    # exactly 0; every coverage value is 0.875, so the coverage test fails as well.
    report = calibration_check.assess_pit(np.full(N_OBS, value))
    assert report['location_t'] is None
    assert report['findings'] == [shift, OVER]
    assert json.loads(json.dumps(report)) == report
```

- [ ] **Step 2: Run the tests to verify they fail**

Run the suite command. Expected: exactly 26 failures, all in the new tests, and no pre-existing test fails.
- 25 fail with `AttributeError: module 'calibration_check' has no attribute 'assess_pit'`.
- `test_findings_constant_holds_the_five_labels_centre_first` fails with `AttributeError: module 'calibration_check' has no attribute 'FINDINGS'`.

The reason is the same for all 26: `assess_pit` and `FINDINGS` do not exist yet. Any other failure reason means a test is wrong; fix it before Step 3.

- [ ] **Step 3: Implement `FINDINGS`, `_pot_c_p_value` and `assess_pit`**

Edit 1.1:

In `calibration_check.py`, replace:

```python
import json
import os
```

with:

```python
import json
import math
import os
```

Edit 1.2, the imports inside the existing `try:` block:

In `calibration_check.py`, replace:

```python
    import arviz_stats as azs
    from arviz_base import convert_to_datatree
    from arviz_stats.ecdf_utils import ecdf_pit
```

with:

```python
    import arviz_stats as azs
    import xarray as xr
    from arviz_base import convert_to_datatree
    from arviz_stats.ecdf_utils import ecdf_pit
    from scipy import stats
```

Edit 1.3:

In `calibration_check.py`, replace:

```python
BAND_SIMULATIONS = 1000
```

with:

```python
BAND_SIMULATIONS = 1000

# The five calibration findings, centre first.
BIASED_HIGH = "biased (predictions too high)"
BIASED_LOW = "biased (predictions too low)"
OVER_CONFIDENT = "over-confident (predictions too certain)"
UNDER_CONFIDENT = "under-confident (predictions too uncertain)"
SHAPE_MISMATCH = "shape mismatch (neither a shift nor a spread error)"
FINDINGS = (BIASED_HIGH, BIASED_LOW, OVER_CONFIDENT, UNDER_CONFIDENT, SHAPE_MISMATCH)
```

Edit 1.4. The docstring carries the spec's rules and both known limits. Task 5 adds the pointer to the sweep (D7).

In `calibration_check.py`, insert directly above the line `def _extract_ecdf_results(ds, var_name):`, leaving two blank lines between the block and that line:

```python
def _pot_c_p_value(values):
    """The pot_c uniformity-test p-value of `values`.

    Read by index, never by unpacking: arviz-stats 1.1 returns (p, shapley) and 1.3
    returns (p, shapley, shapley_unsorted).
    """
    result = xr.DataArray(values, dims=["pit"]).azstats.uniformity_test(dim=["pit"], method="pot_c")
    return float(result[0])


def assess_pit(pit, ci_prob=0.99):
    """Judge PIT values with pot_c and name every failing calibration component.

    With α = 1 − ci_prob and coverage levels c = 2|u − 0.5|, the PIT test and the
    coverage test each pass when their pot_c p-value is at least α. Findings, centre
    first:

    1. Location. The PIT test failed and |location_t| exceeds the Student-t quantile at
       1 − α/2 on n − 1 df, where location_t = (mean(u) − 0.5)/(sd(u)/√n). A negative
       location_t means the observations sit low in their predictive: biased
       (predictions too high). A positive one: biased (predictions too low). A spread
       error leaves the mean PIT at 0.5 while a shift moves it many standard errors, and
       gating the t-test on a failed PIT test keeps it an explanation rather than a
       third test, so it adds no false-alarm rate.
    2. Spread. The coverage test failed: over-confident (predictions too certain) when
       mean_coverage_deviation = 0.5 − mean(c) is ≤ 0, so intervals cover too little;
       otherwise under-confident (predictions too uncertain). A shift also lowers
       interval coverage, to second order, and the data cannot tell that echo from
       real narrowness, so a shift and a spread error are both named.
    3. Shape. The PIT test failed and neither of the above fired: shape mismatch
       (neither a shift nor a spread error).

    well_calibrated holds when both tests pass, which is exactly when findings is empty.
    Every rule reads the value the report records (alpha, mean_pit, location_t,
    mean_coverage_deviation), so each finding re-derives from calibration.json alone.
    When sd(u) = 0 (every LOO-PIT clamped to one tail), the mean counts as a
    significant shift toward mean_pit − 0.5, and location_t is None: an infinite t is
    not valid JSON.

    Known limits:
    - A skewed predictive with the right mean and variance is not labelled shape
      mismatch. A standardized Gamma(2) predictive for N(0, 1) data reads
      over-confident, sometimes with biased (predictions too low).
    - The t-test treats PIT values as independent. Heavy posterior dependence (few
      observations per parameter) inflates it, so read a borderline biased call against
      the PIT figure.

    Raises ValueError for fewer than 2 PIT values, where the t-test is undefined.
    """
    u = np.asarray(pit, dtype=float).ravel()
    n = u.size
    if n < 2:
        raise ValueError(f"Calibration needs at least 2 PIT values; got {n}.")
    # 1 - 0.99 is 0.010000000000000009 in floating point; record the α that was asked for.
    alpha = round(1 - ci_prob, 10)
    coverage = 2 * np.abs(u - 0.5)
    pit_p_value = _pot_c_p_value(u)
    coverage_p_value = _pot_c_p_value(coverage)
    pit_test_passed = pit_p_value >= alpha
    coverage_test_passed = coverage_p_value >= alpha
    mean_pit = round(float(u.mean()), 4)
    mean_coverage_deviation = round(0.5 - float(coverage.mean()), 4)

    sd = float(u.std(ddof=1))
    if sd > 0:
        location_t = round((float(u.mean()) - 0.5) / (sd / math.sqrt(n)), 2)
        shifted = abs(location_t) > float(stats.t.ppf(1 - alpha / 2, n - 1))
        sits_low = location_t < 0
    else:
        location_t = None
        shifted = mean_pit != 0.5
        sits_low = mean_pit < 0.5

    findings = []
    if shifted and not pit_test_passed:
        findings.append(BIASED_HIGH if sits_low else BIASED_LOW)
    if not coverage_test_passed:
        findings.append(OVER_CONFIDENT if mean_coverage_deviation <= 0 else UNDER_CONFIDENT)
    if not pit_test_passed and not findings:
        findings.append(SHAPE_MISMATCH)

    return {
        "pit_p_value": pit_p_value,
        "coverage_p_value": coverage_p_value,
        "alpha": alpha,
        "pit_test_passed": pit_test_passed,
        "coverage_test_passed": coverage_test_passed,
        "mean_pit": mean_pit,
        "location_t": location_t,
        "mean_coverage_deviation": mean_coverage_deviation,
        "findings": findings,
        "well_calibrated": pit_test_passed and coverage_test_passed,
        "calibration_diagnosis": " and ".join(findings) or "well-calibrated",
    }
```

- [ ] **Step 4: Run the tests to verify they pass**

Run the suite command. Expected: 0 failed, with 26 more tests passing than before this task.

- [ ] **Step 5: Commit**

```bash
git add skills/bayesian-workflow/scripts/calibration_check.py skills/bayesian-workflow/scripts/test_calibration_check.py
git commit -m "feat(bayesian-workflow): assess_pit names every failing calibration component"
```

---

### Task 2: `pit_values` owns the PIT

**Files:**
- Modify: `skills/bayesian-workflow/scripts/calibration_check.py`. Edits 2.1–2.2: `PIT_SEED`, and `pit_values` above `_pot_c_p_value`.
- Test: `skills/bayesian-workflow/scripts/test_calibration_check.py`. Edits 2.3–2.4.

**Interfaces:**
- Consumes: `assess_pit` from Task 1, which the regression test calls; the existing test helpers `_normal_model` and `_model_with_pit_values`.
- Produces: `PIT_SEED = 214` and `pit_values(dt, var_name, use_loo, seed=PIT_SEED) -> np.ndarray`, a 1-D array pooled over all observation dims and strictly inside (0, 1). Test-side, for Task 3, the helpers `_two_dimensional_model()` and `_draws_below(data)`.

- [ ] **Step 1: Write the failing tests**

Edit 2.3:

In `test_calibration_check.py`, replace:

```python
PER_OBSERVATION_PRIOR_SD = 0.7
```

with:

```python
PER_OBSERVATION_PRIOR_SD = 0.7
DISCRETE_RATE = 3.0
```

Edit 2.4. What each test checks:
- **Regression test.** An odd centred grid holds a PIT of exactly 0.5, so one observation has exactly S/2 of the S = 1000 draws below it. The test first proves the trap is real: the grid PIT k/S fails the coverage test on that calibrated fixture. Only then does it check that the owned PIT passes.
- **Discrete test.** It checks that each value lands in its rank cell, `[below, below + ties + 1) / (S + 1)`.
- **2-D test.** It compares a (20, 10) variable with the same draws flattened to 200, value for value.

Append to the end of `test_calibration_check.py`, two blank lines after the last definition:

```python
def _two_dimensional_model():
    """_normal_model's calibrated draws, reshaped into a (20, 10) observed variable."""
    flat = _normal_model(0.0, TRUE_SCALE)
    shape = (20, 10)
    return from_dict(
        {
            'posterior_predictive': {'y': flat['posterior_predictive']['y'].values.reshape(N_CHAIN, N_DRAW, *shape)},
            'observed_data': {'y': flat['observed_data']['y'].values.reshape(shape)},
        },
        dims={'y': ['row', 'col']},
    )


def _draws_below(data):
    return (data['posterior_predictive']['y'] < data['observed_data']['y']).sum(('chain', 'draw')).values


def test_ppc_pit_values_sit_strictly_inside_the_unit_interval_and_repeat_for_a_seed():
    # A too-narrow predictive leaves observations with every draw on one side of them,
    # where a grid PIT reads exactly 0 or 1.
    data = _normal_model(0.0, OVER_CONFIDENT_SCALE)
    below = _draws_below(data)
    assert (below == 0).any() and (below == N_CHAIN * N_DRAW).any()
    pit = calibration_check.pit_values(data, 'y', use_loo=False)
    assert pit.min() > 0 and pit.max() < 1
    assert calibration_check.PIT_SEED == 214
    np.testing.assert_array_equal(pit, calibration_check.pit_values(data, 'y', use_loo=False))
    reseeded = calibration_check.pit_values(data, 'y', use_loo=False, seed=calibration_check.PIT_SEED + 1)
    assert not np.array_equal(pit, reseeded)


def test_a_pit_at_the_predictive_median_does_not_break_the_coverage_test():
    # An odd centred grid holds one PIT of exactly 0.5, so one observation has exactly S/2
    # of the S = 1000 draws below it. The grid PIT k/S puts it at u = 0.5, coverage 0, and
    # pot_c's coverage test collapses on this calibrated fixture.
    data = _model_with_pit_values((np.arange(N_OBS - 1) + 0.5) / (N_OBS - 1))
    n_draws = N_CHAIN * N_DRAW
    below = _draws_below(data)
    assert np.sum(below == n_draws // 2) == 1
    assert calibration_check.assess_pit(below / n_draws)['coverage_test_passed'] is False
    pit = calibration_check.pit_values(data, 'y', use_loo=False)
    assert not np.any(pit == 0.5)
    assert calibration_check.assess_pit(pit)['coverage_test_passed'] is True


def test_discrete_pit_values_land_inside_their_rank_cell():
    # Poisson data under a Poisson predictive, so draws tie with y. The rank k spreads
    # over {below, ..., below + ties}, so u lands in [below, below + ties + 1) / (S + 1).
    rng = np.random.default_rng(SEED)
    y = rng.poisson(DISCRETE_RATE, size=N_OBS)
    y_rep = rng.poisson(DISCRETE_RATE, size=(N_CHAIN, N_DRAW, N_OBS))
    data = from_dict({'posterior_predictive': {'y': y_rep}, 'observed_data': {'y': y}}, dims={'y': ['obs']})
    draws = y_rep.reshape(-1, N_OBS)
    below, ties = (draws < y).sum(axis=0), (draws == y).sum(axis=0)
    assert (ties > 0).sum() > N_OBS // 2
    n_draws = N_CHAIN * N_DRAW
    pit = calibration_check.pit_values(data, 'y', use_loo=False)
    assert np.all(pit >= below / (n_draws + 1))
    assert np.all(pit < (below + ties + 1) / (n_draws + 1))


def test_a_two_dimensional_observed_variable_is_pooled():
    # The same draws, as a (20, 10) variable and as a flat 200: the same values in the same order.
    np.testing.assert_array_equal(
        calibration_check.pit_values(_two_dimensional_model(), 'y', use_loo=False),
        calibration_check.pit_values(_normal_model(0.0, TRUE_SCALE), 'y', use_loo=False),
    )


def test_loo_pit_values_are_arviz_pareto_smoothed_loo_pit():
    data = _normal_model(0.0, TRUE_SCALE)
    np.testing.assert_array_equal(
        calibration_check.pit_values(data, 'y', use_loo=True),
        azs.loo_pit(data, var_names='y', pareto_pit=True)['y'].values,
    )
```

- [ ] **Step 2: Run the tests to verify they fail**

Run the suite command. Expected: exactly 5 failures, all with `AttributeError: module 'calibration_check' has no attribute 'pit_values'`. `pit_values` does not exist yet. In the regression test, the `assess_pit` precondition on the grid PIT runs and passes first, then the `pit_values` call fails. No other test fails.

- [ ] **Step 3: Implement `PIT_SEED` and `pit_values`**

Edit 2.1:

In `calibration_check.py`, replace:

```python
# The five calibration findings, centre first.
```

with:

```python
# ArviZ's own default seed for PIT tie-breaking.
PIT_SEED = 214

# The five calibration findings, centre first.
```

Edit 2.2. Its docstring states both constructions and why a grid PIT breaks `pot_c`'s coverage test.

In `calibration_check.py`, insert directly above the line `def _pot_c_p_value(values):`, leaving two blank lines between the block and that line:

```python
def pit_values(dt, var_name, use_loo, seed=PIT_SEED):
    """PIT values of `var_name`, pooled over all its observation dims into one 1-D array.

    PPC-PIT is a seeded rank PIT, randomized within its cell. With S posterior-predictive
    draws (chain × draw), an observation's rank is k = #(draws < y) + ⌊U·(#(draws = y) + 1)⌋
    and its PIT is u = (k + V)/(S + 1), where U and V are U(0, 1) draws from
    np.random.default_rng(seed). When y and its draws are exchangeable, k is uniform on
    {0, …, S}, so u is exactly U(0, 1). The floor term randomizes ties, so discrete data
    stays correct.

    A grid PIT breaks pot_c's coverage test. arviz-plots' plot_ppc_pit draws the
    empirical k/S in the centre, so when exactly S/2 of an even S draws fall below y,
    u = 0.5 and the coverage value 2|u − 0.5| is exactly 0. pot_c reads a smallest
    coverage value of 0 as impossible, and its p-value collapses on a calibrated model.
    Spreading each PIT over its 1/(S + 1) cell keeps u off 0, 0.5 and 1.

    LOO-PIT is arviz_stats.loo_pit(..., pareto_pit=True): the values plot_loo_pit draws,
    which Pareto smoothing keeps off 0 and 1.
    """
    if use_loo:
        return azs.loo_pit(dt, var_names=var_name, pareto_pit=True)[var_name].values.ravel()
    predicted = dt["posterior_predictive"][var_name]
    observed = dt["observed_data"][var_name]
    below = (predicted < observed).sum(("chain", "draw")).values.ravel()
    ties = (predicted == observed).sum(("chain", "draw")).values.ravel()
    n_draws = predicted.sizes["chain"] * predicted.sizes["draw"]
    rng = np.random.default_rng(seed)
    rank = below + np.floor(rng.uniform(size=below.shape) * (ties + 1))
    return (rank + rng.uniform(size=below.shape)) / (n_draws + 1)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run the suite command. Expected: 0 failed, with 5 more tests passing than before this task.

- [ ] **Step 5: Commit**

```bash
git add skills/bayesian-workflow/scripts/calibration_check.py skills/bayesian-workflow/scripts/test_calibration_check.py
git commit -m "feat(bayesian-workflow): own a cell-randomized PIT that never lands on 0.5"
```

---

### Task 3: One PIT for the JSON and both figures

**Files:**
- Modify: `skills/bayesian-workflow/scripts/calibration_check.py`. Edits 3.1–3.6:
  - the module docstring and imports;
  - removing the envelope code;
  - the new `assess_calibration` and `save_pit_plot`;
  - the `--ci-prob` help;
  - `main()`.
- Test: `skills/bayesian-workflow/scripts/test_calibration_check.py`. Edits 3.7–3.12: the existing verdict and CLI tests move to the new contract, and 7 new tests.

**Interfaces:**
- Consumes: `assess_pit` (Task 1), `pit_values` (Task 2); the test-side `HIGH`, `LOW`, `OVER`, `UNDER`, `ASSESSMENT_KEYS` (Task 1) and `_two_dimensional_model()` (Task 2).
- Produces:
  - `assess_calibration(dt, var_name, use_loo, ci_prob=0.99) -> dict`, with the same signature, now `assess_pit(pit_values(...), ci_prob)`;
  - `save_pit_plot(pit, output_path, *, var_name, coverage=False, ci_prob=0.99) -> output_path`;
  - the CLI contract: the eleven assessment keys, a pooled `n_observations`, a JSON error exit for fewer than 2 PIT values, and a stderr warning naming `plot_ppc_pava` when every observed value is 0 or 1.
- Produces, test-side:
  - `_run_cli(monkeypatch, capsys, data, *flags) -> (exit_code, json, stderr)`, now three values;
  - `_record_figures(monkeypatch) -> list[(tree, kwargs)]`.

- [ ] **Step 1: Write the failing tests**

Edit 3.7, the test module docstring:

In `test_calibration_check.py`, replace:

```python
The rule tests feed assess_pit
```

with:

```python
The figure-rendering test skips unless matplotlib is installed (add --with matplotlib).

The rule tests feed assess_pit
```

Edit 3.8:

In `test_calibration_check.py`, replace:

```python
# Right spread, biased centre: the PIT band fails. The coverage fold is only second-order
# sensitive to a shift, so it holds at SEED (and on most seeds, not all).
```

with:

```python
# Right spread, biased centre: the PIT test fails. The coverage fold is only second-order
# sensitive to a shift, so its test holds at SEED (and on most seeds, not all).
```

Edit 3.9:

In `test_calibration_check.py`, replace:

```python
# A calibrated model is still flagged at ci_prob=0.99 on ~2-3% of seeds (3 of seeds
# 0-99, on both paths): each of the two simultaneous bands has its own false-alarm
# rate. Both the data and arviz-stats' band simulation are seeded, so the outcome
# for this seed is deterministic.
```

with:

```python
# A calibrated model is still flagged at ci_prob=0.99 on a few percent of seeds: each of
# the two pot_c tests has its own false-alarm rate. The data and the PIT randomization
# are both seeded, and pot_c is deterministic given the PIT values, so the outcome for
# this seed is deterministic.
```

Edit 3.10, which deletes the five-key set; `ASSESSMENT_KEYS` replaces it:

In `test_calibration_check.py`, delete these lines (and the blank line after them):

```python
REPORT_KEYS = {
    'pit_ecdf_inside_bands',
    'coverage_ecdf_inside_bands',
    'well_calibrated',
    'mean_coverage_deviation',
    'calibration_diagnosis',
}
```

Edit 3.11, which moves the existing tests to the new contract. What changes:
- the key set and the `*_test_passed` names;
- `findings` replaces `calibration_diagnosis` checks;
- `_run_cli` returns stderr too;
- `alpha` is recorded;
- `mean_coverage_deviation` is checked exactly against the PIT the verdict reads.

The `_coverage_levels` helper goes. `test_ppc_pit_needs_no_log_likelihood_group`, `FIXTURES`, `test_diagnosis_reads_well_calibrated_exactly_when_the_report_is` and `_model_with_pit_values` are carried through unchanged.

In `test_calibration_check.py`, replace everything from the `@PIT_PATHS` line directly above `def test_report_carries_exactly_the_five_documented_keys(use_loo):` up to, but not including, the `@PIT_PATHS` line directly above `def test_an_observed_only_variable_does_not_disturb_the_assessed_one(use_loo):` (keep the two blank lines before that decorator) with:

```python
@PIT_PATHS
def test_report_carries_exactly_the_eleven_documented_keys(use_loo):
    assert set(_assess(0.0, TRUE_SCALE, use_loo)) == ASSESSMENT_KEYS


@PIT_PATHS
def test_calibrated_predictive_passes_both_tests(use_loo):
    report = _assess(0.0, TRUE_SCALE, use_loo)
    assert report['pit_test_passed'] is True
    assert report['coverage_test_passed'] is True
    assert report['well_calibrated'] is True
    assert report['calibration_diagnosis'] == 'well-calibrated'


@PIT_PATHS
def test_too_narrow_predictive_is_diagnosed_over_confident(use_loo):
    report = _assess(0.0, OVER_CONFIDENT_SCALE, use_loo)
    assert report['coverage_test_passed'] is False
    assert report['well_calibrated'] is False
    # Empirical coverage below nominal: the coverage ΔECDF runs negative.
    assert report['mean_coverage_deviation'] < 0
    assert report['findings'] == [OVER]


@PIT_PATHS
def test_too_wide_predictive_is_diagnosed_under_confident(use_loo):
    report = _assess(0.0, UNDER_CONFIDENT_SCALE, use_loo)
    assert report['coverage_test_passed'] is False
    assert report['well_calibrated'] is False
    # Empirical coverage above nominal: the coverage ΔECDF runs positive.
    assert report['mean_coverage_deviation'] > 0
    assert report['findings'] == [UNDER]


@PIT_PATHS
def test_location_shift_fails_the_pit_test_alone_and_is_not_well_calibrated(use_loo):
    report = _assess(LOCATION_SHIFT, TRUE_SCALE, use_loo)
    assert report['pit_test_passed'] is False
    assert report['coverage_test_passed'] is True
    assert report['well_calibrated'] is False


def test_ppc_pit_needs_no_log_likelihood_group():
    no_log_likelihood = _normal_model(0.0, TRUE_SCALE, drop=('log_likelihood',))
    assert assess_calibration(no_log_likelihood, 'y', use_loo=False)['well_calibrated'] is True


def test_loo_pit_clears_the_double_dipping_that_ppc_pit_flags():
    # Every theta_i is fit to its own y_i, so every PPC-PIT is pulled toward 0.5 and
    # reads as under-confident. Exact leave-one-out gives the prior predictive
    # N(0, tau^2 + sigma^2), which is the data-generating process, so a correct LOO-PIT
    # is uniform. PSIS k-hat exceeds 0.7 on a few extreme-|y| points (6 of 200 at SEED).
    data = _per_observation_model()
    in_sample = assess_calibration(data, 'y', use_loo=False)
    assert in_sample['coverage_test_passed'] is False
    assert in_sample['findings'] == [UNDER]
    assert assess_calibration(data, 'y', use_loo=True)['well_calibrated'] is True


FIXTURES = {
    'calibrated': (0.0, TRUE_SCALE),
    'too_narrow': (0.0, OVER_CONFIDENT_SCALE),
    'too_wide': (0.0, UNDER_CONFIDENT_SCALE),
    'shifted_up': (LOCATION_SHIFT, TRUE_SCALE),
    'shifted_down': (-LOCATION_SHIFT, TRUE_SCALE),
}


@PIT_PATHS
@pytest.mark.parametrize('loc, scale', FIXTURES.values(), ids=FIXTURES.keys())
def test_diagnosis_reads_well_calibrated_exactly_when_the_report_is(use_loo, loc, scale):
    report = _assess(loc, scale, use_loo)
    assert (report['calibration_diagnosis'] == 'well-calibrated') is report['well_calibrated']


@PIT_PATHS
@pytest.mark.parametrize(
    'loc, direction',
    [(LOCATION_SHIFT, 'too high'), (-LOCATION_SHIFT, 'too low')],
    ids=['shifted_up', 'shifted_down'],
)
def test_location_shift_is_diagnosed_as_bias_in_its_direction(use_loo, loc, direction):
    report = _assess(loc, TRUE_SCALE, use_loo)
    assert report['findings'] == [f'biased (predictions {direction})']


def _run_cli(monkeypatch, capsys, data, *flags):
    """Run main() on in-memory data; only the netCDF load is replaced.

    Returns (exit code, the JSON on stdout, stderr).
    """
    monkeypatch.setattr(calibration_check, 'convert_to_datatree', lambda _path: data)
    monkeypatch.setattr(sys, 'argv', ['calibration_check.py', '--idata', 'in-memory.nc', *flags])
    try:
        calibration_check.main()
        exit_code = 0
    except SystemExit as exited:
        exit_code = exited.code
    captured = capsys.readouterr()
    return exit_code, json.loads(captured.out), captured.err


@pytest.mark.parametrize('missing', ['posterior', 'log_likelihood'])
def test_loo_pit_cli_names_a_missing_required_group(monkeypatch, capsys, missing):
    data = _normal_model(0.0, TRUE_SCALE, drop=(missing,))
    exit_code, output, _ = _run_cli(monkeypatch, capsys, data, '--loo-pit')
    assert exit_code == 1
    assert missing in output['error']


def test_loo_pit_cli_reports_on_data_with_every_required_group(monkeypatch, capsys):
    exit_code, output, _ = _run_cli(monkeypatch, capsys, _normal_model(0.0, TRUE_SCALE), '--loo-pit')
    assert exit_code == 0
    assert output['pit_method'] == 'loo_pit'
    assert output['assessment']['well_calibrated'] is True


@PIT_PATHS
def test_ci_prob_sets_the_test_level(use_loo):
    # At α = 0.99 a test passes only with p >= 0.99, so the calibrated fixture that passes
    # both tests at ci_prob = 0.99 fails both.
    report = assess_calibration(_normal_model(0.0, TRUE_SCALE), 'y', use_loo=use_loo, ci_prob=0.01)
    assert report['alpha'] == 0.99
    assert report['pit_test_passed'] is False
    assert report['coverage_test_passed'] is False


def test_cli_passes_ci_prob_to_the_assessment(monkeypatch, capsys):
    data = _normal_model(0.0, TRUE_SCALE)
    exit_code, output, _ = _run_cli(monkeypatch, capsys, data, '--ci-prob', '0.01')
    assert exit_code == 0
    assert output['assessment']['alpha'] == 0.99
    assert output['assessment']['pit_test_passed'] is False
    assert output['assessment']['coverage_test_passed'] is False


@PIT_PATHS
@pytest.mark.parametrize('loc, scale', FIXTURES.values(), ids=FIXTURES.keys())
def test_mean_coverage_deviation_is_the_mean_gap_between_coverage_ecdf_and_nominal(use_loo, loc, scale):
    # The mean of ECDF(c) - x over [0, 1] is 0.5 - mean(c), rounded to 4 dp, on the same
    # PIT values the verdict reads.
    data = _normal_model(loc, scale)
    coverage = 2 * np.abs(calibration_check.pit_values(data, 'y', use_loo) - 0.5)
    report = assess_calibration(data, 'y', use_loo=use_loo)
    assert report['mean_coverage_deviation'] == round(0.5 - float(coverage.mean()), 4)


def _model_with_pit_values(pit):
    """PPC-only DataTree whose PIT values are exactly `pit`: y = 0 and P(y_rep <= 0) = pit_i."""
    n_draws = N_CHAIN * N_DRAW
    quantiles = (np.arange(n_draws) + 0.5) / n_draws
    y_rep = (quantiles[:, None] - np.asarray(pit)[None, :]).reshape(N_CHAIN, N_DRAW, -1)
    return from_dict(
        {'posterior_predictive': {'y': y_rep}, 'observed_data': {'y': np.zeros(len(pit))}},
        dims={'y': ['obs']},
    )


def test_coverage_test_failing_alone_is_not_well_calibrated():
    # An even PIT grid plus a tenth of the points exactly at their predictive median: the
    # PIT test passes, while those points' coverage values all sit within 1/(S + 1) of 0,
    # which the coverage test cannot absorb. No sampling; the PIT randomization is seeded.
    n_centred = N_OBS // 10
    grid = (np.arange(N_OBS - n_centred) + 0.5) / (N_OBS - n_centred)
    report = assess_calibration(
        _model_with_pit_values(np.concatenate([grid, np.full(n_centred, 0.5)])), 'y', use_loo=False
    )
    assert report['pit_test_passed'] is True
    assert report['coverage_test_passed'] is False
    assert report['well_calibrated'] is False
    assert report['findings'] == [UNDER]
```

Edit 3.12, the 7 new tests:
- an n < 2 JSON error;
- the pooled `n_observations`;
- the binary warning, binary and continuous;
- the two figures drawing the JSON's values, on both paths;
- the rendering check, gated by `pytest.importorskip('matplotlib')`.

Append to the end of `test_calibration_check.py`, two blank lines after the last definition:

```python
def test_cli_reports_too_few_observations_as_a_json_error(monkeypatch, capsys):
    rng = np.random.default_rng(SEED)
    data = from_dict(
        {'posterior_predictive': {'y': rng.normal(size=(N_CHAIN, N_DRAW, 1))}, 'observed_data': {'y': np.zeros(1)}},
        dims={'y': ['obs']},
    )
    exit_code, output, _ = _run_cli(monkeypatch, capsys, data)
    assert exit_code == 1
    assert 'at least 2' in output['error']


def test_n_observations_counts_every_pooled_pit_value(monkeypatch, capsys):
    exit_code, output, _ = _run_cli(monkeypatch, capsys, _two_dimensional_model())
    assert exit_code == 0
    assert output['n_observations'] == N_OBS


@pytest.mark.parametrize('binary', [True, False], ids=['binary', 'continuous'])
def test_binary_observations_warn_toward_plot_ppc_pava(monkeypatch, capsys, binary):
    rng = np.random.default_rng(SEED)
    if binary:
        y = rng.integers(0, 2, size=N_OBS)
        y_rep = rng.integers(0, 2, size=(N_CHAIN, N_DRAW, N_OBS))
        data = from_dict({'posterior_predictive': {'y': y_rep}, 'observed_data': {'y': y}}, dims={'y': ['obs']})
    else:
        data = _normal_model(0.0, TRUE_SCALE)
    exit_code, _, stderr = _run_cli(monkeypatch, capsys, data)
    assert exit_code == 0
    if binary:
        assert 'plot_ppc_pava' in stderr
    else:
        assert stderr == ''


def _record_figures(monkeypatch):
    """Replace azp.plot_ecdf_pit with a recorder. Returns its list of (tree, kwargs) calls."""
    calls = []

    class _Figure:
        def savefig(self, _path):
            pass

    def record(tree, **kwargs):
        calls.append((tree, kwargs))
        return _Figure()

    monkeypatch.setattr(calibration_check.azp, 'plot_ecdf_pit', record)
    return calls


@PIT_PATHS
def test_both_figures_draw_the_pit_values_the_json_judged(monkeypatch, capsys, tmp_path, use_loo):
    calls = _record_figures(monkeypatch)
    data = _normal_model(0.0, TRUE_SCALE)
    flags = ['--save-plots', '--plot-dir', str(tmp_path), '--ci-prob', '0.95'] + (['--loo-pit'] if use_loo else [])
    exit_code, output, _ = _run_cli(monkeypatch, capsys, data, *flags)
    assert exit_code == 0
    pit = calibration_check.pit_values(data, 'y', use_loo)
    assert output['assessment'] == calibration_check.assess_pit(pit, ci_prob=0.95)
    assert [kwargs['coverage'] for _, kwargs in calls] == [False, True]
    for tree, kwargs in calls:
        np.testing.assert_array_equal(tree['ecdf_pit']['y'].values, pit)
        assert kwargs['method'] == 'pot_c'
        assert kwargs['envelope_prob'] == 0.95
    prefix = 'loo_pit' if use_loo else 'pit'
    assert output['plots'] == {
        'pit_ecdf': str(tmp_path / f'{prefix}_ecdf.png'),
        'coverage': str(tmp_path / f'{prefix}_coverage.png'),
    }


def test_each_figure_prints_the_p_value_its_json_verdict_records(monkeypatch, tmp_path):
    matplotlib = pytest.importorskip('matplotlib')
    matplotlib.use('Agg')
    from matplotlib.text import Text

    drawn = []
    draw = calibration_check.azp.plot_ecdf_pit

    def draw_and_keep(*args, **kwargs):
        drawn.append(draw(*args, **kwargs))
        return drawn[-1]

    monkeypatch.setattr(calibration_check.azp, 'plot_ecdf_pit', draw_and_keep)
    # The per-observation LOO-PIT prints two distinct p-values (0.18 and 0.09), so a
    # figure showing the other test's p-value would fail here.
    pit = calibration_check.pit_values(_per_observation_model(), 'y', use_loo=True)
    report = calibration_check.assess_pit(pit)
    for coverage, key in ((False, 'pit_p_value'), (True, 'coverage_p_value')):
        calibration_check.save_pit_plot(pit, tmp_path / f'{key}.png', var_name='y', coverage=coverage)
        figure = drawn[-1].viz['figure'].item()
        printed = [text.get_text() for text in figure.findobj(Text) if text.get_text().startswith('p=')]
        assert len(printed) == 1
        assert printed[0].startswith(f'p={report[key]:.2f}(α={report["alpha"]:.2f})')
        matplotlib.pyplot.close('all')
```

- [ ] **Step 2: Run the tests to verify they fail, twice**

**Without matplotlib:** run the suite command. Expected: exactly 34 failures; the rendering test is skipped.

| Failure reason | Tests |
|---|---|
| `AssertionError` on the key set: today's five keys against the eleven | `test_report_carries_exactly_the_eleven_documented_keys` ×2 |
| `KeyError: 'pit_test_passed'` | `test_calibrated_predictive_passes_both_tests` ×2, `test_location_shift_fails_the_pit_test_alone_and_is_not_well_calibrated` ×2, `test_coverage_test_failing_alone_is_not_well_calibrated` |
| `KeyError: 'coverage_test_passed'` | `test_too_narrow_predictive_is_diagnosed_over_confident` ×2, `test_too_wide_predictive_is_diagnosed_under_confident` ×2, `test_loo_pit_clears_the_double_dipping_that_ppc_pit_flags` |
| `KeyError: 'findings'` | `test_location_shift_is_diagnosed_as_bias_in_its_direction` ×4 |
| `KeyError: 'alpha'` | `test_ci_prob_sets_the_test_level` ×2, `test_cli_passes_ci_prob_to_the_assessment` |
| a value mismatch such as `assert 0.2978 == 0.2994`: today's value is the band's grid mean on arviz's own PIT | `test_mean_coverage_deviation_is_the_mean_gap_between_coverage_ecdf_and_nominal` ×10 |
| an uncaught `ValueError: zero-size array to reduction operation minimum which has no identity` from today's envelope code: no JSON error exit | `test_cli_reports_too_few_observations_as_a_json_error` |
| an uncaught `ValueError: object too deep for desired array`: today's envelope code cannot read a 2-D variable | `test_n_observations_counts_every_pooled_pit_value` |
| `AssertionError: assert 'plot_ppc_pava' in ''` | `test_binary_observations_warn_toward_plot_ppc_pava[binary]` |
| `TypeError: 'none' backend figures can't be saved.`: today's `save_pit_plot` calls `plot_ppc_pit`, which falls back to arviz's `none` backend without matplotlib | `test_both_figures_draw_the_pit_values_the_json_judged` ×2 |

These pass before the change by design, as guards:
- `test_binary_observations_warn_toward_plot_ppc_pava[continuous]`;
- `test_ppc_pit_needs_no_log_likelihood_group`;
- `test_diagnosis_reads_well_calibrated_exactly_when_the_report_is` ×10;
- the three `--loo-pit` CLI group tests;
- `test_an_observed_only_variable_does_not_disturb_the_assessed_one` ×2;
- every Task 1 and Task 2 test.

**With matplotlib:** expected exactly 35 failures. They match the table, with two exceptions:
- The two figure tests fail on `assert output['assessment'] == calibration_check.assess_pit(...)`, because with matplotlib today's figures render and the five-key assessment is reached first.
- `test_each_figure_prints_the_p_value_its_json_verdict_records` fails with `TypeError: save_pit_plot() got multiple values for argument 'var_name'`, from today's signature.

- [ ] **Step 3: Implement one PIT for the JSON and both figures**

Edit 3.1, the module docstring. It carries Q2's default citation and Q1's default floors.

In `calibration_check.py`, replace:

```python
"""
Calibration assessment for Bayesian models.

Computes coverage calibration, PIT ECDFs, and generates calibration plots
using ArviZ 1.0+ (arviz_plots). Supports both PPC-PIT and LOO-PIT.

Usage:
    python calibration_check.py --idata path/to/inference_data.nc
    python calibration_check.py --idata path/to/inference_data.nc --var-name obs --save-plots
    python calibration_check.py --idata path/to/inference_data.nc --loo-pit --save-plots
    python calibration_check.py --idata path/to/inference_data.nc --save-plots --plot-dir plots/
"""
```

with:

```python
"""
Calibration assessment for Bayesian models.

Computes one set of PIT values per run, judges them with the pot_c uniformity test
(Tesso & Vehtari 2026) that ArviZ's PIT plots print, names every failing calibration
component, and draws the PIT Δ-ECDF and coverage figures from the same values, so the
p-value printed on each figure is the one the JSON records. Supports both PPC-PIT and
LOO-PIT. Requires arviz-stats >= 1.1 and arviz-plots >= 1.1.

Usage:
    python calibration_check.py --idata path/to/inference_data.nc
    python calibration_check.py --idata path/to/inference_data.nc --var-name obs --save-plots
    python calibration_check.py --idata path/to/inference_data.nc --loo-pit --save-plots
    python calibration_check.py --idata path/to/inference_data.nc --save-plots --plot-dir plots/
"""
```

Edit 3.2, the imports and the import error (D6). This removes the `difference_ecdf_pit` fallback and the `ecdf_pit` import.

In `calibration_check.py`, replace:

```python
try:
    import arviz_plots as azp
    import arviz_stats as azs
    import xarray as xr
    from arviz_base import convert_to_datatree
    from arviz_stats.ecdf_utils import ecdf_pit
    from scipy import stats

    # `difference_ecdf_pit` is a statistics helper; its stable home is
    # arviz_stats.ecdf_utils on arviz-stats >= 1.0 (both PyMC-5 and PyMC-6 stacks).
    # arviz_plots <= 1.0 also re-exported it under arviz_plots.plots.ppc_pit_plot,
    # but arviz_plots 1.1 removed that re-export — import from arviz_stats, and only
    # fall back to the old plots path for the older layout.
    try:
        from arviz_stats.ecdf_utils import difference_ecdf_pit
    except ImportError:  # pragma: no cover - pre-1.0 arviz_stats layout
        from arviz_plots.plots.ppc_pit_plot import difference_ecdf_pit
except ImportError:
    print(
        json.dumps(
            {
                "error": (
                    "arviz_plots and arviz_base are required. "
                    "Install with: pip install arviz-plots arviz-base"
                )
            }
        )
    )
    sys.exit(1)
```

with:

```python
try:
    import arviz_plots as azp
    import arviz_stats as azs
    import xarray as xr
    from arviz_base import convert_to_datatree
    from scipy import stats
except ImportError:
    print(
        json.dumps(
            {
                "error": (
                    "arviz-plots >= 1.1, arviz-stats >= 1.1 and arviz-base are required. "
                    "Install with: pip install 'arviz-plots>=1.1' 'arviz-stats>=1.1' arviz-base"
                )
            }
        )
    )
    sys.exit(1)
```

Edit 3.3, which removes the band-simulation count:

In `calibration_check.py`, delete these lines (and the blank line after them):

```python
# Monte Carlo draws behind each simultaneous confidence band.
BAND_SIMULATIONS = 1000
```

Edit 3.4. It replaces the region holding `_extract_ecdf_results`, `_ecdf_check`, today's `assess_calibration` and today's `save_pit_plot`. `save_pit_plot` follows D4 and D5.

In `calibration_check.py`, replace everything from the line `def _extract_ecdf_results(ds, var_name):` up to, but not including, the line `def _exit_with_error(message) -> NoReturn:` (keep the two blank lines before it) with:

```python
def assess_calibration(dt, var_name, use_loo, ci_prob=0.99):
    """Assess the calibration of `var_name`: assess_pit on its pit_values (see both)."""
    return assess_pit(pit_values(dt, var_name, use_loo), ci_prob)


def save_pit_plot(pit, output_path, *, var_name, coverage=False, ci_prob=0.99):
    """Save the PIT Δ-ECDF figure of `pit`, or with coverage=True its coverage view.

    Draws with public azp.plot_ecdf_pit from the same PIT values and the same pot_c test
    as assess_pit, so the p-value printed on the figure is the JSON's pit_p_value
    (coverage_p_value with coverage=True), judged against the same α = 1 − ci_prob. The
    figure shows the Δ-ECDF step line, a zero line, that p-value with its α, and the
    suspicious points the test highlights when it rejects; no band is drawn.
    method="pot_c" is passed explicitly: it is the default on every version checked,
    but "the same test as the JSON" must not depend on a future default. The axis
    labels are the ones plot_ppc_pit sets.
    """
    # Named after the variable so the dim can never share its name: a 1-D variable named
    # like its own dim becomes a coordinate, not a data variable.
    sample_dim = f"{var_name}_dim_0"
    tree = xr.DataTree.from_dict({"ecdf_pit": xr.Dataset({var_name: ((sample_dim,), pit)})})
    pc = azp.plot_ecdf_pit(
        tree,
        group="ecdf_pit",
        sample_dims=[sample_dim],
        method="pot_c",
        envelope_prob=ci_prob,
        coverage=coverage,
        visuals={"xlabel": {"text": "ETI %" if coverage else "PIT"}, "ylabel": {}},
    )
    pc.savefig(output_path)
    return output_path
```

Edit 3.5, the `--ci-prob` help text (D6):

In `calibration_check.py`, replace:

```python
        help="Probability for simultaneous confidence bands (default: 0.99)",
```

with:

```python
        help="A test fails when its pot_c p-value is below 1 - ci-prob (default: 0.99)",
```

Edit 3.6, `main()`:
- the binary warning;
- one `pit_values` call feeding both the assessment and both figures;
- the n < 2 `ValueError` as a JSON error exit;
- the pooled `n_observations`.

In `calibration_check.py`, replace:

```python
    # Assess calibration using ArviZ ΔECDF + simultaneous bands
    ci_prob = args.ci_prob
    assessment = assess_calibration(dt, var_name, use_loo=args.loo_pit, ci_prob=ci_prob)

    n_obs = len(dt["observed_data"][var_name].values)
    report = {
        "variable": var_name,
        "n_observations": n_obs,
        "pit_method": "loo_pit" if args.loo_pit else "ppc_pit",
        "assessment": assessment,
    }

    # Save plots using arviz_plots
    if args.save_plots:
        os.makedirs(args.plot_dir, exist_ok=True)
        prefix = "loo_pit" if args.loo_pit else "pit"
        report["plots"] = {
            "pit_ecdf": save_pit_plot(
                dt,
                var_name,
                os.path.join(args.plot_dir, f"{prefix}_ecdf.png"),
                use_loo=args.loo_pit,
                ci_prob=ci_prob,
            ),
            "coverage": save_pit_plot(
                dt,
                var_name,
                os.path.join(args.plot_dir, f"{prefix}_coverage.png"),
                use_loo=args.loo_pit,
                coverage=True,
                ci_prob=ci_prob,
            ),
        }
```

with:

```python
    # plot_ppc_pit warns on binary data; this script bypasses it, so it warns itself.
    if np.isin(dt["observed_data"][var_name].values, (0, 1)).all():
        print(
            f"Warning: every observed value of '{var_name}' is 0 or 1. The PIT checks, "
            "and this verdict, are weak on binary outcomes; azp.plot_ppc_pava may be "
            "more appropriate.",
            file=sys.stderr,
        )

    # One set of PIT values feeds the JSON verdict and both figures.
    ci_prob = args.ci_prob
    pit = pit_values(dt, var_name, use_loo=args.loo_pit)
    try:
        assessment = assess_pit(pit, ci_prob=ci_prob)
    except ValueError as e:
        _exit_with_error(str(e))

    report = {
        "variable": var_name,
        "n_observations": int(pit.size),
        "pit_method": "loo_pit" if args.loo_pit else "ppc_pit",
        "assessment": assessment,
    }

    if args.save_plots:
        os.makedirs(args.plot_dir, exist_ok=True)
        prefix = "loo_pit" if args.loo_pit else "pit"
        report["plots"] = {
            "pit_ecdf": save_pit_plot(
                pit,
                os.path.join(args.plot_dir, f"{prefix}_ecdf.png"),
                var_name=var_name,
                ci_prob=ci_prob,
            ),
            "coverage": save_pit_plot(
                pit,
                os.path.join(args.plot_dir, f"{prefix}_coverage.png"),
                var_name=var_name,
                coverage=True,
                ci_prob=ci_prob,
            ),
        }
```

- [ ] **Step 4: Run the tests to verify they pass, twice**

1. Run the suite command. Expected: 0 failed, 1 skipped (the rendering test); 6 more tests pass than before the task, out of the +7 new.
2. Run it with matplotlib. Expected: 0 failed and 0 skipped.

Then confirm nothing outside the scripts still names the removed API:

```bash
grep -rn -E "inside_bands|difference_ecdf_pit|BAND_SIMULATIONS|_ecdf_check|_extract_ecdf_results" skills/bayesian-workflow/scripts/ skills/track-model-experiments/ build/ commands/ agents/ runtimes/
```

Expected: no output. `references/reporting.md` still names `*_inside_bands` until Task 6.

- [ ] **Step 5: Smoke-run the CLI end to end on a real file**

This writes a calibrated model to netCDF and runs the script with `--save-plots`. Run it from `skills/bayesian-workflow/scripts`:

```bash
cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray --with h5netcdf --with h5py python -c "
from test_calibration_check import _normal_model
_normal_model(0.0, 1.0).to_netcdf('/tmp/calcheck-smoke.nc')
" && uv run --python 3.13 --with arviz --with arviz-stats --with numpy --with xarray --with matplotlib --with h5netcdf --with h5py python calibration_check.py --idata /tmp/calcheck-smoke.nc --save-plots --plot-dir /tmp/calcheck-smoke-plots && ls /tmp/calcheck-smoke-plots
```

The first command needs pytest because it imports the test module, and both need h5py, the h5netcdf engine's backend.

Expected:
- The JSON shows the eleven keys, `"findings": []` and `"calibration_diagnosis": "well-calibrated"`.
- `ls` lists `pit_coverage.png` and `pit_ecdf.png`.
- Open one PNG: its corner p-value is the JSON's `pit_p_value` or `coverage_p_value` to 2 dp. At planning, the coverage figure printed `p=0.45(α=0.01)` beside a JSON `coverage_p_value` of 0.4528.
- The x-label is cut off at the bottom edge, as on today's figures (F7), unless Q3 chose the fix. That is not a regression.

- [ ] **Step 6: Floor run (Q1's default: arviz-stats ≥ 1.1, arviz-plots ≥ 1.1)**

The spec verified its design on this stack; this step verifies the implementation. Run from `skills/bayesian-workflow/scripts`:

```bash
cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with 'arviz-plots==1.1.0' --with 'arviz-stats==1.1.0' --with 'arviz-base==1.1.0' --with 'matplotlib<3.11' --with numpy --with xarray python -m pytest -q test_calibration_check.py \
  --deselect 'test_calibration_check.py::test_every_failing_component_is_named_centre_first[calibrated]' \
  --deselect 'test_calibration_check.py::test_every_failing_component_is_named_centre_first[shape_200]' \
  --deselect 'test_calibration_check.py::test_every_failing_component_is_named_centre_first[shape_400]' \
  --deselect 'test_calibration_check.py::test_every_failing_component_is_named_centre_first[shape_1000]' \
  --deselect 'test_calibration_check.py::test_the_report_is_consistent_with_itself[calibrated]' \
  --deselect 'test_calibration_check.py::test_the_report_is_consistent_with_itself[shape_200]' \
  --deselect 'test_calibration_check.py::test_the_report_is_consistent_with_itself[shape_400]' \
  --deselect 'test_calibration_check.py::test_the_report_is_consistent_with_itself[shape_1000]' \
  --deselect 'test_calibration_check.py::test_alpha_is_one_minus_ci_prob_without_float_noise' \
  --deselect 'test_calibration_check.py::test_a_pit_at_the_predictive_median_does_not_break_the_coverage_test'
```

Expected: 0 failed, 10 deselected. `matplotlib<3.11` is required here, because arviz-plots 1.1.0 fails to import against newer matplotlib.

The 10 deselected tests all feed super-uniform PIT values, which arviz-stats below 1.3.1 cannot test (F1). **Never weaken, delete or mark these tests to make a floor run green.** Run them on the floor without `--deselect` once, to confirm each fails with `ValueError: Cannot compute truncated Cauchy combination test. No p-values below 0.5 found.` and nothing else.

If the owner amended the floor at Q1, run the same command pinned to `arviz-plots==1.3.1`, `arviz-stats==1.3.1` and `arviz-base==1.3.1` with plain `--with matplotlib`, and without the `--deselect` lines. Expected: 0 failed.

- [ ] **Step 7: Commit**

```bash
git add skills/bayesian-workflow/scripts/calibration_check.py skills/bayesian-workflow/scripts/test_calibration_check.py
git commit -m "feat(bayesian-workflow): one PIT feeds calibration_check's verdict and both figures"
```

---

### Task 4: `check_diagnostics.py` routes every finding

**Files:**
- Modify: `skills/bayesian-workflow/scripts/check_diagnostics.py`. Edits 4.2–4.6:
  - the prefix constants and `_calibration_findings`;
  - `findings` in the report;
  - `_spread_step` and `_calibration_steps`;
  - the calibration block of `suggest_next_steps`.
- Modify: `skills/bayesian-workflow/scripts/calibration_check.py`. Edit 4.1, the `FINDINGS` comment (D7).
- Test: `skills/bayesian-workflow/scripts/test_check_diagnostics.py` (edit 4.7) and `test_calibration_check.py` (edits 4.8–4.9, the contract test).

**Interfaces:**
- Consumes: `calibration_check.FINDINGS` (Task 1), in the contract test only.
- Produces:
  - `check_diagnostics(...)["calibration"]["findings"] -> list[str]`;
  - `_calibration_findings(cal) -> list[str]`, which falls back to `[calibration_diagnosis]` for legacy files unless that is empty or reads `well-calibrated`;
  - `_calibration_steps(cal) -> list[str]`, one step per finding in findings order;
  - `_spread_step(finding, rating) -> str`;
  - the constants `BIASED_PREFIX`, `OVER_CONFIDENT_PREFIX`, `UNDER_CONFIDENT_PREFIX` and `SHAPE_MISMATCH_PREFIX`.
- Unchanged: the rating rule (`_rate_calibration`) and `_build_summary`.

- [ ] **Step 1: Write the failing tests**

Edit 4.7. It replaces `test_check_diagnostics.py`'s calibration section, from `def _calibration(` to the end of the file. The `_calibration` helper moves to the new contract and carries the four assessment keys this script reads. A `_legacy_calibration` helper models a file written before `findings` existed. There is a test for every row of the spec's routing table.

In `test_check_diagnostics.py`, replace:

```python
def _calibration(diagnosis, mean_coverage_deviation, *, pit_inside, coverage_inside):
    """calibration_check.py-shaped input."""
    return {
        "variable": "y",
        "pit_method": "ppc_pit",
        "assessment": {
            "pit_ecdf_inside_bands": pit_inside,
            "coverage_ecdf_inside_bands": coverage_inside,
            "well_calibrated": pit_inside and coverage_inside,
            "mean_coverage_deviation": mean_coverage_deviation,
            "calibration_diagnosis": diagnosis,
        },
    }


def _calibration_step(steps):
    hits = [s for s in steps if s.startswith("Calibration")]
    assert len(hits) == 1, steps
    return hits[0]


@pytest.mark.parametrize("direction", ["too high", "too low"])
def test_biased_calibration_points_at_the_mean_structure(direction):
    # Right spread, off-centre: the coverage deviation is small, so the rating is "fair".
    cal = _calibration(f"biased (predictions {direction})", -0.0255, pit_inside=False, coverage_inside=True)
    step = _calibration_step(suggest_next_steps(check_diagnostics(calibration=cal)))
    assert f"biased (predictions {direction})" in step
    assert "mean structure" in step
    assert "heavier-tailed" not in step


def test_over_confident_calibration_keeps_its_likelihood_advice():
    cal = _calibration(
        "over-confident (predictions too certain)", -0.3126, pit_inside=False, coverage_inside=False
    )
    step = _calibration_step(suggest_next_steps(check_diagnostics(calibration=cal)))
    assert "likelihood is too narrow" in step
```

with:

```python
HIGH = "biased (predictions too high)"
OVER = "over-confident (predictions too certain)"
UNDER = "under-confident (predictions too uncertain)"
SHAPE = "shape mismatch (neither a shift nor a spread error)"
POOR_OVER, POOR_UNDER = -0.3126, 0.3126  # |deviation| > 0.05 rates calibration poor
FAIR_OVER, FAIR_UNDER = -0.0255, 0.0255  # |deviation| <= 0.05 rates it fair


def _calibration(findings, mean_coverage_deviation):
    """calibration_check.py-shaped input: the four assessment keys this script reads."""
    return {
        "variable": "y",
        "pit_method": "ppc_pit",
        "assessment": {
            "findings": findings,
            "well_calibrated": not findings,
            "mean_coverage_deviation": mean_coverage_deviation,
            "calibration_diagnosis": " and ".join(findings) or "well-calibrated",
        },
    }


def _legacy_calibration(diagnosis, mean_coverage_deviation):
    """A calibration.json written before findings existed: one diagnosis, no findings key."""
    well_calibrated = diagnosis == "well-calibrated"
    return {
        "variable": "y",
        "pit_method": "ppc_pit",
        "assessment": {
            "pit_ecdf_inside_bands": well_calibrated,
            "coverage_ecdf_inside_bands": well_calibrated,
            "well_calibrated": well_calibrated,
            "mean_coverage_deviation": mean_coverage_deviation,
            "calibration_diagnosis": diagnosis,
        },
    }


def _calibration_steps(cal):
    return [s for s in suggest_next_steps(check_diagnostics(calibration=cal)) if s.startswith("Calibration")]


@pytest.mark.parametrize("direction", ["too high", "too low"])
def test_biased_calibration_points_at_the_mean_structure(direction):
    # Right spread, off-centre: the coverage deviation is small, so the rating is "fair".
    (step,) = _calibration_steps(_calibration([f"biased (predictions {direction})"], FAIR_OVER))
    assert f"biased (predictions {direction})" in step
    assert "mean structure" in step
    assert "heavier-tailed" not in step


def test_over_confident_calibration_keeps_its_likelihood_advice():
    (step,) = _calibration_steps(_calibration([OVER], POOR_OVER))
    assert "likelihood is too narrow" in step


def test_under_confident_calibration_keeps_its_prior_advice():
    (step,) = _calibration_steps(_calibration([UNDER], POOR_UNDER))
    assert "predictions are too uncertain" in step


@pytest.mark.parametrize("finding, deviation", [(OVER, FAIR_OVER), (UNDER, FAIR_UNDER)], ids=["over", "under"])
def test_a_fair_spread_finding_gets_the_fair_step(finding, deviation):
    (step,) = _calibration_steps(_calibration([finding], deviation))
    assert "fair but not excellent" in step


def test_over_confidence_after_a_shift_is_re_checked_not_treated():
    # A shift alone lowers interval coverage, so the spread step waits for a re-run.
    biased_step, spread_step = _calibration_steps(_calibration([HIGH, OVER], POOR_OVER))
    assert "mean structure" in biased_step
    assert "re-run calibration_check.py" in spread_step
    assert "likelihood is too narrow" not in spread_step


def test_under_confidence_after_a_shift_keeps_its_spread_step():
    # A shift cannot make intervals too wide, so the spread step stands.
    biased_step, spread_step = _calibration_steps(_calibration([HIGH, UNDER], POOR_UNDER))
    assert "mean structure" in biased_step
    assert "predictions are too uncertain" in spread_step


def test_shape_mismatch_points_at_the_likelihood_shape():
    (step,) = _calibration_steps(_calibration([SHAPE], FAIR_OVER))
    assert "posterior-predictive density overlay" in step
    assert "zero-inflated" in step


def test_an_unknown_finding_gets_the_generic_step():
    # Fair-rated, so it cannot fall into the fair spread step either.
    (step,) = _calibration_steps(_calibration(["a label from a newer calibration_check.py"], FAIR_OVER))
    assert step.startswith("Calibration check failed")


def test_a_well_calibrated_report_adds_no_calibration_step():
    assert _calibration_steps(_calibration([], 0.0012)) == []


def test_findings_are_carried_into_the_report():
    report = check_diagnostics(calibration=_calibration([HIGH, OVER], POOR_OVER))
    assert report["calibration"]["findings"] == [HIGH, OVER]


@pytest.mark.parametrize(
    "diagnosis, findings",
    [(HIGH, [HIGH]), ("well-calibrated", []), ("", [])],
    ids=["one_finding", "well_calibrated", "empty"],
)
def test_a_legacy_calibration_file_falls_back_to_its_diagnosis(diagnosis, findings):
    report = check_diagnostics(calibration=_legacy_calibration(diagnosis, FAIR_OVER))
    assert report["calibration"]["findings"] == findings


def test_a_legacy_over_confident_file_keeps_its_likelihood_advice():
    (step,) = _calibration_steps(_legacy_calibration(OVER, POOR_OVER))
    assert "likelihood is too narrow" in step
```

Edit 4.8:

In `test_calibration_check.py`, replace:

```python
import calibration_check
```

with:

```python
import calibration_check
import check_diagnostics
```

Edit 4.9, the contract test:

Append to the end of `test_calibration_check.py`, two blank lines after the last definition:

```python
@pytest.mark.parametrize('label', calibration_check.FINDINGS)
def test_every_finding_reaches_a_specific_next_step(label):
    # check_diagnostics.py keeps its own copy of the labels, since importing
    # calibration_check would pull the ArviZ stack into a pure-JSON reader. A label it
    # cannot route falls through to the generic step. A |deviation| above 0.05 rates
    # calibration poor, so the spread labels take their specific steps.
    calibration = {
        'assessment': {
            'findings': [label],
            'well_calibrated': False,
            'calibration_diagnosis': label,
            'mean_coverage_deviation': -0.3,
        }
    }
    report = check_diagnostics.check_diagnostics(calibration=calibration)
    steps = [step for step in check_diagnostics.suggest_next_steps(report) if step.startswith('Calibration')]
    assert len(steps) == 1, steps
    assert 'Calibration check failed' not in steps[0]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run the suite command. Expected: exactly 9 failures.

| Failure reason | Test |
|---|---|
| `ValueError: not enough values to unpack (expected 2, got 1)`: today's routing gives the joined diagnosis one step | `test_over_confidence_after_a_shift_is_re_checked_not_treated`, `test_under_confidence_after_a_shift_keeps_its_spread_step` |
| `AssertionError: assert 'posterior-predictive density overlay' in 'Calibration is fair but not excellent — …'` | `test_shape_mismatch_points_at_the_likelihood_shape` |
| `AssertionError`: `step.startswith("Calibration check failed")` is false, because today a fair-rated unknown label gets the fair step (D9) | `test_an_unknown_finding_gets_the_generic_step` |
| `KeyError: 'findings'` | `test_findings_are_carried_into_the_report`, `test_a_legacy_calibration_file_falls_back_to_its_diagnosis` ×3 |
| `AssertionError: assert 'Calibration check failed' not in …`: the shape label falls through to the generic step | `test_every_finding_reaches_a_specific_next_step[shape mismatch (neither a shift nor a spread error)]` |

These pass before the change by design, as guards on today's routing:
- `test_biased_calibration_points_at_the_mean_structure` ×2;
- `test_over_confident_calibration_keeps_its_likelihood_advice`;
- `test_under_confident_calibration_keeps_its_prior_advice`;
- `test_a_fair_spread_finding_gets_the_fair_step` ×2;
- `test_a_well_calibrated_report_adds_no_calibration_step`;
- `test_a_legacy_over_confident_file_keeps_its_likelihood_advice`;
- the contract test's other four labels.

- [ ] **Step 3: Implement the routing**

Edit 4.2, the prefix constants (D8):

In `check_diagnostics.py`, replace:

```python
PSENSE_FAIR = 0.10
```

with:

```python
PSENSE_FAIR = 0.10

# calibration_check.FINDINGS labels, routed by prefix. This is a copy, not an import:
# importing calibration_check would pull the ArviZ stack into this pure-JSON reader.
# test_calibration_check.py's contract test keeps the two in step.
BIASED_PREFIX = "biased ("
OVER_CONFIDENT_PREFIX = "over-confident ("
UNDER_CONFIDENT_PREFIX = "under-confident ("
SHAPE_MISMATCH_PREFIX = "shape mismatch ("
```

Edit 4.3, inserted after `_rate_calibration`:

In `check_diagnostics.py`, insert directly below the line `    return "poor", diagnosis`, leaving two blank lines between that line and the block:

```python
def _calibration_findings(cal: dict) -> list[str]:
    """Return the calibration findings, in calibration_check.py's order.

    A calibration.json written before findings existed falls back to its one
    diagnosis, unless that is empty or reads well-calibrated.
    """
    assessment = cal.get("assessment", {})
    if "findings" in assessment:
        return list(assessment["findings"])
    diagnosis = assessment.get("calibration_diagnosis", "")
    if not diagnosis or diagnosis == "well-calibrated":
        return []
    return [diagnosis]
```

Edit 4.4:

In `check_diagnostics.py`, replace:

```python
        report["calibration"] = {
            "rating": cal_rating,
            "diagnosis": cal_diagnosis,
        }
```

with:

```python
        report["calibration"] = {
            "rating": cal_rating,
            "diagnosis": cal_diagnosis,
            "findings": _calibration_findings(calibration),
        }
```

Edit 4.5, the per-finding steps. The mean-structure step follows D3. The re-check step replaces the spread step only for `over-confident` after a `biased` finding, because a shift cannot cause under-confidence.

In `check_diagnostics.py`, insert directly above the line `def suggest_next_steps(report: dict) -> list[str]:`, leaving two blank lines between the block and that line:

```python
def _spread_step(finding: str, rating: str) -> str:
    """The spread step: specific when the calibration rating is poor, general when fair."""
    if rating != "poor":
        return (
            "Calibration is fair but not excellent — consider tightening priors, "
            "switching to a heavier-tailed likelihood, or running a sensitivity "
            "check on the most informative observations."
        )
    if finding.startswith(OVER_CONFIDENT_PREFIX):
        return (
            "Calibration is over-confident — likelihood is too narrow for the "
            "data. Consider StudentT for continuous outcomes with heavy tails, "
            "NegBinomial for overdispersed counts, or hierarchical structure if "
            "groups have distinct variance."
        )
    return (
        "Calibration is under-confident — predictions are too uncertain. "
        "Tighten priors that are dominating the likelihood, or check whether "
        "the model is overcomplicated for the data."
    )


def _calibration_steps(cal: dict) -> list[str]:
    """One next step per calibration finding, in findings order (centre first)."""
    steps: list[str] = []
    shifted = False
    for finding in cal.get("findings", []):
        if finding.startswith(BIASED_PREFIX):
            shifted = True
            steps.append(
                f"Calibration is {finding} — the predictive's centre is off, so check "
                "the mean structure before the likelihood: a missing predictor or "
                "group effect, a wrong link or offset, or an intercept prior pulling "
                "the centre. Compare posterior-predictive means with observed means "
                "by group."
            )
        elif finding.startswith(OVER_CONFIDENT_PREFIX) and shifted:
            # A shift alone lowers interval coverage, so this may be its echo.
            steps.append(
                "Calibration is also over-confident, but a shift alone lowers interval "
                "coverage — fix the centre first, re-run calibration_check.py, and act "
                "on the spread only if the over-confidence remains."
            )
        elif finding.startswith((OVER_CONFIDENT_PREFIX, UNDER_CONFIDENT_PREFIX)):
            # A shift cannot cause under-confidence, so it keeps its spread step.
            steps.append(_spread_step(finding, cal.get("rating", "")))
        elif finding.startswith(SHAPE_MISMATCH_PREFIX):
            steps.append(
                "Calibration fails the PIT test, but neither a shift nor a spread "
                "error explains it — read the highlighted points on the PIT figure "
                "beside a posterior-predictive density overlay (azp.plot_ppc_dist), and "
                "consider a likelihood with the right shape: skewed, mixture, "
                "zero-inflated or hurdle."
            )
        else:
            steps.append(
                "Calibration check failed — re-examine the likelihood and the "
                "prior predictive range before interpreting posteriors."
            )
    return steps
```

Edit 4.6, the calibration block of `suggest_next_steps`:

In `check_diagnostics.py`, replace:

```python
    # ── Calibration ───────────────────────────────────────────────────
    cal = report.get("calibration", {})
    if "biased" in cal.get("diagnosis", ""):
        # Spread fits but the centre is off: the coverage deviation stays small, so
        # the rating alone would route this to the spread-oriented "fair" advice.
        steps.append(
            f"Calibration is {cal['diagnosis']} — the predictive's spread fits but its "
            "centre is off, so check the mean structure before the likelihood: a "
            "missing predictor or group effect, a wrong link or offset, or an "
            "intercept prior pulling the centre. Compare posterior-predictive means "
            "with observed means by group."
        )
    elif cal.get("rating") == "poor":
        diag = cal.get("diagnosis", "")
        if "over-confident" in diag:
            steps.append(
                "Calibration is over-confident — likelihood is too narrow for the "
                "data. Consider StudentT for continuous outcomes with heavy tails, "
                "NegBinomial for overdispersed counts, or hierarchical structure if "
                "groups have distinct variance."
            )
        elif "under-confident" in diag:
            steps.append(
                "Calibration is under-confident — predictions are too uncertain. "
                "Tighten priors that are dominating the likelihood, or check whether "
                "the model is overcomplicated for the data."
            )
        else:
            steps.append(
                "Calibration check failed — re-examine the likelihood and the "
                "prior predictive range before interpreting posteriors."
            )
    elif cal.get("rating") == "fair":
        steps.append(
            "Calibration is fair but not excellent — consider tightening priors, "
            "switching to a heavier-tailed likelihood, or running a sensitivity "
            "check on the most informative observations."
        )
```

with:

```python
    # ── Calibration ───────────────────────────────────────────────────
    steps.extend(_calibration_steps(report.get("calibration", {})))
```

Edit 4.1, in `calibration_check.py`:

In `calibration_check.py`, replace:

```python
# The five calibration findings, centre first.
```

with:

```python
# The five calibration findings, centre first. check_diagnostics.py routes on these
# labels by prefix and keeps its own copy; test_calibration_check.py holds the two in step.
```

- [ ] **Step 4: Run the tests to verify they pass**

Run the suite command. Expected: 0 failed, with 18 more tests passing than before this task.

Then confirm `check_diagnostics.py` still imports nothing from the arviz stack:

```bash
grep -nE "^(import|from) " skills/bayesian-workflow/scripts/check_diagnostics.py
```

Expected: exactly `import argparse`, `import json` and `import sys`.

- [ ] **Step 5: Commit**

```bash
git add skills/bayesian-workflow/scripts/check_diagnostics.py skills/bayesian-workflow/scripts/test_check_diagnostics.py skills/bayesian-workflow/scripts/calibration_check.py skills/bayesian-workflow/scripts/test_calibration_check.py
git commit -m "feat(bayesian-workflow): route one next step per calibration finding"
```

---

### Task 5: The pre-registered acceptance sweep

**Files:**
- Test: `skills/bayesian-workflow/scripts/test_calibration_check.py`. Edits 5.2–5.6: the imports, `_normal_model` gaining `seed=`, the docstring, and the sweep.
- Modify: `skills/bayesian-workflow/scripts/calibration_check.py`. Edit 5.1, the sweep pointer in the `assess_pit` docstring (D7).

**Interfaces:**
- Consumes: `assess_calibration` (Task 3), and the test-side constants from Task 1.
- Produces:
  - `_normal_model(loc, scale, *, seed=SEED, drop=())`, generalized as the spec asks;
  - `_skewed_model(*, seed)`;
  - `_sweep(build, use_loo)`;
  - `SWEEP_THRESHOLDS`, the spec's table as data;
  - the `CALIBRATION_SWEEP=1` gate.

**This task has no RED phase.** The sweep measures the finished implementation against thresholds the spec pre-registered before implementation. Run before Tasks 1–3, it would fail on missing keys, which proves nothing.

- [ ] **Step 1: Write the sweep**

Edit 5.2:

In `test_calibration_check.py`, replace:

```python
import json
import sys
```

with:

```python
import functools
import json
import operator
import os
import sys
from collections import Counter
```

Edit 5.3:

In `test_calibration_check.py`, replace:

```python
def _normal_model(loc, scale, *, drop=()):
```

with:

```python
def _normal_model(loc, scale, *, seed=SEED, drop=()):
```

Edit 5.4:

In `test_calibration_check.py`, replace:

```python
    rng = np.random.default_rng(SEED)
    y = rng.normal(0.0, TRUE_SCALE, size=N_OBS)
    mu = rng.normal(loc,
```

with:

```python
    rng = np.random.default_rng(seed)
    y = rng.normal(0.0, TRUE_SCALE, size=N_OBS)
    mu = rng.normal(loc,
```

Edit 5.5, the test module docstring:

In `test_calibration_check.py`, replace:

```python
The figure-rendering test skips unless matplotlib is installed (add --with matplotlib).
```

with:

```python
The figure-rendering test skips unless matplotlib is installed (add --with matplotlib).
The pre-registered acceptance sweep runs only with CALIBRATION_SWEEP=1 set (seeds 0-99
on both PIT paths, a minute or two); add -s to see the counts it records.
```

Edit 5.6, the sweep. `SWEEP_THRESHOLDS` must match the Global Constraints table exactly. A skewed fixture is not run on LOO, because PSIS fails on observations that sit outside the predictive's support in every draw.

Append to the end of `test_calibration_check.py`, two blank lines after the last definition:

```python
SWEEP = pytest.mark.skipif(
    os.environ.get('CALIBRATION_SWEEP') != '1',
    reason='pre-registered acceptance sweep: set CALIBRATION_SWEEP=1 (seeds 0-99, both paths)',
)
SWEEP_SEEDS = range(100)
MILDLY_NARROW_SCALE = 0.8
SMALL_SHIFT = 0.25
SKEWED_SHAPE = 2.0  # Gamma(2), standardized to mean 0 and sd 1: right-skewed
AT_LEAST, AT_MOST = operator.ge, operator.le


def _named(label):
    return lambda findings: label in findings


def _exactly(*labels):
    return lambda findings: findings == list(labels)


def _any_biased(findings):
    return HIGH in findings or LOW in findings


# The spec's pre-registered thresholds (specs/calibration-check-verdicts.md, "Acceptance"),
# set from the 2026-10-03 probe before implementation. A miss is a finding for the owner,
# never a reason to edit a threshold. "Named" counts any finding list that holds the label.
SWEEP_THRESHOLDS = {
    'calibrated': ((0.0, TRUE_SCALE), [('well-calibrated', _exactly(), AT_LEAST, 95)]),
    'too_narrow': ((0.0, OVER_CONFIDENT_SCALE), [('exactly [over-confident]', _exactly(OVER), AT_LEAST, 95)]),
    'too_wide': ((0.0, UNDER_CONFIDENT_SCALE), [('exactly [under-confident]', _exactly(UNDER), AT_LEAST, 95)]),
    'mildly_narrow': (
        (0.0, MILDLY_NARROW_SCALE),
        [('over-confident named', _named(OVER), AT_LEAST, 80), ('any biased named', _any_biased, AT_MOST, 5)],
    ),
    'shift_up': (
        (LOCATION_SHIFT, TRUE_SCALE),
        [('biased (predictions too high) named', _named(HIGH), AT_LEAST, 95),
         ('biased (predictions too low) named', _named(LOW), AT_MOST, 0)],
    ),
    'shift_down': (
        (-LOCATION_SHIFT, TRUE_SCALE),
        [('biased (predictions too low) named', _named(LOW), AT_LEAST, 95),
         ('biased (predictions too high) named', _named(HIGH), AT_MOST, 0)],
    ),
    'small_shift': ((SMALL_SHIFT, TRUE_SCALE), [('biased (predictions too high) named', _named(HIGH), AT_LEAST, 60)]),
    'shift_and_narrow': (
        (LOCATION_SHIFT, COMPOUND_NARROW_SCALE),
        [('exactly [biased (predictions too high), over-confident]', _exactly(HIGH, OVER), AT_LEAST, 95)],
    ),
    'shift_and_wide': (
        (LOCATION_SHIFT, COMPOUND_WIDE_SCALE),
        [('exactly [biased (predictions too high), under-confident]', _exactly(HIGH, UNDER), AT_LEAST, 95)],
    ),
}


def _skewed_model(*, seed):
    """y ~ N(0, 1) under a standardized Gamma(2) predictive: the right mean and spread, the wrong shape."""
    rng = np.random.default_rng(seed)
    y = rng.normal(0.0, TRUE_SCALE, size=N_OBS)
    mu = rng.normal(0.0, POSTERIOR_SD_OF_MEAN, size=(N_CHAIN, N_DRAW, 1))
    gamma = rng.gamma(SKEWED_SHAPE, 1.0, size=(N_CHAIN, N_DRAW, N_OBS))
    y_rep = mu + (gamma - SKEWED_SHAPE) / np.sqrt(SKEWED_SHAPE)
    return from_dict({'posterior_predictive': {'y': y_rep}, 'observed_data': {'y': y}}, dims={'y': ['obs']})


def _sweep(build, use_loo):
    """The findings for each sweep seed of the fixture `build(seed=...)` builds."""
    return [assess_calibration(build(seed=seed), 'y', use_loo=use_loo)['findings'] for seed in SWEEP_SEEDS]


@SWEEP
@PIT_PATHS
def test_acceptance_sweep_meets_the_pre_registered_thresholds(use_loo):
    path = 'loo_pit' if use_loo else 'ppc_pit'
    misses = []
    for fixture, ((loc, scale), checks) in SWEEP_THRESHOLDS.items():
        runs = _sweep(functools.partial(_normal_model, loc, scale), use_loo)
        for what, holds, compare, bound in checks:
            count = sum(1 for findings in runs if holds(findings))
            print(f'{path} {fixture}: {what} {count}/{len(runs)}')
            if not compare(count, bound):
                misses.append(f'{fixture}: {what} {count}, needs {compare.__name__} {bound}')
    if not use_loo:
        # PPC only: PSIS fails on observations outside the predictive's support in every draw.
        split = Counter(' and '.join(findings) or 'well-calibrated' for findings in _sweep(_skewed_model, use_loo))
        print(f'{path} skewed (a known limit, recorded with no threshold): {dict(split.most_common())}')
    assert not misses, misses
```

Edit 5.1, in `calibration_check.py`:

In `calibration_check.py`, replace:

```python
      over-confident, sometimes with biased (predictions too low).
```

with:

```python
      over-confident, sometimes with biased (predictions too low); the acceptance sweep
      in test_calibration_check.py records the split.
```

- [ ] **Step 2: Run the suite without the flag**

Run the suite command. Expected: 0 failed, with 2 more skipped than before this task. Both new skips carry the reason `pre-registered acceptance sweep: set CALIBRATION_SWEEP=1 …`.

- [ ] **Step 3: Run the sweep once and record its counts**

```bash
cd skills/bayesian-workflow/scripts && CALIBRATION_SWEEP=1 uv run --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray python -m pytest -q -s -k acceptance_sweep test_calibration_check.py
uv run --python 3.13 --with arviz --with arviz-stats --with numpy --with xarray python -c "import importlib.metadata as m; print('arviz-stats', m.version('arviz-stats'), 'arviz-plots', m.version('arviz-plots'))"
```

Expected: `2 passed`, with the rest of the file deselected, in about 80 s (78 s at planning). The run prints one line per count and the skewed split (PPC). F5 gives the counts the prototype measured. A planning run of this test on the scratch end state reproduced them exactly.

Copy every printed count line, the skewed split and the two versions into the commit message body below. The completion markup records them under this step.

**If any threshold misses, the test fails and lists the misses. Stop.** Do not commit, and do not edit a threshold or `SWEEP_THRESHOLDS`. Report the misses to the owner as a finding, with the printed counts.

- [ ] **Step 4: Commit**

```bash
git add skills/bayesian-workflow/scripts/test_calibration_check.py skills/bayesian-workflow/scripts/calibration_check.py
git commit -m "test(bayesian-workflow): pre-registered calibration acceptance sweep" -m "<the printed counts, the skewed split and the stack versions from Step 3>"
```

---

### Task 6: References, `CLAUDE.md`, and the skill gates

**Files:**
- Modify: `skills/bayesian-workflow/references/reporting.md` (edits 6.1–6.4), `references/model-criticism.md` (6.5), `references/publications.md` (6.6), and `CLAUDE.md` (6.7).

**Interfaces:** none. These are prose edits that describe Tasks 1–5's behaviour. No python code fence is added, removed or edited.

- [ ] **Step 1: Re-read before editing**

Plan 33 may have landed first, and it also edits root `CLAUDE.md`. Re-read the bayesian-workflow test-suite comment in `CLAUDE.md`, and the lines each edit below names. Every `old_string` below was checked against this branch at 2026-10-03, and each occurs exactly once. If one no longer matches, re-anchor on the current text and record a `> Deviation:` note.

- [ ] **Step 2: `reporting.md`**

Edit 6.1, the file-tree comments at lines 36–37. These lines sit inside a bare code fence. Only the comments change; the fence lines do not.

In `skills/bayesian-workflow/references/reporting.md`, replace:

```markdown
├── pit_ecdf.png                 # azp.plot_ppc_pit (or azp.plot_loo_pit)
├── pit_coverage.png             # azp.plot_ppc_pit(coverage=True)
```

with:

```markdown
├── pit_ecdf.png                 # calibration_check.py --save-plots
├── pit_coverage.png             # calibration_check.py --save-plots
```

Edit 6.2, lines 74–75. Readers are sent to the script, and told its figures share `calibration.json`'s PIT values.

In `skills/bayesian-workflow/references/reporting.md`, replace:

```markdown
For the calibration plots (`azp.plot_ppc_pit` / `azp.plot_loo_pit`), use `pc.savefig(...)` directly —
`scripts/calibration_check.py --save-plots --plot-dir <slug>` does this automatically with the right filenames.
```

with:

```markdown
For the calibration plots, run `scripts/calibration_check.py --save-plots --plot-dir <slug>`. It writes both
figures with the right filenames, drawn from the same PIT values as `calibration.json`, so the p-value on each
figure is the one the JSON records.
```

Edit 6.3, the static PIT-ECDF paragraph at line 165. What changes:
- the figure's p-value is named as `pit_p_value` / `coverage_p_value`, judged against `alpha`;
- "names every failing component" replaces the band and precedence sentences;
- the guidance on reading the curve's shape stays.

In `skills/bayesian-workflow/references/reporting.md`, replace:

```markdown
The PIT-ECDF plot tests whether the model's predictive distribution is calibrated — that is, whether stated credible levels match empirical coverage. It plots the difference between the empirical CDF of the probability integral transform values and the uniform reference, so a calibrated model stays near the dashed zero line; no band is drawn around it — the panel carries a uniformity-test p-value with the α it is judged against, and points are highlighted only when that test rejects. The band still exists in the numbers even though the figure omits it: `calibration_check.py` computes it and records the verdict in `calibration.json` as `pit_ecdf_inside_bands` / `coverage_ecdf_inside_bands`. Read its *shape*, not a global sign: in the raw PIT ECDF neither miscalibration sits wholly above or below the zero line — both trace a sign-flipping slope that integrates to ≈0. A predictive that is too narrow runs above the zero line in the lower half and below it in the upper half; one that is too broad mirrors that. A predictive with the right spread but an off-centre location is the exception: it sits above the zero line when predictions run too high and below it when they run too low. When only the PIT band fails, `calibration.json` diagnoses it as `biased (predictions too high)` or `biased (predictions too low)`; if the coverage band trips as well, the coverage verdict takes precedence. That label reads the failure as a shift, taking its direction from the sign of the mean deviation. A shape mismatch — a skewed predictive, a missing mode — can also fail the PIT band alone, so check the plot before trusting the direction: a shift keeps the curve on one side of the zero line, while a curve that crosses it points at shape rather than location, and its mean deviation can sit near zero with a sign that means nothing. For spread, the single-signed reading belongs to the coverage plot below. See [references/model-criticism.md](model-criticism.md).
```

with:

```markdown
The PIT-ECDF plot tests whether the model's predictive distribution is calibrated — that is, whether stated credible levels match empirical coverage. It plots the difference between the empirical CDF of the probability integral transform values and the uniform reference, so a calibrated model stays near the dashed zero line; no band is drawn around it — the panel carries a uniformity-test p-value with the α it is judged against, and points are highlighted only when that test rejects. That p-value is `pit_p_value` in `calibration.json` (`coverage_p_value` on the coverage plot below), judged against its `alpha`: `calibration_check.py` draws both figures from the same PIT values its verdict reads. Read the curve's *shape*, not a global sign: in the raw PIT ECDF neither miscalibration sits wholly above or below the zero line — both trace a sign-flipping slope that integrates to ≈0. A predictive that is too narrow runs above the zero line in the lower half and below it in the upper half; one that is too broad mirrors that. A predictive with the right spread but an off-centre location is the exception: it sits above the zero line when predictions run too high and below it when they run too low. A shift keeps the curve on one side of the zero line, while a curve that crosses it points at shape rather than location. `calibration.json` names every failing component, so one failed check never hides another: `biased (predictions too high)` or `biased (predictions too low)` when the PIT test fails and the mean PIT sits significantly off 0.5 (its `location_t`); `over-confident` or `under-confident` when the coverage test fails; both together when both hold; and `shape mismatch` when the PIT test fails and neither a shift nor a spread error explains it. For spread, the single-signed reading belongs to the coverage plot below. See [references/model-criticism.md](model-criticism.md).
```

Edit 6.4, the Assessment placeholder at line 171. It adds `shape mismatch` and compound findings.

In `skills/bayesian-workflow/references/reporting.md`, replace:

```markdown
**Assessment:** <1–2 sentences from `check_diagnostics()` calibration section — well-calibrated, over-confident, under-confident, or biased (predictions too high or too low), with the mean coverage deviation if available.>
```

with:

```markdown
**Assessment:** <1–2 sentences from `check_diagnostics()` calibration section — well-calibrated, or each finding it names: over-confident, under-confident, biased (predictions too high or too low), shape mismatch, or a compound such as biased and over-confident — with the mean coverage deviation if available.>
```

- [ ] **Step 3: `model-criticism.md`**

Edit 6.5 adds one prose sentence directly after the code fence that closes at line 110. The sentence warns about the false alarm, gives the rate formula, and points to the script's coverage figure. The fence and the gated SBC paragraph are not edited.

In `skills/bayesian-workflow/references/model-criticism.md`, replace:

```markdown
Refer to [this guide](https://arviz-devs.github.io/EABM/Chapters/Prior_posterior_predictive_checks.html#coverage) for detailed coverage interpretation — it's a treasure trove for the whole Bayesian workflow.
```

with:

```markdown
A direct `plot_ppc_pit(idata, coverage=True)` can print `p=0.00` on a calibrated model: when exactly half of an even number S of posterior-predictive draws fall below an observation, its PIT is exactly 0.5 and its coverage value exactly 0, which the test reads as impossible, and a calibrated fit holds such an observation with probability 1 − (1 − 1/(S+1))ⁿ over n observations (18% at S = 1000 and n = 200), so take the coverage figure from `scripts/calibration_check.py --save-plots`, which randomizes each PIT within its rank cell.

Refer to [this guide](https://arviz-devs.github.io/EABM/Chapters/Prior_posterior_predictive_checks.html#coverage) for detailed coverage interpretation — it's a treasure trove for the whole Bayesian workflow.
```

- [ ] **Step 4: `publications.md`**

Edit 6.6 adds the entry after Talts et al., per Q2's default.

In `skills/bayesian-workflow/references/publications.md`, replace:

```markdown
  unpublished PDF at sites.stat.columbia.edu/gelman/research/unpublished/sbc.pdf, not arXiv.
```

with:

```markdown
  unpublished PDF at sites.stat.columbia.edu/gelman/research/unpublished/sbc.pdf, not arXiv.
- Tesso & Vehtari (2026), *LOO-PIT predictive model checking* — arXiv:2603.02928. Cited as
  "Tesso & Vehtari 2026" for the `pot_c` uniformity test behind ArviZ's default PIT plots
  (`plot_ppc_pit`, `plot_loo_pit`, `plot_ecdf_pit`) and `scripts/calibration_check.py`'s verdicts.
```

- [ ] **Step 5: Check that no fence line changed**

```bash
git diff -U0 -- skills/bayesian-workflow | grep -cE '^[-+][[:space:]]*`{3}'
```

Expected: `0`.

- [ ] **Step 6: Re-measure the suite and update `CLAUDE.md`**

```bash
cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray python -m pytest -q 2>&1 | tail -1
```

Expected shape: `<P> passed, 3 skipped, <W> warnings in …`. The 3 skips are the rendering test and the two sweep items. The warnings are the four arviz RuntimeWarnings the current line already names.

Write the measured values into edit 6.7: `<T>` = `<P>` + 3, the collected total. Fill the placeholders from this run, never by arithmetic on old totals.

In `CLAUDE.md`, replace:

```markdown
# bayesian-workflow script tests (MCSE precision block + divergence-gate and calibration next
# steps + calibration verdicts on both PIT paths, --ci-prob plumbing and the --loo-pit group
# checks) — 59 tests
# (4 arviz RuntimeWarnings — "invalid value encountered in scalar divide" on the constant-parameter
# fixture — are expected and not silenced)
```

with:

```markdown
# bayesian-workflow script tests (MCSE precision block + divergence-gate and per-finding calibration
# next steps + calibration verdicts from one owned PIT on both paths: the pot_c rules, the figures
# drawing the JSON's own values, --ci-prob plumbing and the --loo-pit group checks) — <T> tests
# (this command reports <P> passed, 3 skipped: add --with matplotlib to run the figure-rendering
# test, and set CALIBRATION_SWEEP=1 to run the 2-path pre-registered acceptance sweep — seeds 0-99,
# about a minute and a half; -s prints its counts. <W> arviz RuntimeWarnings — "invalid value
# encountered in scalar divide" on the constant-parameter fixture — are expected and not silenced)
```

- [ ] **Step 7: Run the skill gates**

From the worktree root:

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py
uv run --python 3.13 python build/check_snippets.py skills/
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies
```

Expected: each exits 0. A Tier 1 failure here means a fence moved; undo the edit that moved it.

- [ ] **Step 8: Commit**

```bash
git add skills/bayesian-workflow/references/reporting.md skills/bayesian-workflow/references/model-criticism.md skills/bayesian-workflow/references/publications.md CLAUDE.md
git commit -m "docs(bayesian-workflow): calibration references name the owned PIT and every finding"
```

---

## Completion

After the final whole-branch review, run the writing-plans **Plan Completion Protocol**. This plan's specifics follow.

- **Markup.** Record Task 5 Step 3's printed counts, the skewed split and the stack versions under that step, as a `> Result:` block.
- **Tick the two items the spec closes,** in `specs/deferred_items.md`. Leave each item's own text as recorded.
  - Change the `- [ ]` on the item's first line to `- [x]`, and add the `→ done in plan 34 …` note after its last continuation line.
  - The deferred-tick-pass trap: re-count each section's `- [ ]` and `- [x]` afterwards, and confirm each changed by exactly one.
  - **Calibration diagnosis labels** (§ `deferred-triage (no plan; /deferred pass, branch deferred-triage-2026-09-28) — 2026-09-28`, the item starting "Calibration diagnosis labels: precedence misreads a pure location shift"). Both halves are done: `→ done in plan 34`.
  - **Split the durable Δ-ECDF reading rule** (§ `20-bayesian-workflow-book-integration — 2026-09-03`, the item starting "Split the durable Δ-ECDF reading rule"). Its `calibration_check.py` half is done: `→ done in plan 34 (the calibration_check.py half); the model-criticism.md half carries forward as the SBC-paragraph item under § 34-calibration-check-verdicts`.
- **Append** `## 34-calibration-check-verdicts — <completion date>` with these items. Each states its evidence, size and closure condition, per the Deferred-item schema.
  - **The SBC paragraph** in `skills/bayesian-workflow/references/model-criticism.md` ("What that call actually draws") keeps its version-pinned detail until upstream settles. When it does, keep the one durable instruction (read the p-value and the highlighted points, not a picture of a band) and shrink the version notes to a clause.
    - Evidence on arviz-plots 1.3.2 (2026-10-03): the envelope branch of `plot_ecdf_pit` still raises `TypeError: 'DataArray' object cannot be interpreted as an integer`. That was measured on PPC and LOO trees, not on the SBC call itself. And `pot_c` false-alarms on grid-valued PPC PITs after the coverage fold.
    - Carried from the 20-bayesian-workflow-book-integration item that plan 34 half-closed.
    - Size: quick-fix. Revisit if: an arviz-plots release fixes or removes `method="envelope"`.
  - **The skewed-predictive residual.** A skewed predictive with the right mean and variance is not labelled `shape mismatch`; this is the first known limit in `assess_pit`'s docstring.
    - Measured by Task 5's sweep (PPC, seeds 0–99, a standardized Gamma(2) predictive for N(0, 1) data): `<the recorded split>`.
    - No rule scored in the 2026-10-03 design pass labelled it `shape mismatch`.
    - Size: design. Revisit if: a real model's shape failure is reported as a shift or a spread error.
  - **Only if Q1 kept the spec's floor:** below arviz-stats 1.3.1, a super-uniform PIT gets an error instead of a verdict.
    - On arviz-stats 1.1.0–1.3.0, `pot_c` raises `ValueError: Cannot compute truncated Cauchy combination test. No p-values below 0.5 found.` on super-uniform PITs: exact grids, near-perfect fits, and typical n = 2–3. `calibration_check.py` then exits with that JSON error instead of a verdict, and `--save-plots` never runs.
    - arviz-stats 1.3.1 and later return p = 0.5 (Tesso & Vehtari 2026, Eq. 24).
    - The floor stayed at arviz-stats ≥ 1.1 / arviz-plots ≥ 1.1 at the owner's call (plan 34, Q1).
    - Size: quick-fix: raise the floor in the module docstring and the import error. Revisit if: a run on an older stack reports that error, or every stack the skill runs on reaches arviz-stats ≥ 1.3.1.
- **Upstream issues** for the two arviz-plots defects (the coverage-fold false alarm, and the envelope `TypeError`) stay out of scope. Filing is outward-facing and the owner's call; the spec offers a draft separately.
- **Retire.** `git mv` the plan to `specs/plans/completed/`. Retire the spec to `specs/completed/`, marked complete, because no other live plan implements it. Re-point both files' relative links for their new depth.
