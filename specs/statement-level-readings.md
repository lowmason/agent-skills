# Statement-level readings at plan review — Design Spec

**Status:** DRAFT (2026-11-09), for the owner's review.

This spec redesigns the finding 24 half of `specs/spec-derived-acceptance-tests.md`, called "the old spec" below.
Finding 24 is "Planner-authored tests can share a spec misreading" (`specs/superpowers-drift-spec-v7-0-2.md`). The
design came from a brainstorming session on 2026-11-09. That session followed the owner's ruling at plan 81's
review gate on 2026-11-08 (`specs/deferred_items.md:5352`). Decisions D9–D13 are the owner's. They continue the old
spec's D1–D8, so every id stays unique. Text marked *(designer's call)* is the designer's choice. The list under
"Designer's calls" collects them.

> **For agentic workers:** plan the probe first, as its own plan (Verification, "Probe first"). Write no build
> plan until the owner has reviewed the probe's results (D8, carried).

## What this spec replaces and keeps

The old spec (APPROVED 2026-11-08) covers findings 21 and 24. Another session plans its finding 21 half, the
test-run script (old Design 1), from that file. This spec takes over finding 24 only.

**Replaced.** These parts of the old spec no longer apply. This spec's parts take their place:

- The Goals bullets for the second reader, the adjudicator, unclear cases at plan review, acceptance-test runs
  during execution and the probe (`:58-65`).
- The anti-goals on the second reader's inputs and on acceptance-test edits (`:80`, `:84`).
- The Approaches section and its pick, approach A (`:87-124`, D6). D11 and D13 replace them.
- Design 2 to 6 (`:173-254`): the second reader, the adjudicator, plan review, execution and model tiers.
- Design 1's clause "plus the acceptance tests that the task makes runnable (part 5)" (`:163-164`). No acceptance
  tests exist in this design.
- Verification: "Probe first" steps 1 to 5 and the proposed bars (`:258-292`). Plan 81 ran that probe, and its
  record stands. The micro-test bullets for the second reader, the adjudicator and the acceptance tests
  (`:299-300`, `:302-304`) go too.
- The parts of "Closing the backlog and the drift spec" that close layers 3 and 5 and finding 24 (`:359-370`).
- The designer's calls that serve only those parts.

**Carried.** These parts apply here as well, and this spec restates them where it uses them:

- D3, the adjudicator. It now rules on differences between the two readers, and it never sees the plan (D12).
- D7, the cheaper Codex model. D8, the probe as its own plan, first.
- The assessment "What a second reading can and cannot catch" (`:33-49`), adapted below.
- The anti-goals on unquoted rulings, on stops in every run and on Codex data (`:81-83`, `:85`).
- The Constraints "Codex data" and "Codex model" (`:332-347`).

**Kept as they stand.** Everything else in the old spec serves finding 21, and this spec does not change it.

**Closure.** The old spec ties finding 24's closure to its build plan (`:359-370`). This spec's section "Closing the
backlog and the drift spec" moves it.

## Intent

Today the planner writes the plan's tests from its own reading of the spec. The implementer then writes code that
passes them. So a misreading in the plan passes every test (old spec, Intent).

Plan 81 tested one fix: a second reader that writes acceptance tests from the spec, and an Opus adjudicator that
rules on conflicts. The control was a fresh `claude -p` session that runs the Self-Review checklist. It caught all
15 planted misreads, and no test-writing arm caught more than 11. Plan 81's results file,
`specs/red-baseline-acceptance-tests.md`, is called "the record" below (sections 3 and 4).

The owner's direction (D9): two readers "check whether the agree on what is being asked rather than writing code
and rests separately". Claude and Codex each state what the spec asks, in fixed slots, from the spec alone. A script
compares the two statements with each other, and both with the plan's values.

Statements may beat the control where tests did not, for three reasons:

- **The control was a best case** (record, section 8, item 7). It was a fresh session, and each plant was a bare
  contradiction that nothing in the plan defended. A real misread comes from the planner's own reading, and the
  planner may defend it in the plan. A reviewer that reads the plan also reads the defense. The readers never see
  the plan, and a script cannot be argued with.
- **A unit slot does not depend on inputs.** Plan 81's unit plant got through because 14 of 15 reader runs tested
  with ASCII text only. For ASCII text, characters and bytes give the same count (record, section 8, item 2).
- **Disagreement marks ambiguity.** Two readers that differ mark a sentence with two readings. An "other reading"
  slot lets one reader mark it alone.

Nobody has measured any of this. So the probe comes first (D8, carried).

### What a statement can and cannot catch

This adapts the old spec's assessment (`:33-49`). It is the designer's view, and the probe tests the first two
points.

- **It catches a stated value that the plan changed:** the value, its unit, its edge or its default. The plan's
  defense of the value does not reach the comparison.
- **It finds ambiguity, but it cannot resolve it.** Two readers that differ, or one reader that names another
  reading, send the sentence to the owner.
- **It misses shared blind spots.** Where the spec says nothing, or both readers take one reading and name no
  other, the step sees nothing. Two models reading one spec are likely correlated (Knight and Leveson, 1986).
- **It misses errors that are not stated values.** A missing task or a dropped requirement stays with Self-Review
  and the final code-reviewer. Plan 81's control found several such errors in approved plans (record, section 6).

## Goals, non-goals and anti-goals

**Goals.**

- At plan review, Claude and Codex each state what the spec asks, in fixed slots, from the spec alone (D9, D11).
- The planner states its own plan's values in the same slots, before the readers run (D13).
- A script compares the statements. No Claude agent compares a statement with the plan's values (D10).
- The adjudicator (D3) rules on each difference between the two readers, from the spec and their two statements
  only. It rules only when it can quote the text that decides the case. The owner gets the rest (D12).
- The owner sees each unclear sentence and each plan value that the planner keeps against the agreed reading, in
  the plan review message.
- A probe with harder plants measures the step against the fresh-session control before any skill text changes
  (D8, D9).

**Non-goals.**

- Tests from a second reader, hidden or visible, and any run of them during execution (D9, D12). Statements leave
  nothing to run. Finding 21's test-run script still ships from the old spec, and the final code-reviewer still
  reads the spec (plan 73). So code that passes the visible tests and misreads the spec is caught at the final
  review at the earliest.
- Errors that are not stated values (D12). Self-Review keeps them.
- Finding 21's half. The old spec keeps it.
- Worked examples from the owner (old D4). When a spec states examples, they are stated values like any other.
- Layer 4 of the backlog item: spec excerpts in the implementer brief. It stays open in the backlog item.
- Mutation testing. The backlog item rules it out.

**Anti-goals.** Each of these makes the design a failure, even if it works:

- A reader sees any part of the plan. Its statement is then a copy of the planner's reading.
- A Claude agent compares a statement with the plan's values, or reads the plan to rule on a case (D10).
- The adjudicator rules without quoting the text that decides the case.
- The planner writes its statement after it sees a reader's statement.
- The planner drops a case without a fix or an owner ruling.
- The step adds a stop to every run, or a ruling for the owner on every task.
- A Codex run sends a project's spec to OpenAI without the owner's approval for that project.

## Approaches

**Where the readers run (D11).**

- **At plan review, in writing-plans (chosen).** The owner's words were "for writing-plans". The plan's values exist
  there, so the readers and the comparison run in one step. An unclear sentence becomes a spec-amendment task, a
  route that writing-plans already has (`skills/writing-plans/SKILL.md:242-246`). One skill changes.
- **At spec approval, in brainstorming.** A difference between the readers would mark an unclear sentence while the
  owner is still in the design conversation. The designer would then fix the spec before any plan exists. But two
  skills change, Codex sends every spec to OpenAI at approval, and the saved statements must track later spec
  amendments.

**How the plan's values are found and compared (D13).** Both ways obey D10.

| | A. The planner states its values (chosen) | B. Codex finds the plan's values |
|---|---|---|
| Who finds the plan's values | The planner fills the same slots, and cites the plan lines that use each value. | Codex reads the plan and the agreed reading, and lists each place where the plan differs. |
| Who compares | A script | Codex |
| Who reads the plan's defense of a value | No one | Codex |
| Without Codex approval | Still runs | No comparison with the plan |
| Extra cost for each plan | The planner's slot entries | One more Codex run, about 10 minutes at plan 81's effort |
| Main risk | The planner's statement can differ from its own plan. | Codex can miss a place, or follow the plan's defense. |

**The pick: A (D13).** A script cannot be argued with, and that matters most for a plan that defends a wrong value.
A also works where Codex is not approved. Its main risk can be measured: the probe reports how often a stand-in
planner's statement carries the planted value (Verification, step 4).

The design dropped three ideas:

- **A Claude agent that reads the plan.** D10 rules it out.
- **A script that searches the plan for each agreed value.** It finds where a value appears, but not where the plan
  states another value.
- **The test-writing second reader of the old spec.** Plan 81's control caught every plant that it did, and more.
  D9 replaced it.

## Owner decisions (2026-11-09)

- **D9. Statement-level readings, tested by a probe first** (owner, 2026-11-08, at plan 81's review gate). "What if
  for writing-plans, the Claude and Codex subagente merely check whether the agree on what is being asked rather
  than writing code and rests separately." Then "Go ahead", to a recommendation that said: "**But don't stake the
  build plan on them yet.** No probe has shown that any second reading beats a fresh Self-Review." and "**A spec
  revision, in its own session:** Claude and Codex each state what the spec asks, in fixed slots, from the spec
  alone. One step compares the two statements with each other, and both with the plan's values. A small probe
  tests this with harder plants: a wrong value that the plan argues for, and spec sentences with two readings. The
  bar to beat is the fresh-session control."
- **D10. The backlog rule covers the comparison step.** Asked: "Does the 'no further Claude reviewers that start from
  the plan' rule cover the comparison step?" The owner: "Yes, it applies". Reading: a script or Codex compares the
  statements with the plan's values, never a Claude agent. The rule "Add no further Claude reviewers that start
  from the plan." (`specs/deferred_items.md:5334-5335`) stands unchanged.
- **D11. The readers run at plan review.** Asked: "Where should the two readers run: at plan review or at spec
  approval?" The owner: "At plan review".
- **D12. The playbacks stand.** "Looks right", to the playback of the reading step, and again to the playback of the
  probe. The designer proposed these parts in the playbacks, and the owner accepted them:
  - A script numbers the spec's sentences, and each entry names its sentence number.
  - The slots, the "other reading" slot included (Design 3).
  - Claude reads alone where Codex is not approved.
  - D3 applies to each difference between the readers and to each "other reading". The adjudicator rules from the
    spec and the two statements, and it sees nothing from the plan.
  - The planner fixes each plan value that differs from the agreed reading, or the case goes to the owner.
  - The comparison skips each sentence that the plan's own amendment tasks change.
  - The probe's kit, plants, arms and bars (Verification). The non-goals on tests and on errors that are not
    stated values.
- **D13. Approach A: the planner states its values, and a script compares.** The owner: "A, planner states". The
  approaches message added two rules: the planner writes its statement before the readers run, and it marks each
  sentence that its amendment tasks change.

## Design

### 1. The step and its order

The step runs in writing-plans, after Self-Review and before the plan review message (D11). In
`skills/writing-plans/SKILL.md`, Self-Review starts at `:208` and Plan review at `:233`. The order:

1. The numbering script numbers the requirement text's sentences (part 2).
2. The planner writes its statement and saves it (part 4).
3. The two readers write their statements from the numbered text alone (part 5).
4. The comparison script compares the two readers' statements (part 6).
5. The adjudicator rules on each case from step 4 (part 7).
6. The comparison script compares the agreed reading with the planner's statement (part 6).
7. The planner answers each case from step 6 (part 8).
8. The plan review message lists the cases (part 8).

**The requirement text** is the text that the plan's `**Spec:**` line names (`skills/writing-plans/SKILL.md:99`). That
is usually a spec. It can also be backlog items or a brief.

**Scope** *(designer's call)*: every plan whose `**Spec:**` line names requirement text. The step needs no test
steps, so it also covers prose and skill-text plans. A plan whose `**Spec:**` line names none skips the step, and the
plan review message says so. The probe tests code plans only, so the owner may narrow the scope at the build plan.

**Working files** *(designer's call)*: the numbered text, the three statements and the case lists go to a scratch
directory outside the checkout. They are not committed. The plan review message carries the outcome, and the owner's
rulings go to `## Decisions`. The old spec's `## Acceptance` plan section is not needed.

### 2. The numbering script

- It splits the requirement text into numbered sentences, `S1` to `Sn`, and writes a numbered copy (D12).
- A table row counts as one sentence, and so does a fenced block. Each sentence keeps its section heading for
  context *(designer's call)*.
- The same input always gives the same numbers. So the three statements key their entries alike.

### 3. The slots

A **stated value** is a value that the plan must match exactly *(designer's call)*. It can be a number, a limit, a
unit, a default, a date or time, a name, a path or exact text. Each stated value gets one entry. The slots (D12):

| Slot | Holds | Form |
|---|---|---|
| `sentence` | the sentence number | `S<n>` |
| `quote` | the words of the sentence that state the value | copied word for word |
| `subject` | what the value applies to: a field, an option, a file or a command *(designer's call)* | words copied from the sentence |
| `value` | the value | a literal in plain notation: a number, a string, a list in brackets, a date or time |
| `unit` | what the value counts or measures | the spec's word, such as `characters`, or `none` |
| `edge` | for each limit in the value, whether the limit itself is in | `in`, `out`, or `n/a` with no limit |
| `default` | the value used when the input is absent | a literal, or `none` |
| `other_reading` | another reading that the words allow | the same slots, or `none` |

- A sentence that states two values gets two entries. `subject` tells them apart, because a quote alone does not.
  The writer copies `subject` from the sentence's own words, so that two writers word it alike.
- The readers fill every slot. The planner leaves out `other_reading` and adds two slots (D13). `plan_lines` gives
  the plan lines that use the value. `amended` names the plan's amendment task that changes the sentence, or holds
  `none`.
- The comparison script checks that each `quote` occurs in its numbered sentence. It returns an entry that fails
  this check to its writer *(designer's call)*.

### 4. The planner's statement (D13)

- After Self-Review, the planner fills the slots for each value that its plan uses, keyed by the sentence numbers.
- It states the value that its plan implements, not a fresh reading of the spec. It writes that value in the slot
  forms of part 3, as the readers do, and not in the plan's code syntax *(designer's call)*. For example, a plan
  line `DEFAULT_PYTHONS = ('3.13',)` gives the default `['3.13']`. Each entry cites the plan lines that hold the
  value, so the planner reads its plan, not the spec, while it fills the slots.
- If it finds that its plan and the spec differ while it fills the slots, it fixes the plan first. That is
  Self-Review at work. A planner that writes the spec's value over an unfixed plan defeats the step. The probe
  measures how often that happens (Verification, step 4).
- It saves the statement before any reader runs. After that, it changes the statement only to answer a case.

### 5. The readers

- **Claude and Codex** (D9). Each gets the numbered text and the slot instructions, and nothing from the plan: no
  plan path, Tech Stack line, Files list or Interfaces block. A statement needs no module names, unlike a test.
- **The Claude reader** cannot reach the plan. It has no tools, or none that can read the checkout *(designer's
  call)*. The builder picks the mechanism. The reader runs at the capable tier.
- **The Codex reader** runs `codex exec` with plan 81's isolation flags: no shell and no web search (record,
  Appendix A). It runs from a directory that holds only the numbered text, and it names its model with `-m` (D7).
- **Without Codex approval** for the project, Claude reads alone, and the plan review message says "one reading"
  (D12). The comparison rules below still apply, with one reader's statement always absent.

### 6. The comparison script

**Pairing** *(designer's call)*. The script pairs entries by sentence number. When each statement has one entry for a
sentence, those entries pair, whatever their `subject`. Only a sentence with several entries in one statement pairs
them by `subject`. An entry that still has no partner is treated as absent below. The case for that sentence also
lists the unpaired entry, so the planner sees both.

**Matching** *(designer's call)*. Two entries match when their `value`, `unit`, `edge` and `default` slots match after
normalization. `quote` and `subject` are not compared. The script lowercases, maps dashes, strips quotes and
backticks, collapses spaces, and reads number forms and list forms alike. Plan 81's `measure.py` matching rules are a
start. The same inputs always give the same cases.

The rules below apply to each pair, with reader entries A and B and planner entry P:

1. **The readers agree.** A and B match, and neither names another reading. Their reading is the agreed reading.
2. **The readers differ.** A and B do not match. The adjudicator rules (part 7).
3. **One reader only** *(designer's call)*. If P matches the lone entry, there is no case. Otherwise the adjudicator
   rules whether the sentence states that value.
4. **Another reading.** A reader's `other_reading` is not `none`. The adjudicator rules whether the text decides
   between the readings (part 7).
5. **Neither reader** lists the sentence, and P does. There is no case, and the plan's value stands unchecked. The
   probe counts these entries.

Then, for each agreed reading:

6. **P matches.** There is no case.
7. **P differs.** This is a **plan conflict** (part 8).
8. **P is absent.** This is a **missing entry** *(designer's call)*. The planner adds the entry, or marks the sentence
   unused. A sentence that the plan must build and does not is a gap, and the planner adds the task.
9. **P names an amendment.** The script skips the sentence and lists it (D12). The owner approves the plan's
   amendments at plan review anyway. In plan 81, they caused most of the false alarms in the test-writing arms
   (record, section 3).

### 7. The adjudicator (D3)

- It reads the whole numbered text and, for each case, the readers' entries. It never sees the plan, the planner's
  statement or a plan path (D10, D12).
- For each case, it returns the reading that the text supports, in the slots or as `no value` *(designer's call:
  the form)*. It quotes the words that decide the case, word for word. With no deciding text, it rules `unclear`
  (D3).
- An unclear sentence goes to the owner at plan review.
- It runs on Opus, pinned (D3). It edits no file.

### 8. The planner's answers and the plan review message

- **A plan conflict.** The planner fixes the plan at every line that uses the value, and its own entry. Or it keeps
  its value, and the case goes to the owner with the planner's reason. It never drops a case.
- **A missing entry.** The planner adds the entry, marks the sentence unused, or adds the missing task (part 6,
  rule 8).
- The planner re-runs Self-Review on whatever changed, as writing-plans already asks (`:251-252`).
- **The plan review message** lists the owner's cases first. Each unclear sentence comes with its readings. Each
  kept value comes with the agreed reading, its quote and the planner's reason. Then, for information, it lists the
  plan values fixed, the missing entries answered, the sentences skipped as amended, and "one reading" when Claude
  read alone.
- The owner's answers are decisions, routed as writing-plans routes any (`:238-246`). A plan-level one goes into
  `## Decisions`. A spec-level one goes into a spec-amendment task.

### 9. Model tiers

- The Claude reader: the capable tier. The probe uses `opus`.
- The Codex reader: the cheapest model that meets the probe's bars, `gpt-6-sol` first (D7).
- The adjudicator: Opus (D3).
- Every dispatch names its model (old spec, Design 6).

## Verification

### Probe first

The probe runs as its own plan, before any build plan and before any skill text changes (D8, D9). The owner reviews
its results. Nobody writes a build plan before that review.

1. **The kit** (D12). Copy `specs/red-baseline-acceptance-tests/kit/` to `specs/red-baseline-statement-readings/kit/`
   *(designer's call: the path)*. Leave the original unchanged, because plan 81's record and its copies'
   `MANIFEST.txt` point at it. Reuse the plant tools (`plants.py`, `make_copies.py`, `extract.py`) and the runners
   (`run_reps.sh`, and `run_codex.sh` with its isolation flags). Write new parts: the numbering script, the reader
   prompt, the planner stand-in prompt, the adjudicator prompt, the comparison script and a scorer. The scripts get
   self-tests, as plan 81's kit had.
2. **The copies** (D12). Build them in the new folder with their own `MANIFEST.txt`, from plan 81's sources (plan 53
   at `b8f4d0f`, plan 66 at `526b7de` and plan 55 at `f0ebef6`):
   - **Three argued plants:** plan 81's unit plant (`p53`), bound plant (`p66`) and default plant (`p55`), at every
     site as before. Each plan also gets one plausible sentence that defends the planted value. The defense is the
     planner's reasoning, not an owner decision. It sits where a planner would write it, such as a Global
     Constraints line or an approach line *(designer's call)*.
   - **Two two-reading plants:** two copies whose spec has one sentence edited, so that it allows two plausible
     readings. The plan's value matches one of them, and the plan stays as approved. The probe plan records both
     readings before any run.
   - **The clean copy:** plan 55 unchanged, as plan 81's `p55-clean`, to count false alarms.
3. **The readers.** The readers see only the numbered spec, so one set of reader runs serves every copy of one spec.
   Five Claude runs and five Codex runs for each distinct spec: the three originals and the two edited specs.
4. **The planner stand-in** (D13). A fresh `claude -p` call plays the planner for each copy. It gets the copy and the
   numbered spec, is told that it wrote the plan, and states each value as its plan uses it. Five runs for each
   copy. The scorer reports the stand-in's **fidelity** apart from the catches: how often its statement carries the
   planted value.
5. **The comparison.** Run *i* pairs reader run *i* with stand-in run *i*. The comparison script and the adjudicator
   (`opus`) run on that pair. The adjudicator's prompt holds the numbered spec and the readers' entries, never the
   copy or the stand-in's statement (D10).
6. **The control.** A fresh `claude -p` Self-Review, as in plan 81: its control prompt with today's writing-plans
   text, the spec and the whole copy. Five runs for each planted copy. The control does not rerun the clean copy,
   because the bars count false alarms for the step only *(designer's call)*. Plan 81's control results on the bare
   plants (15 of 15) stay the reference for plants with no defense.
7. **The arms.** The treatment is the step with both readers. From the same runs, the scorer also reports Claude
   alone and Codex alone, each as a one-reader step (D12). Codex runs `gpt-6-sol` first, and `gpt-6.1-sol` only if
   `gpt-6-sol` misses a bar (D7).
8. **The measures**, for each arm and copy:
   - **Catches.** On an argued plant, a catch is a plan conflict on the planted sentence. In it, the agreed reading
     holds the spec's value, and the planner's entry holds the planted value. On a two-reading plant, a catch is an
     `unclear` ruling on the planted sentence, so that it reaches the owner. The scorer reports a plan conflict on
     that sentence apart. For the control, plan 81's catch rule applies on an argued plant. On a two-reading plant,
     any control finding that quotes the edited sentence is a catch *(designer's call)*. The scorer reports near
     catches apart, as plan 81's did.
   - **False alarms**, on the clean copy: each plan conflict against a plan value that agrees with the spec. A
     person labels each plan conflict by hand with a reason line, as in plan 81's `CLASSIFY.txt` files. A conflict on
     a real error in the approved plan gets the label real, not false alarm.
   - **Unclear cases**, on the clean copy: each `unclear` ruling. Every one counts against the unclear bar, because
     each one reaches the owner. A person also labels each one by hand, with a reason line *(designer's call)*. The
     label is `ambiguous` when the sentence truly allows two readings, and `false` when the text decides it. The
     results report both counts, for the owner's review.
   - **Owner load:** the unclear rulings and plan conflicts for each plan. No planner answers a plan conflict in the
     probe, so this count is an upper bound.
   - **Fidelity** (step 4), and the missing entries for each plan.
   - **Cost:** dollars for Claude, tokens for Codex.
9. **The bars** (D12):
   - The step catches each new plant in at least 4 of 5 runs, and the control catches it in at most 2 of 5. On a
     plant that the control catches in 3 or more runs, the step shows no gain.
   - On the clean copy, the step raises at most one false alarm and at most one unclear case per plan. Each bar uses
     the mean over the 5 runs.
   - The second reader stays only if the pair beats Claude alone on catches or on false alarms. This adapts the old
     spec's rule for the Codex arm *(designer's call)*.
   - The owner reviews the results against the bars. The owner decides whether anyone writes a build plan, and what
     it keeps (D8). The designer reads the bars this way *(designer's call)*. A build plan is worth writing only if
     the step beats the control on one plant or more. The step must also meet both clean-copy bars.
10. **The results** go to `specs/red-baseline-statement-readings.md`, linked from this spec *(designer's call)*.
    That file states the probe's limits, as plan 81's section 8 did. These limits are known now:
    - 5 runs for each arm and copy.
    - One person labels the cases.
    - The control is a fresh session.
    - The stand-in is not a real planner.
    - The two-reading plants are edits, not natural ambiguity.
    - The control's checklist has no item for ambiguity. So on a two-reading plant, the comparison mostly measures
      the step's own catch rate, and the clean-copy bars carry more of the verdict.

### If the owner approves a build

The build plan, if any, adds the step to writing-plans. This section outlines it, so that the probe tests what would
ship.

- The numbering script and the comparison script go to `skills/writing-plans/scripts/` *(designer's call)*, with
  pytest cases. That folder's suite is already registered in `build/suites.toml`.
- The step's text goes to a new `references/` file in writing-plans, with one pointer line in the body (Constraints,
  "Room").
- The reader and adjudicator prompts go beside it. An agent file, if the builder makes one, needs
  `build/sync_runtime_assets.py` and its `--check`.
- Each behavior that the wording shapes gets a micro-test against a no-guidance control, with the repository's
  isolated kit, as writing-skills requires:
  - The planner writes its statement before any reader runs, and states its plan's values, not a fresh reading.
  - The planner gives the readers only the numbered requirement text.
  - The adjudicator quotes the deciding text, and rules `unclear` when no text decides.
  - The planner fixes a plan conflict at every plan line, or sends it to the owner, and never drops it.
  - The plan review message lists unclear sentences and kept values first.

## Constraints

- **Order (D8).** The probe plan comes first. It changes no skill text and needs no other plan. A build plan comes
  only after the owner's review of the probe's results.
- **Room.** On 2026-11-09 at `d067b7e`, writing-plans' body is 19,689 characters. The compaction window is 20,000
  (`build/cc_guide/conformance.toml`, `compaction-window`: 5,000 tokens at 4 characters). So 311 characters are
  left, enough for one pointer line. A build plan measures the room again on `main`. If other plans used the room
  first, the build needs an equal cut. The other choice is the writing-plans references split that the old spec's
  Constraints describe ("Order").
- **Codex data** (carried). A Codex run sends the numbered spec, and every file that it reads, to OpenAI. In the
  probe, Codex reads only the numbered spec copies. `CLAUDE.md:54` approves Codex reviews only. So the probe plan
  asks the owner for approval in each session that runs Codex. The built step asks once per session until the
  owner extends that line.
- **Codex model** (carried). The old spec's Constraints record the checks on 2026-11-08 (`:335-347`). Each Codex
  run names its model with `-m`, and the probe records each run's model and effort. A Codex run started through
  `claude -p` needs `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` raised.
- **Isolation.** Claude runs use plan 81's flags, under `env -i` when a Desktop session drives them. Codex runs use
  plan 81's Task 4 flags (record, Appendix A).
- **No baseline from plan 81's treatment arms.** Their adjudicator prompts did not pair the reader's tests with
  their tasks (record, section 8, item 1). This spec uses only plan 81's control results, as the reference for the
  bare plants.
- **False alarms.** The bars compare catches with the control, and count false alarms on the clean copy. In plan
  81, 59 of the control's 72 false alarms were findings on today's writing-plans format. The copied plans predate
  that format (record, sections 3 and 8, item 6).
- **Watch items** in `specs/deferred_items.md`, § 81-spec-derived-acceptance-tests:
  - **Fires:** "`measure.py score` does not VOID a Codex reader rep whose log shows tool activity" (`:6103`). This
    probe scores Codex reader runs with a scorer built from a copy of plan 81's `measure.py`, so the copy carries
    the gap. The new scorer runs the residual check inside its score step. The probe plan names the item, and the
    old kit stays unchanged.
  - **Does not fire:** "Rerun the 60 adjudicator reps on paired prompts" (`:6110`). Its trigger is a redesign that
    keeps test-writing second readers, and this design has none.
- **Leave alone.** Plan 81's record, kit, copies and runs. The old spec's finding 21 parts.
- **Lints.** `build/run_commit_lints.sh` passes before each commit.

## Provenance

- The step, the slots, the scripts, the adjudicator's new scope and the probe are this repository's own work. The
  build would add them to writing-plans, which adapts upstream superpowers (MIT, `LICENSE-superpowers`). NOTICE then
  records them as local changes.
- The probe kit adapts plan 81's kit, which is this repository's own work.
- Knight and Leveson (1986) is cited for an idea only (carried).
- No text or fixture comes from `prime-radiant-inc/superpowers-evals`, which carries no license (carried).

## Closing the backlog and the drift spec

The backlog item "Spec-reading test check" (`specs/deferred_items.md:5306`) is done when "a brainstorming spec decides
the layers and records the baseline probe results" (`:5344-5345`). This spec decides the layers. Layer 3 becomes the
reading step, if the probe and the owner keep it. Layer 5's acceptance tests go (D9). Layer 1 stays out (old D4), and
layer 4 stays open. The probe's results file records the results.

- **The probe plan's completion** adds a progress note to the item that points at the results file. If the owner
  then decides on no build plan, that completion also closes finding 24's line, as below *(designer's call)*.
- **The plan that closes the line** is the probe plan with no build, or else the build plan. It ticks the item. Its
  closing note says what happened to layers 3 and 5. It also says that layer 1 applies only when a spec has examples
  (old D4), and that layer 4 stays open as a new item. Finding 21's own closure stays with the old spec's build
  plan.
- The same plan updates finding 24, and its bullet under "Suggested disposition", in
  `specs/superpowers-drift-spec-v7-0-2.md`, from the file as it stands on `main` at that time. It also retires this
  spec.

## Designer's calls

These were not put to the owner one by one:

1. **The requirement text and the scope.** Every plan whose `**Spec:**` line names requirement text, prose and
   skill-text plans included. The probe tests code plans only.
2. **Working files outside the checkout,** and no new plan section.
3. **Numbering units.** A table row or a fenced block counts as one sentence, with its heading for context.
4. **What counts as a stated value.**
5. **The `subject` slot,** copied from the sentence's words, so that one sentence can carry two entries.
6. **The quote check.** An entry whose quote is not in its sentence goes back to its writer.
7. **Pairing and matching.** Entries pair by sentence number, and by `subject` only within a sentence that has
   several entries. Only `value`, `unit`, `edge` and `default` are compared, after normalization that starts from
   plan 81's matching rules.
8. **Comparison rule 3.** A lone reader entry that the plan matches needs no ruling.
9. **Comparison rule 8.** A missing planner entry is a case for the planner, not for the owner.
10. **The Claude reader has no way to the plan,** and the builder picks the mechanism.
11. **The planner's slot forms.** The planner states its plan's value in the slot forms, not in the plan's code
    syntax, and cites the plan lines that hold it.
12. **The adjudicator's output:** a reading in the slots, or `no value`, with the deciding quote, or `unclear`.
13. **The kit path,** `specs/red-baseline-statement-readings/kit/`.
14. **Where the planted defense sits,** and that it is not an owner decision.
15. **Five stand-in runs per copy.** The stand-in itself, and its fidelity count, come from D13.
16. **The control's catch on a two-reading plant:** any finding that quotes the edited sentence. The control does
    not rerun the clean copy.
17. **Unclear cases on the clean copy.** Every one counts against the unclear bar. Each also gets a hand label,
    `ambiguous` or `false`, and the results report both counts.
18. **The reading of the bars.** A build is worth planning only if the step beats the control on one plant or more.
    The step must also meet both clean-copy bars. The second reader stays only if the pair beats Claude alone, as
    the old spec ruled for the Codex arm.
19. **The results file,** `specs/red-baseline-statement-readings.md`.
20. **Closure:** the plan that ends finding 24's line ticks the item.
21. **The scripts' home in a build,** `skills/writing-plans/scripts/`.

## Left to the builder

- The exact splitting rules of the numbering script.
- The statement file format and the exact normalization rules.
- Whether the comparison script also checks that a planner entry's `value` appears in a cited plan line. That check
  would be a cheap guard on the planner's fidelity for literal values.
- The text of the reader, stand-in and adjudicator prompts.
- The mechanism that keeps the Claude reader from the plan, and whether the readers and the adjudicator are agent
  files.
- The two-reading edits and the defense sentences, which the probe plan writes before any run.
- Whether the adjudicator runs once per spec or once per copy in the probe. Its prompt holds no plan text either way.
- The layout of the plan review message.
- The micro-test cases and their bars.
