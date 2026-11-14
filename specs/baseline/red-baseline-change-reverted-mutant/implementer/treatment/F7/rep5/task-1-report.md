# Task 1 report

Implemented: `slugify` now uses `re.sub(r'\s+', '-', title.lower())` (slug.py); added tests/test_slug.py (2 plan tests + 6 extra shape tests: single space, long run, mixed whitespace run, tab/newline, run at edges, lowercase across words).

TDD
- RED: `pytest -q tests/test_slug.py` -> `1 failed, 1 passed` (`assert 'a--b' == 'a-b'`), expected: old code hyphenates each space.
- GREEN: `pytest -q tests` -> `8 passed`.

Mutants: caught 4, survived 0, invalid 0. Run: /private/tmp/mt-rep-aXKjkA/repo/.sdd/plan/task-1-mutants.log
Revert: failed 6, passed 2 (test_slugify_lowercases, test_slugify_single_space — both recorded as Keeps in the mutants file; pre-existing behavior kept).

Commit: "Collapse whitespace runs in slugify". Files: slug.py, tests/test_slug.py (workspace files under .sdd/plan not committed).

Concerns: none. Spec says "run of whitespace becomes one hyphen" and nothing on trimming, so edge runs yield a leading/trailing hyphen (tested as such).
