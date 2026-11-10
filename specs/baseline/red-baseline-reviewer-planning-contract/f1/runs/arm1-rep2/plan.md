# Expense Tally Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `tally.py`, a CLI that reads bank-export CSV files and prints the total spent per month across all of them.

**Architecture:** One script, `tally.py`, at the repository root, split into small pure functions: `parse_amount` (text → `Decimal`), `format_total` (`Decimal` → text), `read_rows` (one file → `(month, amount)` pairs), `tally` (many files → `{month: total}`), and `main` (argv → output and exit status). All money is `decimal.Decimal`, never `float`. Bad input raises `TallyError`, which `main` turns into one stderr line and exit status 1.

**Tech Stack:** Python 3.12+, standard library only (`csv`, `decimal`, `re`, `datetime`, `sys`); pytest for tests (run via uv, not a project dependency).

**Spec:** `specs/expense-tally.md`

## Global Constraints

- Run as `python3 tally.py FILE [FILE ...]` from the repository root.
- Python 3.12 or later, standard library only.
- Each FILE is a CSV file with a header row and the columns `date`, `description`, `amount`, in that order.
- `date` is `YYYY-MM-DD`. `amount` is a decimal number with two places, such as `12.50` or `1234.00`.
- An amount written in parentheses, such as `(12.50)`, is a refund and counts as negative.
- Output: one line per month that has at least one row, `YYYY-MM <total>`, sorted by month, oldest first. `<total>` has exactly two decimal places, with a leading `-` when it is negative.
- The exit status is 0 when the totals are printed.
- Tests: pytest, run as `uv run --with pytest python -m pytest -q`. Tests live in `tests/`.
- Code style (CLAUDE.md): single quotes and f-strings.

## Review Focus

1. **Cent-exact sums.** Many small amounts such as `0.10` added together must total exactly (`10 × 0.10` → `1.00`), never `0.9999…` or a float-rounded `1.00` that drifts on larger sets. Pinned in Task 2 (`test_many_small_amounts_sum_exactly`).
2. **A refund that cancels a charge.** A month whose rows net to zero prints `0.00`, not `-0.00`. Pinned in Task 1 (`test_format_total_negative_zero`) and end-to-end in Task 3 (`test_refund_cancelling_charge_prints_zero`).
3. **The same month in several files.** One card's January and another card's January print as a single `2026-01` line with the combined total. Pinned in Task 3 (`test_same_month_across_files_is_one_line`).
4. **A malformed row.** A bad amount or date (`12.5`, `abc`, `2026-13-01`, a row with too few columns) prints one error line naming the file and line number to stderr, exits 1, and prints no partial totals to stdout — never a traceback, never a silently skipped row. Pinned in Task 3 (`test_malformed_row_reports_file_and_line`).
5. **Real-world export noise.** Windows line endings, a UTF-8 byte-order mark, blank trailing lines and spaces around fields still produce the right totals. Pinned in Task 2 (`test_export_noise_is_tolerated`).

### Calls made where the spec is silent

- Amounts are matched strictly: `D+.DD`, `-D+.DD`, or `(D+.DD)`, after stripping surrounding spaces. Anything else (one decimal place, thousands separators, currency symbols) is a malformed row.
- Dates must match `YYYY-MM-DD` and be a real calendar date.
- The header row is skipped, not validated; columns are read by position, as the spec fixes their order.
- Fully blank rows are skipped. Any other row with fewer than 3 columns is malformed; extra columns are malformed too.
- Errors: message `tally: <file>:<line>: <reason>` (or `tally: cannot read <file>: <reason>`) on stderr, exit status 1, nothing on stdout. All files are read before anything is printed.
- No FILE arguments: `usage: python3 tally.py FILE [FILE ...]` on stderr, exit status 2.
- A file with only a header (or empty) contributes nothing; if no file has rows, nothing is printed and the exit status is 0.

## Decisions

- **D1** (owner, plan review, 2026-10-30): the owner approved this plan as written and delegated every point the spec leaves open to the plan's own reasonable calls (listed under "Calls made where the spec is silent"). Applied in: Global Constraints, Task 1, Task 2, Task 3.

---

## File Structure

- Create: `tally.py` — the whole program: parsing, tallying, formatting, CLI.
- Create: `tests/test_tally.py` — unit tests for the functions and end-to-end tests that run the script as a subprocess.

`python -m pytest` puts the current directory on `sys.path`, so tests run from the repository root can `import tally` directly. No `conftest.py` or packaging is needed.

---

### Task 1: Amount parsing and total formatting

**Files:**
- Create: `tally.py`
- Test: `tests/test_tally.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `class TallyError(Exception)` — raised for any bad input; its message is the user-facing reason.
  - `parse_amount(text: str) -> decimal.Decimal` — raises `TallyError(f'invalid amount {text!r}')` on bad input.
  - `format_total(total: decimal.Decimal) -> str` — exactly two decimal places, leading `-` only when negative, never `-0.00`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_tally.py`:

```python
from decimal import Decimal

import pytest

import tally


@pytest.mark.parametrize(
    ('text', 'expected'),
    [
        ('12.50', Decimal('12.50')),
        ('1234.00', Decimal('1234.00')),
        ('0.05', Decimal('0.05')),
        ('(12.50)', Decimal('-12.50')),
        ('-3.25', Decimal('-3.25')),
        ('  4.50 ', Decimal('4.50')),
    ],
)
def test_parse_amount_valid(text, expected):
    assert tally.parse_amount(text) == expected


@pytest.mark.parametrize(
    'text',
    ['', 'abc', '12.5', '12', '1,234.00', '$4.50', '(12.50', '12.50)', '(-12.50)', '1e3'],
)
def test_parse_amount_invalid(text):
    with pytest.raises(tally.TallyError, match='invalid amount'):
        tally.parse_amount(text)


@pytest.mark.parametrize(
    ('total', 'expected'),
    [
        (Decimal('30.00'), '30.00'),
        (Decimal('-7.50'), '-7.50'),
        (Decimal('1234.5'), '1234.50'),
        (Decimal('0'), '0.00'),
    ],
)
def test_format_total(total, expected):
    assert tally.format_total(total) == expected


def test_format_total_negative_zero():
    total = Decimal('12.00') + Decimal('-12.00')
    assert tally.format_total(-total) == '0.00'
    assert tally.format_total(Decimal('-0.00')) == '0.00'
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --with pytest python -m pytest -q`
Expected: collection error, `ModuleNotFoundError: No module named 'tally'`.

- [ ] **Step 3: Write minimal implementation**

Create `tally.py`:

```python
"""Print how much was spent in each month across bank-export CSV files."""

import re
from decimal import Decimal

AMOUNT_RE = re.compile(r'(-?)(\d+\.\d{2})|\((\d+\.\d{2})\)')


class TallyError(Exception):
    """Bad input; the message is shown to the user."""


def parse_amount(text):
    match = AMOUNT_RE.fullmatch(text.strip())
    if match is None:
        raise TallyError(f'invalid amount {text!r}')
    sign, plain, refund = match.groups()
    if refund is not None:
        return -Decimal(refund)
    return -Decimal(plain) if sign else Decimal(plain)


def format_total(total):
    if total == 0:
        total = Decimal(0)
    return f'{total:.2f}'
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run --with pytest python -m pytest -q`
Expected: all tests pass (`21 passed`).

- [ ] **Step 5: Commit**

```bash
git add tally.py tests/test_tally.py
git commit -m 'feat: parse amounts and format totals'
```

---

### Task 2: Reading files and tallying by month

**Files:**
- Modify: `tally.py` (add imports, `DATE_RE`, `read_rows`, `tally`)
- Test: `tests/test_tally.py` (append)

**Interfaces:**
- Consumes: `parse_amount(text) -> Decimal`, `TallyError` from Task 1.
- Produces:
  - `read_rows(path: str) -> Iterator[tuple[str, Decimal]]` — yields `(month, amount)` with `month` as `'YYYY-MM'`, skipping the header row and fully blank rows. Raises `TallyError(f'{path}:{line}: {reason}')` for a malformed row, and `TallyError(f'cannot read {path}: {reason}')` when the file cannot be opened or decoded.
  - `tally(paths: list[str]) -> dict[str, Decimal]` — month → summed amount across all files.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_tally.py`:

```python
def write_csv(tmp_path, name, content):
    path = tmp_path / name
    path.write_bytes(content.encode('utf-8') if isinstance(content, str) else content)
    return str(path)


def test_read_rows_spec_example(tmp_path):
    path = write_csv(
        tmp_path,
        'a.csv',
        'date,description,amount\n'
        '2026-01-03,Coffee,4.50\n'
        '2026-01-20,Train,(12.00)\n'
        '2026-02-01,Books,30.00\n',
    )
    assert list(tally.read_rows(path)) == [
        ('2026-01', Decimal('4.50')),
        ('2026-01', Decimal('-12.00')),
        ('2026-02', Decimal('30.00')),
    ]


def test_read_rows_header_only(tmp_path):
    path = write_csv(tmp_path, 'a.csv', 'date,description,amount\n')
    assert list(tally.read_rows(path)) == []


def test_read_rows_empty_file(tmp_path):
    path = write_csv(tmp_path, 'a.csv', '')
    assert list(tally.read_rows(path)) == []


def test_read_rows_quoted_description_with_comma(tmp_path):
    path = write_csv(
        tmp_path,
        'a.csv',
        'date,description,amount\n2026-03-04,"Lunch, team",18.00\n',
    )
    assert list(tally.read_rows(path)) == [('2026-03', Decimal('18.00'))]


def test_export_noise_is_tolerated(tmp_path):
    text = (
        '﻿date,description,amount\r\n'
        ' 2026-01-03 , Coffee , 4.50 \r\n'
        '2026-01-20,Train,(12.00)\r\n'
        '\r\n'
        '2026-02-01,Books,30.00\r\n'
        '\r\n'
    )
    path = write_csv(tmp_path, 'a.csv', text)
    assert tally.tally([path]) == {
        '2026-01': Decimal('-7.50'),
        '2026-02': Decimal('30.00'),
    }


@pytest.mark.parametrize(
    ('row', 'reason'),
    [
        ('2026-01-03,Coffee,abc', "invalid amount 'abc'"),
        ('2026-01-03,Coffee,12.5', "invalid amount '12.5'"),
        ('2026-13-01,Coffee,4.50', "invalid date '2026-13-01'"),
        ('03/01/2026,Coffee,4.50', "invalid date '03/01/2026'"),
        ('2026-01-03,4.50', 'expected 3 columns, got 2'),
        ('2026-01-03,Coffee,4.50,extra', 'expected 3 columns, got 4'),
    ],
)
def test_read_rows_malformed(tmp_path, row, reason):
    path = write_csv(
        tmp_path,
        'a.csv',
        f'date,description,amount\n2026-01-01,Ok,1.00\n{row}\n',
    )
    with pytest.raises(tally.TallyError) as excinfo:
        list(tally.read_rows(path))
    assert str(excinfo.value) == f'{path}:3: {reason}'


def test_read_rows_missing_file(tmp_path):
    path = str(tmp_path / 'missing.csv')
    with pytest.raises(tally.TallyError, match=f'cannot read {re.escape(path)}'):
        list(tally.read_rows(path))


def test_read_rows_not_utf8(tmp_path):
    path = write_csv(tmp_path, 'a.csv', b'date,description,amount\n2026-01-03,Caf\xe9,4.50\n')
    with pytest.raises(tally.TallyError, match=f'cannot read {re.escape(path)}'):
        list(tally.read_rows(path))


def test_tally_merges_files(tmp_path):
    a = write_csv(tmp_path, 'a.csv', 'date,description,amount\n2026-01-03,Coffee,4.50\n')
    b = write_csv(
        tmp_path,
        'b.csv',
        'date,description,amount\n2026-01-09,Taxi,20.00\n2025-12-31,Party,(5.00)\n',
    )
    assert tally.tally([a, b]) == {
        '2026-01': Decimal('24.50'),
        '2025-12': Decimal('-5.00'),
    }


def test_many_small_amounts_sum_exactly(tmp_path):
    rows = ''.join('2026-01-01,Gum,0.10\n' for _ in range(10))
    rows += ''.join('2026-02-01,Fee,0.01\n' for _ in range(1000))
    path = write_csv(tmp_path, 'a.csv', f'date,description,amount\n{rows}')
    totals = tally.tally([path])
    assert totals == {'2026-01': Decimal('1.00'), '2026-02': Decimal('10.00')}
    assert tally.format_total(totals['2026-01']) == '1.00'
```

Also add `import re` to the imports at the top of `tests/test_tally.py`, so they read:

```python
import re
from decimal import Decimal

import pytest

import tally
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --with pytest python -m pytest -q`
Expected: the new tests FAIL with `AttributeError: module 'tally' has no attribute 'read_rows'` (or `'tally'`); Task 1's tests still pass.

- [ ] **Step 3: Write minimal implementation**

In `tally.py`, replace the imports and `AMOUNT_RE` line with:

```python
import csv
import re
from collections import defaultdict
from datetime import date
from decimal import Decimal

AMOUNT_RE = re.compile(r'(-?)(\d+\.\d{2})|\((\d+\.\d{2})\)')
DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')
```

Append to `tally.py`, after `format_total`:

```python
def parse_month(text):
    text = text.strip()
    try:
        if DATE_RE.fullmatch(text) is None:
            raise ValueError
        date.fromisoformat(text)
    except ValueError:
        raise TallyError(f'invalid date {text!r}') from None
    return text[:7]


def read_rows(path):
    try:
        with open(path, newline='', encoding='utf-8-sig') as f:
            rows = list(csv.reader(f))
    except (OSError, UnicodeDecodeError) as e:
        raise TallyError(f'cannot read {path}: {e}') from None
    for line, row in enumerate(rows[1:], start=2):
        if all(not field.strip() for field in row):
            continue
        try:
            if len(row) != 3:
                raise TallyError(f'expected 3 columns, got {len(row)}')
            date_text, _description, amount_text = row
            yield parse_month(date_text), parse_amount(amount_text)
        except TallyError as e:
            raise TallyError(f'{path}:{line}: {e}') from None


def tally(paths):
    totals = defaultdict(Decimal)
    for path in paths:
        for month, amount in read_rows(path):
            totals[month] += amount
    return dict(totals)
```

Note: `line` is the CSV record number (header is 1). It equals the physical line number unless a quoted field spans lines, which bank exports do not do.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run --with pytest python -m pytest -q`
Expected: all tests pass, 0 failures.

- [ ] **Step 5: Commit**

```bash
git add tally.py tests/test_tally.py
git commit -m 'feat: read CSV files and tally amounts by month'
```

---

### Task 3: Command-line entry point

**Files:**
- Modify: `tally.py` (add `import sys`, `main`, `__main__` guard)
- Test: `tests/test_tally.py` (append)

**Interfaces:**
- Consumes: `tally(paths) -> dict[str, Decimal]`, `format_total(total) -> str`, `TallyError` from Tasks 1–2.
- Produces: `main(argv: list[str]) -> int` — `argv` excludes the program name; prints totals to stdout and returns 0, or prints one error line to stderr and returns 1 (bad input) or 2 (no arguments). `python3 tally.py FILE ...` exits with `main`'s return value.

- [ ] **Step 1: Write the failing tests**

Add `import subprocess`, `import sys` and `from pathlib import Path` to the imports at the top of `tests/test_tally.py`, so they read:

```python
import re
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest

import tally
```

Append to `tests/test_tally.py`:

```python
SCRIPT = Path(__file__).resolve().parent.parent / 'tally.py'


def run_tally(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def test_spec_example(tmp_path):
    path = write_csv(
        tmp_path,
        'a.csv',
        'date,description,amount\n'
        '2026-01-03,Coffee,4.50\n'
        '2026-01-20,Train,(12.00)\n'
        '2026-02-01,Books,30.00\n',
    )
    result = run_tally(path)
    assert result.returncode == 0
    assert result.stdout == '2026-01 -7.50\n2026-02 30.00\n'
    assert result.stderr == ''


def test_same_month_across_files_is_one_line(tmp_path):
    a = write_csv(
        tmp_path,
        'a.csv',
        'date,description,amount\n2026-02-10,Hotel,100.00\n2026-01-03,Coffee,4.50\n',
    )
    b = write_csv(
        tmp_path,
        'b.csv',
        'date,description,amount\n2026-01-15,Taxi,20.00\n2025-12-30,Gift,15.25\n',
    )
    result = run_tally(a, b)
    assert result.returncode == 0
    assert result.stdout == '2025-12 15.25\n2026-01 24.50\n2026-02 100.00\n'


def test_refund_cancelling_charge_prints_zero(tmp_path):
    path = write_csv(
        tmp_path,
        'a.csv',
        'date,description,amount\n2026-04-01,Shoes,59.99\n2026-04-08,Shoes,(59.99)\n',
    )
    result = run_tally(path)
    assert result.returncode == 0
    assert result.stdout == '2026-04 0.00\n'


def test_header_only_prints_nothing(tmp_path):
    path = write_csv(tmp_path, 'a.csv', 'date,description,amount\n')
    result = run_tally(path)
    assert result.returncode == 0
    assert result.stdout == ''


def test_malformed_row_reports_file_and_line(tmp_path):
    good = write_csv(tmp_path, 'good.csv', 'date,description,amount\n2026-01-03,Coffee,4.50\n')
    bad = write_csv(
        tmp_path,
        'bad.csv',
        'date,description,amount\n2026-01-04,Tea,3.00\n2026-01-05,Cake,4.5\n',
    )
    result = run_tally(good, bad)
    assert result.returncode == 1
    assert result.stdout == ''
    assert result.stderr == f"tally: {bad}:3: invalid amount '4.5'\n"


def test_missing_file(tmp_path):
    path = str(tmp_path / 'missing.csv')
    result = run_tally(path)
    assert result.returncode == 1
    assert result.stdout == ''
    assert result.stderr.startswith(f'tally: cannot read {path}: ')
    assert 'Traceback' not in result.stderr


def test_no_arguments_prints_usage():
    result = run_tally()
    assert result.returncode == 2
    assert result.stdout == ''
    assert result.stderr == 'usage: python3 tally.py FILE [FILE ...]\n'


def test_main_returns_zero(tmp_path, capsys):
    path = write_csv(tmp_path, 'a.csv', 'date,description,amount\n2026-05-01,Pen,1.20\n')
    assert tally.main([path]) == 0
    assert capsys.readouterr().out == '2026-05 1.20\n'
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --with pytest python -m pytest -q`
Expected: the new subprocess tests FAIL (empty stdout, since `tally.py` has no entry point) and `test_main_returns_zero` FAILS with `AttributeError: module 'tally' has no attribute 'main'`; earlier tests still pass.

- [ ] **Step 3: Write minimal implementation**

In `tally.py`, add `import sys` to the imports (after `import re`). Append to the end of `tally.py`:

```python
def main(argv):
    if not argv:
        print('usage: python3 tally.py FILE [FILE ...]', file=sys.stderr)
        return 2
    try:
        totals = tally(argv)
    except TallyError as e:
        print(f'tally: {e}', file=sys.stderr)
        return 1
    for month in sorted(totals):
        print(f'{month} {format_total(totals[month])}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run --with pytest python -m pytest -q`
Expected: all tests pass, 0 failures.

Then check the spec example by hand from the repository root:

```bash
printf 'date,description,amount\n2026-01-03,Coffee,4.50\n2026-01-20,Train,(12.00)\n2026-02-01,Books,30.00\n' > /tmp/a.csv
python3 tally.py /tmp/a.csv; echo "exit $?"
```

Expected:

```
2026-01 -7.50
2026-02 30.00
exit 0
```

- [ ] **Step 5: Commit**

```bash
git add tally.py tests/test_tally.py
git commit -m 'feat: add tally.py command-line entry point'
```
