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

## Fix round 4: after review findings

Finding: the Inputs table had no row for a weight at a medium band's upper edge (`specs/bands.md:9`), and no test used it.

- Added row `specs/bands.md:9 | a weight at the band's upper edge | test_band_medium_at_its_upper_edge` to the Inputs table.
- Added `test_band_medium_at_its_upper_edge` (`band(2000) == 'medium'`). RED: it failed (`1 failed, 4 passed`), because `is_large` used `>=`, so 2000 was large. That was a real bug.
- Fixed `bands.py`: `is_large` now uses `grams > MEDIUM_LIMIT`. GREEN: `tests/test_bands.py` 5 passed; full suite 5 passed.
- Mutant 4 (`specs/bands.md:9`, the new test): `>` back to `>=` in `is_large`.
- Revert: the new test is "not loaded" on the revert (no `bands.py` at BASE), so it fails there.
- Commit: "Keep a weight of 2000 grams medium", with trailer `Mutant-step: task 1 review`.

Mutants: /private/tmp/msr104/rep2/repo/.sdd/plan/task-1-screen-3.log — caught 4, survived 0, invalid 0 (3 carried)

Files changed: `bands.py`, `tests/test_bands.py`.
