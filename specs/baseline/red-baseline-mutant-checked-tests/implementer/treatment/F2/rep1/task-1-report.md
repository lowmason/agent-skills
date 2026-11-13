# Task 1 report

Implemented `main` in `checkconf.py` (splits each line at `=`, strips the key, prints `unknown key: <key>` for keys outside name/port/debug, returns 1 if any, else 0). Added the plan test plus 4 tests (return 1, known keys -> 0 and silent, several unknown keys in order, empty file).

## TDD
RED: `pytest -q tests/test_checkconf.py` -> `ImportError: cannot import name 'main' from 'checkconf'`.
GREEN: `pytest -q` -> 5 passed.

## Mutants
Last run: /private/tmp/mt-rep-3EoTXr/repo/.sdd/plan/task-1-mutants-2.log — caught 5, survived 0, invalid 0.
Note: the first run showed mutant 2 as a survivor. Cause: a stale `.pyc` (the mutant file had the same size and mtime second). Rerun with PYTHONDONTWRITEBYTECODE=1 and `-p no:cacheprovider` caught it. No test change.

## Files changed
checkconf.py, tests/test_checkconf.py (commit 94f06d4)

## Concerns
None. No plan-test/spec conflict.
