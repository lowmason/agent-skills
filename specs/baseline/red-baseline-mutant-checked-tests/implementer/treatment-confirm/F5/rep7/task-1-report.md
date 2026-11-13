# Task 1 report

Implemented `parse_duration` in `duration.py` (regex fullmatch on `[0-9]+` h/m/s parts, empty text rejected, returns int seconds) and added the plan's tests in `tests/test_duration.py` unchanged.

## TDD Evidence
- RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_duration.py` -> collection error (ImportError: parse_duration missing from empty duration.py), as expected.
- GREEN: same command -> `22 passed`.

## Mutants
Run: /tmp/mt-rep-CgpZTI/repo/.sdd/plan/task-1-mutants.log — caught 9, survived 0, invalid 0 (mutant 10 withdrawn: no visible change).

## Files changed
duration.py, tests/test_duration.py, .sdd/plan/task-1-mutant-*.patch, task-1-mutants.md

## Self-review
No plan/spec conflicts found. No concerns.
