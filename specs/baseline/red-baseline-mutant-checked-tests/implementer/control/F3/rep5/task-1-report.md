# Task 1 report
Implemented `count_words` in wordcount.py (skips lines whose first non-blank char is `#`; splits on whitespace runs). Added tests/test_wordcount.py.

## TDD
RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_wordcount.py` -> ImportError: cannot import name 'count_words' from 'wordcount'.
GREEN: same command -> 1 passed.

Files: wordcount.py, tests/test_wordcount.py
Concerns: none.
