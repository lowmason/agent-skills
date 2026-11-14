# Change-reverted mutant: new tests must fail on the pre-change code — Design Spec

**Status: COMPLETE (2026-11-14)** — implemented by plan 97 (`specs/plans/completed/97-change-reverted-mutant.md`) and
retired here. APPROVED on 2026-11-13. The owner's question was "Do you approve the change-reverted mutant spec
(specs/change-reverted-mutant.md, uncommitted), with its 11 designer's calls?", and the owner answered "Approve it".

This design came from a brainstorming session on 2026-11-13. A side session ran it to design the backlog item "A
'change reverted' mutant, so that a task's new tests must fail on the pre-change code" (`specs/deferred_items.md:6255`).
A builder check read the draft, and the owner answered its one open question (D4). Decisions D1 to D4 are the
owner's. Text marked *(designer's call)* is the designer's choice, and "Designer's calls" lists each one. Line numbers are as of `99b876e`, the `main` commit this design read. All probes ran on throwaway
projects under `/tmp/revert-probe*/`. No repository was changed.

> **For agentic workers:** plan this with writing-plans. The micro-test in Verification is part of the plan, because
> the implementer and reviewer text shape behavior (writing-skills). No execution starts before plan 96's execution
> ends. Plan 96's controller uses `mutant-run`, `task-done` and the task reviewer live, through the symlinks into the
> main checkout.

## Terms

- **BASE:** the commit that a task's review range is cut from. The SDD controller records it before it dispatches the
  task's implementer (`skills/subagent-driven-development/references/file-handoffs.md:57-59`). executing-plans'
  `task-start` prints it. Fix rounds keep it, and a batch uses the batch's BASE.
- **Revert:** the reverse of the task's diff from BASE to HEAD, over each changed path except test files and project
  config files (Design 2). It puts the task's code back as it was at BASE and keeps the tests at HEAD. No agent writes
  or picks it.
- **Agent mutant:** a mutant that the implementer writes, as plan 93 defines "Mutant"
  (`skills/subagent-driven-development/references/mutants.md:9`).
- **Fails on the revert:** with the revert applied, a test fails or errors. A test also fails on the revert when its
  file cannot load, or when the revert makes it skip. Any cause counts, a missing import included. A test that cannot run without the change needs the change.
- **Passes on the revert:** with the revert applied, the test passes. When the task adds or changes that test, the
  test does not test the change, unless it checks old behavior that the task keeps.
- **Did not run on the revert:** the test has no entry in the revert run's report. An earlier failing step stopped
  the command, or pytest stopped early (`-x`, `--maxfail`). It is a gap in the controller's run, not evidence about
  the test.
- **`Keeps:` line:** a line in the mutants file, `Keeps: <test> — <the behavior from before the task that it checks>`,
  for a test that passes on the revert by design.
- **`Strengthened:` line:** a line in the mutants file, `Strengthened: <plan test> — by <new test>`, for a plan test
  that passes on the revert. The new test fails on the revert and checks the behavior that the plan test should have
  caught (D4).
- **Project config file:** a file whose change makes the test command rebuild or re-sync its environment, or that
  holds pytest's own settings. Design 2 lists them.

Mutant task, caught, survived, invalid and stated rule keep plan 93's meanings
(`specs/completed/mutant-checked-tests.md:15-32`).

## Intent

Plan 93 made each task prove that its tests can fail. An implementer writes mutants from the stated rules, and
`mutant-run` proves that the tests catch each one. But one claim stays unchecked. The implementer's report says that
each new test failed before the code existed ("TDD Evidence", RED,
`skills/subagent-driven-development/implementer-prompt.md:160-161`). Nothing reruns the new tests on the code as it
was before the task.

A test that passes on the pre-change code does not test the change. This matters most in a bugfix: a regression test
that passes on the buggy code proves nothing about the fix. Plan 93's agent mutants do not find it. They change the
code after the task, and a test can catch them by checking behavior that the old code shared.

The idea comes from Eric J. Ma's post "The understanding zeitgeist in AI code review" (2026-07-24,
https://ericmjl.github.io/blog/2026/7/24/understanding-zeitgeist-ai-code-review/), section "What breaks at the pull
request". When one agent writes both the code and its tests, a passing test is weak evidence. So the post asks for a
test that fails on the pre-change behavior. Only the idea is taken, by citation.

## Evidence (probes, 2026-11-13)

The backlog item left four questions open. Probes on throwaway pytest projects answered the parts that depend on how
pytest and uv behave. The table shows what pytest's JUnit report records for each case on a revert.

| Case on the revert | Exit | JUnit report |
|---|---|---|
| A test body imports a module or a name that is missing | 1 | `<failure message="ImportError: cannot import name …">` |
| A test calls a module attribute that is missing | 1 | `<failure message="AttributeError: module … has no attribute …">` |
| A test passes a new keyword argument | 1 | `<failure message="TypeError: … unexpected keyword argument …">` |
| A test runs a new script in a subprocess | 1 | `<failure message="FileNotFoundError: …">` |
| A test file imports missing code at its top | 2 | One `<error message="collection failure">`. The session stops, and no test in any file runs. |
| The same, with `--continue-on-collection-errors` | 1 | The collection error, and the results of every other file |
| Only collection errors, with that flag | 1 | The collection errors, and no failed test |
| A `conftest.py` imports missing code | 4 | No report file |

Three findings follow:

- **No filter by exception type can tell "the code is missing" from "the behavior differs".** A missing name shows
  as `ImportError`, `AttributeError`, `TypeError` or `FileNotFoundError`, and real behavior raises each of these too.
  `mutant-run` reads each row with exit 1 and a `<failure>` as CAUGHT
  (`skills/subagent-driven-development/scripts/mutant-run:576-578`). So the item's question 1 holds, and it is wider
  than imports.
- **A top-level import of new code stops the whole run.** Without the flag, one file that cannot load hides the
  results of every other file.
- **A revert of `pyproject.toml` and `uv.lock` under `uv run` changes `.venv`.** A probe dropped a dependency at HEAD,
  then ran `uv run` with the BASE manifest and lockfile in place. uv installed the dropped package, and the package
  stayed installed after the files were put back. `uv run` syncs without removing extra packages, so the change
  outlives the run. `mutant-run`'s tree check compares tracked files only (`mutant-run:242-249`), so it cannot see
  this change.

## Goals, non-goals and anti-goals

**Goals.**

- In a mutant task, each test that the task adds or changes fails on the revert, or carries a `Keeps:` line that
  holds (D1). A plan test may carry a `Strengthened:` line that holds instead (D4).
- In a mutant task whose brief states a behavior change, at least one test fails on the revert.
- A script, not an agent's report, records which tests fail on the revert.
- The same check runs under subagent-driven-development and executing-plans.

**Non-goals.**

- Tasks that are not mutant tasks: prose, skill text, and tasks with no focused pytest command. Plan 93's D1 left
  prose out, and this design does too.
- A script that tells a missing-code failure from a behavior failure (Evidence).
- A fix round before review for the revert. The reviewer rules on it (D2).
- Spec-derived acceptance tests and a second test-writing agent (plans 81 and 83).
- Any change to agent-mutant verdicts, to the `result:` line, or to `mutant-run`'s exit status.

**Anti-goals.** Each of these makes the design a failure, even if it works:

- A revert result enters the `result:` line, a `mutant K:` line or the `--- tests ---` section. Then `task-done`'s
  gate or reviewer check 4 would read a missing-code failure as a catch.
- A revert run that ran nothing reads as a clean result.
- The revert leaves state behind: a changed tracked file, a marker, or packages that the BASE manifest installed.
- `skills/subagent-driven-development/SKILL.md` grows.

## Approaches

**What the revert proves (D1).** The session weighed two targets:

1. **Each test that the task adds or changes fails on the revert.** Chosen. It matches the item's own sentence: "A new
   or changed test that passes on it does not test the change." Any failure counts, so a new-code task needs no
   exemption, and question 1 goes away. A test that checks kept old behavior gets a `Keeps:` line.
2. **At least one test fails on the revert.** The revert reads like an agent mutant. One missing-code failure
   satisfies it, and a weak regression test can hide behind another test's failure. A new-code task whose test file
   imports the new module at its top reads INVALID, so this target needs a bugfix-only scope.

**Who acts on a test that passes on the revert (D2).** A script cannot tell an old test from a changed one, because a
changed test keeps its name. The reviewer already finds the new and changed tests in the diff, for check 4. The
session weighed two ways:

- **A. The script records, and the reviewer rules.** Chosen. `mutant-run` records each test that fails on the revert.
  The implementer checks its own tests against that list before it reports. The reviewer grades a new or changed test
  that passes on the revert as Important, unless a `Keeps:` line holds. `task-done` checks only that the revert ran
  at the task's BASE. This keeps plan 93's split: a script decides what a script can decide, and the reviewer judges
  the rest. Cost: a miss that the implementer overlooks costs a review round, and an inline run relies on the final
  review.
- **B. The implementer lists its tests, and a script blocks.** The mutants file lists each test that the task adds or
  changes, by exact test ID. `task-done` and the controller block before review when a listed test passes on the
  revert with no `Keeps:` line. It gives a mechanical block, for inline runs too. But it adds an exact-ID list to keep
  up and more parsing in `task-done`, and the reviewer must still check that the list is complete.

Dropped before the comparison: a script that finds the new tests by comparing the test IDs collected at BASE and at
HEAD. It misses changed tests, and it would have to put the BASE test files in place too.

## Owner decisions (2026-11-13)

- **D1. Each test.** Asked "must EACH new or changed test fail on that pre-change code, or is it enough that at least
  one test fails?", the owner chose "Each test".
- **D2. Approach A.** Asked who acts when a new or changed test passes on the pre-change code, the owner chose "A:
  reviewer rules".
- **D3. A revert-only reading of collection errors.** The owner was asked about the revert run only. May
  `mutant-run` add `--continue-on-collection-errors` to it, and read a test file that cannot load as "its tests need
  the change"? Agent-mutant verdicts would not change. The owner chose "Yes, revert-only". Plan 93's rule that a
  collection error makes an agent mutant INVALID stays as it is.

The owner then approved the played-back design: "Looks right, write it".

- **D4. A new test clears a weak plan test.** The builder check found a gap. Plan 93 lets an implementer strengthen a
  plan test only in a new test (`references/mutants.md:93`). So a weak plan test keeps passing on the revert, and no
  edit can clear it. Asked what clears check 7 for it, the owner chose "A new test clears it". The implementer adds a
  new test that fails on the revert, and it writes a `Strengthened:` line. The other option was a plan-mandated finding
  and a controller `Ruling:` for each weak plan test.

## Design

### 1. BASE reaches `mutant-run` as an argument (question 3)

*(Designer's call)* BASE becomes a required argument, in the place where `task-done` takes it:

`<this-skill-dir>/scripts/mutant-run PLAN_FILE N BASE -- TEST_COMMAND [ARGS...]`

- The script refuses (exit 2) a BASE that is not a commit, and a BASE that is not an ancestor of HEAD, as
  `review-package` does (`skills/subagent-driven-development/scripts/review-package:26-31`). A BASE equal to HEAD is
  allowed. Its diff is empty, so the revert reads `none` (Design 2).
- The run file gains a header line, `base: <full sha>`, right after `head:`.
- **SDD controller.** It passes the BASE that it recorded before the first dispatch. Fix rounds and re-reviews reuse
  it, so the revert always covers the whole task, never only the last fix. A batch uses the batch's BASE.
- **SDD implementer.** It runs the script itself (`references/mutants.md:34`). So the dispatch gains a `[BASE]`
  placeholder, filled with the full SHA, beside `[MUTANT_RUN]` (`implementer-prompt.md:185-194`,
  `references/file-handoffs.md:20-25`).
- **executing-plans.** The inline executor passes the BASE that `task-start` printed
  (`skills/executing-plans/SKILL.md:252`).
- **The checks.** `task-done` refuses a run whose `base:` is not its own BASE (Design 6). The task reviewer and the
  re-reviewer compare `base:` with the review range's BASE. A mismatch is a gap in the controller's run, as a stale
  `head:` is today.

An argument is explicit at each call, and two independent readers check it. A file written when the brief is
extracted would be hidden from the reader, and a rerun of `task-brief` partway through a task could move it.

### 2. The revert patch

*(Designer's call)* After the last agent mutant, the script builds the revert:

1. List the paths that changed from BASE to HEAD: `git diff --no-renames --name-only BASE HEAD`. With renames off, a
   rename is a deletion and an addition, and each is reverted on its own.
2. Drop the test and fixture paths, with `is_test_path` (`mutant-run:408-422`).
3. Drop the project config files, matched by base name at any depth: `pyproject.toml`, `uv.lock`, `uv.toml`,
   `.python-version`, `requirements*.txt`, `setup.cfg`, `pytest.ini` and `tox.ini`. These files rebuild or re-sync the
   environment (Evidence), or they hold the pytest settings that the tests at HEAD rely on.
4. When no path is left, write `revert: none: <why>` and run nothing. An example is "the task changed only tests and
   project config".
5. Otherwise, write the patch with `git diff --no-renames --binary HEAD BASE -- <paths>` to a file in the workspace.
   Its name must not match the agent-mutant glob `task-<N>-mutant-*.patch`. With `--binary`, deletions, additions,
   binary files and mode changes all round-trip.

The revert runs on the agent mutants' machinery (`mutant-run:553-566`). The script writes the marker, applies the
patch, runs the command, reverses the patch, removes the marker and checks the tree. The next run recovers a killed
run from the marker, as today. Three things differ:

- The "already in HEAD" check (`mutant-run:297-302`) does not apply to the revert, which is built from HEAD.
- The revert's `.py` files join the bytecode purge (`mutant-run:424-462`), so no run loads stale bytecode.
- The revert run adds `--continue-on-collection-errors` to `PYTEST_ADDOPTS`, beside the JUnit option (D3).
  Agent-mutant runs do not get it.

The revert has the agent mutants' time limit.

### 3. Reading the revert

*(Designer's call)* The revert gets no CAUGHT, SURVIVED or INVALID verdict. The script reads its JUnit report one
test case at a time, and it lists every test case with one of four outcomes:

- **Failed:** a `<testcase>` that holds a `<failure>`, or an `<error>` other than a collection failure or an internal
  error. The existing reader counts the same cases (`mutant-run:367-399`).
- **Not loaded:** a collection failure. pytest writes it as a `<testcase>` with an empty `classname` and the module's
  dotted path as its `name`, holding `<error message="collection failure">`. Every test in that file needs the change
  (D3). The baseline at HEAD passed first, so the revert caused any load failure.
- **Skipped:** a `<testcase>` that holds a `<skipped>`, with its reason. A skip that the revert caused, such as an
  `importorskip` of new code, counts as failing on the revert. Any other skip counts as did not run.
- **Passed:** any other test case.

The list holds passed tests too, although most are old tests that pass on old code. Without them, a reader cannot
tell a new test that passed from one that did not run. The builder check found three ways for a test not to run. A
`&&` chain stops at its first failing step. `-x` or `--maxfail` stops pytest early. A skip hides the test. So a
test with no entry did not run, and only the reviewer, who knows which tests are new, can say whether that matters.

The revert never changes the `result:` line, a `mutant K:` line, the `--- tests ---` section or the exit status
(anti-goals).

### 4. The run file

The header gains two lines. `base:` follows `head:`, and `revert:` follows `result:`, or the `note:` line when there
is one:

```text
mutant-run: Task 4, run 2
command: uv run pytest -q tests/test_scan.py
head: <full sha>
base: <full sha>
tree: clean
result: caught 3, survived 0, invalid 0
revert: ran, exit 1, failed 1, not loaded 1, skipped 0, passed 2
--- mutants ---
mutant 1: CAUGHT exit 1 sha256 <hex> tests: tests.test_scan::test_plain_fence
--- tests ---
test tests.test_scan::test_plain_fence: caught 1
--- revert ---
paths: src/scan.py src/newmod.py
sha256: <hex>
failed tests.test_scan::test_quoted_fence: AssertionError: assert ['x'] == []
not loaded tests.test_newmod: ImportError: cannot import name 'newmod' from 'src'
passed tests.test_scan::test_plain_fence
passed tests.test_scan::test_span
--- output: baseline ---
--- output: mutant 1 ---
--- output: revert ---
```

The `revert:` line takes one of these forms:

- `revert: ran, exit <n>, failed <f>, not loaded <u>, skipped <s>, passed <p>`, when the run wrote a JUnit report.
- `revert: ran, exit <n>, no report`, when the run wrote none, for example when a `conftest.py` cannot load (exit 4).
- `revert: timeout after <n>s`.
- `revert: not applied: <reason>`. The patch is built from HEAD on a clean tree, so this should not happen. If it
  does, the script records it and goes on.
- `revert: none: <why>` (Design 2).

The existing readers stay intact:

- `task-done` takes the first `head:` after line 1, and the first `result:` between `head:` and the first `---`
  (`skills/executing-plans/scripts/task-done:190-198`). Neither `base:` nor `revert:` matches either reader.
- Its `ran` reader takes `mutant K:` lines from `--- mutants ---` only (`task-done:207-211`). The revert section's
  lines start with `paths:`, `sha256:`, `failed `, `not loaded `, `skipped ` or `passed `, never with `mutant ` or
  `test `.
- Reviewer check 4 reads `test <id>: caught K` lines, and the revert writes none.

A failing baseline stops the run before any mutant, as today, so its run file has no revert section. Its header still
carries `base:`.

### 5. The implementer's step (`references/mutants.md`)

The guide gains:

- **Terms:** Revert, Fails on the revert, Did not run on the revert, and the `Keeps:` and `Strengthened:` lines.
- **The call:** step 5's command gains BASE (`mutants.md:34`). The command starts pytest once, with no `-x` and no
  `--maxfail` (Design 8).
- **A new step, once the run shows no survivor and no invalid mutant:** read the revert section. Each test that the
  task adds or changes, plan tests included, must fail on the revert (Terms). A test with no entry did not run: run
  the script again on a command that runs it. For a test that passed on the revert, take one of three paths:
  - It is a test that the task wrote, and it checks behavior that the task changes. Strengthen it, or add a test, so
    that it fails on the old code. Then commit and run again.
  - It is a plan test, and it checks behavior that the task changes. Leave it as the plan wrote it. Add a new test
    that checks the same behavior and fails on the old code, commit, run again, and write
    `Strengthened: <plan test> — by <new test>` (D4).
  - It checks behavior from before the task that the task keeps on purpose, such as the normal case beside a bug's
    fix. Write `Keeps: <test> — <the behavior it checks>`.
- **A check before a `Keeps:` line,** in the style of the checks for `Unproven:` and `Withdrawn:`
  (`mutants.md:59-63`). Read the brief and the excerpts. If the task changes the behavior that the test checks, the
  test is weak: strengthen it, and write no line.
- **The mutants file form** gains the `Keeps:` and `Strengthened:` lines, which start at column 0 like the others.
- **Reading the run** gains the revert section and its `revert:` forms. For a `no report` or `timeout` revert, read
  the revert's output. A task whose tests all need the change, such as one whose `conftest.py` imports new code, needs
  nothing more.

The SDD implementer's report gains no new field, because it already gives the last run's path.

### 6. executing-plans and `task-done`

- The command at `SKILL.md:252` gains BASE. The body has room: 17,935 characters against the register's window of
  19,700.
- *(Designer's call)* `task-done`'s gate gains two refusals (exit 4), after its `head:` check:
  - The run has no `base:` line, or its `base:` is not the commit that `task-done`'s BASE argument names. Both are
    resolved to full SHAs before they are compared.
  - The run has no `revert:` line in its header.

  `task-done` does not read the revert's outcome, which needs the reviewer's judgment (D2). `revert: none: …` passes.
  `--no-mutants` skips the whole gate, as today. The completion line does not change.
- The mutant check list in `references/final-review.md` (`:36-61`) gains a **Revert** item with the content of
  reviewer check 7 (Design 7). The review already reads each task's newest run file, which holds the revert section.
  Each run's `base:` is the first SHA of its task's ledger line, as its `head:` is the second (`:63-64`).

### 7. The task reviewer (check 7) and the re-reviewer

The `## Mutants` section gains a check 7, in `task-reviewer-prompt.md` and `agents/task-reviewer.md`. It goes after
check 6, so the existing numbers stay. Its content:

7. **Each test that the task adds or changes fails on the revert,** plan tests that the task writes included. A test
   fails on the revert when the revert section lists it as failed or lists its file as not loaded. A skip that the
   revert caused counts too. A test with no entry did not run: that is a gap for the controller, not a finding. A
   test that passes on the revert needs a `Keeps:` line or, for a plan test, a `Strengthened:` line that holds. A `Keeps:` line holds when the test checks behavior that exists at BASE and that the task keeps. It
   never holds for behavior that the brief or the excerpts change. A `Strengthened:` line holds when its new test
   fails on the revert and checks the behavior that the plan test should have caught. A test with no line that holds
   is a finding: name the behavior that it should have caught on the old code. Also check a task whose brief states a
   behavior change. If its revert section shows no failed test and no file not loaded, no test checks the change, and
   that is a finding. A `revert: none: …` line holds when the diff changes only test files and project config files.
   Read a `no report` or `timeout` revert from its output. A `conftest.py` that cannot load means that every test needs
   the change. Any other cause is a gap for the controller.

The grading paragraph after check 6 already grades each finding in the section as Important. It also keeps the shared
block's last pass from deleting them. So it covers check 7 with no change. The section's description of the mutant
run gains the `base:` line and the revert section. The `[MUTANT_RUN_FILE]` placeholder's command
(`task-reviewer-prompt.md:471`) gains BASE. The `## Mutants` section stays outside the shared reviewer block
(`build/check_reviewer_block.py`), so the four shared copies do not change.

The re-review prompt (`skills/subagent-driven-development/re-review-prompt.md:38-56`) gains the same check for each
test that the fixes add or change. Its `<MUTANT_RUN_FILE>` comes from a run with the task's BASE.

### 8. The controller (`references/test-run.md`, `references/file-handoffs.md`)

- The `mutant-run` call gains BASE (`test-run.md:19`). Fix rounds keep the task's BASE.
- *(Designer's call)* The focused command for `mutant-run` starts pytest once, with no `-x` and no `--maxfail`.
  `test-run.md:21` joins the brief's `Run:` steps with `&&`. On the revert the first step nearly always fails, so the
  later steps never run. Agent mutants lose nothing from this, but the revert does. `PYTEST_ADDOPTS` cannot undo a
  `-x` in the command, because pytest reads `PYTEST_ADDOPTS` before the command line. When the brief's steps run
  pytest more than once, the controller writes one pytest call that runs the tests of every step. The test-run call
  keeps the brief's steps as they are.
- **A limit.** Some tasks have new tests in two suites that one pytest call cannot run, such as two
  directory-scoped suites with different dependencies. The second suite's tests then do not run on the revert, and
  the reviewer reads them as did not run.
- The exit-status reading does not change, because the revert never changes the exit status.
- "Check the run" gains the `base:` line beside `head:`. A `base:` other than the recorded BASE is a gap in the
  controller's own run.
- The dispatch list in `file-handoffs.md` gains `[BASE]`. The reviewer's placeholders already carry `[BASE_SHA]`
  (`task-reviewer-prompt.md:478`).
- `references/fix-loop.md:25` ("run mutant-run again") needs no change.

### 9. Where the text goes

- `skills/subagent-driven-development/scripts/mutant-run`: Designs 1 to 4, with its header comment. Its tests go in
  `scripts/test_sdd_scripts.py`, where the usage test (`:1453`) and every existing call gain BASE.
- `skills/subagent-driven-development/`: `references/mutants.md` (Design 5), `implementer-prompt.md` (`[BASE]`),
  `task-reviewer-prompt.md` and `re-review-prompt.md` (Design 7), and `references/test-run.md` and
  `references/file-handoffs.md` (Design 8).
- `agents/task-reviewer.md`: check 7, then the adapters under `runtimes/`, which `build/sync_runtime_assets.py`
  regenerates.
- `skills/executing-plans/`: `SKILL.md:252`, `references/final-review.md` and `scripts/task-done` (Design 6).
  `task-done`'s tests go in `scripts/test_executing_plans_scripts.py`, whose run-file writer (`:128-150`) gains
  `base:` and `revert:` lines.
- `skills/subagent-driven-development/SKILL.md`: **no change**.
- `NOTICE`: one change line under the superpowers entry, after plan 93's line (`NOTICE:1010-1026`). It cites the post
  as the idea's source, by citation only, in the form of the existing Eric J. Ma citation (`NOTICE:289-297`)
  *(designer's call)*.

## Verification

1. **The script, test first.** In `test_sdd_scripts.py`, each of these fails before the change, then passes:
   - A call with no BASE is refused with the new usage line. A BASE that is not a commit is refused, and so is a BASE
     that is not an ancestor of HEAD.
   - A test that needs the task's code change is listed as failed in the revert section. A test that the task adds
     and that passes on the old code is listed as passed. A test that `importorskip`s a module that the task added is
     listed as skipped, with its reason.
   - A test file that imports a module that the task added is listed as not loaded, and the tests in the other files
     still run.
   - Test files and project config files stay at HEAD during the revert. A change to `pyproject.toml` is not
     reverted.
   - A task that changed only tests gets `revert: none: …`.
   - The revert never changes the `result:` line, a `mutant K:` line, the `--- tests ---` section or the exit status.
   - A task that deletes a file and adds an executable script round-trips: tracked files equal HEAD after the run.
   - A run killed while the revert is applied is recovered by the next run, from the marker.
   - The header has `base:` after `head:`, and `revert:` after `result:`.
2. **`task-done`, test first.** A missing `base:`, a `base:` that is not BASE, and a missing `revert:` line each block
   the completion line with exit 4. `revert: none: …` passes. A short BASE argument matches the run's full `base:`.
   Every existing gate test still passes.
3. **A micro-test of the implementer text and of reviewer check 7,** by writing-skills' method, against a control arm.
   The control arm gets today's text, with only BASE added to the `mutant-run` call. The script lands first, and it
   refuses a call with no BASE *(designer's call)*. Both arms get run files with the revert section. The
   fixtures are synthetic, and no code is copied from any repository:

   | Fixture | What it holds | Bar for the treatment arm |
   |---|---|---|
   | F6 | A bugfix whose plan-given regression test also passes on the buggy code | It leaves the plan test unchanged, adds a new test that the next run lists as failed, and writes a `Strengthened:` line, in at least 4 of 5 reps |
   | F7 | A bugfix with a second test that rightly checks the unchanged normal case | It writes a `Keeps:` line for that test and leaves the test unchanged, in at least 4 of 5 reps |
   | F8 | A pure new-code task whose new tests all fail on the revert by import | No `Keeps:` line and no test change, in at least 4 of 5 reps |
   | R4 | A task package whose new test passes on the revert, with no `Keeps:` line | An Important finding, in at least 4 of 5 reps |
   | R5 | The same test with a `Keeps:` line that holds | No revert finding, in at least 4 of 5 reps |
   | R6 | A pure new-code package with a file not loaded and import failures | No revert finding, in at least 4 of 5 reps |
   | All | — | No rep in either arm weakens a test |

   There are five reps per fixture per arm, with implementers and reviewers at **standard**: 60 reps, an estimated
   $15–40 *(designer's call)*. A control arm that meets a bar on F6, F7 or R4 means that the text adds nothing on that
   fixture. The results file reports it, and the owner rules before the text ships. F8, R5 and R6 guard against false
   alarms. Today's text knows nothing of the revert, so the control arm is expected to meet their bars. Those bars apply
   to the treatment arm only *(designer's call)*. When the treatment arm misses a bar, revise
   the wording and rerun only the failing fixtures, at most twice. Then stop for the owner. Stop at once if the total
   spend passes $60.
4. **The commit lints and the suites** that the change reaches (CLAUDE.md, Commands): `check_conformance.py`,
   `check_reviewer_block.py`, `check_helper_paths.py`, `sync_runtime_assets.py --check`, the dependency-drift test,
   and the subagent-driven-development and executing-plans suites.

The controller steps (Design 8) and the `task-done` gate get no micro-test, as in plan 93. The scripts and their tests
enforce the run and the gate.

## Constraints

- **SDD's SKILL.md does not grow.** Its body is past the register's window, under the waiver
  `subagent-driven-development-compaction-window` (`build/cc_guide/conformance.toml:796-802`). All new text goes into
  prompts, reference files and scripts.
- **Reviewer block.** Check 7 lives in `## Mutants`, outside the shared block, so `check_reviewer_block.py`'s four
  copies do not change.
- **Helper paths.** Every mention of `mutant-run` under `skills/` keeps its `<this-skill-dir>/` anchor
  (`build/check_helper_paths.py`).
- **Runtimes.** Run the adapter generator after the change to `agents/task-reviewer.md`.
- **Shells.** The script runs under macOS bash 3.2, with perl, as today.
- **Live tooling.** `~/.claude/skills` and `~/.claude/agents` are symlinks into the main checkout. So no execution
  starts before plan 96's execution ends, and the plan runs in a worktree. The plan changes scripts that its own
  executor runs, so it says which copy of `mutant-run` its controller calls while the script changes.
- **Provenance.** subagent-driven-development and executing-plans are adapted from superpowers (MIT,
  `LICENSE-superpowers`). This design adds original text and script code, and it takes one idea, by citation, from
  Eric J. Ma's post. No text from the post is reproduced.
- **Python style** for the tests: single quotes, Python as pinned in `build/versions.toml`.

## Left to the builder

- The exact wording of the guide, the reviewer check and the re-review text, within Designs 5 and 7, shaped by the
  micro-test.
- The exact layout inside the revert section, within Design 4's rules: the header lines, the section name, and line
  prefixes that never read as `mutant K:` or `test <id>:`.
- How the error line for a file not loaded is cut from the report. The `message` attribute holds only "collection
  failure", so the cause comes from the element's text.
- The workspace name of the revert patch file.
- Whether `mutant-run` builds the revert before the baseline, to refuse a bad BASE early, or after the agent mutants.
- How the micro-test kit reuses plan 93's kit (`specs/baseline/red-baseline-mutant-checked-tests/`).
- More project config file names, when a probe shows that another file re-syncs the environment.
- How the controller closes a did-not-run gap that one pytest call cannot close (Design 8's limit). One way is a
  second `mutant-run` call over the second suite, with both run files sent to the reviewer.

## Designer's calls

1. BASE reaches `mutant-run` as a required positional argument, in `task-done`'s place. The run file records it, and
   `task-done` and the reviewers check it (Design 1).
2. The revert leaves test files and project config files at HEAD, matched by base name, and it uses `--no-renames
   --binary` (Design 2).
3. The revert runs after the agent mutants, on their machinery and with their time limit. Only the revert run gets
   `--continue-on-collection-errors` (Design 2).
4. The revert gets no verdict. The script lists every test case in its report as failed, not loaded, skipped or
   passed. A test with no entry then reads as did not run (Design 3). The first draft listed failures only. The
   builder check showed that a test that never ran then looks like a test that passed.
5. The run file gains `base:` and `revert:` header lines and a `--- revert ---` section. The revert stays out of the
   `result:` line, `--- mutants ---`, `--- tests ---` and the exit status (Design 4).
6. The excuse line is `Keeps: <test> — <the behavior it checks>`, with a check before it is written. D4's line for a
   plan test is `Strengthened: <plan test> — by <new test>` (Design 5).
7. `task-done` checks that the revert ran at its BASE, and never reads the revert's outcome (Design 6).
8. Reviewer check 7 also flags a behavior-change task whose revert no test fails (Design 7).
9. The NOTICE line cites Eric J. Ma's post as the idea's source (Design 9).
10. The micro-test: six synthetic fixtures, 60 reps at standard, two revision rounds at most, and a $60 stop. The
    control arm gets today's text with BASE added to the call. The false-alarm fixtures F8, R5 and R6 bind the
    treatment arm only (Verification).
11. The focused command for `mutant-run` starts pytest once, with no `-x` and no `--maxfail` (Design 8).

## Backlog effects

- **"A 'change reverted' mutant, so that a task's new tests must fail on the pre-change code"**
  (`specs/deferred_items.md:6255`): this spec decides it. Its done-when, "a spec decides the change-reverted mutant
  and its plan lands", is met when the plan lands. Its four questions are settled as follows:
  - **Question 1** (an import in a test body reads as caught): D1 makes it moot, because any failure counts.
  - **Question 2** (bugfix and behavior-change tasks only?): every mutant task gets the revert (D1, Design 2).
  - **Question 3** (how BASE reaches `mutant-run`): Design 1.
  - **Question 4** (what the reviewer does with a revert that no test fails): D2 and Design 7.
