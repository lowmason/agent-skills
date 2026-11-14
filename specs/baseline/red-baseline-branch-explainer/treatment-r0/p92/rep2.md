# claude/compassionate-jennings-98ff45: plan 92, writing-skills against the Claude Code guide

## Synopsis

**The plan:** Plan 92 brought writing-skills in line with the repository's Claude Code guide. It
closed three backlog items. The last STALE file of the drift sweep was `skills/writing-skills/SKILL.md`.
Register gap `writing-skills-guide-gaps` still held it. Decision 10 of the conformance spec had put
off a distilled file of Claude Code text until the split. writing-skills is the meta-skill, so a
wrong Claude Code fact in it spreads to every skill an agent writes.

**The build:** A pre-registered micro-test ran first on the old text: a RED control for "critical
rules first" and a descriptive arm of a pointer test. RED came back null, so no new instruction was
added. Then a new file, `references/claude-code.md`, took the Claude Code facts. `discovery.md` and
`SKILL.md` kept portable advice and gained pointers. The new-layout arms met every bar. A review of
56 rows against eight guide sections followed, then the restamp at `@2.1.306`. The register,
`NOTICE` and the backlog were updated to match.

**The project:** writing-skills now has one home for Claude Code facts, each backed by a guide
section. `cli.py lint` prints no `STALE` line. Three wrong or unsupported claims are corrected. The
register loses one gap and gains a sharper reason for the TDD deviation. The branch adds five
backlog items.

## Background

writing-skills cited the guide at `@2.1.219` (`skills/writing-skills/SKILL.md:14`). The drift sweep
of plan 43 had stamped 41 files stale, and this was the last one. Plan 72 had split the skill to a
434-line body and moved most of its Claude Code text into `references/discovery.md`. There it sat
mixed with lint rules and advice that holds on every runtime.

Two register entries in `build/cc_guide/conformance.toml` waited on a rewrite:

- Gap `writing-skills-guide-gaps` covered the listing budget (audit row S-58), critical rules first
  (S-67) and `@` loading (S-107).
- Deviation `writing-skills-tdd-for-docs` named the rewrite as its revisit trigger.

The spec's Claims table listed what was wrong or unsupported. `discovery.md` said a description is
"resident in EVERY conversation". It said `@` syntax "force-loads files immediately, consuming 200k+
context", which no source supports. The fork advice rested on a premise that is gone: that subagents
cannot start subagents. The directory examples showed no `references/` folder.

The owner's decisions in the spec frame the work. D1 picks distilling over fixing in place. D2 keeps
the Iron Law and refreshes the TDD deviation. D4 waives reps for factual corrections. D5 reviews
against the guide as it is on main, with no `/cc-guide` pass.

## The change

### 1. Micro-test kit and registered rules

The kit sits in `specs/baseline/red-baseline-writing-skills-guide/kit/`. `cases.py` holds four frozen
conversations: `R1` (a long skill with one hard rule), `P1` (a key that only Claude Code reads), `P2`
(a skill that stopped triggering) and `P3` (forking a skill that dispatches subagents).
`build_prompts.py` inlines the SKILL.md body and the reference files for each layout. `run_reps.sh`
runs isolated `claude -p` reps from empty `/tmp` folders. `show_reps.py` is a reading aid, not a
judge. The rules, bars and the RED null outcome were committed at `d1aaba9` before any rep ran. They
head `specs/baseline/red-baseline-writing-skills-guide.md`. Everything later depends on this
pre-registration.

### 2. RED control and descriptive arm on the old layout

All 25 base reps ran at `3684b96`. `R1` passed 5 of 5 on both models: every rep stated the hard rule
before the table line. So RED showed no failure. By the registered null outcome, no template
instruction was added, `claude-code.md` states the compaction mechanism only, and S-67's part of the
gap closes on this record.

The descriptive arm ran on Opus only. `P1a` and `P2a` passed 5 of 5, and `P3a` passed 0 of 5. Every
`P3a` rep gave the old wrong reason: a forked skill cannot dispatch. The `P1a` and `P2a` passes rest
on loose readings of the registered rules. The record names those readings and the reps that fail
under stricter ones (history deviation, Task 2, commit `c0756d0`).

### 3. The new file: `skills/writing-skills/references/claude-code.md`

This 64-line file holds every sentence whose truth depends on Claude Code. It has four parts:

- **Frontmatter keys** (line 8): `when_to_use`, `model`, `effort`, `context: fork`, `agent` and
  `disable-model-invocation`. The `model` bullet says that with `context: fork`, `model` sets the
  forked subagent's model. That clause departs from the plan's verbatim text. The Task 3 ruling
  added it because the guide row states it (history ruling, Task 3, commit `942fee0`).
- **A Haiku `model`** (line 26): why `model: haiku` applies on one provider and is ignored on another.
- **When to fork** (line 34): the fork advice moved here from `discovery.md`. It has a new reason,
  taken from the guide's `subagents.frontmatter` row. With fork mode off, nested subagents start in
  the background in `claude -p` and the Agent SDK, so a forked skill can return before they report.
- **The skill listing** (line 43) and **The body after compaction** (line 59): whole descriptions
  drop on overflow, least-invoked first. The tools and settings that show or change the budget are
  listed. Only each body's first 5,000 tokens come back after compaction, within a shared
  25,000-token budget.

The file has no citation comment. Drift rule R4.1 lets the SKILL.md citation cover it.

### 4. Portable advice and pointers in `discovery.md` and `SKILL.md`

`references/discovery.md:11` now lists only the keys the lint accepts and the Haiku lint rule. It
points to `claude-code.md`. Token Efficiency (around line 115) no longer says a description is
always resident. It says the description is the only text that loads before the skill triggers,
apart from the name and any `when_to_use` text a runtime appends. It also says a runtime may drop or
shorten it on overflow. The `@` reason at line 202 is now "Why bare names", a portability reason.

The `when_to_use` qualifier came late. The Task 5 review found rows 42 and 47 contradicted the guide,
and a ruling fixed both places (commits `3d0d226` and `b76c2a3`).

`SKILL.md` gains a pointer at lines 111–114, beside the one to `discovery.md`. Line 425 corrects the
listing wording. The directory examples now show `references/` and `scripts/`. The body measured
18,753 characters at Task 3, under the plan's 18,800 gate and the 19,700 window.

### 5. New-layout arms

The arms ran at `942fee0`, on both models, 60 reps in all. All twelve prompt-and-model bars were met
at 5 of 5. Two limits are on record. First, all 30 `read` passes came from the no-edit clause, so
read-before-edit stayed untested. Second, the `apply` prompts give the reference text as already
read. `P3a` is the one prompt that the new layout separated: 0 of 5 on base and 5 of 5 on new, on
Opus. Total spend was $3.4320 of the $30 cap. The `green` arm did not run.

### 6. Review against the guide and restamp

The record's review table has 56 rows. It covers `SKILL.md` and its seven on-demand files against
eight sections. The method was manual because `packets.py` `files()` copies only the citing file. Each
section has a covered row, so the citation at `SKILL.md:14` names all eight. It adds
`subagents.frontmatter` and `subagents.models`. `cli.py baseline cite` restamped it at `@2.1.306` and
wrote the eight hashes to `build/cc_guide/baseline.json`. The owner received rows 38, 41, 48 and 56
at the completion gate.

### 7. Register, NOTICE and backlog

In `build/cc_guide/conformance.toml`:

- `writing-skills-guide-gaps` is removed.
- `writing-skills-tdd-for-docs` (line 677) carries the narrower reason, the D2/D4 evidence and the new
  revisit trigger. The final review deleted "for such edits" from the reason, because the spec's
  wording governs (commit `40f5bf3`).
- `description-when-only` (line 633) now also lists `discovery.md` in `artifacts`. This came from the
  owner's ruling at the completion gate on row 38 (commit `d7811de`).

`NOTICE` records the new file and the corrected claims. It notes that the file departs from upstream
v7.0.1's `references/` map. The spec and plan move to `completed/`, and `specs/history.md` gains the
entry.

## What it adds to the project

- Skill authors who use writing-skills in Claude Code now meet a pointer to one file of
  guide-backed facts. Codex and Gemini sessions load that detail only if they follow the pointer.
- A later drift review of writing-skills checks one small file for Claude Code facts. When
  `/cc-guide` upkeep changes any of the eight cited sections, `SKILL.md` goes STALE again, as D5
  intends.
- The stale list from plan 43's drift sweep is empty. Two more older items are ticked: the distilled file from
  conformance Decision 10 and the residual writing-skills rewrite.
- `discovery.md` is now covered by the `description-when-only` deviation, so a `/cc-guide files`
  pass will not report its description-rule repeats.

Left for later, in `specs/deferred_items.md`:

- The guide lacks the `@`-path fact for local skills against claude.ai-synced ones.
- `packets.py` `files()` leaves out a SKILL.md's on-demand files.
- The kit's isolation pilot asks no identity question. One rep addressed the owner by surname.
- `claude-code.md` omits that a forked skill runs in the background by default in interactive
  sessions.
- From the Codex review of PR #184's code: `build/extract_structure.py` drops a contents line that
  has a page number but no title. That item came in with the merge of `origin/main`, not with
  plan 92.

A progress note also keeps the read-before-edit item open.

## Questions

1. What did plan 92 set out to do, and why did writing-skills, of all files, need it?
2. How was it built: what ran before the new file was written, and what did the RED result decide?
3. What does the branch add to the project, and what does it leave in the backlog?
