# Decision examples

Compact sketches of real decisions: the decision, the trade-off that actually drives it, and the
real alternatives. Each group is dated to the project state it describes. Use them as models for
a Decision or Alternatives section, and tune the pattern to the repo you are in. Do not copy a
decision you have not weighed.

## NFP nowcasting (the `alt-nfp` family, late 2025)

These five come from the `alt-nfp` project as it stood in late 2025, before a 2026-09 split
turned it into `alt-nfp-stats` and `alt-nfp-model`. They describe that state, not the current
repos.

**1. Inference engine: NumPyro/JAX over PyMC (the flagship).** The same nowcast ran three ways
across repos (NumPyro/JAX in `alt-nfp`; PyMC in `alt_nfp` and `oi-indices`). `alt-nfp` chose JAX
for `vmap`-batched fitting over the as-of grid, GPU as the speed lever, and float64 parity gates
against the frozen PyMC reference. Cost: a full rewrite, an ongoing parity-gate maintenance
burden, and a familiarity split across the three repos. Alternatives: stay on PyMC (ergonomics,
`nutpie`, team fluency — rejected for batching/GPU); Stan (fast but a second language and weaker
Python data interop); BlackJAX (same JAX upside, more boilerplate than NumPyro). Worked in full
in the reference file — this is the decision whose absence motivated the whole skill.

**2. Parquet store layout & dedup/vintage policy.** Decision: store **levels only**, partitioned
Hive-style by `(source, seasonally_adj)`, with `vintage_date` / `revision` tags; derive log-growth
at *read* time per cohort. Trade-off: read-time derivation costs CPU on every panel build, but
keeps the store small, append-friendly, and free of precomputed-growth staleness bugs.
Alternatives: store growth precomputed (rejected — every revision invalidates it, and the growth
convention is still an open scoring question); one flat file (rejected — no partition pruning,
forces full scans). Dedup: last-writer-wins on `(series_id, ref_date, vintage_date)`; never
mutate in place — rebuild to a scratch prefix and promote.

**3. Scraper resilience: retry policy + recorded fixtures.** Decision: bounded exponential backoff
with jitter on the BLS/FRED HTTP layer (`httpx`/`curl-cffi`), plus checked-in HTML/JSON **fixtures**
so parsers (`BeautifulSoup`/`lxml`) are tested offline and CI runs without network. Trade-off:
fixtures go stale when BLS changes page structure, so you need a refresh path — but the alternative
(live-network tests) is flaky and unrunnable in CI. Alternatives: retry-only, no fixtures (rejected
— can't test the parser, can't run in CI); full VCR-style cassettes (rejected — heavier than the
handful of pages warrant). Mark live tests `network` and exclude them in CI.

**4. As-of / vintage data model: two-layer censoring.** Decision: every backtest sees only what
was knowable on date D via **combined** filtering — `vintage_date ≤ D` *and* `ref_date < D` — then
rank-based revision selection per series. Trade-off: two filters plus a rank are more complex than
one date cut, but each single-filter shortcut leaks future information in a documented way.
Alternatives: `vintage_date`-only or `ref_date`-only (both rejected — settled empirically to leak).
This is a one-way door: get it wrong and every backtest number is silently optimistic. (The
per-program publication lags this censoring depends on are catalogued in `bls-data-context`.)

**5. Multi-package workspace boundaries.** Decision: a `uv` workspace of 5 packages with a
**one-directional import graph** — the data chain (`lookups → download → ingest → vintages`) and a
model package that imports **no `nfp_*`**, consuming a content-hashed `.npz` snapshot as the only
boundary. Trade-off: the artifact seam adds a serialize/hash step, but it makes "the model never
sees a `vintage_date`" a *structural* guarantee (test-enforced), lets the model develop offline
against fixtures, and runs identically on CPU/GPU. Alternative: one package with module discipline
(rejected — discipline isn't enforceable; imports drift).
