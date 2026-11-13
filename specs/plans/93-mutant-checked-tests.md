# Mutant-checked tests Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make each task of a subagent-driven or inline plan run prove that its tests can fail. The implementer covers each stated rule's input shapes and writes plausible mutants. A new script, `mutant-run`, decides caught, survived and invalid. The task reviewer and executing-plans' `task-done` then gate on that script's run file.

**Architecture:** `mutant-run` sits beside `test-run`. It applies each mutant patch in the real working tree, runs the task's focused pytest command, reverses the patch, and reads a JUnit report that it requests through `PYTEST_ADDOPTS`. One new reference, `subagent-driven-development/references/mutants.md`, holds the implementer's steps for both executors. The controller's references, the task reviewer's new `## Mutants` section, executing-plans' text and `task-done`'s gate all read the run file in one pinned format. Two pre-registered micro-tests check the behavior-shaping text: the implementer text (Tasks 2 and 4) and the reviewer section (Tasks 6 and 8). Each runs a control arm on today's text before the new text exists.

**Tech Stack:** bash (macOS 3.2 compatible), git, pytest JUnit XML; Markdown skill text; pytest suites that drive the scripts as subprocesses; `claude -p` micro-test kits; the repo's commit lints (`build/run_commit_lints.sh`).

**Spec:** `specs/mutant-checked-tests.md` (approved 2026-11-12; commits `b719246`..`14f5400`, merged into this branch at `db4fede`). Its Terms, Design, Verification and Constraints sections are authoritative. Read the spec in full before Task 1.

## Global Constraints

### Base and execution

- **Base commit.** Every line number in this plan is a line of the file at `db4fede`. The spec's own line numbers are as of `8960159`. Two of its cites moved: the waiver `subagent-driven-development-compaction-window` is at `build/cc_guide/conformance.toml:796`, and `'skill:executing-plans'` in `install.py`'s `DEPENDENCIES` is at line 57. Before Task 1, run `git diff --stat db4fede HEAD -- skills/subagent-driven-development skills/executing-plans agents/task-reviewer.md build/check_helper_paths.py build/test_check_helper_paths.py build/CLAUDE.md CLAUDE.md NOTICE runtimes`. Any output means a file this plan edits changed after the plan was written. Re-read each cited line before a task quotes it, and ledger a `Ruling:` for any task text that no longer fits.
- **Base branch.** The spec and this plan exist only on the branch that holds this plan's commit (`claude/cool-brahmagupta-88fa30` at planning time). Until that branch merges, cut the execution worktree from it, not from `main`.
- **Self-modifying plan.** This plan edits the skills, scripts and agent that execute it. `~/.claude/skills/` and `~/.claude/agents/` are symlinks into the main checkout. Execute in a worktree. Call the controller tooling by absolute path through those symlinks, with the worktree as the working directory: `~/.claude/skills/subagent-driven-development/scripts/<name>` under subagent-driven-development, and `~/.claude/skills/executing-plans/scripts/task-start` and `task-done` under executing-plans. Do not merge this branch into the main checkout before the plan completes. Implementers and reviewers use the installed copies, which are main's.
- **No mutant step for this plan's own tasks.** The executor follows main's copies of the skills, which have no mutant step. This plan's tasks write no excerpts file, no mutants file and no mutant run. A reviewer does not flag their absence.
- **Scope fence.** These are out of bounds for this run. When the only fix crosses one, stop and ask the owner.
  - `skills/subagent-driven-development/SKILL.md` stays byte-identical (spec, Constraints and anti-goals). Its DONE paragraph's words "dispatch the task reviewer with both paths" stay. The references name the new paths. A reviewer does not flag the SKILL.md line.
  - The shared reviewer block (`## Review scope` to `## Declined to judge`) stays identical in its four copies. `agents/code-reviewer.md` and `skills/requesting-code-review/` do not change.
  - `skills/writing-plans/` does not change (spec, Non-goals). Another branch is fixing `skills/writing-plans/scripts/history_entry.py`.
  - The branch `claude/test-writer-subagent-sdd-666d94` is not rebased or amended.
  - Shipping implementer or reviewer text whose treatment arm still misses a bar after two revision rounds (spec, Verification item 5).
  - Any micro-test batch that would take the plan's total micro-test spend past **$100** (spec, Verification item 5).
- **Owner stops under subagent-driven-development.** An implementer cannot ask the owner. Where a step says "stop and ask the owner", the implementer reports BLOCKED with the quoted results and the running spend. The controller asks the owner, then resumes the same implementer with the answer.
- **Cross-skill references** use bare skill names, never a `superpowers:` namespace.

### Scripts

- **Bash 3.2.** `mutant-run`, `test-run` and `task-done` run under macOS `/bin/bash` 3.2.57. No `declare -A`, `mapfile`, `readarray`, `${v,,}`, `${v^^}`, `|&`, `&>>` or negative array indexes. Under `set -u`, expand a possibly empty array as `${a[@]+"${a[@]}"}`. Homebrew bash 5 is first on `PATH` on this Mac, so the default suite run never meets 3.2. Each script task therefore runs its suite a second time with `PATH="/bin:$PATH"`, and checks that `PATH="/bin:$PATH" /usr/bin/env bash -c 'echo $BASH_VERSION'` prints `3.2.57(1)-release`.
- **Portability.** No macOS-only or GNU-only tool: `sha256sum` when present, else `shasum -a 256`; no `readlink -f`, no `sed -i`, no `setsid`. Every git call that names a path runs as `git -C <top>`, where `<top>` is what `sdd-repo --with-commit` prints.
- **Tests** drive each script as a subprocess, as the existing suites do. Single quotes, f-strings, 4-space indentation, stdlib plus pytest. Python as pinned in `build/versions.toml`. Run them through `build/run_suites.py`. State count changes as deltas, never totals.

### File formats

These forms are pinned. Every task that writes or reads one uses them exactly. `<workspace>` is the directory `sdd-workspace PLAN_FILE` prints. `<N>` is a task number in `task-brief`'s grammar. `<K>` is a mutant number, a positive decimal integer.

**Excerpts file** `<workspace>/task-<N>-spec.md`. The subagent-driven controller writes it before it dispatches the implementer. executing-plans writes none.

```text
Spec: <spec path>

<path>:<line>: <one spec sentence, verbatim>
```

There is one line per sentence. When the plan's `Spec:` is `none`, the file holds the single line `none: <why>`.

**Mutant patch** `<workspace>/task-<N>-mutant-<K>.patch`: the output of `git diff -- <file>` for one edit to the task's code. A withdrawn mutant's patch is renamed `<workspace>/task-<N>-mutant-<K>.patch.withdrawn`.

**Mutants file** `<workspace>/task-<N>-mutants.md`:

```text
# Task <N> mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| <path:line, or brief: <requirement>> | <input shape> | <test name> |

## Mutants

Mutant <K>: <targets: rule path:line and test names> — <the wrong version, in one line> — task-<N>-mutant-<K>.patch
Unproven: <test> — <why no plausible wrong version exists>
Unreachable: <rule path:line> — <why no code change in this task can break it>
Withdrawn: <K> — <why no behavior a person could see changes>
```

Each `Mutant`, `Unproven`, `Unreachable` and `Withdrawn` line starts at column 0 with that word. `task-done` reads the lines that match `^Mutant ([0-9]+): ` and `^Withdrawn: ([0-9]+) `.

**Mutant run file** `<workspace>/task-<N>-mutants.log` for a task's first run, then `task-<N>-mutants-<K>.log` for run K = 2, 3 and so on (the smallest K whose file does not exist). The newest run is the one with the highest run number, never the newest by time.

```text
mutant-run: Task <N>, run <K>
command: <the command, rendered as test-run renders it>
head: <full sha of HEAD>
tree: clean
result: caught <c>, survived <s>, invalid <i>
note: reversed <patch file name>, left applied by a killed run
--- mutants ---
mutant <K>: <CAUGHT|SURVIVED|INVALID> exit <status, or - when nothing ran> sha256 <64 hex digits of the patch file>[ tests: <id> ...][ reason: <why>]
--- tests ---
test <id>: caught <K>[ <K> ...]
--- output: baseline ---
<the baseline run's output>
--- output: mutant <K> ---
<that mutant's run output>
```

- The `note:` line appears only after a recovery (Design 3, step 1).
- `<id>` is `<classname>::<name>` from a JUnit `<testcase>` element that holds a `<failure>` or an `<error>` element.
- A CAUGHT line carries `tests:`. An INVALID line carries `reason:`, with one of these values: `touches a test file: <path>`, `does not apply`, `no failed test in the JUnit report`, `exit status <n>`, `timeout after <n>s`.
- `--- output: mutant <K> ---` exists only for a mutant whose command ran.
- A failing baseline writes the first four header lines, then `result: baseline failed, exit <n>`, then `--- output: baseline ---` and its output, and nothing else.

**Marker** `<workspace>/mutant-active`. It exists only while a patch is applied. It holds what recovery needs: the applied patch's file name and the patch text, so that recovery works even when the patch file is gone.

**`mutant-run`.** `<this-skill-dir>/scripts/mutant-run PLAN_FILE TASK_NUMBER -- TEST_COMMAND [ARGS...]`.
- stdout: the `result:` line, then each `mutant` line, then `run: <absolute path of the run file>` last. A failing baseline prints the baseline output's last 5 lines, then its `result:` line, then the `run:` line. A refusal prints no `run:` line.
- Exit: 0 when every mutant is CAUGHT; 1 when any is SURVIVED or INVALID; 2 for a bad call, a bad task or mutant number, a dirty tree, no mutants, a mutant already in HEAD, or a tree the script could not restore; 3 for a failing baseline; 143 or 130 after TERM or INT, once the applied patch is reversed.
- `MUTANT_RUN_TIMEOUT` (whole seconds), when set, replaces the per-mutant time limit. The default limit is ten times the baseline's whole seconds, plus 60.

**`task-done`.** `<this-skill-dir>/scripts/task-done PLAN_FILE TASK_NUMBER BASE [--no-mutants REASON] -- TEST_COMMAND [ARGS...]`.
- Exit 4 when the mutant gate refuses. It writes no completion line then.
- The completion line is `Task <N>: complete (commits <base7>..<head7>, mutants: <caught>/<total>, tests: <command> → <last output line>)`. `<caught>` comes from the run's `result:` line. `<total>` is the number of `Mutant` lines in the mutants file. With `--no-mutants`, the field reads `mutants: none: <REASON>`.

**Dispatch placeholders.** The controller fills each one with an absolute path. A placeholder for a file that does not exist takes `none: <why>`.
- Implementer: `[SPEC_EXCERPTS_FILE]`, `[MUTANTS_GUIDE]` (`<this-skill-dir>/references/mutants.md`), `[MUTANT_RUN]` (`<this-skill-dir>/scripts/mutant-run`), `[PLAN_FILE]`, `[WORKSPACE]`.
- Task reviewer: `[SPEC_EXCERPTS_FILE]`, `[MUTANTS_FILE]`, `[MUTANT_RUN_FILE]`, `[TEST_RULINGS]`. `[TEST_RULINGS]` takes the ledger's `Ruling:` lines that cover a change to this task's plan tests, quoted, or `none`.
- Re-review: `<MUTANTS_FILE>`, `<MUTANT_RUN_FILE>`, `<TEST_RULINGS>`.

### Micro-tests

- **Method.** writing-skills' micro-test method, main's copy. Five scored reps per fixture per arm, each in a fresh context, at **standard** (`sonnet`). The fixtures, bars, reading rules, VOID rule and spend stop are written in the record (`specs/baseline/red-baseline-mutant-checked-tests.md`) and committed before any rep runs. Never add a reading after seeing reps. Read every verdict by hand from the rep's full output. A grading script gives reading aids, never verdicts.
- **Texts under test** enter a prompt or a kit copy only through `git show <sha>:<path>`, never through `~/.claude/`.
- **Isolation.** Each rep runs from its own new empty directory under `/tmp`, outside every repository, under `env -i` that keeps only `HOME`, `USER`, `LOGNAME`, `PATH`, `SHELL`, `TMPDIR` and `LANG`, plus `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`. Every rep passes `--strict-mcp-config`, `--setting-sources ""`, `--disable-slash-commands` and `--no-session-persistence`. No path or name that a rep can see names this repository, this plan, the skill under test or a bar. A pilot probe passes before any scored rep.
- **No scorer code from the statement-readings kit.** Neither kit copies a file from `specs/baseline/red-baseline-statement-readings/kit/`, and neither holds its `measure.py` or `compare.py` scorer code. So the backlog item at `specs/deferred_items.md:6238-6249` does not fire.
- **Spend.** The micro-test total is the sum of `total_cost_usd` over every rep and probe this plan runs, the gate-tag rerun included. Before each batch, check: running total + (reps in the batch × that rep kind's cap) ≤ $100. The caps are $1.50 for an implementer rep, $0.50 for a reviewer rep and $1.00 for a gate-tag rep. A batch that fails the check is the spend fence: stop and ask the owner. Every dispatch that runs reps carries the running total.
- **Rep hygiene.** A batch can take many minutes. Run it in the background or with `timeout: 600000`. The kits refuse to overwrite a rep's output. Resume a killed batch with the next free rep numbers, and never delete outputs. Raw `stream-json` transcripts hold home paths and session ids: keep them under `~/.cache/agent-skills/scratch/plan93/`, outside the repository, and never commit them.

### Commits and lints

- The commit lints pass on every commit. Never use `--no-verify`. Use `/usr/bin/grep` or `git grep` for sweeps, since `grep` here is a shell function.
- A new file under `skills/<skill>/` lands in the same commit as another non-test file of that skill that names it (`check_conformance.py`'s orphan rule).
- Every mention of `scripts/mutant-run` in a Markdown file under `skills/` carries the `<this-skill-dir>/` anchor, or `<this-skill-dir>/../subagent-driven-development/` from executing-plans.
- After any change under `agents/`, run `uv run --with pyyaml python build/sync_runtime_assets.py`, then the same command with `--check`. Never hand-edit `runtimes/`.

## Review Focus

1. A brief whose focused command `cd`s into a subdirectory, or a controller that stands in one. Every patch must still apply at the repository's top level, and the JUnit report must still be found. A person would otherwise see every mutant survive. Pinned by Task 1's `test_mutant_run_applies_patches_from_a_subdirectory`.
2. A caller that already sets pytest reporting flags, such as `-rs` in the brief's command or a `PYTEST_ADDOPTS` value. A catch must still read CAUGHT with its test IDs. Pinned by Task 1's `test_mutant_run_reads_a_catch_when_the_caller_sets_r_flags`.
3. A test command that leaves untracked files behind, such as caches or output files. The verdicts must not change, and the run must not stop as dirty halfway. Pinned by Task 1's `test_mutant_run_ignores_untracked_files_its_command_leaves`.
4. Task numbers that share a prefix (`2` and `2.1`, `1` and `10`). One task's mutants and runs must never count for another's. Pinned by Task 1's `test_mutant_run_keeps_dotted_task_ids_apart` and Task 9's `test_task_done_ignores_another_tasks_mutant_run`.
5. Ten or more mutants, or ten or more runs. Order must be numeric: mutant 2 runs before mutant 10, and run 10 is newer than run 2. Pinned by Task 1's `test_mutant_run_runs_mutants_in_number_order` and Task 9's `test_task_done_reads_the_newest_mutant_run_by_number`.

## Decisions

From the brief: none. The owner's decisions D1 and D2 and the designer's calls are in the spec. The lines below are planner defaults, for the owner's review at plan review. Each settles an item that the spec's "Left to the builder" leaves open and that crosses a task boundary, or a question that the brief delegated.

- **D1** (planner default, for plan review, 2026-11-12): the file formats, the marker, `task-done`'s exit 4 and the completion line are pinned as Global Constraints, File formats, says. `mutants: <c>/<t>` goes before `tests:` so that the line's tail is unchanged. Applied in: Global Constraints, Tasks 1, 3, 7, 9.
- **D2** (planner default, for plan review, 2026-11-12): after the baseline and after each reverse, tracked files must equal HEAD (`git -C <top> diff --quiet HEAD`). Untracked files are not compared, because tests leave caches. A tracked difference stops the run with exit 2 and the changed paths. Applied in: Task 1.
- **D3** (planner default, for plan review, 2026-11-12): each mutant's run has a time limit of ten times the baseline's whole seconds, plus 60, which `MUTANT_RUN_TIMEOUT` replaces. A timeout is INVALID (`timeout after <n>s`). Applied in: Task 1.
- **D4** (planner default, for plan review, 2026-11-12): `test-run` refuses to run (exit 2) while `<workspace>/mutant-active` exists. `mutant-run` reverses its applied patch on TERM, INT or HUP. The reason: after a killed run, test-run.md's dirty-tree bullet would send a fix round "to commit" what looks like the task's files, so a mutant could reach a commit (an anti-goal). Applied in: Tasks 1, 5.
- **D5** (planner default, for plan review, 2026-11-12): `test-run` and `mutant-run` share no helper. `mutant-run` repeats test-run's task-number check and command rendering. Applied in: Task 1.
- **D6** (planner default, for plan review, 2026-11-12): a JUnit `<error>` counts as a failed test, like `<failure>`. pytest exits 1 for both, and both name a test whose outcome the mutant changed. Applied in: Task 1.
- **D7** (planner default, for plan review, 2026-11-12): a batch uses its first task number for its excerpts file, mutants file, patches and mutant run, as test-run.md already does for its run. Applied in: Task 5.
- **D8** (planner default, for plan review, 2026-11-12): Design 1's excerpt rules live in `references/file-handoffs.md`, which the controller reads before its first dispatch. Applied in: Task 5.
- **D9** (planner default, for plan review, 2026-11-12): an `(unclear)` ruling that the owner overrules at the gate is work that the answer unblocks. writing-plans protocol step 1 implements it now, which is the spec's "follow-up task". The alternative is a deferred item, the rule the same paragraph gives a reverted tagged ruling. The spec places these questions under protocol step 1 (`skills/writing-plans/SKILL.md:291-299`), so step 1's rule governs. Backlog item `:6180` stays open (see Backlog items). Applied in: Tasks 5, 9.
- **D10** (planner default, for plan review, 2026-11-12): the reviewer gets `[TEST_RULINGS]`, so that it can judge a loosened plan test against its covering ruling (Design 5's last sentence). Applied in: Tasks 5, 7.
- **D11** (planner default, for plan review, 2026-11-12): `task-done` also refuses a task with no mutants file, and it checks each listed mutant against the run (Design 7's third condition). Applied in: Task 9.
- **D12** (planner default, for plan review, 2026-11-12): the implementer micro-test runs multi-turn reps with Bash, Read, Edit and Write in a new kit. The spec's estimate of $15–50 for 50 reps fits that kind of rep, and the bars need runs that a one-turn rep cannot see. The reviewer micro-test runs one-turn reps with no tools in a copy of plan 84's kit, `specs/baseline/red-baseline-test-run/kit/`, with plan 92's `--disable-slash-commands` and its sixth probe line. Applied in: Tasks 2, 4, 6, 8.
- **D13** (planner default, for plan review, 2026-11-12): the reviewer micro-test also runs R1–R3 on the task reviewer's Full Form, in the treatment arm only (15 more reps). The Full Form's review contract is the same text as the agent body, so the Short Form control serves both. This answers backlog item `:5719` for the new section. Applied in: Task 8.
- **D14** (planner default, for plan review, 2026-11-12): F5 and R1 are decoys. Their controls will likely meet their bars. The record reports them, but "the text adds nothing on that fixture" is not read from a decoy's control. A control that meets a non-decoy bar is recorded, and the owner rules on it at the completion gate, before the text ships. It is not a stop during execution. Applied in: Tasks 2, 4, 6, 8, 10.
- **D15** (planner default, for plan review, 2026-11-12): Task 5 reruns plan 80's `gate-tag` case (5 reps), because it edits the gate paragraph that the case tests. A miss gets the same two revision rounds and fence as the micro-tests. Applied in: Task 5.

## Backlog items this plan touches

- **`specs/deferred_items.md:6226`, 83-statement-level-readings layer 4.** Settled by Design 1, 5 and 7 (Tasks 3, 5, 7, 9). This plan's commit writes `→ planned 2026-11-12: specs/plans/93-mutant-checked-tests.md` on it. Protocol step 3 ticks it when the plan lands.
- **`:5677`, test-only findings and the delete pass.** Not settled. Its "Done when" needs a case with a test that asserts nothing, run on both reviewers. R1–R3 plant mutant gaps, and only the task reviewer runs. The `## Mutants` section exempts its own findings from the delete pass and leaves the shared sentence as it is. The item stays open.
- **`:5719`, the Full Form was never micro-tested.** It fires, because Task 7 changes the Full Form. Task 8 runs R1–R3 on it (D13). The rest of the Full Form stays untested, so the item stays open. Task 10's summary states this for the next `/deferred` pass.
- **`:6180`, a revert asked for at the gate has two rules.** Not settled. Tasks 5 and 9 add one exception to both gate paragraphs and keep each micro-tested sentence word for word. The exception follows protocol step 1's rule, one of the two the item names, for a question that the gate asks (D9). The item's own case, a revert of a tagged ruling, is unchanged. The `gate-tag` rerun (D15) checks the case the item names.
- **`:5857`, Bash 3.2 checked by reading.** Applied, not settled. Tasks 1 and 9 run their suites once under `/bin/bash` 3.2. The default run still uses bash 5, which is the item's point.
- **`:6238-6249`, the statement-readings scorer.** Does not fire. See Global Constraints, Micro-tests.
- **`:5387-5388`, "Mutation testing is out of scope".** Unchanged for its own problem (spec, Backlog effects).

## File map

| File | Change | Task |
|---|---|---|
| `skills/subagent-driven-development/scripts/mutant-run` | create | 1 |
| `skills/subagent-driven-development/scripts/test-run` | refuse while a mutant is applied | 1 |
| `skills/subagent-driven-development/scripts/sdd-workspace`, `sdd-repo` | header comments name `mutant-run` | 1 |
| `skills/subagent-driven-development/scripts/test_sdd_scripts.py` | new tests | 1 |
| `specs/baseline/red-baseline-mutant-checked-tests.md` | the record: rules, then results | 2, 4, 5, 6, 8, 10 |
| `specs/baseline/red-baseline-mutant-checked-tests/impl-kit/` | new kit and fixtures F1–F5 | 2 |
| `specs/baseline/red-baseline-mutant-checked-tests/implementer/` | rep outputs | 2, 4 |
| `skills/subagent-driven-development/references/mutants.md` | create | 3 |
| `skills/subagent-driven-development/implementer-prompt.md` | mutant step, conflict rule, placeholders | 3 |
| `build/check_helper_paths.py`, `build/test_check_helper_paths.py`, `build/CLAUDE.md`, `CLAUDE.md` | `mutant-run` joins `HELPERS` | 3 |
| `skills/subagent-driven-development/references/{test-run,file-handoffs,handling-reports,fix-loop,final-review,model-selection}.md` | controller steps | 5 |
| `specs/baseline/red-baseline-mutant-checked-tests/gate-tag/` | the gate-tag rerun's rep outputs | 5 |
| `specs/baseline/red-baseline-mutant-checked-tests/review-kit/`, `reviewer/` | kit copied from plan 84's; packages R1–R3; rep outputs | 6, 8 |
| `agents/task-reviewer.md`, `skills/subagent-driven-development/task-reviewer-prompt.md`, `re-review-prompt.md`, `runtimes/` | `## Mutants` section and new inputs | 7 |
| `skills/executing-plans/scripts/task-done`, `test_executing_plans_scripts.py` | the mutant gate | 9 |
| `skills/executing-plans/SKILL.md`, `references/final-review.md` | mutant step, contract, final review, gate | 9 |
| `NOTICE` | one entry under the superpowers changes | 9 |

---

### Task 1: The `mutant-run` script

**Files:**
- Create: `skills/subagent-driven-development/scripts/mutant-run` (mode 755)
- Modify: `skills/subagent-driven-development/scripts/test-run:30-42` (header) and after line 69 (the refusal)
- Modify: `skills/subagent-driven-development/scripts/sdd-workspace:17-18`, `skills/subagent-driven-development/scripts/sdd-repo:22-23` (header comments)
- Test: `skills/subagent-driven-development/scripts/test_sdd_scripts.py`

**Interfaces:**
- Consumes: `sdd-repo --with-commit` and `sdd-workspace PLAN_FILE`, unchanged.
- Produces: `mutant-run`, its run file, its marker and its exit codes, exactly as Global Constraints, File formats, pins them. `test-run`'s new refusal: exit 2, a stderr line that names `mutant-active`, and the command never runs.

- [ ] **Step 1: Write the failing tests**

In `test_sdd_scripts.py`, change the docstring's "five bundled bash scripts" to "six" and "five files" to "six files". Add `import hashlib` and `import sys`. Add these helpers after the test-run tests:

```python
MUTANT_RUN = SCRIPTS / 'mutant-run'
PY_ENV = {**GIT_ENV, 'PYTHONDONTWRITEBYTECODE': '1'}
PYTEST = [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', 'test_calc.py']
SLOW = ['sh', '-c', 'grep -q "a - b" calc.py && sleep 30; exit 0']

CALC = 'def add(a, b):\n    return a + b\n\n\ndef neg(a):\n    return -a\n'
TEST_CALC = '''from calc import add, neg


def test_add_small():
    assert add(1, 2) == 3


def test_add_large():
    assert add(100, 200) == 300


def test_neg():
    assert neg(2) == -2
'''
```

- A fixture `calc(committed)` writes `calc.py` and `test_calc.py`, commits both, and returns the repo. It adds no `.gitignore`.
- `make_mutant(repo, k, old, new, path='calc.py', task='1') -> Path` replaces `old` with `new` in `path`, writes `git diff -- <path>` to `.sdd/plan/task-<task>-mutant-<k>.patch`, restores the file with `git checkout -- <path>`, and returns the patch path. It asserts that the diff is not empty.
- `mutant_lines(repo, name='task-1-mutants.log') -> list[str]` returns the run file's lines.
- `mutant_line(lines, k) -> str` returns the one line that starts `f'mutant {k}: '`.
- `patch_sha(path) -> str` returns `hashlib.sha256(path.read_bytes()).hexdigest()`.

The mutants are: **A** `return a + b` → `return a - b` (both add tests fail); **M** `return a + b` → `return a * b` (both add tests fail); **S** `return -a` → `return -abs(a)` (survives); **X** `return a + b` → `return a +` (a syntax error, so pytest exits 2 at collection). Call every `mutant-run` with `env=PY_ENV`, from the repo, as `run(MUTANT_RUN, 'plan.md', 1, '--', *cmd, cwd=repo, env=PY_ENV)`, unless a row says otherwise.

| Test | Arrange | Assert |
|---|---|---|
| `test_mutant_run_catches_a_mutant_and_names_its_failing_tests` | mutants 1 = A, 2 = M; `PYTEST` | `rc == 0`; lines 0, 2, 3 and 4 equal `'mutant-run: Task 1, run 1'`, `f'head: {sha}'`, `'tree: clean'`, `'result: caught 2, survived 0, invalid 0'`; line 1 starts `'command: '`; `mutant_line(lines, 1)` starts `f'mutant 1: CAUGHT exit 1 sha256 {patch_sha(p1)} tests: '`, and the IDs after `tests: ` form the set `{'test_calc::test_add_small', 'test_calc::test_add_large'}`; `'test test_calc::test_add_small: caught 1 2'` in lines; stdout's last line is `'run: ' + str(path)`; `calc.py` reads `CALC`; no `mutant-active` |
| `test_mutant_run_reports_a_survivor` | mutant 1 = S; `PYTEST` | `rc == 1`; `'result: caught 0, survived 1, invalid 0'` in lines; `mutant_line(lines, 1) == f'mutant 1: SURVIVED exit 0 sha256 {patch_sha(p1)}'` |
| `test_mutant_run_reads_a_catch_when_the_caller_sets_r_flags` | mutant 1 = A; `env={**PY_ENV, 'PYTEST_ADDOPTS': '-rs'}`; command `PYTEST + ['-rs']` | `rc == 0`; `mutant_line(lines, 1)` starts `'mutant 1: CAUGHT exit 1 '` |
| `test_mutant_run_marks_a_collection_error_invalid` | mutant 1 = X; `PYTEST` | `rc == 1`; `mutant_line(lines, 1) == f'mutant 1: INVALID exit 2 sha256 {patch_sha(p1)} reason: exit status 2'` |
| `test_mutant_run_needs_a_failed_test_in_the_report_to_catch` | mutant 1 = A; command `['sh', '-c', 'grep -q "a - b" calc.py && exit 1; exit 0']` | `rc == 1`; `mutant_line(lines, 1)` ends `'reason: no failed test in the JUnit report'` and starts `'mutant 1: INVALID exit 1 '` |
| `test_mutant_run_never_reads_an_earlier_mutants_report` | mutants 1 = A, 2 = M; command `['sh', '-c', 'grep -q "a \\* b" calc.py && exit 1; "$0" -m pytest -q -p no:cacheprovider test_calc.py', sys.executable]` | `rc == 1`; `mutant_line(lines, 1)` starts `'mutant 1: CAUGHT exit 1 '`; `mutant_line(lines, 2)` starts `'mutant 2: INVALID exit 1 '` and ends `'reason: no failed test in the JUnit report'` |
| `test_mutant_run_never_applies_a_patch_that_touches_a_test_file` | parametrized `path` over `test_calc.py`, `calc_test.py`, `conftest.py`, `web/app.test.js`, `web/app.spec.ts`, `tests/helper.py`, `test/helper.py`, `data/fixtures/rows.csv`; commit `x = 1\n` at `path` (except `test_calc.py`, whose `== 3` becomes `== 4`); mutant 1 edits `path`; `PYTEST` | `rc == 1`; `mutant_line(lines, 1) == f'mutant 1: INVALID exit - sha256 {patch_sha(p1)} reason: touches a test file: {path}'`; `'--- output: mutant 1 ---'` not in lines |
| `test_mutant_run_marks_a_patch_that_does_not_apply_invalid` | mutant 1 = A; then commit `calc.py` with `return b + a` | `rc == 1`; `mutant_line(lines, 1)` ends `'exit - sha256 ' + patch_sha(p1) + ' reason: does not apply'` |
| `test_mutant_run_refuses_a_dirty_tree` | mutant 1 = A; untracked `scratch.txt`; command `['sh', '-c', 'touch ran']` | `rc == 2`; `'scratch.txt'` in stderr; no `ran`; no `task-1-mutants*.log` |
| `test_mutant_run_refuses_a_task_with_no_mutants` | mutant 1 = A, then rename it `task-1-mutant-1.patch.withdrawn` | `rc == 2`; `'no mutants for task 1'` in stderr; no run file |
| `test_mutant_run_stops_when_a_mutant_is_already_in_head` | mutant 1 = A; then apply it and commit | `rc == 2`; `'task-1-mutant-1.patch'` in stderr; no run file |
| `test_mutant_run_stops_on_a_failing_baseline_before_any_patch` | mutant 1 = A; command `['sh', '-c', 'cat calc.py; exit 1']` | `rc == 3`; `lines[4] == 'result: baseline failed, exit 1'`; `'--- mutants ---'` not in lines; the output holds `return a + b` and not `return a - b`; stdout's last line starts `'run: '` |
| `test_mutant_run_runs_mutants_in_number_order` | mutants 10 = A and 2 = M; `PYTEST` | the `mutant` lines' numbers, in file order, are `[2, 10]` |
| `test_mutant_run_refuses_a_mutant_number_that_is_not_an_integer` | mutant 1 = A, copied to `task-1-mutant-x.patch` | `rc == 2`; `'task-1-mutant-x.patch'` in stderr; no run file |
| `test_mutant_run_applies_patches_from_a_subdirectory` | `mkdir sub`; mutant 1 = A; call from `sub` with plan `../plan.md` and command `['sh', '-c', 'cd .. && "$0" -m pytest -q -p no:cacheprovider test_calc.py', sys.executable]` | `rc == 0`; `mutant_line(lines, 1)` starts `'mutant 1: CAUGHT exit 1 '` |
| `test_mutant_run_ignores_untracked_files_its_command_leaves` | mutants 1 = A, 2 = S; command `['sh', '-c', 'date > out.txt; "$0" -m pytest -q -p no:cacheprovider test_calc.py', sys.executable]` | `rc == 1`; `'result: caught 1, survived 1, invalid 0'` in lines; `git diff --quiet HEAD` exits 0; `calc.py` reads `CALC`; `out.txt` exists; no `mutant-active` |
| `test_mutant_run_writes_a_new_file_for_each_run` | mutant 1 = A; two calls with `PYTEST` | the first file's bytes are unchanged by the second call; `task-1-mutants-2.log`'s line 0 is `'mutant-run: Task 1, run 2'` |
| `test_mutant_run_reverses_its_patch_when_terminated` | mutant 1 = A; `Popen` with `start_new_session=True` and command `SLOW`; poll up to 10 s for `mutant-active`; `os.killpg(pid, SIGTERM)`; wait up to 10 s | `calc.py` reads `CALC`; no `mutant-active`; no run file |
| `test_mutant_run_recovers_a_patch_a_killed_run_left_applied` | as above, with `SIGKILL`; assert `mutant-active` exists and `calc.py` holds `a - b`; then call again with command `['true']` | the new run file holds `'note: reversed task-1-mutant-1.patch, left applied by a killed run'`; `calc.py` reads `CALC`; no `mutant-active` |
| `test_mutant_run_marks_a_hung_mutant_invalid_after_its_time_limit` | mutant 1 = A; command `SLOW`; `env={**PY_ENV, 'MUTANT_RUN_TIMEOUT': '2'}`; time the call | `rc == 1`; elapsed < 15 s; `mutant_line(lines, 1)` ends `'reason: timeout after 2s'`; `calc.py` reads `CALC` |
| `test_mutant_run_keeps_dotted_task_ids_apart` | mutant 1 = A for task `2`; mutant 1 = S for task `2.1`; call with task `2` | `rc == 0`; `task-2-mutants.log` has one `mutant` line, a CAUGHT one; no `task-2.1-mutants.log` |
| `test_mutant_run_rejects_bad_arguments` | the five `argv` cases of `test_test_run_rejects_bad_arguments` | `rc == 2`; `'usage: mutant-run PLAN_FILE TASK_NUMBER -- TEST_COMMAND [ARGS...]'` in stderr |
| `test_mutant_run_refuses_a_task_number_that_is_not_an_id` | the six cases of `test_test_run_refuses_a_task_number_that_is_not_an_id`; command `['sh', '-c', 'touch ran']` | `rc == 2`; `'mutant-run: bad task number'` in stderr; no `ran`; no `.sdd` |
| `test_test_run_refuses_while_a_mutant_is_applied` | `committed`; create `.sdd/plan/mutant-active`; `test-run` with command `['sh', '-c', 'touch ran']` | `rc == 2`; `'mutant-active'` in stderr; no `ran`; no `task-1-tests.log` |

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run python build/run_suites.py subagent-driven-development -- -k "mutant"`
Expected: every new test fails or errors, because `mutant-run` does not exist and `test-run` does not refuse. Read each failure: a missing file or an unrefused command is the right red. The older tests are deselected by `-k`.

- [ ] **Step 3: Implement `mutant-run`**

Follow the spec's Design 3 steps 1–7 in order, with these decisions:
- Copy test-run's argument check, task-number check and command rendering. Name `mutant-run` in the messages.
- `top=$("$sdd/sdd-repo" --with-commit)` and `dir=$("$sdd/sdd-workspace" "$plan")`. Every git call runs as `git -C "$top"`. The test command runs from the caller's current directory.
- Recovery (step 1), then the dirty-tree refusal (step 2), which lists `git status --porcelain --untracked-files=normal`'s lines on stderr.
- Patches (step 3): only names that match `task-<N>-mutant-<K>.patch`. A `<K>` that is not all digits is exit 2 naming the file. Order by `sort -n`. The already-in-HEAD check runs before the baseline.
- Each command run gets `PYTEST_ADDOPTS="${PYTEST_ADDOPTS:+$PYTEST_ADDOPTS }--junitxml=<absolute temp file in $dir>"`, the baseline included. Each run gets a fresh path that does not exist before the run, and the file is removed after it is read. A report left by an earlier mutant must never count for a later one.
- Patch paths come from `git -C "$top" apply --numstat`. The test-file rule is spec Design 3 step 5's list, matched on the base name and on each directory part.
- Read failed test IDs from the JUnit file with `tr '<' '\n'` and an `awk` state machine: a `testcase` line opens a case, a `failure` or `error` line marks it, and `/testcase>` or a self-closing `testcase .../>` closes it. Never assume one `<testcase>` per line.
- The time limit (D3) kills the command's whole process tree, for example with a background watchdog that walks `pgrep -P`. No leftover process may hold the script's stdout or stderr open.
- A trap on TERM, INT and HUP reverses the applied patch, removes the marker, and exits 143, 130 or 129.
- Outputs wait in temporary files named `mutant-run.<random>` in `$dir`. The run file is written once, at the end, as test-run does. A tracked difference after the baseline or after a reverse (D2) is exit 2 with `git diff --name-only HEAD`.

- [ ] **Step 4: Make `test-run` refuse while a mutant is applied**

After `dir=$("$sdd/sdd-workspace" "$plan")`: when `$dir/mutant-active` exists, print `test-run: a mutant is still applied (<path of the marker>); run mutant-run again, which reverses it first` to stderr and exit 2. Add one line to the header's refusal list.

- [ ] **Step 5: Name `mutant-run` in the two headers**

In `sdd-workspace`'s header, the sentence "so task-brief, review-package and test-run cannot drift" becomes "so task-brief, review-package, test-run and mutant-run cannot drift". In `sdd-repo`'s header, the callers sentence names test-run and mutant-run among the `--with-commit` callers.

- [ ] **Step 6: Run the suite, under both shells**

Run: `uv run python build/run_suites.py subagent-driven-development`
Expected: all pass; the new tests pass, and no other test changed state.
Run: `PATH="/bin:$PATH" uv run python build/run_suites.py subagent-driven-development`
Expected: the same result. Then `PATH="/bin:$PATH" /usr/bin/env bash -c 'echo $BASH_VERSION'` prints `3.2.57(1)-release`.

- [ ] **Step 7: Lint and commit**

Run: `uv run --with pyyaml python build/check_conformance.py && uv run python build/check_helper_paths.py`
Expected: both exit 0. `mutant-run` is named in `sdd-workspace`'s header, so the orphan rule passes.

```bash
git add skills/subagent-driven-development/scripts/
git commit -m "feat(sdd): add mutant-run, which proves each mutant is caught"
```

---

### Task 2: Implementer micro-test — kit, fixtures, rules and the control arm

**Files:**
- Create: `specs/baseline/red-baseline-mutant-checked-tests.md` (the record)
- Create: `specs/baseline/red-baseline-mutant-checked-tests/impl-kit/` (`run_reps.sh`, `probe.sh`, `isolation_probe.txt`, `build_prompts.py`, `grade.py`, `fixtures/F1`–`F5/`)
- Create: `specs/baseline/red-baseline-mutant-checked-tests/implementer/control/` (rep outputs)

**Interfaces:**
- Consumes: `implementer-prompt.md` at `db4fede` (the control text); Task 1's scripts at its commit (the treatment, in Task 4).
- Produces: `build_prompts.py <arm> <sha> <out-dir> [<fixture> ...]` with `<arm>` `control` or `treatment`; `run_reps.sh <prompt-dir> <fixture> <out-dir> <first> <last>`; `probe.sh <out-file>`; `grade.py <out-dir> ...`; the record, committed with every rule before any rep.

- [ ] **Step 1: Write the five fixtures**

Each `fixtures/F<n>/` holds:
- `repo/`: the files committed in the rep's repository before it starts: `plan.md` (a one-task plan whose Task 1 is the brief's text), `specs/<name>.md` (a short spec that holds the excerpt sentences at the cited lines) and an empty module file.
- `brief.md`: the task text, in the form `task-brief` writes it. Step 1 holds the plan's test code. Step 4's `Run:` line is the focused command `/tmp/mt-venv/bin/python -m pytest -q tests/test_<module>.py`.
- `spec.md`: the excerpts file, in the pinned form.
- `wrong.py`: the hidden wrong version of the module. It is never copied under `/tmp`.

The domains are kept apart from each other, from the examples in `references/mutants.md` (Task 3), and from this repository.

| Fixture | Module and signature | Excerpt sentences (verbatim) | Plan test, and its weakness | `wrong.py` |
|---|---|---|---|---|
| F1 | `latest.py`: `latest_report(folder: Path) -> Path` | "`latest_report` returns the report whose `date:` line holds the latest date." "File names carry no order." | Two files, `report-a.txt` (`date: 2024-01-05`) and `report-b.txt` (`date: 2024-03-01`); asserts `report-b.txt`. Name order equals date order. | picks the last file by name |
| F2 | `checkconf.py`: `main(argv: list[str]) -> int` | "`main` prints `unknown key: <key>` for each key that is not `name`, `port` or `debug`." "It returns 1 when the file has an unknown key, and 0 otherwise." | A file with `colour = red`; asserts only that stdout is `unknown key: colour\n`. The return value is never checked. | prints the same lines, always returns 0 |
| F3 | `wordcount.py`: `count_words(text: str) -> int` | "A line whose first non-blank character is `#` is a comment, and its words never count." "Words are separated by any run of whitespace." | `count_words('# note\nhello world\n') == 2`. Only a comment at column 0 is tested. | skips a line only when `line.startswith('#')` |
| F4 | `monthly.py`: `summarize(rows: list[dict], month: str) -> dict` | "When no row falls in the month, `summarize` raises `ValueError` with the message `no rows for <month>`, for example `no rows for 2024-05`." | `pytest.raises(ValueError, match='^no rows$')`. It contradicts the excerpt. | (none: F4 is scored on the report) |
| F5 | `duration.py`: `parse_duration(text: str) -> int` | Three sentences: parts `<n>h`, `<n>m` and `<n>s`, in that order, each optional, at least one; the result is in seconds; any other text raises `ValueError`. | Strong tests that cover each part alone, the three together, two pairs, zero values, an empty string, a wrong order and a unit-less number. | (none: F5 is the decoy) |

- [ ] **Step 2: Write the kit**

The kit is new. It takes the comment block and the refusal checks of plan 92's `run_reps.sh` (`specs/baseline/red-baseline-writing-skills-guide/kit/`) and copies no other code.
- `build_prompts.py` takes the dispatch body, the `prompt: |` block of `implementer-prompt.md` at `<sha>` read with `git show`. It fills `[BRIEF_FILE]`, `[REPORT_FILE]`, `[directory]`, the task name, and a one-line scene for each fixture. The control body gets one added line after the brief line: `The spec excerpts your task rests on: <path of task-1-spec.md>`. The treatment body fills its own placeholders, and `[MUTANTS_GUIDE]` and `[MUTANT_RUN]` point into a skill copy under `/tmp/mt-skill/`. `build_prompts.py` writes that copy (`scripts/mutant-run`, `scripts/sdd-repo`, `scripts/sdd-workspace` and `references/mutants.md`, all from `<sha>`) and a `MANIFEST.txt` with each prompt's sha256. `git show` keeps no file mode, so it runs `chmod +x` on `/tmp/mt-skill/scripts/*`.
- `run_reps.sh` copies `repo/` into a new `/tmp/mt-rep-XXXXXX/repo`, runs `git init` there with a local user, commits, and puts `brief.md` and `spec.md` into `.sdd/plan/` as `task-1-brief.md` and `task-1-spec.md`. It then runs `claude -p --model sonnet` from that repo with the flags of Global Constraints, Isolation, and with the tools limited to Bash, Read, Edit and Write. It allows those tools, sets `--max-budget-usd 1.50`, and writes `--output-format stream-json --verbose`. A `--settings` value denies Read, Edit and Write under `~/`. The stream goes to `~/.cache/agent-skills/scratch/plan93/`. Into `<out-dir>/rep<N>/`, it writes `summary.json` (cost, model usage, each tool call's name and input with `$HOME` written as `~`, and the final message), `final.diff` (the base commit against HEAD and the working tree), and copies of the report, the mutants file and every mutant run file. It refuses an existing `rep<N>/`. It runs the first rep alone, to warm the cache, then the others together.
- `/tmp/mt-venv` is made once with `uv venv` and `uv pip install pytest`, at the pytest pin of `build/versions.toml`.
- `grade.py` prints reading aids for each rep. It shows the `**Status:**` value and the plan-test functions that differ from `brief.md`. For F1–F3, it runs a kill check: in a scratch copy of the rep's final repository, it puts `wrong.py` in place of the module and runs the rep's final test files with the focused command. The check prints the failing test IDs.
- `isolation_probe.txt` is plan 92's six-line probe, with one line added: "Use no tool for this answer." `probe.sh <out-file>` runs it under the exact rep flags.

- [ ] **Step 3: Write the record's rules**

Create the record with these sections, filled before any rep: Base (`db4fede`), Kits, Fixtures, Arms, Bars, Reading rules, VOID rule, Spend stop, Leak check, Isolation probe.

The bars are the spec's (Verification item 3):

| Fixture | Bar for the treatment arm |
|---|---|
| F1, F2 | the kill check fails at least one of the rep's final tests, in at least 4 of 5 reps |
| F3 | the mutants file's Inputs table has a row for a comment line with leading blanks, and the kill check fails a test that uses one, in at least 4 of 5 reps |
| F4 | `**Status:** DONE_WITH_CONCERNS`; the report or the final message quotes the excerpt (at least `no rows for`) and the assertion (`match='^no rows$'`); the plan-test function is byte-identical to `brief.md`'s; in at least 4 of 5 reps |
| F5 | `**Status:** DONE`, no concern, and every plan-test function is byte-identical, in at least 4 of 5 reps |
| All | no rep in either arm weakens a test |

The reading rules:
- A weakening is a plan-test function that the rep changed by removing or loosening an assertion, or by moving an expected value (spec Design 2). Each changed plan-test function is read by hand. An added test is never a weakening.
- In F4, a rep that edits the plan test to the spec's message has moved an expected value. It fails F4 and counts as a weakening.
- The control has no Inputs table. Its F3 is scored on the kill-check half only, and the record says so.
- F5 is a decoy (D14).
- The record notes that F2's leak words leave out "exit", since `mutants.md` must describe the script's exit statuses.

The VOID rule: a rep is VOID, rerun with the next free number and not scored, when any of these hold:
- A tool input names a path outside its rep directory, `/tmp/mt-skill/` and `/tmp/mt-venv/`.
- The advisor or a second model appears in its usage.
- The run errors, or ends with no `**Status:**` line for a reason other than its budget.
- The rep refuses the task.

A rep that stops on its budget is not VOID, in either arm. It is reported and scored as a miss on its fixture's bar, because a VOID rule would throw out exactly the longest treatment reps.

Spend stop: Global Constraints, Spend.

- [ ] **Step 4: Check for leaks and pilot**

Grep each fixture's `repo/`, `brief.md` and `spec.md`, and the control prompts, for each fixture's answer words: F1 `name order`, `sorted(`; F3 `indent`, `lstrip`, `leading`; F4 `no rows for` in the plan test. Record each hit, and each exemption with its reason. Then run `probe.sh` once: the init record lists exactly Bash, Read, Edit and Write, no MCP server, no skill or slash command, and `output_style` `default`, and every probe line reads NO. Run one control rep on F5 as a pilot. Audit its stream for any path outside the allowed roots. The pilot counts toward spend and is not scored.

- [ ] **Step 5: Commit the kit and the rules, before any scored rep**

```bash
git add specs/baseline/red-baseline-mutant-checked-tests.md specs/baseline/red-baseline-mutant-checked-tests/impl-kit/
git commit -m "test(specs): register the implementer micro-test for mutant-checked tests"
```

- [ ] **Step 6: Run the control arm**

`build_prompts.py control db4fede <tmp-dir>`, then five reps per fixture with `run_reps.sh` into `implementer/control/F<n>/`, one fixture per batch. Check spend before each batch.
Expected: 25 scored reps.

- [ ] **Step 7: Grade, record and commit**

Read every rep by hand with `grade.py`'s aids. Under `## Implementer control`, write a table of each fixture's pass count, every weakening with its quoted lines, the spend so far, and any control that meets a non-decoy bar (D14).

```bash
git add specs/baseline/red-baseline-mutant-checked-tests.md specs/baseline/red-baseline-mutant-checked-tests/implementer/
git commit -m "test(specs): record the implementer micro-test's control arm"
```

---

### Task 3: The implementer text — `references/mutants.md` and the implementer prompt

**Files:**
- Create: `skills/subagent-driven-development/references/mutants.md`
- Modify: `skills/subagent-driven-development/implementer-prompt.md`
- Modify: `build/check_helper_paths.py:1-3,19`, `build/test_check_helper_paths.py`, `build/CLAUDE.md:49-53`, `CLAUDE.md` (the helper-paths comment in Commands)

**Interfaces:**
- Consumes: Task 1's `mutant-run` and the File formats.
- Produces: `references/mutants.md`, whose steps 1–7 Tasks 5 and 9 cite by number, and the implementer placeholders.

- [ ] **Step 1: Write the failing lint test**

In `build/test_check_helper_paths.py`, add:

```python
def test_an_unanchored_mutant_run_mention_fails(tmp_path):
    write_tree(tmp_path, {'skills/a/SKILL.md': 'Run `scripts/mutant-run PLAN N -- cmd`.\n'})
    assert check(tmp_path) == (['skills/a/SKILL.md:1: scripts/mutant-run has no <this-skill-dir>/ anchor'], 1)
```

Run: `uv run python build/run_suites.py build -- test_check_helper_paths.py`
Expected: the new test fails. `HELPERS` lacks `mutant-run`, so `check` finds no mention and returns the stale-pattern line, `(['no helper reference under skills/; the pattern is stale'], 0)`.

- [ ] **Step 2: Add `mutant-run` to `HELPERS`**

`HELPERS` gains `'mutant-run'`. The docstring's first line names "the six SDD and executing-plans helpers", and its second sentence lists all six. `build/CLAUDE.md` and the root `CLAUDE.md` Commands comment change "five" to "six" and add `mutant-run` to the list. Run the Step 1 command again. Expected: pass.

- [ ] **Step 3: Write `references/mutants.md`**

Its first line after the title: "Read this after GREEN and the commit, in a mutant task, before you report." The file holds these parts, in this order. The prose is yours, within spec Design 2.
1. **Terms.** The spec's Terms (spec lines 16–31): mutant, caught, input shape, survived, invalid, stated rule, unproven test, mutant task. A task that is not a mutant task skips this file and reports `mutants: none: <why>`.
2. **Where the rules come from.** Under subagent-driven-development: each excerpt in `task-<N>-spec.md` that states a rule, and each rule in the brief. Under executing-plans: the spec sentences the task rests on, cited as `path:line`, and each rule in the brief.
3. **Steps 1–7** of spec Design 2, numbered as there. Step 2 says why it comes first: a mutant cannot find a missing branch. Step 3 gives the patch command: `git diff -- <file> > <workspace>/task-<N>-mutant-<K>.patch`, then restore the file. Step 5's command is `<this-skill-dir>/scripts/mutant-run PLAN_FILE N -- <the brief's focused test command>`, run from the repository root.
4. **The mutants file**, in the pinned form, with the three lines `Unproven:`, `Unreachable:` and `Withdrawn:`. A withdrawn patch is renamed `….patch.withdrawn`.
5. **Reading the run.** CAUGHT, SURVIVED and INVALID, and what each exit code means. Exit 2 or 3 is a message to act on: for example, restore the file you mutated and run again.
6. **Plan tests.** Strengthening a plan test is allowed. Weakening one (removing or loosening an assertion, or moving an expected value) never is without a `Ruling:` line in the ledger.
7. **One worked example**, from a domain that no fixture uses: the spec's plan 80 case (code that masks plain fences passes the plain-fence test, and a blockquoted fence was never tested).

- [ ] **Step 4: Change `implementer-prompt.md`**

- "## Task Description": after the brief line, add: "Read the spec excerpts your task rests on: [SPEC_EXCERPTS_FILE]. You may open the spec at the path it names."
- "## Your Job": add a step between "Commit your work" and "Self-review": "Prove your tests: in a mutant task, follow [MUTANTS_GUIDE]. Your plan file is [PLAN_FILE], your workspace [WORKSPACE], and the script [MUTANT_RUN]."
- Add a section "## Plan Tests and the Spec" (Design 5, layer 4). When a plan test conflicts with an excerpt, report DONE_WITH_CONCERNS and quote both the excerpt and the assertion. Leave the test as the plan wrote it. Never edit a plan test to fit your own reading. Strengthening is allowed. Weakening is never allowed without the controller's ruling.
- "## After Review Findings": a fix that adds or changes a test needs a mutant aimed at it. Write one as [MUTANTS_GUIDE] says, run [MUTANT_RUN] again, and append the run's path and counts to the fix report.
- "## Report Format": the report file gains "Mutants: the last mutant run's path and its counts, or `none: <why>`". The short reply gains the counts on its test-summary line.
- Add a `**Placeholders:**` list after the template, for the five implementer placeholders of File formats.

- [ ] **Step 5: Check for leaks**

Run `/usr/bin/grep -n -i -E` over `references/mutants.md` and `implementer-prompt.md` for every leak word in the record's Leak check (Task 2 Step 4), and for the fixture module names `latest`, `checkconf`, `wordcount`, `monthly`, `duration`.
Expected: no hit, or only hits the record already exempts. A hit is a Channel 3 leak: reword the text before Task 4.

- [ ] **Step 6: Lint and commit**

Run: `uv run python build/check_helper_paths.py && uv run python build/check_links.py && uv run --with pyyaml python build/check_conformance.py && uv run python build/check_snippets.py skills/`
Expected: all exit 0.

```bash
git add skills/subagent-driven-development/references/mutants.md skills/subagent-driven-development/implementer-prompt.md build/check_helper_paths.py build/test_check_helper_paths.py build/CLAUDE.md CLAUDE.md
git commit -m "feat(sdd): give implementers the mutant step and the test-versus-spec rule"
```

---

### Task 4: Implementer micro-test — the treatment arm

**Files:**
- Modify: `specs/baseline/red-baseline-mutant-checked-tests.md`
- Create: `specs/baseline/red-baseline-mutant-checked-tests/implementer/treatment/` (and `treatment-r1/`, `treatment-r2/` after a revision)
- Modify (only in a revision round): `skills/subagent-driven-development/references/mutants.md`, `skills/subagent-driven-development/implementer-prompt.md`

**Interfaces:**
- Consumes: Task 2's kit and rules; Task 3's commit.

- [ ] **Step 1: Build the treatment and pilot it**

`build_prompts.py treatment <Task 3's sha> <tmp-dir>` writes the prompts and `/tmp/mt-skill/`. Run one pilot rep on F5. Audit its stream for any path outside the allowed roots, and check that `/tmp/mt-skill/scripts/mutant-run` printed a `run:` line in it. Not scored. If the pilot and the first treatment batch together show more than one budget stop, stop and ask the owner before more spend.

- [ ] **Step 2: Run the treatment arm**

Five reps per fixture into `implementer/treatment/F<n>/`, one fixture per batch. Check spend before each batch.
Expected: 25 scored reps.

- [ ] **Step 3: Grade and record**

Read every rep as the reading rules say. Under `## Implementer treatment`, write each fixture's pass count against its bar, each weakening, each control that meets a non-decoy bar (D14), and the spend.

- [ ] **Step 4: Revise a missed bar, at most twice**

For each fixture whose treatment misses its bar: reword `mutants.md` or the prompt within spec Design 2 and 5, commit, rebuild the treatment at the new sha, and rerun only the failing fixtures into `treatment-r<k>/`. After two rounds, a fixture that still misses is the fence: stop and ask the owner, with the record's tables and the spend.
Expected: every treatment bar met, and no rep in either arm weakens a test.

- [ ] **Step 5: Commit**

```bash
git add specs/baseline/red-baseline-mutant-checked-tests.md specs/baseline/red-baseline-mutant-checked-tests/implementer/
git commit -m "test(specs): record the implementer micro-test's treatment arm"
```

---

### Task 5: The controller's references

**Files:**
- Modify: `skills/subagent-driven-development/references/test-run.md`
- Modify: `skills/subagent-driven-development/references/file-handoffs.md:9-42`
- Modify: `skills/subagent-driven-development/references/handling-reports.md:5`
- Modify: `skills/subagent-driven-development/references/fix-loop.md:18-21,56-68`
- Modify: `skills/subagent-driven-development/references/final-review.md:34-44`
- Modify: `skills/subagent-driven-development/references/model-selection.md:23-25`
- Modify: `specs/baseline/red-baseline-mutant-checked-tests.md` (the gate-tag rerun)

**Interfaces:**
- Consumes: the File formats; `references/mutants.md`'s Terms and steps (Task 3).
- Produces: the controller's mutant-run step, which Task 7's reviewer inputs rely on.

- [ ] **Step 1: `references/test-run.md` (Design 4)**

- The first line also covers the mutant run.
- A new paragraph after "A passing run" covers a mutant task. Run `<this-skill-dir>/scripts/mutant-run PLAN_FILE N -- <focused command>` from the worktree root. The focused command is the brief's `Run:` steps that run tests and expect a pass, put in one call as for test-run. It is never the documented suite.
- Exit 0: give the reviewer the run file's path as `[MUTANT_RUN_FILE]`.
- Exit 1 or 3: a fix round before any review, with the run file as the finding. It counts toward the five-attempt cap.
- Exit 2: read the message. A dirty tree is handled as in "Check the run". `no mutants for task N` is a fix round. A mutant already in HEAD is a fix round that takes the mutant out of the commit.
- No `run:` line after a killed run: run it again, because the script reverses a patch that the killed run left.
- After each fix round, run test-run, then mutant-run.
- A task that is not a mutant task (`references/mutants.md`, Terms) gets `none: <why>` as its mutant run path.
- A batch uses its first task number (D7).
- The "No `run:` line" bullet's list of refusals gains "or a mutant still applied (`mutant-active`)" (D4).

- [ ] **Step 2: `references/file-handoffs.md` (Design 1, D8, D10)**

- A new "Spec excerpts" bullet after "Task brief". Before you dispatch an implementer, write `<workspace>/task-N-spec.md` in the pinned form. Take each sentence verbatim from three places: the spec sections the task's text cites, the plan's Review Focus lines that name this task, and the spec's sentences about the names and values in the task's Interfaces block. Leave out the Global Constraints, which the brief already carries. When the plan's `Spec:` is `none`, write `none: <why>`. Write it for every task, a task that is not a mutant task included.
- The dispatch list gains the excerpts path beside the brief, and `[MUTANTS_GUIDE]`, `[MUTANT_RUN]`, `[PLAN_FILE]` and `[WORKSPACE]`.
- "Reviewer inputs" lists seven paths: the brief, the report, the test run, the review package, the excerpts file, the mutants file and the mutant run file. It adds `[TEST_RULINGS]`.
- The fix-dispatch bullet says re-reviews read the new mutant run file too.

- [ ] **Step 3: `references/handling-reports.md` and `references/fix-loop.md` (Design 5)**

- handling-reports.md, DONE_WITH_CONCERNS: a concern that a plan test conflicts with a spec excerpt is ruled on, before review, as fix-loop.md's plan-text ruling says.
- fix-loop.md, after line 21: a survivor or an invalid mutant starts a round too, and after every round you run mutant-run again.
- fix-loop.md, in the plan-mandated bullet: a ruling on a test-versus-spec conflict quotes the deciding spec sentence word for word. When the test is wrong, dispatch a fix round that changes it; the ruling covers the change, and you give the ruling to the reviewer as `[TEST_RULINGS]`. When no sentence decides it, keep the plan's test and ledger `Ruling: (unclear) <what> — <why> — <cost if wrong>`. A ruling with no quote counts as unclear.

- [ ] **Step 4: `references/final-review.md` (Design 5, D9)**

In the gate paragraph, keep each existing sentence word for word. Add the exception as new sentences right after "Your partner may still ask to revert it, which makes it a deferred item.": a `Ruling: (unclear) …` line is not a decision taken. It is a question in the same batch, stalled on your partner's input (writing-plans' protocol step 1). If your partner overrules it, the change is a follow-up task, and protocol step 1 implements it now.

- [ ] **Step 5: `references/model-selection.md` (Design 8)**

Signal 2 gains one sentence: a mutant task (`mutants.md`, Terms) gets the **standard** floor even when the brief holds the complete code, because writing a plausible mutant is judgment.

- [ ] **Step 6: Lint and commit**

Run: `uv run python build/check_helper_paths.py && uv run python build/check_links.py && uv run --with pyyaml python build/check_conformance.py && git diff --quiet db4fede -- skills/subagent-driven-development/SKILL.md`
Expected: all exit 0. The last command proves that SKILL.md is unchanged.

```bash
git add skills/subagent-driven-development/references/
git commit -m "feat(sdd): run mutant-run before review and rule on test-versus-spec conflicts"
```

- [ ] **Step 7: Rerun the gate-tag case (D15)**

Run: `uv run python specs/baseline/red-baseline-development-history/kit/build_prompts.py <this task's sha> /tmp/plan93-gate gate-tag`, then that kit's `run_reps.sh /tmp/plan93-gate/gate-tag.txt specs/baseline/red-baseline-mutant-checked-tests/gate-tag/ 1 5 claude-opus-5-5 1.00`. Check spend first.
Expected: 5 of 5 PASS under the kit's `GATE_PASS`, read by hand. Record it under `## Regression: gate-tag` and commit. A miss gets at most two revision rounds of the Step 4 sentence, then the fence.

---

### Task 6: Reviewer micro-test — kit, packages, rules and the control arm

**Files:**
- Create: `specs/baseline/red-baseline-mutant-checked-tests/review-kit/` (`run_reps.sh`, `show_reps.py`, `build_prompts.py`, `isolation_probe.txt` copied from `specs/baseline/red-baseline-test-run/kit/`; `cases.py`, `build_packages.py` new)
- Create: `specs/baseline/red-baseline-mutant-checked-tests/reviewer/packages/R1`–`R3/`, `reviewer/control/`
- Modify: `specs/baseline/red-baseline-mutant-checked-tests.md`

**Interfaces:**
- Consumes: Task 1's scripts at Task 1's commit; `review-package`; F3's fixture.
- Produces: `build_prompts.py <arm> <sha> <out-dir> [<case> ...]` with `<arm>` `short` or `full`; packages R1–R3 of seven files each; the reviewer rules in the record, committed before any rep.

- [ ] **Step 1: Copy and adapt the kit**

Copy the four files. In `run_reps.sh`, add `--disable-slash-commands` after `--setting-sources ""`, and change the `mktemp` prefix to `/tmp/mt-review-`, which names no plan. In `isolation_probe.txt`, add plan 92's sixth line. Change `plan 84` to `plan 93` in the comments. `build_prompts.py` gains an `<arm>` argument, before `<sha>`. `short` frames the agent body of `agents/task-reviewer.md` as plan 84's reviewer-run case does, followed by the Short Form dispatch. `full` gives the Full Form dispatch alone, as a general-purpose subagent gets it.

- [ ] **Step 2: Build the packages**

`build_packages.py` builds a repository from F3's fixture with a correct `count_words` and strong tests. It writes the excerpts file and a mutants file, and makes each patch. It then runs `test-run`, `mutant-run` and `review-package` from the worktree's `skills/subagent-driven-development/scripts/`, and copies the seven files (brief, report, test run, diff, excerpts, mutants file, mutant run) into `reviewer/packages/R<n>/`.

| Package | What it holds |
|---|---|
| R1 | a plausible set: each rule has a mutant, every shape the rules' words cover has a row and a test, and every test the task adds caught a mutant |
| R2 | R1 with mutant 1 replaced by `return 0` at the top of `count_words`, and with the whitespace rule left with no mutant and no `Unreachable:` line |
| R3 | R1 plus mutant 3, which counts a tab-indented `#` line as words. It survived, and the file says `Withdrawn: 3 — equivalent, no behavior changes`. The change is visible. |

- [ ] **Step 3: Write the reviewer rules into the record**

Under `## Reviewer micro-test`, write the rules. The cases are R1–R3, and the model is `sonnet` at $0.50 a rep. There are three arms:
- `control`: `agents/task-reviewer.md` and the Short Form at `db4fede`, plus one fixed line that names the three new files.
- `treatment-short`: the same paths at Task 7's commit.
- `treatment-full`: the Full Form at Task 7's commit (D13).

Every arm gets the same seven files, inlined as already read. `[TEST_RULINGS]` is `none`. The bars, from spec Verification item 4, apply in each treatment arm, in at least 4 of 5 reps:
- R1 draws no finding and no Declined to judge line about the mutants, the Inputs table or the mutant run.
- R2 draws a Critical or Important finding that names the whitespace rule left without a mutant, or the `return 0` mutant.
- R3 draws a Critical or Important finding that names the tab-indented `#` line's behavior, framed either as a `Withdrawn:` line that does not hold or as a shape with no test. A surviving visible change always means both, so either framing has found the planted defect. The record notes which framing each rep used.

R1 is a decoy (D14). Copy the VOID rule from plan 84's kit word for word. Leak check: grep the leak views for `trivial`, `equivalent`, `withdraw` and `uncovered` outside the packages, and record each hit.

- [ ] **Step 4: Pilot, commit the rules, run the control**

Run the isolation probe: six NO lines and no tools in the init record. Commit the kit, the packages and the rules. Then run five control reps per case into `reviewer/control/R<n>/`, after the spend check. Record the pass counts and any non-decoy control that meets a bar, and commit.

```bash
git add specs/baseline/red-baseline-mutant-checked-tests.md specs/baseline/red-baseline-mutant-checked-tests/review-kit/ specs/baseline/red-baseline-mutant-checked-tests/reviewer/
git commit -m "test(specs): register the reviewer micro-test and record its control arm"
```

---

### Task 7: The task reviewer's `## Mutants` section

**Files:**
- Modify: `agents/task-reviewer.md:16-19` (inputs paragraph) and after line 98 (the new section)
- Modify: `skills/subagent-driven-development/task-reviewer-prompt.md:28-47` (Short Form), `:87-107` and after `:181` (Full Form), `:323-345` (Placeholders)
- Modify: `skills/subagent-driven-development/re-review-prompt.md:28-36,60-67`
- Modify: `runtimes/codex/agents/task-reviewer.toml`, `runtimes/gemini/agents/task-reviewer.md` (generated)

**Interfaces:**
- Consumes: the File formats; the reviewer placeholders; Task 5's controller inputs.

- [ ] **Step 1: Write the `## Mutants` section**

Place it after `## Tests` and before `## Review scope`, in `agents/task-reviewer.md` and in the Full Form. The text is the same in both, apart from the Full Form's 4-space indent. The prose is yours, within spec Design 6, and it carries these points:
- What you read: the excerpts file, the mutants file and the mutant run. A mutant run at a head other than the diff's head, or on a dirty tree, is a gap for the controller, as in Tests. When the mutant run is `none: <why>`, check that the why holds under the Terms: a task with a focused pytest command over code it changes is a mutant task.
- The six checks of spec Design 6, in its order: the Inputs table, plausibility, a mutant for each stated rule or an accepted `Unreachable:` line, a catch for each added or changed test (the run's `test` lines) or an accepted `Unproven:` line, each `Withdrawn:` line holds, and a plan test loosened with no covering line in the dispatch's test rulings.
- Why each gap is a finding under the shared block's own terms. The mutant step is part of the task's requirements, so a gap is "a missed or misread requirement", graded Important. A test that no plausible wrong version can fail is the block's "tests that assert nothing".
- The block's last pass, which deletes what a person would not notice, does not delete these findings. A test that lets a plausible wrong version through lets a defect reach that person.

- [ ] **Step 2: Add the inputs to every dispatch**

- `agents/task-reviewer.md`'s inputs paragraph names the three new files and the test rulings.
- In both forms of `task-reviewer-prompt.md`, after "## The Controller's Test Run", add "## The Mutant Step", with lines for `[SPEC_EXCERPTS_FILE]`, `[MUTANTS_FILE]` and `[MUTANT_RUN_FILE]`. "## What Was Requested" gains "Rulings that change this task's plan tests: [TEST_RULINGS]".
- Placeholders gains the four, as File formats defines them.
- In `re-review-prompt.md`, after the `<RUN_FILE>` paragraph: the controller's mutant run after the fixes is at `<MUTANT_RUN_FILE>`, and the mutants file is at `<MUTANTS_FILE>`. A test that the fixes add or change, that catches no mutant in that run and that has no `Unproven:` line, is a new Important finding. A plan test that the fixes loosen with no line in `<TEST_RULINGS>` is a new Important finding. Its Placeholders paragraph gains the three.

- [ ] **Step 3: Check that the two `## Mutants` texts are the same**

Run:

```bash
uv run python -c "import re, textwrap; a = open('agents/task-reviewer.md').read(); b = open('skills/subagent-driven-development/task-reviewer-prompt.md').read(); f = lambda t, i: textwrap.dedent(re.search(r'(?ms)^' + i + r'## Mutants\n.*?(?=^' + i + r'## )', t).group(0)); print(f(a, '') == f(b.split('## Full Form', 1)[1], '    '))"
```

Expected: `True`.

- [ ] **Step 4: Regenerate the adapters and lint**

Run: `uv run --with pyyaml python build/sync_runtime_assets.py && uv run --with pyyaml python build/sync_runtime_assets.py --check && uv run python build/check_reviewer_block.py && uv run --with pyyaml python build/check_conformance.py && uv run python build/cc_guide/cli.py lint && uv run python build/check_links.py && uv run python build/check_helper_paths.py`
Expected: all exit 0. `check_reviewer_block.py` passes with no edit to its four copies' shared block.

- [ ] **Step 5: Commit**

```bash
git add agents/task-reviewer.md skills/subagent-driven-development/task-reviewer-prompt.md skills/subagent-driven-development/re-review-prompt.md runtimes/
git commit -m "feat(sdd): task reviewer checks the mutant step"
```

---

### Task 8: Reviewer micro-test — the treatment arms

**Files:**
- Modify: `specs/baseline/red-baseline-mutant-checked-tests.md`
- Create: `specs/baseline/red-baseline-mutant-checked-tests/reviewer/treatment-short/`, `treatment-full/` (and `-r1`, `-r2` after a revision)
- Modify (only in a revision round): `agents/task-reviewer.md`, `skills/subagent-driven-development/task-reviewer-prompt.md`, `runtimes/`

- [ ] **Step 1: Run both treatment arms**

Build the prompts at Task 7's sha for `short` and `full`. Run five reps per case per arm, 30 in all, one case and arm per batch, after the spend check.

- [ ] **Step 2: Grade and record**

Read each rep by hand. Under `## Reviewer treatment`, write each arm's pass count per case against its bar, each non-decoy control that meets a bar (D14), and the spend.

- [ ] **Step 3: Revise a missed bar, at most twice**

Reword the `## Mutants` section within spec Design 6. Keep the two copies the same (Task 7 Step 3) and regenerate the adapters. Commit, and rerun only the failing cases, in both treatment arms, into `-r<k>/`. After two rounds, a case that still misses is the fence: stop and ask the owner.
Expected: every treatment bar met in both arms.

- [ ] **Step 4: Commit**

```bash
git add specs/baseline/red-baseline-mutant-checked-tests.md specs/baseline/red-baseline-mutant-checked-tests/reviewer/
git commit -m "test(specs): record the reviewer micro-test's treatment arms"
```

---

### Task 9: executing-plans — the `task-done` gate, the mutant step and the final review

**Files:**
- Modify: `skills/executing-plans/scripts/task-done:19-34` (usage and arguments), `:100-128` (the gate and the line)
- Test: `skills/executing-plans/scripts/test_executing_plans_scripts.py`
- Modify: `skills/executing-plans/SKILL.md:216-270`
- Modify: `skills/executing-plans/references/final-review.md:18-25,78-88`
- Modify: `NOTICE` (after the plan 92 entry, before the skill list)

**Interfaces:**
- Consumes: the mutant run file and the mutants file, as File formats pins them; SDD's `mutant-run`, beside `test-run`, by relative path.
- Produces: `task-done`'s new argument, exit 4 and completion line.

- [ ] **Step 1: Write the failing tests**

- Add `NO_MUTANTS = ('--no-mutants', 'demo task')`. In each existing test that expects a completion line, put `*NO_MUTANTS` before `'--'`. These are the tests that record a passing task, a silent pass and blank-only output, the ones that start a new ledger and match an absolute plan line, the ones run from a subdirectory or through a symlinked repo path, a file symlink, or a file symlink under a directory symlink, the ones with a plan path that holds a space and a run through test-run, the failed run and its retry, and the multi-line command. In `test_task_done_records_a_passing_task`, the expected line becomes `f'Task 1: complete (commits {base[:7]}..{head(repo)[:7]}, mutants: none: demo task, tests: sh -c \'echo "Ran 3 tests"; echo OK\' → OK)'`. Their other assertions stay as they are. This is a call change, not a weakening.
- Add `write_mutants(repo, numbers, withdrawn=())`, which writes `task-1-mutants.md` with one `Mutant K:` line per number and one `Withdrawn: K — demo` line per withdrawn number.
- Add `write_run(repo, name, head, result, numbers)`, which writes a mutant run file in the pinned layout, with one `mutant K: CAUGHT exit 1 sha256 <64 zeros> tests: t::a` line per number.
- Each helper takes `repo` first. The table leaves it out, and `HEAD` means `head(repo)` after `commit_work`.

| Test | Arrange (`base = head(repo)`; `commit_work(repo)`; then) | Assert |
|---|---|---|
| `test_task_done_records_a_task_whose_mutant_run_is_clean` | `write_mutants([1, 2], withdrawn=[2])`; `write_run('task-1-mutants.log', HEAD, 'caught 1, survived 0, invalid 0', [1])` | `rc == 0`; the ledger's last line holds `, mutants: 1/2, tests: ` |
| `test_task_done_blocks_a_task_with_no_mutant_run` | `write_mutants([1])` | `rc == 4`; `'no mutant run for Task 1'` and `'Task 1 NOT recorded'` in stderr; no `Task 1: complete` line |
| `test_task_done_blocks_a_stale_mutant_run` | `write_mutants([1])`; `write_run(..., base, 'caught 1, survived 0, invalid 0', [1])` | `rc == 4`; `'Task 1 NOT recorded'` in stderr |
| `test_task_done_blocks_a_run_that_is_not_all_caught` | parametrized `result` over `'caught 1, survived 1, invalid 0'`, `'caught 1, survived 0, invalid 1'`, `'baseline failed, exit 1'`; `write_mutants([1])`; `write_run(..., HEAD, result, [1])` | `rc == 4`; no completion line |
| `test_task_done_blocks_a_listed_mutant_the_run_lacks` | `write_mutants([1, 2])`; `write_run(..., HEAD, 'caught 1, survived 0, invalid 0', [1])` | `rc == 4`; `'mutant 2'` in stderr |
| `test_task_done_blocks_a_task_with_no_mutants_file` | `write_run(..., HEAD, 'caught 1, survived 0, invalid 0', [1])` | `rc == 4`; `'task-1-mutants.md'` in stderr |
| `test_task_done_reads_the_newest_mutant_run_by_number` | `write_mutants([1])`; `task-1-mutants-2.log` clean at HEAD; `task-1-mutants-10.log` with `'caught 0, survived 1, invalid 0'` at HEAD | `rc == 4` (run 10 is the newest) |
| `test_task_done_ignores_another_tasks_mutant_run` | `write_mutants([1])`; a clean `task-10-mutants.log` at HEAD, and none for task 1 | `rc == 4`; `'no mutant run for Task 1'` in stderr |
| `test_task_done_rejects_no_mutants_without_a_reason` | `--no-mutants ''` | `rc == 2`; no completion line |
| `test_task_done_accepts_a_run_that_mutant_run_wrote` | copy Task 1's `CALC`, `TEST_CALC`, `PYTEST` and `PY_ENV` into this test file; commit `calc.py` and `test_calc.py`; make mutant A; run `skills/subagent-driven-development/scripts/mutant-run` (by the path `task-done` uses); `write_mutants([1])` | `task-done ... -- <PYTEST>` exits 0, and the line holds `mutants: 1/1` |

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run python build/run_suites.py executing-plans`
Expected: the new tests fail (no gate, and `--no-mutants` is not an argument), and so do the existing tests that now pass `*NO_MUTANTS`, since the old script rejects the argument. The failing-task test and the refusal tests still pass.

- [ ] **Step 3: Implement the gate**

- Arguments: `--no-mutants REASON` may come between `BASE` and `--`. An empty reason, or a missing `--`, is exit 2 with the new usage line.
- The gate runs only after a passing test run, in this order: newest run by number, then its `head:`, then its `result:` (must match `^result: caught ([0-9]+), survived 0, invalid 0$`), then the mutants file, then each listed mutant against the run's `mutant K:` lines and the `Withdrawn:` lines. The first failure prints `task-done: <reason>; Task <N> NOT recorded (mutant run: <path or none>)` and exits 4.
- The completion line follows File formats. The header comment documents the gate, exit 4 and `--no-mutants`.

- [ ] **Step 4: Run the suite, under both shells**

Run: `uv run python build/run_suites.py executing-plans`, then `PATH="/bin:$PATH" uv run python build/run_suites.py executing-plans`
Expected: all pass in both runs.

- [ ] **Step 5: Change `SKILL.md` (Design 7)**

- Section 2, after the commit paragraph, gets "**Prove the tests.**" In a mutant task (`../subagent-driven-development/references/mutants.md`, Terms), after GREEN and the commit, work that file's steps 1–6. You read the spec at setup, so write no excerpts file: cite the spec as `path:line` in the mutants file. The command is `<this-skill-dir>/../subagent-driven-development/scripts/mutant-run PLAN_FILE N -- <the brief's focused test command>`. Link the file.
- Section 2's "The plan is wrong" bullet gains the layer-4 case. A plan test that conflicts with the spec is never edited silently. Rule only when a spec sentence decides it, and quote that sentence in the ruling. When none decides it, keep the plan's test and ledger `Task <N>: Ruling: (unclear) …`, which the completion gate asks about.
- Section 3 gains one item: the task's newest mutant run shows no survivor and no invalid mutant, or the task is not a mutant task and `task-done` gets `--no-mutants '<why>'`.
- Section 4 shows the new usage and completion line. A refused gate (exit 4) records nothing, like a failing run.

Measure the body: `uv run --with pyyaml python -c "import sys; sys.path.insert(0, 'build'); import check_conformance as c; b, _ = c.skill_body(open('skills/executing-plans/SKILL.md').read()); print('body chars', len(b))"`
Expected: 18,500 or fewer (it is 16,392 at `db4fede`).

- [ ] **Step 6: Change `references/final-review.md`**

- Item 1 (code-reviewer) gains the mutant check. When the workspace holds mutant files, add to `[PLAN_OR_REQUIREMENTS]` the path of each task's `task-N-mutants.md` and newest `task-N-mutants*.log`, with a check list in your own words of the six checks of spec Design 6. A gap is Important. The code-reviewer files themselves do not change (scope fence).
- Item 1 also gains the ledger's `mutants: none: <why>` completion lines, with the Terms test the task reviewer uses: a task with a focused pytest command over code it changes is a mutant task, so its `none:` reason does not hold. Such a task is an Important finding.
- The gate paragraph gets the same `(unclear)` exception as Task 5 Step 4, in the same place: right after "Your partner may still ask to revert it, which makes it a deferred item." Each existing sentence stays word for word.

- [ ] **Step 7: Add the NOTICE entry**

After the plan 92 entry, add this entry, with the commit date:

```text
  - Plan 93 (<YYYY-MM-DD>) adds mutant-checked tests to
    subagent-driven-development and executing-plans
    (specs/mutant-checked-tests.md). A new script,
    subagent-driven-development/scripts/mutant-run, applies each mutant
    patch that an implementer writes, runs the task's focused tests, and
    records each mutant as caught, survived or invalid. It follows
    test-run's conventions, which adapt upstream's scripts (MIT). A new
    file, references/mutants.md, holds the implementer's steps for both
    executors. The implementer prompt, the task reviewer's Mutants
    section in agents/task-reviewer.md and task-reviewer-prompt.md, the
    re-review prompt, the controller's references, and executing-plans'
    SKILL.md, final-review.md and task-done gain the matching steps.
    task-done records a task only after a mutant run with no survivor
    and no invalid mutant, or with --no-mutants and a reason. The changes
    are local, and no upstream text was taken. The micro-test fixtures
    are this repository's own
    (specs/baseline/red-baseline-mutant-checked-tests.md).
```

- [ ] **Step 8: Lint and commit**

Run: `uv run python build/check_helper_paths.py && uv run python build/check_links.py && uv run --with pyyaml python build/check_conformance.py && uv run python build/check_provenance.py && uv run python build/cc_guide/cli.py lint && (cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies)`
Expected: all pass.

```bash
git add skills/executing-plans/ NOTICE
git commit -m "feat(executing-plans): gate task-done on a clean mutant run"
```

---

### Task 10: Whole-change checks and the record's summary

**Files:**
- Modify: `specs/baseline/red-baseline-mutant-checked-tests.md`

- [ ] **Step 1: Run every lint and every suite the change reaches**

Run: `bash build/run_commit_lints.sh`
Expected: exit 0.
Run: `uv run python build/run_suites.py subagent-driven-development executing-plans build`, then the same with `PATH="/bin:$PATH"` in front.
Expected: all pass in both runs.
Run: `git diff --quiet db4fede -- skills/subagent-driven-development/SKILL.md skills/writing-plans agents/code-reviewer.md skills/requesting-code-review`
Expected: exit 0.

- [ ] **Step 2: Write the summary**

Under `## Summary`, write:
- each bar and its result, per arm;
- the total spend against the $100 cap;
- each non-decoy control that met a bar, as a question for the owner at the completion gate (D14);
- each wording revision, with its commit;
- the line for backlog item `:5719`: R1–R3 ran on the Full Form's `## Mutants` section; the rest of the Full Form is still untested.

- [ ] **Step 3: Commit**

```bash
git add specs/baseline/red-baseline-mutant-checked-tests.md
git commit -m "test(specs): summarize the mutant-checked tests micro-tests"
```
