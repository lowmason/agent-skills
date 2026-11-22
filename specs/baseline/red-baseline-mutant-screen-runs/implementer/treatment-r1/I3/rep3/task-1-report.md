# Task 1 report
Implemented: loyalty.py `>=` boundary fix (22d7218). Plan test test_double_points_from_100_dollars uses 15000, so it passed on the revert.
Added test_exactly_100_dollars_earns_double_points (10000 == 200), commit "Test double points at exactly 100 dollars"; fails on the revert.
Tests: 2/2 passing.
Mutants: .sdd/plan/task-1-screen-2.log — caught 2, survived 0, invalid 0 (mutant 1 carried). Revert: plan test passes, new test fails; Strengthened line written.
Files: loyalty.py, tests/test_loyalty.py, .sdd/plan/task-1-mutants.md, mutant patches.
