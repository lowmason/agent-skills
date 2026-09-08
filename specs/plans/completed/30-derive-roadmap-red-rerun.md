# derive-roadmap Clean RED Baseline Re-run — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-run the `derive-roadmap` RED baseline under clean isolation, so that "E1–E5 NOT OBSERVED" either becomes a trustworthy null or flips — settling whether the SKILL.md guidance those five failures justify is earned or speculative.

> **STATUS: EXECUTED 2026-09-08 — measurement VOID IN FULL (0 of 12 reps valid).**
> Tasks 1, 2 and 4 completed as specified. Task 3 ran to the pre-registered 12-dispatch
> halt and produced no valid rep. Result: **E1–E6 all INCONCLUSIVE**; no SKILL.md change
> recommended or made. Record: `specs/completed/red-baseline-derive-roadmap-2026-09-08.md`.
>
> **The plan's central premise was false.** It assumed the leak channels were closed and
> the fixture rename would keep them closed. Neither held:
> - The rename does not prevent the header hunt, it *provokes* it — a header naming a
>   skill that resolves nowhere is an anomaly worth investigating. Plan 19's "leak" and
>   "Hawthorne confound" are one phenomenon, not two.
> - **Channel 5 (decisive):** every rep receives the skill name in inherited session
>   context — project CLAUDE.md + the session-start gitStatus naming this very plan file —
>   before its first tool call. Invisible to the VOID rule (no tool call), to the grep
>   gate (filesystem-only), and unaffected by the neutral cwd.
> - **Global Constraint line 22 was unachievable as written.** gitStatus snapshots at
>   session start, so quarantining this plan file mid-session cannot alter what subagents
>   already inherited.
>
> Deviations D1–D6 are listed at the foot of this file.

**Architecture:** This plan produces a measurement, not a feature. Four tasks: build a contamination-free fixture outside both repos and prove it clean by grep; pre-register the failure list *and* the decision rule before any agent runs; dispatch fresh no-guidance subagents in disclosed batches and score them verbatim against transcripts; then apply the pre-registered rule and gate the SKILL.md consequence past the owner. There is no application code and no pytest suite — the verification gates are grep exit codes and subagent transcripts.

**Tech Stack:** Bash, `grep`, the Agent tool (`general-purpose` subagents), subagent transcript JSONL under `~/.claude/projects/<proj>/*/subagents/`.

## Global Constraints

These govern every task and outrank any conflicting task text.

- **The E1–E6 list is frozen.** Reuse it verbatim from `specs/plans/completed/19-methodology-pipeline-skills.md` Task 1 Step 2. Changing a single expectation destroys comparability with the confounded round, which is the entire point of the re-run.
- **Nothing a rep can read may contain the answer** (`microtest-isolation-channels`, Channel 3 general form). This covers the fixture, the fixture's directory siblings, the task list, the SDD ledger, and this plan file.
- **The fixture is at `~/Projects/alt-nfp/specs/completed/usable_series_methodology_roadmap.md`** — NOT the path the deferred item names (`specs/usable_series_methodology_roadmap.md`); it was retired to `completed/` after plan 19. Never point a rep at any path inside `~/Projects/alt-nfp`.
- **An answer key exists and is the new third leak channel:** `~/Projects/alt-nfp/specs/completed/usable-series-selection-roadmap.md` ("Derived 2026-07-30") is the finished staging of this exact fixture, sitting in the same directory. `~/Projects/alt-nfp/specs/alt-nfp-unified-spec-revisions.md` also names the skill.
- **Batching is 2+2+1, not 5-in-one** (`microtest-isolation-channels`, dispatch mechanics (a)). Plan 19's "dispatch 5 in one message" is superseded; a ~50 KB prompt fits twice per message. Disclose the actual batching in the record.
- **`TOOLS USED: advisor` is not contamination** (dispatch mechanics (b)) — it is the harness's built-in model-consult with no file access. Never void a rep for it. Void only on transcript evidence of `Read|Grep|Glob|Skill|Bash`.
- **Every task list subject is opaque** (`Step N of 4`). Delete stale task-list entries before dispatching.
- **This plan file must be quarantined during the dispatch window** — it names the skill, the fixture and the pre-registered failures.
- **Do not edit `skills/derive-roadmap/SKILL.md` in this plan.** The outcome is a recommendation to the owner, never an automatic cut. See Task 4.
- Scratch root for all working files: `~/.cache/red30/`. Never `/tmp` directly (`tmp-struct-shadow`).

---

### Task 1: Contamination-free fixture, proven by grep

**Files:**
- Create: `~/.cache/red30/fixture/usable-series-selection-v2.md` (scratch — never committed)
- Create: `~/.cache/red30/grep-gate.log` (scratch — the evidence Task 4's record cites)
- Read-only: `~/Projects/alt-nfp/specs/completed/usable_series_methodology_roadmap.md`

**Interfaces:**
- Consumes: nothing.
- Produces: an absolute fixture path that Task 3's dispatch prompt embeds verbatim, and a grep log proving the three leak channels are closed. Task 3 must not dispatch if this task's gate did not exit 0.

- [x] **Step 1: Create the scratch root and copy the fixture under a neutral name**

```bash
mkdir -p ~/.cache/red30/fixture
cp ~/Projects/alt-nfp/specs/completed/usable_series_methodology_roadmap.md \
   ~/.cache/red30/fixture/usable-series-selection-v2.md
wc -l ~/.cache/red30/fixture/usable-series-selection-v2.md
```
Expected: `470 /Users/lowell/.cache/red30/fixture/usable-series-selection-v2.md`

- [x] **Step 2: Neutralize the skill name, keeping the header's instruction intact**

The routing header must survive as an *instruction* so E2 ("ignores the routing header") stays measurable — only the skill's name changes. `sequence-spec-stages` was verified absent everywhere in plan 19; re-verify in Step 4.

```bash
python3 - <<'PY'
from pathlib import Path
p = Path.home() / '.cache/red30/fixture/usable-series-selection-v2.md'
s = p.read_text()
n = s.count('derive-roadmap')
s = s.replace('derive-roadmap', 'sequence-spec-stages')
p.write_text(s)
print(f'renamed {n} occurrence(s)')
PY
```
Expected: `renamed 1 occurrence(s)` (the `REQUIRED NEXT SKILL:` header line).

- [x] **Step 3: Remove the fixture's own back-references to its real filename**

Round 2's confound was that reps diffed the copy against the original and reasoned about tampering *before* staging. A copy that names its own source invites exactly that diff. Neutralize self-references so the document is internally consistent.

```bash
grep -n "usable_series_methodology" ~/.cache/red30/fixture/usable-series-selection-v2.md
```
Then rewrite each hit to the neutral stem:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path.home() / '.cache/red30/fixture/usable-series-selection-v2.md'
s = p.read_text()
for old, new in (('usable_series_methodology_roadmap', 'usable-series-selection-v2'),
                 ('usable_series_methodology_review', 'usable-series-selection-review'),
                 ('usable_series_methodology', 'usable-series-selection-methodology')):
    s = s.replace(old, new)
p.write_text(s)
print('self-references neutralized')
PY
grep -c "usable_series_methodology" ~/.cache/red30/fixture/usable-series-selection-v2.md
```
Expected: `0`

- [x] **Step 4: Run the pre-dispatch contamination gate**

> Deviation (D3, D2): run AFTER the quarantine window opened, so it measured the state
> reps actually see; extended with checks (d) and (e). (b) excludes session-transcript
> `*.jsonl`, which necessarily contain this plan's text. All five passed — **and all five
> were irrelevant**, because the gate greps the filesystem and Channel 5 lives in
> inherited context.

One command covering all three channels. Per `microtest-isolation-channels`, this single grep would have caught every prior occurrence.

```bash
{
  echo "=== gate run: $(git -C ~/Projects/agent-skills rev-parse --short HEAD) ==="
  echo "--- (a) skill name / neutral name inside the fixture ---"
  grep -c "derive-roadmap\|sequence-spec-stages" ~/.cache/red30/fixture/usable-series-selection-v2.md
  echo "--- (b) neutral name must be absent everywhere else ---"
  grep -rl "sequence-spec-stages" ~/Projects/agent-skills ~/Projects/alt-nfp ~/.claude 2>/dev/null | grep -v '.cache/red30' | wc -l
  echo "--- (c) answer key / E-list reachable from the scratch root? ---"
  grep -rl "usable-series-selection-roadmap\|Derived 2026-07-30\|E1 Plans the spec" ~/.cache/red30 2>/dev/null | wc -l
} | tee ~/.cache/red30/grep-gate.log
```
Expected: `(a)` = `1` (the header line only), `(b)` = `0`, `(c)` = `0`. **If any value differs, stop — do not proceed to Task 3.**

- [x] **Step 5: Commit nothing; record the gate result in the todo ledger**

This task creates no repo files. Confirm the working tree is untouched:

```bash
git -C ~/Projects/agent-skills status --short
```
Expected: no output (clean), or only pre-existing unrelated changes.

---

### Task 2: Pre-register the failures AND the decision rule

**Files:**
- Create: `~/.cache/red30/PREREG.md` (scratch during the window; becomes the spine of Task 4's committed record)

**Interfaces:**
- Consumes: nothing from Task 1 — this task must be completable before or after fixture prep, but strictly **before** any dispatch in Task 3.
- Produces: `~/.cache/red30/PREREG.md`, whose "Observed" section Task 3 fills and whose "Decision rule" section Task 4 applies unchanged.

- [x] **Step 1: Write the pre-registration file**

The E-list is copied verbatim from plan 19 and must not be edited. The decision rule is new — it is what makes this round's outcome un-back-fittable in *either* direction.

````bash
cat > ~/.cache/red30/PREREG.md <<'EOF'
# RED baseline (clean re-run) — derive-roadmap

Pre-registered BEFORE any dispatch. Plan 30, Task 2.
Supersedes the confounded round recorded at
specs/plans/completed/19-methodology-pipeline-skills.md Task 1.

## Pre-registered expected failures (frozen — copied verbatim from plan 19)
- E1 Plans the spec WHOLESALE — one plan covering all 18 requirements.
- E2 Invokes writing-plans directly, ignoring the spec's routing header.
- E3 No gap analysis — stages the spec's requirements without ever
     checking what is already implemented.
- E4 Stages by spec section order rather than by dependency, contradicting
     the fixture's own Rollout-note sequencing.
- E5 No per-stage exit criterion, or exit criteria that are restatements
     of the requirement rather than observable outcomes.
- E6 Restates spec requirement text into the roadmap instead of citing §-refs.

## What the confounded round found (for comparison, not for reuse)
E1-E5 NOT OBSERVED, E6 OBSERVED 4/4 — but all 4 valid reps had just noticed
the fixture rename and reasoned about tampering/prompt injection BEFORE
staging. That Hawthorne confound is what this round exists to remove.

## Decision rule (pre-registered — applies whichever way the result falls)
- A failure is OBSERVED if it appears in >= 2 of 5 valid reps, with a
  verbatim excerpt recorded for each.
- If E1-E5 are again NOT OBSERVED in a clean round: writing-skills'
  no-speculative-guidance rule says the SKILL.md guidance answering them is
  unearned and should be CUT. This plan does NOT cut it — Task 4 puts the
  recommendation to the owner, who kept it deliberately at plan 19's Task 8
  gate. The owner's prior decision stands until the owner changes it.
- If any of E1-E5 IS observed: that guidance is earned; record the excerpt
  as the evidence plan 19 never had, and recommend no change.
- A rep is VOID only on transcript evidence of Read|Grep|Glob|Skill|Bash
  reaching outside the fixture. `TOOLS USED: advisor` is NOT void.
- Reps are replaced until 5 valid reps exist. Every dispatch, valid or void,
  is counted and disclosed.

## Observed (verbatim excerpts + counts — filled by Task 3)
EOF
wc -l ~/.cache/red30/PREREG.md
````
Expected: a file of ~40 lines.

- [x] **Step 2: Verify the pre-registration is itself outside the repo**

```bash
git -C ~/Projects/agent-skills status --short | grep -c PREREG
```
Expected: `0`

- [x] **Step 3: Confirm Channel 1 is closed WITHOUT moving this plan file**

> Deviation (D1) — **this step's instruction was not followed, and its premise is false.**
> It argues the neutral name "is absent from this entire repo". Grep before dispatch found
> it in TWO tracked files: this plan and `specs/plans/completed/19-...md`. Global Constraint
> line 16 therefore governs, and line 22 requires quarantining this file outright. Under
> executing-plans the plan is already in the controller's context, so moving it costs
> nothing — the `self-modifying-plan-hazard` objection is specific to
> subagent-driven-development. Quarantine set expanded to: this plan, plan 19,
> `specs/deferred_items.md`, `.sdd/`, and the `~/.claude/skills/derive-roadmap` symlink.
> **It did not help** — see Channel 5.

This plan names the skill, the fixture and the expected failures, so the instinct is to `mv` it out of the tree for the dispatch window. **Do not.** This plan is the executor's own instruction source — under subagent-driven-development the controller re-reads it between tasks, so moving it here would leave Task 3 with nothing to execute (`self-modifying-plan-hazard`).

It also does not need moving. Channel 1's trigger in plan 19 was that the fixture *named a skill*, which sent every rep hunting through the cwd for it. Task 1 Step 2 removed that trigger at its source: the neutral name `sequence-spec-stages` is absent from this entire repo, so there is nothing here to find by name. Reps receive one absolute `~/.cache/red30/` path and no repo context.

Verify that reasoning rather than assuming it:

```bash
grep -rl "sequence-spec-stages" ~/Projects/agent-skills 2>/dev/null | wc -l
```
Expected: `0` — the fixture's neutral name leads nowhere in this repo.

The residual risk is a rep that browses the repo unprompted. Moving one file does not prevent that, and Task 3 Step 3 already catches it: any rep whose transcript shows a read outside the fixture is void.

- [x] **Step 4: Quarantine the SDD ledger — inside Task 3 only, never across tasks**

`.sdd/progress.md` names the expected verdict, and a rep in plan 20 read one and quoted the pass bar back verbatim. Unlike this plan file, the ledger is not needed *during* a dispatch, so its window can be closed inside one task. Move it as the FIRST action of Task 3 and restore it as the LAST:

```bash
mkdir -p ~/.cache/red30/quarantine
mv ~/Projects/agent-skills/.sdd ~/.cache/red30/quarantine/sdd 2>/dev/null || echo "no .sdd to move"
```
Restore (last step of Task 3):
```bash
mv ~/.cache/red30/quarantine/sdd ~/Projects/agent-skills/.sdd 2>/dev/null || echo "nothing to restore"
```

- [x] **Step 5: Clear stale task-list subjects**

> No task list existed in this session (no TodoWrite tool available), so Channel 2 was
> closed by absence rather than by action.

Channel 2: subagents can call `TaskList`/`TaskGet` and read the orchestrator's task titles, including completed ones from earlier plans. Retitle every live task to `Step N of 4` and delete stale entries before dispatching.

Expected: no task subject anywhere contains `derive-roadmap`, `roadmap`, `RED`, `P19`, `P30`, or `baseline`.

---

### Task 3: Dispatch 5 valid no-guidance reps and score them verbatim

**Files:**
- Modify: `~/.cache/red30/PREREG.md` (fill the "Observed" section)
- Read-only: subagent transcripts under `~/.claude/projects/-Users-lowell-Projects-agent-skills/*/subagents/agent-*.jsonl`

**Interfaces:**
- Consumes: the fixture path from Task 1 and the frozen E-list from Task 2. **Do not start if Task 1 Step 4's gate did not report (a)=1, (b)=0, (c)=0.**
- Produces: `~/.cache/red30/PREREG.md` with per-rep OBSERVED/NOT-OBSERVED scoring and verbatim excerpts, plus a dispatch count including voids.

- [x] **Step 1: Dispatch the first batch of 2 reps**

Two `general-purpose` agents in ONE message so they run concurrently. Each gets exactly this prompt — no mention of the skill, no hints, no repo context:

```
Read /Users/lowell/.cache/red30/fixture/usable-series-selection-v2.md.
It is a design spec for work on a data pipeline. Turn it into staged, actionable work.
Do NOT write, create, or edit any file, and do NOT run git. Report your staging
as your final message.
```

- [x] **Step 2: Dispatch the second batch of 2, then the fifth**

> Deviation: actual batching was **2+2+3+5 = 12 dispatches**, not 2+2+1. The plan's
> batching assumed a ~50 KB embedded prompt; the prompt is four lines because reps read the
> fixture themselves. Deviation D6: from batch 2 on, the controller's cwd was moved to a
> neutral scratch dir so subagents no longer inherited the skills repo. That stopped reps
> reading the skill body but did not stop the header hunt, and did not touch Channel 5.

Identical prompt, unchanged. Batching is 2+2+1 because a ~50 KB prompt fits only twice per dispatch message. Record the actual batching for the disclosure in Task 4.

- [x] **Step 3: Check every rep's transcript before scoring it**

Reps confabulate having read things they did not, and omit things they did — require the transcript, not the self-report.

```bash
for f in ~/.claude/projects/-Users-lowell-Projects-agent-skills/*/subagents/agent-*.jsonl; do
  echo "--- $f"
  grep -o '"name":"\(Read\|Grep\|Glob\|Skill\|Bash\)"' "$f" | sort | uniq -c
done
```
Expected: for a valid rep, either no matches, or only `Read` of the fixture path itself. Any hit reaching `~/Projects/agent-skills`, `~/Projects/alt-nfp`, or `~/.claude/skills` voids that rep — replace it and keep dispatching until 5 valid reps exist.

- [x] **Step 4: Score each valid rep against E1–E6, reading every match manually**

> Deviation: scoring was done by a blind panel (3 independent scorers per rep, majority
> vote, then an adversarial refuter per OBSERVED verdict) rather than by the controller,
> who knew the pre-registered list. 18 agents, 0 errors. **The scoring is descriptive only
> and is NOT a result** — 0 reps were valid. It is retained in the record because two real
> defects came out of it: the VOID rule censors the behaviour E2 detects, and the fixture
> rename makes the routing header legitimately unfollowable. Both apply retroactively to
> plan 19.

Do not count keyword hits. For each rep, append to the "Observed" section of `~/.cache/red30/PREREG.md`: the rep letter, then for each of E1–E6 either `OBSERVED` with a verbatim excerpt, or `NOT OBSERVED`.

- [x] **Step 5: Total the counts and state the NOT-OBSERVED set explicitly**

Under "Observed", write one summary line per expectation in the form `E<n>: OBSERVED k/5` or `E<n>: NOT OBSERVED`. Also record the total dispatch count including voids, and the actual batching.

---

### Task 4: Apply the pre-registered rule, commit the record, gate the consequence

**Files:**
- Create: `specs/completed/red-baseline-derive-roadmap-<YYYY-MM-DD>.md` (committed; date is the day Task 3 ran)
- Verify restored: `.sdd/` (moved and restored within Task 3; this plan file is never moved)
- **Do NOT modify:** `skills/derive-roadmap/SKILL.md`

**Interfaces:**
- Consumes: the filled `~/.cache/red30/PREREG.md` and `~/.cache/red30/grep-gate.log` from Tasks 1–3.
- Produces: the committed RED record, and a batched question to the owner. No skill file changes.

- [x] **Step 1: Confirm the quarantine window is fully closed**

```bash
ls ~/.cache/red30/quarantine/ 2>/dev/null || echo "quarantine empty"
git -C ~/Projects/agent-skills status --short
```
Expected: the quarantine directory is empty — Task 3's last step restored `.sdd`, and this plan file was never moved.

- [x] **Step 2: Write the record, following the house RED-record format**

Match the structure of `specs/completed/red-baseline-divergence-gate-2026-09-02.md`: `# RED baseline — <what>`, a `**Date:** … **Status:** …` line, a `**Governs:**` line, the quarantine warning block, then `## Measured behaviour`, `## Fixture`, `## Result`, `## Decision (pre-registered rule applied)`, `## Qualitative evidence`, `## Disposition`.

The record MUST disclose, because each was a confound or a deviation:
- the name substitution (`derive-roadmap` → `sequence-spec-stages`) and the self-reference neutralization, with the reason;
- the actual dispatch batching and the total dispatch count including voids;
- the grep-gate output from `~/.cache/red30/grep-gate.log`;
- that this round supersedes plan 19's Task 1 result, and why that one was confounded.

Open it with the standard quarantine warning:

```markdown
> ⚠️ **Quarantine this file during any future micro-test of `derive-roadmap`.** It names
> the skill and states the expected failures — Channel 1 per `microtest-isolation-channels`.
```

- [x] **Step 3: Commit the record**

```bash
cd ~/Projects/agent-skills
git add specs/completed/red-baseline-derive-roadmap-*.md
git commit -m "test(derive-roadmap): clean RED baseline, superseding plan 19's confounded round"
```

- [x] **Step 4: Put the pre-registered consequence to the owner — do not act on it**

> Deviation: the plan's binary (cut / keep / narrow) does not apply. E1–E5 were not
> "NOT OBSERVED again" — they were **not measured at all**. The question to the owner is
> narrower: the guidance-cut question is not ripe, and the plan-19 keep-decision now stands
> against *no clean null having ever been obtained* rather than against a confounded one.
> `skills/derive-roadmap/SKILL.md` was not modified.

If E1–E5 came back NOT OBSERVED again, state plainly: a clean round now says the guidance answering them is unearned under `writing-skills`' no-speculative-guidance rule, and the owner's plan-19 Task 8 decision to keep it was made against a confounded null. Ask whether to cut, keep, or narrow. **Do not edit SKILL.md in this plan either way** — a guidance cut is a skill-contract change and belongs in its own cycle with its own GREEN arm.

Cite the exact sites, and note that E6's bullet is NOT among them — E6 was OBSERVED 4/4 even in the confounded round, so its guidance is earned and stays regardless:

| Failure | Guidance site in `skills/derive-roadmap/SKILL.md` |
|---|---|
| E1 Plans wholesale | `:162` — "Planning the spec wholesale" |
| E2 Ignores routing header | `:28-45` — the "Entry, in this order" block; and `:164` — "Designing a stage" |
| E3 No gap analysis | `:47` — "§1. Gap analysis — ONCE, at entry" |
| E4 Stages by section order | `:168` — "Sequencing by the spec's own priority ranking" |
| E5 No/restated exit criteria | `:171` — "Exit criteria that restate the requirement" |
| **E6 (earned — do not touch)** | `:166` — "Restating requirements" |

If any of E1–E5 WAS observed, state which, quote the evidence, and record that the guidance is now earned — no question needed for those.

- [x] **Step 5: Run the Plan Completion Protocol**

Per writing-plans § Plan Completion Protocol: resolve-before-defer gate (Step 4's question is a gate question — it blocks the rest until answered), plan markup with deviation notes, then tick the source item in `specs/deferred_items.md`:

`- [x] **The RED baseline for this skill is confounded…** → done in plan 30`

Then run `deferred_stats.py`, present the triage per step 4, and retire the plan to `specs/plans/completed/` in a `chore(specs): retire plan 30` commit. **Do not retire a spec** — this plan is spec-less, derived from a deferred item.


---

## Deviations (all disclosed in the record)

| # | Deviation | Why |
|---|---|---|
| D1 | Quarantine set expanded to plan 19, `deferred_items.md`, the skill symlink | GC16 over Task 2 Step 3, whose premise grep disproved |
| D2 | Gate (b) excludes session-transcript `*.jsonl` | They necessarily contain the controller's plan text; unsatisfiable as literally written |
| D3 | Gate runs after the quarantine window opens | It should measure the state reps actually see |
| D4 | Two stopping rules pre-registered before any dispatch | Deciding them after seeing voids would be back-fitting |
| D5 | Quarantine relocated out of the rep-visible scratch root | Controller error: it was first placed *inside* the directory reps are pointed at |
| D6 | Controller cwd moved to a neutral dir before batch 2 | Subagents inherit cwd; batch 1 showed both reps going straight to the skills repo |

**Not done, deliberately:** the answer key in `~/Projects/alt-nfp` was not quarantined. It
is a different user repo, and the evidence says moving it would not close the channel — one
rep reached the source via the fixture's *prose*, another by grepping `usable_series` across
`~/Projects`. Moving the roadmap leaves the original, the methodology doc and the review doc
all still matching. Surfaced to the owner rather than actioned.
