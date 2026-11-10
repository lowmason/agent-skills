# Test run

Read this when a task reaches review: after DONE, after DONE_WITH_CONCERNS once its concerns are handled, and after every fix round.

The implementer's report claims a test result. Before any review, you run the task's tests yourself, through a script, so the reviewer reads a run that the implementer did not report.

From the worktree root, run:

`<this-skill-dir>/scripts/test-run PLAN_FILE N -- <test command>`

- **The command.** Every `Run:` command in the brief whose expected result is a pass, and the project's documented test command(s) that the change can reach (test-driven-development's "other tests"). Put them in one call, `-- sh -c '<cmd1> && <cmd2>'`, never one call each. Leave out a step that is expected to fail, and any run that calls a model or spends money, such as a micro-test rep.
- **What it does.** The script runs the command once. It saves the exit status and the full output in a new run file in the plan's workspace, prints the output's last lines, and prints `run: <path>` last. Each run gets its own file, and no run overwrites an earlier one.
- **A failing run** (a non-zero exit) goes back to the implementer as a fix round, before any review. The run file's path is the round's finding, as [fix-loop.md](fix-loop.md) says. The round counts toward the five-attempt cap.
- **A passing run.** Generate the review package. Give the reviewer the run file's path alone, not the `run:` line: `[RUN_FILE]` in the task review, `<RUN_FILE>` in a scoped re-review.
- **No command to run.** When the brief names no runnable test command (a prose or skill-text task) and the project documents none that the change can reach, run nothing. Put `none: <why>` where the path goes.
- **A batch** ([batching.md](batching.md)) gets one run, with the batch's first task number. Put the commands of every task in the batch into the one call. The reviewer gets that one run file.
- Never paste the run's output into a dispatch. The file is the evidence.
