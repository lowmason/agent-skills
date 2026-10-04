# Superpowers drift assessment — 2026-09-03

**Status:** findings only. No skill files were edited. This document exists to
decide *what, if anything, becomes a spec*.

## Scope and method

| | |
|---|---|
| Vendored baseline | `896224c` (v6.0.3, 2026-06-18), per `NOTICE` |
| Upstream HEAD | `b36e082` (v6.3.0, 2026-08-12) |
| Commits since baseline | 72 |
| Files changed under `skills/` | 32 (+1203 / −1210) |

Comparison is **per behavioral claim, not per diff hunk**. `NOTICE` records that
most vendored files were adapted on the way in, so `896224c` is not a true
ancestor of our copies and a mechanical three-way merge produces noise. Each
upstream RELEASE-NOTES entry was instead read as a claim and checked against our
tree: *does our copy already satisfy the intent?*

That distinction is load-bearing. Upstream's `0b47219` (2026-07-05) fixes a
worktree path recomputed after `cd`, which made cleanup silently no-op. It
landed after our vendoring, so a diff-driven read flags us as behind. We are
not: `finishing-a-development-branch/SKILL.md:187` already carries an equivalent
guard ("Do NOT re-run detection here"), and the file has not been edited since
the layout move. **Already covered.** Whether that guard arrived as adaptation
or the vendoring record is imprecise about this file is undetermined, and does
not change the disposition.

## Dismissed without further review

Roughly half the 72 commits are harness and packaging work with no bearing on a
standalone macOS install: Devin, Hermes, and Grok support, Codex marketplace
manifests and packaging scripts, the Windows SessionStart hook dispatch, the
`render-graphs.js` Windows fix, and the Gemini removal-then-restore. The entire
`using-superpowers` bootstrap compression and its per-harness reference files go
with them, since we dropped that skill.

Three skills changed by deletion only, with no new content:
`receiving-code-review`, `verification-before-completion`,
`dispatching-parallel-agents`. The additions in `executing-plans`,
`writing-skills`, and `systematic-debugging` are all `superpowers:`-namespaced
cross-references or pointers into `using-superpowers/references/`, which
violate our bare-skill-name invariant. Nothing to take.

## Ranked findings

### 1. SDD workspace has no plan identity — cross-plan ledger contamination

**Verified gap.** `scripts/sdd-workspace` resolves `$root/.sdd`, flat, with no
plan in the path. Upstream observed a follow-up plan in the same working tree
reading the previous plan's ledger as its own progress, and moved to a
per-plan directory.

This repo is the configuration that bug needs: plans are sequentially numbered
into one `specs/plans/` directory and executed in the same working tree. The
next plan is id 22.

Adoption is surgical and composes with our local reworks:

- `sdd-workspace` takes the plan file and resolves `.sdd/<plan-basename>/`,
  preserving our `.sdd` rename from `c5ff0b5`.
- `task-brief` passes the plan through. Upstream's change to this script is
  *only* that call — it does not touch the heading-termination or
  Global-Constraints logic we added in `b8faf9c`. **No collision.**
- The ledger names its plan on line 1; the workspace is deleted once the final
  review is clean.

**Conflict to plan around:** `review-package` gains `PLAN_FILE` as its **first
positional argument**, shifting `BASE`/`HEAD`. That is a breaking signature
change pinned by our 14 dispatch-script tests and documented in the SKILL.md
`DIFF_FILE` contract from `6a803cd`. Scripts, tests, and call sites move
together or not at all.

### 2. Implementer subagents can spawn duplicate reviewers

**Verified gap, with a cost impact.** Our implementer is dispatched as
`Subagent (general-purpose)` (`implementer-prompt.md:6`), which carries the full
tool set including subagent dispatch, and the prompt contains no prohibition.
An implementer that decides "an independent review would strengthen my report"
duplicates a review the controller has already scheduled, at full cost, for a
verdict that counts for nothing.

Upstream added an explicit "You Do Not Dispatch Subagents" block to both the
implementer and reviewer prompts.

**Our reviewer coverage is real but conditional.** `agents/code-reviewer.md` and
`agents/task-reviewer.md` both declare `tools: Read, Grep, Glob, Bash` — no
Agent tool at all, a structural guarantee where upstream has only prose. But
both reviewer templates route conditionally:
`task-reviewer-prompt.md:10` dispatches to the `task-reviewer` agent *if it is
defined*, else falls back to `general-purpose` with the Full Form;
`requesting-code-review/code-reviewer.md:8` does the same. That fallback exists
so the skills work standalone, and it was a deliberate choice (`068b6c1`).

So the exposure is:

| Seat | Restricted path | Fallback path |
|---|---|---|
| Task reviewer | `task-reviewer` agent — safe | `general-purpose`, no ban |
| Final reviewer | `code-reviewer` agent — safe | `general-purpose`, no ban |
| Implementer | none — always `general-purpose` | no ban |

In this repo the agents are defined, so both reviewer seats take the safe path
today. The prose ban is what protects the implementer always, and both
reviewers whenever these skills run somewhere the agents are absent.

### 3. TDD reference has no falsifiability discipline

We still ship `testing-anti-patterns.md`; upstream replaced it with
`writing-good-tests.md`, rebuilt as a positive catalog around two principles —
name the break, exercise the real thing — plus gate functions, a mutation
check, and a warning-signs list.

Two named traps are **absent from our copy**:

- **String-presence.** Grep-style assertions on scripts, skills, and prompts
  counterfeit falsifiability; the observable is behavior, never text.
- **Change-detector.** A constant assertion can fail and still protect nothing.

The first is pointed directly at a repo whose product *is* skill text and shell
scripts.

**Our existing suites are clean on it.** The `read_text()` calls in the SDD,
ADR-scaffolder, and explore-data tests all read *generated output* — the brief a
script produced, the ADR it wrote — which is behavior testing. No test asserts
on skill or script source text. So the value here is prospective guidance, not
remediation.

**Do not adopt the compression naively.** Upstream measured that deleting TDD's
"Why Order Matters" section outright degraded test-first behavior under
"just write it, tests after" pressure — control 8/10 → treatment 5/10,
corroborated on two models — and shipped only after converting each rebuttal
into a Common Rationalizations row. Our `SKILL.md:194` still has the full
section *and* a rationalizations table, so **we never shipped that regression.**
Any compression pass here has to clear the bar upstream set.

### 4. Brainstorming ceremony does not scale, and is out of step with our own policy

Our brainstorming runs one path: a 9-step checklist ending in a committed spec
file, a user review, and a fresh-session handoff — for every request, including
a config change. `SKILL.md:21` actively forecloses scaling with
*"Anti-Pattern: This Is Too Simple To Need A Design"*.

Upstream now classifies each request as **spike / bounded / architectural**,
announces the classification for the partner to override, and sends only
architectural work through the full spec process.

This is worth attention less because upstream changed it than because **it
converges on the proportional-process policy already recorded for this repo**
(brainstorming and specs only for open design decisions; minor work fixed
directly). That policy currently lives in `/deferred`, while the brainstorming
skill still argues the opposite.

Upstream did **not** weaken the gate, which is the part that makes it adoptable:
*"What scales with simplicity is the artifact, never the approval."* Every path
still stops for approval before implementation. It ships with a one-way ratchet
(hidden complexity upgrades the path mid-task, nothing downgrades) and a
seven-row rationalization table defending against the obvious failure mode of
reaching for the "bounded" label to skip work.

A port must keep our repo-specific lifecycle — the `specs/` conventions, the
`deferred_items.md` check, the fresh-session handoff — as what the
*architectural* path routes into.

### 5. Every task gets its own dispatch, however small

**Verified gap.** Our only uses of "batch" are batching *questions to the human*
(`SKILL.md:100`, `:222`). There is no notion of batching *work*.

Upstream now composes one dispatch for several tasks that are each a small,
independent edit of the same kind — the same one-line fix, constant change, or
field addition repeated across files — and reviews that diff as one unit,
reserving per-task dispatch for work needing its own judgment, tests, or review
surface.

This repo is where that saving lands. `writing-plans` has a dedicated
`Bite-Sized Task Granularity` section (`:49`); a repo that writes bite-sized
tasks by policy is one where per-task dispatch overhead dominates on
mechanical plans.

The safeguard travels with it: a batched review must check the diff file by
file against the brief's list, and a listed file the diff never touches is a
Missing finding no matter how clean the rest looks. Without that, batching
trades cost for silent omissions.

### 6. SDD review loop has no round cap and no scoped re-review

Ours sends findings back and re-reviews (`SKILL.md:160`) with no bound. Upstream
added three things:

- **Resume the implementer** rather than dispatching fresh, with the implementer
  appending a fix report — what changed, the covering tests, the command, the
  output — to its existing report file.
- **A scoped `re-review-prompt.md`** (115 lines) that returns per-finding
  ADDRESSED / NOT ADDRESSED verdicts, so the re-reviewer checks the fixes
  instead of re-reading the whole task.
- **A five-round circuit breaker** with escalation: rounds 1–3 resume the
  implementer, rounds 4–5 dispatch a fresh implementer on a more capable model,
  and at round 5 the controller adjudicates each open finding. That escalation
  ladder is congruent with this repo's own model-routing policy, which already
  escalates per-diff rather than per-session.

A fourth change lands on the reviewer templates: **evidence you cannot see is
not evidence that doesn't exist.** A reviewer that finds a report truncated or
its test results unlocatable must re-read the file at its stated path and report
a genuine gap, rather than re-running the suite to regenerate what it failed to
read. Re-running is not verification.

**Two of our files, not one.** We carry both the skill-level
`task-reviewer-prompt.md` and the distilled `agents/task-reviewer.md`, and the
template's Short/Full split means the contract lives in the agent definition on
one path and in the prompt on the other. Any reviewer-contract change has to
land on both or it silently applies to only one dispatch path.

Developed against upstream's SDD structure, which ours has diverged from. This
is a port, not a merge.

### 7. Pre-flight conflicts always stall for a human — partially by our design

Upstream v6.3.0 lets non-catastrophic plan conflicts take a *recorded ruling* so
work continues, reserving human stops for destructive or irreversible actions.
Their motivating case: a donated session blocked almost nine hours on a question
the controller could have decided.

The mechanism is specific enough to evaluate. Rulings go in the ledger as
`Ruling: <what you decided> — <why> — <what it costs if wrong>`, the spec is
binding authority and the plan its argument, and exactly four things still stop
the run: an irreversible or destructive operation, a security-sensitive action,
a side effect outside the worktree that norms say you ask about first, and a
plan so broken every path forward is a guess. The pre-dispatch conflict scan
also records its checks in the ledger rather than merely asserting the plan is
clean.

Ours (`SKILL.md:92`) is already better than upstream's pre-fix state — it
batches all conflicts into one question *before* execution rather than
interrupting per discovery. But it still blocks the start on any conflict.

**Flagging a tension rather than a gap.** `SKILL.md:222` calls that gate "this
skill's one deliberate human [checkpoint]". Auto-ruling erodes a deliberate
local design choice. Worth a decision, not an assumed adoption.

### 8. Smaller items

- **`find-polluter.sh` is broken in our tree.** `find .` emits `./`-prefixed
  paths, so the documented `-path "src/**/*.test.ts"` pattern matches nothing,
  and `wc -l` on empty input then reports "Found 1". Ours has both bugs. Port
  the fix rather than the file — ours carries a local `TEST_CMD` addition
  upstream lacks. The fix is three parts: strip a caller-supplied `./` so it
  cannot double-prefix, match both the `./`-prefixed pattern and one with `**/`
  collapsed (so `src/top.test.ts` isn't skipped by `src/**/*.test.ts`), and
  branch on empty output so the count is 0 rather than 1. Upstream also added a
  deterministic test suite, which fits our directory-scoped convention.
- **Plan `Spec:` header pointer.** Upstream plans carry a spec path so SDD can
  resolve conflicts against the design instead of guessing. We have no formal
  pointer, though our naming convention already couples them. Small, and it
  composes with finding 1.
- **`finishing-a-development-branch` still advertises "Discard this work" in
  both completion menus** — last option in each (`SKILL.md:88` in the 4-option
  normal-repo menu, `:100` in the 3-option detached-HEAD menu). Upstream
  demoted discard to
  explicit-request-only, on the grounds that advertising it next to "Merge"
  offers to destroy finished, passing work. We do have the typed-confirmation
  ritual; the issue is the menu placement.
- **No untracked-file guard on worktree removal.** Upstream stops and names the
  files when `git worktree remove` refuses, instead of reaching for `--force`.
  Our risk is lower — we never reach for `--force` outside discard — but the
  refusal case is unhandled.
- **`using-git-worktrees` guard content exists in the older Problem/Fix form**
  (`:178`, `:197`) rather than the house Excuse/Reality table. Format
  convergence only.
- **PR creation is `gh`-specific** (`:73`, `:136`). Upstream went
  forge-agnostic. Low value for a GitHub-only workflow.

**Checked, no action:** `brainstorming/visual-companion.md` changed 9 lines
upstream. `NOTICE` records that we removed its remote brand-image fetch and
telemetry toggles, making it the one file where an upstream change could quietly
reintroduce something dropped on purpose. It does not: the change is entirely
Copilot CLI backgrounding guidance for Windows. Our removal is intact and no
network call or telemetry toggle returns.

## Suggested disposition

Under this repo's proportional-process rule these do not all belong in one spec.

- **Fix directly, no spec:** finding 8's `find-polluter.sh` bug. Three small
  corrections to a script that currently cannot work, plus a test.
- **Spec candidate — SDD hardening:** findings 1, 2, 5, and 6 share the SDD
  surface, the three dispatch scripts, the two reviewer templates, and the
  14-test suite. The `review-package` signature change makes them one
  coordinated edit rather than four independent ones.
- **Spec candidate, separate — brainstorming ceremony:** finding 4 is a
  behavior-shaping change to a discipline skill that touches our specs
  lifecycle. It needs its own pressure-test and micro-test against a
  no-guidance control before deployment, per `writing-skills`.
- **Decide, don't assume:** finding 7 conflicts with a deliberate local design
  choice.
- **Prospective only:** finding 3. Adopt the falsifiability material if you want
  the guidance; do not take the compression without clearing upstream's
  measured bar.

Any adoption needs a `NOTICE` change-list entry. The current entry pins the
vendoring at `896224c` and describes our two local script reworks; taking
plan-scoping means the `sdd-workspace` and `task-brief` bullets both need
rewriting to say what is ours and what is upstream's.
