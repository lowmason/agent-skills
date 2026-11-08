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

## Isolation probe

`run_reps.sh isolation_probe.txt /tmp/plan80-work/probe 1 1 claude-opus-5-5` ran on Claude Code 2.1.316
(`claude --version` printed `2.1.316 (Claude Code)`), under `env -i`, with the default per-rep cap of $0.50. The
CLI signed in with its stored login. All five probe lines read `NO`: no `CLAUDE.md` text, no output style, no rule,
no SessionStart context and no memory. The reply, in full:

```text
1. NO
2. NO
3. NO
4. NO
5. NO
```

`show_reps.py` shows one turn, no extra iterations, one model (`claude-opus-5-5`), `success`, and a cost of $0.014.
The probe output sits in `/tmp/plan80-work/probe` and is not committed, so its cost is not in the kit's sum.

## Control

Arm `control`: the texts at `BASE80` (`fb784f4`). The prompts were built with
`build_prompts.py fb784f4 /tmp/plan80-work/control`. `MANIFEST.txt` gives these prompt hashes:

- `gate-tag.txt`: sha256 `1123892d8589e8c51a16caaec82f95831e9dcfb5ef95decffbc86dbbd141a7f9`. It carries the whole of
  `final-review.md` at `fb784f4`.
- `history-filter.txt`: sha256 `4eb71ee338872fe5a8da77eac1a589122fea8dff7f90915833e7a8b1bdf22f76`. It carries the
  writing-plans `SKILL.md` body and no reference file, because the `histor*.md` glob matched nothing.

Each case ran 5 reps on Claude Code 2.1.316, with this command:
`run_reps.sh <prompt> specs/red-baseline-development-history/control/<case> 1 5 claude-opus-5-5 1.00`.
So there are 10 rep files. No rep was VOID: every rep ran one turn, no tool and one model, and ended with
`success`. No rep wrote an error file, so no rep was rerun. Every reply was read
in full, and every verdict was read by hand by the committed rules.

| Case | Bar | Passing reps | Failing reps |
|---|---|---|---|
| `gate-tag` | `treatment 5/5; control fails at least 1 of 5` | 0/5 | 5/5 |
| `history-filter` | `treatment 5/5; control fails at least 1 of 5` | 0/5 | 5/5 |

Both cases fail at least 1 of 5, so the bar's control condition is met for each. The stop rule does not apply.

### gate-tag

The pass rule has four clauses: (1) all four rulings listed; (2) the Task 2 entry holds the literal text
`contradicts spec` followed by `§ 2` or `Alert threshold`; (3) no other ruling's entry holds `contradicts spec`;
(4) no ruling is put to the partner as a question to approve. Every rep meets clauses 1 and 3. Every rep lists the
four rulings in order with a cost, and no rep writes `contradicts spec` anywhere. Every rep breaks clause 2 first.

- rep1: FAIL — clause 2: the Task 2 entry says "this departs from spec § 2", with no `contradicts spec`. Clause 4
  also breaks: the reply asks "Do you want any of rulings 1–4 reversed?", and asks whether to record a § 2
  amendment "if you keep" ruling 1.
- rep2: FAIL — clause 2: the Task 2 entry says "not the spec's 2 or fewer", with no `contradicts spec`. Clause 4
  also breaks: question B asks whether to update § 2 "or would you rather revisit the threshold", which puts the
  Task 2 ruling up for approval.
- rep3: FAIL — clause 2: the Task 2 entry names no spec section and has no `contradicts spec`. The § 2 conflict
  comes up only in question A. Clause 4 also breaks: question A asks "do you want the threshold reverted to 2?"
- rep4: FAIL — clause 2: the Task 2 entry has no `contradicts spec`. The § 2 conflict comes up only in question B.
  Clause 4 also breaks: question B offers "revert the code to 2" as an option.
- rep5: FAIL — clause 2: the Task 2 entry says "This departs from spec § 2", with no `contradicts spec`. Clause 4
  holds: the reply lists the rulings as decisions "already in the code" and invites the partner to overturn one,
  but it asks no question about a ruling. Its one question is the Declined to judge line.

Fails: 5 of 5. The `question` aid fired on every rep. In every rep it marks the Declined to judge line, which the
reference text puts to the partner as a question on purpose. In reps 1 to 4 it also marks a question about the
Task 2 ruling. In the control, each rep sees the § 2 conflict and says so in its own words, but no rep uses the tag,
and four of the five reps turn the conflict into a question about the ruling.

### history-filter

The pass rule has six clauses: (1) the Task 2 ruling is labelled `Ruling, contradicts spec (Task 2)` with its what,
why and cost parts; (2) the module-name ruling is labelled `Ruling (Task 3)` with its three parts; (3) the
batch-email ruling and the retry-jitter ruling are left out; (4) the Deviation line is kept with a Source pointer;
(5) the closed-item line is kept with its quoted title and `(deferred by 9-dock-status)` unchanged; (6) the heading
and the Plan line are unchanged. Every rep meets clauses 2, 4, 5 and 6. Every rep breaks clauses 1 and 3.

- rep1: FAIL — clause 1: the Task 2 ruling keeps the draft's label `Ruling (Task 2)` and adds "Contradicts spec: §
  2 Alert threshold" at the end of the line, with a note on the retired spec. Clause 3 also breaks: the batch-email
  ruling and the retry-jitter ruling both stay in.
- rep2: FAIL — clause 1: the label is `Ruling (Task 2)`, with "Contradicts spec: § 2 Alert threshold." added at the
  end. Clause 3 also breaks: both rulings that kept the plan stay in. The rep also adds a line that is not in the
  draft: "All four rulings confirmed by owner at the completion gate, 2026-11-09; no reverts." The rule does not
  score that line.
- rep3: FAIL — clause 1: the label is `Ruling (Task 2)`, with "Contradicts spec § 2 Alert threshold, which still
  reads 2 or fewer" added at the end. Clause 3 also breaks: both rulings that kept the plan stay in.
- rep4: FAIL — clause 1: the label is `Ruling (Task 2)`, with "Contradicts spec: § 2 Alert threshold." added at the
  end. Clause 3 also breaks: both rulings that kept the plan stay in.
- rep5: FAIL — clause 1: the label is `Ruling (Task 2)`, with "Contradicts spec: § 2 Alert threshold" and a note on
  the retired spec added at the end. Clause 3 also breaks: both rulings that kept the plan stay in.

Fails: 5 of 5. In the control, every rep carries the gate's tag into the entry, but as trailing text, not as the
label. No rep filters the rulings. Each rep keeps the draft's four rulings as printed.

### Spend

| Item | Cost |
|---|---|
| `gate-tag` control, reps 1 to 5 | $0.140 |
| `history-filter` control, reps 1 to 5 | $0.176 |
| Control arms, `show_reps.py` total over both folders | $0.32 |
| Isolation probe (in `/tmp`, not in the kit's sum) | $0.014 |

The control arms cost $0.32, against the $5 control stop. The kit's sum is $0.32 of $12, or $0.33 with the probe.

Findings for Task 7:

- `gate-tag`: the control fails 5 of 5. Task 7's treatment must pass 5 of 5.
- `history-filter`: the control fails 5 of 5. Task 7's treatment must pass 5 of 5.
