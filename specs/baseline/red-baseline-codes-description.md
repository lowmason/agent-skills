# Plan 111 trigger test: the classification-codes description

> ⚠️ Quarantine this file during the trigger test of classification-codes. It names the prompts and the
> rule that scores them, so a rep that reads this file is void.

This record belongs to plan 111 (`specs/plans/111-codes-and-bls-reference-skills.md`). Plan 111 adds Census
industry (IND) codes to classification-codes and changes its description to name them. A trigger test of the
old description against the new one gates that change. The test is the one in
`skills/writing-skills/references/discovery.md` § 6, run under `skills/writing-skills/references/micro-tests.md`.

Task 3 wrote the kit and the rules below, from Kit to Spend stop, and spent nothing. The commit that adds this
file registers the rules before any probe, pilot or rep runs. No reading is added after a rep is seen. If a rep
shows a reading that these rules did not foresee, the registered verdict stands, and the record reports the
counts under both readings. Task 4 fills in the shas, the probe, the results and the spend table.

## Kit

The kit is `specs/baseline/red-baseline-codes-description/kit/`. It copies files from plan 107's committed kit
`specs/baseline/red-baseline-writing-skills-tests/kit/` and edits none of them. It keeps only the trigger lane.
Plan 107's case runner, sheets, probe runner, privacy sweep and guard-run files stay out.

When Task 3 ran, `claude --version` printed `2.1.323 (Claude Code)`. Task 4 records the version again.

| File | Source | Change |
|---|---|---|
| `common.sh` | plan 107's | The case-rep parts are cut. The root is `/private/tmp/cd111t` and the scratch folder is `~/.cache/agent-skills/scratch/plan111/triggers/`. The deny list gains `Bash` and `Read(~/**)`. `TRIGGER_SETTINGS` sets `blockReadsOutsideWorkingDirectories`. A finished rep folder is removed, not parked. |
| `run_trigger_reps.sh` | plan 107's | No `<condition>` argument and no condition folder. No plugin skill is copied in. The runner refuses a ref whose `skills/` lacks a name of `fixtures/trigger/listing.txt`, and a rep root inside a git repository. The prompt id `probe` runs the isolation probe as a trigger rep. |
| `rep_tools.py` | plan 107's | Only `strip` and `summarize` stay. `strip` also drops `origin`. `summarize` runs rule 4's check on the raw stream before it strips anything. |
| `audit.py` | plan 107's | Trigger reps only. The path audit, the Glob limits, the Bash audit, the reference reads and the R3 tree check are cut. Rules 3, 4 and 5 and the listing check are as below. |
| `triggers.py` | plan 107's | The skill under test is `classification-codes`. `judge()` applies the PASS rule below. |
| `trigger_prompts.py` | new | The nine prompts and the groups `SHOULD_LOAD`, `IND` and `NEAR_MISS`. |
| `cases.py` | plan 107's name | The skill under test, the listing names, the arms, the models, the reps per cell and the quarantined names. Plan 107's audit imported `cases.py`, so the name and the import stay. |
| `kit_identity.py` | plan 107's | Unchanged except its first docstring line. |
| `isolation_probe.txt` | plan 107's | Unchanged, byte for byte. |
| `fixtures/trigger/repo/README.md` | new | The rep's project: a neutral README with no codes words. |
| `fixtures/trigger/listing.txt` | new | The three names that the listing check needs. |
| `test_cd_kit.py` | plan 107's tests, cut to the trigger lane, and the tests that Task 3 adds | Tests with a stub `claude` and no model. The suite `codes-description-kit` in `build/suites.toml` runs them. |

**The runner.** Each rep runs in a new session, in a new folder `CD_TROOT/rep<N>/` with `repo/`, `home/` and
`tmp/`. `env -i` keeps only `HOME`, `USER`, `LOGNAME`, `PATH`, `SHELL`, `TMPDIR`, `LANG` and the two disable
flags. The rep's `repo/` is a copy of `kit/fixtures/trigger/repo/`, with one commit. `home/.claude/` holds
`git archive <ref> skills/` and a `settings.json`. The settings hold the deny list,
`blockReadsOutsideWorkingDirectories`, `"syncClaudeAiSkills": false` and `"skillListingBudgetFraction": 0.05`.
The flags are `--setting-sources user`, `--strict-mcp-config`, `--no-session-persistence`,
`--tools Read,Glob,Grep,Skill`, `--allowedTools` with the same value, `--max-turns 3`, `--max-budget-usd 0.25`
and `--output-format stream-json --verbose`. `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` is set. The runner has no
`--disable-slash-commands` and no `--settings`, because either one would hide the listing under test. After
the rep, `summary.json` goes to `<out-dir>/rep<N>/`, and the stream, the prompt and stderr stay in the scratch
folder. The rep folder is then removed.

**The commands.** Each one runs from the repository root. `<kit>` is the kit folder.

1. `<kit>/run_trigger_reps.sh <ref> <arm> <prompt-id> <out-dir> <first> <last> <model>` runs trigger reps.
   `<arm>` is `old`, `new` or `pilot`. `<prompt-id>` is `P1` to `P5`, `N1` to `N4`, or `probe`. `<out-dir>`
   ends in `<prompt-id>/<arm>/<model>`.
2. `uv run python <kit>/audit.py <rep-dir> ...` prints each rep's audit and its VOID reasons.
3. `uv run python <kit>/triggers.py loads|listing <rep-dir>` reads one rep.
4. `uv run python <kit>/triggers.py tally <runs-root>` prints the counts, the bars and the verdict. The runs
   root holds the scored reps only: `tally` refuses a `probe` or `pilot` folder, so those go in a root of
   their own.

## Arms

`old` is `skills/` at the commit before Task 4's description change. `new` is the same tree with the
description below. Task 4 records both shas here. At the start of Task 3 (`b7b95c0`), the old description
was 1,022 characters once folded. The `new` description is 1,005 characters once folded and stripped:

```yaml
description: >
  Use when a task touches NAICS, SOC, or Census industry (IND) or occupation (OCC) codes — mapping a
  code to its title or a title to its code, listing a sector's or major group's members, converting
  between vintages (NAICS 2012↔2017↔2022, SOC 2010↔2018, Census OCC 2010↔2018), joining datasets
  coded in different vintages, a series break at a revision, or explaining how
  industries and occupations are defined and revised (ECPC / SOCPC, NAICS 2027, SOC 2028). Consult
  BEFORE answering any code↔title question, joining on an industry or occupation code, or treating a
  code as the same thing in two vintages. Trigger on: NAICS, SOC, O*NET, ACS / CPS IND or OCC
  variable, sector, subsector, industry group, six-digit code, occupation code, major group, detailed
  occupation, concordance, crosswalk, trilateral, change indicator, unclassified / 999999, "what
  industry is X", "what does code X mean", "is code X still valid", "when is the next revision".
  Codes and titles come from data/, never from model memory.
```

## Trigger prompts

`kit/trigger_prompts.py` holds the nine prompts.

- Should load (P1 to P5). P1 and P2 are the IND prompts:
  - P1: "Our CPS extract has an IND column with values like 7860 and 0770. What industries are those, and which NAICS codes do they cover?"
  - P2: "I need to join ACS PUMS records coded with 2017 Census industry codes to QCEW data keyed by NAICS. How do I map one to the other?"
  - P3: "What is the 2022 NAICS title for 541511, and did that code change from 2017?"
  - P4: "Map these SOC 2010 codes to SOC 2018: 15-1132 and 15-1133."
  - P5: "Our ACS file has OCCP 1021. Which occupation is that?"
- Near miss (N1 to N4):
  - N1: "Which counties are in the Austin-Round Rock CBSA?"
  - N2: "How does the CES birth-death model feed into the monthly payroll estimate?"
  - N3: "How do I compute an unemployment rate from CPS microdata with the PWSSWGT weight?"
  - N4: "Write a Polars function that drops duplicate rows keyed on series_id and ref_date."

## Rules

These are the six rules of plan 111's Task 3 Step 1. The kit applies each one.

1. Each rep gets its own new folder outside every repository, with its own HOME and scratch folder. The kit:
   `CD_TROOT/rep<N>/` with `home/` and `tmp/`, made new for each rep. The runner refuses a root that holds
   anything, or a root inside a git repository. The rep's `repo/` is a git repository of its own: a new
   one-commit copy of the fixture project, kept from plan 107's design. It is the rep's project, not a
   repository that holds the rep folder.
2. The deny list holds `Bash`, `Read(~/**)`, `ListAgents`, `SendMessage`, `PushNotification` and
   `RemoteTrigger`, and the settings set `blockReadsOutsideWorkingDirectories`. The runner starts each rep
   with a single `claude -p` call, in that rep's own folder and HOME, not a shell `for` loop that shares one
   HOME. The deny list also keeps plan 107's entries for `/Users` and `~/Library`.
3. The runner removes `credential_expires_at` from every saved `.json` and `.jsonl` file. A rep is VOID if the
   key is still there. The saved files are `summary.json` and the stream `rep<N>.jsonl`. The runner removes the
   rep folder, so no other file of the rep is kept.
4. A rep is VOID if any record has `result_index` > 0 or an `origin` whose `kind` is `peer`. The runner scrubs
   `origin` objects from saved records after that check.
5. Quarantine: no rep may read this plan, the kit, this write-up or `specs/deferred_items.md`. A rep that does
   is VOID.
6. Models: `claude-sonnet-5-5` and `claude-opus-5-5`, with the same rep count on each.

## Reading rule and PASS rule

A rep loads when `triggers.py loads` says `load`. It reads the stream as it stands: any `tool_use` named
`Skill` whose `skill` input is exactly `classification-codes`, at any point, counts.

The run has 3 reps per cell: 9 prompts × 2 arms × 2 models = 108 reps.

- **PASS,** on each model, when all three hold:
  - `new` loads on P1 + P2 ≥ `old` loads there.
  - `new` loads on P1 to P5 ≥ `old` loads there.
  - `new` loads on N1 to N4 ≤ `old` loads there.
- **FAIL** otherwise.

`triggers.py tally` applies this rule and prints three bars per model: `ind` (P1 + P2), `should-load` (P1 to
P5) and `near-miss` (N1 to N4). It prints `verdict: pass` or `verdict: fail`. It prints `verdict: incomplete`
unless each of the 36 cells holds exactly 3 valid reps.

## VOID rule

A rep is void for any reason in this list. `audit.py` prints each reason it finds.

- Rules 3 to 5 above.
- An error result. The kit reads this as plan 107 did: a result subtype other than `success`, or `is_error`
  true. A trigger rep has `--max-turns 3`, so the subtypes `error_max_turns` and `error_max_budget_usd` are a
  normal end, not an error result.
- A listing that lacks `classification-codes`, `geographic-codes` or `bls-data-context`. The listing is the init
  record's `skills` field, and the names must match exactly.

How the kit reads the rules:

- **Kit errors.** A rep that the kit cannot read whole cannot show rules 3 to 5 or its result, so it is void
  too: no `summary.json`, a `kit_error` in it, no `peer_check` in it, no saved stream, a stream line that is not
  a JSON object, no result record, or a second result record.
- **Rule 4.** `rep_tools.py summarize` checks the raw stream before the strip and writes its findings to
  `summary.json` as `peer_check`. These are reason strings only, never the origin's text. The audit voids a rep
  for each entry there, and it checks the saved stream again. The check looks at every depth of every record.
  A record with no `result_index` counts as 0. A `result_index` that is not a JSON integer (a string, a float
  such as 1.5 or 0.0, or null), or is a boolean, cannot be compared with 0, so it voids the rep too (plan 103's
  reading). An integer voids only above 0.
- **Rule 5.** No rep can reach these files: the rep's folder holds only the fixture project and the
  `skills/` archive, and rule 2 fences reads to `repo/`. So the audit checks the rep's calls. A rep is void when
  a `Read`, `Grep` or `Glob` call's `file_path` or `path`, or a `Glob` pattern, holds
  `111-codes-and-bls-reference-skills`, `red-baseline-codes-description` or `deferred_items.md`, in any case,
  and its tool result came back without an error. A refused call, or a call with no result, read nothing, so it
  does not void the rep. A `Grep` content pattern is not a path and is not checked.
- **No other VOID reason.** Plan 107's path audit, Glob limits and Bash audit void nothing here. Rule 2's deny
  list and read fence refuse those calls instead. Plan 107's record (Task 6, Limit 1) showed that its
  path-audit VOID dropped reps that had loaded the skill. The audit prints a cross-session tool or another
  extra tool in the init record, but it does not void the rep for it. Task 4's probe checks the tools.

A void rep is rerun once, with the next rep number in the same cell. If the rerun is void too, the cell stays
short of 3 valid reps, `tally` prints `verdict: incomplete`, and the controller asks the owner. A void rep's
cost still counts in the spend.

## Spend stop

The cap for every probe, pilot and rep of this test is $35. Per-rep `--max-budget-usd` is $0.25. At worst
case, 108 reps cost $27. The probe, two pilots and the void reruns come on top. Before each batch, check:
running total + the batch's reps × $0.25 ≤ $35. Stop when the check fails. Record each batch's cost as you go.

| Step | Reps | Cost | Running total |
|---|---|---|---|
| Task 3 (no model call) | 0 | $0.00 | $0.00 |

## Task 4: what the probe and the pilots must show

Task 3 cannot check these without a model, so Task 4 Step 1 checks them before any scored rep.

1. The probe: `run_trigger_reps.sh <old-ref> pilot probe <root>/probe/pilot/<model> 1 1 <model>`, in a root of
   its own. The answer must show no instruction file, no memory, no other session and only the planned tools.
   Line 6 of the probe asks about a list of skills. A trigger rep lists skills by design, so YES on line 6 is
   expected. `triggers.py listing` must show the three listing names.
2. The pilots: one rep per model on P1, arm `pilot`, from the `old` ref, in the same root as the probe. The
   skills sit in the rep's HOME, outside its working directory, under a `Read(~/**)` deny. A pilot or the
   probe must show that the `Skill` tool still works there: a `Skill` call whose tool result is not an error.
   If no `Skill` call succeeds, the setup cannot measure loads. Stop and ask.
3. A pilot that loads a skill must show no rule 4 finding in `audit.py`. Plan 102's probe saw a clean rep end
   with a task-notification result at `result_index` 2, after its own subagent handed back
   (`specs/history.md`). One skill in `skills/` (`tech-debt`) runs in a forked context, so a rep that loads it
   could end the same way. Rule 4 stays as registered. If a pilot is void on `result_index` and its stream
   shows a task notification, stop and ask before any scored rep.
4. A leak or a failed check stops Task 4.

## Deviations from plan 107's kit

1. The path audit, the Glob limits and the Bash audit are cut (VOID rule). Plan 111 registers no VOID reason
   for them.
2. The rep folder is removed after each rep, not parked. Rule 3 then covers every saved file, and no copy of
   claude's own state files in the rep's HOME stays on disk. The stream, the prompt and stderr stay in the
   scratch folder.
3. The listing names live in `fixtures/trigger/listing.txt`, beside the rep's project and not in it. The runner
   and the audit read the same file. The runner refuses a ref whose `skills/` lacks one of them, so no batch can
   void every rep through the listing check.
4. The prompt id `probe` runs `isolation_probe.txt` with a trigger rep's exact flags. Plan 107 ran its probe
   with the case runner's flags (`probe_tools.sh`), which this kit does not copy.
5. `tally` refuses an arm folder other than `old` and `new` and a model folder other than the two models.
   Plan 107's `tally` refused only an unknown prompt folder.
6. The kit errors, the integer reading of `result_index` and the rule 5 reading are stated in the VOID
   rule. The plan's Step 3 lists rules 3 to 5, an error result and the listing check.
