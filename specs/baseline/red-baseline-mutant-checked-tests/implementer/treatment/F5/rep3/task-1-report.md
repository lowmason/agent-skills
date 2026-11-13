# Task 1 report
Implemented `parse_duration` in duration.py (regex `fullmatch` with ASCII `[0-9]+` parts, empty text rejected) and plan tests in tests/test_duration.py, verbatim.
RED: `pytest -q tests/test_duration.py` -> ImportError: cannot import name 'parse_duration' (expected, empty module).
GREEN: 22 passed, output pristine.
Mutants: /private/tmp/mt-rep-9T3qUx/repo/.sdd/plan/task-1-mutants.log — caught 9, survived 0, invalid 0.
Files: duration.py, tests/test_duration.py. Commit 1310118.
Self-review: no plan-test/spec conflicts; no extra tests needed (all rule shapes covered).
