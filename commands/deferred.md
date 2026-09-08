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

1.–4. Run the **Triage rubric** in the writing-plans skill's
   `references/deferred-backlog.md` (steps 1–4: read, group, sort into
   retire / quick fix / plan / design / hold, present). Those four steps are
   read-only, and an agent may run them unprompted — this command exists to
   carry them through to step 5, which an agent may not run.
5. Act only on what the user selects, per disposition:
   - **Retire** → tick the item in place:
     `- [x] … → retired <YYYY-MM-DD>: <one-line why>`.
   - **Quick fix** → fix it under the house disciplines
     (test-driven-development for code, verification-before-completion
     before claiming done), then tick the item:
     `- [x] … → done <YYYY-MM-DD> (/deferred quick fix)`.
     Items you defer instead of fixing follow the **Deferred-item schema**
     in the writing-plans skill's `references/deferred-backlog.md`.
   - **Plan** → use the writing-plans skill with the selected items as the
     requirements; name the plan for the theme, since there is no spec.
     That plan's completion protocol ticks the items.
   - **Design** → use the brainstorming skill with the selection as the
     idea — a new spec through the normal design cycle.
   - **Hold** → no edit; restate the blocking condition in the report.
