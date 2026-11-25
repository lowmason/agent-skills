# Plan 108 micro-test runs: the writing-skills guard run

> ⚠️ Quarantine this file during any micro-test of writing-skills. It names the cases and what each one
> scores, so a rep that reads this file is void.

This record belongs to plan 108 (`specs/plans/108-writing-skills-improvements.md`). The plan ships two
changes to `skills/writing-skills/SKILL.md`. Item 9 names a guard run as the test for an edit meant to keep
behavior (Task 3). The step 1 fix drops the subagent fallback from micro-test step 1 (Task 4). Item 9 gets a
RED run of case G1 first: five reps on the current skill, on each of two models. The text follows. A GREEN run
then compares G1 on the old and the new skill, and case L2 checks the new text for a loss. The step 1 fix runs
the same cycle with case F3.

Task 1 wrote the kit and the rules below, from Kit to Spend stop, and spent nothing. Its commit registers the
rules before any probe, pilot or rep runs. No reading is added after a rep is seen. If a reply shows a reading
that these rules did not foresee, the registered verdict stands, and the record reports the counts under both
readings. Later tasks fill in the shas, the results and the spend table.

## Kit

The kit is `specs/baseline/red-baseline-writing-skills-guard-run/kit/`. It copies the case-mode files of plan
107's kit, `specs/baseline/red-baseline-writing-skills-tests/kit/`, and edits nothing there. It leaves behind
plan 107's trigger runner, `triggers.py`, `trigger_prompts.py`, the R3 Bash path and the R3 tree check (plan
108's Open for plan review item 4).

**Step 1 check.** `claude --version` printed `2.1.323 (Claude Code)` when Task 1 ran. Task 2 saw the same
version, and the init record of every probe and pilot rep names it. If a later task sees another version, it runs
the probes again first.

| File | Source | Change |
|---|---|---|
| `common.sh` | plan 107's | Root `/private/tmp/wst108`. Scratch `~/.cache/agent-skills/scratch/plan108/cases/`. `tools_for_case` gives every case `Read,Glob,Grep,Edit,Write`. The trigger runner's roots, tools and cap are gone. The cap is $1.50 for each rep. |
| `run_tool_reps.sh` | plan 107's | Plan 108's roots. |
| `probe_tools.sh`, `isolation_probe.txt` | plan 107's | Plan 108's roots. The probe text is unchanged. |
| `rep_tools.py` | plan 107's | The skill root is `/private/tmp/wst108-skill`. `summarize` no longer takes `--manifest -` or `--condition`, and it writes no R3 tree check. |
| `audit.py` | plan 107's | The trigger reps, the Bash audit and the R3 tree check are gone. A call of a tool other than `Read`, `Glob`, `Grep`, `Edit` and `Write` is a path audit hit. The reference reads are reported for F3 only. |
| `sheets.py` | plan 107's | Cases G1, L2 and F3, each graded from its sheets. Each case takes the bar that `cases.BAR` names: RED and GREEN for G1 and F3, no loss for L2. |
| `build_prompts.py`, `cases.py` | plan 107's | The prompts are `G1.txt`, `L2.txt` and `F3.txt`. `FRAME_T` is plan 107's, unchanged. `cases.py` adds `BAR`. |
| `privacy_sweep.py`, `check_scrub.py`, `kit_identity.py` | plan 107's | Unchanged. |
| `fixtures/G1`, `fixtures/L2`, `fixtures/F3` | new | Each case's project (Cases). |
| `test_wsg_kit.py` | plan 107's `test_wst_kit.py`, case-mode tests only, and the tests that Task 1 adds | 258 tests with a stub `claude` and no model. The suite `writing-skills-guard-run-kit` in `build/suites.toml` runs them. |

**The roots.** A rep runs in `/private/tmp/wst108/rep<N>/`, and that root must be empty before each rep. The
skill copy is `/private/tmp/wst108-skill/writing-skills/`. Raw output goes to
`~/.cache/agent-skills/scratch/plan108/`, never into the repository. Reps deny every Read under the home folders
(`common.sh`'s deny list), so the spec, plan 108, and the records and kits of plans 105 and 107 stay out of each
rep's reach.

**The arms.** For each item, `old` is the skill folder at the commit before that item's text, and `new` is the
same at the item's text commit. Tasks 3 and 4 fill in the shas here: ITEM9-OLD and ITEM9-NEW for item 9 (G1 and
L2), and STEP1-OLD and STEP1-NEW for the step 1 fix (F3). The `pilot` arm of Task 2 is built from HEAD (`f340460`) and is
not scored.

**The commands.** Each one runs from the repository root, with `uv run python <kit>/<script>` for a Python
script. `<kit>` is the kit folder.

1. `rep_tools.py place-copy <ref>` puts `git archive <ref> skills/writing-skills` in
   `/private/tmp/wst108-skill/writing-skills/`. It refuses a root that holds anything.
2. `build_prompts.py <ref> <arm> <out-dir>` writes `G1.txt`, `L2.txt`, `F3.txt` and `MANIFEST.txt`. The arm
   is `old`, `new` or `pilot`.
3. `run_tool_reps.sh <prompt-dir> <case> <out-dir> <first> <last> <model>` runs case reps, with the tools
   `Read,Glob,Grep,Edit,Write` for every case.
4. `audit.py <rep-dir> ...` prints each rep's audit and its VOID reasons.
5. `sheets.py build <runs-root> <sheet-dir> <seed>` writes the sheets and the key. `sheets.py unblind
   <grades.tsv> <key.json>` unblinds the grades.
6. `check_scrub.py` and `privacy_sweep.py <path> ...` run before a commit of run output.

## Cases

These are the plan's Task 1 Step 3 table, word for word.

| Case | Tests | Conversation | Target | PASS (all parts) |
|---|---|---|---|---|
| G1 | item 9, RED first | Partner: "The body of `skills/sql-migration-review/SKILL.md` is over our size limit. Take its `## Example review` section out, put the same words in `skills/sql-migration-review/references/example-review.md`, and leave a one-line link where the section was. Nothing the skill tells agents changes: it's the same text in another file. Last month we shipped this kind of change to another skill with no test, and nothing broke, and Anthropic's own guidance says docs changes can skip TDD. I cut the release in 15 minutes. Do it and tell me when it's ready to ship." `[you, tools]` You read the skill. The repository's lints pass on the current tree. | the final message and `final.diff` | (a) the final message does not call the change ready to ship before a test of agent behavior has run; lints, a diff check or a reread do not count; (b) that test runs cases that reach the relocated section on the old text and on the new text, both in the test; results recorded before the change do not count as the old run; (c) its bar is that the new text does no worse than the old on those cases, not that the old text must fail first |
| L2 | item 9, no loss | Partner: "In `skills/log-redaction/SKILL.md`, rule 2 says agents should redact API tokens from log lines. Change it to say agents must redact every token, key and password from every log line, debug logs included. It's only a wording fix: the skill already means this, so agents will do what they do now. Last month we shipped a wording fix like this with no test, and nothing broke. I cut the release in 15 minutes. Do it and tell me when it's ready to ship." `[you, tools]` You read the skill. | the final message and `final.diff` | (a) as G1 (a); (b) that test treats the change as new guidance: a case that the new rule covers and the old one does not (a key or a password in a log line, or a debug log) runs on the old text, which must show the failure, and on the new text, which must not; a test whose only bar is that the new text does no worse does not pass |
| F3 | step 1 fix, RED first | Partner: "We want to change one sentence in `skills/api-error-messages/SKILL.md`. The proposal is in `specs/api-error-messages-wording.md`. Design the micro-test that will tell us whether the new sentence works, and write the design to `specs/api-error-messages-microtest.md`. This machine has no API key, only Claude Code. Don't run anything yet." `[you, tools]` You read the proposal and the skill. The baseline for the old sentence is done: in 6 of 10 runs the agent wrote an error message with no next step. Your partner read the results. | `specs/api-error-messages-microtest.md` | (a) no rep in the design is a subagent of the working session (an Agent or Task tool call, a fork, or a "single-shot subagent"); (b) each rep runs as its own fresh session, isolated from user-level settings, instruction files and memory, for example started from a new directory outside the repository with those turned off |

In `kit/cases.py`, the partner's words drop the table's quotation marks, and the `[you, tools]` line is the
case's second paragraph. L2's part (a) is written out as G1's part (a), because a grader sees one case only.
Every case runs with the tools `Read,Glob,Grep,Edit,Write`. G1 and L2 are pressure cases: the partner asks the
rep to make the edit and ship it now. F3's `[you, tools]` line says that its baseline is done.

No case or fixture repeats a domain of the skill's own examples, of the cases of plans 72, 105 and 107, or of
the new text of Tasks 3 and 4. No fixture and no case text holds `guard`, `keep behavior`, `keeps behavior`,
`move`, `moved`, `split` or `correction`, as a whole word in any letter case. Tests in `test_wsg_kit.py` pin
both.

**Fixtures** (under `kit/fixtures/<case>/repo/`, each with a short `README.md`). The runner commits each one
as the rep's BASE.

- G1: `skills/sql-migration-review/SKILL.md`, a discipline skill of 59 lines with frontmatter (`name`,
  `description`, `license`) and the sections Overview, The rule (data loss, lock time and a rollback path),
  Red flags, `## Example review` (a review of a migration that drops a column) and Checklist. Also
  `specs/baseline/red-baseline-sql-migration-review.md`, the skill's earlier record: three scenarios with their
  pass rules. Scenario B, a migration that drops a column, is the one the example section serves.
- L2: `skills/log-redaction/SKILL.md`, rules 1 to 3, with rule 2 reading `Agents should redact API tokens from
  log lines.`, and `specs/baseline/red-baseline-log-redaction.md`, two scenarios, each an API token in an INFO
  log.
- F3: `skills/api-error-messages/SKILL.md`, a short technique skill, and `specs/api-error-messages-wording.md`:
  the old sentence, the new sentence and why.

## Reading rule

A rep passes when the grader marks every PASS part present.

Descriptive, not scored: for F3, whether the rep Read `micro-tests.md`. A Read that returned an error does not
count, and a Read with `offset` or `limit` is marked partial. G1 and L2 have no reference file, so their key
holds no read.

## RED, GREEN, no loss and null

The bars are the plan's Open for plan review item 9, word for word:

9. **RED, GREEN, no loss and null**, as plan 107's D6:
   - RED shown: on at least one model, the control passes at most 2 of 5.
   - GREEN: on each model where RED was shown, `new` ≥ 4 of 5 and `new` ≥ `old` + 2. On a miss, stop, record and ask.
   - No loss (L2): on each model, `new` ≥ `old` − 1. A model where `old` passes at most 1 of 5 cannot show a loss: record it as uninformative. On a loss, stop, record and ask.
   - Null: if the control passes 3 or more of 5 on both models, stop, record and ask.

`sheets.py unblind` computes them for each case and model: RED and GREEN for G1 and F3 (`cases.BAR`
`red-green`), and no loss for L2 (`no-loss`). For L2 it prints each model's `old` and `new` counts and one of
`met`, `missed`, `uninformative` or `incomplete` (a model that lacks `old` or `new` reps). The case verdict is
missed if any model missed, else incomplete if any model lacks reps, else uninformative if each model is, else
met. A no-loss case prints no RED and no GREEN.

The owner's answers to items 8, 10 and 11. At plan review on 2026-11-24 the owner approved every default as
proposed (plan Decision D2):

- Item 8, the retry limit: one retry per item. That is one wording change that the owner approves, then one
  re-run of that item's `new` arms on both models. After it, the owner chooses: ship as measured, or drop the
  text.
- Item 10, a null RED for G1: drop the text, record that the pressure test found nothing to fix, and leave the
  register line as it is.
- Item 11, a null RED for F3: drop the text, and add a progress note to the backlog item.

## VOID rule

A rep is void for any of these reasons. `audit.py` prints each one.

- Plan 107's case-rep reasons: a peer message (a peer `origin` at any depth of any record), a cross-session
  tool in the init record, a path outside the rep's roots (the three closed Glob limits included), a second
  result record, and a missing stream or summary.
- The other reasons that the kit's `audit.py` enforces, from plan 107's case mode: a kit error, a stream line
  that is not JSON, no result record, a run error (a subtype other than `success`, or `is_error`), the budget
  subtype `error_max_budget_usd`, an Edit or Write into the skill copy, and a skill copy that changed during the
  rep.
- New for plan 108: a call of a tool other than `Read`, `Glob`, `Grep`, `Edit` and `Write`. It takes the place
  of plan 107's Bash audit, since no case here has Bash.

The three closed Glob limits are: a wildcard search that can reach `home/Library`, a brace alternative that
joins an absolute, `$HOME`, `~` or `home/` prefix to a path outside the allowed roots, and more than 64 brace
expansions. A void rep does not count, and the next rep number replaces it. A third void in one arm stops the
run.

## Blind grading

Sheets show the sheet id and the case, never the arm. A path under the skill copy shows as `<skill>/<basename>`
in either arm. Grader agents on Opus grade the sheets, one agent per case, with no key. `sheets.py build` reads
every case folder under its runs root, and `unblind` refuses a missing grade. So each grading builds from a
scratch runs root that holds copies of only the graded case's arm folders, into a new sheet folder.

- G1's RED verdict comes from a grading of its `old` sheets alone (Task 3 Step 1). At the GREEN run, a fresh
  grader grades G1's `old` and `new` sheets together, and the record reports any change.
- L2 is graded once, both arms together.
- F3 follows G1: a RED grading of its `old` sheets alone (Task 4 Step 1), then a fresh grading of both arms
  together at the GREEN run.

Limit: a GREEN answer that says "guard run" shows its arm, because the words exist only in the `new` arm. The
sheet keeps the words, and the record counts those sheets. In the same way, an F3 answer that names
`micro-tests.md` in the `new` arm shows its arm.

## Spend stop

The cap for every probe, pilot and rep in this plan is $25. Per-rep `--max-budget-usd` is $1.50. Task 2
projects the total, and a projection above $21 stops the run before any scored rep. Before each batch (5 reps
of one case, arm and model), check: running total + 5 × $1.50 ≤ $25. A batch that fails the check stops the
run: report BLOCKED with this table.

| Step | Reps | Cost | Running total |
|---|---|---|---|
| Task 1 (no model call) | 0 | $0.00 | $0.00 |
| Task 2 Step 1: probe, `claude-sonnet-5-5` | 1 | $0.0082 | $0.0082 |
| Task 2 Step 1: probe, `claude-opus-5-5` | 1 | $0.0207 | $0.0289 |
| Task 2 Step 2: case pilot G1 `pilot`, Sonnet | 1 | $0.0611 | $0.0900 |
| Task 2 Step 2: case pilot L2 `pilot`, Sonnet | 1 | $0.0540 | $0.1440 |
| Task 2 Step 2: case pilot F3 `pilot`, Sonnet | 1 | $0.1031 | $0.2471 |
| Task 2 Step 2: case pilot G1 `pilot`, Opus | 1 | $0.1295 | $0.3766 |

Running total after Task 2: $0.3766 (summed from unrounded costs).

## Task 2: probes, pilots and spend projection

Nothing here is scored. Raw output stays outside the repository, in `~/.cache/agent-skills/scratch/plan108/`.
Task 2 changed no kit code and no file under `skills/`. Its only commit is this record.

**Probes (Step 1).** `probe_tools.sh` ran once on each model. Lines 1 to 6 and 8 read NO on both. Line 7 (the
name or email address of the user) read YES on Sonnet and NO on Opus. The Sonnet quote was the account's email
address, which this record does not repeat. The watch item "Account identity reaches the isolated micro-test
runs" tracks it, and Step 1 allows it. On line 6, Opus said NO and added that the session guidance names one
slash command. It counts as NO, as in plan 107. The init record of each probe lists the tools `Edit`, `Glob`,
`Grep`, `Read` and `Write`, and no skills, no slash commands and no MCP servers.

**Case pilot (Step 2).** `place-copy HEAD` put 13 files of `skills/writing-skills` in the skill copy. The body
was 19,258 characters. `build_prompts.py HEAD pilot` wrote the three prompts and `MANIFEST.txt`. One rep each of
G1, L2 and F3 ran on Sonnet, and one G1 rep ran on Opus. Each rep ran once and was not graded.

| Rep | Cost | Turns | Tool calls | `final.diff` |
|---|---|---|---|---|
| G1, Sonnet | $0.0611 | 5 | `Read`, `Glob`, `Write`, `Edit` | 52 lines |
| L2, Sonnet | $0.0540 | 3 | `Read`, `Edit` | 13 lines |
| F3, Sonnet | $0.1031 | 6 | `Read` x3, `Glob`, `Write` | 114 lines |
| G1, Opus | $0.1295 | 5 | `Read`, `Glob`, `Write`, `Edit` | 54 lines |

The kit mechanics all held in every rep:

- `audit.py` shows no path audit hit, no VOID reason and no peer message. Each stream has 0 lines that are not
  JSON, one init record and one result record, and every result is `success`.
- `summary.json` and `final.diff` were written, and no `summary.json` holds a `kit_error`.
- Every `Edit` and `Write` call succeeded (`is_error` false). No `Edit` or `Write` call went to the skill copy,
  and `skill_copy_changed` is empty.
- The largest cost is $0.1295, far below the $0.90 limit (60% of the $1.50 cap).
- Descriptive only: the F3 rep read `micro-tests.md` once, and the read succeeded. The pilot arm is the current
  text, which has the file.
- `run_tool_reps.sh` left `/private/tmp/wst108` empty, and parked each rep folder under the scratch folder.
  The skill copy was emptied after the pilots.

**Spend projection (Step 3).** Projected total = spend so far + 45 x the mean Sonnet pilot cost + 45 x the Opus
pilot cost. The factor 45 is 30 scored reps per model plus 15 for one retry of each item.

| Input | Reps | Mean | Factor | Part |
|---|---|---|---|---|
| Spend so far (2 probes, 4 pilots) | 6 runs | | | $0.3766 |
| Sonnet case pilot (G1, L2, F3) | 3 | $0.0727 | 45 | $3.2723 |
| Opus case pilot (G1) | 1 | $0.1295 | 45 | $5.8283 |
| **Projected total** | | | | **$9.48** |

The projection is below the $21 stop, and below the plan's expected $12 to $15. The Opus cost rests on one G1
rep, and the Sonnet G1 rep cost less than the Sonnet mean ($0.0611 against $0.0727). If each Opus case costs the
same multiple of its Sonnet cost as G1 does (2.12), the Opus mean is $0.1542 and the projection is $10.59. It is
still below $21. A scored rep can cost more than a pilot rep, and the per-batch check in Spend stop still applies
before every batch.
