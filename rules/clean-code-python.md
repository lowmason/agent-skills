---
paths:
  - '**/*.py'
---

# Python conventions (always-on)

Standing guardrails injected on every Python edit. The full judgment-level
catalog is the clean-code skill (open it for naming / function / comment /
test decisions); cite fixes by rule code (e.g. G25). Opportunistic cleanup of
code outside the task is gated by the clean-coder skill.

- Single quotes for strings; f-strings for interpolation.
- 4-space indentation.
- Polars over pandas — no new `import pandas`.
- Method-style Polars expressions: `pl.col('x').eq(1)`, `.gt(...)`,
  `.is_in(...)`, `.and_(...)` — not the `==` / `>` / `&` operator forms.
  (Plain-Python comparisons on ints/strings still use `==`.)
- Lazy Polars: `pl.scan_parquet(...)` → transforms → one `.collect()` at the
  end; no intermediate collects. A fluent chain on one LazyFrame is idiomatic,
  not a Law-of-Demeter violation (G36 caveat in clean-code).
- NumPyro + JAX for Bayesian code (not PyMC); pure functions — return new
  arrays, never mutate inputs (F2).
- Named constants over magic numbers (G25): HTTP codes, retry counts,
  thresholds. ruff PLR2004 flags these mechanically where configured.
- Target Python 3.12.
