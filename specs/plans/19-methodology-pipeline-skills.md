# derive-roadmap Implementation Plan (plan #2 of 2 for methodology-pipeline-skills)

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the `derive-roadmap` skill — the step that takes a synthesized Design Spec, compares it against the current implementation, and partitions the remaining gaps into staged spec→plan cycles (or exits without an artifact when the gaps fit a single cycle).

**Architecture:** A pure prose skill: `SKILL.md` plus two `references/` files. Unlike plan 18's Skill A, **no bundled script** — Reqs 7–12 mandate no validator, and a brevity-budget checker is YAGNI (record it in `deferred_items.md` if the urge strikes). The skill's discipline is enforced by wording, and the wording is verified by fresh-subagent micro-tests against a no-guidance control, per `writing-skills`. Two real fixtures drive verification: a multi-stage one and a single-stage one, both described in Global Constraints.

**Tech Stack:** Markdown skill text; `uv run --python 3.13` for the two lint scripts; fresh Claude Code subagents as the test apparatus.

## Global Constraints

Every task's requirements implicitly include this section.

- **Spec:** `specs/methodology-pipeline-skills.md` (live; retires with THIS plan under the standard protocol, since no other live plan shares the `methodology-pipeline-skills` suffix). Requirements implemented here: **Req 7–12**, plus Req 14's remaining provenance work.
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

- [ ] **Step 1: Cut the branch**

```bash
git checkout main && git status --short && git checkout -b feat/derive-roadmap && git branch --show-current
```
Expected: clean status, then `feat/derive-roadmap`.

- [ ] **Step 2: Pre-register the expected failures BEFORE dispatching**

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

- [ ] **Step 3: Dispatch 5 fresh no-guidance subagents**

Dispatch 5 `general-purpose` agents **in one message** so they run concurrently. Each gets exactly this prompt — no mention of derive-roadmap, no skill hints:

```
Read /Users/lowell/Projects/alt-nfp/specs/usable_series_methodology_roadmap.md.
It is a design spec for work on that repo. Turn it into staged, actionable work.
Do NOT write, create, or edit any file, and do NOT run git. Report your staging
as your final message.
```

- [ ] **Step 4: Score every rep against E1–E6, quoting verbatim**

For each rep, record which of E1–E6 occurred with a verbatim excerpt. **Read every match manually** — do not count keyword hits. Append to the "Observed" section.

- [ ] **Step 5: Record the scoped-cut rule outcome**

Under "Observed", state explicitly which pre-registered failures did NOT occur. Task 2 writes guidance for the observed ones only. If a failure was predicted but absent, write `E<n>: NOT OBSERVED — no guidance written` so Task 2's reviewer can check the rule was honored.

- [ ] **Step 6: Commit the branch marker (no scratch)**

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

- [ ] **Step 1: Write `skills/derive-roadmap/SKILL.md`**

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

- [ ] **Step 2: Verify the description length is in the Req 7 band**

```bash
uv run --python 3.13 --with pyyaml python -c "
import yaml,sys
t=open('skills/derive-roadmap/SKILL.md').read().split('---')[1]
d=' '.join(yaml.safe_load(t)['description'].split())
print(len(d)); sys.exit(0 if 250<=len(d)<=500 else 1)"
```
Expected: a number between 250 and 500, exit 0. If it fails, adjust wording — do not widen the band.

- [ ] **Step 3: Write `skills/derive-roadmap/references/gap-rubric.md`**

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

- [ ] **Step 4: Write `skills/derive-roadmap/references/roadmap-format.md`**

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

- [ ] **Step 5: Update provenance — all four files in one pass**

In `NOTICE`, add `    derive-roadmap/` to the originals block (before its terminating blank line, alphabetical position). In `CLAUDE.md`, add `` `derive-roadmap` `` to the originals bullet and change `(Thirteen — keep in sync` to `(Fourteen — keep in sync`. In `README.md`, add one row to the skills table matching the neighbors' format.

- [ ] **Step 6: Fix the provenance test's hard-coded count**

This test WILL fail otherwise — plan 18 hit exactly this. In `build/test_check_provenance.py`, rename `test_real_notice_originals_has_thirteen_entries` to `..._has_fourteen_entries` and change the assertion:

```python
def test_real_notice_originals_has_fourteen_entries():
    # Guards against a silent vacuous pass: if a future heading rewording ever
    # breaks notice_originals's regex, it would return [] and the drift check
    # would compare empty-to-empty and pass without checking anything.
    notice = (Path(__file__).resolve().parent.parent / 'NOTICE').read_text()
    assert len(notice_originals(notice)) == 14
```

- [ ] **Step 7: Symlink the skill so later tasks can dispatch against it**

```bash
ln -s /Users/lowell/Projects/agent-skills/skills/derive-roadmap ~/.claude/skills/derive-roadmap && ls -l ~/.claude/skills/derive-roadmap
```
Expected: symlink resolving into the repo.

- [ ] **Step 8: Run lints and the build suite**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && uv run --python 3.13 python build/check_provenance.py && cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q
```
Expected: both lints silent (exit 0), then `34 passed`.

- [ ] **Step 9: Commit**

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

- [ ] **Step 1: Add the Rollout-stamp rule to Synthesize mode**

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

- [ ] **Step 2: Verify both skills emit identical stamp wording**

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

- [ ] **Step 3: Lints and commit**

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

- [ ] **Step 1: Define the arms and the PASS bar before dispatching**

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

- [ ] **Step 2: Dispatch arm A1 — 5 reps, one message**

```
Read /Users/lowell/Projects/alt-nfp/specs/usable_series_methodology_roadmap.md.
Here's a spec — plan it. Do NOT write, create, or edit any file, and do NOT
run git. Report which skill you would use and why, then stop.
```

- [ ] **Step 3: Dispatch arm A2 — 5 reps, one message**

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

- [ ] **Step 4: Dispatch arm A3 (control) — 5 reps, one message**

Copy the gold master to the scratchpad with its routing-header line removed, and point A3 at the copy. Same prompt as A1.

- [ ] **Step 5: Score and read every match manually**

Record per rep which skill was named. **Read the reasoning, not just the skill name** — a rep that names derive-roadmap while describing writing-plans' behavior is a fail.

- [ ] **Step 6: Record the verdict honestly**

If A1 misses the bar, the lean description is insufficient and the fix is one of: densify the description (breaking Req 7's chosen tradeoff — needs the user's call), or strengthen the header. **Do not silently widen the bar.** Stop and ask.

---

### Task 5: SINGLE-STAGE EXIT verification

**Files:**
- Create: `<scratchpad>/MT-single-stage-exit.md` (scratch — never committed)

**Interfaces:**
- Consumes: the live skill from Task 2.
- Produces: evidence that Req 8's no-artifact path actually fires.

This is the path where the skill correctly produces **nothing**, and an agent that has just loaded a roadmap-writing skill is under maximum pressure to write a roadmap anyway. It ships untested otherwise — exactly how Synthesize mode shipped in plan 18.

- [ ] **Step 1: Dispatch 3 fresh reps against the single-stage fixture**

```
Use the derive-roadmap skill on /Users/lowell/Projects/agent-skills/specs/methodology-pipeline-skills.md
against the current state of that repo. Do NOT write, create, or edit any
file, and do NOT run git. Report your conclusion and stop.
```

- [ ] **Step 2: Score against the expected verdict**

Expected: **no roadmap file proposed**, an explicit single-stage-exit statement, and a handoff naming `writing-plans` (the spec fully determines the remaining work). Record verbatim what each rep concluded.

- [ ] **Step 3: Record the result**

PASS = 3/3 take the exit. Any rep that proposes a roadmap file is a real failure — strengthen the SINGLE-STAGE EXIT wording in `SKILL.md` §1 and the "Writing a roadmap for one stage" common-mistake bullet, then re-run. Record both the before and after.

---

### Task 6: Full multi-stage run, graded against the gold master

**Files:**
- Create: `/Users/lowell/Projects/alt-nfp/specs/usable_series_roadmap.md` (target repo — **write it, never commit it**)
- Create: `<scratchpad>/gold-master-grading.md` (scratch)

**Interfaces:**
- Consumes: the live skill; Task 3's stamp wording.
- Produces: the real roadmap artifact, and the plan's substantive quality evidence.

- [ ] **Step 1: Run derive-roadmap for real, in-session**

Run the skill against `/Users/lowell/Projects/alt-nfp/specs/usable_series_methodology_roadmap.md`. Let it do the gap analysis, ask its batched questions, and write the artifact. **No git in alt-nfp.**

- [ ] **Step 2: Verify the artifact's structure mechanically**

```bash
cd /Users/lowell/Projects/alt-nfp && \
  grep -c '^- \[ \] Stage ' specs/usable_series_roadmap.md && \
  grep -c 'ROUTING:' specs/usable_series_roadmap.md && \
  grep -c 'Consumes:\|Produces:\|Exit:' specs/usable_series_roadmap.md && \
  head -4 specs/usable_series_roadmap.md
```
Expected: stage count == ROUTING count; the Consumes/Produces/Exit count is 3× the stage count; the routing header appears in the first four lines.

- [ ] **Step 3: Grade the partition against the gold master's Rollout note**

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

- [ ] **Step 4: Report to the user and STOP for the gate**

Present the artifact path, the structural check, and the grading table. The artifact is **uncommitted in alt-nfp by design** — committing it is the user's call.

---

### Task 7: Deployment gate

**Files:** none.

**Interfaces:**
- Consumes: the Task 2 symlink.
- Produces: Req 12's residency evidence.

- [ ] **Step 1: Confirm the symlink resolves**

```bash
ls -l ~/.claude/skills/derive-roadmap && ls ~/.claude/skills/derive-roadmap/
```
Expected: symlink into the repo; `SKILL.md` and `references` listed.

- [ ] **Step 2: Verify nothing was evicted**

Ask the user to run `/context` in a NEW session, then check mechanically:

```bash
ls skills/ | sort > /tmp/repo_skills.txt
ls ~/.claude/skills/ | sort > /tmp/installed_skills.txt
comm -3 /tmp/repo_skills.txt /tmp/installed_skills.txt
```
Expected: 30 in each, no output from `comm -3`. Then confirm from the `/context` Skills table that all 30 User skills are listed and `derive-roadmap` is among them.

- [ ] **Step 3: Record the result**

Req 12 makes residency a **correctness precondition, not a cost line**. If any skill dropped, stop and report — do not proceed to retirement.

---

### Task 8: Plan completion protocol + branch completion

**Files:**
- Modify: `specs/plans/19-methodology-pipeline-skills.md` (this file — markup)
- Modify: `specs/deferred_items.md`
- Move: this plan → `specs/plans/completed/`
- Move: `specs/methodology-pipeline-skills.md` → `specs/completed/`

- [ ] **Step 1: Resolve-before-defer gate**

Collect every skipped step and unfixed finding. Partition into: needs-the-user (ask now, ONE batched set), unblocked-by-an-answer (implement now — the protocol restarts), and defer. Unanswered questions block the rest of the protocol.

- [ ] **Step 2: Mark up this plan**

Tick every completed step. Add `> Deviation: …` under any step that diverged, `> Skipped: <why> → deferred` on skipped ones. Add the status header at the top:

```
**Status: COMPLETE (YYYY-MM-DD)** — executed via <skill>; deferred items in specs/deferred_items.md
```

- [ ] **Step 3: Update deferred items**

First tick any earlier entries this plan implemented (`- [x] … → done in plan 19`) — notably the plan-18 entry *"Synthesize mode has no scenario verification"*, whose remaining legs (locator discipline, triage-before-spec-text ordering, the derive-roadmap handoff) this plan exercises. Then append a `## 19-methodology-pipeline-skills — YYYY-MM-DD` section with this plan's deferrals. Skip the append entirely if nothing was deferred; run the ticking pass regardless.

- [ ] **Step 4: Retire the plan AND the spec**

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

- [ ] **Step 5: Delete the scratch handoff**

`specs/SESSION-HANDOFF-dcm.md` says "Delete once acted on." Its content is now recorded in the retired spec's Amendment A. Remove it in the retirement commit.

- [ ] **Step 6: Finish the branch**

Announce: "I'm using the finishing-a-development-branch skill to complete this work." Run every test suite in `CLAUDE.md` § Commands, present the four options, and stop. **No pushes, no merges without the user's explicit choice.**
