# Task 1 report
Implemented: loyalty.py `>` -> `>=` (commit dad230a), plan test test_double_points_from_100_dollars (points(15000)==300).
Finding: the plan test uses 15000, so it passes on the revert (does not test the $100 boundary). Left unchanged; added new tests
test_exactly_100_dollars_earns_double_points (points(10000)==200, fails on revert) and test_just_under_100_dollars_earns_single_points (points(9999)==99, Keeps line).
Tests: 3/3 passing, output pristine.
Mutants: /private/tmp/msr104/rep3/repo/.sdd/plan/task-1-mutants-2.log — caught 3, survived 0, invalid 0. Revert: plan test passed (Strengthened line), exactly-100 test failed, just-under passed (Keeps).
Files: loyalty.py, tests/test_loyalty.py; .sdd/plan mutants files.
Concerns: plan test does not exercise the boundary its name claims; strengthened via a new test, plan test untouched.
