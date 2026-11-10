# RED baseline — brainstorming, the v7.0.2 retune (plan 86)

**Date:** 2026-11-10 · **Status:** Rules registered. No rep has run yet.
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

## Spend

Running total of `total_cost_usd` across every rep and panel vote of plan 86. The plan stops for the owner before the total passes $10.

| Batch | Reps or votes | Cost | Running total |
|---|---|---|---|
| (none yet) | 0 | $0.00 | $0.00 |
