# Task 1 report
Implemented: `points` in loyalty.py uses `>=` so exactly $100 earns double points (ca2053a). Plan test kept unchanged.
Added tests (commit "Test the 100 dollar boundary directly"): test_exactly_100_dollars_earns_double_points (10000 -> 200), test_just_under_100_dollars_earns_single_points (9999 -> 99).
Why: the plan test uses 15000, so it passes on the revert (BASE code); the exact-$100 test fails on the revert and is named in a `Strengthened:` line. Under-$100 test passes on the revert by design (`Keeps:` line).
Tests: 3/3 passing.
Mutants: .sdd/plan/task-1-mutants.log — caught 3, survived 0, invalid 0. Revert: failed 1 (exact $100), passed 2 (plan test, under-$100 Keeps).
Files: loyalty.py, tests/test_loyalty.py, .sdd/plan/task-1-mutants.md + patches.
Concerns: plan test does not exercise the boundary itself (15000 passes on old code).
