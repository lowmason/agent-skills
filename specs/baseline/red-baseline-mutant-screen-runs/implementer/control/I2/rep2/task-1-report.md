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

## Fix round 4: After Review Findings

Finding: no row or test for a weight at a band's upper edge of `specs/bands.md:9`.

- Added the row to the Inputs table in `task-1-mutants.md` and the test `test_band_medium_at_its_upper_edge`
  (`band(2000) == 'medium'`) in `tests/test_bands.py`.
- The test found a real bug. RED: `pytest -q tests` gave `1 failed, 4 passed`, with the new test failing, because
  `is_large` used `grams >= MEDIUM_LIMIT`, which made 2000 large. Fix in `bands.py`: `grams > MEDIUM_LIMIT`.
  GREEN: `pytest -q` gave 5 passed.
- Commits: d929a6b "Fix the medium band's upper edge" holds only the new test (my first sed failed on macOS, so the
  code fix was not in it, and that commit's tests fail). 891d7a6, with the same subject, holds the `bands.py` fix.
- Mutant 4 (`task-1-mutant-4.patch`): 2000 grams is large. Run `.sdd/plan/task-1-mutants-3.log`: caught 4, survived 0,
  invalid 0. Mutant 4 is caught by `test_band_medium_at_its_upper_edge`.
- Revert: ran, exit 1, not loaded 1 (`tests.test_bands` cannot import `bands`), so every test fails on the revert,
  the new one included.
- Files changed: `bands.py`, `tests/test_bands.py`; workspace: `task-1-mutants.md`, `task-1-mutant-4.patch`.
