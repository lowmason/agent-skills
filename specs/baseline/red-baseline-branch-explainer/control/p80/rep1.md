# Plan 80, the development history record (`4d69454..HEAD`)

21 commits, 46 files, +3134 / −21. Most of the line count is spec, plan and test-evidence material. The behaviour change is in about 10 files.

## What it does, in one paragraph

Each project that uses these skills gets a new append-only file, **`specs/history.md`**. When a plan retires, the plan-completion protocol appends an entry that records **what the plan built and where the build differed from its design**. The entry holds the ledger's `Ruling:` lines (which used to be lost when the executor deleted its workspace), the plan's `> Deviation:` notes, spec-level decisions, the count of deferred items, and the earlier deferred items that the plan closed. A `/deferred` pass that closes items with a quick fix also writes an entry. A new script prints a draft of each entry. The agent finishes the draft by hand and appends it. The script never writes a file.

This answers finding 22 ("spec drift is unaddressed"). Approved specs are still not edited. The history file holds the record of what changed after approval (spec D2).

## What changes in behaviour

| Where | Change |
|---|---|
| `skills/writing-plans/SKILL.md` (step 5, Retire) | New: before the `chore(specs): retire plan <id>` commit, draft the history entry, finish it, and append it in that commit. To stay under the 20,000-character compaction limit, step 3's example block of deferred items was cut. The deferred-backlog reference already has that example. |
| `skills/writing-plans/references/history.md` (new) | The file's format, the 7 entry rules, the commands, and an 8-step "Finish the draft" list: delete rulings that did not change the build, relabel the ones the gate tagged `contradicts spec`, and so on. |
| `skills/writing-plans/scripts/history_entry.py` (new, 555 lines, stdlib) | `draft <plan> [--ledger] [--spec --spec-status retired\|live] [--date]` and `deferred [--date]`. Exit 2 on bad input. `deferred` prints nothing when no item qualifies. It reuses `deferred_stats.parse_items` and `deferral_scan.blank_code`, so text in a code fence or inline code is never parsed. |
| Both executors' `references/final-review.md` | At the completion gate, each ruling that contradicts spec text is tagged `contradicts spec: <spec section>`. Two new sentences say a tagged ruling is still a decision already taken, not a question: the history entry records it in place of a spec amendment, and if you ask for a revert, the revert becomes a deferred item. |
| `commands/deferred.md`, and the generated Gemini `deferred.toml` | When the pass ticked at least one item `→ done … (/deferred quick fix)`, run `history_entry.py deferred --date <tick date>` before the archive run and commit `specs/history.md` with the pass. |
| README, NOTICE, `build/suites.toml` | README lists the new file. NOTICE records the three new files as original MIT work in an adapted skill. The suite note now names the new tests. |

## Plan 80's own artifacts

- `specs/completed/development-history-record.md`: the spec, approved and retired. Decisions D1–D7 are yours.
- `specs/plans/completed/80-development-history-record.md`: the plan, retired.
- `specs/history.md`: the **first real entry**, plan 80's own. You can read it as a sample of the output. It lists 8 rulings and 6 deviations.
- `specs/red-baseline-development-history.md` and the kit plus 25 rep JSONs: the micro-test evidence (see below).
- `specs/deferred_items.md`: one pointer fixed and **two new deferred items** (below).

## How the build differed from the spec (the rulings worth your attention)

1. **Commit order 4 → 2 → 3.** `check_conformance` fails any commit that bundles a script no skill text names. So the commit that names the script (Task 4) landed before the script (Task 2). As a result, one commit's tree refers to a script that only arrives in the next commit. Bisecting across `a7ea1d7`/`a119dc0` can hit that tree.
2. **The spec-amendment marker was widened** (final review, tagged *contradicts spec*). A decision now qualifies on the regex `\(spec amendments?\b`, not only on the literal `(spec amendment)`, because retired plans 38, 43, 44, 53, 58 and 66 use variants. **The reference was not updated to match:** rule 4 in `references/history.md` still says the `Applied in:` list "contains `(spec amendment)`". The script is broader than its documented rule. The difference is small, but it is drift inside the change that is meant to record drift.
3. **Deviation text joins wrapped `>` lines.** A deviation under a non-task heading gets `§ <heading>` as its source, and a fence inside a blockquote counts as code. These are parser fixes found against real retired plans.
4. **`--date` is passed explicitly for `/deferred`.** The default is local today, so a pass that crossed midnight would otherwise lose its entry silently.
5. **Gate wording got one extra round.** See below.

## Evidence

**Micro-tests** (`claude-opus-5-5`, 5 reps per arm):

| Case | Control | Treatment | Treatment 2 |
|---|---|---|---|
| `gate-tag` | fails 5/5 | 2/5 at `6df0a2c` | **5/5** at `fd4749b` |
| `history-filter` | fails 5/5 | **5/5** at `6df0a2c` | not run |

The first `gate-tag` treatment applied the tag every time. But 3 of 5 reps then asked you to confirm the ruling or to amend the spec. The wording round (`fd4749b`) fixed that. Two caveats are recorded honestly in the baseline file:
- A clarifying reading of pass clause 4 was written **after** the treatment replies had been seen. The file shows that it changes no bar result.
- Only the subagent-driven-development copy of the gate text was tested. The **executing-plans copy is untested**, though its sentences are the same.

The `history-filter` reference text changed after its test only in the `/deferred` command section (`--date`), which that case does not read.

**Checks I ran on HEAD:**
- `writing-plans` pytest suite: **402 passed, 4 xfailed**.
- `build/check_conformance.py`: exit 0.
- `build/sync_runtime_assets.py --check`: exit 0. The Gemini copy is in sync.
- `build/check_provenance.py`: exit 0.

## Open items it leaves (filed in `specs/deferred_items.md`, § 80-development-history-record)

1. **A revert asked for at the gate has two rules (design).** The gate text and the spec say a revert "makes it a deferred item as today". But writing-plans protocol step 1 already handles a gate answer that unblocks work at once, and the final review found no source for "as today". You kept the spec's wording for now.
2. **No source for the gate's tags after a `/clear` (quick-fix).** Finish step 2 relabels rulings "that the gate listed" with `contradicts spec`. If the context clears between the gate and step 5, nothing on disk holds the tags. Plan 80's own run wrote them into its ledger by hand.

## Things to decide before merging

- **Rule-4 wording mismatch** (point 2 above). It is a one-line fix in `references/history.md`, so you can make it now or defer it.
- **The `/clear` gap** (open item 2) is real for any long run that clears context before retiring. It is filed as quick-fix. Merge with it open only if you accept that it can drop `contradicts spec` labels until it is fixed.
- **Every future plan-retire commit and every quick-fix `/deferred` pass now includes a manual finishing step.** The draft is deliberately not auto-appended. That is the intended trade-off (spec "The script"), but it adds work to every retirement.
- History is not backfilled for plans 1–79, by design (Non-goals).
