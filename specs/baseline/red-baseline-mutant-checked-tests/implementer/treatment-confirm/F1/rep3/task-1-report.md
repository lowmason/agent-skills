# Task 1 report
Implemented `latest_report` in latest.py (glob *.txt files in folder, max by ISO date from `date:` line). Added tests/test_latest.py: the plan test plus 4 added tests (name order irrelevant, cross-year dates, date line position, non-.txt/subdir ignored).
TDD RED: `pytest -q tests/test_latest.py` -> ImportError: cannot import name 'latest_report'. GREEN: 5 passed.
Mutants: .sdd/plan/task-1-mutants-2.log — caught 5, survived 0, invalid 0 (first run invalid from my BSD sed error; patches remade).
Files: latest.py, tests/test_latest.py, .sdd/plan/task-1-mutant-*.patch, task-1-mutants.md
Concerns: none. Reports with no `date:` line raise ValueError (spec silent).
