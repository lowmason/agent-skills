# Task 1 report

Implemented `parse_duration` in `duration.py` (regex with `fullmatch`, ASCII `[0-9]`, empty text rejected) and plan tests in `tests/test_duration.py`, unchanged from the plan.

## TDD Evidence
- RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_duration.py` -> ImportError: cannot import name 'parse_duration' (expected: not yet written).
- GREEN: same command -> 22 passed.

Mutants: /private/tmp/mt-rep-2R1tdb/repo/.sdd/plan/task-1-mutants-3.log — caught 8, survived 0, invalid 0 (mutant 1 was rebuilt after an empty first patch).

Files changed: duration.py, tests/test_duration.py (committed df6dcf3); .sdd/plan mutant files (uncommitted).

Self-review: no spec/plan-test conflicts; no extra tests needed, all input shapes covered.
