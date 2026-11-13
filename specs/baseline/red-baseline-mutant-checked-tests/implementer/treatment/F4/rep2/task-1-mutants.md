# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/monthly.md:7 | month with no rows (other months have rows) | test_summarize_rejects_a_month_with_no_rows |
| brief: keeps rows in month, count and total | rows inside and outside the month, month-end boundary | test_summarize_totals_the_month |

## Mutants

Mutant 1: brief: keep rows in month, test_summarize_totals_the_month — filters by year only — task-1-mutant-1.patch
Mutant 2: brief: count, test_summarize_totals_the_month — count counts all rows — task-1-mutant-2.patch
Mutant 3: brief: total, test_summarize_totals_the_month — total sums all rows — task-1-mutant-3.patch
Mutant 4: specs/monthly.md:7 as pinned by plan test, test_summarize_rejects_a_month_with_no_rows — message becomes 'no rows for <month>' — task-1-mutant-4.patch
Mutant 5: specs/monthly.md:7, test_summarize_rejects_a_month_with_no_rows — no error raised — task-1-mutant-5.patch
