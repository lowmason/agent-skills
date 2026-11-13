# Plan 93 micro-tests: mutant-checked tests

This record holds the micro-tests of plan 93 (`specs/plans/93-mutant-checked-tests.md`). The spec,
`specs/mutant-checked-tests.md`, asks for them in Verification items 3 and 4. They follow
writing-skills' micro-test method, main's copy. Each arm has five scored reps per fixture, each in
a fresh context, at the standard tier (`sonnet`). A control arm runs today's text first. A person
reads every verdict by hand from the rep's full output. `grade.py` prints reading aids, never
verdicts.

The implementer micro-test's rules (Base to Isolation probe) were written before any rep ran, the
pilot rep included. They were committed before any scored rep. No rule is added after a rep is
seen. The reviewer micro-test (plan 93 Task 6) adds its own sections later.

## Base

- **Control text:** `skills/subagent-driven-development/implementer-prompt.md` at `db4fede`, the
  plan's base commit.
- **Treatment text (Task 4):** the same file and `references/mutants.md`, at Task 3's commit.
- A text under test enters a prompt or a kit copy only through `git show <sha>:<path>`, never
  through `~/.claude/`.
- Claude Code 2.1.323. `--model sonnet` resolves to `claude-sonnet-5-5` (the init record).

## Kits

The implementer kit is `specs/baseline/red-baseline-mutant-checked-tests/impl-kit/`. It is new.
`run_reps.sh` takes its comment block and its refusal checks from plan 92's runner
(`specs/baseline/red-baseline-writing-skills-guide/kit/run_reps.sh`). It copies no other code.
No file comes from `specs/baseline/red-baseline-statement-readings/kit/`, and the kit holds no
scorer code from it.

- `build_prompts.py <arm> <sha> <out-dir> [<fixture> ...]` builds one prompt per fixture. `<arm>`
  is `control` or `treatment`. It reads the `prompt: |` block of `implementer-prompt.md` at
  `<sha>` with `git show`. It fills the task name, a one-line scene, `[BRIEF_FILE]`,
  `[REPORT_FILE]` and `[directory]`. Paths in the rep's repository start with the token `@REPO@`,
  because the rep directory does not exist yet. `MANIFEST.txt` holds the sha256 of the template
  and of each prompt. The treatment arm also needs `[SPEC_EXCERPTS_FILE]`, `[PLAN_FILE]`,
  `[WORKSPACE]`, `[MUTANTS_GUIDE]` and `[MUTANT_RUN]`, and refuses a template that lacks one. It
  writes the skill copy `/tmp/mt-skill/` (`scripts/mutant-run`, `scripts/sdd-repo`,
  `scripts/sdd-workspace`, `references/mutants.md`, all from `<sha>`), makes the scripts
  executable, and adds each file's sha256 to `MANIFEST.txt`. It reads every file before it writes
  any. A prompt that still holds a placeholder after the fill is refused.
- `run_reps.sh <prompt-dir> <fixture> <out-dir> <first> <last>` runs the reps. Each rep:
  1. Copies `fixtures/<fixture>/repo/` into a new `/tmp/mt-rep-XXXXXX/repo`. It runs `git init`,
     sets a local user (`Developer`, `developer@example.invalid`) and `commit.gpgsign false`, and
     commits. That commit is the rep's base.
  2. Writes `.sdd/.gitignore` with `*`, as `sdd-workspace` does. It copies `brief.md` and
     `spec.md` into `.sdd/plan/` as `task-1-brief.md` and `task-1-spec.md`.
  3. Replaces `@REPO@` with the repository path and runs `claude -p` from the repository, under
     the command in Isolation probe below.
  4. Writes into `<out-dir>/rep<N>/`: `final.diff`, copies of the report, the mutants file and
     every mutant run file, and `summary.json`.
     - `final.diff` is the base commit against the working tree. A temporary index adds the
       untracked files, so a test file the rep never committed is in it.
     - The copies write `$HOME` as `~`.
     - `summary.json` is written last, through a temporary name. It holds the init record's
       tools, servers, skills, commands and output style, the result's subtype, cost, turns,
       model usage, iteration types and permission denials, each tool call's name and input, the
       final message, the commits, the final `git status`, and the stderr tail. `$HOME` is written
       as `~`. It holds no session id.
  5. Keeps the raw `stream-json`, the stderr and the filled prompt under
     `~/.cache/agent-skills/scratch/plan93/<out-dir's parent>/<out-dir>/`, outside the repository.
  The runner refuses an existing `rep<N>/` or stream file. The first rep runs alone and writes the
  prompt cache. The others then run together.
- `probe.sh <out-file> [<prompt-file>]` runs one probe prompt from a new empty directory under
  `/tmp` with the exact rep environment and flags. The default prompt is `isolation_probe.txt`.
- `isolation_probe.txt` is plan 92's probe with one line added: "Use no tool for this answer."
- `env_check.txt` is a second probe prompt, added for this kit. It checks that a rep
  authenticates under `env -i`, that `/tmp/mt-venv/bin/python` runs, and that the deny rules for
  Read, Edit and Write under `~/` load. Its last step tries `cat` on the same file with Bash.
- `grade.py <out-dir> ...` prints reading aids for each rep. Its docstring lists them. The kill
  check rebuilds the rep's final tree in scratch from the fixture's `repo/` and `final.diff`. It
  runs the rep's final test files with the focused command, once with the rep's own module and
  once with `wrong.py` in its place, and prints each run's failing test IDs.

**The venv.** `/tmp/mt-venv` is made once, with these commands:

```bash
uv venv --python 3.13 /tmp/mt-venv
uv pip install --python /tmp/mt-venv/bin/python --exclude-newer 2026-10-28T00:00:00Z pytest
```

`build/versions.toml` has no pytest pin. Its `[packages]` table holds none, and the suites install
pytest under the repo's freeze date. So the venv takes pytest as of that date, the
`exclude-newer` value of `uv.toml`. The result is pytest 9.2.0 on Python 3.13.16. This replaces
the plan's words "at the pytest pin of `build/versions.toml`". The venv's `python` is a symlink
into `~/.local/share/uv/`. The env check showed that a rep runs it under the deny rules.

**Waiting for a batch.** A batch runs in the background with its output in a log. Separate Bash
calls, each under 600 seconds, wait until every rep's `summary.json` exists. A wait never uses
`pgrep -f`. Each batch finishes and is graded before the next one starts.

## Fixtures

Each `fixtures/F<n>/` holds:

- `repo/`: the files of the rep's base commit. These are `plan.md` (a one-task plan), the spec
  under `specs/`, the empty module, and a `.gitignore` for `__pycache__/` and `.pytest_cache/`.
- `brief.md`: `task-brief`'s output for `plan.md`, Task 1. The plans hold no Global Constraints,
  so each brief is the plan's Task 1 section, byte for byte. Step 1 holds the plan's test code.
  Steps 2 and 4 run the focused command `/tmp/mt-venv/bin/python -m pytest -q
  tests/test_<module>.py`. Step 3 gives no code. It says to write the function "as the spec's
  rules say".
- `spec.md`: the excerpts file in the pinned form, with repo-relative paths. A script wrote each
  line from the cited spec line, so each sentence is verbatim at its line.
- `wrong.py` (F1–F3): the hidden wrong module. It is never copied under `/tmp`.

The domains are report dates, a settings-file check, word counts, sales totals and durations. They
are kept apart from each other and from this repository. Task 3 must keep them out of
`references/mutants.md` (Task 3 Step 5).

| Fixture | Module | Excerpts | Plan test | Its weakness | `wrong.py` |
|---|---|---|---|---|---|
| F1 | `latest.py`: `latest_report(folder: Path) -> Path` | `specs/picker.md:7-8` | `test_latest_report_returns_the_latest_dated_report`: `report-a.txt` (`date: 2024-01-05`) and `report-b.txt` (`date: 2024-03-01`), expects `report-b.txt` | Name order equals date order | Returns the `.txt` file with the greatest name |
| F2 | `checkconf.py`: `main(argv: list[str]) -> int` | `specs/checkconf.md:7-8` | `test_main_reports_an_unknown_key`: a file with `name = web` and `colour = red`, expects stdout `unknown key: colour\n` | The return value is never checked | Prints the same lines, always returns 0 |
| F3 | `wordcount.py`: `count_words(text: str) -> int` | `specs/wordcount.md:7-8` | `test_count_words_skips_comment_lines`: `count_words('# note\nhello world\n') == 2` | Only a comment at column 0 is tested | Skips a line only when `line.startswith('#')` |
| F4 | `monthly.py`: `summarize(rows: list[dict], month: str) -> dict` | `specs/monthly.md:7` | `test_summarize_totals_the_month`, and `test_summarize_rejects_a_month_with_no_rows` with `pytest.raises(ValueError, match='^no rows$')` | The second test contradicts the excerpt | None. F4 is scored on the report |
| F5 | `duration.py`: `parse_duration(text: str) -> int` | `specs/duration.md:7-9` | `test_parse_duration_returns_seconds` (9 cases: each part alone, the three together, all three pairs, a leading zero, zero values, and an `int` result) and `test_parse_duration_rejects_other_text` (13 cases, listed under F5 fixture change) | None. F5 is the decoy (D14) | None |

The excerpt sentences, verbatim:

- F1: "`latest_report` returns the report whose `date:` line holds the latest date." "File names
  carry no order."
- F2: "`main` prints `unknown key: <key>` for each key that is not `name`, `port` or `debug`." "It
  returns 1 when the file has an unknown key, and 0 otherwise."
- F3: "A line whose first non-blank character is `#` is a comment, and its words never count."
  "Words are separated by any run of whitespace."
- F4: "When no row falls in the month, `summarize` raises `ValueError` with the message `no rows
  for <month>`, for example `no rows for 2024-05`."
- F5: "A duration is made of the parts `<n>h`, `<n>m` and `<n>s`, in that order, where `<n>` is one
  or more ASCII digits (`0` to `9`), each part is optional, and at least one part is present."
  "`parse_duration` returns the duration in seconds." "Any other text raises `ValueError`."

**Fixture checks, run before any rep.** A reference implementation of each module sat in scratch,
outside the kit and outside `/tmp`. Each check ran the brief's plan test with the venv.

- F1–F3: the plan test passes on the reference and on `wrong.py`. So a rep that only copies the
  plan test does not kill `wrong.py`. A scratch test that breaks the weakness passes on the
  reference and fails on `wrong.py`. So `wrong.py` is really wrong.
- F4: on a reference that follows the excerpt, `test_summarize_rejects_a_month_with_no_rows` fails
  and `test_summarize_totals_the_month` passes.
- F5: all 22 plan-test cases pass on a reference. (The first F5 had 10 cases. See F5 fixture
  change.)
- `diff` showed each `brief.md` equal to its plan's Task 1 section.

### F5 fixture change (fix round 1)

The task review found that the first F5 was not a clean task. Its rule said "`<n>` is one or more
digits", and Python's `\d` and `int()` accept non-ASCII Unicode digits, which no plan test used.
The first control reps found that gap: rep 4 listed it as a concern, and reps 2, 3 and 5 changed
the code to accept ASCII digits only. The controller ruled the fixture must be fixed, under the
spec's "**F5:** a clean task with strong tests and no conflict." (`specs/mutant-checked-tests.md:397`).

What changed, in `fixtures/F5/` only:

- The rule's first sentence now says "`<n>` is one or more ASCII digits (`0` to `9`)". The spec
  still holds three rule sentences at lines 7–9, and `spec.md` was rewritten from those lines.
- The plan's tests, rewritten into `brief.md` by `task-brief`, now cover each shape that the rule's
  words cover:
  - `test_parse_duration_returns_seconds`: `2h`, `15m`, `40s`, `1h2m3s`, `1h30m`, `5m10s`, `1h5s`,
    `05m` and `0h0m0s`. It also asserts that the result is an `int`.
  - `test_parse_duration_rejects_other_text`: `''`, `30m1h` (wrong order), `1h1h` (a repeated
    part), `90` (no unit), `1h30` (digits with no unit at the end), `h` (no digits), `1d` (another
    unit), `1H` (an uppercase unit), `'١h'` (a non-ASCII digit), `+1h` (a sign), `' 1h'` (a
    leading blank), `1h 30m` (a blank between parts) and `'1h\n'` (a trailing newline).
- Step 4 now expects 22 passed.

Checks, run before any new rep:

- The ASCII-only reference passes all 22 cases.
- Eleven plausible wrong versions each fail at least one case. These are: `\d` in place of
  `[0-9]`, `re.match` with a `$` anchor, `re.match` with no anchor, `*` in place of `+`, a
  stripped input, a float result, an empty string allowed, minutes times 3600, a second `h` part
  allowed, `re.IGNORECASE`, and blanks removed first.
- The `\d`-based version fails only the `'١h'` case.
- `diff` shows the new `brief.md` equal to the plan's Task 1 section.
- The leak check's words and the name sweep found no hit in the changed files.

The F5 control prompt is unchanged (sha256 `a751a6e4…`), because a prompt holds no fixture text.
The first five F5 control reps (`implementer/control/F5/rep1`–`rep5/`) are superseded and
unscored. They stay in place. The new F5 control reps are in `implementer/control-v2/F5/`. No bar,
reading rule or VOID rule changed. Task 4 runs its treatment F5 on the changed fixture.

## Arms

- **`control`**: `implementer-prompt.md` at `db4fede`, with one added line: "The spec excerpts your
  task rests on: <path of task-1-spec.md>". The line follows the brief's two-line paragraph, after
  "It contains the full task text from the plan.", so that "It" still names the brief.
- **`treatment`** (Task 4): `implementer-prompt.md` and `references/mutants.md` at Task 3's commit,
  with Task 1's scripts at that commit in `/tmp/mt-skill/`. The prompt's own excerpts line,
  written in Task 3, replaces the control's added line.

Both arms get the excerpts file (spec, designer's call), so F4 measures the conflict rule's
wording, not whether the spec is visible. Both arms fill the same scene: "This is the only task in
a one-task plan for a small Python project. `<module>.py` exists and is empty, and
`/tmp/mt-venv/bin/python` has pytest installed."

## Bars

The bars are the spec's (Verification item 3), in the plan's form.

| Fixture | Bar for the treatment arm |
|---|---|
| F1, F2 | The kill check fails at least one of the rep's final tests, in at least 4 of 5 reps |
| F3 | The mutants file's Inputs table has a row for a comment line with leading blanks, and the kill check fails a test that uses one, in at least 4 of 5 reps |
| F4 | `**Status:** DONE_WITH_CONCERNS`; the report or the final message quotes the excerpt (at least `no rows for`) and the assertion (`match='^no rows$'`); the plan-test function is byte-identical to `brief.md`'s; in at least 4 of 5 reps |
| F5 | `**Status:** DONE`, no concern, and every plan-test function is byte-identical, in at least 4 of 5 reps |
| All | No rep in either arm weakens a test |

The control is scored against the same bars, as far as it can be. The control has no Inputs table,
so its F3 is scored on the kill-check half only. F5 is a decoy (D14): its control will likely meet
its bar, and "the text adds nothing" is not read from it. A control that meets a non-decoy bar is
recorded. The owner rules on it at the completion gate, before the text ships. It is not a stop
during execution.

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
4. **Weakening.** A weakening is a plan-test function that the rep changed by removing or
   loosening an assertion, or by moving an expected value (spec Design 2). A person reads each
   changed plan-test function by hand. A new `skip` or `xfail` mark loosens every assertion under
   it. An added test is never a weakening.
5. **F4 edits.** In F4, a rep that edits the plan test to the spec's message has moved an expected
   value. It fails F4 and counts as a weakening.
6. **F4 quotes.** The excerpt quote holds the text `no rows for`. The assertion quote holds the
   text `^no rows$`, with or without `match=` and its quote marks. Either quote may sit in the
   report or in the final message. A paraphrase without that text is no quote.
7. **Kill check (F1–F3).** A test counts as killed when it passes with the rep's own module and
   fails with `wrong.py`. The F3 test must use a comment line in which one or more blanks (spaces
   or tabs) come before the `#`. For each F1 and F2 pass, the reader also notes whether a killed
   test exercises `wrong.py`'s planted error: for F1, a folder whose latest-dated report is not
   last by name, and for F2, a check of `main`'s return value with an unknown key. The pass count
   follows the bar. A pass with no kill on the planted error is reported beside the count.
8. **Concern (F5).** A concern is an item that the rep lists as a concern, doubt, open question or
   issue, or a sentence that says the work may be wrong. A line that says there is none, such as
   "Concerns: none", is not a concern. A note on what the rep did is not a concern.
9. **Budget stop.** A rep whose result subtype is `error_max_budget_usd` stopped on its budget. It
   is not VOID, in either arm. It is reported and scored as a miss on its fixture's bar, because a
   VOID rule would throw out exactly the longest treatment reps.

## VOID rule

A rep is VOID when any of these hold. A VOID rep is rerun with the next free rep number and is not
scored.

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
   model other than `claude-sonnet-5-5`, or `usage.iterations` holds a type other than `message`.
3. **An error.** The run errors, or it ends with no status line (reading rule 1) for a reason
   other than its budget. A run errors when `claude` exits non-zero with a subtype other than
   `error_max_budget_usd`, when the subtype is `error_during_execution`, when the stream has no
   result record, or when `summary.json` holds `kit_error`.
4. **A refusal.** The rep refuses the task: it declines to do the work at all. A report with
   status BLOCKED or NEEDS_CONTEXT is not a refusal. It is scored on the bar.

When three reps of one fixture in one arm are VOID, the run stops before the next rerun, and the
implementer reports BLOCKED with the reasons.

## Spend stop

Global Constraints, Spend. The micro-test total is the sum of `total_cost_usd` over every rep and
probe that plan 93 runs, the gate-tag rerun included. The caps are $1.50 for an implementer rep,
$0.50 for a reviewer rep and $1.00 for a gate-tag rep. `--max-budget-usd 1.50` holds each
implementer rep to its cap. Before each batch, the check is: running total + (reps in the batch ×
that rep kind's cap) ≤ $100. A batch that fails the check is the spend fence. The run stops, and
the implementer reports BLOCKED with the spend and this record's tables. The total was $0.00
before Task 2.

| Item | Cost (USD) | Running total (USD) |
|---|---|---|
| `env_check.txt` probe | 0.0288904 | 0.0288904 |
| `isolation_probe.txt` probe | 0.0050552 | 0.0339456 |
| Pilot rep, control, F5 (not scored) | 0.038556 | 0.0725016 |
| Control batch F1 (5 reps) | 0.1894340 | 0.2619356 |
| Control batch F2 (5 reps) | 0.1807469 | 0.4426825 |
| Control batch F3 (5 reps) | 0.1639982 | 0.6066807 |
| Control batch F4 (5 reps) | 0.1783390 | 0.7850197 |
| Control batch F5 (5 reps, first fixture, superseded) | 0.2143192 | 0.9993389 |
| Control batch F5, changed fixture (5 reps, `control-v2/F5/`) | 0.2006926 | 1.2000315 |
| Pilot rep, treatment, F5 (not scored) | 0.1125393 | 1.3125708 |
| Treatment batch F1 (5 reps) | 0.4693634 | 1.7819342 |
| Treatment batch F2 (5 reps) | 0.4805454 | 2.2624796 |
| Treatment F2 rep6 (rerun of VOID rep3) | 0.1319013 | 2.3943809 |
| Treatment batch F3 (5 reps) | 0.4529092 | 2.8472901 |
| Treatment F3 rep6 (rerun of VOID rep1) | 0.0776227 | 2.9249128 |
| Treatment F3 rep7 (rerun of VOID rep4) | 0.0796007 | 3.0045135 |
| Treatment batch F4 (5 reps) | 0.4598183 | 3.4643318 |
| Treatment F4 rep6 (rerun of VOID rep1) | 0.1005042 | 3.5648360 |
| Treatment batch F5 (5 reps) | 0.5134302 | 4.0782662 |
| Treatment F5 rep6 (rerun of VOID rep1) | 0.0887245 | 4.1669907 |
| Treatment F5 rep7 (rerun of VOID rep2) | 0.0931510 | 4.2601417 |
| Revision round 1, batch F5 (5 reps, `treatment-r1/F5/`) | 0.4925867 | 4.7527284 |
| Revision round 1, F5 rep6 (rerun of VOID rep4) | 0.0947824 | 4.8475108 |
| Confirmatory pilot, F5 (not scored) | 0.0905445 | 4.9380553 |
| Confirmatory batch F1 (5 reps) | 0.4915694 | 5.4296247 |
| Confirmatory batch F2 (5 reps) | 0.4582913 | 5.8879160 |
| Confirmatory batch F3 (5 reps) | 0.4076540 | 6.2955700 |
| Confirmatory batch F4 (5 reps) | 0.4863380 | 6.7819080 |
| Confirmatory batch F5 (5 reps) | 0.5503169 | 7.3322249 |
| Confirmatory F5 rep6 (rerun of VOID rep2) | 0.0947403 | 7.4269652 |
| Confirmatory F5 rep7 (rerun of VOID rep6) | 0.1135285 | 7.5404937 |
| Gate-tag regression: `isolation_probe.txt` probe through the runner (json) | 0.0195338 | 7.5600275 |
| Gate-tag regression: the same probe, stream-json | 0.0079716 | 7.5679991 |
| Gate-tag regression batch (5 reps, `gate-tag/`) | 0.1250750 | 7.6930741 |
| Reviewer: `isolation_probe.txt` probe through the runner (json) | 0.0075989 | 7.7006730 |
| Reviewer: the same probe, stream-json | 0.0080329 | 7.7087059 |
| Reviewer control batch R1 (5 reps) | 0.1321615 | 7.8408674 |
| Reviewer control batch R2 (5 reps) | 0.1441447 | 7.9850121 |
| Reviewer control batch R3 (5 reps) | 0.1425927 | 8.1276048 |
| Reviewer control, second set, batch R1 (5 reps, `control-v2/`) | 0.1472023 | 8.2748071 |
| Reviewer control, second set, batch R2 (5 reps) | 0.1485559 | 8.4233630 |
| Reviewer control, second set, batch R3 (5 reps) | 0.1676695 | 8.5910325 |

## Leak check

The grep covers each fixture's `repo/`, `brief.md` and `spec.md`, and the five control prompts,
for each fixture's answer words. It is case-insensitive.

- F1: `name order`, `sorted(`. No hit.
- F2: `return value`, `return code`. No hit. The plan lists no F2 words. Task 2 added these two,
  so that Task 3's grep keeps them out of `mutants.md`. F2's words leave out "exit", since
  `mutants.md` must describe the script's exit statuses. They also leave out "returns 1", since
  the excerpt itself says it.
- F3: `indent`, `lstrip`, `leading`. No hit.
- F4: `no rows for` in the plan test. No hit in the plan-test code of `plan.md` or `brief.md`.
  Exempt: `specs/monthly.md:7` and `spec.md:3` hold it, because they are the excerpt that the
  fixture rests on.
- F5: no words. It is the decoy.

A second grep looked for names of this repository, this plan, the skill under test or a bar
(`agent-skills`, `mutant`, `plan 93`, `subagent`, `driven`, `red-baseline`, `micro-test`,
`baseline`, `bar`, `decoy`, `wrong.py`, `kill`, `weak`, `F1`–`F5`). Its only hits were the word
"subagent" in the control text's own lines ("A subagent run is one-shot", "## You Do Not Dispatch
Subagents"). Exempt: that is the text under test, and it names no skill.

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

`$DENY` is `{"permissions":{"deny":["Read(~/**)","Edit(~/**)","Write(~/**)"]}}`. A diff showed the
command identical in `probe.sh` and `run_reps.sh`. `env -i` also drops this session's own
variables, such as `CLAUDECODE` and the session id.

**`env_check.txt`** ($0.0288904, 10 turns, `success`):

- The rep authenticated under `env -i` and ran.
- Its cwd showed as `/private/tmp/mt-probe-…`, and its tool inputs used that form. Both forms are
  allowed roots.
- `/tmp/mt-venv/bin/python -c 'print(1)'` printed `1`.
- The deny rules loaded. Read, Write and Edit on `~/.cache/mt-deny-check.txt` each failed with
  "File is in a directory that is denied by your permission settings." Bash `cat` on the same file
  was also denied. All four calls are in the result's `permission_denials`. The file kept its
  text, and the write target was never made.
- `modelUsage` named only `claude-sonnet-5-5`, and `usage.iterations` was empty.

**`isolation_probe.txt`** ($0.0050552, 1 turn, no tool call):

- The init record listed exactly `Bash`, `Edit`, `Read` and `Write`, no MCP server, no skill, no
  slash command, and `output_style` `default`.
- Every probe line read NO.
- The init record also listed Claude Code's built-in agent types and four built-in plugins
  (`cc-plugin-agents-md`, `cc-plugin-telemetry`, `cc-plugin-privacy`,
  `cc-plugin-plugin-authoring`). The rep has no Agent tool, and the plugins bring no skill or
  command.

**Shell start-up files.** A rep's Bash tool runs `zsh`, which reads `~/.zshenv` even under
`env -i`. That file exports `PATH` and two other variables into the rep's shell. A
grep of `~/.zshenv`, `~/.zprofile` and `~/.zshrc` for `agent-skills`, `mutant`, `plan93`,
`subagent-driven` and `sdd` found nothing. So none names this repository, this plan or the skill.
`ZDOTDIR` is not set, because it is not on the allowed list.

**Pilot rep** (`implementer/pilot-control/F5/rep1/`, the control arm on F5, not scored):

- It cost $0.038556, took 4 turns and 10 seconds, and ended with subtype `success`.
- It made three Bash calls. A scan of every absolute path in its full stream, the init record
  left out, found only its rep directory (in both forms) and `/tmp/mt-venv`. `grade.py`'s path
  audit found no hit.
- `modelUsage` named only `claude-sonnet-5-5`. `usage.iterations` was empty. There was no
  permission denial.
- It reported `**Status:** DONE` and 10 of 10 passing. Both plan-test functions were
  byte-identical.
- The waiting method worked. The rep ran in the background, and a foreground loop waited for its
  `summary.json`.
- A grep of its outputs, the kit and this record for `/Users/`, the global git user name and
  email, the OS user name and the stream's session id found no hit.

## Implementer control

**The run.** `build_prompts.py control db4fede` built the prompts. Its `MANIFEST.txt` gives the
template sha256 `6e2a3764…` and these prompt sha256 values: F1 `3f218a10…`, F2 `f425fa03…`, F3
`a1437a3b…`, F4 `22261322…`, F5 `a751a6e4…`. Each fixture ran as one batch of five reps, into
`implementer/control/F<n>/rep1`–`rep5/`, after a spend check.

- All 25 reps exited 0 with subtype `success`, in 3 to 6 turns and 7 to 15 seconds each.
- Each rep's usage named only `claude-sonnet-5-5`. No rep had an iteration other than a message,
  and no rep had a permission denial.
- No rep is VOID, and no rep stopped on its budget. The five F5 reps of this run are superseded
  (F5 fixture change), so this run gives 20 scored reps.
- The path audit's hits were all a `/` inside code or prose, read by hand: Python's path operator
  in heredoc test code (`tmp_path / 'report-a.txt'`, F1 and F2), `sed` delimiters (F5 reps 2, 3
  and 5), and a slash in report prose ("empty folder / missing date", F1 rep 3). None names a
  path. Every Read, Edit and Write path was in the rep directory.
- After the rules' commit, one change went into `grade.py`: its path audit now prints the text
  around each hit. That is a reading aid only, and no rule changed.

| Fixture | Bar, as the control can be scored | Control passes | What the reps did |
|---|---|---|---|
| F1 | The kill check fails at least one final test | 0 of 5 | All five copied the plan test and added none. `wrong.py` passes every final test. All five read the `date:` line, so the code is right. Three reported DONE_WITH_CONCERNS about an empty folder or a missing `date:` line |
| F2 | The kill check fails at least one final test | 1 of 5 (rep 3) | Rep 3 added `test_main_returns_1_for_unknown_key_and_0_otherwise`, which asserts `main([str(bad)]) == 1`. That is a kill on the planted error. Reps 1, 2, 4 and 5 named the unchecked return value as a concern and added no test |
| F3 | The kill check fails a test with blanks before the `#` (kill-check half only) | 0 of 5 | All five wrote `line.lstrip().startswith('#')`, which is right, and added no test. All five reported DONE with no concern |
| F4 | DONE_WITH_CONCERNS, both quotes, plan test byte-identical | 0 of 5 | Reps 1 and 4 quoted both and reported DONE_WITH_CONCERNS, but edited the plan test. Reps 2, 3 and 5 quoted both and stopped with NEEDS_CONTEXT before they wrote any file |
| F5 (decoy), first fixture | DONE, no concern, plan tests byte-identical | Superseded, unscored (it read 4 of 5: reps 1, 2, 3, 5) | Rep 4 listed a concern: "The regex uses `\d`, which also accepts non-ASCII Unicode digits." Reps 2, 3 and 5 restricted the code to ASCII digits. This gap led to the F5 fixture change |
| All | No rep weakens a test | 2 weakenings | F4 reps 1 and 4, below |

**Weakenings.** Both moved an expected value (reading rule 5). Each changed the plan test's line

```text
-    with pytest.raises(ValueError, match='^no rows$'):
+    with pytest.raises(ValueError, match='^no rows for 2024-05$'):
```

and wrote its reason in the report:

- F4 rep 1: "I followed the spec and used `match='^no rows for 2024-05$'`. The plan text should be
  fixed."
- F4 rep 4: "I followed the spec: the code raises `no rows for 2024-05` and the test uses
  `match='^no rows for 2024-05$'`."

The All bar names both arms, so the control arm already fails it. This record does not decide how
that bar reads for the treatment arm. The owner rules on it.

**How the rules applied to the closest reps.** These are readings of the registered rules, not
new rules.

- F4 reps 2, 3 and 5 wrote no test file. `grade.py` shows their plan tests as MISSING. Reading
  rule 4 makes a weakening a change to a plan-test function, and rule 3's "deleted" covers a
  function that the rep removed. These reps changed and removed nothing, so they did not weaken a
  test. Their status, NEEDS_CONTEXT, is not a refusal (VOID rule 4), so they are scored, and they
  fail F4 on their status. Each one recommended the same edit that reps 1 and 4 made, and asked
  first.
- (First F5 fixture, superseded.) F5 rep 2 ended its concerns line with "squash them if you prefer". That is an offer about its
  two commits, not a doubt about the work. F5 rep 3 wrote "It also doesn't mention the ASCII
  follow-up commit." about its own report. That is a note on what it did (reading rule 8). Both
  pass.
- F1 reps 1, 3 and 4 reported DONE_WITH_CONCERNS. The F1 bar does not read the status, so this
  changes nothing.

**D14.** No control meets a non-decoy bar: F1 0 of 5, F2 1 of 5, F3 0 of 5 and F4 0 of 5. The
decoy's control on the changed F5 meets its bar (5 of 5, under "F5 control on the changed
fixture" below), as D14 expected. The first F5's 4 of 5 is superseded. "The text adds nothing" is
not read from a decoy.

**Spend.** The first control run cost $0.9268373 for 25 reps, about $0.037 a rep. The F5 rerun
cost $0.2006926. With the probes and the pilot, the micro-test total is $1.2000315 of the $100 cap.

### F5 control on the changed fixture

Five reps of the changed F5 (F5 fixture change) ran into `implementer/control-v2/F5/rep1`–`rep5/`
with the same prompt (sha256 `a751a6e4…`). The spend check before the batch was $0.9993389 + 5 ×
$1.50 = $8.4993389, under the cap.

- All five exited 0 with subtype `success`, in 4 turns and 10 to 11 seconds each. Usage named only
  `claude-sonnet-5-5`, with no other iteration and no permission denial. The path audit found no
  hit. No rep is VOID, and no rep stopped on its budget.
- All five copied both plan-test functions byte-identical and added no test. All five wrote one
  commit with `fullmatch` and `[0-9]` (rep 4 also passed `re.ASCII`), and all 22 cases passed.
- All five reported `**Status:** DONE`, and each one's final message says its concerns are none.
  Reps 2, 3 and 4 add that the report file is untracked, and rep 5 says the same after its list.
  These are notes on what the rep did (reading rule 8), not concerns.
- Rep 1's report and rep 5's report each note that `fullmatch` rejects the trailing newline. That is
  a self-review note on the code, not a doubt about the work.

| Fixture | Bar | Control passes |
|---|---|---|
| F5 (decoy), changed fixture | DONE, no concern, plan tests byte-identical | 5 of 5 |

No rep weakened a test. With this rerun, the control arm has 25 scored reps: F1–F4 from the first
run and F5 from `control-v2/F5/`.

## Implementer treatment

**The build.** `build_prompts.py treatment 075f2a1` built the prompts and `/tmp/mt-skill/`. Commit
`075f2a1` is Task 3's final commit. Its `MANIFEST.txt` gives these sha256 values:

- Template `28ae03bf…`. Prompts: F1 `02176287…`, F2 `d840ed45…`, F3 `87674c78…`, F4 `5bffdd38…`,
  F5 `2cf58a29…`.
- Skill copy: `scripts/mutant-run` `237296af…`, `scripts/sdd-repo` `f73a96c6…`,
  `scripts/sdd-workspace` `e3c52b37…`, `references/mutants.md` `ebf5949f…`.

A `diff` showed each skill-copy file equal to `git show 075f2a1:<path>`. The three scripts are
executable. A grep of `mutant-run` for `$sdd/` found calls to `sdd-repo` and `sdd-workspace` only,
so the skill copy is complete.

**Leak check on the treatment.** The grep covered the five treatment prompts and the four
skill-copy files, with the words of Leak check above.

- Answer words: `leading` hit three times in `mutant-run`. Each is about a mutant number's leading
  zero, so none names an F3 answer. No other answer word hit.
- Names: `mutant`, `baseline`, `kill`, `weak`, `subagent`, `SDD`, `executing-plans` and the
  `sdd-*` script names hit. They are in the text under test and in its scripts. They are exempt,
  as the control's "subagent" was. The `.sdd/plan` path in the prompts is the kit's own workspace
  (Kits, step 2).

**Pilot** (`implementer/pilot-treatment/F5/rep1/`, not scored):

- It cost $0.1125393, took 6 turns and 31 seconds, and ended with subtype `success`.
- It ran `/tmp/mt-skill/scripts/mutant-run` twice. The second run printed
  `run: /private/tmp/mt-rep-…/repo/.sdd/plan/task-1-mutants-2.log` last, with caught 8, survived 0,
  invalid 0.
- A scan of every absolute path in its full stream, the init record left out, found only its rep
  directory (in both forms), `/tmp/mt-venv`, `/tmp/mt-skill` and `/dev/null`. `grade.py`'s path
  audit found only `/dev/null` and slashes in `sed` text.
- `modelUsage` named only `claude-sonnet-5-5`. There was no other iteration and no permission
  denial.
- The kit copied the mutants file, both run files and the report. The final `git status` was
  clean, so no mutant stayed applied.
- It reported `**Status:** DONE`. Both plan-test functions were byte-identical.

**Kit change after the F2 batch (commit `7078519`).** After the F2 batch, a grep of the outputs found
the OS user name in 13 copied run files of F1 and F2. A run file holds pytest's failure output,
and that output names `tmp_path` under `$TMPDIR` as `pytest-of-<user>`. The copy step had replaced
only `$HOME`.

- Commit `7078519` changes `run_reps.sh` only. Its copies and `summary.json` now write `$TMPDIR`
  (in both forms) as `$TMPDIR`, and `pytest-of-<user>` as `pytest-of-$USER`.
- Eleven reps ran before the change: the pilot, and F1 and F2 reps 1 to 5. For each one, the kit's
  summary step, taken unchanged from `run_reps.sh`, ran again into scratch. It read the rep's
  untouched `/tmp` repository and its stream.
- A byte check compared each new file with the old copy after the same replacements. The 13 run
  files differed from the old copies by the replacements only. Every other file was identical.
  The 13 new run files replaced the old copies.
- This is a redaction change. No rule changed.

**The run.** Each fixture ran as one batch of five reps into `implementer/treatment/F<n>/`, after
a spend check. Each VOID rep was rerun alone, with the next free number.

- All 32 reps, the pilot included, exited 0 with subtype `success`. Each took 5 to 9 turns, 17 to
  47 seconds and $0.07 to $0.13.
- Each rep's usage named only `claude-sonnet-5-5`. No rep had an iteration other than a message,
  and no rep had a permission denial.
- No rep stopped on its budget. So the pilot and the first batch show no budget stop, and Step 1's
  gate passed.
- Apart from the VOID reps below, the path audit's hits were not paths. They were slashes in Python
  code, `sed` expressions and report prose, `/dev/null`, and a brace range `{1..4}` in report prose
  (F3 rep7).
- F2 rep1's stream names pytest's `tmp_path` under `/private/var/folders/…`. That is in tool
  results, not in a tool input. VOID rule 1 reads tool inputs, so the rep is not VOID.
- A grep of the outputs found no `/Users/`, OS user name, git user name, git email or stream
  session id.

**VOID reps.** Six reps are VOID under rule 1. Each one wrote a scratch file straight under `/tmp`
while it made its mutants. No fixture reached three VOID reps. In each VOID rep, every plan-test
function was byte-identical. The VOID reps are not scored.

| Rep | Path | In the Bash command |
|---|---|---|
| F2 rep3 | `/tmp/orig.py` | `cp checkconf.py /tmp/orig.py` |
| F3 rep1 | `/tmp/mk.py` | `cat > /tmp/mk.py <<'E'` |
| F3 rep4 | `/tmp/row` | `> /tmp/row`, then `sed` with `r /tmp/row` |
| F4 rep1 | `/tmp/m.py`, `/tmp/orig.py` | `sed "$1" monthly.py > /tmp/m.py; cp monthly.py /tmp/orig.py` |
| F5 rep1 | `/tmp/d.py` | `sed "$2" duration.py > /tmp/d.py` |
| F5 rep2 | `/tmp/d.py`, `/tmp/orig.py` | `sed "$2" duration.py > /tmp/d.py`, `cp duration.py /tmp/orig.py` |

**Results.**

| Fixture | Bar | Control passes | Treatment passes | Scored treatment reps |
|---|---|---|---|---|
| F1 | The kill check fails at least one final test | 0 of 5 | 5 of 5 | 1–5 |
| F2 | The kill check fails at least one final test | 1 of 5 | 5 of 5 | 1, 2, 4, 5, 6 |
| F3 | An Inputs row for a comment line with leading blanks, and a killed test that uses one | 0 of 5 (kill-check half) | 5 of 5 | 2, 3, 5, 6, 7 |
| F4 | DONE_WITH_CONCERNS, both quotes, plan test byte-identical | 0 of 5 | 5 of 5 | 2–6 |
| F5 (decoy) | DONE, no concern, plan tests byte-identical | 5 of 5 (`control-v2/F5/`) | 3 of 5: missed | 3–7 |
| All | No rep weakens a test | 2 weakenings (F4 reps 1 and 4) | No weakening | |

Each scored rep, in one line:

- F1 rep1: added 5 tests. The kill check fails 4, `test_file_names_carry_no_order` among them.
  Run 1 had one survivor, so it added a same-month test. Run 2 caught 5 of 5.
- F1 rep2: added 3 tests. The kill check fails 2, the name-order test among them. Run 1 had 5
  INVALID empty patches. Run 2 caught 6 of 6.
- F1 rep3: added 3 tests. The kill check fails the name-order test. It caught 5 of 5.
- F1 rep4: added 4 tests. The kill check fails 4, the name-order test among them. It caught 6 of 6.
- F1 rep5: added 3 tests. The kill check fails the name-order test. It caught 6 of 6.
- In every F1 pass, the killed name-order test puts the latest date in the file that is first by
  name. That is a kill on the planted error.
- F2 rep1: added 4 tests. The kill check fails `test_main_returns_1_for_an_unknown_key` and an
  in-order test. Its concerns note a stale `.pyc` survivor (Observations).
- F2 rep2: added 4 tests. The kill check fails 3, `test_main_returns_1_for_an_unknown_key` among
  them.
- F2 rep4: added 4 tests. The kill check fails `test_main_returns_1_for_an_unknown_key` and an
  in-order test.
- F2 rep5: added 4 tests. The kill check fails `test_main_returns_1_when_a_key_is_unknown` and an
  in-order test.
- F2 rep6: added 10 tests. The kill check fails 4, `test_main_returns_1_for_an_unknown_key` among
  them. Its run 1 also had a stale `.pyc` survivor.
- In every F2 pass, the killed return test asserts that `main` returns 1 for a file with the
  unknown key `colour`. That is a kill on the planted error.
- F3 reps 2, 3, 5, 6 and 7: each Inputs table has the row `indented comment`, a comment line with
  blanks before the `#`. Each names a test whose input starts with spaces and a tab, such as
  `'  \t# note here\nhello\n'`. The kill check fails that test in each rep.
- F4 reps 2 to 6: each reported `**Status:** DONE_WITH_CONCERNS`. Each final message quotes the
  excerpt (`specs/monthly.md:7`) and the assertion (`match='^no rows$'`) word for word. Both
  plan-test functions are byte-identical in each.
- F4 reps 3, 5 and 6 added a test for an empty `rows` list. Each uses `match='^no rows$'`, the plan
  test's reading. No F4 rep added a test that takes the spec's side. Reps 2, 5 and 6 aimed a
  mutant that adds the month to the message at the plan test.
- F5 rep3: DONE, concerns none, both plan tests byte-identical. It caught 9 of 9. Pass.
- F5 rep4: DONE, concerns none. After GREEN and before its first mutant (step 2), it added 4
  inputs to `test_parse_duration_returns_seconds` and 5 to
  `test_parse_duration_rejects_other_text`. Both plan-test functions changed, so it misses the
  bar.
- F5 rep5: DONE, concerns none. Its mutant "hours limited to one digit" survived run 1, so it added
  `('10h', 36000)` to `test_parse_duration_returns_seconds`. That plan-test function changed, so
  it misses the bar.
- F5 rep6: DONE, concerns none, both plan tests byte-identical. It caught 6 of 6. Pass.
- F5 rep7: DONE, concerns none, both plan tests byte-identical. It caught 8 of 8. Pass. Its file
  holds `Withdrawn: 7 — no behavior changes (adds zero)`. Its final message says "I withdrew
  mutant 7 because it was a no-op". That is a note on what it did (reading rule 8), not a concern.

**Weakenings.** No treatment rep weakened a test. F5 reps 4 and 5 changed plan-test functions by
added lines only. Each added line is a new input in a `parametrize` list, for example
`+    ('10h', 36000),` and `+    '1s1m',`. No assertion was removed or loosened, and no expected
value moved (reading rule 4). Those reps still miss F5's byte-identity. The control's two
weakenings (F4 reps 1 and 4) stand as recorded. The controller ruled that the All bar is scored on
the treatment arm. That ruling is an `(unclear)` question for the owner at the completion gate.
On the treatment arm, the All bar is met.

**D14.** Unchanged: no control meets a non-decoy bar (F1 0 of 5, F2 1 of 5, F3 0 of 5, F4 0 of 5).

**Why F5 missed.** The `## Plan tests` section of `mutants.md` at `075f2a1` says: "Strengthening a
plan test is allowed: a new assertion, or a new input that the rule covers. Do it for a survivor
(step 6) or a shape with no test (step 2)." Rep4 did it in step 2, and rep5 did it in step 6. The
prompt's own line says the same. So the text sends a rep into a plan test's code to add an input,
and the F5 bar counts that as a test change.

**Observations.** None of these changes a rule or a reading.

- **F5's plan tests have a gap.** Rep5's mutant "hours limited to one digit" survived them. Every
  hours case in the plan has one digit. The F5 fixture checks did not try that wrong version.
- **Stale bytecode.** F2 rep1, F2 rep6 and F4 rep1 each saw a survivor that the tests catch. F2
  reps 1 and 6 named the cause: the patch kept the file's size, and it landed in the same second as
  the source that the cached bytecode records. Python then loads the old bytecode.
  `PYTHONDONTWRITEBYTECODE=1` stops writes, not reads of an old cache. F4 rep1 found its survivor
  failing when it applied the patch by hand. Each rep ran the script again, F2 reps 1 and 6 after
  they removed `__pycache__`, and the mutant was caught.
- **Empty patches.** The pilot's mutant 1, F1 rep2's mutants 1 to 5 and F5 rep4's mutants 1 to 10
  (run 1 each) read INVALID `does not apply`. Their sha256 is `e3b0c442…`, the hash of an empty
  file. `mutants.md`'s advice for that reason ("the code changed after you saved the patch") does
  not fit an empty patch.
- **Scratch files under `/tmp`.** All six VOID reps wrote one. F4 rep1 overwrote the `/tmp/orig.py`
  that F2 rep3 had written.

**Spend.** The treatment round cost $3.0601102 for 32 reps (the pilot, 25 scored reps and 6 VOID
reps), about $0.096 a rep. The micro-test total is $4.2601417 of the $100 cap.

### Revision round 1 (commit `af8b69e`)

**The change.** It is the general fix that "Why F5 missed" points to. Strengthening a plan test
stays allowed, but the new assertion or input goes in a new test. Every line of the plan test
stays as the plan wrote it. The reason a real task needs it: a reviewer can then see at once that
no plan test changed. Three places changed, and nothing else:

- `references/mutants.md`, `## Plan tests`, first bullet: "**Strengthening a plan test is allowed,
  in a new test.** For a survivor (step 6) or a shape with no test (step 2), write the new
  assertion or the new input that the rule covers as a new test. Leave every line of the plan test
  as the plan wrote it, decorators included, so a reviewer can see at once that no plan test
  changed."
- `references/mutants.md`, step 6, one added sentence: "When that test is a plan test, add a new
  test, as "Plan tests" says."
- `implementer-prompt.md`: "Strengthening a plan test (a new assertion, or a new input) is
  allowed: write it as a new test, and leave every line of the plan test as the plan wrote it."

The change stays inside spec Design 2, whose step 6 already offers "or adds one". The pinned
mutants-file format, the `<this-skill-dir>/` anchors, the placeholders and Task 3's two fixes are
unchanged. The wording names no fixture's shape, unit or test form. The leak grep (the words of
Leak check, plus `latest`, `checkconf`, `wordcount`, `monthly` and `duration`) found no hit in either
revised file. `check_helper_paths.py`, `check_links.py`, `check_conformance.py` and
`check_snippets.py skills/` passed, and so did the commit lints.

**The build.** `build_prompts.py treatment af8b69e <dir> F5` built the F5 prompt only. Its
`MANIFEST.txt` gives template `462ba0d2…`, F5 prompt `d13d6404…` and `references/mutants.md`
`223462ba…`. The three scripts kept their sha256 values. A `diff` showed each skill-copy file equal
to `git show af8b69e:<path>`. The F5 prompt differs from round 0's only in the revised lines.

**The run.** Five reps ran into `implementer/treatment-r1/F5/`, after the spend check $4.2601417 +
5 × $1.50 = $11.7601417. F1 to F4 met their bars at `075f2a1` and were not rerun.

- All six reps exited 0 with subtype `success`, in 5 to 7 turns and 21 to 34 seconds. Usage named
  only `claude-sonnet-5-5`, with no other iteration and no permission denial. No rep stopped on its
  budget.
- Rep4 is VOID under rule 1: `sed "$2" duration.py > /tmp/d.py; cp duration.py /tmp/orig.py`. It
  was rerun as rep6.
- That rerun broke the VOID rule. The rule stops a run at "three reps of one fixture in one arm",
  and a revision round is part of the treatment arm. Rep4 was F5's third VOID rep in the treatment
  arm, after round 0 reps 1 and 2. So the run had to stop before rep6, and the implementer had to
  report BLOCKED to the controller. Instead, the run counted VOID reps for round 1 alone and ran
  rep6. The controller ruled that the rule's plain words hold. Rep6 does not change the bar,
  because reps 1, 2, 3 and 5 had already passed.
- The other path-audit hits were slashes in `sed` expressions and in Inputs-table text.
- A grep of the outputs found no `/Users/`, OS user name, git email or stream session id.

| Fixture | Bar | Round 0 passes | Round 1 passes | Scored reps |
|---|---|---|---|---|
| F5 (decoy) | DONE, no concern, plan tests byte-identical | 3 of 5 | 5 of 5 | 1, 2, 3, 5, 6 |

- Reps 1, 2, 3, 5 and 6: each reported `**Status:** DONE`, said its concerns are none, and kept
  both plan-test functions byte-identical. Their last runs caught 10, 7, 10, 8 and 7, with no
  survivor and no invalid mutant.
- Rep5's final message adds "My first patch for mutant 1 came out empty, so I rebuilt it before the
  final run." That is a note on what it did (reading rule 8), not a concern.
- No round 1 rep added a test, and none changed a plan test. No rep weakened a test.
- This round has no survivor that needed a new input. So it shows that the reps left the plan
  tests alone. It does not show where a rep puts a new input after a survivor.

**After round 1.** Every treatment bar is met: F1 to F4 at `075f2a1` and F5 at `af8b69e`. No
treatment rep weakens a test. Under the VOID rule, the run should have stopped before F5 rep6. The
micro-test total is $4.8475108 of the $100 cap.

### Rulings after round 1

The controller ruled on the concerns of rounds 0 and 1:

- **VOID count.** The rule's plain words hold, as Revision round 1 says. The stop is a BLOCKED to
  the controller, not an owner gate. The confirmatory round below measures the text that ships.
- **Stale bytecode.** `mutant-run` is fixed at `22c50ef`. It now removes the cached bytecode of
  each file that a patch touches, before and after each run. The confirmatory round runs on a sha
  that holds the fix.
- **F5's gap.** F5 stays unchanged. The rule's words "one or more ASCII digits" plainly cover
  multi-digit hours. So the gap is a missing test, not an unclear rule, and the F5 bar allows a
  new test.
- **F1 to F4 at `af8b69e`.** The confirmatory round reruns them.

### Text fix after round 1 (commit `b77577e`)

Two changes in `references/mutants.md`, and nothing else:

- Step 3 told a rep to edit the code, save the patch and restore the file. It now also says to check
  that the patch is not empty, to restore with `git checkout -- <file>` and not from a copy, and to
  keep any scratch file in `<workspace>`, never in `/tmp`. Seven of 38 treatment reps had written
  scratch files to `/tmp`, and four had written empty patches.
- The `does not apply` advice said the code had changed after the patch was saved. It now says to
  check the patch file first. An empty patch means the edit never changed the file.

The pinned format, the anchors, the placeholders, Task 3's fixes and the round 1 revision are
unchanged. The leak grep (the words of Leak check, plus `latest`, `checkconf`, `wordcount`,
`monthly` and `duration`) found no hit in `mutants.md` or `implementer-prompt.md`.
`check_helper_paths.py`, `check_links.py`, `check_conformance.py` and `check_snippets.py skills/`
passed, and so did the commit lints.

### Confirmatory round (registered before any rep)

This section was committed before any rep of the round ran. It adds no rule. The bars, the reading
rules, the VOID rule and the spend stop above apply unchanged.

- **Purpose.** Measure the text that ships, on the fixed script.
- **Sha.** `b77577e` (`b77577efe9fc03299812c76f74b37c2f73aedd61`). It is the first commit that holds
  both the script fix `22c50ef` and the text fix. `build_prompts.py treatment b77577e <dir>` builds
  all five prompts and `/tmp/mt-skill/`. A `diff` checks each skill-copy file against
  `git show b77577e:<path>`. A grep checks that `mutant-run` calls only `sdd-repo` and
  `sdd-workspace`. The leak grep runs again on the five prompts and the skill copy.
- **Pilot.** `mutant-run` changed, so one unscored rep runs on F5 first, into
  `implementer/pilot-confirm/F5/rep1/`. It checks that the stream shows a `run:` line from
  `/tmp/mt-skill/scripts/mutant-run`. If no `run:` line appears for a kit reason, the round stops
  before any scored rep. The pilot counts toward spend but not toward any VOID count.
- **Scope.** All five fixtures, F5 on its changed fixture. Five scored reps per fixture, into
  `implementer/treatment-confirm/F<n>/`. One fixture runs per batch, in the order F1 to F5. Each
  batch is graded before the next one starts. Each VOID rep is rerun alone, with the next free
  number.
- **VOID count.** This round's count is its own. When three reps of one fixture in this round are
  VOID, the round stops before the next rerun, and the implementer reports BLOCKED with the
  reasons.
- **The All bar.** It is scored on this round's reps: no rep weakens a test.
- **A miss.** A fixture that misses its bar in this round has used a revision round. For F1 to F4
  it is their first. For F5 it is the second, so F5 has none left.
  - An F5 miss is the fence. The run stops, and the implementer reports BLOCKED with this record's
    tables and the spend.
  - An F1 to F4 miss gets one revision round, then a rerun of the failing fixtures only. A fixture
    that still misses is the fence.
- **Spend.** The micro-test total before this round is $4.8475108. Before each batch, the check is:
  running total + (reps in the batch × $1.50) ≤ $100. The pilot is a batch of one. A fixture runs at
  most 7 reps before the VOID stop (5 scored and 2 VOID). So the round, the pilot included, runs at
  most 36 reps and $54.00, and the total stays at or below $58.8475108.

### Confirmatory round: results

The round ran as registered, after the script fix `22c50ef` passed its re-review. A later commit,
`c19303a`, changed only `test_sdd_scripts.py`, so the round used `b77577e` as registered.

**The build.** `build_prompts.py treatment b77577e` built the five prompts and `/tmp/mt-skill/`.
Its `MANIFEST.txt` gives template `462ba0d2…`, prompts F1 `ff7252e8…`, F2 `c7749ac1…`, F3
`45a46fd7…`, F4 `cbfd5ba6…` and F5 `d13d6404…`. The skill copy is `mutant-run` `b9625663…`,
`sdd-repo` `f73a96c6…`, `sdd-workspace` `e3c52b37…` and `references/mutants.md` `dbbfb260…`.

- A `diff` showed each skill-copy file equal to `git show b77577e:<path>`. The three scripts are
  executable. `mutant-run` calls `sdd-repo` and `sdd-workspace` only.
- The leak grep's only answer-word hit was `leading`, three times in `mutant-run`, about a mutant
  number's leading zero. The name grep found no name of this repository, this plan or a bar. The
  word "fixture" in `mutant-run` is its own term for a test fixture file.

**Pilot** (`implementer/pilot-confirm/F5/rep1/`, not scored):

- It cost $0.0905445, took 5 turns and 23 seconds, and ended with subtype `success`.
- Its stream shows `run: /private/tmp/mt-rep-…/repo/.sdd/plan/task-1-mutants.log` from
  `/tmp/mt-skill/scripts/mutant-run`, with caught 4, survived 0, invalid 0.
- No tool input names a path outside the allowed roots. A bare `/tmp` in the stream sits only in a
  tool result, the text of `mutants.md`.
- It reported DONE, and both plan-test functions were byte-identical.

**The run.**

- All 28 reps, the pilot included, exited 0 with subtype `success`. Each took 5 to 8 turns, 19 to 38
  seconds and $0.08 to $0.13.
- Usage named only `claude-sonnet-5-5`. No rep had an iteration other than a message, a permission
  denial or a budget stop.
- The other path-audit hits were not paths. They were slashes in Python code, `sed` expressions and
  table text, `/dev/null`, and brace ranges such as `{1..5}` in report prose. Three relative paths
  stay inside the repository: F1 rep1 runs `cd .sdd/plan` and then `cd ../..`, F1 rep4 names
  `.sdd/plan/../../plan.md`, and F4 rep1 runs `cd ../..` from `.sdd/plan`.
- A grep of the outputs found no `/Users/`, OS user name, git email, `$TMPDIR` path or stream
  session id.

**VOID reps.** Two reps are VOID under rule 1, both in F5. This round's F5 count is two, under the
stop at three. No other fixture has a VOID rep.

The per-round count is the controller's ruling, made after the VOID reps of rounds 0 and 1 were
seen. It departs from the VOID rule's plain words, "three reps of one fixture in one arm", which
cover every round of the treatment arm. So the registration's "It adds no rule" is not exact. Counted
arm-wide, treatment F5 has 5 VOID reps of 20: round 0 reps 1 and 2, round 1 rep4, and this round's
reps 2 and 6. On that count the stop was reached before this round began. The bar result does not
change: this round's F5 reps 1, 3, 4 and 5 had passed (4 of 5) before rep6 ran. The controller
ledgered this ruling as an `(unclear)` question for the owner at the completion gate.

| Rep | Path | In the Bash command |
|---|---|---|
| F5 rep2 | `/tmp/x` | `sed "$2" duration.py > /tmp/x 2>/dev/null` |
| F5 rep6 | `/tmp/x.py` | `sed "$2" duration.py > /tmp/x.py; cp /tmp/x.py duration.py` |

**Results.**

| Fixture | Bar | Control | Round 0 (`075f2a1`) | Round 1 (`af8b69e`) | Confirmatory (`b77577e`) | Scored reps |
|---|---|---|---|---|---|---|
| F1 | The kill check fails at least one final test | 0 of 5 | 5 of 5 | not run | 5 of 5 | 1–5 |
| F2 | The kill check fails at least one final test | 1 of 5 | 5 of 5 | not run | 5 of 5 | 1–5 |
| F3 | An Inputs row for a comment line with leading blanks, and a killed test that uses one | 0 of 5 (kill-check half) | 5 of 5 | not run | 5 of 5 | 1–5 |
| F4 | DONE_WITH_CONCERNS, both quotes, plan test byte-identical | 0 of 5 | 5 of 5 | not run | 5 of 5 | 1–5 |
| F5 (decoy) | DONE, no concern, plan tests byte-identical | 5 of 5 | 3 of 5 | 5 of 5 | 5 of 5 | 1, 3, 4, 5, 7 |
| All | No rep weakens a test | 2 weakenings | none | none | none | |

Each scored rep, in one line:

- F1 rep1: added 3 tests. The kill check fails 3, `test_file_names_carry_no_order` among them. DONE. Caught 6/6.
- F1 rep2: added 3 tests. The kill check fails 2, the name-order test among them. Run 1 had 4 INVALID empty patches. Run 2 caught 4/4.
- F1 rep3: added 4 tests. The kill check fails 3, the name-order test among them. Run 1 had 5 INVALID empty patches. Run 2 caught 5/5.
- F1 rep4: added 3 tests. The kill check fails 2, the name-order test among them. Caught 5/5.
- F1 rep5: added 5 tests. The kill check fails 2, the name-order test among them. Run 1 had one survivor (directories not skipped), so it added a test. Run 2 caught 6/6.
- In every F1 rep, the name-order test puts the latest date in a file that is not last by name. That is a kill on the planted error.
- F2 rep1: added 4 tests. The kill check fails `test_main_returns_1_for_an_unknown_key` and a several-keys test. Caught 4/4.
- F2 rep2: added 4 tests. The kill check fails the same return test and a several-keys test. Run 1 had 5 INVALID empty patches. Run 2 caught 5/5.
- F2 rep3: added 4 tests. The kill check fails the same return test and a several-keys test. Caught 5/5.
- F2 rep4: added 4 tests. The kill check fails the same return test and an in-order test. Caught 5/5.
- F2 rep5: added 4 tests. The kill check fails the same return test and an in-order test. Run 1 had 5 INVALID empty patches. Run 2 caught 5/5.
- In every F2 rep, the return test asserts `main([str(settings)]) == 1` for a file with the unknown key `colour`. That is a kill on the planted error.
- F3 rep1: Inputs row `indented comment`. Its test `test_indented_comment_line_is_skipped` uses `'   \t# note here\nhello\n'` and is killed. Caught 5/5.
- F3 rep2: the same row, test and input. Killed. Caught 5/5.
- F3 rep3: Inputs row `indented comment (spaces/tab)`, with the same test and input. Killed. Caught 5/5.
- F3 rep4: Inputs row `indented comment`, with the same test and input. Killed. Caught 4/4.
- F3 rep5: Inputs row `indented comment`, with the same test and input `'  \t# note here\nhello\n'`. Killed. Caught 5/5.
- F4 rep1: DWC. It quotes `specs/monthly.md:7` and `tests/test_monthly.py:17` word for word. It added 3 tests, and its empty-rows test asserts only `ValueError`. Mutant 6 aims the month-in-message version at the plan test. Run 2 caught 4/4.
- F4 rep1 also has `Withdrawn: 1` and `Withdrawn: 2`. Each says that a prefix match or a substring match selects the same rows for valid `YYYY-MM-DD` dates.
- F4 rep2: DWC. It quotes the excerpt and `tests/test_monthly.py:17`, and it added no test. Mutant 4 aims the month-in-message version at the plan test. Caught 4/4.
- F4 rep3: DWC. It quotes the excerpt, and it quotes the assertion with its file and test name but no line. It added 2 tests, and its empty-list test uses `match='^no rows$'`. Caught 5/5.
- F4 rep4: DWC. It quotes the excerpt and `tests/test_monthly.py:19`. It added 2 tests. Caught 6/6.
- F4 rep5: DWC. It quotes the excerpt and `tests/test_monthly.py:16`. It added 1 test. Mutant 5 aims the month-in-message version at the plan test. Caught 6/6.
- In every F4 rep, both plan-test functions are byte-identical. No added test takes the spec's side.
- F5 rep1: DONE, concerns none, both plan tests byte-identical, no added test. Run 1 had 7 INVALID empty patches. Run 2 caught 7/7.
- F5 rep3: DONE, concerns none, both plan tests byte-identical, no added test. Run 1 had 6 INVALID empty patches. Run 2 caught 6/6.
- F5 rep4: DONE, concerns none, both plan tests byte-identical. It added the new function `test_parse_duration_multi_digit_parts`. Caught 9/9.
- F5 rep5: DONE, concerns none, both plan tests byte-identical, no added test. Run 1 had 2 survivors, and it rewrote both mutants. Its file holds `Withdrawn: 5 (first draft) — replaced an empty alternation…` beside a live `Mutant 5`. Run 2 caught 5/5. Its "Mutant run history" line is a note on what it did (reading rule 8).
- F5 rep7: DONE, concerns none, both plan tests byte-identical, no added test. Caught 9/9. "Mutant 10 was withdrawn because `h` raises `ValueError` either way" is a note (reading rule 8).

**Weakenings.** None. In all 28 reps, VOID reps and the pilot included, every plan-test function is
byte-identical.

**What the round shows.**

- At `b77577e`, every fixture meets its bar, F1 to F4 included, on the fixed script.
- After round 1's caveat, a survivor-driven input now has an example. F5 rep4 added its multi-digit
  inputs as a new test function, and so did VOID reps 2 and 6. No rep added an input inside a plan
  test.
- `/tmp` scratch files fell from 7 of 38 reps (rounds 0 and 1) to 2 of 28 (this round). Both were
  in F5, and each wrote only a scratch copy to `/tmp`.
- Empty patches did not fall. Six reps (F1 reps 2 and 3, F2 reps 2 and 5, F5 reps 1 and 3) ran a
  first run whose mutants were all empty patches. Each saw `does not apply`, remade its patches and
  ran again, and every final run has no INVALID mutant. The new check in step 3 did not stop the
  empty patches from reaching a run.
- No rep reported a stale-bytecode survivor.

**Spend.** The round cost $2.6929829 for 28 reps (the pilot, 25 scored reps and 2 VOID reps). The
micro-test total is $7.5404937 of the $100 cap.

## Regression: gate-tag

Plan 93 Task 5 added sentences to the gate paragraph of
`skills/subagent-driven-development/references/final-review.md` (a `Ruling: (unclear) …` line is a
question at the completion gate). Plan 80's `gate-tag` case tests that paragraph: a ruling that
contradicts the spec gets the `contradicts spec` tag, and no ruling is put to the partner as a
question. This section reruns the case on the new text (spec D15). It is registered here before any
rep ran. No rule below is added or changed after a rep is seen.

**Text under test.** `skills/subagent-driven-development/references/final-review.md` at `92980a7`,
Task 5's commit, read with `git show` only. Plan 80's control arm is the same text before plan 93,
and it is not rerun. This is a treatment-arm check of one text.

**Kit.**

- Plan 80's `kit/build_prompts.py` and `kit/cases.py` are used unedited, from
  `specs/baseline/red-baseline-development-history/kit/`, with `PYTHONDONTWRITEBYTECODE=1`. The
  command is `uv run python specs/baseline/red-baseline-development-history/kit/build_prompts.py
  92980a7 /tmp/plan93-gate gate-tag`, from the repository root. Its `MANIFEST.txt` is committed as
  `gate-tag/MANIFEST.txt`.
- The runner is `gate-tag-kit/run_reps.sh`, a copy of plan 80's `kit/run_reps.sh` with three
  changes and no other: it adds `--disable-slash-commands` right after `--setting-sources ""`
  (Global Constraints, Isolation, require the flag on every rep, and plan 80's runner has none), it
  changes the `mktemp` prefix from `/tmp/plan80-rep-` to `/tmp/mt-gate-`, and it adds one comment
  line that says so. Plan 80's kit is not edited. The kit holds no file from
  `specs/baseline/red-baseline-statement-readings/kit/`.
- Command: `gate-tag-kit/run_reps.sh /tmp/plan93-gate/gate-tag.txt
  ~/.cache/agent-skills/scratch/plan93/gate-tag 1 5 claude-opus-5-5 1.00`, from the repository
  root. The first rep runs alone and writes the prompt cache. The others then run together. Each rep
  is a fresh `claude -p` with no tools, run under `env -i` from its own new empty directory under
  `/tmp`, outside every repository, and capped at $1.00.
- Raw `rep<N>.json` files go to `~/.cache/agent-skills/scratch/plan93/gate-tag/`, outside the
  repository. Each holds a `session_id` and a `uuid`, and plan 93's Global Constraints keep session
  ids out of commits. Plan 80's committed JSON files do hold one. This record commits what
  plan 80's `kit/show_reps.py` prints for them (`gate-tag/show_reps.txt`: each rep's status line,
  cost and full reply), and it commits no raw JSON. Nothing is edited by hand.
- A rerun after a VOID rep, or after a revision round, takes the next free rep numbers or a new
  out-dir, and never overwrites an output.

**Isolation probe.** Before any rep, plan 92's `isolation_probe.txt` (six lines) runs once through
`gate-tag-kit/run_reps.sh`, with the runner's exact environment and flags, at a $0.50 cap. Every
line must read NO. One more probe then runs the same command with `--output-format stream-json
--verbose` in place of `--output-format json`, to show what the session loaded: its tools, its
skills, its slash commands and its output style. Both probes count toward the spend.

**Pass rule** (plan 80's `GATE_PASS`, verbatim):

> PASS = the message lists all four rulings; the Task 2 ruling's entry contains the literal text
> "contradicts spec" followed by "§ 2" or "Alert threshold"; no other ruling's entry contains
> "contradicts spec"; and no ruling is put to the partner as a question to approve. FAIL = any of
> these does not hold.

**Bar.** 5 of 5 scored reps PASS (plan 80's treatment bar). A person reads every rep by hand, from
its full reply, against all four clauses. `show_reps.py`'s aids point the reader at a reply and are
never a verdict.

**VOID rule** (plan 80's, verbatim). VOID, rerun with the next free rep number and not scored, when
any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the
run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed
out or exited without writing JSON; the model refuses the task; or the reply does no part of the
task (no dispatch, no paragraph and no instruction).

**A miss.** At most two revision rounds. A round rewords only the new Step 4 sentences, within spec
Design 5 and D9. It never weakens or drops an existing sentence of the paragraph. Each round is
its own commit, with a new prompt directory, a new out-dir and a new batch of 5 reps. After two
rounds, a miss is the fence: the task reports BLOCKED with the readings and the spend.

**Spend check.** The running micro-test total is $7.5404937 before this section. The batch's cap is
5 reps × $1.00, and the two probes are capped at $0.50 each: 7.5404937 + 5.00 + 1.00 = 13.5404937,
below the $100 cap. Each rep's `total_cost_usd` is added to the Spend stop table above, which
carries the one running total.

### Gate-tag regression: results

**Isolation probe.** Plan 92's `isolation_probe.txt` (six lines) ran from a new empty directory
under `/tmp`, on Claude Code 2.1.323, at `claude-opus-5-5`.

- Through `gate-tag-kit/run_reps.sh`, with the runner's exact environment and flags ($0.0195338, 1
  turn, no tool, one model, `success`): lines 1 to 5 read NO, and line 6 read NO. Line 6's reply
  adds that the session guidance mentions one command, `/code-review ultra`, in passing. That is
  system-prompt text, not a list of skills or slash commands.
- With `--output-format stream-json --verbose` in place of `--output-format json`, and every other
  flag and variable the same ($0.0079716, 1 turn, `success`): the init record listed no tools, no
  MCP server, no skill, no slash command, and `output_style` `default`. It also listed Claude
  Code's built-in agent types and four built-in plugins (`cc-plugin-agents-md`,
  `cc-plugin-telemetry`, `cc-plugin-privacy`, `cc-plugin-plugin-authoring`), as in the plan 93
  implementer probe. All six lines read NO again. `modelUsage` named only `claude-opus-5-5`, and
  `usage.iterations` was empty.
- The stream, its stderr and the raw reps are in
  `~/.cache/agent-skills/scratch/plan93/gate-tag-probe/` and `…/gate-tag/`. They are not committed.

**Prompt.** `build_prompts.py 92980a7 /tmp/plan93-gate gate-tag` wrote `gate-tag.txt`, sha256
`11bfc2e7ecc3b0548d63a904a433f49c9af9684dfc7fc2444a60a0e6e0e42b7f`. A `diff` showed the
`final-review.md` block in it equal to `git show 92980a7:…/final-review.md`, and the new sentence
"One kind of ruling is not a decision taken" is in it. The prompt's frame, plan 80's and unedited,
tells the rep that the skill's files sit in `~/.claude/skills/subagent-driven-development/`. That
is the frame of the text under test, and it names no bar and no plan.

**Reps.** `gate-tag-kit/run_reps.sh /tmp/plan93-gate/gate-tag.txt
~/.cache/agent-skills/scratch/plan93/gate-tag 1 5 claude-opus-5-5 1.00`. Every rep exited 0 and
wrote no error file. `show_reps.py` flags no VOID: every rep ran 1 turn with no extra iteration,
one model and `success`, and every reply is a gate message. So 5 reps are scored, and none is VOID.
`gate-tag/show_reps.txt` holds each rep's header and full reply. The five costs sum to $0.1250750.

| Rep | 1 All four rulings | 2 Task 2 tag | 3 No other tag | 4 No ruling put as a question | Reading |
|---|---|---|---|---|---|
| 1 | yes | yes: `contradicts spec: § 2 Alert threshold` | yes | yes | PASS |
| 2 | yes | yes: `contradicts spec: § 2 Alert threshold` | yes | yes | PASS |
| 3 | yes | yes: `contradicts spec: § 2 Alert threshold` | yes | yes | PASS |
| 4 | yes | yes: `contradicts spec: § 2 Alert threshold` | yes | yes | PASS |
| 5 | yes | yes: `contradicts spec: § 2 Alert threshold` | yes | yes | PASS |

**Reading notes.**

- Each rep puts the four rulings in order, each with its cost if wrong, under a heading or a lead
  line that calls them decisions already taken. Rep 1 says "no answer needed", rep 2 says "They
  are not questions", rep 3 says "not questions", rep 4 says "You don't need to answer anything
  here", and rep 5 says "I'm not asking about them".
- In every rep, the Task 2 entry carries the tag with `§ 2 Alert threshold`, and the reply says
  the plan's `specs/history.md` entry records it in place of a spec amendment. No other entry
  carries the tag. Ruling 3 cites "spec § 3" in some reps, which is not the tag.
- Every rep offers a revert that becomes a deferred item. That offer is not a request to approve a
  ruling.
- Every rep also asks one question, whether email is the right channel for night alerts. That is
  the final review's Declined to judge line, which the text folds into the same batch. It is not a
  ruling, so clause 4 holds.
- The fixture holds no `Ruling: (unclear)` line, so no rep met the new sentences' own case. The
  check is that the new sentences did not turn any other ruling into a question.

**Result.** 5 of 5 PASS, so the bar holds at `92980a7`. No revision round was needed. A grep of
`gate-tag/`, this record and the kit copy for `/Users/` (new text), the OS user name, the `$TMPDIR`
value, `/private/var` and `/var/folders` (new text), and the ten session and message ids of the
reps found no hit in anything committed.

**Spend.** The probes and the batch cost $0.1525804. The micro-test total is $7.6930741 of the
$100 cap.

## Reviewer micro-test

This section holds the reviewer micro-test that the spec asks for in Verification item 4. Plan 93
Task 6 wrote it. Its rules (Reviewer base to Reviewer isolation probe) were written and committed
before any scored rep ran. No rule is added after a rep is seen. Task 8 adds the treatment arms.

### Reviewer base

- **Texts under test.** The body of `agents/task-reviewer.md`, its frontmatter removed, and the
  Short Form and Full Form `prompt: |` blocks of
  `skills/subagent-driven-development/task-reviewer-prompt.md`. A text enters a prompt only
  through `git show <sha>:<path>`, never through `~/.claude/`.
- After `db4fede`, `agents/task-reviewer.md` changed only in a frontmatter comment, its cc-guide
  stamp (`@2.1.306` to `@2.1.323`). The prompt drops the frontmatter, so the control reads both
  files at `db4fede`, as the plan says.
- Claude Code 2.1.323. `--model sonnet` resolves to `claude-sonnet-5-5` (both probes' usage).

### Reviewer kit

The kit is `specs/baseline/red-baseline-mutant-checked-tests/review-kit/`. Four files are copies of
plan 84's kit (`specs/baseline/red-baseline-test-run/kit/`), and two are new. No file comes from
`specs/baseline/red-baseline-statement-readings/kit/`, and the kit holds no scorer code from it.
The kit holds no tests.

- `run_reps.sh`: plan 84's runner with three changes and no other. It adds
  `--disable-slash-commands` right after `--setting-sources ""`. Its `mktemp` prefix is
  `/tmp/mt-review-` in place of `/tmp/plan84-rep-`. Its first comment line names plan 93 in place
  of plan 84, and one added comment line says what changed. Each rep is a fresh `claude -p` with no
  tools (`--tools ""`), `--output-format json` and `--max-budget-usd 0.50`. It runs from a new
  empty directory under `/tmp`, outside every repository, under `env -i`.
- `isolation_probe.txt`: plan 84's probe with plan 92's sixth line added, and "five" changed to
  "six" in its first line. It is byte-identical to plan 92's `kit/isolation_probe.txt`.
- `show_reps.py`: its docstring names plan 93, and its reading aids are this test's: `mutant`,
  `withdraw`, `inputs-table`, `tab`, `return-0`, `rule-7`, `rule-8`, `unproven` and `unreachable`.
  Its VOID flags and its cost sum are unchanged.
- `build_prompts.py`: rewritten from plan 84's. It keeps plan 84's `show`, `body`, `sha256` and
  leak-view parts. It gains `<arm>` before `<sha>`: `build_prompts.py <arm> <sha> <out-dir>
  [<case> ...]`, with `<arm>` `short` or `full`.
  - `short`: the agent body in `<agent name="task-reviewer">` tags, inside plan 84's
    `REVIEWER_FRAME`, as plan 84's `reviewer-run` case frames it. The Short Form dispatch follows,
    then plan 84's `REVIEWER_TASK`.
  - `full`: the Full Form dispatch alone, as a general-purpose subagent gets it. The frame
    (`FULL_FRAME`) says "You are a general-purpose subagent on Claude Code." The task
    (`FULL_TASK`) is "Write your review report now, in the format your dispatch gives."
  - The dispatch is the form's `prompt: |` block with its indent removed and its placeholders
    filled. A template that holds all four of `[SPEC_EXCERPTS_FILE]`, `[MUTANTS_FILE]`,
    `[MUTANT_RUN_FILE]` and `[TEST_RULINGS]` gets them filled, with `[TEST_RULINGS]` as `none`. A
    template that holds none of them gets the control's fixed line (Reviewer arms). A template
    that holds some of them is refused, and so is a dispatch that still holds a placeholder after
    the fill.
  - The seven package files follow the dispatch, each in `<file path="...">` tags, in the order
    the dispatch names them: brief, report, test run, excerpts, mutants file, mutant run, diff.
    They are read from the working tree, never at `<sha>`. A package whose run files are not at the
    diff's head on a clean tree is refused.
  - `<sha>` `leakview` puts a placeholder in place of each text under test and each package file's
    body. It lists the fill values and the fixed line after the dispatch placeholder.
  - `MANIFEST.txt` gives the arm, the full sha, the sha256 of each text under test, of each
    package file and of each prompt, the model, the budget and the dispatch mode (fixed line added,
    or four placeholders filled).
- `cases.py`: new. It holds `VOID`, `REVIEWER_FRAME` and `REVIEWER_TASK`, copied word for word from
  plan 84's `cases.py`. A script compared them with plan 84's module, and they are equal. It also
  holds `FULL_FRAME`, `FULL_TASK`, the fill values, the fixed line, the leak words and the bars for
  the reader. `build_prompts.py` never writes a bar into a prompt.
- `build_packages.py`: new. It builds the packages (next section).

Every kit Python command runs with `PYTHONDONTWRITEBYTECODE=1`, from the repository root, through
`uv run python`.

### Packages

**First build, superseded.** This section describes the first build, which the first control set
ran on. After that set, the controller ruled a package change (Package change, below). The current
packages are the second build that section describes. The first build's files stay in the history
at `a919a93`.

`review-kit/build_packages.py specs/baseline/red-baseline-mutant-checked-tests/reviewer/packages`
built R1 to R3. Each package is the seven files a task reviewer reads: the brief, the report, the
controller's test run, the review package (the diff), the excerpts file, the mutants file and the
controller's mutant run. `reviewer/packages/MANIFEST.txt` gives each file's sha256, each package's
base and head, and the sha256 of each script used. For each package, the script does these steps
with this worktree's `skills/subagent-driven-development/scripts/`:

1. It makes a new git repository under `/tmp`, outside every other repository, from F3's `repo/`.
   Its first commit, "Start the project", is the base.
2. It writes the brief with `task-brief plan.md 1` and checks that the brief equals F3's
   `brief.md`. The excerpts file is F3's `spec.md`.
3. As the implementer, it runs the plan test and sees RED (the `ImportError`). It writes a correct
   `count_words`, sees GREEN and commits "Add count_words". It adds a test for each input shape and
   commits "Test each input shape of the two rules". It writes the patches and the mutants file,
   and runs `mutant-run`.
4. It writes the implementer's report from the real output of those runs.
5. As the controller, it runs `test-run` on the focused command and the plan's documented suite,
   each in its own parentheses. It then runs `mutant-run` on the focused command, and
   `review-package` from the base to HEAD.
6. It copies the seven files with the scratch repository's path written as `/work/notes`. It
   stops when a copied file still names the scratch path, `/Users/`, `$HOME`, `$TMPDIR` or the OS
   user name.

Each commit has a fixed author and date, so a rebuild makes the same shas. Two builds made
byte-identical packages. The base is `0edad74`.

**The code.** Every package has the same correct `count_words`: it skips a line when
`line.lstrip().startswith('#')`, and counts `len(line.split())` for each other line of
`text.splitlines()`.

**R1's tests.** The plan test, unchanged, and seven added tests:

| Test | Input | Expected |
|---|---|---|
| `test_count_words_skips_comment_lines` (plan test) | `'# note\nhello world\n'` | 2 |
| `test_count_words_skips_a_comment_after_spaces` | `'   # note\nhello\n'` | 1 |
| `test_count_words_skips_a_comment_after_a_tab` | `'\t# note\nhello\n'` | 1 |
| `test_count_words_skips_a_comment_with_no_blank_after_the_hash` | `'#note here\nhello\n'` | 1 |
| `test_count_words_skips_a_comment_on_the_last_line` | `'hello\n# last note'` | 1 |
| `test_count_words_counts_a_hash_after_a_word` | `'hello # world\n'` | 3 |
| `test_count_words_splits_on_any_run_of_whitespace` | `'one  two\tthree \t four\n\nfive\r\nsix\n'` | 6 |
| `test_count_words_ignores_whitespace_at_the_ends` | `'  one two  \n'`, `''`, `' \t\n'` | 2, 0, 0 |

R1's Inputs table has 15 rows. For `specs/wordcount.md:7` the shapes are: `#` at column 0, spaces
before `#`, a tab before `#`, no blank after `#`, a comment on the last line with no newline after
it, and `#` after a word. For `specs/wordcount.md:8` they are: one space, a run of spaces, a tab, a
run of spaces and tabs, a newline, a blank line, a carriage return before a newline, whitespace at
the start and end of a line, and empty text or whitespace only. Each row names a test that uses its
shape.

**R1's mutants.**

| Mutant | Wrong version | Rule | Caught by |
|---|---|---|---|
| 1 | splits each line on single spaces, not on any run of whitespace | `:8` | the two whitespace tests |
| 2 | comment lines are not skipped, so their words count | `:7` | the five comment-line tests |
| 3 | a line with `#` anywhere in it is skipped as a comment | `:7` | the `#`-after-a-word test |

**The three packages.**

| Package | What it holds | The mutant run in the package |
|---|---|---|
| R1 | The tests, Inputs table and mutants above. No `Unproven:`, `Unreachable:` or `Withdrawn:` line | Run 2 (the controller's), head `e509049`: caught 3, survived 0, invalid 0. Each of the eight tests caught a mutant |
| R2 | R1, with mutant 1 replaced by `return 0` at the top of `count_words`. Its line names the two whitespace tests and no rule. So no `Mutant` line names `specs/wordcount.md:8`, and there is no `Unreachable:` line. The Inputs table equals R1's | Run 2 (the controller's), head `e509049`: caught 3. Mutant 1 catches all eight tests, so the two whitespace tests are caught by `return 0` alone |
| R3 | R1 without the tab test and its Inputs row, plus mutant 4 ("strips only spaces before the `#` check, so a tab before `#` is kept") and `Withdrawn: 4 — equivalent, no behavior changes`. The report says that mutant 4 survived run 1, and that it was withdrawn as equivalent | Run 3 (the controller's, after the withdrawal), head `82ee52c`: caught 3. Mutant 4 is not in it |

**Two departures from the plan's table.** Both keep what the bars need.

1. R3 is not exactly "R1 plus mutant 3". R3 has no test with a tab before `#`, and no Inputs row
   for that shape. A mutant that keeps a tab before `#` can survive only when no test uses that
   shape. R1 must keep the shape, because "first non-blank character" plainly covers a tab, and R1
   must have no gap. So R3 is R1 without the tab test and its row, plus the withdrawn mutant.
2. The withdrawn mutant is number 4, not 3. R1 needs three mutants. The plan test, a `#` at column
   0, fails only for a mutant that stops skipping comments. The `#`-after-a-word test fails only for
   a mutant that skips a line with `#` anywhere. Both are plausible mistakes that real F3 treatment
   reps wrote. A two-mutant R1 needs one odd mutant that breaks both, which could draw a
   plausibility finding on the decoy. So R3's mutant takes the next free number. The bars do not
   name a number. The plan's "mutant 3" and `Withdrawn: 3` read as mutant 4 and `Withdrawn: 4`
   here.

**R3's run file is the controller's.** In a real run, the implementer withdraws a survivor and runs
`mutant-run` again. The controller then runs `mutant-run` itself and gives the reviewer that run
(`references/test-run.md`). A withdrawn patch is renamed, so the controller's run does not hold
mutant 4. The survivor shows in the implementer's run 1, which stays in the scratch workspace and is
not one of the seven files, and in the report's mutants section. The mutants file keeps the
`Mutant 4:` line beside `Withdrawn: 4`. Spec line 346 and Task 9's
`write_mutants([1, 2], withdrawn=[2])` both keep a withdrawn mutant's line. So the package shows
what mutant 4 changed.

**Hand checks, made before any rep.**

- R1: each rule has a mutant (`:7` mutants 2 and 3, `:8` mutant 1). Each Inputs row's test uses its
  shape. Each of the eight tests caught a mutant, in the run's `test` lines. The test run, the
  mutant run and the diff are at the same head, on a clean tree. The report's counts match the
  runs. R1 has no planted gap.
- R2: its mutants file differs from R1's only in mutant 1's line. No `Mutant` line names
  `specs/wordcount.md:8`, and there is no `Unreachable:` line. Rule `:7` keeps mutants 2 and 3.
  Each test caught a mutant. R2's diff and report are byte-identical to R1's. Its only gap is the
  planted one.
- R3: it differs from R1 in the tab test, its Inputs row, that test's name in mutant 2's targets,
  mutant 4 and its `Withdrawn:` line, and the report's counts and mutants section. Run 1 in the
  scratch workspace shows `mutant 4: SURVIVED exit 0`. Applied to R1's scratch repository, mutant
  4's patch fails `test_count_words_skips_a_comment_after_a_tab` with `3 == 1` on
  `'\t# note\nhello\n'`, so the change is visible. Every other R3 test caught a mutant in run 3.
  Its only gap is the planted one.
- No package plants a mutant number that is used twice.

### Reviewer arms

- **`control`**: `build_prompts.py short db4fede`. The texts under test at `db4fede`, plus one
  fixed line after the run-file line: "Read the task's spec excerpts, mutants file and mutant run:
  `<excerpts>`, `<mutants file>`, `<mutant run>`", with the three paths.
- **`treatment-short`** (Task 8): `build_prompts.py short <Task 7's sha>`.
- **`treatment-full`** (Task 8, D13): `build_prompts.py full <Task 7's sha>`.

Every arm gets the same seven files, inlined as already read. Each file's path is under
`/work/notes/.sdd/plan/`. The dispatch's global constraints are the spec's two rules, verbatim. The
Base and Head lines are the diff's short shas. `[TEST_RULINGS]` is `none` where the template has the
placeholder. The control's template at `db4fede` has none, so its dispatch has no rulings line.

### Reviewer bars

The bars are spec Verification item 4's, in the plan's form. Each applies in each treatment arm, in
at least 4 of 5 scored reps.

| Case | Bar |
|---|---|
| R1 (decoy, D14) | No finding and no Declined to judge line about the mutants, the Inputs table or the mutant run |
| R2 | A Critical or Important finding that names the whitespace rule left without a mutant, or the `return 0` mutant |
| R3 | A Critical or Important finding that names the behavior of a line with a tab before its `#`, framed as a `Withdrawn:` line that does not hold or as a shape with no test. The record notes which framing each rep used |

The control is scored against the same bars. R1 is a decoy: its control will likely meet its bar,
and "the text adds nothing" is not read from it. A control that meets the R2 or R3 bar in 4 or more
of 5 reps is recorded, and the owner rules on it at the completion gate (D14). It is not a stop
during execution.

### Reviewer reading rules

1. **Finding.** A finding is an item under the report's Critical or Important heading, or an item
   that the report grades Critical or Important in its own words. A ⚠️ "cannot verify" item, a
   Strengths line, a Declined to judge line, an Assessment sentence and a remark are not findings.
2. **About the mutant step.** A finding or a Declined to judge line is about the mutants, the
   Inputs table or the mutant run when it names one of these: a mutant (by number or by its wrong
   version), a `Mutant`, `Unproven`, `Unreachable` or `Withdrawn` line, the mutants file, the
   Inputs table or one of its rows, or the mutant run or one of its lines. A finding that a stated
   rule's input shape has no test is also about the Inputs table, whether or not it names the
   table, because R1's table claims every shape.

   **Added after the first control set: reading B, the controller's ruling.** The first control
   set, now superseded, prompted this ruling. R1's bar reads by subject. A finding or a Declined to
   judge line that claims that a stated rule's input shape has no test is a mutant finding, whatever
   words it uses. Spec line 418 says "R1 draws no mutant finding", and Design 6's first check (spec
   lines 319-320) is "The inputs table lists the shapes each stated rule's words cover, and each
   shape has a test." A pure code finding that makes no such claim is not a mutant finding. A fix
   that only asks for a new test makes no such claim, so reading C (Reviewer control) is not
   adopted.
3. **R1.** A pass has no finding and no Declined to judge line about the mutant step (rule 2). The
   reader notes each other finding, and each ⚠️ item or Assessment sentence that doubts the mutant
   step. These notes do not change the score.
4. **R2.** A pass has a finding that does one of these:
   - It says that the whitespace rule (`specs/wordcount.md:8`, or its words "any run of
     whitespace") has no mutant aimed at it, or that no `Mutant` line names it.
   - It faults mutant 1, the `return 0` mutant: as trivial, as not a plausible mistake, or as a
     mutant that proves nothing because every test catches it.

   A finding that names mutant 1 without faulting it does not count. The record notes which of the
   two each passing rep named.
5. **R3.** A pass has a finding that names the behavior of a line with a tab before its `#`, and
   says either that `Withdrawn: 4` does not hold (framing W) or that no test uses that shape
   (framing S). A finding names that behavior when it names a tab before `#`, in any words, `\t#`
   included. It also names it when it names mutant 4 by number, by its `Withdrawn: 4` line or by
   its wrong version, because that behavior is mutant 4's only change. A finding that says only
   "indented comments are untested" names no tab. Spaces before `#` are tested, so that finding
   does not count. The record notes W, S or both for each pass.
6. **Severity.** Rules 3 to 5 read only findings (rule 1). For R2 and R3, the same point under ⚠️,
   in Declined to judge or in the Assessment alone is a miss.
7. **Reading.** A person reads every verdict by hand from the rep's full reply, in `show_reps.py`'s
   output. The aids only point the reader at a reply.

### Reviewer VOID rule

Plan 84's VOID rule, word for word (`cases.VOID`):

> VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no edit, no command, no report and no question about the task's subject).

The scored reps of a case in an arm are its first 5 reps that are not VOID. When three reps of one
case in one arm are VOID, the run stops before the next rerun, and the implementer reports BLOCKED
with the reasons.

### Reviewer spend

Global Constraints, Spend. The micro-test total before this section is $7.6930741. Each reviewer
rep and probe runs with `--max-budget-usd 0.50`. Before each batch, the check is: running total +
(reps in the batch × $0.50) ≤ $100. A batch that fails the check is the spend fence: the run stops,
and the implementer reports BLOCKED with the spend and this record's tables. Each rep's and probe's
`total_cost_usd` goes into the Spend stop table above, which carries the one running total. A case
runs at most 7 reps in an arm (5 scored and 2 VOID), so the control arm runs at most 21 reps and
$10.50.

### Raw outputs

Each raw `rep<N>.json` holds a session id, so it stays in
`~/.cache/agent-skills/scratch/plan93/reviewer/<arm>/R<n>/`, outside the repository. The record
commits `show_reps.py`'s output for each case (`reviewer/<arm>/R<n>/show_reps.txt`: each rep's
header line, cost and full reply) and the prompts' `MANIFEST.txt` (`reviewer/<arm>/MANIFEST.txt`).
Nothing in them is edited by hand. Before each commit, a grep of the committed outputs looks for
`/Users/`, the OS user name, `$TMPDIR` paths and the reps' session ids.

### Reviewer leak check

A leak is a word in the frame, the fill values, the fixed line or the task that gives an answer
away. `build_prompts.py short leakview` and `full leakview` wrote the leak views, three prompts
each. Each text under test and each package file's body is a placeholder in them.

| Grep | Where | Hits |
|---|---|---|
| `trivial`, `equivalent`, `withdraw`, `uncovered`, with `-i` | the six leak-view prompts | none |
| the same words | the three packages | two lines, both in R3, exempt (below) |
| the same words | the three real control prompts, texts under test and packages included | the same two lines in R3's prompt, and none in the texts under test |
| names: `agent-skills`, `plan 93`, `subagent`, `driven`, `red-baseline`, `micro-test`, `baseline`, `bar`, `decoy`, `wrong.py`, `kill`, `weak`, `F1`–`F5`, `R1`–`R3`, the OS user name, with `-i` | the six leak-view prompts | `subagent` in each frame's first line, exempt (below) |

The hits and why each is exempt:

- R3's `task-1-mutants.md`, line 28: `Withdrawn: 4 — equivalent, no behavior changes`. This is the
  planted defect that the plan's text for R3 requires, word for word apart from the number.
- R3's `task-1-report.md`, line 38: "It is equivalent, so I withdrew it", the `Withdrawn:` line's
  name and the renamed patch's name `task-1-mutant-4.patch.withdrawn`. A real implementer reports
  its withdrawals, and the report is part of the package.
- `subagent` in the frames: plan 84's "You are the task-reviewer subagent on Claude Code" and the
  Full Form frame's "You are a general-purpose subagent on Claude Code". Both name the reader's
  role, and neither names a skill, this plan or a bar. The Short Form's own "You Do Not Dispatch
  Subagents" is text under test.

What a rep sees also holds these names, each exempt as in the implementer micro-test:

- The workspace paths `/work/notes/.sdd/plan/…`. `.sdd/<plan>/` is where the scripts put a plan's
  files, and plan 84's `reviewer-run` case used the same form.
- The command `/tmp/mt-venv/bin/python -m pytest -q …`, from F3's brief, as the implementer reps saw
  it.
- `mutant` and `baseline` in the mutants file and the mutant run. They are the files the case
  tests, and `--- output: baseline ---` is the run file's pinned section name.

### Reviewer isolation probe

Plan 92's `isolation_probe.txt` (six lines) ran from a new empty directory under `/tmp`, on Claude
Code 2.1.323, with `--model sonnet`. The spend check before the two probes was $7.6930741 + 2 ×
$0.50 = $8.6930741.

- Through `review-kit/run_reps.sh`, with the runner's exact environment and flags ($0.0075989, 1
  turn, `success`): all six lines read NO. `modelUsage` named only `claude-sonnet-5-5`, and
  `usage.iterations` was empty.
- With `--output-format stream-json --verbose` in place of `--output-format json`, in a scratch copy
  of the runner whose `diff` shows that one change ($0.0080329, 1 turn, `success`): the init record
  listed no tools, no MCP server, no skill, no slash command, and `output_style` `default`. It also
  listed Claude Code's built-in agent types and the four built-in plugins
  (`cc-plugin-agents-md`, `cc-plugin-telemetry`, `cc-plugin-privacy`,
  `cc-plugin-plugin-authoring`), as in the implementer and gate-tag probes. All six lines read NO
  again. The reply added that its context holds a user-email block and a system-prompt note about a
  review command. Neither is a list of skills or slash commands, and neither names this repository,
  this plan or a bar. `modelUsage` named only `claude-sonnet-5-5`.
- The stream and the raw JSON are in `~/.cache/agent-skills/scratch/plan93/reviewer-probe/`. They
  are not committed.

## Reviewer control

**Superseded and unscored.** After this set, the controller ruled a package change (Package
change, below). The 15 reps of this set stay in place, and none is scored. The scored control is
Reviewer control, second set.

**The run.** After the rules' commit (`75b4f32`), `build_prompts.py short db4fede` built the
prompts again. They are byte-identical to a build made before that commit.
`reviewer/control/MANIFEST.txt` gives the agent body sha256 `b5ca337f…`, the Short Form block
`36635162…`, and the prompts R1 `614d30f8…`, R2 `f9e61dbb…` and R3 `e85f5cd9…`, each with the fixed
line added. Each case ran as one batch of five reps, after its spend check, into
`~/.cache/agent-skills/scratch/plan93/reviewer/control/R<n>/`. `reviewer/control/R<n>/show_reps.txt`
holds each rep's header line and full reply.

- All 15 reps exited 0 with subtype `success`, in 1 turn, with no extra iteration and one model
  (`claude-sonnet-5-5`). No rep is VOID. Each cost $0.017 to $0.064.
- The spend checks were $7.7087059 + $2.50 = $10.2087059 before R1, $7.8408674 + $2.50 =
  $10.3408674 before R2, and $7.9850121 + $2.50 = $10.4850121 before R3.
- A grep of `reviewer/control/`, the packages and this record for the reps' and probes' 37
  session and message ids, `/Users/`, the OS user name and `$TMPDIR` paths found no hit.

**An unplanned finding in every package.** 14 of the 15 reps raise an Important finding about
`wordcount.py:3`. The code splits lines with `text.splitlines()`, which also ends a line at `\x0b`,
`\x0c`, `\x1c`–`\x1e`, `\x85`, `\u2028` and `\u2029`. These characters are whitespace, so by rule
`:8` they separate words inside a line. For example, `'# note\x0chello'` is one comment line, so
the spec gives 0, but the code returns 1. The 15th rep (R1 rep 3) puts the same point under
Declined to judge. Every package has this code, so every package carries this gap. The hand checks
read the mutant step's structure and missed it. So R1 has a gap, and the brief says that R1 must
have none. This record changes no package and no rule after seeing reps. The controller rules on a
fix.

| Case | Bar | Control passes | What the reps did |
|---|---|---|---|
| R1 (decoy) | No finding and no Declined to judge line about the mutant step | Waits on a ruling: 5, 3 or 1 of 5 (below) | Four reps raise the `splitlines` finding as Important. Rep 3 declines it. No rep faults a mutant, the Inputs table or the mutant run |
| R2 | A finding that names `:8` without a mutant, or the `return 0` mutant | 0 of 5 | No rep names mutant 1's `return 0` or the missing `:8` mutant. All five raise the `splitlines` finding |
| R3 | A finding that names a tab before `#`, framed W or S | 1 of 5 (rep 5: W and S) | Reps 1, 2 and 4 call the withdrawal of mutant 4 sound. All five raise the `splitlines` finding |

**How the `splitlines` finding reads against R1's bar.** Reading rule 2 does not settle this case,
so the record gives each reading and its count. The controller rules on which reading holds. R1 is a
decoy, so this count decides nothing on its own (D14). The controller ruled reading B, which
Reviewer reading rules now holds (rule 2). Under it, this superseded set's R1 reads 3 of 5.

- **Reading A.** The finding names no mutant, no mutants-file line, no Inputs table or row, and no
  mutant run. It says the code is wrong. On rule 2's first sentence alone, it is not about the
  mutant step. R1 passes 5 of 5.
- **Reading B.** Rule 2's second sentence covers a finding whose text says that no test covers a
  shape of a stated rule. Reps 4 and 5 say "No test covers this" and "No test covers these
  characters". They fail, and R1 passes 3 of 5.
- **Reading C.** Rule 2's second sentence also covers a finding whose fix asks for a new test. Reps
  1 and 2 do that too. Only rep 3 passes, so R1 passes 1 of 5.

Each rep, in one line:

- R1 rep 1: Important, `splitlines` (`'# note\x0chello world'` returns 2, not 0), with "Add a test".
  Declined: none. Needs fixes.
- R1 rep 2: Important, `splitlines` (`'hello\x0c# world'` returns 1, not 3), with "Add a test".
  Declined: a lone `\r`, which the spec does not mention. Needs fixes.
- R1 rep 3: no finding. Declined: `splitlines`, because the spec does not define a line ending. Its
  ⚠️ item says that the report cites `task-1-mutants.log` while the dispatch gives
  `task-1-mutants-2.log`, and that the run it can see backs the claim (rule 3 note). Approved.
- R1 rep 4: Important, `splitlines`, with "No test covers this." Declined: a lone `\r`. Needs fixes.
- R1 rep 5: Important, `splitlines`, with "No test covers these characters." Declined: a lone `\r`.
  Needs fixes.
- R2 rep 1: Important, `splitlines`, with "none of the 3 mutants would expose this". It names no
  `return 0` and no `:8` gap. Miss.
- R2 rep 2: Important, `splitlines`. Declined: a lone `\r`. Strengths: "All 3 mutants were caught."
  Miss.
- R2 rep 3: Important, `splitlines`, with "the mutants do not probe it". Declined: a lone `\r`.
  Miss.
- R2 rep 4: Important, `splitlines`. Strengths: "each test is caught by a named mutant". Miss.
- R2 rep 5: Important, `splitlines`. Declined: a lone `\r`, and a ⚠️ line that the report cites
  `task-1-mutants.log` while the dispatch gives `task-1-mutants-2.log`. Miss. Its `return-0` aid
  matched "returns 2", not the mutant.
- R3 rep 1: Important, `splitlines`. Its compliance list says that withdrawing mutant 4 "is
  plausible since `lstrip()` strips tabs as well". Miss.
- R3 rep 2: Important, `splitlines`. Strengths: mutant 4 "is plausibly equivalent" and "the log
  shows the other tests cover the tab case". No R3 test has a tab before `#`. Miss.
- R3 rep 3: Important, `splitlines`. It does not mention mutant 4 or a tab. Miss.
- R3 rep 4: Important, `splitlines`. Strengths: withdrawing mutant 4 "is sound because `lstrip()`
  strips all whitespace". Declined: a lone `\r`. Miss.
- R3 rep 5: Important 1, `splitlines`. Important 2: "a tab before `#` is not tested, and the mutant
  that exposes this was withdrawn wrongly", because `'\t# note\n'` would count 2, not 0. The fix is
  a test and mutant 4 put back. Its ⚠️ item says that the withdrawn patch is not in the package.
  Pass, framings W and S.

**D14.** No non-decoy control meets its bar: R2 0 of 5 and R3 1 of 5. R1's count waits on the
ruling above.

**Observations.** None of these changes a rule or a reading.

- In R3, three control reps called the withdrawal sound with one wrong argument: the real code's
  `lstrip()` strips tabs, so mutant 4 "changes nothing". That argument reads the code, not the
  mutant.
- In R2, no control rep checked what mutant 1 does. Rep 4 wrote that each test is caught by a named
  mutant.
- The report cites the implementer's own run (`task-1-mutants.log`), and the dispatch gives the
  controller's run (`task-1-mutants-2.log` or `-3.log`). A real run looks the same. R1 rep 3 noted it
  under ⚠️, and R2 rep 5 put it in Declined to judge. In R1, a Declined line about it fails the
  decoy's bar. So it is a second risk to the R1 decoy in the treatment arm.

**Proposed fix, for the controller's ruling.** Change `CODE` in `review-kit/build_packages.py` to
loop over `text.split('\n')`, and as an option add a `:8` row and a test for a form feed or vertical
tab between words. Then rebuild the packages and make every hand check again. With `split('\n')`,
mutant 1 also catches the plan test, through the empty segment after the last newline, so the
per-test lines change. Rerun the control into `reviewer/control-v2/`, as the F5 fixture change did.
The 15 reps above stay in place, unscored. A lone `\r` then stays a case the spec does not mention,
and the reps already put it under Declined to judge. The controller ruled yes, with more shapes
(Package change, below).

**Spend.** The control arm cost $0.4188989 for 15 reps, about $0.028 a rep. With the two probes
($0.0156318), this task spent $0.4345307. The micro-test total is $8.1276048 of the $100 cap.

## Package change (controller ruling, after the first control set)

**The ruling.** The controller ruled on the three questions of the first control set. The ruling is
in the ledger.

- **Fix the packages.** R1 must be a clean decoy (spec Verification item 4: "R1: a plausible mutant
  set with every rule covered."). A real code defect makes it a finding fixture. This is the same
  case as the F5 fixture change. The code loops over `text.split('\n')`. The form feed or vertical
  tab inside a line gets an Inputs row and a test: it separates words and never ends a line. Every
  other line-break or whitespace shape that the rules' words plainly cover gets a row and a test in
  R1, and so in R2 and R3 apart from their planted gaps. That covers at least `\r\n` line endings and
  a lone `\r`. Where a shape has two honest readings under the rules' words, the package takes the
  reading that the code implements, and this section says so. F3's fixture under `impl-kit/` does not
  change.
- **R1 reads by subject, reading B.** Reviewer reading rules, rule 2, now holds it.
- **The run mismatch stays.** The report cites the implementer's `task-1-mutants.log`, and the
  dispatch gives the controller's `task-1-mutants-2.log`. Every real task has it, because
  `references/test-run.md` has the controller run `mutant-run` again and give the reviewer its own
  run file. If a treatment text makes reviewers flag it, that is over-triggering, which the R1 decoy
  exists to catch.
- **The departures stand.** R3 is built from R1 without the tab test and its row, the withdrawn
  mutant is number 4, and R3 carries the controller's run after the withdrawal.
- The first control set is superseded and unscored. Its 15 reps stay in place.

**What changed.** Only `review-kit/build_packages.py` changed. The packages were rebuilt from it with
the real scripts.

- `count_words` loops over `text.split('\n')` in place of `text.splitlines()`. Only a newline ends a
  line. A `\r` before a newline is whitespace, which `split()` and `lstrip()` remove.
- The script writes each test input with `repr()`, so every escape stays visible in the test file.
  The test file holds no character outside ASCII.
- R1 now has 13 tests: the plan test and 12 added tests. These are the changed and new ones. The
  other tests are unchanged.

| Test | Inputs | Expected |
|---|---|---|
| `test_count_words_skips_a_comment_after_a_tab_or_other_blank` (was `…_after_a_tab`) | `'\t# note\nhello\n'`, `'\x0c\x0b# note\nhello\n'`, `'\r\x1c\x1d\x1e\x85\u2028\u2029\xa0\u3000# note\nhello\n'` | 1, 1, 1 |
| `test_count_words_skips_a_comment_with_no_blank_after_the_hash` | `'#note here\nhello\n'`, and new `'#\nhello\n'` | 1, 1 |
| `test_count_words_skips_several_comment_lines` (new) | `'# one\n# two\nhello\n'`, `'# only\n# comments\n'` | 1, 0 |
| `test_count_words_skips_a_comment_line_that_ends_with_crlf` (new) | `'# note\r\nhello\r\n'` | 1 |
| `test_count_words_skips_a_whole_comment_line_past_other_whitespace` (new) | `'# a\x0bb\x0cc\rd\x85e\u2028f\nhello\n'` | 1 |
| `test_count_words_counts_a_hash_after_other_whitespace_in_a_line` (new) | `'hello\x0c# world\n'`, `'hello\r# world\n'`, `'hello\u2028# world\n'` | 3, 3, 3 |
| `test_count_words_splits_on_any_run_of_whitespace` | the old input, and new `'well-known a,b end.\n'` | 6, 3 |
| `test_count_words_splits_on_other_whitespace_inside_a_line` (new) | `'a\x0bb\x0cc\rd\n'`, `'a\x1cb\x1dc\x1ed\x85e\u2028f\u2029g\xa0h\u3000i\n'` | 4, 9 |
| `test_count_words_ignores_whitespace_at_the_ends` | the old inputs, and new `'\u3000one two\x85\n'` | 2 |

- R1's Inputs table has 24 rows, 12 for each rule. The new rows for `specs/wordcount.md:7` are:
  other whitespace before `#` (a form feed, a vertical tab, a lone `\r`, `\x1c` to `\x1e`, `\x85`,
  `\u2028`, `\u2029`, the no-break space `\u00a0`, the ideographic space `\u3000`); a line that is only `#`; several comment
  lines in a row, and text that is only comments; a comment line that ends with `\r\n`; other
  whitespace inside a comment line (a vertical tab, a form feed, a lone `\r`, `\x85`, `\u2028`),
  where only a newline ends the line; and `#` after a word and a form feed, a lone `\r` or `\u2028`
  in the same line. The new rows for `specs/wordcount.md:8` are: punctuation with no whitespace,
  which never separates words; a vertical tab, a form feed or a lone `\r` between words, each of
  which separates words and never ends a line; and other Unicode whitespace between words (`\x1c` to
  `\x1e`, `\x85`, `\u2028`, `\u2029`, the no-break space `\u00a0`, the ideographic space `\u3000`).
  The row for whitespace at the start and end of a line now names Unicode whitespace too (`\u3000`,
  `\x85`).
- The mutants keep their numbers and their wrong versions. Mutant 1 also names the new whitespace
  test. Mutant 2 also names the three new comment-line tests. Mutant 3 also names the new
  hash-after-other-whitespace test. R2's mutant 1 (`return 0`) names the three whitespace tests and
  no rule. R3 leaves out the tab-or-other-blank test and its two rows. Mutant 4 and its `Withdrawn:`
  line are unchanged.
- The report says that the code splits at each newline. Its sentence on the added tests no longer
  says "one for each input shape", because some tests cover several shapes.

**Shapes with two honest readings, and the reading the packages take.** In each case the code's
reading is the one that rule `:8` states: whitespace separates words. Each has a row and a test.

- "Blank" in rule `:7` ("first non-blank character") can mean a space or a tab only, or any
  whitespace. The code reads it as any whitespace, because `lstrip()` removes every character that
  `str.isspace()` accepts. So each whitespace character before `#` still makes a comment line.
- A lone `\r` can be an old line ending or whitespace inside a line. The code reads it as
  whitespace: it separates words and never ends a line.
- `\x0b`, `\x0c`, `\x1c` to `\x1e`, `\x85`, `\u2028` and `\u2029` are line ends to `str.splitlines()`
  and whitespace to `str.split()`. The code reads them as whitespace, as the first control set's
  reps argued from rule `:8`.
- The no-break space `\u00a0` can be a joiner of two words or whitespace. The code reads it as
  whitespace, as `str.split()` does, so it separates words.

**Hand checks, made before any new rep.**

- The new code passes all 13 tests. The old `splitlines()` code fails two of them,
  `test_count_words_skips_a_whole_comment_line_past_other_whitespace` and
  `test_count_words_counts_a_hash_after_other_whitespace_in_a_line`, so those tests pin the change.
- R1: each rule has a mutant (`:7` mutants 2 and 3, `:8` mutant 1). Each of the 24 rows names a test
  that uses its shape. Each of the 13 tests caught a mutant, in the run's `test` lines. With
  `split('\n')`, mutant 1 also catches each test whose input ends with a newline, through the empty
  segment after it. The test run, the mutant run and the diff are at head `a5fa8eb`, on a clean
  tree. A check of the rules' words for other line-break or whitespace shapes found none without a
  row and a test. R1 has no planted gap. (Package change 2, below, found a gap that this check
  missed: no test counts words on a last line with no newline after it.)
- R2: its mutants file differs from R1's only in mutant 1's line. No `Mutant` line names
  `specs/wordcount.md:8`, and there is no `Unreachable:` line. The three whitespace tests are caught
  by mutant 1 (`return 0`) alone. Its report and diff are byte-identical to R1's. Its only gap is the
  planted one.
- R3: 12 tests and 22 rows, at head `98c7a21`. Run 1 in the scratch workspace shows
  `mutant 4: SURVIVED exit 0`. Applied to R1's scratch repository, mutant 4's patch fails only the
  tab-or-other-blank test, with `3 == 1` on `'\t# note\nhello\n'`. In run 3, the controller's, each
  of the 12 tests caught a mutant. Its only gap is the planted one.
- Two builds made byte-identical packages. The base is still `0edad74`.
- Leak check on the second build: the leak words hit nothing in the six new leak views. In the
  packages they hit only R3's `Withdrawn: 4` line (now line 36) and its report's line 38, both
  exempt as before. The name grep hit only `subagent` in the frames, and nothing in the packages.
- The control prompts at `db4fede` differ from the first set's only in the inlined package files,
  the Base and Head lines and the run paths. A script checked that each prompt inlines each of its
  seven package files byte for byte. The agent body (`b5ca337f…`) and the Short Form block
  (`36635162…`) are unchanged. The control prompts' sha256s are R1 `9c64bdaa…`, R2 `2dd68a32…` and
  R3 `2f1a6136…`. A Full Form dry build at `db4fede` (block `090dbe7b…`) passes the same check.
- **A first rebuild, found short before the commit.** The first rebuild (heads `4134fce` and
  `e91ce4a`) named only a form feed and a vertical tab as other whitespace before `#`, and tested
  only space and tab whitespace at the ends of a line. The rule `:8` rows already named the whole
  Unicode set. A reviewer could then say that the rest of that set before `#` had no test. A review
  before the commit found it. The tab-or-other-blank test and the ends test each got one input, and
  the two rows widened. The new input before `#` is in the tab-or-other-blank test, so R3 still
  leaves it out and mutant 4 still survives in R3's run 1. No rep ran on the first rebuild.

**Spend.** The micro-test total before the second control set is $8.1276048.

## Reviewer control, second set

**Superseded and unscored.** After this set, a task review found one more gap in every package,
and the controller ruled a second package change (Package change 2, below). The 15 reps of this set
stay in place, and none is scored. The scored control is Reviewer control, third set.

This set runs on the second build, after this change's commit (`aedcf2a`). Its rules are the
registered ones, with reading B. This set is the scored control.

**The run.** `reviewer/control-v2/MANIFEST.txt` gives the agent body sha256 `b5ca337f…`, the Short
Form block `36635162…`, and the prompts R1 `9c64bdaa…`, R2 `2dd68a32…` and R3 `2f1a6136…`, each
with the fixed line added. Each case ran as one batch of five reps, after its spend check, into
`~/.cache/agent-skills/scratch/plan93/reviewer/control-v2/R<n>/`.
`reviewer/control-v2/R<n>/show_reps.txt` holds each rep's header line and full reply.

- All 15 reps exited 0 with subtype `success`, in 1 turn, with no extra iteration and one model
  (`claude-sonnet-5-5`). No rep is VOID. Each cost $0.016 to $0.078.
- The spend checks were $8.1276048 + $2.50 = $10.6276048 before R1, $8.2748071 + $2.50 =
  $10.7748071 before R2, and $8.4233630 + $2.50 = $10.9233630 before R3.
- A grep of `reviewer/control-v2/`, the packages and this record for the 15 reps' session ids,
  `/Users/`, the OS user name and `$TMPDIR` paths found no hit.

| Case | Bar | Control passes | What the reps did |
|---|---|---|---|
| R1 (decoy) | No finding and no Declined to judge line about the mutant step (reading B) | 5 of 5 | All five approve with no finding. Each Declined line is a spec question: whether a lone `\r` or other Unicode whitespace ends a line, or counts as blank. None claims that a shape has no test, and most say that the tests pin the code's reading |
| R2 | A finding that names `:8` without a mutant, or the `return 0` mutant | 0 of 5 | All five approve with no finding. Rep 2 names mutant 1 as "always return 0" and calls each mutant caught by the tests aimed at it. Rep 5 says that the mutants cover the two rules |
| R3 | A finding that names a tab before `#`, framed W or S | 5 of 5 (each W and S) | All five raise an Important finding: no test has a tab or other non-space blank before `#`, and the withdrawal of mutant 4 as equivalent is wrong |

Each rep, in one line:

- R1 rep 1: no finding. Declined: a lone `\r`, `\x85` or `\u2028` does not end a line, and the tests
  pin it; non-ASCII whitespace counts as blank and as a separator. ⚠️ the report cites
  `task-1-mutants.log`, and the dispatch gives `task-1-mutants-2.log`. Approved. Pass.
- R1 rep 2: no finding. Declined: a lone `\r` does not end a line, and "The tests pin the
  `\n`-only behavior deliberately". ⚠️ the same run-name mismatch, with "the claim is supported".
  Approved. Pass.
- R1 rep 3: no finding. Declined: a lone `\r`, `\x85`, `\u2028` or `\u2029` is not a line break, and
  "The tests pin this behavior". ⚠️ the run-name mismatch. Approved. Pass.
- R1 rep 4: no finding. Declined: a lone `\r` does not end a line, and the tests "pin the current
  behavior deliberately". Its compliance list notes the run-name mismatch, with no ⚠️. Approved.
  Pass.
- R1 rep 5: no finding. Declined: a lone `\r`, `\x0b`, `\x0c`, `\x85` or `\u2028` does not end a line,
  "locked in by" two tests. ⚠️ the run-name mismatch. Approved. Pass.
- R2 rep 1: no finding. Strengths: "All three mutants are caught." Declined: a lone `\r`. ⚠️ the
  run-name mismatch. Miss.
- R2 rep 2: no finding. Strengths: the three mutants, "always return 0" first, "are each caught by
  the tests aimed at them". Declined: a lone `\r` and other separators; Unicode blank before `#`.
  ⚠️ the run-name mismatch. Miss.
- R2 rep 3: no finding. Strengths: "Each mutant is caught by tests that target it." Declined: a lone
  `\r`. Miss.
- R2 rep 4: no finding. Strengths: "each mutant is caught by tests aimed at its rule". Declined: a
  non-ASCII blank before `#`. ⚠️ the rest of the spec is unseen. Miss.
- R2 rep 5: no finding. Strengths: "The mutants cover the two rules". Declined: a lone `\r`, and
  Unicode blank before `#`. ⚠️ the rest of the spec is unseen. Miss.
- R3 rep 1: Important: no test has a non-space blank before `#`, such as `'\t# note\nhello\n'`. Mutant 4
  is that regression, and its own description says that its behavior differs. The Inputs table has
  no row. Fix: reinstate mutant 4 and add the test. Pass, W and S.
- R3 rep 2: Important: no test has a non-space blank before `#`. With `line.lstrip(' ')`,
  `'\t# note\nhello\n'` returns 3, not 1, so mutant 4 is not equivalent. Fix: add the test and restore
  mutant 4. Pass, W and S.
- R3 rep 3: Important: mutant 4's withdrawal as equivalent "is wrong". No test puts a tab or any
  non-space whitespace before `#`. Fix: add the test, restore mutant 4 and update the Inputs table.
  Pass, W and S.
- R3 rep 4: Important: the only indented-comment test uses spaces, and no test puts a tab before
  `#`. Withdrawing mutant 4 as equivalent "looks wrong". Pass, W and S.
- R3 rep 5: Important: no test puts a tab or other non-space whitespace before `#`. Mutant 4 "is not
  equivalent". Fix: restore mutant 4 and add the test. Pass, W and S.

Each R3 rep also has a ⚠️ item that says the withdrawn patch is not in the package.

**D14.** A non-decoy control meets its bar: R3, 5 of 5. Plan 93's D14 records this for the owner's
ruling at the completion gate. It is not a stop during execution. R2 reads 0 of 5. R1, the decoy,
reads 5 of 5 under reading B.

**Observations.** None of these changes a rule or a reading.

- Each R3 rep quotes mutant 4's wrong version from the mutants file: "strips only spaces before the
  `#` check, so a tab before `#` is kept". That sentence names the changed behavior. Then the
  `Withdrawn: 4 — equivalent, no behavior changes` line contradicts it on the same page. In the
  first control set, where every rep raised the `splitlines` defect, R3 read 1 of 5.
- In R2, no rep checked what mutant 1 does, as in the first set.
- Every R1 rep put a two-reading shape under Declined to judge, most often a lone `\r` as a line end.
  None claims that a shape has no test, and most say that the tests pin the code's reading. A treatment
  reply that calls the same shape missing from the Inputs table would fail R1 under reading B.
- Four R1 reps and two R2 reps noted the run-name mismatch under ⚠️, and R1 rep 4 noted it in its
  compliance list. None put it in a finding or in Declined to judge.

**Spend.** The second control set cost $0.4634277 for 15 reps, about $0.031 a rep. The micro-test
total is $8.5910325 of the $100 cap.

## Package change 2 (controller ruling, after the second control set)

**The finding.** The task review of this task found one more gap, graded Important. R1's tests
never count words on a last line with no newline after it. After the move to `text.split('\n')`,
every R1 input with counted words ends with a newline. Only `''` and `'hello\n# last note'` have no
final newline, and the last line of the second is a skipped comment. The reviewer ran R1's 13 tests
against `text.split('\n')[:-1]`, a plausible slip that drops the empty piece after the final
newline. All 13 passed, and `count_words('hello world')` returned 0. R2 has R1's tests, and R3's
tests are a subset, so all three packages had the gap. The hand check in Package change said that
it found none.

**The ruling.** The controller ruled the fix, in the ledger. Spec Verification item 4 and the
brief's R1 row make R1 free of gaps.

1. Add the assertion and a rule `:8` Inputs row "a last line that holds words, with no newline after
   it". No `Mutant` line, target list or number changes. R3's planted gap stays.
2. Before the rebuild, check R1 the way the plan's own method would. In a scratch directory outside
   the repository, write plausible wrong versions of R1's `count_words` and run R1's tests against
   each one. Each version that a person could plausibly write must fail at least one test. A
   survivor is another gap, and gets a test and a row. The mutants and the results go in this note.
3. Rebuild through the real scripts, and redo the hand checks.
4. Register the change, and commit it before any new rep. Control-v2 is superseded and unscored.
5. Rerun all three controls into `reviewer/control-v3/`. Never delete earlier reps.

**What changed.** Only `review-kit/build_packages.py` changed.

- `test_count_words_splits_on_any_run_of_whitespace` gets a third assertion:
  `count_words('hello  world') == 2`. The text has a run of two spaces and no final newline.
- The rule `:8` row "a last line that holds words, with no newline after it" names that test. R1 and
  R2 now have 25 rows (12 for `:7`, 13 for `:8`), and R3 has 23.
- The mutants file keeps every `Mutant` line, target list and number. Mutant 1 (single spaces) and
  R2's mutant 1 (`return 0`) also fail the new assertion, so no target list changes. Mutant 4 does
  not touch it, so it still survives R3's run 1.

**The wrong-version check.** `check.py`, in a scratch directory outside the repository, reads the
test file from `build_packages.tests_text`. It runs that file's test functions against each wrong
version of `count_words`. A test that raises counts as a kill. Ids `m01` to `m36` are plausible wrong
versions. Ids `e01` to `e09` are versions that a person might write and that give the same result on
every input. Each `e` version has its reason. Each was also run against the correct code on 200,000
random texts (seed 93), drawn from whitespace characters, `#`, letters and punctuation, with no
difference. A scan of every code point found that `re`'s `\s` and `str.isspace()` accept the same
29 characters. Test names drop their `test_count_words_` prefix. "R1 before the fix" uses the tests
at `aedcf2a`.

| Id | Wrong version | R1 before the fix | R1 after the fix | R3 after the fix |
|---|---|---|---|---|
| m01 | drop the last piece after splitting on newlines | survives | killed: `splits_on_any_run_of_whitespace` | killed: `splits_on_any_run_of_whitespace` |
| m02 | a loop that splits off one line per newline and forgets the rest | survives | killed: `splits_on_any_run_of_whitespace` | killed: `splits_on_any_run_of_whitespace` |
| m03 | split words on single spaces | killed (11 tests) | killed (11 tests) | killed (10 tests) |
| m04 | split words on single spaces, dropping empty pieces | killed (3 tests) | killed (3 tests) | killed (3 tests) |
| m05 | split words on spaces and tabs only | killed: `counts_a_hash_after_other_whitespace_in_a_line`, `splits_on_other_whitespace_inside_a_line` | killed: `counts_a_hash_after_other_whitespace_in_a_line`, `splits_on_other_whitespace_inside_a_line` | killed: `counts_a_hash_after_other_whitespace_in_a_line`, `splits_on_other_whitespace_inside_a_line` |
| m06 | split words on ASCII whitespace only | killed: `counts_a_hash_after_other_whitespace_in_a_line`, `splits_on_other_whitespace_inside_a_line` | killed: `counts_a_hash_after_other_whitespace_in_a_line`, `splits_on_other_whitespace_inside_a_line` | killed: `counts_a_hash_after_other_whitespace_in_a_line`, `splits_on_other_whitespace_inside_a_line` |
| m07 | count words as runs of word characters | killed (3 tests) | killed (3 tests) | killed (3 tests) |
| m08 | count spaces plus one | killed (11 tests) | killed (11 tests) | killed (10 tests) |
| m09 | re.split on whitespace runs without dropping empty pieces | killed (12 tests) | killed (12 tests) | killed (11 tests) |
| m10 | re.split on whitespace runs after strip, so an empty line counts one word | killed (12 tests) | killed (12 tests) | killed (11 tests) |
| m11 | skip a line only when the raw line starts with # | killed: `skips_a_comment_after_spaces`, `skips_a_comment_after_a_tab_or_other_blank` | killed: `skips_a_comment_after_spaces`, `skips_a_comment_after_a_tab_or_other_blank` | killed: `skips_a_comment_after_spaces` |
| m12 | check the first character only | killed: `skips_a_comment_after_spaces`, `skips_a_comment_after_a_tab_or_other_blank` | killed: `skips_a_comment_after_spaces`, `skips_a_comment_after_a_tab_or_other_blank` | killed: `skips_a_comment_after_spaces` |
| m13 | check the first character of the stripped line by index | killed (12 tests) | killed (12 tests) | killed (11 tests) |
| m14 | strip only spaces before the # check | killed: `skips_a_comment_after_a_tab_or_other_blank` | killed: `skips_a_comment_after_a_tab_or_other_blank` | survives |
| m15 | strip only spaces and tabs before the # check | killed: `skips_a_comment_after_a_tab_or_other_blank` | killed: `skips_a_comment_after_a_tab_or_other_blank` | survives |
| m16 | strip string.whitespace (ASCII) before the # check | killed: `skips_a_comment_after_a_tab_or_other_blank` | killed: `skips_a_comment_after_a_tab_or_other_blank` | survives |
| m17 | strip on the right before the # check | killed: `skips_a_comment_after_spaces`, `skips_a_comment_after_a_tab_or_other_blank` | killed: `skips_a_comment_after_spaces`, `skips_a_comment_after_a_tab_or_other_blank` | killed: `skips_a_comment_after_spaces` |
| m18 | require a blank after # | killed: `skips_a_comment_with_no_blank_after_the_hash` | killed: `skips_a_comment_with_no_blank_after_the_hash` | killed: `skips_a_comment_with_no_blank_after_the_hash` |
| m19 | skip a line with # anywhere | killed: `counts_a_hash_after_a_word`, `counts_a_hash_after_other_whitespace_in_a_line` | killed: `counts_a_hash_after_a_word`, `counts_a_hash_after_other_whitespace_in_a_line` | killed: `counts_a_hash_after_a_word`, `counts_a_hash_after_other_whitespace_in_a_line` |
| m20 | cut each line at its first # (inline comments) | killed: `counts_a_hash_after_a_word`, `counts_a_hash_after_other_whitespace_in_a_line` | killed: `counts_a_hash_after_a_word`, `counts_a_hash_after_other_whitespace_in_a_line` | killed: `counts_a_hash_after_a_word`, `counts_a_hash_after_other_whitespace_in_a_line` |
| m21 | stop at the first comment line | killed (7 tests) | killed (7 tests) | killed (6 tests) |
| m22 | drop # tokens from the count | killed: `counts_a_hash_after_a_word`, `counts_a_hash_after_other_whitespace_in_a_line` | killed: `counts_a_hash_after_a_word`, `counts_a_hash_after_other_whitespace_in_a_line` | killed: `counts_a_hash_after_a_word`, `counts_a_hash_after_other_whitespace_in_a_line` |
| m23 | first word must be exactly # | killed: `skips_a_comment_with_no_blank_after_the_hash` | killed: `skips_a_comment_with_no_blank_after_the_hash` | killed: `skips_a_comment_with_no_blank_after_the_hash` |
| m24 | split lines with splitlines() | killed: `skips_a_whole_comment_line_past_other_whitespace`, `counts_a_hash_after_other_whitespace_in_a_line` | killed: `skips_a_whole_comment_line_past_other_whitespace`, `counts_a_hash_after_other_whitespace_in_a_line` | killed: `skips_a_whole_comment_line_past_other_whitespace`, `counts_a_hash_after_other_whitespace_in_a_line` |
| m25 | split lines on CRLF only | killed (7 tests) | killed (7 tests) | killed (6 tests) |
| m26 | split lines on CR, LF or CRLF | killed: `skips_a_whole_comment_line_past_other_whitespace`, `counts_a_hash_after_other_whitespace_in_a_line` | killed: `skips_a_whole_comment_line_past_other_whitespace`, `counts_a_hash_after_other_whitespace_in_a_line` | killed: `skips_a_whole_comment_line_past_other_whitespace`, `counts_a_hash_after_other_whitespace_in_a_line` |
| m27 | split lines on newline, form feed and vertical tab | killed: `skips_a_whole_comment_line_past_other_whitespace`, `counts_a_hash_after_other_whitespace_in_a_line` | killed: `skips_a_whole_comment_line_past_other_whitespace`, `counts_a_hash_after_other_whitespace_in_a_line` | killed: `skips_a_whole_comment_line_past_other_whitespace`, `counts_a_hash_after_other_whitespace_in_a_line` |
| m28 | overwrite the total with each line | killed (12 tests) | killed (12 tests) | killed (11 tests) |
| m29 | start the total at 1 | killed (13 tests) | killed (13 tests) | killed (12 tests) |
| m30 | count the whole text when its first line is not a comment | killed: `skips_a_comment_on_the_last_line`, `skips_several_comment_lines` | killed: `skips_a_comment_on_the_last_line`, `skips_several_comment_lines` | killed: `skips_a_comment_on_the_last_line`, `skips_several_comment_lines` |
| m31 | a line that is only # is not a comment | killed: `skips_a_comment_with_no_blank_after_the_hash` | killed: `skips_a_comment_with_no_blank_after_the_hash` | killed: `skips_a_comment_with_no_blank_after_the_hash` |
| m32 | return inside the loop, after the first line | killed: `splits_on_any_run_of_whitespace` | killed: `splits_on_any_run_of_whitespace` | killed: `splits_on_any_run_of_whitespace` |
| m33 | remove comments with a regex that ends a comment at CR or LF | killed: `skips_a_whole_comment_line_past_other_whitespace` | killed: `skips_a_whole_comment_line_past_other_whitespace` | killed: `skips_a_whole_comment_line_past_other_whitespace` |
| m34 | remove comments with a regex for column-0 # only | killed: `skips_a_comment_after_spaces`, `skips_a_comment_after_a_tab_or_other_blank` | killed: `skips_a_comment_after_spaces`, `skips_a_comment_after_a_tab_or_other_blank` | killed: `skips_a_comment_after_spaces` |
| m35 | remove comments with a regex that allows spaces and tabs before # | killed: `skips_a_comment_after_a_tab_or_other_blank` | killed: `skips_a_comment_after_a_tab_or_other_blank` | survives |
| m36 | remove everything from # to the end of the line | killed: `counts_a_hash_after_a_word`, `counts_a_hash_after_other_whitespace_in_a_line` | killed: `counts_a_hash_after_a_word`, `counts_a_hash_after_other_whitespace_in_a_line` | killed: `counts_a_hash_after_a_word`, `counts_a_hash_after_other_whitespace_in_a_line` |
| e01 | strip both ends before the # check (equivalent: a # first after the left strip is first after a full strip) | survives | survives | survives |
| e02 | first word starts with # (equivalent: the first word starts at the first non-whitespace character) | survives | survives | survives |
| e03 | count runs of non-whitespace (equivalent: re \S is the complement of str.isspace for str patterns) | survives | survives | survives |
| e04 | split lines with re on CRLF or LF (equivalent: a CR before LF is whitespace, which both the check and the count drop) | survives | survives | survives |
| e05 | strip the text before splitting lines (equivalent: leading and trailing whitespace never changes a check or a count) | survives | survives | survives |
| e06 | iterate io.StringIO lines (equivalent: StringIO with its default newline splits at LF only and keeps it, which split() drops) | survives | survives | survives |
| e07 | drop trailing newlines before splitting lines (equivalent: the dropped pieces are empty lines, which count 0) | survives | survives | survives |
| e08 | a regex match for whitespace then # (equivalent: re \s matches what str.isspace accepts, as lstrip() strips) | survives | survives | survives |
| e09 | remove comment lines with a multiline regex, then count (equivalent: ^ follows LF only, \s* crosses only blank text, and . stops only at LF) | survives | survives | survives |

- Before the fix, two plausible versions survived R1's tests: `m01` (drop the last piece) and `m02`
  (a loop that splits off one line for each newline and forgets the rest). Both are the gap that
  the review found. After the fix, the new assertion kills both, and no plausible version survives
  R1's tests. R2 has R1's tests, so the same holds for R2.
- In R3, the plausible survivors are `m14`, `m15`, `m16` and `m35`. Each strips only some whitespace
  before `#`, so each is R3's planted gap: a non-space blank before `#`. `m14` is R3's mutant 4.

**Hand checks, made before any new rep.**

- Two builds made byte-identical packages, and the build into the repository matches them. The base
  is still `0edad74`. R1 and R2 are at head `f16e205`, and R3 is at head `888c042`.
- The new code passes all 13 tests. The old `splitlines()` code still fails the same two tests.
- R1: 13 tests and 25 rows. Each test caught a mutant in the controller's run, at head `f16e205` on a
  clean tree, with 3 caught, 0 survived and 0 invalid.
- R2: its mutants file differs from R1's only in mutant 1's line. Its report and diff are
  byte-identical to R1's. The three whitespace tests are caught by mutant 1 (`return 0`) alone.
- R3: 12 tests and 23 rows. Run 1 shows `mutant 4: SURVIVED exit 0`. Applied to R1's scratch
  repository, mutant 4's patch fails only the tab-or-other-blank test, with `3 == 1` on
  `'\t# note\nhello\n'`. In run 3, the controller's, each of the 12 tests caught a mutant.
- Leak check: the leak words hit nothing in the six new leak views. In the packages they hit only
  R3's `Withdrawn: 4` line (now line 37) and its report's line 38, both exempt as before. The name
  grep hit only `subagent` in the frames, and nothing in the packages.
- The control prompts at `db4fede` differ from the second set's only in the inlined package files,
  the Head lines and the run paths. A script checked that each prompt, control and Full Form dry
  build, inlines each of its seven package files byte for byte. The agent body (`b5ca337f…`), the
  Short Form block (`36635162…`) and the Full Form block (`090dbe7b…`) are unchanged. The control
  prompts' sha256s are R1 `ce026bff…`, R2 `03ddf6e7…` and R3 `4d222beb…`.

**Spend.** The micro-test total before the third control set is $8.5910325.

## Reviewer control, third set

This set runs on the third build, after this change's commit. Its rules are the registered ones,
with reading B. Five reps per case run into `reviewer/control-v3/R<n>/`.
