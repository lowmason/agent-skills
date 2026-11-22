# Task 1 report
Implemented: `points` uses `>=` at DOUBLE_FROM_CENTS (commit 25ed77e). Plan test uses 15000, so it passes on the revert (bug only at exactly 10000).
Added tests (new, plan test untouched): test_exactly_100_dollars_earns_double_points (10000->200; fails on revert), test_just_below_100_dollars_earns_single_points (9999->99; Keeps line).
Tests: 3/3 passing.
Mutants: /private/tmp/msr104/rep1/repo/.sdd/plan/task-1-screen-2.log — caught 3, survived 0, invalid 0 (1 carried). Revert: failed 1, passed 2 (plan test: Strengthened; just-below: Keeps).
Files: loyalty.py, tests/test_loyalty.py, .sdd/plan/task-1-mutant-{1,2,3}.patch, task-1-mutants.md
Concerns: none; no spec/plan-test conflict.
