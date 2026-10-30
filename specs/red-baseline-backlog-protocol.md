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
context, no memory). `show_reps.py`: one turn, no extra iterations, one model, cost $0.008.

`run_reps.sh` writes `--output-format json`, which does not carry the init record, so that half of
plan 73's check was not made during the control runs. The controller made it afterward with one
probe on the same Claude Code 2.1.312, the same model, the same flags and the same
`isolation_probe.txt`, with `--output-format stream-json --verbose` added (cost $0.003). Init record:
`tools` empty, `output_style` `default`, `mcp_servers` empty, plugins the three built-in ones, skills
and agents the built-in ones only (none of the user's personal skills or agents). The reply was
again all five lines `NO`. The isolation holds on both of plan 73's checks. A later Claude Code
version needs both checks again, and the init check needs the stream-json form.

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

Run 2026-10-30 on Claude Code 2.1.312, the same version as the control, from the texts at
`9057df7` (HEAD after Task 9). Prompts: `build_prompts.py 9057df7 /tmp/plan74-green`.
`MANIFEST.txt` names `arm 9057df7`. Outside the texts under test, every green prompt is
byte-identical to its control prompt: the kit is unchanged since `fce05d2`, and the green leak
view is identical to the control's leak view. The leak grep of the `## Leak check` section, repeated on the leak view, printed no line
and `exit=1` for every case, and the supplementary greps also matched nothing. The isolation
probe ran again (`run_reps.sh isolation_probe.txt /tmp/plan74-greenprobe 1 1 claude-sonnet-5-5`):
all five lines `NO`, one turn, no extra iterations, one model, $0.008. The Claude Code version did
not change, so the init-record check was not repeated. The five cases ran at the same time, each
with `run_reps.sh <case>.txt green/<case> 1 5 <model> <budget>`, the models and budgets as in the
control. 25 reps. No rep was VOID (each `show_reps.py` header: no error, one turn, no extra
iterations, one model, and R1-R3 ran on `claude-sonnet-5-5`, R4-R5 on `claude-opus-5-5`). None
wrote a `.err` file, and none was rerun. The scored reps are `rep1`-`rep5` of each case.

Summary: the new wording passes every case 5 of 5, against 0 of 5 for the control, so every
case clears the bar. No case is a ceiling, because the control passed no rep. In R1 and R2 every
rep filed both deferrals as entries with correct closure fields and wrote an `→ item:` marker
that names the new section. In R3 every rep offered the carry for the fresh entry only, and
routed the carry-used entry to `/deferred` alone, with no write before the question. In R4 every
rep proposed an `→ triggered` note on the probe-timeout entry. In R5 every rep added an
`→ planned` note to the chapter-markers entry only. The caveat from "What the control shows"
stands: R2 and R4 discriminate on form, not substance. Their passes show that the new wording
teaches the marker and note forms. They do not show that a loss is caught, because the control
already filed the R2 work and saw the met R4 condition. R1 shares the caveat in part: leave the
marker out of the count and the control filed W with `Done when:` and routed S to a question in
reps 2-5 (4 of 5, against 5 of 5 for the new wording), a ceiling on substance. R4 also depends
on how strictly the note form is read: see the note under "Verdicts under the bar".

| Case | Control passes | New passes | What the new wording did |
|---|---|---|---|
| R1 | 0/5 | 5/5 | Every rep appended entries for W (`Done when:`) and S (`Revisit if:` a `BUFFER_FULL` report) and wrote an `→ item:` marker in each of the two plan paragraphs. |
| R2 | 0/5 | 5/5 | Every rep appended both entries, with D12 met, and put one `→ item:` marker naming the new section in the closure note. |
| R3 | 0/5 | 5/5 | Every rep offered a carry for `6-currency-rounding` only and said only `/deferred` clears `4-pdf-export`. No rep wrote anything before asking. |
| R4 | 0/5 | 5/5 | Every rep said the probe condition was met and proposed an `→ triggered` note on that entry. Every rep kept it under Quick fix. |
| R5 | 0/5 | 5/5 | Every rep added `→ planned 2026-10-30: specs/podcast-chapter-markers.md` to the chapter-markers entry only. |

### R1, new wording

No rep wrote `→ dropped:`. Each rep offered to swap S's marker for `→ dropped:` if the partner
calls the 64 MB decision final, and wrote none. Every rep also changed the status header from
`nothing deferred` to `deferred items in specs/deferred_items.md`. All five replies mention that
the `/tmp` run directory is not a git repository, as in the control.

| Rep | W | S | Verdict | Deciding line |
|---|---|---|---|---|
| 1 | entry + marker | entry + marker | PASS | both plan paragraphs rewritten to end ``→ item: 12-station-upload-retry — 2026-10-30``; S's entry ends ``Revisit if: a station's health log reports `BUFFER_FULL`.`` |
| 2 | entry + marker | entry + marker | PASS | ``Line 13 gains this at its end, on the same paragraph:`` and ``Line 36 gains this at its end``, each with ``→ item: 12-station-upload-retry — 2026-10-30`` |
| 3 | entry + marker | entry + marker | PASS | ``Line 13, append to the end of the line:`` and ``Line 36, append to the end of the line:``, each with ``→ item: 12-station-upload-retry — 2026-10-30`` |
| 4 | entry + marker | entry + marker | PASS | ``Line 13 now ends: `...but it needs its own tests on the gateway side. → item: 12-station-upload-retry — 2026-10-30` `` and the same on line 36 |
| 5 | entry + marker | entry + marker | PASS | lines 13 and 36 replaced whole, each ending ``→ item: 12-station-upload-retry — 2026-10-30`` |

D12: every W entry is `Size: plan` with `Done when:` (for example rep 1: ``Done when: station
uploads are compressed and the gateway-side tests for the compressed payload pass``). Every S
entry is `Size: quick-fix` with ``Revisit if: a station's health log reports `BUFFER_FULL` ``
(rep 2 adds ``(none has in the last year of logs)``, rep 3 writes ``a station health log
reports``). Each condition is one checkable report. No S entry carries `Done when:`.

### R2, new wording

No rep wrote `→ dropped:`. Each rep wrote one marker, ``→ item: 15-reminder-batching —
2026-10-30``, in the closure note of the ticked entry. It names the new section, which holds
both entries, so one marker meets the rule for W and for S. Reps 1, 2, 4 and 5 also changed the
plan's status header from `nothing deferred` to point at the backlog. Rep 3 left it.

| Rep | W | S | Verdict | Deciding line |
|---|---|---|---|---|
| 1 | entry + marker | entry + marker | PASS | the drafted note kept whole, then ``→ item: 15-reminder-batching — 2026-10-30`` on its own line |
| 2 | entry + marker | entry + marker | PASS | the note ends ``` `421 Too many messages`. → item: 15-reminder-batching — 2026-10-30 ``` |
| 3 | entry + marker | entry + marker | PASS | the note cut to ``→ done in plan 15. Batching covers e-mail only; SMS reminders still make one gateway call per message → item: 15-reminder-batching — 2026-10-30`` |
| 4 | entry + marker | entry + marker | PASS | ``→ done 2026-10-30 in plan 15. SMS reminders still make one gateway call per message; the batch size of 50 stays as is. → item: 15-reminder-batching — 2026-10-30`` |
| 5 | entry + marker | entry + marker | PASS | the drafted note kept whole, then ``→ item: 15-reminder-batching — 2026-10-30`` on its own line |

D12: in all five reps W's entry is `Size: plan` with `Done when:` and S's entry is
`Size: quick-fix` with ``Revisit if: the mail host rejects a batch with `421 Too many messages` ``.
Rep 4 wraps the field name across a line break (`Revisit` / `if:`), which is still the field.
Rep 3 removed the batch-size sentence from the closure note. Its marker still names the section
that holds S's entry, so S counts as resolved. Rep 4 added a date to the done note
(`→ done 2026-10-30 in plan 15`).

### R3, new wording

X is `4-pdf-export` (carry used). Y is `6-currency-rounding`. No rep wrote an `<edit>` block or
a `<command>` block, so point 3 holds in all five. Every rep offers Y the choice of `/deferred`
or a carry (``Carry it. Tell me why, and I'll note it on the item.`` or close to it), and lists X
apart.

| Rep | Verdict | Deciding line |
|---|---|---|
| 1 | PASS | ``This 1 already used its one carry. Only `/deferred` clears it:`` |
| 2 | PASS | ``This 1 already used its one carry, so only `/deferred` clears it:`` |
| 3 | PASS | ``This one already used its one carry. Only `/deferred` clears it:`` |
| 4 | PASS | ``This one already used its one carry, so only `/deferred` clears it:`` |
| 5 | PASS | ``This 1 already used its one carry. Only `/deferred` clears it:`` |

Descriptive: reps 1, 3, 4 and 5 show the note they would write after a carry,
``→ acknowledged 2026-10-30 (feat/vat-rounding): <your reason>``. Rep 4 also points out that the
branch's rounding work may already close Y, so `/deferred` could retire it.

### R4, new wording

| Rep | Verdict | Deciding line | Descriptive |
|---|---|---|---|
| 1 | PASS | ``**Proposed `→ triggered 2026-10-30: nightly hardware run failed tests/hw/test_moisture.py::test_read_bed_4 — TimeoutError: probe bed-4 did not answer within 2.0 s`.**`` | condition met: yes; Quick fix; for the frost-threshold entry, ``If so, I'll propose `→ triggered` instead``, a conditional offer only |
| 2 | PASS | ``→ triggered 2026-10-30: nightly hardware run failed tests/hw/test_moisture.py::test_read_bed_4 — TimeoutError: probe bed-4 did not answer within 2.0 s`` | condition met: yes; Quick fix; no `→ triggered` on another entry |
| 3 | PASS | ``**Proposed `→ triggered`:** last night's hardware run failed `tests/hw/test_moisture.py::test_read_bed_4` `` | condition met: yes; Quick fix; bare form, no date or text; a `→ held` on the frost-threshold entry called optional |
| 4 | PASS | ``**Proposed:** `→ triggered 2026-10-30: tests/hw/test_moisture.py::test_read_bed_4 timed out in the 2026-10-29 nightly hardware run (…)` `` | condition met: yes; Quick fix; no `→ triggered` on another entry |
| 5 | PASS | ``**Proposed `→ triggered` (pick to record it)**`` heading the probe-timeout entry | condition met: yes; Quick fix; bare form, no date or text; a `→ held` on the frost-threshold entry called optional |

Reps 3 and 5 write the bare `→ triggered` and give the date and the evidence in prose, not in
the full `→ triggered <YYYY-MM-DD>: <what happened>` form. The frozen rule counts a proposed note
that starts `→ triggered`, so both pass. Under the exact note form from the plan's Global
Constraints, only reps 1, 2 and 4 pass, so R4 would score 3 of 5, below the bar of 4. The owner
rules on which reading stands. Every rep asks the partner to select the note before it is
written. No rep proposes Retire for the entry.

### R5, new wording

| Rep | Verdict | Deciding line |
|---|---|---|
| 1 | PASS | ``→ planned 2026-10-30: specs/podcast-chapter-markers.md`` after ``survive a transcode.`` in the chapter-markers entry; ``No other items change.`` |
| 2 | PASS | ``→ planned 2026-10-30: specs/podcast-chapter-markers.md`` under the chapter-markers entry; ``The `<itunes:explicit>` item and the 33-listener-stats item stay unchanged.`` |
| 3 | PASS | ``→ planned 2026-10-30: specs/podcast-chapter-markers.md`` on ``the chapter-markers item only``; ``The checkbox stays `[ ]`.`` |
| 4 | PASS | the whole chapter-markers entry shown with ``→ planned 2026-10-30: specs/podcast-chapter-markers.md`` as its last line |
| 5 | PASS | the whole chapter-markers entry shown with ``→ planned 2026-10-30: specs/podcast-chapter-markers.md`` as its last line, ``on the chapter-markers item only`` |

Descriptive: every note is dated 2026-10-30 and points at `specs/podcast-chapter-markers.md`.
Every commit message says the entry is marked as planned.

### Verdicts under the bar

| Case | Control passes | New passes | Verdict under the bar | Note |
|---|---|---|---|---|
| R1 | 0/5 | 5/5 | PASS | Mostly form: the control wrote no marker in any rep. On substance alone only rep 1 failed (S left unresolved), so the substance difference is 1 rep, below the bar. The pass shows the marker is taught. |
| R2 | 0/5 | 5/5 | PASS | Form only: the control already filed both pieces of work with D12 met. The pass shows the marker is taught. |
| R3 | 0/5 | 5/5 | PASS | Substance: the control offered one carry for both entries, X included. |
| R4 | 0/5 | 5/5 under the frozen rule | PASS | Form only: the control already saw the met condition and routed the entry to Quick fix. Reps 3 and 5 write the bare `→ triggered`. Under the exact note form R4 scores 3/5, below the bar: the owner rules on which reading stands. |
| R5 | 0/5 | 5/5 | PASS | Substance: the control wrote no state note on the selected entry. |

No case could fail to discriminate on the numbers, because the control passed no rep in any
case. No case missed its bar, so no wording changed after the green runs.

## Spend

| Run | Reps | Spend |
|---|---|---|
| Isolation probe | 1 | $0.01 |
| Isolation probe, init record (stream-json) | 1 | $0.003 |
| Control R1 | 5 | $0.21 |
| Control R2 | 5 | $0.20 |
| Control R3 | 5 | $0.12 |
| Control R4 | 5 | $0.26 |
| Control R5 | 5 | $0.17 |
| Control arm total | 27 | $0.96 |
| Isolation probe, green arm | 1 | $0.008 |
| Green R1 | 5 | $0.290 |
| Green R2 | 5 | $0.216 |
| Green R3 | 5 | $0.141 |
| Green R4 | 5 | $0.328 |
| Green R5 | 5 | $0.178 |
| Green arm total | 26 | $1.16 |
| Kit total | 53 | $2.12 |

The control arm stayed far below its $20 stop. The kit stop is $40, and the kit total is far
below it. The totals are exact sums of the runs' `total_cost_usd` (control $0.963, green
$1.160, kit $2.123), rounded once. Each row is rounded on its own: the green rows to a tenth of
a cent, so they sum to within a tenth of a cent of their total, and the control rows from Task 1
to the cent, so they differ from their total by about a cent.
