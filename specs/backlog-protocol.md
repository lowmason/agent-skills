# Backlog protocol: deferrals that stay found, and a backlog that can shrink

> For agentic workers: REQUIRED NEXT SKILL: writing-plans. Plan this spec in a fresh session.
> Do not build from this file directly.

**Status: APPROVED (owner, 2026-10-29), as committed in 2869c93.** Designed with the owner on
2026-10-29 through the brainstorming skill, after a `/deferred` Design pick. Execution no
longer waits: the reviewer-contract plan (plan 73) completed and merged on 2026-10-30 as
lowmason/agent-skills#128. Plan: `specs/plans/74-backlog-protocol.md`.

## Intent

This spec settles one backlog item: "Write the backlog-protocol spec: deferrals outside this
file get lost, and the file only grows". The item is in `specs/deferred_items.md`, section
`audit-3-10-26 routing (no plan; re-verification pass, …) — 2026-10-18`. It carries two audit
findings from `specs/completed/audit-3-10-26.md`:

- **B1, lost deferrals.** A "deferred to …" sentence in a spec, plan or findings document never
  reaches a backlog item. The same is true of a follow-up named only in a closure note. A
  re-filed finding starts again at age 0. The audit counted seven such losses.
- **B6, the file only grows.** The `## Aged-backlog acknowledgements` log only grows, and it
  has 31 bullets today. A Hold under `/deferred` leaves no trace. Nothing archives fully
  ticked sections. `deferred_stats.py` assumes no item is ever deleted, so archived and
  removed items fall out of its ever-closed count.

**Why it matters.** The backlog is the repo's memory of work that was chosen not to be done
now. A loss is silent: nobody sees the item again. A file that only grows costs context on
every triage and on every ticking pass. The aged-tail gate (finishing-a-development-branch's
Step 1b) also blocks merges on items that nobody can act on.

**Numbers on 2026-10-29** (`uv run skills/writing-plans/scripts/deferred_stats.py`):
- 130 open and 336 ever closed, a closure rate of 72%. No items are aged past 45 days.
- The file has 6,907 lines and 80 sections.
- 27 sections are fully ticked. They hold 1,750 lines, about 25% of the file.

## Owner decisions

Each line records what the owner chose, in the owner's terms.

- **D1. Watch items do not age.** A `Revisit if:` item "should not be held to deadlines until
  the revisit if condition is met".
- **D2. Influence over speed.** The 2026-11-13 date is not a reason to rush. The owner is "less
  concerned about time than influence".
- **D3. Archiving pays less than the item suggested.** About 25% of the file today, not the
  36% that held on 2026-10-18. Most growth is now in sections that mix open and ticked
  items.
- **D4. One rule for archived and deleted items.** The 11 items deleted on 2026-10-27 and the
  6 items moved in July both drop out of the stats today. One rule covers both.
- **D5. Work that waits on the owner keeps pressing.** It keeps aging through the gate, even
  when a note records that it waits on the owner.
- **D6. A second acknowledgement forces action.** An item may be carried past the gate once.
  The next time, the owner acts on it.
- **D7. The lost-deferral check runs when a document is retired or an item is ticked,** not
  when the sentence is first written.
- **D8. Archiving runs on a rule,** not as a one-off.
- **D9. Approach 3** (see Approaches): wording, an advisory scan and a commit lint.
- **D10. After the one carry, only a state change opens the gate.** An aged item that has
  used its carry blocks a merge until `/deferred` closes it, holds it on an outside
  condition, triggers it or plans it. A new `→ planned` note pauses aging while its plan or
  spec is live. An `→ owner-only` item stays blocked until the owner does it or retires it.
  The owner accepted this as recommended.
- **D11. Archive per item, not per section.** A ticked item moves once its tick is more than
  45 days old, so mixed sections drain as their items close. The owner accepted this as
  recommended. It replaces the per-section rule that D8 first took.
- **D12. New watch items name one concrete signal.** A new `Revisit if:` names a signal that
  a triage can answer yes or no. It is only for work nobody wants until that signal. Old
  items stay as written. The owner accepted this rule as recommended.
- **D13. The committing session writes `→ planned`.** The session that commits the spec
  (brainstorming) or the plan (writing-plans) for a `/deferred` Plan or Design pick writes the
  note on the picked items. It records the earlier pick and is not a new disposition. When
  writing-plans commits the plan, it changes the note's path from the spec to the plan. The
  owner accepted this as recommended.
- **D14. The rule "an acknowledgement cites the last `/deferred` pass" is declined.** The
  one-carry limit (D6, D10) does its job more directly. The owner confirmed the decline
  ("Is fine").

## The item's candidate rules

The backlog item is done when the spec is approved or the owner records each rule as
declined. This table maps its six candidate rules to their outcomes.

| Candidate rule | Outcome | Decided by |
|---|---|---|
| A deferral sentence appends an item, or says it was dropped | Adopted, checked at retirement (section 6) | Owner: D7, D9 |
| A closure note naming follow-up work does the same | Adopted, checked at the tick and at archive time (sections 5 and 6) | Owner: D7, D9 |
| A re-filed finding cites its original source and date | Adopted, as a phrase in the item's text (section 8) | My call |
| An acknowledgement cites the last `/deferred` pass | Declined: the one-carry limit replaces it (section 3) | Owner: D14 |
| A Hold writes a dated `→ held` note that the gate respects | Adopted as modified: `→ held` for outside conditions, `→ owner-only` for work waiting on the owner, which keeps pressing | Owner: D5 |
| Archiving is codified and read by the stats, or July is a one-off | Codified, per item, and both files read by the stats | Owner: D4, D8, D11 |

## Goals

1. Every deferral in a retired document or a closure note ends as a backlog item or an
   explicit "dropped" line. The check runs at retirement and at a tick.
2. The aged-tail gate counts only items that someone can act on now.
3. An item can pass the gate on an acknowledgement once, and only once.
4. Every disposition that `/deferred` makes leaves a dated note on the item.
5. Closed history leaves the live file on a rule, and the stats still count it.

## Non-goals

- Finding deferrals in live documents before they retire (D7).
- Changing the triage dispositions (Retire, Quick fix, Plan, Design, Hold) or their routing.
- Changing the 45-day horizon or the 20-item volume line.
- Rewriting old items to add fields. The schema's rule stands: never rewrite an old item only
  to add fields, and never treat a missing field as a defect.
- Live roadmap stages (`specs/*-roadmap.md`). They stay out of scope, as today.
- **Merge conflicts on the one backlog file.** Every session appends to its tail, and 181
  commits touched it since 2026-10-01. One file per section (for example
  `specs/deferred/<section>.md`, with the stats reading a folder) would remove most
  conflicts. It changes every caller's write path, so it is a design of its own, not part of
  this one. → item: backlog-protocol-design (no plan; brainstorming, branch
  claude/backlog-protocol-design-aa6201) — 2026-10-29
- **The cost of the triage at plan completion.** Protocol step 4 runs the full read-only
  triage whenever 20 or more items are open, so every completion reads the whole backlog
  (about 36k tokens of open-item text today). Its cost grows with the backlog, not the plan.
  Narrowing it changes a protocol step that this spec does not otherwise touch. → item:
  backlog-protocol-design (no plan; brainstorming, branch
  claude/backlog-protocol-design-aa6201) — 2026-10-29

## Anti-goals

The work fails, even if it runs, in these cases:

- The gate blocks a merge on a watch item whose trigger has not fired.
- A rule depends on someone remembering to run it. The July archive move is the example: it
  was never repeated.
- The lint trips on history, so the owner learns to ignore it.
- An agent writes an acknowledgement, a "dropped" line or a Hold without the owner's word.
- `/deferred` stops being the only caller that executes a disposition.

## Approaches

The parts in the Design section below are the same in every approach. The approaches differ
in how the lost-deferral check is enforced.

| Approach | Trade-off | Outcome |
|---|---|---|
| 1. Wording only: the protocol steps tell the agent to read the document and resolve each deferral sentence | Cheapest. But it relies on an agent spotting a sentence in a long document, which is how the seven losses happened. It misses findings documents moved by hand | Not picked |
| 2. Wording plus an advisory scan script that lists candidate sentences (always exits 0) | The agent only judges each sentence. It no longer has to find them. Hand-moved findings documents stay uncovered | Not picked |
| 3. Approach 2 plus a commit lint that fails when a file newly added under the completed folders has an unmarked candidate | The only option that catches a findings document moved by hand. One more commit lint, with its tests and CI wiring. Each false positive costs one marker | **Picked (D9)** |

Why 3: the recurring failure is an agent that does not see the sentence. Approach 3 is the only
one where a miss stops the commit. The lint reads only new files in two folders, and a marker
answers it, so its reach stays narrow.

## Design

### 1. Item notes

An item's state lives in dated notes on its continuation lines. Each note starts with `→`, as
the existing `→ done` and `→ retired` notes do. New forms:

| Note | Written by | Meaning |
|---|---|---|
| `→ held <date>: <condition>` | `/deferred` step 5, on the owner's Hold | Blocked by a condition outside the owner and the agent. The gate skips the item from that date until a `→ triggered` note. |
| `→ owner-only <date>: <what the owner must do>` | `/deferred` step 5, on the owner's Hold of an owner-only item | A record only. The item keeps aging and pressing (D5). |
| `→ triggered <date>: <what happened>` | `/deferred` step 5 | The watch or held condition has fired. The item ages from this date like work. |
| `→ planned <date>: <path>` | The session that commits the spec or plan for a `/deferred` Plan or Design pick (D13); writing-plans updates the path from spec to plan | The item is in a live plan or spec. The gate skips it while `<path>` sits in `specs/` or `specs/plans/`. When the file retires to a `completed/` folder without ticking the item, the item ages from its section date again (D10). |
| `→ acknowledged <date> (<branch>): <reason>` | finishing Step 1b, on the owner's word | The one carry past the gate (D6). |
| `- [x] … → removed <date>: <why>` | whoever removes an item | The item left the backlog without being done or retired. It moves to the archive file (section 5). |

**Which notes set state (my call, from the builder check):**
- The checkbox alone decides open or closed. A `- [ ]` item with a `→ done` note is still
  open, and the stats print a warning naming it. This happened once before: a tick pass
  appended the note and left the box unticked.
- For an open item, only `→ held`, `→ triggered` and `→ planned` set the aging state. The
  latest of those wins. Every other note is ignored for aging. That includes
  `→ acknowledged`, `→ owner-only` and the existing `→ progress`, `→ decided`,
  `→ re-deferred` and `→ attempted` forms.
- Old notes that record a firing in another form (for example `→ progress 2026-10-29
  (plan 72): the trigger fired`) are not read as `→ triggered`. The next `/deferred` pass
  checks every watch item (section 4) and writes the `→ triggered` note. A disposition note
  is not "rewriting an old item to add fields".

### 2. How the stats age an item

`deferred_stats.py` today counts only column-0 checkbox lines. It must also read each item's
continuation lines, up to the next item or heading, so it can see the closure line and the
notes. Rules for an open item, applied in order; the first that matches decides:

1. **Triggered item**: its latest state note is `→ triggered`. Aged from the note's date, not
   the section's date. This holds for a watch item too.
2. **Held item**: its latest state note is `→ held`. Not aged. Counted as watching.
3. **Planned item**: its latest state note is `→ planned` and the named file is live. Not
   aged, and not counted as watching. Reported as `planned`. If the file is gone from
   `specs/` and `specs/plans/`, the item goes on to rules 4 and 5.
4. **Watch item**: it has `Revisit if:` and no `Done when:`. Not aged (D1). Counted as
   watching.
5. **Everything else**, including items with no closure line and items with an `owner-only`
   note: aged from the section date, as today.

Output changes:
- The first summary line keeps its exact shape, because finishing Step 1b reads
  `aged >45d:` off it.
- A new line reports `Watching: N (Revisit-if or held; not aged).` when N > 0.
- A new line names the aged items whose carry is used, by section and first words. Step 1b
  reads this line. A carry is used when the item has an `→ acknowledged` note dated after its
  latest `→ held`, `→ triggered` or `→ planned` note, or after its section date when it has
  none of those (D10).
- `--json` gains `watching`, `planned`, `aged_acknowledged` (a list) and `removed`.
- The script stays a reporter and always exits 0.

### 3. The acknowledgement: one carry, on the item

Finishing Step 1b changes in two ways:

- **First carry.** The owner gives a reason, as today. The agent writes the
  `→ acknowledged` note on each aged item it carries, not a bullet in a separate log. The
  `## Aged-backlog acknowledgements` section is no longer written.
- **Second time.** An aged item whose carry is used (section 2) cannot be carried again. For
  those items, Step 1b offers only `/deferred`. The merge waits until a pass changes the
  item's state: done, retired, held, triggered or planned (D10). A `→ owner-only` note is not
  a state change.

Reasons for putting the note on the item:
- The gate can see that the carry was used.
- The note leaves the live file when its item is archived, so nothing grows without bound
  (B6a).

The candidate rule "an acknowledgement cites the last `/deferred` pass" is **declined** (D14).
The one-carry limit does its job more directly.

### 4. `/deferred` changes

The triage rubric in `references/deferred-backlog.md` and the command's step 5 change in
these ways:

- **Step 3 (sort).** For each watch item and each held item, check whether its trigger has
  fired, from what the repo and the conversation show. If it has, propose `→ triggered`.
  This is where triggers get checked, because no script can tell whether "a `--skill`
  install is reported broken" has happened.
- **Step 5, Hold.** Hold writes a note. Use `→ held` when the condition is outside the owner.
  Use `→ owner-only` when only the owner can discharge it. Today a Hold makes no edit, so it
  leaves no trace (B6b).
- **Step 5, triggered.** On the owner's selection, write the `→ triggered` note.
- **Step 5, Plan and Design.** The hand-off to writing-plans or brainstorming names the
  picked items, so the session that commits the plan or spec can write `→ planned` on them
  (D13). `/deferred` itself writes the note only when that file is committed inside the
  same pass.
- **End of pass: archive.** Run the archive script (section 5) and commit its moves with
  the pass's other edits.

`/deferred` stays the only caller that executes a disposition.

### 5. Archive and removal

**The rule (D4, D8).** An item leaves the live file only by moving to
`specs/completed/deferred_items.md`. There are two cases:

- **Archive (D11).** A ticked item moves when its tick is more than 45 days old.
  - The tick's date is the date in its `→ done`, `→ retired` or `→ removed` note. 280 of the
    336 ticked items have one today. An item whose note has no date (mostly
    `→ done in plan N`) uses its section date.
  - It moves to the archive file under a copy of its section heading, unchanged, so the stats
    still date it. A heading may stand in both files while the section drains. When the last
    item leaves, the live heading and any section preamble go too.
  - The script reuses the aged-tail figure, so there is no new number to remember. The 45-day
    wait keeps a recent closure nearby while follow-ups are still likely.
  - About 80% of all items are closed today, but only 25% of the file sits in fully ticked
    sections. Per-item archiving reaches the closed items in mixed sections too.
- **Removal.** An item removed for any other reason, for example its skill was archived, gets
  `- [x] … → removed <date>: <why>`. It moves to the archive file under its own section
  heading, unchanged.

**The archive script.** A new script in `skills/writing-plans/scripts/` (name left to the
builder):
- It moves eligible items to the archive file. It appends each one under its section
  heading there, creating the heading in date order when the archive lacks it.
- **It also acts as a retirement check for closure notes (D7).** Before it moves an item, it
  runs the deferral scan (section 6) over the item's closure note. An item with an unmarked
  candidate stays in the live file, and the script lists it for the pass to resolve.
- **History is exempt from the hold-back (my call, from the builder check).** The scan reads
  only closure notes dated on or after the day this plan lands. Undated notes count as
  older. Without this cutoff, the first run would hold back much of the history: 15 of the
  17 fully ticked sections eligible today have candidate lines (51 lines, on a narrow
  pattern). It would also harvest a batch of items from history. The audit's three
  closure-note losses were re-filed in the 2026-10-18 routing pass, so the cutoff loses
  nothing known. The same reasoning gave the lint its frozen baseline. The archive file
  itself is on that baseline, since it exists today.
- It has a dry-run mode, and it exits 0.

**The stats read both files.** `deferred_stats.py` reads the live file and the archive file.
`closed` counts both. `removed` is reported on its own and counted as closed, because it left
the backlog. Archived items never count as open or aged.

### 6. The lost-deferral check

**Markers.** A deferral sentence is resolved when a marker sits in the same paragraph:
- `→ item: <section heading>`: a backlog item exists for it.
- `→ dropped: <why>`: the work will not be done.

The agent writes `→ item:` and appends the item. It writes `→ dropped:` only on the owner's
word, or when the work has already landed, with the check cited (a path, a `git log -S`).

**The scan script** (in `skills/writing-plans/scripts/`, so other repos get it with the
skill). It has two modes:

- **Advisory**: `scan <file>…` lists each candidate line with no marker in its paragraph. It
  always exits 0.
- **Lint**: it checks every file under `specs/completed/` and `specs/plans/completed/` that is
  not on a frozen baseline list. It exits 1 on any unmarked candidate.
  - The baseline lists the files present when the lint lands. It never grows, so history
    never trips the lint, and the lint needs no git base to compare against. It works the
    same in the pre-commit hook, in CI and in a fresh clone.
  - `build/run_commit_lints.sh` runs the lint. CLAUDE.md's Commands list and
    `test_commit_lints.py` follow, as for every commit lint.

**Candidates.** The phrase list is left to the builder, with these requirements:
- It catches every file-based instance in the audit's B1 table, taken from the file at the
  audit's base. Those are plan 4:19, plan 29's Task 5 (`:693`, `:710`),
  `agents-and-commands-expansion.md:233-234`, the audit_9_2_26 scorecard note (`:200`),
  audit_1_3_26:139 and the three closure notes. Each becomes a test fixture.
- Two forms are exempt:
  - the Plan Completion Protocol's own status header ("deferred items in
    specs/deferred_items.md" and "nothing deferred");
  - its `> Skipped: <why> → deferred` lines, because step 3 always appends those as items.
- The scan ignores fenced code blocks and inline code spans, so note forms and quoted
  phrases in backticks never count.
- **This spec and its plan are fixtures.** Both retire into the completed folders, off the
  baseline, and both are full of deferral words. Each must pass the lint when it retires,
  with markers only where a real deferral stands.
- **Burden check (my call).** Run the scan over the five most recently retired plans and their
  specs. If the median document has more than 3 unmarked candidates, tighten the list
  before landing. Ten markers per retirement would be the noise that teaches people to
  ignore a lint. Record the measured figure in the plan.

**When it runs (D7):**

| Moment | Where | Enforcement |
|---|---|---|
| A plan or spec retires | Plan Completion Protocol step 5, before the `git mv` | Advisory scan, then the lint at commit |
| A findings document moves to `specs/completed/` by hand | none | The lint at commit |
| An item is ticked with a closure note | Protocol step 3, `/deferred` step 5 | Wording: a closure note that names follow-up work carries a marker |
| A ticked item is archived | The archive script | The script holds the item back |

### 7. Watch items: one concrete signal (D12)

The schema in `references/deferred-backlog.md` gains two rules for **new** items. They do not
apply to old items, under the schema's rule against rewriting them.

- A `Revisit if:` names one concrete signal that a triage can answer yes or no from the repo
  or the owner: a test failing, a version shipping, a file appearing, or a named event such
  as "a `--skill` install is reported broken". A vague condition ("if it becomes a problem")
  is not deferrable, like an item with no closure condition today.
- `Revisit if:` is only for work that nobody wants until the signal. If the work is wanted,
  the item is `Done when:`, and it ages.

Reason: D1 makes watch items immune to the gate. Without this rule, `Revisit if:` becomes the
way to dodge the gate, and the trigger check at each `/deferred` pass grows without bound.
63 of the 130 open items are watch items today. The stats' watching line keeps that number
visible.

### 8. Re-filed findings (my call)

A re-filed item cites where and when it was first found: `first found in <doc>, <date>`.
The triage reads that phrase and ranks the item by its real age. The stats keep dating items
by their section. Reason: a per-item date field would split the dating rule in two for one
rare case. The schema's rule against a per-item date stays.

### 9. One-time migration (my call)

The plan's last task does these, so the change is visible at once:

1. Move the 31-bullet acknowledgement log to the archive file under
   `## Aged-backlog acknowledgements (to 2026-10-12) — 2026-10-12`.
2. Restore the 11 items deleted on 2026-10-27 (commit `3abd782`) into the archive file. Use
   their original section headings and add `→ removed 2026-10-27: skill archived
   (lowmason/agent-skills#121)`. The 3 open ones are ticked by that note.
3. Run the archive script once.
4. Re-run the stats, and record before and after in the completion report.

## Files touched

| File | Change | Budget |
|---|---|---|
| `skills/writing-plans/references/deferred-backlog.md` | Note forms, the aging rules, the one-carry gate text (moved here from finishing), triage steps 3 and 5, archive and removal, markers, re-filed citation, a new caller (the archive script) | No limit, but keep it a reference |
| `skills/writing-plans/SKILL.md`, Plan Completion Protocol steps 3 and 5 | Step 3: closure-note markers. "Never delete items" becomes "removal moves the item to the archive". Step 5: run the scan before the `git mv` and resolve each hit | **Net zero or less in the body.** The sibling plan uses the body's room (see Constraints). Put detail in the reference |
| `skills/finishing-a-development-branch/SKILL.md`, Step 1b | The note on the item, one carry, `/deferred` only for items already acknowledged | **Net zero or less.** The body is 19,970 characters against a 20,000-character window. Move the acknowledgement example and its paragraph to the reference, and keep a pointer |
| `skills/brainstorming/SKILL.md`, The Written Design | One line: when the spec comes from a `/deferred` Design pick, write `→ planned` on the picked items in the spec's commit (D13) | Body is 16,634 characters, so it has room. Rebuilt in plan 70: keep the edit to that one line |
| `skills/writing-plans/SKILL.md`, Plan Document Header or Execution Handoff | When the plan settles `/deferred` items, write or update their `→ planned` notes in the plan's commit (D13) | Counts against the same net-zero body budget as the protocol edits |
| `commands/deferred.md` | Step 5's Hold, triggered and planned notes, the archive run | Regenerate `runtimes/` |
| `install.py` `DEPENDENCIES` or `build/test_runtime_support.py` `SOFT_REFERENCES` | Only if brainstorming gains a path into `writing-plans/references/` | The dependency-drift test decides |
| `skills/writing-plans/scripts/deferred_stats.py` and its tests | Continuation lines, aging rules, two files, new output | Test first |
| New scan and archive scripts and their tests, in `skills/writing-plans/scripts/` | Sections 5 and 6 | Test first, with PEP 723 headers like `deferred_stats.py` |
| `build/` lint entry, `build/run_commit_lints.sh`, `build/test_commit_lints.py`, `.github/workflows/lints.yml` if needed, `CLAUDE.md` Commands | The lint mode | |
| `NOTICE` | Change-list lines for writing-plans, finishing-a-development-branch and brainstorming, all superpowers ports | |
| `specs/deferred_items.md`, `specs/completed/deferred_items.md` | The migration (section 9) | |

## Constraints

- **Sequence with the reviewer-contract plan.** The owner allows one agent-skills plan
  execution at a time.
  - The spec `specs/reviewer-and-planning-contract.md` (branch
    `claude/reviewer-contract-design-fe5868`, approved 2026-10-29) is planned first, and its
    plan executes first. This plan executes only after that plan completes and merges.
  - That plan edits `skills/writing-plans/SKILL.md`: the plan-writing sections, a new Review
    Focus section, and the "Review Minor" deferred-item example. It edits
    `references/deferred-backlog.md` for the same example. It may also move text into a new
    `references/step-recipe.md` to fit the compaction window.
  - So the planner for this spec re-reads both files after that merge, measures the
    writing-plans body again, and leaves the relabelled example alone.
  - The sibling spec does not name finishing-a-development-branch. The planner still
    measures that body again before planning, because it has only 30 characters of room.
- **Micro-tests.** writing-plans, finishing-a-development-branch and brainstorming are
  discipline skills. Every wording change is micro-tested with a no-guidance control, under
  the writing-skills
  skill. Cases:
  - **R1, retirement.** A fixture plan holds an unmarked "deferred to a future plan" sentence
    and one deferral inside a task's prose. The scan output is pasted into the prompt. Pass:
    the agent appends an item and an `→ item:` marker for each, or asks the owner. It never
    writes `→ dropped:` unasked.
  - **R2, closure note.** A ticking pass whose closure note names follow-up work. Pass: an
    item plus a marker, or a question to the owner.
  - **R1 and R2 also check D12.** One deferral in each fixture is work the owner wants, and
    one waits on a named signal. Pass: the wanted work gets `Done when:`, and the watch item's
    `Revisit if:` names one concrete signal.
  - **R3, gate.** The stats output shows two aged items, one already acknowledged. Pass: the
    agent offers an acknowledgement only for the other one. It offers `/deferred` for the
    acknowledged one, and it writes nothing without the owner's word.
  - **R4, triage.** A watch item whose trigger has fired, with the evidence in the fixture.
    Pass: the triage proposes `→ triggered`.
  - **R5, planned note.** A brainstorming session whose request names a `/deferred` Design
    pick reaches the spec's commit. Pass: the commit writes `→ planned` on the picked item,
    and on no other item.
  - Arms: the new wording against the current wording, 5 runs each. A stop at $40 for the
    whole kit (my call, the same figure as the sibling spec).
- **Isolated micro-test kits.** Use `claude -p --tools "" --setting-sources ""` with
  `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, and pilot an isolation probe before the runs. Earlier
  kits leaked user-level context.
- **`/deferred` stays the only caller that executes a disposition.** The archive script runs
  only from `/deferred` after the one-time migration.
- **No new ceremony** beyond what an open decision needs (the owner's proportional-process
  preference).
- **Repo rules.** The repo's `CLAUDE.md` governs:
  - `specs/` conventions, and the plan id from `entry_check.py`;
  - the conformance register (`check_conformance.py`) for the skill, command and script
    edits;
  - the runtime adapters, after `commands/deferred.md` changes;
  - the dependency-drift test, if a skill or command gains a path into another skill;
  - the commit lints.
- **Codex review** is pre-approved for this repo.

## Timing

The aged-tail gate re-arms on **2026-11-13**. On that date three items reach 45 days:
- the `install-py-rework` handoff item;
- the two `readonly-guard-leading-token-bypasses` items.

All three are `Revisit if:` watch items. Under this spec they do not age.

**Nothing must land before 2026-11-13 (D2).** Until this plan merges, those items take a
`/deferred` pass or an acknowledgement under today's rules. More sections age in on
2026-11-18 (`34-calibration-check-verdicts`) and 2026-11-19 (`35-…` and `37-…`). The same
holds for them.

## Done when

- `deferred_stats.py` passes its new tests:
  - continuation lines are read;
  - watch, held and triggered items age as section 2 says;
  - both files are read;
  - the summary's first line is unchanged.
- The scan catches every B1 fixture. The lint passes on the repo as it stands and fails on a
  new completed file with an unmarked candidate.
- The archive script's tests cover:
  - eligible and ineligible items, including an undated tick that falls back to its section
    date;
  - a section heading present in both files;
  - a live heading removed when its last item leaves;
  - the scan hold-back and the history cutoff;
  - dry run, and date order in the archive file.
- R1 to R5 pass on the new wording and show a difference from the control, or the plan
  records why a case could not discriminate.
- The migration is done, and the stats before and after are in the completion report.
- All commit lints pass.
- The backlog item is ticked by the plan's completion protocol.

## Left to the builder

- The scan's phrase list, within section 6's requirements.
- The script names, and whether the lint entry lives in `build/` or calls the skill script.
- How a marker is matched to its candidate inside a paragraph, tested on the fixtures.
- The final wording of each changed passage, as fixed by the micro-tests.
- Task order, provided that the RED baselines run before any wording change.

## My calls (for the owner to check)

- The `→ owner-only` note form beside `→ held` (section 1).
- A triggered item ages from its note's date, not its section's date (section 2).
- An item with both `Done when:` and `Revisit if:` counts as work, not watch (section 2).
- A removed item counts as closed in the closure rate (section 5).
- The frozen baseline for the lint (section 6), and the burden check's figure of 3.
- Which notes set state, and the checkbox's precedence (section 1).
- History is exempt from the archive hold-back (section 5).
- Two non-goals with reasons: merge conflicts on the one file, and the triage cost at plan
  completion.
- Re-filed findings cite a phrase, not a date field (section 8).
- The one-time migration, including restoring the 11 deleted items (section 9).
- The $40 micro-test stop.

## Proposed backlog items

This spec defers two pieces of work in its Non-goals: one file per section, and a narrower
triage at plan completion. Under its own rule, each needs a backlog item or a "dropped"
line. The owner said yes on 2026-10-29, and both items are in `specs/deferred_items.md`,
section `backlog-protocol-design … — 2026-10-29`, with `Size: design` and a `Done when:`.
