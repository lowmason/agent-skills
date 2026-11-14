# Task 1 report
Implemented `slugify` as `re.sub(r'\s+', '-', title.lower())` (slug.py); created tests/test_slug.py (2 plan tests unchanged + 3 added: single space, long runs, mixed whitespace).
TDD RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_slug.py` -> 1 failed, 1 passed (test_slugify_collapses_space_runs; 'a--b' != 'a-b').
GREEN: same command -> 5 passed.
Mutants: /private/tmp/mt-rep-ImUUVL/repo/.sdd/plan/task-1-mutants.log — caught 3, survived 0, invalid 0.
Files: slug.py, tests/test_slug.py (committed); .sdd/plan mutant files (uncommitted).
Concerns: none. Leading/trailing whitespace yields leading/trailing hyphen; spec silent.
