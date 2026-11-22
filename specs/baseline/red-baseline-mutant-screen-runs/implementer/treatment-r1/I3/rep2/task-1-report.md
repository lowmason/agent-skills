# Task 1 report
Implemented: `points` uses `>=` at $100 (47d707c). Plan test test_double_points_from_100_dollars uses 15000, so it passes on the revert.
Added (commit "Test the exact $100 boundary and just under it"): test_exactly_100_dollars_earns_double_points (fails on revert; Strengthened line) and test_just_under_100_dollars_earns_single_points (Keeps line, passes on revert by design).
Tests: 3/3 passing, output pristine.
Mutants: .sdd/plan/task-1-screen-2.log — caught 3, survived 0, invalid 0 (mutant 1 carried). Revert: failed 1, passed 2 (plan test: Strengthened; just-under: Keeps).
Files: loyalty.py, tests/test_loyalty.py, .sdd/plan/task-1-mutant-{1,2,3}.patch, task-1-mutants.md
Concerns: none.
