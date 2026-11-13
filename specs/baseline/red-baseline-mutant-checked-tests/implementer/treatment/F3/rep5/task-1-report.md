# Task 1 report
Implemented `count_words` in wordcount.py (skip lines whose lstrip starts with '#', sum len(line.split())). Tests in tests/test_wordcount.py (plan test + 6 shape tests); 7 passed.

TDD RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_wordcount.py` -> ImportError: cannot import name 'count_words' (expected, empty module).
GREEN: same command -> 7 passed.

Mutants: /private/tmp/mt-rep-atkjo3/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.
Files: wordcount.py, tests/test_wordcount.py (committed); .sdd/plan mutant files (uncommitted).
No plan/spec conflicts; no concerns.
