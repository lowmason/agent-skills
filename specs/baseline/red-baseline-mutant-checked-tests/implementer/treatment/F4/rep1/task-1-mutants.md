# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| brief: keeps rows whose date falls in month | rows in month, incl. month-end day | test_summarize_totals_the_month |
| brief: keeps rows whose date falls in month | rows of other months excluded | test_summarize_ignores_rows_of_other_months |
| specs/monthly.md:7 | month with no rows (plan test pins message `no rows`) | test_summarize_rejects_a_month_with_no_rows |

## Mutants

Mutant 1: brief month filter, test_summarize_totals_the_month — date compared with <= instead of == — task-1-mutant-1.patch
Mutant 2: brief total, test_summarize_totals_the_month — total sums all rows — task-1-mutant-2.patch
Mutant 3: brief count, test_summarize_totals_the_month — count counts all rows — task-1-mutant-3.patch
Mutant 4: specs/monthly.md:7, test_summarize_rejects_a_month_with_no_rows — no error raised on empty month — task-1-mutant-4.patch
Mutant 5: brief month filter, test_summarize_ignores_rows_of_other_months — compares only first 6 chars (year+tens digit of month) — task-1-mutant-5.patch
