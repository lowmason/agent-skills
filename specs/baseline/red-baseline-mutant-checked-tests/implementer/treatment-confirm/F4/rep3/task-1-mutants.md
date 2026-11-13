# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| brief: keep rows whose date is in month | rows in month among others | test_summarize_totals_the_month |
| brief: keep rows whose date is in month | same month, other year | test_summarize_ignores_the_same_month_of_another_year |
| specs/monthly.md:7 | month with no matching rows | test_summarize_rejects_a_month_with_no_rows |
| specs/monthly.md:7 | empty row list | test_summarize_rejects_no_rows_at_all |

## Mutants

Mutant 1: brief: keep rows in month; test_summarize_ignores_the_same_month_of_another_year — filter ignores year — task-1-mutant-1.patch
Mutant 2: brief: count; test_summarize_totals_the_month — count uses all rows — task-1-mutant-2.patch
Mutant 3: brief: total; test_summarize_totals_the_month — total sums all rows — task-1-mutant-3.patch
Mutant 4: specs/monthly.md:7; test_summarize_rejects_a_month_with_no_rows, test_summarize_rejects_no_rows_at_all — never raises — task-1-mutant-4.patch
Mutant 5: brief: month key; test_summarize_totals_the_month — month echoed wrongly — task-1-mutant-5.patch
