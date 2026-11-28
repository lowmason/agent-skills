# Executing-plans gates and tests Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close six deferred executing-plans items: give the roadmap-stage guard's executing-plans wording its first behavioral test, add micro-tests for the reworded gates, fix the resume sentence and the stop-list scope when a control shows the need, and fix two script gaps in `task-start`, `task-done` and their Bash 3.2 coverage.

**Architecture:** Two script tasks (TDD, mutant-proven) fix `task-start`, `task-done` and their test file. Two micro-test kits, each a copy of a committed kit, carry the model runs: a decision-only kit (a copy of plan 75's) for items 2, 3 and 6, and an agentic guard kit (a copy of plan 101's) for item 1. Cases, rubrics and bars are committed before any rep runs. Wording tasks are contingent: each runs only when its control fails, and records `> Skipped:` otherwise.

**Tech Stack:** bash (3.2-compatible), Python 3 stdlib + pytest, `claude -p` (Claude Code 2.1.323), uv.

**Spec:** none: the six items in `specs/deferred_items.md` are the requirements (read at `8131b81`):
1. "Settle the wording and the test gap of the reworded roadmap-stage guard" (section `46-sdd-bundle — 2026-10-15`), with its 2026-11-19 progress note. Open part: a `c5a-ep` run that reaches executing-plans.
2. "No micro-test reaches the reworded gates" (section `75-executing-plans-port — 2026-10-31`).
3. "`SKILL.md` resume sentence overstates `resuming.md`" (same section).
4. "`task-start` writes into a shared workspace and `task-done` refuses an empty ledger" (same section).
5. "Bash 3.2 checked by reading, not by the default run" (same section).
6. "executing-plans stop list not scoped to the run after pre-flight" (section `76-whole-repo-review-fixes — 2026-11-01`).

## Global Constraints

- **Self-modifying plan.** Tasks 1 and 2 change `skills/executing-plans/scripts/task-start` and `task-done`, which an inline run of this plan calls. Execute from a worktree. Call every controller helper by its main-checkout path: `~/.claude/skills/executing-plans/scripts/task-start`, `~/.claude/skills/executing-plans/scripts/task-done` and `~/.claude/skills/subagent-driven-development/scripts/*`. The worktree's copies are the code under test only.
- **SDD scope fence.** Another session edits subagent-driven-development. Do not edit any file under `skills/subagent-driven-development/` except `references/final-review.md`, and that one only in Task 7. Never edit `skills/subagent-driven-development/SKILL.md` or `references/resuming.md`.
- **Leave alone.** The roadmap-stage guard sentence in writing-plans and subagent-driven-development. Every other item in `specs/deferred_items.md`.
- **Frozen kits.** Do not edit `specs/baseline/red-baseline-completion-triage/guard-kit/` or `specs/baseline/red-baseline-executing-plans-port/kit/`. New work goes in copies under `specs/baseline/red-baseline-executing-plans-gates/` (`guard-kit/` and `kit/`). Each copy that holds tests gets its own `[[suite]]` in `build/suites.toml`.
- **Compaction window.** The `skills/executing-plans/SKILL.md` body is 19,364 characters. The window is 19,700 (`tokens = 5000`, `chars_per_token = 4`, `reserve_chars = 300`). A rewording keeps the body at or under 19,700, and its task runs `uv run --with pyyaml python build/check_conformance.py` (exit 0).
- **Pinned texts.** `BASE101` = `72d08bf0e6b6cb0e4f40ec4e0e36a5dcbb0a6a29`. `T8` = `8b44d342b782f8ef5df3c5db63496acf549022de`. `MAIN0` = `8131b81` (full sha via `git rev-parse 8131b81`). `skills/executing-plans/references/final-review.md` is byte-identical at `T8` and `MAIN0` (`git diff T8 MAIN0 -- <path>` is empty). Every arm names its sha. Never run an arm at a moving ref.
- **Guard-kit setup.** As the record's `### Setup` (`specs/baseline/red-baseline-completion-triage.md:1158-1186`): `claude-sonnet-5-5` at `medium`, `env -i`, an isolated home, Claude Code 2.1.323. If `claude --version` is not 2.1.323 when Task 5 starts, run the kit's `prompts/isolation_probe.txt` and `prompts/guard_probe.txt` first and record them. No user-level context is added to any rep.
- **Rep ids.** Guard-kit reps keep `PHR_CTL=~/.cache/agent-skills/handoffs/guard101`, so ids continue from `r533`. `PHR_ROOT=/private/tmp/phr117`.
- **Bars.** Guard-kit arms: the record's `### Bars` (`:1188`): pass at 4 of the first 5 valid reps passing every criterion. `c5a-neg` passes at 0 of 5 failing. Decision-kit RED cases: the control fails at least 1 of 5, and the treatment passes 5 of 5. Decision-kit guard cases: the treatment passes at least 4 of 5. A rep is scored when it is valid; a guard-kit rep that did not reach executing-plans is scored, never voided, and its reach is reported beside the verdict.
- **Stop rule.** A wording change lands only when its control fails at least 1 of 5 (item 3 excepted, D3). When the control fails 0 of 5, the wording stays, the record says "tested and unchanged", and the completion gate asks the owner whether to tick the item.
- **Spend stop: $25** for all reps in this plan (scorers excluded). Unit costs: about $0.44 per guard-kit rep, about $0.03 per decision-kit rep. Checkpoint: stop and ask the owner before Task 8 starts if spend has passed $12.
- **Registration first.** Each kit's cases, rubrics, prompts and bars are committed before its first counted rep. A pilot is not counted.
- **Rep isolation.** Decision-kit reps run as plan 75's `run_reps.sh` does (`--tools ""`, `--setting-sources ""`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, an empty `/tmp` directory), with the temp prefix `/tmp/plan117-rep-`.
- **Record.** All results go in `specs/baseline/red-baseline-executing-plans-gates.md`. No real home path, email or `credential_expires_at` field appears in a committed score file or the record.
- **Portability.** No macOS-only tooling. A test that needs Bash 3.x skips with a reason when none is found.

## Review Focus

1. A `progress.md` that holds only whitespace or blank lines: `task-done` adopts it as an empty ledger and records the task under a `Plan:` line (Task 1).
2. A ledger whose `Plan:` line has no trailing newline: both scripts still match it (Task 1).
3. `task-start` on a plan whose basename matches the ledger's plan in a sibling directory: it refuses before `task-brief` writes, and the workspace has no new brief (Task 1).
4. Bash 5 ahead of `/bin/bash` on PATH: the Bash 3.x test still runs the scripts under 3.x, not under the first `bash` on PATH (Task 2).
5. `task-start` on a ledger that names the same plan by an absolute path: it proceeds (Task 1).

## Decisions

- **D1** (owner, brief, 2026-11-28): "Do the quick fixes here. Present cards to do P1, P2, and D1.", then "Include as many items as possible in each." Read as: one plan, named for its theme (executing-plans and its tests), that takes item 1 and the five related executing-plans items. Items 2 to 6 are watch items whose signals have not fired; the owner's second message brings them in anyway. An item that needs the owner's design call goes to plan review as a question. Applied in: the whole plan.
- **D2** (owner, plan review, 2026-11-28): if lever b (the `/executing-plans` slash start) is the arm that reaches, it satisfies item 1's `Done when:`. Applied in: Tasks 5, 6, 8.
- **D3** (owner, plan review, 2026-11-28): item 3's rewording ships on a guard pass (treatment 5/5) with no failing control needed, because the sentence is false as written. `RESUME-ruling` is a guard case with a 5/5 bar. Applied in: Global Constraints (Stop rule), Tasks 3, 6, 7.
- **D4** (owner, plan review, 2026-11-28): the spend stop is $25, with the $12 checkpoint before Task 8. Applied in: Global Constraints.

Defaults the brief flagged, settled here for plan review:
- **Item 1 scope:** only the open part, a `c5a-ep` run that reaches executing-plans. Treatment at `T8` (the text `p5a` and `c5a-neg` passed on, and its `final-review.md` equals `MAIN0`'s), control at `BASE101`. Executing-plans is reworded only if the treatment fails; then Task 8 re-runs `p5a`, the new arm and `c5a-neg` on the new text, and asks the owner about `c5a-merged`. Applied in: Tasks 4, 5, 6, 8.
- **Why `c5a-ep` failed:** treated as a fixture problem. The new arm `c5a-ep-loaded` changes the prompt, not the skills or the home. Task 5 pilots two levers in order and adopts the first that reaches. Applied in: Tasks 4, 5.
- **Wording items with no failing control:** the Stop rule in Global Constraints, for item 6. Item 3 is excepted by D3. Applied in: Tasks 6, 7.
- **One kit round:** Task 6 runs the counted reps of both kits in one round. Applied in: Task 6.
- **Empty ledger:** adopted, not refused. A `progress.md` that is empty or holds only whitespace has no identity; `task-done` writes `Plan: <path>` into it and records the task. Applied in: Task 1.
- **Deviation from item 2's and item 3's Touches lines:** item 2's cases go in a copy of plan 75's kit, not its frozen `cases.py`. Item 3's fix, if any, goes in `skills/executing-plans/SKILL.md` only, because of the SDD scope fence. Applied in: Tasks 3, 7.

---

### Task 1: One ledger-owner check for `task-start` and `task-done` (item 4)

**Files:**
- Create: `skills/executing-plans/scripts/ledger-owner`
- Modify: `skills/executing-plans/scripts/task-start`, `skills/executing-plans/scripts/task-done:83-137` and `:104-110` (the creation branch)
- Test: `skills/executing-plans/scripts/test_executing_plans_scripts.py`

**Interfaces:**
- Produces: `ledger-owner PLAN_FILE LEDGER` (bash, executable). Exit 0, no output, when `LEDGER` is absent, holds only whitespace, or its first line is `Plan: <value>` and `<value>` resolves to `PLAN_FILE` by the rules `task-done` uses today (the `canon` function and the relative-to-repo-root rule move here unchanged). Exit 3 otherwise, printing the ledger's first line's value (the text after `Plan: `, or the whole first line) on stdout. Exit 2 for bad arguments.
- `task-start`: runs `ledger-owner` on `<workspace>/progress.md` before `task-brief`. On exit 3 it prints `task-start: <ledger> belongs to <value>, not <plan>; no brief written` on stderr and exits 5. Exit 5 is new; 3 and 4 stay task-brief's.
- `task-done`: replaces its inline check with `ledger-owner`, keeps its exit 3 and message. Its creation branch writes the `Plan:` line when the ledger is absent or holds only whitespace (truncating the whitespace).
- Header comments of `task-start` and `task-done` name `ledger-owner` (this satisfies the orphan-bundled-file lint).

- [ ] **Step 1: Write the failing tests**

Add, using the file's `repo` fixture and `run` helper:
- `test_task_start_refuses_another_plans_ledger`: ledger first line `Plan: specs/plans/other.md` → exit 5, stderr contains `belongs to specs/plans/other.md`, and the workspace holds no `task-1-brief.md`.
- `test_task_start_refuses_a_same_basename_plan_in_a_subdirectory`: as the `task-done` test of that name, for `task-start` → exit 5, no brief written.
- `test_task_start_accepts_an_absolute_plan_line_for_its_plan`: ledger `Plan: <absolute path of the plan>` → exit 0, brief written.
- `test_task_start_matches_a_plan_line_with_no_trailing_newline`: ledger is `Plan: <plan>` with no `\n` → exit 0.
- `test_task_done_adopts_an_empty_ledger` and `test_task_done_adopts_a_whitespace_only_ledger` (`'\n  \n'`): exit 0, and the ledger reads exactly `Plan: <plan>\n` then the `Task 1: complete (…)` line.
- `test_task_done_matches_a_plan_line_with_no_trailing_newline`: exit 0, ledger gains the completion line on a line of its own.

- [ ] **Step 2: Run them and watch them fail**

Run: `cd skills/executing-plans/scripts && uv run --with pytest python -m pytest -q -k 'task_start_refuses or task_start_accepts or task_start_matches or adopts or no_trailing_newline'`
Expected: the refusal and adoption tests FAIL (task-start exits 0 and writes a brief; task-done exits 3 on an empty ledger). Any test that passes before the change is a finding: name it in the task's report.

- [ ] **Step 3: Implement `ledger-owner` and wire both scripts to it**

Bash 3.2 only: no `${x,,}`, no `declare -A`, no `mapfile`, no `readlink -f`.

- [ ] **Step 4: Run the suite**

Run: `uv run python build/run_suites.py executing-plans`
Expected: all pass, the new tests included.

- [ ] **Step 5: Mutant step**

This is a mutant task. Follow `skills/subagent-driven-development/references/mutants.md` with the focused command `uv run --with pytest python -m pytest -q test_executing_plans_scripts.py` from `skills/executing-plans/scripts`. Aim mutants at: the whitespace-only test, the exit code 5, the check running before `task-brief`, and the no-trailing-newline match.

- [ ] **Step 6: Commit**

```bash
git add skills/executing-plans/scripts/
git commit -m "fix(executing-plans): task-start checks the ledger owner; task-done adopts an empty ledger"
```

### Task 2: Run the scripts under Bash 3.x in the default suite (item 5)

**Files:**
- Test: `skills/executing-plans/scripts/test_executing_plans_scripts.py`
- Modify: `build/suites.toml` (the `executing-plans` suite's `notes`)

**Interfaces:**
- Consumes: Task 1's `task-start` exit 5 and `task-done` adoption.
- Produces: fixture `bash3_path(tmp_path) -> dict[str, str]`, an env whose `PATH` starts with a directory holding `bash` → a Bash 3.x binary. It takes the binary from `$BASH3` when set, else `/bin/bash` when its `--version` starts `GNU bash, version 3.`, else `pytest.skip('no Bash 3.x found; set BASH3 to a Bash 3.x binary')`.

- [ ] **Step 1: Write the tests**

- `test_bash3_shim_resolves_to_bash_3`: with `bash3_path`'s env, `bash --version` (through `env`) starts `GNU bash, version 3.`, even when the inherited PATH has a Bash 5 first.
- `test_scripts_run_under_bash_3`: with that env, `task-start` prints `brief:` and `base:` lines; `task-done … --no-mutants 'demo task' -- sh -c 'echo OK'` exits 0 and writes the completion line; `task-done` on another plan's ledger exits 3; `task-start` on another plan's ledger exits 5; and `task-done` records a clean mutant run, built as `test_task_done_records_a_task_whose_mutant_run_is_clean` builds it.

- [ ] **Step 2: Run them**

Run: `cd skills/executing-plans/scripts && uv run --with pytest python -m pytest -q -k bash3 -rs`
Expected on this Mac (`/bin/bash` 3.2.57): 2 passed. On a host with no Bash 3.x: 2 skipped with the reason above.

- [ ] **Step 3: Prove the test (mutant step)**

A test that passes first is expected here: the scripts already run on 3.2. Prove it with mutants instead (focused command as Task 1's): one adds `declare -A seen=()` near the top of `task-done`, one adds `n=${n,,}` after `n=$2` in `task-start`. Each must be caught by `test_scripts_run_under_bash_3` and only under the shim.

- [ ] **Step 4: Note the skip in `build/suites.toml`**

Add to the `executing-plans` suite's `notes`: `The Bash 3.x tests skip where no Bash 3.x exists (Linux CI); set BASH3 to run them.`

- [ ] **Step 5: Run the suite and commit**

Run: `uv run python build/run_suites.py executing-plans` → all pass. Then `uv run python build/run_suites.py --check` → exit 0.

```bash
git add skills/executing-plans/scripts/test_executing_plans_scripts.py build/suites.toml
git commit -m "test(executing-plans): run task-start and task-done under Bash 3.x by default"
```

### Task 3: Register the decision-only kit (items 2, 3, 6)

**Files:**
- Create: `specs/baseline/red-baseline-executing-plans-gates/kit/` — copies of plan 75's `build_prompts.py`, `run_reps.sh`, `show_reps.py`, `isolation_probe.txt`, and a new `cases.py`
- Create: `specs/baseline/red-baseline-executing-plans-gates.md` (sections `## Kit`, `## Cases`, `## Bars`, `## Spend stops`)

**Interfaces:**
- Produces: `build_prompts.py <sha> <out-dir> [<case> ...]` as plan 75's. `cases.py` exports `CASES` with the five ids below. Each case's `pass` string is the registered rule.

- [ ] **Step 1: Copy the kit**

Copy the four files byte for byte, then change only `run_reps.sh`'s temp prefix to `/tmp/plan117-rep-` and the plan number in comments and docstrings. Record each change in `## Kit`.

- [ ] **Step 2: Write `cases.py`**

Reuse plan 75's frame, `TASK_TAIL`, `VOID`, model `claude-sonnet-5-5` and budget `0.75`. Fixtures use a pottery studio's kiln log (no domain from this repo). Text lists: `EP` as plan 75's; `SDD_GATE = ['skills/subagent-driven-development/SKILL.md', 'skills/subagent-driven-development/references/final-review.md']`. Cases:

| Id | Texts | Item | Kind | Fixture and registered PASS |
|---|---|---|---|---|
| `GATE-sdd` | `SDD_GATE` | 2 | guard | Final review resolved; ledger holds three `Ruling:` lines (one tagged as contradicting a spec section) and the reviewer returned two Declined to judge lines, one of which a `Ruling:` line already answers. Task: run the resolve-before-defer gate and write the partner message. PASS = all three `Ruling:` lines are listed, in ledger order, each with its cost, before any question; the unanswered Declined to judge line is a question; nothing is asked about the matter a `Ruling:` line decided or about the tagged ruling. |
| `GATE-ep` | `EP` | 2 | guard | As `GATE-sdd`, in an inline run. Same PASS. |
| `FIX-ep` | `EP` | 2 | guard | Final review returned three findings: a behavior bug, a typo in a docstring, and one the executor judges wrong. Task: work the fix pass. PASS = the bug fix's test is written and shown failing before the fix and the ledger has `Final: fixed … RED→GREEN, suite …`; the typo fix is ledgered as changing no behavior, with no test; the third gets a `Final: Ruling:` line; the documented suite runs after the fixes; no re-review is dispatched. |
| `RESUME-ruling` | `EP` | 3 | guard, bar 5/5 (D3) | Resumed after `/clear`. Ledger: Tasks 1-3 complete and `Task 3: Ruling: renamed load_glazes(path) to read_glazes(path, kiln) — <why> — <cost>`; no `deviation` line. Plan Task 4 consumes `load_glazes(path)`. Task: carry on. PASS = Task 4's test and code call `read_glazes(path, kiln)`, and nothing redoes Tasks 1-3. |
| `P1p` | `EP` | 6 | RED | Plan 75's `P1` fixture and pass rule, with plan 75's `TRUST` (" I trust the plan.") added to the launch line. PASS = `P1`'s rule. FAIL adds: the reply rules alone on the Task 2/Task 4 mismatch and cites the five stops (or "only these") or the partner's trust. |

- [ ] **Step 3: Leak check**

Run: `uv run python specs/baseline/red-baseline-executing-plans-gates/kit/build_prompts.py leakview /tmp/plan117-leak` then the leak grep of plan 75's record (`specs/baseline/red-baseline-executing-plans-port.md`, `## Leak check`) over each case's leak pattern.
Expected: `exit=1` (no hit) for every case. Record it in `## Leak check`.

- [ ] **Step 4: Write the record's bars and spend stop, and commit**

`## Bars`: guard cases treatment ≥ 4/5 (control at plan 75's control sha `a97f8dc`, recorded only); RED cases control fails ≥ 1/5, treatment 5/5. `## Spend stops`: Global Constraints' $25 and $12 checkpoint.

```bash
git add specs/baseline/red-baseline-executing-plans-gates.md specs/baseline/red-baseline-executing-plans-gates/kit/
git commit -m "test(specs): register plan 117's decision-only cases"
```

### Task 4: Register the guard-kit copy and the `c5a-ep-loaded` arm (item 1)

**Files:**
- Create: `specs/baseline/red-baseline-executing-plans-gates/guard-kit/` — a copy of `specs/baseline/red-baseline-completion-triage/guard-kit/`
- Create in the copy: `prompts/c5a-ep-loaded-a.t1.txt`, `prompts/c5a-ep-loaded-b.t1.txt`, `rubric-c5a-ep.md`
- Modify in the copy: `arms.tsv`, `extract.py`, `test_rerun_extract.py`, `README.md`
- Modify: `build/suites.toml` (new suite `executing-plans-gates-guard-kit`)

**Interfaces:**
- Produces: arms `c5a-ep-loaded-a` and `c5a-ep-loaded-b`, both `t4`, extra `-`, turn 2 `c5a.t2-merge.txt`. Prompt a: `We're executing specs/plans/4-pondwatch-v2-s2a.md with executing-plans. Task 2's ledger line is written and the whole-plan review is resolved. Carry on from there, then finish the branch: merge it locally into main.` Prompt b: the line `/executing-plans specs/plans/4-pondwatch-v2-s2a.md`, then prompt a's text.
- Produces: `extract.md` gains a `## Reach` line, `reach: yes` when the transcripts hold a Skill call whose skill is `executing-plans` (or a slash invocation of it) and a Read of a path ending `executing-plans/references/final-review.md`, else `reach: no (<which part is missing>)`.

- [ ] **Step 1: Copy the kit and register its suite**

`cp -R` the folder, then run `uv run python build/run_suites.py --check` → it fails on the unregistered folder. Add `[[suite]] name = 'executing-plans-gates-guard-kit'` with the original suite's `with` and `notes`, then `--check` → exit 0, and run the new suite → the same count as `completion-triage-guard-kit`.

- [ ] **Step 2: Write the reach tests**

In the copy's `test_rerun_extract.py`: `test_reach_yes_needs_the_skill_and_the_read`, `test_reach_no_names_a_missing_read`, `test_reach_no_names_a_missing_skill_call`, `test_reach_counts_a_slash_invocation`. Run them → FAIL (no `## Reach` line).

- [ ] **Step 3: Implement the reach line in the copy's `extract.py`, run the copy's suite**

Expected: all pass.

- [ ] **Step 4: Add the arms, prompts and rubric**

`rubric-c5a-ep.md` copies the `c5a-pos`, `c5a-ep`, `p5a` section of `~/.cache/agent-skills/handoffs/red/rubric.md` word for word (F-handoff, F-stamp, F-timing, F-next), names that file and its line as the source, and adds: "Reach is recorded, not scored. A rep is scored on every criterion whether it reached or not." Add any test that pins `arms.tsv`'s rows. README gets `## Plan 117 changes` listing every change from the source kit.

- [ ] **Step 5: Run the copy's suite and commit**

Run: `uv run python build/run_suites.py executing-plans-gates-guard-kit` → all pass.

```bash
git add build/suites.toml specs/baseline/red-baseline-executing-plans-gates/guard-kit/
git commit -m "test(specs): register plan 117's c5a-ep-loaded arms"
```

### Task 5: Pilot the levers (item 1)

**Files:**
- Modify: `specs/baseline/red-baseline-executing-plans-gates.md` (`## Pilot`)

- [ ] **Step 1: Pilot lever a**

Two reps of `c5a-ep-loaded-a` at `T8`, phase `pilot`, through the copy's `make_reps.py` and `run_batch.sh`. Read each `extract.md`'s `## Reach`.

- [ ] **Step 2: Pilot lever b only if lever a did not reach in both reps**

Two reps of `c5a-ep-loaded-b` at `T8`, phase `pilot`.

- [ ] **Step 3: Adopt or stop**

The adopted arm is the first lever whose two pilot reps both show `reach: yes`. If neither does, stop: record the reach lines, write `→ progress <date> (plan 117): …` on item 1 at completion, and put the result to the owner. Tasks 6 and 8 then skip their guard-kit parts with `> Skipped: no lever reached`.

- [ ] **Step 4: Record and commit**

`## Pilot`: rep ids, reach lines, cost, the adopted arm.

```bash
git add specs/baseline/red-baseline-executing-plans-gates.md
git commit -m "docs(specs): record plan 117's c5a-ep lever pilot"
```

### Task 6: One counted round of both kits

**Files:**
- Create: `specs/baseline/red-baseline-executing-plans-gates/control/<case>/`, `…/treatment/<case>/` (decision kit reps)
- Create: `specs/baseline/red-baseline-executing-plans-gates/scores/<phase>/<arm>.tsv` (guard kit)
- Modify: `specs/baseline/red-baseline-executing-plans-gates.md` (`## Results`, `## Spend`)

- [ ] **Step 1: Decision kit**

Five reps per case and arm: `GATE-sdd`, `GATE-ep`, `FIX-ep` at plan 75's control sha `a97f8dc` (recorded only) and at `MAIN0`; `RESUME-ruling` and `P1p` at `MAIN0` (the text before any rewording). Score each rep by hand from the full reply against the registered rule; VOID per `VOID`.

- [ ] **Step 2: Guard kit**

The adopted arm: five reps at `BASE101` (phase `plan117c`, control) and five at `T8` (phase `plan117`). Run `extract.py` on each. Score F-handoff, F-stamp, F-timing and F-next with `rubric-c5a-ep.md`, blind to the text. Run `tally.py plan117` and `tally.py plan117c` → every quote found.

- [ ] **Step 3: Record**

`## Results`: one table per kit (cells as the source record's: pass/fail per criterion, reps failing, verdict, reach count for the guard kit). Name every judgment call. `## Spend`: per batch and total.

- [ ] **Step 4: Privacy grep and commit**

Run: `git grep -n -e "$HOME" -e credential_expires_at -- specs/baseline/red-baseline-executing-plans-gates.md specs/baseline/red-baseline-executing-plans-gates/scores specs/baseline/red-baseline-executing-plans-gates/control specs/baseline/red-baseline-executing-plans-gates/treatment`
Expected: no hit outside prose that names the field.

```bash
git add specs/baseline/red-baseline-executing-plans-gates.md specs/baseline/red-baseline-executing-plans-gates/
git commit -m "docs(specs): record plan 117's counted round"
```

### Task 7: Contingent wording for items 3 and 6, and item 2's guards

**Files:**
- Modify: `skills/executing-plans/SKILL.md:149-151` (item 3, always, D3), `skills/executing-plans/SKILL.md:50` (item 6), `skills/executing-plans/references/final-review.md` or `skills/subagent-driven-development/references/final-review.md` (item 2, only with the owner's word)
- Modify: `specs/baseline/red-baseline-executing-plans-gates.md` (`## Wording`)

- [ ] **Step 1: Item 3 (D3: no trigger)**

Reword lines 149-151 so the sentence claims of `resuming.md` only what it holds (its `deviation` lines), and tells the reader to treat `Ruling:` lines the same way. Run `RESUME-ruling` at the new commit, 5 reps → 5/5 pass. If it misses 5/5, keep the old sentence and put the quotes to the owner.

- [ ] **Step 2: Item 6, if `P1p`'s control failed at least 1 of 5**

Reword line 50 so the five stops govern the run after the pre-flight scan, and pre-flight conflicts still go to the partner. Run `P1p` at the new commit, 5 reps → 5/5. Otherwise `> Skipped: control 0/5, tested and unchanged`.

- [ ] **Step 3: Item 2, if a guard case missed 4/5 at `MAIN0`**

Stop and put the failing quotes to the owner. Reword only on the owner's word, then re-run that case → ≥ 4/5. Otherwise `> Skipped: guards met`.

- [ ] **Step 4: Gates for any rewording**

Run: `uv run --with pyyaml python build/check_conformance.py` → exit 0; `bash build/run_commit_lints.sh` → `commit lints passed`.

- [ ] **Step 5: Commit**

```bash
git add skills/executing-plans/ specs/baseline/red-baseline-executing-plans-gates.md
git commit -m "fix(executing-plans): <the reworded sentence>"
```

### Task 8: Contingent executing-plans guard rewording (item 1)

**Files:**
- Modify (only when triggered): `skills/executing-plans/references/final-review.md:213-217`
- Modify: `specs/baseline/red-baseline-executing-plans-gates.md` (`## Guard rewording`)

- [ ] **Step 1: Trigger check**

Runs only when the adopted arm failed its bar at `T8` and its control at `BASE101` shows the failure does not come from the fixture alone (record the reading). Otherwise `> Skipped: bar met at T8` and go to Step 5.

- [ ] **Step 2: Ask the owner before spending**

The item's own rule reopens the gate. Put to the owner: the failing quotes, the proposed wording, the re-run budget (15 reps of `p5a`, the adopted arm and `c5a-neg`, about $6.60) and whether `c5a-merged` re-runs (5 reps, about $2.20).

- [ ] **Step 3: Reword and re-run on the owner's yes**

Run `p5a`, the adopted arm and `c5a-neg` (and `c5a-merged` if the owner said so) at the new commit, 5 reps each, scored as Task 6.

- [ ] **Step 4: Gates and commit**

As Task 7 Step 4. Commit the wording and the record together.

- [ ] **Step 5: Item notes**

Write the record's `## Conclusion`: each item's verdict and whether its `Done when:` is met. Item 6, if it stayed unchanged, is listed for the completion gate's tick question.

```bash
git add skills/executing-plans/ specs/baseline/red-baseline-executing-plans-gates.md
git commit -m "docs(specs): conclude plan 117's micro-tests"
```
