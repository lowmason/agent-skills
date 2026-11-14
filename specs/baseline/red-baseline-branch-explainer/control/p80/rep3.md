# Plan 80: the development history record

Range: `4d69454..325330a` (21 commits, 46 files, +3,134 / −21).

## What it does

Approved specs are never edited once a plan is built. So when a build drifts from its design, through a mid-run
`Ruling:` or a `> Deviation:` note, the spec no longer describes the system. The worst case is the ledger's rulings.
They live in the executor's workspace, which is deleted when the plan finishes, so they are lost after the gate shows
them once. This branch adds one append-only file for each project, `specs/history.md`, with one short entry for each
completed plan and one for each `/deferred` pass that does quick fixes. Each entry lists only what differed from the
design, with a pointer to the source. It is finding 22 from the drift assessment. You approved the design as
`specs/completed/development-history-record.md`, with decisions D1–D7.

## The parts

**1. A script that drafts entries:** `skills/writing-plans/scripts/history_entry.py` (555 lines, stdlib, PEP 723)

- `draft <plan> [--ledger] [--spec --spec-status retired|live] [--date]` reads the retired plan's header (the Spec
  and Roadmap lines), its `> Deviation:` notes (with the task each one sits under), the `## Decisions` entries whose
  `Applied in:` part marks a spec amendment, every `Ruling:` line in the ledger, and the backlog. From the backlog it
  takes the number of items this plan deferred and the earlier items the plan closed. It prints a draft entry.
- `deferred [--date]` lists the items ticked `→ done <date> (/deferred quick fix)`. It leaves out any item that an
  earlier `## /deferred — <date>` section already lists, so two passes on one day do not repeat an item.
- **It never writes a file.** The agent finishes the draft and appends it, so a wrong draft is always read first.
  A bad input exits 2 with a one-line error.
- Text in code is skipped. That covers fenced blocks, inline code and fences inside blockquotes, so an example
  `> Deviation:` inside a code block is not counted as a real one. It reuses `blank_code`, `parse_items` and
  `NOTE_RE` from the existing scripts next to it.
- Tests: `test_history_entry.py` (661 lines) is in the existing `writing-plans` suite.

**2. The reference and the protocol step:** `skills/writing-plans/references/history.md` is new. It covers the file
format, the entry rules, the commands and an 8-step "finish the draft" list. In that list the agent deletes rulings
that did not change the build (D7) and relabels the rulings the gate tagged as `Ruling, contradicts spec`.
`SKILL.md` step 5 (Retire) gets a 3-line pointer: draft, finish and append the entry inside the
`chore(specs): retire plan <id>` commit. To stay under the 20,000-character compaction limit, the same commit
removes step 3's example deferred-items block. I confirmed that the same example is still in
`references/deferred-backlog.md`.

**3. The gate tag:** this is in both executors' `references/final-review.md`, for subagent-driven-development and
executing-plans. At the completion gate, a ruling that contradicts spec text is listed with
`contradicts spec: <spec section>`. It is still a decision already taken, not a question: the history entry records
it instead of a spec amendment. If you ask to revert it, it becomes a deferred item.

**4. `/deferred`:** `commands/deferred.md` step 5 runs `history_entry.py deferred --date <date of the ticks>` before
the archive run, but only when the pass did a quick fix. Retire, hold, plan and design passes write no entry. The
Gemini runtime copy was regenerated from this file.

**5. Bookkeeping:**
- The README layout list gains a `specs/history.md` line.
- `NOTICE` names the three new files as your original MIT work and lists the changes to the adapted skills.
- The `build/suites.toml` note is updated.
- Plan 80 and its spec are retired to `completed/`.
- The first real entry is in `specs/history.md` (plan 80's own).
- Two new deferred items are in `specs/deferred_items.md` (below).

## How the wording was tested

`specs/red-baseline-development-history.md` holds a micro-test kit (`specs/red-baseline-development-history/kit/`)
and its results. Each rep ran `claude -p` 5 times for each arm. The bar was: the treatment passes 5/5 and the
control fails at least 1/5.

| Case | Control | Treatment | Result |
|---|---|---|---|
| `gate-tag` (the executor's gate text) | 0/5 | 2/5 at `6df0a2c`, then 5/5 at `fd4749b` | met, after one wording round |
| `history-filter` (the reference's D7 filter) | 0/5 | 5/5 at `6df0a2c` | met |

The first `gate-tag` treatment failed because 3 of 5 reps asked you to confirm the tagged ruling. The fix in
`fd4749b` added the "still a decision, ask nothing" sentences, and the copy under test then passed 5/5. The kit
spent $0.74 in total. The record also has real-data runs of `draft` on plans 79 and 74 and of `deferred` on
2026-10-05.

I checked whether the texts under test changed after their passing runs:
- `SKILL.md` and the subagent-driven-development gate paragraph did not.
- The reference's only later edit is the `/deferred` command line (`--date`), which `history-filter` does not test.
- The executing-plans copy of the gate paragraph got the same `fd4749b` wording but was never micro-tested. Plan
  80's own history entry says so.

## Rulings made during the run (already in `specs/history.md`)

The ones you might care about:

- **Commit order 4 → 2 → 3.** The orphan-bundled-file lint fails any commit while no skill text names
  `history_entry.py`. So the reference (Task 4) landed first, and for one commit it named a script that was not yet
  in the tree.
- **Spec-amendment match widened (tagged `contradicts spec`).** A decision counts when `Applied in:` matches
  `\(spec amendments?\b`, not only the exact `(spec amendment)`. Retired plans 38, 43, 44, 53, 58 and 66 use the
  longer forms.
- **`/deferred` passes `--date`.** Without it, a pass that crosses midnight would silently print nothing.
- **Deviation text** joins wrapped `>` lines. A note under a non-task heading after the tasks gets the source
  `§ <heading>` instead of the wrong task label.

## Verified on this checkout

- writing-plans suite: **402 passed, 4 xfailed**.
- `build/check_conformance.py` exit 0, `build/sync_runtime_assets.py --check` exit 0, `build/check_provenance.py`
  clean, `build/check_links.py` found 217 links and 0 broken.

## Things to know before merging

1. **Rule 4 in the reference is behind the script.** `references/history.md` rule 4 still says decisions qualify
   when `Applied in:` contains the exact `(spec amendment)`. The script accepts `(spec amendments)`,
   `(spec amendment A2)` and so on. The spec keeping the old wording is by design, because the history records the
   difference. But the reference is the text agents follow, so it should probably say "`(spec amendment` or
   `(spec amendments`" as the script's docstring does. This is a one-line fix. It is not in the deferred items.
2. **Open deferred item: a revert at the gate has two rules.** The gate paragraphs say a revert "makes it a deferred
   item". writing-plans protocol step 1 handles an answer that unblocks work at once. You kept the spec's wording
   for now. Size: design.
3. **Open deferred item: the gate tags are lost after a `/clear`.** Finish step 2 relabels rulings "that the gate
   listed" as contradicting the spec. If the context is cleared between the gate and step 5, nothing on disk holds
   those tags. Plan 80's run wrote them into its ledger by hand. The suggested fix is one fallback line: judge each
   ruling against the spec. Size: quick-fix.
4. **`draft`'s date defaults to today.** The step 5 command does not pass `--date`, so the plan heading gets the
   day the retire step runs. That is normally the completion date. This only matters if retiring is split across
   days.
5. **No backfill.** Plans retired before 80 get no entries, as the spec's non-goals say. `specs/history.md` starts
   with plan 80.
6. The branch adds about 35 small JSON rep files and the kit scripts under `specs/red-baseline-development-history/`.
   This is the same pattern as earlier red-baseline records.

Overall the branch is coherent and matches the approved spec, and its deviations are recorded. Item 1 is the only
thing I would fix before merging.
