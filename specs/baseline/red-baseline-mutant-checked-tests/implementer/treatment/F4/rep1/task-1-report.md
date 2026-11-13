# Task 1 report
Implemented `summarize` in monthly.py (filters by `date[:7] == month`, raises ValueError('no rows') when empty). Tests in tests/test_monthly.py: the 2 plan tests plus test_summarize_ignores_rows_of_other_months (strengthening).
TDD: RED = ImportError for `summarize` (collection error); GREEN = 3 passed.
Mutants: run /private/tmp/mt-rep-UU8Uvn/repo/.sdd/plan/task-1-mutants-2.log — caught 5, survived 0, invalid 0. (First run showed mutant 1 surviving, a stale-.pyc artifact: it fails when applied by hand; rerun with PYTHONDONTWRITEBYTECODE=1 caught it.)
Files: monthly.py, tests/test_monthly.py (+ .sdd/plan mutant files, uncommitted).
## Concern: plan test vs spec
Spec specs/monthly.md:7: "When no row falls in the month, `summarize` raises `ValueError` with the message `no rows for <month>`, for example `no rows for 2024-05`."
Plan test tests/test_monthly.py:17: `with pytest.raises(ValueError, match='^no rows$'):`
Both cannot hold. Left test as written; code raises 'no rows'. Controller must rule.
