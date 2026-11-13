# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| brief: keep rows in month | row in month at start/end, row in other month | test_summarize_totals_the_month |
| brief: keep rows in month | same month, other year | test_summarize_ignores_the_same_month_of_another_year |
| brief: count and total | several rows | test_summarize_totals_the_month |
| specs/monthly.md:7 | month with no rows (plan test pins message `no rows`) | test_summarize_rejects_a_month_with_no_rows |

## Mutants

Mutant 1: brief: keep rows — test_summarize_totals_the_month — no filtering — task-1-mutant-1.patch
Mutant 2: brief: count — test_summarize_totals_the_month — count of all rows — task-1-mutant-2.patch
Mutant 3: brief: keep rows — test_summarize_ignores_the_same_month_of_another_year — compares month number only — task-1-mutant-3.patch
Mutant 4: specs/monthly.md:7 — test_summarize_rejects_a_month_with_no_rows — no error raised — task-1-mutant-4.patch
Mutant 5: specs/monthly.md:7 — test_summarize_rejects_a_month_with_no_rows — message `no rows for <month>` (plan test pins `no rows`) — task-1-mutant-5.patch
Mutant 6: brief: total — test_summarize_totals_the_month — total of first kept row only — task-1-mutant-6.patch
