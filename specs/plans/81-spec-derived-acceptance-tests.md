# Acceptance-tests probe Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Measure, before any skill text changes, how many planted spec misreads a second reader plus an Opus
adjudicator catch at plan review, how many false alarms and unclear cases they raise, and how the current Self-Review
checklist does on the same plans.

**Architecture:** A kit in `specs/red-baseline-acceptance-tests/kit/` makes four plan copies from three completed
spec-and-plan pairs: three copies each carry one planted misread, and one copy is unchanged. It builds three kinds of
prompt: a control prompt (writing-plans' body, the spec and the whole copy), a reader prompt (the spec and only the
inputs the spec's Design 2 allows) and an adjudicator prompt (the spec, each task's Interfaces block, the plan's tests
and the reader's tests). Isolated `claude -p` reps run the control and the Claude arm. `codex exec` runs the Codex
reader on the owner's machine. A scorer counts catches, false alarms and unclear cases, and the results go to
`specs/red-baseline-acceptance-tests.md` for the owner's review (spec D8).

**Tech Stack:** Python 3.13 stdlib scripts run with `uv run python`, bash, `claude -p` (Claude Code 2.1.319 at
planning), `codex exec` (codex-cli 0.163.0 at the spec's check), git.

**Spec:** `specs/spec-derived-acceptance-tests.md` (APPROVED 2026-11-08; decisions D1–D8). This plan implements its
Verification section, "Probe first", only. The build plan comes after the owner reviews this plan's results (D8).

## Global Constraints

- **Probe only.** "Plan the probe first, as its own plan (Verification, "Probe first"). Write the build plan only
  after the owner has reviewed the probe's results." (spec header, D8). This plan changes no file under `skills/`,
  `agents/`, `commands/`, `hooks/`, `rules/` or `runtimes/`, and it writes no build plan.
- **One execution at a time.** No execution of this plan starts while another plan executes in this repository
  (owner ruling D10, `specs/plans/completed/73-reviewer-and-planning-contract.md:59`). This rule forbids overlap
  only. The owner ordered the two plans (D2): this plan starts only after plan 80's execution finishes. Before
  Task 1, ask the owner to confirm that plan 80's execution has finished.
- **Plan 80.** Plan 80 (branch `claude/zealous-bell-ltw3ta`, approved 2026-11-08) edits writing-plans' protocol steps
  3 and 5 and the gate paragraph of both executors' `references/final-review.md`. It does not change the Self-Review
  checklist (`skills/writing-plans/SKILL.md:208`), which the control arm uses. The control prompt reads writing-plans
  from `origin/main` at the time of the run and records that sha.
- **Leave alone.** Branch `claude/admiring-curie-2vilnz` (never push to it), plan 80 and its branch, and the build
  plan.
- **The pairs** (spec, Verification step 1): spec-and-plan pairs from `specs/completed/` and
  `specs/plans/completed/`, each with code tasks and exact values in its spec. This plan uses three: portability
  (plan 53), test-suite registry (plan 55) and package versions (plan 66). See DF1 and DF2.
- **The plants** (spec, Verification step 2): "an inclusive bound made exclusive, a wrong unit and a wrong default.
  Plant each one everywhere the plan states that value: the Global Constraints, the Interfaces blocks, the test steps
  and the code steps". "Keep one plan unchanged, to count false alarms."
- **Control arm** (step 3): "the current Self-Review checklist, run by a fresh planner session against the spec."
- **Treatment arms** (step 4): "the second reader and the adjudicator, with a Claude reader and with Codex. The Codex
  arm runs `gpt-6-sol` first (D7). It runs the config default, `gpt-6.1-sol`, only when `gpt-6-sol` misses a bar".
  "Codex is not installed in cloud sessions, so the Codex arms run where the owner's `codex` CLI is logged in."
- **Counts** (step 5): "planted misreads caught, false alarms and unclear cases. A catch means that the adjudicator
  rules the plan wrong and quotes the right sentence. A false alarm is a ruling against a correct assertion."
- **Bars** (spec, Proposed bars): "a treatment arm catches each planted misread in at least 4 of 5 repetitions. The
  control catches it in at most 2 of 5. A treatment arm raises at most one false alarm and at most one unclear case
  per plan." "The Codex arm stays only if it beats the Claude arm on catches or on false alarms." The owner reviews
  the results against these bars and decides what the build plan keeps (D8). This plan reports. It decides nothing.
- **Reader inputs** (spec, Design 2): "the requirement text, the plan's Tech Stack line, and each task's Files list
  and Interfaces block." "The reader never gets the Global Constraints, the task steps, the test code, the approach
  lines, the Review Focus section or the Decisions section." The reader "uses the Interfaces blocks for names, paths
  and types only. It takes every value from the requirement text, and it flags each plan value that differs from it."
- **Reader isolation** (spec, Design 2): the inputs sit outside the checkout, "The prompt names no plan path, and it
  tells the reader not to search for one."
- **Reader output** (spec, Design 2): "Each test names the spec sentence that it checks, and the task whose Produces
  it needs. The reader also lists the spec sentences that it could not turn into a test."
- **Adjudicator rule** (spec, Design 3): "Each case gets one ruling: the plan or code is wrong, the acceptance test
  is wrong, or the case is unclear. Every ruling except "unclear" quotes the binding text that decides it. No
  deciding text means "unclear"." For names, paths and types the binding text is the task's Interfaces block, "when
  the behavior under test does not change". It "never edits a file."
- **Models.** The control and the Claude reader run on `opus`, the adjudicator on `opus` (D3, spec Model tiers).
  Every `claude -p` call names `--model`. Every Codex call names `-m`, and its log header's model is recorded.
- **Codex data** (spec, Constraints): "A Codex run sends the spec, the Interfaces blocks and every file it reads to
  OpenAI." `CLAUDE.md:54` approves Codex review only, so the session that runs Task 4 asks the owner once before the
  first Codex run.
- **Rep isolation.** Every `claude -p` rep runs as plan 73's kit runs it
  (`specs/red-baseline-reviewer-planning-contract/kit/run_reps.sh`): a fresh empty directory under `/tmp`, outside
  every repository; `--tools ""`, `--strict-mcp-config`, `--setting-sources ""`, `--no-session-persistence`,
  `--output-format json`, `--max-budget-usd`; `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and
  `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`. A rep stopped by its budget cap, or with no parsable reply block, is VOID: it is
  rerun, never scored as a miss.
- **Provenance.** "No text or fixture comes from `prime-radiant-inc/superpowers-evals`, which carries no license."
  Knight and Leveson (1986) is cited for an idea only. The plan copies are this repository's own files.
- **Kit tests** are `selftest` subcommands, not pytest files (DF7).
- **Commit gate.** Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Commit messages
  follow Conventional Commits, use plain technical English and end with the attribution trailer that the executing
  session is given.
- **Completion.** At plan completion, the spec does not retire: the build plan is still to come (D8), even though no
  other live plan names the spec then. Completion adds the spec's link and the backlog progress note (Task 5).

## Review Focus

1. A heading or a test inside a code fence in an Interfaces block or a Files list: the reader must still get no
   test code and no step text. A leak makes the reader's reading a copy of the planner's (spec anti-goal 1). Pinned
   by `extract.py selftest` on all four copies (Task 1 Step 1).
2. A plant that leaves one statement of the true value in the copy: the control can then spot an internal
   contradiction, which no real misread gives it. Pinned by `make_copies.py selftest`'s true-pattern scan (Task 1
   Step 1).
3. A rep that hits its budget cap, or returns no `<rulings>` or `<findings>` block: it is VOID and rerun, never a
   miss and never a clean rep. Pinned by `measure.py selftest` (Task 2 Step 1).
4. An adjudicator ruling that catches the plant but quotes a paraphrase, not the spec sentence: the scorer lists it
   as a near catch for the executor to judge, never silently as a miss. Pinned by `measure.py selftest` (Task 2
   Step 1).
5. A Codex run that runs on a model other than the one named: the scorer refuses the rep. Pinned by
   `measure.py selftest` (Task 2 Step 1).

## Decisions

- **D1** (owner, plan review, 2026-11-08): approved the planner defaults DF1–DF11 as written ("Approve defaults"). DF8's cost stop is the one stop this plan adds. Applied in: Global Constraints, Tasks 1–5.
- **D2** (owner, plan review, 2026-11-08): execute inline (executing-plans), after plan 80's execution on the owner's machine finishes. Applied in: Global Constraints.

## Planner defaults (approved, D1)

The brief flagged no defaults. These are the planner's. The owner approved them at plan review (D1):

- **DF1. Pairs and plants.** One misread in each planted copy, so a catch is not confused with another plant:
  - `p53-unit`: portability spec R1.3, `compatibility` "a string of 1–500 characters after stripping", planted as
    500 UTF-8 bytes.
  - `p66-bound`: package-versions spec R2.1, the cutoff is "00:00:00Z on the day after the freeze date" and "Files
    uploaded on the freeze date itself (UTC) are included", planted as 00:00:00Z on the freeze date, which
    excludes the freeze day.
  - `p55-default`: test-suite-registry spec R2.2, `pythons` "Default `['3.13']`", planted as `['3.12']`.
  - `p55-clean`: plan 55 unchanged. It is the smallest of the three plans, and set against `p55-default` it shows
    what the plant alone changes.
- **DF2. Source versions.** Each copy takes the plan as the owner approved it, before execution, and the spec at the
  same commit, unchanged: plan 53 and its spec at `b8f4d0f`, plan 55 at `f0ebef6`, plan 66 at `526b7de`. Spec
  amendments that a plan's tasks would apply are not applied, since the step sees the spec as it stands at plan
  review.
- **DF3. Each plant reaches a plan test.** The adjudicator compares test sets, so a value that no plan test asserts
  cannot be caught at plan review. Plan 66's `bump --date` default (today, UTC) was rejected as the default plant
  for that reason.
- **DF4. Repetitions.** 5 reps of each arm on each copy. A treatment rep is one reader call and one adjudicator call
  on that reader's reply.
- **DF5. "Per plan".** The false-alarm and unclear bars hold when the mean over a copy's 5 scored reps is at most
  1.0. The record also gives each rep's counts.
- **DF6. The adjudicator in the probe** is a kit prompt run by `claude -p --model opus`, not an `agents/` file. The
  agent file is build-plan work.
- **DF7. Kit tests as `selftest` subcommands,** as plan 73's `measure.py selftest` did, so `run_suites.py --check`
  needs no new suite.
- **DF8. A cost stop.** Each `claude -p` call caps at `--max-budget-usd 4.00`. After the pilot (Task 2), if the
  projected cost of Task 3 is above $150, stop and ask the owner before Task 3.
- **DF9. Codex runs directly** through `codex exec` from `run_codex.sh`, not through `claude -p`, so the
  `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` setting in the spec's Codex model note is not needed.
- **DF10. Hand classification.** The executor classifies each scored ruling that is neither a catch nor "unclear":
  `false-alarm` (it rules against an assertion that agrees with the spec), `real` (the assertion it rules against
  does contradict the spec, an error in the approved plan, quoted), or `interface` (a test-wrong ruling on a name,
  path or type, per the Interfaces block). `real` and `interface` rulings are reported, but not counted as false
  alarms.
- **DF11. The control is told what it is.** Its prompt says that it wrote the plan and now runs Self-Review, with
  no hint that a plant exists.

## Files

All new, under `specs/red-baseline-acceptance-tests/` (written `RB/` below):

| Path | Responsibility |
|---|---|
| `RB/kit/plants.py` | The four copies: source commit, paths, and each plant's replacements, true patterns and keep lines |
| `RB/kit/extract.py` | Splits a plan into tasks, fence-aware. Builds the reader inputs and each task's plan tests |
| `RB/kit/make_copies.py` | `build` writes the copies, `selftest` checks the plants and the reader inputs |
| `RB/kit/prompts/control.txt`, `reader.txt`, `adjudicator.txt` | The three instruction texts |
| `RB/kit/build_prompts.py` | Fills the prompts from a copy (and, for the adjudicator, a reader reply) |
| `RB/kit/run_reps.sh` | Plan 73's runner, adapted: a prompt file, or a directory of per-rep prompts |
| `RB/kit/run_codex.sh` | The Codex reader runner |
| `RB/kit/measure.py` | `score`, `table` and `selftest` |
| `RB/copies/<copy>/{spec.md,plan.md,SITES.txt}`, `RB/copies/MANIFEST.txt` | The built copies |
| `RB/runs/<arm>/<copy>/` | Prompts, rep replies, `SCORE.txt`, `CLASSIFY.txt` |
| `specs/red-baseline-acceptance-tests.md` | The record |

Arms: `control-opus`, `reader-opus` and `adjudicator-opus` (the Claude arm), `codex-gpt-6-sol` and
`adjudicator-codex-gpt-6-sol` (the Codex arm), and the same two for `gpt-6.1-sol` only when Task 4 Step 6 calls for
them.

---

### Task 1: Plant the copies

**Files:**
- Create: `RB/kit/plants.py`, `RB/kit/extract.py`, `RB/kit/make_copies.py`
- Create (built): `RB/copies/{p53-unit,p66-bound,p55-default,p55-clean}/{spec.md,plan.md,SITES.txt}`,
  `RB/copies/MANIFEST.txt`

**Interfaces:**
- Consumes: nothing.
- Produces, in `plants.py`:
  - `@dataclass(frozen=True) class Plant(kind: str, spec_key: str, planted_tokens: tuple[str, ...], replacements: tuple[tuple[str, str, int], ...], true_patterns: tuple[str, ...], keep: tuple[tuple[str, str], ...])`.
    `kind` is `'bound'`, `'unit'` or `'default'`. A replacement is `(old, new, count)`: `old` occurs exactly `count`
    times in the source plan. A keep entry is `(line_text, reason)`: a line that matches a true pattern but states
    another value.
  - `@dataclass(frozen=True) class Copy(id: str, commit: str, spec_path: str, plan_path: str, plant: Plant | None)`.
  - `COPIES: tuple[Copy, ...]`, in the order `p53-unit`, `p66-bound`, `p55-default`, `p55-clean`.
- Produces, in `make_copies.py`: `@dataclass(frozen=True) class Site(line: int, section: str, text: str)`;
  `plant(source: str, plant: Plant) -> tuple[str, list[Site]]`; `true_hits(planted: str, plant: Plant) -> list[str]`,
  the lines that match a true pattern and are not keep lines.
- Produces, in `extract.py`:
  - `@dataclass(frozen=True) class Task(number: int, title: str, files: str, interfaces: str, body: str)`.
  - `split_tasks(plan: str) -> list[Task]`, `tech_stack(plan: str) -> str`, `reader_inputs(plan: str) -> str`,
    `plan_tests(task: Task) -> str`, `section_of(plan: str, line: int) -> str`.
- Produces: the four copies, and `MANIFEST.txt` with one line per file: `<sha256>  <path>  <commit>:<source path>`.

- [ ] **Step 1: Write the selftests**

In `extract.py`, `selftest` builds a small inline plan with a `## ` heading and a `def test_` inside a code fence in
an Interfaces block, and asserts:

```python
tasks = split_tasks(SAMPLE)
assert [t.number for t in tasks] == [1, 2]            # a fenced '### Task' line splits nothing
assert 'def test_' not in reader_inputs(SAMPLE)
assert 'def test_inside' in plan_tests(tasks[0])
assert section_of(SAMPLE, GC_LINE) == 'global-constraints'
assert section_of(SAMPLE, IFACE_LINE) == 'interfaces'
assert section_of(SAMPLE, TEST_LINE) == 'test-step'   # a fenced block that holds 'def test_'
assert section_of(SAMPLE, CODE_LINE) == 'code-step'   # any other block inside a task step
```

`reader_inputs` returns the Tech Stack line, then for each task its `### Task N:` title, its `**Files:**` list and
its `**Interfaces:**` block, and nothing else. `plan_tests` returns the task's fenced blocks that contain `def test_`
or `@pytest`, in order.

In `make_copies.py`, `selftest` builds every copy in memory from `git show <commit>:<path>` and asserts, for each:

```python
assert source.count(old) == count                     # each replacement, before it applies
assert true_hits(planted, plant) == []                # true-pattern lines left, minus the keep lines
assert any(site.section == 'test-step' for site in sites)   # DF3
assert planted == source                              # p55-clean only
for leak in ('def test_', '- [ ] **Step', '## Global Constraints', '## Review Focus', '## Decisions'):
    assert leak not in reader_inputs(planted)         # all four copies
```

It prints each plant's sites, one line each: `<line>  <section>  <new text, first 80 characters>`.

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run python specs/red-baseline-acceptance-tests/kit/extract.py selftest` and the same with `make_copies.py`.
Expected: FAIL (`NameError` or `ImportError`): nothing is defined yet.

- [ ] **Step 3: Implement `extract.py`**

A line-by-line scan that tracks code fences (```` ``` ```` and `~~~`, any length of three or more). Headings and
`**Files:**` or `**Interfaces:**` markers inside a fence are text.

- [ ] **Step 4: Write the plants in `plants.py`**

For each plant, find every place where the copy's plan states the value, with `grep -n` on the source plan, and write
one replacement for each form. The planted copy must read as a planner who misread the spec would write it: values,
test names and assertions, messages, comments and docstrings change together, and so do the expected values derived
from them. The true value and its forms:

| Copy | Spec sentence (the `spec_key`) | True forms to replace | Planted value |
|---|---|---|---|
| `p53-unit` | `a string of 1–500 characters after stripping` | `500 characters`, `1-500 characters`, `1–500 characters`, `1 to COMPATIBILITY_CAP characters`, `{COMPATIBILITY_CAP} characters`, `len(compat.strip())` | 500 UTF-8 bytes: `len(compat.strip().encode('utf-8'))`, messages say `bytes`, the test is `test_compatibility_must_be_a_string_of_1_to_500_bytes` |
| `p66-bound` | `00:00:00Z on the day after the freeze date` | `day after the freeze date`, `day after freeze`, `freeze day itself is included`, `timedelta(days=1)` in `cutoff`, `2026-10-20T00:00:00Z`, `2027-01-01T00:00:00Z`, and each expected date in a test that a cutoff decides | 00:00:00Z on the freeze date (the freeze day excluded): `cutoff == '2026-10-19T00:00:00Z'`, the test is `test_cutoff_is_midnight_utc_on_the_freeze_date` |
| `p55-default` | `` Default `['3.13']` `` | `DEFAULT_PYTHONS = ('3.13',)`, `(default ['3.13'])`, and each expected `--python 3.13` or `(3.13)` for a fixture suite with no `pythons` key | `('3.12',)`, `['3.12']`, and `3.12` in those expected values |

`planted_tokens` holds the planted forms that a ruling would quote from the plan (for example `bytes`,
`2026-10-19T00:00:00Z`, `3.12`). A form that states another value goes in `keep` with its reason, for example
plan 53's `Keep under 500 characters if possible` (upstream skill-creator text, not R1.3), plan 55's runner command
`uv run --python 3.13 python build/run_suites.py` (R3.1's interpreter, not the default), or plan 55's explicit
`pythons = ['3.13', '/usr/bin/python3']`.

- [ ] **Step 5: Implement `make_copies.py build`**

It writes the files listed under this task and refuses to overwrite a differing file. `SITES.txt` holds the site
lines that `selftest` prints.

- [ ] **Step 6: Run the selftests and build**

Run: `uv run python specs/red-baseline-acceptance-tests/kit/extract.py selftest`, then `make_copies.py selftest`,
then `make_copies.py build`.
Expected: `extract selftest ok`, `make_copies selftest ok` with the site lines, then four copy directories and
`MANIFEST.txt`. Read each `SITES.txt`: each planted copy has sites in the Global Constraints when the approved plan
states the value there, in the Interfaces blocks when it states it there, and in at least one test step and one code
step.

- [ ] **Step 7: Commit**

```bash
git add specs/red-baseline-acceptance-tests/kit/plants.py specs/red-baseline-acceptance-tests/kit/extract.py \
  specs/red-baseline-acceptance-tests/kit/make_copies.py specs/red-baseline-acceptance-tests/copies
git commit -m "test(specs): plant three misreads in copies of plans 53, 55 and 66 (plan 81 task 1)"
```

### Task 2: Prompts, runners, scorer and pilot

**Files:**
- Create: `RB/kit/prompts/control.txt`, `RB/kit/prompts/reader.txt`, `RB/kit/prompts/adjudicator.txt`,
  `RB/kit/build_prompts.py`, `RB/kit/run_reps.sh`, `RB/kit/run_codex.sh`, `RB/kit/measure.py`
- Create (pilot): `RB/runs/pilot/`

**Interfaces:**
- Consumes: `extract.split_tasks`, `extract.tech_stack`, `extract.reader_inputs`, `extract.plan_tests`,
  `plants.COPIES`.
- Produces:
  - `uv run python RB/kit/build_prompts.py control <copy> <out-file>`, `reader <copy> <out-file>`,
    `adjudicator <copy> <reader-reply-file> <out-file>`. `control` reads `skills/writing-plans/SKILL.md` with
    `git show origin/main:` and writes the sha into the prompt's first comment line and into
    `RB/runs/<arm>/<copy>/SOURCES.txt`.
  - `bash RB/kit/run_reps.sh <prompt-file|prompt-dir> <out-dir> <first> <last> <model> [<budget>]`. With a
    directory, rep `i` reads `<prompt-dir>/rep<i>.txt`.
  - `bash RB/kit/run_codex.sh <prompt-file> <out-dir> <first> <last> <model>`, writing `rep<i>.md` (the last
    message) and `rep<i>.log`.
  - `uv run python RB/kit/measure.py score <run-dir> <copy>` (writes `SCORE.txt`), `table <runs-dir>`, `selftest`.
  - `reply(path: Path) -> str | None`: the `result` text of a `claude -p` JSON, the text of a Codex `.md`, or `None`
    for a VOID rep.
  - `@dataclass class Score(void: bool, catch: bool, near: list[int], unclear: int, to_classify: list[int])`, the
    list items being 1-based ruling or finding numbers; `score_reply(text: str | None, plant: Plant | None) -> Score`
    (with `plant=None`, `catch` is `False` and every non-unclear ruling is to classify);
    `codex_model(log: str) -> str | None`; `score_codex(log: str, model: str) -> Score`, VOID when the models differ.
- Produces, the reply formats:
  - Reader: one `<tests>` block of pytest code, where each test has the comments `# spec: "<sentence>"` and
    `# task: <N>`; one `<flags>` block of `<flag task="N"><spec>…</spec><plan>…</plan></flag>`; one `<untestable>`
    block, one spec sentence per line.
  - Adjudicator: one `<rulings>` block of
    `<ruling task="N" verdict="plan-wrong|test-wrong|unclear"><quote>…</quote><plan>…</plan><acceptance>…</acceptance></ruling>`,
    or `<rulings></rulings>` when no case conflicts.
  - Control: one `<findings>` block of `<finding task="N"><quote>…</quote><plan>…</plan><fix>…</fix></finding>`.

- [ ] **Step 1: Write `measure.py selftest`**

Inline fixture replies, scored against `p66-bound`'s plant:

```python
assert score_reply(CATCH, plant).catch is True        # plan-wrong, spec_key quoted, planted token in <plan>
assert score_reply(PARAPHRASE, plant).catch is False
assert score_reply(PARAPHRASE, plant).near == [1]     # listed for the executor, never a silent miss
assert score_reply(UNCLEAR_TWO, plant).unclear == 2
assert score_reply(OTHER_PLAN_WRONG, plant).to_classify == [1]
assert score_reply(None, plant).void is True          # budget cap or no reply block
assert score_reply(NO_BLOCK, plant).void is True
assert codex_model(LOG_ASTRA) == 'gpt-6-astra'        # read from the log header's `model:` line
assert score_codex(LOG_ASTRA, 'gpt-6-sol').void is True
assert score_reply(OTHER_PLAN_WRONG, None).to_classify == [1]   # p55-clean
```

Matching lowercases, maps en and em dashes to `-`, strips backticks and quotes, and collapses whitespace. A catch
needs `verdict="plan-wrong"`, the `spec_key` inside `<quote>`, and a planted token inside `<plan>`. For a control
reply, a catch is a finding with the `spec_key` inside `<quote>` and a planted token inside `<plan>`. A near catch
names a planted token but fails another part. `table` counts a rep's false alarms from `CLASSIFY.txt` (DF10), whose
lines read `rep<i> ruling<j> <false-alarm|real|interface> <reason>`, and refuses a run directory with an
unclassified ruling.

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run python specs/red-baseline-acceptance-tests/kit/measure.py selftest`
Expected: FAIL: nothing is defined yet.

- [ ] **Step 3: Implement `measure.py`**

- [ ] **Step 4: Run it to verify it passes**

Run: the same command. Expected: `measure selftest ok`.

- [ ] **Step 5: Write the prompts and `build_prompts.py`**

- `control.txt`: writing-plans' `SKILL.md` body, then "You wrote the plan below from the spec below. Run your
  Self-Review now", the spec, the whole copy, and the `<findings>` format (DF11). No hint of a plant.
- `reader.txt`: the spec's Design 2 rules from Global Constraints (Reader inputs, Reader isolation, Reader output),
  "Do not search for a plan file or any other file", the spec, the reader inputs and the reply format. It names no
  path.
- `adjudicator.txt`: the Adjudicator rule from Global Constraints, the binding-text rule for names, paths and types,
  then the spec, and for each task its Interfaces block, the plan's tests (`plan_tests`) and the reader's tests and
  flags for that task. It names no path.

`build_prompts.py` refuses to write a reader or adjudicator prompt that contains `def test_` from outside the
reader reply and `plan_tests`, or the copy's path.

- [ ] **Step 6: Adapt the runners**

`run_reps.sh` is plan 73's script with `/tmp/plan81-rep-XXXXXX` directories and the prompt-directory form.
`run_codex.sh` runs each rep from a fresh empty `/tmp/plan81-codex-XXXXXX` directory, with the prompt on stdin:
`codex exec -m <model> -c sandbox_mode=read-only --skip-git-repo-check -C <rep-dir> -o <out>/rep<i>.md - < <prompt> > <out>/rep<i>.log 2>&1`.
Both refuse an existing `rep<i>` file and a run directory inside a git repository.

- [ ] **Step 7: Check isolation**

Run: `bash RB/kit/run_reps.sh specs/red-baseline-reviewer-planning-contract/kit/isolation_probe.txt RB/runs/pilot/isolation 1 1 opus`
Expected: all five lines of the reply read `NO`. Any `YES` stops the task: report it.

- [ ] **Step 8: Pilot one rep of each Claude arm on `p55-default`**

Build the prompts, then run rep 1 of `control-opus`, `reader-opus` and, on that reader reply, `adjudicator-opus`,
under `RB/runs/pilot/`. Score each with `measure.py score`.
Expected: three non-VOID reps that parse. Record each rep's `total_cost_usd`. Project Task 3's cost as
20 control reps plus 20 reader and 20 adjudicator reps, scaled by each copy's prompt size. Above $150, stop and ask
the owner (DF8).

- [ ] **Step 9: Commit**

```bash
git add specs/red-baseline-acceptance-tests/kit specs/red-baseline-acceptance-tests/runs/pilot
git commit -m "test(specs): add the probe's prompts, runners and scorer, and pilot them (plan 81 task 2)"
```

### Task 3: The control and the Claude arm

**Files:**
- Create: `RB/runs/{control-opus,reader-opus,adjudicator-opus}/<copy>/` for the four copies

**Interfaces:**
- Consumes: everything Task 2 produces.
- Produces: for each arm and copy, 5 scored reps with `SCORE.txt` and `CLASSIFY.txt`.

- [ ] **Step 1: Run the control arm**

For each copy, build the control prompt and run reps 1–5 on `opus`. Rerun each VOID rep under a new rep number until
5 reps score.

- [ ] **Step 2: Run the Claude reader**

For each copy, build the reader prompt and run reps 1–5 on `opus`, VOID reps rerun as in Step 1.

- [ ] **Step 3: Run the adjudicator on each reader reply**

For each copy, build `adjudicator-opus/<copy>/prompts/rep<i>.txt` from reader rep `i`, and run reps 1–5 on `opus`
with the prompt-directory form. A VOID adjudicator rep reruns on the same reader reply.

- [ ] **Step 4: Score and classify**

Run `measure.py score` on each run directory. Write `CLASSIFY.txt` for each ruling or finding that `SCORE.txt` lists
to classify (DF10), and judge each near catch: a ruling counts as a catch only when its quote is the spec sentence
that holds the `spec_key`. Record each judgment's reason. Then run `measure.py table RB/runs`.
Expected: a table with, for each arm and copy, the catches out of 5, the false alarms per rep and the unclear cases
per rep. Every cell is filled.

- [ ] **Step 5: Commit**

```bash
git add specs/red-baseline-acceptance-tests/runs
git commit -m "test(specs): run the control and the Claude arm of the acceptance-tests probe (plan 81 task 3)"
```

### Task 4: The Codex arm (on the owner's machine)

This task runs in a session on the computer where the owner's `codex` CLI is logged in, not in a cloud session.
The cloud executor pushes Task 3, then hands this task over with the branch name and stops.

**Files:**
- Create: `RB/runs/{codex-gpt-6-sol,adjudicator-codex-gpt-6-sol}/<copy>/`, and the `gpt-6.1-sol` pair only after
  Step 6

**Interfaces:**
- Consumes: the reader prompts and the kit from Task 2.
- Produces: for each copy, 5 scored Codex-arm reps with the model of each Codex run recorded.

- [ ] **Step 1: Ask the owner**

Ask once: "The Codex arm sends the probe's specs and reader inputs to OpenAI. Approve the Codex runs for this
session?" Without a yes, skip this task. The record then says the Codex arm did not run, and why.

- [ ] **Step 2: Check the CLI**

Run: `codex --version` and `codex exec --help`.
Expected: a version line, and help that lists `-m`, `-c`, `--skip-git-repo-check`, `-C` and `-o`. A missing flag
stops the task: report it.

- [ ] **Step 3: Run the Codex reader on `gpt-6-sol`**

For each copy, run reps 1–5 of the copy's reader prompt with `run_codex.sh` and the model `gpt-6-sol`.
Expected: each `rep<i>.log` header reads `model: gpt-6-sol`. A rep on any other model is VOID and reruns.

- [ ] **Step 4: Adjudicate**

As Task 3 Step 3, from the Codex replies, into `adjudicator-codex-gpt-6-sol/<copy>/`, on `opus`.

- [ ] **Step 5: Score and classify**

As Task 3 Step 4.

- [ ] **Step 6: Run `gpt-6.1-sol` only on a miss**

If `gpt-6-sol`'s arm misses a bar, repeat Steps 3–5 with `gpt-6.1-sol`. Otherwise skip this step, and the record
says so.

- [ ] **Step 7: Commit and push**

```bash
git add specs/red-baseline-acceptance-tests/runs
git commit -m "test(specs): run the Codex arm of the acceptance-tests probe (plan 81 task 4)"
git push -u origin <execution branch>
```

### Task 5: The record and the owner's review

**Files:**
- Create: `specs/red-baseline-acceptance-tests.md`
- Modify: `specs/spec-derived-acceptance-tests.md` (one link line under Verification, "Probe first")
- Modify: `specs/deferred_items.md` (a progress note under the item in section `spec-reading-test-check`)

**Interfaces:**
- Consumes: `measure.py table RB/runs`, every `CLASSIFY.txt`, `MANIFEST.txt`, and each run's `SOURCES.txt`.

- [ ] **Step 1: Write the record**

The record gives, in this order: the date and the shas used (the copies' source commits, writing-plans at
`origin/main`, Claude Code and codex-cli versions, and the Codex models from the log headers); the plants, with each
site count from `SITES.txt`; the table from `measure.py table`; each bar from Global Constraints with its result
(met, missed, or not run), using DF5's per-plan rule; the comparison of the Codex arm with the Claude arm on catches
and false alarms; every `real` ruling with its spec quote; the cost; and what the probe cannot show (the spec's
"What a second reading can and cannot catch"). It recommends nothing about the build plan. The owner decides (D8).

- [ ] **Step 2: Link it and note the backlog**

Under the spec's Verification, "Probe first", add one line: "Results: `specs/red-baseline-acceptance-tests.md`
(plan 81, <date>)." Under the backlog item "Spec-reading test check", add a line in its existing `Progress (…)` form
that names plan 81 and the record's path. Leave the item open.

- [ ] **Step 3: Check and commit**

Run: `bash build/run_commit_lints.sh`. Expected: `commit lints passed`.

```bash
git add specs/red-baseline-acceptance-tests.md specs/spec-derived-acceptance-tests.md specs/deferred_items.md
git commit -m "docs(specs): record the acceptance-tests probe results (plan 81 task 5)"
```

- [ ] **Step 4: Owner gate (D8)**

Present the record's table and bar results to the owner, and stop. The owner reviews them and decides what the
build plan keeps. Do not write the build plan.
