# Task 1 report
Implemented: `stock.py` now `return level <= threshold`. Tests in tests/test_stock.py: plan test unchanged, plus three new (equals threshold, above threshold, zero/zero).
RED: with the old `<`, `pytest -q tests/test_stock.py` -> 2 failed, 2 passed (equals-threshold and zero tests failed: `assert False is True`).
GREEN: after fix, 4 passed.
Note: the plan test `reorder_needed(2, 5)` is below the threshold, so it passes on the old code too; it does not cover the boundary. No spec conflict. Strengthened by test_reorder_when_level_equals_threshold.
Mutants: .sdd/plan/task-1-mutants-2.log — caught 4, survived 0, invalid 0. Revert: failed 2 (equals, zero), passed 2 (plan test -> Strengthened line; above-threshold -> Keeps line).
Files: stock.py, tests/test_stock.py (commit e60bce3); .sdd/plan mutant files uncommitted.
