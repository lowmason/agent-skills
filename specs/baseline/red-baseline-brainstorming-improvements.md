# RED baseline — brainstorming improvements (plan 106)

**Date:** 2026-11-22 · **Status:** Registered. No case rep has run yet.
**Governs:** plan 106 (`specs/plans/106-brainstorming-improvements.md`), items 1, 2, 4, 5, 6 and 8 of the brainstorming findings (`specs/findings/brainstorming-improvements.md`).

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

## Spend

Running total of `total_cost_usd` over every rep and vote of plan 106, read from the raw JSON (so a void rep's cost counts). The plan stops for the owner before the total passes $3.00 at the end of Task 2, and before it passes $8.00 at any point.

| Batch | Claude Code | Reps or votes | Cost | Running total |
|---|---|---|---|---|
| Isolation pilot | 2.1.323 | 2 reps | $0.05 | $0.05 |
| Round A: twelve guards ×5 on A | 2.1.323 | 60 reps | $2.46 | $2.50 |
