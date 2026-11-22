# Brainstorming Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply items 1, 2, 4, 5, 6 and 8 of the brainstorming findings to `skills/brainstorming/`, measure the four that change tested wording in two isolated micro-test rounds, and record every change to upstream text in `NOTICE`.

**Architecture:** Task 1 builds a micro-test kit from plan 86's frozen kit with three next-kit fixes, registers the rules and runs the isolation pilot. Task 2 cuts the body (item 1) and runs round A on the twelve guards. Task 3 lands item 6, then items 2, 4 and 5, one commit each, and runs round B on plan 86's full case set, with a T7 panel that scores the shipped copy's committed reps beside the new ones. Task 4 fixes `visual-companion.md` (item 8) after an agy probe. Task 5 writes every `NOTICE` change.

**Tech Stack:** Markdown skill text; Python 3 stdlib and bash for the kit; the `claude` CLI (2.1.323 at planning); `agy` (1.5.7 at planning) for Task 4's probe; `build/run_commit_lints.sh`; pytest through `build/run_suites.py`.

**Spec:** `specs/findings/brainstorming-improvements.md`, read at `07ea574` (findings with owner rulings, approved for planning 2026-11-22, no spec in between). The plan also closes two backlog items in `specs/deferred_items.md`, named by their opening words:
- section `86-brainstorming-v7-0-2-retune`, "The scope of brainstorming's first-message design" (item 2, Task 3);
- section `70-brainstorming-proportional-rebuild`, "The Red Flags cell for the quick-task row does not point back to the size rules" (item 5, Task 3).

## Labels used in this plan

- **BASE**: the commit that `git rev-parse HEAD` prints at Task 1 Step 1. **A**: the commit of Task 2 Step 3. **B**: the commit of Task 3 Step 4, the last of four.
- **The shipped copy**: `skills/brainstorming/SKILL.md` at BASE. Its body (the text after the frontmatter) equals plan 86's NEW-R1 (`9761c88`) body: 19,524 characters, sha256 `f6067e3a10f9e2ec46a6ec11cb861abb9fcc1d6c60a97ca3995f311487542f7a`. Only the frontmatter's cc-guide stamp changed since.
- **`<rec>`**: `specs/baseline/red-baseline-brainstorming-improvements`. `<rec>.md` is the record, `<rec>/` its folder, `<rec>/kit/` the kit.
- **`<v702>`**: `specs/baseline/red-baseline-brainstorming-v7-0-2`, plan 86's record folder. It is frozen: read it, never write it.
- **The twelve guards**: T1, T2, T3, T4 (broad and strict readings), T5, T6v, T8a, T8b, T9, P1, P2b, P3 (`<v702>.md`, Bars on the new copy).
- **A body length**: `len(check_conformance.skill_body(text)[0])` from `build/check_conformance.py`, run with `uv run --with pyyaml`.

## Global Constraints

- **Execution start.** This is a domain execution. It starts only after plan 103 (`specs/plans/103-worktree-skills-cc-guide-fixes.md`, the machinery stream) has merged, and only when no other running execution edits `skills/brainstorming/`. Under default 8, another domain execution may also edit `NOTICE`, `build/suites.toml`, `specs/deferred_items.md` or `specs/history.md`. Execute from a worktree.
- **Anchors.** Line numbers in this plan were read at `07ea574` and are hints only. Each replacement's old text is its match key, and each must match exactly once (`git grep -c -F` prints `<path>:1`). A miss means the text moved: stop and report.
- **One owner per file.** `skills/brainstorming/SKILL.md` changes only in Tasks 2 and 3. `skills/brainstorming/visual-companion.md` changes only in Task 4. `NOTICE` changes only in Task 5. `build/suites.toml` changes only in Task 1. Task 1 creates `<rec>.md`, and Tasks 2 to 4 append their sections to it.
- **Compaction window.** The SKILL.md body stays at most 19,700 characters (the `compaction-window` check, `build/cc_guide/conformance.toml`: 5,000 tokens × 4 − 300). Expected body lengths: 19,524 at BASE, 19,054 after Task 2, 19,385 after Task 3. No Red Flags or HARD-GATE heading may start past the window. If an owner gate reverts a hunk or adds a wording round, the later expected lengths and hashes no longer hold: recompute them with the same function and record the new figures in `<rec>.md`.
- **Measured equals shipped.** The SKILL.md body at B is the body that round B measures. No SKILL.md edit lands after B unless the owner picks a wording round or a revert at a gate, and then its cases re-run.
- **Micro-tests.** Every rep runs `<rec>/kit/run_reps.sh` on `claude-opus-5-5`, with plan 86's flags: `env -i` (HOME, USER, LOGNAME, PATH, SHELL, TMPDIR, LANG, plus `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`), `--tools ""`, `--strict-mcp-config`, `--setting-sources ""`, `--no-session-persistence`, `--output-format json`, `--max-budget-usd 0.50`, each rep in its own new folder under `/tmp`, outside every repository. Panel votes use the same isolation, through `<rec>/kit/panel.py`. Nobody messages or subscribes to a running rep or vote.
- **Next-kit fixes.** Every rep JSON and every vote JSON passes through `postprocess` before it is written: it drops `origin` and `credential_expires_at`, applies the identity scrub to the text, and marks a rep whose JSON has `result_index` above 0 or a non-null `origin` (checked before the drop) as void. A void rep gets a replacement rep. This plan does not tick the backlog item "Void a no-tools rep that took a peer message" (plan 103 owns it).
- **Privacy.** Before each commit that holds rep-derived or vote-derived text, `uv run python <rec>/kit/privacy_sweep.py <the new folders>` exits 0. The user's name and e-mail address are written nowhere, in the repository or in a report.
- **Spend.** Keep a running total of `total_cost_usd` over every rep and vote in `<rec>.md`, Spend. Stop for the owner before the total passes $3.00 at the end of Task 2, and before it passes $8.00 at any point.
- **Commit gate.** Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Messages follow Conventional Commits in plain technical English and end with the attribution trailer the executing session is given. State test counts as deltas.
- **Upstream.** No step opens or drafts an upstream pull request. Whether item 2 goes upstream is the owner's separate question after this plan.
- **Shared files at merge.** Plan 105 (writing-skills, planned in parallel) and plan 103's Task 4 add bullets to `NOTICE`'s superpowers change list. Plan 103's Task 1 adds a suite to `build/suites.toml`. Before the merge, re-read both files on `origin/main`, keep every side, and run the merge-order check (chain the merges with `git merge-tree --write-tree`, then check that no conflict marker is left and no line of either side is lost).
- **Leave alone.** Findings items 3 (T7 wording) and 7 (builder check, in the backlog). The frozen `<v702>/` folder and `<v702>.md`. The findings' Scope line: derive-roadmap, writing-plans, `/deferred` and `install.py`. The Copilot CLI block of `visual-companion.md`. Step 1 of the ordered list in SKILL.md ("have your human partner pick one"): approving your one sensible way, or handing you the how, is their pick.

## Review Focus

1. **A secret or a peer's session data lands in a committed rep or vote file.** The person expects no `credential_expires_at`, no `origin` and no identity in any file under `<rec>/`. Task 1 pins it with `test_run_reps_drops_secrets_and_keeps_the_answer` and `test_vote_output_is_postprocessed`.
2. **A rep that answered a peer message gets scored.** The person expects that rep to read VOID and to be replaced. Task 1 pins it with `test_run_reps_voids_a_peer_turn`, `test_show_reps_prints_void` and `test_gather_skips_a_void_rep`.
3. **The T7 panel compares arms under different inputs.** The person expects the shipped and new arms to be scored in one panel, under plan 86's rule and control request, byte for byte. Task 3 Steps 6 and 9 check both sha256 values before the panel runs.
4. **A revert arm is built from the wrong text.** The person expects a "B without item N" arm to differ from B only in item N's lines. Task 3 Step 12 checks the arm's diff against B before any rep runs on it.
5. **The agy line ships a guessed recipe.** The person expects the recipe to be the one a live agy run proved, or the "not supported" text. Task 4 Step 4 fills the slot only from the live run's output.

## Decisions

- **D1** (owner, plan review, 2026-11-22): default 1, "Approve as written (Recommended)": two rounds, and round B runs plan 86's full set (105 reps plus the panel). Applied in: Tasks 2 and 3, `<rec>.md` Bars.
- **D2** (owner, plan review, 2026-11-22): default 2, "Approve as written (Recommended)": copy plan 103's merged `postprocess` after an interface check, and stop if it differs. Applied in: Task 1.
- **D3** (owner, plan review, 2026-11-22): default 3, "Approve as written (Recommended)": keep the Gemini CLI and Copilot CLI blocks, and add an agy line from the probe, never a guessed recipe. Applied in: Tasks 4 and 5.
- **D4** (owner, plan review, 2026-11-22): default 4, approved with D2's answer: a YES on isolation line 7 is recorded and does not stop the run. Applied in: Task 1, `<rec>.md` Rules.
- **D5** (owner, plan review, 2026-11-22): default 5, approved with D1's answer: P3 is held to 3 of 5 in round A and 4 of 5 in round B. Applied in: `<rec>.md` Bars.
- **D6** (owner, plan review, 2026-11-22): default 6, approved with D1's answer: about $6.30, with stops at $3.00 and $8.00. Applied in: Global Constraints.
- **D7** (owner, plan review, 2026-11-22): default 7, "Inline, executing-plans (Recommended)". Applied in: the execution handoff.
- **D8** (owner, plan review, 2026-11-22): default 8, "Yes, they may overlap (Recommended)": `NOTICE` merges as keep-both, so plan 105's execution and this one may overlap. Applied in: Global Constraints.
- **D9** (owner, plan review, 2026-11-22): "Approve the wording (Recommended)": the exact copy of edits I1a to I1c, I6, I2a to I2d and I4 (I5 is the owner's own wording, findings Owner decisions 3). Applied in: Tasks 2 and 3.
- **D10** (owner, plan review, 2026-11-22): "Approve the NOTICE text (Recommended)": the exact copy of Task 5 Steps 2 to 4. Applied in: Task 5.

## Defaults (approved at plan review, D1 to D8)

These were the planning session's defaults. The owner approved each at plan review (Decisions).

1. **Round shape.** Two rounds. Round A runs item 1 alone, on the twelve guards at 5 reps. Round B runs items 2, 4, 5 and 6 together on plan 86's full new-copy set: T7 at 25 reps plus a panel, T10 to T13 and the twelve guards at 5 reps. That set is wider than the union of the three items' case lists, because edit I2a changes the ordered list that every case reads and edit I2d changes what the written design records, which T4's strict reading scores. If a case regresses in round B, it re-runs on each "B without item N" arm for items 2, 4 and 5 (Task 3 Step 12).
2. **The kit.** A new record `<rec>.md` and kit `<rec>/kit/`. The cases come from `<v702>/kit/` unchanged. The kit adds (a) the peer-message void, (b) the `credential_expires_at` drop and (c) plan 104's 8-question isolation probe (`specs/baseline/red-baseline-mutant-screen-runs/kit/isolation_probe.txt`). No ref held plan 103's kit when this plan was written. Because this execution starts after plan 103 merges, Task 1 copies plan 103's merged `postprocess.py`, `test_postprocess.py`, `kit_identity.py` and `check_scrub.py`, and records the commit it copied them from. If plan 103's merged `postprocess` does not have the interface in Task 1's Interfaces block, stop for the owner.
3. **Item 8.** Keep the `**Gemini CLI:**` block unchanged and add an agy line beside it. The line comes from Task 4's probe: agy's docs, then one live run. It gives the recipe the live run proved, or says the visual companion is not supported on agy. It never gives a guessed recipe. The optional browser-pane line (findings, item 8) stays out. `NOTICE` gets no sentence for the kept Copilot block.
4. **Isolation line 7.** Plan 104's probe adds line 7 (the user's name or e-mail) and line 8 (other sessions). Plans 97 and 104 found line 7 reads YES on `claude-opus-5-5`, because the account identity is in every logged-in `claude -p` run's system context. Registered rule: a YES on line 7 is recorded and does not stop the run, because the identity scrub covers every rep and vote file and the privacy sweep runs before each commit. A YES on any other line stops the run for the owner.
5. **P3's round-A bar.** The shipped copy scores P3 at 3 of 5, a known gap. Round A holds P3 to at least 3 of 5. Round B holds it to 4 of 5, because item 4 targets it.
6. **Spend.** About $2.10 for the pilot and round A, and about $4.20 for round B with its panel, so about $6.30 before any diagnostic. Stop points at $3.00 (end of Task 2) and $8.00 (any time).
7. **Execution mode.** Inline (executing-plans), as plan 86 ran. The hand scoring and the owner gates after each round tie the tasks to one controller context.
8. **Overlap with plan 105.** The owner's rule lets domain executions run at once only when their files do not overlap. Plan 105 (writing-skills) also edits `NOTICE`'s superpowers change list, in other bullets. Default: `NOTICE`, like `specs/deferred_items.md` and `specs/history.md`, counts as a file that merges as keep-both. So the two executions may overlap, and Task 5 runs last, re-reads `NOTICE` and keeps both sides. If wrong: this execution waits until plan 105's execution has merged.

## Files

| Path | Task | Change |
|---|---|---|
| `<rec>/kit/` | 1 | Create (the files Task 1 Step 2 names) |
| `<rec>.md` | 1, 2, 3, 4 | Create (Task 1), then append |
| `<rec>/isolation-pilot/`, `prompts/`, `round-a/`, `round-b/`, `diag/`, `bisect/`, `panel/T7/` | 1–3 | Create (rep and vote output) |
| `build/suites.toml` | 1 | Register suite `brainstorming-improvements-kit` |
| `skills/brainstorming/SKILL.md` | 2, 3 | Edits I1a–I1c (Task 2); I6, I2a–I2d, I4, I5 (Task 3) |
| `skills/brainstorming/visual-companion.md` | 4 | The agy line and the stop-server sentence |
| `NOTICE` | 5 | Plan 70's and plan 86's brainstorming entries, and one new bullet |

---

### Task 1: Kit, registered rules and isolation pilot

**Files:**
- Create: `<rec>/kit/` with `cases.py`, `build_prompts.py`, `show_reps.py`, `panel.py`, `run_reps.sh` (from `<v702>/kit/`), `postprocess.py`, `test_postprocess.py`, `kit_identity.py`, `check_scrub.py` (from plan 103's merged kit), `privacy_sweep.py` (from `specs/baseline/red-baseline-change-reverted-mutant/review-kit/`), `isolation_probe.txt` (from `specs/baseline/red-baseline-mutant-screen-runs/kit/`), and a new `test_kit.py`
- Create: `<rec>.md`, `<rec>/isolation-pilot/`
- Modify: `build/suites.toml`

**Interfaces:**
- Consumes: plan 103's `postprocess(raw: dict) -> dict` in `postprocess.py`. It returns `{'void': True, 'reason': 'result_index' | 'origin'}` for a void rep, else the rep with `'void': False`, without `origin` and `credential_expires_at`, and with `kit_identity`'s scrub applied to its text.
- Produces: `run_reps.sh <prompt-file> <out-dir> <first-rep> <last-rep> <model>`, as `<v702>/kit/run_reps.sh`, with each `rep<N>.json` written through `postprocess`.
- Produces: `panel.py run|tally|selftest`, as `<v702>/kit/panel.py`, with `gather` skipping a void rep and `call_voter` returning `postprocess` of the voter's JSON.
- Produces: `build_prompts.py <arm> <sha> <out-dir>` and `show_reps.py <dir> ...`, as in `<v702>/kit/`. `show_reps.py` prints `VOID (<reason>)` for a void rep file.
- Produces: the record's sections Method, Rules, Bars, Isolation pilot and Spend.

- [ ] **Step 1: Fix BASE and check for drift.** Record `git rev-parse HEAD` as BASE and `claude --version` in `<rec>.md`. Then check:
  - the SKILL.md body at BASE is 19,524 characters with sha256 `f6067e3a10f9e2ec46a6ec11cb861abb9fcc1d6c60a97ca3995f311487542f7a`;
  - each old text of edits I1a to I1c, I6, I2a to I2d, I4 and I5 (Tasks 2 and 3) matches once in `skills/brainstorming/SKILL.md`;
  - plan 103's kit is on `origin/main`: `git log -1 --format=%H origin/main -- specs/baseline/red-baseline-worktree-skills-fix/kit/postprocess.py` prints a sha. Record it as the source commit.
  - plan 103's `postprocess` has the interface in Interfaces: `git grep -n "def postprocess(raw" -- specs/baseline/red-baseline-worktree-skills-fix/kit/postprocess.py` prints one line, the file names both reasons `'result_index'` and `'origin'`, and `uv run python build/run_suites.py worktree-skills-fix-kit` passes.
  A failed check stops the task for the owner.

- [ ] **Step 2: Copy the kit.** Copy the files that Files names, unchanged except for these edits:
  - In `cases.py`, `build_prompts.py`, `show_reps.py`, `panel.py` and `run_reps.sh`, change "plan 86" to "plan 106" in docstrings and comments, and the temp prefixes `plan86-rep-` and `plan86-panel-` to `plan106-rep-` and `plan106-panel-`.
  - `panel.py` keeps `MODEL = 'claude-opus-5-5'`, and its `HEADER_SOURCE` still resolves (the kit sits at the same depth as `<v702>/kit/`).
  Then run `uv run python <rec>/kit/panel.py selftest`. Expected: `selftest ok`.

- [ ] **Step 3: Write the failing tests and register the suite.** Add to `build/suites.toml`, after the suite named `brainstorming`:

```toml
[[suite]]
name = 'brainstorming-improvements-kit'
dir = 'specs/baseline/red-baseline-brainstorming-improvements/kit'
with = ['pytest']
notes = ['Plan 106 micro-test kit: postprocess, runner, reader and panel tests with a stub claude and no model.']
```

  `test_kit.py` builds a stub `claude` (a script first on `PATH`) that prints one JSON object, and runs the kit's real files on it. No model runs.
  - `test_run_reps_drops_secrets_and_keeps_the_answer`: the stub prints `result` `'ok'`, `result_index` 0, `origin` null, and `credential_expires_at` at the top level and inside `usage`. After `run_reps.sh` reps 1 to 1: `rep1.json` parses, `void` is False, `result` is `'ok'`, and the text holds neither `credential_expires_at` nor `origin`.
  - `test_run_reps_voids_a_peer_turn`: the stub prints `result_index` 1 and `origin` `{'kind': 'peer', 'title': 'peer-title-x'}`. `rep1.json` equals `{'void': True, 'reason': 'result_index'}`, and its text holds no `peer-title-x`.
  - `test_show_reps_prints_void`: over that folder, `show_reps.py` prints `VOID (result_index)` for rep1.
  - `test_gather_skips_a_void_rep`: a folder with `rep1.json` (`result` `'a'`, `void` False) and a void `rep2.json`. `panel.gather([('x', folder)])` returns `{'x-rep1': 'a'}`.
  - `test_vote_output_is_postprocessed`: with `subprocess.run` patched to return the peer stub's stdout, `panel.call_voter('text')` returns a void dict. With the clean stub's stdout, the dict holds no `credential_expires_at` and no `origin`.

  Run: `uv run python build/run_suites.py brainstorming-improvements-kit`. Expected: plan 103's three `test_postprocess.py` tests pass, and the five new tests fail.

- [ ] **Step 4: Wire `postprocess` in.** In `run_reps.sh`, after each rep ends, pass `rep<N>.json` through `postprocess` the way plan 103's `run_reps.sh` does. In `panel.py`, `call_voter` returns `postprocess` of the parsed JSON, `gather` skips a rep whose JSON has `void` True, and `run` stops with a message naming the vote when a vote comes back void (re-run the panel into a new folder). In `show_reps.py`, a rep JSON with `void` True prints `rep<N> VOID (<reason>)` and nothing else.

- [ ] **Step 5: Run the kit checks.** Run `uv run python build/run_suites.py brainstorming-improvements-kit`, `uv run python <rec>/kit/check_scrub.py` and `uv run python <rec>/kit/panel.py selftest`. Expected: the suite passes (+8 tests), `PASS`, and `selftest ok`.

- [ ] **Step 6: Write the record and commit it before any rep.** `<rec>.md` opens with a quarantine note like `<v702>.md`'s: quarantine this file, its folder and this plan during any later micro-test of brainstorming whose reps have tools. Then: **Method** (BASE, the Claude Code version, the kit and its source commits, the command, the model, the arms: the shipped copy at BASE, A and B, each read with `git show`), **Rules** and **Bars** (exact copy below), and **Spend** (a running-total table). Commit with `test(specs): register plan 106 micro-test kit and rules`, after the commit gate.

````text
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
````

- [ ] **Step 7: Isolation pilot.** Run 2 reps of `<rec>/kit/isolation_probe.txt` into `<rec>/isolation-pilot/`. Expected: lines 1 to 6 and 8 read NO in both, under the line-7 rule, and `show_reps.py` shows `turns=1 extra-iters=- models=1` and no VOID. Write the result to `<rec>.md`, Isolation pilot, and add the cost to Spend.

- [ ] **Step 8: Commit the pilot.** Run `privacy_sweep.py <rec>/isolation-pilot`, then the commit gate. Commit with `test(specs): run plan 106 isolation pilot`.

### Task 2: Item 1, free body room, and round A

**Files:**
- Modify: `skills/brainstorming/SKILL.md` (Visual Companion section, the paragraph after the ordered list, Size the Work's several-projects sentence)
- Modify: `<rec>.md` (append Round A)
- Create: `<rec>/prompts/shipped/`, `<rec>/prompts/a/`, `<rec>/round-a/<case>/`, `<rec>/diag/shipped/<case>/` (only for a missed guard)

**Interfaces:**
- Consumes: Task 1's kit.
- Produces: commit A, with a SKILL.md body of 19,054 characters, sha256 `143b293e4595d1621bdff4068c14d3b238ca6a87ea2639957311b0ca7f598e94`.

- [ ] **Step 1: Apply I1a.** Delete this paragraph and the blank line after it (Visual Companion, about line 392):

```text
**Per question, ask: would they understand this better by seeing it?**
Mockups, layouts, diagrams, and side-by-side designs go in the browser.
Requirements, scope, tradeoffs, and conceptual choices stay in text. A
question about a UI topic isn't automatically a visual question.

```

- [ ] **Step 2: Apply I1b and I1c.** I1b, after the ordered list (about line 54). Replace:

```text
One kind of work takes a different path. A new project of several stages,
with nothing built yet, goes to derive-roadmap's New-Project Entry once its
outcomes are clear, in place of steps 1 to 4 (see Size the Work).
```

with:

```text
A new project of several stages takes another path (see Size the Work).
```

  I1c, Size the Work (about line 272). Replace:

```text
stages with nothing built goes to the New-Project Entry whole, and it
splits unrelated outcomes into tracks.
```

with:

```text
stages with nothing built goes to the New-Project Entry whole.
```

- [ ] **Step 3: Check and commit A.** Expected: body 19,054 characters, sha256 `143b293e…598e94` as above, and the commit gate passes. Commit with `refactor(brainstorming): drop the per-question paragraph and shorten the roadmap pointers`. Record its sha as A.

- [ ] **Step 4: Build the prompts.** Run `build_prompts.py skill BASE <rec>/prompts/shipped` and `build_prompts.py skill A <rec>/prompts/a`. Check that each case's prompt in `a/` differs from the same case in `shipped/` only inside the `<skill name="brainstorming">` block, and that each `shipped/` prompt equals the same case in `<v702>/prompts/new-r1/` where that folder has it.

- [ ] **Step 5: Run round A.** The twelve guards, reps 1 to 5 each, from `<rec>/prompts/a/` into `<rec>/round-a/<case>/`. Update Spend after each batch. Stop for the owner before the total passes $3.00.

- [ ] **Step 6: Score and apply the bars.** Hand-score every rep under the Rules. For a guard below its bar, run the diagnostic: 5 reps from `<rec>/prompts/shipped/` into `<rec>/diag/shipped/<case>/`. A missed bar is an owner gate (Bars, Outcomes). Under (c), revert the one hunk the miss points to, then repeat Steps 3 to 6 for that case.

- [ ] **Step 7: Write the results and commit.** Append `## Round A` to `<rec>.md`: a table of the twelve guards (shipped figure from `<v702>.md`, round A tally, verdict), the rep verdicts in rep order, one line per FAIL and VOID (`<case> rep<N>: <why>, "<short verbatim quote>"`), the diagnostics, and the owner's ruling quoted when there was a gate. Run the privacy sweep on the new folders and the commit gate. Commit with `test(specs): record plan 106 round A`.

### Task 3: Items 6, 2, 4 and 5, and round B

**Files:**
- Modify: `skills/brainstorming/SKILL.md` (Look Before You Ask; the paragraph after the ordered list; Your First Message; Lay out the approaches; Size the Work; Red Flags)
- Modify: `<rec>.md` (append Round B)
- Create: `<rec>/prompts/b/`, `<rec>/prompts/control/`, `<rec>/round-b/<case>/`, `<rec>/panel/T7/`, and only when needed `<rec>/diag/shipped/<case>/`, `<rec>/bisect/<arm>/<case>/`

**Interfaces:**
- Consumes: commit A; Task 1's kit.
- Produces: commit B, with a SKILL.md body of 19,385 characters, sha256 `2bccdaeda4c8c6ba64470f4dd9c9ad061daea57ca994445571fa3a8d45353ba9`.

- [ ] **Step 1: Apply I6 and commit (item 6).** Look Before You Ask (about line 65). Replace:

```text
a `specs/deferred_items.md`, check it for deferred work the idea touches.
```

with:

```text
a `specs/deferred_items.md`, search it for the idea's terms to find
deferred work the idea touches.
```

  Expected: body 19,080. After the commit gate, commit with `fix(brainstorming): search the backlog for the idea's terms`.

- [ ] **Step 2: Apply I2a to I2d and commit (item 2).** I2a, the paragraph after the ordered list (about line 46). Replace:

```text
If nothing is open when you write your first message and there's one
sensible way, steps 1 to 3 happen in that message for a small change,
and step 1 does for a project (see Your First Message).
```

with:

```text
If nothing is open when you write your first message, step 1 happens
in that message, and for a small change with one sensible way, steps 2
and 3 do too (see Your First Message).
```

  I2b, Your First Message (about line 89). Replace:

```text
  and which you'd pick. If nothing like that is open, there's one
  sensible way. For a small change, end with the short design itself
```

with:

```text
  and which you'd pick. If nothing like that is open and several ways
  fit, end by laying them out (see Lay out the approaches). If one
  does, there's one sensible way. For a small change, end with the
  short design itself
```

  I2c, Size the Work (about line 236). Replace:

```text
Once you understand what they want and they've picked an approach, say
```

with:

```text
Once you understand what they want and an approach is picked, say
```

  I2d, Size the Work (about line 246). Replace:

```text
three ways you considered building it, what each trades off, which one
they picked, and why. They pick in the conversation, before you write
the design.
```

with:

```text
three ways you considered building it, what each trades off, which one
was picked, by whom, and why. The pick comes in the conversation,
before you write the design; only a small change with one sensible way
may carry both in one message.
```

  Expected: body 19,236. After the commit gate, commit with `fix(brainstorming): make Size the Work agree with the first-message design`.

- [ ] **Step 3: Apply I4 and commit (item 4).** Lay out the approaches (about line 186). Replace:

```text
say you'll go with your pick instead, and write the design in the next
message. When there's genuinely one sensible way, say so in that message
```

with:

```text
say you'll go with your pick instead, and write the design in the next
message. A push to hurry doesn't hand you the how: the approaches still
go first, in a message of their own. When there's genuinely one
sensible way, say so in that message
```

  Expected: body 19,336. After the commit gate, commit with `fix(brainstorming): a push to hurry does not hand over the how`.

- [ ] **Step 4: Apply I5 and commit (item 5, the owner's wording).** Red Flags, last row (about line 376). Replace:

```text
once you've looked, do it, and say what you did and what else it touches. |
```

with:

```text
once you've looked, do it, and say what you did and what else it touches. If the look shows a wider reach, step up a size. |
```

  After the commit gate, commit with `fix(brainstorming): point the quick-task Red Flags cell back to the size rules`.

- [ ] **Step 5: Check B.** Record the Step 4 commit's sha as B, and the shas of the Step 1 to 4 commits as I6, I2, I4 and I5. Expected: body 19,385 characters, sha256 `2bccdaed…353ba9` as above, at most 19,700, and the commit gate passes.

- [ ] **Step 6: Build the prompts.** Run `build_prompts.py skill B <rec>/prompts/b` and `build_prompts.py control - <rec>/prompts/control`. Check that each case's prompt in `b/` differs from the same case in `<rec>/prompts/shipped/` only inside the skill block, and that `<rec>/prompts/control/T7.txt` has sha256 `e26f6b19251da9f5c4ae096fc4fa394e347368b1c228ccc035e9b34cc54c670c` (plan 86's control T7 prompt). No rep runs on the control prompts.

- [ ] **Step 7: Run round B.** From `<rec>/prompts/b/`: T7 reps 1 to 25 into `<rec>/round-b/T7/`, and T10, T11, T12, T13 and the twelve guards, reps 1 to 5 each, into `<rec>/round-b/<case>/`. Update Spend after each batch. Stop for the owner before the total passes $8.00.

- [ ] **Step 8: Hand-score every rep.** Score under the Rules. Write T7's hand scores to `<rec>/round-b/T7/hand-scores.json` (`{"b-rep<N>": "P" | "F"}`) before the panel. Then write `<rec>/panel/T7/hand-scores.json` with B's scores and the shipped scores from `<v702>/green/new-r1/T7/hand-scores.json`, each key `newr1-rep<N>` renamed `shipped-rep<N>`. If a T7 rep is VOID, copy B's 25 scored rep files into `<rec>/round-b/T7-scored/` and give the panel that folder.

- [ ] **Step 9: Run the T7 panel.** Check that `<v702>/panel/T7/rule.txt` has sha256 `d0b60c615ba84ef14f4eea79e718108b8c96b5059c0ff5b763eb4d6826889af8`. Then run:

```bash
uv run python specs/baseline/red-baseline-brainstorming-improvements/kit/panel.py run \
  --rule specs/baseline/red-baseline-brainstorming-v7-0-2/panel/T7/rule.txt \
  --request specs/baseline/red-baseline-brainstorming-improvements/prompts/control/T7.txt \
  --out specs/baseline/red-baseline-brainstorming-improvements/panel/T7 --votes 3 --seed 106 \
  shipped=specs/baseline/red-baseline-brainstorming-v7-0-2/green/new-r1/T7 \
  b=specs/baseline/red-baseline-brainstorming-improvements/round-b/T7
uv run python specs/baseline/red-baseline-brainstorming-improvements/kit/panel.py tally \
  specs/baseline/red-baseline-brainstorming-improvements/panel/T7/panel-verdicts.json \
  --hand specs/baseline/red-baseline-brainstorming-improvements/panel/T7/hand-scores.json \
  --compare shipped b
```

  Expected: 50 replies, 3 votes, 0 missing votes, and both one-sided Fisher p values printed. Add the cost to Spend.

- [ ] **Step 10: Apply the bars.** Score each case against Round B's bars. For a guard below its bar, run the diagnostic on `<rec>/prompts/shipped/` into `<rec>/diag/shipped/<case>/`.

- [ ] **Step 11: Stop on a T7 regression.** A T7 regression goes to the owner before Step 12. Present the panel figures and the fail forms.

- [ ] **Step 12: Re-run a regressing case on the revert arms.** For each item N in 2, 4 and 5, build the arm as a commit object, without touching the working tree, the index or the stash (`<N>` is item N's commit from Step 5):

```bash
T=$(mktemp)
GIT_INDEX_FILE=$T git read-tree B
git diff <N>^ <N> -- skills/brainstorming/SKILL.md | GIT_INDEX_FILE=$T git apply --cached -R
ARM=$(git commit-tree "$(GIT_INDEX_FILE=$T git write-tree)" -p B -m "plan 106 arm: B without item N")
rm -f "$T"
git diff --name-only B "$ARM"
```

  The last command must print only `skills/brainstorming/SKILL.md`, and `git diff B "$ARM"` must show only item N's hunks reversed. Record `$ARM` and its SKILL.md blob sha in `<rec>.md`. The planning session tested this recipe on a scratch clone with a tracked edit in the working tree: the arm reversed only the item, and the edit and the stash list stayed as they were. Build `build_prompts.py skill "$ARM" <rec>/prompts/no-item<N>`, and run the regressing case at 5 reps into `<rec>/bisect/no-item<N>/<case>/`. Report which arm restores the bar. Then the owner gate applies (Bars, Outcomes).

- [ ] **Step 13: Write the results and commit.** Append `## Round B` to `<rec>.md`: a table of T10 to T13 and the twelve guards (shipped figure, round B tally, verdict); the rep verdicts; one line per FAIL and VOID; the descriptive counts that plan 86's Rules keep, the T11 and T13 call/ask/skip tables among them; the T7 panel table (panel majority and hand score with Wilson intervals for each arm, both Fisher p values, where hand and panel differ, and the fail forms); the diagnostics and the revert-arm results; and the owner's rulings, quoted. Run the privacy sweep on the new folders and the commit gate. Commit with `test(specs): record plan 106 round B`.

### Task 4: Item 8, `visual-companion.md`

**Files:**
- Modify: `skills/brainstorming/visual-companion.md` (Launching the server by platform; Cleaning Up)
- Modify: `<rec>.md` (append `## agy probe (item 8)`)

**Interfaces:**
- Produces: the agy outcome, recipe or not supported, which Task 5's `NOTICE` sentence names.

- [ ] **Step 1: Read agy's docs.** Read `agy --help`, `agy changelog`, `specs/guides/antigravity-customization-guide.md` and agy's online docs (https://antigravity.google/docs, its CLI headless, terminal and sandbox pages) for a way to keep a shell process alive across turns, like Gemini CLI's `is_background: true` or Codex's foreground mode. Note each page or command read and what it says, with `agy --version`.

- [ ] **Step 2: Ask the owner before the live run.** The run spends agy plan quota and approves shell calls inside one new scratch folder under `/tmp`, outside every repository. It may need a second run with the terminal sandbox off (Step 3), and the owner approves that run in the same answer. Name the mechanism from Step 1, or say none was found and the run tests `start-server.sh`'s default mode and `--foreground`.

- [ ] **Step 3: The live run.** In the scratch folder, run one `agy -p` session with `--input-format stream-json --output-format stream-json`, two turns. Turn 1: start `<repo>/skills/brainstorming/scripts/start-server.sh --project-dir <scratch>` (with `--foreground` and the Step 1 mechanism when there is one) and print the JSON it returns. Leave out `--open`, so no browser opens. Turn 2: run `test -f <state_dir>/server-info && ! test -e <state_dir>/server-stopped && kill -0 "$(cat <state_dir>/server.pid)" && echo ALIVE || echo DEAD`. The server is kept when turn 2 prints ALIVE. Then stop the server with `stop-server.sh <session_dir>` and delete the scratch folder. Append `## agy probe (item 8)` to `<rec>.md`: the docs read, the agy version, the execution mode and the terminal sandbox setting the run used (agy's auto mode turns the sandbox on), the commands, turn 2's output and the verdict. If turn 2 prints DEAD with the sandbox on, run once more with it off before the verdict, since a sandbox can block a localhost server. Form 1 then names the mode and the sandbox setting that the recipe needs.

- [ ] **Step 4: Add the agy block.** Put it after the `**Gemini CLI:**` block and before `**Copilot CLI:**`, with a blank line on each side. Use the first form only when Step 3 printed ALIVE, with the mechanism and flags exactly as the live run used them. Otherwise use the second form.

  Form 1, a proven recipe:

````text
**Antigravity CLI (`agy`):**
```bash
# <one line: the mechanism the live run used, in agy's own terms>
<this-skill-dir>/scripts/start-server.sh --project-dir /path/to/project --open<flags the live run used>
```
````

  Form 2, not supported:

```text
**Antigravity CLI (`agy`):** Not supported yet. No way to keep the server running across turns was found on agy <version> (<YYYY-MM-DD>). Tell your human partner the visual companion can't run here, and stay in text.
```

- [ ] **Step 5: Say where `$SESSION_DIR` comes from.** In Cleaning Up, after the code block that runs `stop-server.sh $SESSION_DIR`, add this paragraph, with a blank line on each side:

```text
`$SESSION_DIR` is the session directory: the parent of `screen_dir` and `state_dir` from the startup JSON (for example `/path/to/project/.brainstorm/12345-1706000000`).
```

- [ ] **Step 6: Check and commit.** Run `uv run python build/check_snippets.py skills/brainstorming/`, `uv run python build/check_links.py` and the commit gate. Expected: each exits 0, and `git diff --stat` shows only `visual-companion.md` and `<rec>.md`. Commit with `docs(brainstorming): add the agy launch line and say where SESSION_DIR comes from`.

### Task 5: `NOTICE`

**Files:**
- Modify: `NOTICE` (plan 70's brainstorming entry, about line 742; plan 86's entry, about line 955; one new bullet at the end of the superpowers change list)

**Interfaces:**
- Consumes: round B's P3 tally (Task 3), the agy outcome (Task 4).

- [ ] **Step 1: Re-read `NOTICE`.** Fetch, and compare `NOTICE` on `origin/main` with BASE. Plan 105 (writing-skills) and plan 103's Task 4 may have added bullets to the superpowers change list. Keep every line they added. Wrap each edited paragraph at about 72 columns with the list's indentation (two spaces, a dash, four spaces on continuation lines).

- [ ] **Step 2: Update plan 70's entry (item 6).** In the bullet that starts `brainstorming was rebased on upstream v7.0.1`, replace the sentence `Look Before You Ask also checks specs/deferred_items.md.` with `Look Before You Ask also searches specs/deferred_items.md for the idea's terms.`

- [ ] **Step 3: Extend plan 86's entry (items 1, 2 and 4).** In the bullet that starts `Plan 86 (2026-11-10) took upstream v7.0.2's brainstorming retune`, append after its last sentence, whose last two lines read `    round, as it does on the copy before the port, and is recorded as a` and `    known gap.`, with `<date>` and the P3 sentence filled from round B:

```text
Plan 106 (<date>) changed four parts of that text. The Visual
Companion section no longer carries the paragraph that asks, per
question, whether seeing would help more than reading, since
visual-companion.md gives the same test. Size the Work's Approaches
part records who made the pick, and only a small change with one
sensible way puts the pick and the short design in one message.
Upstream's Size the Work says that the partner picks before the
design. When nothing is open but several ways fit, the first message
lays them out, a path that upstream lacks, and the note under the
ordered list on what the first message carries now covers it. And a
push to hurry does not hand over the how: the approaches still come
first, in a message of their own. These changes are local, and no
upstream text was taken. <P3 sentence>
```

  The P3 sentence, by round B's P3 tally: at 4 or 5 of 5, `The P3 case then met its bar (<n> of 5), so its known gap is closed.`; at 3 of 5 or fewer, `The P3 case scored <n> of 5 and stays a known gap.` (with the owner's ruling quoted when the gate ran).

- [ ] **Step 4: Add the visual-companion bullet (item 8).** Add as the last bullet of the superpowers change list, after any bullet that plans 103 and 105 added, exact copy with the slots filled:

```text
  - Plan 106 (<date>) changed brainstorming/visual-companion.md.
    Cleaning Up says that $SESSION_DIR is the session directory, the
    parent of screen_dir and state_dir, which upstream does not say.
    Beside the Gemini CLI block, an Antigravity CLI (agy) line <agy
    clause>. This repository's gemini runtime targets agy. These
    changes are local, and no upstream text was taken.
```

  The agy clause, by Task 4's outcome: `gives the launch recipe that a live run on agy <version> proved` or `says the visual companion is not supported on agy <version>, since no way to keep the server running across turns was found`.

- [ ] **Step 5: Check and commit.** Run `uv run python build/check_provenance.py` and the commit gate. Expected: both pass, and `git diff BASE -- NOTICE` shows only this task's three changes beside lines other plans added. Commit with `docs(notice): record plan 106's brainstorming changes`.
