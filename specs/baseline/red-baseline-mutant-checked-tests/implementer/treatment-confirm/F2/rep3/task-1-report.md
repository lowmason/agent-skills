# Task 1 report
Implemented `main` in checkconf.py (prints `unknown key: <key>` per unknown key, returns 1/0). Tests in tests/test_checkconf.py: plan test plus 4 added (return 1, known keys -> 0 and silent, multiple unknown keys, empty file).
## TDD
RED: `pytest -q tests/test_checkconf.py` -> ImportError: cannot import name 'main' from 'checkconf'.
GREEN: 5 passed.
## Mutants
/private/tmp/mt-rep-LgFZCD/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0
## Files
checkconf.py, tests/test_checkconf.py
## Concerns
None; plan test did not conflict with spec.
