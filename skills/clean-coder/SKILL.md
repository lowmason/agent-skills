---
name: clean-coder
description: >
  Use when editing, fixing, or refactoring existing Python — before touching code near the
  task. Trigger on: applying cleanups to code you are already editing; noticing adjacent
  code that could be improved; "while you're at it", "any quick wins", "clean this up too",
  "anything else obviously wrong", "just make it clean"; the urge to fix a smell you
  spotted outside the task's scope; deciding whether a cleanup shares a commit with a
  behavior change; or a small tidying starting to cascade into further tidyings.
license: MIT
metadata:
  author: Lowell Mason
  version: '1.0'
---

# Clean Coder

## Overview

Leave each file you touch a little cleaner than you found it — proportional to the task,
one small improvement per edit, never a crusade. This is litter-pickup (Fowler's
opportunistic refactoring), not a refactoring project: the task stays primary and cleanup
rides along only where it serves the task.

Standards come from the clean-code skill (the curated catalog, cited by rule code). This
skill governs *when you may apply them*.

**Violating the letter of the Gate is violating the spirit of the Gate.**

## The Confirmation Gate

Before any cleanup edit, classify it. Everything hinges on this:

**In-scope** — the lines the task requires you to change, and the function(s) those lines
live in. Apply clean-code standards directly. No confirmation. Cite each fix by rule code
in your report.

**Out-of-scope / adjacent** — everything else in the file or repo, however small. All
four steps, in order:

1. **Announce** — say clean-coder is engaged and you noticed adjacent cleanups.
2. **List** — each proposal as `file:line — rule code — one-line description`.
3. **Ask** — request a yes/no per item.
4. **Apply only on an explicit yes.** Declined or unanswered → the code stays exactly as
   it was. No re-proposing in the same session. No applying "a different version" of a
   declined edit.

Blanket phrases are not consent. "Do whatever", "just make it clean", "use your
judgment", "handle it as you see fit", "don't ask me questions" — none of these authorize
a specific out-of-scope edit. They change nothing: in-scope fixes proceed as always;
out-of-scope items still get listed and still wait for a yes. When the user said not to
ask questions, put the list at the end of your report and apply none of it.

## Tidy vs. behavior — never in one commit

From Beck's *Tidy First?*:

- A **tidying** changes structure, not observable behavior: rename, extract a constant or
  explanatory variable, reorder declarations, delete a redundant comment.
- A **behavior change** alters what the code does: bug fix, new logic, changed output.

Rules:

- One commit holds exactly one kind. A sequence may interleave (`SSSSBBSB`), a single
  commit never mixes.
- A tidying needs **no new test**, but must be provably behavior-preserving: run the
  suite before and after — identical results (a red suite must stay identically red).
- A behavior change gets a failing test first — the test-driven-development skill
  governs.

## The stopping rule

One tidying reveals another; that is the trap, not a license.

- If tidying starts to eat the task instead of serving it — stop.
- More than roughly an hour of accumulated tidying before any behavioral change means you
  have lost track of the minimum set — stop, keep what is committed, defer the rest.
- Deferred findings go to the tech-debt skill's audit-and-backlog process, not to "later
  in this session".

## Boundary with tech-debt

clean-coder is edit-triggered and incremental; it produces **no backlog**. When you
notice something bigger than an opportunistic fix — a duplicated module, a notebook that
needs extraction, a security finding, anything past the stopping rule — stop, name it in
your report, and defer to the tech-debt skill. Do not fix it in-flow even if invited to:
it needs the audit treatment (DELETE-vs-HARDEN, prioritization), not a drive-by.

## Routing

| About to… | Open |
|---|---|
| Name or rename anything | clean-code references/names.md |
| Delete, rewrite, or add a comment | clean-code references/comments.md |
| Split, extract, or judge a function | clean-code references/functions.md |
| DRY, magic numbers, conditionals, method chains | clean-code references/general.md |
| Add or judge tests | clean-code references/tests.md |

## Report format

Cite every applied fix by rule code; keep proposals separate from applied fixes:

    Fixed: extracted HTTP_TOO_MANY_REQUESTS (G25) — etl/fetch.py:11
    Proposed (awaiting yes): fetch_page retry count → named constant (G25) — etl/fetch.py:9

## Rationalizations

| Excuse | Reality |
|---|---|
| "It's a tiny change, I'll just fix it" | Out-of-scope tiny changes still go through announce → list → ask. Size is not scope. |
| "They said 'do whatever' / 'make it clean'" | Blanket words are not per-item consent. List and ask. |
| "I'm already in this file" | File proximity is not scope. The task defines scope. |
| "It's the same kind of fix I did in-scope" | Same rule, different scope. The Gate is about *where*, not *what*. |
| "Asking would interrupt their flow" | The list costs one message. An unrequested refactor costs trust and review time. |
| "I'll bundle the tidy-up into the fix commit — it's related" | Related is not same-kind. Tidy and behavior never share a commit. |
| "This duplication is small enough to consolidate now" | Module-level duplication is a tech-debt finding. Name it, defer it. |
| "The user declined, but this variant is different" | Declined means untouched. Any variant of the edit is the same edit. |
| "Same category as something they already declined" | A decline covers the item declined, not its category. In-scope work still needs no confirmation — fix it. |
| "This is the minimal change that fixes it" | Minimal means the smallest *complete* fix. In-scope cleanup the task calls for isn't an optional extra. |
| "That's already correct, no need to touch it" | Declaring code clean isn't applying the rule. In-scope and rule-flagged means fix it. |
| "It's just repo hygiene — untracked cruft" | Category doesn't exempt an edit from the Gate. Out-of-scope hygiene fixes still get announced and asked. |
| "I left it untouched and flagged it for follow-up" | Check the diff before you write that. A claimed restraint the diff contradicts is worse than the edit itself. |
| "Fixing that in-scope smell would change behavior — safer to leave it" | The tidy/behavior rule sequences work, it never cancels it: a named constant preserves behavior exactly, and a genuinely behavioral cleanup lands as its own step after the fix. Skipping the in-scope pass is not caution. |
| "There's a literal / a smell, but it's not worth fixing" | In-scope, "worth" is not the test: rule-flagged means fixed and cited. A constant costs one line; re-grading materiality per item is the dodge. |

## Red flags — STOP

- You are editing a line the task does not require and nobody said yes to.
- You are rephrasing a declined cleanup instead of dropping it.
- Your diff touches more functions than the task named.
- Structural and behavioral changes are staged for one commit.
- Tidying has gone on for a while and the task itself has not advanced.
- "While I'm at it…" in your own reasoning — that phrase is the Gate's trigger, never
  permission.
- Your report cites no rule code for a function you edited — the in-scope pass was
  skipped. Run the routing table over the lines you touched before reporting.
- A proposal in your list has no rule code — open the routing table's reference and
  cite one, or drop the item.

Any of these → stop and re-enter the Gate: announce, list, ask.

## Interactions

- **test-driven-development** — behavior changes get a failing test first; tidyings keep
  the suite's results identical (run it before and after).
- **tech-debt** — receives everything past the stopping rule; the batch-audit
  counterpart to this skill's in-flow mode.
- **verification-before-completion** — the report's cited fixes must match the diff.
