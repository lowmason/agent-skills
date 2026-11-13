# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| brief: keep rows whose date falls in month | rows in and out of the month, incl. last day | test_summarize_totals_the_month |
| brief: count and total of kept rows | two kept rows | test_summarize_totals_the_month |
| specs/monthly.md:7 (plan test pins message `no rows`) | month with no rows | test_summarize_rejects_a_month_with_no_rows |

## Mutants

Mutant 1: brief: month filter, test_summarize_totals_the_month — filters by year only — task-1-mutant-1.patch
Mutant 2: brief: count, test_summarize_totals_the_month — count counts all rows — task-1-mutant-2.patch
Mutant 3: brief: total, test_summarize_totals_the_month — total sums all rows — task-1-mutant-3.patch
Mutant 4: specs/monthly.md:7, test_summarize_rejects_a_month_with_no_rows — never raises — task-1-mutant-4.patch
