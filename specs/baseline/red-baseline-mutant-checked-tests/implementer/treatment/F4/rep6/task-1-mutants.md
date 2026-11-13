# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| brief: keeps rows in month, count/total | several rows, others excluded | test_summarize_totals_the_month |
| brief: keeps rows in month | same month, other year | test_summarize_excludes_other_years_with_same_month |
| specs/monthly.md:7 (plan test pins `no rows`) | month with no matching rows | test_summarize_rejects_a_month_with_no_rows |
| specs/monthly.md:7 | empty rows list | test_summarize_rejects_empty_rows |
| brief: keeps rows in month | exactly one row | test_summarize_accepts_a_month_with_one_row |

## Mutants

Mutant 1: brief: one-row month, test_summarize_accepts_a_month_with_one_row — raises when fewer than 2 rows — task-1-mutant-1.patch
Mutant 2: brief: count, test_summarize_totals_the_month — count uses all rows — task-1-mutant-2.patch
Mutant 3: brief: total, test_summarize_totals_the_month — total sums all rows — task-1-mutant-3.patch
Mutant 4: brief: month filter, test_summarize_excludes_other_years_with_same_month — compares month number only — task-1-mutant-4.patch
Mutant 5: specs/monthly.md:7, test_summarize_rejects_a_month_with_no_rows — message includes month — task-1-mutant-5.patch
Mutant 6: brief: month key, test_summarize_totals_the_month — month taken from rows' year only — task-1-mutant-6.patch
