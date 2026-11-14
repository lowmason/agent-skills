# Task 1 report

Implemented: `stock.py` `reorder_needed` now returns `level <= threshold` (specs/stock.md:7).
Tests (tests/test_stock.py): the plan test `test_reorder_at_threshold` as written, plus new `test_reorder_when_level_equals_threshold` (5,5) and `test_no_reorder_above_threshold` (6,5).

## TDD
RED: `pytest -q tests/test_stock.py` on old code: `1 failed, 2 passed` (`reorder_needed(5, 5)` -> False).
GREEN: same command after fix: `3 passed`.

## Mutants
Last run: /private/tmp/mt-rep-VUNBpy/repo/.sdd/plan/task-1-mutants-2.log — caught 3, survived 0, invalid 0.
Revert: failed 1 (equality test), passed 2. The plan test passes on the revert because (2,5) is below the threshold, not at it: Strengthened line names the equality test. The above-threshold test is a Keeps.

## Files changed
stock.py, tests/test_stock.py

## Concerns
- Plan test `test_reorder_at_threshold` uses (2, 5), which is below the threshold and does not exercise the boundary. It does not conflict with the spec; left unchanged and strengthened by a new test.
- Two commits share the subject "Fix reorder_needed at the threshold": the first commit missed the stock.py edit (a macOS sed slip), the second applied it.
