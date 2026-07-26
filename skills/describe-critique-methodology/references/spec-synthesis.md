# Synthesize mode — triage and spec format

## Critique triage table

Before any spec text, present ONE batched table covering every numbered
critique point:

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

## Locators

Every requirement cites its origin inline: `(methodology §N)` and/or
`(critique C7)`, plus the triage verdict where it was not a plain accept.
A requirement with no locator is a new idea — route it to brainstorming
instead of smuggling it into the synthesis.

## Routing header

The spec's first line after the title, verbatim:

> For agentic workers: REQUIRED NEXT SKILL: derive-roadmap — do not plan
> this spec directly and do not split it into per-subsystem plans.

## Self-review, gate, handoff

Run the four checks (placeholders, internal consistency, scope, ambiguity);
fix inline. Then the scripted user gate, then hand off to derive-roadmap by
bare name in a fresh session — and stop.
