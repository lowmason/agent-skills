# Plan 94 baseline probe: the branch explainer

Status: complete

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

**Spend confirmation (Task 2 Step 1, 2026-11-14).** The executor asked: "Plan 94's probe is ready. The plan
estimates about $57 for the live runs, or about $97 with both wording rounds. It stops to ask at $35 for pilots and
control, and at $120 in all. Do you confirm the spend?" The owner answered: "Yes, confirm". In the same question set,
the owner kept inline execution on Opus: "Keep inline on Opus (Recommended)".

**Isolation probe** (`pilot/probe/`, fixture `p90`, $0.03). The writer flags with the probe prompt.

- Lines 1 to 6 read NO. Line 1 shows that no `CLAUDE.md` loads, the fixture's own included.
- Line 7 reads NO. The `Read` of `~/Projects/agent-skills/README.md` was denied automatically and appears in
  `permission_denials`. A read outside the rep's folders is refused under `--permission-prompts none`.
- Line 8 quotes only `refs/heads/main`.
- The init record lists exactly `Bash`, `Glob`, `Grep`, `Read` and `Write`. The model is `claude-opus-5-5`, and
  `modelUsage` names only that model.
- The audit's `no explainer file` and its one `outside` hit (the line 7 read) are expected for this prompt.

**Write check** (`pilot/permcheck/`, fixture `p90`, $0.03). The writer flags without `--add-dir <rep>/out`.

- The reply: "REFUSED: I couldn't write `ok` to `<rep>/out/check.txt`. That path is outside the folders this session
  is allowed to use, so the write needed your approval. There's no way to approve it in this session, so it was
  denied automatically and the file wasn't created."
- `permission_denials` holds the `Write`. `<rep>/out/check.txt` does not exist.
- So under `-p`, a write outside the working directory and the added folders is refused (C9). Step 3b's procedure
  must handle a refused write in one line. Task 7's live run shows what happens in the owner's own session.

**Cost pilot** (`pilot/writer/`, fixture `p92`, one unscored control rep, not scored).

| Run | Cost | Notes |
|---|---|---|
| Writer | $0.68 | 14 turns, 1,647 words, no void reason, no `outside` hit |
| Reader | $0.06 | |
| Adjudicator | $0.54 | 63,266 input tokens written to the cache, none read from it; prompt 156,724 bytes |

- The writer cap is twice the pilot writer's cost, rounded up to the next $0.50, with a $3.00 floor: **$3.00**.
- `ADJ_CAP` is twice the pilot adjudicator's cost, rounded up to the next $0.50, with a $1.00 floor: **$1.50**.
- The projection from the pilot for control, round 0 and held-out is 21 × ($0.68 + $0.06 + $0.54) = about $27. That
  is below the $90 stop.
- The pilot control headed its summary "In short", which is not a C7 synopsis name, so B5 would judge it on the
  2,000-word limit only. Its adjudication parsed and gave B1 to B4 PASS.

## Control

Writer cap $3.00, `ADJ_CAP` $1.50. Writer reps 1 to 3 ran on each fixture, and `p90` reps 4 and 5 replaced two VOID
reps. In the final review, `p90` rep4 became VOID, and rep6 replaced it.

**VOIDs.**

- `p90` rep1: the writer ran `ls /tmp/codex-review 2>/dev/null | tail -3` and got three file names from that folder.
- `p90` rep2: the writer listed `/tmp/codex-review/` and ran `cat` on two real Codex review files there.
- The cause: plan 90's text names `/tmp/codex-review/`, the folder where the real Codex reviews of that branch were
  written. `Read` has a path check, which the isolation probe showed. `Bash`, allowed through `--allowedTools Bash`,
  has none. The writer reached the folder through `Bash`.
- `p90` rep4 (made VOID in the final review): the writer ran `ls ~/.local/bin 2>/dev/null | head; which uv pytest
  python3.12 python3.13`. The executor first kept this rep, because the VOID rule exempts system tools. The
  code-reviewer read the rule as an exemption for running a system tool, not for listing a folder in the home folder.
  The executor accepted that reading. `rep4.VOID` records it.

**`outside` hits read and kept.** These hits are not VOID:

- `Read`s of `~/.claude/projects/-private-tmp-plan94-rep-<id>-repo/<session>/tool-results/*.txt`. Claude Code saves a
  long `Bash` output there, so these files hold the rep's own command output.
- `cd ../../..` after a `cd` into the rep's own subfolder.
- Grep patterns that search the fixture's own files, such as `/5`, `/Users/` and the owner's name.

**Scores** (scored reps: `p80` 1 to 3, `p90` 3, 5 and 6, `p92` 1 to 3). Each cell is the count of scored reps that pass.

| Bar | `p80` | `p90` | `p92` |
|---|---|---|---|
| B1 Plan | 3/3 holds | 3/3 holds | 3/3 holds |
| B2 Build | 3/3 holds | 3/3 holds | 2/3 holds |
| B3 Project | 2/3 holds | 3/3 holds | 3/3 holds |
| B4 Accuracy | 1/3 **fails** | 1/3 **fails** | 1/3 **fails** |
| B5 Length | 3/3 holds | 3/3 holds | 3/3 holds |
| All five bars at once | 1/3 | 1/3 | 1/3 |

Explainer lengths run from 1,119 to 1,574 words. Only `p92` rep2 has a section that C7 reads as a synopsis (220
words). The others open with a summary under another heading, such as "In short", so B5 judges them on length only.

**The B4 failures.** The executor checked each contradicted claim against the fixture's files and agrees with every
one:

| Rep | Claim | What the branch shows |
|---|---|---|
| `p80` rep1 | the history entry "lists 8 rulings and 6 deviations" | 8 rulings and 7 deviations |
| `p80` rep3 | the branch "adds about 35 small JSON rep files" | 25 `rep<N>.json` files |
| `p90` rep3 | `hooks/readonly-agent-guard.py` is "+142/−37"; "three 'Not caught' entries are removed" | +123/−19 (142 lines changed); one bullet removed, two rewritten |
| `p90` rep5 | the guard file is "+142/−37 lines in total" | +123/−19 |
| `p92` rep2 | a committed rep reply "begins its reply with your first name" | the reply names the owner once, by surname, about 200 characters in |
| `p92` rep3 | "you waive those case by case", with the waiver limited to edits that change no instruction | a final-review ruling removed "for such edits" so that the waiver has no such limit |

Five of the six are numbers or details that the writer stated without checking them. They are counts, line totals
or a name. The sixth restates wording that a later commit of the same branch removed. The VOID `p90` rep4 had one
more of the first kind: input sizes of "64 and 128 words", where the tests repeat a pattern 64 and 128 times.

**Other FAILs, not contested.** `p80` rep3 B3: the project part describes the new record and names no workflow step
that changes. `p92` rep3 B2: the synopsis puts the register change before the micro-test whose null result it needs.
Neither FAIL changes its bar's result on the fixture.

**Contested readings:** none.

**Held-out exposure check.** No control explainer names plan 84 or its subject.

**Verdict: RED.** The control fails B4 on all three tuning fixtures and holds B1, B2, B3 and B5 on all three. The
treatment brief adds one instruction aimed at B4 (Task 3).

**Spend.** Pilots $1.34, control $11.18 (the two VOID writer reps included), total $12.52. That is below the $35 stop
for pilots and control. The final review's `p90` rep6 added $0.90 (Spend).

**Public repository scan** over `pilot/` and `control/`: the plan's grep for email addresses and key shapes printed no
line. An extra check for the owner's name and home folder found three kinds of text. Each is already public in this
repository: the home folder path in audit paths (already in 233 committed files), the owner's name in grep patterns
(in `LICENSE`), and a quote of the surname line from `p92`'s committed rep file.

## Treatment

### Round 0 brief

`kit/brief-r0.md` (853 words by `wc -w`). It holds the values, the inputs, the diff-versus-spec rule, the layout, the
limits, the style and the output that plan Task 3 lists. The control failed B4 only, so the brief adds one
instruction aimed at that bar:

| Bar the control failed | Instruction in the brief |
|---|---|
| B4 Accuracy | "Check before you state": take each number from a command or a file read in the session, with `git diff --numstat` for one file's lines, and leave out an unchecked number; take names, limits and quoted words from the files at `HEAD`, and describe the later state when a later commit changes an earlier one. |

Two executor choices in the brief, each in the execution ledger:

- **Background carries the plan's gap.** Spec §5 gives Background "the parts of the project that the change touches,
  as they worked before the branch". The brief adds "and the gap that the plan set out to close". The treatment's
  reader never sees the Synopsis, and no other body section of §5 says why the plan exists.
- **Inputs stay in the Repository folder.** The brief says "Read only files inside the Repository folder, and this
  brief." Spec §3 says that the writer sees only the files, as the owner would. Two control reps read outside their
  folder, and each such rep is VOID.

**Round 0 estimate:** 9 × ($0.542 + $0.046 + $0.551) = **$10.24**. The writer mean is over the 12 explainer writer runs
so far (the pilot writer and all 11 control writers, the VOID reps included). The reader and adjudicator means are over
their 10 runs each. The isolation probe and the write check are not explainer runs, so they are not in the means.

### Round 0 results

Writer cap $3.00, `ADJ_CAP` $1.50, brief `kit/brief-r0.md`. Nine writer reps ran, and none is VOID. The executor read
every `outside` hit by hand. They are sed, awk and grep patterns (`/^##`, `/5`, `grep -v '/base/\|/new/'`), explainer
text in a `Bash` heredoc write, and the reps' own tool-result files.

All nine explainers use the exact layout. Their Synopsis sections run from 196 to 235 words, and the whole explainers
from 1,404 to 1,737.

| Bar | `p80` | `p90` | `p92` |
|---|---|---|---|
| B1 Plan | 3/3 holds | 3/3 holds | 2/3 holds |
| B2 Build | 3/3 holds | 3/3 holds | 3/3 holds |
| B3 Project | 3/3 holds | 3/3 holds | 3/3 holds |
| B4 Accuracy | 3/3 holds | 2/3 holds | 2/3 holds (3/3 under the executor's reading) |
| B5 Length | 3/3 holds | 3/3 holds | 3/3 holds |
| All five bars at once | 3/3 | 2/3 | 1/3 |

**Every bar holds on all three tuning fixtures, so the treatment passes at round 0.** No wording round runs (plan
Task 3 Step 4).

**FAILs, checked against the fixture files.**

- `p90` rep2 B4: "The `specs/history.md` entry records three rulings and four deviations." The entry has 3 rulings and
  5 deviations. The executor agrees. Reps 1 and 3 state 3 and 5, correctly.
- `p92` rep1 B1: the reader wrote "Eight claims (C1–C8) were wrong or missing", from the body's "The spec lists them
  as C1 to C8". The spec lists six Claude Code claims, C1 to C6, and marks C6 "Correct as written". C7 and C8 are
  edits that are "not Claude Code claims". The executor agrees.
- `p92` rep2 B4: **contested.** The adjudicator read the hunk `@@ -107,6 +108,11 @@` and wrote that the pointer
  paragraph is at lines 112 to 115, so "`SKILL.md` gains a pointer at lines 111–114" was wrong. The file at the head
  has the paragraph at lines 111 to 114, with blank lines at 110 and 115. The executor's reading is that the claim is
  correct, so rep2 passes B4. Both readings leave B4 holding on `p92`, so the reading does not go to the owner.

**Spot-check of the PASS reps at the margin.** Three bars hold at exactly 2 of 3, so a wrong PASS could reverse a
result. The executor checked the numbers and line citations in `p90` reps 1 and 3 and `p92` reps 1 and 3 against
the fixture files. These all match:

- `p90`: `hooks/readonly-agent-guard.py:108`, `:781`, `:822`, `:896` and `:921`; the cap of 64; 10 new test
  functions; 148 test lines; the 16 repeats; 3 rulings and 5 deviations; 7 files, +1,262/−37; the guard's +123/−19;
  the plan's 636 lines and the spec's 295.
- `p92`: `discovery.md:11`, `:115-122` and `:202`; `SKILL.md:111-114`; the body's 18,285 to 18,753 characters; 25
  reps in `f88f36a` and 60 in `2207cc5`.

`p92` rep3's "cut the `SKILL.md` body to 434 lines" describes plan 72's earlier state, which the diff does not cover.
Under B4's text it is no contradiction. No PASS is disputed.

**What the brief changed.** The treatment fixed the control's failure mode. The control stated unchecked counts and
line totals. The treatment reps ran `git diff --numstat`, `wc -w` and line counts before they wrote. The one remaining
count error (`p90` rep2) is a ruling and deviation count. The brief's instruction to give "the line where that helps"
brought in line citations, which are a new kind of B4 claim. All the cited lines that the executor checked are
correct.

**Held-out exposure check.** No round 0 explainer names plan 84 or its subject.

**Spend.** Round 0: writers $4.96, readers $0.49, adjudicators $5.19, total $10.65 (estimate $10.24). Running total:
$23.17.

**Public repository scan** over `treatment-r0/`: no line.

## Held-out

`p84` runs once, on the shipped brief `skills/finishing-a-development-branch/references/branch-explainer-prompt.md`,
which is `kit/brief-r0.md` byte for byte. No round tunes against it.

**Estimate:** 3 × ($0.546 + $0.050 + $0.563) = **$3.48**. The means are over every run so far: 21 explainer writers
(pilot, control and round 0), 19 readers and 19 adjudicators. Spend so far is $23.95, so spend plus the estimate is
$27.43, below the $120 stop.

**Run.** Writer cap $3.00, `ADJ_CAP` $1.50. Three writer reps ran, and none is VOID. Every `outside` hit is a sed or
awk pattern (`/^##`, `/p`). All three explainers use the exact layout. Their Synopsis sections have 208 to 221 words,
and the whole explainers 1,556 to 1,737.

| Bar | `p84` |
|---|---|
| B1 Plan | 3/3 holds |
| B2 Build | 3/3 holds |
| B3 Project | 3/3 holds |
| B4 Accuracy | 3/3 holds |
| B5 Length | 3/3 holds |
| All five bars at once | 3/3 |

**Every bar holds on the held-out fixture.** The executor read all three adjudications against the bar text and
disputes none. A spot-check agrees with the adjudications: each explainer states the entry's counts as 12 rulings and
13 deviations, and the entry has 12 and 13. Before they wrote, the writers counted these with `grep -c`, as the brief's
B4 instruction asks.

**Spend.** Writers $1.86, readers $0.15, adjudicators $2.02, total $4.03 (estimate $3.48).

**Public repository scan** over `heldout/`: no line.

## Micro-test

The shipped Step 3b, before its commit. The kit is `micro/` (`build_micro.py`, `tools.txt`, `GRADING.md` and
`fixtures/`), committed before any rep (`c9e1952`, `a4595d8`). Each rep is a tool-less `claude -p` answer on
`claude-sonnet-5-5`, cap $0.50, run by `kit/run_plain.sh`.

**Skill text under test.**

- `SKILL.md`: Core principle gains "Explain branch". A Step 3b pointer (306 characters, at most 400) sits before
  Step 4. Red Flags, Always, gains "Explain a plan branch (Step 3b) before presenting options".
- Finishing's body: 19,009 characters at EXEC_BASE, 19,392 now (+383), within the 19,700 window and the plan's
  19,600 limit.
- `references/branch-explainer.md` holds the procedure. Its `DISPATCH` block is the kit's text, byte for byte.
- `references/branch-explainer-prompt.md` is `kit/brief-r0.md`, byte for byte (sha256
  `c7f7ef606adde4fcda1369aa8bcf09d742109598f656a63c4926d5eacc90331e`).

**Rule test** (Review Focus 2). On a scratch repository whose branch renames `specs/plans/7-x.md` to
`specs/plans/completed/7-x.md`, item 3's command printed `specs/plans/completed/7-x.md` from the top folder, from
`specs/` and with `diff.renames=false`. On a branch that changes only `src/a.py`, it printed nothing.

**Prompt hashes** (`MANIFEST.txt`; prompts in `~/.cache/agent-skills/scratch/plan94/micro/`):

| Arm | Scenario | sha256 |
|---|---|---|
| control | `M1-plan` | `d01d51e088272bbdf82f8e6df93d2161fe1beb9e63ab58e20e7769ddbd6983d5` |
| control | `M2-noplan` | `cf715645b180ca3a5ae51534a441947999df3913632f40506ca39e2d99b9770d` |
| treatment | `M1-plan` | `c282cba5fd87db1c19d704a1fcae1b1fca387bed57317d78eb20cc288195c276` |
| treatment | `M2-noplan` | `9bbf9aea7329e5fa67397e8b6fde1f9d8fbc7f3777feec351bc03c67e40cdb54` |
| treatment | `M3-refused` | `5aa3930bdbea5d499e34d6f15d432d6a6927aedd57e1ecfeee78cab3c1b753aa` |
| treatment | `M4-detached` | `641747a37a09e18da1307fa4e66c61a3526e2f262a063e2e6f39252947cd78f0` |
| treatment | `M5-skip` | `172a0592e1b1c5be4671f5a1f1ec20e630313369d5240fd6ee4f5d88434d86e2` |
| treatment | `M6-pointer` | `00b2fc2fabfb9b2e6a14b971b2b410bbf529a44a3386198c6909cbf010efc6d1` |

**VOIDs:** none. All 40 reps pass `result-ok`, and each names one model, `claude-sonnet-5-5`, with no non-message
iteration, one turn and no permission denial.

**Grades** (bar: at least 4 of 5 treatment reps; the control arms have no bar).

| Scenario | Treatment | Control | Deciding words |
|---|---|---|---|
| `M1-plan` | 5/5 PASS | 0/5 dispatch | Every treatment rep runs `git fetch origin main`, then `git merge-base origin/main HEAD`, then dispatches `TOOL Agent subagent_type=general-purpose, model=opus` with `Repository: /work/atlas` and an output under `branch-explainers/atlas/`, then `REPORT Explainer (<N> words): <path>`, then the four-option menu. The no-plan question appears only under `IF it prints nothing`. Every control rep shows the menu at once. |
| `M2-noplan` | 5/5 PASS | 0/5 offer | Every treatment rep asks `This branch adds no plan. Do you want an explainer of it before the menu?`, followed only by `IF yes` or `IF no` lines. Every control rep shows the menu at once. |
| `M3-refused` | 5/5 PASS | — | "Explainer failed: the subagent could not write … (permission denied), so nothing was written. I won't retry it.", then the four-option menu. |
| `M4-detached` | 5/5 PASS | — | `Repository: /work/atlas/.claude/worktrees/csv-header-2f1c`, a `detached-4be1c9a` slug, `REPORT Explainer (<N> words): <path>`, then the three-option detached-HEAD menu. |
| `M5-skip` | 5/5 PASS | — | No `git fetch`, `git merge-base`, dispatch or offer. The four-option menu follows, after at most the skill's opening line. |
| `M6-pointer` | 5/5 PASS | — | `TOOL Read file_path=/Users/lm/.claude/skills/finishing-a-development-branch/references/branch-explainer.md` comes first, before any dispatch or menu. |

Grading readings, applied the same way to every rep:

- **A placeholder for an unseen output counts as that output.** The answers write `<full BASE sha>`, `<HOME>` and
  `<date>` for the outputs of the `RUN` lines that they name. Under the session's facts, the date is 2026-11-13 and
  the slug is `feat-csv-header` or `detached-4be1c9a`. So each output path ends as the row requires. A decision-only
  answer cannot write BASE in any other way.
- **A dispatch under a branch that the facts do not take is not graded.** M2's answers show a dispatch under
  `IF it prints a path`. The session's facts take the `prints nothing` branch, and the grading rule grades that branch.
- **The backlog line before the menu is allowed.** `M1` rep5 reports Step 1b's summary line before the menu, as
  Step 1b says ("report the summary line as printed"). The menu itself is word for word.

**An observation from M6.** After the Read, the answers guess the procedure, because they have not seen the file. Two
of them "REPORT the subagent's explainer", which the procedure forbids. M1 to M5, with the file read, never do that.
M6's row tests only that the pointer opens the file.

**Wording rounds:** none. Every treatment scenario met its bar on the first run.

**Micro-test spend:** $0.78 for 40 reps.

**Final-review scenario `M7-notrack`.** Codex finding F2 in the final review: the fetch fails, and no
`origin/<base>` ref exists, so item 2 names no command that gives BASE. `GRADING.md` gained the M7 row and
`fixtures/M7-notrack.txt` before any M7 rep ran (`6c0d244`). The text under test is the shipped text above.

- Prompt: treatment `M7-notrack`, sha256 `b22912b075045f1c75f27dd80240cad8e20a2601f254d2732af9cbd36aaf7a9f`.
- VOIDs: none. All 5 reps pass the screen.
- Grade: **5/5 PASS**. Every rep runs `git merge-base main HEAD` first, records BASE under `IF it prints a sha`,
  and goes on to item 3's plan check, the dispatch and the four-option menu, word for word. No rep guesses BASE.
- The branch that the facts do not take: if local `main` also fails, reps 2, 4 and 5 report one line and show the
  menu. Reps 1 and 3 ask the partner which commit the work starts after. The row grades the branch that the facts
  take, so these lines do not count.
- Cost: $0.15.

The current text reaches BASE or the menu on this path, so it stays unchanged. The ledger records F2 as a ruling.

## Spend

| Item | Cost |
|---|---|
| Pilots: isolation probe, write check, cost pilot | $1.34 |
| Control arm (11 writers, 2 of them VOID; 9 readers; 9 adjudicators) | $11.18 |
| Treatment round 0 (9 each) | $10.65 |
| Micro-test (40 Sonnet reps) | $0.78 |
| Held-out `p84` (3 each) | $4.03 |
| Final review: `p90` control rep6 (writer, reader, adjudicator) | $0.90 |
| Final review: micro-test `M7-notrack` (5 Sonnet reps) | $0.15 |
| **Total** | **$29.02** |

The plan estimated about $57 with no wording round. The run stayed below both stops: pilots and control came to
$13.42 with the final review's `p90` rep6, against the $35 stop, and the total stayed below the $120 stop.

## Verdict

- **Baseline: RED.** With no guidance, Opus writes an explainer that teaches the plan, the build and the project
  (B1, B2, B3 and B5 hold on all three tuning fixtures). It fails B4 Accuracy on all three: 1/3 on `p80`, 1/3 on
  `p90` and 1/3 on `p92`. Five of its six contradicted claims are numbers or details that it did not check.
- **Treatment: passes at round 0.** The brief adds the spec's layout, inputs, limits, style and output, and one
  instruction aimed at B4 ("Check before you state"). Every bar holds on `p80`, `p90` and `p92`. B4 rises to 3/3,
  2/3 and 2/3 (3/3 on `p92` under the executor's reading). No wording round ran.
- **Held-out: passes.** On `p84`, every bar holds at 3/3 with the shipped brief.
- **Contested readings:** one, `p92` treatment rep2 B4 (Treatment, Round 0 results). It changes no bar's result on
  the fixture, so it did not go to the owner.
- **Step 3b wording:** every micro-test scenario passes 5 of 5 (Micro-test), the final review's `M7-notrack`
  included.
- **Exposure:** no explainer of the tuning fixtures names plan 84.
- **What the probe does not show:** see Known limits. The live run on this plan's own branch (plan Task 7) is
  report-only, and its result goes in the final report, not here.
