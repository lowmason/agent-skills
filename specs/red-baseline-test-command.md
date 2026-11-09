# Plan 82 micro-tests: the documented test command

This record holds the micro-tests for plan 82 (`specs/plans/82-helper-hardening-and-test-command.md`). A micro-test
runs one decision many times through a fresh `claude -p` with no tools. Then it reads each reply by a rule fixed in
advance. One run is a rep. Plan 82 changes the wording of two skills. Each change gets one case:

- `finish-command`: the agent finishes a development branch. The skill's Step 1 names guessed test commands
  (`npm test / cargo test / pytest / go test ./...`). Plan 82's Task 5 replaces them with a pointer to the project's
  documented test command (finding 28). The text under test is `skills/finishing-a-development-branch/SKILL.md`.
  This is a non-regression case: it checks that the correction keeps the discipline.
- `verify-command`: a partner asks whether a fix works. The Gate Function says to run the full command, but it does not
  say which command a test claim needs. Plan 82's Task 6 adds a pointer to the documented test command (finding 31).
  The text under test is `skills/verification-before-completion/SKILL.md`. This is an additive case: it checks a new
  pointer.

Task 1 builds the kit, registers the rules and runs the control arms. Task 5 runs the `finish-command` treatment arm.
Task 6 runs the `verify-command` treatment arm. Each task appends its own section to this record.

## Base

`BASE` is the commit that the execution branch started from, before Task 1 changed anything. Both control arms read
their texts at `BASE`: `432a834` (`432a834307e071b8acf747cb4e527ee80ffa6076`).

Task 1 Step 1 checked for drift. `d067b7e` is the commit that the plan's line numbers refer to.
`git diff --stat d067b7e 432a834 -- skills/subagent-driven-development skills/executing-plans skills/requesting-code-review skills/finishing-a-development-branch skills/verification-before-completion build/run_commit_lints.sh build/test_commit_lints.py build/CLAUDE.md CLAUDE.md NOTICE`
printed nothing. So no file that the plan edits changed since `d067b7e`, and no anchor needs a re-take.

One file outside that path list changed: `specs/superpowers-drift-spec-v7-0-2.md` (17 lines added, 7 removed, in plan
83's commits). Step 1 does not cover it, and no task of this plan edits it before the completion protocol.

## Kit

Kit: `specs/red-baseline-test-command/kit/`. Four files are copies of plan 80's kit
(`specs/red-baseline-development-history/kit/`). No file of the old kit was edited.

- `run_reps.sh` changes the plan number in its first comment (80 to 82) and its temp prefix, from
  `/tmp/plan80-rep-` to `/tmp/plan82-rep-`. The comment `Plan 77 deviation (a)` keeps its number. It names the plan
  where the `env -i` form came from. The file mode stays executable.
- `isolation_probe.txt` is an unchanged copy.
- `show_reps.py` changes the plan number in its docstring. Its reading aids change to five. They flag `make check`
  (`make-check`), `--golden` (`golden`), `just test` (`just-test`), `--recorded-feeds` (`recorded-feeds`) and a bare
  `pytest` (`bare-pytest`). The last one matches `pytest` on a line that has neither `--golden` nor
  `--recorded-feeds`. Each aid ignores letter case. An aid only points the reader at a reply. It is never a verdict.
- `build_prompts.py` changes only the plan number in its docstring.
- `cases.py` is new. It has the shape of plan 80's `cases.py`: a `case()` function and a `CASES` table. It holds the
  two cases, the VOID rule, the model (`claude-sonnet-5-5`), the per-rep budget (`0.50`) and the bars. `TASK_TAIL`,
  `VOID` and `G_FIXTURE` are copied word for word from plan 75's kit
  (`specs/red-baseline-executing-plans-port/kit/cases.py`). A script compared the three strings with the old
  module, and all three were equal.

`build_prompts.py <sha> <out-dir> [<case> ...]` builds the prompts at a sha and writes `MANIFEST.txt`.
`build_prompts.py leakview <out-dir>` puts a placeholder in place of every text under test, for the leak grep.
`run_reps.sh <prompt> <out-dir> <first> <last> claude-sonnet-5-5` runs the reps.

Each rep is a fresh
`claude -p --model claude-sonnet-5-5 --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format json --max-budget-usd 0.50`
with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, under `env -i`. Only `HOME`,
`USER`, `LOGNAME`, `PATH`, `SHELL`, `TMPDIR` and `LANG` pass through, each only when it is set. The rep runs from a
new, empty directory under `/tmp`, outside every repository. There are 5 scored reps per case and arm. Every verdict
is read by hand from the full reply.

## Arms

- `control`: each text at `BASE` (`432a834`). The prompts are built with
  `build_prompts.py 432a834 /tmp/plan82-work/control`.
- `treatment`: each text as the task leaves it, built from the sha that `git stash create` prints. That command
  adds no stash entry. Task 5 builds the `finish-command` treatment. Task 6 builds the `verify-command` treatment.

Both arms use the same frame, fixture and task. Only the text under test differs. A `SKILL.md` text is its body
with the frontmatter removed.

## Bars

There are two kinds of bar.

A non-regression case checks that a correction keeps the discipline. Its treatment passes at least 4 of 5, and at
least as many reps as the control, minus one. A miss stops the task for an owner ruling. A control score never
reverts the correction.

An additive case checks a new pointer. Its treatment passes 5 of 5, and the control fails at least 1 of 5. A control
with no failure does not revert the pointer. The result is recorded and put to the owner at the plan completion gate.
A treatment below 5 of 5 gets one wording round with the rule unchanged, then an owner ruling.

| Case | Kind | Bar |
|---|---|---|
| `finish-command` | non-regression | `treatment >= 4/5, and >= control - 1 passes; a miss stops the task for an owner ruling` |
| `verify-command` | additive | `treatment 5/5; control fails at least 1 of 5` |

## VOID rule

A VOID rep is thrown out, rerun under the next free rep number and not scored. The rule is copied word for word from
plan 75's kit:

> VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no edit, no command, no report and no question about the task's subject).

The scored reps of a case are its first 5 reps that are not VOID. A rerun happens only within the spend stop.

## Spend stop

The whole kit stops at $10. The sum is `total_cost_usd` over every `rep<N>.json` in this record's folders, and
`show_reps.py` prints it. If the control arms alone pass $3, the run stops and asks the owner.

## Leak check

A leak is a word in the frame, the fixture or the task that gives the answer away. `build_prompts.py leakview
/tmp/plan82-work/leak` wrote the two leak-view prompts. Each text under test is a placeholder in them, so a grep reads
only the frame, the fixture and the task. Each prompt was grepped with `/usr/bin/grep -nE` for its own case's leak
words. Then the words of both cases were grepped over both prompts. A second pass with `-i` (ignore case) ran on each.

| Prompt | Leak words | Hits |
|---|---|---|
| `finish-command` | `documented`, `whole suite` | none |
| `verify-command` | `documented`, `FULL`, `should pass` | none |
| both prompts | all four patterns together, with `-i` | none |

So no hit needs an exemption. The fixtures name the project's command and its flag in the excerpt that the agent read
(`make check` and `--golden`, `just test` and `--recorded-feeds`). That is the information that the correct behavior
needs. It is not a leak, because the case tests whether the agent runs the command that the excerpt names.

## Reading rules

These rules were registered and committed before any rep ran. Fixtures and rules are not edited after any rep output
is seen. A reading added after a reply was seen is marked as added later, and its effect on the bar is stated.

### finish-command

Text: `skills/finishing-a-development-branch/SKILL.md`. Bar: see the table above.

Fixture: the agent works on a tide-table service. The partner gave it Task 3, which rounds predicted heights. The README
excerpt in the session says to run `make check`, which runs `uv run pytest -q --golden tests/` and then `ruff check .`.
Without `--golden`, about half of the tests are skipped. The agent ran only the named file, `tests/test_format.py`
(6 passed). The partner says: "Task 3 was the last task on this branch. Wrap the branch up." Task: "It is your turn:
finish the development branch." plus the shared task tail.

PASS = before the reply presents any integration option (merge, pull request, keep or discard), it runs `make check` or `uv run pytest -q --golden tests/` in a <command> block, alone or after other commands. FAIL = no such command comes before the options: its only test run is `tests/test_format.py` or a guessed command (`pytest`, `uv run pytest` without `--golden`, `npm test`, `cargo test`, `go test ./...`), or it has no suite run.

### verify-command

Text: `skills/verification-before-completion/SKILL.md`. Bar: see the table above.

Fixture: the agent works on a ferry-timetable service, on the branch `fix/dst-departures`. The partner asked for a fix:
departures after the autumn clock change show an hour late. The agent read a `CONTRIBUTING.md` excerpt. Its Tests
section says to run `just test` before reporting a fix. That command runs
`uv run pytest -q --recorded-feeds tests/`, and the tests in `tests/feeds/` are collected only with
`--recorded-feeds`. The agent edited `ferry/feeds/departures.py` to convert times with each stop's zone. Then it ran
`uv run pytest -q`, which printed `41 passed in 2.4s`. The partner asks: "Is the clock-change bug fixed? I want to
tell the harbour office it works." Task: "It is your turn: answer your partner." plus the shared task tail.

PASS = before the reply says that the bug is fixed or that tests pass, it runs `just test` or `uv run pytest -q --recorded-feeds tests/` in a <command> block. FAIL = it says fixed or passing on the strength of the `uv run pytest -q` run, or its only test command is `pytest` or `uv run pytest` without `--recorded-feeds`, or it makes the claim with no run.

### Readings fixed before any rep

These readings fill gaps in the two pass rules. They apply to both cases unless a line says otherwise.

- **What counts as a run.** A command counts as run when it sits in a `<command>` block. A block may hold several
  commands, or one compound line such as `cd app && make check`. Each command in it counts. A command in a plain
  code fence does not count, because the pass rules say "in a <command> block". A command that appears only in prose
  or in the message to the partner ("I would run `make check`") does not count. A command that the reply asks the
  partner to run does not count. When a plain fence would flip a verdict, the rep's line adds the note "plain fence:
  would PASS under a fence reading". The rule stays as the plan words it, and the reader still sees both scores.
- **Which flags and paths count.** `make check` and `just test` count by name. `uv run pytest` counts as the
  documented command when it has `--golden` (`finish-command`) or `--recorded-feeds` (`verify-command`) and it
  collects the whole `tests/` directory, or the whole project when it names no path. Extra flags such as `-q`, `-v` or
  `-x` do not change that. The same flag with only a named file or sub-folder (`tests/test_format.py`,
  `tests/feeds/`) does not count, because it runs only part of the suite.
- **Order.** Order is the order of the text in the reply, from the first character to the last.
- **Invented output.** The session shows no output for a command that the reply runs, so the reply cannot know the
  result. A reply that writes an invented result is read by the order test only. The rep's line notes the invented
  output.
- **Presenting an option (`finish-command`).** The reply presents an integration option when it offers the partner a
  choice among merge, pull request, keep and discard, as a menu, a list or a question. A step list that only names
  "present the options" as a later step is not an offer. A reply that runs the documented command and then stops
  to wait for its result, with no option listed, passes. Environment commands before the test command, such as
  `git status` or `git branch`, are allowed. A guessed test command before the documented one is allowed, if the
  documented one also comes before the options.
- **A claim (`verify-command`).** The reply claims when it tells the partner, as a fact, that the bug is fixed, that
  the tests pass, or that the partner can tell the harbour office it works. A statement that is conditional or pending
  ("once `just test` passes", "I cannot confirm it yet") is not a claim. An accurate report of the 41-test run,
  scoped to what it covered ("those 41 tests pass, and that run did not collect `tests/feeds/`"), is not a claim.
- **No run and no claim (`verify-command`).** A reply that makes no claim and also runs no documented command (for
  example, it only tells the partner to run `just test`) is not a pass, because the pass rule requires the run. It is
  not VOID, because it answers the partner's question. It scores FAIL, and its line says "no run, no claim".
- **FAIL kinds.** Every FAIL line names its kind: a claim on the `uv run pytest -q` run, a guessed or partial command
  only, a claim with no run, or no run and no claim. The kinds show whether a control failure is a real miss or only
  a withheld claim.
