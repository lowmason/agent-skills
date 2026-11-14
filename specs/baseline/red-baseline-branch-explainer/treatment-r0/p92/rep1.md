# claude/compassionate-jennings-98ff45: plan 92, writing-skills against the Claude Code guide

## Synopsis

**The plan:** writing-skills held the last file that `cli.py lint` stamped STALE. Some of its Claude Code facts were wrong or had no source, and they were mixed with portable advice in `references/discovery.md`. Because writing-skills is the meta-skill, a wrong fact spreads to every skill an agent writes. Plan 92 set out to close three backlog items at once. It would move the Claude Code facts into one distilled file, correct the bad claims, settle two register entries and restamp the citation.

**The build:** First came a micro-test kit and pre-registered rules. Next, a RED control and a descriptive arm ran on the old text. The RED run found no failure, so no new instruction was added. Then a new file, `references/claude-code.md`, took the Claude Code facts, and `discovery.md` and `SKILL.md` gained pointers to it. The register gap went away and the TDD deviation got a new reason. New-layout arms met every bar on both models. Last, a 56-row review against the guide fixed two rows and restamped the citation at `@2.1.306`.

**The project:** `cli.py lint` now prints no `STALE` line. writing-skills states only guide-backed Claude Code facts, and they live in one file. Four new backlog items and one Codex finding go to the backlog.

## Background

Plan 72 split writing-skills to 434 body lines. It moved most of the Claude Code text into `references/discovery.md`. There it sat beside lint rules and advice that holds on every runtime. At BASE, the frontmatter bullet in `discovery.md:11` mixed the lint's key list with key meanings, the Haiku portability reason and the fork advice.

Several claims did not match the guide. The spec lists them as C1 to C8:

- C1: the description was "resident in EVERY conversation", and `SKILL.md` called the listing "always-loaded". The guide says Claude Code drops whole descriptions when the listing overflows its budget.
- C2: there was no advice to put critical rules near the top (audit S-67).
- C3: "`@` syntax force-loads files immediately, consuming 200k+ context". No source supported it.
- C4: the advice not to fork a skill that dispatches subagents rested on a premise that is gone.
- C5 and C7: the `haiku` facts and the key meanings needed a home and a cited section.
- C8: the directory examples showed no `references/` or `scripts/` folders.

The conformance register held gap `writing-skills-guide-gaps` for S-58, S-67 and S-107. It also held deviation `writing-skills-tdd-for-docs`, whose revisit trigger was this rewrite. The `SKILL.md` citation was `@2.1.219`, so `cli.py lint` printed one STALE line. That backlog item would have entered the aged tail on 2026-11-27 and started to block merges.

The spec (`specs/completed/writing-skills-guide-rewrite.md`) chose to distill (D1), to keep and refresh the TDD deviation (D2), to waive reps for factual corrections (D4) and to review against the guide as it is on main, with no `/cc-guide` pass (D5).

## The change

### 1. The micro-test kit and its rules

`specs/baseline/red-baseline-writing-skills-guide/kit/` adapts plan 72's kit. `cases.py` holds four frozen conversations. `R1` asks for a long skill with one hard rule. `P1`, `P2` and `P3` test a Claude Code-only key, a dropped description and the fork decision. Each case has a `read` and an `apply` prompt. `build_prompts.py` inlines the skill text at a given commit and layout. `run_reps.sh` runs each rep with `--tools ""`, `--setting-sources ""` and `--disable-slash-commands` (line 29), so no installed skill reaches a rep. `probe.sh` and `isolation_probe.txt` run the isolation pilot.

The record, `specs/baseline/red-baseline-writing-skills-guide.md`, fixed every pass rule and bar at `d1aaba9`, before any rep ran (commit `b897a61`). The R1 rule scores where the hard rule first appears relative to a table line that stands for more than the 19,700-character compaction window. Everything after this step depends on these rules.

### 2. RED control and descriptive arm on the old text

Commit `f88f36a` ran 25 reps at `3684b96`. `R1` passed 5 of 5 on both models, so the record states `RED outcome: null`. Under the spec, a null RED means no template slot is added. `claude-code.md` states the compaction mechanism only, and S-67's part of the gap closes on this record.

The `desc` arm ran on Opus only and set no bar. It scored `P1a` 5 of 5, `P2a` 5 of 5 and `P3a` 0 of 5. Commit `c0756d0` added a note that names the loose `P1a(a)` and `P2a(a)` readings and the reps that fail under stricter ones. This is the first Task 2 deviation in the history entry.

### 3. `references/claude-code.md` and the pointers

Commit `e183c735` wrote `skills/writing-skills/references/claude-code.md` (64 lines). It has four parts:

- **Frontmatter keys:** `when_to_use`, `model`, `effort`, `context: fork`, `agent` and `disable-model-invocation`, with what each does.
- **A Haiku `model`:** why auto mode ignores it and why the alias differs by provider.
- **When to fork:** the fork advice, moved here from `discovery.md`. Its new reason comes from `subagents.frontmatter`. With fork mode off, nested subagents in `claude -p` and the Agent SDK start in the background, so a forked skill can return before they report.
- **The skill listing** and **The body after compaction:** whole descriptions dropped, least invoked first, and the 5,000-token and 25,000-token figures.

Commit `942fee0` added one sentence to the `model` bullet: with `context: fork`, `model` sets the forked subagent's model. The history entry's Task 3 ruling records this as a departure from the plan's verbatim text, because the guide row states it.

`discovery.md:11` now lists only the keys the lint accepts and the Haiku lint rule, then points to `claude-code.md`. Token Efficiency (`discovery.md:115-122`) drops "resident in EVERY conversation" and points to `claude-code.md` for Claude Code's rule. The `@` example now reads "(a file path, not a skill name)", and `discovery.md:202` gives a portability reason under "Why bare names". `SKILL.md:111-114` adds the pointer paragraph, the listing step gets its new wording, and the directory examples show `references/` and `scripts/`. The body grew from 18,285 to 18,753 characters (new `MANIFEST.txt`), under the spec's 18,800 target.

### 4. Register and NOTICE

In `build/cc_guide/conformance.toml`, the `writing-skills-guide-gaps` block is gone. With RED null and the `@` claim dropped, no part stayed open. `writing-skills-tdd-for-docs` keeps its place with a new reason, evidence and revisit trigger, as D2 asked. The final review removed "for such edits" from the reason (commit `40f5bf3`), because the spec's wording governs. `NOTICE` gains a 14-line entry for plan 92 in the superpowers changes list.

### 5. New-layout arms

Commit `2207cc59` ran 60 reps at `942fee0`. All 12 bars (`read` and `apply`, three prompts, two models) were met at 5 of 5, so no tightening round ran. The record gives two limits. All 30 `read` passes came from the no-edit clause, so read-before-edit stays untested. `P3a` is the one prompt where the new layout differs from the old one on Opus: 5 of 5 against 0 of 5. The record calls that comparison descriptive. Total spend was $3.4320 of the $30 cap. The `green` arm did not run.

### 6. Review against the guide and restamp

Task 5 reviewed `SKILL.md` and its seven on-demand files against eight guide sections in a 56-row table. Rows 42 and 47 were contradicted and are fixed. `discovery.md` now says that, apart from the name and any `when_to_use` text a runtime appends, the description is the only text that loads before a skill triggers (commits `3d0d226` and `b76c2a3`). The history entry's Task 5 ruling explains this. Row 38 is the description rule that `discovery.md` repeats. At the completion gate the owner added `discovery.md` to the `artifacts` of `description-when-only` (commit `d7811de`). Rows 41, 48 and 56 were listed for the owner as not covered. The history entry records no ruling on them.

The guide on `origin/main` had not changed, so no second review ran. `cli.py baseline cite` restamped `SKILL.md:14` to eight sections at `@2.1.306`, adding `subagents.frontmatter` and `subagents.models`. It wrote eight `text_hash` entries to `build/cc_guide/baseline.json`.

### 7. Closing the plan

Commit `c3ee1807` marks plan 92 complete and updates the backlog. Commit `cecc5dc8` merges `origin/main`. Commit `f17319a9` moves the plan and spec to `completed/` and adds the history entry. Commit `0b6d34f4` files a Codex finding about `build/extract_structure.py`. That code came from PR #184, not from this branch.

## What it adds to the project

- **Drift backlog cleared.** `cli.py lint` prints no `STALE` line. The aged-tail deadline of 2026-11-27 no longer applies. When `/cc-guide` upkeep changes any of the eight cited sections, writing-skills goes STALE again, as D5 intends.
- **One home for Claude Code facts.** Skill authors in Claude Code follow a pointer to `claude-code.md`. Codex and Gemini sessions skip it unless they follow the pointer. A future drift review checks one small file.
- **Corrected guidance.** Skills that agents write will not repeat "always resident" or the `@` force-load claim. They also get a guide-backed fork rule.
- **Register.** One gap fewer. `description-when-only` now covers `discovery.md` too. `writing-skills-tdd-for-docs` states the narrow real difference.
- **Three backlog items closed:** the distilled `references/` file (plan 35), the 41 STALE files (plan 43), and the writing-skills rewrite (plan 53). The read-before-edit item from plan 72 gains a progress note and stays open.

Deferred items added in `specs/deferred_items.md`:

1. The guide omits the docs fact about `@` paths in local and synced skills. It goes to `skills.progressive-disclosure`.
2. `packets.py` `files()` leaves a SKILL.md's on-demand files out of a `/cc-guide files` packet.
3. The kit's isolation pilot asks no identity question, and one rep addressed the owner by surname.
4. `claude-code.md` does not say that a forked skill runs in the background by default in interactive sessions.
5. From the Step 4b Codex review: `extract_structure.py` drops a contents line that has a page and no title.

## Questions

1. What did plan 92 set out to do, and why did the meta-skill and the last STALE file make it urgent?
2. How was it built? Name the parts in order, and say how the null RED result shaped what was added.
3. What does the branch add to the project, and what does it leave in the backlog?
