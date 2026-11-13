# Task 1 report
Implemented `main` in checkconf.py (KNOWN_KEYS name/port/debug; prints `unknown key: <key>` per unknown key; returns 1/0). Tests in tests/test_checkconf.py: the plan test unchanged plus 4 added (return 1, return 0 + silent, several/repeated keys in order, empty file).
## TDD
RED: `pytest -q tests/test_checkconf.py` -> ImportError: cannot import name 'main' from 'checkconf'.
GREEN: 5 passed.
## Mutants
Run: /private/tmp/mt-rep-LiJqlu/repo/.sdd/plan/task-1-mutants-2.log — caught 5, survived 0, invalid 0 (first run was invalid 5 from my BSD-sed patch errors; patches rebuilt).
## Files
checkconf.py, tests/test_checkconf.py (+ .sdd/plan mutant files, uncommitted)
## Concerns
None. No plan/spec conflict.
