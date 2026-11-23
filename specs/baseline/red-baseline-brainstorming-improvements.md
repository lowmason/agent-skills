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

## Spend

Running total of `total_cost_usd` over every rep and vote of plan 106, read from the raw JSON (so a void rep's cost counts). The plan stops for the owner before the total passes $3.00 at the end of Task 2, and before it passes $8.00 at any point.

| Batch | Claude Code | Reps or votes | Cost | Running total |
|---|---|---|---|---|
