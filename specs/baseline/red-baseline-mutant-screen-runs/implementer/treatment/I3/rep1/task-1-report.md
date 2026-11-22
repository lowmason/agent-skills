# Task 1 report
Implemented: `points` now uses `cents >= DOUBLE_FROM_CENTS` (commit b7c6a18). Plan test uses 15000, which does not touch the boundary and passes on the revert.
Added (commit 279bc34): test_exactly_100_dollars_earns_double_points (points(10000)==200; fails on revert, 100 == 200) and test_just_under_100_dollars_earns_single_points (points(9999)==99; Keeps line).
Plan test left unchanged; Strengthened line in mutants file.
Tests: 3/3 passing, pristine.
Mutants: .sdd/plan/task-1-screen-2.log — caught 3, survived 0, invalid 0 (mutant 1 carried). Revert: plan test passed (strengthened by new test), exact-100 failed, just-under passed (Keeps).
Files changed: loyalty.py, tests/test_loyalty.py
Concerns: none. Plan test as written does not cover the boundary; the spec and plan do not conflict.
