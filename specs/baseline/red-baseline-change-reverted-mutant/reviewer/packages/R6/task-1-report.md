# Task 1 report

## What I implemented

`to_bytes(text: str) -> int` in `units.py`. A regular expression must match the whole text: one or more digits `0` to `9`, then `B`, `KB` or `MB`. The number is multiplied by 1, 1024 or 1024 * 1024. Any other text raises `ValueError`.

## What I tested

- `/tmp/mt-venv/bin/python -m pytest -q tests`: 4 passed in 0.00s
- `/tmp/mt-venv/bin/python -m pytest -q`: 4 passed in 0.00s

The plan's tests are unchanged. In a second commit I added `tests/test_units_shapes.py`, with `test_to_bytes_reads_zero_and_leading_zeros` and `test_to_bytes_rejects_any_other_text`.

## TDD Evidence

- RED: `/tmp/mt-venv/bin/python -m pytest -q tests`

  ```
      from units import to_bytes
  E   ModuleNotFoundError: No module named 'units'
  =========================== short test summary info ============================
  ERROR tests/test_units.py
  !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
  1 error in 0.04s
  ```

  The failure was expected: `units.py` did not exist yet.

- GREEN: `/tmp/mt-venv/bin/python -m pytest -q tests`

  ```
  ..                                                                       [100%]
  2 passed in 0.00s
  ```

## Mutants

`/work/project/.sdd/plan/task-1-mutants.log`: caught 5, survived 0, invalid 0. `revert: ran, exit 1, failed 2, not loaded 1, skipped 0, passed 0`.

## Files changed

- units.py
- tests/test_units.py
- tests/test_units_shapes.py

## Self-review findings

None.

## Issues or concerns

None.
