# Mutants

Read this after GREEN and the commit, in a mutant task, before you report.

A passing test proves little until a wrong version of the code makes it fail. Here you write wrong versions on purpose, and a script proves that your tests catch each one. The script also runs your tests once on the code as it was before the task, to show which tests need the task's change.

## Terms

- **Mutant:** a small patch that makes the task's code wrong in a way a person could plausibly write. An example is code that no longer blanks fenced blocks before it matches. It changes code, never a test or a test fixture.
- **Caught:** with the mutant applied, the task's focused tests fail. For pytest that is exit status 1, with a failed test in the run's JUnit report.
- **Input shape:** one form of input that a stated rule's words cover, such as a quoted, nested, empty or repeated form, or a value at a boundary.
- **Survived:** with the mutant applied, the tests pass. Some test is too weak, or an input is missing.
- **Invalid:** the patch does not apply, touches a test file, or makes the run fail for another reason (pytest exit 2, 3, 4 or 5: a collection error, an internal error, a usage error, no tests).
- **Stated rule:** a sentence in the spec, or in the task's own text, that says what the code must do for some class of inputs. An example is "a form inside code never matches".
- **Unproven test:** a test that the task adds or changes and that catches no mutant.
- **Mutant task:** a task whose brief has a focused pytest command that tests code the task changes. Lints, link checks and checks over Markdown do not count. A task that is not a mutant task skips this file and reports `mutants: none: <why>`.
- **Plan test:** a test whose code the plan gives. When this task writes it, it is a test the task adds, and every step below covers it.
- **BASE:** the commit that the task's review range is cut from, as a full SHA. Your dispatch gives it. Under executing-plans, `task-start` prints it.
- **Revert:** the reverse of the task's diff from BASE to HEAD, over each changed path except test files and project config files (`pyproject.toml`, `uv.lock`, `uv.toml`, `.python-version`, `requirements*.txt`, `setup.cfg`, `pytest.ini` and `tox.ini`, at any depth). It puts the task's code back as it was at BASE and keeps the tests at HEAD. The script builds it and runs the tests on it after the mutants. No agent writes or picks it.
- **Fails on the revert:** with the revert applied, a test fails or errors. A test also fails on the revert when its file cannot load, or when the revert makes it skip. Any cause counts, a missing import included. A test that cannot run without the change needs the change.
- **Passes on the revert:** with the revert applied, the test passes. When the task adds or changes that test, the test does not test the change, unless it checks behavior from before the task that the task keeps.
- **Did not run on the revert:** the test has no entry in the revert's report, or it skips at HEAD too. An earlier failing step stopped the command, or pytest stopped early (`-x`, `--maxfail`). It is a gap in the run, not evidence about the test.
- **`Keeps:` line:** a line in the mutants file, `Keeps: <test> — <the behavior from before the task that it checks>`, for a test that passes on the revert by design.
- **`Strengthened:` line:** a line in the mutants file, `Strengthened: <plan test> — by <new test>`, for a plan test that passes on the revert. The new test fails on the revert and checks the behavior that the plan test should have caught.

## Where the rules come from

- **Your dispatch names a spec excerpts file** (`task-<N>-spec.md`): each excerpt in it that states a rule, and each rule in the brief. When the file holds `none: <why>`, the rules are the brief's own requirement lines.
- **No excerpts file:** the spec sentences the task rests on, each cited as `path:line`, and each rule in the brief.

Cite an excerpt by its `path:line`, and a rule from the brief as `brief: <requirement>`.

## Steps

`<workspace>` is the plan's workspace: the directory your dispatch names, or the one `<this-skill-dir>/scripts/sdd-workspace PLAN_FILE` prints. `<N>` is the task number. `<K>` numbers the mutants 1, 2, 3 and so on.

1. **List the stated rules,** from the places above. When an excerpt and a plan test's assertion cannot both hold, keep the rule on the plan test's reading: add no test that takes the spec's side of that assertion, cover the rule's other shapes as usual (step 2), and aim a mutant at the rule as the plan test pins it, so that the plan test catches it (step 3). Report the conflict as "Plan tests" says.
2. **Cover each rule's input shapes.** For each rule, list the input shapes its words cover: for example quoted, nested, empty, at a boundary, repeated, or at the start or end. For each shape, name the test that uses it. For each shape with no test, add a test, and fix the code if that test fails. Commit. Only shapes that the rule's words cover count. If every shape has a test, add nothing. This step comes first because a mutant cannot find a missing branch: a mutant changes code that exists, and no change reaches a shape the code never handles (the example at the end shows one).
3. **Write mutants:** at least one aimed at each stated rule, and enough that each test the task adds or changes, plan tests included, is aimed at by one. One mutant may serve several targets. For each test, ask what wrong version of the code it would let through, and write that version. Each mutant is a plausible mistake, not a syntax break. To make one, edit the code and save `git diff -- <file> > <workspace>/task-<N>-mutant-<K>.patch`. Check that the patch is not empty: an empty patch means the edit never changed the file. Then restore the file with `git checkout -- <file>`, not from a copy. Keep any scratch file in `<workspace>`, never in `/tmp`, where another run can overwrite it.
4. **Write the mutants file,** `<workspace>/task-<N>-mutants.md`, in the form below.
5. **Run the script** from the repository root, on the brief's focused test command (its `Run:` steps that run tests and expect a pass): `<this-skill-dir>/scripts/mutant-run PLAN_FILE N BASE -- <the brief's focused test command>`. Use the same BASE on every run, so that the revert covers the whole task. The command starts pytest once, with no `-x` and no `--maxfail`, so that every test runs on the revert: when the brief's steps start pytest more than once, write one pytest call that runs the tests of every step. When your dispatch gives the script's absolute path, use that path. Read the result as "Reading the run" says.
6. **Answer each survivor and each invalid mutant.** For a survivor, strengthen the test it is aimed at (a new assertion, or a new input that the rule covers) or add a test, commit, and run the script again. When that test is a plan test, add a new test, as "Plan tests" says. For an invalid mutant, act on its reason ("Reading the run") and run again. Repeat until the run shows no survivor and no invalid mutant. When every mutant is caught, change no test.
7. **The revert.** Once the run shows no survivor and no invalid mutant, read its revert section ("Reading the run"). Each test that the task adds or changes (`git diff BASE HEAD` shows them), plan tests included, must fail on the revert (Terms). A test that the task neither adds nor changes needs nothing. A test with no entry did not run: run the script again on a command that runs it. For each test that the task adds or changes and that passed on the revert, read the brief and the excerpts, and take the path that fits:
   - **It is not a plan test, and it checks behavior that the task changes.** Strengthen it so that it fails on the revert. Then commit and run the script again.
   - **It is a plan test, and it checks behavior that the task changes.** Leave every line of it as the plan wrote it. Add a new test that checks the same behavior and fails on the revert, commit, run the script again, and write `Strengthened: <plan test> — by <new test>`. If a test that you added in step 2 or 6 already checks that behavior and fails on the revert, name it in the `Strengthened:` line and add no other.
   - **It checks behavior from before the task that the task keeps on purpose,** such as the normal case beside a bug's fix. Make the check for a `Keeps:` line ("The mutants file") first. Then leave the test as it is, and write `Keeps: <test> — <the behavior it checks>`.

   A test that you add here is a test the task adds: aim a mutant at it (step 3) before you commit, and answer each new run from step 6 again. When every test that the task adds or changes fails on the revert, change no test and write no line.
8. **Report** the last run's path and its counts.

## The mutants file

```text
# Task <N> mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| <path:line, or brief: <requirement>> | <input shape> | <test name> |

## Mutants

Mutant <K>: <targets: rule path:line and test names> — <the wrong version, in one line> — task-<N>-mutant-<K>.patch
Unproven: <test> — <why no plausible wrong version exists>
Unreachable: <rule path:line> — <why no code change in this task can break it>
Withdrawn: <K> — <why no behavior a person could see changes>
Keeps: <test> — <the behavior from before the task that it checks>
Strengthened: <plan test> — by <new test>
```

The table has one row for each rule and shape. Each `Mutant`, `Unproven`, `Unreachable` and `Withdrawn` line starts at column 0 with that word. Each `Keeps` and `Strengthened` line starts at column 0 too.

Most tasks need no `Unproven:`, `Unreachable:` or `Withdrawn:` line. Each one is a claim that a reviewer checks against the code. Survival alone is never a reason for one: most survivors mean a test is too weak, and step 6 strengthens it. Before you write one of these lines, make its check:

- **`Unproven:`** First name a plausible wrong version of the code that the test should catch. If you can name one, it is a mutant: write it. Write the line only when no plausible wrong version exists.
- **`Unreachable:`** If code in this task's diff decides the rule, the rule is reachable: write a mutant. Write the line only when no code change in this task can break the rule.
- **`Withdrawn:`** First look for an input on which the mutant's result differs from the code's in a way a person could see. If you find one, that input is a missing test: add it, and keep the mutant. Write the line only when no input changes anything a person could see. Then rename the patch to `task-<N>-mutant-<K>.patch.withdrawn`, so the script no longer runs it.

A `Keeps:` or `Strengthened:` line is a claim too, and a reviewer checks it against the brief, the excerpts and the run. Passing on the revert alone is never a reason for a `Keeps:` line: a test of changed behavior that passes on the revert is too weak, and step 7 strengthens it. Before you write one of these lines, make its check:

- **`Keeps:`** Read the brief and the excerpts. If the task changes the behavior that the test checks, the test is weak: take step 7's path for a test of changed behavior (for a plan test, a new test and a `Strengthened:` line), and write no `Keeps:` line. Write the line only when the test checks behavior from before the task that the task keeps on purpose.
- **`Strengthened:`** Write the line only when a run after the new test's commit shows that the new test fails on the revert.

## Reading the run

The script prints its `result:` line, one line for each mutant, and `run: <path>` last. The run file at that path is the verdict, not your report. It holds each run's output. Just before `run:`, the script prints the `revert:` line.

Each mutant line reads CAUGHT, SURVIVED or INVALID:

- **CAUGHT:** the tests failed with the mutant applied. Its `tests:` field names the tests that caught it.
- **SURVIVED:** the tests passed with the mutant applied. Go to step 6.
- **INVALID:** its `reason:` field says why.
  - `touches a test file: <path>`: a mutant changes code only. Make it again from the code.
  - `does not apply`: check the patch file first. If it is empty, the edit never changed the file: make the edit again, and check the patch before you restore the file. Otherwise the code changed after you saved the patch: make the patch again against HEAD.
  - `exit status <n>`, or `no failed test in the JUnit report`: the run failed with no failed test, for example on an import or syntax error. Write a plausible mistake instead. A second cause: the command starts pytest more than once and keeps going after a failure (two suites, or a suite with two interpreters, through one runner), so a later report replaced the one with the failure. Then run the script on a command that starts pytest once, or that joins its pytest runs with `&&`.
  - `timeout after <n>s`: the run passed its time limit. If the mutant makes the code hang, write a different one. If the tests are only slow, set `MUTANT_RUN_TIMEOUT` to a larger whole number of seconds.

Leave `--junitxml` out of the command. The script asks pytest for its own report, and a `--junitxml` in your command replaces it, so every catch reads INVALID.

The revert gets no verdict. It never changes the `result:` line, a mutant line, the `--- tests ---` section or the exit status, so exit 0 does not finish step 7. The `revert:` line reads one of:

- `revert: ran, exit <n>, failed <f>, not loaded <u>, skipped <s>, passed <p>`: the tests ran on the revert and wrote a report. Read the revert section (step 7).
- `revert: ran, exit <n>, no report`, or `revert: timeout after <n>s`: read the revert's output, under `--- output: revert ---`. A task whose tests all need the change, such as one whose `conftest.py` imports new code, needs nothing more. If the tests are only slow, set `MUTANT_RUN_TIMEOUT` as for a mutant, and run again. Report any other cause as a concern.
- `revert: not applied: <reason>`: the revert patch did not apply. The script builds it from HEAD on a clean tree, so this should not happen. Report the line as a concern.
- `revert: none: no file outside the tests and the project config changed`: the task changed only test files and project config files, so nothing ran, and step 7 has nothing to read. If the task changed code, check that BASE is the task's BASE.

The revert section, `--- revert ---`, holds one `path: <path>` line for each path that the revert put back, and a `sha256:` line for the revert patch, `<workspace>/task-<N>-revert.patch`. When the tests ran on the revert and wrote a report, one line follows for each test case in that report, in report order. `<id>` is `<classname>::<name>`, as in a mutant's `tests:` field.

- `failed <id>: <the first line of the failure's message>`: the test fails on the revert.
- `not loaded <name>: <the cause>`: the test file whose dotted module name is `<name>` cannot load. Each test in that file fails on the revert.
- `skipped <id>: <the reason>`: the revert made the test skip, such as an `importorskip` of new code, so it fails on the revert. A file skipped at its top gives its module name alone. A test that also skips at HEAD did not run.
- `passed <id>`: the test passes on the revert.

A test with no line did not run on the revert. pytest's own internal error gets no line.

The exit status:

- **0:** every mutant was caught. Go to step 7.
- **1:** a mutant survived or is invalid. Go to step 6.
- **2:** the script refused and wrote no run file. Act on its message, then run it again. For a dirty tree, restore the file you mutated (`git checkout -- <file>`), or commit the task's own files. For `no mutants for task N`, check the patch names and N. For a mutant already in HEAD, a mutant reached a commit: revert it. For a tree it could not restore, restore the tree by hand as the message says, then remove `<workspace>/mutant-active`. For `bad BASE` or `HEAD is not a descendant of BASE`, check BASE against your dispatch.
- **3:** the baseline run, with no patch applied, failed. Every mutant would then look caught, so none ran. Read the output lines it printed, make the tests pass, commit, and run it again.
- **143, 130 or 129:** a TERM, INT or HUP stopped the run, and the script reversed the patch first. Run it again.

Give the call a time limit long enough for the baseline and one run for each mutant. Add one more run for the revert. A run that your tool stops can leave a patch applied, with `<workspace>/mutant-active` beside it. Run the script again before you edit or commit anything: it reverses that patch first and notes it in the run file.

## Plan tests

- **Strengthening a plan test is allowed, in a new test.** For a survivor (step 6) or a shape with no test (step 2), write the new assertion or the new input that the rule covers as a new test. Leave every line of the plan test as the plan wrote it, decorators included, so a reviewer can see at once that no plan test changed. A plan test that passes on the revert is strengthened the same way, with a `Strengthened:` line (step 7).
- **Weakening a plan test is never allowed without a `Ruling:` line in the ledger.** Weakening is removing or loosening an assertion, or moving an expected value. Changing an expected value is moving it, even when the new value matches the spec.
- **A plan test that conflicts with the spec is never a target to strengthen.** If a controller dispatched you, leave the test as the plan wrote it and report the conflict as your dispatch says. If you keep the ledger yourself, the conflict is a ruling that the plan is wrong, never a silent edit. Ledger it before you change the test, and quote the spec sentence that decides it. If no sentence decides it, keep the plan's test.

## Example

The rule: "a form inside code never matches". The code blanks fenced blocks and inline spans before it looks for a form. The plan's test puts a form inside a plain fence and checks that it does not match.

The mutant "fences are not blanked" is caught, because the plain-fence test fails. So the mutant step alone looks done. But a fence inside a blockquote is also code, the code never blanked it, and no test used it. No mutant can reach that shape, because there is no branch for it to change. A later review broke the rule with exactly that input.

Step 2 finds it. The rule's words, "inside code", cover a plain fence, an inline span and a fence inside a blockquote:

```text
| Rule | Shape | Test |
|---|---|---|
| specs/scan.md:40 | a plain fence | test_form_in_fence_never_matches |
| specs/scan.md:40 | an inline span | test_form_in_span_never_matches |
| specs/scan.md:40 | a fence inside a blockquote | test_form_in_quoted_fence_never_matches |
```

The third row had no test. Step 2 adds it, the test fails, and the code is fixed and committed before any mutant is written. Then step 3 aims one mutant at each shape:

```text
Mutant 1: specs/scan.md:40, test_form_in_fence_never_matches — fences are not blanked — task-4-mutant-1.patch
Mutant 2: specs/scan.md:40, test_form_in_span_never_matches — inline spans are not blanked — task-4-mutant-2.patch
Mutant 3: specs/scan.md:40, test_form_in_quoted_fence_never_matches — a fence inside a blockquote is not blanked — task-4-mutant-3.patch
```
