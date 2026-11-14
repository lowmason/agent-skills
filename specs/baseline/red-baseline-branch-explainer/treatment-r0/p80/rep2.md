# claude/plan-80-execution-636c1e: plan 80, the development history record

## Synopsis

**The plan:** Plan 80 closes finding 22: a mid-run `Ruling:` that contradicts spec text never reaches the spec. Rulings
live only in the executor's ledger, which the protocol deletes. Differences from the design are spread over
deviation notes, decisions and deferred items. The plan gives each project one append-only file, `specs/history.md`,
that records where each plan's build differed from its design and what each `/deferred` quick-fix pass closed.

**The build:** A micro-test kit and its control arms came first. Then a reference, `references/history.md`, and a
one-sentence pointer in protocol step 5 of writing-plans. Then the script `history_entry.py`, with a `draft` command
for plans and a `deferred` command for `/deferred` passes. Both executors' gates now tag a ruling that contradicts
the spec. `/deferred` step 5 runs the script. Treatment arms and a real-data check closed the build. The plan's own
retirement wrote the first entry.

**The project:** Every plan retirement and every quick-fix `/deferred` pass now appends a short, sourced entry to
`specs/history.md`. Rulings that changed the build outlive the ledger. The owner sees spec-contradicting rulings
tagged at the gate. No approved spec is edited to stay current. Two deferred items remain, both about the gate's
tags.

## Background

Before the branch, the Plan Completion Protocol in `skills/writing-plans/SKILL.md` ran the gate, plan markup,
deferred items and retirement. Both executors' `references/final-review.md` gate paragraphs listed every `Ruling:`
line from the ledger (`<workspace>/progress.md`) once, then deleted the workspace. No lasting file kept those
rulings.

The spec (`specs/completed/development-history-record.md`, Motivation) adds three facts. Rulings are lost after
completion. Differences sit in `> Deviation:` notes, `## Decisions` entries and deferred-item notes, with no one
place that collects them. Most deferred closures come from `/deferred` quick fixes, not plans.

The spec's decisions frame the fix. D2 keeps the spec as the design record and puts the as-built record elsewhere.
D4 replaces your earlier trigger proposal for retired plans. D5 picks approach B: a protocol step, a reference and a
draft script. D6 adds `/deferred` entries. D7 keeps only rulings that changed the build. One constraint shaped the
edits: `SKILL.md` sat at 19,995 body characters, just under the 20,000 compaction cut.

## The change

### 1. Micro-test kit and control arms (Task 1)

`specs/red-baseline-development-history/kit/` holds `cases.py`, `build_prompts.py`, `run_reps.sh`, `show_reps.py`
and an isolation probe. Two cases test the two rules that change an agent's choices. `gate-tag` checks that the gate
tags only the contradicting ruling and asks nothing about it. `history-filter` checks that the agent drops
non-qualifying rulings and relabels the contradicting one. The bar for both is `treatment 5/5; control fails at
least 1 of 5`. Both controls failed 5 of 5 (`specs/red-baseline-development-history.md`, Control). The treatment
arms in part 6 depend on this kit. One ruling: `run_reps.sh` keeps its comment `Plan 77 deviation (a)`, because that
deviation was plan 77's.

### 2. The reference and the step 5 pointer (Task 4)

`skills/writing-plans/references/history.md` is new. It holds the file rules, the entry format, rules 1 to 7, the
`draft` and `deferred` commands, and an eight-step "Finish the draft" list. The agent deletes non-qualifying rulings,
relabels gate-tagged ones `Ruling, contradicts spec`, shortens deviation and decision lines, resolves warning lines
and appends the entry.

`skills/writing-plans/SKILL.md` gets three lines at the end of step 5: draft the entry, finish it, append it in the
`chore(specs): retire plan <id>` commit. The cut that pays for them is step 3's example block, which
`references/deferred-backlog.md` already holds. The file shows 3 lines added and 11 removed.

This part committed first (`a119dc0`), before the script. The orphan-bundled-file rule in `check_conformance` fails
any commit that adds `history_entry.py` while no skill text names it. The entry records this as a ruling and a
deviation under Task 4.

### 3. `history_entry.py draft` (Task 2)

`skills/writing-plans/scripts/history_entry.py` (555 lines) is a PEP 723 stdlib script. It imports `blank_code`
from `deferral_scan` and `parse_items`, `Item` and `NOTE_RE` from `deferred_stats`. `draft_entry` (line 388)
assembles the entry from:

- the plan header: `**Spec:**` and `Roadmap:` lines (`header_spec`, `header_roadmap`)
- `> Deviation:` notes with their task labels (`deviation_lines`)
- spec-level decisions (`decision_lines`)
- every `Ruling:` line in the ledger (`ruling_lines`)
- the count of the plan's deferred items and items ticked `→ done … (plan <id>)` (`closed_by_plan`)

It writes no file. It exits 2 on a missing plan or on `--spec` without `--spec-status`.

Several rulings changed the parse from the spec's text. A deviation's text joins its wrapped `>` lines. A note under
a non-task heading after the tasks gets `Source: plan, § <heading>`. A fence inside a blockquote counts as code
(`_blank_quoted_fences`, line 138). A decision qualifies on `SPEC_AMENDMENT_MARK_RE`, `\(spec amendments?\b`
(line 84), not only the literal `(spec amendment)`. The entry tags that last one `Ruling, contradicts spec (final
review)`, because retired plans 38, 43, 44, 53, 58 and 66 write other forms. Note that rule 4 in
`references/history.md` still names the literal `(spec amendment)`. The last fix, `7931b3c`, landed after the retire
commit. It tests that mark on code-masked text, so a mark inside inline code no longer qualifies. The history entry
does not list it.

### 4. `history_entry.py deferred` (Task 3)

`deferred_entry` (line 474) reads `specs/deferred_items.md` for items ticked `→ done <date> (/deferred quick fix)`.
It skips items that an earlier `## /deferred — <date>` section in `specs/history.md` already lists
(`_listed_lines`). It prints nothing when no item qualifies. `test_history_entry.py` (661 lines, 40 test functions)
covers both commands, and `build/suites.toml` names it in the `writing-plans` suite notes.

### 5. Gate tags and `/deferred` (Tasks 5 and 6)

Both `skills/subagent-driven-development/references/final-review.md` and
`skills/executing-plans/references/final-review.md` now tell the gate to tag each ruling that contradicts spec text
`contradicts spec: <spec section>`. That tag is the source for the relabel in Finish step 2.

`commands/deferred.md` step 5 runs `history_entry.py deferred --date <YYYY-MM-DD>` before the archive run, and
commits `specs/history.md` with the pass. The regenerated `runtimes/gemini/commands/deferred.toml` follows. The
spec gave `--date` a default of today. A final-review ruling made the command pass the ticks' date, so a pass that
crosses midnight does not lose its entry. `NOTICE` records the three new files as original work in an adapted skill.
`README.md` lists `specs/history.md` in the layout.

### 6. Treatment arms and the real-data check (Task 7)

At `6df0a2c`, `history-filter` passed 5 of 5, but `gate-tag` passed only 2 of 5: three reps asked the partner to
confirm. One wording round (`fd4749b`) added two sentences to both gate paragraphs. A tagged ruling stays a decision
that the history entry records in place of a spec amendment, so ask nothing. A revert makes it a deferred item. The
`treatment2` arm then passed 5 of 5. The real-data check ran `draft` on plans 79 and 74 and `deferred` on
2026-10-05, which printed 47 item lines. Each step met its expected values.

### 7. The first entry

The retire commit (`d5d40ff`) moves the plan and spec to `completed/` and creates `specs/history.md` with plan 80's
entry. The entry lists 8 rulings, 7 deviations and a `Deferred: 2 items` line.

## What it adds to the project

- **Plan retirement** gains a step. Protocol step 5 now drafts, finishes and appends a history entry in the retire
  commit. Both executors depend on it through the gate tag and the ledger, which must still exist at step 5.
- **The gate** now tags spec-contradicting rulings. This is the branch's answer to finding 22. The history entry
  replaces the spec amendment that the assessment proposed.
- **`/deferred`** now writes an entry for each pass that closes items with a quick fix.
- **The history file** gives later readers one place for what was built against each spec. D2 and the Non-goals
  keep approved specs unedited. Plans retired before plan 80 get no backfill.

Plan 80 adds two deferred items under `## 80-development-history-record` in `specs/deferred_items.md`:

1. A revert asked for at the gate has two rules. The spec and both gate paragraphs say it becomes a deferred item.
   But writing-plans protocol step 1 treats an answer as unblocking work at once. Size: design.
2. Finish step 2 has no source for the gate's tags after a `/clear`. No file holds the tags once the gate message
   is gone. Plan 80's run wrote them into its ledger by hand. Size: quick-fix.

## Questions

1. What gap did plan 80 set out to close, and why did it put the record in a new file rather than in the spec?
2. In what order were the kit, the reference, the script, the gate tag and `/deferred` built, and what forced the
   reference to commit before the script?
3. What now happens at plan retirement and at a quick-fix `/deferred` pass, and what does that leave open about
   the gate's tags?
