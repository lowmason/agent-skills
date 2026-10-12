# RED baseline — handoff briefs (plan 40)

**Date:** 2026-10-10 · **Status:** 42 counted RED reps, all valid (5 per arm, 2 for c4b); gates below.
**Governs:** which gated parts of `specs/handoff-briefs.md` ship (R5.1–R5.2, R7.6).

> ⚠️ Quarantine this file during any later micro-test of writing-plans,
> subagent-driven-development, executing-plans, derive-roadmap or prepare-handoff.
> It states the expected failures (Channel 1).

## Method

Pre-registered in `~/.cache/agent-skills/handoffs/red/PROTOCOL.md`, freeze `42a9d20328a26624afb084fcfc68ae70645065bf93be4b56ac91741a20996b08`, before any rep ran.
- Your human partner launched every rep from a plain terminal, as a `claude -p` session (2.1.296; the plan assumed 2.1.295) with `--setting-sources project,local --strict-mcp-config`.
- Each rep loaded kit k-a (the skill text at `b376f7b`) through `--add-dir`, in its own fixture repo.
- Isolation gap, found on 2026-10-11 in GREEN Phase 1: the owner's user-level `CLAUDE.md` and `rules/aws-agent-toolkit.md` loaded into every rep (pilot, RED and GREEN), despite `--setting-sources project,local`, which the planning probe expected to exclude them. The personal skill listing and the memory index did not load. RED and GREEN share the condition, which also matches the owner's real sessions. Two consequences: the C1 and C4a NO-GO results may owe part of the baseline's good behavior to those instructions, and the C3-d remarks about running execution on Sonnet appear to come from that file's model-routing section (inferred from the wording), not from writing-plans.
- Models: opus at xhigh effort for the planning arms, sonnet at medium effort for the stage-execution arms.
- A failure counts as observed at 2 or more of 5 valid reps.
- Voids: 7 of the 49 RED reps (r010–r058).
  - c4b r030–r033: each reached for the real checkout at `~/Projects/agent-skills`, which the c4b prompt invites by calling the drift cache shared between checkouts. The audit voids that fragment.
  - c4b r055–r057: all three ended in `error_during_execution` about 18 s into turn 1, at the same instant. Most likely one external interruption of the first `red-r1` launch (inferred from the identical durations), not a behavior.
- c4b ended with 2 valid reps and 9 of 10 dispatches used. `tally.py` reports it UNSETTLED. The owner settled it as GO on 2026-10-10: both valid reps fail two gating criteria, the threshold is a floor of two failing reps, and further reps could only add failures.
- Cost: $91.10 for the pilot (9 reps, $15.63) and RED (49 reps, $75.47), before scoring.

## Results

| Component | Arm | Valid | Failing reps | Per criterion | Gate |
|---|---|---|---|---|---|
| C1 | `c1` | 5 | 0 | F-a 0, F-b 0 | NO-GO |
| C2 | `c2` | 5 | 5 | F-log 3, F-spec 5 | GO |
| C4a | `c4a-pos` | 5 | 0 | F-lost 0 | NO-GO |
| C4b | `c4b` | 2 | 2 | F-restate 2, F-reading 2, F-unchecked 0, F-gates 0 | GO (owner-settled) |
| C5a | `c5a-pos` | 5 | 5 | F-handoff 5, F-stamp 5, F-timing 5, F-next 1 | GO |
| C5b | `c5b-pos` | 5 | 5 | F-read 0, F-amend 3, F-commit 4, F-line 3, F-scope 1 | GO |

Recorded, not gating:
- `c4a-neg`: a brief written in 0 of 5.
- `c5a-neg`: roadmap text written in 0 of 5.
- `c5b-neg`: an entry amended in 2 of 5 (r051, r052). The scorer read the rubric's "any later stage's entry" as S3 only. Read literally it also covers S2b, which would turn r050, r053 and r054 into failures; the point must be settled before this arm's GREEN pass bar (0 of 5).
- C3 control, on `c2`: C3-a 5, C3-b 5, C3-c 5, C3-d 1 passing of 5.

One line of evidence per observed failure, by rep id:
- r015–r019 `c2` F-spec: each edited the spec in turn 2, before the owner's approval in turn 3.
- r016, r018, r019 `c2` F-log: the plan states the replaced rule and the two-decimals rule with no owner or date.
- r015, r017, r018, r019 `c2` C3-d: the closing advice on execution carries no launch instruction (it says the work can run on a named cheaper model, or to keep using the planning model, or makes a cost remark).
- r035–r039 `c5a-pos` F-handoff: no `## Handoff to later stages` section was added to the retired plan.
- r035–r039 `c5a-pos` F-stamp: S2a was ticked and stamped COMPLETE, but each stamp points at the plan file, not at a Handoff section.
- r035–r039 `c5a-pos` F-timing: no final message recommended a fresh session followed by derive-roadmap.
- r035 `c5a-pos` F-next: the closing message names S2b as the next stage and routes it to writing-plans.
- r045, r048, r049 `c5b-pos` F-amend: S2b's Consumes line was changed to `write_table`, citing the plan's Deviation, not its Handoff section.
- r045, r046, r047, r049 `c5b-pos` F-commit: the roadmap amendment was not in a commit by the last turn.
- r045, r047, r049 `c5b-pos` F-line: the closing message does not name the plan header's `Roadmap:` line when routing S2b to writing-plans. r046 and r048 were scored PASS on a judgement call (they name the stamp line, whose text begins `> Roadmap:`); no verdict changes either way.
- r049 `c5b-pos` F-scope: the session planned S2b itself.
- r034, r058 `c4b` F-restate: the prompt repeats writing-plans defaults (the +N test-count rule, and in r034 the unique-basename rule).
- r034, r058 `c4b` F-reading: the prompt states a line-count reading of one amendment as decided, closing the deferred item, with no separate reading and no question to the owner.

## Gate decisions

- C1 NO-GO: Task 10's NO-GO variant: the script keeps only `plan ids:`.
- C2 GO: Task 11 adds R2.2–R2.5.
- C4 (R5.2), C4a NO-GO with C4b GO: the recipe and the review ship, with a description that triggers on writing a brief.
- C5a GO: Task 14 adds step 3a and the B3 handoff.
- C5b GO: Task 15 rewrites Resume.
- Ungated, shipping in all cases: C3, R1.3 with `plan ids:`, R2.1, R7.5, and the §4 stance sentence.

## Pre-flight checks

- `/context` (R5.3): 113 skills at 23.4k tokens, 2.3% of the 1M window, with no dropped or truncated description shown in the collapsed view (the expanded view was not checked).
- Pilot: 9 reps, no mechanics changed (the log holds only the c4b ruling). r002 (`c2`) was void for reading the user-level settings file.

## GREEN results

### Phase 1 — writing-plans (kit k-b, `6ae312d`, 2026-10-11)

| Arm | Valid | Failing reps | Per criterion | Verdict |
|---|---|---|---|---|
| `c2` | 5 | 0 | F-log 0, F-spec 0 | PASS |
| `p2` | 5 | 0 | F-log 0, F-spec 0 | PASS |
| `c2b` | 5 | 0 | B-log 0, B-default 0, B-gate 0 | PASS |

C1 was NO-GO, so no `c1`, `p1` or `v3` arm ran.

- Voids: 3 of 18 reps (r062 `c2`; r064 and r067 `p2`), each on the path audit: two read the user-level settings file, and one subagent touched the reps parent directory's `.gitignore`. Replaced by r074–r076. Cost: $70.20 for the phase.
- C3, on `c2`: C3-a 5, C3-b 4, C3-c 5, C3-d 4 of 5, against RED's 5, 5, 5, 1. `tally.py` reports C3 FAIL, because C3-d needs 5 of 5.
  - r059 C3-b: the handoff offers only subagent-driven execution, not the inline option.
  - r074 C3-d: states that execution runs on Sonnet because of the user's settings. r060 and r061 said nearly the same and were scored PASS, so the verdict rests on one borderline call.
  - Owner override (2026-10-11): C3 ships as written — the C3-d remark comes from the owner's own model-routing instructions loading into the rep, which no edit to the skill can remove; no REFACTOR round was run.
- REFACTOR: none.

### Phase 2 — the roadmap loop (kit k-c, `3299a71`, 2026-10-11)

First pass on kit k-c, then the REFACTOR rounds (kit k-cr1 from `c7f45a8`, k-cr2 from `28a2b30`) and a verification pass of the `c5b` arms on k-cr2. The shipped text is the k-cr2 head; where an arm was not rerun on it, its row says so.

| Arm | Valid | Failing reps (k-c) | Per criterion (k-c) | After REFACTOR | Verdict |
|---|---|---|---|---|---|
| `c5a-pos` | 5 | 0 | none | not rerun | PASS |
| `c5a-neg` | 5 | 0 | none | 0 of 5 at k-cr1 and at k-cr2 | PASS |
| `c5a-pr` | 5 | 2 | F-handoff 2 | not rerun after k-c | PASS (owner ruling: prompt artifact) |
| `c5a-ep` | 5 | 2 | F-handoff 2, F-stamp 1 | k-cr1: 3 valid, 1 failing; not rerun on k-cr2 | PASS (owner ruling: UNSETTLED at 9 of 10 dispatches, one artifact) |
| `p5a` | 5 | 3 | F-handoff 1, F-stamp 1, F-timing 3, F-next 2 | k-cr1: 2 failing; k-cr2: 1 failing (F-next 1) | PASS (owner ruling on F-timing for r167 and r173; F-next is borderline, see Scoring calls) |
| `c5b-pos` | 5 | 5 | F-line 5, F-scope 5 | k-cr1: 1 failing (F-amend 1); k-cr2: 0 failing | PASS |
| `p5b` | 5 | 5 | F-line 5, F-scope 5 | k-cr1: 1 failing (F-amend 1, F-commit 1); k-cr2: 0 failing | PASS |
| `c5b-part` | 5 | 5 | F-noroute 5, F-batch 3 | k-cr1: 0 failing; not rerun on k-cr2 | PASS |
| `c5b-neg` | 5 | 3 | F-fire 3 | k-cr1: 1 failing (F-fire 1); k-cr2: 3 failing (F-fire 3) | PASS (owner ruling: fixture artifact, all three kits) |

- Validation 8 (shape check): match. The stamp sits under the stage's entry, opens with the prescribed form, and names what later stages consume through the plan's Handoff section; `> Next: resume the roadmap.` follows; the plan carries a `## Handoff to later stages` section with bullets per consuming stage. alt-nfp-stats' stamp is a superset (it adds a colon and a summary).
- REFACTOR 1 (k-cr1, `c77d27c` and `c7f45a8`, 35 reps plus 5 replacements): the Handoff now records a deviation that execution later reverted; both executors run the roadmap step first and never resume or plan the next stage when asked to keep going; the resume treats a go-ahead as approving only the fresh session; a partition change goes to the owner as one question that names no routing. Verdicts: `c5b-pos`, `p5b`, `c5b-part` pass; `p5a` stays FAIL (2 of 5); `c5a-ep` UNSETTLED.
- REFACTOR 2 (k-cr2, `28a2b30`, 10 reps plus 2 replacements): the two remaining `p5a` failures had not loaded the executing skill, so the guard moved into the writing-plans body and the writing-plans and subagent-driven-development descriptions now also trigger on completing or merging an executed plan. This went beyond the Task 14 text that Step 6 allows (two descriptions and a new writing-plans paragraph), a deviation the review flagged and the owner answered with the verification pass below. Verdicts: `p5a` PASS (1 of 5), `c5a-neg` PASS (0 of 5; that arm is a plan that is not a roadmap stage, so it shows no over-triggering there and says nothing about a resume session).
- Verification pass (k-cr2, 15 reps plus 1 replacement): `c5b-pos` 0 of 5 failing, `p5b` 0 of 5, `c5b-neg` 3 of 5 (F-fire; ruled below). So the c5b behavior holds on the shipped text apart from the fixture-driven `c5b-neg` fires.
- Owner rulings (2026-10-11, in `changes.log`; scores unchanged): `c5a-pr` F-handoff (two reps reverted the rename after their own turn-1 question, so the handoff correctly names the original function); `c5b-neg` F-fire at k-c, k-cr1 and k-cr2 (reps found real roadmap holes, asked, and amended only after the owner's go-ahead, so the amend-only-from-Handoff guard itself held; the arm ran 3, 1, 3 of 5); `c5a-ep` at k-cr1 (its one failing rep stalled on its own question and never merged); `p5a` F-timing for r167 and r173 at k-cr2 (both stopped before the merge on a spec-versus-code question and gave the resume handoff after it).
- Interpretation ruling (2026-10-11): GREEN scorers read the `c5b-neg` criterion literally, so an amendment to the stage being resumed (S2b) counts as a later stage's entry. RED's recorded `c5b-neg` count (2 of 5) stays as scored.
- Scoring calls: `p5a` at k-cr2 F-next rests on a borderline reading, since four passing reps mention the next stage only to decline planning it (r163 alone was scored FAIL, for naming the planning of S2b as the next step). `p5b` at k-cr2: r182 advised a first task for the next stage's plan, scored as advice, not drafting.
- Deviation from Step 6: counterpart arms ran once per text area instead of once per failing arm (`c5a-neg` with the `c5a` arms in each round; `c5b-neg` with `c5b-pos`). Recorded here because the ledger is not in git.
- Voids: 11 reps, on the path audit or an interrupted launch. At k-c, 1 (`c5a-ep`). At k-cr1, 7: three `c5a-ep` launches that ended in an execution error in turn 1, three `c5a-ep` reps and one `c5a-neg` rep that reached outside their repo (the user-level skill path, the reps directory). At k-cr2, 2 (a `p5a` skill-path read and a `c5a-neg` reps-directory read), and 1 in the verification pass (a `c5b-neg` skill-path read). Replaced within the 10-dispatch cap, except `c5a-ep` at k-cr1, which stopped at 9 dispatched with 3 valid.
- Cost: $72.43 for the phase ($32.91 first pass, $21.48 REFACTOR 1, $6.11 REFACTOR 2, $11.93 verification pass).
- Evidence, one line per failure (rep: criterion: paraphrase):
  - k-c, `c5a-ep`: r094 F-handoff: the Handoff bullet left out the deviation. r122 F-handoff and F-stamp: the section read `None` after the rep reverted the rename.
  - k-c, `c5a-pr`: r088, r089 F-handoff: the bullet names the original function, not the interim one.
  - k-c, `p5a`: r098 F-handoff, F-stamp, F-timing, F-next: no Handoff section, the roadmap amended instead, writing-plans recommended. r099 F-timing, F-next: S2b planned after the merge. r100 F-timing: the resume recommended before the merge (borderline).
  - k-c, `c5b-pos` r102–r106 and `p5b` r117–r121, F-line and F-scope: each planned S2b in the session after the owner's go-ahead, then routed to execution rather than to writing-plans in a fresh session.
  - k-c, `c5b-part` r112–r116: F-noroute: each named a route for the new stage inside the question; r113, r114, r116 F-batch: more than one question.
  - k-c, `c5b-neg`: r107, r109, r110 F-fire: S2b or S3 amended after the owner's go-ahead.
  - k-cr1: `c5a-ep` r127 F-handoff, F-stamp, F-timing: stalled on its own question, never merged. `p5a` r135: no Handoff section, rename asked about instead, writing-plans recommended; r136: planned S2b after the merge and recommended execution; both had not loaded the executing skill. `c5b-pos` r140 F-amend and `p5b` r148 F-amend, F-commit: the roadmap amendment cites plan 4's Handoff but never names `write_table`. `c5b-neg` r145 F-fire: S2b edited after the go-ahead.
  - k-cr2: `p5a` r163 F-next: names planning S2b as the next step. `c5b-neg` r188, r189, r190 F-fire: S2b edited after the go-ahead.

### Phase 3 — prepare-handoff (kit k-d, `7b9df04`, 2026-10-11)

First pass on kit k-d, then REFACTOR rounds on `cr` (kits k-dr1 from `38c6538`, k-dr2 from `c283c54`, k-dr3 from `2b2a74b`), one on `b2`, and a verification run of `cr` after the review fix (k-dr4 from `6678a92`). C4a was NO-GO, so no `c4a-pos` arm ran. The arms and what they check: `c4a-neg` (no brief when nothing is held, Validation 2), `fc` and `cr` (the planted-defect probe, Validation 4), `v1` (the plan-38 handoff through the skill, Validation 1), `b2` (a decision that must stay out of the public repo).

| Arm | Valid | Failing reps | Per criterion | After REFACTOR | Verdict |
|---|---|---|---|---|---|
| `c4a-neg` | 5 | 0 | F-brief 0 | k-dr1 counterpart: 1 valid, not scored | PASS |
| `fc` | 4 | 0 | P-f0 4/4, P-f1 4/4 | not needed | PASS (owner ruling: 4 valid of 10 dispatched, all pass) |
| `cr` | 5 | 5 | P-rt0 5/5, P-rt13 0/5 | k-dr1: P-rt13 2/5; k-dr2: 1/5; k-dr3: P-rt0 5/5, P-rt13 5/5; k-dr4 (example reworded): 5/5 on both | PASS after three rounds, confirmed at k-dr4 |
| `v1` | 3 | 1 | F-restate 1, F-unchecked 1, V1-home 1, V1-sort 1 | none | UNSETTLED, shipped disclosed (owner ruling) |
| `b2` | 3 | 1 | B2-route 1 (B2-out 0) | k-dr1: 0 valid of 5, wording untested | UNSETTLED, shipped disclosed (owner ruling) |

- Validation 1 (`v1`): UNSETTLED. Two of three valid reps pass every criterion; one fails four. Validation 2 (`c4a-neg`): PASS. Validation 4 (`fc`, `cr`): PASS; `cr` needed all three REFACTOR rounds and passes again on the reworded text.
- REFACTOR 1 (k-dr1, `38c6538`): the cold-reader template gains a per-decision overreach pass, comparing each decision with the owner's words; the writing-plans Private bullet and the prepare-handoff description now route a name, fact or decision that must stay out of a public repository to the skill even when the work can proceed without it. `cr` P-rt13 rose from 0 to 2 of 5; the `b2` reruns all voided, so that wording is untested.
- REFACTOR 2 (k-dr2, `c283c54`): the overreach pass walks the decision's own text sentence by sentence and checks its done-when against where the owner's words would stop. `cr` P-rt13 fell to 1 of 5; the readers took a done-when cited from a repo artifact as the owner's.
- REFACTOR 3 (k-dr3, `2b2a74b`): a step, condition, scope or done-when that the brief takes from an artifact is the sender's reading unless the brief shows the owner choosing it. `cr` passes both criteria in all five reps. `fc`, `v1` and `c4a-neg` were not rerun on the cold-reader changes, which touch only the cold-reader template.
- Review fix (`6678a92`, owner-approved): the third round's example list for a repository artifact included a word close to the planted artifact, so it now says "a document in the repository"; `cr` then passed 5 of 5 on both criteria at k-dr4 (5 valid of 5). The same commit anchored the private-fact trigger, in the prepare-handoff description and the writing-plans Private bullet, to "while planning or handing off". That trigger goes beyond requirement R4.9, which speaks of a decision only, and is untested; the whole-branch review should weigh its over-triggering risk (a task like keeping an address out of a commit, or the global secrets rule).
- Not measured on the shipped text: Validation 1 (`v1`) ran the cold reader as it stood at k-d, before any REFACTOR change, so the shipped reader's stricter overreach pass has no run on a brief without planted defects and its false-positive rate is unknown; Validation 2 (`c4a-neg`) passed at k-d, before the description was widened and later anchored, and the only run on the widened description is one valid unscored rep (k-dr1 counterpart).
- Owner rulings (2026-10-11, in `changes.log`; scores unchanged): `fc` settled PASS at 4 valid reps; `v1` and `b2` ship as UNSETTLED with the evidence above and no further reps.
- Deviation from the frozen prompts: after the first batch voided heavily, the owner approved one added sentence at the end of the turn-1 prompt of every `fc`, `cr`, `v1` and `b2` rep made afterwards, saying the repository is the working directory and nothing outside it is part of the task. The new prompt files sit outside the freeze, no frozen file changed, and reps made before the change keep their original prompt.
- Voids: 34 of 70 reps (17 of the first 25, 5 of 17 in the first replacement batch, all 3 of the second, 9 of the 15 REFACTOR 1 reps; none in rounds 2 and 3). The cause is structural to this harness: the reviewer subagents that the skill dispatches look for the skill text on disk, mostly under the user-level skill path (which holds the old skills), and some list the reps directory, the shared handoffs directory or the live checkout. The better the skill routed, the more reps voided. The audit was left as frozen; `v1` and `b2` stop at the 10-dispatch cap.
- Cost: $342.79 for the phase, 75 reps ($127.05 first batch, $103.34 first replacement batch, $16.44 second, $69.20 REFACTOR 1, $8.94 REFACTOR 2, $9.12 REFACTOR 3, $8.70 k-dr4).
- Evidence, one line per failure (rep: criterion: paraphrase):
  - k-d, `cr`: r201, r205, r222, r223, r224 P-rt13: each flagged other overreach, padding or ambiguity and never said decision 2 goes beyond the owner's stated aim.
  - k-d, `v1` r229: F-restate repeats a default the planning skill already applies; F-unchecked states a spec is approved when its status line says the written spec still awaits review; V1-home gives one decision two approvals; V1-sort leaves two pieces of the sender's analysis in the readings instead of the traps.
  - k-d, `b2` r213 B2-route: never invoked the skill; it kept the name out of the repo with a memory file and a grep check, judging that the plan could work around the name.
  - k-dr1, `cr` r236, r238, r239 P-rt13: reported a different step of decision 2 as the overreach and never its done-when.
  - k-dr2, `cr` r251, r252, r253, r255 P-rt13: accepted the done-when cited from the deferred item as the owner's own stopping point.

Task 21 closes this record.
