# Task 1 report
Implemented `summarize` in monthly.py (prefix match on `month + '-'`, ValueError('no rows') when empty). Tests: plan's two plus one new (same month, other year).
TDD RED: pytest -> ImportError cannot import name 'summarize'. GREEN: 2 passed; later 3 passed.
Mutants: /tmp/mt-rep-fwpCAC/repo/.sdd/plan/task-1-mutants.log — caught 6, survived 0, invalid 0.
Files: monthly.py, tests/test_monthly.py, .sdd/plan/task-1-mutant*.
CONFLICT: specs/monthly.md:7 "When no row falls in the month, `summarize` raises `ValueError` with the message `no rows for <month>`, for example `no rows for 2024-05`." vs tests/test_monthly.py:16 `with pytest.raises(ValueError, match='^no rows$'):`. Plan test left as written; code raises 'no rows'. Controller must rule.
