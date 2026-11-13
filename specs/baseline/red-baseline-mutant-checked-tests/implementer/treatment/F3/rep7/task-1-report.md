# Task 1 report
Implemented `count_words` in wordcount.py (skip lines whose first non-blank char is `#`; split rest on whitespace runs). Tests in tests/test_wordcount.py: plan test plus 4 added shape tests.
TDD RED: pytest -> ImportError cannot import name 'count_words'. GREEN: 5 passed.
Mutants: /private/tmp/mt-rep-tyePj8/repo/.sdd/plan/task-1-mutants.log — caught 4, survived 0, invalid 0.
Files: wordcount.py, tests/test_wordcount.py, .sdd/plan/task-1-mutant-{1..4}.patch, task-1-mutants.md
Concerns: none; no plan-test/spec conflict.
