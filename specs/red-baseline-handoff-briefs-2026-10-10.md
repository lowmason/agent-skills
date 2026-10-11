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

First pass on kit k-c, then the REFACTOR rounds (kit k-cr1 from `c7f45a8`, k-cr2 from `28a2b30`).

| Arm | Valid | Failing reps (k-c) | Per criterion (k-c) | After REFACTOR | Verdict |
|---|---|---|---|---|---|
| `c5a-pos` | 5 | 0 | none | | PASS |
| `c5a-neg` | 5 | 0 | none | 0 of 5 at k-cr1 and at k-cr2 | PASS |
| `c5a-pr` | 5 | 2 | F-handoff 2 | not rerun | PASS (owner ruling: prompt artifact) |
| `c5a-ep` | 5 | 2 | F-handoff 2, F-stamp 1 | k-cr1: 3 valid, 1 failing | PASS (owner ruling: UNSETTLED at 9 of 10 dispatches, one artifact) |
| `p5a` | 5 | 3 | F-handoff 1, F-stamp 1, F-timing 3, F-next 2 | k-cr1: 2 failing; k-cr2: 1 failing (F-next 1) | PASS |
| `c5b-pos` | 5 | 5 | F-line 5, F-scope 5 | k-cr1: 1 failing (F-amend 1) | PASS |
| `p5b` | 5 | 5 | F-line 5, F-scope 5 | k-cr1: 1 failing (F-amend 1, F-commit 1) | PASS |
| `c5b-part` | 5 | 5 | F-noroute 5, F-batch 3 | k-cr1: 0 failing | PASS |
| `c5b-neg` | 5 | 3 | F-fire 3 | k-cr1: 1 failing (F-fire 1) | PASS (owner ruling: fixture artifact) |

- Validation 8 (shape check): match. The stamp sits under the stage's entry, opens with the prescribed form, and names what later stages consume through the plan's Handoff section; `> Next: resume the roadmap.` follows; the plan carries a `## Handoff to later stages` section with bullets per consuming stage. alt-nfp-stats' stamp is a superset (it adds a colon and a summary).
- REFACTOR 1 (k-cr1, `c77d27c` and `c7f45a8`, 35 reps plus 5 replacements): the Handoff now records a deviation that execution later reverted; both executors run the roadmap step first and never resume or plan the next stage when asked to keep going; the resume treats a go-ahead as approving only the fresh session; a partition change goes to the owner as one question that names no routing. Verdicts: `c5b-pos`, `p5b`, `c5b-part` pass; `p5a` stays FAIL (2 of 5); `c5a-ep` UNSETTLED.
- REFACTOR 2 (k-cr2, `28a2b30`, 10 reps plus 2 replacements): the two remaining `p5a` failures had not loaded the executing skill, so the guard moved into the writing-plans body and the writing-plans and subagent-driven-development descriptions now also trigger on completing or merging an executed plan. Verdicts: `p5a` PASS (1 of 5), `c5a-neg` PASS (0 of 5, so no over-triggering). The `c5b` arms were not rerun on k-cr2.
- Owner rulings (2026-10-11, in `changes.log`; scores unchanged): `c5a-pr` F-handoff (two reps reverted the rename after their own turn-1 question, so the handoff correctly names the original function); `c5b-neg` F-fire at k-c and k-cr1 (reps found real roadmap holes, asked, and amended only after the owner's go-ahead); `c5a-ep` at k-cr1 (its one failing rep stalled on its own question and never merged).
- Scoring calls: `p5a` at k-cr2 F-next rests on a borderline reading, since four passing reps mention the next stage only to decline planning it; two of them stopped before the merge in turn 1, so a literal F-timing reading could fail them.
- Voids: 10 reps, on the path audit or an interrupted launch. At k-c, 1 (`c5a-ep`). At k-cr1, 7: three `c5a-ep` launches that ended in an execution error in turn 1, three `c5a-ep` reps and one `c5a-neg` rep that reached outside their repo (the user-level skill path, the reps directory). At k-cr2, 2 (a `p5a` skill-path read and a `c5a-neg` reps-directory read). Replaced within the 10-dispatch cap, except `c5a-ep` at k-cr1, which stopped at 9 dispatched with 3 valid.
- Cost: $60.50 for the phase ($32.91 first pass, $21.48 REFACTOR 1, $6.11 REFACTOR 2).
- Evidence, first pass, one line per failure mode:
  - `c5a-ep`: one Handoff bullet left out the deviation; another section read `None` after the rep reverted the rename.
  - `c5a-pr`: r088 and r089 name the original function, not the interim one.
  - `p5a`: no Handoff section (r098); S2b planned after the merge (r099); resume recommended before the merge (r100).
  - `c5b-pos`, `p5b`: every rep planned S2b in the session after the owner's go-ahead, then routed to execution rather than to writing-plans in a fresh session.
  - `c5b-part`: every rep named a route for the new stage inside the question; three asked more than one question.
  - `c5b-neg`: r107, r109 and r110 amended S2b or S3 after the owner's go-ahead.

Phase 3 is appended by Task 19.
