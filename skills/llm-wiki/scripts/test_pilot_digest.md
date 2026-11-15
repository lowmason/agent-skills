---
note: anonymized copy of the llm-wiki pilot digest, the golden file of test_distill_specs.py; release-stats and the commit hashes are made up
---

[d-01] Flat files primary; BLS API v2 demoted to utility
at: specs/completed/release-stats-architecture.md §6.1 · sha: abc0002
excerpt: "The BLS API v2 **cannot** carry full-universe daily increments on one
registered key (500 queries/day, 50 series/query, 50 req/10s; one query returns
all periods in a <=20-year window, so queries scale with series count only)"

[d-02] Backfill honesty rule: never fabricate unobserved prints
at: specs/completed/release-stats-architecture.md §4.3 · sha: abc0002
excerpt: "**Backfill honesty rule:** stage-1 rows get `release_date` = snapshot
date and `revision` / `benchmark` = **null** — print history that was never
observed is not fabricated."

[d-03] Deny back-dated releases when the source serves only its current file
at: specs/plans/completed/2-audit_1-1-26.md Task 2 (L176) · sha: abc0003
excerpt: "`_fetch_event` always downloads the *current* LABSTAT file, so an
older release gets stamped with its old `release_date` but carries today's
revised values — the clairvoyance the vintage model exists to prevent."

[d-04] Deferred slots expire by supersession, not wall-clock
at: specs/plans/completed/1-release-stats-architecture.md L3815 · sha: abc0004
excerpt: "a deferred slot whose live-vintage window closed (a newer release for
the same program ingested) transitions to missed — never by wall-clock timeout."

[d-05] Calendar filter passes pre-coverage periods through
at: specs/completed/release-stats-architecture.md §5.4 · sha: abc0005
excerpt: "**Periods predating calendar coverage pass through** — their presence
in the bulk file proves publication. Strict membership against the calendar
would silently discard decades of history."

[d-06] Retain cancelled-then-rescheduled releases in the calendar
at: specs/completed/audit_1-1-26.md §3.1 C-25 · sha: abc0003
excerpt: "**Decision (human, 2026-07-05): the post-shutdown-seeding case IS in
scope.** The lapse overlay / `filter_published` must distinguish \"cancelled and
never published\" (stays dropped) from \"rescheduled and later published\" (must
be retained)."

[g-01] BLS API v2 hides errors in HTTP 200 responses
at: specs/completed/release-stats-architecture.md §6.1 · sha: abc0002
  (also specs/plans/completed/1-release-stats-architecture.md L3204 · sha: abc0004)
excerpt: "**must check the response `message` array** — BLS returns errors as
HTTP 200 + \"status\": \"REQUEST_SUCCEEDED\" with the failure in `message`
(verified live)"

[g-02] BLS release feeds: Atom despite .rss; link href is the only stable key
at: specs/completed/release-stats-architecture.md §5.2 · sha: abc0002
  (also specs/plans/completed/1-release-stats-architecture.md L1525 · sha: abc0004)
excerpt: "**Stable identity key is the link href**
(`…/archives/{feed}_{MMDDYYYY}.htm`, release date embedded). The Atom `id` is
**not** stable (observed edited in place on `cewbd`)."

[g-03] Benchmark releases detected structurally, never from wording
at: specs/plans/completed/1-release-stats-architecture.md L1525 · sha: abc0004
excerpt: "**no benchmark wording exists** — `is_benchmark` comes from the
profile's structural rule (`jan_data`: monthly ref month == 1; `q1_data`:
quarterly ref quarter == 1)"

[g-04] BLS feeds are hand-edited; flat files flip in place
at: specs/completed/audit_1-1-26.md C-2 · sha: abc0006
excerpt: "BLS hand-edits these feeds — the module itself notes ids edited in
place — so a typo'd filename is realistic and persists for weeks; vintages
missed while the cron is down are permanently unobservable because flat files
flip in place."

[g-05] LABSTAT files: space-padded headers and M13 annual rows
at: specs/plans/completed/1-release-stats-architecture.md L2611 · sha: abc0007
excerpt: ".rename(lambda c: c.strip())  # LABSTAT headers are space-padded /
.with_columns(pl.col(\"series_id\", \"period\", \"value\",
\"footnote_codes\").str.strip_chars()) / .filter(pl.col(\"period\")
.str.contains(period_re))  # drops M13 (BEH §2.1)"
note: sha abc0007 is a dedicated fix commit whose message records the empirical
failure (padded header silently broke schema_overrides).

[g-06] QCEW area_fips has alpha codes and leading zeros
at: specs/plans/completed/1-release-stats-architecture.md L2747 · sha: abc0004
excerpt: "def test_area_fips_stays_utf8_with_alpha_codes() -> None:  # BEH §2.2
critical gotcha / assert df.schema[\"area_fips\"] == pl.Utf8 / assert \"C1010\"
in df[\"area_fips\"].to_list()"

[g-07] Catch-up ingest of the current file fabricates historical vintages
at: specs/completed/audit_1-1-26.md C-14 · sha: abc0008
excerpt: "The result is a vintage row claiming an old release date while
carrying today's revised values — exactly the clairvoyance the vintage model
exists to prevent."

[g-08] Calendar cancellation is per-row; rescheduled periods have both rows
at: specs/plans/completed/2-audit_1-1-26.md Task 8 (L656) · sha: abc0003
excerpt: "a period that was cancelled in the schedule but later published under
a rescheduled release has *both* a null-`release_date` row and a non-null one,
so it lands in `cancelled` and is permanently dropped"

[c-01] QCEW year-to-date revision structure per quarterly release
at: specs/plans/completed/2-audit_1-1-26.md Task 20 (L1578) · sha: abc0003
excerpt: "a QCEW release for quarter *q* carries all quarters of the year so
far, each at revision `(q − carried quarter)` — the Q3 release carries Q3 at
revision 0, Q2 at revision 1, Q1 at revision 2."

[c-02] Backfill is the comparator baseline, so it is not gated by validation
at: specs/completed/audit_1-1-26.md §3 V4 · sha: abc0008
  (also specs/plans/completed/2-audit_1-1-26.md Task 6 L516 · sha: abc0003)
excerpt: "`run_backfill` committing without `validate()` is **spec-mandated**
(ARCH §8, §7.3: backfill is the trusted comparator baseline). So the behavior
is correct; the only real issue is the docstring/docs claiming validation
happens"

[p-01] Freshness check: Last-Modified versus scheduled embargo
at: specs/plans/completed/1-release-stats-architecture.md L2662 · sha: abc0004
excerpt: "ARCH §6.3 stale-file guard: Last-Modified >= scheduled embargo on the
release date."

[p-02] Three-lens adversarial verification with 2-of-3 quorum
at: specs/completed/audit_1-1-26.md §1 (L24-28) · sha: abc0006
excerpt: "Every raw finding then faced three adversarial verifiers with
distinct lenses — **reachability** (is the failure path real in the code as
written), **spec-alignment** (is the \"correct\" behavior actually what
ARCH/BEH mandate), and **materiality** (does an existing backstop intercept
it)."

[p-03] Keep refuted-at-severity findings as recorded sub-threshold items
at: specs/completed/audit_1-1-26.md §3 (L566-569) · sha: abc0008
excerpt: "They are recorded — not dropped — because several are worth a cheap
hardening fix and one may be re-raised if assumptions change."
note: in-file proof of value — contested V15 was later re-raised and became
confirmed finding C-25.

[p-04] Reconcile human vs agent verification disagreements explicitly
at: specs/completed/audit_1-1-26.md §1.1 (L47-49) · sha: abc0008
excerpt: "Where the second pass disagreed with my own earlier hand-verification,
I reconciled it in §3.2 rather than silently trusting either — the agents
corrected one of my calls (V14)."

[q-01] QCEW routine print count and touched-set
at: specs/completed/release-stats-architecture.md §12.3
The actual QCEW revision lifecycle (how many routine prints a quarter receives,
which prior quarters each release touches) is an unverified BLS-data-source
fact any implementation would face again.

[q-02] Benchmark revision reach per BLS program
at: specs/completed/release-stats-architecture.md §12.5
  (also specs/plans/completed/1-release-stats-architecture.md L398)
How far back each program's annual benchmark actually revises is unverified;
the configured windows (sae/jolts/cps 5y, bed 2y, qcew 1y) await confirmation
against observed benchmark events.
