# Task 1 report

Implemented `count_words` in `wordcount.py` (split on '\n'; skip lines whose first non-blank char is '#'; count `str.split()` words otherwise). Tests in `tests/test_wordcount.py`: the plan test plus 9 extra shape tests.

## TDD Evidence
- RED: `pytest -q tests/test_wordcount.py` -> `ImportError: cannot import name 'count_words' from 'wordcount'` (function not yet written).
- GREEN: `1 passed` after implementation; final suite `10 passed`.

## Mutants
/private/tmp/mt-rep-T99xGP/repo/.sdd/plan/task-1-mutants.log — caught 7, survived 0, invalid 0

## Files changed
wordcount.py, tests/test_wordcount.py (plus .sdd/plan mutant files)

## Self-review
No plan/spec conflict. Switched from splitlines() to split('\n') so U+2028 etc. don't end a comment line (mutant 7).
Note: sed misbehaved in this environment, so edits were done via Edit/python.
