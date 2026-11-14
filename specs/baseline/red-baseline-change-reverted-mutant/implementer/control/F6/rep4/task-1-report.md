# Task 1 report

Implemented: `stock.py` now uses `level <= threshold` (specs/stock.md:7). Added tests/test_stock.py: the plan test unchanged plus equality, above-threshold and zero-boundary tests.

Plan test `reorder_needed(2, 5)` is a below-threshold case, not equality; it does not conflict with the spec. The equality shape is covered by a new test.

RED: `pytest -q tests/test_stock.py` against the old code (`<`): 2 failed, 2 passed (equality and zero-boundary tests failed), as expected.
GREEN: after the fix: 4 passed.

Mutants: /tmp/mt-rep-c5pGCd/repo/.sdd/plan/task-1-mutants-2.log — caught 4, survived 0, invalid 0. (The script's revert check fails on the base code, as expected.)

Files: stock.py, tests/test_stock.py. Commit was amended once locally to include the fix (the first attempt had a failed sed).
