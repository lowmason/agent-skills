# Model selection — choosing the tier

The signal order behind a dispatch-tier choice, and the cost reasoning that
sets the defaults.

SKILL.md § Model Selection carries what must hold on **every** dispatch: the
three tiers and their aliases, the requirement to name a model explicitly, the
`standard` default, and the review floors. Read this file alongside it before
the first dispatch of a plan.

## Why the cheapest tier is not always the cheapest choice

A model that takes 2-3× the turns, or comes back wrong and needs a re-dispatch,
costs more than the tier above it; turn count and rework dominate sticker price.
That is what the two defaults in SKILL.md buy: erring toward the stronger tier
on a genuine toss-up, and defaulting to **standard** when nothing clearly fires
— the floor that absorbs the cost of one wrong cheap pick.

## Choosing the tier — read the signals in order; the first that fires wins

1. **Risk / subtlety** — concurrency, security, data-loss, broad blast radius,
   or debugging from symptoms → **capable**, regardless of file count or diff size.
2. **Source of the work** — the complete code is in the brief (transcription +
   testing) → **cheap**; behavior is described in prose → **standard floor**
   (prose implementers never get the cheap tier).
3. **Spread** — 1-2 files with a clear spec → **cheap**; multiple files /
   integration / pattern-matching → **standard**; open design judgment or
   broad-codebase understanding → **capable**.
