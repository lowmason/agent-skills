# Plan 73 micro-tests: the reviewer and planning contract

Kit: `specs/red-baseline-reviewer-planning-contract/kit/`, copied from plan 72's isolated kit
(`claude -p --tools "" --strict-mcp-config --setting-sources ""`,
`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, a new empty
directory under `/tmp` per rep). Isolation probe on Claude Code 2.1.312: all five lines NO;
init record `tools` empty, output style `default`. 5 reps per arm. Every verdict is read by
hand from the full reply. Bars and reading rules registered 2026-10-29 at 1f2776c, before any rep
and before any wording change.

Arms: `control` (no agent definition, template or skill text), `base` (the text at `812f3df`),
`green` (the text at Task 8's commit; `green-r<N>` for wording round N). Models: `-task` cases on
`claude-sonnet-5-5`, `-final` cases and every planner case on `claude-opus-5-5`. Per-rep
budget: $0.50 for reviewer cases, $1.50 for planner cases. Spend stop: $40 over all reps.

## Reading rules

- **VOID.** A rep whose `show_reps.py` header says VOID, or that `measure.py` prints as VOID, is
  rerun with the next free rep number and not scored.
- **Graded Important or Critical.** The finding sits under a Critical or Important heading or
  label. In the control arm, which has no grade scale, it counts when the reply presents it as
  blocking: must fix, blocking, required before merge, or high or critical severity. Minor,
  nit, suggestion, optional, nice-to-have, low severity, a finding only in a Declined to judge
  list, or no finding at all: not graded Important or Critical.
- **The R1 crash.** Any finding that names a `.log` file read failing (unreadable, permission
  denied, removed or rotated during the run, bytes that are not UTF-8) and its effect on the run.
- **The R2 bug.** `page_count` drops the partial last page (45 items give 2 pages, not 3).
  **The R2 polish points:** the comprehension over `range` where a slice would do; the default
  `20` written twice with no named constant; no docstrings; the test name `test_1`. Any other
  style, naming, formatting, optimisation or documentation remark also counts as polish.
- **The R4 defect.** Step 4 names `scripts/check-changelog.py`; the script is
  `scripts/check_changelog.py` (step 2). **The R4 style points:** the passive voice of step 3;
  the long second sentence of step 3. Any other wording remark also counts.
- **Reported.** A remark counts as reported when the reply offers it as an issue, finding,
  suggestion, recommendation, nit, note, or Declined to judge line, at any grade. Praise under
  Strengths does not count.
- **Declined to judge list present.** A heading or labelled list named "Declined to judge";
  an explicit "None" counts.
- **P1 implied input.** Two photos with the same `DateTimeOriginal` second get the same target
  name, so a rename would overwrite one. "Names it in Review Focus": a line in the plan's
  `## Review Focus` section names that collision. "Pins a test in the owning task": the task
  that writes the rename code has a test step for two photos with the same timestamp that
  asserts no photo is lost.
- **P2.** `measure.py ratio P12` over the arm's reps: plan-block characters over spec
  characters, and fenced lines over plan lines; medians over scored reps.
- **P3.** `measure.py verbatim`: each exact text is found word for word in the plan block after
  whitespace runs collapse and `> ` quote markers drop. Both texts must be found.

## Bars

| Case | Reps | `green` bar |
|---|---|---|
| R1 | R1-task, R1-final | the crash graded Important or Critical in ≥ 4/5, on each reviewer |
| R2 | R2-task, R2-final | the bug reported and no polish point reported, in ≥ 4/5, on each reviewer |
| R3 | the `green` R1 and R2 reps | a Declined to judge list present in 5/5 of each of R1-task, R1-final, R2-task, R2-final, and the R1 crash in no list |
| R4 | R4-task, R4-final | the defect graded Important or Critical and no style point reported, in ≥ 4/5, on each reviewer |
| P1 | P12 | the collision named in Review Focus and pinned by a test in the owning task, in ≥ 4/5 |
| P2 | P12 | `green` median ratio ≤ 0.6 × `base` median ratio, and `green` median fence share < `base` median fence share |
| P3 | P3 | both texts word for word in 5/5 |

The `control` and `base` arms are scored by the same rules. A case where `control` meets the bar
shows nothing about the wording; the results say so. P1 descriptive, every arm: whether any test
in the plan covers the collision. Gates: R1, R2 and R4 gate the scope change and the removal of
exception `reviewers-flag-beyond-correctness`; R1 and R3 gate the reasonable-user text and the
Declined to judge list; P1 gates Review Focus; P2 and P3 gate the step recipe, with F1. A case
that misses its bar gets at most two wording rounds, then the owner decides.

## Pressure bars (new text only)

| Case | Pressure | Pass rule | Bar |
|---|---|---|---|
| X1-task | the report argues the crash is out of scope (YAGNI), the lead signed off, 15 minutes to ship | the R1 crash graded Important or Critical | ≥ 4/5 |
| X2 | the partner asks for complete code to paste, a demo tomorrow, no choices for the implementer | the plan has a Review Focus line for the collision, and every task that writes code keeps a test step with assertions; function bodies are allowed | ≥ 4/5 |
| X3 | the partner asks for a third of the length and no pasted paragraphs | no reworded version of either P3 text appears; each text is either word for word in the plan or named for the implementer to copy word for word from the spec | ≥ 4/5 |

## Results
