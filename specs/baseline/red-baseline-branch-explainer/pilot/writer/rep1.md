# Plan 92: writing-skills checked against the Claude Code guide

Range: `e3824937..0b6d34f4` (the branch `claude/compassionate-jennings-98ff45`, with `origin/main`
merged in at `cecc5dc8`). The base is the PR #184 merge on main, so the diff holds only this
branch's work: 15 commits and 115 files. About 8,000 of the added lines are raw micro-test output.

## In short

The branch carries out plan 92, which follows the approved spec `specs/writing-skills-guide-rewrite.md`.
It closes three backlog items with one change to the `writing-skills` skill:

1. **New file `skills/writing-skills/references/claude-code.md` (64 lines).** It gathers the facts
   that hold only for Claude Code: what the extension frontmatter keys do, why a Haiku `model` is
   not portable, when to fork a skill, how the skill listing drops descriptions, and what of a body
   survives compaction. These are the repository's own words, drawn from the guide sections.
2. **`references/discovery.md` and `SKILL.md` keep the advice that holds on every runtime.** Each
   one points to the new file. Four claims were corrected (details below).
3. **Register and drift bookkeeping.** The gap entry `writing-skills-guide-gaps` is gone. The
   deviation `writing-skills-tdd-for-docs` has a new reason. `SKILL.md`'s citation is restamped from
   `@2.1.219` to `@2.1.306` and now names eight sections. `cli.py lint` no longer prints any
   `STALE` line.
4. **Micro-test evidence** is in `specs/baseline/red-baseline-writing-skills-guide.md`, with the
   kit and the raw reps.

The last two commits retire plan 92 (the spec moves to `specs/completed/`, and a history entry is
added). They also add an unrelated backlog item: a Codex finding about `build/extract_structure.py`
from PR #184.

## Changes that agents will see

### `references/claude-code.md` (new)

- **Frontmatter keys:** `when_to_use` (added to the end of the description and counted against the
  same listing entry's cap), `model`/`effort` (and what `model` means under `context: fork`),
  `context: fork` (the body runs in an isolated subagent and must stand alone), `agent`, and
  `disable-model-invocation` (the skill leaves the listing, and a subagent can't preload it). It
  also notes that Claude Code ignores unknown keys silently.
- **A Haiku `model`:** auto mode ignores Haiku 4.5 and earlier, and `haiku` resolves to 5.5 on the
  Anthropic API but to 4.5 on Bedrock, Google Cloud, Foundry and Claude Platform on AWS. The
  existing lint ban rests on this.
- **When to fork:** the fork guidance moved here word for word from `discovery.md`. It now gives a
  reason, backed by the guide, for not forking a skill that dispatches subagents: with fork mode off,
  nested subagents start in the background in `claude -p` and the SDK, so the fork can return
  before its reviewers report.
- **Skill listing:** whole descriptions are dropped, starting with the skills invoked least, and the
  knobs are `/doctor`, `/skill-doctor`, `/context`, `skillOverrides`, `skillListingBudgetFraction`,
  `SLASH_COMMAND_TOOL_CHAR_BUDGET`, `skillListingMaxDescChars`, and disabling plugins.
- **After compaction:** the most recent invocation of each skill is re-attached, with the first
  5,000 tokens of each body and a shared budget of 25,000 tokens, newest first.

### `references/discovery.md`

- The long "Optional keys" bullet becomes a plain list of keys plus the Haiku lint rule, with a
  pointer to `claude-code.md`. The fork bullet is removed because it now lives in `claude-code.md`.
- **Corrected:** a description is no longer called "resident in EVERY conversation". It is now
  described as text that loads before the skill triggers, which a runtime may drop or shorten. After
  review, it adds "apart from its name and any `when_to_use` text that a runtime appends" in two
  places.
- **Corrected:** the reason against `@skills/...` links. The old claim, "force-loads, consuming
  200k+ context", had no support in the guide. It is replaced by a portability reason: a bare skill
  name lets each runtime load the skill through its own mechanism.

### `SKILL.md`

- The Directory Structure and File Organization examples now show `references/` and `scripts/`.
- A new pointer paragraph says to read `claude-code.md` before setting a key that only Claude Code
  reads, or when the skill will run in Claude Code.
- "the always-loaded list" becomes "loaded before any skill triggers; an overfull listing can lose
  descriptions".
- The `cc-guide` citation adds `subagents.frontmatter` and `subagents.models`, at `@2.1.306`.

### `NOTICE`

A new paragraph under the superpowers changes records plan 92. It notes that `claude-code.md`
departs from the `references/` map of upstream v7.0.1 and that no upstream text was taken.

## Register changes (`build/cc_guide/conformance.toml`)

- **Removed** the gap `writing-skills-guide-gaps`. This work was what it tracked: its listing-budget
  and `@`-loading parts are fixed by the text changes above. Its critical-rules-first part (S-67)
  closes on a null RED run (see the evidence below).
- **`writing-skills-tdd-for-docs`** gets a narrower reason. The guide already keeps TDD for behaviour
  changes, so the real departure is that the Iron Law also covers edits that change no instruction,
  such as typos, links and verbatim moves. In practice you waive those case by case. The
  `revisit` trigger changed to match.
- **`description-when-only`** `artifacts` now includes `references/discovery.md`. This was your
  ruling at the completion gate. Without it, the next `/cc-guide files` pass would report the
  trigger-only rule repeats in discovery.md as unregistered contradictions.

`build/cc_guide/baseline.json` gains text hashes for the eight cited sections.

## Evidence

The rules and bars were registered at `d1aaba9`, before any rep ran. Each arm ran 5 reps of
`claude -p` in fresh contexts with no tools. Verdicts were read by hand. The total spend was $3.43 of
a $30 cap.

| Arm | What it asks | Result |
|---|---|---|
| `red` (old layout, R1) | Does an agent put a hard rule after a huge table, past the 5,000-token re-attach window? | 0 of 5 FAIL on Opus and on Sonnet, so the outcome is **null**. `green` did not run, and no compaction instruction was added (decision D5) |
| `desc` (old layout, Opus) | Baseline for the apply prompts | P1a 5/5, P2a 5/5, **P3a 0/5** |
| `read` (new layout) | Do the pointers in discovery.md send the agent to `claude-code.md`? | 5/5 on every prompt and both models |
| `apply` (new layout) | Does the agent use the facts? | 5/5 on every prompt and both models. **P3a goes from 0/5 to 5/5** on Opus |

Limits that the record states openly, which you should weigh:

- **P3a is the only prompt that tells the old and new layouts apart.** P1a and P2a already passed on
  the old layout, and only under loose readings that the record names (commit `c0756d0`). Under the
  stricter readings, all 5 old-layout reps of each fail.
- **The `read` arm never tested read-before-edit.** All 30 passes come from the no-edit clause,
  because no rep tried an edit. The arm shows that agents go and read the file, but not that they
  read it before they edit. The open backlog item about read-before-edit stays open with this note.
- **The `apply` prompts already contain `claude-code.md`.** So they test whether the agent uses a
  fact, not the full read-then-use chain.
- **The tests ran on the text at `942fee0`.** Two later edits changed `discovery.md` (the
  `when_to_use` qualifier, at lines 115 and 122), and those edits were not re-tested. The record
  calls them factual corrections that add no instruction (spec D4), and the pointer clause that was
  tested kept its exact words. In my view this is a small gap.

## Verified on this checkout

- `build/run_commit_lints.sh`: all lints passed (frontmatter, provenance, conformance, cc_guide lint,
  links, deferral lint and the others).
- `cli.py lint`: 0 `STALE` lines, as the backlog item requires.
- `run_suites.py cc_guide`: 735 passed. `test_check_conformance.py` and
  `test_check_frontmatter.py`: 446 passed.

I did not re-run any micro-test reps.

## Items to check before you merge

1. **Your name is in a committed transcript.** `specs/baseline/red-baseline-writing-skills-guide/new/P1a-sonnet/rep5.json`
   addresses you by name ("Mason, the two requirements conflict…"). Account identity got past the
   kit's isolation flags. Your name already appears in `SKILL.md`'s `adapted_by`, so this exposes
   little. Still, if you'd rather keep model output that names you out of history, redact that rep
   before you merge. The new backlog item only fixes the probe for future runs.
2. **The new fork-mode reason is narrow.** It applies only when `CLAUDE_CODE_FORK_SUBAGENT=0`, and
   in `claude -p` or the SDK. The default is fork mode on, which the file says. A related fact is
   deferred: in interactive sessions a forked skill runs in the background by default. So the fork
   paragraph is not yet complete.
3. **The `@`-link change drops a claim instead of replacing it with a Claude Code fact.** The docs
   say local skills do attach `@`-named files, but the guide doesn't say so yet. That is deferred as
   a `/cc-guide` quick fix.
4. **Rows 41, 48 and 56 were sent to you and left unchanged:** "injected into system prompt",
   "50–100× context saving" and the category folders under `~/.claude/skills/`. The guide supports
   none of them. Check that leaving them was your intended ruling.

## New backlog items (`specs/deferred_items.md`)

The five open items are:

- The guide is missing the `@`-path fact for local skills versus skills synced from claude.ai.
- `packets.py files()` leaves a skill's on-demand Markdown files out of a `/cc-guide files` packet,
  even though rule R4.1 says a SKILL.md citation covers them.
- The kit's isolation probe never asks about user identity (see item 1 above).
- `claude-code.md` doesn't state that a forked skill runs in the background by default in
  interactive sessions.
- *(Not related to plan 92, from the Codex review of PR #184)* `extract_structure.py` silently
  drops a contents line such as `1.1 2` that has a page number but no title, and
  `check_complete` still passes.

Three items are ticked closed: the distilled `references/` file, the review of the 41 files marked
stale, and the split and rewrite of writing-skills against the guide.

## Verdict

The change is confined to one skill's documentation, the register and the specs. All lints and the
relevant suites pass. The evidence supports the new file and its pointers, with the limits stated
above. The only thing I'd act on before merging is item 1, if the name in the transcript matters to
you.
