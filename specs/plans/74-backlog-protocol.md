# Backlog Protocol Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make deferrals outside `specs/deferred_items.md` reach the backlog, and let the backlog shrink by rule, through item notes, new aging rules, a one-carry gate, a deferral scan and lint, a per-item archive script and a one-time migration.

**Architecture:** Three stdlib scripts in `skills/writing-plans/scripts/` (the extended `deferred_stats.py`, a new `deferral_scan.py`, a new `archive_deferred.py`) carry the mechanics, each test first. The lint mode of `deferral_scan.py` becomes the twelfth commit lint, reading a frozen baseline in `build/`. Wording moves into `references/deferred-backlog.md`, with net-zero edits to the writing-plans and finishing bodies, one line in brainstorming and a reworked `/deferred` step 5, all micro-tested (R1-R5) against the current wording.

**Tech Stack:** Python 3.11+ stdlib (PEP 723 scripts), pytest through `build/run_suites.py`, bash (`build/run_commit_lints.sh`), `claude -p` micro-test kit.

**Spec:** `specs/backlog-protocol.md`

## Global Constraints

- Thresholds stay: the aged tail is open items more than **45 days** old; the volume line is **20 or more** open items.
- The stats' first summary line keeps its exact shape (finishing Step 1b reads `aged >45d:` off it): `Deferred backlog: <open> open, <closed> ever closed (closure rate <n>%), aged >45d: <n>.`
- New stats lines, exact text, each printed only when its count or list is non-empty, in this order after the first line and before `Oldest open:`:
  - `  Watching: <n> (Revisit-if or held; not aged).`
  - `  Planned: <n> (in a live plan or spec; not aged).`
  - `  Aged, carry unused: <section>: <first words>…; <section>: <first words>…`
  - `  Carry used (only /deferred clears): <section>: <first words>…; <section>: <first words>…`
  - `  Removed: <n> (counted as closed).`
  - `  Warning: open item has a → done note: <section>: <first words>…` (one line per item)
  - `<first words>` is the first 6 words of the item's text after the checkbox.
- Note forms, exact: `→ held <YYYY-MM-DD>: <condition>`, `→ owner-only <YYYY-MM-DD>: <what the owner must do>`, `→ triggered <YYYY-MM-DD>: <what happened>`, `→ planned <YYYY-MM-DD>: <path>`, `→ acknowledged <YYYY-MM-DD> (<branch>): <reason>`, `- [x] … → removed <YYYY-MM-DD>: <why>`.
- Marker forms, exact: `→ item: <section heading>` and `→ dropped: <why>`.
- The checkbox alone decides open or closed. For an open item only `→ held`, `→ triggered` and `→ planned` set aging state, and the latest of those wins.
- `deferred_stats.py`, `deferral_scan.py scan` and `archive_deferred.py` always exit 0. `deferral_scan.py lint` exits 1 on any unmarked candidate.
- New scripts carry a PEP 723 header like `deferred_stats.py` (`requires-python = '>=3.11'`, `dependencies = []`), use the stdlib only, single quotes, and take `--file` and `--archive` paths, so the later one-file-per-section design can re-point them.
- The archive file is `specs/completed/deferred_items.md`. Stats `--json` gains `watching`, `planned`, `aged_carryable` (a list), `aged_acknowledged` (a list) and `removed`.
- Body budgets, measured with `build/check_conformance.py`'s `skill_body` (Task 8 gives the command): writing-plans body ≤ 20,000 characters (19,994 at the plan's base) and finishing-a-development-branch body ≤ 20,000 (19,970 at the base), both net zero or less against the base. brainstorming gains one line (16,634 at the base).
- Do not change the relabeled deferred example's words in `skills/writing-plans/SKILL.md` or `references/deferred-backlog.md` (the cosmetic rewrap below moves a line break only).
- Do not move `## What a Step Contains` (micro-tested exact copy from plan 73) out of the writing-plans body.
- Never write an acknowledgement, a `→ dropped:` line or a Hold without the owner's word. `/deferred` stays the only caller that executes a disposition. The archive script runs only from `/deferred` after the one-time migration.
- Never rewrite an old item only to add fields, and never treat a missing field as a defect.
- Micro-tests: cases R1-R5 as the spec's Constraints define them, arms new wording against current wording, 5 runs each, stop at **$40** for the whole kit. Reps run with `claude -p --tools "" --setting-sources ""` and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, after a piloted isolation probe.
- Test fixtures are literal text in the test files. Tests never call `git show` (a CI checkout is shallow). No kit or fixture file is named `test_*.py` outside a registered suite.
- After any change to `commands/deferred.md`, regenerate and check `runtimes/` (`build/sync_runtime_assets.py`). Every superpowers-port edit gets a NOTICE change-list line.
- Run `bash build/run_commit_lints.sh` before each commit. Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Shell: use `/usr/bin/grep` for sweeps, and quote any `====` in zsh.
- In this plan and in every file it adds, put note forms, marker forms and quoted deferral phrases inside backticks, so the scan reads none of them at retirement.
- This spec and this plan are fixtures of the lint (spec section 6). At retirement, the new Protocol step 5 scans both, and each passes the lint with markers only where a real deferral stands. Neither goes on the baseline.

## Review Focus

1. A note form quoted in backticks inside an item's prose (this spec's own backlog items do it) sets no state and counts as no marker. Pinned in Task 2 (`test_note_form_in_backticks_sets_no_state`) and Task 4 (`test_code_span_neither_flags_nor_marks`).
2. An item whose continuation lines hold a nested bullet keeps that bullet and its notes; the nested bullet is not a new item and is not assigned to the next item. Pinned in Task 2 (`test_nested_bullet_stays_in_its_item`).
3. Running the archive script twice moves nothing the second time and duplicates nothing in the archive. Pinned in Task 6 (`test_second_run_moves_nothing`).
4. A ticked item in a section with no usable date and no dated closure note is never archived, and the run still exits 0. Pinned in Task 6 (`test_undated_tick_in_undated_section_stays`).
5. A four-backtick fence that holds a three-backtick fence hides both from the scan, and the lint ignores non-Markdown files under the completed folders (kit `.py` files sit there). Pinned in Task 4 (`test_nested_fence_is_ignored`) and Task 5 (`test_lint_reads_markdown_only`).

## Decisions

Numbered after the spec's D1-D14.

- **D15** (owner, brief, 2026-10-30): execution no longer waits for the reviewer-contract plan. Plan 73 completed and merged as lowmason/agent-skills#128 (67758d7). Applied in: the spec's status line (this plan's commit), Global Constraints.
- **D16** (owner, brief, 2026-10-30): build on the post-plan-73 text of `skills/writing-plans/SKILL.md` and `references/deferred-backlog.md`, and re-measure the three bodies on this tree. Applied in: Global Constraints (measured figures), Tasks 7-9.
- **D17** (owner, brief, 2026-10-30): name the two overlapping backlog items, and fold each in or leave it as the plan's own call. Applied in: Overlapping backlog items.
- **D18** (owner, plan review, 2026-10-30): approve Task 0's amendment. The scan must catch the five B1 instances that carry a deferral phrase; the four phraseless fixtures become `xfail` fixtures that record the limit. Applied in: Task 0 (spec amendment), Task 4.
- **D19** (owner, plan review, 2026-10-30): approve the plan, including the planner's calls in Open for plan review items 2-7, for execution by subagent-driven-development in a fresh Sonnet session. Applied in: Open for plan review.
- **D20** (owner, completion batch, 2026-10-31): date the tick note. Protocol step 3 no longer spells the undated `→ done in plan <id>`, which skipped the archive hold-back and moved by its section date. It points at the reference, which gives the dated form `→ done <YYYY-MM-DD> (plan <id>)`. Applied in: the reference's `## Item notes` and `## Archive and removal`, protocol step 3 in `skills/writing-plans/SKILL.md`.
- **D21** (owner, completion batch, 2026-10-31): the agent writes `→ dropped:` only on the owner's word. This departs from spec section 6, which also allowed it when the work had already landed and the check was cited. Applied in: the reference's `## Markers`.
- **D22** (owner, completion batch, 2026-10-31): accept the R4 pass under the reading rule frozen before the runs (5/5; under the exact note form it scores 3/5). No wording change. Applied in: `specs/red-baseline-backlog-protocol.md`.
- **D23** (owner, completion batch, 2026-10-31): do four leftovers now: the twelfth commit lint line in `build/CLAUDE.md`, the scan negation follow-up (E3), a stats list of the aged items that can still take a carry, and the scan recall gaps. Applied in: Tasks 13 and 14 (completion additions; no task text), plus `build/CLAUDE.md`.

## Overlapping backlog items

- **Folded in:** `73-reviewer-and-planning-contract — 2026-10-30`, item `Cosmetic wraps from plan 73's task reviews`. Its line numbers are stale: the example's long line is now `skills/writing-plans/SKILL.md:332` and `skills/writing-plans/references/deferred-backlog.md:71`, and the third site is the `Order matters` line in `skills/subagent-driven-development/references/final-review.md:50`. Tasks 7 and 8 rewrap all three (whitespace only, so the body budget is unchanged). The completion protocol ticks the item.
- **Left, sequenced after this plan:** both items in `backlog-protocol-design (no plan; brainstorming, branch claude/backlog-protocol-design-aa6201) — 2026-10-29` (one file per section; narrowing the completion triage). They change the same callers and scripts. This plan keeps `--file` and `--archive` parameters so the split stays cheap.
- **Left:** `73-reviewer-and-planning-contract — 2026-10-30`, item `Declined review line: writing-plans' completion gate does not name Declined to judge lines`. It edits Plan Completion Protocol step 1 in the same body. Task 8 frees no room beyond its own needs, so that item still needs its own room.
- **Ticked at completion:** the spec's own item, `audit-3-10-26 routing … — 2026-10-18`, first words `Write the backlog-protocol spec`. No `→ planned` note is written on it now: D13 is not live until Task 8 lands, and the brief bars backlog edits before the owner's yes.

## Open for plan review

All seven items are settled: item 1 by D18, items 2-7 approved as written by D19 (2026-10-30).

1. **B1 fixtures with no deferral phrase (spec-level).** Three of the eight B1 instances carry no phrase a scan can match at the audit base `6186635`: plan 29 `:693` (a Task heading) and `:710` (a design for a `floating` tier that was then never built), the audit_9_2_26 scorecard line `:200` (a finding), and audit_1_3_26:139 (a fix list, lost through a re-file). Section 6 requires the scan to catch every B1 instance, and also caps noise at a median of 3. No phrase list can do both. **Resolved:** the owner approved Task 0's amendment (D18).
2. **writing-plans body room (my call).** The additions (the step 3 marker sentence, the removal rewording, the step 5 scan sentence, the D13 line) are paid for by three cuts inside sections the spec names: step 3's restatement of the schema (`Each item follows …` to `… resolve it now or drop it.`), which the reference already holds, shrinks to a pointer; step 5's link re-pointing sentence is shortened; and step 5's closing paragraph (`These commits land on the current branch …`) is shortened. The relabeled example and `## What a Step Contains` stay. A scratch draft of all seven edits measured 19,957 characters (base 19,994), so the budget closes with about 35 characters to spare. If the final wording passes the base figure, stop and ask the owner; do not cut elsewhere.
3. **Pass bar (my call).** A case passes when the new arm passes 4 or more of 5 reps and the control passes at least 2 fewer. When the control also passes 4 or more, the record says the case could not discriminate (a ceiling).
4. **Rep models (my call).** R1, R2 and R3 run on `claude-sonnet-5-5`, because the completion protocol and finishing run in Sonnet execution sessions. R4 and R5 run on `claude-opus-5-5`, because `/deferred` and brainstorming run in Opus sessions.
5. **Hold-back cutoff (my call).** `archive_deferred.py`'s `SCAN_FROM` is the date Task 6 is committed, written as a literal.
6. **Scan unit (my call).** A marker answers a candidate in the same unit. A unit is a run of non-blank lines, split also before each line that starts a list item (`-`, `*` or `N.` after any indent). A heading is its own unit.
7. **Baseline at merge (my call, a departure from the spec's never-grows rule).** If another session retires a file between Task 5 and this plan's merge, that file was retired before the lint existed on main. Task 11 Step 7 adds it to the baseline and says so in the PR text. The alternative is to give that file markers in this branch.

---

### Task 0: Spec amendment for the B1 fixtures (approved at plan review, D18)

**Files:**
- Modify: `specs/backlog-protocol.md` (section 6 Candidates; Done when)

- [ ] **Step 1: Replace in section 6**

Replace:
```
- It catches every file-based instance in the audit's B1 table, taken from the file at the
  audit's base. Those are plan 4:19, plan 29's Task 5 (`:693`, `:710`),
  `agents-and-commands-expansion.md:233-234`, the audit_9_2_26 scorecard note (`:200`),
  audit_1_3_26:139 and the three closure notes. Each becomes a test fixture.
```
with:
```
- It catches every file-based instance in the audit's B1 table that carries a deferral
  phrase, taken from the file at the audit's base: plan 4:19,
  `agents-and-commands-expansion.md:233-234` and the three closure notes. Each becomes a test
  fixture. Plan 29's Task 5 (`:693`, `:710`), the audit_9_2_26 scorecard note (`:200`) and
  audit_1_3_26:139 carry no deferral phrase: a design dropped without a word, a finding and a
  fix list. They become fixtures that record what a phrase scan cannot see. (owner, plan 74,
  2026-10-30)
```

- [ ] **Step 2: Replace in Done when**

Replace `- The scan catches every B1 fixture.` with `- The scan catches every B1 fixture that carries a deferral phrase. (owner, plan 74, 2026-10-30)`. Leave the status line alone.

- [ ] **Step 3: Commit**

```bash
git add specs/backlog-protocol.md
git commit -m "docs(specs): amend backlog-protocol B1 fixture scope (plan 74)"
```

### Task 1: Micro-test kit and RED baselines

**Files:**
- Create: `specs/red-baseline-backlog-protocol/kit/run_reps.sh` (copy of `specs/red-baseline-reviewer-planning-contract/kit/run_reps.sh`, temp prefix `/tmp/plan74-rep-`)
- Create: `specs/red-baseline-backlog-protocol/kit/isolation_probe.txt` (copy of plan 73's)
- Create: `specs/red-baseline-backlog-protocol/kit/cases.py`, `specs/red-baseline-backlog-protocol/kit/build_prompts.py`
- Create: `specs/red-baseline-backlog-protocol.md` (the record)
- Create: `specs/red-baseline-backlog-protocol/control/` (rep output)

**Interfaces:**
- Produces: `build_prompts.py <sha> <out-dir> [<case> …]`, which reads each case's texts at `<sha>` with `git show` and writes `<case>.txt` plus `MANIFEST.txt` (sha256, model, budget, files per prompt). Task 10 runs it again at the new wording's sha.
- Produces: the record's sections `## Reading rules`, `## Control`, `## New wording`, `## Spend`.

- [ ] **Step 1: Write `cases.py`**

One entry per case, with its texts, model, fixture, task and pass rule. Texts are SKILL.md bodies plus whole reference or command files.

| Case | Texts | Model | Fixture and task | Pass (from the spec) |
|---|---|---|---|---|
| R1 | writing-plans SKILL.md, `references/deferred-backlog.md` | `claude-sonnet-5-5` | A finished fixture plan at Protocol step 5, with one unmarked `deferred to a future plan` sentence and one deferral inside a task's prose. One is work the owner wants; one waits on a named signal. The scan output, in Task 4's `scan` format (`<file>:<line>: <line text>`), is pasted in. Task: carry out step 5. | Each deferral gets an appended item and an `→ item:` marker, or a question to the owner. No `→ dropped:` unasked. The wanted work gets `Done when:`; the watch item's `Revisit if:` names one concrete signal. |
| R2 | same as R1 | `claude-sonnet-5-5` | A Protocol step 3 ticking pass whose closure note names follow-up work, with one wanted and one signal-bound follow-up. | An item plus a marker, or a question to the owner. D12 as in R1. |
| R3 | finishing SKILL.md, `references/deferred-backlog.md` | `claude-sonnet-5-5` | Step 1b with stats output showing `aged >45d: 2` and a `Carry used (only /deferred clears):` line naming one of the two. The partner picked Option 2. | Offers an acknowledgement only for the other item, offers `/deferred` for the carried one, writes nothing without the owner's word. |
| R4 | `commands/deferred.md`, `references/deferred-backlog.md` | `claude-opus-5-5` | A backlog of 6 items, one a watch item whose signal has fired, with the evidence in the fixture (a quoted test failure or log line). Task: run steps 1-4. | The triage proposes `→ triggered` for that item. |
| R5 | brainstorming SKILL.md | `claude-opus-5-5` | A brainstorming session whose request names a `/deferred` Design pick of one item, at the point of committing the approved spec; the fixture backlog holds that item and two others. Task: list the files and edits in the spec's commit. | The commit writes `→ planned` on the picked item and on no other. |

Write each fixture in a domain unrelated to this repo's backlog (no item text from `specs/deferred_items.md`, no word of the pass rule).

- [ ] **Step 2: Write `build_prompts.py`**

Adapt plan 73's `build_prompts.py`: texts read with `git show <sha>:<path>`, never through `~/.claude`; frontmatter stripped from SKILL.md files.

- [ ] **Step 3: Check for answer leaks**

Build the control prompts, then grep each case's fixture and task (not the texts under test) for the words of its own answer: R1 and R2 `item:` and `dropped`; R4 `triggered`; R5 `planned`; R3 `acknowledged`. R3's pasted stats line (`Carry used (only /deferred clears): …`) is part of its input and is exempt by name.
Expected: no match. The pass-rule strings in `cases.py` are never written into a prompt.

- [ ] **Step 4: Pilot the isolation probe**

Run: `bash specs/red-baseline-backlog-protocol/kit/run_reps.sh specs/red-baseline-backlog-protocol/kit/isolation_probe.txt /tmp/plan74-probe 1 1 claude-sonnet-5-5`
Expected: the reply shows no output style, no `~/.claude/CLAUDE.md` text, no rules and no memory, judged as plan 73's record judges it (`specs/red-baseline-reviewer-planning-contract.md`).

- [ ] **Step 5: Register the reading rules**

Write each case's pass rule and void rules into the record's `## Reading rules` before any rep runs. Commit.

- [ ] **Step 6: Run the control arm**

Run `build_prompts.py <base-sha> /tmp/plan74-control` with `<base-sha>` = `git rev-parse HEAD` at this task's start (the current wording), then 5 reps per case into `specs/red-baseline-backlog-protocol/control/<case>/`. Expected: 25 rep files. Record each verdict and the spend. Stop if the spend reaches $20, so the new arm has the other half of the $40.

- [ ] **Step 7: Commit**

```bash
git add specs/red-baseline-backlog-protocol specs/red-baseline-backlog-protocol.md
git commit -m "test(specs): backlog-protocol RED baselines R1-R5 (plan 74)"
```

### Task 2: Stats read items, notes and aging rules

**Files:**
- Modify: `skills/writing-plans/scripts/deferred_stats.py`
- Test: `skills/writing-plans/scripts/test_deferred_stats.py`

**Interfaces:**
- Produces: `@dataclass Note(kind: str, date: dt.date | None, rest: str)`; `@dataclass Item(section: str, section_date: dt.date | None, checked: bool, text: str, notes: list[Note])`; `parse_items(text: str) -> list[Item]`; `aging_state(item: Item, is_live: Callable[[str], bool]) -> tuple[str, dt.date | None]`, which returns one of `'triggered' | 'held' | 'planned' | 'watch' | 'work'` and the date the item ages from (`None` when not aged); `compute_stats(items: list[Item], today: dt.date, aged_days: int = 45, is_live: Callable[[str], bool] = …) -> dict`.
- `parse_sections` goes. Only `deferred_stats.py` and `test_deferred_stats.py` use it (`git grep parse_sections` outside `specs/plans/completed/`). The three tests that read its section dicts assert the same counts and dates from `parse_items`; the other existing tests switch to `compute_stats(parse_items(...), ...)` and keep their assertions.

- [ ] **Step 1: Write the failing tests**

Each test builds a small backlog string. Assertions:
- `test_continuation_notes_belong_to_their_item`: two items, the first with `      → held 2026-10-01: vendor fix` on a continuation line. `parse_items` gives the first item one `held` note dated 2026-10-01, the second none.
- `test_nested_bullet_stays_in_its_item`: an item with an indented `  - sub point → held 2026-10-01: x` line, then a second item. Two items; the first holds the nested line's note.
- `test_note_form_in_backticks_sets_no_state`: an open work item whose text quotes `` `→ held <date>: <condition>` `` and `` `→ triggered 2026-01-01: x` ``. Its state is `work`, aged from the section date.
- `test_open_item_with_done_note_stays_open_and_warns`: `- [ ] x → done 2026-10-01 (plan 9)`. `open == 1`, and `format_report` holds `  Warning: open item has a → done note: <section>: x…`.
- `test_triggered_item_ages_from_note_date`: a `Revisit if:` item in a section dated 2026-06-01 with `→ triggered 2026-10-01: it broke`; today 2026-12-01. It is aged (61 days), `oldest_open_days == 61`.
- `test_held_item_is_not_aged_and_counts_as_watching`: a work item in a section 90 days old with `→ held 2026-09-01: upstream`. `aged_open == 0`, `watching == 1`.
- `test_latest_state_note_wins`: `→ held 2026-09-01: x` then `→ triggered 2026-10-01: y`. State `triggered`.
- `test_planned_item_with_live_file_is_not_aged_or_watching`: `→ planned 2026-10-01: specs/plans/9-x.md` with `is_live` returning True. `aged_open == 0`, `watching == 0`, `planned == 1`.
- `test_planned_item_whose_file_retired_ages_from_section_date`: same, `is_live` False, section 90 days old. `aged_open == 1`.
- `test_watch_item_is_not_aged`: `Revisit if:` and no `Done when:`, section 90 days old. `aged_open == 0`, `watching == 1`.
- `test_item_with_both_closure_lines_ages_as_work`: both lines, section 90 days old. `aged_open == 1`.
- `test_owner_only_note_does_not_stop_aging`: `→ owner-only 2026-09-01: run it` on a work item in a section 90 days old. `aged_open == 1`.
- `test_first_summary_line_shape_unchanged`: the first line of `format_report` matches `^Deferred backlog: \d+ open, \d+ ever closed \(closure rate (\d+%|n/a)\), aged >\d+d: \d+\.$`.
- `test_watching_and_planned_lines`: `format_report` holds `  Watching: 2 (Revisit-if or held; not aged).` and `  Planned: 1 (in a live plan or spec; not aged).` in that order, after the first line and before `  Oldest open:`.

Watch, held and planned items count as open and are left out of `aged_open`, `age_histogram` and `oldest_open_*`.

- [ ] **Step 2: Run the tests and see them fail**

Run: `uv run python build/run_suites.py writing-plans`
Expected: the new tests FAIL (`ImportError` for `parse_items` collects the whole module as an error first). Read each failure.

- [ ] **Step 3: Implement the parsing and aging rules**

A note is `→` followed by a lowercase word (letters and hyphens) and an optional ISO date, matched only outside inline code spans. `→ planned`'s path is the first `.md` token after its colon. The default `is_live(path)` is true when `Path(path)` exists and no path part is `completed`. Rules apply in the spec's section 2 order.

- [ ] **Step 4: Run the tests and see them pass**

Run: `uv run python build/run_suites.py writing-plans`
Expected: PASS, all tests.

- [ ] **Step 5: Check the live backlog**

Run: `uv run skills/writing-plans/scripts/deferred_stats.py`
Expected: exit 0, the first line in the unchanged shape, a `Watching:` line near 63 (the spec's count of watch items on 2026-10-29), and no traceback.

- [ ] **Step 6: Commit**

```bash
git add skills/writing-plans/scripts/deferred_stats.py skills/writing-plans/scripts/test_deferred_stats.py
git commit -m "feat(writing-plans): stats read item notes and age watch, held and planned items apart"
```

### Task 3: Stats read the archive, count removals and name used carries

**Files:**
- Modify: `skills/writing-plans/scripts/deferred_stats.py`
- Test: `skills/writing-plans/scripts/test_deferred_stats.py`

**Interfaces:**
- Consumes: Task 2's `parse_items`, `aging_state`, `compute_stats`.
- Produces: `compute_stats(items, today, aged_days=45, is_live=…, archived: list[Item] = ())`; `carry_used(item: Item) -> bool`; CLI flag `--archive` (default `specs/completed/deferred_items.md`); JSON keys `watching: int`, `planned: int`, `aged_acknowledged: list[{'section': str, 'first_words': str}]`, `removed: int`.

- [ ] **Step 1: Write the failing tests**

- `test_archived_items_count_as_closed_never_open`: a live file with 1 open item and an archive with 2 ticked items. `open == 1`, `closed == 2`, `aged_open` ignores the archive.
- `test_removed_items_count_as_closed_and_are_reported`: one `- [x] y → removed 2026-10-27: skill archived` in the archive. `removed == 1`, it is in `closed`, and `format_report` holds `  Removed: 1 (counted as closed).`
- `test_missing_archive_file_is_fine`: `main(['--file', live, '--archive', missing])` returns 0 and prints the summary.
- `test_carry_used_after_latest_state_note`: an aged work item with `→ acknowledged 2026-10-20 (feat/x): reason` and no state note. `carry_used` True; `aged_acknowledged == [{'section': …, 'first_words': …}]`.
- `test_acknowledgement_before_triggered_note_is_not_a_used_carry`: `→ acknowledged 2026-09-01 (b): r` then `→ triggered 2026-10-01: z`, aged. `carry_used` False.
- `test_carry_line_names_section_and_first_words`: two aged items with used carries. `format_report` holds `  Carry used (only /deferred clears): s1: alpha beta gamma delta epsilon zeta…; s2: …`.
- `test_json_output_carries_the_new_keys`: `--json` output has `watching`, `planned`, `aged_acknowledged` and `removed`, plus every existing key.

- [ ] **Step 2: Run the tests and see them fail**

Run: `uv run python build/run_suites.py writing-plans`
Expected: the seven new tests FAIL, each on the missing key, line or flag.

- [ ] **Step 3: Implement**

A carry is used when the item has an `→ acknowledged` note dated after its latest `held`, `triggered` or `planned` note, or after its section date when it has none (spec D10). Update the module docstring and the `compute_stats` docstring, whose line about items never being deleted no longer holds.

- [ ] **Step 4: Run the tests and see them pass**

Run: `uv run python build/run_suites.py writing-plans`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/writing-plans/scripts/deferred_stats.py skills/writing-plans/scripts/test_deferred_stats.py
git commit -m "feat(writing-plans): stats read the archive file, count removals and name used carries"
```

### Task 4: Deferral scan, advisory mode

**Files:**
- Create: `skills/writing-plans/scripts/deferral_scan.py`
- Create: `skills/writing-plans/scripts/test_deferral_scan.py`
- Modify: `skills/writing-plans/references/deferred-backlog.md` (one command block naming the script, so the orphan-bundled-file check passes; Task 7 writes the prose around it)
- Modify: `build/suites.toml` (the `writing-plans` suite's notes name the scan)

**Interfaces:**
- Produces: `@dataclass Candidate(line: int, text: str)`; `unmarked(text: str) -> list[Candidate]` (1-based line numbers into `text`); `main(argv) -> int` with subcommand `scan <file>…`, printing `<file>:<line>: <stripped line>` per unmarked candidate and always returning 0. Task 6 imports `unmarked`.

- [ ] **Step 1: Write the B1 fixtures as literal strings**

In `test_deferral_scan.py`, copy each fixture's whole unit from the audit base `6186635` (`git show 6186635:<path>`), as a module-level string with a comment naming its source:
- `PLAN_4` (`specs/plans/completed/4-audit_1_3_26.md:19`);
- `FIX_ISSUE` (`specs/completed/agents-and-commands-expansion.md:233-234`);
- `TASK_BRIEF_NOTE`, `SBC_RANK_NOTE`, `SESS8_NOTE` (`specs/deferred_items.md:999`, `:857`, `:382`, each the closure note from its `→` line to its item's end);
- `PLAN_29_HEADING`, `PLAN_29_FLOATING` (`specs/plans/completed/29-snippet-execution-gate.md:693`, `:710`), `SCORECARD_200` (`specs/completed/audit_9_2_26.md:200`), `AUDIT_1_3_139` (`specs/completed/audit_1_3_26.md:139`).

- [ ] **Step 2: Write the failing tests**

- `test_catches_each_phrase_bearing_b1_fixture`: parametrized over the first five strings; `unmarked(s)` is non-empty.
- `test_phraseless_b1_fixtures_record_the_limit`: parametrized over the last four, each marked `pytest.mark.xfail(strict=False, reason='no deferral phrase; see plan 74 Task 0')`; assert `unmarked(s)` is non-empty. A phrase list that catches one shows as XPASS, never as a failure.
- `test_item_marker_resolves_its_unit`: `PLAN_4 + ' → item: 9-x — 2026-01-01'` gives `[]`.
- `test_dropped_marker_resolves_its_unit`: the same with `→ dropped: landed in abc123`.
- `test_marker_in_another_unit_does_not_count`: a candidate bullet followed by a second bullet that carries the marker. One candidate.
- `test_protocol_status_header_is_exempt`: `**Status: COMPLETE (2026-01-01)** — executed via x; deferred items in specs/deferred_items.md` and the `nothing deferred` form give `[]`.
- `test_skipped_line_is_exempt`: `> Skipped: needs a DSN → deferred` gives `[]`.
- `test_code_span_neither_flags_nor_marks`: `` `deferred to a future plan` `` alone gives `[]`; `PLAN_4` plus `` `→ item: x` `` (marker in backticks) gives one candidate.
- `test_fenced_block_is_ignored`: `PLAN_4` inside a three-backtick fence gives `[]`.
- `test_nested_fence_is_ignored`: a four-backtick fence holding a three-backtick fence and `PLAN_4` gives `[]`, and a `PLAN_4` line after the outer fence closes is flagged.
- `test_scan_cli_prints_path_line_text_and_exits_0`: `main(['scan', str(f)])` returns 0 and prints `f'{f}:1: …'`.

- [ ] **Step 3: Run the tests and see them fail**

Run: `uv run python build/run_suites.py writing-plans`
Expected: `ModuleNotFoundError: deferral_scan` collects as an error.

- [ ] **Step 4: Implement `deferral_scan.py`**

The phrase list is the builder's (spec section 6), case-insensitive, as one module constant `PHRASES`. Units as in Open for plan review item 6. A fence closes only on a run of the same character at least as long as its opener. Copy the module docstring style of `deferred_stats.py`.

- [ ] **Step 5: Run the tests and see them pass**

Run: `uv run python build/run_suites.py writing-plans`
Expected: PASS.

- [ ] **Step 6: Burden check**

Run the scan over plans 69-73 in `specs/plans/completed/` and over the spec each names on its `**Spec:**` line (in `specs/completed/`). Count unmarked candidates per document.
Expected: median ≤ 3. If above 3, tighten `PHRASES` and re-run Steps 5 and 6. Record the per-document counts and the median in this plan, under this step, as a `> Measured:` line.

> Measured: 2026-10-30, 7 documents: plan 69 2, plan 70 2, plan 71 0, plan 72 0, plan 73 0, `specs/completed/brainstorming-proportional-rebuild.md` 0, `specs/completed/reviewer-and-planning-contract.md` 0. Median 0. Plans 69, 71 and 72 name no spec. Plan 73's `**Spec:**` line names `specs/reviewer-and-planning-contract.md`, which now sits in `specs/completed/`.

- [ ] **Step 7: Name the script in the reference and the suite notes**

Add under `## Backlog stats` in `references/deferred-backlog.md`:
```bash
uv run <this-skill-dir>/scripts/deferral_scan.py scan <file>…
```
Add `deferral scan` to the `writing-plans` suite's notes in `build/suites.toml`.

- [ ] **Step 8: Commit**

```bash
git add skills/writing-plans/scripts/deferral_scan.py skills/writing-plans/scripts/test_deferral_scan.py skills/writing-plans/references/deferred-backlog.md build/suites.toml specs/plans/74-backlog-protocol.md
git commit -m "feat(writing-plans): advisory deferral scan with B1 fixtures"
```

### Task 5: Deferral lint and its commit-lint wiring

**Files:**
- Modify: `skills/writing-plans/scripts/deferral_scan.py`, `skills/writing-plans/scripts/test_deferral_scan.py`
- Create: `build/deferral_baseline.txt`
- Modify: `build/run_commit_lints.sh`, `build/test_commit_lints.py`, `CLAUDE.md` (Commands)
- Check: `.github/workflows/lints.yml` (expected unchanged: it runs the runner)

**Interfaces:**
- Consumes: Task 4's `unmarked`.
- Produces: subcommand `lint --baseline <file> [--root <dir>]`. It reads every `*.md` under `<root>/specs/completed/` and `<root>/specs/plans/completed/` (recursive) whose repo-relative path is not a line of the baseline. It prints `scan`'s lines, then either `deferral lint: <n> unmarked candidate(s) in <m> file(s); add a → item: or → dropped: marker in each one's paragraph` (exit 1) or `deferral lint: clean` (exit 0).

- [ ] **Step 1: Write the failing tests**

- `test_lint_passes_when_every_file_is_on_the_baseline`: a tmp root with one flagged file listed in the baseline; exit 0, `deferral lint: clean`.
- `test_lint_fails_on_a_new_unmarked_file`: the same file not listed; exit 1, the summary line names 1 candidate in 1 file.
- `test_lint_passes_a_new_marked_file`: a new file whose candidate has `→ item: x`; exit 0.
- `test_lint_reads_markdown_only`: a flagged `kit/run.py` under `specs/completed/`; exit 0.
- `test_lint_reads_both_completed_folders`: a flagged new file under `specs/plans/completed/`; exit 1.

- [ ] **Step 2: Run them and see them fail**

Run: `uv run python build/run_suites.py writing-plans`
Expected: the five new tests FAIL (`lint` is an invalid choice).

- [ ] **Step 3: Implement `lint`**

- [ ] **Step 4: Run them and see them pass**

Run: `uv run python build/run_suites.py writing-plans`
Expected: PASS.

- [ ] **Step 5: Freeze the baseline**

Run: `git ls-files 'specs/completed/*.md' 'specs/plans/completed/*.md' | sort > build/deferral_baseline.txt`
Then: `uv run skills/writing-plans/scripts/deferral_scan.py lint --baseline build/deferral_baseline.txt`
Expected: `deferral lint: clean`, exit 0. The baseline holds `specs/completed/deferred_items.md`.

- [ ] **Step 6: Wire the lint**

In `build/run_commit_lints.sh`, after `reviewer_block`:
```bash
run deferral_lint uv run skills/writing-plans/scripts/deferral_scan.py lint --baseline build/deferral_baseline.txt
```
In `CLAUDE.md` § Commands: add the deferral lint to the comment that lists the commit lints, and add a command block:
```bash
# Deferral lint: a file newly added under specs/completed/ or specs/plans/completed/ (not on the frozen
# build/deferral_baseline.txt) fails on a deferral sentence with no → item: or → dropped: marker in its paragraph
uv run skills/writing-plans/scripts/deferral_scan.py lint --baseline build/deferral_baseline.txt
```
Add `test_unmarked_deferral_is_refused(clone)` to `build/test_commit_lints.py`, in the style of `test_drifted_reviewer_block_is_refused`: write `specs/completed/x.md` holding `PLAN_4`'s text, commit, expect the hook to refuse with `deferral_lint` named.

- [ ] **Step 7: Run the lints, then commit**

Run: `bash build/run_commit_lints.sh`
Expected: `commit lints passed`.

```bash
git add skills/writing-plans/scripts/deferral_scan.py skills/writing-plans/scripts/test_deferral_scan.py build/deferral_baseline.txt build/run_commit_lints.sh build/test_commit_lints.py CLAUDE.md
git commit -m "feat(build): deferral lint over newly completed specs and plans"
```

- [ ] **Step 8: Run the clone tests after the commit**

`test_commit_lints.py` clones HEAD, so it sees the lint only now.
Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_commit_lints.py`
Expected: PASS, including `test_unmarked_deferral_is_refused`.

### Task 6: Archive script

**Files:**
- Create: `skills/writing-plans/scripts/archive_deferred.py`
- Create: `skills/writing-plans/scripts/test_archive_deferred.py`
- Modify: `skills/writing-plans/references/deferred-backlog.md` (one command block naming the script)

**Interfaces:**
- Consumes: Task 2's `parse_items`/`Item`/`Note` (import from `deferred_stats`), Task 4's `unmarked`.
- Produces: `SCAN_FROM: dt.date` (the date this task is committed, as a literal); `archive(live: str, archived: str, today: dt.date, scan_from: dt.date = SCAN_FROM, days: int = 45) -> tuple[str, str, list[str]]`, returning the new live text, the new archive text and the held-back report lines; CLI `--file`, `--archive`, `--dry-run`, printing `archived <n> item(s), held back <k>:` and then one `  held back: <section>: <first words>…: <candidate line>` per held item; always exit 0.

- [ ] **Step 1: Write the failing tests**

Fixed `today = dt.date(2026, 12, 31)`, `scan_from = dt.date(2026, 11, 1)`.
- `test_tick_older_than_45_days_moves`: `- [x] a → done 2026-10-01 (plan 9)`. It leaves the live text and sits under the same heading in the archive.
- `test_tick_45_days_old_or_newer_stays`: `→ retired 2026-11-16: …` stays.
- `test_undated_tick_falls_back_to_section_date`: `→ done in plan 9` in a section dated 2026-10-01 moves; in a section dated 2026-12-01 it stays.
- `test_undated_tick_in_undated_section_stays`: a ticked item with no dated note under `## notes`; it stays, and `main` exits 0.
- `test_open_item_never_moves`.
- `test_removed_item_moves_at_any_age`: `- [x] b → removed 2026-12-30: skill archived` moves.
- `test_heading_in_both_files_while_section_drains`: a section with one old tick and one open item. The heading stays live and is created in the archive.
- `test_live_heading_and_preamble_go_with_last_item`: a section with a preamble line and one old tick. The heading and preamble leave the live text; the next section is intact.
- `test_new_heading_lands_in_date_order`: an archive with sections dated 2026-07-01 and 2026-09-01 gains 2026-08-01 between them.
- `test_existing_archive_heading_gains_the_item_at_its_end`.
- `test_closure_note_with_unmarked_candidate_is_held_back`: `→ done 2026-11-02: … still worth a future item …` (phrase from `PHRASES`) stays live and appears in the report lines.
- `test_closure_note_before_scan_from_is_not_held_back`: the same note dated 2026-10-01 moves.
- `test_undated_closure_note_counts_as_older`: `→ done in plan 9 …` with the same phrase moves.
- `test_dry_run_writes_nothing`: `main(['--file', live, '--archive', arch, '--dry-run'])` prints the counts and leaves both files byte-identical.
- `test_second_run_moves_nothing`: running `archive` on its own output returns the same two texts.

- [ ] **Step 2: Run them and see them fail**

Run: `uv run python build/run_suites.py writing-plans`
Expected: `ModuleNotFoundError: archive_deferred` collects as an error.

- [ ] **Step 3: Implement `archive_deferred.py`**

The tick date is the date of the latest `done`, `retired` or `removed` note, or the section date when that note has none. The closure note is the item text from its first such note onward. The archive keeps its `# Deferred items` title line; undated sections sort last.

- [ ] **Step 4: Run them and see them pass**

Run: `uv run python build/run_suites.py writing-plans`
Expected: PASS.

- [ ] **Step 5: Dry-run on the live backlog**

Run: `uv run skills/writing-plans/scripts/archive_deferred.py --dry-run`
Expected: exit 0, an `archived <n> item(s)` count, and no held-back line (all history predates `SCAN_FROM`). Both files unchanged (`git status --porcelain specs/` prints nothing).

- [ ] **Step 6: Name the script in the reference, then commit**

Add under `## Backlog stats` in `references/deferred-backlog.md`:
```bash
uv run <this-skill-dir>/scripts/archive_deferred.py --dry-run
```

```bash
git add skills/writing-plans/scripts/archive_deferred.py skills/writing-plans/scripts/test_archive_deferred.py skills/writing-plans/references/deferred-backlog.md
git commit -m "feat(writing-plans): per-item archive script with a closure-note hold-back"
```

### Task 7: The deferred-backlog reference

**Files:**
- Modify: `skills/writing-plans/references/deferred-backlog.md`

**Interfaces:**
- Consumes: the output lines and flags of Tasks 2-6 (Global Constraints).
- Produces: the sections Tasks 8 and 9 point to, by these exact headings: `## Item notes`, `## Markers`, `## Archive and removal`, `## Aged-tail gate`.

- [ ] **Step 1: Callers and stats**

The `Three callers` list becomes four or more: add the archive script's caller (`/deferred`, end of pass) and the scan's (Protocol step 5, the lint). In `## Backlog stats`, add the new `--json` keys, the `--archive` file, and the meaning of the `Watching`, `Planned`, `Carry used`, `Removed` and `Warning` lines.

- [ ] **Step 2: `## Item notes`**

Add the note table of spec section 1 and the state rules (checkbox precedence, the three state notes, latest wins, old firing notes are not read as `→ triggered`), then spec section 2's five aging rules in order.

- [ ] **Step 3: Schema additions**

In `## Deferred-item schema`, after the closure-condition bullet: spec section 7's two rules for new watch items (one concrete signal, a triage can answer yes or no; `Revisit if:` only for work nobody wants until the signal), and spec section 8's re-filed phrase `first found in <doc>, <date>`. Keep the old-items rule as it is.

- [ ] **Step 4: Triage rubric**

Step 3: for each watch item and each held item, check whether its signal has fired, from what the repo and the conversation show, and propose `→ triggered` when it has. Step 5: point to `/deferred` for the note forms each disposition writes.

- [ ] **Step 5: `## Markers` and `## Archive and removal`**

Markers: the two forms, who writes each (the agent writes `→ item:` and appends the item; `→ dropped:` only on the owner's word or with the landed work cited), the scan command, and the four moments of spec section 6's table. Archive and removal: spec section 5's rule, the 45-day tick age, the removal form, the hold-back and its `SCAN_FROM` cutoff, and that the script runs only from `/deferred`. Replace any `never delete` wording with: removal and archiving move the item to `specs/completed/deferred_items.md`.

> Deviation: `→ dropped:` is written only on the owner's word (D21). The spec and this step also allowed it with the landed work cited. The owner removed that exception at completion.

- [ ] **Step 6: `## Aged-tail gate`**

Rewrite the section to spec section 3: the gate reads the stats; a first carry writes `→ acknowledged <YYYY-MM-DD> (<branch>): <reason>` on each carried item, on the owner's reason; an item named on the `Carry used` line gets only `/deferred`, and the merge waits for a state change (done, retired, held, triggered or planned; `→ owner-only` is not one). Move here, from finishing Step 1b, the question template, the acknowledgement example (rewritten as a note on an item) and the paragraph on why a reason is required. The `## Aged-backlog acknowledgements` section is no longer written.

- [ ] **Step 7: Rewrap the relabeled example**

Move the line break in the example's second item so no line passes 76 columns (`:71` today). Words unchanged.

- [ ] **Step 8: Check and commit**

Run: `uv run python build/check_links.py && uv run --with pyyaml python build/check_conformance.py && uv run python build/check_snippets.py skills/`
Expected: each exits 0.

```bash
git add skills/writing-plans/references/deferred-backlog.md
git commit -m "docs(writing-plans): backlog reference gains item notes, markers, archive and the one-carry gate"
```

### Task 8: writing-plans and brainstorming wording

**Files:**
- Modify: `skills/writing-plans/SKILL.md` (Plan Completion Protocol steps 3 and 5; one D13 line)
- Modify: `skills/brainstorming/SKILL.md` (§ The Written Design, one line)
- Modify: `skills/subagent-driven-development/references/final-review.md:50` (rewrap only)
- Modify: `NOTICE` (superpowers change list)

**Interfaces:**
- Consumes: Task 7's headings `## Markers`, `## Archive and removal`; Task 4's scan command.

- [ ] **Step 1: Measure the bodies before**

Run:
```bash
uv run --with pyyaml python -c "
import sys; sys.path.insert(0, 'build')
from check_conformance import skill_body
for f in ('skills/writing-plans/SKILL.md', 'skills/finishing-a-development-branch/SKILL.md', 'skills/brainstorming/SKILL.md'):
    print(f, len(skill_body(open(f).read())[0]))"
```
Expected: `19994`, `19970`, `16634`. A different figure means main moved: record it as a deviation and budget from it.

- [ ] **Step 2: Step 3 of the protocol**

Three edits:
- shrink the schema restatement to a pointer to the reference's schema (Open for plan review item 2);
- add: a closure note that names follow-up work carries a marker (`→ item:` or `→ dropped:`, reference `## Markers`);
- replace `Never delete items — the file doubles as a history of consciously-deferred work.` with a sentence saying an item is never deleted: removal and archiving move it to `specs/completed/deferred_items.md` (reference `## Archive and removal`).

Rewrap the example's second item as in Task 7 Step 7 (words unchanged).

> Deviation: step 3 no longer spells the tick form. The form moved to the reference's `## Item notes` with a date, `→ done <YYYY-MM-DD> (plan <id>)` (D20).

- [ ] **Step 3: Step 5 of the protocol**

Before the `git mv`, run `uv run <this-skill-dir>/scripts/deferral_scan.py scan <plan> <spec>` and resolve each line it lists with a marker (reference `## Markers`). Shorten the link re-pointing sentence, keeping its `../skills/…` to `../../skills/…` example, and shorten the closing paragraph (`These commits land on the current branch …`) to the same meaning: the commits are the branch's last, a merge or PR carries them, and a discarded branch takes them with it.

- [ ] **Step 4: The D13 line**

One sentence in the opening paragraph of `## Execution Handoff` (spec: Plan Document Header or Execution Handoff): when the plan settles `/deferred` items, its commit writes `→ planned <YYYY-MM-DD>: <plan path>` on each, replacing a spec path already there.

- [ ] **Step 5: brainstorming**

One line in `## The Written Design`, in the `**Where it goes:**` paragraph: when the spec comes from a `/deferred` Design pick, the spec's commit writes `→ planned <YYYY-MM-DD>: <spec path>` on the picked items, and on no other. No path into `writing-plans/references/` (no new install dependency).

- [ ] **Step 6: Rewrap `final-review.md:50`**

Move line breaks in the `Order matters` paragraph so no line passes 76 columns. Words unchanged.

- [ ] **Step 7: Measure the bodies after**

Run Step 1's command.
Expected: writing-plans ≤ 20000 and ≤ its Step 1 figure; finishing unchanged; brainstorming ≤ 20000.

- [ ] **Step 8: NOTICE**

In the superpowers change list's deferred-backlog paragraph (`NOTICE`, the bullet that begins `The planning/execution skills`), name the two new scripts and their tests, the item notes and the one-carry gate, and brainstorming's `→ planned` line.

- [ ] **Step 9: Check and commit**

Run: `bash build/run_commit_lints.sh`
Expected: `commit lints passed`.

```bash
git add skills/writing-plans/SKILL.md skills/brainstorming/SKILL.md skills/subagent-driven-development/references/final-review.md NOTICE
git commit -m "feat(writing-plans): completion protocol scans retiring documents and marks closure-note follow-ups"
```

### Task 9: finishing Step 1b and `/deferred`

**Files:**
- Modify: `skills/finishing-a-development-branch/SKILL.md` (Step 1b; Step 4b's acknowledgement mention; the Option 1 and Option 2 gate lines; the Red Flags acknowledgement line)
- Modify: `commands/deferred.md` (preamble; `description`; step 5)
- Regenerate: `runtimes/gemini/commands/deferred.toml`
- Modify: `NOTICE` (finishing's change-list line)

**Interfaces:**
- Consumes: Task 3's `Carry used (only /deferred clears):` line; Task 6's archive command; Task 7's `## Aged-tail gate`.

- [ ] **Step 1: Step 1b**

Keep the stats run and the two summary examples. Move the acknowledgement bullet, its example block and the `Carried deliberately` paragraph to the reference (Task 7 placed them), leaving a pointer to `## Aged-tail gate`. The question offers two choices per item: `/deferred`, or a carry noted on the item with a reason. An item on the `Carry used` line is offered `/deferred` only. Keep `Never write the acknowledgement without asking` in the body.

- [ ] **Step 2: The other finishing sites**

Step 4b (`an acknowledgement, or /deferred quick fixes`), Options 1 and 2 (`a /deferred pass or a logged acknowledgement`) and Red Flags (`Write an aged-backlog acknowledgement your partner did not ask for`) name the note on the item instead of the log.

- [ ] **Step 3: Measure finishing**

Run Task 8 Step 1's command.
Expected: finishing ≤ 19970.

- [ ] **Step 4: `/deferred`**

- Preamble: edits happen only in step 5, for selected items, in the forms step 5 names (no longer `two tick forms`).
- `description`: unchanged unless it names the tick forms (it does not today).
- Step 5, Hold: write `→ held <date>: <condition>` for a condition outside the owner, `→ owner-only <date>: <what the owner must do>` for owner-only work.
- Step 5, a new Triggered line: on the user's selection, write `→ triggered <date>: <what happened>`.
- Step 5, Retire and Quick fix: a tick note that names follow-up work carries a marker (`→ item:` or `→ dropped:`, reference `## Markers`), as Protocol step 3 says (spec section 6's table).
- Step 5, Plan and Design: the hand-off names the picked items, so the session that commits the plan or spec writes `→ planned`; `/deferred` writes it only when that file is committed in the same pass.
- A closing line: end the pass with `uv run <writing-plans-dir>/scripts/archive_deferred.py` and commit its moves with the pass's other edits. Use the path form `commands/deferred.md` already uses for the writing-plans skill.

- [ ] **Step 5: Regenerate the adapters**

Run: `uv run --with pyyaml python build/sync_runtime_assets.py && uv run --with pyyaml python build/sync_runtime_assets.py --check`
Expected: the second command exits 0.

- [ ] **Step 6: Dependency drift**

Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies`
Expected: PASS. If `/deferred` gained a path into the skill that `install.py`'s `DEPENDENCIES` lacks, add it.

- [ ] **Step 7: NOTICE, lints, commit**

Add finishing's line (the acknowledgement moved onto the item, one carry). Run `bash build/run_commit_lints.sh`; expected `commit lints passed`.

```bash
git add skills/finishing-a-development-branch/SKILL.md commands/deferred.md runtimes/ NOTICE install.py
git commit -m "feat(finishing): one carry per aged item, noted on the item; /deferred writes state notes"
```

### Task 10: GREEN runs and the record

**Files:**
- Create: `specs/red-baseline-backlog-protocol/green/`
- Modify: `specs/red-baseline-backlog-protocol.md`

- [ ] **Step 1: Build and check the new-wording prompts**

Run `build_prompts.py <new-sha> /tmp/plan74-green` with `<new-sha>` = HEAD after Task 9. Repeat Task 1 Step 3's leak grep on them.

- [ ] **Step 2: Run 5 reps per case**

Expected: 25 rep files under `green/<case>/`. Stop if the kit's total spend reaches $40.

- [ ] **Step 3: Judge and record**

Judge each rep by the registered reading rules. Record per case: control passes, new passes, the verdict under Open for plan review item 3, and the total spend.

- [ ] **Step 4: Handle a miss**

A case that misses its bar: change the wording it tests, re-run Task 8 or 9's checks, and re-run that case only, within the $40. A case that still misses goes to the owner with the record. Never ship a miss without the owner's ruling.

- [ ] **Step 5: Commit**

```bash
git add specs/red-baseline-backlog-protocol specs/red-baseline-backlog-protocol.md
git commit -m "test(specs): backlog-protocol GREEN runs R1-R5 (plan 74)"
```

### Task 11: One-time migration

**Files:**
- Modify: `specs/deferred_items.md`, `specs/completed/deferred_items.md`
- Modify: `specs/plans/74-backlog-protocol.md` (the before and after figures)

- [ ] **Step 1: Stats before**

Run: `uv run skills/writing-plans/scripts/deferred_stats.py --json > /tmp/plan74-before.json` and the text form. Record the text form under this step as a `> Before:` line.

> Before: 2026-10-30, `deferred_stats.py` text form:
> `Deferred backlog: 143 open, 344 ever closed (closure rate 71%), aged >45d: 0.`
> `  Watching: 70 (Revisit-if or held; not aged).`
> `  Oldest open: 32d (readonly-guard-leading-token-bypasses (no plan; branch claude/objective-nash-accd9c)).`
> `  Age spread — 0-14d: 57  15-30d: 15  31-45d: 1`
> `  At or above the 20-item volume threshold.`

- [ ] **Step 2: Move the acknowledgement log**

Count the bullets in `## Aged-backlog acknowledgements` and read the last bullet's date. Expected: 31 bullets, the last dated 2026-10-12. Move the section's bullets to the archive under `## Aged-backlog acknowledgements (to 2026-10-12) — 2026-10-12`, in date order. The live `## Aged-backlog acknowledgements` heading leaves too, so `# Deferred items` is followed directly by the first dated section. If the count or the last date differs, record a `> Deviation:` line and stop for the owner before renaming the heading.

- [ ] **Step 3: Restore the 11 deleted items**

Take the 11 items `git show 3abd782 -- specs/deferred_items.md` deletes, from `3abd782^`. Append each to the archive under its original section heading, adding `→ removed 2026-10-27: skill archived (lowmason/agent-skills#121)`. Tick the 3 open ones (`- [ ]` to `- [x]`) by that note.
Expected: `/usr/bin/grep -c 'removed 2026-10-27' specs/completed/deferred_items.md` prints 11.

- [ ] **Step 4: Run the archive script once**

Run: `uv run skills/writing-plans/scripts/archive_deferred.py`
Expected: exit 0, no held-back line.

- [ ] **Step 5: Stats after, and the checks**

Run the stats again. Expected: `removed` = 11; `closed` after = `closed` before + 11; `open` after = `open` before (the 3 restored open items were already out of the counts). Record the text form as a `> After:` line.
Run: `uv run skills/writing-plans/scripts/deferral_scan.py lint --baseline build/deferral_baseline.txt`
Expected: `deferral lint: clean`.

> After: 2026-10-30, `deferred_stats.py` text form:
> `Deferred backlog: 143 open, 355 ever closed (closure rate 71%), aged >45d: 0.`
> `  Watching: 70 (Revisit-if or held; not aged).`
> `  Removed: 11 (counted as closed).`
> `  Oldest open: 32d (readonly-guard-leading-token-bypasses (no plan; branch claude/objective-nash-accd9c)).`
> `  Age spread — 0-14d: 57  15-30d: 15  31-45d: 1`
> `  At or above the 20-item volume threshold.`

- [ ] **Step 6: Commit**

```bash
git add specs/deferred_items.md specs/completed/deferred_items.md specs/plans/74-backlog-protocol.md
git commit -m "chore(specs): migrate the acknowledgement log, restore removed items and archive old ticks (plan 74)"
```

- [ ] **Step 7: Before the merge, confirm the baseline**

If `origin/main` moved since Task 5, merge it, then re-run Task 5 Step 5's lint. A file another session retired in between and that the lint flags was retired before the lint existed: add its path to `build/deferral_baseline.txt` and say so in the PR text. This plan's own spec and plan never go on the baseline.
