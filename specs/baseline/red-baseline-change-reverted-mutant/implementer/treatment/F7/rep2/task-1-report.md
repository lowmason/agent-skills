# Task 1 report
Implemented: slug.py `slugify` now does `re.sub(r'\s+', '-', title.lower())`. Tests in tests/test_slug.py: the 2 plan tests plus 6 added (single space, long run, tab/newline, mixed run, run at ends, several runs).
TDD: RED before the fix: 6 failed, 2 passed (the plan's collapse test failed as expected). GREEN: 8 passed.
Mutants: /private/tmp/mt-rep-GiBJau/repo/.sdd/plan/task-1-mutants.log — caught 4, survived 0, invalid 0.
Revert: failed 6, passed 2 (test_slugify_lowercases, test_slugify_single_space); both recorded as Keeps lines (pre-existing behavior kept).
Files: slug.py, tests/test_slug.py (committed); .sdd/plan mutant files (uncommitted workspace).
Concerns: spec says nothing about leading/trailing whitespace; the code gives one hyphen at the ends (pinned by a test).
