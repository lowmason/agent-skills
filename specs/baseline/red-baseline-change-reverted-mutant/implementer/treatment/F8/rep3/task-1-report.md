# Task 1 report
Implemented `to_bytes` in units.py (regex `(\d+)(B|KB|MB)`, factors 1/1024/1024², ValueError otherwise) and the plan's tests in tests/test_units.py, unchanged.
RED: `pytest -q tests/test_units.py` -> ModuleNotFoundError: No module named 'units'.
GREEN: `pytest -q` -> 2 passed.
Mutants: .sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0. Revert: both tests not loaded (fail on revert).
Files: units.py, tests/test_units.py (commit cf6b216); mutant patches/mutants file in .sdd/plan.
Concerns: none.
