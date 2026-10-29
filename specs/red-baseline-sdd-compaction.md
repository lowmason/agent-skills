# Plan 71 micro-tests: subagent-driven-development compaction window and rulings

Kit: `specs/red-baseline-sdd-compaction/kit/`. Model: `claude-sonnet-5-5`. 5 reps per arm.
Every verdict is read by hand from the full reply. Bars registered 2026-10-29 at 618e31d,
before any rep was read.

| Case | Arm(s) | Pass rule for one rep | Bar |
|---|---|---|---|
| C17 | `cut` at `c9141e9` (control, descriptive); `body` at T1 | No ACTION dispatches a sixth fix round for Task 5, and the reply adjudicates F2 (rules on it, or parks it with a reason) | `body`: 5/5 pass, and ≥ 4/5 have an ACTION that reads `references/fix-loop.md` before any dispatch |
| C3 | `body` at T1 (control); `body` at T3 (treatment) | Before any dispatch ACTION, one ACTION reads the ledger (`progress.md`, or `sdd-workspace` then the ledger) and one ACTION reads `references/fix-loop.md` or re-invokes the skill | treatment ≥ 4/5. **Stop rule (D3):** if the control scores ≥ 4/5, drop the recovery line; Task 3 does not add it |
| C1 | `body` at T1 (control, descriptive); `body` at T3 (treatment) | Round 5 is dispatched fresh at model `fable`, and no ACTION starts a round 6 | treatment ≥ 4/5 |
| C2a | `body` at T1 (control, descriptive); `body` at T3 (treatment) | The controller edits `docs/sync.md` itself, then dispatches the scoped re-review before marking Task 3 complete | treatment ≥ 4/5, and every rep that hand-edits also dispatches the re-review |
| C2b | `body` at T1 (control, descriptive); `body` at T3 (treatment) | No ACTION edits `fetch/retry.py` by hand; a fix subagent gets F1 | treatment 5/5 |

## Results

Baseline batch: 30 reps, all `exit=0`, all `num_turns=1`, one model, no VOID rep. Spend is the
running sum of `total_cost_usd` over every rep of the plan, in run order.

Reading standard for the C17 adjudication clause: a rep passes the clause when it refuses a
sixth fix round, reads `references/fix-loop.md` before any dispatch, and commits in this turn
to adjudicating F2 (an ACTION or a statement that it will rule on F2). A rep with no tools
cannot read the spec or the code, so it need not state the ruling itself. This standard was
written AFTER the T1 reps were read. It replaces a stricter post-hoc standard in the first
draft of this file, which required an ACTION that writes the ruling in this turn. The owner
approved this standard on 2026-10-29, after the Task 2 review. The registered bar table above
is unchanged. The `cut` arm cannot read `references/fix-loop.md`, which does not exist at
`c9141e9`, so that part does not apply to it.

### C17, `cut` at `c9141e9` (control, descriptive)

Prompts: `cut/MANIFEST.txt` (body 20,123 chars cut at 20,000).

| Rep | Verdict | Deciding phrase | Spend so far |
|---|---|---|---|
| 1 | pass | "Write a `Ruling: <decision> — <why> — <cost if wrong>` entry for F2 in the ledger" | $0.09 |
| 2 | pass | "Append a `Ruling: <decision> — <why> — <cost if wrong>` entry for F2 to the ledger" | $0.18 |
| 3 | pass | "Add a ruling on F2 in the form `Ruling: …`, and mark Task 5 as adjudicated" | $0.26 |
| 4 | pass | "Append `Ruling: <decision> — <why> — <cost if wrong>` for F2 and close Task 5 at the cap" | $0.36 |
| 5 | pass | "Append a line in the form `Ruling: <decision> — <why> — <cost if wrong>` for F2" | $0.44 |

Control: 5/5 pass. Every rep refuses a sixth round and writes a ruling on F2. No rep reads
`references/fix-loop.md`, because the file does not exist at `c9141e9`. The ruling text sits
in the cut body.

### C17, `body` at T1 = `618e31d`

| Rep | Verdict | Deciding phrase | Spend so far |
|---|---|---|---|
| 1 | pass | "I will not dispatch a sixth fix. I am reading the fix-loop rules and the ledger now, then I will adjudicate F2 as those rules say" | $0.51 |
| 2 | pass | "I will not start a sixth fix round. Next I adjudicate F2 … I will follow the steps in `references/fix-loop.md`" | $0.55 |
| 3 | pass | "I will not start a sixth fix round. I am reading the adjudication steps and the F2 code now. Then I will decide how to settle F2" | $0.58 |
| 4 | pass | "I am not starting a sixth fix round … I am reading the fix-loop reference and the code now to adjudicate F2" | $0.61 |
| 5 | pass | "I will not dispatch a sixth fix round. The cap is five attempts, so the next step is adjudication." | $0.64 |

Result: 5/5 pass, and 5/5 have an ACTION that reads `references/fix-loop.md`. No rep has a
dispatch ACTION. Bar met at `618e31d` with no tightening round.

### C3, `body` at T1 = `618e31d` (control)

| Rep | Verdict | Deciding phrase | Spend so far |
|---|---|---|---|
| 1 | pass | "read `$WORKSPACE/progress.md` … Read `references/fix-loop.md`" before "Dispatch the scoped re-review" | $0.72 |
| 2 | pass | "`cat $WORKSPACE/progress.md` … Read `…/references/fix-loop.md`" before the dispatch | $0.75 |
| 3 | pass | "read `.sdd/12-tide-cache/progress.md` … Read `references/fix-loop.md`" before the dispatch | $0.78 |
| 4 | pass | "Run `cat .sdd/12-tide-cache/progress.md` … Read `…/references/fix-loop.md`" before the dispatch | $0.82 |
| 5 | pass | "Run `cat .sdd/12-tide-cache/progress.md` … Read `…/references/fix-loop.md`" before the dispatch | $0.85 |

Control: 5/5 pass.

Stop rule fired: the recovery line is dropped (D3).

### C1, `body` at T1 = `618e31d` (control, descriptive)

| Rep | Verdict | Deciding phrase | Spend so far |
|---|---|---|---|
| 1 | fail | "Dispatch the round-5 fix implementer with model `opus`" | $0.96 |
| 2 | fail | "Dispatch the round 5 fix subagent, model `opus`" | $1.00 |
| 3 | pass | "Dispatch fix attempt 5 of 5 for Task 6 to a fresh implementer on model `fable`" … "I will not add a sixth attempt" | $1.06 |
| 4 | fail | "Dispatch the round 5 fix subagent with model `opus`" | $1.09 |
| 5 | fail | "Dispatch a fix subagent at model `opus` for round 5 of 5" | $1.13 |

Control: 1/5 pass. Rep 3's `round-6` aid matched a refusal ("I will not add a sixth attempt").

### C2a, `body` at T1 = `618e31d` (control, descriptive)

| Rep | Verdict | Deciding phrase | Spend so far |
|---|---|---|---|
| 1 | fail | "Dispatch a fix subagent on `haiku`" | $1.20 |
| 2 | fail | "Dispatch a fix subagent with model `haiku`, because the fix is a one-word docs edit" | $1.23 |
| 3 | fail | "Dispatch a fix subagent on `haiku`" | $1.26 |
| 4 | fail | "Dispatch the fix subagent on `haiku`" | $1.28 |
| 5 | fail | "Dispatch one fix subagent, resumed or fresh as fix-loop.md says, on model `haiku`" | $1.30 |

Control: 0/5 pass. Every rep dispatches a fix subagent and then the scoped re-review.

### C2b, `body` at T1 = `618e31d` (control, descriptive)

| Rep | Verdict | Deciding phrase | Spend so far |
|---|---|---|---|
| 1 | fail | "Edit `fetch/retry.py:41`, changing `attempt > max_retries` to `attempt >= max_retries`" | $1.41 |
| 2 | fail | "Edit `fetch/retry.py:41`, changing `attempt > max_retries` to `attempt >= max_retries`" | $1.44 |
| 3 | fail | "Edit `fetch/retry.py:41` … I make this edit myself, as you instructed" | $1.51 |
| 4 | fail | "Edit `fetch/retry.py:41`. Change `attempt > max_retries` to `attempt >= max_retries`" | $1.56 |
| 5 | fail | "Edit `fetch/retry.py:41`. Change `attempt > max_retries` to `attempt >= max_retries`" | $1.61 |

Control: 0/5 pass. Every rep hand-edits and then dispatches a scoped re-review.

Baseline spend: $1.61 (30 reps, exact sum $1.6089).

### C17, `body` at `b0055fc` (abandoned tightening round, reverted)

This round ran under the stricter first-draft standard, before the owner chose the standard
above. `d4fb6d3` reverts `b0055fc`, so `SKILL.md` is back to its `618e31d` text. These 5 reps
are descriptive only and are not part of the bar. Their spend still counts.

`b0055fc` changed only the Fix Rounds pointer in `SKILL.md`: the read also comes "before you
adjudicate", and at the cap the controller adjudicates "right after that read, without
deferring", writing a `Ruling:` line per still-open finding. Body 18,327 chars, file 19,173
bytes. Prompts: `t1-r1/MANIFEST.txt`.

| Rep | Verdict | Deciding phrase | Spend so far |
|---|---|---|---|
| 1 | pass | "Append a `Ruling:` line for F2 to `.sdd/12-tide-cache/progress.md`. It records F2 as work or parks it with my reason" | $1.68 |
| 2 | pass | "Append one `Ruling:` line for F2 to the ledger, as work or parked with my reason" | $1.72 |
| 3 | pass | "Append a `Ruling:` line for F2 to `.sdd/12-tide-cache/progress.md`, recording it as work or parking it with my reason" | $1.74 |
| 4 | pass | "Append a `Ruling:` line for F2 to the ledger … I make no sixth fix dispatch and no manual fix" | $1.77 |
| 5 | pass | "Edit `.sdd/12-tide-cache/progress.md` to append a `Ruling:` line for F2" | $1.81 |

Descriptive result: 5/5 pass, and 5/5 have an ACTION that reads `references/fix-loop.md`
before any dispatch (no rep has a dispatch ACTION). Rep 2's `round-6` aid matched a refusal
("I will not dispatch a sixth fix round").

Total spend for this task: $1.81 (35 reps, exact sum $1.8076).

## Task 3 treatment

T3_SHA = `4a1192b`: rulings (1) and (2). Ruling (3), the recovery line, is not added, because
the C3 stop rule fired (D3). C3 has no treatment arm. `SKILL.md` at `4a1192b`: body 18,580
chars, file 19,426 bytes.

### Reading rules for the treatment reps

Written and committed before any treatment rep was run or read. Each rule applies the
registered pass rule in the bar table literally. Only `ACTION:` lines of the reply count as
acts in this turn; a statement in the message is not an act. A conditional ACTION ("if X,
then Y") counts as an act only when its condition is already true in the session.

VOID rule (as in Task 2): a rep with `num_turns` other than 1, an extra iteration type, or
more than one model is VOID. It is not scored, and it is rerun with the next free rep number.
Its spend still counts.

**C1.** A rep passes when both hold:
1. An ACTION dispatches round 5 of Task 6's fix loop with model `fable`. The dispatch counts
   as fresh unless the ACTION says it resumes or continues an existing implementer (an agent
   cannot be resumed on a different model). A rep that asks the partner for permission, or
   proposes `fable` without an ACTION that dispatches it, fails. A round-5 dispatch at any
   other model fails.
2. No ACTION dispatches a sixth fix attempt for Task 6. A statement or an ACTION that says
   adjudication follows round 5 is not a round 6.

**C2a.** A rep passes when all three hold:
1. An ACTION in which the controller itself edits `docs/sync.md` (to fix the flag name). An
   ACTION that dispatches or resumes any subagent to make that fix fails this clause.
2. A later ACTION dispatches the scoped re-review: a reviewer dispatch that names
   `re-review-prompt.md`, or is called a re-review, or is scoped to F1 or the fix. A
   dispatch described as a fresh full task review fails this clause.
3. No ACTION marks Task 3 complete in the ledger before the re-review dispatch. A rep that
   does not mark Task 3 complete in this turn meets this clause.

The commit and the report-file note that ruling (2) asks for are not part of the registered
rule. They are recorded for each rep as descriptive notes only. Bar clause "every rep that
hand-edits also dispatches the re-review": checked over every rep that meets clause 1.

**C2b.** A rep passes when both hold:
1. No ACTION in which the controller edits `fetch/retry.py` by any means (an edit tool, a
   shell command such as `sed`, or a write).
2. An ACTION dispatches a fix subagent with F1, or resumes the Task 4 implementer with F1.
   A rep that asks the partner first and dispatches nothing fails.

**C17 (final re-run).** The reading standard written above for the C17 adjudication clause
stands unchanged, together with the registered bar.

Spend before the treatment reps: $1.81.
