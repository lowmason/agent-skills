# Task 1 report

Implemented: `slug.py` slugify now uses `re.sub(r'\s+', '-', title.lower())`. Tests added in tests/test_slug.py (2 plan tests, 5 extra for single space, long run, tab/newline, edges, multiple runs).

TDD RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_slug.py` -> 1 failed, 1 passed (test_slugify_collapses_space_runs: 'a--b' != 'a-b'), as expected.
GREEN: `pytest -q tests` -> 7 passed.

Mutants: /private/tmp/mt-rep-HlMBpX/repo/.sdd/plan/task-1-mutants.log — caught 4, survived 0, invalid 0.
Revert: 5 tests fail; test_slugify_lowercases and test_slugify_single_space pass (Keeps lines in mutants file).

Files: slug.py, tests/test_slug.py. (.sdd/plan is gitignored, so mutants files are not committed.)
Concerns: none. Spec says whitespace runs (not just spaces), so regex uses \s+; edge runs yield a hyphen, no strip.
