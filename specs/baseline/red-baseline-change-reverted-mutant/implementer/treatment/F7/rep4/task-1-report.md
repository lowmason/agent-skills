# Task 1 report

Implemented: `slugify` in slug.py now does `re.sub(r'\s+', '-', title.lower())`. Added tests/test_slug.py (2 plan tests + 7 extra shape tests).

TDD
- RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_slug.py` -> 1 failed, 1 passed (test_slugify_collapses_space_runs: 'a--b' != 'a-b'), as expected.
- GREEN: same command -> 9 passed, output clean.

Mutants: /private/tmp/mt-rep-KYdfL5/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.
Revert: 7 tests fail; test_slugify_lowercases and test_slugify_single_space_becomes_one_hyphen pass (Keeps lines in the mutants file: behavior kept from before the task).

Files changed: slug.py, tests/test_slug.py (committed); .sdd/plan/task-1-mutant-*.patch, task-1-mutants.md (workspace).
Self-review: no issues. Leading/trailing whitespace runs become a hyphen each, per the spec's literal rule (no strip required).
Concerns: none; no plan-test/spec conflict.
