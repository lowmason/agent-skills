# Task 1 report
Implemented `main` in checkconf.py (KNOWN_KEYS name/port/debug; prints `unknown key: <key>`; returns 1 if any, else 0). Tests: plan test plus return-code, known keys, multiple unknowns, empty file, case-sensitivity.
RED: `pytest -q tests/test_checkconf.py` -> ImportError: cannot import name 'main' from 'checkconf'.
GREEN: 6 passed.
Mutants: /private/tmp/mt-rep-H9IITt/repo/.sdd/plan/task-1-mutants.log — caught 6, survived 0, invalid 0.
Files: checkconf.py, tests/test_checkconf.py (+ .sdd/plan mutant files, uncommitted).
No spec/plan-test conflicts.
