# Synthesize mode — triage and spec format

## Critique triage table

**First: was the critique adjudicated at all?** The prompt asks Chat for the
positions reached after interactive push-back. A critique taken as a first
pass — no push-back — carries none: no point marked rejected, no record of
positions reached. Detect that and say so above the table — the signal is the
absent push-back, not an absent routing header or missing C-numbers, which
only mean the critique predates this skill. The adjudication then happens
here: make the calls yourself with a rationale each, rather than forwarding
the critique to the user as questions. There are no Chat-side rejections to
inherit, so never read their absence as agreement; reserve
needs-user-adjudication for what genuinely turns on the user's priorities.

Before any spec text, present ONE batched table covering every critique
point:

| # | Critique point (one line) | Verdict | Rationale (one line) |
|---|---|---|---|

Verdicts: **accept** / **reject** / **needs-user-adjudication**. Ask every
needs-user-adjudication question in the same message as the table — one
batched set, never a drip. Rejected-by-Chat points (recorded as rejected in
the critique) default to reject here; overturn only with a rationale.

## Spec format

The synthesized spec uses the house skeleton: summary paragraph, Motivation,
Core principle (when one exists), numbered Requirements with
(chosen)/(rejected) alternatives inline, Verification (observable outcomes),
Out of scope, Rollout note. Do not reinvent the skeleton — before writing
your first synthesized spec, read two retired exemplars in the agent-skills
repo's `specs/completed/` directory (that repo owns the house format; this
file cites it rather than restating it).

A third inline marker, **(open)**, carries a decision that turns on a matter
of fact about a system outside this repo — settled by checking, not by
argument (*is the downstream likelihood Gaussian or Student-t?*). Write it
self-describing, naming its own discharge mechanism:
`(open — resolved by verification, not argument)`. Every (open) item MUST be
discharged by a named Verification bullet, and one that blocks others opens
the Rollout note. In triage such a point is an **accept** whose requirement
carries the marker — not a needs-user-adjudication, which assumes the user
can settle it.

## Locators

After the routing header and the summary paragraph, place a **Design
provenance** paragraph naming both source files and declaring the locator
scheme in use. Default scheme:
`(methodology §N)` and `(critique C7)` — the critique prompt makes Chat
number its points C1..Cn, so a critique produced through this skill has
them. A foreign or pre-skill critique may not; declare whatever scheme its
structure affords (e.g. **M §n** for the description, **R §n** for the
review) and hold to it.

Every requirement cites its origin inline, plus the triage verdict where it
was not a plain accept. A requirement with no locator is a new idea — route
it to brainstorming instead of smuggling it into the synthesis.

## Routing header

The spec's first line after the title, verbatim:

> For agentic workers: REQUIRED NEXT SKILL: derive-roadmap — do not plan
> this spec directly and do not split it into per-subsystem plans.

## Self-review, gate, handoff

Run the four checks (placeholders, internal consistency, scope, ambiguity);
fix inline. Then the scripted user gate, then hand off to derive-roadmap by
bare name in a fresh session — and stop.
