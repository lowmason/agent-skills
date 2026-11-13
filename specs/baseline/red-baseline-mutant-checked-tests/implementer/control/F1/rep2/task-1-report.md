# Task 1 report
Implemented `latest_report` in latest.py (max of *.txt by parsed ISO `date:` line; ValueError if a report lacks one; empty folder raises ValueError from max).
RED: `pytest -q tests/test_latest.py` -> ImportError: cannot import name 'latest_report'.
GREEN: `pytest -q` -> 1 passed.
Files: latest.py, tests/test_latest.py
