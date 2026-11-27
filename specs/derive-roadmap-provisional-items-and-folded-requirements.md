# derive-roadmap: provisional items and folded requirements — Design Spec

**Status:** DRAFT (2026-11-27), for owner review. The design came from a brainstorming session on 2026-11-27,
opened by a `/deferred` Design pick. Decisions D1 and D2 are the owner's, from that session, and so is D2's one-path
form after the builder check. Text marked *(designer's call)* is the designer's choice.

Two gaps in `skills/derive-roadmap/`, both found in plan 85's final review, and one open re-run from plan 79. First,
a provisional roadmap marks a suggested later quality `suggested, not approved`, and no rule ever asks the owner to
approve, rank or decline it. Second, the completion review (§6) lists a spec requirement as unmet whenever no
outcome's `Spec` cell cites it, even when a stage built it. Third, `dr-tracks` still needs two independent
five-rep runs at the final text.

## Motivation

Three items in `specs/deferred_items.md`:

| Item (section) | What goes wrong | Evidence |
|---|---|---|
| "A resume that finds a later quality and asks nothing else has no question for it to join" (`85-derive-roadmap-later-qualities-and-spec-refs`), narrowed by the owner on 2026-11-17 to its second gap | When the session cannot ask, `references/roadmap-format.md` (Ranked list) gives each suggested quality an O-number, a list place and an Outcomes row, all marked `suggested, not approved`. No rule in §4 or §5 asks the owner about these items, so the label can stay for ever and the item can be promoted like an approved outcome. | `references/roadmap-format.md`, last paragraph of Ranked list; commit `59df779`. |
| "A spec requirement that the partner folds into constraints is listed as unmet at §6" (`85-derive-roadmap-later-qualities-and-spec-refs`) | §6 lists each numbered spec requirement that no outcome's `Spec` cell cites as unmet (spec R12 of the plan 85 spec). The roadmap format has no constraints field, so a requirement the owner folded into a stage's constraints has no record in the roadmap, and §6 reports it as unmet even when the stage's plan implemented it. | `SKILL.md` §6; `specs/completed/derive-roadmap-later-qualities-and-spec-refs.md`, R12. |
| "dr-tracks and dr-known-progression-79 miss conformance clause C at the final skill text" (`79-derive-roadmap-resume-and-route-tests`) | The owner settled the readings: Provenance on bytes (2026-11-11) and no Echo (2026-11-17). Only the runs remain: two independent five-rep `dr-tracks` runs and a `dr-known-progression-79` run, each at 4 of 5 or better. | `specs/baseline/red-baseline-new-project-entry.md` (Plan 79 and Plan 85 summaries, owner rulings). |

## Decisions (owner, 2026-11-27)

- **D1. §6 checks evidence, not cells** (option B of three). A numbered spec requirement that no outcome's `Spec`
  cell cites is not unmet on that fact alone. It goes through the same gap rubric as every other requirement in
  §6, with evidence. It is met when a stage's plan, stamp or Handoff shows it was implemented, and the verdict cites
  that evidence. It is unmet when nothing shows it, and then exits by the two existing ways: a new stage, or
  conscious deferral with a written why. Rejected: (A) a new stage field that records folded spec refs, which adds a
  format field and more cases; (C) forbidding the fold at §4, which adds friction at the checkpoint. R12's purpose,
  to catch a requirement dropped with no record, stays.
- **D2. The first session that can ask settles every provisional item** (option A of two, in its one-path form).
  The owner first picked A: the §4 checkpoint asks about each `suggested, not approved` item, with a §5 resume
  fallback. The builder check then found that a provisional roadmap carries the roadmap header, so entry rule 1
  sends every later session on it to §5, Resume, and no rule sends it back to §4. The checkpoint and the fallback
  are therefore one path, and the owner took that form (2026-11-27): a §5 resume that finds any
  `suggested, not approved` item puts each one in the Ask's ONE question, to approve with a rank or to decline. When
  nothing else is open, the items open the Ask by themselves. Nothing is handed off and nothing is promoted before
  the answer. The label on each item is the marker; no new field. The answer is recorded as an approval or a decline
  is recorded today (`references/roadmap-format.md`, Ranked list). Rejected: (B) a resume rule that leaves the
  partition approvable while the label stays; a new "provisional" marker with an entry rule that routes such a file
  to §4, which adds a format field (a non-goal).

## Goals, non-goals and anti-goals

**Goals.**
- No `suggested, not approved` item survives a session that can ask the owner.
- An item marked `suggested, not approved` is never promoted to a stage, and never counted as an outcome, until the
  owner approves it. *(designer's call: the plain consequence of D2, stated so the plan tests it)*
- §6 reports a spec requirement as unmet only when no evidence shows it was built.
- `dr-tracks` and `dr-known-progression-79` meet their bars at the final text, so plan 79's item closes.

**Non-goals.**
- A constraints field, or any new field, in the roadmap format.
- Changing how a roadmap is written when the session can ask (the §4 suggestion flow of plan 85 stays as it is).
- Re-opening the dropped resume half of the plan 85 spec's D4 and R7: a quality found for the first time at a
  resume still joins no question.
- Old-format roadmaps (no `Outcomes` column) and roadmaps with no spec: D1 changes nothing for them.

**Anti-goals.** It fails, even if the cases pass, when:
- a resume or checkpoint promotes a `suggested, not approved` item without the owner's answer;
- §6 marks a requirement met with no cited evidence (a silent pass is worse than a false unmet);
- the fix restates spec requirement text in the roadmap (§3's brevity budget).

## Requirements

- **R1 (D2).** §5: a resume that finds any item marked `suggested, not approved` puts each one in the Ask's ONE
  question: approve with a rank, or decline. When the resume has nothing else to ask, the items open the Ask by
  themselves. Nothing is handed off before the answer. On approval the item drops the label and is an ordinary
  outcome. On a decline its Outcomes row and list item go, and the stage's `Leaves out` entry reads
  `<quality>: declined, <YYYY-MM-DD>`, as the existing decline rule says.
- **R2 (goal 2).** Until the answer, a `suggested, not approved` item is not promoted and not counted as an outcome
  in §5 or §6. A research track whose committed stages are all ticked and whose Ranked list holds only such items
  counts as waiting on its Ranked list (§5). Its one question asks the owner to approve and rank each item first,
  and only then proposes the next stage, so the owner's single answer settles both. *(designer's call)*
- **R3 (D1).** §6: for a roadmap whose `Source` is a spec, each numbered spec requirement that no outcome's `Spec`
  cell cites goes through the gap rubric with evidence, as the other requirements do. Met needs the rubric's own
  evidence, a path:line or a test name (`references/gap-rubric.md`), and the verdict names the stage plan that built
  it. A stage stamp alone is not enough, since a stamp names no requirement. Unmet exits by a new stage or a written
  deferral. *(designer's call: the evidence standard)*

## Verification

All micro-tests use plan 78's kit (`specs/baseline/red-baseline-new-project-entry/kit/`), its runner, record and
bars (4 of 5 per case).

- **V1 (R1, R2).** Two new fixtures, one case each, each with a control at this plan's base and then a treatment.
  (a) The first interactive resume of a provisional roadmap that also has other changes to ask about, with one
  `suggested, not approved` item: the one question covers the item (approve with a rank, or decline) beside the
  other changes. (b) A resume whose stages give no Ask, with one such item: the item opens the Ask by itself. In
  both, nothing is handed off or promoted before the answer.
- **V2 (R3).** A new case: a spec-sourced roadmap at §6, with one requirement folded into a stage (no outcome cites
  it) and a stage plan and code file that implemented it, and a second uncited requirement with no evidence. The
  reply marks the first met with a path:line or test name and the plan cited, and the second unmet with the two
  exits. Control, then treatment.
- **V3 (item 5095).** Two independent five-rep `dr-tracks` runs and one `dr-known-progression-79` run at the final
  text, each at 4 of 5 or better, scored by the readings of record (Provenance on bytes; no Echo). *(designer's
  call: these double as guards for this spec's edits)* A run below its bar is recorded and goes to the owner. The
  plan does not reword §7 or `references/new-project-entry.md`, which this spec does not change, and item 5095 then
  stays open. *(designer's call)*
- **V4 (guards).** Non-regression re-runs of the cases that read text this spec changes: at least
  `dr-quality-suggest`, `dr-spec-column`, `dr-resume-rerank`, `dr-resume-marker` and `dr-resume-blocked`. The plan
  names the full set from the edits it makes.

## Constraints

- **Examples stay out of the fixtures (micro-test Channel 3).** New skill text uses a transit agency's trip records
  for any example, as plans 78 and 85 do.
- **Compaction window.** The derive-roadmap SKILL.md body (17,818 characters at this spec's base) stays at most
  20,000 characters. No description change.
- **Leave alone.** `references/gap-rubric.md`, the §4 flow for a session that can ask, old-format roadmap rules, and
  every other skill.
- **Order.** No execution starts while another plan executes in this repository (owner ruling, 2026-10-28).
- **Public repository.** No private detail in the spec, plan, kit or record.

## Left to the builder

- The exact wording of R1 to R3, and which file holds each rule. Follow the existing split: steps in `SKILL.md`,
  the rules behind them in `references/roadmap-format.md`.
- The fixtures, pass rules and leak words of V1 and V2.
- Whether a declined item's O-number is freed or burned. *(designer's call: burned, so O-numbers in history never
  change meaning, unless the builder finds a rule that says otherwise)*
- The spend stop for the plan's micro-tests. *(designer's call: $30, as plans 79 and 85)*

## Out of scope

- A quality found for the first time at a resume (dropped from the plan 85 spec on 2026-11-17).
- Any change to writing-plans, brainstorming or `/deferred`.
