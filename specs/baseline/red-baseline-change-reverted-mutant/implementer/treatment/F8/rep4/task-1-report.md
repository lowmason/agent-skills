# Task 1 report
Implemented `to_bytes` in units.py (regex `(\d+)(B|KB|MB)`, ValueError otherwise) and tests/test_units.py (plan tests verbatim).
RED: `pytest -q tests/test_units.py` -> collection error (ModuleNotFoundError for units).
GREEN: 2 passed, output pristine.
Mutants: /private/tmp/mt-rep-O3smUe/repo/.sdd/plan/task-1-mutants.log — caught 3, survived 0, invalid 0. Revert: not loaded 1 (both tests fail on revert).
Files: units.py, tests/test_units.py (committed); .sdd/plan mutant files (uncommitted).
Self-review: no issues; no plan/spec conflict.
