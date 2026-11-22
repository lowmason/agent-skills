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

## Fix round 4: a weight at a medium band's upper edge

Finding: the Inputs table had no row for *a weight at a band's upper edge* of specs/bands.md:9, and no test used it.

- Added the row to `.sdd/plan/task-1-mutants.md` and the test `test_band_medium_at_its_upper_edge` (`band(2000) == 'medium'`).
- RED: `pytest -q tests` gave `1 failed, 4 passed`. `band(2000)` returned `large`, because `is_large` used `>=`. The input had never been tried, so the code was wrong against specs/bands.md:9 ("2000 included").
- Fix: `is_large` in `bands.py` now uses `grams > MEDIUM_LIMIT`.
- GREEN: `pytest -q tests`: 5 passed.
- Commit: "Fix a medium parcel at its upper edge", trailer `Mutant-step: task 1 review`.
- Mutant 4 (`task-1-mutant-4.patch`): `>` back to `>=` in `is_large`, so 2000 grams is large. Aimed at `test_band_medium_at_its_upper_edge`.
- Mutants: /private/tmp/msr104/rep3/repo/.sdd/plan/task-1-screen-3.log — caught 4 (3 carried, 1 run), survived 0, invalid 0
- Revert: `not loaded 1` (the revert removes `bands.py`, so every test in the file fails on it, the new test included).

Files changed: `bands.py`, `tests/test_bands.py`.
