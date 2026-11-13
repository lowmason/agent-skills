# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| brief: keep rows in month, count and total | month with several rows, last day of month | test_summarize_totals_the_month |
| brief: keep rows in month | same month, other year | test_summarize_ignores_same_month_of_other_year |
| specs/monthly.md:7 (plan test pins message `no rows`) | month with no rows | test_summarize_rejects_a_month_with_no_rows |
| specs/monthly.md:7 | empty input | test_summarize_rejects_empty_rows |

## Mutants

Mutant 1: test_summarize_ignores_same_month_of_other_year — compares only the month digits, ignoring year — task-1-mutant-1.patch
Mutant 2: test_summarize_totals_the_month — total drops the last kept row — task-1-mutant-2.patch
Mutant 3: specs/monthly.md:7, test_summarize_rejects_a_month_with_no_rows — never raises — task-1-mutant-3.patch
Mutant 4: test_summarize_totals_the_month — count uses all rows — task-1-mutant-4.patch
