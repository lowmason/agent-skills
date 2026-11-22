# Task 1 report
Implemented: loyalty.py `points` uses `cents >= DOUBLE_FROM_CENTS` (commit 86386e4). Plan test test_double_points_from_100_dollars (15000 cents) left as written.
Added tests (follow-up commit): test_double_points_at_exactly_100_dollars (10000 -> 200), test_single_points_just_below_100_dollars (9999 -> 99).
Tests: 3/3 passing, output pristine.
Mutants: /private/tmp/msr104/rep5/repo/.sdd/plan/task-1-mutants.log — caught 3, survived 0, invalid 0.
Revert: the plan test passed on the revert (15000 is above the boundary), so it is Strengthened by test_double_points_at_exactly_100_dollars, which fails on the revert. The below-$100 test passes on the revert by design (Keeps line).
Files: loyalty.py, tests/test_loyalty.py, .sdd/plan/task-1-mutants.md, mutant patches.
Concerns: none (no plan/spec conflict).
