# Reviewer items marked ⚠️

Read this when a reviewer marks an item it could not verify.

The task reviewer may report "⚠️ Cannot verify from diff" items — requirements
that live in unchanged code or span tasks. These do not block the rest of the
review, but you must resolve each one yourself before marking the task
complete: you hold the plan and cross-task context the reviewer
lacks. If you confirm an item is a real gap, treat it as a failed spec
review — send it back to the implementer and re-review. That send-back is a
fix round: it uses the scoped [re-review-prompt.md](re-review-prompt.md) and
counts against the five (see **Fix Rounds**).
