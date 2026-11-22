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

- Mutants: /private/tmp/msr104/rep3/repo/.sdd/plan/task-1-screen-2.log — caught 3, survived 0, invalid 0
- The script's first run left mutant 1 (a weight of 500 grams is medium) alive, so I added
  `test_band_small_at_its_upper_edge` and ran the script again.

## Files changed

- `bands.py` (created)
- `tests/test_bands.py` (created)

## Self-review

No findings.

## Concerns

None.

## After Review Findings — fix round 4

Finding: no Inputs row and no test for a weight at the medium band's upper edge (`specs/bands.md:9`).

- Added `test_band_medium_at_its_upper_edge` (`band(2000) == 'medium'`). It failed at first: `band(2000)` returned
  `large` because `is_large` used `>=`. That was a real bug against `specs/bands.md:9` ("2000 included").
- Fixed `bands.py`: `is_large` now uses `grams > MEDIUM_LIMIT`.
- Also added the shapes just above each lower edge: `test_band_medium_just_above_small` (501) and
  `test_band_large_just_above_medium` (2001). The Inputs table in `task-1-mutants.md` now has a row for each.
- Mutants 4-6 aim at the three new tests (2000 is large; 501 is small; 2001 is medium).
- Commits: the first fix commit (tests plus a failed `sed` that left the bug in) was followed by a second commit
  that applied the code fix. The first of the two commits therefore has a failing test.

Tests: `/private/tmp/msr104-venv/bin/python -m pytest -q tests`: 7 passed.

Mutants: /private/tmp/msr104/rep3/repo/.sdd/plan/task-1-mutants-3.log — caught 6, survived 0, invalid 0.
Revert: ran, exit 1, not loaded 1 (`bands.py` does not exist at BASE, so the test file cannot import it); every test,
the three new ones included, fails on the revert.

Files changed: `bands.py`, `tests/test_bands.py`, `.sdd/plan/task-1-mutants.md`, mutant patches 4-6.
