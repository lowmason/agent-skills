# Task 1 report
Implemented `parse_duration` in duration.py (regex fullmatch with ASCII [0-9], empty rejected). Tests from plan verbatim plus extra `test_parse_duration_multi_digit_parts`.
RED: `pytest -q tests/test_duration.py` -> ImportError: cannot import name 'parse_duration'.
GREEN: 22 passed (25 with the added test).
Mutants: /private/tmp/mt-rep-RQu0gn/repo/.sdd/plan/task-1-mutants.log — caught 8, survived 0, invalid 0.
Files: duration.py, tests/test_duration.py, .sdd/plan/task-1-mutant*.patch, task-1-mutants.md.
No plan/spec conflicts.
