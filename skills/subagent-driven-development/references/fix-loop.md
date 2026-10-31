# Fix loop

Read this again before every fix round: who fixes, how the re-review runs, and when you stop to adjudicate.

A task gets at most **five fix attempts**. Adjudication follows the fifth; it
is not itself an attempt.

| Round | Action |
|---|---|
| 1-3 | Resume the same implementer with the findings. It appends a fix report to its existing report file: what changed, the covering tests it ran, the command, and the output. |
| 4-5 | Dispatch a **fresh** implementer with the task brief and the findings. Raise reasoning effort when the prior rounds show a thorough attempt rather than a missing-context failure. |
| after 5 | The cap is reached. Adjudicate every still-open finding; dispatch no further fix rounds for this task. |

Re-review each round with the scoped [re-review-prompt.md](../re-review-prompt.md),
not a fresh full review — the task review already happened, and re-reading the
whole task every round is the cost this cap exists to bound.

Going fresh at round 4 is the load-bearing half. A resumed implementer carries
its own failed attempts as context, which anchors it to the approach that is not
working; a fresh one does not. Escalate in the order context, then effort, then
model, and stop when there is no headroom. Which rungs remain depends on the
tier **this implementer was dispatched at** — not on your own session's model,
which it never inherited. An implementer below **capable** still has the model
rung. One already at **capable** has fresh context and higher reasoning effort,
then one last model rung: when round 4 was a thorough attempt that still
failed, where the runtime offers `fable`, dispatch round 5 at `fable`. Where the
runtime does not offer `fable`, effort is the last rung.

**Adjudicating** means you rule on each open finding: record the load-bearing
ones as work, and park the rest in the ledger with your reasoning
(`Ruling: <what you decided> — <why> — <what it costs if wrong>`). Stop for your
human partner only when every path forward is a guess.

## Fix dispatches

- Exception: a fix confined to one file that changes no behavior (wording, a
  typo, a wrong name or path in prose or docs) you may make yourself. Commit it,
  append to the implementer's report file what you changed and that it changes
  no behavior, so no test covers it, then dispatch the scoped re-review as
  usual. A fix that changes what code does, even by one character, goes to a
  fix subagent, also when your partner asked you to fix small things yourself:
  tell your partner why, and dispatch the fix subagent in the same turn. A
  hand fix counts as one of the five attempts.
- Dispatch fix subagents for Critical and Important findings — rounds 1-3
  resume the same implementer, rounds 4-5 dispatch a fresh one (see **Fix
  Rounds**). Rule on each Declined to judge line from a task review as you
  go: make it a finding, or ledger why it stays out
  (`Ruling: <what you decided> — <why> — <what it costs if wrong>`). Point
  the final whole-branch review at these `Ruling:` lines; a ruling it
  disagrees with comes back as a finding.
- A finding labeled plan-mandated — or any finding that conflicts with
  what the plan's text requires — is yours to rule on: weigh the finding
  against the plan text, decide with the spec as the binding authority,
  and ledger `Ruling: <what you decided> — <why> — <what it costs if
  wrong>` before you act on it. Do not dismiss the finding because the
  plan mandates it, and do not dispatch a fix that contradicts the plan
  without a recorded ruling. Five things stop such a ruling, and only
  these; for them, stop and ask your human partner:
  1. An irreversible or destructive operation.
  2. A security-sensitive action.
  3. A side effect outside this worktree that norms say you ask about first: a merge, a push to a shared branch, a publish.
  4. A plan so broken that every path forward is a guess.
  5. The explicit scope fence: a line in the plan (its Global Constraints, its header or a task) or in your partner's launch message that puts a file, a directory, a system or a kind of change out of bounds for this run — "Do not edit `skills/`", "No changes outside `build/`", "Do not change the public API". A ruling never crosses a fence: when the only fix crosses one, stop and ask. A task's text that contradicts a Global Constraint that is not a fence is not a stop: the constraint wins, and that is a ruling.
- Every fix dispatch — resumed for rounds 1-3, fresh for 4-5 (see **Fix
  Rounds**) — carries the implementer contract: the fix subagent re-runs the
  tests covering its change and reports the results. Name the covering test
  files in the dispatch — a one-line fix does not need the whole suite.
  Before re-dispatching the reviewer, confirm the fix report contains the
  covering tests, the command run, and the output; dispatch the re-review
  once all three are present.
