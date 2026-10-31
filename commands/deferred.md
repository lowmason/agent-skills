---
description: Triage specs/deferred_items.md — group unticked items, then sort each into retire / quick fix / plan / design / hold so the ceremony matches the item; brainstorming only for items that record an open design decision
disable-model-invocation: true
# cc-guide: skills.frontmatter commands.overview @2.1.306
---

Triage the deferred-work backlog in the current project. The triage pass
(steps 1–4) is read-only. Edits to `specs/deferred_items.md` happen only in
step 5, only for items the user selected, and only in the forms step 5
names. The one exception is the archive run that ends step 5: it moves ticked
items the user did not select. Ticking items implemented by a plan remains the
job of that plan's completion-protocol run.

Scope: unticked (`- [ ]`) items in `specs/deferred_items.md`. Live roadmap
stages (`specs/*-roadmap.md`) are out of scope — the roadmap is its own
backlog (derive-roadmap's gap rubric records the same boundary).

1.–4. Run the **Triage rubric** in the writing-plans skill's
   `references/deferred-backlog.md` (steps 1–4: read, group, sort into
   retire / quick fix / plan / design / hold, present). Those four steps are
   read-only, and an agent may run them unprompted — this command exists to
   carry them through to step 5, which an agent may not run.
5. Act only on what the user selects, per disposition. Write each note on
   one line, in the forms of **Item notes** in the writing-plans skill's
   `references/deferred-backlog.md`.
   - **Retire** → tick the item in place:
     `- [x] … → retired <YYYY-MM-DD>: <one-line why>`.
   - **Quick fix** → fix it under the house disciplines
     (test-driven-development for code, verification-before-completion
     before claiming done), then tick the item:
     `- [x] … → done <YYYY-MM-DD> (/deferred quick fix)`.
     Items you defer instead of fixing follow the **Deferred-item schema**
     in the writing-plans skill's `references/deferred-backlog.md`.
   - **A Retire or Quick fix tick note that names follow-up work** carries a
     marker (**Markers** in the same reference). Append the item under the
     schema and add `→ item: <section heading>`, or add `→ dropped: <why>` only
     on the user's word.
   - **Plan** → use the writing-plans skill with the selected items as the
     requirements; name the plan for the theme, since there is no spec.
     Name the picked items in the hand-off, so the session that commits the
     plan writes `→ planned <YYYY-MM-DD>: <path>` on them. That plan's
     completion protocol ticks the items.
   - **Design** → use the brainstorming skill with the selection as the
     idea — a new spec through the normal design cycle. Name the picked
     items in the hand-off, so the session that commits the spec writes
     `→ planned <YYYY-MM-DD>: <path>` on them.
     For Plan and Design, write `→ planned` yourself only when that file is
     committed in this same pass.
   - **Hold** → on the user's word only, write a note on the item:
     `→ held <YYYY-MM-DD>: <condition>` for a condition outside the owner, or
     `→ owner-only <YYYY-MM-DD>: <what the owner must do>` for work only the
     owner can discharge. Restate the blocking condition in the report.
   - **Triggered** → not a disposition. For each item the user selects from
     the proposed `→ triggered` notes (rubric step 3), whatever its
     disposition, write `→ triggered <YYYY-MM-DD>: <what happened>`. A fired
     signal never makes the item Retire.

   End the pass by running the writing-plans skill's
   `scripts/archive_deferred.py` with `uv run`. It moves ticked items more
   than 45 days old, and removed items, to `specs/completed/deferred_items.md`.
   If it holds an item back, tell the user which one. On their word, resolve
   the listed text as **Markers** says and run it again. Commit both files
   with the pass's other edits.
