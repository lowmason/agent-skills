# Task 1 report
Implemented `count_words` in wordcount.py (skip lines whose lstrip starts with '#', sum len(line.split())). Added 5 extra tests beyond the plan test (plan test untouched).
RED: `pytest -q tests/test_wordcount.py` -> ImportError: cannot import name 'count_words' (expected, empty module).
GREEN: 6 passed, output pristine.
Mutants: /private/tmp/mt-rep-LftVOm/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.
Files: wordcount.py, tests/test_wordcount.py, .sdd/plan/task-1-mutant-*.patch, task-1-mutants.md (workspace files left uncommitted).
Self-review: no issues; no plan/spec conflict.
