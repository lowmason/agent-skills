# Task 1 report

Implemented: `slugify` in slug.py now does `re.sub(r'\s+', '-', title.lower())`. Added tests/test_slug.py (2 plan tests + 5 extra shapes).

TDD RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_slug.py` -> `1 failed, 1 passed` (test_slugify_collapses_space_runs: 'a--b' != 'a-b'), as expected.
GREEN: same command after the fix -> `7 passed`.

Mutants: /private/tmp/mt-rep-lhZDfL/repo/.sdd/plan/task-1-mutants.log — caught 3, survived 0, invalid 0.
Revert: 5 tests fail; test_slugify_lowercases and test_slugify_single_space pass by design (Keeps lines in task-1-mutants.md).

Files: slug.py, tests/test_slug.py (committed); .sdd/plan mutant files (uncommitted workspace).
Self-review: no plan/spec conflict. Leading/trailing whitespace is unspecified, so left as-is (becomes a hyphen).
