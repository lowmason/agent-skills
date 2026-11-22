# Task 1 report

Implemented `fee(minutes)` in `parking.py` (<=30 free; else 2 per started hour). Tests in `tests/test_parking.py`: 2 plan tests plus 6 boundary tests (0, 30, 31, 60, 61, 180).

TDD: RED — `pytest -q tests/test_parking.py` gave `ModuleNotFoundError: No module named 'parking'`. GREEN — 2 passed; later 8 passed.

Mutants: /private/tmp/msr104/rep5/repo/.sdd/plan/task-1-screen.log — caught 5, survived 0, invalid 0. Revert: not loaded 1 (test file fails to import on the revert, so every test fails there).

Files: parking.py, tests/test_parking.py (+ .sdd mutants file and patches).
Spec/plan-test conflict: none. Concerns: none.
