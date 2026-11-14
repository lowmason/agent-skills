# What `e382493..HEAD` changes: plan 92, writing-skills checked against the Claude Code guide

## In one paragraph

This branch carries out plan 92. It moves the Claude Code facts in the `writing-skills` skill into a new
file, `skills/writing-skills/references/claude-code.md`, and fixes the claims that the guide in
`specs/guides/claude-code-customization-guide.md` does not support. It also closes one conformance-register
entry and gives another a new reason. Then it reviews the skill against the guide and restamps the skill's
citation, so `cli.py lint` no longer reports any file as `STALE`. Micro-tests check that agents find and
use the new file. Plan 92's spec and plan move to `completed/`, and the backlog and history files are
updated.

Size: 115 files and about 8,600 added lines. Almost all of it (about 8,300 lines) is the recorded test
evidence in `specs/baseline/red-baseline-writing-skills-guide/`. The skill text itself changes by about
100 lines.

The merge commit `cecc5dc8` brings in `origin/main` (PR #184). Your base commit `e382493` is that PR's merge,
so none of PR #184's code is part of this diff.

## The skill changes (the part to read closely)

### New: `skills/writing-skills/references/claude-code.md` (64 lines)
It holds the facts that apply only to Claude Code, written in the repository's own words:
- **The frontmatter keys only Claude Code reads:** `when_to_use` (added to the description and sharing its
  length cap), `model`/`effort` (with `context: fork`, `model` sets the forked subagent's model instead),
  `context: fork`, `agent`, and `disable-model-invocation` (also takes the skill out of the listing, and
  a subagent can no longer preload it). Claude Code silently ignores keys it does not recognise.
- **Why a Haiku `model` is not portable:** auto mode ignores Haiku 4.5, and the `haiku` alias points to
  different models on different providers.
- **When to fork:** this advice moved here word for word from `discovery.md`. It now has a reason the
  guide supports. When fork mode is off, the subagents a forked skill starts can run in the background, so
  the fork can return before they report.
- **The skill listing budget:** Claude Code drops whole descriptions, starting with the skills used least.
  The section lists the tools for this (`/doctor`, `/skill-doctor`, `/context`) and the settings
  (`skillOverrides`, `skillListingBudgetFraction`, `SLASH_COMMAND_TOOL_CHAR_BUDGET`,
  `skillListingMaxDescChars`).
- **Compaction:** Claude Code keeps the first 5,000 tokens of each body it re-attaches, with a combined
  budget of 25,000 tokens, filled newest first.

### `SKILL.md`
- A new pointer paragraph sends the reader to `claude-code.md` before they set a key only Claude Code reads.
- The directory examples now show `references/` and `scripts/`, which the skill's own layout already uses.
- Discovery step 2 no longer calls the listing "always-loaded". It now says an overfull listing can lose
  descriptions.
- The `# cc-guide:` citation adds `subagents.frontmatter` and `subagents.models`, and it is restamped from
  `@2.1.219` to `@2.1.306`. `build/cc_guide/baseline.json` records the hash of each of the eight sections.

### `references/discovery.md`
- The long optional-keys bullet is now shorter. It lists the keys the lint accepts, says the lint rejects a
  Haiku `model`, and points to `claude-code.md` for what each key does.
- **Token Efficiency:** the old text said a description is "resident in EVERY conversation", which the guide
  contradicts. The new text says the description loads before the skill triggers, together with the name
  and any `when_to_use` text, and that a runtime may drop or shorten it.
- **@ links:** the old reason said `@` "force-loads files … consuming 200k+ context", which the guide does
  not support. The new reason is portability: a bare skill name lets each runtime load the skill its own
  way. The ❌ example's comment now reads "(a file path, not a skill name)".

### Register (`build/cc_guide/conformance.toml`) and `NOTICE`
- **`writing-skills-guide-gaps` is deleted.** The new file and the edits above close its listing-budget,
  `@`-loading and progressive-disclosure parts. Its "critical rules first" part closes on a null RED test
  (below).
- **`writing-skills-tdd-for-docs` stays, with a narrower reason:** the guide already keeps TDD for behaviour
  changes. The departure now covers only the edits that change no instruction (a typo, a link, a verbatim
  move), and you waive those case by case. A new `revisit` condition was added.
- **`description-when-only` now also lists `references/discovery.md` in its `artifacts`.** You decided this
  at the completion gate. Without it, the trigger-only description rule that `discovery.md` repeats would
  show up as an unregistered deviation.
- **`NOTICE`:** a new entry in the superpowers changes list describes the new file and states that no
  upstream text was taken.

## The tests

The full record is `specs/baseline/red-baseline-writing-skills-guide.md`, with the kit, prompts and raw
reps. Each rep was a fresh, isolated `claude -p` run with no tools. The rules were registered before any rep
ran. Total spend was $3.43 of the $30 cap.

| Arm | What it asked | Result |
|---|---|---|
| `red` (old text, Opus and Sonnet) | When the agent writes a skill with a long table, does the hard rule come after the table, past the 5,000-token compaction window? | 0 of 10 FAIL, so **the outcome is null**. No "Hard Rules" slot was added, and `claude-code.md` only states the compaction mechanism. |
| `desc` (old text, Opus) | Apply the facts for P1 (preloading), P2 (dropped description) and P3 (forking a skill that starts subagents). | P1a 5/5, P2a 5/5, **P3a 0/5** |
| `read` (new text, both models) | Does the `discovery.md` pointer send the agent on to `claude-code.md`? | 30/30, every bar met |
| `apply` (new text, both models) | Same tasks as `desc`, with the new file in context | 30/30, every bar met (**P3a 5/5**) |
| `green` | Only if `red` showed the failure | Not run |

What these results do not show (the record says so itself):
- All 30 `read` passes come from the "no edit" clause. No rep made an edit, so the tests do not show that an
  agent reads the file *before* it edits.
- The `apply` prompts already contain the reference text, so they test whether the agent uses a fact, not
  whether it reads the file and then uses it.
- P1a and P2a pass on the old text too, under readings the record names as loose. Under stricter readings,
  all `desc` reps fail those parts. **P3a is the only prompt where the new text made a clear difference.**

## Review against the guide

The record has a 56-row table that checks `SKILL.md` and its seven on-demand files against the eight cited
sections. Rows 42 and 47 contradicted the guide and were fixed (the "only text that loads before triggering"
wording). Row 38 was settled by your `artifacts` decision above. Rows 41, 48 and 56 ("injected into system
prompt", the "50–100×" saving from subagents, and category folders under `~/.claude/skills/`) are listed for
you as "not covered". The record does not say how you ruled on each of the three.

## Bookkeeping
- `specs/writing-skills-guide-rewrite.md` → `specs/completed/` (marked COMPLETE).
- `specs/plans/92-…md` → `specs/plans/completed/` (all steps ticked, with deviation and skip notes).
- `specs/history.md`: plan 92 entry with four rulings, five deviations, and three earlier deferred items
  closed.
- `specs/deferred_items.md`: three items ticked, one progress note, and five new open items:
  1. The guide does not say that `@` paths in a local skill's body are attached, but not in a skill synced
     from claude.ai.
  2. `packets.py` `files()` leaves a skill's on-demand files out of a `/cc-guide files` packet.
  3. The kit's isolation probe never asks whether the agent knows the user's identity (see the warning below).
  4. `claude-code.md` does not say that a forked skill runs in the background by default in interactive
     sessions.
  5. The last commit adds a Codex finding against PR #184's `extract_structure.py`: a contents line with a
     page number but no title is silently dropped, and `check_complete` still passes.

## Before you merge

1. **One committed rep contains personal data.**
   `specs/baseline/red-baseline-writing-skills-guide/new/P1a-sonnet/rep5.json` addresses you by surname
   ("Mason, the two requirements conflict…"). Deferred item 3 records this, but the file is still committed.
   I searched the whole baseline directory for your name, your email and `/Users/` paths. That is the only
   match, and no email appears. If the repository is public, consider removing the name before you merge.
2. **Deferred item 4 is a gap in the new reference.** In interactive sessions, a forked skill runs in the
   background by default, and `claude-code.md` does not say so. The fork paragraph only covers the
   fork-mode-off case.
3. **Item 5 is a real bug on `main`, not on this branch.** It sits in code that PR #184 already merged. This
   branch only records it.

## Verification I ran
- `bash build/run_commit_lints.sh` ends `commit lints passed`.
- `uv run python build/cc_guide/cli.py lint` prints nothing, so no `STALE` line is left.

I did not re-run any micro-test reps. The test results above come from the committed record.
