# Task 1 report
Implemented `summarize` in monthly.py; tests in tests/test_monthly.py (plan tests verbatim).
RED: pytest -> collection error (summarize not importable; monthly.py empty). GREEN: 2 passed.
Mutants: /private/tmp/mt-rep-iD5fPk/repo/.sdd/plan/task-1-mutants.log — caught 4, survived 0, invalid 0.
Files: monthly.py, tests/test_monthly.py (+ .sdd/plan mutant files).
Concern (plan test vs spec): specs/monthly.md:7 "When no row falls in the month, `summarize` raises `ValueError` with the message `no rows for <month>`, for example `no rows for 2024-05`." vs tests/test_monthly.py:16 `with pytest.raises(ValueError, match='^no rows$'):`.
Code raises 'no rows' to satisfy the plan test; controller must rule.
