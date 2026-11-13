# Task 1 report
Implemented `parse_duration` in duration.py (regex fullmatch with [0-9]; empty string rejected explicitly) and tests/test_duration.py (plan's tests verbatim).
TDD RED: `pytest -q tests/test_duration.py` -> ImportError: cannot import name 'parse_duration' (expected, empty module).
GREEN: 22 passed, output pristine.
Mutants: /private/tmp/mt-rep-lMQwGW/repo/.sdd/plan/task-1-mutants.log — caught 6, survived 0, invalid 0.
Files: duration.py, tests/test_duration.py (commit); .sdd/plan mutant files.
No plan/spec conflicts found.
