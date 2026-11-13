# Task 1 report
Implemented `main` in checkconf.py (prints `unknown key: <key>`, returns 1 if any, else 0; blank lines skipped). Added tests/test_checkconf.py.
RED: pytest -> ImportError: cannot import name 'main' from 'checkconf'.
GREEN: pytest -q -> 1 passed.
Note: the test doesn't assert the return value; blank-line skipping is my own choice (spec silent).
