# derive-roadmap: resume and parking follow-ups Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Quarantine.** This plan, the record `specs/baseline/red-baseline-new-project-entry.md` and its folder name the
> cases, the pass rules and the expected behavior. Keep them out of every prompt (plan 78's quarantine, extended to
> this plan).

**Goal:** Settle the fifteen open items of the `79-derive-roadmap-resume-and-route-tests` and
`113-derive-roadmap-provisional-items-and-folded-requirements` sections of `specs/deferred_items.md`: give the kit a
source of record for the sec-edgar spec, measure the two plan 113 drops, close the §5 gaps with one skill commit, and
cover each new path with a case.

**Architecture:** Two diagnostic arms run first, at the current skill text, before any edit. Nine new cases and their
controls follow. One skill commit `T` then makes up to ten edits: eight in `skills/derive-roadmap/SKILL.md` (§3 and
§5) and one in `references/roadmap-format.md` (Ranked list), with two of them conditional on a control. Treatments,
one guard round and item 1's runs read the last skill commit. Every result goes into plan 78's record, in new sections
headed `Plan 119`.

**Tech Stack:** Markdown skill text. The stdlib Python kit in `specs/baseline/red-baseline-new-project-entry/kit/`.
`claude -p` reps on Opus 5.5.

**Spec:** none. The fifteen items and their `Done when:` lines are the requirements. Items are cited below as
**I1** to **I15**, in the brief's order:

| Id | Item (heading text in `specs/deferred_items.md`) | Section |
|---|---|---|
| I1 | dr-tracks and dr-known-progression-79 miss conformance clause C at the final skill text | 79 |
| I2 | A block the partner resolved can be raised again at a later resume | 79 |
| I3 | The gap-analysis path has no overwrite guard | 79 |
| I4 | The unticked-producer clause and the unusable-output path have no case | 79 |
| I5 | A partial block gets no question about the blocked stage | 79 |
| I6 | A Handoff that amends nothing is re-read at every resume | 79 |
| I7 | The term "roadmap name" differs between `references/new-project-entry.md` and `SKILL.md` §5 Parking | 79 |
| I8 | §5's Commit step does not name a declined provisional item | 113 |
| I9 | No rule says what a track stop does with a `suggested, not approved` item that is still open | 113 |
| I10 | The format does not say what a stage's `Leaves out` reads for a provisional item after approval | 113 |
| I11 | Numbered points inside the ONE question are not scored | 113 |
| I12 | A provisional roadmap with no suggested item still hands off Stage 1 at its first resume | 113 |
| I13 | The kit's sec-edgar cases depend on an archived clone | 113 |
| I14 | dr-known-progression-79 drops from 5 of 5 at plan 113's base to 3 of 5 at its final text | 113 |
| I15 | dr-park-ranked misses its guard bar at plan 113's final text and at its base | 113 |

## Global Constraints

- **Execution base.** `BASE119` is the execution branch's start commit. Task 1 Step 1 records its sha. Line anchors were
  taken at `8131b81`. The skill text at `8131b81` is byte-identical to `2bd982d`, plan 113's last skill commit
  (`git log -1 --format=%h -- skills/derive-roadmap` prints `2bd982d`). The old text in each edit is the match key, not
  the line number.
- **Order of executions.** Up to three file-disjoint domain executions run at once in this repository (owner rule,
  2026-11-17). No other live plan may edit `skills/derive-roadmap/` or the kit while this one executes.
- **One owner per file.** Only Task 5, and a wording round of Task 6 or Task 7, edit skill files. Only Tasks 1, 2 and 3
  edit the kit. Each task appends its own sections to the record.
- **Leave alone.** derive-roadmap text outside §3, §5 and the format's Ranked list; every other skill; every existing
  case, rule, fixture, rep file and arm folder of the kit, except where Task 1 changes how `SEC_SPEC` is read; the
  case-study repositories.
- **Examples stay out of the fixtures (micro-test Channel 3).** New skill text adds no example. New fixtures reuse the
  kit's domains: canal locks, parking occupancy and SEC filings.
- **Compaction window.** The derive-roadmap SKILL.md body stays at most 20,000 characters
  (`len(check_conformance.skill_body(text)[0])`). It is **18,799** at `8131b81`, so the edits have 1,201 characters.
  Task 5's edits add about 880 at most. If the body passes 20,000, stop and ask the owner which edit to shorten.
- **Commit gate.** Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Messages follow
  Conventional Commits in plain technical English and end with the session's attribution trailer. A record commit
  stages both paths:
  `git add specs/baseline/red-baseline-new-project-entry specs/baseline/red-baseline-new-project-entry.md`.
- **Micro-tests.** Plan 78's kit and runner, as plan 85's Micro-tests constraint states them: a fresh
  `claude -p --model claude-opus-5-5` rep per run under `env -i`, from a new empty directory under `/tmp`, at a $1.00
  cap. Five reps per arm unless a task says otherwise. Text is read with `git show`, never through
  `~/.claude/skills/`. Each pass rule and each decision rule is committed before any rep of its case runs. Every verdict
  is read by hand from the full reply, by the case's rule and the readings of record.
- **Fixtures (the sec-edgar spec).** No sec-edgar case builds before Task 1 lands. After Task 1, every build reads
  `SEC_SPEC` from the source of record that D2 names, and each manifest's sec-edgar line shows sha256
  `c43fa45500db57e048eeea10befdcb7d48ce361068073c6e6211ef65c14576f6`. The case-study repositories are read only.
- **Same-day arms.** The two arms of each Task 2 comparison run on one calendar day. Task 7's runs also run on one day.
- **Arms run at the last skill commit.** Controls read every text at `BASE119`. Treatments, guards and item 1's runs
  read every text at the last skill commit that exists when they run. A later skill commit re-runs, before the summary,
  every case whose decision the changed passage can reach. The record says why each other case was not re-run.
- **Bars.** Plan 78's, unchanged, read as plan 113 read them.
  - *Additive* (Tasks 4 and 6): the treatment passes every bar and conformance clause in at least 4 of 5 reps, and the
    control fails a bar clause in at least 1 of 5.
  - *Guard* (Task 7): the treatment passes at least as many reps as its comparison arm, minus one.
  - *I1* (Task 7): each of the three runs passes at least 4 of 5. No wording round follows. A run below its bar goes
    to the owner, and I1 stays open.
  - A control with no failure never reverts a change, and its item stays open. Record it and put it to the owner at the
    completion gate.
  - An additive or guard treatment below its bar gets one wording round with the case's rule unchanged, then an owner
    ruling. An owner stop ends the implementer with `BLOCKED (owner gate: Task N Step M)` (plan 78's D13).
- **Date reading.** New fixtures say `TODAY` ("Today is 2026-11-06."), as the kit's other cases do, except
  `dr-park-ranked-dated` (Task 2). No new clause scores a date.
- **Spend.** The controller keeps the running total in the record's `Plan 119: spend` table. Stop and ask the owner
  before the total passes **$40** (Open item 10). Before each `run_reps.sh` call, check the total plus that
  call's worst case (reps × cap). An unreadable or empty rep file counts at its cap.
- **Folders.** Builds go under `/tmp/plan119-work/`. Each build's `MANIFEST.txt` is copied into the record's folder as
  `control/p119-MANIFEST.txt` or `treatment/p119-<label>-MANIFEST.txt`. Control rep folders are `control/<case>/`.
  Treatment and guard folders are `treatment/<case>-p119/`. Task 2's folders are named in Task 2. A wording round
  adds `-r1`.
- **Public repository.** The plan, kit, record and commits hold no private detail.

## Review Focus

1. **An ordinary sequential roadmap.** A later stage whose producer is only unticked is not blocked. The person expects
   a resume to hand off the next ready stage with no question. Edit 1 fires the question beside a ready stage only when
   a Handoff or stamp shows the input missing. Pinned in Task 5 Step 2 by edit 1's phrase row, and by the guards
   dr-resume-marker and dr-rerank-second (Task 7), whose next stage is ready and whose later stages wait on it.
2. **A provisional file whose Stage 1 was launched before any resume.** The person expects the ticked stage to stay as
   built and the rest of the partition to go into the one question. Edit 7 says so. dr-provisional-ask and
   dr-provisional-only (Task 7 guards) have a ticked Stage 1 in a provisional file, so they score it.
3. **The partner declines a provisional item.** The person expects the decline written and committed before any
   handoff. Case `dr-provisional-decline` (Task 3) scores the answer path, which plan 113 left untested.
4. **The new-project path's name rule.** Edit 8 adds the overwrite guard to §3. The person expects the new-project
   path to ask for another name as before. Pinned by the dr-name-collision guard (Task 7).
5. **A roadmap whose earlier resume ran under the old text.** A stage added at that Ask cites no Handoff, so edit 3
   does not reach it, and the block can still be raised again. The summary names this as a known limit.

## Decisions

- **D1** (owner, brief, 2026-11-28): "Provide briefs for P6 and P7 as well.", then "Include as many items as possible
  in each." One plan, named for its theme, takes every open item of both sections. An item that needs the owner's
  design call goes to plan review as a question. Applied in: Spec table, Open for plan review.
- **D2** (owner, plan review, 2026-11-28): each of the eleven items of Open for plan review approved as proposed,
  answered one by one: (1) store the spec file in the kit, (2) an open suggested item parks, marked never approved,
  (3) numbered points inside one request are one question, stated in the Ask, (4) a provisional file puts its
  partition into the question, (5) I6 keeps watching, (6) the two-case I2 design, (7) the Fisher rule, (8) the dated
  variant closes I15 when the date is the cause, (9) the provisional cases as guards, (10) the $40 stop, (11) add
  `dr-provisional-decline`. Applied in: Global Constraints (Spend), Tasks 1 to 7, Plan completion.

## Open for plan review

Resolved at plan review on 2026-11-28: the owner approved each item as proposed (D2).

The owner approves or amends these as one batch. Tasks are built on each default.

1. **I13: the source of record for the sec-edgar spec.** The sec-edgar history was rewritten after `22c6767f`:
   GitHub and `~/Projects/sec-edgar` start from a different first commit, and only `~/Projects/archive/sec-edgar-cloud`
   holds `22c6767f`. Both options below publish bytes that GitHub no longer holds. If the rewrite was on purpose, say
   so, and the plan keeps the links folder and names the archive as the source.
   - *(a), default:* store the one spec file in the kit, at
     `specs/baseline/red-baseline-new-project-entry/kit/sources/sec-edgar/22c6767f/specs/sec-filing-index-ingestion-spec.md`.
     The builder reads it in place of `git show`, checks its sha256 and writes the same manifest line. Only the one
     file is published. sec-edgar is the owner's own repository, so no `NOTICE` change.
   - *(b):* the owner pushes a tag on `22c6767f` from the archive clone to `lowmason/sec-edgar`, then fetches it into
     `~/Projects/sec-edgar`. No builder change, and the default `CASE_REPOS` works. This publishes the whole first
     commit, and it is an owner step.
2. **I9: an open `suggested, not approved` item at a track stop or park.** Default: it parks with the other items, and
   its deferred item says that your partner never approved it (edit 5). A park is a deferral, not an approval, and the
   backlog keeps the suggestion. Alternative: it goes with no item, as a decline does.
3. **I11: numbered points inside the ONE question.** Default ruling: numbered points inside one approve-or-amend
   request are one question and meet the rule. The Ask says so (edit 6). Alternative: the same ruling as a kit reading
   of record only, with no skill text.
4. **I12: a provisional file with no suggested item.** The file already carries the provisional label (SKILL.md §1,
   `references/gap-rubric.md`). Default: a file still labelled provisional puts its partition into the Ask's one
   question at any resume that can ask, with or without suggested items, and the label goes on approval. A stage
   already ticked stays as built. The handoff gate also waits for the label to go (edits 7 and 7b). This uses the
   existing label, not the new marker that the spec rejected (D2, option B).
5. **I6: keep watching.** Default: no edit. Its `Revisit if:` signal has not fired. Task 7 records, unscored, whether
   any resume rep reports a trap or deferred-item bullet that the fixture shows an earlier resume already reported. I6
   gets no `→ planned` note unless the owner keeps it in the plan.
6. **I2: the two-resume case design.** A one-prompt rep cannot run two resumes. Default: two cases.
   `dr-ask-commit` is the answer step of the first resume: it scores whether the approved added stage cites
   `plan 5, Handoff`. `dr-resume-twice` is the second resume. Its control fixture holds the added stage as the old text
   writes it (no citation). Its treatment fixture holds the stage as edit 3 writes it (cited). So `dr-resume-twice`'s
   two arms differ in text and in fixture, as the edit's effect requires. The `Done when:` reads its control and
   treatment from these arms.
7. **I14: the decision rule, fixed before any rep.** Ten reps per arm, on one day, at `BASE119`'s text and at
   `171e763`. "The drop repeats" when a one-sided Fisher exact test on the two PASS counts gives p < 0.05 (for example,
   5 of 10 against 10 of 10). Otherwise the record calls it sampling. When it repeats, the record names the diff
   passages of `171e763..2bd982d` that the failing reps' wording echoes as the candidate cause, and I1 goes to the owner.
8. **I15: the date confound and what closes the item.** Task 2 adds `dr-park-ranked-dated`, the same case with the run
   day as "Today" and clause C expecting that date. Ten reps each of dr-park-ranked and the variant run on one day at
   `BASE119`. The record names the date as the cause when the variant passes at least 3 more reps than the original and
   at most one of its fails is a clause C heading. Default: if the date is the cause, I15 closes when the variant
   passes at least 3 of 5 at the final text, since the original's date gap grows each day. Otherwise the original must
   pass 3 of 5, after a wording round if needed.
9. **The bars of dr-provisional-alone and dr-provisional-only.** Both have clean controls (plan 113, D4), so I10's
   "meet their bars" can never be met additively. Default: read all three `dr-provisional-*` cases as guards against
   plan 113's `T-r1` arms (5 of 5 each, guard needs 4).
10. **Spend stop $40.** Estimate about $25: Task 2, 40 reps; nine new cases, 90 reps; Task 7, 17 arms, 85 reps.
11. **I8: a new answer-path case, `dr-provisional-decline`.** I8's `Done when:` needs only re-runs. The case covers the
    answer path that no arm has scored (Review Focus 3), for about $1. Default: add it.

---

### Task 1: the sec-edgar source of record (I13)

Written for Open item 1's default (a). Under (b), Steps 2 and 3 become: the owner pushes and fetches the tag, and the
implementer runs Step 4 with `CASE_REPOS="$HOME/Projects"`.

**Files:**
- Create: `specs/baseline/red-baseline-new-project-entry/kit/sources/sec-edgar/22c6767f/specs/sec-filing-index-ingestion-spec.md`
- Modify: `specs/baseline/red-baseline-new-project-entry/kit/build_prompts.py` (`repo_file`, the module docstring)
- Modify: `specs/baseline/red-baseline-new-project-entry/kit/cases.py` (`SEC_SPEC` gains `'sha256'`)
- Modify: the record (append `## Plan 119: base and the sec-edgar source`)

**Interfaces:**
- Produces: `repo_file(repo, commit, path, excerpt=None, sha256=None) -> str`. It reads
  `kit/sources/<repo>/<commit>/<path>` when that file exists, else `git -C "$CASE_REPOS/<repo>" show`. When `sha256` is
  given, it refuses on a mismatch. The MANIFEST line is unchanged in form. `fixture()` passes `spec.get('sha256')`.

- [ ] **Step 1: Record the base**

Append `## Plan 119: base and the sec-edgar source` to the record. Give `BASE119` (short and full sha, and branch).
Run `git diff --stat 8131b81 <BASE119> -- skills/derive-roadmap specs/baseline/red-baseline-new-project-entry`.
Expected: it prints nothing. If a line prints, stop and report it. Run `claude --version`. If no record section has run
the isolation probe at that version, run it as the record's "Isolation probe (Task 1 Step 5)" does, into
`pilot/probe-p119/`, and record that all five lines read `NO`.

- [ ] **Step 2: Write the failing check**

Build `dr-offer-yes` at `<BASE119>` twice into `/tmp/plan119-work/src-old` (with `CASE_REPOS` set to a links folder
`/tmp/plan119-work/repos/`, `sec-edgar` → `$HOME/Projects/archive/sec-edgar-cloud`, the other three →
`$HOME/Projects/<name>`) and `/tmp/plan119-work/src-new` (with `CASE_REPOS="$HOME/Projects"`). Expected now: the second
build refuses with `cannot read specs/sec-filing-index-ingestion-spec.md at 22c6767f`.

- [ ] **Step 3: Store the file and read it**

Write the file with `git -C ~/Projects/archive/sec-edgar-cloud show 22c6767f:specs/sec-filing-index-ingestion-spec.md`.
Check that `shasum -a 256` prints the pinned sha256. Add `'sha256'` to `SEC_SPEC` and change `repo_file` as the
Interfaces block says. Add a docstring paragraph that names the source of record: the stored file, its origin
(`lowmason/sec-edgar` at `22c6767f`, held now only in the archived clone) and its sha256.

- [ ] **Step 4: Run the check again**

Rebuild into `/tmp/plan119-work/src-new` with `CASE_REPOS="$HOME/Projects"`. Expected: `wrote 1 prompts`, and
`shasum -a 256 /tmp/plan119-work/src-old/dr-offer-yes.txt /tmp/plan119-work/src-new/dr-offer-yes.txt` prints one hash
twice. Then change one byte of a scratch copy of the stored file, point a test build at it, and expect the refusal.
Record both results.

- [ ] **Step 5: Commit**

```bash
git add specs/baseline/red-baseline-new-project-entry/kit specs/baseline/red-baseline-new-project-entry.md
git commit -m "test(specs): store the sec-edgar spec as the kit's source of record"
```

### Task 2: the two drops, at the current text (I14, I15)

**Files:**
- Modify: `cases.py` (add `dr-park-ranked-dated`)
- Create: `treatment/dr-known-progression-79-p119-now/` and `treatment/dr-known-progression-79-p119-base113/` (ten
  reps each), `treatment/dr-park-ranked-p119-now/` and `treatment/dr-park-ranked-dated-p119/` (ten reps each),
  `treatment/p119-t2-MANIFEST.txt`
- Modify: the record (append `## Plan 119: the two drops`)

**Interfaces:**
- Consumes: Task 1's builder.
- Produces: the I14 and I15 verdicts, which Task 7's summary reads.

- [ ] **Step 1: Add the dated variant and commit the decision rules**

`dr-park-ranked-dated` is `dr-park-ranked` with `TODAY` swapped (by `edit()`) for `Today is <run day>.` in every
fixture line, and the pass rule's `2026-11-06` swapped for that day. The run day is the day Step 2 runs. Append to the
record, before any rep: Open item 7's and Open item 8's decision rules, word for word, and the variant's date. Commit
with the message `test(specs): add plan 119's dated dr-park-ranked variant and decision rules`.

- [ ] **Step 2: Build and run, all on one day**

Build at `<BASE119>` into `/tmp/plan119-work/t2-now` (dr-known-progression-79, dr-park-ranked, dr-park-ranked-dated)
and at `171e763` into `/tmp/plan119-work/t2-base113` (dr-known-progression-79). Copy both manifests. Run ten reps
(`1 10`) into each of the four folders.

- [ ] **Step 3: Score and decide**

Score by the cases' rules and the readings of record: Provenance on bytes (owner, 2026-11-11) and no Echo (owner,
2026-11-17) for dr-known-progression-79, and plan 113's dr-park-ranked readings. Apply the two decision rules. Compute
the Fisher p with `math.comb` and give the counts. Write `### Plan 119: dr-known-progression-79, current text against
171e763` and `### Plan 119: dr-park-ranked and the run date`. Each ends with its verdict: repeats or sampling (I14),
and the date named or not named as the cause (I15). Add the spend row.

- [ ] **Step 4: Commit**

```bash
git add specs/baseline/red-baseline-new-project-entry specs/baseline/red-baseline-new-project-entry.md
git commit -m "test(specs): measure plan 113's two drops at the current text"
```

### Task 3: nine new cases and their leak check

**Files:**
- Modify: `cases.py` (new constants and nine `CASES` entries, after `dr-folded-req`)
- Modify: the record (append `## Plan 119: cases and leak check`)

**Interfaces:**
- Consumes: `case()`, `lines()`, `edit()`, `TODAY`, `STEP_TASK`, `DR`, `OCCUPANCY_ROADMAP_BLOCKED`,
  `resume_gap_fixture()`, `PLAN_3_HANDOFF`, `TWO_TRACK_ROADMAP`, `LOCK_ROADMAP`, `LOCK_PLAN_4_READ`,
  `LOCK_STAGE_1_FINDINGS`, `PROVISIONAL_LINE` and the provisional helper beside it, `DR_PROVISIONAL_ASK_FIXTURE`.
- Produces: `CASES` keys `dr-ask-commit`, `dr-resume-twice` (two fixtures:
  `DR_RESUME_TWICE_CONTROL_FIXTURE` and `DR_RESUME_TWICE_TREATMENT_FIXTURE`; the key builds the control one, and
  `dr-resume-twice-cited` builds the treatment one), `dr-gap-collision`, `dr-blocked-chain`, `dr-unusable-output`,
  `dr-partial-block`, `dr-stop-pending`, `dr-provisional-none` and `dr-provisional-decline`. All are `additive`, with
  texts `DR` and task `STEP_TASK`.

- [ ] **Step 1: Write the fixtures and rules**

Each fixture starts with `TODAY` and a repository line and holds the state below. Write each roadmap strictly in the
form `references/roadmap-format.md` gives at `BASE119`. Record each choice the format leaves open as a fixture judgment
call. Pass rules are exact copy.

1. `dr-ask-commit` (I2). The `dr-resume-blocked` session, then `[earlier]` your question (add a stage that builds
   `occupancy_hourly` from the bay-sensor events, your default), then `[now] Your partner: Approve. Add the stage.`
   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): the new stage entry, or the commit that adds it, cites plan 5's Handoff.
   Clause B (conformance): the reply commits the roadmap change before any "Next:" line.
   Clause C (conformance): the new stage is handed off, or the reply says it is next; Stage 3 is not handed off.
   Reading notes. Clause A: "plan 5, Handoff" in any field of the entry counts, and so does a commit message that names it; a citation of plan 3 alone fails A.
   ```
2. `dr-resume-twice` and `dr-resume-twice-cited` (I2). A second resume of the parking roadmap. The first resume, on
   2026-11-05, added Stage 2b (rebuild `occupancy_hourly` from bay-sensor events) at the Ask, and the partner approved
   it. Stage 2b is unticked, and nothing has shipped since. In the control fixture Stage 2b cites nothing. In the
   `-cited` fixture its `Consumes` line ends `(plan 5, Handoff; Resolved at resume, 2026-11-05)`. Both fixtures read plan
   5's Handoff bullet, as `dr-resume-blocked` does.
   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): the reply does not raise plan 5's missing occupancy_hourly again: it asks no question about it and proposes no new stage for it.
   Clause B (bar): the reply hands off Stage 2b with a "Next:" line.
   Clause C (conformance): Stage 3 and Stage 4 are not handed off.
   Reading notes. Clause A: naming the earlier answer as settled passes. Clause B: either routing passes.
   ```
3. `dr-gap-collision` (I3). The gap-analysis path (§1 to §3) over a hand-written spec `specs/bay-pricing-spec.md`
   with one built module. The partner approved the partition. `ls specs/` shows `bay-pricing-spec-roadmap.md`, and its
   first 12 lines show the roadmap header with `Source spec: specs/bay-pricing-pilot-spec.md`, another spec.
   `[now] Your partner: Go ahead and write the roadmap.`
   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): the reply does not write specs/bay-pricing-spec-roadmap.md, by tool call or as file content.
   Clause B (bar): the reply asks the partner for another name and writes no roadmap file before the answer.
   Clause C (conformance): the reply says that the existing file is another spec's roadmap, and it does not resume it.
   Reading notes. Clause B: a name proposed inside the question passes.
   ```
4. `dr-blocked-chain` (I4, the unticked-producer clause). `OCCUPANCY_ROADMAP_BLOCKED`, with Stage 4's `Consumes`
   changed to Stage 3's alert rule. Plan 5's Handoff bullet says `occupancy_hourly` was not built.
   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): the reply hands off no stage before the answer: no "Next:" line names a stage.
   Clause B (bar): one question names occupancy_hourly as unmet and says that it blocks Stage 3, and through Stage 3, Stage 4.
   Clause C (conformance): the question has a proposed default.
   Reading notes. Clause B: "Stage 3 and Stage 4" passes when the reply ties Stage 4 to Stage 3's output; two or more separate questions fail B.
   ```
5. `dr-unusable-output` (I4, the unusable-output path). `OCCUPANCY_ROADMAP`'s marker state, with plan 5's bullet:
   "`occupancy_hourly` shipped, but its hours are in UTC and two car parks have no rows, so Stage 3 cannot use it as it
   stands."
   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): the reply hands off no stage before the answer.
   Clause B (bar): one question names occupancy_hourly and the defect, with a default that fixes or accepts the shipped table: a stage that corrects it, or the Consumes amended.
   Clause C (conformance): the default does not rebuild occupancy_hourly from scratch.
   Reading notes. Clause B: a default named only "a stage added to produce it", with no word on the defect, fails B.
   ```
6. `dr-partial-block` (I5). `OCCUPANCY_ROADMAP_BLOCKED`, with Stage 4's `Consumes` changed to Stage 1's `bay_events`
   only, so Stage 4 is ready and Stage 3 is blocked by plan 5's bullet.
   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): one question names occupancy_hourly as unmet and Stage 3 as the stage it blocks, with a proposed default.
   Clause B (bar): no stage is handed off before the answer: no "Next:" line names a stage.
   Clause C (conformance): the question may propose Stage 4 as next; it is one question.
   Reading notes. Clause B: naming Stage 4 as ready inside the question passes.
   ```
7. `dr-stop-pending` (I9). `DR_PROVISIONAL_ASK_FIXTURE`'s session, with an `[earlier]` question that covered O6, Stage
   2's unmet `Consumes` and Track A's next stage, then `[now] Your partner: Stop Track A. Skip the rest.`
   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): O6 is not dropped without a word: it is parked as a deferred item, or the reply asks about it before it removes it.
   Clause B (bar): O6 is not treated as an approved outcome: it is not ranked, promoted or written as an ordinary item.
   Clause C (conformance): the track's other Ranked-list items each get one deferred item, and the roadmap stays live.
   Reading notes. Clause A: a deferred item for O6 that says it was never approved passes. Clause B: a deferred item for O6 with no such word fails B.
   ```
8. `dr-provisional-none` (I12). `LOCK_ROADMAP` made provisional, with no suggested item and Stage 1 unticked. The
   `git log` line dates the file 2026-11-05.
   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): no stage is handed off before the answer: no "Next:" line names a stage, and Stage 1 is not routed.
   Clause B (bar): one question asks the partner to approve or amend the file's partition or ranking.
   Clause C (conformance): the reply plans, specs and brainstorms nothing.
   Reading notes. Clause A: saying that Stage 1 follows once the partner answers passes.
   ```
9. `dr-provisional-decline` (I8). `DR_PROVISIONAL_ASK_FIXTURE`'s session, with an `[earlier]` question as in case 7,
   then `[now] Your partner: Decline O6. Amend Stage 2's Consumes to the weekly export. Promote O2.`
   ```
   PASS needs every bar and conformance clause.
   Clause A (bar): the reply removes O6's Outcomes row and list item, and Stage 1's Leaves out reads traceability: declined, with a date.
   Clause B (bar): the reply commits the roadmap with the decline before any "Next:" line.
   Clause C (conformance): Stage 2's Consumes is amended, and O2 becomes a stage entry.
   Reading notes. Clause A: any date passes. Clause B: one commit that holds the decline, the amendment and the new entry passes.
   ```

Leak words, one pattern each: `r'cites|citation|Handoff,'` (cases 1 and 2), `r'overwrite|another name|collision'`
(case 3), `r'blocked|unmet|unusable|beside a ready'` (cases 4 to 6), `r'never approved|parks too'` (case 7),
`r'provisional label|partition'` (case 8) and `r'declin'` (case 9). The format tokens the fixtures must hold
(`suggested, not approved`, `Leaves out`, `Ranked list`, `Consumes`) are not leak words.

- [ ] **Step 2: Check the cases load and build**

Run
`uv run python -c "import sys; sys.path.insert(0, 'specs/baseline/red-baseline-new-project-entry/kit'); import cases; print(len(cases.CASES))"`.
Expected: `41` (30 + Task 2's one + ten keys here). Then build `leakview` into `/tmp/plan119-work/leak` with the ten
keys. Expected: `wrote 10 prompts to /tmp/plan119-work/leak`.

- [ ] **Step 3: Run the leak check**

As the record's `## Leak check` does: grep each new case's hand-written fixture lines, then its leak-view prompt,
case-insensitively, for its leak words. Expected: 0 hits in hand-written lines. Trace every leak-view hit to its
source. Reword a hand-written line that hits, and rebuild into `/tmp/plan119-work/leak-2`. Also grep the ten prompts
for `red-baseline`, `plan 119`, `micro-test` and `quarantine`. Expected: 0 hits.

- [ ] **Step 4: Start the spend table and commit**

Append `## Plan 119: spend` with the stop ($40), the per-rep cap ($1.00) and a row per task (Task 2's row moves here).

```bash
git add specs/baseline/red-baseline-new-project-entry/kit/cases.py specs/baseline/red-baseline-new-project-entry.md
git commit -m "test(specs): add plan 119's resume, collision and parking cases"
```

### Task 4: control arms, before any skill edit

**Files:**
- Create: `control/<case>/rep1.json` … `rep5.json` for the nine control keys (all Task 3 keys but
  `dr-resume-twice-cited`), and `control/p119-MANIFEST.txt`
- Modify: the record (append `## Plan 119: control`)

**Interfaces:**
- Produces: one control verdict per case (RED, thin or clean). Task 5 reads the verdicts of `dr-blocked-chain` and
  `dr-unusable-output` to decide edits 2a and 2b.

- [ ] **Step 1: Build at `<BASE119>` into `/tmp/plan119-work/control`, then run five reps per case**

Expected: `wrote 9 prompts to /tmp/plan119-work/control`. Copy the manifest. Rerun a VOID rep with the next free rep
number.

- [ ] **Step 2: Score and record**

Score as plan 113's Task 2 Step 2 does, in `### Plan 119 control: <case>` sections. Name each case RED, thin or clean.
A clean control goes to the owner at the completion gate, and its item stays open. Add the spend row.

- [ ] **Step 3: Commit**

```bash
git add specs/baseline/red-baseline-new-project-entry specs/baseline/red-baseline-new-project-entry.md
git commit -m "test(specs): run plan 119's control arms"
```

### Task 5: the skill text

**Files:**
- Modify: `skills/derive-roadmap/SKILL.md` (§3; §5 Ask, Commit, the handoff line after the waiting paragraph, Parking)
- Modify: `skills/derive-roadmap/references/roadmap-format.md` (Ranked list, provisional paragraph)
- Modify: the record (append `## Plan 119: skill text`)

**Interfaces:**
- Consumes: Task 4's verdicts for edits 2a and 2b.
- Produces: the skill commit `T`, which Tasks 6 and 7 read.

- [ ] **Step 1: Edit the skill text**

Exact copy. Rewrap to the file's width. Change nothing else. "Old" is the match key at `BASE119`. Apply edits in
order. Edits 1, 2a and 2b touch one sentence pair, so each later match key is the text as the earlier edit leaves it.

1. §5 Ask, I5. Old: `When unticked stages remain and none has all its `Consumes` met, the same question` New:
   `When a Handoff or stamp shows a stage's `Consumes` input missing or not built, even beside a ready stage, or when unticked stages remain and none has all its `Consumes` met, the same question`
2. §5 Ask, I4. Apply each part only when its case's control fails a bar clause.
   - 2a (`dr-unusable-output`). Old: `a stage added to produce it, or the `Consumes` amended.` New:
     `a stage added to produce it (or to fix it, when it shipped but cannot be used), or the `Consumes` amended.`
   - 2b (`dr-blocked-chain`). Old: the sentence 2a leaves, ending `amended.` New: that sentence, then
     ` A stage whose input comes from a blocked stage is blocked too.`
3. §5 Commit, I2 and I8. Old: `**Commit** the amendments, and whatever your partner approved at the Ask, on the current branch before the handoff, so the fresh session reads them.`
   New: `**Commit** the amendments, and whatever your partner approved or declined at the Ask, on the current branch before the handoff, so the fresh session reads them. A change approved at the Ask for a Handoff bullet cites `plan <id>, Handoff`, as an amendment does.`
4. §5 Parking, I7. Old: `under a dated `## <name>-roadmap — <YYYY-MM-DD>` section. When your partner stops a research track,`
   New: `under a dated `## <name>-roadmap — <YYYY-MM-DD>` section (its heading uses the roadmap file's stem). When your partner stops a research track,`
5. §5 Parking, I9. Old: `section, and the roadmap stays live. Each item follows` New:
   `section, and the roadmap stays live. An item still marked `suggested, not approved` parks too, and its item says that your partner never approved it. Each item follows`
6. §5 Ask, I11. Old: `as ONE question, not a numbered list:` New:
   `as ONE question, not a numbered list of questions (numbered points inside one approve-or-amend request are one question):`
7. §5 Ask, I12. Old: `When nothing else is open, these items open the Ask by themselves.` New:
   `When nothing else is open, these items open the Ask by themselves. A file still labelled provisional also puts its partition into the same question, with or without such items, and on approval the label goes. A stage already ticked stays as built.`
   7b. Old: `Then, once no item marked `suggested, not approved` is open, hand off` New:
   `Then, once no item marked `suggested, not approved` is open and no provisional label is left, hand off`
8. §3, I3. Old: `Write `specs/<name>-roadmap.md` in the target repo per` New:
   `If `specs/<name>-roadmap.md` exists with another source, ask for another name: never overwrite it. Write `specs/<name>-roadmap.md` in the target repo per`
9. `roadmap-format.md` Ranked list, I10. Old: `Each also gets an Outcomes row, marked `suggested, not approved`.` New:
   `Each also gets an Outcomes row, marked `suggested, not approved`. The stage's `Leaves out` entry points at it by O-number, in the file and after approval.`

If the owner chose an alternative at plan review (Open items 2 to 4), the Decisions section gives the replacement
text, and this step applies it instead.

- [ ] **Step 2: Check the edits**

For each row, run `tr '\n' ' ' < <file> | tr -s ' ' | /usr/bin/grep -o -F '<phrase>' | wc -l` and expect the count.

| File | Phrase | Count |
|---|---|---|
| `SKILL.md` | `even beside a ready stage` | 1 |
| `SKILL.md` | `or to fix it, when it shipped but cannot be used` | 1 if 2a applied, else 0 |
| `SKILL.md` | `comes from a blocked stage is blocked too` | 1 if 2b applied, else 0 |
| `SKILL.md` | `approved or declined at the Ask` | 1 |
| `SKILL.md` | `for a Handoff bullet cites` | 1 |
| `SKILL.md` | `uses the roadmap file's stem` | 1 |
| `SKILL.md` | `parks too, and its item says` | 1 |
| `SKILL.md` | `are one question` | 1 |
| `SKILL.md` | `still labelled provisional` | 1 |
| `SKILL.md` | `no provisional label is left` | 1 |
| `SKILL.md` | `exists with another source` | 1 |
| `roadmap-format.md` | `in the file and after approval` | 1 |

Then
`uv run --with pyyaml python -c "import sys; sys.path.insert(0, 'build'); import check_conformance as c; print(len(c.skill_body(open('skills/derive-roadmap/SKILL.md').read())[0]))"`.
Expected: at most 20,000 (about 19,700). Run `uv run python build/check_links.py` and the commit gate.

- [ ] **Step 3: Commit, then record `T`**

```bash
git add skills/derive-roadmap/SKILL.md skills/derive-roadmap/references/roadmap-format.md
git commit -m "fix(derive-roadmap): settle resume blocks, provisional files and parking gaps"
```

Append `## Plan 119: skill text` to the record: the sha as `T`, the body size, which of 2a and 2b applied and why, and
the edit for each item. A fix that this task's review finds is a further skill commit here, before Task 6. The record
names the last one as `T`. Commit the record with the message `test(specs): record plan 119's skill commit`.

### Task 6: treatment arms for the new cases

**Files:**
- Create: `treatment/<case>-p119/` (five reps each) for the nine control keys and `dr-resume-twice-cited`, and
  `treatment/p119-t6-MANIFEST.txt`
- Modify: the record (append `## Plan 119: treatment`)

**Interfaces:**
- Consumes: `T` (Task 5) and Task 4's verdicts.
- Produces: the additive verdicts, and the last skill commit after any wording round here, which Task 7 reads.

- [ ] **Step 1: Build at `<T>` into `/tmp/plan119-work/t6` and run five reps per case**

Expected: `wrote 10 prompts to /tmp/plan119-work/t6`. `dr-resume-twice`'s treatment arm is the
`dr-resume-twice-cited` folder (Open item 6).

- [ ] **Step 2: Score, apply the additive bar, record**

Score as Task 4 Step 2, in `### Plan 119 treatment: <case>` sections. Each ends with its bar verdict against its
control. For a miss, follow the Bars' wording round: the new text, its commit as `T-r1`, the re-run cases in `-r1`
folders, and why each other case was not re-run. A second miss is an owner gate. Add the spend row.

- [ ] **Step 3: Commit**

```bash
git add specs/baseline/red-baseline-new-project-entry specs/baseline/red-baseline-new-project-entry.md
git commit -m "test(specs): run plan 119's treatment arms"
```

### Task 7: the guards and I1's runs at the final text, and the summary

**Files:**
- Create: `treatment/<case>-p119/` (five reps each) for the guards below, `treatment/dr-tracks-p119a/`,
  `treatment/dr-tracks-p119b/`, `treatment/dr-known-progression-79-p119/`, and `treatment/p119-t7-MANIFEST.txt`
- Modify: the record (append `## Plan 119: guards`, `## Plan 119: I1 runs` and `## Plan 119: summary`)

**Interfaces:**
- Consumes: `T-final`, the last skill commit. No skill commit may follow this task's runs.
- Produces: the verdicts that Plan completion reads.

- [ ] **Step 1: Build at `<T-final>` into `/tmp/plan119-work/t7` and run, all on one day**

Run five reps per guard below. Then three separate `run_reps.sh` calls, five reps each: `dr-tracks.txt` into
`dr-tracks-p119a`, `dr-tracks.txt` into `dr-tracks-p119b`, and `dr-known-progression-79.txt` into
`dr-known-progression-79-p119`. Neither dr-tracks run is read before both are complete.

| Guard | Reads edit | Compared with (record section, text) | Arm PASS | Guard needs |
|---|---|---|---|---|
| dr-resume-blocked | 1, 2, 3 | "Plan 113 guard: dr-resume-blocked", `2bd982d` | 5 of 5 | 4 |
| dr-resume-marker | 1, 3 | "Plan 113 guard: dr-resume-marker", `2bd982d` | 5 of 5 | 4 |
| dr-resume-rerank | 1, 6 | "Plan 113 guard: dr-resume-rerank", `2bd982d` | 5 of 5 | 4 |
| dr-rerank-second | 1, 6 | "Plan 113 guard: dr-rerank-second", `2bd982d` | 5 of 5 | 4 |
| dr-stop-track | 4, 5 | "Plan 113 guard: dr-stop-track", `2bd982d` | 5 of 5 | 4 |
| dr-park-ranked | 4, 5 | Task 2's `-p119-now` arm, first five reps | Task 2 | Task 2 count − 1, and I15's 3 |
| dr-park-ranked-dated | 4, 5 | Task 2's arm, first five reps | Task 2 | Task 2 count − 1, and I15's 3 |
| dr-resume-legacy | 1, 3 | "Plan 113 guard: dr-resume-legacy", `2bd982d` | 5 of 5 | 4 |
| dr-name-collision | 8 | "/deferred pass (2026-11-11): dr-name-collision at the final text", `e885184` | 5 of 5 | 4 |
| dr-provisional-ask | 6, 7, 9 | "Plan 113 treatment r1: dr-provisional-ask", `2bd982d` | 5 of 5 | 4 |
| dr-provisional-alone | 7, 9 | "Plan 113 treatment r1: dr-provisional-alone", `2bd982d` | 5 of 5 | 4 |
| dr-provisional-only | 6, 7, 9 | "Plan 113 treatment r1: dr-provisional-only", `2bd982d` | 5 of 5 | 4 |
| dr-quality-suggest | 9 | "Plan 113 guard: dr-quality-suggest", `2bd982d` | 5 of 5 | 4 |
| dr-offer-yes | 4 (I7) | "Plan 85 Task 4: dr-offer-yes", `2e91b05` | 5 of 5 | 4 |

- [ ] **Step 2: Score**

Guards are read by their rules and readings of record, other readings under "Other readings", never counted. For each
resume guard, also record, unscored, whether the reply reports a trap or deferred-item bullet that the fixture shows an
earlier resume already reported (I6's signal). A guard below its bar takes the Bars' wording round, then an owner
ruling. Score the I1 runs by the readings of record, Provenance on bytes and no Echo, with plan 85's item-4 reading and
Stage word test for dr-tracks. Each needs 4 of 5, with no wording round. Add the spend rows.

- [ ] **Step 3: Write the summary**

`## Plan 119: summary` holds: one table of every plan 119 arm; the spend total; each item of Plan completion with
whether its `Done when:` is met; the untested passages (Review Focus 5, and any passage changed after the arm that reads
it); I6's signal; and the owner-gate list.

- [ ] **Step 4: Commit**

```bash
git add specs/baseline/red-baseline-new-project-entry specs/baseline/red-baseline-new-project-entry.md
git commit -m "test(specs): run plan 119's guards and I1 runs, and the summary"
```

## Plan completion

The Plan Completion Protocol ticks each item from Task 7's summary. An item whose `Done when:` is not met stays open
with a dated note, and the miss goes to the owner at the gate.

- I1: Task 2's I14 verdict and Task 7's three runs (each 4 of 5 at `T-final`). I1 closes only if both hold.
- I2: edit 3, `dr-ask-commit`, and `dr-resume-twice` against `dr-resume-twice-cited`.
- I3: edit 8 and `dr-gap-collision`.
- I4: `dr-blocked-chain` and `dr-unusable-output`, with edits 2a and 2b as their controls decide.
- I5: edit 1 and `dr-partial-block`.
- I6: no tick. Task 7's signal record only, unless the owner keeps it.
- I7: edit 4, and the dr-offer-yes guard and I1's two dr-tracks runs.
- I8: edit 3, `dr-provisional-decline`, and the guards that read the Commit bullet.
- I9: edit 5 and `dr-stop-pending`.
- I10: edit 9 and the three `dr-provisional-*` guards.
- I11: edit 6, the owner's ruling (Decisions).
- I12: edits 7 and 7b and `dr-provisional-none`.
- I13: Task 1.
- I14: Task 2's comparison and its verdict.
- I15: Task 2's cause verdict and Task 7's dr-park-ranked (or, by Open item 8, dated) arm.
