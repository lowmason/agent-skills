# Mutant step: cost, benefit and parallel runs

**Status:** findings only. No skill or script was edited. This document exists to decide what, if anything, becomes a spec.

**Date:** 2026-11-19. **Data:** every real `mutant-run` run file on this machine (198 run files, 52 tasks, 11 plans, 4 repos). Also the review records of those plans, and a benchmark in scratch clones. The micro-test kits of plans 93 and 97 are left out. Some run files are copies (one workspace is a handoff backup), so a file date can be a copy date.

## Question

The mutant step of plan 93 (#198) and its revert check (plan 97, #206) run each mutant one after another. The owner asked three things:

1. Has the mutant step been beneficial?
2. About how much time has it added?
3. Can pytest-xdist run the mutants in parallel batches, and what should change?

## Short answer

1. **Benefit: real but small, and not yet proven against the proxy.** In 52 tasks, mutants exposed 2 real bugs. Both were in one task (agent-skills plan 102, task 7) and both were rare-input defects in new grader code. Their fix is in one commit, `d120723`. The other effects are stronger tests (28 survivor events in the logs) and a few dead-code removals. There is also one probable input-shape fix, and one vacuous plan test that the revert check exposed. Reviewers and implementers found the other real bugs of these plans. Mutant-era final reviews still find "stated rule with no test" gaps. The owner's proxy, Codex final-review findings before and after, cannot answer yet. Codex ran on 5 mutant-era code plans. The only usable before group is in agent-skills, and there only 8 mutant tasks have a finished final review.
2. **Time: about 39 hours of pytest time, or about 47 hours of wall time.** By wall time, the median task spent about 31 minutes in `mutant-run`, the mean task 54 minutes, and the worst task 3 hours 27 minutes. These totals add up sessions that ran at the same time, so they are not hours that a person waited. The agent time to write about 100 mutant patches for each task, and the review rounds about them, come on top.
3. **Parallel:** xdist cannot run two mutants at once, because each mutant needs its own source tree. Parallel mutants need one checkout per worker. In a benchmark, 4 workers gave a 1.9–2.7× wall-time speedup. But parallel workers do not remove work: they used about 22% more pytest time than one serial run. On this machine other sessions already use every core, so parallel workers mostly take CPU from those sessions. Incremental middle runs and fewer mutants remove work instead.

**Recommendation, in order:**

1. Stop re-running caught mutants between rounds. This saves about 45%.
2. Cap the number of mutants, because most are redundant.
3. Use xdist only for slow focused suites.
4. Add parallel workers last, with a cap.

Then measure the benefit properly. After that, decide to keep, shrink or drop the mutant runs. Section 6 gives the details.

## 1. Data and method

- **Run files.** A script parsed each `task-<N>-mutants*.log`: the header, each mutant's verdict and patch SHA-256, the revert line, and the pytest summary line (`… in <t>s`) of each output section. One duplicate copy (naics-embedder plan 19 under `logs/`) was dropped.
- **Wall time.** pytest's own timer leaves out `uv run`, interpreter start and plugin import. It also leaves out `mutant-run`'s own work for each run: applying and reversing the patch, the tree checks and the bytecode purge. In the benchmark, `mutant-run`'s wall time was 1.9 s for each run above pytest's sum, in both reps (34 s over 18 runs). A bare replay of the test command showed 1.2–1.3 s of that. The wall-time estimate adds 1.9 s to each of the 15,397 mutant runs and to each baseline and revert run.
- **Review records.** One read-only agent for each repo read the records: SDD ledgers, task reviews, task reports, `task-*-mutants.md` files, final-review notes and commit bodies. Each one sorted every finding into five classes:
  - (a) unstated input;
  - (b) stated rule with no test;
  - (c) shared reading;
  - (d) prose or docs only;
  - (e) other. Each one also listed every non-test code change that a mutant, an input-shape row or the revert check caused.
- **Benchmark.** Scratch clones of embedding-data, at the `head:` commits of two logged runs, each with its own `.venv`. Other live sessions shared the machine, at load averages of 24–61 on 14 cores. So each variant ran alternately with its comparison, two or three times.

## 2. Time added

### By plan

| Repo | Plan | Tasks | Runs | Mutant runs | pytest hours | Wall hours (est.) |
|---|---|---|---|---|---|---|
| embedding-data | 11 ITA establishment (backup workspace) | 11 | 54 | 4,609 | 12.5 | 15.0 |
| embedding-data | 14 ACS wage microdata | 6 | 29 | 1,757 | 10.3 | 11.2 |
| agent-skills | 102 cc-guide verifier recall | 8 | 37 | 2,704 | 6.9 | 8.4 |
| embedding-data | 13 TRI parent links | 5 | 23 | 2,526 | 3.1 | 4.5 |
| embedding-data | 15 USAspending vendor links | 7 | 22 | 3,032 | 3.1 | 4.7 |
| naics-embedder | 20 text-to-code reference read | 3 | 6 | 216 | 2.2 | 2.4 |
| naics-embedder | 19 economic decision read | 1 | 2 | 13 | 0.5 | 0.5 |
| ces-revisions | 15 revision drivers, stage 9 | 7 | 15 | 361 | 0.2 | 0.4 |
| others (3 plans) | — | 4 | 10 | 179 | <0.1 | 0.2 |
| **Total** | | **52** | **198** | **15,397** | **38.8** | **47.3** |

Per task:

- mutants: median 46, mean 69, maximum 251;
- runs: median 4, maximum 8;
- pytest time: median 21 minutes, mean 45, maximum 190;
- wall time: median 31 minutes, mean 54, maximum 207.

### Where the time goes

- **Re-runs of caught mutants: 68%.** The 15,397 mutant runs cover 5,238 distinct patches. 10,139 runs (25.8 h) re-ran a patch that an earlier run of the same task had already caught. Each fix round, and each new test, starts a full run again.
- **None of those re-runs changed the answer.** 10 of the 10,139 re-runs did not read CAUGHT. All 10 are plan 102, task 3, run 5, "does not apply": the code had changed under the patch. No caught mutant ever came back as a survivor.
- **The final run must stay full.** `task-done` reads only the newest run. Its `head:` must be HEAD, and its result must be `survived 0, invalid 0`. Each `Mutant K:` line in the mutants file needs a matching run line and patch SHA. Only the middle runs can shrink. If middle runs ran only survivors, invalid mutants and new patches, mutant time would fall from 37.8 h to 20.6 h (−45%). The mean task would fall from 44 to 24 minutes and the median from 21 to 15.
- **Mutant count.** In each task's last run, a greedy set cover finds the smallest set of mutants that still gives every caught test one catch. That set is a median of 10 mutants, against a median of 46 written (5.0× over all tasks). The rule asks for one mutant for each stated rule and for each test that the task adds, so the cover is only a guide. But 99.7% of all mutant runs read CAUGHT (15,354 of 15,397), so most extra mutants confirm what one mutant already proved. The workspaces hold 46 helper scripts for mutants, such as `task-*-make-mutants.py`, which make mutants in bulk.
- **Suite length.** 85% of mutant time came from runs of 5 s or more, and 60% from runs of 15 s or more. Sub-second suites (ces-revisions, agent-skills plan 101) cost almost nothing.
- **Contention.** The logged times were taken on a loaded machine. The ACS-wage suite logged 17–21 s for each run. The same commit ran in 7–9 s in this study at a load average near 33. At the start of this study the 15-minute load average was 124 on 14 cores, with other sessions running `mutant-run` and xdist suites. Contention about doubled the logged cost.

## 3. Benefit: direct evidence from the run files

- **Survivors: 28 events in 16 tasks** (0.5% of distinct patches). Each one ended in a stronger or new test, a rewritten mutant, or a `Withdrawn:` line. The review records confirm that the commits that answered these logged survivors changed test files only. The 2 real bugs of section 4 came from survivors of an unlogged screen that one implementer ran before the official run.
- **Revert check: often vacuous.** In 30 of 51 final runs the revert reads `not loaded`, with no test passing. The task created a new module, so at BASE the tests cannot import it, and every test "fails on the revert" by construction. The check is informative only when a task changes existing code. Example: naics-embedder plan 19 had 520 tests fail and 234 pass, and all 28 changed tests failed. The revert is cheap (0.3 h in total), so its cost does not matter.
- **Mutants file lines** (final files on disk, from the agents' counts): `Strengthened:` 2, `Keeps:` 20, `Withdrawn:` 20, `Unproven:` 36, `Unreachable:` 76, against about 3,600 `Mutant` lines. Some files are gone, so these are lower bounds.

## 4. Benefit: evidence from the reviews

| Repo | Mutant-era plans read | Real bugs that the mutant step found | Other effects |
|---|---|---|---|
| embedding-data | 11, 13, 14, 15 | none confirmed. One probable: plan 15 `29fe0fd`, a Ctrl-C left a `.part` file that blocked retries (`except Exception` → `BaseException`). It came from an input-shape row, but the report credits the brief's rule and TDD | 4–5 commits that removed dead or redundant code that a surviving mutant exposed |
| ces-revisions | 12–16 | none. The 4 survivors in plan 15 led to test-only commits | about 35 tests added. One equivalent change (plan 12 `0ba27fa`) |
| naics-embedder | 19, 20, 21 | none. Every step-2 or strengthening commit changed tests only | — |
| agent-skills | 97, 99, 100, 101, 102 | **2, in one commit:** plan 102 `d120723` (task 7, a new grader). The implementer's own `-x` screen of 189 patches, run before the official run, left 12 survivors. Survivor 100 showed that `load_jsonl` split records at U+2028 (`splitlines()`), and survivor 86 showed that a `true` subagent count read as 0. Both are rare inputs. The advisor then found the same `splitlines()` flaw elsewhere (`fa26a5b`) | about 21 survivors: 2 code defects, 9 missing inputs (new tests), the rest equivalent or withdrawn. The revert exposed one vacuous plan test (plan 101, task 6a) |

Apart from `d120723`, the reviewers and the implementers' own checks found the real bugs of these plans. One example is embedding-data plan 15 `348e37c`: the code removed a foreign `.part` file, and the tests still passed. In another, the task reviewer of ces-revisions plan 15 task 3 found 4 Important defects.

**Review cost.** Mutant bookkeeping is a large share of task-review findings. Examples are `mutants.md` claims, `Unproven:`, `Withdrawn:` and `Keeps:` lines that do not hold, and tests with no targeted catch.

The naics-embedder row also counts final-review Importants, because plan 20 had no task reviews.

| Repo | Important review findings | Bookkeeping | Code defect | Missing test | Docs or other |
|---|---|---|---|---|---|
| embedding-data (plans 11, 13–15) | 55 | 23 | 8 | 20 | 4 |
| ces-revisions (plan 14) | about 15 | 10 | 0 | 1 | 4 |
| naics-embedder (plans 19–21) | 14 | 6 | 1 | 3 | 4 |
| agent-skills (plans 101–102) | 27 | 5 | 10 | 3 | 9 |

Each bookkeeping finding starts a fix round, and each fix round starts another full mutant run. Before the mutant step, embedding-data plan 9 had 4 Important findings over 9 tasks, all about code or the spec.

**The owner's proxy cannot answer yet.**

- Codex ran a final review on 5 mutant-era plans with code tasks. They are agent-skills plans 97, 99 (clean) and 100, ces-revisions plan 15 (1 finding) and naics-embedder plan 20 (2 findings). It was skipped or not approved on embedding-data plan 11 and ces-revisions plans 13 and 14. The newest plans have no final review yet. agent-skills plan 100 used mutants only at its final gate, and its final reviews found at least 12 findings, about 10 of them class (a).
- agent-skills has the only usable "before" group. In 20 pre-mutant plans (69–96), final reviews found 35 code-behavior findings over 63 code tasks. That is 0.56 for each task: 23 class (a), 11 class (b) and 1 class (c). This rate counts Minor findings too. The mutant-era tasks with a finished final review are 8 tasks (plans 97, 99 and 101) with 2 findings (0.25 for each task). Task reviews had raised both of them first. Eight tasks is too few to call a trend. The later plans are also guard and kit code, written by other models.
- In the other repos the "before" group is one to three plans, with different sizes and processes.
- Mutant-era final reviews still found class (b) gaps (stated rule with no test). naics-embedder plan 20 had 3, ces-revisions plans 13 and 15 had 3, and embedding-data plan 11 had 1. No class (a) or (c) finding appeared in an embedding-data mutant-era final review, but its three newest plans have no final review yet.

## 5. Parallel runs: what was measured

**xdist inside each run** (`-n`, through the repo's own overlay `tests/xdist-requirements.txt`, no lockfile change). This needs no script change: `mutant-run` already reads xdist JUnit reports correctly (naics-embedder plan 19 ran `-n auto`).

| Suite | Serial wall | `-n 2` wall | `-n 4` wall |
|---|---|---|---|
| ACS wage rules (314 tests, about 7 s) | 8.8 s | 6.7 s | 7.0 s |
| Vendor link layouts (417 tests, under 1 s) | 2.2 s | 3.3 s | — |

xdist gives about 1.3× on a 7 s suite and makes a sub-second suite slower. Two tests take 2.2 s and 1.6 s of the ACS suite and set its floor. Medians of 3 runs each. Suites of 15–60 s, which hold 54% of the mutant time, were not measured. naics-embedder plan 19 already ran `-n auto` and still took about 115 s for each mutant. xdist workers also add load on a busy machine, as parallel mutants do.

**Mutants in parallel** (one clone and one `.venv` for each worker, real `mutant-run`, 16 ACS-wage mutants split 4 ways):

| Rep | Serial (16 mutants) | 4 workers (4 mutants each) | Speedup | Load average at start |
|---|---|---|---|---|
| 1 | 281 s | 149 s | 1.9× | 24 → 54 |
| 2 | 322 s | 120 s | 2.7× | 61 → 49 |

All verdicts matched. The speedup is less than 4× for two reasons: each worker ran its own baseline and revert, and the machine was already loaded. In rep 2 the four workers used 351 s of pytest time, against 288 s for the serial run. A `uv sync --locked` for a new clone took 0.3 s, because uv clones from its cache.

**Traps for a parallel design:**

- A worker must not share a `.venv` with an editable install. The venv would import the original `src/`, and every mutant would falsely read SURVIVED. Each clone in this study imported its own `src/`, and that was checked.
- The run-file contract (one file, one baseline, the revert, the `mutant-active` marker and its recovery) assumes one working tree. A parallel runner must merge worker results into the same run file that `task-done` and the reviewer read.
- This machine often runs several plan executions at once. A runner with no cap moves CPU from one session to another and does not raise total throughput.

## 6. Recommendations

1. **Incremental middle runs (largest saving, low risk).** Let `mutant-run` run a chosen set of patches, for example survivors, invalid mutants and new or changed patches, and mark that run file as partial. `task-done` already reads only the newest run, and it already refuses a run that lacks a mutant that the mutants file lists. So a partial newest run fails the gate as `task-done` stands, and the final full run at HEAD stays the evidence of record. Expected saving: about 45% of mutant time. Risk: in 10,139 re-runs no caught mutant became a survivor. One implementer already did a version of this by hand. Plan 102 task 7 first screened 189 patches with `-x`, which stops pytest at the first failing test. Then it made the official run. A partial run could also use `-x`, because only the final run needs the full `tests:` map. A partial run with `-x` must skip the revert, because the revert needs every test to run.
2. **Cap the number of mutants (second-largest saving).** Ask for one mutant aimed at each stated rule and at each test that the task adds. Ask for no bulk generator that mutates every literal or operator. A fixed ceiling needs more data first: no tally of the tests that each task added was made here. The median task wrote 46 mutants where 10 already gave every caught test a catch. This changes implementer wording, so it needs the writing-skills micro-test.
3. **xdist only for slow focused suites.** When a focused suite's baseline is 5 s or more and the repo has an xdist overlay, add `-n 2` to the command. This needs only a sentence in `mutants.md`, not a script change. Never use it for sub-second suites. Expected gain: about 1.3× on a 7 s suite. The gain on 15–60 s suites is not measured, and it falls when the machine is busy.
4. **Parallel workers last, with a cap.** Add a `MUTANT_RUN_JOBS` setting (default 1) for one clone and one venv per worker, with results merged into one run file. Measured: 1.9–2.7× wall time at 4 workers, for about 22% more CPU. Do this only after 1 and 2, and only with a cap tied to free cores, because sibling sessions already saturate the machine.
5. **Measure the benefit before the step grows.** Record for each task whether a survivor or an input-shape row led to a change in non-test code. Run the Codex final review on code plans, so that the owner's proxy has data. After about 5 more plans with Codex reviews, compare class (a)–(c) findings for each task with agent-skills' pre-mutant rate of 0.56. Suppose the mutant runs still find a code defect in only about 1 task in 50. Then keep the cheap parts, the step-2 input-shape table and the revert, and make the mutant runs opt-in. One candidate rule is to require mutants only for new parsing, validation and grading code, where the one confirmed catch was.
6. **Cut review churn.** Bookkeeping was 23 of 55 Important task-review findings in embedding-data and 10 of about 15 in ces-revisions plan 14, but 5 of 27 in agent-skills. Each one costs a fix round and a full re-run. Recommendation 1 removes the re-run cost. Whether the reviewer should check bookkeeping less is a separate design question.

Recommendations 1, 2 and 4 change the `mutant-run` contract or implementer wording. They need the spec-then-plan path, not a direct edit.

## 7. Caveats

- The time totals cover only run files still on disk. Some workspaces are gone: agent-skills plans 97, 99 and 100, ces-revisions plans 12, 14 and 16, and embedding-data plan 12. The true total is therefore higher.
- The window is short: about four days and 52 tasks. Several plans were still running (embedding-data 13–15, naics-embedder 20–21).
- For the gone workspaces, and naics-embedder plans 16–17, the agents took mutant use from commit bodies, plan text or transcripts.
- Finding classes rest on one-line ledger summaries, read by agents. Treat each count as approximate.
- The incremental saving counts by patch SHA. A patch that was rewritten gets a new SHA and counts as new, so the saving is a lower bound.
- The benchmark ran on a shared, loaded machine, with two reps. Its ratios show the direction and rough size, not exact speedups.
