# Task 1 report
Implemented `parse_duration` in duration.py (regex fullmatch with ASCII [0-9]; empty rejected) and tests/test_duration.py.

TDD
- RED: `pytest -q tests/test_duration.py` -> ImportError: cannot import name 'parse_duration' from 'duration' (expected: function not yet written)
- GREEN: `pytest -q` -> 22 passed

Files: duration.py, tests/test_duration.py
Self-review: fullmatch avoids the `$` trailing-newline pitfall ('1h\n' rejected); no concerns.
