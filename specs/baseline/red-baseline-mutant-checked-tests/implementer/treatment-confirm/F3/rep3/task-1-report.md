# Task 1 report
Implemented `count_words` in wordcount.py (skip lines whose first non-blank char is '#', split others on whitespace runs). Added plan test plus 6 extra tests in tests/test_wordcount.py.
TDD RED: `pytest -q tests/test_wordcount.py` -> ImportError: cannot import name 'count_words' (collection error). GREEN: 7 passed.
Mutants: /private/tmp/mt-rep-HmwGJb/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.
Files: wordcount.py, tests/test_wordcount.py (+ .sdd/plan mutant files).
No plan/spec conflicts.
