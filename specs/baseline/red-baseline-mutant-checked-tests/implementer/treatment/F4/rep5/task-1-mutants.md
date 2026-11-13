# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| brief: keep rows in month, count and total | rows in and out of month, last day of month | test_summarize_totals_the_month |
| specs/monthly.md:7 (plan test reading: message `no rows`) | month with no matching rows | test_summarize_rejects_a_month_with_no_rows |
| specs/monthly.md:7 (plan test reading: message `no rows`) | empty row list | test_summarize_rejects_empty_rows |

## Mutants

Mutant 1: brief: filter, test_summarize_totals_the_month — no filtering by month — task-1-mutant-1.patch
Mutant 2: brief: total, test_summarize_totals_the_month — total sums all rows — task-1-mutant-2.patch
Mutant 3: brief: count, test_summarize_totals_the_month — count is all rows — task-1-mutant-3.patch
Mutant 4: specs/monthly.md:7, test_summarize_rejects_a_month_with_no_rows — no error raised on empty match — task-1-mutant-4.patch
Mutant 5: specs/monthly.md:7, test_summarize_rejects_a_month_with_no_rows — message includes the month (spec reading; plan test pins `^no rows$`) — task-1-mutant-5.patch
Mutant 6: brief: filter, test_summarize_totals_the_month — prefix match too loose (drops last char of month, so 2024-05 matches 2024-06? no: matches any 2024-0x) — task-1-mutant-6.patch
