---
description: Triage specs/deferred_items.md — group unticked items, classify actionable vs blocked, propose promotions to a new spec
---

Triage the deferred-work backlog in the current project. This is read-only:
never edit `specs/deferred_items.md` — ticking items is the job of later
plans' completion-protocol runs.

1. Read `specs/deferred_items.md` at the project root. If the file does not
   exist, or it contains no unticked (`- [ ]`) items, report that nothing
   is deferred and stop.
2. Group the unticked items by theme — related items from different plan
   sections belong together. Keep each item's source plan and date (from
   its `## <plan> — <date>` section header) attached.
3. Classify each group as **actionable now** or **still blocked**, judging
   only from each item's recorded reason for deferral.
4. Propose the top promotion candidates: which items or groups deserve to
   become a new spec. Present a short ranked list with one-line reasoning
   each.
5. If the user selects candidates, use the brainstorming skill with the
   selection as the idea — promotion means a new spec through the normal
   design cycle.
