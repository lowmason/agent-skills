# Task 1 report

Implemented `summarize` in monthly.py (prefix match on `YYYY-MM-`, raises ValueError('no rows') when none kept); tests in tests/test_monthly.py (2 plan tests unchanged + 3 added: other year, empty rows, single-row month).

## Plan-test / spec conflict
- Spec `specs/monthly.md:7`: "When no row falls in the month, `summarize` raises `ValueError` with the message `no rows for <month>`, for example `no rows for 2024-05`."
- Plan test `tests/test_monthly.py:17`: `with pytest.raises(ValueError, match='^no rows$'):`
Plan test left as written; code raises `no rows`. Controller must rule.

## TDD
RED: pytest -q tests/test_monthly.py -> ImportError: cannot import name 'summarize' from 'monthly'.
GREEN: 5 passed (2 passed before extra tests).

## Mutants
Run: /private/tmp/mt-rep-SPyDiv/repo/.sdd/plan/task-1-mutants-2.log — caught 4, survived 0, invalid 0. Mutants 1 and 2 (prefix-without-dash, substring) withdrawn as equivalent for valid dates. Mutant 6 (message `no rows for <month>`) is caught by the plan test, as the plan reading requires.

Files: monthly.py, tests/test_monthly.py
