# derive-roadmap: later qualities and spec references Implementation Plan

**Status: COMPLETE (2026-11-10)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Quarantine.** This plan, the spec, the record `specs/baseline/red-baseline-new-project-entry.md` and its folder
> name the cases, the pass rules and the expected behavior. Keep them out of every prompt. (Plan 78's quarantine,
> extended to this plan.)

**Goal:** Keep stage text out of derive-roadmap's one message, let a later quality join a research track's Ranked
list only after the owner approves and ranks it, and keep each outcome's spec references in a new-project roadmap
built from a spec.

**Architecture:** Three skill files change: `skills/derive-roadmap/SKILL.md` (§4, the §5 Ask bullet, §6, §7 steps 4
and 5, one Common-mistakes bullet), `references/new-project-entry.md` (The one message, Later qualities) and
`references/roadmap-format.md` (the Outcomes table, the Ranked list). Plan 78's micro-test kit gains three cases and a
two-step probe. Every result goes into plan 78's record, in new sections headed `Plan 85`.

**Tech Stack:** Markdown skill text; the stdlib Python kit in `specs/baseline/red-baseline-new-project-entry/kit/`;
`claude -p` reps on Opus 5.5.

**Spec:** `specs/completed/derive-roadmap-later-qualities-and-spec-refs.md` (APPROVED 2026-11-07, owner decisions D1–D8).
Requirements R1–R12 and verification items V1–V5 below are the spec's.

## Global Constraints

- **Execution base.** `BASE85` is the execution branch's start commit: the tip of `claude/charming-dhawan-c7855b`
  that holds this plan, or `main` once that branch has merged. Task 1 Step 1 records its sha. Line numbers below were
  taken at `91d49c4`. The old text in each step is the match key, not the line number. At `91d49c4` no derive-roadmap
  file differs from plan 79's `T-final` (`5f52dfc`).
- **Order of executions.** No execution starts while another plan executes in this repository (owner ruling,
  2026-10-28). Plan 84 (the finding-21 build plan) may be planned or executing at the same time. Start only when it
  is not executing.
- **One owner per file.** Only Task 3, and a wording round of Tasks 4 to 6, edit skill files. Task 1 writes the new
  constants and `CASES` entries in
  `cases.py`. Task 5 adds one `CASES` entry (`wp-stage-plan`), which needs a sha that exists only after its Step 1.
  Each task appends its own sections to the record.
- **Leave alone.** `references/gap-rubric.md`; §1's offer; the old-format roadmap rules (`roadmap-format.md` from its
  opening to the end of Stage stamps, and §5 as it reads an old-format roadmap); the definition of a known-progression
  track ("can name its stages from first to last"), which the plan 79 item for dr-tracks owns; `SKILL.md` outside the
  parts named in Architecture; every other skill; every existing case, rule, fixture, rep file and arm folder of the
  kit; the four case-study repositories.
- **Examples stay out of the fixtures (micro-test Channel 3).** New skill text adds no example. R5's interim entry
  is written as a placeholder form (`<quality>: suggested, see the approval question`), not as the spec's
  `traceability` example, because V3's fixture uses traceability. New fixtures reuse the kit's domains (canal locks
  and river gauges, SEC filings).
- **Compaction window.** The derive-roadmap SKILL.md body stays at most 20,000 characters
  (`len(check_conformance.skill_body(text)[0])`; 16,125 at `91d49c4`). No description changes.
- **Commit gate.** Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Commit messages
  follow Conventional Commits, use plain technical English and end with the attribution trailer that the executing
  session is given. A record commit stages both paths:
  `git add specs/baseline/red-baseline-new-project-entry specs/baseline/red-baseline-new-project-entry.md`
  (the folder alone does not stage the sibling record file).
- **Micro-tests.** Plan 78's kit and runner, unchanged: every rep is a fresh
  `claude -p --model claude-opus-5-5 --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format json --max-budget-usd <cap>`
  under `env -i`, from a new empty directory under `/tmp`. The cap is $1.00 unless a step says otherwise. Five reps
  per arm, except the probe (Task 5). Text is read with `git show`, never through `~/.claude/skills/`. Each pass rule
  is committed before any rep of its case runs. Every verdict is read by hand from the full reply, by the case's rule
  and by every reading in the record's Control sections, plan 79's sections and this plan's Open for plan review.
- **Arms run at the last skill commit.** Controls read every text at `BASE85`. Treatments, the probe and the guards
  read every text at the last skill commit that exists when they run. Any later skill commit (a wording round, a
  review-found fix, a final-review fix) re-runs, at the new commit and before the summary, every case whose decision
  the changed passage can reach. The record says why each other case was not re-run. A passage that no arm reads at
  the final text is named as untested in the summary.
- **Bars.** Plan 78's, unchanged.
  - *Additive:* the treatment passes every bar and conformance clause in at least 4 of 5 reps, and the control fails
    a bar clause in at least 1 of 5.
  - *Non-regression (guard):* the treatment passes at least as many reps as the named comparison arm, minus one.
  - A control with no failure never reverts a change. Record it and put it to the owner at the plan completion
    gate. A RED that comes only from a term the control text lacks is still RED: the record names the clause.
  - A treatment below its bar gets one wording round with the case's rule unchanged, then an owner ruling. An owner
    stop is not a subagent-driven-development blocker: the implementer leaves its files and ends with
    `BLOCKED (owner gate: Task N Step M)` (plan 78's D13).
- **Date reading.** Every fixture says "Today is 2026-11-06", and the CLI's own date line gives the run day. No clause
  of this plan scores a date. Where a reading turns on a date, the frame date and the run-day date both pass. This is
  set before any rep.
- **Spend.** The controller keeps the running total in the record's `Plan 85: spend` table. Stop and ask the owner
  before the total passes **$30**. Before each `run_reps.sh` call, check the total plus that call's worst case (reps ×
  cap). A task's spend is one `show_reps.py` run after its last rep. An unreadable or empty rep file counts at its cap.
- **Fixtures.** The sec-edgar spec is read at build time with `CASE_REPOS="$HOME/Projects"`, as plan 78's Fixtures
  constraint says. The case-study repositories are read only.
- **Folders.** Build folders go under `/tmp/plan85-work/`. Each build's `MANIFEST.txt` is copied into the record's
  folder as `control/p85-MANIFEST.txt` or `treatment/p85-<label>-MANIFEST.txt`. New control rep folders are
  `control/<case>/`, and V1's fresh control is `control/dr-offer-yes-p85/`. Treatment rep folders are
  `treatment/<case>-p85/`. A wording round adds `-r1`.
- **Public repository.** The plan, kit, record and commits hold no private detail.

## Review Focus

1. **A one message for a project where the check finds no later quality.** The person expects no qualities line and
   no stage word. No arm has such a fixture. Pinned in Task 3 Step 2: "With no quality to name, leave it out" is in
   `new-project-entry.md`. The summary names the path as untested.
2. **The owner declines a suggested quality.** The person expects `Leaves out` to read `<quality>: declined,
   <YYYY-MM-DD>` and no list item, no O-number. V3 stops before the answer. Pinned in Task 3 Step 2 by the decline
   form in `roadmap-format.md`. The summary names R6's answer path as untested.
3. **A sub-agent or non-interactive run writes a research-track roadmap that needs a later quality.** The person
   expects the provisional file to list it last in the Ranked list, with its next free O-number and `suggested, not
   approved`. Pinned in Task 3 Step 2 by that label. The summary names R9 as untested.
4. **A spec that is only background (the dr-known-progression fixture).** The person expects no `Spec` column, because
   the outcomes came from the partner's words. Pinned in Task 3 Step 2 ("gives no column") and recorded, unscored, on
   every `dr-known-progression-79` rep in Task 6.
5. **The completion review of a spec-sourced roadmap where a spec requirement has no outcome.** The person expects that
   requirement listed as unmet, with the two exits. Pinned in Task 3 Step 2 by the §6 sentence. The summary names R12
   as untested.

## Decisions

- **D1** (brief, 2026-11-10): the plan id is 85, because 84 is reserved for the finding-21 build plan. Applied in:
  this file's name.
- **D2** (brief, 2026-11-10): comparison arms and match keys come from plan 79's results (the record's
  `Plan 79: summary`), and plan 79 is not re-run. Applied in: Task 6 (the guard table).
- **D3** (brief, 2026-11-10): plan 79's three lessons are carried: the Date reading is set before any rep, arms run at
  the last skill commit with untested passages named, and a record commit stages the folder and its sibling `.md`.
  Applied in: Global Constraints.
- **D4** (owner, plan review, 2026-11-10): "Approve as written". It covers the nine defaults of Open for plan review,
  each as proposed, and confirms D1 to D3. Applied in: Global Constraints (Arms run at the last skill commit, Spend),
  Task 1 Step 2, Task 2 Step 3, Task 3 Step 1, Tasks 4 to 6.

## Open for plan review

Resolved at plan review on 2026-11-10: the owner approved each item as proposed and confirmed D1 to D3 (D4).

Defaults this plan settles. The owner approves or amends them as one batch. Each was open in the spec or is new here.

1. **V1's reading of record** (the spec asks the plan to fix it before any rep). dr-offer-yes clause C, and clause B's
   position reading, use plan 78's committed Stage list reading and its core-and-later-stages reading (record, Task 3
   summary), with the owner's ruling of 2026-11-07 as plan 79 Task 4 applied it:
   - A reply that sends later qualities or hardening to "later stages" inside the one message sets out stages and
     fails C, also when it names no core stage (plan 79 Task 4 rep4: "Under this plan, deployment and scheduling
     become named later stages in the track, not separate work.").
   - R2's line in its exact form names no stage. It is never a stage list and never a position. A form of the line
     that adds a stage word is read by the bullet above.
   - A passing mention of one stage ("The core stage measures it") is a passing reference, not a list (plan 79 Task 4).
   - Other readings are reported under "Other readings" and never count toward a bar.
2. **V1's control.** It runs fresh at `BASE85`, as the spec says. Its derive-roadmap text is byte-identical to
   `5f52dfc`, where plan 79 Task 4's dr-offer-yes arm passed 4 of 5 (clause C failed once). So the control may come
   back thin or clean. If it is clean, the additive bar cannot be met: the record says so, and the owner gets it at the
   completion gate. The deferred item's `Done when:` asks only that the wording lands and that a re-run passes 4 of 5
   by the core-and-later-stages reading. So a treatment at 4 of 5 or better meets the item whatever the control shows,
   and the summary reports both.
3. **V2's comparison arms** (Task 6's table). dr-tracks compares with plan 79's run a (3 of 5), not run b (2 of 5):
   against run b the guard needs only 1 of 5 and can catch no regression. `dr-resume-legacy` joins the guards, because
   R12 edits §6 and that case goes to §6 (about $0.26). Each guard keeps its reading of record from plan 79 or plan 78:
   dr-tracks the item-4 reading and the Stage word test, dr-park-ranked the inline-fields reading, dr-rerank-second
   the one-question reading, dr-known-progression-79 the Provenance on bytes and First stage per outcome readings.
4. **"With a spec" means a spec as the roadmap's `Source`.** A spec named only under `Background` gives no `Spec`
   column, because background never adds an outcome (`new-project-entry.md`, Inputs). The dr-known-progression-79 guard
   records, unscored, whether each reply writes the column.
5. **V3's design.** A canal-locks research fixture with one track. The later quality is traceability, and the
   partner's words state the need (the funding board will ask which gauge readings each estimate came from). The
   earlier one message, summarized, ends with R2's exact line, as it would at the new text. V3 has its own task line,
   because `ROADMAP_TASK` asks for a one-line message and R4's suggestion does not fit one line.
6. **V5's design.** Two steps. Step A: derive-roadmap at the last skill commit gets "Approved." for a fixed V4-style
   roadmap and writes the handoff. Step B: writing-plans, in a fresh session, gets step A's whole reply as the
   partner's message, plus reads of the roadmap and the spec, and writes the plan's header, Global Constraints and
   task list (not the steps). Step A runs one counted rep. Its first rep that is not VOID feeds step B (fixed before
   any rep). Step B runs 3 reps, and the probe passes when at least 2 of 3 pass. The spec says "one stage plan"; 3 reps
   make one plan's read less noisy for about $1. The text set is writing-plans' `SKILL.md` only: its two references
   serve the backlog and the history, which writing a stage plan does not reach. Step B reads whatever writing-plans
   holds at the last skill commit, which plan 84 may have changed by then. A step-B rep that stops on its budget is
   rerun at a $2.00 cap, recorded.
7. **Untested passages.** No arm tests R6's answer (approval and decline), R7 (a quality found at a resume), R9 (the
   provisional label), R12 (§6) or R11's brainstorming half. The summary names each. The alternative is one more case
   for R6's answer, with its control (about $1.50).
8. **Spend stop $30** (the spec's designer's call). Estimate about $16: controls about $2, treatments about $2, the
   probe about $1.50, the guards about $5, and one wording round each for Task 4 and Task 5.
9. **Paths.** "Organize red-baseline specs" (#157) merged before this plan was written. Every cited
   `specs/baseline/red-baseline-*` path is the current one.

---

### Task 1: three cases, the probe's step-B constants and their leak check

**Files:**
- Modify: `specs/baseline/red-baseline-new-project-entry/kit/cases.py` (new constants, one function, three new
  `CASES` entries)
- Modify: `specs/baseline/red-baseline-new-project-entry.md` (append `## Plan 85: base, cases and leak check` and
  `## Plan 85: spend`)

**Interfaces:**
- Consumes: `case()`, `lines()`, `edit()`, `TODAY`, `STEP_TASK`, `ROADMAP_TASK`, `DR`, `SEC_SPEC`,
  `DR_OFFER_YES_FIXTURE` from `cases.py`.
- Produces: `CASES` keys `dr-quality-suggest`, `dr-spec-column` (both `additive`, texts `DR`) and `dr-handoff-spec`
  (the probe's step A, texts `DR`); constants `WP = ['skills/writing-plans/SKILL.md']`, `ROADMAP_ASK_TASK`,
  `WP_TASK`, `SEC_SPEC_ROADMAP`, `WP_STAGE_PLAN_FIXTURE`, `WP_STAGE_PLAN_PASS`, `WP_STAGE_PLAN_LEAK`; and
  `rep_result(text: str) -> str`, which returns the `result` field of a rep's JSON and refuses (`SystemExit`) when it
  is missing or empty. Task 5 uses the last five.

- [x] **Step 1: Record the base**

Append `## Plan 85: base, cases and leak check` to the record. Give `BASE85` (short and full sha, and branch). Run
`git diff --stat 91d49c4 <BASE85> -- skills/derive-roadmap specs/baseline/red-baseline-new-project-entry` and
`git diff --stat 5f52dfc <BASE85> -- skills/derive-roadmap`. Expected: both print nothing. If a line prints, stop and
report it: an anchor or V1's premise may have moved. Run `claude --version`. If it is not `2.1.316`, run the isolation
probe as the record's "Isolation probe (Task 1 Step 5)" does, into `pilot/probe-p85/`, and record that all five lines
read `NO`. Record the blob sha of `skills/writing-plans/SKILL.md` at `BASE85` (`git rev-parse <BASE85>:skills/writing-plans/SKILL.md`):
plan 84 may change that file before Task 5 reads it.

- [x] **Step 2: Write the constants and cases in `cases.py`**

Each fixture is a `lines(...)` call that starts with `TODAY` and a repository line. The state each one must hold is
below. The implementer writes the fixture text. Pass rules and task lines are exact copy.

Task lines:

```python
ROADMAP_ASK_TASK = 'It is your turn. You have no tools in this turn. Write the full roadmap file you will commit now, as Markdown, then the message you send with it.'
WP_TASK = 'It is your turn. You have no tools in this turn. Write the start of the plan file you will save: its header, its Global Constraints and its task list, with each task\'s title, its Files block and one line on what the task delivers. Do not write the task steps.'
```

1. `dr-quality-suggest` (spec `V3, R4, R5`). Repository `lock-closures`, on `main`. `[earlier] Your partner:` asks for a
   roadmap for a study of canal lock closures, says nothing is built, and gives in plain words the four wants of
   `LOCK_ROADMAP`'s O1 to O4 in that order. The same message says that the canal trust's board funds the study and will
   ask which gauge readings each closure estimate came from. A `[you, tools]` line lists a scaffold repository (a
   README, `pyproject.toml`, an empty package and one smoke test; no file under `specs/`). An `[earlier] You` line in
   summary: your message gave the outcome list, unranked, O1 to O4, each with `LOCK_ROADMAP`'s cost note written with
   no stage word (O1 "measured by the first run on real data", O2 "one model run a day, small once O1's model exists;
   basis: the first fit's time", O3 "about 14 times the first run's data", O4 as it is); then the line
   `Qualities to place when the roadmap is written: traceability.`; then one research track, Track A, and the name
   `lock-closures`; and it asked your partner to rank the outcomes and confirm the track. `[now] Your partner: One
   research track is right. Rank them O1, O2, O3, O4. The name is fine. Go ahead.` Task: `ROADMAP_ASK_TASK`.

   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): the roadmap file holds no Ranked-list item, no O-number and no Outcomes row for traceability.
   Clause B (bar): the message after the file suggests traceability, with a reason that this project will need it, and asks the partner to approve it and, if approved, to give its place in Track A's ranking.
   Clause C (conformance): the approval of the partition and the request about traceability are one question.
   Clause D (conformance): the first stage's Leaves out names traceability as suggested or as waiting on the partner's answer.
   Clause E (conformance): the suggestion gives, in plain words, the outcome line that traceability would become.
   Reading notes. Clause A: a list line that names traceability fails A, numbered or not, labeled suggested or not; traceability named only in Leaves out or in the message passes. Clause B: a reason is any statement of why this project needs it, such as the board's question; a rank request that proposes a default place passes. Clause C: one question may offer options and close with them; two or more separate questions fail C. Clause D: any wording that marks traceability as not yet approved passes; a Ranked list named as its destination with no such mark fails D. Clause E: the outcome line says what the partner gets.
   ```

   Leak words: `r'suggest|approv|Leaves out|O5|not yet'`.

2. `dr-spec-column` (spec `V4, R10`). The lines of `DR_OFFER_YES_FIXTURE` with its last line's `[now]` changed to
   `[earlier]` (as `DR_NAME_COLLISION_FIXTURE` does), then an `[earlier] You` line in summary: you sent the one
   message: eleven outcomes, O1 to O11, one plain line each, drawn in order from R1 to R11; one track, a known
   progression; cost notes with their bases; and the roadmap takes the spec's stem. `[now] Your partner: Rank them in
   the order you listed. One track, a known progression. Go ahead and write the roadmap.` Task: `ROADMAP_TASK`.
   Files: `{'spec': SEC_SPEC}`.

   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): the Outcomes table has a column of spec refs, and every outcome row's cell in it holds at least one § or R ref of the spec.
   Clause B (bar): every cell of that column holds refs only.
   Clause C (conformance): the column is headed Spec and comes right after the Outcome column.
   Reading notes. Clause A: a ref is a § number (§4.2) or an R number (R1), alone, in a range (R1–R3) or in a list; refs written only inside an Outcome cell or a stage entry do not pass A. Clause B: a cell holds only § numbers, R numbers, ranges, commas and none; any other word fails B, such as a requirement's title ("R1 Baseline") or its text.
   ```

   Leak words: `r'Spec column|refs only|requirement text|restate'`.

3. `SEC_SPEC_ROADMAP`: a new-project roadmap for the sec-edgar spec in this plan's format (Task 3 edits 10 and 11):
   the roadmap header verbatim; `## Outcomes` with
   `Source: specs/sec-filing-index-ingestion-spec.md. Background: specs/sec-filing-index-ingestion-adr.md.` and
   `Choices made: none.`; an Outcomes table `| # | Outcome | Spec | Track | Rank | Cost (estimate; basis) |` with O1 to
   O11, one per requirement in order, every row in Track A at the rank of its number. Pinned cells: O1 `R1, §4.2`, O2
   `R2, §4.2`, O4 `R4, §4.1`, O9 `R9, §4.5`. Every other Spec cell holds its R number and the §4 section that details
   it, refs only. `Tracks: A — SEC filing indexes (known progression).` Four unticked stages, every field filled.
   Stage 1 is the core stage: `Outcomes: O1, O2`, `Consumes: nothing`,
   `Produces: specs/sec-filing-index-ingestion-spec-stage-1-findings.md, with the result and the measured cost of the real run`,
   an Exit on one real quarterly index and one real daily index parsed into the filing-index table on a local disk,
   with the measured time and data volume,
   `Leaves out: the versioned quarter manifest and its active pointer (O9, Stage 3); Azure orchestration (O4, Stage 4)`,
   `ROUTING: writing-plans`. Stages 2 to 4 cover every other outcome; Stage 3 holds O9 and Stage 4 holds O4. Then
   `## Stage-spec stamp` and `## Completion` as `LOCK_ROADMAP` has them, with this roadmap's path.

4. `dr-handoff-spec` (spec `V5 step A, R11`). The fixture of `dr-spec-column` with its last line's `[now]` changed to
   `[earlier]`, then `[you, tools] Wrote and committed specs/sec-filing-index-ingestion-spec-roadmap.md. Its full
   text:` and `SEC_SPEC_ROADMAP`, then an `[earlier] You` line in summary: you sent the stage partition for approval
   in one message. `[now] Your partner: Approved.` Task: `STEP_TASK`. Files: `{'spec': SEC_SPEC}`. Kind `additive`
   (the kit has two kinds; the probe applies no bar to step A).

   ```
   Probe step A. No PASS rule: both clauses are recorded, and the probe's verdict is read from step B.
   Clause A (recorded): the reply hands off Stage 1 to writing-plans with a "Next:" line and stops.
   Clause B (recorded): the reply names Stage 1's scope for the receiver: its O-numbers, the spec refs they carry, and what its Leaves out names.
   ```

   Leak words: `r'Scope:|scoped to|minus|leave out'`.

5. `WP_STAGE_PLAN_FIXTURE`, `WP_STAGE_PLAN_PASS` and `WP_STAGE_PLAN_LEAK` (spec `V5 step B`), no `CASES` entry yet.
   Fixture: `TODAY` and `The repository is \`sec-edgar\`, on branch \`main\`. This session is new.`; then
   `[earlier] Your partner pasted the message that ended the derive-roadmap session:`, `{file:handoff}` and
   `[end of the pasted message]`; then `[you, tools] Read specs/sec-filing-index-ingestion-spec-roadmap.md. Its full
   text:` and `SEC_SPEC_ROADMAP`; then `[you, tools] Read specs/sec-filing-index-ingestion-spec.md. Its full text:`
   and `{file:spec}`; then `[you, tools] Ran the plan-id check from the repository root. It printed: plan ids: none
   yet; next free: 1; collisions: none.` Leak words: `r'Scope:|scoped to|minus|leave out'`.

   ```
   PASS needs both bar clauses. Clause C is recorded.
   Clause A (bar): the plan cites as its scope R1, R2 and §4.2, the refs that the Spec cells of Stage 1's outcomes (O1 and O2) hold.
   Clause B (bar): no task and no Global Constraint builds the versioned quarter manifest or its active pointer (R9, §4.5) or Azure orchestration (R4: ADF, Container Apps Jobs, ADLS, Table Storage), the two qualities that Stage 1's Leaves out names.
   Clause C (recorded): the header carries the line Roadmap: specs/sec-filing-index-ingestion-spec-roadmap.md, Stage 1.
   Reading notes. Clause A: a citation in the header, the Spec line, Global Constraints or a task line counts; a range that covers a ref counts (R1–R2); a citation of the whole spec alone does not. Clause B: a task builds a quality when its title, Files block or line delivers it; a line that names a quality as out of scope passes, and so does a local stand-in such as a local directory in place of ADLS.
   ```

- [x] **Step 3: Check the cases load and build**

Run
`uv run python -c "import sys; sys.path.insert(0, 'specs/baseline/red-baseline-new-project-entry/kit'); import cases; print(len(cases.CASES))"`.
Expected: `25`. Then
`CASE_REPOS="$HOME/Projects" uv run python specs/baseline/red-baseline-new-project-entry/kit/build_prompts.py leakview /tmp/plan85-work/leak dr-quality-suggest dr-spec-column dr-handoff-spec`.
Expected: `wrote 3 prompts to /tmp/plan85-work/leak`.

- [x] **Step 4: Run the leak check**

As the record's `## Leak check` does: grep each new case's hand-written fixture lines and task line, then its
leak-view prompt, case-insensitively, for its leak words. Do the same for the hand-written lines of
`WP_STAGE_PLAN_FIXTURE` and `WP_TASK` (its leak view comes in Task 5). Expected: 0 hits in hand-written lines. Trace
every leak-view hit to its source (a case-repository file read verbatim is exempt) and add the table to the record.
Reword a hand-written line that hits, then rebuild into `/tmp/plan85-work/leak-2`. Also grep the three leak-view
prompts for `red-baseline`, `plan 7[89]`, `plan 85`, `micro-test` and `quarantine`. Expected: 0 hits.

- [x] **Step 5: Start the spend table and commit**

Append `## Plan 85: spend` with the stop ($30), the per-rep cap ($1.00) and a row per task. Then:

```bash
git add specs/baseline/red-baseline-new-project-entry/kit/cases.py specs/baseline/red-baseline-new-project-entry.md
git commit -m "test(specs): add plan 85's derive-roadmap quality and spec-ref cases"
```

### Task 2: control arms (RED), before any skill edit

**Files:**
- Create: `specs/baseline/red-baseline-new-project-entry/control/dr-offer-yes-p85/`, `control/dr-quality-suggest/`,
  `control/dr-spec-column/` (`rep1.json` … `rep5.json` each), and `control/p85-MANIFEST.txt`
- Modify: `specs/baseline/red-baseline-new-project-entry.md` (append `## Plan 85: control`)

**Interfaces:**
- Consumes: `CASES` keys `dr-offer-yes`, `dr-quality-suggest`, `dr-spec-column` (Task 1).
- Produces: one control verdict per case (RED, thin or clean), which Task 4 reads.

- [x] **Step 1: Build the controls**

`CASE_REPOS="$HOME/Projects" uv run python specs/baseline/red-baseline-new-project-entry/kit/build_prompts.py <BASE85> /tmp/plan85-work/control dr-offer-yes dr-quality-suggest dr-spec-column`.
Expected: `wrote 3 prompts to /tmp/plan85-work/control`. Copy its `MANIFEST.txt` to `control/p85-MANIFEST.txt`.

- [x] **Step 2: Run five reps per case**

`bash specs/baseline/red-baseline-new-project-entry/kit/run_reps.sh /tmp/plan85-work/control/<case>.txt specs/baseline/red-baseline-new-project-entry/control/<folder> 1 5 claude-opus-5-5 1.00`,
with `<folder>` `dr-offer-yes-p85`, `dr-quality-suggest` and `dr-spec-column`. Check the spend headroom before each
call. Rerun a VOID rep with the next free rep number.

- [x] **Step 3: Score and record**

Run `uv run python specs/baseline/red-baseline-new-project-entry/kit/show_reps.py <folder>` for each folder. Score each
rep by hand, clause by clause, dr-offer-yes by Open for plan review item 1. Write one `### Plan 85 control: <case>`
section per case in the record's Task 7 form (table, clause counts, one quote per failed clause, judgment calls,
other readings). Name each case RED, thin (a bar clause fails in exactly 1 of 5) or clean. For dr-offer-yes, set the
control beside plan 79 Task 4's arm at the same derive-roadmap text, and record for each rep, unscored, whether the
reply carries a line that names later qualities. Add the spend row.

- [x] **Step 4: Commit**

```bash
git add specs/baseline/red-baseline-new-project-entry specs/baseline/red-baseline-new-project-entry.md
git commit -m "test(specs): run plan 85's control arms"
```

### Task 3: the skill text

**Files:**
- Modify: `skills/derive-roadmap/SKILL.md:133-155` (§4), `:177-187` (§5 Ask), `:227` (§6), `:263-275` (§7 steps 4
  and 5), `:311-313` (Common mistakes)
- Modify: `skills/derive-roadmap/references/new-project-entry.md:60-76` (The one message), `:97-106` (Later qualities)
- Modify: `skills/derive-roadmap/references/roadmap-format.md:100-105` (Outcomes table), `:122-131` (Ranked list)
- Modify: `specs/baseline/red-baseline-new-project-entry.md` (append `## Plan 85: skill text`)

**Interfaces:**
- Consumes: nothing from earlier tasks. The controls (Task 2) must be committed first.
- Produces: the skill commit `T` (the last skill commit after this task's review), which Tasks 4 to 6 read. The
  exact phrases that later tasks and the probe rely on: the qualities line
  `Qualities to place when the roadmap is written: <names>.`; the handoff line `Scope: …`; the interim entry
  `<quality>: suggested, see the approval question`; the decline entry `<quality>: declined, <YYYY-MM-DD>`; the label
  `suggested, not approved`; the `Spec` column after `Outcome`.

- [x] **Step 1: Edit the skill text**

Exact copy. Rewrap to the file's width. Change nothing else. "Old" is the match key at `BASE85`.

`SKILL.md`:

1. §4, R4. Old: `Present the stage partition for approval before stage 1. On approval,`. New:
   `Present the stage partition for approval before stage 1. In a new-project roadmap, ask for the approval as ONE question. A later quality that a research-track stage's `Leaves out` sends to the Ranked list is suggested inside it: its name, one line on why this project will need it, and the outcome line it would become. The same question asks your partner to approve the quality and, if they do, to give its place in the track's ranking. Record the answer per `references/roadmap-format.md` (Ranked list). On approval,`
2. §4, R11, the ROUTING writing-plans bullet. Old:
   `the plan is scoped to the stage entry's `Spec` refs, or its `Outcomes` refs in a new-project roadmap.` New:
   `the plan is scoped to the stage entry's `Spec` refs, or, in a new-project roadmap, to its `Outcomes` (with a spec, to the Scope line below).`
3. §4, R11. Insert this bullet before `- Then stop.`:
   `- In a new-project roadmap with a spec, put one more line under the "Next:" line, for the receiver to carry with it: `Scope: <the stage's O-numbers> — spec <the refs their Spec cells hold>; leave out <each quality the stage's Leaves out names>.` The stage plan, or the stage spec's inputs under brainstorming, cover that scope and no more.`
4. §5 Ask, R7. Old: `Otherwise it counts as met, and the receiving session checks it.` New:
   `Otherwise it counts as met, and the receiving session checks it. A later quality that this resume finds for the first time, bound for a research track's Ranked list, joins the same question in §4's form.`
5. §6, R12. Old: `In a new-project roadmap, run it over the Outcomes list in place of spec requirements.` New:
   `In a new-project roadmap, run it over the Outcomes list in place of spec requirements. When its `Source` is a spec, also list each numbered spec requirement that no outcome's `Spec` cell cites, as unmet.`
6. §7 step 4, R1 and R2. Old: `4. **One message.** Before any roadmap text, send one message: the outcome list,`. New:
   `4. **One message.** Before any roadmap text, check the project against the later qualities (`references/new-project-entry.md`, Later qualities). Then send one message: the outcome list,`
   Then old: `with no spec, a proposed roadmap name. It makes one request:`. New:
   `with no spec, a proposed roadmap name. When the check finds a quality the project will need, one line follows the outcome list, in exactly this form, names only: `Qualities to place when the roadmap is written: <names>.` The message names no stage, core or later: stages come only after your partner ranks. It makes one request:`
7. §7 step 5, R3. Old:
   `A quality the project needs eventually but not to work goes to a named later stage or a Ranked-list item, never into a core stage's Exit.`
   New:
   `Now check the project against the later qualities, and place every one it will need. In a known progression it goes to a named later stage. In a research track it is suggested at the approval (§4), and it joins the Ranked list only once your partner approves and ranks it. None goes into a core stage's Exit.`
8. Common mistakes, last bullet. Old: `go to a named later stage or a Ranked-list item, recorded in `Leaves out`.` New:
   `go to a named later stage, or to a Ranked-list item once your partner approves it, recorded in `Leaves out`.`

`references/new-project-entry.md`:

9. The one message, R1 and R2. Old: `1. the numbered outcome list, unranked, each line with its cost note;`. New:
   `1. the numbered outcome list, unranked, each line with its cost note, then the qualities line below when it applies;`
   Then insert this paragraph before `Do not rank for your partner unless they ask`:
   `The qualities line reads, in exactly this form: `Qualities to place when the roadmap is written: <names>.` It gives names only, from the check under Stages (Later qualities): no reason, and none of the words "stage", "core", "first" or "later". With no quality to name, leave it out. The message names no stage, core or later, the rule that SKILL.md §1's offer already states: stages come only after your partner ranks the outcomes.`
10. Later qualities, R3. Old, from the bullet's start to `A core stage's Exit never requires one.`:
    `- **Later qualities.** A quality the project needs eventually but not to work goes to a named later stage in a known progression, or to a Ranked-list item in a research track. Examples: manifests, traceability, point-in-time awareness, full validation suites, scheduling and deployment. Check the project against each one, and place every one it will need. A core stage's Exit never requires one.`
    New:
    `- **Later qualities.** A quality the project needs eventually but not to work. Examples: manifests, traceability, point-in-time awareness, full validation suites, scheduling and deployment. Check the project against each one before the one message, and name each one it will need only in that message's qualities line. When you write the stages, check again and place every one it will need. In a known progression, each goes to a named later stage. In a research track, each is suggested at the approval (SKILL.md §4) and joins the Ranked list only once your partner approves and ranks it (`roadmap-format.md`, Ranked list). A core stage's Exit never requires one.`

`references/roadmap-format.md`:

11. Outcomes table, R10. In the Outcomes code block, old:
    `| # | Outcome | Track | Rank | Cost (estimate; basis) |` / `|---|---|---|---|---|` /
    `| O1 | <what your partner gets> | A | 1 |`. New:
    `| # | Outcome | Spec | Track | Rank | Cost (estimate; basis) |` / `|---|---|---|---|---|---|` /
    `| O1 | <what your partner gets> | <§ and R refs> | A | 1 |` (the rest of the O1 row unchanged). Then insert this
    paragraph before `Stage entries carry these fields and nothing else.`:
    `When `Source` is a spec, the `Spec` cell holds the § and R refs that the outcome came from: refs only, never requirement text, and `none` for an outcome that no spec section asks for. When `Source` is not a spec, leave the column out. A spec named only under `Background` gives no column.`
12. Ranked list, R5, R6, R8 and R9. Insert this paragraph before `An item leaves the list when your partner promotes it`:
    `A later quality joins a Ranked list only as an outcome your partner approved and ranked (SKILL.md §4). Until the answer, the stage's `Leaves out` names it as `<quality>: suggested, see the approval question`, and it has no list item, no O-number and no Outcomes row. On approval it takes the next free O-number, an Outcomes row (its outcome line, its `Spec` refs or `none` when `Source` is a spec, the track, your partner's rank and a cost note) and its ranked place in the list, and the `Leaves out` entry points at it by O-number. On a decline, the entry reads `<quality>: declined, <YYYY-MM-DD>`, and no item is made. From approval on it is an ordinary outcome, with no special case at a resume, at parking or in the completion review. When the session cannot ask, the provisional file lists each suggested quality at the end of the Ranked list, with its next free O-number and the label `suggested, not approved`.`

- [x] **Step 2: Check the edits**

For each row, run `tr '\n' ' ' < <file> | tr -s ' ' | /usr/bin/grep -o -F '<phrase>' | wc -l` and expect the count.

| File | Phrase | Count |
|---|---|---|
| `SKILL.md` | `Qualities to place when the roadmap is written: <names>.` | 1 |
| `SKILL.md` | `The message names no stage, core or later` | 1 |
| `SKILL.md` | `put one more line under the` | 1 |
| `SKILL.md` | `ask for the approval as ONE question` | 1 |
| `SKILL.md` | `against the later qualities, and place every one it will need` | 1 |
| `SKILL.md` | `joins the same question in §4` | 1 |
| `SKILL.md` | `cell cites, as unmet` | 1 |
| `SKILL.md` | `and, with no spec, a proposed roadmap name` | 1 |
| `SKILL.md` | `to a Ranked-list item once your partner approves it` | 1 |
| `SKILL.md` | `or a Ranked-list item, never into a core stage` | 0 |
| `new-project-entry.md` | `Qualities to place when the roadmap is written: <names>.` | 1 |
| `new-project-entry.md` | `With no quality to name, leave it out` | 1 |
| `new-project-entry.md` | `When you write the stages, check again and place every one it will need` | 1 |
| `new-project-entry.md` | `Check the project against each one, and place every one it will need` | 0 |
| `roadmap-format.md` | `| # | Outcome | Spec | Track | Rank |` | 1 |
| `roadmap-format.md` | `suggested, see the approval question` | 1 |
| `roadmap-format.md` | `declined, <YYYY-MM-DD>` | 1 |
| `roadmap-format.md` | `suggested, not approved` | 1 |
| `roadmap-format.md` | `gives no column` | 1 |

Then
`uv run --with pyyaml python -c "import sys; sys.path.insert(0, 'build'); import check_conformance as c; print(len(c.skill_body(open('skills/derive-roadmap/SKILL.md').read())[0]))"`.
Expected: a number at most 20,000 (about 17,500). Run `uv run python build/check_links.py` and the commit gate.

- [x] **Step 3: Commit, then record `T`**

```bash
git add skills/derive-roadmap/SKILL.md skills/derive-roadmap/references/new-project-entry.md skills/derive-roadmap/references/roadmap-format.md
git commit -m "feat(derive-roadmap): suggest later qualities at approval and keep spec refs"
```

Append `## Plan 85: skill text` to the record: the sha as `T`, the body size, and the edit numbers each requirement
maps to (R1 6, 9; R2 6, 9; R3 7, 10; R4 1; R5, R6, R8, R9 12; R7 4; R10 11; R11 2, 3; R12 5). A fix found by this
task's review is a further skill commit here, before Task 4 runs: the record names the last one as `T`. Commit the
record as Task 2 Step 4 does, with the message `test(specs): record plan 85's skill commit`.

### Task 4: treatment arms for V1, V3 and V4

**Files:**
- Create: `treatment/dr-offer-yes-p85/`, `treatment/dr-quality-suggest-p85/`, `treatment/dr-spec-column-p85/` (five
  reps each), `treatment/p85-t4-MANIFEST.txt`
- Modify: `specs/baseline/red-baseline-new-project-entry.md` (append `## Plan 85: treatment, Task 4`)

**Interfaces:**
- Consumes: `T` (Task 3) and Task 2's verdicts.
- Produces: the verdicts for V1, V3 and V4, and the last skill commit after any wording round here (`T-r1` or `T`),
  which Tasks 5 and 6 read.

- [x] **Step 1: Build and run**

`CASE_REPOS="$HOME/Projects" uv run python specs/baseline/red-baseline-new-project-entry/kit/build_prompts.py <T> /tmp/plan85-work/t4 dr-offer-yes dr-quality-suggest dr-spec-column`.
Expected: `wrote 3 prompts to /tmp/plan85-work/t4`. Copy its `MANIFEST.txt` to `treatment/p85-t4-MANIFEST.txt`. Run
five reps per case into the folders above, as Task 2 Step 2 does.

- [x] **Step 2: Score, apply the bars, record**

Score as Task 2 Step 3, in `### Plan 85 Task 4: <case>` sections, each ending with its bar verdict against its
control. dr-offer-yes uses Open for plan review items 1 and 2. For each dr-offer-yes rep, also record, unscored (V1's
line note): whether the reply carries R2's line, and whether the line keeps its form (names only, no reason, no stage
word). For a miss, follow the Bars' wording round: the new text, its commit as `T-r1`, the re-run cases with `-r1`, and
why each other case was not re-run. A second miss is an owner gate. Add the spend row.

- [x] **Step 3: Commit**

```bash
git add specs/baseline/red-baseline-new-project-entry specs/baseline/red-baseline-new-project-entry.md
git commit -m "test(specs): run plan 85's treatment arms"
```

> Deviation: commit `003423a` corrected the record's counts for the other readings after the task review (a controller
> hand fix, one file, wording only). The rest followed the plan.

### Task 5: the stage-plan probe (V5)

**Files:**
- Create: `treatment/dr-handoff-spec-p85/rep1.json` (or the first rep that is not VOID),
  `treatment/wp-stage-plan-p85/rep1.json` … `rep3.json`, `treatment/p85-t5-MANIFEST.txt`
- Modify: `specs/baseline/red-baseline-new-project-entry/kit/cases.py` (add the `wp-stage-plan` `CASES` entry)
- Modify: `specs/baseline/red-baseline-new-project-entry.md` (append `## Plan 85: probe`)

**Interfaces:**
- Consumes: the last skill commit after Task 4 (`T-probe`); `dr-handoff-spec`, `WP`, `WP_TASK`,
  `WP_STAGE_PLAN_FIXTURE`, `WP_STAGE_PLAN_PASS`, `WP_STAGE_PLAN_LEAK` and `rep_result` (Task 1).
- Produces: the probe verdict, and the last skill commit after any wording round here, which Task 6 reads.

- [x] **Step 1: Run step A and commit its rep**

`CASE_REPOS="$HOME/Projects" uv run python specs/baseline/red-baseline-new-project-entry/kit/build_prompts.py <T-probe> /tmp/plan85-work/t5a dr-handoff-spec`.
Expected: `wrote 1 prompts to /tmp/plan85-work/t5a`. Run
`bash specs/baseline/red-baseline-new-project-entry/kit/run_reps.sh /tmp/plan85-work/t5a/dr-handoff-spec.txt specs/baseline/red-baseline-new-project-entry/treatment/dr-handoff-spec-p85 1 1 claude-opus-5-5 1.00`.
A VOID rep is rerun with the next free number. The first rep that is not VOID feeds step B: no other rep is chosen.
Record its two recorded clauses and quote its handoff. Commit the rep folder and the record as Task 2 Step 4 does,
with the message `test(specs): run plan 85's probe step A`. Call this commit `PROBE_A`.

- [x] **Step 2: Add the step-B case and check it**

Add to `CASES`:

```python
'wp-stage-plan': case('V5 step B, R11', 'additive', WP, WP_STAGE_PLAN_FIXTURE, WP_TASK, WP_STAGE_PLAN_PASS,
                      WP_STAGE_PLAN_LEAK,
                      {'spec': SEC_SPEC,
                       'handoff': {'repo': 'agent-skills', 'commit': '<PROBE_A full sha>',
                                   'path': 'specs/baseline/red-baseline-new-project-entry/treatment/dr-handoff-spec-p85/rep<N>.json',
                                   'derive': rep_result}}),
```

`<N>` is the rep that Step 1 chose. `$CASE_REPOS/agent-skills` is this repository's main checkout, which shares its
objects with every worktree, so `git show <PROBE_A>:<path>` reads the committed rep. Check that the case count prints
`26`. Build `leakview /tmp/plan85-work/leak-5 wp-stage-plan`, and grep it for `WP_STAGE_PLAN_LEAK`'s words and the
Task 1 Step 4 quarantine words. Hits inside the pasted handoff are expected when step A wrote a `Scope:` line: it is
the output under test, not a hand-written line. Trace and record every hit. Then commit, so that the case is committed
before any of its reps runs:

```bash
git add specs/baseline/red-baseline-new-project-entry/kit/cases.py specs/baseline/red-baseline-new-project-entry specs/baseline/red-baseline-new-project-entry.md
git commit -m "test(specs): add plan 85's probe step-B case"
```

- [x] **Step 3: Run step B**

`CASE_REPOS="$HOME/Projects" uv run python specs/baseline/red-baseline-new-project-entry/kit/build_prompts.py <T-probe> /tmp/plan85-work/t5b wp-stage-plan`.
Expected: `wrote 1 prompts to /tmp/plan85-work/t5b`. Join the two `MANIFEST.txt` files into
`treatment/p85-t5-MANIFEST.txt`. Run three reps:
`bash specs/baseline/red-baseline-new-project-entry/kit/run_reps.sh /tmp/plan85-work/t5b/wp-stage-plan.txt specs/baseline/red-baseline-new-project-entry/treatment/wp-stage-plan-p85 1 3 claude-opus-5-5 1.00`.
A rep that stops on its budget is rerun at a $2.00 cap with the next free number, and the record says so.

- [x] **Step 4: Read each plan against the spec**

For each step-B rep, read the reply against `specs/sec-filing-index-ingestion-spec.md` §3 (R1, R2, R4, R9), §4.1,
§4.2 and §4.5 at `22c6767f`, clause by clause, in a `### Plan 85 probe` section. The probe passes when at least 2 of 3
reps pass clauses A and B. The section says that a pass cannot show that the `Scope:` line caused it, because
`SEC_SPEC_ROADMAP` already carries Stage 1's Spec refs and its `Leaves out`, and it gives the blob sha of
`skills/writing-plans/SKILL.md` at `T-probe` beside the one that Task 1 Step 1 recorded. On a fail, run one wording round on edits 2 and 3 only (R11's handoff text, the only text
this spec can change for it), commit it, re-run Step 1 and Steps 2 and 3 with `-r1` folders and the entry pointed at
the new step-A commit (record both shas), then put the result to the owner. Add the spend row.

- [x] **Step 5: Commit**

```bash
git add specs/baseline/red-baseline-new-project-entry specs/baseline/red-baseline-new-project-entry.md
git commit -m "test(specs): run plan 85's stage-plan probe"
```

### Task 6: the guards at the final text, and the summary

**Files:**
- Create: `treatment/<case>-p85/` (five reps each) for the nine guards below, `treatment/p85-t6-MANIFEST.txt`
- Modify: `specs/baseline/red-baseline-new-project-entry.md` (append `## Plan 85: guards` and `## Plan 85: summary`)

**Interfaces:**
- Consumes: the last skill commit, `T-final` (after any Task 4 or Task 5 wording round).
- Produces: the verdicts that the plan completion protocol reads to tick the three items.

- [x] **Step 1: Build and run**

`CASE_REPOS="$HOME/Projects" uv run python specs/baseline/red-baseline-new-project-entry/kit/build_prompts.py <T-final> /tmp/plan85-work/t6 dr-offer-scaffold dr-tracks dr-known-progression-79 dr-research-depth dr-resume-rerank dr-rerank-second dr-stop-track dr-park-ranked dr-resume-legacy`.
Expected: `wrote 9 prompts to /tmp/plan85-work/t6`. Copy its `MANIFEST.txt` to `treatment/p85-t6-MANIFEST.txt`. Run
five reps per case into `treatment/<case>-p85/`.

- [x] **Step 2: Score and apply the guard bar**

Each case is read as a guard (plan 79's "additive in `cases.py`, read as a guard here"), by its rule and its reading of
record (Open for plan review item 3). Other readings go under "Other readings" and never count.

| Case | Compared with (record section) | Arm PASS | Guard needs |
|---|---|---|---|
| dr-offer-scaffold | plan 78 "Task 7: dr-offer-scaffold" (`f824492`) | 5 of 5 | 4 |
| dr-tracks | plan 79 "Plan 79 Task 4: dr-tracks, run a" (`5f52dfc`) | 3 of 5 | 2 |
| dr-known-progression-79 | plan 79 "Plan 79 Task 4: dr-known-progression-79" | 3 of 5 | 2 |
| dr-research-depth | plan 78 "Fix round 1: dr-research-depth" (`d3fc772`) | 5 of 5 | 4 |
| dr-resume-rerank | plan 79 "Plan 79 Task 4: dr-resume-rerank" | 5 of 5 | 4 |
| dr-rerank-second | plan 79 "Plan 79 Task 3 round 3: dr-rerank-second" (`5f52dfc`) | 5 of 5 | 4 |
| dr-stop-track | plan 79 "Plan 79 Task 3 round 3: dr-stop-track" | 5 of 5 | 4 |
| dr-park-ranked | plan 79 "Plan 79 Task 3 round 3: dr-park-ranked" | 4 of 5 | 3 |
| dr-resume-legacy | plan 79 "Plan 79 Task 4: dr-resume-legacy" | 5 of 5 | 4 |

Also record, unscored: for each dr-tracks rep, V1's line note (as Task 4 Step 2) and whether clause C would pass at 4
of 5 for the plan 79 item that this case keeps open; for each dr-known-progression-79 rep, whether its roadmap writes a
`Spec` column (Review Focus 4); for each dr-research-depth rep, whether the reply suggests a later quality and where its
roadmap puts it. A guard below its bar gets the Bars' wording round, then an owner ruling.

- [x] **Step 3: Write the summary**

`## Plan 85: summary`: one table of every plan 85 arm (case, bar, control, treatment, result); the probe verdict; the
spend total; for each of the three items in the Plan completion section, whether its `Done when:` is met; the
untested passages (Open for plan review item 7, and any passage that changed after the arm that reads it); and the
owner-gate list. Add the spend row.

- [x] **Step 4: Commit**

```bash
git add specs/baseline/red-baseline-new-project-entry specs/baseline/red-baseline-new-project-entry.md
git commit -m "test(specs): run plan 85's guards and summary"
```

> Deviation: Task 6 ran as six commits where the plan names one: the reps (`85156d1`), the scores of the first five
> cases (`c1acd56`) and of the last four (`0beb489`), two record fixes after review (`f043608`, `eaedf74`), and the
> summary under the plan's message (`145b72c`). The final review added a seventh (`c278ea1`), which lists every reading
> pair that misses dr-quality-suggest's bar.
>
> Deviation: two tasks followed the final review. Task 7 (`59df779`) is the owner's choice at the completion gate (R9's
> provisional quality also gets an Outcomes row), and six cases ran again at that commit. Task 8 (`e885184`) is the
> plan's one wording round, because dr-spec-column read 2 of 5 at Task 7 (reps put section titles in the Spec cell) and
> reads 5 of 5 at Task 8. The record commit is `f275de1`. A later quality's resume rule and four smaller points went
> to `specs/deferred_items.md`.

## Plan completion

The Plan Completion Protocol ticks these items in `specs/deferred_items.md` from Task 6's summary. An item whose
`Done when:` is not met stays open with a dated note, and a miss goes to the owner at the gate.

- "The derive-roadmap new-project offer still draws core-and-later-stages text before the partner ranks"
  (`deferred-2026-11-07`): Task 3 edits 6 and 9, and V1 (Task 4).
- "A later quality in a research track's Ranked list has no O-number and no partner rank"
  (`78-derive-roadmap-new-project-entry`): Task 3 edit 12, and V3 (Task 4).
- "A new-project roadmap built from a spec maps each outcome to no spec section reference"
  (`78-derive-roadmap-new-project-entry`): Task 3 edits 2, 3, 5 and 11, V4 (Task 4) and the probe (Task 5).

The open plan 79 item "dr-tracks and dr-known-progression-79 miss conformance clause C at the final skill text" gets a
progress note with Task 6's two counts. Its `Done when:` needs two independent dr-tracks runs, so one run does not
close it.
