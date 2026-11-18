# cc-guide Verifier Recall and Covered Files Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** An audit packet lists the changelog bullets that name its group's terms and the verifier must answer each one. A files packet for a skill copies the Markdown files its citation covers. The files rule compares a statement with the component it describes. A micro-test gates the audit change and the files change separately.

**Architecture:** Parts A to C change `build/cc_guide/` (`docs.py`, `packets.py`, `state.py`, `settle.py`, `report_grammar.py`), the verifier contract `.claude/agents/cc-guide-verifier.md` and the `/cc-guide` skill's text. The commits group into three revert units: Part A, Part B's code, and the files-contract text (B3 and C1). Part D is a new committed kit under `specs/baseline/red-baseline-cc-guide-verifier-recall/kit/`. It runs paid `claude -p` reps one at a time, each in its own folder under `/private/tmp/vr102/`. The kit keeps raw output in `~/.cache/agent-skills/scratch/vr102/` and grades the reps blind against plan 45's pre-registration, as this plan amends it. Each contract section then lands or reverts on its own gate.

**Tech Stack:** Python 3.13 through `uv run` (stdlib only, plus pytest for tests), git, `claude -p` (a held copy of the newest installed Claude Code; 2.1.323 at planning).

**Spec:** `specs/cc-guide-verifier-recall-and-covered-files.md`, as of `924f8ee`, its first commit. `af37043` (PR #228) later corrected two of its Motivation facts.

## Global Constraints

From the spec's Constraints, verbatim:
- "The repo is public. Packets, reports and docs text stay in the cache. The spec, plan and record carry counts, labels and pointers only."
- "`.claude/agents/cc-guide-verifier.md` and `.claude/skills/cc-guide/` are project-local, so `runtimes/` needs no regeneration. Their `# cc-guide:` citations follow the usual lint, and `check_conformance.py` must pass."
- "`build/cc_guide/conformance.toml` and `build/cc_guide/baseline.json` are hot spots that other lanes also edit. This work should not need either, except a `baseline cite` that an edit to a citing file calls for." No edit here calls for one: the lint's STALE rule reads cited sections, not the citing file's body. So no `baseline cite` runs, and `cli.py lint` prints the same lines before Task 1 and after Task 5.
- "This is a domain lane. It edits no execution machinery. `skills/writing-skills/` and `skills/executing-plans/` are read only, as fixtures."

From the spec's Anti-goals:
- The contract names no fixture fact. Each contract commit passes the term gate in Task 2 Step 6.
- Settle never applies a B row or a listed-item answer as an edit.
- Each contract section lands or reverts on its own gate (Revert units, below).

Execution:
- **Branch.** This plan reaches `main` first, in its own PR, opened only after the owner approves the plan. Execution starts in a fresh session, on a new branch cut from that `main`, in its own worktree. Do not push during execution. finishing-a-development-branch decides how the branch is integrated.
- **Concurrency** (owner rule, 2026-11-17). This is a domain stream. Before execution starts, `list_sessions` must show at most two other plan executions running in agent-skills, and none of them a machinery stream. `build/suites.toml` is shared with plans 100 and 101: add one table and touch nothing else in it.
- **Before Task 1.** Create the execution worktree, and keep SDD scratch in its gitignored `.sdd/102-cc-guide-verifier-recall-and-covered-files/`. Record in the ledger:
  - `START`, the output of `git rev-parse HEAD`, before any commit;
  - the output of `git diff dc8e020 START -- .claude/agents/cc-guide-verifier.md`. It must be empty (PC1). Any output stops the run until the owner rules;
  - the pass count of `uv run python build/run_suites.py cc_guide`, and both streams of `uv run python build/cc_guide/cli.py lint`.
- **Revert units.** Commits keep these units apart, so a failed gate reverts one unit with `git revert`:
  - **Part A:** Task 1 and Task 2 (code and audit-contract text together, spec E1).
  - **Part B code:** Task 3 and Task 4 (stays even if gate F fails, spec E2).
  - **Files-contract text:** Task 5's two commits, B3 with B5, then C1 with C2. Never put A3 text in a commit with B3 or C1 text.

  Each unit's edits keep at least one unchanged line away from another unit's, so each revert applies cleanly. Every step that places text says where it goes, and Task 5 Step 8 proves it with a dry run.
- **Pinned contract text.** The eight strings of `report_grammar.FORMATS` (seven today, plus Task 2's) stay byte-identical in the verifier and in `formats.md`. The verifier has exactly one line holding `TODO(owner)` and exactly one holding `none line is exactly` (`test_skill_files.py`). The frontmatter does not change. New prose in the agent file never holds the bare word `cc-guide` (`check_conformance.py`'s dmi-handoff check).
- **Paid runs.** No `claude -p` run before the owner approves the ceiling at Task 8 (brief D2).
- **Never commit docs text.** Packets, reports, sheets, transcripts and the precision key stay in `~/.cache/agent-skills/scratch/vr102/` (`$K`). Kit tests are hand-written. The record scores by label and points by file and line.
- **Leave alone:**
  - the masters `~/.cache/agent-skills/cc-guide/packets/20261013T113847-audit/`, `~/.cache/agent-skills/cc-guide/packets/20261013T121854-files/` and `~/.cache/agent-skills/cc-guide/2.1.296/docs/`. They are the last copies. The kit reads them and writes only copies;
  - plan 100's kit, `specs/baseline/red-baseline-handoff-rerun/`: copy from it, never edit it;
  - `~/.cache/agent-skills/scratch/deferred-triage-2026-11-17.md`: copy nothing from it;
  - the spec's status line and the guide.
- **Tests.** Each task writes its tests first and runs them. Each RED failure must match the step's stated reason; a test that passes at RED is a plan defect unless the step marks it a guard. Test counts are stated as `+N`.
- **Commits.** Every commit runs `build/run_commit_lints.sh` through the hook. Never pass `--no-verify`. Each message ends with the executing session's own `Co-Authored-By` trailer.
- **Style.** Python: single quotes, `'''` docstrings, 4-space indent, Python 3.13. The record, the kit README and commit messages follow the plain-English rule.
- **Anchor on text.** Line numbers are as of `072d708`. Guide lines in plan 45's key are the audit packet's own numbering.

## Review Focus

1. **A packet built before this plan settles as it did.** The control arm's audit copy, and every audit or files packet already in the cache, lack `listed` or `covered`. Settle must print nothing new for them and hold nothing new. Pinned in Task 2 (`test_an_audit_packet_without_listed_settles_as_before`) and Task 4 (`test_a_files_packet_without_covered_settles_as_before`), both guards.
2. **Today's changelog format gets the right item numbers and lines.** The fixture changelog uses `<Update>` blocks, but today's changelog uses bold `**X**` labels. Pinned in Task 1 (`test_release_lines_give_each_bullets_line_in_both_formats`).
3. **A covered file that moves after the packet was built holds the skill.** Changed, added or removed: settle prints no `baseline cite` for text no verifier read. Pinned in Task 4 (`test_a_covered_file_that_moved_holds_the_citing_file`).
4. **Only a skill's own `SKILL.md` covers files.** `runtimes/gemini/skills/<x>/SKILL.md` and other paths cover nothing. A `README.md` at any depth and anything under `scripts/` at any depth stay out. Pinned in Task 3 (`test_covered_files_are_a_skills_on_demand_markdown`).
5. **A mistyped item ID in a none line holds the whole audit,** as spec A4 keeps it ("as today"). Settle must list the line as unparseable, so the owner sees why. Pinned in Task 2 (`test_a_none_line_for_an_unlisted_item_holds_every_section`).

## Decisions

- **D1** (owner, brief, 2026-11-17): plan 100 closes the three next-kit items. This kit still carries the three fixes, each with its test (spec Part D, D2), and this plan writes no note on those items. It reuses plan 100's kit code if that code is on `main` at execution, and builds its own otherwise. Spec Part D, D2's option "or the owner records that the gap stays" moves to plan 100. Applied in: Task 6, Planner's call PC2, Completion.
- **D2** (owner, brief, 2026-11-17): one cost ceiling, approved before the pilot. After the pilot the plan estimates again, and it stops for the owner only when the new estimate exceeds the approved ceiling. Applied in: Task 8.

---

## Planning record

### Checks run while planning (2026-11-18)

- `entry_check.py`: `highest: 101`, `next free: 102`, `collisions: none`. Overlap: `build/suites.toml` with plans 100 and 101.
- `git log dc8e020..origin/main -- .claude/agents/cc-guide-verifier.md` printed nothing. The file last changed in `0fad401`.
- Today's `state.parse_manifest` reads `5bd78a7`'s `build/cc_guide/manifest.toml`. Group `models` has 4 sections and 47 terms there.
- On the audit master, the A1 rule lists 206 bullets, among them the bullets at `changelog.md:1288` (P11) and `:1702` (P8).
- Plan 100's kit is not on `origin/main` (`92f6a37`).
- `~/.claude/settings.json` sets `model: opus`, `advisorModel: opus` and `permissions.defaultMode: auto`, and no `effortLevel`.

### Planner's calls (the owner reviews each at plan review)

- **PC1. Control arm** (the brief's default). The control arm is `.claude/agents/cc-guide-verifier.md` at the execution branch's base, `START`. Before Task 1, execution records `START` and checks that `git diff dc8e020 START -- .claude/agents/cc-guide-verifier.md` is empty (Global Constraints). If it is not, the run stops for the owner before any rep. If wrong: another lane's edit makes the arms differ by more than Parts A to C, and gates A and F compare the wrong things.
- **PC2. Isolation: the real `HOME`, no Bash anywhere, and a read fence.** This departs from the brief's reading of D1, which named plan 100's per-rep `HOME` (its C1) and guard (C5). A per-rep `HOME` drops `~/.claude/settings.json`, and with it the advisor, auto mode and the default model and effort that spec Part D, D1's fidelity aim keeps. So each rep runs with the owner's user settings, as plan 45's did, plus:
  - `--settings` with `permissions.deny: ["Bash", "Read(~/**)"]` and `permissions.blockReadsOutsideWorkingDirectories: true`. No session in a rep has a usable Bash tool: the verifier's tools are Read, Grep and Glob, and the main session needs only Agent. This closes the third next-kit item's gap for this kit, and the probe (Task 8) shows it.
  - Each rep's folder holds copies of its packet and the docs snapshot, so no rep needs a read under the home folder (spec D1).
  - Reps run one at a time, and the runner moves each rep's folder and session files into `$K` when the rep ends (plan 100's C6).
  - The runner strips `credential_expires_at` (plan 100's C7), with plan 100's `postprocess.py` when it is on `main`.

  If wrong: the owner wants plan 100's C1. Then the kit passes the advisor, auto mode and model through `--settings`, adds the keychain link and plan 100's guard, and the pilot checks that nothing else from user settings changes the verifier's context.
- **PC3. Precision fixture: `skills/writing-skills/SKILL.md`.** It cites 8 sections, none of them `hooks.*` or `permissions.*`. It covers 7 Markdown files, and `references/claude-code.md` states Claude Code facts throughout. `skills/executing-plans/SKILL.md` cites one section and covers one file, so both arms may write almost no rows on it, and the precision count would measure little. The key costs more to build (Task 7). If wrong: switch to `executing-plans` before the freeze.
- **PC4. A C row still counts toward P11.** Spec D5 says "a correction that names `deniedModels`", and replaces DF10 only to add the B row. DF10 counted a SUPPORTED C row, so this plan does too. If wrong: drop the C-row clause from the P11 rule before the freeze.
- **PC5. An unanswered listed item makes settle unclean** (exit 1), as a left-out section does.
- **PC6. `lacks`** compares against the code spans of every guide line, fenced lines included ("anywhere in the guide", spec A1).
- **PC7. Covered files are tracked files** (`git ls-files` or `git ls-tree`), as the citation scan reads tracked files. An untracked new file in a skill is neither copied nor detected.
- **PC8. The pilot is one changed-arm audit rep.** It is the longest and costliest rep, and the D2 estimate turns on its cost. Its sheet is read for validity, duration, cost and the listed-item counts only. P11 and P8 are not scored on it.
- **PC9. Reps.** Valid reps per arm: audit 5, readme 3, precision 3. At most 2 spares per packet and arm. Per-rep caps (`--max-budget-usd`): audit $10, files $4, probe $1. Timeouts: audit 60 minutes, files 20, probe 10. `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` is 4,200,000 (70 minutes), above the audit timeout (spec D2).
- **PC10. Main session model: the owner's default** (no `--model`, so user settings give `opus`). This departs from plan 45's DF13 (Sonnet), because a subagent may inherit its parent's effort, and V7 compares the verifier's effort with production's.
- **PC11. Launch.** The controller launches `run.py` from its own session, in the background (audit reps take up to an hour), not the owner from a terminal (plan 45's DF5). The runner builds each rep's environment from scratch (`env -i`, plan 100's C13), so nothing from the controller's session, `CLAUDECODE` included, reaches a rep. The owner's user hooks still run in each rep (PC2): they call `/usr/bin/env python3` scripts and tools by absolute path, which the rep's `PATH` covers.
- **PC12. Early stop in gate A.** Gate A's first wave stops when the control meets P11 in 2 reps (spec D5, UNSETTLED). It also stops when the changed arm misses P11, or P8, in 2 valid reps, since 4 of 5 is then out of reach (FAIL). Plan 45 needed an owner ruling for that case.
- **PC13. The record** goes to `specs/baseline/red-baseline-cc-guide-verifier-recall.md`, with the kit beside it (`CLAUDE.md` Conventions), not to plan 45's DF11 path.
- **PC14. Contract wording.** Tasks 2 and 5 give the exact A3, B3 and C1 text. The arm is that text.

**Owner question (does not block the plan).** A changed arm that writes a B row for every listed item meets P11 and P8 by volume. Spec D5 reports B rows per rep and does not gate them. Should gate A add a B-row ceiling, for example changed-arm B rows at most twice the control's median? The default keeps the spec: reported, not gated.

### Cost (the owner approves a ceiling at Task 8)

Plan 45's measured costs per rep: control audit $2.95–3.36, changed audit $3.09–3.51, readme files $0.53–1.20, all with the advisor. The listed items add about 20,000 input tokens and about 200 short answers to a changed audit rep. The main session now runs the owner's default model (PC10).

| Run | Reps | Per rep | Subtotal |
|---|---|---|---|
| probe | 1 | $0.10–0.50 | ≤ $0.50 |
| pilot (audit, changed) | 1 | $4–8 | ≤ $8 |
| gate F: readme | 6 | $0.50–1.40 | $3–8.40 |
| gate F: precision | 6 | $1–3 | $6–18 |
| gate A: audit | 10 | $3.20–7 | $32–70 |
| spares, if needed | ≤ 2 per packet and arm | as above | ≤ $28 audit, ≤ $18 files |

Expected: about $45–105 before spares, most likely near $70. **Proposed ceiling: $130.** The run starts a rep only when its full cap still fits under the ceiling, counting each earlier rep at its cost, or at its cap when it left no result. A rep held that way is the owner's call.

---

## Pre-registration (fixed at the freeze, Task 8 Step 3)

This plan adopts plan 45's Pre-registration (`specs/plans/completed/45-claude-code-drift-automation.md:254-327`) and its settled defaults DF2 to DF21 (`:159-187`), with the changes below. A rule not changed here stands as written there. After the freeze, any change is logged in `$K/changes.log` with the freeze hash before and after, and never follows a result it would affect.

**Arms.**
- **control:** the agent file at `START` (PC1), copied to `$K/arms/control.md`.
- **changed:** the agent file at Task 5's second commit, `ARM_COMMIT`, copied to `$K/arms/changed.md`. The bodies differ only in Task 2's and Task 5's added text.

**Packets.**

| Packet | Master | Mode | Valid reps per arm |
|---|---|---|---|
| audit | `20261013T113847-audit` | audit | 5 |
| readme | `20261013T121854-files/hooks__README.md` | files | 3 |
| precision | built at Task 7 from `skills/writing-skills/SKILL.md` | files | 3 |

- The changed arm's audit copy holds `listed.md` and `index.json` `listed`, computed by `packets.listed_bullets` from that packet's own `changelog.md` and `guide.md` and group `models`'s terms under `5bd78a7`'s manifest. The control arm's copy holds neither (spec D4).
- Both arms' readme copies gain `"covered": {}` in `index.json`, as a files packet built today would hold.
- In each audit copy, `index.json` `docs` and `quotes.docs` name the rep's own docs copy, in both arms alike. This is the one change to the control's copy: spec D4 reads it unchanged, but spec D1 puts the docs inside the rep.

**Rep layout.** Rep `<rid>` runs in `/private/tmp/vr102/<rid>/work/`, which holds `.claude/agents/cc-guide-verifier.md` (the arm's file), `packet/` (the copy, without `report.md` or `settled.json`) and, for audit reps, `docs/` (a copy of the 2.1.296 snapshot). `/private/tmp/vr102/<rid>/tmp/` is its `TMPDIR`. Each rep is one `claude -p` session, with the prompt `common.MAIN` on stdin. That prompt asks the main session to make SKILL.md step 1's dispatch (subagent type `cc-guide-verifier`, `model: sonnet`, the exact prompt) and to reply with the verifier's report.

**VOID rules** (plan 45's V1 to V8, amended):
- **V1:** as plan 45's, but the Agent call may also pass `model`, whose value must be `sonnet`.
- **V2:** a verifier Read, Grep or Glob that named a path outside the rep's `work/` folder and returned, or a Grep or Glob result that listed such a path. Paths resolve as plan 45's V2 says, and `/tmp/…` and `/System/Volumes/Data/private/tmp/…` both map to `/private/tmp/…`. The docs snapshot is now inside `work/`, so plan 45's exemption for it goes.
- **V3:** as plan 45's, with `common.MARKERS = ('deniedModels', 'availableModels', 'effortLevel', 'README.md:89')`.
- **V4, V5:** as plan 45's.
- **V6:** as plan 45's, plus a rep whose results still hold `credential_expires_at` after the strip.
- **V7:** the verifier is not `claude-sonnet-5-5`, or its effort or version differs from the pilot's. The pilot records both, after checking them against the production comparison (Task 8 Step 6).
- **V8:** the verifier's advisor attachment differs from the production comparison's: present, available and on `claude-opus-5-5` when production's verifier had one, absent when it had none.

**Rulings.** The pilot may fix the three values V1 and V7 leave open, logged in `$K/changes.log`: an Agent parameter that changes nothing the verifier sees (such as background dispatch), the verifier's effort, and its version. No post-hoc rulings.

**Scoring.** Ratings are plan 45's (SUPPORTED or UNSUPPORTED, `:289-293`), read by hand from each sheet into `$K/RESULTS.md` before `grade.py unblind`. A files row is SUPPORTED when the cited section's passage gives the case the row states, and the statement, read as about the component it describes, fails in that case.
- **Gate A (audit), per valid rep:**
  - P11 is met by a B row that settle lists with `changelog.md:1288`, or by a kept STALE, WRONG or PARTIAL row on guide lines 415–442, or a C row (PC4), that names `deniedModels` as blocking a model the allow list would permit and is SUPPORTED (DF10's scope rule holds).
  - P8 is met by a B row that settle lists with `changelog.md:1702`.
  - DF7 (precision) and DF8 (retention) as written, over every valid gate rep.
  - Reported, not gated: B rows per rep; listed items answered by a B row, answered none and unanswered per rep; DF21's volume; P7, P10 and P12.
- **Gate F (files), per valid rep:**
  - Readme: each kept `contradicts` row whose line or range covers `hooks/README.md:89`, and the count of UNSUPPORTED `contradicts` rows.
  - Precision: the count of UNSUPPORTED `contradicts` rows, rated against the precision key (Task 7). A kept `contradicts` row on a key statement is SUPPORTED. Any other is rated by hand, and a SUPPORTED one the key missed is reported as a key miss.
  - Reach: whether a kept row names a covered file.

**Decision rules.**
- **Order:** probe, pilot, gate F, then gate A.
- **Pilot check.** Stop for the owner before any counted rep when the pilot leaves more than 10% of the listed items unanswered, or writes 5 or more B rows that settle lists as unparseable. A wording revision is then a new changed arm, logged in `$K/changes.log` with a new freeze hash. It is piloted again before any counted rep.
- **Gate F PASS** when, over the valid reps: no changed readme rep keeps a `contradicts` row on `hooks/README.md:89`; no changed readme rep and no changed precision rep has more than 2 UNSUPPORTED `contradicts` rows; and a covered file is named in at least 2 of the 3 changed precision reps. The precision counts are reported for both arms either way (I5). **FAIL** otherwise: the owner rules whether to revert C1 alone and rerun gate F as a new round, or to revert B3 and C1 (spec D6).
- **Gate A, first wave** (2 control and 2 changed reps): stop as UNSETTLED when the control meets P11 in 2 reps (spec D5). Stop as FAIL when the changed arm misses P11, or P8, in 2 reps (PC12). Otherwise run the second wave to 5 valid reps per arm.
- **Gate A PASS** when, over the valid reps: the changed arm meets P11 in at least 4 of 5 and P8 in at least 4 of 5; the control meets P11 in at most 1; DF7 and DF8 hold. **FAIL** otherwise. No rerun without the owner's word.
- **Replacement:** plan 45's (`:286`). With too few valid reps after 2 spares, the packet's result is UNSETTLED, for the owner.
- **Blind reading:** plan 45's DF15. Both arms' audit reps settle against one layout, gate A's first-wave stop is read by `grade.py stop`, which names no arm, and each gate is unblinded only once all its sheets have their verdicts.

---

### Task 1: Listed bullets in an audit packet (A1, A2, A8)

**Files:**
- Modify: `build/cc_guide/docs.py` (`parse_changelog`, new `release_lines`)
- Modify: `build/cc_guide/packets.py` (new `LISTED`, `listed_bullets`, `listed_lines`; `audit()`)
- Test: `build/cc_guide/test_docs.py`, `build/cc_guide/test_packets.py`

**Interfaces:**
- Produces: `docs.release_lines(text: str) -> dict[str, list[int]]`: for each release label, the 1-based changelog line of each of its bullets, in `parse_changelog`'s bullet order. Both functions come from one scan of the text, so item numbers match triage's. Raises `ValueError` as `parse_changelog` does. `Release` keeps its two fields, since `test_docs.py:32` and `:107` compare whole tuples.
- Produces: `packets.LISTED = 'listed.md'`.
- Produces: `packets.listed_bullets(changelog: str, terms: dict[str, set[str]], guide: str) -> list[dict]`. `terms` is `state.group_terms(manifest, guide)[group]`, section to terms (brief trap 1). A bullet is listed when one of its code spans (`guide.code_spans`) equals a term of any section. Each entry is `{'item': '<release>#<n>', 'line': int, 'sections': [...], 'lacks': [...], 'text': str}`:
  - `sections`: the sections whose terms it names, in `terms`' order;
  - `lacks`: its spans of `TERM_MIN` to `TERM_MAX` characters, not in `STOP_TERMS`, that are not a code span of any line of `guide` (PC6), in the bullet's order, without repeats.

  Releases go newest first, as `parse_changelog` orders them, and bullets in changelog order.
- Produces: `packets.listed_lines(entries: list[dict]) -> list[str]`: `# Listed changelog bullets`, a blank line, then one line per item: `- <item> · changelog.md:<line> · <sections, joined by ', '> · names the guide lacks: <lacks, joined by ', '> · <text>`, without the lacks part when `lacks` is empty. With no entries, `None.` follows the heading.
- Produces: `audit()` writes `listed.md` and adds `'listed': <entries>` to `index.json`, from `world.docs.changelog`, `world.terms[group]` and `world.guide`. `releases.md` does not change (A7).
- Placement: `LISTED` goes on the line after `RELEASES`, and the two functions go after `release_items`. Task 3's `COVERED` goes after `SECTIONS`, so one unchanged line separates them.

- [ ] **Step 1: Write the failing tests.**

In `test_docs.py`:

```python
def test_release_lines_give_each_bullets_line_in_both_formats():
    text = '\n'.join(['# Changelog', '', '<Update label="2.1.10" description="x">', '  * one `A_B`', '  - two',
                      '</Update>', '', '**2.1.9**', '', '* three', '* four'])
    assert docs.release_lines(text) == {'2.1.10': [4, 5], '2.1.9': [10, 11]}
    assert [len(r.bullets) for r in docs.parse_changelog(text)] == [2, 2]
```

In `test_packets.py`, after `test_an_audit_packet_holds_every_section_its_untriaged_releases_and_its_blocks`:

```python
def test_listed_bullets_name_each_bullet_holding_a_group_term():
    changelog = '\n'.join(['<Update label="2.1.902" description="d">',
                           '  * Changed `BETA_ENV` beside `NEW_FLAG` and `true`', '  * Fixed `BETA_ENV_X`',
                           '</Update>', '<Update label="2.1.901" description="d">', '  * Added `ALPHA_ENV`',
                           '</Update>'])
    terms = {'beta.overview': {'BETA_ENV'}, 'beta.reference': {'BetaEvent'}}
    assert packets.listed_bullets(changelog, terms, guide_text()) == [
        {'item': '2.1.902#1', 'line': 2, 'sections': ['beta.overview'], 'lacks': ['NEW_FLAG'],
         'text': 'Changed `BETA_ENV` beside `NEW_FLAG` and `true`'}]


def test_an_audit_packet_lists_the_bullets_that_name_its_groups_terms(world, tmp_path):
    out = packets.audit(load(world), tmp_path / 'a', 'alpha')
    assert index(out)['listed'] == [{'item': '2.1.901#1', 'line': 14, 'sections': ['alpha.reference'],
                                     'lacks': [], 'text': 'Added `ALPHA_ENV` to the alpha tools'}]
    assert (out / 'listed.md').read_text().split('\n')[:3] == [
        '# Listed changelog bullets', '',
        '- 2.1.901#1 · changelog.md:14 · alpha.reference · Added `ALPHA_ENV` to the alpha tools']
    assert 'Added `ALPHA_ENV`' in (out / 'changelog.md').read_text().split('\n')[13]
```

In `test_an_audit_packet_holds_every_section_its_untriaged_releases_and_its_blocks`, add `'listed.md'` to the expected file list.

- [ ] **Step 2: Run them and confirm RED.**

Run: `uv run python build/run_suites.py cc_guide -- -k "release_lines or listed_bullets or audit_packet"`
Expected: 4 FAIL: `AttributeError` on `release_lines` and on `listed_bullets`, `KeyError: 'listed'`, and the file-list mismatch.

- [ ] **Step 3: Implement `release_lines`, `listed_bullets`, `listed_lines` and the `audit()` change** to the Interfaces block. Refactor `parse_changelog`'s loop into one private scan that both public functions read.

- [ ] **Step 4: Run the suite and confirm GREEN.**

Run: `uv run python build/run_suites.py cc_guide`
Expected: all pass, `+3` against the count recorded before Task 1.

- [ ] **Step 5: Commit.**

```bash
git add build/cc_guide/docs.py build/cc_guide/packets.py build/cc_guide/test_docs.py build/cc_guide/test_packets.py
git commit -m "feat(cc-guide): list the changelog bullets that name an audit group's terms (plan 102)"
```

### Task 2: Settle answers every listed item; the audit contract (A3–A6)

**Files:**
- Modify: `build/cc_guide/report_grammar.py` (new `LISTED_NONE_ROW`, added to `FORMATS`)
- Modify: `build/cc_guide/settle.py` (`settle_review`, audit mode)
- Modify: `.claude/agents/cc-guide-verifier.md` (`### verify and audit`)
- Modify: `.claude/skills/cc-guide/SKILL.md` (`## audit [<group>]`), `.claude/skills/cc-guide/references/formats.md` (audit row, report formats, settle rules)
- Test: `build/cc_guide/test_settle.py`, `build/cc_guide/test_skill_files.py`

**Interfaces:**
- Consumes: `index['listed']` (Task 1).
- Produces: `report_grammar.LISTED_NONE_ROW = 'item | none'`, appended to `FORMATS`. The existing format test then requires it in both the agent and `formats.md`.
- Produces, in `settle_review`, for an audit packet with `listed = index.get('listed', [])`:
  - a B row that parses, whose `changelog.md:<n>` is a listed item's `line`, answers that item;
  - a line whose first field is a listed item's ID answers it when `none_line` holds. Otherwise it is listed `unparseable: <line>` and answers nothing;
  - each unanswered item holds those of its `sections` that are in the packet's scope;
  - when `listed` is not empty, settle prints `listed items: <b> answered by a B row, <n> answered none, <u> unanswered` after the B items. When `u > 0` it also prints `unanswered listed items, so their sections are held: <IDs, space-separated>`;
  - `Settled.clean` is False while an item is unanswered (PC5);
  - a none line for an ID that is not listed stays as today: unparseable, and it holds every section in the packet;
  - verify packets carry no `listed`, so nothing changes there.

- [ ] **Step 1: Write the failing tests** in `test_settle.py`, after `test_an_audit_ends_with_audited_unless_a_section_is_held`. Each builds the alpha audit packet as that test does, with `REVIEWED = ('L14 | Alpha uses ALPHA_TOOL | CONFIRMED | tools.md:5 | "runs alpha batches" | -', 'alpha.reference | none')`.

```python
def test_an_audit_answers_each_listed_item_by_a_b_row_on_its_line_or_its_none_line(world, tmp_path):
    out = audit_packet(world, tmp_path)
    by_b = settled(out, *REVIEWED, 'B | 2.1.901 | adds ALPHA_ENV | changelog.md:14')
    assert 'listed items: 1 answered by a B row, 0 answered none, 0 unanswered' in by_b.lines
    assert f'  {CLI} baseline audited alpha --to 2.1.902' in by_b.lines and by_b.clean
    by_none = settled(out, *REVIEWED, '2.1.901#1 | none')
    assert 'listed items: 0 answered by a B row, 1 answered none, 0 unanswered' in by_none.lines and by_none.clean


def test_an_unanswered_listed_item_holds_its_sections(world, tmp_path):
    out = audit_packet(world, tmp_path)
    # The last case pins A5: the B row's form does not change, so an item ID in its version field does not parse.
    for extra in ((), ('B | 2.1.902 | other | changelog.md:9',), ('2.1.901#1 | not relevant',),
                  ('B | 2.1.901#1 | adds ALPHA_ENV | changelog.md:14',)):
        result = settled(out, *REVIEWED, *extra)
        assert 'listed items: 0 answered by a B row, 0 answered none, 1 unanswered' in result.lines
        assert 'unanswered listed items, so their sections are held: 2.1.901#1' in result.lines
        assert 'held, neither advanced nor audited: alpha.reference' in result.lines
        assert not any('audited' in line for line in result.lines if line.startswith('  ')) and not result.clean


def test_a_none_line_for_an_unlisted_item_holds_every_section(world, tmp_path):
    out = audit_packet(world, tmp_path)
    result = settled(out, *REVIEWED, 'B | 2.1.901 | adds ALPHA_ENV | changelog.md:14', '2.1.999#4 | none')
    assert 'listed items: 1 answered by a B row, 0 answered none, 0 unanswered' in result.lines
    assert '  unparseable: 2.1.999#4 | none' in result.lines
    assert 'held, neither advanced nor audited: alpha.overview alpha.reference' in result.lines


def test_an_audit_packet_without_listed_settles_as_before(world, tmp_path):
    '''Guard: passes at RED, and must still pass at GREEN.'''
    out = audit_packet(world, tmp_path)
    i = json.loads((out / packets.INDEX).read_text())
    del i['listed']
    (out / packets.INDEX).write_text(json.dumps(i))
    result = settled(out, *REVIEWED)
    assert not any(line.startswith('listed items') for line in result.lines)
    assert f'  {CLI} baseline audited alpha --to 2.1.902' in result.lines and result.clean
```

`audit_packet(world, tmp_path)` is a new helper holding that test's two setup lines.

In `test_skill_files.py`, after `test_the_verifier_writes_a_none_line_exactly_and_no_other_line_with_a_pipe` (above the format test, so Task 5's tests at the file's end stay apart):

```python
def test_the_verifier_answers_every_listed_item_in_an_audit():
    lines = (REPO / AGENT).read_text(encoding='utf-8').split('\n')
    (rule,) = [line for line in lines if 'Answer every listed item' in line]
    assert '`<item> | none`' in rule and 'holds its sections' in rule
    assert 'with its release as the version' in rule
```

- [ ] **Step 2: Run them and confirm RED.**

Run: `uv run python build/run_suites.py cc_guide -- -k "listed or unlisted or skill_files"`
Expected: FAIL for the three settle tests (no `listed items` line), for the new skill-file test (`ValueError` from the empty unpack), and for the new `'item | none'` case of `test_the_skill_and_the_verifier_state_the_report_formats_settle_parses` (the agent lacks it). The guard passes.

- [ ] **Step 3: Add `LISTED_NONE_ROW` and the settle rule** to the Interfaces block.

- [ ] **Step 4: Edit the verifier contract.** In `### verify and audit`, add `    item | none` as the last line of the format block. After the bullet `- B, one row per changelog item that changes a claim in scope.` add this bullet, exactly:

```markdown
- In an audit, `listed.md` lists each changelog bullet that names one of the group's terms, as `<release>#<n>` with its `changelog.md` line, the sections whose terms it names, and any names it holds that the guide lacks. Answer every listed item: give it a B row, with its release as the version and its `changelog.md` line, when the bullet changes a claim in a section of this packet, and otherwise the line `<item> | none`. A listed item with neither holds its sections, as if unreviewed.
```

- [ ] **Step 5: Edit the skill text** (A6).
  - `formats.md`, Packets: leave the table alone, since Task 3 edits the files row beside the audit row. After the paragraph that begins "`packets --verify <ids> --from <triage>`", add a paragraph: "An audit packet also holds `listed.md`: each changelog bullet that names one of the group's terms, numbered `<release>#<n>` as triage numbers it, with its `changelog.md` line, the sections it names, the names it holds that the guide lacks, and its text. `index.json` names the same items as `listed`."
  - `formats.md`, Reports: add `    item | none` to the verify-and-audit format block. Change its lead sentence to end "…and a none line for each section with no checkable claim; in an audit, a B row on its line or `<item> | none` for each item in `listed.md`:".
  - `formats.md`, `## What settle does with a report`: add a last bullet, after Bookkeeping (Task 4 edits the Holds bullet): "- **Listed items (audit).** An item in `listed.md` that neither a B row on its line nor its `<item> | none` line answers holds the sections it names. Settle prints how many items a B row answered, how many were answered none and which are unanswered, and an unanswered item makes the exit 1. A `<item> | none` line for an ID that `listed.md` does not hold is unparseable and holds every section in the packet."
  - `SKILL.md`, `## audit [<group>]`: after "It costs about \$2.50–5.30." add "Its `listed.md` lists each changelog bullet that names one of the group's terms, about 300 to 400 per group on the changelog of 2026-11-17, and the verifier answers each one with a B row or `<item> | none`. That adds about 20,000 input tokens and as many short answers."

- [ ] **Step 6: Run the term gate** on the agent file:

```bash
git diff -U0 dc8e020 HEAD -- .claude/agents/cc-guide-verifier.md | /usr/bin/grep '^+[^+]' | /usr/bin/grep -iE 'deniedModels|availableModels|effortLevel|effort|opus|sonnet|haiku|fable|1288|1702|2\.1\.28[03]|matcher|newline|uv-guard|README\.md:89|permission'
```

Expected: no output, exit 1. Run it again after Task 5 against the same base.

- [ ] **Step 7: Run the checks and confirm GREEN.**

```bash
uv run python build/run_suites.py cc_guide
uv run python build/cc_guide/cli.py lint
uv run --with pyyaml python build/check_conformance.py
```

Expected: the suite passes, `+6` against Task 1's count: 4 settle tests, 1 skill-file test, and 1 new case of the parametrized format test. Lint prints the same lines as before Task 1. Conformance passes.

- [ ] **Step 8: Commit.**

```bash
git add build/cc_guide/report_grammar.py build/cc_guide/settle.py build/cc_guide/test_settle.py build/cc_guide/test_skill_files.py .claude/agents/cc-guide-verifier.md .claude/skills/cc-guide/SKILL.md .claude/skills/cc-guide/references/formats.md
git commit -m "feat(cc-guide): answer every listed changelog bullet in an audit (plan 102)"
```

### Task 3: Covered files in a files packet (B1, B2)

**Files:**
- Modify: `build/cc_guide/state.py` (`Source.tracked_under`, new `covered_files`)
- Modify: `build/cc_guide/packets.py` (new `COVERED`; `files()`; `write_packet` creates parent folders)
- Modify: `.claude/skills/cc-guide/references/formats.md` (the files row)
- Test: `build/cc_guide/test_state.py`, `build/cc_guide/test_packets.py`

**Interfaces:**
- Produces: `Source.tracked_under(folder: str) -> list[str]`: the tracked files under `folder`, as sorted repo paths, read where the source reads: `git ls-files -z -- <folder>` for the working tree, `git ls-tree -r -z --name-only <ref> -- <folder>` for a ref (PC7). A git failure is a `SetupError`.
- Produces: `state.covered_files(source: Source, path: str) -> list[str]`. A `path` that fully matches `(?:\.claude/)?skills/[^/]+/SKILL\.md` covers each tracked `.md` file under its folder, except `path` itself, any file named `README.md`, and any file with a `scripts` folder in its path below the skill folder. The list is sorted. Any other path covers `[]`.
- Produces: `packets.COVERED = 'covered'`. `files()` writes each covered file to `covered/<path within the skill folder>` and adds `'covered': {<repo path>: 'covered/<path within the skill folder>'}` to `index.json`. A file that covers nothing gets `{}`.

- [ ] **Step 1: Write the failing tests.**

In `test_state.py`, with `fixture_repo` and `git` from `cc_fixtures`:

```python
SKILL_TREE = {'skills/demo/SKILL.md': 'a\n', 'skills/demo/beside.md': 'b\n', 'skills/demo/references/a.md': 'c\n',
              'skills/demo/references/deep/b.md': 'd\n', 'skills/demo/README.md': 'e\n',
              'skills/demo/references/README.md': 'f\n', 'skills/demo/scripts/notes.md': 'g\n',
              'skills/demo/references/scripts/x.md': 'h\n', 'skills/demo/data.txt': 'i\n',
              '.claude/skills/local/SKILL.md': 'j\n', '.claude/skills/local/ref.md': 'k\n',
              'runtimes/gemini/skills/demo/SKILL.md': 'l\n', 'runtimes/gemini/skills/demo/x.md': 'm\n'}


def test_covered_files_are_a_skills_on_demand_markdown(tmp_path):
    repo = fixture_repo(tmp_path / 'repo', SKILL_TREE)
    source = state.Source(repo)
    assert state.covered_files(source, 'skills/demo/SKILL.md') == [
        'skills/demo/beside.md', 'skills/demo/references/a.md', 'skills/demo/references/deep/b.md']
    assert state.covered_files(source, '.claude/skills/local/SKILL.md') == ['.claude/skills/local/ref.md']
    assert state.covered_files(source, 'runtimes/gemini/skills/demo/SKILL.md') == []
    assert state.covered_files(source, 'skills/demo/beside.md') == []
    write_tree(repo, {'skills/demo/new.md': 'n\n'})
    git(repo, 'add', 'skills/demo/new.md')
    assert 'skills/demo/new.md' in state.covered_files(source, 'skills/demo/SKILL.md')
    assert 'skills/demo/new.md' not in state.covered_files(state.Source(repo, 'HEAD'), 'skills/demo/SKILL.md')
```

In `test_packets.py`, after `test_files_takes_named_citing_files_and_refuses_any_the_lint_never_reads`, add a citing skill to the world's repo and commit it (a helper `with_skill(world)`). Its `SKILL.md` carries `# cc-guide: alpha.overview @2.1.900` as its frontmatter's last line. Beside it are `skills/demo/beside.md`, `skills/demo/references/a.md`, `skills/demo/references/deep/b.md`, `skills/demo/README.md` and `skills/demo/scripts/notes.md` (spec B6's cases):

```python
def test_a_files_packet_for_a_skill_copies_each_covered_file(world, tmp_path):
    with_skill(world)
    out = packets.files(load(world), tmp_path / 'f', ['skills/demo/SKILL.md', 'hooks/gate.sh'])
    skill, gate = (index(folder) for folder in out)
    assert skill['covered'] == {'skills/demo/beside.md': 'covered/beside.md',
                                'skills/demo/references/a.md': 'covered/references/a.md',
                                'skills/demo/references/deep/b.md': 'covered/references/deep/b.md'}
    assert sorted(str(p.relative_to(out[0])) for p in (out[0] / 'covered').rglob('*.md')) == sorted(
        skill['covered'].values())
    for repo_path, copy in skill['covered'].items():
        assert (out[0] / copy).read_text() == (world[0] / repo_path).read_text()
    assert gate['covered'] == {} and not (out[1] / 'covered').exists()
```

- [ ] **Step 2: Run them and confirm RED.**

Run: `uv run python build/run_suites.py cc_guide -- -k "covered"`
Expected: 2 FAIL, an `AttributeError` on `covered_files` and a `KeyError: 'covered'`.

- [ ] **Step 3: Implement `tracked_under`, `covered_files`, `COVERED`, the `files()` change and nested writes in `write_packet`.**

- [ ] **Step 4: Edit `formats.md`'s files row.** Files: add `` `covered/<path within the skill folder>` (a copy of each Markdown file a skill's `SKILL.md` citation covers: each tracked `.md` file in the skill folder or below it, except `SKILL.md`, any `README.md` and anything under `scripts/`) ``. Index: add `covered` (repo path to copy; `{}` for a file that is no skill's `SKILL.md`).

- [ ] **Step 5: Run the suite and confirm GREEN.** Run: `uv run python build/run_suites.py cc_guide`. Expected: all pass, `+2` against Task 2's count.

- [ ] **Step 6: Commit.**

```bash
git add build/cc_guide/state.py build/cc_guide/packets.py build/cc_guide/test_state.py build/cc_guide/test_packets.py .claude/skills/cc-guide/references/formats.md
git commit -m "feat(cc-guide): copy the files a skill's citation covers into its files packet (plan 102)"
```

### Task 4: Settle reads rows on covered files (B4, B6)

**Files:**
- Modify: `build/cc_guide/settle.py` (`settle_files`; new `covered_changes`)
- Modify: `.claude/skills/cc-guide/references/formats.md` (the Holds bullet)
- Test: `build/cc_guide/test_settle.py`

**Interfaces:**
- Consumes: `state.covered_files`, `index['covered']` (Task 3).
- Produces: `settle.covered_changes(p: Packet, repo: Path) -> list[str]`: the sorted repo paths of covered files whose text in the checkout differs from the packet's copy or is gone, and of files that `covered_files(Source(repo), p.index['file'])` adds to or drops from `p.index['covered']`. A packet with no `covered` key gives `[]`, so an older packet is never held for it.
- Produces, in `settle_files`:
  - a row's file may be `index['file']` or a key of `covered`. Any other file stays unparseable;
  - with a non-empty `covered`, the two phrases "in {path}" (the contradictions heading and the closing line) read "in {path} or the covered file its row names". With `covered` empty or absent, every line stays byte-identical to today's;
  - `covered_changes` adds the hold reason `covered files changed after its packet was built: <paths, joined by ', '>`;
  - `baseline cite` still names only `index['file']`.

- [ ] **Step 1: Write the failing tests** in `test_settle.py`, after `test_a_file_whose_citation_stamp_alone_changed_is_still_cited`. A helper `skill_packet(world, tmp_path)` commits the demo skill of Task 3's packet test into the world's repo and returns its files packet. `SKILL_OK = ('skills/demo/SKILL.md:5 | a body | alpha.overview | "Alpha uses `ALPHA_TOOL`" | consistent',)`.

```python
def test_settle_accepts_a_row_on_a_covered_file_and_discards_one_on_another_file(world, tmp_path):
    out = skill_packet(world, tmp_path)
    result = settled(out, *SKILL_OK,
                     'skills/demo/references/a.md:1 | uses ALPHA_TOOL | alpha.overview | "Alpha uses `ALPHA_TOOL`" | contradicts',
                     'skills/demo/other.md:1 | x | alpha.overview | "Alpha uses `ALPHA_TOOL`" | consistent')
    assert 'contradictions, to fix in skills/demo/SKILL.md or the covered file its row names in the working tree:' in result.lines
    assert '  skills/demo/references/a.md:1 (alpha.overview): uses ALPHA_TOOL (guide: "Alpha uses `ALPHA_TOOL`")' in result.lines
    assert any(line.startswith('  unparseable: skills/demo/other.md:1') for line in result.lines)


@pytest.mark.parametrize('move, path', [('change', 'skills/demo/references/a.md'), ('add', 'skills/demo/new.md'),
                                        ('remove', 'skills/demo/beside.md')])
def test_a_covered_file_that_moved_holds_the_citing_file(world, tmp_path, move, path):
    out = skill_packet(world, tmp_path)
    repo = world[0]
    if move == 'remove':
        git(repo, 'rm', '-q', path)
    else:
        write_tree(repo, {path: 'moved\n'})
        git(repo, 'add', path)
    result = settled(out, *SKILL_OK)
    assert (f'held, not cited: skills/demo/SKILL.md: covered files changed after its packet was built: {path}'
            in result.lines)
    assert not any(' baseline cite ' in line for line in result.lines)


def test_a_files_packet_without_covered_settles_as_before(world, tmp_path):
    '''Guard: passes at RED, and must still pass at GREEN.'''
    out = skill_packet(world, tmp_path)
    i = json.loads((out / packets.INDEX).read_text())
    del i['covered']
    (out / packets.INDEX).write_text(json.dumps(i))
    result = settled(out, *SKILL_OK)
    assert f'  {CLI} baseline cite skills/demo/SKILL.md' in result.lines
    assert not any(line.startswith('held') for line in result.lines)
```

- [ ] **Step 2: Run them and confirm RED.**

Run: `uv run python build/run_suites.py cc_guide -- -k "covered"`
Expected: the first test and the three parametrized cases FAIL (the covered-file row is unparseable, and no hold line appears). The guard and Task 3's tests pass.

- [ ] **Step 3: Implement `covered_changes` and the `settle_files` change** to the Interfaces block.

- [ ] **Step 4: Edit `formats.md`'s Holds bullet.** After "…no longer matches the packet's copy, which the verifier read (`the file changed after its packet was built`)." add: "For a skill, a row may name a covered file, and the file is also held when a covered file differs from its copy or the skill has gained or lost one since the packet was built (`covered files changed after its packet was built`)."

- [ ] **Step 5: Run the suite and confirm GREEN.** Run: `uv run python build/run_suites.py cc_guide`. Expected: all pass, `+5` against Task 3's count.

- [ ] **Step 6: Commit.**

```bash
git add build/cc_guide/settle.py build/cc_guide/test_settle.py .claude/skills/cc-guide/references/formats.md
git commit -m "feat(cc-guide): settle rows on covered files and hold a skill whose covered files moved (plan 102)"
```

### Task 5: The files contract, covered files and component scope (B3, B5, C1, C2)

**Files:**
- Modify: `.claude/agents/cc-guide-verifier.md` (`### files`)
- Modify: `.claude/skills/cc-guide/SKILL.md` (Ground rules, `## files [<paths>]` step 2), `.claude/skills/cc-guide/references/formats.md` (Reports, files)
- Test: `build/cc_guide/test_skill_files.py`

This task makes two commits, so that C1 can revert alone (spec D6).

- [ ] **Step 1: Write the failing B3 test** at the end of `test_skill_files.py`:

```python
def test_the_files_rows_cover_the_cited_file_and_each_covered_file():
    text = (REPO / AGENT).read_text(encoding='utf-8')
    assert 'Give one row per statement in the cited file or a covered file that rests on a cited section' in text
    assert 'or a path `covered` names' in text
```

Run: `uv run python build/run_suites.py cc_guide -- -k covered_file`. Expected: FAIL on the first assertion.

- [ ] **Step 2: Replace the `### files` section's text above its format block** with this, exactly:

```markdown
The cited file's copy is the file `index.json` names as `copy`; its line numbers are the file's. When the cited file is a skill's `SKILL.md`, `index.json` also names `covered`: each Markdown file the skill loads on demand, by its repo path, with the packet copy that holds it; a copy's line numbers are its file's. `sections.md` holds the sections the citation names, each marked when it changed after the file's stamp. Give one row per statement in the cited file or a covered file that rests on a cited section, and a none line for each cited section that no statement in those files rests on:
```

Replace the sentence after the format block that begins "`file` is the path" with:

```markdown
`file` is the path `index.json` names as `file`, or a path `covered` names, as in `hooks/README.md:56`. A not-covered row may leave its quote `-`. A cited section with no row and no none line holds the file, as if unreviewed.
```

- [ ] **Step 3: Edit the skill text** (B5).
  - `SKILL.md`, Ground rules: replace "Edit only the guide in verify and audit, and only the reviewed file in files." with "Edit only the guide in verify and audit, and in files only the reviewed file or a file its packet's `covered` names."
  - `SKILL.md`, `## files [<paths>]` step 2: replace "fix each contradiction it lists, in that file only" with "fix each contradiction it lists, in the file its row names: the reviewed file or one its packet's `covered` names".
  - `formats.md`, Reports: replace "Files, one row per statement that rests on a cited section" with "Files, one row per statement in the cited file or a covered file that rests on a cited section".

- [ ] **Step 4: Run the checks, the term gate (Task 2 Step 6) and commit.** Expected: the suite passes, `+1` against Task 4's count. Lint and conformance are as in Task 2 Step 7, and the term gate prints nothing.

```bash
git add .claude/agents/cc-guide-verifier.md .claude/skills/cc-guide/SKILL.md .claude/skills/cc-guide/references/formats.md build/cc_guide/test_skill_files.py
git commit -m "feat(cc-guide): have the files verifier review a skill's covered files (plan 102)"
```

- [ ] **Step 5: Write the failing C2 test:**

```python
def test_the_files_rule_compares_a_statement_with_the_component_it_describes():
    lines = (REPO / AGENT).read_text(encoding='utf-8').split('\n')
    (rule,) = [line for line in lines if 'the component the statement describes' in line]
    assert 'is not Claude Code' in rule
```

Run: `uv run python build/run_suites.py cc_guide -- -k component`. Expected: FAIL (`ValueError` from the empty unpack).

- [ ] **Step 6: Add C1** as the last paragraph of `### files`, exactly:

```markdown
Compare each statement with what the guide says about the component the statement describes. A repo's own script, hook or agent is not Claude Code: a guide fact about how Claude Code behaves contradicts a statement only when the statement describes that behaviour.
```

- [ ] **Step 7: Run the checks and the term gate, then commit.** Expected: the suite passes, `+1` against Step 4's count. The term gate prints nothing. Record this commit's SHA as `ARM_COMMIT` in the SDD ledger.

```bash
git add .claude/agents/cc-guide-verifier.md build/cc_guide/test_skill_files.py
git commit -m "feat(cc-guide): scope the files rule to the component a statement describes (plan 102)"
```

- [ ] **Step 8: Prove that each revert unit reverts cleanly.** With a clean working tree, run each of these, then `git revert --abort` after each one:
  - `git revert --no-commit <Task 2 commit> <Task 1 commit>` (Part A);
  - `git revert --no-commit <Task 5 second commit>` (C1 alone);
  - `git revert --no-commit <Task 5 second commit> <Task 5 first commit>` (B3 and C1).

  Expected: no conflict in any of them. A conflict is a plan defect: move the text so that an unchanged line separates the units, amend the commit before any kit work, and log the deviation.

### Task 6: The kit's runner and its no-model tests

**Files:**
- Create: `specs/baseline/red-baseline-cc-guide-verifier-recall/kit/common.py`, `build.py`, `run.py`, `postprocess.py`, `README.md`, `test_vr_runner.py`
- Modify: `build/suites.toml` (one `[[suite]]` table)

**Interfaces:**
- Consumes: `START` (Before Task 1) and `ARM_COMMIT` (Task 5).
- Produces: `common.py`:
  - `k_dir() -> Path`, `~/.cache/agent-skills/scratch/vr102`, read from `HOME` at call time so tests can move it;
  - `KIT` (this folder), `REPO` (the repo root, from `__file__`), and `R = Path('/private/tmp/vr102')`, a module attribute that tests may replace;
  - `CAPS`, `TIMEOUTS` and `BG_CEILING_MS` (PC9), `MARKERS` (V3), `MAIN` (the main session's prompt template), `SETTINGS` (PC2's `--settings` JSON) and `PACKETS` (the Pre-registration table).
- Produces: `build.py batch <name> <packet> <pairs>`, which appends `<pairs>` (control, changed) pairs to `$K/plan.json` under new rep ids (`r001` on, never reused). It puts each pair's arms in random order with `secrets` (DF15) and writes `$K/batches/<name>.txt`, which names rep ids only. `build.py spare <rid>` adds one rep with the void rep's packet and arm, and refuses a third spare for a packet and arm without naming the arm.
- Produces: `build.py probe` and `build.py pilot`, the two uncounted reps. The probe rep's work folder holds the control arm's file and the kit's `vr-probe.md` as `.claude/agents/vr-probe.md`, and its prompt is the kit's `probe.txt` (both Task 8). The pilot is one changed-arm audit rep.
- Reads: the arms from `$K/arms/control.md` and `$K/arms/changed.md` (Task 8 Step 3), the packet copies from `$K/fixtures/audit-control/`, `audit-changed/`, `readme/` and `precision/`, and the docs from `$K/fixtures/docs/` (Task 7). This task's tests use small fakes in the same layout.
- Produces: `run.py <batch>`, which runs the batch's reps one at a time and skips a rep that has results. For each rep it:
  1. refuses (exit 3) while `R` holds anything (C6);
  2. refuses when `$K/binary.txt`'s sha256 does not match the held binary;
  3. holds the rep when the spend so far plus its cap exceeds `$K/ceiling.txt`;
  4. builds `R/<rid>/work/` and `R/<rid>/tmp/` (Rep layout), rewriting an audit copy's `docs` and `quotes.docs`;
  5. runs `command(rid)` with `MAIN` on stdin and the rep's timeout, writing `stream.jsonl` and `stderr.txt` to `$K/results/<rid>/`;
  6. moves the session's files, found under `~/.claude/projects/` by the init record's `session_id`, to `$K/results/<rid>/project/`;
  7. writes `result.json`, the stream's `result` record;
  8. runs `postprocess.py strip-tree` on `$K/results/<rid>/`, then fails the rep (V6) if the string `credential_expires_at` remains anywhere there;
  9. moves `R/<rid>` to `$K/homes/<rid>`.
- Produces: `command(rid) -> tuple[list[str], dict[str, str]]`, the argv and environment. Argv: `<held binary> -p --permission-mode auto --settings <SETTINGS> --max-budget-usd <cap> --output-format stream-json --verbose`. Environment, which is all of it (`env -i`): `HOME`, `USER`, `LOGNAME`, `SHELL=/bin/zsh`, `LANG`, `PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin`, `TMPDIR=R/<rid>/tmp`, `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=<BG_CEILING_MS>` and `DISABLE_AUTOUPDATER=1`. There is no `--model` (PC10) and no `--setting-sources`. The working folder is `R/<rid>/work`.
- Produces: `postprocess.strip(obj) -> obj` (removes the key `credential_expires_at` at any depth) and `postprocess.py strip-tree <dir>` (strips every `.json` and `.jsonl` file under the folder in place).

- [ ] **Step 1: Confirm the control pin.** Read `START` and the empty diff from the ledger (Before Task 1). If either is missing, stop and record them first.

- [ ] **Step 2: Reuse or write `postprocess.py`** (D1). If `git cat-file -e origin/main:specs/baseline/red-baseline-handoff-rerun/kit/postprocess.py` succeeds, copy that file into this kit byte for byte and record its blob SHA in the kit `README.md`. Otherwise, write it to the Interfaces block. The tests are the same either way.

- [ ] **Step 3: Write the failing tests** in `test_vr_runner.py`. Each sets `HOME` to a temporary folder (so `k_dir()` is temporary), points `R` at a temporary folder through a module attribute, and writes a stub `claude`. The stub is a Python script that records its argv, environment and working folder, writes a marker file into its working folder and `TMPDIR`, lists `R` recursively into its stream, and prints an init record and a `result` record (with a nested `credential_expires_at` and `total_cost_usd`). It also writes a fake session file under `$HOME/.claude/projects/<slug>/`.
  - `test_two_reps_see_nothing_of_each_other`: two reps run in one batch. Rep 2's listing names no rep-1 marker and no `r001`, and `r001` is under `$K/homes/`. (next-kit item, scratch folders)
  - `test_the_runner_refuses_a_nonempty_rep_root`: with a stray file in `R`, `run.py` exits 3 and starts no stub.
  - `test_rep_files_hold_no_credential_expires_at`: after a rep, no file under `$K/results/<rid>/` holds the string, and `result.json` keeps `total_cost_usd`. (next-kit item, strip)
  - `test_the_rep_command_denies_bash_and_fences_reads`: `command(rid)`'s `--settings` JSON has `"Bash"` and `"Read(~/**)"` in `permissions.deny` and `blockReadsOutsideWorkingDirectories` true. Its environment holds exactly the Interfaces block's keys, with the ceiling above the audit timeout in milliseconds. (next-kit item, Bash gap; the probe in Task 8 is its live test)
  - `test_no_controller_variable_reaches_a_rep`: with `CLAUDECODE=1` and `CLAUDE_CODE_ENTRYPOINT=cli` in the runner's own environment, the rep runs, and the environment the stub records holds exactly the Interfaces block's keys (PC11).
  - `test_the_ceiling_holds_a_rep_whose_cap_does_not_fit`.
  - `test_an_audit_reps_index_names_its_own_docs_copy_in_both_arms`: for an audit rep of each arm, `docs` and `quotes.docs` name `R/<rid>/work/docs`, and the two arms' `index.json` differ only in `listed`.
  - `test_build_orders_each_pair_at_random_and_batches_name_no_arm`, and `test_build_refuses_a_third_spare`.

- [ ] **Step 4: Register the suite.** Add to `build/suites.toml`, before the `cc_guide` table (name order):

```toml
[[suite]]
name = 'cc-guide-verifier-recall-kit'
dir = 'specs/baseline/red-baseline-cc-guide-verifier-recall/kit'
with = ['pytest']
notes = ['Plan 102 micro-test kit: no-model tests with a stub claude. The fixture tests skip without the cache masters.']
```

Run: `uv run python build/run_suites.py cc-guide-verifier-recall-kit`. Expected: every test FAILs on its import (`common`, `build` or `run` missing). `uv run python build/run_suites.py --check` passes.

- [ ] **Step 5: Write `common.py`, `build.py`, `run.py` and the kit `README.md`** to the Interfaces block. The README names the kit's purpose, `$K`, `R`, the commands in order, and plan 102 as the source of every rule.

- [ ] **Step 6: Run the kit suite and confirm GREEN.** Expected: all pass, `+9`.

- [ ] **Step 7: Commit.**

```bash
git add specs/baseline/red-baseline-cc-guide-verifier-recall/kit build/suites.toml
git commit -m "test(cc-guide): add the verifier-recall kit's runner and its no-model tests (plan 102)"
```

### Task 7: Fixtures, the precision key and the grader

**Files:**
- Create: `specs/baseline/red-baseline-cc-guide-verifier-recall/kit/fixtures.py`, `grade.py`, `test_vr_grade.py`, `test_vr_fixtures.py`

**Interfaces:**
- Consumes: `packets.listed_bullets`, `packets.listed_lines`, `state.parse_manifest`, `state.group_terms` (from `build/cc_guide/`, put on `sys.path` by `common.py`); `settle.settle`; `probe_checks.parse_stream`, `probe_checks.dispatches`, `probe_checks.tool_result_text`; `probes.read_transcripts`.
- Produces: `fixtures.py build`, which writes `$K/fixtures/`:
  - `audit-control/` and `audit-changed/`, copies of the audit master without `report.md` or `settled.json`. Only `audit-changed/` gains `listed.md` and `index.json` `listed`, computed with `git show 5bd78a7:build/cc_guide/manifest.toml` as the manifest. Group `models`;
  - `docs/`, a copy of the 2.1.296 snapshot;
  - `readme/`, a copy of the readme master with `"covered": {}` added to `index.json`;
  - `precision/`, a copy of the packet that Step 1 builds.

  It writes `$K/fixtures.sha256` (a `shasum -a 256` listing) and prints the listed-item count. It fails when `listed` holds no item at line 1288 or at line 1702. It never writes under a master (it opens them read-only and copies with `shutil.copytree`).
- Produces: `grade.py <batch>`, which writes one sheet per rep, `$K/sheets/<rid>.txt`, naming no arm. A sheet holds:
  - the VOID checks V1 to V8, each `ok` or the reason;
  - settle's lines for the rep's report. They come from a scratch copy of the packet, with the report as `report.md`. Every audit rep, of either arm, is settled against a copy of `$K/fixtures/audit-changed/`, so the sheet's layout names no arm (DF15). Kept corrections and B rows do not depend on `listed`, and the control's listed counts become a reported measure. In that copy, `docs` and `quotes.docs` point at `$K/fixtures/docs`, since the rep's own docs copy moved to `$K/homes/` with its folder, and a stale path would discard every doc quote;
  - for an audit rep: every B row on `changelog.md:1288`, `:1702` or `:224`, every row that names `deniedModels`, every kept correction and C row with its guide line (P1 to P14 candidates), the listed-item counts, and the B-row count;
  - for a files rep: every kept `contradicts` row, whether a kept row names a covered file, and every row on `hooks/README.md` lines 85 to 93;
  - the cost and duration.
- Produces: `grade.py stop <batch>`, which refuses until every sheet of the batch has its verdicts in `$K/RESULTS.md`. It then applies gate A's first-wave stop rules and prints only `continue`, `stop: UNSETTLED` or `stop: FAIL`, with no count per arm.
- Produces: `grade.py unblind <gate>` (`F` or `A`), which refuses until every sheet of that gate's batches has its verdicts in `$K/RESULTS.md`. It then joins `$K/plan.json` and prints that gate's tables of the Pre-registration.
- The report is taken as plan 45's V6 takes it: a finished Agent result that is no launch notice, else the main session's handback.

- [ ] **Step 1: Build the precision packet.** On the execution worktree, whose HEAD holds Part B's code, record `FIXTURE_COMMIT=$(git rev-parse HEAD)` in the ledger. A files packet needs a latest fetch but not fresh docs. Run `cli.py check --worktree` only when `~/.cache/agent-skills/cc-guide/latest/fetch.json` is absent, since a refetch makes another session's `rebaseline --head` refuse. Then:

```bash
uv run python build/cc_guide/cli.py packets --files skills/writing-skills/SKILL.md --out ~/.cache/agent-skills/scratch/vr102/masters/precision
```

Expected: one packet folder, `skills__writing-skills__SKILL.md/`, whose `index.json` `covered` names 7 files. Record the `head` and `cache` from its index in `$K/changes.log`.

- [ ] **Step 2: Build the precision key** before any rep (spec D4). The controller reads each statement, in `cited_SKILL.md` and in each covered copy, that rests on one of the 8 cited sections. It lists those that truly contradict their section in the packet's `guide.md`, in `$K/precision-key.tsv` (columns `file:line`, section, guide line, why in own words). Then it dispatches one fresh read-only subagent (`general-purpose`, `model: opus`). The subagent gets the packet folder and plan 45's SUPPORTED definition with this plan's files clause, and nothing else. It builds its own list. The controller resolves each difference against the guide text and logs both lists and each resolution in `$K/changes.log`. An empty key is a valid key.

- [ ] **Step 3: Write the failing tests.** Every test feeds hand-written data. No test reads a docs file, except where marked.
  - `test_vr_fixtures.py`:
    - `test_the_changed_audit_copy_lists_p11_and_p8` (skips with a reason when the audit master is absent): after `fixtures.py build`, `audit-changed/index.json` `listed` has items with lines 1288 and 1702, and `audit-control/` has no `listed`;
    - `test_a_fixture_build_never_writes_under_a_master`: on fake masters, every master file's mtime and hash are unchanged after a build.
  - `test_vr_grade.py`, on synthetic streams and transcripts:
    - `test_v1_allows_model_sonnet_and_voids_another_tool_call`;
    - `test_v2_voids_an_outside_read_that_returned_and_logs_a_refused_one`, including a `/System/Volumes/Data/private/tmp/` path inside `work/` (allowed) and a relative `../` path that leaves it (void);
    - `test_v5_voids_a_snapshot_whose_first_part_is_not_the_arm_body`;
    - `test_v7_compares_model_effort_and_version_with_the_pilot`;
    - `test_v8_follows_the_production_advisor`;
    - `test_an_audit_sheet_lists_p11_and_p8_candidates_and_the_listed_counts`: a report with `B | 2.1.283 | x | changelog.md:1288` and a C row naming `deniedModels` shows both. The sheet's listed counts equal settle's, and a doc quote that the fixtures' docs copy holds is kept even after the rep folder has moved;
    - `test_a_files_sheet_lists_kept_contradictions_and_covered_rows`;
    - `test_no_sheet_names_an_arm`: no sheet holds `control` or `changed`;
    - `test_one_audit_report_gives_the_same_sheet_in_either_arm`: the same report, graded as a control rep and as a changed rep, gives sheets that differ only in the rep id;
    - `test_stop_prints_no_count_per_arm`: on verdicts where the control meets P11 in 2 reps, `grade.py stop` prints exactly `stop: UNSETTLED`;
    - `test_unblind_refuses_before_every_verdict_is_in`.

Run: `uv run python build/run_suites.py cc-guide-verifier-recall-kit`. Expected: the new tests FAIL on import. The master-reading test may skip in CI.

- [ ] **Step 4: Write `fixtures.py` and `grade.py`** to the Interfaces block.

- [ ] **Step 5: Run the kit suite and confirm GREEN** (`+13`). Then run `fixtures.py build` against the real masters and the precision packet. Expected: it prints a listed count near 206 (do not pin it; brief trap 2), and `test_the_changed_audit_copy_lists_p11_and_p8` passes locally.

- [ ] **Step 6: Commit** the kit code only. The key and fixtures stay in `$K`.

```bash
git add specs/baseline/red-baseline-cc-guide-verifier-recall/kit
git commit -m "test(cc-guide): add the verifier-recall kit's fixtures and grader (plan 102)"
```

### Task 8: Freeze, the ceiling, the probe and the pilot (paid)

**Files:**
- Create: `specs/baseline/red-baseline-cc-guide-verifier-recall/kit/probe.txt`, `vr-probe.md`
- Create: `specs/baseline/red-baseline-cc-guide-verifier-recall.md` (the record: Method, Probe, Pilot)

- [ ] **Step 1: Hold the binary** (spec D8, brief trap 3). Copy the newest version that `uv run python build/cc_guide/cli.py binaries` lists to `$K/bin/claude-<version>`, outside `~/.local/share/claude/versions/`. Write its path, version and `shasum -a 256` to `$K/binary.txt`. Every rep runs this copy, and `run.py` checks the hash.

- [ ] **Step 2: Find the production comparison.** Find the newest `agent-*.meta.json` under `~/.claude/projects/` whose agent type is `cc-guide-verifier`, from a `/cc-guide` run. Record its path in `$K/changes.log`, with its version, its model and effort, whether it had an advisor attachment, and its attachment types. If its version differs from the held binary's, record that too.

- [ ] **Step 3: Freeze.** Copy the arms to `$K/arms/control.md` and `$K/arms/changed.md` (Pre-registration). Write `$K/FREEZE.sha256` over the kit files, the arms, `fixtures.sha256`, the precision key, the binary and this plan's Pre-registration section.

- [ ] **Step 4: Owner gate: the ceiling** (D2). Tell the owner the Cost table and its expected range, the proposed $130 ceiling and the caps. Wait for an approved number. Write it to `$K/ceiling.txt` and log it in `## Decisions` as `D3`.

- [ ] **Step 5: Probe.** Write `probe.txt`, which asks the main session for three things, each reported as one line:
  1. run, with the Bash tool, one `for`-loop `ls ~/…` command (spec Part D, D2's construction), whose exact text the probe file holds;
  2. Read `$K/canary.txt`, which holds a random token that `build.py probe` writes, by its absolute path;
  3. dispatch the agent `vr-probe`, which the probe rep's `.claude/agents/` holds. Write `vr-probe.md` with tools Read, Grep and Glob and `model: sonnet`; its body asks it to read the canary, read one file in `work/docs/`, and name its tools.

  Run it with `run.py probe`, in the background. Its stream is saved to `$K/results/<rid>/`, and the record carries only the counts.
  Expected: the Bash call's result is a permission denial, or no Bash call exists because the tool is refused. Both canary reads are refused. The token appears in no stream or transcript. The docs read returns. `vr-probe` names Read, Grep and Glob. No hook error appears in the stream. Any other outcome stops the run for the owner.

- [ ] **Step 6: Pilot** (PC8). Run `run.py pilot` (one changed-arm audit rep), then `grade.py pilot`. Compare it with Step 2's production verifier: system-prompt parts by index, model, effort, version, advisor, attachment types, request shape (background or not) and entrypoint (`sdk-cli` against `cli` is known). Read its whole injected context by hand (V3). Log the three rulings the Pre-registration allows.
  Expected: valid under V1 to V8 as ruled; the report arrived before the timeout; the verifier made only Read, Grep and Glob calls; no hook error appears in the stream (a crashed hook fails open). Record its listed-item counts, duration and cost, and apply the Pilot check. P11 and P8 are not scored.

- [ ] **Step 7: Estimate again** (D2). Re-estimate the run from the pilot's cost, scaled for the control arm by plan 45's control-to-changed ratio. When the new expected total exceeds the approved ceiling, stop and ask the owner. Otherwise continue, and log the estimate.

- [ ] **Step 8: Write the record's Method, Probe and Pilot sections, and commit.** Method: `START`, `ARM_COMMIT`, `FIXTURE_COMMIT`, the binary's version and hash, the command (Task 6's Interfaces), PC2 and PC9 to PC11, the freeze hash and the ceiling. Probe and Pilot: outcomes as counts and labels.

```bash
git add specs/baseline/red-baseline-cc-guide-verifier-recall/kit/probe.txt specs/baseline/red-baseline-cc-guide-verifier-recall/kit/vr-probe.md specs/baseline/red-baseline-cc-guide-verifier-recall.md
git commit -m "test(cc-guide): record the verifier-recall probe and pilot (plan 102)"
```

### Task 9: Gate F (paid)

- [ ] **Step 1: Build and run the batch.** `build.py batch gateF readme 3` and `build.py batch gateF precision 3`, then `run.py gateF` (in the background) and `grade.py gateF`. Replace each void rep with `build.py spare <rid>` and run the spares.
- [ ] **Step 2: Rate.** Read every sheet and enter each verdict in `$K/RESULTS.md` (Scoring). Then run `grade.py unblind F`.
- [ ] **Step 3: Decide** under the Decision rules. On FAIL, give the owner the counts and ask: revert C1 alone and rerun gate F as a new round within the ceiling (`$K/arms/changed-b.md`, new rep ids), or revert both B3 and C1. Log the ruling in `## Decisions`.
- [ ] **Step 4: Write the record's gate F result,** as counts per arm with sheet pointers, and commit it: `test(cc-guide): record gate F of the verifier-recall micro-test (plan 102)`.

### Task 10: Gate A (paid)

- [ ] **Step 1: First wave.** `build.py batch gateA1 audit 2`, `run.py gateA1` (in the background), `grade.py gateA1`. Rate the sheets, then run `grade.py stop gateA1`, which names no arm. On a stop, run `grade.py unblind A`, report to the owner and skip Step 2.
- [ ] **Step 2: Second wave.** Build pairs and spares to reach 5 valid reps per arm (`build.py batch gateA2 audit 3`, plus spares), then run, grade and rate. Run `grade.py unblind A` only once every gate A sheet has its verdicts.
- [ ] **Step 3: Decide** under the Decision rules, and write the record's gate A result: a clause-by-clause table as plan 45's record has, with the reported measures. Commit: `test(cc-guide): record gate A of the verifier-recall micro-test (plan 102)`.

### Task 11: Land or revert, and the record's close

**Files:**
- Modify: `specs/baseline/red-baseline-cc-guide-verifier-recall.md` (Decision, Disposition)
- Modify, by gate: the files of Tasks 1, 2 and 5; `.claude/skills/cc-guide/SKILL.md` (audit cost)

- [ ] **Step 1: Apply the gates.**
  - Gate A PASS: Part A stays. In `SKILL.md`'s audit section, replace "about \$2.50–5.30" with the range of the valid changed audit reps' costs, rounded out to the nearest $0.10.
  - Gate A FAIL: `git revert` Task 2's commit, then Task 1's, in one session. Gate A UNSETTLED: the owner rules.
  - Gate F PASS: Task 5's two commits stay.
  - Gate F FAIL: apply the owner's Task 9 ruling, reverting Task 5's second commit, or both.
  - Part B's code (Tasks 3 and 4) stays in every case (spec E2).
- [ ] **Step 2: Run every check.** Run the `cc_guide` and kit suites, `cli.py lint` (the same lines as before Task 1), `check_conformance.py` and `build/run_commit_lints.sh`. Expected: all pass. Report each count as a delta.
- [ ] **Step 3: Write the record's Decision and Disposition.** Disposition names, for each backlog item, the clause that closes it or keeps it open (Completion, below). It names E3's files pass as the next step.
- [ ] **Step 4: Commit:** `docs(cc-guide): record the verifier-recall decision and disposition (plan 102)`.

---

## Completion (for the Plan Completion Protocol)

Each item closes on its own done-when (spec E4), with a `→ done <date>` note that gives the counts and the record's path:
- **I3** ("The audit verifier writes no B row…"): when gate A passes.
- **I4** ("The audit verifier's omission recall…"): when the changed arm meets P11 in at least 4 of 5 valid reps.
- **I5** ("The files rule has no precision fixture…"): when gate F's precision counts are reported for both arms, whatever the verdict.
- **I6** ("The files rule must take its reference case…"): when C1 has landed with its C2 test and gate F's readme clause is met.
- **I1** and **I2**: they stay open with a `→ progress <date> (plan 102)` note. The note says that Part B and its tests have landed, and that E3's fresh `/cc-guide files` pass, run in its own session, closes both.
- The three next-kit items get no note (D1).

An item whose gate failed stays open with a `→ progress` note giving the counts. The completion report names E3's pass, and finishing writes its handoff brief (prepare-handoff). The spec retires with the plan, since no other live plan implements it.
