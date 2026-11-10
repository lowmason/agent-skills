# derive-roadmap: later qualities and spec references — Design Spec

**Status:** APPROVED (2026-11-07). The design came from a brainstorming session on 2026-11-07, opened by a
`/deferred` Design pick. Decisions D1–D8 are the owner's, from that session. Text marked *(designer's call)* was the
designer's choice. The owner approved this file, its designer's calls included, on 2026-11-07 ("Spec approved").

Three follow-ups to plan 78's New-Project Entry in `skills/derive-roadmap/`. First, the one message keeps
stage text out and records the later qualities in one fixed line. Second, a later quality joins a research track's
Ranked list only after the owner approves it and ranks it. Third, a new-project roadmap built from a spec keeps each
outcome's spec references, so a stage plan and the completion review can read them.

## Motivation

Three items in `specs/deferred_items.md` came out of plan 78's micro-tests and final review:

| Item (section) | What goes wrong | Evidence |
|---|---|---|
| "The derive-roadmap new-project offer still draws core-and-later-stages text before the partner ranks" (`deferred-2026-11-07`) | Replies describe a core stage and later stages in the one message, before the owner ranks anything. The owner ruled that this is a stage list, so `dr-offer-yes` stays at 3 of 5 (bar 4 of 5). | `specs/baseline/red-baseline-new-project-entry.md`, Task 3 summary and owner gate, Task 7. Quotes: "It would leave out manifests, pointers, the withdrawal gate and Azure, each placed in a named later stage." (round 2, rep2); "Some qualities go to later stages, never a core stage's Exit:" (dr-tracks, round 2, rep1). |
| "A later quality in a research track's Ranked list has no O-number and no partner rank" (`78-derive-roadmap-new-project-entry`) | A quality that a stage's `Leaves out` sends to the Ranked list has neither, so replies add it as an unranked item. | `skills/derive-roadmap/references/roadmap-format.md`, Ranked list. |
| "A new-project roadmap built from a spec maps each outcome to no spec section reference" (`78-derive-roadmap-new-project-entry`) | `Outcomes` replaced `Spec` and `Gap closed` (plan 78's spec, R10). A stage plan is scoped to one-line outcomes, and the completion review audits only the Outcomes list. | `skills/derive-roadmap/SKILL.md` §4 handoff, §6. |

The first two meet in one paragraph, "Later qualities" in `references/new-project-entry.md`. Its sentence "Check
the project against each one, and place every one it will need" carries no timing. It is the likely source of the
early stage text, and it creates the list items that have no number.

## Goals, non-goals and anti-goals

**Goals.**
- The one message names no stage, core or later, and still records which later qualities the project will need.
- Every item in a Ranked list has an O-number and the owner's rank.
- A stage plan from a roadmap with a spec is held to the spec sections behind its outcomes, minus what its stage
  leaves out.
- The completion review of such a roadmap shows each spec requirement that no outcome carries.

**Non-goals.**
- No change to old-format roadmaps, the gap rubric, or the §1 offer.
- No change to known-progression tracks beyond the one-message line and the timing (D5).
- No new kind of list entry: an approved quality is an ordinary outcome.

**Anti-goals.**
- A quality placed or suggested for a stage before the owner ranks the outcomes.
- Requirement text copied into the roadmap. The roadmap cites, it never restates.
- A core stage pulled up to the spec's full standard through the new references.

## Approaches

1. **One spec, one plan, full tests** *(picked)*. All three changes in one plan, with re-runs of the cases that read
   the changed text, two new cases and one stage-plan probe. The three changes touch the same two files and the
   same two moments, the one message and the approval. One kit pass serves them all.
2. **Two specs.** Items 1 and 3 in one, the `Spec` column in another. Smaller plans, but both edit the same files,
   executions run one at a time, and each pays for its own control and treatment arms.
3. **One spec, re-runs only.** The cheapest. The two new behaviors would ship untested, and the spec-reference item's
   own `Done when:` asks for the stage-plan check.

The owner picked 1 on 2026-11-07.

## Decisions (owner, 2026-11-07)

- **D1.** A later quality bound for a research track's Ranked list is suggested with its reasoning (why this project
  will need it). If the owner approves it, the skill asks for its rank.
- **D2.** An approved quality gets the next free O-number and a row in the Outcomes table, and is then an ordinary list
  item. A declined quality is recorded in the stage's `Leaves out` as declined, with the date.
- **D3.** The suggestion and the rank request go in one question.
- **D4.** The suggestion comes at the first roadmap's approval (§4). A quality first found at a resume uses the same
  form inside the resume's one question (§5).
- **D5.** The one message may hold one line of a fixed form that names the qualities with no stage words. "Check the
  project against each one, and place every one it will need" moves to the time the stages are written.
- **D6.** A stage plan from a roadmap with a spec is held to the spec sections behind its outcomes, except what the
  stage's `Leaves out` names. The Outcomes table gains a `Spec` column of refs. The completion review uses it.
- **D7.** Approach 1.
- **D8.** Check before, place later: the check of the project against the later qualities runs before the one
  message, and its result goes only into R2's line. Placing waits for the time the stages are written. (Answer to the
  builder check's timing question.)

## Requirements

**One message and timing (D5).**

- **R1.** §7 step 4 of `SKILL.md` and "The one message" in `references/new-project-entry.md` say that the message names
  no stage, core or later, the rule that §1's offer already states.
- **R2.** When the check (R3) finds a quality the project will need, the one message holds one line in exactly this
  form, after the outcome list:
  `Qualities to place when the roadmap is written: <names>.`
  The line gives names only. It carries no reason and none of the words "stage", "core", "first" or "later". With no
  quality to name, the line is left out.
- **R3.** In "Later qualities", the check runs before the one message, and its result goes only into R2's line. The
  placing ("place every one it will need") happens when the stages are written (§7 step 5), not in the one message
  (D8). The examples list stays.

**Qualities in a research track (D1–D4).**

- **R4.** When a research-track stage's `Leaves out` sends a quality to the Ranked list, the §4 approval message
  suggests it: its name, one line on why this project will need it, and the outcome line it would become. The same
  question asks the owner to approve it and, if approved, to give its place in the track's ranking. It is one question
  for the whole approval, as §4's approval already is.
- **R5.** Before the answer, the roadmap file holds no list item for a suggested quality. The stage's `Leaves out`
  names it as suggested, for example `traceability: suggested, see the approval question`. *(designer's call: the
  form of that interim entry)*
- **R6.** On approval, the quality gets the next free O-number, a row in the Outcomes table (outcome line, track,
  the owner's rank, a cost note) and its ranked place in the list. The `Leaves out` entry then points at it by
  O-number. On a decline, the `Leaves out` entry reads `<quality>: declined, <YYYY-MM-DD>`, and no list item is made.
- **R7.** At a resume (§5), a quality found for the first time goes into the one question in the same form as R4,
  and R6 applies to the answer.
- **R8.** Once approved, the quality is an ordinary outcome: it is re-ranked, promoted, parked and audited like any
  other, with no special case in §5, the Parking rule or §6.
- **R9.** When the session cannot ask, the provisional file lists each suggested quality at the end of the Ranked list
  with its next free O-number and the label `suggested, not approved`. *(designer's call)*

**Spec references (D6).**

- **R10.** With a spec, the Outcomes table carries a `Spec` column after `Outcome`: the § and R refs each outcome came
  from, refs only, never requirement text. With no spec, the column is left out. An approved quality's row holds the
  refs of any spec section that asks for it, or `none`.
- **R11.** The §4 handoff for a new-project roadmap with a spec scopes the stage plan to the stage's `Outcomes`, the
  spec refs those outcomes carry, minus what the stage's `Leaves out` names. A stage routed to brainstorming gets
  the same refs as its inputs. *(designer's call: the brainstorming half)*
- **R12.** §6 for a new-project roadmap with a spec lists each numbered spec requirement that no outcome's `Spec` cell
  cites. Each one exits by the two existing ways: a new stage, or conscious deferral with a written why.

## Verification

All micro-tests use plan 78's kit (`specs/baseline/red-baseline-new-project-entry/kit/`) and its runner, record and bars.

- **V1.** `dr-offer-yes` re-runs at the new text and passes its bar, 4 of 5, by plan 78's committed
  core-and-later-stages reading. This closes the item for early stage text.
- **V2.** Non-regression (guard) re-runs: `dr-offer-scaffold`, `dr-tracks`, `dr-known-progression-79`,
  `dr-research-depth`, `dr-resume-rerank`, and plan 79's `dr-rerank-second`, `dr-stop-track` and `dr-park-ranked`,
  each against its latest plan 79 or plan 78 arm, named from plan 79's summary. Each reads text that this spec
  changes (§5, §6, §7 and the two references). *(designer's call: the plan 79 cases join the guards)*
- **V3.** A new case: a research-track roadmap being written, where the core stage leaves out a quality the project
  needs. The approval message suggests it with a reason, asks to approve and rank it in one question, and the file
  holds no unnumbered list item.
- **V4.** A new case: a new-project roadmap written from a spec fills the `Spec` column with refs and copies no
  requirement text.
- **V5.** A probe: one stage plan, written by writing-plans from a V4-style roadmap, is read against the spec. It
  passes when the plan cites the spec sections behind its stage's outcomes and keeps out what `Leaves out` names.
  This meets the spec-reference item's `Done when:` (one stage plan checked against its spec). A fail gets one
  wording round on R11's handoff text, the only text this spec can change for it, then an owner ruling, as plan 78's
  Bars rule does for a case. *(designer's call)*
- **V1's line note.** The `dr-offer-yes` and `dr-tracks` re-runs record, unscored, whether each reply carries R2's
  line, and whether the line keeps its form (names only, no reason, no stage word).
- **V1's control and reading.** V1's control runs fresh at this plan's base, because plan 78's control predates §7.
  The plan fixes V1's reading of record before any rep, in its Open for plan review section. *(designer's call)*

## Constraints

- **Order.** The plan for this spec executes after plan 79 (`specs/plans/79-derive-roadmap-resume-and-route-tests.md`)
  ends, and builds on its edits to `roadmap-format.md` (Ranked list) and `SKILL.md` §7 step 4. No execution starts
  while another plan executes in this repository (owner ruling, 2026-10-28).
- **Examples stay out of the fixtures (micro-test Channel 3).** New skill text uses a transit agency's trip records for
  any example, as plan 78's text does.
- **Compaction window.** The derive-roadmap SKILL.md body stays at most 20,000 characters. No description changes.
- **Leave alone.** `references/gap-rubric.md`, §1's offer, old-format roadmap rules, and every other skill.
- **Public repository.** No private detail in the spec, plan, kit or record.

## Left to the builder

- The exact wording of R1, R3, R4, R6, R7, R11 and R12, within the requirements. R2's line is exact copy.
- Which file holds each rule: `SKILL.md` §4, §5, §6, §7, or `references/new-project-entry.md` and
  `references/roadmap-format.md`. Follow plan 78's split: steps in `SKILL.md`, the rules behind them in the
  references.
- The fixtures, pass rules and leak words of V3 and V4, and how V5's probe is run and read.
- The spend stop for the plan's micro-tests. *(designer's call: $30, as plan 79)*

## Out of scope

- Re-ranking or numbering for known-progression tracks, whose qualities are named later stages that the owner
  approves with the partition.
- A `Spec` column, or any spec link, for a roadmap with no spec.
- Changes to writing-plans or brainstorming. R11 changes only what derive-roadmap's handoff names.

## Rollout note

Next: writing-plans, in a fresh session, after plan 79's execution ends. The plan is written then, not before:
its comparison arms, base commit and match keys come from plan 79's summary and final text. On commit, this spec's path goes as
`→ planned` on the three items in the Motivation table.

Designer's calls for the owner to check: R5 (the interim `Leaves out` entry), R9 (the provisional label), R11 (the
brainstorming half), V2's added guards, V5's fail path, V1's control and reading, and the $30 spend stop.
