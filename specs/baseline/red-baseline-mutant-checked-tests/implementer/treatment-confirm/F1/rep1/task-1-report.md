# Task 1 report
Implemented `latest_report` in latest.py (max over *.txt regular files in folder, keyed by `date:` line; ISO strings compare chronologically). Tests: plan test unchanged plus 3 added (name order irrelevant, date line position, non-.txt/subfolder exclusion).
TDD RED: `pytest -q tests/test_latest.py` -> ImportError: cannot import name 'latest_report'. GREEN: 4 passed.
Mutants: /private/tmp/mt-rep-jdVs0f/repo/.sdd/plan/task-1-mutants.log — caught 6, survived 0, invalid 0.
Files: latest.py, tests/test_latest.py (committed); .sdd/plan mutant files (uncommitted).
Concerns: none. Reports with no `date:` line sort as earliest; folder with no reports raises ValueError (unspecified).
