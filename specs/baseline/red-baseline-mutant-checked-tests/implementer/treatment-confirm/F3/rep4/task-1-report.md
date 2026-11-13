# Task 1 report
Implemented `count_words` in wordcount.py (skip lines whose lstripped form starts with '#', count str.split() words). Added plan test plus 5 extra tests for spec shapes (indented comment, mid-line #, whitespace runs, empty, only comments).
RED: `pytest -q tests/test_wordcount.py` -> ImportError: cannot import name 'count_words'.
GREEN: 6 passed, output pristine.
Mutants: /private/tmp/mt-rep-D2Zs3V/repo/.sdd/plan/task-1-mutants.log — caught 4, survived 0, invalid 0.
Files: wordcount.py, tests/test_wordcount.py, .sdd/plan/task-1-mutant-*.patch, task-1-mutants.md
No concerns; no plan/spec conflict.
