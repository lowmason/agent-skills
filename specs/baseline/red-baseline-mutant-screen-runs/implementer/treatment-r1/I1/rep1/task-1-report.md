# Task 1 report
Implemented `fee` in parking.py (<=30 min free; else 2 per started hour) and tests/test_parking.py.
RED: pytest -q tests/test_parking.py -> ModuleNotFoundError: No module named 'parking' (expected, file absent).
GREEN: pytest -q -> 2 passed.
Mutants: none: not a mutant task (plan has no mutant step).
Files: parking.py, tests/test_parking.py
Concerns: none; plan tests agree with spec.
