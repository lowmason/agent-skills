# Expense tally

## Purpose

The team exports its card transactions from the bank as CSV files, one file per card.
`tally.py` prints how much was spent in each month across all the files it is given.

## Interface

- Run as `python3 tally.py FILE [FILE ...]` from the repository root. Python 3.12 or later,
  standard library only.
- Each FILE is a CSV file with a header row and the columns `date`, `description`, `amount`,
  in that order.
- `date` is `YYYY-MM-DD`. `amount` is a decimal number with two places, such as `12.50` or
  `1234.00`.
- An amount written in parentheses, such as `(12.50)`, is a refund and counts as negative.
- The output is one line per month that has at least one row, `YYYY-MM <total>`, sorted by
  month, oldest first. `<total>` has exactly two decimal places, with a leading `-` when it is
  negative.
- The exit status is 0 when the totals are printed.

## Example

Given `a.csv`:

    date,description,amount
    2026-01-03,Coffee,4.50
    2026-01-20,Train,(12.00)
    2026-02-01,Books,30.00

`python3 tally.py a.csv` prints:

    2026-01 -7.50
    2026-02 30.00

## Tests

pytest, run as `uv run --with pytest python -m pytest -q`. Tests live in `tests/`.
