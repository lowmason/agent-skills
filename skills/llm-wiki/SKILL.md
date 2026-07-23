---
name: llm-wiki
description: >
  Maintain the personal research wiki (Karpathy LLM-wiki pattern) at
  $LLM_WIKI_ROOT. Use whenever the user says 'ingest', 'add to the wiki',
  'what does the wiki say', 'wiki lint', 'verify <page>', or 'file this into
  the wiki'; whenever they reference the research wiki, sampler literature
  notes, or nowcasting literature notes; and whenever they drop a paper into
  raw/ and ask to process it.
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
---

# llm-wiki

Procedure for maintaining the research wiki. The wiki carries its own schema, so
this skill stays generic — a second wiki can reuse it unchanged.

## Resolve the root, then read the schema

1. Root is `$LLM_WIKI_ROOT`, default `~/research-wiki`. All paths below are
   relative to it.
2. **Before any operation, read `SCHEMA.md` at the root.** It is the normative
   contract (page formats, quarantine rule, index/log grammar, capture-note
   format). Do not act from memory of it.

## Hard rules (never violate)

- **Raw is immutable.** Never modify anything under `raw/`; the human curates it,
  the agent only reads it.
- **Quarantine.** A page's `cites` may list only `type: source` pages with
  `status: verified`. An unverified summary is never grounds for another page.
- **Contradictions are kept, not overwritten.** A new claim conflicting with an
  existing one keeps both (with locators) and appends to `open-questions.md`.
- **Every mutating operation appends one line to `log.md`** using the grammar in
  `SCHEMA.md`: `## [YYYY-MM-DD] <op> | <subject> | <note>`.
- Run `$LLM_WIKI_ROOT/scripts/lint_wiki.py` (mechanical) before any status flip
  and before a semantic pass; it must exit 0.

## Operations

### ingest `<raw/path>`
1. Read the source. Propose 3–5 key takeaways, a source-page draft
   (`type: source`, `status: unverified`, `raw:` = the file), and a touch-list
   of existing concept pages to update.
2. New concept page only for an entity linked from ≥2 pages; ceiling one new
   concept page per ingest without explicit approval.
3. On approval: write the source page; apply concept edits (each new claim
   carries an inline locator `[slug §x]`); update `index.md`; append to `log.md`.
4. Write-time contradiction → keep both claims, append to `open-questions.md`.
5. **Cadence:** grep `log.md`; if ≥5 ingests since the last `lint-semantic`
   entry, or that entry is >30 days old, say so and offer to run one now.
6. A session digest (`raw/sessions/…`) ingests the same way, but its source-page
   body is atomic capture notes (see `SCHEMA.md`), not prose.

### query `<question>`
1. Read `index.md`; select ≤5 pages; read them; answer with page references and
   inline locators.
2. Open raw sources only if the pages are insufficient — say so explicitly; that
   is a coverage gap worth an `open-questions.md` entry.
3. **File-back only** when the answer synthesizes ≥2 sources or records a
   decision; simple lookups are never filed. Filed pages are `type: synthesis`,
   `status: unverified`. If a needed source page is unverified, verification is
   the visible prerequisite.

### lint
1. **Mechanical:** run `$LLM_WIKI_ROOT/scripts/lint_wiki.py` (add `--strict` to
   fail on warnings). Fix errors before proceeding.
2. **Semantic:** an agent pass over the whole wiki — contradictions not yet in
   `open-questions.md`; claims plausibly superseded by newer ingests; concepts
   mentioned ≥3 times without their own page; gaps worth a web search. Write
   `reports/lint-YYYY-MM-DD.md`, add new items to `open-questions.md`, append one
   line to `log.md`.

### verify `<wiki/page.md>`
1. Mechanical lint must be clean first.
2. Walk every locator-carrying claim; open the cited source page's raw file at
   the locator; confirm or flag. For a session-digest source page, confirm each
   capture against its cited turns (and, for `basis: git:<sha>`, the commit).
3. All confirmed → flip to `status: verified`, append to `log.md`. Anything
   flagged → status unchanged; write flags to `reports/`.

## Attribution

Pattern from Andrej Karpathy's LLM-wiki idea file; the per-claim citation-audit
form is simplified from `kfchou/wiki-skills`. This skill is original prose.
