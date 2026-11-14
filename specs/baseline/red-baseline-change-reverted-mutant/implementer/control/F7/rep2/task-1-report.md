# Task 1 report
Implemented: `slugify` now does `re.sub(r'\s+', '-', title.lower())` (slug.py). Tests in tests/test_slug.py: the 2 plan tests unchanged plus 4 added (mixed whitespace run, single tab, single space, multi-word lowercase).
TDD RED: `pytest -q tests/test_slug.py` -> 4 failed, 2 passed (plan space-run test failed as expected; 3 added tests also failed on the old code).
GREEN: 6 passed.
Mutants: run /private/tmp/mt-rep-Wa8zAl/repo/.sdd/plan/task-1-mutants.log — caught 3, survived 0, invalid 0.
Files: slug.py, tests/test_slug.py (committed); mutant patches and mutants file in .sdd/plan.
Concerns: none. Leading/trailing whitespace becomes hyphens (spec silent).
