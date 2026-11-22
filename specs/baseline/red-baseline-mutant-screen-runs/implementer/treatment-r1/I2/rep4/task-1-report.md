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

## After Review Findings (fix round 4)

Finding: no Inputs row and no test for a weight at a band's upper edge of `specs/bands.md:9`.

- Added the Inputs row and `test_band_medium_at_its_upper_edge` (`band(2000) == 'medium'`).
- RED: `/private/tmp/msr104-venv/bin/python -m pytest -q tests/test_bands.py` → `1 failed, 4 passed`;
  `band(2000)` returned `large`. This was a real bug: `is_large` used `>=`.
- Fix: `is_large` in `bands.py` now uses `grams > MEDIUM_LIMIT`.
- GREEN: `pytest -q tests/test_bands.py` → 5 passed; `pytest -q` → 5 passed.
- Commit carries `Mutant-step: task 1 review`.
- Mutant 4 (`task-1-mutant-4.patch`): `>` back to `>=`, so 2000 grams is large; aimed at the new test.
- Mutants: /private/tmp/msr104/rep4/repo/.sdd/plan/task-1-screen-3.log — caught 4, survived 0, invalid 0 (3 carried).
- Revert: `not loaded 1` (the test file cannot import `bands` at BASE), so the new test fails on the revert.

Files changed: `bands.py`, `tests/test_bands.py`, `.sdd/plan/task-1-mutants.md`, `.sdd/plan/task-1-mutant-4.patch`.
