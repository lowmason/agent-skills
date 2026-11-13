# Task 1 report
Implemented `count_words` in wordcount.py (skip lines whose first non-blank char is '#', split the rest on whitespace runs). Added 5 extra tests for rule shapes beyond the plan test (plan test unchanged).
TDD RED: `pytest -q tests/test_wordcount.py` -> ImportError: cannot import name 'count_words' (expected, function not yet written).
GREEN: `pytest -q tests` -> 6 passed, output clean.
Mutants: /private/tmp/mt-rep-hiSy1M/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.
Files: wordcount.py, tests/test_wordcount.py (committed); .sdd/plan mutant files.
Concerns: none; no plan-test/spec conflict.
