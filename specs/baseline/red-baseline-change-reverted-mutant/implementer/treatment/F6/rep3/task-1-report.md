# Task 1 report
Implemented: `reorder_needed` now returns `level <= threshold` (stock.py). Tests in tests/test_stock.py: the plan test plus two new ones (equal to threshold, above threshold).
Note: the plan test `reorder_needed(2, 5)` is below the threshold, not at it, so it passes on the old code; strengthened by test_reorder_when_level_equals_threshold. No conflict with specs/stock.md:7.
TDD: RED `pytest -q tests/test_stock.py` -> 1 failed (test_reorder_when_level_equals_threshold, assert on 5,5), 2 passed. GREEN after fix -> 3 passed.
Mutants: /private/tmp/mt-rep-Zc2Ub7/repo/.sdd/plan/task-1-mutants.log — caught 3, survived 0, invalid 0. Revert: failed 1 (equality test), passed 2 (plan test -> Strengthened line; above-threshold -> Keeps line).
Commits: 8bc292c (tests; accidentally committed before the fix, a sed failure), then the fix commit "Make reorder_needed true at the threshold".
Files: stock.py, tests/test_stock.py
