# Plan 107 micro-test runs: the writing-skills tests

> ⚠️ Quarantine this file during any micro-test of writing-skills. It names the cases, the trigger prompts
> and what each one scores, so a rep that reads this file is void.

This record belongs to plan 107 (`specs/plans/107-writing-skills-improvements.md`). The plan ships three
changes to `skills/writing-skills/`: the micro-test method (item 1), a trigger test (item 2) and a rename
procedure (item 10). Then it reorders the description (item 3b). Each of items 1, 2 and 10 gets a RED run
first: five reps of a case on the current skill, on each of two models. The text follows. A GREEN run then
compares the same case on the old and the new skill. The description is checked with the trigger test, old
against new.

Task 1 wrote the kit and the rules below, from Kit to Spend stop, and spent nothing. Its commit registers the
rules before any probe, pilot or rep runs. No reading is added after a rep is seen. If a reply shows a reading
that these rules did not foresee, the registered verdict stands, and the record reports the counts under both
readings. Later tasks fill in the shas, the results and the spend table.

## Kit

The kit is `specs/baseline/red-baseline-writing-skills-tests/kit/`. It copies files from two committed kits
and edits neither of them:

- plan 105's `specs/baseline/red-baseline-writing-skills-layout/kit/`: the case runner, its folder layout, the
  probe, the audit, the sheets and the identity scrub;
- plan 100's `specs/baseline/red-baseline-handoff-rerun/kit/run_rep.sh`: the layout of a rep HOME that holds
  skills (a HOME with the Keychains link, `.claude/` and a `settings.json`). The trigger runner copies its
  design and none of its text.

**Step 1 check.** Plan 105's kit is on this branch's base. `claude --version` printed `2.1.323 (Claude Code)`
and `codex --version` printed `codex-cli 0.167.2` when Task 1 ran. If a later task sees another version, it
runs the probes again first.

**The competitor skills.** The trigger test lists two plugin skills beside this repository's skills. They are
the plugin skills that also claim skill creation. The owner fixed which copy to use. Their text never enters
this repository. The record names each by plugin, skill and version only.

| Plugin | Skill | Version |
|---|---|---|
| `plugin-dev` | `skill-development` | `0.1.2` (the plugin manifest). The skill's own frontmatter says `0.1.0`. |
| `skill-creator` (the official plugin) | `skill-creator` | `7b7a29e0458e` (the cache folder name, which the plugin installer lists as the installed version after its update on 2026-11-23). The manifest has no version field. Task 1 named `65adb96f26de`, the version the installer listed earlier that day. That folder now has an orphan marker, so Task 2 used `7b7a29e0458e` (Deviation 10). |

`run_trigger_reps.sh` copies the two skill folders from the local plugin cache at run time. It takes their
source folders from the variables `WST_COMPETITOR_PLUGIN_DEV` and `WST_COMPETITOR_SKILL_CREATOR`, so no
committed file holds a path with a user part. The first batch writes one `competitors.txt` in the runs
root (the folder above `<prompt>`), the sha256 of each competitor's `SKILL.md`. Every later batch, of any
prompt, arm, condition or model, must match it, and the runner refuses a batch whose competitor differs.
`triggers.py tally` skips that one file and refuses any other stray name in the runs root.

| File | Source | Change |
|---|---|---|
| `common.sh` | plan 105's | Roots `/private/tmp/wst107` (cases) and `/private/tmp/wst107t` (triggers). Scratch `~/.cache/agent-skills/scratch/plan107/cases/` and `.../triggers/`. `tools_for_case`: an R3 rep also gets `Bash`, and `--allowedTools` limits it to `Bash(git mv *)`. The trigger runner shares the deny list, `make_folder`, `park` and `check_model`. The case cap is $1.50 and the trigger cap is $0.25. |
| `run_tool_reps.sh` | plan 105's | Plan 107's roots. The tools follow the case. |
| `run_trigger_reps.sh` | new, after plan 100's `run_rep.sh` | Section "The trigger runner" below. |
| `probe_tools.sh`, `isolation_probe.txt` | plan 105's | Plan 107's roots. The probe text is unchanged. |
| `rep_tools.py` | plan 105's | The skill root is `/private/tmp/wst107-skill`. `summarize` takes `--manifest -` (a trigger rep has no skill copy) and an optional `--condition`. For R3 it records `audit.r3_check` on the finished repository. |
| `audit.py` | plan 105's | The three Glob limits are closed, a Bash call is audited, the read check is now descriptive, R3 has a tree check, and a trigger rep is audited with a listing check (below). |
| `triggers.py`, `trigger_prompts.py` | new | The trigger reader and the eight prompts. |
| `sheets.py` | plan 105's | Cases M1, T2 and R3. R3 has no sheet. The bars are RED and GREEN. |
| `build_prompts.py`, `cases.py` | plan 105's | The prompts are `M1.txt`, `T2.txt` and `R3.txt`. `FRAME_T` names the case's tools. |
| `privacy_sweep.py`, `check_scrub.py`, `kit_identity.py` | plan 105's | Unchanged. |
| `fixtures/M1`, `fixtures/T2`, `fixtures/R3`, `fixtures/trigger` | new | Each case's project (Cases) and the trigger repository. |
| `test_wst_kit.py` | plan 105's tests, renamed, and the tests that Task 1 adds | 361 tests with a stub `claude` and no model (plan 105's kit has 191). The suite `writing-skills-tests-kit` in `build/suites.toml` runs them. |

**The arms.** `old` is `SKILL.md`'s body and the skill folder at the commit before an item's text. `new` is
the same at the commit of the item's text. Tasks 3 to 5 fill in the shas here. For item 1 (case M1) they are
M1-OLD `ec641509e2719e88370bf1dec12156de4bbed1e7`, M1-NEW `fe00dc0407670040879f514fecc57961be28132b` (attempt 1)
and M1-NEW2 `f87b1e76cf1f88bfc0888ca739b559f556327e3e` (attempt 2); see the Task 3 section. For item 2
(case T2) they are T2-OLD `02ebe3d067d29bf7a319336611d9387cc969780a`, T2-NEW `322ceabd8289581691c083dbd10e6f67076b39f0`
(attempt 1), T2-NEW2 `261e039efcb9cb10811b47e839e3513e8841689f` (attempt 2) and T2-NEW3
`bfe4da46806d5d88249278ade30fd980947f0cd5` (attempt 3); see the Task 4 section. For item 10 (case R3) there is
R3-OLD `068115951015ed8204f6f25fe89c7c6dd14d4a60` only, because the control was null and no `new` arm exists; see the
Task 5 section. The `pilot` arm of Task 2 is built from HEAD and is not scored. For item 3b (Task 6, the trigger test) TR-OLD is `32b296a2d4537599e57c924c86330b31a3a136de` and TR-NEW is
`063b8b823a72aa24cd305ab399fdb7314a7c15f4`; see the Task 6 section.

**The Glob limits, closed.** Plan 105's audit judged a Glob pattern by its literal part only. Its record named
three open reaches. Plan 107 closes each one, with a test and a mutant:

1. A `**` (or a run of wildcard segments) that starts at the rep folder, its `home/` or an ancestor of
   `home/Library` can list names under `home/Library/Keychains`, a link to the real Keychains folder. The
   audit now judges the search root, which is the literal part joined to the Glob `path` (or the repository).
   A search that can reach `home/Library` is a hit. A single `*` counts too, as in `*/Library/Keychains/*`.
2. A relative brace alternative under an absolute prefix was not joined to the prefix. The audit expands the
   braces, so each alternative is judged with the text before and after its group.
3. A brace alternative under a `$HOME`, `~` or `home/` prefix was not joined to it. The same expansion covers it.

More than 64 brace expansions is a hit. Grep is judged by its path only, because ripgrep does not follow the
link. The Bash audit is new: a Bash call is clean only when its command is one `git mv <src> <dst>` with plain
path words and both paths inside the rep's `repo/`.

**The trigger runner.** Each rep runs in a new session, in a new folder `WST_TROOT/rep<N>/` with `repo/`,
`home/` and `tmp/`. `env -i` keeps only `HOME`, `USER`, `LOGNAME`, `PATH`, `SHELL`, `TMPDIR`, `LANG` and the
two disable flags. The rep's `repo/` is a copy of `kit/fixtures/trigger/repo/`. `home/.claude/` holds
`git archive <ref> skills/`, the two competitors in `skills/`, and a `settings.json` with the deny list,
`"syncClaudeAiSkills": false`, `"skillListingBudgetFraction": 0.05` and, for `cut150`,
`"skillListingMaxDescChars": 150`. The flags are `--setting-sources user` (Task 2's pilot checks it),
`--strict-mcp-config`, `--no-session-persistence`, `--tools Read,Glob,Grep,Skill`, `--allowedTools` with the
same value, `--max-turns 3`, `--max-budget-usd 0.25` and `--output-format stream-json --verbose`.
`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` is set. The runner has no `--disable-slash-commands` and no `--settings`,
because either one would hide the listing under test.

**The commands.** Each one runs from the repository root, with `uv run python <kit>/<script>` for a Python
script. `<kit>` is the kit folder.

1. `rep_tools.py place-copy <ref>` puts `git archive <ref> skills/writing-skills` in
   `/private/tmp/wst107-skill/writing-skills/`. It refuses a root that holds anything.
2. `build_prompts.py <ref> <arm> <out-dir>` writes `M1.txt`, `T2.txt`, `R3.txt` and `MANIFEST.txt`.
3. `run_tool_reps.sh <prompt-dir> <case> <out-dir> <first> <last> <model>` runs case reps.
4. `run_trigger_reps.sh <ref> <arm> <condition> <prompt-id> <out-dir> <first> <last> <model>` runs trigger reps.
5. `audit.py <rep-dir> ...` prints each rep's audit and its VOID reasons. `triggers.py loads|listing|tally`
   reads trigger reps.
6. `sheets.py build <runs-root> <sheet-dir> <seed>` writes the sheets and the key. `sheets.py unblind
   <grades.tsv> <key.json>` unblinds the grades.
7. `check_scrub.py` and `privacy_sweep.py <path> ...` run before a commit of run output.

## Cases

Each case states that the earlier steps it needs are done, so the Iron Law (RED first) does not hold the
agent. No domain repeats the skill's examples, plan 72's cases, plan 105's cases or the new text of Tasks 3
to 5. A test pins that. Each case runs with the tools `Read,Glob,Grep,Edit,Write`. R3 also gets `Bash`, limited
to `git mv`.

| Case | Item | Conversation | Target | PASS (all parts) |
|---|---|---|---|---|
| M1 | 1 | Partner: "We want to change one line in `skills/changelog-entry/SKILL.md`. The proposal is in `specs/changelog-entry-wording.md`. Before I merge it, design the micro-test that will tell us whether the new wording works. Write the design to `specs/changelog-entry-microtest.md`. Don't run anything yet." | `specs/changelog-entry-microtest.md` | (a) the design isolates each rep from user-level settings, instruction files or memory, runs it in a fresh directory outside the repository, or runs it as a raw API call, beyond "a fresh context" or "a new subagent"; (b) it fixes the pass and fail rule before any reply is read; (c) it names at least two models to run each arm on |
| T2 | 2 | Partner: "Agents never load our `parquet-schema-check` skill, even when they're about to write a parquet file that breaks the schema. Fix it." | `skills/parquet-schema-check/SKILL.md` | the final message or a written file gives (a) at least three prompts that should load the skill and at least one that should not, and (b) says to run them, or ran them, with the old description and again with the new one, comparing loads |
| R3 | 10 | Partner: "Rename our `csv-dialect-sniff` skill to `sniffing-csv-dialects`." | the rep's repository | in the final tree: `skills/sniffing-csv-dialects/SKILL.md` exists with `name: sniffing-csv-dialects`, `skills/csv-dialect-sniff/` is gone, and `grep -rn --exclude-dir=.git csv-dialect-sniff .` prints nothing, untracked files included (mechanical) |

M1, T2 and R3 each add one line after the partner's words, in the form `[you, tools] ...`. It says that the
needed earlier step is done, so the Iron Law of the loaded skill does not hold the rep. M1's line also says
that the baseline for the old line is done. T2's line is exactly: `[you, tools] You ran the baseline earlier.
Your partner read the results. The skill is `skills/parquet-schema-check/SKILL.md`.` R3's line is
`[you, tools] You ran the baseline earlier. Your partner read the results.` T2's line holds no run counts,
because the old-description load count is what PASS (b) asks the rep to propose. The partner's words are the
plan's, word for word.

**Fixtures** (under `kit/fixtures/<case>/repo/`):

- M1: `skills/changelog-entry/SKILL.md` (a short technique skill) and `specs/changelog-entry-wording.md` (the
  old line, the proposed line and why).
- T2: `skills/parquet-schema-check/SKILL.md`, whose description is `Helps with parquet files.` with valid
  frontmatter, and a neighbor `skills/polars-lazy-tuning/SKILL.md` with a sound description.
- R3: `skills/csv-dialect-sniff/SKILL.md`, `skills/ingest-raw-files/SKILL.md`
  (`**REQUIRED SUB-SKILL:** Use csv-dialect-sniff`), `skills/sniffing-csv-headers/SKILL.md` (a near collision,
  scored descriptively), `commands/ingest.md` and `AGENTS.md`. Task 1 also had a `.claude/settings.json` with a
  `skillOverrides` entry for the old name. Task 2's pilot removed it (Deviation 11). The runner makes the
  repository and commits it once as the rep's BASE.
- Trigger: `skills/` with `table-diff`, `retry-budget`, `release-notes` and `fixture-loader`, one short skill
  each, and a `README.md`.

## Trigger prompts

`kit/trigger_prompts.py` holds the eight prompts.

- Should load, testing (P1 to P3):
  - P1: "The `table-diff` skill never gets picked up, even when I ask it to compare two tables. Can you sort that out?"
  - P2: "`retry-budget` keeps loading on every HTTP question, even unrelated ones. Make it stop."
  - P3: "I reworded the core rule in `release-notes`. Before I ship it, check that the new wording actually changes what agents do."
- Should load, core (P4 and P5):
  - P4: "Make a new skill that teaches agents how we load test fixtures."
  - P5: "Rename the `fixture-loader` skill to `loading-test-fixtures`."
- Near miss (N1 to N3):
  - N1: "Package the skills in this repo as a Claude Code plugin with a marketplace.json."
  - N2: "Write an implementation plan for adding a timeout to `retry-budget`'s HTTP client."
  - N3: "Write a CLAUDE.md for this repo."

## Reading rule, cases

A rep passes when the grader marks every PASS part present. For R3 the check is mechanical: `audit.r3_check`
walks the parked final tree and every file counts, untracked and ignored files and dotfiles included. Only
a folder named `.git` is skipped.

Descriptive, not scored:

- whether the rep Read the item's reference file (`micro-tests.md` for M1, `discovery.md` for T2 and R3). A
  Read that returned an error does not count, and a Read with `offset` or `limit` is marked partial;
- for R3, whether the rep flagged `sniffing-csv-headers` (its final message names it).

## RED, GREEN and null

These are the plan's Open for plan review items 3 and 4, word for word.

3. **RED shown.** On at least one model, the control passes at most 2 of 5. If the control passes 3 or more of 5 on both models, the item is null: stop, record, and ask. Default answer: drop that item's text (micro-test step 2).
4. **GREEN bar.** On each model where RED was shown: `new` ≥ 4 of 5, and `new` ≥ `old` + 2. On a miss, stop, record, and ask. The executor changes no wording without the owner.

`sheets.py unblind` computes both for each case and model.

## Reading rule, triggers

A rep loads when `triggers.py loads` says `load`. It reads the stream as it stands: any `tool_use` named
`Skill` whose `skill` input is exactly `writing-skills`, at any point, counts. A trigger rep that stops on
`--max-turns` or on its budget is a normal end, not a VOID.

- **Floor.** Per model, `old` should-load loads in `full` (P1 to P5, 15 reps) are at least 8. Below the floor
  the verdict is uninformative: stop and ask. `triggers.py tally` prints `verdict: uninformative (below the
  floor)` for a complete run with a floor entry below 8, even if a bar also fails.
- **No-loss bars,** per model and condition: `new` should-load loads (15 reps) ≥ `old` − 2, and `new`
  near-miss loads (N1 to N3, 9 reps) ≤ `old` + 1.
- **Registered prediction (descriptive).** In `cut150`, `new` ≥ `old` on P1 to P3.

`triggers.py tally` applies these rules to the counts. A full run has 3 reps in each of 64 cells (8 prompts,
2 arms, 2 conditions, 2 models).

### The narrow check

The owner registered this check on 2026-11-24, after the 15-rep test above failed its floor. The 15-rep test
stays as registered. Its `triggers.py tally` verdict stays `uninformative (below the floor)`: on Sonnet, the `old`
arm in `full` loaded `writing-skills` in 3 of 15 should-load reps (P3 only; P1, P2, P4 and P5 loaded nothing),
the same as the pilot.

These rules were written after the floor failed at Sonnet `old` in `full`. The 25 Sonnet `old` reps in `full`
already existed when the rules were written, and they were read first. Their loads of `writing-skills` were: P3
3 of 3 valid reps (rep 1 was void, and rep 4 replaced it), and N1, N2 and N3 0 of 3 each. The rules below reuse
those reps. The Sonnet `old` `full` result therefore did not test a prediction. It is the input that these rules
use.

- **Cells.** For each model (`claude-sonnet-5-5`, `claude-opus-5-5`) and condition (`full`, `cut150`): P3 with 5
  valid reps per arm (should-load), and N1, N2 and N3 with 3 valid reps each per arm (near-miss, 9 per arm).
  The arms are `old` (TR-OLD) and `new` (TR-NEW). A void rep is replaced, as in the VOID rule.
- **Informative cell.** A cell (one model and one condition) is informative only when `old` loads `writing-skills`
  in at least 3 of the 5 P3 reps. A cell that is not informative says so, and its `new` group is not run, because
  nothing can be lost there.
- **Bars,** on an informative cell: P3 loads of `new` are at least `old` - 1 (of 5), and near-miss loads of
  `writing-skills` in `new` are at most `old` + 1 (of 9).
- **Verdict.** The check passes when at least one `full` cell is informative and every informative cell meets
  both bars. It is uninformative when no `full` cell is informative. The description reorder stays on a pass. On
  a failed bar the controller asks the owner, and the default is to revert.
- **Reading.** The tally for this check is by hand, from `triggers.py loads` for each prompt. The record shows the
  table.

## Codex cut

Task 6 Step 1 measures this. The check passes when the candidate's Codex entry holds "micro-testing" whole
and the old entry does not hold it.

## VOID rule

A rep is void for any of these reasons. `audit.py` prints each one.

- Plan 105's T-rep reasons: a kit error, a stream line that is not JSON, a peer `origin` or a cross-session
  tool (V9), a second result record, no result record, a run error (a subtype other than `success`, or
  `is_error`), the budget subtype `error_max_budget_usd` for a case rep, a path audit hit and a skill copy
  that changed during the rep.
- The three closed Glob limits: a wildcard search that can reach `home/Library`, a brace alternative that
  joins an absolute, `$HOME`, `~` or `home/` prefix to a path outside the allowed roots, and more than 64
  brace expansions.
- A Bash call other than one `git mv` with both paths inside the rep's `repo/`.
- For a trigger rep, a listing without `writing-skills` or without both competitors.

For a trigger rep, the subtypes `error_max_turns` and `error_max_budget_usd` are not VOID reasons. A void
rep does not count, and the next rep number replaces it. A third void in one arm stops the run.

## Blind grading

Sheets show the sheet id and the case, never the arm. A path under the skill copy shows as
`<skill>/<basename>` in either arm. At a GREEN run, the grader grades the `old` and `new` sheets of the case
together, freshly. The RED verdict comes from that mixed grading, and the record reports any change from the
RED-only grading of Tasks 3 to 5.

Limit: a GREEN answer that names `micro-tests.md` shows its arm, because the file exists only in the `new`
arm. The sheet keeps the name and the record reports it.

## Spend stop

The cap for every probe, pilot and rep in this plan is $50. Per-rep `--max-budget-usd` is $1.50 for a case
rep (Tasks 3 to 5) and $0.25 for a trigger rep (Task 6). Task 2 projects the total. A projection above $42
stops the run before any scored rep. Before each pair, check: running total + reps in the pair × per-rep cap
≤ $50. A pair is a case's 5 `old` and 5 `new` reps on one model, or a trigger cell's `old` and `new` reps on
one model and condition. A pair that fails the check stops the run: report BLOCKED with this table.

| Step | Reps | Cost | Running total |
|---|---|---|---|
| Task 1 (no model call) | 0 | $0.00 | $0.00 |
| Task 2 Step 1: probe, `claude-sonnet-5-5` | 1 | $0.0073 | $0.0073 |
| Task 2 Step 1: probe, `claude-opus-5-5` | 1 | $0.0241 | $0.0314 |
| Task 2 Step 2: trigger pilot, P1 `old` `full`, Sonnet | 1 | $0.0647 | $0.0961 |
| Task 2 Step 2: trigger pilot, N1 `old` `full`, Sonnet | 1 | $0.0845 | $0.1806 |
| Task 2 Step 2: trigger pilot, P1 `old` `cut150`, Sonnet | 1 | $0.0262 | $0.2068 |
| Task 2 Step 2: trigger pilot, P1 `old` `full`, Opus | 1 | $0.1343 | $0.3412 |
| Task 2 Step 2: listing probe, `full`, Sonnet | 1 | $0.0806 | $0.4217 |
| Task 2 Step 2: listing probe, `cut150`, Sonnet | 1 | $0.0343 | $0.4561 |
| Task 2 Step 2: 4 more P1 `old` `full` pilots, Sonnet | 4 | $0.2374 | $0.6936 |
| Task 2 Step 2: 2 more P1 `old` `full` pilots, Opus | 2 | $0.2478 | $0.9414 |
| Task 2 Step 3: case pilot M1, T2 and R3, Sonnet | 3 | $0.2332 | $1.1745 |
| Task 2 Step 3: case pilot R3, Opus | 1 | $0.1746 | $1.3492 |
| Task 2 Step 3: case pilot R3 again after the fixture change, Sonnet | 1 | $0.0687 | $1.4179 |
| Task 3 Step 1: M1 `old`, Sonnet | 5 | $0.3920 | $1.8099 |
| Task 3 Step 1: M1 `old`, Opus | 5 | $0.9373 | $2.7473 |
| Task 3 Step 5, attempt 1: M1 `new` at M1-NEW, Sonnet | 5 | $0.5151 | $3.2623 |
| Task 3 Step 5, attempt 1: M1 `new` at M1-NEW, Opus | 5 | $1.1486 | $4.4109 |
| Task 3 Step 5, attempt 2: M1 `new` at M1-NEW2, Sonnet | 5 | $0.5067 | $4.9176 |
| Task 3 Step 5, attempt 2: M1 `new` at M1-NEW2, Opus | 5 | $1.1471 | $6.0647 |
| Task 4 Step 1: T2 `old`, Sonnet | 5 | $0.3504 | $6.4151 |
| Task 4 Step 1: T2 `old`, Opus | 5 | $0.9095 | $7.3246 |
| Task 4 Step 6, attempt 1: T2 `new` at T2-NEW, Sonnet | 5 | $0.3635 | $7.6881 |
| Task 4 Step 6, attempt 1: T2 `new` at T2-NEW, Opus | 5 | $0.9572 | $8.6453 |
| Task 4 Step 6, attempt 2: T2 `new` at T2-NEW2, Sonnet | 5 | $0.3757 | $9.0209 |
| Task 4 Step 6, attempt 2: T2 `new` at T2-NEW2, Opus | 5 | $0.9670 | $9.9880 |
| Task 4 Step 6, attempt 3: T2 `new` at T2-NEW3, Sonnet | 5 | $0.3795 | $10.3674 |
| Task 4 Step 6, attempt 3: T2 `new` at T2-NEW3, Opus | 5 | $1.0712 | $11.4386 |
| Task 5 Step 1: R3 `old`, Sonnet | 5 | $0.3025 | $11.7411 |
| Task 5 Step 1: R3 `old`, Opus | 5 | $0.7508 | $12.4919 |
| Task 6 Step 3: trigger test, Sonnet `full` `old`, P1 to P5 and N1 to N3 (3 reps each) | 24 | $1.6952 | $14.1871 |
| Task 6: P3 `old` `full` Sonnet, rep 4 (replaces void rep 1) | 1 | $0.1005 | $14.2876 |
| Task 6: aborted P3 `old` `full` Sonnet rep 5 (runner killed; stream kept in scratch, never scored) | 1 | $0.0876 | $14.3752 |
| Task 6, narrow check: P3 `old` `full` Sonnet, reps 5 and 6 (top-up) | 2 | $0.1575 | $14.5327 |
| Task 6, narrow check: Sonnet `full` `new` (P3 5 reps, N1 to N3 3 reps each) | 14 | $1.1061 | $15.6388 |
| Task 6, narrow check: Sonnet `cut150` `old` (with 2 replacements for voids) | 16 | $0.7507 | $16.3895 |
| Task 6, narrow check: Sonnet `cut150` `new` (stopped by the third void, checked at the end of the round) | 14 | $0.7058 | $17.0953 |

Running total after Task 2: $1.42 (about $1.4179, summed from unrounded costs). The projection below adds the
scored runs. Running total after Task 3: $6.0647 (summed from unrounded costs).
Running total after Task 4: $11.4386 (summed from unrounded costs).
Running total after Task 5: $12.4919 (summed from unrounded costs).
Running total after Task 6: $17.0953 (summed from unrounded costs).

## Task 2: probes, pilots and spend projection

Nothing here is scored. Raw output stays outside the repository. The Claude Code version was `2.1.323`, as in
Task 1. Task 2 changed no kit code. It removed one fixture file and changed the two test lines that pinned it
(Deviation 11); the suite still runs 361 tests, all passing.

**Probes (Step 1).** `probe_tools.sh` ran once on each model. Lines 1 to 6 and 8 read NO on both. Line 7 (the
user's identity) read NO on Sonnet and YES on Opus. The Opus quote was the account's email address, which this
record does not repeat. The watch item "Account identity reaches the isolated micro-test runs" tracks it. On line
6, Opus said NO and added that the session guidance names one slash command, so it counts as NO.

**Trigger pilot (Step 2).** The rep arm was `old` (skills from `HEAD`, where `skills/writing-skills` equals
`bc01afc`). The competitors were plugin-dev's `skill-development` `0.1.2` and the official `skill-creator`
`7b7a29e0458e`.

- `triggers.py listing` shows `writing-skills`, `skill-development` and `skill-creator` in every rep. `audit.py`
  shows no finding and no VOID in any rep. No trigger pilot rep cost more than $0.15 (the largest was $0.1343).
- The init record's `skills` field is a list of strings. `triggers.listing` accepts that shape. This confirms
  the second item that Task 1 left open.
- `--setting-sources user` loads the rep HOME's skills and its `settings.json`. The fallback value
  `user,project,local` was not needed. This confirms the first open item.
- Listing probes (Sonnet, `old`): in `full`, the rep quoted each whole description (413, 309 and 334 characters
  with the name). In `cut150`, it quoted about 150 characters of each, ending in an ellipsis. So both conditions
  are real. The third open item (`skillListingBudgetFraction 0.05` keeps every description whole) holds for
  these three skills. The probe cannot show it for all the other skills in the listing.
- The `Skill` tool works in a trigger rep: the N1 rep loaded `plugin-authoring`.
- Loads of `writing-skills`, as `triggers.py loads` counts them, in P1 `old` `full` pilot reps: Sonnet 0 of 5,
  Opus 0 of 3. P1 `old` `cut150` on Sonnet: 0 of 1. N1 `old` `full` on Sonnet: 0 of 1. No pilot rep loaded the
  skill. The first pilot expectation ("at least one P1 pilot rep loads `writing-skills`") was missed. The owner
  ruled that the P1 wording stays and that the extra reps are unscored pilots. Task 6's floor (`old` `full`
  should-load loads of at least 8 in 15 per model) is at risk. The controller decides what this means for
  Task 6. The reps read `table-diff` and `fixture-loader`, then tried an `Edit` that the trigger runner does not
  offer, and ended on `--max-turns 3` or with prose.

**Case pilot (Step 3).** `place-copy HEAD` and `build_prompts.py HEAD pilot` built the pilot arm. One rep each of
M1, T2 and R3 ran on Sonnet, and one R3 rep ran on Opus.

- `audit.py` shows no finding and no VOID in any of them. M1 did not read `micro-tests.md` (the pilot arm has
  none, as `HEAD` is the old text). T2 read `discovery.md`.
- Both first R3 reps ran `git mv skills/csv-dialect-sniff skills/sniffing-csv-dialects` and the `Bash` audit
  passed it. In both, the `Edit` of `.claude/settings.json` was refused (the stream's error: Claude Code
  "requested permissions to write" to the file and "you haven't granted it yet"). Both ended with a final tree
  where `r3_check` fails on that file only. The Task 2 rule for a refusal in both reps applied: remove the
  reference from the fixture and commit that change before any scored rep (Deviation 11).
- A new R3 rep on Sonnet, on the changed fixture, ran the same `git mv` and `r3_check` reported PASS.
  Risk for Task 5: the `old` arm (the current text) already passed R3 once, and the two first reps failed only on
  the refused `Edit`, not on a missed holder. So the R3 RED arm may be null (the control passes 3 or more of 5 on
  both models). The fixture now has no settings holder. The controller rules before Task 5's first pair, and a null
  stops Task 5 and asks the owner (Open for plan review item 3).
- R3 void rate in the pilot: 0 of 3 R3 reps were void (2 on Sonnet, 1 on Opus). A Bash call other than one in-repo
  `git mv` is the void rule, and none occurred.
- The skill copy was emptied after the case pilot.

**Spend projection (Step 4).** Projected total = spend so far + 30 x the mean Sonnet case pilot cost + 30 x the
Opus case pilot cost + 96 x the mean Sonnet trigger pilot cost + 96 x the mean Opus trigger pilot cost.

| Input | Reps | Mean | Factor | Part |
|---|---|---|---|---|
| Spend so far (probes, pilots, listing probes) | 19 runs | | | $1.4179 |
| Sonnet case pilot (M1, T2, R3 twice) | 4 | $0.0755 | 30 | $2.2642 |
| Opus case pilot (R3) | 1 | $0.1746 | 30 | $5.2391 |
| Sonnet trigger pilot (P1 x6 incl. `cut150`, N1 x1) | 7 | $0.0590 | 96 | $5.6641 |
| Opus trigger pilot (P1 x3) | 3 | $0.1274 | 96 | $12.2258 |
| **Projected total** | | | | **$26.81** |

The projection is below the $42 stop. It is also below the plan's expected $30 to $35, because the pilot reps
are cheap (each case pilot rep ended in 5 to 17 turns, and each trigger pilot rep in at most 4 turns). A scored
rep can cost more, and the per-pair check in Spend stop still applies.

## Task 3: item 1, the micro-test method (case M1)

Raw output, sheets, keys and grades stay outside the repository, in the scratch folder. Two things are committed.
The scrubbed rep folders are in `runs/M1/old/<model>/`, `runs/M1/new-attempt1/<model>/` and `runs/M1/new/<model>/`
(attempt 2). Each holds `final.diff` and `summary.json` for each rep. The prompt folders sit next to `runs/`:
`prompts-M1-old/`, `prompts-M1-new-attempt1/` and `prompts-M1-new/` (attempt 2, built at M1-NEW2). Each holds
`M1.txt`, `R3.txt`, `T2.txt` and `MANIFEST.txt`, and only `M1.txt` was sent. `check_scrub.py` printed PASS and
`privacy_sweep.py` found 0 hits in the runs folder and in the three prompt folders. The `stream` field of an
attempt-1 `summary.json` names the parked scratch path `cases-attempt1/`, not `cases/`, because attempt 2's streams
now sit under `cases/`. The Claude Code version was `2.1.323`.

**The arms.**

| Name | Commit | What it is |
|---|---|---|
| M1-OLD | `ec641509e2719e88370bf1dec12156de4bbed1e7` | `skills/writing-skills/` as at `main` `bc01afc`. `SKILL.md` body 19,053 characters. No `micro-tests.md`. |
| M1-NEW | `fe00dc0407670040879f514fecc57961be28132b` | Attempt 1. Adds `references/micro-tests.md` and the pointer in micro-test step 1. Body 19,194 characters. |
| M1-NEW2 | `f87b1e76cf1f88bfc0888ca739b559f556327e3e` | Attempt 2. M1-NEW plus one sentence in `micro-tests.md`, section "Run each model" (below). Body still 19,194 characters. |

**RED (Step 1).** Five `old` reps on each model, graded alone by one Opus agent with no key. No rep was void.

| Model | `old` PASS | RED |
|---|---|---|
| `claude-sonnet-5-5` | 0 of 5 | shown |
| `claude-opus-5-5` | 0 of 5 | shown |

Every `old` rep failed part (c): it named no second model, and left one model for every arm. Three of the ten
also failed part (a). RED is shown on both models, so item 1 is not null (Open for plan review item 3).

**GREEN, attempt 1 (Step 5, at M1-NEW).** The grader graded the 10 `old` and the 10 `new` sheets together, freshly.

| Model | `old` PASS | `new` PASS | RED | GREEN |
|---|---|---|---|---|
| `claude-sonnet-5-5` | 0 of 5 | 2 of 5 | shown | missed |
| `claude-opus-5-5` | 0 of 5 | 0 of 5 | shown | missed |

GREEN missed, so the run stopped and the executor changed no wording (Open for plan review item 4). The graders'
notes give the reason. All 8 failing `new` reps failed part (c): the design left the model list to the partner
and named none. Seven of those 8 held parts (a) and (b). The eighth (Sonnet rep 5) also failed part (a), because
it did not state that the directory was outside the repository. The two passing reps (Sonnet reps 2 and 4) named
Opus, Sonnet and Haiku. All 10 `new` reps read `micro-tests.md`, and the grading of `old` did not change.

**The owner's ruling (2026-11-23).** Tighten the model rule, and run the `new` arm again, with the `old` reps kept.
The owner approved this sentence, to go at the end of the section "Run each model" in `micro-tests.md`, and
nothing else:

> Name at least two models in the design itself. If the user has not said which, choose two and say so; do not leave the choice open.

This is M1-NEW2. Attempt 1's reps, sheets, key and grades stay in the scratch folder. Attempt 1's `new` reps are
committed under `runs/M1/new-attempt1/`.

**GREEN, attempt 2 (at M1-NEW2).** Five new `new` reps on each model. The grader graded the 10 `old` and the
10 attempt-2 `new` sheets together, freshly. No rep was void.

| Model | `old` PASS | `new` PASS | RED | GREEN |
|---|---|---|---|---|
| `claude-sonnet-5-5` | 0 of 5 | 5 of 5 | shown | met |
| `claude-opus-5-5` | 0 of 5 | 5 of 5 | shown | met |

GREEN is met on both models: `new` is at least 4 of 5 and at least `old` + 2 (Open for plan review item 4). The
mixed grading did not change the RED verdict. `old` was 0 of 5 on both models in the RED-only grading, in
attempt 1's mixed grading and in attempt 2's mixed grading.

**Reads of `micro-tests.md`** (descriptive, from `audit.py`; no rep Read it partially or with an error). None of the
10 `old` reps read it, because the `old` arm has no such file. All 10 `new` reps read it in attempt 1, and all 10
in attempt 2. The Sonnet reps read it at tool call 1 (two reps in attempt 1, one in attempt 2) or at call 3. Every
Opus rep read it at call 3.

**Every scored rep.** Costs are `total_cost_usd` of each rep. The running total starts at $1.4179 (after Task 2) and
is summed from unrounded costs.

*`old` reps (RED run).* The three grade columns are the three grading rounds.

| Model | Rep | RED-only grade | Mixed grade, attempt 1 | Mixed grade, attempt 2 | Read `micro-tests.md` | Cost (USD) | Running total (USD) | Grader note (RED-only round) |
|---|---|---|---|---|---|---|---|---|
| claude-sonnet-5-5 | 1 | FAIL | FAIL | FAIL | no | 0.0754 | 1.4933 | (c) fails: same model for every arm. (a) also missing: only a single-shot call or subagent. |
| claude-sonnet-5-5 | 2 | FAIL | FAIL | FAIL | no | 0.0783 | 1.5716 | (c) fails: same model and settings in every arm, no second model named. |
| claude-sonnet-5-5 | 3 | FAIL | FAIL | FAIL | no | 0.0710 | 1.6426 | (c) fails: no model named. (a) missing: fresh single-shot call only. (b) weak: threshold left to user. |
| claude-sonnet-5-5 | 4 | FAIL | FAIL | FAIL | no | 0.0868 | 1.7294 | (c) fails: no model named at all. |
| claude-sonnet-5-5 | 5 | FAIL | FAIL | FAIL | no | 0.0806 | 1.8099 | (c) fails: no model named. (a) also missing: a single-shot subagent is fine. |
| claude-opus-5-5 | 1 | FAIL | FAIL | FAIL | no | 0.2224 | 2.0324 | (c) fails: same model and settings for all arms, no second model named. |
| claude-opus-5-5 | 2 | FAIL | FAIL | FAIL | no | 0.1884 | 2.2208 | (c) fails: same model and settings as the baseline run, one model only. |
| claude-opus-5-5 | 3 | FAIL | FAIL | FAIL | no | 0.1815 | 2.4022 | (c) fails: same model and settings for every arm, no second model named. |
| claude-opus-5-5 | 4 | FAIL | FAIL | FAIL | no | 0.1747 | 2.5769 | (c) fails: same model and temperature as the baseline, one model only. |
| claude-opus-5-5 | 5 | FAIL | FAIL | FAIL | no | 0.1703 | 2.7473 | (c) fails: same model and settings for all arms, no second model named. |

*Attempt 1, `new` reps (M1-NEW).*

| Model | Rep | Grade | Read `micro-tests.md` | Cost (USD) | Running total (USD) | Grader note |
|---|---|---|---|---|---|---|
| claude-sonnet-5-5 | 1 | FAIL | yes | 0.1106 | 2.8579 | (a) and (b) hold; (c) fails: asks which models, names none. |
| claude-sonnet-5-5 | 2 | PASS | yes | 0.1066 | 2.9645 | Empty dir outside repo with settings and memory off, rules registered first, names opus, sonnet and haiku 5-5. |
| claude-sonnet-5-5 | 3 | FAIL | yes | 0.1022 | 3.0667 | (a) and (b) hold; (c) fails: asks partner which models, names none. |
| claude-sonnet-5-5 | 4 | PASS | yes | 0.1024 | 3.1691 | Dir outside repos with settings and memory off, rules committed first, names sonnet, opus and haiku 5-5. |
| claude-sonnet-5-5 | 5 | FAIL | yes | 0.0932 | 3.2623 | (c) fails: model list left for partner, none named; (a) directory not stated outside repo. |
| claude-opus-5-5 | 1 | FAIL | yes | 0.2262 | 3.4885 | (a) and (b) hold; (c) fails: models left open, none named. |
| claude-opus-5-5 | 2 | FAIL | yes | 0.2296 | 3.7181 | (a) and (b) hold; (c) fails: partner to name models, none named. |
| claude-opus-5-5 | 3 | FAIL | yes | 0.2234 | 3.9415 | (a) and (b) hold; (c) fails: model list left for partner, none named. |
| claude-opus-5-5 | 4 | FAIL | yes | 0.2411 | 4.1826 | (a) and (b) hold; (c) fails: models left to fill in, falls back to one baseline model. |
| claude-opus-5-5 | 5 | FAIL | yes | 0.2283 | 4.4109 | (a) and (b) hold; (c) fails: model list left for partner to confirm, none named. |

*Attempt 2, `new` reps (M1-NEW2).*

| Model | Rep | Grade | Read `micro-tests.md` | Cost (USD) | Running total (USD) | Grader note |
|---|---|---|---|---|---|---|
| claude-sonnet-5-5 | 1 | PASS | yes | 0.1088 | 4.5197 | (a) empty dir outside repos, settings/instructions/memory off; (b) registered rules; (c) Sonnet and Haiku named. |
| claude-sonnet-5-5 | 2 | PASS | yes | 0.0925 | 4.6122 | (a) empty dir outside repos, no settings/memory; (b) rules committed before reading; (c) Haiku and Sonnet named. |
| claude-sonnet-5-5 | 3 | PASS | yes | 0.0976 | 4.7098 | (a) empty dir outside repos, settings/instructions/memory off; (b) rules registered first; (c) Sonnet and Haiku named. |
| claude-sonnet-5-5 | 4 | PASS | yes | 0.0994 | 4.8092 | (a) empty dir outside repos, settings/instructions/memory off; (b) rules committed first; (c) Sonnet and Haiku named. |
| claude-sonnet-5-5 | 5 | PASS | yes | 0.1084 | 4.9176 | (a) empty dir outside repo, no settings/instructions/memory; (b) rules committed first; (c) Sonnet and Haiku named. |
| claude-opus-5-5 | 1 | PASS | yes | 0.2221 | 5.1397 | (a) empty dir outside repos, no settings/instructions/memory; (b) rules registered by commit; (c) Opus and Sonnet named. |
| claude-opus-5-5 | 2 | PASS | yes | 0.2297 | 5.3694 | (a) empty dir outside repos, no settings/instructions/memory; (b) rules registered before reading; (c) Opus and Sonnet named. |
| claude-opus-5-5 | 3 | PASS | yes | 0.2184 | 5.5878 | (a) raw API, new dir outside repos, settings/instructions/memory off; (b) rules registered; (c) Opus and Sonnet named. |
| claude-opus-5-5 | 4 | PASS | yes | 0.2191 | 5.8068 | (a) empty dir outside repos, settings/instructions/memory off; (b) rules committed first; (c) Opus and Sonnet named. |
| claude-opus-5-5 | 5 | PASS | yes | 0.2579 | 6.0647 | (a) empty dir outside repos, no settings/instructions/memory; (b) rules committed first; (c) Opus and Sonnet named. |

**Spend by batch.** The running total is $6.0647 at the end of Task 3, below the $50 cap. Each attempt's run
script looped over both models with no gate between them. So one pair check ran for each attempt, before its Sonnet
batch, with the true running total: $1.4179 + 5 x $1.50 = $8.92 for `old`, $2.7473 + 5 x $1.50 = $10.25 for attempt 1
and $4.4109 + 5 x $1.50 = $11.91 for attempt 2. No check ran before an Opus batch. Its bound was computed afterwards,
from the running total before that batch: $9.31 for `old` ($1.8099), $10.76 for attempt 1 ($3.2623) and $12.42 for
attempt 2 ($4.9176). Every bound is far below the $50 cap.

| Batch | Reps | Cost | Running total |
|---|---|---|---|
| M1 `old`, Sonnet | 5 | $0.3920 | $1.8099 |
| M1 `old`, Opus | 5 | $0.9373 | $2.7473 |
| M1 `new` at M1-NEW (attempt 1), Sonnet | 5 | $0.5151 | $3.2623 |
| M1 `new` at M1-NEW (attempt 1), Opus | 5 | $1.1486 | $4.4109 |
| M1 `new` at M1-NEW2 (attempt 2), Sonnet | 5 | $0.5067 | $4.9176 |
| M1 `new` at M1-NEW2 (attempt 2), Opus | 5 | $1.1471 | $6.0647 |

**Limits.**

1. *Blind scoring is not fully blind.* A sheet that names `micro-tests.md` shows its arm, because the file exists only
   in the `new` arm. In attempt 1, 4 of the 20 sheets named it. In attempt 2, 1 of the 20 did. The graders also
   marked a hint on many sheets. A hint mark means the grader saw a clue about the arm or the model. Counts, by
   arm, from the keys: the RED-only round marked 7 of the 10 `old` sheets. Attempt 1's mixed round marked 12 of 20
   (7 `old`, 5 `new`). Attempt 2's mixed round marked 16 of 20 (7 `old`, 9 `new`). The verdicts do not turn on a
   hint: every `old` rep failed in all three rounds, and an attempt-2 `new` rep passed when it named two models,
   which is a visible fact of the design.
2. *The added sentence repeats part (c) of the PASS rule.* Attempt 2's GREEN was met after a wording change that
   attempt 1's miss guided, and the sentence asks for exactly what part (c) scores. The owner approved the sentence
   (the ruling above). The record reports both attempts, and a reader should weigh attempt 2 as a result that the
   first miss shaped.
3. *Three grading rounds, one agent each.* The graders were Opus agents with no key: the RED-only grading of the 10
   `old` sheets, attempt 1's mixed grading of 20 sheets, and attempt 2's mixed grading of 20 sheets. The `old`
   sheets were graded three times, each time freshly, with new ids.

## Task 4: item 2, the trigger test (case T2)

Raw output, sheets, keys and grades stay outside the repository, in the scratch folder. Two things are committed.
The scrubbed rep folders are in `runs/T2/old/<model>/`, `runs/T2/new-attempt1/<model>/`,
`runs/T2/new-attempt2/<model>/` and `runs/T2/new/<model>/` (attempt 3). Each holds `final.diff` and `summary.json`
for each rep. The prompt folders sit next to `runs/`: `prompts-T2-old/`, `prompts-T2-new-attempt1/`,
`prompts-T2-new-attempt2/` (scratch name `prompts-T2-new2`) and `prompts-T2-new/` (attempt 3, scratch name
`prompts-T2-new3`). Each holds `M1.txt`, `R3.txt`, `T2.txt` and `MANIFEST.txt`, and only `T2.txt` was sent.
`check_scrub.py` printed PASS and `privacy_sweep.py` found 0 hits in the runs folder and in the four prompt
folders. The `stream` field of a `summary.json` in `new-attempt1/` and `new-attempt2/` names the parked scratch path
`cases-attempt1/` or `cases-attempt2/`, not `cases/`, because attempt 3's streams now sit under `cases/`; the
`<REAL-HOME>` placeholder stays. The Claude Code version was `2.1.323`.

**The arms.**

| Name | Commit | What it is |
|---|---|---|
| T2-OLD | `02ebe3d067d29bf7a319336611d9387cc969780a` | `skills/writing-skills/` at the head of Task 3. `SKILL.md` body 19,194 characters. No "Test triggering" step. |
| T2-NEW | `322ceabd8289581691c083dbd10e6f67076b39f0` | Attempt 1. Adds `discovery.md` section 6 (Test triggering), the `claude-code.md` section "Testing triggering", the `skills.iterating` citation and the pointer in SDO. Body 19,258 characters. |
| T2-NEW2 | `261e039efcb9cb10811b47e839e3513e8841689f` | Attempt 2. T2-NEW plus one sentence in step 2 of section 6 (below). Body still 19,258. |
| T2-NEW3 | `bfe4da46806d5d88249278ade30fd980947f0cd5` | Attempt 3. T2-NEW2 plus a second sentence in step 2 of section 6 (below). Body still 19,258. |

T2-OLD already holds `discovery.md`, so the `old` reps could read it too (they did, see the reads below).

**RED (Step 1).** Five `old` reps on each model, graded alone by one Opus agent with no key. No rep was void.

| Model | `old` PASS | RED |
|---|---|---|
| `claude-sonnet-5-5` | 0 of 5 | shown |
| `claude-opus-5-5` | 0 of 5 | shown |

Every `old` rep failed part (a): it gave no prompt set (no three should-load prompts and no should-not prompt), or
only one vague should-not task. Part (b) was moot. RED is shown on both models, so item 2 is not null (Open for plan
review item 3). The RED grades carry the hint mark in 6 of the 10 notes.

**GREEN, attempt 1 (Step 6, at T2-NEW).** The grader graded the 10 `old` and the 10 `new` sheets together, freshly.

| Model | `old` PASS | `new` PASS | RED | GREEN |
|---|---|---|---|---|
| `claude-sonnet-5-5` | 0 of 5 | 0 of 5 | shown | missed |
| `claude-opus-5-5` | 0 of 5 | 3 of 5 | shown | missed |

The graders' notes give the reason. In the 7 failing `new` reps, the answer used the new step's shape (a plan to
write prompts and run them old and new), and failed part (a): it listed no concrete prompt set, or only one
should-load prompt, with the near misses as categories. The 3 passing reps (Opus reps 2, 4 and 5) gave 3 or 4
should-load prompts and 3 near-miss prompts and said to run each old and new. All 10 `new` reps read `discovery.md`.

**The owner's ruling after attempt 1 (2026-11-23).** Add one sentence and run the `new` arm again, with the `old`
reps kept. The owner approved this sentence, to go after step 2 of section 6 in `discovery.md` as a continuation of
that step, and nothing else:

> List every prompt in full. A plan that only says to write prompts has no prompts yet.

This is T2-NEW2. Attempt 1's reps, sheets, key and grades stay in the scratch folder. Attempt 1's `new` reps are
committed under `runs/T2/new-attempt1/`.

**GREEN, attempt 2 (at T2-NEW2).** Five new `new` reps on each model, graded with the 10 `old` sheets, freshly.
No rep was void.

| Model | `old` PASS | `new` PASS | RED | GREEN |
|---|---|---|---|---|
| `claude-sonnet-5-5` | 0 of 5 | 0 of 5 | shown | missed |
| `claude-opus-5-5` | 0 of 5 | 5 of 5 | shown | met on Opus |

On Sonnet, the notes say that in 4 of 5 reps the rep fixed the description, then repeated the step as work for the
partner ("write 3+ prompts, run them old and new") without writing the prompts. The fifth (rep 1) gave one
should-load prompt. All 5 Opus reps gave 3 to 5 should-load and 3 to 4 near-miss prompts.

**The owner's ruling after attempt 2 (2026-11-24).** Add one more sentence and run the `new` arm again. The owner
said this is the last retry. The owner approved this sentence, as a continuation line right after the first one, and
nothing else:

> Write them yourself, in your answer or in a file; do not leave them for the user.

This is T2-NEW3. Attempt 2's reps are committed under `runs/T2/new-attempt2/`.

**GREEN, attempt 3 (at T2-NEW3).** Five new `new` reps on each model, graded with the 10 `old` sheets, freshly. No
rep was void.

| Model | `old` PASS | `new` PASS | RED | GREEN |
|---|---|---|---|---|
| `claude-sonnet-5-5` | 0 of 5 | 3 of 5 | shown | missed |
| `claude-opus-5-5` | 0 of 5 | 5 of 5 | shown | met |

GREEN on Sonnet needs `new` at least 4 of 5 and at least `old` + 2 (Open for plan review item 4). Sonnet passed 3 of
5, so it missed the bar by one rep. In Sonnet reps 3 and 5 the rep described the old-versus-new test but wrote no
prompts (rep 3 said so; rep 5 gave no should-load prompt and one near miss). On Opus, every rep wrote 4 to 5
should-load and 4 to 5 near-miss prompts into a file and said to run each old and new.

**The mixed grading did not change the RED verdict.** `old` was 0 of 5 on both models in the RED-only grading and in
the mixed gradings of attempts 1, 2 and 3.

**Verdict.** RED is shown on both models. GREEN is met on Opus (attempt 3: 5 of 5; also attempt 2) and missed on
Sonnet (3 of 5 against a bar of 4, after 0 and 0 in attempts 1 and 2). The owner's limit was that the third attempt
was the last, and the owner said a third miss ships as measured. So the text stays as T2-NEW3 and ships with a
known gap: a Sonnet run still often describes the test and leaves the prompts for the partner. The plan-completion
gate sees this gap.

**Reads of `discovery.md`** (descriptive, from `audit.py`; no rep Read it partially or with an error). All 10 `old`
reps read it, because the `old` copy already holds the file. All 10 `new` reps read it in attempt 1, all 10 in
attempt 2 and all 10 in attempt 3. Each rep read it at tool call 2.

**Every scored rep.** Costs are `total_cost_usd` of each rep. The running total starts at $6.0647 (after Task 3) and
is summed from unrounded costs. A hint mark means the grader saw a clue about the arm or the model.

*`old` reps (RED run).* The four grade columns are the four grading rounds.

| Model | Rep | RED-only grade | Mixed, attempt 1 | Mixed, attempt 2 | Mixed, attempt 3 | Read `discovery.md` | Cost (USD) | Running total (USD) | Hint marks (4 rounds) | Grader note (RED-only round) |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-sonnet-5-5 | 1 | FAIL | FAIL | FAIL | FAIL | yes | 0.0708 | 6.1355 | YYYY | Part (a) fails: no should-load or should-not prompts written; (b) moot without a prompt set. |
| claude-sonnet-5-5 | 2 | FAIL | FAIL | FAIL | FAIL | yes | 0.0722 | 6.2077 | YYYY | Part (a) fails: no should-load or should-not prompts given; (b) moot without a prompt set. |
| claude-sonnet-5-5 | 3 | FAIL | FAIL | FAIL | FAIL | yes | 0.0697 | 6.2775 | YYYY | Part (a) fails: no trigger prompt set, only the baseline scenario; (b) moot without a prompt set. |
| claude-sonnet-5-5 | 4 | FAIL | FAIL | FAIL | FAIL | yes | 0.0665 | 6.3440 | nnnn | Part (a) fails: only suggests rephrased reps, gives no concrete prompts; (b) moot without a prompt set. |
| claude-sonnet-5-5 | 5 | FAIL | FAIL | FAIL | FAIL | yes | 0.0712 | 6.4151 | YYYY | Part (a) fails: no prompt set given, only the baseline scenario; (b) moot without a prompt set. |
| claude-opus-5-5 | 1 | FAIL | FAIL | FAIL | FAIL | yes | 0.1716 | 6.5867 | YYYY | Part (a) fails: no should-load or should-not prompts given; (b) moot without a prompt set. |
| claude-opus-5-5 | 2 | FAIL | FAIL | FAIL | FAIL | yes | 0.1919 | 6.7786 | nnnn | Part (a) fails: no should-load or should-not prompts listed; (b) moot without a prompt set. |
| claude-opus-5-5 | 3 | FAIL | FAIL | FAIL | FAIL | yes | 0.1751 | 6.9537 | YYYY | Part (a) fails: no three should-load prompts or a should-not prompt; (b) moot without a prompt set. |
| claude-opus-5-5 | 4 | FAIL | FAIL | FAIL | FAIL | yes | 0.1895 | 7.1432 | nnnn | Part (a) fails: one vague should-not task (Polars tuning), no should-load prompts; (b) moot. |
| claude-opus-5-5 | 5 | FAIL | FAIL | FAIL | FAIL | yes | 0.1814 | 7.3246 | nnnn | Part (a) fails: no three should-load prompts or a should-not prompt listed; (b) moot without a prompt set. |

*Attempt 1, `new` reps (T2-NEW).*

| Model | Rep | Grade | Read `discovery.md` | Cost (USD) | Running total (USD) | Hint mark | Grader note |
|---|---|---|---|---|---|---|---|
| claude-sonnet-5-5 | 1 | FAIL | yes | 0.0734 | 7.3980 | yes | (a) fails: no concrete prompts given, only describes the 3+ and 3+ test. |
| claude-sonnet-5-5 | 2 | FAIL | yes | 0.0723 | 7.4703 | yes | (a) fails: only one concrete should-load prompt given, near misses as categories. |
| claude-sonnet-5-5 | 3 | FAIL | yes | 0.0775 | 7.5478 | yes | (a) fails: no concrete should-load prompts, near misses only as categories. |
| claude-sonnet-5-5 | 4 | FAIL | yes | 0.0698 | 7.6175 | yes | (a) fails: no concrete prompts given, only mentions should-load and near-miss test in general. |
| claude-sonnet-5-5 | 5 | FAIL | yes | 0.0705 | 7.6881 | yes | (a) fails: no concrete prompts, only instructs writing 3+ should-load and near-miss prompts. |
| claude-opus-5-5 | 1 | FAIL | yes | 0.1878 | 7.8759 | yes | (a) fails: only one concrete should-load prompt given (two near misses). |
| claude-opus-5-5 | 2 | PASS | yes | 0.1949 | 8.0708 | no | Gives 4 should-load and 3 shouldnt-load prompts, says run each with old then new description and count loads. |
| claude-opus-5-5 | 3 | FAIL | yes | 0.1801 | 8.2509 | yes | (a) fails: one example should-load prompt, near misses only as categories, tells user to write them. |
| claude-opus-5-5 | 4 | PASS | yes | 0.2009 | 8.4519 | no | Gives 3 should-load and 3 near-miss prompts, says run each with old and new description and count loads. |
| claude-opus-5-5 | 5 | PASS | yes | 0.1934 | 8.6453 | yes | Gives 4 should-load and 3 near-miss prompts, says run each with old and new description and count loads. |

*Attempt 2, `new` reps (T2-NEW2).*

| Model | Rep | Grade | Read `discovery.md` | Cost (USD) | Running total (USD) | Hint mark | Grader note |
|---|---|---|---|---|---|---|---|
| claude-sonnet-5-5 | 1 | FAIL | yes | 0.0812 | 8.7264 | no | Part (a) missing: only one should-load prompt given, three needed. |
| claude-sonnet-5-5 | 2 | FAIL | yes | 0.0727 | 8.7991 | yes | Part (a) missing: says three prompts are needed but gives none. |
| claude-sonnet-5-5 | 3 | FAIL | yes | 0.0811 | 8.8803 | no | Part (a) missing: describes 3+ prompts but writes none. |
| claude-sonnet-5-5 | 4 | FAIL | yes | 0.0699 | 8.9502 | no | Part (a) missing: says write 3+ prompts but gives none. |
| claude-sonnet-5-5 | 5 | FAIL | yes | 0.0707 | 9.0209 | yes | Part (a) missing: says write 3+ prompts but gives none. |
| claude-opus-5-5 | 1 | PASS | yes | 0.2098 | 9.2307 | yes | Written file gives 5 should-load and 4 near-miss prompts; says run each with old and new description and compare counts. |
| claude-opus-5-5 | 2 | PASS | yes | 0.1768 | 9.4075 | no | Gives 3 should-load and 3 near-miss prompts; run with old and new description and count loads. |
| claude-opus-5-5 | 3 | PASS | yes | 0.1972 | 9.6048 | no | Gives 4 should-load and 3 near-miss prompts; run with old and new description and count loads. |
| claude-opus-5-5 | 4 | PASS | yes | 0.1777 | 9.7825 | yes | Gives 4 should-load and 3 should-not prompts; run with old and new description and count loads. |
| claude-opus-5-5 | 5 | PASS | yes | 0.2055 | 9.9880 | no | Gives 4 should-load and 3 should-not prompts; run with old then new description and count loads. |

*Attempt 3, `new` reps (T2-NEW3).*

| Model | Rep | Grade | Read `discovery.md` | Cost (USD) | Running total (USD) | Hint mark | Grader note |
|---|---|---|---|---|---|---|---|
| claude-sonnet-5-5 | 1 | PASS | yes | 0.0744 | 10.0624 | yes | Message gives 3 should-load and 3 should-not prompts; says count loads on each set for both descriptions. |
| claude-sonnet-5-5 | 2 | PASS | yes | 0.0783 | 10.1406 | no | Message gives 4 should-load and 4 near-miss prompts; says run with old and new, count loads. |
| claude-sonnet-5-5 | 3 | FAIL | yes | 0.0703 | 10.2109 | no | Describes the old-vs-new test but says it has not written any prompts; none given. |
| claude-sonnet-5-5 | 4 | PASS | yes | 0.0725 | 10.2834 | no | Message gives 4 should-load and 4 near-miss prompts; says run with old and new, count loads. |
| claude-sonnet-5-5 | 5 | FAIL | yes | 0.0840 | 10.3674 | no | Describes the old-vs-new test but gives no should-load prompts and only one near miss. |
| claude-opus-5-5 | 1 | PASS | yes | 0.2216 | 10.5890 | yes | File gives 4 should-load and 4 near-miss prompts; says run each with old and again with new, compare. |
| claude-opus-5-5 | 2 | PASS | yes | 0.2107 | 10.7997 | yes | File gives 5 should-load and 4 near-miss prompts; says run once with each description, compare counts. |
| claude-opus-5-5 | 3 | PASS | yes | 0.2093 | 11.0091 | yes | File gives 5 should-load and 5 near-miss prompts; says run each with old and new description, compare counts. |
| claude-opus-5-5 | 4 | PASS | yes | 0.2154 | 11.2244 | yes | File gives 5 should-load and 4 near-miss prompts; says run each with old and new description, count loads. |
| claude-opus-5-5 | 5 | PASS | yes | 0.2142 | 11.4386 | yes | File gives 5 should-load and 5 near-miss prompts; says run with old and again with new, compare. |


**Spend by batch.** The running total is $11.4386 at the end of Task 4, below the $50 cap. Each run script gated each
model's batch: a pair check ran before the Sonnet batch and again before the Opus batch, with the true running total
at that moment (the script summed the costs of the batch before it). The bound is that total plus 5 x $1.50.

| Batch | Reps | Cost | Running total | Pair check bound |
|---|---|---|---|---|
| T2 `old`, Sonnet | 5 | $0.3504 | $6.4151 | $6.0647 + $7.50 = $13.56 |
| T2 `old`, Opus | 5 | $0.9095 | $7.3246 | $6.4151 + $7.50 = $13.92 |
| T2 `new` at T2-NEW (attempt 1), Sonnet | 5 | $0.3635 | $7.6881 | $7.3246 + $7.50 = $14.82 |
| T2 `new` at T2-NEW (attempt 1), Opus | 5 | $0.9572 | $8.6453 | $7.6881 + $7.50 = $15.19 |
| T2 `new` at T2-NEW2 (attempt 2), Sonnet | 5 | $0.3757 | $9.0209 | $8.6453 + $7.50 = $16.15 |
| T2 `new` at T2-NEW2 (attempt 2), Opus | 5 | $0.9670 | $9.9880 | $9.0209 + $7.50 = $16.52 |
| T2 `new` at T2-NEW3 (attempt 3), Sonnet | 5 | $0.3795 | $10.3674 | $9.9880 + $7.50 = $17.49 |
| T2 `new` at T2-NEW3 (attempt 3), Opus | 5 | $1.0712 | $11.4386 | $10.3674 + $7.50 = $17.87 |

Every bound is far below the $50 cap. The Task 3 run did not gate each model; Task 4 did.

**Limits.**

1. *Blind scoring is not fully blind.* A sheet that names the new step ("trigger test") shows its arm, because the
   text exists only in the `new` arm. That was 5 of the 20 sheets in attempt 1, 5 of 20 in attempt 2 and 8 of 20 in
   attempt 3. The term "near-miss" also exists only in the new step, so by the same rule it shows the arm. Counting
   a sheet that names "trigger test" or "near-miss", 9, 8 and 10 of the 10 `new` sheets in attempts 1, 2 and 3
   show their arm, and no `old` sheet does. This changes no verdict, because every `old` rep failed in all four
   rounds, and the failing `new` reps carry the terms too. In attempt 1, 2 of the 20 sheets also named
   `discovery.md`. The graders also marked hint marks. Counts,
   by arm, from the keys: the RED-only round marked 6 of the 10 `old` sheets. Attempt 1's mixed round marked 14 of 20
   (6 `old`, 8 `new`). Attempt 2's mixed round marked 10 of 20 (6 `old`, 4 `new`). Attempt 3's mixed round marked 12
   of 20 (6 `old`, 6 `new`). The verdicts do not turn on a hint: every `old` rep failed in all four rounds, and a
   `new` rep passed when its answer held a visible prompt set.
2. *Each added sentence repeats part (a) of the PASS rule.* Both sentences ask for a prompt set, after a miss on part
   (a) that guided them. So attempts 2 and 3 are not independent of attempt 1: a reader should weigh each as a
   result that the earlier miss shaped. The owner approved each exact sentence.
3. *Four grading rounds, one agent each.* The graders were Opus agents with no key: the RED-only grading of the 10
   `old` sheets, and the mixed gradings of 20 sheets for attempts 1, 2 and 3. The `old` sheets were graded four times,
   each time freshly, with new ids.
4. *Sonnet's attempt-3 result is below the bar by one rep* (3 of 5 against 4). The item ships with that gap.

## Task 5: item 10, the rename procedure (case R3)

Raw output stays outside the repository, in the scratch folder. Two things are committed. The scrubbed rep folders
are in `runs/R3/old/<model>/`. Each holds `final.diff` and `summary.json` for each rep. The prompt folder
`prompts-R3-old/` sits next to `runs/`. It holds `M1.txt`, `R3.txt`, `T2.txt` and `MANIFEST.txt`, and only `R3.txt`
was sent. `check_scrub.py` printed PASS and `privacy_sweep.py` found 0 hits in the runs folder, in the prompt folder
and in this record. Every committed `summary.json` parses as JSON, and its `stream` field names a scratch path that
exists. R3 has no sheets and no grader, because `audit.r3_check` scores it from the parked final tree. The key is the
output of `sheets.py unblind` run with an empty grades file. The Claude Code version was `2.1.323`.

**The arm.**

| Name | Commit | What it is |
|---|---|---|
| R3-OLD | `068115951015ed8204f6f25fe89c7c6dd14d4a60` | `skills/writing-skills/` at the head of Task 4. `SKILL.md` body 19,258 characters. `discovery.md` section 3 has no rename list. |

There is no R3-NEW. The control was null (below), and the owner ruled to drop item 10's text.

**RED (Step 1).** Five `old` reps on each model. No rep was void: `audit.py` shows `VOID: none` in all 10, a path
audit with 0 hits, and a clean Bash audit (each Bash call was one in-repo `git mv`).

| Model | `old` PASS (`r3_check`) | RED |
|---|---|---|
| `claude-sonnet-5-5` | 5 of 5 | not shown |
| `claude-opus-5-5` | 5 of 5 | not shown |

`sheets.py unblind` printed `R3: RED null, GREEN n/a`. RED needs the control to pass at most 2 of 5 on at least one
model. It passed 5 of 5 on both, which is 3 or more of 5 on both models. So item 10 is null by Open for plan review
item 3.

**Verdict and ruling.** RED is null. Under Open for plan review item 3, the executor stopped before it wrote any
text, and asked the owner. The owner ruled on 2026-11-24 to drop item 10's text: no rename list goes into
`discovery.md`, no GREEN is run, no `new` arm exists, and R3 is recorded as null. Nothing in `skills/` changed in
Task 5. The `SKILL.md` body stays at 19,258 characters.

**Per-rep results.** All 10 `r3_check` results are PASS. No rep read `discovery.md` (0 of 10, Sonnet 0 of 5 and
Opus 0 of 5). The flag column is descriptive: it says whether the final message names the near collision
`sniffing-csv-headers` (Sonnet 0 of 5, Opus 2 of 5).

| Model | Rep | `r3_check` | Read `discovery.md` | Flagged `sniffing-csv-headers` | Cost (USD) | Running total (USD) |
|---|---|---|---|---|---|---|
| claude-sonnet-5-5 | 1 | PASS | no | no | 0.0583 | 11.4970 |
| claude-sonnet-5-5 | 2 | PASS | no | no | 0.0598 | 11.5567 |
| claude-sonnet-5-5 | 3 | PASS | no | no | 0.0578 | 11.6146 |
| claude-sonnet-5-5 | 4 | PASS | no | no | 0.0582 | 11.6727 |
| claude-sonnet-5-5 | 5 | PASS | no | no | 0.0684 | 11.7411 |
| claude-opus-5-5 | 1 | PASS | no | yes | 0.1597 | 11.9008 |
| claude-opus-5-5 | 2 | PASS | no | yes | 0.1667 | 12.0675 |
| claude-opus-5-5 | 3 | PASS | no | no | 0.1315 | 12.1990 |
| claude-opus-5-5 | 4 | PASS | no | no | 0.1472 | 12.3462 |
| claude-opus-5-5 | 5 | PASS | no | no | 0.1457 | 12.4919 |

**Spend by batch.** The running total is $12.4919 at the end of Task 5, below the $50 cap. `plan107/run-r3.sh` ran a
pair check before the Sonnet batch and again before the Opus batch, with the true running total at that moment (the
script summed the costs of the batch before it). The bound is that total plus 5 x $1.50. No GREEN batch ran, so no
GREEN pair check ran.

| Batch | Reps | Cost | Running total | Pair check bound |
|---|---|---|---|---|
| R3 `old`, Sonnet | 5 | $0.3025 | $11.7411 | $11.4386 + $7.50 = $18.9386 |
| R3 `old`, Opus | 5 | $0.7508 | $12.4919 | $11.7411 + $7.50 = $19.2411 |

Both bounds are far below the $50 cap.

**Limits.**

1. *The fixture is easier than the plan's.* The R3 fixture lost its `.claude/settings.json` holder after the Task 2
   pilot, because both first pilot reps had their `Edit` of that file refused (Deviation 11). With that file gone, the
   old name is held in fewer places, so a rename is easier to finish. The pilot passed one `old` rep and predicted
   this null.
2. *The reps did not use the old text's rename guidance.* No rep read `discovery.md`. The rename passed on the
   models' own search for the old name, not on anything the skill text said. So the null does not tell us that the
   old text's guidance works. It tells us that the reps did not need it here.
3. *A null on this fixture is not proof that renames never fail.* It says that this fixture does not show a failure
   of the old text. Item 10 stays open in the spec. The plan-completion gate should list it as a known gap.
4. *The `sniffing-csv-headers` flag is descriptive only.* It does not score a rep. The count (Sonnet 0 of 5, Opus 2
   of 5) comes from `audit.py`, which tests whether the final message names that skill.

## Task 6: item 3b, front-load the description

Raw output stays outside the repository, in the scratch folder. The scrubbed tally and the per-rep load lines are
committed in `runs/triggers/` (`tally.txt` is `triggers.py tally` on the scored root, and `loads.tsv` has one line
for each rep: valid or void, whether it loaded `writing-skills`, the skills it called, its result subtype and its
cost). There are no raw streams, no `competitors.txt` and no skill text. The Claude Code version was `2.1.323`.

**The commits.**

| Name | Commit | What it is |
|---|---|---|
| TR-OLD | `32b296a2d4537599e57c924c86330b31a3a136de` | `skills/writing-skills/` at the head of Task 5. The old description. |
| TR-NEW | `063b8b823a72aa24cd305ab399fdb7314a7c15f4` | The description with the testing triggers first (368 characters; the first 150 hold "fails to trigger", "over-triggers", "tightening a description", "pressure-testing" and "micro-testing"). The `SKILL.md` body stayed at 19,258 characters. |
| Revert | `0620898effcc108fe7f398331f824ecd8e0cc578` | `git revert` of TR-NEW, after the owner's ruling below. `git diff 32b296a HEAD -- skills` is empty and the body measures 19,258. |

**Step 1: the Codex cut.** `codex --version` printed `codex-cli 0.167.2`. The command was `codex debug prompt-input`,
which renders the prompt and calls no model. A copy of the two personal skill folders (`~/.agents/skills` and
`~/.codex/skills`, dereferenced) listed 76 entries and cut the old `writing-skills` entry at 220 description
characters. A real HOME listed 95 entries and cut it at 152 (the entry ends mid-word, so it lacks "micro-testing").
The listed count did not match, so the first scratch HOME did not measure the real cut (the budget is about 22,150
characters of list, so a shorter list shows longer entries). Adding the plugin cache and `config.toml` did not fix it
either (88 entries, cut at 172). The owner ruled to pad the scratch HOME instead. The padding is 19 synthetic filler
skills with made-up names (43 characters each) and made-up descriptions (400 characters each, no real text). With
them the scratch HOME listed 95 entries, and its old `writing-skills` entry was byte for byte the real one, cut at
152. The new entry, with the same fillers, listed 95 entries and cut at 152 too. It holds "micro-testing" whole. The
word ends at character 148, so the margin is 4 characters (2 if the cut counts bytes, because the em dash takes 3).
Step 1 passes: the old entry lacks "micro-testing" and the new one holds it whole. The measure is a gain in Codex only.

**Step 3: the registered 15-rep test.** The runs root is `~/.cache/agent-skills/scratch/plan107/triggers-scored`
(raw streams in `triggers-scored-raw`). The pair check ran first (bound in the spend table). Sonnet, `full`, arm `old`
ran 24 reps (P1 to P5 and N1 to N3, 3 reps each). One rep was void (P3 rep 1), and rep 4 replaced it. Loads of
`writing-skills`, valid reps only, in 3:

| Prompt | Loads of 3 | What else loaded |
|---|---|---|
| P1 | 0 | nothing |
| P2 | 0 | nothing |
| P3 | 3 | |
| P4 | 0 | nothing |
| P5 | 0 | `update-config` in 1 rep |
| N1 | 0 | `plugin-authoring` in 1 rep, `skill-development` in 1 rep |
| N2 | 0 | `writing-plans` in 1 rep |
| N3 | 0 | `init` in 3 reps |

The floor needs at least 8 of 15 should-load loads. Sonnet `old` `full` had 3 of 15 (only P3 loads the skill, as in the
Task 2 pilot, where P1 loaded it in 0 of 9). The run stopped there by the controller's ruling: no Sonnet `new`, no
Opus and no `cut150` group ran for the 15-rep test. The registered verdict is **uninformative (below the floor)**.
`runs/triggers/tally.txt` was taken after the narrow check's reps were added, so it prints a floor of 5 of 15 (P3 now
has 5 valid reps) and `verdict: incomplete` (the root does not hold every cell). Its `bar` and `prediction` lines count P3 only on a partial root. They are not the registered bars
and not the narrow check's.

**The narrow check.** The owner ruled on 2026-11-24 to replace the 15-rep test with a narrow check on P3 and N1 to
N3. The rules are in "The narrow check" under Reading rule, triggers, committed in `4dd9cd8` before any later rep. The
rules came after the floor failed and after the old Sonnet reps in `full` had been read. Reps reused: Sonnet `old`
`full`, P3 reps 2, 3 and 4 (rep 1 was void), and N1 to N3 reps 1 to 3 (all valid). P3 reps 5 and 6 topped the cell
up to 5 valid reps. Counts of `writing-skills` loads, valid reps only:

| Model | Condition | Arm | P3 loads of 5 | Near-miss loads of 9 | Status |
|---|---|---|---|---|---|
| Sonnet | `full` | `old` | 5 | 0 | informative (5 of 5 is at least 3) |
| Sonnet | `full` | `new` | 3 | 0 | |
| Sonnet | `cut150` | `old` | 5 | 0 | informative |
| Sonnet | `cut150` | `new` | 2 of 2 valid (3 reps void) | 0 of 8 valid (N2 has 2) | incomplete: the third-void stop |
| Opus | `full` | `old`, `new` | not run | not run | |
| Opus | `cut150` | `old`, `new` | not run | not run | |

Bars: Sonnet `full` P3: `new` 3 against `old` - 1 = 4, **missed**. Sonnet `full` near-miss: `new` 0 against `old` + 1 = 1,
held. Sonnet `cut150` cannot be scored (the `new` group is incomplete). The check's verdict: not a pass, because an
informative cell missed a bar. The two `new` reps of Sonnet `full` P3 that did not load called no skill at all.
Other skills loaded in the near-miss reps as before (`writing-plans` for N2 in every `new` rep and in `cut150` `old`,
and `init` for N3), and none of those counts for `writing-skills`.

**Ruling.** On a failed bar the default was to revert, and the owner ruled on 2026-11-24 to revert the description.
The revert is the commit in the table above. No more reps ran, and the running total stays $17.0953.

**Voids.** 7 reps in the root were void, each with the reason "path audit: 1 hit(s)". Six were a Bash call that the
trigger runner's tool list (`Read`, `Glob`, `Grep`, `Skill`) does not name. The seventh (P3 `new` `cut150` rep 5) made
no Bash call: its `Glob` had the rep folder as its `path`, and a `**` search from there can reach `home/Library`, the
first closed Glob limit. Five of the 7 had loaded `writing-skills` (all five P3 voids: `old` `full` rep 1, `old`
`cut150` rep 2, `new` `cut150` reps 1, 3 and 5). The other two (N2 `new` `cut150` rep 3 and N3 `old` `cut150` rep 1)
did not load `writing-skills`. The stop was the third void in Sonnet `cut150` `new`: 4 voids there. The driver checked
the void count only at the end of each round, so the third void (P3 rep 5) came before the 9 reps of N1 to N3 that
ran after it (about $0.39). The fourth void and the near-miss count of 0 of 8 valid reps in that cell come from those
9 reps. The verdict does not change, because the `cut150` cells are not scored.
One rep was also aborted: the first launch of the narrow check ran P3 `old` `full` rep 5 and its runner was killed,
because the driver's loop did not guard the runner's standard input. The rep had finished (it loaded `writing-skills`, and cost
$0.0876) but not summarized. Its files were moved to scratch (`aborted/`), it was never scored, its cost is in the
spend table, and rep 5 was rerun.

**Spend.** Pair checks ran before each pair, with the true running total (`running total + the pair's reps x $0.25 <= $50`):

| Pair | Check | Result |
|---|---|---|
| Sonnet `full`, registered pair (48 reps) | $12.4919 + $12.00 = $24.4919 | pass |
| Sonnet `full`, narrow (16 reps), first launch | $14.2876 + $4.00 = $18.2876 | pass (run killed, see Voids) |
| Sonnet `full`, narrow (16 reps), second launch | $14.3752 + $4.00 = $18.3752 | pass |
| Sonnet `cut150`, narrow (28 reps) | $15.6388 + $7.00 = $22.6388 | pass |

The groups' costs are in the Spend stop table. The running total at the end of Task 6 is $17.0953, below the $50 cap.

**Limits.**

1. *The trigger-rep VOID rule drops reps that loaded.* A rep that calls Bash, or that searches with a wide `Glob`
   from the rep folder, is void. Five of the 7 voids were reps that had loaded `writing-skills` (four by a Bash
   call, one by a wide `Glob`). So the rule lowers the valid load counts, most in the arm that loads more. Sonnet `cut150` `new` shows it: all 5 P3 reps loaded `writing-skills`, but 3 were void.
   The Sonnet `full` `new` result (3 of 5) had no voids, so that miss is real, but the `cut150` numbers are not fair.
2. *Claude Code routing for the reorder is unproven either way.* The one clean Sonnet `full` pair shows a drop (5 to
   3 of 5), and Opus never ran. A pair of 5 reps cannot separate a real loss from noise.
3. *The Codex gain is measured, not shipped.* The reorder moves "micro-testing" inside the 152-character cut (margin 4
   characters), and the revert gives that up.
4. *The registered 15-rep test cannot run on these prompts.* Only P3 loads the skill on Sonnet, so the floor fails.
5. *Opus never ran.* No Opus group started, so no Opus cell is informative.

For the plan-completion gate, the known gaps are: item 3b's Codex gain is measured but not shipped, Claude Code
routing for the reorder is unproven, Opus never ran, and the trigger-rep VOID rule needs a ruling before any later
trigger test. Item 2's open status (spec item 2) is unchanged.

## Deviations from the plan's Task 1 text

1. `FRAME_T` has a `{tools}` slot. The plan says to copy `FRAME_T` with the skill-copy path changed. Plan
   105's sentence says the tools are Read, Glob, Grep, Edit and Write. That is false for an R3 rep, which also
   has `Bash`. `cases.TOOLS_TEXT` fills the slot for each case.
2. M1, T2 and R3 each add one `[you, tools]` line (Cases). The plan says each case states that the needed earlier
   steps are done, and its table lists only the partner's words.
3. The plan's third Glob test (`test_brace_alternative_under_home_library_prefix_voids`) passes on plan 105's
   audit already. Its pattern `$HOME/Library/{Keychains,Caches}/*` has a literal part under `$HOME/Library`.
   The third limit is the relative alternative that sits after the prefix, as in `$HOME/{Library,x}/Keychains/*`.
   Task 1 keeps the plan's test as written and adds tests for that spelling.
4. The Glob fix expands braces in full, so the text after a group is judged too (`rep/{home,x}/Library/*`).
   Plan 105's per-alternative checks stay as they were, so every pattern it flagged is still flagged.
5. The `[you, tools]` line of T2 drops the run counts that the first version held, and R3 gets a line (see
   Cases). Review round 1 asked for both.
6. `sheets.py` reads a missing model as unknown. A case's RED is null only when `old` has reps on both plan
   models and none shows RED, else it is `incomplete`. A case's GREEN is `incomplete` when a model where RED is
   shown has no `new` reps while the graded ones do not miss. It is also `incomplete` when a plan model has no
   `old` reps, because RED was never checked there. Open items 3 and 4 name both models, so a verdict from one
   model says neither null nor met. A graded miss still reads `missed`.
7. `triggers.py tally` prints `verdict: uninformative (below the floor)` when the run is complete and a floor
   entry fails. The plan's Task 6 Step 4 says only "On a failure, revert". The floor rule of Open item 5 says
   stop and ask, so it governs. A bar failure with every floor entry met still prints `fail`.
8. `run_trigger_reps.sh` keeps one `competitors.txt` in the runs root. The first version wrote one per
   `<prompt>/<arm>/<condition>/<model>` folder, so the old and new batches of a pair never met.
9. The Bash audit does not test for a flag. `git mv -f a` reads as a move of `-f` to `a`, is clean, and moves
   nothing, because git prints its usage. The `audit.py` docstring now says so.
10. Task 2 used `skill-creator` version `7b7a29e0458e`, not `65adb96f26de`. The plugin installer's list changed
    between Task 1 and Task 2 (the plugin updated on 2026-11-23), and the folder that Task 1 named now carries an
    orphan marker. The brief says to choose by the installed version.
11. Task 2's case pilot removed the R3 fixture's `.claude/settings.json`. Both first R3 reps (Sonnet and Opus)
    had their `Edit` of that file refused, so no rep could pass the R3 check that Task 1 defined. The file held
    only the `skillOverrides` entry for the old name. The kit test that pinned it
    (`test_r3_fixture_is_the_plans_repository`) changed first and failed, then passed with the file removed.
    The plan's Task 1 fixture text names that file too. The plan is not changed here.
