# Plan 80 micro-tests: the development history record

This record holds the micro-tests for plan 80 (`specs/plans/80-development-history-record.md`). A micro-test runs one
decision many times through a fresh `claude -p` with no tools, then reads each reply by a rule fixed in advance. One
run is a rep. Plan 80 changes the wording of two texts, and each change gets one case:

- `gate-tag`: at the plan-completion gate, the controller lists every `Ruling:` line of the ledger. Plan 80 adds a
  tag. A ruling that contradicts spec text is listed with `contradicts spec: <spec section>`, and it stays a decision
  already taken, not a question. The text under test is
  `skills/subagent-driven-development/references/final-review.md`.
- `history-filter`: at the end of the plan-completion protocol, the agent appends an entry to `specs/history.md`.
  Plan 80's spec decision D7 says that an entry keeps only the rulings that changed the build against the spec or the
  plan. A ruling that declined a finding and kept the plan as written stays out. The texts under test are
  `skills/writing-plans/SKILL.md` and any `skills/writing-plans/references/histor*.md` file.

Task 1 builds the kit, registers the rules and runs the control arms. Task 7 runs the treatment arms with the same
kit and appends its own section to this record.

## Base

`BASE80` is the commit that adds plan 80. It is the execution branch's start commit and the commit that the control
arm reads its texts from: `fb784f4` (`fb784f46955d69f9149344be916755a95bd23946`).

Two checks ran before Task 1:

- `git diff --stat fcc631e fb784f4 -- skills commands` printed nothing. `fcc631e` is the commit that first added the
  plan. So no skill or command changed while the plan was reviewed.
- The parallel-session check of the Global Constraints ran after `git fetch origin main`:
  `git log --oneline fb784f4..origin/main` over `skills/writing-plans/SKILL.md` and both executors'
  `references/final-review.md`. It listed no commit.

## Kit

Kit: `specs/red-baseline-development-history/kit/`. Four files are copies of plan 77's kit
(`specs/red-baseline-audit-p2/kit/`). No file of plan 77's kit was edited.

- `run_reps.sh` changes the plan number in its first comment line (77 to 80) and its temp prefix, from
  `/tmp/plan77-rep-` to `/tmp/plan80-rep-`. The comment `Plan 77 deviation (a)` keeps its number. It names the plan
  where the `env -i` form came from. Plan 80 requires `env -i` in its Global Constraints, so the form is no
  deviation here, and "Plan 80 deviation (a)" would be false. The file mode stays executable.
- `isolation_probe.txt` is an unchanged copy.
- `show_reps.py` changes the plan number in its docstring and its reading aids. The four aids flag
  `contradicts spec` (`contradicts-spec`), `Ruling` (`ruling`), `history` (`history`) and a question mark
  (`question`). Each aid ignores case. An aid only points the reader at a reply. It is never a verdict.
- `build_prompts.py` changes only the plan number in its docstring.
- `cases.py` is new. Its shape is the shape of plan 76's `specs/red-baseline-review-fixes/kit/cases.py`. It holds
  the two cases, the VOID rule (when a rep is thrown out and rerun, not scored), the model, the per-rep budget and
  the bar. The model constant is `MODEL = 'claude-opus-5-5'`, and the budget is `BUDGET = '1.00'`. The VOID rule is
  copied word for word from plan 76's `cases.py`.

Each case's fixture, task, pass rule and leak pattern were checked against plan 80's Task 1 text by a script, byte
for byte. All matched.

`build_prompts.py <sha> <out-dir> [<case> ...]` builds the prompts at a sha and writes `MANIFEST.txt`.
`build_prompts.py leakview <out-dir>` puts a placeholder in place of every text under test, for the leak grep.
`run_reps.sh <prompt> <out-dir> <first> <last> claude-opus-5-5 1.00` runs the reps.

Each rep is a fresh
`claude -p --model claude-opus-5-5 --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format json --max-budget-usd 1.00`
with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, under `env -i`. Only `HOME`,
`USER`, `LOGNAME`, `PATH`, `SHELL`, `TMPDIR` and `LANG` pass through, each only when it is set. The rep runs from a
new, empty directory under `/tmp`, outside every repository. There are 5 scored reps per case and arm. Every verdict
is read by hand from the full reply.

## Arms

- `control`: each text at `BASE80` (`fb784f4`). At `BASE80` the `histor*.md` glob matches no file, so the
  `history-filter` control prompt carries the writing-plans `SKILL.md` body alone.
- `treatment`: each text at `T5`, the last commit of plan 80's Task 5. Task 7 runs it.

Both arms use the same frame, fixture and task. Only the sha of the texts differs. A `SKILL.md` text is its body
with the frontmatter removed. A reference file is the whole file.

## Bars

Both cases have the same bar: `treatment 5/5; control fails at least 1 of 5`. The treatment arm must pass all 5
scored reps. The control arm must fail at least 1 of its 5 scored reps, or the wording change has nothing to fix.

## Spend stop

The whole kit stops at $12. The sum is `total_cost_usd` over every `rep<N>.json` in this record's folders, and
`show_reps.py` prints it. If the control arms alone pass $5, the run stops and asks the owner.

## Stop rule

A case whose control fails 0 of 5 has nothing to fix in wording. Record it and put it to the owner
in the completion gate's batch. The spec-required wording still lands.

## Leak check

`build_prompts.py leakview /tmp/plan80-work/leak` wrote the two leak-view prompts. Each was grepped with
`/usr/bin/grep -nE` for its own case's leak pattern. The `gate-tag` pattern was also grepped over the
`history-filter` prompt. A second pass with `-i` (ignore case) gave the same hits.

| Prompt | Pattern | Hits |
|---|---|---|
| `gate-tag` | `gate-tag`: `contradicts spec\|spec section\|changed the build` | none |
| `history-filter` | `history-filter`: `changed the build\|kept the plan as written\|rule 3\|parks? a finding` | none |
| `history-filter` | `gate-tag`: `contradicts spec\|spec section\|changed the build` | line 21 only: `contradicts spec` |

The one hit is line 21 of the `history-filter` prompt, the first item of the gate list in the fixture. It ends with
`contradicts spec: § 2 Alert threshold`. The plan puts it there on purpose: the fixture shows the gate message that
the agent already sent, with the tag on the Task 2 ruling. The case tests whether the entry keeps that tag in its
label, not whether the agent finds the tag. So the hit stands. No hit comes from the frame, the task line or the rest
of either fixture.

## Reading rules

These rules were registered and committed before any rep ran. Fixtures and rules are not edited after any rep
output is seen.

**VOID (every case).** VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no dispatch, no paragraph and no instruction).

This VOID rule is copied word for word from plan 76's `cases.py`. Its last parenthetical names plan 76's task
outputs, not this plan's. This record reads its main clause: a reply that writes no gate message (`gate-tag`) or no
entry (`history-filter`) does no part of the task. A rerun happens only within the spend stop. The scored reps of a
case are its first 5 reps that are not VOID.

**gate-tag** (text: `skills/subagent-driven-development/references/final-review.md`). Bar:
`treatment 5/5; control fails at least 1 of 5`.

Fixture: the controller of a subagent-driven run of a bike-share dock-status service has finished all four tasks.
The final review is clean, with one Declined to judge line. The fixture shows the spec's three sections and the
ledger in full. The ledger holds four rulings. The Task 2 ruling changes the alert threshold that spec § 2 sets.
The Task 3 module-name ruling changes a plan path, not a spec section. The batch-email ruling and the retry-jitter
ruling keep the plan as written. Task: write the gate message to the partner, exactly as sent.

PASS = the message lists all four rulings; the Task 2 ruling's entry contains the literal text "contradicts spec" followed by "§ 2" or "Alert threshold"; no other ruling's entry contains "contradicts spec"; and no ruling is put to the partner as a question to approve. FAIL = any of these does not hold.

**history-filter** (texts: `skills/writing-plans/SKILL.md` and `skills/writing-plans/references/histor*.md`). Bar:
`treatment 5/5; control fails at least 1 of 5`.

Fixture: the same run, at the end of the plan-completion protocol. The gate list already went to the partner, with
the `contradicts spec` tag on the Task 2 ruling, and the partner let all four rulings stand. The plan and the spec
are retired. The fixture shows the draft that `history_entry.py draft` printed. The draft lists all four rulings
under the plain `Ruling` label, one deviation and one closed earlier item. Task: write the exact text appended to
`specs/history.md`.

PASS = the entry keeps the Task 2 ruling labelled "Ruling, contradicts spec (Task 2)" and the module-name ruling labelled "Ruling (Task 3)", each with its what, why and cost parts all present; it leaves out the batch-email ruling and the retry-jitter ruling; it keeps the Deviation line (shortened or not) with a Source pointer, and the closed-item line with its quoted title and "(deferred by 9-dock-status)" unchanged; and the heading and Plan line are unchanged. FAIL = any of these does not hold.
