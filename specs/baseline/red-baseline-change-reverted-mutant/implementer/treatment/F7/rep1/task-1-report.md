# Task 1 report

## Implemented
`slug.py`: `slugify` now returns `re.sub(r'\s+', '-', title.lower())`, so each whitespace run becomes one hyphen (specs/slugs.md:7) and letters are lowercased (:8).
Added tests/test_slug.py: the 2 plan tests unchanged, plus 7 extra tests for single space, long run, mixed whitespace, tab/newline, several runs, leading/trailing runs, lowercase across whitespace.

## TDD
RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_slug.py` -> `1 failed, 1 passed` (test_slugify_collapses_space_runs: 'a--b' != 'a-b'), as expected.
GREEN: same command -> `9 passed`.

## Mutants
Run: /private/tmp/mt-rep-2NSrou/repo/.sdd/plan/task-1-mutants.log
Counts: caught 6, survived 0, invalid 0.
Revert: failed 7, passed 2 (test_slugify_lowercases, test_slugify_single_space_becomes_one_hyphen). Both are `Keeps:` lines in task-1-mutants.md, since both check pre-task behavior the task keeps.

## Files changed
slug.py, tests/test_slug.py (committed); .sdd/plan/task-1-mutant-*.patch, task-1-mutants.md, this report.

## Concerns
None. No plan test conflicts with the spec.
