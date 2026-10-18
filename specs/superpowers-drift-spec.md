# Superpowers drift assessment

**Status:** findings only. No skill files were edited. This document exists to
decide *what, if anything, becomes a spec*.

It is a living record: each review re-baselines it in place rather than adding
a dated copy. This revision (2026-10-18) brings it to upstream v7.0.0 and
re-takes every line anchor against the current tree. The 2026-10-03 revision
brought it to v6.4.2; the first pass (2026-09-03, against v6.3.0) lived at
`specs/superpowers-drift-2026-09-03.md` until that revision renamed it.
Finding numbers never change, because other documents cite them (`NOTICE`,
`specs/completed/sdd-hardening.md`, `specs/completed/handoff-briefs.md`,
`specs/audit-3-10-26.md`).
Findings 1–8 are the first pass's, 9–15 came from v6.4.x, and findings from
v7.0.0 start at 16.

## Scope and method

| | |
|---|---|
| Vendored baseline | `896224c` (v6.0.3, 2026-06-18), per `NOTICE` |
| Adoption baselines | `b36e082` (v6.3.0) for the four pieces plan 22 (SDD hardening) adopted: findings 1, 2, 5, 6. `8ca22db` (v6.4.2) for the two pieces plan 40 (handoff briefs) adopted: finding 8's `Spec:` pointer and finding 11's handoff half |
| Previous review | `8ca22db` (v6.4.2, 2026-09-25), reviewed 2026-10-03 |
| Upstream HEAD | `bb92a77` (v7.0.0, 2026-10-09) |
| Commits since previous review | 1 squash merge, `bb92a77`; upstream's `dev` branch keeps one commit per pull request |
| Files changed under `skills/` since previous review | 8 (+240 / −321) |
| Unreleased skill work | None: `dev`'s `skills/` tree matches `main`. Of the branches new since the last pass, two hold older drafts of v7.0.0's brainstorming text and one matches `main` |
| Next review starts from | `bb92a77` |

Comparison is **per behavioral claim, not per diff hunk**. `NOTICE` records that
most vendored files were adapted on the way in, so neither baseline is a true
ancestor of our copies and a mechanical three-way merge produces noise. Each
upstream RELEASE-NOTES entry was instead read as a claim and checked against our
tree: *does our copy already satisfy the intent?* v6.4.1, v6.4.2, and v7.0.0
each landed as one squash commit, so commit counts say nothing about scope. The
claim units are the release notes' pull-request numbers (obra/superpowers pull
requests, written #NNNN below), and `dev`'s per-PR commits are cited where a
port would start from the diff. Where a claim is about script behavior, a probe
in a scratch repository decided it rather than a reading.

That distinction is load-bearing. Upstream's `0b47219` (2026-07-05) fixes a
worktree path recomputed after `cd`, which made cleanup silently no-op. It
landed after our vendoring, so a diff-driven read flags us as behind. We are
not: `finishing-a-development-branch/SKILL.md:339` carries an equivalent guard
("Do NOT re-run detection here"), present since the layout move (`5fee1d7`).
**Already covered.** Whether that guard arrived as adaptation or the vendoring
record is imprecise about this file is undetermined, and does not change the
disposition.

Most line anchors moved since the last pass. Plan 40 rewrote parts of
`writing-plans/SKILL.md`, and plan 46 (the SDD bundle, 2026-10-15)
restructured `subagent-driven-development/SKILL.md`. Elsewhere, the `cc-guide`
citation line added near the top of every file that rests on the Claude Code
guide (`4efba4e`) shifted anchors by one.

## Status of earlier findings

| # | Finding | Status at 2026-10-18 |
|---|---|---|
| 1 | SDD workspace has no plan identity | **Adopted** — plan 22 |
| 2 | Implementers can spawn duplicate reviewers | **Adopted** — plan 22 |
| 3 | TDD reference has no falsifiability discipline | Open, prospective only; upstream unchanged |
| 4 | Brainstorming ceremony does not scale | Open; upstream rebuilt the skill (v7.0.0) and loosened its gate, so the finding is rewritten |
| 5 | Every task gets its own dispatch | **Adopted** — plan 22 |
| 6 | SDD review loop has no round cap | **Adopted** — plan 22, with a deliberate ladder divergence |
| 7 | Pre-flight conflicts stall for a human | Partly adopted (fix-round rulings); premise corrected; still a decision |
| 8 | Smaller items | `find-polluter.sh` **fixed** — plan 50; two items partly covered; the `Spec:` pointer adopted by plan 40 |
| 9 | writing-plans asks for code transcripts | Open; both plans written since that implement their own spec show the pattern; its tier premise re-sourced |
| 10 | Reviewers grade the spec's silence | Open; upstream unchanged |
| 11 | executing-plans was rebuilt as a ledgered native mode | Handoff half adopted by plan 40; the port is open and waits on 7; upstream has since fixed `task-done` |
| 12 | SDD script hardening | `review-package` range guards and v7.0.0's create-only `.gitignore` **adopted** — plan 50; the basename collision stays decided (M2) |
| 13 | TDD does not say what "other tests" means | Open; travels with 11 |
| 14 | Nested controller on Claude Code | Not adopted; premise narrowed to non-fork subagents |
| 15 | diagnosing-superpowers | Not adopted |

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
- **`LICENSE`.** Unchanged since the vendoring, and byte-identical to our
  `LICENSE-superpowers` (re-checked at v7.0.0).

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

### 4. Brainstorming ceremony does not scale — open; upstream rebuilt the skill

Our side is unchanged. `brainstorming/SKILL.md:22` still carries
*"Anti-Pattern: This Is Too Simple To Need A Design"*, and the nine-step
checklist (`:26-38`) ends in a committed spec, a user review, and a
fresh-session handoff for every request, including a config change. The
proportional-process policy recorded for this repo (brainstorming and specs
only for open design decisions; minor work fixed directly) still lives in
`/deferred` while this skill argues the opposite.

**What earlier passes compared against is gone.** The 2026-10-03 text measured
us against v6.3.0's three-path router (#2063) and v6.4.1's additions to it
(#2258). v7.0.0 replaced both with a rewrite from scratch (#2463, `9e63918`).
Its design record
(`docs/superpowers/specs/2026-10-05-brainstorming-rebuild-design.md`) says the
old skill had grown to about 2,600 words, mostly routing, approval gates, and
the spec-to-plan handoff. The new SKILL.md is 225 lines. The earlier pieces map
onto it like this:

- **The router becomes sizing.** The spike / bounded / architectural
  classification, made up front, becomes three sizes chosen once intent is
  clear. A quick, clear task is done at once, a small change is agreed in
  chat, and a project gets a written design and then a plan. The skill names
  the size in plain words, and the partner can override it. The one-way
  ratchet survives: "If it grows mid-task, stop, say so, and step up a size."
- **Shared Understanding becomes describing and playback.** The first message
  offers to skip the questions, then asks one open question about "a real
  moment or a concrete picture". A menu comes only when the partner is stuck.
  Each part is played back in 200–300 words as soon as it is understood, with
  guesses marked as guesses, before the questions move on. #2258's write-back
  note becomes continuous. Ours asks about "purpose/constraints/success
  criteria" (`:32`) but plays back only the design (`:34`), never the
  understanding.
- **Stage-scoped approval becomes one gate.** Nothing gets built until the
  partner approves the full description: in chat for a small change, the
  document for a project. #2258's stage-by-stage list is gone. Its failure,
  approval of scope read as approval to build, survives as a Red Flags row:
  "Approval covers what you showed them." Ours already stages approval: the
  design (`:34`), then the written spec (`:37`), then the fresh-session
  handoff.
- **The spec-document reviewer becomes a builder check.** A fresh subagent
  (`builder-check-prompt.md`) reads the design as the person who will build it
  and lists what it would still need to ask. Brainstorming answers what it
  can, settles minor points itself and marks them as its own calls, and brings
  the rest to the partner in one round.
- **Context exploration becomes an offer.** Ours explores the project first,
  unasked (`:30`). v7.0.0 offers to look at the project, the partner's files,
  or the web once there is some grounding, and the partner decides.

Two pieces are new:

- **How it gets made (#2482, #2483).** Find out early which choices of
  platform, language, libraries, or medium the partner wants to make. State
  defaults in plain words, and record a choice the agent made "as your call,
  never as something they agreed to", on the skip path too. The motivating
  failure: a session designed an iOS app, never asked about platform, and
  built a web app.
- **Spikes.** A throwaway build the partner says yes to skips tests, plan,
  and review. Keeping what it produced is a new request that goes back through
  the gate.

**v7.0.0 loosens the gate.** The 2026-10-03 text recorded that #2063 did not
weaken the gate. v7.0.0 does, in three ways: a quick, clear task is done
without a design step; a partner who opts out of the questions ends the skill,
"and the gate goes with it"; and an accepted spike may be built. The first
matches this repo's proportional-process policy. The opt-out and the spike
exemption are the owner's decision, not a free port.

**Two rules contradict ours outright.**

- v7.0.0's first Red Flags row is "Options steer. Ask them to describe it
  first." Ours says "Prefer multiple choice questions when possible" (`:77`)
  and keeps "Multiple choice preferred" as a key principle (`:151`).
- v7.0.0 generates several ideas privately and shows the comparison "only when
  it helps them decide". Ours proposes 2-3 approaches every time (`:33`,
  `:153`).

**There is no measured bar this time.** v6.4.1 and v6.4.2 shipped eval
numbers. v7.0.0's release notes report none, the design record's last section
is "Will be tuned after first use", and the two evals it names for rewriting
(`brainstorming-todo-purpose-discovery`, `brainstorming-todo-shared-intent`)
are not in the repository. A port needs its own RED baseline.

**What a port keeps:**

- Our `Use when…` description (`:2-8`). Upstream's "You MUST use this before
  any creative work" fails this repo's frontmatter rule.
- Our software-specific guidance (`:95-106`: design for isolation, working in
  existing codebases). v7.0.0 went domain-general, to "a talk, a business, a
  renovation".
- The repo lifecycle: `specs/<name>.md`, the `deferred_items.md` check
  (`:30`), and the fresh-session handoff to writing-plans (`:38`). v7.0.0
  invokes writing-plans with no fresh-session step, and writes to
  `docs/superpowers/specs/`.

v7.0.0 also drops the visual-companion offer's token-cost warning, which ours
keeps (`:162`).

A port is a rewrite of our skill, and brainstorming is a discipline skill, so
it gets writing-skills' pressure-test and micro-test. Its RED cases should
include the two failures upstream named: approval of scope read as approval to
build (#2258), and a platform choice nobody asked about (#2482).

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
Adopting either means settling this first. **Decide, don't assume** still
stands.

### 8. Smaller items

- **`find-polluter.sh` — fixed by plan 50 (2026-10-18).** Plan 50 ported the
  three-part fix with a deterministic test and anchored the invocation as
  `<this-skill-dir>/find-polluter.sh`; where no test file matches, the port
  exits 2 rather than taking upstream's all-clear path (`NOTICE`). The record
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
  together as its item X3 (`specs/audit-3-10-26.md`). Neither has an entry in
  `specs/deferred_items.md`.
- **Plan `Spec:` header pointer — adopted by plan 40.** Upstream has carried it
  since v6.3.0 (#2086). Our plan header now carries `**Spec:** <path>`, or
  `none`, after Tech Stack (`specs/completed/handoff-briefs.md` R2.1).
  Upstream's executing-plans also reads the spec at setup and ledgers a missing
  one, so rulings made without it are marked provisional; that half belongs to
  finding 11's port.
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
(`writing-plans/SKILL.md:219-224`).

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
`writing-plans/SKILL.md:16` keeps "zero context ... questionable taste". `:73`
keeps "one action (2-5 minutes)". "No Placeholders" (`:162-170`) requires code
blocks for code steps, and `:174` says "Complete code in every step — if a step
changes code, show the code". The handoff repeats the premise (`:192-193`: "a
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
each costs, and recommends one with a reason drawn from the plan. Plan 40
adopted this handoff half without Native mode
(`specs/completed/handoff-briefs.md` R2.2–R2.4); the executing-plans port below
stays open.

Ours (`executing-plans/SKILL.md`, 142 lines) has no workspace or ledger.
Progress lives in todos, so a `/clear` or compaction mid-plan loses its place —
the failure plan 22 fixed for SDD. It stops on any unclear instruction, and its
description routes it to tightly coupled plans rather than to cost.

It also carries local work upstream lacks:

- Step 1's record of the base-branch start (item 5, `:27-37`).
- Step 3's two-seat whole-plan review (code-reviewer plus Codex, worked through
  receiving-code-review; `:47-73`).
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
  is the instance that matters; the `./render-graphs.js` call at
  `writing-skills/SKILL.md:337-338` is the same pattern in an authoring-only
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
  recommends a fresh session for execution, with the model chosen at launch
  (`writing-plans/SKILL.md:219-224`).
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

## New findings (v7.0.0)

v7.0.0's main change, the brainstorming rebuild, is finding 4's new upstream
baseline, and finding 4 is rewritten above. Its `task-done` and `sdd-workspace`
fixes join findings 11 and 12. One finding is new.

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
- **Spec candidate, planning surface:** findings 9 and 10. They share the
  writing-plans plan template and self-review, and finding 10 also reaches
  the four reviewer surfaces. Both shape
  discipline-skill behavior, so they need writing-skills' pressure-test and
  micro-test. Upstream's planted-defect probe and its unnamed-input crash eval
  are ready controls.
- **Spec candidate, brainstorming:** finding 4, now against v7.0.0 rather than
  the v6.x router. The spec has to carry the owner's calls on the opt-out, the
  spike exemption, and open questions over multiple choice. Upstream expects to
  tune v7.0.0 after first use, so re-read upstream when the spec starts. It is
  micro-tested before deployment against its own RED baseline, since upstream
  published none.
- **Decide first:** finding 7. Two items hang on it:
  - Finding 11's executing-plans port, which merits its own spec once 7 is
    settled; its handoff half was adopted by plan 40. Finding 13's TDD wording
    travels with it, micro-tested.
  - Finding 14, which stays declined unless 7 goes to rulings.
- **Prospective only:** finding 3. Adopt the falsifiability material if you
  want the guidance; do not take the compression without clearing upstream's
  measured bar.
- **Not adopted, recorded:** finding 12's basename collision (decided as M2,
  with v7.0.0's Git Bash marker fix) and interpreter prefixes, finding 14, and
  finding 15.

Any adoption needs a `NOTICE` change-list entry. The two existing "adopted
FROM upstream" entries are the model: name what was taken, from which release,
and where the port deliberately diverges. When the next pass runs, update this
document's "Next review starts from" row along with the findings.
