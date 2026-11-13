# Task 1 report
Implemented `parse_duration` in duration.py (regex fullmatch on ASCII digits h/m/s, empty rejected) and tests/test_duration.py.

TDD
- RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_duration.py` -> ImportError: cannot import name 'parse_duration' (expected, duration.py empty).
- GREEN: same command (full suite) -> 22 passed.

Files: duration.py, tests/test_duration.py
Self-review: no issues; fullmatch (not `$`) correctly rejects trailing newline.
