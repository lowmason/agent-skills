# Task 1 report
Implemented: stock.py `level < threshold` -> `level <= threshold`. Added tests/test_stock.py: plan test (unchanged) plus test_reorder_exactly_at_threshold (5,5) and test_no_reorder_above_threshold (6,5).
Note: the plan test uses (2,5), which passed even before the fix; the new exactly-at-threshold test is the real regression test.
TDD RED: pytest -q tests/test_stock.py -> 1 failed (test_reorder_exactly_at_threshold: assert False is True), 2 passed. GREEN: 3 passed.
Commits: first commit accidentally had the tests only (sed failed on macOS); second commit has the fix.
Mutants: run .sdd/plan/task-1-mutants-2.log — caught 3, survived 0, invalid 0.
Files: stock.py, tests/test_stock.py, .sdd/plan/task-1-mutant-{1,2,3}.patch, task-1-mutants.md
No spec/plan-test conflict.
