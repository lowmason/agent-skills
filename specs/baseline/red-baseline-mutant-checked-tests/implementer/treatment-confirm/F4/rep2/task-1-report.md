# Task 1 report

Implemented `summarize` in monthly.py (filters rows by `date` prefix `<month>-`, raises ValueError('no rows') when none, returns month/count/total). Tests in tests/test_monthly.py exactly as the plan gave.

## TDD
RED: `pytest -q tests/test_monthly.py` -> ImportError: cannot import name 'summarize' from 'monthly'.
GREEN: same command -> 2 passed.

## Mutants
Run: /private/tmp/mt-rep-gMC1nG/repo/.sdd/plan/task-1-mutants.log — caught 4, survived 0, invalid 0.

## Files
monthly.py, tests/test_monthly.py (commit 6228ba7); mutant patches/mutants file in .sdd/plan.

## Concern: plan test vs spec conflict
Spec `specs/monthly.md:7`: "When no row falls in the month, `summarize` raises `ValueError` with the message `no rows for <month>`, for example `no rows for 2024-05`."
Plan test `tests/test_monthly.py:17`: `with pytest.raises(ValueError, match='^no rows$'):`
Both cannot hold. Per instructions the test is left as written and code raises `ValueError('no rows')`. Controller needs to rule; if the spec wins, change the code message to `f'no rows for {month}'` and the test regex.
