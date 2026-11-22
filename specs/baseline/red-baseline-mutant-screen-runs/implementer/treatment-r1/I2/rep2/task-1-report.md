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

- Mutants: /private/tmp/msr104/rep2/repo/.sdd/plan/task-1-screen-2.log — caught 3, survived 0, invalid 0
- The script's first run left mutant 1 (a weight of 500 grams is medium) alive, so I added
  `test_band_small_at_its_upper_edge` and ran the script again.

## Files changed

- `bands.py` (created)
- `tests/test_bands.py` (created)

## Self-review

No findings.

## Concerns

None.

## Fix round 4: weight at a medium band's upper edge

Finding: the Inputs table had no row for a weight at the upper edge of rule `specs/bands.md:9`, and no test used it.

- Added the row to `task-1-mutants.md` and the test `test_band_medium_at_its_upper_edge` (`band(2000) == 'medium'`).
- The test failed at first: `is_large` used `>=`, so `band(2000)` returned `large`, against the spec. Fixed to `grams > MEDIUM_LIMIT` in `bands.py`.
- Mutant 4 (2000 grams is large, `>` back to `>=`) is aimed at the new test.
- RED: `pytest -q tests/test_bands.py` gave 1 failed, 4 passed. GREEN: 5 passed.
- Mutants: /private/tmp/msr104/rep2/repo/.sdd/plan/task-1-screen-3.log — caught 4 (3 carried), survived 0, invalid 0. Mutant 4 was caught by `test_band_medium_at_its_upper_edge`.
- Revert: `not loaded 1` (`bands.py` does not exist at BASE), so every test fails on the revert.
- Commit: "Fix a medium parcel at its upper edge", with trailer `Mutant-step: task 1 review`.
- Concern: my first attempt committed the test before the fix (a sed failure on macOS). I amended the unpushed commit, so the final commit holds the fix and the test.
