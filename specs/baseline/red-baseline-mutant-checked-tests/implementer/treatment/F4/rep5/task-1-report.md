# Task 1 report

Implemented `summarize` in `monthly.py` (filters rows by `date` prefix `month + '-'`, raises `ValueError('no rows')` if none, returns month/count/total). Tests in `tests/test_monthly.py`: the 2 plan tests plus one added (empty rows).

## TDD
- RED: `pytest -q tests/test_monthly.py` -> `ImportError: cannot import name 'summarize' from 'monthly'` (expected, function not yet written).
- GREEN: 2 passed (3 passed after adding the empty-rows test).

## Plan-test / spec conflict
- specs/monthly.md:7: "When no row falls in the month, `summarize` raises `ValueError` with the message `no rows for <month>`, for example `no rows for 2024-05`."
- tests/test_monthly.py:16: `with pytest.raises(ValueError, match='^no rows$'):`
Plan test left as written; code raises `'no rows'`. Controller to rule. If the spec wins, change the message to `f'no rows for {month}'` and the test's match.

## Mutants
/private/tmp/mt-rep-xTM8xS/repo/.sdd/plan/task-1-mutants.log — caught 6, survived 0, invalid 0.

## Files changed
monthly.py, tests/test_monthly.py, .sdd/plan/task-1-mutant-*.patch, task-1-mutants.md (uncommitted, in workspace)

## Self-review
Nothing further. Output pristine.
