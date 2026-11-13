# Claude Code facts for skill authors

Read this before you set a frontmatter key that only Claude Code reads, or when the skill will
run in Claude Code. Each fact here holds for Claude Code and can change between its versions.
Advice that holds on every runtime stays in [SKILL.md](../SKILL.md) and
[discovery.md](discovery.md).

## Frontmatter keys

Claude Code reads these keys beyond the Agent Skills spec's own:

- `when_to_use`: more trigger text. Claude Code appends it to the description, and the two share
  one entry in the skill listing and that entry's length cap.
- `model` and `effort`: the model for the rest of the turn in which the skill runs, and the
  reasoning effort while the skill is active. With `context: fork`, `model` sets the forked
  subagent's model instead.
- `context: fork`: Claude Code runs the body in an isolated subagent that does not see the
  conversation, so the body must stand alone. Only the subagent's final text comes back.
- `agent`: the agent type that runs a forked skill. The default is `general-purpose`.
- `disable-model-invocation: true`: Claude never starts the skill on its own, and the skill leaves
  the skill listing. Typing `/name` at the start of a message runs it. A subagent cannot preload
  the skill through its `skills` field.

Claude Code ignores an unknown or misspelled key and reports no error.

### A Haiku `model`

In auto mode, Claude Code ignores a skill `model` that auto mode does not support, Haiku 4.5 and
earlier among them, and the session model runs. The `haiku` alias means Haiku 5.5 on the
Anthropic API, but Haiku 4.5 on Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry
and Claude Platform on AWS. So a skill's `model: haiku` applies on one provider and is ignored on
another.

### When to fork

Fork a skill whose value is a **verdict or artifact** you act on (`tech-debt` returns a prioritized backlog). Do **not** fork a skill whose value is **guidance** — it has to stay resident to shape what the main thread writes next — nor one that dispatches subagents itself, nor one with a mix of artifact and question-answering operations, since `context` is all-or-nothing per skill.

The reason not to fork a skill that dispatches subagents: with fork mode off
(`CLAUDE_CODE_FORK_SUBAGENT=0`), the subagents that a subagent starts in `claude -p` and the
Agent SDK start in the background. So a forked skill can return before its own subagents report.
Fork mode is on by default.

## The skill listing

Before any skill triggers, Claude Code loads a listing of skill names and descriptions, within a
budget. Every name stays listed. When the descriptions overflow the budget, Claude Code drops
whole descriptions, not parts of them, starting with the skills invoked least. A skill whose
description was dropped still runs by name, but it rarely triggers on its own.

- `/doctor` estimates what the listing costs, `/skill-doctor` shows each skill's cost and use,
  and the Skills row of `/context` shows the listing's size after the budget.
- `disable-model-invocation: true` takes a skill out of the listing.
- `skillOverrides` in settings lists a skill by name only, hides it from Claude, or turns it off.
  It does not reach plugin skills.
- `skillListingBudgetFraction` raises the budget, `SLASH_COMMAND_TOOL_CHAR_BUDGET` sets it as a
  fixed character count, and `skillListingMaxDescChars` sets each entry's length cap.
- A plugin's whole skill set joins the listing, so disabling an unused plugin frees room.

## The body after compaction

An invoked SKILL.md body stays in the conversation for the rest of the session. After compaction,
Claude Code re-attaches the most recent invocation of each skill and keeps the first 5,000 tokens
of each body. The re-attached bodies share a 25,000-token budget, filled newest first. Text past a
body's first 5,000 tokens is gone after compaction, and an older skill can drop out entirely.
