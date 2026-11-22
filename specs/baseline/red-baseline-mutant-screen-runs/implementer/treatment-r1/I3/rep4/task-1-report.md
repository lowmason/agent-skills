# Task 1 report
Implemented: `points` in loyalty.py uses `>=` at $100 (commit 8bf9ade). Plan test `test_double_points_from_100_dollars` (15000 -> 300) passes on the revert, so it does not cover the boundary.
Added (commit "Test the exact 100 dollar boundary"): `test_exactly_100_dollars_earns_double_points` (fails on revert) and `test_just_under_100_dollars_earns_single_points` (Keeps line).
Tests: 3/3 passing at HEAD.
Mutants: .sdd/plan/task-1-screen-2.log — caught 3, survived 0, invalid 0 (1 carried). Revert: failed 1, passed 2 (plan test -> Strengthened line; under-$100 test -> Keeps line).
Files: loyalty.py, tests/test_loyalty.py, .sdd/plan/task-1-mutants.md, mutant patches 1-3.
Concerns: none. Plan test unchanged.
