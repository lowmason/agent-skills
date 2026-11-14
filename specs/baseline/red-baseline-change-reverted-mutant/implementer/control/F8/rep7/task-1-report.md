# Task 1 report
Implemented `to_bytes` in units.py (regex fullmatch `\d+(B|KB|MB)`, ValueError otherwise) and plan tests in tests/test_units.py.
TDD: RED `pytest -q tests/test_units.py` -> collection error (ModuleNotFoundError units). GREEN -> 2 passed.
Mutants: /private/tmp/mt-rep-6E3g0f/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.
Files: units.py, tests/test_units.py (commit 6db006e); mutant files in .sdd/plan.
Concerns: none.
