# Plan 80: the development history record (`4d69454..325330a`)

## The short version

This branch adds **`specs/history.md`**, one append-only file for each project. It records what each completed plan built and **where the build differed from its design**. It also records which deferred items each `/deferred` pass fixed with a quick fix.

The main reason is finding 22 ("spec drift"). A mid-run `Ruling:` that contradicts the spec lives only in the executor's ledger (`.sdd/<plan>/progress.md`), and that workspace is deleted when the plan completes. The branch keeps such rulings after the workspace is gone, and the approved spec is never edited.

It has 21 commits, 46 files and about 3,100 added lines. Most of the added lines are the plan (811), the micro-test record (535), the script (555) and its tests (661). The behavioural changes to skill text are small.

## What changes, by file

### New: the script and its reference
- **`skills/writing-plans/scripts/history_entry.py`** is a PEP 723 script that uses only the standard library. It **prints a draft and never writes a file.** The agent finishes the draft and appends it.
  - `draft <plan> [--ledger] [--spec --spec-status retired|live] [--date]` builds an entry from these sources:
    - the plan header: the spec path, or `none`, and the `Roadmap:` line
    - `> Deviation:` notes, labelled by task or by `§ <heading>`, with wrapped blockquote lines joined
    - `## Decisions` bullets whose `Applied in:` matches `\(spec amendments?\b`
    - every ledger `Ruling:` line, labelled by task or `final review`
    - the count of items in the plan's own deferred section
    - earlier deferred items whose `→ done` note names `plan <id>` as a whole word
  - `deferred [--date]` lists the items ticked `→ done <date> (/deferred quick fix)`. It leaves out any item that an earlier `## /deferred — <date>` section already lists.
  - Text inside code is never read. That covers fenced blocks, fences inside blockquotes and inline code spans. It reuses `deferral_scan.blank_code` and `deferred_stats.parse_items`.
  - It exits 2 with a one-line stderr message on bad input: a missing file, a file that is not a plan, or `--spec` given without `--spec-status` (or the reverse).
- **`skills/writing-plans/references/history.md`** gives the file format, the entry format, seven rules, and an 8-step "Finish the draft" checklist. In the checklist the agent:
  - deletes rulings that did not change the build (D7)
  - relabels gate-tagged rulings as `Ruling, contradicts spec`
  - shortens Deviation and Decision lines
  - never edits quoted titles
  - resolves the warning lines

### Changed skill and command text
- **`skills/writing-plans/SKILL.md`**: Protocol step 5 (Retire) gets three lines. Before the `chore(specs): retire plan <id>` commit, the agent drafts the history entry, finishes it and appends it in that same commit. To stay under the 20,000-character compaction cut, the example block in step 3 was removed. `references/deferred-backlog.md` already holds the same example.
- **Both executors' `references/final-review.md`** (subagent-driven-development and executing-plans): at the completion gate, each ruling that contradicts spec text is tagged `contradicts spec: <spec section>`. Two new sentences say three things:
  - A tagged ruling is still a decision already taken, not a question.
  - The history entry records it in place of a spec amendment, so the agent asks the owner nothing about it.
  - If the owner asks to revert it, it becomes a deferred item.
- **`commands/deferred.md`**, plus the regenerated Gemini `runtimes/…/deferred.toml`: when a pass ticks at least one quick fix, step 5 runs `history_entry.py deferred --date <tick date>` before `archive_deferred.py` and commits `specs/history.md` with the pass.
- **README, NOTICE, `build/suites.toml`**: a one-line mention in the layout list, a provenance note (the three new files are original MIT work in an adapted skill), and an updated suite note.

### Records
- `specs/history.md` is created, and its first entry is plan 80's own.
- The spec and plan move to `specs/completed/` and `specs/plans/completed/`.
- `specs/deferred_items.md` gets a `## 80-development-history-record` section with 2 items (see below).
- `specs/red-baseline-development-history.md` and its kit hold the micro-tests (next section).

## Evidence

- **Unit tests:** I ran the `writing-plans` suite and got **402 passed, 4 xfailed**.
- **Repo checks:** `check_conformance.py`, `sync_runtime_assets.py --check` and `check_provenance.py` all exit 0.
- **Micro-tests** (model `claude-opus-5-5`, 5 reps per arm, bar = treatment 5/5 and control fails at least 1 of 5):

  | Case | Control | Treatment | Treatment 2 | Bar met |
  |---|---|---|---|---|
  | `gate-tag` | fails 5/5 | 2/5 at `6df0a2c` | 5/5 at `fd4749b` | yes, after one wording round |
  | `history-filter` | fails 5/5 | 5/5 | not run | yes |

  `gate-tag` first failed because three of five reps turned the tagged ruling into a question for the owner ("should I update § 2…?"). The wording round added the two sentences above, and the second treatment arm then passed 5/5. The total spend was $0.74 of the $12 stop.
- **Real-data check:** the record runs `draft` on retired plans 79 and 74, and `deferred` on the 2026-10-05 pass. I reran `draft` on plan 80 and `deferred --date 2026-10-05` myself, and both give sensible output. On a non-plan file the script exits 2 with a clear error.

## Things to know before merging

1. **One reading of the micro-test rule was written after the results were seen.** In `gate-tag`, a reading of clause 4 was added after the first treatment replies were read: an imperative "please confirm or reverse ruling 1" counts as a fail. It was added before `treatment2` ran, the record says so openly, and it does not change any bar result (the first treatment would be 3/5 at best). It is still worth knowing that the rule moved.
2. **Two code commits land after the retire commit.** `7931b3c` is a real fix: the spec-amendment mark was read on unmasked text, so a mark inside inline code wrongly counted. `325330a` fixes stale paths. Both answer Codex comments on `d5d40ff`. Plan 80's history entry was written before them. That is acceptable because the entry is a design-difference record, but the entry does not mention `7931b3c`.
3. **The reference and the script disagree slightly on rule 4.** `references/history.md` rule 4 still says a decision qualifies when `Applied in:` "contains `(spec amendment)`". The script, after a final-review ruling tagged *contradicts spec*, accepts `\(spec amendments?\b`. That also covers `(spec amendments)` and `(spec amendment A2)`. The agent never filters decisions by hand, so the effect is small, but the live reference now describes less than the code does. Consider updating that sentence. The spec stays as it is by design (D2).
4. **Long quoted titles get cut off.** Titles are the item's *first line* (spec rule 6). For backlog items whose bold title wraps, the quote ends mid-phrase. For example, `deferred --date 2026-10-05` prints `"The fair-rated spread step is direction-blind (plan 34 final-review recommendation,"`. Finish step 5 forbids editing the quoted title, so these cut-off titles will reach `history.md` as printed. This is cosmetic and follows the spec, but it may be worth a deferred item.
5. **Plan 80 deferred two of its own items:**
   - *A revert asked for at the gate has two rules* (design): the spec and the gate paragraphs say "deferred item as today", but writing-plans protocol step 1 handles it as an answer that unblocks work at once.
   - *Finish step 2 has no source for the gate's tags after a `/clear`* (quick fix): the `contradicts spec` tags exist only in the gate message. Plan 80's own run wrote them into its ledger by hand.

   Both are real gaps in the new flow. The second one will show up whenever a context reset falls between the gate and retirement.
6. **Out of scope by design:** no history entries for plans retired before this change, no fix for the stale-pointer defect (it is tracked separately in the backlog), and findings 21 and 24 are not addressed.

## My read

The change is narrow in behaviour: one step-5 pointer, one gate tag with two sentences, and one `/deferred` step. The script writes no file, so a wrong draft can't land unread. Tests, lints and the micro-test bars pass. I'd merge. Items 3 and 4 are small follow-ups, and item 5's `/clear` gap is the one most likely to come up in practice.
