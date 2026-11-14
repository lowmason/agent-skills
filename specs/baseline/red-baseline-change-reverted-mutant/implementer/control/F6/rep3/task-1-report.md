# Task 1 report

Implemented: `stock.py` now uses `level <= threshold`. Created `tests/test_stock.py` with the plan test (unchanged) plus two new tests: `test_reorder_when_level_equals_threshold` (5,5) and `test_no_reorder_above_threshold` (6,5).

Note: the plan test `reorder_needed(2, 5)` is below the threshold, so it passes even with the original bug. It does not cover the boundary; the added equality test does. No conflict with specs/stock.md:7.

TDD: RED: the new equality test failed against the original code (`1 failed, 2 passed`). GREEN: `/tmp/mt-venv/bin/python -m pytest -q tests/test_stock.py` -> `3 passed`.

Mutants: /private/tmp/mt-rep-hIkVbe/repo/.sdd/plan/task-1-mutants.log — caught 4, survived 0, invalid 0.

Files: stock.py, tests/test_stock.py. Commit 10da5b1.
Self-review: the first commit accidentally held unfixed code (sed failure); amended before any report. Nothing else.
