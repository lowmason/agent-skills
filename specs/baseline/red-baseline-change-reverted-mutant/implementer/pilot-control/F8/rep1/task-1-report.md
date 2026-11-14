# Task 1 report
Implemented `to_bytes` in units.py (strip trailing unit letters, int * factor table); tests/test_units.py as given by plan.
TDD: RED = ModuleNotFoundError-style collection error ("1 error during collection") before units.py existed. GREEN = `2 passed`.
Mutants: .sdd/plan/task-1-mutants-2.log — caught 3, survived 0, invalid 0 (first run had invalid patches from BSD sed; regenerated).
Files: units.py, tests/test_units.py (committed); mutants file/patches in .sdd/plan.
Concerns: none. Invalid input (e.g. '5GB') raises KeyError; spec doesn't define it.
