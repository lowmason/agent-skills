# Task 1 report
Implemented `parse_duration` in duration.py (regex fullmatch on `(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?` with [0-9], empty rejected). Tests: tests/test_duration.py as given by the plan.
TDD RED: `pytest -q tests/test_duration.py` -> ImportError for parse_duration. GREEN: 22 passed.
Mutants: /private/tmp/mt-rep-ROOdBk/repo/.sdd/plan/task-1-mutants.log — caught 10, survived 0, invalid 0.
Files: duration.py, tests/test_duration.py (+ .sdd/plan mutant files, uncommitted).
No plan/spec conflicts. No concerns.
