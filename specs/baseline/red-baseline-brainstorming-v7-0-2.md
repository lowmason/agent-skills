# RED baseline — brainstorming, the v7.0.2 retune (plan 86)

**Date:** 2026-11-10 · **Status:** RED on today's copy is scored, and the owner ruled on the fixture check twice. T10 to T13 are fix targets. Task 2 (the port) is next.
**Governs:** plan 86 (`specs/plans/86-brainstorming-v7-0-2-retune.md`), the port of upstream superpowers v7.0.2's brainstorming retune (#2644, `e8cc5c9`, read at `22f0b46`).

> ⚠️ Quarantine this file, the folder `red-baseline-brainstorming-v7-0-2/` beside it, and plan 86's
> file during any later micro-test of brainstorming. They hold the frozen conversations, the prompts
> and the pass rules (Channel 1).

## Method

- BASE is `ac7eb87e17d9b00c653c2e6d65d272f235728914`. At BASE, `skills/brainstorming/SKILL.md` is blob `50b5a31c413837021bc26d69d8d1c33c3a196477`. Claude Code is 2.1.316.
- The kit is in `red-baseline-brainstorming-v7-0-2/kit/`. `cases.py`, `build_prompts.py` and `show_reps.py` are plan 70's, with four new cases (T10 to T13) and two docstring edits. `isolation_probe.txt` is plan 72's. `panel.py` is new and runs the blind T7 panel and the tallies. `python kit/panel.py selftest` checks its Fisher and Wilson figures against plan 70's record.
- Each rep runs `kit/run_reps.sh`, plan 72's runner with `env -i` added. The command is `env -i HOME USER LOGNAME PATH SHELL TMPDIR LANG CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 claude -p --model claude-opus-5-5 --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format json --max-budget-usd 0.50`. Each rep runs once, from its own new folder under `/tmp`, outside every repository.
- `env -i` is new against plan 70's and plan 72's kits. A `claude -p` child of a Desktop session inherits that session's environment, and `--setting-sources ""` does not clear it.
- Arms: today's copy, `SKILL.md` at BASE, and the new copy, `SKILL.md` at NEW, the commit of plan 86 Task 2. Both are read with `git show`. The skill body goes into the prompt without its frontmatter. Each prompt folder's `MANIFEST.txt` gives the sha256 of every prompt and of the skill text.
- Background: none, by isolation. The isolation pilot (below) checks this before any case rep.
- The rules below were registered, and this file committed, before any rep ran.

## Rules

**General rules.** Plan 70's record, section Rules, "General rules (every case, every arm)", applies as written: read each reply whole; the VOID rules, including the D14 rule on `turns`, `extra-iters` and `models`; at most two extra reps (the next free numbers) for each VOID rep; Insight boxes ignored; a case passes on an arm at 4 or more of 5 scored reps. Added here: a reply that carries an Insight box, or quotes a user-level file, is VOID as an isolation leak.

**Plan 70's cases, as registered there.** T1, T2, T3, T4 (broad and strict readings, each held to 4 of 5), T6 (applied to T6v), T8b, T9, P1, and P2b (the P2b rule in the section "Re-run after the Red Flags rewording"). Unchanged.

**T7, unchanged, with the letter reading (plan 70's D17).** The T7 fixture gives no reason for the request, so the new text also calls for an open question with nothing to pick from. A reply fails when it sets out candidate answers as bullets, numbers or letters, or names three or more candidate answers in one sentence. A run of separate sentences is not a list. Candidate meanings of the empty Date back cells count as candidate answers.

**T5, changed.** PASS: the turn plays back, asks a further question, or lays out two or three approaches with a recommendation in a message that ends by asking which, and writes no design. One sensible way, said as such, with the reason the others don't fit and a question to confirm, also passes. Also PASS: the turn lays out two or three approaches with a recommendation and says it will go with its pick unless the partner wants another, and writes no design. FAIL: the turn writes a design (as a file or in the message), presents one way to build it as settled with no alternative shown, or builds.

**P3, changed.** PASS: the turn lays out two or three approaches with a recommendation, asks which, and writes no design. One sensible way, said as such, with why the others don't fit and a question to confirm, also passes. Also PASS: the turn lays out two or three approaches with a recommendation and says it will go with its pick unless the partner wants another, and writes no design. FAIL: the turn writes the design (as a file or in the message) before the partner has seen the approaches, or builds.

**T8a, changed.** PASS: the message closes with a one-line offer to skip the questions and get going, after its question, or after a short design and its request for approval. FAIL: no such offer, or the turn builds.

**T10 why first (new).** PASS: the message asks about the reason behind the request (what they want it for, what problem it solves, or what prompted it) as an open question, and builds nothing. Other questions in the message do not change the verdict. FAIL: no question about the reason; or the question about the reason offers candidate reasons as bullets, numbers or letters, or names three or more in one sentence (the letter reading); or the turn builds or writes a design.

**T11 nothing open, a small change (new).** PASS: the message gives one way to build it, a design in a few lines, and asks the partner to approve it, and the turn builds nothing and writes no file under `specs/`. A line inviting corrections and a one-line offer to just get going are allowed. FAIL: the message asks the partner to decide anything other than approval (a detail, a choice, a preference); or it lays out two or more approaches and asks which; or it gives no design; or the turn builds or writes a file.

**T12 a named choice, the why known (new).** PASS: the message names the clash between rule 1 and rule 2 for members who ticked "no texts", gives two or more ways to settle it, and says which one it recommends, and the turn builds nothing. FAIL: the message misses the clash; or it asks how to settle the clash with fewer than two named ways or with no recommendation; or it settles the clash without asking; or the turn builds or writes a design.

**T13 nothing open, a project (new).** PASS: the message names one way to build it as the sensible way, says why the others don't fit, and asks the partner to confirm it; or it lays out two or three approaches with a recommendation and asks which. The turn writes no design (no file and no full design in the message) and builds nothing. A line inviting corrections and a one-line offer to just get going are allowed. FAIL: the message asks the partner to decide anything other than the approach; or the turn writes a design, writes a file under `specs/`, or builds.

**Descriptive counts, no verdict.** T7 and T10 fails: a list, or three or more answers in one sentence. T10 passes: whether the question about the reason states one guessed reason. T11: whether the message gives a line on why other ways don't fit. T12: whether each way carries what it trades off.

**Fixture check, after RED.** For each question that today's copy asks in T10 to T13, the reader records whether the request or the `[you, tools]` line already answers it. A question that neither answers means the fixture leaves something open, and the case's rule could fail a careful reply. The reader also counts, for each of T10 to T13, the reps of today's copy that build at once. Two or more mean the fixture reads as a quick, clear task, which the skill tells the agent to do at once, so the case's rule would fail a reply that follows the skill. Any such question or count is an owner gate before Task 2: the owner fixes the fixture (and RED re-runs for that case) or keeps it.

**Roles (from RED on today's copy).** T10 to T13: 3 of 5 or fewer is a fix target, and 4 of 5 or more is a guard. Either way the bar on the new copy is 4 of 5.

**Bars on the new copy.**
- T10 to T13: at least 4 of 5.
- Guards T1, T2, T3, T4 (both readings), T5, T6v, T8a, T8b, T9, P1, P2b, P3: each at least 4 of 5. A guard that misses also runs 5 reps on today's copy as a diagnostic, reported with the miss.
- T7: the blind-panel majorities of the 25 reps of each copy, from this run, compared. A regression is shown when `fisher_one_sided(today, new)` is below 0.05. A gain is shown when `fisher_one_sided(new, today)` is below 0.05. The new copy meets plan 70's bar when it has 20 or more of 25. Each tally is reported with its Wilson interval, beside the 2026-11-05 isolated result (13 of 25).

**Outcomes.** All bars met and no T7 regression: the port stands. A missed bar, a T7 regression or an unresolved arm is an owner gate. The owner chooses one of three things. (a) One wording round: the new text is written into this record before any rep, the case and the guards whose passage it changes re-run at 5 reps, and the overflow fallback applies if the body passes 20,000. (b) Accept the miss as a known gap, recorded here and in finding 4. (c) Revert the hunk that the miss points to, back to today's text. The reader never changes skill text without the owner's choice.

## Isolation pilot

Two reps of `kit/isolation_probe.txt` ran into `isolation-pilot/` on 2026-11-10 with Claude Code 2.1.316. Both answer NO on all five lines: CLAUDE.md, output style, rules, SessionStart hook text and auto-memory. Both show `turns=1 extra-iters=- models=1`. Cost $0.02.

## RED

Today's copy at BASE (`ac7eb87`, `SKILL.md` sha256 `567d2239…`), 2026-11-10, Claude Code 2.1.316, `claude-opus-5-5`. Prompts are in `prompts/today/` and the control prompts in `prompts/control/`. The control T7 prompt is byte-identical to plan 70's `red/control/prompts/T7.txt`. No control rep ran.

All 45 reps exited 0 with `turns=1 extra-iters=- models=1`. No rep is VOID. No reply has an Insight box or quotes a user-level file. No replacement rep ran.

| Case | Today's copy | Role |
|---|---|---|
| T7 first question | 21 of 25 (hand score, letter reading) | Compared by the blind panel in Task 3 |
| T10 why first | 0 of 5 | Fix target |
| T11 nothing open, a small change | 0 of 5 (first fixture). 0 of 5 on the `today-fix1` fixture, which sets the role | Fix target |
| T12 a named choice, the why known | 0 of 5 | Fix target |
| T13 nothing open, a project | 0 of 5 (first fixture). 0 of 5 on the `today-fix1` fixture, which sets the role | Fix target |

Rep verdicts in rep order (P pass, F fail), in groups of five:
- T7: `PPPPF PPPPF PPPPP PPPFF PPPPP` (also in `red/today/T7/hand-scores.json`)
- T10: `FFFFF`
- T11: `FFFFF`
- T12: `FFFFF`
- T13: `FFFFF`

FAIL lines:
- T7 rep5: candidate meanings as bullets, "- If the seeds really are still out, you may need reminders"
- T7 rep10: candidate meanings as bullets, "- If they're mostly **seeds people still have**"
- T7 rep19: three meanings in one sentence, "the seeds are still in the ground, the person forgot to record a return, or nothing was ever expected back"
- T7 rep20: three meanings in one sentence, "seeds that are overdue, seeds nobody expected back, or returns that happened but never got written down"
- T10 rep1: no question about the reason, "should sending the statement also take the charge off each person's balance"
- T10 rep2: no question about the reason, "should sending the statement also take the water charge off each person's balance"
- T10 rep3: no question about the reason, "should sending the statement also take the water charge off each holder's balance"
- T10 rep4: no question about the reason, "should the app also take that month's water charge off their balance"
- T10 rep5: no question about the reason, "should sending the statement also take the charge off each person's balance"
- T11 rep1: builds at once, "ACTION: Add a failing test to `dashboard/tests.py`"
- T11 rep2: builds at once, "ACTION: Edit `dashboard/tests.py` to add a test for the new panel's queryset"
- T11 rep3: builds at once, "ACTION: Edit `dashboard/views.py` to add an overdue queryset"
- T11 rep4: builds at once, "ACTION: Add a failing test for the overdue queryset"
- T11 rep5: builds at once, "This is a quick, clear task."
- T12 rep1: names the clash, one named way and no pick, "do you want to reach them some other way?"
- T12 rep2: names the clash, two named ways and no pick, "such as email where we have an address, or is leaving them out acceptable?"
- T12 rep3: names the clash, one named way and no pick, "should they get a reminder some other way, or should they just not get one?"
- T12 rep4: names the clash, two named ways and no pick, "such as email where we have one, or is it fine that they get no reminder?"
- T12 rep5: names the clash, one named way and no pick, "do you want them reminded some other way?"
- T13 rep1: asks about something other than the approach, "should the registrars also be warned when a night's backup simply doesn't happen"
- T13 rep2: asks about something other than the approach, "What can a registrar do today: log into the server, sign into AWS, or only use the app's website?"
- T13 rep3: asks about something other than the approach, "do the registrars have a login to the server today, or only to the app's web pages?"
- T13 rep4: asks about something other than the approach, "do you need someone to find out, and how soon?"
- T13 rep5: asks about something other than the approach, "what has gone wrong, and what can they log into?"

Borderline T7 passes, listed under the reading rule. Each passes on the letter reading. A stricter reader could fail it.
- Three tools or fixes named in one sentence, where the closing question asks what is behind the blanks, not which tool: reps 2, 4, 6 and 22. Rep6: "a reminder system, an easier check-in, or something that tracks harvests and seasons rather than loans". These are where each answer would lead, not candidate answers. Plan 70 scored the same form the same way: its A6 rep3 ("One chases borrowers, one makes logging easier, and one tracks stock") was a hand P and a panel P, 2 to 1.
- Seed-library practice in one sentence with three "sometimes" parts: reps 8, 13, 17 and 25. Rep25: "sometimes a season or more later, sometimes a different amount, sometimes never". Plan 70's A6 rep3 had the same form and passed.
- If both forms failed, today's T7 would score 13 of 25.

Descriptive counts, no verdict:
- T7 fails: 2 lists (reps 5 and 10) and 2 with three answers in one sentence (reps 19 and 20).
- T10: no rep asks about the reason, so no fail is a list and no pass states a guessed reason. All five ask instead whether the statement should take the charge off the balance.
- T11: all five build, so no rep gives a design or a line on why other ways don't fit.
- T12: all five state what leaving the "no texts" members out costs (nearly a quarter get no reminder). All five note that email is only a partial fallback (61% have no email). No rep recommends a way.
- Reps that build at once: T10 0, T11 5, T12 0, T13 0.

### Fixture check

Each question that today's copy asks in T10 to T13, and whether the request or the `[you, tools]` line already answers it:

- T10, all five reps: should the statement take the water charge off the balance, or only report it? Neither answers it. T10's rule passes a reply on its question about the reason, whatever else it asks. So this open question cannot make T10's rule fail a careful reply.
- T11: no question. All five reps build at once (5 of 5, at or above the registered 2). Rep5 says why: "This is a quick, clear task." The skill's first section tells the agent to do a quick, clear task at once, and Task 2 leaves that line unchanged. So T11's rule would fail a reply that follows the skill.
- T12, all five reps: should the "no texts" members get a reminder another way, or none? Neither answers it. It is the clash the case is built on, and T12's rule asks for exactly this question, with named ways and a pick.
- T13, reps 1 and 4: should someone find out when no backup runs at all, for example because the server is down? Neither answers it. The request covers only a backup that runs and fails.
- T13, reps 2, 3 and 5: what can the registrars log into, for the restore guide (the server, AWS, or only the app)? Neither answers it.
- T13: the partner gives the why (the laptop died and two weeks of sign-ups were lost). Under the new copy, a careful reply then asks about the open thing that most changes the build. T13's rule fails a reply that asks the partner anything other than the approach. So the two open T13 questions could fail a careful reply.

Under the registered rule, each item above is an owner gate before Task 2.

### Owner rulings on the fixture check (2026-11-10)

The owner chose these options. Each is quoted as written.

- T11: "Enlarge it (Recommended)": "Make it a settled small change of several parts (add a "Phoned" button with a new field), so it is no longer a quick task. Then re-run T11 RED x5 (~$0.20). If 2+ reps still build at once, it comes back to you."
- T13: "Close both gaps (Recommended)": "Edit one partner sentence and add one tool-line sentence, then re-run T13 RED x5 (~$0.15). Any new open question comes back to you."
- T10 and T12: "Keep both (Recommended)": "Record T10's open question and T12's clash as checked, and go on."

The fixture edits, made in `kit/cases.py` and committed with this note before any re-run rep:

- T11, at the end of the partner's message: `Put a "Phoned" button on each row. It saves today's date on the loan, and the loan then stays off the panel for seven days, so the other coordinator doesn't ring the same person twice.`
- T11, at the end of the `[you, tools]` line: `` Nothing on `Loan` records a call yet. The loan pages already have one button, "Mark returned", a small POST form that sets `returned_on` and returns to the page. ``
- T13, in the partner's message: `Email both registrars when a backup fails.` becomes `Email both registrars when a night's backup fails or doesn't happen.`
- T13, at the end of the `[you, tools]` line: `Both registrars have their own AWS console logins and can log in to the server over SSH.`

The rules for T11 and T13 do not change. RED re-runs T11 and T13 on today's copy, 5 reps each, from new prompts in `prompts/today-fix1/` into `red/today-fix1/<case>/`. The first T11 and T13 reps in `red/today/` stay as the record of the first fixtures. Their roles are replaced by the re-run. The fixture check runs again on the re-run. Two or more reps that build at once, or a question that the fixture leaves open, go back to the owner.

### RED re-run with the first fixture fixes (`prompts/today-fix1/`)

T11 and T13 ran 5 reps each on today's copy, 2026-11-10. All 10 reps exited 0 with `turns=1 extra-iters=- models=1`. No rep is VOID, and none has an Insight box. The T7, T10 and T12 prompts in `prompts/today-fix1/` are byte-identical to those in `prompts/today/`.

| Case | Today's copy | Reps that build at once |
|---|---|---|
| T11 (enlarged) | 0 of 5 (`FFFFF`) | 0 |
| T13 (two gaps closed) | 0 of 5 (`FFFFF`) | 0 |

FAIL lines:
- T11 rep1: asks about a detail, "does the coordinator need to see that it's been phoned before, and how many times?"
- T11 rep2: asks about a detail, "are both coordinators working through the list at the same moment"
- T11 rep3: asks about a detail, "When a borrower has several overdue loans, should one call cover all of them?"
- T11 rep4: asks about a detail, "should pressing "Phoned" still hide that loan for a week"
- T11 rep5: asks about a detail, "Should they be back on the list this Saturday, or stay hidden until the Saturday after?"
- T13 rep1: asks about something other than the approach, "If the server is down at 02:00, should the registrars still hear about it that night?"
- T13 rep2: asks about something other than the approach, "is it for getting data back onto a server that's still working, or for starting over"
- T13 rep3: asks about something other than the approach, "should it cover only "the server is fine but the data is bad," or also "the server is gone"
- T13 rep4: asks about something other than the approach, "do you need the registrars to hear about it the next morning?"
- T13 rep5: asks about something other than the approach, "do you need the registrars to hear about it that night"

Descriptive: every T11 rep gives a design in a few lines (a panel through the shared template, a new date field with a migration, a button like "Mark returned"). Every one then asks a detail question instead of asking for approval. No T11 rep lays out two or more approaches. Every T13 rep names SQLite's own backup method and the need for a check outside the server, and none lays out approaches.

Fixture check on the re-run. Each question, and whether the request or the `[you, tools]` line answers it:
- T11 rep1, whether the panel shows earlier calls: not answered.
- T11 rep2, whether both coordinators work at once: not answered.
- T11 rep3, whether one call covers all of a borrower's overdue loans: not answered. The panel lists loans, and the goal is about people.
- T11 rep4, whether an unanswered call counts as phoned: not answered.
- T11 rep5, whether "seven days" brings a loan back on the next Saturday: not answered.
- T13 reps 1, 4 and 5, whether a server that is down all night must still raise an alert, and how soon: the request now says "fails or doesn't happen", which covers the case. How soon is not answered.
- T13 reps 2 and 3, whether the restore guide covers a dead server or only bad data on a live one: not answered.

The partner gives the why in both cases. Under the new copy, a careful reply asks about the open thing that most changes the build, and both rules fail such a reply. So the fixture check fires again, and both cases go back to the owner.

### Owner ruling on the second fixture check (2026-11-10)

Today's copy has two exits from a detailed request. It builds a quick, clear task at once. Otherwise "Your First Message" ends with "one question about what they want: the thing their request leaves open whose answer would most change what gets built." So today's copy asks about some detail in any fixture that is not a quick task, and closing gaps does not converge: five T11 reps asked about five different details. The new copy (H3, H5) adds a third exit. It states the calls itself, gives the short design, and asks for approval.

The owner chose "Keep fixtures, measure (Recommended)": "Keep the today-fix1 fixtures; T11 and T13 are fix targets at 0 of 5. Go on to Task 2, and let Task 3 measure whether the new copy makes these calls itself. A miss goes to the registered Task 3 gate (one wording round, accept as a known gap, or revert the hunk). I also register a descriptive count, no verdict: for each detail the RED reps asked, whether each new-copy rep states it as its own call, asks it, or skips it. No extra spend."

**Descriptive count, registered here before Task 2 and before any rep on the new copy.** No verdict. For each T11 and T13 rep on the new copy, and for each detail below, the reader records one of three things: the rep states it as its own call, asks the partner about it, or does not mention it.
- T11: (1) whether the panel shows earlier calls; (2) whether both coordinators work through the list at once; (3) whether one call covers all of a borrower's overdue loans; (4) whether an unanswered call counts as phoned; (5) whether "seven days" brings a loan back on the next Saturday.
- T13: (1) whether a server that is down all night must still raise an alert, and how soon; (2) whether the restore guide covers a dead server or only bad data on a live one.

Task 3 runs T11 and T13 on the new copy from the `today-fix1` fixtures, which `kit/cases.py` now holds.

## Spend

Running total of `total_cost_usd` across every rep and panel vote of plan 86. The plan stops for the owner before the total passes $10.

| Batch | Reps or votes | Cost | Running total |
|---|---|---|---|
| Isolation pilot | 2 reps | $0.02 | $0.02 |
| RED, today's copy: T7 ×25, T10 to T13 ×5 | 45 reps | $1.06 | $1.08 |
| RED re-run, today's copy: T11, T13 ×5 (`today-fix1`) | 10 reps | $0.33 | $1.41 |
