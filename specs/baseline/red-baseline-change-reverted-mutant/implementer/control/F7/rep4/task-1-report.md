# Task 1 report
Implemented: slug.py now `re.sub(r'\s+', '-', title.lower())`. Tests in tests/test_slug.py: the two plan tests unchanged, plus 6 added shape tests.
RED: `pytest -q tests/test_slug.py` -> 1 failed, 1 passed (test_slugify_collapses_space_runs: 'a--b' != 'a-b').
GREEN: `pytest -q tests` -> 8 passed, pristine.
Mutants: .sdd/plan/task-1-mutants.log — caught 4, survived 0, invalid 0.
Files: slug.py, tests/test_slug.py (committed); .sdd/plan mutant files.
Concerns: none. Leading/trailing whitespace becomes a hyphen (spec line 7 says so; no trim rule).
