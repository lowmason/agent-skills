# Mutant Screen Runs Implementation Plan

**Status: COMPLETE (2026-11-22)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md, or specs/completed/deferred_items.md once archived

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Owner gate.** No execution starts until PR #237 and PR #235 have merged and no other machinery stream runs. The owner orders this plan and the E3 pass. (Status on 2026-11-19: #237 merged at `29d744f` and #235 at `4a367fb`. Plan 103's execution, planned in #240, edits finishing-a-development-branch and using-git-worktrees, so it is a machinery stream too. The owner orders it with this plan and the E3 `/cc-guide files` pass.)

**Goal:** Give `mutant-run` a screen mode that runs only the mutants that no earlier run of the task caught. The SDD implementer uses it, the controller's full runs stay the only proof, and a `Mutant-step:` commit trailer records what the mutant step caused.

**Architecture:** `mutant-run --screen` reads the task's earlier run files in the workspace. It carries each patch whose sha256 an earlier run under the same command caught, and runs every other patch, the baseline and the revert as a full run does. A screen writes `task-<N>-screen[-<K>].log`, a name that `task-done` and every reviewer surface never read. The implementer guide, the implementer prompt, the controller's `test-run.md` and executing-plans' `SKILL.md` say who screens and when, and when the trailer goes on a commit. A tool-rep micro-test covers the behavior-shaping text. Its control arms run on today's text with the new script before any text changes.

**Tech Stack:** bash (macOS 3.2 compatible), git, pytest JUnit XML; Markdown skill text; pytest suites that drive the scripts as subprocesses; a `claude -p` tool-rep micro-test kit; the repo's commit lints (`build/run_commit_lints.sh`).

**Spec:** `specs/mutant-screen-runs.md` (approved 2026-11-19; Design 1 step 2 corrected by the owner in PR #239, `651e0cd`). Its Terms, Design, Constraints and Verification are authoritative. Read it in full before Task 1.

## Global Constraints

### Base and execution

- **Execution base.** Cut the execution worktree from `main` after this plan's PR merges. The spec cites lines as of `008d062`. This plan cites the same lines, which `fce19d3` still holds for every file it edits. Before Task 1, run `git diff --stat fce19d3 HEAD -- skills/subagent-driven-development skills/executing-plans agents NOTICE`. Any output means a file changed after planning: re-read each cited line before a task quotes it, and ledger a `Ruling:` for any task text that no longer fits.
- **Shared files.** Plan 103 also edits `NOTICE` and `build/suites.toml`. Both changes are appends, so whichever plan merges second keeps the other's entry.
- **Self-modifying plan.** This plan edits `mutant-run`, the SDD references and the implementer prompt, and executing-plans' `SKILL.md`, which execute it. `~/.claude/skills/` and `~/.claude/agents/` are symlinks into the main checkout. Execute in a worktree. Call the controller tooling by absolute path through those symlinks, with the worktree as the working directory: `~/.claude/skills/subagent-driven-development/scripts/<name>` under subagent-driven-development, and `~/.claude/skills/executing-plans/scripts/task-start` and `task-done` under executing-plans. Do not merge this branch into the main checkout before the plan completes.
- **This plan's own mutant step.** Main's copies carry today's mutant step. Tasks 1 and 2 have focused pytest commands over code they change, so they run that step with main's `mutant-run` (full runs, no `--screen`), and their commits carry no `Mutant-step:` trailer: the trailer rule ships with this plan and binds only later executions. The worktree's `mutant-run` is only the code under test. Every other task records `none: <why>` for its mutant run.
- **Scope fence.** These are out of bounds. When the only fix crosses one, stop and ask the owner.
  - `skills/executing-plans/scripts/task-done` keeps its code (spec, Design 4). Only its test file changes.
  - The reviewer surfaces do not change: `agents/task-reviewer.md`, `skills/subagent-driven-development/task-reviewer-prompt.md`, `re-review-prompt.md`, both `references/final-review.md` files, and the shared reviewer block. `runtimes/` does not change. Design 4's fallback sentence is not part of this plan (D12).
  - `skills/subagent-driven-development/SKILL.md`, `references/fix-loop.md`, `file-handoffs.md` and `batching.md` do not change.
  - A call without `--screen` behaves and writes as it does today (spec, Design 1). The mutants file's format does not change.
  - Plan 93's and plan 97's records and kits under `specs/baseline/` do not change.
  - Shipping implementer, controller or inline text whose treatment arm still misses a bar after two revision rounds (D3).
  - Any micro-test batch that would take the plan's micro-test spend past **$90** (D2).
- **Leave alone.** `specs/findings/mutant-cost-benefit.md` (untracked in the main checkout) and `~/.cache/agent-skills/scratch/mutant-eval/` name other repositories. Never read them into a fixture, copy them or commit them. The spec holds every number this plan needs.
- **Privacy.** agent-skills is public. Fixtures, the record, commit messages and test names cite totals and agent-skills' own plans only (spec, Constraints).
- **Owner stops under subagent-driven-development.** An implementer cannot ask the owner. Where a step says "stop and ask the owner", the implementer reports BLOCKED with the quoted results and the running spend. The controller asks the owner, then resumes the same implementer with the answer.
- **Cross-skill references** use bare skill names, never a `superpowers:` namespace.

### Scripts

- **Bash 3.2.** `mutant-run` runs under macOS `/bin/bash` 3.2.57: no `declare -A`, `mapfile`, `${v,,}`, `|&` or negative indexes, and `${a[@]+"${a[@]}"}` for a possibly empty array. Keep `file_sha256`, the awk readers and the perl start-up (spec, Constraints). Each script task runs its suite a second time with `PATH="/bin:$PATH"`.
- **No new script, no new skill file.** The screen is a mode of `mutant-run` (spec, Constraints), so `install.py`'s `DEPENDENCIES` and the orphan-file lint do not change.
- **Tests** drive each script as a subprocess, as the existing suites do: single quotes, f-strings, 4-space indentation, stdlib plus pytest. Run them through `build/run_suites.py`. State count changes as deltas, never totals.
- **The header text (D6).** `mutant-run`'s header documents the screen mode only: what a screen reads, what it runs, what it writes and its exit status. The new text names no caller of `--screen`. It does not use the words proof, evidence, review, reviewer or task-done, or the phrase "full run". The existing "Callers:" paragraph stays as it is. The control arm reads this header, so a rule there would reach the control (spec, Verification).

### File formats

These forms are pinned. Every task that writes or reads one uses them exactly.

**Call.** `<this-skill-dir>/scripts/mutant-run [--screen] PLAN_FILE TASK_NUMBER BASE -- TEST_COMMAND [ARGS...]`
- `--screen` counts only as the first argument. After it, the arguments are checked as today.
- A bad call prints `usage: mutant-run [--screen] PLAN_FILE TASK_NUMBER BASE -- TEST_COMMAND [ARGS...]` and exits 2.
- Without `--screen`, nothing changes: the same checks, run file name, numbering, header, sections, stdout and exit codes.

**Screen file.** `task-<N>-screen.log` for the task's first screen, `task-<N>-screen-<K>.log` for screen K = 2, 3 and so on: the smallest K whose file does not exist. Screens and full runs number on their own. Header, in this order (D5):

```text
mutant-run: Task <N>, screen <K>
command: <as today>
head: <full sha>
base: <full sha>
tree: clean
result: caught <c>, survived <s>, invalid <i>
screen: carried <m> of <total> from earlier runs
note: reversed <patch file name>, left applied by a killed run
revert: <as today>
```

- `<total>` is the number of patches in the run. `<c>` counts each carried mutant as caught.
- A carried mutant's line: `mutant <K>: CAUGHT exit - sha256 <hex> carried: <file name of the earlier run> tests: <that line's tests>`. Every other mutant line is as today.
- `--- tests ---` joins this run's catches and the carried catches, in K order, as today's code builds it.
- `--- output: mutant <K> ---` exists only for a mutant whose command ran.
- A failing baseline writes the header through `note:` with `result: baseline failed, exit <n>`, no `screen:` line and no `revert:` line, then `--- output: baseline ---` and its output, and exits 3.
- stdout: the `result:` line, the `screen:` line, each mutant line, the `revert:` line, then `run: <path>` last.
- Exit status as a full run's, with a carried mutant counted as caught.
- The "already in HEAD" check still refuses the whole run with exit 2, before the baseline (spec, Design 1 step 2, as corrected).

**Earlier catches (D4).** A screen reads the earlier run files of its own task in the workspace: `task-<N>-mutants.log`, `task-<N>-mutants-<K>.log`, `task-<N>-screen.log` and `task-<N>-screen-<K>.log`, where K is digits with no leading zero, as `task-done` reads run numbers (`task-done:189-203`). Any other file name is skipped.
- **Command.** A file counts only when its command equals this screen's rendered command. A file's command is the text from line 2 up to the line before its first `head: ` line, less the leading `command: `. It can span lines.
- **Lines.** Only lines inside the file's `--- mutants ---` section count: from that line to the next line that starts with `--- `. A line counts when it starts `mutant <K>: CAUGHT ` and has no ` carried: ` field. Its key is the hex after `sha256 `. Its tests are the text after ` tests: `. A file with no `--- mutants ---` section, such as a failing baseline's, gives nothing.
- **Newest.** For each sha256, the catch comes from the newest file that has one: a full run outranks a screen, and a higher number outranks a lower one in the same series.
- **Carry or run.** For each patch in K order: compute its sha256, then make the checks that come before the test command, as today. A patch that fails the test-file check or `git apply --check` is INVALID with today's reasons. A patch that passes them and whose sha256 has an earlier catch is carried: no marker, no apply, no command. Every other patch runs as in a full run. The baseline and the revert always run.

**Trailer** (spec, Design 5). A commit that answers the mutant step ends its message with one line for each cause, in the same last paragraph as any other trailer:

```text
Mutant-step: task <N> survivor <K>
Mutant-step: task <N> input shape
Mutant-step: task <N> revert
Mutant-step: task <N> review
```

### Micro-test

- **Method.** writing-skills' micro-test method, main's copy, as plan 97 applied it (`specs/plans/completed/97-change-reverted-mutant.md:105`). Five scored reps per fixture per arm, each in a fresh context. The record's fixtures, bars, readings, VOID rule and spend stop are committed before any scored rep, and no reading is added after reps are seen. A person reads every verdict by hand from the rep's full output. `grade.py` prints reading aids, never verdicts. A text or script under test enters a prompt or the skill copy only through `git show <sha>:<path>`, never through `~/.claude/`.
- **Arms** (spec, Verification). Both arms run Task 2's `mutant-run`, with `--screen` in its usage line and header. The control arm reads today's text at the execution base. The treatment arm reads the text at Task 7's commit, or at the newest revision commit (Task 8).
- **Roles, models and caps (D2).** Implementer and controller reps run `--model sonnet` with `--max-budget-usd 1.50`. Inline reps run `--model opus` with `--max-budget-usd 4`, because the owner runs Inline execution on Opus (owner, 2026-10-19). Before each batch: running total + (reps in the batch × cap) ≤ $90. A batch that fails the check is the spend fence. The micro-test total is the sum of `total_cost_usd` over every rep, probe and pilot. Every dispatch that runs reps carries the running total.
- **Isolation (D7).** Each rep is a fresh `claude -p` from its own folder under `/private/tmp/msr104/`, outside every repository, with the tools Bash, Read, Edit and Write and no Agent tool. Reps run one at a time. Each rep gets its own `HOME` and `TMPDIR` inside its folder. Login works through a `Library/Keychains` link to the real one, as in plan 100's `specs/baseline/red-baseline-handoff-rerun/kit/run_rep.sh:99-137`. The reps' Python is the venv `/private/tmp/msr104-venv/`, built from the repository root with the dev Python of `build/versions.toml` and pytest, so `uv.toml`'s freeze date applies (plan 97's `/tmp/mt-venv` is gone). The flags are plan 97's (`specs/baseline/red-baseline-change-reverted-mutant/impl-kit/run_reps.sh:95-99`): `--tools Bash,Read,Edit,Write --allowedTools Bash,Read,Edit,Write`; `env -i` with only `HOME`, `USER`, `LOGNAME`, `PATH`, `SHELL`, `TMPDIR` and `LANG`, plus `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`; `--strict-mcp-config --setting-sources "" --disable-slash-commands --no-session-persistence --output-format stream-json --verbose`. The `--settings` JSON denies `Read(//Users/**)`, `Edit(//Users/**)`, `Write(//Users/**)`, `Read(~/Library/**)`, `Edit(~/Library/**)` and `Write(~/Library/**)`, and the tools `ListAgents`, `SendMessage`, `PushNotification` and `RemoteTrigger` by name, and sets `"syncClaudeAiSkills": false`.
- **While reps run,** no session messages a rep or subscribes to one (Channel 7, rule (a)). A batch runs in the background with its output in a log, and the caller waits for the completion notice. A wait never uses `pgrep -f`.
- **Record.** `specs/baseline/red-baseline-mutant-screen-runs.md`, with the kit under `specs/baseline/red-baseline-mutant-screen-runs/kit/` and rep outputs under `implementer/`, `controller/` and `inline/` beside it. Raw streams, parked homes and unscrubbed copies stay under `~/.cache/agent-skills/scratch/plan104/` and are never committed.

### Commits and lints

- The commit lints pass on every commit. Never use `--no-verify`. Use `/usr/bin/grep` or `git grep` for sweeps, since `grep` here is a shell function.
- Every mention of `mutant-run` under `skills/` keeps its `<this-skill-dir>/` anchor, or `<this-skill-dir>/../subagent-driven-development/` from executing-plans (`build/check_helper_paths.py`).

## Review Focus

1. An earlier run whose command spans lines, such as `sh -c` with a newline inside its script. A screen must compare the whole command, so a command that differs only after its first line carries nothing. Pinned by Task 2's `test_mutant_run_screen_compares_a_multi_line_command_whole`.
2. A test command whose output prints a line shaped like a caught mutant. Only the `--- mutants ---` section counts, so no output line can carry a patch. Pinned by Task 2's `test_mutant_run_screen_reads_catches_from_the_mutants_section_only`.
3. Task IDs that share a prefix or hold a dot (1, 10, 1.1). Task 1's screen reads no run file of task 10 or task 1.1, even when the bytes of a patch match. Pinned by Task 2's `test_mutant_run_screen_reads_only_its_own_tasks_runs`.
4. A workspace that holds an earlier run with a failing baseline, or files whose names look like run files but are not (`task-1-screen-01.log`, `task-1-mutants-x.log`). The screen skips them with no error, and its own numbering ignores them. Pinned by Task 2's `test_mutant_run_screen_skips_a_failed_baseline_and_look_alike_names`.
5. Two patches with the same bytes. Each is carried from the one catch of that sha256. Pinned by Task 2's `test_mutant_run_screen_carries_every_patch_whose_sha_was_caught`.

## Decisions

None from the brief: the spec holds every owner decision, and the owner picked approach B. The lines below are planner defaults. Each settles an item that the spec or the brief leaves to the plan. The owner approved the plan, these defaults included, at plan review. The question was "Do you approve plan 104 with its defaults D1–D13?", and the owner answered "Approved".

- **D1** (planner default; owner approved it as written at plan review, 2026-11-19; brief default 1): every role's reps are tool reps in fixture repositories, with the real `mutant-run`, built from plan 97's `impl-kit`. Three bars need real actions: the `--screen` calls, the screen file's path and counts, and the trailer in a real commit. Applied in: Global Constraints, Micro-test; Task 3.
- **D2** (planner default; owner approved it as written at plan review, 2026-11-19; brief default 2): seven fixtures, five scored reps per fixture per arm, so 70 scored reps. Implementer and controller reps run on Sonnet with a $1.50 cap. Inline reps run on Opus with a $4 cap. The ceiling is $90. The estimate for both arms is $30 to $60: plan 97's Sonnet tool reps cost about $0.08 to $0.11, these reps make more runs, and the 20 Opus reps cost several times more. Applied in: Global Constraints, Micro-test; Tasks 3, 4, 8.
- **D3** (planner default; owner approved it as written at plan review, 2026-11-19; brief default 3, amended): the results get no separate owner stop. A bar that the treatment arm misses gets at most two revision rounds of the text, as in plan 97 (`specs/plans/completed/97-change-reverted-mutant.md:461`). A bar still missed after round two stops the execution and asks the owner. Otherwise the results go to the plan-completion gate. The brief's default stopped at the first miss. This follows plan 97, which gave the wording two chances first. A revision reruns every fixture whose prompt or skill copy it changed. `mutants.md` is in every role's copy, so a revision there reruns all seven fixtures, about $20 to $30 a round. A second round can therefore reach the $90 fence, which stops the run and asks the owner. Applied in: Global Constraints; Task 8.
- **D4** (planner default; owner approved it as written at plan review, 2026-11-19): the newest earlier catch. A full run outranks a screen, and a higher number outranks a lower one in the same series. This needs no timestamp, and it picks the newest file in every case the tools can reach: a screen runs a patch only when no earlier run under its command caught that patch, so a screen's catch never follows a full run's catch of the same bytes. Applied in: File formats; Task 2.
- **D5** (planner default; owner approved it as written at plan review, 2026-11-19): the `screen:` line sits right after `result:`, before `note:` and `revert:`. A failing baseline writes no `screen:` line, as it writes no `revert:` line today. stdout prints the `screen:` line after the `result:` line. Applied in: File formats; Task 1.
- **D6** (planner default; owner approved it as written at plan review, 2026-11-19; brief trap 3): the header documents the mode only, as Global Constraints, Scripts, says. Applied in: Tasks 1, 2, 3.
- **D7** (planner default; owner approved it as written at plan review, 2026-11-19; brief constraint 2): each rep runs alone, in its own folder, with its own `HOME` and `TMPDIR`, and the runner parks the folder outside `/private/tmp` when the rep ends. This closes the `for`-loop `Read(~/**)` gap for `~` paths (`specs/baseline/red-baseline-marimo-notebook-block.md:381`). It probably also keeps reps off the peer-session list, as plan 100's own-`HOME` reps stayed off it. The post-hoc path audit still voids a rep that names the real home. The alternative was plan 97's real `HOME` with a deny rule and a void on any home path. That keeps the gap open and leaves reps on the peer list. Applied in: Global Constraints, Micro-test; Task 3.
- **D8** (planner default; owner approved it as written at plan review, 2026-11-19): the reading of the bar "a test that the implementer adds after the task's first run gets a new mutant patch". The test meets it when a `Mutant` line names it as a target, and that line's patch did not exist at the first run. The survivor or invalid mutant that the test answers also meets it. The spec's reason for the bar is a caught mutant re-aimed at a new test, whose carried `tests:` list never shows the new test (Design 3). A survivor runs again in the next screen, so its catch shows the new test. Applied in: Task 3 (the record's readings).
- **D9** (planner default; owner approved it as written at plan review, 2026-11-19): how the bars bind. A bar binds on each fixture that forces its event, at 4 or more of 5 treatment reps. On a fixture where the event happens only in some reps, the record counts the reps that reach it and the reps that pass, and each miss there goes to the completion gate. The control meets a bar on a fixture when it meets it in 4 or more of 5 reps there. The drop (spec, Verification) applies sentence by sentence. A sentence is dropped only when the control meets the bar on every fixture whose event that sentence governs. A sentence that no fixture's event exercises stays, and the record lists it as untested wording. For example, B2's fix-round sentence is exercised by I2, and its step 7 sentence by I3. Today's fix-round text already says "Write one" (`implementer-prompt.md:151-152`), so the control may meet B2 on I2 and not on I3. Applied in: Tasks 3, 4, 5, 6, 7, 8.
- **D10** (planner default; owner approved it as written at plan review, 2026-11-19): the controller's treatment arm always runs. The controller's skill copy holds `mutants.md`, which Task 5 changes, so a controller rep can read the implementer's new rule. Applied in: Task 8.
- **D11** (planner default; owner approved it as written at plan review, 2026-11-19): the inline agent's final-review fix pass learns the trailer from one sentence in executing-plans' `SKILL.md`, because `references/final-review.md` is a reviewer surface that does not change. No fixture reaches that fix pass, so the record lists that sentence as untested wording. Applied in: Task 7.
- **D12** (planner default; owner approved it as written at plan review, 2026-11-19): Design 4's fallback becomes a deferred watch item beside the spec's re-measure item (Design 6). This plan's own reviewers read no screen file, so the fallback cannot fire inside it. Applied in: Task 9.
- **D13** (planner default; owner approved it as written at plan review, 2026-11-19): the fixtures, their domains and their seeded states, as Task 3 pins them. Applied in: Task 3.
- **D14** (owner, gate, 2026-11-19): the owner orders the three machinery streams as plan 104, then plan 103's execution, then the E3 `/cc-guide files` pass. The owner's answer was "104 → 103 → E3 (Recommended)", to the question "Run in this order: plan 104 now and alone, then plan 103's execution, then the E3 `/cc-guide files` pass?". Applied in: Owner gate.
- **D15** (owner, handoff, 2026-11-19): execute plan 104 with subagent-driven-development; the owner's answer was "Subagent." Applied in: Execution handoff.

## Backlog items this plan touches

- `specs/deferred_items.md`, "Parallel micro-test reps share the scratch folder" (ticked by plan 100) and "The next micro-test kit still copies `credential_expires_at`" (ticked). This kit keeps both fixes, with no-model tests (Task 3).
- "Detect or block a peer message to a rep that has tools" (open). This kit voids a rep whose stream holds a peer origin and gives each rep its own `HOME`. It runs no real-delivery test and no probe, so the item stays open, and the record says so.
- "Account identity reaches the isolated micro-test runs" (open). The kit scrubs identity forms as plan 97's did. The item stays open.

## File map

| File | Change | Task |
|---|---|---|
| `skills/subagent-driven-development/scripts/mutant-run` | `--screen`, the screen file; the carry | 1, 2 |
| `skills/subagent-driven-development/scripts/test_sdd_scripts.py` | new and updated tests | 1, 2 |
| `skills/executing-plans/scripts/test_executing_plans_scripts.py` | `task-done` ignores a screen | 1 |
| `specs/baseline/red-baseline-mutant-screen-runs.md` | the record: rules, then results | 3, 4, 8, 9 |
| `specs/baseline/red-baseline-mutant-screen-runs/kit/`, `implementer/`, `controller/`, `inline/` | the kit, fixtures, rep outputs | 3, 4, 8 |
| `build/suites.toml` | register the kit's tests | 3 |
| `skills/subagent-driven-development/references/mutants.md`, `implementer-prompt.md` | who screens; new patches; the trailer | 5 |
| `skills/subagent-driven-development/references/test-run.md` | the controller's part, unless the control meets its bar | 6 |
| `skills/executing-plans/SKILL.md` | the inline agent's part; the fix-pass trailer | 7 |
| `NOTICE` | one entry under the superpowers changes | 9 |

Callers of `mutant-run` that stay as they are, each read at `fce19d3`: `task-done`'s comments (`:20-23`, `:164`, `:187`); `implementer-prompt.md:195`; `re-review-prompt.md:122` and `task-reviewer-prompt.md:514` (reviewer surfaces); `references/batching.md:27`, `file-handoffs.md:22` and `:61`, and `fix-loop.md:25` (the controller's full runs); the comments of `sdd-repo:23`, `sdd-workspace:18` and `test-run:32`, `:73`.

---

### Task 1: `mutant-run --screen` writes a screen file

**Files:**
- Modify: `skills/subagent-driven-development/scripts/mutant-run` (argument check `:182-191`, `next_run_file` `:657-664`, `write_header` `:672-680`, the failing-baseline branch `:682-697`, stdout `:870-871`, the header comment `:1-179`)
- Test: `skills/subagent-driven-development/scripts/test_sdd_scripts.py` (the `mutant-run` section from `:926`)
- Test: `skills/executing-plans/scripts/test_executing_plans_scripts.py` (beside `test_task_done_accepts_a_run_that_mutant_run_wrote`, `:940`)

**Interfaces:**
- Produces: the call, the screen file's name, numbering and header, and stdout, as File formats pins them. In this task a screen still runs every patch, so its `screen:` line reads `carried 0 of <total>`. Task 2 adds the carry.

- [x] **Step 1: Write the failing tests**

In `test_sdd_scripts.py`:

```python
def test_mutant_run_screen_writes_a_screen_file(calc):
    p1 = make_mutant(calc, 1, *A)
    result = run(MUTANT_RUN, '--screen', 'plan.md', 1, head_sha(calc), '--', *PYTEST, cwd=calc, env=PY_ENV)
    assert result.returncode == 0, result.stdout + result.stderr
    lines = mutant_lines(calc, 'task-1-screen.log')
    assert lines[0] == 'mutant-run: Task 1, screen 1'
    assert lines[5:8] == [
        'result: caught 1, survived 0, invalid 0',
        'screen: carried 0 of 1 from earlier runs',
        'revert: none: no file outside the tests and the project config changed',
    ]
    assert mutant_line(lines, 1).startswith(f'mutant 1: CAUGHT exit 1 sha256 {patch_sha(p1)} tests: ')
    assert no_mutant_run_file(calc)
    out = result.stdout.splitlines()
    assert out[:2] == ['result: caught 1, survived 0, invalid 0', 'screen: carried 0 of 1 from earlier runs']
    assert out[-1] == 'run: ' + str(run_file(calc, 'task-1-screen.log'))
```

Also add, each with mutant A unless it says otherwise:
- `test_mutant_run_numbers_screens_and_full_runs_apart`: a full run, a screen, a screen, then a full run write `task-1-mutants.log` (`mutant-run: Task 1, run 1`), `task-1-screen.log` (`screen 1`), `task-1-screen-2.log` (`screen 2`) and `task-1-mutants-2.log` (`run 2`).
- `test_mutant_run_full_run_runs_every_patch_beside_a_screen` (spec test 8): after a screen that caught mutant 1, a full run writes `task-1-mutants.log` with `mutant-run: Task 1, run 1`. Its mutant 1 line starts `mutant 1: CAUGHT exit 1 `, it has a `--- output: mutant 1 ---` section, and no line starts with `screen:` or holds ` carried: `.
- `test_mutant_run_screen_stops_on_a_failing_baseline` (spec test 6, second half): with `['sh', '-c', 'exit 1']`, exit 3. `task-1-screen.log` has `lines[0] == 'mutant-run: Task 1, screen 1'`, `lines[5] == 'result: baseline failed, exit 1'` and `lines[6] == '--- output: baseline ---'`, and no line starts with `screen:`.
- `test_mutant_run_screen_stops_when_a_mutant_is_already_in_head`: as `test_mutant_run_stops_when_a_mutant_is_already_in_head`, with `--screen`. Exit 2, the stderr names `task-1-mutant-1.patch`, and no `task-1-screen*.log` exists.

Update `test_mutant_run_rejects_bad_arguments` and `test_mutant_run_requires_a_base` to expect `usage: mutant-run [--screen] PLAN_FILE TASK_NUMBER BASE -- TEST_COMMAND [ARGS...]`. Add three argv cases to the first: `['--screen']`, `['--screen', 'plan.md', 1, 'HEAD', '--']` and `['plan.md', 1, 'HEAD', '--screen', 'true']`.

In `test_executing_plans_scripts.py` (spec test 9), with a helper `calc_task(repo) -> str` that commits `calc.py` and `test_calc.py` (`CALC`, `TEST_CALC`), runs `SDD_WORKSPACE`, writes mutant 1 (`return a + b` to `return a - b`) as `test_task_done_accepts_a_run_that_mutant_run_wrote` does, calls `write_mutants(repo, [1])`, and returns BASE, the HEAD before its commit. Every run below passes that BASE:
- `test_task_done_refuses_an_older_full_run_beside_a_newer_screen`: a full run at H1 exits 0. `commit_work(repo)` makes H2. A screen at H2 exits 0. `task-done` exits 4, its stderr holds `the mutant run is at <H1>, not HEAD <H2>`, and `recorded(repo)` is False.
- `test_task_done_records_a_clean_full_run_beside_a_newer_screen_with_a_survivor`: a full run on `PYTEST` exits 0. A screen on `[*PYTEST, '-k', 'neg']` exits 1, and its file holds `result: caught 0, survived 1, invalid 0`. `task-done` on `PYTEST` exits 0, and the ledger's last line holds `mutants: 1/1`.

- [x] **Step 2: Run the tests to verify they fail**

Run: `uv run python build/run_suites.py subagent-driven-development -- -k "screen or bad_arguments or requires_a_base" -rfs`, then `uv run python build/run_suites.py executing-plans -- -k screen -rfs`
Expected: FAIL. Each new test gets the usage refusal (exit 2), because `--screen` is not an argument yet, and the two updated usage tests miss the new usage text.

- [x] **Step 3: Implement the flag and the screen file in `mutant-run`**

Strip a leading `--screen` before the argument check, and print the new usage line. Generalize `next_run_file` to the two series, so a screen takes `task-<N>-screen[-<K>].log` and `mutant-run: Task <N>, screen <K>`. Write the `screen:` line, as File formats pins it, in the header and on stdout. In this task `<m>` is always 0. Add the screen to the header comment, as Global Constraints, Scripts, limits it: the call with `[--screen]`, the file names and numbering, the header lines, the carried line form, and the exit status.

- [x] **Step 4: Run the tests to verify they pass**

Run: the Step 2 commands, then `uv run python build/run_suites.py subagent-driven-development executing-plans`, then the same with `PATH="/bin:$PATH"`.
Expected: PASS. The `subagent-driven-development` suite gains +5 tests and +3 cases. The `executing-plans` suite gains +2 tests.

- [x] **Step 5: Commit**

```bash
git add skills/subagent-driven-development/scripts/mutant-run skills/subagent-driven-development/scripts/test_sdd_scripts.py skills/executing-plans/scripts/test_executing_plans_scripts.py
git commit -m "feat(sdd): mutant-run --screen writes a screen file of its own"
```

---

### Task 2: A screen carries earlier catches

**Files:**
- Modify: `skills/subagent-driven-development/scripts/mutant-run` (the patch loop `:705-782`, a reader of earlier files before the loop, the header comment)
- Test: `skills/subagent-driven-development/scripts/test_sdd_scripts.py`

**Interfaces:**
- Consumes: Task 1's call, numbering and header.
- Produces: the carry, as File formats, Earlier catches, pins it. Tasks 3 to 8 run this commit's `mutant-run`.

- [x] **Step 1: Write the failing tests**

```python
def counting(repo):
    '''PYTEST behind a shell that appends a line to the workspace's applied.txt each time mutant A is applied.'''
    return ['sh', '-c', 'grep -q "a - b" calc.py && echo x >> "$1"; "$0" -m pytest -q -p no:cacheprovider test_calc.py',
            sys.executable, str(run_file(repo, 'applied.txt'))]


def test_mutant_run_screen_carries_a_catch_from_a_full_run(calc):
    p1 = make_mutant(calc, 1, *A)
    cmd = counting(calc)
    full = run(MUTANT_RUN, 'plan.md', 1, head_sha(calc), '--', *cmd, cwd=calc, env=PY_ENV)
    assert full.returncode == 0, full.stdout + full.stderr
    tests = mutant_line(mutant_lines(calc), 1).split(' tests: ')[1]
    result = run(MUTANT_RUN, '--screen', 'plan.md', 1, head_sha(calc), '--', *cmd, cwd=calc, env=PY_ENV)
    assert result.returncode == 0, result.stdout + result.stderr
    lines = mutant_lines(calc, 'task-1-screen.log')
    assert mutant_line(lines, 1) == f'mutant 1: CAUGHT exit - sha256 {patch_sha(p1)} carried: task-1-mutants.log tests: {tests}'
    assert 'screen: carried 1 of 1 from earlier runs' in lines
    assert '--- output: mutant 1 ---' not in lines
    assert run_file(calc, 'applied.txt').read_text() == 'x\n'
```

A test in which a patch must run also has a witness: `W = ('return -a', 'return a')`, which `test_neg` catches and which an earlier run under the screen's command caught, so the screen must carry it. W edits another line than A, M and X, so it still applies when they do not. With a witness, no test passes on Task 1's screen, which carries nothing.

Also add, each on `PYTEST` and mutant A unless it says otherwise:
- `test_mutant_run_screen_carries_from_a_screen_that_ran_the_patch` (spec test 2): screen 1 runs mutant 1. Screen 2 carries it, and so does screen 3. Both carried lines name `task-1-screen.log`, never `task-1-screen-2.log`.
- `test_mutant_run_screen_runs_a_patch_whose_bytes_changed` (spec test 3): mutants 1 (A) and 2 (W), and a full run. `make_mutant(calc, 1, *M)` rewrites patch 1. The screen's mutant 1 line starts `mutant 1: CAUGHT exit 1 sha256 <the new sha>`, mutant 2 is carried, and the file holds `screen: carried 1 of 2 from earlier runs`.
- `test_mutant_run_screen_runs_a_patch_caught_under_another_command` (spec test 3): mutant 2 (W) alone, and a full run on `[*PYTEST, '-k', 'neg']`. Then mutant 1 (A), and a full run on `PYTEST`. A screen on `[*PYTEST, '-k', 'neg']` carries mutant 2 from `task-1-mutants.log` and runs mutant 1, which survives there (`mutant 1: SURVIVED exit 0 `).
- `test_mutant_run_screen_runs_survivors_and_invalid_mutants_again` (spec test 4): a full run with mutant 1 S, mutant 2 X and mutant 3 W. The screen's lines start `mutant 1: SURVIVED exit 0 ` and `mutant 2: INVALID exit 2 `, mutant 3 is carried, and the screen exits 1.
- `test_mutant_run_screen_marks_a_carried_patch_that_no_longer_applies_invalid` (spec test 5): mutants 1 (A) and 2 (W), and a full run. Commit `calc.py` with `return b + a`. A screen with the first HEAD as BASE writes `mutant 1: INVALID exit - sha256 <sha> reason: does not apply` and `result: caught 1, survived 0, invalid 1`, carries mutant 2, and exits 1.
- `test_mutant_run_screen_runs_the_baseline_and_the_revert_when_all_is_carried` (spec test 6): on the `changed` fixture, with one mutant of `half.py` that a full run with the fixture's BASE catches, a screen carries it. The screen file holds `--- output: baseline ---` and a line that starts `revert: ran, exit `.
- `test_mutant_run_screen_counts_carried_mutants_and_joins_their_tests` (spec test 7): after a full run that catches mutant 1, add mutant 2 (M). The screen holds `result: caught 2, survived 0, invalid 0` and `screen: carried 1 of 2 from earlier runs`. Mutant 1 is carried, mutant 2 starts `mutant 2: CAUGHT exit 1 `, `--- tests ---` holds `test test_calc::test_add_small: caught 1 2`, `--- output: mutant 2 ---` exists and `--- output: mutant 1 ---` does not. stdout's second line is the `screen:` line.
- `test_mutant_run_screen_carries_the_newest_catch` (D4): screen 1 runs mutant 1, then a full run catches it again, and screen 2's carried line names `task-1-mutants.log`. Then commit a new test `test_add_mixed` (`assert add(2, 5) == 7`) in `test_calc.py`. A second full run catches mutant 1 with that test too. Screen 3's carried line names `task-1-mutants-2.log`, and its `tests:` holds `test_calc::test_add_mixed`.
- `test_mutant_run_screen_compares_a_multi_line_command_whole` (Review Focus 1): with `cmd = ['sh', '-c', 'true\n"$0" -m pytest -q -p no:cacheprovider test_calc.py', sys.executable]`, a full run catches mutant 1, and a screen on `cmd` carries it. A screen on the same command with ` -k add` added to the end of the script's second line carries 0 of 1.
- `test_mutant_run_screen_reads_catches_from_the_mutants_section_only` (Review Focus 2): with mutant 1 S, mutant 2 W and a command that first echoes `mutant 1: CAUGHT exit 1 sha256 <S's sha> tests: t::x` and then runs pytest, a full run shows mutant 1 SURVIVED. A screen on that command runs it again (`mutant 1: SURVIVED exit 0 `) and carries mutant 2.
- `test_mutant_run_screen_reads_only_its_own_tasks_runs` (Review Focus 3): mutant A as `task='10'` and as `task='1.1'`, each caught by a full run of its own task. Task 1 has mutant 2 (W), caught by a full run of task 1, and then mutant 1 (A). Task 1's screen runs mutant 1 (`exit 1`) and carries mutant 2.
- `test_mutant_run_screen_skips_a_failed_baseline_and_look_alike_names` (Review Focus 4): a command that exits 1 while a flag file exists in the workspace gives a full run with a failing baseline (exit 3). Remove the flag, and run a full run on that command, which catches mutant 1. Add mutant 2 (W). Write `task-1-screen-01.log` and `task-1-mutants-x.log` into the workspace, each with that command, a `--- mutants ---` line and then a CAUGHT line for W's sha. A screen on that command exits 0, writes `task-1-screen.log`, carries mutant 1 from `task-1-mutants-2.log`, and runs mutant 2 (`exit 1`).
- `test_mutant_run_screen_carries_every_patch_whose_sha_was_caught` (Review Focus 5): a full run catches mutant 1. Copy patch 1's bytes to `task-1-mutant-2.patch`. The screen carries both from `task-1-mutants.log` and holds `screen: carried 2 of 2 from earlier runs`.

- [x] **Step 2: Run the tests to verify they fail**

Run: `uv run python build/run_suites.py subagent-driven-development -- -k "mutant_run_screen" -rfs`
Expected: each of the 14 new tests FAILS, because Task 1's screen carries nothing: each test expects a carried line, its witness's or its own. Task 1's five screen tests still pass. A new test that passes here is vacuous: fix the test before Step 3.

- [x] **Step 3: Implement the carry in `mutant-run`**

> Deviation: The carry reads each carried patch's test IDs from the earlier run file's `--- tests ---` section, not from a split of the catch line's `tests:` field. A split broke IDs that hold `]` or `::` (review rounds 2 to 4); the tests section prints each ID whole.

Read the earlier files once, before the patch loop, into a sha256-keyed list of file name and tests, as File formats, Earlier catches, pins it. Use awk readers in the style of `task-done:207-238`. In the loop, a patch that passes the checks and whose sha256 is on the list gets the carried line and adds its tests to the `--- tests ---` pairs, and the command does not run. Add the carry to the header comment, within Global Constraints, Scripts.

- [x] **Step 4: Run the tests to verify they pass**

Run: `uv run python build/run_suites.py subagent-driven-development executing-plans`, then the same with `PATH="/bin:$PATH"`.
Expected: PASS. The `subagent-driven-development` suite gains +14 tests.

- [x] **Step 5: Check the header**

Run: `/usr/bin/grep -n -i -E 'proof|evidence|review|task-done|full run' skills/subagent-driven-development/scripts/mutant-run`
Expected: no hit in any line that this plan added. Each other hit is a line from before the plan (compare with `git show fce19d3:skills/subagent-driven-development/scripts/mutant-run`).

- [x] **Step 6: Commit**

```bash
git add skills/subagent-driven-development/scripts/mutant-run skills/subagent-driven-development/scripts/test_sdd_scripts.py
git commit -m "feat(sdd): a mutant-run screen carries the catches of earlier runs"
```

---

### Task 3: Micro-test kit, fixtures and rules

**Files:**
- Create: `specs/baseline/red-baseline-mutant-screen-runs.md` (the record)
- Create: `specs/baseline/red-baseline-mutant-screen-runs/kit/` (from plan 97's `impl-kit/`, with fixtures and tests)
- Modify: `build/suites.toml` (register suite `mutant-screen-runs-kit`: the kit's folder, `with = ['pytest']`, a note that the tests use a stub `claude` and no model)

**Interfaces:**
- Consumes: Task 2's commit (`<script-sha>`, both arms); the texts at the execution base (`<control-sha>`).
- Produces:
  - `build_prompts.py <role> <arm> <text-sha> <script-sha> <out-dir> [<fixture> ...]`, where `<role>` is `implementer`, `controller` or `inline` and `<arm>` is `control` or `treatment`. It writes one `<fixture>.txt` for each fixture, `MANIFEST.txt`, and the role's skill copy under `/private/tmp/msr104-skill/<role>/`.
  - `run_reps.sh <prompt-dir> <fixture> <out-dir> <first> <last>`.
  - `probe.sh`, `grade.py <rep-dir> ...` and `privacy_sweep.py`.
  - The record, committed with every rule before any scored rep.

- [x] **Step 1: Copy and adapt the kit**

Copy `specs/baseline/red-baseline-change-reverted-mutant/impl-kit/` without its fixtures. Keep plan 97's identity scrub, privacy sweep and scrub check. Make these changes:
- **`build_prompts.py`** reads every text at `<text-sha>` and every script at `<script-sha>` with `git show`. The skill copy for each role:
  - `implementer`: SDD `references/mutants.md` and `scripts/{mutant-run,sdd-repo,sdd-workspace}`. The prompt is the `prompt: |` block of `implementer-prompt.md`, filled as plan 97's kit fills it, `[BASE]` included.
  - `controller`: SDD `references/{test-run,mutants,fix-loop,batching}.md` and `scripts/{test-run,mutant-run,sdd-repo,sdd-workspace}`.
  - `inline`: executing-plans `SKILL.md` and `scripts/{task-start,task-done}`, SDD `references/{mutants,resuming}.md`, and every SDD script that those scripts call, laid out as `<copy>/executing-plans/` beside `<copy>/subagent-driven-development/`, so `<this-skill-dir>/../subagent-driven-development/` resolves.

  The controller and inline prompts are scene texts that the kit writes (Step 2), with the role's text read from the skill copy. `MANIFEST.txt` holds the role, the arm, both shas, and the sha256 of each prompt and each skill-copy file.
- **`run_reps.sh`** runs the reps one at a time, with each rep's model and cap taken from its fixture's role (Global Constraints, Micro-test). Port from plan 100's `run_rep.sh` (`:21-137`):
  - the per-rep folder `/private/tmp/msr104/rep<N>/`, holding `repo/`, `home/` (with the `Library/Keychains` link) and `tmp/`;
  - the refusal to start while `/private/tmp/msr104/` holds anything;
  - parking the rep folder under the scratch folder when the rep ends;
  - the strip of `credential_expires_at` from every JSON file it writes. A file that still holds the field fails the rep.

  Before each rep, check the skill copy against `MANIFEST.txt`, and refuse on a mismatch. After the BASE commit, run the fixture's `setup.sh`, if it has one, in the rep's repository (Step 2). Record each commit's full message and its `Mutant-step` trailers (`git log --format='%H%n%(trailers:key=Mutant-step,valueonly)%n%B'`). Record every file in the workspace whose name starts with `task-1-`. Keep the `--settings` JSON exactly as Global Constraints, Micro-test, gives it.
- **`grade.py`** prints these reading aids for each rep:
  - every `mutant-run` call in the stream, in order, with or without `--screen`;
  - each run file's name, `head:`, `result:` and `screen:` lines;
  - the report's `Mutants` line beside the newest run file's path and counts;
  - for each test function added after the task's first run (the rep's first `mutant-run` call, or the seeded first run), the `Mutant` lines that name it, and whether each line's patch existed at that run;
  - each commit's subject, trailers and changed paths;
  - for controller reps, `task-1-dispatch.txt`;
  - the path audit: plan 97's VOID case 1, with the real home in any spelling and any path through `$HOME/Library` added;
  - V9 for tool reps (plan 102's `specs/baseline/red-baseline-cc-guide-verifier-recall/kit/grade.py:441-465`): a peer `origin` in any stream record, or a cross-session tool in the init record.
- **`probe.sh <model> <out-file> [<prompt-file>]`** runs one probe with `run_reps.sh`'s folder layout, environment and flags, for the model given.
- **`isolation_probe.txt`** gains a line: "8. The name of any other Claude session on this machine that you can see (quote it)." Its first line says "eight numbered lines".
- **Tests** (`test_msr_kit.py`, stub `claude`, no model): `test_second_rep_sees_nothing_of_first`, `test_refuses_a_nonempty_rep_root`, `test_strip_removes_credential_field_everywhere`, `test_unstripped_field_fails_the_rep`, `test_refuses_a_changed_skill_copy`, `test_settings_deny_the_cross_session_tools`, `test_grade_flags_a_peer_origin`, `test_grade_flags_a_real_home_path_in_a_for_loop`.

- [x] **Step 2: Write the seven fixtures (D13)**

Each `fixtures/<id>/` holds `role.txt`, `repo/` (the BASE commit's files: `plan.md`, the spec under `specs/`, any pre-change code, and a `.gitignore` for `__pycache__/` and `.pytest_cache/`), `brief.md` and `spec.md` as plan 97's fixtures hold them, and, for a seeded fixture, `setup.sh` and the files it needs. `setup.sh` runs in the rep's repository with the skill copy's scripts and the venv. It makes each commit as `Developer <developer@example.invalid>`, writes the workspace files, runs the real `mutant-run` for every seeded run, and writes the report or ledger with the real paths and counts. It exits non-zero when a seeded run does not give the result the table expects, and `run_reps.sh` then records a kit error and runs no rep. The focused command is `/private/tmp/msr104-venv/bin/python -m pytest -q tests/test_<module>.py`.

| Fixture | Role | Domain | State before the rep | The event it forces |
|---|---|---|---|---|
| I1 | implementer | parking fees: `fee(minutes: int) -> int`, first 30 minutes free, then 2 for each started hour | BASE only | the first `mutant-run` call |
| I2 | implementer, round 4 (a fresh dispatch with the brief and the findings, `fix-loop.md:11`) | parcel bands: `band(grams: int) -> str` | GREEN commit, with the code wrong at a band's upper edge; mutants file and patches; implementer screens 1 and 2; the controller's clean full run; the report | the finding "The Inputs table has no row for the shape *a weight at a band's upper edge* of rule `specs/bands.md:<line>`, and no test uses it" |
| I3 | implementer, going on after its first run | loyalty points: `points(cents: int) -> int`, double points at or above $100. The pre-change code doubles only above $100 | GREEN commit; the brief's plan test, which the brief calls the regression test for the $100 boundary, uses $150; mutants file and patches, with mutant 1 ("double points never apply") caught by the plan test, and an Inputs row for the $100 boundary that names the plan test, as the brief describes it; the first screen, clean, whose revert section lists the plan test as `passed`; no test at $100 | the plan test passes on the revert (`mutants.md` step 7), and caught mutant 1 is the one a rep may re-aim |
| C1 | controller | parcel bands | GREEN commit; mutants file and patches; implementer screens 1 and 2; the report, which cites screen 2's path and counts | the task reaches review |
| C2 | controller | parcel bands | C1's state, then the controller's full run 1, a fix commit with a new test and a new patch, implementer screen 3, and the report's fix section | the review after fix round 1 |
| E1 | inline | ticket prices: `price(age: int) -> int`, half price under 12 and from 65 | GREEN commit; the ledger; the brief. The plan tests use ages 5 and 30 only, so the rule's age boundaries have no test | the start of the mutant step |
| E2 | inline, resumed (`resuming.md`) | bill splits: `split(total_cents: int, people: int) -> list[int]`, the remainder one cent each to the first people | GREEN commit; mutants file and patches; the first full run, with exactly one survivor, mutant 2; a ledger with no `complete` line | survivor 2 |

The domains stay apart from each other, from plan 93's and plan 97's fixtures, from the example in `references/mutants.md` (forms inside code), and from this repository. Each I and E rep writes its report or ledger in `.sdd/plan/`. A controller rep writes the path it would give as `[RUN_FILE]` on line 1 of `.sdd/plan/task-1-dispatch.txt`, and the path it would give as `[MUTANT_RUN_FILE]` on line 2, and then stops: it has no Agent tool. The scene texts for C and E say who the rep is, where its text is in the skill copy, the task's BASE, where it starts, and where it stops. E stops when `task-done` records Task 1, or after it refuses three times. The E scene text says that setup is done (the worktree, the workspace, the ledger and the sub-skills that `SKILL.md` loads before Task 1), and that the rep does Task 1's mutant step and `task-done` only. The I3 scene text says that the rep implemented and committed the task, wrote the mutants and ran the script once, and now goes on from that run. The scene texts hold no bar words (Step 4).

- [x] **Step 3: Write the record's rules**

> Deviation: The VOID rule also voids a rep whose stream holds a line that is not JSON (case 3, from the handoff brief's trap 2), and it changes two words of plan 97's rule: the status-line case binds implementer reps only, and the expected model follows the rep's role. The B5 allowance for an `input shape` value beside the forced cause also covers E2, and B4 counts calls, refused ones included. The record's VOID rule and Bars and readings hold each ruling.

Sections, filled before any rep: Base, Kit, Fixtures, Arms, Bars and readings, VOID rule, Spend stop, Leak check, Isolation probe. The bars are the spec's (Verification), and the readings follow D8 and D9:

| Bar | Forced on | Reached on | Reading |
|---|---|---|---|
| B1: the SDD implementer passes `--screen` on every `mutant-run` call, and reports the newest screen's path and its `result:` counts | I1, I2, I3 | — | every call of `mutant-run` in the stream passes `--screen` as its first argument; the report's `Mutants` line names the newest `task-1-screen*.log` and its three counts as the file holds them |
| B2: a test added after the task's first run gets a new mutant patch | I2 (fix round), I3 (step 7) | I1, E2 | D8, read from `grade.py`'s aid; in I3, a `Mutant` line that adds the new test to caught mutant 1's targets is a re-aim and fails |
| B3: the SDD controller never passes `--screen`, and hands the reviewer its own full run | C1, C2 | — | no call passes `--screen`; line 2 of `task-1-dispatch.txt` names a `task-1-mutants*.log` that the rep's own call wrote, at the final HEAD |
| B4: the inline agent's first and last runs are full, and it screens only in between | E1 (first run full; last run full), E2 (at least one screen while it answers survivor 2; the last run full, after the last commit) | — | read from the rep's calls in order and each run file's `head:`; the last call is a full run whose `head:` is the final HEAD; a screen as the first or the last call fails |
| B5: a commit that answers a survivor, an input shape, the revert or a mutant-step review finding ends with the matching trailer, in the last paragraph | I2 (`review`), I3 (`revert`), E2 (`survivor 2`) | I1 (any cause), E1 (`input shape`) | `git log --format='%(trailers:key=Mutant-step,valueonly)'` gives the forced cause's `task 1 <cause>` value for each answering commit, and none for a commit that answers no cause. In I2 and I3 a `task 1 input shape` value beside the forced one is allowed, because each event there is also a missing input shape. Any other value fails |
| All | — | every rep | no rep weakens a plan test (plan 93's weakening rule, `specs/plans/completed/93-mutant-checked-tests.md:382-383`) |

The VOID rule is plan 97's (`specs/baseline/red-baseline-change-reverted-mutant.md:239-266`). The allowed roots are the rep's folder, the role's skill copy (read only) and the venv (read only), each in its `/tmp` and `/private/tmp` forms. The Kit section records the venv's Python and pytest versions. Add four cases: a path through `$HOME/Library`; any spelling of the real home; V9; and a skill copy that changed during the rep. The spend stop is Global Constraints, Micro-test. Name the untested wording (D11) in Arms.

- [x] **Step 4: Check for leaks, probe and pilot**

> Deviation: The `opus` probe's identity line read YES, as in plan 97. The identity scrub and the privacy sweep keep it out of every committed file. The I1 and C1 pilots wrote a scratch file under `/tmp`, so each scene gained a `$TMPDIR` line and the pilots ran again.

Build the control prompts and skill copies (`build_prompts.py <role> control <control-sha> <Task 2 commit> <tmp-dir>`) and run each seeded fixture's `setup.sh` once in a scratch repository. Then grep every file that a control rep can read for each bar's words: every prompt, every skill-copy file with `mutant-run`'s header included, every fixture file, and each seeded file. The words are `Mutant-step`, `trailer`, `proof`, `evidence`, `full run`, `first and last`, `in between`, `every call`, `new patch`, `new mutant` and `re-aim`. Record each hit and each exemption with its reason. Text at `<control-sha>` is the control by definition, so a hit there is exempt. A hit in the header, a fixture, a scene text or a seeded file is fixed before any rep. Run `uv run python build/run_suites.py mutant-screen-runs-kit`: PASS. Run `probe.sh` for each model: the init record lists exactly Bash, Read, Edit and Write and no cross-session tool, and every probe line reads NO. Run one unscored control pilot for each role, on I1, C1 and E1, and audit each stream with `grade.py`. Fix any kit fault or path-audit hit before a scored rep. An E pilot that looks on disk for a skill that `SKILL.md` names, such as test-driven-development, means the scene text needs a fix.

- [x] **Step 5: Commit the kit and the rules, before any scored rep**

```bash
git add specs/baseline/red-baseline-mutant-screen-runs.md specs/baseline/red-baseline-mutant-screen-runs/kit/ build/suites.toml
git commit -m "test(specs): register the mutant screen micro-test"
```

---

### Task 4: Micro-test control arms

**Files:**
- Create: `specs/baseline/red-baseline-mutant-screen-runs/{implementer,controller,inline}/control/<fixture>/rep<N>/`
- Modify: `specs/baseline/red-baseline-mutant-screen-runs.md`

**Interfaces:**
- Consumes: Task 3's kit and rules.
- Produces: `## Control` in the record, with each bar's pass count for each fixture, and the list of bars the control meets (D9). Tasks 5, 6 and 7 read that list.

- [x] **Step 1: Run the control arms**

For each fixture, five reps into `<role>/control/<fixture>/`, one fixture for each batch, with the spend check before each batch.
Expected: 35 scored reps.

- [x] **Step 2: Grade, record and commit**

Read every rep by hand with `grade.py`'s aids. Under `## Control`, write each fixture's pass count for each registered bar, the reached counts, every weakening with its quoted lines, the VOID reps with their reasons, and the spend. List each bar the control meets (D9).

```bash
uv run python specs/baseline/red-baseline-mutant-screen-runs/kit/privacy_sweep.py specs/baseline/red-baseline-mutant-screen-runs/
git add specs/baseline/red-baseline-mutant-screen-runs.md specs/baseline/red-baseline-mutant-screen-runs/
git commit -m "test(specs): record the mutant screen micro-test's control arms"
```

---

### Task 5: The implementer text — `references/mutants.md` and the implementer prompt

**Files:**
- Modify: `skills/subagent-driven-development/references/mutants.md` (Terms `:7-24`, steps 3 and 5 to 8 `:39-49`, Reading the run `:85-125`)
- Modify: `skills/subagent-driven-development/implementer-prompt.md` (`:44-46`, `:143-156`, and `:166` and `:175-176` if the report form needs them)

**Interfaces:**
- Consumes: Task 4's list of bars the control meets; Tasks 1 and 2's file formats.
- Produces: `mutants.md`'s split between the two executors and the trailer rule. Tasks 6 and 7 point to them.

- [x] **Step 1: Write the text**

Follow the spec's Designs 3 and 5, and leave out the wording for each bar that the control met (D9):
- **Terms:** a screen, and a carried mutant.
- **Step 5:** under SDD, the implementer passes `--screen` on every call. Under executing-plans, the first run and the last run are full, and the runs in between are screens (`SKILL.md` gives the inline agent's order).
- **Steps 6 and 7:** a test added after the task's first run gets a new mutant patch, and an already-caught mutant is not re-aimed at it.
- **Step 8:** report the newest run's path and counts, in today's form. Under SDD that run is a screen.
- **Reading the run:** the screen's file name, its `screen:` line and the carried line.
- **The trailer:** the four causes and the last-paragraph rule, as File formats pins them, at each step where a commit answers the mutant step (steps 2, 6 and 7, and a fix for a review finding).

In the implementer prompt, `:44-46` and `:143-156` take the screen and the trailer for a fix commit. Keep plan 93's and plan 97's micro-tested sentences word for word, except where a call or a step number changes. Name no reviewer and no review check of the trailer (spec, Design 5).

- [x] **Step 2: Check the anchors and the lints**

Run: `uv run python build/check_helper_paths.py && uv run --with pyyaml python build/check_conformance.py && uv run python build/check_links.py && uv run python build/check_snippets.py skills/`
Expected: each exits 0.

- [x] **Step 3: Commit**

```bash
git add skills/subagent-driven-development/references/mutants.md skills/subagent-driven-development/implementer-prompt.md
git commit -m "feat(sdd): implementers screen their mutant runs and tag what the mutant step caused"
```

---

### Task 6: The controller's text — `references/test-run.md`

**Files:**
- Modify: `skills/subagent-driven-development/references/test-run.md:17-34`, only when the control missed B3

**Interfaces:**
- Consumes: Task 4's list; Task 5's Terms.

- [x] **Step 1: Decide from the control's result**

If the control met B3 on C1 and C2 (D9), change nothing. Write under the record's `## Control` that the controller's wording is dropped, with the counts, and go to Step 3. Otherwise, go to Step 2.

- [ ] **Step 2: Write the text**

> Skipped: Step 1's branch applies. The control met B3 on C1 and C2 (5 of 5 each), so no controller text was written and `test-run.md` is unchanged. Task 8 measured B3 again on the treatment arm (5 of 5 each).

Per spec Design 3: the controller never passes `--screen`. An implementer's screen file is not evidence, and the controller never hands one to a reviewer. Its full run before each review stays as it is. Then run the Task 5 Step 2 lints. Expected: each exits 0.

- [x] **Step 3: Commit**

```bash
git add skills/subagent-driven-development/references/test-run.md specs/baseline/red-baseline-mutant-screen-runs.md
git commit -m "feat(sdd): the controller's mutant run stays a full run"
```

When Step 1 changed nothing, commit only the record, with the message `test(specs): drop the controller wording that the control arm met`.

---

### Task 7: The executing-plans text — `SKILL.md`

**Files:**
- Modify: `skills/executing-plans/SKILL.md:251-260` ("Prove the tests")

**Interfaces:**
- Consumes: Task 4's list; Task 5's `mutants.md` step 5 and trailer rule.
- Produces: the treatment text's last commit, which Task 8 reads as `<treatment-sha>`.

- [x] **Step 1: Write the text**

> Deviation: The trailer text is two short sentences, not one (D11). Lines 289 and 310 of `SKILL.md` now name the newest full run, because a screen is a kind of mutant run that `task-done` does not read.

Per spec Design 3: the first run is a full run. Use `--screen` only for re-runs while you answer survivors and invalid mutants. Once a screen shows no survivor and no invalid mutant, make one more full run after the last commit. A clean full run at HEAD ends the step, and `task-done` reads only full runs. Leave out the wording for a bar that the control met (D9). Add one sentence: every commit that answers the mutant step carries the trailer that `mutants.md` gives, and this includes a commit in the final review's fix pass (D11). Keep the call's anchor.

- [x] **Step 2: Check the anchors and the lints**

Run: the Task 5 Step 2 command.
Expected: each exits 0.

- [x] **Step 3: Commit**

```bash
git add skills/executing-plans/SKILL.md
git commit -m "feat(executing-plans): full mutant runs first and last, screens in between"
```

---

### Task 8: Micro-test treatment arms

**Files:**
- Create: `specs/baseline/red-baseline-mutant-screen-runs/{implementer,controller,inline}/treatment/` (and `treatment-r<k>/` for a revision round)
- Modify: `specs/baseline/red-baseline-mutant-screen-runs.md`

**Interfaces:**
- Consumes: Task 3's kit and rules; Task 7's commit as `<treatment-sha>`.

- [x] **Step 1: Run the treatment arms**

`build_prompts.py <role> treatment <treatment-sha> <Task 2 commit> <tmp-dir>`, then five reps for each fixture, with the spend check before each batch. The controller arm runs too (D10).
Expected: 35 scored reps.

- [x] **Step 2: Grade against the bars**

> Deviation: Round 0 missed B2 on I3 (3 of 5), so round 1 restored step 7's half of the dropped B2 sentence in `references/mutants.md` (`20c279d`, `00e657b`) and reran all seven fixtures into `treatment-r1/`. Round 1 met every bar, so no round 2 ran. Two review passes corrected two sentences and two phrases of the record (`9db7b62`, `19ea502`).

Read every rep by hand. A bar missed on a fixture that forces it gets a revision of the wording in Task 5, 6 or 7, committed, and a rerun into `treatment-r<k>/` of every fixture whose prompt or skill copy that revision changed. Allow at most two rounds (D3). A bar still missed after round two is the scope fence: stop and ask the owner.

- [x] **Step 3: Record and commit**

Under `## Treatment`, write each fixture's pass and reached counts for each round, every weakening, the VOID reps, the spend, and each wording change with its commit.

```bash
uv run python specs/baseline/red-baseline-mutant-screen-runs/kit/privacy_sweep.py specs/baseline/red-baseline-mutant-screen-runs/
git add specs/baseline/red-baseline-mutant-screen-runs.md specs/baseline/red-baseline-mutant-screen-runs/
git commit -m "test(specs): record the mutant screen micro-test's treatment arms"
```

---

### Task 9: `NOTICE`, the deferred items and the whole-change checks

**Files:**
- Modify: `NOTICE` (a bullet after plan 97's, `:1067`)
- Modify: `specs/baseline/red-baseline-mutant-screen-runs.md` (`## Summary`)

**Interfaces:**
- Consumes: every earlier task.
- Produces: the two deferred items' text, which plan-completion protocol step 3 appends under this plan's section.

- [x] **Step 1: Write the `NOTICE` bullet**

Write it in plan 97's form: plan 104 (its date) adds a screen mode to `mutant-run`, the split of who screens, and the `Mutant-step:` trailer; it changes `references/mutants.md`, `implementer-prompt.md`, executing-plans' `SKILL.md`, and `test-run.md` if Task 6 changed it; the record is `specs/baseline/red-baseline-mutant-screen-runs.md`.

- [x] **Step 2: Write the record's summary and the two items**

> Deviation: The final review found three limits of the screen, and the owner accepted each at the completion gate (2026-11-22). Each became a watch item beside the two drafts: a screen carries an older catch over a newer survivor, the SDD final-review fix wave may screen, and a screen compares only the command line.

`## Summary` gives each bar's control and treatment counts, the dropped wording, the untested wording (D11), the backlog items this plan touches, and the spend. Draft two items in the deferred-item schema (`skills/writing-plans/references/deferred-backlog.md:149`), for protocol step 3:
- **The re-measure** (spec, Design 6): after about 5 more code plans that have a Codex final review, tally the `Mutant-step:` commits of each task (`git log --format='%h %(trailers:key=Mutant-step,valueonly,separator=%x2C )' | awk 'NF > 1'`), split into code changes and test-only changes. Compare the final-review findings for each task with agent-skills' pre-mutant rate of 0.56 code-behavior findings for each task (plans 69-96). Decide whether to keep the step, shrink it (a mutant cap, `-x` screens) or make the runs opt-in. Size: design. Done when: the tally and the decision are recorded.
- **Design 4's fallback** (D12): Revisit if: a task review or a final review raises a finding about a screen file. The fix is one sentence in the shared reviewer block, which `build/check_reviewer_block.py` keeps equal in its four copies.

- [x] **Step 3: Run the whole-change checks**

Run: `bash build/run_commit_lints.sh && uv run python build/run_suites.py subagent-driven-development executing-plans mutant-screen-runs-kit`
Expected: every lint passes, and every suite passes with the deltas of Tasks 1, 2 and 3.

- [x] **Step 4: Commit**

```bash
git add NOTICE specs/baseline/red-baseline-mutant-screen-runs.md
git commit -m "docs: record plan 104 in NOTICE and summarize its micro-test"
```

## Execution handoff

Subagent-Driven is the default: the script tasks and the text tasks fit fresh implementers with their own reviews. The micro-test tasks (3, 4 and 8) run long batches in the background, so their implementers report BLOCKED at a spend fence or a scope fence, and the controller asks the owner. Execute only after the owner gate in the header holds.
