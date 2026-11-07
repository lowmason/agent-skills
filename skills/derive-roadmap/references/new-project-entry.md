# New-Project Entry

SKILL.md §7 gives the steps. This file gives the rules behind each one.

## When you are here

Your partner asked for a roadmap for a project with nothing built (defined in
SKILL.md's Overview), or said yes to the offer that SKILL.md §1 makes when a
gap table shows nothing built. A document that carries the roadmap header
goes to Resume (§5) first, always.

## Inputs

- Your partner's outcomes or progression, in plain words. These are the
  source.
- A spec, when there is one. Its numbered requirements become outcome
  candidates, one line each, for your partner to confirm and rank.
- Background files, when given: research results, a draft spec, notes. Read
  them for facts, options and costs. An outcome that only a background file
  states is a candidate: list it, mark it "from <file>", and let your partner
  confirm it. Background never becomes a requirement list on its own.
- Choices your partner has already made for the whole project, such as the
  language or the platform. Record each in one line. Recording a choice is
  not designing.

## Checks you may run before the message

Only cheap read-only checks: a directory listing, a file-size lookup, a
published limit such as a rate limit, a quota or a price. The message may
also propose one small probe, such as fetching one real file or timing one
model fit, to firm up a cost note. Run a probe only after your partner says
yes. A probe gathers information. It does not design the stage.

## Outcomes and tracks

- One line per outcome: what your partner gets, not how it is built. "On-time
  rates per route for one real month of trip records" is an outcome. "A
  pipeline with a manifest layer" is not.
- Put outcomes in separate tracks when they answer unrelated questions or
  serve different uses, even when one request names them together. Two
  questions are unrelated when either answer stands without the other, even
  when both explain the same result. Whether late trips follow the weather
  and whether they follow the age of the buses are two questions, though both
  explain lateness. Joined, the first outcome waits on the machinery of the
  second. Say why in one line.
- A track is a known progression when your partner can name its stages from
  first to last, and research when the method or the answer is open. One
  project may hold tracks of both kinds. When the kind is unclear, propose one
  and ask in the same message.

## Cost notes

Each outcome whose cost is material gets a rough estimate and its basis.
Material costs include compute hours or dollars, data volume, rate limits and
your partner's time. A basis is a published limit, a file size, or arithmetic
from known figures: "about 4 GB: 12 monthly files of about 330 MB each, from
the listing". When no estimate is possible without running the work, say so:
the track's core stage measures it.

## The one message

Before any roadmap text, send one message that holds:

1. the numbered outcome list, unranked, each line with its cost note;
2. the proposed tracks, each with its kind and, for a split, the reason;
3. the choices already made, one line each;
4. with no spec, a proposed roadmap name, the `<name>` in
   `specs/<name>-roadmap.md` (with a spec, the name is its stem);
5. one request: rank the outcomes within each track and the tracks among
   themselves, and confirm or change the tracks, their kinds and, with no
   spec, the name.

Do not rank for your partner unless they ask: the ranking is their judgment of
value. A list or a table both work. When the session cannot ask, write the
roadmap as a provisional file (SKILL.md §1): rank by the order your partner
gave, or else by the list order, and label the ranking provisional.

## Stages

- **Core stage.** Each track's first stage. It works on real data at the
  smallest standard that gives a usable result, and in a research track it
  delivers the top-ranked outcome end to end. Its Exit names the observable
  result and the measured cost of the real run: time, compute or data volume.
  Its Produces names `specs/<name>-stage-<N>-findings.md`, which records the
  result and the measured cost. Example: a first stage that loads one real
  month of a transit agency's trip records, reports on-time rates per route,
  has no manifest layer, and records how long the month took to load.
- **Known progression.** Commit every stage, first to last, later hardening
  stages included. describe-critique-methodology runs once these stages are
  built, not before.
- **Research.** Commit the core stage only. The track's other outcomes go in
  its Ranked list, in your partner's order, until the core has run on real
  data, because the first results may change the ranking (SKILL.md §5). A
  stage that your partner later promotes from the list also names its own
  findings file in `Produces` and the measured cost of its real run in
  `Exit`, so the next re-rank reads what that stage found and cost.
- **Later qualities.** A quality the project needs eventually but not to work
  goes to a named later stage in a known progression, or to a Ranked-list item
  in a research track. Examples: manifests, traceability, point-in-time
  awareness, full validation suites, scheduling and deployment. Check the
  project against each one, and place every one it will need. A core stage's
  Exit never requires one. Each stage entry's `Leaves out` field names what
  that stage leaves out and which later stage or item picks it up, so the
  stage's own brainstorming session or plan does not pull the quality back in.
  The later stage or item that picks a quality up names it in its own fields,
  by the name that `Leaves out` gives it.
- **Order.** Sequence by SKILL.md §2. A core stage is the cheap information
  about its track, so the core stages come first, in your partner's track
  ranking, unless a dependency says otherwise.

## What stays out

How a stage is built: its tasks, its tests, its approach. That stays with
brainstorming or writing-plans, by bare name, in the stage's own session.
