# Task 1 report
Implemented `latest_report` in latest.py (max over `*.txt` by parsed ISO `date:` line; ValueError if a report has no date line; empty folder raises ValueError from max). Added tests/test_latest.py.

TDD RED: `pytest -q tests/test_latest.py` -> ImportError: cannot import name 'latest_report' from 'latest'.
GREEN: `pytest -q` -> 1 passed.

Files: latest.py, tests/test_latest.py
Concerns: spec doesn't define behavior for empty folder / missing date; left as raising errors.
