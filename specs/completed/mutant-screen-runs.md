# Mutant screen runs: stop re-running caught mutants — Design Spec

**Status: COMPLETE (2026-11-22)** — implemented by plan 104 (`specs/plans/completed/104-mutant-screen-runs.md`) and
retired here. APPROVED on 2026-11-19: the owner's question was "Do you approve the committed spec?", and the owner
answered "Approve it".

This design came from a brainstorming session on 2026-11-19. Its input was a local findings write-up on the cost and
benefit of the mutant step. That write-up is not committed, because it names private repositories. This spec copies
only the totals that the design needs. The owner chose approach B (Approaches). A builder check read the draft. Its
six questions were settled from the repositories or as designer's calls, so none went to the owner. Text marked
*(designer's call)* is the designer's choice, and "Designer's calls" lists each one. Line numbers are as of `008d062`,
the `main` commit this design read. On 2026-11-19, `origin/main` had not changed any file this design edits since
`008d062`, and the one open PR (#235) touched none of them.

> **For agentic workers:** plan this with writing-plans. This change edits the execution machinery (`mutant-run`, the
> subagent-driven-development references and the implementer prompt, and executing-plans' SKILL.md). So it executes
> with no other plan execution in flight, unless the owner rules otherwise. The micro-test in Verification is part
> of the plan, because the implementer and controller text shapes behavior (writing-skills).

## Terms

- **Mutant, caught, survived, invalid, mutant task, BASE, revert:** as `skills/subagent-driven-development/references/mutants.md`
  Terms defines them (lines 7-24).
- **Full run:** a `mutant-run` call without `--screen`. It runs the test command once for each mutant. Its run file is
  `task-<N>-mutants.log` or `task-<N>-mutants-<K>.log`. A full run is the only proof of the mutant step.
- **Screen:** a `mutant-run --screen` call. It runs the test command only for mutants that no earlier run of the task
  caught. Its file is `task-<N>-screen.log` or `task-<N>-screen-<K>.log`. A screen is never proof.
- **Carried mutant:** a mutant that a screen does not run, because an earlier run of the same task caught a patch with
  the same bytes (the same sha256).
- **Controller:** the subagent-driven-development (SDD) session that dispatches implementers and reviewers.
- **Inline agent:** the executing-plans session, which implements and checks each task itself.

## Intent

The mutant step works, and the owner wants to keep it. But much of its test time buys no new evidence. A full run
re-runs every mutant, including mutants that an earlier run of the same task already caught. In the logged runs, a
caught mutant never came back as a survivor.

The owner runs plan executions in many repositories at once, on one machine. So the mutant step's cost is mostly CPU
that other sessions also need. The owner is not waiting on the time now. The aim is to remove the repeat work, keep
the proof exactly as strong as it is, and get a real read on what the step catches.

## Evidence

From the local write-up and this session's analysis of the same run files. All figures are totals over 198 run files,
52 tasks and 11 plans, written over about four days up to 2026-11-19. Every one of the 52 tasks ran under SDD.

- **Cost.** About 38.8 hours of pytest time. The median task spent about 21 minutes of pytest time in `mutant-run`.
  These hours overlap across sessions.
- **Re-runs.** 68% of mutant time re-ran a patch that an earlier run of the same task had already caught. In 10,139
  such re-runs, no caught mutant became a survivor. The only changed verdicts were 10 "does not apply" results, after
  the code changed under the patch.
- **Who re-runs.** Under SDD, the implementer runs `mutant-run`. Then the controller runs it again before the review
  (`skills/subagent-driven-development/references/test-run.md:17-34`). Each fix round repeats the pair
  (`references/fix-loop.md:23-25`). In 59 of the 198 runs, about 13 hours, HEAD and every patch's bytes were the same
  as in the run just before. The implementers' reports cite the first run of each such pair, and the controllers'
  ledgers cite the second.
- **Benefit.** Survivors exposed 2 real code defects in 52 tasks, both in agent-skills plan 102, task 7. Other effects
  were stronger tests, some dead-code removal, and one vacuous plan test that the revert exposed. Reviewers found
  most other real bugs.
- **Mutant count.** The median task wrote 46 mutants. In each task's last run, a median of 10 mutants was enough for
  every caught test to catch one. But the 2 real defects came from mutants 86 and 100 of a 189-patch set.

## Goals

1. Stop the implementer's re-runs of mutants that the task's earlier runs already caught.
2. Keep the proof unchanged. The controller's full run under SDD, and the inline agent's last full run under
   executing-plans, stay the evidence that `task-done` and every reviewer read.
3. Record, in a form that outlives the plan workspace, which commits the mutant step caused. This gives the owner a
   real read on the benefit later.

## Non-goals

- **A cap on the number of mutants.** The only confirmed catches came from a large mutant set. A cap waits for the
  re-measure (Design 6).
- **Parallel mutant workers, and xdist inside mutant runs.** The owner's sessions already share every core. Parallel
  runs would move CPU from one session to another and add no total throughput.
- **Cutting the controller's runs.** They are the proof, and approach B keeps them as they are.
- **Changing what reviewers check.** Bookkeeping findings are a large share of task-review findings. Whether the
  reviewer should check less is a separate design question.

## Anti-goals

- Any change that lets a run that is not full count as proof, in `task-done`, in a review dispatch or in a final
  review.
- Any change that weakens what the mutant step catches, even if it saves time.
- New bookkeeping that a reviewer checks. The benefit record must not start review findings or fix rounds.

## Approaches

The savings below come from a simulation on the 198 run files. They are shares of the 38.8 hours. Runs were split
between implementer and controller by the plans' ledgers and by the exact repeats, so each figure is approximate.

| Approach | What changes | Saving | What it gives up |
|---|---|---|---|
| **A. The controller checks instead of re-running** | When the implementer's newest run is clean, at HEAD and BASE, and every patch is unchanged, the controller checks that file and skips its own run. | about 33% | The controller's independent run. The proof becomes a file the implementer produced. Nothing changes under executing-plans. |
| **B. The implementer screens, the controller proves** *(picked)* | A screen mode runs only mutants that no earlier run caught, plus the baseline and the revert. The controller's full run each round stays as it is. | about 30% (30–43% by how controller runs are counted) | Nothing in the proof. The implementer's first screen has nothing to carry, so the first-round repeat stays. |
| **C. Screens everywhere, one full run at the end** | B, and the controller's fix-round runs screen too. One full run happens after the last review passes. | about 45% | Fix-round reviewers read partial runs. A survivor in the end run reopens a reviewed task. More contract text changes. |

**The owner picked B** (2026-11-19, "Go with B"). It is the only approach that leaves the proof exactly as it is.

**A dropped variant.** A screen could also stop each mutant at its first failing test (pytest `-x`). A log-based
estimate puts B at about 48% with it. That estimate is optimistic, because it treats every test as the same length.
The cost: a screen would show only the first test that catches each mutant. The implementer could no longer see
whether each new test catches a mutant. Those gaps would reach review as findings and fix rounds. The re-measure
(Design 6) can revisit it.

## Design

### 1. `mutant-run --screen`

`mutant-run` takes an optional first argument, `--screen` *(designer's call: a leading flag, so the existing
positional form stays valid)*:

```text
mutant-run [--screen] PLAN_FILE TASK_NUMBER BASE -- TEST_COMMAND [ARGS...]
```

Without `--screen`, nothing changes: the full run behaves and writes as it does today.

With `--screen`, the run follows the same steps as a full run (`mutant-run` header, steps 1-7), with these changes:

1. **Find earlier catches.** Before the patch loop, read every earlier run file of this task in the workspace: the
   full runs (`task-<N>-mutants.log`, `task-<N>-mutants-<K>.log`) and the screens (`task-<N>-screen*.log`). Read only
   files whose `command:` line equals this screen's rendered command *(designer's call: a catch under a wider command
   may not hold under a narrower one)*. Take each `mutant K: CAUGHT` line that ran in that file, so not a carried
   line. Key it by the line's `sha256`. When several lines have the same sha256, keep the one from the newest file
   *(designer's call: the newest catch has the most recent `tests:` list)*.
2. **Carry or run each patch.** For each patch, in K order, compute its sha256 as today. Then make every check that
   comes before the test command, as today. The "already in HEAD" check of step 4 still refuses the whole run with
   exit 2. A patch that fails the test-file check or `git apply --check` is INVALID. *(Corrected (owner, 2026-11-19):
   the approved text had put the "already in HEAD" check among the checks that give INVALID.)* A patch that passes
   the checks and whose sha256 has an earlier
   catch is carried: it is not applied, and the test command does not run for it. Every other patch runs as in a
   full run. *(Designer's call: a carried patch keeps the cheap checks, so a code change that breaks a patch shows up
   in the screen, not first in the controller's run.)*
3. **The baseline and the revert run as in a full run.** The baseline guards against a failing suite. The revert lets
   the implementer answer step 7 of `mutants.md`. In the logged runs the revert cost about 0.3 hours in total.
4. **The time limit,** the `mutant-active` marker, the recovery, the signal handling and the tree checks are the same
   as in a full run.

### 2. The screen file

The screen writes `task-<N>-screen.log` for the task's first screen, and `task-<N>-screen-<K>.log` for screen K = 2,
3 and so on. Screens and full runs number on their own. A screen never takes a `task-<N>-mutants*.log` name, so
`task-done` (`skills/executing-plans/scripts/task-done:189-203`) and the final review
(`skills/executing-plans/references/final-review.md:29-32`) never read one.

The file has the full run's format (`mutant-run` header, lines 111-140), with these changes:

- The first line reads `mutant-run: Task <N>, screen <K>`.
- A new header line follows the `result:` line: `screen: carried <m> of <total> from earlier runs`.
- The `result:` line counts each carried mutant as caught *(designer's call)*. So when no verdict changes, a screen's
  counts equal a full run's counts. No reviewer text needs to change, because the reviewer already expects the
  implementer's report to cite "an earlier run of its own under another file name", and judges the mutant step by the
  controller's run (`agents/task-reviewer.md:145-146`). Equal counts are a side benefit: a reader who compares the
  report with the controller's run sees the same numbers.
- A carried mutant's line reads
  `mutant <K>: CAUGHT exit - sha256 <hex> carried: <file name of the earlier run> tests: <that run's tests>`.
- The `--- tests ---` section joins this run's catches and the carried catches. A carried catch's tests come from the
  earlier run, at an earlier HEAD (Known limits).
- The `--- output: mutant <K> ---` sections exist only for mutants whose command ran, as today.

The exit status has the full run's meaning: 0 when no mutant survived or is invalid, carried ones included. A screen
with exit 0 is still not proof.

### 3. Who screens

- **The SDD implementer** uses `--screen` on every `mutant-run` call: the first run, each re-run while it answers
  survivors and invalid mutants, and each fix-round run. Its report names the newest screen's path and gives that
  file's `result:` counts, in the same form as today
  (`skills/subagent-driven-development/implementer-prompt.md:166`, `:175-176`). *(Designer's call: no new words in
  the report. The file's name and its `screen:` line show that it is a screen. The reviewer already expects "an
  earlier run of its own under another file name" in the report and judges the step by the controller's run
  (`agents/task-reviewer.md:145-146`).)*
- **The SDD controller** never passes `--screen`. Its full run before each review stays as `test-run.md:17-34`
  describes. An implementer's screen file is not evidence. The controller never hands one to a reviewer.
- **The executing-plans inline agent** makes its first run a full run. It uses `--screen` only for re-runs while it
  answers survivors and invalid mutants. Once a screen shows no survivor and no invalid mutant, it makes one more full
  run after its last commit. A clean full run at HEAD ends the step. *(Designer's call: a task whose first full run
  is clean pays one run, as today. A rule "screen first, full run last" would make that task pay two.)*
  `task-done` already refuses when the newest full run is not at HEAD.

- **A test added after the task's first run gets a new mutant patch.** This covers a test added in step 6, in step 7
  or in a fix round. One mutant may still serve several targets (step 3), but an already-caught mutant is not re-aimed
  at the new test. A screen carries that mutant with its old `tests:` list, so the new test's catch would not show
  until the controller's full run. A new patch always runs. *(Designer's call.)*

`references/mutants.md` steps 5 to 8 and "Reading the run" carry this split, because both executors read that file.
`implementer-prompt.md:44-46` and `:143-156`, `references/test-run.md:17-34` and executing-plans' `SKILL.md:251-260`
carry their own part.

### 4. What does not change

- `task-done`'s code. It reads only `task-<N>-mutants*.log`, so a screen can neither satisfy nor block its gate.
- The four reviewer surfaces (`agents/task-reviewer.md`, `task-reviewer-prompt.md`, `re-review-prompt.md`,
  `references/final-review.md`). They read only the controller's or the inline agent's full run.
- The controller's runs, the fix-round loop and the five-attempt cap.
- The mutants file's format and every line type in it.

If a reviewer still raises findings about screen files, the anti-goal "no new review findings" outranks this list.
Then one sentence goes into the shared reviewer block, and `build/check_reviewer_block.py` keeps the four copies
equal. *(Designer's call: the frozen reviewer text is a means, not a goal.)*

**Backward compatibility.** A session that started before this change never passes `--screen`. It keeps working as
before. A controller that loads the new references mid-plan still makes full runs. An implementer that reads the new
`mutants.md` mid-plan makes screens, and its controller's full run stays the proof. So the change is safe to merge
while other executions run, although the machinery rule above still decides when it executes.

### 5. The benefit record: a `Mutant-step:` trailer

When a commit answers the mutant step, its message ends with a git trailer that names the task and the cause
*(designer's call)*:

```text
Mutant-step: task <N> survivor <K>
Mutant-step: task <N> input shape
Mutant-step: task <N> revert
Mutant-step: task <N> review
```

- `survivor <K>`: the commit answers survivor K (step 6 of `mutants.md`).
- `input shape`: the commit adds a test, and fixes the code if needed, for an input shape that had no test (step 2).
- `revert`: the commit answers a test that passed on the revert (step 7).
- `review`: the commit answers a reviewer's finding against the mutant step, from a task review or a final review
  (`implementer-prompt.md:143-156`, executing-plans' final review).

`<N>` is the task number that the commit answers, as in the task's file names. The task number is in the trailer
because nothing else that git keeps maps a commit to a task: the ledger and the workspace are gitignored. A commit
that answers more than one cause gets one trailer line for each. The trailer goes in the same last paragraph as any
other trailer, such as `Co-Authored-By:`. Git reads trailers only from the last paragraph of a message.

No reviewer checks the trailer, and no reviewer text mentions it. It is a record, not a claim. So it cannot start a
review finding.

Why a trailer: the plan workspaces are gitignored, and several were gone before the write-up could read them. Git
history stays. On 2026-11-19, every repository where the mutant step ran merged its plan branches with merge
commits, so each branch commit and its trailer reach the default branch. The re-measure can classify each tagged
commit as a code change or a test-only change from the files it touches, with no agent judgment:

```bash
git log --format='%h %(trailers:key=Mutant-step,valueonly,separator=%x2C )' | awk 'NF > 1'
```

A plan's merge commit gives the plan that each commit belongs to: the commits in `<merge>^1..<merge>^2`. If a
repository later squashes a plan's PR, the re-measure reads that PR's commits with
`gh pr view <number> --json commits`, which GitHub keeps after a squash.

This replaces the per-survivor report line and ledger copy that the session described before the owner's pick
(Designer's calls, 9).

### 6. The re-measure

The plan's completion adds one item to `specs/deferred_items.md`: re-measure the mutant step after about 5 more code
plans that have a Codex final review. The item:

- tallies the `Mutant-step:` commits for each task, split into code changes and test-only changes;
- compares final-review findings for each task with agent-skills' pre-mutant rate (0.56 code-behavior findings for
  each task, over plans 69-96);
- decides whether to keep the mutant step, shrink it (a mutant cap, `-x` screens), or make the mutant runs opt-in.

Which repositories run the Codex final review stays the owner's choice for each repository.

## Constraints

- **Privacy.** agent-skills is public. The spec, the plan, test fixtures and commit messages cite totals and
  agent-skills' own plans only. They name no other repository, no path in one, and no commit in one.
- **Script style.** `mutant-run` is bash that must run on bash 3.2 (macOS) and on Linux. Keep its existing helpers
  (`file_sha256`, the awk readers) and its perl start-up.
- **Helper paths.** Every new mention of `mutant-run` under `skills/` carries the `<this-skill-dir>/` anchor
  (`build/check_helper_paths.py`).
- **Tests.** `skills/subagent-driven-development/scripts/test_sdd_scripts.py` and
  `skills/executing-plans/scripts/test_executing_plans_scripts.py` hold the script tests. Plans state test counts as
  +N deltas.
- **No new script.** The screen is a mode of `mutant-run`, so the orphan-file lint and `install.py`'s `DEPENDENCIES`
  do not change.

## Verification

**Script tests** (test-driven: each fails first):

1. A screen carries a patch that an earlier full run caught, and does not run the command for it.
2. A screen carries a patch that an earlier screen caught by running it, and never carries from a carried line.
3. A patch whose bytes changed since its catch runs again, and so does a patch caught only under another `command:`.
4. A survivor and an invalid mutant from an earlier run run again.
5. A carried patch that no longer applies reads INVALID with `reason: does not apply`.
6. A screen runs the baseline and the revert, and a failing baseline exits 3 as in a full run.
7. The screen file's name, its first line, its `screen:` line, its `result:` counts with carried mutants as caught,
   and its carried mutant lines.
8. A full run ignores every screen file: it runs every patch, and its run number counts only full runs.
9. `task-done` ignores a screen file. A newer screen beside an older full run at another HEAD still gets the refusal
   "the mutant run is at …", and a clean full run at HEAD still passes when a newer screen holds a survivor.

**Micro-test** (writing-skills). The control arm gets the new `mutant-run`, with `--screen` in its usage line and
header, beside the current instruction text *(designer's call: that is the real temptation, a tool that offers a
screen with no rule on who uses it)*. The treatment arm gets the new script and the new text. Bars:

- The SDD implementer passes `--screen` on every `mutant-run` call, and reports the newest screen's path and its
  `result:` counts.
- A test that the implementer adds after the task's first run gets a new mutant patch.
- The SDD controller never passes `--screen`, and hands the reviewer its own full run.
- The executing-plans inline agent makes its first and last runs full, and screens only in between.
- A commit that answers a survivor, an input shape, the revert or a mutant-step review finding ends with the matching
  `Mutant-step: task <N> …` trailer, in the last paragraph.

As writing-skills says, a bar that the control arm already meets needs no new wording, and the plan drops that
wording. No reviewer arm runs, because no reviewer text changes and the report keeps its form. The plan sets the
fixtures and the rep counts.

## Known limits

- **Carried tests are from an older HEAD.** A carried mutant's `tests:` list does not show tests added after its
  catch. Design 3 gives each such test a new patch, which always runs. If an implementer re-aims a caught mutant
  anyway, the gap shows first in the controller's full run, as a review finding.
- **A reviewer may still question a screen file.** The reviewer text already expects the implementer's own run under
  another file name, but no micro-test arm checks reviewers here. Design 4 says what gives way if one does.
- **A carried mutant can, in principle, survive a later code change.** The logged runs show no case in 10,139
  re-runs. The controller's full run, or the inline agent's last full run, would find it.
- **The first-round repeat stays under SDD.** The implementer's first screen carries nothing, so it costs a full run.
  Approach A would remove it, at the price of the controller's independent run.
- **The saving is unmeasured under executing-plans.** None of the 52 measured tasks used it.
- **The saving assumes one command for each task.** The simulation did not compare `command:` lines. A screen whose
  command differs from the earlier runs' command carries nothing.

## Left to the builder

- The parsing of earlier run files, and how the screen and full-run numbering share code with `next_run_file`
  (`mutant-run:657`).
- The exact wording in `mutants.md`, `implementer-prompt.md`, `test-run.md` and executing-plans' `SKILL.md`, within
  the micro-test's bars.
- The `mutant-run` header text that documents the screen.
- The test fixtures, within the privacy constraint.

## Designer's calls

1. `--screen` is a leading flag, so the current positional form is unchanged.
2. Screen files take their own name and numbering, `task-<N>-screen[-<K>].log`, so no reader of full runs can take
   one for proof.
3. A catch is carried by the patch's sha256, from the newest earlier line that actually ran, in a run whose
   `command:` line equals the screen's.
4. A carried patch still gets the test-file check, `git apply --check` and the "already in HEAD" check.
5. A screen always runs the baseline and the revert.
6. The `result:` line counts carried mutants as caught, with a separate `screen:` line. No reviewer text changes,
   because the reviewer already expects the implementer's own run under another file name
   (`agents/task-reviewer.md:145-146`). The implementer's report keeps its current form: the screen's path and its
   `result:` counts, with no new words.
7. The SDD implementer screens every run. The executing-plans inline agent runs full first and last, and screens only
   in between.
8. No `-x` in screens (Approaches, "A dropped variant").
9. The benefit record is a `Mutant-step:` commit trailer, not a report line plus a ledger copy plus a tally script.
   Before the owner picked B, the session described the latter. The trailer survives the workspace, needs no agent
   tally, and adds nothing for a reviewer to check.
10. The re-measure is a deferred item, not part of this plan.
11. The trailer names the task (`task <N>`), because nothing that git keeps maps a commit to a task. It has a fourth
    cause, `review`, so commits that answer a reviewer's mutant-step finding count too.
12. A test added after the task's first run gets a new mutant patch, not an already-caught mutant re-aimed at it.
13. The micro-test's control arm has the new script with the current text. No reviewer arm runs.
14. If reviewers still question screen files, one sentence goes into the shared reviewer block, because the anti-goal
    outranks the frozen reviewer text.
