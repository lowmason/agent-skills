# Task 1 report
Implemented `main` in checkconf.py (prints `unknown key: <key>` per unknown key; returns 1 if any, else 0; blank lines skipped). Added tests/test_checkconf.py.
RED: `pytest -q tests/test_checkconf.py` -> ImportError: cannot import name 'main' from 'checkconf'.
GREEN: full suite -> 1 passed.
Files: checkconf.py, tests/test_checkconf.py
Concern: return value (1/0) is not covered by the plan's test; blank-line skipping is my addition.
