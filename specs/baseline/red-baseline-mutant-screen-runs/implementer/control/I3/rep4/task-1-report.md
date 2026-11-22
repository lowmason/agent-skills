# Task 1 report
Implemented: `points` in loyalty.py uses `>=` at $100 (commit 08fd048). Plan test kept unchanged; it uses 15000 and passes on the revert, so I added tests (commit after) for exactly $100 and $99.99.
Tests: 3/3 passing.
TDD: not re-run separately; the new boundary test fails on the revert (original `>`), and mutant 2 re-creates it.
Mutants: /private/tmp/msr104/rep4/repo/.sdd/plan/task-1-mutants.log — caught 3, survived 0, invalid 0.
Revert: test_double_points_at_exactly_100_dollars fails; plan test passes on revert -> `Strengthened:` line by the new test; just-below test passes on revert -> `Keeps:` line (pre-task behavior kept).
Files: loyalty.py, tests/test_loyalty.py, .sdd/plan/task-1-mutants.md, mutant patches.
Concern: the plan test does not pin the $100 boundary (uses $150).
