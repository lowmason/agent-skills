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

## Fix round 1

- Finding: the Inputs table had no row for the shape a weight at a band's upper edge of rule `specs/bands.md:9`,
  and no test used it.
- Change: I added the row and `test_band_medium_at_its_upper_edge` (`band(2000) == 'medium'`). The test failed,
  because `is_large` counted 2000 grams as large, so I fixed `is_large`. Mutant 4 (a weight of 2000 grams is
  large) aims at the test.
- Covering tests: `/private/tmp/msr104-venv/bin/python -m pytest -q tests/test_bands.py`: 5 passed.
- Documented suite: `/private/tmp/msr104-venv/bin/python -m pytest -q`: 5 passed.
- Mutants: /private/tmp/msr104/rep1/repo/.sdd/plan/task-1-screen-3.log — caught 4, survived 0, invalid 0
