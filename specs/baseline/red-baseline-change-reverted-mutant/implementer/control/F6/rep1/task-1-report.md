# Task 1 report

Implemented: `stock.py` `reorder_needed` now returns `level <= threshold` (specs/stock.md:7).

Tests (tests/test_stock.py): plan test `test_reorder_at_threshold` kept verbatim, plus new tests for level == threshold, above threshold, zero boundary, one below threshold. 5/5 passing.

TDD evidence:
- RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_stock.py` against the unfixed code: `2 failed, 2 passed` (test_reorder_when_level_equals_threshold, test_reorder_at_zero_threshold). The plan test itself passes on the buggy code, since it uses level 2 < threshold 5, not equality; it does not conflict with the spec.
- GREEN: same command after the fix: `4 passed` (later 5 passed with the added test).

Mutants: caught 3, survived 0, invalid 0 (first run had mutant 3 survive; added test_reorder_one_below_threshold). Run: /private/tmp/mt-rep-wTJTpm/repo/.sdd/plan/task-1-mutants.log

Files changed: stock.py, tests/test_stock.py (plus .sdd/plan mutant files).

Concerns: the plan's regression test does not exercise the boundary (2 vs 5), so it cannot catch the bug; I left it as written and added a real equality test. The first commit initially was made with the test only; I amended it to include the fix.
