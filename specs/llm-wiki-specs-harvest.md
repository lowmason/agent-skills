# llm-wiki specs-harvest framework

**Status:** design — approved via brainstorming 2026-07-24; awaiting implementation plan
**Companions:** `skills/llm-wiki/` (skill + bundled scripts); the wiki root's `SCHEMA.md` (root copy governs, human-gated); `specs/completed/llm-wiki-spec.md` (the wiki's own spec, esp. §3 boundary rule, §16 session digests, §13 P2 deferred code-wiki root)

## 1. TL;DR

1. A generic, repo-agnostic avenue for turning a pre-existing repo's `specs/` tree
   (specs, completed specs, completed plans, deferred items) into research-wiki
   content, structured so the mechanical stages are scripted, the judgment stages
   are agent+human procedure, and the human tick remains the gate in front of
   `raw/`.
2. Three artifacts: a new `distill_specs.py` (subcommands `inventory` and
   `assemble`) beside the session distiller; a new **harvest** operation in the
   llm-wiki SKILL.md; a contract extension (`SCHEMA.md` + `schema-template.md` +
   `lint_wiki.py`) codifying the `raw/specs/` class, the `at:` capture locator,
   and the brief format, and extending secret/echo-rule lint to `raw/specs/`.
3. Grounded in a completed pilot (bls-stats, 2026-07-24): 5 files → 32 proposed
   captures → 32 survived adversarial verification → 28 after spec↔plan dedup →
   20 human-ticked into the live digest `raw/specs/2026-07-24-bls-stats-specs-harvest.md`
   and source page (research wiki). The pilot artifacts are the reference
   instances for the formats below.

## 2. Motivation and pilot evidence

The session distiller covers conversation history, but pre-existing repos carry a
denser, already-human-approved record: their spec/plan corpora (agent-skills 30
files, alt-nfp 79, bls-stats 5, all sharing the specs/ convention). The pilot
established:

- **Precision-first extraction + independent adversarial verification works:**
  100% capture survival (32/32), with verifiers pickaxe-correcting several
  introducing SHAs past mechanical retirement/reorg commits.
- **Completed plans are first-class inputs**, not echoes: they matched specs
  capture-for-capture (16 vs 16) and contributed unique classes — library
  gotchas, review-caught fixes, dedicated fix commits (the strongest provenance
  in the set, e.g. bls-stats `50e0f52`).
- **`deferred_items.md` is near-noise:** 15/15 entries and 27/29 open-question
  candidates overall were repo-local backlog. It stays in the walk but is
  demoted to lowest priority; expected yield is open questions only, rarely.
- **A spec↔plan dedup stage is required:** 4 of 32 captures were cross-file
  duplicates (plan text echoing its spec); merged entries carry multi-source
  `at:` lines.
- **SHA archaeology and seed inventory are mechanizable; extraction is not:**
  much of the yield was interleaved prose no seed regex can see, so whole-file
  agent reading is mandatory and seed hits are prompts, not bounds.

## 3. Scope and non-goals

**In scope:** the three artifacts of §4; the formats of §5; tests of §9.

**Non-goals (recorded so they are not re-litigated):**
- No `docs/` or ADR-directory input class in v1 (alt-nfp's `docs/` rationale
  records are a noted future input class).
- No code-wiki root. The engineering-stratum captures parked by the pilot
  (Appendix A) are that root's seed content if/when the llm-wiki spec's P2
  deferral is taken up; this framework must not block or assume it.
- No git-history delta mining (hunks/lifecycle events as capture units) and no
  read-path-only alternative (§10); both were considered and set aside.
- No prospective capture emission at plan completion (a separate, composable
  process change).
- No daemons or auto-capture: harvests are supervised runs, matching the wiki's
  no-automation posture.

## 4. Architecture

Three artifacts, mirroring the session-distiller split:

1. **`skills/llm-wiki/scripts/distill_specs.py`** — stdlib-only, deterministic,
   installed to wiki roots by `bootstrap_wiki.py` alongside the existing
   scripts; imports `redact` and `slugify` from `distill_sessions.py` (the
   test-proven sibling-import seam). Subcommands:
   - `inventory <repo> --root <wiki>`: tolerant walk of `specs/`,
     `specs/completed/`, `specs/plans/`, `specs/plans/completed/`,
     `specs/deferred_items.md` (each optional); seed grep; per-file landing-SHA
     table via `git log --follow` with substantive-vs-mechanical commit
     classification (mechanical = every hunk in the commit's diff for that file
     is a pure rename/move with no content change); reads prior briefs for this
     repo and pre-filters
     already-seen items; writes the skeleton brief to `<root>/reports/`.
   - `assemble <brief> --root <wiki>`: validates ticked entries, redacts, writes
     the `raw/specs/` digest atomically, stamps the brief header, emits the
     source-page capture-note body for the ingest step.
   Both commands require explicit paths (no defaults); `assemble` refuses a
   brief whose recorded root mismatches `--root`.
2. **llm-wiki SKILL.md `harvest` operation** (~20 lines, root-generic): run
   inventory → agent extraction (whole-file, at the brief's pinned `repo_head`;
   seeds as prompts) → independent per-file adversarial verification
   (excerpt-verbatim by grep; basis SHA confirmed as the *introducing* commit;
   kind honesty under the echo rule, downgrading where unmet; boundary verdict
   challenged) → spec↔plan dedup and prior-brief/digest dedup → human ticks →
   assemble → normal ingest flow. Extraction policy stated as hard rules:
   transferable or mixed-with-standalone-claim content only; proprietary
   stratum (e.g. provider specifics) never enters a brief.
3. **Contract extension** — root `SCHEMA.md` (human-gated edit + `schema` log
   line) codifies: the `raw/specs/` raw class; the capture metadata variant
   `kind: … · at: <repo> <path> <section> · basis: git:<sha>` (replacing the
   session-digest `turns:` field); the brief format and its tick semantics.
   `scripts/schema-template.md` gains the same sections so bootstrapped wikis
   inherit them. `lint_wiki.py` extends the secret-pattern scan and the
   decision-basis (echo-rule) check from `raw/sessions/*.md` to
   `raw/specs/*.md`.

## 5. Formats

Reference instances: the pilot digest
(`raw/specs/2026-07-24-bls-stats-specs-harvest.md`) and source page
(`wiki/sources/` same stem) in the research wiki.

### 5.1 Brief — `<root>/reports/harvest-<repo>-<YYYY-MM-DD>.md`

- **Header:** repo, `repo_head` SHA, wiki root, date, files walked, pointer to
  the prior brief (if any), and after assembly `assembled: <digest-stem>`.
- **Per file:** seed hits (Decision/Rejected markers, `(recorded)` sections,
  TL;DR claim lists, POLICY / Global-Constraints blocks, completion banners and
  Deviation blocks, deferred-items entries); SHA table
  (`sha · subject · substantive|mechanical`); capture entries.
- **Capture entry:** checkbox line with id (`d-NN`/`r-NN`/`g-NN`/`c-NN`/`p-NN`),
  kind, `at:` locator(s), basis SHA, boundary verdict
  (transferable|mixed|code-coupled), verbatim excerpt, claim (1–3 sentences,
  self-contained, no square brackets in claim text — BODY_CITE_RE discipline).
- **Tick semantics:** `[x]` = approved for assembly; unticked entries persist as
  the durable declined record. Idempotence memory: subsequent inventories dedup
  against *all* prior-brief entries (approved and declined), keyed on locator +
  claim hash — never only against what was kept.

### 5.2 Digest — `<root>/raw/specs/<date>-<repo>-specs-<id8>.md`

Piloted format: header (source, repo, `repo_head`, date, counts, method note,
brief pointer, files_read) + per-capture ground-truth entries (id, title, `at:`,
sha, verbatim excerpt, optional note). `id8` is the first 8 hex chars of a
SHA-256 over the ordered ticked-capture content, so re-assembling an unchanged
brief rewrites the identical file (no duplicates, no growth-check semantics).
The hand-authored pilot digest predates the `id8` filename rule and is
grandfathered; it is the reference for content, not for the filename. Open-question entries (`q-NN`) ride in the digest and are appended
to `open-questions.md` at ingest.

### 5.3 Source page — `wiki/sources/<digest-stem>.md`

Standard source frontmatter (`type: source`, `status: unverified`,
`raw: raw/specs/<digest>`) with a capture-note body:
`### [<id>] <title>` / `kind: … · at: … · basis: git:<sha>` / claim. Assemble
emits this body; the agent wraps frontmatter and performs index/log updates in
the normal ingest op. Verification walks capture → digest excerpt → repo file at
the pinned SHA.

## 6. Data flow

1. `inventory` (script; deterministic; re-runnable)
2. Agent extraction into the brief (whole-file reading at `repo_head`)
3. Agent adversarial verification (independent pass, tool-checked, amendments
   visible in the brief)
4. Dedup: spec↔plan merges; prior briefs; existing digests
5. Human ticks (the `raw/` gate)
6. `assemble` (script; validates → redacts → writes digest → stamps brief →
   emits source-page body; per-entry errors, exit 1, nothing written on failure)
7. Existing wiki machinery: backlog INFO queues the digest; `ingest` writes
   source page + index + log; later `verify` flips status. The framework ends at
   step 6.

## 7. Error handling and edge cases

- **Partial conventions:** missing dirs/files → empty inventory sections plus a
  note. No `specs/` at all, or no git history → hard error (SHAs are
  load-bearing).
- **Drift:** extraction/verify read at pinned `repo_head`; `assemble` warns when
  repo HEAD has moved since inventory. Post-`repo_head` edits are the wiki's
  dated-claims staleness, not the script's concern.
- **Scale:** `inventory --only <glob>` batches large corpora (alt-nfp: 79
  files); one brief per repo per date accretes across batches — a same-date
  re-run appends new per-file sections to the existing brief, never overwrites
  it or duplicates a section already present. Skill
  procedure orders completed specs + completed plans first (settled strata);
  live drafts are harvested last if at all.
- **Failure containment:** `assemble` mirrors the session distiller's
  failures-list contract (report all, exit 1, atomic write last).
- **Secrets / proprietary content:** `redact()` at assemble; extended lint as
  backstop; proprietary-stratum exclusion is a hard extraction rule.
- **Wrong-wiki protection:** explicit paths everywhere; brief-root vs `--root`
  match enforced.

## 8. Requirements

- **R1** `distill_specs.py inventory` per §4.1/§5.1 (walk, seeds, SHA tables,
  prior-brief dedup, skeleton brief).
- **R2** `distill_specs.py assemble` per §4.1/§5.2 (validation, redaction,
  atomic digest write, brief stamping, source-page body emission,
  content-hash idempotence).
- **R3** llm-wiki SKILL.md `harvest` operation per §4.2, root-generic, within
  the skill's existing body-budget discipline.
- **R4** `lint_wiki.py`: secret patterns + decision-basis check over
  `raw/specs/*.md`; `at:` metadata lines pass clean; existing 31 lint tests
  unchanged.
- **R5** Root `SCHEMA.md` amendment (human-gated, `schema` log line) and
  matching `scripts/schema-template.md` sections.
- **R6** Test suite per §9; repo gates (`check_frontmatter.py`,
  `check_provenance.py`) pass.

## 9. Testing requirements

TDD; tests beside the existing suites in `skills/llm-wiki/scripts/` under the
same `uv run --python 3.13 --with pytest` harness.

- `inventory`: tmp_path git fixture repos (including a rename-only retirement
  commit); seed detection per pattern; SHA classification; every missing-dir
  permutation; prior-brief dedup; no-git and no-specs error paths.
- `assemble`: hand-ticked fixture brief → golden digest; the real pilot brief →
  pilot digest as a second golden pair; each validation failure class red-tested
  (exit 1, no file); byte-identical re-assembly; root-mismatch refusal.
- Redaction: planted secret in a fixture excerpt never reaches the digest.
- Lint extension: secret in `raw/specs/` = ERROR; decision capture without
  valid basis = ERROR; piloted `at:` line clean; existing lint tests untouched.
- Template parity: bootstrap-seeded `SCHEMA.md` contains the new sections.

## 10. Alternatives considered (recorded)

- **Script as validator only / script as full generator** — rejected for v1:
  the former leaves the measured-mechanizable stages manual; the latter's
  excerpt-boundary regexes are brittle across heterogeneous formats and anchor
  recall to seeds.
- **Wholesale spec ingest; theme dossiers; pointer-registry (no copies);
  federated per-repo roots; second engineering root** — mapped candidates not
  taken for v1; the second root remains the designated home for the parked
  engineering stratum (Appendix A) under the llm-wiki spec's P2 deferral.
- **Git-delta mining** (revision hunks as capture units) — highest-signal for
  decision *corrections*, but unproven signal-to-churn ratio; revisit after two
  or more full-repo harvests if outcome-vs-intent captures prove scarce.
- **Consult-specs read-path skill** (no distillation) — the zero-cost baseline;
  rejected because nothing durable accumulates and cross-repo synthesis is the
  point; remains the fallback if harvest yield collapses on later repos.

## Appendix A — parked engineering-stratum captures (code-wiki seed)

Verified in the pilot, deliberately not ticked into the research wiki
(boundary: engineering practice, not literature). All from bls-stats; content
immutable at the recorded SHAs.

1. Delta Lake over plain Parquet for the vintage store (decision, ARCH §4.1,
   `1d26d71`)
2. Delta merge/upsert rejected for idempotent re-runs (rejected-approach,
   ARCH §7.2, `1d26d71`)
3. Conditional-PUT probe gates Delta S3 commit safety (decision, plan 1 L269,
   `168da46`)
4. Nullable key columns silently defeat idempotency checks (gotcha, ARCH §7.2,
   `6885a5e`)
5. Idempotency counters must exclude the event's own prior writes (gotcha,
   audit C-13 `198325a` + plan 2 L66 `1ddff48`)
6. Never downgrade a resolved success status on re-poll (gotcha, plan 2 L239,
   `fcc70d0`)
7. Plain HTML is well-formed XML — ParseError tests need an undefined entity
   (gotcha, plan 2 L590, `6c6af27`)
8. Polars streaming collect: `engine='streaming'`, not `streaming=True`
   (gotcha, plan 2 L1299, `b2437d3`)

## Appendix B — pilot yield statistics

5 files (2 completed specs, 2 completed plans, deferred_items.md) → 32 proposed
captures → 32 verified (100% survival) → 28 after 4 spec↔plan merges → 20
ticked + 8 parked; 29 open-question candidates → 2 kept; deferred_items.md
alone: 0 captures, 0 surviving open questions. Ten agents (5 extract + 5
verify), all landing SHAs pickaxe-confirmed as introducing commits.
