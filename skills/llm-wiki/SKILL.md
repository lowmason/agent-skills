---
name: llm-wiki
description: >
  Use when maintaining or setting up the research wiki (Karpathy LLM-wiki
  pattern) at $LLM_WIKI_ROOT: 'ingest', 'add to the wiki', 'what does the wiki
  say', 'wiki lint', 'verify <page>', 'file this into the wiki'; any reference
  to the research wiki, sampler literature notes, or nowcasting literature
  notes; a paper dropped into raw/ to process; and 'set up', 'bootstrap', or
  'install the research wiki' on a new machine or for a second wiki root.
license: MIT
metadata:
  author: Lowell Mason
  version: "1.1"
---

# llm-wiki

Procedure for maintaining the research wiki. The wiki carries its own schema, so
this skill stays generic — a second wiki can reuse it unchanged.

## Resolve the root, then read the schema

1. Root is `$LLM_WIKI_ROOT`, default `~/research-wiki`. All paths below are
   relative to it. Personal and work wikis are separate roots; their content
   never crosses.
2. **Root missing, or no `SCHEMA.md` in it?** The wiki is not installed — do
   not improvise a layout. Confirm the intended root with the human, then run
   this skill's `scripts/bootstrap_wiki.py` with that root as its only
   argument: `python3 ~/.claude/skills/llm-wiki/scripts/bootstrap_wiki.py <root>`.
   The root is required — there is no default, so nothing is written to the
   wrong wiki by accident. It seeds the skeleton and `SCHEMA.md` and installs
   the lint and session-distiller scripts under `<root>/scripts/`; it never
   overwrites existing content (`--check` reports stale tooling, `--force`
   refreshes only the scripts). Then export `LLM_WIKI_ROOT=<root>` and confirm
   with a clean mechanical lint.
3. **Before any operation, read `SCHEMA.md` at the root.** It is the normative
   contract (page formats, quarantine rule, index/log grammar, capture-note
   format). Do not act from memory of it. The skill's bundled
   `scripts/schema-template.md` is only what the bootstrap seeds from; the
   root's copy governs and must never be overwritten by the template.

## Hard rules (never violate)

- **Raw is immutable.** Never modify anything under `raw/`; the human curates it,
  the agent only reads it.
- **Quarantine.** A page's `cites` may list only `type: source` pages with
  `status: verified`. An unverified summary is never grounds for another page.
- **Contradictions are kept, not overwritten.** A new claim conflicting with an
  existing one keeps both (with locators) and appends to `open-questions.md`.
- **Every mutating operation appends one line to `log.md`** using the grammar in
  `SCHEMA.md`: `## [YYYY-MM-DD] <op> | <subject> | <note>`.
- Run `python3 $LLM_WIKI_ROOT/scripts/lint_wiki.py` (mechanical) before any
  status flip and before a semantic pass; it must exit 0.

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
   body is atomic capture notes (see `SCHEMA.md`), not prose. Produce digests
   with `python3 $LLM_WIKI_ROOT/scripts/distill_sessions.py --source claude-code
   ~/.claude/projects $LLM_WIKI_ROOT/raw/sessions` — `--source` (Claude Code
   session history), SRC (`~/.claude/projects`), and OUT_DIR (the root's
   `raw/sessions`) are all required, so digests can only land in the wiki you
   name (`--help` for the optional `--project` / `--since` filters).

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
1. **Mechanical:** run `python3 $LLM_WIKI_ROOT/scripts/lint_wiki.py` (add
   `--strict` to fail on warnings). Fix errors before proceeding.
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
form is simplified from `kfchou/wiki-skills`. This skill's prose and its bundled
scripts are original work.
