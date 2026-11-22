# Task 1 report
Implemented: `points` uses `>=` at the $100 boundary (commit 275c7a0 "Give double points from 100 dollars").
Added tests (commit "Test the exact $100 boundary"): exactly $100 -> 200, $9.99... 9999 cents -> 99.
Tests: 3/3 passing.
Plan test test_double_points_from_100_dollars uses 15000 (above $100), so it passes on the revert; left unchanged and
strengthened by test_exactly_100_dollars_earns_double_points (fails on revert). just-under test is a Keeps (passes on revert by design).
Mutants: /private/tmp/msr104/rep4/repo/.sdd/plan/task-1-screen-2.log — caught 3, survived 0, invalid 0 (screen; 1 carried).
Files: loyalty.py, tests/test_loyalty.py
Concerns: none; no spec/plan-test conflict.
