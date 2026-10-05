# Handoff briefs — Design Spec

**Status: DESIGN APPROVED (2026-10-04).** The owner approved the written spec,
including the self-review's changes to the approved sections: R2.5 and R4.9
moved so each component stands alone, behavioral gate criteria for C1 and C2,
and R2.4's default recommendation. Designed
section by section in one brainstorming session, from the plan-38 handoff of
the same day. Nothing here has been implemented. The evidence lives outside
this public repo, in `~/.cache/agent-skills/handoff-brief/`: `scouts.md` (the
repo's handoff surfaces, the authoring rules, per-runtime delivery),
`example-plan38-prompt.md` (the worked example) and `example-plan38-review.txt`
(its fact-check and cold read). Finding ids below, `[f<n>]` and `[rt<n>]`, are
that review's "facts" and "redteam" items.

## Purpose and scope

At both boundaries of the usual DAG, the committed file is the handoff:

- **B1**, brainstorming → writing-plans: the approved spec
  (`skills/brainstorming/SKILL.md:37`, `:66`, `:134-143`).
- **B2**, writing-plans → subagent-driven-development | executing-plans: the
  plan (`skills/writing-plans/SKILL.md:160-192`).

That loses four things:

- decisions taken after the artifact's approval gate;
- preconditions recorded in other files. Plan 35's constraint on the
  drift-automation spec sits at
  `specs/plans/completed/35-claude-code-guide-conformance.md:40` and calls that
  spec only "the drift spec";
- owner gates, and defaults the next session should flag;
- any check that the artifact still matches HEAD.

writing-plans has no entry check, and its plan-id rule (`:22`) reads only the
current branch. Decisions taken at plan review have no defined home in the plan.

On 2026-10-04 a triage session carried `specs/claude-code-drift-automation.md`
into planning (plan 38) with a reviewed brief instead:

- the owner's decisions were captured;
- a precondition was fixed;
- a prompt was drafted, and a fact-checker and a cold reader reviewed it;
- the ambiguities went back to the owner;
- memory was synced;
- the prompt was pasted into a fresh session.

The review made 36 findings, the two reviewers overlapping. Among them were three
factual errors, a self-contradiction and two scope ambiguities.

This spec operationalizes that mechanism in proportion: most handoffs need no
brief. It adds four components, each gated and shipped on its own:

| | Component | Where |
|---|---|---|
| C1 | Entry check | writing-plans: a new step and `scripts/entry_check.py` |
| C2 | Plan review and decision home | writing-plans: header, template, Execution Handoff |
| C3 | Premise-free model line (audit-3-10-26 D14) | writing-plans `:166-184` |
| C4 | Sender skill `prepare-handoff` | new original skill |

These skills are unchanged: brainstorming, subagent-driven-development,
executing-plans, derive-roadmap and describe-critique-methodology. This work
never touches `specs/claude-code-drift-automation.md`, any plan-38 file, or
`~/.claude/CLAUDE.md`.

## Decisions and alternatives

All were settled with the owner on 2026-10-04.

1. **Trigger: sender-only context.** A brief is warranted when the sending
   session holds decisions, gates, defaults or constraints that are not in the
   artifact and cannot be recomputed from the repo. A sender that wrote the
   artifact, and can still amend it, amends it instead. On every handoff, the
   receiver handles whatever can be recomputed.
   - *Rejected:* a brief whenever the artifact was approved in an earlier
     session. It fires on clean re-entries with nothing to carry and misses
     decisions that cannot be committed.
   - *Rejected:* a brief only on the owner's request. Nothing would remind a
     session that holds unrecorded decisions.
2. **The plan-38 case is B1 entered late.** Its receiver, writing-plans against
   a spec, is B1's, so there is no new boundary type. What differs is the
   sender, which ran neither DAG skill. The sender-side guidance must therefore
   load in any session. Choosing which spec to plan next is out of scope.
   - *Rejected:* a named re-entry procedure, which repeats B1's receiver logic.
   - *Rejected:* bringing readiness triage into scope.
3. **Absorb the superpowers-drift pieces that are the same mechanism.** From
   `specs/superpowers-drift-spec.md` this spec takes:
   - finding 8's plan-header `Spec:` pointer (`:278`);
   - the handoff half of finding 11, upstream's partner plan-review stage
     (`:435`).

   That spec keeps findings 4, 9 and 10 and the executing-plans port. One
   micro-test campaign then covers writing-plans' handoff text.
   - *Rejected:* coordinating only, which tests the same lines twice.
   - *Rejected:* waiting for those ports, which have no spec yet.
4. **Form: a new original skill on the sender side, writing-plans edits on the
   receiver side and at B2.** A skill is the only surface that reaches Claude,
   Codex and Gemini and can prompt a session unasked.
   - *Rejected:* a `disable-model-invocation` command. It has no Codex adapter,
     starts only when the owner remembers it, and portability Decision 3 bars
     handing off to it.
   - *Rejected:* a writing-plans-only "pull", in which the owner restates the
     decisions in the fresh session.
5. **Storage: briefs are disposable working copies outside the repo, and
   decisions land in what the receiver reads.** Briefs go to
   `~/.cache/agent-skills/handoffs/<repo>/`. Decisions land as follows:
   - spec-level ones become tagged amendments;
   - plan-level ones go to the plan's `## Decisions`;
   - private ones go to memory.
   - *Rejected:* an in-repo self-ignoring directory as the primary home. `git
     clean -fdx` deletes it, and one `git add -f` would publish it. It is kept
     as the Codex fallback.
   - *Rejected:* briefs committed under `specs/handoffs/`, which would be public
     and a second source of truth.
6. **Review scales with what the brief contains.**
   - *Rejected:* both reviewers every time, at about 350k subagent tokens per
     pass on plan 38.
   - *Rejected:* a self-check plus the owner's reading. Plan 38's errors got
     past a careful author.
   - *Rejected:* thresholds on length. A short brief with one scope-changing
     decision is the riskiest kind.
7. **RED baselines run at plan pre-flight, gated per component, each with a
   named fallback.** This is the shape of the NO-GO in
   `specs/plans/completed/recommend-model-and-effort.md`.
   - *Rejected:* measuring before the spec.
   - *Rejected:* per-task RED only.
8. **Parity: one skill body for all three runtimes.**
   - Reviewers are prompt templates, dispatched as the runtime's subagents. A
     fresh session is the fallback cold reader.
   - Launch lines are written per runtime.
   - Micro-tests run on Claude. Codex and Gemini get one smoke run each.
   - *Rejected:* Claude-first.
   - *Rejected:* canonical reviewer agents. The read-only guard's roster is
     pinned at five
     (`hooks/test_readonly_agent_guard.py::test_roster_is_the_five_readonly_agents`),
     and each agent would also need adapters and conformance coverage.
9. **D14: premise-free wording.** The handoff keeps the history-cost reason,
   drops every model-tier claim, and says to choose the execution model at
   launch. This closes audit-3-10-26 D14 without settling the guide's
   TODO(owner) (`specs/guides/claude-code-customization-guide.md:411`), which
   stays open.
   - *Rejected:* settling the default-model stance here.
   - *Rejected:* keeping the sentence verbatim and micro-testing text with a
     false premise.
10. **The entry check is a reporting script plus agent judgment.** The script
    prints facts. The agent reads the hits and decides.
    - *Rejected:* a prose checklist. Agents skip it under pressure, and
      hand-written commands go wrong, as plan 38's `git branch -a` loop did
      ([f10]/[rt23]).
    - *Rejected:* a gating script. It cannot gate the semantic check, because
      35:40 never names its spec's file, and false gates stall planning.
11. **Gates.** A part whose failure is structural, so that no control could
    pass it, ships without a gate:
    - C3's false premise;
    - R1.3's id check, since the `:22` rule cannot see other refs or
      worktrees;
    - R2.1's `Spec:` pointer, since the template has no such field.

    The rest is gated on behavior: C1's judgment step, C2's decision home, and
    C4 per failure, with its trigger (C4a) and its recipe (C4b) gated
    separately.

Also confirmed with the owner:

- the skill name `prepare-handoff`;
- this file's name;
- the `## Decisions` format (R2.2);
- one review round;
- no pinned reviewer model;
- `specs/audit-3-10-26.md` stays findings-only.

## Requirements

### Layout

```
skills/prepare-handoff/
  SKILL.md                         new: R4
  references/fact-checker.md       new: R4.5
  references/cold-reader.md        new: R4.5
skills/writing-plans/
  SKILL.md                         modified: R1.2-R1.3, R2, R3, R4.9
  scripts/entry_check.py           new: R1.1
  scripts/test_entry_check.py      new: R5.6
NOTICE, CLAUDE.md, README.md       modified: R6.1-R6.3
specs/superpowers-drift-spec.md    modified: R6.5
```

### R1 — Entry check (C1)

**R1.1** Add `skills/writing-plans/scripts/entry_check.py`.

- **Invocation.** Stdlib only, run from the repo root as
  `uv run --no-project --python 3.13 python <this-skill-dir>/scripts/entry_check.py [<spec-path>]`.
- **Contract.** It is a reporter, like `deferred_stats.py`, and it is
  read-only. It exits 0 whenever it prints a report. It exits non-zero only when
  it cannot run: outside a git repository, or when given a spec path that does
  not exist.
- **Report.** It prints four labelled fields:
  - `status:` the first line among the spec's first 10 that starts with
    `**Status`, verbatim, or `none`.
  - `since:` the commits touching the spec, committed on or after the first `YYYY-MM-DD`
    date in the status line, newest first, as `<short-sha> <date> <subject>`.
    The commit that last changed the status line is marked. If the status line
    has no date, it lists the commits after the last one that changed that
    line.
  - `mentions:` every file under the current worktree's `specs/`, untracked
    files included, except the spec itself, that contains the spec's filename
    stem, with line numbers. In
    `specs/deferred_items.md` each hit is marked `open` or `done`, taken from
    the nearest preceding `- [ ]` or `- [x]` item line.
  - `plan ids:` drawn from every ref in `git for-each-ref refs/heads
    refs/remotes` (skipping symbolic refs such as `refs/remotes/origin/HEAD`)
    and from every worktree's `specs/plans/` directory, untracked files
    included. It reports:
    - the highest id and where it occurs;
    - the next free id;
    - any id used by two different plan filenames;
    - any plan whose filename ends in this spec's stem.

  Without a spec path, it prints only `plan ids:`.

**R1.2** Add a `## Entry Check` section to writing-plans, after the opening
lines and before `## Scope Check`. It runs the script, then reads each
mention's constraint section: a plan's Global Constraints and scope fence, an
audit's row, a deferred item. It asks one batched question if any of these
holds:

- a precondition aimed at this spec;
- a status that is not approved;
- commits since approval that cannot be reconciled;
- an id collision;
- an existing plan for this spec.

A clean report proceeds without comment, as subagent-driven-development's
pre-flight does (`skills/subagent-driven-development/SKILL.md:128-140`).

**R1.3** The `:22` id rule takes the next free id from the report. A collision
is the owner's call.

### R2 — Plan template and review stage (C2)

**R2.1** The plan header gains `**Spec:** <path>`, or `**Spec:** none`, after
`**Tech Stack:**`.

**R2.2** In the template, a `## Decisions` section follows
`## Global Constraints`. Each entry reads:
`- **D<n>** (owner, <brief | plan review>, YYYY-MM-DD): <decision>. Applied in: <Task N | Global Constraints | Task N (spec amendment)>.`
An empty section reads `None.`

**R2.3** A decision that changes the spec becomes an amendment task in plan 35
Task 13's form (`specs/plans/completed/35-claude-code-guide-conformance.md:3336`):

- exact replace-this-with-that blocks;
- each edit tagged `(owner, plan <id>, <date>)`;
- the spec's status line left untouched;
- the wording approved at plan review.

**R2.4** The Execution Handoff gains a plan-review stage, after the plan is
saved and before the execution choice.

1. The owner reviews the saved plan.
2. Each decision is applied to the tasks or the Global Constraints and logged in
   `## Decisions`. Self-review re-runs on whatever changed.
3. The execution choice offers subagent-driven or inline execution, and
   recommends one with a reason drawn from the plan: subagent-driven by
   default, inline when the tasks are tightly coupled.

There is no Native mode. The sentence that sends a decision the plan cannot
hold to prepare-handoff arrives with C4 (R4.9).

**R2.5** When the session began from a handoff brief, writing-plans also:

- reads the artifact at or after the brief's earliest commit;
- logs each of the brief's decisions in `## Decisions`, with source `brief`
  and its Home;
- settles each default in the plan and lists it for review;
- honors the brief's owner gates and leave-alone list.

If C2 is a no-go, the brief's closing line (R4.4) still tells the receiver
where each decision goes.

### R3 — Model line (C3)

**R3.1** Rewrite the Execution Handoff's model claims without a tier premise.

- **Removed:**
  - "usually runs on a stronger, pricier model tier" (`:167`);
  - "inherit the pricier model" and "drops both" (`:169`);
  - "the standard model default (planning belongs on the stronger tier;
    execution does not)" (`:175-176`);
  - the inherited-model cost (`:183-184`).
- **Kept:** the history-cost reason. A fresh session does not re-read the
  planning conversation every turn.
- **Added:**
  - choose the execution model when launching the fresh session
    (`claude --model <m>`, `codex -m <m>`, `gemini -m <m>`);
  - `/clear` keeps the current model;
  - `/model` saves a new default for later sessions.

The exact wording is micro-tested (R5.4).

### R4 — `prepare-handoff` (C4)

**R4.1** The skill is `skills/prepare-handoff/SKILL.md`, with
`references/fact-checker.md` and `references/cold-reader.md`. It is portable
across runtimes: it uses no `$ARGUMENTS` and no `!` preprocessing, and it reads
files with ordinary tool calls.

**R4.2** The description is written and tested under writing-skills. It starts
"Use when…", is third person, is trigger-only, and is at most 1024 characters.
Its triggers:

- a session about to hand its work to a fresh session while holding
  decisions, owner gates, defaults or constraints the artifact does not record.
  The handoff can be a spec to planning, a plan to execution, an SDD or roadmap
  checkpoint, or "/clear and continue";
- writing a handoff brief or prompt;
- an approved spec picked up in a later session, with new decisions;
- a decision that must stay out of a public repo.

If C4a passes and C4b fails (R5.2), the description triggers on writing a
handoff brief or prompt, instead of on the handoff moment.

**R4.3 Step 1, sort.** Each thing the next session needs goes into one bin:

| Bin | Action |
|---|---|
| In the artifact | Nothing. The brief may point to it by section. |
| Recomputable by the receiver's entry check (status, commits since, files naming the artifact, plan ids) | Nothing. |
| Amendable now, with the owner approving the exact wording now | Amend and commit: a spec amendment tagged `(owner, YYYY-MM-DD)`, a `## Decisions` entry (the plan itself, if C2 did not ship), a deviation line in the subagent-driven-development ledger, or the derive-roadmap roadmap file. |
| Everything else | The brief. |

"Everything else" includes:

- decisions whose wording the owner approves later;
- provisional defaults;
- traps that only the sender's analysis found;
- owner gates;
- leave-alone items;
- anything that cannot be committed.

If that bin is empty, there is no brief, and the handoff stays "/clear (or a
fresh session), then invoke <next skill> on <artifact>".

**R4.4 Step 2, the brief.** The parts come in this order. Every slot is
required, and an empty slot reads "none".

1. **Opening line:** the receiving skill, the artifact path, the earliest commit
   to read, what to produce, and where to stop.
2. **Decisions:** each `D<n>` has four fields:
   - *You said:* the owner's words, dated;
   - *Reading:* the sender's interpretation;
   - *Home:* exactly one durable home;
   - *Approval:* now, or at a named later point, such as plan review.
3. **Defaults to flag:** each has a question, a recommended default, and the
   effect if it is wrong.
4. **Constraints and traps:** each has `path:line` evidence.
5. **Owner gates:** new gates, plus the artifact's own gates by section
   reference, not restated.
6. **Leave alone.**
7. **Closing line:** the brief's path, and the instruction to record each
   decision in its Home. After that, the brief is disposable.

The brief carries nothing the artifact states and nothing the entry check
recomputes.

**R4.5 Step 3, review, tiered by content.**

- **Always:** the sender checks each claim against its source.
- **Fact-checker** (`references/fact-checker.md`), added when the brief cites
  repo or artifact text: paths, `path:line`, section numbers, ids, commits.
  - It reports each finding as wrong, misleading, missing or nit, with DRAFT,
    PROBLEM, SUGGEST and evidence.
  - It then gives a VERIFIED OK list, the format of
    `example-plan38-review.txt`.
- **Cold reader** (`references/cold-reader.md`), added when the brief carries
  a scope-changing decision or an owner gate.
  - It reads only the brief and the repo, as the receiver would.
  - It reports contradictions, ambiguities, traps, padding, and overreach (a
    Reading presented as You said).

How the review runs:

- Both reviewers are read-only and run in parallel as the runtime's subagents.
  No reviewer model is pinned.
- Where a runtime cannot dispatch subagents, the owner opens a fresh session
  with the template.
- The sender fixes the findings. Ambiguities go to the owner as one batched
  question before the brief is sent.
- There is one review round. Slots changed afterwards get the sender's
  self-check, and the owner may ask for another round.

**R4.6 Step 4, store.** The brief goes to
`~/.cache/agent-skills/handoffs/<repo>/<YYYY-MM-DD>-<slug>.md`.

- `<repo>` is the main worktree's directory name, the same from every
  worktree. `<slug>` names the receiving work.
- **Fallback:** when the runtime refuses that write, the brief goes to
  `.handoff/` at the main worktree's root, which holds its own `.gitignore` of
  `*` (the `.sdd/` pattern). Codex's workspace-write sandbox, for example,
  permits only "the project and temporary directories"
  (`specs/guides/codex-customization-guide.md:317`).
- A brief is never committed.

**R4.7 Step 5, memory.** Update any runtime memory entry the brief
contradicts. Private decisions go to the runtime's memory. On a runtime with
no memory, a private decision lives only in the brief, and the skill says so.

**R4.8 Step 6, deliver.** The final message gives:

- the brief's path;
- "start a fresh session and paste it", the route that works on every surface,
  the desktop app included;
- one launch line per runtime, with `<model>` left to the owner. The skill may
  recommend a model, with a reason drawn from the receiving work, but never
  assumes a default:

```
claude --model <model> "$(cat <path>)"
codex -m <model> "$(cat <path>)"
gemini -m <model> -i "$(cat <path>)"
```

It adds that `/model` saves a default for later sessions, while `--model`
applies to the one session only (`model-config.md:126`, `:131` and `:145` in
`~/.cache/agent-skills/cc-guide/2.1.288/docs/`).

**R4.9** C4's phase adds one sentence to writing-plans' Execution Handoff:
a decision that cannot be written into the plan, such as one that must stay
out of a public repo, goes to prepare-handoff. The sentence goes in the
plan-review stage when C2 has shipped. writing-plans therefore never names the
skill before it exists.

### R5 — Tests and gates

**R5.1 Pre-flight.** The plan's first task runs the no-guidance baselines.

- **Where:** in sessions the owner launches from a plain terminal outside the
  repo, per Channel 5 and plan 36's precedent
  (`specs/plans/completed/36-synthesize-mode-scenario-verification.md:17`).
- **Prompts:** pre-registered under `~/.cache/agent-skills/handoffs/red/`.
- **Reps:** at least 5 per arm.
- **Record:** the results go in `specs/red-baseline-handoff-briefs-<date>.md`,
  like the existing `red-baseline-*.md` records.
- **Fixtures:** before anything else, the pre-flight copies
  `example-plan38-prompt.md` and `example-plan38-review.txt` from
  `~/.cache/agent-skills/handoff-brief/` into
  `~/.cache/agent-skills/handoffs/red/`. Neither file is in git, and both
  Validation 1 and R5.5 read them from there.

| | Scenario | RED looks for | If the control passes |
|---|---|---|---|
| C1 | writing-plans on a fixture spec with (a) a precondition in a completed plan's constraints that names the spec only by nickname, and (b) a status that is not approved | misses (a) or (b) | R1.2 is not added. The script ships with its `plan ids:` field only, and R1.3 still applies |
| C2 | the owner gives decisions at plan review, one of them spec-level, and the session is then cleared | after `/clear`, the plan does not show which decisions were taken, by whom, when, or where each applies; or the spec-level one changes the spec without the owner approving its wording | R2.2–R2.5 are not added; R2.1 still ships |
| C4a | positive: a session holds decisions taken after approval, with the wording to be approved at plan review; negative: a fresh B1 with nothing held | positive: "/clear, invoke writing-plans", with the decisions lost; negative: a brief written anyway | R5.2 |
| C4b | the control is asked to write the plan-38 handoff | a restated artifact; a Reading presented as You said; unchecked claims; missing gates | R5.2 |

**R5.2 Outcomes.** C4 is gated per failure:

| C4a | C4b | What ships |
|---|---|---|
| fails | fails | the full skill |
| fails | passes | the skill without the R4.4 recipe |
| passes | fails | the skill with the recipe and the review, triggered by writing a handoff brief or prompt (R4.2) |
| passes | passes | no skill; the owner asks for briefs |

Three parts ship without a gate. Their failure is structural, so no control
could pass them:

- **C3**, whatever C2's gate decides. Its current text asserts a cheaper
  default, which is false wherever the default is Opus: the repo's
  `.claude/settings.json` sets `"model": "opus"`, and the guide's `:422` gives
  Opus 5.5 as the account default on most plans. Its micro-test checks for no
  regression (R5.4).
- **R1.3's id check**, with the script's `plan ids:` field. The `:22` rule
  reads only the current branch.
- **R2.1's `Spec:` pointer.** The template has no such field.

R5.6's tests cover whichever script fields ship.

**R5.3** Before C4 is built, check `/context` for dropped skill descriptions.
If any description is dropped, use `skillOverrides` or prune plugins; never
trim descriptions (audit-3-10-26 I7, `specs/audit-3-10-26.md:936`).

**R5.4** writing-plans (C1–C3) gets one campaign under writing-skills.

- **Pressure scenarios** combine at least three pressures: "just plan it",
  sunk cost, and time. They check that neither the entry check nor the review
  stage gets skipped.
- **Micro-tests** run against a no-guidance control.
- **C3's micro-test** checks that the execution choice does not regress.

**R5.5** prepare-handoff follows RED-GREEN-REFACTOR, including the negative
case.

- **Planted-defect probe:** [f0], [f1], [rt0] and [rt13] are re-planted into
  the final plan-38 brief, using the DRAFT text the review quotes.
- **Pass condition:** the fact-checker reports [f0] and [f1], and the cold
  reader reports [rt0] and [rt13].
- **B2 case:** a decision that must stay out of the public repo reaches
  prepare-handoff through R4.9's sentence.

**R5.6** `entry_check.py` is built red-first, with tests in
`skills/writing-plans/scripts/test_entry_check.py`, run by writing-plans'
existing suite command. The fixtures are throwaway git repositories in a
temporary directory. They cover:

- a dated and an undated status line;
- commits before, on and after the status date;
- a constraint that names the spec only by nickname, in a file that names it
  by stem elsewhere, so the file is listed;
- open and done deferred items;
- a plan on another branch;
- a symbolic ref;
- an untracked plan in a second worktree;
- a run without a spec path;
- the non-zero exits.

**R5.7** Codex and Gemini get one smoke run each:

- the skill loads;
- a brief is written, through `.handoff/` if the first write is refused;
- a launch line starts a session whose first turn is the brief.

The owner names the model, and Codex gets an explicit `-m`.

**R5.8** Every commit passes:

- `build/check_frontmatter.py`;
- `build/check_provenance.py`;
- `build/check_conformance.py`;
- `build/check_snippets.py skills/` (Tier 1);
- the dependency-drift test;
- `build/test_runtime_support.py`;
- the writing-plans suite.

### R6 — Provenance and sync points

**R6.1** `NOTICE` gains three entries:

- **The original skill.** prepare-handoff joins the originals block.
- **The upstream adoption.** A superpowers change-list entry, modeled on "Four
  changes were later adopted FROM upstream" (`NOTICE:273`).
  - It names the `Spec:` pointer (#2086, v6.3.0) and the partner plan-review
    stage (#2258 and #2318, v6.4.1), both read at upstream `8ca22db`.
  - It records the divergences: decisions are logged in a local `## Decisions`
    section, spec-level ones are routed to tagged amendment tasks, and there is
    no Native mode.
- **The script.** `entry_check.py` and its tests are original works inside an
  adapted skill, following the `deferred_stats.py` precedent (`NOTICE:241-254`).

The plan reads upstream's text at `8ca22db` before porting. This spec has seen
only the superpowers-drift spec's description of it.

**R6.2** CLAUDE.md changes in two places:

- The "Lowell's originals" bullet (`CLAUDE.md:26`) gains `prepare-handoff`,
  stays on one line in its current form, and its "(19 originals" note becomes
  20. `build/test_check_provenance.py` pins both.
- The Commands block's comment for the writing-plans suite names the
  entry-check tests, without a count.

**R6.3** The README skill table gains a row for prepare-handoff.

**R6.4** prepare-handoff names writing-plans, subagent-driven-development and
derive-roadmap by bare skill name only, with no path into them, and
writing-plans names prepare-handoff the same way. Neither `install.py`'s
`DEPENDENCIES` nor `SOFT_REFERENCES` changes, and the dependency-drift test
confirms it.

**R6.5** `specs/superpowers-drift-spec.md` is updated:

- finding 8's `Spec:` pointer and finding 11's handoff half are marked adopted
  by this spec's plan;
- the executing-plans port stays open;
- the Suggested disposition (`:552`) is updated to match.

**R6.6** After the merge, the owner runs `install.py` to link prepare-handoff
for each runtime. The plan reminds the owner and does not run it.

## Sequencing and execution constraints

1. **Pre-flight:** R5.3's `/context` check and R5.1's baselines, then go or
   no-go per component.
2. **C1, C2 and C3 in writing-plans:** R1.1 red-first, the R5.4 campaign,
   R6.1's adoption and script entries, and R6.5.
3. **C4:** R4, R5.5, R5.7, R6.1's originals entry, R6.2 and R6.3.

Constraints:

- **Each component's commits stand alone,** so a no-go strands nothing:
  - C3, R1.3 and R2.1 ship whatever the gates decide (R5.2).
  - R2.5's brief handling sits in C2, beside the `## Decisions` section it
    writes to. If C2 is a no-go, the brief's closing line still tells the
    receiver where each decision goes.
  - writing-plans names prepare-handoff only in C4's phase (R4.9), so it never
    names a skill that does not exist.
  - If C1's gate is a no-go, R4.3's second bin reads "the receiver's checks".
- **Coordinate with plan 38.** It is in flight and rewrites the root CLAUDE.md
  to under 200 lines, removing its count comments. This plan touches two of
  those lines (R6.2). Whichever merges second rebases and re-checks the
  200-line limit.
- **Check plan ids by hand.** This spec's own plan cannot use C1, which does
  not exist yet. Check every ref, and every worktree's `specs/plans/` with
  untracked files included. Plan 38 holds 38.
- **Worktree.** Execute in a worktree created with `git worktree add` under
  `.claude/worktrees/`, from the main checkout, never with `EnterWorktree`. Put
  a branch check in the same command as every commit.
- **Test counts.** State test changes as +N deltas, never as absolute totals.
- **Leave alone:** `specs/claude-code-drift-automation.md` and every plan-38
  file.

## Validation and acceptance

1. **Plan 38, run through the design.** On the plan-38 scenario, a GREEN
   prepare-handoff routes to a brief, because the owner chose to approve the
   decisions' wording at plan review. It selects both reviewers, because the
   brief makes repo claims and carries scope-changing decisions. It sorts the
   original prompt as follows:

   | `example-plan38-prompt.md` section | Bin | Goes to |
   |---|---|---|
   | Line 1: skill, spec, stage, plan only, commit gate | everything else | Opening line; Owner gates |
   | Inputs: spec path and 7137e5e, guide anchors, snapshot, register | recomputable, or in the artifact | the entry check and the spec; the brief keeps the path and the earliest commit |
   | Inputs: which R11 and R12 parts serve Stage 1 | the sender's reading | Defaults to flag |
   | Owner decisions 1–3 | everything else | Decisions: Home = amendment task, Approval = plan review |
   | The decisions' consequence bullets (restamp, the `checked` date, C-02 to C-05, the provenance bullet, headroom) | the sender's analysis | Constraints and traps, with evidence |
   | Settle in the plan | provisional resolutions | Defaults to flag |
   | `check --worktree`; the worktree recipe | the sender's analysis; a pointer | Constraints and traps |
   | Owner gates | everything else | Owner gates, the spec's by reference |
   | Plan ID | recomputable | the entry check |
   | Leave alone | everything else | Leave alone |

   The brief it writes exhibits none of the seven findings that the recipe and
   C1 target. They are six distinct issues:
   - [rt13], prevented by You said vs Reading;
   - [rt0] and [rt14], prevented by one Home and an Approval per decision;
   - [rt8], prevented by the required gates slot;
   - [rt21], prevented by carrying only what the artifact lacks;
   - [f10]/[rt23], prevented by C1 computing plan ids.

   The other 29 of the review's 36 findings remain the reviewers' work.
2. **Negative case.** A fresh B1 with nothing held produces no brief.
3. **Entry check on this repo.** `entry_check.py
   specs/claude-code-drift-automation.md` lists
   `specs/plans/completed/35-claude-code-guide-conformance.md` among its
   mentions. When R1.2 ships, an agent following it finds the precondition at
   that plan's line 40.
4. **Probe.** The R5.5 planted-defect probe passes.
5. **Smoke runs.** The R5.7 smoke runs pass.
6. **Gates.** The R5.8 gates pass.

## Out of scope

- Choosing which approved spec to plan next.
- Upstream's executing-plans rebuild (Native mode), and superpowers-drift
  findings 4, 7, 9 and 10.
- Edits to brainstorming, subagent-driven-development, executing-plans,
  derive-roadmap or describe-critique-methodology.
- Delivery by SessionStart hook, `--append-system-prompt-file`, deep link,
  `/compact`, forks or desktop-app automation. `scouts.md`'s delivery section
  records why each falls short of a pasted user turn.
- The guide's default-model stance (TODO(owner), `:411`).

## Sources and verification notes

Re-verified on 2026-10-04 against `main@7137e5e`:

- **Handoff surfaces.** The line numbers cited above hold. writing-plans has
  no entry check. Its only step that reads `specs/deferred_items.md` is the
  completion protocol.
- **Plan 35's precondition.**
  `specs/plans/completed/35-claude-code-guide-conformance.md:40` refers to the
  drift-automation spec only as "the drift spec".
- **Refs.** `git for-each-ref` gives usable refs. `git branch -a` prints the
  symbolic `remotes/origin/HEAD -> origin/main`, which is not one.
- **Installed CLIs:**
  - claude 2.1.289: `--model`.
  - codex-cli 0.154.0: `codex [OPTIONS] [PROMPT]` and `-m`. Here `-p` is
    `--profile` and `-i` is `--image`.
  - gemini 0.46.0: `query` runs interactive by default, `-m`, `-i` runs a
    prompt then continues interactively, and `-p` is headless.
- **Model persistence.** `model-config.md:126`, `:131` and `:145` (docs
  snapshot 2.1.288): `/model` saves a default, and `--model` applies to one
  session.
- **Visibility.** `gh repo view` reports the repo PUBLIC.
- **Listing.** The session's skill listing showed all 33 personal skills
  installed under `~/.claude/skills`. The three deep-learning skills are in
  `skills/` but not installed there.
- **A stale pointer.** audit-3-10-26's D14 cites the guide's TODO(owner) at
  `:377`. It now sits at `:411`.
