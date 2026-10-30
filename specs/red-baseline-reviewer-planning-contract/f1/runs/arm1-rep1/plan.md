# Expense Tally Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `tally.py`, a standard-library Python script that prints per-month spending totals across one or more bank-exported CSV files.

**Architecture:** One script at the repository root, `tally.py`, made of small pure functions: `parse_amount` turns an amount cell into integer cents, `format_cents` renders cents as a two-decimal string, `read_rows` yields `(month, cents)` pairs from one file, `tally` sums them across files, and `main` prints the sorted result and returns the exit status. Money is held as integer cents throughout, never as `float`, so totals are exact. Input problems raise `TallyError`, which `main` reports on stderr with a non-zero exit before anything is printed.

**Tech Stack:** Python 3.12+, standard library only (`csv`, `re`, `sys`); pytest for tests, run through `uv`.

**Spec:** `specs/expense-tally.md`

## Global Constraints

- Run as `python3 tally.py FILE [FILE ...]` from the repository root.
- Python 3.12 or later, standard library only.
- Each FILE is a CSV file with a header row and the columns `date`, `description`, `amount`, in that order.
- `date` is `YYYY-MM-DD`. `amount` is a decimal number with two places, such as `12.50` or `1234.00`.
- An amount written in parentheses, such as `(12.50)`, is a refund and counts as negative.
- Output is one line per month that has at least one row, `YYYY-MM <total>`, sorted by month, oldest first. `<total>` has exactly two decimal places, with a leading `-` when it is negative.
- The exit status is 0 when the totals are printed.
- Tests live in `tests/` and run with `uv run --with pytest python -m pytest -q`.
- Code style (CLAUDE.md): single quotes and f-strings.

## Defaults settled by this plan

The spec is silent on these; the plan makes the call (owner pre-approved the plan as written, 2026-10-30):

- Columns are read by position, not by header name; the header row is skipped, not validated.
- Files are read as UTF-8 with an optional BOM (`utf-8-sig`), any line ending.
- Blank lines are ignored. A file with only a header contributes nothing.
- Only the forms the spec names are accepted: `12.50` and `(12.50)`; surrounding whitespace is tolerated. Anything else — `-12.50`, `1,234.00`, `12.5`, `$12.50` — is an error, not a guess.
- A month whose total is zero prints `0.00` (never `-0.00`).
- Errors: no FILE arguments → usage on stderr, exit 2. Unreadable file, non-UTF-8 file, wrong column count, bad date or bad amount → `tally: <file>[:<line>]: <problem>` on stderr, exit 1, and nothing on stdout (no partial totals).

## Review Focus

1. **The same month appearing in several card files** — a person expects one line per month with the combined total, not one line per file. Pinned in Task 2 (`test_same_month_across_files_is_combined`).
2. **Many small amounts that do not add up exactly in binary floating point** (`0.10 + 0.20`, ten `0.10`s) — a person expects `0.30` and `1.00`, not `0.31` or `0.99`. Pinned in Task 2 (`test_totals_are_exact`).
3. **A month whose refunds cancel or exceed its spending by a few cents** — a person expects `0.00` and `-0.05`, not `-0.00`, `-0.5` or `0.-5`. Pinned in Task 2 (`test_zero_and_small_negative_totals`).
4. **A bank export saved with a UTF-8 BOM and Windows CRLF line endings** — a person expects the same totals as for a plain file, not a crash or a skipped row. Pinned in Task 2 (`test_bom_and_crlf_export`).
5. **A description containing a comma, quoted per CSV rules** (`"Smith, J"`) — a person expects the row counted normally, not misread as four columns. Pinned in Task 2 (`test_quoted_comma_in_description`).

## Decisions

None.

---

### Task 1: Amount parsing and formatting

**Files:**
- Create: `tally.py`
- Create: `tests/conftest.py`
- Test: `tests/test_amounts.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `tally.parse_amount(text: str) -> int` — cents; parenthesised amounts are negative; raises `ValueError(f'bad amount {text!r}')` on anything else.
  - `tally.format_cents(cents: int) -> str` — e.g. `-750 -> '-7.50'`, `0 -> '0.00'`.
  - `tests/conftest.py` puts the repository root on `sys.path` so tests can `import tally`.

- [ ] **Step 1: Write the conftest and the failing tests**

`tests/conftest.py`:

```python
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
```

`tests/test_amounts.py`:

```python
import pytest

import tally


@pytest.mark.parametrize('text, cents', [
    ('12.50', 1250),
    ('1234.00', 123400),
    ('0.05', 5),
    ('(12.50)', -1250),
    ('(0.05)', -5),
    (' 4.50 ', 450),
])
def test_parse_amount(text, cents):
    assert tally.parse_amount(text) == cents


@pytest.mark.parametrize('text', [
    '', '12', '12.5', '12.500', '-12.50', '1,234.00', '$12.50', '(12.50', '12.50)', 'abc',
])
def test_parse_amount_rejects(text):
    with pytest.raises(ValueError, match='bad amount'):
        tally.parse_amount(text)


@pytest.mark.parametrize('cents, text', [
    (3000, '30.00'),
    (-750, '-7.50'),
    (0, '0.00'),
    (-5, '-0.05'),
    (5, '0.05'),
    (123456789, '1234567.89'),
])
def test_format_cents(cents, text):
    assert tally.format_cents(cents) == text
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run --with pytest python -m pytest -q tests/test_amounts.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'tally'`.

- [ ] **Step 3: Write the minimal implementation**

`tally.py`:

```python
"""Print how much was spent in each month across bank-exported CSV files."""

import re

AMOUNT_RE = re.compile(r'(\()?(\d+)\.(\d{2})(?(1)\))')


def parse_amount(text: str) -> int:
    """Return the amount in cents; an amount in parentheses is a refund."""
    match = AMOUNT_RE.fullmatch(text.strip())
    if match is None:
        raise ValueError(f'bad amount {text!r}')
    cents = int(match[2]) * 100 + int(match[3])
    return -cents if match[1] else cents


def format_cents(cents: int) -> str:
    """Render cents with exactly two decimal places and a leading '-' if negative."""
    sign = '-' if cents < 0 else ''
    whole, part = divmod(abs(cents), 100)
    return f'{sign}{whole}.{part:02d}'
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run --with pytest python -m pytest -q tests/test_amounts.py`
Expected: all pass (22 passed).

- [ ] **Step 5: Commit**

```bash
git add tally.py tests/conftest.py tests/test_amounts.py
git commit -m 'feat: parse and format expense amounts as integer cents' -m 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'
```

---

### Task 2: Read files, tally by month, print

**Files:**
- Modify: `tally.py` (add imports, `read_rows`, `tally`, `main`, `__main__` block)
- Modify: `tests/conftest.py` (add `make_csv` fixture)
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `tally.parse_amount(text: str) -> int`, `tally.format_cents(cents: int) -> str`, `tests/conftest.py::ROOT`.
- Produces:
  - `tally.read_rows(path: str) -> Iterator[tuple[str, int]]` — yields `(month 'YYYY-MM', cents)` per data row.
  - `tally.tally(paths: list[str]) -> dict[str, int]` — month → total cents across all files.
  - `tally.main(argv: list[str]) -> int` — prints totals to stdout, returns exit status.
  - Fixture `make_csv(name: str, body: str | bytes) -> str` — writes `body` verbatim (no newline translation) to `tmp_path / name` and returns the path as a string.

- [ ] **Step 1: Add the fixture and write the failing tests**

Append to `tests/conftest.py`:

```python
import pytest


@pytest.fixture
def make_csv(tmp_path):
    def make(name: str, body: str | bytes) -> str:
        path = tmp_path / name
        if isinstance(body, bytes):
            path.write_bytes(body)
        else:
            path.write_text(body, encoding='utf-8', newline='')
        return str(path)
    return make
```

`tests/test_cli.py`:

```python
import subprocess
import sys

import tally
from conftest import ROOT

HEADER = 'date,description,amount\n'

SPEC_EXAMPLE = (
    HEADER
    + '2026-01-03,Coffee,4.50\n'
    + '2026-01-20,Train,(12.00)\n'
    + '2026-02-01,Books,30.00\n'
)


def run_main(capsys, paths):
    status = tally.main(paths)
    out, err = capsys.readouterr()
    return status, out, err


def test_spec_example(make_csv, capsys):
    path = make_csv('a.csv', SPEC_EXAMPLE)
    status, out, err = run_main(capsys, [path])
    assert status == 0
    assert out == '2026-01 -7.50\n2026-02 30.00\n'
    assert err == ''


def test_spec_example_as_a_script(make_csv):
    path = make_csv('a.csv', SPEC_EXAMPLE)
    result = subprocess.run(
        [sys.executable, 'tally.py', path], cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert result.stdout == '2026-01 -7.50\n2026-02 30.00\n'


def test_same_month_across_files_is_combined(make_csv, capsys):
    a = make_csv('a.csv', HEADER + '2026-03-01,Lunch,10.00\n')
    b = make_csv('b.csv', HEADER + '2026-03-15,Taxi,25.25\n2026-04-02,Hotel,100.00\n')
    status, out, _ = run_main(capsys, [a, b])
    assert status == 0
    assert out == '2026-03 35.25\n2026-04 100.00\n'


def test_months_sorted_oldest_first_across_years(make_csv, capsys):
    path = make_csv('a.csv', HEADER + '2026-01-05,B,2.00\n2025-12-31,A,1.00\n2025-02-01,C,3.00\n')
    _, out, _ = run_main(capsys, [path])
    assert out == '2025-02 3.00\n2025-12 1.00\n2026-01 2.00\n'


def test_totals_are_exact(make_csv, capsys):
    rows = '2026-05-01,x,0.10\n2026-05-02,y,0.20\n' + '2026-06-01,z,0.10\n' * 10
    path = make_csv('a.csv', HEADER + rows)
    _, out, _ = run_main(capsys, [path])
    assert out == '2026-05 0.30\n2026-06 1.00\n'


def test_zero_and_small_negative_totals(make_csv, capsys):
    rows = (
        '2026-07-01,Shoes,40.00\n2026-07-09,Shoes refund,(40.00)\n'
        '2026-08-01,Snack,1.95\n2026-08-03,Refund,(2.00)\n'
    )
    path = make_csv('a.csv', HEADER + rows)
    _, out, _ = run_main(capsys, [path])
    assert out == '2026-07 0.00\n2026-08 -0.05\n'


def test_bom_and_crlf_export(make_csv, capsys):
    body = '﻿date,description,amount\r\n2026-01-03,Coffee,4.50\r\n2026-01-20,Train,(12.00)\r\n'
    path = make_csv('a.csv', body.encode('utf-8'))
    status, out, _ = run_main(capsys, [path])
    assert status == 0
    assert out == '2026-01 -7.50\n'


def test_quoted_comma_in_description(make_csv, capsys):
    path = make_csv('a.csv', HEADER + '2026-09-01,"Smith, J",12.00\n2026-09-02,"Say ""hi""",1.00\n')
    status, out, _ = run_main(capsys, [path])
    assert status == 0
    assert out == '2026-09 13.00\n'


def test_blank_lines_and_header_only_file(make_csv, capsys):
    a = make_csv('a.csv', HEADER + '\n2026-10-01,Tea,3.00\n\n')
    b = make_csv('b.csv', HEADER)
    status, out, _ = run_main(capsys, [a, b])
    assert status == 0
    assert out == '2026-10 3.00\n'
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run --with pytest python -m pytest -q tests/test_cli.py`
Expected: FAIL — `AttributeError: module 'tally' has no attribute 'main'` (the script test fails with a non-zero/empty result).

- [ ] **Step 3: Write the minimal implementation**

In `tally.py`, replace the imports with:

```python
import csv
import re
import sys
from collections.abc import Iterator
```

and append after `format_cents`:

```python
def read_rows(path: str) -> Iterator[tuple[str, int]]:
    """Yield (month, cents) for each data row of one CSV file."""
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader, None)  # header row
        for row in reader:
            if not row:  # blank line
                continue
            date, _description, amount = row
            yield date.strip()[:7], parse_amount(amount)


def tally(paths: list[str]) -> dict[str, int]:
    """Return total cents per 'YYYY-MM' month across all files."""
    totals: dict[str, int] = {}
    for path in paths:
        for month, cents in read_rows(path):
            totals[month] = totals.get(month, 0) + cents
    return totals


def main(argv: list[str]) -> int:
    totals = tally(argv)
    for month in sorted(totals):
        print(f'{month} {format_cents(totals[month])}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run --with pytest python -m pytest -q`
Expected: all pass (Task 1's 22 plus Task 2's 9).

- [ ] **Step 5: Commit**

```bash
git add tally.py tests/conftest.py tests/test_cli.py
git commit -m 'feat: tally CSV expenses by month and print totals' -m 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'
```

---

### Task 3: Report bad input instead of crashing

**Files:**
- Modify: `tally.py` (add `DATE_RE`, `TallyError`; replace `read_rows` and `main`)
- Test: `tests/test_errors.py`

**Interfaces:**
- Consumes: `tally.parse_amount`, `tally.format_cents`, `tally.tally`, `make_csv` fixture, `tests/conftest.py::ROOT`.
- Produces:
  - `tally.TallyError(Exception)` — message is `'<path>[:<line>]: <problem>'`.
  - `tally.read_rows(path: str)` — same signature as Task 2; now raises `TallyError` for malformed rows and non-UTF-8 files.
  - `tally.main(argv: list[str]) -> int` — returns 2 with usage on no args; 1 with `tally: <message>` on stderr for any input error, printing nothing to stdout.

- [ ] **Step 1: Write the failing tests**

`tests/test_errors.py`:

```python
import subprocess
import sys

import pytest

import tally
from conftest import ROOT

HEADER = 'date,description,amount\n'


def run_main(capsys, paths):
    status = tally.main(paths)
    out, err = capsys.readouterr()
    return status, out, err


def test_no_arguments_prints_usage(capsys):
    status, out, err = run_main(capsys, [])
    assert status == 2
    assert out == ''
    assert err == 'usage: python3 tally.py FILE [FILE ...]\n'


def test_missing_file(tmp_path, capsys):
    path = str(tmp_path / 'nope.csv')
    status, out, err = run_main(capsys, [path])
    assert status == 1
    assert out == ''
    assert err == f'tally: {path}: No such file or directory\n'


@pytest.mark.parametrize('row, problem', [
    ('2026-01-03,Coffee\n', 'expected 3 columns, got 2'),
    ('2026-01-03,Coffee,4.50,extra\n', 'expected 3 columns, got 4'),
    ('03/01/2026,Coffee,4.50\n', "bad date '03/01/2026'"),
    ('2026-13-01,Coffee,4.50\n', "bad date '2026-13-01'"),
    ('2026-01-03,Coffee,-4.50\n', "bad amount '-4.50'"),
    ('2026-01-03,Coffee,\n', "bad amount ''"),
])
def test_malformed_row_names_file_and_line(make_csv, capsys, row, problem):
    path = make_csv('a.csv', HEADER + '2026-01-01,Fine,1.00\n' + row)
    status, out, err = run_main(capsys, [path])
    assert status == 1
    assert out == ''
    assert err == f'tally: {path}:3: {problem}\n'


def test_error_in_later_file_prints_no_partial_totals(make_csv, capsys):
    good = make_csv('good.csv', HEADER + '2026-01-01,Fine,1.00\n')
    bad = make_csv('bad.csv', HEADER + '2026-01-02,Broken,oops\n')
    status, out, err = run_main(capsys, [good, bad])
    assert status == 1
    assert out == ''
    assert err == f"tally: {bad}:2: bad amount 'oops'\n"


def test_non_utf8_file(make_csv, capsys):
    path = make_csv('a.csv', (HEADER + '2026-01-01,Caf\xe9,1.00\n').encode('latin-1'))
    status, out, err = run_main(capsys, [path])
    assert status == 1
    assert out == ''
    assert err == f'tally: {path}: not UTF-8 text\n'


def test_script_exit_status_on_error(tmp_path):
    result = subprocess.run(
        [sys.executable, 'tally.py', str(tmp_path / 'nope.csv')],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert result.stdout == ''
    assert 'Traceback' not in result.stderr
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run --with pytest python -m pytest -q tests/test_errors.py`
Expected: FAIL — tracebacks such as `FileNotFoundError`, `ValueError: not enough values to unpack`, and `UnicodeDecodeError` escape `main`.

- [ ] **Step 3: Write the implementation**

In `tally.py`, below `AMOUNT_RE`, add:

```python
DATE_RE = re.compile(r'\d{4}-(0[1-9]|1[0-2])-\d{2}')


class TallyError(Exception):
    """A problem with an input file, reported to the user without a traceback."""
```

Replace `read_rows` with:

```python
def read_rows(path: str) -> Iterator[tuple[str, int]]:
    """Yield (month, cents) for each data row of one CSV file."""
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        try:
            next(reader, None)  # header row
            for row in reader:
                if not row:  # blank line
                    continue
                where = f'{path}:{reader.line_num}'
                if len(row) != 3:
                    raise TallyError(f'{where}: expected 3 columns, got {len(row)}')
                date, _description, amount = row
                date = date.strip()
                if DATE_RE.fullmatch(date) is None:
                    raise TallyError(f'{where}: bad date {date!r}')
                try:
                    cents = parse_amount(amount)
                except ValueError as error:
                    raise TallyError(f'{where}: {error}') from None
                yield date[:7], cents
        except UnicodeDecodeError:
            raise TallyError(f'{path}: not UTF-8 text') from None
```

Replace `main` with:

```python
def main(argv: list[str]) -> int:
    if not argv:
        print('usage: python3 tally.py FILE [FILE ...]', file=sys.stderr)
        return 2
    try:
        totals = tally(argv)
    except OSError as error:
        print(f'tally: {error.filename}: {error.strerror}', file=sys.stderr)
        return 1
    except TallyError as error:
        print(f'tally: {error}', file=sys.stderr)
        return 1
    for month in sorted(totals):
        print(f'{month} {format_cents(totals[month])}')
    return 0
```

Totals are computed in full before the first `print`, so an error in any file leaves stdout empty.

- [ ] **Step 4: Run the whole suite to verify it passes**

Run: `uv run --with pytest python -m pytest -q`
Expected: all pass (22 + 9 + 11 = 42 passed).

- [ ] **Step 5: Commit**

```bash
git add tally.py tests/test_errors.py
git commit -m 'feat: report malformed input with file and line instead of a traceback' -m 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'
```
