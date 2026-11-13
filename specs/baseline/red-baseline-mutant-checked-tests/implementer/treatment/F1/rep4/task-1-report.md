# Task 1 report
Implemented `latest_report` in latest.py (max by parsed ISO `date:` line over `*.txt` files directly in folder). Tests: tests/test_latest.py (plan test + 4 added for no-name-order, date-line position, cross-year, txt/nesting/dir filtering).
TDD: RED `pytest -q tests/test_latest.py` -> ImportError for latest_report. GREEN: 5 passed.
Mutants: /private/tmp/mt-rep-iFUrP1/repo/.sdd/plan/task-1-mutants.log — caught 6, survived 0, invalid 0.
Files: latest.py, tests/test_latest.py, .sdd/plan/task-1-mutants.md + patches.
Concerns: none. A report with no/invalid date line raises ValueError (spec silent).
