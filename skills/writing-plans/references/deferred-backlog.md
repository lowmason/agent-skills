# Deferred-backlog reference

The shared contract for `specs/deferred_items.md`: what an item must record,
how to triage the backlog, and when the aged tail blocks a branch finish.

Three callers read this file:
- **writing-plans** § Plan Completion Protocol — writes items (schema below)
  and runs the read-only triage at completion.
- **finishing-a-development-branch** § Step 1b — runs the aged-tail gate.
- **`/deferred`** — runs the full triage and is the only caller that may
  execute a disposition.

## Thresholds

| Name | Value | Used by |
|---|---|---|
| Aged tail | open items in a section dated more than **45 days** ago | the aged-tail gate; the triage's ranking |
| Volume | **20 or more** open items | the soft one-line backlog status |

Age comes from each item's `## <plan> — <YYYY-MM-DD>` section header, which the
Plan Completion Protocol has always written. Do not add a per-item date field:
a new field would only exist on new items, and the aged tail is by definition
made of old ones.

## Backlog stats

Run from the repo root:

```bash
uv run --python 3.13 python ~/.claude/skills/writing-plans/scripts/deferred_stats.py
```

Add `--json` when you need the raw numbers (`open`, `closed`, `closure_rate`,
`aged_open`, `oldest_open_days`, `age_histogram`) rather than the text summary.
The script always exits 0 — it reports, it does not gate. It reads
`specs/deferred_items.md` by default and reports cleanly when that file is
absent, so it is safe to run in any repo.

Report **closure rate and the age spread**, never a bare open count. A bare
"69 open" is a number people tolerate; "69 open, 17% closure rate, 29 aged
>45d" is a decision.

## Deferred-item schema

Every item is self-contained — it is read months later by someone with none of
this session's context. It records file paths, why it was deferred, what it
would take to do, plus:

- **Closure condition** — `Done when:` for work, or `Revisit if:` for a
  watch item. This is what the triage checks; without it, the disposition has
  to be reconstructed from scratch every pass, which is the effort that makes
  triage get skipped.
- **Size** — one of `quick-fix`, `plan`, or `design`, matching the
  dispositions below. Written when context is freshest, so triage becomes
  "check the condition, route by size."

```markdown
## 7-rate-limiter — 2026-07-04
- [ ] Redis-backed counter store (plan Task 4, skipped): needs prod Redis
      DSN decision. See specs/plans/completed/7-rate-limiter.md; touches
      src/limiter/store.py. Size: design. Done when: the DSN decision is
      recorded and the store lands behind it.
- [ ] Review Minor: retry jitter is fixed-seed in tests only (reviewer
      report, triaged defer). Size: quick-fix. Revisit if: a flake in
      tests/test_limiter.py traces to jitter.
```

**An item that cannot state a closure condition is not deferrable.** Resolve it
now or drop it. "Maybe look at this again" with no condition never closes,
because nothing can ever discharge it.

Items written before this schema landed have no `Size:` or `Done when:` line.
Triage them from their recorded reason as before — never rewrite an old item
just to add the fields, and never treat a missing field as a defect.

## Triage rubric

Scope: unticked (`- [ ]`) items in `specs/deferred_items.md`. Live roadmap
stages (`specs/*-roadmap.md`) are out of scope — the roadmap is its own
backlog (derive-roadmap's gap rubric records the same boundary).

Steps 1–4 are **read-only** and may be run by an agent unprompted. Step 5 is
the human's, and runs only under `/deferred`.

1. Read `specs/deferred_items.md` at the project root. If the file does not
   exist, or it contains no unticked items, report that nothing is deferred
   and stop.
2. Group the unticked items by theme — related items from different plan
   sections belong together. Keep each item's source plan and date (from
   its `## <plan> — <date>` section header) attached.
3. Sort every item or group into exactly one disposition. When the item
   records a `Size:`, that is the disposition unless its closure condition
   has already been met (then it is **Retire**) or is still unmet and
   external (then it is **Hold**). Match the ceremony to the item; most
   backlogs are mostly small.
   - **Retire** — the premise no longer holds: the code it names was
     rewritten or removed, the fix already landed, the artifact is gone,
     the recorded closure condition is already satisfied, or the item
     records a no-action decision and never needed a checkbox. Age alone is
     not staleness. Back each retire verdict with one concrete check (a
     path, a `git log -S`, a grep) and cite it.
   - **Quick fix** — one site, the fix is spelled out in the item, no
     decision left to make. Done directly, no spec or plan.
   - **Plan** — the item or group records *what* to do and only needs
     sequencing and tests: a hardening pass, a batch of test-coverage gaps,
     a refactor touching several call sites. The recorded items are the
     requirements; go straight to writing-plans — no brainstorming.
   - **Design** — an open decision is recorded ("decide", "needs a
     design", "spec change"), or the change touches a skill or protocol
     contract. Only these go through brainstorming to a new spec.
   - **Hold** — still blocked on the recorded condition ("revisit if it
     recurs", "when X is reachable", "after N real runs"), or dischargeable
     only by the owner (an interactive check, a commit in another repo).
     List the owner-only ones separately so they get done.

   Judge from each item's recorded reason. Open the repo only to confirm a
   retire verdict, never to re-litigate an item's merit.
4. Present one section per disposition, items within grouped by theme, each
   with plan and date. Lead with the `deferred_stats.py` summary line. Rank
   within **Plan** and **Design** with one-line reasoning, aged items first;
   leave the rest flat. Then stop and wait for the user's selection.
5. **Human-invoked only, under `/deferred`.** Act on what the user selects,
   per disposition — see that command for the tick forms.

## Aged-tail gate

Run by finishing-a-development-branch before it offers merge/PR. Volume alone
is reported, never blocking: a large backlog can be legitimate. **Age is the
proxy for neglect**, so only the aged tail gates.

When `aged_open` is 0, report the one-line status and continue.

When `aged_open` is greater than 0, the branch does not finish until one of:

- **A `/deferred` pass**, which the human runs. Then re-run the stats.
- **A logged acknowledgement.** Append one plain bullet — never a checkbox,
  so it never enters the backlog counts — under a `## Aged-backlog
  acknowledgements` section pinned directly beneath the file's
  `# Deferred items` title, creating that section if absent:

```markdown
## Aged-backlog acknowledgements
- 2026-09-08 — finished `feat/rate-limiter` with 29 items aged >45d, carried
  deliberately: the Redis decision is still with the platform team.
```

The acknowledgement needs a reason. "Carried deliberately" with no reason is
the silent default this gate exists to convert into a conscious one. The
override is deliberately easy to take and impossible to take invisibly.
