# delegation-frontmatter rollout — Design Spec

**Status: COMPLETE (2026-07-19)** — implemented by plan 11
(`specs/plans/completed/11-delegation-frontmatter-rollout.md`) and retired here;
executed via executing-plans. Reconciled to the repo's Sonnet-default routing
decision (plan 10); merged the (now-deleted) Rev. 2 report's §a (skill frontmatter)
and §c (agent definitions) into one rollout so the single "which Haiku path"
decision was made in one place.

Add `model`/`effort` delegation frontmatter to the compute-heavy skills and the
reviewer agents, and give the genuinely mechanical data skills a Haiku path — so a
Sonnet-default session gets the right model/effort *by structure* (the skill you
invoked) rather than by per-prompt guessing. This is primarily task-model **fit**;
the Haiku pins are a modest, per-turn cost trim, not the main cost lever (that
remains plan 10's session-boundary work).

## Motivation — the real gaps

Plan 10 shipped the *session-level* routing (Sonnet default; reviewer agents pinned;
CLAUDE.md policy; `availableModels`/`enforceAvailableModels`). What remains undone,
and is this spec's scope:

- **No skill carries any delegation frontmatter.** `grep -rE '^(model|effort):'
  skills/*/SKILL.md` → none; no `context: fork` anywhere. The report's §a/§b are
  entirely unimplemented.
- **The reviewer agents pin `model` but not `effort`.** `code-reviewer` (opus) and
  `task-reviewer` (sonnet floor) set no effort.
- **No Haiku path exists** for the mechanical data skills — profiling/lookup work
  inherits the (Sonnet or Opus) session model.

## Core principle — effort before model; both structural, never per-prompt

The report's tier table pins advisory routers (`recommend-*`) to `opus/high`. That
encodes the **rejected** Opus-default philosophy. This rollout re-derives the
assignments under the repo's policy:

- **Prefer `effort` pins over `model` pins.** Effort is Anthropic's cheaper,
  earlier lever (context→effort→model) and it **composes** with whatever session
  model the user deliberately chose; a `model:` pin **overrides** that choice for
  the skill's active window. So default to bumping effort, and reserve `model: opus`
  for skills whose *very invocation is an unambiguous structural signal* of heavy
  work **and** that actually do the heavy reasoning (not advisory routers).
- **A skill/agent frontmatter pin is a *structural* router, which the policy
  allows** ("route by task structure"). It is **not** the banned per-prompt
  self-assessment. The distinction the spec must hold: pin on *what skill loaded*
  (structure), never on a model's per-prompt "this feels hard" (self-assessment).
- **Haiku has no effort parameter** — never add `effort` to a Haiku-pinned item.

## Requirements

### 1. Prereq A — verify field support against the installed version (do first)

The report self-flags that it "could not inspect raw SKILL.md frontmatter." Do not
trust its field claims. Before any edit, confirm on the installed Claude Code
(`claude --version` / `/doctor` / claude-code-guide) that:

- `model:` and `effort:` on a **skill** override the session model/effort for the
  skill's active window and resume after (report §3's claim).
- `effort:` on an **agent** is honored (agents already prove `model:` works).
- `context: fork` + `agent:` runs the body in a forked subagent using that agent's
  tools+model — **and** that a fork with a real task body does not no-op.
- **Explore no longer forces Haiku.** Report §1: as of v2.1.198 the built-in Explore
  **inherits the session model** (capped at Opus), where it used to be always-Haiku.
  Confirm this on the installed version — it decides Req 5.

Record what each key actually does on this version in the plan; a surprise here
changes the design. **Fallback, not a blocker:** if the installed version does
*not* honor `model:`/`effort:` in SKILL.md frontmatter, Req 3 collapses — proceed
with only the agent-level pins (Req 4's `code-reviewer` effort) and, if forks work,
the Req 5 Haiku path via a fork; treat a negative result as a branch to take, not a
reason to stop.

### 2. Prereq B — extend the frontmatter lint (blocking)

`build/check_frontmatter.py:22` `ALLOWED_KEYS =
{'name','description','license','allowed-tools','metadata','when_to_use'}`; line 87
errors on any unknown key. Add the delegation keys this rollout uses — at minimum
`model`, `effort`, `context`, `agent` (and `disable-model-invocation` if the
router skill has not already added it) — **only after confirming each is a valid
Agent Skills frontmatter key** (Prereq A). Add/keep a test in
`build/test_*frontmatter*` covering an accepted `model:`/`effort:` skill and a still-
rejected bogus key. No frontmatter edit below can land until this passes.

### 3. Skill pins — re-derived under Sonnet-default

| Skill | Proposed pin | Rationale |
|---|---|---|
| `bayesian-workflow` | `effort: xhigh`; **`model:` decision** (opus-pin vs inherit) | Heaviest reasoning skill and the one case where invocation ≈ heavy regime. But it now runs in its own fresh session (commit `af4b252`), where the user already picks the model — so a `model: opus` pin *overrides* that deliberate choice. **Recommend `effort: xhigh` only, `model` left `inherit`**; add the opus pin only if the user wants invocation to force Opus regardless of session. Flag as the one deliberate escalation to bless. |
| `tune-hyperparameters` | `effort: xhigh`, `model: inherit` | Regime-A search reasoning is heavy, but the skill is often consulted mid-execution on Sonnet; effort composes, model-override would fight that. |
| `recommend-probabilistic-model`, `recommend-visualization` | **no `model` pin**; optional `effort: high` | Advisory routers ("recommend, don't fit"). The report's `opus/high` contradicts the policy — an advisory skill should be *cheap*. Leave `model: inherit`; add `effort: high` only if the decision-map reasoning measurably needs it. |
| superpowers process skills (`systematic-debugging`, `writing-plans`, `subagent-driven-development`, …) | leave `inherit` | They need the session's reasoning depth and already adapt to session context; pinning would fight the plan-on-Opus/execute-on-Sonnet boundary. Optionally read `${CLAUDE_EFFORT}` in-body (future). |

### 4. Reviewer-agent effort

- `agents/code-reviewer.md` (opus, whole-branch): add `effort: xhigh`. Fixed pin —
  this reviewer is unconditionally the heavy one.
- `agents/task-reviewer.md` (sonnet floor, escalated to opus per-diff by the SDD
  controller): **do not hard-pin a fixed `effort`.** Its `model` is deliberately a
  *floor* the controller overrides per dispatch; effort should mirror that — set it
  per-dispatch, or add an `effort` *floor* comment only. Encoding a fixed high
  effort would fight the per-diff escalation that SDD's Model Selection owns.
  Confirm against `skills/subagent-driven-development` before touching it.

### 5. One Haiku path — pick one, name the rejected alternative

Scope the Haiku pin to **genuinely mechanical** work, not "data skills" as a
category: **`explore-data`** (its numbers come from the deterministic bundled
`profile.py`, and it feeds *into* analysis with `validate-data` downstream as the
net) and **`bls-data-context`** (reference retrieval with facts in-context).
**Exclude `validate-data`** — it is the ship-gate (benchmark reconciliation,
methodology/bias, silent-fallback detection), reasoning checks whose whole value is
catching the subtle problem a weaker model misses, and it is the last line with
nothing downstream to catch what it lets through; it stays `inherit`. Because Explore
no longer forces Haiku (Req 1), the report's "`context: fork` + `agent: Explore`"
would now run on the **session** model (Sonnet), *not* Haiku — it no longer does what
the report claims. Options:

- **(chosen) `model: haiku` directly on the two mechanical skills.** Simplest;
  guaranteed Haiku; no new agent; no reliance on Explore's changed behavior. Runs
  in-context (no fork isolation), fine for short profiling/lookup bodies; the override
  is per-turn (Req 1). Verify `model: haiku` on a skill behaves as documented.
- (rejected) **new `data-explorer` haiku agent** (report §c) + fork to it — an extra
  agent and install surface for no gain over the direct pin.
- (deferred upgrade) a single **haiku-pinned `Explore` override agent** — restores
  fork isolation *and* Haiku, and doubles as the global Explore→Haiku lever the
  report recommends. Add later only if fork isolation proves worth it.

Ship the direct `model: haiku` pin on the two mechanical skills; leave a one-line
note pointing at the Explore-override upgrade.

### 6. Watch-outs to encode

- Haiku takes no `effort` — none on the two Haiku-pinned skills (`explore-data`,
  `bls-data-context`).
- `context: fork` with a reference-only body silently no-ops — not a risk here since
  the chosen path avoids fork, but note it if the deferred upgrade is taken.
- Cross-skill references stay bare skill names (repo invariant).
- No new third-party code; `build/check_provenance.py` must still pass. These are
  edits to existing files — no `NOTICE`/`README` provenance rows needed (the
  rejected `data-explorer` agent *would* have needed a README Agents-table row;
  skipping it avoids that).

## Verification

- `build/check_frontmatter.py` and `build/check_provenance.py` pass with the new
  keys accepted and a bogus key still rejected.
- Each pinned skill still triggers on its existing `description` (pins do not touch
  the description) and, when invoked, the active model/effort matches the pin
  (spot-check via `/status` or the model indicator).
- The two Haiku-pinned skills (`explore-data`, `bls-data-context`) demonstrably run
  on Haiku on a Sonnet session; `validate-data` stays on the session model.
- `task-reviewer`'s per-diff escalation still works — an SDD dispatch that requests
  Opus for a risky diff is not overridden by a hard effort pin (because none was
  added).
- **Cost check (the point of the rollout):** measure subagent/session token spend
  via `/status` before and after on one representative Bayesian session; confirm
  exploration/profiling spend drops.

## Out of scope

- Session defaults / `opusplan` / `settings.json` — decided in plan 10 (`opusplan`
  rejected); not revisited.
- `recommend-model-and-effort` router skill — `specs/recommend-model-and-effort.md`.
- Custom `advisor` agent (report §b′) — redundant here: the built-in advisor is live
  (`advisorModel: opus`). Adopt only on a gateway work machine where the built-in is
  unavailable; not a build task.

## Rollout note

Decisions here are mostly mechanical once the "effort before model" principle and
the Haiku path are approved. Per the repo lifecycle this spec can go **straight to a
plan** (`specs/plans/<id>-delegation-frontmatter-rollout.md`) rather than a long
brainstorming cycle — the open items are the two flagged decisions (bayesian-workflow
`model` pin; task-reviewer effort), which are yes/no, not design-space explorations.
Every change is per-file frontmatter or one lint line; rollback is deletion.
