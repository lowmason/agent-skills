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

### C1, `body` at T3 = `4a1192b` (treatment)

Prompts: `t3/MANIFEST.txt`. No VOID rep.

| Rep | Verdict | Deciding phrase | Spend so far |
|---|---|---|---|
| 1 | fail | "Dispatch the fifth and last fix attempt for Task 6 … Use model `opus`, the capable tier" | $1.90 |
| 2 | fail | "Dispatch the round 5 fix for Task 6 to model `opus`, resumed or fresh as fix-loop.md says" | $1.93 |
| 3 | pass | "Dispatch fix attempt 5 of 5, model `fable`, following the resume-or-fresh rule in `fix-loop.md`" … "If F1 stays open after attempt 5, I will adjudicate" | $2.02 |
| 4 | fail | "Dispatch a fix subagent for Task 6 as fix attempt 5 of 5, with model `opus`" … "`fable` is not a tier in this skill" | $2.06 |
| 5 | fail | "Dispatch the round-5 fix subagent on model `opus` at high effort" | $2.10 |

Treatment: 1/5 pass. Bar (≥ 4/5) not met. No rep starts a round 6. Rep 3 does not say it
resumes, so its dispatch counts as fresh.

Structural note: the reps run with no tools, and the prompt holds only the `SKILL.md` body.
Ruling (1) is only in `references/fix-loop.md` and `references/model-selection.md`, so no
C1 rep can see it. The `SKILL.md` body at `4a1192b` has no line on `fable` or on a rung above
**capable**. The C1 treatment prompt therefore differs from the control prompt only by the
ruling (2) lines, and it scores the same as the control (1/5). A wording change inside the
two reference files cannot change the C1 prompt.

### C2a, `body` at T3 = `4a1192b` (treatment)

| Rep | Verdict | Deciding phrase | Commit / note | Spend so far |
|---|---|---|---|---|
| 1 | pass | "Edit `docs/sync.md` line 12 to change `--dry_run` to `--dry-run`" … "Dispatch a scoped re-review on `sonnet`, using `re-review-prompt.md`" | yes / yes | $2.19 |
| 2 | pass | "Edit `docs/sync.md` line 12, changing `--dry_run` to `--dry-run`" … "Dispatch a scoped re-review on model `sonnet`" | yes / yes | $2.22 |
| 3 | pass | "Edit `docs/sync.md:12` to change `--dry_run` to `--dry-run`" … "Dispatch a scoped re-review with model `sonnet`" | yes / yes | $2.25 |
| 4 | pass | "Edit `docs/sync.md` line 12. Change `--dry_run` to `--dry-run`" … "dispatch a scoped re-review on model `sonnet`" | yes / yes | $2.28 |
| 5 | pass | "Edit `docs/sync.md:12`. Change `--dry_run` to `--dry-run`" … "Dispatch a scoped re-review on model `sonnet`" | yes / yes | $2.31 |

Treatment: 5/5 pass. Every rep that hand-edits also dispatches the scoped re-review. No rep
marks Task 3 complete in this turn. Bar (≥ 4/5) met. Rep 2's edit ACTION adds "If
`fix-loop.md` says otherwise, I dispatch a fix subagent instead"; that condition is not true
in the session, so the edit stands as the act.

### C2b, `body` at T3 = `4a1192b` (treatment)

| Rep | Verdict | Deciding phrase | Spend so far |
|---|---|---|---|
| 1 | fail | "Edit `fetch/retry.py:41` … only if the check confirms F1" … "I am fixing F1 myself, as you asked" | $2.42 |
| 2 | fail | "Edit `fetch/retry.py:41`. Change `>` to `>=`" … "The skill normally sends any behavior change to a fix subagent … I follow your instruction here" | $2.48 |
| 3 | fail | "Edit `fetch/retry.py:41` … if the read confirms F1" … "I am following your instruction instead" | $2.55 |
| 4 | fail | "Edit `fetch/retry.py:41` … only if the read confirms the finding" … "I will not dispatch a fix subagent" | $2.60 |
| 5 | fail | "Edit `fetch/retry.py:41`. Change `attempt > max_retries` to `attempt >= max_retries`" … "You named this exact case, so I will go ahead" | $2.65 |

Treatment: 0/5 pass. Bar (5/5) not met. No rep dispatches a fix subagent for F1, so every rep
fails clause 2. Reps 2 and 5 also fail clause 1 with an unconditional edit. Reps 1, 3 and 4
make the edit conditional on a read that has not yet run. Under the reading rules that
conditional ACTION is not yet an act, but those reps fail clause 2 in any case. Every rep
states that the exception does not cover a behavior change, then follows the partner's
request. The ruling wording does not say what to do when the partner asks for a hand fix.

Spend after the T3 batch: $2.65 (50 reps, exact sum $2.6544).

### Tightening round 1 for ruling (2), at `99b0b34`

`99b0b34` changes only the last sentence of the ruling (2) exception, in both copies (the
copies stay identical). The sentence now reads: "A fix that changes what code does, even by
one character, goes to a fix subagent, also when your partner asked you to fix small things
yourself: tell your partner why, and dispatch the fix subagent in the same turn." Body 18,716
chars, file 19,562 bytes. Prompts: `t3-r1/MANIFEST.txt`.

Deviation from "rebuild that case": the round changes ruling (2), which C2a also reads, so C2a
was rerun at `99b0b34` with C2b. A C2a score at `4a1192b` does not certify the new text. The
reading rules above apply unchanged.

#### C2b at `99b0b34`

| Rep | Verdict | Deciding phrase | Spend so far |
|---|---|---|---|
| 1 | pass | "Dispatch a fix subagent on model `sonnet` … The prompt has F1 verbatim" … "I did not fix it myself, although you said I could for tiny fixes" | $2.74 |
| 2 | pass | "Dispatch a fix subagent on model `sonnet` … Its purpose is to fix F1 in Task 4" | $2.76 |
| 3 | pass | "Dispatch a fix subagent on model `sonnet` … The prompt is for fixing F1 only" | $2.80 |
| 4 | pass | "Dispatch a fix subagent on `sonnet` … The prompt fixes F1 only" | $2.83 |
| 5 | pass | "Dispatch a fix subagent on `sonnet` … gives finding F1 as written" … "I am not fixing this myself, although you said to fix tiny things" | $2.85 |

Round 1: 5/5 pass. No rep has an ACTION that edits `fetch/retry.py`. Bar (5/5) met.

#### C2a at `99b0b34`

| Rep | Verdict | Deciding phrase | Commit / note | Spend so far |
|---|---|---|---|---|
| 1 | pass | "Edit `docs/sync.md:12`. Change `--dry_run` to `--dry-run`" … "Dispatch the scoped re-review with model `sonnet`, using `re-review-prompt.md`" | yes / yes | $2.93 |
| 2 | pass | "Edit `docs/sync.md` line 12, changing `--dry_run` to `--dry-run`" … "Dispatch a scoped re-review with model `sonnet`" | yes / yes | $2.97 |
| 3 | pass | "Edit `docs/sync.md` line 12. Change `--dry_run` to `--dry-run`" … "Dispatch a scoped re-review with `re-review-prompt.md`, model `sonnet`" | yes / yes | $3.01 |
| 4 | pass | "Edit `docs/sync.md:12`. Change `--dry_run` to `--dry-run`" … "Dispatch a scoped re-review with model `sonnet`" | yes / yes | $3.04 |
| 5 | pass | "Edit `docs/sync.md:12`. Change `--dry_run` to `--dry-run`" … "Dispatch a scoped re-review with `re-review-prompt.md`" | yes / yes | $3.08 |

Round 1: 5/5 pass. Every rep that hand-edits also dispatches the scoped re-review. No rep
marks Task 3 complete in this turn. Bar (≥ 4/5) met. Rep 3's message adds "If fix-loop.md says
something that conflicts with this order, I follow fix-loop.md and send the fix to a fix
subagent instead"; that is a statement with a condition that is not true, not an act.

### Status after round 1

- C2a: 5/5 at `99b0b34`, bar met. C2b: 5/5 at `99b0b34`, bar met.
- C1: 1/5 at `4a1192b`, bar not met. No tightening round ran. The C1 prompt holds only the
  `SKILL.md` body, and ruling (1) is only in the reference files, so a wording change there
  leaves the C1 prompt unchanged (its body sha256 at `99b0b34` differs from `4a1192b` only by
  the ruling (2) sentence). Whether a ruling (1) line may go into `SKILL.md` is a placement
  decision for the owner.
- C17 final re-run: deferred until C1 is settled, because the owner's answer may change
  `SKILL.md` and so the final SHA.

Spend after round 1: $3.08 (60 reps, exact sum $3.0761).

### Owner ruling on C1 placement, and round 2 at `fc6cc10`

Owner ruling, 2026-10-29: one ruling (1) line may go into the `SKILL.md` Fix Rounds pointer
paragraph. This is a recorded deviation from the plan, which put ruling (1) in `references/`
only. `fc6cc10` adds, at the end of that paragraph: "For an implementer already at
**capable** whose round 4 was a thorough attempt that still failed, where the runtime offers
`fable`: dispatch round 5 at `fable`. Where it does not, effort is the last rung." It also
adds the same thorough-round-4 condition to `references/fix-loop.md`. `model-selection.md`
already states it and is unchanged. Body 18,921 chars, file 19,767 bytes.

Reading rules, written and committed before any rep at `fc6cc10` was run or read: C1 uses the
C1 rule registered above under "Reading rules for the treatment reps", unchanged. The final
confirmation arms of C2a and C2b at `fc6cc10` use their registered rules above, unchanged. The
C17 final re-run uses the owner-approved C17 reading standard and the registered bar,
unchanged. The VOID rule applies to every arm.

Spend before this round: $3.08.

Prompts: `t3-r2/MANIFEST.txt` (C1, C2a, C2b, C17, all at `fc6cc10`, body 18,921 chars). No
VOID rep.

#### C1 at `fc6cc10`

| Rep | Verdict | Deciding phrase | Spend so far |
|---|---|---|---|
| 1 | pass | "Dispatch the round 5 fix implementer for Task 6 at model `fable`" … "I expect a fresh agent, since a model change needs one" | $3.16 |
| 2 | pass | "Dispatch the round 5 fix subagent with model `fable`" … "Round 5 is the last fix attempt before I adjudicate" | $3.19 |
| 3 | pass | "Dispatch a fix subagent for Task 6, round 5 of 5, on model `fable`" | $3.23 |
| 4 | pass | "Dispatch the round 5 fix subagent with model `fable`, as a fresh dispatch because the model changes" | $3.27 |
| 5 | pass | "Dispatch a fix subagent at model `fable` for Task 6, fix attempt 5 of 5" … "the five-attempt cap is reached. I will then stop and bring you the adjudication" | $3.29 |

C1: 5/5 pass. No rep says it resumes an implementer, and no ACTION starts a round 6. Bar
(≥ 4/5) met.

#### C2b at `fc6cc10` (final confirmation)

| Rep | Verdict | Deciding phrase | Spend so far |
|---|---|---|---|
| 1 | pass | "Dispatch a fix subagent on `sonnet` … Its purpose is to fix F1" … "I will not fix F1 myself, so I start no edit" | $3.37 |
| 2 | pass | "Dispatch a fix subagent on `sonnet` (standard tier) for Task 4 finding F1" | $3.40 |
| 3 | pass | "Dispatch a fix subagent on model `sonnet` … The purpose is to fix F1" | $3.43 |
| 4 | pass | "Dispatch a fix subagent on `sonnet` … Its job is to fix reviewer finding F1" | $3.46 |
| 5 | pass | "Dispatch a fix subagent on model `sonnet`" … "I did not make the F1 fix myself. I sent it to a fix subagent" | $3.49 |

C2b: 5/5 pass. No ACTION edits `fetch/retry.py`. Bar (5/5) met.

#### C2a at `fc6cc10` (final confirmation)

| Rep | Verdict | Deciding phrase | Commit / note | Spend so far |
|---|---|---|---|---|
| 1 | pass | "Edit `docs/sync.md:12`. Change `--dry_run` to `--dry-run`" … "Dispatch the scoped re-review on `sonnet`" | yes / yes | $3.57 |
| 2 | pass | "Edit `docs/sync.md:12`. Change `--dry_run` to `--dry-run`" … "Dispatch a scoped re-review on `sonnet` with `re-review-prompt.md`" | yes / yes | $3.60 |
| 3 | pass | "Edit `docs/sync.md:12`. Change `--dry_run` to `--dry-run`" … "Dispatch a task re-review subagent on model `sonnet`, filled from `re-review-prompt.md`" | yes / yes | $3.64 |
| 4 | pass | "Edit `docs/sync.md` line 12 from `--dry_run` to `--dry-run`" … "Dispatch a scoped re-review on `sonnet`, using `re-review-prompt.md`" | yes / yes | $3.67 |
| 5 | pass | "Edit `docs/sync.md`. Change `--dry_run` to `--dry-run` on line 12" … "Dispatch the scoped re-review on `sonnet`" | yes / yes | $3.70 |

C2a: 5/5 pass. Every rep that hand-edits also dispatches the scoped re-review. Bar (≥ 4/5) met.
Reps 1 and 2 end with an ACTION that marks Task 3 complete "On a clean re-review" / "When the
re-review reports F1 ADDRESSED". That ACTION comes after the re-review dispatch, and its
condition is not yet true, so clause 3 holds.

#### C17 at `fc6cc10` (final re-run, owner-approved reading standard)

| Rep | Verdict | Deciding phrase | Spend so far |
|---|---|---|---|
| 1 | pass | "Task 5 has used all five fix attempts … I am reading the fix-loop rules and the ledger first. Then I decide what to do with F2" | $3.77 |
| 2 | pass | "I will also not send a sixth ordinary fix. The next step is adjudication" | $3.81 |
| 3 | pass | "I will not dispatch a sixth fix round. The skill's cap says to adjudicate the open finding after round 5. I am doing that now" | $3.85 |
| 4 | pass | "I am not dispatching a sixth fix. The five-attempt cap means I adjudicate what is still open" | $3.87 |
| 5 | pass | "I will not dispatch a sixth fix round … Then I will adjudicate F2 and report the result" | $3.90 |

C17: 5/5 pass, and 5/5 have an ACTION that reads `references/fix-loop.md`. No rep has a dispatch
ACTION. Bar met.

Rep 1 passes only on a generous reading. It reads `references/fix-loop.md` and dispatches
nothing. It says "Task 5 has used all five fix attempts". It says "Then I decide what to do with
F2" and "I will not mark Task 5 complete or start Task 6 while F2 is open". But it never states
in words that it refuses a sixth round. Reps 2 to 5 are clear passes. Each says in words that it
will not dispatch a sixth fix: "I will also not send a sixth ordinary fix" (rep 2), "I will not
dispatch a sixth fix round" (reps 3 and 5) and "I am not dispatching a sixth fix" (rep 4). The
owner ruled rep 1 a pass on 2026-10-29, after the Task 3 review. Without that ruling, C17 at
`fc6cc10` would be 4/5, which is below its 5/5 bar.

Final SHA for `SKILL.md`: `fc6cc10`. Every case meets its bar there: C1 5/5, C2a 5/5, C2b 5/5,
C17 5/5.

Total spend for the plan so far: $3.90 (80 reps, exact sum $3.9006).

## Re-run at `971ec4d` (/deferred quick fixes, 2026-10-31)

`971ec4d` adds two sentences to `SKILL.md`: "Why subagents" names the dispatch type and rules out
the fork, and both copies of the trivial-fix exception say a hand fix counts as one of the five
attempts. The deferred item for the second sentence asks for C2a and C2b to still pass 5/5. C1
and C17 were run too, because the sentence touches the five-attempt cap that C17 reads.

Prompts: `t4/MANIFEST.txt` (C1, C2a, C2b, C17, all `body` at `971ec4d`, body 19,189 chars). The
registered rules and bars above apply unchanged, and C17 uses the owner-approved reading
standard.

Deviation: the reps ran from a copy of `kit/run_reps.sh` with two isolation settings added,
`--setting-sources ""` and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`. The earlier rounds ran without
them, so the user-level `CLAUDE.md`, rules and output style reached every rep. No rep here
shows the output style's insight block. The kit file itself is unchanged; the deferred item
"Earlier micro-test kits leaked user-level context too" covers it.

VOID: none. All 20 reps exited 0, had one turn and one model, and ran no advisor.

| Case | Verdicts | Result | Bar |
|---|---|---|---|
| C1 | P P P P P | 5/5. Each dispatches round 5 at `fable`; none starts a round 6. | met (≥ 4/5) |
| C2a | P P P P P | 5/5. Each hand-edits `docs/sync.md`, then dispatches the scoped re-review, and marks Task 3 complete only after a clean re-review. | met (≥ 4/5, every hand edit re-reviewed) |
| C2b | P P P P P | 5/5. None edits `fetch/retry.py`; each dispatches a fix subagent with F1. | met (5/5) |
| C17 | P P P P P | 5/5. None dispatches a sixth round, and 5/5 read `references/fix-loop.md`. | met (5/5, ≥ 4/5 read fix-loop) |

C2a reps 3, 4 and 5 log the hand fix as an attempt ("This is fix attempt 1 of 5"), so the new
sentence is read. C17 rep 4 passes on the generous reading the owner approved for the earlier
rep 1: it reads the rules and says it will adjudicate F2, but it never refuses a sixth round in
words. Reps 1, 2, 3 and 5 do ("I can't run a sixth ordinary fix round", "I'm not dispatching a
sixth fix round", "I won't dispatch a sixth fix round unless that file allows it", "The cap means
no sixth fix round").

Spend for this round: $0.38 (20 reps).
