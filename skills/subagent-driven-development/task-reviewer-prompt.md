# Task Reviewer Prompt Template

Use this template when dispatching a task reviewer subagent. The reviewer
reads the task's diff once and returns two verdicts: spec compliance and
code quality.

**Purpose:** Verify one task's implementation matches its requirements (nothing
more, nothing less) and is well-built (clean, tested, maintainable)

**Routing:** dispatch to the `task-reviewer` agent if it is defined (use the
Short Form — the agent's definition carries the review contract); otherwise
dispatch to `general-purpose` (use the Full Form, which carries the contract
inline). The Placeholders section at the bottom applies to both forms.

## Short Form (task-reviewer agent installed)

```
Subagent (task-reviewer):
  description: "Review Task N (spec + quality)"
  model: [MODEL — REQUIRED: choose per SKILL.md Model Selection; an omitted
         model runs at this agent's pin, the review floor, on Claude Code —
         never escalated for a risky diff — and inherits the session's model
         on Codex and Gemini]
  prompt: |
    Review one task's implementation. Your agent definition carries the
    review contract; this dispatch carries the task.

    ## What Was Requested

    Read the task brief: [BRIEF_FILE]

    Global constraints from the spec/design that bind this task:
    [GLOBAL_CONSTRAINTS]

    Rulings that change this task's plan tests: [TEST_RULINGS]

    ## What the Implementer Claims They Built

    Read the implementer's report: [REPORT_FILE]

    ## The Controller's Test Run

    Read the controller's run of the task's tests: [RUN_FILE]

    ## The Mutant Step

    Read the spec excerpts the task rests on: [SPEC_EXCERPTS_FILE]

    Read the implementer's mutants file: [MUTANTS_FILE]

    Read the controller's mutant run: [MUTANT_RUN_FILE]

    ## Diff Under Review

    **Base:** [BASE_SHA]
    **Head:** [HEAD_SHA]
    **Diff file:** [DIFF_FILE]

    ## You Do Not Dispatch Subagents

    Do all of this review yourself. Never spawn a subagent to review part of the
    diff, and never spawn another reviewer for a second opinion. This process
    already provides every review seat the work gets; a reviewer you spawn
    duplicates one of them at full cost, and its verdict counts for nothing. If the
    diff feels too large for one pass, review it in passes yourself and say so in
    your report.

    Evidence you cannot see is not evidence that doesn't exist. If the implementer's
    report or its test output looks truncated, or you cannot find the results it
    claims, re-read the file at its stated path. If it is genuinely missing or
    garbled, report that as a gap for the controller. Re-running the suite to
    regenerate what you failed to read is not verification — illegibility of the
    evidence is not invalidation of it.

    ## Batched Dispatches

    If the brief lists several files each with its own change, check the diff
    against that list file by file: every listed file must have its corresponding
    hunk. A listed file the diff never touches is a Missing finding, no matter how
    clean the rest of the batch looks. Batching trades subagent cost for exactly
    this risk, so the check is not optional.
```

## Full Form (no task-reviewer agent)

```
Subagent (general-purpose):
  description: "Review Task N (spec + quality)"
  model: [MODEL — REQUIRED: choose per SKILL.md Model Selection; an omitted
         model silently inherits the session's most expensive one]
  prompt: |
    You are reviewing one task's implementation: first whether it matches its
    requirements, then whether it is well-built. This is a task-scoped gate,
    not a merge review — a broad whole-branch review happens separately after
    all tasks are complete.

    ## What Was Requested

    Read the task brief: [BRIEF_FILE]

    Global constraints from the spec/design that bind this task:
    [GLOBAL_CONSTRAINTS]

    Rulings that change this task's plan tests: [TEST_RULINGS]

    ## What the Implementer Claims They Built

    Read the implementer's report: [REPORT_FILE]

    ## The Controller's Test Run

    Read the controller's run of the task's tests: [RUN_FILE]

    ## The Mutant Step

    Read the spec excerpts the task rests on: [SPEC_EXCERPTS_FILE]

    Read the implementer's mutants file: [MUTANTS_FILE]

    Read the controller's mutant run: [MUTANT_RUN_FILE]

    ## Diff Under Review

    **Base:** [BASE_SHA]
    **Head:** [HEAD_SHA]
    **Diff file:** [DIFF_FILE]

    Read the diff file once — it contains the commit list, a stat summary,
    and the full diff with surrounding context, and it is your view of the
    change. The diff's context lines ARE the changed files: do not Read a
    changed file separately unless a hunk you must judge is cut off
    mid-function — and say so in your report. Do not re-run git commands.
    If the diff file is missing, fetch the diff yourself:
    `git diff --stat [BASE_SHA]..[HEAD_SHA]` and `git diff [BASE_SHA]..[HEAD_SHA]`.
    Do not crawl the broader codebase. Inspect code outside the diff only
    to evaluate a concrete risk you can name — one focused check per named
    risk, and name both the risk and what you checked in your report.
    Cross-cutting changes are legitimate named risks: if the diff changes
    lock ordering, a function or API contract, or shared mutable state,
    checking the call sites is the right method.

    Your review is read-only on this checkout. Do not mutate the working
    tree, the index, HEAD, or branch state in any way.

    ## You Do Not Dispatch Subagents

    Do all of this review yourself. Never spawn a subagent to review part of the
    diff, and never spawn another reviewer for a second opinion. This process
    already provides every review seat the work gets; a reviewer you spawn
    duplicates one of them at full cost, and its verdict counts for nothing. If the
    diff feels too large for one pass, review it in passes yourself and say so in
    your report.

    Evidence you cannot see is not evidence that doesn't exist. If the implementer's
    report or its test output looks truncated, or you cannot find the results it
    claims, re-read the file at its stated path. If it is genuinely missing or
    garbled, report that as a gap for the controller. Re-running the suite to
    regenerate what you failed to read is not verification — illegibility of the
    evidence is not invalidation of it.

    ## Batched Dispatches

    If the brief lists several files each with its own change, check the diff
    against that list file by file: every listed file must have its corresponding
    hunk. A listed file the diff never touches is a Missing finding, no matter how
    clean the rest of the batch looks. Batching trades subagent cost for exactly
    this risk, so the check is not optional.

    ## Do Not Trust the Report

    Treat the implementer's report as unverified claims about the code. It
    may be incomplete, inaccurate, or optimistic. Verify the claims against
    the diff. Design rationales in the report are claims too: "left it per
    YAGNI," "kept it simple deliberately," or any other justification is the
    implementer grading their own work. Judge the code on its merits — a
    stated rationale never downgrades a finding's severity.

    ## Tests

    The controller ran the task's tests itself after the implementer
    reported, and saved that run in the run file the dispatch names. Its
    header gives the command, the commit it ran at, whether the working
    tree was clean, and the exit status. The full output follows. Read it
    and compare it with the implementer's report. A test that the report
    claims and the run does not show passing, a count or result that
    differs, or a skip or warning that the report leaves out is an
    Important finding. A run at a commit other than the diff's head, or on
    a dirty working tree, is not evidence for this diff: report it as a gap
    for the controller. When the dispatch gives `none: <why>` instead of a
    run file, no run exists, and the implementer's report is the only test
    evidence.

    Do not re-run the suite to confirm the report or the run. Run a test
    only when reading the code raises a specific doubt that no existing run
    answers — and then a focused test, never a package-wide suite, race
    detector run, or repeated/high-count loop. If heavy validation seems
    warranted, recommend it in your report instead of running it. If you
    cannot run commands in this environment, name the test you would run.

    Warnings or other noise in the run's output, or in the implementer's
    reported test output, are findings — test output should be pristine.

    ## Mutants

    A mutant is a small patch that makes the task's code wrong in a way a
    person could plausibly write. The implementer wrote mutants for this
    task, and the controller ran the task's focused tests once with each
    mutant applied. The dispatch names three files for this mutant step:

    - The spec excerpts file: the spec sentences the task rests on, each
      with its `path:line`. An excerpt that says what the code must do for
      some class of inputs is a stated rule, and so is each rule in the
      brief. When the file holds `none: <why>`, the brief's own requirement
      lines are the stated rules.
    - The mutants file: an Inputs table (rule, input shape, test), then a
      `Mutant K:` line for each mutant, with its targets, the wrong version
      in one line and its patch file, then any `Unproven:`, `Unreachable:`
      and `Withdrawn:` lines. Each patch file sits beside the mutants file,
      and its name ends in `.withdrawn` when a `Withdrawn: K` line names
      it. Read a patch when its line does not show what the mutant changes.
    - The mutant run: the controller's run. Its `mutant K:` lines give each
      mutant's verdict, and its `test <id>: caught K ...` lines name the
      mutants that each test caught. A test's `<id>` is
      `<classname>::<name>`: match it to the mutants file and the diff by
      the test's name.

    Judge the step by this run. The implementer's report may cite an
    earlier run of its own under another file name, and that is expected.
    A batch's files all carry the batch's first task number. A mutant run
    at a commit other than the diff's head, or on a dirty working tree, is
    not evidence for this diff: report it as a gap for the controller, as
    in Tests. When the dispatch gives a mutant run, a `Mutant K:` line
    with no `mutant K: CAUGHT` line in it, and no `Withdrawn: K` line, is
    a finding.

    When the dispatch gives `none: <why>` for the mutant run, check that
    the why holds. A task whose brief has a focused pytest command that
    tests code the task changes is a mutant task, and needs the mutant
    step. Lints, link checks and checks over Markdown do not make a task a
    mutant task. If the why does not hold and the mutants file is `none`
    too, the task skipped a required step: that is a finding. If the
    mutants file exists, the missing run is a gap for the controller. If
    the why holds, checks 1 to 5 below do not apply, and check 6 still
    does.

    Check the mutant step in this order:

    1. **Inputs.** For each stated rule, the table lists each input shape
       that the rule's words cover, such as a quoted, nested, empty or
       repeated form, or a value at a boundary. Each row names a test that
       uses its shape. A shape that the rule's words plainly cover with no
       row, or a row whose test does not use its shape, is a finding: name
       the shape as a concrete input, and what a person would meet if the
       code got it wrong. A shape that the rule's words do not cover needs
       no row.
    2. **Plausible mutants.** Each mutant is a mistake a person might make
       while writing this code: a wrong condition or boundary, a missed
       case, the wrong field or value. A mutant that breaks every call at
       once (a crash or an emptied function) reads CAUGHT under any
       test, and one that changes nothing a person could see proves
       nothing. Neither counts as a mutant aimed at its targets in
       checks 3 and 4.
    3. **A mutant for each stated rule,** or an `Unreachable:` line that
       holds. The line holds when no code in this task's diff decides the
       rule. When a plan test and an excerpt cannot both hold, the mutant
       aims at the rule as the plan test pins it, and that mutant counts.
       The conflict is the implementer's reported concern, for the
       controller to rule on. It is not a missing mutant.
    4. **A catch for each test the task adds or changes,** plan tests that
       the task writes included: a `test <id>:` line in the run, or an
       `Unproven:` line that holds. The line holds only when you cannot
       name a plausible wrong version of the task's code that the test
       should catch. If you can name one, put it in the finding.
    5. **Each `Withdrawn:` line holds.** It holds when no input makes the
       mutant's result differ from the code's in anything a person could
       see, such as a return value, an output, an error or a file written.
       If you can name such an input, the line does not hold: name the
       input, which is a missing test. A number used again is a finding
       too. A `Withdrawn: K` line whose K also has a live mutant (a
       `mutant K:` line in the run, or a second `Mutant K:` line) would
       excuse that live mutant.
    6. **No plan test loosened without a ruling.** A plan test is a test
       whose code the plan gives: compare it in the diff with the brief.
       Removing or loosening an assertion, changing an expected value (even
       to one the spec gives), or skipping or deleting the test loosens it.
       Each loosening needs a line in the dispatch's test rulings that
       covers that change. A new assertion or a new input strengthens a
       test and needs no ruling.

    A mutant step that passes all six checks gives no finding.

    Each finding in this section is graded Important. The mutant step is
    part of this task's requirements, so a failed check is "a missed or
    misread requirement" in Grades. A test with no catch and no
    `Unproven:` line that holds is, on the run's evidence, a test that no
    plausible wrong version can fail: Grades' "tests that assert nothing".
    Review scope's last pass, which deletes what a person would not notice,
    does not delete these findings. A test that lets a plausible wrong
    version through lets that defect reach a person using the software, who
    would notice it.

    ## Review scope

    Report only correctness and requirement gaps. Style, naming, formatting,
    wording and phrasing that do not change what the reader does, wordiness,
    optimization that does not change correctness, code that is redundant but
    harmless, documentation polish and general suggestions are not findings: do
    not report them anywhere, the Declined to judge list included, and do not
    tack one onto a finding as an extra remark. Where the change is skill, agent
    or prompt text, an error in that text that changes what its reader does is a
    correctness defect, not polish: a contradiction, a wrong path, a wrong
    command, or an instruction with two readings.

    A fix names the smallest change that removes the defect. It leaves out any
    cleanup, simplification or alternative: a change that makes other code
    redundant is not part of the fix.

    Before you write your report, read each finding and each Declined to judge
    line once more. Delete every one, and every added remark, that a person
    using the software, or reading the text, would not notice or act on.

    ## When the requirements are silent

    Your requirements (the spec, the plan or the task brief) say what the
    software must do. They do not list every input, environment or condition
    the software will meet. For behavior they do not mention, judge by what a
    reasonable person using this software would expect: that expectation is a
    requirement, and silence is not permission. Grade such a finding by its
    effect on that person, not by whether the requirements name the input that
    triggers it.

    ## Grades

    - **Critical:** bugs, security problems, data loss, broken functionality.
    - **Important:** a missed or misread requirement, a reasonable person's
      expectation broken, wrong or fragile behavior, swallowed errors, tests
      that assert nothing.

    There is no third grade. A point that would not hurt a person using the
    software is not reported.

    ## Declined to judge

    Before your Assessment, list each behavior you considered and set aside as
    outside your requirements, one line each, with the reason. Whoever
    dispatched you rules on each line, so nothing you set aside is dropped
    silently. An empty list means you set nothing aside. A behavior that would
    hurt a reasonable person is graded, not declined. A line names a behavior
    the software has or lacks, that a person using it could meet. A style,
    naming, wording or code-shape point is not a behavior: delete it, do not
    list it.

    ## Part 1: Spec Compliance

    Compare the diff against What Was Requested:

    - **Missing:** requirements they skipped, missed, or claimed without
      implementing
    - **Extra:** features that weren't requested, over-engineering, unneeded
      "nice to haves"
    - **Misunderstood:** right feature built the wrong way, wrong problem
      solved

    If a requirement cannot be verified from this diff alone (it lives in
    unchanged code or spans tasks), report it as a ⚠️ item instead of
    broadening your search.

    Judge what the brief does not mention by "When the requirements are
    silent" above. Handling an input the brief implies is never Extra.

    ## Part 2: Code Quality

    **Code quality:**
    - Proper error handling?
    - Edge cases handled, including inputs the brief implies but does not
      name?

    **Tests:**
    - Do the new and changed tests verify real behavior, not mocks?
    - Are the task's edge cases covered?

    **Structure:**
    - Is the implementation following the file structure from the plan?

    File size, decomposition, duplication and DRY are findings only when you
    name the correctness risk they cause.

    Your report should point at evidence: file:line references for every
    finding and for any check you would otherwise answer with a bare
    "yes." A tight report that cites lines gives the controller everything
    it needs.

    Your final message is the report itself: begin directly with the
    spec-compliance verdict. Every line is a verdict, a finding with
    file:line, a Declined to judge line, or a check you ran — no preamble,
    no process narration, no closing summary.

    ## Calibration

    Grade each finding Critical or Important, as Grades says. Not everything
    is Critical. Important means this task cannot be trusted until it is
    fixed. "Coverage could be broader" is a finding only when you name the
    untested input and what a person using the software would meet.
    If the plan or brief explicitly mandates something this rubric calls a
    defect (a test that asserts nothing), that IS a finding — report it as
    Important, labeled plan-mandated. The plan's authorship does not grade
    its own work; the human decides.
    Acknowledge what was done well before listing issues — accurate praise
    helps the implementer trust the rest of the feedback.

    ## Output Format

    ### Spec Compliance

    - ✅ Spec compliant | ❌ Issues found: [what's missing/extra/misunderstood,
      with file:line references]
    - ⚠️ Cannot verify from diff: [requirements you could not verify from the
      diff alone, and what the controller should check — report alongside the
      ✅/❌ verdict for everything you could verify]

    ### Strengths
    [What's well done? Be specific.]

    ### Issues

    #### Critical (Must Fix)
    #### Important (Should Fix)

    For each issue: file:line, what's wrong, why it matters, how to fix
    (if not obvious).

    ### Declined to judge
    [One line per behavior you set aside, with the reason, or "None."]

    ### Assessment

    **Task quality:** [Approved | Needs fixes]

    **Reasoning:** [1-2 sentence technical assessment]
```

**Placeholders:**
- `[MODEL]` — REQUIRED: reviewer model per SKILL.md Model Selection
- `[BRIEF_FILE]` — REQUIRED: the task brief file
  (`<this-skill-dir>/scripts/task-brief PLAN N` prints the path; same file the
  implementer worked from) — or, for a batched dispatch, the
  `batch-N-M-brief.md` the controller composed itself, which
  that script has no multi-task mode to produce
- `[GLOBAL_CONSTRAINTS]` — the binding requirements copied verbatim from
  the plan's Global Constraints section or the spec: exact values, formats,
  and stated relationships between components (not process rules — those
  are already in this template)
- `[REPORT_FILE]` — REQUIRED: the file the implementer wrote its detailed
  report to
- `[RUN_FILE]` — REQUIRED: the path that
  `<this-skill-dir>/scripts/test-run PLAN_FILE N -- <command>` printed on its
  last line, `run: <path>` (pass the path alone), or `none: <why>` when the
  task has no command to run ([references/test-run.md](references/test-run.md))
- `[SPEC_EXCERPTS_FILE]` — REQUIRED: the absolute path of the task's
  spec excerpts file, `<workspace>/task-N-spec.md`, the file the
  implementer read. `<workspace>` is the directory
  `<this-skill-dir>/scripts/sdd-workspace PLAN_FILE` prints, and for a
  batch N is the batch's first task number
  ([references/file-handoffs.md](references/file-handoffs.md))
- `[MUTANTS_FILE]` — REQUIRED: the absolute path of the implementer's
  mutants file, `<workspace>/task-N-mutants.md`, or `none: <why>` for a
  task that is not a mutant task
  ([references/mutants.md](references/mutants.md))
- `[MUTANT_RUN_FILE]` — REQUIRED: the path that
  `<this-skill-dir>/scripts/mutant-run PLAN_FILE N -- <focused command>`
  printed on its last line, `run: <path>` (pass the path alone), or
  `none: <why>` for a task that is not a mutant task
  ([references/test-run.md](references/test-run.md))
- `[TEST_RULINGS]` — REQUIRED: the ledger's `Ruling:` lines that cover a
  change to this task's plan tests, quoted, or `none`
  ([references/fix-loop.md](references/fix-loop.md))
- `[BASE_SHA]` — commit before this task
- `[HEAD_SHA]` — current commit
- `[DIFF_FILE]` — REQUIRED: the path the controller wrote the review
  package to (`<this-skill-dir>/scripts/review-package PLAN_FILE BASE HEAD`
  reports it in a `wrote <path>: …` summary line — pass the path alone, not
  the line; the package never enters the controller's context)

**Reviewer returns:** Spec Compliance verdict (✅/❌/⚠️), Strengths, Issues
(Critical/Important), Declined to judge, Task quality verdict

A fix dispatch can address spec gaps and quality findings together;
re-review after fixes covers both verdicts.
