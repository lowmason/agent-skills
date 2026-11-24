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
| `skill-creator` (the official plugin) | `skill-creator` | `65adb96f26de` (the cache folder name, which the plugin installer lists as the installed version on 2026-11-23). The manifest has no version field. |

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
the same at the commit of the item's text. Tasks 3 to 5 fill in the shas here. The `pilot` arm of Task 2 is
built from HEAD and is not scored. Task 6's arms are TR-OLD and TR-NEW (the trigger test).

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
  scored descriptively), `commands/ingest.md`, `AGENTS.md` and `.claude/settings.json`
  (`"skillOverrides": {"csv-dialect-sniff": "name-only"}`). The runner makes the repository and commits it
  once as the rep's BASE.
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
