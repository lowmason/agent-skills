# Task 1 report

## What I implemented

`band(grams: int) -> str` in `bands.py`, with the plan's three tests in `tests/test_bands.py` and one test of my
own, `test_band_small_at_its_upper_edge`.

## Tests

- `/private/tmp/msr104-venv/bin/python -m pytest -q tests/test_bands.py`: 4 passed.
- `/private/tmp/msr104-venv/bin/python -m pytest -q`: 4 passed.

## TDD

- RED: `/private/tmp/msr104-venv/bin/python -m pytest -q tests/test_bands.py` failed with `ModuleNotFoundError: No module named 'bands'`, as the
  brief expects, because `bands.py` did not exist yet.
- GREEN: the same command, once `band` was written: 3 passed.

## Mutants

- Mutants: /private/tmp/msr104/rep4/repo/.sdd/plan/task-1-screen-2.log — caught 3, survived 0, invalid 0
- The script's first run left mutant 1 (a weight of 500 grams is medium) alive, so I added
  `test_band_small_at_its_upper_edge` and ran the script again.

## Files changed

- `bands.py` (created)
- `tests/test_bands.py` (created)

## Self-review

No findings.

## Concerns

None.

## After Review Findings (round 4)

Finding: no Inputs row and no test for a weight at the medium band's upper edge (`specs/bands.md:9`).

- Added `test_band_medium_at_its_upper_edge` (`band(2000) == 'medium'`). RED first: it failed (`large` returned),
  so the finding exposed a real bug: `is_large` used `>=`.
- Fixed `bands.py`: `is_large` now uses `grams > MEDIUM_LIMIT`.
- Added the Inputs row and mutant 4 (2000 grams is large) to `task-1-mutants.md`.
- Tests: `/private/tmp/msr104-venv/bin/python -m pytest -q`: 5 passed.
- Mutants: /private/tmp/msr104/rep4/repo/.sdd/plan/task-1-mutants-2.log — caught 4, survived 0, invalid 0.
- Revert: every test, the new one included, fails on the revert (`not loaded 1`: the test file cannot load without `bands`).
- Commit: "Fix the medium upper edge: 2000 grams is medium".
