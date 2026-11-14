# Branch `claude/musing-dhawan-59a2d0`: plan 84, controller test runs in subagent-driven development

## Synopsis

**The plan:** Plan 84 closes finding 21 of the drift spec, "Per-task test evidence is self-reported in SDD". Before
this branch, the task reviewer took the implementer's report as the only test evidence. The plan builds Design 1 of
`specs/spec-derived-acceptance-tests.md`, so a run the implementer did not report backs each review. It leaves out
Designs 2-6, which served finding 24 and which plan 83 closed with no build (D1).

**The build:** A micro-test kit ran the control arms at BASE first. Then a new script, `test-run`, runs one command
and keeps each run in its own file in the plan's workspace. `task-done` now runs its command through it. The SDD
controller text runs `test-run` before every task review, and a failing run becomes a fix round. The task reviewer
and the scoped re-review then read the run file and compare it with the report. NOTICE lines and the plan's
retirement close the branch.

**The project:** Each SDD task review now rests on a recorded run with its command, commit, tree state and exit
status. A mismatch with the report is an Important finding. Both executors share one run script. The drift spec
marks finding 21 adopted. One deferred item asks that a killed run keep its partial output.

## Background

In SDD, the implementer ran the tests and reported them. The task reviewer's Tests section said "Do not re-run the
suite to confirm their report", so the report was the whole test record. executing-plans already ran its tests
mechanically. `task-done` ran the command itself, wrote `task-<N>-tests.log`, and wrote the ledger line only on a pass.
A second run of a task overwrote that log.

The spec named two kinds of independence: in execution (finding 21) and in authorship (finding 24). The finding 24
probes (plans 81 and 83) missed their bars, and the owner closed that half with no build. Finding 21's half was left
for its own build plan, which is plan 84. Plan 82 had already given `sdd-repo --with-commit`, the commit guard Design
1 asks for (D2).

## The change

**1. Micro-test kit and control arms.** `specs/baseline/red-baseline-test-run/kit/` copies plan 82's kit. It adds two
cases in `cases.py`, set in an unrelated recipe-scaling story. `controller-run` asks whether the controller runs
`test-run` before `review-package`. `reviewer-run` gives the reviewer a run file that shows a skip the report hides. The
record, `specs/baseline/red-baseline-test-run.md`, fixed the reading rules before any rep ran. The `controller-run`
control scores 0 of 5 by construction, because `test-run` does not exist at BASE. The `reviewer-run` control passed 4
of 5, and its one failure is borderline. Tasks 4 and 5 need these arms for their treatment runs.

**2. The `test-run` script.** `skills/subagent-driven-development/scripts/test-run` is new (117 lines). It:

- checks the task number against task-brief's ID grammar before it builds any path (line 55), and refuses with exit 2
  otherwise.
- calls `sdd-repo --with-commit` (line 66), so a repository with no commit is refused, and gets the workspace from
  `sdd-workspace`.
- takes `git status --porcelain --untracked-files=normal` before the run (line 80). The flag came from a review
  ruling: a `status.showUntrackedFiles=no` config would otherwise report a dirty tree as `tree: clean`.
- runs the command once into a temporary file, then writes the run file only after the command ends. The first run is
  `task-<N>-tests.log`, and run K is `task-<N>-tests-<K>.log` (line 98). No run overwrites another.
- writes six header lines (`test-run:`, `command:`, `head:`, `tree:`, `exit:`, `--- output ---`) and the full output.
- prints the last 5 lines of output, then `run: <path>` as its last line (line 116). A guard adds a newline when the
  output lacks one, so the `run:` line always stands alone. It exits with the command's status.

The build cut two extras the implementer added: a noclobber write and a `cannot write` exit. No spec line asked for
them. `skills/subagent-driven-development/scripts/test_sdd_scripts.py` gains 23 tests, against the brief's 21. The
two extra tests cover the newline guard and the untracked-files config. Everything below depends on this script.
The Task 2 commit also edits the header comment of `scripts/sdd-workspace` so that a file names `test-run`. That
satisfies the `orphan-bundled-file` lint, and a ruling records the departure from the "listed files only" rule.

**3. `task-done` through `test-run`.** `skills/executing-plans/scripts/task-done` drops its own render loop and log
write. It calls `test-run` (line 101) and passes its stdout through. With no `run:` line, it exits with `test-run`'s
status. It now reads the ledger's command from the run file's `command:` entry (line 116), and its last output line
from after `--- output ---` (line 118). A review ruling made it read the whole `command:` entry up to `head:`, not
line 2 alone, so an argument that holds a newline keeps the ledger line byte for byte. The ledger line itself does not
change, and the BASE-era tests stay. `test_executing_plans_scripts.py` adds four tests: the delegation, a failed run
kept beside its retry, a bad task number, and the multi-line command.

**4. The controller's procedure.** `skills/subagent-driven-development/references/test-run.md` is new. It holds the
procedure, because the SKILL.md body is close to its 20,000-character compaction limit. It says:

- run every brief `Run:` command that tests or checks and should pass, plus the project's documented test commands
  that the change can reach, in one call, each in its own parentheses: `sh -c '(<cmd1>) && (<cmd2>)'`.
- never rerun a command that edits files, rewrites git history or restores state, and skip model-calling runs.
- a failing run is a fix round before any review, and it counts toward the five-attempt cap.
- no `run:` line means either a refusal (correct the call) or a killed run (retry with a longer timeout, then treat it
  as failing).
- read `head:` and `tree:` before dispatch. A wrong commit or a dirty tree is the controller's gap, and the controller
  resolves it.
- pass the path alone, or `none: <why>` when nothing runs. A batch gets one run.

The parentheses, the narrowed command rule, the head and tree bullet and the split "No `run:` line" bullet all came
from final-review rulings (C1, C2, R2, R3 and the New Important). `SKILL.md` adds a "Your test run passes?" diamond to
the process graph and rewrites **DONE** (line 181). `fix-loop.md` says to run the tests again after every round.
`file-handoffs.md` gives the reviewer four paths, not three. `handling-reports.md` and `example-workflow.md` follow.
`implementer-prompt.md` no longer says "Reviewers will not re-run tests for you". It now says the controller runs the
tests before each review. The `controller-run` treatment ran three times, each 5 of 5. The third arm tests the shipped
text.

**5. The reviewer's reading.** `agents/task-reviewer.md` (Tests, line 75) and both forms of
`skills/subagent-driven-development/task-reviewer-prompt.md` (lines 39 and 98) now read the run file. A claimed test
that the run does not show passing is an Important finding. So is a differing count, or a skip or warning the report
leaves out. A run at another commit or on a dirty tree is a gap for the controller. "Do not re-run the suite" stays.
`[RUN_FILE]` is a required placeholder. `re-review-prompt.md` adds `<RUN_FILE>` with the same rules, which final-review
rulings C3 and R1 added, because the scoped re-review does not inherit the full review's Tests section. The runtimes
under `runtimes/codex` and `runtimes/gemini` were regenerated. The `reviewer-run` treatment passed 5 of 5, and the
owner kept the text.

**6. NOTICE and completion.** `NOTICE` adds a Plan 84 bullet after plan 86's and a line under executing-plans. A
review rewrote the bullet so that it credits the kept upstream wording and calls the header, per-run files and
reviewer reading local. The plan moved to `specs/plans/completed/` and the spec to `specs/completed/`. The paths that
cite it were re-pointed, and the drift spec marks finding 21 **Adopted** and **Done**.

The `specs/history.md` entry lists 12 rulings and 13 deviations. The plan's draft differs from the diff in the
places named above: 23 tests, the `--untracked-files=normal` flag, the `sdd-workspace` comment, the narrowed
`test-run.md` and the expanded re-review prompt.

## What it adds to the project

- **SDD flow.** Implementer DONE → controller `test-run` → pass: review package and review. A fail sends the task to a
  fix round with no review. Every fix round gets a new run before the next review. The reviewer now gets four inputs:
  brief, report, run file and diff.
- **Evidence on disk.** Each run is a separate file with its commit and tree state. A failing run stays beside its
  retry, for both executors.
- **Shared script.** `task-done` and the SDD controller depend on `test-run`. Any later change to its header or
  `run:` line reaches both, and `task-done`'s ledger parsing depends on the `command:` and `--- output ---` lines.
- **Not added.** `build/check_helper_paths.py` still checks five helpers, and it does not check `test-run` (plan item
  8). Nothing changes for finding 24's acceptance tests.
- **Deferred.** One item, in `specs/deferred_items.md` § `84-spec-derived-acceptance-tests`: keep a killed run's
  partial output. At BASE, `task-done` streamed into the log, so a timeout left partial output. Now the EXIT trap
  removes the temporary file, and a killed run leaves nothing. The owner ruled to defer it at the gate.

## Questions

1. What gap in SDD's test evidence did plan 84 set out to close, and why did it build only Design 1 of the spec?
2. In what order were the parts built, and what does each part (kit, `test-run`, `task-done`, controller text,
   reviewer text) depend on?
3. How does a task's path from DONE to approval differ now, and what did the branch leave for later?
