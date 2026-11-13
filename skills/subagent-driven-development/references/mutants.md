# Mutants

Read this after GREEN and the commit, in a mutant task, before you report.

A passing test proves little until a wrong version of the code makes it fail. Here you write wrong versions on purpose, and a script proves that your tests catch each one.

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

## Where the rules come from

- **Your dispatch names a spec excerpts file** (`task-<N>-spec.md`): each excerpt in it that states a rule, and each rule in the brief. When the file holds `none: <why>`, the rules are the brief's own requirement lines.
- **No excerpts file:** the spec sentences the task rests on, each cited as `path:line`, and each rule in the brief.

Cite an excerpt by its `path:line`, and a rule from the brief as `brief: <requirement>`.

## Steps

`<workspace>` is the plan's workspace: the directory your dispatch names, or the one `<this-skill-dir>/scripts/sdd-workspace PLAN_FILE` prints. `<N>` is the task number. `<K>` numbers the mutants 1, 2, 3 and so on.

1. **List the stated rules,** from the places above. When an excerpt and a plan test's assertion cannot both hold, keep the rule on the plan test's reading: add no test that takes the spec's side of that assertion, cover the rule's other shapes as usual (step 2), and aim a mutant at the rule as the plan test pins it, so that the plan test catches it (step 3). Report the conflict as "Plan tests" says.
2. **Cover each rule's input shapes.** For each rule, list the input shapes its words cover: for example quoted, nested, empty, at a boundary, repeated, or at the start or end. For each shape, name the test that uses it. For each shape with no test, add a test, and fix the code if that test fails. Commit. Only shapes that the rule's words cover count. If every shape has a test, add nothing. This step comes first because a mutant cannot find a missing branch: a mutant changes code that exists, and no change reaches a shape the code never handles (the example at the end shows one).
3. **Write mutants:** at least one aimed at each stated rule, and enough that each test the task adds or changes, plan tests included, is aimed at by one. One mutant may serve several targets. For each test, ask what wrong version of the code it would let through, and write that version. Each mutant is a plausible mistake, not a syntax break. To make one, edit the code, save `git diff -- <file> > <workspace>/task-<N>-mutant-<K>.patch`, and restore the file with `git checkout -- <file>`.
4. **Write the mutants file,** `<workspace>/task-<N>-mutants.md`, in the form below.
5. **Run the script** from the repository root, on the brief's focused test command (its `Run:` steps that run tests and expect a pass): `<this-skill-dir>/scripts/mutant-run PLAN_FILE N -- <the brief's focused test command>`. When your dispatch gives the script's absolute path, use that path. Read the result as "Reading the run" says.
6. **Answer each survivor and each invalid mutant.** For a survivor, strengthen the test it is aimed at (a new assertion, or a new input that the rule covers) or add a test, commit, and run the script again. For an invalid mutant, act on its reason ("Reading the run") and run again. Repeat until the run shows no survivor and no invalid mutant. When every mutant is caught, change no test.
7. **Report** the last run's path and its counts.

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
```

The table has one row for each rule and shape. Each `Mutant`, `Unproven`, `Unreachable` and `Withdrawn` line starts at column 0 with that word.

Most tasks need no `Unproven:`, `Unreachable:` or `Withdrawn:` line. Each one is a claim that a reviewer checks against the code. Survival alone is never a reason for one: most survivors mean a test is too weak, and step 6 strengthens it. Before you write one of these lines, make its check:

- **`Unproven:`** First name a plausible wrong version of the code that the test should catch. If you can name one, it is a mutant: write it. Write the line only when no plausible wrong version exists.
- **`Unreachable:`** If code in this task's diff decides the rule, the rule is reachable: write a mutant. Write the line only when no code change in this task can break the rule.
- **`Withdrawn:`** First look for an input on which the mutant's result differs from the code's in a way a person could see. If you find one, that input is a missing test: add it, and keep the mutant. Write the line only when no input changes anything a person could see. Then rename the patch to `task-<N>-mutant-<K>.patch.withdrawn`, so the script no longer runs it.

## Reading the run

The script prints its `result:` line, one line for each mutant, and `run: <path>` last. The run file at that path is the verdict, not your report. It holds each run's output.

Each mutant line reads CAUGHT, SURVIVED or INVALID:

- **CAUGHT:** the tests failed with the mutant applied. Its `tests:` field names the tests that caught it.
- **SURVIVED:** the tests passed with the mutant applied. Go to step 6.
- **INVALID:** its `reason:` field says why.
  - `touches a test file: <path>`: a mutant changes code only. Make it again from the code.
  - `does not apply`: the code changed after you saved the patch. Make the patch again against HEAD.
  - `exit status <n>`, or `no failed test in the JUnit report`: the run failed with no failed test, for example on an import or syntax error. Write a plausible mistake instead.
  - `timeout after <n>s`: the run passed its time limit. If the mutant makes the code hang, write a different one. If the tests are only slow, set `MUTANT_RUN_TIMEOUT` to a larger whole number of seconds.

Leave `--junitxml` out of the command. The script asks pytest for its own report, and a `--junitxml` in your command replaces it, so every catch reads INVALID.

The exit status:

- **0:** every mutant was caught. Go to step 7.
- **1:** a mutant survived or is invalid. Go to step 6.
- **2:** the script refused and wrote no run file. Act on its message, then run it again. For a dirty tree, restore the file you mutated (`git checkout -- <file>`), or commit the task's own files. For `no mutants for task N`, check the patch names and N. For a mutant already in HEAD, a mutant reached a commit: revert it. For a tree it could not restore, restore the tree by hand as the message says, then remove `<workspace>/mutant-active`.
- **3:** the baseline run, with no patch applied, failed. Every mutant would then look caught, so none ran. Read the output lines it printed, make the tests pass, commit, and run it again.
- **143, 130 or 129:** a TERM, INT or HUP stopped the run, and the script reversed the patch first. Run it again.

Give the call a time limit long enough for the baseline and one run for each mutant. A run that your tool stops can leave a patch applied, with `<workspace>/mutant-active` beside it. Run the script again before you edit or commit anything: it reverses that patch first and notes it in the run file.

## Plan tests

- **Strengthening a plan test is allowed:** a new assertion, or a new input that the rule covers. Do it for a survivor (step 6) or a shape with no test (step 2).
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
