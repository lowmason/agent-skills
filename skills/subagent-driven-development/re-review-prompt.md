# Scoped Re-Review Prompt Template

Use this template when dispatching a re-review after an implementer has fixed
a previous round's findings. It is scoped: the re-reviewer checks whether each
finding was addressed, not whether the task as a whole is correct. The full
task review already happened.

**Routing:** dispatch to the `task-reviewer` agent if it is defined; otherwise
dispatch to `general-purpose`. Either way, paste the findings list and the diff
path — never your session history.

**Purpose:** Verify each finding from the previous review was addressed, and
that the fixes introduced nothing new.

## Dispatch Body

    You are re-reviewing fixes to one task. A previous review raised the
    findings below; an implementer has since amended the work.

    Your agent definition may carry a full-review contract and report format
    (Spec Compliance / Strengths / Issues / Assessment) — set both aside for
    this dispatch. Return only the scoped verdict shape below: per-finding
    ADDRESSED / NOT ADDRESSED plus any new findings.

    Findings from the previous round:
    <numbered findings, verbatim from the previous reviewer's report>

    The amended diff is at <DIFF_FILE>. The implementer's report, including
    its appended fix report, is at <REPORT_FILE>.
    The controller's run of the task's tests after the fixes is at
    <RUN_FILE>. A test result in the fix report that this run does not
    show is a new Important finding. A run at a commit other than the
    amended diff's head, or on a dirty working tree, is not evidence for
    these fixes: report it as a gap for the controller. When <RUN_FILE>
    is `none: <why>`, no run exists, and the fix report is the only test
    evidence.

    The controller's mutant run after the fixes is at <MUTANT_RUN_FILE>,
    and the mutants file is at <MUTANTS_FILE>. A test that the fixes add
    or change, that catches no mutant in that run (no `test <id>:` line
    names it) and that has no `Unproven:` line that holds, is a new
    Important finding. An `Unproven:` line holds only when you cannot
    name a plausible wrong version of the task's code that the test
    should catch. Check each `Withdrawn:` and `Unreachable:` line in the
    mutants file too, since a fix can change the code that the line
    rests on. A `Withdrawn:` line holds only when no input makes the
    mutant's result differ from the code's in anything a person could
    see, such as a return value, an output, an error or a file written.
    An `Unreachable:` line holds only when no code in this task's diff
    decides its rule. A `Withdrawn:` or `Unreachable:` line that does
    not hold is a new Important finding: name the input, or the code
    that decides the rule. A plan test (a test whose code the plan
    gives) that the fixes loosen with no line in <TEST_RULINGS> is a new
    Important finding.

    Each test that the fixes add or change must also fail on the revert.
    BASE is the amended diff's base. The revert is the task's diff from
    BASE to HEAD reversed, over each changed path except test files and
    project config files (`pyproject.toml`, `uv.lock`, `uv.toml`,
    `.python-version`, `requirements*.txt`, `setup.cfg`, `pytest.ini` and
    `tox.ini`, at any depth). It puts the task's code back as it was at
    BASE and keeps the tests at HEAD. The mutant run ran the tests on it,
    and its `--- revert ---` section lists each test case: `failed <id>`,
    `not loaded <name>` for a test file that cannot load, `skipped <id>`
    or `passed <id>`. A test that skips at HEAD too did not run. A test
    fails on the revert when that section lists it as failed, or lists
    its file as not loaded. A skip that the revert caused counts too. A
    test with no entry did not run: that is a gap for the controller, not
    a finding. A test that passes on the revert needs a `Keeps:` line or,
    for a plan test, a `Strengthened:` line in the mutants file that
    holds. A `Keeps:` line holds when the test checks behavior that exists
    at BASE and that the task keeps. It never holds for behavior that the
    task changes, as the amended diff shows. A `Strengthened:` line holds
    when its new test fails on the revert and checks the behavior that the
    plan test should have caught. A test with no line that holds is a new
    Important finding: name the behavior that it should have caught on
    the old code. A `revert: none: …` line holds when the amended diff
    changes only test files and project config files. Read a `no report`
    or `timeout` revert from its output, under `--- output: revert ---`.
    A `conftest.py` that cannot load means that every test needs the
    change. Any other cause is a gap for the controller.

    A mutant run at a commit other than the amended diff's head, with a
    `base:` other than the amended diff's base, or on a dirty working
    tree, is a gap for the controller too. When <MUTANT_RUN_FILE> is
    `none: <why>`, the task has no mutant step, and only the plan-test
    check applies.

    For EACH numbered finding, return one verdict:
      ADDRESSED     — the diff resolves it; say which hunk does
      NOT ADDRESSED — it remains; say what is still missing

    Then report any NEW findings the fixes introduced: only correctness and
    requirement gaps, graded Critical or Important, and a Declined to judge
    list for them (one line per behavior you set aside, with the reason, or
    "None."). Do not re-review parts of the
    task no finding touched — that review already happened and its cost is
    not worth paying twice.

    ## You Do Not Dispatch Subagents

    Do all of this review yourself. Never spawn a subagent for part of the
    diff or for a second opinion.

    Evidence you cannot see is not evidence that doesn't exist. If the
    report or its test output looks truncated, or you cannot find the
    results it claims, re-read the file at its stated path. If it is
    genuinely missing or garbled, report that as a gap. Re-running the
    suite to regenerate what you failed to read is not verification.

**Placeholders:** `<numbered findings, verbatim from the previous reviewer's
report>` is the previous round's findings, copied over and numbered so each
can get its own verdict; `<DIFF_FILE>` is the path reported by
`<this-skill-dir>/scripts/review-package <plan-file> <base> <head>` in its
`wrote <path>: …` summary line — the path alone, not the whole line;
`<REPORT_FILE>` is the implementer's report path; `<RUN_FILE>` is the path
`<this-skill-dir>/scripts/test-run` printed on its `run: <path>` line after this
round, the path alone, or `none: <why>`; `<MUTANT_RUN_FILE>` is the path
`<this-skill-dir>/scripts/mutant-run` printed on its `run: <path>` line after
this round, from a call with the task's BASE (the base of the task review's
diff), the path alone, or `none: <why>`; `<MUTANTS_FILE>` is the
implementer's mutants file, `<workspace>/task-N-mutants.md` as an absolute
path, or `none: <why>`; `<TEST_RULINGS>` is the ledger's `Ruling:` lines that
cover a change to this task's plan tests, quoted, or `none`.

**Re-reviewer returns:** per-finding verdicts (ADDRESSED / NOT ADDRESSED) plus
any new findings and their Declined to judge list.
