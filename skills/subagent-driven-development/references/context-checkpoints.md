# Context checkpoints — the handoff procedure

The three-step durable handoff to run once a context checkpoint fires.

SKILL.md § Context Checkpoints names the trigger. This file holds the reasons,
the boundary rules and the handoff to run once it fires.

## When and why

Everything you dispatch and every report you read stays resident in your
context, re-read on every later turn at cache-read cost. On a long plan this
recurring cost grows with each task — the controller's accumulated history, not
the work, becomes the dominant spend. Cap it by resetting context at a task
boundary and handing off to a fresh session that resumes where this one stopped.

A checkpoint is **not** a "should I continue?" check-in (still banned) and never
interrupts a task — it is a durable handoff taken only at a clean boundary.

**When:** at a task boundary (never mid-task, never with a review loop open)
when the harness signals context pressure — a compaction warning, or context
you notice has grown large. Many tasks since the last fresh start is a weak
secondary hint, not a trigger by itself; task sizes vary, so read the
context-pressure signal, not a task count.

**How:** run the three-step handoff below. The relaunch resumes from the ledger via SKILL.md § Durable Progress.

## How

1. **Capture cross-task state the ledger lacks.** The plan's `Produces:` blocks
   carry each task's *planned* interfaces, not what changed during execution.
   For each task done since the last fresh start, append any plan deviation a
   later implementer must know — a renamed symbol, a changed signature, or an
   unanticipated decision (`Task 3: deviation — plan said clearLayers(); shipped
   clearAll()`). A task that matched its plan needs no line. After `/clear` your
   memory of these is gone; the ledger is the only carrier.
2. Confirm the ledger's completion lines are current through the last finished
   task and that their commits exist in `git log`.
3. In one line, tell your human partner which tasks are complete, that the
   ledger is current, and that you recommend `/clear` + relaunching
   subagent-driven-development on the same plan to resume with fresh context —
   with the cost reason. Then stop; the relaunch resumes from the ledger via
   SKILL.md § Durable Progress and [resuming.md](resuming.md).
