# Roadmap artifact format

`specs/<name>-roadmap.md` in the target repo. Opens with this header,
verbatim:

> For agentic workers: REQUIRED SKILL: derive-roadmap — resume via its
> reconcile step; route each unticked stage per its ROUTING line; never plan
> this document wholesale.

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
      Exit: <one observable outcome>
      ROUTING: brainstorming | writing-plans
```

**Consumes/Produces are load-bearing.** The roadmap and the spec are the
ONLY cross-stage carriers — a stage's implementer sees neither the previous
stage's session nor its plan.

**ROUTING** is `brainstorming` when the stage's design space is open, and
`writing-plans` when the spec fully determines it. Name the skill bare.

## Stage-spec Rollout stamp

Every stage spec's Rollout note carries this line, which writing-plans then
copies verbatim into the stage plan's header:

> Roadmap: specs/<name>-roadmap.md, Stage N — on plan completion, tick the
> stage and re-validate later stages against what shipped.

On completion the stamp becomes authoritative:

> Stage N: COMPLETE (YYYY-MM-DD) — implemented by plan <id> (path).
> Next: resume the roadmap.
