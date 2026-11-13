# Task 1 report
Implemented `parse_duration` in `duration.py` (regex with `[0-9]`, `fullmatch`, empty rejected) and `tests/test_duration.py` from the brief.
RED: `pytest -q tests/test_duration.py` -> ImportError: cannot import name 'parse_duration' (expected, function absent).
GREEN: `pytest -q` -> 22 passed.
Files: duration.py, tests/test_duration.py. No concerns.
