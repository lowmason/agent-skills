# Plan-completion triage and gate reverts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Narrow Plan Completion Protocol step 4 to a backlog report, give a revert asked for at the gate one rule,
and fold in four fixes to the same protocol text: the final review's Declined to judge lines in step 1, a status
line that names both backlog files, the roadmap-stage guard wording with its reruns, and the three next-kit fixes.

**Architecture:** Text edits in `skills/writing-plans/SKILL.md` (the guard paragraph and protocol steps 1, 2 and 4),
its `references/deferred-backlog.md` and `references/history.md`, both executors' `references/final-review.md`, and
the guard sentence in `skills/subagent-driven-development/SKILL.md`. One script change: `deferral_scan.py` exempts
the new status line. A one-time fix rewrites the status line of retired plans. A new decision-only kit, copied from
plan 80's and carrying the next-kit fixes, micro-tests every wording change except the guard. A copy of plan 100's
multi-turn kit tests the guard on plan 40's frozen arms, as plan 46 did in plan 40's harness (D15).

**Tech Stack:** Markdown skill text, Python 3.11+ stdlib (`deferral_scan.py`, kit scripts), pytest through
`build/run_suites.py`, the `claude -p` micro-test kit, and a copy of plan 100's multi-turn kit
(`specs/baseline/red-baseline-handoff-rerun/kit/`) with plan 40's frozen prompts and rubric under
`~/.cache/agent-skills/handoffs/red/`.

**Spec:** `specs/plan-completion-triage-and-gate-revert.md` (APPROVED 2026-11-17; decisions D1–D4)

## Global Constraints

- **Execution base.** `BASE101` is the commit at the start of Task 1 (Task 1 Step 1 records it). Line numbers below
  were taken at `b0994a6`. The old text in each edit step is the match key, not the line number. A match key ignores
  line breaks and indentation: the old text may wrap anywhere in the file. A text check that a rewrap could split
  runs on `FLAT <file>`, which is `tr -s ' \n' ' ' < <file>`.
- **A machinery stream runs alone.** This plan edits writing-plans and both executors, which drive every execution.
  Before Task 1, `mcp__ccd_session_mgmt__list_sessions` (or the owner) shows no other plan execution running in
  agent-skills, except plan 100's (D16). Execute in a worktree of your own. Call controller tooling through
  `~/.claude/skills/<skill>/scripts/…`, which resolves to the main checkout, so it keeps the old behavior all run
  long. Merge only when no other execution runs. This plan's own completion runs under main's old step 4 and old
  gate rule: that is expected (spec, Constraints).
- **Plan 100 before Task 9** (D15, D16). Tasks 1–8 may run while plan 100's execution runs. Before Task 9, this
  command lists plan 100's kit, so its execution has merged:
  `git ls-tree --name-only origin/main -- specs/baseline/red-baseline-handoff-rerun/kit/`. If it lists nothing,
  stop and ask your human partner. Task 9 Step 1 merges that kit into this branch and copies it.
- **Parallel sessions.** Before Task 1, and before each of Tasks 3–7, run `git fetch origin main` and
  `git log --oneline <BASE101>..origin/main -- skills/writing-plans/ skills/subagent-driven-development/SKILL.md skills/subagent-driven-development/references/final-review.md skills/executing-plans/references/final-review.md build/cc_guide/conformance.toml`.
  If it lists a commit, stop and tell your human partner before the task starts.
- **The writing-plans body budget.** The body (frontmatter stripped) stays at or under 19,700 characters after every
  commit. Measure it with `BODY`:
  `uv run --with pyyaml python -c "import sys, pathlib; sys.path.insert(0, 'build'); import check_conformance as c; print(len(c.skill_body(pathlib.Path('skills/writing-plans/SKILL.md').read_text())[0]))"`.
  Expected path, from 19,689 at `b0994a6`:

  | After | Edit | Delta (about) | Body (about) |
  |---|---|---|---|
  | Task 3 | step 4 rewrite | −360 | 19,330 |
  | Task 4 | step 1 names Declined to judge lines | +50 | 19,380 |
  | Task 6 | step 2 status line names both files | +55 | 19,435 |
  | Task 7 | guard sentence | −10 | 19,425 |

  The about 275 characters left are for wording rounds. A step that would pass 19,700 stops and asks.
- **The subagent-driven-development body.** Lane M4 owns it, and it is already past the window under the waiver
  `subagent-driven-development-compaction-window`. Task 7 must not make it longer than its base (19,926 at
  `b0994a6`). If its length changes, update both figures in that waiver's `reason` in
  `build/cc_guide/conformance.toml` in the same commit.
- **Commit gate.** Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Before a commit
  that changes a skill, also run `uv run --with pyyaml python build/check_conformance.py` (exit 0) and
  `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies`
  (pass: the spec adds no install dependency). Commit messages follow Conventional Commits, use plain technical
  English and end with the attribution trailer that the executing session is given.
- **Test counts.** Record what `uv run python build/run_suites.py writing-plans` reports in Task 1 Step 1 as the
  baseline. Expected counts below are deltas from it.
- **Deferral-scan wording.** The spec, this plan and the record retire into `completed/` folders, where the deferral
  lint reads them. Put note forms, marker forms and quoted deferral phrases in backticks, and give any deferral
  sentence a marker.
- **Leave alone.** `deferred_stats.py`, the Triage rubric, the Thresholds table, `commands/deferred.md` and
  finishing-a-development-branch (spec, Non-goals); `archive_deferred.py` (owner ruling of 2026-11-17 on the
  retired-plans item: the script does not edit plans); Protocol step 1's partition bullets; the retired spec
  `specs/completed/development-history-record.md`; plan 80's kit files and every committed rep file; every file of
  plan 40's harness (`~/.cache/agent-skills/handoffs/red/`) except `changes.log`, which gets one new line (Task 9);
  plan 100's kit and its committed results (Task 9 copies the kit and edits only the copy).
- **New kit** (spec, Micro-tests, as amended in Task 1). Kit `specs/baseline/red-baseline-completion-triage/kit/`,
  record `specs/baseline/red-baseline-completion-triage.md`. Every rep is a fresh
  `claude -p --model <case model> --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format json --max-budget-usd <case budget>`
  under `env -i`, run by the kit's `run_reps.sh` from its own new, empty directory `/tmp/plan101-rep-XXXXXX`. Work
  files go under `/tmp/plan101-work/`. Five scored reps per case and arm. Texts are read with `git show` at a sha,
  never through `~/.claude/skills/`. Each fixture and pass rule is committed before any rep of its case runs and is
  not edited after a rep is seen. Every verdict is read by hand from the full reply. No file in `kit/` is named
  `test_*.py` (Task 9's guard kit keeps plan 100's test files and registers them as a suite). Run reps in a local
  session on the owner's computer, so they sign in with the CLI's stored login.
- **Bars.** RED: `treatment 5/5; control fails at least 1 of 5`. Guard and regression: `treatment 5/5`. A case
  below its bar gets one wording round. Stop rule, exact: `A RED case whose control fails 0 of 5 has nothing to fix
  in wording. Record it and put it to the owner in the completion gate's batch. The spec-required wording still
  lands.`
- **Spend stops.** New kit: $30 for all its reps and plan 80's reruns, summed by `show_reps.py`. If the control arms
  alone pass $12, stop and ask your human partner. Task 9's guard kit: $20 for its pilot and its reps, summed from
  `total_cost_usd` in each rep's `turn<N>.json`. Past it, stop and ask.
- **Next-kit fixes** (D8). The new kit's `run_reps.sh` drops `credential_expires_at` from each rep JSON file it
  writes, and `kit_selftest.py` shows that, and that two reps get separate folders and cannot see each other's files.
  Task 9's guard kit is a copy of plan 100's kit, which carries all three fixes: one `HOME` per rep, run one after
  the other, the strip of `credential_expires_at`, and the PreToolUse guard that denies a `for`-loop read of the
  real home (D15).

## Review Focus

1. **A ledger line `Reverted at the gate: Task 2 ruling — …`.** `history_entry.py` must print no `Ruling` line and
   no warning line for it, or the history entry would record a reverted ruling as standing. Pinned in Task 5
   (`test_reverted_at_gate_line_is_not_a_ruling`).
2. **A revert of a ruling that the gate did not tag.** The spec says the rule covers any listed ruling, and the new
   sentence sits after the tagged-ruling sentence. Pinned in Task 8 by the guard case `gate-revert-untagged`.
3. **A plan retired with the old status line after this plan merges.** Other branches keep writing the old form
   until they rebase. The commit lint must still exempt it. Pinned in Task 6
   (`test_protocol_status_header_is_exempt` keeps both forms).
4. **A deferral phrase after the new status line on the same line.** Only the status line is exempt. The text after
   it must still be read. Pinned in Task 6 (`test_text_after_status_header_is_read`).
5. **A quoted status template in a retired plan's body.** Plans 80 and others quote the status form with
   `(YYYY-MM-DD)` placeholders. The one-time fix must change only each plan's real status line. Pinned in Task 6
   Step 7's check.

## Decisions

Numbered after the spec's D1–D4. The brief is the 2026-11-17 `/deferred` pass's lane M1 task.

- **D5** (owner, brief, 2026-11-17): fold in "Declined review line: writing-plans' completion gate does not name
  Declined to judge" after the step 4 shrink, in this plan. Applied in: Task 1 (spec amendment), Task 4.
- **D6** (owner, brief, 2026-11-17): fold in "Settle the wording and the test gap of the reworded roadmap-stage
  guard", with its reruns. Applied in: Task 7, Task 9.
- **D7** (owner, brief, 2026-11-17): fold in "Retired plans point at the live backlog after their deferred section
  has moved to the archive", with the owner's ruling of 2026-11-17: the status line names both backlog files, a
  one-time fix updates the old plans, and `archive_deferred.py` does not edit plans. Applied in: Task 6, Global
  Constraints (Leave alone).
- **D8** (owner, brief, 2026-11-17): every kit that this plan builds or reruns carries the three next-kit fixes:
  the `Read(~/**)` Bash-read gap, a per-rep scratch folder, and no `credential_expires_at` in rep JSON files.
  Applied in: Task 1 (spec amendment), Task 2, Task 9.
- **D9** (owner, brief, 2026-11-17): a machinery stream. It executes alone, in its own worktree, with the tooling
  pinned to main, and merges only when no other execution runs. Applied in: Global Constraints. D16 amends it.
- **D10** (owner, plan review, 2026-11-17): the spec's non-goal `No edit to Protocol step 1` covers the revert rule
  only, so Task 4 adds the final review's Declined to judge lines to step 1's leftovers. Amendment A1 says so.
  Applied in: Task 1 (spec amendment), Task 4.
- **D11** (owner, plan review, 2026-11-17): the one-time fix rewrites every real old-form status line in
  `specs/plans/completed/`, not only the 14 plans whose deferred section is now only in the archive. Each other old
  line would go stale when `/deferred` archives its section. Applied in: Task 6.
- **D12** (owner, plan review, 2026-11-17): the new status tail is exactly
  `deferred items in specs/deferred_items.md, or specs/completed/deferred_items.md once archived`. It is a format
  line that the agent copies, so it gets no micro-test. Applied in: Task 6.
- **D13** (owner, plan review, 2026-11-17): add two cases that the spec does not list: `gate-declined` (RED, for
  D10's wording) and `gate-revert-untagged` (guard, Review Focus 2). Amendment A3 adds them to the spec's table.
  Applied in: Task 1 (spec amendment), Task 2, Task 8.
- **D14** (owner, plan review, 2026-11-17): the reruns of `gate-tag` and `history-filter` build their prompts with
  plan 80's `build_prompts.py` and `cases.py` unchanged and run through the new kit's `run_reps.sh`, whose
  `claude -p` flags are the same. Amendment A2 says so. Applied in: Task 1 (spec amendment), Task 8.
- **D15** (owner, plan review, 2026-11-17): "Copy plan 100's kit (Recommended)". Asked after plan 100 (PR #225)
  merged with the `→ planned` notes on the three next-kit-fix items. Task 9 runs the guard rerun in a copy of plan
  100's kit, with plan 40's frozen arms, prompts and rubric. Plan 40's harness stays frozen except one
  `changes.log` line. The record that the `Read(~/**)` gap stays is dropped: plan 100 closes that item with its
  guard. Applied in: Global Constraints, Task 9, Completion notes.
- **D16** (owner, plan review, 2026-11-18): "Yes, amend D9". Tasks 1–8 may run while plan 100's execution runs.
  Task 9 starts only after plan 100's execution has merged, and its Step 1 first merges `origin/main` into this
  branch. No other execution may overlap this plan, and D9's merge rule stands. The control and treatment reps keep
  `BASE101` and `T8`. Neither holds Step 1's merge, so they differ only by this plan's edits. Applied in: Global
  Constraints, Task 9.

## Plan review

Resolved on 2026-11-17. The owner accepted the planner's call on all seven open items ("accept all"). Plan 100 then
merged with a different design for the same three next-kit-fix items, so items 6 and 7 were asked again, and the
owner chose to copy plan 100's kit. D10–D15 record the answers. On 2026-11-18 the owner let Tasks 1–8 run while
plan 100's execution runs (D16).

---

### Task 1: Spec amendments

**Files:**
- Modify: `specs/plan-completion-triage-and-gate-revert.md` (Non-goals; Micro-tests, Kit; Micro-tests table)

**Interfaces:**
- Produces: the amended spec that Tasks 2, 4 and 8 follow. The status line stays `APPROVED (2026-11-17)`.

- [ ] **Step 1: Record the base and run the parallel-session check**

Run: `git rev-parse --short HEAD`. Note it as `BASE101`. Run the Global Constraints' `git log` check. Expected: no
commit listed. Run `uv run python build/run_suites.py writing-plans` and note its pytest summary as the test-count
baseline.

- [ ] **Step 2: Apply A1 (Non-goals)**

Replace:

```text
- No edit to Protocol step 1. Its `Unblocked by an answer → implement it now` already holds the rule (D2). The gate
  paragraphs send the revert there, as they already do for an overruled `(unclear)` ruling.
```

with:

```text
- No edit to Protocol step 1 for the revert. Its `Unblocked by an answer → implement it now` already holds the rule
  (D2). The gate paragraphs send the revert there, as they already do for an overruled `(unclear)` ruling. Plan 101
  adds the final review's Declined to judge lines to step 1's leftovers, for the item that the next bullet names
  (owner, plan 101, 2026-11-17).
```

In the next bullet, after its marker `→ item: 73-reviewer-and-planning-contract — 2026-10-30.`, add the sentence
`Plan 101 folds it in after the step 4 shrink (owner, plan 101, 2026-11-17).` Rewrap at the file's width.

- [ ] **Step 3: Apply A2 (Micro-tests, Kit)**

Replace:

```text
are copies of plan 80's kit, with only the plan number and temp prefix changed.
```

with:

```text
are copies of plan 80's kit, with the plan number and temp prefix changed and the next-kit fixes added:
`run_reps.sh` drops `credential_expires_at` from each rep JSON file, and a no-model self-test shows that each rep
has its own scratch folder (owner, plan 101, 2026-11-17).
```

Replace:

```text
The re-runs of `gate-tag` and `history-filter` use plan 80's kit unchanged,
```

with:

```text
The re-runs of `gate-tag` and `history-filter` build their prompts with plan 80's kit unchanged and run them
through this kit's `run_reps.sh` (owner, plan 101, 2026-11-17),
```

Rewrap the paragraph at the file's width.

- [ ] **Step 4: Apply A3 (Micro-tests table)**

After the `gate-tag-ep` row, add:

```text
| `gate-revert-untagged` | guard | `skills/subagent-driven-development/references/final-review.md` | As `gate-revert-sdd`, but the partner reverts the Task 3 module-name ruling, which the gate did not tag (owner, plan 101, 2026-11-17). | As `gate-revert-sdd`, for the Task 3 ruling. |
| `gate-declined` | RED | writing-plans `SKILL.md` body | Protocol step 1, run from writing-plans alone after a `/clear`. The final review left one finding unfixed and two Declined to judge lines (owner, plan 101, 2026-11-17). | The gate message puts both Declined to judge lines and the unfixed finding to the partner, in one batch. |
```

- [ ] **Step 5: Check and commit**

Run: `git diff --stat` (one file) and `bash build/run_commit_lints.sh`. Expected: `commit lints passed`.

```bash
git add specs/plan-completion-triage-and-gate-revert.md
git commit -m "docs(specs): amend the completion-triage spec for plan 101's folded items"
```

### Task 2: The kit, its next-kit fixes, and the control arms

**Files:**
- Create: `specs/baseline/red-baseline-completion-triage/kit/{run_reps.sh,isolation_probe.txt,show_reps.py,build_prompts.py,cases.py,scrub_json.py,kit_selftest.py}`
- Create: `specs/baseline/red-baseline-completion-triage.md`
- Create: `specs/baseline/red-baseline-completion-triage/control/<case>/rep<N>.json`

**Interfaces:**
- Produces: `cases.CASES` with keys `triage-narrow`, `triage-aged`, `gate-revert-sdd`, `gate-revert-ep`,
  `gate-revert-untagged`, `history-revert`, `gate-tag-ep`, `gate-declined`; `scrub_json.scrub(text: str) -> str`;
  the record's `## Base`, `## Control` sections. Task 8 runs the treatment arms with this kit, and runs plan 80's
  reruns through its `run_reps.sh`.

- [ ] **Step 1: Copy plan 80's kit**

Copy `run_reps.sh`, `isolation_probe.txt`, `show_reps.py` and `build_prompts.py` from
`specs/baseline/red-baseline-development-history/kit/`. Change the plan number in comments and docstrings (80 → 101),
the temp prefix (`/tmp/plan80-rep-` → `/tmp/plan101-rep-`), and `show_reps.py`'s `AIDS` to flag `/deferred`,
`Reverted at the gate`, `Declined`, `deferred item` and `\?`. `isolation_probe.txt` stays unchanged.

- [ ] **Step 2: Write the failing self-test**

`kit_selftest.py` (stdlib, run as `uv run python <kit>/kit_selftest.py`, prints `kit self-test passed` or raises).
It writes a stub `claude` (a `#!/usr/bin/env python3` script) into a temporary directory and runs `run_reps.sh`
with that directory first on `PATH`. The stub ignores its arguments, writes a file `marker-<its pid>` into its
working directory, and prints to stdout one JSON object: `type` `result`; `result`, a string that holds the stub's
working directory on its first line and then the sorted names in that directory, one a line; `total_cost_usd` 0;
`num_turns` 1; `credential_expires_at` at the top level; and `usage` holding a nested `credential_expires_at`. The
test runs `run_reps.sh` on a one-line prompt for reps 1 and 2 into a temporary output folder, then asserts:
- `credential_expires_at` occurs in neither `rep1.json` nor `rep2.json` (raw text check), and both still parse as
  JSON with `type`, `result` and `total_cost_usd` intact;
- each rep's `result` lists exactly one name, a `marker-` file, and the two markers differ (each rep sees only its
  own folder's files);
- the two working directories differ, and both start with `/tmp/plan101-rep-` or `/private/tmp/plan101-rep-`.

Run: `uv run python specs/baseline/red-baseline-completion-triage/kit/kit_selftest.py`.
Expected: FAIL on the `credential_expires_at` assertion (the copied runner does not scrub yet).

- [ ] **Step 3: Implement `scrub(text: str) -> str` in `scrub_json.py`, and call it from `run_reps.sh`**

`scrub` parses `text` as JSON and drops every `credential_expires_at` key at any depth. It returns the JSON dumped
with `ensure_ascii=False`. When `text` does not parse, it returns `text` with each line that contains
`credential_expires_at` removed, so `show_reps.py` still sees an unreadable, VOID rep. As a script,
`python3 scrub_json.py <file>` rewrites `<file>` in place. In `run_reps.sh`, set `KIT` to the runner's own
folder as an absolute path before any `cd`, write `claude`'s stdout to `$OUT/rep$1.json` as now, and then, after the
rep's subshell, run `python3 "$KIT/scrub_json.py" "$OUT/rep$1.json"`.

- [ ] **Step 4: Run the self-test**

Run: Step 2's command. Expected: `kit self-test passed`.

- [ ] **Step 5: Write `cases.py`**

Same shape as plan 80's (`case(texts, fixture, task, pass_rule, leak, bar)`, `VOID`, constants). Models:
`claude-sonnet-5-5`, budget `0.75`, for the two triage cases; `claude-opus-5-5`, budget `1.00`, for the rest.
Every fixture uses plan 80's bike-share dock-status domain (`specs/plans/12-dock-alerts.md`,
`specs/dock-alerts.md`), and never names this repository. Gate and history cases reuse plan 80's ledger: the Task 2
ruling (`contradicts spec: § 2 Alert threshold`), the Task 3 module-name ruling, the Task 3 batch-email ruling and
the final-review retry-jitter ruling. The task line for a case whose reply acts uses plan 74's `TASK_TAIL`
(`specs/baseline/red-baseline-backlog-protocol/kit/cases.py`).

| Case | Texts | Fixture must hold | Pass rule (register verbatim) | Leak |
|---|---|---|---|---|
| `triage-narrow` | `skills/writing-plans/SKILL.md`, `skills/writing-plans/references/deferred-backlog.md` | Steps 1–3 done. Step 3 appended two items to a new section `12-dock-alerts`, each with its title and `Size:`. `deferred_stats.py` printed `Deferred backlog: 26 open, 51 ever closed (closure rate 66%), aged >45d: 0.` and the volume line. The 26 open items, one line each, in 9 sections, so a triage is possible. | `PASS = the reply shows the summary line and both new items; it presents no disposition proposal over the backlog (no grouped or sorted list of the older items with a proposed action); and it goes on to step 5 or names /deferred for the full triage. FAIL = any of these does not hold.` | `Backlog report\|full triage\|waits for` |
| `triage-aged` | as `triage-narrow` | The same, with `aged >45d: 2.` and two of the 26 items 50 and 61 days old. | `PASS = the reply shows the summary line and both new items; it presents a read-only grouped disposition proposal over the backlog; it edits no file for the proposal; and it does not stop the protocol on it (it goes on to step 5, or says that it does). FAIL = any of these does not hold.` | as `triage-narrow` |
| `gate-revert-sdd` | `skills/subagent-driven-development/references/final-review.md` | Plan 80's gate fixture. The gate message went out listing the four rulings, the Task 2 ruling tagged. The partner answers: revert the Task 2 ruling, the others stand. | `PASS = the next action implements the revert now, as a task before plan markup; the reply writes a ledger line that names the Task 2 ruling; and it writes no backlog item for the revert. FAIL = any of these does not hold.` | `Reverted at the gate\|follow-up task\|protocol step 1` |
| `gate-revert-ep` | `skills/executing-plans/references/final-review.md` | `gate-revert-sdd`'s, recast as an executing-plans run (inline execution, the whole-plan review). | As `gate-revert-sdd`, with `implements the revert now, inline, before plan markup`. | as `gate-revert-sdd` |
| `gate-revert-untagged` | as `gate-revert-sdd` | `gate-revert-sdd`'s, but the partner reverts the Task 3 module-name ruling, and the others stand. | As `gate-revert-sdd`, for the Task 3 module-name ruling. | as `gate-revert-sdd` |
| `history-revert` | `skills/writing-plans/SKILL.md`, `skills/writing-plans/references/histor*.md` | Plan 80's history fixture, after a `/clear`: the gate message is not in context. The ledger, shown in full, holds the four rulings and `Reverted at the gate: Task 2 ruling — alert at 3 or fewer free slots`. The revert's commits are in. The draft still lists the Task 2 ruling. | `PASS = the entry leaves out the Task 2 ruling; keeps the module-name ruling labelled "Ruling (Task 3)" with its what, why and cost parts; leaves out the batch-email and retry-jitter rulings; keeps the Deviation line with a Source pointer and the closed-item line with its quoted title and "(deferred by 9-dock-status)" unchanged; and leaves the heading and Plan line unchanged. FAIL = any of these does not hold.` | `changed the build\|kept the plan as written\|rule 3` |
| `gate-tag-ep` | `skills/executing-plans/references/final-review.md` | Plan 80's `GATE_FIXTURE`, recast as an executing-plans run. Task: plan 80's `GATE_TASK`. | Plan 80's `GATE_PASS`, verbatim. | plan 80's `GATE_LEAK` |
| `gate-declined` | `skills/writing-plans/SKILL.md` | After a `/clear`, the partner says "complete the plan". Only writing-plans is loaded. All four tasks are done. The final review left one Important finding unfixed (`send_alert` retries forever on a 5xx) and two Declined to judge lines: "Whether email is the right channel for alerts sent at night." and "Whether 2 free slots is the right threshold for docks next to stations." The ledger has no ruling. Task: write the message you send your partner at protocol step 1. | `PASS = the message puts both Declined to judge lines and the unfixed finding to the partner, each for a ruling, in one message; and it files neither Declined line as a deferred item without asking. FAIL = any of these does not hold.` | `Declined to judge` (expected in the fixture: record it) |

Bars: `BAR` (RED) for `triage-narrow`, `gate-revert-sdd`, `gate-revert-ep`, `history-revert`, `gate-declined`;
`'treatment 5/5'` (guard) for `triage-aged`, `gate-revert-untagged`, `gate-tag-ep`.

- [ ] **Step 6: Write the record, run the leak check, commit the registration**

Record sections, in order: `## Base` (`BASE101`), `## Kit` (what was copied and what changed, including the
next-kit fixes), `## Arms` (control at `BASE101`; treatment at `T7`, Task 7's commit; a wording round at its own
commit), `## Bars`,
`## Spend stops`, `## Stop rule`, `## Leak check`, `## Reading rules` (the VOID rule and every pass rule, copied from
`cases.py`).

Run: `uv run python specs/baseline/red-baseline-completion-triage/kit/build_prompts.py leakview /tmp/plan101-work/leak`,
then `grep -nE '<leak>' /tmp/plan101-work/leak/<case>.txt` for each case. Expected: no hit except the ones the table
names. Record each hit and why it stands.

```bash
git add specs/baseline/red-baseline-completion-triage specs/baseline/red-baseline-completion-triage.md
git commit -m "test(specs): register the completion-triage micro-tests with the next-kit fixes"
```

- [ ] **Step 7: Run the isolation probe**

Run: `bash specs/baseline/red-baseline-completion-triage/kit/run_reps.sh specs/baseline/red-baseline-completion-triage/kit/isolation_probe.txt /tmp/plan101-work/probe 1 1 claude-opus-5-5`.
Expected: all five lines `NO`. Record the Claude Code version and the result in `## Isolation probe`. Any `YES`:
stop and ask your human partner.

- [ ] **Step 8: Run and read the control arms**

Run: `uv run python specs/baseline/red-baseline-completion-triage/kit/build_prompts.py <BASE101> /tmp/plan101-work/control`,
then for each case
`bash specs/baseline/red-baseline-completion-triage/kit/run_reps.sh /tmp/plan101-work/control/<case>.txt specs/baseline/red-baseline-completion-triage/control/<case> 1 5 <model> <budget>`.
Rerun VOID reps with the next free number. Read each reply in full with `show_reps.py`, and write `## Control`: one
line per scored rep (`rep<N>: PASS|FAIL — <reason>`), the fail count per case, the spend. Apply the stop rule to each
RED case whose control fails 0 of 5.

- [ ] **Step 9: Commit the control arms**

```bash
git add specs/baseline/red-baseline-completion-triage specs/baseline/red-baseline-completion-triage.md
git commit -m "test(specs): run the completion-triage control arms"
```

### Task 3: Step 4 becomes the backlog report

**Files:**
- Modify: `skills/writing-plans/SKILL.md:363-384` (step 4)
- Modify: `skills/writing-plans/references/deferred-backlog.md:9-10` (the callers line)

**Interfaces:**
- Produces: step 4 under the heading `**4. Backlog report.**`. Task 8's triage arms read it at `T8`.

- [ ] **Step 1: Write the failing check**

Run: `grep -c '4. Backlog report' skills/writing-plans/SKILL.md; FLAT skills/writing-plans/references/deferred-backlog.md | grep -c 'triage only when the aged tail is above 0'`.
Expected: `0` and `0`.

- [ ] **Step 2: Replace step 4**

Replace the whole of step 4, from `**4. Backlog triage.**` up to the blank line before `**5. Retire.**`, with the
spec's draft (spec, Design, Step 4):

````markdown
**4. Backlog report.** Run from the repo root:

```bash
uv run <this-skill-dir>/scripts/deferred_stats.py
```

Put its summary line (open count, closure rate, aged tail) in the completion
report, and under it the items step 3 appended for this plan, one line each,
or `nothing deferred`. Always: the summary keeps the trend legible.

When `aged >45d:` is above 0, also run steps 1–4 of the **Triage rubric** in
`references/deferred-backlog.md`, which are read-only, and present the
proposal in this completion batch. Otherwise the full triage waits for
`/deferred`, which alone executes a disposition. The triage never blocks
completion — the aged tail is gated at finishing-a-development-branch.
````

Add nothing more to `SKILL.md`. The spec's designer's call (each listed item gives its first words and its `Size:`)
describes what the agent writes in its report, and `triage-narrow`'s pass rule reads that report.

- [ ] **Step 3: Replace the callers line**

In `references/deferred-backlog.md`, replace:

```text
- **writing-plans** § Plan Completion Protocol — writes items (schema below)
  and runs the read-only triage at completion.
```

with:

```text
- **writing-plans** § Plan Completion Protocol — writes items (schema below),
  shows the stats line and the plan's new items at completion, and runs the
  read-only triage only when the aged tail is above 0.
```

- [ ] **Step 4: Run the checks**

Run: Step 1's command. Expected: `1` and `1`. Run `BODY`. Expected: about 19,330, and at most 19,700. Run
`git grep -n 'Backlog triage' -- skills/ commands/ agents/`. Expected: no hit. Run the commit gate.

- [ ] **Step 5: Commit**

```bash
git add skills/writing-plans/SKILL.md skills/writing-plans/references/deferred-backlog.md
git commit -m "feat(writing-plans): narrow the completion triage to a backlog report"
```

### Task 4: Step 1 names the final review's Declined to judge lines

**Files:**
- Modify: `skills/writing-plans/SKILL.md:292-293` (step 1's leftovers sentence)

**Interfaces:**
- Produces: the step 1 wording that Task 8's `gate-declined` arm reads at `T8`.

- [ ] **Step 1: Write the failing check**

Run: `FLAT skills/writing-plans/SKILL.md | grep -c "the final review's Declined to judge lines"`. Expected: `0`.

- [ ] **Step 2: Edit step 1**

Replace `Collect the leftovers: plan steps skipped or descoped during execution, plus review findings that were not
fixed.` with `Collect the leftovers: plan steps skipped or descoped during execution, review findings that were not
fixed, and the final review's Declined to judge lines.` Rewrap the paragraph at its width. Leave the partition
bullets unchanged: a Declined to judge line needs the partner's ruling, so the first bullet already asks.

- [ ] **Step 3: Run the checks**

Run: Step 1's command. Expected: `1`. Run `BODY`. Expected: at most 19,700. Run the commit gate.

- [ ] **Step 4: Commit**

```bash
git add skills/writing-plans/SKILL.md
git commit -m "feat(writing-plans): name Declined to judge lines among the gate's leftovers"
```

### Task 5: One rule for a revert asked for at the gate

**Files:**
- Modify: `skills/subagent-driven-development/references/final-review.md:43-44`
- Modify: `skills/executing-plans/references/final-review.md:174-175`
- Modify: `skills/writing-plans/references/history.md:78-79` (Finish the draft, step 1)
- Test: `skills/writing-plans/scripts/test_history_entry.py`

**Interfaces:**
- Produces: the ledger form `Reverted at the gate: <task> ruling — <its first words>`, which both gate paragraphs
  write and history "Finish the draft" step 1 reads. Task 8's gate and history arms read these files at `T8`.

- [ ] **Step 1: Pin the ledger form against `history_entry.py`**

Add `test_reverted_at_gate_line_is_not_a_ruling` to `test_history_entry.py`, built like
`test_ruling_quoted_inside_a_ledger_note_is_not_a_ruling` (`write_repo`, `run_draft`, `TINY_PLAN`, `DATE`). Its ledger
holds `Task 2: Ruling: alert at 3 or fewer free slots — refill is slow — one extra alert a day if
wrong.` and the line `Reverted at the gate: Task 2 ruling — alert at 3 or fewer free slots`. Assert that the draft's
output has exactly one line that starts with `- Ruling` (the Task 2 ruling), and no line that contains
`Reverted at the gate` or starts with `Rulings: ledger line`.

Run: `uv run python build/run_suites.py writing-plans -- -k reverted_at_gate`. Expected: PASS (it pins the form the
spec chose, so it passes before any edit). If it fails, stop: the form needs a change that the spec did not make.

- [ ] **Step 2: Write the failing check**

Run, for each of `skills/subagent-driven-development/references/final-review.md` and
`skills/executing-plans/references/final-review.md`: `FLAT <file> | grep -c 'which makes it a deferred item'`; then
`FLAT skills/writing-plans/references/history.md | grep -c 'that a .Reverted at the gate:. ledger line names'`.
Expected: `1`, `1`, `0`.

- [ ] **Step 3: Edit both gate paragraphs**

In each file, replace `Your partner may still ask to revert it, which makes it a deferred item.` with the sentence
below, identical in both files. Rewrap each paragraph at its own width. Change nothing else.

```text
If your partner asks to revert a ruling, tagged or not, the revert is a
follow-up task, and protocol step 1 implements it now. Ledger it as
`Reverted at the gate: <task> ruling — <its first words>`, so that a restarted
gate shows that ruling as reverted and asks nothing about it, and the history
entry leaves it out.
```

- [ ] **Step 4: Edit history "Finish the draft" step 1**

Replace its two lines with the spec's draft (spec, Design, History "Finish the draft" step 1):

```text
1. Delete each ruling that did not change what got built against the spec or the plan: one that declined a finding
   and kept the plan as written, one that parked a finding with no change to the build, or one that a
   `Reverted at the gate:` ledger line names.
```

- [ ] **Step 5: Run the checks**

Run: Step 2's commands. Expected: `0`, `0`, `1`. Run: `diff <(tr -s ' \n' ' ' < skills/subagent-driven-development/references/final-review.md | grep -o 'If your partner asks to revert.*leaves it out\.') <(tr -s ' \n' ' ' < skills/executing-plans/references/final-review.md | grep -o 'If your partner asks to revert.*leaves it out\.')`.
Expected: no output (one identical sentence). Run `uv run python build/run_suites.py writing-plans` (+1 over the
baseline, all pass), `uv run python build/check_reviewer_block.py`, and the commit gate.

- [ ] **Step 6: Commit**

```bash
git add skills/subagent-driven-development/references/final-review.md skills/executing-plans/references/final-review.md skills/writing-plans/references/history.md skills/writing-plans/scripts/test_history_entry.py
git commit -m "feat(executors): do a revert asked for at the gate now and ledger it"
```

### Task 6: The status line names both backlog files

**Files:**
- Modify: `skills/writing-plans/scripts/deferral_scan.py:37-39` (docstring) and `:221-224` (`STATUS_HEADER`)
- Test: `skills/writing-plans/scripts/test_deferral_scan.py:110-115`
- Modify: `skills/writing-plans/SKILL.md:310` (step 2's status line)
- Modify: `skills/writing-plans/references/deferred-backlog.md:277-279` (Markers: the exempt forms)
- Modify: the status line of every retired plan under `specs/plans/completed/` that carries the old form (D11)

**Interfaces:**
- Produces: the status tail `deferred items in specs/deferred_items.md, or specs/completed/deferred_items.md once
  archived`, exact (D12). `STATUS_HEADER` accepts it and the old tail
  `deferred items in specs/deferred_items.md` and `nothing deferred`.

- [ ] **Step 1: Write the failing tests**

In `test_deferral_scan.py`, extend `test_protocol_status_header_is_exempt` with a third line, the new form:
`'**Status: COMPLETE (2026-01-01)** — executed via x; deferred items in specs/deferred_items.md, or specs/completed/deferred_items.md once archived'`,
and assert `unmarked(<it>) == []`. Keep the two existing assertions. Add
`test_text_after_status_header_is_read`: the new form followed by `; the retry path is deferred to a future plan`
on the same line gives exactly one `Candidate` for line 1.

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run python build/run_suites.py writing-plans -- -k "status_header"`.
Expected: `test_protocol_status_header_is_exempt` FAILS on the new form.
`test_text_after_status_header_is_read` passes before and after the change (the regex is anchored at the line end):
it is a guard, so confirm it by reading its assertion, not its RED.

- [ ] **Step 3: Widen `STATUS_HEADER`**

Make the tail `deferred items in specs/deferred_items\.md(?:, or specs/completed/deferred_items\.md once archived)?`
or `nothing deferred`, still anchored at `\s*$`. Update the docstring's exempt-forms sentence to name the new form.

- [ ] **Step 4: Run the suite**

Run: `uv run python build/run_suites.py writing-plans`. Expected: +1 test over the baseline (+2 with Task 5's), all
pass.

- [ ] **Step 5: Edit the template and the reference**

In `SKILL.md` step 2, replace the status line's tail `deferred items in specs/deferred_items.md` with the new tail
(the `nothing deferred` line stays). In `deferred-backlog.md`'s Markers paragraph, replace:

```text
its status header (`deferred items in specs/deferred_items.md` and `nothing deferred`)
```

with:

```text
its status header (`deferred items in specs/deferred_items.md`, with or without
`, or specs/completed/deferred_items.md once archived`, and `nothing deferred`)
```

Run `BODY`. Expected: at most 19,700.

- [ ] **Step 6: Commit the rule**

Run the commit gate, then:

```bash
git add skills/writing-plans/scripts/deferral_scan.py skills/writing-plans/scripts/test_deferral_scan.py skills/writing-plans/SKILL.md skills/writing-plans/references/deferred-backlog.md
git commit -m "feat(writing-plans): the plan status line names both backlog files"
```

- [ ] **Step 7: The one-time fix**

Select each file under `specs/plans/completed/` whose first 6 lines hold a line matching
`^\*\*Status: COMPLETE \(\d{4}-\d{2}-\d{2}\)\*\* — .*deferred items in specs/deferred_items\.md\s*$` (a real date,
never a placeholder). Fix every selected file (D11). In each one, replace that one line's tail with the new tail.
Do it with a one-off Python snippet; ship no script.

Check: `git diff -U0 -- specs/plans/completed/ | grep -c '^+\*\*Status: COMPLETE (2[0-9-]*)\*\*.*once archived$'`
equals the number of files changed (`git diff --name-only -- specs/plans/completed/ | wc -l`), and
`git diff -U0 -- specs/plans/completed/ | grep '^[-+]' | grep -v '^[-+][-+]' | grep -vc 'Status: COMPLETE'` prints
`0` (no other line changed). Expected count: 72 at `275edc1`, plus each plan retired with the old line since then.

- [ ] **Step 8: Run the lints and commit the fix**

Run: `uv run skills/writing-plans/scripts/deferral_scan.py lint --baseline build/deferral_baseline.txt` (exit 0)
and `uv run python build/check_links.py`.

```bash
git add specs/plans/completed/
git commit -m "chore(specs): point retired plans at both backlog files"
```

### Task 7: The roadmap-stage guard wording

**Files:**
- Modify: `skills/writing-plans/SKILL.md:37-38`
- Modify: `skills/subagent-driven-development/SKILL.md:220-221`
- Modify: `skills/executing-plans/references/final-review.md:211-214`
- Modify (if the body length changes): `build/cc_guide/conformance.toml:810`

**Interfaces:**
- Produces: the guard text that Task 9's treatment reps carry (`KIT_COMMIT` `T8`). The new sentence fixes the
  item's reading (b): the branch is the one the stage merged into, and the session, not the stage, is what starts.
  The executing-plans parenthesis fixes reading (a): it names writing-plans' protocol.

- [ ] **Step 1: Write the failing check**

Run: `git grep -c 'runs the protocol on the merged branch now' -- skills/; FLAT skills/executing-plans/references/final-review.md | grep -c "of writing-plans' protocol step 3a"`.
Expected: three files with `1`; and `0`.

- [ ] **Step 2: Edit the three sentences**

In all three files, replace `A stage this session finds already merged when it starts, with the protocol not yet
run, runs the protocol on the merged branch now.` with:

```text
A stage merged before this session began, with the protocol not run, runs the
protocol now on the branch it merged into.
```

In `executing-plans/references/final-review.md`, also replace `(step 3a's Handoff bullets and stamp still name the
stages they feed)` with `(the Handoff bullets and stamp of writing-plans' protocol step 3a still name the stages
they feed)`. Rewrap each paragraph at its width.

- [ ] **Step 3: Run the checks**

Run: Step 1's command. Expected: no hit; and `1`. Run `BODY`. Expected: at most 19,700. Measure the
subagent-driven-development body with `BODY`'s command on its path. Expected: at most 19,926. If it changed, update
the waiver's `reason` figures (`The body is <n> characters, <n − 19,700> over …`). Run the commit gate, the
declared-dependencies test included.

- [ ] **Step 4: Commit and record `T7`**

```bash
git add skills/writing-plans/SKILL.md skills/subagent-driven-development/SKILL.md skills/executing-plans/references/final-review.md build/cc_guide/conformance.toml
git commit -m "fix(skills): name the branch in the already-merged roadmap-stage guard"
```

Run: `git rev-parse --short HEAD`. Note it as `T7`.

### Task 8: Treatment arms, plan 80's reruns, and wording rounds

**Files:**
- Create: `specs/baseline/red-baseline-completion-triage/treatment/<case>/rep<N>.json`
- Create: `specs/baseline/red-baseline-development-history/plan101/<case>/rep<N>.json`
- Modify: `specs/baseline/red-baseline-completion-triage.md`, `specs/baseline/red-baseline-development-history.md`

**Interfaces:**
- Consumes: Task 2's kit; the texts at `T7`.
- Produces: `T8`, the last text commit before Task 9's reps (`T7` unless a wording round commits).

- [ ] **Step 1: Run and read the treatment arms**

First compare `claude --version` with the version in the record's `## Isolation probe`. If it is newer, rerun Task 2
Step 7's probe and record it before any treatment rep.

Run: `uv run python specs/baseline/red-baseline-completion-triage/kit/build_prompts.py <T7> /tmp/plan101-work/treatment`,
then `run_reps.sh` for each case into `specs/baseline/red-baseline-completion-triage/treatment/<case>`, as Task 2
Step 8. Read every reply. Write `## Treatment` in the record as `## Control` is written. The record states that the
`triage-*`, `history-revert` and `gate-declined` arms read a body that also holds Tasks 4, 6 and 7's edits.

- [ ] **Step 2: Rerun `gate-tag` and `history-filter`**

Run: `uv run python specs/baseline/red-baseline-development-history/kit/build_prompts.py <T7> /tmp/plan101-work/rerun gate-tag history-filter`,
then for each case
`bash specs/baseline/red-baseline-completion-triage/kit/run_reps.sh /tmp/plan101-work/rerun/<case>.txt specs/baseline/red-baseline-development-history/plan101/<case> 1 5 claude-opus-5-5 1.00`.
Read each reply against plan 80's pass rule. Append `## Plan 101 re-run (<date>)` to
`specs/baseline/red-baseline-development-history.md`: the sha, the runner used and why (D8), one verdict line per
rep, the count. The `gate-tag` bar met closes the revert item's `Done when:` together with Task 5.

- [ ] **Step 3: Wording rounds**

For each case below its bar: one wording round inside the text that the case tests, within the spec's content.
Commit it (`fix(<skill>): <case> wording round`), rerun that case's treatment arm and every other case that reads
the same file, into a `treatment-r1/` folder, and record both. Run `BODY` after any `SKILL.md` round. A case still
below its bar goes to the owner at the completion gate. Note the last text commit as `T8`.

- [ ] **Step 4: Check the spend and commit**

Run: `uv run python specs/baseline/red-baseline-completion-triage/kit/show_reps.py specs/baseline/red-baseline-completion-triage/*/* specs/baseline/red-baseline-development-history/plan101/*`.
Expected: total at most $30.

```bash
git add specs/baseline/
git commit -m "test(specs): run the completion-triage treatment arms and plan 80's reruns"
```

### Task 9: The guard rerun in a copy of plan 100's kit

The controller runs this task. An implementer subagent may take Steps 2 and 3. `$RED` is plan 40's frozen harness,
`~/.cache/agent-skills/handoffs/red`: read it, and append only to its `changes.log`. `GK` is
`specs/baseline/red-baseline-completion-triage/guard-kit`. `$CTL` is `~/.cache/agent-skills/handoffs/guard101`.
`KIT100` is the `origin/main` commit that Step 1 merges into this branch. It holds plan 100's kit (D16).
Plan 46's Task 4 (`specs/plans/completed/46-sdd-bundle.md`) is the pattern for the arms and the scoring. Plan 100's
Tasks 2–5 (`specs/plans/100-prepare-handoff-rerun.md`, or its retired path) are the pattern for the kit. Follow them
where this task is silent (D15).

**Files:**
- Create: `GK/`, a copy of `specs/baseline/red-baseline-handoff-rerun/kit/` at `KIT100`
- Modify: `GK/run_rep.sh`, `GK/make_reps.py`, `GK/arms.tsv`, `GK/tally.py`, `GK/test_rerun_runner.py`, `GK/prompts/`
- Create: `GK/prompts/c5a-merged.t1.txt`, `GK/prompts/c5a-merged.t2.txt`, `GK/rubric-c5a-merged.md`
- Modify: `build/suites.toml` (one `[[suite]]` table, `completion-triage-guard-kit`)
- Create: `specs/baseline/red-baseline-completion-triage/scores/<arm>.tsv`
- Modify: `specs/baseline/red-baseline-completion-triage.md` (`## Roadmap-stage guard`)
- Modify (outside the repository): `$RED/changes.log` (one line)

**Interfaces:**
- Consumes: plan 100's kit at `KIT100`: `run_rep.sh REP`, `run_batch.sh BATCH`, `make_reps.py ARM PHASE COUNT BATCH`
  with `KIT_COMMIT` in the environment, `extract.py BATCH` and `extract.py --rep REP`, `tally.py PHASE`, `arms.tsv`,
  and the variables `PHR_ROOT`, `PHR_CTL`, `PHR_TEMPLATES` and `CLAUDE_BIN` (plan 100, Tasks 2 and 3 Interfaces).
  Where the kit differs from plan 100's text, the kit is right. `BASE101`; `T8`; `KIT100`.
- Produces: the verdicts that close the guard item's `Done when:`.

- [ ] **Step 1: Merge `main`, copy the kit and register its suite**

Run the Global Constraints' plan 100 check and their Parallel-sessions check. Then run `git fetch origin main`,
record `git rev-parse origin/main` as `KIT100`, and run
`git merge --no-ff <KIT100> -m "chore: merge main for plan 100's kit (plan 101, D16)"`. If the merge stops on a
conflict, stop and ask your human partner. Run the Commit gate's lints on the result. From here on, Task 9's review
diff starts at the merge commit, and the final review's diff starts at `KIT100`, so plan 100's changes stay out of
both.

Run: `git ls-tree --name-only <KIT100> -- specs/baseline/red-baseline-handoff-rerun/kit/`. Expected: plan 100's kit
files. Then:

```bash
mkdir -p specs/baseline/red-baseline-completion-triage/guard-kit
git archive <KIT100> specs/baseline/red-baseline-handoff-rerun/kit/ | tar -x --strip-components=4 -C specs/baseline/red-baseline-completion-triage/guard-kit/
```

In `build/suites.toml`, add a copy of the `handoff-rerun-kit` table with the name `completion-triage-guard-kit` and
the directory `GK`. If a copied test names plan 100's kit path, point it at `GK` and change nothing else.

Run: `uv run python build/run_suites.py completion-triage-guard-kit` and `uv run python build/run_suites.py --check`.
Expected: the same pass count as `handoff-rerun-kit`, and the check passes.

```bash
git add specs/baseline/red-baseline-completion-triage/guard-kit/ build/suites.toml
git commit -m "chore(specs): copy plan 100's kit as plan 101's guard kit"
```

- [ ] **Step 2: Write the failing tests**

In `GK/test_rerun_runner.py`:
- `test_merged_extra_starts_on_merged_main`: a template repo has `main` and `feat/s2a-csv-export` one commit ahead,
  with HEAD on the feature branch, as `t4` has. In a rep of an arm whose `extra` is `merged`, the stub's first turn
  records `git log --format=%s -1` as `Merge branch 'feat/s2a-csv-export'`,
  `git branch --format='%(refname:short)'` as `main` only, and `git rev-parse main origin/main` as one sha twice.
- `test_unknown_extra_refuses`: for an arm whose `extra` is `other`, `run_rep.sh` exits 3 and runs no turn.
- `test_ids_start_at_r501`: the first row that `make_reps.py` writes into an empty `$PHR_CTL` has the id `r501`.
- `test_env_holds_no_session_variables` (change the copied test): the stub's environment holds
  `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=3600000` and no other name that starts `CLAUDE`, except
  `CLAUDE_CODE_DISABLE_ADVISOR_TOOL`.

Run: `uv run python build/run_suites.py completion-triage-guard-kit`. Expected: these four fail, the rest pass.

- [ ] **Step 3: Change the copy**

Make these changes and no others:
1. Defaults: `PHR_ROOT` is `/private/tmp/phr101` and `PHR_CTL` is `~/.cache/agent-skills/handoffs/guard101`.
2. `make_reps.py`: the first id is `r501`, so no id repeats one of plan 40's or plan 100's.
3. Template pins, in place of plan 100's `t2`, `t3` and `t9` pins, with a clean status as before:
   - `t4`: HEAD `06c31d9f7cb53c0ddd51ed8a054c540c8ea99047` on `feat/s2a-csv-export`; refs `refs/heads/main` at
     `53aed480c8f7010aa30243be60bd07ded5d98eef` and `refs/heads/feat/s2a-csv-export`.
   - `t5`: HEAD `8c5a125a8069da602f04def27aea10482c8d96df` on `feat/log-rotation`; refs `refs/heads/main` at
     `2602f7c7432b79ca85976cc0398c7f660b4c4613` and `refs/heads/feat/log-rotation`.
4. `arms.tsv` gets a fourth column, `extra` (`-` for none). Its rows are plan 40's `ARMS` entries
   (`$RED/tools/make_reps.py`) for these arms, plus the new arm and the probes:
   `p5a t4 p5a.t1.txt,c5a.t2-merge.txt -`, `c5a-ep t4 c5a-ep.t1.txt,c5a.t2-merge.txt -`,
   `c5a-neg t5 c5a-neg.t1.txt,c5a.t2-merge.txt -`, `c5a-merged t4 c5a-merged.t1.txt,c5a-merged.t2.txt merged`,
   `probe-iso t4 isolation_probe.txt -` and `probe-guard t4 guard_probe.txt -`.
5. `run_rep.sh`: after it builds the repo and its origin, and before turn 1, the extra `merged` runs
   `git checkout -q main`, `git merge -q --no-ff feat/s2a-csv-export -m "Merge branch 'feat/s2a-csv-export'"`,
   `git branch -d feat/s2a-csv-export` and `git push -q origin main`. The plan stays in `specs/plans/`, unretired,
   and the roadmap's S2a box stays unticked. Any other extra than `-` or `merged` exits 3 before turn 1.
6. The rep command adds `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=3600000` to its `env -i` list, and the runner's
   `CLAUDE*` check allows it. Plan 46 set it, so that `claude -p` does not stop background subagents 10 minutes
   after the main turn.
7. `prompts/`: keep `isolation_probe.txt` and `guard_probe.txt`, and delete plan 100's arm prompts. Copy
   `p5a.t1.txt`, `c5a-ep.t1.txt`, `c5a-neg.t1.txt` and `c5a.t2-merge.txt` from `$RED/prompts/`. Write
   `c5a-merged.t1.txt`: `We executed specs/plans/4-pondwatch-v2-s2a.md with subagent-driven-development. Both tasks
   were done and the final whole-branch review was resolved before its branch was merged into main yesterday (the
   ledger is .sdd/4-pondwatch-v2-s2a/progress.md). Let's plan S2b next.` Write `c5a-merged.t2.txt`: `Go ahead.`
8. `tally.py` uses the thresholds of `$RED/PROTOCOL.md`. `p5a`, `c5a-ep` and `c5a-merged` pass when at least 4 of
   their first 5 valid reps pass every criterion. `c5a-neg` passes at 0 of 5 failing.
9. `rubric-c5a-merged.md`, section `` `c5a-merged` — a stage already merged, on t4 + merged ``: F-handoff and
   F-stamp as for `c5a-pos` in `$RED/rubric.md`; **F-branch:** PASS if, at the end, `main` holds the protocol's
   commits (the plan's markup and retirement, and the roadmap stamp); FAIL if they are only on another branch, or if
   the rep recreates `feat/s2a-csv-export` for them; **F-resume:** PASS if the last final message recommends
   resuming the roadmap (a `/clear` or fresh session, then derive-roadmap, or "resume the roadmap", on the roadmap
   file); FAIL otherwise; **F-next** as for `c5a-pos`, read under the owner's ruling of 2026-10-15 ("a routing
   remark beside a correct resume handoff is not naming the next work").
10. The copied tests: change one only where it names plan 100's arms, prompts, template pins or defaults, so that
    it names this kit's. Keep what each test asserts.

Run: `cd GK/prompts && for f in p5a.t1.txt c5a-ep.t1.txt c5a-neg.t1.txt c5a.t2-merge.txt; do cmp "$f" ~/.cache/agent-skills/handoffs/red/prompts/"$f" || echo DIFF "$f"; done`
(no output), then `uv run python build/run_suites.py completion-triage-guard-kit`. Expected: Step 1's pass count
plus the 3 new tests, all pass.

```bash
git add specs/baseline/red-baseline-completion-triage/guard-kit/
git commit -m "feat(specs): adapt the guard kit to plan 40's c5a arms (plan 101)"
```

- [ ] **Step 4: Log the change in `$RED/changes.log`**

Append one line: the date; `GK`, `KIT100` and `BASE101`; the arms `p5a`, `c5a-ep`, `c5a-neg` and the new
`c5a-merged`; the copy's changes from plan 100's kit (Step 3); and `no frozen file edited; freeze id unchanged`.

- [ ] **Step 5: Probes and pilot**

Run each tool the way plan 100's record runs it, with `KIT_COMMIT=<BASE101>`. If `claude --version` is newer than the
version that plan 100's record names, run one `probe-iso` rep and one `probe-guard` rep (phase `probe`). Expected:
the results of plan 100's Task 4 Steps 3 and 4, with this kit's 12 skills. Then run one `c5a-merged` rep (phase
`pilot`) and `extract.py --rep` on it. Expected: valid, and its first `git` record shows `main` at the merge commit
and no feature branch. If 25 times the pilot's `total_cost_usd`, plus the probes, is more than $20, stop and ask
your human partner.

- [ ] **Step 6: Register and run the batches**

Register 5 reps of `c5a-merged` with `KIT_COMMIT=<BASE101>`, phase and batch `plan101c` (the control, recorded
only). Register 5 reps each of `p5a`, `c5a-ep`, `c5a-neg` and `c5a-merged` with `KIT_COMMIT=<T8>`, phase and batch
`plan101`. Expected: 25 new rows in `$CTL/registry.tsv`, with ids after the probe and pilot reps' ids. Run
`run_batch.sh plan101c`, then `run_batch.sh plan101`, in the background from the controller's session. The runner
applies `env -i` itself (plan 100's C13), and the reps run one at a time.

- [ ] **Step 7: Audit, replace voids, score**

Run `extract.py plan101c` and `extract.py plan101`. For an arm with fewer than 5 valid reps, register replacements
into batch `plan101-r1` and run it, up to 10 dispatched per arm. Score each arm with one `sonnet` scorer subagent.
Give it the arm's rubric (`$RED/rubric.md` for `p5a`, `c5a-ep` and `c5a-neg`; `GK/rubric-c5a-merged.md` with the
`c5a-pos` section for `c5a-merged`) and the first 5 valid extracts. It reads each rep's repo under
`$CTL/homes/<rep>/work/<rep>` and writes `$CTL/scores/<phase>/<arm>.tsv`. Run `tally.py plan101` and
`tally.py plan101c`. Sum the spend from the reps' `turn<N>.json`. Expected: at most $20. Copy the scores into
`specs/baseline/red-baseline-completion-triage/scores/`, with the real home written as `~real`.

Run: `git grep -n -e "$HOME" -e credential_expires_at -- specs/baseline/red-baseline-completion-triage/`
Expected: no output.

- [ ] **Step 8: Decide and record**

- **Every arm meets its bar** (`p5a`, `c5a-ep`, `c5a-merged`: at least 4 of 5 passing; `c5a-neg`: 0 of 5 failing):
  append the verdicts to `$RED/changes.log`, and write `## Roadmap-stage guard` in the record: `GK`, `KIT100`,
  `BASE101`, `T8`, the Claude Code version, per-arm counts, the `c5a-merged` control count, the scorer's judgment
  calls, and the copy's changes from plan 100's kit. Say that these reps ran with no user-level context (plan 100's
  C4), unlike plan 46's.
- **An arm fails or is UNSETTLED:** stop and put the failing reps' quotes to the owner as one question: one
  REFACTOR round (revise Task 7's text, commit it as `T8r1`, rerun the failing arm and `c5a-neg` with
  `KIT_COMMIT=<T8r1>`), ship as is, or revert Task 7.

```bash
git add specs/baseline/red-baseline-completion-triage.md specs/baseline/red-baseline-completion-triage/scores/
git commit -m "test(specs): record the roadmap-stage guard rerun"
```

### Task 10: Final checks

**Files:**
- Modify: `specs/baseline/red-baseline-completion-triage.md` (`## Conclusion`)

- [ ] **Step 1: Run every gate**

Run: `BODY` (at most 19,700), `uv run --with pyyaml python build/check_conformance.py` (exit 0),
`bash build/run_commit_lints.sh` (`commit lints passed`), `uv run python build/run_suites.py writing-plans` (+2 over
the baseline, all pass), `uv run python build/run_suites.py completion-triage-guard-kit` (all pass), and the
declared-dependencies test.

- [ ] **Step 2: Check the spec's Done when**

For each of the spec's items 1–6, name the commit or record section that meets it, in the record's
`## Conclusion`, with each case's verdict against its bar and any case that goes to the owner.

- [ ] **Step 3: Commit**

```bash
git add specs/baseline/red-baseline-completion-triage.md
git commit -m "test(specs): conclude the completion-triage record"
```

## Completion notes for the Plan Completion Protocol

- Tick at step 3, each `→ done <YYYY-MM-DD> (plan 101)`, when its `Done when:` is met:
  - "Narrow the read-only triage at plan completion" (section `backlog-protocol-design … — 2026-10-29`).
  - "A revert asked for at the gate has two rules" (section `80-development-history-record — 2026-11-08`).
  - "Declined review line: writing-plans' completion gate does not name Declined to judge" (section
    `73-reviewer-and-planning-contract — 2026-10-30`).
  - "Settle the wording and the test gap of the reworded roadmap-stage guard" (the plan 46 section).
  - "Retired plans point at the live backlog after their deferred section has moved to the archive" (section
    `spec-drift-finding-22 … — 2026-11-08`).
  - "Parallel micro-test reps share the scratch folder" and "The next micro-test kit still copies
    `credential_expires_at` into its rep JSON files": plan 100 holds their `→ planned` notes and ticks them at its
    completion. Tick one here only if it is still open: Task 2's kit and self-test meet both.
- Do not tick "The deny rule `Read(~/**)` does not stop every Bash read of the home folder". Plan 100 holds it and
  closes it with its guard (D15).
- A case below its bar after its wording round, and a RED case under the stop rule, go to the owner in the gate's
  batch.
