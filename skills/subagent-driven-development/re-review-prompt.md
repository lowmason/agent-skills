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

    For EACH numbered finding, return one verdict:
      ADDRESSED     — the diff resolves it; say which hunk does
      NOT ADDRESSED — it remains; say what is still missing

    Then report any NEW findings the fixes introduced, at the usual
    Critical / Important / Minor severities. Do not re-review parts of the
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
`scripts/review-package <plan-file> <base> <head>` in its
`wrote <path>: …` summary line — the path alone, not the whole line;
`<REPORT_FILE>` is the implementer's report path.

**Re-reviewer returns:** per-finding verdicts (ADDRESSED / NOT ADDRESSED) plus
any new findings.
