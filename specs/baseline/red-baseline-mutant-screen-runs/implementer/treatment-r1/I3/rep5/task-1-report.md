# Task 1 report
- Implemented: `points` uses `>=` at $100 (commit f242db8). Added boundary tests (exactly $100, $9999 cents) since the plan test uses 15000 and passes on the revert.
- Tests: 3/3 passing, output pristine.
- Mutants: .sdd/plan/task-1-screen-2.log — caught 3, survived 0, invalid 0 (1 carried).
- Revert: plan test passes on revert (Strengthened by test_exactly_100_dollars_earns_double_points, which fails on revert); just-under test passes on revert by design (Keeps line).
- Files: loyalty.py, tests/test_loyalty.py, .sdd/plan/task-1-mutants.md, mutant patches 1-3.
- Concerns: none. The plan test is unchanged.
