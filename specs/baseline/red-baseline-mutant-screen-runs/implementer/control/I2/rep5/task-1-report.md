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

- Mutants: /private/tmp/msr104/rep5/repo/.sdd/plan/task-1-screen-2.log — caught 3, survived 0, invalid 0
- The script's first run left mutant 1 (a weight of 500 grams is medium) alive, so I added
  `test_band_small_at_its_upper_edge` and ran the script again.

## Files changed

- `bands.py` (created)
- `tests/test_bands.py` (created)

## Self-review

No findings.

## Concerns

None.

## Fix round 4: upper edge of the medium band

Finding: no Inputs row and no test for a weight at a band's upper edge of `specs/bands.md:9`.

- Added `test_band_medium_at_its_upper_edge` (`band(2000) == 'medium'`) and `test_band_large_just_above_medium_edge`
  (`band(2001) == 'large'`). The first failed at once: `band(2000)` returned `large`, because `is_large` used
  `>=`. That was a real bug against specs/bands.md:9 ("2000 included"). Fixed in `bands.py` (`>` instead of `>=`).
- Tests: `/private/tmp/msr104-venv/bin/python -m pytest -q`: 6 passed, output pristine.
- Mutants: /private/tmp/msr104/rep5/repo/.sdd/plan/task-1-mutants-2.log — caught 5, survived 0, invalid 0
  (new: mutant 4, 2000 is large; mutant 5, 2001 is medium). Inputs table updated in task-1-mutants.md.
- Revert: `not loaded 1` — tests.test_bands cannot load on the revert (no `bands`), so every test in it fails there.
- Commit: "Make a weight of 2000 grams medium".
