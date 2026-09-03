<!-- schema-version: 3 (bump on a breaking contract change; `bootstrap_wiki.py --check` flags a root whose schema is behind the bundle) -->
# SCHEMA — research-wiki normative formats

This file is the machine-readable contract. `scripts/lint_wiki.py` enforces the
mechanical parts; the `llm-wiki` skill reads this file before any operation.
Transcribed from the llm-wiki spec §6–§9, §16.3, §16.5.

## Page format

Three page types. Frontmatter is the machine-readable contract.

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

Frontmatter is flat: scalar values and single-line bracketed lists only. Inline
`#` annotations shown above are illustrative — do **not** write them into real
pages. Required keys on every page: `title`, `type`, `status`, `topics`,
`updated`. Enums: `type ∈ {source, concept, synthesis}`;
`status ∈ {unverified, verified}`.

Per-type keys:

- `type: source` — carries `raw:` (e.g. `raw: raw/samplers/robnik-2022-mclmc.pdf`)
  instead of `cites`. The page filename stem matches the raw file stem. A source
  page is the agent's summary of one raw source; it is not trusted by
  construction and starts `unverified`.
- `type: concept` — an entity page (a sampler, a method, an estimator). Carries
  `cites`, not `raw`.
- `type: synthesis` — a comparison, decision, or filed-back answer spanning
  sources. Carries `cites`, not `raw`.

### Quarantine rule (load-bearing)

`cites` may only list pages of `type: source` with `status: verified`. Anything
else is a lint error. Consequence: an unverified summary — including any freshly
filed-back answer — cannot become grounds for anything else until checked. This
is the circular-self-citation guard.

### Body conventions

Prose-first; relative links only; no H1 (title lives in frontmatter). Every
quantitative or attributable claim carries an inline locator in square brackets
referencing a source-page slug plus a position: `[robnik-2022-mclmc §4.2]`,
`[hoffman-2014-nuts Table 2]`. Contradictory claims are recorded adjacently with
both locators and a one-line note, then logged to `open-questions.md`. Session
digest source pages structure their body as capture notes (below), not prose.

A position opens with `§`, `p.`, `Table`, `Fig`, `Eq`, or a digit — `Table`
also covers `Tables`, and `Fig` covers `Figure`/`Figs`, while a page range is
written `p. 3-4` (not `pp.`). A bracketed token whose remainder does not open
that way is prose, not a citation, and is never checked as one: `[see below]`,
`[Figure 2]` and `[NUTS §3]` are ordinary text. A citation is recognized only
when the position matches *and* the token either is multi-part (carries a
hyphen or a four-digit year) or exactly names an existing source-page slug.
Extend the position list additively, against real content.

## index

`wiki/index.md`: one line per page, grouped by topic heading:

```
## samplers
- [mclmc](samplers/mclmc.md) — microcanonical dynamics; tuning-free ESS claims · 3 sources · verified · 2026-07-22
```

Parity holds in both directions: every page on disk has exactly one index line;
every index line resolves to a page.

## log

`wiki/log.md`: append-only, one line per operation, grep-parseable:

```
## [2026-07-22] ingest | robnik-2022-mclmc | 1 source page, 2 concept pages touched
## [2026-07-22] lint-mechanical | clean
```

Grammar: `## [YYYY-MM-DD] <op> | <subject> | <note>`, with
`op ∈ {ingest, file-back, verify, lint-mechanical, lint-semantic, schema}`.
Every mutating operation appends a line. Plain queries are logged only when they
file back or expose a coverage gap.

## contradictions

A new claim conflicting with an existing one is never overwritten — both are
kept with locators, and an entry is appended to `open-questions.md`.

## Operations (dispatched by the skill; see the skill for procedure)

- **ingest** — one source, supervised: read source, propose 3–5 takeaways +
  source-page draft + concept touch-list; on approval write source page
  (`unverified`), edit concept pages (each new claim carries a locator), update
  `index.md`, append to `log.md`. New concept page only for an entity linked
  from ≥2 pages; ceiling one new concept page per ingest without approval.
- **query** — index-first: read `index.md`, select ≤5 pages, answer with page
  references and locators; open raw only if pages are insufficient (a coverage
  gap). File-back only when synthesizing ≥2 sources or recording a decision;
  filed pages are `type: synthesis`, `status: unverified`.
- **lint** — mechanical (`scripts/lint_wiki.py`) then semantic (agent pass).
- **verify** — walk every locator-carrying claim, open the cited source page's
  raw file at the locator, confirm or flag; all confirmed → `status: verified`.

## Epistemic rules for session digests (spec §16.3)

1. **Echo rule.** The assistant's proposals are not the user's decisions. A
   capture of `kind: decision` requires `basis: user-turn` (the user states or
   confirms it, with a turn locator) or `basis: git:<sha>` (the decision landed
   in code). An unadopted assistant proposal is captured, if at all, as
   `kind: rejected-approach`. No `decision` captures from compaction-summary
   text — decisions require verbatim turns.
2. **Staleness.** Every capture carries the session date from its digest header;
   claims about code are dated claims, suspect once the referenced files change.
3. **Secrets.** Redaction happens at distillation and is not optional; any
   residual secret-shaped string under `raw/sessions/` or `raw/specs/` is a
   lint error.

## Capture-note format for session-digest source pages (spec §16.5)

A session-digest source page's body is atomic capture notes, not prose:

```
### [d-03] Blackjax stays the sampler layer; NumPyro the model layer
kind: decision · turns: 18–24 · basis: user-turn
One- to three-sentence self-contained statement of the capture.
```

Kinds and id prefixes: `decision` (d), `rejected-approach` (r), `gotcha` (g),
`resolved-confusion` (c), `validated-pattern` (p). The metadata line is
regex-checkable; lint enforces the echo rule on `decision` captures mechanically.

## Specs-harvest briefs and digests (specs-harvest framework)

`raw/specs/` holds specs-harvest digests: ground truth distilled from a
repo's `specs/` corpus (specs, completed specs, completed plans, deferred
items). Digest filename: `<date>-<repo>-specs-<id8>.md`, where `id8` is the
first 8 hex chars of SHA-256 over the ordered ticked-capture content — an
unchanged brief re-assembles to the identical file. Digest entries are
`[<id>]`-keyed ground truth: `at: <path> <position> · sha: <introducing
commit>` plus a verbatim excerpt; `[q-NN]` open questions carry `at:` and
prose only and are appended to `open-questions.md` at ingest.

Specs-harvest source pages use the `at:` capture-metadata variant — the
session-digest `turns:` locator is replaced by a repo locator and the basis
is always a commit:

```
### [d-01] Flat files primary; BLS API v2 demoted to utility
kind: decision · at: bls-stats specs/completed/bls-stats-architecture.md §6.1 · basis: git:1d26d71
One- to three-sentence self-contained claim (no square brackets).
```

Briefs (`reports/harvest-<repo>-<date>.md`) are working files, not wiki
content: `distill_specs.py inventory` writes the skeleton, agents extract
and adversarially verify capture entries, the human ticks. A capture entry
is a checkbox line plus 2-space-indented fields; 4-space-indented lines
continue the previous field, and `(also <path> <pos> · sha: <sha>)` lines
add secondary locations:

```
- [x] [d-01] Flat files primary; BLS API v2 demoted to utility
  kind: decision · boundary: transferable
  at: specs/completed/bls-stats-architecture.md §6.1 · sha: 1d26d71
  excerpt: "The BLS API v2 cannot carry full-universe daily increments"
  claim: One- to three-sentence self-contained claim (no square brackets).
```

`[q-NN]` open-question entries carry only `at:` and `claim:`. Boundary
verdicts: `transferable | mixed | code-coupled`; a code-coupled entry is
never ticked. `[x]` = approved for assembly; unticked entries persist as
the durable declined record — later inventories dedup against all prior
entries, approved and declined, keyed on locator + claim hash. The echo
rule holds: every capture's basis is its introducing commit (`sha:` on the
`at:` line); a `[d-NN]` digest entry without one is a lint error, as is any
secret-shaped string under `raw/specs/`.
