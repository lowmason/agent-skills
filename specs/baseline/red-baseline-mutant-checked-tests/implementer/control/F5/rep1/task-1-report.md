# Task 1 report
Implemented `parse_duration` in `duration.py` (regex fullmatch on `(Nh)?(Nm)?(Ns)?`, ASCII digits only, empty string rejected) and tests in `tests/test_duration.py`.

## TDD Evidence
- RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_duration.py` -> `ImportError: cannot import name 'parse_duration' from 'duration'` (function not yet written).
- GREEN: same command after implementation, full suite -> `10 passed`.

Files changed: duration.py, tests/test_duration.py
Self-review: no issues; no concerns.
