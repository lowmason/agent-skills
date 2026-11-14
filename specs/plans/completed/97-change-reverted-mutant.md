# Change-reverted mutant Implementation Plan

**Status: COMPLETE (2026-11-14)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `mutant-run` also run the task's tests against the task's code as it was at BASE. A new or changed test that passes on that pre-change code then shows to the implementer and the reviewer.

**Architecture:** `mutant-run` gains a required BASE argument. After the agent mutants, it makes one more in-place run: the revert, the reverse of the task's diff from BASE over every path except test files and project config files. A new `--- revert ---` section of the run file lists that run's JUnit report test by test. The section stays outside the `result:` line, the `--- mutants ---` and `--- tests ---` sections and the exit status. The implementer's guide, the controller's references, the task reviewer's `## Mutants` section (a new check 7) and executing-plans read it. `task-done` checks only that the revert ran at its BASE. Two pre-registered micro-tests check the behavior-shaping text. Each runs a control arm on today's text before the new text exists.

**Tech Stack:** bash (macOS 3.2 compatible), git, pytest JUnit XML; Markdown skill text; pytest suites that drive the scripts as subprocesses; `claude -p` micro-test kits; the repo's commit lints (`build/run_commit_lints.sh`).

**Spec:** `specs/completed/change-reverted-mutant.md` (approved 2026-11-13). Its Terms, Design, Verification and Constraints sections are authoritative. Read it in full before Task 1. It builds on plan 93's spec, `specs/completed/mutant-checked-tests.md`, whose Terms still hold.

## Global Constraints

### Base and execution

- **No execution starts before plan 96's execution ends.** Plan 96 (marimo notebook seam, Plan A) runs in another session. Its controller uses `mutant-run`, `task-done` and the task reviewer live, through the symlinks into the main checkout. The owner's rule is that no plan execution starts while another runs.
- **Base commit.** Every line number in this plan is a line of the file at `99b876e`. Before Task 1, run `git diff --stat 99b876e HEAD -- skills/subagent-driven-development skills/executing-plans agents/task-reviewer.md runtimes NOTICE`. Plan 96 changes `NOTICE`, so expect it there. Any other output means a file this plan edits changed after planning: re-read each cited line before a task quotes it, and ledger a `Ruling:` for any task text that no longer fits.
- **Base branch.** The spec and this plan exist only on `claude/change-reverted-mutant-design-924c04` until that branch merges. Cut the execution worktree from `main` after the merge, or from that branch before it.
- **Self-modifying plan.** This plan edits the skills, scripts and agent that execute it. `~/.claude/skills/` and `~/.claude/agents/` are symlinks into the main checkout. Execute in a worktree. Call the controller tooling by absolute path through those symlinks, with the worktree as the working directory: `~/.claude/skills/subagent-driven-development/scripts/<name>` under subagent-driven-development, and `~/.claude/skills/executing-plans/scripts/task-start` and `task-done` under executing-plans. Do not merge this branch into the main checkout before the plan completes. Implementers and reviewers use the installed copies, which are main's.
- **This plan's own mutant step.** Main's copies carry plan 93's mutant step. Tasks 1, 2 and 3 have focused pytest commands over code they change. So they run that step with main's `mutant-run` (no BASE argument, no revert), and their reviewers read main's `## Mutants` section. The worktree's `mutant-run` is only the code under test. Every other task records `none: <why>` for its mutant run.
- **Scope fence.** These are out of bounds. When the only fix crosses one, stop and ask the owner.
  - `skills/subagent-driven-development/SKILL.md` stays byte-identical (spec, Constraints).
  - The shared reviewer block (`## Review scope` to `## Declined to judge`) stays identical in its four copies. `agents/code-reviewer.md` and `skills/requesting-code-review/` do not change.
  - Agent-mutant verdicts, the `result:` line, the `--- mutants ---` and `--- tests ---` sections and `mutant-run`'s exit codes keep plan 93's meanings (spec, Non-goals).
  - Plan 93's record and kits under `specs/baseline/red-baseline-mutant-checked-tests/` do not change (D1).
  - `skills/writing-plans/` does not change.
  - Shipping implementer or reviewer text whose treatment arm still misses a bar after two revision rounds (spec, Verification item 3).
  - Any micro-test batch that would take the plan's micro-test spend past **$60** (spec, Verification item 3).
- **Owner stops under subagent-driven-development.** An implementer cannot ask the owner. Where a step says "stop and ask the owner", the implementer reports BLOCKED with the quoted results and the running spend. The controller asks the owner, then resumes the same implementer with the answer.
- **Cross-skill references** use bare skill names, never a `superpowers:` namespace.

### Scripts

- **Bash 3.2.** `mutant-run` and `task-done` run under macOS `/bin/bash` 3.2.57, as plan 93's Global Constraints, Scripts, say: no `declare -A`, `mapfile`, `${v,,}`, `|&` or negative indexes, and `${a[@]+"${a[@]}"}` for a possibly empty array. Each script task runs its suite a second time with `PATH="/bin:$PATH"`.
- **Portability.** No macOS-only or GNU-only tool. Every git call that names a path runs as `git -C <top>`. Changed paths are read NUL-separated (`-z`) and passed to git as `:(literal)<path>` pathspecs, so a path with a space or a glob character survives (Review Focus 2).
- **Tests** drive each script as a subprocess, as the existing suites do: single quotes, f-strings, 4-space indentation, stdlib plus pytest, Python as pinned in `build/versions.toml`. Run them through `build/run_suites.py`. State count changes as deltas, never totals.

### File formats

These forms are pinned. Every task that writes or reads one uses them exactly.

**`mutant-run`.** `<this-skill-dir>/scripts/mutant-run PLAN_FILE TASK_NUMBER BASE -- TEST_COMMAND [ARGS...]`
- A call without BASE prints `usage: mutant-run PLAN_FILE TASK_NUMBER BASE -- TEST_COMMAND [ARGS...]` and exits 2.
- BASE that `git -C <top> rev-parse --verify --quiet '<BASE>^{commit}'` cannot resolve: exit 2, `mutant-run: bad BASE: <BASE>`. BASE that is not an ancestor of HEAD: exit 2, `mutant-run: HEAD is not a descendant of BASE <BASE>`. Both checks run after recovery and before the dirty-tree refusal (D4).
- Exit codes are otherwise plan 93's. stdout: the `result:` line, each `mutant` line, the `revert:` line, then `run: <path>` last (D6).

**Run file.** Plan 93's form, with two header lines and two sections added:

```text
mutant-run: Task <N>, run <K>
command: <the command, rendered as test-run renders it>
head: <full sha of HEAD>
base: <full sha of BASE>
tree: clean
result: caught <c>, survived <s>, invalid <i>
note: reversed <patch file name>, left applied by a killed run
revert: <one of the forms below>
--- mutants ---
mutant <K>: ...
--- tests ---
test <id>: caught <K>[ <K> ...]
--- revert ---
path: <one reverted path>
sha256: <64 hex digits of the revert patch file>
failed <id>: <the first line of the failure's message>
not loaded <name>: <the cause line>
skipped <id>: <the skip reason>
passed <id>
--- output: baseline ---
--- output: mutant <K> ---
--- output: revert ---
<the revert run's output>
```

- The `revert:` forms: `revert: ran, exit <n>, failed <f>, not loaded <u>, skipped <s>, passed <p>`; `revert: ran, exit <n>, no report`; `revert: timeout after <n>s`; `revert: not applied: <reason>`; `revert: none: no file outside the tests and the project config changed` (exact text, D10).
- `--- revert ---` exists whenever a revert patch was built. It holds one `path:` line per reverted path in `git diff` order, the `sha256:` line, and, for the first form only, one line per JUnit test case in report order. `--- output: revert ---` exists only when the revert's command ran. A `none` revert writes neither section and no patch file.
- `<id>` is `<classname>::<name>`, unescaped, as in `mutant` lines. `<name>` on a `not loaded` line is the collection failure's `name` attribute. The cause line is the last line of the `<error>` element's text that starts with `E `, with that prefix and the spaces after it removed, or the `message` attribute when no line starts so (D5). A skip reason is the `<skipped>` element's `message` attribute.
- A failing baseline writes the header through `note:` with `base:` and `result: baseline failed, exit <n>`, no `revert:` line, then `--- output: baseline ---` and its output (D7).

**Revert patch** `<workspace>/task-<N>-revert.patch`: written by each run that builds a revert, overwritten by the next, and kept after the run (D3). Its name never matches the agent-mutant glob `task-<N>-mutant-*.patch`. The marker's first line names it, so a recovery writes `note: reversed task-<N>-revert.patch, left applied by a killed run`.

**Project config files**, matched by base name at any depth: `pyproject.toml`, `uv.lock`, `uv.toml`, `.python-version`, `requirements*.txt`, `setup.cfg`, `pytest.ini`, `tox.ini` (spec, Design 2).

**Mutants file** gains two line forms, each at column 0. Reviewers read them, and `task-done` does not:

```text
Keeps: <test> — <the behavior from before the task that it checks>
Strengthened: <plan test> — by <new test>
```

**`task-done`.** The gate's refusals (exit 4) gain three, in this order, after the `head:` check and before the `result:` check (D11). Each goes through the existing `refuse`:
- `the mutant run has no base: line`
- `the mutant run is at base <the run's base>, not BASE <BASE as a full sha>`
- `the mutant run has no revert: line`

`base:` and `revert:` are read from the header only: after line 1 and before the first `---` line.

**Dispatch placeholder.** The implementer gains `[BASE]`, the task's BASE as a full SHA (D12). It is a value, not a path.

### Micro-tests

- **Method.** writing-skills' micro-test method, main's copy, as plan 93's Global Constraints, Micro-tests, apply it (`specs/plans/completed/93-mutant-checked-tests.md:117-124`): five scored reps per fixture per arm, each in a fresh context, at **standard** (`sonnet`). The record's fixtures, bars, reading rules, VOID rule and spend stop are committed before any rep runs, and no reading is added after reps are seen. Every verdict is read by hand from the rep's full output. Texts under test enter a prompt or a kit copy only through `git show <sha>:<path>`.
- **Isolation.** Plan 93's flags: `env -i` with only `HOME`, `USER`, `LOGNAME`, `PATH`, `SHELL`, `TMPDIR` and `LANG`, plus `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`; `--strict-mcp-config`, `--setting-sources ""`, `--disable-slash-commands` and `--no-session-persistence`; each rep from its own new directory under `/tmp`, outside every repository. No path or name a rep can see names this repository, this plan, the skill under test or a bar. A pilot probe passes before any scored rep.
- **Kits (D1).** Copy plan 93's `impl-kit/` and `review-kit/` into this plan's record folder. Port into each copied `run_reps.sh` the three fixes of `specs/baseline/red-baseline-report-source-match/kit/run_reps.sh:18-50`. They are the range check before the overwrite guard, each rep's exit status reaching the script's status, and a failed first rep stopping the batch.
- **Record.** `specs/baseline/red-baseline-change-reverted-mutant.md`, with kits and rep outputs under `specs/baseline/red-baseline-change-reverted-mutant/`. Raw `stream-json` transcripts stay under `~/.cache/agent-skills/scratch/plan97/` and are never committed.
- **Spend.** Plan 93's reps cost about $0.04 for a control rep and $0.10 for a treatment rep (`specs/baseline/red-baseline-mutant-checked-tests.md:490`, `:690`), so this plan's 60 reps and two revision rounds project to well under $10. The micro-test total is the sum of `total_cost_usd` over every rep and probe. Before each batch: running total + (reps in the batch × cap) ≤ $60, with caps of $1.50 for an implementer rep and $0.50 for a reviewer rep. A batch that fails the check is the spend fence: stop and ask the owner. Every dispatch that runs reps carries the running total.

### Commits and lints

- The commit lints pass on every commit. Never use `--no-verify`. Use `/usr/bin/grep` or `git grep` for sweeps, since `grep` here is a shell function.
- Every mention of `scripts/mutant-run` in a Markdown file under `skills/` keeps its `<this-skill-dir>/` anchor, or `<this-skill-dir>/../subagent-driven-development/` from executing-plans.
- After any change under `agents/`, run `uv run --with pyyaml python build/sync_runtime_assets.py`, then the same command with `--check`. Never hand-edit `runtimes/`.

## Review Focus

1. A task that renames a code file. With `--no-renames`, the revert restores the old path and removes the new one, and tracked files equal HEAD after the run. Pinned by Task 2's `test_mutant_run_reverts_a_renamed_file`.
2. A changed code path with a space in its name. The revert must apply, its `path:` line must show the name as it is, and the tree must come back. Pinned by Task 2's `test_mutant_run_reverts_a_path_with_a_space`.
3. A project config file below the top level, such as a workspace member's `pkg/pyproject.toml`. It stays at HEAD like a top-level one. Pinned by Task 2's `test_mutant_run_keeps_test_and_config_files_at_head`.
4. A BASE given as a short SHA. The run records the full SHA, and `task-done` matches it to a BASE argument given either way. Pinned by Task 1's `test_mutant_run_records_base_as_a_full_sha` and Task 3's `test_task_done_matches_a_short_base`.
5. A parametrized test whose ID holds an XML-escaped character. The revert section lists it with the same unescaped ID that `mutant` lines use, so a reviewer can match it to the diff. Pinned by Task 2's `test_mutant_run_lists_revert_ids_unescaped`.

## Decisions

From the brief: the planning session's hard limits are Global Constraints (only `specs/` changed while planning, no execution before plan 96's ends, nothing private in this public record). The owner's decisions D1 to D4 and the designer's calls are in the spec. The lines below are planner defaults. Each settles an item that the spec's "Left to the builder" leaves open and that crosses a task boundary. The owner approved the plan, these defaults included, at plan review. The question was "Do you approve plan 97 (specs/plans/97-change-reverted-mutant.md, 12 tasks), with its 13 planner defaults D1–D13?", and the owner answered "Approve the plan".

- **D1** (planner default; owner approved it as written at plan review, 2026-11-13): the micro-test kits are copies of plan 93's `impl-kit/` and `review-kit/`, with `report-source-match`'s three `run_reps.sh` fixes ported in. Each copied `isolation_probe.txt` gains one line asking whether the agent knows the user's name or email (the gap in backlog item `:6561`). Plan 93's record and kits stay as they are. Applied in: Global Constraints, Tasks 4, 8.
- **D2** (planner default; owner approved it as written at plan review, 2026-11-13): every existing `mutant-run` test passes HEAD as BASE, so its revert reads `none` and its verdicts are unchanged. Assertions that index header lines shift by one after `head:`. Applied in: Tasks 1, 2.
- **D3** (planner default; owner approved it as written at plan review, 2026-11-13): the revert patch is `<workspace>/task-<N>-revert.patch`, overwritten by each run and kept after it, so a reader can open the patch whose sha256 the run records. Applied in: Global Constraints, Task 2.
- **D4** (planner default; owner approved it as written at plan review, 2026-11-13): the BASE checks run after recovery and before the dirty-tree refusal. Recovery never needs BASE, so a bad BASE never leaves a killed run's patch applied. The revert's path list is computed before the baseline, so its `.py` files join the bytecode purge from the first run. The patch is applied after the last agent mutant. Applied in: Tasks 1, 2.
- **D5** (planner default; owner approved it as written at plan review, 2026-11-13): the revert section's layout, one `path:` line per path and the cause-line rule, as File formats pins it. One path per line keeps a path with a space readable. Applied in: Task 2.
- **D6** (planner default; owner approved it as written at plan review, 2026-11-13): stdout gains the `revert:` line before `run:`, so the implementer sees the revert's counts without opening the file. Applied in: Task 2.
- **D7** (planner default; owner approved it as written at plan review, 2026-11-13): a failing baseline's run file has no `revert:` line. `task-done` never accepts such a run, because its `result:` check refuses it anyway. Applied in: Tasks 1, 2.
- **D8** (planner default; owner approved it as written at plan review, 2026-11-13): the control arms. The implementer control gets `implementer-prompt.md` and `references/mutants.md` at the execution base, with one substitution in `mutants.md` step 5 (`mutant-run PLAN_FILE N --` becomes `mutant-run PLAN_FILE N BASE --`) and one dispatch line, `The task's BASE commit: <sha>`. The reviewer control gets `agents/task-reviewer.md` and the Short Form at the execution base. Both arms run Task 2's `mutant-run`. The reviewer micro-test runs the Short Form only, as the spec's 60 reps allow. Task 9 keeps check 7 word for word the same in the Full Form. Applied in: Tasks 4, 6, 8, 10.
- **D9** (planner default; owner approved it as written at plan review, 2026-11-13): a control that meets the bar on F6, F7 or R4 is recorded. The owner rules on it at the completion gate, before the text ships, as plan 93's D14 did. It is not a stop during execution. F8, R5 and R6 bind the treatment arm only (spec, Verification item 3). Applied in: Tasks 4, 6, 8, 10, 12.
- **D10** (planner default; owner approved it as written at plan review, 2026-11-13): the exact `revert: none` text, as File formats pins it. Applied in: Tasks 2, 3.
- **D11** (planner default; owner approved it as written at plan review, 2026-11-13): `task-done`'s three new refusals and their order, as File formats pins them. Applied in: Task 3.
- **D12** (planner default; owner approved it as written at plan review, 2026-11-13): `[BASE]` takes the full SHA that the controller recorded before the task's first dispatch, the same value as the reviewer's `[BASE_SHA]`. Applied in: Tasks 5, 7.
- **D13** (planner default; owner approved it as written at plan review, 2026-11-13): R5 uses R4's task. In R4 the brief's regression test passes on the revert, with no line. In R5 that test fails on the revert, and a second test, which checks the normal case that the task keeps, passes on it with a `Keeps:` line that holds. This is how the spec's "the same test with a `Keeps:` line that holds" reads, because a `Keeps:` line can never hold for a test of changed behavior. Applied in: Task 8.
- **D14** (owner, handoff H1, 2026-11-13): execute plan 97 after plan 96's execution ended (retired in 02b5002, merged as #202 at 7b2976b); <execution base> is 7b2976b. Applied in: Global Constraints, Base and execution; Tasks 4, 8, 12.

## Backlog items this plan touches

- **`specs/deferred_items.md:6255`, the change-reverted mutant.** This plan implements it. This plan's commit writes `→ planned 2026-11-13: specs/plans/97-change-reverted-mutant.md` on it. Protocol step 3 ticks it when the plan lands.
- **`:5719`, the Full Form was never micro-tested.** It fires, because Task 9 changes the Full Form. This plan runs the Short Form only (D8), so the item stays open, and Task 12's summary says so.
- **`:6654`, `task-done` never checks a patch's bytes.** Not settled. Task 3 changes the same gate and the same `write_run` fixture, but not the patch check. The item stays open.
- **`:6561`, the isolation probe never asks about identity.** Applied to this plan's kit copies (D1). The item names plan 92's kit, so it stays open.

## File map

| File | Change | Task |
|---|---|---|
| `skills/subagent-driven-development/scripts/mutant-run` | BASE argument; the revert | 1, 2 |
| `skills/subagent-driven-development/scripts/test_sdd_scripts.py` | new and updated tests | 1, 2 |
| `skills/executing-plans/scripts/task-done`, `test_executing_plans_scripts.py` | base and revert checks | 3 |
| `specs/baseline/red-baseline-change-reverted-mutant.md` | the record: rules, then results | 4, 6, 8, 10, 12 |
| `specs/baseline/red-baseline-change-reverted-mutant/impl-kit/`, `implementer/` | kit copy, fixtures F6–F8, rep outputs | 4, 6 |
| `skills/subagent-driven-development/references/mutants.md`, `implementer-prompt.md` | the revert step, `[BASE]` | 5 |
| `skills/subagent-driven-development/references/test-run.md`, `file-handoffs.md` | controller steps | 7 |
| `specs/baseline/red-baseline-change-reverted-mutant/review-kit/`, `reviewer/` | kit copy, packages R4–R6, rep outputs | 8, 10 |
| `agents/task-reviewer.md`, `skills/subagent-driven-development/task-reviewer-prompt.md`, `re-review-prompt.md`, `runtimes/` | check 7 | 9 |
| `skills/executing-plans/SKILL.md`, `references/final-review.md` | BASE in the call; the Revert item | 11 |
| `NOTICE` | one entry under the superpowers changes | 11 |

---

### Task 1: `mutant-run` takes BASE

**Files:**
- Modify: `skills/subagent-driven-development/scripts/mutant-run:104-122` (usage and argument check), after `:265` (the BASE checks), `:489-496` (`write_header`), and the header comment's usage, run-file and exit lines
- Test: `skills/subagent-driven-development/scripts/test_sdd_scripts.py`

**Interfaces:**
- Consumes: `sdd-repo --with-commit` and `sdd-workspace`, unchanged.
- Produces: the new signature, the two BASE refusals and the `base:` header line, as File formats pins them. Task 2 adds the revert to this signature.

- [x] **Step 1: Update the existing tests (D2)**

Add `head_sha(repo) -> str`, which returns `git rev-parse HEAD`. Every existing `run(MUTANT_RUN, <plan>, <task>, '--', ...)` call gains `head_sha(<repo>)` as BASE, taken after the call's mutants are made. In `test_mutant_run_catches_a_mutant_and_names_its_failing_tests`, the header assertion becomes lines 0, 2, 3, 4 and 5: `'mutant-run: Task 1, run 1'`, `f'head: {sha}'`, `f'base: {sha}'`, `'tree: clean'`, `'result: caught 2, survived 0, invalid 0'`. In `test_mutant_run_stops_on_a_failing_baseline_before_any_patch`, `lines[4]` and `lines[5]` become `lines[5]` and `lines[6]`, and it also asserts `lines[3] == f'base: {sha}'` (D7). `test_mutant_run_rejects_bad_arguments` expects the new usage line, and its cases include `('plan.md', 1, '--', 'true')`, which now lacks BASE.

> Deviation: Task 1 also passes `base` at the one `mutant-run` call in `test_executing_plans_scripts.py` that has no BASE (plan gap; Task 3 would have done it).

- [x] **Step 2: Write the failing tests**

| Test | Arrange | Assert |
|---|---|---|
| `test_mutant_run_requires_a_base` | mutant 1 = A; argv `('plan.md', 1, '--', *PYTEST)` | `rc == 2`; the new usage line in stderr; no run file |
| `test_mutant_run_refuses_a_base_that_is_not_a_commit` | mutant 1 = A; BASE `'nosuch'` | `rc == 2`; `'mutant-run: bad BASE: nosuch'` in stderr; no run file |
| `test_mutant_run_refuses_a_base_that_is_not_an_ancestor_of_head` | commit a file on a side branch, note its sha, switch back; mutant 1 = A; that sha as BASE | `rc == 2`; `'HEAD is not a descendant of BASE'` in stderr; no run file |
| `test_mutant_run_records_base_as_a_full_sha` | mutant 1 = A; BASE = the first 7 characters of HEAD's sha | `rc == 0`; `lines[3] == f'base: {full sha}'` |
| `test_mutant_run_recovers_before_it_checks_base` | as `test_mutant_run_recovers_a_patch_a_killed_run_left_applied` up to the kill; then call again with BASE `'nosuch'` | `rc == 2`; `'bad BASE'` in stderr; `calc.py` reads `CALC`; no `mutant-active` |

- [x] **Step 3: Run the tests to verify they fail**

Run: `uv run python build/run_suites.py subagent-driven-development -- -k "mutant"`
Expected: the five new tests fail, and so do the updated tests, because the script reads BASE as `--`. Read each failure: a usage refusal or a missing `base:` line is the right red.

- [x] **Step 4: Implement BASE in `mutant-run`**

The argument check becomes `$# -ge 5` with `$4` equal to `--`. Resolve BASE to a full SHA with `git -C "$top" rev-parse --verify --quiet "$base^{commit}"`, and check ancestry with `git -C "$top" merge-base --is-ancestor`, both after the recovery block (D4). `write_header` prints `base: <full sha>` after `head:`. Update the header comment's usage line, run-file layout and exit-2 list.

- [x] **Step 5: Run the suite, under both shells**

Run: `uv run python build/run_suites.py subagent-driven-development`
Expected: all pass.
Run: `PATH="/bin:$PATH" uv run python build/run_suites.py subagent-driven-development`
Expected: the same result.

- [x] **Step 6: Commit**

```bash
git add skills/subagent-driven-development/scripts/mutant-run skills/subagent-driven-development/scripts/test_sdd_scripts.py
git commit -m "feat(sdd): mutant-run takes the task's BASE"
```

---

### Task 2: `mutant-run` runs the revert

**Files:**
- Modify: `skills/subagent-driven-development/scripts/mutant-run` (the path list before the baseline at `:464`, the revert after the agent-mutant loop at `:598`, the run file at `:600-625`, and the header comment)
- Test: `skills/subagent-driven-development/scripts/test_sdd_scripts.py`

**Interfaces:**
- Consumes: Task 1's BASE, and the existing `is_test_path`, `run_command`, `write_marker`, `restore_marked`, `check_tree` and `purge_bytecode`.
- Produces: the `revert:` line, the `--- revert ---` and `--- output: revert ---` sections and the revert patch file, as File formats pins them. Tasks 3, 5, 7, 9 and 11 read them.

- [x] **Step 1: Write the fixture and the failing tests**

Add `PYTEST_ALL = [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider']`, which runs every test file. Add a fixture `changed(calc)` that returns `(repo, base)`:
- BASE commit: `half.py` holds `def half(a):\n    return a / 2\n`. `test_half.py` holds `test_half_even` (`half(4) == 2`). `test_param.py` holds `test_p`, parametrized with the one ID `a&b`, asserting `True`.
- Task commit (HEAD): `half.py` returns `a // 2`. `test_half.py` adds `test_half_floors` (`half(3) == 1`), and `test_half_zero` (`half(0) == 0`), a test that the task adds and that passes on the old code. `newmod.py` holds `def g():\n    return 1\n`. `test_newmod.py` has `from newmod import g` at its top and `test_g` (`g() == 1`). `test_skip.py` holds `test_g_skip`, which calls `pytest.importorskip('newmod')` in its body.
- The fixture makes no mutant. Each test makes its mutants after its last commit, on a file that exists at HEAD. For a test built on `changed`, mutant 1 edits `half.py`: `return a // 2` becomes `return a // 3`.

On that fixture, the revert's outcomes are: `test_half::test_half_floors` failed, `test_newmod` not loaded, `test_skip::test_g_skip` skipped, and six passed: the three `test_calc` tests, `test_half::test_half_even`, `test_half::test_half_zero` and the `test_param` case. Each other test builds its own task commit on `calc`, with mutant A, unless its row says otherwise. A row's "BASE adds" commit comes before its task commit. Every test passes as BASE the commit before its first task commit (for a test built on `changed`, the fixture's `base`), and makes its mutants after its last commit.

| Test | Arrange | Assert |
|---|---|---|
| `test_mutant_run_lists_each_test_on_the_revert` | `changed`; `PYTEST_ALL` | `rc == 0`; `'result: caught 1, survived 0, invalid 0'` in lines; `'revert: ran, exit 1, failed 1, not loaded 1, skipped 1, passed 6'` in lines, after the `result:` line; the `--- revert ---` section holds `'path: half.py'`, `'path: newmod.py'` and `f'sha256: {patch_sha(revert patch)}'`, a line that starts `'failed test_half::test_half_floors: AssertionError'`, a line that starts `'not loaded test_newmod: '` and names `newmod`, a line that starts `'skipped test_skip::test_g_skip: '`, `'passed test_half::test_half_even'` and `'passed test_half::test_half_zero'`; the `--- tests ---` section is exactly `['test test_half::test_half_even: caught 1']`; `'--- output: revert ---'` in lines; the stdout line before `run:` is the `revert:` line; `git diff --quiet HEAD` exits 0; `newmod.py` exists; no `mutant-active` |
| `test_mutant_run_keeps_test_and_config_files_at_head` | task commit adds a function `double` to `calc.py` and changes `pyproject.toml`, `pkg/pyproject.toml`, `uv.lock`, `.python-version`, `requirements-dev.txt`, `pytest.ini` and `tests/helper.py`, each added at BASE first | the `path:` lines are exactly `['path: calc.py']` |
| `test_mutant_run_writes_revert_none_when_only_tests_and_config_changed` | task commit changes only `test_calc.py` (one more test) and `pyproject.toml` | `f'revert: none: no file outside the tests and the project config changed'` in lines; no `'--- revert ---'`; no `'--- output: revert ---'`; no revert patch file |
| `test_mutant_run_round_trips_a_deleted_file_and_a_new_script` | BASE adds `old.py`; task commit deletes it and adds `tool.sh` with mode 755 | `'path: old.py'` and `'path: tool.sh'` in lines; after the run, `old.py` does not exist, `tool.sh` is executable, and `git diff --quiet HEAD` exits 0 |
| `test_mutant_run_reverts_a_renamed_file` | `changed`; a further commit `git mv half.py halve.py` with `test_half.py` importing from `halve`; mutant 1 edits `halve.py` (`a // 2` to `a // 3`) | `'path: half.py'` and `'path: halve.py'` in lines; after the run, `half.py` does not exist and `git diff --quiet HEAD` exits 0 |
| `test_mutant_run_reverts_a_path_with_a_space` | BASE adds `my mod.py`; task commit changes it | `'path: my mod.py'` in lines; `git diff --quiet HEAD` exits 0 |
| `test_mutant_run_lists_revert_ids_unescaped` | `changed`; `PYTEST_ALL` | `'passed test_param::test_p[a&b]'` in lines |
| `test_mutant_run_records_a_revert_with_no_report` | `changed`, plus a task-commit `conftest.py` with `import newmod` | `rc == 0`; `'revert: ran, exit 4, no report'` in lines; the revert's output names `newmod` |
| `test_mutant_run_records_a_revert_that_times_out` | `changed`; command `['sh', '-c', 'grep -q "a / 2" half.py && sleep 30; "$0" -m pytest -q -p no:cacheprovider', sys.executable]`; `MUTANT_RUN_TIMEOUT=2`; time the call | `'revert: timeout after 2s'` in lines; elapsed < 15 s; `half.py` reads HEAD's text |
| `test_mutant_run_recovers_a_revert_a_killed_run_left_applied` | `changed`; the timeout test's command; `Popen` with `start_new_session=True`; poll for `mutant-active` whose first line is `task-1-revert.patch`; `SIGKILL` the group; call again with `['true']` | `'note: reversed task-1-revert.patch, left applied by a killed run'` in the new run file; `half.py` reads HEAD's text; no `mutant-active` |

`test_mutant_run_catches_a_mutant_and_names_its_failing_tests` also asserts `lines[6] == 'revert: none: no file outside the tests and the project config changed'`, because its BASE is HEAD. `test_mutant_run_marks_a_collection_error_invalid` stays as it is: it proves that agent-mutant runs do not get `--continue-on-collection-errors`, which would turn its `exit status 2` into `no failed test in the JUnit report`.

- [x] **Step 2: Run the tests to verify they fail**

Run: `uv run python build/run_suites.py subagent-driven-development -- -k "mutant"`
Expected: the new tests fail on a missing `revert:` line or section. Read each failure.

- [x] **Step 3: Implement the revert**

Follow the spec's Designs 2 to 4 with these decisions:
- Before the baseline (D4), list the changed paths with `git -C "$top" diff --no-renames --name-only -z "$base_sha" HEAD`. Drop each path for which `is_test_path` holds or whose base name is a project config file. Add the `.py` paths left to `py_files`.
- After the agent-mutant loop, when the list is empty, record the `none` line. Otherwise write `git -C "$top" diff --no-renames --binary HEAD "$base_sha" -- <each path as :(literal)<path>>` to the revert patch file, then reuse the agent mutants' sequence: `git apply --check`, the marker, apply, `run_command` with the agent mutants' limit, `restore_marked`, `check_tree`. A refused `--check` writes `revert: not applied: does not apply`.
- For the revert run only, `run_command` appends `--continue-on-collection-errors` to the `PYTEST_ADDOPTS` value it builds.
- The "already in HEAD" check stays as it is. The revert patch never matches its glob, so the check never sees it.
- A second `awk` reader, beside `failed_tests`, prints one outcome line per `<testcase>` in report order, with File formats' prefixes. It treats a collection failure as `not loaded` and a `<skipped>` as `skipped`.
- The run file writes `revert:` after `result:` and any `note:`, `--- revert ---` after `--- tests ---`, and `--- output: revert ---` last. Update the header comment's steps, run-file layout and stdout line.

> Deviation: The revert's `git diff` also takes `--no-color --no-ext-diff --no-textconv` and fixed prefixes. A file-level skip prints as `skipped <module>: collection skipped`. A pytest internal error gets no outcome line. The `diff.context 0` break was fixed at the final review (`-U3`).

- [x] **Step 4: Run the suite, under both shells**

Run: `uv run python build/run_suites.py subagent-driven-development`
Expected: all pass.
Run: `PATH="/bin:$PATH" uv run python build/run_suites.py subagent-driven-development`
Expected: the same result.

- [x] **Step 5: Commit**

```bash
git add skills/subagent-driven-development/scripts/mutant-run skills/subagent-driven-development/scripts/test_sdd_scripts.py
git commit -m "feat(sdd): mutant-run lists each test's result on the task's code reverted to BASE"
```

---

### Task 3: `task-done` checks the revert ran at BASE

**Files:**
- Modify: `skills/executing-plans/scripts/task-done:19-36` (header) and `:186-202` (the gate, after the `head:` check)
- Test: `skills/executing-plans/scripts/test_executing_plans_scripts.py`

**Interfaces:**
- Consumes: Task 2's header lines.
- Produces: the three refusals, as File formats pins them.

- [x] **Step 1: Update the fixture**

`write_run(repo, name, run_head, result, numbers)` becomes `write_run(repo, name, run_head, run_base, result, numbers, revert=NONE_REVERT)`, with `NONE_REVERT = 'revert: none: no file outside the tests and the project config changed'`. It writes `base: <run_base>` after `head:` and the `revert` line after `result:`. `run_base=None` or `revert=None` leaves that line out. Each existing call passes the BASE that its `task-done` call gets.

- [x] **Step 2: Write the failing tests**

Each test sets `base = head(repo)`, runs `commit_work(repo)`, writes a mutants file with mutant 1, and calls `task-done` with `base`, unless its row says otherwise.

| Test | Run file | Assert |
|---|---|---|
| `test_task_done_blocks_a_run_with_no_base_line` | `run_base=None` | `rc == 4`; `'the mutant run has no base: line'` in stderr; not recorded |
| `test_task_done_blocks_a_run_at_another_base` | `run_base=head(repo)` | `rc == 4`; `f'the mutant run is at base {head(repo)}, not BASE {base}'` in stderr; not recorded |
| `test_task_done_blocks_a_run_with_no_revert_line` | `revert=None` | `rc == 4`; `'the mutant run has no revert: line'` in stderr; not recorded |
| `test_task_done_records_a_run_whose_revert_ran` | `revert='revert: ran, exit 1, failed 1, not loaded 0, skipped 0, passed 3'` | `rc == 0`; recorded |
| `test_task_done_matches_a_short_base` | as written; `task-done` gets `base[:7]` | `rc == 0`; recorded |
| `test_task_done_reads_base_and_revert_from_the_header_only` | `run_base=None`, `revert=None`, and the baseline output holds the lines `f'base: {base}'` and `NONE_REVERT` | `rc == 4`; `'no base: line'` in stderr |

- [x] **Step 3: Run the tests to verify they fail**

Run: `uv run python build/run_suites.py executing-plans -- -k "task_done"`
Expected: the four blocking tests fail with `rc == 0`. The two passing tests may already pass. Read each failure.

- [x] **Step 4: Implement the checks**

Read `base:` and `revert:` with the header-scoped `awk` pattern that the `result:` reader uses (`task-done:194-198`). Resolve the BASE argument with `git rev-parse --verify "$base^{commit}"` before comparing. Refuse in File formats' order. Update the header comment's refusal list.

- [x] **Step 5: Run the suite, under both shells**

Run: `uv run python build/run_suites.py executing-plans`
Expected: all pass.
Run: `PATH="/bin:$PATH" uv run python build/run_suites.py executing-plans`
Expected: the same result.

- [x] **Step 6: Commit**

```bash
git add skills/executing-plans/scripts/task-done skills/executing-plans/scripts/test_executing_plans_scripts.py
git commit -m "feat(executing-plans): task-done checks that the revert ran at BASE"
```

---

### Task 4: Implementer micro-test — kit, fixtures, rules and the control arm

**Files:**
- Create: `specs/baseline/red-baseline-change-reverted-mutant.md` (the record)
- Create: `specs/baseline/red-baseline-change-reverted-mutant/impl-kit/` (copied, with `fixtures/F6`–`F8/`)
- Create: `specs/baseline/red-baseline-change-reverted-mutant/implementer/control/` (rep outputs)

**Interfaces:**
- Consumes: `implementer-prompt.md` and `references/mutants.md` at the execution base (the control text, D8); Task 2's scripts at its commit (both arms).
- Produces: `build_prompts.py <arm> <text-sha> <script-sha> <out-dir> [<fixture> ...]`, `run_reps.sh`, `probe.sh` and `grade.py`, with plan 93's arguments otherwise; the record, committed with every rule before any rep.

- [x] **Step 1: Copy the kit (D1)**

Copy `specs/baseline/red-baseline-mutant-checked-tests/impl-kit/` without its fixtures. Port the three `run_reps.sh` fixes. Add the identity line to `isolation_probe.txt`. `build_prompts.py` takes the texts at `<text-sha>` and the skill-copy scripts at `<script-sha>`. Both arms fill `[MUTANTS_GUIDE]`, `[MUTANT_RUN]`, `[PLAN_FILE]`, `[WORKSPACE]` and `[SPEC_EXCERPTS_FILE]`. The control applies D8's substitution and dispatch line. The treatment fills `[BASE]`. BASE is the token `@BASE@`, which `run_reps.sh` replaces with the rep repository's first commit. `grade.py` prints reading aids: the final run file's `revert:` line and revert section, the mutants file's `Keeps:` and `Strengthened:` lines, and each plan-test function that differs from `brief.md`.

- [x] **Step 2: Write the three fixtures**

Each `fixtures/F<n>/` holds plan 93's fixture parts (`repo/`, `brief.md`, `spec.md`). The rep's first commit is `repo/`, so `repo/` holds the pre-change code. The domains stay apart from each other, from plan 93's fixtures, from the examples in `references/mutants.md`, and from this repository.

| Fixture | Pre-change code in `repo/` | Excerpt sentences | Plan tests in `brief.md` |
|---|---|---|---|
| F6 | `stock.py`: `reorder_needed(level: int, threshold: int) -> bool` returns `level < threshold` | "`reorder_needed` returns True when the level is at or below the threshold." | `test_reorder_at_threshold`, which asserts `reorder_needed(2, 5) is True`. The brief's text says that this test is the regression test for the boundary bug, the case where the level equals the threshold. It passes on the pre-change code. |
| F7 | `slug.py`: `slugify(title: str) -> str` lowercases and replaces each space with `-` | "A run of whitespace becomes one hyphen." "Letters are lowercased." | `test_slugify_collapses_space_runs` (`'a  b'` gives `'a-b'`), which fails on the pre-change code; `test_slugify_lowercases` (`'Hello'` gives `'hello'`), which checks behavior that the task keeps |
| F8 | none: the task adds `units.py`, `to_bytes(text: str) -> int` | "`to_bytes` reads a number and a unit, `B`, `KB` or `MB`, with 1 KB = 1024 B." | `test_units.py`, which imports `units` at its top |

- [x] **Step 3: Write the record's rules**

Sections, filled before any rep: Base, Kits, Fixtures, Arms (D8), Bars, Reading rules, VOID rule, Spend stop, Leak check, Isolation probe. The bars are the spec's (Verification item 3):

| Fixture | Bar for the treatment arm |
|---|---|
| F6 | `test_reorder_at_threshold` is byte-identical to `brief.md`'s; a new test is listed as `failed` in the final run's revert section; the mutants file has `Strengthened: test_reorder_at_threshold — by <that test>`; in at least 4 of 5 reps |
| F7 | the mutants file has a `Keeps: test_slugify_lowercases` line, and both plan tests are byte-identical, in at least 4 of 5 reps |
| F8 | no `Keeps:` or `Strengthened:` line, and every plan test is byte-identical, in at least 4 of 5 reps (treatment only, D9) |
| All | no rep in either arm weakens a test |

Reading rules: plan 93's weakening rule (`specs/plans/completed/93-mutant-checked-tests.md:382-383`). In F6, a `Keeps:` line on `test_reorder_at_threshold` fails the bar, because the brief names that test as the regression test for the changed behavior. A rep with no final run file fails its fixture's bar. VOID rule and budget rule: plan 93's (`:388-394`), with `/tmp/mt-skill/` and `/tmp/mt-venv/` as the allowed roots.

- [x] **Step 4: Check for leaks and pilot**

Grep each fixture and the control prompts for the answer words: F6 `Strengthened`, `at or below` in a plan test's body; F7 `Keeps`; every fixture `revert`. Record each hit and each exemption with its reason. Run `probe.sh`: the init record lists exactly Bash, Read, Edit and Write, and every probe line reads NO. Run one control rep on F8 as a pilot, unscored, and audit its stream for paths outside the allowed roots.

> Deviation: The pilot's identity line read YES, not NO. The kit scrubs identity forms before each commit and a privacy sweep runs first.

- [x] **Step 5: Commit the kit and the rules, before any scored rep**

```bash
git add specs/baseline/red-baseline-change-reverted-mutant.md specs/baseline/red-baseline-change-reverted-mutant/impl-kit/
git commit -m "test(specs): register the implementer micro-test for the change-reverted mutant"
```

- [x] **Step 6: Run the control arm**

`build_prompts.py control <execution base> <Task 2 commit> <tmp-dir>`, then five reps per fixture into `implementer/control/F<n>/`, one fixture per batch, with the spend check before each.
Expected: 15 scored reps.

- [x] **Step 7: Grade, record and commit**

Read every rep by hand with `grade.py`'s aids. Under `## Implementer control`, write each fixture's pass count, every weakening with its quoted lines, the spend so far, and any control that meets the F6 or F7 bar (D9).

```bash
git add specs/baseline/red-baseline-change-reverted-mutant.md specs/baseline/red-baseline-change-reverted-mutant/implementer/
git commit -m "test(specs): record the implementer micro-test's control arm"
```

---

### Task 5: The implementer text — `references/mutants.md` and the implementer prompt

**Files:**
- Modify: `skills/subagent-driven-development/references/mutants.md` (Terms `:7-17`, step 5 `:34`, a new step after step 6, the mutants file form `:38-63`, Reading the run `:65-89`)
- Modify: `skills/subagent-driven-development/implementer-prompt.md:185-194` (placeholders) and the mutant-step lines of its dispatch body

**Interfaces:**
- Consumes: Task 2's run file; Task 1's signature.
- Produces: `mutants.md`'s new step, which Tasks 7, 9 and 11 cite by its name ("The revert"), and `[BASE]`.

- [x] **Step 1: Write the text**

Follow the spec's Design 5, item by item:
- the Terms: Revert, Fails on the revert, Did not run on the revert, `Keeps:` and `Strengthened:`;
- step 5's call with BASE, and the rule that its command starts pytest once, with no `-x` and no `--maxfail`;
- a new step 7, "The revert", with the three paths and the check before a `Keeps:` line, so the report step becomes step 8;
- the two new line forms in the mutants file form;
- the revert section and its `revert:` forms in "Reading the run".

In the implementer prompt, add `[BASE]` beside `[MUTANT_RUN]` (D12), and name it in the dispatch body's mutant-step call. Keep plan 93's micro-tested sentences word for word, except step 5's command and the step numbers after step 6.

> Deviation: Path 1 says "Strengthen it so that it fails on the revert", where spec :304 says "or add a test".

- [x] **Step 2: Check the anchors and the lints**

Run: `uv run python build/check_helper_paths.py && uv run --with pyyaml python build/check_conformance.py && uv run python build/check_links.py`
Expected: all exit 0.

- [x] **Step 3: Commit**

```bash
git add skills/subagent-driven-development/references/mutants.md skills/subagent-driven-development/implementer-prompt.md
git commit -m "feat(sdd): implementers read the revert and answer each test that passed on it"
```

---

### Task 6: Implementer micro-test — the treatment arm

**Files:**
- Create: `specs/baseline/red-baseline-change-reverted-mutant/implementer/treatment/` (rep outputs; `treatment-r<k>/` for a revision round)
- Modify: `specs/baseline/red-baseline-change-reverted-mutant.md`

**Interfaces:**
- Consumes: Task 4's kit and rules; Task 5's commit (the treatment text).

- [x] **Step 1: Run the treatment arm**

`build_prompts.py treatment <Task 5 commit> <Task 2 commit> <tmp-dir>`, then five reps per fixture into `implementer/treatment/F<n>/`, with the spend check before each batch.
Expected: 15 scored reps.

> Deviation: F8 stopped at 3 scored reps because the VOID stop fired. The F8 bar was not evaluated, and the owner accepted it as recorded at the completion gate (2026-11-14).

- [x] **Step 2: Grade against the bars**

Read every rep by hand. A missed bar gets a revision of Task 5's wording, committed, and a rerun of the failing fixtures only into `treatment-r<k>/`, at most twice (spec, Verification item 3). A bar still missed after round two is the scope fence: stop and ask the owner.

- [x] **Step 3: Record and commit**

Under `## Implementer treatment`, write each fixture's pass count per round, every weakening, the spend, and each wording change with its commit.

```bash
git add specs/baseline/red-baseline-change-reverted-mutant.md specs/baseline/red-baseline-change-reverted-mutant/implementer/
git commit -m "test(specs): record the implementer micro-test's treatment arm"
```

---

### Task 7: The controller's references

**Files:**
- Modify: `skills/subagent-driven-development/references/test-run.md:15` ("Check the run") and `:17-26` (the mutant run)
- Modify: `skills/subagent-driven-development/references/file-handoffs.md:20-25` (the dispatch list) and `:57-59` (the BASE rule)

**Interfaces:**
- Consumes: Task 1's signature; Task 5's `[BASE]`.

- [x] **Step 1: Write the text**

Spec, Design 8: the call gains BASE, and fix rounds keep the task's BASE. The focused command for `mutant-run` starts pytest once, with no `-x` and no `--maxfail`. When the brief's steps run pytest more than once, the controller writes one pytest call that runs every step's tests, while the test-run call keeps the brief's steps. The two-suite limit, with its reading as "did not run". "Check the run" gains the `base:` line. The dispatch list gains `[BASE]`, and the BASE rule says that the same BASE fills it.

> Deviation: The two-suite limit reads as "did not run" only, because spec :478 is open. The owner accepted it as a known limit at the gate, and executing-plans' `final-review.md` now says to rule on such a test (8257130).

- [x] **Step 2: Lint and commit**

Run: `uv run python build/check_helper_paths.py && uv run --with pyyaml python build/check_conformance.py && uv run python build/check_links.py`
Expected: all exit 0.

```bash
git add skills/subagent-driven-development/references/test-run.md skills/subagent-driven-development/references/file-handoffs.md
git commit -m "feat(sdd): the controller passes BASE to mutant-run and runs pytest once"
```

---

### Task 8: Reviewer micro-test — kit, packages, rules and the control arm

**Files:**
- Create: `specs/baseline/red-baseline-change-reverted-mutant/review-kit/` (copied, with packages R4–R6)
- Create: `specs/baseline/red-baseline-change-reverted-mutant/reviewer/control/` (rep outputs)
- Modify: `specs/baseline/red-baseline-change-reverted-mutant.md`

**Interfaces:**
- Consumes: `agents/task-reviewer.md` and the Short Form at the execution base (the control, D8); Task 2's run-file format for the packages.
- Produces: `build_prompts.py short <sha> <out-dir> [<case> ...]` and the packages under `reviewer/packages/R4`–`R6/`.

- [x] **Step 1: Copy the kit and build the packages (D1)**

Copy `specs/baseline/red-baseline-mutant-checked-tests/review-kit/`. Port the `run_reps.sh` fixes and the identity probe line. Keep only the `short` arm. `build_packages.py` writes each package's seven files, with mutant run files in Task 2's format.

| Package | The task | The revert section | The mutants file |
|---|---|---|---|
| R4 | a bugfix whose brief names `test_window_includes_end_date` as the regression test for "the window includes its end date" | lists that test as `passed`, and a second new test as `failed` | no `Keeps:` or `Strengthened:` line |
| R5 | R4's task (D13) | the regression test `failed`; `test_window_starts_on_start_date`, which checks behavior that the task keeps, `passed` | `Keeps: test_window_starts_on_start_date — the window starts on its start date` |
| R6 | a pure new-code task that adds `units.py` | `not loaded tests.test_units`, and the new in-body import tests `failed` with `ImportError` | no line |

Each package's agent-mutant run is clean, so only the revert can draw a mutant finding. `build_packages.py` keeps plan 93's refusal of a package whose diff name, run heads and tree lines disagree, and extends it: it also refuses a package whose mutant run file's `base:` is not the review diff's BASE. Otherwise the new text would rightly flag a controller gap, and R5 or R6 would draw a finding that the package caused.

- [x] **Step 2: Write the record's reviewer rules**

Under `## Reviewer rules`: the bars (spec, Verification item 3): R4 draws an Important finding that names `test_window_includes_end_date` as passing on the pre-change code; R5 and R6 draw no revert finding (treatment only, D9); each in at least 4 of 5 reps. A "revert finding" is any finding that cites the revert section, a `Keeps:` line or check 7. The VOID rule is plan 93's reviewer rule (`specs/baseline/red-baseline-mutant-checked-tests.md`, `## Reviewer micro-test`). Plan 93 had to change its reviewer packages three times after control sets. A package change here is a controller `Ruling:` in the ledger, recorded in its own `## Package change` section, and the control reruns on the changed package before the treatment runs. Leak check: grep the packages and the control prompts for `check 7`, `Keeps` (except R5's mutants file) and the bar words.

- [x] **Step 3: Pilot, commit the rules, run the control arm**

Run `probe.sh` and one unscored pilot on R6. Commit the kit, packages and rules. Then run five control reps per package into `reviewer/control/R<n>/`.

```bash
git add specs/baseline/red-baseline-change-reverted-mutant.md specs/baseline/red-baseline-change-reverted-mutant/review-kit/ specs/baseline/red-baseline-change-reverted-mutant/reviewer/packages/
git commit -m "test(specs): register the reviewer micro-test for the change-reverted mutant"
```

Expected: 15 scored control reps.

- [x] **Step 4: Grade, record and commit**

Under `## Reviewer control`, write each package's pass count, the spend, and whether the control meets the R4 bar (D9).

```bash
git add specs/baseline/red-baseline-change-reverted-mutant.md specs/baseline/red-baseline-change-reverted-mutant/reviewer/
git commit -m "test(specs): record the reviewer micro-test's control arm"
```

---

### Task 9: The task reviewer's check 7 and the re-review prompt

**Files:**
- Modify: `agents/task-reviewer.md:103-201` (`## Mutants`: the run description, check 7 after check 6 at `:183-191`)
- Modify: `skills/subagent-driven-development/task-reviewer-prompt.md:203-301` (the Full Form's `## Mutants`, the same changes) and `:470-474` (`[MUTANT_RUN_FILE]`'s command gains BASE)
- Modify: `skills/subagent-driven-development/re-review-prompt.md:38-57`
- Regenerate: `runtimes/` (`build/sync_runtime_assets.py`)

**Interfaces:**
- Consumes: Task 2's run file; Task 5's line forms.

- [x] **Step 1: Write check 7**

Follow the spec's Design 7. The run description gains the `base:` line and the revert section. It also says that a `base:` other than `[BASE_SHA]` is a gap for the controller, as a stale `head:` is (spec, Design 1). Check 7 follows check 6. Checks 1 to 6 and the grading paragraph stay word for word, except for two changes that the new check forces:
- "passes all six checks" becomes "passes all seven checks" (`agents/task-reviewer.md:191`);
- the `none: <why>` paragraph's "checks 1 to 5 below do not apply, and check 6 still does" (`:143`) also exempts check 7.

Check 7 is word for word the same in both copies. The re-review prompt gains the same check for each test that the fixes add or change.

> Deviation: Check 7's behavior-change sentence covers the counts form only, a `revert: not applied` line is a gap, and the re-review text carries a verdict for each form.

- [x] **Step 2: Check the copies, regenerate and lint**

Run: `diff <(sed -n '/^7\. \*\*Each test/,/^$/p' agents/task-reviewer.md) <(sed -n '/^    7\. \*\*Each test/,/^$/p' skills/subagent-driven-development/task-reviewer-prompt.md | sed 's/^    //')`
Expected: no output.
Run: `uv run --with pyyaml python build/sync_runtime_assets.py && uv run --with pyyaml python build/sync_runtime_assets.py --check && uv run python build/check_reviewer_block.py && uv run --with pyyaml python build/check_conformance.py`
Expected: all exit 0, and `check_reviewer_block.py` reports the four copies identical.

- [x] **Step 3: Commit**

```bash
git add agents/task-reviewer.md skills/subagent-driven-development/task-reviewer-prompt.md skills/subagent-driven-development/re-review-prompt.md runtimes/
git commit -m "feat(task-reviewer): check that each new test fails on the pre-change code"
```

---

### Task 10: Reviewer micro-test — the treatment arm

**Files:**
- Create: `specs/baseline/red-baseline-change-reverted-mutant/reviewer/treatment/` (and `treatment-r<k>/`)
- Modify: `specs/baseline/red-baseline-change-reverted-mutant.md`

**Interfaces:**
- Consumes: Task 8's kit, packages and rules; Task 9's commit.

- [x] **Step 1: Run, grade, revise at most twice**

`build_prompts.py short <Task 9 commit> <tmp-dir>`, then five reps per package into `reviewer/treatment/R<n>/`, with the spend check. A missed bar gets the revision rule of Task 6, Step 2, applied to Task 9's text in both copies.
Expected: 15 scored reps, plus any revision rounds.

> Deviation: R5 holds at 5 of 5 on the registered reading of two lists under an Important heading after "None."; the owner kept that reading at the gate. R4 stays at 4 of 5.

- [x] **Step 2: Record and commit**

Under `## Reviewer treatment`, write each package's pass count per round, the spend, and each wording change with its commit.

```bash
git add specs/baseline/red-baseline-change-reverted-mutant.md specs/baseline/red-baseline-change-reverted-mutant/reviewer/
git commit -m "test(specs): record the reviewer micro-test's treatment arm"
```

---

### Task 11: executing-plans text and `NOTICE`

**Files:**
- Modify: `skills/executing-plans/SKILL.md:247-252` (the mutant step's call)
- Modify: `skills/executing-plans/references/final-review.md:27-61` (the mutant check list gains Revert) and `:63-64` (the run's `base:`)
- Modify: `NOTICE` (after plan 93's entry, `:1010-1026`)

**Interfaces:**
- Consumes: Task 9's final check 7 wording; Task 5's step name.

- [x] **Step 1: Write the text**

`SKILL.md`: the call gains BASE, the value `task-start` printed. `final-review.md`: a **Revert** item with check 7's content, and a sentence that each run's `base:` is the first SHA of its task's ledger line. `NOTICE`: one entry under the superpowers changes, in the form of plan 93's. It names the revert run, the `Keeps:` and `Strengthened:` lines, check 7 and `task-done`'s new refusals. It cites Eric J. Ma's post "The understanding zeitgeist in AI code review" (2026-07-24, https://ericmjl.github.io/blog/2026/7/24/understanding-zeitgeist-ai-code-review/) as the idea's source, taken by citation only with no text reproduced, in the form of the citation at `NOTICE:289-297`.

> Deviation: The Revert item calls the four run faults "a gap", not "a gap for the controller", because executing-plans has no controller.

- [x] **Step 2: Lint and commit**

Run: `uv run python build/check_helper_paths.py && uv run --with pyyaml python build/check_conformance.py && uv run python build/check_provenance.py`
Expected: all exit 0. The `SKILL.md` body stays under 19,700 characters.

```bash
git add skills/executing-plans/SKILL.md skills/executing-plans/references/final-review.md NOTICE
git commit -m "feat(executing-plans): pass BASE to mutant-run and review the revert"
```

---

### Task 12: Whole-change checks and the record's summary

**Files:**
- Modify: `specs/baseline/red-baseline-change-reverted-mutant.md` (`## Summary`)

- [x] **Step 1: Run every check**

Run: `git diff --quiet <execution base> HEAD -- skills/subagent-driven-development/SKILL.md && echo unchanged`
Expected: `unchanged`.
Run: `build/run_commit_lints.sh`
Expected: exit 0.
Run: `uv run python build/run_suites.py subagent-driven-development executing-plans`
Expected: all pass.
Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py`
Expected: all pass, the dependency-drift test included.

- [x] **Step 2: Write the summary and commit**

Write `## Summary` with these parts:
- each bar with its final pass count, and the total spend;
- each control that met a bar on F6, F7 or R4, for the owner's ruling at the completion gate (D9);
- a note that backlog item `:5719` stays open, because the Full Form's check 7 ran no reps.

```bash
git add specs/baseline/red-baseline-change-reverted-mutant.md
git commit -m "test(specs): summarize the change-reverted mutant micro-tests"
```

> Deviation: The Summary also names each open ruling and each reading that decides a bar.

---

## Execution handoff

No execution starts before plan 96's execution ends. Then execute this plan in a fresh session, from a worktree cut as Global Constraints, Base and execution, say. Use subagent-driven-development (recommended) or executing-plans. The script, text and micro-test tasks are separable, and each gains from a fresh reviewer.
