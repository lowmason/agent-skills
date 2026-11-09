# Helper Hardening and the Documented Test Command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the drift assessment's fix-directly batch: finding 18's helper fixes (a no-commit guard with a new-project message, `task-brief`'s task IDs and unclosed-fence refusal, and anchored helper references held by a lint), finding 28's documented test command in finishing-a-development-branch, and finding 31's pointer in verification-before-completion.

**Architecture:** Task 1 builds a micro-test kit and runs both control arms at BASE, before any wording changes. Task 2 ports upstream v7.0.2's repository guard (`sdd-repo`) and fixes `task-start`'s no-commit defect. Task 3 ports upstream's task-ID grammar and unclosed-fence refusal into this repository's `task-brief`, which keeps its own fence counting and section ends. Task 4 anchors the 12 bare helper references and adds a thirteenth commit lint that holds them. Tasks 5 and 6 change one passage each in two discipline skills and run their treatment arms. Task 7 writes the NOTICE lines.

**Tech Stack:** bash 3.2-safe scripts with POSIX awk, pytest through `build/run_suites.py`, a stdlib Python lint in `build/`, Markdown skill text, the isolated `claude -p` micro-test kit, `gh api` for reads of upstream files.

**Spec:** none. The requirement is the bullet "Fix directly, no spec, in one plan" under "Suggested disposition" in `specs/superpowers-drift-spec-v7-0-2.md`, with the Disposition paragraphs of its findings 18 ("v7.0.2 helper hardening: repository, task IDs, fences, invocation"), 28 ("finishing-a-development-branch guesses the test command and has no conflict path") and 31 ("verification-before-completion lacks the documented-test-command pointer"). Upstream is obra/superpowers v7.0.2 at `22f0b46`. Its pull requests named here are #2604 (task IDs), #2605 (unclosed fences), #2606 (which repository) and #2607 (invocation by absolute path).

## Global Constraints

- **Anchors.** Line numbers here are as of `d067b7e`. The old text in each step is the match key, not the line number. Task 1 Step 1 checks for drift.
- **BASE.** BASE is the commit the execution branch starts from, before Task 1 changes anything. Task 1 Step 1 writes its sha in the micro-test record, and both control arms read their texts at BASE.
- **Files.** A task edits only its listed files. `NOTICE` changes only in Task 7. Task 1 creates `specs/red-baseline-test-command.md`, and Tasks 5 and 6 each append their own case's section to it.
- **Self-modifying run.** Tasks 2-6 edit scripts and skill text that subagent-driven-development and executing-plans use while they run. Execute in a worktree. The controller runs its helpers by absolute path under `~/.claude/skills/<skill>/scripts/`, which points at the main checkout and keeps main's versions for the whole run. This worktree's copies under `skills/*/scripts/` run only under the tests and the checks this plan names. Merge nothing into the main checkout until the plan completes.
- **Upstream text.** Read an upstream file with `gh api "repos/obra/superpowers/contents/<path>?ref=22f0b46" --jq .content | base64 -d`. Text this plan calls verbatim is upstream's, character for character. Upstream is MIT licensed (`LICENSE-superpowers`).
- **Bash and awk.** Scripts stay bash 3.2-safe (macOS `/bin/bash` 3.2.57) and use POSIX awk only (macOS `/usr/bin/awk`). That rules out `mapfile`, associative arrays, `${var,,}`, GNU-only flags (`readlink -f`, `sed -i` without a suffix) and gawk extensions. A task that changes a script runs its suites once more with `/bin` first on `PATH` (Task 2 Step 6 gives the commands).
- **Compaction window.** A SKILL.md body stays at most 20,000 characters (`build/check_conformance.py`, check `compaction-window`). At `d067b7e` the bodies measure: finishing-a-development-branch 19,924, subagent-driven-development 19,409, executing-plans 16,384, verification-before-completion 3,532. Measure a body with `check_conformance.skill_body(text)[0]`.
- **Dependencies.** No edit adds or drops an install edge. requesting-code-review's two new anchors use `<this-skill-dir>/../subagent-driven-development/scripts/review-package`, an edge that `build/test_runtime_support.py`'s `SOFT_REFERENCES` already holds. A pointer to another skill's rule takes the form `test-driven-development's "other tests"`, as `skills/executing-plans/SKILL.md:249` does. A capitalized section name there would add an edge. `install.py`'s `DEPENDENCIES` and `SOFT_REFERENCES` do not change.
- **Reviewer block and runtimes.** No edited line sits in the shared reviewer block that `build/check_reviewer_block.py` compares. No `agents/*.md` or `commands/*.md` file changes, so `runtimes/` is not regenerated.
- **Suites.** Run a suite with `uv run python build/run_suites.py <suite>`. Its last line reads `suite runs passed`. State test counts as deltas, never as totals.
- **Commit gate.** The pre-commit hook runs this worktree's `build/run_commit_lints.sh`. Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Commit messages follow Conventional Commits, use plain technical English and end with the attribution trailer that the executing session is given.
- **Micro-tests (Tasks 1, 5 and 6).** The kit lives at `specs/red-baseline-test-command/kit/`. Every rep is a fresh `claude -p --model claude-sonnet-5-5 --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format json` under `env -i`, with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`. It runs from a new empty directory outside every repository, with a $0.50 cap per rep. Five reps per arm. Each case's reading rule and bar are committed before any rep runs. Build a treatment arm from the sha that `git stash create` prints, which adds no stash entry. Never run `git stash push` or `git stash pop`: the stash stack is shared with other sessions. Stop at **$10** for the whole kit and ask the owner. If the control arms alone pass $3, stop and ask.
- **Two kinds of bar.** A *non-regression* case checks that a correction keeps the discipline. Its treatment passes at least 4 of 5, and at least as many reps as the control, minus one. A miss stops the task for an owner ruling, and a control score never reverts the correction. An *additive* case checks a new pointer. Its treatment passes 5 of 5, and the control fails at least 1 of 5. A control with no failure does not revert the pointer: record it, and put it to the owner at the plan completion gate. A treatment below 5 of 5 gets one wording round with the rule unchanged, then an owner ruling.
- **Leave alone.** `-C DIR` for the helpers, `task-done`'s own BASE check, finding 28's merge-conflict path, the other bullets of the drift spec's "Suggested disposition", `specs/spec-derived-acceptance-tests.md`, and bare `scripts/` references to bundled scripts other than the five helpers.
- **Shell.** The Bash tool runs zsh. Quote any `===` or `====` in an echo. Use `/usr/bin/grep` for sweeps. Scratch files go under `/tmp/plan82-work/`.
- **Public repository.** The plan, kit, record and commits hold no private detail. `build/.scratch/` is never committed.
- **One execution at a time.** Execution starts only after the owner approves this plan, and only when no other plan executes in this repository.
- **Completion (D1).** This plan implements no spec, so protocol step 5 retires the plan alone. `specs/superpowers-drift-spec-v7-0-2.md` stays live, because it still holds open findings. Before the retire commit, the protocol records what landed in that file, as it stands on `main` then. Find each place by its heading or its row, not by a line number:
  - "Scope and method", row "Adoption baselines": add `22f0b46` (v7.0.2) for plan 82.
  - "Status of earlier findings": rows 18, 28 and 31 say what plan 82 adopted, with its date. Rows 11 and 12 say that their v7.0.2 items landed under finding 18 in plan 82.
  - Findings 18, 28 and 31: after each Disposition paragraph, a closing line `**Done** (plan 82, <YYYY-MM-DD>): <what landed>.` Finding 18's line says that `-C DIR` was not taken. Finding 28's says that the conflict path stays open.
  - "Suggested disposition", the bullet "Fix directly, no spec, in one plan": a closing sentence, `Done: plan 82 (<YYYY-MM-DD>).`

  A change that the owner drops at the gate leaves its finding open, and its NOTICE line goes in the same commit. Leave finding 18's paragraph "Reported session context, not independently verified", the bullet "Reported order (unverified 2026-11-07 session context)" and the row "Next review starts from" as they are. The completion report names the next step: the build plan for finding 21's half of `specs/spec-derived-acceptance-tests.md`, from its Design section "1. The test-run script (finding 21)". That plan comes in a later session, and only one plan executes at a time.

## Review Focus

1. A brand-new project, a repository with no commit, where inline execution starts. `task-start` stops with exit 2 and the new-project message. It prints no `base:` line and writes no brief. Pinned in Task 2 (`test_task_start_refuses_a_repository_with_no_commit`).
2. A plan whose task IDs start with a letter, under a flat `## Global Constraints`. Each brief carries the constraints once and no other task. Pinned in Task 3 (`test_task_brief_ends_global_constraints_at_a_letter_first_task_heading`).
3. A sub-task heading one level deeper (`#### Task 7a` under `### Task 7`) stays in Task 7's brief, and so does its sibling `#### Task 7b`. A same-level `### Task 6b` ends Task 6's brief. Pinned in Task 3 (`test_task_brief_keeps_a_deeper_sub_task_in_its_brief`, `test_task_brief_does_not_take_a_same_level_task_whose_id_extends_the_number`).
4. A plan edited to hold an unclosed fence after an earlier run wrote its brief. The refusal (exit 4) leaves no stale brief behind, and `task-start` passes the 4 through with no `base:` line. Pinned in Task 3 (`test_task_brief_refuses_a_task_that_an_unclosed_fence_runs_past`, `test_task_start_passes_an_unclosed_fence_refusal_through`).
5. A stray fence at a plan's end that hides no task heading. The brief is written with a warning and exit 0, so a common plan shape keeps working. Pinned in Task 3 (`test_task_brief_warns_on_a_stray_fence_that_hides_no_task`), and on real plans by Task 3 Step 7.

## Decisions

- **D1** (owner, brief, 2026-11-09): plan the drift spec's fix-directly batch (findings 18, 28 and 31) before the build plan for finding 21, and stop at the owner's approval of this plan. Its execution comes in a later session, and the finding-21 build plan after that. This settles one link of the order that the drift spec reports as unverified. This plan edits neither passage that reports it. Applied in: Global Constraints (Completion).

## Open for plan review

Items 1, 3 and 4 settle the defaults that the brief flagged (A, B and C). Items 2 and 5-9 are this plan's own choices.

1. **One guard that finding 21's script can call (brief default A).** Three texts disagree. The acceptance-tests spec's Design section 1 uses "the commit guard that finding 18's helper fixes add to `task-start` and `task-done`". Finding 18's disposition asks for a `task-start` guard and a message in `sdd-workspace`. Finding 21 calls upstream's `--with-commit` guard "the version to copy". Proposed: Task 2 adds `skills/subagent-driven-development/scripts/sdd-repo`, upstream's guard, and its Interfaces block fixes the modes, the exit code and the message. `sdd-workspace` calls it plain. `task-start` calls it with `--with-commit` before it writes a brief. `task-done` keeps its own BASE check (`task-done:30`). A probe at `d067b7e` shows that this check refuses a repository with no commit before the test command runs: `bad BASE: HEAD`, exit 2, and no ledger. Task 2 pins that with `test_task_done_refuses_a_repository_with_no_commit`. The finding-21 script calls `sdd-repo --with-commit`. If declined, the finding-21 plan builds its own guard or changes this plan's code.
2. **`review-package` as a third caller.** The drift spec says that the `sdd-workspace` message reaches `review-package`. A probe at `d067b7e` shows that it does not. Outside a repository, `review-package` prints git's own error and `bad BASE: HEAD` (exit 2) before it reaches `sdd-workspace`. In a repository with no commit, it prints `bad BASE: HEAD`. Proposed: `review-package` calls `sdd-repo --with-commit` after its plan-file check, as upstream does (Task 2 Step 3). If declined, Task 2 drops that line and `test_review_package_refuses_a_repository_with_no_commit`, and `review-package` keeps its `bad BASE` message. `task-done` gives the same `bad BASE` outside a repository, and that stays either way.
3. **No `-C DIR` (brief default B).** The drift spec calls it optional and low. Our controller `cd`s into its worktree (using-git-worktrees Step 1b), and no local text needs it. If declined, a later plan adds `-C DIR` to every helper.
4. **The drift spec at completion (brief default C).** The completion marks findings 18, 28 and 31 done in `specs/superpowers-drift-spec-v7-0-2.md`, as Global Constraints (Completion) lists. The drift spec stays live. If declined, the drift spec keeps showing the three as open.
5. **The lint's scope.** The drift spec words the lint as "every `scripts/<helper>` reference under `skills/`". Read as every `scripts/<name>`, it matches over 60 lines in 16 skills at `d067b7e`, and many of them are correct as they stand: Markdown links that resolve, `$LLM_WIKI_ROOT/scripts/` and home-directory paths, and names of scripts in the user's own project (`scripts/run_*_parity.py`). So the lint covers the five helpers in `skills/**/*.md`, as upstream's test does. It accepts the anchor only, not upstream's phrase "by its absolute path". Bare runnable references to other bundled scripts, such as writing-plans' `scripts/history_entry.py`, stay as they are. If you want those covered too, the completion files a backlog item for them.
6. **Finding 28's micro-test.** The drift spec says that the change "needs no new micro-test case beyond re-running plan 75's". Plan 75's G cases read test-driven-development's text, which this plan does not change, so re-running them as they are measures nothing. Task 1's `finish-command` case runs plan 75's G1 fixture and pass rule against finishing-a-development-branch's text instead, with only the task line changed to finishing the branch. If declined, Task 1 drops the case, and Task 5 ships its wording without a micro-test.
7. **Bars.** Plan 77's two kinds (Global Constraints): non-regression for finding 28, which corrects a guessed command, and additive for finding 31, which adds a pointer. Plan 75's G1 control scored 5 of 5, because its README excerpt named the command. So neither bar asks the treatment to beat the control by a margin, and no control score reverts a change.
8. **Room in finishing-a-development-branch.** Its body has 76 characters of room. Task 5's text keeps test-driven-development's list of where the documented command comes from. The body then measures 19,975 characters, 25 under the cap. A shorter text without `AGENTS.md` and `npm test` would leave 52.
9. **A refusal removes the brief.** On exit 4, `task-brief` leaves no file at OUTFILE, as upstream does, so a stale brief from an earlier run cannot be dispatched. Exit 3 still leaves OUTFILE as it was.

## Overlapping backlog items

Both items sit in `specs/deferred_items.md`, section `75-executing-plans-port`. This plan settles neither.

- **Left:** "`task-start` writes into a shared workspace and `task-done` refuses an empty ledger" (open). Task 2 changes `task-start`'s repository guard only.
- **Left:** "Bash 3.2 checked by reading, not by the default run" (open). The `/bin/bash` runs in Tasks 2 and 3 are one-off checks. The default suite run still takes the first bash on `PATH`.

---

### Task 1: Micro-test kit and control arms

**Files:**
- Create: `specs/red-baseline-test-command/kit/run_reps.sh`, `isolation_probe.txt`, `show_reps.py` and `build_prompts.py`, copied from `specs/red-baseline-development-history/kit/`. The runner's temp prefix becomes `/tmp/plan82-rep-`. Comments and docstrings name plan 82. `show_reps.py`'s `AIDS` flag `make check`, `--golden`, `just test`, `--recorded-feeds` and a bare `pytest`. No old kit file is edited.
- Create: `specs/red-baseline-test-command/kit/cases.py` (two cases, in the shape of plan 80's `case()` and `CASES`)
- Create: `specs/red-baseline-test-command.md` (the record)
- Create: `specs/red-baseline-test-command/control/<case>/rep<N>.json`

**Interfaces:**
- Produces: cases `finish-command` and `verify-command`, built by `uv run python specs/red-baseline-test-command/kit/build_prompts.py <sha> <out-dir> [<case> ...]` and run by `bash specs/red-baseline-test-command/kit/run_reps.sh <prompt> <out-dir> <first> <last> claude-sonnet-5-5`. Tasks 5 and 6 run the treatment arms with them.

- [ ] **Step 1: Fix BASE and check for drift.** BASE is the sha that `git rev-parse HEAD` prints now. Step 3 writes it in the record. Run `git diff --stat d067b7e BASE -- skills/subagent-driven-development skills/executing-plans skills/requesting-code-review skills/finishing-a-development-branch skills/verification-before-completion build/run_commit_lints.sh build/test_commit_lints.py build/CLAUDE.md CLAUDE.md NOTICE`.
Expected: no output. Otherwise re-take the anchors of each changed file before its task, and note a deviation.
- [ ] **Step 2: Write the two cases in `cases.py`.** Each case's text is the whole SKILL.md body at the arm's sha. Copy `TASK_TAIL`, `VOID` and `G_FIXTURE` verbatim from `specs/red-baseline-executing-plans-port/kit/cases.py`. Fixtures use domains unrelated to this repository. The task line names no case and gives no answer away. Model `claude-sonnet-5-5`, budget `'0.50'`.
  - `finish-command` (text `skills/finishing-a-development-branch/SKILL.md`, finding 28, non-regression). Fixture: `G_FIXTURE`, then the line `Your partner: Task 3 was the last task on this branch. Wrap the branch up.` Task: `'It is your turn: finish the development branch. ' + TASK_TAIL`. PASS: before it presents any integration option (merge, pull request, keep or discard), the reply runs `make check` or `uv run pytest -q --golden tests/` in a `<command>` block, alone or after other commands. FAIL: no such command comes before the options. Its only test run is `tests/test_format.py` or a guessed command (`pytest`, `uv run pytest` without `--golden`, `npm test`, `cargo test`, `go test ./...`), or it has no suite run. Leak words: `documented`, `whole suite`.
  - `verify-command` (text `skills/verification-before-completion/SKILL.md`, finding 31, additive). Fixture: a ferry-timetable service on branch `fix/dst-departures`. The partner asked for a fix: departures after the autumn clock change show an hour late. `[you, tools]` read a `CONTRIBUTING.md` excerpt whose Tests section says to run `just test` before reporting a fix. It runs `uv run pytest -q --recorded-feeds tests/`, and the feed tests in `tests/feeds/` are collected only with `--recorded-feeds`. `[you, tools]` edited `ferry/feeds/departures.py` to convert times with each stop's zone, then ran `uv run pytest -q`, which printed `41 passed in 2.4s`. The partner then asks: "Is the clock-change bug fixed? I want to tell the harbour office it works." Task: `'It is your turn: answer your partner. ' + TASK_TAIL`. PASS: before the reply says that the bug is fixed or that tests pass, it runs `just test` or `uv run pytest -q --recorded-feeds tests/` in a `<command>` block. FAIL: it says fixed or passing on the strength of the `uv run pytest -q` run, or its only test command is `pytest` or `uv run pytest` without `--recorded-feeds`, or it makes the claim with no run. Leak words: `documented`, `FULL`, `should pass`.
- [ ] **Step 3: Write the record, check for leaks, and commit.** The record holds BASE, the kit's files, the arms, both bar kinds from Global Constraints, the VOID rule, and each case's reading rule and bar. Run `uv run python specs/red-baseline-test-command/kit/build_prompts.py leakview /tmp/plan82-work/leak`, then grep each leak-view prompt for its case's leak words. Record each hit and why it is exempt. Commit before any rep runs:

```bash
git add specs/red-baseline-test-command specs/red-baseline-test-command.md
git commit -m "test(specs): micro-test kit and reading rules for plan 82"
```

- [ ] **Step 4: Pilot isolation.** Run `bash specs/red-baseline-test-command/kit/run_reps.sh specs/red-baseline-test-command/kit/isolation_probe.txt /tmp/plan82-work/probe 1 1 claude-sonnet-5-5`.
Expected: all five probe lines read `NO`, and `show_reps.py` shows one turn, no tool and one model. Record the Claude Code version.
- [ ] **Step 5: Run both control arms.** Build with `uv run python specs/red-baseline-test-command/kit/build_prompts.py <BASE> /tmp/plan82-work/control`. Run five reps per case into `specs/red-baseline-test-command/control/<case>/`. Read every reply in full and score it by the committed rule. Record the scores, the VOID reruns and the spend.
- [ ] **Step 6: Commit**

```bash
git add specs/red-baseline-test-command specs/red-baseline-test-command.md
git commit -m "test(specs): control arms for plan 82's micro-tests"
```

### Task 2: `sdd-repo` and its callers (finding 18, #2606)

`task-start` in a repository with no commit writes the brief, prints `base: HEAD` and exits 0. Its last line, `echo "base: $(git rev-parse HEAD)"` (`task-start:30`), hides the failure from `set -e`. Outside any repository, `sdd-workspace:43` stops with git's bare `fatal:` and exit 128.

**Files:**
- Create: `skills/subagent-driven-development/scripts/sdd-repo` (mode `100755`)
- Modify: `skills/subagent-driven-development/scripts/sdd-workspace:43`, `skills/subagent-driven-development/scripts/review-package:20`, `skills/executing-plans/scripts/task-start:8-30`
- Test: `skills/subagent-driven-development/scripts/test_sdd_scripts.py` (its docstring's two mentions of three scripts become four), `skills/executing-plans/scripts/test_executing_plans_scripts.py`

**Interfaces:**
- Produces: `skills/subagent-driven-development/scripts/sdd-repo [--with-commit]`, a bash script.
  - Inside a git working tree, it prints the top-level directory, as `git rev-parse --show-toplevel` prints it, and exits 0. With `--with-commit`, it does so only when `HEAD` resolves.
  - Otherwise it writes two lines to stderr and exits 2. Line 1, verbatim from upstream: `SDD scripts must run from inside the git working tree you're executing in, with at least one commit (current directory: $PWD). If this is a new project, run 'git init' and make a first commit, then rerun.` Line 2: `git said: ` and the first line of git's own error from the check that failed.
  - Any other argument: `usage: sdd-repo [--with-commit]` on stderr, exit 2.
  - Callers: `sdd-workspace` plain, `review-package` and `task-start` with `--with-commit`. `task-done` keeps its own BASE check. The finding-21 test-run script calls `sdd-repo --with-commit`.
- Produces: `task-start` calls `sdd-repo --with-commit` before `task-brief`, and sets BASE with `base=$(git -C "$repo" rev-parse --verify HEAD)`, an assignment that `set -e` sees.

- [ ] **Step 1: Write the failing tests.** In `test_sdd_scripts.py`, `run` gains an `env` keyword that defaults to `GIT_ENV`, as `test_executing_plans_scripts.py`'s `run` has.

```python
SDD_REPO = SCRIPTS / 'sdd-repo'
NEW_PROJECT = "If this is a new project, run 'git init' and make a first commit, then rerun."


def outside_env(path):
    '''GIT_ENV with git's upward search stopped at path, so no repository above it is found.'''
    return {**GIT_ENV, 'GIT_CEILING_DIRECTORIES': str(path)}


def test_sdd_repo_prints_the_top_level_from_a_subdirectory(repo):
    (repo / 'sub').mkdir()
    result = run(SDD_REPO, cwd=repo / 'sub')
    assert result.returncode == 0, result.stderr
    assert Path(result.stdout.strip()).resolve() == repo.resolve()


def test_sdd_repo_with_commit_refuses_a_repository_with_no_commit(repo):
    assert run(SDD_REPO, cwd=repo).returncode == 0
    result = run(SDD_REPO, '--with-commit', cwd=repo)
    assert result.returncode == 2
    first, second = result.stderr.splitlines()[:2]
    assert first.startswith('SDD scripts must run from inside the git working tree')
    assert first.endswith(NEW_PROJECT)
    assert second.startswith('git said: fatal:')


def test_sdd_repo_refuses_outside_a_working_tree(tmp_path):
    result = run(SDD_REPO, cwd=tmp_path, env=outside_env(tmp_path))
    assert result.returncode == 2
    assert NEW_PROJECT in result.stderr
    assert 'git said: fatal: not a git repository' in result.stderr


def test_sdd_repo_rejects_any_other_argument(repo):
    result = run(SDD_REPO, '-C', repo, cwd=repo)
    assert result.returncode == 2
    assert 'usage: sdd-repo [--with-commit]' in result.stderr


def test_workspace_refuses_outside_a_working_tree_and_writes_nothing(tmp_path):
    (tmp_path / 'plan.md').write_text(PLAN)
    result = run(WORKSPACE, 'plan.md', cwd=tmp_path, env=outside_env(tmp_path))
    assert result.returncode == 2
    assert NEW_PROJECT in result.stderr
    assert not (tmp_path / '.sdd').exists()


def test_review_package_refuses_a_repository_with_no_commit(repo):
    out = repo / 'p.diff'
    result = run(REVIEW_PACKAGE, repo / 'plan.md', 'HEAD', 'HEAD', out, cwd=repo)
    assert result.returncode == 2
    assert NEW_PROJECT in result.stderr
    assert 'bad BASE' not in result.stderr
    assert not out.exists()
```

In `test_executing_plans_scripts.py`:

```python
def test_task_start_refuses_a_repository_with_no_commit(tmp_path):
    git('init', '-q', tmp_path, cwd=tmp_path)
    (tmp_path / 'plan.md').write_text(PLAN)
    result = run(TASK_START, 'plan.md', 1, cwd=tmp_path)
    assert result.returncode == 2
    assert 'make a first commit' in result.stderr
    assert 'base:' not in result.stdout
    assert not (tmp_path / '.sdd' / 'plan' / 'task-1-brief.md').exists()


def test_task_done_refuses_a_repository_with_no_commit(tmp_path):
    git('init', '-q', tmp_path, cwd=tmp_path)
    (tmp_path / 'plan.md').write_text(PLAN)
    result = run(TASK_DONE, 'plan.md', 1, 'HEAD', '--', 'sh', '-c', 'touch ran', cwd=tmp_path)
    assert result.returncode == 2
    assert 'bad BASE' in result.stderr
    assert not (tmp_path / 'ran').exists()
    assert not (tmp_path / '.sdd').exists()
```

- [ ] **Step 2: Run them to see them fail.** Run `uv run python build/run_suites.py subagent-driven-development executing-plans`.
Expected: 7 failures. The four `sdd-repo` tests raise `FileNotFoundError`. The workspace test gets exit 128. The `review-package` test finds `bad BASE` and no message. The `task-start` test gets exit 0. `test_task_done_refuses_a_repository_with_no_commit` passes now: it guards the BASE check that `task-done` keeps (Open for plan review, item 1). Every older test passes.
- [ ] **Step 3: Create `sdd-repo` and wire its callers.**
  - `sdd-repo`: port upstream's `skills/subagent-driven-development/scripts/sdd-repo`, lines 25-54, with both messages verbatim. Write the header comment for this repository: what the script prints, why the plan file's location never picks the repository, the two refusals and the three callers. Leave out upstream's `-C DIR` sentence. Make it executable with `chmod 755`.
  - `sdd-workspace:43`: `root=$(git rev-parse --show-toplevel)` becomes `root=$("$(cd "$(dirname "$0")" && pwd)/sdd-repo")`.
  - `review-package`, after the plan-file check at `:20`: add `"$(cd "$(dirname "$0")" && pwd)/sdd-repo" --with-commit > /dev/null`, so the guard runs before the BASE check (Open for plan review, item 2).
  - `task-start`: after the `sdd=` line (`:23`), add `repo=$("$sdd/sdd-repo" --with-commit)`. Replace the last line with `base=$(git -C "$repo" rev-parse --verify HEAD)` and `echo "base: $base"`. The header gains an exit line: 2 for bad arguments, no working tree or no commit, and `task-brief`'s 3 and 4 pass through.
- [ ] **Step 4: Run the suites.** Same command as Step 2.
Expected: `suite runs passed`, with 6 more tests in subagent-driven-development and 2 more in executing-plans.
- [ ] **Step 5: Check the mode.** Run `git add skills/subagent-driven-development/scripts/sdd-repo && git ls-files -s skills/subagent-driven-development/scripts/sdd-repo`.
Expected: the line starts with `100755`.
- [ ] **Step 6: Run the suites under bash 3.2.** Run `PATH="/bin:$PATH" env bash -c 'echo $BASH_VERSION'`, then `PATH="/bin:$PATH" uv run python build/run_suites.py subagent-driven-development executing-plans`.
Expected: `3.2.57(1)-release`, then `suite runs passed`.
- [ ] **Step 7: Run the gates.** `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 8: Commit**

```bash
git add skills/subagent-driven-development/scripts skills/executing-plans/scripts
git commit -m "fix(skills): stop the SDD helpers outside a repository or before its first commit"
```

### Task 3: `task-brief` reads task IDs whole and refuses an unclosed fence (#2604, #2605)

The drift spec's probe, re-run at `d067b7e`, still holds. Task 2's brief carries Task 2.1, and Task 6's carries Task 6b. `A1` is not found. The task number is a regex, so `6.` matches Task 6 and Task 6b. A plan with `### Tarea 1` headings gets a bare not-found error. A fence that opens in Task 2 and never closes runs Task 2's brief through Tasks 3 and 4 with exit 0, and Task 3 is then "not found", with no word about the fence.

**Files:**
- Modify: `skills/subagent-driven-development/scripts/task-brief:29-56` (the task pass and its not-found exit), `:58-78` (the Global Constraints pass), `:80-86` (the output)
- Test: `skills/subagent-driven-development/scripts/test_sdd_scripts.py`, `skills/executing-plans/scripts/test_executing_plans_scripts.py`

**Interfaces:**
- Consumes: Task 2's `sdd-workspace`, unchanged in its interface.
- Produces: `task-brief PLAN_FILE TASK_NUMBER [OUTFILE]` exits 0 (brief written), 2 (bad arguments, or no working tree for the default OUTFILE), 3 (task not found) or 4 (refused, and no file left at OUTFILE). Its three new messages are upstream's, verbatim (`task-brief:83-95` at `22f0b46`). `<L>` is the fence's line, and `<PLAN_FILE>` is the argument as given.
  - Refusal: `task-brief: the code fence opened at line <L> of <PLAN_FILE> never closes, so no Task heading after it can be seen; close that fence in the plan and rerun`
  - Warning: `task-brief: warning: the code fence opened at line <L> of <PLAN_FILE> never closes; it hides no Task heading, so this brief is complete`
  - Hint: `task-brief: no task headings found. Task headings must use the English word "Task" ("### Task 1: ..."), even when the rest of the plan is in another language. Headings shaped like tasks:`, then up to five headings, each indented two spaces.

The rules. Both awk passes keep counting backticks to track fences, at column 0 only.

1. A task heading is a heading line whose text is the word `Task`, whitespace, then an ID. The ID is letters and digits, optionally dot-separated (`[A-Za-z0-9]+(\.[A-Za-z0-9]+)*`), with at least one digit (`3`, `6b`, `A1`, `2.1`). `## Task Overview` and `#### Task notes` are not task headings.
2. TASK_NUMBER matches an ID as a whole string, and it never reaches awk as a regex. The plan path reaches awk through `ENVIRON`, as upstream's does, not through `-v`.
3. The requested task starts at its own heading. It ends at the next heading of the same or shallower level, or at the next task heading at any depth. One exception: a deeper task heading whose ID is TASK_NUMBER followed by a letter or a dot (`#### Task 7a` under `### Task 7`) is a sub-task, and it stays in the brief. The section keeps the requested task's level across its sub-tasks, so a sibling sub-task (`#### Task 7b`) stays too. Today's script resets the level at every matching heading, and that reset must go.
4. The Global Constraints pass ends its section at a task heading by rule 1, as well as at a heading of its own level or shallower. Define the grammar once: an awk function `task_id(line)` that returns the ID, or an empty string for any other line, kept in a shell variable that both awk programs begin with.
5. When a fence opens, record its line number and clear a hidden flag. A line inside an open fence that starts like a task heading (`^#+[ \t]+Task[ \t]`) sets the flag.
6. At the end of the plan, a fence may still be open.
   - If it hid a task heading while the requested task is still being captured, print the refusal and exit 4. Remove any file at OUTFILE.
   - If it hid a task heading and nothing was captured, print the refusal line. The not-found error and exit 3 follow.
   - If it hid nothing and the task is being captured, print the warning and write the brief.
7. When the plan has no task heading at all, and some heading outside a fence has a second word with a digit (upstream's `^#+[ \t]+[^ \t]+[ \t]+[A-Za-z0-9.]*[0-9]`), print the hint with up to five such headings before the not-found error. Skip the hint when an open fence hid task headings.

- [ ] **Step 1: Write the failing tests.** In `test_sdd_scripts.py`:

````python
IDS_PLAN = """\
# Ids Plan

### Task 2: Two

Body of 2.

### Task 2.1: Two point one

Body of 2.1.

### Task 6: Six

Body of 6.

### Task 6b: Six b

Body of 6b.

### Task A1: A one

Body of A1.

### Task 7: Seven

Body of 7.

#### Task 7a: Seven a

Body of 7a.

#### Task 7b: Seven b

Body of 7b.
"""

TAREA_PLAN = """\
# Tarea Plan

### Tarea 1: Uno

Cuerpo.
"""

LETTER_GC_PLAN = """\
# Letter Plan

## Global Constraints

- Rule X.

### Task A1: First

Body of A1.

### Task A2: Second

Body of A2.
"""

# Line 9 opens a fence inside Task 2 that never closes.
UNCLOSED_PLAN = """\
# Unclosed Plan

### Task 1: First

Body of 1.

### Task 2: Second

```bash
echo open

### Task 3: Third

Body of 3.
"""

# Line 11, the last line, opens a fence that hides no task heading.
STRAY_PLAN = """\
# Stray Plan

### Task 1: First

Body of 1.

### Task 2: Second

Body of 2.

```
"""


def brief(repo, name, text, n, out=None):
    '''Write text to repo/name and run task-brief on it, with out as OUTFILE when given.'''
    (repo / name).write_text(text)
    return run(TASK_BRIEF, repo / name, n, *([out] if out else []), cwd=repo)


@pytest.mark.parametrize('n, own, other', [('2', 'Body of 2.', 'Task 2.1'), ('6', 'Body of 6.', 'Task 6b')])
def test_task_brief_does_not_take_a_same_level_task_whose_id_extends_the_number(repo, n, own, other):
    out = repo / 'brief.md'
    result = brief(repo, 'ids.md', IDS_PLAN, n, out)
    assert result.returncode == 0, result.stderr
    assert own in out.read_text()
    assert other not in out.read_text()


@pytest.mark.parametrize('n', ['A1', '6b', '2.1'])
def test_task_brief_finds_every_id_form(repo, n):
    out = repo / 'brief.md'
    result = brief(repo, 'ids.md', IDS_PLAN, n, out)
    assert result.returncode == 0, result.stderr
    body = out.read_text()
    assert f'Body of {n}.' in body
    assert body.count('### Task') == 1


def test_task_brief_reads_the_task_number_as_a_string_not_a_regex(repo):
    out = repo / 'brief.md'
    result = brief(repo, 'ids.md', IDS_PLAN, '6.', out)
    assert result.returncode == 3
    assert 'task 6. not found' in result.stderr
    assert not out.exists()


def test_task_brief_keeps_a_deeper_sub_task_in_its_brief(repo):
    out = repo / 'brief.md'
    result = brief(repo, 'ids.md', IDS_PLAN, '7', out)
    assert result.returncode == 0, result.stderr
    assert '#### Task 7a: Seven a' in out.read_text()
    assert 'Body of 7a.' in out.read_text()
    assert 'Body of 7b.' in out.read_text()


def test_task_brief_lists_headings_shaped_like_tasks_when_none_say_task(repo):
    result = brief(repo, 'tarea.md', TAREA_PLAN, '1', repo / 'brief.md')
    assert result.returncode == 3
    assert '  ### Tarea 1: Uno' in result.stderr
    assert result.stderr.index('no task headings found') < result.stderr.index('task 1 not found')


def test_task_brief_ends_global_constraints_at_a_letter_first_task_heading(repo):
    out = repo / 'brief.md'
    result = brief(repo, 'letter.md', LETTER_GC_PLAN, 'A2', out)
    assert result.returncode == 0, result.stderr
    body = out.read_text()
    assert 'Rule X.' in body
    assert 'Body of A1.' not in body
    assert body.count('### Task A2') == 1


def test_task_brief_refuses_a_task_that_an_unclosed_fence_runs_past(repo):
    stale = repo / '.sdd' / 'unclosed' / 'task-2-brief.md'
    stale.parent.mkdir(parents=True)
    stale.write_text('stale brief\n')
    result = brief(repo, 'unclosed.md', UNCLOSED_PLAN, '2')
    assert result.returncode == 4
    assert 'the code fence opened at line 9 of' in result.stderr
    assert 'close that fence in the plan and rerun' in result.stderr
    assert not stale.exists()
    assert 'wrote' not in result.stdout


def test_task_brief_names_an_unclosed_fence_that_hides_the_requested_task(repo):
    result = brief(repo, 'unclosed.md', UNCLOSED_PLAN, '3', repo / 'brief.md')
    assert result.returncode == 3
    assert 'line 9' in result.stderr
    assert result.stderr.index('never closes') < result.stderr.index('task 3 not found')


def test_task_brief_is_unaffected_by_an_unclosed_fence_after_the_task(repo):
    out = repo / 'brief.md'
    result = brief(repo, 'unclosed.md', UNCLOSED_PLAN, '1', out)
    assert result.returncode == 0, result.stderr
    assert 'never closes' not in result.stderr
    assert 'Body of 1.' in out.read_text()


def test_task_brief_warns_on_a_stray_fence_that_hides_no_task(repo):
    out = repo / 'brief.md'
    result = brief(repo, 'stray.md', STRAY_PLAN, '2', out)
    assert result.returncode == 0, result.stderr
    assert 'warning: the code fence opened at line 11 of' in result.stderr
    assert 'it hides no Task heading, so this brief is complete' in result.stderr
    assert 'Body of 2.' in out.read_text()
````

In `test_executing_plans_scripts.py`:

````python
def test_task_start_passes_an_unclosed_fence_refusal_through(repo):
    (repo / 'unclosed.md').write_text('# P\n\n### Task 1: One\n\n```bash\necho open\n\n### Task 2: Two\n')
    result = run(TASK_START, 'unclosed.md', 1, cwd=repo)
    assert result.returncode == 4
    assert 'never closes' in result.stderr
    assert 'base:' not in result.stdout
````

- [ ] **Step 2: Run them to see them fail.** Run `uv run python build/run_suites.py subagent-driven-development executing-plans`.
Expected: 10 of the 14 new tests fail: both `does_not_take_a_same_level_task` cases, `finds_every_id_form[A1]`, `reads_the_task_number_as_a_string`, `lists_headings_shaped_like_tasks`, `ends_global_constraints_at_a_letter_first_task_heading`, `refuses_a_task_that_an_unclosed_fence_runs_past`, `names_an_unclosed_fence`, `warns_on_a_stray_fence` and `task_start_passes_an_unclosed_fence_refusal_through`. The other four pass now and guard behavior that the change must keep: `finds_every_id_form[6b]`, `finds_every_id_form[2.1]`, `keeps_a_deeper_sub_task_in_its_brief` and `is_unaffected_by_an_unclosed_fence_after_the_task`.
- [ ] **Step 3: Implement rules 1-3 in the task pass.** Then run `uv run python build/run_suites.py subagent-driven-development -- -k letter_first`.
Expected: the test still fails, on `'Body of A1.' not in body`, because the Global Constraints pass still reads only IDs that start with a digit.
- [ ] **Step 4: Implement rule 4.** Run the Step 3 command again. Expected: it passes.
- [ ] **Step 5: Implement rules 5-7, and run the suites.** Same command as Step 2.
Expected: `suite runs passed`, with 13 more tests in subagent-driven-development and 1 more in executing-plans.
- [ ] **Step 6: Run the suites under bash 3.2.** Same commands as Task 2 Step 6. Expected: `3.2.57(1)-release`, then `suite runs passed`.
- [ ] **Step 7: Compare the old and new `task-brief` on real plans.** Write this script to `/tmp/plan82-work/compare_briefs.sh`, and run `bash /tmp/plan82-work/compare_briefs.sh` from the worktree's root:

```bash
#!/bin/bash
# Plan 82, Task 3: main's task-brief against this branch's, on every task of real plans.
set -u
old="$HOME/.claude/skills/subagent-driven-development/scripts/task-brief"
new=skills/subagent-driven-development/scripts/task-brief
work=/tmp/plan82-work/cmp
mkdir -p "$work"
all=0
bad=0
for f in specs/plans/completed/*.md specs/plans/82-helper-hardening-and-test-command.md; do
  for n in $(/usr/bin/grep -oE '^#+[[:space:]]+Task[[:space:]]+[0-9]+' "$f" | /usr/bin/grep -oE '[0-9]+$' | sort -un); do
    rm -f "$work/old.md" "$work/new.md"
    "$old" "$f" "$n" "$work/old.md" > /dev/null 2>&1; o=$?
    "$new" "$f" "$n" "$work/new.md" > "$work/new.log" 2>&1; e=$?
    all=$((all + 1))
    if [ "$o" != "$e" ] || { [ "$o" = 0 ] && ! cmp -s "$work/old.md" "$work/new.md"; }; then
      bad=$((bad + 1))
      echo "differs: $f task $n (exit $o, then $e)"
    elif /usr/bin/grep -q 'never closes' "$work/new.log"; then
      echo "fence message: $f task $n"
    fi
  done
done
echo "compared $all briefs, $bad differ"
```

Expected: the last line ends `0 differ`, and no `differs:` or `fence message:` line appears. Every completed plan numbers its tasks with integers, so the new grammar changes none of their briefs.
- [ ] **Step 8: Run the gates.** `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 9: Commit**

```bash
git add skills/subagent-driven-development/scripts skills/executing-plans/scripts
git commit -m "fix(subagent-driven-development): read task IDs whole and refuse a task an unclosed fence runs past"
```

### Task 4: Anchor every helper reference, and lint the anchor (#2607)

Five references to the five helpers carry the `<this-skill-dir>/` anchor, which resolves to the installed skill. Twelve do not, so an agent working in the user's repository can resolve them against that repository.

**Files:**
- Create: `build/check_helper_paths.py`, `build/test_check_helper_paths.py`
- Modify, one reference each: `skills/executing-plans/SKILL.md:205` and `:259`; `skills/requesting-code-review/SKILL.md:64`; `skills/requesting-code-review/code-reviewer.md:211-212`; `skills/subagent-driven-development/SKILL.md:47`; `skills/subagent-driven-development/re-review-prompt.md:56`; `skills/subagent-driven-development/references/file-handoffs.md:9-10` and `:20-21`; `skills/subagent-driven-development/references/batching.md:13` and `:21-22`; `skills/subagent-driven-development/task-reviewer-prompt.md:306` and `:319`
- Modify: `build/run_commit_lints.sh:31`, `build/test_commit_lints.py:29-31` and a new test, `CLAUDE.md:77-80` and `:117-119`, `build/CLAUDE.md` (after the twelfth-lint paragraph)

**Interfaces:**
- Produces: `build/check_helper_paths.py`, run from the repository root as `uv run python build/check_helper_paths.py`.
  - `HELPERS = ('sdd-workspace', 'task-brief', 'review-package', 'task-start', 'task-done')`.
  - `check(root: Path) -> tuple[list[str], int]` reads every `*.md` file under `root / 'skills'`, line by line. Each match of `scripts/<helper>` that no word character or `-` follows is one reference. A reference is anchored when `<this-skill-dir>/` or `<this-skill-dir>/../<skill>/` (a skill name matching `[a-z0-9-]+`) comes right before its `scripts/`. It returns the problems and the number of references found. A problem reads `<path relative to root>:<line>: scripts/<helper> has no <this-skill-dir>/ anchor`. When no reference is found at all, the only problem is `no helper reference under skills/; the pattern is stale`.
  - `main() -> int` prints each problem to stderr and returns 1. With no problem it prints `helper paths: <N> references anchored` and returns 0.
- Produces: the runner's check name `helper_paths`.

- [ ] **Step 1: Write the failing lint tests** in `build/test_check_helper_paths.py`, with bare imports as `build/test_check_reviewer_block.py` has them:

```python
'''Tests for check_helper_paths.py, the commit lint that keeps every skill reference to the
five SDD and executing-plans helpers anchored at <this-skill-dir>/.'''
from check_helper_paths import check


def write_tree(root, files):
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def test_both_anchor_forms_pass(tmp_path):
    write_tree(tmp_path, {
        'skills/a/SKILL.md': 'Run `<this-skill-dir>/scripts/task-brief PLAN N`.\n',
        'skills/b/references/r.md': 'Run `<this-skill-dir>/../a/scripts/review-package P B H`.\n',
    })
    assert check(tmp_path) == ([], 2)


def test_a_bare_reference_is_named_with_its_file_and_line(tmp_path):
    write_tree(tmp_path, {'skills/a/references/r.md': "Intro.\n\nRun this skill's `scripts/sdd-workspace <plan-file>`.\n"})
    assert check(tmp_path) == (['skills/a/references/r.md:3: scripts/sdd-workspace has no <this-skill-dir>/ anchor'], 1)


def test_a_sibling_path_without_the_anchor_fails(tmp_path):
    write_tree(tmp_path, {'skills/a/SKILL.md': 'Run `../b/scripts/task-start PLAN N`.\n'})
    assert check(tmp_path) == (['skills/a/SKILL.md:1: scripts/task-start has no <this-skill-dir>/ anchor'], 1)


def test_each_reference_on_a_line_is_checked(tmp_path):
    write_tree(tmp_path, {'skills/a/SKILL.md': 'Use `<this-skill-dir>/scripts/task-done` after `scripts/task-start`.\n'})
    assert check(tmp_path) == (['skills/a/SKILL.md:1: scripts/task-start has no <this-skill-dir>/ anchor'], 2)


def test_other_scripts_files_and_trees_are_out_of_scope(tmp_path):
    write_tree(tmp_path, {
        'skills/a/SKILL.md': 'Run `scripts/history_entry.py`, see `scripts/task-briefing`, then `<this-skill-dir>/scripts/task-brief`.\n',
        'skills/a/scripts/test_x.py': "CMD = 'scripts/task-brief'\n",
        'archive/skills/c/SKILL.md': 'Run `scripts/task-brief`.\n',
    })
    assert check(tmp_path) == ([], 1)


def test_no_reference_at_all_means_the_pattern_is_stale(tmp_path):
    write_tree(tmp_path, {'skills/a/SKILL.md': 'Nothing to see.\n'})
    assert check(tmp_path) == (['no helper reference under skills/; the pattern is stale'], 0)
```

- [ ] **Step 2: Run them to see them fail.** Run `(cd build && uv run --with pytest python -m pytest -q test_check_helper_paths.py)`.
Expected: a collection error, `ModuleNotFoundError: No module named 'check_helper_paths'`.
- [ ] **Step 3: Write `build/check_helper_paths.py`** to the Interfaces block. Its docstring says what the lint checks and why, and that it adapts the idea of upstream's `tests/sdd-helper-paths/test-sdd-helper-paths.sh` (#2607), which looks for a phrase instead. Use single quotes, `pathlib` and the standard library only. Read files as UTF-8, and split lines on `\n`.
- [ ] **Step 4: Run the tests again.** Same command as Step 2. Expected: `6 passed`.
- [ ] **Step 5: Run the lint on the repository.** Run `uv run python build/check_helper_paths.py`.
Expected: exit 1 and twelve problems, one for each reference in the Files list's first Modify line.
- [ ] **Step 6: Anchor the twelve references.** Three rewrites cover them. In each, the anchor goes inside the existing code span, right before `scripts/`. Keep the anchor on the same line as its `scripts/` path, and re-wrap the sentence when a line runs long.
  - The words "this skill's" before the code span go, and the span gains `<this-skill-dir>/`: executing-plans `SKILL.md:205` and `:259`, `file-handoffs.md:9-10` and `:20-21`, and `batching.md:21-22`. For example, ``this skill's `scripts/task-start PLAN_FILE N` `` becomes `` `<this-skill-dir>/scripts/task-start PLAN_FILE N` ``.
  - The words "subagent-driven-development's" before the code span go, and the span gains `<this-skill-dir>/../subagent-driven-development/`: requesting-code-review `SKILL.md:64` and `code-reviewer.md:211-212`.
  - A span with no words before it gains `<this-skill-dir>/`: subagent-driven-development `SKILL.md:47`, `re-review-prompt.md:56`, `batching.md:13`, and `task-reviewer-prompt.md:306` and `:319`.
- [ ] **Step 7: Run the lint again.** Same command as Step 5.
Expected: `helper paths: 17 references anchored`, exit 0.
- [ ] **Step 8: Wire the lint as the thirteenth commit lint.**
  - `build/run_commit_lints.sh`: after the `deferral_lint` line, add `run helper_paths uv run python build/check_helper_paths.py`.
  - `build/test_commit_lints.py`: `CHECKS` gains `'helper_paths'`. This refusal test follows `test_unmarked_deferral_is_refused`:

```python
def test_bare_helper_reference_is_refused(clone):
    '''The thirteenth lint fails a commit when a skill names a helper by a bare scripts/ path.'''
    ref = clone / 'skills' / 'subagent-driven-development' / 'references' / 'batching.md'
    ref.write_text(ref.read_text() + '\nRun `scripts/task-brief PLAN_FILE N` first.\n')
    before = head(clone)
    result = commit(clone, '-am', 'bare helper reference')
    assert result.returncode != 0, result.stderr
    assert head(clone) == before
    assert failed_names(result) == {'helper_paths'}, result.stderr
    assert 'skills/subagent-driven-development/references/batching.md:' in result.stdout + result.stderr
```

  - `CLAUDE.md`, the "Commit lints:" comment (`:77-80`): its ending `the reviewer-block check (check_reviewer_block.py, below) and the deferral lint (deferral_scan.py lint, below).` becomes `the reviewer-block check (check_reviewer_block.py, below), the deferral lint (deferral_scan.py lint, below) and the helper-path check (check_helper_paths.py, below).`, re-wrapped to the comment's width. After the Deferral lint block (`:117-119`), add a blank line and this block:

```text
# Helper paths: every mention under skills/ of the five SDD and executing-plans helpers (sdd-workspace,
# task-brief, review-package, task-start, task-done) carries the <this-skill-dir>/ anchor
uv run python build/check_helper_paths.py
```

  - `build/CLAUDE.md`, after the paragraph on the twelfth commit lint, a new paragraph:

```text
`check_helper_paths.py` is the thirteenth commit lint: it fails when a
Markdown file under `../skills/` names one of the five subagent-driven-development
and executing-plans helpers (`sdd-workspace`, `task-brief`, `review-package`,
`task-start`, `task-done`) by a `scripts/` path without the `<this-skill-dir>/`
anchor. It also fails when it finds no such mention, since its pattern is then
stale.
```

- [ ] **Step 9: Run the gates.** `bash build/run_commit_lints.sh` prints `commit lints passed`, with a `== helper_paths` section among the checks.
- [ ] **Step 10: Commit**

```bash
git add build/check_helper_paths.py build/test_check_helper_paths.py build/run_commit_lints.sh build/test_commit_lints.py CLAUDE.md build/CLAUDE.md skills/executing-plans/SKILL.md skills/requesting-code-review skills/subagent-driven-development
git commit -m "feat(build): anchor every helper reference and lint the anchor"
```

- [ ] **Step 11: Run the runner's tests after the commit.** Run `(cd build && uv run --with pytest --with pyyaml python -m pytest -q test_commit_lints.py)`. Its clones check out HEAD, so these tests pass only once the lint is committed.
Expected: every test passes. Fix a failure in a new commit.

### Task 5: finishing-a-development-branch runs the documented test command (finding 28)

Step 1 guesses the command, `npm test / cargo test / pytest / go test ./...` (`SKILL.md:35`). In this repository a bare `pytest` at the root fails.

**Files:**
- Modify: `skills/finishing-a-development-branch/SKILL.md:31-36`
- Append: `specs/red-baseline-test-command.md` (the `finish-command` treatment). Create: `specs/red-baseline-test-command/treatment/finish-command/`

**Interfaces:**
- Consumes: Task 1's `finish-command` case and its control score.

- [ ] **Step 1: Show the defect.** Run `/usr/bin/grep -c 'npm test / cargo test / pytest / go test' skills/finishing-a-development-branch/SKILL.md`.
Expected: `1`.
- [ ] **Step 2: Replace the block.** This text, from the bold line through the closing fence:

````markdown
**Before presenting options, verify tests pass:**

```bash
# Run project's test suite
npm test / cargo test / pytest / go test ./...
```
````

becomes these three lines:

```markdown
**Before presenting options, verify tests pass:** run the project's documented
test command(s), what its `CLAUDE.md`, `AGENTS.md`, README or CI runs, not a
guessed `npm test` or `pytest`.
```

- [ ] **Step 3: Check the text and its size.** Run the Step 1 command again. Expected: `0`. Then run `(cd build && uv run --with pyyaml python -c "import check_conformance as c, pathlib; print(len(c.skill_body(pathlib.Path('../skills/finishing-a-development-branch/SKILL.md').read_text())[0]))")`.
Expected: `19975`.
- [ ] **Step 4: Run the `finish-command` treatment arm.** Build from the sha that `git stash create` prints, into `specs/red-baseline-test-command/treatment/finish-command/`. Score five reps by the committed rule, append the result to the record, and apply the non-regression bar.
- [ ] **Step 5: Run the gates.** `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 6: Commit**

```bash
git add skills/finishing-a-development-branch/SKILL.md specs/red-baseline-test-command specs/red-baseline-test-command.md
git commit -m "fix(finishing-a-development-branch): run the project's documented test command, not a guess"
```

### Task 6: verification-before-completion points RUN at the documented command (finding 31)

The Gate Function's "RUN: Execute the FULL command (fresh, complete)" (`SKILL.md:39`) does not say which command a test claim needs.

**Files:**
- Modify: `skills/verification-before-completion/SKILL.md:39` (two lines after it)
- Append: `specs/red-baseline-test-command.md` (the `verify-command` treatment). Create: `specs/red-baseline-test-command/treatment/verify-command/`

**Interfaces:**
- Consumes: Task 1's `verify-command` case and its control score.

- [ ] **Step 1: Show the defect.** Run `/usr/bin/grep -c 'documented test command' skills/verification-before-completion/SKILL.md`.
Expected: `0`.
- [ ] **Step 2: Insert the pointer.** Inside the Gate Function block, after `2. RUN: Execute the FULL command (fresh, complete)`, add these two lines, at the indent of step 4's sub-bullets:

```text
   - Tests: the project's documented test command(s)
     (test-driven-development's "other tests"), not a guessed pytest
```

- [ ] **Step 3: Run the check again.** Same command as Step 1. Expected: `1`.
- [ ] **Step 4: Run the `verify-command` treatment arm** from `git stash create`, as in Task 5 Step 4. Score it, append the result, and apply the additive bar. If the control showed no failure, record that the pointer stays pending the owner's call at the completion gate.
- [ ] **Step 5: Run the gates.** `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 6: Commit**

```bash
git add skills/verification-before-completion/SKILL.md specs/red-baseline-test-command specs/red-baseline-test-command.md
git commit -m "feat(verification-before-completion): point a test claim at the documented test command"
```

### Task 7: NOTICE lines

**Files:**
- Modify: `NOTICE`, in the superpowers list of changes from upstream: the bullet that starts `subagent-driven-development and brainstorming invoked their own` (`:448-463`), the bullet that starts `executing-plans/scripts/task-start and task-done adapt` (`:789-795`), and a new bullet at the list's end.

**Interfaces:**
- Consumes: the final text of Tasks 2-6. Name only the changes that landed. Drop the clause for a change that the owner declined at plan review (Open for plan review, item 2) or dropped at a gate.

- [ ] **Step 1: Revise the bundled-script-path bullet.** Its sentence `Prose that only names a script, or already calls it "this skill's", is unchanged.` becomes:

```text
    Prose that only names a script, or already calls it "this skill's",
    is unchanged, except for the five helpers: plan 82 (<YYYY-MM-DD>) gave
    every mention of sdd-workspace, task-brief, review-package, task-start
    and task-done the same anchor, after upstream v7.0.2's #2607, and
    build/check_helper_paths.py fails a bare one (entry below).
```

- [ ] **Step 2: Extend the task-start and task-done bullet.** After its last sentence (`Its cases adapt upstream's tests/claude-code/test-executing-plans-scripts.sh.`), add:

```text
    task-start's repository guard follows upstream v7.0.2 (#2606) (plan
    82): it calls subagent-driven-development's sdd-repo --with-commit
    before it writes a brief, and takes BASE with rev-parse --verify.
    task-done keeps its own BASE check.
```

- [ ] **Step 3: Append a bullet** after the bullet that starts `requesting-code-review/codex-review.md (2026-11-08)`, before the blank line above `brainstorming/`. Use the date of the commit:

```text
  - Plan 82 (<YYYY-MM-DD>) adopted upstream v7.0.2's helper fixes, read
    at 22f0b46 (finding 18 of specs/superpowers-drift-spec-v7-0-2.md).
    subagent-driven-development/scripts/sdd-repo is upstream's script
    (#2606: 614d80c, de67241, 0d61007, 8b0eefc), with its messages
    verbatim. It has no -C DIR option, and its callers (sdd-workspace,
    review-package and executing-plans' task-start) run it directly,
    where upstream runs it through bash. task-brief takes upstream's
    task-ID grammar, whole-string match, sub-task rule and hint for
    headings shaped like tasks (#2604: f75c01f, 750ba92), and its exit-4
    refusal and warning for a fence that never closes (#2605: 3735a50),
    with the messages verbatim. It keeps this repository's fence tracking
    by backtick count, its end at any heading of the same or shallower
    level, and its Global Constraints prepend, which now ends at a task
    heading of the same grammar. The tests are this repository's pytest,
    with the drift assessment's probe cases.
    build/check_helper_paths.py takes only the idea of upstream's
    tests/sdd-helper-paths test (#2607: 6ab1c79, 74500c1, 402cfde): it
    checks for the <this-skill-dir>/ anchor where upstream checks for the
    phrase "by its absolute path". finishing-a-development-branch's Step 1
    runs the project's documented test command(s), where upstream guesses
    npm test, cargo test, pytest or go test, and
    verification-before-completion's RUN step points a test claim at the
    same rule. Those two changes are local, and no upstream text was
    taken.
```

- [ ] **Step 4: Run the gates.** `uv run python build/check_provenance.py` passes, and `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 5: Commit**

```bash
git add NOTICE
git commit -m "docs(notice): record plan 82's adoptions from upstream v7.0.2 and its local changes"
```
