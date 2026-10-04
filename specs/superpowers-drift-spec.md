# Superpowers drift assessment

**Status:** findings only. No skill files were edited. This document exists to
decide *what, if anything, becomes a spec*.

It is a living record: each review re-baselines it in place rather than adding
a dated copy. This revision (2026-10-03) brings it to upstream v6.4.2. The first
pass (2026-09-03, against v6.3.0) lived at `specs/superpowers-drift-2026-09-03.md`
until this rename. Findings 1–8 keep their numbers because
`specs/completed/sdd-hardening.md` cites four of them; findings from v6.4.x
start at 9.

## Scope and method

| | |
|---|---|
| Vendored baseline | `896224c` (v6.0.3, 2026-06-18), per `NOTICE` |
| SDD adoption baseline | `b36e082` (v6.3.0), for the four pieces plan 22 adopted (findings 1, 2, 5, 6) |
| Previous review | `b36e082` (v6.3.0, 2026-08-12), reviewed 2026-09-03 |
| Upstream HEAD | `8ca22db` (v6.4.2, 2026-09-25) |
| Commits since previous review | 2 squash merges: `5bf4e78` (v6.4.1, 2026-09-18) and `8ca22db` |
| Files changed under `skills/` since previous review | 41 (+1577 / −166) |
| Next review starts from | `8ca22db` |

Comparison is **per behavioral claim, not per diff hunk**. `NOTICE` records that
most vendored files were adapted on the way in, so neither baseline is a true
ancestor of our copies and a mechanical three-way merge produces noise. Each
upstream RELEASE-NOTES entry was instead read as a claim and checked against our
tree: *does our copy already satisfy the intent?* v6.4.1 and v6.4.2 each landed
as one squash commit, so commit counts say nothing about scope in this pass; the
release notes' PR numbers are the claim units. Where a claim is about script
behavior, a probe in a scratch repository decided it rather than a reading.

That distinction is load-bearing. Upstream's `0b47219` (2026-07-05) fixes a
worktree path recomputed after `cd`, which made cleanup silently no-op. It
landed after our vendoring, so a diff-driven read flags us as behind. We are
not: `finishing-a-development-branch/SKILL.md:339` carries an equivalent guard
("Do NOT re-run detection here"), present since the layout move (`5fee1d7`).
**Already covered.** Whether that guard arrived as adaptation or the vendoring
record is imprecise about this file is undetermined, and does not change the
disposition.

## Status of the 2026-09-03 findings

| # | Finding | Status at 2026-10-03 |
|---|---|---|
| 1 | SDD workspace has no plan identity | **Adopted** — plan 22 |
| 2 | Implementers can spawn duplicate reviewers | **Adopted** — plan 22 |
| 3 | TDD reference has no falsifiability discipline | Open, prospective only; upstream unchanged |
| 4 | Brainstorming ceremony does not scale | Open; upstream moved further (v6.4.1) |
| 5 | Every task gets its own dispatch | **Adopted** — plan 22 |
| 6 | SDD review loop has no round cap | **Adopted** — plan 22, with a deliberate ladder divergence |
| 7 | Pre-flight conflicts stall for a human | Partly adopted (fix-round rulings); premise corrected; still a decision |
| 8 | Smaller items | `find-polluter.sh` still broken — its "fix directly" disposition was never carried out; two items now partly covered |

## Dismissed without further review

**First pass (72 commits to v6.3.0).** Roughly half were harness and packaging
work with no bearing on a standalone macOS install: Devin, Hermes, and Grok
support, Codex marketplace manifests and packaging scripts, the Windows
SessionStart hook dispatch, the `render-graphs.js` Windows fix, and the Gemini
removal-then-restore. The entire `using-superpowers` bootstrap compression and
its per-harness reference files go with them, since we dropped that skill.
Three skills changed by deletion only, with no new content:
`receiving-code-review`, `verification-before-completion`,
`dispatching-parallel-agents`. The additions in `executing-plans`,
`writing-skills`, and `systematic-debugging` were all `superpowers:`-namespaced
cross-references or pointers into `using-superpowers/references/`, which
violate our bare-skill-name invariant.

**Since v6.3.0.** The same treatment for OpenCode 2.0 support and V2 skill
registration, Muse and Qwen Code support and their manifests, the new
`using-superpowers` reference files (`claude-code-tools.md`, `muse-tools.md` —
except the nested-controller idea, which finding 14 evaluates on its merits),
`AGENTS.md` becoming canonical and `CLAUDE.md` being removed, the Code of
Conduct, issue templates, `docs/testing.md`'s Quorum eval lab, version bumps,
and the other harnesses' test directories. `proving-it-works-with-a-movie` was
held back from v6.4.1 and has not shipped.

**Already covered, no action:**

- **`plan-document-reviewer-prompt.md` removed (v6.4.2).** We deleted ours as
  orphaned in `8502a1f` (2026-07-03).
- **Multi-commit `BASE_SHA` via `git merge-base` (#2133).**
  `requesting-code-review/SKILL.md:32-34` already uses the recorded BASE or
  `git merge-base main HEAD`, and forbids `HEAD~1` outright.
- **`brainstorming/visual-companion.md` (12 lines).** Re-checked because it is
  the one file where an upstream change could reintroduce the remote
  brand-image fetch and telemetry toggles `NOTICE` records removing. The change
  is entirely `bash` prefixes on the `start-server.sh`/`stop-server.sh` commands
  (#2301), which our `<this-skill-dir>/scripts/...` anchors already supersede.
  The server scripts did not change; no network call or telemetry toggle
  returns.
- **`LICENSE`.** Unchanged since the vendoring, and byte-identical to our
  `LICENSE-superpowers`.

## Findings from the first pass, re-verified

### 1. SDD workspace has no plan identity — adopted

Plan 22 (`specs/completed/sdd-hardening.md`) made the workspace
`.sdd/<plan-basename>/`, gave the ledger a `Plan:` first line, and gave
`review-package` `PLAN_FILE` as its first positional argument. `NOTICE` records
the one divergence: `.sdd`, not upstream's `.superpowers/sdd`. Upstream's
follow-on fix for plans that share a basename is finding 12.

### 2. Implementer subagents can spawn duplicate reviewers — adopted

Plan 22 put the no-nested-subagent ban on the implementer and reviewer
templates, `requesting-code-review/code-reviewer.md`, and both agent
definitions, carrying the illegible-evidence rule with it
(`agents/code-reviewer.md:31`, `agents/task-reviewer.md:49`).

The case has since sharpened. Claude Code 2.1.288 lets a subagent spawn its own
subagents up to three layers below the main conversation by default
(`sub-agents.md`, "Let subagents spawn their own subagents";
`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`). The `general-purpose` implementer
therefore holds a working `Agent` tool, and the prose ban is the only thing on
that seat. The two agent definitions stay structurally safe: they omit `Agent`
from `tools`, which is the documented opt-out.

### 3. TDD reference has no falsifiability discipline — open, prospective

Unchanged on both sides. We still ship `testing-anti-patterns.md` (linked from
`test-driven-development/SKILL.md:344`); upstream replaced it with
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
into a Common Rationalizations row. Ours still has the full section
(`SKILL.md:194`) *and* a rationalizations table (`:244`), so **we never shipped
that regression.** Any compression pass here has to clear the bar upstream set.

Upstream's only TDD change since v6.3.0 is finding 13.

### 4. Brainstorming ceremony does not scale — open; upstream moved further

Our side is unchanged. `brainstorming/SKILL.md:21` still carries
*"Anti-Pattern: This Is Too Simple To Need A Design"*, and the nine-step
checklist (`:25-37`) ends in a committed spec, a user review, and a
fresh-session handoff for every request, including a config change. The
proportional-process policy recorded for this repo (brainstorming and specs
only for open design decisions; minor work fixed directly) still lives in
`/deferred` while this skill argues the opposite.

**v6.3.0 (#2063)** classifies each request as **spike / bounded /
architectural**, announces the classification for the partner to override, and
sends only architectural work through the full spec process. It did **not**
weaken the gate: every path still stops for approval before implementation. It
ships with a one-way ratchet (hidden complexity upgrades the path mid-task,
nothing downgrades) and a rationalization table against reaching for "bounded"
to skip work.

**v6.4.1 (#2258)** added two things on top, motivated by a session that took
"that scope is ok" as permission to scaffold:

- **Establish Shared Understanding.** Discover intent — the outcome, who it is
  for, what success looks like — asking one focused question about purpose
  before proposing features. Write the understanding back as a short note that
  separates what the partner said from assumptions, and carry it into the
  path's design artifact. Our step 3 asks about "purpose/constraints/success
  criteria" (`:31`) but never writes the understanding back for correction.
- **Stage-scoped approval.** The HARD-GATE now lists each path's prerequisites,
  and "a reply approves the stage actually presented": design approval permits
  only writing the spec, spec approval only invoking writing-plans, and the
  architectural path ends with the partner reviewing the written plan and
  choosing its execution method. Our architectural flow already stages the
  first two (`:33`, `:36`, then the fresh-session handoff). The plan-review
  stage belongs to writing-plans, whose handoff asks only "Which approach?"
  (finding 11).

A port now covers two upstream changes, and its micro-test should cover the new
failure as well as the old: approval of scope read as approval to build. Our
repo-specific lifecycle — the `specs/` conventions, the `deferred_items.md`
check, the fresh-session handoff — remains what the architectural path routes
into.

### 5. Every task gets its own dispatch — adopted

Plan 22 added same-shape batching (`subagent-driven-development/SKILL.md:100-126`)
with its safeguard — a batched review checks the diff file by file against the
brief's list, and a listed file the diff never touches is a Missing finding —
and the one-entry batched ledger line (`:381-386`).

### 6. SDD review loop has no round cap — adopted, with a divergence

Plan 22 added the five-attempt cap, resumed-then-fresh implementers with
appended fix reports, the scoped `re-review-prompt.md`, and controller
adjudication (`SKILL.md:196-223`). The escalation ladder diverges deliberately
and `NOTICE` records it: escalate context, then effort, then model, and take
the model rung only when the failing implementer was dispatched below the
capable tier.

Parked rulings reach the partner through the plan-completion gate, which reads
the ledger before the workspace is deleted (`:298-310`); upstream lists them in
the final message instead ("Rulings I made"). Equivalent in effect; no action.

### 7. Pre-flight conflicts always stall for a human — partly adopted; premise corrected

**Correction.** The first pass quoted `SKILL.md:222` as calling the pre-flight
gate "this skill's one deliberate human [checkpoint]". Re-read at the same
commit (`5e5983d`), that sentence is about the plan-completion protocol's
resolve-before-defer gate — the batch that pending plan-mandated questions fold
into (now `:288-296`). Asking at pre-flight is still a local design choice, but
not the one that quote named, so the tension is narrower than first stated.

**What plan 22 brought.** Rulings now exist in one place: fix-round
adjudication records `Ruling: <what you decided> — <why> — <what it costs if
wrong>` and stops for the partner "only when every path forward is a guess"
(`:220-223`) — upstream's format and one of its four stops.

**What still asks.** Pre-flight (`:128-140`) presents conflicts as one batched
question before execution, and a clean scan proceeds "without comment" where
upstream's #2080 records the scan's checks in the ledger. Mid-run, a reviewer
finding that conflicts with plan text is "the human's decision" (`:258-262`).

Upstream v6.3.0 lets non-catastrophic conflicts take a recorded ruling so work
continues, with the spec as binding authority and the plan its argument.
Exactly four things still stop the run: an irreversible or destructive
operation; a security-sensitive action; a side effect outside the worktree
that norms say you ask about first; and a plan so broken that every path
forward is a guess.

**Why it matters more now.** Two v6.4.1 features assume rulings-not-stalls: the
executing-plans rebuild (finding 11) and the nested controller (finding 14).
Adopting either means settling this first. **Decide, don't assume** still
stands.

### 8. Smaller items

- **`find-polluter.sh` is still broken; the first pass's "fix directly"
  disposition was never carried out.** The only commit touching the file is the
  layout move (`5fee1d7`). A probe on 2026-10-03 shows the bug is worse than
  first described:
  - A pattern matching nothing prints "Found 1 test files", runs no test, and
    ends "✅ No polluter found - all tests clean!" — a false all-clear on any
    typo in the pattern.
  - The header's TS example, `'src/**/*.test.ts'`, produces that same output
    with two matching files present.
  - The pytest pattern documented at `root-cause-tracing.md:102`
    (`'*/test_*.py'`) does work ("Found 2"), which is why the bug is easy to
    miss on this stack.
  - Upstream's fixed script finds both TS files.

  The invocation is broken too. `root-cause-tracing.md:102` runs
  `./find-polluter.sh`, which resolves against the user's repository, not the
  skill directory. That is the class of bug `NOTICE`'s bundled-script-path
  entry (`47dc45c`) fixed for subagent-driven-development and brainstorming,
  and that fix missed this file. Upstream's own change there
  (`bash ./find-polluter.sh`, #2301) does not fix path resolution.

  Port the fix rather than the file — ours carries a local `TEST_CMD`. It has
  three parts: strip a caller-supplied `./` so it cannot double-prefix; match
  both the `./`-prefixed pattern and one with `**/` collapsed (so
  `src/top.test.ts` isn't skipped by `src/**/*.test.ts`); and branch on empty
  output so the count is 0. Add the deterministic test upstream added, in our
  directory-scoped convention. Anchor the invocation as
  `<this-skill-dir>/find-polluter.sh`.
- **Plan `Spec:` header pointer — still absent.** Upstream has carried it since
  v6.3.0 (#2086). Its executing-plans now reads the spec at setup and ledgers a
  missing one, so rulings made without it are marked provisional. Our plan
  header (`writing-plans/SKILL.md:58-77`) has no such line. Plan 22 did not take
  it, and our `<id>-<spec-name>` naming couples plan and spec only by
  convention. Small, and it composes with finding 9.
- **`finishing-a-development-branch` still advertises "Discard this work"** in
  both completion menus, now `:160` (4-option) and `:172` (detached HEAD).
  Upstream demoted discard to explicit-request-only, on the grounds that
  advertising it next to "Merge" offers to destroy finished, passing work, and
  has not changed it since. We have the typed-confirmation ritual; the issue is
  the menu placement.
- **Untracked-file guard on worktree removal — partly covered since `51fb8e4`
  (2026-09-27).** Step 4b now requires
  `git status --porcelain --untracked-files=normal` to print nothing before
  merge or PR (`:187`), so Option 1 normally reaches `git worktree remove`
  (`:350`) clean. A refusal caused by files created after Step 4b is still
  unhandled; upstream stops, names the files, and asks instead of reaching for
  `--force`.
- **`using-git-worktrees` guard content** is still in the Problem/Fix form
  (`:163-188`), not the house Excuse/Reality table. Format convergence only.
- **PR creation is no longer `gh`-only.** `f8b96c0` (2026-09-08) made `gh`
  optional with a compare-URL fallback (`:269-300`); Step 3's `gh repo view`
  probe (`:144`) fails silently into the ask path. Upstream's forge-agnostic
  rewrite adds little now.

## New findings (v6.4.1 and v6.4.2), ranked

### 9. writing-plans asks for code transcripts, and our plans show it

**Verified gap; the highest-relevance item in this pass.** v6.4.2 (#2333)
rewrote writing-plans around one claim: *a plan records decisions; it is not a
transcript of the code.* Its release notes name Opus 5.5 among the frontier
models that "could get overzealous during plan writing", sometimes trying to
implement the whole project while designing the plan. This repo plans on the
stronger tier by its own handoff text ("planning belongs on the stronger tier",
`writing-plans/SKILL.md:175`), which is Opus here (`executing-plans/SKILL.md`
Step 3: "the capable model tier (opus)"). This is the exact configuration.

The upstream changes:

- **A capable reader.** The plan is written for an engineer who has not seen
  this codebase or spec but writes idiomatic code once given the exact
  interface and test. That replaces "zero context ... and questionable taste".
- **"What a Step Contains" replaces "No Placeholders".** A test step gives the
  test's name and assertions, with the spec's values. A code step gives the
  exact signature, the file, and the spec-pinned values; a body appears only
  for an algorithm the signature and tests don't determine, or for exact copy
  the spec fixes. A verification step gives the command and its passing output.
  A reference to another task goes through that task's Interfaces block.
  Placeholders are still called out, as the opposite failure.
- **A proportion check in self-review.** A plan several times longer than its
  spec is a transcript; when code blocks dominate, replace bodies with
  signatures and assertions.
- **Step sizing.** "One action with a checkable result" replaces "2-5 minutes".
- **Measured.** Reproducing the original report, scratch builds disappeared,
  and plans took a quarter of the time and about a third of the tokens. Every
  lean plan executed 9/9 against planted-defect probes on Sonnet 5, the same as
  full-code plans.

Our copy still has every replaced line. The overview at
`writing-plans/SKILL.md:14` keeps "zero context ... questionable taste". `:51`
keeps "one action (2-5 minutes)". "No Placeholders" (`:132-139`) requires code
blocks for code steps, and `:144` says "Complete code in every step — if a step
changes code, show the code". The handoff repeats the premise (`:163`: "a
complete, zero-context handoff").

**Our plans show the pattern.** Below are recent plans with a spec: plan length
against spec length, and the share of plan lines inside code fences.

| Plan | Plan lines | Spec lines | Ratio | In-fence |
|---|---|---|---|---|
| 15 clean-code-family | 1397 | 227 | 6.2× | 53% |
| 16 llm-wiki-specs-harvest | 2254 | 262 | 8.6× | 73% |
| 17 agents-and-commands-expansion | 1073 | 260 | 4.1× | 38% |
| 22 sdd-hardening | 875 | 309 | 2.8× | 44% |
| 24 readonly-agent-guard | 1860 | 377 | 4.9× | 65% |
| 31 skill-model-pin-removal | 539 | 130 | 4.1× | 30% |

Four of the six exceed 4× their spec, and two put more than 60% of their lines
inside fences. Three caveats apply:

- Completed plans include their completion markup, which inflates length a
  little.
- The fence share comes from a line scan, not a parser.
- Fence contents were not classified. For skill-text plans such as 15, much of
  what sits inside fences is verbatim skill wording, which the carve-out below
  treats as legitimate, so the share is an upper bound on transcript.

Even so, most of these plans sit well past upstream's "several times longer
than the spec" line.

**This repo needs one carve-out stated.** Upstream keeps a body for "exact copy
the spec fixes". Here the product is skill text, and wording micro-tested
against a no-guidance control *is* exact copy. A port has to say so, or the
proportion check pushes plans to paraphrase wording whose exact form was the
point. The savings land in plans for scripts and tests.

**It composes with local machinery.** task-brief's heading-bounded extraction
and its Global Constraints prepend are indifferent to step length. Upstream
kept both Global Constraints and Interfaces, and leans on Interfaces harder.

This is a behavior-shaping change to a discipline skill, so it needs
writing-skills' pressure-test and micro-test before deployment. Upstream's
planted-defect probe is a ready bar.

### 10. Reviewers grade the spec's silence, not the user's experience

**Verified gap.** v6.4.1 (#2319) is a three-part change. Its motivating eval:
every implementer shipped the same crash on an input the spec implied but never
named.

- **Reviewer.** "The spec is a vision document": for behavior the spec is
  silent on, judge by what a reasonable person using the software would expect,
  and grade by effect on that person, not by whether the spec mentions the
  trigger. A **"Declined to judge"** list before the verdict names every
  behavior set aside as outside the plan or spec, so the executor rules on each
  instead of dropping it silently.
- **Plan.** A **Review Focus** section lists up to five input classes or
  failure modes the spec implies but no task's tests exercise. Each is pinned
  by a test added to the task that owns the code, and self-review item 4 checks
  the section.
- **Executor.** Re-grades the reviewer's severities by effect before gating,
  and rules on each "Declined to judge" line.

None of this is in our tree. There is no "reasonable person", "vision", or
"Declined to judge" text in `requesting-code-review/code-reviewer.md`,
`subagent-driven-development/task-reviewer-prompt.md`, or either agent
definition, and no Review Focus section in the plan template.

The first pass's rule applies. Our reviewer contract lives in both the
templates and `agents/{code,task}-reviewer.md`, so the change lands on all four
or it applies to only one dispatch path.

The failure class fits the stack these skills serve. Scrapers and ETL pipelines
meet inputs no spec enumerates: relayouts, malformed rows, empty pulls. It
composes with finding 9 through the shared plan template.

### 11. executing-plans was rebuilt as a ledgered native mode

**A port, not a merge.** v6.4.1 (#2318) rebuilt upstream's 64-line
`executing-plans` stub, which "measured the same as running with no plugin at
all". The new version is 373 lines, with `task-start` (28 lines) and
`task-done` (52 lines) helpers and a 139-line script test.

What upstream's version does:

- Shares SDD's workspace and ledger, so a plan can change executors mid-flight.
- Reads each task's brief through `task-start`.
- Loads TDD at setup.
- Holds each task to a completion contract with evidence; `task-done` writes the
  ledger line only when the tests pass.
- Runs continuously under rulings-not-stalls and its four stops.
- Dispatches one whole-branch reviewer on the most capable model.
- Makes one TDD-verified fix pass, with no re-review.
- Ends with exhaustive "Rulings I made" and "Deferred minors" lists.

The writing-plans handoff (#2258, #2318) now asks the partner to review the
saved plan before anything runs. It offers Subagent-driven and Native, says what
each costs, and recommends one with a reason drawn from the plan.

Ours (`executing-plans/SKILL.md`, 122 lines) has no workspace or ledger.
Progress lives in todos, so a `/clear` or compaction mid-plan loses its place —
the failure plan 22 fixed for SDD. It stops on any unclear instruction, and its
description routes it to tightly coupled plans rather than to cost.

It also carries local work upstream lacks:

- Step 1.5's record of the base-branch start.
- Step 3's two-seat whole-plan review (code-reviewer plus Codex, worked through
  receiving-code-review).
- The plan-completion protocol.

A port keeps those, reuses plan 22's `.sdd/<plan-basename>/` workspace, and
keeps the routing story `977a61a` unified. It takes the ledger and the
completion contract, plus `task-start` and `task-done` as new scripts with
tests in our convention. It depends on finding 7 for rulings-not-stalls and on
finding 13 for what "tests pass" means.

Native mode on a mid-tier session model matches this repo's routing, where
execution runs on the standard default after a fresh-session handoff.

### 12. SDD script hardening (v6.4.1)

Three upstream fixes to the scripts plan 22 touched, judged separately:

- **`review-package` accepts empty and non-descendant ranges — verified gap.**
  - Probe, BASE == HEAD: it wrote `review-<sha>..<sha>.diff` with "0 commit(s)"
    and exited 0.
  - Probe, BASE on a sibling branch: it wrote a package whose diff carries the
    sibling's only file as `deleted file mode 100644` — a phantom deletion —
    and exited 0.

  Upstream (#2136, #2050) adds two guards that exit 3:
  `git merge-base --is-ancestor "$base" "$head"`, and a non-zero
  `git rev-list --count`. Our argument order is already upstream's, so the
  guards drop in after `review-package:22-23`, with a test for each.
- **Plans sharing a basename share a workspace — decided locally, no action.**
  The probe confirms that `docs/alpha/plan.md` and `docs/beta/plan.md` both
  resolve to `.sdd/plan`. The 2026-09-03 completion gate handled this as
  deferred item M2. It recorded the assumption in `sdd-workspace:31-38`, and
  relies on the ledger's `Plan:` first line to make a collision visible
  rather than silent, with "stop and say so" on a mismatch (`SKILL.md:366-368`,
  `:374-377`). Upstream (#2138, #2045) prevents the collision outright: a
  `plan-path` marker, disambiguation by parent directory and then a counter,
  and legacy workspaces adopted in place. Exposure here stays low, because a
  collision needs the same `<id>-<spec-name>` in the same working tree.
  Upstream's scheme is the ready port if M2 is revisited.
- **Interpreter invocation (#2301) — low.** Upstream prefixes `bash` and `node`
  because some marketplace packagers strip exec bits. Our installs keep them:
  symlinks do, and `install.py --copy` uses `shutil.copy2`. The live issue in
  this class is path resolution, not exec bits. `find-polluter.sh` (finding 8)
  is the instance that matters; the `./render-graphs.js` call at
  `writing-skills/SKILL.md:336-337` is the same pattern in an authoring-only
  context.

### 13. TDD does not say what "other tests" means

**Partly covered.** v6.4.1 (#2110) found that when a task named one test file,
sessions ran only that file in 11 of 12 probe runs, so a broken neighbor went
unseen. TDD now says three things:

- The project's suite defines green.
- A task's scope bounds the deliverable, not the verification.
- Every failure is reported by name, including ones the session didn't cause.

Our SDD implementer already runs "the full suite once before committing"
(`implementer-prompt.md:50-51`). Standalone TDD stops at "Other tests fail? Fix
now." (`test-driven-development/SKILL.md:171`), and executing-plans names no
suite at all.

**Upstream's wording is wrong for this repo.** It says to run "bare `pytest`".
This repo has no root runner, and a repo-root collection fails outright on the
colliding `test_build.py` basenames (`CLAUDE.md`, Commands). A port has to say
"the project's documented test command(s)". The report-every-failure half fits
as it stands: several suites here have documented environment-dependent skips
and failures, and naming them is exactly the discipline.

This is a wording change to a discipline skill, so it needs a micro-test.
Upstream's 11-of-12 probe is the control to beat.

### 14. Nested controller on Claude Code — not adopted

v6.4.1 (#2320) lets the whole SDD loop run one layer down: one orchestrator
subagent on a mid-tier model, opt-in, measured at about half the cost and wall
clock. The claim lives in `using-superpowers/references/claude-code-tools.md`,
under a skill we dropped. Its platform premise holds: nesting is on by default
(finding 2).

It does not fit here, for two reasons:

- **The saving is already taken another way.** writing-plans' handoff
  recommends `/clear` and executing on the standard model default.
- **A nested controller cannot hold our human checkpoints.** Claude Code
  removes `AskUserQuestion` from every subagent (`sub-agents.md`, "Available
  tools"). The pre-flight batched question and the plan-completion gate would
  each end the orchestrator's run. Upstream can nest because it rules where we
  ask.

This stays a function of finding 7.

### 15. diagnosing-superpowers — not adopted

A new skill (#2236, #2287): a 120-line SKILL.md plus 19 support files (11
prompts, 4 references, 4 templates). It reads session transcripts on disk, dispatches seven analyst
subagents, and reports findings with `path:line` evidence. On request it scrubs
a bundle or drafts a GitHub issue for the superpowers maintainers.

Its purpose is upstream bug reporting: it writes to `~/.superpowers/` and files
against `obra/superpowers`. Adopting it would mean de-branding, choosing who
receives the report, and a `NOTICE` entry. Recorded for awareness. Its evidence
rule ("Every finding cites `path:line`. No citation, no finding.") is the
transferable idea.

## Suggested disposition

Under this repo's proportional-process rule:

- **Done:** findings 1, 2, 5, and 6, through plan 22 (2026-09-03).
- **Fix directly, no spec:** two items, both small, mechanical, and verified
  by probe.
  - Finding 8's `find-polluter.sh`: the three-part script fix, a deterministic
    test, and the invocation anchor. This was the first pass's disposition, and
    it is still undone.
  - Finding 12's `review-package` range guards, with tests.
- **Spec candidate, planning surface:** findings 9 and 10, plus finding 8's
  `Spec:` pointer. They share the writing-plans plan template and self-review,
  and finding 10 also reaches the four reviewer surfaces. Both shape
  discipline-skill behavior, so they need writing-skills' pressure-test and
  micro-test. Upstream's planted-defect probe and its unnamed-input crash eval
  are ready controls.
- **Spec candidate, brainstorming:** finding 4, now covering #2063 and #2258
  together. Unchanged in kind: a discipline skill that touches the specs
  lifecycle, micro-tested before deployment.
- **Decide first:** finding 7. Two items hang on it:
  - Finding 11, the executing-plans port, which merits its own spec once 7 is
    settled. Finding 13's TDD wording travels with it, micro-tested.
  - Finding 14, which stays declined unless 7 goes to rulings.
- **Prospective only:** finding 3. Adopt the falsifiability material if you
  want the guidance; do not take the compression without clearing upstream's
  measured bar.
- **Not adopted, recorded:** finding 12's basename collision (decided as M2)
  and interpreter prefixes, finding 14, and finding 15.

Any adoption needs a `NOTICE` change-list entry. The existing "Four changes
were later adopted FROM upstream v6.1.0-v6.3.0" entry is the model: name what
was taken, from which release, and where the port deliberately diverges. When
the next pass runs, update this document's "Next review starts from" row along
with the findings.
