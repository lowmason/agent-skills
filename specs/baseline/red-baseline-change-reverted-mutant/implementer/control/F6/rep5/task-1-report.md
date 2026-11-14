# Task 1 report
Implemented: `reorder_needed` now returns `level <= threshold` (stock.py). Added tests/test_stock.py: the plan test (unchanged) plus two new tests (equality boundary, above threshold).
Note: the plan test (2, 5) passes even on the buggy code, so it does not pin the boundary; test_reorder_when_level_equals_threshold does.
TDD RED: `pytest -q tests/test_stock.py` on buggy code -> 1 failed (test_reorder_when_level_equals_threshold), 2 passed. GREEN: after fix -> 3 passed.
Commits: 482e4e8 (tests + unfixed code, committed by mistake as the sed failed), 0817edf (the actual fix).
Mutants: .sdd/plan/task-1-mutants.log — caught 3, survived 0, invalid 0.
Files: stock.py, tests/test_stock.py, .sdd/plan/task-1-mutant-{1,2,3}.patch, task-1-mutants.md (patches/notes not committed).
