# Example workflow

One worked pass through the per-task loop in SKILL.md § The Process: a
NEEDS_CONTEXT round-trip on Task 1, and a failed spec review with a fix round
and a scoped re-review on Task 2. Illustration only — the procedure it
illustrates is normative in SKILL.md, not here.

```
You: I'm using Subagent-Driven Development to execute this plan.

[Read plan file once: specs/plans/7-feature-name.md]
[Create todos for all tasks]

Task 1: Hook installation script

[Run task-brief for Task 1; dispatch implementer with brief + report paths + context]

Implementer (final message): NEEDS_CONTEXT — "Should the hook be installed
  at user or system level?"

You: [Re-dispatch the implementer with the same brief plus: "User level (~/.claude/hooks/)"]

Implementer (second run):
  - Implemented install-hook command
  - Added tests, 5/5 passing
  - Self-review: Found I missed --force flag, added it
  - Committed

[Run review-package, dispatch task reviewer with the path it reports]
Task reviewer: Spec ✅ - all requirements met, nothing extra.
  Strengths: Good test coverage, clean. Issues: None. Task quality: Approved.

[Mark Task 1 complete]

Task 2: Recovery modes

[Run task-brief for Task 2; dispatch implementer with brief + report paths + context]

Implementer: [No questions, proceeds]
Implementer:
  - Added verify/repair modes
  - 8/8 tests passing
  - Self-review: All good
  - Committed

[Run review-package, dispatch task reviewer with the path it reports]
Task reviewer: Spec ❌:
  - Missing: Progress reporting (spec says "report every 100 items")
  - Extra: Added --json flag (not requested)
  Issues (Important): Magic number (100)

[Fix round 1: resume the same implementer with all findings]
Implementer (resumed): Removed --json flag, added progress reporting,
  extracted PROGRESS_INTERVAL constant

[Dispatch scoped re-review (re-review-prompt.md) with the numbered findings]
Re-reviewer:
  1. Missing progress reporting — ADDRESSED (reports every PROGRESS_INTERVAL items)
  2. Extra --json flag — ADDRESSED (removed)
  3. Magic number (100) — ADDRESSED (extracted to PROGRESS_INTERVAL)
  No new findings.

[Mark Task 2 complete]

...

[After all tasks]
[Dispatch final code-reviewer]
Final reviewer: All requirements met, ready to merge

Done!
```
