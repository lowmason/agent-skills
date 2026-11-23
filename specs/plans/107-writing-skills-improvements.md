# writing-skills Micro-Test Method, Trigger Test and Rename Procedure Implementation Plan

> ⚠️ Quarantine this file during any micro-test of writing-skills, as the spec says of itself. Task 1
> names the RED cases, the trigger prompts and what each one scores, so a rep that reads this file is void.

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship step 3 of the spec's Proposed sequence: the full micro-test method (item 1), a trigger test (item 2) and a rename procedure (item 10), each RED first, then the reordered writing-skills description (item 3b), checked with item 2's trigger test.

**Architecture:** Seven tasks on one branch, in order. Task 1 builds one kit and commits its rules, and spends nothing. Task 2 runs the probes and pilots and projects the spend. Tasks 3, 4 and 5 each run one item's cycle: a RED run on the current skill, the text, then a GREEN run, graded blind with both arms mixed. Task 6 measures the Codex cut and runs the trigger test, old description against new. Task 7 writes the `NOTICE` bullet, and then the owner runs the `/cc-guide files` verify.

**Tech Stack:** Markdown skill text; a `claude -p` micro-test kit (bash 3.2 and Python 3.11+, stdlib), copied from plan 105's kit; pytest through `build/run_suites.py`; `codex debug prompt-input` for one local measurement.

**Spec:** `specs/writing-skills-improvements.md`, approved for planning on 2026-11-22, with the owner rulings in its Owner decisions section. This plan covers Proposed sequence step 3: items 1, 2 and 10, then 3b. Step 4 (item 9) gets its own plan. Item 13 goes with its backlog item's plan. Item 16 is held (Q6).

## Global Constraints

- **Base.** `skills/writing-skills/` at `main` `bc01afc` (D1). Before Task 1, run `git diff bc01afc HEAD -- skills/writing-skills`. If it prints anything, stop and ask. Line numbers below were taken at `bc01afc`. The old text in each step is the match key.
- **Execution order.** This plan is a domain stream. Start it only while fewer than 3 domain executions run and none shares its files (check `list_sessions`). Step 4's plan (item 9) also edits `SKILL.md`, so it waits for this plan's merge.
- **One owner per file.** `SKILL.md` changes in Tasks 3, 4 and 6 only. `references/discovery.md` changes in Tasks 4 and 5 only. `references/claude-code.md` changes in Task 4 only. `NOTICE` changes only in Task 7. `build/suites.toml` gains one entry, in Task 1. `build/cc_guide/baseline.json` changes only through Task 7's `/cc-guide` run.
- **Body ceiling.** At the end of this plan the `SKILL.md` body is at most 19,280 characters, measured with `check_conformance.skill_body(text)[0]` (`uv run --with pyyaml python`, with `build/` on `sys.path`). It is 19,053 at `bc01afc`. That leaves at least 420 of the 19,700-character window: about 240 for items 9 and 13 and about 180 spare. The exact text in this plan measures 19,258 (Task 3: +141 → 19,194; Task 4: +64 → 19,258; Tasks 5 and 6: +0). If an edit would pass 19,280, stop and ask.
- **RED first.** Each of Tasks 3, 4 and 5 runs its RED arm and grades it before any of its skill text is written (writing-skills' Iron Law). Each item can drop alone. A null control drops that item's text only.
- **Live skill.** `CLAUDE.md` sends every agent that edits a skill to writing-skills, and `~/.claude/skills` links to the main checkout. Execute from a worktree, so agents keep reading main's writing-skills until the merge.
- **Bare names.** New skill text names no other skill, so `install.py`'s `DEPENDENCIES` and `SOFT_REFERENCES` do not change.
- **Claude Code facts.** Every Claude Code fact in new text rests on a guide section that the `SKILL.md` citation names. Task 4 adds `skills.iterating` to the citation. `references/micro-tests.md` names no Claude Code flag (spec item 1: the flags stay in the kits).
- **Commit gate.** Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Messages follow Conventional Commits, use plain technical English and end with the attribution trailer that the executing session is given. State test counts as deltas.
- **Mutant step.** Task 1 runs the mutant step on `audit.py`, `triggers.py` and `sheets.py`, with one mutant per Glob limit (D5). Tasks 2 to 7 record `--no-mutants` with the reason "Markdown, records and kit runs only; no code".
- **Micro-tests.** Models `claude-opus-5-5` and `claude-sonnet-5-5`. Nobody messages or subscribes to a running rep. The spec and this plan stay out of every rep's reach (D2): reps deny `Read(//Users/**)`, run from `/private/tmp`, and read a skill copy made by `git archive`. Raw output goes to `~/.cache/agent-skills/scratch/plan107/`, never into the repository. Committed copies are scrubbed, and `privacy_sweep.py` passes on them before their commit.
- **Grading.** Grader agents on Opus grade the sheets, one agent per case, with no key, as plan 105's Deviation 9 did and the owner ratified. A sheet never shows the arm. Trigger reps are scored mechanically from the stream, so they have no sheets.
- **Spend (plan 105's D2).** The cap for every probe, pilot and rep in this plan is $50. Per-rep `--max-budget-usd`: $1.50 for a case rep (Tasks 3–5), $0.25 for a trigger rep (Task 6). Task 2 projects the total, and a projection above $42 stops the run before any scored rep. Before each pair (a case's 5 `old` and 5 `new` reps on one model, or a trigger cell's `old` and `new` reps on one model and condition), check: running total + reps in the pair × per-rep cap ≤ $50. A pair that fails the check stops the run: report BLOCKED with the spend table. Expected spend is about $30–35.
- **Codex (D3).** `~/.cache/agent-skills/scratch/plan105/` and `~/.cache/agent-skills/scratch/plan107/` hold unscrubbed rep output, and Codex's read-only sandbox can read them. Ask the owner before any Codex seat (the final review, or finishing's Step 4b), and delete neither folder without asking. Task 6's `codex debug prompt-input` renders a prompt and calls no model; it is not a seat.
- **Public repository.** The plan, kit, record and commits carry no private detail. Records cite committed files only. Plugin skill text never enters the repository (Open for plan review item 9).
- **Leave alone.** Item 9, item 13 and item 16. Every committed kit under `specs/baseline/`. The status of the "Trigger-eval suites" item (section `53-agent-skills-portability`), which stays open (spec item 2), and of the "Add a guard case that only the moved file can pass" item, which this plan does not fire (Open for plan review item 13).
- **Completion.** The spec stays in `specs/` at completion, because step 4 remains. The protocol's step 5 retires the plan only.

## Review Focus

1. **A `**` Glob from the rep folder, or a brace alternative under an absolute or `$HOME/Library` prefix, that reaches the real Keychains folder.** Expected: the audit voids the rep. Pinned in Task 1 Step 2 (the three Glob tests).
2. **A case rep that runs a Bash command other than `git mv`, or a `git mv` with a path outside the rep folder.** Expected: VOID, whether or not the command succeeded. Pinned in Task 1 Step 2, `test_bash_other_than_git_mv_voids` and `test_git_mv_outside_rep_voids`.
3. **A trigger rep that loads `writing-skills` through a second Skill call, after another skill.** Expected: it counts as a load. Pinned in Task 1 Step 2, `test_load_counts_a_later_skill_call`.
4. **A rep whose stream shows a listing without `writing-skills` or without both competitor skills.** Expected: VOID (the listing is the condition under test). Pinned in Task 1 Step 2, `test_listing_without_competitors_voids`.
5. **A GREEN answer that names `micro-tests.md`, which shows the arm.** Expected: the sheet keeps the name, and the record reports it as a blind-scoring limit, as plan 105's did. Pinned in Task 1 Step 4 (the record's Blind grading section).

## Decisions

- **D1** (owner, brief, 2026-11-23): pin the base at `main` `bc01afc`, where PR #257 merged plan 105's last quick fixes. Applied in: Global Constraints (Base).
- **D2** (owner, brief, 2026-11-23): quarantine the spec and this plan file during every writing-skills micro-test, because both name the RED scenarios. Applied in: Global Constraints (Micro-tests), Task 1.
- **D3** (owner, brief, 2026-11-23): `~/.cache/agent-skills/scratch/plan105/` still holds unscrubbed rep output. Ask the owner before any Codex seat, and do not delete that folder without asking. Applied in: Global Constraints (Codex).
- **D4** (owner, brief, 2026-11-23): copying plan 105's guard kit fires the backlog item "Close the three Glob audit limits when the guard kit is reused"; moving or rewriting a writing-skills file with a guard run fires "Add a guard case that only the moved file can pass". This plan copies `audit.py`, so the first fires, and Task 1 closes it. Whether the second fires is Open for plan review item 13. Applied in: Task 1.
- **D5** (owner, brief, 2026-11-23): close each of the three Glob limits with a test and a mutant (the backlog item's own "Done when"). Applied in: Task 1.
- **D6** (owner, plan review, 2026-11-23): "Approve as proposed": every default in Open for plan review (items 1–14), so the $50 cap with its $42 projection stop, the case wording and pass rules, the trigger prompts and bars, and the new skill text are final. Applied in: Global Constraints, Tasks 1–7.

## Open for plan review

Resolved at plan review on 2026-11-23: the owner approved each default as proposed (D6). Each item carries the default this plan uses.

1. **The cap** (plan 105's D2). $50, with Task 2's projection (stop above $42) and the pair check. The estimate: 60 case reps at plan 105's tools-rep rates (about $0.12 Sonnet, $0.28 Opus) ≈ $12; 192 trigger reps at about $0.05 Sonnet and $0.15 Opus ≈ $19; probes and pilots ≈ $2.
2. **The case wording and pass rules** (Task 1 Step 4). M1, T2 and R3 as the table states.
3. **RED shown.** On at least one model, the control passes at most 2 of 5. If the control passes 3 or more of 5 on both models, the item is null: stop, record, and ask. Default answer: drop that item's text (micro-test step 2).
4. **GREEN bar.** On each model where RED was shown: `new` ≥ 4 of 5, and `new` ≥ `old` + 2. On a miss, stop, record, and ask. The executor changes no wording without the owner.
5. **Item 2's reading of "on and off".** The spec's procedure counts loads "with the skill on and with it off". A session with the skill off never loads it, so this plan's text counts loads with the old description and the new one, and keeps on-and-off for comparing the work once the skill loads, as the guide's `skills.iterating` says. Alternative: the spec's wording as it stands.
6. **Item 10 has no body pointer**, as the spec's 0 body characters says. The rename list sits in `discovery.md` only. If R3's GREEN misses its bar and no `new` rep read `discovery.md`, stop and ask whether to add a pointer (about +40, inside the ceiling's spare room) and re-run the `new` arm only.
7. **Item 10's search scope.** The spec's step 2 names "skills and instruction files". This plan's text adds commands, agents and settings, where this repository and the fixture both hold names. Alternative: the spec's two places only.
8. **R3's Bash.** A rename needs a move, and the case tools have none. R3 reps get `Bash` with `--allowedTools` limited to `Bash(git mv *)`, and the audit voids any other Bash call. Alternative: tell the rep that the partner runs the move, which drops the spec's step 1 from the test.
9. **The trigger test's listing.** Every skill in `skills/` at the arm's commit, plus plugin-dev's `skill-development` and the official `skill-creator`, the plugin skills that also claim skill creation (spec item 3, Test). They are copied from the local plugin cache into scratch at run time. Their text never enters the repository, and the record names each plugin, skill and version only. Claude Code's bundled skills also list, in both arms. The rep's settings set `skillListingBudgetFraction` to 0.05, so that the budget drops no description; Task 2's listing probe checks it.
10. **3b's test is a routing check in Claude Code, and the gain is measured in Codex** (Task 6). Claude Code lists the full description, so the trigger test can only show no loss. The `cut150` condition (`skillListingMaxDescChars: 150`) imitates Codex's cut, and `codex debug prompt-input` measures the real one. Running `codex debug prompt-input` calls no model, so no rep output reaches OpenAI.
11. **The new description** (Task 6 Step 2). Its first 150 characters hold all four testing triggers. It replaces "pressure-testing a discipline skill" in its second sentence with "bulletproofing a discipline skill", so "pressure-testing" occurs once.
12. **The files verify.** The owner types `/cc-guide files skills/writing-skills/SKILL.md` in the execution session after Task 7's `NOTICE` commit, as plan 105 did.
13. **The guard-case item does not fire.** Its trigger is a plan that "moves, splits or rewrites a file in `skills/writing-skills/` and plans a guard run". This plan moves and splits no file. Task 6 rewrites the description and runs old against new, but that run checks routing, not whether an agent reads a file and then uses it, which is what the item's case would test. Default: the item stays as it is. Alternative: treat Task 6 as firing it, and add a case to Task 6 that only the new description can pass.
14. **M1 part (a) and a raw API call.** The current step 1 offers a raw API call, which carries no user settings, instruction files or memory. Default: a design that runs each rep as a raw API call passes part (a).

---

### Task 1: Kit and its registered rules (no reps)

This task spends nothing. Its review gates the kit, the cases and the rules before Task 2 spends any money.

**Files:**
- Create: `specs/baseline/red-baseline-writing-skills-tests.md` (the record; later tasks append to it)
- Create: `specs/baseline/red-baseline-writing-skills-tests/kit/` (the files below)
- Modify: `build/suites.toml` (suite `writing-skills-tests-kit`, dir the kit, `with = ['pytest']`)
- Modify: `specs/deferred_items.md` (`→ planned 2026-11-23: specs/plans/107-writing-skills-improvements.md` on the Glob item, in the commit that adds this plan)

**Interfaces:**
- Consumes: plan 105's kit (`specs/baseline/red-baseline-writing-skills-layout/kit/`): `common.sh`, `run_tool_reps.sh`, `rep_tools.py` (`place-copy`, `check-copy`, `summarize`), `audit.py`, `sheets.py`, `privacy_sweep.py`, `check_scrub.py`, `probe_tools.sh`, `isolation_probe.txt`, `cases.py`'s `FRAME_T`, and their tests in `test_wsl_kit.py`. Plan 100's `run_rep.sh` (`specs/baseline/red-baseline-handoff-rerun/kit/`) for a rep HOME that holds skills.
- Produces, for Tasks 2 to 6:
  - `build_prompts.py <ref> <arm> <out-dir>`: writes `M1.txt`, `T2.txt` and `R3.txt` from `SKILL.md`'s body at `<ref>`, and `MANIFEST.txt` (ref, arm, body sha256 and length, each prompt's sha256, the skill copy's file hashes). Refuses an out-dir that exists. Arms: `old`, `new`, `pilot`.
  - `rep_tools.py place-copy <ref>`: `git archive <ref> skills/writing-skills` at `/private/tmp/wst107-skill/writing-skills/`. Refuses a non-empty folder.
  - `run_tool_reps.sh <prompt-dir> <case> <out-dir> <first> <last> <model>`: plan 105's runner, roots `/private/tmp/wst107` and `/private/tmp/wst107-skill`, scratch `~/.cache/agent-skills/scratch/plan107/cases/`. Tools `Read,Glob,Grep,Edit,Write`, and for R3 also `Bash` with `--allowedTools` adding `Bash(git mv *)`.
  - `run_trigger_reps.sh <ref> <arm> <condition> <prompt-id> <out-dir> <first> <last> <model>`: one fresh session per rep (below).
  - `triggers.py loads <rep-dir>` (prints `load` or `no-load` and the Skill calls), `triggers.py listing <rep-dir>` (the skills in the init record), `triggers.py tally <runs-root>` (counts per prompt, arm, condition and model).
  - `audit.py <rep-dir> ...` and `sheets.py build|unblind`, as plan 105's, with the changes below.

**Brief note.** Copy files; never edit plan 100's or plan 105's kit in place. The kit changes no skill text.

- [ ] **Step 1: Check the sources**

Check that plan 105's kit is on this branch's base. Run `claude --version` and `codex --version`, and record both in the record's Kit section. Find the newest cached copy of plugin-dev's `skill-development` and of the official `skill-creator` under `~/.claude/plugins/`, and record each one's plugin name, skill name and version (the cache folder name), never its path's user part.

- [ ] **Step 2: Write the failing self-tests**

`kit/test_wst_kit.py`, on synthetic records and folders. Copy plan 105's tests of the copied parts, renamed. Add:
- The three Glob limits (D5), each of which must void the rep:
  - `test_glob_double_star_from_rep_folder_reaching_keychains_voids`: a Glob with `path` `/private/tmp/wst107/rep1` and pattern `**/*`.
  - `test_relative_brace_alternative_joins_its_absolute_prefix`: pattern `/private/tmp/wst107/rep1/{home/Library/Keychains,x}/*`.
  - `test_brace_alternative_under_home_library_prefix_voids`: pattern `$HOME/Library/{Keychains,Caches}/*`, and the same with `~/Library/`.
  - And their clean neighbors: `**/*.md` with `path` the rep's `repo/`, and `{a,b}/*.md` under the rep's `repo/`, stay clean.
- `test_bash_other_than_git_mv_voids` (`ls`, `rm -rf x`, `git mv a b && ls`), `test_git_mv_outside_rep_voids` (`git mv skills/a /private/tmp/elsewhere/a`), `test_git_mv_inside_rep_is_clean` (`git mv skills/a skills/b`).
- `test_load_counts_a_skill_call_naming_writing_skills`, `test_load_counts_a_later_skill_call`, `test_no_skill_call_is_no_load`, `test_other_skill_call_is_no_load`.
- `test_listing_without_competitors_voids`, `test_listing_reads_the_init_record`.
- `test_trigger_rep_max_turns_stop_is_not_void`, `test_trigger_rep_budget_stop_is_not_void`: each keeps its load verdict.
- `test_r3_check_finds_old_name_in_untracked_file`.
- `test_trigger_runner_writes_cut150_settings` (the rep HOME's `settings.json` holds `"skillListingBudgetFraction": 0.05` in both conditions, and `"skillListingMaxDescChars": 150` for `cut150` and no such key for `full`), `test_trigger_runner_refuses_non_empty_root`.
- `test_sheets_hide_the_arm` for M1: two rep folders whose answers differ only in a path under the skill copy give byte-identical sheets.

Register the suite. Run: `uv run python build/run_suites.py writing-skills-tests-kit`. Expected: FAIL on the missing modules and the three Glob tests.

- [ ] **Step 3: Build the kit**

- **Case mode (M1, T2, R3).** Copy plan 105's tools-mode files with the roots, scratch and tools above, and `FRAME_T` with the skill-copy path changed. Close the three Glob limits in `audit.py`: join each brace alternative to the literal prefix before it, judge an alternative under `$HOME`, `~` or the rep's `home/` by the joined path, and treat a `**` whose search root is the rep folder, its `home/` or an ancestor of `home/Library` as reaching `home/Library`. Add the Bash audit: a Bash call is clean only when its command is one `git mv <src> <dst>` with both paths inside the rep's `repo/`.
- **Trigger mode.** `run_trigger_reps.sh` builds each rep as plan 100's runner does: `env -i`, an own HOME with `Library/Keychains` linked, `git archive <ref> skills/` extracted to `home/.claude/skills/`, the two competitor skill folders copied from the paths recorded in Step 1 to `home/.claude/skills/`, and `home/.claude/settings.json` holding the deny list, `"syncClaudeAiSkills": false`, `"skillListingBudgetFraction": 0.05` and, for `cut150`, `"skillListingMaxDescChars": 150`. The rep's `repo/` is `kit/fixtures/trigger/repo/`. Flags: `--setting-sources user` (Task 2's pilot checks it), `--strict-mcp-config`, `--no-session-persistence`, `--tools Read,Glob,Grep,Skill`, `--allowedTools Read,Glob,Grep,Skill`, `--max-turns 3`, `--max-budget-usd 0.25`, `--output-format stream-json --verbose`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`. Roots `/private/tmp/wst107t`, scratch `plan107/triggers/`. `audit.py` runs on each trigger rep too.
- **`triggers.py`**: a load is any `tool_use` named `Skill` whose `skill` input is `writing-skills`. `listing` reads the skills from the stream's init record.

Run the suite. Expected: all pass.

- [ ] **Step 4: Write `cases.py`, the prompts and the fixtures**

`kit/cases.py` holds `FRAME_T`, `CASES`, `TARGET` and `PASS`, as in the table. Each case states that the needed earlier steps are done, so the Iron Law does not hold the agent. No domain repeats the skill's examples, plan 72's or plan 105's cases, or the new text in Tasks 3–5.

| Case | Item | Conversation | Target | PASS (all parts) |
|---|---|---|---|---|
| M1 | 1 | Partner: "We want to change one line in `skills/changelog-entry/SKILL.md`. The proposal is in `specs/changelog-entry-wording.md`. Before I merge it, design the micro-test that will tell us whether the new wording works. Write the design to `specs/changelog-entry-microtest.md`. Don't run anything yet." | `specs/changelog-entry-microtest.md` | (a) the design isolates each rep from user-level settings, instruction files or memory, runs it in a fresh directory outside the repository, or runs it as a raw API call, beyond "a fresh context" or "a new subagent"; (b) it fixes the pass and fail rule before any reply is read; (c) it names at least two models to run each arm on |
| T2 | 2 | Partner: "Agents never load our `parquet-schema-check` skill, even when they're about to write a parquet file that breaks the schema. Fix it." | `skills/parquet-schema-check/SKILL.md` | the final message or a written file gives (a) at least three prompts that should load the skill and at least one that should not, and (b) says to run them, or ran them, with the old description and again with the new one, comparing loads |
| R3 | 10 | Partner: "Rename our `csv-dialect-sniff` skill to `sniffing-csv-dialects`." | the rep's repository | in the final tree: `skills/sniffing-csv-dialects/SKILL.md` exists with `name: sniffing-csv-dialects`, `skills/csv-dialect-sniff/` is gone, and `grep -rn --exclude-dir=.git csv-dialect-sniff .` prints nothing, untracked files included (mechanical) |

Fixtures under `kit/fixtures/<case>/repo/`:
- M1: `skills/changelog-entry/SKILL.md` (a short technique skill) and `specs/changelog-entry-wording.md` (the old line, the proposed line and why).
- T2: `skills/parquet-schema-check/SKILL.md`, whose description is `Helps with parquet files.` with valid frontmatter, and a neighbor `skills/polars-lazy-tuning/SKILL.md` with a sound description.
- R3: `skills/csv-dialect-sniff/SKILL.md`, `skills/ingest-raw-files/SKILL.md` (`**REQUIRED SUB-SKILL:** Use csv-dialect-sniff`), `skills/sniffing-csv-headers/SKILL.md` (a near collision, scored descriptively), `commands/ingest.md` (names the skill), `AGENTS.md` (names the skill) and `.claude/settings.json` (`"skillOverrides": {"csv-dialect-sniff": "name-only"}`). The repo is a git repository, committed once as the rep's BASE.
- Trigger: `skills/` with `table-diff`, `retry-budget`, `release-notes` and `fixture-loader`, one short skill each, and a `README.md`.

`kit/trigger_prompts.py` holds the eight prompts. Should-load, testing (P1–P3): "The `table-diff` skill never gets picked up, even when I ask it to compare two tables. Can you sort that out?"; "`retry-budget` keeps loading on every HTTP question, even unrelated ones. Make it stop."; "I reworded the core rule in `release-notes`. Before I ship it, check that the new wording actually changes what agents do." Should-load, core (P4–P5): "Make a new skill that teaches agents how we load test fixtures."; "Rename the `fixture-loader` skill to `loading-test-fixtures`." Near-miss (N1–N3): "Package the skills in this repo as a Claude Code plugin with a marketplace.json."; "Write an implementation plan for adding a timeout to `retry-budget`'s HTTP client."; "Write a CLAUDE.md for this repo."

- [ ] **Step 5: Write and commit the record's rules before any rep runs**

Create `specs/baseline/red-baseline-writing-skills-tests.md` with these sections:
- **Kit:** the paths, the sources, the versions and the competitor skills from Step 1. The arms per case: `old` is `SKILL.md` and the skill folder at the commit before that item's text, and `new` is the same at the item's text commit. Tasks 3–5 fill in the shas.
- **Cases** and **trigger prompts**, as Step 4 states them.
- **Reading rule, cases:** a rep passes when the grader marks every PASS part present (R3: the mechanical check). Descriptive, not scored: whether the rep Read the item's reference file (`micro-tests.md`, or `discovery.md` for T2 and R3), and for R3 whether it flagged `sniffing-csv-headers`.
- **RED, GREEN and null:** Open for plan review items 3 and 4, word for word.
- **Reading rule, triggers:** a rep loads when `triggers.py loads` says `load`, read from the stream as it stands. A trigger rep that stops on `--max-turns` or on its budget is a normal end, not a VOID. Floor: per model, `old` should-load loads in `full` (P1–P5, 15 reps) are at least 8. Below the floor the verdict is uninformative: stop and ask. No-loss bars, per model and condition: `new` should-load loads (15 reps) ≥ `old` − 2, and `new` near-miss loads (N1–N3, 9 reps) ≤ `old` + 1. Registered prediction (descriptive): in `cut150`, `new` ≥ `old` on P1–P3.
- **Codex cut (Task 6 Step 1):** pass when the candidate's Codex entry holds "micro-testing" whole and the old entry does not hold it.
- **VOID:** plan 105's T-rep reasons, the three closed Glob limits, a Bash call other than one in-repo `git mv`, and, for a trigger rep, a listing without `writing-skills` or without both competitors. For a trigger rep, the subtypes `error_max_turns` and `error_max_budget_usd` are not VOID reasons. A void rep does not count, and the next rep number replaces it. A third void in one arm stops the run.
- **Blind grading:** sheets show the sheet id and the case, never the arm. At a GREEN run, the grader grades the `old` and `new` sheets of the case together, freshly; the RED verdict comes from that mixed grading, and the record reports any change from Task 3–5's RED-only grading. Limit: a GREEN answer that names `micro-tests.md` shows its arm.
- **Spend stop:** Global Constraints' cap, projection and pair check, with a running-total table that starts at $0.00.

- [ ] **Step 6: Mutant step and commit**

Run the mutant step on `audit.py`, `triggers.py` and `sheets.py`. Each Glob limit has one mutant that reverts its fix, and its test must kill it. Run the commit gate. Commit: `test(baseline): add the writing-skills tests kit and its rules`. This commit comes before any probe or rep.

### Task 2: Probes, pilots and spend projection (not scored)

**Files:**
- Modify: `specs/baseline/red-baseline-writing-skills-tests.md` (Kit, Spend stop)

**Interfaces:**
- Consumes: Task 1's kit and record.
- Produces: the projection that Task 3's first pair needs; the confirmed `--setting-sources` value for trigger reps.

- [ ] **Step 1: Probes**

Run `probe_tools.sh` on each model, and add each cost to the running total. Expected: NO on probe lines 1–6 and 8. Line 7 (the user's identity) may read YES: the watch item "Account identity reaches the isolated micro-test runs" tracks it. Any other YES stops the run.

- [ ] **Step 2: Trigger pilot**

Run one trigger rep each of P1 and N1, arm `old`, condition `full`, on `claude-sonnet-5-5`, then P1 `cut150` on `claude-sonnet-5-5`, then P1 `full` on `claude-opus-5-5`. Expected: `triggers.py listing` shows `writing-skills`, `skill-development` and `skill-creator`, `audit.py` shows no finding, at least one P1 pilot rep loads `writing-skills`, and no pilot rep costs more than $0.15 (60% of its cap). Then run one listing probe per condition on `claude-sonnet-5-5`, at arm `old`: a rep whose prompt asks it to quote, word for word, the listing entry it sees for `writing-skills`, `skill-development` and `skill-creator`. Expected: in `full`, each whole description; in `cut150`, about 150 characters of each. A miss on any expectation means the condition is not real: fix the runner with a test, or stop and ask. If the listing lacks them, try `--setting-sources user,project,local` (plan 100's value), record which value works, and fix it in the runner with a test. If neither works, stop and ask.

- [ ] **Step 3: Case pilot**

Run `rep_tools.py place-copy HEAD` and `build_prompts.py HEAD pilot <scratch>/prompts-pilot`. Run one rep each of M1, T2 and R3 on `claude-sonnet-5-5`, and one R3 rep on `claude-opus-5-5`. Expected: `audit.py` shows no finding, and the R3 reps show a `git mv` that ran and an Edit of `.claude/settings.json` that succeeded. If that Edit is refused in both R3 reps, remove the reference from the fixture, record why, and commit the fixture change before any scored rep. Otherwise stop and ask. Empty the skill copy.

- [ ] **Step 4: Project the spend**

Projected total = spend so far + 30 × the mean Sonnet case pilot cost + 30 × the Opus case pilot cost + 96 × the mean Sonnet trigger pilot cost + 96 × the Opus trigger pilot cost. If the projection passes $42, stop and ask before any scored rep.

- [ ] **Step 5: Record and commit**

Add the probe answers, the pilot facts, the projection and the running total to the record. Run `privacy_sweep.py` on anything committed. Run the commit gate. Commit: `test(baseline): record the writing-skills tests kit's probes and pilots`.

### Task 3: Item 1, the micro-test method

**Files:**
- Create: `skills/writing-skills/references/micro-tests.md`
- Modify: `skills/writing-skills/SKILL.md:335` (micro-test step 1)
- Modify: `specs/baseline/red-baseline-writing-skills-tests.md` (M1 shas, results, verdict, spend)
- Create: `specs/baseline/red-baseline-writing-skills-tests/runs/M1/<arm>/<model>/` (scrubbed) and `.../prompts-M1-<arm>/`

**Interfaces:**
- Consumes: Task 1's kit, Task 2's projection.
- Produces: `references/micro-tests.md`, which Task 4's body and `NOTICE` name.

- [ ] **Step 1: RED run**

Record `git rev-parse HEAD` in the ledger as M1-OLD. Run the pair check. Build `prompts-M1-old`, place the copy at M1-OLD, and run M1 reps 1–5 on each model. Run `audit.py`, build the sheets, and have one grader grade them. Record the RED verdict per model. If the control is null (Open for plan review, item 3), stop, record, and ask.

- [ ] **Step 2: Write `references/micro-tests.md`**

Exact text:

```markdown
# Running a micro-test

Read this before the first rep of a micro-test or a pressure test. The five steps in SKILL.md say
what to run. This file says how to keep each rep clean and each verdict honest.

## Contents

- Isolate each rep
- Probe the isolation first
- Quarantine the scenario
- Register the rules before you read
- Score blind
- Run each model
- Cap the spend

## Isolate each rep

Start each rep in a new directory outside every repository. Give it no tools unless the test needs
them. Turn off user-level settings, instruction files and memory, so that the rep sees only the
context you planned. This is not full isolation: a rep can still know the user's name.

## Probe the isolation first

Before the first arm, run one probe rep as a pilot. Ask it what context it can see: instruction
files, memory, tools, other sessions and the user's name. An answer you did not plan for means the
setup leaks. Fix it before any scored rep.

## Quarantine the scenario

Keep every file that names the scenario or the pass rule out of each rep's reach: the spec, the
plan, the kit and earlier records. A rep that reads one is void.

## Register the rules before you read

Write down the PASS, FAIL and VOID rules, and commit them, before you read any reply. If a reply
shows a reading that the rules did not foresee, keep the registered verdict and report the counts
under both readings.

## Score blind

Grade from sheets that hide the arm. No file name, path, order or count on a sheet may show which
arm a reply came from. Unblind only after every sheet has its grade.

## Run each model

Run every arm on each model that will run the guidance, with the same number of reps on each. A
wording that binds one model can fail on another.

## Cap the spend

Before the first rep, set a spend cap and a stop rule, for example: stop when the running total plus
the next batch's worst case would pass the cap. Record each batch's cost as you go.

## In agent-skills

The newest committed kit under `specs/baseline/*/kit/` holds the exact runner flags, the isolation
probe and the scrub.
```

- [ ] **Step 3: Point step 1 at it**

In `SKILL.md`, replace `user message = a task that tempts the failure.` (the end of micro-test step 1) with `user message = a task that tempts the failure. Before the first rep, read [references/micro-tests.md](references/micro-tests.md): isolation, rules set first, blind scoring, models, spend.` Measure the body. Expected: 19,194.

- [ ] **Step 4: Check and commit the text**

Run `uv run python build/check_links.py` and `uv run --with pyyaml python build/check_conformance.py`. Expected: both pass; no finding for writing-skills. Run the commit gate. Commit: `feat(writing-skills): describe the micro-test method in full`. Record `git rev-parse HEAD` as M1-NEW.

- [ ] **Step 5: GREEN run, grade, verdict**

Run the pair check. Build `prompts-M1-new`, place the copy at M1-NEW, and run M1 reps 1–5 on each model. Grade the 20 `old` and `new` sheets together, freshly (the record's Blind grading section). Record the results table, the read counts and the verdict against Open for plan review item 4. If the mixed grading turns the RED verdict null, stop and ask. On a miss, stop and ask; change no wording. Run `check_scrub.py` and `privacy_sweep.py` on the runs folder, then the commit gate. Commit: `test(baseline): run the micro-test method cycle`.

### Task 4: Item 2, the trigger test

**Files:**
- Modify: `skills/writing-skills/references/discovery.md` (Contents; a new `### 6. Test triggering` at the end of the SDO section)
- Modify: `skills/writing-skills/references/claude-code.md` (a new `## Testing triggering` after `## The skill listing`)
- Modify: `skills/writing-skills/SKILL.md:15` (citation) and `:136-139` (the SDO pointer)
- Modify: the record (T2), and Create: `runs/T2/...`, `prompts-T2-<arm>/`

**Interfaces:**
- Consumes: Task 3's HEAD as T2-OLD.
- Produces: `discovery.md` § 6. Test triggering, the procedure that Task 6 follows.

- [ ] **Step 1: RED run**

As Task 3 Step 1, for T2, with T2-OLD = HEAD. Null → stop, record, ask.

- [ ] **Step 2: Add the procedure to `discovery.md`**

Add `  - 6. Test triggering` to the Contents list, after `  - 5. Cross-Referencing Other Skills`. Append at the end of the file:

```markdown
### 6. Test triggering

A description that reads well has not yet shown that it loads. Test a description change on loads:

1. Write three or more prompts that should load the skill, worded as users word them.
2. Write three or more near-miss prompts: tasks that belong to a neighboring skill, or to none.
3. Run each prompt in a fresh session with the old description, and again with the new one. Count
   the sessions that load the skill.
4. Report both counts for both descriptions: loads on the should-load prompts and loads on the near
   misses. A fix raises the first count and does not raise the second.
5. To check what the skill changes once it loads, run the should-load prompts with the skill on and
   again with it off, and compare the work.

This is the small check for one skill. For Claude Code, [claude-code.md](claude-code.md) says how to
turn a skill off and how to imitate a runtime that shortens descriptions.
```

- [ ] **Step 3: Add the Claude Code mechanics**

In `claude-code.md`, after the `## The skill listing` section, add:

```markdown
## Testing triggering

discovery.md's Test triggering step gives the procedure. In Claude Code:

- Turn a personal or project skill off with a `skillOverrides` entry of `off`. `skillOverrides` does
  not reach a plugin skill: use `claude plugin eval`, which repeats each run with no plugin loaded.
- To see how a shortened entry routes, as on a runtime that cuts descriptions, lower
  `skillListingMaxDescChars` for the test sessions.
- `/skill-doctor` shows each skill's cost and how often it is used.
```

- [ ] **Step 4: Cite and point**

In the `# cc-guide:` line, insert `skills.iterating` after `skills.progressive-disclosure`. In § Skill Discovery Optimization, replace:

```text
and bad descriptions, keyword coverage, naming, token efficiency and
cross-references to other skills.
```

with:

```text
and bad descriptions, keyword coverage, naming, token efficiency,
cross-references to other skills, and the trigger test to run before and after
a description change.
```

Measure the body. Expected: 19,258.

- [ ] **Step 5: Check and commit the text**

Run `check_links.py`, `check_conformance.py`, `uv run python build/cc_guide/cli.py lint` (expected: no line for writing-skills) and `uv run --with pyyaml python build/check_frontmatter.py`. Run the commit gate. Commit: `feat(writing-skills): add a trigger test`. Record T2-NEW.

- [ ] **Step 6: GREEN run, grade, verdict**

As Task 3 Step 5, for T2. Commit: `test(baseline): run the trigger test cycle`.

### Task 5: Item 10, the rename procedure

**Files:**
- Modify: `skills/writing-skills/references/discovery.md` (§ 3. Descriptive Naming)
- Modify: the record (R3), and Create: `runs/R3/...`, `prompts-R3-<arm>/`

**Interfaces:**
- Consumes: Task 4's HEAD as R3-OLD.

- [ ] **Step 1: RED run**

As Task 3 Step 1, for R3, with R3-OLD = HEAD. R3's verdict is mechanical; the grader still grades the sheets for the descriptive near-collision count. Null → stop, record, ask.

- [ ] **Step 2: Add the list**

In `discovery.md`, after the `### 3. Descriptive Naming` block's last bullet (`- ✅ `condition-based-waiting` not `async-test-helpers``), add:

```markdown

**Renaming a skill:**
1. Rename the folder and the `name` field together, in one change.
2. Search for the old name in skills, commands, agents, instruction files and settings, and update
   each bare-name reference.
3. Check the new name against the skill listing for a near collision: a name one word or one suffix
   away from another skill's.
4. In agent-skills, run the commit lints. The dependency-drift test, `check_provenance.py` and
   `check_conformance.py` find what the search missed.
```

The body does not change (19,258).

- [ ] **Step 3: Check and commit the text**

Run `check_links.py` and `check_conformance.py`. Run the commit gate. Commit: `feat(writing-skills): add a rename procedure`. Record R3-NEW.

- [ ] **Step 4: GREEN run, grade, verdict**

As Task 3 Step 5, for R3. If R3 misses its bar and no `new` rep read `discovery.md`, ask the owner Open for plan review item 6's question. Commit: `test(baseline): run the rename procedure cycle`.

### Task 6: Item 3b, front-load the description

**Files:**
- Modify: `skills/writing-skills/SKILL.md:3-8` (the description)
- Modify: the record (Codex cut, trigger results, verdict), and Create: `runs/triggers/` (scrubbed `triggers.py` tallies and per-rep load lines, no raw streams)

**Interfaces:**
- Consumes: Task 5's HEAD as TR-OLD; Task 4's procedure; Task 1's trigger runner.

**Brief note.** Spec item 3: "(b) changes routing, so it waits for item 2's trigger test." Claude Code lists the full description, so this test checks routing for no loss there; the gain is measured in Codex (Open for plan review item 10).

- [ ] **Step 1: Measure the Codex cut, old and new**

Build a scratch HOME under `~/.cache/agent-skills/scratch/plan107/codex/`: copy `~/.agents/skills` and `~/.codex/skills`, dereferenced, into it, and set `CODEX_HOME` to its `.codex`. From a directory outside every repository, run `HOME=<scratch> CODEX_HOME=<scratch>/.codex codex debug prompt-input` and save the Skills list. Check that the listed count equals a run with the real HOME. Then replace the copy's `writing-skills/SKILL.md` description with Step 2's text and run it again. Record the count, both writing-skills entries and their cut lengths. Expected: the old entry lacks "micro-testing" and the new one holds it whole. If the cut falls elsewhere, or the command needs a login or fails, stop and ask with what it printed.

- [ ] **Step 2: Reorder the description**

Record `git rev-parse HEAD` as TR-OLD. Replace the description's text (`SKILL.md:4-8`) with:

```text
  Use when creating, editing, renaming or testing a skill — fails to trigger, over-triggers,
  tightening a description, pressure-testing, micro-testing wording against a no-guidance baseline.
  Also when writing SKILL.md frontmatter (name/description limits), structuring references/ and
  scripts/, bulletproofing a discipline skill, or verifying a skill before deployment.
```

Run `check_frontmatter.py` and `check_conformance.py`. Expected: pass; the description is 368 characters and its first 150 hold "fails to trigger", "over-triggers", "tightening a description", "pressure-testing" and "micro-testing". Commit: `feat(writing-skills): front-load the testing triggers in the description`. Record TR-NEW. This test is a routing check, old against new, not a RED-first test, so the text may come before it.

- [ ] **Step 3: Run the trigger pairs**

For each model (`claude-sonnet-5-5`, then `claude-opus-5-5`) and condition (`full`, then `cut150`): run the pair check (48 reps × $0.25), then reps 1–3 of P1–P5 and N1–N3 on arm `old` at TR-OLD, then the same on arm `new` at TR-NEW. A stop never leaves an `old` cell without its `new` cell.

- [ ] **Step 4: Tally and verdict**

Run `triggers.py tally`. Record the per-prompt table (loads of 3) for each arm, model and condition, the floor, the no-loss bars, the prediction and the Codex result. The verdict passes when Step 1 passes, the floor holds and every no-loss bar holds. On a failure, revert the description commit with `git revert`, record, and ask. Run `check_scrub.py` and `privacy_sweep.py`, then the commit gate. Commit: `test(baseline): run the description trigger test`.

### Task 7: `NOTICE` and the files verify

**Files:**
- Modify: `NOTICE` (a new last bullet of the superpowers change list, after plan 105's)
- Modify, through `/cc-guide` only: `build/cc_guide/baseline.json`, and a fix that it lists in a covered file

- [ ] **Step 1: Add the plan 107 bullet**

Fetch, and compare `NOTICE` on `origin/main` with this branch; keep every line other plans added. Add this bullet last, wrapped like its neighbors, with the commit's date. Drop the sentence of any item that did not ship, and say instead that it was dropped and why.

```text
  - Plan 107 (<YYYY-MM-DD>) changed writing-skills, from
    specs/writing-skills-improvements.md. The changes are local, and no
    upstream text was taken. references/micro-tests.md is new: it says how
    to isolate reps, probe the isolation, quarantine the scenario, register
    the rules first, score blind, run each model and cap the spend.
    discovery.md gains a trigger test and a rename procedure, and
    claude-code.md the Claude Code mechanics of the trigger test. The
    description puts its testing triggers first. Items 1, 2 and 10 were
    tested RED first, and the description was checked with the trigger
    test (specs/baseline/red-baseline-writing-skills-tests.md), with this
    repository's own fixtures.
```

- [ ] **Step 2: Check and commit**

Run `uv run python build/check_provenance.py` and the commit gate. Commit: `docs(notice): record plan 107's writing-skills changes`.

- [ ] **Step 3: Owner gate: the files verify**

Stop and ask the owner to type `/cc-guide files skills/writing-skills/SKILL.md` in this execution session. The citation gained `skills.iterating`, which `build/cc_guide/baseline.json` has no hash for, `claude-code.md` gained Claude Code facts, and `micro-tests.md` joined the covered files. `/cc-guide` commits nothing, so wait for the owner's review of its diff.

- [ ] **Step 4: Commit the verify**

Run `uv run python build/cc_guide/cli.py lint` and the commit gate. Commit what `/cc-guide` changed: `chore(cc-guide): re-verify writing-skills after the trigger test`. If settle held the file, record the hold and its reason in the ledger for the completion gate.
