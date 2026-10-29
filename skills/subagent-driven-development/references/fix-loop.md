# Fix loop

Read this again before every fix round: who fixes, how the re-review runs, and when you stop to adjudicate.

A task gets at most **five fix attempts**. Adjudication follows the fifth; it
is not itself an attempt.

| Round | Action |
|---|---|
| 1-3 | Resume the same implementer with the findings. It appends a fix report to its existing report file: what changed, the covering tests it ran, the command, and the output. |
| 4-5 | Dispatch a **fresh** implementer with the task brief and the findings. Raise reasoning effort when the prior rounds show a thorough attempt rather than a missing-context failure. |
| after 5 | The cap is reached. Adjudicate every still-open finding; dispatch no further fix rounds for this task. |

Re-review each round with the scoped [re-review-prompt.md](re-review-prompt.md),
not a fresh full review — the task review already happened, and re-reading the
whole task every round is the cost this cap exists to bound.

Going fresh at round 4 is the load-bearing half. A resumed implementer carries
its own failed attempts as context, which anchors it to the approach that is not
working; a fresh one does not. Escalate in the order context, then effort, then
model, and stop when there is no headroom. Which rungs remain depends on the
tier **this implementer was dispatched at** — not on your own session's model,
which it never inherited. An implementer below **capable** still has the model
rung. One already at **capable** has fresh context and higher reasoning effort,
then one last model rung where the runtime offers `fable`: when round 4 was a
thorough attempt that still failed, dispatch round 5 at `fable`. Where it does
not, effort is the last rung.

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
  tell your partner why, and dispatch the fix subagent in the same turn.
- Dispatch fix subagents for Critical and Important findings — rounds 1-3
  resume the same implementer, rounds 4-5 dispatch a fresh one (see **Fix
  Rounds**). Record Minor findings in the progress ledger as you go, and
  point the final whole-branch review at that list so it can triage which
  must be fixed before merge. A roll-up nobody reads is a silent discard.
- A finding labeled plan-mandated — or any finding that conflicts with
  what the plan's text requires — is the human's decision, like any plan
  contradiction: present the finding and the plan text, ask which governs.
  Do not dismiss the finding because the plan mandates it, and do not
  dispatch a fix that contradicts the plan without asking.
- Every fix dispatch — resumed for rounds 1-3, fresh for 4-5 (see **Fix
  Rounds**) — carries the implementer contract: the fix subagent re-runs the
  tests covering its change and reports the results. Name the covering test
  files in the dispatch — a one-line fix does not need the whole suite.
  Before re-dispatching the reviewer, confirm the fix report contains the
  covering tests, the command run, and the output; dispatch the re-review
  once all three are present.
