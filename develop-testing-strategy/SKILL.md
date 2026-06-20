---
name: develop-testing-strategy
description: >
  Use when designing a test STRATEGY/PLAN for data-science code — web scrapers, Polars
  pipelines, or Bayesian models — that should start from invariants and properties that must
  hold, not from line coverage: when a repo has zero or smoke-test-only tests, when adding the
  first tests to an ETL/scraper/model package, when a scraper silently breaks on a site-layout
  change, when a
  Polars pipeline emits a malformed parquet (wrong schema, dropped rows, exploded null rate,
  duplicate keys, stale data), when a NumPyro/PyMC model needs more than "it ran without
  crashing", when you need parameter recovery / SBC-lite / golden-master parity / determinism
  under a fixed seed, when MCMC tests make CI slow, or when as-of/vintage correctness and
  future-leakage are at stake. Trigger on: "how should we test this", "what tests do we need",
  "test plan", "test strategy", "add tests to", "this has no tests", flaky/slow test suites,
  pytest marker design (network/slow/real_store) and CI exclusions, recorded HTML fixtures vs
  live sites, schema/row-count/null-rate/freshness assertions, reproducibility and seed tests,
  or mentions of httpx, BeautifulSoup, lxml, Polars, parquet, NumPyro, JAX, PyMC, PRNGKey,
  golden master, parity, BLS / QCEW / CES / JOLTS data. Consult this BEFORE writing tests so
  the plan is driven by what must be true, not by chasing a coverage number.
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
---

# Develop a Testing Strategy

## Overview

A test suite is only as good as the questions it asks. The default failure mode in
data-science code is the opposite of under-testing line count — it is testing the wrong thing:
asserting on internal call order, mocking until nothing real runs, or treating "the script
finished" as a pass. The fix is to start from **invariants** — statements that must be true of
any correct run — and write the smallest test that would fail loudly when one breaks.

This skill produces a *plan* before any test code: the invariants, where each is checked, what
fixture it needs, and which marker keeps it out of CI. The three code kinds here — scrapers,
Polars pipelines, Bayesian models — each have a characteristic set of invariants and a
characteristic trap. Work through them in that order; most repos here contain all three.

Coverage percentage is a lagging, gameable proxy. A 90%-covered pipeline that never asserts
its output schema is worse than a 40%-covered one that does. Plan for the invariants; let
coverage be whatever it is.

## This skill vs. its siblings

- **`explore-data`** — *understand* a dataset ad-hoc; discover the invariants and thresholds worth testing.
- **`validate-data`** — *gate* a dataset or analysis once before it ships (a report, not a suite).
- **`develop-testing-strategy` (this skill)** — *automate*: turn invariants into a permanent pytest suite that runs in CI forever.

This skill owns the **automated test plan**. Discover candidate invariants with `explore-data`; for a one-off pre-publication check with no CI, use `validate-data` instead.

## Step 1 — Enumerate invariants before writing any test

For the unit under consideration, write down what must hold regardless of inputs. Group them:

- **Structural** — output has these columns with these dtypes; this array has this shape;
  posterior has these coords/dims.
- **Relational** — keys are unique; subsets partition disjointly; a round trip inverts; two
  code paths agree (golden master / parity).
- **Bounds** — null rate below a threshold; row count in a plausible band; values in a valid
  domain; freshness within an expected window.
- **Reproducibility** — same seed → same output; pinned/vintaged inputs → pinned outputs; no
  data past the as-of boundary leaks in.

Each invariant becomes one focused test. If you cannot state an invariant, you do not yet
understand the unit well enough to test it — that gap is the finding, not a reason to skip.

Pick the cheapest layer that can falsify each invariant. A schema check needs a 3-row
in-memory frame, not a 2 GB parquet. A parse check needs one HTML snippet, not the live site.
A shape check needs 40 MCMC draws, not 4000. Cheap tests run in CI on every push; the
expensive ones go behind a marker (Step 6).

## Step 2 — Web scrapers (httpx / BeautifulSoup / lxml)

The characteristic trap is testing against the live site. A test that hits the network is
slow, flaky, breaks offline, hammers BLS, and — worst — *passes today and silently rots* when
the site relayouts six months from now, exactly when you need it to scream.

**Test the parse, not the fetch.** Separate "get bytes" from "turn bytes into rows" so the
parser is a pure function of an HTML string. Then feed it recorded fixtures:

- Save a real page once to `tests/fixtures/<source>/<page>.html` (download it, commit it, never
  re-fetch in the test). Point the parser at the saved bytes.
- Cover the **edge cases that BLS pages actually throw**: month names (`MARCH 2026`) and
  quarter names (`First Quarter 2025`, `Fourth Quarter 2024`); layout variants across release
  programs (CES vs JOLTS vs QCEW vs BED); embargo-date vs reference-period extraction; missing
  fields; weekend/last-business-day rollback. Each variant is a tiny fixture string and an
  expected parsed value.
- Test the small pure helpers directly — date parsers, period mappers, link extractors —
  exactly as `bls-stats` already does for `_parse_ref_date` and `_last_business_day`. These are
  the highest-value, cheapest tests in a scraper.

**Mark the live test and exclude it from CI.** Keep *one* test that actually fetches, to prove
the request still works, but gate it with `@pytest.mark.network` and deselect it in CI with
`-m "not network"`. Network tests are for a human running them deliberately, not for every push.

**Add a periodic canary to detect layout drift.** Recorded fixtures answer "does my parser
still handle the HTML I saved?" — they cannot answer "did the site change?". Add one canary
(also `@pytest.mark.network`) that fetches the live page and asserts the *anchors the parser
depends on still exist* (the table id, the heading text, the row count is plausible). Run it on
a schedule, not in PR CI. When it fails, the site moved and the fixtures need refreshing — that
is the alarm zero-test scrapers never get.

Copy-paste scaffolds (fixture loader, parametrized edge cases, `httpx.MockTransport` for the
fetch layer, the canary): [references/scraper-tests.md](references/scraper-tests.md).

## Step 3 — Polars pipelines (→ parquet)

A pipeline's contract is its output. Assert the contract; do not re-implement the
transformation inside the test (that only checks the code against itself). The invariants that
catch real production breakage:

These are the same data contracts `validate-data` checks once before shipping — here you codify
them as permanent CI tests, with thresholds you discovered using `explore-data`.

- **Schema** — exact columns and dtypes. `out.schema == {"period": pl.Date, "value": pl.Float64,
  ...}`. This single assertion catches renamed columns, a `Utf8` that should be `Date`, an Int
  that silently became Float, and accidental column drops/adds — the failures that corrupt a
  parquet most quietly.
- **Row-count sanity** — not an exact number (brittle), a *band*: non-empty, and within a
  plausible range for the input (e.g. one row per month-series, no explosion from a bad join).
- **Key uniqueness / dedup** — `out.select(keys).is_duplicated().sum() == 0`. A fan-out join is
  the most common pipeline bug and is invisible until a downstream aggregate doubles.
- **Null-rate bounds** — `out["value"].null_count() / len(out)` below a threshold per column.
  Catches an upstream schema drift or a join that stopped matching.
- **Freshness** — the latest period present is within the expected window of the as-of date
  (e.g. CES for last month is present by mid-this-month). Stale data passes every other check.

**Build minimal in-memory fixtures, not large parquet.** Construct a 3–10 row
`pl.DataFrame` literal in the test, run it through the *real* transform, and write to
`tmp_path` only when the test genuinely exercises round-trip I/O. A handwritten tiny frame is
readable, fast, diffable in review, and lets you craft the exact edge case (a null, a duplicate
key, a boundary date). Reserve real parquet fixtures for a small committed golden sample when
you specifically need to test the reader.

When a transform is itself complex, add a **property** test: e.g. "row count is preserved by
this normalization", "the output is sorted by period", "concatenating then dedup equals dedup
then concatenate". Properties catch classes of bugs that example rows miss.

Reusable schema/uniqueness/null-rate/freshness assertion helpers and a `tmp_path` round-trip
example: [references/pipeline-tests.md](references/pipeline-tests.md).

## Step 4 — Bayesian models (NumPyro / PyMC)

You cannot assert an exact posterior — MCMC is stochastic and the true posterior is unknown. So
"smoke test only" (it sampled without crashing) is where most model packages stop, and it
catches almost nothing. Replace it with four checks that *are* falsifiable:

1. **Determinism under a fixed seed.** Same `PRNGKey` (NumPyro) or `random_seed` (PyMC) and
   same data → bit-identical draws. This is the cheapest, highest-value model test: it guards
   against accidental nondeterminism (an unseeded init, a dict-ordering leak, a non-reproducible
   transform) and makes every other test stable. NumPyro is deterministic given the key on a
   fixed device; assert two runs match with `np.testing.assert_array_equal`.

2. **Parameter recovery on simulated data (SBC-lite).** Simulate data from the model with known
   parameters, fit, and assert the true value lands inside a generous posterior interval (e.g.
   inside the 94% HDI, or within k posterior SDs of the mean). This is the test that "is the
   model implemented correctly?" actually needs — a sign error or a mislinked prior fails it.
   Keep it tiny (small N, short chains, a few parameters) so it can run more often than full
   inference. This is a lightweight stand-in for full Simulation-Based Calibration; the full
   rank-uniformity SBC is a separate, heavier validation, not a CI test.

3. **Shapes / dims / coords.** Assert posterior site shapes against `(chains, draws, *dims)`,
   that deterministics line up with the sites they are built from, and that every array is
   finite. This is exactly the `nfp_model` smoke pattern (`post["tau"].shape == (2, 40)`,
   `np.all(np.isfinite(arr))`, deterministics reconstructed and compared with
   `assert_allclose`). Cheap, and it catches the broadcasting bugs that produce plausible-looking
   garbage.

4. **Golden-master parity within tolerance.** Freeze a reference fit (or summary statistics)
   from a trusted version, then assert a new fit matches within a numerical tolerance —
   `np.testing.assert_allclose(new, golden, rtol=...)`, never exact equality. This is the
   `test_parity_golden` pattern: it guards a port (PyMC→NumPyro), a refactor, or a dependency
   bump from silently shifting results. Document what vintage/store the golden was computed on,
   because data drift, not code, will eventually break it.

**Keep full MCMC behind `@pytest.mark.slow` with a tiny smoke config in CI.** Real inference is
tens of seconds to minutes — not a per-push cost. Define a `TINY` sampler config
(`num_samples=40, num_warmup=40, num_chains=2`, à la `nfp_model`) for the slow smoke and
recovery tests, and let CI run only the millisecond-scale shape/determinism/unit tests by
default. The minutes-long full parity run belongs in a script (`scripts/run_*_parity.py`) and
an opt-in env flag, with the pytest version re-running *one* fixture as a reproducibility guard.

Determinism, SBC-lite recovery, and parity scaffolds for both NumPyro and PyMC:
[references/model-tests.md](references/model-tests.md).

## Step 5 — Reproducibility as a first-class test target

For nowcasting and vintage work, "the same inputs produce the same outputs" is a correctness
property of equal standing to any schema check — and as-of correctness is a property nothing
else will catch. See `bls-data-context` for each BLS program's revision cadence. Plan explicit
tests for:

- **Seeds.** Every stochastic step takes an explicit, descriptive seed (derive it, e.g.
  `sum(map(ord, "name"))`, not a bare `42`; see `bayesian-workflow` for the convention). A test
  fixes the seed and asserts repeatability.
  Unseeded randomness is a bug a determinism test surfaces immediately.
- **Pinned / vintaged inputs.** A run against a frozen input snapshot must produce a frozen
  output. This is the snapshot round-trip idea (`from_snapshot` inverts `collect_snapshot`) and
  the golden-master idea applied to data: pin the vintage, pin the result.
- **No future leakage past the as-of boundary.** The single most dangerous bug in nowcasting:
  a feature built with data published *after* the as-of date inflates backtest accuracy and
  cannot exist in production. Write a test that asserts every input row's *publication/vintage*
  date is `<=` the as-of date, and a backtest test that fails if any feature references a future
  period. This invariant is invisible to schema, shape, and even golden-master tests — it needs
  its own assertion. (`validate-data` runs this as a one-time gate on a single run; this skill
  makes it a standing test. `explore-data` first tells you the vintage layout the test depends on.)

## Step 6 — Marker conventions and CI exclusions

Mirror the marker vocabulary already in use across these repos and declare it in
`pyproject.toml` so unmarked usage errors instead of silently passing:

```toml
[tool.pytest.ini_options]
markers = [
    "network: hits the network (live site / canary); deselect with '-m \"not network\"'",
    "slow: MCMC/sampling tests measured in tens of seconds, not milliseconds",
    "real_store: legitimately reads the real (read-only) vintage store; exempt from the credential-blanking net",
]
```

- **CI default** runs the fast, hermetic tier: `pytest -m "not slow and not network and not real_store"`.
  Every parse test, every schema/uniqueness/null-rate/freshness check, every shape and
  determinism test lives here and must stay millisecond-fast.
- **`slow`** — full MCMC, parameter recovery, end-to-end pipeline. A nightly or pre-merge job,
  or a manual `pytest -m slow`.
- **`network`** — the one live fetch and the canary. Scheduled, never in PR CI.
- **`real_store`** — anything touching the real vintage store. Fail closed by default: an
  *unmarked* test that reaches the store should be blocked (the `alt-nfp` conftest blanks
  credentials and severs the s3fs path for unmarked tests precisely so a stray write cannot
  destroy irreplaceable data). Opt in deliberately with the marker for read-only access.

State the exact CI command in the plan so "excluded from CI" is concrete, not aspirational.

## Common mistakes and anti-patterns

- **Chasing a coverage number.** Coverage measures lines executed, not invariants checked. A
  test that calls a function and asserts nothing meaningful raises coverage and catches nothing.
  Plan invariants; report coverage as a side effect.
- **Testing implementation details.** Asserting on internal call order, private helper names,
  or "was this method called" couples the test to the code's shape, so every refactor breaks
  tests that found no bug. Assert on observable contracts — the output frame, the parsed value,
  the posterior shape — not on how they were produced.
- **Over-mocking.** Mocking the parser, the transform, and the sampler until only glue remains
  means the test passes while the real logic is broken. Mock the *boundary* (the network fetch,
  the clock, the store) and run the real logic against real fixtures. If a test would still pass
  with the function body deleted, it is testing the mock.
- **Testing against the live site.** Covered in Step 2: slow, flaky, and it rots silently.
  Recorded fixtures plus a marked canary instead.
- **Asserting on plot output.** Comparing image bytes or pixel hashes is brittle, hard to
  diagnose, and tests the rendering library, not your model. Assert on the *data behind* the
  plot (the summary table, the HDI bounds, the calibration statistic), and let plotting be
  visually reviewed.
- **Asserting exact MCMC numbers.** Posteriors are stochastic; exact-equality parity breaks on
  any platform or dependency change. Use tolerances (`assert_allclose`, interval containment),
  and reserve exact equality for the determinism test (same seed, same device).
- **Re-implementing the transform in the test.** If the test computes the expected output the
  same way the code does, it only proves the code equals itself. Hand-write the expected value,
  or assert a property (uniqueness, preserved row count, invertibility) instead.
- **Giant binary fixtures.** Multi-megabyte committed parquet/HTML are slow to load, opaque in
  review, and tempt re-fetching. Prefer tiny in-memory frames and short HTML snippets; commit a
  real sample only when you must test the reader itself, and keep it small.
- **A smoke test masquerading as model validation.** "It sampled" is necessary, not sufficient.
  Pair every smoke test with at least a determinism check and a parameter-recovery check, or the
  model is effectively untested.
