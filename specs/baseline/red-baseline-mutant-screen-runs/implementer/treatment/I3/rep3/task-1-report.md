# Task 1 report

Implemented: `points` in loyalty.py now uses `cents >= DOUBLE_FROM_CENTS` (spec loyalty.md:9). Plan test test_double_points_from_100_dollars kept unchanged.

Tests: 2/2 passing at HEAD (`pytest -q tests/test_loyalty.py`).

Revert finding: the plan test uses 15000, so it passed on the revert (boundary bug not exercised). Added new test test_exactly_100_dollars_earns_double_points (points(10000) == 200), which fails on the revert. Mutants file has `Strengthened:` line. Mutant 2 (`>` boundary) aims at it.

Mutants: .sdd/plan/task-1-screen-2.log — caught 2, survived 0, invalid 0 (mutant 1 carried). Revert: plan test passes (strengthened), new test fails.

Files: loyalty.py, tests/test_loyalty.py.
Commits: 6eb114e Give double points from 100 dollars; "Test the exact 100 dollar boundary".
Concerns: none.
