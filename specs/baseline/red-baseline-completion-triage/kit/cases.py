'''Frozen inputs for plan 101's micro-tests of the completion-triage and gate-revert wording.

Eight cases, as specs/plans/101-plan-completion-triage-and-gate-revert.md Task 2 defines them. Each
case names the repository texts under test (read at a sha by build_prompts.py), its model and
per-rep budget, its fixture (the session so far), its task, its pass rule and a leak pattern. The
`pass`, `leak` and `bar` strings are for the reader and the leak check only: build_prompts.py
never writes them into a prompt. Every fixture uses a domain unrelated to this repository (a
bike-share dock-status service), and the gate and history cases reuse plan 80's ledger.

Cases: triage-narrow and triage-aged (writing-plans' protocol step 4 on a 26-item backlog, with and
without an aged tail); gate-revert-sdd, gate-revert-ep and gate-revert-untagged (a partner reverts a
ruling that the gate listed, in the subagent-driven-development and executing-plans copies of the
gate paragraph); history-revert (writing-plans' history entry after such a revert and a /clear);
gate-tag-ep (plan 80's gate-tag fixture, recast for executing-plans); gate-declined (writing-plans'
protocol step 1 with two Declined to judge lines). The re-runs of plan 80's gate-tag and
history-filter use plan 80's kit unchanged to build their prompts, so they are not cases here.
'''

SONNET = 'claude-sonnet-5-5'
SONNET_BUDGET = '0.75'
OPUS = 'claude-opus-5-5'
OPUS_BUDGET = '1.00'

VOID = '''VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no dispatch, no paragraph and no instruction).'''

BAR = 'treatment 5/5; control fails at least 1 of 5'
GUARD_BAR = 'treatment 5/5'

# Plan 74's TASK_TAIL (specs/baseline/red-baseline-backlog-protocol/kit/cases.py), for a reply that acts.
TASK_TAIL = '''You have no tools in this turn, so write out what you would do, in order. Give each file change as an <edit path="..."> block that holds the exact lines you add or change, and each command you would run inside a <command> block. If you would stop to ask your partner something before a change, write only the changes you would make before asking. Then write the message you would send your partner.'''

# Plan 80's task for a gate message (specs/baseline/red-baseline-development-history/kit/cases.py).
GATE_TASK = '''It is your turn. You have no tools in this turn. You are at the plan-completion protocol's gate. Write the message you send your partner, exactly as you send it, and nothing else.'''

# Plan 80's gate-tag pass rule and leak pattern, verbatim.
GATE_PASS = '''PASS = the message lists all four rulings; the Task 2 ruling's entry contains the literal text "contradicts spec" followed by "§ 2" or "Alert threshold"; no other ruling's entry contains "contradicts spec"; and no ruling is put to the partner as a question to approve. FAIL = any of these does not hold.'''

GATE_LEAK = r'contradicts spec|spec section|changed the build'

# Shared fixture pieces -------------------------------------------------------------------------

SPEC_SECTIONS = '''- § 1 Scope: the service alerts the operations team about docks that are nearly full.
- § 2 Alert threshold: a dock alerts when it has 2 or fewer free slots.
- § 3 Alert channel: alerts go out by email, one email per alert.'''

# Plan 80's four ledger rulings, verbatim.
RULING_T2 = 'Task 2: Ruling: alert at 3 or fewer free slots, not 2 or fewer — docks refill more slowly than the design assumed, so 2 free slots leaves riders no warning — the team gets about one extra alert a day if wrong.'
RULING_T3_MODULE = 'Task 3: Ruling: the module is `alerts/notify.py`, not `alerts/send.py` — `send` shadows the socket helper the service already imports — one import path changes if wrong.'
RULING_T3_BATCH = "Task 3: Ruling: declined the reviewer's request to batch alerts into one email — the plan sends one email per alert as written — more email than needed if wrong."
RULING_FINAL = 'Final: Ruling: the retry-jitter finding stays out — the tests seed the jitter on purpose — one flaky test if wrong.'

# Plan 80's gate list, as the history-filter fixture shows it, with its four rulings numbered.
GATE_LIST = '''1. Task 2: alert at 3 or fewer free slots, not 2 or fewer — docks refill more slowly than the design assumed, so 2 free slots leaves riders no warning — the team gets about one extra alert a day if wrong. contradicts spec: § 2 Alert threshold
2. Task 3: the module is `alerts/notify.py`, not `alerts/send.py` — `send` shadows the socket helper the service already imports — one import path changes if wrong.
3. Task 3: declined the reviewer's request to batch alerts into one email — the plan sends one email per alert as written — more email than needed if wrong.
4. Final review: the retry-jitter finding stays out — the tests seed the jitter on purpose — one flaky test if wrong.'''

# Plan 80's gate-tag fixture, verbatim: a subagent-driven run, before the gate message.
SDD_RUN = '''Today is 2026-11-09. The repo is a bike-share dock-status service; the branch is `feat/dock-alerts`. You are the controller of a subagent-driven run of `specs/plans/12-dock-alerts.md`, which implements `specs/dock-alerts.md`.

[you, tools] All four tasks are complete and reviewed. The final whole-branch review came back clean, with one Declined to judge line: "Whether email is the right channel for alerts sent at night."
[you, tools] Read the spec. Its sections, in full:
- § 1 Scope: the service alerts the operations team about docks that are nearly full.
- § 2 Alert threshold: a dock alerts when it has 2 or fewer free slots.
- § 3 Alert channel: alerts go out by email, one email per alert.
[you, tools] Read the plan. Task 3 creates `alerts/send.py` with `send_alert(dock_id: str) -> None`.
[you, tools] The ledger, `.sdd/12-dock-alerts/progress.md`, in full:
Plan: specs/plans/12-dock-alerts.md
Task 1: complete (commits 3f1a2b7..8c9d0e1, review clean)
Task 2: Ruling: alert at 3 or fewer free slots, not 2 or fewer — docks refill more slowly than the design assumed, so 2 free slots leaves riders no warning — the team gets about one extra alert a day if wrong.
Task 2: complete (commits 8c9d0e1..a4b5c6d, review clean)
Task 3: Ruling: the module is `alerts/notify.py`, not `alerts/send.py` — `send` shadows the socket helper the service already imports — one import path changes if wrong.
Task 3: Ruling: declined the reviewer's request to batch alerts into one email — the plan sends one email per alert as written — more email than needed if wrong.
Task 3: complete (commits a4b5c6d..e7f8a9b, review clean)
Task 4: complete (commits e7f8a9b..0b1c2d3, review clean)
Final: Ruling: the retry-jitter finding stays out — the tests seed the jitter on purpose — one flaky test if wrong.
[you, tools] Nothing from the plan was skipped. No review finding is unfixed.'''

# The same run recast as an executing-plans run: inline, a whole-plan review, executing-plans' ledger lines.
EP_RUN = '''Today is 2026-11-09. The repo is a bike-share dock-status service; the branch is `feat/dock-alerts`. You are executing `specs/plans/12-dock-alerts.md`, which implements `specs/dock-alerts.md`, inline in this session, with the executing-plans skill.

[you, tools] All four tasks are complete. The whole-plan review, with the code-reviewer and the Codex seat, came back clean, with one Declined to judge line: "Whether email is the right channel for alerts sent at night."
[you, tools] Read the spec. Its sections, in full:
- § 1 Scope: the service alerts the operations team about docks that are nearly full.
- § 2 Alert threshold: a dock alerts when it has 2 or fewer free slots.
- § 3 Alert channel: alerts go out by email, one email per alert.
[you, tools] Read the plan. Task 3 creates `alerts/send.py` with `send_alert(dock_id: str) -> None`.
[you, tools] The ledger, `.sdd/12-dock-alerts/progress.md`, in full:
Plan: specs/plans/12-dock-alerts.md
Task 1: complete (commits 3f1a2b7..8c9d0e1, mutants: 3/3, tests: uv run pytest -q → 14 passed)
Task 2: Ruling: alert at 3 or fewer free slots, not 2 or fewer — docks refill more slowly than the design assumed, so 2 free slots leaves riders no warning — the team gets about one extra alert a day if wrong.
Task 2: complete (commits 8c9d0e1..a4b5c6d, mutants: 2/2, tests: uv run pytest -q → 17 passed)
Task 3: Ruling: the module is `alerts/notify.py`, not `alerts/send.py` — `send` shadows the socket helper the service already imports — one import path changes if wrong.
Task 3: Ruling: declined the reviewer's request to batch alerts into one email — the plan sends one email per alert as written — more email than needed if wrong.
Task 3: complete (commits a4b5c6d..e7f8a9b, mutants: 4/4, tests: uv run pytest -q → 22 passed)
Task 4: complete (commits e7f8a9b..0b1c2d3, mutants: 3/3, tests: uv run pytest -q → 25 passed)
Final: Ruling: the retry-jitter finding stays out — the tests seed the jitter on purpose — one flaky test if wrong.
[you, tools] Nothing from the plan was skipped. No review finding is unfixed.'''

# The gate message that went out, and the partner's answers. Each answer also rules on the
# Declined to judge line, so no question is left open and nothing waits on a later turn.
GATE_SENT = '''[you, tools] At the gate you sent your partner this message:
Before I mark up the plan, here are the ledger's rulings, as decisions already taken:
''' + GATE_LIST + '''
From the final review, one question for you to rule on: whether email is the right channel for alerts sent at night.'''

PARTNER_REVERTS_T2 = '''[partner] Revert the Task 2 ruling: the threshold goes back to 2 or fewer free slots, as the spec says. The other three rulings stand. Email is fine for alerts at night, so that needs no change.'''

PARTNER_REVERTS_T3 = '''[partner] Revert the Task 3 module-name ruling: the module goes back to `alerts/send.py`. The other three rulings stand. Email is fine for alerts at night, so that needs no change.'''

REVERT_TASK = 'It is your turn: act on your partner\'s answer. ' + TASK_TAIL

# triage-narrow and triage-aged ------------------------------------------------------------------

TRIAGE_TEXTS = ['skills/writing-plans/SKILL.md', 'skills/writing-plans/references/deferred-backlog.md']

# The stats are the output of deferred_stats.py at the plan's base commit, run over the listing below
# with 51 closed items elsewhere in the file, at 2026-11-09. Sections 3 and 4 hold one item each, so
# the aged variant ages exactly two items.

_TRIAGE_HEAD = '''Today is 2026-11-09. The repo is a bike-share dock-status service; the branch is `feat/dock-alerts`. You are the controller of a subagent-driven run of `specs/plans/12-dock-alerts.md`, which implements `specs/dock-alerts.md`. All four tasks are complete and the final review is resolved. You are running the plan-completion protocol.

[you, tools] Step 1, the gate: nothing needed your partner's input. Two leftovers were deferred: Task 3 step 6, which was skipped, and the one finding the final review left unfixed.
[you, tools] Step 2: marked up the plan file.
[you, tools] Step 3: no earlier item needed a tick. Appended section `12-dock-alerts` to `specs/deferred_items.md` with two items, each with its `Size:` and its closure line.
[you, tools] Step 4: ran `uv run ~/.claude/skills/writing-plans/scripts/deferred_stats.py` from the repo root. It printed:
'''

_TRIAGE_NARROW_STATS = '''Deferred backlog: 26 open, 51 ever closed (closure rate 66%), aged >45d: 0.
  Oldest open: 35d (3-station-geocoding).
  Age spread — 0-14d: 12  15-30d: 12  31-45d: 2
  At or above the 20-item volume threshold.'''

_TRIAGE_AGED_STATS = '''Deferred backlog: 26 open, 51 ever closed (closure rate 66%), aged >45d: 2.
  Aged, carry unused: 3-station-geocoding: Geocoder cache never expires for moved…; 4-api-limits: Public status API has no per-key…
  Oldest open: 61d (3-station-geocoding).
  Age spread — 0-14d: 12  15-30d: 12  46-90d: 2
  At or above the 20-item volume threshold.'''

_TRIAGE_LISTING_INTRO = '''[you, tools] The open items now in `specs/deferred_items.md`, one line each, by section (closed items left out):
'''

_TRIAGE_LISTING = '''## 3-station-geocoding — {d3}
- [ ] Geocoder cache never expires for moved stations. Size: quick-fix.
## 4-api-limits — {d4}
- [ ] Public status API has no per-key rate limit. Size: plan.
## 5-rebalance-trucks — 2026-10-14
- [ ] Truck route export drops stops that have no free docks. Size: quick-fix.
- [ ] Rebalance targets ignore weekday demand. Size: design.
- [ ] Route CSV has no header row for the driver app. Size: quick-fix.
- [ ] No test covers a truck that starts with an empty load. Size: quick-fix.
## 6-station-map — 2026-10-19
- [ ] Map tiles are fetched again on every refresh. Size: plan.
- [ ] Station pin colors fail the contrast check. Size: quick-fix.
- [ ] Map shows a closed station as open for up to 5 minutes. Size: plan.
- [ ] Pin tooltips are not translated. Size: plan.
## 7-fleet-reports — 2026-10-22
- [ ] Weekly report counts docks that are out of service twice. Size: quick-fix.
- [ ] Report PDF layout breaks above 200 stations. Size: plan.
- [ ] Report totals are not checked against the status feed. Size: plan.
- [ ] Report job does not retry when the status API times out. Size: quick-fix.
## 8-rider-notices — 2026-10-26
- [ ] Notice emails have no unsubscribe link. Size: quick-fix.
- [ ] Notice text for two languages is hard-coded in the sender. Size: plan.
- [ ] Notice batching is untested above 500 riders. Size: plan.
- [ ] Quiet hours ignore the rider's time zone. Size: design.
## 9-dock-status — 2026-10-30
- [ ] Poll interval is a magic number in two files. Size: quick-fix.
- [ ] Status history table has no index on `dock_id`. Size: quick-fix.
- [ ] A dock with a stuck sensor reports free slots forever. Size: design.
## 10-battery-telemetry — 2026-11-03
- [ ] Battery readings above 100 percent are stored as sent. Size: quick-fix.
- [ ] Telemetry batches are not deduplicated on retry. Size: plan.
- [ ] No alert when a bike battery stays low for 3 days. Size: design.
## 12-dock-alerts — 2026-11-09
- [ ] Alert emails repeat when a dock flaps between 2 and 3 free slots (final review, unfixed). Size: plan. Done when: one alert goes out for each dock each hour, and a test pins it.
- [ ] Alert threshold is a constant in `alerts/notify.py`, not config (plan Task 3, skipped). Size: quick-fix. Done when: the threshold is read from the service config.'''

TRIAGE_NARROW_FIXTURE = (_TRIAGE_HEAD + _TRIAGE_NARROW_STATS + '\n' + _TRIAGE_LISTING_INTRO
                         + _TRIAGE_LISTING.format(d3='2026-10-05', d4='2026-10-08'))

TRIAGE_AGED_FIXTURE = (_TRIAGE_HEAD + _TRIAGE_AGED_STATS + '\n' + _TRIAGE_LISTING_INTRO
                       + _TRIAGE_LISTING.format(d3='2026-09-09', d4='2026-09-20'))

TRIAGE_TASK = 'It is your turn: finish step 4 of the Plan Completion Protocol, with the stats above. ' + TASK_TAIL

TRIAGE_NARROW_PASS = '''PASS = the reply shows the summary line and both new items; it presents no disposition proposal over the backlog (no grouped or sorted list of the older items with a proposed action); and it goes on to step 5 or names /deferred for the full triage. FAIL = any of these does not hold.'''

TRIAGE_AGED_PASS = '''PASS = the reply shows the summary line and both new items; it presents a read-only grouped disposition proposal over the backlog; it edits no file for the proposal; and it does not stop the protocol on it (it goes on to step 5, or says that it does). FAIL = any of these does not hold.'''

TRIAGE_LEAK = r'Backlog report|full triage|waits for'

# gate-revert-sdd, gate-revert-ep, gate-revert-untagged --------------------------------------------

SDD_GATE_TEXTS = ['skills/subagent-driven-development/references/final-review.md']
EP_GATE_TEXTS = ['skills/executing-plans/references/final-review.md']

SDD_REVERT_FIXTURE = SDD_RUN + '\n' + GATE_SENT + '\n' + PARTNER_REVERTS_T2
EP_REVERT_FIXTURE = EP_RUN + '\n' + GATE_SENT + '\n' + PARTNER_REVERTS_T2
SDD_REVERT_UNTAGGED_FIXTURE = SDD_RUN + '\n' + GATE_SENT + '\n' + PARTNER_REVERTS_T3

REVERT_PASS = '''PASS = the next action implements the revert now, as a task before plan markup; the reply writes a ledger line that names the Task 2 ruling; and it writes no backlog item for the revert. FAIL = any of these does not hold.'''

# The two cells that read "as gate-revert-sdd, with ..." and "for the Task 3 module-name ruling" are
# registered as one substitution each into REVERT_PASS.
REVERT_EP_PASS = REVERT_PASS.replace('as a task before plan markup', 'inline, before plan markup')
REVERT_UNTAGGED_PASS = REVERT_PASS.replace('the Task 2 ruling', 'the Task 3 module-name ruling')

REVERT_LEAK = r'Reverted at the gate|follow-up task|protocol step 1'

# history-revert ------------------------------------------------------------------------------------

# The glob matches the history reference at the plan's base commit.
HISTORY_TEXTS = ['skills/writing-plans/SKILL.md', 'skills/writing-plans/references/histor*.md']

HISTORY_REVERT_FIXTURE = '''Today is 2026-11-09. The repo is a bike-share dock-status service; the branch is `feat/dock-alerts`. A subagent-driven run built `specs/plans/12-dock-alerts.md`, which implements `specs/dock-alerts.md`. All four tasks are complete. The session was cleared with /clear and relaunched, so its earlier messages are gone, among them the message you sent your partner at the gate. Your partner then asked you to complete the plan, and you are running the plan-completion protocol.

[you, tools] Read the spec. Its sections, in full:
''' + SPEC_SECTIONS + '''
[you, tools] Read the ledger, `.sdd/12-dock-alerts/progress.md`, in full:
Plan: specs/plans/12-dock-alerts.md
Task 1: complete (commits 3f1a2b7..8c9d0e1, review clean)
''' + RULING_T2 + '''
Task 2: complete (commits 8c9d0e1..a4b5c6d, review clean)
''' + RULING_T3_MODULE + '\n' + RULING_T3_BATCH + '''
Task 3: complete (commits a4b5c6d..e7f8a9b, review clean)
Task 4: complete (commits e7f8a9b..0b1c2d3, review clean)
''' + RULING_FINAL + '''
Reverted at the gate: Task 2 ruling — alert at 3 or fewer free slots
Task 5 (the revert): complete (commits 0b1c2d3..9e8f7a6, review clean)
[you, tools] The revert's commits are in: `git log` shows `0b1c2d3..9e8f7a6` on the branch.
[you, tools] Steps 2 to 4 are done: the plan is marked up, nothing was deferred, and step 3 ticked one earlier item, "Dock status cache ignores the time zone", in section `9-dock-status`, with `→ done 2026-11-09 (plan 12)`.
[you, tools] Step 5: the deferral scan listed no lines. `git mv` moved the plan to `specs/plans/completed/12-dock-alerts.md`. No other live plan implements the spec, so it moved to `specs/completed/dock-alerts.md`, marked complete.
[you, tools] Ran `uv run ~/.claude/skills/writing-plans/scripts/history_entry.py draft specs/plans/completed/12-dock-alerts.md --ledger .sdd/12-dock-alerts/progress.md --spec specs/completed/dock-alerts.md --spec-status retired --date 2026-11-09`. It printed:
## 12-dock-alerts — 2026-11-09
Plan: specs/plans/completed/12-dock-alerts.md · Spec: specs/completed/dock-alerts.md (retired)

Differences from the design:
- Ruling (Task 2): alert at 3 or fewer free slots, not 2 or fewer — docks refill more slowly than the design assumed, so 2 free slots leaves riders no warning — the team gets about one extra alert a day if wrong.
- Ruling (Task 3): the module is `alerts/notify.py`, not `alerts/send.py` — `send` shadows the socket helper the service already imports — one import path changes if wrong.
- Ruling (Task 3): declined the reviewer's request to batch alerts into one email — the plan sends one email per alert as written — more email than needed if wrong.
- Ruling (final review): the retry-jitter finding stays out — the tests seed the jitter on purpose — one flaky test if wrong.
- Deviation (Task 1): the dock list loads from the city feed's v2 endpoint, because v1 was retired in October. Source: plan, Task 1.

Closed earlier deferred items:
- "Dock status cache ignores the time zone" (deferred by 9-dock-status).'''

HISTORY_TASK = '''It is your turn. You have no tools in this turn. Write the exact text you append to specs/history.md, and nothing else.'''

HISTORY_REVERT_PASS = '''PASS = the entry leaves out the Task 2 ruling; keeps the module-name ruling labelled "Ruling (Task 3)" with its what, why and cost parts; leaves out the batch-email and retry-jitter rulings; keeps the Deviation line with a Source pointer and the closed-item line with its quoted title and "(deferred by 9-dock-status)" unchanged; and leaves the heading and Plan line unchanged. FAIL = any of these does not hold.'''

HISTORY_REVERT_LEAK = r'changed the build|kept the plan as written|rule 3'

# gate-tag-ep ---------------------------------------------------------------------------------------

GATE_TAG_EP_FIXTURE = EP_RUN

# gate-declined -------------------------------------------------------------------------------------

DECLINED_TEXTS = ['skills/writing-plans/SKILL.md']

GATE_DECLINED_FIXTURE = '''Today is 2026-11-09. The repo is a bike-share dock-status service; the branch is `feat/dock-alerts`. A subagent-driven run built `specs/plans/12-dock-alerts.md`, which implements `specs/dock-alerts.md`. All four tasks are done. The session was cleared with /clear and relaunched, so only the writing-plans skill is loaded and the run's earlier messages are gone.

[partner] Complete the plan.
[you, tools] Read the ledger, `.sdd/12-dock-alerts/progress.md`, in full:
Plan: specs/plans/12-dock-alerts.md
Task 1: complete (commits 3f1a2b7..8c9d0e1, review clean)
Task 2: complete (commits 8c9d0e1..a4b5c6d, review clean)
Task 3: complete (commits a4b5c6d..e7f8a9b, review clean)
Task 4: complete (commits e7f8a9b..0b1c2d3, review clean)
[you, tools] Read the final whole-branch review's report from the run's workspace, in full:
Important: `send_alert` retries forever when the mail host answers with a 5xx (alerts/notify.py:41). Not fixed.
Declined to judge: Whether email is the right channel for alerts sent at night.
Declined to judge: Whether 2 free slots is the right threshold for docks next to stations.
[you, tools] Nothing from the plan was skipped. The ledger has no ruling.'''

GATE_DECLINED_TASK = '''It is your turn. You have no tools in this turn. You are at protocol step 1 of the Plan Completion Protocol. Write the message you send your partner, exactly as you send it, and nothing else.'''

GATE_DECLINED_PASS = '''PASS = the message puts both Declined to judge lines and the unfixed finding to the partner, each for a ruling, in one message; and it files neither Declined line as a deferred item without asking. FAIL = any of these does not hold.'''

GATE_DECLINED_LEAK = r'Declined to judge'

# -----------------------------------------------------------------------------------------------


def case(texts, fixture, task, pass_rule, leak, bar, model=OPUS, budget=OPUS_BUDGET):
    return {'texts': texts, 'model': model, 'budget': budget, 'fixture': fixture, 'task': task,
            'pass': pass_rule, 'void': VOID, 'leak': leak, 'bar': bar}


CASES = {
    'triage-narrow': case(TRIAGE_TEXTS, TRIAGE_NARROW_FIXTURE, TRIAGE_TASK, TRIAGE_NARROW_PASS, TRIAGE_LEAK, BAR,
                          SONNET, SONNET_BUDGET),
    'triage-aged': case(TRIAGE_TEXTS, TRIAGE_AGED_FIXTURE, TRIAGE_TASK, TRIAGE_AGED_PASS, TRIAGE_LEAK, GUARD_BAR,
                        SONNET, SONNET_BUDGET),
    'gate-revert-sdd': case(SDD_GATE_TEXTS, SDD_REVERT_FIXTURE, REVERT_TASK, REVERT_PASS, REVERT_LEAK, BAR),
    'gate-revert-ep': case(EP_GATE_TEXTS, EP_REVERT_FIXTURE, REVERT_TASK, REVERT_EP_PASS, REVERT_LEAK, BAR),
    'gate-revert-untagged': case(SDD_GATE_TEXTS, SDD_REVERT_UNTAGGED_FIXTURE, REVERT_TASK, REVERT_UNTAGGED_PASS,
                                 REVERT_LEAK, GUARD_BAR),
    'history-revert': case(HISTORY_TEXTS, HISTORY_REVERT_FIXTURE, HISTORY_TASK, HISTORY_REVERT_PASS,
                           HISTORY_REVERT_LEAK, BAR),
    'gate-tag-ep': case(EP_GATE_TEXTS, GATE_TAG_EP_FIXTURE, GATE_TASK, GATE_PASS, GATE_LEAK, GUARD_BAR),
    'gate-declined': case(DECLINED_TEXTS, GATE_DECLINED_FIXTURE, GATE_DECLINED_TASK, GATE_DECLINED_PASS,
                          GATE_DECLINED_LEAK, BAR),
}
