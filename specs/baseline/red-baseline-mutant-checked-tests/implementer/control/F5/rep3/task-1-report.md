# Task 1 report
Implemented `parse_duration` in duration.py (regex fullmatch, re.ASCII so only 0-9 digits; empty string rejected) and tests/test_duration.py.
RED: `pytest -q tests/test_duration.py` -> ImportError: cannot import name 'parse_duration'.
GREEN: 10 passed, output pristine.
Files: duration.py, tests/test_duration.py
