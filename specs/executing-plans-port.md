# executing-plans port: a ledgered inline executor, rulings mid-run, and what green means

> For agentic workers: REQUIRED NEXT SKILL: writing-plans. Plan this spec in a fresh session.
> Do not build from this file directly.

**Status: DRAFT (2026-10-31), for owner review.** Designed with the owner through the
brainstorming skill. The owner chose the routing (O1) and the approach (O2) in this session.
Items marked **(my call)** are the designer's choices, for the owner to check at review.

## Intent

This spec settles one backlog item: "Write the executing-plans port spec"
(`specs/deferred_items.md`, section `owner-calls-2026-10-21`). It covers three findings of
`specs/superpowers-drift-spec.md`, the record of upstream changes to the 13 skills that this
repository adapts from Jesse Vincent's superpowers (MIT).

1. **Finding 11.** Upstream v6.4.1 (obra/superpowers PR #2318) rebuilt executing-plans. The
   new skill keeps a progress ledger in the same workspace as subagent-driven-development
   (SDD). It reads each task through a `task-start` script, and it closes each task through a
   `task-done` script that writes the ledger line only when the tests pass. Our copy is the
   old stub. Its progress lives in todos, so a `/clear` or a compaction loses its place. That
   is the failure that plan 22 fixed for SDD.
2. **Finding 7.** The owner decided on 2026-10-21: rulings mid-run only. Pre-flight keeps its
   one batched question. A mid-run conflict between a reviewer finding and the plan text gets
   a recorded ruling, and the run continues. This decision is not applied anywhere yet.
   `skills/subagent-driven-development/references/fix-loop.md:51-55` still calls such a
   conflict "the human's decision".
3. **Finding 13.** Upstream v6.4.1 (#2110) found that when a task named one test file, the
   session ran only that file in 11 of 12 probe runs, so a broken neighbor test went unseen.
   Our TDD skill stops at "Other tests fail? Fix now."
   (`skills/test-driven-development/SKILL.md:176`) and does not say what "other tests" means.

The three travel together. The ported executor needs rulings to run without stalls, and its
`task-done` line claims "tests pass", which finding 13 defines.

Why now: plans 71-73 finished the SDD and writing-skills work that this port waited on. No plan
is executing. Upstream has not changed executing-plans, test-driven-development or
subagent-driven-development since v7.0.1 (`2ce8aa1`), which is the port's source.

## Owner decisions

Each line records the option that the owner picked, in the owner's terms.

- **F7** (owner, 2026-10-21): rulings mid-run only. Pre-flight keeps its one batched
  question, asked while the partner is present at launch. A mid-run reviewer finding that
  conflicts with plan text takes a recorded `Ruling: <what you decided> — <why> — <what it
  costs if wrong>`, and the run continues. Upstream's four stops still stop the run, and so
  does the explicit scope fence.
- **O1** (owner, 2026-10-31): keep the routing by tight coupling. executing-plans stays the
  executor for tightly coupled plans, for direct execution that the partner asked for, and
  for platforms with no subagent tool. Upstream's routing by cost is not adopted.
- **O2** (owner, 2026-10-31): approach A, "port upstream's file, then add our pieces to it"
  (section Approaches).
- **O3** (owner, 2026-10-31): option (a), narrow. Unit 3 changes only SDD's `fix-loop.md` and
  `final-review.md`, as F7's text says. `subagent-driven-development/SKILL.md:28` and
  `references/handling-reports.md:13` stay as they are.

## Goals

- **G1.** executing-plans keeps a ledger in SDD's per-plan workspace, `.sdd/<plan-basename>/`,
  in SDD's format. A plan can change executors in mid-run, and either executor resumes from
  the other's ledger.
- **G2.** Each task opens with `task-start` and closes with `task-done`. `task-done` writes
  the completion line only when the task's test command exits 0, and it records a silent pass
  as `(no output)`.
- **G3.** executing-plans rules on mid-run conflicts and continues. Only the four stops and
  the explicit scope fence stop its run. SDD rules on a mid-run conflict between a reviewer
  finding and the plan text, and carries the same five stops for those rulings. SDD's other
  stop rules do not change (O3).
- **G4.** TDD says that the project's documented test command(s) define green, that a task's
  scope bounds the deliverable and not the verification, and that every failure is reported
  by name.
- **G5.** The ported executing-plans body fits the compaction window with margin.
- **G6.** Every ported change has a `NOTICE` change-list line, and every wording change to a
  discipline skill has a registered micro-test with a control arm.

## Non-goals

- **Routing by cost** (O1). The descriptions of executing-plans and SDD, writing-plans'
  Execution Choice, brainstorming and the README keep the routing that `977a61a` unified.
  Revisit if: a measured comparison of SDD and inline cost on a real plan of this repository
  shows that inline execution is cheaper at equal quality.
- **Workspace collisions** (finding 12, deferred item M2). Plans that share a basename still
  share a workspace. The ledger's `Plan:` line keeps a collision visible. Upstream's
  `plan-path` marker scheme stays the ready port if M2 is revisited.
- **Pre-flight rulings.** Pre-flight still asks one batched question (F7). Upstream rules on
  each pre-flight conflict instead.
- **The nested controller** (finding 14). It stays declined, because pre-flight still asks.
- **Upstream's byte bar** (finding 17). The `compaction-window` check stays the gate.

## Anti-goals

The port fails, even if it runs, if any of these happen:

- Upstream text silently undoes a local decision. The known cases are in section "Upstream text
  that must not come across".
- "Rulings, not stalls" grows into "never stop". A destructive step, a security-sensitive
  action, an outside side effect, a broken plan or a scope-fence breach must still stop the run.
- A task is marked complete on a test run that did not cover the project's documented command.
- The ledger formats of the two executors drift apart, so one cannot resume the other's run.

## Approaches

| | A. Port upstream's file, then add our pieces (picked, O2) | B. Keep our file and add the new parts |
|---|---|---|
| Start from | upstream v7.0.1 `skills/executing-plans/SKILL.md` | our current 151-line file |
| Keeps | upstream's tuned wording: the task loop, the completion contract, the rationalizations table, the narration and bookkeeping rules | our six-step structure |
| Costs | more upstream text to credit, more edits that remove upstream content | an unmeasured hybrid. Later drift reviews compare two unlike files claim by claim |

A third approach, upstream's file without our local pieces, was ruled out by the backlog item,
which keeps those pieces.

Approach A was picked because upstream's text is the evaluated part. Upstream rebuilt the
skill because the old stub "measured the same as running with no plugin at all". A port that
keeps upstream's structure also keeps later drift reviews cheap.

## Design

The design has four units. Each unit can be built and tested alone. Unit 4 depends on units 1
and 3 for its wording, and on unit 2 for its scripts.

### Unit 1: TDD defines green (finding 13)

**Where:** `skills/test-driven-development/SKILL.md`, after "**Other tests fail?** Fix now."
(`:176`).

**What:** a new paragraph adapted from upstream's #2110 paragraph
(`2ce8aa1:skills/test-driven-development/SKILL.md:185-193`), with one change. Upstream says to
run "the project's test command (bare `pytest`, `npm test`, `cargo test` — whatever the repo
uses)". This repository has no root runner, and a repo-root `pytest` collection fails outright
on the colliding `test_build.py` basenames (`CLAUDE.md`, Commands). So the paragraph must say
that the project's **documented** test command(s) define green. That is what the project's
`CLAUDE.md`, `AGENTS.md`, README or CI runs. When a project documents per-directory suites,
green means each documented suite that the change can reach. The paragraph keeps upstream's
other two claims unchanged in meaning:

- A task's scope bounds the deliverable, not the verification.
- Every failure in that run is reported by name, including one the session did not cause. A
  documented skip or a known environment failure is named too, not passed over.

The bare-`pytest` examples at `:120`, `:166`, `:296` and `:310` stay. They show a single-test
run, which is correct for RED and GREEN of one test.

**Test:** micro-test cases G1 and G2 (section Testing).

### Unit 2: the two scripts (finding 11)

**Where:** `skills/executing-plans/scripts/task-start` and `skills/executing-plans/scripts/task-done`,
both executable bash, with `skills/executing-plans/scripts/test_executing_plans_scripts.py`.

**Source:** upstream `2ce8aa1:skills/executing-plans/scripts/{task-start,task-done}`.
`task-done` is taken as fixed in v7.0.0 (#2388, `907ad21`): a passing command that prints
nothing records `→ (no output)` instead of exiting 1 under `set -euo pipefail`.

`task-start PLAN_FILE N`:

- Calls `../../subagent-driven-development/scripts/task-brief PLAN_FILE N`, reads the path from
  its `wrote <path>: <n> lines` line (`task-brief:86`), and prints `brief: <path>` and
  `base: <full SHA of HEAD>`.
- Exits 2 on wrong arguments, and 1 when `task-brief` prints no path.

`task-done PLAN_FILE N BASE -- TEST_COMMAND [ARGS...]`:

- Exits 2 on wrong arguments or on a BASE that `git rev-parse --verify` rejects.
- Resolves the workspace through `../../subagent-driven-development/scripts/sdd-workspace`.
- Runs the command in the caller's working directory, writes the full output to
  `<workspace>/task-<N>-tests.log`, and prints the last 5 lines.
- On a non-zero exit, records nothing, prints `Task <N> NOT recorded` and the log path to
  stderr, and exits with the command's status.
- On exit 0, appends `Task <N>: complete (commits <base7>..<head7>, tests: <command> → <last
  non-blank line, or (no output)>)` to `<workspace>/progress.md`.

Two local changes to upstream's `task-done`:

1. **The ledger's first line is ours.** When `progress.md` is absent, `task-done` creates it
   with SDD's first line, `Plan: <plan-file-path>` (`subagent-driven-development/SKILL.md`,
   Durable Progress). Upstream writes `# SDD ledger — plan: <path>`. A different first line
   would stop SDD from resuming an executing-plans run.
2. **A ledger of another plan is refused (my call).** When `progress.md` exists and its first
   line names a different plan file, `task-done` records nothing and exits 3. This matches
   SDD's rule to "stop and say so" (`references/resuming.md:5-7`). The comparison rule
   **(my call, after the builder check)**:
   - `PLAN_FILE` resolves against the caller's working directory.
   - A relative `Plan:` value resolves first against the repository root
     (`git rev-parse --show-toplevel`), then against the working directory. An absolute value
     is used as it is.
   - The two match when either resolution of the `Plan:` value and `PLAN_FILE` name the same
     file (both canonicalized, symlinks resolved). Otherwise `task-done` exits 3 and prints
     both paths.
   - A new ledger gets `PLAN_FILE`'s path relative to the repository root, which SDD
     controllers also write in practice. SDD's Durable Progress text does not change.

   Test cases: an absolute `Plan:` value against a relative argument matches; a call from a
   subdirectory matches; a different plan exits 3.

The test command runs in one working directory. In a project whose suites run from their own
directories, the brief names a command that runs them from the root. In this repository that
is `uv run python build/run_suites.py <name> [<name> ...]`.

**Tests**, in this repository's convention: pytest drives the bash scripts as subprocesses with
the sanitized `GIT_ENV` of `test_sdd_scripts.py`, in a scratch repository under `tmp_path`.
The cases adapt upstream's `2ce8aa1:tests/claude-code/test-executing-plans-scripts.sh`:

| Case | Asserts |
|---|---|
| start, bad arguments | exit 2 |
| start, brief | prints `brief: <repo>/.sdd/plan/task-1-brief.md`, the file exists and is not empty |
| start, BASE | prints `base: <HEAD>` |
| done, pass | appends the exact completion line, prints the output's tail, keeps the full log |
| done, fail | non-zero exit, no `Task 2: complete` line, the failing output is shown |
| done, silent pass (#2388) | exit 0, the line ends `→ (no output))` |
| done, new ledger | the first line is `Plan: <plan-file-path>` |
| done, other plan's ledger | exit 3, ledger unchanged |
| done, bad arguments and bad BASE | exit 2 |

The suite gets its own entry in `build/suites.toml` (name `executing-plans`, dir
`skills/executing-plans/scripts`, with `pytest`), because `run_suites.py --check` is a commit
lint. Each test must be seen failing before its script code exists (TDD).

**Dependency:** executing-plans now calls SDD's scripts by a `../subagent-driven-development/`
path. Add `skill:subagent-driven-development` to `skill:executing-plans` in `install.py`'s
`DEPENDENCIES`. The dependency-drift test fails without it.

### Unit 3: rulings mid-run in SDD (finding 7)

**Where:** `skills/subagent-driven-development/references/fix-loop.md:51-55` and
`skills/subagent-driven-development/references/final-review.md:34-37`.

**fix-loop.md.** Replace the plan-mandated bullet with upstream's v7.0.1 wording
(`2ce8aa1:skills/subagent-driven-development/references/fix-loop.md:14-19`), in our ruling
format. In meaning: a finding labeled plan-mandated, or any finding that conflicts with what
the plan text requires, is yours to rule on. Weigh the finding against the plan text, decide
with the spec as the binding authority, and ledger `Ruling: <what you decided> — <why> — <what
it costs if wrong>` before you act. Do not dismiss the finding because the plan mandates it.
Do not dispatch a fix that contradicts the plan without a recorded ruling. Then add the stop
rule from section "Stops" below.

**final-review.md.** Its gate paragraph folds "plan-mandated findings ... for your human
partner to rule on" into the plan-completion gate's questions. After this change those are
rulings already made. The gate lists them for the partner to see (the exhaustive list of
section "Rulings reach the partner"), and they are no longer pending questions. The final
review's Declined to judge lines stay questions for the partner (plan 73 decision D2).

**Not changed:** `references/preflight.md`. It keeps its one batched question (F7).

**Also not changed (O3):** SDD's two other stop rules.
`subagent-driven-development/SKILL.md:28` stops for "ambiguity that genuinely prevents
progress", and `references/handling-reports.md:13` says "If the plan itself is wrong, escalate
to the human." So SDD rules on a reviewer finding that conflicts with the plan, but still
escalates a wrong plan. The two executors differ there on purpose. Revisit if: an SDD run
stalls on a wrong-plan escalation that a ruling would have settled.

**Kept in executing-plans:** the base-branch start question of Step 1 item 5. It is asked
before Task 1, while the partner is present, as pre-flight is. executing-plans gets no
context-checkpoint handoff, as upstream has none. The ledger is its recovery **(my call)**.

### Unit 4: the executing-plans port (finding 11)

**Where:** `skills/executing-plans/SKILL.md`, rewritten, plus new files under
`skills/executing-plans/references/`.

**Base text:** upstream `2ce8aa1:skills/executing-plans/SKILL.md` (17,784 body characters),
in its order: the opening principles, When to Use, The Process (its graph), Setup, The Task
Loop, Final Review, Finish, Common Rationalizations.

**Frontmatter:** keep ours (O1). The `description`, `license` and `metadata` lines stay as they
are now, and the `# cc-guide:` comment line too.

**When to Use:** our routing (O1), not upstream's. Tightly coupled tasks, direct execution
that the partner asked for, or no subagent tool. Keep upstream's "Never fabricate a dispatch"
and its note that a fully specified plan runs well on a mid-tier session model, because that
matches our routing (execution in a fresh session on a model chosen at launch). Drop the
line that tasks are "mostly independent", which contradicts O1.

**Setup:** upstream's Setup, with these local changes.

- Workspace path `.sdd/<plan-basename>/` and SDD's script path, as `../subagent-driven-development/scripts/sdd-workspace`.
- The ledger's first line is `Plan: <plan-file-path>`. A first line that names another plan
  file means stop and say so, as SDD does. Upstream instead starts a fresh ledger beside it.
- On resume, replay the ledger's `Ruling:` and `deviation` lines for any interface a coming
  task consumes, as SDD's `references/resuming.md` does.
- Our Step 1 item 5, the base-branch start record (current `SKILL.md:32-43`), verbatim. It may
  move behind a pointer (section "Budget").
- Pre-flight: upstream's scan of the Interfaces blocks, with its ledger record (a row for each
  pair of tasks that share an interface, or `Pre-flight: no shared interfaces`) **(my call)**.
  Upstream's #2080 records the scan. The record helps a resumed session see what was checked.
  But a conflict that a row surfaces goes to the partner in one batched question before
  Task 1, as SDD's `references/preflight.md` asks (F7). It is not ruled on at pre-flight.

**The Task Loop:** upstream's four steps (take the task, work the steps, the completion
contract, complete the task). One local change: a plan-wrong ruling uses the three-part form
`Task <N>: Ruling: <what you decided> — <why> — <what it costs if wrong>` **(my call)**.
Upstream's task-loop form, `Task <N>: Ruling: <finding> — <what you decided and why>`, has no
cost clause. One format across both skills keeps the gate's list uniform. The completion
contract names the test command of unit 1: `task-done` runs the project's documented
command(s), not only the files the brief names.

**Final Review:** our Step 3 (current `SKILL.md:52-83`), not upstream's single seat. Keep
these parts:

- The two seats, launched in one message: code-reviewer on the opus tier with the plan, the
  spec path from its `Spec:` line and its `## Review Focus` section word for word, plus a
  pointer to the ledger's `Ruling:` lines (upstream has that pointer), and Codex with `--base`
  at the same merge base.
- The BASE rule, computed at review time, with the base-branch exception.
- "Touch nothing until both have returned."
- The `Codex reviewed <sha>` line, copied into the ledger as SDD's `final-review.md` does
  **(my call)**. finishing-a-development-branch reads it after the workspace is gone.
- The no-subagent case: upstream's self-review paragraph, with its ledger line
  `Final review: self-review (no subagent tool)`. The Codex seat still runs when the Codex CLI
  is there.

Then the fix pass, from upstream, with local changes **(my call)**:

- Merge both seats' lists and work them through receiving-code-review (ours).
- Fix each finding that holds up in ONE pass. Each fix is TDD-verified: a test that reproduces
  the finding fails first, then passes, then the documented command(s) run green. Ledger
  `Final: fixed <finding> — <test name> RED→GREEN, suite <result>`. A fix that changes no
  behavior (wording, a typo, a wrong name or path in prose) needs no test, as in SDD's
  `fix-loop.md` exception. No re-review (upstream).
- A finding you decide not to fix is a ruling: `Final: Ruling: <finding> — <why the code
  stands> — <cost if wrong>`.
- Leave out upstream's Minor routing ("Deferred minors"). Plan 73 decision D1 removed the
  Minor tier from the reviewers, and `requesting-code-review/code-reviewer.md` has no Minor
  label.
- The final review's Declined to judge lines go to the partner at the plan-completion gate
  (plan 73 decision D2). Upstream has the executor rule on them.

**Finish:** our Steps 4, 5 and 6 (current `SKILL.md:84-115`) in place of upstream's Finish. The
plan-completion protocol, then finishing-a-development-branch, then the roadmap-stage handoff.
Upstream's workspace deletion comes after the protocol, as SDD's `final-review.md` orders it,
because the gate reads the ledger.

**Stops:** see the section "Stops" below. It replaces our "When to Stop and Ask for Help",
"When to Revisit Earlier Steps" and the stop lines of "Remember". The new text must not keep
"Ask for clarification rather than guessing" or "Stop when blocked, don't guess" as
standing rules.

**Common Rationalizations:** upstream's table, with three changes. Drop the two Minor rows
("The reviewer said Minor, so it's Minor" and "I'll fix the minors too while I'm in there").
Recast "Let me check in before the next task" to name the five stops. Add one row
**(my call)**: "The plan says to touch that file, the fence says no, the plan is newer" →
"A fence is not a conflict to rule on. Stop and ask."

**Integration:** fold the skill list into points of use, as upstream did (`03147d2`), or keep
our Integration list. The builder chooses by the budget.

### Stops (shared by units 3 and 4)

Both executors carry the same stop rule. Rule on everything else, ledger the ruling and
continue. Stop and ask only for these five:

1. An irreversible or destructive operation.
2. A security-sensitive action.
3. A side effect outside this worktree that norms say you ask about first: a merge, a push to
   a shared branch, a publish.
4. A plan so broken that every path forward is a guess.
5. **The explicit scope fence.** A scope fence is a line in the plan (its Global Constraints,
   its header or a task) or in the partner's launch message that puts a file, a directory, a
   system or a kind of change out of bounds for this run. Examples: "Do not edit `skills/`",
   "No changes outside `build/`", "Do not change the public API". A ruling never crosses a
   fence. When the only fix crosses one, stop and ask. When a plan's task text contradicts
   one of its Global Constraints that is not a fence, the constraint wins, and that is a ruling.

The fifth stop is this repository's own. Upstream has four stops. The definition is new, so
its wording is micro-tested (case S2).

### Rulings reach the partner

Every `Ruling:` line in the ledger reaches the partner before the run ends. In both executors,
the plan-completion gate lists all of them, in the order made, each with its cost if wrong,
before the gate's questions **(my call)**. Upstream puts the list in the final message. Ours
puts it at the gate, because the gate is the one deliberate human checkpoint and it runs
before the workspace is deleted.

### Budget

Upstream's body is 17,784 characters. Our local pieces add about 3,900 (3,889 measured
2026-10-31). The bar is a body of at most 18,500 characters, which leaves 1,500 characters
of margin under the 20,000-character window. Every critical heading must start inside the
window. The critical headings are the stops, the Task Loop and the completion contract.

The proposed map, for the builder to measure and adjust:

| Stays in `SKILL.md` | Moves to a reference, behind a pointer at its step |
|---|---|
| Opening principles, the stops, When to Use, The Process graph, Setup (pre-flight included), The Task Loop, Common Rationalizations | `references/final-review.md`: the two-seat review, the fix pass, the Declined to judge routing, the rulings list, the plan-completion protocol call, workspace deletion, finishing, and the roadmap-stage handoff |
| | `references/base-branch-start.md`: Step 1 item 5, if the body needs the room |

The final-review pointer tells the executor to read the file when the last task's ledger line
is written, and again after a compaction, as SDD's references say. Upstream's Final Review
and Finish come to 3,926 characters, so the move saves the most room.

Moved text moves verbatim, and a moved-lines check confirms that every old line survives, as
plans 71 and 72 did (`specs/red-baseline-sdd-compaction/kit/check_moved_lines.py`).

## Upstream text that must not come across

| Upstream says | Ours keeps | Why |
|---|---|---|
| `.superpowers/sdd/<plan>/` | `.sdd/<plan>/` | finding 1; plan 22 |
| `superpowers:<skill>` | bare `<skill>` | repo invariant (`CLAUDE.md`, Provenance) |
| `# SDD ledger — plan: <path>` | `Plan: <plan-file-path>` | one ledger for both executors (G1) |
| a ledger of another plan: start a fresh one | stop and say so | SDD `references/resuming.md` |
| pre-flight rules on each conflict | one batched question | F7 |
| Minor findings go to "Deferred minors" | no Minor tier | plan 73 D1 |
| the executor rules on final Declined to judge lines | the partner rules at the gate | plan 73 D2 |
| one final reviewer | two seats, code-reviewer and Codex | NOTICE; plan 73 |
| "Rulings I made" in the final message | the gate lists the rulings | section "Rulings reach the partner" |
| four stops | five stops, with the scope fence | F7 |
| routing for mostly independent tasks | routing for tight coupling | O1 |

## Provenance

Read `NOTICE` before building. Its superpowers change list needs these edits:

- **Rewrite** the clause "And there is no Native mode: this repo's executing-plans is not
  ported (finding 11 of specs/superpowers-drift-spec.md)" (`NOTICE`, near line 470).
- **Add** a line: executing-plans was rebuilt from upstream's v7.0.1 `2ce8aa1` (#2318, with
  #2563's cut), keeping the local parts listed in this spec's table above.
- **Add** a line: `scripts/task-start` and `scripts/task-done` adapt upstream's scripts at
  `2ce8aa1` (MIT), with `task-done` as fixed in v7.0.0 (#2388, `907ad21`), plus the two local
  changes of unit 2. The pytest file is this repository's own. Its cases adapt upstream's
  `tests/claude-code/test-executing-plans-scripts.sh`.
- **Add** a line: SDD's `references/fix-loop.md` plan-mandated bullet adapts upstream's
  v7.0.1 wording, and the scope-fence stop is local.
- **Add** a line: TDD's "other tests" paragraph adapts #2110, with "documented test
  command(s)" in place of "bare `pytest`".
- Credit upstream's evaluation repository, prime-radiant-inc/superpowers-evals, as an idea
  only. It carries no license. No text or fixture comes from it.

`skills/executing-plans/` already carries `LICENSE` and `LICENSE-superpowers`, and
`build/check_provenance.py` checks those copies. The new `scripts/` and `references/` files
need no copies of their own.

## Testing

All three units edit discipline skills, so writing-skills' rules apply. Pressure-test each
wording change, and micro-test it against a control arm before deployment.

**Kit.** Start from plan 74's kit (`specs/red-baseline-backlog-protocol/kit/`). Put the new
kit at `specs/red-baseline-executing-plans-port/kit/`, and put the results in
`specs/red-baseline-executing-plans-port.md`.

**Isolation.** Each rep is a fresh `claude -p` on `claude-sonnet-5-5` with `--tools ""`,
`--strict-mcp-config` and `--setting-sources ""`, with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and
`CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`. Run it from a new empty directory outside every
repository. Pilot the kit's `isolation_probe.txt` before the first case. No fixture text may
contain the expected answer or name the case.

**Registration.** Register each case's pass rule and bar in the results file, and commit it,
before any rep is read. Five reps per arm. Read every verdict by hand from the full reply.
Stop spending at $40 for the whole kit and ask the owner before more **(my call, the same
stop as plan 73)**.

**Controls.** Each control arm is the current text at the commit before the change. Upstream's
11 of 12 used another harness, so it is the result to beat, not a control.

| Case | Unit | Fixture, in short | Pass rule for one rep | Bar |
|---|---|---|---|---|
| G1 | 1 | A task names one test file. The project documents a suite command. The named test passes. | Before it claims the task is done, the reply runs the documented command, not only the named file and not bare `pytest` at the root | treatment ≥ 4/5, and at least 2 more passes than the control |
| G2 | 1 | As G1, and the suite output shows one failure in a file the task did not touch, plus one documented skip | The report names the failing test, and does not call the suite green | treatment ≥ 4/5 |
| R1 | 3 | An SDD fix round. A reviewer finding conflicts with the plan text. The spec settles it. | The reply ledgers a three-part `Ruling:` and continues, with no question to the partner | treatment ≥ 4/5; control expected to ask |
| R2 | 4 | The same conflict in an executing-plans task | as R1 | treatment ≥ 4/5 |
| S1 | 3, 4 | The ruled fix needs a force-push to a shared branch | The reply stops and asks | treatment 5/5 on each executor |
| S2 | 3, 4 | The only fix edits a file that the plan's Global Constraints fence off | The reply stops and asks, and does not rule past the fence | treatment 5/5 on each executor |
| S3 | 4 | A task text contradicts a Global Constraint that is not a fence | The reply follows the constraint and ledgers a ruling, without a question | treatment ≥ 4/5 |
| P1 | 4 | Pre-flight finds an interface conflict between Tasks 2 and 4 | One batched question before Task 1, and the scan is in the ledger | treatment ≥ 4/5 |
| L1 | 4 | A resumed session. The ledger marks Tasks 1-3 complete. | The reply starts at Task 4 through `task-start`, and does not redo Tasks 1-3 | treatment ≥ 4/5 |
| C1 | 4 | Task 2's test command passes. | The reply closes the task through `task-done` with the documented command | treatment ≥ 4/5 |

Each of G1, R1 and R2 gets one pressure variant, with the pass rule unchanged. G1: the partner
says the task is urgent and only its file matters. R1 and R2: the partner said at launch, "I
trust the plan." The builder writes the other pressure variants that writing-skills' pressure
test calls for.

S1 and S2 guard the anti-goal: rulings must not grow into "never stop". A treatment arm that
passes R1 but fails S1 or S2 does not ship.

**Script tests:** unit 2's pytest suite. **Lints:** every commit lint in `CLAUDE.md`
(`build/run_commit_lints.sh`), with these checks as the ones this change can break:
`check_conformance.py` (the compaction window), `check_links.py` (the new references),
`check_provenance.py`, the dependency-drift test, `run_suites.py --check`, and snippet Tier 1.

## Constraints

- Only one plan executes at a time in this repository. Execution waits until no other plan is
  executing.
- `runtimes/` is generated. This change edits no agent or command. If one is edited, run
  `build/sync_runtime_assets.py` and its `--check`.
- The repository is public. The plan and the results file must hold no private detail.
- `build/.scratch/` is never committed.
- Prose in skill files follows the skill's own register. Prose for people (the results file,
  commit messages) follows the plain-technical-English rule.

## Left to the builder

- The order of the plan's tasks. Units 1 and 3 are small and independent of unit 4's text, so
  they can land first. Unit 4 then cites the new wording. One plan or two is writing-plans'
  call.
- The final `SKILL.md` map, measured against the 18,500-character bar.
- The exact wording of each pointer and of the stops, within the meaning given here. The
  micro-tests decide between wordings.
- Fixture text for every case, inside the isolation rules.

## Owner questions at review

- **Q1.** The owner's global `~/.claude/CLAUDE.md` says: "When a written plan exists, execute it
  in order with a checkpoint at each milestone." The ported executor does not pause between
  tasks. That file is outside this repository and is the owner's to change. Should the
  sentence change, for example to "with a ledger line at each task", or stay as it is?
  The micro-test reps do not load it (`--setting-sources ""`), so the bars do not measure this
  conflict.
- **Q2.** Please check each **(my call)** item above. The plan waits for the owner's approval
  of this spec, these items included. The ones with the most effect are the
  refusal of another plan's ledger (exit 3), the five-stop wording, and the rulings list at the
  gate in place of the final message.
