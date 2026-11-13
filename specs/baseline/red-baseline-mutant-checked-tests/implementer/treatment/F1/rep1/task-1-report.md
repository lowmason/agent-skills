# Task 1 report
Implemented `latest_report` in latest.py (glob *.txt files in folder, max by ISO date from `date:` line). Tests in tests/test_latest.py (6).
TDD RED: `pytest -q tests/test_latest.py` -> ImportError for latest_report. GREEN: full suite passed.
Mutants: last run /private/tmp/mt-rep-n7i5wl/repo/.sdd/plan/task-1-mutants-2.log — caught 5, survived 0, invalid 0. (First run: mutant 5 survived; added same-month test.)
Files: latest.py, tests/test_latest.py, .sdd/plan/task-1-mutant-*.patch, task-1-mutants.md.
Concerns: none. A report with no `date:` line raises ValueError (spec silent).
