# Task 1 report
Implemented `parse_duration` in duration.py (ASCII-only regex, fullmatch, empty rejected) and tests/test_duration.py exactly as planned.
TDD RED: `pytest -q tests/test_duration.py` -> ImportError: cannot import name 'parse_duration'.
GREEN: 22 passed.
Mutants: /private/tmp/mt-rep-3KS6xF/repo/.sdd/plan/task-1-mutants.log — caught 4, survived 0, invalid 0.
Files: duration.py, tests/test_duration.py (commit 10736ed); mutant artifacts in .sdd/plan.
Concerns: none; no plan-test/spec conflict.
