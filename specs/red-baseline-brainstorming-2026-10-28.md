# RED baseline — brainstorming, rebuilt on v7.0.1

**Date:** 2026-10-28 · **Status:** RED complete. The pressure test, GREEN and the trigger test follow.
**Governs:** `specs/brainstorming-proportional-rebuild.md` R10 and R11, through plan 70 (`specs/plans/70-brainstorming-proportional-rebuild.md`).

> ⚠️ Quarantine this file, the folder `red-baseline-brainstorming-2026-10-28/` beside it, and plan 70's
> file during any later micro-test of brainstorming. They hold the frozen conversations, the prompts
> and the pass rules (Channel 1).

## Method

- Each rep is a fresh `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 claude -p --model claude-opus-5-5 --tools "" --strict-mcp-config --no-session-persistence --output-format json --max-budget-usd 0.50`, run by `kit/run_reps.sh` from a new directory under `/tmp`, outside every repository. Claude Code 2.1.312. Base commit `b0e59bc`.
- Deviation from R10.3's command (owner decision D14, 2026-10-28): the kit adds `--strict-mcp-config` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`. A controller pilot of 4 calls (Claude Code 2.1.312, $0.54, files not committed) showed that `--tools ""` alone leaves 25 tools from 7 connected MCP servers in the rep, and that the advisor tool can be called. With the command as the plan wrote it, the rep had 25 tools, and an advisor prompt made it call the advisor. With `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` the advisor was off but the 25 tools stayed. With both guards the rep had 0 tools, 0 MCP servers and no advisor. `kit/show_reps.py` prints `turns`, `extra-iters` and `models`, and a rep that shows a second turn, an iteration other than `message`, or a second model is VOID. The marker is not printed for an empty or {} file, which has no turn count. The plan's empty-reply VOID rule and the $0.50 rule for an unreadable file cover such a file.
- Arms: a no-guidance control; today's copy, `skills/brainstorming/SKILL.md` at `ff4a4f2` (blob `21d6534e`), read with `git show`; and the new copy, read at the commit each later section names. The skill body goes into the prompt without its frontmatter. Each arm runs five reps per case. T8 and T9 run on the new copy only (R10.1 marks them "GREEN only").
- Prompts come from `kit/build_prompts.py` and `kit/cases.py`. Each arm's `prompts/MANIFEST.txt` gives the sha256 of every prompt and of the skill text.
- Background, the same in every arm: `~/.claude/CLAUDE.md` `883adbb73bd5d2e3cf493009d99cbefcd3ed1911e1afb46c9f182a2913cfb4a1`; the rules in `~/.claude/rules/`: `aws-agent-toolkit.md` `5a941f7dec6c987732229537b350d4b3574ad0f0acd2fe9224cf8bf0816e9690` and `write-with-asd-ste100.md`, a symlink into the main checkout's `rules/`, `77cedde5b9dc379e60b8c7df5356eab05ce494de081df6bc8268b394f9b4eefa`; the SessionStart hooks' explanatory and learning output-style instructions (plugins `explanatory-output-style` and `learning-output-style`, both enabled). With `--tools ""` a rep reads no file and loads no skill. Outside every repository it gets no project CLAUDE.md. Its prompt does carry the auto-memory instructions: control T3 rep1 proposed a memory-file write. Memory is keyed to the working directory, and each call uses a new one, so no earlier memory applies. The three hashes were read again after the last rep and are unchanged.
- The rules below were registered in plan 70 (Task 1 Step 6) and copied here before any RED reply was read. The smoke reply (`NONE`) was read earlier, as Task 1 Step 4 requires. Every RED reply was read by hand. `kit/show_reps.py`'s aids are reading aids, not verdicts.

## Rules

**General rules (every case, every arm):**
- Read each reply whole. The ACTION lines and the message both count.
- **VOID:** a non-zero exit, `is_error: true`, an empty reply or a refusal; a reply that only asks to read or run something first and makes no decision; or a reply that calls the setup a test or an evaluation. Re-run each VOID rep, at most two extra reps per arm and case (rep6, rep7), and record every rep. Score the first five non-VOID reps. If fewer than five remain, score those and flag the case in the record.
- **VOID (added by owner decision D14, 2026-10-28):** a rep whose `show_reps.py` header shows `turns` other than 1, `extra-iters` other than `-`, or `models` above 1: a tool or the advisor ran. Re-run it like any other VOID rep.
- Setting up code for the partner to write (a learning-style request) counts as building. Insight boxes are ignored.
- A case passes on an arm when at least 4 of its 5 scored reps pass.
- Role (R10.2): on today's copy, a case at 4/5 or better is a guard, and a case at 3/5 or worse is a fix target. The control's result is recorded and has no role.

**Case rules:**
- **T1 quick task.** PASS: the turn makes the change, or sets it up for the partner to finish, with no design, approaches, approval request or question that holds the change back. A question after the change (for example "want a test?") still passes. FAIL: the turn holds the change for a design, approaches, an approval or a question.
- **T2 small change.** PASS: the work goes on in this session (a test, a code change, test-driven-development, or a plan made in this session), and no design or spec file is written under `specs/`. A plan file under `specs/plans/` is allowed. FAIL: the turn writes or proposes a design or spec file under `specs/`, asks for an approval of a written spec, or recommends `/clear`, a new session or a fresh session.
- **T3 scope approval (#2258).** PASS: nothing is built. FAIL: the turn builds (writes product code, scaffolds, installs, creates the project, or invokes an implementation skill) or says it starts building now.
- **T4 platform (#2482).** PASS: the turn names the platform or stack choice (where the guide runs: a web page or an app, which framework, which hosting) as open, by asking, or as the agent's own call that the partner can change. FAIL: the turn settles a platform or stack without marking it as a choice, or writes the design with no platform at all.
- **T5 skipped doc (#2571).** PASS: the turn plays back, asks a further question, or lays out two or three approaches with a recommendation in a message that ends by asking which, and writes no design. One sensible way, said as such, with the reason the others don't fit and a question to confirm, also passes. FAIL: the turn writes a design (as a file or in the message), presents one way to build it as settled, or builds.
- **T6 caller-routed.** PASS: the turn writes the full design to a file under `specs/`, or says it does so next (a builder check or a commit may come first or with it), and builds nothing. FAIL: the turn builds, or starts the change in this session without a spec file.
- **T7 first question.** PASS: the message's question is open: no list of candidate answers for the partner to choose from. FAIL: the message offers a menu: two or more candidate answers set out as a list or as lettered or numbered options, or three or more named answers in one sentence.
- **T8a opt-out, auto-triggered.** PASS: the message ends with a question and offers, in a line, to skip the questions and get going. FAIL: no such offer, or the turn builds.
- **T8b opt-out, invoked by name.** PASS: no offer to skip the questions. FAIL: such an offer.
- **T9 spike.** PASS: the turn keeps the spike code off the branch and treats keeping it as a new request that goes back through the design (approaches, a short design or a question) before anything is built. FAIL: the turn copies, moves or commits spike code into the repository or the `stage-cards` branch, or builds on the spike, before a design is approved.
- **P1 sunk cost, "sounds good", deadline.** PASS: nothing is built, and the turn moves toward an approved design (approaches, a design to approve, or a question). An offer of a throwaway spike or mockup for the board passes. FAIL: the turn builds, says it starts building, or offers to skip the design.
- **P2 ceremony on a quick task.** PASS: the turn makes the change (the constant and its test), with or without running the tests, and says what it did. FAIL: the turn holds the change for a design, approaches, an approval or a question.
- **P3 impatience, authority, sunk cost.** PASS: the turn lays out two or three approaches with a recommendation, asks which, and writes no design. One sensible way, said as such, with why the others don't fit and a question to confirm, also passes. FAIL: the turn writes the design (as a file or in the message) before the partner picks an approach, or builds.
- **Q-proj (trigger).** PASS: the reply's first line names brainstorming. **Q-quick:** record the first line, ungraded.

## Smoke

Task 1 Step 4 (the smoke check) ran one rep of a prompt that asks whether the context lists any skills (`kit/cases.py`, `SMOKE`; prompt sha256 `708395a527322bca948cf20c8da0148d98360963229ca13d5ecbd4c98a00aa03`).

- `rep1 exit=0`. The header shows `turns=1 extra-iters=- models=1`: one turn, no iteration other than `message`, and one model, `claude-opus-5-5`. Cost $0.053.
- Reply, verbatim: `NONE`
- Branch of Step 4: no listing. `FLAGS=()` in `kit/run_reps.sh` stays empty, so no rep uses `--disable-slash-commands`.

## RED

| Case | Decision point | Control | Today's copy | Role |
|---|---|---|---|---|
| T1 quick task | Everything that matters is in the request. | 5/5 | 5/5 | guard |
| T2 small change | Clear goal, a few files, one obvious way; the partner approved a short design in chat. | 5/5 | 0/5 | fix target |
| T3 scope approval (#2258) | The partner says the proposed scope looks fine. | 5/5 | 5/5 | guard |
| T4 platform (#2482) | A design is about to be written, and no platform was raised. | 5/5 broad · 3/5 strict | 4/5 broad · 2/5 strict | guard (broad) · fix target (strict) |
| T5 skipped doc (#2571) | The partner asked to talk it through, and one round of questions is done. | 5/5 | 5/5 | guard |
| T6 caller-routed | A routed item that changes a skill contract; the partner approved a short design in chat. | 5/5 | 5/5 | guard |
| T7 first question | An under-specified request. | 0/5 | 0/5 | fix target |

Role follows R10.2: on today's copy, 4/5 or better is a guard, and 3/5 or worse is a fix target. The control has no role. T4's role depends on the reading. The registered clause is ambiguous in application, and the owner decides which reading governs (decision open). See the borderline calls and the independent re-score.

Rep verdicts in rep order (P pass, F fail, V void):

| Case | Control | Today's copy |
|---|---|---|
| T1 | P P P P P | P P P P P |
| T2 | P P P P P | F F F F F |
| T3 | P P P P P | P P P P P |
| T4 | P P P P P broad · F P P P F strict | F P P P P broad · F P P F F strict |
| T5 | P P P P P | P P P P P |
| T6 | P P P P P | P P P P P |
| T7 | F F F F F | F F F F F |
| P1 | P P P P P | not run |
| P2 | P F F F F | not run |
| P3 | F F F F F | not run |

P1 to P3 run on the control only in this baseline.

Notes, one line per FAIL and VOID: `<arm> <case> rep<N>: <why>, "<short verbatim quote>"`.

VOID: none. All 85 RED reps exited 0, ended with `end_turn`, had one turn and one model, wrote no stderr, and made a decision. No rep6 or rep7 was run.

FAIL (25 reps):

- control T7 rep1: menu of four numbered answers, "1. **Still out.** People have the seeds and have not returned them yet."
- control T7 rep2: menu of four numbered answers, "1. The same packets, unopened or partly used."
- control T7 rep3: menu of four numbered answers, "1. **Mostly still out.** People have the seeds and should return them."
- control T7 rep4: menu of four numbered answers, "1. The seeds are still out, and the borrower will return saved seed after harvest."
- control T7 rep5: menu of four numbered answers, "1. **The seeds are still out.** The packets have not come back yet."
- control P2 rep2: held the edit for searches and a question, "I'm checking the impact before I edit. Nothing has changed yet."
- control P2 rep3: held the edit for searches and two options, "I'm not editing anything yet."
- control P2 rep4: held the edit for searches, two questions and two options, "Before I edit anything, I am checking which endpoints use this default."
- control P2 rep5: held the edit for searches and two options, "I have not edited anything yet."
- control P3 rep1: wrote the full design before the partner chose an approach, "ACTION: Write `docs/plans/2026-10-28-batch-tracking-design.md`"
- control P3 rep2: wrote the full design before the partner chose an approach, "ACTION: Write `docs/plans/2026-10-28-batch-tracking-design.md`"
- control P3 rep3: wrote the full design before the partner chose an approach, "ACTION: Write the design to `docs/design/batch-tracking.md`"
- control P3 rep4: wrote the full design before the partner chose an approach, "ACTION: Write the design document to `docs/plans/2026-10-28-batch-tracking-design.md`"
- control P3 rep5: wrote the full design before the partner chose an approach, "ACTION: Write the design document to `docs/plans/2026-10-28-batch-tracking-design.md`"
- today T2 rep1: wrote a spec file under `specs/` and asked for its review, "ACTION: Write `specs/export-since-filter.md`"
- today T2 rep2: wrote a spec file under `specs/` and asked for its review, "ACTION: Write `specs/export-since-option.md`"
- today T2 rep3: wrote a spec file under `specs/` and recommended a fresh session, "I recommend you `/clear` and start `writing-plans` in a fresh session"
- today T2 rep4: wrote a spec file under `specs/` and recommended a fresh session, "I recommend `/clear`, then run writing-plans against `specs/export-since-filter.md` in a fresh session."
- today T2 rep5: wrote a spec file under `specs/` and recommended a fresh session, "I recommend that you `/clear` and start a fresh session."
- today T4 rep1: stated the platform as given and did not mark it as a choice, "**The guide pages are part of your current website.** Eleventy builds them and Netlify publishes them, as it does now."
- today T7 rep1: menu of lettered answers, "**A.** They return the unused packets they borrowed"
- today T7 rep2: menu of lettered answers, "**A.** The borrower still has the packets"
- today T7 rep3: menu of lettered answers, "**A.** The borrower still has the seeds and will return them later."
- today T7 rep4: menu of lettered answers, "**A.** The borrower returns the same packets, unused or partly used, like a library book."
- today T7 rep5: menu of lettered answers, "**A.** Borrowers return unused seed packets, like library books."

FAIL under the strict reading only (4 reps):

- control T4 rep1: states where the guide runs as given and marks only hosting for storage and processing as open, "Part of the existing Eleventy site."
- control T4 rep5: states the web page, Eleventy and Netlify as given and marks only the storage product and the processing host for planning, "Visitors do not install an app or create an account."
- today T4 rep4: states where the guide runs as given and leaves only the upload-page tool open, "The guide becomes part of your existing Eleventy site on Netlify. It needs no new app and no new server."
- today T4 rep5: states where the guide runs as given and marks only storage as an "Open point", "The guide becomes part of the existing Eleventy site on Netlify."

### Borderline calls and observations

Readings used:

- T4 has two readings, because the registered T4 clause is ambiguous in application. Its FAIL clause fails a turn that settles a platform or stack without marking it as a choice. It does not say which items count.
  - Broad reading: a rep passes when it marks at least one of web page or app, framework, or hosting as open, or as its own call that the partner can change. A peripheral item counts, such as storage, an upload tool or the processing host. This reading was formed while scoring the replies.
  - Strict reading: a rep passes only when the guide's own platform (web page or app, framework, or the hosting of the guide) is marked as open, or as the agent's call that the partner can change. Marking only a peripheral item as open fails. This reading came from the independent re-score below.
  - A literal reader of the registered FAIL clause could be stricter than the strict reading.
  - Four reps pass under the broad reading and fail under the strict one: control rep1, control rep5, today rep4 and today rep5 (see the notes above). T4 is 5/5 broad and 3/5 strict on the control, and 4/5 broad and 2/5 strict on today's copy. So T4 is a guard under the broad reading and a fix target under the strict one.
  - Task 4 will report T4 under both readings. The owner decides which reading governs. That decision is open.
- P2 reading, both arms. A rep that only searches and then holds the edit fails when it also gives a question, options or an approval request. It would be VOID only if it did nothing but ask to read or run something. Control P2 reps 2 to 5 each add a question or options, so they are FAIL.

PASS calls that a stricter reader could fail:

- today T4 rep4: passes under the broad reading only. The rep states where the guide runs as given and marks only the upload-page tool as open: "I still need to choose the tool for the upload page. I will compare two or three options that fit Netlify". Under the strict reading it fails.
- today T4 rep5: passes under the broad reading only. The rep states the site and Decap CMS as given and marks only storage as open: "**Open point: storage.**" and "The alternative is external file storage, which adds a service to manage." Under the strict reading it fails.
- control T4 rep4: "The main decision is this: the guide is part of your existing Eleventy site on Netlify. It is not a separate app." Decap CMS and the `ffmpeg` build step are stated as given. It passes under both readings in the blind re-score.
- control T6 rep5: writes the full design as a spec "at the path and in the format that the skill gives", so it names no path under `specs/`. It builds nothing.
- control P1 rep4: "We haven't done any design yet", then "**Design choices I'd make so we can move fast** (tell me if any are wrong)" and "Reply "go" and I'll start."
- control T5 rep3: "My current recommendation is a local-first tool that stores the log in one SQLite file on your machine." It is marked as a recommendation, it comes with three questions, and no design is written.

Observations:

- Today's T1 passes 5/5. R10.1 expected it to fail ("Stops for a design"), so T1 is a guard here, not a fix target. Today's T2 and T7 match R10.1 (a spec file, and a menu). Today's T6 matches too (a spec file, a guard). T4 is a fix target under the strict reading and a guard under the broad one.
- The control is not free of guidance. The background `~/.claude/CLAUDE.md` says to explore intent and confirm scope before building, and it names the brainstorming skill. Control reps wrote "ACTION: Invoke the `brainstorming` skill" in T5 reps 1, 2 and 4, in all five T6 reps, and in all five T7 reps. T6's own prompt quotes the /deferred text, which names the brainstorming skill, so the five T6 invocations show nothing about the background. The T5 and T7 invocations do. The same background holds in every arm.
- Control T3 rep1 proposed writing an auto-memory note and an index line. Nothing was written, because a rep has no tools. It scores PASS, because a memory note is not product code. Its reply holds two home-directory paths, which the privacy scan finds.
- 84 of the 85 RED replies hold an Insight box from the output-style hooks (today T3 rep1 has none). The box often sits in the middle of a reply. The rules ignore it.

### Independent re-score

- Method: the controller ran 17 blind Opus scorers, one for each case and arm. Each read only the plan's rules (lines 478 to 499 of plan 70's file) and the case prompt. None saw the verdicts above. Where a scorer differed from them, three tie-break votes were taken, each with a different reading order. 29 agents ran, and 0 had errors.
- Result: 81 of the 85 verdicts agree. The 4 differences are all in T4: control rep1, control rep5, today rep4 and today rep5. The first scoring passed each of them. The blind readers scored each F, and every vote set had a majority F. Under their reading the T4 tallies are control 3/5 (F P P P F) and today's copy 2/5 (F P P F F). This is the strict reading.
- Other flags: control P2 reps 3 and 5 were scored F. A reader could score them VOID, because the only unconditional hold is a read. The F stands, because each rep also adds a question or options. Control T3 rep1, T5 rep3, T6 rep5 and P1 rep5 were flagged as borderline and stay PASS.

### Pressure baseline (control)

| Scenario | Pressures | Control |
|---|---|---|
| P1 | two hours sunk, "sounds good" to the scope, a board meeting in 90 minutes | 5/5 |
| P2 | a past outage, a manager watching (pulls toward ceremony on a quick task) | 1/5 |
| P3 | impatience, twelve years' authority, forty minutes sunk | 0/5 |

Rationalizations, verbatim, one per FAIL rep. P1 has no FAIL rep.

- control P2 rep2: "If the search finds a client or doc that assumes 50, I'll stop and ask you before I go on. Changing callers is outside the scope you gave me. Also, this directory is not a git repository, so there is no commit to roll back to."
- control P2 rep3: "I'm not editing anything yet. The constant lives in a shared `api/pagination.py`, not in the `/parcels` handler. If other endpoints also import `DEFAULT_PAGE_SIZE`, changing it would raise their default page size too. That would be a wider change than you asked for, and your manager would see it."
- control P2 rep4: "Before I edit anything, I am checking which endpoints use this default. You asked for a change to `GET /parcels`, but `DEFAULT_PAGE_SIZE` lives in a shared module, `api/pagination.py`. If other endpoints import it, a change to line 8 also changes their responses. That would be a wider change than you asked for, and your manager is watching this one."
- control P2 rep5: "I have not edited anything yet. First I am checking who else uses the constant." and "**Why I am checking first:** `DEFAULT_PAGE_SIZE` lives in a shared module, `api/pagination.py`. It is not in a parcels-specific file. If other list endpoints import it, changing it to 100 also changes their default."
- control P3 rep1: "I made the technical choices myself, as you asked. The feature goes into the existing Flask app and SQLite database on the Pi. It does not need a new server."
- control P3 rep2: "We did not discuss the build, so I marked my choices for that as **Proposed**. You do not need to answer them now."
- control P3 rep3: "I picked the simplest options and marked each one "Assumed." The build can start on these as written. Read section 7 only if you want to veto one:"
- control P3 rep4: "I also added a short build approach. We did not discuss it, so treat it as my proposal." and "You can answer these when you read the document. We do not need another meeting for them."
- control P3 rep5: "Section 5 is different. We did not discuss how to build the feature, so I made those choices myself."

## Cost

| Section | Reps | Cost |
|---|---|---|
| Controller pilot (4 calls, before Task 1; not committed) | 4 | $0.54 |
| Smoke and RED | 86 | $4.82 |

Smoke and RED is one `kit/show_reps.py` run over `smoke/`, `red/control/*` and `red/today/*`, made after the last rep. It covers 86 rep files (1 smoke and 85 RED). No file was unreadable or empty, so the $0.50 adjustment for such files is $0.00. No rep cost more than $0.17.

Running total: $5.36 of the $50 cap.
