# Task 1 report

Implemented `summarize` in monthly.py; tests in tests/test_monthly.py (2 plan tests unchanged + 2 added: other-year same month, empty rows).

TDD: RED = `ImportError: cannot import name 'summarize' from 'monthly'` (collection error, expected: monthly.py empty). GREEN = `2 passed`; later 4 passed.

Mutants: /private/tmp/mt-rep-1RRkVc/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.

Files: monthly.py, tests/test_monthly.py (+ .sdd/plan mutant files).

CONCERN (plan test vs spec):
- Spec specs/monthly.md:7: "When no row falls in the month, `summarize` raises `ValueError` with the message `no rows for <month>`, for example `no rows for 2024-05`."
- Plan test tests/test_monthly.py (test_summarize_rejects_a_month_with_no_rows): `with pytest.raises(ValueError, match='^no rows$'):`
Both cannot hold. Test left as written; code raises `ValueError('no rows')`. Controller to rule. My added empty-list test also pins '^no rows$' following the plan reading.
