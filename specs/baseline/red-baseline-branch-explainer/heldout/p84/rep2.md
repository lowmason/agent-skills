# claude/musing-dhawan-59a2d0: plan 84, controller test runs in subagent-driven development

## Synopsis

**The plan:** Plan 84 fixes finding 21 of `specs/superpowers-drift-spec-v7-0-2.md`, "Per-task test evidence is self-reported in SDD". Before the branch, the implementer's report was the only test evidence, and the task reviewer was told not to re-run the suite. The plan builds Design 1 of the acceptance-tests spec only (D1). The test result now comes from a run that the implementer did not report.

**The build:** A micro-test kit first ran control arms against the texts at BASE. A new script, `test-run`, runs one command and keeps each run in its own file in the plan's workspace, with a header that names the command, HEAD, the tree state and the exit status. `task-done` now runs its command through `test-run`. The SDD controller runs the task's tests through the script before each review, and a failing run becomes a fix round. The task reviewer and the re-review read the run file and compare it with the report. NOTICE lines and the plan's retirement close the branch.

**The project:** SDD gains test evidence that is independent of the implementer, and both executors share one run script. Every run stays on disk, so a failing run sits beside the run that follows its fix. Finding 21 is marked done, and the acceptance-tests spec retires. One item is deferred: a killed run leaves no partial output.

## Background

SDD's controller dispatched an implementer, took its DONE report, built the review package and dispatched the task reviewer. The reviewer's Tests section said "The implementer already ran the tests and reported results with TDD evidence for exactly this code. Do not re-run the suite to confirm their report." So a false or careless claim of passing tests reached the reviewer unchecked.

executing-plans already ran its tests mechanically. `skills/executing-plans/scripts/task-done` ran the command, wrote the output to `task-<N>-tests.log` and appended the ledger line only on a pass. A second run of the same task overwrote that log.

The spec (`specs/completed/spec-derived-acceptance-tests.md`) covers two findings. Finding 21 wants independence in execution. Finding 24 wants a second reader to write tests from the spec. Plan 83 closed finding 24's designs with no build plan, so plan 84 builds Design 1 alone and drops its clause on acceptance tests (D1). Plan 82's `sdd-repo --with-commit` supplies the commit guard that Design 1 asks for (D2).

## The change

### 1. Micro-test kit and control arms

`specs/baseline/red-baseline-test-run/kit/` holds `build_prompts.py`, `cases.py`, `run_reps.sh`, `show_reps.py` and an isolation probe. Two additive cases exist. `controller-run` checks that the controller calls `test-run` before `review-package`. `reviewer-run` checks that the reviewer grades a skipped test in the run against the report's `3 passed` claim. Reading rules and bars were committed before any rep ran. The bar is treatment 5 of 5 and control failing at least 1 of 5.

The control arms ran on BASE. `controller-run` passed 0 of 5, by construction, since `test-run` did not exist. `reviewer-run` passed 4 of 5, with one borderline failure (rep3) under the strict one-finding reading. The record is `specs/baseline/red-baseline-test-run.md`, and the rep JSON files sit under `control/` and `treatment/`. The later tasks depend on these arms to show that their text changes behavior.

### 2. The `test-run` script

`skills/subagent-driven-development/scripts/test-run` (117 lines) is the core of the branch. Everything after it calls it or describes it.

- It validates the task number as a task ID before it builds any path (`test-run:55-64`), then calls `sdd-repo --with-commit` and `sdd-workspace`.
- It records `git rev-parse HEAD` and counts `git status --porcelain --untracked-files=normal` lines before the command runs (`test-run:79-85`). The flag keeps a `status.showUntrackedFiles=no` config from hiding untracked files (ruling on Task 2 Important 1).
- It runs the command into a temporary file in the workspace, then writes the run file only after the command ends. The first run is `task-<N>-tests.log`. Run K is `task-<N>-tests-<K>.log`, the smallest K that does not exist. No file is overwritten.
- The run file has six header lines: `test-run: Task <N>, run <K>`, `command:`, `head:`, `tree:`, `exit:` and `--- output ---`. The full output follows.
- Stdout is the last 5 lines of output, then `run: <path>`. A newline guard keeps a final line with no newline from running into the `run:` line (`test-run:115`). A refusal prints no `run:` line. The exit status is the command's own, or 2 for a bad call.

The `tree:` line is the plan's addition, not the spec's (plan, Open item 5). The ruling on Task 2's extras cut a noclobber write and a `cannot write` exit and kept the newline guard. `scripts/sdd-workspace` gains `test-run` in its header comment, which the ruling on the commit gate allowed so the `orphan-bundled-file` lint passes.

`skills/subagent-driven-development/scripts/test_sdd_scripts.py` gains 23 tests, not the plan's 21 (deviation, Task 2). They cover a passing run, a failing run, a new file per run, empty output, no final newline, a dirty tree, the git-config case, a command that cannot start (exit 127), task-ID grammar, a repository with no commit and bad arguments.

### 3. `task-done` through `test-run`

`skills/executing-plans/scripts/task-done` drops its own render loop and its direct run. It calls `"$sdd/test-run" "$plan" "$n" -- "$@"`, prints its output, and takes the run file from the `run:` line. A missing `run:` line means a refusal, so it exits with test-run's status. The ledger line keeps its BASE form. It reads the rendered command from the run file, from the `command:` line up to the `head:` line, so a multi-line argument stays whole (ruling on Task 3 Important 1). The last non-blank output line comes from below `--- output ---`.

`skills/executing-plans/scripts/test_executing_plans_scripts.py` gains four tests, and its BASE tests are unchanged. One test pins the retry: a failing run stays on disk, and the next run gets its own file. executing-plans now depends on `test-run` through the `../../subagent-driven-development/scripts` path that it already used, so no install edge changes.

### 4. The controller's text

A new reference, `skills/subagent-driven-development/references/test-run.md`, holds the procedure, because SKILL.md had little room under the 20,000-character compaction window. Its bullets cover:

- **The command.** It covers `Run:` commands that run tests or checks and expect a pass, plus the project's documented tests that the change can reach. It never covers a command that edits files, rewrites history or restores state (ruling C1). All commands go in one call, `sh -c '(<cmd1>) && (<cmd2>)'`, so a `cd` does not leak (ruling C2). Expected failures and paid runs stay out.
- **A failing run.** It becomes a fix round before any review, and the round counts toward the five-attempt cap.
- **No `run:` line.** A refusal is a bad call to correct. A killed run gets a longer timeout, and a run that still does not finish is a failing run (rulings R3 and the new Important).
- **Check the run.** The controller reads `head:` and `tree:` before it dispatches. A dirty tree or the wrong HEAD is the controller's own gap (ruling R2).
- **Edge cases.** A task with no runnable test passes `none: <why>`. A batch gets one run.

`SKILL.md` adds a diamond node, "Your test run passes?", between implementation and the reviewer dispatch, with a "no: fix round" edge. Its DONE paragraph sends the controller to `test-run.md` first. `references/fix-loop.md` adds a run after every round. `references/handling-reports.md` adds the run to DONE_WITH_CONCERNS. `references/file-handoffs.md` lists four reviewer paths, not three. `references/example-workflow.md` shows the run before each review. `implementer-prompt.md` says that the report is still the implementer's evidence and that the reviewer checks it against the controller's run.

The `controller-run` treatment ran three times, each 5 of 5. The third arm (`treatment/controller-run-3`) tests the shipped text after the final review's wording changes (deviation, Task 4).

### 5. The reviewer's text

`agents/task-reviewer.md` (`## Tests`, line 75) and both forms in `task-reviewer-prompt.md` now read the run file. The report's claims are compared with the run, and a missing pass, a different count or an unreported skip or warning is Important. A run at another commit or on a dirty tree is a gap for the controller. `none: <why>` leaves the report as the only evidence. Upstream's "Do not re-run the suite" stays. Both prompt forms add a "The Controller's Test Run" section with `[RUN_FILE]` (lines 39 and 98). `re-review-prompt.md` adds `<RUN_FILE>` with the same head, tree and `none:` rules (ruling C3+R1). The Codex and Gemini adapters under `runtimes/` are regenerated.

The `reviewer-run` treatment passed 5 of 5, and the control passed 4 of 5. The control's one failure holds only under the strict reading, and the owner kept the text (deviation, Task 5). The kit spent $0.65 of its $10 stop.

### 6. Records and retirement

`NOTICE` adds a plan 84 bullet. It credits upstream for the kept "do not re-run" rule and the adapted wording, and marks the exit line, header lines, per-run files, controller run, fix round and reviewer reading as local (ruling on Task 6 Important 1 and 2). The drift spec marks finding 21 adopted and done. The spec moves to `specs/completed/` with a COMPLETE status line, and the plan moves to `specs/plans/completed/`. `specs/history.md` records 12 rulings and 13 deviations.

## What it adds to the project

- **Independent evidence.** Every SDD task review now rests on a run that the controller made at a known HEAD on a known tree. The reviewer reads it instead of trusting the implementer's claim.
- **One run script for both executors.** `test-run` serves the SDD controller and `task-done`. A change to the run format reaches both.
- **Run history.** Failing runs survive their fixes. Before the branch, `task-done` overwrote `task-<N>-tests.log`.
- **New dependencies.** `task-done`, `references/test-run.md`, both task-reviewer surfaces and the re-review prompt depend on the run-file format and the `run:` stdout line.
- **Deferred.** In `specs/deferred_items.md`, § 84: keep a killed run's partial output. `test-run` removes its temporary file in an EXIT trap, so a run that the Bash tool kills leaves no file. At BASE, `task-done` streamed its output to the log path, so this is a small regression that the owner deferred at the gate. The fix is an explicit `rm` after the run file is written.

## Questions

1. What did plan 84 set out to fix, which part of the spec did it build, and why did it leave the rest out?
2. How does a task's test run flow from `test-run` through `task-done`, the SDD controller and the reviewers, and what does the run file record?
3. What can SDD and executing-plans do after this branch that they could not do before, and what gap did the branch leave for later?
