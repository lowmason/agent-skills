---
note: anonymized copy of the llm-wiki pilot source page, the golden file of test_distill_specs.py; release-stats and the commit hashes are made up
---


### [d-01] Flat files primary; BLS API v2 demoted to utility
kind: decision · at: release-stats specs/completed/release-stats-architecture.md §6.1 · basis: git:abc0002
BLS API v2 quotas (500 queries/day, 50 series/query, 50 req/10s) cannot carry
full-universe daily ingest — the CES+CPS Employment Situation morning alone
needs 841 or more queries. LABSTAT flat files are re-stamped at the embargo
minute (verified: 08:30 ET for ce/ln, 10:00 ET for jt/sm/bd), so one HTTP GET
delivers the same-morning vintage with Last-Modified doubling as vintage
verification; the API is only worth keeping for targeted pulls and spot checks.

### [d-02] Backfill honesty rule: never fabricate unobserved prints
kind: decision · at: release-stats specs/completed/release-stats-architecture.md §4.3 · basis: git:abc0002
When seeding a vintage store from bulk files, unobserved print history must be
stamped null or recorded as explicitly missed, never reconstructed — bulk files
contain only the current vintage, so print history is capturable only from the
day live tracking starts. Structurally derivable counters (a release's own
print slots) are the exception: correct even for periods predating tracking.

### [d-03] Deny back-dated releases when the source serves only its current file
kind: decision · at: release-stats specs/plans/completed/2-audit_1-1-26.md Task 2 · basis: git:abc0003
When a source serves only its current file, a vintage pipeline must refuse to
fetch back-dated releases during outage catch-up or bootstrap: stamping today's
file with an old release date fabricates a historical print. Record those slots
as missed, visible to the gap audit, and recover history only through the
dedicated backfill path.

### [d-04] Deferred slots expire by supersession, not wall-clock
kind: decision · at: release-stats specs/plans/completed/1-release-stats-architecture.md L3815 · basis: git:abc0004
A deferred, not-yet-fresh vintage fetch is marked permanently missed only when
a newer release of the same source has been ingested — its live-vintage window
has provably closed — never by an elapsed-time timeout. Supersession is the
event that makes the print unrecoverable; wall-clock deadlines would
misclassify slow or shutdown-delayed releases.

### [d-05] Calendar filter passes pre-coverage periods through
kind: decision · at: release-stats specs/completed/release-stats-architecture.md §5.4 · basis: git:abc0005
When filtering historical periods against a release calendar whose coverage is
shorter than the data (CES flat files start 1939), periods predating calendar
coverage must pass through — presence in the official bulk file is itself proof
of publication, and strict calendar membership would silently discard decades
of history. Only drop periods later than the latest published reference date or
explicitly recorded as cancelled.

### [d-06] Retain cancelled-then-rescheduled releases in the calendar
kind: decision · at: release-stats specs/completed/audit_1-1-26.md §3.1 C-25 · basis: git:abc0003
A release-calendar cancel-drop rule must distinguish cancelled-and-never-
published (drop) from cancelled-then-republished-under-a-rescheduled-date
(retain) — government shutdowns produce the latter, as with CES October 2025,
and a naive null-release-date drop permanently omits such periods from any
store first seeded after the shutdown. Decided by human adjudication of a 1-1
verifier split, 2026-07-05.

### [g-01] BLS API v2 hides errors in HTTP 200 responses
kind: gotcha · at: release-stats specs/completed/release-stats-architecture.md §6.1 · basis: git:abc0002
The BLS API v2 returns errors as HTTP 200 with status REQUEST_SUCCEEDED and the
actual failure buried in the message array (verified live), so clients must
inspect the message array — status-code checking alone silently accepts failed
requests. Registered keys also expire annually.

### [g-02] BLS release feeds: Atom despite .rss; link href is the only stable key
kind: gotcha · at: release-stats specs/completed/release-stats-architecture.md §5.2 · basis: git:abc0002
BLS release feeds are Atom 1.0 despite the .rss extension, retain only 12
entries, and the only stable entry identity is the archive link href with the
release date embedded — Atom ids get edited in place, titles give the reference
month but never the year, and timestamps are unreliable. Infer the year as the
latest occurrence of that month strictly before the release date; correct even
for shutdown-lagged releases.

### [g-03] Benchmark releases detected structurally, never from wording
kind: gotcha · at: release-stats specs/plans/completed/1-release-stats-architecture.md L1525 · basis: git:abc0004
BLS feeds and release titles carry no textual marker for benchmark releases;
benchmark status must be derived structurally from the reference period per
program — CES-style: the release carrying January data is the annual benchmark;
quarterly programs: the release carrying Q1 data.

### [g-04] BLS feeds are hand-edited; flat files flip in place
kind: gotcha · at: release-stats specs/completed/audit_1-1-26.md C-2 · basis: git:abc0006
BLS release feeds are manually hand-edited (typo'd entries are realistic and
persist for weeks) and retain roughly 12 entries, about a year for monthly
programs, while LABSTAT flat files are overwritten in place — so any release
missed while ingestion is down is permanently unobservable as a vintage, and
feed parsers must tolerate malformed entries by skip-and-warn.

### [g-05] LABSTAT files: space-padded headers and M13 annual rows
kind: gotcha · at: release-stats specs/plans/completed/1-release-stats-architecture.md L2611 · basis: git:abc0007
BLS LABSTAT tab-separated flat files have space-padded column headers and cell
values — both must be stripped; the padding broke parsing in practice — and
they interleave M13 annual-average period rows with monthly data. Monthly-series
parsers must drop M13 and annual rows or annual averages contaminate the series.

### [g-06] QCEW area_fips has alpha codes and leading zeros
kind: gotcha · at: release-stats specs/plans/completed/1-release-stats-architecture.md L2747 · basis: git:abc0004
QCEW's area_fips column is not numeric: it mixes alpha aggregate codes such as
C1010 for MSAs with zero-padded county FIPS such as 01001, so it — like all BLS
code columns — must be read and stored as strings; numeric type inference
silently corrupts the keys.

### [g-07] Catch-up ingest of the current file fabricates historical vintages
kind: gotcha · at: release-stats specs/completed/audit_1-1-26.md C-14 · basis: git:abc0008
In a point-in-time pipeline over sources that overwrite files in place,
catch-up after an outage must never fetch the current latest-revised file and
stamp it with a missed release's historical date — that fabricates a first
print a backtest would read as what was actually published. Missed vintages are
unrecoverable; record them as gaps or as snapshot-dated backfill vintages with
null revision counters.

### [g-08] Calendar cancellation is per-row; rescheduled periods have both rows
kind: gotcha · at: release-stats specs/plans/completed/2-audit_1-1-26.md Task 8 · basis: git:abc0003
In release-calendar data, cancellation and publication are separate rows for
the same reference period: a release cancelled then rescheduled yields both a
null-release-date row and a published row. Compute dropped periods as the
cancelled set minus the ever-published set; treating any null row as
cancellation permanently drops rescheduled-then-published periods.

### [c-01] QCEW year-to-date revision structure per quarterly release
kind: resolved-confusion · at: release-stats specs/plans/completed/2-audit_1-1-26.md Task 20 · basis: git:abc0003
QCEW publishes year-to-date files: the release for quarter q re-carries every
earlier quarter of the year, with carried quarter k at its (q minus k)-th
revision, so a quarter reaches its terminal within-year revision only at the
year's Q4 release. Prior-year quarters are additionally republished in annual
benchmark windows. Records the correction of a wrong documented formula.

### [c-02] Backfill is the comparator baseline, so it is not gated by validation
kind: resolved-confusion · at: release-stats specs/completed/audit_1-1-26.md §3 V4 · basis: git:abc0008
When validation gates are defined relative to a trusted baseline, the backfill
path that seeds that baseline cannot itself run those gates — validating the
baseline against itself is circular — so backfill legitimately relies on
parse-layer type locks and the store's schema gate only. Adjudicated
correct-by-design; the actual defect was documentation claiming validation runs
before every commit.

### [p-01] Freshness check: Last-Modified versus scheduled embargo
kind: validated-pattern · at: release-stats specs/plans/completed/1-release-stats-architecture.md L2662 · basis: git:abc0004
BLS flat files are overwritten in place with no versioning, so on release
morning the file at the increment URL can still be the previous vintage. Decide
freshness by comparing the file's HTTP Last-Modified header against the
release's scheduled embargo time; if the file predates the embargo, defer
ingestion rather than committing a stale vintage.

### [p-02] Three-lens adversarial verification with 2-of-3 quorum
kind: validated-pattern · at: release-stats specs/completed/audit_1-1-26.md §1 · basis: git:abc0006
Adversarial codebase audits work as dimension-scoped finders whose raw findings
each face three verifiers with distinct lenses — reachability, spec-alignment,
and materiality — with at least 2 of 3 upheld votes required to confirm. On
release-stats this adjudicated 40 raw findings to 25 confirmed with zero left
unadjudicated.

### [p-03] Keep refuted-at-severity findings as recorded sub-threshold items
kind: validated-pattern · at: release-stats specs/completed/audit_1-1-26.md §3 · basis: git:abc0008
When verification reproduces a finding's mechanism but refutes its severity,
record it as a downgraded sub-threshold item instead of silently dropping it —
several such items justify cheap hardening fixes, and any may be re-raised if
the neutralizing assumption changes. In-file proof: contested V15 was later
re-raised and became confirmed finding C-25.

### [p-04] Reconcile human vs agent verification disagreements explicitly
kind: validated-pattern · at: release-stats specs/completed/audit_1-1-26.md §1.1 · basis: git:abc0008
When an automated verification pass contradicts your own hand-verification,
reconcile the disagreement explicitly in the record rather than silently
trusting either side. In the release-stats audit this caught a human category
error on V14 — two different regexes parse release dates versus reference
periods — and the finding was downgraded honestly.
