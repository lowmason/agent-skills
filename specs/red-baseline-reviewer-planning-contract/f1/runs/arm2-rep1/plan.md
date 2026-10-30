# Expense Tally Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `tally.py`, which reads bank-export CSV files and prints the total spent per month across all of them.

**Architecture:** One script at the repo root. Pure functions (`parse_amount`, `tally`, `format_total`) do the parsing and summing with `decimal.Decimal`; `main(argv) -> int` handles the command line, printing and exit status. Tests import the module directly and also run it as a subprocess.

**Tech Stack:** Python 3.12+, standard library only (`csv`, `decimal`, `sys`); pytest for tests.

**Spec:** `specs/expense-tally.md`

## Global Constraints

- Run as `python3 tally.py FILE [FILE ...]` from the repository root. Python 3.12 or later, standard library only.
- Input CSV: header row, columns `date`, `description`, `amount`, in that order. `date` is `YYYY-MM-DD`; `amount` has two decimal places (`12.50`, `1234.00`); `(12.50)` is a refund and counts as negative.
- Output: one line per month with at least one row, `YYYY-MM <total>`, sorted oldest first; `<total>` has exactly two decimal places, leading `-` when negative.
- Exit status 0 when the totals are printed.
- Tests live in `tests/`, run with `uv run --with pytest python -m pytest -q`.
- Code style (CLAUDE.md): single quotes and f-strings.

## Review Focus

Calls this plan makes where the spec is silent: money is summed as `Decimal`, never `float`; a malformed row or unreadable file prints `tally: <file>:<line>: <reason>` to stderr, prints no totals, and exits 1 (a partial tally would silently lose money); files are read as `utf-8-sig` with `newline=''`; blank lines are skipped.

1. **Many small amounts** (`0.10` three times) must total `0.30`, not `0.30000000000000004` or `0.29`. Pinned in Task 1 (`test_small_amounts_sum_exactly`).
2. **A month whose refunds exactly cancel its purchases** prints `0.00`, never `-0.00`. Pinned in Task 1 (`test_net_zero_month_prints_positive_zero`).
3. **Descriptions containing commas**, quoted by the bank (`"Lunch, team"`), must not shift the amount column. Pinned in Task 1 (`test_quoted_description_with_comma`).
4. **Bank-export encoding quirks**: a UTF-8 BOM before the header, CRLF line endings, and a trailing blank line must still tally every row. Pinned in Task 1 (`test_bom_crlf_and_blank_line`).
5. **A malformed row** (`amount` of `abc`, or a bad date) must fail loudly naming the file and line, not print a total that silently omits it. Pinned in Task 2 (`test_malformed_row_exits_1_without_totals`).

## Decisions

None.

---

### Task 1: Parsing and monthly totals

**Files:**
- Create: `tally.py`
- Test: `tests/test_tally.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `class TallyError(Exception)` — message already formatted as `<file>:<line>: <reason>`.
  - `parse_amount(text: str) -> Decimal` — `'12.50'` → `Decimal('12.50')`, `'(12.50)'` → `Decimal('-12.50')`; raises `ValueError` on anything else.
  - `tally(paths: list[str]) -> dict[str, Decimal]` — keys `'YYYY-MM'`, summed across all files; raises `TallyError` on a malformed row.
  - `format_total(total: Decimal) -> str` — exactly two places, `'-7.50'`, `'30.00'`, `'0.00'` for any zero.

- [ ] **Step 1: Write the failing tests** in `tests/test_tally.py`, using a `write_csv(tmp_path, name, text) -> str` helper that writes `text` (header included by caller) and returns the path:

```python
from decimal import Decimal
import pytest
import tally

def test_parse_amount():
    assert tally.parse_amount('12.50') == Decimal('12.50')
    assert tally.parse_amount('1234.00') == Decimal('1234.00')
    assert tally.parse_amount('(12.00)') == Decimal('-12.00')
    for bad in ['abc', '12.5', '', '(12.00']:
        with pytest.raises(ValueError):
            tally.parse_amount(bad)

def test_spec_example(tmp_path):
    a = write_csv(tmp_path, 'a.csv', 'date,description,amount\n2026-01-03,Coffee,4.50\n2026-01-20,Train,(12.00)\n2026-02-01,Books,30.00\n')
    assert tally.tally([a]) == {'2026-01': Decimal('-7.50'), '2026-02': Decimal('30.00')}

def test_sums_across_files(tmp_path):
    # a.csv: 2026-01 4.50; b.csv: 2026-01 1.00 and 2025-12 2.00
    assert tally.tally([a, b]) == {'2025-12': Decimal('2.00'), '2026-01': Decimal('5.50')}

def test_format_total():
    assert tally.format_total(Decimal('-7.50')) == '-7.50'
    assert tally.format_total(Decimal('30')) == '30.00'
    assert tally.format_total(Decimal('1234.00')) == '1234.00'

def test_small_amounts_sum_exactly(tmp_path):
    # three 2026-03 rows of 0.10
    assert tally.format_total(tally.tally([p])['2026-03']) == '0.30'

def test_net_zero_month_prints_positive_zero(tmp_path):
    # 2026-04 rows 12.00 and (12.00)
    assert tally.format_total(tally.tally([p])['2026-04']) == '0.00'

def test_quoted_description_with_comma(tmp_path):
    # row: 2026-05-02,"Lunch, team",20.00
    assert tally.tally([p]) == {'2026-05': Decimal('20.00')}

def test_bom_crlf_and_blank_line(tmp_path):
    # bytes: b'\xef\xbb\xbfdate,description,amount\r\n2026-06-01,Taxi,8.00\r\n2026-06-02,Tea,(1.00)\r\n\r\n'
    assert tally.tally([p]) == {'2026-06': Decimal('7.00')}

def test_malformed_row_raises_with_location(tmp_path):
    # line 3 has amount 'abc'
    with pytest.raises(tally.TallyError, match=r'bad\.csv:3:'):
        tally.tally([p])
```

Fill in each `# ...` comment as a `write_csv` call (or `write_bytes` for the BOM case) with exactly the rows it names.

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --with pytest python -m pytest -q tests/test_tally.py`
Expected: collection error, `ModuleNotFoundError: No module named 'tally'`.

- [ ] **Step 3: Implement the four Interfaces items in `tally.py`**

`parse_amount` matches `^\(?\d+\.\d{2}\)?$` with balanced parentheses (use `re.fullmatch(r'(\()?(\d+\.\d{2})(?(1)\))', text)`). `tally` opens each file with `encoding='utf-8-sig', newline=''`, reads with `csv.reader`, skips the header and empty rows, validates the date with `date.fromisoformat` and requires exactly three columns, keys on `row[0][:7]`, and converts `ValueError` into `TallyError(f'{path}:{reader.line_num}: {reason}')`. An `OSError` opening a file becomes `TallyError(f'{path}: {exc.strerror}')`. `format_total` returns `f'{total:.2f}'` after replacing any zero (including `Decimal('-0.00')`) with `Decimal(0)`, so it never prints `-0.00`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run --with pytest python -m pytest -q tests/test_tally.py`
Expected: `9 passed`.

- [ ] **Step 5: Commit**

```bash
git add tally.py tests/test_tally.py
git commit -m 'feat: parse bank CSVs and total spending per month'
```

### Task 2: Command-line entry point

**Files:**
- Modify: `tally.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `tally(paths) -> dict[str, Decimal]`, `format_total(total) -> str`, `TallyError` from Task 1.
- Produces: `main(argv: list[str]) -> int` (argv excludes the program name) and `if __name__ == '__main__': sys.exit(main(sys.argv[1:]))`.

- [ ] **Step 1: Write the failing tests** in `tests/test_cli.py`, running `[sys.executable, 'tally.py', *paths]` via `subprocess.run(..., capture_output=True, text=True, cwd=<repo root>)`:

```python
def test_spec_example_output(tmp_path):
    # a.csv = the spec's Example file
    r = run(a)
    assert r.returncode == 0
    assert r.stdout == '2026-01 -7.50\n2026-02 30.00\n'

def test_months_sorted_across_files(tmp_path):
    # a.csv: 2026-02 30.00; b.csv: 2025-11 5.00, 2026-01 1.25
    assert run(a, b).stdout == '2025-11 5.00\n2026-01 1.25\n2026-02 30.00\n'

def test_malformed_row_exits_1_without_totals(tmp_path):
    # good.csv valid; bad.csv line 2 has date 2026-13-01
    r = run(good, bad)
    assert r.returncode == 1
    assert r.stdout == ''
    assert r.stderr.startswith('tally: ') and 'bad.csv:2:' in r.stderr

def test_missing_file_exits_1(tmp_path):
    r = run(str(tmp_path / 'nope.csv'))
    assert r.returncode == 1 and r.stdout == '' and 'nope.csv' in r.stderr

def test_no_arguments_prints_usage():
    r = run()
    assert r.returncode == 2 and 'usage: python3 tally.py FILE [FILE ...]' in r.stderr
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --with pytest python -m pytest -q tests/test_cli.py`
Expected: 5 failed (no output, return code 0 from a script with no entry point).

- [ ] **Step 3: Implement `main(argv: list[str]) -> int` in `tally.py`**

No arguments: print `usage: python3 tally.py FILE [FILE ...]` to stderr, return 2. Otherwise compute all totals first, then print `f'{month} {format_total(total)}'` for each month in sorted order and return 0; on `TallyError` print `f'tally: {exc}'` to stderr and return 1 before printing anything to stdout.

- [ ] **Step 4: Run the full suite to verify it passes**

Run: `uv run --with pytest python -m pytest -q`
Expected: `14 passed`.

- [ ] **Step 5: Commit**

```bash
git add tally.py tests/test_cli.py
git commit -m 'feat: add tally.py command-line entry point'
```
