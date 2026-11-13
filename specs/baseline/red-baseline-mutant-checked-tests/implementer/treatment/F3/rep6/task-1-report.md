# Task 1 report
Implemented `count_words` in wordcount.py (skips lines whose first non-blank char is '#', splits on whitespace runs); tests in tests/test_wordcount.py (6 tests).
TDD RED: `pytest -q tests/test_wordcount.py` -> ImportError: cannot import name 'count_words' (expected, empty module).
GREEN: 6 passed.
Mutants: /private/tmp/mt-rep-efcXeR/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.
Files: wordcount.py, tests/test_wordcount.py, .sdd/plan/task-1-mutants.md and patches (uncommitted workspace files).
Concerns: none; no plan-test/spec conflict.
