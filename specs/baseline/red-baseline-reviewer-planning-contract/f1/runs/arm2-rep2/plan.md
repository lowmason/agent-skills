# Expense Tally Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `tally.py` prints per-month spending totals across one or more bank CSV exports.

**Architecture:** One script, `tally.py`, at the repo root: pure functions (`parse_amount`, `tally`, `format_totals`) plus a `main(argv) -> int` CLI wrapper. Money is `decimal.Decimal` throughout, never `float`. Tests import the functions directly and run the script through `subprocess` for end-to-end checks.

**Tech Stack:** Python 3.12+, standard library only (`csv`, `decimal`, `datetime`, `re`, `sys`); pytest for tests.

**Spec:** `specs/expense-tally.md`

## Global Constraints

- Run as `python3 tally.py FILE [FILE ...]` from the repository root. Python 3.12 or later, standard library only.
- Columns `date`, `description`, `amount`, in that order, after a header row.
- `date` is `YYYY-MM-DD`; `amount` is a decimal number with two places; `(12.50)` is a refund and counts as negative.
- Output: one line per month that has at least one row, `YYYY-MM <total>`, oldest first; `<total>` has exactly two decimal places, leading `-` when negative.
- Exit status 0 when the totals are printed.
- Tests: `uv run --with pytest python -m pytest -q`, in `tests/`.
- Code style (CLAUDE.md): single quotes and f-strings.
- Plan calls where the spec is silent:
  - Any bad input (unreadable file, wrong header, bad date, bad amount, wrong column count) → one line on stderr `tally: <file>:<line>: <reason>` (or `tally: <file>: <reason>` for file-level errors), exit 1, and **nothing** on stdout (no partial totals).
  - No FILE arguments → usage message on stderr, exit 2 (argparse default).
  - Files are read with `encoding='utf-8-sig'`, `newline=''`.
  - Surrounding whitespace in a field is stripped. A plain leading `-` (`-12.50`) is also accepted as negative; `(-12.50)` is rejected.
  - Header-only files contribute nothing; if no file has rows, print nothing and exit 0.

## Review Focus

- Amounts that don't sum exactly in binary floating point (`0.10` + `0.20`) → the month prints `0.30`, not `0.30000000000000004` or `0.31`.
- The same month appearing in several files → one merged line, not one per file.
- A file saved by Excel with a UTF-8 BOM before `date` → parsed normally, not rejected as a bad header.
- A description containing a comma, quoted per CSV (`"Dinner, team"`) → the row counts with its amount.
- A refund that exactly cancels a purchase in its month → prints `0.00`, never `-0.00`, and the month still appears.

## Decisions

None.

---

### Task 1: Core parsing and totals

**Files:**
- Create: `tally.py`
- Test: `tests/test_tally.py`

**Interfaces:**
- Produces:
  - `parse_amount(text: str) -> Decimal` — raises `ValueError` on anything other than `\d+\.\d{2}`, `(\d+\.\d{2})`, or `-\d+\.\d{2}` (after stripping whitespace).
  - `month_of(text: str) -> str` — returns `'YYYY-MM'`; raises `ValueError` unless the text matches `\d{4}-\d{2}-\d{2}` and is a real calendar date (`date.fromisoformat`).
  - `tally(rows: Iterable[tuple[str, str]]) -> dict[str, Decimal]` — `(date, amount)` pairs to month totals via `month_of` and `parse_amount`, so their `ValueError`s propagate.
  - `format_totals(totals: dict[str, Decimal]) -> list[str]` — sorted `'YYYY-MM <total>'` lines.

- [ ] **Step 1: Write the failing tests** in `tests/test_tally.py` (import via `sys.path` insert of the repo root, or a `tests/conftest.py` that does it):

```python
def test_parse_amount_plain_and_refund():
    assert parse_amount('12.50') == Decimal('12.50')
    assert parse_amount('1234.00') == Decimal('1234.00')
    assert parse_amount('(12.50)') == Decimal('-12.50')
    assert parse_amount(' -3.00 ') == Decimal('-3.00')

@pytest.mark.parametrize('bad', ['', '12', '12.5', '12.505', '(12.50', '12.50)', '(-12.50)', 'abc', '1,234.00'])
def test_parse_amount_rejects(bad):
    with pytest.raises(ValueError):
        parse_amount(bad)

def test_month_of():
    assert month_of('2026-01-03') == '2026-01'
    for bad in ['2026-1-03', '2026-02-30', '20260103', '03/01/2026']:
        with pytest.raises(ValueError):
            month_of(bad)

def test_spec_example():
    rows = [('2026-01-03', '4.50'), ('2026-01-20', '(12.00)'), ('2026-02-01', '30.00')]
    assert format_totals(tally(rows)) == ['2026-01 -7.50', '2026-02 30.00']

def test_decimal_exact():
    assert format_totals(tally([('2026-03-01', '0.10'), ('2026-03-02', '0.20')])) == ['2026-03 0.30']

def test_cancelled_month_prints_zero():
    assert format_totals(tally([('2026-04-01', '12.00'), ('2026-04-02', '(12.00)')])) == ['2026-04 0.00']

def test_sorted_across_years():
    assert format_totals(tally([('2026-01-05', '1.00'), ('2025-12-31', '2.00')])) == ['2025-12 2.00', '2026-01 1.00']
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run --with pytest python -m pytest -q tests/test_tally.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'tally'`.

- [ ] **Step 3: Implement the four functions in `tally.py`** — `parse_amount` with one `re.fullmatch`; `format_totals` uses `f'{month} {total:.2f}'` and normalises a zero total to `Decimal('0.00')` so `-0.00` cannot appear.

- [ ] **Step 4: Run to verify pass**

Run: `uv run --with pytest python -m pytest -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add tally.py tests/
git commit -m 'feat: add amount parsing and monthly totals'
```

### Task 2: Command-line interface

**Files:**
- Modify: `tally.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `month_of`, `parse_amount`, `tally`, `format_totals` from Task 1.
- Produces: `main(argv: list[str] | None = None) -> int`; `if __name__ == '__main__': sys.exit(main())`.

- [ ] **Step 1: Write the failing tests** in `tests/test_cli.py`. Helper `run(*files) -> CompletedProcess` runs `[sys.executable, 'tally.py', *files]` with `cwd` = repo root, `capture_output=True, text=True`. Files go in `tmp_path`.

```python
def test_spec_example(tmp_path):  # a.csv exactly as in the spec
    r = run(a)
    assert (r.returncode, r.stdout, r.stderr) == (0, '2026-01 -7.50\n2026-02 30.00\n', '')

def test_same_month_merged_across_files(tmp_path):
    # a.csv: 2026-01-03,Coffee,4.50   b.csv: 2026-01-09,Lunch,10.00
    assert run(a, b).stdout == '2026-01 14.50\n'

def test_bom_header(tmp_path):
    # file written with encoding='utf-8-sig'
    assert run(f).stdout == '2026-01 4.50\n'

def test_quoted_description_with_comma(tmp_path):
    # row: 2026-01-03,"Dinner, team",40.00
    assert run(f).stdout == '2026-01 40.00\n'

def test_header_only_prints_nothing(tmp_path):
    r = run(f)
    assert (r.returncode, r.stdout) == (0, '')

@pytest.mark.parametrize('body, reason', [
    ('date,description,amount\n2026-01-03,Coffee,4.5\n', ':2:'),
    ('date,description,amount\n2026-13-03,Coffee,4.50\n', ':2:'),
    ('date,description,amount\n2026-01-03,Coffee\n', ':2:'),
    ('amount,date,description\n4.50,2026-01-03,Coffee\n', 'header'),
])
def test_bad_input_fails_without_output(tmp_path, body, reason):
    # good.csv valid, listed first, so partial output would show
    r = run(good, bad)
    assert r.returncode == 1 and r.stdout == ''
    assert r.stderr.startswith('tally: ') and reason in r.stderr

def test_missing_file(tmp_path):
    r = run(tmp_path / 'nope.csv')
    assert r.returncode == 1 and r.stdout == '' and 'nope.csv' in r.stderr

def test_no_args():
    assert run().returncode == 2
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run --with pytest python -m pytest -q tests/test_cli.py`
Expected: FAIL — no output / exit 0 from a script without `main`.

- [ ] **Step 3: Implement `main` in `tally.py`** — `argparse` with `files` `nargs='+'`; read every file with `csv.reader` (`encoding='utf-8-sig'`, `newline=''`), strip header cells and require exactly `['date', 'description', 'amount']`; collect all `(date, amount)` pairs (skip fully blank lines), converting `ValueError`/`OSError` into the stderr message from Global Constraints and `return 1`; validate every row before printing anything; print `format_totals` lines; `return 0`. Line numbers come from `reader.line_num`.

- [ ] **Step 4: Run to verify pass**

Run: `uv run --with pytest python -m pytest -q`
Expected: all pass. Also run the spec example by hand: `python3 tally.py <a.csv>` prints the two spec lines.

- [ ] **Step 5: Commit**

```bash
git add tally.py tests/test_cli.py
git commit -m 'feat: add tally command-line interface'
```
