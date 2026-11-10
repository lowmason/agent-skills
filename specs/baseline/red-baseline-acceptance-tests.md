# Acceptance-tests probe: results

**Plan:** `specs/plans/completed/81-spec-derived-acceptance-tests.md` (plan 81). **Spec:**
`specs/spec-derived-acceptance-tests.md`, Verification, "Probe first". **Date:** 2026-11-08.

This record gives the probe's results. It recommends nothing about the build plan. The owner reviews the
results against the spec's bars and decides what the build plan keeps (spec decision D8). The kit, the copies
and every rep's prompt and reply are in `specs/baseline/red-baseline-acceptance-tests/`.

**Read section 8, item 1 first.** The final review found that the adjudicator prompts did not pair the
reader's tests with their tasks. Every treatment-arm number in this record comes from those prompts. The
control's numbers do not.

Terms used in this record:

- A **copy** is a completed plan with one planted misread, or with none (`p55-clean`).
- The **control** runs the current Self-Review checklist. It is one fresh `claude -p` call, told that it wrote
  the plan, with the spec and the whole copy (plan 81 default DF11).
- A **treatment arm** is a second reader and an adjudicator. The **Claude arm** has an `opus` reader. A
  **Codex arm** has a Codex reader, on `gpt-6-sol` or on `gpt-6.1-sol`. Every arm uses the same `opus`
  adjudicator and the same prompt template.
- A **rep** is one repetition: one control call, or one reader call and one adjudicator call on that reply.
- A **catch** is an adjudicator ruling (or a control finding) that rules the plan wrong, quotes the spec
  sentence that holds the planted value, and names a planted token.
- A **false alarm** is a ruling against an assertion that agrees with the copy's spec. An **unclear case** is a
  ruling with the verdict "unclear". A **real** ruling names an error in the approved plan itself, against the
  copy's spec. An **interface** ruling disputes a name, path or type against an Interfaces block (default DF10).
- An **`amendment:` false alarm** rules against a value that the plan's own owner-approved spec amendment sets.
  Each copy keeps its spec as it stood at plan review, without the amendment (default DF2), so the adjudicator
  cannot see the amendment.

## 1. Date, sources and versions

- Runs: 2026-11-08. The pilot, the control and the Claude arm (plan 81 Tasks 2 and 3) ran in a cloud
  container. The Codex arms (Task 4) ran on the owner's Mac.
- Copies, each from the plan and the spec as the owner approved them, before execution (DF2):
  - `p53-unit`: `specs/plans/53-agent-skills-portability.md` and `specs/agent-skills-portability-spec.md` at
    `b8f4d0f`.
  - `p66-bound`: `specs/plans/66-package-versions.md` and `specs/package-versions.md` at `526b7de`.
  - `p55-default` and `p55-clean`: `specs/plans/55-test-suite-registry.md` and `specs/test-suite-registry.md`
    at `f0ebef6`.
- The control prompt's Self-Review checklist: `skills/writing-plans/SKILL.md` at `origin/main` `ca3404f`.
- Claude Code: 2.1.319 for the pilot, the control and the Claude arm. 2.1.316 for the Codex arms'
  adjudicators and their isolation probe. No 2.1.319 binary was on the owner's Mac.
- Claude model: `opus` for the control, the Claude reader and every adjudicator. Every rep's `modelUsage`
  names `claude-opus-5-5` only.
- codex-cli 0.163.0. The log headers name `gpt-6-sol` on all 20 reps of the first Codex arm and `gpt-6.1-sol`
  on all 20 reps of the second, each with `reasoning effort: ultra`.
- The owner approved the Codex runs for this session on 2026-11-08 (Task 4 Step 1): "The Codex arm sends the
  probe's specs and reader inputs to OpenAI."

## 2. The plants

The spec plants three misreads (Verification, step 2). Each copy carries one, at every site where the plan
states that value. `SITES.txt` in each copy lists the sites.

- **`p53-unit`, a wrong unit.** Spec R1.3: `compatibility` is "a string of 1–500 characters after stripping".
  Planted as 500 UTF-8 bytes. 15 sites: 1 in the Global Constraints, 3 in test steps and 11 in code steps.
- **`p66-bound`, an inclusive bound made exclusive.** Spec R2.1: the cutoff is "00:00:00Z on the day after
  the freeze date", and "Files uploaded on the freeze date itself (UTC) are included". Planted as 00:00:00Z on
  the freeze date, which excludes the freeze day. 19 sites: 1 in the labels list, 1 in the Global
  Constraints, 12 in test steps, 4 in code steps and 1 in step text.
- **`p55-default`, a wrong default.** Spec R2.2: `pythons` has "Default `['3.13']`". Planted as `['3.12']`.
  16 sites: 1 in an Interfaces block, 11 in test steps, 2 in code steps, 1 in step text and 1 in the
  planning record.
- **`p55-clean`:** plan 55 unchanged, to count false alarms.

The reader gets only the spec, the Tech Stack line, the Files lists and the Interfaces blocks (spec Design 2).
So only one plant reaches the reader's inputs: `p55-default`'s Interfaces site (`3.12` once in the reader
prompt). No planted token is in the `p66-bound` or `p53-unit` reader prompt. There, a catch needs the reader's
tests to disagree with the plan's tests, so that the adjudicator gets a case to rule on.

## 3. The table

`runs/TABLE.txt` holds the output of `measure.py table specs/baseline/red-baseline-acceptance-tests/runs`, and two
counts of the false alarms from the `CLASSIFY.txt` files. Each row gives an arm and a copy: the scored reps,
the catches out of 5 (`n/a` for the clean copy), the false alarms per rep (the mean, then each rep), the
unclear cases per rep, and the real and interface rulings in all 5 reps. Every rep of every arm scored. No
rep was VOID, and none was rerun. The treatment-arm rows come from adjudicator prompts that did not pair the
reader's tests with their tasks (section 8, item 1).

```text
adjudicator-codex-gpt-6-sol p53-unit     scored=5 catches=1/5 false_alarms/rep=3.2 [3, 4, 3, 3, 3] unclear/rep=1.8 [2, 0, 3, 2, 2] real=5 interface=0
adjudicator-codex-gpt-6-sol p55-clean    scored=5 catches=n/a false_alarms/rep=2.0 [2, 2, 2, 2, 2] unclear/rep=0.6 [0, 0, 1, 2, 0] real=2 interface=0
adjudicator-codex-gpt-6-sol p55-default  scored=5 catches=5/5 false_alarms/rep=2.0 [2, 2, 2, 2, 2] unclear/rep=0.8 [1, 1, 1, 1, 0] real=0 interface=0
adjudicator-codex-gpt-6-sol p66-bound    scored=5 catches=5/5 false_alarms/rep=1.4 [3, 1, 2, 0, 1] unclear/rep=2.4 [0, 2, 3, 0, 7] real=1 interface=1
adjudicator-codex-gpt-6.1-sol p53-unit     scored=5 catches=1/5 false_alarms/rep=5.0 [5, 5, 6, 3, 6] unclear/rep=0.8 [1, 1, 0, 1, 1] real=9 interface=0
adjudicator-codex-gpt-6.1-sol p55-clean    scored=5 catches=n/a false_alarms/rep=2.0 [2, 2, 2, 2, 2] unclear/rep=0.4 [1, 0, 0, 0, 1] real=0 interface=0
adjudicator-codex-gpt-6.1-sol p55-default  scored=5 catches=5/5 false_alarms/rep=2.0 [2, 2, 2, 2, 2] unclear/rep=0.0 [0, 0, 0, 0, 0] real=0 interface=0
adjudicator-codex-gpt-6.1-sol p66-bound    scored=5 catches=5/5 false_alarms/rep=0.8 [2, 0, 1, 1, 0] unclear/rep=2.6 [3, 1, 2, 3, 4] real=2 interface=1
adjudicator-opus       p53-unit     scored=5 catches=0/5 false_alarms/rep=2.6 [2, 2, 4, 3, 2] unclear/rep=2.6 [4, 2, 2, 3, 2] real=10 interface=0
adjudicator-opus       p55-clean    scored=5 catches=n/a false_alarms/rep=2.8 [3, 2, 2, 3, 4] unclear/rep=3.0 [1, 3, 4, 3, 4] real=3 interface=0
adjudicator-opus       p55-default  scored=5 catches=5/5 false_alarms/rep=2.6 [2, 3, 2, 2, 4] unclear/rep=2.6 [3, 0, 4, 4, 2] real=3 interface=0
adjudicator-opus       p66-bound    scored=5 catches=5/5 false_alarms/rep=0.4 [1, 0, 1, 0, 0] unclear/rep=1.6 [1, 3, 2, 0, 2] real=3 interface=3
control-opus           p53-unit     scored=5 catches=5/5 false_alarms/rep=2.8 [2, 3, 3, 3, 3] unclear/rep=0.0 [0, 0, 0, 0, 0] real=5 interface=0
control-opus           p55-clean    scored=5 catches=n/a false_alarms/rep=4.4 [5, 4, 6, 3, 4] unclear/rep=0.0 [0, 0, 0, 0, 0] real=14 interface=0
control-opus           p55-default  scored=5 catches=5/5 false_alarms/rep=3.2 [3, 3, 2, 3, 5] unclear/rep=0.0 [0, 0, 0, 0, 0] real=7 interface=0
control-opus           p66-bound    scored=5 catches=5/5 false_alarms/rep=4.0 [3, 4, 5, 4, 4] unclear/rep=0.0 [0, 0, 0, 0, 0] real=18 interface=0
```

False alarms whose `CLASSIFY.txt` reason starts `amendment:`, of all false alarms in the 5 reps:

| Copy | Claude arm | Codex `gpt-6-sol` | Codex `gpt-6.1-sol` | Control |
|---|---|---|---|---|
| `p53-unit` | 10 of 13 | 10 of 16 | 18 of 25 | 0 of 14 |
| `p55-clean` | 14 of 14 | 10 of 10 | 10 of 10 | 0 of 22 |
| `p55-default` | 13 of 13 | 10 of 10 | 10 of 10 | 0 of 16 |
| `p66-bound` | 1 of 2 | 4 of 7 | 3 of 4 | 0 of 20 |

False alarms per rep without the `amendment:` lines:

| Copy | Claude arm | Codex `gpt-6-sol` | Codex `gpt-6.1-sol` | Control |
|---|---|---|---|---|
| `p53-unit` | 0.6 [0, 0, 2, 1, 0] | 1.2 [1, 2, 1, 1, 1] | 1.4 [1, 1, 2, 1, 2] | 2.8 [2, 3, 3, 3, 3] |
| `p55-clean` | 0.0 | 0.0 | 0.0 | 4.4 [5, 4, 6, 3, 4] |
| `p55-default` | 0.0 | 0.0 | 0.0 | 3.2 [3, 3, 2, 3, 5] |
| `p66-bound` | 0.2 [0, 0, 1, 0, 0] | 0.6 [2, 0, 1, 0, 0] | 0.2 [1, 0, 0, 0, 0] | 4.0 [3, 4, 5, 4, 4] |

59 of the control's 72 false alarms are findings on today's writing-plans format, which the approved plans
predate (section 8, item 6).

## 4. The bars

The bars come from the spec's "Proposed bars". Default DF5 applies the false-alarm and unclear bars per plan:
a bar holds when the mean over a copy's 5 scored reps is at most 1.0. The owner decided on 2026-11-08 that
each bar is judged on the literal counts and on the counts without the `amendment:` lines.

**The control.** Its bar is "at most 2 of 5" catches. It caught each plant in 5 of 5 reps (`p53-unit`,
`p66-bound` and `p55-default`), so it missed the bar on all three plants.

**The treatment arms:**

| Bar, per copy | Claude arm | Codex `gpt-6-sol` | Codex `gpt-6.1-sol` |
|---|---|---|---|
| Catches at least 4 of 5: `p53-unit` | missed (0/5) | missed (1/5) | missed (1/5) |
| Catches at least 4 of 5: `p66-bound` | met (5/5) | met (5/5) | met (5/5) |
| Catches at least 4 of 5: `p55-default` | met (5/5) | met (5/5) | met (5/5) |
| False alarms at most 1.0, literal: `p53-unit` | missed (2.6) | missed (3.2) | missed (5.0) |
| False alarms at most 1.0, literal: `p55-clean` | missed (2.8) | missed (2.0) | missed (2.0) |
| False alarms at most 1.0, literal: `p55-default` | missed (2.6) | missed (2.0) | missed (2.0) |
| False alarms at most 1.0, literal: `p66-bound` | met (0.4) | missed (1.4) | met (0.8) |
| False alarms at most 1.0, without `amendment:`: `p53-unit` | met (0.6) | missed (1.2) | missed (1.4) |
| False alarms at most 1.0, without `amendment:`: `p55-clean` | met (0.0) | met (0.0) | met (0.0) |
| False alarms at most 1.0, without `amendment:`: `p55-default` | met (0.0) | met (0.0) | met (0.0) |
| False alarms at most 1.0, without `amendment:`: `p66-bound` | met (0.2) | met (0.6) | met (0.2) |
| Unclear cases at most 1.0: `p53-unit` | missed (2.6) | missed (1.8) | met (0.8) |
| Unclear cases at most 1.0: `p55-clean` | missed (3.0) | met (0.6) | met (0.4) |
| Unclear cases at most 1.0: `p55-default` | missed (2.6) | met (0.8) | met (0.0) |
| Unclear cases at most 1.0: `p66-bound` | missed (1.6) | missed (2.4) | missed (2.6) |

`gpt-6-sol` missed bars on both counts, so Task 4 Step 6 ran the config default, `gpt-6.1-sol` (spec D7 and
Verification step 4). No bar was "not run".

**One label moves a bar.** The counts without `amendment:` for `p53-unit` rest on one judgment. All 5 reps of
each Codex arm, and 1 rep of the Claude arm, rule against plan 53's default DF11. DF11 renames
`recommend-causal-design`'s skill `LICENSE` to `LICENSE-causal-design-sources` and maps that file to the
skill. Spec R4.1's table does not list that file, but R4.2 says "Every root `LICENSE*` file is mapped to at
least one skill." Task 3 labeled this ruling a false alarm, and Task 4 kept that label, so that one rule
covers every arm. With the label `real` instead, the `p53-unit` counts without `amendment:` would be 0.4
(Claude arm), 0.2 (`gpt-6-sol`) and 0.4 (`gpt-6.1-sol`). Every arm would then meet that bar on `p53-unit`.

## 5. The Codex arms against the Claude arm

The spec's rule: "The Codex arm stays only if it beats the Claude arm on catches or on false alarms." The
numbers follow. The owner applies the rule (D8).

**Catches.** The Claude arm caught 10 of 15 plants and each Codex arm 11 of 15. The difference is one rep of
`p53-unit` in each Codex arm (1 of 5 against 0 of 5):

- `gpt-6-sol` rep 4: the adjudicator ruled the plan wrong on the message in the plan's own test,
  "compatibility must be a string of 1-500 bytes", and quoted R1.3. The reader's tests used ASCII values only.
  The two test sets agree on all of those inputs, so this ruling did not come from a conflict between them.
  Adjudicator rule 5 says not to rule on such a case. The scorer counts it because it meets the spec's
  definition of a catch. Without it, `gpt-6-sol` ties the Claude arm on catches, 10 of 15.
- `gpt-6.1-sol` rep 3: the reader's test passes `"é" * 500` (500 characters, 1,000 UTF-8 bytes), the one input
  that separates the spec from the plant. It is the only such test in the 15 reader reps of the three arms.

**False alarms per rep**, the mean over the four copies:

| Count | Claude arm | Codex `gpt-6-sol` | Codex `gpt-6.1-sol` |
|---|---|---|---|
| Literal | 2.10 | 2.15 | 2.45 |
| Without `amendment:` | 0.20 | 0.45 | 0.40 |

By copy, both Codex arms raise fewer false alarms than the Claude arm on the two `p55` copies (2.0 against
2.8 and 2.6), and every one of those is an `amendment:` false alarm. They raise more on `p53-unit` (3.2 and 5.0
against 2.6). On `p66-bound`, `gpt-6-sol` raises more (1.4 against 0.4), and so does `gpt-6.1-sol` (0.8).
Without `amendment:`, the Claude arm has the lowest count, or a tied count, on every copy.

**Other measures** (not in the spec's rule):

| Measure | Claude arm | Codex `gpt-6-sol` | Codex `gpt-6.1-sol` |
|---|---|---|---|
| Unclear cases per rep, mean over the copies | 2.45 | 1.40 | 0.95 |
| Real rulings, all copies | 19 | 8 | 11 |
| Reader tests per reply, mean (range) | 63.4 (46–82) | 41.1 (30–50) | 56.6 (46–77) |
| Reader flags per reply, mean | 5.1 | 3.1 | 2.9 |

## 6. Real rulings

Each row is one error in an approved plan, judged against the copy's spec. The count in each column is the
number of reps that ruled on it. The control made 44 real rulings on 17 errors. The treatment arms made 38 on
5 errors, and the control also found each of those 5.

| Copy | Spec text quoted | The plan | Control | Claude arm | `gpt-6-sol` | `gpt-6.1-sol` |
|---|---|---|---|---|---|---|
| `p53-unit` | R1.9: "CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run)" | owner decision D7 drops the line, and the plan has no R1.9 amendment | 3 | 5 | 5 | 5 |
| `p53-unit` | R3.7: "A `skills/*/scripts/*.py` file with a `__main__` guard carries a PEP 723 block that parses with `tomllib` and has `requires-python` and `dependencies`." | DF6 exempts vendored scripts (`VENDORED_SCRIPTS`), and a plan test passes one without a header | 1 | 5 | 0 | 4 |
| `p53-unit` | Task 2 record: "Record the scenario, prompts, outputs, and verdicts in `specs/baseline/red-baseline-description-openings-<YYYY-MM-DD>.md`, the house red-baseline format." | keeps only a prompt hash and each output's first 150 characters | 1 | 0 | 0 | 0 |
| `p55-clean`, `p55-default` | R6.2: "`test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint." | the plan test writes `test_scan.py` | 2 | 6 | 2 | 0 |
| `p55-clean`, `p55-default` | R5.3: "one sentence names `suites.toml` and `run_suites.py` and says that `--check` is a commit lint." | adds a two-sentence paragraph | 8 | 0 | 0 | 0 |
| `p55-clean`, `p55-default` | R6.1: "validation: each R3.9 failure, with exit 2" | tests exit 2 for one failure kind only | 4 | 0 | 0 | 0 |
| `p55-clean`, `p55-default` | R2.1: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file." | the header says "a commit lint" | 4 | 0 | 0 | 0 |
| `p55-clean`, `p55-default` | Verification: "Then run `--all` once, and record each run's result beside the direct result." | Task 7 Step 3 records no `--all` result | 2 | 0 | 0 | 0 |
| `p55-default` | R5.1: "Drop "There is no root test runner" and the sentence that comments name the skip-unlocking deps." | keeps the clause "pytest's summary line gives the counts" | 1 | 0 | 0 | 0 |
| `p66-bound` | R4.1 item 4: "Each script's `requires-python` must match the Python floor in its `SKILL.md` `compatibility:` line." | owner decision D4 lets a lower script floor pass, and the plan has no R4.1 amendment | 5 | 2 | 1 | 2 |
| `p66-bound` | R2.3: "`build/check_jax_examples.py` and its documented command: they install `stack('jax-cpu')` in place of `--with-requirements specs/verification/32-jax-cpu.txt`." | the rewrite also drops `JAX_PLATFORMS=cpu` from the documented command | 4 | 0 | 0 | 0 |
| `p66-bound` | R5: "Illustrative text, such as the run manifest at `skills/evaluate-deep-learning/references/experiments.md:86-87`, goes on `HISTORICAL` with a reason." | no task handles that file | 3 | 0 | 0 | 0 |
| `p66-bound` | R7: "`build/test_run_suites.py` and `build/test_check_frontmatter.py:434` build their expected commands from the file, not from a `3.13` literal." | leaves that test on its literal | 2 | 1 | 0 | 0 |
| `p66-bound` | Constraints: "Plan 63. It edits `build/run_commit_lints.sh`. This work lands after plan 63, or the plan that lands second rebases onto the other and re-reads the anchors." | states that plan 63 does not edit it, and drops the landing-order rule | 1 | 0 | 0 | 0 |
| `p66-bound` | R1.3: "A package gets a `[cited]` entry when skill prose cites a version for it and no check runs it." | the inventory lists `numpydoc>=1.11`, and `[cited]` leaves it out | 1 | 0 | 0 | 0 |
| `p66-bound` | R2.3: "Retire `specs/verification/32-jax-cpu.in` and `32-jax-cpu.txt`, and point their readers at `build/versions.toml`." | no task edits `build/check_jax_examples.py`, which names that path | 1 | 0 | 0 | 0 |
| `p66-bound` | R5 step 5: "The known stale citations are the Polars, Altair and plotly lines, …" | keeps the Altair and plotly lines in `[cited]`, and no task re-checks them | 1 | 0 | 0 | 0 |

**Interface rulings.** One plan value drew them: the return shape of `late_pins` in `p66-bound` (messages
or package specs), against its Interfaces wording. Spec R3.6 asks only that the error name the package and
the date, and the plan's message does. The Claude arm ruled on it in 3 reps, each Codex arm in 1.

## 7. Cost

- **Claude** (the sum of `total_cost_usd`): $40.68 for 105 `claude -p` calls. Pilot and isolation probes
  $1.33 (5 calls). Control $5.04, Claude reader $11.32 and Claude-arm adjudicator $7.98 (20 calls each).
  Codex-arm adjudicators $6.95 (`gpt-6-sol`) and $8.06 (`gpt-6.1-sol`), 20 calls each. No call reached its
  $4.00 cap (default DF8). Task 3, with the pilot, cost $25.66, against a $150 stop.
- **Codex** (the owner's ChatGPT login, so no dollar figure): 40 reader reps used 1,830,388 tokens, as the
  logs' `tokens used` lines give them: 837,950 on `gpt-6-sol` and 992,438 on `gpt-6.1-sol`. The three
  context probes used 61,670 more. At `ultra` effort a reader rep took about 9 to 12 minutes. The four copies
  ran in parallel, 5 reps each, so an arm took about 45 minutes (`gpt-6-sol`) and 60 minutes
  (`gpt-6.1-sol`).

## 8. What the probe cannot show

The spec's own assessment, "What a second reading can and cannot catch", is that a second reading catches
transcription errors, finds ambiguity without resolving it, and misses shared blind spots. The probe tests
only the first kind: each plant is a value that the spec states and the copy changed. These are its limits:

1. **The adjudicator prompts did not pair the reader's tests with their tasks.** Plan Task 2 Step 5 gives each
   task section "the reader's tests and flags for that task", and spec Design 4 says that the adjudicator
   "reads both test sets for each task". But `build_prompts.py` split the reader's module before every `def`
   and decorator line. So each test's `# spec:` and `# task:` lines went into its task's `<acceptance-tests>`
   section. The test function itself went into one shared `<acceptance-tests-without-a-task>` section, without
   those lines. The decorators of all 433 decorated tests went into the shared preamble, apart from their tests. All
   60 treatment-arm adjudicator prompts have this layout, and so does the Task 2 pilot prompt: their task
   sections hold 3,222 comment pairs and no test code. The adjudicator therefore had to match each test to its
   task and its spec sentence by itself.
   - Not affected: the control (its catches, its false alarms and its bar miss), the 60 reader replies, and
     the reason for the `p53-unit` result (item 2), which does not depend on the prompt layout.
   - Measured with this layout: every treatment-arm count in sections 3 to 6, the treatment rows of the bars
     in section 4, and the comparison in section 5. The size and the direction of the effect are unknown. The
     catches could move as well.
   - The final review found the defect (code-reviewer and Codex). Its fix pass corrected the split, and
     `build_prompts.py selftest` pins it on a sample and on the 60 committed reader replies. Built with the
     fix, the 60 prompts hold all 3,222 reader tests under their tasks. The committed prompts and runs are
     unchanged, and no rep was rerun. The committed prompts come from the kit as it was before the fix, so the
     kit now builds different prompts from the same replies. A rerun of the 60 adjudicator reps is the owner's
     decision (D8).
2. **The `p53-unit` plant almost never reached the adjudicator as a case.** The plan's own test of R1.3 uses
   `'x' * 500` and `'x' * 501`. Of the 15 reader reps, 14 also tested R1.3 with ASCII values only, and no
   reader flagged the unit (the plant has no Interfaces site, so no reader saw it). For ASCII text,
   characters and UTF-8 bytes give the same count. So the two test sets agreed on every input, and the
   adjudicator had no conflict to rule on. The Claude arm caught the plant in 0 of 5 reps and each Codex arm
   in 1 of 5 (section 5). This is the blind-spot pattern in a small form: nearly every reading left out the
   one input that tells the two readings apart. The control reads the whole copy, the plan's prose included,
   and it caught the plant in 5 of 5 reps.
3. **Amendments read as false alarms.** Each copy keeps its spec as it stood at plan review (DF2). A plan
   that amends its own spec in a task therefore states values that the copy's spec contradicts. Most of the
   treatment arms' false alarms are rulings against those values (section 3). At a real plan review, the
   spec has not yet received the plan's amendments either.
4. **Small sample.** Three plants in three plans, one clean copy, 5 reps per arm and copy. With 5 reps, a
   true catch rate of 70% still meets the 4-of-5 bar about half the time (53%).
5. **One judge.** The executors labeled every false alarm, real ruling and near catch by hand (DF10), with
   one reason line each. Task 4 reused Task 3's reason lines word for word where a plan value recurs. No
   second person checked the labels. Section 4 names the one label that moves a bar.
6. **The approved plans are older than today's writing-plans.** The control judged them by today's
   checklist. Findings on format only (Review Focus, plan length, the Decisions-line form) count as false
   alarms (Appendix B, Task 3), so the control's false-alarm counts measure format drift as well.
7. **The control is a fresh session, so it is a best case for Self-Review.** The spec's control is "a fresh
   planner session" (Verification, step 3), told that it wrote the plan (DF11). To that session, each plant is
   a plain contradiction between the spec and the plan, and nothing ties it to the planted value. The plants
   also give no reason for the planted value. A real misread comes from the planner's own reading of the spec,
   and a Self-Review in the same session can read the spec the same way again. So the control's 15 of 15
   catches is an upper bound for Self-Review on these plants. The probe does not test the case that a second,
   independent reading exists for: a misread that the planner repeats when it reviews its own plan.
8. **The arms did not run in one place.** The Claude arm's adjudicator ran on Claude Code 2.1.319 in a cloud
   container. The Codex arms' adjudicators ran on 2.1.316 on the owner's Mac, under `env -i`. All used the
   same prompt form, model and flags.
9. **The Codex reader is not the owner's everyday Codex.** Its isolation flags drop the user's
   `config.toml` (Appendix A). Its context still held the owner's global `~/.codex/AGENTS.md` and the skills
   list, by the owner's decision.

## Appendix A. Isolation of the reps

**Claude reps.** Every `claude -p` rep ran as plan 73's kit runs it: from a fresh empty folder under `/tmp`,
with `--tools ""`, `--strict-mcp-config`, `--setting-sources ""`, `--no-session-persistence`, a budget cap,
`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`. Plan 73's five-line context
probe answered NO on every line on both Claude Code versions (`runs/pilot/isolation/` on 2.1.319,
`runs/pilot/isolation-local/` on 2.1.316). On the owner's Mac the reps also ran under `env -i` with only
`HOME`, `USER`, `LOGNAME`, `PATH`, `SHELL`, `TMPDIR` and `LANG`. The Claude Desktop session that drove them
exports `CLAUDE_EFFORT=max` and its own session variables, which a child `claude -p` would inherit.

**Codex reps.** `codex exec` has no `--tools ""`, and its `read-only` sandbox blocks writes, not reads. A
context probe with the same questions (`runs/pilot/codex-isolation/`) showed what reaches a rep:

| Reaches the rep | `run_codex.sh` as Task 2 wrote it | With Task 4's flags |
|---|---|---|
| The owner's global `~/.codex/AGENTS.md` | yes | yes |
| An output style, from plugins' SessionStart hooks | yes | no |
| The skills list (Codex system skills and `~/.agents/skills`) | yes | yes |
| A shell, and so every file on the Mac, `SITES.txt` included | yes | no |
| Web search | yes | no |
| The user's MCP servers, image generation, image view, goals | yes | no |
| Sub-agents, `apply_patch` (read-only), MCP resource tools, a clock, code-mode exec ("will fail closed") | yes | yes |

Task 4's flags are `--ignore-user-config`, `--ignore-rules`, `--ephemeral`, `-c web_search="disabled"`, the
`--disable` list in `kit/run_codex.sh` and a pinned `-c model_reasoning_effort="ultra"`. None of them edits
`~/.codex`. The owner decided that the reps run although `AGENTS.md` and the skills list still load ("Record
it and run"). Without a shell, a rep can read no file. `measure.py residual` checks each Codex log for any
line that is not the prompt, the reply or a known status line, such as a tool call. `measure.py score` checks
only a Codex rep's model, so the executor ran `residual` on each reader folder by hand. A rule fixed before the
first rep made a rep VOID if its leftover lines showed a tool call or any event other than the reply. The
check found no leftover line in the 40 reader logs.

## Appendix B. The executors' rulings

The execution ledger is git-ignored, so it is not committed. Its rulings and the owner's decisions are copied
here word for word, in ledger order.

```text
Ruling: this session runs Tasks 1-3 only, then pushes the branch and stops; no final review or Plan Completion Protocol here — owner D3 (handoff 2026-11-08): "open a new session for implementation of tasks 1-3"; overrides the skill's run-all-tasks rule — if wrong, Tasks 4-5 and the final review wait for another session, which the plan already expects for Task 4.
Owner confirmation (Global Constraints, "One execution at a time"): plan 80's execution has finished — owner, 2026-11-08: "Yes, it's finished" (handoff D4). Evidence: origin/main at ca3404f merges lowmason/agent-skills#150 and retires plan 80. Not asked again.
Task 2: Ruling: build_prompts redacts the copy's own plan path to `<this plan>` in reader and adjudicator prompts — plan 53's Task 15 Files list names `specs/plans/53-agent-skills-portability.md`, and spec Design 2 says the prompt names no plan path — if wrong, the reader loses one Files entry's path, which no test needs.
Task 2: Ruling: CLASSIFY.txt takes two more labels, near-catch and near-miss, for the executor's judgment of each near catch; table counts a near-catch as a catch and refuses an unjudged near catch — Task 3 Step 4 asks the executor to judge each near catch and record its reason, and Task 2 Step 1's CLASSIFY format had no line for it — if wrong, the judgments move to another file and table's count stays the same.
Task 2: Ruling: reader replies are scored as valid or VOID only (a <tests> block), since catches are scored on the adjudicator's replies; measure.py score picks the kind from the arm name (control-, adjudicator-, reader-, codex-) — the plan gives score one signature for every run dir — if wrong, a reader dir's SCORE.txt carries no catch column, which no bar reads.
Task 3: Ruling: CLASSIFY judges every control finding and adjudicator ruling against the copy's spec only (DF10): a finding that cites current writing-plans format (Review Focus, plan length, Decisions-line form) and names no contradicted spec sentence is a false-alarm, and each reason line says so — DF10 defines a false alarm as a ruling against an assertion that agrees with the spec, and the approved plans predate today's skill — if wrong, the control's false-alarm counts fall, which no bar reads (the control's bar is catches).
Task 3: Ruling: a treatment ruling against a plan value that the plan's own owner-approved spec amendment sets (p55's cc_guide, from Q1/D1 in Task 1) is labeled false-alarm, and its reason starts 'amendment:' — spec step 5 defines a false alarm as a ruling against a correct assertion, and DF2 keeps amendments out of the copy's spec — if wrong, the treatment false-alarm means fall; Task 5's record should give the counts with and without the 'amendment:' lines.
Task 3: Ruling: a to_classify ruling about the plant that carries no planted token (adjudicator-opus/p66-bound rep4 ruling6) is labeled near-miss in CLASSIFY, which table counts neither as a catch nor as a false alarm — it is the plant, so not a false alarm, and not an error in the approved plan, so not real — if wrong, that rep's counts do not change (it caught the plant in another ruling).
Ruling: this session runs Tasks 4-5 — the owner asked for the Tasks 4-5 handoff (2026-11-08) — if wrong, the session stops at Task 4 Step 7.
Ruling: the execution branch is origin/claude/acceptance-tests-probe-plan; this worktree's app-made branch claude/plan-81-acceptance-tests-exec-7b85b9 (at ca3404f, no commits of its own, clean tree) was reset to that branch's tip ab233eb and tracks it, so Task 4 Step 7 runs `git push -u origin HEAD:claude/acceptance-tests-probe-plan` — the handoff names that branch, and the app cut this worktree's branch from main — if wrong, the work is pushed to the probe branch, not to a new remote branch named after this worktree, and nothing else changes.
Task 4: Ruling: every claude -p rep in this session runs under `env -i` with HOME, USER, LOGNAME, PATH, SHELL, TMPDIR and LANG only — this Desktop session exports CLAUDE_EFFORT=max, CLAUDE_CODE_SESSION_ID, CLAUDE_CODE_MESSAGING_* and ANTHROPIC_BASE_URL, which a child claude -p inherits (memory, 2026-11-05), and Task 3 ran with no Desktop parent — if wrong, nothing is lost: env -i only removes variables, and run_reps.sh still sets its two disable flags.
Task 4: Owner decision (Step 1, 2026-11-08): "Yes, approve" to "The Codex arm sends the probe's specs and reader inputs to OpenAI. Approve the Codex runs for this session? That is 2 short context probes first, then 20 reader reps on gpt-6-sol, and 20 more on gpt-6.1-sol if plan 81's Step 6 runs."
Task 4: Owner decision (DF-A, 2026-11-08): "Yes, count both ways" — judge each bar on the literal counts and on the counts without 'amendment:' lines; a miss on either count runs Step 6.
Task 4: Owner decision (T2b contingency, 2026-11-08): "Record it and run" — if the flags still let ~/.codex/AGENTS.md or the skills list reach a rep, run anyway and list in the record what loaded.
Task 4: Ruling: run_codex.sh adds isolation flags to Task 2's command (--ignore-user-config --ignore-rules --ephemeral --enable skip_host_skill_discovery -c web_search="disabled" and --disable for shell_tool, unified_exec, code_mode_host, plugins, apps, hooks, skill_search, tool_suggest, multi_agent, goals, browser_use, computer_use, in_app_browser, image_generation, view_image, sleep_tool), pins -c model_reasoning_effort (6th arg, default ultra), and appends each call's prompt sha256, codex version, model, effort and flags to SOURCES.txt; every Codex call runs under the same env -i — the Claude reader had --tools "" and no user context, and the committed command gave the Codex reader a shell that reads the plant's answer key (SITES.txt), web search, the user's plugins and their output-style hooks; ~/.codex is not edited and auth.json is not touched — if wrong, the Codex reader differs from the owner's everyday Codex (no personality, verbosity or priority tier from config.toml), which the record states.
Task 4: Ruling: measure.py gains codex_residual() and `residual <run-dir> <prompt-file>` (selftest RED → GREEN): the log lines that the header, the prompt echo, the reply, user/codex/tokens-used lines, the token count and warning lines do not explain — the plan's scorer checks a Codex rep's model only, and a Codex rep can call tools — if wrong, one more check runs, and no count changes.
Task 4: Owner decision (2026-11-08, mid-run message): "Increase spend budget if needed" — a rep that stops on its --max-budget-usd cap (DF8: 4.00) reruns with a higher cap, ledgered; no cap had been reached when it arrived.
Task 4: Ruling: measure.py table counts the false-alarm, real and interface labels of near items too (selftest RED → GREEN) — control-opus/p53-unit rep2 ruling3 is a near item that Task 3 labeled false-alarm, which table dropped, so TABLE.txt read 2.6 [2, 2, 3, 3, 3] beside 14 false-alarm lines; regenerated, only that row moves, to 2.8 [2, 3, 3, 3, 3] — if wrong, the control's p53 false-alarm mean is 0.2 high, which no bar reads (the control's bar is catches). Task 3's CLASSIFY line is unchanged.
Task 4: Ruling: the Task 4 commit adds kit/run_codex.sh and kit/measure.py beside runs/ (Step 7's command adds runs/ only) — the runs depend on the isolation flags and the residual check, and the table fix changes TABLE.txt — if wrong, the kit changes sit in the Task 4 commit rather than in a commit of their own.
Final: Ruling: measure.py keeps crediting gpt-6-sol p53-unit rep4's catch (Codex P1) — spec Verification step 5 defines a catch as a ruling that the plan is wrong which quotes the right sentence, with no test-set-conflict condition; the record now says that the ruling broke adjudicator rule 5 and that gpt-6-sol ties the Claude arm on catches without it — if wrong, gpt-6-sol's catches are 10 of 15, not 11.
Final: Declined to judge (Codex P2): measure.py score() does not VOID a Codex reader rep whose log shows tool activity — the plan's scorer checks the model only (score_codex), and Task 4's pre-registered VOID rule runs measure.py residual as its own step, with a judgment on the leftover lines; it ran on all 40 reader reps with 0 leftover lines, and no Codex reader rep reruns. For the owner to rule.
```
