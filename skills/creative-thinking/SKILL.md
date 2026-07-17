---
name: creative-thinking
description: >
  Use when the target itself is fuzzy: "something interesting in this data
  but I can't articulate the analysis", "what should I even be estimating",
  "the true objective is too expensive to evaluate — what cheap target
  stands in", every design a flavor of one idea, or brainstorming's
  propose-approaches step running thin. Named goal: brainstorming. Objective
  chosen: tune-hyperparameters. Model-family or chart choice for a defined
  question: recommend-probabilistic-model, recommend-visualization.
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
---

# Creative Thinking

Divergent target-finding. When the goal itself is fuzzy — the analysis, the
estimand, the objective, or the approach space — the first deliverable is a
map of genuinely distinct candidate targets, in full or in preview. The map
runs ahead of brainstorming's first narrowing question and ahead of any
tuning mechanics, because both presuppose a candidate space the user has
already seen; once the user picks, converging the target is the roster's job.

## The deliverable: the map

These parts, in this order — one message when part 1 resolves its own
gate, two when it asks first. In a repo, glance at specs/ and
specs/deferred_items.md first: a deferred item may already name a candidate.

1. **The gate.** When a question gates the map's shape, sort it by where
   its answer lives. An answer only the user holds — data access, intent,
   which decision consumes the output, what exists or has already been
   tried — gets asked before the full map, with a preview attached: one
   line per candidate direction, at least three directions, noting which
   depend on the answer; sketches, criteria, and check-in follow the
   answer. Asking was never the failure; a bare question that withholds
   the map is, as is a guess that spends the map on dead branches — the
   preview cures one, the round-trip the other. A modeling judgment gets
   the likely answer stated, the map built on it, and the candidates that
   flip under the other answer marked. The sort is settled by the
   conversation, not by guessability: a question is a judgment only once
   the user-held facts feeding it are already on record — which vintage
   counts as truth is a judgment after the consuming decision has been
   named, and user-held before then. A stated deliverable form (write-up
   vs data product) names no consuming decision: who acts on the number,
   and against what, stays open until said. An open user-held question leads the
   message even when every candidate would survive its answer, because
   the answer re-weights the map, and a guessed weighting reads as a
   finished recommendation. A
   fact or question that invalidates several candidates at once (a source
   that leaks under any CV scheme, an archive that may not exist) is gate
   material: it rides with the gate questions, not inside one candidate's
   sketch, where a map-level risk shrinks to a local caveat. A question
   that only refines one candidate waits until that candidate is picked.
2. **The candidates.** 5–8 by default; 3–6 when the candidates are cheap
   stand-ins for an expensive true objective. Each gets a name, the axis it
   flips relative to its neighbors, and one trade-off — three lines or
   fewer, because an 80-word essay per candidate prices the reader out of
   comparing them. Observing that several distinct readings or analyses
   exist is itself a map claim: the same message enumerates them. Promote
   to candidates the criteria that would otherwise be smuggled in as gates
   or regularizers — a constraint someone plans to penalize is usually a
   target someone could optimize.
3. **Selection criteria.** 2–4 named criteria, applied at one line per
   candidate — decision value, data sufficiency, effort, novelty are a
   common set; fidelity to the true objective, evaluation cost, and gaming
   resistance suit stand-in objectives — or a single discriminating
   question keyed to the user's use case. The user needs a named way to
   weigh the map, not just its entries.
4. **One deferral line** for machinery that waits on a target, e.g. "CV
   design and search mechanics: deferred until a target is chosen —
   tune-hyperparameters."
5. **The check-in.** Hand the pick to the user, candidates in neutral
   order. A lean is welcome when its wording carries the tentativeness —
   the worked example closes with one — not a tag ahead of the sentence.

Part names and move names here are scaffolding, not reader vocabulary:
the gate lands as an ordinary question or a stated assumption, an axis
difference in plain words ("a different data source, not a different
metric"). A reader who has never seen this skill should find nothing in
the message that presumes it — template-shaped phrases get echoed verbatim.

Verdicts, hybrids, taxonomies, and implementation depth follow the user's
pick, at whatever depth the chosen target deserves.

## Widening the map

First-pass candidates usually share an organizing frame — one metric
family, one decomposition, one design parameterized six ways. Name that
frame (a one-line label in the map is enough), then include at least one
candidate the frame cannot generate: a map drawn from one frame reproduces
the frame's blind spot, and the blind spot is usually why the target felt
fuzzy. Three ways to produce that candidate:

- **Shift the output shape** — when every candidate outputs the same type
  of thing: level → change, point → distribution or exceedance, error
  score → pass/fail verdict, forecast → anomaly flag or ranking.
- **Swap the data pairing** — when the map silently assumes the evidence
  at hand: a different source, join, or granularity; an external
  benchmark; a recorded fixture instead of the live system.
- **Change the paradigm** — when every candidate lives in one paradigm:
  descriptive ↔ predictive ↔ causal ↔ decision; a metric ↔ a cadence or
  process change; a model fix ↔ a data-collection fix.

Two candidates that lead to the same next action are one candidate — keep
the better-named one and spend the slot on another move. When first-pass
candidates arrive already scattered across frames, the map is wide enough;
apply that same next-action check and move on.

## Scope and handoff

This skill ends when the user picks a target:

- Hand the chosen target to brainstorming unchanged — refinement is
  brainstorming's job, so it arrives as the user stated it.
- When invoked mid-brainstorming because its propose-approaches step
  produced flavors of one idea, the deliverable is the same map — widened
  candidates, criteria, check-in — and brainstorming resumes on the pick.
- A picked target that is an objective to search over goes to
  tune-hyperparameters; a defined question choosing a model family goes to
  recommend-probabilistic-model; a defined dataset choosing a chart goes
  to recommend-visualization.
- When a candidate's sketch needs data facts (does the join exist, is the
  panel balanced), state them as one-line assumptions on that candidate
  rather than blocking the map; explore-data profiles unfamiliar data and
  bls-data-context supplies program facts — point to them rather than
  loading them mid-map, since each is heavy enough to be the user's call.

## Worked example — choosing a stand-in objective

> "Tuning a state-employment nowcast that feeds monthly directional
> staffing calls. The true objective — error against the fully benchmarked
> data — arrives about 21 months late. What do I tune against meanwhile?"

Whether vintages of the official series were ever recorded is a fact only
the user holds, and it decides two directions at once, so the first
message asks with the whole space in view:

"Do you keep, or could you cheaply build, an archive of the official
series' vintages? It decides two of these six: error vs the latest
official series; error vs a frozen vintage panel (needs the archive);
revision-direction hit rate (needs it too); cross-state rank agreement
with a sibling series; stability under resampling; a small pre-registered
grid scored annually on the true objective."

After "no archive, and not worth building this year," those two drop.
Which vintage counts as truth is a judgment the map absorbs: the calls
are graded against the benchmark, so that is the assumed yardstick.

1. **Error vs latest-available official series** — cheapest, monthly;
   treats revision noise as signal. Were the first release the yardstick
   instead, this would be nearly the true objective itself.
2. **Cross-state rank agreement with a sibling series** — differs by
   evidence, not by metric; robust to level bias, and blind to it.
3. **Nowcast stability under resampling** — needs no ground truth;
   measures reliability, not accuracy.
4. **Pre-register a small grid, score on the true objective annually** —
   changes the cadence rather than the metric; slowest feedback, no
   leakage risk.

On fidelity to the benchmark, 1 leads, then 2; 3 stands outside the
comparison. 1–3 score monthly, 4 annually; effort is lowest for 1 and 3.
CV design and search mechanics wait until a target is chosen —
tune-hyperparameters. If pressed today I'd start with 1 read as sign of
change — but does the decision compare each state to its own past, or
states to each other?
