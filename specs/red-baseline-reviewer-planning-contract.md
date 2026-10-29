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
