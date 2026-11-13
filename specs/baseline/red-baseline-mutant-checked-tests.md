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
