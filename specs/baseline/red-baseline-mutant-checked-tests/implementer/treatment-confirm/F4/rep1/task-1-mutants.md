# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| brief: keeps rows whose date falls in month | rows at month start/end, other month | test_summarize_totals_the_month |
| brief: keeps rows whose date falls in month | same month, other year | test_summarize_ignores_the_same_month_of_another_year |
| brief: count and total of kept rows | single row | test_summarize_counts_a_single_row_month |
| specs/monthly.md:7 | month with no rows (plan test pins message `no rows`) | test_summarize_rejects_a_month_with_no_rows |
| specs/monthly.md:7 | empty rows list | test_summarize_rejects_empty_rows |

## Mutants

Mutant 3: specs/monthly.md:7; test_summarize_rejects_empty_rows, test_summarize_rejects_a_month_with_no_rows — never raise — task-1-mutant-3.patch
Mutant 4: brief: count; test_summarize_totals_the_month — count all rows — task-1-mutant-4.patch
Mutant 5: brief: total; test_summarize_totals_the_month — sum all rows — task-1-mutant-5.patch
Mutant 6: specs/monthly.md:7; test_summarize_rejects_a_month_with_no_rows — message `no rows for <month>` — task-1-mutant-6.patch
Withdrawn: 1 — for a YYYY-MM month and YYYY-MM-DD dates, a prefix match with or without '-' selects identical rows.
Withdrawn: 2 — a valid date contains the 7-char YYYY-MM only at its start (the day field is 2 digits), so substring and prefix select identical rows.
