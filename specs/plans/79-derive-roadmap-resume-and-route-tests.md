# derive-roadmap: resume gaps, route micro-tests and re-runs Implementation Plan

**Status: COMPLETE (2026-11-07)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Quarantine.** This plan, the record `specs/red-baseline-new-project-entry.md` and its folder name the cases, the
> pass rules and the expected behavior. Keep them out of every prompt. (Plan 78's quarantine, extended to this plan.)

**Goal:** Close two derive-roadmap resume gaps and two wording gaps, give plan 78's four untested routes their
micro-tests, and run the re-runs the owner ruled on 2026-11-07.

**Architecture:** Two skill files change: `skills/derive-roadmap/SKILL.md` (§5, and one phrase in §7 step 4) and
`skills/derive-roadmap/references/roadmap-format.md`. Plan 78's micro-test kit gains six cases and one amended copy of
an old case. Every rep result goes into plan 78's record, in new sections headed `Plan 79`.

**Tech Stack:** Markdown skill text; the stdlib Python kit in `specs/red-baseline-new-project-entry/kit/`; `claude -p`
reps on Opus 5.5.

**Spec:** none. This plan comes from a `/deferred` pass (2026-11-07). Its requirements are these items in
`specs/deferred_items.md`:

- (a) "Four routes that plan 78 added have no micro-test" (section `78-derive-roadmap-new-project-entry — 2026-11-06`).
- (b) "Two wording gaps left by plan 78's final review" (same section).
- (c) "`skills/derive-roadmap/SKILL.md` §5 (the resume) has two gaps found in review" (an older section).
- (d) "dr-known-progression fails conformance clause C" (78 section), with its 2026-11-07 owner ruling.
- (e) "dr-tracks passes unstably" (78 section), with its 2026-11-07 owner ruling.

## Global Constraints

- **Execution base.** `BASE79` is the execution branch's start commit: the tip of
  `claude/deferred-items-last-plan-784993` that holds this plan, or `main` once that branch has merged. Task 1 Step 1 records its sha. Line numbers below were taken at `a849bd2`. The old text in each step is the
  match key, not the line number.
- **Order of executions.** This plan executes before the plan for the 2026-11-07 spec that the same `/deferred` pass
  sends to brainstorming (the core-and-later-stages offer wording, roadmap spec-section references and Ranked-list
  O-numbers). That spec edits the Ranked-list section and the one-message text that this plan also edits, so its plan
  builds on this plan's edits. No execution starts while another plan executes in this repository (owner ruling,
  2026-10-28).
- **One owner per file.** Only Task 3 edits skill files. Tasks 1 to 4 each append their own sections to the record.
  Only Task 1 edits `cases.py`.
- **Leave alone.** `skills/derive-roadmap/references/new-project-entry.md` and `references/gap-rubric.md`;
  `SKILL.md` outside §5 and the one phrase of §7 step 4; every other skill; every existing case, pass rule and
  fixture in `cases.py`; every existing rep file and arm folder; the four case-study repositories.
- **Examples stay out of the fixtures (micro-test Channel 3).** New skill text adds no example. New fixtures reuse
  the kit's fixture domains (canal locks and river gauges, parking sensors, SEC filings).
- **Compaction window.** The derive-roadmap SKILL.md body stays at most 20,000 characters
  (`check_conformance.skill_body(text)[0]`; 15,400 after plan 78). No description changes.
- **Commit gate.** Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Commit messages
  follow Conventional Commits, use plain technical English and end with the attribution trailer that the executing
  session is given.
- **Micro-tests.** Plan 78's kit and runner, unchanged: every rep is a fresh
  `claude -p --model claude-opus-5-5 --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format json --max-budget-usd 1.00`
  under `env -i`, from a new empty directory under `/tmp`. Five reps per arm. Text is read with `git show`, never
  through `~/.claude/skills/`. Each pass rule is committed before any rep of its case runs. Every verdict is read by
  hand from the full reply, by the case's rule and by every reading in the record's Control and Task 3 sections.
- **Arms.**
  - *Route cases* (`dr-stop-track`, `dr-park-ranked`, `dr-name-collision`, `dr-rerank-second`): control reads every
    text at `1844bd8` (plan 78's `BASE`, before the routes existed). Treatment reads every text at Task 3's commit.
  - *Resume-gap cases* (`dr-resume-marker`, `dr-resume-blocked`): control reads every text at `BASE79`. Treatment
    reads every text at Task 3's commit.
  - *Re-runs* (Task 4): treatment only, at Task 3's final commit. Each compares with the plan 78 arm that Task 4
    names.
- **Bars.** Plan 78's, unchanged.
  - *Additive:* the treatment passes every bar and conformance clause in at least 4 of 5 reps, and the control fails
    a bar clause in at least 1 of 5.
  - *Non-regression (guard):* the treatment passes at least as many reps as the named comparison arm, minus one.
  - A control with no failure never reverts a change. Record it and put it to the owner at the plan completion
    gate. A RED that comes only from a term the control text lacks is still RED: the record names the clause.
  - A treatment below its bar gets one wording round with the case's rule unchanged, then an owner ruling. The
    round re-runs every case of the task whose decision the changed passage can reach, and the record says why each
    other case was not re-run. An owner stop is not a subagent-driven-development blocker: the implementer leaves its
    files and ends with `BLOCKED (owner gate: Task N Step M)` (plan 78's D13).
- **Spend.** The controller keeps the running total in the record's `Plan 79: spend` table. Stop and ask the owner
  before the total passes **$30**. Before each `run_reps.sh` call, check the total plus that call's worst case
  (5 reps × $1.00). A task's spend is one `show_reps.py` run after its last rep; an unreadable or empty rep file
  counts at its cap.
- **Fixtures.** The sec-edgar spec is read at build time with `CASE_REPOS="$HOME/Projects"`, as plan 78's Fixtures
  constraint says. The case-study repositories are read only.
- **Folders.** Build folders go under `/tmp/plan79-work/`. Each build's `MANIFEST.txt` is copied into the record's
  folder as `control/p79-MANIFEST.txt` or `treatment/p79-<label>-MANIFEST.txt`. New control rep folders are
  `control/<case>/`. Treatment rep folders are `treatment/<case>-p79/`. A wording round adds `-r1`. Task 4's two
  dr-tracks runs are `treatment/dr-tracks-p79a/` and `treatment/dr-tracks-p79b/`.
- **Public repository.** The plan, kit, record and commits hold no private detail.

## Review Focus

1. **A resume of a roadmap whose last stamped stage shipped a Handoff that reads `None`.** The person expects the
   resume to change nothing for that stage, every time. Pinned in Task 3 Step 1: the marker sentence says that such a
   stage is read again and changes nothing.
2. **A track stop while another track still has an unticked stage.** The person expects that track's list items to
   park and the other track's stage to be handed off, with the roadmap live. Pinned by `dr-stop-track` (Task 1 Step 2).
3. **A whole-roadmap park that leaves Ranked-list items behind.** The person expects every list item to park, not
   only the unticked stages. Pinned by `dr-park-ranked` clause A and Task 3 Step 1's Ranked-list sentence.
4. **A spec whose stem's roadmap file already exists but names another source.** The person expects a request for
   another name, never an overwrite and never a resume of the wrong roadmap. Pinned by `dr-name-collision`.
5. **A second re-rank, after a promoted stage has run.** The person expects the report to come from the promoted
   stage's findings file, not the core's. Pinned by `dr-rerank-second` clause B.

## Decisions

- **D1** (owner, `/deferred` pass, 2026-11-07): dr-known-progression: "clause C fits the fixture". Clause C drops
  point-in-time awareness for this fixture, and the case is re-run under the new clause, not re-scored. Applied in:
  Task 1 Step 2, Task 4.
- **D2** (owner, `/deferred` pass, 2026-11-07): dr-tracks: the Task 7 result is not accepted as it stands. The item
  stays open for the two independent five-rep runs, which join this plan. Applied in: Task 4.
- **D3** (owner, `/deferred` pass, 2026-11-07): resume gap 1 uses the item's suggested marker: a stamped stage counts
  as new when no roadmap entry yet cites its plan's Handoff. Applied in: Task 3 Step 1.
- **D4** (owner, `/deferred` pass, 2026-11-07): resume gap 2 goes into the one Ask: name each unmet `Consumes` and the
  stage it blocks, propose a default such as adding a producing stage or amending the `Consumes`, and hand off only
  after the answer. Applied in: Task 3 Step 1.
- **D5** (owner, `/deferred` pass, 2026-11-07): plan items (a), (b), (c) and the dr-tracks re-runs together, as one
  plan. Applied in: the whole plan.
- **D6** (owner, plan review, 2026-11-07): "Approve as written". It covers the six defaults of Open for plan review,
  each as proposed, and keeps item 5's marker sentence as written. Applied in: Global Constraints (Arms, Spend),
  Task 1 Step 2, Task 3 Step 1, Task 4 Step 2.

## Open for plan review

Resolved at plan review on 2026-11-07: the owner approved each item as proposed and kept item 5's sentence (D6).

Defaults this plan settles. The owner approves or amends them as one batch.

1. **Route-case controls read `1844bd8`.** The routes already ship, so a control at `BASE79` would read the same text
   as the treatment. Plan 78's `BASE` shows whether the shipped text drives the behavior.
2. **The amended dr-known-progression is a new case key**, `dr-known-progression-79`. The old case and its rule stay
   as plan 78 recorded them. Its RED stands from plan 78's control (bar clause B fails in rep5), because the
   amendment touches conformance clause C only. That RED rests on the by-reference reading of clause B (plan 78's
   controller ruling); by the other reading plan 78's control is clean, which the summary reports.
3. **Guard re-runs.** Task 3's §5 edits can reach `dr-resume-rerank` and `dr-resume-legacy`, and its §7 step 4 phrase
   can reach `dr-offer-yes` and `dr-tracks`. Task 4 re-runs the first three as guards. The dr-tracks runs (D2) cover
   the fourth.
4. **dr-tracks reading of record.** Clause C is read as plan 78's Task 3 round 2 and Task 7 read it: an order of
   outcomes inside a known-progression track, not called stages, is not a stage list. The other reading (such an order
   is a stage list) is reported under "Other readings" for each run and does not count toward the bar. Fixing the
   reading before any rep keeps the verdict from being chosen after scoring.
5. **Marker text for a Handoff that amends nothing.** Task 3 Step 1 edit 1 says that a `None` Handoff is read again and
   changes nothing, as D3's option said. A Handoff whose bullets change no entry's fields (a trap, a deferred item) is
   also never cited, so it too is read again at each resume. Choose: keep the sentence as written, or widen it to "A
   Handoff that amends no entry, one that reads `None` included, is never cited, so a resume reads it again and
   changes nothing it has already reported."
6. **Spend stop at $30.** About 24 five-rep calls at about $0.62 each, a wording round included, is about $15.

---

### Task 1: six cases, the amended case and their leak check

**Files:**
- Modify: `specs/red-baseline-new-project-entry/kit/cases.py` (new constants and seven new `CASES` entries)
- Modify: `specs/red-baseline-new-project-entry.md` (append `## Plan 79: base, cases and leak check` and
  `## Plan 79: spend`)

**Interfaces:**
- Consumes: `case()`, `lines()`, `TODAY`, `STEP_TASK`, `DR`, `SEC_SPEC`, `LOCK_ROADMAP`, `PARKING_ROADMAP`,
  `DR_OFFER_YES_FIXTURE` and `DR_KNOWN_PROGRESSION_FIXTURE`, `DR_KNOWN_PROGRESSION_LEAK` from `cases.py`.
- Produces: `CASES` keys `dr-stop-track`, `dr-park-ranked`, `dr-name-collision`, `dr-rerank-second`,
  `dr-resume-marker`, `dr-resume-blocked` and `dr-known-progression-79`. Every one is `additive` with texts `DR`.

- [x] **Step 1: Record the base**

Append `## Plan 79: base, cases and leak check` to the record. Give `BASE79` (`git rev-parse HEAD` at the start, short
and full sha, and branch). Run
`git diff --stat a849bd2 BASE79 -- skills/derive-roadmap specs/red-baseline-new-project-entry`. Expected: no line for
a skill file. If one prints, stop and report it: the anchors may have moved.

- [x] **Step 2: Write the fixtures and rules in `cases.py`**

> Deviation: the fixtures needed judgment calls the brief did not give (a new four-stage `OCCUPANCY_ROADMAP`, two extra `PROMOTED_ROADMAP` edits, a reworded Completion line), recorded in the record under `Plan 79: fixture judgment calls`. A review round (`fee932a`) removed two additions (an untracked-file sentence in dr-name-collision and a changed plan 3 Handoff in dr-resume-blocked).

Each fixture is a `lines(...)` call that starts with `TODAY` and a repository line, as `DR_RESUME_RERANK_FIXTURE`
does. The state each one must hold is below. The implementer writes the fixture text. The pass rules are exact copy.

Two new roadmap constants:

- `TWO_TRACK_ROADMAP`: `LOCK_ROADMAP` with a second track. Tracks line:
  `Tracks: A — lock closures and river level (research). B — closure notices (known progression). Split from A because the notices serve boat operators whether or not the curve holds.`
  Outcome `O5 | An email notice to boat operators within an hour of a lock closing | B | 1 | small; basis: one
  closure-log poll each 10 minutes`. An unticked `Stage 2: Closure notices`, `Outcomes: O5`, `Track: B`,
  `Consumes: the closure log's live feed`, `ROUTING: writing-plans`, with `Objective`, `Produces`, `Exit` and
  `Leaves out` filled. Stage 1 and the `## Ranked list — Track A` section stay as in `LOCK_ROADMAP`.
- `PROMOTED_ROADMAP`: `LOCK_ROADMAP` after one re-rank. A resume on 2026-10-21 promoted O2 to `Stage 2: 7-day
  outlook`, which carries `(Resolved at resume, 2026-10-21)`, names `specs/lock-closures-stage-2-findings.md` in
  `Produces`, and is ticked with the stamp `Stage 2: COMPLETE (2026-11-04) — implemented by plan 6
  (specs/plans/completed/6-closure-outlook.md).` The Ranked list holds O3 then O4.

The six cases:

1. `dr-stop-track` (spec `plan 78 D6, §5 track stop`). Fixture: the partner asked to resume. Tools read
   `TWO_TRACK_ROADMAP`, plan 4's Handoff (`None`) and the Stage 1 findings (as `DR_RESUME_RERANK_FIXTURE`). An
   `[earlier] You` line in summary: you reported the finding and cost and asked one question: promote O2 as Stage 3,
   re-order, or stop Track A. `[now] Your partner: Stop Track A. The curve answers what we needed.` Task: `STEP_TASK`.

   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): the reply appends to specs/deferred_items.md one item for each of O2, O3 and O4, and no item for Stage 2 or O5.
   Clause B (bar): the roadmap stays live: it is not moved to specs/completed/, it is not marked PARKED, and Stage 2's entry stays.
   Clause C (conformance): the items sit under one dated section heading of the form `## <roadmap name> — 2026-11-06`.
   Clause D (conformance): each item has a `Size:` line and a `Done when:` line that names its outcome.
   Clause E (conformance): no completion review starts, and the reply hands off Stage 2 with a "Next:" line that names writing-plans and the roadmap, and plans nothing.
   Reading notes. Clause A: an item written in a tool call or as file content counts; a reply that only asks to confirm the stop fails A. Clause C: the roadmap name may be the file's stem or its title in kebab case. Clause E: a completion review is the audit run before a roadmap retires (derive-roadmap §6).
   ```

   Leak words: `r'one item per|PARKED|deferred_items|only that track'`.

2. `dr-park-ranked` (spec `§5 Parking, roadmap-format Ranked list`). Fixture: as `dr-stop-track` up to the question.
   `[now] Your partner: Park the whole roadmap. The canal study's funding ended.` Task: `STEP_TASK`.

   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): the reply appends to specs/deferred_items.md one item for each of Stage 2, O2, O3 and O4: four items.
   Clause B (bar): the roadmap moves to specs/completed/ and is marked PARKED with the date and "1 of 2 stages complete".
   Clause C (conformance): the items sit under one dated section heading of the form `## <roadmap name> — 2026-11-06`.
   Clause D (conformance): each item has a `Size:` line and a `Done when:` line that names the stage's Produces or the item's outcome.
   Clause E (conformance): no completion review starts, and no stage is handed off.
   Reading notes. Clause A: an item written in a tool call or as file content counts; one item that bundles the list items fails A. Clause B: any wording of the count passes when it says 1 complete of 2 stages; a count that includes list items fails. Clause C: as dr-stop-track's clause C.
   ```

   Leak words: `r'one item per|PARKED|deferred_items|stages complete'`.

3. `dr-name-collision` (spec `roadmap-format New-project roadmaps, name rule`). Fixture: the lines of
   `DR_OFFER_YES_FIXTURE` with its last line's `[now]` changed to `[earlier]`, then an `[earlier] You` line in summary: you sent the one message with the outcomes drawn from R1 to R11, one
   known-progression track and cost notes, and said the roadmap takes the spec's stem. Tools: `ls specs/` lists
   `sec-filing-index-ingestion-spec.md`, its ADR and `sec-filing-index-ingestion-spec-roadmap.md`. A read of that
   roadmap's first 12 lines shows the roadmap header and
   `Source: your partner's words, 2026-09-14. Background: none.`, for a filing-alert project.
   `[now] Your partner: Rank them in the order you listed. Go ahead and write the roadmap.` Task: `STEP_TASK`.
   Files: `{'spec': SEC_SPEC}`.

   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): the reply does not write specs/sec-filing-index-ingestion-spec-roadmap.md, by tool call or as file content.
   Clause B (bar): the reply asks the partner for another name and writes no roadmap file under any name before the answer.
   Clause C (conformance): the reply says that the existing file is not this spec's roadmap, and it does not resume it.
   Reading notes. Clause B: a name proposed inside the question passes; a file written under the proposed name fails. Clause C: any statement that the file's source is not this spec passes.
   ```

   Leak words: `r'overwrite|another name|collision|already exists'`.

4. `dr-rerank-second` (spec `§5 research track, most recently ticked stage`). Fixture: the partner asked to resume.
   Tools read `PROMOTED_ROADMAP`; `git log` (written 2026-10-14, Stage 1 stamped 2026-10-20, Stage 2 entry added
   2026-10-21, Stage 2 stamped 2026-11-04); plan 6's Handoff (`None`); the Stage 1 findings (as
   `DR_RESUME_RERANK_FIXTURE`); and `specs/lock-closures-stage-2-findings.md`:
   `Result: the outlook flagged 81% of closures at least 2 days ahead, with one false alarm in 9.` and
   `Cost of the real run: 14 minutes a day on one small VM, 0.3 GB of forecasts.` Task: `STEP_TASK`.

   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): no completion review starts, and the roadmap is neither parked nor retired.
   Clause B (bar): the reply reports Stage 2's finding and its measured cost.
   Clause C (bar): one question that asks for a re-ranking of O3 and O4 or the approval of a proposed next stage from them, with a default.
   Clause D (conformance): no new stage entry is written before the answer, and O2 is not offered again.
   Reading notes. Clause B: the finding is the 81% or the false-alarm rate; the cost is the 14 minutes a day or the 0.3 GB. Stage 1's finding reported as well passes; Stage 1's alone fails. Clause C: as dr-resume-rerank's clause C.
   ```

   Leak words: `r're-rank|promote|stop the track|most recently'`.

5. `dr-resume-marker` (spec `§5 resume gap 1, D3`). Roadmap: `PARKING_ROADMAP`'s domain, old format, four stages.
   Stages 1 and 2 are ticked and stamped (plans 3 and 5). Stage 3's `Consumes` already cites `plan 3, Handoff` with
   `(Resolved at resume, 2026-10-12)`. Tools: plan 3's Handoff has one bullet for Stage 3 (the one already applied).
   Plan 5's Handoff has one bullet: `occupancy_hourly` shipped as `occupancy_by_hour` with the same columns, which
   Stage 3 and Stage 4 consume. `git log` shows commits only, none labeled as a resume. `[now] Your partner: Resume
   the roadmap.` Task: `STEP_TASK`.

   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): the reply amends the Consumes of Stage 3 and Stage 4 from plan 5's Handoff bullet, citing plan 5, Handoff.
   Clause B (bar): no amendment re-applies or restates plan 3's Handoff bullet, which Stage 3's entry already cites.
   Clause C (conformance): the reply commits the amendments and hands off Stage 3 with a "Next:" line, and plans nothing.
   Reading notes. Clause A: a stated amendment counts, in a tool call or in the roadmap text. Clause B: naming plan 3's bullet as already applied passes; amending from it again fails.
   ```

   Leak words: `r'since the last resume|no entry yet cites|already cites'`.

6. `dr-resume-blocked` (spec `§5 resume gap 2, D4`). Roadmap: as `dr-resume-marker`, but plan 5's Handoff bullet reads:
   `occupancy_hourly` was not built, because the vendor feed has no bay ids, and Stage 3 and Stage 4 consume it.
   Stage 3's entry carries no citation yet. `[now] Your partner: Resume the roadmap.` Task: `STEP_TASK`.

   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): the reply hands off no stage before the answer: no "Next:" line names a stage.
   Clause B (bar): one question that names the unmet Consumes (occupancy_hourly) and the stages it blocks (3 and 4), with a proposed default.
   Clause C (conformance): the default adds a stage that produces it, or amends the Consumes.
   Clause D (conformance): no completion review starts, and the roadmap is not parked.
   Reading notes. Clause B: two or more separate questions fail B. Clause C: either default passes; a default that hands off Stage 3 as it stands fails C.
   ```

   Leak words: `r'blocked|unmet|no unticked stage'`.

The amended case:

7. `dr-known-progression-79` (spec `V2, R7-R9; plan 79 D1`): fixture, task, files and leak words of
   `dr-known-progression`. Its rule, `DR_KNOWN_PROGRESSION_PASS_79`, is `DR_KNOWN_PROGRESSION_PASS` with clause C
   replaced by:

   ```
   Clause C (conformance): manifests and traceability each appear in a named later stage. Point-in-time awareness is not scored for this fixture (owner ruling, 2026-11-07).
   ```

- [x] **Step 3: Check the cases load and build**

Run `uv run python -c "import sys; sys.path.insert(0, 'specs/red-baseline-new-project-entry/kit'); import cases; print(len(cases.CASES))"`.
Expected: `22`. Then
`CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py leakview /tmp/plan79-work/leak dr-stop-track dr-park-ranked dr-name-collision dr-rerank-second dr-resume-marker dr-resume-blocked dr-known-progression-79`.
Expected: `wrote 7 prompts to /tmp/plan79-work/leak`.

- [x] **Step 4: Run the leak check**

As the record's `## Leak check` does: grep each new case's hand-written fixture lines and task line, then its
leak-view prompt, case-insensitively, for its leak words. Expected: 0 hits in hand-written lines. Trace every
leak-view hit to its source and add the table to the record. Reword a hand-written line that hits, then rebuild into
`/tmp/plan79-work/leak-2`.

- [x] **Step 5: Start the spend table and commit**

> Deviation: two commits, `abe5ec3` and the review fix `fee932a`.

Append `## Plan 79: spend` with the stop ($30), the per-rep cap ($1.00) and a row per task. Then:

```bash
git add specs/red-baseline-new-project-entry/kit/cases.py specs/red-baseline-new-project-entry.md
git commit -m "test(specs): add plan 79's derive-roadmap resume and route cases"
```

### Task 2: control arms (RED)

**Files:**
- Create: `specs/red-baseline-new-project-entry/control/<case>/rep1.json` … `rep5.json` for the six new cases, and
  `control/p79-MANIFEST.txt`
- Modify: `specs/red-baseline-new-project-entry.md` (append `## Plan 79: control`)

**Interfaces:**
- Consumes: the six new `CASES` keys (Task 1).
- Produces: one control verdict per case (RED, or clean), which Task 3 reads.

- [x] **Step 1: Build the controls**

```bash
CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py 1844bd8 /tmp/plan79-work/control-routes dr-stop-track dr-park-ranked dr-name-collision dr-rerank-second
CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py <BASE79> /tmp/plan79-work/control-gaps dr-resume-marker dr-resume-blocked
```

Expected: `wrote 4 prompts …` and `wrote 2 prompts …`. Join the two `MANIFEST.txt` files into
`control/p79-MANIFEST.txt`, each under a line that names its sha.

- [x] **Step 2: Run five reps per case**

For each case: `bash specs/red-baseline-new-project-entry/kit/run_reps.sh /tmp/plan79-work/<build>/<case>.txt specs/red-baseline-new-project-entry/control/<case> 1 5 claude-opus-5-5 1.00`.
Check the spend headroom before each call. Rerun a VOID rep with the next free rep number.

- [x] **Step 3: Score and record**

Run `uv run python specs/red-baseline-new-project-entry/kit/show_reps.py specs/red-baseline-new-project-entry/control/<case>/`
for each case. Score each rep by hand, clause by clause. Write one `### Plan 79 control: <case>` section per case in
the record's Task 7 form (table, clause counts, one quote per failed clause, judgment calls). Name each case RED or
clean. Add the spend row.

- [x] **Step 4: Commit**

> Deviation: the plan's `git add specs/red-baseline-new-project-entry` stages the folder only, so the commit also staged the sibling record file. A second commit (`b4bf196`) recorded the controller's rulings on the readings and on the date conflict.

```bash
git add specs/red-baseline-new-project-entry
git commit -m "test(specs): run plan 79's control arms"
```

### Task 3: the resume gaps and wording gaps, then the treatment arms

**Files:**
- Modify: `skills/derive-roadmap/SKILL.md:164-165` (§5 marker), `:174-179` (§5 Ask), `:255-257` (§7 step 4)
- Modify: `skills/derive-roadmap/references/roadmap-format.md:42-46` (Consumes/Produces paragraph), `:126-127`
  (Ranked list)
- Create: `specs/red-baseline-new-project-entry/treatment/<case>-p79/rep1.json` … for the six new cases
- Modify: `specs/red-baseline-new-project-entry.md` (append `## Plan 79: treatment, Task 3`)

**Interfaces:**
- Consumes: Task 2's verdicts.
- Produces: the skill commit `T3`, which Task 4's re-runs read.

- [x] **Step 1: Edit the skill text**

> Deviation: three further skill commits followed the plan's five edits (`c500e14`, `T3`): `T3-r1` `43fca10` (the wording round of Step 4), and `T3-r2` `99265a5` and `T3-r3` `5f52dfc` (review-found fixes to the unmet-`Consumes` text and the Parking heading). The final skill text is `5f52dfc`.

Exact copy. Rewrap to the file's width. Change nothing else.

1. `SKILL.md` §5. Replace `For each stage stamped COMPLETE since the last resume, read the stamp and its plan's `## Handoff to later stages`.`
   with:
   `For each stage stamped COMPLETE whose plan's Handoff no roadmap entry yet cites (an amendment cites `plan <id>, Handoff`), read the stamp and that Handoff. A Handoff that reads `None` is never cited, so a resume reads it again and changes nothing.`
2. `SKILL.md` §5, the **Ask** bullet. After `ask for a single approve-or-amend.` insert:
   `When unticked stages remain and none has all its `Consumes` met, the same question names each unmet `Consumes` and the stages it blocks, with your proposed default: a stage added to produce it, or the `Consumes` amended. Hand off nothing before the answer.`
3. `SKILL.md` §7 step 4. Replace `the tracks and their kinds, and a proposed roadmap name.` with
   `the tracks and their kinds, and, with no spec, a proposed roadmap name.`
4. `roadmap-format.md`, the **Consumes/Produces are load-bearing** paragraph. Append:
   `A resume treats a stamped stage as new while no entry cites its plan's Handoff, and it asks when unticked stages remain and none has its `Consumes` met (SKILL.md §5).`
5. `roadmap-format.md`, Ranked list. Replace `or parks when the track stops (SKILL.md §5).` with
   `or parks when the track stops or the whole roadmap parks (SKILL.md §5).`

- [x] **Step 2: Check the edits**

Run each and expect `1`:
`tr '\n' ' ' < skills/derive-roadmap/SKILL.md | tr -s ' ' | /usr/bin/grep -c 'no roadmap entry yet cites'`,
the same for `'unticked stages remain and none has all its'`, `'Hand off nothing before the answer'` and `'and, with no spec, a proposed roadmap name'`, and on
`roadmap-format.md` for `'or the whole roadmap parks'` and `'treats a stamped stage as new'`. Expect `0` for
`'since the last resume'` in `SKILL.md`. Check the body size (Global Constraints). Run the commit gate, then commit:

```bash
git add skills/derive-roadmap/SKILL.md skills/derive-roadmap/references/roadmap-format.md
git commit -m "fix(derive-roadmap): specify the resume marker and the blocked-roadmap ask"
```

Record the sha as `T3` in the record.

- [x] **Step 3: Build and run the treatments**

`CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py <T3> /tmp/plan79-work/t3 dr-stop-track dr-park-ranked dr-name-collision dr-rerank-second dr-resume-marker dr-resume-blocked`.
Expected: `wrote 6 prompts …`. Copy its `MANIFEST.txt` to `treatment/p79-t3-MANIFEST.txt`. Run five reps per case
into `treatment/<case>-p79/`, as Task 2 Step 2 does.

- [x] **Step 4: Score, apply the bars, record**

> Deviation: dr-stop-track and dr-park-ranked missed their bar at `T3`. The wording round closed dr-stop-track. dr-park-ranked took the owner's ruling to re-run once more (3 of 5, then 4 of 5), and its met result rests on the inline-fields reading of clause D.

Score as Task 2 Step 3, in `### Plan 79 Task 3: <case>` sections, each ending with its bar verdict against its
control. For a miss, follow the Bars' wording round: the new text, its commit as `T3-r1`, the re-run cases with
`-r1`, and why each other case was not re-run. A second miss is an owner gate. Add the spend row.

- [x] **Step 5: Commit**

```bash
git add specs/red-baseline-new-project-entry
git commit -m "test(specs): run plan 79's treatment arms"
```

### Task 4: re-runs at the final text

**Files:**
- Create: `treatment/dr-known-progression-79-p79/`, `treatment/dr-tracks-p79a/`, `treatment/dr-tracks-p79b/`,
  `treatment/dr-resume-rerank-p79/`, `treatment/dr-resume-legacy-p79/`, `treatment/dr-offer-yes-p79/` (five reps each)
- Modify: `specs/red-baseline-new-project-entry.md` (append `## Plan 79: re-runs` and `## Plan 79: summary`)

**Interfaces:**
- Consumes: `T3`, or `T3-r1` when Task 3 ran a wording round (the last skill commit). Call it `T-final`.
- Produces: the verdicts the plan completion protocol reads to tick items (a) to (e).

- [x] **Step 1: Build and run**

> Deviation: `T-final` is `T3-r3` (`5f52dfc`), not `T3-r1`, because two review-found fixes followed the wording round.

`CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py <T-final> /tmp/plan79-work/t4 dr-known-progression-79 dr-tracks dr-resume-rerank dr-resume-legacy dr-offer-yes`.
Copy its `MANIFEST.txt` to `treatment/p79-t4-MANIFEST.txt`. Run five reps into each folder above. The two dr-tracks
runs are separate `run_reps.sh` calls from the same prompt, into `dr-tracks-p79a` and `dr-tracks-p79b`.

- [x] **Step 2: Score and apply the bars**

> Skipped: no wording round for the three Task 4 misses (dr-tracks runs a and b, dr-known-progression-79), because a fix would edit files on the plan's leave-alone list → deferred. → item: 79-derive-roadmap-resume-and-route-tests — 2026-11-07

Each verdict uses the case's rule and its reading of record (dr-tracks: Open for plan review item 4; every other case:
the reading plan 78's record applied to it). Other readings go under "Other readings", as the record's Task 7 sections
do, and never count toward a bar.

| Case | Bar | Compared with |
|---|---|---|
| dr-known-progression-79 | additive, rule `DR_KNOWN_PROGRESSION_PASS_79` | plan 78's control (RED from clause B, rep5) |
| dr-tracks, runs a and b | additive: each run passes at least 4 of 5 | plan 78's control |
| dr-resume-rerank | guard | plan 78's Task 7 fix round 1 arm |
| dr-resume-legacy | guard | plan 78's Task 7 fix round 1 arm |
| dr-offer-yes | guard | plan 78's Task 7 arm (3 of 5) |

For each dr-offer-yes and dr-tracks rep, also record, unscored, whether the reply proposes a roadmap name (§7 step 4's
phrase). With a spec (dr-offer-yes) the expected form is the stem. With no spec (dr-tracks) it is a proposed name. A
miss here takes no wording round of its own: Task 3's phrase is reworded only when a scored case misses.

- [x] **Step 3: Write the summary**

`## Plan 79: summary`: one table of every plan 79 arm (case, bar, control, treatment, result), the spend total, and
for each of items (a) to (e) whether its `Done when:` is met. Add the spend row.

- [x] **Step 4: Commit**

> Deviation: record-only commits followed the review and the final review (`9e4e89d`, `ad807f9`, `b30f3c9`).

```bash
git add specs/red-baseline-new-project-entry
git commit -m "test(specs): run plan 79's re-runs and summary"
```

## Plan completion

The Plan Completion Protocol ticks items (a) to (e) from Task 4's summary. An item whose `Done when:` is not met
stays open with a dated note, and a miss goes to the owner at the gate.
