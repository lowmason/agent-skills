# Task 1 report
Implemented `to_bytes` in units.py (regex `\d+` + B|KB|MB, 1 KB = 1024 B; ValueError otherwise) and the plan's tests in tests/test_units.py.
RED: `pytest -q tests/test_units.py` -> ModuleNotFoundError for `units`. GREEN: 2 passed.
Mutants: /private/tmp/mt-rep-xw5j6M/repo/.sdd/plan/task-1-mutants.log — caught 4, survived 0, invalid 0.
Files: units.py, tests/test_units.py (committed); mutant patches/mutants file in .sdd/plan.
Concerns: none.
