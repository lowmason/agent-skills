# Task 1 report

Implemented `summarize` in monthly.py; tests in tests/test_monthly.py (2 plan tests verbatim + 2 added).

## Plan test / spec conflict
- specs/monthly.md:7: "When no row falls in the month, `summarize` raises `ValueError` with the message `no rows for <month>`, for example `no rows for 2024-05`."
- tests/test_monthly.py:19: `with pytest.raises(ValueError, match='^no rows$'):`
Code raises `ValueError('no rows')` to pass the plan test. Controller must rule; a ruling to follow the spec means changing the message to `f'no rows for {month}'` and the test's match.

## TDD
RED: pytest -q tests/test_monthly.py -> ImportError: cannot import name 'summarize' (collection error).
GREEN: 2 passed.

## Mutants
Run: /private/tmp/mt-rep-hKnegi/repo/.sdd/plan/task-1-mutants.log — caught 6, survived 0, invalid 0.
Added tests: other-year same month; first/last day boundaries.

Final: 4 passed. Files: monthly.py, tests/test_monthly.py, .sdd/plan mutant files.
