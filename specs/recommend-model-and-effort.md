# recommend-model-and-effort — Design Spec

**Status: DRAFT (2026-07-19)** — proposed from `specs/model-effort-delegation-plan.md`
(the Rev. 2 report); **not yet approved**. The report was written without visibility
into plan 10 (`specs/plans/completed/10-model-routing-setup.md`) or the current
`settings.json`/`CLAUDE.md`; this spec reconciles its `recommend-model-and-effort`
proposal to the repo's *actual* routing decision before any build.

A user-invoked skill that, on demand, diagnoses why a session is underperforming
or overspending and recommends a **model** (haiku/sonnet/opus) and **effort**
(low/medium/high/xhigh/max) for the task at hand — naming the exact `/model` and
`/effort` commands to run. It **recommends and points; it never switches the
model itself** (mirrors `recommend-probabilistic-model`'s "recommend, don't fit").

## The two go/no-go gates (resolve these first)

This skill is **not** obviously worth building. Two gates decide it; both are the
first work of any implementation plan, before a line of SKILL.md is written.

- **Gate 1 — does it survive plan 10's objection?** Plan 10 *deliberately rejected
  any automatic per-prompt router*: "a model cannot reliably detect tasks above its
  own ability, and the failure mode — silent under-escalation — is invisible.
  Routing must be decided by structure … never by per-prompt classification." The
  report's draft (`disable-model-invocation: false`, auto-invocable) **fails this
  gate**. The skill clears it **only** if it is (a) **user-invoked only**
  (`disable-model-invocation: true` — Claude cannot auto-fire it) and (b)
  **advisory** (emits a recommendation + commands; never calls `/model` or edits).
  A user who is *unsure* asks for advice; the skill never inserts itself. If the
  design cannot hold this line, **do not build it**.

- **Gate 2 — does it earn its place beside the CLAUDE.md block?** The global
  `~/.claude/CLAUDE.md` already carries a "Model routing" block (Sonnet default,
  Opus at checkpoints, Haiku for Explore, never per-prompt). `writing-skills` warns
  against skilling standard practice. The skill earns its keep only if the
  **interactive decision *procedure*** — diagnose context→effort→model, map the
  task to a tier, emit exact commands — is materially more than the always-on
  6-line block. If the honest answer is "no," the **fallback is to enrich the
  CLAUDE.md block** and ship no skill. Record that outcome; it is a valid result of
  this spec.

## Motivation — the gap (if the gates clear)

The CLAUDE.md block states the *policy*; it does not walk a stuck user through the
*diagnosis*. The report quotes Anthropic's diagnostic order (Hallie, claude.com,
2026-07-07): **context → effort → model**. The recurring failure it addresses is a
user reaching for a bigger model when the real fix is more context or more effort —
or, in this environment, reaching for a bigger model *that does not exist* (Opus is
the ceiling; Fable is outside the allowlist). A short, user-invoked procedure that
forces the diagnosis in order — and, at the ceiling, redirects to decompose / fresh
context / advisor rather than "a bigger model" — is the marginal value over a
static policy block.

## Goal

An **on-demand, advisory** decision skill. When invoked it (1) diagnoses the
failure mode in Anthropic's order (context, then effort, then model), (2) maps the
task to a tier under the **Sonnet-default** policy, and (3) returns a one-line
recommendation naming the exact `/model` and `/effort` commands — and never runs
them. It is the routing analogue of `recommend-probabilistic-model`: it points at
the right knob and stops.

## Non-goals

- **Not an auto-router.** It never fires on its own and never switches the model
  (Gate 1). Per-prompt model self-assessment stays banned.
- **Not a settings/`opusplan` change.** Session defaults live in `settings.json`
  and are already decided (Sonnet default; `opusplan` rejected). Out of scope.
- **Not a re-statement of the CLAUDE.md policy.** If it is only that, it should not
  ship (Gate 2).
- **Not a cost dashboard.** Spend is read via `/status`; this skill points there,
  it does not compute token accounting.

## Design decisions (proposed — pending approval)

- **R1 — user-invoked, advisory, recommend-and-point.** Frontmatter
  `disable-model-invocation: true`; the body ends in a recommendation + exact
  commands, never an action. This is the load-bearing reconciliation with plan 10.
- **R2 — diagnosis before tier.** Step 1 is always the context→effort→model triage:
  missing context (vague prompt / wrong files / no skill) → fix context, touch no
  knob; Claude skipped a file / bailed on a refactor / skipped tests → raise effort;
  Claude tried thoroughly with full context and still failed → raise model. This
  ordering is the skill's reason to exist over the static block.
- **R3 — tiers reflect the Sonnet-default policy, not the report's Opus-default
  table.** Default Sonnet; **raise effort before model**; Opus at structural
  checkpoints (planning/design, whole-branch review) or explicit manual escalation.
  Haiku for mechanical search/profiling/lookup. The skill must not tell a user to
  "default to Opus."
- **R4 — name the ceiling behavior.** At opus/xhigh with full context and still
  failing, there is no larger model here. The recommendation becomes: raise effort
  to `max`/`ultracode` (session-only), **decompose** into narrower briefs, or run
  an **advisor pass** (the built-in advisor tool is live on this machine —
  `advisorModel: opus`). Never "use a bigger model."
- **R5 — output contract, fixed.** Return exactly: recommended model, recommended
  effort, the failure-mode diagnosis (which of context/effort/model), and the
  commands to run. Nothing else; no narration.

## Architecture — SKILL.md

Single file, no scripts (there is nothing to run to verify — this is guidance, not
code). Sections, house voice (lean, decision-first):

- **Overview** — the context→effort→model diagnosis over a knob-twiddling reflex;
  core principle: diagnose the failure mode first, then pick the cheapest knob that
  fixes it.
- **Step 1: diagnose the failure mode** (R2) — a short decision block, three
  branches (context / effort / model), each naming its tell.
- **Step 2: map the task to a tier** (R3) — the Sonnet-default tier table:
  heavy Bayesian fitting / model-comparison reasoning / whole-branch review →
  opus (xhigh at the checkpoint); implementation from a clear plan / per-task review
  / test-strategy design → sonnet / high; data profiling / schema-null checks / BLS
  lookups / doc munging → haiku (no effort knob).
- **Step 3: at the ceiling** (R4) — the decompose / max / advisor redirect.
- **Output** (R5) — the fixed contract + exact `/model …` / `/effort …` commands.

### Proposed frontmatter (reconciled)

```yaml
---
name: recommend-model-and-effort
description: Use when you (the user) are unsure which Claude model or effort level
  to use for a task, or a session feels too slow or too expensive for the work.
  Recommends a model (haiku/sonnet/opus) and effort (low/medium/high/xhigh/max),
  grounded in the diagnose-context-then-effort-then-model order, and names the exact
  /model and /effort commands to run. Advisory only — it recommends and points,
  never switches the model itself.
disable-model-invocation: true
allowed-tools: Read, Grep, Glob
---
```

The `description` starts "Use when…", is third-person, and is dense with triggers
(repo convention). `disable-model-invocation: true` enforces user-invoked-only
(Gate 1). `allowed-tools` is a pre-approval, not a restriction.

## Dependencies / prerequisites

- **Shared prereq with `delegation-frontmatter-rollout`:** `disable-model-invocation`
  is **not** in `build/check_frontmatter.py`'s `ALLOWED_KEYS`
  (`{'name','description','license','allowed-tools','metadata','when_to_use'}`,
  line 22); line 87 errors on any unknown key. The lint must learn
  `disable-model-invocation` (and confirm the Agent Skills spec permits it) **before
  this skill can lint clean**. If this skill ships first, it carries that one-line
  `ALLOWED_KEYS` change; otherwise it depends on the rollout spec landing it.
- **Version check:** confirm the installed Claude Code honors
  `disable-model-invocation: true` as "user-invocable only" on this version
  (`claude --version` / `/doctor` / the claude-code-guide agent). Do not assume from
  the report, which could not inspect frontmatter behavior.

## Provenance

New **original** work by Lowell Mason (MIT, `LICENSE`). On build: register in
`NOTICE` (originals list) and `README` (Mine table + "My original skills"). No
third-party code, no bundled prose. `build/check_frontmatter.py` and
`build/check_provenance.py` must pass.

## Testing strategy (how it ships)

This is a **guidance** skill, not code — no scripts, no run-to-verify artifact. Per
`writing-skills`, a behavior/reference skill of this kind is validated by:

- **Description micro-test** against a no-guidance control: does the `description`
  fire on "which model should I use / this feels too expensive" and *not* over-fire
  on unrelated prompts? (Auto-loading is off by `disable-model-invocation: true`, so
  the description drives *user discoverability* and any subagent preloading, not
  Claude auto-invocation — weight the micro-test accordingly.)
- **Procedure pressure-test:** on a scripted "stuck at opus/xhigh with full context"
  prompt, does the body route to decompose/advisor (R4) rather than "use a bigger
  model"? On a "skipped a file" prompt, does it raise *effort*, not model (R2)?
  A structural decision block, not a rationalization table, is the writing-skills
  target for these failure modes.

## Out of scope / future

- Any change to `settings.json` session defaults or `opusplan` (decided elsewhere).
- The delegation frontmatter on *other* skills and the reviewer-agent effort — those
  are `specs/delegation-frontmatter-rollout.md`.
- A `context: fork` variant that runs the recommendation itself on Haiku — the skill
  is tiny and advisory; forking buys nothing. Revisit only if it grows.
