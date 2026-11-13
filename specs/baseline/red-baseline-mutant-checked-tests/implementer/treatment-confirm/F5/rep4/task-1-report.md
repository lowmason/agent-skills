# Task 1 report

Implemented `parse_duration` in `duration.py` (regex `fullmatch` with ASCII `[0-9]+` parts, rejects empty text) and `tests/test_duration.py` (plan tests verbatim plus a new multi-digit test).

TDD
- RED: `pytest -q tests/test_duration.py` -> ImportError: cannot import name 'parse_duration' from 'duration'.
- GREEN: `pytest -q` -> 22 passed (plan tests); 26 with the added multi-digit test.

Mutants: /private/tmp/mt-rep-4oNmE3/repo/.sdd/plan/task-1-mutants.log — caught 9, survived 0, invalid 0.

Files: duration.py, tests/test_duration.py (+ .sdd/plan mutant files).
Commits: 8b45e4d Add parse_duration; second commit adds multi-digit test (aimed at one-digit-only hour mutant).
Self-review: no spec/plan-test conflicts; no concerns.
