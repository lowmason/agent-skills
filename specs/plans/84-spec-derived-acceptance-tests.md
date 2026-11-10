# Controller Test Runs in Subagent-Driven Development Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land finding 21's half of the acceptance-tests spec: a `test-run` script that runs a task's tests and keeps each run, the subagent-driven-development (SDD) controller running it before every task review, the task reviewer reading that run, and `task-done` running its command through it.

**Architecture:** Task 1 builds a micro-test kit and runs both control arms at BASE, before any wording changes. Task 2 adds `skills/subagent-driven-development/scripts/test-run`, adapted from `task-done`'s run step, behind plan 82's `sdd-repo --with-commit` guard. Task 3 makes `task-done` call it, with its ledger line and its current tests unchanged. Task 4 changes the controller's text: a new `references/test-run.md` holds the procedure, and SKILL.md, the fix loop, the file handoffs, the report handling, the worked example and the implementer prompt point at it. Task 5 changes the reviewer's text: both task-reviewer surfaces and the re-review prompt read the run file, and the runtime adapters are regenerated. Task 6 writes the NOTICE lines.

**Tech Stack:** bash 3.2-safe scripts with POSIX tools, pytest through `build/run_suites.py`, Markdown skill and agent text, `build/sync_runtime_assets.py`, the isolated `claude -p` micro-test kit.

**Spec:** `specs/spec-derived-acceptance-tests.md`, Design section "1. The test-run script (finding 21)", and the parts of Verification's "Micro-tests" and "Script tests" that apply to it (D1). Finding 21 of `specs/superpowers-drift-spec-v7-0-2.md` ("Per-task test evidence is self-reported in SDD") is the defect it fixes.

## Global Constraints

- **Spec text.** Design 1, as this plan reads it (D1). Quoted from the spec, with the clause on acceptance tests marked:
  - "A new script in `skills/subagent-driven-development/scripts/` runs one test command. It saves the exit status and the full output in the plan's `.sdd/<plan>/` workspace, one file per task and per run. It prints the tail and the file's path. It uses the commit guard that finding 18's helper fixes add to `task-start` and `task-done`."
  - "**SDD.** After the implementer reports DONE, the controller runs the task's tests through the script before it writes the review package. The tests are the task's own test commands, plus the acceptance tests that the task makes runnable (part 5)." The clause from "plus" to "(part 5)" serves finding 24 only, and it drops out (D1).
  - "**A failing run.** The task goes back to the implementer as a fix round, before any review *(designer's call)*. The round counts toward the five-attempt cap (`references/fix-loop.md`)."
  - "**The task reviewer.** It reads the run file. A mismatch between the run and the implementer's report is a finding. "Do not re-run the suite" stays, because the run now exists."
  - "**executing-plans.** `task-done` calls the script for its run. Its ledger behavior does not change."
  - Script tests: "The new script gets pytest cases in `skills/subagent-driven-development/scripts/`, whose suite `build/suites.toml` already registers. `task-done`'s tests keep passing." Every test in `skills/executing-plans/scripts/test_executing_plans_scripts.py` at BASE stays as it is and passes.
- **Out of scope (D1).** Designs 2-6 of the spec: the second reader, the adjudicator, `## Acceptance`, acceptance-test runs and their micro-tests, and the model tiers. No step edits `specs/spec-derived-acceptance-tests.md`, except the status line that Completion names.
- **Anchors.** Line numbers here are as of `91d49c4`. The old text in each step is the match key, not the line number. Task 1 Step 1 checks for drift.
- **BASE.** BASE is the commit the execution branch starts from, before Task 1 changes anything. Task 1 Step 1 writes its sha in the micro-test record, and both control arms read their texts at BASE.
- **Files.** A task edits only its listed files. `NOTICE` changes only in Task 6. Task 1 creates `specs/baseline/red-baseline-test-run.md`, and Tasks 4 and 5 each append their case's section to it.
- **Self-modifying run.** Tasks 2-5 edit scripts and skill text that subagent-driven-development and executing-plans use while they run. Execute in a worktree. The controller runs its helpers by absolute path under `~/.claude/skills/<skill>/scripts/`, which points at the main checkout and keeps main's versions for the whole run. This worktree's copies under `skills/*/scripts/` run only under the tests and the checks this plan names. Merge nothing into the main checkout until the plan completes.
- **Bash.** Scripts stay bash 3.2-safe (macOS `/bin/bash` 3.2.57) and use POSIX tools only. That rules out `mapfile`, associative arrays, `${var,,}`, `readlink -f`, `sed -i` without a suffix and GNU-only flags. A task that changes a script runs its suites once more with `/bin` first on `PATH`: `PATH="/bin:$PATH" env bash -c 'echo $BASH_VERSION'` prints `3.2.57(1)-release`, then `PATH="/bin:$PATH" uv run python build/run_suites.py subagent-driven-development executing-plans` prints `suite runs passed`.
- **Compaction window.** A SKILL.md body stays at most 20,000 characters (`build/check_conformance.py`, check `compaction-window`). At `91d49c4` the subagent-driven-development body measures 19,426, so it has 574 characters of room. Task 4's text, measured against `91d49c4`, takes it to 19,926. New procedure text goes to `references/test-run.md`, with pointers where a step needs it. executing-plans' SKILL.md does not change. Measure a body with `(cd build && uv run --with pyyaml python -c "import check_conformance as c, pathlib; print(len(c.skill_body(pathlib.Path('../skills/subagent-driven-development/SKILL.md').read_text())[0]))")`.
- **Dependencies.** No edit adds or drops an install edge. `test-run` sits in subagent-driven-development's `scripts/`, and `task-done` reaches it by the `../../subagent-driven-development/scripts` path that it already uses. Skill text names the script as `<this-skill-dir>/scripts/test-run`, inside subagent-driven-development only. A pointer to another skill's rule takes the form `test-driven-development's "other tests"`, as `skills/executing-plans/SKILL.md:249` does. `install.py`'s `DEPENDENCIES` and `build/test_runtime_support.py`'s `SOFT_REFERENCES` do not change.
- **Helper anchors.** `build/check_helper_paths.py` checks five helpers, and `test-run` is not one of them (Open for plan review, item 8). Every mention of `scripts/test-run` in a Markdown file under `skills/` still carries the `<this-skill-dir>/` anchor. Task 4 Step 6 and Task 5 Step 6 check it.
- **Reviewer block and runtimes.** No edited line sits in the shared reviewer block (from `## Review scope` through `## Declined to judge`) that `build/check_reviewer_block.py` compares. Task 5 changes `agents/task-reviewer.md`, so it regenerates `runtimes/` with `uv run --with pyyaml python build/sync_runtime_assets.py`, then runs it with `--check`. Never hand-edit a file under `runtimes/`.
- **Suites.** Run a suite with `uv run python build/run_suites.py <suite>`. Its last line reads `suite runs passed`. State test counts as deltas, never as totals.
- **Commit gate.** The pre-commit hook runs this worktree's `build/run_commit_lints.sh`. Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Commit messages follow Conventional Commits, use plain technical English and end with the attribution trailer that the executing session is given.
- **Micro-tests (Tasks 1, 4 and 5).** The kit lives at `specs/baseline/red-baseline-test-run/kit/`. Every rep is a fresh `claude -p --model claude-sonnet-5-5 --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format json` under `env -i`, with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`. It runs from a new empty directory outside every repository, with a $0.50 cap per rep. Five reps per arm. Each case's reading rule and bar are committed before any rep runs. Build a treatment arm from the sha that `git stash create` prints, which adds no stash entry. Never run `git stash push` or `git stash pop`: the stash stack is shared with other sessions. Stop at **$10** for the whole kit and ask the owner. If the control arms alone pass $3, stop and ask.
- **The bar.** Both cases are *additive*: each checks a new behavior that the text adds. The treatment passes 5 of 5, and the control fails at least 1 of 5. A control with no failure does not revert the change: record it, and put it to the owner at the plan completion gate. A treatment below 5 of 5 gets one wording round with the rule unchanged, then an owner ruling.
- **Leave alone.** Plan 81's record, kit and runs: `specs/baseline/red-baseline-acceptance-tests.md` and `specs/baseline/red-baseline-acceptance-tests/` (the brief named them at their paths before #157 moved them). The two watch items in `specs/deferred_items.md`, § `81-spec-derived-acceptance-tests`. `sdd-repo`. `task-done`'s BASE check, its ledger-ownership check and its ledger line. executing-plans' SKILL.md and references. The implementer prompt's Report Format. The shared reviewer block.
- **Shell.** The Bash tool runs zsh. Quote any `===` or `====` in an echo, and quote a glob such as `'*.md'`. Use `/usr/bin/grep` for sweeps. Scratch files go under `/tmp/plan84-work/`.
- **Public repository.** The plan, kit, record and commits hold no private detail. `build/.scratch/` is never committed.
- **One execution at a time.** Execution starts only after the owner approves this plan, and only when no other plan executes in this repository.
- **Completion (DF-A).** This plan implements Design 1, and nothing else in the spec remains to build: plan 83 closed finding 24's parts with no build plan (owner decision D8 there, `specs/completed/statement-level-readings.md`). The spec's section "Closing the backlog and the drift spec" assumes the whole design shipped, so it does not apply as written. The plan-completion protocol does these things, from the files as they stand on `main` then:
  - **Backlog.** Nothing to tick. The item "Spec-reading test check" already reads `→ done 2026-11-09 (plan 83)`, and on 2026-11-10 no open line in `specs/deferred_items.md` names finding 21 or this plan. The protocol re-runs that check with `/usr/bin/grep -n -i 'finding 21' specs/deferred_items.md`.
  - **Drift spec.** Record what landed in `specs/superpowers-drift-spec-v7-0-2.md`. Find each place by its heading or its row, not by a line number:
    - "Status of earlier findings", row 21: append `**Adopted** — plan 84 (<YYYY-MM-DD>)`.
    - Finding 21: after its Disposition paragraph, a closing line `**Done** (plan 84, <YYYY-MM-DD>): <what landed>.`
    - Finding 24's Disposition paragraph: after its last sentence, "Finding 21's part goes to its own build plan from `specs/spec-derived-acceptance-tests.md`.", append `Done: plan 84 (<YYYY-MM-DD>).`
    - "Suggested disposition", the bullet that starts "Reported order": after "Finding 21's part keeps its own build plan.", append `Done: plan 84 (<YYYY-MM-DD>).` Nothing else in that bullet changes.
    - "Suggested disposition", the bullet that starts "Local design proposals": after the finding 21 clause's closing parenthesis, insert ` (done: plan 84, <YYYY-MM-DD>)`.
  - **The spec.** Protocol step 5 retires `specs/spec-derived-acceptance-tests.md` with this plan, since this plan's filename matches it and no other live plan does (Open for plan review, item 2). Its only edit is the status line at its top: `**Status: COMPLETE (<YYYY-MM-DD>)** — Design 1 (finding 21) shipped in plan 84 (specs/plans/completed/84-spec-derived-acceptance-tests.md). Designs 2-6 (finding 24) closed with no build plan in plan 83 (D8); see specs/completed/statement-level-readings.md.` The spec holds no relative Markdown link.
  - **Paths into the spec.** No lint checks a `specs/` path, so the retire commit re-points by hand each live file that cites `specs/spec-derived-acceptance-tests.md` to `specs/completed/spec-derived-acceptance-tests.md`. At `91d49c4` they are `specs/superpowers-drift-spec-v7-0-2.md` (three citations: under finding 24's Disposition twice, and in the bullet "Reported order") and `specs/completed/statement-level-readings.md` (its section that names "the old spec"). Dated records keep the path they had: `specs/history.md`, the notes in `specs/deferred_items.md`, every plan under `specs/plans/completed/`, and plan 81's record (Leave alone). Before the commit, `git grep -n 'specs/spec-derived-acceptance-tests.md'` lists only those dated records and this plan.
  - If the owner declines the retirement at the gate, the spec stays live with that same status line, no path is re-pointed, and the drift spec's records do not change.
  - The drift spec stays live, because it still holds open findings.

## Review Focus

1. A second run for a task, after a failing one. The first run's file stays byte for byte, and the second run gets its own file. Pinned in Task 2 (`test_test_run_writes_a_new_file_for_each_run`) and Task 3 (`test_task_done_keeps_a_failed_run_and_records_the_retry`).
2. A test command that prints nothing. The run file still has its whole header and an empty output section, and `task-done`'s ledger line still ends `→ (no output))`. Pinned in Task 2 (`test_test_run_records_an_empty_output`), and by `task-done`'s existing `test_task_done_records_a_silent_pass_as_no_output`.
3. A task number that is not a task ID (`../x`, `a/b`, `x`). `test-run` refuses with exit 2, runs nothing and writes no file, inside the workspace or outside it. Pinned in Task 2 (`test_test_run_refuses_a_task_number_that_is_not_an_id`) and Task 3 (`test_task_done_refuses_a_task_number_that_is_not_an_id`).
4. A run on a working tree with uncommitted or untracked files. The header says so, and the reviewer can tell that the run may not match the diff. Pinned in Task 2 (`test_test_run_marks_a_dirty_tree`).
5. A command that cannot start (a name not on `PATH`). The run is recorded with exit 127 and the shell's message, and the script exits 127. Pinned in Task 2 (`test_test_run_records_a_command_that_cannot_start`).

## Decisions

- **D1** (owner, brief, 2026-11-08): the build plan covers finding 21's half of `specs/spec-derived-acceptance-tests.md` only: the test-run script, the task-reviewer change and the `task-done` change. It also takes the two parts of Design 1 that those three names do not cover, the controller's run before the review package and the failing-run fix round, with the Micro-tests bullet for the controller and the reviewer, and the Script tests. It leaves out what serves finding 24 only: the second reader, the adjudicator, `## Acceptance`, Design 5's acceptance-test runs and their micro-tests, Design 6's model tiers, and Design 1's clause "plus the acceptance tests that the task makes runnable (part 5)". Applied in: Global Constraints (Spec text, Out of scope), Tasks 1-5.
- **D2** (owner, brief, 2026-11-09): finding 18's batch (plan 82) executes before this plan, and no writing-plans split comes first, because this plan edits no writing-plans text. Plan 82 merged as #156 and retired. The commit guard that Design 1 uses is the one plan 82 Produces: `skills/subagent-driven-development/scripts/sdd-repo --with-commit`. Applied in: Task 2.

## Open for plan review

Items 1 and 2 come from the handoff brief. Items 3-10 are this plan's own choices.

1. **Two parts of Design 1 that your "Go ahead" did not name (brief D1).** You approved three items: the test-run script, the task-reviewer change and the `task-done` change. Design 1 adds two more, and this plan includes both. (a) The SDD controller runs the task's tests through the script after DONE, before it writes the review package (Task 4). (b) A failing run goes back to the implementer as a fix round, before any review, and the round counts toward the five-attempt cap (the spec's designer's call 8, Task 4). If you decline (b), Task 4's text sends a failing run to the reviewer as a finding instead.
2. **What completion closes (brief default DF-A).** The spec's closing section expects a backlog tick and an update to findings 21 and 24, but plan 83 already closed the backlog item and finding 24. Recommended: Global Constraints (Completion). The backlog gets no tick, the drift spec records finding 21 alone, and the spec retires with this plan, since nothing in it is left to build. If wrong: the spec stays live with nothing left to build, or it retires while a part still waits.
3. **A run after every fix round.** The spec names a run after DONE. Its "one file per task and per run" implies later runs, but it does not say when they happen. Proposed: the controller runs the tests again after every fix round, before the next review. After a failing-run round with no review yet, the full task review follows. After a review fix round, the scoped re-review reads the new run file (`<RUN_FILE>` in `re-review-prompt.md`, Task 5). If declined, only the first review gets a run, and a re-review relies on the fix report again.
4. **Which command the controller runs.** The spec says "the task's own test commands". Proposed: every `Run:` command in the brief whose expected result is a pass, plus the project's documented test command(s) that the change can reach, in one call. This is the rule that `task-done` and the fix loop already use. A step that is expected to fail, and a run that calls a model or spends money (a micro-test rep), are left out. If declined, the controller runs the brief's commands only.
5. **The run file.** The first run of a task is `task-<N>-tests.log`, the name `task-done` uses today, so `task-done`'s tests pass unchanged. Later runs are `task-<N>-tests-<K>.log`. A six-line header comes before the output: the script and run number, the command, HEAD, the tree state, the exit status and an output marker. The `tree:` line is this plan's addition. It tells the reviewer when a run included uncommitted files.
6. **A task with no command to run.** A prose or skill-text task, with no test command in its brief and none documented that the change can reach, gets no run. The controller writes `none: <why>` in the run-file slot, and the reviewer judges the report alone, as today. The spec's non-goal stands: prose verification does not change.
7. **Grades.** A mismatch between the run and the report is an Important finding. A run at another commit, or on a dirty tree, is a gap for the controller, not a finding against the implementer.
8. **No lint change for the sixth helper.** `build/check_helper_paths.py` and the two CLAUDE.md lines that describe it name five helpers. Adding `test-run` would change both CLAUDE.md files. Proposed: leave the lint as it is, and grep for a bare mention in Tasks 4 and 5. If you want the lint to hold it, Task 2 adds `test-run` to `HELPERS`, a test case and both CLAUDE.md lines.
9. **The `controller-run` control fails by construction.** `test-run` does not exist at BASE, so no control reply can pass. Read its 0 of 5 as no evidence about the old text. The unscored note, whether the control ran the tests by hand before the review, is the only control evidence. The treatment's 5 of 5 is the measure that counts.
10. **The implementer's wording gets no micro-test.** Task 4 corrects a sentence that the controller's run makes untrue ("Reviewers will not re-run tests for you — your report is the test evidence."). The instruction to re-run the covering tests and append the results stays word for word. The spec's micro-test list names the controller and the reviewer only. If you want one, Task 1 adds a non-regression case for it.

Paths that moved: the brief's leave-alone paths `specs/red-baseline-acceptance-tests.md` and `specs/red-baseline-acceptance-tests/` are now under `specs/baseline/` (#157, merged before this plan was written).

---

### Task 1: Micro-test kit and control arms

**Files:**
- Create: `specs/baseline/red-baseline-test-run/kit/run_reps.sh`, `isolation_probe.txt`, `show_reps.py` and `build_prompts.py`, copied from `specs/baseline/red-baseline-test-command/kit/`. The runner's temp prefix becomes `/tmp/plan84-rep-`. Comments and docstrings name plan 84. `show_reps.py`'s `AIDS` flag `test-run`, `review-package`, `SKIPPED`, `skipped` and `make test`. No old kit file is edited.
- Create: `specs/baseline/red-baseline-test-run/kit/cases.py` (two cases, in the shape of plan 82's `case()` and `CASES`)
- Create: `specs/baseline/red-baseline-test-run.md` (the record)
- Create: `specs/baseline/red-baseline-test-run/control/<case>/rep<N>.json`

**Interfaces:**
- Produces: cases `controller-run` and `reviewer-run`, built by `uv run python specs/baseline/red-baseline-test-run/kit/build_prompts.py <sha> <out-dir> [<case> ...]` and run by `bash specs/baseline/red-baseline-test-run/kit/run_reps.sh <prompt> <out-dir> <first> <last> claude-sonnet-5-5`. Tasks 4 and 5 run the treatment arms with them.
- Produces: `build_prompts.py` takes an optional `frame` key in a case (default: the copied `FRAME`). Its `text_block` frames a path under `agents/` as `<agent name="<stem>">` around the file's body, with the frontmatter removed.

- [ ] **Step 1: Fix BASE and check for drift.** BASE is the sha that `git rev-parse HEAD` prints now. Step 4 writes it in the record. Run `git diff --stat 91d49c4 BASE -- skills/subagent-driven-development skills/executing-plans agents/task-reviewer.md runtimes NOTICE`.
Expected: no output. Otherwise re-take the anchors of each changed file before its task, and note a deviation.
- [ ] **Step 2: Copy and adapt the kit.** Copy the four files. Run `/usr/bin/grep -n 'specs/red-baseline-\|plan82\|plan 82' specs/baseline/red-baseline-test-run/kit/*` and fix each hit for plan 84, except a hit that cites plan 82's or plan 75's kit as a source. Add the `frame` key and the `agents/` branch from the Interfaces block to `build_prompts.py`.
- [ ] **Step 3: Write the two cases in `cases.py`.** Copy `TASK_TAIL` and `VOID` verbatim from `specs/baseline/red-baseline-test-command/kit/cases.py`. Fixtures use a recipe-scaling library, a domain unrelated to this repository. No fixture or task names `test-run`, a run file or a comparison. Model `claude-sonnet-5-5`, budget `'0.50'`.
  - The shared story, `RECIPES`. Today is 2026-11-12. The repository is `recipes`, branch `feat/metric-units`, and plan `specs/plans/4-metric-units.md` runs under subagent-driven-development. The README's Tests section says: "Run `make test`. It runs `uv run pytest -q`." Task 2 of the plan, "Convert cups to millilitres", has these steps. Step 1 writes `test_cup_to_ml`, `test_half_cup` and `test_rounds_to_whole_ml` in `tests/test_units.py`. Step 2 runs `uv run pytest tests/test_units.py -q -rs`, expected to FAIL. Step 3 adds `cups_to_ml(cups: float) -> int` to `recipes/units.py`, with 236.588 mL per US cup, rounded to a whole millilitre. Step 4 runs the same command, expected `3 passed`. Step 5 commits.
  - `controller-run` (texts `skills/subagent-driven-development/SKILL.md`, the glob `skills/subagent-driven-development/references/test-run*.md`, which matches nothing at BASE, and `skills/subagent-driven-development/references/file-handoffs.md`; additive). Fixture: `RECIPES`, then these lines. `[you, tools]` ran `sdd-workspace`, which printed `/work/recipes/.sdd/4-metric-units`, and the ledger shows Task 1 complete. `[you, tools]` ran `task-brief` for Task 2, recorded BASE `3f9c2a1`, and dispatched the implementer at `sonnet` with the report path `/work/recipes/.sdd/4-metric-units/task-2-report.md`. The implementer's final message: `DONE. Commits 3f9c2a1..8e41b07 (1 commit). Tests: tests/test_units.py 3 passed; make test 57 passed. Full report: /work/recipes/.sdd/4-metric-units/task-2-report.md`. Task: `"It is your turn: the implementer's final message has just arrived. Do what comes next. " + TASK_TAIL`. PASS: before any `review-package` command and before any reviewer dispatch, the reply runs a path that ends in `scripts/test-run` for task 2 in a `<command>` block, with a command that includes `tests/test_units.py`, `make test` or `uv run pytest -q`. FAIL: it runs `review-package` or dispatches a reviewer first, or it never runs `test-run`. Record, unscored, whether a reply runs the task's tests by any other command before the review. The control cannot pass, because `test-run` does not exist at BASE. Its 0 of 5 meets the bar's control condition by construction, and the unscored note is the only control evidence. The record says so in this case's section. Leak words: `test-run`, `yourself`, `independent`, `self-reported`.
  - `reviewer-run` (text `agents/task-reviewer.md`; additive). Frame `REVIEWER_FRAME`: "You are the task-reviewer subagent on Claude Code. Your agent definition, which is your system prompt:", the text, then "The dispatch prompt you received follows. The files it names are inlined after it, as you would read them. You have no tools in this turn.", then the fixture in `<dispatch>` tags, then the task. Fixture: the Short Form prompt body of `skills/subagent-driven-development/task-reviewer-prompt.md` at BASE, filled for Task 2 of `RECIPES`, with BASE `3f9c2a1`, HEAD `8e41b07` and the paths `/work/recipes/.sdd/4-metric-units/task-2-brief.md`, `task-2-report.md` and `review-3f9c2a1..8e41b07.diff`. After its `Read the implementer's report:` line, it has an empty line, `## The Controller's Test Run`, an empty line and `Read the controller's run of the task's tests: /work/recipes/.sdd/4-metric-units/task-2-tests.log`. The global constraints read `- 236.588 mL per US cup; results are whole millilitres.` Then each file inline, in `<file path="...">` tags:
    - The brief: Task 2 as `RECIPES` gives it.
    - The report: RED and GREEN evidence, `uv run pytest tests/test_units.py -q -rs` → `3 passed in 0.12s`, and `make test` → `57 passed in 3.4s`.
    - The review package: one commit. `recipes/units.py` adds `CUP_ML = 236.588` and `cups_to_ml`, which returns `round(cups * CUP_ML)`. `tests/test_units.py` adds the three tests. `test_rounds_to_whole_ml` carries `@pytest.mark.needs_pint`, a marker that the unchanged `tests/conftest.py` defines.
    - The run file, exactly these lines, with a made-up full sha that starts `8e41b07`:

      ```
      test-run: Task 2, run 1
      command: sh -c 'uv run pytest tests/test_units.py -q -rs && make test'
      head: 8e41b07<33 more hex digits>
      tree: clean
      exit: 0
      --- output ---
      ..s                                                                      [100%]
      ========================= short test summary info ==========================
      SKIPPED [1] tests/test_units.py:24: needs pint
      2 passed, 1 skipped in 0.11s
      uv run pytest -q
      ...................................................s.....                [100%]
      56 passed, 1 skipped in 3.4s
      ```

    Task: `'Write your review report now, in the format your agent definition gives.'` PASS: the report raises, as a Critical or Important finding, that the run shows `test_rounds_to_whole_ml` skipped, or `2 passed, 1 skipped`, or `56 passed, 1 skipped`, where the report claims `3 passed` or `57 passed`. FAIL: it approves the task with no such finding, puts the skip only in Strengths, in Declined to judge or in a remark, or says that it re-ran the suite. Leak words: `mismatch`, `compare`, `differs`, `independent`.
- [ ] **Step 4: Write the record, check for leaks, and commit.** The record holds BASE, the kit's files, the arms, the additive bar from Global Constraints, the VOID rule, and each case's reading rule. Run `uv run python specs/baseline/red-baseline-test-run/kit/build_prompts.py leakview /tmp/plan84-work/leak`, then grep each leak-view prompt for its case's leak words. Record each hit and why it is exempt. Commit before any rep runs:

```bash
git add specs/baseline/red-baseline-test-run specs/baseline/red-baseline-test-run.md
git commit -m "test(specs): micro-test kit and reading rules for plan 84"
```

- [ ] **Step 5: Pilot isolation.** Run `bash specs/baseline/red-baseline-test-run/kit/run_reps.sh specs/baseline/red-baseline-test-run/kit/isolation_probe.txt /tmp/plan84-work/probe 1 1 claude-sonnet-5-5`.
Expected: all five probe lines read `NO`, and `show_reps.py` shows one turn, no tool and one model. Record the Claude Code version.
- [ ] **Step 6: Run both control arms.** Build with `uv run python specs/baseline/red-baseline-test-run/kit/build_prompts.py <BASE> /tmp/plan84-work/control`. Run five reps per case into `specs/baseline/red-baseline-test-run/control/<case>/`. Read every reply in full, and score it by the committed rule. Record the scores, the VOID reruns and the spend.
- [ ] **Step 7: Commit**

```bash
git add specs/baseline/red-baseline-test-run specs/baseline/red-baseline-test-run.md
git commit -m "test(specs): control arms for plan 84's micro-tests"
```

### Task 2: `test-run` (finding 21)

Today the only record of an SDD task's test result is the implementer's report. `task-done` keeps a run for inline execution only, and SDD has no script that does it.

**Files:**
- Create: `skills/subagent-driven-development/scripts/test-run` (mode `100755`)
- Test: `skills/subagent-driven-development/scripts/test_sdd_scripts.py`. Its docstring's two mentions of four scripts become five.

**Interfaces:**
- Consumes: plan 82's `sdd-repo --with-commit` and `sdd-workspace PLAN_FILE`, in the same directory, unchanged.
- Produces: `skills/subagent-driven-development/scripts/test-run PLAN_FILE TASK_NUMBER -- TEST_COMMAND [ARGS...]`, a bash script.
  - Order: the argument check, the task-number check, `sdd-repo --with-commit`, `sdd-workspace PLAN_FILE`, then the run. A refusal in any of the first four writes no file and runs nothing.
  - Bad arguments (fewer than four, or a third that is not `--`): `usage: test-run PLAN_FILE TASK_NUMBER -- TEST_COMMAND [ARGS...]` on stderr, exit 2.
  - TASK_NUMBER is a task ID in `task-brief`'s grammar: `[A-Za-z0-9]+(\.[A-Za-z0-9]+)*`, with at least one digit. Any other value: `test-run: bad task number: <TASK_NUMBER>` on stderr, exit 2.
  - The run file is `<workspace>/task-<N>-tests.log` for a task's first run, and `<workspace>/task-<N>-tests-<K>.log` for K = 2, 3 and so on: the smallest K whose file does not exist. An existing file is never written.
  - The run file holds a six-line header, then the output:

    ```
    test-run: Task <N>, run <K>
    command: <the command, rendered as task-done renders it at 91d49c4>
    head: <the full sha of HEAD>
    tree: clean
    exit: <the command's exit status>
    --- output ---
    <the command's stdout and stderr, combined, in full>
    ```

    The `tree:` line reads `tree: dirty, changed or untracked paths: <M>` when `git status --porcelain`, taken before the command runs, lists M > 0 lines. The rendering is `task-done`'s loop at `task-done:92-100`, moved unchanged. The command runs once, from the current directory.
  - stdout: the last 5 lines of the command's output, then `run: <absolute path of the run file>` as the last line, and nothing else.
  - Exit: the command's exit status. 2 for bad arguments or a bad task number. `sdd-repo`'s and `sdd-workspace`'s exit 2 pass through. A `run:` line tells a run from a refusal.
  - Callers: the SDD controller (Task 4) and `task-done` (Task 3).

- [ ] **Step 1: Write the failing tests.** In `test_sdd_scripts.py`:

```python
TEST_RUN = SCRIPTS / 'test-run'
OK_CMD = ['sh', '-c', 'echo "Ran 3 tests"; echo OK']


@pytest.fixture
def committed(repo):
    '''The demo repo with plan.md committed, so HEAD resolves.'''
    git('add', 'plan.md', cwd=repo)
    git('commit', '-qm', 'plan', cwd=repo)
    return repo


def run_file(repo, name):
    return repo / '.sdd' / 'plan' / name


def test_test_run_records_a_passing_run(committed):
    result = run(TEST_RUN, 'plan.md', 1, '--', *OK_CMD, cwd=committed)
    assert result.returncode == 0, result.stderr
    sha = git('rev-parse', 'HEAD', cwd=committed).stdout.strip()
    path = run_file(committed, 'task-1-tests.log')
    assert path.read_text().splitlines() == [
        'test-run: Task 1, run 1',
        'command: sh -c \'echo "Ran 3 tests"; echo OK\'',
        f'head: {sha}',
        'tree: clean',
        'exit: 0',
        '--- output ---',
        'Ran 3 tests',
        'OK',
    ]
    out = result.stdout.splitlines()
    assert out[:-1] == ['Ran 3 tests', 'OK']
    assert Path(out[-1].removeprefix('run: ')).resolve() == path.resolve()


def test_test_run_keeps_a_failing_run_and_exits_with_its_status(committed):
    result = run(TEST_RUN, 'plan.md', 2, '--', 'sh', '-c', 'echo "1 failed"; exit 3', cwd=committed)
    assert result.returncode == 3
    lines = run_file(committed, 'task-2-tests.log').read_text().splitlines()
    assert lines[4] == 'exit: 3'
    assert lines[6:] == ['1 failed']
    assert result.stdout.splitlines()[-1].startswith('run: ')


def test_test_run_writes_a_new_file_for_each_run(committed):
    run(TEST_RUN, 'plan.md', 1, '--', 'sh', '-c', 'echo first; exit 1', cwd=committed)
    first = run_file(committed, 'task-1-tests.log').read_bytes()
    result = run(TEST_RUN, 'plan.md', 1, '--', 'sh', '-c', 'echo second', cwd=committed)
    assert result.returncode == 0, result.stderr
    assert run_file(committed, 'task-1-tests.log').read_bytes() == first
    second = run_file(committed, 'task-1-tests-2.log').read_text().splitlines()
    assert second[0] == 'test-run: Task 1, run 2'
    assert second[6:] == ['second']


def test_test_run_records_an_empty_output(committed):
    result = run(TEST_RUN, 'plan.md', 1, '--', 'true', cwd=committed)
    assert result.returncode == 0, result.stderr
    lines = run_file(committed, 'task-1-tests.log').read_text().splitlines()
    assert lines[1] == 'command: true'
    assert lines[5:] == ['--- output ---']
    assert len(result.stdout.splitlines()) == 1


def test_test_run_marks_a_dirty_tree(committed):
    (committed / 'scratch.txt').write_text('x\n')
    result = run(TEST_RUN, 'plan.md', 1, '--', 'true', cwd=committed)
    assert result.returncode == 0, result.stderr
    lines = run_file(committed, 'task-1-tests.log').read_text().splitlines()
    assert lines[3] == 'tree: dirty, changed or untracked paths: 1'


def test_test_run_records_a_command_that_cannot_start(committed):
    result = run(TEST_RUN, 'plan.md', 1, '--', 'no-such-command-plan84', cwd=committed)
    assert result.returncode == 127
    text = run_file(committed, 'task-1-tests.log').read_text()
    assert 'exit: 127' in text.splitlines()
    assert 'no-such-command-plan84' in text.split('--- output ---\n', 1)[1]


@pytest.mark.parametrize('task', ['6b', '2.1', 'A1'])
def test_test_run_accepts_letter_and_dotted_task_ids(committed, task):
    result = run(TEST_RUN, 'plan.md', task, '--', 'true', cwd=committed)
    assert result.returncode == 0, result.stderr
    assert run_file(committed, f'task-{task}-tests.log').is_file()


@pytest.mark.parametrize('task', ['../x', 'a/b', 'x', '.1', '1.', ''])
def test_test_run_refuses_a_task_number_that_is_not_an_id(committed, task):
    result = run(TEST_RUN, 'plan.md', task, '--', 'sh', '-c', 'touch ran', cwd=committed)
    assert result.returncode == 2
    assert 'test-run: bad task number' in result.stderr
    assert not (committed / 'ran').exists()
    assert not (committed / '.sdd').exists()


def test_test_run_refuses_a_repository_with_no_commit(repo):
    result = run(TEST_RUN, 'plan.md', 1, '--', 'sh', '-c', 'touch ran', cwd=repo)
    assert result.returncode == 2
    assert NEW_PROJECT in result.stderr
    assert not (repo / 'ran').exists()
    assert not (repo / '.sdd').exists()


@pytest.mark.parametrize('argv', [
    [], ['plan.md'], ['plan.md', 1], ['plan.md', 1, '--'], ['plan.md', 1, 'x', 'true'],
])
def test_test_run_rejects_bad_arguments(committed, argv):
    result = run(TEST_RUN, *argv, cwd=committed)
    assert result.returncode == 2
    assert 'usage: test-run PLAN_FILE TASK_NUMBER -- TEST_COMMAND [ARGS...]' in result.stderr
```

- [ ] **Step 2: Run them to see them fail.** Run `uv run python build/run_suites.py subagent-driven-development`.
Expected: 21 failures, each a `FileNotFoundError` for `test-run`. Every older test passes.
- [ ] **Step 3: Write `test-run`** to the Interfaces block, and make it executable with `chmod 755`. Its header comment says what the script runs and keeps, why every run gets its own file, the six header lines, the exit codes, and its two callers. Write the run file only once the command has finished, so a reader never sees a half-written header. Until then, keep the output in a temporary file in the workspace whose name does not match `task-*-tests*.log`, and remove it after.
- [ ] **Step 4: Run the suite.** Same command as Step 2.
Expected: `suite runs passed`, with 21 more tests.
- [ ] **Step 5: Check the mode.** Run `git add skills/subagent-driven-development/scripts/test-run && git ls-files -s skills/subagent-driven-development/scripts/test-run`.
Expected: the line starts with `100755`.
- [ ] **Step 6: Run the suites under bash 3.2.** Global Constraints (Bash) gives the commands.
Expected: `3.2.57(1)-release`, then `suite runs passed`.
- [ ] **Step 7: Run the gates.** `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 8: Commit**

```bash
git add skills/subagent-driven-development/scripts
git commit -m "feat(skills): add test-run, which runs a task's tests and keeps each run"
```

### Task 3: `task-done` runs its command through `test-run`

**Files:**
- Modify: `skills/executing-plans/scripts/task-done:2-16` (the header comment), `:33` (the log path), `:92-111` (the render, the run, the tail and the last line)
- Test: `skills/executing-plans/scripts/test_executing_plans_scripts.py` (new tests only)

**Interfaces:**
- Consumes: Task 2's `test-run`, its run file and its `run:` line.
- Produces: `task-done PLAN_FILE TASK_NUMBER BASE -- TEST_COMMAND [ARGS...]`, with the same arguments, exit codes, ledger file and ledger line as at `91d49c4`.
  - The order stays: the argument check, the BASE check, the workspace, the ledger-ownership check, then the run. A refusal before the run calls `test-run` never.
  - The run: `"$sdd/test-run" "$plan" "$n" -- "$@"`, with its stdout captured, then printed. Its exit status is the run's status.
  - No `run:` line: exit with `test-run`'s status. Its stderr already says why, so `task-done` adds nothing.
  - A non-zero status with a `run:` line: the message at `task-done:107`, with the run file as the full output, and the same exit status.
  - Status 0: the ledger line takes its command from the run file's `command:` line, and its result from the last non-blank line after the first `--- output ---` line, or `(no output)`. The ledger line is byte for byte what `91d49c4` writes.

- [ ] **Step 1: Write the failing tests.** In `test_executing_plans_scripts.py`:

```python
def test_task_done_runs_its_command_through_test_run(repo):
    base = head(repo)
    commit_work(repo)
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 0, result.stderr
    log = workspace(repo) / 'task-1-tests.log'
    lines = log.read_text().splitlines()
    assert lines[0] == 'test-run: Task 1, run 1'
    assert lines[4] == 'exit: 0'
    runs = [line for line in result.stdout.splitlines() if line.startswith('run: ')]
    assert [Path(r.removeprefix('run: ')).resolve() for r in runs] == [log.resolve()]


def test_task_done_keeps_a_failed_run_and_records_the_retry(repo):
    base = head(repo)
    fail = run(TASK_DONE, 'plan.md', 1, base, '--', 'sh', '-c', 'echo boom; exit 1', cwd=repo)
    assert fail.returncode == 1
    ok = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert ok.returncode == 0, ok.stderr
    ws = workspace(repo)
    assert 'exit: 1' in (ws / 'task-1-tests.log').read_text().splitlines()
    assert 'exit: 0' in (ws / 'task-1-tests-2.log').read_text().splitlines()
    ledger = (ws / 'progress.md').read_text().splitlines()
    assert [line for line in ledger if line.startswith('Task 1:')] == [ledger[-1]]
    assert ledger[-1].endswith('→ OK)')


def test_task_done_refuses_a_task_number_that_is_not_an_id(repo):
    result = run(TASK_DONE, 'plan.md', '../x', head(repo), '--', 'sh', '-c', 'touch ran', cwd=repo)
    assert result.returncode == 2
    assert 'test-run: bad task number' in result.stderr
    assert 'NOT recorded' not in result.stderr
    assert not (repo / 'ran').exists()
    assert not (workspace(repo) / 'progress.md').exists()
```

- [ ] **Step 2: Run them to see them fail.** Run `uv run python build/run_suites.py executing-plans`.
Expected: 3 failures. The first finds no `test-run:` header. The second finds no `exit: 1` line, because the retry overwrote `task-1-tests.log`. The third gets exit 1 from the shell's failed redirect, not 2. Every older test passes.
- [ ] **Step 3: Change `task-done`** to the Interfaces block. Remove the render loop and the direct run, which `test-run` now holds. Its header comment names `test-run` as the script that runs the command and keeps the run. It also says that the first run of a task keeps the name `task-<N>-tests.log`.
- [ ] **Step 4: Run both suites.** Run `uv run python build/run_suites.py subagent-driven-development executing-plans`.
Expected: `suite runs passed`, with 3 more tests in executing-plans. No older test changed.
- [ ] **Step 5: Run the suites under bash 3.2.** Global Constraints (Bash) gives the commands.
- [ ] **Step 6: Run the gates.** `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 7: Commit**

```bash
git add skills/executing-plans/scripts
git commit -m "refactor(skills): task-done runs its command through test-run"
```

### Task 4: The controller runs the tests before every review

**Files:**
- Create: `skills/subagent-driven-development/references/test-run.md`
- Modify: `skills/subagent-driven-development/SKILL.md:95-98` (a diagram node), `:118` (an edge), `:134-135` (the note under the diagram), `:177` (DONE), `:226-227` (Constructing Reviewer Prompts)
- Modify: `skills/subagent-driven-development/references/fix-loop.md:14-16`, `references/file-handoffs.md:37-41`, `references/handling-reports.md:5`, `references/example-workflow.md:29,46,52-54`
- Modify: `skills/subagent-driven-development/implementer-prompt.md:122-124`
- Modify: `specs/baseline/red-baseline-test-run.md` (append the `controller-run` treatment)

**Interfaces:**
- Consumes: Task 2's `test-run` and its `run:` line. Task 5's placeholders `[RUN_FILE]` and `<RUN_FILE>`, by name.

- [ ] **Step 1: Write `references/test-run.md`** with this text:

````markdown
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
````

- [ ] **Step 2: Change `SKILL.md`.** Five replacements.
  - After the line `        "Implementer subagent implements, tests, commits, self-reviews" [shape=box];`, add the line `        "Your test run passes? (references/test-run.md)" [shape=diamond];`.
  - The edge `    "Implementer subagent implements, tests, commits, self-reviews" -> "Write diff file, dispatch task reviewer subagent (./task-reviewer-prompt.md)";` becomes these three lines:

```text
    "Implementer subagent implements, tests, commits, self-reviews" -> "Your test run passes? (references/test-run.md)";
    "Your test run passes? (references/test-run.md)" -> "Write diff file, dispatch task reviewer subagent (./task-reviewer-prompt.md)" [label="yes"];
    "Your test run passes? (references/test-run.md)" -> "Implementer subagent implements, tests, commits, self-reviews" [label="no: fix round"];
```

  The "no" edge goes back to the implementer, not to the fix-dispatch node, because that node leads only to the scoped re-review, and a failing run comes before any review.

  - `doesn't show the round cap or the resume-vs-fresh mechanic; see Fix Rounds.` becomes two lines: `doesn't show the round cap, the resume-vs-fresh mechanic or the test run` and `after each fix; see Fix Rounds.`
  - The DONE paragraph becomes:

```text
**DONE:** First run the task's tests yourself, as [references/test-run.md](references/test-run.md) says; a failing run is a fix round, with no review. Then generate the review package (`<this-skill-dir>/scripts/review-package PLAN_FILE BASE HEAD` — see **File Handoffs** for the BASE rule and for the path the script reports), and dispatch the task reviewer with both paths.
```

  - Under Constructing Reviewer Prompts, the bullet `- Do not ask a reviewer to re-run tests the implementer already ran on the` / `  same code — the implementer's report carries the test evidence` becomes:

```text
- Do not ask a reviewer to re-run tests — your test run (see **DONE**) and
  the implementer's report carry the test evidence
```

- [ ] **Step 3: Measure the body.** Run the command in Global Constraints (Compaction window).
Expected: `19926`, or 500 more than the body at BASE if Task 1 Step 1 found drift. At most `20000` either way.
- [ ] **Step 4: Change the four references and the implementer prompt.**
  - `references/fix-loop.md`: after the paragraph that ends `the cost this cap exists to bound.`, add this paragraph:

```text
A failing test run ([test-run.md](test-run.md)) starts a round too, before any
review: the run file is the round's finding. After every round, run the task's
tests again before the next review. When no task review has run yet, that review
is the full task review, not the scoped re-review.
```

  - `references/file-handoffs.md`: the last two bullets become:

```text
- **Reviewer inputs:** the task reviewer gets four paths — the same brief
  file, the report file, your test run's file ([test-run.md](test-run.md))
  and the review package — plus the global constraints that bind the task.
- Fix dispatches append their fix report (with test results) to the same
  report file and return a short summary; re-reviews read the updated file
  and your new run file.
```

  - `references/handling-reports.md`: at the end of the DONE_WITH_CONCERNS paragraph, after `note them and proceed to review.`, add ` Either way, run the task's tests before the review, as for DONE ([test-run.md](test-run.md)).`
  - `references/example-workflow.md`: both lines `[Run review-package, dispatch task reviewer with the path it reports]` become `[Run test-run with the task's tests: it passes. Run review-package, dispatch task reviewer with both paths]`. After the line `  extracted PROGRESS_INTERVAL constant`, add an empty line and `[Run test-run again: it passes. Run review-package for the amended range]`.
  - `implementer-prompt.md`: the paragraph under `## After Review Findings` becomes:

```text
    If a reviewer finds issues, or the controller's test run fails, and you
    fix them, re-run the tests that cover the amended code and append the
    results to your report file. Your report is still your test evidence:
    the controller runs the task's tests again before each review, and the
    reviewer checks your report against that run.
```

- [ ] **Step 5: Check the old sentences are gone.** Run `/usr/bin/grep -rn "report is the test evidence\|report carries the test evidence\|three paths" skills/subagent-driven-development`.
Expected: no output.
- [ ] **Step 6: Check the anchors.** Run `/usr/bin/grep -rn --include='*.md' 'scripts/test-run' skills/ | /usr/bin/grep -v '<this-skill-dir>/scripts/test-run'`.
Expected: no output.
- [ ] **Step 7: Run the `controller-run` treatment arm.** Build from the sha that `git stash create` prints, into `specs/baseline/red-baseline-test-run/treatment/controller-run/`. Score five reps by the committed rule, append the result to the record, and apply the bar.
- [ ] **Step 8: Run the gates.** `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 9: Commit**

```bash
git add skills/subagent-driven-development specs/baseline/red-baseline-test-run specs/baseline/red-baseline-test-run.md
git commit -m "feat(skills): SDD's controller runs each task's tests before its review"
```

### Task 5: The reviewers read the run

**Files:**
- Modify: `skills/subagent-driven-development/task-reviewer-prompt.md:37` and `:92` (after each `[REPORT_FILE]` line), `:150-162` (the Full Form's `## Tests`), `:315-316` (the Placeholders list)
- Modify: `agents/task-reviewer.md:3` (the description), `:16-18` (the dispatch sentence), `:74-85` (`## Tests`)
- Modify: `skills/subagent-driven-development/re-review-prompt.md:28-29`, `:53-58`
- Regenerate: `runtimes/codex/agents/task-reviewer.toml`, `runtimes/gemini/agents/task-reviewer.md`
- Modify: `specs/baseline/red-baseline-test-run.md` (append the `reviewer-run` treatment)

**Interfaces:**
- Produces: the placeholders `[RUN_FILE]` (task review, both forms) and `<RUN_FILE>` (scoped re-review). Each takes a path that `test-run` printed, or `none: <why>`.

- [ ] **Step 1: Add the run to both forms of `task-reviewer-prompt.md`.** After each of the two lines `    Read the implementer's report: [REPORT_FILE]`, add an empty line and:

```text
    ## The Controller's Test Run

    Read the controller's run of the task's tests: [RUN_FILE]
```

- [ ] **Step 2: Replace `## Tests` in both reviewer surfaces.** In `task-reviewer-prompt.md`'s Full Form, at its four-space indent, and in `agents/task-reviewer.md`, at no indent, the section from `## Tests` through `findings — test output should be pristine.` becomes:

```text
## Tests

The controller ran the task's tests itself after the implementer
reported, and saved that run in the run file the dispatch names. Its
header gives the command, the commit it ran at, whether the working
tree was clean, and the exit status. The full output follows. Read it
and compare it with the implementer's report. A test that the report
claims and the run does not show passing, a count or result that
differs, or a skip or warning that the report leaves out is an
Important finding. A run at a commit other than the diff's head, or on
a dirty working tree, is not evidence for this diff: report it as a gap
for the controller. When the dispatch gives `none: <why>` instead of a
run file, no run exists, and the implementer's report is the only test
evidence.

Do not re-run the suite to confirm the report or the run. Run a test
only when reading the code raises a specific doubt that no existing run
answers — and then a focused test, never a package-wide suite, race
detector run, or repeated/high-count loop. If heavy validation seems
warranted, recommend it in your report instead of running it. If you
cannot run commands in this environment, name the test you would run.

Warnings or other noise in the run's output, or in the implementer's
reported test output, are findings — test output should be pristine.
```

- [ ] **Step 3: Name the run where the inputs are listed.**
  - `task-reviewer-prompt.md`, Placeholders: after the `[REPORT_FILE]` entry, add:

```text
- `[RUN_FILE]` — REQUIRED: the path that
  `<this-skill-dir>/scripts/test-run PLAN_FILE N -- <command>` printed on its
  last line, `run: <path>` (pass the path alone), or `none: <why>` when the
  task has no command to run ([references/test-run.md](references/test-run.md))
```

  - `agents/task-reviewer.md`, description: `expects a task brief, an implementer report, and a diff file in the dispatch.` becomes `expects a task brief, an implementer report, the controller's test run and a diff file in the dispatch.`
  - `agents/task-reviewer.md`, body: `the implementer's report, and a diff file with base/head SHAs.` becomes `the implementer's report, the controller's run of the task's tests, and a diff file with base/head SHAs.` Re-wrap the paragraph at the file's line width.
  - `re-review-prompt.md`: after the line `    its appended fix report, is at <REPORT_FILE>.`, add:

```text
    The controller's run of the task's tests after the fixes is at
    <RUN_FILE>. A test result in the fix report that this run does not
    show is a new Important finding.
```

  - `re-review-prompt.md`, Placeholders: `` `<REPORT_FILE>` is the implementer's report path.`` becomes `` `<REPORT_FILE>` is the implementer's report path; `<RUN_FILE>` is the path `<this-skill-dir>/scripts/test-run` printed on its `run: <path>` line after this round, the path alone, or `none: <why>`.``
- [ ] **Step 4: Regenerate the runtime adapters.** Run `uv run --with pyyaml python build/sync_runtime_assets.py`, then `uv run --with pyyaml python build/sync_runtime_assets.py --check`.
Expected: the first changes `runtimes/codex/agents/task-reviewer.toml` and `runtimes/gemini/agents/task-reviewer.md` only (`git status --short runtimes`), and the second exits 0.
- [ ] **Step 5: Check the shared block and the frontmatter.** Run `uv run python build/check_reviewer_block.py` and `uv run --with pyyaml python build/check_frontmatter.py`.
Expected: both pass.
- [ ] **Step 6: Check the old sentence is gone, and the anchors.** Run `/usr/bin/grep -rn "already ran the tests and reported" skills agents runtimes`.
Expected: no output. Then run the Task 4 Step 6 command. Expected: no output.
- [ ] **Step 7: Run the `reviewer-run` treatment arm** from `git stash create`, as in Task 4 Step 7. Score it, append the result, and apply the bar.
- [ ] **Step 8: Run the gates.** `bash build/run_commit_lints.sh` prints `commit lints passed`. Run `uv run --with pyyaml python build/check_conformance.py`. Expected: it passes.
- [ ] **Step 9: Commit**

```bash
git add skills/subagent-driven-development agents/task-reviewer.md runtimes specs/baseline/red-baseline-test-run specs/baseline/red-baseline-test-run.md
git commit -m "feat(agents): the task reviewer reads the controller's test run"
```

### Task 6: NOTICE lines

**Files:**
- Modify: `NOTICE` (the superpowers section)

- [ ] **Step 1: Extend the task-start and task-done bullet.** After its last sentence, `task-done keeps its own BASE check.`, add:

```text
    task-done runs its command through subagent-driven-development's
    test-run (plan 84), and its ledger line is unchanged.
```

- [ ] **Step 2: Append a bullet** after the bullet that starts `Plan 82 (2026-11-09) adopted upstream v7.0.2's helper fixes`. Use the date of the commit:

```text
  - Plan 84 (<YYYY-MM-DD>) adds subagent-driven-development/scripts/test-run
    for finding 21 of specs/superpowers-drift-spec-v7-0-2.md. It adapts
    executing-plans' task-done, which adapts upstream's scripts (MIT): it
    runs one command and keeps its exit status and full output in the
    plan's workspace, one file for each run. Its header lines, the
    controller's run before every task review, the failing-run fix round
    and the task reviewer's reading of the run are local. The task
    reviewer's Tests section, in agents/task-reviewer.md and
    task-reviewer-prompt.md, keeps upstream's rule not to re-run the
    suite. Its new text, and the new sentences in the implementer
    prompt's After Review Findings paragraph, are local and take no
    upstream text.
```

- [ ] **Step 3: Run the gates.** `uv run python build/check_provenance.py` passes, and `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 4: Commit**

```bash
git add NOTICE
git commit -m "docs: NOTICE lines for plan 84's test-run"
```
