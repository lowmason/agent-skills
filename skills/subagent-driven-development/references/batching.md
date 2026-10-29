# Batching small same-shape tasks

Read this before you dispatch several small edits of the same kind one by one.

**Batch small same-shape work.** When the plan lists several tasks that are
each a small, independent edit of the same kind — the same one-line fix,
constant change, or field addition repeated across files — do not dispatch one
subagent per task. Compose ONE dispatch brief listing every file and its
change, send the whole batch to a single implementer, and review its diff as
one unit. Reserve one-dispatch-per-task for work that needs its own judgment,
its own tests, or its own review surface.

You write the batch brief yourself; `scripts/task-brief` still extracts exactly
one task and gains no multi-task mode. That is a deliberate exception to the
rule that task text stays out of your context: batching applies only to changes
small enough to state in a line each, so the cost is bounded — and teaching
`task-brief` to concatenate sections would pull full task text through your
context for exactly the tasks that need it least.

Write the composed brief to `batch-N-M-brief.md` (the covered task numbers,
e.g. `batch-4-7-brief.md`) in this plan's workspace — the directory this
skill's `scripts/sdd-workspace <plan-file>` prints. Hand that one path to
both the implementer and the reviewer as `[BRIEF_FILE]`, the same handoff
**File Handoffs** gives a single-task brief.

Open that brief with the plan's Global Constraints, copied verbatim.
`task-brief` prepends them to every brief it writes, which is what lets
**File Handoffs** promise the implementer its brief carries them; a brief you
compose yourself inherits the promise with nothing mechanical to keep it, and
the reviewer's file-by-file check verifies file coverage, not constraint
carriage — so a batch that drops them fails silently.

## The batch's ledger entry

- A batched dispatch gets ONE ledger entry naming every task number it covered:
  `Tasks 4-7: complete (batched; commits <base7>..<head7>, review clean)`. The
  range is shorthand for a contiguous batch, not the required form — a
  non-contiguous batch lists its numbers:
  `Tasks 2, 5, 9: complete (batched; commits <base7>..<head7>, review clean)`. A
  resuming controller reads task numbers from that line, so a batch recorded
  under only its first task's number re-dispatches the rest.
