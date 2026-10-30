# Plan 74 micro-tests: the backlog-protocol wording

Kit: `specs/red-baseline-backlog-protocol/kit/`. `run_reps.sh` and `isolation_probe.txt` are
copies of plan 73's kit (`specs/red-baseline-reviewer-planning-contract/kit/`). The runner's only
changes are its temp prefix (`/tmp/plan74-rep-`) and the plan number in a comment. `show_reps.py`
is plan 73's helper, unchanged except for the plan number in its docstring. It reads each rep's
VOID flags and cost. `cases.py` holds the five cases. `build_prompts.py <sha> <out-dir>` builds
the prompts at a sha, and `build_prompts.py leakview <out-dir>` builds them with every text under
test replaced by a placeholder, for the leak grep.

Each rep is a fresh `claude -p --tools "" --strict-mcp-config --setting-sources ""` with
`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, run from a new,
empty directory under `/tmp`. 5 reps per case and arm. Every verdict is read by hand from the
full reply.

Arms:
- `control`: the current wording, the texts at `f3a4af4` (HEAD when Task 1 started; no skill,
  command or reference text changed after the plan was approved).
- `green`: the new wording, the texts at HEAD after Task 9 (Task 10 runs it).

Both arms use the same frame, fixture and task. Only the sha of the texts differs.

| Case | Texts under test | Model | Per-rep budget |
|---|---|---|---|
| R1, retirement (Protocol step 5) | writing-plans `SKILL.md` body, `references/deferred-backlog.md` | `claude-sonnet-5-5` | $0.75 |
| R2, closure note (Protocol step 3) | the same | `claude-sonnet-5-5` | $0.75 |
| R3, aged-tail gate (finishing Step 1b) | finishing-a-development-branch `SKILL.md` body, `references/deferred-backlog.md` | `claude-sonnet-5-5` | $0.75 |
| R4, triage (`/deferred` steps 1-4) | `commands/deferred.md` (whole file), `references/deferred-backlog.md` | `claude-opus-5-5` | $1.50 |
| R5, the spec commit after a `/deferred` Design pick | brainstorming `SKILL.md` body | `claude-opus-5-5` | $1.50 |

Spend stop: $20 for the control arm, $40 for the whole kit (owner-approved in the plan).

## Leak check

Command (Task 1 Step 3), on the leak-view prompts, which hold only the frame, the fixture and
the task:

```bash
uv run python specs/red-baseline-backlog-protocol/kit/build_prompts.py leakview /tmp/plan74-leak
cd /tmp/plan74-leak && for c in R1:'item:|dropped' R2:'item:|dropped' R3:'acknowledged' R4:'triggered' R5:'planned'; do k=${c%%:*}; p=${c#*:}; echo "== $k /$p/"; /usr/bin/grep -n -i -E "$p" $k.txt; echo "exit=$?"; done
```

Result on 2026-10-30: every case printed no line and `exit=1` (no match). A supplementary grep
for the pass rules' key terms also matched nothing: `done when|revisit|signal|concrete|marker|wanted`
in R1 and R2, `fired|trigger` in R4, `acknowledg` in R3. R3's pasted stats line
(`Carry used (only /deferred clears): …`) is part of its input and exempt by name. It holds no
leak word anyway. The pass-rule strings in `cases.py` are never written into a prompt.

## Isolation probe

`run_reps.sh isolation_probe.txt /tmp/plan74-probe 1 1 claude-sonnet-5-5` on Claude Code
2.1.312: all five lines `NO` (no `CLAUDE.md` text, no output style, no rule, no SessionStart
context, no memory). `show_reps.py`: one turn, no extra iterations, one model, cost $0.008. The
isolation holds, judged as plan 73's record judges it.

## Reading rules

Registered 2026-10-30, after the probe and before any rep. Fixtures and rules are not edited
after any rep output is seen.

**VOID (every case).** A rep is VOID, rerun with the next free rep number (`rep6` and on) and
not scored, when any of these hold:
- `show_reps.py`'s header for the rep says VOID: a tool or the advisor ran, or the run errored
  or stopped on its budget;
- the JSON is unreadable or its `result` is empty;
- the run timed out or exited without writing JSON;
- the model refuses the task;
- the reply does no part of the task: no edit, no command, no triage, no commit list and no
  question about the task's subject.

A rerun happens only within the spend stop. The scored reps of a case are its first 5 reps that
are not VOID.

**Marker and note forms.** A form counts when the reply writes it literally, with the arrow
`→` or `->`, as an edit or as a proposed edit. A paraphrase (for example "mark it as fired")
does not count as the form.

**A question to the partner** about a deferral counts when it names that deferral (by its
subject) and the reply writes no entry, marker or drop for it.

**R1, retirement.** Two deferrals in the fixture plan:
- W, the `deferred to a future plan` sentence in Scope (payload compression). The fixture says
  `we want it`, so it is wanted work.
- S, the Task 2 sentence that waits on a station's health log reporting `BUFFER_FULL`.

Each must be resolved, in one of two ways:
1. The reply appends a backlog entry for it to `specs/deferred_items.md` AND writes a marker
   that starts `→ item:` (or `-> item:`) followed by a section heading, in the plan paragraph
   that holds the sentence.
2. The reply asks the partner a question about it, as defined above.

One deferral routed each way is allowed. An entry with no marker leaves its deferral
unresolved. A marker with no entry also leaves it unresolved.

Fail: any `→ dropped:` (or `-> dropped:`) that the reply writes for either deferral, unasked.

D12, on each entry the reply writes:
- W's entry carries `Done when:`.
- S's entry carries `Revisit if:`, and its condition can be answered yes or no from the repo or
  the partner: a `BUFFER_FULL` report, or an equally checkable restatement. More conditions
  joined by `or` are allowed only when each one is checkable the same way. A vague condition
  anywhere in it fails D12. A `Done when:` on S as well is recorded, not scored.
- D12 does not apply to a deferral routed to a question.

PASS = W and S both resolved, no unasked drop, and D12 met on every entry written.

**R2, closure note.** Two follow-ups in the drafted closure note:
- W, SMS batching. The partner says it is `the next thing we want done`.
- S, the batch size, which waits on the mail host rejecting a batch with
  `421 Too many messages`.

Each must be resolved, in one of two ways:
1. The reply appends a backlog entry for it to `specs/deferred_items.md` AND the closure note
   carries a marker that starts `→ item:` (or `-> item:`) followed by a section heading.
2. The reply asks the partner a question about it, as defined above.

The rest is as in R1: an entry with no marker, or a marker with no entry, leaves the follow-up
unresolved; any unasked `→ dropped:` fails; D12 as in R1 (W `Done when:`; S `Revisit if:` with a
yes-or-no condition, a `421` rejection or an equally checkable restatement).

PASS = W and S both resolved, no unasked drop, and D12 met on every entry written.

**R3, aged-tail gate.** Two aged entries:
- X, `4-pdf-export` (`Retry failed PDF renders…`), named on the `Carry used (only /deferred clears):`
  line.
- Y, `6-currency-rounding` (`Round each line total…`).

PASS = all three of:
1. The reply offers the partner a carry for Y: carrying it past the gate with a reason, which
   the current wording calls an acknowledgement.
2. It does not offer a carry for X, and it offers `/deferred` for X. A carry offer that covers
   both entries, or one that does not exclude X, fails this point.
3. It writes nothing to `specs/deferred_items.md` and runs no push, PR, merge or commit before
   the partner answers: no `<edit>` block and no such `<command>` ahead of the question. A
   draft shown for approval inside the message is not a write.

**R4, triage.** The probe-timeout entry (`Soil-moisture probes are read with a fixed 2.0 s
timeout…`) is a watch entry. The quoted line
`FAILED tests/hw/test_moisture.py::test_read_bed_4 - TimeoutError` meets its `Revisit if:`
condition.

PASS = the reply's entry for it proposes a note that starts `→ triggered` (or `-> triggered`) on
it.

Recorded, not scored: whether the reply says the condition is met; the disposition it gives the
entry (for example Retire because the condition is met, or Quick fix); any `→ triggered`
proposed for another entry.

**R5, the spec commit.** The selected entry is `Chapter markers: episodes uploaded with ID3 CHAP
frames…`. The other two are `The feed XML omits <itunes:explicit>…` and
`Download counts double…`.

PASS = the commit's edits add a note that starts `→ planned` (or `-> planned`) on the
chapter-markers entry, and on neither other entry. The note's date and path are recorded, not
scored.

**The bar (plan 74, Open for plan review item 3).** A case passes when the new arm passes 4 or
more of 5 reps and the control passes at least 2 fewer. When the control also passes 4 or
more, the case could not discriminate (a ceiling), and the record says so.

## Control

Not run yet.

## New wording

Task 10 fills this section.

## Spend

Isolation probe: $0.01. Control arm: not run yet.
