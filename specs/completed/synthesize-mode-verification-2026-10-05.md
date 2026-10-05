# Synthesize-mode scenario verification — `describe-critique-methodology`

**Date:** 2026-10-05 · **Status:** `VOID: 0 of 5 reps valid; replacement reps not run (owner decision)`
**Governs:** whether `describe-critique-methodology` Synthesize mode's triage ordering, locator
discipline and derive-roadmap handoff hold in practice. It remains **unverified**. This run
produced no verdict on B1, B2 or B3 and asserts no skill defect: the void is a kit-isolation
problem (below).

> This file names the skill, the behaviours under test and the pass bar, and it sits in
> `specs/completed/`, the directory every rep listed. Its name matches the plan's VOID
> pattern `specs/completed/synthesize-mode-*`. Any re-run's isolation must cover it (Channel 1
> per `microtest-isolation-channels`).

Executes `specs/plans/36-synthesize-mode-scenario-verification.md` (Tasks 1-4). Source: the
2026-07-26 deferred item "Synthesize mode has no scenario verification (spec Req 13,
gate-deferred)" from plan 18-methodology-pipeline-skills. The behaviour under test is specified
in `skills/describe-critique-methodology/SKILL.md` § Synthesize mode and
`skills/describe-critique-methodology/references/spec-synthesis.md`.

## Fixture

Two real pre-skill files from alt-nfp-model, copied byte for byte into each rep's scratch repo
(`~/.cache/nfp-series/rep-<n>`, one commit, plus a one-line `# nfp-series` README):

- `/Users/lowell/Projects/alt-nfp-model/specs/completed/calibration_methodology.md` (765 lines),
  the methodology description.
- `/Users/lowell/Projects/alt-nfp-model/specs/completed/calibration_methodology_review.md`
  (102 lines), the external critique. Pre-skill shape: it carries no C-numbers (a grep for
  `\bC[0-9]+` finds none) and a foreign structure (TL;DR, Key Findings, Details A-D,
  Recommendations, Caveats), so a synthesis has to declare its own locator scheme.

**Coverage key: 50 points**, frozen before any rep ran and held outside the repo at
`~/.cache/ctl-q9/coverage-key.md`. It was built from the critique's Key Findings bullets
(KF1, KF2, KF3, KF3a, KF3b, KF4 ...), its Details points (A-D), its numbered Recommendations,
and its change-asking Caveats, in document order, with distinct claims not merged. One point,
C3c (pay-frequency composition, Details C gap 3), was added at Task 1 review, which moved the
count from 49 to 50. The key was never used for scoring in this run, because no rep was valid.

The kit (`~/.cache/ctl-q9/` and `~/.cache/nfp-series/`) is outside the repo. It is rebuildable
from plan 36 Task 1.

## Pre-registration (fixed before any rep runs)

**The three turns.** These are the exact texts, also written to `~/.cache/ctl-q9/prompts/`:
- T1, the skill's own re-entry utterance from `SKILL.md` Describe step 4: `The critique is back — use describe-critique-methodology (synthesize mode) on specs/calibration_methodology_review.md`
- T2: `Thanks. On every needs-user-adjudication point, go with your recommendation, or with the critique's position where you gave none. Go ahead and finish the spec.`
- T3: `Approved — the spec looks good.`

**Behaviours and how each is scored** (per valid rep; pass/fail):
- **B1 — triage before spec text.** M1 (mechanical): the first assistant message carrying a markdown table with a verdict column comes before the first write to the new spec file in the transcript. This holds even when both happen in one turn, because a first-pass critique may leave no question to wait on. Manual:
  - R1: the rep states whether the critique was adjudicated or a first pass, above the table.
  - R2: the table covers every critique point in the coverage key (Task 1 Step 5).
  - R3: every needs-user-adjudication question is in the table's message, with none asked in a later message.
  
  B1 passes when M1, R1, R2 and R3 all hold.
- **B2 — locator discipline.** M3 (mechanical): before the Requirements section, the spec names both fixture files. Manual:
  - R4: a Design provenance paragraph declares a locator scheme. The critique has no C-numbers, so a declared custom scheme is the expected behaviour.
  - R5: every requirement carries at least one locator in that scheme.
  - R6: five locators sampled per rep each resolve to a real section or point of the fixture.
  - R7: no requirement without a locator, unless it is explicitly routed to brainstorming.
  
  B2 passes when M3 and R4–R7 all hold.
- **B3 — routing header and handoff.** Mechanical:
  - M2: the spec's first non-blank line after its title is the verbatim routing header from `spec-synthesis.md`, with whitespace normalised.
  - M4: no roadmap or plan file exists after T3.
  - M5: the final assistant message names derive-roadmap and recommends a fresh or new session.
  
  Manual R8: the rep stops after the handoff, never drafting a roadmap, stages or a plan in chat. B3 passes when M2, M4, M5 and R8 all hold.

**Pass bar:** each behaviour holds in at least 4 of 5 valid reps. Below that, the behaviour is a recorded failure.

**VOID rule.** A rep is void if its transcript shows it reading this plan's context or a worked synthesis of its own fixture:
- A tool input naming, or a tool result carrying, the full path of any of:
  - agent-skills `specs/deferred_items.md`
  - `specs/plans/`
  - `specs/completed/methodology-pipeline-skills.md`
  - `specs/completed/audit_9_2_26.md`
  - `specs/completed/red-baseline-*`
  - `specs/completed/synthesize-mode-*`
  - `.claude/`
  - anything under `~/Projects/alt-nfp-model`, `~/Projects/alt-nfp-stats*` or `~/Projects/archive/alt_nfp`
  - the control directory
- Or injected context (`attachment` / `system` records) carrying any Channel-5 marker: `36-synthesize-mode`, `synthesize-mode-verification`, `scenario verification`, `ctl-q9`.

Reading the skill's own files, and reading other `specs/completed/` exemplars, is required behaviour and never voids: `spec-synthesis.md` tells the rep to read two exemplars there. A bare directory listing that shows file names does not void. Reading or grepping the content of a listed VOID path does.

**Replacement:** void reps are replaced from rep-6 upward, up to 10 reps in total. With fewer than 5 valid reps after rep-10, stop: record the run as void and report.

## Dispatch

**Owner-run, from a plain terminal, not from a Claude Code session.** Two reasons. Channel 5: a
rep started inside this repository's Claude Code session would inherit its `CLAUDE.md` and
`gitStatus`, and no file quarantine can close that. And the isolation guard: a worktree-isolated
session refuses to launch `claude -p` with a prompt in another directory (verified 2026-10-03).
Each rep is a fresh `claude -p` session with `--session-id` / `--resume` across the three
scripted turns, `--permission-mode acceptEdits`, rooted in its own scratch repo. The control
directory (prompts, scripts, results, grader) is outside every rep repo.

**Batching.** Rep-1 ran alone as the pilot (12m53.9s). Reps 2-5 then ran in parallel as one
batch (17m39.4s).

**Model and effort.** All five transcripts carry `message.model` = `claude-opus-5-5` (the
ledger records Claude Code 2.1.289). Assistant records in all five carry the fields
`effort: "xhigh"` and `perTurnEffort: "xhigh"`; no other effort value appears in any of them.
Per the controller's ledger (not re-verified here), the reps ran with the `explanatory` and
`learning` output-style SessionStart hooks, the advisor tool on, iterm2 cc-status hooks, and the
global `~/.claude/CLAUDE.md` only (no project memory).

**Pilot audit (rep-1), method as the ledger states it.** The injected-context audit was a
dedup-and-marker-scan, not a full line-by-line read of the 395 KB dump. 141 injected records
deduped to 77 unique bodies. Every unique body under 1.3 KB was read whole. The large blobs
(a 74 KB skill listing, a 60 KB prompt snapshot, and 5-10 KB hook and instruction bodies) were
marker-scanned and their heads read. The five skill-listing marker hits were checked in context
and are skill descriptions (bayesian-workflow, executing-plans, subagent-driven-development,
tech-debt, writing-skills). No plan, item or behaviour marker appeared (`36-synthesize`,
`ctl-q9`, `deferred_items` and the like), only expected content. The grader's `inherited_hits`
was `[]` and `permission_denials` was 0 for all five reps.

## Validity

**0 of 5 reps are valid.** All five are void under the pre-registered VOID rule, by the same
mechanism: a `Read` of `agent-skills/specs/completed/methodology-pipeline-skills.md`, the design
spec of the skill under test, which the rule names. I re-traced each transcript. "Record" is the
0-based line index in the session JSONL (the ledger's "event 148" for rep-1 is this index);
"event" is `grade.py`'s item counter over non-attachment, non-system records.

| Rep | Found the exemplars by | Void tool call (record / event) |
|---|---|---|
| 1 | `Glob` `specs/completed/*.md` in `/Users/lowell/Projects/agent-skills` (rec 113, ev 37) | `Read` `{"file_path": "/Users/lowell/Projects/agent-skills/specs/completed/methodology-pipeline-skills.md"}` (rec 148, ev 47). Before it, `Grep` count mode over `agent-skills/specs` (rec 139, ev 45), whose result carries both `methodology-pipeline-skills.md:6` and `plans/completed/38-claude-code-drift-automation.md:7` |
| 2 | `Glob` `specs/completed/*.md` (rec 93, ev 26) | `Read` of the same path, no offset (rec 103, ev 30) |
| 3 | `Glob` `*.md` in `.../specs/completed` (rec 92, ev 24) | `Read` of the same path, no offset (rec 105, ev 31) |
| 4 | `Glob` `specs/completed/*.md` (rec 109, ev 33) | `Read` of the same path, no offset (rec 120, ev 38) |
| 5 | `Glob` `specs/completed/*.md` (rec 99, ev 30) | `Grep` content mode over `specs/completed` with glob `{methodology-pipeline-skills,readonly-agent-guard,skill-model-pin-removal}.md` (rec 130, ev 41), whose result carries lines of `methodology-pipeline-skills.md`; then `Read` with `offset 1, limit 140` (rec 143, ev 46) and `offset 250, limit 140` (rec 147, ev 48) |

Rep-5 read lines 1-140 and 250-376 of the 376-line file, not every line, but that is a Read of
a named VOID path and voids it. For reps 1-4 the Read result was 28,298 characters, the whole
file.

**Exemplars each rep opened** (the grader's `exemplars_read`, from `Read` inputs under
`agent-skills/specs/completed/`):

- Reps 2, 3, 4: `calibration-check-verdicts.md` and `methodology-pipeline-skills.md`.
- Rep-1: those two plus `tune-hyperparameters.md`.
- Rep-5: those two plus `skill-model-pin-removal.md` and `track-model-experiments.md`.

`methodology-pipeline-skills.md` is the only exemplar the VOID rule names. Every rep opened it,
and 5 of 5 also opened `calibration-check-verdicts.md`.

**Cause.** `spec-synthesis.md` tells a rep to read two retired exemplars in `specs/completed/`
without naming them (quoted under Qualitative evidence). The directory that the skill points at
holds that skill's own design spec. Five of five reps chose it.

Rep-1 had already `Read` two other exemplars (`calibration-check-verdicts.md`, ev 40, and
`tune-hyperparameters.md`, ev 41) when it ran the count-mode `Grep` at rec 139. That result
(rec 144) ranks `specs/completed/methodology-pipeline-skills.md:6` against
`specs/plans/completed/38-claude-code-drift-automation.md:7`, and the other `specs/completed/`
entries it lists are `refine-subagent-driven-development.md:1` and
`delegation-frontmatter-rollout.md:2`. The controller's ledger reads the pick as name-driven,
because the Grep's higher count (7) belonged to a different file. But `38-claude-code-...`
is a plan under `specs/plans/completed/`, not a candidate exemplar from `specs/completed/`,
and among the `specs/completed/` entries `methodology-pipeline-skills.md` has the highest
count (6, against 2 and 1). So the pick is as consistent with a count-driven ranking as with a
name-driven one, and this trace cannot tell them apart. It is n=1: the other four reps ran no
such ranking. This is a kit-isolation problem: the exemplar step is a documented part of the skill's procedure, and
the plan quarantines no file, so nothing kept the reps from the skill's own design spec. It
does not show a defect in the skill.

**The three VOID rulings, fixed 2026-10-05 before the batch** (post-hoc rulings are not
allowed):

1. A `Grep` in any output mode whose result carries a VOID path name voids the rep, because it
   searched that path's content. `Glob` or `ls` listings that only show names do not.
2. A bare listing of `specs/plans/` that shows the plan-36 file name does not void. Any later
   `Read` or `Grep` of it does. `grade.py` flags it mechanically, so the flag is overridden and
   recorded.
3. `bash_write_suspect` entries that are a rep's own heredoc `git commit` calls are false
   positives and never count against a rep.

**False-positive notes.** `grade.py` lists `Projects/agent-skills/specs/completed/audit_9_2_26.md`
and `.../red-baseline-` in `void_hits` for all five reps. Those come from the `Glob` result
listing in each rep (the 2,874-character file listing returned to the `specs/completed/*.md`
Glob), which shows names only and does not void under the rule. Those two are false positives.
Rep-1's `specs/plans/` hit is different, and is not a false positive: it comes from the
count-mode `Grep` result (rec 144), which carries `specs/completed/methodology-pipeline-skills.md`
and `specs/plans/completed/...` paths. Ruling 1 was fixed after the pilot and before the batch;
at the pilot the controller treated that Grep as counts-only. Under ruling 1 as it stands,
that Grep would itself void rep-1. Rep-1 is void by the `Read` at rec 148 either way. The
`bash_write_suspect` entries in reps 1-5 are heredoc `git commit -F -` or `git commit -m` calls
(ruling 3), plus rep-3's `cat README.md; ... ls -la .../specs/completed/` command, which writes
nothing.

## Result

Mechanical checks M1-M5 were true in all five reps. **They are UNSCORED: every rep is void, and
the reps had read the skill's own design spec, so these numbers are observations, not evidence
about any behaviour.**

| Rep | Void cause | M1 | M2 | M3 | M4 | M5 (all UNSCORED, void) | Write turn | Spec path | Exemplars read |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `Read` of `methodology-pipeline-skills.md` (rec 148) | true | true | true | true | true | 2 | `specs/calibration.md` | calibration-check-verdicts, methodology-pipeline-skills, tune-hyperparameters |
| 2 | `Read` of the same file (rec 103) | true | true | true | true | true | 2 | `specs/calibration.md` | calibration-check-verdicts, methodology-pipeline-skills |
| 3 | `Read` of the same file (rec 105) | true | true | true | true | true | 2 | `specs/calibration.md` | calibration-check-verdicts, methodology-pipeline-skills |
| 4 | `Read` of the same file (rec 120) | true | true | true | true | true | 2 | `specs/calibration.md` | calibration-check-verdicts, methodology-pipeline-skills |
| 5 | `Grep` content (rec 130), then two offset `Read`s (rec 143, 147) | true | true | true | true | true | 2 | `specs/calibration.md` | calibration-check-verdicts, methodology-pipeline-skills, skill-model-pin-removal, track-model-experiments |

R1-R8 and B1-B3 were not scored, because no rep was valid. The manual rubric was not applied to
any rep's output.

## Decision

No B1, B2 or B3 verdict was reachable: the pass bar needs at least 4 of 5 valid reps, and there
were none. Under the plan's rule the run is **VOID**, and nothing about
`describe-critique-methodology` Synthesize mode is settled either way. No skill change is
recommended and none was made (Global Constraint: this plan edits no skill).

The plan's replacement rule (reps 6-10, needing 5 valid) was **not run**. The owner decided on
2026-10-05 to stop at 5 reps and record the run void, because 0 of 5 reps were valid, the
mechanism was identical in all five, so the odds that a replacement rep would avoid the same
`Read` were judged near zero. This skips the plan's Step 3
replacement dispatch and is an owner-approved deviation.

## Qualitative evidence

**The instruction that sends the rep to the exemplars**, verbatim from
`skills/describe-critique-methodology/references/spec-synthesis.md` (the "Spec format"
paragraph, lines 29-35, the sentence ending at line 35), with the line breaks joined:

> Do not reinvent the skeleton — before writing your first synthesized spec, read two retired
> exemplars in the agent-skills repo's `specs/completed/` directory (that repo owns the house
> format; this file cites it rather than restating it).

It names neither exemplar, so a rep has to list the directory and choose.

**The tool inputs that voided the reps** (verbatim, from the transcripts):

- Listing (all five, same result, 2,874 characters; the pattern and path vary by rep):
  `{"pattern": "specs/completed/*.md", "path": "/Users/lowell/Projects/agent-skills"}`
  (reps 1, 2, 4, 5); `{"pattern": "*.md", "path": "/Users/lowell/Projects/agent-skills/specs/completed"}` (rep-3).
- Void read (reps 1-4):
  `{"file_path": "/Users/lowell/Projects/agent-skills/specs/completed/methodology-pipeline-skills.md"}`.
- Rep-5's void content search:
  `{"pattern": "^#{1,3} |\\(chosen\\)|\\(rejected\\)|\\(open", "path": "/Users/lowell/Projects/agent-skills/specs/completed", "output_mode": "content", "glob": "{methodology-pipeline-skills,readonly-agent-guard,skill-model-pin-removal}.md"}`,
  then `{"file_path": ".../methodology-pipeline-skills.md", "offset": 1, "limit": 140}` and
  `{"file_path": ".../methodology-pipeline-skills.md", "offset": 250, "limit": 140}`.
- Rep-1's ranking search (the count-mode Grep):
  `{"pattern": "\\(chosen\\)|\\(rejected\\)|\\(open", "path": "/Users/lowell/Projects/agent-skills/specs", "output_mode": "count"}`.
  Its result begins `.../specs/completed/methodology-pipeline-skills.md:6` and
  `.../specs/plans/completed/38-claude-code-drift-automation.md:7`.

**What the void spec contains.** Rep-5's `offset 250` read returned the spec's
"Amendment A — 2026-07-26: gold-master reconciliation (Reqs 3, 4)", which describes a
hand-built synthesized spec in alt-nfp (`specs/usable_series_methodology.md` and its
`_review.md`) as a gold master for Synthesize mode. That is why a read of this file is a worked
example of the behaviour under test, not a neutral house-format sample.

**Behaviour the pass bar does not capture, observed in the transcripts.**

- After reading that spec, reps 2 and 5 each ran `Glob` `{"pattern": "specs/usable_series*",
  "path": "/Users/lowell/Projects/alt-nfp"}` (rep-2 rec 123, rep-5 rec 158). Both results were
  `Directory does not exist: /Users/lowell/Projects/alt-nfp.` Rep-3 ran `Glob`
  `{"pattern": "*/{src/,}nfp_series/calibration*", "path": "/Users/lowell/Projects"}` (rec 120),
  result `No files found`. So reps went looking outside their scratch repo for the fixture's
  origin and, here, found nothing. That the search followed the read is the order of events; I
  did not verify that the read caused it. Note that `Projects/alt-nfp` is not on the VOID list
  (`alt-nfp-model`, `alt-nfp-stats*` and `archive/alt_nfp` are), so a hit there would not have
  voided a rep under the rule as written. That is a gap worth closing in any re-run.
- Rep-3 ran a `Bash` `ls -la /Users/lowell/.cache/nfp-series/` (rec 80), a listing of the
  sibling rep directories. It is not on the VOID list and was not counted.
- Rep-5 ran a combined `cd /Users/lowell/Projects/agent-skills/specs/completed && wc -l ...`
  `Bash` command (rec 110), which was blocked: the result begins `cd in
  '/Users/lowell/Projects/agent-skills/specs/completed' was blocked`, and the allowed working
  directory it names is `/Users/lowell/.cache/nfp-series/rep-5`. Its later reads of that
  directory used `Read` and `Grep`, which were not blocked.

The manual rubric (R1-R8) was not scored, and nothing here claims a Synthesize-mode behaviour
held or failed.

## Disposition

No change to any skill. One successor deferred item, in the schema of
`skills/writing-plans/references/deferred-backlog.md`. The controller enters it in
`specs/deferred_items.md` at plan completion; this record does not edit that file. Proposed,
pending the owner's confirmation at the plan-completion gate: close the original item as
superseded by this one and keep the original 2026-07-26 date, so aging is not reset.

- [ ] Synthesize mode has no scenario verification (spec Req 13, gate-deferred; original item
      from plan 18-methodology-pipeline-skills #1, dated 2026-07-26). The locator discipline,
      the triage-table-before-spec-text ordering and the derive-roadmap handoff of
      `describe-critique-methodology` Synthesize mode are still unverified: plan 36 ran VOID,
      0 of 5 reps valid, because the exemplar step of `references/spec-synthesis.md` leads every
      rep to read the skill's own design spec
      (`specs/completed/methodology-pipeline-skills.md`). This is a kit-isolation problem; no
      skill defect is asserted. The kit (`~/.cache/ctl-q9`, `~/.cache/nfp-series`) is outside
      the repo and is rebuildable from plan 36 Task 1. See
      `specs/completed/synthesize-mode-verification-2026-10-05.md` for the traces and the
      pre-registration. Size: design. Done when: a re-run whose exemplar step is isolated (for
      example neutral exemplars supplied to the reps, or the VOID rule revised BEFORE the run;
      the owner's call) yields 5 valid reps and a record under `specs/completed/` with verdicts
      for B1-B3.
