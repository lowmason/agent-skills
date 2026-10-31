# Final review and plan completion

Read this when the last task's ledger line is written, and again after a compaction.

## Review the whole plan

After the last task is verified, review the whole branch with two reviewers,
launched in the same message so they run concurrently. Compute one BASE for
both, now: `git merge-base <base-branch> HEAD`. On a branch cut for this plan
that is where the plan began; on a branch that already carried work, the
review covers that work too — as subagent-driven-development's final review
does, and as finishing-a-development-branch relies on. Computing it at review
time, rather than recording it earlier, also survives a `/clear` and a rebase
onto a newer base branch. On the base branch itself that command returns HEAD
— an empty range — so use the start Setup had you record, or the one your
partner confirmed.

1. **code-reviewer** — fill requesting-code-review's
   [code-reviewer.md](../../requesting-code-review/code-reviewer.md) with the plan
   file, the spec path from its `Spec:` line (or `none: the plan is the
   requirement` when it has none) and its `## Review Focus` section word for
   word if it has one, and a pointer to the ledger's `Ruling:` lines, as
   `[PLAN_OR_REQUIREMENTS]` (the reviewer checks each
   Review Focus line deliberately), BASE as `[BASE_SHA]`, and the capable
   model tier (opus), as for any final whole-branch review.
2. **Codex** — the second-opinion review in
   [codex-review.md](../../requesting-code-review/codex-review.md), with
   `--base <BASE>`.

**Without a subagent tool:** read code-reviewer.md and perform that review
yourself against the BASE..HEAD diff, as a separate pass after the last task's
ledger line. Write `Final review: self-review (no subagent tool)` to the
ledger, and say so in your final message: a self-review by the author is
weaker than a fresh reviewer, and your human partner decides whether that
is enough before merge. The Codex seat still runs when the Codex CLI is present.

Touch nothing until both have returned. When the Codex run completes, copy
its `Codex reviewed <sha>` line into the ledger too, and back into the
conversation if you resume from the ledger, as
subagent-driven-development's final review does.

## Fix pass

Merge the two lists into one, and work it with the receiving-code-review
skill.

Fix the findings that hold up yourself — you are the
implementer here — in ONE pass. Each fix is verified by TDD, not by a
second reviewer: write the test that reproduces the finding, watch it
fail, make it pass, then run the project's documented test command(s).
Record each in the ledger as
`Final: fixed <finding> — <test name> RED→GREEN, suite <result>`. A fix
that changes no behavior (wording, a typo, a wrong name or path in prose
or docs) needs no test: ledger what you changed and that it changes no
behavior, so no test covers it. Any other fix
without a test that failed first is not verified; a documented suite that is not
green after the pass means the pass is not over. Do not dispatch a
re-review: it would re-read a diff whose covering tests already answer
"addressed" and whose suite run already answers "broke nothing".

A finding you decide not to fix is a ruling — `Final: Ruling: <finding> —
<why the code stands> — <cost if wrong>` — and reaches your human partner
in the rulings list at the plan-completion gate. There is no second fix pass.

The code-reviewer's Declined to judge lines are not ruled on here: they go
to your partner at the plan-completion gate.

Commit the fixes — the plan-completion protocol commits only
`specs/`, and the branch ships as committed.

## Complete the plan

After the review resolves, run the plan-completion protocol
from the writing-plans skill (its "Plan Completion Protocol" section):
resolve-before-defer gate → plan markup → deferred items → retire the plan
and (conditionally) its spec.

In the gate's batched questions, list every `Ruling:` line in the ledger
first, all of them, in the order made, each with what it costs if wrong —
decisions already taken, shown so your partner sees them, not questions —
then fold the final review's Declined to judge lines, each for your human
partner to rule on, into the same batch, so your human partner gets at most
one round-trip. Findings the fix pass left unfixed feed the gate.

When the protocol has finished, delete this plan's workspace — the
directory `sdd-workspace` printed at setup; if you lost it, re-run the
`sdd-workspace` command that Setup ran. Sibling directories under `.sdd/` belong to other plans; leave them
alone. The delete runs after the protocol, never before, because the
resolve-before-defer gate reads the ledger, the unfixed findings and the
Declined to judge lines to build its questions and deferred items.

## Complete development

Once the plan is complete and retired:
- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use finishing-a-development-branch
- Follow that skill to verify tests, present options, execute choice

## Hand off a roadmap stage

When the plan's header carries a `Roadmap:` line, end by the outcome of
finishing-a-development-branch:

| Outcome | Final message |
|---|---|
| Merged locally | "Stage N of `<roadmap>` is merged. Next: /clear (or a fresh session), then resume the roadmap: derive-roadmap on `<roadmap>`." Then stop. |
| PR opened | "Resume the roadmap once `<PR>` merges." |
| Kept | "Stage N is complete on `<branch>` but unmerged. Resume the roadmap after it merges." |
| Discarded | No handoff: the stamp went with the branch. |

Even when asked to keep going, never resume the roadmap here or plan,
brainstorm or route to the next stage (step 3a's Handoff bullets and stamp
still name the stages they feed), and make no model-tier claim. A stage this
session finds already merged when it starts, with the protocol not yet run,
runs the protocol on the merged branch now.
Any other plan ends at Complete development.
