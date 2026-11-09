# Development history reference

`specs/history.md` is one project's record of what each plan built and where the build differed from its design. It
also records which deferred items each `/deferred` pass fixed. Two steps write it: Protocol step 5 (Retire) writes one
entry for each plan, and step 5 of `/deferred` writes one entry for each pass that closes items. Each step runs
`scripts/history_entry.py`, which prints a draft. You finish the draft and append it.

## The history file

- Path: `specs/history.md`.
- First line: `# Development history`, and no other preamble. Create the file on first use.
- One `##` section for each completed plan, and one for each `/deferred` pass that closes items. Newest last.
- Plan heading: `## <plan-stem> — YYYY-MM-DD`. `<plan-stem>` is the plan filename without `.md`. The date is the
  completion date.
- `/deferred` heading: `## /deferred — YYYY-MM-DD`. The date is the pass date.
- Append-only. No skill step edits or moves an earlier section.

## Plan entries

**When.** In Protocol step 5, after the `git mv` of the plan and the decision on whether the spec retires, and before
the `chore(specs): retire plan <id>` commit. The executor deletes its workspace only after the protocol ends, so the
ledger is still readable.

**Command.** Run it from the repo root:

```bash
uv run <this-skill-dir>/scripts/history_entry.py draft specs/plans/completed/<file> --ledger <workspace>/progress.md --spec <final spec path> --spec-status retired|live
```

- `<workspace>` is the executor's `.sdd/<plan-basename>/` directory.
- `--spec` is the spec's path after step 5's decision. `--spec-status` is `retired` or `live`. Give both or neither.
- Leave out `--spec` and `--spec-status` for a plan whose header reads `**Spec:** none`.
- Leave out `--ledger` only when the run kept no ledger.

**Entry format.**

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

**Rules.**

1. The first line names the plan's retired path and the spec's path with `(retired)` or `(live)`. When the plan
   header has a `Roadmap:` line, add `· Roadmap: <path>, Stage N`. When the plan has no spec, write `Spec: none`.
2. **Rulings are copied whole**, because their source is deleted. Each is the ledger's `Ruling:` text after the
   prefix. Its label is `Ruling` or `Ruling, contradicts spec`, followed by the task or `final review` in brackets
   when the ledger line shows it.
3. **Rulings that go in:** each ruling that changed what got built against the spec or the plan text. A ruling that
   only parks a finding with no change to the build stays out (D7). The script lists every ruling and
   the agent removes the ones that do not qualify.
4. **Deviations and decisions** are one short line each, with a source pointer. Decisions go in only when they are
   spec-level: their `Applied in:` list contains `(spec amendment)` anywhere, for example
   `Applied in: Task 1 (spec amendment), Task 2`. A plan-level decision is already the plan text.
5. **Deferred** is one line with the count and a pointer to the section. When nothing was deferred, the line is left
   out.
6. **Closed earlier deferred items** lists each item that this plan ticked in protocol step 3, by its first-line
   title and the section it came from. The tick form is `→ done <YYYY-MM-DD> (plan <id>)`, as the Item notes table in
   [deferred-backlog.md](deferred-backlog.md) already fixes. Older ticks use other forms (`→ done in plan 63 (D)`,
   `→ done D (plan 79)`), so the script matches any `→ done` note that names `plan <id>` as a whole word.
7. When a list has no lines, it is left out. When the entry has no differences and closed nothing, its body after
   the first line is `No differences from the design.`

**Finish the draft.** The script labels every ruling `Ruling`. It adds no tag from the gate. Do these in order:

1. Delete each ruling that did not change what got built against the spec or the plan: one that declined a finding
   and kept the plan as written, or one that parked a finding with no change to the build.
2. Relabel each ruling that the gate listed with `contradicts spec: <spec section>` as `Ruling, contradicts spec`,
   keeping its bracketed task.
3. Keep each remaining ruling's text whole.
4. Shorten each `Deviation` and `Decision` line to one short line, and keep its `Source:` pointer.
5. Never edit a quoted title or its `(deferred by …)` part.
6. Resolve and delete each warning line: `Rulings: no ledger given`, `Spec: --spec not given`.
7. Delete a list heading whose list is now empty (`Differences from the design:`, `Closed earlier deferred items:`).
   When both lists are gone, the body after the `Plan:` line is `No differences from the design.`
8. Create `specs/history.md` with its title line when it is absent, append the entry after one blank line, and stage
   the file into the `chore(specs): retire plan <id>` commit.

## /deferred entries

**When.** In step 5 of `/deferred`, before the closing `archive_deferred.py` run, and only when the pass ticked at
least one item with `→ done <YYYY-MM-DD> (/deferred quick fix)`. A pass that only retires, holds, plans or designs
items writes no entry: those passes change no built thing.

**Command.** Run it from the repo root:

```bash
uv run <this-skill-dir>/scripts/history_entry.py deferred --date <YYYY-MM-DD>
```

The date is the one on the pass's `→ done … (/deferred quick fix)` ticks.

It reads `specs/deferred_items.md` and prints one line for each ticked item whose `→ done <YYYY-MM-DD> (/deferred quick fix)`
note carries the pass date (`--date`, default today). A second pass on the same date appends its own section with the
same heading. The script leaves out each item that an earlier section of that heading already lists.

**Entry format.**

```markdown
## /deferred — 2026-10-05

Closed deferred items:
- "Retry jitter is fixed-seed in tests only" (deferred by 7-rate-limiter): seeded jitter from the test fixture.
```

**Finish the draft.** Shorten the text after the `:` only. Never edit the quoted title or the `(deferred by …)` part.
When the script prints nothing, write no entry. Append the entry to `specs/history.md` (create it with its title line
when it is absent), after one blank line, and put the file into the pass's commit.

## The script

`scripts/history_entry.py` is a stdlib script with a PEP 723 header, so `uv run` gives it its own environment.

- It writes no file. A wrong draft never lands unread, because you finish the draft and append it.
- `draft` exits 0 with a draft. It exits 2, with a one-line error on stderr, when the plan file is missing or not a
  plan, or when `--spec` and `--spec-status` do not come together.
- `deferred` exits 0, and prints nothing when no item qualifies or `specs/deferred_items.md` is absent. It exits 2,
  with a one-line error on stderr, when `specs/deferred_items.md` or `specs/history.md` exists but cannot be read.
- `--date YYYY-MM-DD` sets the entry date. It defaults to today.
