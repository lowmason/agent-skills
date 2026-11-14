# What `e382493..0b6d34f` changes: plan 92, writing-skills checked against the Claude Code guide

## Summary

This branch carries out **plan 92**. It moves `writing-skills`' Claude Code facts into a new file,
corrects six claims the guide doesn't support, settles two conformance-register entries, and
restamps the skill's `cc-guide` citation. With that restamp, `cli.py lint` prints no `STALE`
line for the first time since plan 43.

The diff is large (115 files, +8.6k lines), but most of it is test evidence. The text that ships
changes in about 120 lines across 7 files:

| File | What changed |
|---|---|
| `skills/writing-skills/references/claude-code.md` | **New** (64 lines). Claude Code–only facts: frontmatter keys, Haiku `model`, when to fork, the listing budget, compaction. |
| `skills/writing-skills/references/discovery.md` | The key list is shorter, the fork advice moved out, the "always resident" and `@` claims are corrected, and two pointers to the new file were added. |
| `skills/writing-skills/SKILL.md` | A pointer to the new file, directory examples that now show `references/` and `scripts/`, the corrected listing wording, and a new citation. |
| `build/cc_guide/conformance.toml` | `writing-skills-guide-gaps` removed, `writing-skills-tdd-for-docs` reworded, and `description-when-only` widened to cover `discovery.md`. |
| `build/cc_guide/baseline.json` | Text hashes for the eight sections the new citation names. |
| `NOTICE` | One new entry in the superpowers changes list. |
| `specs/…` | Plan and spec retired to `completed/`, history entry, 3 backlog items closed, 5 opened. |

The merge commit `cecc5dc` has `e382493` as a parent, so the range diff holds only this branch's
work. PR #184's `extract_structure` changes are not part of it.

## The skill-text changes in detail

### New: `references/claude-code.md`

This file holds facts that are true only in Claude Code and can change between its versions. Its
four sections:

- **Frontmatter keys.** It covers what `when_to_use`, `model`/`effort`, `context: fork`, `agent` and
  `disable-model-invocation` do. One point is new: with `disable-model-invocation`, a subagent
  can't preload the skill. It also notes that Claude Code ignores unknown keys silently.
- **A Haiku `model`.** This is the portability reason that used to sit in a long parenthetical in
  `discovery.md`. Auto mode ignores Haiku 4.5, and `haiku` means 5.5 on the Anthropic API but 4.5
  on Bedrock, Google Cloud, Foundry and Claude Platform on AWS.
- **When to fork.** The fork advice moved here word for word from `discovery.md`. It now has a
  reason the guide supports for not forking a skill that dispatches subagents: with fork mode off,
  those subagents start in the background, so the forked skill can return before they report.
- **The skill listing** and **the body after compaction.** It explains that whole descriptions
  are dropped (least-invoked first) when the listing overflows, and lists the knobs
  (`/skill-doctor`, `skillOverrides`, `skillListingBudgetFraction`, …). It also gives the
  5,000-token-per-body and 25,000-token total limits on what gets re-attached after compaction.

One change departs from the plan's verbatim text: the `model` bullet gained "With `context: fork`,
`model` sets the forked subagent's model instead." (`942fee0`). The guide row says so, and the
history entry records the ruling.

### Corrections to existing claims

1. **"Description is resident in every conversation"** is now "the only text loaded before the
   skill triggers, apart from the name and any `when_to_use` text, and a runtime may drop or
   shorten it" (`discovery.md` §4, `SKILL.md` step 2 of "How future agents find your skill").
2. **"`@` force-loads files, consuming 200k+ context"** is gone. The guide doesn't support it. The
   ❌ example now says "(a file path, not a skill name)", and the reason given is a portability
   one: a bare name lets each runtime load the skill its own way. A backlog item tracks the
   related `@`-path fact that the guide is missing.
3. **Directory examples** in `SKILL.md` now show `references/` and `scripts/` instead of loose
   files.
4. **The optional-key list** in `discovery.md` is now a plain list plus the lint rule (a Haiku
   `model` fails), with a pointer to `claude-code.md` for what the keys do.

### Pointers (these change agent behaviour, so they were tested)

- In `SKILL.md`, after the discovery.md pointer: read `claude-code.md` before you set a key only
  Claude Code reads, or when the skill will run in Claude Code.
- In `discovery.md`: a pointer at the end of the key bullet, and one in §4 for Claude Code's
  listing rule.

**Not added:** a "Hard Rules slot after Overview" in the body template. The plan added it only if
the RED control showed agents burying a hard rule below a long table. They didn't (see below).

## Register changes (`conformance.toml`)

- **`writing-skills-guide-gaps` (gap) is removed.** Its parts were the listing budget,
  critical-rules-first and `@` loading. The first and third are fixed by the text changes above.
  Critical-rules-first closed on the null RED result (plan decision D5).
- **`writing-skills-tdd-for-docs` (deviation)** has a new reason, evidence and revisit trigger.
  The departure is now described as narrow: the guide already keeps TDD for behaviour changes, and
  writing-skills goes further only on edits that change no instruction (typos, links, verbatim
  moves). In practice you waive those case by case (`7bb8810`). The final review removed a phrase
  ("for such edits") that went beyond the spec's wording (`40f5bf3`).
- **`description-when-only`** now also lists `skills/writing-skills/references/discovery.md` in
  `artifacts`. You approved this at the completion gate. It registers row 38 of the review, where
  discovery.md repeats the trigger-only description rule, as the known deviation. Without it, the
  next `/cc-guide files` pass would report the rule as unregistered.

## Evidence: the micro-tests

Record: `specs/baseline/red-baseline-writing-skills-guide.md`. The kit and rules were committed at
`d1aaba9`/`b897a61`, before any rep ran. The kit runs `claude -p` with no tools, no setting
sources and `--disable-slash-commands`, from a temporary directory outside any git repository.

| Arm | Layout | What it asks | Result |
|---|---|---|---|
| `red` (R1) | base `3684b96` | Does an agent writing a new skill put a hard rule after a long table? | **0/5 FAIL on Opus and on Sonnet, so the outcome is null.** No new instruction was added, and `green` didn't run. |
| `desc` (P1a–P3a) | base | Descriptive control on Opus, no bar | P1a 5/5, P2a 5/5, **P3a 0/5** |
| `read` (P1r–P3r) | new `942fee0` | Does the agent go to `claude-code.md`? | 5/5 on every prompt and model (bar 4/5) |
| `apply` (P1a–P3a) | new | Does the agent use the fact? | 5/5 on every prompt and model (bar 4/5) |

Total spend was **$3.43 of the $30 cap** (85 reps plus a pilot).

The record states these limits itself, and you should weigh them:

- All 30 `read` passes came from the **no-edit clause**: no rep went as far as an edit, so
  "read before editing" is untested. The rep only shows that the agent's first action is to read
  the file.
- The `apply` prompts include `claude-code.md` as already read, so they test whether the agent
  uses a fact, not the whole read-then-use chain.
- **P1a and P2a pass on the old layout too**, under loose readings of rule (a) that `c0756d0`
  names. So only **P3a** (the fork/background-subagents reason) separates the new layout from the
  old one: 0/5 against 5/5 on Opus. That comparison is descriptive, 5 reps on one model.
- The related backlog item ("writing-skills reference reads untested") stays open, with this
  noted.

## Review against the guide

The same record holds a 56-row table that checks `SKILL.md` and its seven on-demand files against
the guide. Rows 42 and 47 were contradicted and are fixed. Row 5 and row 38 are covered by the
registered deviation. Three rows were flagged for you and **left unchanged**:

- **Row 41:** `discovery.md:79` says descriptions are "injected into system prompt". The guide
  doesn't say where the listing sits.
- **Row 48:** `discovery.md:153` says subagents save "50 to 100×" context. The guide gives no
  factor.
- **Row 56:** `CLAUDE_MD_TESTING.md` puts skills in category folders under `~/.claude/skills/`.
  The guide documents only `<name>/`.

The completion notes don't say how you ruled on these three, and none of them has a backlog item.
**Decide whether they need one.**

## Backlog changes (`specs/deferred_items.md`)

**Closed:** the distilled `references/` file (conformance Decision 10), the review of the 41
files the drift sweep stamped stale (this was the last one), and the "split and rewrite
writing-skills" item.

**Opened (5):**
1. The guide omits that `@` paths in a local skill body are attached, but not in a skill synced
   from claude.ai.
2. `packets.py files()` leaves a SKILL.md's on-demand files out of `/cc-guide files` packets.
3. The kit's isolation pilot has no question about user identity (see the privacy note below).
4. `claude-code.md` doesn't say that a forked skill runs in the background by default in
   interactive sessions.
5. `extract_structure.py` drops a numbered contents line that has a page but no title, and
   `check_complete` still passes. This was found by Codex in review of PR #184 code, not plan 92
   code.

## Things to check before merging

- **Your name is in a committed test output.**
  `specs/baseline/red-baseline-writing-skills-guide/new/P1a-sonnet/rep5.json` begins its reply
  with your first name. The account identity reached a run that was meant to be isolated (backlog
  item 3). The name already appears in `NOTICE`/frontmatter as `adapted_by`, so this may not
  matter to you. All 85 `rep*.json` files also contain Claude Code `session_id`s and costs. No home
  paths or email addresses appear (I grepped for them). If the repo is public and you'd rather not
  ship these, redact them before merging.
- **The micro-test evidence for the pointers is thinner than the 5/5 tables suggest.** See the
  limits above. The facts themselves are factual edits checked against the guide, and they don't
  rest on the tests.
- **Rows 41, 48 and 56** are unresolved, with no backlog item.

## Verification I ran on `0b6d34f`

- `uv run python build/check_links.py`: `231 relative link(s) checked, 0 broken` (the count the
  plan expected).
- `uv run python build/cc_guide/cli.py lint`: exit 0, **no `STALE` lines**.
- `bash build/run_commit_lints.sh`: `commit lints passed`.

I didn't rerun any micro-test reps. The results above are as the branch records them.
