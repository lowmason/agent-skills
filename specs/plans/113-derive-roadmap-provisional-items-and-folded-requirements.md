# derive-roadmap: provisional items and folded requirements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Quarantine.** This plan, the spec, the record `specs/baseline/red-baseline-new-project-entry.md` and its folder
> name the cases, the pass rules and the expected behavior. Keep them out of every prompt (plan 78's quarantine,
> extended to this plan).

**Goal:** Make the first derive-roadmap resume that can ask settle every `suggested, not approved` item before
anything is promoted or handed off. Make §6 judge an uncited spec requirement by evidence. Close plan 79's dr-tracks
item with the independent runs it still needs.

**Architecture:** Two skill files change. `skills/derive-roadmap/SKILL.md` gets three edits: the §5 Ask bullet, the
§5 waiting-Ranked-list paragraph and §6. `references/roadmap-format.md` gets one edit, to the provisional paragraph of
Ranked list. Plan 78's micro-test kit gains four cases. Every result goes into plan 78's record, in new sections headed
`Plan 113`.

**Tech Stack:** Markdown skill text. The stdlib Python kit in `specs/baseline/red-baseline-new-project-entry/kit/`.
`claude -p` reps on Opus 5.5.

**Spec:** `specs/derive-roadmap-provisional-items-and-folded-requirements.md` (APPROVED 2026-11-27, owner decisions D1
and D2). R1–R3 and V1–V4 below are the spec's.

## Global Constraints

- **Execution base.** `BASE113` is the execution branch's start commit. Task 1 Step 1 records its sha. Line numbers
  below were taken at `f620eba`. The old text in each edit is the match key, not the line number.
- **Order of executions.** No execution starts while another plan executes in this repository (owner ruling,
  2026-10-28). Plan 112 is live in `specs/plans/`. Start only when it is not executing.
- **One owner per file.** Only Task 3, and a wording round of Task 4 or Task 5, edit skill files. Only Task 1 edits
  `cases.py`. Each task appends its own sections to the record.
- **Leave alone.** `references/gap-rubric.md`; §4's flow for a session that can ask; the old-format roadmap rules
  (`roadmap-format.md` from its opening to the end of Stage stamps); §7 and `references/new-project-entry.md`; every
  other skill; every existing case, rule, fixture, rep file and arm folder of the kit; the case-study repositories.
- **Examples stay out of the fixtures (micro-test Channel 3).** New skill text adds no example. If an edit needs
  one, it uses a transit agency's trip records. New fixtures reuse the kit's domains: canal locks and SEC filings.
- **Compaction window.** The derive-roadmap SKILL.md body stays at most 20,000 characters
  (`len(check_conformance.skill_body(text)[0])`; 17,817 at `f620eba`). No description change.
- **Commit gate.** Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Messages follow
  Conventional Commits in plain technical English and end with the session's attribution trailer. A record commit
  stages both paths:
  `git add specs/baseline/red-baseline-new-project-entry specs/baseline/red-baseline-new-project-entry.md`.
- **Micro-tests.** Plan 78's kit and runner, unchanged, as plan 85's Micro-tests constraint states them: a fresh
  `claude -p --model claude-opus-5-5` rep per run under `env -i`, from a new empty directory under `/tmp`, at a $1.00
  cap. Five reps per arm. Text is read with `git show`, never through `~/.claude/skills/`. Each pass rule is committed
  before any rep of its case runs. Every verdict is read by hand from the full reply, by the case's rule and the
  readings of record.
- **Fixtures (the sec-edgar commit).** `22c6767f`, which `SEC_SPEC` pins, is no longer in `~/Projects/sec-edgar` or on
  GitHub (checked 2026-11-27). The archived clone `~/Projects/archive/sec-edgar-cloud` holds it, with the bytes that
  every earlier manifest records (sha256 `c43fa455…`). So `CASE_REPOS` is a folder of links,
  `/tmp/plan113-work/repos/`: `sec-edgar` → `$HOME/Projects/archive/sec-edgar-cloud`, and `ces-revisions`,
  `embedding-data` and `agent-skills` → `$HOME/Projects/<name>`. Every build below runs with
  `CASE_REPOS=/tmp/plan113-work/repos`. Each manifest's sec-edgar line must show that sha256. The case-study
  repositories are read only.
- **Arms run at the last skill commit.** Controls read every text at `BASE113`. Treatments, guards and V3 read every
  text at the last skill commit that exists when they run. Any later skill commit re-runs, before the summary, every
  case whose decision the changed passage can reach. The record says why each other case was not re-run.
- **Bars.** Plan 78's, unchanged.
  - *Additive* (Tasks 2 and 4): the treatment passes every bar and conformance clause in at least 4 of 5 reps, and the
    control fails a bar clause in at least 1 of 5.
  - *Guard* (Task 5): the treatment passes at least as many reps as its comparison arm, minus one.
  - *V3* (Task 6): each run passes at least 4 of 5. V3 gets no wording round. A run below its bar is recorded, goes to
    the owner, and item 5095 stays open (spec V3).
  - A control with no failure never reverts a change. Record it and put it to the owner at the completion gate.
  - An additive or guard treatment below its bar gets one wording round with the case's rule unchanged, then an owner
    ruling. An owner stop ends the implementer with `BLOCKED (owner gate: Task N Step M)` (plan 78's D13).
- **Date reading.** Every new fixture says "Today is 2026-11-06". No clause scores a date.
- **Spend.** The controller keeps the running total in the record's `Plan 113: spend` table. Stop and ask the owner
  before the total passes **$30**. Before each `run_reps.sh` call, check the total plus that call's worst case (reps ×
  cap). An unreadable or empty rep file counts at its cap.
- **Folders.** Builds go under `/tmp/plan113-work/`. Each build's `MANIFEST.txt` is copied into the record's folder as
  `control/p113-MANIFEST.txt` or `treatment/p113-<label>-MANIFEST.txt`. Control rep folders are `control/<case>/`.
  Treatment and guard folders are `treatment/<case>-p113/`. V3's folders are `treatment/dr-tracks-p113a/`,
  `treatment/dr-tracks-p113b/` and `treatment/dr-known-progression-79-p113/`. A wording round adds `-r1`.
- **Public repository.** The plan, kit, record and commits hold no private detail.

## Review Focus

1. **The owner answers a provisional item.** On approval, the person expects the label gone and the item ranked where
   they put it. On a decline, they expect its row and list item gone and `Leaves out` reading
   `<quality>: declined, <YYYY-MM-DD>`. Every rep stops before the answer. Pinned in Task 3 Step 2 by the edit-4
   phrases. The summary names the answer path as untested.
2. **Two or more `suggested, not approved` items.** The person expects one question that covers each item. The new
   fixtures carry one item each, as the spec's V1 says. Pinned in Task 3 Step 2 by edit 1's phrase row. The
   summary names the many-item path as untested.
3. **A roadmap with a pending item is parked, or its track is stopped.** The spec is silent. Under edit 1, a resume
   asks about the item before it reaches any other question, so the owner's answer comes first. The dr-stop-track and
   dr-park-ranked guards (Task 5) hold no suggested item, so they show only that parking does not regress. The summary
   names the pending-item parking path as untested.
4. **A folded requirement that a plan names but no code implements.** The person expects it unmet, because a plan
   mention alone is neither a path:line nor a test name. Pinned in Task 3 Step 2 by edit 3's phrase row
   (`It is met only on the`). Task 1's V2 fixture gives R11 a mention in plan 14's Global Constraints and no code, so the
   case scores this path (clause B).
5. **The completion review of an old-format roadmap, or of one with no spec.** The person expects §6 to run as before.
   Pinned by the dr-resume-legacy guard (Task 5).

## Decisions

None.

## Open for plan review

The owner approves or amends these defaults as one batch. Each one was open in the spec or is new here.

1. **A declined item's O-number is freed, not burned.** The spec's designer's call is "burned, unless the builder
   finds a rule that says otherwise". R1 fixes the decline form `<quality>: declined, <YYYY-MM-DD>`, which carries no
   O-number, and it removes the Outcomes row and the list item. After that, no trace of the number is left in the
   file, so the next "next free O-number" takes it again. Burning it would need a different decline form, such as
   `<quality> (O<n>): declined, <YYYY-MM-DD>`, which changes R1's form. Default: freed, written into edit 4.
   Alternative: the O-number form above, in both the interactive and the provisional decline rules.
2. **A third V1 case, `dr-provisional-only`, for R2's waiting path.** The spec's V1 has two fixtures. Neither one has
   a research track whose committed stages are all ticked and whose Ranked list holds only a suggested item. That is
   the path where the old text is most likely to promote the item (goal 2's anti-goal). The case costs about $1.
   Default: add it.
3. **Fixture (a)'s "other changes".** Case `dr-provisional-ask` asks the other questions through two existing paths of
   the Ask: an unmet `Consumes` (as in dr-resume-blocked) and a waiting Ranked list (as in dr-resume-rerank). Both are
   live at base, so the case tests only whether the item joins them.
4. **How a provisional roadmap's Stage 1 ran.** Fixtures (a) and (c) have Stage 1 ticked before any resume: the owner
   launched it from the file's ROUTING line. That is the one history in which a first resume finds a ticked stage.
5. **The guard set** (Task 5's table). It holds the spec's five cases. It adds dr-rerank-second, dr-stop-track and
   dr-park-ranked, which read edit 2's paragraph, dr-resume-legacy, which reaches §6, and dr-research-depth, which
   writes a research-track roadmap under edit 4's paragraph. No resume arm has run since the 2026-11-17 removal of a
   §5 sentence (`175bf83`). So each resume guard's comparison spans that change and this plan's edits. A guard that
   misses re-runs at `BASE113` before its wording round, to show which change caused the miss.
6. **Spend stop $30** (the spec's designer's call). Estimate about $15: four controls and four treatments, 40 reps;
   ten guards, 50 reps; V3, 15 reps.
7. **A gap left for the completion gate.** A provisional roadmap with no suggested item still gets its Stage 1 handed
   off at its first resume, with no approval of the partition. D2's builder check shows the cause: no rule routes a
   provisional file back to §4. This plan does not fix it. The completion protocol files it as a deferred item.

---

### Task 1: four cases and their leak check

**Files:**
- Modify: `specs/baseline/red-baseline-new-project-entry/kit/cases.py` (new constants and four `CASES` entries)
- Modify: `specs/baseline/red-baseline-new-project-entry.md` (append `## Plan 113: base, cases and leak check` and
  `## Plan 113: spend`)

**Interfaces:**
- Consumes: `case()`, `lines()`, `edit()`, `TODAY`, `STEP_TASK`, `DR`, `SEC_SPEC`, `LOCK_ROADMAP`,
  `TWO_TRACK_ROADMAP`, `LOCK_STAGE_1_FINDINGS`, `SEC_SPEC_ROADMAP` from `cases.py`.
- Produces: `CASES` keys `dr-provisional-ask`, `dr-provisional-alone`, `dr-provisional-only` and `dr-folded-req`,
  each `additive` with texts `DR` and task `STEP_TASK`. `dr-folded-req` carries `{'spec': SEC_SPEC}`.

- [ ] **Step 1: Record the base and make the repos folder**

Append `## Plan 113: base, cases and leak check` to the record. Give `BASE113` (short and full sha, and branch). Run
`git diff --stat f620eba <BASE113> -- skills/derive-roadmap specs/baseline/red-baseline-new-project-entry`. Expected:
it prints nothing. If a line prints, stop and report it. Make `/tmp/plan113-work/repos/` as the Fixtures constraint
says. Run `claude --version`. If no record section has run the isolation probe at that version, run it as the record's
"Isolation probe (Task 1 Step 5)" does, into `pilot/probe-p113/`, and record that all five lines read `NO`.

- [ ] **Step 2: Write the constants and cases in `cases.py`**

Each fixture is a `lines(...)` call that starts with `TODAY` and a repository line, and ends with
`[now] Your partner: Resume the roadmap.` The implementer writes the fixture text, and the state each one must hold is
below. Write each roadmap strictly in the form `references/roadmap-format.md` gives at `BASE113`. Record each choice
the format leaves open as a fixture judgment call in the record. Such choices include the provisional label, the Rank
cell of a suggested row and the wording of `Leaves out`. Pass rules are exact copy.

The provisional roadmaps share these traits. A line under the header reads that a sub-agent run, which could not ask,
wrote the file, and that the partner has not approved it. Traceability is the suggested quality. Its Outcomes row and
its Ranked-list item, the last item, carry the label `suggested, not approved`. Stage 1's `Leaves out` names it by its
O-number. The roadmap has no Open questions section. A `git log` line says that a sub-agent run wrote and committed the
file, and that no resume has run since.

1. `dr-provisional-ask` (spec V1(a), R1, R2). Repository `lock-closures`. The roadmap is `TWO_TRACK_ROADMAP` made
   provisional, with traceability as O6 in Track A. Stage 1 is ticked and stamped (plan 4, 2026-11-03), launched by the
   partner from the file. Plan 4's Handoff has one bullet, for Stage 2: the closure log has no live feed, because the
   trust exports it once a week. `LOCK_STAGE_1_FINDINGS` follows.

   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): the reply hands off no stage and writes no new stage entry before the answer: no "Next:" line names a stage.
   Clause B (bar): the question asks the partner to approve traceability (O6) with a place in Track A's ranking, or to decline it.
   Clause C (bar): before the answer, O6 is not proposed as the next stage, and it is not ranked among the other items as an outcome.
   Clause D (conformance): one question covers traceability beside the unmet Consumes of Stage 2 and Track A's next stage.
   Reading notes. Clause B: any wording that offers both approval with a rank and a decline passes; a proposed default rank passes; a re-ranking that places O6 with no approval asked fails B. Clause C: a next stage proposed from O2 to O4 passes; a ranking conditional on approval ("if you approve it, O6 goes fourth") passes. Clause D: one question may offer options and close with them; two or more separate questions fail D; either default for Stage 2 (a stage added to produce the feed, or the Consumes amended) passes.
   ```

2. `dr-provisional-alone` (spec V1(b), R1). Repository `lock-closures`. The roadmap is `LOCK_ROADMAP` made provisional,
   with Stage 1 unticked and no stamp, and traceability as O5. The `git log` line dates the file 2026-11-05. There is
   no plan, Handoff or findings read.

   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): no stage is handed off before the answer: no "Next:" line names a stage, and Stage 1 is not routed.
   Clause B (bar): one question asks the partner to approve traceability (O5) with a place in Track A's ranking, or to decline it.
   Clause C (conformance): O5 is not promoted, and it is not treated as an approved outcome, before the answer.
   Clause D (conformance): the reply plans, specs and brainstorms nothing.
   Reading notes. Clause A: saying that Stage 1 follows once the partner answers passes. Clause B: the question may also cover other points, such as approving the partition; two or more separate questions fail B. Clause C: listing O5 as pending passes.
   ```

3. `dr-provisional-only` (Open for plan review item 2, R2). Repository `lock-closures`. The roadmap is `LOCK_ROADMAP`
   made provisional and cut to one research track with two outcomes: O1, and traceability as O2. Stage 1 delivers O1
   and is ticked and stamped (plan 4, 2026-11-03), launched by the partner from the file. The Ranked list holds only
   O2. Plan 4's Handoff reads `None: shipped as the roadmap's Produces states.` `LOCK_STAGE_1_FINDINGS` follows.

   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): before the answer, no new stage entry is written, no stage is handed off, and O2 is not promoted.
   Clause B (bar): one question asks the partner to approve traceability (O2) and give its rank, or to decline it, together with or ahead of any proposed next stage.
   Clause C (conformance): the reply reports Stage 1's finding and its measured cost.
   Clause D (conformance): no completion review starts, and the roadmap is neither parked nor retired.
   Reading notes. Clause A: a proposed stage described in the question is not an entry. Clause B: "if you approve O2, Stage 2 builds it" passes; a proposal to promote O2 that asks no approval fails B; two or more separate questions fail B. Clause C: the finding is the 3.1 m level or the steep rise above it; the cost is the 22-minute, 1.8 GB run. Clause D: a completion review offered as what follows a decline passes.
   ```

4. `dr-folded-req` (spec V2, R3). Repository `sec-edgar`. The roadmap is `SEC_SPEC_ROADMAP` with the O8 (R8) and O11
   (R11) rows removed, the other rows renumbered O1 to O9, and every stage's Outcomes, Exit and `Leaves out` kept
   consistent with that. All four stages are ticked and stamped (plans 11 to 14). `[you, tools]` lines give the state:
   - Plan 12 (Stage 2) Global Constraints hold the line "Every request to the SEC goes through one downloader under one
     request budget (spec R8)". `src/sec_edgar/download.py:41` takes the shared lease, and
     `tests/test_download.py::test_two_collectors_share_one_budget` passes.
   - Plan 14 (Stage 4) Global Constraints name spec R11. A search for the schedules, retry limits and request rate
     finds no such values, no configuration file and no test.
   - Each plan's Handoff reads `None`. The gap rubric over O1 to O9 is already done: each verdict is
     implemented-as-specified, with its stage plan and tests as evidence.

   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): R8 is marked met, with a path:line or a test name as evidence, and plan 12 is named as the plan that built it.
   Clause B (bar): R11 is marked unmet, and the reply gives its two exits: a new stage, or a deferral with a written why.
   Clause C (conformance): no verdict for R8 or R11 rests on a stage stamp alone.
   Clause D (conformance): the roadmap is not retired before the partner chooses R11's exit.
   Reading notes. Clause A: src/sec_edgar/download.py:41 or the test name counts; plan 12 by id or path counts; implemented-as-specified or implemented-differently counts as met. Clause B: a plan mention is neither a path:line nor a test name, so R11 marked met on plan 14 alone fails B; a default exit with a question passes; a deferral with no written why fails B. Clause D: proposing retirement after the answer passes.
   ```

Leak words: the three `dr-provisional-*` cases use
`r'approve with a rank|approve and rank|declin|before the answer|first resume'`, and `dr-folded-req` uses
`r'folded|uncited|stamp alone|path:line'`. The format tokens that the fixtures must hold (`suggested, not approved`,
`Leaves out`, `Ranked list`) are not leak words, and the patterns do not match them.

- [ ] **Step 3: Check the cases load and build**

Run
`uv run python -c "import sys; sys.path.insert(0, 'specs/baseline/red-baseline-new-project-entry/kit'); import cases; print(len(cases.CASES))"`.
Expected: `30`. Then
`CASE_REPOS=/tmp/plan113-work/repos uv run python specs/baseline/red-baseline-new-project-entry/kit/build_prompts.py leakview /tmp/plan113-work/leak dr-provisional-ask dr-provisional-alone dr-provisional-only dr-folded-req`.
Expected: `wrote 4 prompts to /tmp/plan113-work/leak`.

- [ ] **Step 4: Run the leak check**

As the record's `## Leak check` does: grep each new case's hand-written fixture lines, then its leak-view prompt,
case-insensitively, for its leak words. Expected: 0 hits in hand-written lines. Trace every leak-view hit to its
source (a case-repository file read verbatim is exempt). Add the table to the record. Reword a hand-written line that
hits, then rebuild into `/tmp/plan113-work/leak-2`. Also grep the four prompts for `red-baseline`, `plan 113`,
`micro-test` and `quarantine`. Expected: 0 hits.

- [ ] **Step 5: Start the spend table and commit**

Append `## Plan 113: spend` with the stop ($30), the per-rep cap ($1.00) and a row per task. Then:

```bash
git add specs/baseline/red-baseline-new-project-entry/kit/cases.py specs/baseline/red-baseline-new-project-entry.md
git commit -m "test(specs): add plan 113's provisional-item and folded-requirement cases"
```

### Task 2: control arms (RED), before any skill edit

**Files:**
- Create: `control/<case>/rep1.json` … `rep5.json` for the four Task 1 cases, and `control/p113-MANIFEST.txt`
- Modify: the record (append `## Plan 113: control`)

**Interfaces:**
- Consumes: the four Task 1 cases.
- Produces: one control verdict per case (RED, thin or clean), which Task 4 reads.

- [ ] **Step 1: Build, then run five reps per case**

`CASE_REPOS=/tmp/plan113-work/repos uv run python specs/baseline/red-baseline-new-project-entry/kit/build_prompts.py <BASE113> /tmp/plan113-work/control dr-provisional-ask dr-provisional-alone dr-provisional-only dr-folded-req`.
Expected: `wrote 4 prompts to /tmp/plan113-work/control`. Copy its `MANIFEST.txt` to `control/p113-MANIFEST.txt`. For
each case, run
`bash specs/baseline/red-baseline-new-project-entry/kit/run_reps.sh /tmp/plan113-work/control/<case>.txt specs/baseline/red-baseline-new-project-entry/control/<case> 1 5 claude-opus-5-5 1.00`.
Rerun a VOID rep with the next free rep number.

- [ ] **Step 2: Score and record**

Run `show_reps.py` on each folder. Score each rep by hand, clause by clause. Write one `### Plan 113 control: <case>`
section per case in the record's Task 7 form: a table, clause counts, one quote per failed clause, judgment calls and
other readings. Name each case RED, thin (a bar clause fails in exactly 1 of 5) or clean. A clean control goes to the
owner at the completion gate, and the case's treatment still runs. Add the spend row.

- [ ] **Step 3: Commit**

```bash
git add specs/baseline/red-baseline-new-project-entry specs/baseline/red-baseline-new-project-entry.md
git commit -m "test(specs): run plan 113's control arms"
```

### Task 3: the skill text

**Files:**
- Modify: `skills/derive-roadmap/SKILL.md:200-201` (§5 Ask), `:207-220` (§5 waiting Ranked list and the handoff line
  after it), `:241-244` (§6)
- Modify: `skills/derive-roadmap/references/roadmap-format.md:145-148` (Ranked list, provisional paragraph)
- Modify: the record (append `## Plan 113: skill text`)

**Interfaces:**
- Consumes: nothing from earlier tasks. The controls (Task 2) must be committed first.
- Produces: the skill commit `T`, which Tasks 4 to 6 read. Edit 2b's handoff gate is what `dr-provisional-alone`
  scores.

- [ ] **Step 1: Edit the skill text**

Exact copy. Rewrap to the file's width. Change nothing else. "Old" is the match key at `BASE113`. Edit 2b gates the
handoff, so that a resume with no stamped stage (fixture (b)) still reaches edit 1 before it routes a stage.

1. `SKILL.md` §5 Ask, R1. Old: `Otherwise it counts as met, and the receiving session checks it.` New:
   `Otherwise it counts as met, and the receiving session checks it. Each item marked `suggested, not approved` (a provisional file, `references/roadmap-format.md`, Ranked list) joins the same question, to approve with a rank or to decline. When nothing else is open, these items open the Ask by themselves.`
2. `SKILL.md` §5 waiting Ranked list, R2. Old: `A promoted item becomes a stage entry only after the answer.` New:
   `A promoted item becomes a stage entry only after the answer. An item marked `suggested, not approved` is not yet an outcome, and a list that holds only such items is still waiting. Before the answer such an item is never promoted or counted. The question asks your partner to approve and rank each one, or decline it, and only then proposes the next stage, so one answer settles both.`
   2b. `SKILL.md` §5, after the waiting paragraph, R1. Old: `Then hand off the next stage (§4). With every stage ticked`.
   New: `Then, once no item marked `suggested, not approved` is open, hand off the next stage (§4). With every stage ticked`
3. `SKILL.md` §6, R3. Old:
   `When its `Source` is a spec, also list each numbered spec requirement that no outcome's `Spec` cell cites, as unmet.`
   New:
   `When its `Source` is a spec, also run the rubric over each numbered spec requirement that no outcome's `Spec` cell cites. It is met only on the rubric's own evidence, a path:line or a test name, and the verdict names the stage plan that built it. A stage stamp names no requirement, so a stamp alone is not evidence. With no evidence, the requirement is unmet.`
4. `roadmap-format.md` Ranked list, R1 (the record of the answer). Old:
   `Each also gets an Outcomes row, marked `suggested, not approved`.` New:
   `Each also gets an Outcomes row, marked `suggested, not approved`. The first resume that can ask puts each such item to your partner (SKILL.md §5). On approval the label goes, the item takes the rank your partner gives, and it is an ordinary outcome. On a decline its Outcomes row and list item go, the stage's `Leaves out` entry reads `<quality>: declined, <YYYY-MM-DD>`, and its O-number is free again.`

If the owner chose the burned alternative at plan review (Open item 1), edit 4's last clause and the interactive
decline rule in the same paragraph use that form instead, and the Decisions section says so.

- [ ] **Step 2: Check the edits**

For each row, run `tr '\n' ' ' < <file> | tr -s ' ' | /usr/bin/grep -o -F '<phrase>' | wc -l` and expect the count.

| File | Phrase | Count |
|---|---|---|
| `SKILL.md` | `joins the same question, to approve with a rank or to decline` | 1 |
| `SKILL.md` | `these items open the Ask by themselves` | 1 |
| `SKILL.md` | `a list that holds only such items is still waiting` | 1 |
| `SKILL.md` | `so one answer settles both` | 1 |
| `SKILL.md` | `once no item marked` | 1 |
| `SKILL.md` | `It is met only on the` | 1 |
| `SKILL.md` | `a stamp alone is not evidence` | 1 |
| `SKILL.md` | `cell cites, as unmet` | 0 |
| `roadmap-format.md` | `The first resume that can ask puts each such item` | 1 |
| `roadmap-format.md` | `declined, <YYYY-MM-DD>` | 2 |
| `roadmap-format.md` | `its O-number is free again` | 1 |

Then
`uv run --with pyyaml python -c "import sys; sys.path.insert(0, 'build'); import check_conformance as c; print(len(c.skill_body(open('skills/derive-roadmap/SKILL.md').read())[0]))"`.
Expected: at most 20,000 (about 18,700). Run `uv run python build/check_links.py` and the commit gate.

- [ ] **Step 3: Commit, then record `T`**

```bash
git add skills/derive-roadmap/SKILL.md skills/derive-roadmap/references/roadmap-format.md
git commit -m "feat(derive-roadmap): settle provisional items at resume and judge folded requirements by evidence"
```

Append `## Plan 113: skill text` to the record: the sha as `T`, the body size, and the edit for each requirement (R1:
1, 2b and 4; R2: 2; R3: 3). A fix that this task's review finds is a further skill commit here, before Task 4. The record
names the last one as `T`. Commit the record with the message `test(specs): record plan 113's skill commit`.

### Task 4: treatment arms for V1 and V2

**Files:**
- Create: `treatment/<case>-p113/` (five reps each) for the four Task 1 cases, and `treatment/p113-t4-MANIFEST.txt`
- Modify: the record (append `## Plan 113: treatment`)

**Interfaces:**
- Consumes: `T` (Task 3) and Task 2's verdicts.
- Produces: the V1 and V2 verdicts, and the last skill commit after any wording round here, which Tasks 5 and 6 read.

- [ ] **Step 1: Build and run**

Build at `<T>` into `/tmp/plan113-work/t4`, as Task 2 Step 1 does. Expected: `wrote 4 prompts to /tmp/plan113-work/t4`.
Copy its manifest. Run five reps per case into `treatment/<case>-p113/`.

- [ ] **Step 2: Score, apply the additive bar, record**

Score as Task 2 Step 2, in `### Plan 113 treatment: <case>` sections. Each ends with its bar verdict against its
control. For a miss, follow the Bars' wording round. It gives the new text, its commit as `T-r1`, the re-run cases in
`-r1` folders, and why each other case was not re-run. A second miss is an owner gate. Add the spend row.

- [ ] **Step 3: Commit**

```bash
git add specs/baseline/red-baseline-new-project-entry specs/baseline/red-baseline-new-project-entry.md
git commit -m "test(specs): run plan 113's treatment arms"
```

### Task 5: the guards at the final text (V4)

**Files:**
- Create: `treatment/<case>-p113/` (five reps each) for the ten guards below, and `treatment/p113-t5-MANIFEST.txt`
- Modify: the record (append `## Plan 113: guards`)

**Interfaces:**
- Consumes: the last skill commit, `T-final`.
- Produces: the guard verdicts, which the summary (Task 6) reads.

- [ ] **Step 1: Build and run**

Build at `<T-final>` into `/tmp/plan113-work/t5` with the ten cases below. Expected:
`wrote 10 prompts to /tmp/plan113-work/t5`. Copy its manifest. Run five reps per case into `treatment/<case>-p113/`.

- [ ] **Step 2: Score and apply the guard bar**

Each case is read as a guard, by its rule and its reading of record (plan 85's Open item 3 and the record sections
named below). Other readings go under "Other readings" and never count.

| Case | Reads edit | Compared with (record section, text) | Arm PASS | Guard needs |
|---|---|---|---|---|
| dr-quality-suggest | 4 | "/deferred pass: results at `73f7dae`" | 5 of 5 | 4 |
| dr-spec-column | 4 | "/deferred pass: results at `73f7dae`" | 5 of 5 | 4 |
| dr-research-depth | 4 | "/deferred pass: results at `73f7dae`" | 5 of 5 | 4 |
| dr-resume-rerank | 1, 2 | "Plan 85: final-review fixes", at `59df779` | 4 of 5 | 3 |
| dr-rerank-second | 1, 2 | "Plan 85: final-review fixes", at `59df779` | 5 of 5 | 4 |
| dr-stop-track | 1, 2 | "Plan 85 guard: dr-stop-track", at `2e91b05` | 5 of 5 | 4 |
| dr-park-ranked | 1, 2 | "Plan 85 guard: dr-park-ranked", at `2e91b05` | 4 of 5 | 3 |
| dr-resume-marker | 1 | "Plan 79 Task 3 round 3: dr-resume-marker", at `5f52dfc` | 5 of 5 | 4 |
| dr-resume-blocked | 1 | "Plan 79 Task 3 round 3: dr-resume-blocked", at `5f52dfc` | 5 of 5 | 4 |
| dr-resume-legacy | 1, 3 | "Plan 85 guard: dr-resume-legacy", at `2e91b05` | 5 of 5 | 4 |

For each resume guard, also record, unscored, whether the reply asks about any item as if it were provisional. No
guard fixture holds a `suggested, not approved` item, so any such ask is a false trigger. A guard below its bar first
re-runs at `BASE113` into a `-p113-base` folder (Open item 5), then takes the Bars' wording round, then goes to an owner
ruling. Add the spend row.

- [ ] **Step 3: Commit**

```bash
git add specs/baseline/red-baseline-new-project-entry specs/baseline/red-baseline-new-project-entry.md
git commit -m "test(specs): run plan 113's guards"
```

### Task 6: the dr-tracks runs (V3), and the summary

**Files:**
- Create: `treatment/dr-tracks-p113a/`, `treatment/dr-tracks-p113b/`, `treatment/dr-known-progression-79-p113/`
  (five reps each), and `treatment/p113-t6-MANIFEST.txt`
- Modify: the record (append `## Plan 113: dr-tracks runs` and `## Plan 113: summary`)

**Interfaces:**
- Consumes: `T-final` (no skill commit may follow this task's runs).
- Produces: the verdicts that the plan completion protocol reads to tick or note the three items.

- [ ] **Step 1: Build and run**

Build at `<T-final>` into `/tmp/plan113-work/t6` with `dr-tracks` and `dr-known-progression-79`. Expected:
`wrote 2 prompts to /tmp/plan113-work/t6`. Copy its manifest. Run three separate `run_reps.sh` calls, five reps each:
`dr-tracks.txt` into `dr-tracks-p113a`, then `dr-tracks.txt` into `dr-tracks-p113b`, then
`dr-known-progression-79.txt` into `dr-known-progression-79-p113`. The two dr-tracks runs are independent: separate
calls, separate folders, and neither is read before the other is complete.

- [ ] **Step 2: Score against the V3 bar**

Score each run by its case rule and the readings of record: Provenance on bytes (owner, 2026-11-11), and no Echo
(owner, 2026-11-17). Under no Echo, the phrase "your partner can name its stages from first to last" next to an order
calls the order stages, and plan 78's round 2 rep5 verdict stands. For dr-tracks, use plan 85's item-4 reading and the
Stage word test (plan 85, Open item 3). Each run needs at least 4 of 5. A run below its bar is recorded and goes to the
owner. No wording round follows (Bars, V3).

- [ ] **Step 3: Write the summary**

`## Plan 113: summary` holds:
- one table of every plan 113 arm (case, bar, control or comparison, treatment, result);
- the spend total;
- for each item in Plan completion below, whether its `Done when:` is met;
- the untested passages: Review Focus items 1 to 3, and any passage that changed after the arm that reads it;
- the owner-gate list, with Open item 7's gap.

Add the spend row.

- [ ] **Step 4: Commit**

```bash
git add specs/baseline/red-baseline-new-project-entry specs/baseline/red-baseline-new-project-entry.md
git commit -m "test(specs): run plan 113's dr-tracks runs and summary"
```

## Plan completion

The Plan Completion Protocol ticks these items in `specs/deferred_items.md` from Task 6's summary. An item whose
`Done when:` is not met stays open with a dated note, and the miss goes to the owner at the gate.

- "A resume that finds a later quality and asks nothing else has no question for it to join"
  (`85-derive-roadmap-later-qualities-and-spec-refs`): edits 1, 2 and 4, and the three `dr-provisional-*` cases (Tasks 2
  and 4).
- "A spec requirement that the partner folds into constraints is listed as unmet at §6" (same section): edit 3, and
  `dr-folded-req` (Tasks 2 and 4).
- "dr-tracks and dr-known-progression-79 miss conformance clause C at the final skill text"
  (`79-derive-roadmap-resume-and-route-tests`): Task 6's three runs.

The gate also files two new deferred items, unless the owner rules otherwise: Open item 7's gap, and the kit's
dependence on the archived sec-edgar clone (the Fixtures constraint), since `~/Projects/sec-edgar` no longer holds
`22c6767f`.
