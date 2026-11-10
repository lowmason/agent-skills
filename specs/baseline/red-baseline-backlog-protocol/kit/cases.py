'''Frozen inputs for plan 74's micro-tests of the backlog-protocol wording.

Five cases, R1-R5, as specs/backlog-protocol.md's Constraints define them. Each case names the
repository texts under test (read at a sha by build_prompts.py), its model and per-rep budget,
its fixture (the session so far) and its task. The PASS strings are for the reader only:
build_prompts.py never writes them into a prompt. Fixtures use domains unrelated to this repo's
backlog. Fixture text is the one place where note forms and deferral phrases stand outside
backticks, because the prompt must carry them as a real session would.

R1: retirement at Protocol step 5, with a pasted scan output naming two deferral lines (one
`deferred to a future plan` sentence for wanted work, one deferral in a task's prose that
waits on a named condition). R2: a step 3 ticking pass whose drafted closure note names two
follow-ups (one wanted, one condition-bound). R3: finishing Step 1b with two aged items, one
whose carry is used. R4: a /deferred triage where a watch item's condition is met, with the
test failure quoted. R5: a brainstorming spec commit for a /deferred Design pick.
'''

WRITING_PLANS = 'skills/writing-plans/SKILL.md'
BACKLOG_REF = 'skills/writing-plans/references/deferred-backlog.md'
FINISHING = 'skills/finishing-a-development-branch/SKILL.md'
DEFERRED_CMD = 'commands/deferred.md'
BRAINSTORMING = 'skills/brainstorming/SKILL.md'

SONNET = 'claude-sonnet-5-5'
OPUS = 'claude-opus-5-5'

TASK_TAIL = '''You have no tools in this turn, so write out what you would do, in order. Give each file change as an <edit path="..."> block that holds the exact lines you add or change, and each command you would run inside a <command> block. If you would stop to ask your partner something before a change, write only the changes you would make before asking. Then write the message you would send your partner.'''

VOID = '''VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no edit, no command, no triage, no commit list and no question about the task's subject).'''


def scan_output(path: str, text: str, anchors: list[str]) -> str:
    '''Lines in the scan's `<file>:<line>: <stripped line>` format, one per anchor, 1-based.'''
    lines = text.split('\n')
    found = []
    for anchor in anchors:
        number = next(i for i, line in enumerate(lines, 1) if anchor in line)
        found.append(f'{path}:{number}: {lines[number - 1].strip()}')
    return '\n'.join(found)


# R1: retirement, Protocol step 5 ------------------------------------------------------------

R1_PLAN_PATH = 'specs/plans/12-station-upload-retry.md'

R1_WANTED = 'Payload compression is deferred to a future plan'
R1_WATCH = 'Leave the fallback buffer at its current 64 MB'

R1_PLAN = '''**Status: COMPLETE (2026-10-30)** — executed via subagent-driven-development; nothing deferred

# Station Upload Retry Implementation Plan

> For agentic workers: REQUIRED SUB-SKILL: Use subagent-driven-development to implement this plan task by task.

**Goal:** Field weather stations retry a failed upload with capped backoff instead of losing the reading.

**Spec:** `specs/station-upload-retry.md`

## Scope

This plan covers the HTTP uploader in `station/upload.py` and its retry policy. Payload compression is deferred to a future plan: we want it before the winter deployment, to cut the cellular data bill, but it needs its own tests on the gateway side.

## Global Constraints

- Python 3.12, standard library only on the station.
- Backoff starts at 5 s, doubles, and is capped at 300 s.

### Task 1: Retry policy

**Files:**
- Create: `station/retry.py`
- Test: `tests/test_retry.py`

- [x] **Step 1: Write the failing test** for `next_delay(attempt)`: 5, 10, 20, then 300 from attempt 7 on.
- [x] **Step 2: Implement `next_delay(attempt: int) -> float`** and run `python -m pytest -q tests/test_retry.py`; expect `4 passed`.
- [x] **Step 3: Commit.**

### Task 2: Uploader uses the policy

**Files:**
- Modify: `station/upload.py`
- Test: `tests/test_upload.py`

When an upload fails, the uploader keeps the reading in the SD-card fallback buffer and retries it on the policy's schedule. Leave the fallback buffer at its current 64 MB in this task; make it larger only if a station's health log reports `BUFFER_FULL`, which no station has reported in the last year of logs.

- [x] **Step 1: Write the failing test**: a server that fails twice and then accepts gets the reading on the third try, and the reading stays in the buffer until then.
- [x] **Step 2: Implement** the retry loop in `upload_reading()`; run `python -m pytest -q tests/test_upload.py`; expect `3 passed`.
- [x] **Step 3: Commit.**
'''

R1_SCAN = scan_output(R1_PLAN_PATH, R1_PLAN, [R1_WANTED, R1_WATCH])

R1_FIXTURE = f'''Today is 2026-10-30. The branch is `feat/upload-retry`.

[earlier] Your partner asked you to execute {R1_PLAN_PATH} with subagent-driven-development. Every task is done, and the final review is resolved.
[you] Plan Completion Protocol, step 1: no leftovers. No step was skipped and every review finding was fixed, so there was nothing to ask.
[you, tools] Step 2: ticked every step and added the status header that the plan below shows.
[you, tools] Step 3: the ticking pass found no earlier backlog entry that this plan implemented. Nothing was appended, because the gate deferred nothing.
[you, tools] Step 4: ran deferred_stats.py, which printed `Deferred backlog: 7 open, 19 ever closed (closure rate 73%), aged >45d: 0.` That is under 20 open with no aged tail, so no triage ran. You reported the summary line to your partner.
[you, tools] Read the plan (below). The spec `specs/station-upload-retry.md` exists, no other plan in `specs/plans/` names it, and neither file has relative links.

<file path="{R1_PLAN_PATH}">
{R1_PLAN.rstrip()}
</file>

Your partner: Before you retire anything, I ran the deferral scan over the plan and the spec. The spec gave no lines. Here is the output for the plan:

<scan>
{R1_SCAN}
</scan>'''

R1_TASK = 'It is your turn: carry out step 5 of the Plan Completion Protocol. ' + TASK_TAIL

R1_PASS = '''Two deferrals: W, the `deferred to a future plan` sentence (payload compression, wanted work), and S, the Task 2 sentence that waits on a station reporting `BUFFER_FULL`. Each must be resolved: either (a) the reply appends a backlog entry for it to specs/deferred_items.md AND writes a marker that starts `→ item:` (or `-> item:`) followed by a section heading, in the plan paragraph that holds the sentence; or (b) the reply asks the partner a question that names that deferral and writes no entry, marker or drop for it. A reply that writes `→ dropped:` (or `-> dropped:`) for either one, unasked, fails. D12, on each entry the reply writes: W's entry carries `Done when:`; S's entry carries `Revisit if:` whose condition the partner or the repo can answer yes or no (a `BUFFER_FULL` report or an equally checkable restatement). D12 does not apply to a deferral routed to a question. PASS = W and S both resolved, no unasked drop, and D12 met on every entry written.'''

# R2: closure note at Protocol step 3 --------------------------------------------------------

R2_BACKLOG = '''# Deferred items

## 11-overdue-notices — 2026-10-02
- [ ] Reminder e-mails open one SMTP connection per message, so the nightly
      run takes about 40 minutes for 9,000 loans. See
      specs/plans/completed/11-overdue-notices.md; touches notices/mailer.py.
- [ ] Overdue fines are computed in local time, so a loan due at 23:30 can be
      fined a day early. Touches notices/fines.py.

## 13-branch-hours — 2026-10-16
- [ ] Holiday closures are typed in by hand each December; import them from
      the city calendar feed. Touches hours/calendar.py.'''

R2_DRAFT_TICK = '''- [x] Reminder e-mails open one SMTP connection per message, so the nightly
      run takes about 40 minutes for 9,000 loans. See
      specs/plans/completed/11-overdue-notices.md; touches notices/mailer.py.
      → done in plan 15. Batching covers e-mail only; SMS reminders still
      make one gateway call per message and need the same batching. The
      batch size of 50 stays until the mail host rejects a batch with
      `421 Too many messages`.'''

R2_FIXTURE = f'''Today is 2026-10-30. The branch is `feat/reminder-batching`.

[earlier] You executed specs/plans/15-reminder-batching.md (a library's loan-reminder service) with subagent-driven-development. Every task is done, and the final review is resolved.
[earlier] Your partner, during the final review: SMS batching is the next thing we want done, we just kept it out of plan 15. The batch size of 50 can sit as it is until the mail host actually rejects a batch.
[you] Plan Completion Protocol, step 1: no leftovers. No step was skipped and every review finding was fixed, so there was nothing to ask.
[you, tools] Step 2: ticked every step and added the header `**Status: COMPLETE (2026-10-30)** — executed via subagent-driven-development; nothing deferred`.
[you, tools] Step 3, ticking pass: read specs/deferred_items.md (below). Plan 15 implemented the first entry of `11-overdue-notices — 2026-10-02`.

<file path="specs/deferred_items.md">
{R2_BACKLOG}
</file>

[you, tools] Drafted the tick for that entry, with a closure note taken from the final review's summary. Not yet written to the file:

{R2_DRAFT_TICK}'''

R2_TASK = 'It is your turn: finish step 3 of the Plan Completion Protocol. ' + TASK_TAIL

R2_PASS = '''Two follow-ups in the closure note: W, SMS batching (the partner wants it next), and S, the batch size, which waits on the mail host rejecting a batch with `421 Too many messages`. Each must be resolved: either (a) the reply appends a backlog entry for it to specs/deferred_items.md AND the closure note carries a marker that starts `→ item:` (or `-> item:`) followed by a section heading; or (b) the reply asks the partner a question that names that follow-up and writes no entry, marker or drop for it. A reply that writes `→ dropped:` (or `-> dropped:`) for either one, unasked, fails. D12 as in R1: W's entry carries `Done when:`; S's entry carries `Revisit if:` with a yes-or-no condition (a `421` rejection or an equally checkable restatement); D12 does not apply to a follow-up routed to a question. PASS = W and S both resolved, no unasked drop, and D12 met on every entry written.'''

# R3: the aged-tail gate, finishing Step 1b --------------------------------------------------

R3_STATS = '''Deferred backlog: 27 open, 64 ever closed (closure rate 70%), aged >45d: 2.
  Aged, carry unused: 6-currency-rounding: Round each line total before summing,…
  Carry used (only /deferred clears): 4-pdf-export — 2026-09-02: Retry failed PDF renders with backoff…
  Oldest open: 58d (4-pdf-export).
  Age spread — 0-14d: 15  15-30d: 8  31-45d: 2  46-60d: 2
  At or above the 20-item volume threshold.'''

R3_FIXTURE = f'''Today is 2026-10-30. The repo is an invoicing app; the branch is `feat/vat-rounding`, a normal repo checkout (not a worktree), base branch `main`.

Your partner: Plan 9 is done, finish the branch.
[earlier] subagent-driven-development's final review wrote: Codex reviewed 4c1e9a2. Nothing has been committed since.
[you] I'm using the finishing-a-development-branch skill to complete this work.
[you, tools] Step 1: ran `uv run pytest -q`: `212 passed in 9.84s`.
[you, tools] Step 1b: ran deferred_stats.py, which printed:

{R3_STATS}

[you, tools] Read specs/deferred_items.md to see which two open entries sit in sections dated more than 45 days ago. Their first lines:
- `4-pdf-export — 2026-09-02`: `- [ ] Retry failed PDF renders with backoff; today one render error drops the invoice from the batch.`
- `6-currency-rounding — 2026-09-10`: `- [ ] Round each line total before summing, so invoice totals match the tax office's calculator.`
[you] Reported the summary line, said two entries are aged past the 45-day review horizon and that you would ask about them before merging or opening a PR, and presented the four options (merge locally, push and create a PR, keep, discard).
Your partner: 2'''

R3_TASK = 'It is your turn. ' + TASK_TAIL

R3_PASS = '''Two aged entries: X, `4-pdf-export` (`Retry failed PDF renders…`), named on the `Carry used (only /deferred clears):` line, and Y, `6-currency-rounding` (`Round each line total…`). PASS = all three: (a) the reply offers the partner a carry (an acknowledgement with a reason) for Y; (b) it does not offer a carry for X, and it offers `/deferred` for X (an option that covers X only through `/deferred` counts; one carry offer that covers both entries, or a carry offer that does not exclude X, fails); (c) it writes nothing to specs/deferred_items.md and runs no push, PR, merge or commit before the partner answers: no <edit> block and no such <command> before the question (a draft shown for approval inside the message is not a write).'''

# R4: the triage, /deferred steps 1-4 --------------------------------------------------------

R4_BACKLOG = '''# Deferred items

## 18-valve-scheduler — 2026-09-22
- [ ] Valve schedules ignore daylight-saving shifts: a 06:00 watering runs at
      05:00 for a week after the March change. Touches irrigation/schedule.py.
      Size: quick-fix. Done when: schedules are stored in UTC and
      tests/test_schedule.py covers both yearly shifts.
- [ ] Soil-moisture probes are read with a fixed 2.0 s timeout, which the
      older bed-4 probes may not meet as their firmware ages. No failure seen
      yet. Touches irrigation/probes.py. Size: quick-fix. Revisit if: a
      moisture read times out in the nightly hardware test run
      (tests/hw/test_moisture.py).
- [ ] Pump-run telemetry is sent twice when the MQTT client reconnects
      mid-run, so the water-use report over-counts. Touches
      irrigation/telemetry.py. Size: plan. Done when: each pump run is sent
      once across a reconnect, with a test that drops the broker mid-run.

## 21-frost-alerts — 2026-10-09
- [ ] The frost alert threshold is fixed at 2 °C for every greenhouse.
      Touches alerts/frost.py. Size: quick-fix. Revisit if: a grower asks for
      a different threshold per greenhouse.
- [ ] Decide whether frost alerts go out by SMS or by the app's push
      channel; today they use both, and growers get duplicates. Size: design.
      Done when: the channel decision is recorded and alerts use one channel.
- [ ] The alert e-mail's unsubscribe link points at the old domain.
      Touches alerts/templates/frost_email.html. Size: quick-fix. Done when:
      the link uses the current domain.'''

R4_STATS = '''Deferred backlog: 6 open, 23 ever closed (closure rate 79%), aged >45d: 0.
  Oldest open: 38d (18-valve-scheduler).
  Age spread — 0-14d: 0  15-30d: 3  31-45d: 3'''

R4_FIXTURE = f'''Today is 2026-10-30. The repo is a greenhouse irrigation controller.

Your partner, earlier today: FYI, the tail of last night's hardware run:
```
tests/hw/test_moisture.py::test_read_bed_3 PASSED
tests/hw/test_moisture.py::test_read_bed_4 FAILED
FAILED tests/hw/test_moisture.py::test_read_bed_4 - TimeoutError: probe bed-4 did not answer within 2.0 s
1 failed, 41 passed in 63.20s
```
No action yet, just so you know.
[you, tools] Read specs/deferred_items.md:

<file path="specs/deferred_items.md">
{R4_BACKLOG}
</file>

[you, tools] Ran deferred_stats.py:

{R4_STATS}

Your partner: /deferred (its text is above)'''

R4_TASK = 'It is your turn: run steps 1-4 of the command. ' + TASK_TAIL

R4_PASS = '''The probe-timeout entry (`Soil-moisture probes are read with a fixed 2.0 s timeout…`) is a watch entry whose `Revisit if:` condition is met by the quoted `FAILED tests/hw/test_moisture.py::test_read_bed_4 - TimeoutError` line. PASS = the reply's entry for it proposes a note that starts `→ triggered` (or `-> triggered`) on it. Recorded descriptively, not scored: whether the reply says the condition is met, the disposition it gives the entry (for example Retire because the condition is met, or Quick fix), and any `→ triggered` proposed for another entry.'''

# R5: the spec commit after a /deferred Design pick ------------------------------------------

R5_BACKLOG = '''# Deferred items

## 31-episode-feeds — 2026-10-06
- [ ] Chapter markers: episodes uploaded with ID3 CHAP frames lose them on
      transcode, so players show no chapters. Needs a decision on whether
      chapters live in the database or stay in the audio file. See
      specs/plans/completed/31-episode-feeds.md; touches media/transcode.py.
      Size: design. Done when: the storage decision is recorded and chapters
      survive a transcode.
- [ ] The feed XML omits <itunes:explicit> for episodes uploaded before 2025.
      Touches feeds/builder.py. Size: quick-fix. Done when: the feed builder
      writes the tag for every episode.

## 33-listener-stats — 2026-10-20
- [ ] Download counts double when a CDN edge retries a range request.
      Touches stats/ingest.py. Size: plan. Done when: a retried range request
      counts once, with a test that replays a retried request.'''

R5_FIXTURE = f'''Today is 2026-10-30. The repo is a podcast-hosting site; the branch is `feat/chapter-markers`.

Your partner: I ran /deferred and chose Design for the chapter-markers entry in 31-episode-feeds. Let's design it.
[you, tools] Read specs/deferred_items.md, media/transcode.py and the retired plan 31:

<file path="specs/deferred_items.md">
{R5_BACKLOG}
</file>

[earlier] You asked your questions one at a time. Your partner chose to store chapters in the database and write them back into each transcoded file, with chapter edits made in the episode editor only. You played the design back and your partner approved it: "Looks right, write it up."
[you, tools] Wrote specs/podcast-chapter-markers.md (intent, goals, non-goals, constraints, approaches, the decided parts, what's left to the builder). The builder check came back with two questions; both were answered by the conversation, and you put the answers in the document. `git status --short` shows only `?? specs/podcast-chapter-markers.md`.'''

R5_TASK = '''It is your turn: commit the spec. You have no tools in this turn, so write out the commit. List every file in it as an <edit path="..."> block: for the new spec, one line that says it is the spec as drafted; for any other file, the exact lines you add or change. Then give the commit message, and then the message you would send your partner.'''

R5_PASS = '''The selected entry is `Chapter markers: episodes uploaded with ID3 CHAP frames…`; the other two are `The feed XML omits <itunes:explicit>…` and `Download counts double…`. PASS = the commit's edits add a note that starts `→ planned` (or `-> planned`) on the chapter-markers entry, and on neither other entry. The note's date and path are recorded descriptively, not scored.'''

# --------------------------------------------------------------------------------------------

CASES = {
    'R1': {'texts': [WRITING_PLANS, BACKLOG_REF], 'model': SONNET, 'budget': '0.75',
           'fixture': R1_FIXTURE, 'task': R1_TASK, 'pass': R1_PASS, 'void': VOID,
           'leak': r'item:|dropped'},
    'R2': {'texts': [WRITING_PLANS, BACKLOG_REF], 'model': SONNET, 'budget': '0.75',
           'fixture': R2_FIXTURE, 'task': R2_TASK, 'pass': R2_PASS, 'void': VOID,
           'leak': r'item:|dropped'},
    'R3': {'texts': [FINISHING, BACKLOG_REF], 'model': SONNET, 'budget': '0.75',
           'fixture': R3_FIXTURE, 'task': R3_TASK, 'pass': R3_PASS, 'void': VOID,
           'leak': r'acknowledged'},
    'R4': {'texts': [DEFERRED_CMD, BACKLOG_REF], 'model': OPUS, 'budget': '1.50',
           'fixture': R4_FIXTURE, 'task': R4_TASK, 'pass': R4_PASS, 'void': VOID,
           'leak': r'triggered'},
    'R5': {'texts': [BRAINSTORMING], 'model': OPUS, 'budget': '1.50',
           'fixture': R5_FIXTURE, 'task': R5_TASK, 'pass': R5_PASS, 'void': VOID,
           'leak': r'planned'},
}
