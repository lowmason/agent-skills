---
name: derive-roadmap
description: >
  Use when a spec opens with a header naming derive-roadmap as the required
  next skill, when resuming staged work ("resume the roadmap", a
  specs/*-roadmap.md file), when comparing a spec against the current
  implementation to stage what remains, or when a project with nothing built
  yet needs its stages laid out ("lay out the stages", "roadmap this new
  project", outcomes or a progression to rank and stage). Partitions gaps or
  outcomes into staged spec-to-plan cycles. Never plans or brainstorms a stage
  itself.
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
# cc-guide: lean.session-hygiene @2.1.306
---

# derive-roadmap

## Overview

Takes a Design Spec and the system it describes, and partitions the distance
between them into stages. Each stage is one spec→plan→implementation cycle
producing working, testable software — or, for a stage that answers a
question rather than builds, a written finding (§2).

**Core principle:** the roadmap routes; it never designs. Every stage exits
to brainstorming or writing-plans by bare name. This skill does not plan a
stage, and does not brainstorm one. Listing, splitting, ranking and costing
a new project's outcomes is partitioning, not design.

**Entry, in this order** — a spec's filename can echo a roadmap's without
being one, so resolve by header, not by name:

1. The document carries the roadmap header ("REQUIRED SKILL: derive-roadmap
   — resume via its reconcile step", `references/roadmap-format.md`) → §5,
   Resume. Resume reconciles an artifact that already exists, against stage
   stamps that are authoritative; fresh entry re-derives the partition from
   scratch. When a document could be read either way, resuming first is the
   safe direction — routing a live roadmap into fresh entry discards the
   reconciliation §5 exists to do.
2. Your partner asks for a roadmap for a project that has nothing built
   (below), or gives its outcomes or its stages in their own words, with or
   without a spec → §7, New-Project Entry.
3. The document carries the Synthesize-mode routing header ("REQUIRED NEXT
   SKILL: derive-roadmap", describe-critique-methodology's
   `spec-synthesis.md`) → §1, Gap analysis.
4. An explicit request to compare a spec against the implementation, with no
   roadmap header present → §1, Gap analysis.

A filename ending in `_roadmap`, or merely resembling `specs/*-roadmap.md`,
does not make a document a roadmap — only the header does.

**Nothing built** means that no outcome of the system the spec or request
describes works end to end on real data yet. Judge that system, not the whole
repository, and do not count code that only acquires inputs, such as
downloads, as a working outcome.

## 1. Gap analysis — ONCE, at entry

Classify EVERY numbered spec requirement into one of five verdicts using
`references/gap-rubric.md`:

- implemented-as-specified
- implemented-differently
- missing
- in-code-but-not-in-spec
- out-of-repo

Read `specs/deferred_items.md` if it exists — its unticked entries are
pre-existing stage candidates. The /deferred command owns promotion logic;
read it, never duplicate it.

Surface contradictions and ambiguities as ONE batched question set before
writing any roadmap text. When the session cannot ask (a non-interactive or
sub-agent run), put the questions in a clearly marked block at the top of
the artifact and label the artifact provisional; the §4 checkpoint still
gates before stage 1.

**NOTHING BUILT.** When the table shows nothing built (Overview), do not
partition. Add one item to the batched question set: what you found (which
rows are implemented, and why none of them is a working outcome), and an
offer to stage the project through the New-Project Entry (§7), with the
spec's requirements as outcome candidates. Then wait for the answer: never
switch on your own. On a yes, go to §7. On a no, partition as below. When the
session cannot ask, the offer goes in the questions block and the provisional
file partitions as below. The table is the whole test: no other check decides
that a repository is only a scaffold.

**SINGLE-STAGE EXIT.** If the gaps fit one spec→plan cycle, write NO roadmap
file. Say so, hand directly to brainstorming (open design space) or
writing-plans (spec-determined), and record the decision in the spec's
Rollout note. A roadmap for one stage is overhead with a filename.

## 2. Stage partition

One stage = one spec→plan→implementation cycle producing working, testable
software — writing-plans' Scope Check transposed up a level. An
investigation stage is the one exception: its exit artifact is a written
finding rather than software, but it is still a genuine spec→plan cycle,
staged and routed like any other.

Sequence by **dependency and information order**, not by spec section order
and not by the critique's priority tiers. A cheap question whose answer
changes a later stage's parameters goes first, even when it ranks low on
value — this is the case an investigation stage exists for. Say plainly
whether your order follows or diverges from the spec's own ranking, and
why — agreement is itself the most useful signal about the partition, and
saying nothing reads as if no comparison happened at all.

## 3. The roadmap artifact

`<name>` is the spec's own filename stem (drop the path and `.md`) — used
whole, never stripped, even when the stem already ends in `roadmap`.

Before writing, scan `specs/` for any file carrying the roadmap header
(condition 1 above) that names this spec as its source. If one exists,
STOP — do not write — and surface it: the right move is Resume (§5),
whatever its filename. A user calling a headerless document "the roadmap"
is the same case: say the header is missing and confirm before treating
this as fresh entry.

Write `specs/<name>-roadmap.md` in the target repo per
`references/roadmap-format.md`. Hard brevity budget: cite spec §-refs, never
restate requirement text — writing-plans copies constraints verbatim later,
and a roadmap that restates them is a second source of truth that will drift.

## 4. Human checkpoint, then stop

Present the stage partition for approval before stage 1. On approval, hand
off the first stage per its ROUTING line, by bare skill name, in a fresh
session — then STOP.

Between stages, the completed stage's execution session recommends resuming
the roadmap, and your human partner decides by launching the resume. Never
volunteer a stage outside a resume.

**Handing off a stage**, after §4's approval or §5's reconcile:

- The next stage is the first unticked one whose `Consumes` are all met.
- End with "Next: /clear (or a fresh session), then <ROUTING skill> on Stage N
  of `specs/<name>-roadmap.md`", and quote the line the receiver carries,
  `Roadmap: specs/<name>-roadmap.md, Stage N`:
  - ROUTING brainstorming: the new stage spec's Rollout note carries the
    `Roadmap:` line.
  - ROUTING writing-plans: the plan header carries it, and the plan is scoped
    to the stage entry's `Spec` refs, or its `Outcomes` refs in a new-project
    roadmap. This covers a stage with no stage spec.
- Then stop. Launching that session is your human partner's go/no-go. A
  go-ahead, or a request to keep going, approves that fresh session and
  nothing more: never plan, spec or brainstorm the stage in a resume session.
  Repeat the "Next:" line and stop.

## 5. Resume (reconcile)

On re-entry, for each stage: the stage stamp under its roadmap entry
("Stage N: COMPLETE (date) — implemented by plan <id> (path)") is
authoritative. A fuzzy match against `specs/plans/completed/` is FALLBACK
only — never let it overrule a stamp.

For each stage stamped COMPLETE since the last resume, read the stamp and its
plan's `## Handoff to later stages`. Re-validate every unticked stage against
what actually shipped:

- **Amend.** When a Handoff bullet changes a later stage's `Spec`, `Consumes`,
  `Produces` or `Exit`, amend that entry: cite `plan <id>, Handoff`, mark each
  settled point `(Resolved at resume, YYYY-MM-DD)`, and never restate.
  Amend only from Handoff bullets: a section reading `None`, or a plan with
  none, changes no later entry; a shipped difference no bullet names goes to
  the Ask.
- **Ask.** A stage added, split, dropped or reordered is not an amendment. Put
  every such change to your human partner as ONE question, not a numbered
  list: state the changes with your proposed default and ask for a single
  approve-or-amend. Name no stage's routing in it; route only after the
  answer.
- **Commit** the amendments, and whatever your partner approved at the Ask,
  on the current branch before the handoff, so the
  fresh session reads them. Context for a later stage that cannot be
  committed goes to prepare-handoff.

Then hand off the next stage (§4). With every stage ticked, go to §6.

**Parking is a first-class exit.** Remaining unticked stages append to
`specs/deferred_items.md`, one item per stage, under a dated
`## <roadmap-name> — <YYYY-MM-DD>` section. Each item follows the
Deferred-item schema in the writing-plans skill's deferred-backlog reference
(self-contained, with `Size:` and a `Done when:` naming the stage's Produces),
so the item ages and reaches the aged-tail gate. The roadmap moves to
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

## 7. New-Project Entry

For a project with nothing built (Overview). Read
`references/new-project-entry.md` before your first message: it holds the
inputs, the checks you may run, and each rule below in full.

1. **Outcomes.** Write the outcomes as a numbered list (O1, O2, …), one line
   each, in plain words: what your partner gets, not how it is built. They
   come from your partner's words, or from a spec's requirements as
   candidates. Background files give facts, options and costs, and never add
   an outcome on their own.
2. **Tracks.** Group the outcomes into tracks. Outcomes that answer unrelated
   questions, or serve different uses, go in separate tracks, and you say why
   you split them. Catching a bundled request is your job, not your
   partner's. Each track is a known progression (your partner can name its
   stages from first to last) or research (the method or the answer is open).
3. **Cost.** Each outcome whose cost is material gets a rough estimate and its
   basis. When only running the work can tell, say so.
4. **One message.** Before any roadmap text, send one message: the outcome
   list, unranked, with the cost notes, the tracks and their kinds, and a
   proposed roadmap name. It makes one request: rank the outcomes within each
   track and the tracks among themselves, and confirm the tracks. Do not rank
   for your partner unless they ask.
5. **Stages.** Each track's first stage is its core stage: it works on real
   data at the smallest standard that gives a usable result, and its Exit
   names the measured cost of the real run. A known-progression track commits
   every stage, first to last, its later hardening stages included. A research
   track commits its core stage only, and its other outcomes wait in its
   Ranked list until the core has run on real data. A quality the project
   needs eventually but not to work goes to a named later stage or a
   Ranked-list item, never into a core stage's Exit.
6. **Write, then §4.** Write the roadmap per `references/roadmap-format.md`
   (New-project roadmaps), then present the partition for approval (§4).

## Quick reference

| You have | Do |
|---|---|
| A spec carrying the Synthesize-mode header (`REQUIRED NEXT SKILL`) | Gap analysis → partition → roadmap, or single-stage exit |
| Your partner's outcomes or stages for a project with nothing built | §7: outcomes, tracks, cost notes, one message, then stages |
| A gap table that shows nothing built | Offer §7 in the batched questions, then wait for the answer |
| A research track with its committed stages ticked and a Ranked list waiting | Report the core's finding and cost, then one re-rank question (§5) |
| Gaps that fit one cycle | NO roadmap file — hand to brainstorming or writing-plans |
| A document carrying the roadmap header (`REQUIRED SKILL … resume via its reconcile step`) | Reconcile via stamps and Handoff sections, amend and commit, then hand off the next stage |
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
- **Exit criteria that restate the requirement** — exit criteria name
  observable outcomes, not intentions.
- **Writing a roadmap for one stage** — take the single-stage exit.
- **Trusting a fuzzy plan-name match over a stage stamp** — the stamp wins.
- **Switching to §7 on your own** — when the table shows nothing built,
  offer it and wait for a yes.
- **Ranking outcomes for your partner** — show the list unranked; the ranking
  is their judgment of value.
- **A final-standard quality in a core stage's Exit** — manifests,
  traceability and the like go to a named later stage or a Ranked-list item,
  recorded in `Leaves out`.
