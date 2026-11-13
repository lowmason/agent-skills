# Task 1 report
Implemented `count_words` in wordcount.py (sum of split() over lines whose lstrip() doesn't start with '#'). Tests in tests/test_wordcount.py: plan test plus 4 added for indented comment, mid-line '#', whitespace runs, empty/comment-only.
## TDD
RED: pytest -q tests/test_wordcount.py -> ImportError: cannot import name 'count_words' (expected, function absent).
GREEN: 5 passed, output pristine.
## Mutants
/private/tmp/mt-rep-iQos33/repo/.sdd/plan/task-1-mutants.log — caught 4, survived 0, invalid 0
## Files
wordcount.py, tests/test_wordcount.py (committed); .sdd/plan mutant files (uncommitted)
## Concerns
None; no plan/spec conflict.
