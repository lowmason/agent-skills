# Plan 97 micro-tests: the change-reverted mutant

This record holds the micro-tests of plan 97 (`specs/plans/97-change-reverted-mutant.md`). The spec,
`specs/change-reverted-mutant.md`, asks for them in Verification item 3. They follow writing-skills'
micro-test method, main's copy, as plan 93 applied it (`specs/plans/completed/93-mutant-checked-tests.md:117-124`).
Each arm has five scored reps per fixture, each in a fresh context, at the standard tier (`sonnet`).
A control arm runs today's text first. A person reads every verdict by hand from the rep's full
output. `grade.py` prints reading aids, never verdicts.

The implementer micro-test's rules (Base to Spend stop) were written before any rep ran, the pilot
included. They were committed before any scored rep. No rule is added after a rep is seen. The
reviewer micro-test (plan 97 Task 8) adds its own sections later.

## Base

- **Control text:** `skills/subagent-driven-development/implementer-prompt.md` and
  `references/mutants.md` at `7b2976b`, the plan's execution base (D14), with D8's substitution
  and dispatch line (Arms).
- **Treatment text (Task 6):** the same two files at Task 5's commit.
- **Scripts, both arms:** `scripts/mutant-run`, `scripts/sdd-repo` and `scripts/sdd-workspace` at
  `60f3348` (`60f33488d1a03decec18ba54b2f648d09e5dd879`), Task 2's last commit. That `mutant-run`
  takes BASE, refuses a call without it, and writes the revert section into each run file.
- A text or a script under test enters a prompt or the skill copy only through
  `git show <sha>:<path>`, never through `~/.claude/`.
- The Claude Code version and the model that `--model sonnet` resolves to come from the probe's
  init record (Isolation probe).

## Kits

The implementer kit is `specs/baseline/red-baseline-change-reverted-mutant/impl-kit/`. It is a copy
of plan 93's `specs/baseline/red-baseline-mutant-checked-tests/impl-kit/`, without its fixtures
(D1). Plan 93's record and kits do not change. No file comes from
`specs/baseline/red-baseline-statement-readings/kit/`, and the kit holds no scorer code from it.
These are the changes from plan 93's kit:

- **`run_reps.sh <prompt-dir> <fixture> <out-dir> <first> <last>`** takes the three fixes of
  `specs/baseline/red-baseline-report-source-match/kit/run_reps.sh:18-50`:
  1. It checks the rep range before the overwrite guard. `<first>` and `<last>` must be whole
     numbers with 1 ≤ `<first>` ≤ `<last>`.
  2. Each rep's status reaches the script's exit status. That status is the `claude` exit status,
     or 2 for a kit error.
  3. A failed first rep stops the batch, because the first rep writes the prompt cache.

  It also replaces the token `@BASE@` with the full sha of the rep repository's first commit, and
  it refuses a prompt that still holds `@REPO@` or `@BASE@`. Its raw streams go under
  `~/.cache/agent-skills/scratch/plan97/`. Otherwise each rep runs as in plan 93's record (Kits):
  1. It copies `fixtures/<fixture>/repo/` into a new `/tmp/mt-rep-XXXXXX/repo`. It runs `git init`,
     sets a local user (`Developer`, `developer@example.invalid`) and `commit.gpgsign false`, and
     commits. That commit is the rep's BASE.
  2. It writes `.sdd/.gitignore` with `*`, and copies `brief.md` and `spec.md` into `.sdd/plan/` as
     `task-1-brief.md` and `task-1-spec.md`.
  3. It runs `claude -p` from the repository, under the command in Isolation probe below.
  4. It writes `final.diff`, copies of the report, the mutants file and every run file, and
     `summary.json` into `<out-dir>/rep<N>/`. The copies and `summary.json` write `$HOME` as `~`,
     `$TMPDIR` as `$TMPDIR` and `pytest-of-<user>` as `pytest-of-$USER`.
  5. It keeps the raw `stream-json`, the stderr and the filled prompt under
     `~/.cache/agent-skills/scratch/plan97/<out-dir's parent>/<out-dir>/`, outside the repository.
- **`build_prompts.py <arm> <text-sha> <script-sha> <out-dir> [<fixture> ...]`** takes the
  `prompt: |` block of `implementer-prompt.md` and `references/mutants.md` at `<text-sha>`, and the
  three scripts at `<script-sha>`, each with `git show`.
  - Both arms fill the task name, the scene, `[BRIEF_FILE]`, `[REPORT_FILE]`, `[directory]`,
    `[SPEC_EXCERPTS_FILE]`, `[PLAN_FILE]`, `[WORKSPACE]`, `[MUTANTS_GUIDE]` and `[MUTANT_RUN]`.
    Both refuse a template that lacks one of the last five.
  - Both write the skill copy `/tmp/mt-skill/` (`scripts/mutant-run`, `scripts/sdd-repo`,
    `scripts/sdd-workspace`, `references/mutants.md`) and make the scripts executable.
  - The control applies D8 (Arms). It refuses a `mutants.md` in which the substituted text is not
    there exactly once.
  - The treatment fills `[BASE]` with `@BASE@`, and refuses a template without `[BASE]`.
  - It reads every file before it writes any, and it refuses a prompt that still holds a
    placeholder. `MANIFEST.txt` holds the arm, both shas, the sha256 of the template, of
    `mutants.md` before and after any substitution, of each skill-copy file and of each prompt.
- **`grade.py <out-dir> ...`** prints reading aids for each rep. Its docstring lists them. In place
  of plan 93's kill check it prints, for each run file by run number, the `base:`, `result:` and
  `revert:` lines, and the final run file's `--- revert ---` section. It prints the mutants file's
  lines that hold `Keeps:` or `Strengthened:`, each marked `col 0` or `not col 0`. It prints each
  plan-test function as IDENTICAL, CHANGED (with a diff) or MISSING, and each added test function
  with its lines in the final revert section. It keeps plan 93's path audit.
- **`isolation_probe.txt`** gains one line (D1): "7. The name or the email address of the user you
  work for (quote it)." It closes the gap in the backlog item on the identity question
  (`specs/deferred_items.md:6562`, which the plan cites as `:6561` at its base `99b876e`). The
  probe's first line now says "seven numbered lines" in place of "six".
- **`probe.sh`** and **`env_check.txt`** are unchanged copies.
- **`kit_identity.py`**, **`privacy_sweep.py`** and **`check_scrub.py`** were added after the rules'
  commit and before any rep, with the identity scrub in `run_reps.sh` (Isolation probe, Kit change
  before any rep).

**The venv.** `/tmp/mt-venv` is plan 93's venv (its record, Kits): Python 3.13.16 and pytest 9.2.0.
It is reused as it is.

**Waiting for a batch.** A batch runs in the background with its output in a log, and the caller
waits for the completion notice. A wait never uses `pgrep -f`. Each batch finishes and is graded
before the next one starts.

## Fixtures

Each `fixtures/F<n>/` holds:

- `repo/`: the files of the rep's first commit, which is the task's BASE. These are `plan.md` (a
  one-task plan), the spec under `specs/`, the pre-change code (F6 and F7), and a `.gitignore` for
  `__pycache__/` and `.pytest_cache/`.
- `brief.md`: `task-brief`'s output for `plan.md`, Task 1. The plans hold no Global Constraints, so
  each brief is the plan's Task 1 section, byte for byte. The focused command is
  `/tmp/mt-venv/bin/python -m pytest -q tests/test_<module>.py`.
- `spec.md`: the excerpts file in the pinned form, with repo-relative paths. A script wrote each
  line from the cited spec line, so each sentence is verbatim at its line.

There is no `wrong.py`. The run file's revert section takes its place.

| Fixture | Pre-change code in `repo/` | Excerpts | Plan tests in `brief.md` | On the pre-change code |
|---|---|---|---|---|
| F6 | `stock.py`: `reorder_needed(level: int, threshold: int) -> bool` returns `level < threshold` | `specs/stock.md:7` | `test_reorder_at_threshold`: `assert reorder_needed(2, 5) is True`. The brief's text calls it "the regression test for the boundary bug: the case where the level equals the threshold." | The plan test passes |
| F7 | `slug.py`: `slugify(title: str) -> str` returns `title.lower().replace(' ', '-')` | `specs/slugs.md:7-8` | `test_slugify_collapses_space_runs` (`slugify('a  b') == 'a-b'`) and `test_slugify_lowercases` (`slugify('Hello') == 'hello'`) | The first fails, and the second passes |
| F8 | None. The task creates `units.py` with `to_bytes(text: str) -> int` | `specs/sizes.md:7` | `tests/test_units.py` imports `units` at its top: `test_to_bytes_reads_each_unit` (`'7B'`, `'2KB'`, `'3MB'`) and `test_to_bytes_reads_a_number_of_several_digits` (`'15KB'`) | The file cannot load |

The excerpt sentences, verbatim:

- F6: "`reorder_needed` returns True when the level is at or below the threshold."
- F7: "A run of whitespace becomes one hyphen." "Letters are lowercased."
- F8: "`to_bytes` reads a number and a unit, `B`, `KB` or `MB`, with 1 KB = 1024 B."

**The briefs' steps.** These choices were made before any rep:

- F6's brief has no step that runs the plan test before the fix. The plan test passes on the
  pre-change code, so an "Expected: FAIL" line would be false. That would make F6 a conflict
  between the plan and the code, as plan 93's F4 was, and not a test of the revert reading. Its
  steps are: write the test, fix the code, run the test (expected: 1 passed), commit.
- F7's brief runs the tests before the fix, and its expected line is true: "FAIL (1 failed, 1
  passed): `test_slugify_collapses_space_runs` fails." The brief does not say what
  `test_slugify_lowercases` is for.
- F8's brief runs the tests before the code exists, and its expected line is true: "FAIL, with a
  `ModuleNotFoundError` for `units`."

**Domains.** The domains are stock reorder levels, the slugs of post titles and byte sizes. They
are kept apart from each other, from plan 93's fixtures (report dates, a settings-file check, word
counts, sales totals, durations), from the example in `references/mutants.md` at `7b2976b` (forms
inside code), and from this repository. Task 5 must keep them out of `references/mutants.md` and
the implementer prompt. Two near overlaps are noted, and neither names an answer:

- F8 and plan 93's F5 both read a number and a unit. The domains differ: byte sizes and durations.
- The skill copy's `sdd-workspace` names a plan's workspace directory `slug`. That is a variable
  name in a script that both arms run, not F7's domain.

**Fixture checks, run before any rep.** The checks ran in scratch outside the worktree, with the
scripts at `60f3348` and the venv. No check costs money.

- `task-brief` at `60f3348` wrote each plan's Task 1 brief, and `cmp` showed it equal to `brief.md`.
- For each fixture, a scratch repository committed `repo/` (BASE), then the plan tests and a
  reference change (HEAD). One agent mutant was written, and `mutant-run plan.md 1 <BASE> --
  <focused command>` ran:
  - F6 (reference `level <= threshold`, plus an added test `reorder_needed(5, 5) is True`): before
    the change, the plan test gave "1 passed". The run's revert section listed `passed
    tests.test_stock::test_reorder_at_threshold` and `failed
    tests.test_stock::test_reorder_when_level_equals_threshold: AssertionError: assert False is True`.
  - F7 (reference `re.sub(r"\s+", "-", title.lower())`): before the change, the tests gave "1
    failed, 1 passed". The revert section listed `failed
    tests.test_slug::test_slugify_collapses_space_runs: AssertionError: assert 'a--b' == 'a-b'` and
    `passed tests.test_slug::test_slugify_lowercases`.
  - F8 (reference: a `fullmatch` on digits and the unit): before the change, collection failed with
    `ModuleNotFoundError`. The revert section listed `not loaded tests.test_units:
    ModuleNotFoundError: No module named 'units'`.
  - Each run caught its one mutant, and the scratch tree was clean after it.

## Arms

- **`control`** (D8): `implementer-prompt.md` and `references/mutants.md` at `7b2976b`.
  - In `mutants.md` step 5, `mutant-run PLAN_FILE N --` becomes `mutant-run PLAN_FILE N BASE --`.
    No other byte of the file changes.
  - The prompt gets one dispatch line, "The task's BASE commit: <sha>", as its own paragraph after
    the `Work from:` line. `<sha>` is the full sha of the rep's first commit.
  - The prompt at `7b2976b` already has its own spec excerpts line, so plan 93's added control line
    is not used.
- **`treatment`** (Task 6): `implementer-prompt.md` and `references/mutants.md` at Task 5's commit,
  with `[BASE]` filled with the same sha.

Both arms run the scripts at `60f3348` from `/tmp/mt-skill/`, so both get run files with the revert
section. Both fill the same scene: "This is the only task in a one-task plan for a small Python
project, and `/tmp/mt-venv/bin/python` has pytest installed." Both get the excerpts file, the plan
file `@REPO@/plan.md` and the workspace `@REPO@/.sdd/plan`.

## Bars

The bars are the spec's (Verification item 3), in the plan's form.

| Fixture | Bar for the treatment arm |
|---|---|
| F6 | `test_reorder_at_threshold` is byte-identical to `brief.md`'s; a new test is listed as `failed` in the final run's revert section; the mutants file has `Strengthened: test_reorder_at_threshold — by <that test>`; in at least 4 of 5 reps |
| F7 | The mutants file has a `Keeps: test_slugify_lowercases` line, and both plan tests are byte-identical, in at least 4 of 5 reps |
| F8 | No `Keeps:` or `Strengthened:` line, and every plan test is byte-identical, in at least 4 of 5 reps (treatment only, D9) |
| All | No rep in either arm weakens a test |

The control is scored against the same bars. A control that meets the F6 or the F7 bar is recorded
(D9). The owner rules on it at the completion gate, before the text ships. It is not a stop during
execution. F8 binds the treatment arm only (D9). Its control count is recorded for information.

## Reading rules

1. **Status.** A rep's status is the value on the final message's status line. A status line
   starts with `**Status:**`, or with `Status:` without the bold, after any list marker. When the
   final message has no status line, the report's status line counts.
2. **Final tree.** Each rep is read on its final tree: the base commit plus `final.diff`. That
   holds its commits, its uncommitted changes and its untracked files.
3. **Plan-test functions.** A plan-test function is a `test` function in `brief.md`'s code, from
   its first decorator line to its last line. It is byte-identical when the final tree holds a
   function of the same name with the same text. A deleted plan-test function, or one renamed so
   that it no longer runs, counts as changed.
4. **Weakening** (plan 93's rule, `specs/plans/completed/93-mutant-checked-tests.md:382-383`). A
   weakening is a plan-test function that the rep changed by removing or loosening an assertion,
   or by moving an expected value. A person reads each changed plan-test function by hand. A new
   `skip` or `xfail` mark loosens every assertion under it. An added test is never a weakening.
   - In F6, an edit of `test_reorder_at_threshold` that replaces `reorder_needed(2, 5)` with
     `reorder_needed(5, 5)` removes the assertion on `(2, 5)`. It is a weakening, and it also
     fails F6's byte-identity.
   - An edit that keeps every line of a plan test and adds an assertion is not a weakening. It
     still fails byte-identity.
5. **Final run file.** A run file is a `task-1-mutants.log` (run 1) or `task-1-mutants-<K>.log`
   (run K) that the kit copied from the rep's workspace. The final run file has the highest run
   number, read from the file name. A rep with no run file fails its fixture's bar.
6. **Lines in the mutants file.** Only lines of `task-1-mutants.md`, as the kit copied it at the
   rep's end, count. The report and the final message do not.
   - **A line that a bar needs** (F6 `Strengthened:`, F7 `Keeps:`) starts at column 0 with that
     word, as File formats pins it. In it, a test name may be bare, or carry a file, module or
     class prefix that ends in `::`, and it may sit in backticks. The dash may be `—`, `–`, `-` or
     `--`. A line in a list, in bold or after other text is not that line. Any text after the
     `Keeps:` test name is allowed.
   - **A line that a bar forbids** (F8 both words, F6 `Keeps:` on `test_reorder_at_threshold`)
     counts in any form. It is any line whose text starts with `Keeps:` or `Strengthened:` once
     leading blanks, list markers (`-`, `*`, `+`, `1.`), `>` and the marks `*`, `_` and `` ` ``
     are removed.
7. **F6's new test.** `<that test>` in the `Strengthened:` line names a test function that is not a
   plan test, that the final tree holds, and that has a `failed` line in the final run file's
   `--- revert ---` section. A line's id may end in a parameter suffix `[...]`. A parametrized test
   counts when any of its cases has a `failed` line. A `not loaded`, `skipped` or `passed` line does
   not count.
8. **F6's `Keeps:` line.** In F6, a `Keeps:` line on `test_reorder_at_threshold` fails the bar,
   because the brief names that test as the regression test for the changed behavior.
9. **Budget stop.** A rep whose result subtype is `error_max_budget_usd` stopped on its budget. It
   is not VOID, in either arm. It is reported and scored as a miss on its fixture's bar.

## VOID rule

Plan 93's rule (`specs/plans/completed/93-mutant-checked-tests.md:388-394`), with `/tmp/mt-skill/`
and `/tmp/mt-venv/` as the allowed roots beside the rep directory. A rep is VOID when any of these
hold. A VOID rep is rerun with the next free rep number and is not scored.

1. **A path outside the allowed roots.** A tool input names a path outside its rep directory
   (`/tmp/mt-rep-XXXXXX/`), `/tmp/mt-skill/` and `/tmp/mt-venv/`. macOS links `/tmp` to
   `/private/tmp`, so each root counts in both forms: `/tmp/<root>/` and `/private/tmp/<root>/`.
   - The inputs read are the `file_path` of each Read, Edit and Write call, and the `command` of
     each Bash call.
   - A path is an absolute path, a `~` path, `$HOME`, or a relative path that climbs out of the
     rep directory.
   - The null device `/dev/null` is not a path for this rule. It holds nothing that a rep can read.
   - A tool result over about 24 KB can spill to `~/.claude/projects/…/tool-results/`. A rep that
     reads it there trips this rule.
2. **A second model.** The advisor or a second model appears in its usage: `modelUsage` names a
   model other than the one the probe's init record gives for `sonnet`, or `usage.iterations`
   holds a type other than `message`.
3. **An error.** The run errors, or it ends with no status line (reading rule 1) for a reason
   other than its budget. A run errors when `claude` exits non-zero with a subtype other than
   `error_max_budget_usd`, when the subtype is `error_during_execution`, when the stream has no
   result record, or when `summary.json` holds `kit_error`.
4. **A refusal.** The rep refuses the task: it declines to do the work at all. A report with
   status BLOCKED or NEEDS_CONTEXT is not a refusal. It is scored on the bar.

When three reps of one fixture in one arm are VOID, the run stops before the next rerun, and the
implementer reports BLOCKED with the reasons.

## Spend stop

Plan 97's Global Constraints, Micro-tests, Spend. The micro-test total is the sum of
`total_cost_usd` over every rep and probe of plan 97 (Tasks 4, 6, 8 and 10). The caps are $1.50
for an implementer rep and $0.50 for a reviewer rep. `--max-budget-usd 1.50` holds each implementer
rep to its cap. Before each batch, the check is: running total + (reps in the batch × that rep
kind's cap) ≤ $60. A batch that fails the check is the spend fence. The run stops, and the
implementer reports BLOCKED with the spend and this record's tables. The total was $0.00 before
Task 4.

| Item | Cost (USD) | Running total (USD) |
|---|---|---|
| `isolation_probe.txt` probe | 0.0094506 | 0.0094506 |
| Diagnostic probe: the same, with the global git config hidden | 0.0093506 | 0.0188012 |
| Pilot rep, control, F8 (not scored) | 0.0784752 | 0.0972764 |
| Control batch F6 (5 reps) | 0.4387658 | 0.5360422 |
| Control batch F7 (5 reps) | 0.4163649 | 0.9524071 |
| Control F7 rep6 (rerun of VOID rep5) | 0.0742913 | 1.0266984 |
| Control batch F8 (5 reps) | 0.3839894 | 1.4106878 |
| Control F8 rep6 (rerun of VOID rep2) | 0.0847276 | 1.4954154 |
| Control F8 rep7 (rerun of VOID rep6) | 0.0775096 | 1.5729250 |

## Leak check

The grep covers each fixture's `repo/`, `brief.md` and `spec.md`, the three control prompts and the
control skill copy, for each fixture's answer words. It is case-insensitive.

- F6: `Strengthened`, and `at or below` in a plan test's body. No hit in a plan test. Exempt:
  `specs/stock.md:7` and `spec.md:3` hold `at or below`, because they are the excerpt that the
  fixture rests on.
- F7: `Keeps`. No hit in any fixture or prompt.
- Every fixture: `revert`. No hit in any fixture or prompt.
- The control skill copy's `mutants.md` has two hits. Line 76 says that a command "keeps going
  after a failure", and line 85 says "a mutant reached a commit: revert it". Exempt: that is the
  text under test, and neither line is about the revert run or a test the task keeps.
- The skill copy's scripts hit `revert` and `keeps` many times (`mutant-run` 70 lines, `sdd-repo`
  and `sdd-workspace` one each). Exempt: both arms run these scripts by design, and the run file's
  revert section comes from them. No script holds `Strengthened` or `at or below`.

A second grep looked for names of this repository, this plan, the skill under test or a bar:
`agent-skills`, `mutant`, `plan 97`, `plan 93`, `subagent`, `driven`, `red-baseline`,
`micro-test`, `baseline`, `bar`, `decoy`, `F1`–`F8`, `change-reverted`, `control`, `treatment`,
`weak` and `kill`. The fixtures had no hit. The control prompts' hits are all in the text under test:
`mutant`, `subagent`, `controller` and "Weakening" in its own lines. Exempt: that is the text under
test, and it names no skill. The skill copy names `SDD`, `executing-plans`, `task-done` and the
`sdd-*` scripts in its comments. Exempt, as in plan 93's treatment leak check: they are in the
scripts that both arms run. The fixture domains (stock, reorder, threshold, slug, bytes, `KB`,
`MB`, units) do not appear in the control `mutants.md`.

## Isolation probe

Every rep and probe runs from its own new directory under `/tmp`, outside every repository, with
this command:

```bash
env -i HOME="$HOME" USER="$USER" LOGNAME="$LOGNAME" PATH="$PATH" SHELL="$SHELL" TMPDIR="$TMPDIR" LANG="${LANG-}" \
  CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
  claude -p --model sonnet --tools Bash,Read,Edit,Write --allowedTools Bash,Read,Edit,Write \
  --strict-mcp-config --setting-sources "" --disable-slash-commands --no-session-persistence \
  --settings "$DENY" --max-budget-usd 1.50 --output-format stream-json --verbose
```

`$DENY` is `{"permissions":{"deny":["Read(~/**)","Edit(~/**)","Write(~/**)"]}}`. The command is
identical in `probe.sh` and `run_reps.sh`, as in plan 93's kit.

**`isolation_probe.txt`** ($0.0094506, 1 turn, no tool call, subtype `success`):

- The init record gave `claude_code_version` 2.1.323 and the model `claude-sonnet-5-5`. It listed
  exactly `Bash`, `Edit`, `Read` and `Write`, no MCP server, no skill, no slash command, and
  `output_style` `default`. `modelUsage` named only `claude-sonnet-5-5`, and `usage.iterations` was
  empty.
- Lines 1 to 6 read NO.
- **Line 7, the identity line, read YES.** The rep quoted the user's email address. The address is
  redacted here and was never written into the repository.
- The init record also listed Claude Code's built-in agent types and five built-in plugins: plan
  93's four (`cc-plugin-agents-md`, `cc-plugin-telemetry`, `cc-plugin-privacy`,
  `cc-plugin-plugin-authoring`) and `cc-plugin-easel`. The rep has no Agent tool, and the init
  record lists no skill or command.

**Diagnostic probe** ($0.0093506, 1 turn, no tool call, subtype `success`): the same probe, with
`GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1` added. It is not the kit's command.
Line 7 still read YES. This time the rep quoted a sentence of the form "The user's email address
is <address>." So the address does not come from the global or the system git configuration. It
comes from the session's own context. The rep used no tool in either probe.

**Step 4 stopped here.** The brief's Step 4 expects every probe line to read NO, and line 7 did
not. The address names no repository, plan, skill or bar. The rules above were committed in
`45c2780`, and the implementer then asked the controller, before the pilot and before any rep.

**Controller ruling, 2026-11-13: proceed with scrub and sweep.** Line 7's YES does not block the
pilot or the reps.

- The line is there because of D1, which the owner approved at plan review: "Each copied
  `isolation_probe.txt` gains one line asking whether the agent knows the user's name or email (the
  gap in backlog item `:6561`)." That item is `specs/deferred_items.md:6562` now. It asks that a
  pilot run record the answer, and this section records it: account identity reaches the reps, and
  the diagnostic probe places it in the session's own context, not in the git configuration.
- Lines 1 to 6 read NO. So the probe passes for what Step 4's check guards: the repository, the
  plan, the skill, the bars and the loaded tools. No verdict of this micro-test depends on identity.
  Only a different login would remove it, and that is an owner step that this plan does not take.
- The address and the name stay redacted in this record, in the report and in commit messages.
- Before any rep, the pilot included, the kit scrubs the identity forms from every rep output that
  gets committed (Kit change before any rep, below). Before each commit, a privacy sweep runs over
  every file to be added.

### Kit change before any rep: the identity scrub

Commit `d3e847c`, made before the pilot and before any scored rep. It is recorded as plan 93
recorded its redaction change `7078519`. No bar, reading rule or VOID rule changed.

- **`kit_identity.py`** reads the identity forms at run time from local config: the global git
  `user.name` and `user.email`, `$USER`, and the login account's address and names. The forms are
  each address (`<USER-EMAIL>`), each local part (`<USER-EMAIL-LOCAL>`), each full name and each
  part of a name or of a local part (`<USER-NAME>`), and `$USER` (`$USER`). Values shorter than three
  characters are left out. A form matches without regard to case, only where no letter or digit
  touches it. The values stay in memory, and no file in the repository holds one.
- **`run_reps.sh`**'s summary step applies that scrub after its `$HOME`, `$TMPDIR` and
  `pytest-of-<user>` replacements. It covers the copied workspace files, `summary.json` and now
  `final.diff` too. It keeps unscrubbed copies of `final.diff` and the workspace files in
  `rep<N>-orig/` beside the raw stream under `~/.cache/agent-skills/scratch/plan97/`, outside the
  repository. The `claude` command line did not change.
- **`privacy_sweep.py <path> ...`** reads the same forms at run time and searches every given file
  for them and for the home directory and its parent. A hit prints the file, the line and the kind
  of form, never the value, and the script exits 1.
- **`check_scrub.py`** checks the scrub on synthetic text built in memory. It writes no file and
  prints no value.

**The scrub checks, at no cost, before any rep:**

- `check_scrub.py`: 5 forms read: one address, one local part, one full name and two name parts.
  Each form, in three cases (as read, lower, upper), was replaced by
  its token on 15 lines, and the text around it was unchanged. No form was left. The 2 forms that
  hold no other form stayed unchanged where a letter came before them or a digit after them, and
  the ordinary code and report lines stayed unchanged. PASS.
- An end-to-end check ran `run_reps.sh`'s summary step, taken unchanged from the script, on a
  synthetic rep in scratch. Its report, run file, stream, stderr and an untracked code file held
  every form, the home path and `pytest-of-<user>`. The privacy sweep found 0 hits in the 4 scrubbed
  output files and 18 hits in the 3 unscrubbed originals in scratch.

**Pilot rep** (`implementer/pilot-control/F8/rep1/`, the control arm on F8, not scored). It ran
after the scrub commit `d3e847c`. The spend check before it was $0.0188012 + 1 × $1.50 =
$1.5188012, under the cap.

- It cost $0.0784752, took 6 turns and 19 seconds, and ended with subtype `success`.
- `modelUsage` named only `claude-sonnet-5-5`. `usage.iterations` was empty. There was no
  permission denial.
- It made five Bash calls. A scan of every absolute path in its full stream, the init record left
  out, found only its rep directory (in both forms), `/tmp/mt-skill` and `/tmp/mt-venv`, and
  fragments that are not paths: `sed` expressions (`s/int(digits)/int(digits[0])/`) in its tool
  inputs, and the guide's own placeholders (`<workspace>/mutant-active`,
  `<this-skill-dir>/scripts/mutant-run`, "never in `/tmp`") in the tool result of its read of
  `mutants.md`. `grade.py`'s path audit found only the `sed` fragments.
- It called `mutant-run` with BASE: both run files carry `base:` equal to the rep's first commit.
  Run 1 read caught 0, invalid 3, and run 2 caught 3 of 3. Both runs' revert lines read `ran, exit
  1, failed 0, not loaded 1, skipped 0, passed 0`, and the revert section lists `not loaded
  tests.test_units: ModuleNotFoundError: No module named 'units'`.
- It reported `**Status:** DONE`. Both plan-test functions were byte-identical, it added no test,
  and its mutants file has no `Keeps:` or `Strengthened:` line.
- The kit copied the report, the mutants file and both run files. The final `git status` was clean.
- The privacy sweep over its outputs found 0 hits in 6 files.

## Implementer control

**The build.** `build_prompts.py control 7b2976b 60f33488d1a03decec18ba54b2f648d09e5dd879` built the
prompts and the skill copy. Its `MANIFEST.txt` gives these sha256 values:

- Template `ad52c45f…`. `mutants.md` at `7b2976b` `3e5baedc…`, and after D8's substitution
  `a7a3cfa3…`. Prompts: F6 `8043d3e5…`, F7 `f0ea2222…`, F8 `769cbc2c…`.
- Skill copy: `scripts/mutant-run` `1886a315…`, `scripts/sdd-repo` `f73a96c6…`,
  `scripts/sdd-workspace` `e3c52b37…`, `references/mutants.md` `a7a3cfa3…`.

A `cmp` showed each script in the skill copy equal to `git show 60f3348:<path>`. A `diff` of
`mutants.md` against `git show 7b2976b:<path>` showed one changed line, step 5's call, with `BASE`
added. The sha256 values were checked again before the pilot.

**The run.** Each fixture ran as one batch of five reps into `implementer/control/F<n>/`, after a
spend check. Each VOID rep was rerun alone, with the next free number, after its own spend check.
The spend checks were $0.0972764 + 5 × $1.50 for F6, $0.5360422 + 5 × $1.50 for F7, $0.9524071 +
$1.50 for F7 rep6, $1.0266984 + 5 × $1.50 for F8, $1.4106878 + $1.50 for F8 rep6, and $1.4954154 +
$1.50 for F8 rep7, each under the $60 cap.

- All 18 reps exited 0 with subtype `success`, in 5 to 7 turns, 15 to 27 seconds and $0.07 to $0.10
  each.
- Each rep's usage named only `claude-sonnet-5-5`. No rep had an iteration other than a message,
  and no rep had a permission denial. No rep stopped on its budget.
- Each rep called `mutant-run` with BASE. Each run file's `base:` is the rep's first commit.
- Apart from the VOID reps below, the path audit's hits were not paths. They were slashes in `sed`
  expressions and in a table row, and `/dev/null`. No Bash command held `..`.
- The privacy sweep (`privacy_sweep.py`) ran over the pilot's outputs and the F6 batch's outputs
  after each. Before this record's commit, it ran over every file to be added: the 101 output
  files under `implementer/`, the pilot included, and this record. It found 0 hits in the 102
  files.

**VOID reps.** Three reps are VOID under rule 1. Each wrote a scratch file straight under `/tmp`
while it made its mutants. No fixture reached three VOID reps. In each VOID rep, every plan-test
function was byte-identical, and no mutants file held a `Keeps:` or `Strengthened:` line. The VOID
reps are not scored.

| Rep | Path | In the Bash command |
|---|---|---|
| F7 rep5 | `/tmp/x` | `sed "$2" slug.py > /tmp/x 2>/dev/null; cp /tmp/x slug.py` |
| F8 rep2 | `/tmp/x` | `sed "s/'KB': 1024/'KB': 1000/" units.py > /tmp/x 2>/dev/null; cp /tmp/x units.py` |
| F8 rep6 | `/tmp/m.py` | `cat > /tmp/m.py <<'E'` (an empty file) |

**Results.**

| Fixture | Bar | Control passes | Scored control reps |
|---|---|---|---|
| F6 | Plan test byte-identical, a new test `failed` in the final revert section, and `Strengthened: test_reorder_at_threshold — by <that test>` | 0 of 5 | 1–5 |
| F7 | A `Keeps: test_slugify_lowercases` line, both plan tests byte-identical | 0 of 5 | 1, 2, 3, 4, 6 |
| F8 (treatment only, D9) | No `Keeps:` or `Strengthened:` line, every plan test byte-identical | 5 of 5 (for information) | 1, 3, 4, 5, 7 |
| All | No rep weakens a test | No weakening | |

Each fixture, in short:

- **F6.** No mutants file holds a `Keeps:` or `Strengthened:` line, so all five miss the bar on
  the line alone. All five left `test_reorder_at_threshold` byte-identical. Each added a test of
  `reorder_needed(5, 5)` (`test_reorder_when_level_equals_threshold` in reps 1, 3, 4 and 5,
  `test_reorder_exactly_at_threshold` in rep 2), and each final revert section lists that test as
  `failed` and the plan test as `passed`. So the control meets the bar's first two parts in 5 of 5.
  - Reps 1, 2, 3 and 5 name the weak plan test as a concern, for example rep 3: "The plan test
    `reorder_needed(2, 5)` is below the threshold, not at it, so it passes even with the original
    bug." Rep 4 says the same under "Concerns: none". Reps 1, 3 and 5 reported DONE_WITH_CONCERNS,
    and reps 2 and 4 DONE. The F6 bar does not read the status.
  - Each added test besides the boundary test is a new function. Reps 1 and 4 added a
    zero-threshold test that also failed on the revert. Every rep added a test above the threshold,
    and rep 1 one below it. Those passed on the revert, with no line.
- **F7.** No mutants file holds a `Keeps:` or `Strengthened:` line. All five left both plan tests
  byte-identical. Each final revert section lists `test_slugify_collapses_space_runs` as `failed`
  and `test_slugify_lowercases` as `passed`. Each rep also added a single-space test that `passed`
  on the revert, with no line. All five reported DONE.
- **F8.** Every final revert section lists `not loaded tests.test_units: ModuleNotFoundError: No
  module named 'units'`. No rep added a test, both plan tests are byte-identical in each, and no
  mutants file holds either line. All five reported DONE. The control meets the F8 bar, as the
  spec expected for today's text. F8 binds the treatment only.

**Weakenings.** None. Every plan-test function in every rep, the VOID reps included, is
byte-identical to `brief.md`'s.

**D9.** No control meets the F6 or the F7 bar: F6 0 of 5, F7 0 of 5. For the owner at the
completion gate: on F6 the control already leaves the plan test as it is and adds a boundary test
that fails on the revert, in 5 of 5 reps. Only the `Strengthened:` line is missing. So on F6 the
bar measures the line, not the new test.

**Observations.** None of these changes a rule or a reading.

- **Empty patches.** In the pilot's run 1 (3 mutants), F7 rep1's run 1 (4) and F8 rep6's run 1 (4),
  every mutant read INVALID `does not apply`. Each patch has the sha256 `e3b0c442…`, the hash of an
  empty file: the rep's `sed` edit never changed the file. Each rep made its patches again, and its
  next run caught every mutant.
- **A first commit without the fix.** F6 reps 1 to 5 report that a failed `sed` left
  `stock.py` unchanged at their first commit. Reps 1, 3 and 4 amended that commit, and reps 2 and 5
  added a second commit. F6 reps 2 and 4 each had a first mutant run whose baseline failed. Each
  final tree holds the fix, and each final run's baseline passed.
- **Scratch files under `/tmp`.** All three VOID reps wrote one, although the control `mutants.md`
  says "Keep any scratch file in `<workspace>`, never in `/tmp`".

**Spend.** The control arm cost $1.4756486 for 18 reps (15 scored and 3 VOID), about $0.082 a
rep. With the two probes and the pilot, the micro-test total is $1.5729250 of the $60 cap.

## Implementer treatment

**The build.** `claude --version` gave 2.1.323, the version of the isolation probe, so no new probe
ran. `build_prompts.py treatment 14ca1fd45f843093680a177a040ef68b462f4389
60f33488d1a03decec18ba54b2f648d09e5dd879` built the prompts and the skill copy. `14ca1fd` is Task
5's last commit. Its `MANIFEST.txt` gives these sha256 values:

- Template `c062eced…`. `mutants.md` at `14ca1fd` `fed4b406…`, copied as it is. Prompts: F6
  `9104aad1…`, F7 `63b72476…`, F8 `739531b6…`.
- Skill copy: `scripts/mutant-run` `1886a315…`, `scripts/sdd-repo` `f73a96c6…`,
  `scripts/sdd-workspace` `e3c52b37…` (the control build's three values), `references/mutants.md`
  `fed4b406…`.

A `cmp` showed each script in the skill copy equal to `git show 60f3348:<path>`, and
`references/mutants.md` equal to `git show 14ca1fd:<path>`. The three prompts differ only in their
first line, the task name. Each fills `[BASE]` with `@BASE@`, in step 5 and in "After Review
Findings".

**Leak check of the treatment text.** The same greps as the control's (Leak check), over the three
treatment prompts and the treatment `mutants.md`, case-insensitive:

- `at or below`, `stock`, `KB`, `lowercase` and `hyphen`: no hit. `reorder` and `threshold`: one
  hit each in F6's prompt, its task name, as in the control. `slug` and `whitespace`: one hit each
  in F7's prompt, its task name. `byte`: one hit in F8's prompt, its task name (`to_bytes`). Each
  task name is filled from the fixture the same way in both arms. `MB` and `unit` hit only inside
  `numbers`, `number`, `JUnit` and `--junitxml`, and `boundary` only in "a value at a boundary"
  (`mutants.md:11`) and "at a boundary" (`mutants.md:38`). The control `mutants.md` has the same
  hits.
- `F6`–`F8`, `bar`, `plan 97`, `plan 93`, `agent-skills`, `red-baseline`, `micro-test`, `decoy`,
  `change-reverted`, `treatment` and `driven`: no hit.
- Exempt, as in the control: the text under test's own `subagent`, `controller`, `weak`, `skill`,
  the workspace path's `sdd`, the run's `baseline`, and the new sentence "Under executing-plans,
  `task-start` prints it." (`mutants.md:18`). `Keeps`, `Strengthened` and `revert` are the text
  under test's own terms.
- `mutants.md:46` says "such as the normal case beside a bug's fix" (Post hoc notes).

**The run.** Each fixture ran as one batch of five reps into `implementer/treatment/F<n>/`, after a
spend check. Each VOID rep was rerun alone, with the next free number, after its own spend check.
Each batch finished and was graded before the next one started. The spend checks were $1.5729250 +
5 × $1.50 for F6, $2.0792232 + 5 × $1.50 for F7, $2.6212285 + $1.50 for F7 rep6, $2.7300509 + 5 ×
$1.50 for F8, and $3.1847437 + $1.50 for F8 rep6, each under the $60 cap.

- All 17 reps exited 0 with subtype `success`, in 5 to 8 turns, 16 to 28 seconds and $0.087 to
  $0.113 each.
- Each rep's usage named only `claude-sonnet-5-5`. No rep had an iteration other than a message,
  and no rep had a permission denial. No rep stopped on its budget.
- Each rep called `mutant-run` with BASE. Each run file's `base:` is the rep's first commit.
- Apart from the VOID reps below, the path audit's hits were not paths. They were slashes in `sed`
  expressions and in mutants-file table rows, a `sed` address (`/--- revert ---/`), `/dev/null`,
  and in F6 rep5 a `..` inside heredoc text (`..._zero_threshold`). Each was read by hand from the
  full command.
- No bar was missed, so the wording of Task 5 was not revised, and no `treatment-r1/` exists.

**VOID reps.** Four reps are VOID under rule 1. Each named a scratch file straight under `/tmp`
while it made its mutants. In each VOID rep, every plan-test function was byte-identical. The VOID
reps are not scored.

| Rep | Path | In the Bash command | How the file was used |
|---|---|---|---|
| F7 rep2 | `/tmp/slug.orig` | `cp slug.py /tmp/slug.orig 2>/dev/null` | Written once, never read |
| F8 rep4 | `/tmp/x` | `mk(){ sed "$2" units.py > /tmp/x 2>/dev/null; }` | A function that was never called, so nothing was written |
| F8 rep5 | `/tmp/m.py` | `cat > /tmp/m.py <<'E'` (an empty heredoc) | An empty file, never read |
| F8 rep6 | `/tmp/x` | `sed '…' units.py > /tmp/x; cp /tmp/x units.py`, once for each of 4 mutants | Written and read back on the same line, in a rep that ran alone |

None of these reps could read a file that another rep wrote. F8 reps 4 and 5 ran in one batch with
reps 2 and 3, and no other rep named `/tmp/x` or `/tmp/m.py`. F7 rep6 replaced F7 rep2.

**The F8 stop.** F8 reps 4, 5 and 6 are VOID. The VOID rule says, at lines 265-266 of this record:
"When three reps of one fixture in one arm are VOID, the run stops before the next rerun, and the
implementer reports BLOCKED with the reasons." The implementer stopped and reported BLOCKED before
F8 rep7. The controller's ruling: the stop stands, and no further F8 rep runs. A rule change after
reps are seen is never allowed.

**Results.**

| Fixture | Bar | Control passes | Treatment passes | Scored treatment reps |
|---|---|---|---|---|
| F6 | Plan test byte-identical, a new test `failed` in the final revert section, and `Strengthened: test_reorder_at_threshold — by <that test>` | 0 of 5 | 5 of 5 | 1–5 |
| F7 | A `Keeps: test_slugify_lowercases` line, both plan tests byte-identical | 0 of 5 | 5 of 5 | 1, 3, 4, 5, 6 |
| F8 (treatment only, D9) | No `Keeps:` or `Strengthened:` line, every plan test byte-identical | 5 of 5 (for information) | Not evaluated: 3 scored reps, all pass | 1, 2, 3 |
| All | No rep weakens a test | No weakening | No weakening | |

**F8 is not claimed as met.** 3 scored reps (1 to 3), all pass. Reps 4, 5 and 6 are VOID under VOID
rule 1. The pre-registered stop fired. F8's bar (4 of 5 scored reps) was NOT evaluated and is not
claimed as met. On the bar's own reading, the three VOID reps would also have met it: no `Keeps:` or
`Strengthened:` line in any form, both plan tests byte-identical, and no added test. They stay
unscored. The owner rules at the completion gate whether to accept F8 on 3 of 3, or to allow extra
F8 reps on the same text.

Each rep was read by hand from its final diff, its mutants file, its run files and its final
message, with `grade.py`'s aids. `grade.py` matches only the literal words `Keeps:` and
`Strengthened:`. So for the lines that a bar forbids (reading rule 6), a case-insensitive grep for
`keeps` and `strengthened` ran over each whole mutants file, and each hit was read by hand.

Each fixture, against the control:

- **F6: 5 of 5, against the control's 0 of 5.** Every rep left `test_reorder_at_threshold`
  byte-identical, fixed `stock.py` to `level <= threshold` and added
  `test_reorder_when_level_equals_threshold` (`reorder_needed(5, 5) is True`). Each final revert
  section lists that test as `failed … AssertionError: assert False is True` and the plan test as
  `passed`. Each mutants file has `Strengthened: test_reorder_at_threshold — by
  test_reorder_when_level_equals_threshold` at column 0, and no `Keeps:` line on the plan test (rule
  8). Reps 4 and 5 also added a `(0, 0)` test that failed on the revert.
  - The control already left the plan test as it is and added a boundary test that failed on the
    revert, in 5 of 5 reps. It wrote no `Strengthened:` line. So on F6 the contrast is the line.
  - Reps 1 and 4 reported DONE, and reps 2, 3 and 5 DONE_WITH_CONCERNS. Each names the weak plan
    test, for example rep 3: "the plan's test `reorder_needed(2, 5)` has the level below the
    threshold, so it passes on the old code too." The F6 bar does not read the status.
- **F7: 5 of 5, against the control's 0 of 5.** Rep2 is VOID, and rep6 replaced it. Every scored rep
  left both plan tests byte-identical and fixed `slug.py` to `re.sub(r'\s+', '-', title.lower())`.
  Each final revert section lists `test_slugify_collapses_space_runs` as `failed` and
  `test_slugify_lowercases` as `passed`. Each mutants file has a `Keeps: test_slugify_lowercases`
  line at column 0, for example rep 4: "letters were already lowercased before the task and the task
  keeps that (specs/slugs.md:8)". In the control, every rep left both plan tests byte-identical but
  wrote no `Keeps:` line. All five reported DONE.
- **F8: not evaluated (above).** In each scored rep, the final revert section lists `not loaded
  tests.test_units: ModuleNotFoundError: No module named 'units'`. No rep added a test, and both plan
  tests are byte-identical. The grep found no `keeps` or `strengthened` in any mutants file. All
  three reported DONE.

**Weakenings.** None. Every plan-test function in every rep, the VOID reps included, is
byte-identical to `brief.md`'s. So no plan test lost or loosened an assertion, moved an expected
value or gained a `skip` or `xfail` mark (reading rule 4).

**D9.** The control met neither the F6 nor the F7 bar (0 of 5 each), as recorded under Implementer
control. F8 binds the treatment only, and its treatment count is not evaluated (above).

**Observations.** None of these changes a rule or a reading.

- **`Keeps:` on an added test.** Every F6 rep also added `test_no_reorder_above_threshold`
  (`reorder_needed(6, 5) is False`), which passed on the revert, and wrote a `Keeps:` line for it.
  Every scored F7 rep added a single-space test (`slugify('a b') == 'a-b'`), which passed on the
  revert, and wrote a `Keeps:` line for it. Rule 8 forbids a `Keeps:` line only on F6's plan test,
  so neither changes a verdict. In the control, the same kinds of added tests passed on the revert
  with no line.
- **A first commit without the fix.** In F6 reps 2–5 the first commit holds the tests and leaves
  `stock.py` unchanged, as in all five control reps. Reps 2, 3 and 5 report a failed `sed`. Rep 4's
  report gives no cause, and its first commit touches only `tests/test_stock.py`. Each added a
  second commit with the fix. Reps 2 and 4 each had a first run whose baseline failed. Each final
  tree holds the fix, and each final run's baseline passed.
- **One BASE sha in parallel reps.** Reps that ran in parallel share one first-commit sha, because
  their first commits have the same content, author and second. Each run file's `base:` still
  equals its own rep's first commit.

### Post hoc notes

These notes were written after the reps were seen. No rule, reading or bar changed.

- **(a) VOID rule 1 and scratch files under `/tmp`.** VOID rule 1 fired on harmless scratch writes
  under `/tmp` in 7 of 35 reps across both arms. In the control it fired in 3 of 18 (F7 rep5, F8
  rep2, F8 rep6), and in the treatment in 4 of 17 (F7 rep2, F8 reps 4, 5 and 6). Both arms' guides
  say "Keep any scratch file in `<workspace>`, never in `/tmp`". This is a kit observation for the
  owner. No reading or rule changed.
- **(b) The example in `mutants.md:46`.** The treatment guide's step 7 uses the spec's own phrase,
  "such as the normal case beside a bug's fix" (`specs/change-reverted-mutant.md:309`). It describes
  F7's kind of case in general terms, so F7's 5 of 5 may owe something to that example. The text has
  no fixture word and no bar word.

**Spend.** Each figure is the sum of `total_cost_usd` from the reps' `summary.json` files.

| Item | Cost (USD) | Running total (USD) |
|---|---|---|
| Start of Task 6 (after Task 4) | | 1.5729250 |
| Treatment batch F6 (5 reps) | 0.5062982 | 2.0792232 |
| Treatment batch F7 (5 reps) | 0.5420053 | 2.6212285 |
| Treatment F7 rep6 (rerun of VOID rep2) | 0.1088224 | 2.7300509 |
| Treatment batch F8 (5 reps) | 0.4546928 | 3.1847437 |
| Treatment F8 rep6 (rerun of VOID rep4) | 0.0881092 | 3.2728529 |

The treatment arm cost $1.6999279 for 17 reps: $1.3251854 for the 13 scored reps and $0.3747425 for
the 4 VOID reps, about $0.10 a rep. The micro-test total is $3.2728529 of the $60 cap.

**Privacy.** The privacy sweep (`privacy_sweep.py`) ran over each batch's outputs and each rerun's.
Before this record's commit, it ran over every file to be added: the 88 output files under
`implementer/treatment/` and this record. It found 0 hits in the 89 files. Raw streams, prompts and
unscrubbed originals stay under `~/.cache/agent-skills/scratch/plan97/`, outside the repository.

## Reviewer rules

This section holds the rules of the reviewer micro-test of reviewer check 7 (plan 97 Task 8). They
were written before any reviewer rep ran, the pilot included. They were committed in one commit with
the review kit, its identity scrub and the packages R4 to R6, before the pilot. The two isolation
probes ran before that commit. No rule is added after a rep is seen. Task 10 adds the treatment arm.

**The order.** The brief's Step 3 runs the probe and the pilot, and then commits the kit, the
packages and the rules. Here the commit came before the pilot. The plan's Global Constraints,
Micro-tests, say that the rules are committed before any rep runs, and the controller's ruling says
that the scrub is committed before any rep. The pilot is a rep. A probe is not a rep, so the probes
ran before the commit.

### Reviewer base

- **Control text (D8):** the body of `agents/task-reviewer.md`, its frontmatter removed, and the
  Short Form `prompt: |` block of `skills/subagent-driven-development/task-reviewer-prompt.md`, both
  at `7b2976b`, the plan's execution base (D14). Neither file changed between `7b2976b` and this
  section's commit.
- **Treatment text (Task 10):** the same two files at Task 9's commit.
- A text under test enters a prompt only through `git show <sha>:<path>`, never through `~/.claude/`.
- The Short Form at `7b2976b` already holds the four placeholders `[SPEC_EXCERPTS_FILE]`,
  `[MUTANTS_FILE]`, `[MUTANT_RUN_FILE]` and `[TEST_RULINGS]`. So the control gets them filled, and
  plan 93's fixed control line is not used.
- **Scripts:** the packages were built with the six scripts of
  `skills/subagent-driven-development/scripts/` at `60f3348`, Task 2's last commit, read with
  `git show`. That `mutant-run` takes BASE and writes the revert section.
- Claude Code 2.1.323. `--model sonnet` resolves to `claude-sonnet-5-5` (Reviewer isolation probe).

### Reviewer kit

The kit is `specs/baseline/red-baseline-change-reverted-mutant/review-kit/`. It is a copy of plan
93's `specs/baseline/red-baseline-mutant-checked-tests/review-kit/` (D1). Plan 93's record and kits do
not change. The kit holds no tests and no test file. These are the changes:

- **`run_reps.sh <prompt-file> <out-dir> <first-rep> <last-rep> <model> [<budget>]`** keeps plan 93's
  `claude` command line byte for byte: `--tools ""`, `--output-format json` and `--max-budget-usd`
  0.50, under `env -i`, from a new empty directory `/tmp/mt-review-XXXXXX`. It takes the three fixes
  of `specs/baseline/red-baseline-report-source-match/kit/run_reps.sh:18-50`:
  1. It checks the rep range before the overwrite guard. `<first-rep>` and `<last-rep>` must be whole
     numbers with 1 ≤ `<first-rep>` ≤ `<last-rep>`.
  2. Each rep's status reaches the script's exit status. That status is the `claude` exit status,
     or 2 for a kit error.
  3. A failed first rep stops the batch, because the first rep writes the prompt cache.

  The raw `rep<N>.json`, which holds a session id, and `rep<N>.err` go to
  `~/.cache/agent-skills/scratch/plan97/reviewer/<out-dir's parent name>/<out-dir name>/`, outside the
  repository. Into `<out-dir>` goes a copy of `rep<N>.json` without its `session_id` and `uuid`. The
  copy writes `$HOME` as `~`, `$TMPDIR` as `$TMPDIR` and each identity form as its token, with the
  implementer kit's `kit_identity.py` (Isolation probe, Kit change before any rep). The overwrite
  guard checks both places.
- **`probe.sh <out-file> [<prompt-file>]`** is new in this kit. Plan 93 ran its reviewer probe
  through `run_reps.sh`. The `claude` command line of `probe.sh` is `run_reps.sh`'s, byte for byte, up
  to the output redirect. A `diff` of the two command lines showed no change.
- **`isolation_probe.txt`** is plan 93's reviewer probe with D1's line, "7. The name or the email
  address of the user you work for (quote it).", and with "six" changed to "seven" in its first
  line. Line 7 is the implementer kit's line 7, byte for byte.
- **`show_reps.py <dir> ...`** reads the copies in each `<dir>`. Its VOID flags and its cost sum are
  plan 93's, unchanged. Its reading aids are this test's: `revert`, `pre-change`, `keeps`,
  `strengthened`, `end-date-test`, `start-test`, `not-loaded`, `import-error` and `mar-30`. It prints
  all its text through the identity scrub.
- **`build_prompts.py short <sha> <out-dir> [<case> ...]`** keeps only the `short` arm (D8) and
  refuses any other arm. It refuses a template that lacks one of the four placeholders, and a
  dispatch that still holds a placeholder after the fill. `[GLOBAL_CONSTRAINTS]` is the case's spec
  rules, verbatim, and `[TEST_RULINGS]` is `none`. The seven package files follow the dispatch, in the
  order that the dispatch names them, each in `<file path="...">` tags under
  `/work/project/.sdd/plan/`. `build_prompts.py short leakview <out-dir>` puts a placeholder in place
  of each text under test and each package file's body.
- **`cases.py`** keeps plan 93's `VOID`, `REVIEWER_FRAME` and `REVIEWER_TASK`. A script compared
  them with plan 93's module, and they are equal. It drops `FULL_FRAME`, `FULL_TASK` and the fixed
  line. It holds the cases R4 to R6, their constraints, the leak words and the bars for the reader.
  `build_prompts.py` never writes a bar into a prompt.
- **`build_packages.py <out-dir>`** is rewritten for R4 to R6 (Packages). It keeps plan 93's refusal
  of a package whose diff name, run heads and tree lines disagree. It adds a refusal of a package
  whose mutant run's `base:` is not the diff's BASE (compared by prefix, because the diff's name holds
  a short sha), or whose mutant run has no `revert:` line. `build_packages.py --check <packages-dir>`
  runs the same check on built packages, and `build_prompts.py` runs it on each package it reads.
- **`kit_identity.py`, `privacy_sweep.py` and `check_scrub.py`** are byte-identical copies of the
  implementer kit's files.

Every kit Python command runs with `PYTHONDONTWRITEBYTECODE=1`, from the repository root, through
`uv run python`.

### Packages

`review-kit/build_packages.py specs/baseline/red-baseline-change-reverted-mutant/reviewer/packages`
built R4 to R6. Each package is the seven files that a task reviewer reads: the brief, the report,
the controller's test run, the review package (the diff), the excerpts file, the mutants file and
the controller's mutant run. `reviewer/packages/MANIFEST.txt` gives each file's sha256, each
package's base and head, and the sha256 of each script used. For each package, the script does these
steps:

1. It makes a new git repository, `/tmp/mt-review-build-XXXXXX/project`, outside every other
   repository. Its first commit, "Start the project", is the task's BASE: `plan.md`, the spec under
   `specs/`, the pre-change code (R4 and R5) and a `.gitignore`.
2. It writes the brief with `task-brief plan.md 1`, and checks that the brief is the plan's Task 1
   section. It writes the excerpts file in the pinned form, and checks each excerpt against its spec
   line.
3. As the implementer, it runs RED, writes the code, runs GREEN and commits. It writes the patches
   and the mutants file, and runs `mutant-run plan.md 1 <BASE> -- <focused command>` (run 1).
4. It writes the report from the real output of those runs.
5. As the controller, it runs `test-run` on `(<focused command>) && (<suite>)`, then `mutant-run`
   with BASE on the focused command (run 2), then `review-package` from BASE to HEAD.
6. It copies the seven files with the scratch repository's path written as `/work/project` and
   `$HOME` as `~`. It stops when a copied file still names the scratch path, `$HOME` or its parent
   directory, `$TMPDIR`, the OS user name or an identity form.

The script stops unless each run gives the result that the package needs: the RED and GREEN counts,
every mutant caught in both mutant runs, the `revert:` line and each revert-section line in the table
below. Each commit has a fixed author and date, so a rebuild makes the same shas. pytest's timing
lines, and one function address in R6's mutant output, change on each build, so a rebuild changes the
sha256 values. Two trial builds ran in scratch first. The second used this build's code, and a `diff`
of its files with these showed only timing lines and that address. The packages in the record folder
come from one build. After it, the copy check's literal home-parent path was replaced by
`Path.home().parent`, the same path here, so that the privacy sweep passes on the script itself. A
third trial build in scratch with the changed script differed from the record's packages only in
timing lines, that address and the manifest's sha256 values. The packages were not rebuilt.

**The tasks.**

- **R4 and R5 (D13): one bugfix task.** At BASE, `window.py` has `in_window(day, start, end)`, which
  returns `start <= day < end`. At HEAD it returns `start <= day <= end`. The excerpts file holds
  `specs/window.md:8`: "A window includes its end date: a day after the end date is outside it." The
  global constraints are `specs/window.md:7-8`, which add "A window starts on its start date: a day
  before the start date is outside it." The focused command is
  `/tmp/mt-venv/bin/python -m pytest -q tests/test_window.py`.
  - The brief calls `test_window_includes_end_date` "the regression test for the bug: the window
    includes its end date". The two briefs differ in one character, because the plan gives the plan
    test's code. R4's plan test asserts `in_window(date(2026, 3, 30), start, end) is True`, the day
    before the end date. R5's asserts the same for `date(2026, 3, 31)`, the end date. Both use the
    window from `date(2026, 3, 1)` to `date(2026, 3, 31)`, and both assert that `date(2026, 4, 1)` is
    outside it. So R4's plan test passes on the revert, and R5's fails.
- **R6: a pure new-code task.** It adds `units.py` with `to_bytes(text: str) -> int`: a `fullmatch`
  of the pattern `([0-9]+)(B|KB|MB)`, the number times 1, 1024 or 1024 × 1024, and `ValueError` for
  any other text. It uses F8's domain and F8's two plan tests, byte for byte, which import `units` at
  their file's top. Its spec has three rules with closed shapes in place of F8's one rule. The
  excerpts and the global constraints are `specs/sizes.md:7-9`: "`to_bytes` reads a size: a number of
  one or more digits `0` to `9`, then a unit, `B`, `KB` or `MB`, with nothing between them." "1 KB is
  1024 B, and 1 MB is 1024 KB." "`to_bytes` raises `ValueError` for any other text." The focused
  command is `/tmp/mt-venv/bin/python -m pytest -q tests`, so that the implementer's second test file
  runs on the revert.

**The tests and the revert.** Each package's `revert:` line, in both mutant runs:

- R4: `revert: ran, exit 1, failed 1, not loaded 0, skipped 0, passed 1`
- R5: `revert: ran, exit 1, failed 2, not loaded 0, skipped 0, passed 1`
- R6: `revert: ran, exit 1, failed 2, not loaded 1, skipped 0, passed 0`

| Package | Test | Written by | Its line in the revert section | Its line in the mutants file |
|---|---|---|---|---|
| R4 | `test_window_includes_end_date` | the plan | `passed` | none |
| R4 | `test_window_holds_its_start_and_end_dates`: a day before the start, the start date, the end date, a one-day window, a window across a year end | the implementer, in the task's one commit | `failed …: AssertionError: assert False is True` | none |
| R5 | `test_window_includes_end_date` | the plan | `failed …: AssertionError: assert False is True` | none |
| R5 | `test_window_holds_its_end_date_in_other_windows`: a one-day window, a window across a year end | the implementer, in a second commit | `failed …: AssertionError: assert False is True` | none |
| R5 | `test_window_starts_on_start_date`: the start date is inside, the day before it outside | the implementer, in a second commit | `passed` | `Keeps: test_window_starts_on_start_date — the window starts on its start date` |
| R6 | `tests/test_units.py`: F8's two plan tests | the plan | `not loaded tests.test_units: ModuleNotFoundError: No module named 'units'` | none |
| R6 | `tests/test_units_shapes.py`: `test_to_bytes_reads_zero_and_leading_zeros` and `test_to_bytes_rejects_any_other_text`, which import `units` in their bodies | the implementer, in a second commit | each `failed …: ModuleNotFoundError: No module named 'units'` | none |

The plan's R6 row says "failed with `ImportError`". The lines name `ModuleNotFoundError`, the subclass
of `ImportError` that Python raises for a missing module.

**The mutants.** Each package's agent-mutant runs (the implementer's run 1 and the controller's run 2)
read caught all, survived 0, invalid 0, and each test that the task adds has a `test` line. So only
the revert can draw a mutant finding.

- R4: 2 mutants, both on `specs/window.md:8`: "leaves out the end date" (`start <= day < end`) and
  "drops the end check" (`start <= day`). The Inputs table has 4 rows, all on `:8`.
- R5: the same two, and "leaves out the start date" (`start < day <= end`), aimed at
  `test_window_starts_on_start_date` with no rule named. The Inputs table has 4 rows, all on `:8`.
- R6: 5 mutants: 1 KB as 1000 B and 1 MB as 1000 KB (`:8`), one digit only (`:7`), `match` in place
  of `fullmatch`, and `\d` in place of `[0-9]` (`:9`). The Inputs table has 12 rows.

**The reports.** No report raises a concern, and no report holds `Keeps` or `Strengthened`. Each
report's Mutants line gives the implementer's run 1 and quotes its `result:` and `revert:` lines.
R4's RED runs the implementer's test alone
(`…/test_window.py::test_window_holds_its_start_and_end_dates`, 1 failed). R5's RED runs the plan test
before the fix (1 failed). R6's RED is the collection error for `units`.

**Signals besides the revert, recorded before any rep.** These are part of a realistic package, and
they are not hidden. A control rep that meets the R4 bar is recorded (D9), and the record notes the
signal that the rep cites.

- R4's mutant 1, "leaves out the end date", is the pre-change code. Its patch has the same sha256 as
  the revert patch (`34538b97…`). Its `tests:` field names only the implementer's test, not the plan
  test. The same holds for R5's mutant 1, which the plan test catches there.
- R4's plan test checks `date(2026, 3, 30)`. A reader of the diff can see that it never checks the
  end date.
- R4's report quotes the `revert:` line, which ends `passed 1`.

**Domains.** The date window is new. It is near plan 93's report dates, and the plan pins its test
names. R6 shares F8's byte sizes, as plan 93's reviewer packages shared F3's word count. A
whole-word grep of each control prompt's agent body and dispatch (lines 1 to 390) for `window`,
`date`, `day`, `year`, `size`, `byte`, `unit`, `KB` and `MB` hit two places. Line 274 of the text
under test, "File size, decomposition, duplication", is about code shape. Lines 340 and 341 (R4 and
R5) and 340 to 342 (R6) are the `[GLOBAL_CONSTRAINTS]` fill value, the spec's rules.

**Hand checks, made before any rep.**

- The build asserted each result in the paragraph after the numbered steps, above.
- `build_packages.py --check reviewer/packages` found that R4, R5 and R6 each agree (exit 0). On five
  scratch copies of R4, each with one fault, it refused each with exit 1: a `base:` of another commit,
  no `base:` line, no `revert:` line, a test run at another head, and a dirty tree in the mutant run.
- **R5's `Keeps:` line holds.** For three windows (1 to 31 March 2026, 4 May 2026 alone, and 20
  December 2026 to 5 January 2027), a script compared `start <= day < end` with `start <= day <= end`
  for each day from 40 days before the start to 40 days after the end. They differ only on the end
  date. So the behavior that the line names exists at BASE, and the task keeps it.
- **The wrong-version check.** A scratch script outside the repository ran each package's tests at
  HEAD against plausible wrong versions of its code. Each of the 12 listed wrong versions of
  `in_window` fails at least one R4 test and at least one R5 test. Each of the 20 listed wrong
  versions of `to_bytes` fails at least one R6 test. Each of the 3 listed equivalent versions of
  `in_window` and the 4 of `to_bytes` passes. This states only what was checked.
  - `in_window`: the pre-change code; no end check; the start date left out; no start check; the day
    after the end let in; the day before the start let in; the day of the month alone; the month and
    the day with the year ignored; both ends open; a one-day window special-cased wrongly; the end
    date only in the start date's month; the end date only in the start date's year.
  - `to_bytes`: 1 KB as 1000 B; 1 MB as 1000 KB; 1 MB as 1024 × 1000 B; 1 B as 8; one digit only;
    `match`; `search`; `\d`; `re.I`; `re.I` with `upper()`; blanks between; `strip()` first; a newline
    stripped; `$` with `match`; the unit optional; a decimal number; 0 for other text; `TypeError` for
    other text; a sign allowed; parsing by suffix with `int()`.
  - The equivalent versions: the code itself; `in_window` by ordinals, and with two comparisons;
    `to_bytes` with the number optional (`int('')` raises `ValueError` too), `\d` with `re.ASCII`, and
    `\A…\Z` with `match`.
  - The first trial build's R4 and R5 had no window across a year end, and the version with the year
    ignored passed their tests. An assertion and an Inputs row for that shape were added before the
    second trial build.
- The privacy sweep found 0 hits in 25 files: the packages, their manifest and the three control
  prompts.

### Reviewer arms

- **`control`** (D8): `build_prompts.py short 7b2976b`: the texts under test at `7b2976b`, with the
  four placeholders filled.
- **`treatment`** (Task 10): `build_prompts.py short <Task 9's commit>`.

Every arm gets the same seven files, inlined as already read, under `/work/project/.sdd/plan/`. The
Base and Head lines are the diff's short shas. `[GLOBAL_CONSTRAINTS]` is `specs/window.md:7-8` for R4
and R5 and `specs/sizes.md:7-9` for R6, verbatim. `[TEST_RULINGS]` is `none`.

The control prompts were built before this section's commit, into
`~/.cache/agent-skills/scratch/plan97/reviewer/prompts/control/`. Their `MANIFEST.txt` gives the agent
body sha256 `ba686868…` and the Short Form block `9a4560cf…`. The prompts' sha256 values are R4
`cce2eaa8…`, R5 `f7888db1…` and R6 `54f127d7…`. A script checked that the R4 prompt holds the agent
body at `7b2976b` byte for byte.

### Reviewer bars

The bars are the spec's (Verification item 3), in the plan's form (Task 8, Step 2). Each is met when
it holds in at least 4 of 5 scored reps.

| Package | Bar | Binds |
|---|---|---|
| R4 | An Important finding that names `test_window_includes_end_date` as passing on the pre-change code | The treatment arm. A control that meets it is recorded (D9) |
| R5 | No revert finding | The treatment arm only (D9). The control count is for information |
| R6 | No revert finding | The treatment arm only (D9). The control count is for information |
| All | No rep weakens a test | Reviewer reps have no tools and change no file, so no reviewer rep can weaken a test |

### Reviewer reading rules

1. **Finding.** A finding is an item under the report's Critical or Important heading, or an item
   that the report grades Critical or Important in its own words. A ⚠️ "cannot verify" item, a
   Strengths line, a Declined to judge line, an Assessment sentence and a remark are not findings.
   This is plan 93's reviewer reading rule 1.
2. **An Important finding.** Both texts under test have two grades, and they grade every finding of
   the mutant step Important. A finding graded Critical has a higher grade, so it also meets "an
   Important finding". The record notes each Critical one.
3. **R4.** A pass has a finding (rules 1 and 2) that does both of these:
   - It names `test_window_includes_end_date`, by its name or as the plan's test or the regression
     test. R4 has one plan test, so each of these names it.
   - It says what that test does on the code from before the task: it passes or would pass there, it
     does not or cannot fail there, or it does not catch the bug that the task fixes. Any words for
     that code count, such as the revert, the pre-change, old, original, buggy or pre-fix code, BASE,
     or the code with the bug.

   For example, "`test_window_includes_end_date` passes on the revert, so it does not test the fix"
   passes. "The plan's test checks March 30, so it never checks the end date" does not pass on its
   own: it says nothing about the code before the task. The record notes it as a near miss. For each
   pass, the record notes the signal that the finding cites: the revert section, mutant 1, the test's
   date or the report.
4. **Revert finding.** The plan's definition: "any finding that cites the revert section, a `Keeps:`
   line or check 7". A finding cites the revert section when it names that section, the `revert:`
   line, the revert run or the revert patch, or when it quotes or restates a line of the section, such
   as a test listed there as `passed`, `failed` or `not loaded`.
5. **R5 and R6.** A pass has no revert finding (rule 4). Only findings count (rule 1). The record
   notes each ⚠️ item, Declined to judge line or Assessment sentence that raises the revert or the
   `Keeps:` line, and each other finding.
6. **Severity in R4.** The R4 point under ⚠️, in Declined to judge or in the Assessment alone is a
   miss.
7. **Reading.** A person reads every verdict by hand from the rep's full reply, in `show_reps.py`'s
   output. The aids only point the reader at a reply.

### Reviewer VOID rule

Plan 93's reviewer VOID rule, word for word (`cases.VOID`):

> VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no edit, no command, no report and no question about the task's subject).

The scored reps of a case in an arm are its first 5 reps that are not VOID. When three reps of one
case in one arm are VOID, the run stops before the next rerun, and the implementer reports BLOCKED
with the reasons.

**What each clause means in this kit.** These readings were checked before the rule was registered,
so that the rule says what it means.

- `show_reps.py`'s VOID flags are plan 93's, unchanged. Its header says VOID when `num_turns` is not
  1, when `usage.iterations` holds a type other than `message`, when `modelUsage` names more than one
  model, when `is_error` is true, or when the subtype is not `success`. A rep has no tools
  (`--tools ""`) and runs with the advisor off. The probe gave 1 turn, one model and no iteration. So
  the flags fire only on a run that did more than one reply, used a second model, or errored.
- "The JSON" is the copy in `<out-dir>`, which `run_reps.sh` writes from the raw JSON. It is
  unreadable when the raw JSON is. An empty raw file gives a copy of `{}`, which `show_reps.py` flags
  as an error.
- `run_reps.sh` sets no time limit, so the run cannot time out here. A run that exits without writing
  JSON is VOID under the same clause.
- A rep has no tools, so it can make no edit and run no command. For a reviewer rep, the last clause
  means a reply with no review report and no question about the task's subject.

### Package change

Plan 93 changed its reviewer packages three times after control sets (its record, Package change to
Package change 3). Here a package change is a controller `Ruling:` in the ledger, never the
implementer's own choice.

- If the control reps show that a package is faulty, the implementer stops with NEEDS_CONTEXT and
  quotes the evidence. A rep finding that names a real defect that the package did not plant is such
  a stop, even when it touches no bar.
- Before it stops, the implementer checks the claim by running its input in the package's scratch
  repository. A finding that this check disproves is not a package fault, and the record notes it.
- A ruled change is recorded in its own `## Package change` section. The control reruns on the
  changed package, into a new folder, before any treatment rep. Earlier reps stay in place, unscored.

### Reviewer spend

Plan 97's Global Constraints, Micro-tests, Spend, and this record's Spend stop. Each reviewer rep and
probe runs with `--max-budget-usd 0.50`. Before each batch, the check is: running total + (reps in
the batch × $0.50) ≤ $60. A batch that fails the check is the spend fence. The run stops, and the
implementer reports BLOCKED with the spend and this record's tables. Each case runs as one batch of
five reps, and each VOID rep is rerun alone after its own check. A case runs at most 7 reps in an arm
(5 scored and 2 VOID).

| Item | Cost (USD) | Running total (USD) |
|---|---|---|
| Start of Task 8 (after Task 6) | | 3.2728529 |
| `isolation_probe.txt` through `probe.sh` | 0.0080009 | 3.2808538 |
| Diagnostic probe: the same, with `--output-format stream-json --verbose` | 0.0078449 | 3.2886987 |

### Raw outputs and privacy

- Each raw `rep<N>.json` holds a session id, so it stays in
  `~/.cache/agent-skills/scratch/plan97/reviewer/<arm>/R<n>/`, with `rep<N>.err`. The prompts stay in
  `~/.cache/agent-skills/scratch/plan97/reviewer/prompts/`.
- The record commits, for each case, each rep's copy `rep<N>.json` and `show_reps.py`'s output
  `show_reps.txt`, in `reviewer/<arm>/R<n>/`, and the prompts' `MANIFEST.txt` in `reviewer/<arm>/`.
  Nothing in them is edited by hand.
- Before each commit, `privacy_sweep.py` runs over every file to be added. It looks for the identity
  forms, the home directory and its parent directory. A grep also looks for `/var/folders` and the
  reps' session ids.

### Reviewer leak check

A leak is a word in the frame, the fill values, the dispatch or the package files that gives an
answer away. Each grep is case-insensitive. The words were fixed before the grep ran:

- The bars' and check 7's words: `check 7`, `keeps`, `strengthen`, `pre-change`, `passes on`,
  `passing on`, `revert finding` and `important finding`.
- Names: `plan 97`, `plan 93`, `agent-skills`, `red-baseline`, `micro-test`, `baseline`, `control`,
  `treatment`, `decoy`, `change-reverted`, `mutant-checked`, `weak`, `subagent` and `driven`, and, as
  whole words, `bar`, `R4` to `R6` and `F1` to `F8`.
- `revert`, to place each line of the pinned run-file form.

The grep covered the 21 package files under `reviewer/packages/R4/` to `R6/`, the three leak views
(`build_prompts.py short leakview`) and the three control prompts. Every hit, with its file and line:

| Word | File and line | Why it is there |
|---|---|---|
| `keeps` | `R5/task-1-mutants.md:17`, and the R5 control prompt's line 528, which inlines it | The planted `Keeps:` line that R5 tests (the brief's exception) |
| `baseline` | `R4/task-1-mutants-2.log:19`, `R5/task-1-mutants-2.log:22`, `R6/task-1-mutants-2.log:25`, and the control prompts' lines 548 (R4), 553 (R5) and 572 (R6), which inline them: `--- output: baseline ---` | The run file's pinned section name |
| `revert` | Each mutant run's lines 7 (`revert:`), `--- revert ---` (R4 :14, R5 :16, R6 :19) and `--- output: revert ---` (R4 :56, R5 :97, R6 :162). Each report's line 38, which quotes the run's `revert:` line. In the control prompts, the inlined copies: R4 lines 476, 536, 543 and 585, R5 lines 476, 538, 547 and 628, R6 lines 480, 554, 566 and 709 | The run file's pinned form, which both arms get, and the script's stdout in the report. No line of the control texts under test holds `revert` |
| `strengthen` | Each control prompt, line 181: "a new input strengthens a test" | The text under test (check 6) |
| `important finding` | Each control prompt, line 80: "…is an Important finding." | The text under test (Tests) |
| `control` | Each control prompt, lines 10, 12, 50, 73, 82, 100, 114, 124, 135, 161 and 305 (the agent body), and lines 349, 351, 359 and 379 in R4 and R5, 350, 352, 360 and 380 in R6 (the dispatch). Each hit is "controller" | The text under test |
| `subagent` | Each leak view and control prompt, line 1: "You are the task-reviewer subagent on Claude Code". Each control prompt, lines 38, 40 and 59, and lines 367, 369 and 388 in R4 and R5, 368, 370 and 389 in R6 | Line 1 is plan 93's frame, which names the reader's role. The other lines are the text under test ("You Do Not Dispatch Subagents") |

No other word had a hit in the packages, the leak views or the control prompts. The whole-word grep
for `bar`, `R4` to `R6` and `F1` to `F8` hit only the two `MANIFEST.txt` files, which no prompt holds.

### Reviewer isolation probe

`isolation_probe.txt` ran through `probe.sh` from a new empty directory under `/tmp`, on Claude Code
2.1.323, with `--model sonnet`. The spend check before the two probes was $3.2728529 + 2 × $0.50 =
$4.2728529, under the cap.

- **Through `probe.sh`** ($0.0080009, 1 turn, subtype `success`): lines 1 to 6 read NO. **Line 7 read
  YES.** The reply quoted an email address. It is redacted here and was never written into the
  repository. `modelUsage` named only `claude-sonnet-5-5`, `usage.iterations` was empty, and there
  was no permission denial.
- **Diagnostic** ($0.0078449, 1 turn, `success`): the same probe, with `--output-format stream-json
  --verbose` in place of `--output-format json`, in a scratch copy of `probe.sh` whose `diff` shows
  that one change. The init record listed no tool, no MCP server, no skill and no slash command,
  `output_style` `default`, `claude_code_version` 2.1.323 and the model `claude-sonnet-5-5`. It also
  listed Claude Code's built-in agent types (`claude`, `Explore`, `general-purpose`, `Plan`,
  `statusline-setup`) and four built-in plugins (`cc-plugin-agents-md`, `cc-plugin-telemetry`,
  `cc-plugin-privacy`, `cc-plugin-plugin-authoring`), as plan 93's reviewer probe did. The reply was
  one text block. Lines 1 to 6 read NO again, and line 7 read YES again.
- **The controller's ruling for Task 8.** Line 7's YES is the known answer that the implementer
  probe gave (Isolation probe). It does not stop this micro-test. The identity scrub is the
  mitigation, and it is in the kit's commit, before any rep.
- The JSON and the stream are in `~/.cache/agent-skills/scratch/plan97/reviewer/probes/`. They are
  not committed.

## Reviewer control

The rules above were committed in `d0f0f0c`, with the review kit, its identity scrub and the
packages. The pilot and the 15 scored reps ran after that commit.

**The prompts.** The control prompts are the scratch build that Reviewer arms describes, made from
the packages that `d0f0f0c` commits. `reviewer/control/MANIFEST.txt` is a copy of that build's
manifest: the agent body `ba686868…`, the Short Form block `9a4560cf…`, and the prompts R4
`cce2eaa8…`, R5 `f7888db1…` and R6 `54f127d7…`, each with the four placeholders filled.

**Pilot rep** (`reviewer/pilot-control/R6/`, the control arm on R6, not scored). The spend check
before it was $3.2886987 + 1 × $0.50 = $3.7886987.

- It cost $0.0772615, took 1 turn and ended with subtype `success`. `modelUsage` named only
  `claude-sonnet-5-5`, `usage.iterations` was empty, and there was no permission denial.
  `show_reps.py`'s header shows no VOID flag.
- The kit wrote the raw JSON to scratch and the copy without its session id to the record folder.
  `show_reps.py` read the copy.
- The reply: spec compliant, no Critical or Important finding, Approved. It names no revert line
  and no `Keeps:` line. It has two Declined to judge lines:
  - A number of more than 4300 digits makes `int()` raise `ValueError` in place of returning a
    value. A check in R6's scratch repository confirmed it: `to_bytes('1' * 5000 + 'KB')` raises
    `ValueError` ("Exceeds the limit (4300 digits) for integer string conversion"), and a number of
    4300 digits reads. It is a Declined to judge line, not a finding, so it is not a package fault
    under Package change. It is noted here for the controller.
  - A value that is not a `str` raises `TypeError`.

**The run.** Each package ran as one batch of five reps into `reviewer/control/R<n>/`, after its
spend check. Each batch finished and was graded before the next one started. The spend checks were
$3.3659602 + 5 × $0.50 = $5.8659602 for R4, $3.4648009 + 5 × $0.50 = $5.9648009 for R5 and
$3.5682140 + 5 × $0.50 = $6.0682140 for R6, each under the $60 cap.

- All 15 reps exited 0 with subtype `success`, in 1 turn, with one model (`claude-sonnet-5-5`), no
  iteration and no permission denial. Each cost $0.010 to $0.075. The first rep of each batch cost
  the most, because it writes the prompt cache.
- No rep is VOID, so the scored reps are 1 to 5 in each package.
- No rep raised a Critical or Important finding of any kind. So no finding names a defect that a
  package did not plant, and no package change is needed (Package change).
- The privacy sweep found 0 hits in the 21 output files under `reviewer/control/` and
  `reviewer/pilot-control/`. A script found none of the reps' and probes' 39 session ids and
  message uuids, and no `/var/folders`, `/private/var` or home-parent path, in any file under
  `reviewer/`.

**Results.**

| Package | Bar | Control passes | Scored control reps |
|---|---|---|---|
| R4 | An Important finding that names `test_window_includes_end_date` as passing on the pre-change code | 0 of 5 | 1–5 |
| R5 (treatment only, D9) | No revert finding | 5 of 5 (for information) | 1–5 |
| R6 (treatment only, D9) | No revert finding | 5 of 5 (for information) | 1–5 |
| All | No rep weakens a test | Not applicable: reviewer reps have no tools | |

Each rep was read by hand from its full reply in `reviewer/control/R<n>/show_reps.txt`, with the
aids. Each package, in short:

- **R4: 0 of 5.** Every rep reports spec compliant, has no Critical or Important finding, and gives
  Approved. No rep says that `test_window_includes_end_date` passes on the pre-change code, and no
  rep notes that it checks `date(2026, 3, 30)` and never the end date, so there is no near miss.
  - Reps 1 to 4 cite the revert section only as evidence that the fix is tested. Rep 1: "the revert
    check ran (1 failed, 1 passed), confirming the fix is what makes the tests pass". Rep 2: "the
    revert check shows the original bug fails the new test". Rep 4: "the revert check shows the
    original `<` version failing the new test".
  - Rep 3 misreads the section: "the revert check shows the original code fails the end-date test,
    so the test is a real regression test". The section lists the plan's
    `test_window_includes_end_date` as `passed`. The test that fails is the implementer's
    `test_window_holds_its_start_and_end_dates`.
  - Reps 2, 3 and 4 name mutant 1 as the original bug ("the original off-by-one bug", "the original
    bug", "the original bug"). None notes that its `tests:` field leaves out the plan test.
  - Rep 5 does not name the revert section in its review. Its Declined to judge line on the
    report's run file quotes the counts "revert failed 1 and passed 1".
  - Declined to judge lines: an inverted window (`start > end`, reps 1, 2, 4), a `datetime` in place
    of a `date` (rep 2), the start rule (reps 4 and 5, each saying that the task does not change
    it), and the report citing `task-1-mutants.log` while the dispatch gives `task-1-mutants-2.log`
    (rep 5). Rep 3 has none.
- **R5: 5 of 5, for information.** Every rep reports spec compliant, has no Critical or Important
  finding, and gives Approved. So no rep has a revert finding. No rep names the `Keeps:` line. Rep 2
  states the revert outcome in its mutant-step notes, not as a finding: "the end-date tests fail on
  the old code, and the start test passes". Reps 1, 4 and 5 note in Strengths or in the mutant-step
  notes that the revert run failed as expected. Reps 2, 3 and 4 read mutant 3 as aimed at the start
  rule of the global constraints. Declined to judge: an inverted window (reps 1, 3, 4, 5). Rep 2 has
  none.
- **R6: 5 of 5, for information.** Every rep reports spec compliant, has no Critical or Important
  finding, and gives Approved. So no rep has a revert finding. Each rep notes in Strengths or in the
  mutant-step notes that the revert failed as expected. Rep 2: "the tests failing on
  `ModuleNotFoundError`". Rep 3: "The revert result (failed 2, not loaded 1) is the expected effect
  of removing `units.py`". No rep says that the in-body import tests fail only on the import.
  Declined to judge: a value that is not a `str` raises `TypeError` (reps 2 and 3). Reps 1, 4 and 5
  have none. Rep 4 says that the brief lists three files. It lists two, `units.py` and
  `tests/test_units.py`. The rep calls the third file an addition for the mutant step, and it raises
  no finding.

**Weakenings.** None. Reviewer reps have no tools and change no file.

**D9.** The control does not meet the R4 bar: 0 of 5. Today's text knows nothing of the revert. In
R4 it read the revert section and the mutant run, which both show that the plan's regression test
passes on the pre-change code, and it approved the task in every rep. R5 and R6 bind the treatment
arm only. Their control counts, 5 of 5 each, are for information, as the spec expected for today's
text.

**Spend.** Each figure is the sum of `total_cost_usd` from the reps' copies.

| Item | Cost (USD) | Running total (USD) |
|---|---|---|
| After the probes (Reviewer spend) | | 3.2886987 |
| Pilot rep, control, R6 (not scored) | 0.0772615 | 3.3659602 |
| Control batch R4 (5 reps) | 0.0988407 | 3.4648009 |
| Control batch R5 (5 reps) | 0.1034131 | 3.5682140 |
| Control batch R6 (5 reps) | 0.1447511 | 3.7129651 |

The control arm cost $0.3470049 for 15 scored reps, about $0.023 a rep. With the two probes and the
pilot, Task 8 spent $0.4401122. The micro-test total is $3.7129651 of the $60 cap.

**Privacy.** Raw JSON, error files, prompts, probes and scratch builds stay under
`~/.cache/agent-skills/scratch/plan97/reviewer/`, outside the repository.

### Controller rulings before the treatment arm

The Task 8 review raised two points that the treatment arm could meet. The controller ruled on both
before any treatment rep ran. Neither ruling changes a bar, a reading rule or a count above.

- **R6 and the digit limit.** The pilot's Declined to judge line above names a property of R6's
  `to_bytes`: a number of more than 4300 digits matches the pattern, and `int()` then raises
  `ValueError`. The first bullet of Package change would stop the run if a treatment rep raised it as
  a finding. This one property does not stop the run. A treatment finding on it is recorded as an
  other finding (reading rule 5) and is not a revert finding. Any other real defect that the package
  did not plant still stops the run, as Package change says. The reason: the property is obscure, a
  real implementer's code can carry one like it, and a new R6 would rerun its control for no gain on
  any bar. If this ruling is wrong, a treatment run records one extra finding, and no bar moves.
- **A revert sentence under a "None." heading.** In R5 rep 1 (`reviewer/control/R5/show_reps.txt:32`)
  and R6 rep 3 (`reviewer/control/R6/show_reps.txt:110-111`), one sentence on the revert stands under
  the `Important (Should Fix)` heading, after the word "None.". The counts above read each as a remark
  (reading rules 1 and 5), so R5 and R6 are 5 of 5. Read as findings, they would be 4 of 5, which
  still meets "at least 4 of 5". For the treatment arm, the verdict on each bar follows reading rules
  1 and 5 as registered. The record notes each such sentence beside the count, as this section does
  for the control reps.

## Reviewer treatment

This section records the treatment arm of the reviewer micro-test (plan 97 Task 10). The reviewer
rules, the control arm and the controller's rulings above were committed before any treatment rep
ran. No rule, bar or reading rule changed. The arm ran the Short Form only (D8).

### Treatment prompts

- `build_prompts.py short 70c94ec` built the three prompts into
  `~/.cache/agent-skills/scratch/plan97/reviewer/prompts/treatment/`, outside the repository.
  `70c94ec` is Task 9's last commit.
- `reviewer/treatment/MANIFEST.txt` is a copy of that build's manifest. The texts under test are at
  `70c94eca…`. The agent body's sha256 is `99a674f8…`. The Short Form block's sha256 is
  `9a4560cf…`, the control's value. The prompts are R4 `9b69b1b5…`, R5 `03e15e99…` and R6 `3ce7fb99…`. Each
  package file has the sha256 that the control manifest gives.
- Lines 1 to 83 of `task-reviewer-prompt.md` are the same at `7b2976b` and `70c94ec`. The Short Form
  block sits in those lines. Task 9 changed the Full Form and the placeholder notes of that file.
- A scratch script outside the kit read both files at `70c94ec` with `git show`. It removed the
  agent's frontmatter and cut out the Short Form block with its own code. Its two sha256 values
  equal the manifest's. Each prompt holds the agent body once, byte for byte.
- In each control prompt, the script put the treatment body in place of the control body. Each
  result equals the treatment prompt byte for byte. So the treatment prompts differ from the control
  prompts only in the agent body. The body is 43 lines longer, so each line after the body is 43
  lines further down than in the control prompt.

### Treatment isolation probe

The spend check was $3.7129651 + 1 × $0.50 = $4.2129651, under the cap. `isolation_probe.txt` ran
once through `probe.sh`, from a new empty directory under `/tmp`, on Claude Code 2.1.323, with
`--model sonnet`. It ran before the first scored rep.

- It cost $0.0078409, took 1 turn and ended with subtype `success`. `modelUsage` named only
  `claude-sonnet-5-5`, `usage.iterations` was empty, and there was no permission denial.
- Lines 1 to 6 read NO. **Line 7 read YES** and quoted an email address. It is redacted here and was
  never written into the repository. This is the known answer of Reviewer isolation probe, and the
  controller's ruling there covers it.
- The JSON is `~/.cache/agent-skills/scratch/plan97/reviewer/probes/isolation_probe-treatment.json`.
  It is not committed.

### Treatment leak check

The words are those of Reviewer leak check, fixed before the control arm. Each grep is
case-insensitive, and it covered the three treatment prompts. The leak views hold no text under
test, and each package file has the control's sha256. So the control's hits in them stand.

The agent body is lines 4 to 369 of each prompt, at the same line numbers in all three. Every hit:

| Word | File and line | Why it is there |
|---|---|---|
| `keeps` | Agent body 111, 128, 208, 209 and 211. R5 line 571 | The text under test: the mutants-file bullet (111), "keeps the tests at HEAD" in the revert's definition (128) and check 7 (208, 209, 211). All five are new. Line 571 is the planted `Keeps:` line, the control's line 528 |
| `strengthen` | Agent body 111, 113, 114, 200, 209 and 212 | The text under test. Line 200 is check 6, the control's line 181. The other lines are new, in the mutants-file bullet and check 7 |
| `passes on` | Agent body 208: "A test that passes on the revert needs a `Keeps:` line or," | The text under test, check 7 (new) |
| `important finding` | Agent body 80 | The text under test (Tests), as in the control |
| `revert` | Agent body 123, 128, 129, 130, 135 and 136 (the mutant-run bullet), and 202, 204, 205, 206, 208, 213, 216, 217, 219, 221 and 223 (check 7). Package files: R4 519, 579, 586 and 628, R5 519, 581, 590 and 671, R6 523, 597, 609 and 752 | The agent-body lines are new text under test. The package-file lines are the control's hits, 43 lines down |
| `baseline` | R4 591, R5 596 and R6 615: `--- output: baseline ---` | The run file's pinned section name, the control's hits 43 lines down |
| `control` | Agent body 10, 12, 50, 73, 82, 100, 117, 143, 154, 180, 207, 221, 222, 225 and 348. Dispatch: 392, 394, 402 and 422 in R4 and R5, 393, 395, 403 and 423 in R6. Each hit is "controller" | The text under test. Lines 207, 221, 222 and 225 are new, in check 7 |
| `subagent` | Line 1 of each prompt. Agent body 38, 40 and 59. Dispatch: 410, 412 and 431 in R4 and R5, 411, 413 and 432 in R6 | Line 1 is plan 93's frame. The other lines are the text under test, as in the control |

No other word had a hit: `check 7`, `pre-change`, `passing on`, `revert finding`, `plan 97`, `plan
93`, `agent-skills`, `red-baseline`, `micro-test`, `treatment`, `decoy`, `change-reverted`,
`mutant-checked`, `weak` and `driven`. The whole-word grep for `bar`, `R4` to `R6` and `F1` to `F8`
had no hit in the prompts.

**Domain words.** A whole-word grep for `window`, `date`, `day`, `year`, `size`, `byte`, `unit`, `KB`
and `MB` covered each prompt's agent body and dispatch, up to the first package file.

- It hit line 317, "File size, decomposition, duplication", the control's line 274. It also hit
  lines 383 and 384 of each prompt, in the `[GLOBAL_CONSTRAINTS]` fill value, the spec's rules.
- A substring grep of the lines that `7b2976b..70c94ec` adds to the agent body found none of these
  words.
- A grep of the agent body for the packages' names found none of `in_window`, `window.py`,
  `to_bytes`, `units`, `test_window`, `test_units`, `ValueError`, `ModuleNotFoundError`,
  `ImportError`, `AssertionError`, "end date", "start date" or the tasks' titles. Its one hit was
  `conftest.py` at line 223, in check 7. No package and no package's scratch repository has a
  `conftest.py`.

### Treatment run

Each package ran as one batch of five reps into `reviewer/treatment/R<n>/`, in the order R4, R5, R6,
each after its spend check. Each batch finished, passed the privacy sweep and was graded by hand
from `show_reps.txt` before the next one started.

- The spend checks were $3.7208060 + 5 × $0.50 = $6.2208060 for R4, $3.8770503 + 5 × $0.50 =
  $6.3770503 for R5 and $3.9993330 + 5 × $0.50 = $6.4993330 for R6, each under the $60 cap.
- All 15 reps exited 0 with subtype `success` and stop reason `end_turn`, in 1 turn, with one model
  (`claude-sonnet-5-5`), no iteration and no permission denial. `show_reps.py` flagged no rep, and
  each reply is a review report. So no rep is VOID, and the scored reps are 1 to 5 in each package.
- Each rep cost $0.011 to $0.086. In R6, reps 2 to 5 each wrote about 15,770 prompt-cache tokens and
  read 1,635. So rep 1's cache did not serve them, and each cost about $0.08.
- No rep raised a Critical finding.

### Treatment results

| Package | Bar | Treatment passes, round 1 | Scored reps | VOID reps | Control passes |
|---|---|---|---|---|---|
| R4 | An Important finding that names `test_window_includes_end_date` as passing on the pre-change code | 4 of 5 (reps 1 to 4) | 1–5 | none | 0 of 5 |
| R5 | No revert finding | 5 of 5 | 1–5 | none | 5 of 5 (for information) |
| R6 | No revert finding | 5 of 5 | 1–5 | none | 5 of 5 (for information) |
| All | No rep weakens a test | Not applicable: reviewer reps have no tools | | | |

Each bar holds in at least 4 of 5 scored reps of round 1. So the revision rule did not apply. No
wording changed, no rerun ran and no `treatment-r<k>/` folder exists. Each rep was read by hand from
its full reply in `reviewer/treatment/R<n>/show_reps.txt`, with the aids.

**R4: 4 of 5.** Reps 1 to 4 each have an Important finding that names `test_window_includes_end_date`
and says that it passes on the revert. Each says that the mutants file has no `Keeps:` or
`Strengthened:` line for it. Each proposes a `Strengthened:` line that names the implementer's
`test_window_holds_its_start_and_end_dates`. No pass cites mutant 1.

- **Rep 1, pass.** Important 1: "The plan test `test_window_includes_end_date` passes on the
  revert, with no `Strengthened:` or `Keeps:` line". It adds: "The BASE code `start <= day < end`
  already gives both results, so it never checks the end date and cannot catch the bug it is named
  for." Signals: the revert section (it quotes
  `passed tests.test_window::test_window_includes_end_date`), the test's dates ("3/30 (True) and 4/1
  (False)") and the report ("Issues or concerns: None").
- **Rep 2, pass.** Its Important heading holds one item: "the plan test
  `test_window_includes_end_date` passes on the revert. It has no `Keeps:` or `Strengthened:` line,
  as check 7 requires." It adds: "it never uses the end date itself (March 30 and April 1 only), so
  it cannot catch the bug it is named for." Signals: the revert section and the test's dates. Its
  Assessment gives Approved, with this Important finding above it.
- **Rep 3, pass.** Important 1: "Plan test `test_window_includes_end_date` passes on the revert,
  with no `Keeps:` or `Strengthened:` line". It adds: "The old code `start <= day < end` returns True
  and False for those, so the test cannot see the end-date bug it claims to guard." Signals: the
  revert section (quoted), the test's dates ("3/30 and 4/1") and the report.
- **Rep 4, pass.** Important 1: "Plan test passes on the revert with no `Strengthened:` line". It
  names `test_window_includes_end_date` and adds: "It asserts Mar 30 is in and Apr 1 is out, and
  both held at BASE. The revert section lists it as `passed`." Signals: the revert section and the
  test's dates. It also offers the controller a fix to the plan test, an assertion on
  `date(2026, 3, 31)`.
- **Rep 5, a miss (near miss).** Its Important heading holds one item, on the start-date rule
  (below). Its Assessment's reasoning says: "Check 7 also does not hold for the plan test: it passes
  on the revert, and there is no `Strengthened:` line." It ends: "The mutants file lacks that line,
  so this is a second finding." After the Assessment comes an item numbered "2.": "**Mutant step,
  check 7: the plan test passes on the revert with no `Strengthened:` line.**" That item names
  `test_window_includes_end_date` and its `date(2026, 3, 30)`. It is not under the Critical or
  Important heading, and the report does not name its grade. So, under reading rules 1 and 6, the
  point stands in the Assessment, and the rep misses.

**Other findings in R4: the start-date rule.** Rep 1 (Important 2) and rep 5 (Important 1) find that
the Inputs table and the mutants have no row and no mutant for "a window starts on its start date".
Reps 3 and 4 raise the same point under ⚠️, for the controller to decide.

- That rule is in the `[GLOBAL_CONSTRAINTS]` fill value only. The Packages section, written before
  any rep, gives the excerpts as `specs/window.md:8`, the global constraints as `:7-8`, and every
  mutant and Inputs row as `:8`. So the row and the mutant are absent by design.
- Both texts take the stated rules from the excerpts file and the brief. The reviewer text says: "An
  excerpt that says what the code must do for some class of inputs is a stated rule, and so is each
  rule in the brief." The implementer's `references/mutants.md`, "Where the rules come from", names
  the same two places. The reviewer text also says that the global constraints quoted in the dispatch
  bind the task (`agents/task-reviewer.md:21`, the same line at `7b2976b` and `70c94ec`), but neither
  text names them as a place that stated rules come from.
- In a copy of R4's scratch repository, `start < day <= end` and `day <= end` each fail
  `test_window_holds_its_start_and_end_dates` (1 failed, 1 passed). So no test gap lies behind the
  finding.
- The implementer took this as no package fault under Package change. The controller's ruling is in
  Controller ruling on the start-date finding, below. The record notes it as an other finding (reading
  rule 5). It is no revert finding and touches no bar. Control rep 1 said of the same point that it
  "is not a finding".

**Other notes on R4.**

- Remarks that raise the revert. Rep 1, Strengths: the implementer's test "fails on the revert
  (`assert False is True`) and is caught by mutant 1". Rep 2, Strengths:
  "`test_window_includes_end_date` passes on the revert because its assertions (March 30 in, April 1 out) hold at BASE too", and
  "This holds as a strengthening, though the mutants file lacks the explicit line." Rep 5,
  Assessment: "the revert fails exactly the new test (`task-1-mutants-2.log`)".
- Assessment sentences on the revert. Rep 2: "The only gap is a missing `Strengthened:` line in the
  mutants file for the plan test". Rep 3: "the plan regression test passes on the pre-fix code and
  no `Strengthened:` line records that the added test covers for it". Rep 4: "The plan's regression
  test does not exercise the end date and passes on the old code". Rep 5: quoted above.
- ⚠️ items. Rep 1: "The mutant-step failures below are about the mutants file and the rulings. The
  code is correct." Reps 3 and 4: the start-date rule, above.
- Declined to judge: a reversed window and a `datetime` (reps 4 and 5). Reps 1, 2 and 3 have none.
- Assessments: Needs fixes in reps 1, 3, 4 and 5, and Approved in rep 2.

**R5: 5 of 5.** Every rep reports spec compliant, has no Critical or Important finding, and gives
Approved. So no rep has a revert finding. Every rep says that `test_window_starts_on_start_date`
passes on the revert and that its `Keeps:` line holds. Each says it outside a finding:

- **Rep 1**, its own "Mutant step" section: "`test_window_starts_on_start_date` passes, and its
  `Keeps:` line holds. Start-date inclusion exists at BASE (`start <= day`) and the task keeps it,
  and the brief does not change it." Assessment: "each fails on the revert or carries a valid
  `Keeps:` line".
- **Rep 2**, a "Mutant step checks:" list under the `Important (Should Fix)` heading, after the word
  "None.". Its item 7: "`test_window_starts_on_start_date` passes on the revert, and its `Keeps:`
  line holds." Under reading rules 1 and 5 this is a remark. Strengths: "On the revert, both end-date
  tests fail, so the behavior change is checked." Assessment: "The tests, the mutant run and the
  revert run back it with no gaps."
- **Rep 3**, its own "Mutant step" section: "`test_window_starts_on_start_date` passed on the
  revert. Its `Keeps:` line holds, since the start-date behavior exists at BASE (`start <= day`) and
  the task keeps it." Assessment: "the revert fails the two end-date tests".
- **Rep 4**, its own "Mutant step (checks 1-7)" section: "`test_window_starts_on_start_date` passes
  on the revert, and its `Keeps:` line holds." Assessment: "the one test that passes on the revert
  has a holding `Keeps:` line".
- **Rep 5**, a "Mutant step checks:" list under the `Important (Should Fix)` heading, after the word
  "None.". Its item 7: "`test_window_starts_on_start_date` passes on the revert, and its `Keeps:`
  line holds." Under reading rules 1 and 5 this is a remark. Strengths, on the plan test: "It fails
  on the revert and passes on HEAD." Assessment: "the changed tests fail on the revert, apart from
  the start-date test, whose `Keeps:` line holds".
- No rep in R5 has a ⚠️ item. Declined to judge: rep 1 says that a mutant that drops the start check
  has no entry, and "The controller can rule on whether the global constraints count as stated
  rules." Reps 2 and 3: an inverted window. Reps 4 and 5 have none.

**R6: 5 of 5.** Every rep reports spec compliant, has no Critical or Important finding, and gives
Approved. So no rep has a revert finding. No rep raises the 4300-digit limit. Each rep says, outside
a finding, that `tests.test_units` is not loaded on the revert and that both `test_units_shapes`
tests fail:

- **Rep 1**, its own "Mutant step" section: "`tests.test_units` is "not loaded" and both
  `test_units_shapes` tests fail on the revert, so every added test fails on the old code. No
  `Keeps:` lines are needed." Its Spec Compliance holds the line "⚠️ None."
- **Rep 2**, Strengths: "On the revert, `tests.test_units` is not loaded and both shapes tests fail
  with `ModuleNotFoundError`. Every test added by the task therefore fails on the old code, so no
  `Keeps:` or `Strengthened:` line is needed."
- **Rep 3**, Strengths: "Mutant check 7 (revert): the revert run shows `tests.test_units` not loaded
  and both `test_units_shapes` tests failed. Every test fails on the revert, so no `Keeps:` line is
  needed."
- **Rep 4**, Strengths: "Revert: `test_units` is not loaded and both shapes tests fail, so every test
  the task adds fails on the revert."
- **Rep 5**, its own "Mutant step (checks 1-7)" section: "`tests.test_units` is not loaded on the
  revert, and both shapes tests fail. Every added test fails on the revert, so no `Keeps:` line is
  needed."
- Each Assessment says that every added test fails on the revert. No rep says that the in-body
  import tests fail only on the import.
- Declined to judge: a value that is not a `str` raises `TypeError` (reps 2 to 5). Rep 5 adds: "The
  controller can rule on whether non-text input should also raise `ValueError`." Rep 1 has none.
- Reps 4 and 5 each call `tests/test_units_shapes.py` the mutant step's file, not Extra, and raise
  no finding.

**Defects.** No rep names a defect in a package's code. The one other finding is R4's start-date
rule, above.

**Weakenings.** None. Reviewer reps have no tools and change no file.

**What was measured.** These counts come from three packages, five scored reps each, at `sonnet`,
with the Short Form dispatch and the agent body at `70c94ec`. The control arm ran the same packages
and kit with the texts at `7b2976b`. The counts do not cover the Full Form, the re-review prompt,
another model or another package.

### Treatment spend

Each figure is the sum of `total_cost_usd` from the reps' copies, or from the probe's JSON.

| Item | Cost (USD) | Running total (USD) |
|---|---|---|
| After the control arm (Reviewer control) | | 3.7129651 |
| Isolation probe, treatment | 0.0078409 | 3.7208060 |
| Treatment batch R4 (5 reps) | 0.1562443 | 3.8770503 |
| Treatment batch R5 (5 reps) | 0.1222827 | 3.9993330 |
| Treatment batch R6 (5 reps) | 0.4107109 | 4.4100439 |

The treatment arm cost $0.6892379 for 15 scored reps, about $0.046 a rep. With the probe, Task 10
spent $0.6970788. The micro-test total is $4.4100439 of the $60 cap.

**Privacy.** The privacy sweep ran over each batch's outputs before the next batch, with 0 hits each
time. Raw JSON, error files, prompts and the probe stay under
`~/.cache/agent-skills/scratch/plan97/reviewer/`, outside the repository. Before this section's
commit, these checks ran over every file to be added:

- The privacy sweep found 0 hits in 20 files: the 19 files under `reviewer/treatment/` (the
  manifest, 15 rep copies and three `show_reps.txt` files) and this record.
- A script found none of the 71 session ids and message uuids of the raw JSON and stream files
  under `~/.cache/agent-skills/scratch/plan97/reviewer/` in any file under `reviewer/`. It found no
  `/var/folders` or `/private/var` path there either.
- A grep found no uuid-shaped string in the rep copies, the `show_reps.txt` files or this record.

### Controller ruling on the start-date finding

The Task 10 review asked for a ruling on whether the R4 start-date finding is a package fault. It is
not. The Packages section registered the excerpts as `specs/window.md:8` and the global constraints as
`:7-8` before any rep, so a row and a mutant for the start rule are absent by design. The Package change
check disproves the claim that matters, since R4's tests catch the wrong start-date versions. The
finding is a second reading of "stated rule". The reviewer text says that the global constraints bind
the task, and the mutant step takes its rules from the excerpts and the brief. That wording predates
Task 9, and control rep 1 met it too, so it is for the owner at the completion gate. R4 and R5 are not
rerun, and no package changes.

## Summary

This summary gives the final pass counts of plan 97's micro-tests and their cost. The counts cover only
the texts, fixtures, packages and model tier named below. Each fixture and each package is a small
synthetic project, written for this test.

**What was measured.** Two texts ran at the `sonnet` tier (`claude-sonnet-5-5` on Claude Code 2.1.323),
with five scored reps per fixture per arm, except the F8 treatment arm, which has 3 (see the table).

- The implementer text is `implementer-prompt.md` and `references/mutants.md` at `14ca1fd`, on
  fixtures F6, F7 and F8.
- The reviewer text is the `agents/task-reviewer.md` body and the Short Form at `70c94ec`, on
  packages R4, R5 and R6.
- Each control arm ran the same kind of text at `7b2976b`, on the same fixtures or packages, with the
  same kit. The implementer control also took D8's BASE substitution.
- No wording revision ran in either arm.

| Fixture or package | Bar for the treatment arm | Control | Treatment | Bar held |
|---|---|---|---|---|
| F6 | Plan test unchanged, a new test listed `failed` in the final revert section, and a `Strengthened:` line that names it | 0 of 5 | 5 of 5 | Held |
| F7 | A `Keeps: test_slugify_lowercases` line, both plan tests unchanged | 0 of 5 | 5 of 5 | Held |
| F8 | No `Keeps:` or `Strengthened:` line, every plan test unchanged | 5 of 5 (for information) | 3 scored reps, all pass | Not evaluated. The VOID stop fired after 3 scored reps |
| R4 | An Important finding that names `test_window_includes_end_date` as passing on the pre-change code | 0 of 5 | 4 of 5 | Held, at the threshold |
| R5 | No revert finding | 5 of 5 (for information) | 5 of 5 | Held, on a reading that the owner may rule on (Limits) |
| R6 | No revert finding | 5 of 5 (for information) | 5 of 5 | Held |
| All | No rep weakens a test | No weakening | No weakening | Held in the implementer reps. Reviewer reps have no tools, so the bar does not apply to them |

Each bar needs at least 4 of 5 scored reps. F6, F7, R4, R5 and R6 reached that count in this run. The
F8 bar is not claimed as met, because its count was never evaluated (Implementer treatment, The F8
stop).

**Spend.** The micro-test total is $4.4100439 of the $60 cap. It is the sum of `total_cost_usd` over
every rep and probe. Each arm's own figure is in its Spend table (Implementer control, Implementer
treatment, Reviewer control and Reviewer treatment).

**Controls for the owner's ruling (D9).** No control met a bar on F6, F7 or R4. The control counts are
F6 0 of 5, F7 0 of 5 and R4 0 of 5. So no control needs a ruling on that ground.

- On F6, the control already left the plan test unchanged and added a boundary test that failed on
  the revert, in 5 of 5 reps. It lacked only the `Strengthened:` line (Implementer control, D9).
- On R4, the control gave Approved with no Critical or Important finding in 5 of 5 reps (Reviewer
  control, R4).

**Another item for the owner at the completion gate.** In R4 treatment, reps 1 and 5 raised an
Important finding that the mutants have no row or mutant for the start-date rule, and reps 3 and 4
raised it under ⚠️. The controller ruled that this is no package fault. The packages registered the
excerpts as the rule source and the start rule is in the global constraints only. The reviewer text
says that the global constraints bind the task, while its mutant step takes rules from the excerpts
and the brief. The owner rules on that "stated rule" wording (Reviewer treatment, Controller ruling
on the start-date finding).

**Backlog item `specs/deferred_items.md:5719` stays open.** The item says that the task reviewer's
Full Form (`skills/subagent-driven-development/task-reviewer-prompt.md`) was never micro-tested. Its
progress note says that plan 93 ran R1 to R3 on the Full Form's `## Mutants` section, and that the rest
of the Full Form is still untested. Task 9 added check 7 to the Full Form, and a text change is one of
the item's revisit conditions. This micro-test ran the Short Form only (D8). So no rep ran the Full
Form, and no rep ran the Full Form's check 7. The untested part that the item names stands, and the
item stays open. The plan-completion protocol handles the item. This task does not edit it.

**Limits that the record states.**

- **The F8 stop.** F8 treatment reps 4, 5 and 6 are VOID, so the pre-registered stop fired and no
  further F8 rep ran. The 3 scored reps all pass. The 3 VOID reps also met the bar's reading, and they
  stay unscored. The owner rules whether to accept F8 on 3 of 3 or to allow more F8 reps on the same
  text (Implementer treatment, The F8 stop and Results).
- **The VOID rule and scratch files.** VOID rule 1 fired on harmless scratch writes under `/tmp` in 7
  of 35 implementer reps. That is 3 of 18 in the control and 4 of 17 in the treatment (Implementer
  treatment, Post hoc notes (a)). Each VOID rep left every plan test unchanged (the VOID reps
  paragraphs of Implementer control and Implementer treatment).
- **R4 sits at the threshold.** R4 treatment passed in reps 1 to 4. Rep 5 is a miss under reading
  rules 1 and 6, because its check 7 point stands outside the Critical and Important headings
  (Reviewer treatment, Treatment results). Rep 2 counts as a pass because reading rule 1 reads its
  finding by where it stands, although its verdict reads Approved.
- **R5 rests on a reading.** In R5 treatment reps 2 and 5, a "Mutant step checks:" list stands under
  the `Important (Should Fix)` heading after the word "None.", and item 7 of each list cites the
  revert and the `Keeps:` line. The count reads each list as a remark, under reading rules 1 and 5 and
  the controller's ruling. If the owner reads those two lists as revert findings, the R5 bar is not
  held (Reviewer treatment, Treatment results, R5, and Controller rulings before the treatment arm).
- **The example in the implementer guide.** The treatment guide's step 7 uses the phrase "such as the
  normal case beside a bug's fix" (`references/mutants.md:46`). It describes F7's kind of case, so
  F7's 5 of 5 may owe something to that example (Implementer treatment, Post hoc notes (b)).
- **Same fixtures and packages in both arms.** Each control and its treatment ran the same fixtures or
  packages, in one kit. The implementer arms ran the same scripts (Arms). The counts do not cover
  another model or another package (Reviewer treatment, What was measured).
- **No rep ran the Full Form.** The reviewer reps ran the Short Form only, and the counts do not cover
  the Full Form or the re-review prompt (Reviewer treatment, the opening paragraph and What was
  measured).
