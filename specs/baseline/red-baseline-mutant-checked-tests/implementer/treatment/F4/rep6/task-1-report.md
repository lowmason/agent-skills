# Task 1 report
Implemented `summarize` in monthly.py (prefix filter on `YYYY-MM-`, raises ValueError('no rows') when empty).
TDD: RED = ImportError for `summarize`; GREEN = 2 passed. Added 3 strengthening tests (empty rows, same month other year, one-row month); 5 tests pass.
Mutants: run .sdd/plan/task-1-mutants-2.log, caught 6, survived 0, invalid 0 (first run had 1 survivor, fixed by one-row test).
Concern: spec specs/monthly.md:7 says message `no rows for <month>`; plan test tests/test_monthly.py `match='^no rows$'`. Plan test kept; code raises 'no rows'. Controller must rule.
Files: monthly.py, tests/test_monthly.py, .sdd/plan/task-1-mutants.md + patches.
