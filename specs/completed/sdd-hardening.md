# SDD hardening

**Status: COMPLETE (2026-09-03)** — implemented by
[plan 22](../plans/completed/22-sdd-hardening.md); retired to
`specs/completed/`. Eight Minor findings and one adjudicated duplication
recommendation were consciously deferred to `specs/deferred_items.md` at
the 2026-09-03 completion gate.

Adopt four changes from superpowers v6.1.0–v6.3.0 into
`skills/subagent-driven-development`, its three dispatch scripts, and its two
reviewer templates. Sources and per-claim verification are in
`specs/superpowers-drift-2026-09-03.md` (findings 1, 2, 5, 6); this spec is
self-sufficient and does not require reading it.

These four travel together because they touch the same files: the three
scripts, both reviewer prompt templates, `SKILL.md`, and the 14-test suite in
`scripts/test_sdd_scripts.py`. Splitting them means editing the same files
twice.

## Problem

**1. The workspace has no plan identity.** `scripts/sdd-workspace` resolves a
flat `<repo-root>/.sdd`. `SKILL.md:274` tells a resuming controller to read
`.sdd/progress.md` and treat tasks listed complete as DONE. Two plans executed
in the same working tree therefore share one ledger, and the second reads the
first's completions as its own. This repo is exactly that configuration: plans
are sequentially numbered into one `specs/plans/` directory and executed in the
same tree. Upstream observed this failure in the wild.

**2. Subagents can spawn duplicate reviewers.** The implementer is dispatched as
`Subagent (general-purpose)` (`implementer-prompt.md:6`) with the full tool set
and no prohibition. An implementer that decides an independent review would
strengthen its report duplicates a review the controller has already scheduled,
at full cost, for a verdict that counts for nothing in the process.

Coverage of the reviewer seats is real but conditional.
`agents/code-reviewer.md` and `agents/task-reviewer.md` both declare
`tools: Read, Grep, Glob, Bash`, with no Agent tool — a structural guarantee.
But `task-reviewer-prompt.md:10` routes to the `task-reviewer` agent *if it is
defined*, else falls back to `general-purpose` with the Full Form, and
`requesting-code-review/code-reviewer.md:8` does the same. In this repo the
agents are defined, so both reviewer seats are safe today. The prose ban is what
protects the implementer always, and both reviewers wherever these skills run
without the agent definitions installed.

**3. Every task gets its own dispatch, however small.** The skill has no notion
of batching work; its only uses of "batch" concern batching questions to the
human (`SKILL.md:100`, `:222`). `writing-plans` has a dedicated
`Bite-Sized Task Granularity` section (`:49`), so plans here are written as many
small tasks by policy — the case where per-task dispatch overhead dominates.

**4. The review loop is unbounded.** `SKILL.md:160` sends findings back and
re-reviews with no round cap, no scoped re-review, and no escalation. A
re-reviewer re-reads the whole task rather than checking the fixes.

## Scope

In scope: `skills/subagent-driven-development/` (SKILL.md, both prompt
templates, all three scripts, the test suite), a matching ban in
`skills/requesting-code-review/code-reviewer.md`, the two agent definitions if
the reviewer contract changes, and a `NOTICE` change-list update.

Out of scope, and deliberately so:

- The brainstorming ceremony router (drift finding 4) — its own spec, because it
  needs a micro-test against a no-guidance control.
- Rulings-instead-of-stalls for pre-flight plan conflicts (drift finding 7) —
  conflicts with a deliberate local design choice recorded at `SKILL.md:222`,
  and needs its own decision.
- `find-polluter.sh` (drift finding 8) — an unrelated broken script, fixed
  directly under the proportional-process rule.
- Upstream's compression campaign. Not adopted anywhere in this spec.

## Execution constraint: this plan edits its own machinery

**This plan must be executed from a git worktree, not the main checkout.**

`~/.claude/skills/` holds per-skill symlinks into this repo, so edits here are
live. Verified:

```
~/.claude/skills/subagent-driven-development
  -> /Users/lowell/Projects/agent-skills/skills/subagent-driven-development
~/.claude/agents/task-reviewer.md
  -> /Users/lowell/Projects/agent-skills/agents/task-reviewer.md
```

If subagent-driven-development executes this plan from the main checkout, the
controller's own tools change under it mid-run. Two concrete failures:

- The task that changes `review-package` to require `PLAN_FILE` breaks the
  controller's very next review call, which still passes `BASE HEAD` and now
  exits 2.
- The workspace path moves from `.sdd/` to `.sdd/<plan-slug>/` mid-plan,
  orphaning the in-flight ledger. A resume after compaction reads the new path,
  finds no ledger, and re-dispatches completed tasks — the failure `SKILL.md:267`
  names as the single most expensive one observed.

Both symlinks resolve to the **main checkout's** path, so work done in a
worktree leaves the live skill pinned to `main` until the branch merges. Use the
using-git-worktrees skill before starting.

Executing with executing-plans instead also avoids the hazard, since that skill
never calls the three scripts. The worktree is the better option because these
changes want per-task review, but either is safe. Executing with
subagent-driven-development from the main checkout is not.

## Design

### A. Plan-scoped workspace

`sdd-workspace` takes the plan file as its only argument, derives a slug from
its basename with the `.md` extension stripped, and resolves
`<repo-root>/.sdd/<slug>/`. It exits 2 with a message on stderr when the
argument count is not exactly 1, when the plan file does not exist, or when the
slug is empty, `.`, or `..` — the three basenames that would escape or collapse
the intended directory.

The self-ignoring `.gitignore` **stays where it is**, at `.sdd/.gitignore`.
Today `sdd-workspace` writes it into the directory it returns, which is `.sdd`;
under the new layout it must be written to the `.sdd` parent explicitly rather
than to the returned per-plan directory, so one guard keeps covering every
sibling. The path does not change — the code that produces it does. The
repo-level ignore at `.gitignore:21` and its comment about duplicating that
guard both stay accurate.

`task-brief` and `review-package` pass the plan through to `sdd-workspace`
rather than calling it bare. Neither script computes the workspace path itself;
`sdd-workspace` remains the single source of truth.

Call sites in `SKILL.md` change with them. `SKILL.md:274` currently hardcodes
`.sdd/progress.md`; the ledger is per-plan, so the documented resume command
must derive its path from `sdd-workspace` with the plan file rather than
hardcoding a flat path. The ledger names its plan on its first line, so a
controller reading a ledger can confirm it belongs to the plan in hand.

### B. No nested subagents

Add a "You Do Not Dispatch Subagents" section to `implementer-prompt.md` and to
**both** forms of `task-reviewer-prompt.md`, and to
`requesting-code-review/code-reviewer.md`.

The implementer's version states that self-review means reading its own diff,
that review is the controller's job and is already scheduled, and that a
reviewer it spawns duplicates that review at full cost with a verdict that
counts for nothing. The reviewers' version states that a reviewer never spawns
a second opinion, and that a diff too large for one pass is reviewed in
several passes by the same reviewer, said so in the report.

The Short Form's contract lives in the agent definition, so the ban must land in
`agents/task-reviewer.md` and `agents/code-reviewer.md` as well, or it applies
only on the Full Form path. Both files get it, even though their `tools:` lines
already make spawning impossible — the prose is what travels when these skills
are installed without the agents.

Reviewers additionally get the illegible-evidence rule: evidence you cannot see
is not evidence that does not exist. A reviewer that finds a report truncated or
its test results unlocatable re-reads the file at its stated path, and reports a
genuine gap for the controller if it is truly missing. Re-running the suite to
regenerate what it failed to read is not verification.

### C. Batch small same-shape work

When a plan lists several tasks that are each a small, independent edit of the
same kind — the same one-line fix, constant change, or field addition repeated
across files — the controller composes one dispatch brief listing every file and
its change, sends the batch to a single implementer, and reviews the resulting
diff as one unit. One dispatch per task is reserved for work needing its own
judgment, its own tests, or its own review surface.

**`task-brief` does not gain a multi-task mode.** It keeps extracting exactly
one task by number. The controller writes the batch brief itself, listing each
file and its change inline. This is a deliberate exception to the
keep-task-text-out-of-the-controller's-context rule that `task-brief` exists to
serve: batching is only ever applied to changes small enough to state in a line
each, so the context cost is small and bounded, and the alternative — teaching
`task-brief` to concatenate task sections — would pull full task text through
the controller for exactly the tasks that need it least.

The safeguard travels with the feature and is not optional: a batched review
checks the diff against the brief's file list **file by file**, and a listed
file the diff never touches is a Missing finding regardless of how clean the
rest of the batch looks. Without it, batching trades cost for silent omissions.
This rule goes in both forms of `task-reviewer-prompt.md` and in
`agents/task-reviewer.md`. It does **not** go in `agents/code-reviewer.md`:
batching is per-task, and that agent reviews the whole branch.

The ledger records a batched dispatch as one entry naming every task number it
covered, so a resuming controller does not re-dispatch a task that was completed
inside a batch.

### D. Bounded review loop

Add `re-review-prompt.md`, a scoped template whose reviewer receives the prior
round's findings and the new diff, and returns a per-finding verdict of
ADDRESSED or NOT ADDRESSED plus any new findings the fixes introduced. It does
not re-review the whole task.

Fix rounds are capped at five and escalate:

There are **five fix attempts**, and adjudication happens after the fifth comes
back dirty — it is not itself an attempt.

| Round | Action |
|---|---|
| 1–3 | Resume the same implementer with the findings. It appends a fix report to its existing report file: what changed, the covering tests, the command, and the output. |
| 4–5 | Dispatch a **fresh** implementer with the task brief and the findings. Escalate reasoning effort if the prior rounds show a thorough attempt rather than a context gap. |
| after 5 | The cap is reached. The controller adjudicates every still-open finding; no further fix rounds are dispatched for this task. |

Adjudicating means the controller rules on each open finding, recording
load-bearing ones as work and parking the rest in the ledger with its reasoning.
It stops for a human only when every path forward is a guess.

Resume-then-fresh is the load-bearing half. A resumed implementer carries its
own failed attempts as context, which anchors it to the approach that is not
working; a fresh one does not. This is the repo's existing "go horizontal —
fresh context" response to being stuck, applied at a structural trigger.

Escalation follows the repo's own order — context, then effort, then model — and
stops when there is no headroom. The headroom that matters is the tier the
failing implementer was dispatched at, not the controller's session model, which
a subagent never inherits: Model Selection requires an explicit model on every
dispatch and floors prose implementers at standard, so an implementer that has
failed three rounds is often below capable and still has the model rung. This
spec does not adopt upstream's unconditional "dispatch on a more capable model"
wording — the rung is conditional on that tier, and rounds 4-5 buy fresh context
and higher effort only when the implementer is already capable.

### E. Workspace lifecycle

When the final whole-branch review is clean and its fixes are merged, delete
**this plan's** workspace directory. Sibling directories belong to other plans
and are left alone. Git history is the durable record.

Sequencing is load-bearing: the delete runs **after** the plan-completion
protocol at `SKILL.md:217`, never before. That protocol reads the run's
leftovers — unfixed review findings, deferred-Minor confirmations — to build its
gate questions and the `specs/deferred_items.md` entries. Deleting the workspace
first destroys its input.

## Decisions

**`review-package` takes PLAN_FILE as its first argument**, matching upstream:
`review-package PLAN_FILE BASE HEAD [OUTFILE]`.

The deciding argument is internal consistency, not upstream alignment.
`task-brief` already takes the plan as argument 1 and `sdd-workspace` will too,
so this makes all three scripts uniform — which matters because their purpose is
to be one source of truth for workspace location.

Appending the plan instead was rejected as actively unsafe. Today a three-
argument call means `BASE HEAD OUTFILE`; under that scheme it would mean
`BASE HEAD PLAN_FILE`. Same arity, different meaning, and the file-existence
check catches it only when the OUTFILE path happens not to exist. An
environment variable was rejected for hiding a dependency that both sibling
scripts state positionally.

**Escalation rungs are this repo's, not upstream's** — see § D. Upstream
escalates to a more capable model unconditionally at round 4; here that rung is
taken only when the failing implementer was dispatched below capable. The
structural insight is kept: three failed fix rounds on the same findings is
task structure, not per-prompt self-assessment, and is the precondition the
repo's routing policy already names for escalation.

## Testing

`scripts/test_sdd_scripts.py` has 14 tests; 6 call sites exercise the changing
surface. Required changes:

- Every `review-package` invocation gains the plan argument.
- Both `sdd-workspace` tests currently invoke the script with **no arguments**
  and will exit 2 under the new signature. Both need a plan file passed.
  `test_workspace_is_created_inside_the_working_tree` must also assert the
  per-plan directory rather than a flat `.sdd`.
- In `test_workspace_ignores_itself_so_artifacts_never_reach_git_status` the
  `.sdd/.gitignore` assertion stays correct, because the guard stays at that
  path; its invocation and its scratch-file path still change. Add an assertion
  that the guard sits at the `.sdd` parent and not inside the per-plan
  directory, since that is the part the new code could get wrong.
- Both default-workspace-path tests, one for `task-brief` and one for
  `review-package`, assert the per-plan directory.
- The two `task-brief` argument-error tests keep their current arity; that
  script's signature does not change.

New tests: `sdd-workspace` rejects a missing plan file and an unusable
basename; two different plan files resolve to different directories; the same
plan file resolves to the same directory twice.

Run from inside the script directory, per the repo's directory-scoped
convention:

```bash
cd skills/subagent-driven-development/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

The prose changes in § B, C, and D are skill text, not code. They are verified
by reading, not by tests that grep for their wording — an assertion that a
phrase appears in `SKILL.md` would pass without the behavior existing.

## Provenance

All four changes are adapted from superpowers (MIT, © 2025 Jesse Vincent;
`LICENSE-superpowers`). `NOTICE` must be updated: its current entry pins the
vendoring at `896224c` and describes the two local script reworks (`c5ff0b5`,
`b8faf9c`). After this work the `sdd-workspace` and `task-brief` bullets both
need rewriting to distinguish what is ours from what came from upstream, and the
new `re-review-prompt.md` needs listing. The bare-skill-name invariant holds:
nothing adopted here may reintroduce the `superpowers:` namespace, and
upstream's cross-references use it.
