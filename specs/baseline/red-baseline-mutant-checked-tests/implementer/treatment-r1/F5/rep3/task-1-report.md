# Task 1 report
Implemented `parse_duration` in duration.py (regex `(?:([0-9]+)h)?(?:([0-9]+)m)?(?:([0-9]+)s)?` with fullmatch, empty text rejected). Tests from the plan in tests/test_duration.py.

TDD: RED `/tmp/mt-venv/bin/python -m pytest -q tests/test_duration.py` -> ImportError: cannot import name 'parse_duration' (expected, duration.py empty). GREEN: 22 passed.

Mutants: /tmp/mt-rep-D4G8ie/repo/.sdd/plan/task-1-mutants.log — caught 10, survived 0, invalid 0.

Files: duration.py, tests/test_duration.py (commit 1c9b2ec); .sdd/plan mutant files.
Self-review: no plan/spec conflicts; no concerns.
