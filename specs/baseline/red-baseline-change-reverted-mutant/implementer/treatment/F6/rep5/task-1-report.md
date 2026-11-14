# Task 1 report
Implemented: `reorder_needed` now returns `level <= threshold` (stock.py).
Tests: tests/test_stock.py — plan test kept verbatim, plus three added (equal threshold, zero/zero, above threshold). 4 passed.
TDD: RED — before fix, 2 failed (test_reorder_when_level_equals_threshold, ..._zero_threshold: `assert False is True`). GREEN — 4 passed after fix.
Note: the plan test (2, 5) is below the threshold and passes on the old code, so it does not catch the bug; strengthened by test_reorder_when_level_equals_threshold (Strengthened line). No spec conflict.
Mutants: /tmp/mt-rep-gY4eFC/repo/.sdd/plan/task-1-mutants.log — caught 3, survived 0, invalid 0. Revert: failed 2 (the equality tests), passed 2 (plan test -> Strengthened; above-threshold -> Keeps).
Commits: b87ddd2 (tests, RED state, committed before fix by mistake — sed -i failed on macOS), then the fix commit.
Files: stock.py, tests/test_stock.py
