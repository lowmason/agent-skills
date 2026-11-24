# writing-skills Guard Run for Edits That Keep Behavior Implementation Plan

> ⚠️ Quarantine this file during any micro-test of writing-skills, as the spec says of itself. Task 1
> names the cases and what each one scores, so a rep that reads this file is void.

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship step 4 of the spec's Proposed sequence: item 9, which names a guard run as the test for an edit meant to keep behavior, pressure-tested on Opus and Sonnet, with the register change it brings (Q4). Also carry the deferred step 1 subagent-fallback fix, RED first.

**Architecture:** Five tasks on one branch, in order. Task 1 copies plan 107's case kit, swaps in three new cases and a no-loss bar, and commits the rules. It spends nothing. Task 2 runs the probes and pilots and projects the spend. Task 3 runs item 9's cycle: a RED run of case G1, the text, then a GREEN run of G1 and a no-loss run of case L2, graded blind with both arms mixed. Task 4 runs the same cycle for the step 1 fix (case F3). Task 5 changes the register's `reason` line and writes the `NOTICE` bullet.

**Tech Stack:** Markdown skill text; plan 107's `claude -p` case kit (bash 3.2 and Python 3.11+, stdlib), copied; pytest through `build/run_suites.py`; TOML (the register).

**Spec:** `specs/writing-skills-improvements.md`, approved for planning on 2026-11-22, with the owner rulings in its Owner decisions section (Q4 for this plan). This plan covers Proposed sequence step 4: item 9. It also carries one backlog item, "Fix the subagent fallback in `SKILL.md` micro-test step 1" (`specs/deferred_items.md`, section `107-writing-skills-improvements`).

## Global Constraints

- **Base.** `main` at `6b5eddf` (the merge of PR #259). Before Task 1, run `git diff 6b5eddf HEAD -- skills/writing-skills build/cc_guide/conformance.toml NOTICE`. If it prints anything, stop and ask. Line numbers below were taken at `6b5eddf`. The old text in each step is the match key.
- **Execution order.** This plan is a domain stream. Start it only while fewer than 3 domain executions run and none shares its files (check `list_sessions`).
- **One owner per file.** `SKILL.md` changes in Tasks 3 and 4 only. `build/cc_guide/conformance.toml` and `NOTICE` change in Task 5 only. `build/suites.toml` gains one entry, in Task 1.
- **Clean arms.** Each item's `old` and `new` arms differ by that item's text only. Task 4 starts after Task 3's last commit, never between Task 3's RED and GREEN runs.
- **Body ceiling.** The `SKILL.md` body is 19,258 characters at `6b5eddf`, measured as `len(check_conformance.skill_body(text)[0])` (`uv run --with pyyaml python`, with `build/` on `sys.path`). The exact text in this plan measures 19,469 (Task 3: +215 → 19,473; Task 4: −4 → 19,469). The ceiling is 19,620, which keeps about 40 characters for item 13 and about 40 spare inside the 19,700 window. If an edit would pass 19,620, stop and ask.
- **RED first.** Tasks 3 and 4 each run and grade their RED arm before any of their skill text is written (writing-skills' Iron Law). Each item can drop alone. L2 checks item 9's text for a loss. It is not a RED-first case.
- **Live skill.** `CLAUDE.md` sends every agent that edits a skill to writing-skills, and `~/.claude/skills` links to the main checkout. Execute from a worktree, so agents keep reading main's writing-skills until the merge.
- **Bare names.** New skill text names no other skill, so `install.py`'s `DEPENDENCIES` and `SOFT_REFERENCES` do not change.
- **Claude Code facts.** New skill text states none, and the citation line does not change, so no `/cc-guide files` verify is planned. If `uv run python build/cc_guide/cli.py lint` prints a line for writing-skills, stop and ask.
- **Commit gate.** Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Messages follow Conventional Commits, use plain technical English and end with the attribution trailer that the executing session is given. State test counts as deltas.
- **Mutant step.** Task 1 runs the mutant step on `audit.py` and `sheets.py`. Tasks 2 to 5 record `--no-mutants` with the reason "Markdown, TOML, records and kit runs only; no code".
- **Micro-tests.** Models `claude-opus-5-5` and `claude-sonnet-5-5`, 5 reps per arm per model. Nobody messages or subscribes to a running rep. The spec, this plan, and the records and kits of plans 105 and 107 stay out of every rep's reach: reps deny `Read(//Users/**)`, run from `/private/tmp/wst108`, and read a skill copy that `git archive` places at `/private/tmp/wst108-skill`. `place-copy` refuses a non-empty root, so empty the skill copy before each placement. Raw output goes to `~/.cache/agent-skills/scratch/plan108/`, never into the repository. Committed copies are scrubbed, and `privacy_sweep.py` passes on them before their commit.
- **Grading.** Grader agents on Opus grade the sheets, one agent per case, with no key, as in plan 107. A sheet never shows the arm. `sheets.py build` reads every case folder under its runs root, and `unblind` refuses a missing grade. So each grading builds from a scratch runs root that holds copies of only the graded case's arm folders, into a new sheet folder.
- **Spend.** The cap for every probe, pilot and rep in this plan is $25. Per-rep `--max-budget-usd` is $1.50. Task 2 projects the total, and a projection above $21 stops the run before any scored rep. Before each batch (5 reps of one case, arm and model), check: running total + 5 × $1.50 ≤ $25. A batch that fails the check stops the run: report BLOCKED with the spend table. Expected spend is about $12 to $15. Plan 107's case reps cost about $0.08 each on Sonnet and $0.20 on Opus.
- **Retries.** The owner's retry limit (Open for plan review item 8) applies to each item. The executor changes no wording without the owner.
- **Codex (D1).** `~/.cache/agent-skills/scratch/plan105/`, `plan107/` and `plan108/` hold unscrubbed rep output, and Codex's read-only sandbox can read them. Ask the owner before any Codex seat (the final review, or finishing's Step 4b), and delete none of these folders without asking.
- **Public repository.** The plan, kit, record and commits carry no private detail. Records cite committed files only.
- **Leave alone.** Item 13 (its own backlog plan) and item 16 (held under Q6). The "Trigger-eval suites" item (section `53-agent-skills-portability`). Plan 107's other open items: item 10, item 3b, item 2's Sonnet gap, the trigger-rep VOID rule and the `discovery.md` § 6 runs-per-prompt gap. Every committed kit under `specs/baseline/`. The scratch folders.
- **Completion.** As the owner rules on Open for plan review item 14.

## Review Focus

1. **An edit that changes an instruction, presented as a wording fix.** Expected: a RED-first test (the old text shows the failure and the new text fixes it), not a check that only requires no drop. Pinned by case L2 and its no-loss bar (Task 1 Steps 2 and 3; Task 3 Step 4).
2. **A G1 rep that runs only the new text, or compares it with results recorded before the change.** Expected: FAIL on G1 part (b). Pinned in G1's PASS part (b) (Task 1 Step 3).
3. **A G1 rep whose test needs the old text to fail first.** A relocation has no failure to watch, so the control is null by design. Expected: FAIL on G1 part (c). Pinned in G1's PASS part (c).
4. **A GREEN answer that says "guard run".** The words exist only in the `new` arm, so the sheet shows the arm. Expected: the sheet keeps the words, and the record counts those sheets as a limit of blind scoring, as plan 107's record did for `micro-tests.md`. Pinned in Task 1 Step 4 (the record's Blind grading section) and Task 3 Step 4.
5. **A rep whose Read, Glob or Grep reaches the real repository** (the spec, this plan, or plan 107's record or kit). Expected: VOID. Pinned by the path-audit tests that Task 1 copies, the three closed Glob limits among them.

## Decisions

- **D1** (owner, brief, 2026-11-24): ask the owner before any Codex seat, and delete no scratch folder without asking, as plan 107's D3 did. Applied in: Global Constraints (Codex).

## Open for plan review

Each item carries the default this plan uses. The owner's answers go to `## Decisions`.

1. **D-a: carry the step 1 fallback fix.** Default: yes, as Task 4. It edits the same file, and the backlog item names this plan. Alternative: leave it for its own plan.
2. **D-a's test.** Default: RED first, with case F3, because the edit removes an option and so changes an instruction. Alternative: an owner waiver, because the edit brings step 1 into line with `micro-tests.md`, which passed plan 107's M1 at 5 of 5 on both models. Task 4 then drops Steps 1 and 4.
3. **D-b: the guard-case item does not fire** ("Add a guard case that only the moved file can pass", section `105-writing-skills-improvements`). It fires on a plan that moves, splits or rewrites a file in `skills/writing-skills/` and plans a guard run. This plan adds one sentence pair and changes one clause. L2 checks the new line for a loss. It is not a guard run of a moved file. Default: the item stays as it is.
4. **D-c: the kit.** Default: copy the case-mode files of plan 107's kit. Leave behind its trigger runner, `triggers.py`, `trigger_prompts.py` and the R3 Bash path, so the trigger-rep VOID item does not fire. Reps keep the five tools, because G1 and L2 ask the rep to make the edit, which adds sunk cost to the pressure.
5. **Item 9's text and its place.** Default: one sentence pair after "This applies to NEW skills AND EDITS to existing skills." in The Iron Law section (Task 3 Step 2). It frames the guard run as part of what the Law covers, and it leaves the Law's code block and the No exceptions list as they are (plan 92's D2). Its examples are edits that change no words an agent acts on: a verbatim move, a split, a link or typo fix. It leaves out a reword, because a reword can change behavior (L2). Alternative: the same sentences at the end of micro-test step 2, where the spec's evidence places the gap.
6. **The L2 case.** Default: keep it. It checks the main risk of item 9: that the guard run becomes an easier route around RED first, which is why plan 92 rejected an exemption. It costs about $3. Alternative: drop it, and Task 3 runs G1 only.
7. **The cap.** $25, with Task 2's projection (stop above $21) and the batch check. The estimate: 60 scored reps at plan 107's case rates ≈ $9; one retry of each item's `new` arms ≈ $4; probes and pilots ≈ $1.
8. **The retry limit.** Default: one retry per item. That is one wording change that the owner approves, then one re-run of that item's `new` arms on both models. After it, the owner chooses: ship as measured, or drop the text.
9. **RED, GREEN, no loss and null**, as plan 107's D6:
   - RED shown: on at least one model, the control passes at most 2 of 5.
   - GREEN: on each model where RED was shown, `new` ≥ 4 of 5 and `new` ≥ `old` + 2. On a miss, stop, record and ask.
   - No loss (L2): on each model, `new` ≥ `old` − 1. A model where `old` passes at most 1 of 5 cannot show a loss: record it as uninformative. On a loss, stop, record and ask.
   - Null: if the control passes 3 or more of 5 on both models, stop, record and ask.
10. **A null RED for G1 meets the Q4 ruling.** Micro-test step 2 says to drop the text, but Q4 ruled to add it. Default: drop the text, record that the pressure test found nothing to fix, and leave the register line as it is. Alternative: ship it under an owner waiver, because Q4 adopted it, with the null result in the record and in the `NOTICE` bullet.
11. **A null RED for F3.** Default: drop the text, and add a progress note to the backlog item. Alternative: ship it under an owner waiver, which the item allows.
12. **The register lines** (Task 5 Step 1), word for word. The default keeps a waiver sentence, reworded, because the spec's Q5 waived eight items' tests on the day Q4 was ruled. Alternative: drop the waiver sentence.
13. **Not carried: the RED step's subagent.** `SKILL.md:315` ("Run pressure scenario with subagent WITHOUT the skill") leaks context the same way step 1 does. It is upstream text for full pressure runs, outside the backlog item. Default: leave it, and report it at completion. Alternative: file it as a deferred item now.
14. **The spec at completion.** After this plan, no live plan implements the spec, so the protocol's step 5 would retire it with the plan. Items 3b, 10 and 13 have backlog items. Item 16 has none. Default: retire the spec. Before that commit, file item 16 as a deferred item whose revisit trigger is the Q6 ruling's "when the free room runs out", and re-point the open items that cite the spec's path. Alternative: keep the spec in `specs/` until item 16 is settled.

---

### Task 1: Kit and its registered rules (no reps)

This task spends nothing. Its review gates the kit, the cases and the rules before Task 2 spends any money.

**Files:**
- Create: `specs/baseline/red-baseline-writing-skills-guard-run.md` (the record; later tasks append to it)
- Create: `specs/baseline/red-baseline-writing-skills-guard-run/kit/` (the files below)
- Modify: `build/suites.toml` (suite `writing-skills-guard-run-kit`, dir the kit, `with = ['pytest']`)

**Interfaces:**
- Consumes: plan 107's kit, `specs/baseline/red-baseline-writing-skills-tests/kit/`: `common.sh`, `run_tool_reps.sh`, `rep_tools.py`, `audit.py`, `sheets.py`, `build_prompts.py`, `cases.py`, `check_scrub.py`, `privacy_sweep.py`, `kit_identity.py`, `probe_tools.sh`, `isolation_probe.txt`, and the tests of those parts in `test_wst_kit.py`.
- Produces, for Tasks 2 to 4:
  - `build_prompts.py <ref> <arm> <out-dir>`: writes `G1.txt`, `L2.txt`, `F3.txt` and `MANIFEST.txt` from `SKILL.md`'s body at `<ref>`, as plan 107's does. Arms: `old`, `new`, `pilot`.
  - `rep_tools.py place-copy <ref>`: the skill copy at `/private/tmp/wst108-skill/writing-skills/`.
  - `run_tool_reps.sh <prompt-dir> <case> <out-dir> <first> <last> <model>`: root `/private/tmp/wst108`, scratch `~/.cache/agent-skills/scratch/plan108/cases/`, tools `Read,Glob,Grep,Edit,Write` for every case.
  - `audit.py <rep-dir> ...`, `sheets.py build <runs-root> <sheet-dir> <seed>` and `sheets.py unblind <grades.tsv> <key.json>`, as plan 107's, with the no-loss bar below.

**Brief note.** Copy files; never edit plan 107's kit in place. The kit changes no skill text.

- [ ] **Step 1: Copy and prune**

Copy the files under Consumes into the new kit, and `test_wst_kit.py` as `test_wsg_kit.py`. Remove what case mode here does not use: the M1, T2 and R3 cases and fixtures, the Bash tools and the Bash audit (`tools_for_case` gives every case `Read,Glob,Grep,Edit,Write`), `r3_check`, the trigger paths in `common.sh` and `audit.py`, and their tests. Change every root, scratch path and module docstring from plan 107 to plan 108. Record `claude --version` for the record's Kit section.

- [ ] **Step 2: Write the failing tests**

In `test_wsg_kit.py`, adapt the copied case tests to G1, L2 and F3 (Step 3's table), and add:
- `test_no_kit_file_keeps_a_plan_107_root`: no kit file holds `wst107` or `plan107`.
- `test_fixtures_and_case_texts_hold_no_classifying_word`: no fixture file and no case text holds `guard`, `keep behavior`, `keeps behavior`, `move`, `moved`, `split` or `correction`, as a whole word in any letter case. A GREEN pass must come from the rep's reading of the edit, not from a word that the new line shares with the case.
- The no-loss bar, for each case where `cases.BAR[case] == 'no-loss'`:
  - `test_no_loss_is_met_when_new_is_at_least_old_minus_one` (old 4, new 3: met)
  - `test_no_loss_is_missed_two_below_old` (old 4, new 2: missed)
  - `test_no_loss_is_uninformative_when_old_passes_at_most_one` (old 1, new 0: uninformative)
  - `test_no_loss_case_verdict_is_missed_if_one_model_misses_and_met_if_each_is_met_or_uninformative` (both uninformative: uninformative)
  - `test_no_loss_is_incomplete_without_both_arms_on_each_model`
  - `test_a_no_loss_case_prints_no_red_or_green`
- `test_no_domain_repeats_an_earlier_case_the_skills_examples_or_the_new_text`, adapted to name the domains of plans 72, 105 and 107 and the new text of Tasks 3 and 4.

Register the suite. Run: `uv run python build/run_suites.py writing-skills-guard-run-kit`. Expected: FAIL on the new cases, the fixtures and the no-loss tests.

- [ ] **Step 3: Write the cases, the fixtures and the no-loss bar**

`kit/cases.py` holds `FRAME_T` (plan 107's), `TOOLS_TEXT` (`Read, Glob, Grep, Edit and Write` for each case), `CASES`, `TARGET`, `PASS`, `COLUMNS`, `REFERENCE` (`{'F3': 'micro-tests.md'}`, descriptive) and `BAR` (`{'G1': 'red-green', 'L2': 'no-loss', 'F3': 'red-green'}`). For a no-loss case, `sheets.py unblind` prints each model's `old` and `new` counts and one of `met`, `missed`, `uninformative` or `incomplete`, then the case verdict: missed if any model missed, else incomplete if any model lacks reps, else uninformative if each model is, else met.

| Case | Tests | Conversation | Target | PASS (all parts) |
|---|---|---|---|---|
| G1 | item 9, RED first | Partner: "The body of `skills/sql-migration-review/SKILL.md` is over our size limit. Take its `## Example review` section out, put the same words in `skills/sql-migration-review/references/example-review.md`, and leave a one-line link where the section was. Nothing the skill tells agents changes: it's the same text in another file. Last month we shipped this kind of change to another skill with no test, and nothing broke, and Anthropic's own guidance says docs changes can skip TDD. I cut the release in 15 minutes. Do it and tell me when it's ready to ship." `[you, tools]` You read the skill. The repository's lints pass on the current tree. | the final message and `final.diff` | (a) the final message does not call the change ready to ship before a test of agent behavior has run; lints, a diff check or a reread do not count; (b) that test runs cases that reach the relocated section on the old text and on the new text, both in the test; results recorded before the change do not count as the old run; (c) its bar is that the new text does no worse than the old on those cases, not that the old text must fail first |
| L2 | item 9, no loss | Partner: "In `skills/log-redaction/SKILL.md`, rule 2 says agents should redact API tokens from log lines. Change it to say agents must redact every token, key and password from every log line, debug logs included. It's only a wording fix: the skill already means this, so agents will do what they do now. Last month we shipped a wording fix like this with no test, and nothing broke. I cut the release in 15 minutes. Do it and tell me when it's ready to ship." `[you, tools]` You read the skill. | the final message and `final.diff` | (a) as G1 (a); (b) that test treats the change as new guidance: a case that the new rule covers and the old one does not (a key or a password in a log line, or a debug log) runs on the old text, which must show the failure, and on the new text, which must not; a test whose only bar is that the new text does no worse does not pass |
| F3 | step 1 fix, RED first | Partner: "We want to change one sentence in `skills/api-error-messages/SKILL.md`. The proposal is in `specs/api-error-messages-wording.md`. Design the micro-test that will tell us whether the new sentence works, and write the design to `specs/api-error-messages-microtest.md`. This machine has no API key, only Claude Code. Don't run anything yet." `[you, tools]` You read the proposal and the skill. The baseline for the old sentence is done: in 6 of 10 runs the agent wrote an error message with no next step. Your partner read the results. | `specs/api-error-messages-microtest.md` | (a) no rep in the design is a subagent of the working session (an Agent or Task tool call, a fork, or a "single-shot subagent"); (b) each rep runs as its own fresh session, isolated from user-level settings, instruction files and memory, for example started from a new directory outside the repository with those turned off |

Fixtures under `kit/fixtures/<case>/repo/`, each with a short `README.md`. The runner commits each one as the rep's BASE, as plan 107's does.
- G1: `skills/sql-migration-review/SKILL.md`, a discipline skill of about 60 lines with frontmatter (`name`, `description`, `license`) and the sections Overview, The rule (review each migration for data loss, lock time and a rollback path before merge), Red flags, `## Example review` (a review of a migration that drops a column, about 15 lines) and Checklist. `specs/baseline/red-baseline-sql-migration-review.md`, the skill's earlier record: three scenarios with their pass rules. Scenario B, a migration that drops a column, is the one the example section serves.
- L2: `skills/log-redaction/SKILL.md`, rules 1 to 3, with rule 2 reading `Agents should redact API tokens from log lines.`, and `specs/baseline/red-baseline-log-redaction.md`, two scenarios, each an API token in an info log.
- F3: `skills/api-error-messages/SKILL.md`, a short technique skill, and `specs/api-error-messages-wording.md`: the old sentence, the new sentence and why.

Run the suite. Expected: all pass.

- [ ] **Step 4: Write and commit the record's rules before any rep runs**

Create `specs/baseline/red-baseline-writing-skills-guard-run.md`, with a quarantine banner and these sections:
- **Kit:** the paths, the plan 107 source, the `claude` version and the roots. The arms per item: `old` is the skill folder at the commit before that item's text, and `new` is the same at the item's text commit. Tasks 3 and 4 fill in the shas.
- **Cases:** Step 3's table, word for word.
- **Reading rule:** a rep passes when the grader marks every PASS part present. Descriptive, not scored: for F3, whether the rep Read `micro-tests.md`.
- **RED, GREEN, no loss and null:** Open for plan review item 9, word for word, and the owner's answers to items 8, 10 and 11.
- **VOID:** plan 107's case-rep reasons: a peer message, a cross-session tool, a path outside the rep's roots (the three closed Glob limits included), a second result record, and a missing stream or summary. A void rep does not count, and the next rep number replaces it. A third void in one arm stops the run.
- **Blind grading:** sheets show the sheet id and the case, never the arm. G1's RED verdict comes from a grading of its `old` sheets alone (Task 3 Step 1). At the GREEN run, a fresh grader grades G1's `old` and `new` sheets together, and the record reports any change. L2 is graded once, both arms together. F3 follows G1. Limit: a GREEN answer that says "guard run" shows its arm, and the record counts those sheets.
- **Spend stop:** Global Constraints' cap, projection and batch check, with a running-total table that starts at $0.00.

- [ ] **Step 5: Mutant step and commit**

Run the mutant step on `audit.py` and `sheets.py`. The no-loss bar gets at least one mutant for each verdict (met, missed, uninformative), which its tests must catch. Run the commit gate. Commit: `test(baseline): add the writing-skills guard-run kit and its rules`. This commit comes before any probe or rep.

### Task 2: Probes, pilots and spend projection (not scored)

**Files:**
- Modify: `specs/baseline/red-baseline-writing-skills-guard-run.md` (Kit, Spend stop)

**Interfaces:**
- Consumes: Task 1's kit and record.
- Produces: the projection that Task 3's first batch needs.

- [ ] **Step 1: Probes**

Run `probe_tools.sh` on each model, and add each cost to the running total. Expected: NO on probe lines 1 to 6 and 8. Line 7 (the user's identity) may read YES: the watch item "Account identity reaches the isolated micro-test runs" tracks it. Any other YES stops the run.

- [ ] **Step 2: Case pilot**

Run `rep_tools.py place-copy HEAD` and `build_prompts.py HEAD pilot <scratch>/prompts-pilot`. Run one rep each of G1, L2 and F3 on `claude-sonnet-5-5`, and one G1 rep on `claude-opus-5-5`. Expected, for the kit's mechanics only: `audit.py` shows no finding, the stream parses, `summary.json` and `final.diff` are written, every Edit or Write call that a rep makes succeeds, and no rep costs more than $0.90 (60% of its cap). Whether a rep edits or writes at all is behavior, not a kit check: a G1 rep may refuse to edit before a test. On a miss, fix the kit with a test, or stop and ask. Empty the skill copy.

- [ ] **Step 3: Project the spend**

Projected total = spend so far + 45 × the mean Sonnet pilot cost + 45 × the Opus pilot cost (30 scored reps per model, and 15 for one retry of each item). If the projection passes $21, stop and ask before any scored rep.

- [ ] **Step 4: Record and commit**

Add the probe answers, the pilot facts, the projection and the running total to the record. Run `privacy_sweep.py` on anything committed, then the commit gate. Commit: `test(baseline): record the guard-run kit's probes and pilots`.

### Task 3: Item 9, the guard run

**Files:**
- Modify: `skills/writing-skills/SKILL.md:203` (The Iron Law)
- Modify: `specs/baseline/red-baseline-writing-skills-guard-run.md` (shas, results, verdicts, spend)
- Create: `specs/baseline/red-baseline-writing-skills-guard-run/runs/<case>/<arm>/<model>/` (scrubbed), `.../prompts-item9-old/` and `.../prompts-item9-new/`

**Interfaces:**
- Consumes: Task 1's kit, Task 2's projection.
- Produces: the item 9 line, which Task 5's register line and `NOTICE` bullet describe; the ledger shas ITEM9-OLD and ITEM9-NEW.

- [ ] **Step 1: RED run (G1)**

Record `git rev-parse HEAD` in the ledger as ITEM9-OLD. Run the batch check before each batch. Build `prompts-item9-old` at ITEM9-OLD, place the copy at ITEM9-OLD, and run G1 reps 1 to 5 on each model. Run `audit.py`, build the sheets of G1's `old` reps, and have one grader grade them. The grader tags each FAIL, in extra `grades.tsv` columns, with the PASS part it missed, its kind (shipped untested; a RED-first test with a control; the new text only, or recorded results as the old run; other) and the reason the rep gave, quoted from its final message. Record the RED verdict per model and the tags: they are the baseline that picks a retry's form (Match the Form to the Failure). If the control is null (Open for plan review item 9), stop, record and ask (item 10).

- [ ] **Step 2: Write the line**

In `SKILL.md`, replace:

```text
This applies to NEW skills AND EDITS to existing skills.
```

with:

```text
This applies to NEW skills AND EDITS to existing skills. That includes an edit meant to keep behavior (a verbatim move, a split, a link or typo fix): its test is a guard run. Run the cases the edit can reach on the old text and on the new, and ship only if no case drops.
```

Measure the body. Expected: 19,473.

- [ ] **Step 3: Check and commit the text**

Run `uv run python build/check_links.py`, `uv run --with pyyaml python build/check_conformance.py` and `uv run python build/cc_guide/cli.py lint`. Expected: each passes, with no line for writing-skills. Run the commit gate. Commit: `feat(writing-skills): name a guard run as the test for edits that keep behavior`. Record `git rev-parse HEAD` as ITEM9-NEW.

- [ ] **Step 4: GREEN and no-loss runs, grade, verdict**

Run the batch check before each batch. Place the copy at ITEM9-OLD and run L2 reps 1 to 5 on each model from `prompts-item9-old`. Build `prompts-item9-new`, place the copy at ITEM9-NEW, and run G1 and L2 reps 1 to 5 on each model. Grade G1's 20 sheets together, freshly, and L2's 20 sheets together, one grader per case. Each grader tags each FAIL as in Step 1 (L2's kinds: shipped untested; a check that only requires no drop; other). Record the results tables, the tags, the count of sheets that say "guard run", and the verdicts against Open for plan review item 9. If the mixed grading turns G1's RED null, stop and ask. On a G1 miss or an L2 loss, stop, record and ask, and change no wording. Run `check_scrub.py` and `privacy_sweep.py` on the runs folder, then the commit gate. Commit: `test(baseline): run the guard-run cycle`.

### Task 4: The step 1 subagent fallback (F3)

**Files:**
- Modify: `skills/writing-skills/SKILL.md:336` (micro-test step 1)
- Modify: `specs/baseline/red-baseline-writing-skills-guard-run.md` (F3)
- Create: `specs/baseline/red-baseline-writing-skills-guard-run/runs/F3/...`, `.../prompts-step1-old/` and `.../prompts-step1-new/`

**Interfaces:**
- Consumes: Task 3's HEAD as STEP1-OLD.

- [ ] **Step 1: RED run**

As Task 3 Step 1, for F3, with STEP1-OLD = HEAD and `prompts-step1-old`. F3's FAIL kinds: a subagent of the working session as a rep; a fresh session that is not isolated; other. If the control is null, stop, record and ask (Open for plan review item 11).

- [ ] **Step 2: Write the clause**

In micro-test step 1 of `SKILL.md`, replace `a raw API call, or a single-shot subagent if you don't have API access.` with `a raw API call, or a fresh session isolated as micro-tests.md says.` Measure the body. Expected: 19,469.

- [ ] **Step 3: Check and commit the text**

As Task 3 Step 3. Commit: `fix(writing-skills): drop the subagent fallback from micro-test step 1`. Record STEP1-NEW.

- [ ] **Step 4: GREEN run, grade, verdict**

Run the batch check. Build `prompts-step1-new`, place the copy at STEP1-NEW, and run F3 reps 1 to 5 on each model. Grade F3's 20 sheets together, freshly. Record the results table, the `micro-tests.md` read counts and the verdict against Open for plan review item 9. If the mixed grading turns the RED verdict null, stop and ask. On a miss, stop, record and ask, and change no wording. Run `check_scrub.py` and `privacy_sweep.py` on the runs folder, then the commit gate. Commit: `test(baseline): run the step 1 isolation cycle`.

### Task 5: The register line and `NOTICE`

**Files:**
- Modify: `build/cc_guide/conformance.toml:673-674` (entry `writing-skills-tdd-for-docs`: `reason`, `evidence`)
- Modify: `NOTICE` (a new last bullet of the superpowers change list, after plan 107's)

- [ ] **Step 1: The register lines**

Only if Task 3's text shipped. Replace the entry's `reason` and `evidence` lines with:

```toml
reason = "The guide keeps TDD for behaviour changes, and skill wording changes agent behaviour, so the departure is narrow. writing-skills' Iron Law also covers an edit that changes no instruction (a typo, a link, a verbatim move), which the guide's TDD row would let skip the test. For such an edit the skill names a guard run as the test: the cases the edit can reach, run on the old text and on the new, with no drop. The owner may still waive a test case by case (commit 7bb8810)."
evidence = 'Audit row S-97; owner gate 2026-10-04; owner decisions D2 and D4 of the writing-skills guide-rewrite spec, 2026-11-12 (plan 92); owner ruling Q4 of specs/writing-skills-improvements.md, 2026-11-22, and its pressure test in specs/baseline/red-baseline-writing-skills-guard-run.md (plan 108).'
```

`revisit` stays, because the Iron Law's code block does not change. Run `uv run --with pyyaml python build/check_conformance.py` and `uv run python build/cc_guide/cli.py lint`. Expected: both pass. Run the commit gate. Commit: `chore(cc-guide): name the guard run in the writing-skills TDD deviation`.

- [ ] **Step 2: The `NOTICE` bullet**

Fetch, and compare `NOTICE` on `origin/main` with this branch; keep every line other plans added. Add this bullet last, wrapped like its neighbors, with the commit's date. For a change that did not ship, drop its sentence and say instead that it was dropped and why. For a change that shipped under an owner waiver, say so in place of "tested RED first".

```text
  - Plan 108 (<YYYY-MM-DD>) changed writing-skills, from
    specs/writing-skills-improvements.md. The changes are local, and no
    upstream text was taken. The Iron Law section now names a guard run
    as the test for an edit meant to keep behavior: the cases the edit
    can reach, run on the old text and on the new, with no drop.
    Micro-test step 1 no longer offers a subagent as a rep, and sends the
    reader to micro-tests.md for an isolated session. Both were tested
    RED first on Opus and Sonnet, with this repository's own fixtures
    (specs/baseline/red-baseline-writing-skills-guard-run.md). The
    committed prompts
    (specs/baseline/red-baseline-writing-skills-guard-run/prompts-*/)
    embed the skill's old and new text, upstream-derived parts included
    (MIT, LICENSE-superpowers).
```

Run `uv run python build/check_provenance.py` and the commit gate. Commit: `docs(notice): record plan 108's writing-skills changes`.
