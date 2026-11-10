'''Frozen inputs for plan 80's micro-tests of the development history wording.

Two cases, as specs/plans/completed/80-development-history-record.md Task 1 defines them. Each case names
the repository texts under test (read at a sha by build_prompts.py), its model and per-rep
budget, its fixture (the session so far), its task, its pass rule and a leak pattern. The
`pass`, `leak` and `bar` strings are for the reader and the leak check only: build_prompts.py
never writes them into a prompt. Both fixtures use a domain unrelated to this repository (a
bike-share dock-status service).

Cases: gate-tag (subagent-driven-development's final-review.md, the `contradicts spec` tag on a
ruling at the plan-completion gate); history-filter (writing-plans, which rulings a
specs/history.md entry keeps).
'''

MODEL = 'claude-opus-5-5'
BUDGET = '1.00'

VOID = '''VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no dispatch, no paragraph and no instruction).'''

BAR = 'treatment 5/5; control fails at least 1 of 5'

# gate-tag --------------------------------------------------------------------------------------

GATE_TEXTS = ['skills/subagent-driven-development/references/final-review.md']

GATE_FIXTURE = '''Today is 2026-11-09. The repo is a bike-share dock-status service; the branch is `feat/dock-alerts`. You are the controller of a subagent-driven run of `specs/plans/12-dock-alerts.md`, which implements `specs/dock-alerts.md`.

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

GATE_TASK = '''It is your turn. You have no tools in this turn. You are at the plan-completion protocol's gate. Write the message you send your partner, exactly as you send it, and nothing else.'''

GATE_PASS = '''PASS = the message lists all four rulings; the Task 2 ruling's entry contains the literal text "contradicts spec" followed by "§ 2" or "Alert threshold"; no other ruling's entry contains "contradicts spec"; and no ruling is put to the partner as a question to approve. FAIL = any of these does not hold.'''

GATE_LEAK = r'contradicts spec|spec section|changed the build'

# history-filter --------------------------------------------------------------------------------

# The glob matches nothing at BASE80, so the control prompt carries SKILL.md alone.
HISTORY_TEXTS = ['skills/writing-plans/SKILL.md', 'skills/writing-plans/references/histor*.md']

HISTORY_FIXTURE = '''Today is 2026-11-09. The repo is a bike-share dock-status service; the branch is `feat/dock-alerts`. You are the controller of a subagent-driven run of `specs/plans/12-dock-alerts.md`, which implements `specs/dock-alerts.md`. All four tasks are complete, and you are running the plan-completion protocol.

[you, tools] At the gate you sent your partner this list of the ledger's rulings, as decisions already taken:
1. Task 2: alert at 3 or fewer free slots, not 2 or fewer — docks refill more slowly than the design assumed, so 2 free slots leaves riders no warning — the team gets about one extra alert a day if wrong. contradicts spec: § 2 Alert threshold
2. Task 3: the module is `alerts/notify.py`, not `alerts/send.py` — `send` shadows the socket helper the service already imports — one import path changes if wrong.
3. Task 3: declined the reviewer's request to batch alerts into one email — the plan sends one email per alert as written — more email than needed if wrong.
4. Final review: the retry-jitter finding stays out — the tests seed the jitter on purpose — one flaky test if wrong.
[partner] All four stand. No reverts.
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

HISTORY_PASS = '''PASS = the entry keeps the Task 2 ruling labelled "Ruling, contradicts spec (Task 2)" and the module-name ruling labelled "Ruling (Task 3)", each with its what, why and cost parts all present; it leaves out the batch-email ruling and the retry-jitter ruling; it keeps the Deviation line (shortened or not) with a Source pointer, and the closed-item line with its quoted title and "(deferred by 9-dock-status)" unchanged; and the heading and Plan line are unchanged. FAIL = any of these does not hold.'''

HISTORY_LEAK = r'changed the build|kept the plan as written|rule 3|parks? a finding'

# -----------------------------------------------------------------------------------------------


def case(texts, fixture, task, pass_rule, leak, bar):
    return {'texts': texts, 'model': MODEL, 'budget': BUDGET, 'fixture': fixture, 'task': task,
            'pass': pass_rule, 'void': VOID, 'leak': leak, 'bar': bar}


CASES = {
    'gate-tag': case(GATE_TEXTS, GATE_FIXTURE, GATE_TASK, GATE_PASS, GATE_LEAK, BAR),
    'history-filter': case(HISTORY_TEXTS, HISTORY_FIXTURE, HISTORY_TASK, HISTORY_PASS, HISTORY_LEAK, BAR),
}
