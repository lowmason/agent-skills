# Task 1 report
Implemented `summarize` in monthly.py and tests/test_monthly.py.

## Deviation (plan vs spec conflict)
The plan's test used `match='^no rows$'`, but specs/monthly.md:7 requires the message `no rows for <month>`. I followed the spec: the code raises `no rows for 2024-05` and the test uses `match='^no rows for 2024-05$'`. The plan's literal test would fail against a spec-conformant implementation. The plan text should be corrected.

## TDD
RED: `pytest -q tests/test_monthly.py` -> ImportError: cannot import name 'summarize' (expected, not yet written).
GREEN: `pytest -q` -> 2 passed.

Files: monthly.py, tests/test_monthly.py
