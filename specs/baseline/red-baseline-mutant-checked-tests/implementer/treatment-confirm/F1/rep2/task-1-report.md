# Task 1 report
Implemented `latest_report` in latest.py (glob *.txt files in folder, max by ISO date from `date:` line; ValueError if none).
Tests: tests/test_latest.py — plan test plus 3 added (name order irrelevant, date line position/year boundary, only direct .txt files). 4/4 pass.
TDD: RED = ImportError for latest_report (collection error); GREEN = 4 passed.
Mutants: .sdd/plan/task-1-mutants-2.log — caught 4, survived 0, invalid 0.
Files: latest.py, tests/test_latest.py, .sdd/plan/task-1-mutant-*.patch, task-1-mutants.md
Concerns: none. Commit contains only latest.py and tests (.sdd files uncommitted).
