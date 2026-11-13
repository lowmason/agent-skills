# Task 1 report
Implemented `parse_duration` in duration.py (ASCII-only regex, fullmatch, empty rejected) and plan tests in tests/test_duration.py (verbatim).
RED: pytest -q tests/test_duration.py -> collection error (ImportError, parse_duration missing).
GREEN: 22 passed.
Mutants: /private/tmp/mt-rep-79IBoZ/repo/.sdd/plan/task-1-mutants.log — caught 8, survived 0, invalid 0.
Files: duration.py, tests/test_duration.py, .sdd/plan/task-1-mutants.md + patches.
Self-review: no spec/test conflicts; no concerns.
