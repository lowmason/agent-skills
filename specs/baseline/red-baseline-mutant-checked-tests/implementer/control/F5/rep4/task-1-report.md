# Task 1 report
Implemented `parse_duration` in duration.py (regex fullmatch of optional h/m/s parts; empty string raises ValueError).
Tests: tests/test_duration.py as in brief.
RED: `pytest -q tests/test_duration.py` -> ImportError: cannot import name 'parse_duration' (expected, function absent).
GREEN: same command -> 10 passed.
Files: duration.py, tests/test_duration.py
Concern: `\d` also matches non-ASCII Unicode digits (int() accepts them); spec says "digits", so left as is.
