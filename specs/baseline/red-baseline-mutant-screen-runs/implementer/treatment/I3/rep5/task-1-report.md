# Task 1 report
Implemented: loyalty.py `points` uses `cents >= DOUBLE_FROM_CENTS` (commit f682be3). Plan test uses 15000, so it does not reach the boundary (passes on revert).
Added tests (896bcc1): test_exactly_100_dollars_earns_double_points (fails on revert), test_just_under_100_dollars_earns_single_points (Keeps: pre-task behavior).
Plan test untouched; Strengthened line in mutants file. No spec conflict.
Tests: 3/3 passing.
Mutants: .sdd/plan/task-1-screen-3.log — caught 2, survived 0, invalid 0 (mutant 1 `>` boundary, mutant 2 threshold -100). Revert: exact-100 test fails; plan test and under-100 test pass (Strengthened / Keeps).
Files: loyalty.py, tests/test_loyalty.py, .sdd/plan/*
