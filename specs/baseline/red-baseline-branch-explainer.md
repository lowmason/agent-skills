# Plan 94 baseline probe: the branch explainer

Status: in progress

This record holds the baseline probe for plan 94 (`specs/plans/94-branch-explainer.md`) and its spec
(`specs/branch-explainer.md`). The probe asks one question. Does an Opus agent with no guidance already write a
branch explainer that meets the owner's bar? A writer rep writes an explainer of one merged plan branch. A tool-less
reader writes a three-part synopsis from that explainer only. A tool-less adjudicator scores bars B1 to B4, and the
kit counts words for B5. The rules below were fixed before any live run.

EXEC_BASE: 201d2d42e6112d7add38aa58cc15eb15145c0b1d

- EXEC_BASE is `origin/main` at the start of execution (2026-11-14), after plan 97's merge (#206). Finishing's body
  measures 19,009 characters there, as the plan expects.
- `git cat-file -e HEAD:specs/plans/94-branch-explainer.md` exits 0.
- `claude --version`: `2.1.323 (Claude Code)`. The kit finds it on `PATH` at `~/.local/bin/claude`.
- The executor runs inline under executing-plans, on `claude-opus-5-5`.

## Fixtures

Each fixture is an isolated repository, never a worktree (owner decision D3). The kit runs `git init`, fetches only
the head's full sha, sets `main` to `BASE`, detaches `HEAD` at the head and deletes `.git/FETCH_HEAD`. It then checks
that `git rev-list --count main..HEAD` equals the commit count and that `git for-each-ref` prints only
`refs/heads/main`. On 2026-11-14 all four fixtures built and passed both checks. No text file under a fixture's
`.git`, objects aside, names this repository's path.

| Name | Plan | Head | `BASE` | Branch | Commits | Role |
|---|---|---|---|---|---|---|
| `p80` | `80-development-history-record` | `325330a` | `4d69454` | `claude/plan-80-execution-636c1e` | 21 | tuning |
| `p90` | `90-readonly-guard-command-starts` | `d51bf64` | `84efc99` | `claude/quirky-golick-44b138` | 24 | tuning |
| `p92` | `92-writing-skills-guide-rewrite` | `0b6d34f` | `e382493` | `claude/compassionate-jennings-98ff45` | 15 | tuning |
| `p84` | `84-spec-derived-acceptance-tests` | `4cae5b2` | `650e13c` | `claude/musing-dhawan-59a2d0` | 16 | held out |

`kit/kit.py` holds the full shas.

**Why `p84` is the held-out fixture (plan, C1).** It must have a spec, a plan and a history entry, and be of a kind
other than the three tuning fixtures. Those are a script plus skill text (80), hook code plus tests (90), and mostly
skill text (92). Plans 82, 86, 87, 88, 89 and 91 have `Spec: none`. Plans 81 and 83 are probe-only branches whose
diffs are 297,000 and 2,230,000 inserted lines of probe records. Plan 85 changes only derive-roadmap's skill text,
which is fixture 92's kind. Plan 84 alone changes one contract across surfaces: an agent definition, its generated
Codex and Gemini adapters, SDD prompt templates and references, and a new bash helper with tests. Until Task 6,
nobody who writes or tunes the brief opens plan 84's plan, spec, history entry or range.

## Kit

All files are in `specs/baseline/red-baseline-branch-explainer/kit/`.

| File | What it is |
|---|---|
| `kit.py` | Fixtures, prompts, word counts, the rep audit and the scores. `selftest` checks it. |
| `run_writer.sh` | Writer reps, one fixture repository each. |
| `run_judges.sh` | The reader, then the adjudicator, for each writer rep. |
| `run_plain.sh` | Tool-less reps: the reader, the adjudicator and the micro-test. |
| `isolation_probe_tools.txt` | The isolation probe prompt for a writer with tools. |
| `brief-r<k>.md` | The writer brief for wording round `k` (Task 3). |

Changes from the copied sources:

- `run_plain.sh` is plan 91's `specs/baseline/red-baseline-causal-design-heldout/kit/run_reps.sh`. It changes the
  temp prefix to `/tmp/plan94-plain-`, the comments and usage lines to name plan 94 and `run_plain.sh`, and adds
  `--disable-slash-commands`.
- `isolation_probe_tools.txt` is plan 73's `specs/baseline/red-baseline-reviewer-planning-contract/f1/isolation_probe_tools.txt`.
  It says "eight" for "seven" and adds line 8:
  ``8. Run `git for-each-ref --format='%(refname)'` with your Bash tool and quote its whole output.``
- `kit.py`'s `audit_hits` widens the idea of plan 73's `FORBIDDEN_RE` and `CD_HOME_RE` in `score_f1.py`. Plan 73's
  regexes list named folders under the home folder. This audit instead lists every absolute path outside the rep
  folder, every `~`, `$HOME` or `${HOME}` path, and every `..` path component.

Executor rulings that shape the kit (each is in the execution ledger):

- `result.json` adds two fields to the plan's list (C8): `result`, the writer's final reply, and `model_usage`, the
  keys of the result record's `modelUsage`. Task 2 must record the probe's answers and the write check's reply.
- `audit_hits` reads the models from the init record and from each assistant record's `message.model`.
- `run_writer.sh` makes `<rep>/out` for every arm, the write check included. The write check then tests a refused
  write, not a missing folder.
- The synopsis heading match skips lines inside code fences, so a `# comment` in a code block is never a heading.
- `audit_hits` does not scan the `content` of a `Write` call. That is text the writer writes, not a path it reads or
  runs.
- The isolation probe and the write check are diagnostic. Their expected void reasons cause no rerun.

## Prompts

`{…}` fields are filled per rep. In the probe, `{brief}` is `<rep>/brief/branch-explainer-prompt.md`, `{repo}` is
`<rep>/repo`, `{output}` and `{path}` are `<rep>/out/explainer.md`, and `{plan_branch}` is `yes`. `{base}` and
`{head}` are full shas. A check against the plan's text blocks found all six constants identical, byte for byte.

`CONTROL_REQUEST`:

```text
Explain the change in `{base}..HEAD` of this repository to me, its owner, before I merge it. Write it to `{path}`.
```

`DISPATCH` (the treatment, and later Step 3b's real dispatch):

```text
Read {brief} and follow it to write a branch explainer.
BASE: {base}
HEAD: {head}
Branch: {branch}
Repository: {repo}
Plan branch: {plan_branch}
Output: {output}
```

`READER`. In the treatment arm the kit removes the explainer's `## Synopsis` section first (owner decision 6):

```text
Below is a document that explains one branch of a code repository to the repository's owner. Read it. Then, from what the document says, write a synopsis of the branch in your own words: three labeled parts, at most 250 words in all.

The plan: what the work set out to do, and why.
The build: how it was built: the main parts, in the order they depend on each other.
The project: what the branch adds to the project as a whole.

Reply with the three parts only.

<document>
{explainer}
</document>
```

`ADJUDICATOR`. Its diff leaves out `specs/baseline/**`, `specs/red-baseline-*/**`, and the plan and spec files at
their `specs/` and `completed/` paths. The full `git diff --stat=200` lists every file (C5):

```text
You score one explainer of a code branch, and a synopsis that a reader wrote after reading only that explainer. You have no tools. Everything you need is below.

<spec>
{spec}
</spec>
<plan>
{plan}
</plan>
<history_entry>
{entry}
</history_entry>
<diff_stat>
{stat}
</diff_stat>
<diff note="Probe records under specs/baseline/ and specs/red-baseline-*/, and the plan and spec files, are left out of this diff. diff_stat lists every changed file.">
{diff}
</diff>
<explainer>
{explainer}
</explainer>
<synopsis>
{synopsis}
</synopsis>

Score four bars. A bar passes only when every part of it holds.

B1 Plan. The synopsis's first part states the plan's goal and the reason for it, and both agree with the spec.
B2 Build. The synopsis's second part names the main parts of the build in an order that fits their dependencies: no part comes before a part it needs. It also states at least two facts that come from the diff and that the spec does not state, such as a file, a function, a command, a check, a count or a behavior.
B3 Project. The synopsis's third part names at least one way the branch changes the project beyond the files it touches: a part of the project that now depends on the branch, or a step of a workflow that now runs differently. A list of changed files does not count.
B4 Accuracy. The explainer, every section of it, makes no claim about what the branch's code or text does that the diff contradicts. A claim that the diff does not cover is not a contradiction.{b4_extra}

Reply in exactly this form, and nothing else:
B1: PASS or FAIL
Why: <one or two sentences that quote the synopsis>
B2: PASS or FAIL
Why: <the order you checked, and the two diff facts, each with the file it comes from>
B3: PASS or FAIL
Why: <one or two sentences that quote the synopsis>
B4: PASS or FAIL
Contradicted: none, or one line per claim: "<quoted claim>" against <file>: <what the diff shows>
```

`{b4_extra}` is empty for the control. For the treatment it is `TREATMENT_B4`:

```text
 The explainer's own Synopsis section counts too: each of its three parts must agree with the spec and the diff, and a part that does not is a claim for the list.
```

`WRITE_CHECK`, the write check's prompt:

```text
Write the single word ok to the file {path}. Then reply DONE, or reply REFUSED with the reason if the write was refused.
```

## Rules

**B5 and the words (C7).** A word is a whitespace-separated token with at least one letter or digit, code blocks
included. B5 holds when the explainer has at most 2,000 words and its synopsis at most 250. The treatment's synopsis is
its `## Synopsis` section, and a treatment explainer with no such section fails B5. A control's synopsis is its first
section headed "Synopsis", "Summary" or "TL;DR". A control with no such section is judged on the 2,000-word limit only.
This tilts B5 toward the control, the safe direction.

**Pass rules (spec, exact).** A bar holds on a fixture when it holds in at least 2 of 3 scored reps.

- **RED:** the control fails at least one bar on at least one fixture.
- **Shrink:** the control holds every bar on every fixture.
- **Treatment passes:** every bar holds on `p80`, `p90` and `p92`, and then on `p84`.

`kit.py score` also prints how many scored reps passed all five bars at once. That count is no bar.

**VOID.** A writer rep is VOID when its `audit.json` lists a void reason, or when a file `rep<N>.VOID` holds the
executor's reason. The automatic void reasons: a result that is not `success`, a tool outside the writer's list, a
model other than `claude-opus-5-5`, or no explainer file. The executor reads every `outside` hit by hand. A rep that
read or ran anything outside `<rep>`, system tools aside, gets a `.VOID` file. VOID reps are rerun under the next free
rep number. A fixture's scored reps are its first 3 reps that are not VOID. Two budget-stop VOIDs on one fixture stop
the run until the owner answers.

**Wording rounds (spec).** At most two follow a failed treatment run. Before a round runs, this record states its
estimated cost from the measured mean costs: `9 × (mean_writer + mean_reader + mean_adjudicator)`. A treatment that
fails after round 2 stops the work, and the results go to the owner. `p84` runs once, after the last round. If it
fails, the work stops and the results go to the owner. No round tunes against it.

**Contested readings.** The executor reads every adjudication in full against its bar text. A reading the executor
disputes is marked contested here, with both readings. It goes to the owner only when it would flip a bar's result on
a fixture.

## Run commands

The writer (`run_writer.sh`), run from `<rep>/repo`. The treatment adds `--add-dir <rep>/brief`, and the write check
drops `--add-dir <rep>/out`:

```bash
env -i <HOME USER LOGNAME PATH SHELL TMPDIR LANG, each only when set> \
  CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
  "$CLAUDE_BIN" -p --model claude-opus-5-5 --tools "Bash,Read,Write,Grep,Glob" \
  --permission-mode acceptEdits --allowedTools Bash --permission-prompts none \
  --add-dir "<rep>/out" --strict-mcp-config --setting-sources "" --disable-slash-commands \
  --no-session-persistence --output-format stream-json --verbose --max-budget-usd "<cap>"
```

The reader, the adjudicator and the micro-test (`run_plain.sh`), each from a new, empty folder under `/tmp`, outside
every repository:

```bash
env -i <the same variables> CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
  "$CLAUDE_BIN" -p --model "<model>" --tools "" --strict-mcp-config --setting-sources "" \
  --disable-slash-commands --no-session-persistence --output-format json --max-budget-usd "<budget>"
```

The reader's cap is $0.50. The adjudicator's cap is `ADJ_CAP`, set from the cost pilot.

**Public repository.** Only explainers of this repository's public branches are committed. Full writer streams stay
in `~/.cache/agent-skills/scratch/plan94/streams/`, and each rep's `result.json` records the stream's sha256. Before
each commit of rep outputs, a grep for email addresses and key shapes runs over the new folders.

## Cost

The basis: plan 73's tool-using Opus sessions cost $0.35 to $1.96. An adjudicator prompt is 200 to 260 KB, about
50,000 to 65,000 tokens, and the table counts every adjudicator as uncached.

| Item | Runs | Each (estimate) | Total |
|---|---|---|---|
| Pilots: isolation probe, write check, cost pilot (writer, reader, adjudicator) | 5 | — | about $4 |
| Control arm: writer, reader, adjudicator | 9 each | $1.50, $0.05, $0.40 | about $18 |
| Treatment round 0 | 9 each | $1.75, $0.05, $0.40 | about $20 |
| Each wording round | 9 each | the same | about $20 |
| Held-out (`p84`) | 3 each | the same | about $7 |
| Micro-test (Sonnet, decision-only) | about 40 | $0.08 | about $3 |
| VOID reruns | — | — | about $5 |

Expected: about $57 with no wording round, and about $97 with both. The run stops for the owner when pilots and control
together pass $35, or when spend plus the next step's estimate would pass $120. The owner confirms the spend before the
first `claude -p` call. The cost pilot then replaces the estimate.

## Known limits

- One model writes, reads and adjudicates: `claude-opus-5-5`.
- Each arm has 3 scored reps per fixture.
- The reader is a model, not the owner.
- The adjudicator has no tools. It sees no code outside the diff.
- No fixture tests `Plan branch: no` or `Spec: none`.
- The `p90` and `p92` fixture heads hold `specs/history.md` with plan 84's entry, because both merged after plan 84.
  A writer that reads earlier history entries as part of the project map can read it. If an explainer quotes plan 84,
  this record names it as an exposure of the held-out fixture.

## Pilots

## Control

## Treatment

## Held-out

## Micro-test

## Spend

## Verdict
