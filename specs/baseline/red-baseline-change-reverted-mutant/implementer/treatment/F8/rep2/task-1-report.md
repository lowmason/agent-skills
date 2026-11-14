# Task 1 report
Implemented `to_bytes` in units.py (regex fullmatch digits+B|KB|MB, 1KB=1024; ValueError otherwise) and plan tests in tests/test_units.py.

## TDD Evidence
RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_units.py` -> ModuleNotFoundError: No module named 'units' (expected, no module yet).
GREEN: same command -> 2 passed.

## Mutants
/private/tmp/mt-rep-ryjH8Q/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.
Revert: ran, exit 1, failed 0, not loaded 1 (units missing) — both tests fail on the revert.

Files: units.py, tests/test_units.py (committed fdf38e1); mutant patches/mutants file in .sdd/plan.
Self-review: no issues; no plan/spec conflict.
