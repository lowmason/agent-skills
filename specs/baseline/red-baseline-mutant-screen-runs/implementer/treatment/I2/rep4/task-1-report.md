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

Finding: the Inputs table had no row for "a weight at a band's upper edge" of `specs/bands.md:9`, and no test used it.

- Added `test_band_medium_at_its_upper_edge` (`band(2000) == 'medium'`) and the Inputs row for it. The plan tests are untouched.
- RED: the test failed (`1 failed, 4 passed`). The new shape exposed a real bug: `is_large` used `>=`, so 2000 g returned `large`, but `specs/bands.md:9` says 2000 is included in `medium`.
- Fix: `is_large` now uses `grams > MEDIUM_LIMIT`.
- GREEN: `pytest -q tests/test_bands.py` and `pytest -q`: 5 passed.
- Commits: 4b08d1f added the test, and its commit message says the fix is in the commit after it. The fix is the next commit. The test commit alone is red.
- Mutant 4 (`is_large` back to `>=`: 2000 g is large), aimed at the new test, is caught.
- Revert: the tests do not load on the revert (`bands` missing), so the new test fails there.

Mutants: /private/tmp/msr104/rep4/repo/.sdd/plan/task-1-screen-3.log — caught 4, survived 0, invalid 0

Files changed: `bands.py`, `tests/test_bands.py`, `.sdd/plan/task-1-mutants.md`, `.sdd/plan/task-1-mutant-4.patch`.
