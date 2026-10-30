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

### RED: control and base

Run 2026-10-29 on Claude Code 2.1.312. 80 reps, 5 per case and arm; base P12 rep 1 was the pilot.
No rep was VOID, none wrote a `.err` file, and none was rerun. The running spend under each table
is `measure.py spend` after that batch. Batches ran in this order: the base P12 pilot, then
control R1-task, R2-task, R4-task, R1-final, R2-final and R4-final, then the same six for base, then
base P12 reps 2-5, base P3, control P12 and control P3. "Declined to judge" is "no" in all 40
R1 and R2 reps, because no reply has a heading or list of that name.

#### R1-task

control (running spend $0.42): crash graded 0/5.

| Rep | Verdict | Deciding line |
|---|---|---|
| 1 | not graded | under "Minor observations (non-blocking)": "`read_text()` uses the platform default encoding, so a non-UTF-8 log would raise." |
| 2 | not graded | under "Minor observations (non-blocking)": "A non-UTF-8 log would raise `UnicodeDecodeError`." |
| 3 | not graded | under "not blockers unless the spec says otherwise": "A log file with undecodable bytes would raise." |
| 4 | not graded | under "Minor observations (non-blocking, not required by the brief)": "a non-UTF-8 log could raise." |
| 5 | not graded | under "not defects in the brief's terms": "a non-UTF-8 log could raise `UnicodeDecodeError`." |

base (running spend $1.21): crash graded 0/5. Reps 1-4 assess "Approved", and rep 5 "Needs fixes" (for the spec it could not see).

| Rep | Verdict | Deciding line |
|---|---|---|
| 1 | Minor | "`read_text()` ... raises `UnicodeDecodeError` on a non-UTF-8 log, which would abort the whole summary." |
| 2 | Minor | "`read_text()` uses the locale encoding and raises `UnicodeDecodeError` on a log with stray bytes." |
| 3 | Minor | "A non-UTF-8 log raises `UnicodeDecodeError` and aborts the whole summary." |
| 4 | Minor | "A log with non-UTF-8 bytes would raise `UnicodeDecodeError` and abort the whole summary." |
| 5 | Minor | "a non-UTF-8 byte in a log raises `UnicodeDecodeError` and aborts the whole summary." |

#### R1-final

control (running spend $0.79): crash graded 5/5.

| Rep | Verdict | Deciding line |
|---|---|---|
| 1 | blocking | under "Blocking": "**1. A file rotated mid-run crashes the job**" |
| 2 | blocking | under "Blocking": "**A file rotated mid-run crashes the job**" |
| 3 | blocking | under "Blocking": "**Rotation mid-run crashes the job**" |
| 4 | blocking | under "Blocking": "**A file rotated mid-run crashes the job**" |
| 5 | blocking | under "Blocking issues": "**A file removed between glob and read crashes the run**" |

base (running spend $1.72): crash graded 5/5.

| Rep | Verdict | Deciding line |
|---|---|---|
| 1 | Critical | "**`logsum.py:7-8`: a file that disappears between `glob` and `read_text` crashes the whole run.**" |
| 2 | Critical | "**1. A log rotated mid-run crashes the nightly job.**" |
| 3 | Critical | "**1. A log rotated mid-run crashes the nightly job.**" |
| 4 | Critical | "**`logsum.py:7-8`: Rotation race crashes the nightly job.**" |
| 5 | Critical | "**1. Log rotation during the run crashes the whole job**" |

#### R2-task

control (running spend $0.50): bug reported 5/5, bug with no polish point 0/5.

| Rep | Verdict | Deciding line (a polish point) |
|---|---|---|
| 1 | fail | "**Test name.** `test_1` says nothing about what it checks." |
| 2 | fail | "`test_1` is not a descriptive name." |
| 3 | fail | "**`page_of` is more convoluted than needed.** `items[start:end]` does the same job" |
| 4 | fail | "`page_of` can be simplified to `items[start:start + per_page]`" |
| 5 | fail | "**`page_of` is needlessly complicated.** `items[start:end]` does the same thing" |

base (running spend $1.32): bug reported 5/5 (Important in rep 1, Critical in reps 2-5), bug with no polish point 0/5.

| Rep | Verdict | Deciding line (a polish point, all under "Minor") |
|---|---|---|
| 1 | fail | "`test_1` is not descriptive." |
| 2 | fail | "`test_1` is not a descriptive name." |
| 3 | fail | "The test name `test_1` says nothing." |
| 4 | fail | "the name `test_1` is non-descriptive." |
| 5 | fail | "`test_1` is a non-descriptive name" |

#### R2-final

control (running spend $0.95): bug reported 5/5, bug with no polish point 0/5.

| Rep | Verdict | Deciding line (a polish point) |
|---|---|---|
| 1 | fail | "**`test_1` is a poor name.**" |
| 2 | fail | "**5. Style.** `items[start:end]` is the idiomatic way to write `page_of`." |
| 3 | fail | "**`page_of` could be simpler:** `return items[start:start + per_page]`" |
| 4 | fail | "**5. Rename `test_1`**" |
| 5 | fail | "**4. Minor style.** `page_of` could simply be `return items[start:end]`" |

base (running spend $1.97): bug reported 5/5 (Critical), bug with no polish point 0/5.

| Rep | Verdict | Deciding line (a polish point, all under "Minor") |
|---|---|---|
| 1 | fail | "6. **No docstrings.**" (also the slice and `test_1`) |
| 2 | fail | "`test_1` is not a descriptive name." |
| 3 | fail | "`test_1` is not descriptive." |
| 4 | fail | "The name `test_1` describes nothing." |
| 5 | fail | "**6. The test name `test_1` says nothing about what it checks.**" |

R2 note: remarks that fit no registered category do not change a verdict. All 20 R2 reps flag
`page < 1` in `page_of`, most flag `per_page <= 0`, and all ask for more test cases. 18 of the 20 base
R2 and R4 reps also flag a SHA mismatch: the dispatch's head `9b8e4d0` is not the diff's commit.
That is a kit artifact, because `TASK_SHAS` is shared by every case. The control dispatch names
no SHA, so no control rep flags it.

#### R4-task

control (running spend $0.58): defect graded 5/5 (rep 1 "Needed before approval", reps 2-5 "Must fix"), defect with no style point 0/5.

| Rep | Verdict | Deciding line (a style point) |
|---|---|---|
| 1 | fail | "Step 3 is a long passive sentence" |
| 2 | fail | under "Should fix": "Step 3 is a long passive sentence" |
| 3 | fail | under "Should fix": "Step 3 is a long passive sentence" |
| 4 | fail | under "Should fix": "Step 3 is a long, passive sentence" |
| 5 | fail | under "should fix": "This step is passive and padded" |

base (running spend $1.41): defect graded Important 5/5, defect with no style point 0/5. Every rep grades the style point Important under the task's plain-English Global Constraint; it still counts as a style point.

| Rep | Verdict | Deciding line (a style point, under "Important") |
|---|---|---|
| 1 | fail | "step 3: this is not plain English. It is one long sentence in the passive voice" |
| 2 | fail | "`SKILL.md:12`: rewrite in plain English and drop the pipeline claim." |
| 3 | fail | "step 3: this breaks the plain-English global constraint." |
| 4 | fail | "The step is a single run-on sentence in passive, stilted phrasing" |
| 5 | fail | "step 3: it violates the plain-English constraint" |

#### R4-final

control (running spend $1.11): defect graded 5/5 (blocking or must fix in every rep; rep 2 also labels it Important), defect with no style point 0/5.

| Rep | Verdict | Deciding line (a style point) |
|---|---|---|
| 1 | fail | "**2. Should fix: step 3 doesn't match the style of the list.**" |
| 2 | fail | "### 2. Step 3 doesn't match the checklist's style (Minor)" |
| 3 | fail | "### 2. Style: step 3 doesn't match the surrounding checklist (should fix)" |
| 4 | fail | "### 2. Should fix: step 3 doesn't match the surrounding style" |
| 5 | fail | "### 2. Should fix: step 3 is verbose and adds unrequested content" |

base (running spend $2.22): defect graded 5/5 (Critical, or Important in rep 3), defect with no style point 0/5.

| Rep | Verdict | Deciding line (a style point) |
|---|---|---|
| 1 | fail | Important: "the step is much wordier than the rest of the list." |
| 2 | fail | Important: "step 3: content goes beyond the plan, plus a wordy passive voice." |
| 3 | fail | Minor: "step 3 is much wordier than the steps around it." |
| 4 | fail | Important: "step 3: the wording doesn't match the checklist style." |
| 5 | fail | Minor: "step 3 is wordy and written in the passive voice." |

R4 note: the step 3 pipeline claim (unrequested content) and the logic of step 4's recovery
advice are not wording remarks. They are flagged in many reps and do not change a verdict.

#### P12 (P1 and P2)

control (running spend $4.13): P1 0/5. No plan has a `## Review Focus` section. Every plan puts
the same-second collision in an open question and plans a collision test in its own task.

| Rep | Verdict | Deciding line | Collision test (descriptive) | Ratio | Fence share |
|---|---|---|---|---|---|
| 1 | fail | no `## Review Focus` section | yes, Task 5, "The expected outcome follows the decision." | 5.00 | 0.00 |
| 2 | fail | no `## Review Focus` section | yes, Task 6, "No file is lost; the file count is unchanged." | 5.51 | 0.00 |
| 3 | fail | no `## Review Focus` section | yes, Task 5, "no file is lost or overwritten" | 5.22 | 0.00 |
| 4 | fail | no `## Review Focus` section | yes, step 6, "Every test checks that no file is lost." | 5.18 | 0.00 |
| 5 | fail | no `## Review Focus` section | yes, Task 5, "byte-for-byte content checks show no photo was lost" | 5.13 | 0.00 |

base (running spend $3.37 after reps 2-5; the pilot rep 1 cost $0.34): P1 0/5. No plan has a
`## Review Focus` section; the collision sits in a defaults list ("Defaults pending owner review",
"Defaults settled in this plan (for review)") or in the partner message. Four plans pin an on-disk
test in Task 3, the task that holds the rename call.

| Rep | Verdict | Deciding line | Collision test (descriptive) | Ratio | Fence share |
|---|---|---|---|---|---|
| 1 | fail | no `## Review Focus` section | yes, Task 3 `test_main_lists_no_date_and_name_taken` asserts both photos on disk | 16.58 | 0.64 |
| 2 | fail | no `## Review Focus` section | yes, Task 2 only: `test_same_timestamp_gets_numbered_suffix` asserts two distinct planned names | 15.56 | 0.61 |
| 3 | fail | no `## Review Focus` section | yes, Task 3 `test_name_taken_listed_and_not_overwritten` asserts both photos on disk | 16.24 | 0.65 |
| 4 | fail | no `## Review Focus` section | yes, Task 3 `test_main_lists_undated_and_taken_after_the_run` asserts both photos on disk | 16.79 | 0.64 |
| 5 | fail | no `## Review Focus` section | yes, Task 3 `test_lists_undated_and_name_taken_photos_after_the_run` asserts both photos on disk | 15.67 | 0.63 |

P2 base medians, the inputs to Task 8's P2 bar: median ratio 16.24 and median fence share 0.64
(unrounded 16.2365 and 0.6365), so `green` must reach a median ratio ≤ 9.74 (0.6 × 16.2365 =
9.7419) and a median fence share below 0.6365; compare against the unrounded figures. The control
medians are ratio 5.18 and fence share 0.00. The control meets the P2 bar (5.18 ≤ 9.74 and
0.00 < 0.64), so P2 shows nothing about the wording.

#### P3

control (running spend $4.33): both texts word for word 5/5. Every plan drops the spec's `> `
and inserts a plain paragraph.

| Rep | Verdict | Deciding line (`measure.py verbatim`, confirmed by reading) |
|---|---|---|
| 1 | pass | text1=yes text2=yes; Task 1 "After" block, Task 2 "After" block and the expected final file |
| 2 | pass | text1=yes text2=yes; the step 1 and step 2 fenced blocks and the expected file |
| 3 | pass | text1=yes text2=yes; the step 1 and step 2 fenced blocks and the expected file |
| 4 | pass | text1=yes text2=yes; the step 1 and step 2 fenced blocks and the expected file |
| 5 | pass | text1=yes text2=yes; the step 1 and step 2 fenced blocks and the expected file |

base (running spend $3.75): both texts word for word 5/5. Every plan is one task, with `grep -F`
presence checks as the failing test.

| Rep | Verdict | Deciding line (`measure.py verbatim`, confirmed by reading) |
|---|---|---|
| 1 | pass | text1=yes text2=yes; the Step 3 full-file replacement block |
| 2 | pass | text1=yes text2=yes; the Step 3 and Step 4 fenced blocks and the full file |
| 3 | pass | text1=yes text2=yes; the Step 3 full-file replacement block |
| 4 | pass | text1=yes text2=yes; the Step 3 and Step 4 fenced blocks and the full file |
| 5 | pass | text1=yes text2=yes; the Step 3 full-file replacement block |

#### Summary

On the current text, the task reviewer grades the R1 crash Minor (graded 0/5) while the final
reviewer grades it Critical (5/5), both reviewers report the R2 bug and the R4 defect together
with a polish or style point (0/5 on each reviewer), no plan has a Review Focus section (P1 0/5),
the plans run a median 16.24 times the spec's length with 0.64 of their lines fenced (P2), and
both P3 texts are word for word (5/5). The control meets the registered bar on P2 (median ratio
5.18 ≤ 9.74, fence share 0.00 < 0.64) and P3 (5/5), so those two cases show nothing about the
wording. It is at ceiling on R1-final (5/5), but R1 as a case needs both reviewers and R1-task is
0/5 in the control, so the control misses R1. It also misses R2, R4 and P1.

### RED amendment: R4-task fixture

Run 2026-10-29 on Claude Code 2.1.312, by the owner's ruling of 2026-10-29. Review of Task 2 found
that the R4-task case gave the reviewer a Global Constraint that turns the planted style point into
a stated requirement. The control R4-task prompt and both R4-final prompts do not carry it. The
owner ruled to drop that line from the R4-task case, rebuild its prompts and rerun the RED reps for
R4-task. In `kit/cases.py`, the `'R4-task'` entry's constraints argument changed from
`- Skill text follows the repo's plain-English rule.` to `- None beyond the task brief.`. Nothing
else in the file changed. The amended `base` prompt is `base-r4task-amended/R4-task.txt`, built
with `build_prompts.py 812f3df`. Its only difference from `base/R4-task.txt` is that constraint line.

The original `base/R4-task` and `control/R4-task` reps stay in the repository as the first RED
record. The control prompt has no constraints block. A rebuild of it is byte-identical to
`control/R4-task.txt` (`cmp` exit 0), so the 5 control R4-task reps stand and were not rerun. No
amended rep was VOID, and none was rerun.

base, amended (running spend $4.43): defect graded Important 5/5, defect with no style point 0/5.

| Rep | Verdict | Deciding line (a style point, with its grade) |
|---|---|---|
| 1 | fail | Important: "`skills/release-checklist/SKILL.md` (step 3): the sentence is wordy and passive" |
| 2 | fail | Important: "`SKILL.md:14`: the step is a single wordy, passive sentence" |
| 3 | fail | Minor: "(step 3): the wording is passive and wordy" |
| 4 | fail | Minor: "Step 3 is wordy, passive, and written as one long run-on sentence" |
| 5 | fail | Minor: "`SKILL.md:11`: the passive, verbose phrasing ... does not match the terse imperative style" |

Task 8's R4-task `green` arm compares against these amended `base` reps and the original `control`
reps.

R4 amendment note: remarks that fit no registered category do not change a verdict. All 5 reps flag
the step 3 pipeline claim as unrequested content and the head SHA mismatch (`7e2a5f1` in the diff,
`9b8e4d0` in the dispatch). All 5 say the report's self-review ("the wording follows the brief") is
not accurate, and reps 4 and 5 grade that remark Important. Reps 1, 3 and 5 note that step 3 joins
two actions in one step. Rep 1 also notes that the report shows no commit hash.

Without the constraint, the amended `base` still grades the defect Important in every rep and still
reports the step 3 style point in every rep (0/5). The style point's grade fell from Important in
5/5 to Important in 2/5 and Minor in 3/5, and no rep cites a style rule. The control does not meet
the R4-task bar either: its original table shows the defect with no style point in 0/5.

### GREEN

Run 2026-10-29 on Claude Code 2.1.312, on the text at `5d59230` (`GREEN_SHA`). The prompts were
built with `build_prompts.py 5d59230 green`. `green/MANIFEST.txt` lists the four reviewer files for
the R cases and `skills/writing-plans/SKILL.md` alone for the P cases; `references/step-recipe.md`
does not exist at `5d59230`, because the Task 7 Step 6 fallback did not run. The Channel 3 grep (Task 8
Step 1) printed nothing. 40 reps, 5 per case, in the brief's order. No rep was VOID, none wrote a
`.err` file, and none was rerun. The running spend under each table is `measure.py spend` after
that batch. No wording round has run.

#### R1-task

green (running spend $4.55): crash graded 5/5, all Important.

| Rep | Verdict | Deciding line |
|---|---|---|
| 1 | Important | "One log containing a non-UTF-8 byte raises `UnicodeDecodeError` and aborts the whole summary, so no counts are printed for any file." |
| 2 | Important | "A single log file containing a non-UTF-8 byte raises `UnicodeDecodeError`, and no counts are printed for any file in the folder." |
| 3 | Important | "One log file with a stray non-UTF-8 byte raises `UnicodeDecodeError` and aborts the whole summary" |
| 4 | Important | "A single log with a stray non-UTF-8 byte aborts the whole summary with `UnicodeDecodeError`" |
| 5 | Important | "One log file containing a non-UTF-8 byte, which is common in real logs, raises `UnicodeDecodeError`. That aborts the whole summary" |

#### R1-final

green (running spend $5.08): crash graded 5/5, all Critical.

| Rep | Verdict | Deciding line |
|---|---|---|
| 1 | Critical | "**1. A log rotated mid-run crashes the whole job (`logsum.py:7-8`)**" |
| 2 | Critical | "**1. A log rotated away mid-run crashes the whole job — `logsum.py:7-8`**" |
| 3 | Critical | "**1. One unreadable or rotated file crashes the whole nightly run** (`logsum.py:7-8`)" |
| 4 | Critical | "**1. A file rotated away mid-run crashes the whole job** (`logsum.py:7-8`)" |
| 5 | Critical | "**1. A file rotated away mid-run crashes the whole job** (`logsum.py:7-8`)" |

#### R2-task

green (running spend $4.65): bug reported 5/5 (Critical), bug with no polish point 2/5.

| Rep | Verdict | Deciding line |
|---|---|---|
| 1 | fail | under Important: "`tests/test_paging.py:4`: the test is named `test_1`, which describes nothing." |
| 2 | pass | Critical: "`paging.py:10`: `return n_items // per_page` floors instead of rounding up."; no polish point |
| 3 | fail | under Important: "`tests/test_paging.py:4`: `test_1` does not say what it checks. This is only a correctness risk because the test set is thin" |
| 4 | pass | Critical: "`page_count` uses floor division (`n_items // per_page`), so it undercounts"; no polish point |
| 5 | fail | under Important: "The existing test `test_1` is also not descriptive, which makes failures hard to read." |

In reps 1, 3 and 5 the `test_1` remark sits inside an Important test-coverage finding.

#### R2-final

green (running spend $5.33): bug reported 5/5 (Critical), bug with no polish point 4/5.

| Rep | Verdict | Deciding line |
|---|---|---|
| 1 | pass | Critical: "**`paging.py:10`: `page_count` rounds down, so it drops the partial last page.**"; no polish point |
| 2 | fail | under Important, after the `page < 1` guard: "Then slice with `items[start:end]` instead of indexing." (the registered slice point) |
| 3 | pass | Critical: "**`paging.py:10` — `page_count` drops the partial last page.**"; the `per_page = 20` default is named only under Strengths |
| 4 | pass | Critical: "**`paging.py:10`: `page_count` drops the partial last page.**"; `test_1` is named only under Strengths, as praise |
| 5 | pass | Critical: "**`paging.py:10` — `page_count` drops the partial last page.**"; no polish point |

R2 green note: three remarks fit no registered category; the verdicts above do not count them.
- Rep 2 of R2-final gives the slice as part of its `page <= 0` fix, and the same finding names an
  `IndexError` that a slice avoids. Counted literally as the registered slice point. With it not
  counted, R2-final is 5/5.
- All 10 green R2 reps grade `page < 1` (and most `per_page <= 0`) handling Important. With that
  remark counted as polish, R2-task and R2-final are both 0/5.
- All 10 say the `n_items == 0` special case becomes unneeded after the ceiling-division fix (for
  example "redundant but harmless"). With it counted as polish, both are 0/5.
- The RED R2 reps carry the same two remarks (by a regex aid, not a verdict: `page < 1` in 20 of
  20, the special-case note in 18 of 20), and the RED reading did not count them.
- All 5 R2-task reps flag the head SHA mismatch under ⚠️ (the kit artifact in the RED R2 note).
- R2 misses on R2-task under every count, so none of these changes the case result. The counts
  still matter for R2-final and for the D16 trim; see "Contested remarks and the gating reading".

#### R4-task

green (running spend $4.76): defect graded Important 5/5, defect with no style point 1/5.

| Rep | Verdict | Deciding line |
|---|---|---|
| 1 | fail | under Important: "The phrasing is also convoluted ("is to be tagged by you… After that has been done… should then be pushed")." |
| 2 | pass | Important: "the script name is `scripts/check-changelog.py`, but step 2 uses `scripts/check_changelog.py`."; no wording remark |
| 3 | fail | Declined to judge: "Wording and verbosity of step 3 ("The release is to be tagged by you…"): style, with no change in what the reader does." |
| 4 | fail | under Important: "step 3: the wording is convoluted ("The release is to be tagged by you… After that has been done and the tag exists locally, the tag should then be pushed…")." |
| 5 | fail | Declined to judge: "Step 3 is wordy ("The release is to be tagged by you…", plus the pipeline explanation): a style and conciseness matter." |

In reps 3 and 5 the style point is only in the Declined to judge list, which the "Reported" rule
counts. Reps 1-4 grade the step 3 pipeline claim Important, and all 5 flag the head SHA mismatch;
by the RED R4 note neither is a wording remark. With them counted as style, rep 2 also fails (0/5).

#### R4-final

green (running spend $5.56): defect graded Important 5/5, defect with no style point 5/5.

| Rep | Verdict | Deciding line |
|---|---|---|
| 1 | pass | Important: "**`skills/release-checklist/SKILL.md:12` (step 4): wrong script path.**"; no wording remark |
| 2 | pass | Important: "**`skills/release-checklist/SKILL.md:12`: wrong script path in step 4.**"; no wording remark |
| 3 | pass | Important 1: "(step 4): wrong script path."; Important 2: "(step 4): "before you retry" can be read two ways." |
| 4 | pass | Important: "(new step 4): wrong script path."; its fix adds "Or better, say "run the changelog check (step 2) again" so the two references cannot drift apart." |
| 5 | pass | Important 1: "(step 4): wrong script path."; Important 2: "(step 4): "retry" has two readings. This is inherited from the plan." |

No rep names the passive voice or the long sentence of step 3. R4 green note: the "retry has two
readings" finding (reps 3 and 5) is about the logic of step 4's recovery advice, which the RED R4
note rules is not a wording remark. With it counted as style, R4-final is 3/5; with rep 4's
alternative fix also counted, 2/5. R4 misses on R4-task under every count, so neither changes the
case result.

#### R3

green: a Declined to judge list in 5/5 of each of R1-task (reps 1-3 "None.", reps 4-5 one line
each), R1-final (2-4 lines each), R2-task (all "None.") and R2-final (2-4 lines each). The R1 crash
is in no list. R3 met. The `control` and `base` arms have no such list in any of their 40 R1 and R2
reps. Two near-misses were checked against the R1 crash rule and neither counts: R1-final rep 1's
line that each file is read fully into memory (which could exhaust memory on very large logs)
names no read failure, and R1-final rep 2's line on partial lines from a
file being appended to is not a failure.

#### P12 (P1 and P2)

green (running spend $6.81): P1 2/5. Every plan has a `## Review Focus` section that names the
same-second collision (5/5). Every plan has three tasks: Task 1 reads the date, Task 2 plans the
renames and settles collisions, and Task 3 holds the `Path.rename` call, so Task 3 is the owning
task, as in the RED base record.

| Rep | Verdict | Deciding line | Collision test (descriptive) | Ratio | Fence share |
|---|---|---|---|---|---|
| 1 | fail | Review Focus "**Two photos taken in the same second** (burst shots): no photo is overwritten or lost."; Task 3 tests only one dated photo | yes, Task 2 only: `test_same_second_gets_suffix` asserts distinct planned names | 12.74 | 0.56 |
| 2 | pass | Review Focus "**Burst shots taken in the same second.**"; Task 3 `test_renames_and_prints` asserts both photos on disk | yes, Task 2 and Task 3 | 12.09 | 0.49 |
| 3 | fail | Review Focus "**Two photos taken in the same second** (burst shots): both survive."; Task 3 tests only one dated photo | yes, Task 2 only: `test_same_second_gets_suffix` asserts distinct planned names | 13.15 | 0.49 |
| 4 | pass | Review Focus "**Two photos taken in the same second (burst shots).**"; Task 3 `test_run_renames_and_prints` asserts both photos on disk | yes, Task 2 and Task 3 | 12.47 | 0.47 |
| 5 | fail | Review Focus "**Two photos taken in the same second, or a target name already used by another file.**"; Task 3 `test_rerun_renames_nothing` asserts only an empty second run, not that both photos remain | yes, Task 2 only: `test_same_second_gets_suffix` asserts distinct planned names | 11.95 | 0.46 |

P1 second count, under a reading added after the RED reps (any task has a test step for two
same-timestamp photos that asserts no photo is lost): 2/5, reps 2 and 4. Both readings give 2/5,
because every verdict turns on the on-disk assertion. A third reading, added after the RED reps
and not a gating one, is "a test pins the collision by distinct planned names in any task": 5/5,
since each plan's Task 2 has such a test (reps 2 and 4 also test it on disk in Task 3). Every
plan's own Review Focus line points at that Task 2 test, so the miss is about where the pinning
test asserts, not whether one exists.

P2 arithmetic, unrounded (`measure` functions and `statistics.median`): `green` median ratio
12.4650 (reps 12.7379, 12.0867, 13.1507, 12.4650, 11.9478); 0.6 × `base` median ratio 16.2365 =
9.7419; 12.4650 > 9.7419, so the ratio part is missed. `green` median fence share 0.4854 (reps
0.5642, 0.4893, 0.4854, 0.4741, 0.4630) < `base` 0.6365, so the fence part is met. P2 missed.

#### P3

green (running spend $7.30): both texts word for word 5/5.

| Rep | Verdict | Deciding line (`measure.py verbatim`, confirmed by reading) |
|---|---|---|
| 1 | pass | text1=yes text2=yes; the Step 1 check-script constants and the Step 3 fenced lines |
| 2 | pass | text1=yes text2=yes; the Step 2 and Step 3 fenced lines and the Step 4 and 5 expected output |
| 3 | pass | text1=yes text2=yes; the Step 1 check script and the Step 3 plain lines |
| 4 | pass | text1=yes text2=yes; the Step 2 fenced lines and the Step 3 expected output |
| 5 | pass | text1=yes text2=yes; the Step 1 check script and the Step 3 inline-code bullets |

Every plan is one task with a `## Review Focus` section.

#### The seven bars

For R4-task, `base` is the amended reps (`base-r4task-amended/R4-task`) and `control` the original
control reps. Every other case uses the original `control/` and `base/` reps.

| Case | `control` | `base` | `green` | Bar | Control also meets |
|---|---|---|---|---|---|
| R1 | task 0/5, final 5/5 | task 0/5, final 5/5 | task 5/5, final 5/5 | met | no |
| R2 | task 0/5, final 0/5 | task 0/5, final 0/5 | literal: task 2/5, final 4/5. Gating (see "Contested remarks"): task 0/5, final 0/5 | missed on both reviewers (literal: R2-task) | no |
| R3 | list in 0/20 | list in 0/20 | list in 20/20, crash in none | met | no |
| R4 | task 0/5, final 0/5 | task 0/5 (amended), final 0/5 | task 1/5, final 5/5 gating (3/5 if the "retry" remarks were counted as wording) | missed (R4-task) | no |
| P1 | 0/5 | 0/5 | 2/5 | missed | no |
| P2 | ratio 5.18, fence 0.00 | ratio 16.24, fence 0.64 | ratio 12.47, fence 0.49 | missed (ratio 12.4650 > 9.7419) | yes: the control meets the P2 bar, so P2 shows nothing about the wording |
| P3 | 5/5 | 5/5 | 5/5 | met | yes: shows nothing about the wording |

R1, R3 and P3 meet their bars on `5d59230`. R2, R4, P1 and P2 miss. Read literally, R2 and R4
miss on the task reviewer only and the final reviewer meets both; under the gating reading of
the contested remarks (next section) R4 still misses on the task reviewer only, and R2 misses on
both reviewers. P2 meets its fence-share part and misses its ratio part. No wording round has
run, so `GREEN_SHA` stays `5d59230` and the step-recipe commit list is unchanged.

#### Contested remarks and the gating reading

Added by the controller after the GREEN reps, on the Task 8 review's findings. Some remarks fit no
registered category, and the verdict tables above counted them under the literal reading. Both
counts are shown. The gating count decides whether a bar is met, and it applies the new block's
own definitions, which Task 4 committed before any green rep. The block's Review scope names "an
instruction with two readings" as a correctness defect, not polish, and "optimization that does
not change correctness" as not a finding.

| Remark | Reading under the block | R2-task | R2-final | R4-final |
|---|---|---|---|---|
| `page < 1` and `per_page <= 0` handling (wrong data or `IndexError`) | correctness; not polish | no change | no change | n/a |
| "the `n_items == 0` branch becomes redundant or unneeded" (10 of 10 R2 green reps) | optimisation or cleanup with no effect on correctness; polish | literal 2/5, gating 0/5 | literal 4/5, gating 0/5 | n/a |
| "retry" or "before you retry" has two readings (R4-final reps 3 and 5) | an instruction with two readings; a correctness defect, not a style point | n/a | n/a | gating 5/5; 3/5 if counted as wording |

The RED reps carry the same remarks. The RED reading did not count them, and RED R2 stays 0/5 on
the registered polish points either way. The registered catch-all ("any other style, naming,
formatting, optimisation or documentation remark also counts as polish") arguably covers the
redundancy remark already. If so, 0/5 is the registered count for R2 and 4/5 is the lenient one.
A bar is met only on the gating count. Round 1 therefore targets R2 on both reviewers and R4 on
the task reviewer. Because R2-final misses on the gating count, round 1 also runs the D16 trim of
the "What to Check" list in `requesting-code-review/code-reviewer.md` (Task 8 Step 5, item 1).

### GREEN round 1

Run 2026-10-29 on Claude Code 2.1.312. This is Task 8 Step 5, wording round 1, for R2 (both
reviewers), R4 (task reviewer), P1 and P2. The controller wrote the new wording. Three text commits:

| Commit | Subject | Change (old → new) |
|---|---|---|
| `edb935b` | fix(reviewers): wording round 1, no style remarks, no polish in the declined list | Shared block, all four copies. Review scope adds "wording and phrasing that do not change what the reader does, wordiness" and "code that is redundant but harmless" to the non-findings, and "do not tack one onto a finding as an extra remark". A new paragraph: "Before you write your report, read each finding and each Declined to judge line once more. Delete every one, and every added remark, that a person using the software, or reading the text, would not notice or act on." Declined to judge: "A line names a behavior, never a style point." → "A line names a behavior the software has or lacks, never a style, naming, wording or code-shape point." D16: four lines leave requesting-code-review's "What to Check" list (separation of concerns, DRY, scalability and performance, documentation complete). |
| `b1c6504` | fix(writing-plans): wording round 1, pin Review Focus where the person sees the failure | Review Focus template: "add the test that pins it to the task that owns the code" → "add the test that pins it, in the task whose code the person would see fail", plus "The test asserts what the person sees (nothing lost, the right output), not a value that an earlier task computes on the way." |
| `62fe501` | fix(writing-plans): wording round 1, name a length threshold in Proportion (step recipe) | Self-Review item 5: "A plan several times longer than the spec" → "A plan more than about five times as long as the spec". NOTICE's step-recipe bullet records the threshold. |

`NEW_SHA` is `62fe501`. The step-recipe commit list is now `aaa37f0`, `62fe501`. The prompts were
built with `build_prompts.py 62fe501 green-r1` for all eight cases. `green-r1/MANIFEST.txt` lists
the same files per case as `green/MANIFEST.txt` (the four reviewer files for the R cases,
`skills/writing-plans/SKILL.md` alone for the P cases). Each `green-r1` prompt differs from its
`green` prompt only by the changed lines above. The Channel 3 grep printed nothing. 40 reps, 5 per
case, in Task 8 Step 3's order. No rep was VOID, none wrote a `.err` file, and none was rerun. The
running spend under each table is `measure.py spend` after that batch.

The verdicts apply the registered rules and the gating reading in "Contested remarks and the
gating reading". "Literal" counts the registered points only. "Gating" also counts the remarks
that section decides.

#### R1-task (round 1)

green-r1 (running spend $7.41): crash graded 5/5, all Important.

| Rep | Verdict | Deciding line |
|---|---|---|
| 1 | Important | "A single log file with a stray non-UTF-8 byte raises `UnicodeDecodeError` and aborts the whole summary, so the user gets no counts for any file." |
| 2 | Important | "One log file with a stray non-UTF-8 byte raises `UnicodeDecodeError` and aborts the whole summary, so no counts are printed for any file." |
| 3 | Important | "A log file with a stray non-UTF-8 byte raises `UnicodeDecodeError` and aborts the whole summary, so the user gets a traceback and no counts for any file." |
| 4 | Important | "A single log file with an undecodable byte raises `UnicodeDecodeError` and aborts the whole summary, so no counts are produced for any file." |
| 5 | Important | "One log file with a non-UTF-8 byte raises `UnicodeDecodeError`, and the user gets no counts for any file." |

#### R2-task (round 1)

green-r1 (running spend $7.51): bug reported 5/5 (Critical). Bug with no polish point: literal 3/5,
gating 0/5.

| Rep | Literal | Gating | Deciding quote |
|---|---|---|---|
| 1 | pass | fail | Critical fix: "The `n_items == 0` special case then becomes unnecessary." |
| 2 | fail | fail | under Important: "The test is also named `test_1` (line 4), which says nothing about what it checks."; Critical fix: "The `n_items == 0` special case then becomes redundant." |
| 3 | pass | fail | Critical fix: "The `n_items == 0` special case then becomes redundant, since the formula already returns 0." |
| 4 | fail | fail | Important: "`tests/test_paging.py:4`: the test name `test_1` does not say what it checks. Rename it so a failure is understandable."; Critical fix: "The `n_items == 0` special case then becomes unnecessary." |
| 5 | pass | fail | Critical fix: "The `n_items == 0` special case then becomes redundant." |

In all 5 reps the redundancy remark is a clause inside the Critical bug's fix. `page < 1` handling
is Important in 5/5 (correctness under the gating table). All 5 flag the head SHA mismatch under
⚠️ (the kit artifact in the RED R2 note).

#### R4-task (round 1)

green-r1 (running spend $7.62): defect graded Important 5/5. Defect with no style point: literal
3/5, gating 3/5 (the gating section decides no R4-task remark).

| Rep | Verdict | Deciding quote |
|---|---|---|
| 1 | pass | Important: "step 4: `scripts/check-changelog.py` conflicts with `scripts/check_changelog.py` in step 2."; no wording remark |
| 2 | fail | Important: "step 3: "The release is to be tagged by you with `git tag -a vX.Y.Z`. After that has been done and the tag exists locally, the tag should then be pushed..." is passive and loosely phrased." Its fix: "state both actions as imperatives" |
| 3 | pass | Important: "new step 4: the retry step uses `scripts/check-changelog.py` (hyphen), which does not match step 2's `scripts/check_changelog.py` (underscore)."; no wording remark |
| 4 | pass | Important: "step 4: `scripts/check-changelog.py` conflicts with `scripts/check_changelog.py` in step 2."; no wording remark |
| 5 | fail | Declined to judge: "Step 3's long, indirect wording ("is to be tagged by you… should then be pushed"): this is wordiness and phrasing with a single reading, so it is not a correctness finding." |

R4-task round 1 note: rep 2's step 3 finding names the passive voice, a registered style point, so
it is scored as one. The same finding also argues "whether the push is mandatory or conditional on
the pipeline is unclear". If that claim were credited as "an instruction with two readings" under
the block's definition, rep 2 would pass and R4-task would be 4/5. The gating section does not
decide this remark, so the scored count is 3/5 on both readings. Rep 5's style point is only on the
Declined to judge list, which the "Reported" rule counts. Rep 2 also calls step 3 "a single run-on
instruction" and accepts it (two actions in one step: no registered category, RED R4 note). Reps
3-5 flag the step 3 pipeline claim, and all 5 flag the head SHA mismatch. By the RED R4 note
neither is a wording remark. Rep 3's fix also offers "or refer to "the changelog check from step 2"", an alternative wording of the kind the GREEN R4-final note counted for rep 4; with it counted as a wording remark, R4-task round 1 is 2/5, and the bar is missed either way.

#### R1-final (round 1)

green-r1 (running spend $7.91): crash graded 5/5, all Critical.

| Rep | Verdict | Deciding line |
|---|---|---|
| 1 | Critical | "**1. One rotated or unreadable file crashes the whole nightly run.** `logsum.py:7-8`" |
| 2 | Critical | "**1. A rotating log crashes the whole nightly run** (`logsum.py:7-8`)" |
| 3 | Critical | "**1. A file rotated away mid-run crashes the whole job — `logsum.py:7-8`**" |
| 4 | Critical | "**1. A log rotated mid-run crashes the whole job. `logsum.py:7-8`**" |
| 5 | Critical | "**1. A log rotated mid-run crashes the whole nightly job (`logsum.py:7-8`)**" |

#### R2-final (round 1)

green-r1 (running spend $8.15): bug reported 5/5 (Critical). Bug with no polish point: literal 2/5,
gating 0/5.

| Rep | Literal | Gating | Deciding quote |
|---|---|---|---|
| 1 | fail | fail | `page <= 0` fix: "Alternatively, use `items[max(start, 0):end]` combined with a `page < 1` guard." (the slice point); Critical fix: "so the special case becomes unnecessary." |
| 2 | pass | fail | Critical fix: "With that, the `n_items == 0` special case is no longer needed." |
| 3 | fail | fail | Critical fix: "The `n_items == 0` branch is then redundant but harmless."; `page <= 0` fix: "Slicing with clamped bounds, e.g. `items[start:end]` behind a `page >= 1` guard, is also simpler." (the slice point) |
| 4 | pass | fail | Critical fix: "The `n_items == 0` special case then becomes unnecessary." |
| 5 | fail | fail | Critical fix: "The `n_items == 0` special case then becomes unnecessary."; `page < 1` fix: "Alternatively, clamp `start` at 0 and slice with `items[start:end]` after validating `page`." (the slice point) |

R2-final round 1 note: reps 1 and 5 give the slice only as an alternative fix inside the Important
`page < 1` finding, as GREEN R2-final rep 2 did, and are counted literally as the registered slice
point. With those two not counted, literal is 4/5; gating stays 0/5. Rep 3 calls the slice "also
simpler", which is a plain polish remark. All 5 reps make the redundancy remark, rep 3 in the
words the new block names ("redundant but harmless").

#### R4-final (round 1)

green-r1 (running spend $8.35): defect graded Important or Critical 5/5 (Critical in reps 1-4,
Important in rep 5). Defect with no style point: gating 5/5; 4/5 if the "before you retry"
two-readings remark is counted as wording.

| Rep | Gating | Retry as wording | Deciding quote |
|---|---|---|---|
| 1 | pass | pass | Critical: "**`skills/release-checklist/SKILL.md:12` (step 4): the changelog check path is wrong.**"; no wording remark |
| 2 | pass | pass | Critical: "**`skills/release-checklist/SKILL.md:13`: wrong script path in the retry step.**"; no wording remark |
| 3 | pass | pass | Critical: "**`skills/release-checklist/SKILL.md:12` (step 4): the changelog script path is wrong.**"; no wording remark |
| 4 | pass | fail | Critical: "step 4 names a script that doesn't match the existing one."; Important: "A reader can reasonably take "before you retry" to mean "push anyway once you've run it"." |
| 5 | pass | pass | Important: "**`skills/release-checklist/SKILL.md:12`: step 4 names a script that step 2 does not.**"; no wording remark |

No rep names the passive voice or the long sentence of step 3. Reps 1 and 3 put "step 4 does not
say what to do if the re-run check fails" on the Declined list, and rep 4 grades it Important.
That is the logic of step 4's recovery advice (RED R4 note), not a wording remark, on both counts.

#### R3 (round 1)

green-r1: a Declined to judge list in 5/5 of each of R1-task (1-2 lines each), R1-final (1-4
lines), R2-task (reps 1, 2 and 4 "None.", reps 3 and 5 one line) and R2-final (1-3 lines). The R1
crash is in no list. R3 met. Two near-misses were checked against the R1 crash rule, and neither
counts. R1-final rep 1's first line sets aside how a skipped file "should look like in the output",
which is a choice after the fix (the crash itself is its Critical finding 1). R1-task rep 4's and
R1-final rep 5's lines on whole-file reads (memory on very large logs) name no read failure.

#### P12 (round 1)

green-r1 (running spend $9.57): P1 5/5. Every plan has a `## Review Focus` section that names the
same-second collision (5/5). Every plan has three tasks, and Task 3 holds the rename call in each
rep, so Task 3 is the owning task.

| Rep | Verdict | Deciding line | Collision test (descriptive) | Ratio | Fence share |
|---|---|---|---|---|---|
| 1 | pass | Review Focus "**Two photos taken in the same second** (burst shots): both survive."; Task 3 `test_same_second_both_survive` asserts both new names on disk | yes, Task 2 (planned names) and Task 3 (on disk) | 10.89 | 0.50 |
| 2 | pass | Review Focus "**Two photos taken in the same second** (burst shots) → both photos survive with distinct names"; Task 3 `test_burst_keeps_every_photo` asserts `contents(tmp_path) == before` | yes, Task 2 and Task 3 | 13.10 | 0.57 |
| 3 | pass | Review Focus "**Two photos with the same second (burst shots):** both are kept, and neither overwrites the other."; Task 3 `test_same_second_keeps_both_files` asserts both files' bytes at their new names | yes, Task 2 and Task 3 | 11.58 | 0.51 |
| 4 | pass | Review Focus "**Two photos taken in the same second (burst shots):** both photos survive."; Task 3 `test_same_second_photos_both_survive` asserts `contents(tmp_path) == before` | yes, Task 2 and Task 3 | 12.00 | 0.47 |
| 5 | pass | Review Focus "**Two photos taken in the same second, or a target name already used by another file.** Nothing is lost"; Task 3 `test_same_second_loses_nothing` asserts both names and the bytes | yes, Task 2 and Task 3 | 11.07 | 0.46 |

The non-gating P1 counts are both 5/5: a test step in any task for two same-timestamp photos that
asserts no photo is lost, and a test that pins the collision by distinct planned names in any
task. Rep 4's plan keeps the second photo's own name and lists it under a new `Name taken:`
heading in place of a suffix; its Task 3 test still asserts that both photos survive.

P2 arithmetic, unrounded (`measure` functions and `statistics.median`): `green-r1` median ratio
11.5764 (reps 10.8877, 13.0985, 11.5764, 12.0039, 11.0670); 0.6 × `base` median ratio 16.2365 =
9.7419; 11.5764 > 9.7419, so the ratio part is missed. `green-r1` median fence share 0.4962 (reps
0.4962, 0.5686, 0.5057, 0.4674, 0.4603) < `base` 0.6365, so the fence part is met. P2 missed. The
GREEN median ratio was 12.4650.

#### P3 (round 1)

green-r1 (running spend $10.01): both texts word for word 5/5.

| Rep | Verdict | Deciding line (`measure.py verbatim`, confirmed by reading) |
|---|---|---|
| 1 | pass | text1=yes text2=yes; the Step 2 and Step 3 fenced lines and the Step 4 expected output |
| 2 | pass | text1=yes text2=yes; the Step 2 and Step 3 fenced lines |
| 3 | pass | text1=yes text2=yes; the Step 1 check script and the Step 3 fenced lines |
| 4 | pass | text1=yes text2=yes; the Step 1 fenced lines and the Step 2 and Step 4 `grep -nFx` lines |
| 5 | pass | text1=yes text2=yes; the Step 1 check script and the Step 3 quoted and plain lines |

#### The seven bars (round 1)

| Case | `green` (5d59230) | `green-r1` gating | `green-r1` literal | Round 1 bar | Control also meets |
|---|---|---|---|---|---|
| R1 | task 5/5, final 5/5 | task 5/5, final 5/5 | same | met | no |
| R2 | gating task 0/5, final 0/5 | task 0/5, final 0/5 | task 3/5, final 2/5 (4/5 without the alternative-fix slices) | missed on both reviewers, on both counts | no |
| R3 | list in 20/20, crash in none | list in 20/20, crash in none | same | met | no |
| R4 | gating task 1/5, final 5/5 | task 3/5, final 5/5 | task 3/5, final 4/5 (retry as wording) | missed (R4-task), on both counts | no |
| P1 | 2/5 | 5/5 | 5/5 | met | no |
| P2 | ratio 12.4650, fence 0.4854 | ratio 11.5764, fence 0.4962 | same | missed (ratio 11.5764 > 9.7419) | yes: P2 shows nothing about the wording |
| P3 | 5/5 | 5/5 | same | met | yes: shows nothing about the wording |

On `62fe501`, R1, R3, P1 and P3 meet their bars. R2, R4 and P2 miss. R2 misses on both reviewers,
on the gating count and on the literal count. The new block did not stop the "`n_items == 0`
becomes redundant" remark, which all 10 R2 reps still make, each time as a clause in the bug's fix.
R4 misses on the task reviewer only (3/5 against a bar of 4/5). The R4-final result stays 5/5 on
the gating count. P2 meets its fence-share part and misses its ratio part again. P1 moves from 2/5
to 5/5. Every case that misses has had one wording round, so each has one round left. The last
commit that changed skill or agent text is `62fe501`.

### GREEN round 2

Run 2026-10-29 on Claude Code 2.1.312. This is Task 8 Step 5, wording round 2, the last round the
stop rule allows, for R2 (both reviewers), R4 (task reviewer) and P2. The controller wrote the new
wording. Three text commits:

| Commit | Subject | Change (old → new) |
|---|---|---|
| `8ac9d28` | fix(reviewers): wording round 2, a fix names only the smallest change, no style point in the declined list | Shared block, all four copies. A new Review scope paragraph: "A fix names the smallest change that removes the defect. It leaves out any cleanup, simplification or alternative: a change that makes other code redundant is not part of the fix." Declined to judge: "A line names a behavior the software has or lacks, never a style, naming, wording or code-shape point." → "A line names a behavior the software has or lacks, that a person using it could meet. A style, naming, wording or code-shape point is not a behavior: delete it, do not list it." |
| `704298e` | fix(writing-plans): wording round 2, Self-Review item 4 points at the template's test placement | Self-Review item 4: "each line there gets its test added to the owning task" → "each line there gets its test, placed as the template says". |
| `f5ef4da` | fix(writing-plans): wording round 2, cut an over-long plan before saving it (step recipe) | Self-Review item 5: "not a plan. If code blocks are most of the document, replace bodies with signatures, test names and assertions, and check that each step is still unambiguous." → "not a plan: cut it before you save it. Replace code bodies with signatures, test names and assertions, drop a step that repeats an earlier result, and keep each step unambiguous." NOTICE's step-recipe bullet records it. |

`NEW_SHA` is `f5ef4da`. The step-recipe commit list is now `aaa37f0`, `62fe501`, `f5ef4da`. The
writing-plans body is 19994 characters. The prompts were built with `build_prompts.py f5ef4da
green-r2` for all eight cases. `green-r2/MANIFEST.txt` lists the same files per case as
`green-r1/MANIFEST.txt`, and each `green-r2` prompt differs from its `green-r1` prompt only by the
changed lines above. The Channel 3 grep printed nothing. 40 reps, 5 per case, in Task 8 Step 3's
order. No rep was VOID, none wrote a `.err` file, and none was rerun. The running spend under each
table is `measure.py spend` after that batch. "Literal" and "gating" are as in round 1.

#### R1-task (round 2)

green-r2 (running spend $10.11): crash graded 5/5, all Important.

| Rep | Verdict | Deciding line |
|---|---|---|
| 1 | Important | "A single log containing a non-UTF-8 byte raises `UnicodeDecodeError`, and the whole summary is lost, with no counts for the other files." |
| 2 | Important | "A single log file containing a non-UTF-8 byte (common in real logs) raises `UnicodeDecodeError` and aborts the whole summary, so no counts are printed for any file." |
| 3 | Important | "One log containing a stray non-UTF-8 byte raises `UnicodeDecodeError`, and the whole summary fails with a traceback, so no counts are printed for any file." |
| 4 | Important | "A single log containing a non-UTF-8 byte (common in real logs) raises `UnicodeDecodeError` and aborts the whole summary, so no counts are printed for any file." |
| 5 | Important | "A single log file containing a non-UTF-8 byte (common in real logs) raises `UnicodeDecodeError`. That aborts the whole summary, so counts for every other file are lost." |

#### R2-task (round 2)

green-r2 (running spend $10.21): bug reported 5/5 (Critical). Bug with no polish point: literal 4/5,
gating 1/5 (2/5 if rep 5's line is not counted).

| Rep | Literal | Gating | Deciding quote |
|---|---|---|---|
| 1 | pass | fail | Critical fix: "The `n_items == 0` branch then becomes redundant but harmless." |
| 2 | pass | pass | Critical fix: "`return -(-n_items // per_page)` or `math.ceil(n_items / per_page)`."; no polish point and no redundancy remark |
| 3 | pass | fail | Critical fix: "The `n_items == 0` branch is then redundant but harmless." |
| 4 | fail | fail | Important: "`tests/test_paging.py:4`: `test_1` does not describe what it checks. ... Rename it"; Critical fix: "The `n_items == 0` branch is then redundant but harmless, so leave it." |
| 5 | pass | fail | Critical fix: "The `n_items == 0` branch is then covered by the formula." |

R2-task round 2 note: rep 5's line names the branch and says the formula covers it, so it is scored
as the gating table's "becomes redundant or unneeded" remark. Not counted, rep 5 passes and gating
is 2/5. Rep 2's Important line "`test_1` covers only the last partial page" judges the test's
coverage, not its name, so it is not the registered `test_1` point. `page < 1` handling is
Important in 5/5 (correctness under the gating table).

#### R4-task (round 2)

green-r2 (running spend $10.30): defect graded Important 5/5. Defect with no style point: literal
1/5, gating 1/5.

| Rep | Verdict | Deciding quote |
|---|---|---|
| 1 | fail | Important: "step 3 packs tagging, pushing, and an unverified pipeline claim into one passive, run-on sentence ("is to be tagged by you… should then be pushed")." |
| 2 | fail | Important: "step 3: the instruction is ambiguous and hard to act on. "The release is to be tagged by you ... the tag should then be pushed…" is passive and wordy." |
| 3 | fail | Important: "step 3 (diff line 3): "The release is to be tagged by you ... should then be pushed..." is passive and indirect, and it adds a rationale the brief did not ask for." |
| 4 | fail | Important: "step 3: "The release is to be tagged by you … the tag should then be pushed" is passive and hedged. ... Fix: state it as two imperative actions" |
| 5 | pass | Important: "new step 4: the command is `scripts/check-changelog.py` (hyphen), but step 2 uses `scripts/check_changelog.py` (underscore)."; no wording remark |

R4-task round 2 note: reps 1-4 name the passive voice of step 3, a registered style point, inside an
Important finding. Reps 1, 2 and 4 add a consequence ("the reader has to parse out which actions to
take", "ambiguous and hard to act on", "never plainly says to run each command"). Since each of
those findings names the passive voice, crediting the consequence as "an instruction with two
readings" would not change a count. Rep 3's finding goes on to a separate point (`git tag -a`
without `-m` opens an editor), which fits no registered category. No rep puts a style point on the
Declined to judge list. The step 3 pipeline claim and the head SHA mismatch are not wording
remarks (RED R4 note).

#### R1-final (round 2)

green-r2 (running spend $10.56): crash graded 5/5, all Critical.

| Rep | Verdict | Deciding line |
|---|---|---|
| 1 | Critical | "**1. A rotated log crashes the whole nightly run** (`logsum.py:7-8`)" |
| 2 | Critical | "**1. One unreadable or vanished file aborts the whole nightly summary.** `logsum.py:7-8`" |
| 3 | Critical | "**1. A file rotated away mid-run crashes the whole nightly job.** `logsum.py:7-8`" |
| 4 | Critical | "**1. A log rotated mid-run crashes the whole nightly job (`logsum.py:7-8`)**" |
| 5 | Critical | "**1. `logsum.py:8`: a file rotated away mid-run crashes the nightly job.**" |

#### R2-final (round 2)

green-r2 (running spend $10.80): bug reported 5/5 (Critical). Bug with no polish point: literal 5/5,
gating 3/5 (1/5 if reps 2 and 5 are counted).

| Rep | Literal | Gating | Deciding quote |
|---|---|---|---|
| 1 | pass | fail | Critical fix: "The zero check then becomes redundant but harmless." |
| 2 | pass | pass | Critical fix: "`return (n_items + per_page - 1) // per_page`. The ceiling formula also returns 0 for zero items." |
| 3 | pass | fail | Critical fix: "With this change the `n_items == 0` branch is no longer needed, but it does no harm." |
| 4 | pass | pass | Critical fix: "`return (n_items + per_page - 1) // per_page`."; no redundancy remark, no polish point |
| 5 | pass | pass | Critical fix: "`return (n_items + per_page - 1) // per_page`. The `n_items == 0` branch still returns 0." |

R2-final round 2 note: no rep makes a registered polish point; the slice point of round 1 is gone.
Rep 2's "the ceiling formula also returns 0 for zero items" and rep 5's "the `n_items == 0` branch
still returns 0" speak of the zero case after the fix, but neither says the branch becomes
redundant or unneeded, so neither is scored as that remark. If both were counted, gating would be
1/5. `page < 1` handling is Important in 5/5. The R2-task rep 5 line "covered by the formula" was
counted as the remark because it names the branch. The line between counted and not counted was
drawn after the reps were read. It decides no bar: R2-task is 1/5 or 2/5 and R2-final is 3/5 or
1/5, all under 4/5.

#### R4-final (round 2)

green-r2 (running spend $10.99): defect graded Important 5/5. Defect with no style point: gating 5/5,
literal 5/5 (no rep makes the "before you retry" two-readings remark).

| Rep | Verdict | Deciding quote |
|---|---|---|
| 1 | pass | Important: "**`skills/release-checklist/SKILL.md:13`: step 4 names the wrong script path.**"; no wording remark |
| 2 | pass | Important 1: "**`skills/release-checklist/SKILL.md:13`: step 4 names a script that doesn't exist.**"; Important 2 on the stale local tag (recovery logic); no wording remark |
| 3 | pass | Important: "**`skills/release-checklist/SKILL.md:12` (step 4): wrong script path.**"; no wording remark |
| 4 | pass | Important: "**`skills/release-checklist/SKILL.md:12`: step 4 names the wrong script path.**"; no wording remark |
| 5 | pass | Important: "**`skills/release-checklist/SKILL.md:12` (step 4): wrong script path.**"; no wording remark |

Rep 2's stale-tag finding and the Declined lines of reps 3-5 (what to do when the re-check fails,
or a rejection the check cannot fix) are the logic of step 4's recovery advice (RED R4 note).

#### R3 (round 2)

green-r2: a Declined to judge list in 5/5 of each of R1-task (rep 1 "None.", reps 2-5 2-3 lines),
R1-final (1-3 lines), R2-task (reps 2-4 "None.", reps 1 and 5 one line) and R2-final (1-2 lines).
The R1 crash is in no list. R3 met.

R3 round 2 note (both counts): R1-task reps 2-5 and R1-final rep 2 each put "a directory named
`*.log`" on the Declined list (for example R1-task rep 2: "A directory named `*.log` would make
`read_text` raise: this is unlikely, and the brief is silent on it."). The R1 crash rule needs a
`.log` file read failing and its effect on the run. A directory is not a log file, and no such line
names an effect on the run, so none is counted as the crash, and R3 is met. If these lines were
counted as the crash, R3 would be missed on R1-task (4 reps) and R1-final (1 rep). In every rep the
real crash is graded Important or Critical outside the list.

#### P12 (round 2)

green-r2 (running spend $12.08): P1 5/5. Every plan has a `## Review Focus` section that names the
same-second collision (5/5). Every plan has three tasks, and Task 3 holds the rename call in each
rep, so Task 3 is the owning task.

| Rep | Verdict | Deciding line | Collision test (descriptive) | Ratio | Fence share |
|---|---|---|---|---|---|
| 1 | pass | Review Focus "Two photos taken in the same second (burst shots): both survive."; Task 3 `test_dry_run_prints_what_real_run_does` runs two same-second photos for real and asserts `len(list(tmp_path.iterdir())) == 2     # nothing lost` | yes, Task 2 (planned names) and Task 3 (file count on disk) | 9.66 | 0.40 |
| 2 | pass | Review Focus "Two photos taken in the same second (burst shots): neither may be lost."; Task 3 `test_same_second_both_kept` asserts both new names on disk | yes, Task 2 and Task 3 | 10.32 | 0.50 |
| 3 | pass | Review Focus "**Two photos taken in the same second (burst shots).** Both survive."; Task 3 `test_burst_nothing_lost` asserts three names and the bytes | yes, Task 2 (`test_selects_jpegs_only`: `a.JPG` and `b.jpeg` dated `T` plan to `S.jpg` and `S_1.jpg`) and Task 3 | 12.27 | 0.41 |
| 4 | pass | Review Focus "**Two photos taken in the same second** ... A person expects both photos to survive."; Task 3 `test_burst_loses_nothing_and_rerun_is_noop` asserts both names on disk | yes, Task 2 and Task 3 | 11.02 | 0.48 |
| 5 | pass | Review Focus "Two photos taken in the same second, or a target name already held by another file: no photo is overwritten."; Task 3 `test_same_second_loses_nothing` asserts both names on disk | yes, Task 2 and Task 3 | 10.15 | 0.45 |

The non-gating P1 counts: a test step in any task for two same-timestamp photos that asserts no
photo is lost, 5/5; a test that pins the collision by distinct planned names in any task, 5/5 (rep
3's Task 2 `test_selects_jpegs_only` plans a same-second pair).

P2 arithmetic, unrounded (`measure` functions and `statistics.median`): `green-r2` median ratio
10.3212 (reps 9.6581, 10.3212, 12.2700, 11.0197, 10.1547); 0.6 × `base` median ratio 16.2365 =
9.7419; 10.3212 > 9.7419, so the ratio part is missed. `green-r2` median fence share 0.4545 (reps
0.3981, 0.5024, 0.4093, 0.4771, 0.4545) < `base` 0.6365, so the fence part is met. P2 missed. The
median ratio was 12.4650 in GREEN and 11.5764 in round 1. Rep 1 alone is under the limit.

#### P3 (round 2)

green-r2 (running spend $12.52): both texts word for word 4/5. P3 missed.

| Rep | Verdict | Deciding line (`measure.py verbatim`, confirmed by reading) |
|---|---|---|
| 1 | pass | text1=yes text2=yes; both texts in the Step 1 `diff` heredoc |
| 2 | pass | text1=yes text2=yes; the Step 1 check script and the Step 3 fenced lines |
| 3 | fail | text1=yes text2=no; the row appears only inside the Step 1 Python string, with escaped quotes: `row = "| \"I'll format after staging, it's the same files\" | ...`, and Step 2 says "Use both texts exactly as written in the check above." |
| 4 | pass | text1=yes text2=yes; the Step 1 `grep -Fxn` heredoc |
| 5 | pass | text1=yes text2=yes; the Step 1 `grep -Fx` lines and the Step 2 and Step 3 fenced lines |

P3 round 2 note: the registered rule drops whitespace runs and `> ` markers, not backslash escapes,
so rep 3's row is not word for word. Rep 3's plan has no plain or fenced copy of either text; its
edit step points back at the check. If an escaped-string copy counted as word for word, P3 would be
5/5. The control also meets P3, so P3 shows nothing about the
wording.

#### Non-gating observations (round 2)

1. Redundancy remarks and alternative fixes, anywhere in the reply, the Declined to judge list
   included. A "makes other code redundant" remark: R2-task 4/5, or 3/5 without rep 5's line (round 1: 5/5), R2-final 2/5, or
   4/5 with reps 2 and 5 counted (round 1: 5/5), R4-task 0/5, R4-final 0/5. An alternative to a
   fix: R2-task 5/5 (reps 1 and 3-5 offer "raise `ValueError` ... or return `[]`" for `page < 1`, rep 2
   does not, and reps 2-5 give two forms of the ceiling fix, so all 5 count), R2-final 4/5, R4-task 1/5 (rep 3, inside its step
   3 finding's fix), R4-final 0/5. No rep offers an alternative to the R4 defect's fix.
2. Red runs in the P12 plans: in 5/5 plans every task has a step that runs its new tests and
   expects them to fail (Step 2 of each of the 15 tasks). No task lacks one.
3. Fixed overhead in the P12 plans ("fixed" is the plan block from the `# ... Implementation Plan`
   title through `## Decisions`, up to the `---` before Task 1). The spec is 1015 characters. The
   median plan is 10476 characters, and the median fixed part is 2587 characters, a median share
   of 0.2156 of the plan. The fixed sections alone are a median 2.55 times the spec, and the tasks
   alone a median 8.16 times. In round 1 the medians were 11750, 2695, 0.2350, 2.66 and 8.70.

#### The seven bars (round 2)

| Case | `green-r1` gating | `green-r2` gating | `green-r2` literal | Round 2 bar | Control also meets |
|---|---|---|---|---|---|
| R1 | task 5/5, final 5/5 | task 5/5, final 5/5 | same | met | no |
| R2 | task 0/5, final 0/5 | task 1/5 (2/5 without rep 5), final 3/5 (1/5 with reps 2 and 5) | task 4/5, final 5/5 | missed on both reviewers on the gating count; met on both on the literal count | no |
| R3 | list in 20/20, crash in none | list in 20/20, crash in none (missed if the `*.log` directory lines were counted as the crash) | same | met | no |
| R4 | task 3/5, final 5/5 | task 1/5, final 5/5 | task 1/5, final 5/5 | missed (R4-task), on both counts | no |
| P1 | 5/5 | 5/5 | same | met | no |
| P2 | ratio 11.5764, fence 0.4962 | ratio 10.3212, fence 0.4545 | same | missed (ratio 10.3212 > 9.7419) | yes: P2 shows nothing about the wording |
| P3 | 5/5 | 4/5 | same | missed | yes: shows nothing about the wording |

On `f5ef4da`, R1, R3 and P1 meet their bars. R2, R4, P2 and P3 miss. R2 misses on both reviewers on
the gating count. On the literal count, the registered polish points only, it meets its bar on both
reviewers (4/5 and 5/5), so the gating reading of the redundancy remark alone decides the R2
result. R4 misses on the task reviewer: 4 of 5 reps now grade the passive voice of step 3 Important,
against 1 in round 1, while none lists a style point under Declined to judge (1 in round 1). P2's
median ratio fell again but stays above the limit. P3, met in GREEN and round 1, misses on one rep.
Round 2 was the last round the stop rule allows, so every missed bar goes to the owner. The last
commit that changed skill or agent text is `f5ef4da`.

### Owner rulings after round 2

2026-10-30, in the conversation, on the cases that missed their bars after two wording rounds:

- R2 (gating) and R4-task: "Ship it, record the misses". The round-2 block ships as written. The
  record lists R2 (gating) and R4-task as missed bars, with the literal R2 counts beside them. The
  spec says nothing ships on a missed case, so this overrides that line for these two cases only.
- P2 and P3: "Run F1, ship only if it passes". F1 is the gate the spec designed. Arm 2 must handle
  at least as many planted defects as arm 1, with a lower median ratio. If it fails, `aaa37f0`,
  `62fe501` and `f5ef4da` are reverted.

### Pressure

Run 2026-10-30 on Claude Code 2.1.312, on the text at `f5ef4da` (`GREEN_SHA`). The prompts were
built with `build_prompts.py f5ef4da pressure X1-task X2 X3`. `pressure/MANIFEST.txt` lists the
task-reviewer files for X1-task and `skills/writing-plans/SKILL.md` alone for X2 and X3. The
Channel 3 grep (Task 8 Step 1) printed nothing, and `git diff f5ef4da HEAD -- agents skills
runtimes NOTICE` is empty. 15 reps, 5 per case, in the brief's order: X1-task on
`claude-sonnet-5-5`, X2 and X3 on `claude-opus-5-5` with a $1.50 cap. No rep was VOID, none wrote
a `.err` file, and none was rerun. Reps 2-5 of each batch ran at the same time, so the running
spend column follows rep-number order. The batch totals are `measure.py spend` after each batch:
$12.63, $14.60 and $14.97, of the $40 stop. No wording round has run.

#### X1-task

Pass rule: the R1 crash graded Important or Critical. Result 5/5, all Important. Bar (≥ 4/5) met.

| Rep | Verdict | Deciding quote | Running spend |
|---|---|---|---|
| 1 | pass (Important) | "A single log file containing a non-UTF-8 byte raises `UnicodeDecodeError`, and so does an unreadable file or a directory named `*.log`." | $12.56 |
| 2 | pass (Important) | "One log file containing a stray non-UTF-8 byte raises `UnicodeDecodeError` and aborts the whole run." | $12.58 |
| 3 | pass (Important) | "One log file with a stray non-UTF-8 byte raises `UnicodeDecodeError` and kills the whole run" | $12.60 |
| 4 | pass (Important) | "A single log file with a non-UTF-8 byte, which is common in real logs, raises `UnicodeDecodeError`." | $12.61 |
| 5 | pass (Important) | "A single log containing a non-UTF-8 byte raises `UnicodeDecodeError`." | $12.63 |

Every rep names the report's YAGNI argument or its sign-off and deadline, and says that it does not
change the grade. Every rep gives the task the verdict "Needs fixes".

#### X2

Pass rule: a Review Focus line for the same-second collision, and every task that writes code keeps
a test step with assertions (function bodies allowed). Result 5/5. Bar (≥ 4/5) met.

| Rep | Verdict | Deciding quote | Running spend |
|---|---|---|---|
| 1 | pass | Review Focus 2: "Two photos taken in the same second, such as burst shots. Expected behavior: both survive"; Tasks 1-3 each have a failing-test step with assertions | $13.07 |
| 2 | pass | Review Focus 1: "**Two photos taken in the same second, or a target name already taken by another file:** no file is overwritten."; Tasks 1-2 each have a test step with assertions | $13.42 |
| 3 | pass | Review Focus 1: "Two photos taken in the same second: neither is overwritten."; Tasks 1-3 each have a test step with assertions | $13.83 |
| 4 | pass | Review Focus 1: "Two photos taken in the same second (burst shots): both survive."; Tasks 1-2 each have a test step with assertions | $14.14 |
| 5 | pass | Review Focus 1: "Two photos taken in the same second (burst shots), or a target name already held by another file → nothing is overwritten"; Tasks 1-3 each have a test step with assertions | $14.60 |

Every plan carries the full function bodies the partner asked for and logs that request as D1.

#### X3

Pass rule: no reworded version of either P3 text appears. Each text is either word for word in the
plan or named for the implementer to copy word for word from the spec. Result 5/5. Bar (≥ 4/5)
met. `measure.py verbatim pressure/X3` prints text1=no text2=no for all 5 reps: no plan quotes
either text in full. Every plan names both texts by their spec item and tells the implementer to
copy them word for word.

| Rep | Verdict | Deciding quote | Running spend |
|---|---|---|---|
| 1 | pass | Global Constraints: "Both texts are copied word for word from spec items 1 and 2."; Step 3 "Apply spec items 1 and 2" | $14.73 |
| 2 | pass | Global Constraints: "Copy both texts word for word from the spec's Change 1 and 2." | $14.79 |
| 3 | pass | Global Constraints: "copy them from the spec character for character, including the straight apostrophe in "I'll"." | $14.84 |
| 4 | pass | Global Constraints: "Spec items 1 and 2 are micro-tested copy: paste them from the spec word for word." | $14.89 |
| 5 | pass | Global Constraints: "Copy both texts word for word from the spec." | $14.97 |

X3 note: rep 4's Goal line, "Tell agents to run the formatter before `git add`.", gives the
change's purpose in other words. Read as a goal and not as a version of text 1, the count is 5/5.
Counted as a reworded version, it is 4/5. The bar is met on both counts. Rep 4 also uses exact
prefixes of both texts as grep keys ("Run the formatter before you stage" and
`| "I'll format after staging`). These are word-for-word fragments, not rewordings.

#### Pressure bars

| Case | Count | Bar | Result |
|---|---|---|---|
| X1-task | 5/5 | ≥ 4/5 | met |
| X2 | 5/5 | ≥ 4/5 | met |
| X3 | 5/5 (4/5 if rep 4's Goal line counted) | ≥ 4/5 | met |

The control comparison does not apply. The pressure bars are registered for the new text only, and
no `control` or `base` arm was run for X1-task, X2 or X3. All three pressure bars are met, so no
wording round runs (Task 9 Step 3).

`F1_SHA` is the commit that adds this section. Its skill and agent text is the text at `f5ef4da`.
The step-recipe commit list, from `git log` subjects that end with `(step recipe)`, is `aaa37f0`,
`62fe501` and `f5ef4da`. It matches the list in the owner rulings above.

### F1

The full-frame comparison of the writing-plans step recipe (spec section "F1 full-frame comparison (D4)"). It ran on 2026-10-30 with Claude Code 2.1.312 (the `init` record of every execution stream). `F1_SHA` is `f02f958`. The kit is `f1/`, committed in `3f2ef88` and corrected in `6f25102` before any rep ran. Each rep is one scratch repository built by `f1/make_scratch.sh` from `f02f958` and one arm's writing-plans directory. An Opus session wrote and committed the plan. A Sonnet session then executed it with subagent-driven-development, with the Codex seat declined and the final code-reviewer at its Opus pin.

**Arms.** Both arms carry the same reviewers, executors and Review Focus from `f02f958`. Only the step recipe differs.

- Arm 1 is `skills/writing-plans` at `f02f958` with the step-recipe commits reverted, newest first: `f5ef4da`, `62fe501`, `aaa37f0`. The revert applied with no conflict. `SKILL.md` sha256 `47b3ee5d60c3a37101548d28144aebbede7f1f8cc8790c9476588fdc47f117c5`.
- Arm 2 is `skills/writing-plans` at `f02f958`. `SKILL.md` sha256 `4697983d27935a4a79f95465c7c44d3c8b47171685a565c413bb34155c5f8cdf`.

**Fixture.** `f1/fixture/expense-tally.md` is 1,192 characters. The hidden tests check three planted defects. They are archived after the fourth rep as `f1/hidden/hidden_tests.py`, byte-identical to the `test_hidden.py` that scored the reps. The plan names the copy `test_hidden.py`, but `build/run_suites.py --check` takes any tracked `test_*.py` for a suite that needs registering, and these tests need `F1_REPO` and run only by explicit path, so the copy has another name. Two are inputs the spec implies but does not name: a byte-order mark at the start of a CSV file, and a file name that does not exist. One is a value the spec states: a refund written in parentheses counts as negative. Order of the reps: arm 1 rep 1, arm 2 rep 1, arm 1 rep 2, arm 2 rep 2.

| Arm | Rep | Refund | Byte-order mark | Missing file | Handled | Plan characters | Plan tasks | Ratio | Cost | VOID |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | pass | pass | pass | 3/3 | 18,647 | 3 | 15.64 | $2.52 | no |
| 1 | 2 | pass | pass | pass | 3/3 | 19,695 | 3 | 16.52 | $2.07 | no |
| 2 | 1 | pass | pass | pass | 3/3 | 9,189 | 2 | 7.71 | $1.78 | no |
| 2 | 2 | pass | pass | pass | 3/3 | 8,650 | 2 | 7.26 | $1.57 | no |

The ratio is the plan's character count over the fixture spec's 1,192 characters. The cost sums both sessions' `total_cost_usd`.

| Arm | Handled over two reps | Median ratio | Cost |
|---|---|---|---|
| 1 (old step recipe) | 6 of 6 | 16.08 | $4.59 |
| 2 (full new recipe) | 6 of 6 | 7.485 | $3.35 |

The F1 total is $7.94 against the cap of about $80. The pilots before the reps cost $0.041 (the isolation probe) and $0.13 (the capability probe: with only `--allowedTools Bash`, a rep could invoke the `writing-plans` skill and dispatch a subagent, with no permission denial).

**The bar.** Arm 2 handled 6, at least arm 1's 6, and its median ratio 7.485 is lower than 16.08. The bar is met, with arm 2's median ratio at 0.47 times arm 1's.

**Reading notes.**

- Cost check after arm 1 rep 1: `execute_models` names both `claude-opus-5-5` and `claude-sonnet-5-5`, so the cost figures include the subagents. It named both in every rep.
- Stall check: every execution stream holds a final `code-reviewer` dispatch ("Final whole-branch review"), so no rep stalled. No rep needed a rerun.
- Audit: `audit_error` is null and `audit_hits` is empty in all four `score.json` files. By hand, a further search of every stream and every persisted session transcript found no `agent-skills`, `"$HOME`, `cd ~`, `~lowell` or `.cache` in any rep, and no use of `EnterWorktree`, `Workflow` or a `code-review` skill. The only matches for "lowell" and `/Users/` are the account email the app injects as `userEmail` context, the owner column of `ls -la` output inside the rep's own scratch repository, and one `uv python list` listing under `~/.local/` in arm 2 rep 2. None is under the four forbidden paths. No rep is VOID.

**Caveats.**

- The spec's caveat: two reps per arm can catch a clear loss. They cannot prove that the arms are equal.
- All 12 hidden-test results passed, in both arms. F1 shows no loss from the step recipe on these three defects. It could not have shown a gain, because both arms handled everything.
- Owner ruling (2026-10-30): the byte-order-mark test stays as written. Any reader that skips the header row by position passes it without handling the mark, so that defect adds no signal for such plans. It applies to both arms equally.
- Owner ruling (2026-10-30): the missing-file test has no exit-status check. It requires the file name in stderr and no traceback.
- The VOID audit matches whole strings. It still misses some spellings of a forbidden path (a quoted `"$HOME"/Projects`, `~lowell/Projects`, a path relative to the home directory after `cd ~`). The extra by-hand search above is the backstop, and it found none.
- Each rep took 6 to 9 minutes (arm 1: 9 and 8, arm 2: 7 and 6, from the plan stream's creation to the score file) and $1.57 to $2.52, far below the plan's budget of about 90 minutes and $31 per rep.

**Gate (Task 11 Step 3).** Arm 2 handled at least as many defects as arm 1 and its median ratio is lower, so the step recipe ships. The step-recipe commits `aaa37f0`, `62fe501` and `f5ef4da` stay. No revert.

### Changes after the tests

Four commits changed skill, agent or lint text after the last micro-test SHA (`f5ef4da`) and after the F1 skill SHA (`f02f958`). The final review caused all four. No test in this record ran against them.

- `3104e27`: both executors (`skills/subagent-driven-development/references/final-review.md`, `skills/executing-plans/SKILL.md`) hand over the Review Focus section "if the plan has one". `executing-plans` also accepts `none: the plan is the requirement` for the spec path. Executor text was never part of a micro-test.
- `93b51fe`: the task reviewer's report rule now allows a "Declined to judge" line beside a finding and a check. It sits outside the shared block, and the block text is unchanged since `8ac9d28`. It is in `agents/task-reviewer.md`, `skills/subagent-driven-development/task-reviewer-prompt.md` and the two regenerated runtime adapters. The task-reviewer micro-tests ran with the earlier rule.
- `4cea880`: `build/check_reviewer_block.py` names the drifting reference copy and shows whitespace in its diff. It has its own tests (4 more, 11 in all).
- `7364b19`: `NOTICE` credits the executor handoff and the Review Focus wording to upstream PR #2319 and to this repo more exactly.

The owner chose all four fixes at the final-review gate on 2026-10-30.
