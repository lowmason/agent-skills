# Task 1 report

Implemented `parse_duration` in `duration.py` (regex `fullmatch` with ASCII `[0-9]`, empty text rejected, ValueError otherwise) and the plan's tests verbatim in `tests/test_duration.py`.

## TDD
- RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_duration.py` -> ImportError: cannot import name 'parse_duration' (collection error), expected as duration.py was empty.
- GREEN: same command -> 22 passed.

## Mutants
Last run: .sdd/plan/task-1-mutants-2.log — caught 6, survived 0, invalid 0. (First run had 6 invalid due to empty patches from a BSD sed mistake; patches remade.)

## Files changed
duration.py, tests/test_duration.py (committed); .sdd/plan mutants files (uncommitted).

## Self-review
No issues; no plan/spec conflicts.
