# Task 1 report
Implemented `main` in checkconf.py (known keys name/port/debug; prints `unknown key: <key>`; returns 1/0; blank lines skipped). Added 4 tests beyond the plan test (return codes, known keys, multiple keys, empty file).
TDD RED: `pytest -q tests/test_checkconf.py` -> ImportError: cannot import name 'main'.
GREEN: 5 passed.
Mutants: /private/tmp/mt-rep-fmk0hZ/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.
Files: checkconf.py, tests/test_checkconf.py (committed); mutant files in .sdd/plan (uncommitted).
No plan/spec conflicts.
