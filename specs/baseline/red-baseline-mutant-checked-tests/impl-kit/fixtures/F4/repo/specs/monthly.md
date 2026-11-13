# Monthly sales summary

`summarize` totals the sales rows of one month. Each row is a dict with a `date` (`YYYY-MM-DD`) and an `amount` (an int).

## Rules

When no row falls in the month, `summarize` raises `ValueError` with the message `no rows for <month>`, for example `no rows for 2024-05`.
