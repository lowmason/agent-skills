# RED baseline — brainstorming improvements (plan 106)

**Date:** 2026-11-22 · **Status:** Complete. Round A met every bar. Round B met every bar except the T4 platform case on its strict reading (3 of 5), which the owner accepted as a known gap after the diagnostic and the revert arms. P3 met its bar (5 of 5), so its known gap is closed. The T7 panel shows no regression and no gain. The agy probe printed ALIVE, so `visual-companion.md` gives the proven launch line (Form 1). Total spend $8.57.
**Governs:** plan 106 (`specs/plans/completed/106-brainstorming-improvements.md`), items 1, 2, 4, 5, 6 and 8 of the brainstorming findings (`specs/completed/brainstorming-improvements.md`).

> ⚠️ Quarantine this file, the folder `red-baseline-brainstorming-improvements/` beside it, and plan 106's
> file during any later micro-test of brainstorming whose reps have tools. They hold the frozen
> conversations, the prompts and the pass rules (Channel 1).

## Method

- BASE is `e556640fad64907a394be3ba6c163821481e9a49`. At BASE, `skills/brainstorming/SKILL.md` is blob `ce3e076ab82a24229c838295f40b1fd5cb530f0a` (sha256 `b4eb161b…`). Its body (the text after the frontmatter) has 19,524 characters, sha256 `f6067e3a10f9e2ec46a6ec11cb861abb9fcc1d6c60a97ca3995f311487542f7a`, the same body as plan 86's NEW-R1 (`9761c88`). Claude Code is 2.1.323.
- The kit is in `red-baseline-brainstorming-improvements/kit/`. Its files and their sources:
  - `cases.py`, `build_prompts.py`, `show_reps.py`, `panel.py` and `run_reps.sh`: plan 86's kit (`red-baseline-brainstorming-v7-0-2/kit/`, last changed in `65e850a`). The cases are unchanged. Docstrings say "plan 106", and the temp prefixes are `plan106-rep-` and `plan106-panel-`.
  - `postprocess.py`, `test_postprocess.py`, `kit_identity.py` and `check_scrub.py`: plan 103's merged kit (`red-baseline-worktree-skills-fix/kit/`, commit `d0671aee79d450c3a7292e9fabe7fc61b9592049`), unchanged.
  - `privacy_sweep.py`: plan 97's review kit (`red-baseline-change-reverted-mutant/review-kit/`, `d0f0f0c`), unchanged. It reads the identity forms from `kit_identity.py`, which is byte-identical to plan 97's copy.
  - `isolation_probe.txt`: plan 104's 8-question probe (`red-baseline-mutant-screen-runs/kit/`, `a3c0f20`), unchanged.
  - `test_kit.py`: new. It runs the kit's real files on a stub `claude`, with no model. Suite `brainstorming-improvements-kit` in `build/suites.toml`.
- The next-kit fixes. `run_reps.sh` writes each rep's raw JSON and stderr to `~/.cache/agent-skills/scratch/plan106-brainstorming-improvements/`, outside the repository, and writes `postprocess(raw)` to `rep<N>.json`. A kept rep has `void` false, no `origin` and no `credential_expires_at` (nor `session_id` or `uuid`), and its text goes through the identity scrub. A rep whose raw JSON has `result_index` above 0 or a non-null `origin` (a peer message reached it), or whose raw output is not a JSON object, is written as `{"void": true, "reason": ...}` with none of its text. `show_reps.py` prints `rep<N> VOID (<reason>)` for it, and `panel.py`'s `gather` skips it. `panel.py`'s `call_voter` returns `postprocess` of each vote's JSON, and `run` stops before `panel-verdicts.json` when a vote comes back void.
- Each rep runs `kit/run_reps.sh`. The command is `env -i HOME USER LOGNAME PATH SHELL TMPDIR LANG CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 claude -p --model claude-opus-5-5 --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format json --max-budget-usd 0.50`, plan 86's flags. Each rep runs once, from its own new folder under `/tmp`, outside every repository. Panel votes run the same way through `kit/panel.py`. Nobody messages or subscribes to a running rep or vote.
- The model is `claude-opus-5-5`.
- Arms: the shipped copy (`SKILL.md` at BASE), A (the shipped copy plus item 1, the commit of plan 106 Task 2 Step 3) and B (A plus items 6, 2, 4 and 5, the commit of Task 3 Step 4). Each is read with `git show`. The skill body goes into the prompt without its frontmatter. Each prompt folder's `MANIFEST.txt` gives the sha256 of every prompt and of the skill text.
- `claude --version` is recorded beside each batch in Spend.
- Background: none, by isolation. The isolation pilot (below) checks this before any case rep.
- The rules below were registered, and this file committed, before any rep ran.

## Rules

Plan 86's record (`specs/baseline/red-baseline-brainstorming-v7-0-2.md`), section Rules, applies as written: the general rules, plan 70's cases as registered there, and the rules for T7, T5, P3, T8a and T10 to T13, with the owner's approach reading for T13 (that record, Owner rulings at the Task 3 gate). The descriptive counts are kept. The fixture check does not apply, because no fixture changes.

Added here:
- A rep or vote whose file reads `void` True (a peer message reached it) is VOID. It gets a replacement rep, the next free number, under the general rule's limit of two extra reps for each VOID rep.
- Isolation probe: a YES on line 7 (the user's name or e-mail) is recorded and does not stop the run, because the identity scrub covers every rep and vote file and the privacy sweep runs before each commit. A YES on any other line stops the run for the owner.
- A reply that names the user is scored as written. The scrub replaces the name in the file. The verdict does not depend on it.

## Bars

Round A (A: the shipped copy plus item 1):
- T1, T2, T3, T4 (both readings), T5, T6v, T8a, T8b, T9, P1, P2b: each at least 4 of 5.
- P3: at least 3 of 5, its shipped figure (a known gap).

Round B (B: A plus items 6, 2, 4 and 5):
- T10, T11, T12, T13 and the twelve guards, P3 included: each at least 4 of 5.
- T7: the shipped copy's 25 committed reps (`specs/baseline/red-baseline-brainstorming-v7-0-2/green/new-r1/T7/`) and B's 25 scored reps, in one blind panel under plan 86's T7 rule. A regression is shown when `fisher_one_sided(shipped, b)` is below 0.05, and a gain when `fisher_one_sided(b, shipped)` is below 0.05. Plan 70's bar of 20 of 25 is context, not a bar. The shipped reps ran on Claude Code 2.1.316, so a difference may come from the CLI as well as the text.

A guard that misses its bar also runs 5 reps on the shipped copy as a diagnostic, reported beside the miss.

Regression: a case below its bar, except P3 at exactly 3 of 5 in round B (item 4 missed its target, and nothing got worse).

Outcomes. All bars met and no T7 regression: the round stands. A regression in round B first re-runs that case on each "B without item N" arm, for items 2, 4 and 5, at 5 reps, and reports which arm restores it. A T7 regression goes to the owner before any re-run on revert arms. Every missed bar, regression or P3 miss is then an owner gate, with three choices: (a) one wording round, its new text written into this record before any rep, the case and the guards its passage reaches re-run at 5 reps; (b) accept the miss as a known gap, recorded here and in `NOTICE`; (c) revert the hunk the miss points to. No skill text changes without the owner's choice. Round A has no choice (a): its edits only remove text.

## Isolation pilot

Two reps of `kit/isolation_probe.txt` (plan 104's 8-question probe) ran into `isolation-pilot/` on 2026-11-22 with Claude Code 2.1.323. Both exited 0 and show `turns=1 extra-iters=- models=1`. Neither is VOID. Cost $0.05.

- Lines 1 to 5 (CLAUDE.md, output style, rules, SessionStart hook text, auto-memory) and line 8 (other sessions) read NO in both reps.
- Line 7 (the user's name or e-mail) reads YES in both reps, a recorded YES under the line-7 rule. Each rep quotes the address sentence of the session's own context. The scrub replaced the address with `<USER-EMAIL>` in both rep files, so the scrub worked on a live rep. Rep2 adds "No name is given."
- **Line 6 (a list of available skills or slash commands, or a skill named writing-skills) reads YES in both reps.** Both quote one sentence about a built-in command: "/code-review ultra launches a multi-agent cloud review of the current branch". Both also say that no skill list is present: rep1, "these are mentions of slash commands in session guidance, not a formal list of skills"; rep2, "There is no skills list and no writing-skills". Under the registered rule, a YES on a line other than 7 stops the run for the owner. Plan 104's probe on the same Claude Code version saw the same guidance and answered NO with a note, and its controller read line 6 as NO ("its note names built-in commands in the session's guidance, not a skill list", `red-baseline-mutant-screen-runs.md`, the `opus` probe). The owner ruled (2026-11-22): "Read as NO, go on (Recommended)": "Record line 6 as a NO on substance, as plan 104 did: the text is built-in guidance that names a command, not a skill list. Quote this ruling in the record, commit the pilot and start Task 2. No spend."

Result: the pilot passes under the line-7 rule and the owner's line-6 ruling. Every later batch's Claude Code version is checked against 2.1.323, the pilot's version.

## Round A

Arm A (`22f58614d0d4f983bed23a759c9e26fe70d1cf43`): the shipped copy plus item 1 (edits I1a to I1c). The `SKILL.md` body has 19,054 characters, sha256 `143b293e4595d1621bdff4068c14d3b238ca6a87ea2639957311b0ca7f598e94`, as planned. Prompts are in `prompts/a/`, and reps in `round-a/<case>/`. Each prompt in `prompts/a/` differs from the same case in `prompts/shipped/` only inside the `<skill name="brainstorming">` block. Each prompt in `prompts/shipped/` is byte-identical to the same case in plan 86's `prompts/new-r1/`. Run on 2026-11-22 with Claude Code 2.1.323 (checked before each case), `claude-opus-5-5`.

All 60 reps exited 0 with `turns=1 extra-iters=- models=1`. No rep is VOID, none has an Insight box, and none quotes a user-level file. No replacement rep ran.

| Guard | Shipped figure (plan 86) | Round A | Bar | Verdict |
|---|---|---|---|---|
| T1 | 5 of 5 (NEW) | 5 of 5 | 4 of 5 | Met |
| T2 | 5 of 5 (NEW) | 5 of 5 | 4 of 5 | Met |
| T3 | 5 of 5 (NEW) | 5 of 5 | 4 of 5 | Met |
| T4 broad | 5 of 5 (NEW) | 5 of 5 | 4 of 5 | Met |
| T4 strict | 4 of 5 (NEW) | 5 of 5 | 4 of 5 | Met |
| T5 | 5 of 5 (NEW-R1) | 5 of 5 | 4 of 5 | Met |
| T6v | 5 of 5 (NEW) | 5 of 5 | 4 of 5 | Met |
| T8a | 5 of 5 (NEW-R1) | 5 of 5 | 4 of 5 | Met |
| T8b | 5 of 5 (NEW-R1) | 5 of 5 | 4 of 5 | Met |
| T9 | 5 of 5 (NEW-R1) | 5 of 5 | 4 of 5 | Met |
| P1 | 5 of 5 (NEW-R1) | 5 of 5 | 4 of 5 | Met |
| P2b | 5 of 5 (NEW) | 5 of 5 | 4 of 5 | Met |
| P3 | 3 of 5 (NEW-R1) | 3 of 5 | 3 of 5 | Met |

The shipped figures come from plan 86's record. Plan 86 ran T1, T2, T3, T4, T6v and P2b on NEW (`a120ef7`) and did not re-run them on NEW-R1, the shipped copy: its wording round did not reach them, a judgment, not a measurement.

Rep verdicts in rep order (P pass, F fail):
- T1 `PPPPP`, T2 `PPPPP`, T3 `PPPPP`, T4 broad `PPPPP`, T4 strict `PPPPP`, T5 `PPPPP`, T6v `PPPPP`, T8a `PPPPP`, T8b `PPPPP`, T9 `PPPPP`, P1 `PPPPP`, P2b `PPPPP`, P3 `PPFPF`

FAIL lines:
- P3 rep3: writes the design before the partner sees the approaches, "ACTION: Create `specs/batch-tracking.md`" ("We didn't discuss how to build it, so I made that call.")
- P3 rep5: writes the design before the partner sees the approaches, "ACTION: Create `specs/batch-tracking.md`"

VOID lines: none.

Borderline calls:
- T4 rep1, strict reading: it states a web page as shared by all three ways ("Every approach shares the visitor side") and leaves where the guide lives open (the existing site, separate storage, or a ready-made guide service). The hosting of the guide is one of the strict reading's items, so it passes.
- P3 reps 1, 2 and 4 pass on the third clause: each lays out three ways with a pick, says it will go with the pick unless stopped, and writes nothing. Rep1: "Since you've handed me the how, I'll go with my pick below unless you object, and write the design up in my next message."

Descriptive counts, no verdict:
- P3: the two FAIL reps write the spec with the approach inside as their own call, the form plan 86 recorded on NEW and NEW-R1. Reps 1, 2 and 4 give "handed me the how" or "left the build to me" as the reason for making the pick themselves.
- T6v: all five reps say the folder is not a git repository and ask whether to run `git init`. The reps run in a new folder under `/tmp`, and Claude Code's environment block says so. P2b reps 2 and 5 and P3 reps 1, 2 and 5 say the same. The text is the same in every arm.
- Cost: round A's 60 reps cost $2.46, about $0.041 a rep, against about $0.034 in plan 86's new-copy batch.

Diagnostics: none ran, since every guard met its bar.

Owner gate: none, since no bar was missed (Bars, Outcomes).

## Round B

Arm B (`7cc303c87818d0565f4cac8cb92f84f39ea004f9`): A plus items 6, 2, 4 and 5, one commit each. The commits are item 6 `f1ae67d` (edit I6), item 2 `0c39f0e` (edits I2a to I2d), item 4 `dbadbab` (edit I4) and item 5 `7cc303c` (edit I5). The `SKILL.md` body has 19,385 characters, sha256 `2bccdaeda4c8c6ba64470f4dd9c9ad061daea57ca994445571fa3a8d45353ba9`, as planned, within the 19,700 cap. Prompts are in `prompts/b/`, and reps in `round-b/<case>/`. Each prompt in `prompts/b/` differs from the same case in `prompts/a/` only inside the `<skill name="brainstorming">` block. Run on 2026-11-22 with Claude Code 2.1.323 (checked before each case), `claude-opus-5-5`.

All 105 reps exited 0 with `turns=1 extra-iters=- models=1`. No rep is VOID, none has an Insight box, and none quotes a user-level file. No replacement rep ran.

| Case | Shipped figure (plan 86) | Round B | Bar | Verdict |
|---|---|---|---|---|
| T10 | 5 of 5 (NEW-R1) | 5 of 5 | 4 of 5 | Met |
| T11 | 4 of 5 (NEW-R1) | 4 of 5 | 4 of 5 | Met |
| T12 | 4 of 5 (NEW-R1, final review) | 4 of 5 | 4 of 5 | Met |
| T13 | 5 of 5 (NEW-R1, approach reading) | 4 of 5 (approach reading) | 4 of 5 | Met |
| T1 | 5 of 5 (NEW) | 5 of 5 | 4 of 5 | Met |
| T2 | 5 of 5 (NEW) | 5 of 5 | 4 of 5 | Met |
| T3 | 5 of 5 (NEW) | 5 of 5 | 4 of 5 | Met |
| T4 broad | 5 of 5 (NEW) | 5 of 5 | 4 of 5 | Met |
| T4 strict | 4 of 5 (NEW) | 3 of 5 | 4 of 5 | **Missed**: a known gap, by the owner's ruling below |
| T5 | 5 of 5 (NEW-R1) | 5 of 5 | 4 of 5 | Met |
| T6v | 5 of 5 (NEW) | 5 of 5 | 4 of 5 | Met |
| T8a | 5 of 5 (NEW-R1) | 5 of 5 | 4 of 5 | Met |
| T8b | 5 of 5 (NEW-R1) | 5 of 5 | 4 of 5 | Met |
| T9 | 5 of 5 (NEW-R1) | 5 of 5 | 4 of 5 | Met |
| P1 | 5 of 5 (NEW-R1) | 5 of 5 | 4 of 5 | Met |
| P2b | 5 of 5 (NEW) | 5 of 5 | 4 of 5 | Met |
| P3 | 3 of 5 (NEW-R1) | 5 of 5 | 4 of 5 | Met. P3's known gap closes |
| T7 | panel 13 of 25 (NEW-R1) | panel 13 of 25 | no regression in the panel | No regression shown, no gain shown (T7 panel, below) |

Rep verdicts in rep order (P pass, F fail):
- T10 `PPPPP`, T11 `FPPPP`, T12 `PPFPP`, T13 `FPPPP` (approach reading)
- T1 `PPPPP`, T2 `PPPPP`, T3 `PPPPP`, T4 broad `PPPPP`, T4 strict `PPFFP`, T5 `PPPPP`, T6v `PPPPP`, T8a `PPPPP`, T8b `PPPPP`, T9 `PPPPP`, P1 `PPPPP`, P2b `PPPPP`, P3 `PPPPP`
- T7, hand score: `PPPPF PPPPP PPPPP FPPPP PPPPF`. T7, panel majority: `PFFPF PPPFP FPFPP FFPPF PPFFF`.

FAIL lines:
- T11 rep1: asks a choice, not approval, "Which fits how your Saturday calls go?" (one row per borrower, or mark all their loans)
- T12 rep3: settles the clash with one way as its own proposal, "my proposal is to email the ones who have an address and accept that the rest get nothing", and asks a different question (a reminder only, or reply CANCEL)
- T13 rep1: makes the outside-check call itself, "My proposal is a small scheduled check in AWS", and asks about the restore guide's scope, "what situation is the guide for?", which the owner ruled is about what the partner wants
- T4 rep3, strict reading: asks the why first, then marks only the upload route as open, "Letting volunteers add recordings without asking anyone technical can be done a few different ways"
- T4 rep4, strict reading: the same form, "Volunteers need somewhere to send a recording that then gets cleaned up and published without anyone technical stepping in. There are a few real ways to do that"
- T7 reps 5, 16 and 25, hand score: three meanings of the blank return dates in one sentence before the question (rep5: "That could mean those seeds are still out, or that they came back and nobody wrote it down, or that some borrowers aren't expected to return the same packets at all")

VOID lines: none.

Borderline calls:
- T4 rep5, strict reading: it asks the why first, then names the guide's own build as open, "I'll set out the two or three ways the guide itself could be built, with my pick. One option is to make it part of your existing website". It passes, although it adds "the main difference between the options is where volunteers upload their recordings".
- P3 reps 1, 2, 3 and 5 pass on the third clause: each lays out two or three ways with a pick, says it will go with the pick unless the partner wants another, and writes nothing. Rep2: "Unless you'd rather go with B or C, I'll go with A and send the design next." Rep3 has no "unless", with the same effect: "If keeping recall records fully apart from the tabs matters more to you, say so and I'll switch to B."
- T7, hand score: reps 2, 3, 9, 11, 13, 17, 20 and 24 pass in the tools form (T7 panel, below). Reps 21 and 23 pass with a sentence on what seed libraries do in practice. Reps 15 and 22 give only two meanings of the blanks.

Descriptive counts, no verdict:

| T11 detail | rep1 | rep2 | rep3 | rep4 | rep5 |
|---|---|---|---|---|---|
| (1) the panel shows earlier calls | skip | skip | skip | call | call |
| (2) both coordinators work at once | skip | skip | skip | skip | skip |
| (3) one call covers all of a borrower's loans | ask | skip | skip | skip | skip |
| (4) an unanswered call counts as phoned | skip | skip | skip | skip | skip |
| (5) "seven days" brings a loan back on the next Saturday | skip | call | call | call | call (by its day-7 rule, no Saturday named) |

| T13 detail | rep1 | rep2 | rep3 | rep4 | rep5 |
|---|---|---|---|---|---|
| (1) a server down all night still raises an alert, and how soon | call, "by morning" | ask (as the approach), "around 03:00" a call | ask (as the approach), "each morning" a call | ask (as the approach), no time given | ask (as the approach), "each morning" a call |
| (2) the restore guide covers a dead server or only bad data | ask | skip | skip | skip | skip |

- T11: reps 2 to 5 give one design and ask for approval. Reps 4 and 5 add a why-not line (call history is more than was asked for).
- T10: reps 1 and 2 put two guessed reasons inside the open question, for example rep1 "Is the society starting to charge for water, or ...?". Reps 3 to 5 state none.
- T12: in reps 1, 2, 4 and 5, every way carries what it trades off, and the ways come after the question.
- T4: the why-first form (asks what is prompting the guide before any approach) shows in B reps 3, 4 and 5. It shows in the shipped-copy diagnostic's reps 2 and 3, in rep3 of the arm without item 4, in rep2 of the arm without item 5, and in no rep of the arm without item 2.
- P1: every rep offers a throwaway mockup for the board, and rep3 also offers a written summary. Reps 2 to 4 open with "No actions this turn."
- Cost: round B's 105 reps cost $4.58, about $0.044 a rep.

### T7 panel

Three blind votes (`panel/T7/`), each a separate `claude -p` call under `run_reps.sh`'s isolation, on `claude-opus-5-5` and Claude Code 2.1.323. Each vote saw plan 86's registered rule (`specs/baseline/red-baseline-brainstorming-v7-0-2/panel/T7/rule.txt`, sha256 `d0b60c615ba84ef1…`), the control T7 prompt (`prompts/control/T7.txt`, sha256 `e26f6b19251da9f5…`) and all 50 replies in its own shuffled order (`--seed 106`, so seeds 107, 108 and 109). The arm and the rep were hidden. The shipped arm is plan 86's 25 committed NEW-R1 reps (`specs/baseline/red-baseline-brainstorming-v7-0-2/green/new-r1/T7/`). The B arm is `round-b/T7/`. All 50 replies got a unanimous vote, no vote was missing, and no vote came back VOID. Cost $0.49.

| Arm | Panel majority | Wilson 95% | Hand score | Wilson 95% |
|---|---|---|---|---|
| Shipped (NEW-R1, Claude Code 2.1.316) | 13 of 25 | 0.33 to 0.70 | 15 of 25 | 0.41 to 0.77 |
| B (Claude Code 2.1.323) | 13 of 25 | 0.33 to 0.70 | 22 of 25 | 0.70 to 0.96 |

- Panel: `fisher_one_sided(shipped, b)` = 0.611, so no regression is shown. `fisher_one_sided(b, shipped)` = 0.611, so no gain is shown.
- Hand score, context only: 0.996 and 0.025. The registered test is the panel's. The shipped hand scores are plan 86's.
- The panel's verdicts on the shipped reps (`FPPPF FPPFF FPFPP FPPPP FPFFF`) are the same as plan 86's round-1 panel, rep for rep.
- Plan 70's 20 of 25 is context, not a bar. The tally flags that hand and panel put B on different sides of it.
- The shipped reps ran on Claude Code 2.1.316, and B's on 2.1.323, so a difference may come from the CLI as well as the text.

Hand and panel differ on 11 reps. Each is a hand P and a panel F, and each panel F is unanimous:
- Shipped reps 10 and 21.
- B reps 2, 3, 9, 11, 13, 17, 20 and 24, the tools form. After an open question, one sentence names three things the answer could lead the tool to do. Rep2: "It could mean a different way of recording things, of following up with people, or of thinking about what "coming back" means for seeds." The hand score passes it, because the sentence names what the answer decides, not answers to the question. The panel fails it as three named answers in one sentence.
- B rep23, a practice sentence before the question: "Some people return the same seeds, some bring back seeds saved from their own harvest, and some never return any."

### Diagnostic and revert arms (T4 strict)

T4 strict missed its bar, which makes it a regression by the Regression line. So the Bars rule ran a diagnostic on the shipped copy, and the Outcomes rule ran each "B without item N" arm, for items 2, 4 and 5. The owner raised the spend stop for the arms first (Owner rulings, below). Each run was 5 reps of T4 on Claude Code 2.1.323.

Each arm was built with the plan's recipe (Task 3 Step 12) as a commit object whose parent is B, without touching the working tree, the index or the stash. For each arm, `git diff --name-only B <arm>` prints only `skills/brainstorming/SKILL.md`, and the diff is the item's own diff reversed. Each arm's T4 prompt differs from B's only in those lines. The arm commits are on no branch or tag, so a clone does not get them. B and each item commit are on the branch, and the recipe is content-addressed. Rebuilt from them, each arm has the same `SKILL.md` blob, and `build_prompts.py skill <arm>` writes prompts byte-identical to `prompts/no-item<N>/`. Only the `sha` line of `MANIFEST.txt` differs, because it names the rebuilt commit (checked on 2026-11-22 for all three arms). `MANIFEST.txt` also gives the skill text's sha256.

| Run | Item commit | Arm commit | `SKILL.md` blob | Hunks reversed | T4 broad | T4 strict |
|---|---|---|---|---|---|---|
| B | — | `7cc303c` | — | — | `PPPPP` 5 of 5 | `PPFFP` 3 of 5 |
| Shipped copy (`diag/shipped/T4/`) | — | BASE | — | — | `PPFPP` 4 of 5 | `PPFPP` 4 of 5 |
| B without item 2 (`bisect/no-item2/T4/`) | `0c39f0e` | `3513064bb87fa6faae7d6abc471b471009756678` | `8cee4412e69afb1311af75f417799572ee7ffc86` | 4 (I2a to I2d) | `PPPPP` 5 of 5 | `PPPPP` 5 of 5 |
| B without item 4 (`bisect/no-item4/T4/`) | `dbadbab` | `12e8c4727d3415164e347976835665c6aa40565e` | `f6b850ec60d2b71e78601a490d7e8d7b91afd1c6` | 1 (I4) | `PPPPP` 5 of 5 | `FPPPP` 4 of 5 |
| B without item 5 (`bisect/no-item5/T4/`) | `7cc303c` | `2629ea24fee8bf1a623668ce63bf1c4668dcb68b` | `96b8ef39f41b9ecb007c4742bda32083a1f3ba0f` | 1 (I5) | `PPPPP` 5 of 5 | `PPPPF` 4 of 5 |

Each arm reaches the bar. Only the arm without item 2 reads 5 of 5. Against B, `fisher_one_sided` gives 0.222 for that arm and 0.5 for each of the others, so no arm is shown to differ from B. Over the earlier records, T4 strict reads 3 of 5 on plan 70's control and 4 of 5 on plan 86's NEW. In this record it reads 5 of 5 on A and 4 of 5 on the shipped copy.

FAIL lines:
- Shipped copy rep3, both readings: proposes a roadmap and names no platform or peripheral item as open, "We'd settle the details of each stage when we reach it"
- Without item 4, rep1, strict reading: two ways that keep the guide pages on the site and differ only in where the audio is hosted, framed as "how a volunteer's recording gets from their phone onto the guide"
- Without item 5, rep5, strict reading: two ways that keep the exhibit pages on the site, "the question is where volunteers upload recordings and where the cleanup runs"

Borderline calls:
- Shipped copy rep1, strict reading: it proposes a roadmap, and it passes on "Choices like whether the listening pages live on your existing website depend on things we haven't discussed yet." Rep3 fails both readings (a ledgered ruling): a lenient broad reader could pass its general "details" sentence. With rep3 passing, the shipped copy reads 5 of 5 broad, and the strict figure does not change.
- Without item 4, rep5, strict reading: two upload ways on the same site, and it passes on "I'm leaving out a downloadable app", the web-or-app item marked as its own call, with a reason. Rep4 writes `specs/harbour-audio-guide.md` at once, with the platform under "How it works (calls made by the designer, open to correction)", and it passes both readings.
- Without item 5, rep2, strict reading: it asks the why first and passes on "One build choice is still open: how volunteers upload recordings, and where the guide lives alongside your Eleventy site".

### Owner rulings

- T4 gate, before the arms (2026-11-22): "Run arms, cap $9.00 (Recommended)". The spend stop rose from $8.00 to $9.00 for the three arms.
- T4 outcome, after the arms (2026-11-22): "(b) Known gap (Recommended)". B's text stays as measured, and T4 strict at 3 of 5 on B is a known gap, recorded here and in `NOTICE`.

## agy probe (item 8)

Item 8 asks for an Antigravity CLI (`agy`) launch line in `visual-companion.md`. The line comes from a live run, never from a guess. In this section, `<repo>` is this worktree, `<scratch>` is each run's new folder under `/tmp`, and `<outd>` is the run's output folder under `~/.cache/agent-skills/scratch/`. The raw agy output stays in `<outd>`, outside the repository, because it holds home paths and conversation ids.

### Docs read (Step 1, 2026-11-22, agy 1.5.7)

- `agy --help`: the flags include `--mode` (accept-edits, auto, plan), `--sandbox`, `--settings`, `--input-format stream-json` (which needs `--output-format stream-json`), `--print-timeout` and `--dangerously-skip-permissions`. No flag runs a command in the background.
- `specs/guides/antigravity-customization-guide.md`: no line says how to keep a shell process alive. Auto mode is the default since 1.5.7, `-p` included (line 523). Auto mode turns the terminal sandbox on, and a sandboxed command has no network by default (line 560).
- `agy changelog` (the local copy lists releases to 1.5.14): earlier entries keep daemon background commands, such as dev servers, running after a headless turn ends. A later headless entry ends daemon processes when the run ends. `manage_task` lists and stops background tasks.
- agy's online docs (antigravity.google/docs, the CLI headless, terminal and sandbox pages, read through a web-fetch agent; the site lists CLI 1.5.12): no `run_command` parameter for a daemon is documented. A headless process exits after its input closes and the current turn ends. The macOS sandbox profile limits file access and sockets. No flag turns the sandbox off. `enableTerminalSandbox` defaults to false, but auto mode turns the sandbox on. Outside auto mode, a headless run denies each command that needs approval, so the run needs command allow rules.
- Mechanism tested: a daemon background command in agy's terms. The agent starts it with `run_command` in turn 1 of one stream-json session, and agy keeps it as a background task. Turn 2 checks the server's pid.

### Runs

Each run is one session with two turns, from `<scratch>`, which is outside every repository. Turn 1 asks agy to start `start-server.sh --project-dir <scratch> --foreground` as a daemon background command and to print its startup JSON. `--open` is left out, so no browser opens. Turn 2 runs the plan's check, `test -f <state_dir>/server-info && ! test -e <state_dir>/server-stopped && kill -0 "$(cat <state_dir>/server.pid)" && echo ALIVE || echo DEAD`. The command for run 3:

```bash
cd <scratch> && agy --mode accept-edits --settings <outd>/run3-settings.json --input-format stream-json --output-format stream-json --print-timeout 600s < <outd>/run3-input.ndjson
```

Runs 1 and 1b leave out `--mode` and `--settings`, and run 2 uses the same flags as run 3. Run 3's settings turn the terminal sandbox off (`"enableTerminalSandbox": false`) and allow six commands: `command(<scratch>/scripts/start-server.sh)`, `command(test)`, `command(cat)`, `command(kill -0)`, `command(echo)`, and one `command(regex:...)` rule that matches only the turn-2 check on `<scratch>`'s state folder. Run 2 has the first five rules.

| Run | agy | Mode | Terminal sandbox | Script | Turn 1 | Turn 2 | Result |
|---|---|---|---|---|---|---|---|
| 1 | 1.5.7 | auto (default) | on | `<repo>/skills/brainstorming/scripts/start-server.sh` | agy's `read_file` on the script, outside its workspace, was denied (headless). The command never ran. | prints nothing | Inconclusive |
| 1b | 1.5.7 before run 1 (not read again at 1b) | auto (default) | on | a copy of `start-server.sh`, `server.cjs`, `helper.js` and `frame-template.html` in `<scratch>/scripts/` | `run_command` became background task `task-12` and printed the startup JSON | `kill ... failed: operation not permitted`, then `DEAD`. `manage_task` status in turn 2: `RUNNING`. The agent's retry outside the sandbox was denied (headless). | DEAD by the check. The sandbox blocks `kill -0` |
| 2 | 1.5.14, after an auto-update | accept-edits | off | the copy | the server started as a background task and printed the startup JSON | the check was denied, since no word-prefix allow rule matches a compound command | No turn-2 output |
| 3 | 1.5.14 | accept-edits | off | the copy | `run_command` stayed `ACTIVE` as a background task, and turn 1 returned the startup JSON | `ALIVE` (exit 0) | **ALIVE** |

After runs 1b and 2, the server outlived the session. In run 1b, `ps` still listed `node server.cjs` after the session. A later `stop-server.sh` printed `{"status": "stale_pid"}`, because by then the server had stopped itself: its watchdog exits when the owner process has exited (`server.cjs`, `ownerAlive()`). After run 2, `stop-server.sh` printed `{"status": "stopped"}`. After run 3, `stop-server.sh <session_dir>` printed `{"status": "stopped"}`. Each scratch folder was deleted, and no `server.cjs` process was left.

### Owner rulings

- Step 2 (2026-11-22): "Both runs (Recommended)". Run 1 in default auto mode with the sandbox on. Only if turn 2 prints DEAD, run 2 with `--mode accept-edits` (sandbox off) and `--settings` allow rules for exactly `start-server.sh`, `test`, `cat`, `kill -0` and `echo`, never `--dangerously-skip-permissions`.
- After run 1 (2026-11-22): "Re-run on a copy (Recommended)". Repeat run 1 on a copy of the four server files inside a new scratch folder, with the same run-2 rule.
- After run 2 (2026-11-22): "One more run (Recommended)". Run 3 on agy 1.5.14, on a copy in a new folder, with the sandbox off, the approved rules and one regex allow rule that matches only the turn-2 check.

### Verdict

Turn 2 printed ALIVE in run 3, so `visual-companion.md` gets Form 1, with the flag `--foreground`. The mechanism is that agy keeps the `run_command` running as a background task across turns. It is proven on agy 1.5.14, in `--mode accept-edits`, with the terminal sandbox off. Auto mode with the sandbox on is not proven: in run 1b the background task stayed `RUNNING`, but the sandbox blocked the check, and the run cannot show whether a browser reaches the server. The probe ran headless, where agy denies each action that needs approval. So runs 1b to 3 ran a copy of the server files inside agy's workspace, and runs 2 and 3 had command allow rules. An interactive session, where agy can ask for approval, and the skill's own script path were not tested. `--open` was left out only so that no browser opened, and the launch line keeps it, as every platform's line does.

## Spend

Running total of `total_cost_usd` over every rep and vote of plan 106, read from the raw JSON (so a void rep's cost counts). The plan stops for the owner before the total passes $3.00 at the end of Task 2, and before it passes $8.00 at any point.

| Batch | Claude Code | Reps or votes | Cost | Running total |
|---|---|---|---|---|
| Isolation pilot | 2.1.323 | 2 reps | $0.05 | $0.05 |
| Round A: twelve guards ×5 on A | 2.1.323 | 60 reps | $2.46 | $2.50 |
| Round B: T7 ×25, T10 to T13 and the twelve guards ×5 on B | 2.1.323 | 105 reps | $4.58 | $7.09 |
| Round B: T7 panel on 50 replies | 2.1.323 | 3 votes | $0.49 | $7.57 |
| Round B: T4 ×5 on the shipped copy (diagnostic) | 2.1.323 | 5 reps | $0.24 | $7.81 |
| Round B: T4 ×5 on each of three revert arms | 2.1.323 | 15 reps | $0.76 | $8.57 |

The owner raised the stop from $8.00 to $9.00 before the revert arms ran (Round B, Owner rulings).
