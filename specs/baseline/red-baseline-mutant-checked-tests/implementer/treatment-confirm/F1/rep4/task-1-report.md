# Task 1 report

Implemented `latest_report` in latest.py (glob `*.txt` files directly in folder, max by `date:` line value). Tests in tests/test_latest.py: plan test unchanged plus 3 added (name order vs date order, date line not first, non-.txt/nested ignored).

RED: `pytest -q tests/test_latest.py` -> ImportError: cannot import name 'latest_report' (expected, empty latest.py).
GREEN: full suite 4 passed, pristine.

Mutants: /private/tmp/mt-rep-qo4Sgc/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.

Files: latest.py, tests/test_latest.py (committed); .sdd/plan mutant files.
Concerns: none. Behavior with a report lacking a date: line raises ValueError (spec silent).
