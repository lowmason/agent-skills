# Development history record — Design Spec

**Status:** DRAFT (2026-11-08), for the owner's review. The design came from a brainstorming session on
2026-11-08. That session took finding 22 ("Spec drift is unaddressed",
`specs/superpowers-drift-spec-v7-0-2.md:729-750`) alone, apart from findings 21 and 24, on the owner's decision
(D1). Decisions D1–D7 are the owner's, from that session. Text marked *(designer's call)* is the designer's choice.

Each project that uses these skills gets one Markdown file, `specs/history.md`. It records what each plan built and
where the build differed from its design, and which deferred items each `/deferred` pass fixed. The plan-completion
protocol appends one entry for each plan, and `/deferred` one entry for each pass that closes items, from a draft
that a script prints. No spec is edited after approval to keep it current. The history file holds that record.

## Motivation

Finding 22 says that a mid-run `Ruling:` that contradicts spec text never reaches the spec. Over several plans, the
committed design records stop describing the system. The assessment proposed one line in the plan-completion gate:
make such a ruling a spec amendment, or a deferred item that closes when the spec changes.

The brainstorming session found three more facts:

| Fact | Evidence |
|---|---|
| `Ruling:` lines are lost after completion. They live in the run's ledger, `<workspace>/progress.md`. The executor deletes the workspace when the protocol finishes. The gate shows the rulings to the owner once, and no lasting file keeps them. | `skills/subagent-driven-development/references/final-review.md:35`, `:44-52`; `skills/executing-plans/SKILL.md:131-139` |
| Differences from the design are spread over several places: `> Deviation:` notes (70 of 80 retired plans), `## Decisions` entries (40 of 80), deferred items and their closure notes, and the lost rulings. No one place collects them. | `specs/plans/completed/`, `specs/deferred_items.md`, `specs/completed/deferred_items.md` |
| Most closures of deferred items do not come from a plan. They come from `/deferred` quick fixes (for example, 48 items closed on 2026-10-05 with `→ done 2026-10-05 (/deferred quick fix)`). | `specs/deferred_items.md`, `specs/completed/deferred_items.md` |

## Decisions

- **D1** (owner, 2026-11-08): finding 22 gets its own session. Findings 21 and 24 stay in the other session.
- **D2** (owner, 2026-11-08): a later reader of a retired spec needs to know what was built and where the build
  differed from the design. That record need not be in the spec. It can be another, shorter document that refers to
  the spec, the plans and the deferred items.
- **D3** (owner, 2026-11-08): the record serves any project that uses these skills, not only this repository. Its
  uses are a short development history to inform practice, documentation of the system as built, and one input for
  judging a skill. It is read rarely. It lives in `specs/` as Markdown for the same reason as the specs, plans and
  deferred items: an easily accessible record, not a set of PRs to decipher.
- **D4** (owner, 2026-11-08): the history record replaces the owner's earlier trigger proposal (a trigger that writes
  into a retired plan what became of its deferred items, once all of them close). A later plan's history entry
  records the closures of earlier items instead.
- **D5** (owner, 2026-11-08): approach B (below): a protocol step, a reference file, and a script that drafts the
  entry.
- **D6** (owner, 2026-11-08): `/deferred` passes also write history entries, so closures from quick fixes are in the
  history too.
- **D7** (owner, 2026-11-08): an entry keeps only the rulings that changed the build against the spec or the plan
  (rule 3). A ruling that declined a finding and kept the plan as written stays out.

## Goals

1. One file for each project records, for each completed plan, what it built and where it differed from its spec and
   plan, with a pointer from each line to its source. It also records which deferred items each `/deferred` pass
   fixed.
2. A `Ruling:` that changed what got built outlives the ledger.
3. A ruling that contradicts spec text is marked as such at the gate, so the owner sees it before it is recorded.
4. A rare reader finds the record in one place, in any project.

## Non-goals

- Editing an approved spec to describe the current system. The spec stays the design record (D2).
- A spec amendment for each contradicting ruling. The assessment's spec-amendment branch is replaced by the history
  entry *(designer's call, from D2)*. A ruling the owner wants reverted still becomes a deferred item, as today.
- Fixing the stale `deferred items in specs/deferred_items.md` pointer in retired plans whose sections drained to the
  archive (handoff trap T1). It is a separate defect. It stays the owner's call whether to file it.
- Backfilling history entries for plans retired before this change *(designer's call)*.
- Findings 21 and 24, and the backlog item `spec-reading-test-check` (D1).

## Anti-goals

- A record that must be maintained. No step edits an earlier entry. A rarely read file that needs upkeep will rot.
- A record that restates the plan. "What was built" is the plan's pointer and its title. The entry lists only
  differences.
- A new edit that pushes `skills/writing-plans/SKILL.md` over the compaction cut (20,000 body characters).

## Approaches

| Approach | Trade-off | Outcome |
|---|---|---|
| A. A protocol step and a reference file. The agent writes each entry by hand. | Lowest cost. Entry form can vary from plan to plan. | Not chosen. |
| B. As A, plus a script that reads the sources and prints a draft entry for the agent to finish. | Uniform entries, and the sources are read the same way each time. Costs a script and its tests. | **Chosen (D5).** |
| C. Put the differences into each plan's section of `specs/deferred_items.md`. | No new file. `archive_deferred.py` moves drained sections to the archive, so the history would split across two files and mix with open work. | Dropped. It works against D3's one easy place to look. |

## Design

### The history file

- Path: `specs/history.md` *(designer's call)*. Title line `# Development history` and no other preamble, created on
  first use, like `specs/deferred_items.md`.
- One `##` section for each completed plan, and one for each `/deferred` pass that closes items (below), newest
  last. The heading is the same as the plan's section heading in
  `specs/deferred_items.md`: `## <plan-stem> — YYYY-MM-DD`, where `<plan-stem>` is the plan filename without `.md`
  and the date is the completion date.
- Append-only. No skill step edits or moves an earlier section.

### Entry format

```markdown
## 7-rate-limiter — 2026-07-04
Plan: specs/plans/completed/7-rate-limiter.md · Spec: specs/completed/rate-limiter.md (retired)

Differences from the design:
- Ruling, contradicts spec (Task 3): count requests per key, not per IP — the spec's per-IP rule breaks behind the
  proxy — clients behind one NAT share a key if wrong.
- Ruling (Task 4): returned 503, not the plan's 429, when the store is down — a 429 tells clients to back off from
  a fault that is ours — clients retry at once if wrong.
- Deviation (Task 2): the store reads the limit from config, not from a constant. Source: plan, Task 2.
- Decision D2 (spec amendment): the 429 body is JSON. Source: plan, `## Decisions`.
- Deferred: 2 items. Source: specs/deferred_items.md, § 7-rate-limiter.

Closed earlier deferred items:
- "Retry jitter is fixed-seed in tests only" (deferred by 5-http-client).
```

Rules:

1. The first line names the plan's retired path and the spec's path with `(retired)` or `(live)`. When the plan
   header has a `Roadmap:` line, add `· Roadmap: <path>, Stage N`. When the plan has no spec, write `Spec: none`.
2. **Rulings are copied whole**, because their source is deleted. Each is the ledger's `Ruling:` text after the
   prefix. Its label is `Ruling` or `Ruling, contradicts spec`, followed by the task or `final review` in brackets
   when the ledger line shows it.
3. **Rulings that go in:** each ruling that changed what got built against the spec or the plan text. A ruling that
   only parks a finding with no change to the build stays out (D7). The script lists every ruling and
   the agent removes the ones that do not qualify.
4. **Deviations and decisions** are one short line each, with a source pointer. Decisions go in only when they are
   spec-level: their `Applied in:` list contains `(spec amendment)` anywhere, for example `Applied in: Task 1 (spec
   amendment), Task 2` *(designer's call)*. A plan-level decision is already the plan text.
5. **Deferred** is one line with the count and a pointer to the section. When nothing was deferred, the line is left
   out.
6. **Closed earlier deferred items** lists each item that this plan ticked in protocol step 3, by its first-line
   title and the section it came from. The tick form is `→ done <YYYY-MM-DD> (plan <id>)`, as the Item notes table in
   `skills/writing-plans/references/deferred-backlog.md` already fixes. Older ticks use other forms (`→ done in plan
   63 (D)`, `→ done D (plan 79)`), so the script matches any `→ done` note that names `plan <id>` as a whole word
   *(designer's call)*. No change to `SKILL.md` step 3 is needed.
7. When a list has no lines, it is left out. When the entry has no differences and closed nothing, its body after
   the first line is `No differences from the design.`

### `/deferred` entries (D6)

A `/deferred` pass that ticks at least one item `→ done <YYYY-MM-DD> (/deferred quick fix)` appends one entry. A
pass that only retires, holds, plans or designs items writes none: those change no built thing *(designer's call)*.

```markdown
## /deferred — 2026-10-05

Closed deferred items:
- "Retry jitter is fixed-seed in tests only" (deferred by 7-rate-limiter): seeded jitter from the test fixture.
```

- The heading is `## /deferred — YYYY-MM-DD`, the pass date.
- Each line is the item's first-line title, the section it came from, and the quick-fix note's text after the
  arrow's `:` when it has one. That note says what the fix changed.
- A second pass on the same date appends its own section with the same heading. The script leaves out items that an
  earlier section of that heading already lists *(designer's call)*.
- The entry is written before the pass's closing `archive_deferred.py` run, so every item is still in the live file,
  and it goes into the pass's commit. The command step is in `commands/deferred.md`, step 5, beside the archive run.

### Contradicting rulings at the gate (finding 22's line)

Both executors' gate instructions list every `Ruling:` line first (`skills/subagent-driven-development/references/final-review.md:35`,
`skills/executing-plans/references/final-review.md:78`). They add one tag: a ruling that contradicts spec text is
listed with `contradicts spec: <spec section>`. Such a ruling stays a decision already taken, not a question. The
owner may ask to revert it, which makes it a deferred item as today. Either way it goes into the history entry under
rule 2.

### The script

`skills/writing-plans/scripts/history_entry.py`, a PEP 723 stdlib script like its siblings in that folder.

```
uv run <writing-plans>/scripts/history_entry.py draft <plan> [--ledger <path>] [--spec <path> --spec-status retired|live] [--date YYYY-MM-DD]
```

- Reads the plan file: its `Roadmap:` and `**Spec:**` header lines, its `> Deviation:` notes with their task
  numbers, and its `## Decisions` lines whose `Applied in:` contains `(spec amendment)`.
- `--spec` gives the spec's final path and `--spec-status retired|live` its state. The agent passes both from step 5's
  retire decision. The script does not repeat step 5's suffix rule *(designer's call)*.
- Reads the ledger at `--ledger` when given: every line that contains `Ruling:`, with a task number or `final review`
  when the line shows one. Without `--ledger`, it prints a `Rulings: no ledger given` warning line in the draft.
- Reads `specs/deferred_items.md` from the repository root above the plan: the count of items in the plan's section,
  and every item whose notes carry `→ done … (plan <id>)` for this plan's id.
- Prints the draft entry to stdout in the entry format, with every ruling labelled `Ruling` (the agent adds
  `contradicts spec` from the gate). It writes no file *(designer's call)*: the agent finishes the draft and appends
  it, so a wrong draft never lands unread.
- Exit 0 with a draft; exit 2 with a one-line error when the plan file is missing or not a plan.

A second subcommand drafts a `/deferred` entry:

```
uv run <writing-plans>/scripts/history_entry.py deferred [--date YYYY-MM-DD]
```

- Reads `specs/deferred_items.md` from the current repository root: every item with a
  `→ done <date> (/deferred quick fix)` note for the date (default: today).
- Reads `specs/history.md`, when it exists, to leave out items already listed under a `## /deferred — <date>`
  heading.
- Prints the draft. When no item qualifies, prints nothing and exits 0, and the pass writes no entry.

Tests go in `skills/writing-plans/scripts/test_history_entry.py`, in the existing `writing-plans` suite in
`build/suites.toml`. Fixtures are small inline plan, ledger and backlog texts.

### Protocol step

The history entry is written inside step 5 (retire), after step 5 decides whether the spec retires and before its
`chore(specs): retire plan <id>` commit *(designer's call)*. At that point the ledger still exists, the deferred
section is final, and the plan's and spec's final paths are known:

- Run the script with the plan's retired path, `--spec` and `--spec-status`, and the ledger. Finish the draft (rule
  3 and the `contradicts spec` tags), append it to `specs/history.md`, and include it in the retire commit.
- The executors delete their workspace only after the protocol finishes (unchanged), so the ledger is readable here.

The step's text goes in a new reference, `skills/writing-plans/references/history.md`: the file, the entry format,
the rules and the script command. `SKILL.md` gets one pointer line. `SKILL.md` has 19,995 body characters, so the
pointer needs an equal or larger cut elsewhere in that file. Moving prose to a reference is the expected form.
Run `uv run --with pyyaml python build/check_conformance.py` before the commit.

## Left to the builder

- The pointer line's wording and the cut that makes room for it in `skills/writing-plans/SKILL.md`.
- The script's internal parsing, reusing `deferred_stats.parse_items` for item spans where it fits.
- Where the pointer line sits in step 5, and the order of the script run against the `git mv`.
- Whether `install.py` `DEPENDENCIES` or `SOFT_REFERENCES` need a change. The executors already depend on
  writing-plans. Run the dependency-drift check.

## Constraints

- `skills/writing-plans/SKILL.md` is at the compaction limit (finding 17). The other session (D1) may also edit it,
  so the plan should keep this edit to the pointer line and its cut, and expect a merge.
- The deferral lint reads new files under `specs/completed/` and `specs/plans/completed/`. `specs/history.md` is in
  neither, so the lint does not read it.
- `commands/deferred.md` changes (D6). It is canonical: regenerate `runtimes/` with
  `build/sync_runtime_assets.py`, then run its `--check`. The command already depends on writing-plans in
  `install.py`, so its new reference to `references/history.md` and the script needs no new dependency. The
  dependency-drift check confirms it.
- Provenance: writing-plans is a superpowers-adapted skill (`NOTICE`, `LICENSE-superpowers`). The new reference and
  script are original work in an adapted skill. Check `NOTICE` and `build/check_provenance.py` for what that needs.
