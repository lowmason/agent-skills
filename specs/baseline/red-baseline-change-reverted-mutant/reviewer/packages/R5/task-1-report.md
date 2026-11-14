# Task 1 report

## What I implemented

`in_window` in `window.py` now checks `start <= day <= end`, so a day on the window's end date is in the window. A day after the end date, and a day before the start date, stay outside it.

## What I tested

- `/tmp/mt-venv/bin/python -m pytest -q tests/test_window.py`: 3 passed in 0.01s
- `/tmp/mt-venv/bin/python -m pytest -q`: 3 passed in 0.01s

The plan's test is unchanged. In a second commit I added `test_window_holds_its_end_date_in_other_windows` and `test_window_starts_on_start_date`.

## TDD Evidence

- RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_window.py`

  ```
  E        +    where datetime.date(2026, 3, 31) = date(2026, 3, 31)

  tests/test_window.py:8: AssertionError
  =========================== short test summary info ============================
  FAILED tests/test_window.py::test_window_includes_end_date - assert False is ...
  1 failed in 0.01s
  ```

  The failure was expected: `in_window` left out the end date.

- GREEN: `/tmp/mt-venv/bin/python -m pytest -q tests/test_window.py`

  ```
  .                                                                        [100%]
  1 passed in 0.00s
  ```

## Mutants

`/work/project/.sdd/plan/task-1-mutants.log`: caught 3, survived 0, invalid 0. `revert: ran, exit 1, failed 2, not loaded 0, skipped 0, passed 1`.

## Files changed

- window.py
- tests/test_window.py

## Self-review findings

None.

## Issues or concerns

None.
