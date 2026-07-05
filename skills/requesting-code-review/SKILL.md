---
name: requesting-code-review
description: >
  Use when completed work needs a code review — after finishing a task or major feature, before
  merging a branch or opening a PR, when reviewing a commit range (BASE..HEAD) against its plan
  or requirements, when stuck and wanting a fresh pass on recent commits, or after fixing a
  complex bug.
---

# Requesting Code Review

Dispatch a code reviewer subagent to catch issues before they cascade. The reviewer gets precisely crafted context for evaluation — never your session's history. This keeps the reviewer focused on the work product, not your thought process, and preserves your own context for continued work.

**Core principle:** Review early, review often.

## When to Request Review

**Mandatory:**
- The final whole-branch review in subagent-driven development (per-task reviews there use subagent-driven-development's own task-reviewer-prompt.md)
- After completing major feature
- Before merge to main

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
model silently inherits your session's model, usually the most capable and most
expensive.

**Placeholders:**
- `[DESCRIPTION]` - Brief summary of what you built
- `[PLAN_OR_REQUIREMENTS]` - What it should do
- `[BASE_SHA]` - Starting commit
- `[HEAD_SHA]` - Ending commit
- `[DIFF_FILE]` - Review-package path (from subagent-driven-development's `scripts/review-package BASE HEAD`); required when dispatched from that skill, optional otherwise

**3. Act on feedback:**
- Fix Critical issues immediately
- Fix Important issues before proceeding
- Note Minor issues for later
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
    Important: Missing progress indicators
    Minor: Magic number (100) for reporting interval
  Assessment: Ready to proceed

You: [Fix progress indicators]
[Continue to Task 3]
```

## Integration with Workflows

**Subagent-Driven Development:**
- This template serves the FINAL whole-branch review only
- Per-task reviews use subagent-driven-development's task-reviewer-prompt.md (task-scoped gate)

**Executing Plans:**
- Review after each task or at natural checkpoints
- Get feedback, apply, continue

**Ad-Hoc Development:**
- Review before merge
- Review when stuck

## Red Flags

**Never:**
- Skip review because "it's simple"
- Ignore Critical issues
- Proceed with unfixed Important issues
- Argue with valid technical feedback

**If reviewer wrong:**
- Push back with technical reasoning
- Show code/tests that prove it works
- Request clarification

When the review comes back, process the findings with the receiving-code-review skill — verify before implementing.
