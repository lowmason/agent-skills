# Diagnostics Harness Verdicts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop bayesian-workflow's two diagnostics scripts from reporting a clean result for checks that never ran or that failed (audit-3-10-26 X1 and X2), and move their Pareto-k bands to loo's sample-size threshold (F8).

**Architecture:** `diagnose_model.py` is the writer: it runs the ArviZ checks and writes `diagnostics.json`. It gains a `checked` flag on its three sampler-stat blocks, reads tree depth from `sample_stats` itself on both of its code paths, counts Pareto k against `good_k = min(1 − 1/log10 S, 0.7)`, and lists a failing MCSE and an uncomputed LOO in its overall verdict. `check_diagnostics.py` is the reader: stdlib only, it turns the JSON into ratings and next steps. It gives each failed or missing check its own next step. It prints the all-clear only when every required check ran and passed, and names the optional checks that did not run. Every task is test-first, and the last task runs the three-script pipeline on real NumPyro output.

**Tech Stack:** Python 3.13 through `uv run`; ArviZ 1.x (arviz-base, arviz-stats) and NumPy in `diagnose_model.py`; the stdlib only in `check_diagnostics.py`; pytest; NumPyro and JAX for the acceptance run.

**Spec:** none. The three backlog items carry their own fixes: `specs/deferred_items.md`, section `audit-3-10-26 routing (no plan; re-verification pass, branch claude/quizzical-hermann-814d89) — 2026-10-18`, items X1, X2 and F8. That section is not on `main` yet. It is commit `4b683a4` on branch `claude/quizzical-hermann-814d89`, unpushed until the owner approves, so read it with `git show 4b683a4:specs/deferred_items.md`. The findings themselves are in `specs/audit-3-10-26.md`: §X1, §X2, F8 in the F table, and §B3.

## Global Constraints

Every task's requirements include these.

- **`check_diagnostics.py` stays stdlib-only and runs on Python 3.11.** Plan 53 gives it the header floor `>=3.11` with no dependencies (its DF3). So no f-string may reuse its own quote character inside a replacement field: PEP 701 is Python 3.12 and later. `test_check_diagnostics.py` stays stdlib plus pytest.
- **`diagnose_model.py` gains no third-party import.** Plan 53's header row for it (`>=3.12`, `arviz>=1.0`, `numpy>=2.0`, `h5netcdf>=1.0`, `h5py>=3.0`) then still holds. `math` is stdlib and already imported.
- **Shared thresholds are named constants in both scripts**: `REL_MCSE_OK = 0.05` and `PARETO_K_MAX = 0.7`. One test in `test_diagnose_model.py` pins the two copies equal. The reader never imports the writer, because the writer pulls in ArviZ (the same reason `check_diagnostics.py` copies `calibration_check.py`'s finding prefixes).
- **Red first.** Write each task's tests, run them, and read each failure reason before you write code. Each task lists its expected failures and their reasons.
- **Test counts are deltas** from Task 1, Step 2's baseline. On 2026-10-18 at `668b8c3` that baseline read `129 passed, 3 skipped`, on the floating stack the suite command resolves.
- **Simple commands.** Every command is one command, with no `cd … &&`, pipe or loop, because a worktree-isolated session refuses compound shell. `uv run --directory <dir>` runs pytest from the suite's directory, so the tests' bare imports work.
- **Find code by its text, not by line number.** Plan 53 inserts a shebang and a PEP 723 block at the top of both scripts, which shifts every line. Each replace block below quotes the exact text to find, and it occurs once in the file at that point of the plan.
- **Match each file's style.** Both scripts and their tests use double quotes throughout, so new code there does too (DF10). The acceptance script, which is never committed, uses single quotes.
- **Leave these alone**: `CLAUDE.md` (199 of 200 lines, and plans 52, 53 and 55 edit it), the skill's `SKILL.md` (plan 53 edits its invocations and frontmatter), `calibration_check.py`, and `skills/tune-hyperparameters/SKILL.md:142` (backlog item G4, which belongs to the G-A plan).
- **Commit trailer.** Each commit message ends with the executing session's own `Co-Authored-By:` line, added as the last `-m`. Subagent-authored commits keep that same line. Check with `git log -1 --format=%B`.
- **Push or merge nothing** without the owner's go-ahead.

## Decisions

- **D1** (owner, planning, 2026-10-18): Pareto-k, the option "Sample-size cutoff": "Cut at loo's current threshold, min(1 − 1/log10 S, 0.7). diagnose_model.py computes it from the draw count, so every ArviZ version still gives the same rating and the recorded reason holds. It stays 0.7 at 4×1000 draws and is about 0.656 at the 4×200 exploring size. reloo and loo_moment_match already default to it. The JSON carries it as good_k." The bands, as the option showed them: k ≤ good_k is reliable, so LOO rates excellent; good_k < k ≤ 0.7 is unreliable, so LOO rates fair with a "more draws may fix it" step; k > 0.7 or a non-finite k is unreliable, so LOO rates poor with the remedies named. Applied in: Task 4.
- **D2** (owner, planning, 2026-10-18): checks that never ran, the option "All three": "Tree depth (no reached_max_tree_depth), E-BFMI (no energy, which NumPyro stores only if extra_fields asks for it) and divergences (no diverging, as on a hand-built BlackJAX InferenceData). Each writes checked: false, and the all-clear names it." Applied in: Tasks 2 and 3.
- **D3** (owner, plan review, 2026-10-19): the two scope extras, the option "Keep as planned": "Keep both extras in plan 56 as planned: the E-BFMI next step (DF11) and the narrow writer verdict (DF12)." Applied in: Task 3 (DF11) and Task 1 (DF12), unchanged.

---

## Planning record

### Facts measured while planning (2026-10-18, at `668b8c3`)

- **Baseline.** The bayesian-workflow suite reads `129 passed, 3 skipped` on the floating stack its command resolves (arviz 1.3.0, arviz-stats 1.3.3, arviz-base 1.3.1, numpy 2.5.4).
- **X1, reproduced.** Start from a report in which every check ran and passed, and change one input: a max relative MCSE of 0.058, a LOO that was not computed, or no calibration file. Each still gets "All diagnostics are within acceptable bounds — proceed to interpretation." `check_diagnostics.py` never reads `precision`. `diagnose_model.py`'s own verdict says "Model is ready for interpretation." for an InferenceData with posterior-predictive draws and no `log_likelihood` group.
- **X2, reproduced on the pinned stack (arviz 1.3.0, arviz-stats 1.3.2) and the floating one.** A synthetic `az.from_dict` with `reached_max_tree_depth` true on all 2,000 draws gets `treedepth: {'ok': True, 'n_max': 0, 'pct': 0.0}` and `all_ok: True` on the `arviz_stats.diagnose` path. The fallback path writes no `treedepth` block for either flag name. `arviz_stats.diagnose` reads only `reached_max_treedepth`, and sets `has_errors` when that flag shows saturation. `az.from_numpyro` (arviz-base 1.3.1) writes `tree_depth = log2(num_steps) + 1` and `reached_max_tree_depth`, and only when `num_steps` is collected.
- **The backlog fix alone is not enough.** Folding tree depth into `all_ok` still ends in the all-clear: the reader rates convergence fair, adds no step for a non-parameter flag, and its summary says "flags on some parameters". A lone E-BFMI failure ends the same way. That is a finding of this planning pass, folded into Task 3 (DF11).
- **Unchecked reads as passed.** With no `energy` stat the bfmi block is `{'ok': True, 'failed_chains': []}`. With no `diverging` stat the divergences block is `{'count': 0, 'pct': 0.0, 'ok': True}`. D2 settles this.
- **F8.** arviz-stats' `loo` computes `good_k = min(1 − 1/log10 S, 0.7)` and exposes it as `loo.good_k`: 0.65554 at S = 800 on the pin, equal to the formula above. `reloo` and `loo_moment_match` default their `k_threshold` to it. `loo_moment_match` builds its log-density functions itself only for PyMC and Bambi. `reloo` and `loo_kfold` refit through an `azs.SamplingWrapper` subclass. All three exist on arviz-stats 1.3.2.
- **Who reads the changed JSON keys.** Only `check_diagnostics.py` reads `n_marginal`, `n_bad`, `pareto_k`, `treedepth`, `bfmi` or `divergences`. `compare_experiments.py` (track-model-experiments) reads `diagnostics.json`, but none of these keys (backlog item X7).
- **Snippet tiers.** The Pareto-k snippet in `references/model-criticism.md` (the fence after its Pareto k table) is parsed by Tier 1. Tier 3 does not execute it ("not executed: unbound names ['loo']"), before and after this plan's edit. The probe above is the evidence that `loo.good_k` exists.

### Prototype and replay

On 2026-10-18, Tasks 1–4 were written test-first in a scratch clone of `668b8c3`, and Task 5 ran there. The whole suite passed on the pinned stack, `test_check_diagnostics.py` passed under Python 3.11, snippet Tiers 1, 2 and 3 exited 0, and all eight commit lints passed.

A script then replayed this plan's blocks in a fresh clone of `668b8c3`, one step at a time, in task order:
- Each replace matched its quoted text exactly once, on whole lines.
- Each red run printed the failing tests and reasons its step lists, and each green run printed its delta, on the floating stack.
- Both scripts and all four Markdown files came out byte-identical to the prototype. So did the two test files, except that one Task 3 test (`test_the_convergence_summary_names_parameters_and_sampler_flags`) sits at the end of its block here, not mid-file, and calls its local `report`.
- Task 5's commands, run as written from the clone's root, printed every Expected line of its Steps 2–4. The pinned-stack suite, the 3.11 run and Tier 2 passed there too.
- Tier 3 and the commit lints were not re-run there, because the Markdown they read is byte-identical to the prototype's.

### Settled defaults (the owner reviews these)

- **DF1, the all-clear needs calibration.** Without `--calibration`, the reader adds "Calibration was not checked …" instead of an all-clear that lists calibration as missing. `references/reporting.md` makes the all-clear conditional on good calibration, and `references/model-criticism.md` says calibration is mandatory for every model. The backlog item's fix reads "build the all-clear from the sections present and list the rest"; this is the stricter reading.
- **DF2, required and optional checks.** Convergence, Monte Carlo precision, LOO and calibration are required. Each one that is missing or not computed gets a step, and the all-clear needs all four at a passing rating: convergence excellent or good, the other three excellent. Prior sensitivity and the three sampler checks are optional. The all-clear names each one that did not run in a "Not checked:" step, with how to run it.
- **DF3, a gate behind the steps.** The all-clear prints only when no step was added and every required section passed. When no step applies but a required section did not pass, one step names those sections instead. Today that happens for a legacy calibration file that rates fair and names no finding. With the gate, a future failure mode without a step of its own cannot reach the all-clear either.
- **DF4, precision with no usable parameter** (every parameter constant) counts as not computed. `check_precision` writes a max of 0.0 there, which would otherwise pass.
- **DF5, old diagnostics files.** A sampler block with no `checked` key comes from a `diagnostics.json` written before this plan, and counts as checked. A missing block counts as not checked.
- **DF6, the fallback path** (arviz-stats < 1.0) computes no E-BFMI, so it always writes `bfmi: {"checked": False}`. It now reads both tree-depth flags itself.
- **DF7, the summary names sampler flags.** A fair or poor convergence line lists the flagged parameters first, then the sampler flags ("flags on a; max treedepth saturation"), and never says "some parameters" for a flag. The poor line becomes "Poor convergence — flags on …" to match.
- **DF8, a `diagnostics.json` written before `good_k`.** Its `n_bad` counted only k > 0.7, so the reader reads it as `n_high`.
- **DF9, how `good_k` is computed.** From the nominal S = chains × draws, as loo does, and rounded to four places in the JSON. The reader rates LOO from the counts, never by comparing `max` with the rounded `good_k`.
- **DF10, quote style** follows each file: double quotes in both scripts and their tests.
- **DF11, the E-BFMI fold-in.** A lone low E-BFMI gets its own next step (Task 3). This planning pass found it: the same function and the same false all-clear as tree depth. The owner kept it at plan review (D3).
- **DF12, the writer's verdict stays narrow.** `diagnose_model.py`'s overall verdict gains only the two issues X1 names: a failing MCSE and a LOO that did not run. A sampler check that never ran adds no issue, so Task 5's unchecked run still reads "Model is ready for interpretation." there. The reader's all-clear names the check (D2), and `SKILL.md`'s pipeline ends with the reader. The owner kept it at plan review (D3).

### Section 34 (calibration-check verdicts): no item folded

The brief asked to fold in any open item of section `34-calibration-check-verdicts` that fits. None does:
- **Shrink the SBC paragraph:** a watch item whose trigger, an arviz-plots release that fixes or removes `method="envelope"`, has not fired. It edits `model-criticism.md` prose, not the scripts.
- **Skewed-predictive residual:** a design item (no rule labels the case yet), in `calibration_check.py`.
- **Below arviz-stats 1.3.1, a super-uniform PIT errors:** a watch item. Raising the floor would reverse plan 34's Q1 owner call, and would conflict with plan 53's `arviz-stats>=1.1` header row for `calibration_check.py`.
- **The saved figures crop their x-label:** a watch item whose trigger is an owner call (plan 34's Q3 kept `plot_ppc_pit` parity), in `calibration_check.py`.

The audit's B3 grouped section 34 with X1, X2 and F8 when four of its items were open. Three of them (the NaN guard, the fair step and the `--loo-pit` file names) were done by 2026-10-08.

### Couplings

- **Plan 53 (portability, not executed).** Its Task 10 adds `#!/usr/bin/env python3` and a PEP 723 block at the top of both scripts. `check_diagnostics.py` gets `>=3.11` with no dependencies; `diagnose_model.py` gets `>=3.12` with arviz, numpy, h5netcdf and h5py. Its Task 11 rewrites one line of `references/diagnostics.md`, the `python <this-skill-dir>/scripts/diagnose_model.py` command, to `uv run`. Neither touches text that this plan replaces, and this plan keeps both headers valid (Global Constraints). Whichever plan lands second, line numbers shift by the header's length, which is why every block here quotes text.
- **Plan 55 (test-suite registry, not executed).** It replaces `CLAUDE.md`'s per-suite commands with `uv run --python 3.13 python build/run_suites.py bayesian-workflow`, which runs the same suite command this plan uses. Its registry note for the suite lists what the tests cover. After both land, the note may add the all-clear and sampler-stat tests; nothing depends on it.
- **The G-A plan (backlog items G4 and X7 in the routing section).** G4(c) needs a tree-depth rule for tune-hyperparameters that a user can check: after this plan, that rule can point at `diagnostics.json → convergence.treedepth`. X7's fixture for `compare_experiments.py` is to be "written by diagnose_model.py", so write it after this plan lands: the JSON gains `checked`, `good_k` and `n_high`, and drops `n_marginal`.
- **The routing section (`4b683a4`).** This plan's completion ticks X1, X2 and F8 there, so that commit must be on `main` by then (Plan completion).

### Plan ID

`entry_check.py` printed "next free: 56" and "collisions: none" on 2026-10-18, with every branch, remote-tracking ref and worktree read. This file was written straight away to claim the id, since two plans took 54 the same day.

## File structure

| File | Responsibility | Tasks |
|---|---|---|
| `skills/bayesian-workflow/scripts/check_diagnostics.py` | The reader: ratings, next steps and the gated all-clear | 1, 3, 4 |
| `skills/bayesian-workflow/scripts/diagnose_model.py` | The writer: `diagnostics.json` and its overall verdict | 1, 2, 4 |
| `skills/bayesian-workflow/scripts/test_check_diagnostics.py` | Reader tests (stdlib and pytest) | 1, 3, 4 |
| `skills/bayesian-workflow/scripts/test_diagnose_model.py` | Writer tests, the shared-threshold pin and the writer-to-reader tests | 1, 2, 3, 4 |
| `skills/bayesian-workflow/references/reporting.md` | The MCSE row, the LOO next-step patterns and the Pareto-k line | 1, 4 |
| `skills/bayesian-workflow/references/diagnostics.md` | Tree depth on the `from_numpyro` path | 2 |
| `skills/bayesian-workflow/references/model-criticism.md` | The Pareto-k table and snippet | 4 |
| `skills/bayesian-workflow/README.md` | The two test files' coverage lines | 4 |
| `.sdd/56-diagnostics-harness-verdicts/` (ignored) | The acceptance fit script and its outputs | 5 |

---

### Task 1: Pre-flight, and the all-clear (X1)

**Files:**
- Modify: `skills/bayesian-workflow/scripts/check_diagnostics.py`, `skills/bayesian-workflow/scripts/diagnose_model.py`, `skills/bayesian-workflow/references/reporting.md`
- Test: `skills/bayesian-workflow/scripts/test_check_diagnostics.py`, `skills/bayesian-workflow/scripts/test_diagnose_model.py`

**Interfaces:**
- Consumes: nothing.
- Produces, in `check_diagnostics.py`: `REL_MCSE_OK = 0.05`; `REQUIRED_CHECKS`, a tuple of `(report section, label, passing ratings)`; `PSENSE_REMEDY`; `_rate_precision(prec: dict | None) -> dict`, which returns `{"rating": "excellent" | "poor", "max_rel_mcse": float, "max_rel_mcse_param": str}` or `{"rating": "not computed"}`; `report["precision"]`; `report["loo"]["error"]`; `_not_checked(report: dict) -> list[str]`; `_closing_steps(report: dict) -> list[str]`. New step prefixes: "Monte Carlo precision is short of the report's bar", "Monte Carlo precision was not checked", "Calibration was not checked", "LOO was not computed", "No specific next step applies", "Not checked:".
- Produces, in `diagnose_model.py`: `REL_MCSE_OK = 0.05`, and two overall issues: "Max relative MCSE … is above the 0.05 bar — run more draws before reporting" and "LOO not computed: <error>".
- Produces, in the tests: `_clean_diagnostics()`, `WELL_CALIBRATED`, `LOW_PSENSE`, `_steps`, `_one_step`, `_proceeds` (reader tests); `PASSING_PRECISION`, `_stub_checks` and `test_the_two_scripts_share_their_thresholds` (writer tests).

- [ ] **Step 1: Confirm the base.**

```bash
git diff --stat 668b8c3 -- skills/bayesian-workflow/
```

Expected: no output. If plan 53 landed first, the two scripts and `references/diagnostics.md` show its header and invocation lines. Read Couplings, then go on: the replace blocks still match.

- [ ] **Step 2: Record the baseline.**

```bash
uv run --directory skills/bayesian-workflow/scripts --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray python -m pytest -q
```

Expected: `129 passed, 3 skipped` at `668b8c3`, plus arviz's expected "invalid value encountered" warnings. Write down what it prints: every later count is a delta from it.

- [ ] **Step 3: Write the failing tests.**

Append to the end of `skills/bayesian-workflow/scripts/test_check_diagnostics.py`, after two blank lines:

````python
def _clean_diagnostics():
    """diagnose_model.py output in which every check ran and passed."""
    return {
        "convergence": {
            "all_ok": True,
            "method": "arviz_stats.diagnose",
            "rhat": {"ok": True, "max": None, "problematic_params": []},
            "ess_bulk": {"ok": True, "min": 1800, "problematic_params": []},
            "ess_tail": {"ok": True, "min": 1700, "problematic_params": []},
            "divergences": {"checked": True, "count": 0, "pct": 0.0, "ok": True},
            "treedepth": {"checked": True, "ok": True, "n_max": 0, "pct": 0.0},
            "bfmi": {"checked": True, "ok": True, "failed_chains": []},
        },
        "loo": {
            "computed": True,
            "elpd": -120.4,
            "se": 6.2,
            "p_loo": 3.1,
            "pareto_k": {"max": 0.31, "good_k": 0.7, "n_bad": 0, "n_high": 0, "n_nonfinite": 0, "ok": True},
        },
        "posterior_predictive": {"available": True},
        "precision": {
            "params": {"mu": {"rel_mcse": 0.021, "stable_digits": 1}},
            "max_rel_mcse": 0.021,
            "max_rel_mcse_param": "mu",
            "min_stable_digits": 1,
        },
    }


WELL_CALIBRATED = _calibration([], 0.0012)
LOW_PSENSE = {"prior": {"mu": 0.01}, "likelihood": {"mu": 0.02}}


def _steps(diagnostics, calibration=WELL_CALIBRATED, psense=LOW_PSENSE):
    return suggest_next_steps(
        check_diagnostics(diagnostics=diagnostics, calibration=calibration, psense=psense)
    )


def _one_step(steps, prefix):
    hits = [s for s in steps if s.startswith(prefix)]
    assert len(hits) == 1, steps
    return hits[0]


def _proceeds(steps):
    return any("proceed to interpretation" in s for s in steps)


def test_a_clean_report_gets_the_all_clear_alone():
    # The control: each test below changes one input from these.
    steps = _steps(_clean_diagnostics())
    assert len(steps) == 1 and _proceeds(steps), steps


def test_a_failing_mcse_gets_a_precision_step_not_the_all_clear():
    diag = _clean_diagnostics()
    diag["precision"].update(max_rel_mcse=0.058, max_rel_mcse_param="beta[1]")
    steps = _steps(diag)
    step = _one_step(steps, "Monte Carlo precision")
    assert "0.058 on beta[1]" in step and "0.05" in step
    assert not _proceeds(steps)


def test_an_mcse_at_the_bar_passes():
    diag = _clean_diagnostics()
    diag["precision"]["max_rel_mcse"] = 0.05
    assert _proceeds(_steps(diag))


@pytest.mark.parametrize(
    "precision",
    [None, {"params": {}, "max_rel_mcse": 0.0, "max_rel_mcse_param": None, "min_stable_digits": None}],
    ids=["no_block", "no_usable_param"],
)
def test_precision_that_never_ran_is_named_not_passed(precision):
    diag = _clean_diagnostics()
    if precision is None:
        del diag["precision"]
    else:
        diag["precision"] = precision
    steps = _steps(diag)
    assert "diagnose_model.py" in _one_step(steps, "Monte Carlo precision was not checked")
    assert not _proceeds(steps)


@pytest.mark.parametrize("loo", ["error", "no_section"])
def test_a_loo_that_never_ran_quotes_its_remedy(loo):
    diag = _clean_diagnostics()
    if loo == "error":
        diag["loo"] = {
            "computed": False,
            "error": "No log_likelihood group in the InferenceData. Rebuild it with "
            "az.from_numpyro(mcmc, log_likelihood=True, ...) and re-save the netCDF.",
        }
    else:
        del diag["loo"]
    steps = _steps(diag)
    assert "log_likelihood" in _one_step(steps, "LOO was not computed")
    assert not _proceeds(steps)


def test_without_calibration_there_is_no_all_clear():
    steps = _steps(_clean_diagnostics(), calibration=None)
    assert "--calibration" in _one_step(steps, "Calibration was not checked")
    assert not _proceeds(steps)


@pytest.mark.parametrize("psense", [None, {}], ids=["not_passed", "empty"])
def test_the_all_clear_names_prior_sensitivity_when_it_did_not_run(psense):
    steps = _steps(_clean_diagnostics(), psense=psense)
    assert _proceeds(steps)
    assert "prior sensitivity" in _one_step(steps, "Not checked:")


def test_a_rating_that_did_not_pass_blocks_the_all_clear_even_without_a_step():
    # A legacy calibration file that rates fair but names no finding adds no step.
    steps = _steps(_clean_diagnostics(), calibration=_legacy_calibration("", FAIR_OVER))
    assert "calibration (fair)" in _one_step(steps, "No specific next step applies")
    assert not _proceeds(steps)


def test_no_diagnostics_means_no_all_clear():
    steps = _steps(None)
    assert "convergence (not run)" in _one_step(steps, "No specific next step applies")
    assert not _proceeds(steps)
````

Replace in `skills/bayesian-workflow/scripts/test_diagnose_model.py`:

````python
import arviz as az
import numpy as np

from diagnose_model import _json_default, check_precision, generate_report
````

with:

````python
import arviz as az
import numpy as np

import check_diagnostics as cd
import diagnose_model
from diagnose_model import _json_default, check_precision, generate_report
````

Append to the end of `skills/bayesian-workflow/scripts/test_diagnose_model.py`, after two blank lines:

````python
PASSING_PRECISION = {
    "params": {"mu": {"rel_mcse": 0.02, "stable_digits": 1}},
    "max_rel_mcse": 0.02,
    "max_rel_mcse_param": "mu",
    "min_stable_digits": 1,
}


def _stub_checks(monkeypatch, **results):
    """Stub generate_report's four checks with passing results, overridden by ``results``."""
    passing = {
        "check_convergence": {"all_ok": True},
        "check_loo": {"computed": True, "pareto_k": {"ok": True}},
        "check_posterior_predictive": {"available": True},
        "check_precision": PASSING_PRECISION,
    }
    passing.update(results)
    for name, result in passing.items():
        monkeypatch.setattr(diagnose_model, name, lambda idata, result=result: result)


def test_report_overall_passes_when_every_check_passes(monkeypatch):
    # The control: each test below changes one check from these.
    _stub_checks(monkeypatch)
    overall = generate_report(None)["overall"]
    assert overall["ok"] and overall["recommendation"] == "Model is ready for interpretation."


def test_report_overall_flags_a_failing_mcse(monkeypatch):
    _stub_checks(monkeypatch, check_precision={**PASSING_PRECISION, "max_rel_mcse": 0.058})
    overall = generate_report(None)["overall"]
    assert not overall["ok"]
    assert any("0.058 on mu" in issue for issue in overall["issues"]), overall


def test_report_overall_flags_a_loo_that_never_ran(monkeypatch):
    error = "No log_likelihood group in the InferenceData. Rebuild it with az.from_numpyro(...)."
    _stub_checks(monkeypatch, check_loo={"computed": False, "error": error})
    overall = generate_report(None)["overall"]
    assert not overall["ok"]
    assert any(issue.startswith("LOO not computed") and error in issue for issue in overall["issues"]), overall


def test_the_two_scripts_share_their_thresholds():
    assert diagnose_model.REL_MCSE_OK == cd.REL_MCSE_OK
````

- [ ] **Step 4: Run them and see them fail.**

```bash
uv run --directory skills/bayesian-workflow/scripts --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray python -m pytest -q -rf
```

Expected: `13 failed`, and passed is the baseline +3. The three that pass are the two controls and `test_an_mcse_at_the_bar_passes`, a boundary pin that today's code already meets. The 13 `FAILED` lines, with their reasons:
- In `test_check_diagnostics.py`, ten tests fail on `_one_step`'s `assert len(hits) == 1`, and the printed steps list holds the all-clear (the bug): `test_a_failing_mcse_gets_a_precision_step_not_the_all_clear`, `test_precision_that_never_ran_is_named_not_passed[no_block]` and `[no_usable_param]`, `test_a_loo_that_never_ran_quotes_its_remedy[error]` and `[no_section]`, `test_without_calibration_there_is_no_all_clear`, `test_the_all_clear_names_prior_sensitivity_when_it_did_not_run[not_passed]` and `[empty]`, `test_a_rating_that_did_not_pass_blocks_the_all_clear_even_without_a_step`, `test_no_diagnostics_means_no_all_clear`. The `[empty]` case also shows the old "Consider running prior sensitivity" step.
- In `test_diagnose_model.py`: `test_report_overall_flags_a_failing_mcse` and `test_report_overall_flags_a_loo_that_never_ran` (`assert not overall["ok"]`: today's verdict is "Model is ready for interpretation."), and `test_the_two_scripts_share_their_thresholds` (`AttributeError: module 'diagnose_model' has no attribute 'REL_MCSE_OK'`).

- [ ] **Step 5: Implement the reader's half.** Make nine replacements in `skills/bayesian-workflow/scripts/check_diagnostics.py`.

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
PSENSE_OK = 0.05
PSENSE_FAIR = 0.10
````

with:

````python
PSENSE_OK = 0.05
PSENSE_FAIR = 0.10

# The report's own published bar for the largest relative MCSE (references/reporting.md,
# Sampling and Convergence), so unlike the levels above it is quoted in the next step.
# diagnose_model.py keeps a copy for its overall verdict; test_diagnose_model.py pins the two.
REL_MCSE_OK = 0.05

# The checks the all-clear requires: report section, label, and the ratings that pass.
REQUIRED_CHECKS = (
    ("convergence", "convergence", ("excellent", "good")),
    ("precision", "Monte Carlo precision", ("excellent",)),
    ("loo", "LOO", ("excellent",)),
    ("calibration", "calibration", ("excellent",)),
)
PSENSE_REMEDY = (
    "run psense_summary(idata) and pass it with --psense, before publication if any "
    "conclusion is policy-relevant"
)
````

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
    if max_prior_cjs <= PSENSE_OK:
        return "low sensitivity", flagged
    if max_prior_cjs <= PSENSE_FAIR:
        return "moderate sensitivity", flagged
    return "strong sensitivity", flagged
````

with:

````python
    if max_prior_cjs <= PSENSE_OK:
        return "low sensitivity", flagged
    if max_prior_cjs <= PSENSE_FAIR:
        return "moderate sensitivity", flagged
    return "strong sensitivity", flagged


def _rate_precision(prec: dict | None) -> dict:
    """Rate Monte Carlo precision against REL_MCSE_OK.

    "not computed" when diagnostics.json has no precision block, or one with no
    usable parameter: check_precision then reports max_rel_mcse 0.0, which
    would otherwise pass.
    """
    if not prec or not prec.get("params"):
        return {"rating": "not computed"}
    worst = float(prec.get("max_rel_mcse", 0.0))
    return {
        "rating": "excellent" if worst <= REL_MCSE_OK else "poor",
        "max_rel_mcse": worst,
        "max_rel_mcse_param": prec.get("max_rel_mcse_param"),
    }
````

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
    diagnostics : dict, optional
        Output of ``diagnose_model.generate_report()``. Provides
        ``convergence``, ``loo``, and ``posterior_predictive`` sub-reports.
    calibration : dict, optional
        Output of ``calibration_check.py``.
    psense : dict, optional
        Output of ``psense_summary(idata).to_dict()`` or equivalent.

    Returns
    -------
    dict
        Structured assessment with sections: ``convergence``, ``loo``,
        ``calibration``, ``psense``, plus ``summary`` (one-line per section).
    """
````

with:

````python
    diagnostics : dict, optional
        Output of ``diagnose_model.generate_report()``. Provides
        ``convergence``, ``loo``, ``posterior_predictive`` and ``precision``
        sub-reports.
    calibration : dict, optional
        Output of ``calibration_check.py``.
    psense : dict, optional
        Output of ``psense_summary(idata).to_dict()`` or equivalent.

    Returns
    -------
    dict
        Structured assessment with sections: ``convergence``, ``loo``,
        ``posterior_predictive``, ``precision``, ``calibration``, ``psense``,
        plus ``summary`` (one-line per section).
    """
````

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
            # carry the Pareto-k breakdown so suggest_next_steps can distinguish
            # finite k > 0.7 from non-finite (could-not-estimate) points.
            "pareto_k": loo_in.get("pareto_k", {}),
        }
        ppc = diagnostics.get("posterior_predictive", {})
        report["posterior_predictive"] = {
            "available": bool(ppc.get("available", False)),
        }
````

with:

````python
            # carry the Pareto-k breakdown so suggest_next_steps can distinguish
            # finite k > 0.7 from non-finite (could-not-estimate) points.
            "pareto_k": loo_in.get("pareto_k", {}),
            # diagnose_model.py's reason when LOO did not run; the next step quotes it
            "error": loo_in.get("error", ""),
        }
        ppc = diagnostics.get("posterior_predictive", {})
        report["posterior_predictive"] = {
            "available": bool(ppc.get("available", False)),
        }
        report["precision"] = _rate_precision(diagnostics.get("precision"))
````

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
    if "loo" in report:
        s["loo"] = f"LOO Pareto-k: {report['loo']['rating']}."
````

with:

````python
    if "precision" in report:
        r = report["precision"]
        if r["rating"] == "not computed":
            s["precision"] = "Monte Carlo precision: not computed."
        else:
            s["precision"] = (
                f"Monte Carlo precision: {r['rating']} (max relative MCSE "
                f"{r['max_rel_mcse']:.3f} on {r['max_rel_mcse_param']}; bar ≤ {REL_MCSE_OK})."
            )

    if "loo" in report:
        s["loo"] = f"LOO Pareto-k: {report['loo']['rating']}."
````

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
def suggest_next_steps(report: dict) -> list[str]:
    """Combine the interpreted report into an ordered, actionable list.
````

with:

````python
def _not_checked(report: dict) -> list[str]:
    """'check (how to run it)' for each optional check that did not run."""
    missing = []
    if report.get("psense", {}).get("rating", "not computed") == "not computed":
        missing.append(f"prior sensitivity ({PSENSE_REMEDY})")
    return missing


def _closing_steps(report: dict) -> list[str]:
    """The all-clear when every required check ran and passed; otherwise what blocks it.

    Reached only when no other step was added, so a required section that is
    missing, or that did not pass without adding a step of its own, still
    blocks the all-clear.
    """
    unresolved = [
        f"{label} ({report.get(key, {}).get('rating', 'not run')})"
        for key, label, passing in REQUIRED_CHECKS
        if report.get(key, {}).get("rating", "not run") not in passing
    ]
    if unresolved:
        return [
            "No specific next step applies, but not every required check ran and passed: "
            f"{', '.join(unresolved)}. Resolve these before interpreting the posterior."
        ]
    steps = [
        "All diagnostics are within acceptable bounds — proceed to "
        "interpretation. Translate posteriors into decision-relevant terms "
        "and document the model assumptions in the report."
    ]
    missing = _not_checked(report)
    if missing:
        steps.append(f"Not checked: {'; '.join(missing)}. Say so in the report.")
    return steps


def suggest_next_steps(report: dict) -> list[str]:
    """Combine the interpreted report into an ordered, actionable list.
````

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
    # ── Calibration ───────────────────────────────────────────────────
    steps.extend(_calibration_steps(report.get("calibration", {})))
````

with:

````python
    # ── Monte Carlo precision ─────────────────────────────────────────
    prec = report.get("precision", {})
    if prec.get("rating") == "poor":
        steps.append(
            f"Monte Carlo precision is short of the report's bar: max relative MCSE "
            f"{prec['max_rel_mcse']:.3f} on {prec['max_rel_mcse_param']}, above {REL_MCSE_OK} "
            "(references/reporting.md, Sampling and Convergence). Run more draws before "
            "reporting — halving the MCSE costs about four times the draws — and round each "
            "reported value to its stable_digits in diagnostics.json → precision."
        )
    elif prec.get("rating") == "not computed":
        steps.append(
            "Monte Carlo precision was not checked — diagnostics.json has no precision block "
            "with a usable parameter. Re-run diagnose_model.py, which writes it, before filling "
            "the report's MCSE row."
        )

    # ── Calibration ───────────────────────────────────────────────────
    if "calibration" not in report:
        steps.append(
            "Calibration was not checked — run calibration_check.py and pass its JSON with "
            "--calibration. Calibration is mandatory for every model "
            "(references/model-criticism.md), and the report's all-clear depends on it "
            "(references/reporting.md)."
        )
    steps.extend(_calibration_steps(report.get("calibration", {})))
````

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
            "consider a robust likelihood if they reflect a tail-heavy data process."
        )

    # ── PPC availability ──────────────────────────────────────────────
````

with:

````python
            "consider a robust likelihood if they reflect a tail-heavy data process."
        )
    elif loo_rating == "not computed" and "loo" in report:
        reason = loo.get("error") or (
            "diagnostics.json has no LOO result; re-run diagnose_model.py on an "
            "InferenceData with a log_likelihood group."
        )
        steps.append(f"LOO was not computed, so the Pareto-k check never ran — {reason}")

    # ── PPC availability ──────────────────────────────────────────────
````

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
    # ── Default if nothing is wrong ───────────────────────────────────
    if not steps:
        steps.append(
            "All diagnostics are within acceptable bounds — proceed to "
            "interpretation. Translate posteriors into decision-relevant terms "
            "and document the model assumptions in the report."
        )
        if report.get("psense", {}).get("rating") == "not computed":
            steps.append(
                "Consider running prior sensitivity (`psense_summary(idata)`) "
                "before publication, especially if any conclusions are policy-relevant."
            )

    return steps
````

with:

````python
    # ── Closing: the all-clear only when every required check ran and passed ──
    if not steps:
        steps.extend(_closing_steps(report))

    return steps
````

- [ ] **Step 6: Implement the writer's half.** Make two replacements in `skills/bayesian-workflow/scripts/diagnose_model.py`.

Replace in `skills/bayesian-workflow/scripts/diagnose_model.py`:

````python
    HAS_DIAGNOSE = hasattr(azs, "diagnose")
except ImportError:
    HAS_DIAGNOSE = False
````

with:

````python
    HAS_DIAGNOSE = hasattr(azs, "diagnose")
except ImportError:
    HAS_DIAGNOSE = False

# The report's bar for the largest relative MCSE (references/reporting.md, Sampling and
# Convergence). check_diagnostics.py keeps a copy; test_diagnose_model.py pins the two.
REL_MCSE_OK = 0.05
````

Replace in `skills/bayesian-workflow/scripts/diagnose_model.py`:

````python
    issues = []
    if not report["convergence"]["all_ok"]:
        issues.append("Convergence issues detected — results may be unreliable")
````

with:

````python
    issues = []
    if not report["convergence"]["all_ok"]:
        issues.append("Convergence issues detected — results may be unreliable")
    prec = report["precision"]
    if prec["params"] and prec["max_rel_mcse"] > REL_MCSE_OK:
        issues.append(
            f"Max relative MCSE {prec['max_rel_mcse']:.3f} on {prec['max_rel_mcse_param']} "
            f"is above the {REL_MCSE_OK} bar — run more draws before reporting"
        )
    if not report["loo"].get("computed"):
        issues.append(f"LOO not computed: {report['loo'].get('error', 'no LOO result')}")
````

- [ ] **Step 7: Run the suite: green.** Same command as Step 4. Expected: no failures; passed is the baseline +16; skipped is unchanged.

- [ ] **Step 8: Fix the MCSE row in the report template.** Its parenthetical "≥ 1 stable digit" reads as if it were the bar, but a relative MCSE of 0.058 also has one stable digit and fails the bar.

Replace in `skills/bayesian-workflow/references/reporting.md`:

````markdown
| Max relative MCSE | <e.g., 0.02 (β₁)> | ≤ 0.05 (≥ 1 stable digit; from `diagnostics.json → precision`) | <✓ / ✗> |
````

with:

````markdown
| Max relative MCSE | <e.g., 0.02 (β₁)> | ≤ 0.05 (from `diagnostics.json → precision`; `check_diagnostics.py` flags a higher value) | <✓ / ✗> |
````

- [ ] **Step 9: Commit.**

```bash
git add skills/bayesian-workflow/scripts/check_diagnostics.py skills/bayesian-workflow/scripts/diagnose_model.py skills/bayesian-workflow/scripts/test_check_diagnostics.py skills/bayesian-workflow/scripts/test_diagnose_model.py skills/bayesian-workflow/references/reporting.md
```

```bash
git commit -m "fix(bayesian-workflow): no all-clear when MCSE fails or LOO, precision or calibration never ran (audit X1)" -m "check_diagnostics.py now reads the precision block and LOO's error, gives each failed or missing check a next step, and prints the all-clear only when every required check ran and passed, naming prior sensitivity when it did not run. diagnose_model.py's verdict lists a failing MCSE and an uncomputed LOO."
```

### Task 2: The writer's sampler-stat blocks (X2, D2)

**Files:**
- Modify: `skills/bayesian-workflow/scripts/diagnose_model.py`, `skills/bayesian-workflow/references/diagnostics.md`
- Test: `skills/bayesian-workflow/scripts/test_diagnose_model.py`

**Interfaces:**
- Consumes: Task 1's import of `diagnose_model` in the writer tests.
- Produces, in `diagnose_model.py`: `TREEDEPTH_FLAGS = ("reached_max_tree_depth", "reached_max_treedepth")`; `_sample_stats(idata)`; `_divergence_block(stats)`, `_treedepth_block(stats)` and `_bfmi_block(diagnosed)`. The three blocks in `check_convergence`'s result, on both paths: `divergences` is `{"checked": True, "count": int, "pct": float, "ok": bool}`, `treedepth` is `{"checked": True, "ok": bool, "n_max": int, "pct": float}` and `bfmi` is `{"checked": True, "ok": bool, "failed_chains": list[int]}`, or `{"checked": False}` when the sample stat is missing. `all_ok` includes tree depth on both paths.
- Produces, in the tests: `_idata(..., stats=None)`, `CALM`, `SATURATED` and the fixture `both_paths`.

- [ ] **Step 1: Write the failing tests.**

Replace in `skills/bayesian-workflow/scripts/test_diagnose_model.py`:

````python
import arviz as az
import numpy as np

import check_diagnostics as cd
````

with:

````python
import arviz as az
import numpy as np
import pytest

import check_diagnostics as cd
````

Replace in `skills/bayesian-workflow/scripts/test_diagnose_model.py`:

````python
def _idata(n_chains=4, n_draws=500, seed=0, extra=None):
    """Synthetic InferenceData with i.i.d. unit-normal draws (ESS ~ n_chains * n_draws)."""
    rng = np.random.default_rng(seed)
    post = {
        "mu": rng.normal(size=(n_chains, n_draws)),
        "beta": rng.normal(size=(n_chains, n_draws, 2)),
    }
    if extra:
        post.update(extra)
    stats = {"diverging": np.zeros((n_chains, n_draws), dtype=bool)}
````

with:

````python
def _idata(n_chains=4, n_draws=500, seed=0, extra=None, stats=None):
    """Synthetic InferenceData with i.i.d. unit-normal draws (ESS ~ n_chains * n_draws).

    ``stats`` replaces the default sample_stats, which hold only ``diverging``.
    """
    rng = np.random.default_rng(seed)
    post = {
        "mu": rng.normal(size=(n_chains, n_draws)),
        "beta": rng.normal(size=(n_chains, n_draws, 2)),
    }
    if extra:
        post.update(extra)
    if stats is None:
        stats = {"diverging": np.zeros((n_chains, n_draws), dtype=bool)}
````

Append to the end of `skills/bayesian-workflow/scripts/test_diagnose_model.py`, after two blank lines:

````python
CALM = np.zeros((4, 500), dtype=bool)
SATURATED = np.ones((4, 500), dtype=bool)


@pytest.fixture(params=[True, False], ids=["diagnose", "fallback"])
def both_paths(request, monkeypatch):
    """Run check_convergence on the arviz_stats.diagnose path, then on the manual fallback."""
    monkeypatch.setattr(diagnose_model, "HAS_DIAGNOSE", request.param)
    return request.param


@pytest.mark.parametrize("flag", ["reached_max_tree_depth", "reached_max_treedepth"], ids=["numpyro", "cmdstan"])
def test_a_saturated_run_fails_tree_depth_on_both_paths(both_paths, flag):
    conv = diagnose_model.check_convergence(_idata(stats={"diverging": CALM, flag: SATURATED}))
    assert conv["treedepth"] == {"checked": True, "ok": False, "n_max": 2000, "pct": 100.0}
    assert conv["all_ok"] is False


def test_a_calm_numpyro_run_passes_tree_depth(both_paths):
    conv = diagnose_model.check_convergence(_idata(stats={"diverging": CALM, "reached_max_tree_depth": CALM}))
    assert conv["treedepth"] == {"checked": True, "ok": True, "n_max": 0, "pct": 0.0}
    assert conv["all_ok"] is True


def test_no_tree_depth_flag_is_marked_not_checked(both_paths):
    conv = diagnose_model.check_convergence(_idata())
    assert conv["treedepth"] == {"checked": False}
    assert conv["all_ok"] is True


def test_no_energy_stat_marks_e_bfmi_not_checked(both_paths):
    assert diagnose_model.check_convergence(_idata())["bfmi"] == {"checked": False}


def test_an_energy_stat_gives_a_checked_e_bfmi_block():
    # Only the arviz_stats.diagnose path computes E-BFMI; i.i.d. energy is far above 0.3.
    energy = np.random.default_rng(1).normal(size=(4, 500))
    conv = diagnose_model.check_convergence(_idata(stats={"diverging": CALM, "energy": energy}))
    assert conv["bfmi"] == {"checked": True, "ok": True, "failed_chains": []}


def test_a_diverging_stat_gives_a_checked_divergence_block(both_paths):
    assert diagnose_model.check_convergence(_idata())["divergences"] == {
        "checked": True, "count": 0, "pct": 0.0, "ok": True,
    }


def test_no_diverging_stat_marks_divergences_not_checked(both_paths):
    conv = diagnose_model.check_convergence(_idata(stats={"lp": np.zeros((4, 500))}))
    assert conv["divergences"] == {"checked": False}
    assert conv["all_ok"] is True
````

- [ ] **Step 2: Run them and see them fail.**

```bash
uv run --directory skills/bayesian-workflow/scripts --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray python -m pytest -q -rf
```

Expected: `15 failed`, and passed is unchanged from Task 1's green run. All 15 new tests fail:
- On the fallback path (`[fallback]`): `KeyError: 'treedepth'` in the four tree-depth cases and `KeyError: 'bfmi'` in the E-BFMI case, because that path writes neither block. The two divergence cases fail on a block with no `checked` key.
- On the diagnose path (`[diagnose]`, and `test_an_energy_stat_gives_a_checked_e_bfmi_block`): each block lacks `checked`. The `[diagnose-numpyro]` saturation case shows X2 itself: `{'ok': True, 'n_max': 0, 'pct': 0.0}` for 2,000 saturated draws.

- [ ] **Step 3: Implement.** Make five replacements in `skills/bayesian-workflow/scripts/diagnose_model.py`.

Replace in `skills/bayesian-workflow/scripts/diagnose_model.py`:

````python
REL_MCSE_OK = 0.05
````

with:

````python
REL_MCSE_OK = 0.05

# The tree-depth saturation flags, NumPyro's first: az.from_numpyro writes
# reached_max_tree_depth (when num_steps is collected), while arviz_stats.diagnose
# reads only the CmdStan-style reached_max_treedepth.
TREEDEPTH_FLAGS = ("reached_max_tree_depth", "reached_max_treedepth")
````

Replace in `skills/bayesian-workflow/scripts/diagnose_model.py`:

````python
def check_convergence(idata):
    """Run all convergence diagnostics. Returns structured results.

    Both code paths emit the SAME serializable schema so ``check_diagnostics.py``
    has a single contract to consume: ``rhat`` / ``ess_bulk`` / ``ess_tail`` /
    ``divergences`` each carry ``ok`` and ``problematic_params``; the
    ``arviz_stats.diagnose`` path additionally reports ``bfmi`` and ``treedepth``
    (the ``treedepth`` block is populated only when ``sample_stats`` carries
    ``reached_max_treedepth``; NumPyro idata uses ``tree_depth`` instead, so on
    that path treedepth stays ``ok``/0).
    No numpy scalars, numpy arrays, or xarray objects leak into the dict — those
    are not JSON-serializable and would crash the report writer.
    """
    # Use arviz_stats.diagnose() if available — it covers R-hat, ESS,
    # divergences, and E-BFMI in one call. (It only reports tree-depth
    # saturation when sample_stats carries CmdStan-style
    # "reached_max_treedepth"; NumPyro idata uses "tree_depth", so the
    # treedepth block stays ok/0 on that path.)
    if HAS_DIAGNOSE:
````

with:

````python
def _sample_stats(idata):
    """The sample_stats group, or None when the InferenceData has none."""
    return idata.sample_stats if "sample_stats" in _group_names(idata) else None


def _divergence_block(stats):
    """Divergences from sample_stats; {"checked": False} without a diverging stat."""
    if stats is None or "diverging" not in stats:
        return {"checked": False}
    flags = stats["diverging"]
    n_div = int(flags.sum())
    return {"checked": True, "count": n_div, "pct": round(100 * n_div / int(flags.size), 2), "ok": n_div == 0}


def _treedepth_block(stats):
    """Tree-depth saturation from either TREEDEPTH_FLAGS stat; {"checked": False} without one.

    An unchecked block carries no ok key, so check_diagnostics can tell it from
    a pass, and from ok: None, which it reads as saturation.
    """
    flag = next((f for f in TREEDEPTH_FLAGS if stats is not None and f in stats), None)
    if flag is None:
        return {"checked": False}
    hits = stats[flag]
    n_max = int(hits.sum())
    return {"checked": True, "ok": n_max == 0, "n_max": n_max, "pct": round(100 * n_max / int(hits.size), 2)}


def _bfmi_block(diagnosed):
    """E-BFMI from arviz_stats.diagnose's results; {"checked": False} when it had no energy stat."""
    if "bfmi" not in diagnosed:
        return {"checked": False}
    failed = [int(c) for c in diagnosed["bfmi"].get("failed_chains", [])]
    return {"checked": True, "ok": not failed, "failed_chains": failed}


def check_convergence(idata):
    """Run all convergence diagnostics. Returns structured results.

    Both code paths emit the SAME serializable schema so ``check_diagnostics.py``
    has a single contract to consume: ``rhat`` / ``ess_bulk`` / ``ess_tail`` each
    carry ``ok`` and ``problematic_params``. ``divergences``, ``treedepth`` and
    ``bfmi`` carry ``checked``: a block whose sample stat is missing (``diverging``;
    either of ``TREEDEPTH_FLAGS``; ``energy``) is just ``{"checked": False}``, so
    an unchecked block never reads as passed. Only the ``arviz_stats.diagnose``
    path computes E-BFMI; the fallback always marks it unchecked.
    No numpy scalars, numpy arrays, or xarray objects leak into the dict — those
    are not JSON-serializable and would crash the report writer.
    """
    # Use arviz_stats.diagnose() if available — it covers R-hat, ESS,
    # divergences, and E-BFMI in one call. It reads tree depth only from the
    # CmdStan-style "reached_max_treedepth", while az.from_numpyro writes
    # "reached_max_tree_depth", so both paths take the treedepth block from
    # sample_stats themselves.
    if HAS_DIAGNOSE:
````

Replace in `skills/bayesian-workflow/scripts/diagnose_model.py`:

````python
        min_tail = int(min(float(ess_tail_vals[v].min()) for v in ess_tail_vals.data_vars))
        div = d.get("divergent", {})
        n_div = int(div.get("n_divergent", 0))
        td = d.get("treedepth", {})
        n_td = int(td.get("n_max", 0))
        failed_chains = [int(c) for c in d.get("bfmi", {}).get("failed_chains", [])]
        return {
            "all_ok": not has_errors,
            "method": "arviz_stats.diagnose",
````

with:

````python
        min_tail = int(min(float(ess_tail_vals[v].min()) for v in ess_tail_vals.data_vars))
        stats = _sample_stats(idata)
        treedepth = _treedepth_block(stats)
        return {
            # has_errors misses NumPyro's tree-depth flag, so fold the block in here:
            # check_diagnostics rates "excellent" on all_ok before it reads any block.
            "all_ok": not has_errors and treedepth.get("ok", True),
            "method": "arviz_stats.diagnose",
````

Replace in `skills/bayesian-workflow/scripts/diagnose_model.py`:

````python
            "ess_tail": {"ok": len(bad_tail) == 0, "problematic_params": bad_tail, "min": min_tail},
            "divergences": {
                "count": n_div,
                "pct": round(float(div.get("pct", 0.0)), 2),
                "ok": n_div == 0,
            },
            "treedepth": {
                "ok": n_td == 0,
                "n_max": n_td,
                "pct": round(float(td.get("pct", 0.0)), 2),
            },
            "bfmi": {"ok": len(failed_chains) == 0, "failed_chains": failed_chains},
        }
````

with:

````python
            "ess_tail": {"ok": len(bad_tail) == 0, "problematic_params": bad_tail, "min": min_tail},
            "divergences": _divergence_block(stats),
            "treedepth": treedepth,
            "bfmi": _bfmi_block(d),
        }
````

Replace in `skills/bayesian-workflow/scripts/diagnose_model.py`:

````python
    # Divergences
    if "diverging" in idata.sample_stats:
        n_div = int(idata.sample_stats["diverging"].sum())
        total_samples = int(idata.sample_stats["diverging"].size)
        results["divergences"] = {
            "count": n_div,
            "pct": round(100 * n_div / total_samples, 2),
            "ok": n_div == 0,
        }
    else:
        results["divergences"] = {"count": 0, "pct": 0.0, "ok": True}

    results["all_ok"] = all(
        results[k]["ok"] for k in ["rhat", "ess_bulk", "ess_tail", "divergences"]
    )
    results["method"] = "manual"
````

with:

````python
    stats = _sample_stats(idata)
    results["divergences"] = _divergence_block(stats)
    results["treedepth"] = _treedepth_block(stats)
    results["bfmi"] = {"checked": False}  # E-BFMI needs arviz_stats.diagnose

    results["all_ok"] = all(
        results[k].get("ok", True)
        for k in ["rhat", "ess_bulk", "ess_tail", "divergences", "treedepth"]
    )
    results["method"] = "manual"
````

- [ ] **Step 4: Run the suite: green.** Same command as Step 2. Expected: no failures; passed is +15 over Task 1's green run.

- [ ] **Step 5: Correct the tree-depth notes in the diagnostics reference.** They tell the reader to inspect tree depth by hand because nothing reports it.

Replace in `skills/bayesian-workflow/references/diagnostics.md`:

````markdown
`az.from_numpyro` emits `reached_max_tree_depth` instead, so the tree-depth branch never fires.
Inspect tree-depth separately via `idata.sample_stats["tree_depth"]` — see Energy diagnostics
below.) If `azs.diagnose` is not available (arviz-stats < 1.0.0), fall back to the manual checks
below.
````

with:

````markdown
`az.from_numpyro` emits `reached_max_tree_depth` instead, so the tree-depth branch never fires.
`scripts/diagnose_model.py` reads either flag itself and reports saturation in its `treedepth`
block. `az.from_numpyro` writes the flag only when `num_steps` is in `extra_fields`, as in our
sampling flow; without it the block reads `checked: false`.) If `azs.diagnose` is not available
(arviz-stats < 1.0.0), fall back to the manual checks below.
````

Replace in `skills/bayesian-workflow/references/diagnostics.md`:

````markdown
| Chains drift to ±1e20, R-hat ≈ 3, most transitions hit max tree depth (read that one yourself from `idata.sample_stats["tree_depth"]` — it is the check `azs.diagnose` skips on the `from_numpyro` path, above) | **Improper or near-improper posterior** — a site under `dist.ImproperUniform`, or a `Normal(0, 100)`-class prior on a logistic coefficient whose classes are separated | Give every site a proper prior on the scale the parameter actually lives on (`Normal(0, 2.5)` for a standardized logistic coefficient). Raising `max_tree_depth` never helps here |
````

with:

````markdown
| Chains drift to ±1e20, R-hat ≈ 3, most transitions hit max tree depth (`diagnose_model.py`'s `treedepth` block; `azs.diagnose` alone skips it on the `from_numpyro` path, above) | **Improper or near-improper posterior** — a site under `dist.ImproperUniform`, or a `Normal(0, 100)`-class prior on a logistic coefficient whose classes are separated | Give every site a proper prior on the scale the parameter actually lives on (`Normal(0, 2.5)` for a standardized logistic coefficient). Raising `max_tree_depth` never helps here |
````

- [ ] **Step 6: Commit.**

```bash
git add skills/bayesian-workflow/scripts/diagnose_model.py skills/bayesian-workflow/scripts/test_diagnose_model.py skills/bayesian-workflow/references/diagnostics.md
```

```bash
git commit -m "fix(bayesian-workflow): read NumPyro's tree-depth flag and mark sampler checks that never ran (audit X2)" -m "diagnose_model.py reads reached_max_tree_depth or reached_max_treedepth from sample_stats on both paths and folds tree depth into all_ok. The divergences, treedepth and bfmi blocks carry checked, and a block whose stat is missing is {\"checked\": false}, so it can no longer read as passed (owner decision D2)."
```

### Task 3: The reader's convergence flags (X2, D2, the E-BFMI finding)

**Files:**
- Modify: `skills/bayesian-workflow/scripts/check_diagnostics.py`
- Test: `skills/bayesian-workflow/scripts/test_check_diagnostics.py`, `skills/bayesian-workflow/scripts/test_diagnose_model.py`

**Interfaces:**
- Consumes: Task 2's block shapes; Task 1's `_clean_diagnostics`, `WELL_CALIBRATED`, `LOW_PSENSE`, `_steps`, `_one_step`, `_proceeds` and `_not_checked`; Task 2's `CALM` and `SATURATED`.
- Produces, in `check_diagnostics.py`: `NON_PARAM_TOKENS`; `SAMPLER_CHECKS`, a tuple of `(block key, label, how to get the stat)`; `_split_flags(problematic: list) -> tuple[list[str], list[str]]`; `_flag_phrase(named: list[str], flags: list[str]) -> str`; `_unchecked_sampler_checks(conv: dict) -> list[str]`; `report["convergence"]["treedepth"]`, `["bfmi"]` and `["unchecked"]`. New step prefixes: "Tree depth hit max_tree_depth" and "E-BFMI is low".
- Produces, in the tests: `_report_and_steps` (reader tests); `_complete_idata(**stats)` and `_read_back` (writer tests).

- [ ] **Step 1: Write the failing tests.**

Append to the end of `skills/bayesian-workflow/scripts/test_check_diagnostics.py`, after two blank lines:

````python
def _report_and_steps(diag):
    report = check_diagnostics(diagnostics=diag, calibration=WELL_CALIBRATED, psense=LOW_PSENSE)
    return report, suggest_next_steps(report)


def test_tree_depth_saturation_gets_a_step_not_the_all_clear():
    diag = _clean_diagnostics()
    diag["convergence"].update(all_ok=False, treedepth={"checked": True, "ok": False, "n_max": 8000, "pct": 100.0})
    report, steps = _report_and_steps(diag)
    step = _one_step(steps, "Tree depth hit max_tree_depth")
    assert "100.0%" in step and "8000" in step
    assert "treedepth saturation" in report["summary"]["convergence"]
    assert "some parameters" not in report["summary"]["convergence"]
    assert not _proceeds(steps)


def test_low_e_bfmi_gets_a_step_not_the_all_clear():
    diag = _clean_diagnostics()
    diag["convergence"].update(all_ok=False, bfmi={"checked": True, "ok": False, "failed_chains": [0, 2]})
    report, steps = _report_and_steps(diag)
    step = _one_step(steps, "E-BFMI is low")
    assert "chain(s) 0, 2" in step and "plot_energy" in step
    assert "low E-BFMI" in report["summary"]["convergence"]
    assert not _proceeds(steps)


@pytest.mark.parametrize(
    "block, label",
    [("treedepth", "tree depth"), ("bfmi", "E-BFMI"), ("divergences", "divergences")],
)
def test_a_sampler_check_that_never_ran_is_named_not_passed(block, label):
    diag = _clean_diagnostics()
    diag["convergence"][block] = {"checked": False}
    report, steps = _report_and_steps(diag)
    assert _proceeds(steps)
    assert label in _one_step(steps, "Not checked:")
    assert f"not checked: {label}" in report["summary"]["convergence"]


def test_a_missing_sampler_block_counts_as_not_checked():
    diag = _clean_diagnostics()
    del diag["convergence"]["treedepth"]
    assert "tree depth" in _one_step(_steps(diag), "Not checked:")


def test_a_sampler_block_without_a_checked_key_counts_as_checked():
    # A diagnostics.json written before checked existed.
    diag = _clean_diagnostics()
    diag["convergence"]["treedepth"] = {"ok": True, "n_max": 0, "pct": 0.0}
    steps = _steps(diag)
    assert len(steps) == 1 and _proceeds(steps), steps


def test_an_unchecked_divergence_count_is_not_reported_as_zero():
    diag = _clean_diagnostics()
    diag["convergence"]["divergences"] = {"checked": False}
    assert "no divergences" not in check_diagnostics(diagnostics=diag)["summary"]["convergence"]


def test_the_convergence_summary_names_parameters_and_sampler_flags():
    diag = _clean_diagnostics()
    diag["convergence"].update(
        all_ok=False,
        rhat={"ok": False, "max": 1.02, "problematic_params": ["a"]},
        treedepth={"checked": True, "ok": False, "n_max": 4000, "pct": 100.0},
    )
    report, _ = _report_and_steps(diag)
    assert "flags on a; max treedepth saturation" in report["summary"]["convergence"]
````

Append to the end of `skills/bayesian-workflow/scripts/test_diagnose_model.py`, after two blank lines:

````python
WELL_CALIBRATED = {
    "assessment": {
        "findings": [],
        "well_calibrated": True,
        "mean_coverage_deviation": 0.0012,
        "calibration_diagnosis": "well-calibrated",
    },
}
LOW_PSENSE = {"prior": {"mu": 0.01}, "likelihood": {"mu": 0.02}}


def _complete_idata(**stats):
    """An InferenceData on which every check runs and passes: LOO, PPC and all three
    sampler checks. A keyword replaces one sample stat; None drops it."""
    rng = np.random.default_rng(3)
    y = rng.normal(size=20)
    mu = rng.normal(size=(4, 500))
    sample_stats = {"diverging": CALM, "reached_max_tree_depth": CALM, "energy": rng.normal(size=(4, 500))}
    sample_stats.update(stats)
    return az.from_dict({
        "posterior": {"mu": mu},
        "sample_stats": {k: v for k, v in sample_stats.items() if v is not None},
        # a narrow log-likelihood keeps every Pareto k small
        "log_likelihood": {"y": -0.5 * (y - 0.1 * mu[..., None]) ** 2 - 0.5 * np.log(2 * np.pi)},
        "posterior_predictive": {"y": rng.normal(size=(4, 500, 20))},
        "observed_data": {"y": y},
    })


def _read_back(idata):
    """diagnose_model's report read by check_diagnostics, as step 3 of SKILL.md's pipeline does."""
    report = cd.check_diagnostics(diagnostics=generate_report(idata), calibration=WELL_CALIBRATED, psense=LOW_PSENSE)
    return report, cd.suggest_next_steps(report)


def test_a_complete_clean_run_reads_back_as_the_all_clear():
    # The control for the two tests below.
    _, steps = _read_back(_complete_idata())
    assert len(steps) == 1 and "proceed to interpretation" in steps[0], steps


def test_a_saturated_numpyro_run_reads_back_as_saturation():
    report, steps = _read_back(_complete_idata(reached_max_tree_depth=SATURATED))
    assert any(s.startswith("Tree depth hit max_tree_depth on 100.0%") for s in steps), steps
    assert not any("proceed to interpretation" in s for s in steps)
    assert "treedepth saturation" in report["summary"]["convergence"]


def test_a_run_without_the_tree_depth_flag_reads_back_as_not_checked():
    report, steps = _read_back(_complete_idata(reached_max_tree_depth=None))
    assert "proceed to interpretation" in steps[0]
    assert any(s.startswith("Not checked: tree depth") for s in steps), steps
    assert "not checked: tree depth" in report["summary"]["convergence"]
````

- [ ] **Step 2: Run them and see them fail.**

```bash
uv run --directory skills/bayesian-workflow/scripts --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray python -m pytest -q -rf
```

Expected: `10 failed`, and passed is +2 over Task 2's green run. The two that pass from the start: `test_a_sampler_block_without_a_checked_key_counts_as_checked`, which pins DF5's rule for old files, already met today; and `test_a_complete_clean_run_reads_back_as_the_all_clear`, the control. The 10 `FAILED` lines, with their reasons:
- `test_tree_depth_saturation_gets_a_step_not_the_all_clear`, `test_low_e_bfmi_gets_a_step_not_the_all_clear` and, in `test_diagnose_model.py`, `test_a_saturated_numpyro_run_reads_back_as_saturation`: no tree-depth or E-BFMI step. Task 1's gate already blocks the all-clear, so the only step reads "No specific next step applies, but not every required check ran and passed: convergence (fair)."
- `test_a_sampler_check_that_never_ran_is_named_not_passed[treedepth-tree depth]`, `[bfmi-E-BFMI]` and `[divergences-divergences]`, `test_a_missing_sampler_block_counts_as_not_checked`, and, in `test_diagnose_model.py`, `test_a_run_without_the_tree_depth_flag_reads_back_as_not_checked`: no "Not checked:" step names the check.
- `test_an_unchecked_divergence_count_is_not_reported_as_zero`: the summary still says "no divergences".
- `test_the_convergence_summary_names_parameters_and_sampler_flags`: the summary reads "Convergence is fair — flags on a." and drops the saturation.

- [ ] **Step 3: Implement.** Make seven replacements in `skills/bayesian-workflow/scripts/check_diagnostics.py`.

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
PSENSE_REMEDY = (
    "run psense_summary(idata) and pass it with --psense, before publication if any "
    "conclusion is policy-relevant"
)
````

with:

````python
PSENSE_REMEDY = (
    "run psense_summary(idata) and pass it with --psense, before publication if any "
    "conclusion is policy-relevant"
)

# problematic_params entries that are sampler flags, not parameter names.
NON_PARAM_TOKENS = ("divergence", "e-bfmi", "treedepth", "=")

# The sampler-stat blocks diagnose_model.py marks {"checked": False} when their stat is
# missing: block key, the label the report uses, and how to get the stat.
SAMPLER_CHECKS = (
    ("treedepth", "tree depth",
     "collect num_steps in extra_fields so az.from_numpyro writes reached_max_tree_depth"),
    ("bfmi", "E-BFMI", "collect energy in extra_fields; the check needs arviz-stats >= 1.0"),
    ("divergences", "divergences", "the InferenceData has no diverging sample stat"),
)
````

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
def _rate_convergence(conv: dict) -> tuple[str, list[str]]:
````

with:

````python
def _split_flags(problematic: list) -> tuple[list[str], list[str]]:
    """Split problematic_params into (parameter names, sampler flags)."""
    named, flags = [], []
    for p in problematic:
        (flags if any(tok in str(p).lower() for tok in NON_PARAM_TOKENS) else named).append(str(p))
    return named, flags


def _flag_phrase(named: list[str], flags: list[str]) -> str:
    """'flags on a, b; max treedepth saturation': parameter names first, then sampler flags."""
    return "; ".join(([f"flags on {', '.join(named[:3])}"] if named else []) + flags)


def _unchecked_sampler_checks(conv: dict) -> list[str]:
    """Labels of the sampler checks that never ran.

    A block marked checked: false, or no block at all, never ran. A block with
    no checked key comes from a diagnostics.json written before the key existed,
    and counts as checked.
    """
    return [
        label for key, label, _ in SAMPLER_CHECKS
        if not conv.get(key, {}).get("checked", key in conv)
    ]


def _rate_convergence(conv: dict) -> tuple[str, list[str]]:
````

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
            "divergence_pct": float((conv_in.get("divergences") or {}).get("pct", 0.0) or 0.0),
        }
````

with:

````python
            "divergence_pct": float((conv_in.get("divergences") or {}).get("pct", 0.0) or 0.0),
            # the blocks the tree-depth and E-BFMI steps quote
            "treedepth": conv_in.get("treedepth", {}),
            "bfmi": conv_in.get("bfmi", {}),
            "unchecked": _unchecked_sampler_checks(conv_in),
        }
````

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
    if "convergence" in report:
        r = report["convergence"]
        if r["rating"] == "excellent":
            s["convergence"] = "All convergence diagnostics passed (R-hat ≤ 1.01, ESS adequate, no divergences)."
        elif r["rating"] == "good":
            s["convergence"] = "Convergence diagnostics broadly pass; minor flags worth noting."
        elif r["rating"] == "fair":
            _np = ("divergence", "e-bfmi", "treedepth", "=")
            named = [p for p in r["problematic_params"] if not any(tok in str(p).lower() for tok in _np)]
            params = ", ".join(named[:3]) or "some parameters"
            s["convergence"] = f"Convergence is fair — flags on {params}. Inspect before trusting the posterior."
        else:
            _np = ("divergence", "e-bfmi", "treedepth", "=")
            named = [p for p in r["problematic_params"] if not any(tok in str(p).lower() for tok in _np)]
            params = ", ".join(named[:3]) or "multiple parameters"
            s["convergence"] = f"Poor convergence on {params}. Posterior should not be interpreted until resolved."
````

with:

````python
    if "convergence" in report:
        r = report["convergence"]
        named, flags = _split_flags(r["problematic_params"])
        unchecked = r.get("unchecked", [])
        if r["rating"] == "excellent":
            passed = "R-hat ≤ 1.01, ESS adequate" + ("" if "divergences" in unchecked else ", no divergences")
            if unchecked:
                s["convergence"] = (
                    f"Convergence diagnostics that ran passed ({passed}); "
                    f"not checked: {', '.join(unchecked)}."
                )
            else:
                s["convergence"] = f"All convergence diagnostics passed ({passed})."
        elif r["rating"] == "good":
            s["convergence"] = "Convergence diagnostics broadly pass; minor flags worth noting."
        elif r["rating"] == "fair":
            flagged = _flag_phrase(named, flags) or "flags on some parameters"
            s["convergence"] = f"Convergence is fair — {flagged}. Inspect before trusting the posterior."
        else:
            flagged = _flag_phrase(named, flags) or "flags on multiple parameters"
            s["convergence"] = f"Poor convergence — {flagged}. Posterior should not be interpreted until resolved."
````

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
    """'check (how to run it)' for each optional check that did not run."""
    missing = []
````

with:

````python
    """'check (how to run it)' for each optional check that did not run."""
    unchecked = report.get("convergence", {}).get("unchecked", [])
    missing = [f"{label} ({remedy})" for _, label, remedy in SAMPLER_CHECKS if label in unchecked]
````

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
        _non_param = ("divergence", "e-bfmi", "treedepth", "=")
        named_params = [
            p for p in params if not any(tok in str(p).lower() for tok in _non_param)
        ]
````

with:

````python
        named_params, _ = _split_flags(params)
````

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
                "Check for multimodality with az.plot_rank(idata) (runs on both ArviZ stacks)."
            )

    # ── Monte Carlo precision ─────────────────────────────────────────
````

with:

````python
                "Check for multimodality with az.plot_rank(idata) (runs on both ArviZ stacks)."
            )
        td = conv.get("treedepth", {})
        if not td.get("ok", True):
            steps.append(
                f"Tree depth hit max_tree_depth on {td.get('pct', 0.0):.1f}% of transitions "
                f"({td.get('n_max', 0)}) — those trajectories were cut short, so the sampler "
                "explores slowly. Saturation is an efficiency warning, not a validity failure, "
                "but check the geometry before raising max_tree_depth on the NUTS kernel: an "
                "improper or near-improper posterior saturates every transition, and a higher "
                "limit never helps there (references/diagnostics.md, Failure signatures)."
            )
        bfmi = conv.get("bfmi", {})
        if not bfmi.get("ok", True):
            chains = ", ".join(str(c) for c in bfmi.get("failed_chains", []))
            steps.append(
                f"E-BFMI is low on chain(s) {chains} — those chains explore the energy "
                "distribution poorly, often because of heavy tails or a funnel. Plot "
                "az.plot_energy(idata), then work the escalation ladder in "
                "references/diagnostics.md, starting from its Failure signatures table."
            )

    # ── Monte Carlo precision ─────────────────────────────────────────
````

- [ ] **Step 4: Run the suite: green.** Same command as Step 2. Expected: no failures; passed is +12 over Task 2's green run.

- [ ] **Step 5: Commit.**

```bash
git add skills/bayesian-workflow/scripts/check_diagnostics.py skills/bayesian-workflow/scripts/test_check_diagnostics.py skills/bayesian-workflow/scripts/test_diagnose_model.py
```

```bash
git commit -m "fix(bayesian-workflow): give tree-depth saturation and low E-BFMI a next step, and name sampler checks that never ran (audit X2)" -m "check_diagnostics.py adds a step for each, names the sampler flags in the convergence summary instead of 'some parameters', and lists tree depth, E-BFMI or divergences as not checked when diagnose_model.py marks them so (owner decision D2). Writer-to-reader tests run a saturated and an unchecked NumPyro-shaped InferenceData through both scripts."
```

### Task 4: The sample-size Pareto-k cutoff (F8, D1)

**Files:**
- Modify: `skills/bayesian-workflow/scripts/diagnose_model.py`, `skills/bayesian-workflow/scripts/check_diagnostics.py`, `skills/bayesian-workflow/references/model-criticism.md`, `skills/bayesian-workflow/references/reporting.md`, `skills/bayesian-workflow/README.md`
- Test: `skills/bayesian-workflow/scripts/test_check_diagnostics.py`, `skills/bayesian-workflow/scripts/test_diagnose_model.py`

**Interfaces:**
- Consumes: Task 3's `_report_and_steps` and `_complete_idata`; Task 1's `test_the_two_scripts_share_their_thresholds`.
- Produces, in `diagnose_model.py`: `PARETO_K_MAX = 0.7`; `pareto_k_threshold(n_samples) -> float`; `summarize_pareto_k(pareto_k, n_samples) -> dict`, with keys `max`, `good_k`, `n_bad` (finite k above `good_k`), `n_high` (finite k above 0.7), `n_nonfinite` and `ok`, and no `n_marginal`.
- Produces, in `check_diagnostics.py`: `PARETO_K_MAX = 0.7`; `_high_pareto_k(pk: dict) -> int`; LOO rated from the counts: poor for any k > 0.7 or non-finite k, fair when every flagged k is between `good_k` and 0.7, excellent otherwise. New step prefixes: "LOO Pareto-k > 0.7 for N observation(s)" and "LOO Pareto-k is above the sample-size threshold".

- [ ] **Step 1: Write the failing tests.**

Append to the end of `skills/bayesian-workflow/scripts/test_check_diagnostics.py`, after two blank lines:

````python
def _with_pareto_k(**pareto_k):
    diag = _clean_diagnostics()
    diag["loo"]["pareto_k"] = pareto_k
    return diag


def test_pareto_k_between_good_k_and_0_7_asks_for_more_draws():
    # good_k is about 0.656 at S = 800 draws, loo's exploring size here.
    report, steps = _report_and_steps(
        _with_pareto_k(max=0.68, good_k=0.6555, n_bad=3, n_high=0, n_nonfinite=0, ok=False)
    )
    assert report["loo"]["rating"] == "fair"
    step = _one_step(steps, "LOO Pareto-k is above the sample-size threshold 0.66")
    assert "3 observation(s)" in step and "more draws" in step
    assert not _proceeds(steps)


def test_pareto_k_above_0_7_names_the_remedies():
    report, steps = _report_and_steps(
        _with_pareto_k(max=0.92, good_k=0.7, n_bad=2, n_high=2, n_nonfinite=0, ok=False)
    )
    assert report["loo"]["rating"] == "poor"
    step = _one_step(steps, "LOO Pareto-k > 0.7 for 2 observation(s)")
    for remedy in ("azs.reloo", "azs.loo_kfold", "azs.loo_moment_match", "azs.SamplingWrapper"):
        assert remedy in step


def test_the_retired_0_5_band_no_longer_flags():
    report, steps = _report_and_steps(
        _with_pareto_k(max=0.62, good_k=0.7, n_bad=0, n_high=0, n_nonfinite=0, ok=True)
    )
    assert report["loo"]["rating"] == "excellent"
    assert len(steps) == 1 and _proceeds(steps), steps


def test_a_diagnostics_file_without_good_k_reads_n_bad_as_above_0_7():
    # Written before good_k existed: n_bad then counted only k > 0.7.
    report, steps = _report_and_steps(
        _with_pareto_k(max=0.81, n_bad=1, n_marginal=2, n_nonfinite=0, ok=False)
    )
    assert report["loo"]["rating"] == "poor"
    assert "azs.reloo" in _one_step(steps, "LOO Pareto-k > 0.7 for 1 observation(s)")
````

Replace in `skills/bayesian-workflow/scripts/test_diagnose_model.py`:

````python
import json

import arviz as az
````

with:

````python
import json
import math

import arviz as az
````

Replace in `skills/bayesian-workflow/scripts/test_diagnose_model.py`:

````python
def test_the_two_scripts_share_their_thresholds():
    assert diagnose_model.REL_MCSE_OK == cd.REL_MCSE_OK
````

with:

````python
def test_the_two_scripts_share_their_thresholds():
    assert diagnose_model.REL_MCSE_OK == cd.REL_MCSE_OK
    assert diagnose_model.PARETO_K_MAX == cd.PARETO_K_MAX
````

Append to the end of `skills/bayesian-workflow/scripts/test_diagnose_model.py`, after two blank lines:

````python
def test_the_pareto_k_threshold_follows_loo():
    assert diagnose_model.pareto_k_threshold(4000) == 0.7
    assert diagnose_model.pareto_k_threshold(800) == pytest.approx(1 - 1 / math.log10(800))
    assert 0.655 < diagnose_model.pareto_k_threshold(800) < 0.656


def test_pareto_k_counts_against_the_sample_size_threshold():
    k = [0.2, 0.68, 0.9, float("nan")]
    assert diagnose_model.summarize_pareto_k(k, 800) == {
        "max": 0.9, "good_k": 0.6555, "n_bad": 2, "n_high": 1, "n_nonfinite": 1, "ok": False,
    }
    assert diagnose_model.summarize_pareto_k(k, 4000) == {
        "max": 0.9, "good_k": 0.7, "n_bad": 1, "n_high": 1, "n_nonfinite": 1, "ok": False,
    }


def test_check_loo_carries_good_k_and_drops_the_0_5_band():
    pareto_k = diagnose_model.check_loo(_complete_idata())["pareto_k"]
    assert pareto_k["good_k"] == round(diagnose_model.pareto_k_threshold(2000), 4)
    assert "n_high" in pareto_k and "n_marginal" not in pareto_k
````

- [ ] **Step 2: Run them and see them fail.**

```bash
uv run --directory skills/bayesian-workflow/scripts --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray python -m pytest -q -rf
```

Expected: `8 failed`, and passed is one less than Task 3's green run, because the extended threshold test now fails. The 8 `FAILED` lines, with their reasons:
- `test_pareto_k_between_good_k_and_0_7_asks_for_more_draws`: `assert 'poor' == 'fair'` (today's code counts every `n_bad` as poor).
- `test_pareto_k_above_0_7_names_the_remedies` and `test_a_diagnostics_file_without_good_k_reads_n_bad_as_above_0_7`: `_one_step` finds no step with the new prefix; today's reads "LOO Pareto-k > 0.7 for some observations" and names no remedy.
- `test_the_retired_0_5_band_no_longer_flags`: `assert 'fair' == 'excellent'` (the 0.5 band).
- `test_the_two_scripts_share_their_thresholds`: `AttributeError: module 'diagnose_model' has no attribute 'PARETO_K_MAX'`.
- `test_the_pareto_k_threshold_follows_loo` and `test_pareto_k_counts_against_the_sample_size_threshold`: `AttributeError` for `pareto_k_threshold` and `summarize_pareto_k`.
- `test_check_loo_carries_good_k_and_drops_the_0_5_band`: `KeyError: 'good_k'`.

- [ ] **Step 3: Implement the writer's half.** Make four replacements in `skills/bayesian-workflow/scripts/diagnose_model.py`.

Replace in `skills/bayesian-workflow/scripts/diagnose_model.py`:

````python
# The tree-depth saturation flags, NumPyro's first: az.from_numpyro writes
````

with:

````python
# loo's sample-size Pareto-k threshold never exceeds 0.7, and above 0.7 more draws do
# not help. check_diagnostics.py keeps a copy; test_diagnose_model.py pins the two.
PARETO_K_MAX = 0.7

# The tree-depth saturation flags, NumPyro's first: az.from_numpyro writes
````

Replace in `skills/bayesian-workflow/scripts/diagnose_model.py`:

````python
def check_loo(idata):
    """Run LOO-CV and check Pareto k diagnostics.
````

with:

````python
def pareto_k_threshold(n_samples):
    """loo's sample-size Pareto-k threshold, min(1 - 1/log10(S), 0.7); see references/model-criticism.md.

    Computed here from S = chains x draws rather than read from the ELPDData, so
    the same idata gets the same cutoff on ArviZ 0.23 and 1.x. It is 0.7 above
    about 2,200 draws and about 0.656 at the 4 x 200 exploring size.
    """
    return min(1 - 1 / math.log10(n_samples), PARETO_K_MAX)


def summarize_pareto_k(pareto_k, n_samples):
    """The diagnostics.json pareto_k block, counted against pareto_k_threshold.

    n_bad counts each finite k above good_k, where loo calls PSIS-LOO
    unreliable; n_high counts those above 0.7, which more draws cannot fix. A
    non-finite k means PSIS could not estimate that point at all (arviz 1.x
    returns NaN there): it is counted apart in n_nonfinite, and max runs over
    the finite values only, so no bare NaN reaches the JSON (json.dumps would
    emit `NaN`, which is invalid JSON).
    """
    pareto_k = np.asarray(pareto_k, dtype=float)
    finite = pareto_k[np.isfinite(pareto_k)]
    n_nonfinite = int(pareto_k.size - finite.size)
    good_k = pareto_k_threshold(n_samples)
    n_bad = int(np.sum(finite > good_k))
    return {
        "max": float(finite.max()) if finite.size else None,
        "good_k": round(good_k, 4),
        "n_bad": n_bad,
        "n_high": int(np.sum(finite > PARETO_K_MAX)),
        "n_nonfinite": n_nonfinite,
        "ok": n_bad == 0 and n_nonfinite == 0,
    }


def check_loo(idata):
    """Run LOO-CV and check Pareto k diagnostics.
````

Replace in `skills/bayesian-workflow/scripts/diagnose_model.py`:

````python
        loo = az.loo(idata, pointwise=True)
        pareto_k = np.asarray(_loo_field(loo, "pareto_k"), dtype=float)
        elpd = _loo_field(loo, "elpd_loo", "elpd")
        se = _loo_field(loo, "se")
        p_loo = _loo_field(loo, "p_loo", "p")

        # A non-finite Pareto-k means the importance-sampling LOO for that point
        # could not be estimated — arviz 1.x returns NaN there, where arviz 0.23
        # sometimes smoothed it to a finite value. Keep it DISTINCT from a finite
        # k > 0.7 (different diagnosis, different fix), and take the max over the
        # finite values only, so a bare NaN never leaks into the JSON report
        # (json.dumps emits `NaN`, which is invalid JSON).
        finite = pareto_k[np.isfinite(pareto_k)]
        n_nonfinite = int(pareto_k.size - finite.size)

        # Pareto-k cutoff is held at the classic 0.7 (not arviz 1.x's
        # data-dependent good_k) so the same idata yields the same rating on both
        # the PyMC 5 and PyMC 6 stacks — cross-version equivalence over novelty.
        # n_bad counts ONLY finite k > 0.7, so the "k > 0.7" wording downstream is
        # always literally true; non-finite points are reported via n_nonfinite.
        n_high = int(np.sum(finite > 0.7))
        results = {
            "elpd": float(elpd) if elpd is not None else None,
            "se": float(se) if se is not None else None,
            "p_loo": float(p_loo) if p_loo is not None else None,
            "pareto_k": {
                "max": float(finite.max()) if finite.size else None,
                "n_bad": n_high,
                "n_marginal": int(np.sum((finite > 0.5) & (finite <= 0.7))),
                "n_nonfinite": n_nonfinite,
                "ok": n_high == 0 and n_nonfinite == 0,
            },
            "computed": True,
        }
````

with:

````python
        loo = az.loo(idata, pointwise=True)
        elpd = _loo_field(loo, "elpd_loo", "elpd")
        se = _loo_field(loo, "se")
        p_loo = _loo_field(loo, "p_loo", "p")
        n_samples = int(idata.posterior.sizes["chain"]) * int(idata.posterior.sizes["draw"])
        results = {
            "elpd": float(elpd) if elpd is not None else None,
            "se": float(se) if se is not None else None,
            "p_loo": float(p_loo) if p_loo is not None else None,
            "pareto_k": summarize_pareto_k(_loo_field(loo, "pareto_k"), n_samples),
            "computed": True,
        }
````

Replace in `skills/bayesian-workflow/scripts/diagnose_model.py`:

````python
    if loo_pk and not loo_pk.get("ok", True):
        n_high = loo_pk.get("n_bad", 0)
        n_nf = loo_pk.get("n_nonfinite", 0)
        parts = []
        if n_high:
            parts.append(f"{n_high} observation(s) with Pareto k > 0.7")
````

with:

````python
    if loo_pk and not loo_pk.get("ok", True):
        n_bad = loo_pk.get("n_bad", 0)
        n_nf = loo_pk.get("n_nonfinite", 0)
        parts = []
        if n_bad:
            parts.append(f"{n_bad} observation(s) with Pareto k above {loo_pk['good_k']:.2f}")
````

- [ ] **Step 4: Implement the reader's half.** Make five replacements in `skills/bayesian-workflow/scripts/check_diagnostics.py`.

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
PARETO_K_OK = 0.5
PARETO_K_FAIR = 0.7
COVERAGE_DEVIATION_OK = 0.02
````

with:

````python
COVERAGE_DEVIATION_OK = 0.02
````

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
REL_MCSE_OK = 0.05
````

with:

````python
REL_MCSE_OK = 0.05

# loo's sample-size Pareto-k threshold (good_k, which diagnose_model.py writes) never
# exceeds 0.7, and above 0.7 more draws do not help. A copy, pinned like REL_MCSE_OK.
PARETO_K_MAX = 0.7
````

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
def _rate_loo(loo: dict) -> str:
    """Return a qualitative rating for the LOO Pareto-k diagnostic."""
    if not loo or not loo.get("computed"):
        return "not computed"

    pk = loo.get("pareto_k", {})
    n_bad = pk.get("n_bad", 0)
    n_nonfinite = pk.get("n_nonfinite", 0)
    pk_max = pk.get("max")

    # Any bad point caps the rating at poor — whether a finite k > 0.7 or a
    # non-finite k that LOO could not estimate. A low max over the *remaining*
    # points doesn't redeem an unreliable observation. pk_max is None only when
    # every point is non-finite.
    if n_bad > 0 or n_nonfinite > 0:
        return "poor"
    if pk_max is None:
        return "not computed"
    if pk_max <= PARETO_K_OK:
        return "excellent"
    if pk_max <= PARETO_K_FAIR:
        return "fair"
    return "poor"
````

with:

````python
def _high_pareto_k(pk: dict) -> int:
    """Finite k > 0.7. A file written before good_k had no n_high, and its n_bad meant this."""
    return pk.get("n_high", pk.get("n_bad", 0))


def _rate_loo(loo: dict) -> str:
    """Return a qualitative rating for the LOO Pareto-k diagnostic.

    Rated from diagnose_model.py's counts against loo's sample-size threshold
    good_k: poor for any k > 0.7 or non-finite k, which more draws cannot fix;
    fair when every flagged k lies between good_k and 0.7, which more draws can.
    """
    if not loo or not loo.get("computed"):
        return "not computed"

    pk = loo.get("pareto_k", {})
    # Any bad point caps the rating — a low max over the *remaining* points
    # doesn't redeem an unreliable observation. max is None only when every
    # point is non-finite.
    if _high_pareto_k(pk) > 0 or pk.get("n_nonfinite", 0) > 0:
        return "poor"
    if pk.get("max") is None:
        return "not computed"
    if pk.get("n_bad", 0) > 0:
        return "fair"
    return "excellent"
````

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
            # carry the Pareto-k breakdown so suggest_next_steps can distinguish
            # finite k > 0.7 from non-finite (could-not-estimate) points.
````

with:

````python
            # carry the Pareto-k breakdown so suggest_next_steps can tell k above
            # good_k, k > 0.7 and non-finite (could-not-estimate) points apart.
````

Replace in `skills/bayesian-workflow/scripts/check_diagnostics.py`:

````python
    loo_pk = loo.get("pareto_k", {})
    n_high = loo_pk.get("n_bad", 0)
    n_nonfinite = loo_pk.get("n_nonfinite", 0)
    if loo_rating == "poor":
        if n_high:
            steps.append(
                "LOO Pareto-k > 0.7 for some observations — these points are highly "
                "influential. Inspect them (often outliers or high-leverage), consider "
                "a more robust likelihood (StudentT), or refit excluding them to test "
                "sensitivity. Use az.loo(idata, pointwise=True) and az.plot_khat(loo)."
            )
        if n_nonfinite:
            steps.append(
                f"LOO could not be estimated for {n_nonfinite} observation(s) "
                "(non-finite Pareto-k — degenerate importance weights). This usually "
                "co-occurs with sampling problems, so fix convergence first; then "
                "inspect those points and consider a more robust likelihood (StudentT)."
            )
        if not n_high and not n_nonfinite:
            steps.append(
                "LOO flags a problem — inspect the pointwise Pareto-k with "
                "az.loo(idata, pointwise=True) and az.plot_khat(loo)."
            )
    elif loo_rating == "fair":
        steps.append(
            "LOO Pareto-k between 0.5 and 0.7 for some observations — borderline. "
            "Identify the points and decide whether they're substantively important; "
            "consider a robust likelihood if they reflect a tail-heavy data process."
        )
````

with:

````python
    loo_pk = loo.get("pareto_k", {})
    n_high = _high_pareto_k(loo_pk)
    n_nonfinite = loo_pk.get("n_nonfinite", 0)
    if loo_rating == "poor":
        if n_high:
            steps.append(
                f"LOO Pareto-k > {PARETO_K_MAX} for {n_high} observation(s) — PSIS-LOO is "
                "unreliable there, and more draws will not fix it. Inspect them with "
                "az.plot_khat(loo) (often outliers or high-leverage points) and consider a "
                "more robust likelihood (StudentT). For exact values at those points, refit "
                "with azs.reloo (one refit per flagged point) or azs.loo_kfold (K refits) "
                "through an azs.SamplingWrapper subclass for your model, or run "
                "azs.loo_moment_match with your model's log-density functions (it builds "
                "them itself only for PyMC and Bambi)."
            )
        if n_nonfinite:
            steps.append(
                f"LOO could not be estimated for {n_nonfinite} observation(s) "
                "(non-finite Pareto-k — degenerate importance weights). This usually "
                "co-occurs with sampling problems, so fix convergence first; then "
                "inspect those points and consider a more robust likelihood (StudentT)."
            )
    elif loo_rating == "fair":
        steps.append(
            f"LOO Pareto-k is above the sample-size threshold {loo_pk.get('good_k', PARETO_K_MAX):.2f} "
            f"but at most {PARETO_K_MAX} for {loo_pk.get('n_bad', 0)} observation(s) — PSIS-LOO "
            "is not reliable there yet, but more draws may fix it: the threshold rises to "
            f"{PARETO_K_MAX} at about 2,200 draws in total (loo's Pareto-k diagnostic). Re-run "
            "with more draws before trusting or comparing LOO."
        )
````

The old poor-branch fallback ("LOO flags a problem …") goes because it can no longer run: a poor rating now always has a k > 0.7 or a non-finite k.

- [ ] **Step 5: Run the suite: green.** Same command as Step 2. Expected: no failures; passed is +7 over Task 3's green run, so +50 over the baseline.

- [ ] **Step 6: Update the docs.**

Replace in `skills/bayesian-workflow/references/model-criticism.md`:

````markdown
**Pareto k diagnostic** — Critical for trusting LOO results:

| Pareto k | Interpretation | Action |
|---|---|---|
| < 0.5 | Reliable | Trust LOO estimate |
| 0.5–0.7 | Marginally reliable | Investigate flagged observations |
| > 0.7 (or > `loo.good_k`) | Unreliable for that observation | Use K-fold CV or moment matching |
````

with:

````markdown
**Pareto k diagnostic** — Critical for trusting LOO results. The threshold depends on the number of posterior draws S (chains × draws): `good_k = min(1 − 1/log10(S), 0.7)`, which is 0.7 above about 2,200 draws and about 0.66 at 4 × 200 (<https://mc-stan.org/loo/reference/pareto-k-diagnostic.html>; the old fixed 0.5 band is retired). ArviZ 1.x reports it as `loo.good_k`, and `diagnose_model.py` writes it to `diagnostics.json → loo.pareto_k.good_k`.

| Pareto k | Interpretation | Action |
|---|---|---|
| ≤ `good_k` | Reliable | Trust the LOO estimate |
| `good_k` < k ≤ 0.7 | Unreliable, but only because S is small | Run more draws: above about 2,200, `good_k` reaches 0.7 |
| > 0.7 | Unreliable for that observation; more draws do not help | Get exact values for those points: `azs.reloo` (one refit per flagged point) or `azs.loo_kfold` (K refits), both through an `azs.SamplingWrapper` subclass for your model, or `azs.loo_moment_match` with your model's log-density functions (it builds them itself only for PyMC and Bambi). Or use a more robust likelihood |
````

Replace in `skills/bayesian-workflow/references/model-criticism.md`:

````python
bad_obs = np.where(pareto_k > 0.7)[0]
````

with:

````python
bad_obs = np.where(pareto_k > loo.good_k)[0]
````

Replace in `skills/bayesian-workflow/references/reporting.md`:

````markdown
- LOO Pareto k > 0.7 for some observations → "Investigate the influential points (often outliers or leverage). Consider a more robust likelihood or refit excluding the worst points to test sensitivity."
````

with:

````markdown
- LOO Pareto k > 0.7 for some observations → "PSIS-LOO is unreliable there, and more draws will not fix it. Inspect the points (often outliers or leverage), consider a more robust likelihood, and get exact values with `azs.reloo` or `azs.loo_kfold` (refits through an `azs.SamplingWrapper`) or `azs.loo_moment_match`."
- LOO Pareto k above `good_k` but at most 0.7 (fewer than about 2,200 draws) → "Re-run with more draws before trusting or comparing LOO."
````

Replace in `skills/bayesian-workflow/references/reporting.md`:

````markdown
- **Pareto k**: all < 0.5 ✓ (or list problematic observations)
````

with:

````markdown
- **Pareto k**: all ≤ `good_k` (min(1 − 1/log10 S, 0.7), from `diagnostics.json → loo.pareto_k`) ✓ (or list problematic observations)
````

Replace in `skills/bayesian-workflow/README.md`:

````markdown
    ├── test_diagnose_model.py        # pytest: precision block (run from scripts/)
````

with:

````markdown
    ├── test_diagnose_model.py        # pytest: precision, sampler-stat and Pareto-k blocks; the report's verdict (run from scripts/)
````

Replace in `skills/bayesian-workflow/README.md`:

````markdown
    └── test_check_diagnostics.py     # pytest: divergence-fraction gate + calibration advice in suggested next steps
````

with:

````markdown
    └── test_check_diagnostics.py     # pytest: a next step for each failed or missing check; the all-clear only when every required check passed
````

- [ ] **Step 7: Check the edited snippet.** Tier 1 parses every fenced block, including the one Step 6 changed.

```bash
uv run --python 3.13 python build/check_snippets.py skills/
```

Expected: exit 0. Its `WARN` lines are the ones `main` prints too.

- [ ] **Step 8: Commit.**

```bash
git add skills/bayesian-workflow/scripts/diagnose_model.py skills/bayesian-workflow/scripts/check_diagnostics.py skills/bayesian-workflow/scripts/test_check_diagnostics.py skills/bayesian-workflow/scripts/test_diagnose_model.py skills/bayesian-workflow/references/model-criticism.md skills/bayesian-workflow/references/reporting.md skills/bayesian-workflow/README.md
```

```bash
git commit -m "feat(bayesian-workflow): rate Pareto k against loo's sample-size threshold (audit F8, owner decision D1)" -m "diagnose_model.py computes good_k = min(1 - 1/log10 S, 0.7) from the draw count, the same on every ArviZ version, and writes good_k, n_bad and n_high in place of the retired 0.5 band. check_diagnostics.py rates LOO fair when only more draws are needed and poor above 0.7, where its step names reloo, loo_kfold and loo_moment_match."
```

### Task 5: Acceptance on real NumPyro output

**Files:**
- Create: `.sdd/56-diagnostics-harness-verdicts/fit.py` (git ignores `.sdd/`; never committed)

**Interfaces:**
- Consumes: Tasks 1–4.
- Produces: no committed file. This task's outputs are the Expected lines below, for the final review.

- [ ] **Step 1: Write the fit script.** It fits one small regression twice. `saturated.nc` runs NUTS with `max_tree_depth=1` and collects `num_steps`, so every draw hits the limit. `unchecked.nc` runs the default NUTS without `num_steps`, so `az.from_numpyro` writes no tree-depth flag.

Create `.sdd/56-diagnostics-harness-verdicts/fit.py`:

````python
'''Fit one small NumPyro regression twice and save both runs as netCDF (plan 56 acceptance).

saturated.nc: NUTS(max_tree_depth=1) with num_steps collected, so every draw hits the limit.
unchecked.nc: default NUTS without num_steps, so az.from_numpyro writes no tree-depth flag.
'''
import sys

import arviz as az
import jax
import numpy as np
import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS, Predictive


def model(x, y=None):
    a = numpyro.sample('a', dist.Normal(0, 1))
    b = numpyro.sample('b', dist.Normal(0, 1))
    s = numpyro.sample('s', dist.HalfNormal(1))
    numpyro.sample('y', dist.Normal(a + b * x, s), obs=y)


out = sys.argv[1]
rng = np.random.default_rng(0)
x = rng.normal(size=100)
y = 1 + 2 * x + rng.normal(size=100)
runs = {
    'saturated': ({'max_tree_depth': 1}, ('energy', 'diverging', 'num_steps', 'accept_prob')),
    'unchecked': ({}, ('energy', 'diverging', 'accept_prob')),
}
for name, (kernel_kwargs, extra_fields) in runs.items():
    mcmc = MCMC(NUTS(model, **kernel_kwargs), num_warmup=1000, num_samples=1000, num_chains=4,
                chain_method='sequential', progress_bar=False)
    mcmc.run(jax.random.PRNGKey(0), x, y=y, extra_fields=extra_fields)
    ppc = Predictive(model, posterior_samples=mcmc.get_samples())(jax.random.PRNGKey(1), x)
    idata = az.from_numpyro(mcmc, posterior_predictive=ppc, log_likelihood=True)
    idata.to_netcdf(f'{out}/{name}.nc')
    print(name, 'saved')
````

- [ ] **Step 2: Fit both runs** on the pinned stack (`build/snippet_preamble.py`'s `PINNED`). It takes about a minute.

```bash
uv run --python 3.13 --with 'arviz==1.3.0' --with arviz-base --with 'arviz-stats==1.3.2' --with 'arviz-plots==1.3.1' --with 'numpyro==0.21.0' --with 'jax==0.11.1' --with numpy --with xarray --with scipy --with h5netcdf --with h5py --with matplotlib python .sdd/56-diagnostics-harness-verdicts/fit.py .sdd/56-diagnostics-harness-verdicts
```

Expected: `saturated saved`, then `unchecked saved`.

- [ ] **Step 3: Run the pipeline on the saturated run**, as `SKILL.md`'s Utility scripts section runs it.

```bash
uv run --python 3.13 --with 'arviz==1.3.0' --with arviz-base --with 'arviz-stats==1.3.2' --with numpy --with h5netcdf --with h5py python skills/bayesian-workflow/scripts/diagnose_model.py --idata .sdd/56-diagnostics-harness-verdicts/saturated.nc --output .sdd/56-diagnostics-harness-verdicts/saturated-diag.json
```

```bash
uv run --python 3.13 --with 'arviz==1.3.0' --with arviz-base --with 'arviz-stats==1.3.2' --with 'arviz-plots==1.3.1' --with numpy --with xarray --with scipy --with h5netcdf --with h5py --with matplotlib python skills/bayesian-workflow/scripts/calibration_check.py --idata .sdd/56-diagnostics-harness-verdicts/saturated.nc --output .sdd/56-diagnostics-harness-verdicts/saturated-cal.json
```

```bash
uv run --python 3.13 python skills/bayesian-workflow/scripts/check_diagnostics.py --diagnostics .sdd/56-diagnostics-harness-verdicts/saturated-diag.json --calibration .sdd/56-diagnostics-harness-verdicts/saturated-cal.json
```

Expected:
- `saturated-diag.json` holds `"treedepth": {"checked": true, "ok": false, "n_max": 4000, "pct": 100.0}` and `"all_ok": false`. Its LOO block has `good_k` 0.7, with `n_bad` and `n_high` 0.
- In the last command's output, the convergence line ends "max treedepth saturation. Inspect before trusting the posterior." On the planning Mac it read "Convergence is fair — flags on a; max treedepth saturation. …", because `a`'s R-hat there was 1.011, which also put an R-hat step first. Another platform may not flag `a`.
- One suggested step starts "Tree depth hit max_tree_depth on 100.0% of transitions (4000)". No step says "proceed to interpretation".

- [ ] **Step 4: Run the pipeline on the unchecked run.** Use the three commands of Step 3, with `unchecked` in place of `saturated` in every path.

Expected:
- `unchecked-diag.json` holds `"treedepth": {"checked": false}`, a bfmi and a divergences block with `"checked": true`, and `"all_ok": true`. Its overall recommendation is "Model is ready for interpretation."
- The convergence line reads "Convergence diagnostics that ran passed (R-hat ≤ 1.01, ESS adequate, no divergences); not checked: tree depth."
- Step 1 is the all-clear. Step 2 starts "Not checked: tree depth (collect num_steps in extra_fields so az.from_numpyro writes reached_max_tree_depth); prior sensitivity (run psense_summary(idata) …".

- [ ] **Step 5: Run the suite on the pinned stack and under Python 3.11.**

```bash
uv run --directory skills/bayesian-workflow/scripts --python 3.13 --with pytest --with 'arviz==1.3.0' --with arviz-base --with 'arviz-stats==1.3.2' --with numpy --with xarray python -m pytest -q
```

Expected: the same counts as Task 4's green run on the floating stack.

```bash
uv run --directory skills/bayesian-workflow/scripts --python 3.11 --with pytest python -m pytest -q test_check_diagnostics.py
```

Expected: every test passes, none skipped. That is plan 53's 3.11 floor for the stdlib-only reader.

- [ ] **Step 6: Run snippet Tiers 2 and 3**, since Task 4 changed a fence in `model-criticism.md`. Tier 3 takes minutes.

```bash
uv run --python 3.13 --with "arviz>=1.0" --with arviz-base --with arviz-stats --with arviz-plots --with numpyro --with jax python build/check_snippets.py --api skills/bayesian-workflow/
```

```bash
uv run --python 3.13 --with 'arviz==1.3.0' --with arviz-base --with 'arviz-stats==1.3.2' --with 'arviz-plots==1.3.1' --with 'numpyro==0.21.0' --with 'jax==0.11.1' --with numpy --with matplotlib python build/check_snippets.py --run skills/bayesian-workflow/
```

Expected: both exit 0. Tier 3 still prints `WARN skills/bayesian-workflow/references/model-criticism.md:76: not executed: unbound names ['loo']` for the Pareto-k snippet, as on `main` (Facts).

- [ ] **Step 7: Run the commit lints.**

```bash
bash build/run_commit_lints.sh
```

Expected: the last line is `commit lints passed`. The drift lint's `STALE` lines never fail it.

## Self-review

- **Backlog coverage.**
  - X1 (a) precision: Task 1's precision rating, step and summary line, plus the writer's MCSE issue.
  - X1 (b) LOO's error: Task 1's "LOO was not computed" step and the writer's "LOO not computed" issue.
  - X1 (c) the all-clear: Task 1's `_closing_steps`, gate and "Not checked:" step (DF1–DF3).
  - X1 Done when ("a report with no LOO, or with a failing MCSE, gets no all-clear, and tests pin each case"): Task 1, Steps 3–7.
  - X2 (1) both paths: Task 2's `_treedepth_block`. X2 (2) `all_ok`: Task 2, both paths. X2 (3) `checked: false`: Task 2, and D2 extends it to E-BFMI and divergences. X2 (4) red tests in both files: Tasks 2 and 3. X2 (5) the docstring, comment and `diagnostics.md`: Task 2.
  - X2 Done when ("a saturated NumPyro run reports saturation, an unchecked one reports 'not checked', and tests pin both"): Task 3's writer-to-reader tests, and Task 5 on real output.
  - F8: the owner's call is D1. The 0.5 band goes and `good_k` is carried (Task 4, both scripts). The remedies are named in the high-k step and in `model-criticism.md` (Task 4).
  - The brief's constraints: red tests in both test files (every task); plan 53's coupling (Couplings and Global Constraints); the plan id (Plan ID); section 34 (Planning record).
- **Placeholders.** None. Every code step shows its code, and every run step shows its command and expected output.
- **Names.** `REL_MCSE_OK`, `PARETO_K_MAX`, `REQUIRED_CHECKS`, `PSENSE_REMEDY`, `NON_PARAM_TOKENS`, `SAMPLER_CHECKS`, `TREEDEPTH_FLAGS`, `_rate_precision`, `_not_checked`, `_closing_steps`, `_split_flags`, `_flag_phrase`, `_unchecked_sampler_checks`, `_high_pareto_k`, `_sample_stats`, `_divergence_block`, `_treedepth_block`, `_bfmi_block`, `pareto_k_threshold` and `summarize_pareto_k` are the same in every task and test. So are the JSON keys `checked`, `good_k`, `n_bad`, `n_high` and `n_nonfinite`.
- **Replay.** A script applied the blocks above to a fresh clone of `668b8c3`, step by step. Each red and green state and each Task 5 Expected line matched (Prototype and replay). The replay also caught two defects in this plan, now fixed: Task 1, Step 5 said seven replacements where it has nine, and a `diagnostics.md` block quoted part of a table row instead of the whole row.

## Execution handoff

Execute in a fresh session on Sonnet (the owner's routing: plan on Opus, execute on Sonnet), with this plan file as the handoff. Make the worktree from an up-to-date `main` after this plan merges, on a branch such as `fix/plan-56-diagnostics-verdicts`. Subagent-driven development fits: each task has its own red and green cycle and its own commit, and only Task 5's fit and Tier 3 run long. Tasks 1–4 edit the same two scripts in order, so run them one at a time.

## Plan completion

Run the writing-plans Plan Completion Protocol after the final review, then:

- **Tick the three backlog items.** In `specs/deferred_items.md`, section `audit-3-10-26 routing (no plan; re-verification pass, branch claude/quizzical-hermann-814d89) — 2026-10-18`, tick X1, X2 and F8 (`- [x] … → done in plan 56`). That section arrives with commit `4b683a4`: if it is not on `main` yet, ask the owner before you merge it here.
- **Retire this plan.** There is no spec to retire with it.
