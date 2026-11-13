# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| brief: keeps rows whose date is in month | rows inside (incl. last day) and outside the month | test_summarize_totals_the_month |
| brief: returns month, count, total | normal month | test_summarize_totals_the_month |
| specs/monthly.md:7 | month with no rows (plan test pins message `no rows`) | test_summarize_rejects_a_month_with_no_rows |

## Mutants

Mutant 1: brief: keeps rows in month, test_summarize_totals_the_month — no month filtering — task-1-mutant-1.patch
Mutant 2: specs/monthly.md:7, test_summarize_rejects_a_month_with_no_rows — never raises — task-1-mutant-2.patch
Mutant 3: brief: total of kept rows, test_summarize_totals_the_month — total sums all rows — task-1-mutant-3.patch
Mutant 4: plan test message `^no rows$`, test_summarize_rejects_a_month_with_no_rows — message gains ` for <month>` — task-1-mutant-4.patch
