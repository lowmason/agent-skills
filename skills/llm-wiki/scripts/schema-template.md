<!-- schema-version: 1 (bump on a breaking contract change; `bootstrap_wiki.py --check` flags a root whose schema is behind the bundle) -->
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
   residual secret-shaped string under `raw/sessions/` is a lint error.

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
