# Task 1 report
Implemented `latest_report` in latest.py (glob *.txt files directly in folder, parse `date:` line as ISO date, max by date). 
Tests: plan test + 3 added (name order opposite to date order; date line not first / month-year compare; non-.txt and subdir ignored). 4/4 passing.
TDD RED: pytest -> ImportError cannot import name 'latest_report'. GREEN: 4 passed.
Mutants: /private/tmp/mt-rep-bVUHPU/repo/.sdd/plan/task-1-mutants-2.log — caught 6, survived 0, invalid 0
Files: latest.py, tests/test_latest.py, .sdd/plan/task-1-mutant-*.patch, task-1-mutants.md
Note: plan test alone has name order == date order, so it can't catch name-based picking; added test_file_names_carry_no_order (strengthening only).
