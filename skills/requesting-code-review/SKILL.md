---
name: requesting-code-review
description: >
  Use when completed work needs a code review — after finishing a task or major feature, before
  merging a branch or opening a PR, when reviewing a commit range (BASE..HEAD) against its plan
  or requirements, when stuck and wanting a fresh pass on recent commits, or after fixing a
  complex bug.
license: MIT
metadata:
  author: 'Jesse Vincent'
  adapted_by: 'Lowell Mason'
  source: 'https://github.com/obra/superpowers'
# cc-guide: subagents.frontmatter subagents.models subagents.isolation @2.1.306
---

# Requesting Code Review

Dispatch a code reviewer subagent to catch issues before they cascade. The reviewer gets precisely crafted context for evaluation — never your session's history. This keeps the reviewer focused on the work product, not your thought process, and preserves your own context for continued work.

**Core principle:** Review early, review often.

## When to Request Review

**Mandatory:**
- The final whole-branch review in subagent-driven development (per-task reviews there use subagent-driven-development's own task-reviewer-prompt.md), and the whole-plan review in executing-plans — both pair this reviewer with a Codex second opinion ([codex-review.md](codex-review.md))
  - The Codex run sends the diff, and every file Codex reads, to OpenAI. Run it when your human partner has approved Codex review for this repository: in this session, in the request, or in the repo's CLAUDE.md. Otherwise ask once per session before the first run. If they decline, say in the review report that the Codex seat was skipped at their word, write no `Codex reviewed` line, and go on with this reviewer.
- After completing major feature
- Before merge to main, except for a small change your human partner watched being made in this session and told you to merge without review. Subagent-written work and a plan's final review never qualify. The waiver covers the code-reviewer pass only: the Codex second-opinion gate at merge or PR (see Integration with Workflows) still applies.

**Optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing complex bug

## How to Request

**1. Get git SHAs:**
```bash
BASE_SHA=<the BASE you recorded before the work began>   # whole branch: $(git merge-base main HEAD)
HEAD_SHA=$(git rev-parse HEAD)
# Never HEAD~1 — it silently drops all but the last commit of a multi-commit change.
```

**2. Dispatch code reviewer subagent:**

Dispatch a `code-reviewer` subagent if that agent type is defined in your
environment (it carries no edit tools and operates under an explicit
read-only contract); otherwise dispatch `general-purpose`. Either way, fill
the template at [code-reviewer.md](code-reviewer.md).

**Set its model explicitly.** Choose the tier per subagent-driven-development's
Model Selection: a small mechanical diff reviews at **standard**; a subtle or
risky change — and the final whole-branch review — at **capable**. An omitted
model is never a tier choice: on Claude Code a defined `code-reviewer` runs at
its pin whatever the diff, and `general-purpose`, like every agent on Codex and
Gemini, inherits your session's model — usually the most capable and most
expensive.

**Placeholders:**
- `[DESCRIPTION]` - Brief summary of what you built
- `[PLAN_OR_REQUIREMENTS]` - What it should do
- `[BASE_SHA]` - Starting commit
- `[HEAD_SHA]` - Ending commit
- `[DIFF_FILE]` - Review-package path (from subagent-driven-development's `scripts/review-package PLAN_FILE BASE HEAD`); required when dispatched from that skill, optional otherwise

**3. Act on feedback:**
- Fix Critical issues immediately
- Fix Important issues before proceeding
- Rule on each Declined to judge line: make it a finding, or record why it stays out
- Push back if reviewer is wrong (with reasoning)

## Example

```
[Just completed Task 2: Add verification function]

You: Let me request code review before proceeding.

BASE_SHA=<recorded before Task 2 began>  # e.g. a7981ec
HEAD_SHA=$(git rev-parse HEAD)

[Dispatch code reviewer subagent]
  DESCRIPTION: Added verifyIndex() and repairIndex() with 4 issue types
  PLAN_OR_REQUIREMENTS: Task 2 from specs/plans/7-deployment.md
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661

[Subagent returns]:
  Strengths: Clean architecture, real tests
  Issues:
    Important: repairIndex() reports success when a repair fails
  Declined to judge:
    Repair of indexes written before v2: Task 2 covers new indexes only
  Assessment: Ready to proceed

You: [Fix the false success report; rule that pre-v2 repair stays out of scope]
[Continue to Task 3]
```

## Integration with Workflows

**Subagent-Driven Development:**
- This template serves the FINAL whole-branch review only, beside a concurrent Codex second opinion ([codex-review.md](codex-review.md))
- Per-task reviews use subagent-driven-development's task-reviewer-prompt.md (task-scoped gate)

**Executing Plans:**
- Whole-plan review once every task is verified: this template plus a concurrent Codex second opinion, before the plan-completion protocol
- Optional reviews at natural checkpoints before that

**Finishing a Development Branch:**
- A Codex second opinion gates merge and PR — skipped when Codex already reviewed the same code

**Ad-Hoc Development:**
- Review before merge (except the watched small change under **Mandatory**, which still meets the Codex gate at merge or PR)
- Review when stuck

## Red Flags

**Never:**
- Skip review because "it's simple" (the one skip is the watched small change under **Mandatory**, on your partner's word, and the Codex gate at merge or PR still applies)
- Ignore Critical issues
- Proceed with unfixed Important issues
- Argue with valid technical feedback

**If reviewer wrong:**
- Push back with technical reasoning
- Show code/tests that prove it works
- Request clarification

When the review comes back, process the findings with the receiving-code-review skill — verify before implementing.
