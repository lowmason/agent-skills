# derive-roadmap Implementation Plan (plan #2 of 2 for methodology-pipeline-skills)

> **Status: COMPLETE (2026-07-30)** — executed via subagent-driven-development;
> deferred items in specs/deferred_items.md.
>
> Branch `feat/derive-roadmap`, cut from `main` by the controller (Task 0)
> rather than by Task 1's implementer. 9 commits total, `7321354`..`659be53`
> (base `fbb2d51`): the 5 in-plan commits (`7321354`, `4dd8dd7`, `c818893`,
> `0a37288`, `a2d4f1f`) plus two post-review fix commits applying approved
> Minor findings (`f790c37`, `659be53`) — see the new "Post-execution"
> section between Task 7 and Task 8.
>
> **Task 1's RED baseline ran TWICE.** Round 1 (5 reps, exactly as
> specified) was voided in full — a structural leak, not a stray read: the
> fixture names `derive-roadmap` in its own routing header, and the
> session's working directory is that skill's own development repo, so
> every rep went hunting for the named skill before staging anything.
> Round 2 used a scratchpad copy of the fixture with the skill name
> neutralized and produced the recorded result: E1–E5 NOT OBSERVED, E6
> OBSERVED (4/4), under a Hawthorne confound — the reps that scored NOT
> OBSERVED had just noticed apparent fixture tampering before acting
> correctly, so "NOT OBSERVED" cannot be read as "fresh agents do this
> unguided." **The repo owner's call: keep the SKILL.md guidance for E1–E5
> as shipped**, in tension with writing-skills' no-speculative-guidance
> rule — recorded in specs/deferred_items.md for a later, cleanly-run
> baseline to settle. See Task 1 below for the full account.

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the `derive-roadmap` skill — the step that takes a synthesized Design Spec, compares it against the current implementation, and partitions the remaining gaps into staged spec→plan cycles (or exits without an artifact when the gaps fit a single cycle).

**Architecture:** A pure prose skill: `SKILL.md` plus two `references/` files. Unlike plan 18's Skill A, **no bundled script** — Reqs 7–12 mandate no validator, and a brevity-budget checker is YAGNI (record it in `deferred_items.md` if the urge strikes). The skill's discipline is enforced by wording, and the wording is verified by fresh-subagent micro-tests against a no-guidance control, per `writing-skills`. Two real fixtures drive verification: a multi-stage one and a single-stage one, both described in Global Constraints.

**Tech Stack:** Markdown skill text; `uv run --python 3.13` for the two lint scripts; fresh Claude Code subagents as the test apparatus.

## Global Constraints

Every task's requirements implicitly include this section.

- **Spec:** [`specs/completed/methodology-pipeline-skills.md`](../../completed/methodology-pipeline-skills.md) (live at `specs/methodology-pipeline-skills.md` throughout this plan's execution; retired to `specs/completed/` with THIS plan under the standard protocol, since no other live plan shared the `methodology-pipeline-skills` suffix). Requirements implemented here: **Req 7–12**, plus Req 14's remaining provenance work.
- **Branch:** `feat/derive-roadmap`, cut from `main`. **No pushes and no merges** — the user approves integration explicitly at finishing-a-development-branch time.
- **Before EVERY commit:** run `git branch --show-current` AND `git status`. The user commits from parallel terminals; a commit once landed on the wrong branch. Both lints green before every commit:
  ```bash
  uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && uv run --python 3.13 python build/check_provenance.py
  ```
- **Skill name is `derive-roadmap`** (Req 7 — `plan-roadmap`, `stage-roadmap`, `roadmap-from-spec` all rejected). Frontmatter shape matches Skill A: `license: MIT`, `metadata: {author: Lowell Mason, version: "1.0"}`, no model/effort pins.
- **Description is LEAN, 250–500 chars** (Req 7). This is a deliberate bet that the skill is entered by scripted handoff, in-artifact header, or resume — Task 4 tests that bet and is the plan's highest-value verification.
- **Cross-skill references use bare skill names** (`use the writing-plans skill`), never a plugin namespace. Req 12 records bare-name invocation as load-bearing mitigation against `product-management:roadmap-update` and `engineering:documentation` poaching — both confirmed live in the skill listing.
- **Scratch artifacts are never committed.** `<scratchpad>` below means the session scratchpad directory the harness provides (`/private/tmp/claude-*/…/scratchpad`), never `/tmp` and never a path inside either repo. Micro-test records live there and stay there.
- **`alt-nfp` carries a no-git waiver:** read its files, write the roadmap artifact when a task says to, but **never run git in that repo**. Committing there is the user's call.

### Stale spec text — do not "fix" these back

- **Req 14 literally says the NOTICE/CLAUDE.md originals count goes "Twelve→Fourteen".** Plan 18 already took it to **Thirteen**. This plan takes it **Thirteen→Fourteen**. The spec text is stale, not wrong about the destination.
- **Req 12's `skillListingBudgetFraction: 0.025` is already set** in `~/.claude/settings.json` (plan 18, Task 9). Do not set it again; only the `/context` residency check remains.
- **Req 13 assumed derive-roadmap's RED fixture would be Synthesize mode's output.** It is not: the user hand-built it. This is stronger evidence (a real human-authored spec beats a machine round-trip artifact), but it means **derive-roadmap is never tested against Synthesize mode's actual output in this plan**. Record that honestly; Req 11's re-derivation check is where the gap would surface.

### The two fixtures

**Multi-stage fixture (primary):** `/Users/lowell/Projects/alt-nfp/specs/usable_series_methodology_roadmap.md` — a real user-authored Design Spec, 470 lines, 18 numbered requirements, carrying the derive-roadmap routing header. **It is also a second gold master:** its own Rollout note already sequences the requirements into dependency-ordered waves ("Open with Req 3's likelihood confirmation… then Req 12 and Req 7 land first, in the same change… Req 8 second… Req 5 third… Req 10 fourth"). Task 6 grades derive-roadmap's stage partition against that sequencing. Its inputs are `usable_series_methodology.md` and `usable_series_methodology_review.md` in the same directory.

**Single-stage fixture:** `specs/methodology-pipeline-skills.md` in THIS repo. Ground truth is certain: after Task 2's GREEN, everything remaining (deployment gate, provenance, neighbor housekeeping) fits exactly one spec→plan cycle — namely this plan. That is precisely the condition Req 8's SINGLE-STAGE EXIT must detect. Self-reference is a feature here: we know the right answer with certainty, and the fixture is real rather than synthetic.

---

### Task 1: Branch + RED baselines (no-skill) on the multi-stage fixture

**Files:**
- Create: `<scratchpad>/RED-derive-roadmap.md` (scratch — never committed)

**Interfaces:**
- Consumes: nothing.
- Produces: the observed failure list that Task 2's SKILL.md wording must answer. Task 2 may only add guidance for failures **actually observed here** (`writing-skills` discipline — no speculative rules).

- [x] **Step 1: Cut the branch**

```bash
git checkout main && git status --short && git checkout -b feat/derive-roadmap && git branch --show-current
```
Expected: clean status, then `feat/derive-roadmap`.

> Deviation: cut by the controller (Task 0), not by Task 1's implementer —
> the user's standing wrong-branch-commit constraint, plus the fact that
> Task 1 makes no repo commits at all, made this a controller action. Task
> 1 Step 1 became a verification that the branch was live and the tree
> clean.

- [x] **Step 2: Pre-register the expected failures BEFORE dispatching**

Write `<scratchpad>/RED-derive-roadmap.md` containing exactly this block, filled in later:

```markdown
# RED baseline — derive-roadmap (plan 19, Task 1)

## Pre-registered expected failures (written before dispatch)
- E1 Plans the spec WHOLESALE — one plan covering all 18 requirements.
- E2 Invokes writing-plans directly, ignoring the spec's routing header.
- E3 No gap analysis — stages the spec's requirements without ever
     checking what is already implemented.
- E4 Stages by spec section order rather than by dependency, contradicting
     the fixture's own Rollout-note sequencing.
- E5 No per-stage exit criterion, or exit criteria that are restatements
     of the requirement rather than observable outcomes.
- E6 Restates spec requirement text into the roadmap instead of citing §-refs.

## Observed (verbatim excerpts + counts, filled per rep below)
```

> Deviation: written once, before any dispatch, exactly as specified — this
> pre-registration is what makes Round 2's result auditable as a real
> baseline rather than back-fitted. Round 2 (Step 3) reused this same E1–E6
> list against a renamed fixture copy; the list itself never changed.

- [x] **Step 3: Dispatch 5 fresh no-guidance subagents**

Dispatch 5 `general-purpose` agents **in one message** so they run concurrently. Each gets exactly this prompt — no mention of derive-roadmap, no skill hints:

```
Read /Users/lowell/Projects/alt-nfp/specs/usable_series_methodology_roadmap.md.
It is a design spec for work on that repo. Turn it into staged, actionable work.
Do NOT write, create, or edit any file, and do NOT run git. Report your staging
as your final message.
```

> Deviation (the plan's central deviation — see the status header): **Round
> 1, run exactly as specified, VOIDED IN FULL.** All 5 reps were
> contaminated — not a stray read but a structural leak: the RED fixture
> (`alt-nfp/specs/usable_series_methodology_roadmap.md`) carries the
> Synthesize-mode routing header naming `derive-roadmap`, and the session's
> own working directory IS that skill's development repo, so every rep's
> second action was to search this repo for the named skill before doing
> any staging work. 3 reps read `specs/methodology-pipeline-skills.md`
> (Reqs 7–12 alone are enough to reproduce the behavior without the skill);
> 2 reps read this very plan file — the verbatim RED prompt AND the
> pre-registered E1–E6 list — and explicitly announced they had recognized
> a RED-baseline test. Discarded all five; salvaged none. Side finding kept
> for record: the in-artifact routing header drove hunting behavior even
> for a skill that did not yet exist — accidental evidence FOR Req 12's
> in-artifact-header mitigation.
>
> **Round 2 redesign (controller):** quarantine-by-moving-tracked-files was
> blocked twice by the permission classifier, so round 2 instead pointed
> reps at a scratchpad COPY of the fixture,
> `<scratch>/red2/specs/usable_series_methodology_roadmap.md`, with
> `derive-roadmap` renamed to `sequence-spec-stages` (verified to appear
> nowhere in agent-skills, alt-nfp, or `~/.claude`) — mutating no repo file.
> The header's instruction survives intact, so E2 stayed measurable; E1/E3–
> E6 are properties of the rep's output and were unaffected. Plan-19
> briefs and the task-1 report were also moved out of the repo to
> `<scratch>/sdd19/`. The name substitution is disclosed in the RED record
> itself, per the plan's own honesty requirement. 8 dispatches were needed
> to reach 4 valid reps: a SECOND leak channel was found mid-round — the
> shared TaskList tool state was visible to subagents, and the controller's
> own task subjects named "derive-roadmap"/"P19"/the plan, contaminating 2
> more reps with no repo file read at all. Fixed by renaming task-list
> subjects to opaque "Step N of 8" (kept opaque through Tasks 4–6).

- [x] **Step 4: Score every rep against E1–E6, quoting verbatim**

For each rep, record which of E1–E6 occurred with a verbatim excerpt. **Read every match manually** — do not count keyword hits. Append to the "Observed" section.

> Deviation: scored on Round 2's 4 valid reps (A, B, C, R1) only. Round 1's
> 5 reps were discarded wholesale per the deviation above — no partial
> salvage.

- [x] **Step 5: Record the scoped-cut rule outcome**

Under "Observed", state explicitly which pre-registered failures did NOT occur. Task 2 writes guidance for the observed ones only. If a failure was predicted but absent, write `E<n>: NOT OBSERVED — no guidance written` so Task 2's reviewer can check the rule was honored.

> Deviation (load-bearing — do not read as a clean cut signal): RESULT — E1
> NOT OBSERVED, E2 NOT OBSERVED, E3 NOT OBSERVED, E4 NOT OBSERVED, E5 NOT
> OBSERVED, E6 OBSERVED (4/4). But all 4 valid reps had just diffed the
> scratchpad fixture against the untouched real file, noticed the name
> discrepancy, and explicitly reasoned about tampering/prompt injection
> BEFORE staging — a Hawthorne confound. "NOT OBSERVED" here means "reps
> who had just noticed likely tampering did this correctly," not "fresh
> agents do this correctly unguided." E2 is the most confounded (reps
> framed honoring the header as resisting injection, not as domain
> routing). Per the plan's scoped-cut rule this would normally mean Task 2
> writes no guidance for E1–E5; **the repo owner's decision, taken at the
> Task 8 gate, was to KEEP the SKILL.md guidance for E1–E5 exactly as
> shipped** — the confound argues against treating "NOT OBSERVED" as
> settled either way. This sits in real tension with writing-skills'
> no-speculative-guidance rule; flagged in specs/deferred_items.md
> (§19-methodology-pipeline-skills) for a later, cleanly-run baseline
> (both leak channels are now closed) to resolve.

- [x] **Step 6: Commit the branch marker (no scratch)**

Nothing to commit yet — the RED record is scratch. Verify:
```bash
git branch --show-current && git status --short
```
Expected: `feat/derive-roadmap`, clean.

---

### Task 2: GREEN — SKILL.md, references, provenance, symlink (one commit)

**Files:**
- Create: `skills/derive-roadmap/SKILL.md`
- Create: `skills/derive-roadmap/references/gap-rubric.md`
- Create: `skills/derive-roadmap/references/roadmap-format.md`
- Modify: `NOTICE` (originals block)
- Modify: `CLAUDE.md` (originals bullet + count Thirteen→Fourteen)
- Modify: `README.md` (skills table — one new row)
- Modify: `build/test_check_provenance.py:89-94`

**Interfaces:**
- Consumes: Task 1's observed failure list.
- Produces: the live skill at `~/.claude/skills/derive-roadmap`; the exact frontmatter `description` string that Task 4 micro-tests.

- [x] **Step 1: Write `skills/derive-roadmap/SKILL.md`**

```markdown
---
name: derive-roadmap
description: >
  Use when a spec opens with a header naming derive-roadmap as the required
  next skill, when resuming staged work ("resume the roadmap", a
  specs/*-roadmap.md file), or when comparing a spec against the current
  implementation to stage what remains. Partitions gaps into staged
  spec-to-plan cycles. Never plans or brainstorms a stage itself.
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
---

# derive-roadmap

## Overview

Takes a Design Spec and the system it describes, and partitions the distance
between them into stages. Each stage is one spec→plan→implementation cycle
producing working, testable software.

**Core principle:** the roadmap routes; it never designs. Every stage exits
to brainstorming or writing-plans by bare name. This skill does not plan a
stage, and does not brainstorm one.

**Entry:** a spec carrying the Synthesize-mode routing header; a
`specs/*-roadmap.md` being resumed; or an explicit request to compare a spec
against the implementation.

## 1. Gap analysis — ONCE, at entry

Classify EVERY numbered spec requirement into one of four verdicts using
`references/gap-rubric.md`:

- implemented-as-specified
- implemented-differently
- missing
- in-code-but-not-in-spec

Read `specs/deferred_items.md` if it exists — its unticked entries are
pre-existing stage candidates. The /deferred command owns promotion logic;
read it, never duplicate it.

Surface contradictions and ambiguities as ONE batched question set before
writing any roadmap text.

**SINGLE-STAGE EXIT.** If the gaps fit one spec→plan cycle, write NO roadmap
file. Say so, hand directly to brainstorming (open design space) or
writing-plans (spec-determined), and record the decision in the spec's
Rollout note. A roadmap for one stage is overhead with a filename.

## 2. Stage partition

One stage = one spec→plan→implementation cycle producing working, testable
software — writing-plans' Scope Check transposed up a level.

Sequence by **dependency and information order**, not by spec section order
and not by the critique's priority tiers. A cheap question whose answer
changes a later stage's parameters goes first, even when it ranks low on
value. Say plainly when your order diverges from the spec's own ranking, and
why.

## 3. The roadmap artifact

Write `specs/<name>-roadmap.md` in the target repo per
`references/roadmap-format.md`. Hard brevity budget: cite spec §-refs, never
restate requirement text — writing-plans copies constraints verbatim later,
and a roadmap that restates them is a second source of truth that will drift.

## 4. Human checkpoint, then stop

Present the stage partition for approval before stage 1. On approval, hand
off the first stage per its ROUTING line, by bare skill name, in a fresh
session — then STOP.

The between-stages go/no-go is user-initiated via "resume the roadmap". Do
not volunteer the next stage.

## 5. Resume (reconcile)

On re-entry, for each stage: the stage stamp in its spec's Rollout note
("Stage N: COMPLETE (date) — implemented by plan <id> (path)") is
authoritative. A fuzzy match against `specs/plans/completed/` is FALLBACK
only — never let it overrule a stamp.

Re-validate every unticked stage against what actually shipped, then route
the next one per its ROUTING line.

**Parking is a first-class exit.** Remaining unticked stages append to
`specs/deferred_items.md` as self-contained items; the roadmap moves to
`specs/completed/` marked `PARKED (date) — N of M stages complete`. The
methodology and critique files retire alongside the synthesized spec — they
are its inputs.

## 6. Roadmap-completion review

Retirement is gated behind a conformance audit of the ACCUMULATED system:
re-run the gap rubric over every numbered requirement, with evidence per
verdict (implementing stage/plan, Deviation notes, deferred_items entries).

Unmet requirements exit exactly two ways: a new stage (roadmap stays live),
or conscious deferral with a written why.

This is NOT a whole-roadmap code-diff review — stages merged separately and
code quality was reviewed per stage.

Optional independent check: re-run describe-critique-methodology's Describe
mode on the refactored system and diff the fresh description against the
spec. That is a re-derivation, not a self-assessment, and it is the natural
input to the next critique round.

When improvement directions are diffuse, route to creative-thinking.

## Quick reference

| You have | Do |
|---|---|
| A spec with the derive-roadmap header | Gap analysis → partition → roadmap, or single-stage exit |
| Gaps that fit one cycle | NO roadmap file — hand to brainstorming or writing-plans |
| A `specs/*-roadmap.md` and "resume" | Reconcile via stamps, route the next unticked stage |
| Every stage ticked | Completion review, then retire |
| A stage to actually build | Not this skill — brainstorming or writing-plans, by bare name |

## Common mistakes

- **Planning the spec wholesale** — one plan for everything is the failure
  this skill exists to prevent. Partition first.
- **Designing a stage** — writing its tasks, its tests, or its approach.
  Route to writing-plans; stop there.
- **Restating requirements** — cite `§`; never copy requirement prose into
  the roadmap.
- **Sequencing by the spec's own priority ranking** — value order is the
  right way to rank recommendations and the wrong way to sequence work.
  Dependencies and cheap information-gathering come first.
- **Exit criteria that restate the requirement** — an exit criterion names
  an observable outcome, not an intention.
- **Writing a roadmap for one stage** — take the single-stage exit.
- **Trusting a fuzzy plan-name match over a stage stamp** — the stamp wins.
```

> Note: this text shipped as written in Task 2 (review clean, zero
> findings). It was amended THREE TIMES afterward by post-Task-7 fix
> commits — see the "Post-execution" section between Task 7 and Task 8 for
> the header-based overwrite guard (`c818893`, `0a37288`, `a2d4f1f`) and
> the divergence-vs-agreement wording (`f790c37`). Task 2's own review
> covers only the text as first shipped.

- [x] **Step 2: Verify the description length is in the Req 7 band**

```bash
uv run --python 3.13 --with pyyaml python -c "
import yaml,sys
t=open('skills/derive-roadmap/SKILL.md').read().split('---')[1]
d=' '.join(yaml.safe_load(t)['description'].split())
print(len(d)); sys.exit(0 if 250<=len(d)<=500 else 1)"
```
Expected: a number between 250 and 500, exit 0. If it fails, adjust wording — do not widen the band.

Result: 337 (band 250–500), exit 0.

- [x] **Step 3: Write `skills/derive-roadmap/references/gap-rubric.md`**

```markdown
# Gap rubric

Run ONCE at entry, over EVERY numbered spec requirement. One row each.

| Req | Verdict | Evidence (path:line, plan id, or "none found") | Note |
|---|---|---|---|

## Verdicts

- **implemented-as-specified** — the behavior exists and matches. Evidence
  is a path:line or a test name, never a recollection.
- **implemented-differently** — the behavior exists but diverges. Record
  BOTH what the spec says and what the code does. This verdict is the one
  most often mis-filed as implemented-as-specified; when the divergence is
  deliberate and recorded (a `> Deviation:` note in a completed plan), say
  so and cite it.
- **missing** — no implementation found. Say where you looked.
- **in-code-but-not-in-spec** — behavior exists that no requirement covers.
  Not automatically a defect: it may be scope drift to remove, or an
  unrecorded decision to fold back into the spec. Flag, do not assume.

## Batched questions

Contradictions and ambiguities go in ONE message with the completed table,
before any roadmap text. Never drip questions across turns.

## Reading deferred items

If `specs/deferred_items.md` exists, its unticked entries are pre-existing
stage candidates — fold them into the partition. Live roadmap stages are
OUT of /deferred's scope: the roadmap is its own visible backlog. Keeping
that boundary is what stops the two backlogs from diverging.
```

> Note (reviewer WARNING, controller-resolved as no defect, candidate
> deferred item): spec Req 10 mandates RECORDING this boundary, which this
> file satisfies — but the boundary is asserted only HERE, not in
> `commands/deferred.md` itself, so the two files could drift apart later.
> Recorded in specs/deferred_items.md (§19-methodology-pipeline-skills).

- [x] **Step 4: Write `skills/derive-roadmap/references/roadmap-format.md`**

```markdown
# Roadmap artifact format

`specs/<name>-roadmap.md` in the target repo. Opens with this header,
verbatim:

> For agentic workers: REQUIRED SKILL: derive-roadmap — resume via its
> reconcile step; route each unticked stage per its ROUTING line; never plan
> this document wholesale.

## Stage entries

Checkbox stages under a hard brevity budget. Each stage carries exactly
these fields and nothing else:

```
- [ ] Stage N: <short name>
      Objective: <one sentence>
      Spec: <§-refs — cite, never restate>
      Gap closed: <which rubric rows this stage discharges>
      Consumes: <what this stage assumes already exists from prior stages>
      Produces: <what later stages may assume after this ships>
      Exit: <one observable outcome>
      ROUTING: brainstorming | writing-plans
```

**Consumes/Produces are load-bearing.** The roadmap and the spec are the
ONLY cross-stage carriers — a stage's implementer sees neither the previous
stage's session nor its plan.

**ROUTING** is `brainstorming` when the stage's design space is open, and
`writing-plans` when the spec fully determines it. Name the skill bare.

## Stage-spec Rollout stamp

Every stage spec's Rollout note carries this line, which writing-plans then
copies verbatim into the stage plan's header:

> Roadmap: specs/<name>-roadmap.md, Stage N — on plan completion, tick the
> stage and re-validate later stages against what shipped.

On completion the stamp becomes authoritative:

> Stage N: COMPLETE (YYYY-MM-DD) — implemented by plan <id> (path).
> Next: resume the roadmap.
```

- [x] **Step 5: Update provenance — all four files in one pass**

In `NOTICE`, add `    derive-roadmap/` to the originals block (before its terminating blank line, alphabetical position). In `CLAUDE.md`, add `` `derive-roadmap` `` to the originals bullet and change `(Thirteen — keep in sync` to `(Fourteen — keep in sync`. In `README.md`, add one row to the skills table matching the neighbors' format.

> Deviation (adjudicated compliant, not a defect): the implementer also
> synced README's second "Credits" prose list, which this step doesn't
> mention and no lint checks. Global Constraints requires
> NOTICE/CLAUDE.md/README to agree; leaving Credits unsynced would have
> been exactly the silent drift the provenance tooling exists to catch.
> Reviewer independently reached the same conclusion.

- [x] **Step 6: Fix the provenance test's hard-coded count**

This test WILL fail otherwise — plan 18 hit exactly this. In `build/test_check_provenance.py`, rename `test_real_notice_originals_has_thirteen_entries` to `..._has_fourteen_entries` and change the assertion:

```python
def test_real_notice_originals_has_fourteen_entries():
    # Guards against a silent vacuous pass: if a future heading rewording ever
    # breaks notice_originals's regex, it would return [] and the drift check
    # would compare empty-to-empty and pass without checking anything.
    notice = (Path(__file__).resolve().parent.parent / 'NOTICE').read_text()
    assert len(notice_originals(notice)) == 14
```

- [x] **Step 7: Symlink the skill so later tasks can dispatch against it**

```bash
ln -s /Users/lowell/Projects/agent-skills/skills/derive-roadmap ~/.claude/skills/derive-roadmap && ls -l ~/.claude/skills/derive-roadmap
```
Expected: symlink resolving into the repo.

- [x] **Step 8: Run lints and the build suite**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && uv run --python 3.13 python build/check_provenance.py && cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q
```
Expected: both lints silent (exit 0), then `34 passed`.

- [x] **Step 9: Commit**

```bash
git branch --show-current && git status --short
git add skills/derive-roadmap NOTICE CLAUDE.md README.md build/test_check_provenance.py
git commit -m "feat(derive-roadmap): GREEN — SKILL.md, references, provenance"
```

---

### Task 3: Req 10 lifecycle carrier (cross-skill edit)

**Files:**
- Modify: `skills/describe-critique-methodology/references/spec-synthesis.md`

**Interfaces:**
- Consumes: Task 2's `roadmap-format.md` stamp wording — the two skills must emit the SAME line.
- Produces: the stage-stamp contract that Task 6's full run exercises.

- [x] **Step 1: Add the Rollout-stamp rule to Synthesize mode**

Req 10 makes the in-artifact carrier the lifecycle mechanism, so BOTH skills write the stamp. Append to `spec-synthesis.md`'s "Spec format" section:

```markdown
When the spec being synthesized is a STAGE of an existing roadmap, its
Rollout note carries the stamp line verbatim:

> Roadmap: specs/<name>-roadmap.md, Stage N — on plan completion, tick the
> stage and re-validate later stages against what shipped.

writing-plans copies the Rollout note verbatim into the stage plan's header,
which is where the completing session sees it during markup. That copy is
the whole carrier — there is no hook and no protocol edit behind it.
```

> Deviation (reviewer WARNING, confirmed real, deliberately NOT fixed
> here): this text asserts writing-plans "copies the Rollout note verbatim
> into the stage plan's header ... That copy is the whole carrier."
> `grep -rn -i "rollout" skills/writing-plans/` returns ZERO matches.
> writing-plans actually has a generic rule to copy "the spec's
> project-wide requirements ... verbatim from the spec" into the plan's
> Global Constraints block (`skills/writing-plans/SKILL.md:73-78`) — not a
> Rollout-note-specific mechanism. Not a Task 3 defect (scoped to one file;
> Req 10 treats the mechanism as pre-existing) and not the controller's to
> fix unilaterally: Req 10 explicitly REJECTED a writing-plans protocol
> edit for v1 ("revisit only if the carrier proves fragile in the first
> real roadmap"). The carrier looks fragile on inspection, before any real
> roadmap has run — recorded in specs/deferred_items.md
> (§19-methodology-pipeline-skills) rather than fixed at the gate.

- [x] **Step 2: Verify both skills emit identical stamp wording**

The stamp is a two-line blockquote, so a plain `grep` for the whole sentence never matches. Normalize first:

```bash
uv run --python 3.13 python -c "
import re,pathlib
pat=re.compile(r'Roadmap: specs/.*?what shipped\.', re.S)
out=set()
for p in ['skills/derive-roadmap/references/roadmap-format.md',
          'skills/describe-critique-methodology/references/spec-synthesis.md']:
    for m in pat.findall(pathlib.Path(p).read_text()):
        out.add(' '.join(m.replace('>',' ').split()))
print(len(out)); [print(repr(s)) for s in out]"
```
Expected: `1`, followed by the single normalized stamp — meaning both skills emit identical wording. If it prints `2`, reconcile them before committing.

Result: `1`, printed `1`. Reviewer independently re-verified the stamp identity even more strictly than this check does — raw un-normalized comparison including `> ` prefixes and the internal newline, plus the em-dash codepoint (U+2014) compared straight from file bytes in both files. Also confirmed the implementer correctly did NOT mirror `roadmap-format.md`'s second blockquote (the "Stage N: COMPLETE" line) — that one is a roadmap-document mutation derive-roadmap performs later, not something a synthesized spec emits; the asymmetry is correct scoping, not an omission.

- [x] **Step 3: Lints and commit**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && uv run --python 3.13 python build/check_provenance.py
git branch --show-current && git status --short
git add skills/describe-critique-methodology/references/spec-synthesis.md
git commit -m "feat(describe-critique-methodology): Req 10 stage-stamp carrier"
```

---

### Task 4: Micro-test — routing with derive-roadmap INSTALLED

**Files:**
- Create: `<scratchpad>/MT-derive-roadmap-routing.md` (scratch — never committed)

**Interfaces:**
- Consumes: Task 2's exact description string and the routing headers.
- Produces: the pass/fail verdict on Req 7's lean-description bet. **This is the plan's highest-value verification** — everything else assumes routing works.

Plan 18's Task 6 tested the spec header with derive-roadmap **absent**. That is a different experiment. This one runs with it installed and with two live competitors in the listing: `product-management:roadmap-update` and `engineering:documentation`.

- [x] **Step 1: Define the arms and the PASS bar before dispatching**

Write the bar into the scratch file first:

```markdown
# MT — derive-roadmap routing (plan 19, Task 4)

Arms (5 fresh reps each, dispatched concurrently):
- A1 COLD SPEC (primary): the alt-nfp gold master + "here's a spec, plan it"
- A2 RESUME: "resume the roadmap" with a specs/*-roadmap.md present
- A3 CONTROL: identical to A1 with the routing header line deleted

PASS bar (set before dispatch):
- A1: >= 4/5 invoke derive-roadmap; 0/5 invoke writing-plans directly;
      0/5 invoke either live poacher named in Req 12 —
      product-management:roadmap-update or engineering:documentation
- A2: >= 4/5 invoke derive-roadmap
- A3: control — records what the description alone achieves without the
      header. No bar; its purpose is to attribute A1's result to the header
      vs the description.
```

Result — A1 5/5 derive-roadmap, 0/5 writing-plans, 0/5 either poacher: **PASS**. A2 5/5: **PASS**. Req 7's lean-description bet HOLDS with the skill installed and both named poachers live in the listing.

- [x] **Step 2: Dispatch arm A1 — 5 reps, one message**

```
Read /Users/lowell/Projects/alt-nfp/specs/usable_series_methodology_roadmap.md.
Here's a spec — plan it. Do NOT write, create, or edit any file, and do NOT
run git. Report which skill you would use and why, then stop.
```

- [x] **Step 3: Dispatch arm A2 — 5 reps, one message**

A2 tests a trigger surface, not artifact quality, so it carries its own minimal fixture rather than depending on Task 6. Write `<scratchpad>/demo-roadmap.md`:

```markdown
# demo — roadmap

> For agentic workers: REQUIRED SKILL: derive-roadmap — resume via its
> reconcile step; route each unticked stage per its ROUTING line; never plan
> this document wholesale.

- [x] Stage 1: Input contract
      Objective: extend the scan input contract.
      Spec: §4
      Gap closed: rubric row 4
      Consumes: nothing
      Produces: a contract later stages may assume
      Exit: each unavailable input is recorded with its contributor disabled
      ROUTING: writing-plans

- [ ] Stage 2: Volatility-class recalibration
      Objective: replace fixed thresholds with per-class values.
      Spec: §8
      Gap closed: rubric row 8
      Consumes: Stage 1's contract
      Produces: per-class thresholds in configuration
      Exit: per-class values present for all four threshold families
      ROUTING: brainstorming
```

Then dispatch:

```
Resume the roadmap in <scratchpad>/demo-roadmap.md. Do NOT write, create, or
edit any file, and do NOT run git. Report which skill you would use and why,
then stop.
```

- [x] **Step 4: Dispatch arm A3 (control) — 5 reps, one message**

Copy the gold master to the scratchpad with its routing-header line removed, and point A3 at the copy. Same prompt as A1.

> Deviation (controller): the plan's single A3 control was split into A3a
> (header stripped, `-roadmap` filename KEPT) and A3b (header stripped AND
> filename neutralized to `usable_series_design_spec.md`). Reason: the
> description names `specs/*-roadmap.md` as its own trigger, so a single
> A3 with only the header removed leaves the filename cue standing and
> cannot answer "does the description alone suffice" — the same confound
> shape as plan 18's arm B. A1=5, A2=5, A3a=5, A3b=5 reps.

- [x] **Step 5: Score and read every match manually**

Record per rep which skill was named. **Read the reasoning, not just the skill name** — a rep that names derive-roadmap while describing writing-plans' behavior is a fail.

> Deviation (final-review Important 2, cannot fix retroactively —
> forward-mandate honored in Tasks 5/6): no rep output from this round was
> preserved anywhere; the 20-rep dataset rests on the implementer's summary
> plus one excerpt per rep, since subagent transcripts do not persist.
> Reviewer judged this not worth a re-run (line-number corroboration in the
> excerpts addresses fabrication risk) but mandated that Tasks 5 and 6
> preserve full rep output to `<scratchpad>/mt<N>/<arm>-rep<K>.md` — both
> did.

- [x] **Step 6: Record the verdict honestly**

If A1 misses the bar, the lean description is insufficient and the fix is one of: densify the description (breaking Req 7's chosen tradeoff — needs the user's call), or strengthen the header. **Do not silently widen the bar.** Stop and ask.

A1 and A2 both met their bars — no widening needed. Attribution (why the
A3 split mattered): A1 vs A3a shows the routing header's marginal
contribution is ZERO on this fixture (4/5 A3a reps noticed the header was
missing and routed correctly anyway, off the filename + the spec's
Synthesize-mode shape). A1 vs A3b shows description ALONE does NOT
reliably suffice, and the honest number is 1/5 not 3/5: 2 of A3b's 3
apparent successes had reconstructed the stripped header verbatim from
`skills/describe-critique-methodology/references/spec-synthesis.md:76`
rather than routing off the description — the implementer disclosed this
stratification rather than silently recoding, so reps stand as scored.
A fourth entry path was found unprompted (an upstream sibling skill's
reference file naming derive-roadmap as required successor), and a
real hazard was flagged unprompted by 3 reps: a naive `<name>` derivation
would make the skill overwrite its own input spec (see Task 6).

> Deviation (final-review Important 1, fixed as a pre-registration
> annotation, tally unchanged): "description alone" was the wrong label
> for A3b — all 5 reps read full SKILL.md bodies of both derive-roadmap
> and writing-plans (permitted by the dispatch), so the condition actually
> tested was "no header, no `-roadmap` filename, full skill-body reads
> permitted," not "description alone." Separately: a true description-only
> measurement (passive auto-load, not deliberate selection) is not
> reachable by this dispatch method at all — reframed as a method limit,
> not a missing arm. Fix landed as 3 bracketed self-labeling annotations
> above the `## Results` heading in the scratch record, preserving the
> original wrong label at its original line with the correction appended
> — re-review confirmed the tally, bar, and all four arm counts moved
> nowhere.

---

### Task 5: SINGLE-STAGE EXIT verification

**Files:**
- Create: `<scratchpad>/MT-single-stage-exit.md` (scratch — never committed)

**Interfaces:**
- Consumes: the live skill from Task 2.
- Produces: evidence that Req 8's no-artifact path actually fires.

This is the path where the skill correctly produces **nothing**, and an agent that has just loaded a roadmap-writing skill is under maximum pressure to write a roadmap anyway. It ships untested otherwise — exactly how Synthesize mode shipped in plan 18.

- [x] **Step 1: Dispatch 3 fresh reps against the single-stage fixture**

```
Use the derive-roadmap skill on /Users/lowell/Projects/agent-skills/specs/methodology-pipeline-skills.md
against the current state of that repo. Do NOT write, create, or edit any
file, and do NOT run git. Report your conclusion and stop.
```

> Deviation: 6 reps were dispatched to reach 3 admissible (3 void, all
> void-rulings confirmed by transcript grep rather than self-report — see
> Step 2's deviation for the isolation holes found and fixed mid-round).

- [x] **Step 2: Score against the expected verdict**

Expected: **no roadmap file proposed**, an explicit single-stage-exit statement, and a handoff naming `writing-plans` (the spec fully determines the remaining work). Record verbatim what each rep concluded.

> Deviation (controller, PRE-Step-1): the plan's literal bar above assumes
> a known "single-cycle-remains" ground truth, but the plan's own bar was
> a GUESS. After Task 2's GREEN, a gap analysis against the spec's
> Verification section found only Req 12's `/context` residency
> outstanding — so a rep could correctly conclude "nothing remains,"
> which is neither "write a roadmap" nor a `writing-plans` single-stage
> exit, and would have failed the plan's literal bar for the RIGHT reason.
> **The bar was recomputed** to be reading-agnostic: PASS = proposes/writes
> NO roadmap file AND states why; FAIL = proposes/writes a roadmap file or
> partitions into ≥2 stages; whether the rep says "single-stage exit" in
> those words, names writing-plans vs brainstorming, or concludes
> one-cycle vs zero-gap is recorded as INFORMATIONAL ONLY, not scored.
>
> Two isolation holes surfaced and were fixed mid-round: (1) the plan-19
> ledger (`.sdd/progress.md`) was still readable from inside the repo —
> rep 4 read it and quoted the controller-recomputed bar back verbatim;
> moved to `<scratch>/sdd19/progress.md` with a pointer file left behind.
> (2) a rep called TaskList/TaskGet and found stale plan-18 task entries
> still literally titled "Micro-test 1/2/3" — deleted.
>
> Also disclosed: to keep the fixture self-referential-safe, the
> controller had QUARANTINED `specs/plans/19-*.md` and
> `specs/SESSION-HANDOFF-dcm.md` out of the tree for this task (restored
> before Task 8 — see Task 8's markup). This is a genuine confound, not a
> clean read of the real repo state — see Step 3.

- [x] **Step 3: Record the result**

PASS = 3/3 take the exit. Any rep that proposes a roadmap file is a real failure — strengthen the SINGLE-STAGE EXIT wording in `SKILL.md` §1 and the "Writing a roadmap for one stage" common-mistake bullet, then re-run. Record both the before and after.

Result: **PASS 3/3** against the recomputed bar (rep1 zero-gap, rep3
one-cycle, rep6 one-cycle — the recomputed bar tolerated both readings, by
design). No repo diff; HEAD unchanged.

> Deviation (review Important 1, narrows the claim): the dispatch's own
> prompt says "Do NOT write, create, or edit any file," which makes
> "writes no roadmap file" partly unfalsifiable — 3 of 6 reps explicitly
> cited the no-write order as part of their reasoning. What this PASS
> licenses is the narrower claim "under a no-write constraint, reps
> neither propose a roadmap nor partition into stages," not "the
> no-artifact path fires under maximum pressure to actually write one."
> Partially mitigated: reps 3 and 6 affirmatively framed their decision as
> independent of the write constraint. Judged not worth a re-run
> (reviewer concurred).
>
> Deviation (review Important 2, cost of the quarantine): deleting
> `specs/plans/19-*.md` from the tree changed the ground truth the reps
> actually reasoned about — 3 reps concluded from the FALSE premise that
> no plan #2 exists at all. Direct evidence it was the deletion and not
> repo state: the one `.sdd`-contaminated rep (excluded above) correctly
> reported plan #2 exists and is mid-execution. Does not break the PASS
> (reps 3 and 6 still reach a one-cycle remainder and still decline to
> roadmap it; the bar is reading-agnostic by construction), but the
> fixture the reps reasoned about was not the fixture the bar was computed
> against.
>
> **RETRACTED** (struck by the controller on the reviewer's finding, kept
> here for the record rather than silently removed): an earlier pass of
> this record claimed the contamination in this round was directional
> evidence FOR the skill text ("even the void reps declined to roadmap").
> That is wrong — every contamination channel in this dataset (the ledger
> read, the "skill is grading itself" awareness) biased TOWARD the
> measured PASS outcome, so the contaminated reps have zero discriminating
> power in either direction. Do not read a 3/3 PASS as stronger than it
> is on that account.

---

### Task 6: Full multi-stage run, graded against the gold master

**Files:**
- Create: `/Users/lowell/Projects/alt-nfp/specs/usable_series_roadmap.md` (target repo — **write it, never commit it**)
- Create: `<scratchpad>/gold-master-grading.md` (scratch)

**Interfaces:**
- Consumes: the live skill; Task 3's stamp wording.
- Produces: the real roadmap artifact, and the plan's substantive quality evidence.

- [x] **Step 1: Run derive-roadmap for real, in-session**

Run the skill against `/Users/lowell/Projects/alt-nfp/specs/usable_series_methodology_roadmap.md`. Let it do the gap analysis, ask its batched questions, and write the artifact. **No git in alt-nfp.**

> Deviation (controller): separated PRODUCTION from GRADING. Running the
> skill and then grading its own output against a table the same agent has
> already read is a confound — an agent that knows the expected sequencing
> drifts toward it. Instead the controller dispatched one producer
> sub-agent whose prompt mentioned no grading, gold master, or expected
> sequencing, preserved its verbatim output to `<scratch>/mt6/producer.md`,
> then graded separately.

> Deviation (filename): the artifact was actually written to
> `specs/usable-series-selection-roadmap.md` (title-derived), not
> `specs/usable_series_roadmap.md` as this task's Files: block and Step 2
> literally name — the skill text as shipped had no `<name>` derivation
> rule yet (see the overwrite near-miss below). Gold master verified
> byte-identical after the run (`shasum` match against the pre-run backup
> at `<scratch>/GOLDMASTER-backup.md`); no git run in alt-nfp.

- [x] **Step 2: Verify the artifact's structure mechanically**

```bash
cd /Users/lowell/Projects/alt-nfp && \
  grep -c '^- \[ \] Stage ' specs/usable_series_roadmap.md && \
  grep -c 'ROUTING:' specs/usable_series_roadmap.md && \
  grep -c 'Consumes:\|Produces:\|Exit:' specs/usable_series_roadmap.md && \
  head -4 specs/usable_series_roadmap.md
```
Expected: stage count == ROUTING count; the Consumes/Produces/Exit count is 3× the stage count; the routing header appears in the first four lines.

Result (run against the actual artifact path): PASS — 12 stages == 12
ROUTING; 36 real Consumes/Produces/Exit fields (raw grep counts 37; the
extra is a prose line containing the string "Consumes: nothing," not a
defect); routing header verbatim in the first 3 lines.

> **TWO NEAR-MISS DATA-LOSS DEFECTS found here, both fixed post-Task-7**
> (see "Post-execution" section below): (F1) `roadmap-format.md` left
> `<name>` UNDEFINED with no never-overwrite rule — the producer avoided
> overwriting the input spec by one character (hyphen vs underscore) only
> because the controller's dispatch supplied a name, not because the skill
> text did. (F2) this input satisfies BOTH the resume trigger
> (`specs/*-roadmap.md`) and the entry trigger (routing header)
> simultaneously, with no precedence rule in the shipped text — a producer
> landing in §5 Resume would have found no stage stamps and plausibly
> returned no artifact at all.

- [x] **Step 3: Grade the partition against the gold master's Rollout note**

The fixture's own Rollout note is the expected sequencing. Record in the scratch file, per gold-master claim, whether derive-roadmap's partition agrees:

| Gold-master claim | derive-roadmap's stage order | Agrees? |
|---|---|---|
| Req 3 likelihood confirmation opens | | |
| Req 5 Stage-A audit starts in parallel | | |
| Req 12 + Req 7 land first, same change | | |
| Req 8 recalibration second | | |
| Req 5 churn third, despite being must-fix #1 | | |
| Req 10 inferential rewrite fourth | | |
| Req 11 revision stability expected last | | |
| Order diverges from the review's value tiers, and says so | | |

**Disagreement is a finding, not automatically a failure** — the user's ordering is one defensible sequencing, not the only one. Record where and why it differs; a divergence with a stated dependency rationale is a pass, a divergence with no rationale is a fail.

Result: 7 rows agreeing, 1 diverging-WITH-rationale, 0 diverging-without —
**PASS** under the plan's stated rule. The sole ordinal divergence is Req 5
churn landing at Stage 8 rather than third; restricted to the requirements
the Rollout note actually sequences, the order is exact
(12+7 → 8 → 5 → 10 → 11). Strongest positive: pointed at a repo that does
not contain the system its spec describes, the skill still produced a
defensible partition AND independently closed the spec's own open Req 3
question (confirmed `dist.Normal` at `model.py:276,279` vs `dist.StudentT`
at `:191` — the same finding 4 of Task 1's RED reps made independently).
Evidence ceiling (reviewer): only this one underlying fact was
independently tested — the honest claim is "the skill produces rationalized
orderings whose RELATIVE order matches a human expert's," not that the
rationales themselves are correct.

- [x] **Step 4: Report to the user and STOP for the gate**

Present the artifact path, the structural check, and the grading table. The artifact is **uncommitted in alt-nfp by design** — committing it is the user's call.

> Note: the artifact remains uncommitted in alt-nfp by design (a standing
> no-git waiver for that repo) — recorded as a deferred item
> (specs/deferred_items.md §19-methodology-pipeline-skills), not a gap in
> this task.

---

### Task 7: Deployment gate

**Files:** none.

**Interfaces:**
- Consumes: the Task 2 symlink.
- Produces: Req 12's residency evidence.

- [x] **Step 1: Confirm the symlink resolves**

```bash
ls -l ~/.claude/skills/derive-roadmap && ls ~/.claude/skills/derive-roadmap/
```
Expected: symlink into the repo; `SKILL.md` and `references` listed.

Result: symlink resolves into the repo; `SKILL.md` + `references/` present.

- [x] **Step 2: Verify nothing was evicted**

Ask the user to run `/context` in a NEW session, then check mechanically:

```bash
ls skills/ | sort > /tmp/repo_skills.txt
ls ~/.claude/skills/ | sort > /tmp/installed_skills.txt
comm -3 /tmp/repo_skills.txt /tmp/installed_skills.txt
```
Expected: 30 in each, no output from `comm -3`. Then confirm from the `/context` Skills table that all 30 User skills are listed and `derive-roadmap` is among them.

> Deviation: this step's own literal commands write to `/tmp`, contradicting
> Global Constraints ("never `/tmp`") — redirected to the session scratchpad
> instead. Mechanical half done and PASSING: 30 skills in the repo == 30
> installed, `comm -3` silent, ZERO dangling symlinks across all 30.
> **Skipped: the human-run `/context` half → deferred.** Req 12's
> residency check needs an actual human running `/context` in a fresh
> session; that cannot happen inside this non-interactive execution.
> Folded into Task 8's batched completion gate and recorded in
> specs/deferred_items.md (§19-methodology-pipeline-skills).

- [x] **Step 3: Record the result**

Req 12 makes residency a **correctness precondition, not a cost line**. If any skill dropped, stop and report — do not proceed to retirement.

Result recorded: mechanical half PASS (above); human `/context` half
PENDING (deferred item, not a stop condition — nothing observed dropped in
the mechanical check).

---

## Post-execution (final whole-branch review + fix commits)

The opus whole-branch review (`fbb2d51..0a37288`, 4 commits) returned
**"Ready to merge WITH FIXES"** — Critical 0 / Important 5 / Minor 8. The
reviewer independently re-ran the Task 3 stamp-parity script, re-measured
the description length (337), re-verified the 30/30 symlink residency, and
counted compound `Exit:` fields in the real Task 6 artifact.

**Important 1 — the blocker, one root cause / three symptoms.** The
collision guard Task 6 exposed (F1/F2) was implemented as a NAME lookup
inside a skill whose own Entry block says "resolve by header, not by
name": (a) the guard would have MISSED the only real roadmap in existence,
since the run wrote a title-derived filename the name-based check doesn't
match, so re-entering today would silently write a second roadmap beside
the first; (b) "resume the roadmap" against a headerless roadmap had no
branch; (c) the description advertises `specs/*-roadmap.md` while the body
denied filenames mean anything. Composed: adopting F2's naive fix (header
wins over filename) alone would have made the entry path fire MORE often
without the never-overwrite rule landing in the same change — the reviewer
required both in one commit.

**Important 2** — F2's own evidence was overstated (the resume trigger is
literally hyphenated, the input underscored; the "match" is fuzzy-semantic,
not literal) — the citable defect was the missing PRECEDENCE rule, not the
glob. **Important 3** — real conformance violation nobody caught: the
artifact's own Exit fields carried 2–3 outcomes against
`roadmap-format.md`'s "one observable outcome" contract; the structural
check (Task 6 Step 2) verified field presence only, never per-field
content. **Important 4** — both fix commits shipped with ZERO behavioral
coverage (entry precedence, `<name>` derivation, and the overwrite guard
are all post-run wording; neither the Task 4 routing test nor the Task 5
single-stage test touches them). **Important 5** — `SKILL.md:38` cited a
bare `references/spec-synthesis.md`, which repo convention resolves
against THIS skill's own directory; the file actually lives in
describe-critique-methodology.

**Fix wave 1 (`a2d4f1f`)** closed Important 1/2/3/5 + Minor 6 in one
commit: the guard is now HEADER-based ("scan specs/ for any file carrying
the roadmap header that names this spec as its source ... whatever its
filename"), covering the headerless-document case; the `<name>` paragraph
collapsed from 7 lines to 2; a fifth gap verdict (`out-of-repo`) was added
for the case Task 6 actually hit; the investigation-stage / stage-exit
tension was resolved; the `spec-synthesis.md` citation now names the
owning skill by bare name. A follow-up fix review caught a HALF-APPLIED
rewrite (two Quick-reference table cells still carried the old
name-based/glob framing) — controller-fixed directly in `0a37288` rather
than dispatching a subagent for two cells. Lints green, 34 passed after
each commit in this chain.

**Important 4 closed with evidence, not a deviation note.** The
controller ran a 3-rep behavioral check of the new entry-precedence + guard
wording directly (design fixed Task 5's confound: reps were explicitly
PERMITTED to write, so "writes a duplicate" was falsifiable). Fixture was
the real repo state — the spec and its existing roadmap side by side, each
carrying a different header; both files backed up first. **Result: 3/3
PASS.** All three reps read the spec's Synthesize header, ran the new §3
pre-write scan, found `usable-series-selection-roadmap.md` BY ITS HEADER
(all three explicitly noted the filename does not match the stem rule and
resumed anyway), and stopped into §5 Resume — zero new roadmap files;
post-check checksums and directory listing byte-identical to before. Reps
1 and 2 then legitimately reconciled the existing artifact via Resume and
merged rather than duplicating when they noticed each other's concurrent
edit; the controller restored the artifact to its Task-6 graded state
afterward.

**Fix wave 2 (`f790c37`), three approved Minor findings from the
triage below:** a short document skeleton added to `roadmap-format.md`
(Minor 10 — the run had invented 5 top-level sections with no contract);
`SKILL.md` §2's divergence sentence now also covers agreement, "say so"
either way (Minor 7 — it previously misfired when the spec's own ranking
already matches); `NOTICE`'s originals block reordered so `derive-roadmap/`
sits after `describe-critique-methodology/`, restoring the block's
chronological convention (Minor 11). **Knock-on fix (`659be53`):**
`README.md`'s Credits list still carried the pre-reorder position after
`f790c37` moved NOTICE's — no lint catches this (set-equal either way), so
it was fixed by inspection to keep the two files agreeing.

**Minors deferred at the gate** (not fixed — see
specs/deferred_items.md §19-methodology-pipeline-skills for the ones that
became standing items): (8) no non-interactive fallback for the batched
question set; (9) the roadmap format cannot express parallel stages; plus
the reviewer's unprompted coverage gap — `SKILL.md` §1's batched question
set and §4's human approval before Stage 1 both require an interactive
turn that no test in this plan exercised.

This wave is the "resolve-before-defer gate" (writing-plans § Plan
Completion Protocol, Step 1) for this plan: it partitioned every
outstanding finding into fix-now (above) or defer, before Task 8's markup
below was written. That partition is why Task 8 Step 1 is checked off
rather than re-run.

---

### Task 8: Plan completion protocol + branch completion

**Files:**
- Modify: `specs/plans/19-methodology-pipeline-skills.md` (this file — markup)
- Modify: `specs/deferred_items.md`
- Move: this plan → `specs/plans/completed/`
- Move: `specs/methodology-pipeline-skills.md` → `specs/completed/`

- [x] **Step 1: Resolve-before-defer gate**

Collect every skipped step and unfixed finding. Partition into: needs-the-user (ask now, ONE batched set), unblocked-by-an-answer (implement now — the protocol restarts), and defer. Unanswered questions block the rest of the protocol.

Result: run as the "Post-execution" wave above — Important 1–5 and Minors
6/7/10/11/12 from the final review were unblocked-by-an-answer and fixed
immediately (`a2d4f1f`, `0a37288`, `f790c37`, `659be53`); Minors 8/9/13 and
the reviewer's interactive-checkpoint coverage gap, plus Task 1's Hawthorne
confound and the Req 12 `/context` half, were partitioned to defer. The
repo owner separately answered the questions this gate would otherwise
have batched (the E1–E5 keep-as-shipped call, and the branch-decision
deferral) before this markup pass ran — this session executed Steps 2–5
with that answer already in hand.

- [x] **Step 2: Mark up this plan**

Tick every completed step. Add `> Deviation: …` under any step that diverged, `> Skipped: <why> → deferred` on skipped ones. Add the status header at the top:

```
**Status: COMPLETE (YYYY-MM-DD)** — executed via <skill>; deferred items in specs/deferred_items.md
```

- [x] **Step 3: Update deferred items**

First tick any earlier entries this plan implemented (`- [x] … → done in plan 19`) — notably the plan-18 entry *"Synthesize mode has no scenario verification"*, whose remaining legs (locator discipline, triage-before-spec-text ordering, the derive-roadmap handoff) this plan exercises. Then append a `## 19-methodology-pipeline-skills — YYYY-MM-DD` section with this plan's deferrals. Skip the append entirely if nothing was deferred; run the ticking pass regardless.

> Deviation (the plan's own assumption checked and NOT confirmed): the
> plan-18 entry was NOT ticked. Its "remaining legs" — locator discipline,
> triage-before-spec-text ordering, and the derive-roadmap handoff from
> Synthesize mode's ACTUAL output — were not exercised by this plan. This
> plan's own Global Constraints say so directly: "derive-roadmap is never
> tested against Synthesize mode's actual output in this plan," because
> the gold master was hand-built by the user rather than produced by
> running Synthesize mode. Task 6's real critique file
> (`usable_series_methodology_review.md`) also has no Req 3 routing header
> (confirmed by inspection), so the header-carried re-entry path was never
> exercised on it either. The plan-18 item is left exactly as it was —
> ticking it would have been recording something that did not happen.

- [x] **Step 4: Retire the plan AND the spec**

The spec retires here: no other live plan shares the `methodology-pipeline-skills` suffix, and its Rollout note says it retires with the second plan.

```bash
git mv specs/plans/19-methodology-pipeline-skills.md specs/plans/completed/
git mv specs/methodology-pipeline-skills.md specs/completed/
```
Mark the spec complete at the top, and re-point relative links in both files for their new depth (`../skills/…` → `../../skills/…`).

```bash
git branch --show-current && git status --short
git commit -m "chore(specs): retire plan 19 and the methodology-pipeline-skills spec"
```

> Deviation: neither file contained any navigable relative link
> (`grep -nF '](' ` and `grep -n '\.\./'` both returned zero hits in this
> plan and in the spec) — there was nothing to re-point. The spec's new
> status header adds one fresh link to each retiring plan
> (`../plans/completed/18-...md`, `../plans/completed/19-...md`), written
> correct for `specs/completed/`'s depth from the start.

- [x] **Step 5: Delete the scratch handoff**

`specs/SESSION-HANDOFF-dcm.md` says "Delete once acted on." Its content is now recorded in the retired spec's Amendment A. Remove it in the retirement commit.

- [ ] **Step 6: Finish the branch**

Announce: "I'm using the finishing-a-development-branch skill to complete this work." Run every test suite in `CLAUDE.md` § Commands, present the four options, and stop. **No pushes, no merges without the user's explicit choice.**

> Skipped: out of scope for this bookkeeping pass by explicit instruction
> — this session's mandate covers markup, deferred items, and retirement
> only. finishing-a-development-branch is left for the next session/the
> user to invoke.
