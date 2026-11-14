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
- **A first commit without the fix.** F6 reps 1, 2, 3 and 5 report that a failed `sed` left
  `stock.py` unchanged at their first commit. Reps 1 and 3 amended that commit, and reps 2 and 5
  added a second commit. F6 reps 2 and 4 each had a first mutant run whose baseline failed. Each
  final tree holds the fix, and each final run's baseline passed.
- **Scratch files under `/tmp`.** All three VOID reps wrote one, although the control `mutants.md`
  says "Keep any scratch file in `<workspace>`, never in `/tmp`".

**Spend.** The control arm cost $1.4756486 for 18 reps (15 scored and 3 VOID), about $0.082 a
rep. With the two probes and the pilot, the micro-test total is $1.5729250 of the $60 cap.
