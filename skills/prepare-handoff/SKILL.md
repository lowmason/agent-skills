---
name: prepare-handoff
description: >
  Use when writing a handoff brief or handoff prompt for a fresh session — a
  spec to planning, a plan to execution, an SDD or roadmap checkpoint, or
  "/clear and continue" — or, while planning or handing off, when a decision
  must stay out of a public repository.
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
# cc-guide: subagents.isolation rules.auto-memory lean.session-hygiene lean.model-routing @2.1.306
---

# prepare-handoff

## Overview

Beyond what loads every session (instruction files, memory), a fresh session
reads only what it is pointed at. Before handing work on,
sort what the next session needs. Most of it is already in the artifact, is
recomputed by the receiving session, or can be committed now. Only the rest
goes in a brief: a short file the next session starts from, never committed.

## 1. Sort

Put each thing the next session needs into one bin:

| Bin | Action |
|---|---|
| In the artifact | Nothing. The brief may point to it by section. |
| Recomputable by the receiver's checks: status, commits since, files naming the artifact, plan ids | Nothing. |
| Amendable now, with your human partner approving the exact wording now | Amend it, and commit where the home is tracked: a spec amendment tagged `(owner, YYYY-MM-DD)`, a `## Decisions` entry in the plan, a deviation line in the subagent-driven-development ledger, a stage plan's `## Handoff to later stages`, or a derive-roadmap roadmap. |
| Everything else | The brief. |

Everything else includes decisions whose wording your partner approves later,
provisional defaults, traps only your own analysis found, owner gates,
leave-alone items, and anything that cannot be committed, such as a decision
that must stay out of a public repository.

If that last bin is empty, write no brief. The handoff stays "/clear (or a
fresh session), then <next skill> on <artifact>".

## 2. Write the brief

The parts come in this order. Every slot is required; an empty slot reads
`none`.

1. **Opening line:** the receiving skill, the artifact's path, the earliest
   commit to read, what to produce, and where to stop.
2. **Decisions.** Each `D<n>` has four fields:
   - *You said:* your partner's words, dated;
   - *Reading:* your interpretation of them;
   - *Home:* exactly one durable home, such as the plan's `## Decisions` or a
     spec amendment task;
   - *Approval:* now, or a named later point such as plan review.
3. **Defaults to flag:** each with its question, a recommended default, and
   the effect if it is wrong.
4. **Constraints and traps:** each with `path:line` evidence.
5. **Owner gates:** new gates, plus the artifact's own gates by section
   reference, never restated.
6. **Leave alone.**
7. **Closing line:** the brief's path, and "Record each decision in its Home;
   then this brief is disposable."

Carry nothing the artifact states and nothing the receiver recomputes, and do
not restate what the receiving skill does anyway.

## 3. Review

Check each claim against its source yourself. Then add reviewers by content:

- **Fact-checker** (`references/fact-checker.md`), when the brief cites repo
  or artifact text: paths, `path:line`, section numbers, ids, commits.
- **Cold reader** (`references/cold-reader.md`), when the brief carries a
  scope-changing decision or an owner gate.

Fill each template's `[BRIEF_PATH]`, and dispatch the reviewers in parallel as
read-only subagents, with no model pinned. Where the runtime cannot dispatch
subagents, ask your human partner to open a fresh session with the filled
template. Fix what they find, and put every ambiguity to your partner as one
batched question before the brief goes out. There is one round: a slot
changed afterwards gets your own check, and your partner may ask for another
round.

## 4. Store

Write the brief to `~/.cache/agent-skills/handoffs/<repo>/<YYYY-MM-DD>-<slug>.md`.
`<repo>` is the main worktree's directory name, the same from every worktree,
and `<slug>` names the receiving work. If the runtime refuses that write, use
`.handoff/` at the main worktree's root, with its own `.gitignore` holding `*`.

## 5. Memory

Update any memory entry the brief contradicts, and save a private decision to
the runtime's memory as well. On a runtime with no memory, tell your partner
that a private decision lives only in the brief.

## 6. Deliver

End with the brief's path, and "start a fresh session and paste it": the
route that works on every surface, the desktop app included. Then give one
launch line per runtime, leaving `<model>` to your partner:

```bash
claude --model <model> "$(cat <path>)"
codex -m <model> "$(cat <path>)"
gemini -m <model> -i "$(cat <path>)"
```

You may recommend a model, with a reason drawn from the receiving work; never
assume a default. `/model` saves a default for later sessions, while `--model`
applies to the one session only.

## Common mistakes

- **Restating the artifact** instead of pointing to its section.
- **A Reading presented as You said.** Keep your partner's words apart from
  your interpretation, and ask when they differ.
- **A decision with two homes,** such as an amendment that is also recorded as
  a deviation. One Home and one Approval per decision.
- **A hand-written plan-id check.** The receiving session computes ids.
- **No gates slot** because the artifact has gates. Point to them by section.
- **A brief when the last bin is empty.**
