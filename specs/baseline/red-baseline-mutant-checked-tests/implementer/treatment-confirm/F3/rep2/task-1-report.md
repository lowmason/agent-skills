# Task 1 report
Implemented `count_words` in wordcount.py (skip lines whose first non-blank char is `#`; split rest on whitespace runs). Added plan test plus 6 extra tests (indented comment, `#word`, mid-line `#`, whitespace runs, empty/blank, comment-only).

TDD: RED: `pytest -q tests/test_wordcount.py` -> ImportError: cannot import name 'count_words' (expected, empty module). GREEN: 7 passed.

Mutants: run /private/tmp/mt-rep-7WyIFm/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.

Files: wordcount.py, tests/test_wordcount.py (committed); mutant patches/mutants file in .sdd/plan.
No plan/spec conflicts. Self-review: nothing outstanding.
