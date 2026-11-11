# Test run

Read this when a task reaches review: after DONE, after DONE_WITH_CONCERNS once its concerns are handled, and after every fix round.

The implementer's report claims a test result. Before any review, you run the task's tests yourself, through a script, so the reviewer reads a run that the implementer did not report.

From the worktree root, run:

`<this-skill-dir>/scripts/test-run PLAN_FILE N -- <test command>`

- **The command.** Every `Run:` command in the brief that runs tests or checks and whose expected result is a pass, and the project's documented test command(s) that the change can reach (test-driven-development's "other tests"). Never rerun a command that edits files, rewrites git history or restores state. Put the commands in one call, each in its own parentheses so that a `cd` in one does not reach the next: `-- sh -c '(<cmd1>) && (<cmd2>)'`. Never one call each. Leave out a step that is expected to fail, and any run that calls a model or spends money, such as a micro-test rep.
- **What it does.** The script runs the command once. It saves the exit status and the full output in a new run file in the plan's workspace, prints the output's last lines, and prints `run: <path>` last. Each run gets its own file, and no run overwrites an earlier one.
- **A failing run** (a non-zero exit) goes back to the implementer as a fix round, before any review. The run file's path is the round's finding, as [fix-loop.md](fix-loop.md) says. The round counts toward the five-attempt cap.
- **No `run:` line.** Either the script refused or the tool killed the run. If the script refused, read its message and correct your call: it refuses only a bad call (the wrong arguments, a task number that is not an ID, or a repository with no commit). If the tool killed the run, for example at its timeout, its output so far stays in the plan's workspace, in a file named `test-run.<random>`. Read its last lines to see where the run stopped, then run it again with a longer timeout. A run that still does not finish is a failing run: send the implementer a fix round, with the command and the timeout as the round's finding.
- **Check the run.** Before you dispatch, read the run file's `head:` and `tree:` lines. A `head:` other than the HEAD you review, or a dirty tree, is a gap in your own run, not a finding against the implementer. Run `git status --porcelain --untracked-files=normal`, the check the script makes. If the leftovers are the task's files, send the implementer a fix round to commit them. If they are stray artifacts, such as a cache or an editor file, remove them. Then run the tests again.
- **A passing run.** Generate the review package. Give the reviewer the run file's path alone, not the `run:` line: `[RUN_FILE]` in the task review, `<RUN_FILE>` in a scoped re-review.
- **No command to run.** When the brief names no runnable test command (a prose or skill-text task) and the project documents none that the change can reach, run nothing. Put `none: <why>` where the path goes.
- **A batch** ([batching.md](batching.md)) gets one run, with the batch's first task number. Put the commands of every task in the batch into the one call. The reviewer gets that one run file.
- Never paste the run's output into a dispatch. The file is the evidence.
