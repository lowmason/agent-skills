# Task 1 report
Implemented `to_bytes` in units.py (regex `(\d+)(B|KB|MB)` fullmatch, factors 1/1024/1024**2; ValueError otherwise) and plan tests verbatim in tests/test_units.py.
TDD: RED = ModuleNotFoundError for `units` (collection error); GREEN = `2 passed`.
Mutants: .sdd/plan/task-1-mutants-2.log — caught 4, survived 0, invalid 0 (first run invalid due to empty patches from BSD sed; redone).
Files: units.py, tests/test_units.py (committed); mutant files under .sdd/plan.
No plan/spec conflicts.
