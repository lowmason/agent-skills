# Task 1 report

Implemented `main(argv)` in `checkconf.py`: reads `argv[0]`, prints `unknown key: <key>` for each key not in name/port/debug, returns 1 if any, else 0 (blank lines skipped).
Tests (tests/test_checkconf.py): plan test unchanged, plus 4 added (return 1, return 0 with no output, several unknown keys in order, empty file). 5/5 pass.

## TDD Evidence
RED: `pytest -q tests/test_checkconf.py` -> ImportError: cannot import name 'main' from 'checkconf' (expected: file empty).
GREEN: same command -> 5 passed.

## Mutants
/private/tmp/mt-rep-DV5WCm/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0

## Files changed
checkconf.py, tests/test_checkconf.py (committed); .sdd/plan mutants files (uncommitted).

## Concerns
None. No plan-test/spec conflict (plan test doesn't assert the return value).
