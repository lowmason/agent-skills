# llm-wiki — implementation spec

**Status: COMPLETE (2026-07-23)** — both implementing plans shipped: M0 scaffold, `SCHEMA.md`,
`lint_wiki.py`, and the `llm-wiki` skill (`specs/plans/completed/13-llm-wiki.md`), and the
session-history distiller (`specs/plans/completed/14-llm-wiki-distiller.md`). §13 M1–M3 and
§16.7 S1–S3 are content milestones reached through normal wiki use, not code, and remain
open-ended by design. Deferred items in specs/deferred_items.md.
**Date:** 2026-07-22 · rev b (adds §16, session-history backfill; §10 lint table +2 rows; §5 layout +`raw/sessions/`)
**Pattern source:** Karpathy, *LLM Wiki* idea file (gist `karpathy/442a6bf555914893e9891c11519de94f`, 2026-04-04)
**Adopted extensions:** verification quarantine (per the auditor's comment on the gist); per-claim citation audit, sequential form (simplified from `kfchou/wiki-skills`)

---

## 1. Problem statement

Reference knowledge about the sampler and nowcasting literature is currently re-derived on demand: each session re-opens papers, re-establishes what MCLMC/MAMS/NUTS papers claim, and re-discovers where those claims conflict. The `state-space.md` reference is static and rots between manual rewrites. With the pre-registered MCLMC/MAMS-vs-NUTS benchmark about to produce results, there is no place where prior claims and new results accumulate against each other.

This spec instantiates a minimal Karpathy-pattern wiki: immutable raw sources, an agent-maintained markdown wiki, and a schema layer — plus a thin `llm-wiki` skill in the `agent-skills` library that carries the procedures.

## 2. Goals

1. **Compile once, query forever.** A literature question answerable from the wiki is answered from `wiki/` pages with source locators, without re-opening raw papers.
2. **Contradictions are first-class.** Conflicting cross-source claims are recorded side by side with locators and surfaced in `open-questions.md`, never silently overwritten.
3. **Trust is explicit.** No page is cited as grounds for another page until its claims have been checked against raw sources (verification quarantine).
4. **File-back compounds.** Benchmark results and genuine syntheses enter the wiki with provenance; trivial lookups never do.
5. **Drift is enforced, not aspirational.** Mechanical lint is deterministic and cheap; semantic lint has a hard cadence trigger built into the ingest procedure.

Success check at 30 days post-M1: at least three literature questions answered wiki-first that previously required re-opening papers; zero mechanical lint errors at each semantic pass.

## 3. Non-goals

- **Embedding/vector search, qmd.** Index-first navigation holds at target scale (~100 sources). Revisit only at the soft ceiling (§11).
- **MCP server, web UI, Obsidian plugins.** Agent access + plain markdown suffice; Obsidian-*compatible* is free, Obsidian-*dependent* is not.
- **Background workers, session hooks, auto-capture.** Supervised single-source ingest is the point; daemons reintroduce unreviewed writes.
- **Graph DB / typed-edge store.** The `cites` frontmatter key provides the one dependency edge lint needs; git history covers the rest.
- **Team features.** Personal wiki, single writer.
- **Project internals.** `alt-nfp` design decisions, code-review findings, and repo conventions stay in project CLAUDE.md files and ADRs. Boundary rule: **if it changes when the code changes, it is project docs; if it changes when the literature changes, it is wiki.**

## 4. Architecture

Two repositories, three layers:

| Layer | Location | Owner |
|---|---|---|
| Raw sources (immutable) | `research-wiki/raw/` | Human curates; agent reads only |
| Wiki (compiled knowledge) | `research-wiki/wiki/` | Agent writes; human reads and approves |
| Schema | `research-wiki/SCHEMA.md` + `agent-skills/…/llm-wiki/SKILL.md` | Co-evolved, human-gated |

The **skill is procedure, the wiki is data**. Everything wiki-specific (formats, naming, lint checks) lives in `SCHEMA.md` and travels with the wiki; `SKILL.md` stays generic so a second wiki (e.g. labor-measurement policy, if split out later) can reuse it unchanged. The skill resolves the wiki root via `LLM_WIKI_ROOT`, defaulting to `~/research-wiki`.

## 5. Repository layout

```
research-wiki/                  # its own git repo
  SCHEMA.md                     # normative formats (transcribed from §6–§9 of this spec)
  raw/                          # immutable; agent never modifies, only human adds
    samplers/                   #   <firstauthor>-<year>-<slug>.<ext>
    nowcasting/
    benchmarks/                 #   Lowell's own reports enter here (pre-reg spec, results)
    sessions/                   #   distilled session digests (§16); raw JSONL never enters the repo
    assets/                     #   images referenced by raw markdown
  wiki/
    index.md                    # catalog: one line per page, grouped by topic
    log.md                      # append-only operation log
    open-questions.md           # contradictions and gaps awaiting resolution
    sources/                    # one summary page per raw source
    samplers/                   # concept and synthesis pages
    nowcasting/
  reports/                      # dated lint and verify reports (outside wiki/, not indexed)
  scripts/
    lint_wiki.py                # stdlib-only mechanical checks (§10)
    distill_sessions.py         # session history → digests (§16.4)
```

## 6. Page format

Three page types. Frontmatter is the machine-readable contract; lint enforces it.

```yaml
---
title: Microcanonical Langevin Monte Carlo
type: concept            # source | concept | synthesis
status: unverified       # unverified | verified
topics: [samplers]
cites: [sources/robnik-2022-mclmc]   # concept/synthesis only
updated: 2026-07-22
---
```

Per-type keys:

- `type: source` — carries `raw: raw/samplers/robnik-2022-mclmc.pdf` instead of `cites`. Filename stem matches the raw file stem. A source page is the agent's summary of one raw source; it is *not* trusted by construction and starts `unverified`.
- `type: concept` — an entity page (a sampler, a method, an estimator). Carries `cites`.
- `type: synthesis` — a comparison, decision, or filed-back answer spanning sources. Carries `cites`.

**Quarantine rule (load-bearing):** `cites` may only list pages of `type: source` with `status: verified`. Lint errors otherwise. Consequence: an unverified summary — including any freshly filed-back answer — cannot become grounds for anything else until checked. This is the circular-self-citation guard, and it maps onto the existing programmatically-verified-citations discipline in `recommend-probabilistic-model`.

**Body conventions:** prose-first; relative links only; no H1 (title lives in frontmatter). Every quantitative or attributable claim carries an inline locator in square brackets referencing a source-page slug plus a position: `[robnik-2022-mclmc §4.2]`, `[hoffman-2014-nuts Table 2]`. Contradictory claims are recorded adjacently with both locators and a one-line note, then logged to `open-questions.md`. Source pages for session digests structure their body as capture notes rather than free prose (§16.5).

## 7. index.md

One line per page, grouped by topic heading. Format:

```
## samplers
- [mclmc](samplers/mclmc.md) — microcanonical dynamics; tuning-free ESS claims · 3 sources · verified · 2026-07-22
```

Lint enforces parity in both directions: every page on disk has exactly one index line; every index line resolves to a page.

## 8. log.md

Append-only, one line per operation, grep-parseable prefix:

```
## [2026-07-22] ingest | robnik-2022-mclmc | 1 source page, 2 concept pages touched
## [2026-07-22] lint-mechanical | clean
## [2026-07-25] file-back | mclmc-vs-nuts-efficiency-claims | synthesis, 3 cites
```

Grammar: `## [YYYY-MM-DD] <op> | <subject> | <note>`, with `op ∈ {ingest, file-back, verify, lint-mechanical, lint-semantic, schema}`. Every mutating operation appends a line. Plain queries are logged only when they file back or expose a coverage gap.

## 9. Operations

Four operations, dispatched by the skill. All read `SCHEMA.md` first.

### 9.1 ingest — one source, supervised

1. Human drops the file into `raw/<topic>/` under the naming convention and invokes `ingest raw/samplers/robnik-2022-mclmc.pdf`.
2. Agent reads the source and proposes: three to five key takeaways, the source-page draft, and a touch list of existing concept pages to update.
3. **New-page heuristic:** create a new concept page only for an entity that would be linked from at least two other pages; default ceiling of one new concept page per ingest without explicit approval.
4. On approval: write the source page (`status: unverified`), apply concept-page edits (each new claim carries a locator), update `index.md`, append to `log.md`.
5. **Write-time contradiction handling:** a new claim conflicting with an existing one is never overwritten — both are kept with locators, and an entry is appended to `open-questions.md`.
6. **Cadence trigger:** at the end of every ingest, the agent greps `log.md`; if five ingests have occurred since the last `lint-semantic` entry, or that entry is older than 30 days, it says so and offers to run one now. This is the procedural substitute for a scheduler.

Session digests follow this same flow with the capture-note variant of §16.5.

### 9.2 query — index-first

1. Read `wiki/index.md`; select at most five pages; read them; answer with page references and locators.
2. Open raw sources only if wiki pages are insufficient — and say so explicitly, since that is a coverage gap worth an `open-questions.md` entry.
3. **File-back rule:** offer to file the answer only when it synthesizes claims across two or more sources or records a decision. Simple lookups are never filed. Filed pages are `type: synthesis`, `status: unverified`. If a needed source page is itself unverified, verification becomes the visible prerequisite — the quarantine surfacing naturally.

### 9.3 lint — mechanical, then semantic

**Mechanical** is `scripts/lint_wiki.py` (§10) — deterministic, runnable any time, and a required precondition for the semantic pass and for any status flip.

**Semantic** (`wiki lint`) is an agent pass over the whole wiki: contradictions between pages not yet in `open-questions.md`; claims plausibly superseded by newer ingests; concepts mentioned three or more times without their own page; gaps worth a targeted web search. Output goes to `reports/lint-YYYY-MM-DD.md`, new items to `open-questions.md`, one line to `log.md`.

### 9.4 verify — the status flip

`verify samplers/mclmc.md`: walk every locator-carrying claim on the page; open the cited source page's raw file at the locator; confirm or flag. All confirmed → flip to `status: verified`, log it. Anything flagged → status unchanged, flags written to `reports/`. Sequential in v1; a parallel per-source subagent audit (the interesting part of `kfchou/wiki-skills`) is deferred (P2).

## 10. `scripts/lint_wiki.py` contract

Stdlib only (`pathlib`, `re`, `argparse`, `sys`). Python ≥ 3.12. Single quotes, two-space indentation.

```
usage: python scripts/lint_wiki.py [--strict] [ROOT]
exit:  0 clean · 1 errors (with --strict, warnings also exit 1)
out:   one line per finding: 'ERROR|WARN|INFO  <path>  <message>', then a summary line
```

| Check | Severity |
|---|---|
| Broken relative links between wiki pages | error |
| Index/page parity violation, either direction | error |
| Frontmatter schema violation (missing keys, bad enums, wrong per-type key) | error |
| `cites` target not `type: source` | error |
| `cites` target not `status: verified` | error |
| Body citation slug with no matching source page | error |
| Orphan page (no inbound links, index excluded) | warning |
| Newest `updated` frontmatter date newer than last `log.md` entry | warning |
| Secret-shaped string anywhere under `raw/sessions/` (§16.3) | error |
| `kind: decision` capture without `basis: user-turn` or `basis: git:<sha>` (§16.5) | error |
| Raw file with no source page (ingest backlog) | info |
| Page count > 120 or source count > 100 (soft ceiling — revisit qmd) | info |

## 11. Scale policy

Index-first navigation is the retrieval system until a soft ceiling of roughly 120 wiki pages or 100 sources, at which point the info-level lint fires and the qmd/hybrid-search question is revisited as a deliberate decision, not an incremental drift. Until then, retrieval is: index, then pages, with `grep -r` over `wiki/` as fallback.

## 12. Skill integration

Location: `agent-skills/skills/llm-wiki/SKILL.md`, symlinked **tier-2** — loaded on trigger, never in the always-on core set.

Draft frontmatter (description deliberately pushy, per skill-creator guidance):

```yaml
---
name: llm-wiki
description: Maintain the personal research wiki (Karpathy LLM-wiki pattern)
  at $LLM_WIKI_ROOT. Use whenever the user says 'ingest', 'add to the wiki',
  'what does the wiki say', 'wiki lint', 'verify <page>', or 'file this into
  the wiki'; whenever they reference the research wiki, sampler literature
  notes, or nowcasting literature notes; and whenever they drop a paper into
  raw/ and ask to process it.
---
```

Body budget ≤ 150 lines: resolve root (`LLM_WIKI_ROOT`, default `~/research-wiki`); **read `SCHEMA.md` before any operation**; dispatch the four operations of §9; restate the hard rules (raw is immutable; quarantine; contradiction handling; every mutating op logs). No bundled resources — the wiki carries its own schema, which is what keeps the skill reusable for a second wiki.

## 13. Milestones and acceptance

**M0 — scaffold (half day).** Repo initialized; `SCHEMA.md` transcribed from §6–§9; `lint_wiki.py` implemented; skill written and symlinked.
- [ ] `python scripts/lint_wiki.py` exits 0 on the empty scaffold
- [ ] Saying 'ingest <path>' triggers the skill, which reads `SCHEMA.md` before acting

**M1 — seed (one to two sessions).** Ingest the pre-registered benchmark spec plus six to ten sampler/nowcasting papers (MCLMC, MAMS, NUTS baselines, core state-space references). Ingest `state-space.md` itself as a raw source and decompose it into concept pages that cite it. Verify the three most load-bearing source pages.
- [ ] ≥ 8 source pages, ≥ 6 concept pages, index parity clean
- [ ] ≥ 3 source pages `verified`

**M2 — first real use.** One semantic lint pass; one query acceptance test.
- [ ] The query 'what efficiency claims exist for MCLMC vs NUTS on hierarchical models, and where do they conflict' is answered from wiki pages with locators, without opening raw sources
- [ ] `open-questions.md` contains at least one genuine cross-source contradiction

**M3 — file-back (post-benchmark).** Benchmark results report ingested into `raw/benchmarks/`; a synthesis page compares pre-registered predictions against observed results; that page reaches `verified`.
- [ ] The synthesis page's `cites` includes both the pre-registered spec's source page and the results report's source page, both verified

**P2 / deferred:** parallel subagent verify; qmd at the soft ceiling; a second wiki root for labor-measurement policy; the code-wiki root (raw layer = SHA-pinned extracts and PR units, `path@sha` locators, deterministic stale-locator lint, checkpoint-SHA incremental ingest).

The session-backfill track (S0–S3) runs in parallel and is specified in §16.7. **S0 is time-sensitive and independent of M0 — do it first.**

## 14. Coding and prose conventions

Python: stdlib only, single quotes, two-space indentation, `pathlib` over `os.path`. Wiki prose: declarative, claim-per-sentence where locators attach, no rhetorical hedging — the `status` field is the hedge. Dates ISO-8601 everywhere.

## 15. Open questions

1. **Verification depth for source pages** — spot-check headline claims vs paragraph-level check of every quantitative claim. Affects M1 pace only; suggest paragraph-level for benchmark-adjacent sources, spot-check elsewhere. (Owner: Lowell; non-blocking.)
2. **labor-measurement topic** — third topic in this repo after M2, or a second wiki root reusing the skill. The skill design keeps both open. (Non-blocking.)
3. **Superseded claims** — annotate in place with a dated note vs relocate to a superseded section. Suggest annotate in place; git holds history. Decide at first occurrence. (Non-blocking.)
4. **Whether `raw/benchmarks/` should also receive alt-nfp evaluation artifacts** — leans no under the §3 boundary rule (they change when the code changes), but the pre-registered benchmark sits exactly on the line. (Decide at M3.)

## 16. Appendix — session-history backfill

Backfills stream (b): the question-driven knowledge the wiki would have accumulated had it existed from the first session. The corpus is agent conversation history, not git. The appendix is root-agnostic — captures route to this root or the (P2) code-wiki root by the §3 boundary rule; code-bound material waits in the S0 archive until that root exists, losing nothing.

### 16.1 Retention protection — before anything else

Claude Code stores transcripts as plaintext JSONL under `~/.claude/projects/`, one file per session, and at startup silently hard-deletes anything older than the retention window — 30 days by last activity, by default, with no recovery path (reference: `https://code.claude.com/docs/en/data-usage`). Three actions, today:

1. Set `{"cleanupPeriodDays": 3650}` in `~/.claude/settings.json`. **Never 0** — a known bug makes 0 disable transcript persistence entirely rather than disable cleanup.
2. Snapshot: `tar -czf ~/archives/claude-projects-$(date +%F).tar.gz -C ~ .claude/projects`. The dated tarball, kept outside the wiki repo, is the archive of record for raw JSONL; only digests (§16.4) enter the repo.
3. Request the claude.ai data export (Settings → Privacy → Export data); it arrives as `conversations.json`.

### 16.2 Corpus and priority

Three corpora, ingested in descending signal density:

1. **Artifact trail** — review documents, spec series, kickoff briefs. Distilled at the time of writing, fully intact, highest density. Methods-side artifacts ingest into this root as ordinary raw sources; code-side artifacts stay archived until the code-wiki root exists.
2. **claude.ai export** — retained server-side, therefore complete. Distill via the `claude-ai` adapter.
3. **Surviving Claude Code JSONL** — already thinned to roughly the retention window per session. Distill via the `claude-code` adapter, filtered with `--project`.

### 16.3 Epistemic rules — transcribe into SCHEMA.md

Transcripts differ from papers in three ways; each difference gets a rule.

1. **Echo rule.** The assistant's proposals are not the user's decisions. A capture of `kind: decision` requires `basis: user-turn` (the user states or confirms it, with turn locator) or `basis: git:<sha>` (the decision demonstrably landed in code). An unadopted assistant proposal is captured, if at all, as `kind: rejected-approach`. Corollary: no `decision` captures from compaction-summary text — decisions require verbatim turns.
2. **Staleness.** Every capture carries the session date from its digest header. Claims about code are suspect once the referenced files change post-session; in the code-wiki root this becomes the deterministic stale-locator check, here it is simply a dated claim.
3. **Secrets.** Transcripts contain pasted keys, tokens, and credentials — the stated rationale for the short default retention. Redaction happens in stage 1, is not optional, and any residual secret-shaped string under `raw/sessions/` is a lint error (§10).

### 16.4 `scripts/distill_sessions.py` contract

Stage 1 — deterministic, stdlib only (`json`, `pathlib`, `re`, `argparse`, `sys`). Single quotes, two-space indentation.

```
usage: python scripts/distill_sessions.py --source {claude-code,claude-ai}
         [--project SUBSTR] [--since YYYY-MM-DD] [--include-sidechains]
         SRC OUT_DIR
exit:  0 ok · 1 one or more files failed to parse (listed on stderr; good files still written)
```

Behavior:

- **Thread reconstruction** — records link by parent pointer; follow the main chain; drop subagent sidechains unless `--include-sidechains`. Introspect one file before hardcoding field names; the format is an implementation detail of Claude Code, not a stable API.
- **Noise removal** — tool-use and tool-result blocks are elided to one-line traces (`[tools: bash ×14, str_replace ×3]`) so narrative context survives; file dumps never pass through.
- **Compaction summaries** — retained, marked `[compaction summary]`; lossy, but all that remains of pre-compaction turns.
- **Redaction — always on** — key-shaped tokens (`sk-…`, `ghp_…`, `AKIA…`), PEM blocks, `password|token|secret` assignments, and long high-entropy strings become `[REDACTED:<class>]`; per-file counts land in the digest header.
- **Idempotence** — the output filename embeds the session id; existing digests are skipped unless the session has grown, in which case the digest is rewritten (the newly computed turn count is compared against the existing digest's `turns:` header), so the distiller can be re-run at will.

Digest format — one file per session, `raw/sessions/YYYY-MM-DD-<slug>-<sess8>.md`:

```yaml
---
session: a3f2c9d1
source: claude-code          # claude-code | claude-ai
project: alt-nfp             # claude-code only, from the project dir
dates: 2026-05-14/2026-05-15
turns: 62
redactions: 2
---
```

Body: numbered turns — `**[07] user:** …`, `**[08] assistant:** …` — with tool elisions inline. Turn numbers are the locator currency for captures.

### 16.5 Ingesting a digest: capture notes

A session digest goes through §9.1 with one variant: the source page's body is a set of atomic capture notes rather than free prose. Each capture:

```
### [d-03] Blackjax stays the sampler layer; NumPyro the model layer
kind: decision · turns: 18–24 · basis: user-turn
One- to three-sentence self-contained statement of the capture.
```

Kinds and id prefixes: `decision` (d), `rejected-approach` (r), `gotcha` (g), `resolved-confusion` (c), `validated-pattern` (p). The metadata line is regex-checkable, which is what lets lint enforce the echo rule on `decision` captures mechanically. Concept and synthesis pages then cite the session source page like any other — quarantine included: verifying a session source page means confirming each capture against its cited turns, and for `basis: git:<sha>`, against the commit.

Yield expectations: low single digits per ordinary session; a dense review session may produce ten or more; **zero is a legitimate outcome** — not every session contains durable knowledge, and the digest still stands as searchable raw.

### 16.6 Cadence

Backfill is one-shot per corpus. Prospectively, re-run the distiller (idempotent) before each semantic lint and triage new digests then — session capture stays inside the §9.1(6) cadence with no daemons, consistent with the §3 non-goal.

### 16.7 Backfill milestones — M-S track, parallel to §13

**S0 — retention fix (today, ten minutes; independent of M0).**
- [ ] `cleanupPeriodDays: 3650` set — and confirmed not 0
- [ ] Dated tarball of `~/.claude/projects/` exists outside the wiki repo
- [ ] claude.ai export requested

**S1 — artifact ingest (alongside M1).** Methods-side artifacts (PPL landscape analysis; the benchmarking pre-registration is already in M1) enter as ordinary raw sources.
- [ ] ≥ 3 artifact source pages beyond the M1 paper set

**S2 — claude.ai distill.**
- [ ] Digests generated; zero secret-pattern lint errors under `raw/sessions/`
- [ ] ≥ 3 session source pages, ≥ 10 captures total, every `decision` passing the echo check

**S3 — Claude Code JSONL distill.** Surviving sessions, `--project`-filtered to methods-relevant work; code-bound digests remain in the S0 tarball until the code-wiki root exists.
- [ ] Remaining relevant sessions digested; uningested digests surfaced by the info-level backlog check
