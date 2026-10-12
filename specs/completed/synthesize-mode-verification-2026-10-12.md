# Synthesize-mode scenario verification re-run — `describe-critique-methodology`

**Date:** 2026-10-12 · **Status:** `B1 FAILED (held 0/5 as scored); B2 held 5/5; B3 held 5/5 as scored, pending the owner's R8 ruling; E1 5/5. Six reps run, 1 void, 5 scored`
**Governs:** whether `describe-critique-methodology` Synthesize mode's triage ordering, locator
discipline and derive-roadmap handoff hold in practice. B2 is verified on this fixture. B3 is verified
as scored, and the one post-hoc reading behind it (R8) is put to the owner (Decision). B1 is a recorded failure, driven by one rule (R2, table coverage) that the skill leaves undefined: it
asks for a table "covering every critique point" and never says what a point is. Resolving that is a
separate writing-skills cycle (Disposition).

> ⚠️ **Quarantine this file during any future micro-test of `describe-critique-methodology`.**
> It names the skill, the behaviours under test, the pass bar and the failures. Its name matches
> the VOID pattern `specs/completed/synthesize-mode-*`, and it sits in `specs/completed/`, the
> directory the skill's exemplar step points reps at (Channel 1 per `microtest-isolation-channels`).

Executes `specs/plans/completed/42-synthesize-mode-verification-rerun.md` (Tasks 1–5), the re-run of plan 36
(`specs/plans/completed/36-synthesize-mode-scenario-verification.md`, whose run was void:
`specs/completed/synthesize-mode-verification-2026-10-05.md`). Source: the open successor item
"Synthesize mode still has no scenario verification (successor of the … item above; plan 36 ran
VOID)" in `specs/deferred_items.md`, under `18-methodology-pipeline-skills (plan #1,
describe-critique-methodology) — 2026-07-26`, selected at the 2026-10-11 `/deferred` pass. Its closure
condition is "a re-run whose exemplar step is isolated yields 5 valid reps and a record under
`specs/completed/` with verdicts for B1-B3". The behaviour
under test is specified in `skills/describe-critique-methodology/SKILL.md` § Synthesize mode and
`references/spec-synthesis.md`.

## Fixture

Unchanged from plan 36, but in fresh repositories. Each rep's scratch repo is
`~/.cache/nfp-notes/rep-<n>` (n = 1..10). All ten hold the same single commit `0e2c907`
(`docs(specs): calibration methodology and its review`, fixed author and date), a one-line
`# nfp-notes` README, and the two fixture files copied byte for byte:

- `/Users/lowell/Projects/alt-nfp-model/specs/completed/calibration_methodology.md` (the
  methodology description, "M" in locators).
- `/Users/lowell/Projects/alt-nfp-model/specs/completed/calibration_methodology_review.md` (the
  external critique, "R"). Pre-skill shape: it carries no C-numbers and a foreign structure (TL;DR,
  Key Findings 1-5, Details A-D, Recommendations 1-10 plus a governance recommendation, Caveats
  1-5), so a synthesis has to declare its own locator scheme.

**Coverage key: 50 points**, frozen before any rep ran and held outside every rep repo at
`~/.cache/ctl-q9/coverage-key.md`: KF1-KF5 (with KF3a, KF3b), A1-A9, B1-B7, C1, C2, C3a-c, C4a-b,
C5-C7, C8a-b, D1-D2, Rec 1-10, Rec G, Cav 3, Cav 4. C3c (pay-frequency composition) was split out of
the paid-or-active point at plan 36's Task 1 review, which moved the count from 49 to 50. The kit
(`~/.cache/ctl-q9/`, `~/.cache/nfp-notes/`) is outside this repository.

## Changes from plan 36

1. **The exemplar step names its exemplars.** `references/spec-synthesis.md` now reads "…read two
   retired exemplars in the agent-skills repo's `specs/completed/` directory,
   `delegation-frontmatter-rollout.md` and `skill-model-pin-removal.md`". Applied in Task 1 (commit
   `9c1b16d`). It was landed on `main` by fast-forward before the pilot, because reps load the skill
   through `~/.claude/skills/`, a symlink into the main checkout.
2. **The grader counts denials by `toolDenialKind`.** Applied in Task 2, Steps 2-5. Checked against
   plan 36's archived run: 0 denials before the change and 24 after (6, 4, 4, 6, 4), with no denied
   call left unmapped. `grade.py` also gained `denied_calls`, and the `GRADE_SESSIONS` and
   `GRADE_REPOS` overrides.
3. **Fresh rep repositories.** Applied in Task 2, Step 7: `~/.cache/nfp-notes/rep-1` to `rep-10`, with
   plan 36's `~/.cache/nfp-series/` left alone and treated as a VOID path.
4. **`LLM_WIKI_ROOT` is unset, and exactly `printenv LLM_WIKI_ROOT` is allowed.** Applied in Task 2,
   Step 8 (`run_rep.sh`, one `--allowedTools` argument per rule). It took effect in the pilot (see
   Dispatch).
5. **Pre-registration additions:** the shared-checkout guard, the pilot redesign trigger, plan 36's rep
   repos as a VOID path, and `42-synthesize-mode` as an injected-context marker. Applied in Tasks 2-4
   (`grade.py`'s `VOID_PATHS` and `INHERITED`; the guard ran at four points). The redesign trigger was
   not tripped.

## Pre-registration (fixed before any rep runs)

These are plan 36's rules. Each change is marked **(new)** or **(changed)**.

**The three turns.** These are the exact texts, already in `~/.cache/ctl-q9/prompts/` (unchanged):
- T1, the skill's own re-entry utterance from `SKILL.md` Describe step 4: `The critique is back — use describe-critique-methodology (synthesize mode) on specs/calibration_methodology_review.md`
- T2: `Thanks. On every needs-user-adjudication point, go with your recommendation, or with the critique's position where you gave none. Go ahead and finish the spec.`
- T3: `Approved — the spec looks good.`

**Behaviours and how each is scored** (per valid rep; pass/fail):
- **B1: triage before spec text.**
  - M1 (mechanical): the first assistant message with a markdown table that has a verdict column comes before the first write to the new spec file in the transcript. This holds even when both happen in one turn, because a first-pass critique may leave no question to wait on.
  - R1 (manual): above the table, the rep states whether the critique was adjudicated or a first pass.
  - R2 (manual): the table covers every critique point in the coverage key, `~/.cache/ctl-q9/coverage-key.md`, which is frozen at 50 points.
  - R3 (manual): every needs-user-adjudication question is in the table's message, and none is asked in a later message.

  B1 passes when M1, R1, R2 and R3 all hold.
- **B2: locator discipline.**
  - M3 (mechanical): before the Requirements section, the spec names both fixture files.
  - R4 (manual): a Design provenance paragraph declares a locator scheme. The critique has no C-numbers, so a declared custom scheme is the expected behaviour.
  - R5 (manual): every requirement carries at least one locator in that scheme.
  - R6 (manual): five locators sampled per rep each resolve to a real section or point of the fixture.
  - R7 (manual): every requirement has a locator, unless it is explicitly routed to brainstorming.

  B2 passes when M3 and R4–R7 all hold.
- **B3: routing header and handoff.**
  - M2 (mechanical): the spec's first non-blank line after its title is the routing header from `spec-synthesis.md`, verbatim except for whitespace.
  - M4 (mechanical): no roadmap or plan file exists after T3.
  - M5 (mechanical): the final assistant message names derive-roadmap and recommends a fresh or new session.
  - R8 (manual): the rep stops after the handoff, and never drafts a roadmap, stages or a plan in chat.

  B3 passes when M2, M4, M5 and R8 all hold.

**Pass bar:** each behaviour holds in at least 4 of 5 valid reps. Below that, the behaviour is a recorded failure.

**E1, the exemplar step (new; observed, not scored).** For each rep, record which `specs/completed/` files it read (`grade.py`'s `exemplars_read`). The skill now names `delegation-frontmatter-rollout.md` and `skill-model-pin-removal.md`. E1 is the GREEN check of Task 1's edit, and the pilot rule below uses it.

**VOID rule.** A rep is void if its transcript shows it reading this plan's context, or a worked synthesis of its own fixture. That means either of these:
- A tool input that names, or a tool result that carries, the full path of any of:
  - agent-skills `specs/deferred_items.md`
  - `specs/plans/`
  - `specs/completed/methodology-pipeline-skills.md`
  - `specs/completed/audit_9_2_26.md`
  - `specs/completed/red-baseline-*`
  - `specs/completed/synthesize-mode-*`
  - `.claude/`
  - anything under `~/Projects/alt-nfp-model`, `~/Projects/alt-nfp-stats*` or `~/Projects/archive/alt_nfp`
  - the control directory, including its archived run
  - **(new)** `~/.cache/nfp-series/`, plan 36's rep repos, which hold its reps' syntheses of this fixture
- Injected context (`attachment` / `system` records) that carries any injected-context marker: `36-synthesize-mode`, **(new)** `42-synthesize-mode`, `synthesize-mode-verification`, `scenario verification`, `ctl-q9`.

Reading the skill's own files, and reading `specs/completed/` exemplars other than the listed paths, is required behaviour and never voids a rep. A bare directory listing that shows file names does not void a rep. Reading or grepping the content of a listed VOID path does.

**Shared-checkout guard (new).** Record four values at four points: before the pilot, after the pilot, after the batch, and after each replacement rep.
- `git -C ~/Projects/agent-skills rev-parse --abbrev-ref HEAD`
- `git -C ~/Projects/agent-skills rev-parse HEAD:skills/describe-critique-methodology`
- the exit status of `git -C ~/Projects/agent-skills diff --quiet HEAD -- skills/describe-critique-methodology`
- `grep -c 'skill-model-pin-removal.md' ~/.claude/skills/describe-critique-methodology/references/spec-synthesis.md`

Any of the following voids the reps run since the previous check: the branch is not `main`, the tree hash differs from the one recorded before the pilot, the `diff` exits nonzero, or the `grep` count is not 1.

**Pilot redesign trigger (new).** A pilot rep can be void because it followed the skill's own procedure to a VOID path, for example opening a VOID-listed spec while looking for exemplars. Then **stop**: run no batch, record the run as VOID with the cause, and make the redesign a new deferred item. A pilot that is void for any other cause follows plan 36's rule: record the path and GO.

**Denials (changed).** `permission_denials` counts transcript records that carry `toolDenialKind`, and `denied_calls` lists each denied call's tool and input. Plan 36 counted tool results whose text contained "permission", and reported 0 where its transcripts held 24.

**Wiki environment (new).** Every rep runs with `LLM_WIKI_ROOT` unset, and the only `printenv` it may run is `printenv LLM_WIKI_ROOT`.

**Replacement:** void reps are replaced from rep-6 upward, up to 10 reps in total. With fewer than 5 valid reps after rep-10, stop: record the run as void and report.

## Dispatch

**Owner-run, from a plain terminal, not from a Claude Code session.** Reason: Channel 5. A rep started
inside a Claude Code session would inherit that session's `CLAUDE.md` and `gitStatus`, and no file
quarantine can close that. Each rep is a fresh `claude -p` session with `--session-id` / `--resume`
across the three scripted turns, `--permission-mode acceptEdits`, rooted in its own scratch repo, with
`LLM_WIKI_ROOT` unset. The control directory (prompts, scripts, results, grader, coverage key) is outside
every rep repo. The executor built the kit, audited the transcripts and graded; it never launched a rep.

**Batching.** Rep-1 ran alone as the pilot (13m 0.9s). Reps 2-5 then ran in parallel as one batch
(17m 46.5s). Rep-3 was void, so rep-6 ran alone as the one replacement (12m 34.2s). Reps 7-10 were not
needed.

**Executor and ordering.** The executor ran on Sonnet 5.5. An earlier executor attempt was abandoned
after Task 1's commit and part of Task 2, and was rewound in full before any rep ran: the control
directory and rep repos were rebuilt from scratch, and no rep ever ran under the earlier session ids.
Plan 41 merged (PR #32, `178d2d6`) after plan 42 was written, so the review BASE is `178d2d6`. Task 1's
commit `9c1b16d` reached local `main` by fast-forward on the owner's approval (nothing pushed).

**Model and effort.** All six transcripts carry `message.model` = `claude-opus-5-5`, and every assistant
record carries `effort: "xhigh"` and `perTurnEffort: "xhigh"`. All six ran under Claude Code 2.1.296.
Cost is the `total_cost_usd` of each rep's turn-3 result, and turns are the `num_turns` of turns 1-3.

| Rep | Turns (T1/T2/T3) | Cost | Status |
|---|---|---|---|
| 1 | 20 / 15 / 1 | $4.40 | scored (pilot) |
| 2 | 19 / 19 / 1 | $4.51 | scored |
| 3 | 19 / 14 / 1 | $4.68 | **void** |
| 4 | 14 / 23 / 1 | $5.49 | scored |
| 5 | 15 / 26 / 1 | $5.00 | scored |
| 6 | 18 / 7 / 1 | $4.18 | scored (replacement) |

**Shared-checkout guard.** Recorded at four points. Every value was identical at every point, so no rep
was voided by the guard.

| Point | Branch | Tree of `skills/describe-critique-methodology` | `diff --quiet` exit | `grep -c skill-model-pin-removal.md` via `~/.claude/skills/` |
|---|---|---|---|---|
| Before the pilot (after Task 1 landed) | `main` | `69b30fa3bdf080cc0a8fff3fd39bb0fcad95bde7` | 0 | 1 |
| After the pilot | `main` | `69b30fa3bdf080cc0a8fff3fd39bb0fcad95bde7` | 0 | 1 |
| After the batch | `main` | `69b30fa3bdf080cc0a8fff3fd39bb0fcad95bde7` | 0 | 1 |
| After rep-6 | `main` | `69b30fa3bdf080cc0a8fff3fd39bb0fcad95bde7` | 0 | 1 |

**Pilot audit (rep-1).**
- `grade.py`: `inherited_hits` is `[]`; `exemplars_read` is exactly the two named exemplars; `void_hits`
  lists four names, all from a name-only `Glob` of `specs/completed/` (Rulings, 1).
- Injected context: 155 records (402 KB): 151 `attachment`, 3 `system`, and 1 user text that is not one
  of the three prompts. A marker scan covered `plan 36`,
  `plan 42`, `42-synthesize`, `synthesize-mode`, `scenario verification`, `ctl-q9`, `nfp-series`,
  `deferred_items`, `pass bar`, `pre-registr`, `coverage key`, `VOID`, `Channel 5`, `micro-test`, and the
  behaviour labels. It found nothing outside the skill and agent listings (records 8 and 10), where the
  hits are other skills' descriptions. The remaining records were read in full and the two listings
  (75 KB and 55 KB) by head plus the marker scan. The content is the rep's own working directory, its
  own `(clean)` git status with the single `0e2c907` commit, the global `CLAUDE.md`, hooks, and the
  skill and agent listings.
- `printenv` rule: rep-1's `printenv LLM_WIKI_ROOT || true` ran with no denial and printed nothing, so
  the variable is unset in its environment. The bare form ran in reps 2, 3 and 6 (exit code 1, which
  `printenv` returns for an unset variable) and was denied in none. Task 3, Step 3 expected compound forms
  around `printenv` to stay refused, and they did not, uniformly: `… && printenv LLM_WIKI_ROOT || echo …`
  (rep 4) and `… && printenv LLM_WIKI_ROOT; ls -la` (rep 5) also ran, while the forms that added
  `echo "exit=$?"` (rep 1), a subshell (rep 2) or further `ls ~/Projects` commands (reps 3 and 6) were
  denied. No rep ran any `printenv` other than `printenv LLM_WIKI_ROOT`, and none printed a value.
- Denied calls (4): two variable-bearing or compound environment probes (retried as `printenv LLM_WIKI_ROOT
  || true`), and two attempts to list `~/Projects` and `~/.cache/nfp-notes` (neither repeated as an
  `ls`; the rep tried name-pattern `Glob`s for the same purpose at recs 126-127). Task 3, Step 3 expected
  every denied call to be completed another way. The listings were not, so that expectation did not hold
  either. None blocked a spec write or a commit.
- All three turns produced output; GO.

## Validity

**5 of 6 reps are valid; rep-3 is void.** Each transcript was traced for every tool input and result that
carried a VOID path or marker, and for any read of a sibling rep's directory (`nfp-notes/rep-<m>`, m ≠ n).
"Record" is the 0-based line index in the session JSONL.

| Rep | Verdict | What carried VOID strings | `exemplars_read` | Denials |
|---|---|---|---|---|
| 1 | valid | a name-only `Glob` of `specs/completed/*.md` (rec 95 / 97) | the two named | 4 |
| 2 | valid | nothing (never listed the directory) | the two named | 3 |
| 3 | **void** | a name-only `Glob` of `specs/completed/*.md` (rec 102 / 104), then a content `Grep` for `nfp_series` over `/Users/lowell/Projects` (rec 106 / 108) | the two named | 3 |
| 4 | valid | nothing (one `Glob` of its own, empty, auto-memory directory) | the two named | 2 |
| 5 | valid | nothing | the two named | 2 |
| 6 | valid | a name-only `Glob` of `specs/completed/*.md` (rec 88 / 90) | the two named | 2 |

**Rep-3's void.** Its tool input was `{"pattern": "nfp_series", "path": "/Users/lowell/Projects",
"output_mode": "files_with_matches", "head_limit": 20}`. The result began `Found 13 files` and carried
these full paths: `/Users/lowell/Projects/agent-skills/specs/completed/synthesize-mode-verification-2026-10-05.md`
(a VOID path), four files under `/Users/lowell/Projects/alt-nfp-model/specs/completed/`, four under
`.../alt-nfp-stats/specs/completed/`, and four under `.../alt-nfp-stats-runner/specs/completed/`
(`nfp-series-adr.md`, `nfp-series-adr-review.md`, and the two fixture files). Under the pre-registration
that is a tool result carrying the full path of anything under `~/Projects/alt-nfp-model` and
`~/Projects/alt-nfp-stats*`, and of `specs/completed/synthesize-mode-*`. It is also a grep of the content
of VOID paths, which voids a rep, and plan 36's ruling 1 voids a `Grep` in any output mode whose result
carries a VOID path. The rep did not open any of those files: its next call was another `Grep`
(`growth_calibrated|calibration_wedge`, `*.py`, rec 115, "No files found"), then it read the two exemplars.
The rule keys on exposure, so the void stands. Its narration at rec 98 shows the cause: "now checking
the house-format exemplars and whether the described code lives anywhere I can check for staleness".
That is Synthesize step 1, the staleness check, not the exemplar step. The pilot redesign trigger does
not apply, because the pilot was valid. Four of the six reps (1, 3, 5 and 6) searched outside their repo
for the described system. Reps 1, 5 and 6 used name-pattern `Glob`s (`**/nfp_series/calibration*` and
similar, in `~/Projects` or `~/`) that returned nothing or timed out, since `Glob` matches file names and
not contents. Only rep-3 used a content `Grep`, which is why only its search could surface the fixture's
other copies. Reps 2, 4 and 5 also grepped the installed `bls-data-context` skill's `references/` files
under `~/.claude/skills/`, which are the user's own skills and not a VOID path.

**Rulings fixed before the batch** (after the pilot, before any other rep ran; no post-hoc rulings):
1. A name-only `Glob` listing of `specs/completed/` does not void (the plan's own text). It is the
   source of the four names `grade.py` lists in `void_hits` for reps 1, 3 and 6 (`audit_9_2_26`,
   `methodology-pipeline-skills`, `red-baseline-`, `synthesize-mode-`): false positives.
2. Both named exemplars carry relative pointers to `specs/deferred_items.md` and
   `specs/plans/completed/…` in their text (for example in their status headers). Every rep that follows
   the skill therefore has them in a `Read` result. The VOID rule's "full path" was read as not covering
   a relative pointer inside an allowed exemplar. A rep voids only by acting on one, with a `Read`,
   `Grep` or tool input that opens such a path. No rep did.
3. `bash_write_suspect` entries are read-only `grep`, `git` or heredoc `git commit` commands, or
   denied commands that never ran. None counts against a rep.

**Denied calls**, 16 in all (reps 1-6: 4, 3, 3, 2, 2, 2), every one a Bash command, by reason (the
number after `rec` is the record index):
- *A variable the checker cannot resolve* (6): the `echo "LLM_WIKI_ROOT=${LLM_WIKI_ROOT:-unset}"` probe in
  reps 1 (rec 66), 2 (41), 4 (83), 5 (41) and 6 (69), and the unbraced `echo "LLM_WIKI_ROOT=$LLM_WIKI_ROOT"`
  in rep 3 (45).
- *Multiple operations or shell operators* (6): rep 1 recs 75 (`…; echo "exit=$?"`) and 121 (`ls ~/Projects;
  ls ~/.cache/nfp-notes`), rep 2 rec 55 (a subshell), rep 3 recs 82 (a `printenv … || echo …` chain that also
  listed `~/Projects` and `specs/completed/`) and 190 (a `sort -t: -k3 -u` chain), rep 6 rec 75 (a similar
  chain).
- *`ls` outside the working directory* (4): rep 1 rec 137 (`~/Projects`), and the skill's own `references/`
  directory in reps 2 (rec 49), 4 (41) and 5 (49), which the `~/.claude/skills/` symlink resolves into
  `~/Projects/agent-skills`.

None was a bare `printenv LLM_WIKI_ROOT`, and none blocked a spec write, a commit or an exemplar read.

**Sibling reads.** None in any of the six transcripts, in any tool input or result.

**E1 (observed).** 6 of 6 reps (5 of 5 scored) read exactly `delegation-frontmatter-rollout.md` and
`skill-model-pin-removal.md`, and nothing else from `specs/completed/`. Reps 2, 4 and 5 went to them
without listing the directory. In plan 36 all five reps opened the skill's own design spec.

## Result

All values are per scored rep. M1-M5 came from `grade.py` (all true) and were read-checked: the table is
in each turn-1 message and the first spec write is in turn 2; each spec's first non-blank line after its
title is the routing header; each final message names derive-roadmap and a fresh session; no roadmap or
plan file exists. R1-R8 were scored by reading.

| Rep | M1 | M2 | M3 | M4 | M5 | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | B1 | B2 | B3 | Write turn | Spec path |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | yes | yes | yes | yes | yes | yes | **NO** | yes | yes | yes | yes | yes | yes | **fail** | pass | pass | 2 | `specs/calibration.md` |
| 2 | yes | yes | yes | yes | yes | yes | **NO** | **NO** | yes | yes | yes | yes | yes | **fail** | pass | pass | 2 | `specs/calibration.md` |
| 4 | yes | yes | yes | yes | yes | yes | **NO** | yes | yes | yes | yes | yes | yes | **fail** | pass | pass | 2 | `specs/calibration.md` |
| 5 | yes | yes | yes | yes | yes | yes | **NO** | yes | yes | yes | yes | yes | yes | **fail** | pass | pass | 2 | `specs/calibration.md` |
| 6 | yes | yes | yes | yes | yes | yes | **NO** | yes | yes | yes | yes | yes | yes | **fail** | pass | pass | 2 | `specs/calibration.md` |

Each spec sits in its rep's repo, `~/.cache/nfp-notes/rep-<n>/`, on a new branch `spec/calibration`
with two commits in reps 1, 2, 4 and 5 and one in rep 6 (`git status` clean in all five).

**R2 detail.** The table is read against the frozen 50-point key, with one rule applied to every rep: a
point counts when a row names or describes its distinct claim. A row that only cites a section anchor, or
names the programs involved without stating the claim, does not count. An earlier keyword pass over the
tables was too loose (it counted `global`, `ADP` and `variance` as matches), so every table was read in
full, and rep-4's 24 rows were checked by hand against all 50 points.
- **C3c, pay-frequency composition.** Absent from the whole turn-1 message and from the spec in reps 1,
  2 and 6; rep-5's spec mentions only a pay-period convention ("the pay period including the 12th"),
  a different matter. Rep-4's `T21` names it: "mix of pay frequencies". Reps 1, 2, 5 and 6 each have a
  paid-or-active, multi-establishment row that cites `§C.3` but never describes the pay-frequency claim.
  Scoring the spec as well as the table does not change this: pay-frequency composition appears in no
  spec except rep-4's, which also has it in the table.
- **KF2, CES's analyst-mediated treatment of atypical reports.** Stated in no rep's table. Each cites it
  only through an anchor on an "evidence" row (quoted below), so R2 fails for every rep on this point as
  well. KF4 (FRB and ADP validate the architecture) is stated as a claim in rep-5 (`T28`: Fed/ADP as
  precedent, neither publishing its thresholds) and rep-6 (row 23); in reps 1, 2 and 4 it is an anchor
  plus program names, which the same rule counts as a miss.
- **Other points missing from the table:** A7 (collapse size before geography) in reps 2 and 6; B3 (the
  QWI "10 or more jobs" figure) in rep 6.
- **Marginal, not counted as misses:** B7 (n_eff admits a small-employer provider's small cells) is not a
  separate row in any of the five reps (each rep's remark about small-employer providers belongs to its
  coverage-floor row, a different claim), and A9 (the QCEW-weighting principle stays global) is not named
  in reps 4 and 5. B7 is a consequence of Recommendation 1, which every rep's table carries, and A9 is the
  last item of a "keep global" list whose other items every rep names. Counting either as a miss would
  add to the failures already recorded and would change no rep's verdict.
- **Rep 4, hand-checked** (23 rows). Every ask is covered: Recommendations 1-10, the governance recommendation, both
  change-asking caveats, and every Details A-D item except the marginal B7 and A9. It misses only the
  evidence-level KF2 and KF4, and marginally B7 and A9. That is a few points short of "covers every
  point", so R2 fails for rep-4 as written.
- **The pattern in the misses.** Every point missed in any rep is one that the critique's numbered
  Recommendations do not carry. KF2 and KF4 are Key Findings and B3 is an evidence figure. C3c is in Details
  C gap 3's first sentence, while the gap's own asks are "(a) state whether emp counts are paid or active"
  and "(b) flag or stratify multi-establishment records", and Recommendation 9 omits pay frequency too. A7
  ("consider collapsing size before geography", Details A) is an ask, but only as a clause of a bullet whose
  main ask, the collapse order and share cap, reps 2 and 6 did cover. The reps' tables track the
  Recommendations and the asks stated in Details, not every claim the critique makes.

**R3 detail.** Rep-2's turn 2 raises a new owner decision that was not in its triage message (quoted
below). The other four reps put every needs-user-adjudication question in the triage message and ask
none later. All five carry the one unanswered fact question (has the code changed since 2026-09-22) forward
as an open item and do not raise it as a new question.

**R4 (the declared scheme).**
- Rep 1: "the critique … has no C-numbers, so this spec uses its own locator scheme: **M §n** is a
  section of the description. For the review: **R KF1–5** …"
- Rep 2: "this spec cites **M §n** for description sections and, for the review: **R KFn** (Key Findings),
  **R §A (topic)** …"
- Rep 4: "The review predates C-numbering, so the locators are: **M §n** … **R Rec n** … **R §A–§D** …"
- Rep 5: "**Locators:** **M §n** cites the description. The review has no numbered points, so it is cited
  by its own structure: **R KF n** …"
- Rep 6: "Locators: **M §n** cites the description, and **M §13 inv. n** its validation checklist. For the
  review, **R KF n** cites Key Findings …"

**R5 and R7.** Every requirement block carries at least one locator in its scheme: 15, 11, 13, 16 and 12
blocks in reps 1, 2, 4, 5 and 6, with 2 locators at the fewest. None is routed to brainstorming without
one. Every locator in every spec resolves to real fixture structure (0 failures out of 62, 46, 49, 60 and
56 distinct locators).

**R6 (five sampled locators per rep).** The sample is every fifth unique locator by first appearance in
the Requirements section. Each was read against its spec context and its target.

| Rep | Sampled locator → where it resolves |
|---|---|
| 1 | `R Gov` → the governance recommendation (two-level configuration); `R §C.1` → Details C.1, no establishment-level variance estimation; `R §B.4` → Details B.4, effective sample size; `M §7.6` → "7.6 Winsorization of cell growth"; `R Rec 10` → Recommendation 10 (imputation discount, coverage floor, QC caps) |
| 2 | `M §2.1` → "2.1 The leaf and the calibration cell"; `R §C.4` → Details C.4, client churn and onboarding cohorts; `R Rec 2` → Recommendation 2, emit a variance; `R §B.1` → Details B.1, the SE/CV precision test; `R KF1` → Key Finding 1, CES screening constants |
| 4 | `M §7.1–7.2` → "7.1 Establishment-level screening"; `M §4, §5` → "4. Measure 1: `growth_raw`"; `R §B.3` → Details B.3, the QCEW-fraction term; `R Rec 4` → Recommendation 4, industry-specific screen; `R Rec 9` → Recommendation 9, paid vs active |
| 5 | `M §1` → "1. Purpose and Scope" (the leaf is one record per geography × industry × size cell); `M §2.4` → "2.4 QCEW vintages and as-of correctness"; `R §B.4` → Details B.4, effective sample size; `R KF3` → Key Finding 3, Hidiroglou-Berthelot and Kokic-Bell; `M §7.3, §12` → "7.3 Eligibility screening" (the coverage floor) and the configuration surface |
| 6 | `M §2.1` → "2.1 The leaf and the calibration cell"; `R §A` → Details A; `R §C.1` → Details C.1, no establishment-level variance estimation; `M §7.7` → "7.7 Weight normalization" (the max single-weight cap); `R Rec 5` → Recommendation 5, anomaly bounds |

## Decision

Against the pre-registered bar (a behaviour holds in at least 4 of 5 valid reps):

| Behaviour | Result | Verdict |
|---|---|---|
| **B1: triage before spec text** | 0 of 5 as scored | **FAILED** |
| **B2: locator discipline** | 5 of 5 | **held** |
| **B3: routing header and handoff** | 5 of 5 | **held** |
| E1 (observed, unscored) | 5 of 5 read exactly the two named exemplars | the Task 1 edit works |

**B1 in detail.** B1 has four parts, and three hold: the triage table precedes every write to the spec
(M1, 5/5), every rep states above the table whether the critique was adjudicated (R1, 5/5), and four of
five put every adjudication question in the table's message (R3). What fails is R2, table coverage
(0/5 as scored): C3c is missing in four reps, KF2 in all five, KF4 in reps 1, 2 and 4, and reps 2 and 6
also drop A7 (and rep 6 B3).

What the failure is about: the skill asks for "ONE batched table covering every critique point" and never
says what a point is. The reps took the critique's asks as the points (its ten Recommendations, the
governance recommendation, the change-asking caveats and the numbered asks in Details), and every point
they missed is one that the numbered Recommendations do not carry: a Key Finding, an evidence figure, or a
clause of the Details prose (R2 detail, "The pattern in the misses"). The frozen key counts 50 distinct claims. So the failure is
a mismatch between the key's unit and the unit the reps chose, and the skill gives no basis for choosing
between them. That is the fork in the Disposition item.

**How sensitive each verdict is to the readings I chose:**
- *B1 fails under every reading tried.* As scored it holds in 0 of 5. A lenient reading that counts a
  KF anchor with its evidence named as covering that finding gives rep-4 a pass, so 1 of 5. If C3c is
  also excused (the old 49-point reading, which merged it into the paid-or-active point) and the marginal
  omissions are excused, reps 1, 4 and 5 pass R2, but rep-2 still fails R3 and A7 and rep-6 fails A7 and
  B3, giving 3 of 5. None reaches 4. Scoring the spec together with the table does not rescue the
  strict reading either, because the dominant miss, C3c, is in no spec but rep-4's.
- *B3 depends on how R8 is read.* All five final turns are a single turn with no tool calls, and none
  drafts a roadmap, stages or a plan. Four also say what the roadmap's first stage should settle, and
  the fifth tells the new session where to start (quoted below). Each points back at the spec's own
  Rollout-note ordering, and none lays out a staged breakdown, so I scored R8 as a pass for all five.
  If the owner reads those remarks as drafting stages, B3 could fail in up to 5 of 5. This reading was
  made after seeing the transcripts, so it is put to the owner as an explicit ruling at the plan-completion
  gate (see the Rulings line at the end of this record).
- *B2 is not sensitive.* Both R4-R7 and M3 hold in every rep, and every locator resolves.

## Qualitative evidence

Quotations are verbatim from the transcripts, the reps' specs and the fixture, with line wraps collapsed to
single spaces and the markdown list number and bold markers around a whole quoted sentence dropped; … marks
an omission.

**The failures, verbatim.**
- The critique's own text for the dropped clause (Details C, gap 3): "No treatment of pay-frequency
  composition or multi-establishment clients. The FRB/ADP work is explicit that pay frequency
  (weekly/biweekly/semimonthly/monthly) and the paid-vs-active distinction materially affect volatility".
- Rep 1, `T14`: "R Rec 9, §C.3: state whether employment is paid or active; flag client records that span
  several establishments". Rep 2, row 13: "R Rec 9, §C.3: paid vs active employment; client records spanning
  several establishments". Rep 5, `T21`: "R Rec 9 / §C.3: state whether employment is paid or active; flag
  clients with several establishments". Rep 6, row 18: "State whether employment is paid or active; flag
  client records that span several establishments (R Rec 9, R §C.3)".
- The rep that kept it, rep 4, `T21`: "Paid vs. active employment; clients with several establishments; mix of
  pay frequencies (R Rec 9, §C.3)".
- KF2, the critique's text: "CES treatment of "atypical" reports — which the document explicitly mirrors — is
  analyst-mediated and cell-dependent, not a fixed global rule." Rep 4, `T22`, the only row that carries it:
  "FRB/ADP/QuickBooks evidence; limits of ADP/Paychex documentation (R KF 1-5, Caveats 1-2) | accept (no
  action) | Evidence behind the rows above, not requirements." Rep 2, row 22: "R KF2, KF4, KF5: CES,
  ADP-FRB and QuickBooks practice | accept as evidence | Citations supporting the design; no requirement of
  their own."
- A7, rep 2, row 16: "R §A 7.4: per-industry collapse order and collapsed-share cap | **reject for now**".
  Rep 6, row 12: "Per-industry collapse order and collapsed-share cap (R §A) | accept, scoped". The critique's
  words: "consider collapsing *size* before *geography* in industries where size is the dominant confounder".
- R3, rep 2, turn 2: "One new owner decision is flagged at the end of the Rollout note: when a default
  changes, should it be applied retroactively to history or only going forward?" Rep 2's triage message had
  asked only Q0 (staleness) and Q1 (the module's stance). Reps 1, 4 and 5 asked the history question in turn 1.

**The handoff remarks behind the B3 sensitivity** (turn 3 unless noted):
- Rep 1: "The two items that block the most work, O0 … and O1 …, open the Rollout note. That should make
  them the roadmap's first stage."
- Rep 2: "It's the first check in R1, alongside O1, so the roadmap's first stage settles it."
- Rep 4: "Start with the Rollout note: V1 (has the description gone stale?) and V2 (does the module see
  individual establishments or only cell totals?) come first and pick the branches for R4, R5, R7 and R9."
- Rep 5: "derive-roadmap will split the 16 requirements into stages. It should start with the seven open
  facts in Req 1 …"
- Rep 6: "Expect the first stage to be the prerequisite checks (Req 1, O0–O6)".
- Each also stops explicitly or by saying the staging belongs to derive-roadmap ("I'm stopping here; the
  roadmap belongs in that new session", "I'm stopping here: the roadmap and the staging are
  derive-roadmap's job").

**Notable behaviour the pass bar does not capture.**
- *The staleness check is a second systemic void path.* Synthesize step 1 sends a rep to look for "the
  described system", and on this machine that system lives in `alt-nfp-model` and `alt-nfp-stats*`. Four
  of six reps searched outside their repo for it (reps 1, 5 and 6 found nothing; rep-3's content `Grep`
  returned VOID paths and voided it). This is production-faithful behaviour that the VOID rule penalises,
  as plan 36's record noted for the exemplar step, and it recurs at roughly one rep in six here. A later
  re-run could isolate it, or decide the rule, before starting.
- *Reps decided after the triage was approved.* Rep 6, turn 2: "**Decisions made while writing that you
  haven't seen yet.** You approved the triage verdicts, not these:", then five of them, including "triage
  accepted 'derive it from variances later,' but I've rejected the review's actual recipe". These were
  disclosed after the fact, not asked, so R3 passes, but a triage verdict was changed without a question.
- *Convergence.* All five stated the critique was an unadjudicated first pass; all five flagged the
  description's own contradiction about the leaf (M §2.1 says cell totals, M §7.1 screens individual
  establishments) as an `(open)` fact check that opens the Rollout note; all five rejected the review's
  claim that the max-weight cap should be unified with an effective-sample-size floor, and all five rejected
  per-industry values for the QC warning caps.
- *Branching.* All five committed the spec on a new branch `spec/calibration` rather than `main` (rep 1:
  "I branched because I don't commit straight to `main`"), so a fresh derive-roadmap session on `main` will
  not find it unless the branch is merged or checked out. They said so in turns 2 and 3. Not measured.
- *Description defects found unprompted:* the mixed log-versus-ratio growth units (reps 1, 4 and 6) and
  the two definitions of the calibration wedge (reps 1, 5 and 6).
- *Blind spots of the kit.* `grade.py` matches VOID substrings against every tool input and result, so a
  name-only `Glob` of `specs/completed/` is reported as `void_hits` (four false positives in each of reps 1,
  3 and 6) and every hit has to be traced by hand, as the Validity table does. It has no check for a rep
  reading a sibling rep's directory (`~/.cache/nfp-notes/rep-<m>`, m ≠ n), which matters because reps 2-5
  ran in parallel; the sibling-read trace here was a separate manual pass (none found). A later re-run
  could add each sibling directory to a rep's VOID paths when it grades that rep.

## Disposition

No change to the skill in this plan. One deferred item for the failed behaviour, in the schema of
`skills/writing-plans/references/deferred-backlog.md`. The controller enters it in
`specs/deferred_items.md` at plan completion; this record does not edit that file.

- [ ] Synthesize mode never defines what a "critique point" is for the triage table, so the table covers the
      critique's asks and drops claims that live only in its Key Findings or Details (B1 failed, held 0/5 as
      scored of 5 valid reps, in plan 42's re-run; 1/5 on a lenient reading). `skills/describe-critique-methodology/SKILL.md`
      § Synthesize mode step 2 and `references/spec-synthesis.md` § Critique triage table ("ONE batched table
      covering every critique point"). Four reps left pay-frequency composition (Details C gap 3's first
      clause) out of the table, all five left CES's analyst-mediated treatment of atypical reports (Key
      Finding 2) to an anchor on an evidence row, reps 1, 2 and 4 did the same for Key Finding 4, reps 2 and
      6 dropped collapse-size-before-geography, rep 6 dropped the QWI figure, and rep 2 raised a new owner
      decision (history handling) in its turn-2 message. Every miss is a point that the critique's numbered
      Recommendations do not carry (a Key Finding, an evidence figure, or a clause of the Details prose).
      The same reps triaged before any spec text (5/5) and stated the adjudication status above the table
      (5/5), so ordering holds and coverage granularity does not. See `specs/completed/synthesize-mode-verification-2026-10-12.md` for
      the traces. Size: design. Done when: the owner has chosen the fork and it is done. Either (a) the skill
      defines a point as every distinct claim, with a compound point split and a coverage check against the
      critique's own enumeration (a writing-skills RED→GREEN cycle), and a re-run on this fixture holds B1 in
      at least 4 of 5 valid reps; or (b) the owner revises the R2 rubric to score the critique's asks
      (Recommendations, governance, change-asking caveats, numbered Details asks) and records the revised
      bar.

**Rulings.** R8 (whether the handoff remarks about the roadmap's first stage count as drafting stages;
B3's verdict turns on it): pending the owner's ruling at the plan-completion gate. This line is updated
when the owner rules.

Not turned into items: the staleness-check void path, rep-6's post-approval decisions and the kit's
missing sibling-read check are recorded above as observations. Whether any is worth an item is the owner's
call at the completion gate.
