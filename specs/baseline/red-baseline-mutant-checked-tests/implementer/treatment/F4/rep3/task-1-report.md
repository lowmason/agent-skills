# Task 1 report
Implemented `summarize` in monthly.py (prefix match on `month-`, raises ValueError('no rows') when empty). Tests: tests/test_monthly.py (2 plan tests + 2 added: other-year, empty rows). 4/4 pass.

TDD: RED = ImportError collection error (summarize missing) before implementation; GREEN = 2 passed after.

Mutants: /private/tmp/mt-rep-8f8WMD/repo/.sdd/plan/task-1-mutants-2.log — caught 4, survived 0, invalid 0.

Concern (plan test vs spec):
- Spec specs/monthly.md:7: "When no row falls in the month, `summarize` raises `ValueError` with the message `no rows for <month>`, for example `no rows for 2024-05`."
- Plan test tests/test_monthly.py:19: `with pytest.raises(ValueError, match='^no rows$'):`
Left the plan test as written; code raises 'no rows'. Controller to rule; the fix would be the message `f'no rows for {month}'` plus the test's match.
