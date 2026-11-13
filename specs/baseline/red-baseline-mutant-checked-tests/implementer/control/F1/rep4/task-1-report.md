# Task 1 report
Implemented `latest_report` in latest.py (max over *.txt in folder, keyed by ISO date from `date:` line; ValueError if a report lacks one; empty folder raises ValueError from max).
Test added: tests/test_latest.py.
TDD RED: `pytest -q tests/test_latest.py` -> ImportError: cannot import name 'latest_report'.
GREEN: `pytest -q` -> 1 passed.
Files: latest.py, tests/test_latest.py
Concerns: spec doesn't define behavior for empty folder or missing date line; left as errors.
