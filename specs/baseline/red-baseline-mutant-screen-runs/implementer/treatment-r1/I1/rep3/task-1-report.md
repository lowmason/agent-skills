# Task 1 report
Implemented `fee` in parking.py (free <= 30 min; 2 per started hour). Added boundary tests (30, 31, 60, 61) in a second commit (input shape).
TDD: RED = ModuleNotFoundError for `parking`; GREEN = 6 passed.
Mutants: 6 mutants, screen run .sdd/plan/task-1-screen-3.log (caught 6, survived 0, invalid 0; 5 carried).
Revert: tests not loaded on revert (parking.py absent) so every test fails on the revert.
Files: parking.py, tests/test_parking.py, .sdd/plan/task-1-mutant-*.patch, task-1-mutants.md.
No concerns; plan tests don't conflict with the spec.
