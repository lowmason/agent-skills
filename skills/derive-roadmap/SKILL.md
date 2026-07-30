---
name: derive-roadmap
description: >
  Use when a spec opens with a header naming derive-roadmap as the required
  next skill, when resuming staged work ("resume the roadmap", a
  specs/*-roadmap.md file), or when comparing a spec against the current
  implementation to stage what remains. Partitions gaps into staged
  spec-to-plan cycles. Never plans or brainstorms a stage itself.
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
---

# derive-roadmap

## Overview

Takes a Design Spec and the system it describes, and partitions the distance
between them into stages. Each stage is one spec→plan→implementation cycle
producing working, testable software.

**Core principle:** the roadmap routes; it never designs. Every stage exits
to brainstorming or writing-plans by bare name. This skill does not plan a
stage, and does not brainstorm one.

**Entry, in this order** — a spec's filename can echo a roadmap's without
being one, so resolve by header, not by name:

1. The document carries the roadmap header ("REQUIRED SKILL: derive-roadmap
   — resume via its reconcile step", `references/roadmap-format.md`) → §5,
   Resume. Resume reconciles an artifact that already exists, against stage
   stamps that are authoritative; fresh entry re-derives the partition from
   scratch. When a document could be read either way, resuming first is the
   safe direction — routing a live roadmap into fresh entry discards the
   reconciliation §5 exists to do.
2. The document carries the Synthesize-mode routing header ("REQUIRED NEXT
   SKILL: derive-roadmap", `spec-synthesis.md`) → §1, Gap analysis.
3. An explicit request to compare a spec against the implementation, with no
   roadmap header present → §1, Gap analysis.

A filename ending in `_roadmap`, or merely resembling `specs/*-roadmap.md`,
does not make a document a roadmap — only the header does.

## 1. Gap analysis — ONCE, at entry

Classify EVERY numbered spec requirement into one of four verdicts using
`references/gap-rubric.md`:

- implemented-as-specified
- implemented-differently
- missing
- in-code-but-not-in-spec

Read `specs/deferred_items.md` if it exists — its unticked entries are
pre-existing stage candidates. The /deferred command owns promotion logic;
read it, never duplicate it.

Surface contradictions and ambiguities as ONE batched question set before
writing any roadmap text.

**SINGLE-STAGE EXIT.** If the gaps fit one spec→plan cycle, write NO roadmap
file. Say so, hand directly to brainstorming (open design space) or
writing-plans (spec-determined), and record the decision in the spec's
Rollout note. A roadmap for one stage is overhead with a filename.

## 2. Stage partition

One stage = one spec→plan→implementation cycle producing working, testable
software — writing-plans' Scope Check transposed up a level.

Sequence by **dependency and information order**, not by spec section order
and not by the critique's priority tiers. A cheap question whose answer
changes a later stage's parameters goes first, even when it ranks low on
value. Say plainly when your order diverges from the spec's own ranking, and
why.

## 3. The roadmap artifact

`<name>` is the spec's own filename stem (drop the path and `.md`) — used
whole, never stripped. Do not remove a trailing `roadmap` token to dodge a
name like `..._roadmap-roadmap.md`: for a spec whose filename already ends
in `roadmap`, that stripping re-suffixes the stem to within one character of
the input's own filename (a hyphen where the input has an underscore, or an
exact match if the input already used a hyphen) — precisely the case this
rule has to survive. Appending `-roadmap` to the untouched stem is what
keeps the two paths apart, by construction, every time.

Before writing, check whether `specs/<name>-roadmap.md` already exists. If it
does, STOP — do not write it. Surface the collision to the user instead: if
the existing file is this spec's own roadmap, the right move is Resume (§5),
not a fresh Gap analysis.

Write `specs/<name>-roadmap.md` in the target repo per
`references/roadmap-format.md`. Hard brevity budget: cite spec §-refs, never
restate requirement text — writing-plans copies constraints verbatim later,
and a roadmap that restates them is a second source of truth that will drift.

## 4. Human checkpoint, then stop

Present the stage partition for approval before stage 1. On approval, hand
off the first stage per its ROUTING line, by bare skill name, in a fresh
session — then STOP.

The between-stages go/no-go is user-initiated via "resume the roadmap". Do
not volunteer the next stage.

## 5. Resume (reconcile)

On re-entry, for each stage: the stage stamp in its spec's Rollout note
("Stage N: COMPLETE (date) — implemented by plan <id> (path)") is
authoritative. A fuzzy match against `specs/plans/completed/` is FALLBACK
only — never let it overrule a stamp.

Re-validate every unticked stage against what actually shipped, then route
the next one per its ROUTING line.

**Parking is a first-class exit.** Remaining unticked stages append to
`specs/deferred_items.md` as self-contained items; the roadmap moves to
`specs/completed/` marked `PARKED (date) — N of M stages complete`. The
methodology and critique files retire alongside the synthesized spec — they
are its inputs.

## 6. Roadmap-completion review

Retirement is gated behind a conformance audit of the ACCUMULATED system:
re-run the gap rubric over every numbered requirement, with evidence per
verdict (implementing stage/plan, Deviation notes, deferred_items entries).

Unmet requirements exit exactly two ways: a new stage (roadmap stays live),
or conscious deferral with a written why.

This is NOT a whole-roadmap code-diff review — stages merged separately and
code quality was reviewed per stage.

Optional independent check: re-run describe-critique-methodology's Describe
mode on the refactored system and diff the fresh description against the
spec. That is a re-derivation, not a self-assessment, and it is the natural
input to the next critique round.

When improvement directions are diffuse, route to creative-thinking.

## Quick reference

| You have | Do |
|---|---|
| A spec with the derive-roadmap header | Gap analysis → partition → roadmap, or single-stage exit |
| Gaps that fit one cycle | NO roadmap file — hand to brainstorming or writing-plans |
| A `specs/*-roadmap.md` and "resume" | Reconcile via stamps, route the next unticked stage |
| Every stage ticked | Completion review, then retire |
| A stage to actually build | Not this skill — brainstorming or writing-plans, by bare name |

## Common mistakes

- **Planning the spec wholesale** — one plan for everything is the failure
  this skill exists to prevent. Partition first.
- **Designing a stage** — writing its tasks, its tests, or its approach.
  Route to writing-plans; stop there.
- **Restating requirements** — cite `§`; never copy requirement prose into
  the roadmap.
- **Sequencing by the spec's own priority ranking** — value order is the
  right way to rank recommendations and the wrong way to sequence work.
  Dependencies and cheap information-gathering come first.
- **Exit criteria that restate the requirement** — an exit criterion names
  an observable outcome, not an intention.
- **Writing a roadmap for one stage** — take the single-stage exit.
- **Trusting a fuzzy plan-name match over a stage stamp** — the stamp wins.
