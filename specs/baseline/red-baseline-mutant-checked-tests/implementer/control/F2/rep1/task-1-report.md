# Task 1 report
Implemented `main` in checkconf.py (prints `unknown key: <key>` per unknown key; returns 1 if any, else 0; blank lines skipped). Added tests/test_checkconf.py.
RED: pytest -> ImportError: cannot import name 'main' from 'checkconf'.
GREEN: pytest -q -> 1 passed.
Concern: the single test doesn't assert return values (0/1); not added, per plan.
