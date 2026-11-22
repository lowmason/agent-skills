# Task 1 report
Implemented `fee` in parking.py (free up to 30 min; else 2 per started hour). Tests in tests/test_parking.py: 2 plan tests unchanged + 6 boundary tests (input-shape commit).
TDD RED: `pytest -q tests/test_parking.py` -> ModuleNotFoundError: No module named 'parking'. GREEN: 2 passed; later 8 passed.
Mutants: /private/tmp/msr104/rep2/repo/.sdd/plan/task-1-screen.log — caught 6, survived 0, invalid 0. Revert: not loaded 1 (all tests fail on revert).
Files: parking.py, tests/test_parking.py, .sdd/plan/task-1-mutants.md and mutant patches (uncommitted workspace files).
No plan/spec conflicts.
