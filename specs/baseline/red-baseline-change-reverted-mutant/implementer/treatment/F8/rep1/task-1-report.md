# Task 1 report
Implemented `to_bytes` in `units.py` (regex `\d+` + `B|KB|MB`, 1 KB = 1024 B; ValueError on malformed input). Tests in `tests/test_units.py` as the plan wrote them.

TDD
- RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_units.py` -> `ModuleNotFoundError: No module named 'units'` (expected: module absent).
- GREEN: same command -> `2 passed`.

Mutants: run /private/tmp/mt-rep-OUe9tC/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0. Revert: not loaded 1 (both tests fail on the revert).

Files: units.py, tests/test_units.py (commit 5939b6d); .sdd/plan/task-1-mutant-*.patch, task-1-mutants.md.
Self-review: no issues. No plan/spec conflict. ValueError on bad input is beyond spec but harmless.
