# Branch explainer — Design Spec

**Status: APPROVED (2026-11-13)** — the owner approved it on 2026-11-13, after brainstorming and a builder
check. The next step is writing-plans, in a fresh session on branch
`claude/branch-explainer-pre-merge-fde7f8`.

## What this builds

A new step in finishing-a-development-branch writes an explainer of the finished branch for the owner. The
explainer covers `BASE..HEAD` and lets the owner give a synopsis in three parts: what the plan set out to
do, how it was built, and what it adds to the project. The step runs before the Step 4 menu. Nothing waits
on the owner's answers.

The change has four parts:

1. **A baseline probe, before the build.** It shows what an agent with no guidance writes today, scored
   against the owner's bar. See Baseline probe.
2. **Step 3b in `skills/finishing-a-development-branch/SKILL.md`.** It dispatches a fresh subagent on each
   plan branch, and gives the owner the explainer's path before the menu.
3. **A prompt file**, `skills/finishing-a-development-branch/references/branch-explainer-prompt.md`
   **(my call on the name)**. It holds the subagent's instructions: inputs, layout, length and style.
4. **A `NOTICE` entry** that credits the two sources by idea only.

## Why

In the owner's words: "Every review seat today (task-reviewer, code-reviewer, Codex) verifies the work.
None of them builds the owner's mental model of it."

- **Every seat checks correctness.** task-reviewer checks each task against its brief. code-reviewer and
  Codex check the whole branch. None of them teaches the owner the change.
- **The owner's last moment with a branch is the Step 4 pick.** Under the Copilot loop spec
  (`specs/copilot-pr-review-loop.md` on branch `claude/copilot-pr-review-merge-e5714d`, approved
  2026-11-12), the agent merges an Option 2 PR with no owner action. Option 1 is agent-run already. So the
  explainer must come before the menu, or it comes too late.
- **`specs/history.md` is a record, not an explainer.** It lists each plan's rulings and deviations for
  later reference. It does not walk the owner through the change.

The idea comes from Eric J. Ma's post "The understanding zeitgeist in AI code review"
(<https://ericmjl.github.io/blog/2026/7/24/understanding-zeitgeist-ai-code-review/>) and Geoffrey Litt's
`explain-diff` skill (<https://gist.github.com/geoffreylitt/a29df1b5f9865506e8952488eac3d524>). This
design takes ideas from both and copies no text (see Constraints, Provenance).

## Decisions taken in brainstorming

The owner decided these on 2026-11-12:

1. **The questions are a self-check, not a gate.** They do not bind Option 1 or Option 2, unlike the
   aged-tail gate. The Step 4 menu works as it does today.
2. **The bar.** After reading, the owner can give "a synopsis of the plan, how it was implemented, what it
   adds to the overall project."
3. **Approach 1:** a step in finishing, written by a fresh subagent (see Approaches considered).
4. **Out of scope:** another verification seat, and any change to the reviewers.
5. **A baseline probe runs before the build.**
6. **The probe's reader does not see the treatment's synopsis.** The scores must show whether the body
   teaches, not whether the reader can copy a summary.
7. **A fourth branch is held out.** It is scored once, on the final prompt, so the probe shows whether the
   prompt was fitted to the three tuning branches.

The owner decided 6 and 7 after the builder check. The owner saw and accepted a playback of the layout, the inputs, the run rule, the anti-goals and the probe
shape. Those parts are still marked **(my call)** below, because the owner did not choose them. The owner
can overturn any call marked that way.

## Approaches considered

1. **A step in finishing, written by a fresh subagent** — chosen. It runs without the owner having to
   remember it. The writer sees only the files, as the owner would, so it cannot present remembered intent
   as what the code does. It costs one subagent run per plan branch, about a code-reviewer pass in reading.
   It edits the same file as the Copilot loop plan.
2. **The same step, written by the finishing session itself.** It is cheaper and faster. But after
   subagent-driven-development the finishing session never wrote the code. It read implementer reports,
   and its context may be compacted. It would explain the build from second-hand memory.
3. **A manual `/explain-branch` command.** It does not collide with the Copilot loop, and it works on any
   range. But it depends on the owner remembering it, so it is not a step. Codex has no command adapter in
   this repo.

Three options were dropped:

- **A model-invocable skill** costs a listing slot, and finishing would be its only caller.
- **Folding the explainer into the history entry** would put an owner-only text into a committed public
  record.
- **The PR body** comes too late. Option 1 has no PR, and the menu comes before any PR exists.

## Goals, non-goals and anti-goals

**Goals**

- After reading the explainer, the owner can state the plan, the build and what the branch adds to the
  project, in their own words.
- The explainer runs on every plan branch with no owner action.
- The baseline probe shows how the new prompt compares with no guidance, on the owner's bar.

**Non-goals**

- No new verification seat, and no change to task-reviewer, code-reviewer, Codex or the Copilot loop.
- No gate. The Step 4 menu, its wording and its "Don't add explanation" line stay as they are.
- No change to `specs/history.md` or to the Plan Completion Protocol.
- No explainers for other people's PRs, and no HTML or notebook output.

**Anti-goals** (a failure even if the step runs) **(my call)**

- **An explainer that only restates the spec.** The owner approved the spec, so a restatement teaches
  nothing.
- **An explainer too long to read before the pick.**
- **An explainer that says the code does something it does not.**

## Current state (main `af378ac`, 2026-11-12)

- **Finishing's order.** Step 1 (tests), Step 1b (deferred backlog), Step 2 (environment), Step 3 (base
  branch), Step 4 (menu), Step 4b (Codex review, for merge and PR only), Step 5 (execute), Step 6
  (cleanup). Step 4 says "**Don't add explanation** - keep options concise."
- **Finishing dispatches no general-purpose subagent today.** Step 4b runs Codex through
  `requesting-code-review/codex-review.md` and may offer a code-reviewer pass.
- **The plan artifacts exist at finish time.** The Plan Completion Protocol
  (`skills/writing-plans/SKILL.md`, § Plan Completion Protocol) runs before finishing. Its step 5 moves the
  plan to `specs/plans/completed/` and appends a history entry to `specs/history.md` in the same commit.
  Each entry's second line names the plan path and the spec path, for example
  `Plan: specs/plans/completed/80-development-history-record.md · Spec: specs/completed/development-history-record.md (retired)`.
- **The compaction window.** `build/cc_guide/conformance.toml` sets the window for a skill body at
  19,700 characters. Finishing's body is 19,009 characters, so about 690 are left. The Copilot loop spec
  needs some of that room too (its Constraints, "Compaction window").
- **The listing.** Neither a reference file nor a prompt file adds to the skill listing.

## Design

### 1. Where the step goes

Step 3b, "Explain the branch", sits after Step 3 and before Step 4. Step 3 gives the base branch. After a
`git fetch`, `BASE` is `git merge-base origin/<base-branch> HEAD`. With no remote, it is
`git merge-base <base-branch> HEAD`. Step 4 and every later step stay as they are.

The remote-tracking base matters **(my call)**. A branch that merged `origin/main` while the local `main`
fell behind would otherwise count other PRs' commits in `BASE..HEAD`. Most PRs in this repo retire a plan,
so the plan-branch rule would fire on their plans, and the explainer would cover their work. Step 4b's
`--base` has the same weakness today. This spec does not change Step 4b.

### 2. Which branches

- **A plan branch** gets the explainer with no question asked. A branch is a plan branch when
  `BASE..HEAD` adds or renames a file under `specs/plans/completed/`. The Plan Completion Protocol always
  does that before finishing **(my call: the rule reads the diff, not the conversation, so it holds after a
  `/clear` or a compaction)**.
- **Any other branch** gets a one-line offer: the branch has no plan, and an explainer is available before
  the menu. On a yes, the step runs with the diff, the commit log and the project map as its only inputs.
- **The owner can skip it.** If the owner says to skip the explainer, the step does nothing.

The diff size does not matter **(my call: a small plan can still change how a whole flow works)**.

### 3. The writer

- Finishing dispatches a fresh general-purpose subagent with the prompt file and the values it needs:
  `BASE`, `HEAD`, the branch name, the repo root and the output path.
- The dispatch passes `model: opus` **(my call: this is a whole-branch reading task, like the final
  reviewer, which is pinned to Opus)**. The probe runs on the same model.
- The subagent writes the file and returns only its path and its word count **(my call: this keeps the
  explainer out of the finishing session's context, which is often near its limit at this point)**.
- Finishing waits for the subagent, then gives the owner the path in one line, then shows the menu
  **(my call: the point is to read before the pick)**.
- Without a subagent tool, the finishing session writes the explainer itself from the same prompt file.

### 4. Inputs

The prompt file tells the subagent to read these:

- **The diff `BASE..HEAD` and its commit log.** The diff is the truth for what changed.
- **The history entry that the branch adds to `specs/history.md`.** It lists the calls the build made
  without the owner: its rulings and deviations. Its second line names the plan and the spec.
- **The plan and the spec**, for the background and the intent. If the history entry reads `Spec: none`,
  the plan alone gives the intent.
- **The project map**, for the third part of the synopsis: the README, `CLAUDE.md` or `AGENTS.md`, any live
  `specs/*-roadmap.md`, and earlier entries in `specs/history.md`.
- **The code around the change**, as far as the explanation needs it.

Where the diff and the spec differ, the explainer says so and cites the history entry's ruling or deviation
**(my call: the spec says what was meant, and only the diff says what was done)**.

### 5. The explainer's layout **(my call)**

1. **Synopsis**, at most 250 words, on one screen. It has three labeled parts:
   - **The plan:** what it set out to do, and why.
   - **The build:** how it was implemented, in the order the parts depend on each other.
   - **The project:** what the branch adds to the whole.
2. **Background.** The parts of the project that the change touches, as they worked before the branch. It
   is narrow, with no tutorial for beginners, because the owner wrote the project. (Litt's deep background
   is for teammates.)
3. **The change, in dependency order.** Each part has prose around it: what it is, why it is there, and what
   depends on it. Each claim about code names the file, and the line where it helps, so the owner can check
   it.
4. **What it adds to the project.** How the project's flows or abilities change, which other parts now
   depend on the branch, and what it leaves for later (the deferred items it adds).
5. **Questions.** Three, one for each synopsis part: what did the plan set out to do, and why? How was it
   built? What does it add to the project? The owner answers in their own words, then compares with the
   synopsis at the top. Nothing records the answers.

The whole explainer is at most 2,000 words, about ten minutes of reading. It is Markdown. It is written in
plain technical English, as the repo's always-on writing rule asks for documents written for people. The
prompt file says this in its own words and names no skill.

### 6. The output file

- The path is `~/.cache/branch-explainers/<repo-name>/<YYYY-MM-DD>-<branch-slug>.md` **(my call: it is
  outside every repo, never committed, and kept across reboots)**.
- Finishing gives the owner the path. Where the runtime can show a file to the owner, it does that too.
- A re-run on the same day overwrites the file.

### 7. What stays the same

- The Step 4 menu and its wording.
- The aged-tail gate (Step 1b) and the Codex review (Step 4b).
- Option 3 (keep the branch) is always open, so the owner can stop after reading.
- The explainer covers `HEAD` at Step 3b. Fixes that Step 4b makes later do not re-run it. Step 4b already
  shows the owner what it changed or left **(my call)**.

## Baseline probe

The probe runs before the build. It answers one question: does an agent with no guidance already write an
explainer that meets the owner's bar? If it does, the prompt file shrinks to the inputs and the layout,
and the step's value is only that it runs.

**Fixtures.** Three merged plan branches, each with a spec, a plan and a history entry **(my call, and the
builder confirms each)**:

| Plan | Kind of change | Merge | Head | `BASE` |
|------|----------------|-------|------|--------|
| `80-development-history-record` | a script plus skill text | `ca3404f` | `325330a` | `4d69454` |
| `90-readonly-guard-command-starts` | hook code plus tests | `d686779` | `d51bf64` | `84efc99` |
| `92-writing-skills-guide-rewrite` | mostly skill text | `d58980b` | `0b6d34f` | `e382493` |

Each fixture is a detached worktree at the branch head before the merge, with `BASE` at its merge base.
The repo merges PRs with merge commits, so the head is the merge commit's second parent. The builder check
found that each range adds or renames a plan under `specs/plans/completed/` and adds a history entry.

**The held-out fixture** (owner's decision 7). The builder picks a fourth merged plan branch with a spec, a
plan and a history entry, of a different kind from the three above. The builder records it in the kit before
the first treatment run. No tuning round reads it. It is scored once, on the final prompt, in the treatment
arm only, with three reps.

**Arms.**

- **Control:** a fresh Opus agent with repo access gets only this request: "Explain the change in
  `<BASE>..HEAD` of this repository to me, its owner, before I merge it. Write it to `<path>`."
- **Treatment:** the same agent with the new prompt file.
- Three reps per arm on each fixture.

**Scoring.**

- **A reader** is a fresh agent with no tools. It sees only the explainer and writes the three-part
  synopsis. In the treatment arm, the kit removes the explainer's Synopsis section before the reader sees
  it (owner's decision 6). A control explainer keeps any summary it has. That tilts the test toward the
  control, which is the safe direction.
- **An adjudicator** is a fresh agent that sees the spec, the plan, the history entry, the diff, the
  explainer and the reader's synopsis. It scores five bars:
  - **B1 Plan.** The reader's first part states the plan's goal and its reason, and agrees with the spec.
  - **B2 Build.** The second part names the main parts of the build in an order that fits their
    dependencies. It holds at least two facts that come from the diff and not from the spec (anti-goal 1).
  - **B3 Project.** The third part names at least one way the branch changes the project beyond the files
    it touches: a part that now depends on it, or a step of a flow that changes.
  - **B4 Accuracy.** The explainer, its Synopsis section included, makes no claim about what the code does
    that the diff contradicts (anti-goal 3). The adjudicator lists each such claim. In the treatment arm it
    also checks that each synopsis part agrees with the spec and the diff.
  - **B5 Length.** The synopsis is at most 250 words and the explainer at most 2,000 (anti-goal 2). A script
    counts the words.

**Pass rules** **(my call)**.

- **A bar holds on a fixture** when it holds in at least two of three reps. The same rule applies to both
  arms.
- **RED:** the control fails at least one bar on at least one fixture. The prompt file then targets the bars
  that the control failed.
- **Shrink:** the control holds every bar on every fixture. The record says so, and the prompt file shrinks
  as above. RED and Shrink cover every outcome.
- **Treatment passes:** every bar holds on the three tuning fixtures, and then on the held-out fixture.

**Wording rounds** **(my call)**. If the first treatment run fails, at most two wording rounds follow. The
plan states each round's estimated cost before the round runs. If the treatment still fails after the second
round, the work stops and the results go to the owner. The held-out fixture runs once, after the last round.
If it fails, the work stops and the results go to the owner. No round tunes against it.

**Isolation.** The reps follow the repo's micro-test practice: `env -i` with a minimal environment,
`--setting-sources ""` and no auto-memory. The reader runs with no tools.

**Record.** `specs/baseline/red-baseline-branch-explainer.md`, with its kit, prompts and runs in
`specs/baseline/red-baseline-branch-explainer/`.

**Cost.** The plan states an estimate before the first live run, and the owner confirms the spend
**(my call)**.

## Testing

- **The baseline probe** above, for the prompt file.
- **A wording micro-test for Step 3b**, as writing-skills asks for an edit to a process skill. On a plan
  branch fixture, the agent dispatches the explainer before the menu, gives the path in one line, and shows
  the menu unchanged. On a branch with no plan, it makes the one-line offer and dispatches nothing unasked.
  The builder sizes the test. Each behavior holds in at least four of five reps **(my call)**.
- **The commit lints**, through `build/run_commit_lints.sh`. They include the compaction-window check and
  the orphan-bundled-file check, which needs `SKILL.md` to name the prompt file.

## Constraints

- **Compaction window.** About 690 characters are left in finishing's body, and the Copilot loop plan needs
  some of them. Step 3b in `SKILL.md` is a short pointer, at most about 400 characters, and the procedure
  lives in the prompt file. If the two plans together pass the window, the plan that runs second moves
  existing text out of the body to a reference.
- **Sequencing with the Copilot loop plan.** Both plans edit finishing's `SKILL.md` and `NOTICE`. They
  execute one at a time, not at once. The plan that runs second re-reads both files at its base. The design
  needs no fixed order: Step 3b sits before the menu, and the Copilot loop sits inside Option 2.
- **Provenance.** Finishing is adapted from superpowers (MIT, `LICENSE-superpowers`). `NOTICE` gets a dated
  entry under that skill. It says that Step 3b adapts two ideas only: Litt's explain-diff gist (background,
  then intuition, then a code walk in a sensible order, then a quiz) and Ma's framing of understanding as
  the bottleneck. Neither the gist nor the post states a license, and no text comes from either source. The three-part
  synopsis, the recall questions, the plan-branch rule and the inputs are local. No license-file copies
  change.
- **Public repo.** The explainer file never enters a repo. The probe kit commits explainers of this repo's
  public branches only.
- **Cross-runtime.** Finishing installs for Claude, Codex and agy. Step 3b and the prompt file name no
  Claude-only tool, and Step 3b has the fallback for a runtime with no subagent tool.
- **Dependency drift.** The prompt file names no other skill by path or section. If the build adds such a
  reference, it goes into `install.py`'s `DEPENDENCIES` or `build/test_runtime_support.py`'s
  `SOFT_REFERENCES`.
- **Dispatch-model guard.** A hook refuses a general-purpose Agent call with no `model`, so the dispatch
  always passes one.
- **Conformance.** The edits follow the guide sections that `build/cc_guide/conformance.toml` maps to a
  skill. `check_conformance.py` passes before each commit.

## Done when

1. The baseline record and its kit are committed, with the control's result on all three fixtures.
2. Step 3b, the prompt file and the `NOTICE` entry are committed.
3. The treatment meets the pass rule on the three tuning fixtures and on the held-out fixture. Or the
   record shows that the control held every bar and the prompt file was shrunk. The shrunk prompt still
   runs once on the held-out fixture.
4. The Step 3b wording micro-test passes.
5. `build/run_commit_lints.sh` passes, with no compaction-window finding for finishing.
6. At plan completion, the marimo idea (see Not in this spec) is an item in `specs/deferred_items.md`.

## Left to the builder

- The exact wording of Step 3b and of the prompt file.
- The prompt file's final name and place.
- The adjudicator's rubric, beyond the five bars.
- The fixture check: each has a spec, a plan and a history entry, and its merge base is found correctly.
- How to keep finishing's body inside the window, if the Copilot loop plan lands first.
- Whether the subagent or the finishing session writes the file, if a write outside the working directory
  prompts for permission. The probe should show this.
- The branch-slug rule for the file name.
- Whether the Core principle line and the Quick Reference table mention Step 3b.
- The size of the wording micro-test.

## Not in this spec

- **marimo notebooks with controls**, for model changes in downstream repos. → deferred at plan completion,
  as an item in `specs/deferred_items.md`.
- HTML output, diagrams, and explainers for other people's PRs.
- A gate on the questions.
- Any change to the reviewers, the Copilot loop, `specs/history.md` or the Plan Completion Protocol.
