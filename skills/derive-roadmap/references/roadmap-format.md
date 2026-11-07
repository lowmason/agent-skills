# Roadmap artifact format

`specs/<name>-roadmap.md` in the target repo — `<name>` is the spec's own
filename stem, used whole, never stripped (SKILL.md §3). Before writing,
scan `specs/` for an existing roadmap header naming this spec as its
source (SKILL.md §3) — filenames don't establish that on their own. Opens
with this header, verbatim:

> For agentic workers: REQUIRED SKILL: derive-roadmap — resume via its
> reconcile step; route each unticked stage per its ROUTING line; never plan
> this document wholesale.

## Document skeleton

After the header, in order — name a section, don't invent one:

1. **Gap analysis** — the rubric table (`references/gap-rubric.md`).
2. **Open questions** — only if contradictions or ambiguities from SKILL.md
   §1's batched question set are still unresolved when the file is written;
   omit the section otherwise.
3. **Stages** — the checkbox entries, below.
4. **Stage-spec stamp** — the Rollout-note text, below.
5. **Completion** — retirement criteria (SKILL.md §6): re-run the rubric
   over the accumulated system.

## Stage entries

Checkbox stages under a hard brevity budget. Each stage carries exactly
these fields and nothing else:

```
- [ ] Stage N: <short name>
      Objective: <one sentence>
      Spec: <§-refs — cite, never restate>
      Gap closed: <which rubric rows this stage discharges>
      Consumes: <what this stage assumes already exists from prior stages>
      Produces: <what later stages may assume after this ships>
      Exit: <one observable outcome per rubric row closed, not an intention>
      ROUTING: brainstorming | writing-plans
```

**Consumes/Produces are load-bearing.** The roadmap, the spec and each
completed stage plan's `## Handoff to later stages` section are the ONLY
cross-stage carriers — a stage's implementer sees neither the previous stage's
session nor the rest of its plan. A field may cite `plan <id>, Handoff`, and a
point settled at a resume carries `(Resolved at resume, YYYY-MM-DD)`. A resume
treats a stamped stage as new while no entry cites its plan's Handoff, and it
asks when unticked stages remain and none has its `Consumes` met, where a
`Consumes` is unmet only when a Handoff or stamp shows its input missing or not
built (SKILL.md §5).

**ROUTING** is `brainstorming` when the stage's design space is open, and
`writing-plans` when the spec fully determines it. Name the skill bare.

## Stage stamps

Every stage spec's Rollout note carries this line, which writing-plans then
copies verbatim into the stage plan's header:

> Roadmap: specs/<name>-roadmap.md, Stage N — on plan completion, tick the
> stage and re-validate later stages against what shipped.

On completion, a stamp goes under the stage's entry in the roadmap, the one
addition to its fields, and it is authoritative:

> Stage N: COMPLETE (YYYY-MM-DD) — implemented by plan <id> (path). Its Handoff section names what <stages> consume.
> Next: resume the roadmap.

The second sentence points at the plan's `## Handoff to later stages`. Drop it
when the plan has no such section, or when the section reads `None`.

## New-project roadmaps

A roadmap from the New-Project Entry (SKILL.md §7) keeps the header, the stage
checkboxes, the stamps and the resume above, with these differences.

`<name>` is the spec's stem when there is a spec. With no spec, it is the
kebab-case name your partner confirmed in the one message. With a spec,
SKILL.md §3's scan applies first: a roadmap that names this spec as its
source goes to Resume (§5). Then, with or without a spec, check before
writing that `specs/<name>-roadmap.md` does not exist. If it does, ask for
another name: never overwrite it.

After the header, in order:

1. **Outcomes**, in place of the Gap analysis. With no spec, this section is
   the roadmap's source of truth.
2. **Open questions**, as above.
3. **Stages**, the entries below.
4. **Ranked list — Track <X>**, one section for each research track.
5. **Stage-spec stamp**, as above.
6. **Completion**: SKILL.md §6, run over the Outcomes list.

The Outcomes section keeps one line per outcome:

```
Source: <your partner's words, YYYY-MM-DD> | <spec path>. Background: <paths> | none.
Choices made: <one line each> | none.

| # | Outcome | Track | Rank | Cost (estimate; basis) |
|---|---|---|---|---|
| O1 | <what your partner gets> | A | 1 | <estimate; basis> or "measured by Stage 1" |

Tracks: A — <name> (known progression | research). <Split from B because …>
```

Stage entries carry these fields and nothing else. `Outcomes` takes the place
of `Spec` and `Gap closed`:

```
- [ ] Stage N: <short name>
      Objective: <one sentence>
      Outcomes: <the O-numbers this stage delivers>
      Track: <letter> (omit with one track)
      Consumes: <as above>
      Produces: <as above; a core stage, and any stage of a research track, names specs/<name>-stage-<N>-findings.md>
      Exit: <one observable outcome per O-number; a core stage, and any stage of a research track, adds the measured cost of its real run>
      Leaves out: <each quality this stage does not need, with the stage or Ranked-list item that picks it up> | nothing
      ROUTING: brainstorming | writing-plans
```

Each research track's Ranked list keeps your partner's order:

```
## Ranked list — Track B
1. O4 — <cost note>
2. O6 — <cost note>
```

An item leaves the list when your partner promotes it to a stage at a resume,
or parks when the track stops or the whole roadmap parks (SKILL.md §5).
