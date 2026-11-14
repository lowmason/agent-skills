# Task 1 report
Implemented `to_bytes` in units.py (regex `\d+` + B|KB|MB, 1024 factors; ValueError otherwise) and the plan's tests in tests/test_units.py.
TDD: RED = ModuleNotFoundError/collection error for `units` (1 error); GREEN = `2 passed`.
Mutants: /private/tmp/mt-rep-fkNPYZ/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.
Files: units.py, tests/test_units.py (committed "Add to_bytes"); mutant files in .sdd/plan.
Concerns: none. Invalid input raising ValueError is my choice (spec silent).
