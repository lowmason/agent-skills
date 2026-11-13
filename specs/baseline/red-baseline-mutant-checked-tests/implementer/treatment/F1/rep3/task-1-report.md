# Task 1 report
Implemented `latest_report` in latest.py (max over `*.txt` by `date:` line; ISO strings compare correctly). Raises ValueError if a report has no date line (unspecified by spec).
Tests: tests/test_latest.py — plan test plus 3 added (name order, date after other lines/year boundary, non-.txt and nested ignored). 4 passed.
TDD RED: `pytest -q tests/test_latest.py` -> ImportError: cannot import name 'latest_report'. GREEN: 4 passed.
Mutants: /private/tmp/mt-rep-9HPadp/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.
Files: latest.py, tests/test_latest.py, .sdd/plan mutant files (uncommitted).
No plan/spec conflicts.
