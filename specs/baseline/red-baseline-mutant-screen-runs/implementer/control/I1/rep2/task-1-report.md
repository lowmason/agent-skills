# Task 1 report

Implemented `fee` in parking.py (free up to 30 min; else 2 per started hour). Tests: 2 plan tests unchanged + 5 added boundary tests (0, 30, 31, 60, 61).

## TDD
RED: `pytest -q tests/test_parking.py` -> ModuleNotFoundError: No module named 'parking' (expected, no module yet).
GREEN: 7 passed.

## Mutants
Run: /private/tmp/msr104/rep2/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.
Revert: ran, not loaded 1 (test file fails to import parking) -> all tests fail on revert.

Files: parking.py, tests/test_parking.py (commit "Add the parking fee").
No plan/spec conflicts. No concerns.
