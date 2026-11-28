# SDD and Reviewer Text Follow-ups Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring `skills/subagent-driven-development/SKILL.md` back inside the compaction window and retire the last compaction waiver with its guard. Settle the guide conflicts on the SDD files, and close the open reviewer-text items, each with a micro-test.

**Architecture:** Two streams, each a kit, a control round, one wording change and one treatment round. The SDD stream (Tasks 1 to 3) moves two duplicated passages out of the body into the references the controller already must read. It corrects them on the way, then retires the waiver, the guard and the stale lines in one commit. The reviewer stream (Tasks 4 to 6) runs control cases first and changes reviewer text only where a control fails. Task 7 writes the record and the closure notes.

**Tech Stack:** Markdown skill and agent text, Python 3.13 (dev, `build/versions.toml`) for the kits and lints, bash, `claude -p` (CLI version recorded at the first rep).

**Spec:** none. The requirements are thirteen `specs/deferred_items.md` items, read at `8131b81`. They are numbered [1] to [13] in this plan, by heading text and section:

- [1] "`skills/subagent-driven-development/SKILL.md` is 226 characters over the corrected compaction window", section `87-compaction-cut-probe — 2026-11-11`. Re-measured at `8131b81`: body 19,914 characters, window 19,700, 214 over.
- [2] "`skills/subagent-driven-development/SKILL.md` has six lines that contradict the guide", section `claude/bold-solomon-31bcfc cc-guide upkeep after 2.1.323 — 2026-11-12`, with the 2026-11-17 owner ruling that adds `:201` and `:232`.
- [3] "Correct the rework-cost claim in `skills/subagent-driven-development/references/model-selection.md` line 13", section `cc-guide-files-pass-e3 …`.
- [4] "skills/subagent-driven-development/SKILL.md does not say what review-package's exit 3 means", section `50-superpowers-upstream-fixes — 2026-10-18`.
- [5] "Test-only findings and the reviewer block's delete pass", section `73-reviewer-and-planning-contract — 2026-10-30`.
- [6] "Declined review line: the code-reviewer agent and template never say what a Review Focus section is for", same section.
- [7] "Declined review line: `skills/requesting-code-review/code-reviewer.md`'s "What to Check"", same section.
- [8] "Declined review line: the task reviewer's Full Form … was never micro-tested", same section, triggered 2026-11-14.
- [9] "Declined review line: `agents/security-auditor.md` keeps its Minor tier", same section.
- [10] "Wording observations from plan 73's tests", same section.
- [11] "The revert has no evidence for a test in a second suite that one pytest call cannot run", section `97-change-reverted-mutant — 2026-11-14`.
- [12] "The reviewer text supports two readings of "stated rule"", same section, with the 2026-11-17 owner ruling.
- [13] "A reviewer raises a finding about a screen file", section `104-mutant-screen-runs — 2026-11-22`.

This plan carries [1] to [8] and [12]. It leaves [9], [10], [11] and [13] open, by D7 to D10, which plan review settles.

## Global Constraints

- **Files this plan may touch:** `skills/subagent-driven-development/SKILL.md`, its `references/model-selection.md`, `references/fix-loop.md`, `references/file-handoffs.md` and `task-reviewer-prompt.md`. Also `agents/code-reviewer.md`, `agents/task-reviewer.md`, `skills/requesting-code-review/code-reviewer.md`, the `runtimes/` files that `sync_runtime_assets.py` regenerates, and `NOTICE`. Also `build/cc_guide/conformance.toml`, `build/cc_guide/baseline.json` (through `cli.py baseline cite` only), `build/run_commit_lints.sh`, `build/test_check_conformance.py`, `build/test_commit_lints.py`, `CLAUDE.md` and `build/CLAUDE.md`. Also `specs/baseline/red-baseline-sdd-text-followups*`, this plan, and append-only notes in `specs/deferred_items.md` and `specs/history.md`.
- **Never touch** (a concurrent plan owns them): `skills/subagent-driven-development/references/final-review.md`, `references/resuming.md`, `skills/executing-plans/` (its `scripts/task-start`, `scripts/task-done` and `references/final-review.md` included), and `SKILL.md` lines 210 to 221 (`## Plan Completion`'s roadmap paragraph). Leave `SKILL.md:172-175` (deviation `review-sonnet-floor`) as it is.
- **Body limit:** `check_conformance.skill_body(SKILL.md)` returns at most **19,500** characters after every commit that touches `SKILL.md`. That leaves 200 characters under the 19,700 window.
- **The shared reviewer block** runs from `## Review scope` to the end of `## Declined to judge`. It stays identical in `agents/code-reviewer.md`, `agents/task-reviewer.md`, `skills/requesting-code-review/code-reviewer.md` and `skills/subagent-driven-development/task-reviewer-prompt.md`, once template indentation is removed (`uv run python build/check_reviewer_block.py`). A change to it lands in all four copies in one commit.
- **After any change under `agents/`:** `uv run --with pyyaml python build/sync_runtime_assets.py`, then the same command with `--check`. Never hand-edit `runtimes/`.
- **Provenance:** SDD, requesting-code-review, `agents/code-reviewer.md` and `agents/task-reviewer.md` are adapted from superpowers. Read `NOTICE` before editing it. Each substantive change to those files gets one `NOTICE` bullet, under the existing superpowers modification list. `agents/security-auditor.md` is an original, so it needs no bullet.
- **Two kinds of micro-test.** A *behaviour change* lands only when its control (the text at `8131b81`) fails the case's bar and its treatment passes. When the control passes, the text stays unchanged and the record says "tested and unchanged". A *correction or move* is a non-regression test: the treatment meets the same bar as the control, on the case that the moved or corrected text governs.
- **Micro-test discipline:** writing-skills' "Micro-Test Wording Before Full Scenarios" and `skills/writing-skills/references/micro-tests.md`. Bars, reading rules and VOID rules are committed before any rep of that round is read. 5 reps per arm per model. A bar is met at 4 of 5 scored reps unless the case's row says otherwise. Sheets are blind to the arm (memory `microtest-sheet-arm-tell`: no sheet line may differ by arm).
- **Models:** a case ported from a record runs on the models that record used. A new case runs on `claude-opus-5-5` and `claude-sonnet-5-5`. Default effort.
- **Kit isolation (D3):** every rep runs with `env -i`, its own `HOME` and `TMPDIR`, `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, from a new empty directory outside every repository. No kept rep file holds `credential_expires_at`, `session_id`, `uuid` or `origin`. A rep with `result_index` > 0 or a non-null `origin` is VOID. An isolation probe runs before the first scored rep of each kit. No rep can reach this repository, the plan, the kits or the records.
- **Spend cap:** $120 for all reps of the plan, as the running sum of `total_cost_usd`. Stop and ask the owner when the running total plus the next batch's worst case passes the cap, or when one rep costs more than $3.
- **Commit lints** pass before every commit: `bash build/run_commit_lints.sh`.
- **Guide stamp:** `build/cc_guide/baseline.json` changes only through `uv run python build/cc_guide/cli.py baseline cite <file>`. `model-selection.md` carries no citation line, so it is never cited itself. The `SKILL.md` verify covers it.

## Review Focus

1. A controller that never reads `references/model-selection.md` before its first dispatch now misses what an omitted model does. The body keeps the "always specify the model" rule and its pointer (Task 2, case M1).
2. A controller at round 5 under a plan whose `fable` bills to usage credits that the partner has not approved. It must not dispatch `fable`, and it must not stop the run to ask (Task 2, case C1b).
3. A retired guard leaves its name behind in one site, and the runner, the hook or CI fails on a clean tree (Task 3, `test_commit_lints.py` after the commit).
4. A reviewer-text change that lands in fewer than four copies, or in an `agents/` file whose `runtimes/` copy is not regenerated (Task 5, `check_reviewer_block.py` and `--check`).
5. A wording change that fixes its own case but drops a bar that an earlier record met. Every barred case that reads a changed file runs again (Tasks 2 and 6).

## Decisions

- **D1** (owner, brief, 2026-11-28): "Provide briefs for P6 and P7 as well.", then "Include as many items as possible in each." One plan takes the SDD text batch ([1], [2], [3], [8]) and the open items on the same files. An item that needs the owner's design call goes to plan review as a question. Applied in: all tasks; D7 to D10.
- **D2** (planner, for plan review, 2026-11-28): [1] frees room by moving two passages out of the body into references that the body already makes the controller read. The omitted-model mechanics (`SKILL.md:165-170`) go to `references/model-selection.md`. The round-5 rung (`SKILL.md:199-201`) is already in `references/fix-loop.md:28-36`, so the body copy is deleted. The two passages hold about 840 characters. After the pointer sentence and the exit 3 words, the expected body is about 19,350 characters. Each move also carries a [2] correction (D4). Applied in: Task 2.
- **D3** (planner, for plan review, 2026-11-28): the plan 71 kit (`specs/baseline/red-baseline-sdd-compaction/kit/`) and the plan 73 and 97 reviewer kits predate the next-kit isolation fixes. Default: copy each kit into `specs/baseline/red-baseline-sdd-text-followups/`, keep each ported case's text byte-identical, and add the fixes in Global Constraints. The old kits stay frozen. Alternative: reuse them in place, which saves Task 1 and Task 4 setup but leaves the old isolation gaps. Applied in: Tasks 1 and 4.
- **D4** (planner, for plan review, 2026-11-28): [2]'s eight lines, one choice each.
  - `:43`, `:53`, `:232` (reviewer scope): **deviation** `sdd-reviewer-scope-in-shared-block`, with no text change. The shared block already says "Report only correctness and requirement gaps", which is the guide's instruction. These three lines bar the controller from suppressing a named finding, which is a different act. `:232` is consistent under its narrow reading, and the deviation records that reading.
  - `:73` (every behaviour fix goes to a fix subagent): **deviation** `sdd-fix-subagent-for-behaviour-change`. A behaviour change needs a test cycle and the implementer's context, and the existing exception already lets the controller make no-behaviour single-file fixes by hand.
  - `:166`, `:167` (omitted model): **correct**, inside the D2 move. The new text names the per-spawn model, the agent pin, `CLAUDE_CODE_SUBAGENT_MODEL` and `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` in the guide's order (`subagents.frontmatter`, guide line 188, and line 226).
  - `:199` (round 5 at `fable`): **correct**, in `fix-loop.md`. Add a billing check: where `fable` bills to usage credits that the partner has not approved this session, treat it as not offered. Do not stop to ask. The controller continues at effort.
  - `:201` (effort as the last rung): **no change, no deviation.** The full rung in `fix-loop.md:30` already runs context, then effort, then model, which is `lean.model-routing`'s order. The body's short copy goes with D2, so the files verify reads only the full one.
  Applied in: Tasks 2 and 3.
- **D5** (planner, for plan review, 2026-11-28): [4]'s instruction goes into `references/file-handoffs.md`'s review-package bullet, with no added body text beyond a few words in the DONE line. It is a behaviour change, so it lands only if case X3's control fails. Applied in: Tasks 1 and 2.
- **D6** (planner, for plan review, 2026-11-28): [5], [6] and [7] are behaviour changes. Each gets a control case first, and its text changes only when that control fails. [12] is ruled (owner, 2026-11-17), so its sentence lands and is tested against plan 97's barred packages. [8] is a Full Form arm on the final reviewer text, which closes the item when the arm meets the Short Form arm's bars. Applied in: Tasks 4 to 6.
- **D7** (planner, for plan review, 2026-11-28): leave [9] open. No skill or command dispatches `security-auditor`, so its revisit signal cannot fire, and a change now has no case to test it. Alternative: `→ dropped:` with that reason.
- **D8** (planner, for plan review, 2026-11-28): leave [10] out. Its open remainder is writing-plans text (`skills/writing-plans/SKILL.md:80`, `:119`) and plan 73 kit observations, outside this plan's files.
- **D9** (planner, for plan review, 2026-11-28): leave [11] out, and recommend a spec. Its fix touches `skills/executing-plans/scripts/task-done`, which the concurrent plan edits, as well as `mutants.md`, check 7 and micro-tested texts.
- **D10** (planner, for plan review, 2026-11-28): leave [13] open. Reviewers never receive a screen file, so no realistic control can fail, and its revisit signal has not fired.
- **D11** (owner, plan review, 2026-11-28): "Approve as written". D2 to D10 stand as written. Applied in: all tasks.

---

### Task 1: SDD kit and control round

**Files:**
- Create: `specs/baseline/red-baseline-sdd-text-followups/sdd-kit/` (ported from `specs/baseline/red-baseline-sdd-compaction/kit/`)
- Create: `specs/baseline/red-baseline-sdd-text-followups.md` (the record; `## SDD bars` and `## SDD control` sections)
- Modify: `build/suites.toml`, only if the kit carries tests (`run_suites.py --check` says so)

**Interfaces:**
- Produces: `sdd-kit/build_prompts.py <arm> <source> <out-dir> [case ...]`, where `<source>` is a full SHA or the literal `WORKTREE`. Each prompt holds the body of `SKILL.md` from that source. For a case whose row names reference files, each reference is shown as a file the controller has already read, from the same source. `sdd-kit/run_reps.sh <prompt> <out-dir> <first> <last> <model>`.

- [ ] **Step 1: Port the kit** with the isolation fixes in Global Constraints and the `<source>` and `<model>` arguments. Keep C1's case text byte-identical to `cases.py` at `8131b81`.
- [ ] **Step 2: Add the cases and register the bars** in the record before any rep runs:

| Case | Governs | Scene | Pass rule for one rep | Bar |
|---|---|---|---|---|
| M1 | [2] `:166-167`, [3], D2 move | Three task briefs: complete code in one file; prose behaviour in two files; a cache race. The ledger shows `CLAUDE_CODE_SUBAGENT_MODEL=haiku` is set | Each dispatch names a model, at cheap, standard and capable in that order | non-regression: treatment meets the bar whenever the control does, both models |
| C1 | D2 move | Plan 71's C1, unchanged; `fix-loop.md` shown as read | Round 5 is dispatched fresh at `fable`, and no round 6 starts | non-regression, as above |
| C1b | [2] `:199` | C1, plus a session note: `fable` bills to usage credits here, and the partner has not approved that | No dispatch at `fable`; round 5 runs fresh at `opus` with higher effort, or the task goes to adjudication; no ACTION asks the partner and waits | behaviour: the change lands only if the control fails (3 or fewer of 5 on either model) |
| X3 | [4] | An implementer reports DONE; `review-package` prints `empty commit range: <B>..<H>` and exits 3 | No reviewer dispatch for the task; no re-run of the same range; the task goes back to the implementer as a fix round naming the script's message, or the controller first checks the implementer's branch with `git log` | behaviour, as C1b |

- [ ] **Step 3: Run the isolation probe**, then the control arm at `8131b81` for M1, C1, C1b and X3 on both models.
- [ ] **Step 4: Read and score** the control reps by the registered rules. Write `## SDD control` with one row per rep and the running spend.
- [ ] **Step 5: Commit** the kit, prompts, kept reps and record.

```bash
git add specs/baseline/red-baseline-sdd-text-followups specs/baseline/red-baseline-sdd-text-followups.md
git commit -m "test(sdd): micro-test kit and control round for plan 120"
```

### Task 2: SDD text, waiver retirement and deviations

One commit, because `check_conformance.py` reports a `stale-waiver` finding once the body fits, and the guard test fails once the last waiver goes (`build/test_check_conformance.py:1205`).

**Files:**
- Modify: `skills/subagent-driven-development/SKILL.md:163-170` (Model Selection), `:181` (DONE), `:195-201` (Fix Rounds)
- Modify: `skills/subagent-driven-development/references/model-selection.md:11-17` and a new section
- Modify: `skills/subagent-driven-development/references/fix-loop.md:28-36`
- Modify: `skills/subagent-driven-development/references/file-handoffs.md:49-60`, only if X3's control failed
- Modify: `NOTICE`
- Modify: `build/cc_guide/conformance.toml:799-811` (remove), and add two deviations (D4)
- Modify: `build/run_commit_lints.sh:33`, `build/test_check_conformance.py:1190-1207`, `build/test_commit_lints.py:34`, `CLAUDE.md:76-81` and `:129-130`, `build/CLAUDE.md:55-61`

**Interfaces:**
- Consumes: Task 1's kit, with `<source>` = `WORKTREE`.

- [ ] **Step 1: Model Selection.** In `SKILL.md`, keep the bold "Always specify the model explicitly when dispatching" sentence and the alias clause. Replace the rest of `:165-170` with one sentence that points to `references/model-selection.md` for what an omitted model runs. Move that text to a new `## What an omitted model runs` section in `model-selection.md`, with the hook line, corrected in the guide's resolution order. The order is: the dispatch's `model`, then the agent's `model` pin, then `CLAUDE_CODE_SUBAGENT_MODEL`, then your session's model. `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` applies the variable over pins and dispatch models alike, so a tier choice has no effect while it is set.
- [ ] **Step 2: Line 13 ([3]).** Replace `model-selection.md:13-14` so that it says rework costs time and review effort, and that the cheap tier is cheaper per token by a wide margin. Then the two defaults guard against rework, not price. Drop "turn count and rework dominate sticker price".
- [ ] **Step 3: Fix Rounds.** Delete the round-5 sentences (`SKILL.md:199-201`). The bolded instruction to re-read `fix-loop.md` before every round stays. In `fix-loop.md`, after "dispatch round 5 at `fable`.", add the D4 billing check in one sentence.
- [ ] **Step 4: Exit 3 ([4]), only if X3's control failed.** Add to `file-handoffs.md`'s review-package bullet: exit 3 (`empty commit range` or `HEAD is not a descendant of BASE`) means the task's commits are not on BASE..HEAD. Do not dispatch the reviewer. Send the task back to the implementer as a fix round with the script's message. In `SKILL.md`'s DONE line, extend "for the path the script reports" to name exit 3 too.
- [ ] **Step 5: Measure.**

Run: `cd build && uv run --with pyyaml python -c "import check_conformance as c, pathlib; print(len(c.skill_body(pathlib.Path('../skills/subagent-driven-development/SKILL.md').read_text())[0]))"`
Expected: a number ≤ 19500.

- [ ] **Step 6: Treatment arm** at `WORKTREE` for M1 and C1 on both models, for C1b if its control failed, and for X3 if its control failed. Score by the registered rules into `## SDD treatment`. If a bar is missed, stop and ask the owner before the commit.
- [ ] **Step 7: Retire the waiver and its guard.** Delete the exception and its comment (`conformance.toml:799-811`). Delete the `compaction_waiver_guard` line from `run_commit_lints.sh`. Delete `late_heading_findings` and `test_waived_compaction_window_files_hide_no_late_heading`, and drop the name from `CHECKS` in `test_commit_lints.py`. In `CLAUDE.md`, delete the guard's two lines in Commands. Rewrite the lint-list sentence so that it ends "…the deferral lint (deferral_scan.py lint, below) and the helper-path check (check_helper_paths.py, below)." Delete the `compaction_waiver_guard` paragraph in `build/CLAUDE.md`.
- [ ] **Step 8: Add D4's two deviations** to `conformance.toml` in the `review-sonnet-floor` form (`id`, `type = 'deviation'`, `sections`, `artifacts`, `guide`, `reason`, `evidence`, `revisit`). `sdd-reviewer-scope-in-shared-block`: sections `['subagents.isolation']`, artifacts `SKILL.md`, guide text from guide line 235's reviewer sentence, and evidence this plan's D4 and the shared block. `sdd-fix-subagent-for-behaviour-change`: the same section and artifact, with guide text from line 235's "trivial single-file edits".
- [ ] **Step 9: Add the `NOTICE` bullet**, naming the moves, the corrections and, if it landed, the exit 3 line.
- [ ] **Step 10: Verify.**

Run: `uv run --with pyyaml python build/check_conformance.py && git grep -n "compaction_waiver_guard\|late_heading_findings\|waived_compaction" -- ':!specs'`
Expected: the conformance check exits 0, and the grep prints nothing.

- [ ] **Step 11: Commit**, then run the commit-lint tests (they clone HEAD, so they run after the commit).

```bash
git add skills/subagent-driven-development NOTICE build CLAUDE.md specs/baseline/red-baseline-sdd-text-followups.md specs/baseline/red-baseline-sdd-text-followups
git commit -m "fix(sdd): fit the compaction window, correct model and fable text, retire the last waiver"
cd build && uv run --with pytest --with pyyaml python -m pytest -q test_commit_lints.py test_check_conformance.py
```

Expected: all pass.

### Task 3: Guide verify and stamp for SDD

**Files:**
- Modify: `build/cc_guide/baseline.json` (through `cli.py` only), `skills/subagent-driven-development/SKILL.md:14` (the stamp line `cite` rewrites)

- [ ] **Step 1: Run `/cc-guide files skills/subagent-driven-development/SKILL.md`**, a fresh verify that reads the covered references, `model-selection.md` and `fix-loop.md` included.
- [ ] **Step 2: Settle each finding.** One that names a line this plan changed is fixed in a new commit and verified again. One that names any other line goes to the owner as a question. Stop for that answer before Step 3.
- [ ] **Step 3: Stamp.**

Run: `uv run python build/cc_guide/cli.py baseline cite skills/subagent-driven-development/SKILL.md && uv run python build/cc_guide/cli.py lint`
Expected: both exit 0.

- [ ] **Step 4: Commit** `chore(cc-guide): cite subagent-driven-development after plan 120`.

### Task 4: Reviewer kit and control round

**Files:**
- Create: `specs/baseline/red-baseline-sdd-text-followups/review-kit/` (ported from `specs/baseline/red-baseline-reviewer-planning-contract/kit/` and `specs/baseline/red-baseline-change-reverted-mutant/review-kit/`)
- Modify: `specs/baseline/red-baseline-sdd-text-followups.md` (`## Reviewer bars`, `## Reviewer control`)

**Interfaces:**
- Produces: `review-kit/build_prompts.py <arm> <source> <out-dir> [case ...]`, where `<source>` is a full SHA or `WORKTREE`. The arms are `short` (the task-reviewer Short Form plus the agent body, as plan 73's kit does), `full` (the Full Form in `task-reviewer-prompt.md`), and `final` (the code-reviewer agent plus `skills/requesting-code-review/code-reviewer.md`).

- [ ] **Step 1: Port both kits** with the isolation fixes. Keep every ported case and package byte-identical.
- [ ] **Step 2: Add the new cases and register every bar** before any rep runs:

| Case | Governs | Arms | Scene | Pass rule for one rep | Bar |
|---|---|---|---|---|---|
| T1-task, T1-final | [5] | `short`, `final` | A task diff whose one new test calls the function and asserts nothing | The test is reported as Important | behaviour: [5]'s rewording lands only if either control scores 3 or fewer of 5 on either model |
| F1-final | [6] | `final` | The plan's `## Review Focus` names an input (an empty file), no test covers it, and the code raises on it | An Important finding names the empty-file failure | behaviour, as T1 |
| D1-final | [7] | `final` | A correct diff that chooses one module where two would read better, with no requirement either way | No finding, Declined line or remark on the module choice | behaviour: [7]'s trim lands only if the control fails in 2 or more of 5 on either model |
| R4, R5, R6 | [12] | `short` | Plan 97's packages, unchanged | Plan 97's reviewer bars, plus, for R4, no finding that asks for a row or a mutant for the start-date rule | [12] lands (ruled); treatment meets plan 97's bars and the R4 start-date clause at 4 of 5 |

- [ ] **Step 3: Run the isolation probe**, then the control arm at `8131b81` for T1-task, T1-final, F1-final and D1-final on both models. R4 to R6 need no new control: plan 97's record is the control (start-date finding in 4 of 5).
- [ ] **Step 4: Score** into `## Reviewer control`, then **commit** `test(review): reviewer kit and control round for plan 120`.

### Task 5: Reviewer text

**Files:**
- Modify: `agents/task-reviewer.md:21-23` and the matching Full Form lines in `skills/subagent-driven-development/task-reviewer-prompt.md` ([12])
- Modify: the shared block's delete-pass sentence in all four copies (`agents/code-reviewer.md:56-58` and its three twins), only if a T1 control failed ([5])
- Modify: `agents/code-reviewer.md` and `skills/requesting-code-review/code-reviewer.md`, **outside** the shared block, only if F1's control failed ([6])
- Modify: `skills/requesting-code-review/code-reviewer.md:70-96` and both preambles (`agents/code-reviewer.md:11-13`, `skills/requesting-code-review/code-reviewer.md:19-21`), only if D1's control failed ([7])
- Modify: `runtimes/` (regenerated), `NOTICE`

- [ ] **Step 1: [12].** After "The global constraints quoted in the dispatch bind the task.", add one sentence in both files: they are not stated rules for the mutant step, and stated rules come only from the spec excerpts and the brief.
- [ ] **Step 2: [5], if its control failed.** Reword the delete-pass sentence so that it keeps every finding that the Grades section names, tests that assert nothing included, and deletes only points that no person would notice or act on. Make the same edit in all four copies.
- [ ] **Step 3: [6], if its control failed.** Add one sentence outside the shared block, in `## Calibration` of both files: a `## Review Focus` section in the requirements names inputs that no task's tests exercise, so check the code against each line.
- [ ] **Step 4: [7], if its control failed.** Delete "Sound design decisions?", "Integrates cleanly with surrounding code?" and "Type safety where applicable?". Change both preambles to drop the architecture and design-pattern expertise claim.
- [ ] **Step 5: Regenerate and check.**

Run: `uv run --with pyyaml python build/sync_runtime_assets.py && uv run --with pyyaml python build/sync_runtime_assets.py --check && uv run python build/check_reviewer_block.py`
Expected: all exit 0.

- [ ] **Step 6: Add one `NOTICE` bullet** for the changes that landed, then **commit** `fix(review): stated-rule source and plan 120 reviewer text`.

### Task 6: Reviewer treatment round and the Full Form arm

**Files:**
- Modify: `specs/baseline/red-baseline-sdd-text-followups.md` (`## Reviewer treatment`, `## Full Form arm`)

- [ ] **Step 1: Treatment arm** at Task 5's commit. Run R4, R5 and R6 (`short`), each changed case's own case, and every plan 73 case that carries a bar and reads a file that Task 5 changed. The plan 73 cases come from `specs/baseline/red-baseline-reviewer-planning-contract.md` § The seven bars, with that record's models.
- [ ] **Step 2: Full Form arm ([8]).** Run the `full` arm at Task 5's commit on R1-task, R2-task and R4-task (plan 73) and T1-task. The bar is the one each case's `short` arm meets.
- [ ] **Step 3: Score.** If a bar falls, stop and ask the owner before any further wording change. A further round re-runs every case this task ran.
- [ ] **Step 4: Commit** `test(review): treatment and Full Form rounds for plan 120`.

### Task 7: Record and item notes

**Files:**
- Modify: `specs/baseline/red-baseline-sdd-text-followups.md` (summary table at the top: case, arm, model, score, bar, verdict; total spend; CLI version; limits)
- Modify: `specs/deferred_items.md` (progress notes only; the ticks come at the completion protocol)

- [ ] **Step 1: Write the summary.** Name each item that is "tested and unchanged", with the control scores that kept it so.
- [ ] **Step 2: Add a `→ progress <date> (plan 120): …` note** under each item that is tested and unchanged ([4], [5], [6] or [7]). The note names the case and its control score, and asks the owner at the completion gate whether to tick it.
- [ ] **Step 3: Run the commit lints and commit** `docs(specs): plan 120 micro-test record`.
