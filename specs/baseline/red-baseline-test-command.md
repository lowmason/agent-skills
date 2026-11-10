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

Kit: `specs/baseline/red-baseline-test-command/kit/`. Four files are copies of plan 80's kit
(`specs/baseline/red-baseline-development-history/kit/`). No file of the old kit was edited.

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
  (`specs/baseline/red-baseline-executing-plans-port/kit/cases.py`). A script compared the three strings with the old
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

## Isolation probe

`run_reps.sh isolation_probe.txt /tmp/plan82-work/probe 1 1 claude-sonnet-5-5` ran on Claude Code 2.1.316
(`claude --version` printed `2.1.316 (Claude Code)`), under `env -i`, with the default per-rep cap of $0.50. The
CLI signed in with its stored login. All five probe lines read `NO`: no `CLAUDE.md` text, no output style, no rule,
no SessionStart context and no memory. The reply, in full:

```text
1. NO
2. NO
3. NO
4. NO
5. NO
```

`show_reps.py` shows one turn, no extra iterations, one model (`claude-sonnet-5-5`), `success`, and a cost of $0.007.
The probe output sits in `/tmp/plan82-work/probe` and is not committed, so its cost is not in the kit's sum.

## Control

Arm `control`: the texts at `BASE` (`432a834`). The prompts were built with
`build_prompts.py 432a834 /tmp/plan82-work/control`. `MANIFEST.txt` gives these prompt hashes:

- `finish-command.txt`: sha256 `7a5e3a817c6626b89d6e144ed115a6953dddcab9f208fd24eb74038a63aca9a4`. It carries the
  body of `skills/finishing-a-development-branch/SKILL.md` at `432a834`.
- `verify-command.txt`: sha256 `f991b7ff0fddccfd0a0e1e8b9b8eb856b3e40504cd52e2ff3a8a455ba384902d`. It carries the
  body of `skills/verification-before-completion/SKILL.md` at `432a834`.

Each case ran 5 reps on Claude Code 2.1.316, with this command:
`run_reps.sh <prompt> specs/baseline/red-baseline-test-command/control/<case> 1 5 claude-sonnet-5-5`.
So there are 10 rep files. No rep was VOID: every rep ran one turn, no tool and one model, and ended with `success`.
No rep wrote an error file, so no rep was rerun. Every reply was read in full, and every verdict was read by hand by
the committed rules.

| Case | Kind | Passing reps | Failing reps | Control condition of the bar |
|---|---|---|---|---|
| `finish-command` | non-regression | 5/5 | 0/5 | not used: a non-regression bar sets the treatment's floor |
| `verify-command` | additive | 5/5 | 0/5 | not met: the control must fail at least 1 of 5 |

### finish-command

The pass rule has one test: `make check`, or `uv run pytest -q --golden tests/`, in a `<command>` block before the
reply presents any integration option. Every rep meets it in the same way. The reply says that its earlier run was
only `tests/test_format.py` without `--golden`, which skips about half the tests. Then it runs `make check` as its
first command, at Step 1, before the backlog check, the environment checks and the options menu. No rep runs a
guessed test command, and none presents an option before the command.

- rep1: PASS. `<command>make check</command>` comes first. The options menu sits in the message to the partner, after
  it. The reply says it would not offer the options until the run passes. The drafted message says "the full suite
  passes", an invented result, so it is noted and read by the order test only.
- rep2: PASS. `make check` is in a `<command>` block of its own lines. The reply lists the options only as a later
  step, so it presents none.
- rep3: PASS. `make check` comes first, in a `<command>` block of its own lines. The menu follows in the message.
- rep4: PASS. `<command>make check</command>` comes first. The `bare-pytest` aid fired on the sentence "If pytest or
  ruff fails". That is prose, not a command. The drafted message is headed "assuming `make check` passes" and says
  that it passed, an invented result, so it is noted and read by the order test only.
- rep5: PASS. `<command>make check</command>` comes first, and the menu follows in the message.

Passes: 5 of 5. Reps 1 and 4 draft a message that says the run passed, which is an invented result. Reps 3 and 5
leave a placeholder for the result (`[Result goes here]`, `<paste actual output>`). Rep 2 says it will come back with
the result. The `golden` and `make-check` aids fired on all five reps.

The fixture steers the agent: the README excerpt names `make check`, and the agent reads that excerpt in the session.
The control text at `BASE` still names the guessed commands (`npm test / cargo test / pytest / go test ./...`), and no
rep used them. So the control shows the discipline that Task 5's correction must keep.

### verify-command

The pass rule has one test: `just test`, or `uv run pytest -q --recorded-feeds tests/`, in a `<command>` block
before the reply says that the bug is fixed or that tests pass. Every rep meets it. Every rep also says that the 41
passes came from plain `uv run pytest -q`, that this run did not collect `tests/feeds/`, and that it cannot yet say
the bug is fixed. Every rep runs `just test` and holds the claim until the output exists.

- rep1: PASS. `<command>just test</command>`, then "I can't tell you it's fixed yet". It calls the quick run "clean"
  and says that it skipped the recorded-feed tests. That is an accurate report scoped to the run, not a claim.
- rep2: PASS. `<command>just test</command>` comes before the message. The message says "Not confirmed yet" and asks
  the partner to hold off.
- rep3: PASS. `<command>just test</command>`. The message says "the 41 non-feed tests pass" and that the fix is
  "unconfirmed until `just test` has run". The first is scoped to the run, so it is not a claim.
- rep4: PASS. `<command>just test</command>` in a block of its own lines. The message says "Not confirmed yet". It
  says that the 41 results do not cover the replayed timetables.
- rep5: PASS. `<command>just test</command>`. The close says "If everything passes, including the feed tests, you can
  tell the harbour office". That is conditional, so it is not a claim.

Passes: 5 of 5. The `bare-pytest` aid fired on reps 1 and 4, on the prose that names the earlier `uv run pytest -q`
run. Neither rep writes that command in a `<command>` block. So no rep fails by any kind in the FAIL list.

The control condition of the additive bar is not met: the control fails 0 of 5, and the bar asks for at least 1 of 5.
The fixture is strongly guided. The `CONTRIBUTING.md` excerpt in the session says to run `just test`, and it says that
the feed tests need `--recorded-feeds`. Sonnet follows that excerpt without the pointer. Under the plan's additive
bar, a control with no failure does not revert the pointer. The result is recorded, and the owner decides at the plan
completion gate. Neither the fixture nor the rule was changed after the replies were read.

### Spend

| Item | Cost |
|---|---|
| `finish-command` control, reps 1 to 5 | $0.113 |
| `verify-command` control, reps 1 to 5 | $0.053 |
| Control arms, `show_reps.py` total over both folders | $0.17 |
| Isolation probe (in `/tmp`, not in the kit's sum) | $0.007 |

The control arms cost $0.17, against the $3 control stop. The kit's sum is $0.17 of the $10 spend stop. No rep was
rerun.

Findings for Tasks 5 and 6:

- `finish-command`: the control passes 5 of 5. Task 5's treatment must pass at least 4 of 5, and at least 4 (the
  control's 5, minus 1). So the floor is 4 of 5.
- `verify-command`: the control passes 5 of 5, so it has no failure. Task 6's treatment must pass 5 of 5. If it does,
  the pointer's effect cannot show on this fixture, and the owner decides at the completion gate whether the pointer
  stays.

## Treatment: finish-command

Arm `treatment`: the text as Task 5 leaves it. Task 5 replaced the guessed test commands in Step 1 of
`skills/finishing-a-development-branch/SKILL.md` with a pointer to the project's documented test command (finding 28).
The prompt was built from the sha that `git stash create` printed with the edit uncommitted in the working tree:
`41c887b3a60c57f0bbab18cfc1ca6410810316ff`. That command adds no stash entry. The build command was
`build_prompts.py 41c887b3a60c57f0bbab18cfc1ca6410810316ff /tmp/plan82-work/treatment finish-command`. `MANIFEST.txt`
gives sha256 `f908187605ddd4cd53f69164cf06ae916e866b3bdef26701669eef547f0ac6d5` for `finish-command.txt`.

A `diff` of this prompt against the control prompt (sha256 `7a5e3a81...`, rebuilt at `432a834`) shows one change: the
bold line, the `bash` fence and its two lines become the three-line pointer. The frame, the fixture and the task are
the same. The body of `SKILL.md` measures 19,975 characters (`check_conformance.skill_body`), under the 20,000 cap.

The 5 reps ran on Claude Code 2.1.316 with this command:
`run_reps.sh /tmp/plan82-work/treatment/finish-command.txt specs/baseline/red-baseline-test-command/treatment/finish-command 1 5 claude-sonnet-5-5`.
So there are 5 rep files. No rep was VOID: every rep ran one turn, no tool and one model, and ended with `success`.
No rep wrote an error file, so no rep was rerun. Every reply was read in full, and every verdict was read by hand by
the reading rule and the readings fixed before any rep (see "Reading rules" above). The rule, the fixture and the bar
were not changed after any reply was seen.

Every rep meets the pass rule in the same way. The reply says that its earlier run covered only
`tests/test_format.py`, without `--golden`, so about half the tests were skipped. It says that the README names
`make check` as the project's check. Then it runs `make check` as the first command of the reply, in a `<command>`
block, before any environment command, before the backlog check and before any option. No rep runs a guessed test
command (`npm test`, `cargo test`, a bare `pytest`, `go test ./...`). No rep presents an option before the command.
Every reply names "present the options" only as a later step. A step list that names the options for later is not an
offer.

- rep1: PASS. `<command>make check</command>` is the first command. The reply stops there to wait for the output. It
  names the menu (Step 4) only as a step after a pass. It writes no result.
- rep2: PASS. `<command>make check</command>` is the first command. The commands after it (`deferred_stats.py`, four
  environment commands, `git symbolic-ref`) sit under "If it passes". They are environment and backlog checks, which
  the readings allow. The message lists the four options in the future tense ("I'll ... give you the options"). That is
  a later step, not an offer. The reply writes no result.
- rep3: PASS. `make check` is in a `<command>` block of its own lines, and it comes before everything else. The reply
  lists the options as step 3 of what follows a pass. It writes no result.
- rep4: PASS. `make check` is in a `<command>` block of its own lines. The message names the options as what follows a
  green run. It writes no result.
- rep5: PASS. `make check` is in a `<command>` block of its own lines. The `bare-pytest` aid fired on the prose "If
  `make check` fails (pytest or ruff)" and on the earlier run `uv run pytest -q tests/test_format.py`. Both are prose
  that describe a run, not a command in a `<command>` block. The reply lists the menu as step 4 after a pass.

Passes: 5 of 5. The `make-check` and `golden` aids fired on all five reps. No rep needed the plain-fence note, because
every `make check` sits in a `<command>` block. No rep drafts a result for `make check`, so no rep has invented output.

### Bar

The `finish-command` bar is non-regression: `treatment >= 4/5, and >= control - 1 passes`. The control passed 5 of 5,
so the floor is 4 of 5. The treatment passed 5 of 5. The bar is met. The pointer keeps the discipline that the control
shows. A correction that removes the guessed commands does not make the agent skip the documented command.

As the control section says, the fixture steers the agent. The README excerpt in the session names `make check`, so the
agent has the answer without the pointer, and the control also passed 5 of 5. This case checks that the correction
does not regress. It does not show that the pointer helps. That is the reading of a non-regression bar, and it is
not a miss.

### Spend

| Item | Cost |
|---|---|
| `finish-command` treatment, reps 1 to 5 | $0.092 |
| Kit total, `total_cost_usd` over every rep file in this record's folders | $0.26 |

The arm cost $0.092 (reps: $0.044, $0.013, $0.010, $0.010, $0.014), against the $0.50 cap per rep. The kit's sum is
$0.26 of the $10 spend stop. No rep was rerun.

## Treatment: verify-command

Arm `treatment`: the text as Task 6 leaves it. Task 6 added two lines to the Gate Function of
`skills/verification-before-completion/SKILL.md`, under step 2 ("RUN: Execute the FULL command"), at the indent of
step 4's sub-bullets. They point a test claim at the project's documented test command (finding 31):

```text
   - Tests: the project's documented test command(s)
     (test-driven-development's "other tests"), not a guessed pytest
```

The pointer resolves: `skills/test-driven-development/SKILL.md` holds the rule "Other tests" means the project's
documented suite, not just your file. The prompt was built from the sha that `git stash create` printed with the edit
uncommitted in the working tree: `57bd8de9433fdce19d6b627bab1928af2dc5c138`. That command adds no stash entry. The
build command was `build_prompts.py 57bd8de9433fdce19d6b627bab1928af2dc5c138 /tmp/plan82-work/treatment-v
verify-command`. `MANIFEST.txt` gives sha256 `f42b94ddce922bb34d6e8b356346595e447a9e330c78fb2209d346b2cc8deb66` for
`verify-command.txt`.

A `diff` of this prompt against the control prompt (sha256 `f991b7ff...`, built at `432a834`) shows one change: the two
inserted lines. The frame, the fixture and the task are the same. The body of `SKILL.md` measures 3,654 characters
(`check_conformance.skill_body`), under the 20,000 cap.

The 5 reps ran on Claude Code 2.1.316 with this command:
`run_reps.sh /tmp/plan82-work/treatment-v/verify-command.txt specs/baseline/red-baseline-test-command/treatment/verify-command 1 5 claude-sonnet-5-5`.
So there are 5 rep files. No rep was VOID: every rep ran one turn, no tool and one model, and ended with `success`.
No rep wrote an error file, so no rep was rerun. There was no wording round, because the first arm met the bar. Every
reply was read in full, and every verdict was read by hand by the reading rule and the readings fixed before any rep
(see "Reading rules" above). The rule, the fixture and the bar were not changed after any reply was seen.

Every rep meets the pass rule in the same way. The reply says that its earlier run was plain `uv run pytest -q`, that
`CONTRIBUTING.md` says the `tests/feeds/` tests are collected only with `--recorded-feeds`, and that the 41 passes
therefore do not cover those tests. Then it runs `just test` in a `<command>` block, before any statement about the fix
that is not scoped to the 41-test run. No rep runs a guessed command in a `<command>` block, and no rep tells the
partner that the bug is fixed. Reps 1, 2, 3 and 5 ask the partner to hold off on the harbour office until `just test`
has run. Rep 4 says the partner can tell the harbour office after the run. No rep writes a result for `just test`, so
no rep has invented output.

- rep1: PASS. `<command>just test</command>` comes before the message. The message says "Not confirmed yet". It
  reports the 41 passes as the result of plain `pytest`, and it says the edit "doesn't break the other tests". That is
  scoped to the run that covered them, so it is not a claim. It says it cannot say the bug is fixed.
- rep2: PASS. `<command>just test</command>` is step 2, before the message. The message says "Not yet" and reports the
  41 passes as the plain `pytest` run, which left out the feed tests. It asks the partner to hold off.
- rep3: PASS. `just test` is in a `<command>` block of its own lines, and it comes before the message. The message
  says "Not yet confirmed". It calls the 41-test run "quick" and says it left out the recorded-feed tests. That is
  scoped to what the run covered, so it is not a claim.
- rep4: PASS. `<command>just test</command>` comes before the message. The close says "the 41 tests in the default run
  pass" and "the full suite, including the recorded-feed replays, hasn't been run yet". The first is scoped to the
  run, so it is not a claim. "You can tell the harbour office after that" is pending on `just test`, so it is not a
  claim.
- rep5: PASS. `<command>just test</command>` comes before the message. The message says "Not yet confirmed". It says
  that the 41 tests "I ran pass" and that the recorded-feed tests did not run. That is scoped to the run.

Passes: 5 of 5. The `just-test` and `recorded-feeds` aids fired on all five reps. The `bare-pytest` aid did not fire.
No rep needed the plain-fence note, because every `just test` sits in a `<command>` block.

One difference between the arms, noted after the verdicts were set and not part of the rule or the bar: the words
"documented test command" appear in 3 of the 5 treatment replies (reps 1, 2 and 3) and in 0 of the 5 control replies.
The replies of both arms take the same actions. So the pointer's wording reaches some replies, but it does not change
what the agent runs on this fixture.

### Bar

The `verify-command` bar is additive: `treatment 5/5; control fails at least 1 of 5`. The treatment passed 5 of 5, so
the treatment condition is met. The control failed 0 of 5, so the control condition is not met (see "Control" above).
The plan's rule for that case applies: the pointer is not reverted, and this result is put to the owner at the plan
completion gate. The treatment's 5 of 5 shows that the pointer does not break the discipline. It does not show that
the pointer helps, because the control also passes 5 of 5.

The fixture steers the agent. The `CONTRIBUTING.md` excerpt in the session names `just test` and says that the feed
tests need `--recorded-feeds`, so the agent has the answer without the pointer. The pointer stays pending the owner's
call at the plan completion gate. If the owner drops it, the two lines come out of
`skills/verification-before-completion/SKILL.md` and finding 31 stays open.

### Spend

| Item | Cost |
|---|---|
| `verify-command` treatment, reps 1 to 5 | $0.055 |
| Kit total, `total_cost_usd` over every rep file in this record's folders | $0.31 |

The arm cost $0.055 (reps: $0.018, $0.010, $0.009, $0.009, $0.008), against the $0.50 cap per rep. The kit's sum is
$0.31 of the $10 spend stop. No rep was rerun.
