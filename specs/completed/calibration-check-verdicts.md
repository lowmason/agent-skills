# calibration_check verdicts — Design Spec

**Status: COMPLETE (2026-10-03)** — implemented by plan 34 (`specs/plans/completed/34-calibration-check-verdicts.md`) and retired here. At the plan's Q2 the owner chose the citation "Tesso & Vehtari (2026)", which the code and `references/publications.md` use; it supersedes "Tesso et al." below.

Design approved 2026-10-03, section by section, in a brainstorming pass opened by the
2026-10-03 `/deferred` triage (the owner's paired Design selection). It closes two items in
`specs/deferred_items.md`:

- § `deferred-triage (no plan; /deferred pass, branch deferred-triage-2026-09-28) —
  2026-09-28`, item "Calibration diagnosis labels: precedence misreads a pure location
  shift…" — both halves: which failed check wins, and the direction given to a PIT-only
  failure.
- § `20-bayesian-workflow-book-integration — 2026-09-03`, item "Split the durable Δ-ECDF
  reading rule…" — its `calibration_check.py` half only. Its `model-criticism.md` half stays
  gated on upstream (see Closure).

`skills/bayesian-workflow/scripts/calibration_check.py` will compute its PIT values once,
judge them with the `pot_c` uniformity test its saved figures print, draw both figures from
the same values, and name every failing calibration component instead of letting one
failed check hide another. `check_diagnostics.py` routes its next steps on those named
components. The design also fixes a defect found while measuring: the saved PPC coverage
figure false-alarms on calibrated fits.

## Motivation

Every figure below was measured on 2026-10-03 on the skill's live test stack (arviz 1.3.0,
arviz-stats 1.3.3, arviz-plots 1.3.2, arviz-base 1.3.1), with 100 seeds per fixture unless
noted and `ci_prob` = 0.99. The fixtures are the test file's normal model: y ~ N(0, 1),
n = 200, and S = 1000 predictive draws (2 chains × 500) from N(loc, scale), with a posterior
sd of 0.05 on the mean. The probe scripts lived in `/tmp/calprobe/` and are not committed;
this section is the durable record.

### 1. The JSON and the figures run different tests

`save_pit_plot` calls `azp.plot_ppc_pit` / `azp.plot_loo_pit`. On arviz-plots 1.3.x both
default to `method="pot_c"` and print that test's p-value on the figure. The JSON's
`pit_ecdf_inside_bands` / `coverage_ecdf_inside_bands` come from the envelope band instead
(`difference_ecdf_pit` on the PPC path, `ecdf_pit` on the LOO path). Two docstrings claim
the two are the same: `assess_calibration` ("the same ΔECDF + simultaneous bands as the
plots") and `save_pit_plot` ("the bounds themselves feed the *_inside_bands values").

### 2. The saved PPC coverage figure false-alarms

`plot_ppc_pit(coverage=True)` prints `p=0.00(α=0.01)` and highlights suspicious points on a
calibrated model whenever any PIT value is exactly 0.5:

- With `method="pot_c"` the plot computes a Pareto-smoothed PIT (`get_ppc_pit` →
  `_pareto_pit_vec`). In the centre that is the empirical k/S: Pareto smoothing touches only
  the tails, and tie randomization only exact ties.
- When exactly S/2 of an even S draws fall below y, u = 0.5, and the coverage fold
  2|u − 0.5| is exactly 0.
- `pot_c` tests the smallest coverage value as P(U₍₁₎ ≤ 0) = 0. Its two-sided p is 0, its
  Cauchy term is effectively infinite, and the combined p collapses.

The chance that a calibrated fit holds such a point is 1 − (1 − 1/(S+1))ⁿ for even S:

| draws S | n = 200 | n = 1000 | n = 5000 |
|---|---|---|---|
| 1000 | 18% | 63% | 99% |
| 4000 | 5% | 22% | 71% |

Measured: the plot's coverage test rejected 21 of 100 calibrated PPC seeds; the envelope
band rejected 3. On calibrated seeds 0–39 it rejected 8, every one with a PIT of exactly
0.5, and spreading each PIT uniformly over its 1/S cell removed all 8. arviz-plots' own
figure printed `p=0.00(α=0.01)` on seed 5. The LOO figure is unaffected (1 of 100):
importance-weighted LOO-PIT values do not land on exactly 0.5 in practice. `references/reporting.md` tells
readers to trust exactly this p-value and highlighting, and
`references/model-criticism.md:107–109` tells them to call
`plot_ppc_pit(idata, coverage=True)` directly.

### 3. The labels misread

`assess_calibration` lets a failed coverage band win outright. It reads a PIT-only failure
as a shift, taking the direction from the sign of the rounded mean PIT ΔECDF. Current
labels, on the PPC path (LOO matches within one seed):

| Fixture | Current label |
|---|---|
| pure shift ±0.4 | biased 91, **over-confident 7 / 8**, well-calibrated 2 / 1 |
| shift 0.4, scale 0.7 | over-confident 100: **the shift is never named** |
| shift 0.4, scale 1.5 | under-confident 100: **the shift is never named** |
| the exact shape fixture recorded in the `:1396` item, N = 200 / 400 / 1000 | biased too low / too low / too high: **sign noise** (mean ΔECDF −0.0000, 0.0000, +0.0005) |

### Why the obvious fixes fail

- **Move the JSON to `pot_c` on the figures' own PIT values.** That imports the false alarm
  (21 of 100 calibrated PPC seeds). The plots' PPC Pareto-PIT entry point is internal, too:
  `arviz_plots.plots.utils_ppc.get_ppc_pit` dropped a `coverage` parameter between 1.3.1
  and 1.3.2, and does not exist on 1.1.
- **Move the figures to `method="envelope"`.** All four figures (PPC/LOO × PIT/coverage)
  raise `TypeError: 'DataArray' object cannot be interpreted as an integer` on 1.3.2. The
  envelope branch of `plot_ecdf_pit` hands `np.linspace` a DataArray count
  (`np.linspace(0, 1, sample_size_ds.to_array().max())`, `plots/ecdf_plot.py:296`).
- **Take a PIT-only failure's direction from the side of the out-of-band points** (the
  item's candidate rule), and use that one-sidedness to choose between failed checks. On a
  mildly narrow predictive (scale 0.8, no shift) the out-of-band points are one-sided on 53
  of 100 seeds, so the rule calls a shift that is not there. With mild narrowness, only one
  half-plane's excursion crosses the band.
- **Let a shift absorb a coverage shortfall as its echo.** A pure shift lowers
  central-interval coverage only to second order, so the data cannot tell the echo from real
  narrowness. On shift 0.4 with scale 0.7, this hides the narrowness on 100 of 100 seeds.

## Decisions

1. **The script owns the PIT.** The owner chose this over documenting the false alarm.
   PPC values are a seeded rank PIT, randomized within its cell. LOO values come from the
   public `loo_pit(…, pareto_pit=True)`.
2. **The JSON verdict is `pot_c` on those values** — the test the figures print, on the
   values the figures draw. The owner chose this over keeping the envelope band with
   corrected docstrings. On identical PIT values the two tests agree on 90–100% of verdicts
   per fixture, and share the false-alarm rate (PPC 3/100, LOO 2/100). `pot_c` flags more
   mild departures (PPC, current labels: mildly narrow 88 vs 83; shift 0.25, 70 vs 60). It
   is deterministic given the PIT, where the envelope band is a 1000-draw simulation, and
   upstream marks envelope for deprecation.
3. **Name every failing component.** The owner chose this over two alternatives: letting a
   shift absorb its echo, and keeping coverage first with only the PIT-only case fixed. It
   is the only rule scored that never hides a real component.
4. **Location is a t-test on the mean PIT, and it only explains a failed PIT test.** A
   spread error leaves the mean PIT at 0.5; a shift moves it many standard errors. Gating it
   on a failed PIT test keeps it an explanation rather than a third test, so it adds no
   false-alarm rate.
5. **No envelope band remains in the script.** `difference_ecdf_pit`, `ecdf_pit` and the
   band-simulation count go.

## Design

### Data flow

```
pit_values(dt, var_name, use_loo) ─► u   (1-D, pooled over all observation dims, strictly inside (0, 1))
   ├─► assess_pit(u, ci_prob)                                      ─► JSON assessment
   └─► save_pit_plot(u, path, var_name=…, coverage=…, ci_prob=…)  ─► azp.plot_ecdf_pit   (×2: PIT, coverage)
```

`assess_calibration(dt, var_name, use_loo, ci_prob=0.99)` keeps its signature, and becomes
`assess_pit(pit_values(dt, var_name, use_loo), ci_prob)`. `main()` calls `pit_values` once,
and hands the same array to `assess_pit` and to both `save_pit_plot` calls.

### PIT values — `pit_values(dt, var_name, use_loo, seed=PIT_SEED)`

- **PPC.** For each observation, k = #(draws < y) + ⌊U·(#(draws = y) + 1)⌋, and
  u = (k + V)/(S + 1). U and V are U(0, 1) draws from `np.random.default_rng(seed)`, and S
  is the number of posterior-predictive draws (`chain` × `draw`). When y and its draws are
  exchangeable, k is uniform on {0, …, S}, so u is exactly U(0, 1), and it can never equal
  0, 0.5 or 1. The floor term randomizes ties, so discrete data stays correct.
- **LOO.** `arviz_stats.loo_pit(dt, var_names=var_name, pareto_pit=True)`. These are the
  values `plot_loo_pit` computes, and Pareto smoothing keeps them off 0 and 1.
- Both paths flatten all observation dims into one array, which is how both arviz plot
  functions pool. `PIT_SEED = 214` is arviz's own default seed for PIT tie-breaking.

### Verdict rules — `assess_pit(pit, ci_prob=0.99)`

With α = 1 − `ci_prob`, n = len(u), and coverage levels c = 2|u − 0.5|:

| Quantity | Definition |
|---|---|
| `pit_p_value` | `pot_c` p-value of `u`: element `[0]` of `xarray.DataArray.azstats.uniformity_test(method='pot_c')` (Version floor) |
| `coverage_p_value` | `pot_c` p-value of `c` |
| `pit_test_passed` / `coverage_test_passed` | p ≥ α |
| `mean_pit` | mean(u) |
| `location_t` | (mean(u) − 0.5) / (sd(u)/√n), with sd at ddof = 1 |
| location fires | \|`location_t`\| exceeds the Student-t quantile at 1 − α/2 on n − 1 df, **and** the PIT test failed |
| `mean_coverage_deviation` | 0.5 − mean(c): the mean of the coverage ΔECDF; negative means intervals cover too little |

Findings, in this order (centre first):

1. **Location fires →** `biased (predictions too high)` when `location_t` < 0, since the
   observations then sit low in their predictive. Otherwise `biased (predictions too low)`.
2. **Coverage test fails →** `over-confident (predictions too certain)` when
   `mean_coverage_deviation` ≤ 0, otherwise `under-confident (predictions too uncertain)`.
3. **PIT test fails and neither of the above fired →** `shape mismatch (neither a shift
   nor a spread error)`.

`well_calibrated` means both tests passed, which holds exactly when `findings` is empty.
`calibration_diagnosis` joins the findings with `" and "`, or reads `well-calibrated`. The
five label strings are a module constant, `FINDINGS`.

Edge cases:
- **n < 2** raises `ValueError`, because the t-test is undefined. `main()` turns it into
  its JSON error exit.
- **sd(u) = 0** happens when every LOO-PIT is clamped to one tail. It counts as a
  significant shift in the direction of mean(u) − 0.5, and `location_t` is reported as
  `null`, since an infinite t is not valid JSON.

### JSON contract

`report["assessment"]` replaces its five keys with these eleven. The top-level `variable`,
`n_observations`, `pit_method` and `plots` keys stay.

```json
{
  "pit_p_value": 3.1e-07,
  "coverage_p_value": 0.0042,
  "alpha": 0.01,
  "pit_test_passed": false,
  "coverage_test_passed": false,
  "mean_pit": 0.3912,
  "location_t": -5.41,
  "mean_coverage_deviation": -0.0287,
  "findings": ["biased (predictions too high)", "over-confident (predictions too certain)"],
  "well_calibrated": false,
  "calibration_diagnosis": "biased (predictions too high) and over-confident (predictions too certain)"
}
```

- **Rounding.** p-values are unrounded. `mean_pit` and `mean_coverage_deviation` round to
  4 dp, and `location_t` to 2 dp.
- **`alpha` is recorded** because the report stores `ci_prob` nowhere else.
- **Removed keys:** `pit_ecdf_inside_bands` and `coverage_ecdf_inside_bands`.
- **`n_observations`** becomes the number of pooled PIT values. Today it is the first
  dimension's length, which is wrong for a multi-dimensional observed variable.

Every finding traces to a number in the record:
- **biased →** `location_t`.
- **spread →** `coverage_p_value` and the sign of `mean_coverage_deviation`.
- **shape →** `pit_p_value` beside a small `location_t`.

### Figures — `save_pit_plot(pit, output_path, *, var_name, coverage=False, ci_prob=0.99)`

`save_pit_plot` wraps `pit` in a one-variable `xarray.DataTree` named `var_name`, and calls
public `azp.plot_ecdf_pit`. It passes `coverage=coverage`, `envelope_prob=ci_prob` and
`method='pot_c'`. That last is explicit, not left to the default. `pot_c` is the default on
every version checked, but pinning it keeps "the same test as the JSON" from depending on a
future default. The x-label is `PIT`, or `ETI %` for coverage, as `plot_ppc_pit` sets them.
Plot paths and filenames are unchanged. The figure and the JSON read the same values with
the same test, so the p-value printed on each figure is the JSON's `pit_p_value` or
`coverage_p_value`.

**Binary data.** `plot_ppc_pit` warns when a variable looks binary, pointing to
`plot_ppc_pava`. Bypassing it would drop that warning silently. So `main()` prints its own
stderr warning when every observed value is 0 or 1, naming `plot_ppc_pava`, and does so on
every run, since the JSON verdict is PIT-based too. The script does not import arviz's
internal `warn_if_binary`.

### Routing — `check_diagnostics.py`

- **`report["calibration"]` gains `findings`**, read from the assessment. When the key is
  absent (a `calibration.json` written before this change), it falls back to
  `[calibration_diagnosis]`, unless that is empty or reads `well-calibrated`.
- **The rating rule is unchanged.**
- **`suggest_next_steps` emits one step per finding**, in findings order, routed by the
  label's prefix:

| Finding | Step |
|---|---|
| `biased (…)` | today's mean-structure step |
| `over-confident (…)` after a `biased` finding | a re-check step, in place of the spread step: a shift alone lowers interval coverage, so fix the centre, re-run `calibration_check.py`, and act on the spread only if the over-confidence remains |
| `over-confident (…)` / `under-confident (…)` otherwise, including `under-confident` after a shift (a shift cannot cause it) | today's specific spread step when the rating is `poor`; today's `fair` step when it is `fair` |
| `shape mismatch (…)` | new: the PIT fails, but neither a shift nor a spread error explains it. Read the highlighted points on the PIT figure beside a posterior-predictive density overlay, and consider a likelihood with the right shape (skewed, mixture, zero-inflated or hurdle) |
| anything else | today's generic "calibration check failed" step |

- **`_build_summary` is unchanged.**
- **The label strings are duplicated.** `check_diagnostics.py` must not import
  `calibration_check.py`, because that would pull the arviz stack into a pure-JSON reader.
  A contract test keeps the two copies in step.

### Docs

- **`calibration_check.py`:**
  - the module docstring;
  - `pit_values`: the two constructions, and why a grid PIT breaks `pot_c`'s coverage test;
  - `assess_pit` / `assess_calibration`: the rules, and the known limits below;
  - `save_pit_plot`: same values and same test as the JSON. Its current claim becomes true.
- **`references/reporting.md`:**
  - lines 36–37: the file-tree comments for `pit_ecdf.png` / `pit_coverage.png` name
    `calibration_check.py --save-plots`;
  - lines 74–75: send readers to the script, and say its figures share
    `calibration.json`'s PIT values;
  - line 165, the static PIT-ECDF paragraph:
    - the figure's p-value is `pit_p_value` / `coverage_p_value`, judged against `alpha`;
    - "names every failing component" replaces the band and precedence sentences;
    - the guidance on reading the curve's shape stays;
  - line 171, the Assessment placeholder: add `shape mismatch` and compound findings.
- **`references/model-criticism.md`:** one prose sentence directly after the code fence
  that closes at line 110. It warns that a direct `plot_ppc_pit(…, coverage=True)` can print
  p = 0.00 on a calibrated model, gives the rate formula, and points to
  `calibration_check.py`'s coverage figure. The fence itself is not edited, and neither is
  the gated SBC paragraph.
- **`references/publications.md`:** the Tesso et al. entry (Provenance).
- **Root `CLAUDE.md`:** the bayesian-workflow test-suite line (count and description),
  re-measured, plus the sweep flag (Testing).
- **Unchanged:** `SKILL.md`, `references/visualize.md`, `README.md`. Their direct calls use
  the raw-PIT view or LOO, which the defect does not reach.
- **Gates for the skill edits** (root `CLAUDE.md` "Commands"): the frontmatter and
  provenance lints, Tier 1 of the snippet gate, and the dependency-drift check.

### Known limits

Both are stated in the `assess_pit` docstring:

- **A skewed predictive with the right mean and variance is not labelled
  `shape mismatch`.** The probe used a standardized Gamma(2) predictive for N(0, 1) data,
  which has a hard support edge at −√2. On the PPC path it reads `over-confident` on 83 of
  100 seeds, and `biased (predictions too low) and over-confident` on 13. None of the rules
  scored labelled it `shape mismatch`.
- **The t-test treats PIT values as independent.** Heavy posterior dependence (few
  observations per parameter) inflates it. Read a borderline `biased` call against the PIT
  figure.

### Version floor

- **Floors:** arviz-stats ≥ 1.1 and arviz-plots ≥ 1.1.
- **Verified end to end on two stacks.** The floor stack is arviz-plots 1.1.0,
  arviz-stats 1.1.0 and arviz-base 1.1.0. It needs matplotlib < 3.11: arviz-plots 1.1.0
  fails to import against newer matplotlib, which no longer exposes `matplotlib.style.core`.
  The live stack is arviz-plots 1.3.2, arviz-stats 1.3.3 and arviz-base 1.3.1. On both:
  - `plot_ecdf_pit` defaults to `pot_c`, and accepts the one-variable DataTree;
  - the p-value it prints equals the accessor's in all 12 cases checked (calibrated, too
    narrow and shift, × PPC/LOO, × PIT/coverage);
  - `loo_pit(pareto_pit=True)` works.

  Parameter names alone were also checked on arviz-stats 1.2.0 and 1.3.0, and on
  arviz-plots 1.3.1.
- **Read the p-value by index, never by unpacking.** `uniformity_test` returns
  `(p, shapley)` on arviz-stats 1.1, and `(p, shapley, shapley_unsorted)` on 1.3, so take
  element `[0]`.
- **The guarantee is figure = JSON within one stack.** `pot_c`'s p for the same values
  differs across arviz-stats versions: 0.14 vs 0.17 on one calibrated PIT array, 1.1.0 vs
  1.3.3. The sweep thresholds were measured on the live stack.
- **Removed:** the pre-1.0 `difference_ecdf_pit` import fallback.
- **scipy**, used for the t quantile, is already an arviz-stats dependency.

### Provenance

`calibration_check.py` arrived with the initial `bayesian-workflow` commit (2d99584). It is
part of the skill adapted from Alexandre Andorra's PyMC skill (MIT; see `NOTICE`). The
rewrite keeps that attribution, and needs no `NOTICE` edit.

`pot_c` is cited as ArviZ cites it: Tesso et al., *LOO-PIT predictive model checking*,
arXiv:2603.02928 (2026), from the `plot_ppc_pit` and `plot_ecdf_pit` docstrings on
arviz-plots 1.3.2. The citation is author-year, in original wording, with no text reproduced
— the way `references/publications.md` already cites Säilynoja et al. 2022 for the envelope
band. `references/publications.md` gains a Tesso et al. entry after Talts et al., for the
`pot_c` test behind ArviZ's default PIT plots and the script's verdicts.

## Testing

### Unit tests — always on, deterministic

`test_calibration_check.py`:

- **`pit_values`:**
  - values sit strictly inside (0, 1), and are repeatable for a fixed seed;
  - the regression: y placed with exactly S/2 of an even S draws below it gives u ≠ 0.5,
    and its coverage test passes;
  - discrete ties land inside their cell;
  - a 2-D observed variable is pooled;
  - LOO values equal `loo_pit(…, pareto_pit=True)`.
- **Rules,** run through `assess_pit` on exact-quantile PIT arrays (no sampling):
  - calibrated; shifted up and down; too narrow; too wide; both compounds;
  - the exact shape fixture of the `:1396` item at N = 200, 400 and 1000;
  - n < 2 raises, and sd(u) = 0 reads as a shift.
- **Invariants:**
  - `findings == []` exactly when `well_calibrated`;
  - `(calibration_diagnosis == 'well-calibrated') is well_calibrated`;
  - each `*_test_passed` equals its p ≥ `alpha`;
  - `mean_coverage_deviation == round(0.5 − mean(c), 4)`.
- **The figures share the JSON's values:**
  - with `azp.plot_ecdf_pit` monkeypatched to capture its input, both figures receive the
    PIT values the assessment used, with `coverage=`, `envelope_prob=ci_prob` and
    `method='pot_c'`;
  - one rendering test, gated by `pytest.importorskip('matplotlib')`, checks that the
    printed p-value equals `f'{pit_p_value:.2f}'`.
- **Re-measured:**
  - the seeded normal-fixture tests on both PIT paths, since per-seed outcomes change with
    the test;
  - the CLI tests: renamed keys, and `--ci-prob 0.01` → `alpha == 0.99`.
- **Contract:** every label in `calibration_check.FINDINGS` reaches a non-generic step in
  `check_diagnostics.suggest_next_steps`.
- **Binary data:** a 0/1 observed variable prints the `plot_ppc_pava` warning on stderr,
  and a continuous one prints nothing.

`test_check_diagnostics.py`:

- every row of the routing table, including the re-check step replacing the spread step
  after a `biased` finding, and `under-confident` after a shift keeping its spread step;
- the legacy-file fallback;
- the `_calibration` helper moves to the new contract.

### Acceptance — a pre-registered seed sweep

An env-gated test in `test_calibration_check.py` runs when `CALIBRATION_SWEEP=1`. It sweeps
seeds 0–99 on both PIT paths at `ci_prob` = 0.99. The flag is documented on the root
`CLAUDE.md` test line. The plan runs the sweep once and records the counts.

The fixtures:
- **Normal fixtures.** The test file's `_normal_model`, generalized to take the seed and
  (loc, scale):
  - y ~ N(0, 1), with n = 200;
  - μ ~ N(loc, 0.05) per draw, over 2 chains × 500 draws (S = 1000);
  - y_rep ~ N(μ, scale);
  - the log-likelihood is the same normal density.
- **Skewed fixture,** PPC only:
  - y ~ N(0, 1);
  - μ ~ N(0, 0.05) per draw, and y_rep = μ + (G − 2)/√2 with G ~ Gamma(2, 1), a standardized
    Gamma(2) predictive;
  - LOO is skipped, because PSIS fails on observations that sit outside the predictive's
    support in every draw.

The thresholds were set from the 2026-10-03 probe before implementation, below its measured
values. An implementation that misses one is a finding for the owner, never a reason to edit
the threshold. "Named" counts any finding list that contains the label.

| Fixture (loc, scale) | Pass condition, per path, of 100 | Probe, PPC / LOO |
|---|---|---|
| calibrated (0, 1) | `well-calibrated` ≥ 95 | 97 / 98 |
| too narrow (0, 0.3) | exactly `[over-confident]` ≥ 95 | 98 / 98 |
| too wide (0, 3.0) | exactly `[under-confident]` ≥ 95 | 99 / 99 |
| mildly narrow (0, 0.8) | `over-confident` named ≥ 80; any `biased` named ≤ 5 | 88, 1 / 87, 1 |
| shift up (0.4, 1) and down (−0.4, 1) | right-direction `biased` named ≥ 95; wrong direction 0 | 100 and 99 / 100 and 99; wrong 0 |
| small shift (0.25, 1) | `biased (predictions too high)` named ≥ 60 | 69 / 70 |
| shift + narrow (0.4, 0.7) | exactly `[biased (predictions too high), over-confident]` ≥ 95 | 100 / 100 |
| shift + wide (0.4, 1.5) | exactly `[biased (predictions too high), under-confident]` ≥ 95 | 100 / 100 |
| skewed predictive, PPC only | recorded, no threshold: a known limit | `shape mismatch` 0 |

## Planning handoff

- **Plan id:** the next free integer at planning time. Plans 32 and 33 are live on this
  branch, so it is 34 unless another plan lands first.
- **Sequencing with plan 33** (`specs/plans/33-snippet-per-block-fixtures.md`). Both plans
  edit root `CLAUDE.md` and bayesian-workflow references, and plan 33 hard-codes measured
  snippet-block and advisory counts.
  - **`CLAUDE.md`:** plan 33 changes the build-suite and Tier 3 lines; this design changes
    the bayesian-workflow suite line.
  - **References:** plan 33 changes fence info strings in `model-comparison.md` and
    `visualize.md`. This design changes prose in `reporting.md`, `model-criticism.md` and
    `publications.md`, plus comments inside `reporting.md`'s bare-fenced file tree.
  - **No python fence is added, removed or edited,** so plan 33's counts hold whichever
    plan lands first. Either order works; re-read `CLAUDE.md` before editing it.

## Closure

The plan's completion protocol does the ticking:

- **The `:1396` item, both halves:** `- [x] … → done in plan <id>`.
- **The `:822` item:** ticked `→ done in plan <id>` for its `calibration_check.py` half,
  with a pointer to a new item that carries the `model-criticism.md` half forward. The
  item's own text is left as recorded. The new item goes in the plan's own deferred
  section:
  - **Subject:** the SBC paragraph in `references/model-criticism.md` ("What that call
    actually draws") keeps its version-pinned detail until upstream settles.
  - **Evidence on arviz-plots 1.3.2:** the envelope branch of `plot_ecdf_pit` still raises
    the `TypeError` above (measured on PPC and LOO trees, not on the SBC call itself), and
    `pot_c` false-alarms on grid-valued PPC PITs after the coverage fold.
  - **Size:** quick-fix. **Revisit if:** an arviz-plots release fixes or removes
    `method="envelope"`.
- **A second new item: the skewed-predictive residual** from Known limits, with the
  measured split. **Size:** design. **Revisit if:** a real model's shape failure is
  reported as a shift or a spread error.

## Out of scope

- The `model-criticism.md` SBC paragraph. It is gated, and the new item carries it.
- Filing upstream issues for the two arviz-plots defects: the coverage-fold false alarm,
  and the envelope `TypeError`. Filing is outward-facing and the owner's call; a draft is
  offered separately.
- `prit_c` and `piet_c`, any envelope band, and the snippet preamble's pins
  (`build/snippet_preamble.py`).
