# Names (N1–N5, N7)

Judgment-level naming rules from Martin's catalog. A linter checks *casing*
(ruff `pep8-naming`, `N8xx` — deferred there); these rules check whether a name
is *meaningful*. Cite fixes by code, e.g. `renamed data2 → wages_lf (N1)`.

## N1 — Descriptive names

The name states what the thing holds or does; the reader never needs the
assignment to know.

```python
# Bad — the name forces the reader to trace the pipeline
data2 = data.filter(pl.col('year').ge(2020))

# Good
recent_wages_lf = wages_lf.filter(pl.col('year').ge(2020))
```

## N2 — Name at the right abstraction level

A name talks in the caller's terms, not the implementation's.

```python
# Bad — leaks the mechanism into the caller's vocabulary
def get_tsv_lines_from_disk_cache(series_id): ...

# Good — callers think in series, not cache lines
def load_series(series_id): ...
```

## N3 — Standard nomenclature (this stack's vocabulary)

Use the names the ecosystem already taught every reader: `lf` for a LazyFrame,
`df` for a DataFrame, `resp` for an httpx response, `key`/`subkey` for a JAX
PRNGKey, `rng` never reused after `jax.random.split`. Inventing synonyms
(`lazy_table`, `reply`) costs the reader a translation step.

## N4 — Unambiguous names

One plausible reading. `get_data()` could fetch, parse, or read a cache;
`fetch_qcew_csv()` and `parse_qcew_rows()` cannot be confused.

```python
# Bad — is this a count of series, or a series of counts?
series_count = df.group_by('area').len()

# Good
rows_per_area = df.group_by('area').len()
```

## N5 — Long names for long scopes

Scope length buys name length. A comprehension index can be `v`; a
module-level constant spells itself out (`QCEW_FIRST_REFERENCE_YEAR`, not
`FIRST_YR`). Inverting this — verbose loop variables, cryptic module
constants — is the smell.

## N7 — Names describe side effects

If it touches the world, the verb says so: `fetch_` (network), `write_` /
`save_` (disk), `parse_` (pure). In a JAX/Polars codebase most functions are
pure, which makes the few effectful ones worth flagging loudly — a function
named `normalize` that also writes a parquet is a trap.

```python
# Bad — hides a disk write
def normalize(df): ...

# Good
def normalize(df): ...            # pure
def write_normalized(df, path): ...  # the effect is in the name
```

## Deferred to ruff

Casing and convention (N1–N6's mechanical slice): `pep8-naming` — `N802`
(function), `N803` (argument), `N806` (variable). N6 (encodings / Hungarian)
is dead in typed Python; its live slice is the same ruff family.
