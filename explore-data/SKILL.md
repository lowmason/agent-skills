---
name: explore-data
description: >
  Profile a new dataset with Polars before you analyze or model it — the disciplined first pass
  that catches the data problems that would otherwise corrupt downstream work. Use when you've
  just received a parquet/CSV/scrape and don't yet know its shape, schema, null rates, or
  cardinality; when you need to check whether a candidate key (series_id + ref_date, client_id +
  ref_date) is actually unique; when you suspect duplicates, suspicious sentinels (-1, 9999, "",
  "N/A", "."), constant or high-null columns, mixed types from a raw HTML/CSV ingest, or
  unexpected category counts; when you must confirm as-of / vintage correctness on revised series
  (one row per series-period-vintage, no double-counted revisions) before tagging or joining;
  when you need panel diagnostics — coverage by period/geography/industry, panel balance,
  entry/exit; or when comparing a provider's microdata against QCEW/CES/JOLTS/BED. This is the
  pre-flight before bayesian-workflow: profile the data before you build a model on it. Trigger on
  new microdata, "explore/profile this dataset", null/duplicate/quality checks, schema inspection,
  scan_parquet, .describe(), value_counts, .null_count(), n_unique, or "is this column a key?".
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
---

# Explore Data

## Overview

Before any analysis or model, profile the dataset. A profile answers four questions in order:
**shape** (how big, what columns, what types), **quality** (nulls, sentinels, duplicates,
constants), **structure** (date ranges, keys, panel balance, vintage layout), and **next steps**
(which columns are usable as dimensions/metrics, what to fix first). Skipping this is how a `-1`
sentinel becomes a real employment level in a regression, or how a non-unique `(series_id,
ref_date)` key silently double-counts vintages in a join.

The fastest path is to run the bundled profiler, read its flags, then inspect anomalies by hand.
Lead with Polars' lazy API (`scan_parquet` / `scan_csv`) so a multi-GB partitioned dataset never
lands in memory whole — collect only the small summary frames each check needs.

```bash
python scripts/profile.py data/qcew/qcew_estimates.parquet \
    --candidate-keys series_id,ref_date,vintage_date \
    --vintage-cols series_id,ref_date,vintage_date \
    --json profile.json
```

## This skill vs. its siblings

Three data skills cover one pipeline at different moments; keep them distinct so they don't collide:

- **`explore-data` (this skill)** — *understand* a dataset on first contact: what's in it, is it usable, what's broken. Ad-hoc, before analysis.
- **`validate-data`** — *gate* a dataset or analysis right before it ships: is this number defensible? Produces a pass/fail report.
- **`develop-testing-strategy`** — *automate* the invariants you find here into a permanent pytest suite that runs in CI.

This skill owns **discovery**: it is the canonical place for "is this column actually a key?" and "is this a revision panel or a snapshot?". The other two *assert* and *test* what you find here.

## Workflow

1. **Scan, don't read.** `lf = pl.scan_parquet("data/qcew/*.parquet")`. Globs handle partitioned
   output; the schema and row count come from metadata without touching the data. Use
   `lf.collect_schema()` for names/dtypes and `lf.select(pl.len()).collect().item()` for the row
   count. Only collect a full column when a check genuinely needs it.
2. **First-pass profile.** Per column: null %, `n_unique`, dtype, a sample value. Numeric columns:
   min / max / quantiles / mean / std. Low-cardinality string/bool columns: top `value_counts`.
   Date columns: min / max and a gap check. The profiler does all of this in a handful of lazy
   passes — see **Polars idioms** for the hand-written versions.
3. **Quality flags.** High-null columns (≥50%), constant columns (`n_unique <= 1`), suspicious
   sentinels, mixed types, outliers, unexpected cardinality. See **Quality flags**.
4. **Key & duplicate check.** Test whether your candidate key is actually unique
   (`--candidate-keys`). A failed uniqueness check before a join is a found bug, not a nuisance.
5. **Vintage / as-of check** (for revised series). Confirm one clean row per
   `(series_id, ref_date, vintage_date)` and that revised periods carry multiple vintages as
   expected. See **Vintage and as-of correctness**.
6. **Panel diagnostics** (for entity × period microdata). Coverage by period/geography/industry,
   panel balance, entry/exit. See **Panel and time-series microdata**.
7. **Summarize.** Produce a short profile summary, a list of flagged issues, and concrete next
   steps (e.g. "drop `benchmark_revision` (constant); investigate 598 null `series_id` rows before
   keying; `ref_date` is quarterly, ignore the monthly-gap flag"). End with what's safe to model.

## Polars idioms

These are verified on Polars 1.38. Prefer the lazy form; collect only the summary frame.

```python
import polars as pl

lf = pl.scan_parquet("data/qcew/qcew_estimates.parquet")
schema = lf.collect_schema()                                   # names + dtypes, no data read
n_rows = lf.select(pl.len()).collect().item()

# Null count per column, one pass
nulls = lf.select(pl.all().null_count()).collect()

# Distinct count per column, one pass
nunq = lf.select(pl.all().n_unique()).collect()

# value_counts on a categorical-ish column (sort kwarg / count-col name have churned across
# releases — group_by + len is the portable form)
top = (lf.select("geographic_type").group_by("geographic_type")
         .agg(pl.len().alias("count")).sort("count", descending=True).head(5).collect())

# Numeric summary via explicit aggregations. Avoid LazyFrame.describe(): its quantile handling
# has shifted between releases and it materializes more than you need. Be explicit instead.
stats = lf.select(
    pl.col("employment").min().alias("min"),
    pl.col("employment").quantile(0.25).alias("p25"),
    pl.col("employment").median().alias("p50"),
    pl.col("employment").quantile(0.75).alias("p75"),
    pl.col("employment").max().alias("max"),
    pl.col("employment").mean().alias("mean"),
    pl.col("employment").std().alias("std"),
).collect()

# Inspect an anomaly: filter, then collect a small slice
suspects = lf.filter(pl.col("series_id").is_null()).head(20).collect()
```

**Duplicate / key check** — the portable idiom is group-by-count-filter, which also tells you
*which* keys collide and by how much:

```python
dups = (lf.group_by(["series_id", "ref_date", "vintage_date"])
          .agg(pl.len().alias("n")).filter(pl.col("n") > 1)
          .sort("n", descending=True).collect())
is_unique = dups.height == 0
# `lf.unique(subset=keys).select(pl.len())` vs n_rows works too, but loses the offender list.
```

## Quality flags

Each flag points at a likely problem and where it comes from:

- **High-null columns** (≥50% null). Either a mostly-empty field or a join that didn't land. In
  the real QCEW estimates file, `series_id` is ~20% null — those rows are aggregated geographies
  (regions/divisions) with no leaf series ID, which is exactly why they break a `series_id`-keyed
  join until handled.
- **Constant columns** (`n_unique <= 1`). Carries no information for this slice. Common after
  filtering — e.g. `source = "qcew"`, `benchmark_revision = 0`, `industry_code = "00"` in a
  single-industry extract. Safe to drop for analysis; note it rather than silently keeping it.
- **Suspicious sentinels.** Missing-as-a-value codes that pollute statistics if treated as real.
  Strings: `""`, `" "`, `"N/A"`, `"NA"`, `"null"`, `"-"`, and the BLS disclosure markers `"."`
  (not disclosable) and `"N"` (not available). Numerics: `-1`, `-9`, `9999`, `99999`, `999999`,
  `9999.9`. **Flag, never auto-drop** — `-1` may be a legitimate month-over-month change. Verify
  intent, then convert to null deliberately.
- **Mixed types.** Bites at *raw ingest* (BLS HTML/CSV scrape via httpx/BeautifulSoup/lxml), not
  in parquet — parquet is already typed, so a string column there is a real string. On a CSV
  scrape, scan with `infer_schema_length=None` so a numeric column that turns alphabetic in row
  50,000 is caught rather than truncated.
- **Outliers.** Compare max to p75 and mean to median. A `max` orders of magnitude above p75 (e.g.
  national totals mixed into a state-level extract) usually means an aggregation level leaked in —
  filter on `geographic_type` / `agglvl_code` before trusting the column.
- **Unexpected cardinality.** 52 states (50 + DC + national), ~20 NAICS supersectors, 12 months.
  A count that's off (53 "states", 21 supersectors) signals a stray code, a trailing-whitespace
  variant, or a mixed aggregation level. Check with a `value_counts` on the offending column.

## Vintage and as-of correctness

Revised BLS series (QCEW, CES, SAE, BED) carry the same `(series_id, ref_date)` at multiple
`vintage_date`s — that's the revision history, and it's correct. The profiling job is to confirm
the *layout* before any tagging or join. (For each program's actual revision cadence and series-ID
layout, consult the `bls-data-context` skill.)

- **`(series_id, ref_date, vintage_date)` should be a clean unique key — but inspect a failure
  before calling it a bug.** Non-uniqueness has two very different causes. (a) A genuine
  double-count: two rows for the same series, period, *and* vintage, which over-weights one
  revision downstream — a real bug to fix. (b) A null or placeholder key column: aggregate
  geographies (regions, divisions) often carry a *null* `series_id`, and nulls all collide under
  group-by, producing phantom "duplicates." In the real QCEW estimates file the ~20% null
  `series_id` rows are exactly the region/division aggregates — their true key is
  `(geographic_code, ref_date, vintage_date)`, not `series_id`. Look at the offending rows
  (`--vintage-cols` reports the count; then filter to inspect) before concluding which case you
  have.
- **Check whether you have a revision panel or a snapshot.** If most `(series_id, ref_date)` keys
  carry multiple `vintage_date`s, you have a revision panel. If every period has exactly one
  vintage (as the current QCEW estimates file does — `period_keys_with_multiple_vintages: 0`), it's
  a point-in-time snapshot, not a revision history — fine, but know which one you have before
  joining to `vintage_dates.parquet` or attempting an as-of reconstruction.
- **As-of joins need vintage filtering.** To reconstruct what was known on a date, filter to the
  latest `vintage_date <= as_of` per `(series_id, ref_date)` — never join the whole revision
  history. Profiling tells you whether that filter is even necessary.

```python
# Per-period vintage spread and the clean-key check
chk = (lf.group_by(["series_id", "ref_date"])
         .agg(pl.col("vintage_date").n_unique().alias("n_vint")).collect())
revised = chk.filter(pl.col("n_vint") > 1).height        # periods with revisions
full_key_dups = (lf.group_by(["series_id", "ref_date", "vintage_date"])
                   .agg(pl.len().alias("n")).filter(pl.col("n") > 1).collect())
if full_key_dups.height:
    # Inspect before concluding: a null/placeholder key column (e.g. null series_id on aggregate
    # geographies) collides under group-by and looks like a duplicate without being one.
    print(f"{full_key_dups.height} non-unique vintage keys — inspect:", full_key_dups.head())
```

## Panel and time-series microdata

For entity × period data (provider client-month panels; QCEW establishment-quarter), profile
coverage and balance, not just columns:

```python
# Coverage by period — counts and totals over time (watch for ragged endpoints)
coverage = (lf.group_by("ref_date").agg(
    pl.col("client_id").n_unique().alias("n_entities"),
    pl.col("qualified_employment").sum().alias("total_emp"),
).sort("ref_date").collect())

# Coverage by dimension — geography / industry / size_class
by_geo = (lf.group_by(["ref_date", "state_fips"])
            .agg(pl.col("client_id").n_unique().alias("n")).collect())

# Panel balance — obs per entity vs the number of periods present
n_periods = lf.select(pl.col("ref_date").n_unique()).collect().item()
per_entity = lf.group_by("client_id").agg(pl.col("ref_date").n_unique().alias("n_obs")).collect()
balanced_pct = 100 * (per_entity["n_obs"] == n_periods).sum() / per_entity.height

# Entry / exit — entities first/last seen mid-panel (uses explicit entry_month / exit_month
# when present, or first/last ref_date otherwise)
span = lf.group_by("client_id").agg(
    pl.col("ref_date").min().alias("first"), pl.col("ref_date").max().alias("last")
).collect()
```

A low balanced share is normal for a live provider panel (clients churn); the point is to *see*
the churn — entries, exits, and coverage thinning at the most recent periods — before you compute
growth rates on a moving sample. `scripts/profile.py --panel-entity client_id --panel-period
ref_date` reports entities, periods, balanced share, and entry/exit counts in one call.

## Output

A profiling pass produces three things, in this order:

1. **Profile summary** — shape, dtypes, and the per-column null/cardinality table.
2. **Flagged issues** — the quality flags above, each with the specific column and count.
3. **Suggested next steps** — what to fix or drop, which columns are usable dimensions vs metrics,
   and what's safe to feed into analysis or `bayesian-workflow`. To turn the issues you find into
   a pre-ship gate, hand off to `validate-data`; to lock the invariants in as permanent tests, use
   `develop-testing-strategy`.

`scripts/profile.py --json profile.json` writes a machine-readable version of all three so you can
diff two vintages of the same dataset or attach the profile to a report.

## Common mistakes

- **Calling `.collect()` first, then profiling.** Defeats the lazy engine — a partitioned parquet
  glob blows up memory before you've learned anything. Scan, run lazy summaries, collect only the
  small result frames.
- **Trusting a candidate key without checking it.** "It's obviously `series_id` + `ref_date`" is
  how double-counting joins happen. Run the duplicate check every time; null key columns collide as
  duplicates too, which is itself a finding.
- **Auto-dropping or imputing sentinels.** Rewriting `-1` to null before confirming it's missing
  (and not a real diff) destroys data. Flag, inspect, then convert deliberately.
- **Treating a quarterly series as monthly (or vice versa).** The gap check assumes monthly
  cadence by default; QCEW is quarterly, so its "missing monthly periods" flag is expected noise.
  Confirm the true cadence before reading gap flags as data loss.
- **Ignoring aggregation levels.** BLS files mix national / region / division / state rows
  (`geographic_type`, `agglvl_code`) and total / sector / supersector rows (`industry_type`).
  Profiling the whole file without filtering produces meaningless distributions and phantom
  outliers (national totals dwarfing state values). Profile within an aggregation level.
- **Computing growth on an unbalanced panel without noticing.** Entry/exit churn moves the sample
  composition; a growth rate on a thinning panel confounds real change with sample change. Profile
  balance and coverage-by-period first.
- **Skipping the vintage layout check before an as-of join.** Joining the full revision history
  instead of the as-of slice silently multiplies rows. Confirm the vintage key and decide on the
  filter before joining.
- **Stopping at the profile.** The deliverable is the flagged-issues + next-steps summary, not a
  wall of statistics. State explicitly what's safe to model and what must be fixed first.
