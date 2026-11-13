# Task 1 report
Implemented `main` in checkconf.py (reads file, splits on first `=`, prints `unknown key: <key>` for keys not in name/port/debug, returns 1/0). Blank lines skipped.
Tests: 5 passed (plan test + 4 added: return 1, return 0 with known keys, multiple unknown keys, empty file).
TDD RED: `pytest -q tests/test_checkconf.py` -> ImportError: cannot import name 'main' from 'checkconf' (expected, file was empty). GREEN: 5 passed.
Mutants: /private/tmp/mt-rep-1ZbHLU/repo/.sdd/plan/task-1-mutants.log — caught 6, survived 0, invalid 0.
Files: checkconf.py, tests/test_checkconf.py (committed); .sdd/plan mutant files (uncommitted).
Concerns: none; no plan-test/spec conflict.
