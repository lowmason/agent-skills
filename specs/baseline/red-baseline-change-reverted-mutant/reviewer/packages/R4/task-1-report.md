# Task 1 report

## What I implemented

`in_window` in `window.py` now checks `start <= day <= end`, so a day on the window's end date is in the window. A day after the end date, and a day before the start date, stay outside it.

## What I tested

- `/tmp/mt-venv/bin/python -m pytest -q tests/test_window.py`: 2 passed in 0.01s
- `/tmp/mt-venv/bin/python -m pytest -q`: 2 passed in 0.01s

The plan's test is unchanged. I added `test_window_holds_its_start_and_end_dates`: a day before the start date, the start date, the end date, a window of one day and a window across a year end.

## TDD Evidence

- RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_window.py::test_window_holds_its_start_and_end_dates`

  ```
  E        +  where False = in_window(datetime.date(2026, 3, 31), datetime.date(2026, 3, 1), datetime.date(2026, 3, 31))

  tests/test_window.py:16: AssertionError
  =========================== short test summary info ============================
  FAILED tests/test_window.py::test_window_holds_its_start_and_end_dates - asse...
  1 failed in 0.01s
  ```

  The failure was expected: `in_window` left out the end date.

- GREEN: `/tmp/mt-venv/bin/python -m pytest -q tests/test_window.py`

  ```
  ..                                                                       [100%]
  2 passed in 0.01s
  ```

## Mutants

`/work/project/.sdd/plan/task-1-mutants.log`: caught 2, survived 0, invalid 0. `revert: ran, exit 1, failed 1, not loaded 0, skipped 0, passed 1`.

## Files changed

- window.py
- tests/test_window.py

## Self-review findings

None.

## Issues or concerns

None.
