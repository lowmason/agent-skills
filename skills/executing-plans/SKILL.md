---
name: executing-plans
description: >
  Use when you have a written implementation plan to execute yourself, task by task, in the
  current session — e.g. a plan file from writing-plans in specs/plans/ — because tasks are
  tightly coupled or your human partner asked for direct execution rather than subagent dispatch
---

# Executing Plans

## Overview

Load plan, review critically, execute all tasks, report when complete.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

**Note:** If subagents are available AND the tasks are mostly independent AND your human partner didn't ask for direct execution, use the subagent-driven-development skill instead — fresh per-task subagents with review gates produce significantly higher quality. This skill is the right choice for tightly coupled plans, partner-requested direct execution, or platforms without subagent support.

## The Process

### Step 1: Load and Review Plan
1. Read plan file
2. Review critically - identify any questions or concerns about the plan
3. If concerns: Raise them with your human partner before starting
4. If no concerns: Create todos for the plan items and proceed
5. Executing on the base branch itself (only with your partner's explicit
   consent)? Record `git rev-parse --short HEAD` in the conversation before
   Task 1 — Step 3's review starts there, because on the base branch there
   is no merge base to compute. Two things break that record: losing it to
   a `/clear`, and a pull or rebase of the base branch since, which brings
   upstream commits into the range. Either way, ask your partner which
   commit the plan's work starts *after* — the review excludes the commit it
   starts from — rather than guessing. If the plan file is committed,
   offer the commit that added it as a candidate —
   `git log --follow --diff-filter=A --format=%h -- <plan-file> | tail -n 1`
   — but let them confirm it: nothing guarantees it predates every task.

### Step 2: Execute Tasks

For each task:
1. Mark as in_progress
2. Follow each step exactly (plan has bite-sized steps)
3. Run verifications as specified
4. Mark as completed

### Step 3: Review the Whole Plan

After the last task is verified, review the whole branch with two reviewers,
launched in the same message so they run concurrently. Compute one BASE for
both, now: `git merge-base <base-branch> HEAD`. On a branch cut for this plan
that is where the plan began; on a branch that already carried work, the
review covers that work too — as subagent-driven-development's final review
does, and as finishing-a-development-branch relies on. Computing it at review
time, rather than recording it earlier, also survives a `/clear` and a rebase
onto a newer base branch. On the base branch itself that command returns HEAD
— an empty range — so use the start Step 1 had you record, or the one your
partner confirmed.

1. **code-reviewer** — fill requesting-code-review's
   [code-reviewer.md](../requesting-code-review/code-reviewer.md) with the plan
   file as `[PLAN_OR_REQUIREMENTS]`, BASE as `[BASE_SHA]`, and the capable
   model tier (opus), as for any final whole-branch review. On a platform
   without subagents, work through the same template yourself.
2. **Codex** — the second-opinion review in
   [codex-review.md](../requesting-code-review/codex-review.md), with
   `--base <BASE>`.

Touch nothing until both have returned. Then merge the two lists into one, work
it with the receiving-code-review skill, fix what holds up, re-run the plan's
tests, and commit the fixes — the plan-completion protocol commits only
`specs/`, and the branch ships as committed. Findings you leave unfixed carry
into Step 4, where they feed the resolve-before-defer gate.

### Step 4: Complete the Plan

After the review resolves, run the plan-completion protocol
from the writing-plans skill (its "Plan Completion Protocol" section):
resolve-before-defer gate → plan markup → deferred items → retire the plan
and (conditionally) its spec.

### Step 5: Complete Development

Once the plan is complete and retired:
- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use finishing-a-development-branch
- Follow that skill to verify tests, present options, execute choice

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember
- Review plan critically first
- Follow plan steps exactly
- Don't skip verifications
- Review the whole plan — code-reviewer plus Codex — before completing it
- Reference skills when plan says to
- Stop when blocked, don't guess
- Never start implementation on main/master branch without explicit user consent

## Integration

**Required workflow skills:**
- **using-git-worktrees** - Ensures isolated workspace (creates one or verifies existing)
- **writing-plans** - Creates the plan this skill executes
- **requesting-code-review** - code-reviewer template and Codex second-opinion recipe for the whole-plan review
- **receiving-code-review** - Works the merged findings before anything is fixed
- **finishing-a-development-branch** - Complete development after all tasks
