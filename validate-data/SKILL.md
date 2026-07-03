---
name: validate-data
description: >
  Use when QA-ing a dataset or an analysis before it is shared, published, or fed downstream —
  the last gate before a number leaves your laptop. Trigger on: "is this ready to publish",
  "sanity-check this dataset/parquet", "review my analysis", "do the numbers reconcile", "why
  doesn't this match the official total", validating an ETL output, pre-publish review, "I can't
  reproduce yesterday's run", a silent cache or fallback masking a failure, a coverage ratio that
  looks too clean, a decomposition whose components don't add up, unexpected nulls / duplicate
  keys / dtype drift in a parquet, future leakage past the as-of date on revised series
  (QCEW/CES/JOLTS vintages), or a claim that a result is "fine" without an independent check.
  Always consult before signing off on data or an analysis — these checks are the ones agents
  skip unprompted.
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
---

# Validate Data

The job of this skill is to find the reason a number is wrong *before* someone else does. Most
data bugs are not crashes — they are plausible-looking outputs from a silently broken step: a
coverage ratio computed against a missing denominator, a decomposition with a term hardcoded to
zero, a "reproduced" run that loaded a stale cache, a level that leaked a revision the public
couldn't have seen on the as-of date. None of these throw. All of them survive review unless
someone deliberately checks. That checker is you.

## This skill vs. its siblings

- **`explore-data`** — *understand* a new dataset ad-hoc; discover the schema, keys, and vintage layout this skill then asserts.
- **`validate-data` (this skill)** — *gate* a dataset or analysis before it ships: a one-time, adversarial pass/fail with a written report.
- **`develop-testing-strategy`** — *automate* these checks as a permanent pytest suite in CI.

This skill owns the **pre-ship gate** — the content-hash re-run check and the methodology/bias review are its turf. For *why* a key collides or what the vintage layout is, defer to `explore-data`; to make any check here permanent, hand it to `develop-testing-strategy`.

## Two modes — route first

Decide which you are doing; they share machinery but answer different questions.

- **Dataset QA** — "Is this table trustworthy as an input?" Run sections 1–2 (schema/integrity,
  reproducibility). Typical trigger: an ETL parquet, a scraped BLS series, a freshly built panel.
- **Analysis QA** — "Are these conclusions trustworthy as an output?" Run sections 3–4 (accuracy,
  methodology/bias) on top of 1–2, because an analysis is only as sound as its inputs. Typical
  trigger: a nowcast, a provider-vs-official comparison, anything headed for a slide or a doc.

Section 5 (fail loudly) is cross-cutting — apply it throughout. Section 6 is the report you emit.

## Workflow overview

Work top to bottom. Do not skip integrity to get to the interesting accuracy questions — a
schema break upstream invalidates every downstream conclusion, so cheap checks come first.

1. **Schema & integrity** — Does the data match its contract? See §1.
2. **Reproducibility & determinism** — Does re-running yield the identical result? See §2.
3. **Accuracy** — Does it reconcile to an independent benchmark, in the right units? See §3.
4. **Methodology & bias** — Are the conclusions actually supported by the data? See §4.
5. **Fail loudly** — Did any step swallow an error and substitute a plausible value? See §5.
6. **Report** — Emit a structured validation report with explicit pass/fail/warn lines. See §6.

---

## 1. Schema & integrity

Validate the contract before trusting a single value. Express the contract in code, not prose,
so it fails on drift instead of degrading silently.

```python
import polars as pl

lf = pl.scan_parquet("qcew_2019_2024.parquet")
schema = lf.collect_schema()

# Expected columns and dtypes — a contract, checked explicitly.
expected = {
    "ref_date": pl.Date, "quarter": pl.String, "area_fips": pl.String,
    "industry_code": pl.String, "qcew_employment": pl.Int64,
    "qcew_establishments": pl.Int64,
}
missing = set(expected) - set(schema.names())
extra = set(schema.names()) - set(expected)
wrong = {c: (schema[c], expected[c]) for c in expected if c in schema and schema[c] != expected[c]}
assert not missing, f"missing columns: {missing}"
assert not extra, f"unexpected columns: {extra}"
assert not wrong, f"dtype drift: {wrong}"   # e.g. employment read as Float64 / String from a bad parse
```

Then the integrity checks, all as a single lazy aggregation so they run in one pass:

```python
n = lf.select(pl.len()).collect().item()
checks = lf.select(
    pl.len().alias("rows"),
    # Unexpected nulls in columns that must be populated.
    pl.col("qcew_employment").null_count().alias("null_employment"),
    pl.col("area_fips").null_count().alias("null_fips"),
    # Key uniqueness — the grain of the table. A non-unique key silently double-counts downstream.
    pl.struct("ref_date", "area_fips", "industry_code").n_unique().alias("unique_keys"),
    # Cardinality sanity — too few distinct industries means an upstream filter or join dropped rows.
    pl.col("industry_code").n_unique().alias("n_industries"),
    # Value range / domain — employment is non-negative; a negative is a sign or parse error.
    (pl.col("qcew_employment") < 0).sum().alias("negative_employment"),
).collect()

assert checks["unique_keys"].item() == checks["rows"].item(), "key is not unique — table double-counts"
assert checks["null_employment"].item() == 0, "unexpected nulls in employment"
assert checks["null_fips"].item() == 0, "unexpected nulls in area_fips"
assert checks["negative_employment"].item() == 0, "negative employment — sign/parse error"

# Fully-duplicated rows are distinct from key collisions — check both.
dupes = n - lf.unique().select(pl.len()).collect().item()
assert dupes == 0, f"{dupes} fully-duplicate rows"
```

A passing schema is necessary, not sufficient — the right dtypes with the wrong *grain* (e.g.
monthly rows where you expected quarterly, or national rows mixed into a state table) pass every
type check and corrupt every aggregate. Confirm the grain by counting rows per natural key, not
just by asserting uniqueness. If the key *isn't* unique, don't diagnose it here — `explore-data`
distinguishes a genuine double-count from a null-key collision on aggregate-geography rows (the
~20% null `series_id` case); diagnose there, fix, then re-gate.

## 2. Reproducibility & determinism

A result you cannot reproduce is a result you cannot defend. Three sub-checks:

**Re-run parity (hash the output, not the logs).** Run the pipeline twice and compare a content
hash. The trap: a naive byte-hash of a serialized frame is *flaky* — `group_by` without
`maintain_order`, multithreaded joins, and parquet round-trips can reorder rows whose content is
identical, so the bytes differ and you get a false "not reproducible." Canonicalize first, then
hash. Sort columns, sort rows by all columns, sort the per-row hashes — none of these change the
data, all of them remove ordering noise:

```python
import hashlib

def content_hash(df: pl.DataFrame) -> str:
    canon = df.select(sorted(df.columns)).sort(by=sorted(df.columns))
    row_hashes = canon.hash_rows(seed=0).sort()          # UInt64 per row, order-independent
    return hashlib.sha256(row_hashes.to_numpy().tobytes()).hexdigest()

assert content_hash(run_pipeline()) == content_hash(run_pipeline()), "non-deterministic output"
```

**Seeds are fixed and descriptive.** Any stochastic step — a NumPyro/PyMC sampler, a train/test
split, bootstrap resampling — must be seeded, and the seed derived from the analysis name rather
than a magic `42`, so two analyses don't silently share a stream (the repo's descriptive-seed
convention — see `bayesian-workflow`). For NumPyro: `RANDOM_SEED =
sum(map(ord, "qcew-nowcast-v1"))`, then `jax.random.PRNGKey(RANDOM_SEED)`. For PyMC: pass
`random_seed=RANDOM_SEED` to `pm.sample`. Re-running a seeded sampler should reproduce the
posterior summary to within Monte Carlo noise (identical R-hat/ESS, means stable to a few sig
figs); a *materially* different posterior on the same seed means a non-determinism leaked in
(unsorted input, an unpinned dependency, host-device-count change).

**Inputs are pinned and vintaged.** Record exactly which input produced the output — a parquet
path *plus* a content hash, the BLS release date, the data vintage. "Latest QCEW" is not
reproducible; `qcew_2019Q4_vintage_2024-11-20.parquet` is.

**As-of / vintage correctness — no future leakage.** This is the subtlest reproducibility bug in
nowcasting. Every observation has a *knowability boundary*: the date on which a forecaster could
first have seen it. CES is revised for months after first release; QCEW lags ~5–6 months; a
revision merged back onto its original `ref_date` looks like clairvoyance. Verify that no row
carries information dated after its as-of:

```python
# For an as-of run, the publication date of every input must be <= the as-of date.
leaked = lf.filter(pl.col("published_date") > pl.col("as_of_date")).select(pl.len()).collect().item()
assert leaked == 0, f"{leaked} rows leak data published after the as-of date — future leakage"
```

If the data has no `published_date`, you cannot assert the boundary — that absence is itself a
finding, not a pass. Reconstruct it from the release calendar or flag the analysis as
vintage-unverifiable. (`explore-data` profiles the vintage *layout* — revision panel vs snapshot;
`develop-testing-strategy` turns this boundary check into a permanent test.)

## 3. Accuracy

Self-consistent and correct are different properties. Accuracy means reconciling to something the
pipeline did not produce.

**Reconcile aggregates to an independent benchmark.** The aggregate of your microdata should tie
to a published total — provider payroll employment to QCEW, a CES-derived series to the official
CES level. Reconcile with a tolerance and surface the residual; do not eyeball it:

```python
ours = panel.group_by("ref_date").agg(pl.col("payroll_employment").sum()).sort("ref_date")
bench = ces.select(  # unit-align FIRST; alias because arithmetic keeps the left operand's name
    "ref_date", (pl.col("ces_employment_thousands") * 1_000).alias("ces_employment")
)
recon = ours.join(bench, on="ref_date", how="inner").with_columns(
    ((pl.col("payroll_employment") - pl.col("ces_employment")) / pl.col("ces_employment")).alias("rel_err")
)
worst = recon.select(pl.col("rel_err").abs().max()).item()
assert worst < 0.05, f"reconciliation off by {worst:.1%} — investigate before publishing"
```

An *inner* join here is a trap of its own: it silently drops periods present in only one source,
so a reconciliation can "pass" on the overlap while the edges diverge. Check the row counts on
both sides of the join match your expectation.

**Units, scale, sign.** The most common "off by a lot" bug is a units mismatch — CES is published
in thousands, QCEW in persons; rates as 0.034 vs 3.4; dollars vs thousands of dollars. Align
units *before* comparing, and assert sign where the domain demands it (employment ≥ 0, an
unemployment rate in [0, 1] or [0, 100] — know which). A reconciliation that is off by almost
exactly 1000× is a units bug, not a data problem. (`bls-data-context` has the per-program units and
the reconciliation rules — CES↔QCEW March benchmarking, JOLTS rates on CES denominators.)

**Edge periods.** Errors hide at the boundaries: the first and last period (partial windows,
not-yet-revised tails), pandemic months (2020Q2 breaks every YoY comparison), series breaks
(NAICS reclassifications, CES benchmark revisions). Inspect the head and tail of every derived
series explicitly rather than trusting that the middle generalizes.

## 4. Methodology & bias

The hardest failures are not in the data but in the inference. Ask whether the conclusion would
survive a skeptic who shares your data.

**Are the conclusions supported?** Map each claim back to the computation behind it. A claim of
"provider data leads the official series" needs a lead/lag estimate with enough turning points to
mean anything — two sign changes do not establish a lead. If the code computes correlation, the
claim cannot be about causation.

**Within vs composition effects.** When you decompose a divergence into "composition" (the mix
shifted) and "within" (rates moved within cells), verify both terms are actually computed. A
decomposition that hardcodes one term — `pl.lit(0.0).alias("composition_effect")` — and dumps the
remainder into the other is not a decomposition; it is a relabeling. Either compute the shift-
share properly or state plainly that composition is assumed zero and defend that assumption. A
named term that is silently constant is worse than an omitted one, because the chart implies it
was measured.

**Coverage / selection bias.** Provider microdata is not a random sample of the population. Firms
self-select into a payroll provider; coverage skews by size, industry, and region. Before
generalizing a provider trend to the economy, compare its composition to the population frame
(QCEW) — a `misallocation_index` (half the sum of absolute share deviations) quantifies the skew.
If coverage is 3% concentrated in small-firm services, a provider-wide trend is a statement about
that slice, not about total nonfarm.

**Survivorship.** A panel restricted to firms present in every period drops entrants and exits —
exactly the firms that drive births/deaths dynamics. Check whether the panel is balanced by
construction, and whether that balancing removes the signal you are trying to measure.

**Revision effects.** A model that looks prescient on revised (final) data may be useless on the
real-time vintage it would actually have seen. Evaluate nowcasts against the vintage available at
prediction time, not against today's revised history (ties back to §2's as-of check).

## 5. Fail loudly

A validation step that can be defeated by a silent fallback is not a validation step. The failure
mode is always the same shape: an upstream problem gets caught and replaced by a value that looks
fine, so the error never surfaces. Three patterns to hunt, all drawn from real pipelines:

- **Silent cache fallback.** `if cache.exists(): return read(cache)` will happily serve a stale
  or partial cache after a failed refresh. A fetch that falls back to cache *on network error*
  masks the outage entirely. Make staleness an explicit decision: log which path was taken,
  record the cache's vintage in the output, and let a refresh failure raise rather than silently
  serving yesterday's data.
- **`fill_null` on a denominator.** `pl.col("qcew_employment").fill_null(1)` turns a *missing*
  benchmark into a finite, plausible-looking coverage ratio — it is simultaneously an accuracy bug
  and a fail-loud bug in one line. A missing denominator means the join didn't match; the right
  response is to surface the unmatched keys, not to invent a 1. Reserve `fill_null` for values
  that are genuinely, definitionally zero.
- **`except: pass` / broad swallow.** A bare except around a parse or a fetch converts a hard
  failure into a quietly empty or default-valued frame. Catch narrowly, re-raise what you can't
  handle, and never let an empty DataFrame stand in for "the step failed."

The test for any of these: would the pipeline have produced *visibly the same output* if the
input had been broken? If yes, the check is decorative.

## 6. Emit a validation report

Code without a written verdict is incomplete — the report is the audit trail someone reads when
the number is later questioned. Keep this structure verbatim so reports are comparable across
runs; expand the prose with problem-specific context. Write it to `<slug>/validation_report.md`.

```markdown
# Validation Report — <dataset or analysis name>

- **Mode:** dataset QA | analysis QA
- **Validated:** <input path>  (hash: <content_hash>, vintage: <release date / as-of>)
- **Validator:** <name>   **Date:** <YYYY-MM-DD>   **Verdict:** PASS | PASS-WITH-WARNINGS | FAIL

## 1. Schema & integrity
- Schema contract: PASS/FAIL — <columns, dtypes, grain confirmed>
- Nulls / uniqueness / duplicates: PASS/FAIL — <counts>
- Value ranges & cardinality: PASS/WARN — <ranges checked, anomalies>

## 2. Reproducibility & determinism
- Re-run parity: PASS/FAIL — <hash match? two runs>
- Seeds fixed & descriptive: PASS/FAIL — <seed source>
- Inputs pinned / vintaged: PASS/FAIL — <pins>
- As-of / no future leakage: PASS/FAIL/N-A — <boundary checked or why unverifiable>

## 3. Accuracy
- Benchmark reconciliation: PASS/WARN/FAIL — <benchmark, max residual, tolerance>
- Units / scale / sign: PASS/FAIL — <alignment confirmed>
- Edge periods: PASS/WARN — <first/last/pandemic/breaks inspected>

## 4. Methodology & bias
- Conclusions supported: PASS/WARN/FAIL — <claim → evidence map>
- Within vs composition: PASS/WARN/FAIL — <both terms computed? simplifications named>
- Coverage / selection / survivorship / revision: PASS/WARN — <biases assessed>

## 5. Fail-loud audit
- Silent fallbacks / fill_null on denominators / swallowed errors: PASS/FAIL — <findings>

## Blocking issues
1. <must-fix before sharing>

## Warnings (non-blocking)
1. <should-fix or document>
```

A `FAIL` on any §1–2 line is blocking — integrity and reproducibility are preconditions, not
trade-offs. A `WARN` on §3–4 is a documented caveat the consumer must see, not a silent omission.

## Common mistakes

- **Asserting "the numbers look right" without an independent check.** Self-consistency is not
  accuracy. If nothing outside the pipeline confirmed the total, it is unconfirmed.
- **Hashing raw serialization for repro checks.** Row reordering from `group_by`/joins/parquet
  produces false failures. Canonicalize (sort columns, sort rows, sort hashes) before hashing.
- **`fill_null(1)` on a join denominator.** Converts an unmatched key into a believable ratio.
  Surface the unmatched keys instead.
- **A decomposition term hardcoded to a constant.** `pl.lit(0.0).alias("composition_effect")`
  with the remainder dumped into the other term is a relabeling, not a decomposition. Compute it
  or name the assumption.
- **Inner-joining to a benchmark and reporting the overlap as the whole.** Dropped edge periods
  hide the divergence. Check both row counts.
- **Comparing across units without aligning first.** CES thousands vs QCEW persons; rates as
  fractions vs percent. A ~1000× residual is a units bug.
- **Trusting a cache that may be stale.** A fetch that falls back to cache on error masks the
  outage. Record the served vintage and let refresh failures raise.
- **Evaluating a nowcast on revised data.** Final-vintage history flatters a model that never saw
  it. Score against the real-time vintage.
- **Generalizing provider microdata to the population.** Self-selected coverage is not a random
  sample. Quantify the skew against QCEW before claiming an economy-wide trend.
- **Treating a passing schema as a passing dataset.** Right dtypes, wrong grain passes every type
  check and corrupts every aggregate. Confirm the grain.
- **No `published_date`, so the as-of check is skipped and called a pass.** Inability to verify
  the knowability boundary is a finding, not a green light.
