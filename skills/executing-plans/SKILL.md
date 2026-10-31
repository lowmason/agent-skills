---
name: executing-plans
description: >
  Use when a written implementation plan is to be executed directly, task by task, in the current
  session — e.g. a plan file from writing-plans in specs/plans/ — because tasks are tightly
  coupled or the human partner asked for direct execution rather than subagent dispatch
license: MIT
metadata:
  author: 'Jesse Vincent'
  adapted_by: 'Lowell Mason'
  source: 'https://github.com/obra/superpowers'
# cc-guide: subagents.frontmatter @2.1.306
---

# Executing Plans

Execute the plan yourself, task by task, in this session: no implementer
subagent per task, no reviewer per task. One fresh-context review of the
whole branch at the end.

**Why inline:** Tightly coupled tasks need one context that carries each
task's work into the next; a fresh implementer and reviewer per task would
each start from zero. Inline execution keeps one context (yours) plus one
review at the end, and your human partner chose it.
What it gives up is a fresh context per task and a second pair of eyes per
task. This skill keeps what those two things bought, by other means: the
brief is the spec, the ledger is your memory, TDD is the per-task gate, and
the final reviewer is the second pair of eyes.

**Core principle:** The plan already did the thinking. Execute it exactly,
prove each step with a test you watched fail and then pass, and leave a
record that survives your own forgetting.

**Narration:** between tool calls, narrate at most one short line — the
ledger and the tool results carry the record.

**Continuous execution:** Do not pause to check in with your human partner
between tasks. They chose inline execution for one shared context across
coupled tasks, not to answer
"should I continue?" after every task. Execute all tasks from the plan
without stopping.

**Rulings, not stalls.** Conflicts, ambiguities, plan defects — decide them.
The spec is the binding authority, the plan is its argument, and your
judgment settles what neither answers. Record every decision in the ledger
as `Ruling: <what you decided> — <why> — <what it costs if wrong>`, and keep
going. Deviating from the plan without a ledgered ruling is a decision made
in secret.

Five things stop you, and only these. For them, stop and ask:

1. An irreversible or destructive operation.
2. A security-sensitive action.
3. A side effect outside this worktree that norms say you ask about first: a merge, a push to a shared branch, a publish.
4. A plan so broken that every path forward is a guess.
5. The explicit scope fence: a line in the plan (its Global Constraints, its header or a task) or in your partner's launch message that puts a file, a directory, a system or a kind of change out of bounds for this run — "Do not edit `skills/`", "No changes outside `build/`", "Do not change the public API". A ruling never crosses a fence: when the only fix crosses one, stop and ask. A task's text that contradicts a Global Constraint that is not a fence is not a stop: the constraint wins, and that is a ruling.

## When to Use

- You have a plan from writing-plans whose tasks are tightly coupled: each
  builds on the last closely enough that one continuous context serves
  them better than a fresh subagent per task.
- Your human partner asked for direct execution, at the handoff or at
  launch.
- Your harness has no subagent tool. Never fabricate a dispatch; run the
  plan here.

A fully specified plan makes inline execution transcription plus testing:
it runs well on a mid-tier session model, and the one place the most
capable model earns its cost is the final review, which this skill
dispatches separately. Tell your human partner so when they choose inline.

Prefer subagent-driven-development when your human partner
wants a review gate on every task, or when the plan is long enough that
its later tasks would run on a compacted context. Inline execution over a
long plan still works — the ledger is what makes it recoverable — but the
last tasks get the least of you.

## The Process

```dot
digraph process {
    rankdir=TB;

    subgraph cluster_per_task {
        label="Per Task";
        "task-start: brief + BASE; read the brief" [shape=box];
        "Work the steps in order: TDD, run every verification, read every output" [shape=box];
        "Step output matches plan's Expected?" [shape=diamond];
        "Plan wrong? Rule and ledger. Code wrong? systematic-debugging" [shape=box];
        "Commit as the plan's commit steps say" [shape=box];
        "Completion contract met?" [shape=diamond];
        "task-done: run tests, ledger the result; mark todo complete" [shape=box];
    }

    "Setup: worktree, workspace + ledger, read plan + spec, pre-flight scan" [shape=box];
    "More tasks remain?" [shape=diamond];
    "Final review: code-reviewer + Codex (references/final-review.md)" [shape=box];
    "ONE fix pass, each fix RED→GREEN + documented suite green; unfixed → ruling" [shape=box];
    "Plan-completion protocol, then delete this plan's workspace" [shape=box];
    "Use finishing-a-development-branch" [shape=box style=filled fillcolor=lightgreen];

    "Setup: worktree, workspace + ledger, read plan + spec, pre-flight scan" -> "task-start: brief + BASE; read the brief";
    "task-start: brief + BASE; read the brief" -> "Work the steps in order: TDD, run every verification, read every output";
    "Work the steps in order: TDD, run every verification, read every output" -> "Step output matches plan's Expected?";
    "Step output matches plan's Expected?" -> "Plan wrong? Rule and ledger. Code wrong? systematic-debugging" [label="no"];
    "Plan wrong? Rule and ledger. Code wrong? systematic-debugging" -> "Work the steps in order: TDD, run every verification, read every output";
    "Step output matches plan's Expected?" -> "Commit as the plan's commit steps say" [label="yes, last step"];
    "Commit as the plan's commit steps say" -> "Completion contract met?";
    "Completion contract met?" -> "Work the steps in order: TDD, run every verification, read every output" [label="no - finish the task"];
    "Completion contract met?" -> "task-done: run tests, ledger the result; mark todo complete" [label="yes"];
    "task-done: run tests, ledger the result; mark todo complete" -> "More tasks remain?";
    "More tasks remain?" -> "task-start: brief + BASE; read the brief" [label="yes"];
    "More tasks remain?" -> "Final review: code-reviewer + Codex (references/final-review.md)" [label="no"];
    "Final review: code-reviewer + Codex (references/final-review.md)" -> "ONE fix pass, each fix RED→GREEN + documented suite green; unfixed → ruling";
    "ONE fix pass, each fix RED→GREEN + documented suite green; unfixed → ruling" -> "Plan-completion protocol, then delete this plan's workspace";
    "Plan-completion protocol, then delete this plan's workspace" -> "Use finishing-a-development-branch";
}
```

## Setup

Ensure the work happens in an isolated workspace: use
using-git-worktrees to create one or verify the existing one.
Never start implementation on a main/master branch without your human
partner's explicit consent.

Conversation memory does not survive compaction. An inline executor that
loses its place re-implements tasks whose commits already exist — the same
failure as a controller re-dispatching them, paid for in your own context.
Track progress in a ledger file, not only in todos. Harness todos are a
live view; the ledger is the record.

The workspace and ledger are shared with subagent-driven-development
— same directory, same format — so a plan can change executors mid-flight
and the new one resumes from the same ledger.

- Each plan owns a workspace: at skill start, run
  `../subagent-driven-development/scripts/sdd-workspace PLAN_FILE` — it
  prints the plan's git-ignored directory
  (`<repo-root>/.sdd/<plan-basename>/`), home to every
  artifact for THIS plan: ledger, briefs, review packages. Another plan's
  directory is never yours to read or write.
- Check for this plan's ledger at `<workspace>/progress.md`. If its first
  line names your plan file, tasks with a `Task <N>: complete` line are
  DONE — do not redo them; resume at the first task without one. On
  resume, read the ledger's `Ruling:` and `deviation` lines for any
  interface a coming task consumes, as subagent-driven-development's
  `../subagent-driven-development/references/resuming.md` describes. Their
  commits exist in git even when your context no longer remembers making
  them: after compaction, trust the ledger and `git log` over your own
  recollection. A ledger whose first line names a different plan file is
  another plan's progress: stop and say so.
- Create the ledger with its identity as the first line:
  `Plan: <plan-file-path>`.
- `git clean -fdx` will destroy the workspace (it's git-ignored scratch);
  if that happens, recover from `git log`.

Executing on the base branch itself (only with your partner's explicit
consent)? Record `git rev-parse --short HEAD` in the ledger as
`Base start: <sha>` before
Task 1 — the final review starts there, because on the base branch there
is no merge base to compute. Two things break that record: losing it
(a `git clean` deletes the ledger), and a pull or rebase of the base branch
since, which brings
upstream commits into the range. Either way, ask your partner which
commit the plan's work starts *after* — the review excludes the commit it
starts from — rather than guessing. If the plan file is committed,
offer the commit that added it as a candidate —
`git log --follow --diff-filter=A --format=%h -- <plan-file> | tail -n 1`
— but let them confirm it: nothing guarantees it predates every task.

Read the plan once, note its context and Global Constraints, and create a
todo per task. If the plan names a Spec, read that too: the spec is the
authority the plan argues from, and conflicts inside the plan resolve
against it. A plan with no reachable spec gets a ledger note saying so —
rulings made without one are provisional.

**REQUIRED SUB-SKILL:** load test-driven-development now,
before Task 1. It governs every step of every task below; a plan whose
steps already say "write the failing test first" does not exempt you
from reading it.

Before Task 1, scan the plan for conflicts between tasks. The plan's
Interfaces blocks tell you where to look: for every task that consumes
what an earlier task produces, one ledger row — the two tasks, what one
produces against what the other consumes, and what you found. Tasks that
share nothing get no row; a plan whose tasks share nothing gets the single
line `Pre-flight: no shared interfaces`. A conflict a row surfaces goes to
your human partner in one batched question before Task 1, while they are
present at launch; record their answer beside its row. No conflict: start
Task 1. Each task's own text is checked when you read
its brief, not here.

## The Task Loop

Everything you print, and every tool result, stays resident in your
context for the rest of the session. Redirect long test output to a file
in the workspace and read its tail; read a brief, not the whole plan.

### 1. Take the task

- Run this skill's `scripts/task-start PLAN_FILE N`. It prints the brief
  path and BASE (the commit the task's range is cut from) in one call.
  Read the brief for every task, including ones you remember from setup:
  what you remember is a summary, the brief has the exact values,
  signatures, and test cases.
- Mark the task's todo in_progress.

Every tool call is a turn that re-reads your whole context. Bookkeeping
rides along with work — a ledger append in the same call as the commit,
never in a call of its own.

### 2. Work the steps

The plan's steps are already in RED-GREEN order; follow them in that
order under test-driven-development, loaded at setup. A test
step's code is written first and run first. Watching it fail is a step,
not a formality — a test that passes before the implementation exists is
a finding about the test.

Every step that runs a command has an `Expected:` line. Run the command,
read its output, and compare. Three outcomes:

- **Matches.** Next step.
- **The code is wrong.** Use systematic-debugging. Find the
  cause; never patch the symptom to make the step's output match.
- **The plan is wrong** — a step contradicts the spec, an interface from an
  earlier task doesn't match what this task consumes, a command that
  cannot work. Rule on the smallest change that satisfies the spec, ledger
  it as `Task <N>: Ruling: <what you decided> — <why> — <what it costs if
  wrong>`, and
  continue. The ruling is carried, not remembered: later tasks that touch
  the same interface read it from the ledger.

Commit as the plan's commit steps say. A task that spans several commits
is fine; BASE is what the review range is cut from, never `HEAD~1`.

### 3. The completion contract

Before a task's ledger line, all of the following are true, with evidence
in this session — not inferred from the diff looking right:

- Every test the brief names exists and ran in this task, and you read
  the output.
- The final test run for the task passed: `task-done` is that run, with
  the project's documented test command(s) (test-driven-development's
  "other tests"), not only the files the brief names.
- Every `Expected:` line in the brief was compared against real output.
- Every deviation from the brief has a `Ruling:` line in the ledger.

**REQUIRED SUB-SKILL:** verification-before-completion governs
the claim. If any item is missing, the task is not complete: finish it.

### 4. Complete the task

Run this skill's `scripts/task-done PLAN_FILE N BASE -- <test command>`
with the project's documented test command(s) that the change can reach.
It runs the
tests, keeps the full output in the workspace, prints the tail, and — only
if they pass — appends the completion line to the ledger:

`Task <N>: complete (commits <base7>..<head7>, tests: <command> → <result>)`

A failing run records nothing; the task is not complete. When it records,
mark the todo complete and take the next task.

When the last task's ledger line is written, read
[references/final-review.md](references/final-review.md) and follow it.
Read it again after a compaction.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I remember what Task N says" | You remember a summary. The brief has the exact values. Read it. |
| "The plan's code is right, skip watching the test fail" | A test you never saw fail proves nothing. It is one step. Run it. |
| "I'll run the full suite at the end instead of per step" | Per-step runs are how you learn which step broke it. The end-of-task run is the contract, not a substitute. |
| "The plan is wrong here, I'll just do the right thing" | Do the right thing and ledger the ruling. Unledgered deviation is a decision made in secret. |
| "I'll write the ledger lines after a few tasks" | Compaction does not wait for a convenient moment. One line per task, in the same message as the commit. |
| "Let me check in before the next task" | They chose inline for one shared context. Progress prompts spend their time instead. Only the five stops stop you. |
| "The plan says to touch that file, the fence says no, the plan is newer" | A fence is not a conflict to rule on. Stop and ask. |
| "I read my own diff carefully; the final reviewer is redundant" | Same author, same blind spots. The reviewer is the only fresh context this run buys. |
| "Tests should pass, the change was trivial" | "Should" is not evidence. The contract requires the command and its output. |
| "Subagents are slow and expensive, I'll skip the final review too" | Inline already removed the per-task reviewers. One review of the whole branch is the floor, not the ceiling. |
| "The fix is obvious, no need for a failing test first" | The failing test is the only proof the finding was real and is now gone. Without it you have a diff and a hope. |

## Integration

**Required workflow skills:**
- **using-git-worktrees** - Ensures isolated workspace (creates one or verifies existing)
- **writing-plans** - Creates the plan this skill executes
- **requesting-code-review** - code-reviewer template and Codex second-opinion recipe for the whole-plan review
- **receiving-code-review** - Works the merged findings before anything is fixed
- **finishing-a-development-branch** - Complete development after all tasks
- **subagent-driven-development** - its scripts give the workspace and briefs; its ledger format is shared
