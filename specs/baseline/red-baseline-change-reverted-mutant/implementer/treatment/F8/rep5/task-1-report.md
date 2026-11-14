# Task 1 report
Implemented `to_bytes` in units.py (suffix match KB/MB/B, factors 1/1024/1024², ValueError otherwise); tests/test_units.py as in plan.
RED: `pytest -q tests/test_units.py` -> collection ERROR (ModuleNotFoundError for units).
GREEN: 2 passed.
Mutants: /private/tmp/mt-rep-cftPpS/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0. Revert: both tests not loaded (fail on revert).
Files: units.py, tests/test_units.py (committed 38f015e); .sdd/plan mutant files.
Self-review: no issues; no plan/spec conflict.
