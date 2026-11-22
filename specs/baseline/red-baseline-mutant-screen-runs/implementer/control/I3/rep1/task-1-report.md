# Task 1 report
- Implemented: `points` in loyalty.py uses `>=` so exactly $100 earns double points (commit f5c98d3).
- Tests: 3/3 pass, output pristine.
- Finding: the plan test uses 15000 and passes on the revert (does not test the boundary). Left unchanged; added
  test_exactly_100_dollars_earns_double_points (fails on revert) and test_just_under_100_dollars_earns_single_points (Keeps).
- Mutants: run .sdd/plan/task-1-mutants.log — caught 3, survived 0, invalid 0. Revert: failed 1 (exact-$100 test), passed 2 (plan test -> Strengthened; just-under -> Keeps).
- Files: loyalty.py, tests/test_loyalty.py, .sdd/plan/task-1-mutants.md, mutant patches.
- No spec/plan-test conflict.
