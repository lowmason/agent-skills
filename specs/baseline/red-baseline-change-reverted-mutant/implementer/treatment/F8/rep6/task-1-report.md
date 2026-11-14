# Task 1 report
Implemented `to_bytes` in units.py (regex `\d+(B|KB|MB)`, factors 1/1024/1024², ValueError otherwise) and tests/test_units.py (plan tests verbatim).
RED: pytest -> collection error (ModuleNotFoundError units). GREEN: 2 passed.
Mutants: /tmp/mt-rep-nCy64q/repo/.sdd/plan/task-1-mutants.log — caught 4, survived 0, invalid 0. Revert: not loaded 1 (both tests fail on revert).
Files: units.py, tests/test_units.py (committed); mutants/patches/report in .sdd/plan.
No concerns; no plan-test/spec conflict.
