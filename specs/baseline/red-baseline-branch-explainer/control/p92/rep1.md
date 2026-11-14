# What `e382493..HEAD` changes (plan 92: writing-skills against the Claude Code guide)

## In short

This branch carries out plan 92. The plan checks the **writing-skills** skill against the repo's
Claude Code guide. It does four things:

1. It moves the skill's Claude Code facts into one new file,
   `skills/writing-skills/references/claude-code.md`.
2. It fixes several wrong or unsupported claims in `SKILL.md` and `references/discovery.md`.
3. It updates the conformance register, the drift baseline, `NOTICE` and the backlog to match.
4. It commits a micro-test record and its raw outputs as evidence.

This closes three backlog items. One of them is the last STALE file in the drift backlog, so
`cli.py lint` now prints nothing. The branch also files five new backlog items.

Size: 115 files, about 8,600 lines added. Almost all of that is test data under
`specs/baseline/red-baseline-writing-skills-guide/`. The skill text itself changes by about 100
lines.

## The commits, in order

| Commit | What it does |
|---|---|
| `d1aaba9` | Logs D13, your go-ahead to run plan 92 |
| `b897a61` | Registers the micro-test rules and the kit before any rep runs |
| `f88f36a`, `c0756d0` | RED control and descriptive arm on the old layout, plus the readings used to score `P1a` and `P2a` |
| `e183c73` | **The main change:** adds `claude-code.md` and edits `SKILL.md`, `discovery.md`, the register and `NOTICE` |
| `942fee0` | Adds the forked-skill case to the `model` key (this commit is the text the tests ran against) |
| `2207cc5` | Micro-test results on the new layout |
| `3d0d226`, `b76c2a3` | Review against the guide (56 rows), restamp the citation, finish the `when_to_use` qualifier |
| `40f5bf3` | Restores the approved spec's wording of the `tdd-for-docs` reason |
| `d7811de` | Adds `discovery.md` to the `description-when-only` deviation (your ruling at the completion gate) |
| `c3ee180`, `cecc5dc`, `f17319a` | Marks the plan complete, merges `origin/main`, moves the plan and spec to `completed/` |
| `0b6d34f` | Files a Codex finding about `build/extract_structure.py` as a backlog item |

## The skill changes

### New file: `skills/writing-skills/references/claude-code.md` (64 lines)

The rule for this file: a sentence goes here when it is true only for Claude Code and could change
between versions. The file has four parts:

- **Frontmatter keys.** What `when_to_use`, `model`, `effort`, `context: fork`, `agent` and
  `disable-model-invocation` do. It also says that Claude Code ignores unknown keys without an error.
- **A Haiku `model`.** Auto mode ignores Haiku 4.5 and earlier. The `haiku` alias means 5.5 on the
  Anthropic API but 4.5 on Amazon Bedrock, Google Cloud, Microsoft Foundry and Claude Platform on AWS, so it is not portable.
- **When to fork.** This advice moved here from `discovery.md`. It has a new reason for not forking
  a skill that starts its own subagents: when fork mode is off, those subagents start in the
  background in `claude -p` and the SDK, so the forked skill can return before they report. The old
  reason was "a subagent can't start subagents".
- **The skill listing and compaction.** Every name stays listed. When the listing goes over budget,
  whole descriptions are dropped, starting with the least-used skills. The file lists the commands
  and settings that show or change this. After compaction, Claude Code keeps the first 5,000 tokens
  of each skill body, with 25,000 tokens shared across skills, filled newest first.

### `SKILL.md`

- The citation now also names `subagents.frontmatter` and `subagents.models`, and it is restamped
  from `@2.1.219` to `@2.1.306`.
- A new pointer under "SKILL.md Structure" says to read `claude-code.md` before setting a key that
  only Claude Code reads, or when the skill will run in Claude Code.
- The directory examples now show `references/` and `scripts/`, which is the layout the repo
  actually ships, instead of loose `supporting-file.*` and `pptxgenjs.md` files.
- The skill listing is no longer called "always-loaded". It is now "loaded before any skill
  triggers", and the text adds that an overfull listing can lose descriptions.

### `references/discovery.md`

- The frontmatter bullet now lists only what the lint accepts. The meaning of each key moved to
  `claude-code.md`. The text also says plainly that a Haiku `model` fails the lint.
- Token Efficiency no longer says a description is "resident in EVERY conversation". It says the
  description, along with the name and any `when_to_use` text, is the only part of a skill that
  loads before the skill triggers, and that a runtime may drop or shorten it.
- The rule against `@` links stays. Its reason changes from "force-loads files … 200k+ context",
  which no guide section supports, to "a bare skill name lets each runtime load the skill through
  its own mechanism".

**Behaviour that stays the same:** the Iron Law, the "Use when…" trigger-only description rule and
every other discipline rule. The spec ruled these out of scope (non-goals).

## Register, baseline and NOTICE

- `build/cc_guide/conformance.toml`:
  - Gap `writing-skills-guide-gaps` is **removed**. Its three parts each closed:
    - listing budget: corrected in the text
    - `@` loading: the unsupported claim is gone
    - critical rules first: closed by the null RED result, described below
  - Deviation `writing-skills-tdd-for-docs` **stays, with a narrower reason**. The guide already
    keeps TDD for behaviour changes. The real difference is that the Iron Law also covers edits that
    change no instruction, such as a typo fix. In practice you waive the micro-test case by case.
    There is a new revisit trigger.
  - `description-when-only` now also lists `skills/writing-skills/references/discovery.md`. This
    was your ruling on review row 38.
- `build/cc_guide/baseline.json` gains the eight section hashes for the new citation.
- `NOTICE` gets an entry under the superpowers changes. It describes the new file, says that it
  departs from upstream v7.0.1's `references/` layout, and states that no upstream text was taken.

## The evidence (micro-tests)

The record is in `specs/baseline/red-baseline-writing-skills-guide.md`. The kit and raw JSON are
under `specs/baseline/red-baseline-writing-skills-guide/`. Each rep is a fresh `claude -p` with no
tools. The rules were registered before any rep ran.

- **RED (`R1`, old layout):** this tests whether an author puts a hard rule before a large table,
  so the rule falls inside the window that survives compaction. Result: 0 of 5 failures on Opus and
  0 of 5 on Sonnet, a **null** result. So no new "put critical rules first" instruction was added.
  `claude-code.md` states only the mechanism, and the GREEN arm did not run.
- **New layout (`942fee0`):** every bar was met at 5 of 5 on both models, for the read arm
  (`P1r`–`P3r`) and the apply arm (`P1a`–`P3a`).
- **Limits the record names itself:**
  - All 30 read-arm passes came from the "no edit yet" clause. That shows agents follow the pointer
    to `claude-code.md`. It does not show that they read the file *before* an edit.
  - The apply prompts give the agent the reference text as already read. They test whether the
    agent uses a fact, not the full read-then-use chain.
  - `P1a` and `P2a` also passed 5 of 5 on the **old** layout, under loose readings. Under the
    stricter readings, all of those reps fail. So these two prompts do not tell the layouts apart.
  - Only `P3a`, the fork reason, separates the layouts: 0 of 5 on the old layout against 5 of 5 on
    the new one, on Opus.
- Spend: $3.43 of a $30 cap.

## Checks I ran on HEAD

| Check | Result |
|---|---|
| `uv run --with pyyaml python build/check_conformance.py` | exit 0, no output |
| `uv run --with pyyaml python build/check_frontmatter.py` | exit 0 |
| `uv run python build/cc_guide/cli.py lint` | exit 0, no `STALE` lines |

Without `--with pyyaml`, the first two scripts fail with `ModuleNotFoundError: yaml`. That is my
environment, not this branch. I did not run the `build/` pytest suites.

## Things to look at before you merge

1. **Your surname is in a committed test output.**
   `specs/baseline/red-baseline-writing-skills-guide/new/P1a-sonnet/rep5.json` contains a reply
   that addresses you by surname ("Mason, the two requirements conflict…"). The branch knows this:
   it filed it as a backlog item, because the isolation probe never asks about identity. But the
   file itself is still committed. If you don't want your name in the repo's test data, redact that
   rep before you merge. No verdict depended on that wording. I found no other name and no
   `/Users/` paths in the test data.
2. **Three owner rows have no recorded ruling.** The review lists four "rows for the owner". Row 38
   got your ruling (`d7811de`). Rows 41, 48 and 56 appear only in the baseline record, and nothing
   in the backlog, plan or history tracks them:
   - Row 41: "injected into system prompt" as the reason for writing descriptions in the third
     person.
   - Row 48: "subagents save 50 to 100 times the context".
   - Row 56: category folders under `~/.claude/skills/` in `CLAUDE_MD_TESTING.md`.

   Decide whether to rule on them now or file them as backlog items.
3. **The read-before-edit claim is still untested.** That is honest in the record, and the t3 item
   stays open. But the evidence that agents *use* `claude-code.md` mid-edit is weaker than the
   "every bar met" table suggests.
4. **One new backlog item is unrelated to plan 92.** The `extract_structure.py` finding (`0b6d34f`)
   is about code from PR #184, which is already on main. It is only filed here, not fixed.
5. **Other new backlog items (filed, not fixed):**
   - the guide is missing the fact about `@` paths in local vs. synced skills
   - `packets.py` leaves out a skill's on-demand files
   - `claude-code.md` does not say that a forked skill runs in the background by default in
     interactive sessions
6. **Recorded deviations from the plan.** The history entry in `specs/history.md` records four
   rulings and five deviations, all small wording or process changes. The one that changes what the
   skill says is the added clause "With `context: fork`, `model` sets the forked subagent's model
   instead."

## Verdict

The skill edits are small, follow the approved spec, and pass the repo's conformance, frontmatter
and drift checks. Only item 1 (your surname in `rep5.json`) is worth fixing before merge. Item 2
needs a decision but does not block the merge.
