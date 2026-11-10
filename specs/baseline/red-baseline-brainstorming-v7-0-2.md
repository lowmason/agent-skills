# RED baseline — brainstorming, the v7.0.2 retune (plan 86)

**Date:** 2026-11-10 · **Status:** Complete. The shipped copy is NEW-R1 (`9761c88`). Every bar is met except the P3 guard, which the owner accepted as a known gap. T7 shows no regression after wording round 1 and stays the known gap ruled on 2026-11-06. See Disposition.
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

## New copy

The new copy at NEW (`a120ef7`, `SKILL.md` sha256 `9510532…`), 2026-11-10, Claude Code 2.1.316, `claude-opus-5-5`. Prompts are in `prompts/new/`. Each differs from the same case's `prompts/today-fix1/` prompt only inside the `<skill name="brainstorming">` block. All 105 reps exited 0 with `turns=1 extra-iters=- models=1`. No rep is VOID, and none has an Insight box or quotes a user-level file. No replacement rep ran.

| Case | RED (today's copy) | Role | New copy | Verdict |
|---|---|---|---|---|
| T10 why first | 0 of 5 | Fix target | 5 of 5 | Met |
| T11 nothing open, a small change | 0 of 5 (`today-fix1`) | Fix target | 3 of 5 | **Missed** |
| T12 a named choice, the why known | 0 of 5 | Fix target | 5 of 5 | Met |
| T13 nothing open, a project | 0 of 5 (`today-fix1`) | Fix target | 5 of 5 on the approach reading, 0 of 5 on the whole-project reading | **Unresolved** (see the reading below) |

| Guard | New copy | Verdict |
|---|---|---|
| T1 | 5 of 5 | Met |
| T2 | 5 of 5 | Met |
| T3 | 5 of 5 | Met |
| T4 | 5 of 5 broad, 4 of 5 strict | Met on both readings |
| T5 | 5 of 5 | Met |
| T6v | 5 of 5 | Met |
| T8a | 5 of 5 | Met |
| T8b | 5 of 5 | Met |
| T9 | 5 of 5 | Met |
| P1 | 5 of 5 | Met |
| P2b | 5 of 5 | Met |
| P3 | 1 of 5. Diagnostic on today's copy: 5 of 5 | **Missed** |

Rep verdicts in rep order (P pass, F fail), in groups of five:
- T7: `PPPPP PPFPP PPFPF FPFPP FFPPP`, the hand scores. The panel's verdicts are under T7 panel.
- T10 `PPPPP`, T11 `PPPFF`, T12 `PPPPP`, T13 `PPPPP` (approach reading)
- T1 `PPPPP`, T2 `PPPPP`, T3 `PPPPP`, T4 broad `PPPPP`, T4 strict `PPPFP`, T5 `PPPPP`, T6v `PPPPP`, T8a `PPPPP`, T8b `PPPPP`, T9 `PPPPP`, P1 `PPPPP`, P2b `PPPPP`, P3 `FPFFF`
- Diagnostic, today's copy: P3 `PPPPP` (`diag/today/P3/`)

FAIL lines:
- T7 rep8: three meanings in one sentence, "might mean the same packets, seeds saved from the borrower's own harvest, or nothing at all"
- T7 rep13: three meanings in one sentence, "packets still out, returns nobody wrote down, or seeds that were planted and never meant to come back"
- T7 rep15: four meanings in one sentence, "A blank could mean overdue, still growing, forgotten, or never expected back."
- T7 rep16: three meanings in one sentence, "seeds that are overdue, seeds nobody expected to come back, or returns that never got written down"
- T7 rep18: three meanings in one sentence, "still out, were returned but never logged, or were never expected back"
- T7 rep21: three meanings in one sentence, "seed still out, a return nobody wrote down, or a loan that was never expected to come back"
- T7 rep22: three meanings in one sentence, "The seeds might still be out, or they came back and nobody wrote it down, or the borrower planted them"
- T11 rep4: asks a choice, not approval, "Which matches how you'd want it?" (whether "Phoned" covers the person or the loan)
- T11 rep5: asks a choice, not approval, "Which way?" (per loan or per person)
- T4 rep4 (strict reading only): marks only where uploads go as its call, "Where uploads go."
- P3 rep1: writes the design before the partner sees the approaches, "ACTION: Create `specs/batch-tracking.md`"
- P3 rep3: writes the design before the partner sees the approaches, "ACTION: Write `specs/batch-tracking.md`"
- P3 rep4: writes the design before the partner sees the approaches, "ACTION: Create `specs/batch-tracking.md`"
- P3 rep5: writes the design before the partner sees the approaches, "ACTION: Create `specs/batch-tracking.md`"

Borderline calls:
- T7: ten passes name three or more tools or problem areas in one sentence (reps 2, 6, 7, 9, 12, 14, 17, 19, 24 and 25). Rep25: "easier entry at the table, chasing people up, knowing what's on the shelf, or something else". Rep1 names two builds and "something more". The blind panel failed all ten (below).
- T10 rep1 puts two example reasons in its question: "are you starting to bill for water, or do you want plot holders to see what they're using?" Two is below the letter reading's three, so it passes.
- T12 rep3's pick is conditional: "I'd pick this one, if "no texts" doesn't also mean "no reminders at all."" It is still a recommendation.
- T4 rep4 passes the broad reading and fails the strict one. T4 meets the bar on both.
- T13, all five reps. The reading decides the arm, so T13 is unresolved. Each rep lays out two or three ways to catch a backup that never runs (an email from the server only, a scheduled check inside AWS, an outside check-in service), with what each trades off and a pick, and asks which. These are ways of building one part of the project, the part the partner's why turns on. On the reading that "the approach" covers that, all five pass. On the reading that "the approach" means the whole project's approach, all five ask about something else and fail.
- P3 rep2 passes on the registered third clause. It names its pick, says why the others don't fit, and ends: "If extending the taproom app is the wrong call, say so now. Otherwise I'll write it up."

Descriptive counts, no verdict:
- T7 fail forms: see T7 panel.
- T10 passes: rep1 states two guessed reasons in its question, and rep4 names two possibilities after it. The other three state none.
- T11: reps 1, 2 and 3 give a line on why another way doesn't fit (a call-history table is more than was asked).
- T12: every way in every rep carries what it trades off.
- P3: the four FAIL reps each record the approach as "my call" inside the written design, and three say why ("the partner handed me the how", "Approach 1 was my call; the partner handed over how it's built"). Today's copy, in the diagnostic, lays out the approaches and asks which in all five reps.

The registered call / ask / skip count for the details today's copy asked about in RED:

| T11 detail | rep1 | rep2 | rep3 | rep4 | rep5 |
|---|---|---|---|---|---|
| (1) the panel shows earlier calls | call | call | call | skip | skip |
| (2) both coordinators work at once | skip | skip | skip | skip | skip |
| (3) one call covers all of a borrower's loans | skip | skip | skip | ask | ask |
| (4) an unanswered call counts as phoned | skip | skip | skip | skip | skip |
| (5) "seven days" brings a loan back on the next Saturday | call | call | call | skip | skip |

| T13 detail | rep1 | rep2 | rep3 | rep4 | rep5 |
|---|---|---|---|---|---|
| (1) a server down all night still raises an alert, and how soon | ask (as the approach), timing a call | ask (as the approach), "by 03:00" a call | ask (as the approach), "each morning" a call | ask (as the approach), "each morning" a call | ask (as the approach), "each morning" a call |
| (2) the restore guide covers a dead server or only bad data | skip | skip | skip | skip | skip |

## T7 panel

Three blind votes (`panel/T7/`), each a separate `claude -p` call under `run_reps.sh`'s isolation, on `claude-opus-5-5`. Each vote saw `panel/T7/rule.txt` (the registered T7 paragraph), the control T7 prompt and all 50 replies in its own shuffled order (seeds 87, 88 and 89), with the arm and rep hidden. 49 of the 50 replies got a unanimous vote. New rep1 split 2 to 1 for a pass. Cost $0.56.

| Copy | Panel majority | Wilson 95% | Hand score | Wilson 95% |
|---|---|---|---|---|
| Today's copy (BASE) | 17 of 25 (68%) | 0.48 to 0.83 | 21 of 25 (84%) | 0.65 to 0.94 |
| New copy (NEW) | 8 of 25 (32%) | 0.17 to 0.52 | 18 of 25 (72%) | 0.52 to 0.86 |
| Plan 70, isolated re-run, 2026-11-05 | 13 of 25 (52%) | 0.33 to 0.70 | | |

- Panel, one-sided Fisher p: new above today 0.998, today above new **0.011**. Under the registered bar, a regression is shown.
- Hand scores, one-sided Fisher p: new above today 0.915, today above new 0.248. On the hand scores, no regression is shown.
- The new copy is below plan 70's bar (20 of 25) on both scorings. Today's copy meets that bar on the hand scores and misses it on the panel, so the two scorings put today's arm on different sides of the bar.
- Panel verdicts in rep order. Today: `PFPFF FPPPF PPPPP PPPFF PFPPP`. New: `PFPPP FFFFP PFFFF FFFFP FFPFF`.

**Where the hand scores and the panel differ.** All 14 differences are reps that the hand score passed and listed as borderline because they name three or more tools or problem areas in one sentence: today's reps 2, 4, 6 and 22, and new reps 2, 6, 7, 9, 12, 14, 17, 19, 24 and 25. The panel failed each one, 3 to 0 ("Three tool options named in one sentence", "Four candidate focuses named in one sentence"). The hand reading followed plan 70's A6 rep3, a hand pass and a 2-to-1 panel pass. This panel reads the form the other way, and the panel majority is the registered verdict.

**Fail forms (panel majorities).**

| Copy | Bullets or numbers | Three or more meanings of the blanks in one sentence | Three or more tools or problem areas in one sentence |
|---|---|---|---|
| Today's copy | 2 | 2 | 4 |
| New copy | 0 | 7 | 10 |

The new copy sets out no list, as plan 70's sentence asks. But it moves the candidates into one sentence, often after the question: "Your answer decides whether this is mostly about making returns easy to record, chasing people…". This is a hypothesis, not a measurement. H5 removes plan 70's "a single sentence with no list of example answers hanging off it", and H6 keeps the ban on guesses "before the question" only.

**A note on the panel rule.** `panel/T7/rule.txt` is plan 86's registered T7 paragraph, as Task 3 Step 4 says. It differs from plan 70's panel rule. It has no PASS sentence and no line telling voters to ignore an Insight box, and it mentions "the new text". That may explain why this panel failed the tools form that plan 70's panel passed 2 to 1. It also makes the 2026-11-05 figure context only. Both arms here were scored under the same text in one panel, so the comparison between them stands.

## Owner rulings at the Task 3 gate (2026-11-10)

The owner chose these options. Each is quoted as written.

- T13 reading: "Yes, approach: 5 of 5 (Recommended)": "It is a choice about how the project gets built, which the PASS clause names. RED's fails were all questions about what the partner wants (alert timing, guide scope, logins). T13 meets its bar."
- T11: "(b) Accept as known gap (Recommended)": "Record the miss as a fixture gap the new copy correctly asks about, in the record and in finding 4. No spend."
- P3: "(a) One wording round on H9 (Recommended)": "Add one clause (+44 chars incl. the T7 fix; body 19,524). Register it, re-run P3 and the approach guards T5, T9, P1, T11, T13 at 5 reps each: about 30 reps, ~$1.0, running total ~$6.8."
- T7: "(a) One wording round on H6 (Recommended)": "Change "before the question either" to "before or after the question". Re-run T7 x25 plus a fresh 50-reply panel (today + new), and T10, T8a, T8b x5: ~$1.9. With the P3 round, the running total is ~$8.7 of the $10 cap."

### Wording round 1, registered before any rep

This is the plan's one wording round (outcome (a)). Both changes go into `skills/brainstorming/SKILL.md` in one commit, NEW-R1. They are local wording, not upstream text, so Task 4's `NOTICE` bullet and finding 4 name them as divergences.

H6, Get them describing. Replace:

```text
at the answer ("this could mean A, B or C"), or where each would lead,
before the question either; that's a menu too. Their own words carry
```

with:

```text
at the answer ("this could mean A, B or C"), or where each would lead,
before or after the question; that's a menu too. Their own words carry
```

H9, Lay out the approaches. Replace:

```text
why, then ask which way they want to go; if they've handed you the how,
say you'll go with your pick instead. When there's genuinely one
sensible way, say so in that message and explain why the others don't
fit; the design comes in the next one. This is for how it gets built;
for what they want, get them describing first.
```

with:

```text
why, then ask which way they want to go; if they've handed you the how,
say you'll go with your pick instead, and write the design in the next
message. When there's genuinely one sensible way, say so in that message
and explain why the others don't fit; the design comes in the next one.
This is for how it gets built; for what they want, get them describing
first.
```

Expected after the round: `SKILL.md` sha256 `3194843f7a35d36e3de4226790e55f483023f22897d42e5e75078d54a6e9a049`, body 19,524 characters (cap 20,000), file 20,168 bytes. Task 2's Steps 3 and 5 run again on NEW-R1: the hash, the body length and `build/run_commit_lints.sh`.

**What re-runs on NEW-R1**, from new prompts in `prompts/new-r1/` into `green/new-r1/<case>/`:
- For H9: P3, T5, T9, P1, T11 and T13, 5 reps each.
- For H6: T7, 25 reps. T10, T8a and T8b, 5 reps each.

**Rules and bars.** The registered rules apply unchanged, with the owner's T13 reading. Each case and guard is held to 4 of 5. T11's miss stands as a known gap unless NEW-R1 reaches 4 of 5. Its tally and the call / ask / skip count are reported either way.

**T7 panel for the round.** Hand scores for the NEW-R1 T7 reps are written first, to `green/new-r1/T7/hand-scores.json`. Then a fresh blind panel runs into `panel/T7-r1/`: today's 25 reps and NEW-R1's 25 reps (arms `today` and `newr1`), 3 votes, seed 186, the same `rule.txt` and the control T7 prompt. Today's copy is scored again inside this panel, so the Fisher test compares two arms of one panel. A regression is shown when `fisher_one_sided(today, newr1)` is below 0.05. A gain is shown when `fisher_one_sided(newr1, today)` is below 0.05. NEW-R1 meets plan 70's bar at 20 or more of 25. The first panel (`panel/T7/`) stays as the record of NEW.

**Outcomes after the round.** The plan allows one wording round. So any bar the round misses, or a T7 regression it still shows, goes to the owner with (b) accept as a known gap or (c) revert the hunk. Spend: the round costs about $3, so the running total reaches about $8.7. The run stops for the owner before the total passes $10.

## Wording round 1 results (NEW-R1)

NEW-R1 is `9761c88`, `SKILL.md` sha256 `3194843f…`, body 19,524 characters. Task 2's checks ran again on it: the hash and body length match the registration, and `build/run_commit_lints.sh` passes. Prompts are in `prompts/new-r1/`, and reps in `green/new-r1/`. All 70 reps exited 0 with `turns=1 extra-iters=- models=1`. No rep is VOID, and none has an Insight box. Cost $2.00.

| Case | Hunk | NEW | NEW-R1 | Verdict on NEW-R1 |
|---|---|---|---|---|
| P3 | H9 | 1 of 5 | 3 of 5 (`FFPPP`) | **Missed** (today's copy 5 of 5) |
| T5 | H9 | 5 of 5 | 5 of 5 | Met |
| T9 | H9 | 5 of 5 | 5 of 5 | Met |
| P1 | H9 | 5 of 5 | 5 of 5 | Met |
| T11 | H9 | 3 of 5 | 4 of 5 (`FPPPP`) | Met. The known gap is lifted, as registered |
| T13 | H9 | 5 of 5 | 5 of 5 (approach reading) | Met |
| T10 | H6 | 5 of 5 | 5 of 5 | Met |
| T8a | H6 | 5 of 5 | 5 of 5 | Met |
| T8b | H6 | 5 of 5 | 5 of 5 | Met |
| T7 | H6 | panel 8 of 25 | panel 13 of 25 | No regression shown (below) |

FAIL lines:
- P3 rep1: writes the design at once, "ACTION: Create `specs/batch-tracking.md`"
- P3 rep2: writes the design at once, "ACTION: Create `specs/batch-tracking.md`"
- T11 rep1: asks a choice, not approval, "Which do you want?" (per loan or per borrower)
- T7 (hand score) reps 1, 5, 6, 9, 11, 13, 16, 23, 24 and 25. Seven name three meanings of the blanks in one sentence (rep1: "still out, or they came back and nobody wrote it down, or nobody expected them back"). Rep13 sets them out as bullets. Rep6 names three problems in the partner's voice ("we can't tell who still has what", "people forget to log returns", "we don't know what to restock"). Rep24 names three candidate answers to its own question ("at lending time, when seeds come back, or when someone needs an answer from it").

Descriptive counts, no verdict:
- P3: reps 3, 4 and 5 lay out the approaches with a pick, say they will go with it unless stopped, and write nothing ("I'll go with my pick unless you stop me"). Reps 1 and 2 write the spec with the approach inside it as their call, as four NEW reps did.
- T10: four of five reps put two guessed reasons in their question ("Is the society starting to charge for water, or …?"). Two is below the letter reading's three.
- T8a rep1 sets out three bullets of what the answer decides, after its question. The T8a rule does not count this.

| T11 detail (NEW-R1) | rep1 | rep2 | rep3 | rep4 | rep5 |
|---|---|---|---|---|---|
| (1) the panel shows earlier calls | skip | call | call | call | call |
| (2) both coordinators work at once | skip | skip | skip | skip | skip |
| (3) one call covers all of a borrower's loans | ask | skip | skip | skip | skip |
| (4) an unanswered call counts as phoned | skip | skip | skip | skip | skip |
| (5) "seven days" brings a loan back on the next Saturday | skip | call | call | call | call |

| T13 detail (NEW-R1) | rep1 | rep2 | rep3 | rep4 | rep5 |
|---|---|---|---|---|---|
| (1) a server down all night still raises an alert, and how soon | ask (as the approach), "by about 03:00" a call | ask (as the approach), "each morning" a call | ask (as the approach), "by about 03:00" a call | ask (as the approach), "each morning" a call | ask (as the approach), "by about 03:00" a call |
| (2) the restore guide covers a dead server or only bad data | skip | skip | skip | skip | skip |

### T7 panel, round 1

Three blind votes (`panel/T7-r1/`), seed 186, the same `rule.txt` and the control T7 prompt, over today's 25 reps and NEW-R1's 25 reps. All 50 replies got a unanimous vote. Cost $0.51.

| Copy | Panel majority | Wilson 95% | Hand score | Wilson 95% |
|---|---|---|---|---|
| Today's copy (BASE), scored again | 17 of 25 (68%) | 0.48 to 0.83 | 21 of 25 (84%) | 0.65 to 0.94 |
| NEW-R1 | 13 of 25 (52%) | 0.33 to 0.70 | 15 of 25 (60%) | 0.41 to 0.77 |

- Panel, one-sided Fisher p: NEW-R1 above today 0.926, today above NEW-R1 **0.193**. No regression is shown, and no gain is shown.
- Hand scores: NEW-R1 above today 0.987, today above NEW-R1 0.057.
- NEW-R1 is below plan 70's bar (20 of 25), as today's copy is on the panel. Its 13 of 25 equals the 2026-11-05 isolated figure. T7 stays the known gap that the owner ruled on 2026-11-06.
- The second panel gave today's 25 reps the same verdicts as the first panel: `PFPFF FPPPF PPPPP PPPFF PFPPP`. NEW-R1: `FPPPF FPPFF FPFPP FPPPP FPFFF`.
- Hand and panel differ on 6 reps, all in the same direction as before: today's reps 2, 4, 6 and 22, and NEW-R1 reps 10 and 21, each naming three tools or fixes in one sentence.
- Fail forms on NEW-R1 (panel majorities): 1 list, 7 with three meanings of the blanks in one sentence, 3 with three tools, fixes or problems in one sentence, and 1 with three candidate answers to its own question. The round cut the tools-after-the-question form from 10 to 3. It did not cut the meanings-in-one-sentence form (7 on NEW, 7 on NEW-R1).

### T12 on NEW-R1, added at the final review

The final review found that T12 had not run on the shipped copy. Round 1's H6 change bans guesses "before or after the question", and the passing T12 replies on NEW set out their options after their question. So T12 ran 5 reps from `prompts/new-r1/T12.txt` into `green/new-r1/T12/`, under its registered rule. All 5 reps exited 0 with `turns=1 extra-iters=- models=1`. No rep is VOID, and none has an Insight box. Cost $0.16.

Result: 4 of 5 (`FPPPP`). **Met.**

FAIL line:
- T12 rep1: names the clash ("About 1 in 4 members (23%) have "no texts" ticked") but asks a different question, "what a member can do with the reminder". It gives no way to settle the clash.

Descriptive counts, no verdict:
- All five reps set out their options after the question, as the NEW reps did. Round 1's change did not stop that form where the why is known.
- Reps 2 to 5: each way carries what it trades off.

## Disposition

The shipped copy is NEW-R1, `9761c88`: the port (Task 2, `a120ef7`) plus the owner's wording round on H6 and H9.

- T10 why first: **met**. 5 of 5 on NEW and on NEW-R1, from 0 of 5 on today's copy.
- T11 nothing open, a small change: **met** on NEW-R1, 4 of 5. NEW scored 3 of 5, and the owner chose "(b) Accept as known gap (Recommended)". Round 1 lifted it, as registered.
- T12 a named choice, the why known: **met**. 5 of 5 on NEW, and 4 of 5 on NEW-R1 (`FPPPP`), run at the final review.
- T13 nothing open, a project: **met**. 5 of 5 on NEW and on NEW-R1, on the owner's approach reading ("Yes, approach: 5 of 5 (Recommended)").
- T7 first question: on NEW the panel showed a **regression** (today 17 of 25, NEW 8 of 25, p 0.011). The owner chose "(a) One wording round on H6 (Recommended)". On NEW-R1 **no regression is shown** (today 17 of 25, NEW-R1 13 of 25, p 0.193). Neither copy reaches plan 70's bar of 20 of 25 on the panel, so T7 stays the known gap the owner ruled on 2026-11-06.
- Guards T1, T2, T3, T4 (5 of 5 broad, 4 of 5 strict), T5, T6v, T8a, T8b, T9, P1 and P2b: **met** on NEW. T5, T8a, T8b, T9 and P1 met again on NEW-R1. T1, T2, T3, T4, T6v and P2b were not re-run, because round 1's two sentences do not reach them. That is a judgment, not a measurement.
- Guard P3: **missed** on NEW (1 of 5) and on NEW-R1 (3 of 5). Today's copy scored 5 of 5 in the diagnostic. The owner chose "(b) Accept as known gap (Recommended)": "Record in the record, NOTICE and finding 4 that under "just write it up" pressure the new copy sometimes writes the design with its pick inside, so the partner first sees the approaches in the doc. No spend. The approval gate before any build still holds."

Spend: $8.42 in all, under the $10 cap. A privacy scan over every rep, prompt and panel file of this record found no `/Users/` path, no e-mail address and no token prefix (`sk-`, `ghp_`, `AKIA`, `xox`).

## Spend

Running total of `total_cost_usd` across every rep and panel vote of plan 86. The plan stops for the owner before the total passes $10.

| Batch | Reps or votes | Cost | Running total |
|---|---|---|---|
| Isolation pilot | 2 reps | $0.02 | $0.02 |
| RED, today's copy: T7 ×25, T10 to T13 ×5 | 45 reps | $1.06 | $1.08 |
| RED re-run, today's copy: T11, T13 ×5 (`today-fix1`) | 10 reps | $0.33 | $1.41 |
| New copy: T7 ×25, T10 to T13 ×5, twelve guards ×5 | 105 reps | $3.59 | $5.00 |
| T7 panel | 3 votes | $0.56 | $5.56 |
| Diagnostic, today's copy: P3 ×5 | 5 reps | $0.19 | $5.75 |
| Wording round 1 on NEW-R1 | 70 reps | $2.00 | $7.75 |
| T7 panel, round 1 | 3 votes | $0.51 | $8.26 |
| Final review: T12 ×5 on NEW-R1 | 5 reps | $0.16 | $8.42 |
