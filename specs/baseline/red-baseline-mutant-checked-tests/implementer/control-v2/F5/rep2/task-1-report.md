# Task 1 report
Implemented `parse_duration` in duration.py (regex fullmatch, ASCII digits only, empty rejected) and tests/test_duration.py.

## TDD
RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_duration.py` -> ImportError: cannot import name 'parse_duration' (collection error), expected as duration.py was empty.
GREEN: same command (full suite) -> 22 passed.

Files: duration.py, tests/test_duration.py. No concerns.
