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

Run 2026-10-30 on Claude Code 2.1.312, after the reading rules were committed (`fce05d2`).
Prompts: `build_prompts.py f3a4af4 /tmp/plan74-control`. The five cases ran at the same time,
each with `run_reps.sh <case>.txt control/<case> 1 5 <model> <budget>`. 25 reps. No rep was
VOID (each `show_reps.py` header: no error, one turn, no extra iterations, one model), none
wrote a `.err` file, and none was rerun. The scored reps are `rep1`-`rep5` of each case.

All five R1 replies and R2 rep 5 mention that their `/tmp` run directory is not a git
repository, and plan around it. That touches no pass rule.

| Case | Control passes | What the control did |
|---|---|---|
| R1 | 0/5 | No rep wrote an `→ item:` marker. Reps 2-5 appended an entry for W with `Done when:` and offered S as a watch entry. Rep 1 offered W and gave S nothing. |
| R2 | 0/5 | Every rep appended both pieces of open work as entries, with D12 met, and cut them out of the closure note. No rep wrote an `→ item:` marker. |
| R3 | 0/5 | Every rep offered one carry covering both aged entries. Reps 2-4 noted the `Carry used` line but still offered the carry for both. No rep wrote anything. |
| R4 | 0/5 | Every rep said the probe entry's condition was met and routed it to Quick fix. No rep proposed an `→ triggered` note. |
| R5 | 0/5 | No rep wrote an `→ planned` note. Reps 1-4 left the backlog unchanged. Rep 5 added a plain pointer line to the chapter-markers entry only. |

### R1

W is the `deferred to a future plan` sentence (payload compression). S is the `BUFFER_FULL`
sentence. No rep wrote `→ dropped:`.

| Rep | W | S | Verdict | Deciding line |
|---|---|---|---|---|
| 1 | question | unresolved | FAIL | S: ``It has no open work, so there is nothing to log.`` (W: ``If you want it tracked, I can add a `specs/deferred_items.md` section``) |
| 2 | entry, no marker | question | FAIL | W's entry has ``Size: plan. Done when: compressed uploads land with gateway-side tests`` and the plan edit changes only the status header |
| 3 | entry, no marker | question | FAIL | W's entry has ``Size: plan. Done when: uploads are compressed end to end``; the plan edits are the status header and the `Spec:` line |
| 4 | entry, no marker | question | FAIL | W's entry has ``Size: plan. Done when: compressed uploads are accepted by the gateway``; no marker in the Scope paragraph |
| 5 | entry, no marker | question | FAIL | W's entry has ``Size: plan. Done when: compressed uploads are accepted by the gateway``; no marker in the Scope paragraph |

D12, descriptive: every W entry written (reps 2-5) carries `Done when:`. Each S question
(reps 2-5) offers a ``Revisit if: a station health log reports BUFFER_FULL`` entry, which would
meet D12 if written.

### R2

W is SMS batching. S is the batch size and the `421 Too many messages` rejection. No rep wrote
`→ dropped:`.

| Rep | W | S | Verdict | Deciding line |
|---|---|---|---|---|
| 1 | entry, no marker | entry, no marker | FAIL | tick rewritten to end ``→ done in plan 15``: ``My draft had the SMS and batch-size notes folded into the tick`` |
| 2 | entry, no marker | entry, no marker | FAIL | tick ends ``→ done in plan 15``: ``The drafted closure note would have buried them in a ticked item`` |
| 3 | entry, no marker | entry, no marker | FAIL | tick ends ``→ done in plan 15 (e-mail only; SMS follow-up is in the 15-reminder-batching section below)``, a pointer but not the marker form |
| 4 | entry, no marker | entry, no marker | FAIL | tick ends ``→ done in plan 15``: ``I would not put those two items in the closure note of the ticked entry as drafted`` |
| 5 | entry, no marker | entry, no marker | FAIL | tick ends ``→ done in plan 15``: ``**Tick line:** it should be the pointer only`` |

D12, descriptive: in all five reps W's entry carries `Done when:` and S's entry carries
``Revisit if: the mail host rejects a batch with `421 Too many messages` ``. Every rep also changed
the plan's status header from `nothing deferred` to point at the backlog.

### R3

X is `4-pdf-export` (carry used). Y is `6-currency-rounding`. No rep wrote an edit or ran a
command before asking, so point 3 holds in all five. Every rep fails point 2.

| Rep | Verdict | Deciding line |
|---|---|---|
| 1 | FAIL | ``2. Acknowledge and carry them. Tell me why, and I'll log it under `## Aged-backlog acknowledgements` `` |
| 2 | FAIL | ``2. Acknowledge and carry them.`` then ``So option 2 may not clear that item.`` |
| 3 | FAIL | ``2. Acknowledge and carry them. Tell me why, and I'll log it`` after ``An acknowledgement may therefore not settle that item.`` |
| 4 | FAIL | ``2. Acknowledge and carry them — tell me why, and I'll log it`` and ``option 1 is the safer route`` |
| 5 | FAIL | ``2. Acknowledge and carry them. Tell me why, and I'll log it`` |

### R4

| Rep | Verdict | Deciding line | Descriptive |
|---|---|---|---|
| 1 | FAIL | ``**Its `Revisit if:` has now fired.** … so it moves out of Hold`` | condition met: yes; Quick fix; no `→ triggered` anywhere |
| 2 | FAIL | ``**This item's revisit condition fired last night.** … So it moves from watch to its recorded size, quick-fix`` | condition met: yes; Quick fix; no `→ triggered` anywhere |
| 3 | FAIL | ``The bed-4 probe item's trigger fired last night. … So I've moved it from Hold to Quick fix.`` | condition met: yes; Quick fix; it names and rejects the rubric's literal Retire reading; no `→ triggered` anywhere |
| 4 | FAIL | ``This was a watch item, and its trigger has fired`` | condition met: yes; Quick fix; no `→ triggered` anywhere |
| 5 | FAIL | ``This item's `Revisit if:` trigger has fired.`` | condition met: yes; Quick fix; no `→ triggered` anywhere |

### R5

| Rep | Verdict | Deciding line |
|---|---|---|
| 1 | FAIL | ``This commit contains only the spec. I'm leaving `specs/deferred_items.md` unchanged`` |
| 2 | FAIL | ``That's the only file in the commit. I'm leaving `specs/deferred_items.md` unchanged.`` |
| 3 | FAIL | ``No other files are in this commit. I'm leaving `specs/deferred_items.md` unchanged.`` |
| 4 | FAIL | ``I'm leaving `specs/deferred_items.md` unchanged.`` |
| 5 | FAIL | the backlog edit adds ``Design: specs/podcast-chapter-markers.md (2026-10-30).`` on the chapter-markers entry only, not the `→ planned` form |

### What the control shows

- R3 and R5 fail on substance: the current wording offers one carry for every aged entry, and
  it writes nothing on the selected entry.
- R1 fails on substance for S in rep 1 and on the marker in every rep. In reps 2-5 the current
  wording files W and only offers S.
- R2 and R4 fail on the form, not the substance. In R2 the control files both pieces of open work with
  correct closure fields but writes no marker. In R4 it sees the met condition and routes the
  entry to Quick fix but writes no `→ triggered` proposal. On these two cases a new-wording pass
  will show that the form is taught, not that a loss is caught.

## New wording

Task 10 fills this section.

## Spend

| Run | Reps | Spend |
|---|---|---|
| Isolation probe | 1 | $0.01 |
| Control R1 | 5 | $0.21 |
| Control R2 | 5 | $0.20 |
| Control R3 | 5 | $0.12 |
| Control R4 | 5 | $0.26 |
| Control R5 | 5 | $0.17 |
| Total so far | 26 | $0.96 |

The control arm stayed far below its $20 stop. The kit stop is $40.
