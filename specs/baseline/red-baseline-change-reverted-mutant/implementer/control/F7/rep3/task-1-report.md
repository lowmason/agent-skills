# Task 1 report
Implemented: `slugify` now uses `re.sub(r'\s+', '-', title.lower())`. Plan tests kept verbatim; added 5 tests (single space, mixed whitespace, tab/newline, runs at ends, several runs).
RED: `pytest -q tests/test_slug.py` -> 1 failed, 1 passed (`'a--b'` != `'a-b'`), as expected.
GREEN: 7 passed.
Mutants: /private/tmp/mt-rep-5aBkRb/repo/.sdd/plan/task-1-mutants.log — caught 4, survived 0, invalid 0.
Files: slug.py, tests/test_slug.py (committed); mutant files in .sdd/plan.
Concerns: none.
