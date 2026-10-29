# Final review and plan completion

Read this when the last task's review resolves, before you dispatch the final whole-branch review.

## Final whole-branch review

- The final whole-branch review has two seats, launched in the same message:
  the code-reviewer subagent (requesting-code-review's code-reviewer.md) and
  the Codex second opinion in requesting-code-review's
  [codex-review.md](../../requesting-code-review/codex-review.md), `--base` at
  the same merge base. When the Codex run completes, the recipe has you write
  `Codex reviewed <sha>` into the conversation, where
  finishing-a-development-branch reads it after this workspace is gone. Copy
  that exact line into the progress ledger too, and back into the
  conversation if you resume from the ledger. Touch nothing until both seats
  have returned.
- Fill the code-reviewer's `[PLAN_OR_REQUIREMENTS]` with the plan path; the
  spec path from the plan's `Spec:` line, or `none: the plan is the
  requirement`; the plan's `## Review Focus` section, word for word (the
  inputs and failure modes the plan's tests do not exercise: the reviewer
  checks each one deliberately); and a pointer to the ledger's `Ruling:`
  lines.
- If the final whole-branch review returns findings, merge both seats' lists
  and dispatch ONE fix subagent with the complete list — not one fixer per
  finding.
  Per-finding fixers each rebuild context and re-run suites; a real
  session's final-review fix wave cost more than all its tasks combined.

## Plan completion

After the final whole-branch review resolves, run the plan-completion
protocol from the writing-plans skill (its "Plan Completion Protocol"
section): resolve-before-defer gate → plan markup → deferred items →
retire. The gate's batched questions are this skill's one deliberate human
checkpoint — fold any question sets already pending (plan-mandated
findings, the final review's Declined to judge lines, each for your human
partner to rule on) into the same batch, so your human partner gets at most
one round-trip. Review findings the final review left unfixed feed the gate.
This is compatible with Continuous execution: "all tasks complete" is a
sanctioned stop.

When the plan-completion protocol has finished and the final review's fixes
are merged, delete this plan's workspace — the `$WORKSPACE` you resolved at
skill start: `rm -rf "$WORKSPACE"`. If a `/clear` and relaunch since then left
you without that variable, re-run `<this-skill-dir>/scripts/sdd-workspace <plan-file>`; it is
idempotent and reprints the same path. Git history is the record now. Sibling
directories under `.sdd/` belong to other plans — leave them alone, and never
`rm -rf .sdd` itself.

Order matters. The delete runs **after** the protocol, never before: the
resolve-before-defer gate reads this run's leftovers — the ledger, unfixed
review findings, the final review's Declined to judge lines — to build its batched questions
and the `specs/deferred_items.md` entries. Deleting the workspace first
destroys the protocol's input.
