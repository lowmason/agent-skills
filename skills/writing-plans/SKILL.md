---
name: writing-plans
description: >
  Use when you have a spec, design doc, or requirements for a multi-step task and need an
  implementation plan before touching code — "write a plan", "plan this feature", "break this
  into tasks", a finished spec in specs/ awaiting its plan, or before handing work to subagents
  or a separate execution session.
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Context:** If working in an isolated worktree, it should have been created via the `using-git-worktrees` skill at execution time.

**Save plans to:** `specs/plans/<id>-<spec-name>.md` — `<id>` is the next integer (check `specs/plans/` and `specs/plans/completed/`, take the highest existing `<id>` + 1); `<spec-name>` matches the spec the plan implements. When the plan is fully executed, run the Plan Completion Protocol (below).
- (User preferences for plan location override this default)

## Scope Check

If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during design. If it wasn't, suggest breaking this into separate plans — one per subsystem. Each plan should produce working, testable software on its own.

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- You reason best about code you can hold in context at once, and your edits are more reliable when files are focused. Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large files, don't unilaterally restructure - but if a file you're modifying has grown unwieldy, including a split in the plan is reasonable.

This structure informs the task decomposition. Each task should produce self-contained changes that make sense independently.

## Task Right-Sizing

A task is the smallest unit that carries its own test cycle and is worth a
fresh reviewer's gate. When drawing task boundaries: fold setup,
configuration, scaffolding, and documentation steps into the task whose
deliverable needs them; split only where a reviewer could meaningfully
reject one task while approving its neighbor. Each task ends with an
independently testable deliverable.

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

## Global Constraints

[The spec's project-wide requirements — version floors, dependency limits,
naming and copy rules, platform requirements — one line each, with exact
values copied verbatim from the spec. Every task's requirements implicitly
include this section.]

---
```

## Task Structure

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Interfaces:**
- Consumes: [what this task uses from earlier tasks — exact signatures]
- Produces: [what later tasks rely on — exact function names, parameter
  and return types. A task's implementer sees only their own task; this
  block is how they learn the names and types neighboring tasks use.]

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## No Placeholders

Every step must contain the actual content an engineer needs. These are **plan failures** — never write them:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code — the engineer may be reading tasks out of order)
- Steps that describe what to do without showing how (code blocks required for code steps)
- References to types, functions, or methods not defined in any task

## Remember
- Exact file paths always
- Complete code in every step — if a step changes code, show the code
- Exact commands with expected output
- DRY, YAGNI, TDD, frequent commits

## Self-Review

After writing the complete plan, look at the spec with fresh eyes and check the plan against it. This is a checklist you run yourself — not a subagent dispatch.

**1. Spec coverage:** Skim each section/requirement in the spec. Can you point to a task that implements it? List any gaps.

**2. Placeholder scan:** Search your plan for red flags — any of the patterns from the "No Placeholders" section above. Fix them.

**3. Type consistency:** Do the types, method signatures, and property names you used in later tasks match what you defined in earlier tasks? A function called `clearLayers()` in Task 3 but `clearFullLayers()` in Task 7 is a bug.

If you find issues, fix them inline. No need to re-review — just fix and move on. If you find a spec requirement with no task, add the task.

## Execution Handoff

After saving the plan, offer execution choice:

**"Plan complete and saved to `specs/plans/<id>-<spec-name>.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session, in plan order, with a checkpoint at each milestone

**Which approach?"**

**If Subagent-Driven chosen:**
- **REQUIRED SUB-SKILL:** Use subagent-driven-development
- Fresh subagent per task + two-stage review

**If Inline Execution chosen:**
- Execute the tasks in order, pausing at each milestone for review (per your CLAUDE.md engineering-discipline rules)
- Batch execution with checkpoints for review

## Plan Completion Protocol

Run this after every task is done and the final review is resolved — before
finishing-a-development-branch. The gate comes first; markup is written only
once the completed/deferred partition is final.

**1. Resolve-before-defer gate.** Collect the leftovers: plan steps skipped
or descoped during execution, plus review findings that were not fixed.
Partition:
- Stalled because it needed your human partner's input → ask now, as one
  batched set of questions.
- Unblocked by an answer → implement it now (the protocol restarts after
  that work lands).
- Everything else → defer.

**2. Markup the plan file.** Tick every completed step (`- [x]`). Under any
step that deviated from the plan, add a one-line `> Deviation: …` note.
Annotate skipped steps with `> Skipped: <why> → deferred`. Add a status
header at the top of the plan:
`**Status: COMPLETE (YYYY-MM-DD)** — executed via <skill>; deferred items in specs/deferred_items.md`
— or, when the gate deferred nothing:
`**Status: COMPLETE (YYYY-MM-DD)** — executed via <skill>; nothing deferred`
Markup happens once, after the gate resolves — per-task progress tracking
stays in your todo list or ledger.

**3. Append deferred items** to `specs/deferred_items.md`, one section per
plan, newest last. Create the file on first use with a single
`# Deferred items` title line, no other preamble. Skip this step entirely
when nothing was deferred — never append an empty section. Each item is
self-contained: file paths, why it was deferred, what it would take to do.

```markdown
## 7-rate-limiter — 2026-07-04
- [ ] Redis-backed counter store (plan Task 4, skipped): needs prod Redis
      DSN decision. See specs/plans/completed/7-rate-limiter.md; touches
      src/limiter/store.py.
- [ ] Review Minor: retry jitter is fixed-seed in tests only (reviewer
      report, triaged defer).
```

When a later plan implements an item, tick its box with a pointer
(`- [x] … → done in plan 12`). Never delete items — the file doubles as a
history of consciously-deferred work.

**4. Retire.** `git mv` the plan to `specs/plans/completed/`, in one
`chore(specs): retire plan <id>` commit. Retire the spec to
`specs/completed/` (marked complete at top) in the same commit **only if**
the spec file exists and no other live plan in `specs/plans/` implements it
(match by the `<spec-name>` suffix in plan filenames). Spec-less plans and
shared specs leave the spec untouched.

These commits land on the current branch as its final commits — a merge or
PR carries them atomically; a discarded branch takes its completion markup
with it.
