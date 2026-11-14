# Branch `claude/compassionate-jennings-98ff45`: plan 92, writing-skills against the Claude Code guide

## Synopsis

**The plan:** Plan 92 set out to bring writing-skills in line with the repository's Claude Code guide. writing-skills is the meta-skill that every runtime follows when it edits a skill, so a wrong Claude Code fact in it spreads. Its `SKILL.md` was the last file that `cli.py lint` listed as STALE. The plan closes three backlog items: distill the Claude Code facts into one reference file, settle the two register entries on writing-skills, and review and restamp `SKILL.md`.

**The build:** A micro-test kit and its rules came first, registered before any rep ran. A RED control and a descriptive arm then ran on the old text. The RED control found no failure, so no "critical rules first" instruction was added. Next, a new `references/claude-code.md` took the Claude Code facts, and `discovery.md` and `SKILL.md` were cut to portable advice with pointers. The register and `NOTICE` changed in the same commit. The new-layout arms then met every bar. Last, a 56-row review against eight guide sections led to a restamped citation and two wording fixes.

**The project:** writing-skills now keeps its Claude Code facts in one file, each backed by a guide section. The drift backlog has no STALE file left. Gap `writing-skills-guide-gaps` leaves the register. The branch adds five deferred items.

## Background

writing-skills had already been split by plan 72, which cut the `SKILL.md` body to 434 lines. That split moved most of the Claude Code text into `references/discovery.md`. There it sat mixed with repo lint rules and advice that holds on every runtime. Decision 10 of the conformance spec had put off a distilled Claude Code file until the split. That item stayed open.

The drift system tracks files against `specs/guides/claude-code-customization-guide.md`. `SKILL.md` cited six guide sections `@2.1.219`. It was the last STALE file in `cli.py lint`. That backlog item was due to enter the aged tail on 2026-11-27 and then block merges (spec, Why).

The register `build/cc_guide/conformance.toml` held two entries on writing-skills:

- Gap `writing-skills-guide-gaps` covered three departures: the listing budget (S-58), critical rules near the top (S-67) and `@` loading (S-107).
- Deviation `writing-skills-tdd-for-docs` had a revisit trigger that pointed at this rewrite.

The spec lists the wrong or unsupported claims. Examples: a description "resident in EVERY conversation", `@` links that "force-load" files, and directory examples with no `references/` folder. The fork advice also lacked a reason that the guide supports.

## The change

### 1. Micro-test kit and registered rules

`specs/baseline/red-baseline-writing-skills-guide/kit/` adapts plan 72's kit. `run_reps.sh` runs `claude -p` with no tools, no settings sources and `--disable-slash-commands` (plan decision D12), from a new empty directory per rep. `cases.py` holds the fixtures, and `build_prompts.py` builds the prompts for a `base` or `new` layout from `git show`. `probe.sh` and `isolation_probe.txt` run an isolation pilot.

The record `specs/baseline/red-baseline-writing-skills-guide.md` registers five arms (`red`, `desc`, `read`, `apply`, `green`) and their pass rules. They were committed before any rep ran. Every later arm depends on these rules.

### 2. RED control and descriptive arm on the old text

The `red` arm asks for a new skill whose body holds a 24,000-character table and one hard rule. A rep fails when the rule first appears after the table. All 10 reps passed, 5 on each model. So RED was null. Under decision D5, S-67's part of the gap closed on this record, and no new instruction went into the skill.

The `desc` arm ran the three apply prompts on the old layout, on Opus. `P1a` and `P2a` scored 5 of 5, and `P3a` scored 0 of 5. In `P3a`, every rep gave the wrong reason not to fork a skill that dispatches subagents. A late commit (c0756d0) records the loose readings of `P1a(a)` and `P2a(a)` behind those passes. The entry lists this as a Task 2 deviation.

### 3. `references/claude-code.md` and the portable cut

This is the core of the branch. It depends on part 2's null outcome.

`skills/writing-skills/references/claude-code.md` is new (64 lines). It holds four sections:

- **Frontmatter keys**: what `when_to_use`, `model`, `effort`, `context: fork`, `agent` and `disable-model-invocation` do in Claude Code. The `disable-model-invocation` bullet carries the guide's whole row, including that a subagent cannot preload the skill (decision D8).
- **A Haiku `model`**: why it is not portable across providers and auto mode.
- **When to fork**: the fork advice, moved whole from `discovery.md` (decision D7). It gets a narrow reason: with fork mode off, nested subagents in `claude -p` and the Agent SDK start in the background, so a forked skill can return early. Fork mode is on by default (decision D6).
- **The skill listing** and **The body after compaction**: Claude Code drops whole descriptions on overflow, and keeps the first 5,000 tokens of each re-attached body within a 25,000-token budget.

`references/discovery.md` keeps the list of keys that the lint accepts and the Haiku ban. It drops the Claude Code detail and points to `claude-code.md` (line 11). Token Efficiency no longer says the description is resident in every conversation (lines 115-123). The `@` example now reads "(a file path, not a skill name)" (decision D10). "Why no @ links" became "Why bare names", a portability reason (line 202).

`skills/writing-skills/SKILL.md` gains a pointer paragraph to `claude-code.md` (lines 111-114). The directory examples show `references/` and `scripts/`. The listing line no longer says "always-loaded" (line 425).

The same commit (e183c735) removes `writing-skills-guide-gaps` from `conformance.toml` and refreshes `writing-skills-tdd-for-docs`. Its new reason says the departure is narrow: the guide keeps TDD for behaviour changes, but the Iron Law also covers edits that change no instruction. `NOTICE` gains a plan 92 entry under the superpowers changes.

One ruling changed the planned text. Task 3 added "With `context: fork`, `model` sets the forked subagent's model instead." The brief's verbatim text had dropped that clause, which the guide states. A fix round (942fee0) became `T3_SHA`, the commit under test.

### 4. New-layout arms

This part tests part 3 at `942fee0`. The `read` arm checks that an agent opens `claude-code.md` after it sees the pointer. The `apply` arm checks that it uses the fact. All 12 prompt-and-model cells scored 5 of 5 against a bar of 4 of 5. No tightening round ran.

The record names two limits. All 30 `read` passes came from the no-edit clause, so read-before-edit stays untested. `P3a` is the one prompt the new layout separated: 0 of 5 on the old layout, 5 of 5 on the new, Opus. The record gives total spend as $3.4320 of the $30 cap.

### 5. Review against the guide and restamp

This part depends on the final text. The record's `## Review against the guide` table has 56 rows. They cover `SKILL.md` and its seven on-demand files against eight sections. The record counts 45 covered, 4 contradicted, 3 not covered, and 4 files with no Claude Code statement.

- Row 5 is the registered deviation `description-when-only`, left as it is.
- Rows 42 and 47 were fixed in `discovery.md` (3d0d226, b76c2a3). The text now says that the name and any `when_to_use` text also load before a skill triggers. A Task 5 ruling made this fix in both places, because a half-fixed contradicted row is not fixed.
- Row 38 went to the owner. At the completion gate, the owner added `discovery.md` to the `artifacts` of `description-when-only` (d7811de).

The `SKILL.md` citation now names eight sections, adding `subagents.frontmatter` and `subagents.models`, stamped `@2.1.306`. `cli.py baseline cite` wrote eight hashes to `build/cc_guide/baseline.json`.

A final-review ruling (40f5bf3) deleted "for such edits" from the tdd-for-docs reason. The spec's wording governs over the plan's.

### 6. Closeout

`specs/history.md` gains the plan 92 entry: four rulings, five deviations, four deferred items. The plan and spec moved to `completed/`. The merge cecc5dc8 brought in PR #184. The last commit adds a fifth deferred item from the Codex review: `build/extract_structure.py` drops a contents line that has a page but no title. That item is about PR #184's code, not about writing-skills.

## What it adds to the project

- **Skill authoring flow.** An agent that edits a skill on Codex or Gemini reads only portable advice in `discovery.md`. It still finds every key the lint accepts and the Haiku ban. An agent on Claude Code follows one pointer to one file of version-dependent facts. A future drift review of writing-skills checks that one file.
- **Drift backlog.** The backlog note says `cli.py lint` now prints no `STALE` line. Three items close: the distilled file (Decision 10), the 41 STALE files from plan 43, and the writing-skills rewrite from plan 53. Later `/cc-guide` changes to any of the eight cited sections will make `SKILL.md` STALE again, which is the intended design (spec D5).
- **Register.** One gap fewer. `description-when-only` now also covers `discovery.md`. `writing-skills-tdd-for-docs` revisits when the guide's TDD row names agent-facing text, or when the Iron Law changes.
- **Evidence.** The RED record is the evidence that writing-skills needs no "critical rules first" slot today.

Deferred, in `specs/deferred_items.md`:

- The guide omits that `@` paths attach files in a local skill but not in one synced from claude.ai. Until `/cc-guide` adds it, `discovery.md` gives only the portability reason.
- `packets.py` `files()` leaves a SKILL.md's on-demand files out of a `/cc-guide files` packet.
- The kit's isolation pilot never asks about user identity, and one rep named the owner.
- `claude-code.md` omits that a forked skill runs in the background by default in interactive sessions.
- `extract_structure.py` drops a numbered contents line with no title (from PR #184).

A progress note on the plan 72 item "The `t3` micro-test passes show less than they appear to" keeps it open.

## Questions

1. What did plan 92 set out to do, and why did writing-skills need it more than other skills?
2. How was it built: what ran before the text changed, what moved into `claude-code.md`, and what did the review and restamp settle?
3. What does the branch add to the project: what changes for an agent writing a skill, for the drift backlog and for the register, and what is left for later?
