# Independent test evidence: controller test runs and spec-derived acceptance tests — Design Spec

**Status:** APPROVED (2026-11-08). The owner approved this file, its designer's calls included, on 2026-11-08
("Spec approved"). The design came from a brainstorming session on 2026-11-08, opened on
`specs/superpowers-drift-spec-v7-0-2.md`. It covers that assessment's finding 21
("Per-task test evidence is self-reported in SDD") and finding 24 ("Planner-authored tests can share a spec
misreading"). Finding 22 (spec drift) moved to its own session on the same day (D2). Decisions D1–D8 are the
owner's. Text marked *(designer's call)* is the designer's choice. The list under "Designer's calls" collects them.

> **For agentic workers:** this spec gets two plans (D8). Plan the probe first, as its own plan
> (Verification, "Probe first"). Write the build plan only after the owner has reviewed the probe's results.

## Intent

Today one reading of the spec produces both the code and the tests that accept it. The planner writes each
test's name and assertions (`skills/writing-plans/SKILL.md:180-201`, "What a Step Contains"). The implementer
then writes the tests and the code from them. So a misreading in the plan passes every test.

The test evidence is also self-reported. In subagent-driven-development (SDD), the implementer's report is the
evidence, and the task reviewer is told "Do not re-run the suite to confirm their report"
(`skills/subagent-driven-development/task-reviewer-prompt.md:150-162`). executing-plans already runs its tests
mechanically: `task-done` runs the command and writes the ledger line only when the command passes
(`skills/executing-plans/scripts/task-done`).

The owner wants independence in two places (D1):

- **In execution (finding 21).** The test result comes from a run that the implementer did not report.
- **In authorship (finding 24).** A reader other than the planner turns the spec into tests.

The owner's reason, in their words: "An agent writing both code (a function, class, etc.) and the tests that
accept that function are not independent." (D3)

### What a second reading can and cannot catch

This is the designer's assessment, given to the owner on 2026-11-08. Nobody has measured it here.

- **It catches transcription errors.** These are values that the spec states and the plan copied wrong: a bound,
  a unit, a default. A ruling on one of them can quote the spec.
- **It finds ambiguity, but it cannot resolve it.** A disagreement marks a place where the spec needs a
  decision. Agreement proves little.
- **It misses shared blind spots.** Where the spec says nothing, two readers tend to fill the gap the same way.
  In Knight and Leveson's 1986 experiment, separately written versions of one program failed on the same
  inputs far more often than independence predicts. Two models reading one spec are likely at least as
  correlated.
- **Only a different source of truth breaks the correlation.** The owner's worked examples would do it, but
  they almost never exist (D4). Domain checks do it where they exist, such as totals that must reconcile or
  parameter recovery.

So the plan measures the step before it changes any skill text (Verification).

## Goals, non-goals and anti-goals

**Goals.**

- In SDD, the controller runs each task's tests through a script before the task review. The task reviewer
  reads that run, not the implementer's claim (finding 21).
- Both executors use one script for that run (D6).
- At plan review, a second reader that never sees the plan's tests writes acceptance tests from the spec
  (finding 24, approach A, D6).
- An Opus subagent, the adjudicator, rules on each disagreement between the two readings (D3). It rules only
  when it can quote the spec sentence that decides the case. The owner gets the rest (D3, D6).
- Most unclear cases reach the owner at plan review, so a run seldom stops for one.
- During execution, the acceptance tests run through the same script, and a failure goes to the adjudicator.
- A planted-misread probe measures what the step catches, and how many false alarms it raises, before any
  skill text changes (D6, D8).

**Non-goals.**

- No new brainstorming step that asks the owner for worked examples (D4). When a spec states exact values or
  examples, the second reader uses them first.
- Finding 22 (spec drift). Its own session designs it (D2).
- Layer 4 of the backlog item: spec excerpts in the implementer brief, and DONE_WITH_CONCERNS on a conflict
  between a test and the spec. It stays open in the backlog item *(designer's call)*.
- Mutation testing. The backlog item rules it out, because it measures test strength, not correctness.
- A tester subagent for each task (approach B), or a check only at the end of the run (approach C).
- Any change to how prose and skill-text tasks are verified. Micro-tests keep that job *(designer's call)*.

**Anti-goals.** Each of these makes the design a failure, even if it works:

- The second reader sees the plan's tests or approach lines. Its reading is then a copy of the planner's.
- The adjudicator rules on what the code must do without quoting the requirement text that decides it. An
  agent then picks a reading that the owner never chose.
- The step adds a stop to every run, or a ruling for the owner on every task.
- An executor edits an acceptance test to match the code without a recorded ruling.
- A Codex run sends a project's spec to OpenAI without the owner's approval for that project.

## Approaches

The approaches differ in when the second reader writes its tests. All three share four parts, and the owner
accepted them with approach A (D6):

- the shared test-run script
- the adjudicator's quote-the-spec rule
- Codex as the second reader where the repository allows it, and a fresh Claude subagent elsewhere
- the probe, before any skill text changes

| | A. At plan review (chosen) | B. After each task | C. At the end of the run |
|---|---|---|---|
| The second reader writes tests | once, before any code | for each task, after DONE | once, before the final review |
| It writes them against | the Interfaces blocks | the real code | the real code |
| A misreading shows up | before any code depends on it | after its task | after every task is built |
| Unclear cases reach the owner | at plan review | during the run: a new stop, or parked while later tasks build on the reading | at the completion gate |
| Works in | both executors | SDD only (inline execution has no per-task subagents) | both executors |
| Extra passes | 1 per plan | 1 per task | 1 per plan |
| Main edit | writing-plans (6 characters of room) | SDD's `SKILL.md` (591 characters of room) | both executors' `final-review.md` |

- **A** writes tests before the code exists, so some tests fail on interface details, not on meaning. The
  adjudicator corrects those against the Interfaces block.
- **B** gives the fastest feedback, but costs one more subagent per task. Its tester also reads the brief's
  Interfaces block, which the planner wrote.
- **C** is the cheapest to build. But a misreading in Task 1 then costs every task built on it, and the final
  code-reviewer already reads the spec (plan 73).

Three ideas were dropped:

- **A second implementation used as an oracle.** It costs a second build, and Knight and Leveson's result
  applies to it directly.
- **A check of each plan assertion against a quoted spec sentence.** It writes no independent tests, and the
  backlog item rules out new reviewers that start from the plan.
- **The owner's worked examples as the anchor.** They almost never exist (D4).

**The pick: A (D6).** It puts the second reading where the plan's tests are written. A misreading is fixed in
the plan before any code depends on it. Most unclear cases reach the owner at plan review, where the owner is
already present. The cost is the writing-plans references split, which finding 17 already calls for.

## Owner decisions (2026-11-08)

- **D1. Both kinds of independence matter.** "The way I read it, finding 21 applies to both executing-plans
  and subagent-driven-development and finding 24 applies to writing-plans. The first gives independence during
  execution, the second independence during authorship. I think both of these are important."
- **D2. Finding 22 goes to its own session.** "Can we open this part of the session (spec drift, finding 22)
  in a separate session? That way we can proceed with the finding 21 and 24 question separately."
- **D3. An Opus subagent rules, and the owner gets the unclear cases.** "I am not sure anything would. An agent
  writing both code (a function, class, etc.) and the tests that accept that function are not independent.
  Could not the agent driving subagent-driven-development make the ruling on the disagreement and only raise it
  when it is unclear? That said, you'd probably want to launch a third subagent to rule on whether the code and
  tests agree, rule on it, and then pass it on to me if need be. This is because the main agent usually runs on
  Sonnet and it may need an Opus subagent to make the ruling." This replaces the backlog item's rule "no agent
  resolves a disagreement between two readings. Only the owner does." (`specs/deferred_items.md:5334`).
- **D4. Worked examples are rare.** "In practice, almost never. Brainstorming does not ask for these. In theory,
  I could provide these in some limited cases."
- **D5. The playback stands.** "Nothing is missing, lay out the approaches."
- **D6. Approach A.** "Go with A." The approaches message showed the four shared parts with it.
- **D7. A cheaper Codex model.** "It would be nice to use a less capable (and expensive model). We should see if
  Sol 6 works." Reading: the Codex reader uses the cheapest model that meets the probe's bars, and the probe
  tries Sol 6 first. Sol 6's ID is `gpt-6-sol`, and its catalog entry reads "Previous generation workhorse
  model." The repository records no prices, so "cheaper" is the owner's description, not a measurement. The
  owner said this after reporting that Codex's default model, Sol 6.1, fails. A check on 2026-11-08 found that
  it does not fail (Constraints, "Codex model").
- **D8. The probe is its own plan, first.** "yes, run the probe as its own plan first." The owner answered the
  question whether to review the probe's results before anything else is built. The build plan is written
  after that review.

## Design

### 1. The test-run script (finding 21)

- A new script in `skills/subagent-driven-development/scripts/` runs one test command. It saves the exit status
  and the full output in the plan's `.sdd/<plan>/` workspace, one file per task and per run. It prints the tail
  and the file's path. It uses the commit guard that finding 18's helper fixes add to `task-start` and
  `task-done`.
- **SDD.** After the implementer reports DONE, the controller runs the task's tests through the script before
  it writes the review package. The tests are the task's own test commands, plus the acceptance tests that
  the task makes runnable (part 5).
- **A failing run.** The task goes back to the implementer as a fix round, before any review
  *(designer's call)*. The round counts toward the five-attempt cap (`references/fix-loop.md`).
- **The task reviewer.** It reads the run file. A mismatch between the run and the implementer's report is a
  finding. "Do not re-run the suite" stays, because the run now exists. The `## Tests` sections of
  `task-reviewer-prompt.md` (`:150`) and `agents/task-reviewer.md` (`:74`) change together. So does the
  "Constructing Reviewer Prompts" bullet in SDD's `SKILL.md` (`:226`).
- **executing-plans.** `task-done` calls the script for its run. Its ledger behavior does not change.

### 2. The second reader (finding 24)

- **When.** After the planner's Self-Review, before the owner's plan review (`skills/writing-plans/SKILL.md`,
  Self-Review at `:208` and Plan review at `:233`).
- **Who.** Codex where the session has the owner's approval, by the same gate as
  `skills/requesting-code-review/codex-review.md` ("Approval first", `:9`). Elsewhere, a fresh Claude
  subagent at SDD's capable tier. Codex already runs at both executors' final reviews. The Codex run uses the
  cheapest model that meets the probe's bars (D7).
- **The requirement text** *(designer's call)*: the text that the plan's `**Spec:**` line names. That is
  usually a spec. It can also be the backlog items or the brief that a plan with no spec names as its
  requirements (`skills/writing-plans/SKILL.md:99`). A plan whose `**Spec:**` line names no requirement text
  skips the step, and the plan review message says so.
- **Inputs** *(designer's call)*: the requirement text, the plan's Tech Stack line, and each task's Files list
  and Interfaces block. The reader uses the Interfaces blocks for names, paths and types only. It takes every
  value from the requirement text, and it flags each plan value that differs from it. The reader never gets
  the Global Constraints, the task steps, the test code, the approach lines, the Review Focus section or the
  Decisions section. The planner wrote all of those, and the Global Constraints repeat the spec's values in
  the planner's copy (`skills/writing-plans/SKILL.md:103-106`).
- **Isolation** *(designer's call)*: the planner copies the inputs into a scratch directory outside the
  checkout. The prompt names no plan path, and it tells the reader not to search for one.
- **Output.** Acceptance tests in the project's test framework. Each test names the spec sentence that it
  checks, and the task whose Produces it needs. The reader also lists the spec sentences that it could not turn
  into a test.
- **Where the tests live** *(designer's call)*: in a committed path beside the plan, outside every task body.
  `task-brief` never copies them into a brief, and no executor points the implementer at them. Hidden tests can
  catch code that was written to pass visible ones. A fresh execution session can read only committed files.
- **Scope** *(designer's call)*: only tasks with executable test steps. A plan with none skips the step, and
  the plan review message says so.

### 3. The adjudicator

- A read-only subagent, pinned to Opus, in a new agent file in `agents/` *(designer's call)*. Like
  `agents/code-reviewer.md`, it falls under `hooks/readonly-agent-guard.py` and
  `hooks/dispatch-model-guard.py`.
- **Its rule (D3, D6).** Each case gets one ruling: the plan or code is wrong, the acceptance test is wrong, or
  the case is unclear. Every ruling except "unclear" quotes the binding text that decides it. No deciding
  text means "unclear".
- **The binding text** *(designer's call)*. For what the code must do, the binding text is the requirement
  text. For names, paths and types, it is the task's Interfaces block, when the behavior under test does not
  change. So an acceptance test that fails only on an import path or a parameter name is corrected to match
  the Interfaces block. No owner ruling is needed. The quote rule comes from D3's "only raise it when it is
  unclear". A name that the plan fixes is not unclear.
- It never edits a file. The planner applies its plan-time rulings, and the controller applies its run-time
  rulings.

### 4. At plan review

- The adjudicator reads both test sets for each task against the spec, and rules on each conflict.
- **The plan is wrong.** The planner corrects the plan's assertion.
- **The acceptance test is wrong.** The planner fixes or drops the acceptance test.
- The planner records each of those rulings in a new `## Acceptance` section of the plan: the spec sentence,
  both assertions and the ruling *(designer's call)*. `## Decisions` keeps only the owner's decisions.
- **Unclear.** The case goes to the owner in the plan review message, first in the list. The owner's answer is a
  decision, routed as writing-plans already routes one (`skills/writing-plans/SKILL.md:238-246`): a plan-level
  one into `## Decisions`, and a spec-level one into a spec-amendment task.

### 5. During execution

- Each acceptance test runs in the script's run for the task that makes it runnable. The whole set runs once
  more before the final review *(designer's call)*. In executing-plans, the same tests go into `task-done`'s
  command.
- A failing acceptance test goes to the adjudicator:
  - **The code is wrong.** The controller records a fix-loop finding for that task, under the usual cap.
  - **The acceptance test is wrong.** The controller corrects or drops the test, and ledgers a `Ruling:` line.
  - **Unclear.** The controller ledgers a `Ruling:` line marked for the owner, and keeps going unless one of the
    five stops applies *(designer's call)*. It sets the test aside: later runs leave the test out, and the
    ledger line names it. Otherwise the test would fail every later run, and `task-done` records a task only
    when its command passes. The completion gate shows the case with the final review's Declined to judge
    lines, for the owner to rule on (`skills/subagent-driven-development/references/final-review.md:29`,
    `skills/executing-plans/references/final-review.md:71`).
- No executor edits or sets aside an acceptance test without a ledgered ruling.
- The history record from finding 22 keeps each `Ruling:` line that changed the build
  (`specs/development-history-record.md`, merged in `4d69454`). The adjudicator's rulings are ordinary ledger
  lines, so they need no extra step.
- At plan completion, the reconciled acceptance tests join the project's test suite, so they keep guarding the
  behavior *(designer's call)*.

### 6. Model tiers

- The second reader: Codex, or a Claude subagent at the capable tier.
- The adjudicator: its Opus pin (D3).
- Every dispatch names its model (`skills/subagent-driven-development/SKILL.md:159-166`).

## Verification

### Probe first

The backlog item's probe runs as its own plan, before the build plan and before any skill text changes (D8).
The owner reviews its results. The build plan is written only after that review.

1. Take two or three completed spec-and-plan pairs from `specs/completed/` and `specs/plans/completed/`. Each
   needs code tasks and exact values in its spec.
2. In copies of the plans, plant the backlog item's three misreads: an inclusive bound made exclusive, a wrong
   unit and a wrong default. Plant each one everywhere the plan states that value: the Global Constraints,
   the Interfaces blocks, the test steps and the code steps *(designer's call)*. A misread that appears only
   in the test steps never reaches the reader, so it would overstate the catch rate. Keep one plan unchanged,
   to count false alarms.
3. Run the control arm: the current Self-Review checklist, run by a fresh planner session against the spec.
4. Run the treatment arms: the second reader and the adjudicator, with a Claude reader and with Codex. The
   Codex arm runs `gpt-6-sol` first (D7). It runs the config default, `gpt-6.1-sol`, only when `gpt-6-sol`
   misses a bar *(designer's call)*. Codex is not installed in cloud sessions, so the Codex arms run where the
   owner's `codex` CLI is logged in.
5. For each arm, count three things: planted misreads caught, false alarms and unclear cases. A catch means
   that the adjudicator rules the plan wrong and quotes the right sentence. A false alarm is a ruling against a
   correct assertion.

**Proposed bars** *(designer's call)*: a treatment arm catches each planted misread in at least 4 of 5
repetitions. The control catches it in at most 2 of 5. A treatment arm raises at most one false alarm and at
most one unclear case per plan. These bars replace the backlog item's looser rule, "keep only the layers that
catch something". The Codex arm stays only if it beats the Claude arm on catches or on false alarms. The owner
reviews the results against these bars, and decides what the build plan keeps (D8).

**Whatever the probe shows, finding 21's half ships.** The test-run script, the task-reviewer change and the
`task-done` change do not depend on the second reader. The approaches message said so: "The script is useful
on its own, so it lands first."

The results go to `specs/red-baseline-acceptance-tests.md`, linked from this spec *(designer's call)*. The
probe plan's completion adds a progress note to the backlog item that points at that file.

Results: `specs/red-baseline-acceptance-tests.md` (plan 81, 2026-11-08).

### Micro-tests

The wording changes shape agent behavior. So each one gets a micro-test against a no-guidance control, with the
repository's isolated kit, as writing-skills requires. The behaviors to test:

- The planner runs the second reader after Self-Review, and gives it only the allowed inputs.
- The planner sends unclear cases to the owner, and records the other rulings in `## Acceptance`.
- The SDD controller runs the script before the task review, and the task reviewer reads the run file.
- The controller sends a failing acceptance test to the adjudicator, and never edits the test without a ruling.
- The adjudicator quotes the binding text, and it rules "unclear" when no text decides the case.
- After an unclear ruling during a run, the controller ledgers it, sets the test aside and keeps going.

### Script tests

The new script gets pytest cases in `skills/subagent-driven-development/scripts/`, whose suite
`build/suites.toml` already registers. `task-done`'s tests keep passing.

## Constraints

- **Order (D8).** The probe plan comes first. It needs neither finding 18's helper fixes nor the writing-plans
  split, so it can run now. The build plan comes after three things: the owner's review of the probe, finding
  18's helper plan and the writing-plans references split. The split runs as its own plan without a spec, as
  plans 71 and 72 did *(designer's call)*. If the owner drops the acceptance step after the probe, the build
  plan is finding 21's half alone, and it needs no split.
- **Room.** On 2026-11-08 at `e0a360a`, the skill bodies have this much room under the compaction check:
  writing-plans 6 characters, SDD 591 and executing-plans 3,616 (finding 17's measure). New text goes to
  `references/` files, with a pointer at each step that needs it.
- **The history record plan.** Finding 22's design, `specs/development-history-record.md`, is approved and on
  `main` (`4d69454`, lowmason/agent-skills#148). Its session reported on 2026-11-08 that plan 80 is being
  written for it. Plan 80 edits `skills/writing-plans/SKILL.md` (one pointer line in protocol step 5, plus an
  equal cut) and the gate paragraph of both executors' `references/final-review.md`. This design edits the
  same gate paragraph. Plan 80 will likely land first. So this plan measures the room again and takes its line
  numbers from `main` at that time. The writing-plans split must not cut or move the text that plan 80 cuts.
- **Reviewer surfaces.** The two `## Tests` sections sit outside the shared reviewer block that
  `build/check_reviewer_block.py` checks. A new agent file needs `build/sync_runtime_assets.py`, then its
  `--check`.
- **Dependencies.** Each new cross-skill path goes into `install.py`'s `DEPENDENCIES`, or into
  `build/test_runtime_support.py`'s `SOFT_REFERENCES` with a reason.
- **Codex data.** A Codex run sends the spec, the Interfaces blocks and every file it reads to OpenAI. This
  repository's CLAUDE.md approves "Codex second-opinion reviews" only (`CLAUDE.md:54`). So a Codex acceptance
  run asks once per session until the owner extends that line *(designer's call)*.
- **Codex model.** A check on 2026-11-08, with codex-cli 0.163.0 and the owner's ChatGPT login, found that
  `gpt-6-sol`, `gpt-6-astra` and `gpt-6.1-sol` all run. Seven real Codex reviews on 2026-11-06 and 2026-11-07
  ran on `gpt-6.1-sol` with no override. The rejection that plan 69 recorded (codex-cli 0.154.0,
  `specs/plans/completed/69-agent-payload-probe.md:63`, D5) had stopped by 2026-10-29. The fall-back to Astra
  6 that the owner described came from a stale memory entry. Commit `2f35f81` adds `-m gpt-6-sol` to the
  launch command in `skills/requesting-code-review/codex-review.md`. It reached `main` through
  lowmason/agent-skills#149 (`f0a9f89`). A fresh-session proof on 2026-11-08 passed. A `claude -p` session
  with auto memory off ran the recipe once, with `--base 4d69454`. Codex exited 0, and its log header read
  `model: gpt-6-sol`, with effort `ultra`. The `claude -p` session waited for the background Codex run only
  after `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` was raised. A probe arm that runs Codex through `claude -p`
  probably needs the same setting. A Codex acceptance run names its model with `-m` in
  the same way, and the probe records the model of each Codex run. This design does not change the review
  recipe.
- **Lints.** `build/run_commit_lints.sh` passes before each commit.

## Provenance

- The test-run script adapts `skills/executing-plans/scripts/task-done`, which adapts upstream superpowers'
  scripts (MIT, `LICENSE-superpowers`). NOTICE gets a change-list line in the superpowers section.
- The acceptance step, the adjudicator, its quote-the-spec rule and the hidden acceptance tests are this
  repository's own work, in skills adapted from superpowers. NOTICE records them as local changes.
- Knight and Leveson (1986) is cited for an idea only.
- No text or fixture comes from `prime-radiant-inc/superpowers-evals`, which carries no license.

## Closing the backlog and the drift spec

When the build plan completes, the plan-completion protocol does these things:

- It ticks the backlog item "Spec-reading test check" (section `spec-reading-test-check`,
  `specs/deferred_items.md:5306`). The closing note says three things *(designer's call)*:
  - Layers 3 and 5 and finding 21's run landed.
  - Layer 1 applies only when a spec has examples (D4).
  - Layer 4 stays open as a new item.
- It updates findings 21 and 24, and their bullets under "Suggested disposition", in
  `specs/superpowers-drift-spec-v7-0-2.md`, from the file as it stands on `main` at that time.
- It retires this spec with the plan.

## Designer's calls

These were not discussed with the owner:

1. **Hidden acceptance tests, in a committed path beside the plan.** Hidden tests can catch code that was
   written to pass visible ones, and a fresh session reads only committed files.
2. **The second reader's inputs.** It gets the requirement text, the Tech Stack line, the Files lists and the
   Interfaces blocks, and it takes every value from the requirement text. It needs module paths to write
   runnable tests, but not the planner's reading. The Global Constraints are left out, because they repeat the
   spec's values in the planner's copy.
3. **No Review Focus for the second reader.** The planner wrote it.
4. **Isolation in a scratch directory, with no plan path.** A reader that can find the plan can read its
   tests.
5. **A new `## Acceptance` plan section.** `## Decisions` holds the owner's decisions only.
6. **Run timing.** Each acceptance test runs with the task that makes it runnable, and the whole set runs
   before the final review.
7. **An unclear case during a run is ledgered, and the run continues.** This matches the rulings-not-stalls
   rule and the path that Declined to judge lines already take.
8. **A failing controller run goes back to the implementer** before any review.
9. **Code tasks only.** Prose and skill-text tasks keep their micro-tests.
10. **The acceptance tests join the project's suite** at plan completion.
11. **A separate Codex approval** until the owner extends `CLAUDE.md:54`.
12. **The probe bars, and where the results go.** The backlog item's closure condition asks the spec to record
    the probe results. This design has the probe plan record them instead, in the red-baseline file.
13. **Layer 4 stays open** in the backlog.
14. **The adjudicator as an agent file pinned to Opus,** so the existing guards cover it.
15. **The writing-plans split as its own plan,** before this one.
16. **The Interfaces block is the binding text for names, paths and types.** An acceptance test that fails only
    on a name is corrected without an owner ruling.
17. **An unclear test is set aside** until the owner rules at the completion gate.
18. **A plan with no spec uses the requirement text that its `**Spec:**` line names,** and it skips the step
    when that line names none.
19. **The probe plants each misread everywhere the plan states the value.**
20. **A bar of at most one unclear case per plan.** The bars replace the backlog item's keep rule.
21. **The Codex arms run `gpt-6-sol` first,** and the config default, `gpt-6.1-sol`, only when `gpt-6-sol`
    misses a bar.

## Left to the builder

- The script's name, flags and output format.
- The acceptance tests' path and file layout.
- The exact format of the `## Acceptance` section.
- The adjudicator's agent name and prompt text.
- The Codex command and its sandbox options. The command names its model with `-m`, as the review recipe does
  after `2f35f81`.
- How the task that makes a test runnable is found from the Produces lines.
- The micro-test cases and their bars.
