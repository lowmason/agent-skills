# Functions (F2, G6, G30, G34)

Cohesion judgment a linter cannot make. Size proxies (statement count,
branch count, argument count) are deferred to ruff — see the bottom table.

**The tempering (qntm / Ousterhout):** the best-known critique of *Clean
Code* targets its tiny-function dogma — mechanical extraction until every
function is two lines produces "lasagna code": a call stack of shallow
wrappers where no single frame is readable. Ousterhout's counter-principle
is **deep modules**: a simple interface over a rich implementation beats
many shallow ones. So here, G30/G34 are *cohesion* rules, never a line-count
mandate: **never extract purely to make a function shorter.** A 30-line lazy
Polars pipeline that does one coherent transformation is one thing — leave it
whole.

## G30 — Functions do one thing (cohesion, not line count)

"One thing" = one reason to change. Fetching, parsing, and writing are three
reasons.

```python
# Bad — three responsibilities, three reasons to change
def ingest(url, path):
    text = httpx.get(url).text
    rows = [dict(zip(HEADER, ln.split('\t'))) for ln in text.splitlines()[1:]]
    pl.DataFrame(rows).write_parquet(path)

# Good — split by responsibility (and N7: the effectful ones say so)
def fetch_flat_file(client, url): ...
def parse_rows(text): ...
def write_series(df, path): ...
```

```python
# NOT a violation — one coherent transformation; do not shred it into
# five-line helpers that each get called once (deep module, G30 satisfied)
def monthly_state_panel(lf):
    return (
        lf
        .filter(pl.col('period').ne('M13'))
        .with_columns(pl.col('value').cast(pl.Float64))
        .group_by('state_fips', 'year', 'period')
        .agg(pl.col('value').sum().alias('employment'))
        .sort('state_fips', 'year', 'period')
    )
```

## G34 — Descend one level of abstraction

Within a function, every statement sits one level below the function's name.
A function named `build_panel` that mixes `pl.scan_parquet` calls with byte
slicing of a series_id is straddling levels — push the low level down into a
named helper *because it is a different level*, not to save lines.

## G6 — Code at the wrong level of abstraction

The module-scale version of G34: HTTP retry mechanics do not live in a
modeling module; prior definitions do not live in an ETL module. Move code to
the layer whose vocabulary it speaks.

## F2 — No output arguments (free in functional JAX — keep it so)

In NumPyro/JAX the pure style makes this automatic: functions take arrays,
return new arrays, never mutate inputs (`x.at[i].set(v)` returns a copy).
State it as the positive invariant it is — a function that mutates a passed
DataFrame or buffer in this stack is not "efficient", it is a bug factory.

## Deferred to ruff

| Rule | ruff |
|---|---|
| F1 too many arguments | `PLR0913` |
| F3 flag arguments | `FBT001` / `FBT002` / `FBT003` |
| G30 size proxies | `PLR0915`, `PLR0912`, `PLR0911`, `C901` |
