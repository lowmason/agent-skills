# Superpowers drift assessment

**Status:** findings only. No skill files were edited. This document exists to
decide *what, if anything, becomes a spec*.

This versioned assessment continues the
[archived v7.0.1 record](completed/superpowers-drift-spec-v7-0-1.md), formerly
`specs/superpowers-drift-spec.md`. This revision (2026-11-07) brings it to
upstream v7.0.2 for every skill. It edits the status table, the Scope and method table, findings 4, 8, 11,
15 and 17, and adds findings 18 to 33. Findings 1–2, 5–7, 9–10, 12–14 and 16
stand as the 2026-10-28 revision wrote them, at the anchors the 2026-10-31
re-anchor took; this revision does not reprint them, so the archived record is
part of this assessment. Retirement preserves that source; it does not close
its open findings. Every anchor this revision
takes is at upstream `22f0b46` and at our `5beacf5` (2026-11-07). New local
anchors name the file, and the line numbers are hints.

The verification pass also carries unfinished earlier work into this file:
finding 3's prospective test guidance; finding 8's two small considerations;
the post-adoption follow-ups to findings 9–11; and finding 17's uncompleted
writing-skills guide rewrite and compaction probe. Recommendations below are
assessment content, not instructions to implement them in this audit.

Two things are new in kind. Findings 19–24 are the six pushbacks a review of
upstream's spec-driven workflow (brainstorming → writing-plans → subagent-driven-
development or executing-plans) made on 2026-11-07, read against v7.0.2 and
against our tree, so each one records where we already differ. Findings 25–33
extend that review to the other nine shared skills, which earlier passes had only
diffed. Where one of these finds a gap on our side, it is a local design item
and says so; it is not an upstream claim to port.

The 2026-10-28 revision brought the document to v7.0.1 for every skill except
brainstorming; plan 70 (2026-10-28) re-baselined finding 4 to v7.0.1 (`2ce8aa1`)
when it adopted that finding. The 2026-10-18 revision brought it to v7.0.0, the
2026-10-03 revision to v6.4.2, and the first pass (2026-09-03, against v6.3.0)
lived at `specs/superpowers-drift-2026-09-03.md` until the 2026-10-03 revision
renamed it. A re-anchor on 2026-10-31 re-took the local anchors of findings 7,
11, 12 and 13 after plans 71–73.

Finding numbers never change, because other documents cite them (`NOTICE`,
`specs/completed/sdd-hardening.md`, `specs/completed/handoff-briefs.md`,
`specs/completed/audit-3-10-26.md`). Findings 1–8 are the first pass's, 9–15
came from v6.4.x, 16 came from v7.0.0, 17 from v7.0.1, 18 from v7.0.2, and 19–33
from the 2026-11-07 workflow review.

## Scope and method

| | |
|---|---|
| Vendored baseline | `896224c` (v6.0.3, 2026-06-18), per `NOTICE` |
| Adoption baselines | Unchanged from the 2026-10-28 revision: `b36e082` (v6.3.0) for plan 22; `8ca22db` (v6.4.2) for plan 40; per-fix commits for plan 50; `bb92a77` (v7.0.0) for plan 60's idea; `2ce8aa1` (v7.0.1) for plans 70, 71, 72 and 75. Nothing was adopted in this revision. Added by plan 82 (2026-11-09): `22f0b46` (v7.0.2) |
| Previous review | `2ce8aa1` (v7.0.1, 2026-10-21), reviewed 2026-10-28, re-anchored 2026-10-31 |
| Upstream HEAD | `22f0b46` (v7.0.2, 2026-11-03), still `main` on 2026-11-07 |
| Our tree | `5beacf5` (2026-11-07). Its unversioned assessment is byte-identical to the v7.0.1 copy before archival annotations; the v7.0.2 file was added later, in `44554e1` |
| Commits since previous review | 1 on `main`: the release squash merge `22f0b46` (#2657). On upstream's `dev` branch the skill-relevant pull requests merged on 2026-11-02. Their change commits, excluding shared bases of stacked PRs, are: #2644 (`e8cc5c9`), #2654 (`4eb73b6`), #2604 (`f75c01f`, `750ba92`), #2605 (`3735a50`), #2606 (`614d80c`, `de67241`, `0d61007`, `8b0eefc`), #2607 (`6ab1c79`, `74500c1`, `402cfde`), #2602 (`bb3a5aa`), #2608 (`fa50d83`), #2609 (`f713233`) |
| Files changed under `skills/` since previous review | 19 (+282 / −411). Without brainstorming's `SKILL.md`: 18 (+222 / −373). Five of the 19 are systematic-debugging files that moved out to `tests/` (−328), so the live change to skill text and scripts is 14 files, +282 / −83 |
| Unreleased skill work | None: on 2026-11-07 `dev` (`df2e996`, the merge of `main` back into `dev`) has the same tree as `22f0b46`, byte for byte |
| Next review starts from | `22f0b46` |

Comparison is **per behavioral claim, not per diff hunk**. `NOTICE` records that
most vendored files came in byte-identical to `896224c`. Local changes since
then mean a mechanical three-way merge still produces noise. Each upstream
RELEASE-NOTES entry was instead read as a claim and checked against our tree:
*does our copy already satisfy the intent?* v6.4.1, v6.4.2, v7.0.0, v7.0.1 and
v7.0.2 each landed as one squash commit, so commit counts say nothing about
scope. The claim units are the release notes' pull-request numbers
(obra/superpowers pull requests, written #NNNN below), and the commits a pull
request brought to `dev` are cited where a port would start from the diff.
Where a claim is about script behavior, a probe in a scratch repository
decided it rather than a reading; this revision's probes ran on 2026-11-07
against our scripts at `5beacf5`.

That distinction is load-bearing. Upstream's `0b47219` (2026-07-05) fixes a
worktree path recomputed after `cd`, which made cleanup silently no-op. It
landed after our vendoring, so a diff-driven read flags us as behind. We are
not: `finishing-a-development-branch/SKILL.md` carries an equivalent guard
("Do NOT re-run detection here"). **Already covered.** The file came in
byte-identical at the vendoring, so we added the guard ourselves (`46423d5`).
This revision has the same shape of case: #2608's `start-server.sh` fix landed
upstream on 2026-11-03 and here on 2026-11-01 (finding 8).

### Shared skills at v7.0.2

Thirteen skills exist on both sides. Upstream's other two,
`diagnosing-superpowers` (finding 15) and `using-superpowers` (dropped here),
are not shared. The table measures the drift two ways: what upstream changed
in the release, and what we changed since the last re-anchor. Sizes are the
whole `SKILL.md` file in bytes, which is the unit of upstream's size test
(finding 17).

| Skill | Upstream v7.0.1 → v7.0.2 | Our commits since 2026-10-31 | `SKILL.md` bytes, upstream / ours | Where it stands |
|---|---|---|---|---|
| brainstorming | 2 files, +67 / −38: the #2644 retune and `start-server.sh` | 3: `3ad94f8` (start-server), `caeba8f` (neighbor-skill wiring), `1f64a61` (derive-roadmap route, plan 78) | 15,190 / 18,764 | #2644 open under finding 4; #2608 already covered |
| dispatching-parallel-agents | unchanged | 1: `226ab9f` | 6,078 / 7,324 | finding 26 |
| executing-plans | 3 files, +16 / −7: #2607 wording, `task-start` and `task-done` | 8, all plan 75's port (`06e5a96`, `da62ab4`, …) and its loose ends through `686ffd7` | 18,364 / 16,946 | finding 11 adopted; v7.0.2's items under finding 18 |
| finishing-a-development-branch | unchanged | 2: `e544b1e`, `34cec3e` (Declined lines at Step 4b) | 7,781 / 20,741 | finding 8 unchanged; finding 28 |
| receiving-code-review | unchanged | 1: `9c630f9` | 6,203 / 6,550 | finding 27 |
| requesting-code-review | unchanged | 1: `e544b1e` | 2,974 / 6,004 | finding 25 |
| subagent-driven-development | 9 files, +199 / −38: `sdd-repo` (new), `sdd-workspace`, `task-brief`, `review-package`, five prose files | 6: plan 75's five stops (`b6dc9fb`, `1cd8824`), `28031e4`, `9700063`, `cc458b1` | 19,740 / 20,253 | finding 18 |
| systematic-debugging | 5 files, +0 / −328: dev files moved out (#2654) | 2: `98c453e` (find-polluter exit 2), `457fdbe` | 9,530 / 10,390 | #2654 already covered; finding 30 |
| test-driven-development | unchanged | 3: `39ddf96` (plan 75, finding 13), `8fa5b70`, `988ae8f` | 9,578 / 10,881 | findings 3, 13 stand; finding 32 |
| using-git-worktrees | unchanged | 1: `169942a` (slash check, uv before poetry) | 6,813 / 10,184 | finding 29 |
| verification-before-completion | unchanged | 1: `226ab9f` | 3,646 / 4,075 | finding 31 |
| writing-plans | unchanged | 2: `114e233`, `6e220b5` | 10,335 / 20,845 | findings 9, 10 adopted; finding 17 (size) |
| writing-skills | unchanged | 1: `f7a452f` | 16,738 / 18,790 | finding 17 adopted (plan 72); finding 33 |

Nine of the thirteen are unchanged upstream since v7.0.1, so every upstream
anchor the 2026-10-28 revision took for them still stands. Ours moved in all
thirteen since 2026-10-31, most by plan 75 and by one-line fixes; the local
anchors this revision cites were re-taken at `5beacf5`.

## Status of earlier findings

| # | Finding | Status at 2026-11-07 |
|---|---|---|
| 1 | SDD workspace has no plan identity | **Adopted** — plan 22 |
| 2 | Implementers can spawn duplicate reviewers | **Adopted** — plan 22 |
| 3 | TDD reference has no falsifiability discipline | Open, prospective only; upstream unchanged at v7.0.2 |
| 4 | Brainstorming ceremony does not scale | **Adopted** — plan 70, rebased on v7.0.1 (`2ce8aa1`). v7.0.2's retune (#2644) is **open**, a port candidate; see the finding |
| 5 | Every task gets its own dispatch | **Adopted** — plan 22 |
| 6 | SDD review loop has no round cap | **Adopted** — plan 22, with a deliberate ladder divergence |
| 7 | Pre-flight conflicts stall for a human | **Adopted** — plan 75, rulings mid-run only (F7); decided 2026-10-21 |
| 8 | Smaller items | `find-polluter.sh` **fixed** — plan 50, hardened again `98c453e`; the untracked-file guard **adopted** as an idea — plan 60; `start-server.sh --project-dir` **already covered** (`3ad94f8`, 2026-11-01, two days before #2608 shipped); the discard menu and the worktree-guard format stay as they were |
| 9 | writing-plans asks for code transcripts | **Adopted** — plan 73 |
| 10 | Reviewers grade the spec's silence | **Adopted** — plan 73 |
| 11 | executing-plans was rebuilt as a ledgered native mode | **Adopted** — plan 75 (2026-10-31), from v7.0.1. v7.0.2's `task-start` guard and #2607 wording landed under finding 18 in plan 82 (2026-11-09) |
| 12 | SDD script hardening | Range guards and the create-only `.gitignore` **adopted** — plan 50; the basename collision stays decided (M2). v7.0.2's helper fixes are finding 18, not this one, and they landed there in plan 82 (2026-11-09) |
| 13 | TDD does not say what "other tests" means | **Adopted** — plan 75 |
| 14 | Nested controller on Claude Code | Not adopted; premise narrowed to non-fork subagents |
| 15 | diagnosing-superpowers | Not adopted. v7.0.2 did not touch it |
| 16 | Two v7.0.0 bug fixes apply to our copies as they stand | **Adopted** — plan 50 |
| 17 | Skill bodies run past the compaction re-attach cut | SDD and writing-skills splits **done** — plans 71, 72; the writing-skills guide rewrite remains open. Sizes re-taken 2026-11-07: three of our files fail upstream's byte bar, all pass ours, writing-plans by 6 characters. The byte bar stays not adopted until the probe |
| 18 | v7.0.2 helper hardening: repository, task IDs, fences, invocation | **New.** One local defect by probe (`task-start` in a repo with no commit); two shared gaps by probe (#2604, #2605); invocation wording partly covered. **Adopted** — plan 82 (2026-11-09), except `-C DIR`, which was not taken |
| 19 | The autonomy dial is set hard | **New**, workflow. Decided by finding 7; we keep a wider human loop; record only |
| 20 | No durable record of what wasn't built | **New**, workflow. **Already covered** by the plan-completion protocol; the upstreamable core is three rules |
| 21 | Per-task test evidence is self-reported in SDD | **New**, workflow. Gap on both sides; a local design item that the tester-seat work also needs |
| 22 | Spec drift is unaddressed | **New**, workflow. Partly covered by the `## Decisions` log and amendment tasks; a local design item for mid-run rulings |
| 23 | "Tasks mostly independent" is stated for both executors | **New**, workflow. **Already covered**: our executing-plans routes coupled plans inline |
| 24 | Planner-authored tests can share a spec misreading | **New**, workflow. Closed with no build (plan 83, owner decision D8, 2026-11-09). Layer 4 of its backlog item stays open in `specs/deferred_items.md` |
| 25 | requesting-code-review still leads with `HEAD~1` | **New.** **Already covered**; record |
| 26 | dispatching-parallel-agents dispatches without a model or a worktree | **New.** Model half **already covered** (skill text and `hooks/dispatch-model-guard.py`); the shared-working-tree half is a gap on both sides, low |
| 27 | receiving-code-review treats every reviewer as a person | **New.** Partly covered (`9c630f9`); the stall on a partner-decision conflict and the `gh api` line stand on both sides |
| 28 | finishing-a-development-branch guesses the test command and has no conflict path | **New.** Step 1 wording open on both sides; the backlog gate is ours alone. Step 1 wording **adopted** — plan 82 (2026-11-09); the merge-conflict path stays open |
| 29 | using-git-worktrees sets up Python projects wrongly and drops isolation silently | **New.** Setup half **already covered** (`169942a`); the sandbox fallback is a shared design choice |
| 30 | systematic-debugging's `find-polluter.sh` is still invoked by a relative path upstream | **New.** **Already covered** here (plan 50); upstream's #2607 test does not reach it |
| 31 | verification-before-completion lacks the documented-test-command pointer | **New.** Claim-specific command selection exists; the more explicit pointer is a wording proposal on both sides, low. **Adopted** — plan 82 (2026-11-09) |
| 32 | test-driven-development | **New.** Nothing new at v7.0.2; findings 3, 13 and 24 carry it |
| 33 | writing-skills says nothing about where test scenarios live | **New.** Record; a one-line placement rule on both sides, low |

## Dismissed without further review

The first-pass, v6.4.x, v7.0.0 and v7.0.1 paragraphs stand as the 2026-10-28
revision wrote them.

**v7.0.2.** Everything outside `skills/` except the SDD and executing-plans
tests, which finding 18 reads: the three hook fixes (#2592 Copilot PowerShell
form, #2593 no child processes on Git Bash, #2594 zsh fallback), which harden
upstream's bootstrap hooks that we don't ship; the Pi extension (#2595, #2598),
Hermes (#2596), OpenCode (#2597, #2600, #2601) and Muse (#2533) bootstrap
fixes; the Codex packaging scripts in linked worktrees (#2609); version bumps
in ten plugin manifests; `docs/porting-to-a-new-harness.md`,
`docs/windows/polyglot-hooks.md` and `docs/README.opencode.md`. The Windows
path fix in the helpers (#2602, `bb3a5aa`: `cygpath -m` on the printed
workspace path) goes with the earlier Windows work: it changes only what the
scripts print on Git Bash, MSYS2 and Cygwin, and the markers keep `pwd -P`'s
spelling, so it has no effect on a macOS install. The systematic-debugging
test files that #2654 moved to `tests/systematic-debugging/pressure-scenarios/` are
dismissed as files; the claim behind the move is under Already covered.
`proving-it-works-with-a-movie` still has not shipped.

**Already covered, no action:**

- **`start-server.sh --project-dir .` (#2524, #2608, `fa50d83`).** Upstream
  resolves a relative `--project-dir` to an absolute path, creating it if
  missing, before the script `cd`s into its own directory
  (`brainstorming/scripts/start-server.sh:117-123`). Ours has done the same
  since `3ad94f8` (2026-11-01): `start-server.sh:79-86` makes the directory,
  resolves it with `pwd -P`, and stops with a JSON error when it cannot.
  `test_start_server.py:32-40` starts a real server under a relative `proj`
  and checks the state file lands under `proj/.brainstorm`. `NOTICE` records
  the fix as this repository's own. Upstream's new
  `tests/brainstorm-server/start-server.test.sh` is the same case in bash.
- **systematic-debugging no longer installs its test scenarios (#2277,
  #2654, `4eb73b6`).** Upstream moved `CREATION-LOG.md` and four
  `test-*.md` pressure prompts out of the skill, because an agent that greps
  the installed directory mid-task can find "This is a real scenario. You
  must choose and act" and take it as live instructions. Our
  `skills/systematic-debugging/` never held those files: `find skills -name
  CREATION-LOG.md -o -name 'test-*.md'` returns nothing on 2026-11-07, and
  git history shows no commit that ever added them. Upstream's new
  `tests/skill-layout/test-no-dev-files-in-skills.sh` fails on exactly those
  two names. It would pass here as written, but the rule behind it
  ("files meant for developing the skill don't ship") would not: 17 of our
  skills keep 26 `test_*.py` modules beside the scripts they test, by this
  repository's directory-scoped convention, and `install.py` installs them.
  Those files are pytest modules, not prompts, so the #2277 failure cannot
  happen through them. Deliberate divergence; not adopted as a test.
- **`brainstorming/visual-companion.md` and the companion server.** Re-checked
  each pass because an upstream change there could reintroduce the remote
  brand-image fetch and telemetry toggles `NOTICE` records removing. v7.0.2
  changed neither file. Its changes near the companion are test-only:
  `tests/brainstorm-server/server.test.js` (+13) and the new
  `start-server.test.sh`. No network call or telemetry toggle returns.
- **`LICENSE`.** Unchanged since the vendoring, and byte-identical to our
  `LICENSE-superpowers` (re-checked at v7.0.2 with `cmp`).
- **#2607 for the anchored half of our prose.** See finding 18.

## Findings 1–8 (first pass), re-verified

Findings 1, 2, 5, 6 and 7 stand as the 2026-10-28 revision wrote them;
v7.0.2 changed nothing they rest on.

### 3. TDD reference has no falsifiability discipline — open, prospective

The prospective port remains upstream's positive `writing-good-tests.md`
guidance: name the behavior that would break, exercise the real thing, and
check that tests can distinguish working behavior from a defect. Our
`testing-anti-patterns.md` still lacks the two named traps: **string-presence**
assertions that check source wording instead of behavior, and **change-detector**
assertions that fail on an implementation change without protecting a useful
outcome. The candidate includes gate functions, mutation checks and warning
signs. This is guidance to evaluate, not a claim that all source-text tests
are invalid or that existing suites need blanket replacement.

Retain our full **Why Order Matters** section unless a separately tested
compression preserves its behavior under pressure. Upstream's first deletion
regressed test-first behavior (reported control 8/10, treatment 5/10); its
eventual rewrite retained the rebuttals in rationalization rows. Findings 13
and 24 do not close this prospective item. The archived finding 3 holds the
historical evidence; its assurance about the then-existing test suites is not
a fresh audit of today's suites.

### 4. Brainstorming ceremony does not scale — adopted (plan 70), rebased on v7.0.1; v7.0.2's retune open

**Adopted by plan 70 (2026-10-28).** `skills/brainstorming/SKILL.md` follows
upstream v7.0.1 (`2ce8aa1`). `NOTICE` names what was taken and each deliberate
divergence. The behavior record is
`specs/baseline/red-baseline-brainstorming-2026-10-28.md`. Since then plan 78 added the
derive-roadmap route for a new multi-stage project (`SKILL.md:50-52`, `1f64a61`)
and `caeba8f` wired the creative-thinking pointer into Lay out the approaches
(`:165-166`). The 2026-10-28 text of this finding, from "Before plan 70" through
"What plan 70 took, and where it diverges", stands.

**Upstream at v7.0.2 (#2644, `e8cc5c9`): questions earn their place.** The
release retunes the retune. Read against our file, which still carries every
v7.0.1 phrase that v7.0.2 replaced, the change has seven parts:

- **A question only when the answer would change what gets built** and
  neither the request nor the project answers it. Otherwise the skill states
  its call and its reason as a proposal the partner can correct, and moves on.
  Process steps are always its own calls: writing things up, where files go,
  looking further, how to show something (upstream `SKILL.md:98-106`). Ours
  still says "Each message ends with one question" (`:105-111`).
- **Why first, openly.** When the partner has not said why they want it, even
  if the skill can guess, that is the first question, in their terms, with
  nothing to pick from (upstream `:63-77`, `:112-116`). Ours asks "the thing
  their request leaves open whose answer would most change what gets built"
  (`:78-79`), which may be a how question.
- **Options with a recommendation once the why is known.** When a decision has
  choices the skill can name, it sketches each concretely, with what it trades
  off and which it would pick (upstream `:114-116`, `:154-166`). This is the
  half plan 70 already anticipated: our Get them describing ends "A choice
  among known alternatives is different: for the approach pick, a size
  override, or a named decision, give the options with your recommendation"
  (`:121-123`), and the Options steer Red Flags row says so (`:349`).
  Upstream's version is broader, since any named decision qualifies once the
  why is in hand, and it is measured (below).
- **Reading the register.** Someone who raises the how or asks about
  trade-offs wants the options with a pick; someone who talks about outcomes
  is handing the how over, and the skill makes those calls and states each in
  a line (upstream `:118-127`). Ours keeps v7.0.1's "Find out early which of
  those choices they want to make" (`:127-131`), which is a question.
- **A short design in the first message when nothing is open.** For a detailed
  request with one sensible way, the first message ends with the approach, a
  line on why the others don't fit, the design in a few lines, and an approval
  ask; approval covers both, and steps 1 to 3 of the ordered list happen in
  that message (upstream `:31-34`, `:71-77`, Red Flags `:291`). Ours has no
  such path: the ordered list at `:36-44` always runs Lay out the approaches
  as its own message.
- **Do recon, show in text.** "Offer recon" becomes "Do recon": the skill goes
  and looks, then says what it looked for and found (upstream `:149-152`).
  "Show, don't tell" first sketches in text and offers the visual companion
  only when the look itself is the partner's to decide (`:168-170`,
  `:200-207`). Ours offers both (`:156-159`, `:173-174`). Where the design
  goes outside a software repo, upstream now picks a sensible place and says
  where, rather than asking (`:244-247`); ours asks (`:288`).
- **Never reopen what they've already decided** joins Look Before You Ask
  (upstream `:46-49`). Ours does not say it (`:54-61`).

**The upstream-reported measured bar (#2644).** Blind-graded conversations on the same scenarios:
filler questions fell from 41 with v7.0.1 to 23; the reason behind the request
came out before any approach in 33 of 33 conversations (28 of 33 on v7.0.1);
nothing got built before approval (4 times on v7.0.1). Against v6.4.2's
brainstorming, 23 filler questions against 34, the why drawn out in 33 of 33
against 19 of 33, building-before-approval matched. In the Ctrl+K scenario,
where a spec gives one shortcut to two features, v7.0.1 found the conflict
every time but asked a bare "which one?" in 8 of 8 runs; v7.0.2 laid out the
options and recommended one in 8 of 8. The scenarios are in
`prime-radiant-inc/superpowers-evals`, which has no license, so this repository
cites them by name only.

**How a port lands here.** The text to take is #2644's diff against our
v7.0.1-derived copy, hunk by hunk, with plan 70's thirteen divergences held:
the `Use when…` description, the `specs/` lifecycle and fresh-session handoff
(upstream's new "write the short design doc as approved and go on to the plan"
becomes "approve in chat and build in this session" for a small change), the
no-skip-offer for routed work (`:93-94`), the quick-task exit, spikes off the
branch, the `model: opus` builder check and the token-cost warning. The
options-with-a-pick change replaces plan 70's narrower sentence and its Red
Flags row with upstream's wider rule, and the plan-70 pressure row about guess
lists before the first question (`:106-108`) has to be reconciled with
upstream's "sketch each concretely": the two agree once the why is known and
disagree before it, which is exactly the line upstream draws. This is a
behavior-shaping change to a discipline skill, so writing-skills' micro-test
and pressure test apply; plan 70's RED baseline is the control, and its
question-style cases re-run (T7, the first-question case, decided under a
letter reading on 2026-10-28, is the one most likely to move). That original
GREEN result is not the latest evidence: the isolated 2026-11-05 rerun scored
T7 13/25 against an 80% bar, with no measured wording effect (52% after,
48% before). On 2026-11-06 the owner accepted that known gap and kept D17's
letter reading; see `specs/baseline/red-baseline-brainstorming-2026-10-28.md`,
"Re-run with the isolated kit" and "Owner ruling (2026-11-06)". Reuse the
isolated kit and this result rather than treating the original pass as current.
The reported nine-default tester-seat handoff has no artifact path here, so
its claimed question-round-trip saving is a hypothesis, not measured evidence.

### 8. Smaller items

The 2026-10-28 text stands, with these updates and retained considerations:

- **`find-polluter.sh`** was hardened again on 2026-11-01 (`98c453e`): it exits
  2, with a message that is not an all-clear, when the test command cannot
  start (exit 126 or 127), and it reads the file list line by line (`NOTICE`).
  Upstream's copy is unchanged at v7.0.2, and its invocation is finding 30.
- **`start-server.sh --project-dir`** is under Already covered: our fix
  (`3ad94f8`, 2026-11-01) preceded upstream's release of the same fix (#2608,
  2026-11-03) by two days.
- **Discard menu placement remains an open consideration.** Both local
  completion menus still advertise "Discard this work"
  (`finishing-a-development-branch/SKILL.md:182`, `:194`). The earlier
  recommendation was to make discard explicit-request-only, as upstream did.
  Typed confirmation already protects the operation; the unresolved question
  is whether the menus should offer it. No change is adopted by this audit.
- **Worktree-guard format remains optional convergence.** Our guard uses
  Problem/Fix prose (`using-git-worktrees/SKILL.md:205-220`); the earlier
  suggestion was the house Excuse/Reality table. No behavioral gap was
  established, so this is a format consideration, not an implementation defect.

Those two local considerations remain unresolved; the `gh`-optional PR path
already covers the earlier forge-agnostic recommendation.

## Findings 9–15 (v6.4.1 and v6.4.2), re-verified

Findings 9, 10, 12, 13 and 14 stand as the 2026-10-28 revision wrote them.

**Adoption is not closure of the follow-ups.** Findings 9 and 10's mechanism
landed in plan 73, but the earlier record also carried its unmet R2 and
R4-task micro-test bars and the unresolved review findings. The existing
`specs/deferred_items.md` section `73-reviewer-and-planning-contract` owns
the remaining test-only/delete-pass check, completion-gate handling of
Declined lines, Review Focus explanation, Full Form test coverage, kit and
wording observations, and **Watch the Proportion check**. The last item asks
whether cutting plans to about five times the spec removes needed work; its
F1 comparison had a ceiling and did not settle that risk. Keep those backlog
items rather than marking the whole adopted finding unfinished again.

### 11. executing-plans was rebuilt as a ledgered native mode — adopted (plan 75); v7.0.2 items under finding 18

**Adopted by plan 75 (2026-10-31)** from v7.0.1, as recorded in the 2026-10-28
text: `skills/executing-plans/SKILL.md`, `references/final-review.md`,
`scripts/task-start`, `task-done` and their test, with `install.py`,
`build/suites.toml` and `NOTICE` changes; behavior record
`specs/baseline/red-baseline-executing-plans-port.md`. Since the port: `686ffd7`
anchored the workspace script and counts batched tasks, `2b15ba0` and
`e432a73` fixed `task-done`'s ledger match through symlinks, and `05135af`
settled one `task-done` command, the Codex line and the literal workspace path.

v7.0.2 changed three executing-plans files. `task-start` and `task-done` now
read BASE and HEAD in the repository `sdd-repo --with-commit` names, and stop
with exit 2 when there is none or it has no commit (upstream
`scripts/task-start:23-29`, `task-done:23-26`). `SKILL.md` says to run the
three helpers by absolute path from the working tree (`:125-127`, `:173-174`,
`:226-227`, `:238-239`). Both are finding 18's; one of them is a local defect
our port carried from v7.0.1.

Plan 75's remaining review and test caveats are still owned by the existing
backlog sections `75-executing-plans-port` and `76-whole-repo-review-fixes`
(including reworded-gate coverage, strict S1/G1 scoring, resume wording,
basename/empty-ledger assumptions, Bash 3.2 coverage and the stop-list scope).
The v7.0.2 helper fixes do not automatically close those older follow-ups.

### 15. diagnosing-superpowers — not adopted

v7.0.2 did not touch the skill. The disposition does not change.

## New findings (v7.0.0 and v7.0.1)

Findings 16 and 17 stand as the 2026-10-28 revision wrote them, with the
following update to 17.

### 17. Skill bodies run past the compaction re-attach cut — sizes re-taken

Plans 71 and 72 did the two moves. **Sizes, 2026-11-07,** by the same byte
measure as the 2026-10-28 probe (`wc -c` on the whole file), with body characters
recounted using `build/check_conformance.py`'s exact `skill_body` extraction:

| Skill | Bytes | Body characters | Upstream's bar (≥ 20,000 bytes fails) | Our check (> 20,000 body characters fails) |
|---|---|---|---|---|
| writing-plans | 20,845 | 19,994 | fails | passes, 6 characters inside |
| finishing-a-development-branch | 20,741 | 19,924 | fails | passes, 76 inside (19,970 on 2026-10-28) |
| subagent-driven-development | 20,253 | 19,409 | fails | passes (30,268 before plan 71) |
| bayesian-workflow | 19,917 | 18,667 | passes | passes (35,223 before plan 71) |
| writing-skills | 18,790 | 18,012 | passes | passes (29,717 before plan 72) |
| brainstorming | 18,764 | 18,120 | passes | passes |
| executing-plans | 16,946 | 16,384 | passes | passes |

Three findings follow. The two moves worked: `bayesian-workflow` lost 16,556
body characters and `writing-skills` 11,705, and exceptions
`skill-body-past-compaction` and `writing-skills-late-critical-headings` are
gone. **writing-plans is new to the list.** It was not among the four files the
2026-10-28 probe named; plan 73's Review Focus section and the completion
protocol's growth since (`fdf9f47`, `6e220b5`) brought it to 6 characters
inside our window, so a net addition of 7 body characters fails that check. The
2026-10-28 text's observation about finishing-a-development-branch applies to
it now. **Where the two bars disagree, they disagree more.** On 2026-10-28 one
file passed ours and failed upstream's; now three do. The probe item in
`specs/deferred_items.md` (section `superpowers-drift-v7.0.1`) still decides
the measure, and the owner's 2026-10-28 decision not to adopt the stricter bar
until it runs stands. A `references/` split of writing-plans, on the pattern
of plans 71 and 72, is the next move whichever bar wins, and it would also
answer the local design items under findings 21 and 22 if those add text.

The original review's approximate loop undercounted writing-plans by four
characters. The verification pass uses the lint's frontmatter boundary
(`^---\n(.*?)\n---\n`, DOTALL), so the body-character column now gives the
exact count used by that check. The byte gate and body-character gate remain
different measures; neither establishes how the runtime actually truncates.

**The compaction-cut probe remains unfinished.** The existing open item in
`specs/deferred_items.md`, section `superpowers-drift-v7.0.1`, asks whether
the actual cut counts characters or tokens and includes frontmatter or a
runtime-added header. Done when a forced-compaction probe records the
boundary and the register and guide agree with it. The earlier sequencing
blocker, plan 69, is complete; the probe itself has not been implemented.

**The writing-skills split did not complete its guide rewrite.** The open
item **Split and rewrite writing-skills against the guide**, in backlog
section `53-agent-skills-portability`, retains the work the archived finding
17 explicitly excluded from the split:

- Resolve `writing-skills-guide-gaps` in `build/cc_guide/conformance.toml`:
  listing budget, critical rules first and `@` loading.
- Revisit the recorded `writing-skills-tdd-for-docs` deviation; a renewed
  owner decision may reaffirm it rather than remove the discipline.
- Verify or drop the unsupported **Why no @ links** claim that `@` links
  immediately force-load files and consume large amounts of context
  (`skills/writing-skills/references/discovery.md:200-202`).
- Update the skill's Directory Structure and File Organization examples,
  which still omit the `references/` layout that plan 72 installed.

The body split, WARN removal, late-heading exception removal and associated
test updates are done. The guide gaps and deviation remain in the register,
so retiring v7.0.1 must not remove this residual design item from the backlog.

## New finding (v7.0.2)

v7.0.2's main change, the brainstorming retune (#2644), is finding 4's and is
open there. Its `start-server.sh` and systematic-debugging items are under
Already covered. One finding is new.

### 18. v7.0.2 helper hardening: repository, task IDs, fences, invocation

Five pull requests harden the five helper scripts and the prose that invokes
them. Four of them are about the same scripts plan 22 and plan 75 touched, so
each is judged separately, by probe where it is about behavior. Upstream's new
test coverage is `tests/claude-code/test-sdd-workspace.sh` (sections at
`:165`, `:277`, `:310`, `:508`, `:603`, `:655`),
`tests/claude-code/test-executing-plans-scripts.sh` (+76), and the two new
suites `tests/sdd-helper-paths/` and `tests/skill-layout/`.

**Which repository (#2606, `614d80c`, `de67241`, `0d61007`, `8b0eefc`) — partly
covered, with one local defect.** Upstream added `scripts/sdd-repo` (54 lines),
the single source of which working tree the helpers act on: the current
directory's, exactly as `git` picks it, never one guessed from the plan file's
path. Outside any working tree it stops with exit 2 and a two-line message
("SDD scripts must run from inside the git working tree you're executing in,
with at least one commit … If this is a new project, run 'git init' and make a
first commit, then rerun", then git's own first line). `--with-commit` also
stops on a repository with no commit, for the callers that need HEAD:
`review-package`, `task-start` and `task-done` call it that way, and every
`git` in those three now runs as `git -C "$repo"`. Every helper takes `-C DIR`
before its arguments and `cd`s there first, so a controller can review a
worktree without a `cd DIR ;` prefix that Claude Code cannot allowlist (#1799).
The v7.0.1 bug was in `sdd-workspace`'s `root=$(CDPATH='' cd -- "$(git
rev-parse --show-toplevel)" && pwd -P)`: outside a repository the inner
substitution fails, `cd -- ""` succeeds, and the workspace landed in the
caller's directory, often the plugin cache.

Probe, 2026-11-07, our scripts:

- `sdd-workspace ids.md` in a directory with no repository: git's bare
  `fatal: not a git repository`, exit 128, nothing written. Our `:43` is the
  plain `root=$(git rev-parse --show-toplevel)`, so `set -e` stops the script
  on the substitution. **We never had the v7.0.1 bug**, but there is no
  message that says what to do, and `task-brief`'s and `review-package`'s
  callers see the same bare `fatal:`.
- `sdd-workspace -C <dir> ids.md`: usage error, exit 2. No helper here takes
  `-C`.
- In a fresh `git init` with no commit: `sdd-workspace` works (it needs no
  commit, correctly). `review-package ids.md HEAD HEAD` stops with `bad BASE:
  HEAD`, exit 2 (`:22`), which is right. **`task-start ids.md 7` wrote the
  brief, printed `base: HEAD`, and exited 0.** Its last line is `echo "base:
  $(git rev-parse HEAD)"` (`scripts/task-start:30`): with no commit, `git
  rev-parse HEAD` prints the literal `HEAD` to stdout and its error to stderr,
  and `echo`'s exit status is what `set -e` sees. An inline execution in a new
  project therefore starts its first task with the string `HEAD` as BASE,
  despite git's fatal diagnostic on stderr; it does not stop or give an
  actionable new-project message. `task-done` then refuses it at its own `:30`,
  after the task is built. Upstream's `task-start:23-29` cannot do this: BASE is `base=$(git -C
  "$repo" rev-parse --verify HEAD)` as an assignment, behind
  `sdd-repo --with-commit`. `test_executing_plans_scripts.py:104`
  (`test_task_start_prints_head_as_base`) runs in a repository with a commit,
  so no test here covers the empty one. This is the one item in the release
  that is a defect in our tree rather than a hardening we lack.

The `-C DIR` half is a harness-allowlist convenience for a controller that
stays in the main checkout while reviewing a worktree. Our controller `cd`s
into the worktree at using-git-worktrees' Step 1b (`SKILL.md:118-119`), and
plan 75's port keeps the workspace path literal in every command (`9700063`),
so no local text needs it. Low. The exit-2 message is the useful half.

**Task IDs (#2604, `f75c01f`, `750ba92`) — verified gap, shared with v7.0.1.**
Upstream's `task-brief` now reads a task heading as `Task` followed by an ID of
letters and digits, dot-separated, with at least one digit (`3`, `6b`, `A1`,
`2.1`), compares the ID to `TASK_NUMBER` as a whole string, never lets
`TASK_NUMBER` reach awk as a regex, keeps a deeper `Task 7a` inside `Task 7`'s
brief as a sub-task, and, when a plan has no `Task` headings at all, lists the
headings shaped like tasks before the not-found error, because such a plan
usually translated the word (`scripts/task-brief:33-100`). Probe, our
`task-brief:43-44`, on a plan with Tasks 2, 2.1, 6, 6b, A1 and 7:

- Task 2's brief carried Task 2.1's heading and body; Task 6's carried Task
  6b's. The match is `"Task[ \t]+" n "([^0-9]|$)"`, so `6` matches `6b` and
  `2` matches `2.1`, and the section-end rule at `:47-49` does not help,
  because the sub-task heading re-enters the match at `:44` before it can end
  the section.
- `6b` and `2.1` alone work. `A1` is not found (exit 3): the heading pattern at
  `:43` wants a digit first.
- The ID is a regex: `task-brief ids.md '6.'` matched Task 6 and took 6b with
  it.
- A plan whose headings read `### Tarea 1` reports `task 1 not found`, exit 3,
  and nothing more.

`test_sdd_scripts.py` has no case for any of these. Our plans number tasks
with integers, which is why the first three never bit; the regex injection
and the sub-task capture are the two that can bite a plan written by hand.

**An unclosed fence (#2605, `3735a50`) — verified gap.** Upstream's awk tracks
whether a fence opened inside the captured task hides a later `Task` heading.
When it does, the brief would run through every later task, so the script
refuses with exit 4 and names the line where the fence opened; when the fence
hides the requested heading itself, it says so before the not-found error; a
stray fence that hides nothing warns and writes the brief. The reporter's
177-line task had come back as a 1,159-line brief holding five tasks. Probe,
ours, on a plan whose Task 2 opens a ```` ``` ```` block that never closes,
followed by Tasks 3 and 4: Task 2's brief was 15 lines holding all three
headings, exit 0, no warning; `task-brief plan.md 3` reported `task 3 not
found`, exit 3, with no mention of the fence. Our fence tracker counts
backticks (`:32-42`), which is a different and CommonMark-correct fix for a
different problem (a ```` ```` ```` block that legally contains ```` ``` ````
lines, covered by `test_task_brief_keeps_a_fenced_task_heading_as_content`);
it does nothing for a fence that never closes. The two fixes compose: keep the
count, add the hidden-heading check and the exit-4 refusal.

**Invocation by absolute path (#2607, `6ab1c79`, `74500c1`, `402cfde`) — partly
covered.** Upstream's prose said to run the helpers "from this skill's
directory", agents `cd`'d there, and the helpers ran against the plugin's own
files (#2429). Every invocation now reads "by its absolute path, from the
working tree you're executing in", and `tests/sdd-helper-paths/test-sdd-helper-paths.sh`
fails any `scripts/<helper>` reference under `skills/` that lacks the phrase
within two lines. Our text never said "from this skill's directory": `NOTICE`'s
bundled-script-path entry (`47dc45c`) replaced the four runnable calls that
descended from that text with the `<this-skill-dir>/scripts/…` anchor, which
resolves to the absolute skill path and runs from the repository root. Five
invocations carry it today (`subagent-driven-development/SKILL.md:55`, `:177`,
`:262`; `references/final-review.md:48`; `executing-plans/SKILL.md:139`). Ten
do not: `executing-plans/SKILL.md:205` and `:259` ("this skill's
`scripts/task-start`", "`scripts/task-done`"), `references/file-handoffs.md:10`
and `:21`, `references/batching.md:13` and `:22`, `task-reviewer-prompt.md:306`
and `:319`, `re-review-prompt.md:56`, and the descriptive
`subagent-driven-development/SKILL.md:47` mention. `NOTICE` calls those "prose that only
names a script, or already calls it 'this skill's'", and left them; executing-plans'
two are runnable steps, added by plan 75 from v7.0.1 text. Nothing here says to
`cd` into the skill, and no incident has been seen, so the gap is the
consistency of the anchor rather than the bug. Upstream's test is the useful
part: a `build/` lint that every `scripts/<helper>` reference under `skills/`
carries the anchor or the phrase would hold the line that `47dc45c` drew.

**Disposition, per claim unit:**

- **`task-start` with no commit: fix directly, no spec**, as a defect. Guard
  HEAD with `--verify` as an assignment, stop with exit 2 and the new-project
  message, and add the empty-repository case to
  `test_executing_plans_scripts.py`. The same message in `sdd-workspace`'s
  no-repository path (and so in `task-brief` and `review-package`) is a
  two-line change that reaches every caller; `-C DIR` is optional and low.
- **#2604 and #2605: fix directly, no spec**, as script behavior with tests in
  our directory-scoped convention: the ID grammar, whole-string match, no
  regex, the shaped-headings hint, the hidden-heading refusal with exit 4 and
  the warning. Our Global Constraints prepend (`task-brief:58-78`) is
  untouched by either. The test cases are the probe above.
- **#2607: fix directly, no spec**, for the ten bare references, plus a lint.
  Prose only; the anchor is established text.
- **#2602: dismissed** (Windows).

**Done** (plan 82, 2026-11-09): `task-start` and `review-package` stop in a repository with no commit,
through a new `sdd-repo` guard (upstream #2606) that `sdd-workspace` also calls, with exit 2 and the
new-project message. `task-brief` reads task IDs whole and refuses a task that an unclosed fence runs
past, with exit 4 (#2604, #2605). The twelve bare helper references (this spec counted ten) carry the
`<this-skill-dir>/` anchor, and `build/check_helper_paths.py` is the thirteenth commit lint (#2607).
`-C DIR` was not taken.

**Reported session context, not independently verified:** the original author
reports an owner order from a 2026-11-07 review session: this drift pass, then
the brainstorm for the spec-derived tester seat, then its plan. No transcript
or handoff path accompanies that report in this repository. The proposed seat's plan
touches `task-brief` and a `task-done`-shaped helper for SDD (finding 21), so
the helper fixes land first or the two collide in our tree.

## Workflow findings (2026-11-07 review)

A review of upstream's spec-driven workflow at v7.0.2, made on 2026-11-07
independently of our tree, pushed back on six points. Each is recorded here
against both trees, because our repository's two stated differences from
upstream (a durable record of what was not built; a split between who writes
code and who writes tests) sit exactly on two of them. The verdict that framed
the pushbacks stands: the brainstorming rebuild and the context-economy
engineering in subagent-driven-development are the parts that matter most, and
every SDD rule cites a real failure in the release notes.

### 19. The autonomy dial is set hard

**Upstream.** "Rulings, not stalls. A running plan does not wait on a human"
(`subagent-driven-development/SKILL.md:19-21`); four things stop the run and
only these (`:27-30`; `executing-plans/SKILL.md:32-39`); "Let me check in before
the next task" is a Red Flags row (`executing-plans/SKILL.md:317`). The partner
sees the rulings once, at the end, in the final chat message
(`references/final-review.md:37-42`; `executing-plans/SKILL.md:296-300`). The
economics are sound when a parked session costs a human's day. The cost is
that a wrong ruling on a load-bearing interface propagates into every dependent
task before anyone reads it, and the rulings list is read after the branch is
built.

**Ours.** Finding 7's decision (2026-10-21, plan 75) keeps the pre-flight
batched question at launch and takes rulings mid-run only; the explicit scope
fence is a fifth stop (`executing-plans/SKILL.md:50-56`;
`subagent-driven-development/references/fix-loop.md:57-63`). Rulings do not
die with the final message: the resolve-before-defer gate reads them from the
ledger before the workspace is deleted (finding 20). The record of plan 78's
execution (2026-11-06) is the evidence on how the dial behaves in practice:
six `> Deviation:` and `> Skipped:` notes, one owner ruling recorded at the
Task 3 gate (`25d2834`), and two review findings parked for the owner
(`d5d9bd5`, `6cd77bc`). The human was pulled in several times anyway, which
is the right outcome and an argument that "four stops" undersells how often
a partner is in the loop.

**Disposition: decided; record.** No upstream action. Our wider loop is
deliberate and `NOTICE` records it under finding 7.

### 20. No durable record of what wasn't built — already covered

**Upstream.** Parked findings and deferred minors live in the ledger, which
`final-review.md:45-47` tells the controller to `rm -rf` once the branch is
clean; the "Rulings I made" and "Deferred minors" lists go into the final
message, which is ephemeral (`final-review.md:37-42`;
`executing-plans/SKILL.md:270-300`). Nothing in either executor ticks the plan
file or annotates a deviation in it. Git history records what shipped, not
what was decided against. Over several plans, the decisions not to build
something exist nowhere.

**Ours.** This is an established local mechanism, with one known gate omission
below. writing-plans' Plan Completion Protocol
(`skills/writing-plans/SKILL.md:286-316`): the resolve-before-defer gate
collects the leftovers (`:292`); each deviated step gets `> Deviation: …` and
each skipped one `> Skipped: <why> → deferred` (`:307-308`); a status line
points at `specs/deferred_items.md` (`:310`), where every deferral carries a
closure condition (`:316-355`). Both executors run the protocol before deleting
the workspace, and the gate reads the ledger, the unfixed findings and the
rulings first (`subagent-driven-development/references/final-review.md:29-33`,
`:45-46`, `:55`; `executing-plans/references/final-review.md:74-75`, `:85`,
`:92`). At the audited `5beacf5` baseline, the backlog is 144 open and 279
closed items in the live file, plus 106 closed items in the archive
(385 ever closed), a working
record rather than a graveyard. The review's one reservation is weight: three
scripts, markers, a commit lint, an archive migration and an aged-tail gate
that blocks merges (finding 28) is a lot of machinery around a protocol whose
core is three rules: tick and annotate the plan; file every deferral with a
closure condition; never delete the ledger before filing.

The existing plan 73 backlog item still records that the completion gate does
not explicitly list **Declined to judge** lines as leftovers. Both executors
send those lines to the partner, but the gate's wording has not been updated.
The protocol is present; that residual is not closed by finding 20.

**Disposition: already covered.** If any of it is ever sent upstream, send
the core.

### 21. Per-task test evidence is self-reported in SDD

**Upstream.** The task reviewer is told "Do Not Trust the Report" and, in the
same breath, "Do not re-run the suite to confirm their report"
(`task-reviewer-prompt.md:64-80`). The implementer's report is the test
evidence ("Reviewers will not re-run tests for you — your report is the test
evidence", `implementer-prompt.md:124-125`). The workflow does not require an
independent controller run of the task's tests; `SKILL.md:283` forbids asking
the reviewer to repeat the existing run, not the controller from checking.
The reviewer can inspect the diff and reported results, but a passed run is
not mechanically established at this gate. The mandatory mechanical gate is at branch finish
(finishing-a-development-branch Step 1) and, for inline execution, in
`task-done`, which writes the ledger line only when the command passes.

**Ours.** Identical at the execution level: `task-reviewer-prompt.md:141-153`,
`SKILL.md:226`. Our `task-done` exists for inline execution (plan 75) and
has no SDD analogue. The cheap fix is the one the review named: before
dispatching the task reviewer, the controller runs the brief's test command
through a `task-done`-shaped helper that writes the result beside the review
package, so the reviewer reads a run it did not have to trust. That is also
the mechanism the spec-derived tester seat (finding 24) needs to run its
tests, so the two are one design.

**Disposition: a local design item, not an upstream claim.** Log it in
`specs/deferred_items.md` beside the tester-seat item, and let the seat's
brainstorm size it. Upstream's `task-done` is the ready pattern; its
`--with-commit` guard (finding 18) is the version to copy.

### 22. Spec drift is unaddressed

**Upstream.** The spec is the binding authority and the plan its argument
(`SKILL.md:21`; `references/preflight.md:23-24`; `references/fix-loop.md:16`;
`executing-plans/SKILL.md:33`, `:161`), and a ruling that effectively amends
the spec never reaches it. Over several plans against a living codebase, the
committed design docs stop describing the system.

**Ours.** Partly covered. The plan's `## Decisions` log records each decision
with its source and where it was applied, and `Task N (spec amendment)` is one
of the places (`skills/writing-plans/SKILL.md:123-126`); a decision taken while
planning that contradicts the spec gets an amendment task with exact
replace-this-with-that blocks (`:238-243`). That covers decisions made before
execution. A mid-run `Ruling:` in the fix loop reaches the ledger and the
resolve-before-defer gate, which can file it as a deferred item, but nothing
routes a ruling that contradicts spec text into the spec. The gap is narrower
than upstream's and still open.

**Disposition: a local design item, low.** One line in the gate: a ruling that
contradicts spec text becomes a spec amendment or a deferred item with the
spec path as its closure condition. It can ride with the writing-plans split
that finding 17 now calls for.

### 23. "Tasks mostly independent" is stated for both executors — already covered

**Upstream.** Both executors state the same precondition
(`subagent-driven-development/SKILL.md:3`, `:38-47`; `executing-plans/SKILL.md:52`:
"Tasks are mostly independent — the same precondition as"). On paper that
excludes exactly the sequential pipelines research code tends to be (loader →
likelihood → sampler → diagnostics). In practice the Interfaces blocks carry
the coupling and it works; it is a documentation inconsistency, and the first
thing a statistician reading the when-to-use graph trips on.

**Ours.** The routing story `977a61a` already splits it: executing-plans is for
a plan "whose tasks are tightly coupled" (`executing-plans/SKILL.md:5-6`,
`:21`, `:60-62`), SDD keeps "mostly independent" (`:34`), and writing-plans'
handoff recommends one with a reason drawn from the plan (finding 11).

**Disposition: already covered; no action.**

### 24. Planner-authored tests can share a spec misreading

**Upstream.** Inside the workflow the planner has already written each test's
name and assertions (writing-plans, "What a Step Contains"; finding 9), and the
implementer transcribes them. That reduces the implementer's test-design
independence, but does not make TDD's RED step redundant: an assertion can
still pass before the change or fail for the wrong reason. The Iron Law
(`test-driven-development/SKILL.md:31-34`) checks that failure; it does not
establish that the assertion reflects the spec. A test and implementation can
therefore share the planner's misreading. Review Focus addresses spec silence,
and the whole-branch reviewer can also flag a bad plan or a misread requirement.
What neither workflow requires is a separate agent deriving execution tests
independently from the spec. That is the supported gap, not an inability of
existing reviewers to detect it.

**Ours.** The same, and already named: `specs/deferred_items.md`'s item
"Spec-reading test check" (recorded under findings 9 and 10). The 2026-11-07
review examined the repository's second stated difference, one agent writing
code and another writing tests, and found it is not in the tree: our
implementer prompt's step 2 is still "write tests", no tester agent exists in
`agents/` or `skills/`, and no commit in the history introduced one (`git log
-S` on test-writer and tester). The split exists only as planner-authored tests
in the plan, which both repositories have. Our final-review handoffs also pass
the spec path (`subagent-driven-development/references/final-review.md:17-22`;
`executing-plans/references/final-review.md:18-25`), so the final reviewer can
compare the implementation with the spec directly. A second execution-time
test-writer that sees the plan's test code buys independence from the
implementer but not from the planner, who is the party most likely to be
wrong. The version that earns its cost is a spec-derived tester seat: after
the implementer reports DONE, a subagent that has seen the spec and the
brief's Interfaces block but not the plan's test code writes additional
failing tests from the spec's requirements and Review Focus; the controller
runs them mechanically (finding 21's helper); failures enter the fix loop. A
handoff brief for the brainstorm, with nine defaults, was reportedly written
in that session on 2026-11-07. No artifact path or transcript is available here
to verify the handoff or whether that brainstorm has run.

**Disposition: closed with no build (plan 83, owner decision D8, 2026-11-09).** The
tester-seat brainstorm became `specs/spec-derived-acceptance-tests.md`. Its probe (plan 81,
`specs/baseline/red-baseline-acceptance-tests.md`) found that a fresh Self-Review caught all 15 planted
misreads, more than any test-writing arm. The redesign, `specs/completed/statement-level-readings.md`,
had two readers state what the spec asks. Its probe (plan 83, `specs/baseline/red-baseline-statement-readings.md`)
missed every catch bar and the false-alarm bar, with 4.4 to 11.0 false alarms per plan against a bar of
1.0. The backlog item "Spec-reading test check" is closed. Its layer 4, spec excerpts in the implementer
brief, stays open as an item in `specs/deferred_items.md` (`83-statement-level-readings — 2026-11-09`).
Finding 21's part goes to its own build plan from `specs/spec-derived-acceptance-tests.md`.

## Findings on the other shared skills (2026-11-07 review)

Nine shared skills were unchanged by v7.0.2 (table above). Earlier passes
diffed them; this one reads each as a reviewer of upstream's text would, and
records where our copy already departs. Items that are gaps on both sides are
local design items.

### 25. requesting-code-review still leads with `HEAD~1` — already covered

**Upstream.** The first thing the skill tells the agent to run is
`BASE_SHA=$(git rev-parse HEAD~1)  # or: git merge-base origin/main HEAD`
(`SKILL.md:28`), and the worked example derives BASE by grepping the log for
the words "Task 1" (`:55`). SDD's own text forbids `HEAD~1`, "which silently
drops all but the last commit of a multi-commit task" (`SKILL.md:243`), and
#2133 (v6.4.x) added `merge-base` only as the comment. The two skills
disagree, and the one a standalone session reads is the wrong one. The
standalone dispatch has no diff file: its placeholders are DESCRIPTION,
PLAN_OR_REQUIREMENTS, BASE_SHA and HEAD_SHA (`:36-40`), so the reviewer
re-derives the diff with git (`code-reviewer.md:29-30`), which SDD's review
package exists to avoid. "Note Minor issues for later" (`:45`) and the
reviewer's Minor tier (`code-reviewer.md:119`, `:183`) have no durable home:
finding 20 again.

**Ours.** All three are covered: BASE is the recorded one or
`git merge-base main HEAD`, and `HEAD~1` is forbidden in the same lines
(`SKILL.md:39-41`); `[DIFF_FILE]` is a placeholder, required when dispatched
from SDD (`:64`); the shared reviewer block has two grades and no Minor tier
(plan 73, finding 10), and the Codex second seat sits beside the final review
(`:25-28`, `:103`).

**Disposition: already covered; record.**

### 26. dispatching-parallel-agents dispatches without a model or a worktree

**Upstream.** Every dispatch in the skill is `Subagent (general-purpose):
"Fix …"` with no model (`SKILL.md:68-77`), while SDD's Model Selection says
"Always specify the model explicitly when dispatching a subagent"
(`subagent-driven-development/SKILL.md:160`). Three agents editing one
working tree at once is the skill's own example (`:66-85`), and its only
protection is a prose constraint ("Don't change other code", `:60-64`) and a
full-suite run afterwards (`:79-85`); nothing says to give each agent its own
worktree, and the no-nested-subagent rule (finding 2) is not restated for a
skill whose whole subject is dispatching. The skill is framed around test
failures throughout, though its description promises "2+ independent tasks".

**Ours.** The model half is covered twice: the skill sets a model per agent
(`SKILL.md:76-79`, `:84-89`), and `hooks/dispatch-model-guard.py` refuses a
dispatch without one. The worktree half is a gap on both sides: our copy says
nothing about isolating concurrent agents from each other, and using-git-worktrees
is written for one session, not three. `226ab9f` (2026-11-06) dropped two
narrative blocks that upstream had removed, so the files are closer than the
byte counts suggest.

**Disposition: a local design item, low.** One rule: agents that edit files
get disjoint file sets or separate worktrees, and the dispatcher says which.
No upstream action.

### 27. receiving-code-review treats every reviewer as a person

**Upstream.** The skill's reviewers are humans or "External Reviewers"
(`SKILL.md:59-86`). Inside the workflow the reviewer is a subagent whose
findings go through the fix loop's rulings and whose "Declined to judge" lines
need a ruling each (finding 10); the skill never meets that case. "If
conflicts with your human partner's prior decisions: Stop and discuss with
your human partner first" (`:82-83`) is a stall inside a rulings-not-stalls run
(finding 19), and the two skills do not say which wins. Two of its rules are
quoted as "your human partner's rule" (`:86`, `:98`), and the ban on "You're
absolutely right!" cites an "explicit instruction-file violation" (`:30`) that
is a fact about upstream's own `CLAUDE.md`. The GitHub reply recipe uses `gh
api` (`:203-205`) in a skill that is otherwise forge-agnostic, after
finishing-a-development-branch went forge-agnostic in v6.4.x.

**Ours.** `9c630f9` (2026-11-06) states the two rules in the skill's own words
and drops the ban no file here holds. The `gh api` line stands (`:214`). Our
executing-plans Step 3 works the whole-plan review's findings through this
skill (finding 11), so the subagent-reviewer case is live here too and still
unaddressed in the text; in practice the fix loop's `Ruling:` line governs,
and this skill governs the standalone case.

**Disposition: record.** One sentence that a subagent reviewer's finding is
ruled on under the executor's rules, and that this skill's stop applies
outside a run, would close the ambiguity on both sides. Low; a wording change
to a discipline skill, so a micro-test if it is made.

### 28. finishing-a-development-branch guesses the test command and has no conflict path

**Upstream.** Step 1 runs "the project's full test suite (`npm test` / `cargo
test` / `pytest` / `go test ./...`)" (`SKILL.md:16`), a guess, in the skill that
gates integration, after #2110 taught TDD that the project's documented command
defines green (finding 13; for this repository a bare `pytest` fails). Option
1 is `git checkout <base>; git pull; git merge <feature>` (`:88-100`): a `git
pull` whose behavior depends on the user's pull configuration, and a merge
with no instruction for a conflict, though the next paragraph handles a test
failure on the merged result carefully (`:102-104`). Nothing checks that the
plan's leftovers were filed before the branch is integrated: the skill runs
after `final-review.md` has deleted the ledger (finding 20).

**Ours.** Step 1 carries the same guess (`SKILL.md:35`), one line below a core
principle that already names the backlog check (`:23`). The backlog gate is
ours alone: Step 1b runs `deferred_stats.py` and only the aged tail (items
open past 45 days) gates (`:54-95`), and the plan-completion protocol has
already run before this skill starts. The merge-conflict silence is shared.
Finding 8's three items (discard menu, guard format, `gh`-optional PR) stand.

**Disposition: fix directly, no spec, for Step 1's wording on our side**:
"the project's documented test command(s)", plan 75's phrase, which is a port
of our own TDD line and needs no new micro-test case beyond re-running plan
75's. The conflict path is a local design item, low: stop, show the conflict,
ask; never resolve a merge conflict on your own initiative.

**Done** (plan 82, 2026-11-09): finishing-a-development-branch Step 1 runs the project's documented test
command(s), not a guessed one. The micro-test held: the treatment passed 5 of 5 against a control at
5 of 5. The conflict path stays open.

### 29. using-git-worktrees sets up Python projects wrongly and drops isolation silently

**Upstream.** Step 2's setup runs `pip install -r requirements.txt` and `poetry
install` for any `pyproject.toml` (`SKILL.md:106-119`): on a uv project it
installs with the wrong tool, and on a lock-less `pyproject.toml` it installs
anything. Step 3 guesses the test command again (`:121-130`). The sandbox
fallback ("tell the user the sandbox blocked worktree creation and you're
working in the current directory instead", `:100`) is the right message but
then proceeds in the main checkout, where SDD's implementers will commit; the
skill does not ask. Consent is asked at Step 0 (`:41-45`), which is a stop at
launch, where the partner is present; fine under finding 7's decision.

**Ours.** The setup half is covered since `169942a` (2026-11-01): `uv.lock`
first, then `poetry.lock`, then `requirements.txt`, and no automatic install
for a `pyproject.toml` without a lock file (`:136-137`; `NOTICE`); the same
commit checks the chosen directory's ignore rule with a trailing slash (`:102`).
Step 1a adds a base check before a native worktree tool is used (`:64-73`).
The sandbox fallback is the same text (`:122`).

**Disposition: already covered, except the fallback,** which is a shared design
choice: record it, and if it ever bites, make it ask. Low.

### 30. systematic-debugging's `find-polluter.sh` is still invoked by a relative path upstream — already covered

**Upstream.** #2607 fixed path resolution for the five SDD and executing-plans
helpers and added a test that fails any relative `scripts/<helper>` reference.
`find-polluter.sh` is the sixth bundled script, and its invocation is still
`bash ./find-polluter.sh '.git' 'src/**/*.test.ts'`, "in this directory"
(`root-cause-tracing.md:101-104`): it resolves against the user's repository,
the exact class of bug #2607 named, and the new test's pattern lists only the
five helpers, so it cannot catch this one. The 2026-10-28 text of finding 8
already said upstream's `bash ./` prefix (#2301) does not fix resolution; v7.0.2
confirms it. The figure "95% of 'no root cause' cases are incomplete
investigation" (`SKILL.md:275`) is unsourced. Upstream's file ends at line 283
and has no first-time fix-rate statistic.

**Ours.** The invocation is anchored (`root-cause-tracing.md:102`:
`<this-skill-dir>/find-polluter.sh`, plan 50), the script was hardened twice
(finding 8), and `457fdbe` (2026-11-06) pointed the Red Flags at Phase 4,
step 5. The shared 95% figure remains (`SKILL.md:286`); our retained Real-World
Impact section also gives unsourced figures, including a first-time fix rate
(`:305`), which upstream no longer carries.

**Disposition: already covered for the path; record the figures.** The
figures are rhetoric in a discipline skill; cutting them is a micro-tested
change for no measured gain. No action.

### 31. verification-before-completion lacks the documented-test-command pointer

**Upstream.** "If you haven't run the verification command in this message,
you cannot claim it passes" (`SKILL.md:20`); "RUN: Execute the FULL command
(fresh, complete)" (`:27-28`). Its first gate step already says "IDENTIFY:
What command proves this claim?" (`:26`); the Common Failures table also covers
builds and lints, so the command depends on the claim. For a test-suite claim,
it lacks TDD's explicit pointer to the project's documented test command
(#2110). The Common Failures row "Agent completed |
VCS diff shows changes | Agent reports 'success'" (`:47`) names the weakest
evidence in the table: a diff proves that files changed, not that they are
right. The table separately requires tests for a "Tests pass" claim, so this
row should not be read as a substitute for execution evidence. The proposed
documented-command pointer is a wording improvement, not the introduction of
command selection into a skill that has none.

**Ours.** The description was broadened to the moments that matter in this
workflow (marking a task or todo complete, moving to the next task, relaying
a subagent's success report) and a Bottom Line section closes it; `226ab9f`
dropped two narrative blocks upstream had removed. The claim-specific IDENTIFY
step remains (`SKILL.md:38`); the documented-test-command pointer is absent.

**Disposition: fix directly, no spec, low**: one pointer at the documented
test command rule where "FULL command" appears, on our side. A wording change
to a discipline skill, so a micro-test case: the "should pass" temptation
with a project whose documented command is not `pytest`.

**Done** (plan 82, 2026-11-09): verification-before-completion's RUN step points a test claim at the
documented test command. The micro-test's control passed 5 of 5, so it could not show an effect. The
owner kept the pointer at the plan's completion gate.

### 32. test-driven-development — nothing new at v7.0.2

Upstream's file is unchanged since v7.0.1. Findings 3 (falsifiability,
prospective) and 13 (the suite defines green, adopted by plan 75 with "the
project's documented test command(s)" in place of upstream's "bare `pytest`",
`SKILL.md:182`) stand, and finding 24 carries the workflow question. Since
2026-10-31 our copy gained a pointer to develop-testing-strategy for choosing
what to test (`8fa5b70`), scoped on 2026-11-06 so the failing-test rule applies
to new behavior (`988ae8f`). We still ship the full Why Order Matters section
(`:214`) and `testing-anti-patterns.md` (`:364`); upstream still has
`writing-good-tests.md` (`:216`). **No action.**

### 33. writing-skills says nothing about where test scenarios live

**Upstream.** #2654 moved systematic-debugging's pressure scenarios and
creation log under `tests/` and added a test so no skill ships files like them
again. writing-skills, the skill that tells an author to create those
scenarios (`SKILL.md:14`, `:194`, `:278`, `:297-308`, checklist `:352`), says
nothing about where they go. The rule lives in a test, not in the skill an
author reads; the next author puts the scenario beside `SKILL.md` and learns
the rule from a red test. Unchanged otherwise since plan 72's map (finding 17).

**Ours.** Our RED baselines live as `specs/baseline/red-baseline-<topic>.md`, by
convention, and our checklist (`:384`) does not say so either. `f7a452f`
(2026-11-01) aligned the plan-id and skill-name rules with the code that
enforces them, the same shape of fix.

**Disposition: record; a one-line placement rule in the checklist, low.** Not
a discipline wording; no micro-test.

## Suggested disposition

Under this repo's proportional-process rule:

- **Done, earlier:** findings 1, 2, 5, 6 (plan 22); 8's `Spec:` pointer and
  11's handoff half (plan 40); 8's `find-polluter.sh`, 12's range guards and
  `.gitignore`, 16's two fixes (plan 50); 8's untracked-file guard as an idea
  (plan 60); 4 (plan 70, on v7.0.1); 17's SDD half (plan 71) and
  writing-skills half (plan 72); 9 and 10 (plan 73); 7, 11 and 13 (plan 75).
  Unchanged by this revision.
- **Already covered, no action:** #2608 (`start-server.sh`, `3ad94f8`); #2654
  (no dev files here; upstream's layout test not adopted, by convention);
  finding 20 (the plan-completion protocol); finding 23 (the routing story);
  finding 25 (requesting-code-review); finding 26's model half; finding 29's
  setup half; finding 30's path.
- **Fix directly, no spec, in one plan,** after the order below:
  - Finding 18: the `task-start` no-commit guard (a defect), the no-repository
    message with exit 2 in `sdd-workspace`, `task-brief`'s ID grammar and
    hidden-fence refusal (#2604, #2605) with the probe's cases as tests, and
    the ten bare helper references plus a `build/` lint on the anchor
    (#2607). `-C DIR` optional.
  - Finding 28: finishing-a-development-branch Step 1 names the documented
    test command.
  - Finding 31: verification-before-completion points "FULL command" at the
    same rule, with one micro-test case.

  Done: plan 82 (2026-11-09).
- **Earlier work still open:** finding 3's prospective falsifiability
  guidance; finding 8's discard-menu consideration and optional guard-format
  convergence; finding 17's compaction-cut probe and residual writing-skills
  guide rewrite. The latter two retain their existing backlog items; the
  completed splits do not close them. Findings 9–11's post-adoption review and
  test follow-ups retain the backlog owners named above.
- **Port candidate, a plan with micro-tests and no spec:** finding 4's #2644
  retune, applied as upstream's diff against our v7.0.1-derived copy with plan
  70's divergences held, tested against plan 70's RED baseline with the
  question-style cases re-run. The owner decides whether it runs before the
  tester-seat brainstorm. The original author reports that recommendation
  from a review session; the claimed saving on nine defaults is unverified.
  Plan 70's isolated T7 rerun, rather than its original GREEN claim, is the
  current local baseline evidence. **Update 2026-11-09 (plan 83):** the
  tester-seat brainstorm has run, and finding 24 closed with no build plan
  (D8). The order question no longer applies.
- **Reported order (unverified 2026-11-07 session context):** this drift pass; then the tester-seat
  brainstorm (finding 24, handoff reported without an artifact path); then its plan. Finding 18's helper
  fixes land before the seat's plan, since both touch `task-brief` and the
  helper finding 21 asks for. **Update 2026-11-09 (plan 83):** the brainstorm ran as
  `specs/spec-derived-acceptance-tests.md`, then as `specs/completed/statement-level-readings.md`.
  Neither probe's step met its bars against a fresh Self-Review, and the owner chose no build plan for
  finding 24 (D8), so no seat's plan follows. Finding 21's part keeps its own build plan.
- **Local design proposals, not yet logged in `specs/deferred_items.md`, no spec yet:**
  finding 21 (the controller runs the task's tests before the review; one
  design with the tester seat); finding 22 (a ruling that contradicts spec
  text becomes an amendment or a deferred item); finding 26's worktree half;
  finding 28's conflict path; finding 27's one sentence on subagent reviewers;
  finding 33's placement line.
- **Decided, record only:** finding 19 (finding 7's decision); finding 29's
  sandbox fallback; finding 30's figures; finding 32.
- **Not adopted until the probe has run:** upstream's whole-file byte bar
  (finding 17). Three of our files now fail it and pass ours; writing-plans is
  6 characters inside our window, so its `references/` split is the next
  move under either bar.
- **Not adopted, recorded:** finding 12's basename collision (M2) and
  interpreter prefixes, finding 14, finding 15 (unchanged at v7.0.2), the
  Windows path fix (#2602), upstream's layout test (#2654).
- **Declined:** v7.0.1's contribution templates (#2569), and v7.0.2's harness,
  hook and packaging work, which governs installs we don't ship.
- **Prospective only:** finding 3.

Any adoption needs a `NOTICE` change-list entry. The existing "adopted FROM
upstream" entries are the model: name what was taken, from which release,
and where the port deliberately diverges. When the next pass runs, update this
document's "Next review starts from" row along with the findings, and
re-take the anchors the helper plan and the brainstorming port move.

## Verification and retirement record (2026-11-07)

This pass checked upstream claims against the pinned
[v7.0.1 → v7.0.2 comparison](https://github.com/obra/superpowers/compare/2ce8aa1...22f0b46)
and the source files at `22f0b46`. The release delta, all thirteen upstream
byte counts, and the main/dev tree equality were verified. The brainstorming
evaluation figures are [upstream-reported results in #2644](https://github.com/obra/superpowers/pull/2644),
not an independent rerun. The pressure-scenario move is
[#2654, commit `4eb73b6`](https://github.com/obra/superpowers/commit/4eb73b6b70e66a5e1c535f4f579e720b82a3c5de);
the originally cited `4eb1ee9` does not resolve.

The local skill tree is unchanged from `5beacf5`. Fresh isolated probes
reproduced finding 18's no-commit, task-ID and unclosed-fence behavior. Exact
size counts, test-module counts and baseline backlog totals were recomputed.
Review judgments about workflow costs and proposed designs remain judgments;
the claimed 2026-11-07 handoff and owner sequencing remain unverified session
reports. This audit implements no proposed skill or script changes.

The full v7.0.1 record is retired to `specs/completed/` as a historical source,
not marked as fully implemented. All unfinished considerations identified in
it are carried here; already implemented and consciously declined portions
stay historical. Earlier citations now point to that archive, and `NOTICE`'s
next-review pointer names this file. The two duplicate unversioned/versioned
copies no longer need to remain in the live specs directory.
