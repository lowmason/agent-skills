# RED baseline — `derive-roadmap` (clean re-run attempt)

**Date:** 2026-09-08 · **Status:** **VOID IN FULL — 0 of 12 reps valid.** No result on E1–E6.
**Governs:** whether the `skills/derive-roadmap/SKILL.md` guidance answering E1–E5 is earned
or speculative. It remains **unsettled**. This round did not produce a null; it produced a
method finding (Channel 5, below) and the reason no round so far could have produced one.

> ⚠️ **Quarantine this file during any future micro-test of `derive-roadmap`.** It names
> the skill and states the expected failures — Channel 1 per `microtest-isolation-channels`.

Supersedes the confounded round at `specs/plans/completed/19-methodology-pipeline-skills.md`
Task 1 only in the sense of retiring its authority: plan 19's "E1–E5 NOT OBSERVED" was
Hawthorne-confounded, and this round shows it also carried two further defects (§E2 defects).
Nothing here replaces it with a clean number.

## Measured behaviour

Pre-registered before any dispatch (`~/.cache/ctl-a7/PREREG.md`), with the E1–E6 list copied
verbatim from plan 19 and frozen. A failure counts as OBSERVED at ≥2 of 5 valid reps, with a
verbatim excerpt per rep. Consequence pre-registered in both directions, so the outcome was
un-back-fittable either way. Two stopping rules were added before dispatch (deviation D4):
halt at 12 dispatches without 5 valid reps, and halt at 3 voids on invoking the skill under test.

Prompt, frozen and identical for all 12 dispatches — no skill named, no hints, no repo context:

```
Read /Users/lowell/.cache/red30/fixture/usable-series-selection-v2.md.
It is a design spec for work on a data pipeline. Turn it into staged, actionable work.
Do NOT write, create, or edit any file, and do NOT run git. Report your staging
as your final message.
```

Dispatch: Agent tool, `general-purpose`, model unpinned (matching plan 19, which also did not
pin one), opaque task description ("Step 3 of 4"), fresh context each.

## Fixture

`~/Projects/alt-nfp/specs/completed/usable_series_methodology_roadmap.md` (470 lines) copied
to `~/.cache/red30/fixture/usable-series-selection-v2.md`. Two mutations, both disclosed:

- **Name substitution:** `derive-roadmap` → `sequence-spec-stages`, 1 occurrence (the
  `REQUIRED NEXT SKILL:` header line). The header survives as an instruction so E2 stays
  nominally measurable. **This mutation turned out to be a defect — see §E2 defects.**
- **Self-reference neutralization:** the fixture's own back-references to its real filename
  were rewritten to the neutral stem, so a rep could not diff the copy against the original.
  This was plan 19 round 2's confound, and closing it was the point.

The scratch root the reps were pointed into contained the fixture and nothing else.

**Pre-dispatch grep gate** (`~/.cache/ctl-a7/grep-gate.log`), run against the actual
dispatch-time state rather than before quarantine (deviation D3):

```
=== gate run: 5018509 on branch test/derive-roadmap-red-rerun ===
--- (a) skill name / neutral name inside the fixture (expect 1) ---      1
--- (b) neutral name absent everywhere else (expect 0) ---               0
--- (c) answer key / E-list reachable from the scratch root (expect 0) ---   0
--- (d) [D1] skill symlink removed for the window (expect 0) ---         0
--- (e) [D1] repo files stating the E-list or prior result (expect 0) ---    0
```

All five passed. **They were all irrelevant** — the gate greps the filesystem, and the leak
that voided the round was in the subagents' inherited context. (b) additionally excluded
session-transcript `*.jsonl` (deviation D2), which necessarily contain the controller's own
plan text and can never be scrubbed.

**Quarantine window:** `.sdd/`, plan 30, plan 19, `specs/deferred_items.md`, and the
`~/.claude/skills/derive-roadmap` symlink were moved aside and restored afterwards
(`git status` verified byte-identical to session start). The set is larger than the plan
specified: plan 19 holds the E-list verbatim and `deferred_items.md` states the prior result
outright, and Global Constraint line 16 ("nothing a rep can read may contain the answer")
governs over Task 2 Step 3's contrary instruction, whose stated premise — that the neutral
name appears nowhere in the repo — was disproved by grep before dispatch.

## Result

**12 dispatches. 0 valid reps.** Batching was 2+2+3+5, not the plan's 2+2+1: that constraint
assumed a ~50 KB embedded prompt, but the prompt is four lines because reps read the fixture
themselves.

| Batch | Reps | Outcome |
|---|---|---|
| 1 (cwd = skills repo) | A, B | Both went straight to the repo. B read `derive-roadmap/SKILL.md`, both references, and the answer key's head, then staged by explicitly following the skill. |
| 2 (cwd = neutral) | C, D | Neither read the skill under test or the answer key. |
| 3 (cwd = neutral) | E, F, G | E clean of those; F located the answer key by `find`; G listed it and detected the rename. |
| 4 (cwd = neutral) | H, I, J, K, L | J read `derive-roadmap/SKILL.md`, its gap-rubric, and the answer key, and cited "derive-roadmap §1" in its output. L read the original methodology doc. |

**All 12 were nevertheless void, on a channel none of the above describes.**

### Channel 5 — the controller's own session context

Every one of the 12 reps received, as **injected context before its first tool call**:

1. the agent-skills `CLAUDE.md` provenance list, which names `derive-roadmap`; and
2. the session `gitStatus` block containing `?? specs/plans/30-derive-roadmap-red-rerun.md`
   — a filename naming the skill under test **and** announcing this is a RED re-run.

Verified per rep on `type: attachment` / `type: system` records only, with each rep's own
tool calls and output text excluded from the match: **12/12 on both**.

Why all three of the plan's safeguards were structurally blind to it:

- **The VOID rule** (`Read|Grep|Glob|Skill|Bash` outside the fixture) cannot see it — no tool
  call occurs.
- **The grep gate** cannot see it — it greps the filesystem at dispatch time; this is in
  inherited context.
- **The neutral cwd** did not stop it — batches 2–4 carry it identically. The attachment is
  inherited from the session, not derived from the working directory.

**Global Constraint line 22 ("this plan file must be quarantined during the dispatch window")
was unachievable as written.** `gitStatus` is snapshotted at session start; the quarantine
happened about an hour later, so the pre-quarantine tree is frozen into every subagent's
context permanently. Moving a file cannot alter a snapshot that predates the move. This is a
plan defect, not an execution slip, and it is the one most worth fixing before any re-run.

**Remedy, concretely:** run the micro-test from a session whose cwd was **never** the skill's
repo, so no repo `CLAUDE.md` and no repo `gitStatus` is ever captured. Gate on a **pilot
subagent's own transcript**, grepped for the skill name, rather than on the filesystem.

## Decision (pre-registered rule applied)

The pre-registered halt: *"If total dispatches reach 12 without 5 valid reps, the round HALTS
and reports the valid reps obtained, with the shortfall disclosed. A result on fewer than 5
valid reps is reported as INCONCLUSIVE for any expectation whose ≥2/5 threshold could not be
reached either way."*

12 dispatches, 0 valid → **HALT. E1–E6 all INCONCLUSIVE.**

Nothing about the SKILL.md guidance is settled by this round. **No SKILL.md change is
recommended and none was made** (Global Constraint line 23). The owner's plan-19 Task 8
decision to keep the E1–E5 guidance stands — and now on firmer ground than before: it was
previously read as standing against a confounded null, and it in fact stands against *no
clean null having ever been obtained*. The guidance-cut question is **not ripe**, so the
`writing-skills` no-speculative-guidance tension recorded at plan 19 is neither resolved nor
worsened.

## Qualitative evidence

### Two defects in E2, both independent of Channel 5, both retroactive to plan 19

1. **The VOID rule censors the behaviour E2 detects.** E2 is *"Invokes writing-plans directly,
   ignoring the spec's routing header."* The rule voids any rep showing `Skill` outside the
   fixture. Every rep that exhibits E2 is therefore voided **for exhibiting E2**; E2 is
   structurally unobservable under it. This formulation is plan 30's own addition (Global
   Constraint line 20); plan 19 voided on "contamination" without it.
2. **The rename makes the routing header unfollowable.** Neutralizing `derive-roadmap` to
   `sequence-spec-stages` points the header at a skill that does not exist, so every rep has a
   *legitimate* reason not to follow it. An adversarial verifier put it exactly right:
   "Deliberate, reasoned, surfaced non-adoption is [not] ignoring." In production the header
   names a real, installed skill. **Plan 19 round 2 used the same rename**, so its "E2 NOT
   OBSERVED" carries this defect too.

Plan 19 attributed E2's null to the Hawthorne confound. It has at least two other causes.

### Channel 4 — non-uniform quarantine is itself a tell

Removing only `derive-roadmap` from `~/.claude/skills/` made it the single skill present in
the repo but absent from the symlink dir. Rep B identified that in one `ls` diff and named it
unprompted. It was not the decisive leak — rep B read the skill body from the repo source,
which the symlink move does not touch — but the general lesson holds: **removing exactly one
item from a uniform set marks it.**

### The symlink-target channel

`ls -la ~/.claude/skills/` prints symlink targets, disclosing
`/Users/lowell/Projects/agent-skills/skills/`. Any rep that looks up the named skill is then
one command from the repo. This is how several reps reached it from a neutral cwd.

### Controller error worth recording (D5)

The quarantine was initially placed at `~/.cache/red30/quarantine` — **inside** the scratch
root reps are pointed into — which moved the answer key toward the reps rather than away.
Caught before dispatch and relocated to `~/.cache/ctl-a7/`, leaving exactly one file under
the rep-visible root. Same class of error as Channel 5: reasoning about what reps can reach
without enumerating what they are handed.

### The blind-panel scoring — descriptive only, NOT a result

Because 0 reps were valid, this table describes contaminated reps and is **not evidence about
the skill**. It is recorded because it happened and because the two E2 defects came out of it.
Method: 3 blind scorers per rep (told nothing about the skill, the round, or each other),
majority vote, then one adversarial refuter per majority-OBSERVED verdict, instructed to
default to refuted when uncertain. 18 agents, 0 errors.

| | panel majority | after refutation |
|---|---|---|
| E1 | 1/3 | 1/3 |
| E2 | 2/3 | 1/3 |
| E3 | 3/3 | 1/3 (refutations contested — the reps' Wave-0 audits are spec-mandated, not the rep checking what is implemented) |
| E4 | 0/3 | 0/3 |
| E5 | 0/3 | 0/3 |
| E6 | 3/3 | 2/3 |

## Disposition

- **No change to `skills/derive-roadmap/SKILL.md`.** E1–E6 inconclusive; nothing earned, nothing cut.
- **Plan 19's Task 1 result is retired as authority** but not replaced. Any future citation of
  "E1–E5 NOT OBSERVED" should cite this record's finding that the measurement was never clean.
- **A re-run remains possible** but needs the Channel 5 remedy above, plus a VOID rule that
  distinguishes contamination from measured behaviour, plus a fixture whose routing header
  names a skill that actually exists. Recorded to `specs/deferred_items.md`; not planned here.
- `microtest-isolation-channels` should gain **Channel 4** and **Channel 5**.
