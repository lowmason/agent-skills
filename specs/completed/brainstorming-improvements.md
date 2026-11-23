# brainstorming: suggested changes

**Status:** COMPLETE (2026-11-22). Plan 106 (`specs/plans/completed/106-brainstorming-improvements.md`) implemented items 1, 2, 4, 5, 6 and 8. Items 3 and 7 stay out, as Owner decisions says. At the completion gate the owner kept item 2's fix local, with no upstream PR. Before that: findings, owner rulings recorded and approved for planning (2026-11-22). No skill text was edited. This document lists ranked changes to `skills/brainstorming/`. The owner picked six of them (see Owner decisions), and this document is the input for writing-plans, with no spec in between.

**Date:** 2026-11-22. **Scope:** `skills/brainstorming/` and its NOTICE entry. No change is proposed for derive-roadmap, writing-plans, `/deferred` or `install.py`.

## Context

- **Body budget.** The SKILL.md body has 19,524 characters. Compaction keeps 20,000 characters of a skill, and the header and the truncation marker use part of that (plan 87). So the `compaction-window` check in `build/check_conformance.py` allows a body of 19,700 characters (`reserve_chars = 300`, `build/cc_guide/conformance.toml:297`). Only 176 characters are free. Plan 86's figure of about 476 came before plan 87 and is now too high. Each item below gives its character change.
- **Upstream.** superpowers has no brainstorming change after v7.0.2 (`22f0b46`, 2026-11-03). Its `main` and `dev` branches were checked on 2026-11-22. The other upstream branches with "brainstorming" in the name hold older work that v7.0.0 to v7.0.2 already carry.
- **Tests.** The kit in `specs/baseline/red-baseline-brainstorming-v7-0-2/kit/` runs the registered cases T1 to T13 and P1 to P3. In plan 86, a rep cost about $0.03, and a three-vote T7 panel cost about $0.55 (record, Spend table). The costs below use those figures.
- **NOTICE.** A change to text that came from upstream v7.0.2 needs a NOTICE sentence. The brainstorming entry starts at `NOTICE:742`.

## Ranked list

| Rank | Item | Body change (characters) | Re-run cost | NOTICE | Owner ruling |
|---|---|---|---|---|---|
| 1 | Free body room | about −450 | about $1.80 | yes | carry |
| 2 | Make Size the Work agree with the first-message design | about +60 to +120 | about $2.70 | yes | carry |
| 3 | T7: target the form the last wording round did not reach | about +80 | about $3.00 | yes | known gap |
| 4 | P3: "just write it up" does not hand over the how | about +90 | about $0.60 | yes | carry |
| 5 | Red Flags quick-task cell points back to the size rules | about +50 | about $0.30 | no | carry |
| 6 | Search the backlog, do not read it whole | about +10 | none possible | update one sentence | carry |
| 7 | Let the builder check read the project | 0 | by hand | yes | backlog, prove first |
| 8 | Fix three defects in `visual-companion.md` | 0 | server suite | yes | carry |

Items 1 to 5 change wording that the micro-tests measure. Items 6 to 8 do not. Items 2 to 5 together add about 280 to 340 characters, which is more than the 176 free. So item 1 must come first, or the changes must be split across rounds.

## Owner decisions

The owner ruled in chat on 2026-11-22 on the item set, on the three owner calls that items 1, 5 and 8 name, and on approval for planning.

1. **The item set.** Which items go into the plan?
   Ruling: carry items 1, 2, 4, 5, 6 and 8 in one plan. Item 3 stays a known gap, as the owner ruled on
   2026-11-06 and at plan 86's final review. Item 7 goes to the backlog with a prove-first note
   (`specs/deferred_items.md`, section `brainstorming-improvements`).
   Item 4 guards item 2: item 2 lets the agent make the pick when the partner "handed you the how", and P3
   fails through that same branch. P3 runs in item 2's re-run already. Item 2's re-run also measures T7 as a
   no-regression check, so leaving item 3 out keeps a T7 shift traceable to one edit.
2. **Item 1, the per-question paragraph.** Delete it from the body, given the compaction trade-off?
   Ruling: delete it. All three cuts go ahead, about −450 characters.
3. **Item 5, the wording.** Decision D18 set today's text, so the owner picks the new text.
   Ruling: keep today's cell and append "If the look shows a wider reach, step up a size." (about +49
   characters).
4. **Item 8, the Copilot CLI block.** Drop it, or keep it as upstream text?
   Ruling: keep it as upstream text, unchanged. A smaller diff against upstream makes the next superpowers
   port easier.
5. **Approval.** Is this document the input for writing-plans, with no spec in between?
   Ruling: approved for planning.

Not decided here: whether item 2's fix also goes upstream. Item 2 names it as the owner's choice, and it needs its own ask.

## Planning notes (not owner rulings)

The planning session wrote these notes after the owner's rulings. The owner did not rule on them. The plan settles the open one at plan review.

- **Room.** Item 1 frees about 450 characters, so free room goes from 176 to about 625. Items 2, 4, 5 and 6 add about 210 to 270, which leaves about 355 to 415.
- **Test rounds (open).** Items 1, 2, 4 and 5 change measured text, and items 6 and 8 need no micro-test. Whether items 1, 2, 4 and 5 share one micro-test round or run in more than one is not decided. Item 1's Re-run asks for its own run of the twelve guards. Run separately, the re-runs of items 1, 2, 4 and 5 cost about $5.40. A shared round costs less, because their case lists overlap.

## 1. Free body room first

Every other body change needs room. Do this one first.

**Evidence.**

- `SKILL.md:392-395` ("Per question, ask: would they understand this better by seeing it?") repeats `visual-companion.md:7` and `:25`. Those lines give the same test and the same warning that a UI topic is not always a visual question. The paragraph is upstream text (upstream SKILL.md:310 at `22f0b46`).
- The roadmap path appears five times: `SKILL.md:54-56`, `:243`, `:256-263`, `:272-274` and `:361-363`. These lines are local. Upstream has no derive-roadmap.

**Direction.**

- Delete the per-question paragraph from the body. `visual-companion.md` already carries it, so nothing moves. Keep the offer text and "If they accept, read `visual-companion.md`" in the body. The agent needs both before it reads the reference.
- Cut `:54-56` to a one-line pointer to Size the Work.
- In `:272-274`, cut only the trailing clause ", and it splits unrelated outcomes into tracks". It describes what derive-roadmap does. Keep the rest of that sentence: "goes to the New-Project Entry whole" is a brainstorming rule (do not split such a project into separate brainstorms), and no other body line says it.
- Keep the table row, the paragraph at `:256-263` and the HARD-GATE line.

**Trade-off.** After compaction, only the skill body comes back. A body without the per-question paragraph brings that rule back only if the agent reads `visual-companion.md` again. The owner should weigh this against the room it frees.

**Change.** About −278 characters for the deletion, about −125 for the pointer and about −46 for the clause: about −450 in all. Free room goes from 176 to about 625 characters.

**Re-run.** No registered case targets these lines, as I read the case list. Run the twelve guards once at 5 reps each to show no regression: about $1.80.

**NOTICE.** Yes for the deletion. The roadmap lines are already local.

## 2. Make Size the Work agree with the first-message design

This item is open in the backlog: `specs/deferred_items.md:6313`, section `86-brainstorming-v7-0-2-retune`, sized as a design.

**Evidence.** For a small change with nothing open and one sensible way, the first message carries the approach and the short design (`SKILL.md:46-48`, `:89-95`). But Size the Work says the Approaches part records "which one they picked", and "They pick in the conversation, before you write the design" (`:245-248`). In plan 86, T11 rep1 asked "Which do you want?" where an approval was due. Also, no path covers a first message where nothing is open but several ways fit.

**Direction.**

- Let the Approaches part record who made the pick: your human partner, or you when there was one sensible way or they handed you the how.
- Say that the pick and a small change's short design may come in one message.
- Add the missing path in Your First Message: when nothing is open but several ways fit, lay out the ways in the first message, and write no design yet.

**Change.** About +60 to +120 characters.

**Re-run.** The new path goes into Your First Message, so every case that passes through that passage runs. That is T11, T12, T13, P3 and the guards that reach an approval (T2, T3 and T5) at 5 reps (about $1.05), T10 at 5 reps (about $0.15), and T7 at 25 reps plus a panel (about $1.30). About $2.70 with a margin. Plan 86 missed T12 in the same way, so do not drop T7 or T10. The backlog's done-when also needs no regression on T13 and the approach guards.

**NOTICE.** Yes. Upstream carries the same two passages (its SKILL.md lines 72-75 and 219-221 at `22f0b46`). So the same fix could also go upstream. That is the owner's choice.

## 3. T7: target the form the last wording round did not reach

This item is optional. The owner ruled T7 a known gap on 2026-11-06 and again at plan 86's final review.

**Evidence.** T7 asks the first question when the reason for the request is unknown. The shipped copy passes 13 of 25 on the panel, and today's copy before the port passed 17 of 25. I recounted the panel verdicts in `panel/T7-r1/panel-verdicts.json`. The count agrees with the record (`red-baseline-brainstorming-v7-0-2.md:289-293` and `:415`).

| Fail form | Copy before the port | Shipped copy |
|---|---|---|
| What the blank "Date back" cells might mean, in one sentence or as bullets | 4 | 8 |
| Tools, fixes or problems named in one sentence | 4 | 4 |
| All fails | 8 of 25 | 12 of 25 |

Wording round 1 cut the tools form on the first new copy from 10 to 3 (record `:415`). It did not reach the blank-cells form. That form sits in the findings part of the first message. Shipped rep16 is an example: "The seeds might still be out, someone might have forgotten to log a return, or…".

Two hypotheses compete. Neither is shown.

- **Findings push it.** "Add what you found that bears on it" (`SKILL.md:77-78`) predates the port. "Do recon… Say what you looked for and what you found" (`:173-175`) is new in the port.
- **A removed sentence held it back.** The port removed "a single sentence with no list of example answers hanging off it", which the copy before the port carried (record `:296`). But that copy still had 4 blank-cell fails, so the sentence did not stop the form fully.

The fixture also invites the form, because it plants the blank cells. With 25 reps a copy, the split is descriptive, not a shown cause.

**Direction.** Ask the owner a rule question first: does a list of what a finding might mean count as a menu? The registered rule says yes (record `:26`). If no, change the rule and leave the skill text. If yes, two directions fit, one for each hypothesis:

- Add one clause to the findings sentence: report a puzzling finding as a fact, say you cannot tell yet what it means, and list no meanings.
- Restore a short form of the removed sentence: the question is one sentence, with no list of possible answers before or after it.

**Change.** About +80 characters.

**Re-run.** T7 at 25 reps plus a panel: about $1.30. T10 to T13 at 5 reps: about $0.60. The guards that pass through the first message (T1 to T5, T8a and T8b) at 5 reps: about $1.05. About $3.00 in all.

**NOTICE.** Yes.

## 4. P3: "just write it up" does not hand over the how

This item is optional. The owner accepted the P3 miss as a known gap at plan 86's final review.

**Evidence.** The P3 guard puts impatience on the agent ("just write it up"). It passes 3 of 5 on the shipped copy and 5 of 5 on the copy before the port. The four fails on the first new copy write the design with the pick inside, as "my call". Three of them say the partner handed over the how (record `:255`). They follow the branch at `SKILL.md:185-187`: "if they've handed you the how, say you'll go with your pick instead, and write the design in the next message".

Wording round 1 (`9761c88`) already edited this branch. It added "and write the design in the next message", and P3 went from 1 of 5 to 3 of 5. A new clause would stack on a passage that the owner has already tuned once.

**Direction.** Add one clause: a push to hurry speeds the process but does not hand you the how. The approaches still go first, in a message of their own.

**Change.** About +90 characters.

**Re-run.** P3, P1, T12 and T13 at 5 reps: about $0.60.

**NOTICE.** Yes.

## 5. Red Flags quick-task cell points back to the size rules

This item is open in the backlog as a quick fix: `specs/deferred_items.md:5491`. The owner picks the wording (decision D18 set the current text).

**Evidence.** The cell says "Reading is fine. If it's still quick and clear once you've looked, do it, and say what you did and what else it touches." A reader can take "do it" to mean the edit, even when the look found a wider reach. The backlog item cites `SKILL.md:332`, `:33` and `:233`. Those line numbers are stale: the cell is now `:376`, and "If it grows mid-task, stop, say so, and step up a size" is now `:269`. Line `:33` is still right.

**Direction.** Point the cell back to the size rules. When the look finds a wider reach, step up a size.

**Change.** About +50 characters.

**Re-run.** P2b and T1 at 5 reps: about $0.30. The reps have no tools. So the kit shows only what a reply says it will do, not what an agent does after it sees a search result. The backlog item says the same.

**NOTICE.** No. The row is local (NOTICE:790 counts it but does not quote it).

## 6. Search the backlog, do not read it whole

**Evidence.** `SKILL.md:64-65` says to "check" `specs/deferred_items.md` for deferred work the idea touches. In this repo that file has 7,247 lines. A full read takes context that the rest of the brainstorm needs.

**Direction.** Say "search it for the idea's terms" in place of "check it".

**Change.** About +10 characters.

**Re-run.** None can show it, because the kit's reps have no tools. This is a judgment edit.

**NOTICE.** The line is local. NOTICE:771 names it, so update that sentence if its words change.

## 7. Let the builder check read the project

**Evidence.** `builder-check-prompt.md:12` tells the builder to read the design only. Then the sort at `SKILL.md:324-325` drops each question "Answered already by the conversation or the project". writing-plans reads the codebase when it plans. So a builder who cannot read the code asks questions that the planner would not ask, and the main agent spends time to drop them.

**Direction.** Add a line to the prompt: the builder may read the project at a given root, and reports only what neither the design nor the project answers. Keep "You will not be able to talk to the person who wrote it."

**Change.** None in the body. The prompt is a separate file.

**Re-run.** No registered case covers the builder check. Try it by hand on one recent spec, with and without the line, and compare the two question lists.

**NOTICE.** Yes. NOTICE says the prompt is copied from upstream unchanged.

## 8. Fix three defects in `visual-companion.md`

**Evidence and direction.**

1. `visual-companion.md:77-82` gives Gemini CLI launch steps (`is_background: true`). This repo's `gemini` runtime targets agy (CLAUDE.md, Runtime adapters). The agy guide (`specs/guides/antigravity-customization-guide.md`) does not say how to keep a background process alive. Check agy itself before you rewrite the block. Do not guess.
2. `:84-90` gives Copilot CLI launch steps. This repo installs for Claude, Codex and agy only. Drop the block, or keep it as upstream text and say so in NOTICE.
3. `:289-291` runs `stop-server.sh $SESSION_DIR`. The startup JSON returns only `screen_dir` and `state_dir` (`:40-43`). The script wants the session directory (`scripts/stop-server.sh:3`), which is the parent of both. Say that.

Optional: add one line that an agent whose harness has its own browser pane can open the URL there, in place of `--open`. Keep the line free of any one harness's tool names, because the repo is portable.

**Change.** None in the body.

**Re-run.** `uv run python build/run_suites.py brainstorming` if a script changes. The doc edits need no micro-test.

**NOTICE.** Yes, for each change to upstream text.

## Not proposed

- **An `evals/` folder under the skill.** The skill-creator skill would add one. This repo already has registered micro-test kits in `specs/baseline/`. Also, `install.py` links the whole skill directory, so an `evals/` folder would ship with the installed skill.
- **A description change.** I found no evidence that the skill triggers too often or too rarely. No trigger-eval suite exists to measure a change either (`build/cc_guide/conformance.toml:623-631`, `description-when-only`, revisit line). That entry keeps descriptions trigger-only. It does not bar a tighter trigger list.
