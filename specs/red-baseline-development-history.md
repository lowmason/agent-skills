# Plan 80 micro-tests: the development history record

This record holds the micro-tests for plan 80 (`specs/plans/completed/80-development-history-record.md`). A micro-test runs one
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
- `treatment`: each text at `T5`, the last commit of plan 80's Task 5. Task 7 runs it. `T5` is `6df0a2c`
  (`feat(executors): tag gate rulings that contradict the spec`). The one commit after `T5` on the branch at Task 7,
  `8e6ec6e`, changes only `commands/`, `runtimes/`, `NOTICE` and `README.md`, so no text under test changed after
  `T5`.
- Final text, after the final review: the `gate-tag` text is `fd4749b`, the `treatment2` arm. The `history-filter`
  text changed once after `T5`: `00b3c45` adds `--date <YYYY-MM-DD>` to the `deferred` command in
  `## /deferred entries` of `references/history.md`. The case's fixture and task read only plan entries, so no arm
  was re-run for it (controller's ruling).

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

## Treatment

Arm `treatment`: the texts at `T5` (`6df0a2c`, `6df0a2c081002cd073a14c6f5f1d1dc29626b7ef`). The prompts were built
with `build_prompts.py 6df0a2c /tmp/plan80-work/treatment`. `MANIFEST.txt` gives these prompt hashes:

- `gate-tag.txt`: sha256 `ee98fc7144fe08ec2e355e9c9ee6f28d7c6e94c5a8f6c7e7ea241749d608e096`. It carries the whole of
  `final-review.md` at `6df0a2c`.
- `history-filter.txt`: sha256 `0babfc70409f97640996a1e887df44181b74bb2bf38782f333dc00ee45ea82e0`. It carries the
  writing-plans `SKILL.md` body and `references/history.md`, the one file that the `histor*.md` glob matches at
  `6df0a2c`.

A diff of each treatment prompt against its control prompt shows changes only inside the texts under test. The
`gate-tag` prompts differ only in the gate paragraph. The `history-filter` prompts differ only in `SKILL.md` (the
step 3 example block is gone and the step 5 pointer is new) and in the added `history.md` block. The frame, the
fixture and the task are byte-identical.

Three readings were fixed and written here before any treatment reply was read:

- **Letter case.** The `gate-tag` clause "the literal text `contradicts spec`" and the `history-filter` label
  `Ruling, contradicts spec (Task 2)` are read with letter case ignored, as the reading aids are. So
  `Contradicts spec` at the start of a sentence counts. "Literal" means those words, next to each other and in that
  order. A paraphrase ("departs from spec", "conflicts with the spec", "contradicts the spec") does not count. For
  `gate-tag`, `§2` with no space counts, and so does `Alert threshold` alone.
- **Clause 4 of `gate-tag`** is read as the control's reps were. A sentence in question form about a ruling, or
  about the rulings as a group (for example "Do you want any of rulings 1–4 reversed?"), fails the clause. A
  statement that the partner can overturn a ruling, with no question about it, holds (control rep5). A question
  about the Declined to judge line always holds, because the reference text puts that line to the partner on
  purpose.
- **`history-filter` extra lines.** A line that the rule does not name is not scored, as control rep2's extra line
  was not. A `# Development history` title line above the entry does not break clause 6, because Finish step 8 of
  the reference allows it when the file is absent.

Each case ran 5 reps on Claude Code 2.1.316, the control's version, with this command:
`run_reps.sh <prompt> specs/red-baseline-development-history/treatment/<case> 1 5 claude-opus-5-5 1.00`.
So there are 10 rep files. No rep was VOID: every rep ran one turn, no tool and one model, and ended with
`success`. No rep wrote an error file, so no rep was rerun. Every reply was read in full, and every verdict was read
by hand by the committed rules.

| Case | Bar | Passing reps | Failing reps | Bar met |
|---|---|---|---|---|
| `gate-tag` | `treatment 5/5; control fails at least 1 of 5` | 2/5 | 3/5 | no |
| `history-filter` | `treatment 5/5; control fails at least 1 of 5` | 5/5 | 0/5 | yes |

### gate-tag

Every rep meets clauses 1, 2 and 3. Every rep lists the four rulings in order with a cost. The Task 2 entry ends
with `contradicts spec: § 2 Alert threshold` in every rep, in code or bold or both. No other entry holds
`contradicts spec`. Rep2's Task 3 module-name entry says "This departs from the plan, not the spec", which is not the
tag. So the tag itself lands 5 of 5. The fails are all on clause 4.

- rep1: FAIL — clause 4: the reply asks "Please reply with your call on #5, and on #1 in particular, since it
  departs from the spec. If you keep #1, should I update § 2 of `specs/dock-alerts.md` to say 3 or fewer?" That asks
  for a call on the Task 2 ruling and asks a question about it, as control rep1 did.
- rep2: PASS — clause 4 holds. The rulings are "decisions already in the code", and the reply says "Tell me if you
  want any of them reversed" and "flag any ruling you want reversed, especially #1". Those invite a reversal and ask
  no question about a ruling, as control rep5 did. Its one question is the Declined to judge line.
- rep3: FAIL — clause 4: "Please also confirm or reverse ruling 1, since it departs from the spec's threshold." The
  sentence asks the partner to approve (confirm) the Task 2 ruling or reverse it, with no default. So the ruling is
  put to the partner to approve, though the sentence is not in question form. The registered clause 4 reading names
  only question forms and invitations, so this verdict rests on the rule's own words "as a question to approve". The
  added reading below was written after this reply was seen. It does not change the bar result: with rep3 as a pass,
  the case is 3 of 5, still below 5 of 5.
- rep4: PASS — clause 4 holds. The header says "you don't need to answer them". The sentences "If you agree with it,
  I'll record a deferred item to update § 2 to say 3. If you don't, I'll revert the threshold to 2." are statements of
  what the controller does, like control rep5's "Unless you overturn 1, I'll also update spec § 2". The close asks
  for "anything in 1–4 you want reversed", an invitation. This is the closest call of the five.
- rep5: FAIL — clause 4: under "For you to rule on", the reply asks "Ruling 1 vs. spec § 2: should I update the spec
  to say "3 or fewer," or revert the code to "2 or fewer"?" That puts the Task 2 ruling to the partner as a question.

Passes: 2 of 5, below the bar of 5 of 5. The treatment fixes the control's clause 2 fail in every rep. But the tag
draws the agent's attention to the § 2 conflict, and three reps turn it into a request for a decision on the ruling.
The text at `T5` says the rulings are "decisions already taken, … not questions", but it does not say what to do
about the spec. The spec of plan 80 does: the history entry, not a spec amendment, records the ruling, and a revert
that the owner asks for becomes a deferred item. So `gate-tag` gets one wording round.

One reading was added after the `gate-tag` treatment replies were read, and before any `treatment2` rep ran. It
extends the clause 4 reading above. An explicit request to confirm, to approve or to make a call on a named ruling
fails clause 4, even when the sentence is an imperative and not a question ("Please also confirm or reverse ruling
1"). An optional invitation ("tell me if you want any reversed") still holds, as does a statement of what the agent
does by default. The `treatment2` reps are read by this reading without change.

### history-filter

The six clauses are as in the control section. Every rep meets all six.

- rep1: PASS — the Task 2 ruling is labelled `Ruling, contradicts spec (Task 2)` and the module-name ruling
  `Ruling (Task 3)`, each copied whole with its what, why and cost parts. The batch-email and retry-jitter rulings
  are gone. The Deviation line is shortened ("v1 was retired") and keeps `Source: plan, Task 1.` The closed-item line,
  the heading and the Plan line are as the draft printed them.
- rep2: PASS — the same entry as rep1. The Deviation line reads "since v1 was retired" and keeps its Source pointer.
- rep3: PASS — the same entry as rep2, byte for byte.
- rep4: PASS — the same entry as rep1, byte for byte.
- rep5: PASS — the same entry as rep2, byte for byte.

Passes: 5 of 5, the bar. No rep adds a title line or a line that the rule does not name. In the control, every rep
kept all four rulings and put the tag after the text. In the treatment, every rep drops the two rulings that kept
the plan and puts the tag in the label.

### Wording round: gate-tag

`gate-tag` was below its bar, so it got its one wording round. The round is commit `fd4749b`
(`fd4749b9a02c334c8e3377cff71b739993af167e`, `fix(executors): keep a tagged gate ruling out of the questions
(gate-tag)`). It edits only the gate paragraph of the two executor files, in the same words. It touches no fixture,
task, pass rule or kit file. Before the edit, `git fetch origin main` and the parallel-session `git log` of the
Global Constraints listed no commit. The commit passed `run_commit_lints.sh` (`commit lints passed`),
`check_conformance.py`, `check_provenance.py` and `check_reviewer_block.py`.

The added text follows plan 80's spec (`specs/completed/development-history-record.md`, the gate paragraph and the Non-goals
bullet on spec amendments). In `skills/subagent-driven-development/references/final-review.md` it is four new lines
after "gets at most one round-trip.":

```text
A tagged ruling is still a decision taken, not a question: the plan's entry
in `specs/history.md` records it in place of a spec amendment, so ask your
partner nothing about it. Your partner may still ask to revert it, which
makes it a deferred item.
```

`skills/executing-plans/references/final-review.md` carries the same sentences after "one round-trip.", wrapped to
its own line breaks. The kit's `gate-tag` case reads only the subagent-driven-development copy. The executing-plans
copy is the same text, and no rep reads it.

Arm `treatment2`: the `gate-tag` prompt at `fd4749b`, built with
`build_prompts.py fd4749b /tmp/plan80-work/treatment2 gate-tag`. `MANIFEST.txt` gives `gate-tag.txt` sha256
`1192ad9d611286de03daec0aec8bd00a6ed6942d7d69a157cf6fb43ee833cd96`. A diff against the `treatment` prompt shows the
four added lines and nothing else. The 5 reps ran on Claude Code 2.1.316 with
`run_reps.sh <prompt> specs/red-baseline-development-history/treatment2/gate-tag 1 5 claude-opus-5-5 1.00`. No rep
was VOID: each ran one turn, no tool and one model, and ended with `success`. No rep wrote an error file.

| Case | Arm | Bar | Passing reps | Failing reps | Bar met |
|---|---|---|---|---|---|
| `gate-tag` | `treatment2` | `treatment 5/5; control fails at least 1 of 5` | 5/5 | 0/5 | yes |

Every rep meets clauses 1, 2 and 3: the four rulings in order with a cost, and `contradicts spec: § 2 Alert
threshold` on the Task 2 entry only. Each verdict below is on clause 4, read by the extended reading above.

- rep1: PASS — the rulings are "decisions, not questions". The reply says the history entry records ruling 1 "in
  place of a spec amendment" and "If you want any ruling reverted, say so and I'll log it as a deferred item", an
  invitation. Its one question is the Declined to judge line.
- rep2: PASS — the header reads "no answer needed". "If you'd rather revert it to 2 or fewer, say so and I'll log it
  as a deferred item" names ruling 1, but it is an optional invitation, not a request for a call. Its one question
  is the Declined to judge line.
- rep3: PASS — the Task 2 entry says the history entry records it "in place of a spec amendment". "If you want any
  of these reverted, say which one" is an invitation. Its one question is the Declined to judge line.
- rep4: PASS — "You can ask me to revert any of these. A revert becomes a deferred item." is a statement. Its one
  question is the Declined to judge line.
- rep5: PASS — "If you'd rather revert any ruling, say so and I'll log it as a deferred item" is an invitation. Its
  one question is the Declined to judge line.

Passes: 5 of 5, the bar. No rep asks whether to update the spec or to revert, and no rep asks the partner to
confirm a ruling. Every rep says that the history entry records the Task 2 ruling, which none of the `treatment`
reps said.

The clause 4 reading that was added after the `treatment` replies changes no bar result. No `treatment2` rep asks
a question about a ruling or asks for a call on one, so the registered reading also gives 5 of 5. In the
`treatment` arm, the registered reading gives at most 3 of 5, still below the bar.

### Bar results

| Case | Control | Treatment | Treatment 2 | Bar met |
|---|---|---|---|---|
| `gate-tag` | fails 5/5 | 2/5 at `6df0a2c` | 5/5 at `fd4749b` | yes, after the wording round |
| `history-filter` | fails 5/5 | 5/5 at `6df0a2c` | not run | yes |

### Treatment spend

| Item | Cost |
|---|---|
| `gate-tag` treatment, reps 1 to 5 | $0.124 |
| `history-filter` treatment, reps 1 to 5 | $0.169 |
| `gate-tag` treatment2, reps 1 to 5 | $0.128 |
| Kit total, `show_reps.py` over all five rep folders | $0.74 |

The kit's sum is $0.74 of the $12 spend stop. No batch came near the stop.

## Real-data check

Task 7 Steps 3 to 5 ran `history_entry.py` at the branch head (`fd4749b`) on real plans and the real backlog, from
the worktree root. `specs/deferred_items.md` and `specs/completed/deferred_items.md` are unchanged since `BASE80`
(`git diff --quiet fb784f4 HEAD` over both files exits 0), so the plan's expected counts at `BASE80`'s backlog apply
as written. Each run wrote stdout to a file, so the exit code is the script's own. Each count below is a `grep -c`
by pattern, not a count by eye. No run wrote to stderr, and no run wrote a file: `specs/history.md` is still absent.

Two controller rulings changed `draft`'s output after the plan was written. A deviation note's text now joins all
of its wrapped `>` lines, and a deviation under a non-task heading after the tasks prints
`- Deviation: <text>. Source: plan, § <heading>.` with no task label. Neither changes a count here. Plans 79 and 74
print no line of the second form (`grep -c '^- Deviation:'` is 0 for each).

### Step 3: `draft` on plan 79

Command:
`uv run skills/writing-plans/scripts/history_entry.py draft specs/plans/completed/79-derive-roadmap-resume-and-route-tests.md --date 2026-11-07`

| Check | Expected | Result |
|---|---|---|
| Exit code | 0 | 0 |
| Second line | `Plan: specs/plans/completed/79-derive-roadmap-resume-and-route-tests.md · Spec: none` | the same |
| `Rulings: no ledger given` line | 1 | 1 |
| Lines that start `- Deviation (Task` | 7 | 7 |
| Lines that start `- Deviation:` | 0 | 0 |
| Lines that start `- Decision` | 0 | 0 |
| Deferred line | `- Deferred: 8 items. Source: specs/deferred_items.md, § 79-derive-roadmap-resume-and-route-tests.` | the same |
| Closed-item lines | 4: one from `40-handoff-briefs`, three from `78-derive-roadmap-new-project-entry` | 4: 1 and 3 |

Step 3 meets every expected value. The full output:

```text
## 79-derive-roadmap-resume-and-route-tests — 2026-11-07
Plan: specs/plans/completed/79-derive-roadmap-resume-and-route-tests.md · Spec: none
Rulings: no ledger given

Differences from the design:
- Deviation (Task 1): the fixtures needed judgment calls the brief did not give (a new four-stage `OCCUPANCY_ROADMAP`, two extra `PROMOTED_ROADMAP` edits, a reworded Completion line), recorded in the record under `Plan 79: fixture judgment calls`. A review round (`fee932a`) removed two additions (an untracked-file sentence in dr-name-collision and a changed plan 3 Handoff in dr-resume-blocked). Source: plan, Task 1.
- Deviation (Task 1): two commits, `abe5ec3` and the review fix `fee932a`. Source: plan, Task 1.
- Deviation (Task 2): the plan's `git add specs/red-baseline-new-project-entry` stages the folder only, so the commit also staged the sibling record file. A second commit (`b4bf196`) recorded the controller's rulings on the readings and on the date conflict. Source: plan, Task 2.
- Deviation (Task 3): three further skill commits followed the plan's five edits (`c500e14`, `T3`): `T3-r1` `43fca10` (the wording round of Step 4), and `T3-r2` `99265a5` and `T3-r3` `5f52dfc` (review-found fixes to the unmet-`Consumes` text and the Parking heading). The final skill text is `5f52dfc`. Source: plan, Task 3.
- Deviation (Task 3): dr-stop-track and dr-park-ranked missed their bar at `T3`. The wording round closed dr-stop-track. dr-park-ranked took the owner's ruling to re-run once more (3 of 5, then 4 of 5), and its met result rests on the inline-fields reading of clause D. Source: plan, Task 3.
- Deviation (Task 4): `T-final` is `T3-r3` (`5f52dfc`), not `T3-r1`, because two review-found fixes followed the wording round. Source: plan, Task 4.
- Deviation (Task 4): record-only commits followed the review and the final review (`9e4e89d`, `ad807f9`, `b30f3c9`). Source: plan, Task 4.
- Deferred: 8 items. Source: specs/deferred_items.md, § 79-derive-roadmap-resume-and-route-tests.

Closed earlier deferred items:
- "`skills/derive-roadmap/SKILL.md` §5 (the resume) has two gaps found in" (deferred by 40-handoff-briefs).
- "**dr-known-progression fails conformance clause C: point-in-time awareness appears in 0 of 5" (deferred by 78-derive-roadmap-new-project-entry).
- "**Four routes that plan 78 added have no micro-test (plan 78 Task 7 and final review).** A" (deferred by 78-derive-roadmap-new-project-entry).
- "**Two wording gaps left by plan 78's final review (owner ruled file).**" (deferred by 78-derive-roadmap-new-project-entry).
```

### Step 4: `draft` on plan 74

Command:
`uv run skills/writing-plans/scripts/history_entry.py draft specs/plans/completed/74-backlog-protocol.md --spec specs/completed/backlog-protocol.md --spec-status retired --date 2026-10-31`

| Check | Expected | Result |
|---|---|---|
| Exit code | 0 | 0 |
| Lines that start `- Decision` | exactly 1 | 1 |
| The decision line starts | `- Decision D18 (spec amendment): approve Task 0's amendment.` | the same |

Step 4 meets every expected value. The full output:

```text
## 74-backlog-protocol — 2026-10-31
Plan: specs/plans/completed/74-backlog-protocol.md · Spec: specs/completed/backlog-protocol.md (retired)
Rulings: no ledger given

Differences from the design:
- Deviation (Task 1): the controller made the init-record half of the probe check after the control runs, with one `--output-format stream-json --verbose` probe (commit a5bf1ee). Source: plan, Task 1.
- Deviation (Task 4): the negation exemption took five fix attempts. The controller parked the remaining case (`E3`, the exemption's exception tail) as recorded work, and it was closed at completion in the owner-approved Task 13 additions (D23). Source: plan, Task 4.
- Deviation (Task 5): the lint skips dangling `.md` symlinks (commit eb5a18b), because an editor lock file blocked every commit. Source: plan, Task 5.
- Deviation (Task 7): `→ dropped:` is written only on the owner's word (D21). The spec and this step also allowed it with the landed work cited. The owner removed that exception at completion. Source: plan, Task 7.
- Deviation (Task 8): `build/test_runtime_support.py` gained `('skill:brainstorming', 'command:deferred')` in `SOFT_REFERENCES`, because brainstorming now names `/deferred` without running it. Source: plan, Task 8.
- Deviation (Task 8): step 3 no longer spells the tick form. The form moved to the reference's `## Item notes` with a date, `→ done <YYYY-MM-DD> (plan <id>)` (D20). Source: plan, Task 8.
- Deviation (Task 9): the review changed `commands/deferred.md` step 5 so a held-back item is resolved only on the user's word, and `→ dropped:` is written only on the user's word (commit 9057df7). Source: plan, Task 9.
- Deviation (Task 10): the first GREEN run passed 5 of 5 in every case. Its record was corrected for two honesty findings (commit 9e7930f). The final-review fixes changed the texts, so R1-R4 were run again on the final text (commit 21417f8), and the R3 fixture gained the `Aged, carry unused:` line. Both runs are in `specs/red-baseline-backlog-protocol.md`. Source: plan, Task 10.
- Deviation (Task 11): the stats before and after are recorded above. The archive run moved 89 items and held back none. Source: plan, Task 11.
- Deviation (Task 11): the final whole-branch review (after this task) had a fix wave, commits d360bb6, 0e97e03 and aeb16b6. It closed three Codex findings: the archive refuses the same path for `--file` and `--archive`, the hold-back scan keeps paragraph breaks, and code spans are masked by whole backtick runs. Source: plan, Task 11.
- Decision D18 (spec amendment): approve Task 0's amendment. The scan must catch the five B1 instances that carry a deferral phrase; the four phraseless fixtures become `xfail` fixtures that record the limit. Source: plan, `## Decisions`.
- Deferred: 4 items. Source: specs/deferred_items.md, § 74-backlog-protocol.

Closed earlier deferred items:
- "Write the backlog-protocol spec: deferrals outside this file get lost, and the file" (deferred by audit-3-10-26 routing).
- "Cosmetic wraps from plan 73's task reviews (Minors M11 and M13): the "Order matters"" (deferred by 73-reviewer-and-planning-contract).
```

### Step 5: `deferred` on 2026-10-05

Command: `uv run skills/writing-plans/scripts/history_entry.py deferred --date 2026-10-05`

| Check | Expected | Result |
|---|---|---|
| Exit code | 0 | 0 |
| Heading | `## /deferred — 2026-10-05` | the same, once, on line 1 |
| Item lines (`grep -c '^- '`) | 47 | 47 |

Step 5 meets every expected value. The output has 50 lines: the heading, one blank line, the
`Closed deferred items:` list heading and the 47 item lines. The one other 2026-10-05 close sits in
`specs/completed/deferred_items.md`, which the script does not read.

The real-data check is met: Steps 3, 4 and 5 each print what the plan expects.
