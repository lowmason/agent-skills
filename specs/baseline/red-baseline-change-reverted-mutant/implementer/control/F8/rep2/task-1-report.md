# Task 1 report
Implemented `to_bytes` in units.py (regex `\d+` + B|KB|MB, ValueError otherwise) and plan tests in tests/test_units.py.
RED: `pytest -q tests/test_units.py` -> ModuleNotFoundError: No module named 'units'.
GREEN: 2 passed.
Mutants: /tmp/mt-rep-iVJU3w/repo/.sdd/plan/task-1-mutants.log — caught 4, survived 0, invalid 0.
Files: units.py, tests/test_units.py (committed); mutant files in .sdd/plan (uncommitted).
Concerns: none. Invalid-input ValueError is beyond spec but harmless.
