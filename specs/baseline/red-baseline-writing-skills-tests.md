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

Running total after Task 2: $1.42 (about $1.4179, summed from unrounded costs). The projection below adds the
scored runs.

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
