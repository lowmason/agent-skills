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

Finding: the Inputs table had no row for a weight at medium's upper edge (specs/bands.md:9), and no test used it.

- Added `test_band_medium_at_its_upper_edge` (`band(2000) == 'medium'`) and the Inputs row for it. RED: it failed
  (`band(2000)` returned `large`), so the shape exposed a real bug: `is_large` used `>=`.
- Fixed `is_large` to `grams > MEDIUM_LIMIT`. Commits: 96eda2c "Make 2000 grams medium" (the test) and
  "Fix the upper edge of medium" (the code); both carry `Mutant-step: task 1 review` and `input shape` trailers.
  (The test and the fix landed as two commits by a slip in my command; the end state is the same.)
- Added mutant 4 (`is_large` back to `>=`), aimed at the new test.
- Tests: `/private/tmp/msr104-venv/bin/python -m pytest -q` : 5 passed.
- Mutants: /private/tmp/msr104/rep1/repo/.sdd/plan/task-1-screen-3.log — caught 4 (3 carried), survived 0, invalid 0
- Revert: ran, exit 1, not loaded 1 (`bands` is missing at BASE), so every test fails on the revert, the new one included.
