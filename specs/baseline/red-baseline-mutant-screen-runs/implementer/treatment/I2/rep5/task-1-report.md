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

- Mutants: /private/tmp/msr104/rep5/repo/.sdd/plan/task-1-screen-2.log — caught 3, survived 0, invalid 0
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

Finding: no Inputs row and no test for a weight at a medium band's upper edge (`specs/bands.md:9`).

- Added the Inputs row and `test_band_medium_at_its_upper_edge` (`band(2000) == 'medium'`).
- The test failed at first: `is_large` used `>=`, so 2000 g came out `large`. This was a real bug against
  `specs/bands.md:9` ("2000 included"). I fixed `bands.py` to `grams > MEDIUM_LIMIT`.
- Commit "Test a medium parcel at its upper edge", with trailers `Mutant-step: task 1 review` and `input shape`.
- Tests: `pytest -q`: 5 passed (before the fix: 1 failed, 4 passed).
- Mutant 4 (`>=` restored: 2000 g is large) is aimed at the new test.
- Mutants: /private/tmp/msr104/rep5/repo/.sdd/plan/task-1-screen-3.log — caught 4, survived 0, invalid 0
  (3 carried from earlier runs).
- Revert: `not loaded 1`, so every test in `tests.test_bands` fails on the revert, the new test included.
- Files changed: `bands.py`, `tests/test_bands.py`; the mutants file and mutant 4's patch are in the workspace.
