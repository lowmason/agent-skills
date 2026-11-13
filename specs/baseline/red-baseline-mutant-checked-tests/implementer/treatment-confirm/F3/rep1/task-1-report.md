# Task 1 report

Implemented `count_words` in wordcount.py: skips lines whose first non-blank char is `#`, counts `str.split()` words elsewhere.

TDD
- RED: `pytest -q tests/test_wordcount.py` -> ImportError: cannot import name 'count_words' (expected, function absent)
- GREEN: same command -> 1 passed

Extra tests (new, plan test untouched): indented comment, mid-line '#', mixed whitespace runs, empty/blank, comment on last line w/o newline, comment-only text. Full suite: 7 passed.

Mutants: /tmp/mt-rep-r9zWr0/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0

Files: wordcount.py, tests/test_wordcount.py, .sdd/plan/task-1-mutants.md, task-1-mutant-{1..5}.patch
Commits: "Add count_words", "Cover count_words rule input shapes"
Concerns: none; no plan-test/spec conflict.
