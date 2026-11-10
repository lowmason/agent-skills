# Plan 84 micro-tests: the test-run script's two new uses

This record holds the micro-tests for plan 84 (`specs/plans/84-spec-derived-acceptance-tests.md`). A micro-test runs
one decision many times through a fresh `claude -p` with no tools. Then it reads each reply by a rule fixed in
advance. One run is a rep. Plan 84 adds a `test-run` script to the subagent-driven-development skill (finding 21).
It also teaches that skill's controller and task reviewer to use the script. Each new use gets one case:

- `controller-run`: the implementer reports DONE. The controller must run the task's tests through `test-run`
  before it writes the review package and before it dispatches the reviewer. The texts under test are
  `skills/subagent-driven-development/SKILL.md`, the new `references/test-run.md` (Task 4 adds it) and
  `references/file-handoffs.md`. This is an additive case: it checks a behavior that the new text adds.
- `reviewer-run`: the task reviewer gets a run file next to the implementer's report. The run file shows a skipped
  test where the report claims all tests passed. A mismatch between the run and the report is a finding. The text
  under test is `agents/task-reviewer.md`. This is an additive case too.

Task 1 builds the kit, registers the rules and runs the control arms. Task 4 runs the `controller-run` treatment arm.
Task 5 runs the `reviewer-run` treatment arm. Each task appends its own section to this record.

## Base

`BASE` is the commit that the execution branch started from, before Task 1 changed anything. Both control arms read
their texts at `BASE`: `650e13c` (`650e13c4722a83684a33b219a26f74cb1ffe0fdc`).

Task 1 Step 1 checked for drift. `91d49c4` is the commit that the plan's line numbers refer to.
`git diff --stat 91d49c4 650e13c4722a83684a33b219a26f74cb1ffe0fdc -- skills/subagent-driven-development skills/executing-plans agents/task-reviewer.md runtimes NOTICE`
printed one line: ` NOTICE | 43 +`. The 43 added lines come from plan 86 (the brainstorming port), which merged after
the plan was written. No file that the plan edits changed, except `NOTICE`. Task 1 edits no `NOTICE` line and does not
touch the file. `NOTICE` changes only in Task 6, which re-reads it then. So no anchor needs a re-take.

## Kit

Kit: `specs/baseline/red-baseline-test-run/kit/`. Four files are copies of plan 82's kit
(`specs/baseline/red-baseline-test-command/kit/`). No file of the old kit was edited.

- `run_reps.sh` changes the plan number in its second line (82 to 84) and its temp prefix, from `/tmp/plan82-rep-` to
  `/tmp/plan84-rep-`. The comment `Plan 77 deviation (a)` keeps its number. It names the plan where the `env -i` form
  came from. The file mode stays executable.
- `isolation_probe.txt` is an unchanged copy.
- `show_reps.py` changes the plan number in its docstring. Its reading aids change to five. They flag `test-run`
  (`test-run`), `review-package` (`review-package`), `SKIPPED` (`SKIPPED`), `skipped` (`skipped`) and `make test`
  (`make-test`). The aids `test-run`, `review-package`, `skipped` and `make-test` ignore letter case. The aid
  `SKIPPED` is the only one that does not. It matches the capitals of a pytest summary line (`SKIPPED [1] ...`), so
  the aid `skipped` also covers it. An aid only points the reader at a reply. It is never a verdict.
- `build_prompts.py` changes the plan number in its docstring. It adds two things. A case may carry an optional
  `frame` key, and the default stays the copied `FRAME`. The function `text_block` frames a path under `agents/` as
  `<agent name="<stem>">` around the file's body, with the frontmatter removed. The `agents/` branch sits before the
  fallback branch, which splits a path at `skills/`.
- `cases.py` is new. It has the shape of plan 82's `cases.py`: a `case()` function and a `CASES` table. It holds the
  two cases, the model (`claude-sonnet-5-5`), the per-rep budget (`0.50`) and the bar. `TASK_TAIL`, `VOID` and the
  bar string are copied word for word from plan 82's kit. A script compared them with the old module, and they were
  equal. `case()` takes an optional `frame`. The `reviewer-run` case sets it to `REVIEWER_FRAME`. That frame says the
  text is the agent definition, which is the subagent's system prompt, and it puts the dispatch in `<dispatch>` tags.

The fixtures use one domain that has nothing to do with this repository, a recipe-scaling library (`recipes`).
`reviewer-run` holds its dispatch as a frozen literal. It is the Short Form prompt body of
`skills/subagent-driven-development/task-reviewer-prompt.md` at `BASE`, with the indent removed, each placeholder
filled for Task 2 and one section added after the implementer's-report line: `## The Controller's Test Run`, which
says `Read the controller's run of the task's tests: /work/recipes/.sdd/4-metric-units/task-2-tests.log`. A later
task may edit the template. The frozen literal keeps both arms on the same dispatch. A script compared the literal
with the template at `BASE` plus that section, and they were equal. The four files that the dispatch names sit inline
after the dispatch text, inside the same `<dispatch>` tags, each in `<file path="...">` tags. They are the brief,
the report, the review package and the run file. A script compared the review package with the diff of a scratch
repository and the run file with the plan's lines. They match. The run file's made-up head sha is 40 hex digits and
starts `8e41b07`.

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

- `control`: each text at `BASE` (`650e13c`). The prompts are built with
  `build_prompts.py 650e13c4722a83684a33b219a26f74cb1ffe0fdc /tmp/plan84-work/control`. At `BASE` the glob
  `skills/subagent-driven-development/references/test-run*.md` matches nothing, so the `controller-run` control prompt
  holds two texts and not three.
- `treatment`: each text as the task leaves it, built from the sha that `git stash create` prints. That command adds
  no stash entry. It does not capture an untracked file, so Task 4 stages `references/test-run.md` before it runs
  the command. Without that, the glob matches nothing in the treatment prompt. Task 4 builds the `controller-run`
  treatment. Task 5 builds the `reviewer-run` treatment.

Both arms use the same frame, fixture and task. Only the text under test differs. A `SKILL.md` text is its body
with the frontmatter removed. The agent definition is its body with the frontmatter removed.

## Bar

Both cases are additive. Each checks a new behavior that the text adds. The treatment passes 5 of 5, and the control
fails at least 1 of 5. A control with no failure does not revert the change. The result is recorded and put to the
owner at the plan completion gate. A treatment below 5 of 5 gets one wording round with the rule unchanged, then an
owner ruling.

| Case | Kind | Bar |
|---|---|---|
| `controller-run` | additive | `treatment 5/5; control fails at least 1 of 5` |
| `reviewer-run` | additive | `treatment 5/5; control fails at least 1 of 5` |

The `controller-run` control cannot pass, because `test-run` does not exist at `BASE`. Its 0 of 5 meets the control
condition of the bar by construction. So the unscored note on other test commands (see its reading rule) is the only
control evidence for that case.

## VOID rule

A VOID rep is thrown out, rerun under the next free rep number and not scored. The rule is copied word for word from
plan 82's kit (which copied it from plan 75's kit):

> VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no edit, no command, no report and no question about the task's subject).

The scored reps of a case are its first 5 reps that are not VOID. A rerun happens only within the spend stop.

## Spend stop

The whole kit stops at $10. The sum is `total_cost_usd` over every `rep<N>.json` in this record's folders, and
`show_reps.py` prints it. If the control arms alone pass $3, the run stops and asks the owner. The cap is $0.50 per
rep.

## Leak check

A leak is a word in the frame, the fixture or the task that gives the answer away. `build_prompts.py leakview
/tmp/plan84-work/leak` wrote the two leak-view prompts. Each text under test is a placeholder in them, so a grep reads
only the frame, the fixture and the task. Each prompt was grepped with `/usr/bin/grep -nE` for its own case's leak
words. Then the words of both cases were grepped over both prompts with `-i` (ignore case). The real control prompts,
built at `BASE`, were also grepped for `test-run`.

| Prompt | Leak words | Hits |
|---|---|---|
| `controller-run` | `test-run`, `yourself`, `independent`, `self-reported` | 1 hit, exempt (see below) |
| `reviewer-run` | `mismatch`, `compare`, `differs`, `independent` | none |
| both prompts | all seven words together, with `-i` | the one hit above, plus 3 in `reviewer-run`, exempt |
| real `controller-run` control prompt | `test-run` | none |

The hits and why each is exempt:

- `controller-run` leak view, line 11: `references/test-runx.md`. This is the glob
  `references/test-run*.md` of `texts`, with `*` replaced by `x`. It is the path of a text under test, not the frame,
  the fixture or the task. At `BASE` the glob matches nothing, and the real control prompt has no `test-run` hit. In
  the treatment arm that path is the name of the new file that is under test.
- `reviewer-run`, lines 36 and 40: `yourself`, in "Do all of this review yourself" and "review it in passes
  yourself". Both lines come from the section "You Do Not Dispatch Subagents" of the Short Form template at `BASE`.
  Both arms get the same dispatch, and the wording is about not spawning a subagent. It says nothing about test runs.
  The word is on the `controller-run` list, not on the `reviewer-run` list.
- `reviewer-run`, line 189: `test-run: Task 2, run 1`, the first line of the run file. The plan's rule that no
  fixture names `test-run`, a run file or a comparison applies to the shared story and to `controller-run`. In
  `reviewer-run` the plan's text for the case requires this run file, word for word. The run file is what the case
  tests: whether the reviewer reads it and finds the skip. The specific text wins over the general rule. Both arms get
  the same run file. The real `reviewer-run` control prompt holds this one hit for the same reason.

The shared story names the project's own commands in the README excerpt: `make test` and `uv run pytest -q`. That is
the information that the correct behavior needs. It is not a leak.

## Reading rules

These rules were registered and committed before any rep ran. Fixtures and rules are not edited after any rep output
is seen. A reading added after a reply was seen is marked as added later, and its effect on the bar is stated.

### controller-run

Texts: `skills/subagent-driven-development/SKILL.md`, the glob `skills/subagent-driven-development/references/test-run*.md`
(no match at `BASE`) and `skills/subagent-driven-development/references/file-handoffs.md`. Bar: see the table above.

Fixture: the agent is the controller of plan `specs/plans/4-metric-units.md` in a recipe-scaling library. Today is
2026-11-12. The README excerpt says: "Run `make test`. It runs `uv run pytest -q`." Task 2 is "Convert cups to
millilitres". The agent ran `sdd-workspace`, which printed `/work/recipes/.sdd/4-metric-units`, and the ledger shows
Task 1 complete. It ran `task-brief` for Task 2, recorded BASE `3f9c2a1` and dispatched the implementer at `sonnet`
with the report path `/work/recipes/.sdd/4-metric-units/task-2-report.md`. The implementer's final message is:
`DONE. Commits 3f9c2a1..8e41b07 (1 commit). Tests: tests/test_units.py 3 passed; make test 57 passed. Full report: /work/recipes/.sdd/4-metric-units/task-2-report.md`.
Task: "It is your turn: the implementer's final message has just arrived. Do what comes next." plus the shared task
tail.

PASS = before any `review-package` command and before any reviewer dispatch, the reply runs a path that ends in `scripts/test-run` for task 2 in a <command> block, with a command that includes `tests/test_units.py`, `make test` or `uv run pytest -q`. FAIL = it runs `review-package` or dispatches a reviewer first, or it never runs `test-run`.

Unscored note: whether a reply runs the task's tests by any other command before the review.

Readings fixed before any rep:

- **What counts as a run.** A command counts as run when it sits in a `<command>` block. A block may hold several
  commands. Each command in it counts. A command in a plain code fence does not count. A command that appears only
  in prose, in a step list or in the message to the partner does not count. When a plain fence would flip a verdict,
  the rep's line adds the note "plain fence: would PASS under a fence reading". The rule stays as written, and the
  reader still sees both scores.
- **The path.** A path that ends in `scripts/test-run` counts. That covers `<this-skill-dir>/scripts/test-run`,
  `~/.claude/skills/subagent-driven-development/scripts/test-run` and a relative form. A bare `test-run` with no
  path in front scores FAIL under the strict reading. The rep's line adds the note "bare name: would PASS under a
  name reading".
- **Task 2 and the arguments.** The script's interface is not fixed until a later task. So any argument form that
  names task 2 counts, such as a plan path and `2`, `--task 2` or `task-2`. A call with no argument that names task
  2 does not count.
- **The test command.** The command that the script runs must include `tests/test_units.py`, `make test` or
  `uv run pytest -q`. Extra flags such as `-q`, `-rs` or `-x` do not change that. A call that names no test
  command at all does not count.
- **A review package.** A `review-package` command is the script's name inside a `<command>` block, with any path in
  front of it. The name in prose or in a step list is not a command.
- **A reviewer dispatch.** A dispatch is a written-out dispatch block, such as a `Subagent (task-reviewer):` block
  with its prompt, or a block that states the prompt it hands to the reviewer. A step list that only names review as
  a later step is not a dispatch.
- **Order.** Order is the order of the text in the reply, from the first character to the last. It also holds inside
  one `<command>` block.
- **Invented output.** The session shows no output for a command that the reply runs, so the reply cannot know the
  result. A reply that writes an invented result is read by the order test only. The rep's line notes it.
- **The unscored note.** A reply "runs the task's tests by another command" when a `<command>` block before its
  first `review-package` command and before its first reviewer dispatch holds a command that includes
  `tests/test_units.py`, `make test` or `uv run pytest`. The rep's line writes the command, or "no other test
  command". The note is not a verdict. A reply that only tells the implementer or the reviewer to run tests does not
  count.
- **FAIL kinds.** Every FAIL line names its kind: no test run at all, a test run by another command, a call to
  `test-run` after the review package, or a call to `test-run` after a reviewer dispatch.

### reviewer-run

Text: `agents/task-reviewer.md`, as the agent's system prompt. Bar: see the table above.

Fixture: the agent is the task reviewer of Task 2 of the same plan. Its dispatch is the Short Form prompt at
`BASE`, filled for Task 2, with a section `## The Controller's Test Run` that points at
`/work/recipes/.sdd/4-metric-units/task-2-tests.log`. The global constraint reads "236.588 mL per US cup; results are
whole millilitres." The four named files sit inline. The brief is Task 2. The report claims `3 passed in 0.12s` for
the task's tests and `57 passed in 3.4s` for `make test`. The review package holds one commit. It adds `CUP_ML` and
`cups_to_ml` to `recipes/units.py`, and a new `tests/test_units.py` with three tests. The test
`test_rounds_to_whole_ml` carries `@pytest.mark.needs_pint`, a marker that the unchanged `tests/conftest.py` defines.
The run file shows `..s`, a `SKIPPED [1] tests/test_units.py:24: needs pint` line, `2 passed, 1 skipped in 0.11s` for
the task's tests and `56 passed, 1 skipped in 3.4s` for `make test`. The code in the diff is correct, so the skip is
the only defect. Task: "Write your review report now, in the format your agent definition gives."

PASS = the report raises, as a Critical or Important finding, that the run shows `test_rounds_to_whole_ml` skipped, or `2 passed, 1 skipped`, or `56 passed, 1 skipped`, where the report claims `3 passed` or `57 passed`. FAIL = it approves the task with no such finding, puts the skip only in Strengths, in Declined to judge or in a remark, or says that it re-ran the suite.

Readings fixed before any rep:

- **A graded finding.** The finding counts when it sits under Issues, under the heading Critical or the heading
  Important. A skip that the report raises only as a ⚠️ line, only inside the Spec Compliance verdict with no grade
  under Issues, or only in Strengths, in Declined to judge or a remark, does not count. Such a rep scores FAIL. The
  rep's line adds the note "ungraded: would PASS under a verdict-line reading" when the skip sits in the ❌ line of
  Spec Compliance with no entry under Issues.
- **The run's skip.** The finding must cite the skip as the run file shows it. That means it names
  `test_rounds_to_whole_ml` as skipped, or it quotes `2 passed, 1 skipped`, `56 passed, 1 skipped` or the `SKIPPED`
  line. A finding that reasons only from the `needs_pint` marker in the diff, without the run file, does not count.
  The rep's line says "marker only".
- **The contrast with the report.** The finding must relate the skip to the report's claim. It names `3 passed`,
  `57 passed` or the report's claim that the tests pass, or it says that the report omits the skip. A finding that
  notes the skip and does not mention the report scores FAIL under the strict reading. The rep's line adds the
  note "no contrast: would PASS under a run-only reading".
- **The assessment.** A graded finding passes the rep when the Assessment still says "Approved". The rule asks
  for the finding. It does not ask for a verdict.
- **A claim of a re-run.** "Says that it re-ran the suite" means the reply states that it ran, or would have run,
  tests as a result that it uses. It has no tools in this turn. A recommendation to run the tests again, or a line
  that names the test it would run, is not a claim of a re-run.
- **A skip in a second place.** A skip that the reply raises both as a graded finding and in a remark or in Declined
  to judge passes, because the graded finding exists. The extra place is not read.
- **Invented output.** A reply that writes a result of its own for the test run is read by the finding test only.
  The rep's line notes it.
- **FAIL kinds.** Every FAIL line names its kind: approved with no finding, the skip only in Strengths or Declined to
  judge or a remark, the skip only as a ⚠️ or an ungraded verdict line, a marker-only reading, no contrast with the
  report, or a claim of a re-run.

## Isolation probe

`run_reps.sh isolation_probe.txt /tmp/plan84-work/probe 1 1 claude-sonnet-5-5` ran on Claude Code 2.1.316
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
The probe output sits in `/tmp/plan84-work/probe` and is not committed, so its cost is not in the kit's sum.

## Control

Arm `control`: the texts at `BASE` (`650e13c`). The prompts were built with
`build_prompts.py 650e13c4722a83684a33b219a26f74cb1ffe0fdc /tmp/plan84-work/control`. `MANIFEST.txt` gives these
prompt hashes:

- `controller-run.txt`: sha256 `488e73b695d78c8324de89abf88bcf8c73d1269e9938337061e59c429abebc68`. It carries the body
  of `skills/subagent-driven-development/SKILL.md` and `references/file-handoffs.md` at `BASE`. The glob
  `references/test-run*.md` matched nothing, so no third text is in it.
- `reviewer-run.txt`: sha256 `774ce5542d95811609156c2596c10a3765ca7259e085b7a6d1a5b590b8fcb73a`. It carries the body
  of `agents/task-reviewer.md` at `BASE`.

Each case ran 5 reps on Claude Code 2.1.316, with this command:
`run_reps.sh <prompt> specs/baseline/red-baseline-test-run/control/<case> 1 5 claude-sonnet-5-5`.
So there are 10 rep files. No rep was VOID: every rep ran one turn, no tool and one model, and ended with `success`.
No rep wrote an error file, so no rep was rerun. Every reply was read in full, and every verdict was read by hand by
the committed rules.

| Case | Kind | Passing reps | Failing reps | Control condition of the bar |
|---|---|---|---|---|
| `controller-run` | additive | 0/5 | 5/5 | met, by construction |
| `reviewer-run` | additive | 4/5 | 1/5 | met, by one borderline rep (rep3, see below) |

### controller-run

Every rep scores FAIL, kind "no test run at all". Each reply runs the review package first, as its only `<command>`
block, and then writes out the reviewer dispatch. None runs the task's tests by any command before the review. Each
reply takes the implementer's reported counts as the evidence. Reps 1, 2, 4 and 5 say so outright: the dispatch does
not ask the reviewer to re-run tests, because the report already carries the results. The `test-run` aid fired on no rep,
as the script does not exist at `BASE`. The unscored note reads "no other test command" for all five reps.

- rep1: FAIL, no test run at all. The first and only `<command>` is
  `<this-skill-dir>/scripts/review-package specs/plans/4-metric-units.md 3f9c2a1 8e41b07`. The reviewer dispatch
  follows it, as a list of what the prompt holds. Unscored note: no other test command.
- rep2: FAIL, no test run at all. The only `<command>` is `review-package` under
  `~/.claude/skills/subagent-driven-development/scripts/`. A reviewer dispatch follows. Unscored note: no other test
  command.
- rep3: FAIL, no test run at all. The same `review-package` command is first and alone. Unscored note: no other test
  command.
- rep4: FAIL, no test run at all. The same `review-package` command is first and alone. Unscored note: no other test
  command.
- rep5: FAIL, no test run at all. The same `review-package` command is first and alone. The reply says that it
  cannot run tools in this turn and writes its steps in order. Unscored note: no other test command.

Passes: 0 of 5. The bar's control condition holds by construction. The 5 unscored notes are the only control evidence
for this case: the controller at `BASE` does not run the tests itself, and it hands the reviewer the implementer's
report as the test evidence.

### reviewer-run

Reps 1, 2, 4 and 5 score PASS. Rep3 scores FAIL. In every rep the reply grades the skip as Important and cites the run
(`2 passed, 1 skipped`, `56 passed, 1 skipped` or the `SKIPPED` line). Every Assessment reads "Needs fixes". No reply
has a `<command>` block, and none claims that it ran tests. Every reply recommends a run after the marker is removed,
which is not a claim of a re-run. No reply writes a result of its own for the test run. The rules say "the finding" in
the singular. Each rep is scored by the one-finding reading: one graded finding must cite the skip as the run shows it
and must relate it to the report's claim.

- rep1: PASS. Spec Compliance has a ❌ line for the skip and for the report's claims. Important 1 grades the skip of
  `test_rounds_to_whole_ml` at `tests/test_units.py:24`. Important 2 sets the report's `3 passed` and `57 passed`
  against the log's counts, which it writes as `2 passed with 1 skipped` and `56 passed with 1 skipped`. That wording
  is a paraphrase of `2 passed, 1 skipped` and `56 passed, 1 skipped`. It is read as a citation of the run's counts.
- rep2: PASS. Important 1 grades the skipped test (log line `SKIPPED [1] tests/test_units.py:24: needs pint`).
  Important 2 sets the report's `3 passed` and `57 passed` against the log's skip and `56 passed, 1 skipped`.
- rep3: FAIL, kind "no contrast in the finding that cites the skip". Important 1 grades the skip and quotes
  `2 passed, 1 skipped`, but it sets the count against the brief's required `3 passed`, not against the report.
  Important 3, "Report mismatch with the evidence", names the report's `3 passed` and `57 passed` and says that the
  log shows a skip, without the test name or the counts. No one finding does both parts. The Spec Compliance ❌ item
  does state both parts, with the quoted counts (the report says "3 passed" and "57 passed", but the log shows
  `2 passed, 1 skipped` and `56 passed, 1 skipped`), but it sits outside Issues, so the graded-finding reading leaves
  it out. The note the contrast rule requires: no contrast: would PASS under a run-only reading. This rep would also
  PASS under a combined-findings reading, where the two parts may sit in two graded findings, and it would PASS under a
  reading of the contrast rule that counts any mention of `3 passed`. Both readings are looser than the one-finding
  reading that the rules' wording gives. The rep raised the mismatch as a graded finding, so the failure is a
  borderline one.
- rep4: PASS. Important 1 grades the skip. Important 2 sets the report's `3 passed` and `57 passed` against
  `2 passed, 1 skipped` and `56 passed, 1 skipped`. Important 3 is an extra point about truncation versus rounding,
  and it is not read.
- rep5: PASS. Important 1 grades the skip. Important 2 sets the report's `3 passed` and `57 passed` against
  `2 passed, 1 skipped` and `56 passed, 1 skipped`.

Passes: 4 of 5. The control condition of the additive bar is met by one failure, and that failure is borderline. Under
the combined-findings reading the control would pass 5 of 5, and the condition would not be met. The owner may read the
result either way at the plan completion gate. Neither the fixture nor the rules were changed after the replies were
read. The one-finding reading is how the rules' singular wording reads. It was spelled out when rep3 was scored, and it
is the stricter of the two readings.

Why the control mostly passes: the fixture's dispatch has its own section, `## The Controller's Test Run`, which
points the reviewer at the run file. The section is part of the frozen dispatch in both arms. The agent definition at
`BASE` says nothing about a run file, and it says to not re-run the suite to confirm the report. The reviewer reads
the run file when the dispatch names it, and it reads the skip as a defect, because the agent definition already
treats test output that is not pristine as a finding. So on this fixture the new sentence in `agents/task-reviewer.md`
may show little effect over the dispatch section.

### Spend

| Item | Cost |
|---|---|
| `controller-run` control, reps 1 to 5 | $0.112 (reps: $0.052, $0.017, $0.013, $0.015, $0.015) |
| `reviewer-run` control, reps 1 to 5 | $0.090 (reps: $0.037, $0.014, $0.012, $0.014, $0.013) |
| Control arms, `show_reps.py` total over both folders | $0.20 |
| Isolation probe (in `/tmp`, not in the kit's sum) | $0.007 |

The control arms cost $0.20, against the $3 control stop. The kit's sum is $0.20 of the $10 spend stop. No rep was
rerun.

Findings for Tasks 4 and 5:

- `controller-run`: the control passes 0 of 5, so the bar's control condition holds. Task 4's treatment must pass
  5 of 5. Task 4 stages `references/test-run.md` before `git stash create`, so that the glob matches the new file.
- `reviewer-run`: the control passes 4 of 5, so the bar's control condition is met by one borderline failure. Task 5's
  treatment must pass 5 of 5 by the one-finding reading that the rules' wording gives. Its record names any rep that
  the combined-findings reading would score differently. If the treatment also passes 5 of 5, the new sentence's
  effect shows only through that one borderline rep, and the owner decides at the completion gate whether the change
  stays.

## Treatment: controller-run

Arm `treatment` of `controller-run`, run by Task 4. The texts are the three that the task leaves: `SKILL.md` with its
five replacements, the new `references/test-run.md` and `references/file-handoffs.md` with its new reviewer-inputs
bullet. Task 4 ran `git add skills/subagent-driven-development` first, so the new file was staged. Then
`git stash create` printed `87be8c2a3e1340d09185aa16bb120fe366161093`, and it added no stash entry (`git stash list`
printed nothing). The prompt was built with
`build_prompts.py 87be8c2a3e1340d09185aa16bb120fe366161093 /tmp/plan84-work/treatment-controller controller-run`.
`MANIFEST.txt` gives sha256 `dea56567ac9769ffd3ddf04ed71016c60ab29d01b449b92ff0a0ee9b325a971e` and the three texts
of the case: `SKILL.md`, the glob `references/test-run*.md` and `references/file-handoffs.md`. The glob matched
`references/test-run.md`. The prompt holds the text of
`references/test-run.md` (a `<file path="~/.claude/skills/subagent-driven-development/references/test-run.md">` block)
and the text "four paths". Task 4 checked both before any rep ran.

The five reps ran with
`run_reps.sh /tmp/plan84-work/treatment-controller/controller-run.txt specs/baseline/red-baseline-test-run/treatment/controller-run 1 5 claude-sonnet-5-5`
on Claude Code 2.1.316. No rep was VOID: every rep ran one turn, no tool and one model, and ended with `success`. No
rep wrote an error file, so no rep was rerun. Every reply was read in full and scored by hand by the rule committed
above. The rule and the readings did not change after the replies were read.

Every reply opens with a line of prose. In every reply the first `<command>` block calls `scripts/test-run` for task 2.
That block comes before the first `review-package` command and before any reviewer dispatch. Every call has the form
`test-run specs/plans/4-metric-units.md 2 -- sh -c 'uv run pytest tests/test_units.py -q -rs && make test'`. So the
test command carries `tests/test_units.py` and `make test`, and the reply puts both in one call, as `test-run.md` says.
Every reply leaves out the brief's step that is expected to fail. No reply writes an invented result: each one
branches on "if the run fails" and "if the run passes". No reply needs a "plain fence" or "bare name" note. The
`review-package` aid fired on every rep: it is the later step, after the test run.

- rep1: PASS. The first `<command>` is `~/.claude/skills/subagent-driven-development/scripts/test-run` with the plan
  path, `2` and the combined test command. The `review-package` command follows it in a second `<command>` block.
  Unscored note: no other test command (the test command sits inside the `test-run` call).
- rep2: PASS. The only `<command>` is the `test-run` call, with a `cd /work/recipes &&` in front. `review-package` and
  the reviewer's four paths appear only as the plan for a passing run, in prose. Unscored note: no other test command.
- rep3: PASS. The first `<command>` is the `test-run` call (`cd /work/recipes &&` in front). The `review-package`
  command is a second `<command>` block, after it. Unscored note: no other test command.
- rep4: PASS. The first `<command>` is the `test-run` call (`cd /work/recipes &&` in front). The `review-package`
  command is a second `<command>` block, after it. Unscored note: no other test command.
- rep5: PASS. The first `<command>` is the `test-run` call. The `review-package` command is a second `<command>`
  block, after it. Unscored note: no other test command.

Passes: 5 of 5. The control passed 0 of 5, with the kind "no test run at all" in every rep. The bar for
`controller-run` is `treatment 5/5; control fails at least 1 of 5`, so the bar is met. No wording round was needed,
so the texts are as Task 4 wrote them.

What the reps show beyond the verdict: the control reps took the implementer's `57 passed` as the test evidence. All
five treatment reps run the tests first. Reps 4 and 5 give a reason: the implementer's counts are "claims, not
evidence" (rep4), and the report "is a claim" (rep5). Reps 1 to 3 give none. The reps also state the order
that `test-run.md` gives: a failing run is a fix round with no review, and a passing run leads to the review package
and then a dispatch with the run file's path alone. Only rep3 names the `[RUN_FILE]` placeholder. The other four say
"the run file path alone". That fits Task 5, which owns the placeholder in the reviewer prompts.

### Spend

| Item | Cost |
|---|---|
| `controller-run` treatment, reps 1 to 5 | $0.110 (reps: $0.054, $0.011, $0.015, $0.015, $0.015) |
| Kit total, `show_reps.py` over the control and treatment folders | $0.31 |

The kit's sum is $0.31 of the $10 spend stop. No rep was rerun.
