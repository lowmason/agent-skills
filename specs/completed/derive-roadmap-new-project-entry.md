# derive-roadmap new-project entry — Design Spec

**Status:** COMPLETE (2026-11-06), implemented by plan 78 (`specs/plans/completed/78-derive-roadmap-new-project-entry.md`). It was APPROVED on 2026-11-06. The design came from a brainstorming session on 2026-11-06,
and the owner approved this file, its designer's calls included, the same day.

derive-roadmap gets a second way in, for a project with nothing built yet. The owner states the
outcomes or the stage progression in plain words. The skill splits unrelated outcomes into
separate tracks, and the owner ranks them. The skill attaches a rough cost to each outcome and
then writes the usual roadmap file. When the owner knows the progression from start to finish,
the roadmap commits every stage. For a research track, it commits only the core stage and keeps
the rest in a ranked list until the core has run on real data. Qualities that a project needs
eventually but not on day one, such as manifests, traceability and point-in-time awareness,
become named later stages. describe-critique-methodology and brainstorming route a project with
nothing built to this entry. The critique round-trip keeps its original job: improving a system
that exists.

Design provenance: the evidence below comes from the git history of four public repositories
(lowmason/sec-edgar, sec-edgar-local, ces-revisions and embedding-data), read on 2026-11-06.
Decisions D1–D10 are the owner's, from the same session. Text marked *(designer's call)* is a
choice the owner has not yet confirmed, listed for review in the Rollout note.

## Motivation — four roadmaps that began before anything worked

The owner reported that roadmaps from the describe-critique-methodology → derive-roadmap chain
came out as detailed, strict designs when an incremental approach was needed. The owner believed
that in each case no implementation existed to critique. A check of four roadmaps confirmed that
belief. It also showed that a state-of-the-art (SOTA) critique set the size of only one of them.

| Roadmap (derived) | Built when derived | What set its size | Stages | What arrived late |
|---|---|---|---|---|
| sec-edgar index ingestion (2026-10-05) | Package scaffolds only. The day-0 spec says "No repository was supplied. Every code, configuration and deployment path below is proposed." | The owner's design chat. The day-0 spec already held manifests, record identity and publication contracts. | 8 | A Stage 1 "Scope and feasibility findings" ran after the spec was accepted and did not find repeated index keys. After the port to sec-edgar-local, repeated keys quarantined all 28 quarterly files, and the successor roadmap grew from 5 to 11 stages. |
| sec-edgar-local filing platform (2026-10-21) | The platform spec says "Nothing is implemented." | A first-pass SOTA critique: 26 points became 31 requirements. | 13 | The evidence campaign is Stage 6. |
| ces-revisions (2026-09-12) | A two-line scaffold | The owner's research brief plus three research drafts that nobody adjudicated, synthesized as a superset. Two unrelated questions were joined in one model. | 27 | Fit time (10–40 hours per fit) was known after Stage 1. The dollar cost of cloud GPU time was estimated only after Stages 1–5 shipped. |
| embedding-data (2026-10-12) | About 350 lines of source | The owner's design session, plus about 12 requirements added at synthesis, including both manifests. | 13 | Stage 1 built the manifest. The consumer, naics-embedder, reads none of the outputs. |

The common pattern:

1. **Nearly every gap was `missing`.** derive-roadmap's gap analysis compares a spec with the code.
   When no outcome works yet, nearly every requirement is missing, so the analysis filters nothing
   and every requirement becomes stage work. embedding-data shows that "nothing works" is not the
   same as "no code": its first gap table had 13 rows `implemented-as-specified` and 45
   `missing`. The 13 were downloaded ACS and CPS extracts, and no evaluation target existed.
2. **Every stated outcome became a requirement of equal force.** Synthesize mode's triage has
   accept, reject and needs-user-adjudication, but no "later". derive-roadmap orders stages by
   dependency, and its Common mistakes list warns against ordering by priority. It has no way to
   drop a requirement short of a deferral at the end. In the owner's words: "having specified
   what I wanted, they were baked in at the start."
3. **Final-standard qualities were day-one requirements.** Manifests, traceability and
   point-in-time awareness are needed eventually. The owner's judgment: they were "likely not"
   needed from the start.
4. **Unrelated questions were joined.** ces-revisions held a nowcast artifact (more collection
   time gives a better estimate) and a research question (did budget and staffing attrition
   enlarge revisions). One joint model made the first wait on the machinery of the second. No
   step in the chain asks whether a request holds separate projects.
5. **Scoping came after the design.** Two roadmaps opened with a scoping stage (sec-edgar Stage 1,
   ces-revisions Stage 2). Both ran after the spec was accepted and only confirmed it.
6. **Cost was unknown until stages had shipped.**
7. **The critique skill ran outside its design.** It was built for "an existing system". It ran in
   Describe mode on an unbuilt design (sec-edgar-local) and in Synthesize mode with a brief as the
   description and research drafts as the critique (ces-revisions).

For sec-edgar the owner knew the progression from earlier work: "What I lacked was an easy way of
specifying the roadmap stages." For ces-revisions the SOTA research mattered, but it "need not
have come from describe-critique-methodology at all".

## Goals, non-goals and anti-goals

Goals:

- An easy, short way to state a new project's stages or outcomes and get a roadmap.
- Each track reaches a usable result on real data early.
- Cost is visible before the roadmap commits.
- Unrelated outcomes are staged apart.
- Hardening is recorded as named later work, not lost.

Non-goals:

- Changing how derive-roadmap handles a spec for a system that is partly or fully built.
- Changing the critique round-trip for an existing system.

Anti-goals (failure even if the entry technically works):

- The entry becomes a second brainstorming, with a long interview before any stage.
- A core stage quietly drops a quality the project needs, with no later stage or list item that
  picks it up.
- derive-roadmap starts to design stages (their tasks, tests or approach).
- Research background turns back into a requirement list by another route.

## Approaches

- **A. A new entry in derive-roadmap (chosen, D1).** derive-roadmap already owns the roadmap file,
  its resume, parking and completion review. A new entry reuses all of it. brainstorming and
  describe-critique-methodology each get a short routing step. The cost: derive-roadmap grows,
  and its "routes, never designs" rule needs a stated boundary (R14).
- **B. brainstorming owns new-project roadmaps (rejected).** brainstorming already holds this kind
  of conversation and already checks for separate projects. But its written design pulls toward a
  full design, which is the pull that caused the problem. It also adds a second handoff, and
  brainstorming is the most heavily tested skill to change.
- **C. A new skill for new-project roadmaps (rejected).** The separation is clean. But the skill
  listing is already over budget, a new skill needs a NOTICE entry, and its trigger would compete
  with brainstorming's "let's build", the routing collision that the methodology-pipeline spec
  (`specs/completed/methodology-pipeline-skills.md`) worked to avoid.
- **D. Guards and a "later" tier label only (dropped).** The owner would still write a spec first,
  and writing the spec first is what loads the final standard in on day one.

## Decisions (owner, 2026-11-06)

- **D1.** Approach A: a new entry in derive-roadmap.
- **D2.** When the owner knows the progression from start to finish, the roadmap commits every
  stage. describe-critique-methodology runs after those stages are implemented.
- **D3.** For a research track, the roadmap commits the core stage only. The rest stays in a
  ranked list until the core has run on real data, because the first results may change the
  ranking.
- **D4.** Unrelated outcomes go into separate tracks. Catching a bundled request is the skill's
  duty, not the owner's.
- **D5.** The owner ranks outcomes, weighing value against the cost to measure or build.
- **D6.** A rough cost comes before the roadmap commits. The first real run measures the cost.
- **D7.** Final-standard qualities are named later stages, not day-one requirements.
- **D8.** Research results enter as background, not as a synthesized spec.
- **D9.** describe-critique-methodology runs on a built system. Both it and derive-roadmap send a
  project with nothing built to the new-project entry.
- **D10.** When a fresh gap analysis finds nothing built, derive-roadmap offers the new-project
  entry and waits for the owner's yes. It never switches on its own. (Decided after the builder
  check showed that a strict "every requirement missing" rule misses embedding-data.)

## Core principle

On a new project, the roadmap stages what the owner ranked first, at the smallest standard that
works on real data, and names everything else as later work. Facts about data, limits and cost
come from building the first stage, not from a design written before any data was seen.

## Requirements

**Nothing built.** In this spec, a project has *nothing built* when no outcome of the system that
the spec or request describes works end to end on real data yet. The test covers that system, not
the whole repository, so a new subsystem inside a mature repository can qualify. Code that only
acquires inputs, such as downloaded extracts, does not count as a working outcome *(designer's
call)*. R1, R13(b) and R13(c) all use this one definition.

**R1 — Entry conditions.** derive-roadmap takes the new-project entry in either case:

- (a) The owner asks for a roadmap for a project with nothing built, with or without a spec.
- (b) A fresh gap analysis (SKILL.md §1) finds nothing built. The skill does not partition yet. It
  adds one item to §1's batched question set: what it found, and an offer to stage the project
  through the new-project entry with the spec's requirements as outcome candidates. It waits for
  the owner's answer (D10). On a yes it moves to the new-project entry. On a no it partitions as
  today.

A document that carries the roadmap header still goes to Resume first, as today.

**R2 — Inputs.** The entry takes the owner's outcomes or progression in plain words, plus optional
background files: research results, a draft spec, the owner's notes (D8). The skill reads
background for facts, options and costs. Each outcome the roadmap stages comes from the owner's
list, or from candidates the owner confirmed and ranked. Background never becomes a requirement
list on its own.

**R3 — Kind of track.** Each track is one of two kinds, and the kind decides commit depth (R7):

- **Known progression:** the owner can name the stages from start to finish (sec-edgar).
- **Research:** the method or the answer is open (ces-revisions' attrition question).

One project may hold tracks of both kinds *(designer's call)*.

**R4 — Outcome list and tracks.** The skill writes the outcomes as a numbered list in plain words,
one line each. Each line says what the owner gets, not how it is built. The skill groups outcomes
into tracks. Outcomes that answer unrelated questions, or serve different uses, go into separate
tracks, and the skill says why it split them (D4). The owner confirms, merges or splits.

**R5 — Ranking.** The owner ranks the outcomes within each track, and the tracks among themselves
(D5). The skill shows the list unranked, with each outcome's cost note (R6). It does not rank for
the owner unless asked, because the ranking is the owner's judgment of value *(designer's call)*.
In a run that cannot ask, the provisional file uses the order the owner gave, or else the list
order, and labels the ranking provisional.

**R6 — Cost.** Before the roadmap commits, each outcome whose cost is material carries a rough
estimate and its basis (D6). Material costs include compute hours or dollars, data volume, rate
limits and the owner's time. The basis may be published limits, file sizes, or arithmetic from
known figures. At entry the skill may run only cheap read-only checks, such as a directory
listing, a size lookup or a published-limit lookup *(designer's call)*. The batched message (R15)
may also propose a small probe, such as fetching one real file or timing one model fit. The probe
runs only on the owner's yes, and it counts as information gathering, not stage design (R14)
*(designer's call)*. When no estimate is possible without running the work, the cost note says
so, and the track's core stage measures it (R8).

**R7 — Commit depth.**

- A known-progression track commits every stage, from first to last, including its later
  hardening stages (D2).
- A research track commits its core stage only. Its other outcomes stay in a ranked list in the
  roadmap file until the core stage has run on real data (D3).

**R8 — Core stage.** The first stage of each track works on real data at the smallest standard
that gives a usable result. In a research track it delivers the top-ranked outcome end to end. Its
Exit names the observable result and the measured cost of the real run: time, compute or data
volume (D6). Examples from the evidence: a first sec-edgar stage that reads the real quarterly
index files with no manifest layer, and a first ces-revisions stage that estimates first-to-second
revision size on the national total with collection days as its one covariate.

**R9 — Later qualities.** Qualities that a project needs eventually but not to work become named
later stages in a known-progression track, or ranked-list items in a research track (D7). Examples
are manifests, traceability, point-in-time awareness, full validation suites, scheduling and
deployment. A core stage's Exit never requires them. Each stage entry carries a field that names
what the stage leaves out and which later stage or list item picks it up. That field is what keeps
the stage's own brainstorming session or plan from pulling the quality back in.

**R10 — The roadmap file.** A new-project roadmap uses the same header, stage checkboxes, stamps
and resume machinery as today (`references/roadmap-format.md`), with these differences:

- An Outcomes section takes the place of the Gap analysis. It holds the numbered outcome list,
  the tracks and their kinds, the owner's ranking and the cost notes. It also holds, one line
  each, any whole-project choices the owner has already made, such as the language or platform.
  Recording a choice the owner made is not designing (R14).
- Stage entries cite outcome numbers where today they cite spec § references.
- Each research track has a Ranked list section.
- Each stage entry carries the later-qualities field (R9).

With no spec, the Outcomes section is the roadmap's source of truth. The brevity budget still
holds: one line per outcome.

**R11 — Resume of a research track.** When every committed stage of a research track is ticked
and its ranked list is not empty, the resume does not go to the completion review. It reports what
the core stage found, including the measured cost. It asks the owner to re-rank the list, and it
proposes the next stage through SKILL.md §5's existing Ask (a stage added is a single question to
the owner, never an amendment).

**R12 — Completion review.** SKILL.md §6 runs over the outcome list in place of spec requirements.
An unmet outcome exits as today: a new stage, or a conscious deferral with a written reason.
Ranked-list items the owner never promoted follow the existing Parking rule.

**R13 — Routing in.**

- (a) **brainstorming.** When the conversation shows a multi-stage project with nothing built,
  and the owner's outcomes are clear, brainstorming hands off to derive-roadmap's new-project
  entry in the same session. It does this instead of laying out approaches for the whole project
  and writing a full design. The roadmap file is the only written record, so there is no new
  artifact type. How each stage is built is decided later, in that stage's own brainstorming
  session or plan. The builder adjusts brainstorming's "you must, in order" list, its size table
  and its HARD-GATE so that this handoff is an allowed exit *(designer's call: the same session
  keeps the owner's outcomes in context, and a fresh session would need a new handoff artifact)*.
- (b) **describe-critique-methodology, Describe mode.** Before it chooses a granularity, the skill
  checks whether the system it would describe has nothing built (the definition above). If so, it
  says so and routes to the new-project entry. The critique comes after the system is built (D9).
- (c) **describe-critique-methodology, Synthesize mode.** When the "description" is a brief or a
  design for something not built, or the "critique" is research drafts written in answer to that
  brief (the ces-revisions shape), the skill says so and routes the files to the new-project entry
  as background (D8, D9).
- (d) **derive-roadmap's description** gains triggers for a new-project roadmap, for example a
  request to lay out the stages of a project with nothing built yet.

**R14 — The roadmap still routes and never designs.** Listing, splitting, ranking and costing
outcomes is partitioning. How a stage is built stays with brainstorming or writing-plans, by bare
skill name, as today.

**R15 — The entry stays short.** The entry sends one batched message before any roadmap text. That
message holds the outcome list, the proposed tracks with their kinds, the cost notes, and one
request: rank the outcomes and confirm the tracks. The stage partition then goes to the owner for
approval, as SKILL.md §4 requires today. When the session cannot ask, the existing provisional-file
rule applies.

## Verification

Each bullet names an observable outcome. The fixtures come from the four public repositories in
the Motivation.

- **V1 (R1b, D10).** Given sec-edgar's day-0 spec on its scaffold-only commit (22c6767f),
  derive-roadmap does not partition the spec. Its batched question set reports that nothing is
  built and offers the new-project entry, and it writes no roadmap before the answer. On a yes it
  presents the spec's requirements as an outcome list for ranking.
- **V1b (the definition's boundary).** Given embedding-data's spec against the repository as it
  stood when its first roadmap was derived (the parent of 4bc8cda), derive-roadmap makes the same
  offer. The 13 met requirements are input downloads, and no outcome works end to end.
- **V2 (R7, R8, R9).** Given a known progression in the owner's words (index files, then individual
  submissions, then 10-K and 8-K handling), the roadmap commits every stage. No core stage's Exit
  requires manifests, traceability or point-in-time awareness. Each of those appears in a named
  later stage, and each stage entry carries the later-qualities field.
- **V3 (R4, R7, R13c).** Given ces-revisions' brief and its three research drafts, Synthesize mode
  routes them to the new-project entry and writes no spec. In the entry, the collection-window
  outcome and the attrition outcomes land in separate tracks. The roadmap commits one core stage
  per research track, and the core stage's Exit includes a measured cost.
- **V4 (R13b).** Given a repository with nothing built, Describe mode stops and routes to the
  new-project entry.
- **V5 (non-goal).** Given a spec against a partly built system, where at least one outcome works
  end to end on real data, derive-roadmap runs the five-verdict gap analysis and the existing
  partition, and makes no offer.
- **V6 (R11).** Given a research roadmap whose core stage is stamped COMPLETE and whose ranked list
  is not empty, the resume asks one re-ranking question and does not start the completion review.
- **V7 (micro-tests).** Each changed trigger and route has a RED baseline against a no-guidance
  control, recorded before the text changes, and a GREEN run after, per the writing-skills skill.
  At minimum V1, V3 and V2's "no hardening in a core Exit" are micro-tested.
- **V8 (repo gates).** The commit lints pass (`build/run_commit_lints.sh`), including the
  frontmatter, provenance, conformance, link and Tier 1 snippet checks and the dependency-drift
  test.

## Constraints

- The writing-skills skill governs every skill edit: RED before GREEN, and micro-tests against a
  no-guidance control for changed wording.
- derive-roadmap's SKILL.md stays lean. New-entry detail may move to a new file under
  `references/`.
- A new reference from one skill to a named section of another (for example "derive-roadmap's
  new-project entry" in brainstorming or describe-critique-methodology) is mirrored in
  `install.py`'s `DEPENDENCIES` or in `build/test_runtime_support.py`'s `SOFT_REFERENCES`, as
  CLAUDE.md requires.
- derive-roadmap and describe-critique-methodology are the owner's originals. brainstorming is an
  adaptation of the superpowers skills (MIT). NOTICE records changes to the adapted skills, so the
  builder checks NOTICE's brainstorming section and records the routing change if it requires one.
- The guide-conformance register (`build/cc_guide/conformance.toml`) applies to every edited
  artifact. `build/check_conformance.py` runs before each commit.
- No skill gains a `model:` pin.

## Left to the builder

- The name of the new entry, the exact field names in the roadmap format, and where the new text
  lives (SKILL.md or a new reference file).
- The wording of the new triggers and routing lines.
- How to detect scaffolding-only repositories beyond the gap-analysis result.
- The roadmap filename when no spec stem exists.
- The micro-test design, fixture construction and repetition counts.
- Whether the batched message (R15) shows the outcomes as a list or a table.

## Out of scope

- The open deferred item on SKILL.md §5's two resume gaps (no marker for the last resume, and no
  rule when no unticked stage has its Consumes met). R11 covers only the ranked-list case.
- Changes to the critique prompt (`references/critique-prompt.md`).
- Rewriting the existing roadmaps in the four case-study repositories.
- Changes to writing-plans.
- An in-session SOTA research pass. The owner retired that idea on 2026-09-28.

## Rollout note

Next: writing-plans, in a fresh session, against this file. The calls marked *(designer's call)*
are in the "nothing built" definition, R3, R5, R6 and R13(a). The owner checks them while
reviewing this file.
