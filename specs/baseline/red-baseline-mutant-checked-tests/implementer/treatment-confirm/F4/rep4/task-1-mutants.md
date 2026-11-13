# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/monthly.md:7 | month with no rows (message pinned by plan test as `no rows`) | test_summarize_rejects_a_month_with_no_rows |
| brief: keeps rows whose date falls in month | rows in and out of month | test_summarize_totals_the_month |
| brief: keeps rows whose date falls in month | same month, other year | test_summarize_ignores_the_same_month_of_another_year |
| brief: keeps rows whose date falls in month | first and last day | test_summarize_includes_first_and_last_day_of_month |
| brief: count and total of kept rows | count, total | test_summarize_totals_the_month |

## Mutants

Mutant 1: brief: filter, test_summarize_ignores_the_same_month_of_another_year — compares month number only, ignoring year — task-1-mutant-1.patch
Mutant 2: brief: count, test_summarize_totals_the_month — count counts all rows — task-1-mutant-2.patch
Mutant 3: brief: total, test_summarize_totals_the_month — total sums all rows — task-1-mutant-3.patch
Mutant 4: specs/monthly.md:7, test_summarize_rejects_a_month_with_no_rows — no error for empty month — task-1-mutant-4.patch
Mutant 5: brief: filter, test_summarize_includes_first_and_last_day_of_month — drops day 30 — task-1-mutant-5.patch
Mutant 6: brief: filter, test_summarize_includes_first_and_last_day_of_month — drops day 01 — task-1-mutant-6.patch
