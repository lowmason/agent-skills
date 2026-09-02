---
description: Triage specs/deferred_items.md — group unticked items, then sort each into retire / quick fix / plan / design / hold so the ceremony matches the item; brainstorming only for items that record an open design decision
disable-model-invocation: true
---

Triage the deferred-work backlog in the current project. The triage pass
(steps 1–4) is read-only. Edits to `specs/deferred_items.md` happen only in
step 5, only for items the user selected, and only in the two tick forms
named there — ticking items implemented by a plan remains the job of that
plan's completion-protocol run.

Scope: unticked (`- [ ]`) items in `specs/deferred_items.md`. Live roadmap
stages (`specs/*-roadmap.md`) are out of scope — the roadmap is its own
backlog (derive-roadmap's gap rubric records the same boundary).

1. Read `specs/deferred_items.md` at the project root. If the file does not
   exist, or it contains no unticked items, report that nothing is deferred
   and stop.
2. Group the unticked items by theme — related items from different plan
   sections belong together. Keep each item's source plan and date (from
   its `## <plan> — <date>` section header) attached.
3. Sort every item or group into exactly one disposition. Match the
   ceremony to the item; most backlogs are mostly small.
   - **Retire** — the premise no longer holds: the code it names was
     rewritten or removed, the fix already landed, the artifact is gone,
     or the item records a no-action decision and never needed a checkbox.
     Age alone is not staleness. Back each retire verdict with one concrete
     check (a path, a `git log -S`, a grep) and cite it.
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
4. Present one section per disposition, items within grouped by theme,
   each with plan and date. Rank within **Plan** and **Design** with
   one-line reasoning; leave the rest flat. Then stop and wait for the
   user's selection.
5. Act only on what the user selects, per disposition:
   - **Retire** → tick the item in place:
     `- [x] … → retired <YYYY-MM-DD>: <one-line why>`.
   - **Quick fix** → fix it under the house disciplines
     (test-driven-development for code, verification-before-completion
     before claiming done), then tick the item:
     `- [x] … → done <YYYY-MM-DD> (/deferred quick fix)`.
   - **Plan** → use the writing-plans skill with the selected items as the
     requirements; name the plan for the theme, since there is no spec.
     That plan's completion protocol ticks the items.
   - **Design** → use the brainstorming skill with the selection as the
     idea — a new spec through the normal design cycle.
   - **Hold** → no edit; restate the blocking condition in the report.
