# Task 1 report
Implemented `to_bytes` in units.py (regex `(\d+)(B|KB|MB)`, ValueError otherwise) and tests/test_units.py (plan tests verbatim).
RED: pytest -q tests/test_units.py -> collection error (no module `units`). GREEN: 2 passed.
Commit: 6e2e2ad Add to_bytes.
Mutants: /private/tmp/mt-rep-jV1rjo/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.
Files: units.py, tests/test_units.py (mutants/patches in .sdd/plan).
No plan/spec conflicts. Invalid-input behaviour (ValueError) is my choice; spec is silent.
