# BLS Data Acquisition: API v2, LABSTAT Flat Files, and Release Feeds

Cross-program mechanics for getting BLS data into a pipeline: what the v2 API can and cannot
carry, how the LABSTAT flat-file service behaves at release time, how the release feeds are
structured, and how to detect benchmark releases. Program-specific schema and series-ID
anatomy live in the per-program references; this file covers the transport layer they all
share.

## Provenance and verification status

Unlike the program references, which digest official BLS methodology pages, the facts here
describe *observed service behavior* — most of it undocumented — verified live against BLS
endpoints during construction of a daily ingestion pipeline (2025–2026 vintage). Service
behavior can change without notice and without documentation. Re-verify quotas, embargo
times, and feed structure against the live endpoints before hard-coding them.

## Agent rules of thumb

1. Full-universe or scheduled work runs on LABSTAT flat files, not the API — the v2 quotas
   cannot carry it.
2. Never treat HTTP 200 or `status: REQUEST_SUCCEEDED` from the v2 API as success; read the
   `message` array and check that data actually came back per series.
3. Treat `Last-Modified` on a LABSTAT file as the release's vintage stamp — it is re-set at
   the embargo minute.
4. Archive a snapshot of every LABSTAT file you ingest: files are overwritten in place, so a
   missed release is a permanently lost vintage.
5. Strip whitespace from LABSTAT headers *and* cell values — the files are space-padded.
6. Key feed entries by the archive-link href, never by Atom id or title.
7. Derive benchmark status structurally from the reference period, never from release text.

## Channel selection: API v2 vs LABSTAT flat files

The v2 API (`api.bls.gov/publicAPI/v2/timeseries/data/`) with a registered key is
quota-limited to:

```text
500 queries per day
50 series per query
50 requests per 10 seconds
```

That is at most 25,000 series fetched per day — orders of magnitude short of a full-universe
daily ingest for any major program (CES alone publishes thousands of series; the QCEW
universe runs to millions of cells). Consequences:

- Use the API for narrow, interactive retrieval: a handful of headline series, a spot check,
  filling a small gap.
- Use the LABSTAT flat files (`download.bls.gov/pub/time.series/<prefix>/`) for anything
  full-universe, full-history, or on a schedule.
- Registered API keys expire annually. Build key renewal into any pipeline expected to run
  unattended for more than a year, and alert on auth-related messages rather than letting
  the key lapse silently.

## API v2 error semantics

Verified live: the v2 API returns failures as **HTTP 200 with top-level
`status: "REQUEST_SUCCEEDED"`**, reporting the actual failure only in the `message` array.
An unknown series, for example, comes back "successful" with a message such as
`Series does not exist for Series id: ...` and no data for that series.

Agent guidance:

- Success checking must inspect the `message` array and the per-series presence of data. The
  HTTP status code and the top-level `status` field are not failure signals.
- A pipeline that branches only on HTTP status or on `status == "REQUEST_SUCCEEDED"`
  silently ingests empty results.

## LABSTAT flat-file service behavior at release time

The files under `download.bls.gov/pub/time.series/<prefix>/` are **overwritten in place** at
each release. There are no versioned or dated copies on the server.

- Files are **re-stamped at the embargo minute**: the HTTP `Last-Modified` header lands on
  the official release time — verified at 08:30 ET for `ce` (CES) and `ln` (CPS), and
  10:00 ET for `jt` (JOLTS), `sm` (SAE), and `bd` (BED). `Last-Modified` therefore doubles
  as **vintage verification**: it identifies *which release* a downloaded file belongs to,
  not merely when a file was touched.
- Because files are replaced in place, **a release missed while ingestion is down is
  permanently unobservable as a vintage** — the prior file state is gone and BLS keeps no
  archive. If revision history or as-of correctness matters, archive your own snapshot of
  every file at every release.
- To detect a release, poll `Last-Modified` with a HEAD request rather than re-downloading
  and diffing.

### Parsing the tab-separated files

- Headers **and** cell values are space-padded — strip whitespace from both before use. An
  unstripped join key (a `series_id` with trailing spaces) matches nothing, so joins empty
  out silently instead of erroring.
- Monthly data files interleave `M13` annual-average rows with the monthly `M01`–`M12` rows;
  filter by period before time-series work. Period-code rules per program are in the hub
  SKILL.md.

## Release feeds (`bls.gov/feed/*.rss`)

The per-program release feeds are **Atom 1.0 documents despite the `.rss` extension** —
parse them as Atom, not RSS 2.0.

- Feeds retain only **about 12 entries**. An ingestion outage longer than the feed window
  loses release events unrecoverably from the feed; pair feed polling with `Last-Modified`
  polling on the flat files as a backstop.
- The **only stable entry key is the archive link href**, of the form
  `.../archives/{slug}_MMDDYYYY.htm`. Atom `id` values are **edited in place** after
  publication, so they are not reliable dedup keys.
- **Titles carry the reference month but never the year.** Derive the year from the
  `MMDDYYYY` date in the archive-link URL, not from the title.
- Feeds are **hand-edited**: typos and malformed fragments appear and persist for weeks.
  Parse defensively — tolerate irregular whitespace, casing, and spelling in titles, and
  never make strict title parsing load-bearing.

## Detecting benchmark releases

Benchmark releases carry **no textual marker** in the feeds or release titles — nothing says
"benchmark". Benchmark status must be derived **structurally from the reference period** of
the release:

```text
CES (annual March benchmark):  the release covering January data
                               (published in February) is the benchmark release.
Quarterly programs (QCEW
finalization, BED annual
revision):                     the release covering Q1 data is the
                               benchmark / annual-revision release.
```

Agent guidance: encode benchmark detection as a rule on the reference period, and treat any
release matching the rule as one that revises history, with the per-program revision spans
given in the hub's revision table and each program reference.

## Common pitfalls

- Scheduling a full-universe ingest against the v2 API and hitting the 500-query/day wall
  mid-run.
- Treating HTTP 200 / `REQUEST_SUCCEEDED` as success and ingesting empty payloads.
- Letting a registered API key expire silently at the one-year mark.
- Using feed Atom ids or titles as dedup keys (both mutate), or reading a year off a feed
  title (titles never carry one).
- Parsing the `.rss` feeds with an RSS 2.0 parser instead of an Atom parser.
- Assuming a missed release can be re-fetched later — flat files are overwritten in place.
- Joining on an unstripped, space-padded `series_id` and silently matching zero rows.
- Grepping release text for "benchmark" — the marker does not exist; use the reference
  period.
