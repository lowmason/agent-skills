# Task 1 report
Implemented `count_words` in wordcount.py: splits lines, skips lines whose first non-blank char is `#`, sums len(line.split()).
Added tests/test_wordcount.py (brief's test).

TDD
- RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_wordcount.py` -> ImportError: cannot import name 'count_words' from 'wordcount'
- GREEN: same command -> 1 passed

Files: wordcount.py, tests/test_wordcount.py
Self-review: matches both spec rules; no extras. No concerns.
