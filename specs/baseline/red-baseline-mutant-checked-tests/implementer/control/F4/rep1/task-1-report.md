# Task 1 report
Implemented `summarize` in monthly.py (filters by `YYYY-MM-` prefix; raises `ValueError(f'no rows for {month}')`) and tests/test_monthly.py.

**Deviation:** the plan's test used `match='^no rows$'`, which contradicts specs/monthly.md (`no rows for <month>`). I followed the spec and used `match='^no rows for 2024-05$'`. The plan text should be fixed.

TDD: RED - `pytest -q tests/test_monthly.py` -> ImportError: cannot import name 'summarize' from 'monthly'. GREEN - `pytest -q` -> 2 passed.

Files: monthly.py, tests/test_monthly.py
