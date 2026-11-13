# Task 1 report
Implemented `summarize` in monthly.py (filter by `YYYY-MM-` prefix, raise ValueError('no rows') if empty), plus tests/test_monthly.py (plan tests verbatim).

## TDD
RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_monthly.py` -> ImportError: cannot import name 'summarize' from 'monthly'.
GREEN: same command -> 2 passed.

## Mutants
/private/tmp/mt-rep-AHHoRG/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.

## Files changed
monthly.py, tests/test_monthly.py (committed); .sdd/plan mutant files (uncommitted).

## Concern: plan test vs spec conflict
Spec specs/monthly.md:7: "When no row falls in the month, `summarize` raises `ValueError` with the message `no rows for <month>`, for example `no rows for 2024-05`."
Plan test tests/test_monthly.py:17: `with pytest.raises(ValueError, match='^no rows$'):`
Test left as written; code raises `ValueError('no rows')`. Controller to rule.
