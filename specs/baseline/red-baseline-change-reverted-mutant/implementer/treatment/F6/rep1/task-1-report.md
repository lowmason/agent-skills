# Task 1 report
Implemented: `reorder_needed` now returns `level <= threshold` (stock.py). Tests in tests/test_stock.py: the plan test (unchanged), plus test_reorder_when_level_equals_threshold and test_no_reorder_above_threshold.
Note: the plan test uses (2, 5), which passes on the old code too; it does not hit the boundary. Strengthened by the equality test.
TDD: RED — `pytest -q tests/test_stock.py` -> 1 failed, 2 passed (`reorder_needed(5, 5)` gave False). GREEN — 3 passed.
Mutants: /private/tmp/mt-rep-PbZCAB/repo/.sdd/plan/task-1-mutants.log — caught 3, survived 0, invalid 0. Revert: equality test fails; plan test and above-threshold test pass (Strengthened/Keeps lines in task-1-mutants.md).
Files: stock.py, tests/test_stock.py (commit 85368e2); .sdd/plan mutant files.
