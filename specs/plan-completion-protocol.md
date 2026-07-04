# Plan-completion protocol: markup, resolve-before-defer, retire

**Status:** Active (approved 2026-07-04)

## Context

The process skills already encode the front half of the user's spec-driven workflow:
specs are descriptive-named markdown in `specs/` (`brainstorming`), plans go to
`specs/plans/<id>-<spec-name>.md` with an auto-incrementing `<id>` (`writing-plans`),
and implementation runs through `subagent-driven-development` or `executing-plans`.

The back half is missing. After implementation:

- **Nobody edits the plan file.** SDD tracks progress only in the gitignored
  `.sdd/progress.md` ledger; `executing-plans` ticks its session todo list. The plan —
  the durable, tracked artifact — never shows what was actually completed.
- **Deferred work evaporates.** Review findings triaged "defer" and consciously skipped
  plan tasks die in the gitignored ledger (this happened to the audit-remediation
  deferred Minors).
- **Retirement is a convention, not a step.** `writing-plans` and `brainstorming` state
  that completed plans/specs move to `completed/`, but no skill executes the move at the
  right moment.

This spec adds a **plan-completion protocol** operationalized at the end of both
execution skills, and a standing document `specs/deferred_items.md`.

## Decisions

1. **Protocol home** — end of both execution skills (SDD and executing-plans), before
   `finishing-a-development-branch`. The executor session has the freshest knowledge of
   what was completed, deviated, or deferred. Canonical text lives in `writing-plans`
   (owner of plan format); the execution skills carry pointers — the repo's existing
   canonical+pointer pattern.
2. **Deferred scope** — two feeds: plan tasks/steps consciously skipped or descoped
   during execution, and review findings triaged "defer" rather than fixed. Plus a
   **resolve-before-defer gate**: items that stalled on missing user input are asked
   about at completion time; only what the answers can't unblock is deferred.
3. **Commit timing** — markup/defer/retire commits land on the feature branch as its
   final commits, so a merge or PR carries them atomically, and a discarded branch
   correctly takes its "completion" markup with it.

## A — The protocol

Runs after all tasks are done and the final review is resolved, before
`finishing-a-development-branch`. The gate runs FIRST — markup is written only once the
completed/deferred partition is final:

1. **Resolve-before-defer gate.** Collect the leftovers: skipped/descoped plan steps +
   review findings triaged "defer". Partition:
   - Stalled because it needed user input → ask now, as one batched set of questions.
   - Unblocked by an answer → implement before completing (loop back into execution;
     the protocol restarts after that work lands).
   - Everything else → defer.
   Unanswered gate questions block the rest of the protocol: the partition is final
   only once every ask is resolved — in a one-shot run, end the turn with the batched
   questions and resume when answered. (Added by GREEN fix loop: without this sentence,
   6/6 pressure-test agents retired the plan first and asked after, making the ask
   decorative.)
2. **Markup the plan file.** Tick every completed step (`- [x]`). Under any step that
   deviated from the plan, add a one-line `> Deviation: …` note. Annotate skipped steps
   with `> Skipped: <why> → deferred`. Add a status header at the top of the plan:
   `**Status: COMPLETE (YYYY-MM-DD)** — executed via <skill>; deferred items in
   specs/deferred_items.md` — or, when the gate deferred nothing,
   `**Status: COMPLETE (YYYY-MM-DD)** — executed via <skill>; nothing deferred`.
   Markup happens once, after the gate resolves — per-task progress tracking stays
   where it is today (SDD's ledger, executing-plans' todo list).
3. **Append deferred items** to `specs/deferred_items.md` (format below). Create the
   file on first use with a single `# Deferred items` title line, no other preamble.
   Skip this step entirely when nothing was deferred — never append an empty section.
4. **Retire.** `git mv` the plan → `specs/plans/completed/`, in one
   `chore(specs): retire plan <id>` commit. Retire the spec → `specs/completed/`
   (marked complete at top, per the existing convention) in the same commit **only if**
   the spec file exists and no other live plan in `specs/plans/` implements it (match by
   the `<spec-name>` suffix in plan filenames). Spec-less plans and shared specs leave
   the spec untouched.

## B — `specs/deferred_items.md` conventions

Append-only; one section per completed plan **that deferred anything**, newest last
(created on first use — see protocol step 3):

```markdown
## 7-rate-limiter — 2026-07-04
- [ ] Redis-backed counter store (plan Task 4, skipped): needs prod Redis DSN decision.
      See specs/plans/completed/7-rate-limiter.md; touches src/limiter/store.py.
- [ ] Review Minor: retry jitter is fixed-seed in tests only (reviewer report, triaged defer).
```

- Each item is self-contained: file paths, why it was deferred, what it would take to do.
- When a later plan implements one, that plan ticks the box with a pointer
  (`- [x] … → done in plan 12`).
- Items are never deleted — the file doubles as a history of consciously-deferred work.

## C — Edit map

Five files; everything pointer-sized except the one canonical section:

| File | Change |
|---|---|
| `skills/writing-plans/SKILL.md` | Add canonical **Plan completion** section (protocol A); the existing one-line retirement sentence becomes a pointer to it. |
| `skills/subagent-driven-development/SKILL.md` | New flow-chart node + prose step between "final review" and "Finish the branch": run the protocol. Final-review findings left unfixed feed the gate. The protocol **introduces** SDD's one batched human checkpoint (the resolve-before-defer questions), placed after the final review resolves; any conditional question sets already pending (e.g., plan-mandated findings) fold into the same batch so there is at most one round-trip. This is compatible with the Continuous-execution rule — "all tasks complete" is already a sanctioned stop. |
| `skills/executing-plans/SKILL.md` | New Step 3 "Complete the plan" (protocol pointer); finishing-a-development-branch shifts to Step 4. |
| `skills/brainstorming/SKILL.md` | "Explore project context" also checks `specs/deferred_items.md` for related deferred work, so old deferrals resurface when a new spec touches their area. |
| `CLAUDE.md` (this repo) | Conventions § Specs & plans gains the deferred-items convention (this repo dogfoods the workflow). |

No `NOTICE` changes — all four skills are superpowers-adapted and the existing blanket
modifications clause covers this.

## D — Verification

Discipline skills, so `writing-skills` rules apply:

- **RED (control):** a subagent gets a finished-implementation scenario — plan with one
  skipped task, review triage containing a deferred Minor, one item blocked on missing
  user input — without the new skill text. Expected: no plan markup, no deferred capture,
  no retirement (today's behavior).
- **GREEN:** same scenario with the new text, run for both execution paths (SDD wording
  and executing-plans wording). Expected: full protocol, including the ask-first gate
  firing on the blocked item rather than silently deferring it.
- **GREEN (clean path):** a variant with nothing skipped and no deferred findings.
  Expected: "nothing deferred" status header, no deferred_items.md write, plan retired.
- **Lints:** `check_frontmatter.py` + `check_provenance.py` (watching the 1024-char
  description cap if any skill descriptions gain new trigger words).

## Out of scope

- Seeding this repo's own `specs/deferred_items.md` with the audit-remediation deferred
  Minors (recoverable from `git log` of the ledger) — optional follow-up, not part of
  this change.
- Any change to `finishing-a-development-branch` — it stays pure branch mechanics.
- Changes to `requesting-code-review` — its triage vocabulary already produces the
  "defer" decisions the protocol consumes.
