# Task 1 report
Implemented `fee` in parking.py (<=30 free; else 2 per started hour) and tests/test_parking.py (2 plan tests + 5 boundary tests).
RED: `pytest -q tests/test_parking.py` -> ModuleNotFoundError: No module named 'parking' (expected, file absent).
GREEN: 7 passed.
Mutants: .sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0. Revert: not loaded 1 (all tests fail on revert).
Files: parking.py, tests/test_parking.py (committed); mutants/patches in .sdd/plan.
Plan tests vs spec: no conflict (fee(150)=3 started hours*2=6).
