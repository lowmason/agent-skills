# Task 1 report

Implemented `parse_duration` in `duration.py` (regex `fullmatch` with ASCII `[0-9]`, explicit empty check) and added `tests/test_duration.py` exactly as the plan gives.

## TDD
- RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_duration.py` -> `ImportError: cannot import name 'parse_duration' from 'duration'` (function not yet written).
- GREEN: same command -> 22 passed; full suite 22 passed, output pristine.

## Mutants
Run: /private/tmp/mt-rep-6KH4a6/repo/.sdd/plan/task-1-mutants.log — caught 7, survived 0, invalid 0.

## Files changed
duration.py, tests/test_duration.py (committed); .sdd/plan mutant patches and mutants file.

## Self-review
No plan/spec conflicts. No extra tests were needed: all input shapes are covered.
