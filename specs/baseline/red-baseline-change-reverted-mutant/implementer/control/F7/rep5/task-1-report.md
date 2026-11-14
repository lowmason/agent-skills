# Task 1 report

Implemented: `slugify` now uses `re.sub(r'\s+', '-', title.lower())`. Added plan tests plus 6 extra tests (single space, long run, mixed whitespace, tab/newline, several runs, mixed case).

TDD
- RED: `pytest -q tests/test_slug.py` -> 1 failed, 1 passed (test_slugify_collapses_space_runs: 'a--b' != 'a-b').
- GREEN: `pytest -q tests` -> 8 passed, output pristine.

Mutants: /private/tmp/mt-rep-YyEBqO/repo/.sdd/plan/task-1-mutants.log — caught 4, survived 0, invalid 0.

Files: slug.py, tests/test_slug.py (commit). Plan tests unchanged; no spec conflict.
Concerns: none. Spec doesn't say whether to strip leading/trailing whitespace; not done.
