# Task 1 report
Implemented `to_bytes` in units.py (regex digits+unit, factors 1/1024/1024**2, ValueError otherwise) and tests/test_units.py (plan tests verbatim).
RED: `pytest -q tests/test_units.py` -> collection error (ModuleNotFoundError units). GREEN: 2 passed.
Mutants: /private/tmp/mt-rep-2Mo5J7/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.
Files: units.py, tests/test_units.py (committed); mutant patches/mutants.md in .sdd/plan.
No concerns; no plan-test/spec conflict.
