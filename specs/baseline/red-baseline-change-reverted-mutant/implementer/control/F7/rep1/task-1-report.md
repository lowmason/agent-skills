# Task 1 report
Implemented: slug.py now `re.sub(r'\s+', '-', title.lower())`. tests/test_slug.py: 2 plan tests verbatim + 6 added shape tests.
TDD RED: `pytest -q tests/test_slug.py` before fix -> 1 failed, 1 passed (test_slugify_collapses_space_runs). GREEN: 8 passed.
Mutants: /tmp/mt-rep-mJgsIQ/repo/.sdd/plan/task-1-mutants-2.log — caught 4, survived 0, invalid 0.
(The "revert" line in the run, failed 6 passed 2, is the check against the BASE code.)
Files: slug.py, tests/test_slug.py (commit); .sdd/plan mutant files.
Concerns: none. Leading/trailing whitespace yields edge hyphens (spec silent; pinned by a test).
