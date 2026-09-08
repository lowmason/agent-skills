# Context checkpoints — the handoff procedure

The three-step durable handoff to run once a context checkpoint fires.

SKILL.md § Context Checkpoints carries the trigger and the boundary rules —
task boundary only, never mid-task, never with a review loop open, and never a
"should I continue?" check-in. This file is what you do after it fires.

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
   SKILL.md § Durable Progress.
