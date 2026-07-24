# Tests (F.I.R.S.T.; T1, T3, T5, T6)

Coverage *judgment* — which tests are missing and where. Coverage *tooling*
(T2: use a coverage tool; T9: tests should be fast) is CI mechanics:
`pytest-cov` and test-duration budgets, not review judgment; the intent is
kept, the enforcement lives in project tooling. Test *strategy* for scrapers,
pipelines, and models is the develop-testing-strategy skill — this file is
the per-edit judgment layer.

## F.I.R.S.T. (the pytest framing)

- **Fast** — a unit test that fits in the edit loop. MCMC and network calls
  are not unit tests; mark them (`slow`, `network`) and keep them out of the
  default run.
- **Independent** — no test reads another's state. Shared parquet scratch
  files and module-level mutable fixtures are the usual leaks; use `tmp_path`.
- **Repeatable** — same result on any machine, any day. Seed every PRNGKey,
  never `datetime.now()` in an assertion path.
- **Self-Validating** — asserts, not printed output a human eyeballs.
- **Timely** — written with (ideally before — test-driven-development) the
  code, while the failure modes are still in your head.

## T1 — Insufficient tests

The question is never "what percent" but "what could break that no test
would catch". A parser with one happy-path test is untested at every edge
its input format actually has.

## T3 — Don't skip trivial tests

Trivial to write is not trivial in value: the two-line test on a helper is
also executable documentation of its contract, and its cost is near zero.

## T5 — Test boundary conditions

For this stack the recurring boundaries: the empty frame, the single row,
the last line of a flat file (off-by-one territory), period `M13` vs
`M01–M12`, a year boundary, an all-null column, a `'-'` sentinel value.

```python
def test_parse_series_keeps_final_line():
    # boundary: the last data line is the classic off-by-one casualty
    rows = parse_series('h1\th2\na\tb\nc\td\n')
    assert rows[-1] == {'h1': 'c', 'h2': 'd'}


def test_monthly_panel_excludes_m13():
    lf = pl.LazyFrame({'period': ['M01', 'M13'], 'value': [1.0, 12.0]})
    out = monthly_state_panel(lf).collect()
    assert out.filter(pl.col('period').eq('M13')).is_empty()
```

## T6 — Exhaustively test near bugs

A found bug marks a fault-dense region: when a fix lands, add the neighbors
(the line before, the empty input, the double occurrence) in the same
sitting. One bug per region is the exception, not the rule.
