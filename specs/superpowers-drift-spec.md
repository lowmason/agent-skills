# Superpowers drift assessment

**Status:** findings only. No skill files were edited. This document exists to
decide *what, if anything, becomes a spec*.

It is a living record: each review re-baselines it in place rather than adding a
dated copy. This revision (2026-10-28) brings it to upstream v7.0.1 for every
skill except brainstorming. It re-takes the line anchors of the findings it
edits (8, 9, 10, 11, 14, 15 and the new 17) and of the method section's example.
Plan 70 (2026-10-28) re-baselined finding 4 (brainstorming) to v7.0.1
(`2ce8aa1`) when it adopted that finding. The other anchors date from the
2026-10-18 revision, which brought the document to v7.0.0 and re-took every
anchor. The 2026-10-03 revision brought it to v6.4.2; the first pass
(2026-09-03, against v6.3.0) lived at `specs/superpowers-drift-2026-09-03.md`
until that revision renamed it.
Finding numbers never change, because other documents cite them (`NOTICE`,
`specs/completed/sdd-hardening.md`, `specs/completed/handoff-briefs.md`,
`specs/completed/audit-3-10-26.md`).
Findings 1–8 are the first pass's, 9–15 came from v6.4.x, 16 came from v7.0.0,
and findings from v7.0.1 start at 17.

## Scope and method

| | |
|---|---|
| Vendored baseline | `896224c` (v6.0.3, 2026-06-18), per `NOTICE` |
| Adoption baselines | `b36e082` (v6.3.0) for the four pieces plan 22 (SDD hardening) adopted: findings 1, 2, 5, 6. `8ca22db` (v6.4.2) for the two pieces plan 40 (handoff briefs) adopted: finding 8's `Spec:` pointer and finding 11's handoff half. `2ce8aa1` (v7.0.1) for finding 4, which plan 70 adopted. `2ce8aa1` also for finding 17's SDD file map, which plan 71 adopted, and for its writing-skills file map, which plan 72 adopted |
| Previous review | `bb92a77` (v7.0.0, 2026-10-09), reviewed 2026-10-18 |
| Upstream HEAD | `2ce8aa1` (v7.0.1, 2026-10-21), still `main` on 2026-10-28 |
| Commits since previous review | 2 on `main`: `b739a8a`, the contribution templates (its title cites #2570, the release notes cite #2569), and the release squash merge `2ce8aa1` (#2581). Upstream's `dev` branch keeps one commit per pull request |
| Files changed under `skills/` since previous review | 22 (+705 / −667). Without brainstorming's `SKILL.md`: 21 (+594 / −625) |
| Unreleased skill work | None: on 2026-10-28 `dev` differs from `2ce8aa1` in 11 files (hooks, the Pi extension, the Muse manifest, docs and release notes), none under `skills/` |
| Next review starts from | `2ce8aa1` |

Comparison is **per behavioral claim, not per diff hunk**. `NOTICE` records that
most vendored files came in byte-identical to `896224c`. Local changes since
then mean a mechanical three-way merge still produces noise. Each
upstream RELEASE-NOTES entry was instead read as a claim and checked against our
tree: *does our copy already satisfy the intent?* v6.4.1, v6.4.2, v7.0.0 and
v7.0.1 each landed as one squash commit, so commit counts say nothing about scope. The
claim units are the release notes' pull-request numbers (obra/superpowers pull
requests, written #NNNN below), and `dev`'s per-PR commits are cited where a
port would start from the diff. Where a claim is about script behavior, a probe
in a scratch repository decided it rather than a reading.

That distinction is load-bearing. Upstream's `0b47219` (2026-07-05) fixes a
worktree path recomputed after `cd`, which made cleanup silently no-op. It
landed after our vendoring, so a diff-driven read flags us as behind. We are
not: `finishing-a-development-branch/SKILL.md:381` carries an equivalent guard
("Do NOT re-run detection here").
**Already covered.** The file came in byte-identical at the vendoring, so we
added the guard ourselves (`46423d5`).

The 2026-10-18 revision found that most line anchors had moved since the pass
before it. Plan 40 rewrote parts of
`writing-plans/SKILL.md`, and plan 46 (the SDD bundle, 2026-10-15)
restructured `subagent-driven-development/SKILL.md`. Elsewhere, the `cc-guide`
citation line added near the top of every file that rests on the Claude Code
guide (`4efba4e`) shifted anchors by one.

## Status of earlier findings

| # | Finding | Status at 2026-10-28 |
|---|---|---|
| 1 | SDD workspace has no plan identity | **Adopted** — plan 22 |
| 2 | Implementers can spawn duplicate reviewers | **Adopted** — plan 22 |
| 3 | TDD reference has no falsifiability discipline | Open, prospective only; upstream unchanged |
| 4 | Brainstorming ceremony does not scale | **Adopted** — plan 70, rebased on v7.0.1 (`2ce8aa1`) |
| 5 | Every task gets its own dispatch | **Adopted** — plan 22 |
| 6 | SDD review loop has no round cap | **Adopted** — plan 22, with a deliberate ladder divergence |
| 7 | Pre-flight conflicts stall for a human | Partly adopted (fix-round rulings); premise corrected; decided 2026-10-21: rulings mid-run only |
| 8 | Smaller items | `find-polluter.sh` **fixed** — plan 50; the untracked-file guard **adopted** as an idea — plan 60; one item partly covered; the `Spec:` pointer adopted by plan 40 |
| 9 | writing-plans asks for code transcripts | Open; both plans written since that implement their own spec show the pattern; its tier premise re-sourced |
| 10 | Reviewers grade the spec's silence | Open; upstream unchanged |
| 11 | executing-plans was rebuilt as a ledgered native mode | Handoff half adopted by plan 40; the port goes to its own spec (7 decided 2026-10-21); upstream has since fixed `task-done`, and v7.0.1 cut its Example Workflow to fit the compaction window |
| 12 | SDD script hardening | `review-package` range guards and v7.0.0's create-only `.gitignore` **adopted** — plan 50; the basename collision stays decided (M2) |
| 13 | TDD does not say what "other tests" means | Open; travels with 11 |
| 14 | Nested controller on Claude Code | Not adopted; premise narrowed to non-fork subagents |
| 15 | diagnosing-superpowers | Not adopted. v7.0.1 changed only the issues it drafts |
| 17 | Skill bodies run past the compaction re-attach cut | Size bar **already covered** by the compaction lint. Decided 2026-10-28: no byte bar until the probe, the SDD move runs first as a plan, and the writing-skills split follows as a plan without a spec |

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

**v6.4.1 and v6.4.2.** The same treatment for OpenCode 2.0 support and V2 skill
registration, Muse and Qwen Code support and their manifests, the new
`using-superpowers` reference files (`claude-code-tools.md`, `muse-tools.md` —
except the nested-controller idea, which finding 14 evaluates on its merits),
`AGENTS.md` becoming canonical and `CLAUDE.md` being removed, the Code of
Conduct, issue templates, `docs/testing.md`'s Quorum eval lab, version bumps,
and the other harnesses' test directories. `proving-it-works-with-a-movie` was
held back from v6.4.1.

**v7.0.0.** The Antigravity Marketplace manifest and its skill-discovery
bootstrap (#2479), Hermes skill descriptions (#2284), the Windows
`run-hook.cmd` fixes (#2393), the SessionStart broken-`PATH` fix (#2349), the
porting-guide corrections, the `render-graphs` test's version-manager fix,
version bumps and packaging scripts, and the design and plan documents under
`docs/superpowers/`. The
two hook fixes harden upstream's own bootstrap hooks, which we don't ship.
`proving-it-works-with-a-movie` still has not shipped: it is on neither `main`
nor `dev`.

**v7.0.1.** Version bumps across the plugin manifests and install docs, the
removal of 17 old plan documents from `docs/superpowers/plans/`, and an edit to
diagnosing-superpowers' design record. The contribution-policy changes (#2569)
are **declined** too. The issue and PR templates now ask who is filing, what
their human partner asked for, and for a summary that a human wrote. `AGENTS.md`
and the README now refuse agent-written PRs that fix someone else's issue.
These rules govern contributions to upstream's own repository, and this
repository has no issue or PR templates. #2569's change to
diagnosing-superpowers is under finding 15.

**Already covered, no action:**

- **`plan-document-reviewer-prompt.md` removed (v6.4.2).** We deleted ours as
  orphaned in `8502a1f` (2026-07-03).
- **`spec-document-reviewer-prompt.md` removed (v7.0.0).** Deleted here in the
  same commit. Its v7.0.0 replacement, the builder check, is part of finding 4.
- **Multi-commit `BASE_SHA` via `git merge-base` (#2133).**
  `requesting-code-review/SKILL.md:33-35` already uses the recorded BASE or
  `git merge-base main HEAD`, and forbids `HEAD~1` outright.
- **Skill-argument substitution (#2361).** Claude Code expands `$0`, `$1`, …
  in a skill body to the invocation's arguments, counting from zero
  (`specs/guides/claude-code-customization-guide.md:138`; `\$` escapes one,
  `:143`). Upstream's `awk '{print $1}'` example therefore broke whenever the
  skill was invoked with a second argument. No `SKILL.md` or command body here
  contains `$` followed by a digit or by `ARGUMENTS` (grep, 2026-10-18), and our
  base-SHA example uses a placeholder (`requesting-code-review/SKILL.md:33`).
- **`brainstorming/visual-companion.md` and the companion server.** Re-checked
  each pass because an upstream change there could reintroduce the remote
  brand-image fetch and telemetry toggles `NOTICE` records removing. v6.4.1's
  change to `visual-companion.md` (12 lines) is entirely `bash` prefixes on the
  `start-server.sh`/`stop-server.sh` commands (#2301), which our
  `<this-skill-dir>/scripts/...` anchors already supersede. v7.0.0 left
  `visual-companion.md` alone and changed one line of `server.cjs`, finding
  16's content-insertion fix. No network call or telemetry toggle returns.
  v7.0.1 changed neither file. Its one change near the companion is
  test-only, and the release notes do not list it.
  `tests/brainstorm-server/server.test.js` now polls for `fs.watch` events
  instead of sleeping a fixed time, because macOS can deliver them late. Our `brainstorming/scripts/test_server.py` tests
  only `wrapInFrame` and watches no files, so the fix has no counterpart here.
- **`LICENSE`.** Unchanged since the vendoring, and byte-identical to our
  `LICENSE-superpowers` (re-checked at v7.0.1 with `cmp`).

## Findings 1–8 (first pass), re-verified

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
(`agents/code-reviewer.md:32`, `agents/task-reviewer.md:50`).

The case has since sharpened. Claude Code lets a subagent spawn its own
subagents up to three layers below the main conversation by default
(`sub-agents.md`, "Let subagents spawn their own subagents";
`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, default 3 since 2.1.219; re-checked at
2.1.302). The `general-purpose` implementer therefore holds a working `Agent`
tool, and the prose ban is the only thing on that seat. The two agent
definitions stay structurally safe: they omit `Agent` from `tools`, which is
the documented opt-out.

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

### 4. Brainstorming ceremony does not scale — adopted (plan 70), rebased on v7.0.1

**Adopted by plan 70 (2026-10-28).** `skills/brainstorming/SKILL.md` now follows
upstream v7.0.1 (`2ce8aa1`, 2026-10-21). `NOTICE` names what was taken and each
deliberate divergence. The behavior record is
`specs/red-baseline-brainstorming-2026-10-28.md`.

**Before plan 70,** our copy said that every project, however simple, goes
through one process ("a config change — all of them"). That process needed a
design, a committed spec, a review and a handoff to writing-plans. The handoff
recommended a fresh session. Sending every project through that process
contradicted the proportional-process rule in `/deferred` and the guide's
`lean.ceremony` section. Conformance exception `brainstorming-every-project`
recorded the gap, and plan 70 removed it.

**Upstream at v7.0.1.** v7.0.0 (#2463, `9e63918`) rebuilt the skill from scratch,
and v7.0.1 (`2ce8aa1`) retuned it. At `2ce8aa1` the skill works like this:

- **Sizing.** A quick, clear task is done at once. Every size above it gets a
  design doc: a short one for a small change, without the builder check, and the
  full one for a project (#2571). The skill names the size in plain words, and
  the partner can override it. Work that grows steps up a size.
- **Look before you ask.** The skill reads the project and what the partner
  pointed at before its first message (#2560). v7.0.0 made this an offer.
- **The first message.** It echoes a detailed request back (#2571), or asks one
  open question. It offers to skip the questions only when the partner's message
  did not ask for brainstorming (#2560). v7.0.0 always offered.
- **Describing and playback.** Open questions come first, and a menu comes only
  when the partner is stuck. The first Red Flags row is "Options steer. Ask them
  to describe it first." Each part is played back in about 200 to 300 words.
- **How it gets made (#2482, #2483).** The skill finds out early which platform,
  language, library or medium choices the partner wants to make. It records each
  choice it makes as its own call.
- **Laid-out approaches (#2571).** Two or three approaches go in a message of
  their own, with a recommendation, and the partner picks before the doc is
  written. v7.0.0 compared ideas privately.
- **One gate, a builder check, spikes.** Nothing is built before the design doc
  is approved. A fresh subagent reads the doc as its builder and lists what it
  would still need to ask. If the partner opts out of the questions, the skill
  ends and the gate goes with it. An accepted spike may be built, and keeping it
  is a new request.

**The measured bar.** The Brainstorming section of v7.0.0's release notes gives
no figures, but its pull requests do (#2463, #2482). #2560 and #2571 published
figures too, on different baselines.

- **#2560** compared v7.0.0 with its branch. On v7.0.0, Opus offered to skip the
  questions on 10 of 10 runs whose request asked for brainstorming. On the
  branch, Opus and Sonnet made that offer on 0 of 12 such runs. They made it on
  12 of 12 runs whose request did not ask for brainstorming.
- **#2571** published figures from its Gallery scenario (24 runs over three
  variants: explicit, auto-triggered and a quiet persona). "Skipped a step
  without consent" fell from 24 of 24 runs to 3 of 24. "Design doc approved
  before building" rose from 1 of 24 to 23 of 24. These Gallery figures compare
  upstream `dev`, after #2560 merged, with the #2571 branch, not with v7.0.0.
  #2571's final matrix held 176 blind-graded conversations over seven scenarios
  (the three Gallery variants and four others), on Opus and Sonnet.

**Where the #2560 and #2571 scenarios are.** #2560 points to
`prime-radiant-inc/superpowers-evals#73` for its scenarios. #2571 points to
`prime-radiant-inc/superpowers-evals#75` for its scenarios and its experiment
log. The repository `prime-radiant-inc/superpowers-evals` has no license, so
this repo cites its scenarios by name only.

**What plan 70 took, and where it diverges.** Plan 70 took v7.0.1's text and
order, and `builder-check-prompt.md` unchanged. `NOTICE` lists these
divergences:

- our `Use when…` description
- the condensed software guidance carried from upstream v6.0.3
- the `specs/` lifecycle with its fresh-session handoff and the
  `specs/deferred_items.md` check in Look Before You Ask
- a small change designed and approved in chat and built in the same session
- caller sizing with no skip offer for routed work
- the split between open questions and options
- spikes kept off the working branch
- the visual-companion token-cost warning
- the builder check's `model: opus` pin
- the quick-task exit in the HARD-GATE and in the sentence that lists what
  isn't implementing
- the dropped spec self-review

`NOTICE` also records two more changes. They are the Red Flags row that the
pressure test added, and the wording that changed in two upstream passages after
the first GREEN round. Plan 70 ran its own RED baseline, pressure test, GREEN
and trigger test, all newly written. The owner then had the Red Flags row and
the sentence that lists what isn't implementing reworded. Plan 70 re-ran the
cases judged, not measured, to be within reach of those edits. Decisions D1 to
D4 of the design spec, `specs/completed/brainstorming-proportional-rebuild.md`,
record the owner's calls on a small change, the opt-out, spikes and question
style.

**The other v7.0.1 changes** are listed under New finding (v7.0.1).

### 5. Every task gets its own dispatch — adopted

Plan 22 added same-shape batching (`subagent-driven-development/SKILL.md:121-147`)
with its safeguard — a batched review checks the diff file by file against the
brief's list, and a listed file the diff never touches is a Missing finding
(`subagent-driven-development/task-reviewer-prompt.md:65`,
`agents/task-reviewer.md:61`) — and the one-entry batched ledger line
(`SKILL.md:417-423`).

### 6. SDD review loop has no round cap — adopted, with a divergence

Plan 22 added the five-attempt cap, resumed-then-fresh implementers with
appended fix reports, the scoped `re-review-prompt.md`, and controller
adjudication (`SKILL.md:219-246`). The escalation ladder diverges deliberately
and `NOTICE` records it: escalate context, then effort, then model, and take
the model rung only when the failing implementer was dispatched below the
capable tier.

Parked rulings reach the partner through the plan-completion gate, which reads
the ledger before the workspace is deleted (`:260-272`); upstream lists them in
the final message instead ("Rulings I made"). Equivalent in effect; no action.

### 7. Pre-flight conflicts always stall for a human — partly adopted; premise corrected

**Correction.** The first pass quoted `SKILL.md:222` as calling the pre-flight
gate "this skill's one deliberate human [checkpoint]". Re-read at the same
commit (`5e5983d`), that sentence is about the plan-completion protocol's
resolve-before-defer gate — the batch that pending plan-mandated questions fold
into (now `:250-258`). Asking at pre-flight is still a local design choice, but
not the one that quote named, so the tension is narrower than first stated.

**What plan 22 brought.** Rulings now exist in one place: fix-round
adjudication records `Ruling: <what you decided> — <why> — <what it costs if
wrong>` and stops for the partner "only when every path forward is a guess"
(`:243-246`) — upstream's format and one of its four stops.

**What still asks.** Pre-flight (`:149-161`) presents conflicts as one batched
question before execution, and a clean scan proceeds "without comment" where
upstream's #2080 records the scan's checks in the ledger. Mid-run, a reviewer
finding that conflicts with plan text is "the human's decision" (`:320-324`).

Upstream v6.3.0 lets non-catastrophic conflicts take a recorded ruling so work
continues, with the spec as binding authority and the plan its argument.
Exactly four things still stop the run: an irreversible or destructive
operation; a security-sensitive action; a side effect outside the worktree
that norms say you ask about first; and a plan so broken that every path
forward is a guess.

**Why it matters more now.** Two v6.4.1 features assume rulings-not-stalls: the
executing-plans rebuild (finding 11) and the nested controller (finding 14).
Adopting either means settling this first.

**Decided 2026-10-21 (owner): rulings mid-run only.** Pre-flight keeps its one
batched question, asked while the partner is present at launch. A mid-run
reviewer finding that conflicts with plan text takes a recorded `Ruling: <what
you decided> — <why> — <what it costs if wrong>`, and the run continues.
Upstream's four stops still stop the run, and so does the explicit scope fence.
Consequences: finding 11's executing-plans port and finding 13's TDD wording go
to one spec (logged in `specs/deferred_items.md`, section
`owner-calls-2026-10-21`); finding 14 stays declined, since pre-flight still
asks.

### 8. Smaller items

- **`find-polluter.sh` — fixed by plan 50 (2026-10-18).** Plan 50 ported the
  three-part fix with a deterministic test and anchored the invocation as
  `<this-skill-dir>/find-polluter.sh`; where no test file matches, the port
  exits 2 rather than taking upstream's all-clear path. Its review found that
  upstream's `./` prefix drops top-level files from `*/test_*.py`, so the port
  also keeps the bare pattern as a third match (`NOTICE`). The record
  below is this revision's, from before the fix. The first pass's "fix
  directly" disposition was still not carried out: the only commit touching
  the file was still the layout move (`5fee1d7`), so the 2026-10-03 probe
  stood. It showed the bug is worse than first described:
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

  The 2026-10-03 repo audit records this fix and finding 12's range guards
  together as its item X3 (`specs/completed/audit-3-10-26.md`). Neither has an entry in
  `specs/deferred_items.md`.
- **Plan `Spec:` header pointer — adopted by plan 40.** Upstream has carried it
  since v6.3.0 (#2086). Our plan header now carries `**Spec:** <path>`, or
  `none`, after Tech Stack (`specs/completed/handoff-briefs.md` R2.1).
  Upstream's executing-plans also reads the spec at setup and ledgers a missing
  one, so rulings made without it are marked provisional; that half belongs to
  finding 11's port.
- **`finishing-a-development-branch` still advertises "Discard this work"** in
  both completion menus, now `:193` (4-option) and `:205` (detached HEAD).
  Upstream demoted discard to explicit-request-only, on the grounds that
  advertising it next to "Merge" offers to destroy finished, passing work, and
  has not changed it since. We have the typed-confirmation ritual; the issue is
  the menu placement.
- **Untracked-file guard on worktree removal — adopted by plan 60
  (2026-10-21), as an idea only.** Step 4b still requires
  `git status --porcelain --untracked-files=normal` to print nothing before
  merge or PR (`:220`), so Option 1 normally reaches `git worktree remove`
  (`:390`) clean. For a refusal caused by files created later, Step 6 now
  stops, names the cause, and lists the modified or untracked files. It never
  adds `--force` and never unlocks the worktree (`:396-399`). `NOTICE` credits
  upstream's idea, read at `bb92a77`, and plan 60 took no upstream text
  (decision D7).
- **`using-git-worktrees` guard content** is still in the Problem/Fix form
  (`:180-211`), not the house Excuse/Reality table. Format convergence only.
- **PR creation is no longer `gh`-only.** `f8b96c0` (2026-09-08) made `gh`
  optional with a compare-URL fallback (`:313-346`); Step 3's `gh repo view`
  probe (`:177`) fails silently into the ask path. Upstream's forge-agnostic
  rewrite adds little now.

## Findings 9–15 (v6.4.1 and v6.4.2), re-verified

### 9. writing-plans asks for code transcripts, and our plans show it

**Verified gap; the highest-relevance item in the 2026-10-03 pass, and still
open.** v6.4.2 (#2333) rewrote writing-plans around one claim: *a plan records
decisions; it is not a transcript of the code.* Its release notes name Opus 5.5
among the frontier models that "could get overzealous during plan writing",
sometimes trying to implement the whole project while designing the plan.
Planning here runs on Opus, the owner's session default, so this is the
configuration upstream named. The skill text no longer says so: plan 40
(`34cf7f8`) deleted the handoff's "planning belongs on the stronger tier" line,
and the handoff now leaves the execution model to launch time
(`writing-plans/SKILL.md:224-230`).

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
`writing-plans/SKILL.md:21` keeps "zero context ... questionable taste". `:78`
keeps "one action (2-5 minutes)". "No Placeholders" (`:167-175`) requires code
blocks for code steps, and `:179` says "Complete code in every step — if a step
changes code, show the code". The handoff repeats the premise (`:196-197`: "a
complete, zero-context handoff").

**Our plans show the pattern, including the two written since.** Below are
plans that implement a spec of their own: plan length against spec length, and
the share of plan lines inside code fences.

| Plan | Plan lines | Spec lines | Ratio | In-fence |
|---|---|---|---|---|
| 15 clean-code-family | 1397 | 229 | 6.1× | 53% |
| 16 llm-wiki-specs-harvest | 2254 | 262 | 8.6× | 73% |
| 17 agents-and-commands-expansion | 1073 | 260 | 4.1× | 38% |
| 22 sdd-hardening | 875 | 310 | 2.8× | 44% |
| 24 readonly-agent-guard | 1860 | 377 | 4.9× | 65% |
| 31 skill-model-pin-removal | 539 | 130 | 4.1× | 30% |
| 40 handoff-briefs (written 2026-10-09) | 6354 | 986 | 6.4× | 68% |
| 48 compaction-late-heading-ratchet (written 2026-10-16) | 361 | 61 | 5.9× | 27% |

Seven of the eight exceed 4× their spec, and three put more than 60% of their
lines inside fences. (The 2026-10-03 text counted four of six over 4×; plans 17
and 31 sit just over, at 4.1×.) Four caveats apply:

- Completed plans include their completion markup, which inflates length a
  little.
- The fence share comes from a line scan, not a parser. Re-run on 2026-10-18,
  the scan reproduces every earlier row's share. The specs of plans 15 and 22
  grew by a line or two in a status-header fix (`7137e5e`).
- Fence contents were not classified. For skill-text plans such as 15 and 40,
  much of what sits inside fences is verbatim skill wording, which the
  carve-out below treats as legitimate, so the share is an upper bound on
  transcript.
- Rows 40 and 48 are the plans written since this finding that implement a
  spec of their own. The other plans since (41, 42, 46, 47) have no spec. Each
  Claude Code drift-automation plan implements one stage of a shared roadmap
  spec, so its ratio would understate.

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

**What adopting it would not close.** No step checks the plan's test
assertions against the spec, and this finding adds none. The planner still
writes the tests and the code, so a planner's misread of the spec passes every
later gate. A local design for that gap, not an upstream finding, is deferred
in `specs/deferred_items.md`, item "Spec-reading test check".

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

Adopting this finding does not check the plan's test assertions against the
spec either. Its reviewers judge behavior the spec is silent on. A misread of
what the spec does say lands in the tests and the code alike, so it passes
them. The same local design covers that gap (`specs/deferred_items.md`, item
"Spec-reading test check").

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
each costs, and recommends one with a reason drawn from the plan. Plan 40
adopted this handoff half without Native mode
(`specs/completed/handoff-briefs.md` R2.2–R2.4); the executing-plans port below
stays open.

Ours (`executing-plans/SKILL.md`, 146 lines) has no workspace or ledger.
Progress lives in todos, so a `/clear` or compaction mid-plan loses its place —
the failure plan 22 fixed for SDD. It stops on any unclear instruction, and its
description routes it to tightly coupled plans rather than to cost.

It also carries local work upstream lacks:

- Step 1's record of the base-branch start (item 5, `:31-41`).
- Step 3's two-seat whole-plan review (code-reviewer plus Codex, worked through
  receiving-code-review; `:51-77`).
- The plan-completion protocol (Step 4) and the roadmap-stage handoff (Step 6,
  added by plan 40).

A port keeps those, reuses plan 22's `.sdd/<plan-basename>/` workspace, and
keeps the routing story `977a61a` unified. It takes the ledger and the
completion contract, plus `task-start` and `task-done` as new scripts with
tests in our convention. It depends on finding 7 for rulings-not-stalls and on
finding 13 for what "tests pass" means.

**Take `task-done` as fixed in v7.0.0 (#2388, `907ad21`).** Under
`set -euo pipefail`, a passing test command that printed nothing made the
script's last-line `grep` fail, so it exited 1 without writing the ledger line,
and a finished task looked unfinished. The fix records `→ (no output)`. A
port's test covers that silent pass.

**Port from v7.0.1, and budget the compaction window (#2563).** v7.0.1 deleted
the rebuilt skill's 52-line Example Workflow, which repeated rules stated above
it and left the file 405 bytes over 20,000. Its eval found no change: 8 of 8
inline runs passed on each arm, on Opus 5.5. Our copy is the pre-rebuild file
and never had that section, so #2563 needs no action on it. It does constrain
the port. Upstream's body is now 17,783 characters. Our local pieces above
(Step 1's item 5 and Steps 3, 4 and 6) come to about 3,600 more, about 21,400
in all. Our two-seat review would replace part of upstream's 3,248-character
Final Review, which wins some of that back, but the port has little headroom
or none. Its spec should plan a `references/` split from the start (finding
17).

Native mode on a mid-tier session model matches this repo's routing, where
execution runs in a fresh session on a model chosen at launch.

### 12. SDD script hardening (v6.4.1, v7.0.0)

Four upstream fixes to the scripts plan 22 touched, judged separately:

- **`review-package` accepts empty and non-descendant ranges — adopted by
  plan 50 (2026-10-18)**, upstream's guards verbatim with a test for each. The
  record below is from before the fix: the script had not changed since the
  2026-10-03 probes:
  - Probe, BASE == HEAD: it wrote `review-<sha>..<sha>.diff` with "0 commit(s)"
    and exited 0.
  - Probe, BASE on a sibling branch: it wrote a package whose diff carries the
    sibling's only file as `deleted file mode 100644` — a phantom deletion —
    and exited 0.

  Upstream (#2136, #2050) adds two guards that exit 3:
  `git merge-base --is-ancestor "$base" "$head"`, and a non-zero
  `git rev-list --count`. Our argument order is already upstream's, so the
  guards drop in after `review-package:22-23`, with a test for each.
- **`sdd-workspace` overwrites a committed `.gitignore` — verified, low
  (v7.0.0, #2399, `19e54c0`); adopted by plan 50 (2026-10-18).** Before the
  fix, `sdd-workspace:47` wrote `*` to
  `.sdd/.gitignore` on every run. Probe, 2026-10-18: in a scratch repository
  that committed its own `.sdd/.gitignore`, one run left the file modified,
  cut back to `*`. This repo never commits that file, since it deletes each
  workspace at plan end and keeps git history as the record. But the skill
  installs into every repository the owner works in. Upstream now writes the
  default only when no file exists, a one-line change.
- **Plans sharing a basename share a workspace — decided locally, no action.**
  The probe confirms that `docs/alpha/plan.md` and `docs/beta/plan.md` both
  resolve to `.sdd/plan`. The 2026-09-03 completion gate handled this as
  deferred item M2. It recorded the assumption in `sdd-workspace:31-38`, and
  relies on the ledger's `Plan:` first line to make a collision visible
  rather than silent, with "stop and say so" on a mismatch (`SKILL.md:400-402`,
  `:410-413`). Upstream (#2138, #2045) prevents the collision outright: a
  `plan-path` marker, disambiguation by parent directory and then a counter,
  and legacy workspaces adopted in place. Exposure here stays low, because a
  collision needs the same `<id>-<spec-name>` in the same working tree.
  Upstream's scheme is the ready port if M2 is revisited, together with
  v7.0.0's Git Bash fix to its markers (`2b7893a`), which spells the
  repository root the way it spells the plan path.
- **Interpreter invocation (#2301) — low.** Upstream prefixes `bash` and `node`
  because some marketplace packagers strip exec bits. Our installs keep them:
  symlinks do, and `install.py --copy` uses `shutil.copy2`. The live issue in
  this class is path resolution, not exec bits. `find-polluter.sh` (finding 8)
  was the instance that mattered, and plan 50 anchored it; the
  `./render-graphs.js` call at `writing-skills/SKILL.md:337-338` is the same
  pattern in an authoring-only context.

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
  recommends a fresh session for execution, with the model chosen at launch
  (`writing-plans/SKILL.md:224-230`).
- **A nested controller cannot hold our human checkpoints.** Claude Code
  removes `AskUserQuestion` from every non-fork subagent (`sub-agents.md`,
  "Available tools"; re-checked at 2.1.302). The pre-flight batched question
  and the plan-completion gate would each end such an orchestrator's run. A
  fork keeps the main session's tools, but it also runs on the main session's
  model ("How forks differ from other subagents"), so it cannot be the
  mid-tier orchestrator upstream measured. Upstream can nest because it rules
  where we ask.

**Correction.** The 2026-10-03 text said Claude Code removes `AskUserQuestion`
from every subagent. The docs exempt forks, at 2.1.288 as at 2.1.302. The
conclusion stands on the narrower premise.

This stays a function of finding 7, which was decided on 2026-10-21 as rulings
mid-run only, so this finding stays declined.

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

v7.0.1 (#2569) changes only the issues it drafts. They gain two sections, who
is filing and a summary that a human wrote, and the skill files nothing while
the summary is a placeholder. Its prefilled link now opens the Bug Report
template. The disposition does not change.

## New findings (v7.0.0)

v7.0.0's main change, the brainstorming rebuild, was finding 4's upstream
baseline until plan 70 rebased the finding on v7.0.1, and finding 4 is rewritten
above. Its `task-done` and `sdd-workspace` fixes join findings 11 and 12. One
finding is new.

### 16. Two v7.0.0 bug fixes apply to our copies as they stand — adopted

Plan 50 (2026-10-18) ported both fixes verbatim, with a regression test for the
companion server (`brainstorming/scripts/test_server.py`) and a dummy-value
probe for the debugging example; `NOTICE` records them. The record below is
from before the fix.

Both verified by probe on 2026-10-18.

- **The visual companion mangles screens that contain `$` sequences (#2364,
  `ddd35ab`).** `brainstorming/scripts/server.cjs:223` inserts each screen
  fragment with `String.replace('<!-- CONTENT -->', content)`, which reads
  `$'`, `$&`, and their kin in `content` as replacement patterns. Probe: given
  `<p>A: $' B: $&</p>`, our `wrapInFrame` inserted the rest of the frame
  template at `$'` and the `<!-- CONTENT -->` marker itself at `$&`. A mockup
  that shows prices, shell, or regex text can trip it. Upstream's fix passes a
  replacer function, `() => content`. We ship no server tests; upstream's
  regression test is in `tests/brainstorm-server/server.test.js`.
- **systematic-debugging's diagnostic example prints the secret it checks for
  (#2380, `e592b34`).** `systematic-debugging/SKILL.md:98` echoes
  `${IDENTITY:+SET}${IDENTITY:-UNSET}`, which prints `SET` and then the value
  whenever the variable is set. `:102` runs `env | grep IDENTITY`, which prints
  the value too. Probe, with a dummy value: the first line printed `SET`
  followed by the value, and the substring match also printed an unrelated
  variable from the session environment. An agent that copies the example into
  CI or a shared log leaks a signing identity. Upstream's replacement reports
  presence only: `$([ -n "${IDENTITY:-}" ] && echo SET || echo UNSET)`, and
  `printenv IDENTITY >/dev/null 2>&1 && …`.

Both are small and mechanical. The second edits a discipline skill, but it
corrects example code rather than wording that steers behavior, so it needs no
micro-test.

## New finding (v7.0.1)

v7.0.1's main change, the brainstorming retune (#2560, #2571), is finding 4's,
and plan 70 adopted it. Its #2563 joins finding 11, and #2569 joins finding 15
and the dismissed list. One finding is new.

### 17. Skill bodies run past the compaction re-attach cut

**The upstream claim (#2481).** After a compaction, Claude Code re-attaches
each invoked skill cut at 20,000 characters. Text past the cut is gone for the
rest of the session. The issue's transcript (Claude Code 2.1.285 to 2.1.292)
shows four things:

- Each re-attached copy of subagent-driven-development was cut at exactly
  20,000 characters. Each ended with a marker that tells the model to Read the
  skill file for the full text.
- The five-round cap sat past the cut, at character 22,573 of v6.4.1's file.
- After later compactions, the skill dropped out of the re-attached list
  altogether.
- The model never re-read the file, and one task ran 18 fix rounds.

That matches what this repository assumes. The guide says compaction keeps
the first 5,000 tokens of each invoked skill
(`specs/guides/claude-code-customization-guide.md:128`). The
`compaction-window` check in `build/cc_guide/conformance.toml` turns that into
5,000 × 4 = 20,000 body characters. Two facts in the transcript are not in the
guide: the cut counts characters, not tokens, and the marker points the model
at the file. The second bears on the re-invoke question below.

**The size bar (#2481, `tests/skill-size/test-skill-size.sh`) — already
covered.** Upstream's new test fails any `SKILL.md` of 20,000 bytes or more.
Our `compaction-window` check gates the same limit. `build/check_conformance.py`
runs it as a commit lint, and any finding it does not waive fails the commit.
It also does a thing upstream's test does not: it flags a critical-sounding
heading that starts past the window. The two bars measure different things:

| | Upstream's test | Our check |
|---|---|---|
| Measures | the whole file, frontmatter included | the body after the frontmatter |
| Unit | bytes | characters |
| Fails at | 20,000 or more | more than 20,000 |
| Late critical headings | not checked | checked |

Probe, 2026-10-28. This session does not run downloaded code, so it applied
the test's rule with a local loop. The loop ran `wc -c` on each of our 36
`skills/*/SKILL.md` files and failed any at 20,000 bytes or more. Four fail:

| Skill | Bytes | Body characters | Our check |
|---|---|---|---|
| bayesian-workflow | 36,550 | 35,223 | waived by `skill-body-past-compaction` |
| subagent-driven-development | 31,206 | 30,268 | waived by `skill-body-past-compaction` |
| writing-skills | 30,575 | 29,717 | waived by `writing-skills-late-critical-headings`, which waives the whole check for that file |
| finishing-a-development-branch | 20,787 | 19,970 | passes, 30 characters inside |

finishing-a-development-branch is the one file where the two bars disagree.
Its last section, Red Flags, starts at body character 18,671. Nothing read for
this pass shows whether Claude Code counts the frontmatter, or any header it
adds, toward the cut. If it does, the end of Red Flags is cut already. A live
probe under `build/cc_guide/` could settle that, and `specs/deferred_items.md`
logs it (section `superpowers-drift-v7.0.1`). Until then our check stays the
gate. The next edit that grows this body fails the commit lint, and plan 60 has
already moved this skill's Common Mistakes into `references/` once. No action
now. The owner decided on 2026-10-28 not to adopt upstream's stricter bar
until the probe has run.

**The SDD move (#2565) — prior art for an open deferred item.** Upstream moved
seven parts of subagent-driven-development into `references/`, each behind a
pointer at the step that needs it: `fix-loop.md`, `final-review.md` (Finish
included), `handling-reports.md`, `resuming.md`, `preflight.md`, `batching.md`
and `cannot-verify.md`. The fix-loop pointer is the strongest. It tells the
controller to read the file again before every round, because its memory of
the file does not survive compaction. The file fell from 32,577 bytes to
19,506. The PR moved the text verbatim and checked that every old line
survives.

The PR rejected two alternatives. Compressing the prose would rewrite tuned
text. A cap reminder near the top had already failed. The process graph inside
the first 20,000 characters named the cap, and the controller still ran 18
rounds. The PR also names the limit of any fix in the skill file. Nothing in
the file helps when the skill drops out of the re-attached list.

**There is no measured bar.** Upstream's eval runs one headless turn after a
simulated compaction, at round 5 with a finding still open. Each arm parked
the finding instead of starting round 6, in 10 of 10 runs (5 each on Opus 5.5
and Sonnet 5.5). The arms were v7.0.0 cut at 20,000, v7.0.0 whole, and the
split. The split arm read `fix-loop.md` in 10 of 10 runs. The PR calls this a
regression check, not a reproduction, because a short, clean context does not
show the long-session failure.

**How it maps onto ours.** Our body is 30,268 characters. Plan 46 already
moved our fix-round cap inside the window: Fix Rounds starts at character
13,856. Our risk is the text past character 20,000, near line 326. That is the
end of Constructing Reviewer Prompts (with the two final-review bullets the
deferred item names), then File Handoffs, Durable Progress and Context
Checkpoints. Upstream's seven parts map onto these parts of
`subagent-driven-development/SKILL.md`:

| Upstream reference | Our text | Characters |
|---|---|---|
| `batching.md` | The Process, batching paragraphs (`:128-154`) | 1,706 |
| `preflight.md` | Pre-Flight Plan Review (`:156-169`) | 661 |
| `handling-reports.md` | Handling Implementer Status, all but DONE (`:204-215`) | 1,033 |
| `cannot-verify.md` | Handling Reviewer ⚠️ Items (`:216-226`) | 594 |
| `fix-loop.md` | Fix Rounds (`:227-255`) and three fix bullets (`:323-339`) | 2,897 |
| `final-review.md` | Plan Completion (`:256-294`) and the final-review bullets (`:340-355`) | 3,339 |
| `resuming.md` | Durable Progress, the resume bullets (`:405-417`) | 985 |
| Total | | 11,215 |

Moving all of it leaves 19,053 characters. Upstream's seven pointers come to
1,354 characters, and pointers of that length bring our body back to about
20,400. **Upstream's map alone does not clear our window.** The last 400
characters or more must come from parts upstream does not have. File Handoffs
(`:356-394`, 2,518 characters) and Context Checkpoints (`:439-461`, 1,258) are
the candidates.

**A port takes the map, not upstream's files.** Upstream's references differ
from our text in ways a copy would bring in silently:

- They put the workspace under `.superpowers/sdd/`, where ours uses `.sdd/`
  (finding 1), and they name skills with the `superpowers:` prefix.
- `preflight.md` rules on each conflict. Ours asks the partner one batched
  question (`:164-168`), which finding 7's decision of 2026-10-21 keeps.
- `fix-loop.md` rules on a plan-mandated finding. Ours still calls it the
  human's decision (`:328-332`). Finding 7's decision changes that to a
  ruling, and the open executing-plans port spec item carries the change.
- `fix-loop.md` escalates to a stronger model at round 4. Ours escalates
  context, then effort, then model (finding 6).
- `final-review.md` has one review seat and lists the rulings in the final
  message. Ours has two seats, code-reviewer and Codex, and hands the rulings
  to the plan-completion gate.

So a port moves our own text verbatim behind pointers at upstream's places,
and takes upstream's re-read wording for the fix loop. That wording steers
behavior in a discipline skill, so writing-skills' micro-test applies, as the
deferred item already says.

**It also bears on a second deferred item.** Part 3 of "Three
subagent-driven-development decisions" asks whether the skill should tell the
controller to re-invoke it after compaction. Upstream does not re-invoke.
It re-reads each step's reference from disk at that step. Claude Code's own
marker already points at the file, and #2481's controller still never read
it. Upstream therefore puts the pointer at the step. Nothing measured shows
which works better.

**The writing-skills move (#2564) — prior art for an open deferred item.**
Upstream moved three parts into new references, each behind a pointer: the
SKILL.md template with all of Skill Discovery Optimization (`discovery.md`),
bulletproofing (`bulletproofing.md`), and flowchart conventions
(`flowcharts.md`). It also moved its supporting files into `references/`. The
rule that a description names triggers, never the workflow, stays in
SKILL.md. The file fell from 26,623 bytes to 16,738. Its eval found no change
between the arms. On each arm, 12 of 12 written skills had a description in
the required form, and 6 of 6 discipline skills tabled every rationalization.
Every split-arm run read the reference its scenario called for.

The same map fits ours, with room to spare:

| Moved part | Our text (`writing-skills/SKILL.md`) | Characters | Lines |
|---|---|---|---|
| Template | SKILL.md Structure (`:104-153`) | 3,000 | 50 |
| Discovery | Skill Discovery Optimization (`:154-316`) | 7,263 | 163 |
| Flowcharts | Flowchart Usage (`:317-350`) | 1,156 | 34 |
| Bulletproofing | Bulletproofing Skills Against Rationalization (`:503-578`) | 2,360 | 76 |
| Total | | 13,779 | 323 |

The body falls from 29,717 characters to about 15,900, or about 17,000 with
pointers as long as upstream's. The file falls from 716 lines to about 400.
That closes three parts of the open item "Split and rewrite writing-skills
against the guide":

- The body drops below 500 lines, which clears `check_frontmatter.py`'s WARN.
- The late heading Create Red Flags List moves out with bulletproofing.
- STOP: Before Moving to Next Skill starts near character 13,700, inside the
  window. With both late headings gone, exception
  `writing-skills-late-critical-headings` can go.

It does not close the rest of that item: the `writing-skills-guide-gaps` gap,
the `writing-skills-tdd-for-docs` deviation, and the skill's claim about `@`
links. Only the skill itself links its support files
(`persuasion-principles.md`, `testing-skills-with-subagents.md`,
`graphviz-conventions.dot`), so moving them changes no install dependency.

**Disposition, per claim unit:**

- **#2481 and the size test: already covered** by the `compaction-window`
  check. Decided 2026-10-28 (owner): do not add upstream's whole-file byte bar
  now. The logged probe runs first. If it shows that Claude Code counts the
  frontmatter toward the cut, correct the register's window.
- **#2565: fix directly, no spec.** It runs as a plan through the open item
  "Fit the subagent-driven-development and bayesian-workflow bodies inside the
  compaction window" (section `46-sdd-bundle`, Size: plan). Upstream's map is
  the skeleton, plus about 400 characters from our own sections. The
  bayesian-workflow half has no upstream counterpart, but the same pattern
  applies. Decided 2026-10-28 (owner): this plan runs before the
  writing-skills split.
- **#2564: fix directly, no spec, for the split.** Decided 2026-10-28
  (owner): the split runs first as a plan without a spec, after the SDD plan
  (`specs/deferred_items.md`, item "Split writing-skills along upstream
  v7.0.1's map"). The rest of the open item "Split and rewrite writing-skills
  against the guide" stays a spec candidate (Size: design).
- **#2563: already covered** for our file. It constrains finding 11's port.

No execution of the items above starts before plan 69's execution has ended.
The owner set that order on 2026-10-28, while another session was executing
plan 69. Plan 69 also edits the `build/cc_guide/` probe files that the probe
item would touch.

## Suggested disposition

Under this repo's proportional-process rule:

- **Done:** findings 1, 2, 5, and 6, through plan 22 (2026-09-03); finding 8's
  `Spec:` pointer and finding 11's handoff half, through plan 40 (merged
  2026-10-12). Through plan 50 (2026-10-18), the four "fix directly, no spec"
  items, in one plan without a spec:
  - Finding 8's `find-polluter.sh`: the three-part script fix, a deterministic
    test, and the invocation anchor, the first pass's disposition.
  - Finding 12's `review-package` range guards, with tests. With the item
    above, this closes the 2026-10-03 audit's X3.
  - Finding 16's two fixes: the companion server's replacer function and the
    debugging example.
  - Finding 12's create-only `.gitignore` in `sdd-workspace`, the optional
    item.

  Through plan 60 (2026-10-21), finding 8's untracked-file guard, as an idea
  credited in `NOTICE` with no upstream text.
- **Decided 2026-10-28 (owner):** finding 17's three calls, approved as
  recommended. Execution of each waits until plan 69's execution has ended.
  The SDD plan runs first, then the writing-skills split. Upstream's byte bar
  is not adopted until the probe has run.
- **Done, SDD half of finding 17:** through plan 71 (2026-10-29). Our own text
  moved verbatim into upstream's seven references plus `file-handoffs.md` and
  the Context Checkpoints section, with the fix-loop re-read pointer. Plan 71
  also applied the owner's three rulings on "Three subagent-driven-development
  decisions": the Fable round-5 rung and the trivial-fix exception; the
  recovery line was dropped because the control already recovered (D3).
  Results: `specs/red-baseline-sdd-compaction.md`. Exception
  `skill-body-past-compaction` is gone.
- **Done, writing-skills half of finding 17:** through plan 72 (2026-10-29).
  Our own text moved verbatim into upstream's three references
  (`discovery.md`, `flowcharts.md`, `bulletproofing.md`); the description
  rule and the supporting files stay beside SKILL.md. The body fits the
  window and is under 500 lines, so exception
  `writing-skills-late-critical-headings` and the `critical_placement`
  lint are gone. Results: `specs/red-baseline-writing-skills-split.md`. The
  rest of "Split and rewrite writing-skills against the guide" stays a spec
  candidate.
- **Not adopted until the probe has run:** upstream's whole-file byte bar
  (finding 17). finishing-a-development-branch is the one skill that passes
  our check and fails the stricter bar. The probe item decides the measure.
- **Spec candidate, planning surface:** findings 9 and 10. They share the
  writing-plans plan template and self-review, and finding 10 also reaches
  the four reviewer surfaces. Both shape
  discipline-skill behavior, so they need writing-skills' pressure-test and
  micro-test. Upstream's planted-defect probe and its unnamed-input crash eval
  are ready controls.
- **Done, brainstorming:** finding 4, through plan 70 (2026-10-28): the skill
  was rebased on v7.0.1 (`2ce8aa1`) and tested against its own RED baseline,
  `specs/red-baseline-brainstorming-2026-10-28.md`. The GREEN bars are met under
  the registered rules. On the registered verdicts, T7 (the first-question case)
  meets its bar under the letter reading of its rule. The owner chose that
  reading on 2026-10-28. The owner also had the Red Flags row that the pressure
  test added and the sentence that lists what isn't implementing reworded on
  that day. Plan 70 re-ran the cases judged, not measured, to be within reach of
  those edits, and the re-run met every bar.
- **Decided 2026-10-21:** finding 7, as rulings mid-run only. The two items
  that hung on it:
  - Finding 11's executing-plans port, which gets its own spec; its handoff
    half was adopted by plan 40. Finding 13's TDD wording travels with it,
    micro-tested. Port from v7.0.1, which drops the Example Workflow (#2563).
    With our local steps, the body has little or no room under the compaction
    window, so the spec plans a `references/` split from the start.
  - Finding 14, which stays declined.
- **Prospective only:** finding 3. Adopt the falsifiability material if you
  want the guidance; do not take the compression without clearing upstream's
  measured bar.
- **Not adopted, recorded:** finding 12's basename collision (decided as M2,
  with v7.0.0's Git Bash marker fix) and interpreter prefixes, finding 14, and
  finding 15, which v7.0.1's #2569 does not change.
- **Declined:** v7.0.1's contribution templates and policy (#2569), which
  govern contributions to upstream's own repository.
- **Already covered, no action:** finding 17's size bar (#2481, the skill-size
  test) and #2563 for our executing-plans.

Any adoption needs a `NOTICE` change-list entry. The two existing "adopted
FROM upstream" entries are the model: name what was taken, from which release,
and where the port deliberately diverges. When the next pass runs, update this
document's "Next review starts from" row along with the findings.
