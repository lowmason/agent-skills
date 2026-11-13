# Task 1 report

Implemented `parse_duration` in `duration.py` (regex `fullmatch` with ASCII `[0-9]` parts h/m/s in order, empty text rejected, ValueError otherwise). Tests in `tests/test_duration.py` are the plan's, verbatim.

## TDD Evidence
- RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_duration.py` -> `ImportError: cannot import name 'parse_duration' from 'duration'` (function not yet written).
- GREEN: same command -> `22 passed`.

## Mutants
Run: /private/tmp/mt-rep-RaSNWZ/repo/.sdd/plan/task-1-mutants.log — caught 7, survived 0, invalid 0.

## Files changed
duration.py, tests/test_duration.py (commit 38401b3); .sdd/plan mutant files (uncommitted).

## Self-review
No issues; no plan test/spec conflict found.
