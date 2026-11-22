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

Finding: no row or test for a weight at the medium band's upper edge (`specs/bands.md:9`).

The gap hid a real bug: `is_large` used `>=`, so `band(2000)` returned `large`; the spec says 2000 is medium.

- RED: new `test_band_medium_at_its_upper_edge` failed (`- medium` / `+ large`), 1 failed, 6 passed.
- Fix: `is_large` now uses `grams > MEDIUM_LIMIT` in `bands.py`.
- GREEN: `pytest -q`: 7 passed, output pristine.
- Also added the neighbouring edge tests `test_band_medium_just_above_small` (501) and `test_band_large_just_above_medium` (2001), and the rows for all three in `task-1-mutants.md`.
- Mutants 4-6 added (2000 large, 501 small, 2001 medium).
- Mutants: /private/tmp/msr104/rep1/repo/.sdd/plan/task-1-mutants-2.log — caught 6, survived 0, invalid 0
- Revert: bands.py did not exist at BASE, so the test file cannot load (not loaded 1): every test fails on the revert.
- Commit: "Count 2000 grams as medium".
- Files changed: `bands.py`, `tests/test_bands.py`.
