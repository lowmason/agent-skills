# Task 1 report
Implemented: loyalty.py `points` uses `>=` at the $100 threshold (commit 6a8e84b). Plan test uses 15000, which passed on the revert, so I added test_exactly_100_dollars_earns_double_points (10000 -> 200) and test_just_under_100_dollars_earns_single_points (9999 -> 99) in a new commit; the plan test is unchanged.
Tests: 3/3 passing, output pristine.
Mutants: .sdd/plan/task-1-screen-2.log — caught 2, survived 0, invalid 0 (mutant 1 carried).
Revert: exact-100 test fails on revert; plan test is covered by a Strengthened: line; under-100 test has a Keeps: line.
Files: loyalty.py, tests/test_loyalty.py, .sdd/plan/task-1-mutants.md, mutant patches.
