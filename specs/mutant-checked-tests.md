# Mutant-checked tests in plan execution — Design Spec

**Status:** DRAFT (2026-11-12), for the owner's review.

This design came from a brainstorming session on 2026-11-12. It started from the owner's proposal of a separate
test-writer agent for subagent-driven-development (below, "What this replaces"). The session's evidence moved the
target from test tampering to test strength. Decisions D1 and D2 are the owner's. Text marked *(designer's call)* is
the designer's choice, and the list under "Designer's calls" collects them. Line numbers are as of `8960159`.

> **For agentic workers:** plan this with writing-plans, in a fresh session. The micro-test in Verification is part
> of the plan, because the implementer text is behavior-shaping (writing-skills).

## Terms

- **Mutant:** a small patch that makes the task's code wrong in a way a person could plausibly write. An example is
  "read the whole authority, not the filtered keys". It changes code, never a test.
- **Caught:** with the mutant applied, the task's focused tests fail. For pytest that is exit status 1, with a failed
  test in the run's JUnit report.
- **Input shape:** one form of input that a stated rule's words cover, such as a quoted, nested, empty or repeated
  form, or a value at a boundary.
- **Survived:** with the mutant applied, the tests pass. Some test is too weak, or an input is missing.
- **Invalid:** the patch does not apply, touches a test file, or makes the run fail for another reason (pytest exit
  2, 3, 4 or 5: a collection error, an internal error, a usage error, no tests).
- **Stated rule:** a sentence in the spec, or in the task's own text, that says what the code must do for some
  class of inputs. An example is "a form inside code never matches".
- **Unproven test:** a test that the task adds or changes and that catches no mutant.
- **Mutant task:** a task whose brief has a focused pytest command that tests code the task changes. Lints, link
  checks and checks over Markdown do not count, because prose is a non-goal (D1). Every other task is exempt and
  records `none: <why>`. Pytest is the only runner at launch: every code test in the four repositories is pytest,
  and earnings-themes' `workbench.js` has no test runner.

## Intent

Today a task's tests pass, the reviews pass, and the final Codex review still finds defects. The owner asked whether
one agent writing both the code and the tests can ever fail. The owner then named Codex's final-review findings as
the proxy for what the tests miss.

The evidence (next section) shows two things. Implementers almost never weaken a plan's tests. But many tests,
most of them written by the planner, are too weak to fail for a plausible wrong implementation, and many stated
rules are tested on one input shape only. This design makes each task prove that its tests can fail. The implementer
first covers each stated rule's input shapes with tests. It then writes plausible mutants from the stated rules, and a
script proves that the tests catch each one.

## Evidence

A read-only recon on 2026-11-12 covered four repositories, all public: agent-skills (plans 55–92),
earnings-themes (22 plans), sec-edgar-local (8 plans) and embedding-data (10 plans). Subagents counted and
classified, and the designer checked every cited weakened and shared-reading case with `git show`.

**Implementers do not weaken plan tests.**

| Repository | Plan tests compared | Weakened | Plan test wrong, fixed by the implementer |
|---|---|---|---|
| agent-skills | 369 functions | 0 | 2 |
| embedding-data | 196 functions | 2 | 2 |
| sec-edgar-local | 153 functions | 0 | 6 |
| earnings-themes | 228 tasks | 2 | 8 |

All four weakenings are small, and all four happened in plans where Codex was the controller (embedding-data
`2f1ca20` and `9d78625`, earnings-themes `d0dec05` and `7820506`). Claude implementers copied the plan's test code
nearly verbatim: 363 of 369 in agent-skills, 109 of 110 in embedding-data plans 1–3, and 26 of 27 tasks in
sec-edgar-local. In sec-edgar-local, three of the plan-test fixes loosen a proof, and each carries an owner or
controller `Ruling:` that states its cost.

**Codex's final reviews find inputs nobody stated, prose, and stated rules with no test.** About 385 final-review
findings, sorted by the gap that let each one through:

| Gap | Count | Who can close it |
|---|---|---|
| Unstated input | 129 | An adversarial reviewer (Codex) |
| Prose | 78 | Lints, or nobody |
| Stated rule, no test for the input that broke it | 74 | The test author, if it reads the rule and varies the input |
| Not a bug, or unclear | 73 | — |
| Shared reading: a test covers the input but asserts the wrong thing or a weaker property | 31 | The test author, if it asks what the test would let through |

22 of the 31 shared readings sit in tests that the plan wrote. About four of them assert a wrong value: earnings-themes
plan 3 (`3f5cb35`, one crossing where three exist), plan 7 (`test_events_release.py:148`, "fourth quarter and full
year 2025" read as FY 2025 only) and plan 16 (`d88b77e`, a message against spec GS19), and embedding-data plan 1
(`3491905`). The rest assert too weak a property: an exit code never checked, a refusal reason without its subject,
a fixture whose name order equals its date order (embedding-data `8f28015`), or byte equality where the spec
requires a columnar filter (sec-edgar-local `fe6bca0`). Nine of the 31 sit in tests written in fix rounds, by the
controller, or as an implementer's extra test.

Typical stated-rule gaps: agent-skills plan 80 states "a form inside code never matches" and pins it with a test that
uses plain fences only, and Codex broke it with a blockquoted fence (`3df8826`). In earnings-themes, Codex
findings rated Important, Critical or P1 split as 11 unstated inputs, 8 stated rules, 3 shared readings and 2
prose.

Implementers already do this check now and then. Plan 66 Task 8 found three untested behaviors with a mutation run,
and earnings-themes `7cde927` is "mutation-checked". Per-task reviewers also flagged several of these gaps, rated
them Minor, and parked them (sec-edgar-local plan 3, agent-skills plan 66). Both ran before 2026-10-29, when the
shared reviewer block dropped its Minor grade (`6e753d6`). Today's block keeps two grades and tells the reviewer to
delete what a person using the software would not notice, and a weak test is easy to delete under that rule.

## What this replaces

The owner's proposal, as pasted at the session's start: per task, a test-writer subagent commits the tests as a RED
commit, the controller checks that they fail for the right reason, writes the paths to
`.sdd/<plan>/locked-tests.txt`, and dispatches the implementer to make the locked tests pass. A PreToolUse guard
denies Edit, Write and MultiEdit on locked paths for subagents. An implementer that thinks a test is wrong reports
DONE_WITH_CONCERNS, and an Opus adjudicator rules. The plan-time split stays closed (plan 81, plan 83, finding 24,
D8 of `specs/completed/statement-level-readings.md`).

The evidence answers its first open question ("Is the risk real?") with no: four small weakenings in more than 950
plan tests, none under a Claude implementer. The lock would also turn each of the 18 wrong plan tests into an
adjudication loop. A test writer that copies the plan's tests copies their weak properties and wrong values too. The
guard had its own gaps: the probe log records `agent_type` only on Bash and Agent payloads (`hooks/README.md:472-473`),
a shell write gets past an Edit/Write lock, and the hook does not run under the Codex or Antigravity adapters.

The proposal's other questions resolve under this design. One agent, the implementer, does the work (question 2).
The script checks the failure reason by exit status (question 3). No new agent means no cheap-tier question (question
4). The spec excerpts go to the implementer and the task reviewer (question 5).

## Goals, non-goals and anti-goals

**Goals.**

- In a mutant task, every test that the task adds or changes catches at least one plausible mutant, or the task
  records why it cannot.
- In a mutant task, every stated rule that the task implements has at least one mutant aimed at it, or the task
  records why no code change can break it.
- In a mutant task, every input shape that a stated rule's words cover has a test that uses it. Mutants cannot find a
  missing branch, so this goal has its own step (Design 2, step 2).
- A script, not an agent's report, decides caught, survived and invalid.
- The implementer brief carries the spec sentences the task rests on (layer 4 of backlog item
  83-statement-level-readings, `specs/deferred_items.md:6225`).
- An implementer that finds a plan test in conflict with the spec reports it and never edits the test to fit its
  own reading (layer 4).
- The same check runs under subagent-driven-development and executing-plans.

**Non-goals.**

- Unstated inputs. They stay with the final Codex review (D1).
- Prose findings.
- A separate test-writer agent, a lock file and a PreToolUse guard (D2, Approaches).
- A mutation tool (option 2) and plan-time `Rejects:` lines (option 3).
- Any change to writing-plans or to how planners write tests.
- Independence between the planner's reading and the plan's tests. Plans 81 and 83 closed that.

**Anti-goals.** Each of these makes the design a failure, even if it works:

- A mutant that edits a test counts as caught.
- The verdict rests on the implementer's report, not on a run the script made.
- A mutant stays applied after a run, or reaches a commit.
- An implementer loosens a plan test with no `Ruling:` line.
- The step adds a stop for the owner on every task.
- `skills/subagent-driven-development/SKILL.md` grows.

## Approaches

The session laid out three ways to reach D1's target. The owner chose the first (D2).

1. **The implementer writes mutants, and a script proves each catch.** Chosen. The mutants come from the stated
   rules, so they test what the spec asks. Where a rule's input shapes are untested, the implementer adds the missing
   test (the approaches message said so, and Design 2 makes it a step of its own). A script, not the agent, decides each verdict. It works for both
   executors and on every runtime, with no new agent. Costs: one to three more implementer turns per task, one
   focused test run per mutant, and an implementer can pick easy mutants (the task reviewer judges plausibility).
2. **A mutation tool run by the controller** (for example mutmut). It needs no agent judgment and finds unasserted
   outputs well. It is Python-only (earnings-themes' `workbench.js` stays out), slow on large suites, and reports
   equivalent mutants as false alarms. It cannot find a rule tested on one input shape, because that gap needs a new
   input, not changed code.
3. **The planner names what each test rejects** (`Rejects: <wrong implementation>` per test step). It fixes weak
   tests at their source, where 19 of the 22 plan-written cases came from. But the planner's one reading writes both
   the test and its mutant, and plans grow.

Dropped before the comparison: a per-task Codex review (it mostly finds unstated inputs, outside D1), and a reviewer
severity rule alone (reviewers already flagged several gaps as Minor). The severity rule is folded into option 1
(Design 6).

## Owner decisions (2026-11-12)

- **D1. The target is weak tests and stated rules with no test.** Asked "Which gap should the design target?", the
  owner chose "Weak tests + rules". Unstated inputs stay with Codex.
- **D2. Option 1.** "Go with option 1": the implementer writes mutants, and a script proves each catch.

The owner also directed the evidence: "I would look at Codex final review finding issues as a proxy", and "I would
also look at earnings-themes, sec-edgar-local, embedding-data".

## Design

### 1. The spec excerpts file (subagent-driven-development)

Before it dispatches an implementer, the controller writes `<workspace>/task-N-spec.md` *(designer's call)*. It holds
the spec's path and, for each sentence the task's code or tests rest on, the sentence verbatim with its `path:line`.
The controller picks them from three places: the sections the task's text cites, the plan's Review Focus lines that
name this task, and the spec's sentences about the names and values in the task's Interfaces block. The brief already
carries the Global Constraints, so the file does not repeat them. When the plan's `Spec:` is `none`, the file holds
`none: <why>`, and the stated rules are the brief's own requirement lines.

Verbatim quotes keep the controller's reading out of the text. The implementer may still open the spec at its path.

### 2. The implementer's step (subagent-driven-development)

The dispatch names the excerpts file next to the brief. After GREEN and the commit, and before its report, the
implementer:

1. Lists the stated rules: each excerpt that states a rule, and each rule in the brief.
2. **Covers each rule's input shapes.** For each rule, it lists the input shapes the rule's words cover: for example
   quoted, nested, empty, at a boundary, repeated, or at the start or end. For each shape it names the test that uses
   it. For each shape with no test, it adds a test, and fixes the code if that test fails. It commits. This step comes
   first because a mutant cannot find a missing branch. In plan 80, code that masks plain fences passes a mutant "do
   not mask fences" through the plain-fence test, and no mutant ever reaches the blockquoted fence that Codex used.
3. Writes mutants: at least one aimed at each stated rule, and enough that each test the task adds or changes is
   aimed at by one. One mutant may serve several targets. Each mutant is a plausible mistake, not a syntax break. To
   make one, it edits the code, saves `git diff -- <file> > <workspace>/task-N-mutant-K.patch`, and restores the file.
4. Writes `<workspace>/task-N-mutants.md` with two parts:
   - An inputs table: one row per rule and shape, with the test that uses the shape.
   - One entry per mutant: its number, its targets (a rule as `path:line`, or a test name), the wrong version in one
     line, and its patch file.
5. Runs `mutant-run` (Design 3) on its focused test command and reads the result.
6. For each survivor, strengthens a test (a new assertion, or a new input that the rule covers) or adds one, commits,
   and runs again. Three lines in the mutants file record what it cannot aim at:
   - `Unproven: <test> — <why no plausible wrong version exists>`, for a test.
   - `Unreachable: <rule path:line> — <why no code change in this task can break it>`, for a rule.
   - `Withdrawn: K — <why>`, for a mutant it finds equivalent (no behavior a person could see changes). It keeps the
     patch, renamed so the script no longer finds it.
7. Reports the last run's path and its counts.

The instructions for steps 1 to 6 live in one new reference file, `references/mutants.md` *(designer's call)*. The
implementer prompt and executing-plans both point at it, so one text is micro-tested for both executors.

Strengthening a plan test is allowed. Weakening one (removing or loosening an assertion, or moving an expected value)
is never allowed without the controller's ruling (Design 5). The patches and the mutants file live in the plan's
workspace, which git ignores, so they never reach a commit.

### 3. The `mutant-run` script

`<this-skill-dir>/scripts/mutant-run PLAN_FILE N -- TEST_COMMAND [ARGS...]`, beside `test-run` in
`skills/subagent-driven-development/scripts/`. It follows test-run's conventions: the same task-number grammar,
`sdd-repo --with-commit`, `sdd-workspace`, a new run file per call (`task-N-mutants.log`, then
`task-N-mutants-K.log`), the output tail, and a `run: <path>` last line.

In order:

1. **Recover.** If `<workspace>/mutant-active` exists, an earlier run was killed with a mutant applied. Reverse that
   patch (`git apply -R`), remove the marker, and note it in the run file.
2. **Refuse a dirty tree** (exit 2), with test-run's check: `git status --porcelain --untracked-files=normal`.
3. **Find the patches** `task-N-mutant-*.patch`, in K order. None: exit 2, `no mutants for task N`. A patch whose
   `git apply -R --check` succeeds is already in HEAD: a mutant reached a commit. Stop with exit 2 and name it.
4. **Baseline.** Run the command with no patch. A failing baseline stops the run before any patch (exit 3), because
   every mutant would then look caught.
5. **Each patch.** A patch that touches a test or fixture file is INVALID and never applied: `test_*.py`, `*_test.py`,
   `conftest.py`, `*.test.*`, `*.spec.*`, or a path under a `tests/`, `test/` or `fixtures/` directory. A patch that
   `git apply --check` refuses is INVALID. Otherwise: write the marker, apply, run the command, reverse, remove the
   marker, and confirm that the tree matches its state before the patch. Exit 0 is SURVIVED. Exit 1 with at least
   one failed test in the run's JUnit report is CAUGHT, and the run records those test IDs. Any other result is
   INVALID, including exit 1 with no report or no failed test in it, so a runner other than pytest can never produce
   a false catch.

*(Designer's call)* The script asks pytest for the report through `PYTEST_ADDOPTS`, adding
`--junitxml=<workspace>/<a temporary name>` to any value already set. It does not read pytest's `FAILED` summary
lines. pytest's `-r` flag is last-wins, so a brief command with `-rs` prints no `FAILED` lines, and every caught
mutant would read INVALID. None of the four repositories sets `-r` in its pytest config today, but brief commands
can.
6. **Write the run file.** Header lines: `mutant-run: Task <N>, run <K>`, `command:`, `head:`, `tree:` and `result:
   caught <c>, survived <s>, invalid <i>`. Then one line per mutant (number, patch sha256, verdict, exit status,
   failing test IDs), then one line per failing test ID with the mutants it caught, then each run's output.
7. **Exit** 0 when every mutant is CAUGHT, 1 when any is SURVIVED or INVALID, 2 for a bad call or a dirty tree, 3 for
   a failing baseline.

*(Designer's call)* The script mutates the real working tree, not a scratch worktree, for two reasons:

- **The scratch tree lacks the ignored files** that some tests read, such as local data or fixtures that git does not
  keep. Those tests fail there for reasons other than the mutant.
- **Its environment is either slow or wrong.** `uv run` in a fresh worktree builds that tree's own `.venv`, which
  is slow on heavy stacks such as JAX. Reusing the main checkout's environment instead loads the main checkout's
  source through its editable install, so the mutant never loads and every mutant survives.

The marker, the clean-tree checks and the reverse after each run bound the risk of the in-place run.

The command is the brief's focused test command: its `Run:` steps that run tests and expect a pass. It is not the
project's whole documented suite, which can take over an hour (sec-edgar-local's takes about 74 minutes).

### 4. The controller's loop (subagent-driven-development)

- **At DONE.** After test-run passes, run mutant-run with the focused command. Put both commands' steps in
  `references/test-run.md`, which the controller already reads at DONE and after every fix round.
- **A survivor or an invalid mutant** is a fix round before any review, like a failing test run. The run file is the
  finding.
- **After each fix round,** run both scripts again. A fix that adds or changes a test needs a mutant aimed at it. Nine
  of the 31 shared readings sat in tests written outside the plan's Step 1 code.
- **The reviewer gets three more paths** (`references/file-handoffs.md`): the excerpts file, the mutants file and the
  mutant run file.
- **A task that is not a mutant task** (Terms): the mutant run path is `none: <why>`, as test-run.md already does for
  a task with no command. The controller still writes the excerpts file, for layer 4.

### 5. Test-versus-spec conflicts (layer 4)

An implementer that finds a plan test in conflict with an excerpt reports DONE_WITH_CONCERNS. It quotes the excerpt
and the assertion, and it leaves the test as the plan wrote it. `references/handling-reports.md` sends the concern to
the existing ruling rule in `references/fix-loop.md` (a finding against plan text, with the spec as the binding
authority):

- **The spec decides it.** The controller ledgers a `Ruling:` that quotes the deciding spec sentence word for word,
  as Design 7 of `specs/completed/statement-level-readings.md` requires of its adjudicator. When the test is wrong,
  the controller dispatches a fix round that changes the test, and the ruling covers the change.
- **No sentence decides it.** The controller keeps the plan's test, so the task completes on the plan's reading, and
  ledgers `Ruling: (unclear) …`. A ruling with no quote counts as unclear.
- **The owner rules on each unclear ruling at the completion gate.** Both executors' `references/final-review.md`
  today list every `Ruling:` line at the gate as "a decision taken, not a question" (SDD `:41`, executing-plans
  `:84`). Each gains one exception: a `(unclear)` ruling is a question in the gate's batch, stalled on the owner's
  input (`skills/writing-plans/SKILL.md:291-299`). If the owner overrules, the change is a follow-up task.

The owner's proposal had an Opus adjudicator rule on these conflicts, with unclear cases sent to the owner at the
completion gate. *(Designer's call)* The controller keeps that role. It already rules on findings against plan text
with the spec as the binding authority (`references/fix-loop.md`), and the evidence puts these conflicts at about
four in more than 950 plan tests. The three outcomes stay as the owner proposed them.

The task reviewer treats a plan test loosened with no covering `Ruling:` line as a finding.

### 6. The task reviewer

The checks go in a new `## Mutants` section of the task reviewer's own text, beside its `## Tests` section, in
`task-reviewer-prompt.md` and `agents/task-reviewer.md` *(designer's call)*. They stay outside the shared reviewer
block (`## Review scope` to `## Declined to judge`), so `check_reviewer_block.py`'s four copies and the final
whole-branch reviewer are unchanged. The reviewer reads the three new files and checks:

- The inputs table lists the shapes each stated rule's words cover, and each shape has a test. A shape the rule
  plainly covers but the table leaves out is a finding.
- Each mutant is a plausible mistake a person might write, not a syntax break or a change no one could see.
- Each stated rule in the excerpts has a mutant aimed at it, or an `Unreachable:` line the reviewer accepts.
- Each test the task adds or changes caught at least one mutant (the run file's per-test lines), or has an
  `Unproven:` line the reviewer accepts.
- Each `Withdrawn:` line holds.
- A plan test loosened with no `Ruling:` line.

The section says why each gap is a finding under the shared block's own terms. The mutant step is part of the task's
requirements, so a gap is "a missed or misread requirement", graded Important. A test that no plausible wrong version
can fail is the block's "tests that assert nothing". The section also says that the block's last pass, which
deletes what a person would not notice, does not delete these findings. A test that lets a plausible wrong version
through lets a defect reach that person. This is the severity rule folded in from the dropped approach.

### 7. executing-plans

The inline agent read the spec at setup, so it writes no excerpts file *(designer's call)*. Its mutants file cites the
spec as `path:line`. Section 2 ("Work the steps") gains the mutant step after GREEN, and the completion contract (Section
3) gains one item: the task's mutant run shows no survivor and no invalid mutant, or the task has no runnable test
command.

`task-done` gains a gate *(designer's call)*. After a passing test run, it reads the newest `task-N-mutants*.log`.
It writes the completion line only when all of these hold:

- The run's `head:` is HEAD.
- Its result shows no survivor and no invalid mutant.
- Every mutant number in `task-N-mutants.md` either appears in the run or has a `Withdrawn:` line.

Otherwise it records nothing. It does not run mutants itself, because its command is the whole documented suite.
`--no-mutants '<why>'` lets a task that is not a mutant task pass the gate, and the reason goes into the completion
line. The line gains `mutants: <caught>/<total>`.

An inline run has no per-task reviewer, and a script cannot judge whether a mutant is plausible. So the final
whole-branch review gets the workspace's mutants files and run files, and checks them as Design 6 lists
*(designer's call)*. That changes `skills/executing-plans/references/final-review.md` and the review's inputs.

The layer 4 rule applies inline too. A plan test that conflicts with the spec is a "plan is wrong" ruling under
Section 2's existing text, never a silent edit. A spec that does not decide it goes to the completion gate, as in
Design 5.

### 8. Model tiers

*(Designer's call)* A mutant task gets the **standard** floor. Writing a plausible mutant from a stated rule is
judgment, and `references/model-selection.md` signal 2 gives the cheap tier only to transcription and testing. Every
other task is unchanged.

### 9. Where the text goes

- `skills/subagent-driven-development/SKILL.md`: **no change** (Constraints).
- `skills/subagent-driven-development/`: `references/mutants.md`, new (Design 2). `implementer-prompt.md` (Design 2
  and 5). `task-reviewer-prompt.md` and `re-review-prompt.md` (Design 6). `references/test-run.md`,
  `file-handoffs.md`, `handling-reports.md`, `fix-loop.md`, `final-review.md` and `model-selection.md` (Design 4, 5
  and 8).
- `skills/subagent-driven-development/scripts/mutant-run`, new, with its tests in `scripts/test_sdd_scripts.py`.
- `agents/task-reviewer.md`, its `## Mutants` section, then the regenerated adapters under `runtimes/`.
- `skills/executing-plans/SKILL.md`, `references/final-review.md` and `scripts/task-done`, with task-done's tests in
  `scripts/test_executing_plans_scripts.py`.
- `build/check_helper_paths.py`: `mutant-run` joins `HELPERS`.
- `NOTICE`: the modification lines for the two adapted superpowers skills.

## Verification

1. **The script, test first.** In `test_sdd_scripts.py`, each of these fails before the script exists, then passes:
   - A dirty tree is refused, and so is a task with no patches.
   - A failing baseline stops the run before any patch.
   - A patch that touches a test file is INVALID and never applied. A patch that does not apply is INVALID.
   - Exit 1 is CAUGHT, with its failing test IDs. Exit 0 is SURVIVED. Exit 2 is INVALID.
   - A leftover marker is reversed.
   - The tree is clean after every run, and no run file overwrites another.
2. **task-done's gate, test first.** A missing run, a stale `head:`, a survivor and an invalid mutant each block the
   line. A clean run and `--no-mutants` each let it through.
3. **A micro-test of the implementer text** (writing-skills' method, with a control arm on today's text). Five
   synthetic fixtures model the evidence, and no code is copied from the four repositories *(designer's call)*:
   - **F1:** a plan fixture whose name order equals its date order (embedding-data `8f28015`).
   - **F2:** a plan test that never checks an exit code (agent-skills `29b0454`).
   - **F3:** a stated rule tested on one input shape (agent-skills `3df8826`).
   - **F4:** a plan test whose expected message contradicts a spec excerpt (earnings-themes `d88b77e`).
   - **F5:** a clean task with strong tests and no conflict.

   Five reps per fixture per arm, implementers at **standard**: 50 reps, an estimated $15–50. Both arms get the
   excerpts file, so F4 measures the conflict rule's wording, not whether the spec is visible *(designer's call)*.

   | Fixture | Bar for the treatment arm |
   |---|---|
   | F1, F2 | Finds the weak test and strengthens it in at least 4 of 5 reps |
   | F3 | Lists the untested shape in the inputs table and adds a test that uses it in at least 4 of 5 reps |
   | F4 | Reports DONE_WITH_CONCERNS with the quote, and leaves the test unedited, in at least 4 of 5 reps |
   | F5 | No concern and no test change in at least 4 of 5 reps |
   | All | No rep in either arm weakens a test |

   A control arm that meets a bar means the text adds nothing on that fixture. The results file reports it, and the
   owner rules before the text ships.
4. **A micro-test of the reviewer's `## Mutants` section**, on recorded task packages, with a control arm on today's
   reviewer text. Three fixtures:
   - **R1:** a plausible mutant set with every rule covered.
   - **R2:** a set with one trivial mutant and one rule left without a mutant.
   - **R3:** a survivor withdrawn as "equivalent" when it changes visible behavior.

   Five reps per fixture per arm at **standard**: 30 reps, an estimated $5–15. Bars: R1 draws no mutant finding, and
   R2 and R3 each draw an Important finding, in at least 4 of 5 reps.
5. **When the treatment arm misses a bar** *(designer's call)*: revise the wording and rerun only the failing
   fixtures, at most twice. Then stop for the owner with the results. Stop at once if the micro-tests' total spend
   passes $100.

The controller steps (Design 1, 4 and 5) and the inline gate (Design 7) get no micro-test *(designer's call)*. The
scripts and their tests enforce the gate and the runs. The controller's other steps are bookkeeping that the task
reviewer's inputs make visible, since a missing file shows as a missing input.
6. **The commit lints and the suites** the change reaches (CLAUDE.md, Commands), including `check_conformance.py`,
   `check_reviewer_block.py`, `check_helper_paths.py`, `sync_runtime_assets.py --check` and the dependency-drift
   test.

## Constraints

- **SDD's SKILL.md does not grow.** Its body is 19,926 characters, already 226 over the register's window of 19,700,
  under the waiver `subagent-driven-development-compaction-window` (`build/cc_guide/conformance.toml:813-821`). All new
  text goes into prompts and reference files.
- **Reviewer block.** Four reviewer surfaces carry one shared block (`build/check_reviewer_block.py`):
  `agents/code-reviewer.md`, `agents/task-reviewer.md`, `skills/requesting-code-review/code-reviewer.md` and
  `skills/subagent-driven-development/task-reviewer-prompt.md`. A change to the block lands in all four.
- **Helper paths and orphan files.** Every mention of `mutant-run` under `skills/` carries the `<this-skill-dir>/`
  anchor. The script lands in the same commit as a skill file that names it.
- **Runtimes.** Run the adapter generator after any change to `agents/`. The scripts run under macOS bash 3.2, as
  test-run and task-done do.
- **Dependencies.** `install.py`'s `DEPENDENCIES` already makes subagent-driven-development a hard dependency of
  executing-plans (`install.py:55-58`), so the new script needs no new entry. Run the dependency-drift test anyway.
- **Provenance.** subagent-driven-development and executing-plans are adapted from superpowers (MIT, `LICENSE-superpowers`).
  This design adds original text and a script, and it brings in no outside source. Record the change in `NOTICE`.
- **Python style** for the tests: single quotes, Python as pinned in `build/versions.toml`.

## Left to the builder

- The exact prompt wording, within Design 2, 5 and 6, shaped by the micro-test.
- The run file's exact column layout, within Design 3's header lines.
- How the controller words the excerpts in `task-N-spec.md`, within Design 1's rules.
- Whether test-run and mutant-run share a helper for their common steps.
- Whether test-run refuses to run while a `mutant-active` marker exists.
- A per-mutant timeout that works under macOS bash 3.2.
- How mutant-run compares the tree after a run when the tests leave untracked files.
- Which task number a batch ([batching.md](../skills/subagent-driven-development/references/batching.md)) uses for
  its mutant files.
- Which reference file holds Design 1's excerpt rules.

## Designer's calls

1. Only tasks with a focused pytest command over changed code are mutant tasks. Pytest is the only runner at launch
   (Terms).
2. The controller writes a verbatim excerpts file per task, chosen from the task's citations, its Review Focus lines
   and its Interfaces names (Design 1).
3. One reference file, `references/mutants.md`, holds the mutant-writing steps for both executors. A rule no code
   change can break gets an `Unreachable:` line. An inputs step comes before the mutants, because mutants cannot find
   a missing branch (Design 2).
4. The mutant-run script works in the real working tree, with a marker for recovery, not in a scratch worktree. A
   patch already in HEAD stops the run (Design 3).
5. Mutants run against the focused test command, not the whole documented suite (Design 3).
6. A patch that touches a test or fixture file is INVALID. CAUGHT needs exit 1 and a failed test in a JUnit report
   that the script requests through `PYTEST_ADDOPTS` (Design 3).
7. The controller, not a new adjudicator agent, rules on test-versus-spec conflicts. A ruling quotes its deciding
   sentence, and an unclear one keeps the plan's test and becomes a question at the completion gate (Design 5).
8. The reviewer's mutant checks live in a task-reviewer-only `## Mutants` section, outside the shared block. They are
   graded Important under the block's own terms (Design 6).
9. executing-plans writes no excerpts file. task-done gates on the mutant run without running it, and the final
   whole-branch review checks the mutants (Design 7).
10. Mutant tasks get the standard floor (Design 8).
11. The micro-tests use synthetic fixtures: 50 implementer reps and 30 reviewer reps, both arms with the excerpts
    file, two revision rounds at most, and a $100 stop (Verification).

## Backlog effects

- **83-statement-level-readings, layer 4** (`specs/deferred_items.md:6226`): Design 1, 5 and 7 decide it for both
  executors. The item closes when the plan lands.
- **The closed spec-reading item's rule "Mutation testing is out of scope"** (`specs/deferred_items.md:5387-5388`)
  ruled mutation testing out for spec misreadings, "because it measures test strength, not correctness". This design
  is about test strength (D1). That rule is unchanged for its own problem.
