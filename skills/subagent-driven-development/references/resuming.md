# Resuming a plan

Read this after a /clear, a relaunch or a compaction, before any dispatch.

- The workspace is per plan, so that ledger is always this plan's. Its first
  line names the plan it belongs to; if that name is not the plan in your hand,
  stop and say so rather than resuming against it.
- **On resume after a checkpoint, reconcile before dispatching.** Before
  dispatching the first incomplete task, replay the ledger's `deviation` lines:
  for any interface a coming task consumes, trust the ledger's actual signature
  over the plan's `Produces:` block, and if one is still in doubt confirm it
  with `git show <SHA>:<path>`. This repairs the cross-task context that
  `/clear` dropped — without it a relaunched controller dispatches stale
  signatures and the build breaks or the implementer stalls on NEEDS_CONTEXT.
