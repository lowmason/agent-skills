# claude/musing-dhawan-59a2d0: plan 84, controller test runs in subagent-driven development

## Synopsis

**The plan:** In subagent-driven development (SDD), a task's test evidence came only from the implementer's report, and the reviewer was told not to re-run the suite. Finding 21 of the drift spec names this gap. Plan 84 builds Design 1 of the acceptance-tests spec: a test result that the implementer did not report. Finding 24's parts stay out (D1), because plan 83 closed them.

**The build:** A micro-test kit first ran control arms against the old text. Then a new script, `test-run`, runs one test command and keeps each run in its own file with a header. `task-done` now runs its command through `test-run`, with its ledger line unchanged. The controller text runs `test-run` before every task review, and a failing run becomes a fix round. The task reviewer and the scoped re-review read the run file and compare it with the report. NOTICE lines, the drift-spec records and the spec's retirement close the plan.

**The project:** Every SDD task review now rests on a run that the controller made and saved. A mismatch between the run and the report is an Important finding. Failing runs stay on disk beside later runs. executing-plans shares the same run mechanism. One item is deferred: a killed run leaves no partial output.

## Background

Before the branch, the SDD controller went straight from an implementer's DONE to `review-package` and the task reviewer. The reviewer's Tests section in `agents/task-reviewer.md` and `task-reviewer-prompt.md` said the implementer "already ran the tests" and told it not to re-run the suite. So the report was the only test evidence. The implementer prompt said the same: "your report is the test evidence."

executing-plans was already mechanical. `skills/executing-plans/scripts/task-done` ran the command itself, streamed the output to `task-<N>-tests.log` in the workspace, and wrote the ledger line only on a pass. A second run overwrote that log.

The spec (`specs/completed/spec-derived-acceptance-tests.md`, Intent) states the owner's goal: independence in execution, where the test result comes from a run that the implementer did not report. Its other half, independence in authorship (finding 24), closed in plan 83 with no build plan. Plan 82 had already added the commit guard, `sdd-repo --with-commit`, that the new script uses (D2).

## The change

### 1. Micro-test kit and control arms

`specs/baseline/red-baseline-test-run/kit/` is copied from an earlier kit. It adds a `frame` key and an `agents/` framing branch to `build_prompts.py`. `cases.py` holds two cases set in an unrelated recipe-scaling repository. `controller-run` checks that the controller calls `test-run` before `review-package` or a reviewer dispatch. `reviewer-run` gives the reviewer a run file that shows `test_rounds_to_whole_ml` skipped, while the report claims `3 passed`. It checks that the reviewer grades the skip as Important.

The control arms ran at BASE before any text changed. `controller-run` scored 0 of 5 by construction, since `test-run` did not exist. `reviewer-run` scored 4 of 5, with one borderline failure. The record is `specs/baseline/red-baseline-test-run.md`. Tasks 4 and 5 depend on this kit for their treatment arms.

### 2. The `test-run` script

`skills/subagent-driven-development/scripts/test-run` is new (117 lines). Its usage is `test-run PLAN_FILE TASK_NUMBER -- TEST_COMMAND [ARGS...]`.

- It refuses a task number that is not an ID with exit 2, before it builds any path (lines 55-64).
- It calls `sdd-repo --with-commit` and `sdd-workspace` (lines 66-67).
- It takes HEAD and the tree state before the run. The tree check uses `git status --porcelain --untracked-files=normal` (line 80). The flag came from a review ruling: `status.showUntrackedFiles=no` would otherwise hide untracked files and print `tree: clean`.
- It runs the command once into a temporary file in the workspace. An EXIT trap removes that file (line 90).
- It picks the first free name: `task-<N>-tests.log` for run 1, then `task-<N>-tests-<K>.log` (lines 96-101). No run overwrites another.
- It writes six header lines (`test-run:`, `command:`, `head:`, `tree:`, `exit:`, `--- output ---`) and then the full output.
- It prints the last 5 lines, a newline guard (line 115), and `run: <path>` last. It exits with the command's status.

The entry's rulings changed the implementer's draft. A noclobber write and a `cannot write` exit were cut, because no spec line asked for them. The newline guard stayed. The Task 2 commit also edits the header comment of `scripts/sdd-workspace` to name `test-run`, outside the task's listed files, so that the `orphan-bundled-file` lint passes (ruling and deviation). Tests are in `scripts/test_sdd_scripts.py` (134 lines added, 2 removed). The entry records 23 tests added, not the plan's 21.

Everything after this point depends on the script and its run-file format.

### 3. `task-done` runs through `test-run`

`skills/executing-plans/scripts/task-done` drops its own render loop and its direct run. It calls `test-run` at line 101 and parses the `run:` line from its output. A missing `run:` line means a refusal, and `task-done` exits with that status. On failure, the message now names the run file. For the ledger line it reads the `command:` entry back from the run file, from line 2 up to `head:` (line 116). A Task 3 ruling made it read the whole entry, so a command with a newline in an argument keeps the ledger line byte for byte. The script keeps one rendering, in `test-run`.

The plan's constraint held: every test at BASE in `test_executing_plans_scripts.py` stays as it was. The file gains 45 lines, including a test for the multi-line command (deviation, Task 3). The first run still writes `task-<N>-tests.log`, which is why those tests pass unchanged.

### 4. The controller's text

`skills/subagent-driven-development/references/test-run.md` is new and holds the procedure, because the SKILL.md body has little room under the 20,000-character compaction window. Its bullets cover:

- The command: every passing `Run:` step that runs tests or checks, plus the project's documented test commands that the change can reach, in one call (line 11). Each command sits in its own parentheses, `sh -c '(<cmd1>) && (<cmd2>)'`, so that a `cd` does not leak. Final-review rulings C1 and C2 added the "tests or checks" limit and the parentheses. C1 narrows the owner-approved item 4. The entry flags it as a departure from that item's wording.
- A failing run goes back to the implementer as a fix round, before any review, and counts toward the five-attempt cap (line 13).
- No `run:` line (line 14): a refusal means a bad call to correct. A killed run is retried with a longer timeout, and a run that still does not finish is a failing run. Rulings R3 and the later "New Important" added and split this bullet.
- Check the run (line 15): read `head:` and `tree:` before the dispatch. A mismatch is the controller's own gap (ruling R2).
- A passing run hands the bare path to the reviewer. A task with no runnable command gets `none: <why>`. A batch gets one run.

The other SDD files point at it. `SKILL.md` adds a "Your test run passes?" diamond to the process graph and rewrites DONE to run the tests first. `fix-loop.md` makes a failing run start a round and requires a new run after every round. `file-handoffs.md` gives the reviewer four paths, not three. `handling-reports.md` applies the run to DONE_WITH_CONCERNS. `example-workflow.md` shows the run. `implementer-prompt.md` drops "your report is the test evidence" and says the controller runs the tests again before each review.

The treatment arm ran three times, each 5 of 5. The third run (`controller-run-3`) tested the shipped text after the final-review edits (deviation, Task 4).

### 5. The reviewer's text

`agents/task-reviewer.md` and `task-reviewer-prompt.md` get a new first Tests paragraph. The reviewer reads the run file and compares it with the report. A claimed test that the run does not show passing, a differing count, or an omitted skip or warning is an Important finding. A run at another commit or on a dirty tree is a gap for the controller. `none: <why>` leaves the report as the only evidence. "Do not re-run the suite" stays and now covers the run too. The prompt adds a `## The Controller's Test Run` section with `[RUN_FILE]` in both forms (lines 39-41 and 98-100).

`re-review-prompt.md` adds `<RUN_FILE>` with the same rules. The head, dirty-tree and `none:` clauses came from final-review ruling C3 + R1, because the scoped re-review sets the full contract aside. `runtimes/codex` and `runtimes/gemini` were regenerated. The shared reviewer block is untouched.

The treatment passed 5 of 5 against the control's 4 of 5. The owner kept the text (deviation, Task 5).

### 6. NOTICE, records and retirement

`NOTICE` gains a Plan 84 bullet after plan 86's bullet, not after plan 82's (ruling). A review rewrote it so that it credits the kept upstream wording and calls the exit line, header lines and per-run files local. The completion commits mark finding 21 adopted and done in `specs/superpowers-drift-spec-v7-0-2.md`. They move the spec to `specs/completed/` with a COMPLETE status line and re-point the live citations to it. They add the history entry with 12 rulings and 13 deviations. Three `fix(skills)` commits, one after the retirement, refine `test-run.md` after the final review.

## What it adds to the project

- **The SDD flow.** DONE now leads to a controller run, then the review package, then the reviewer. A failing run never reaches a reviewer. Every fix round ends with a new run, and the run files of a task accumulate in `.sdd/<plan>/`.
- **The reviewer's evidence.** The task reviewer and the re-review check the report against a saved run. A skip or a count that the report hides becomes an Important finding.
- **One run mechanism.** SDD's controller and executing-plans' `task-done` share `test-run`. A future change to the run-file format reaches both, and `task-done`'s ledger parsing depends on the `command:` and `--- output ---` lines.
- **Not changed.** `build/check_helper_paths.py` does not list `test-run` (approved item 8). Skill text still anchors it as `<this-skill-dir>/scripts/test-run`. No install dependency changed.
- **Deferred.** One item in `specs/deferred_items.md` under § 84-spec-derived-acceptance-tests. Because the EXIT trap removes the temporary file, a run that the Bash tool kills leaves no output. At BASE, `task-done` left partial output at `task-<N>-tests.log`. The proposed quick fix removes the file with an explicit `rm` after the write and names it in the "No `run:` line" bullet. The owner ruled defer at the completion gate.

## Questions

1. What did plan 84 set out to do, which finding does it close, and why does it leave out the rest of the acceptance-tests spec?
2. How do `test-run`, `task-done`, the controller's text and the reviewer's text depend on each other, and what does a failing or killed run do in the new flow?
3. What does the branch change in how an SDD task gets reviewed, what now depends on the run-file format, and what was deferred?
