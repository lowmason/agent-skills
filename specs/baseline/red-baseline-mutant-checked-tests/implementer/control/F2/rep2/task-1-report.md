# Task 1 report
Implemented `main` in checkconf.py (prints `unknown key: <key>`, returns 1 if any unknown key else 0; blank lines skipped). Added tests/test_checkconf.py.
RED: pytest -> ImportError: cannot import name 'main' from 'checkconf' (expected, file empty).
GREEN: pytest -q -> 1 passed.
Files: checkconf.py, tests/test_checkconf.py
Concern: the test doesn't assert the return value; blank-line skipping is beyond the spec text but harmless.
