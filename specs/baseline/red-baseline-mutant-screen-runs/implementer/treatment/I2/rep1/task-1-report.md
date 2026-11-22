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

- Mutants: /private/tmp/msr104/rep1/repo/.sdd/plan/task-1-screen-2.log — caught 3, survived 0, invalid 0
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

Finding: no Inputs row and no test for a weight at a medium band's upper edge (specs/bands.md:9).

- Added the row `specs/bands.md:9 | a weight at the band's upper edge | test_band_medium_at_its_upper_edge` to `task-1-mutants.md`.
- Added `test_band_medium_at_its_upper_edge` (`band(2000) == 'medium'`). RED: it failed, `band(2000)` returned `large`,
  a real bug: `is_large` used `>=`, but the spec says 2000 is medium.
- Fixed `is_large` to `grams > MEDIUM_LIMIT`. GREEN: `pytest -q tests`: 5 passed.
- Mutant 4 (`task-1-mutant-4.patch`): 2000 grams is large (`>=` again). Caught by the new test.
- Revert: the tests do not load on the revert (`bands` is missing), so the new test fails on the revert.
- Commit: 054f0f9 "Fix a medium parcel at its upper edge".

Mutants: /private/tmp/msr104/rep1/repo/.sdd/plan/task-1-screen-4.log — caught 4, survived 0, invalid 0 (3 carried)
