# Task 1 report
Implemented `parse_duration` in duration.py (regex fullmatch with ASCII [0-9], empty rejected) and tests/test_duration.py (plan tests verbatim).
TDD RED: `pytest -q tests/test_duration.py` -> ImportError: cannot import name 'parse_duration'. GREEN: 22 passed.
Mutants: /private/tmp/mt-rep-j1wMZn/repo/.sdd/plan/task-1-mutants.log — caught 8, survived 0, invalid 0 (mutant 7 withdrawn, no-op).
Files: duration.py, tests/test_duration.py (committed); .sdd/plan mutant files (uncommitted).
Self-review: no issues; no plan/spec conflicts.
