# methodology-pipeline-skills — Design Spec

**Status: COMPLETE (2026-07-30)** — implemented by
[plan 18](../plans/completed/18-methodology-pipeline-skills.md) (Skill A,
`describe-critique-methodology`) and
[plan 19](../plans/completed/19-methodology-pipeline-skills.md) (Skill B,
`derive-roadmap`); retired to `specs/completed/` with the second plan, per
this spec's own Rollout note. Two Verification bullets are genuinely
outstanding rather than satisfied — see the Verification section below,
where they are left unticked rather than marked done: the `/context`
residency check (needs a human, fresh session) and the committed
Describe-mode artifact (`specs/nfp-model-methodology.md` in `alt-nfp`
remains uncommitted, the owner's call under that repo's no-git waiver).

Two new Lowell-original skills productionize the recurring methodology-critique-refactor
loop: `describe-critique-methodology` (write a code-decoupled methodological description;
after an external Claude Chat Research critique, synthesize description + critique into a
house-format specification) and `derive-roadmap` (compare that specification against the
current implementation and stage the gap into a roadmap whose stages execute through the
existing brainstorming → writing-plans → subagent-driven-development chain, gated at the
end by a whole-roadmap conformance review). Step 3 of the loop is deliberately NOT
skillified — it is the existing chain, untouched.

Design provenance: this spec supersedes `specs/methodology-skills-draft.md` (removed in
this spec's commit), which recorded the pre-brainstorming proposal and the findings of a
three-lens adversarial critique. Decisions below marked (chosen)/(rejected) were settled
in the 2026-07-26 brainstorming session.

## Motivation — the real gaps

The loop runs today as manual practice with failure modes a skill exists to guard:
- Methodology write-ups drift into code walkthroughs (variable names smuggled into
  notation, sections mirroring file layout), so the external reviewer critiques the
  implementation instead of the method.
- The critique's return leg is unowned: a fresh session weeks later saying "here's the
  critique back" matches brainstorming's deliberately greedy trigger and would produce a
  plausible spec that silently bypasses the pipeline — the most dangerous failure shape,
  because it looks like success.
- Spec-to-implementation staging is improvised: monolithic plans, restated specs,
  rubber-stamped or ignored existing code.
- Nothing audits the ACCUMULATED system against the specification once all stage plans
  retire; per-plan reviews each see one plan against its own brief.
- The roadmap tier has no lifecycle owner: the Plan Completion Protocol retires specs by
  suffix-matching plan filenames, which stage plans (named after stage specs) never
  satisfy, so a naive roadmap silently rots.

## Core principle

The pipeline's state lives in committed files, never in dialogue — and at every fragile
seam, in-artifact routing headers PAIRED with mirror triggers in the target skill's
description are the routing mechanism. Description-trigger competition alone is unreliable
(the listing is over budget with whole-description eviction) and is treated as the backup,
not the mechanism. The one seam crossing tools (the Chat Research round-trip) is carried
by an artifact the re-entry session is guaranteed to read: the critique file itself.

## Requirements

### Skill A — `describe-critique-methodology`

**Req 1 — Identity and description contract.** Directory and frontmatter name
`describe-critique-methodology` (chosen; `describe-methodology` and
`formalize-methodology` rejected — the user prefers the round-trip arc in the name).
Frontmatter: `license: MIT`, `metadata: {author: Lowell Mason, version: "1.0"}`, no
model/effort pins. The description is the dense one of the pair (≤1024 chars): third
person, "Use when…", trigger-only (never a workflow summary). It MUST carry (a) Describe-
mode cold triggers ("describe the methodology", "write up the model/math independent of
the code", "methodological description", "prepare a document for external/SOTA critique",
domain keywords: nowcast, Bayesian, NumPyro, state-space, statistical procedure);
(b) Synthesize-mode re-entry triggers ("a saved specs/*-critique.md returning from a
Claude Chat Research round-trip", "synthesize a methodology critique into a spec");
(c) delineation fences: "not for new-functionality ideas — that is brainstorming"; "the
critique itself happens externally in Chat Research — not for reviewing code or specs";
"math/prose decoupled from code — not a code walkthrough, README, or analysis writeup".
Exact wording is owned by the plan's micro-tests, not this spec.

**Req 2 — Describe mode.** Numbered workflow: (1) choose granularity up front — module or
system; (2) write the description using the matching template shape; (3) run the advisory
decoupling check (Req 5) and the template-slot self-check; (4) commit and hand off
(Req 3). Two template shapes in `references/methodology-template.md`:
- Module: notation table defining every symbol in-document; data-generating story /
  problem formulation; estimation-or-inference procedure in math; assumptions and
  limitations; evaluation criteria; open questions addressed to the external reviewer.
- System: component inventory; composition/dataflow described mathematically (what each
  component consumes/produces as random variables or estimates); cross-component
  assumptions; per-component pointers, with the module template applying per component.
Decoupling is enforced as a POSITIVE RECIPE via required template slots — held as the
default hypothesis, to be confirmed or revised against observed RED failures (Req 13);
a rationalization table is added at REFACTOR only if identifier smuggling survives
recipe + validator. Hard rule stated in the body: the description is never delegated to
the docs-writer agent (its grounding rule — read the code, verify every claim against
source — is anti-decoupling by design). Output: `specs/<name>-methodology.md` in the
TARGET work repo, committed, opening with the routing header:
`> For agentic workers: when specs/<name>-critique.md exists beside this file, REQUIRED
SKILL: describe-critique-methodology (synthesize mode) — do not draft a spec directly.`

**Req 3 — Critique handoff.** Describe mode's terminal scripted message: the description
is committed at <path>; conduct the Chat Research session INTERACTIVELY as current
practice (push back, steer); then have Chat write the critique file per
`references/critique-prompt.md`, which instructs Chat to (a) include the adjudications
reached during the interactive session, not the first-pass critique, and (b) open the
file with the routing header naming `describe-critique-methodology` (synthesize mode).
The user saves it as `specs/<name>-critique.md` beside the description. The terminal
message states the exact re-entry invocation string verbatim. The critique file's header
is the load-bearing re-entry mechanism; the description's Req 1(b) triggers are backup.

**Req 4 — Synthesize mode.** Numbered workflow: (1) staleness check — one scripted line
("Description committed <date/sha> — has the methodology moved since? git log touching
the described system since that commit"), refresh via Describe mode if yes; (2) critique
triage — a per-point table (accept / reject / needs-user-adjudication, one-line rationale
each) presented as ONE batched question set before any spec text is written; (3) synthesis
into the house spec format (summary, Motivation, Core principle, numbered Requirements
with (chosen)/(rejected) alternatives inline, Verification, Out of scope, Rollout note) at
`specs/<name>.md` in the target repo, with per-claim locators back to the description and
critique; `references/spec-synthesis.md` CITES the house skeleton's owner (this repo's
retired-spec exemplars) rather than restating it; (4) the spec opens with:
`> For agentic workers: REQUIRED NEXT SKILL: derive-roadmap — do not plan this spec
directly and do not split it into per-subsystem plans.` (wording pre-empts writing-plans'
Scope Check escape hatch); (5) the four brainstorming self-review checks (placeholders,
consistency, scope, ambiguity), fixed inline; (6) the scripted user-review gate; (7)
terminal handoff naming `derive-roadmap` by bare name in a fresh session. Synthesis in
Code (chosen); synthesis remaining in Chat, and a Chat-drafts/Code-formalizes hybrid
(rejected — the house-format landing plus the triage gate preserves the Chat-side steering
at lower artifact count).

**Req 5 — Decoupling validator.** `scripts/check_decoupling.py`, ADVISORY only — its
output is review input, never a fix-until-clean gate. Inverted filter: flag only
multi-token identifiers (snake_case with ≥2 tokens, camelCase), backticked/code-font
tokens, file paths, and call syntax; never single dictionary words or Greek-letter names
(house Bayesian style names sample sites sigma/mu/beta — naive harvesting would flag the
notation table's own required content); whitelist every symbol the description's notation
table defines. The harvest-and-flag core is built BEFORE RED (Req 13) because micro-test
scoring requires it as apparatus, independent of its advisory role in the shipped skill.

**Req 6 — Optional wiki touchpoints.** Gated on the observable predicate "if
$LLM_WIKI_ROOT is set", detail in references/ (not the body): a Describe-mode pre-flight
llm-wiki query for already-filed literature, and a Synthesize-mode suggestion that the
human drop the critique into $LLM_WIKI_ROOT/raw/ for llm-wiki ingest (the agent never
writes raw/). Cross-references by bare skill name.

### Skill B — `derive-roadmap`

**Req 7 — Identity and description contract.** Name `derive-roadmap` (chosen;
`plan-roadmap` rejected — "plan" is writing-plans' reserved noun; `stage-roadmap`
rejected — git-stage interference and noun-noun misparse; `roadmap-from-spec` rejected —
breaks verb-first style). Same frontmatter shape as Req 1. LEAN description (~250–500
chars; chosen over full density — the skill is entered almost exclusively by scripted
handoff, in-artifact header, or resume): triggers are the mirror of Req 4's header ("a
spec header naming derive-roadmap as the required next skill"), "resume the roadmap",
"specs/*-roadmap.md", "compare the spec against the current implementation".

**Req 8 — Gap analysis.** Runs ONCE at entry, SDD-pre-flight discipline: every numbered
spec requirement classified implemented-as-specified / implemented-differently / missing /
in-code-but-not-in-spec (rubric table in `references/gap-rubric.md`); contradictions and
ambiguities surface as ONE batched question set before any roadmap text. Reads
`specs/deferred_items.md` for pre-existing stage candidates (/deferred owns promotion
logic — read, don't duplicate). SINGLE-STAGE EXIT: if the gaps fit one spec→plan cycle,
no roadmap file is created — hand directly to brainstorming or writing-plans and record
the decision in the spec's Rollout note.

**Req 9 — Roadmap artifact.** `specs/<name>-roadmap.md` in the target repo: checkbox
stages (`- [ ] Stage N: …`) under a hard brevity budget — name, objective, spec §-refs
(cite, never restate; writing-plans later copies constraints verbatim), the gap closed,
stage-level Consumes/Produces (what the stage assumes exists from prior stages — the
roadmap and spec are the only cross-stage carriers), exit criterion, and a per-stage
ROUTING line: brainstorming when the stage's design space is open; straight to
writing-plans when the spec fully determines it. Stage sizing = writing-plans' Scope
Check transposed up: one stage = one spec→plan→implementation cycle producing working,
testable software. The roadmap opens with its own routing header:
`> For agentic workers: REQUIRED SKILL: derive-roadmap — resume via its reconcile step;
route each unticked stage per its ROUTING line; never plan this document wholesale.`

**Req 10 — Lifecycle.** In-artifact carrier (chosen; a one-line writing-plans protocol
edit rejected for v1 — provenance-touching and needing its own RED cycle; revisit only if
the carrier proves fragile in the first real roadmap). Synthesize mode and derive-roadmap
write into each STAGE SPEC's Rollout note: "Roadmap: specs/<name>-roadmap.md, Stage N —
on plan completion, tick the stage and re-validate later stages against what shipped."
writing-plans' verbatim-copy mechanism carries this into the stage plan's header, where
the completing session sees it during markup. The stage stamp ("Stage N: COMPLETE (date)
— implemented by plan <id> (path)") is authoritative; the reconcile step's fuzzy match
against specs/plans/completed/ is fallback only. The stamp's scripted next-step line
names the resume trigger. Parking is a first-class exit: remaining unticked stages append
to specs/deferred_items.md as self-contained items; the roadmap moves to specs/completed/
with "PARKED (date) — N of M stages complete". The methodology and critique files retire
alongside the synthesized spec (they are its inputs). Live roadmap stages are OUT of
/deferred's scope — the roadmap is its own visible backlog (recorded so the two backlogs
don't diverge).

**Req 11 — Roadmap-completion review.** Retirement is gated behind a conformance audit of
the ACCUMULATED system: re-run the Req 8 rubric over every numbered spec requirement with
evidence per verdict (implementing stage/plan, Deviation notes, deferred_items entries).
Unmet requirements exit exactly two ways: a new stage (roadmap stays live) or conscious
deferral with a written why. Optional independent check: re-run Describe mode on the
refactored system and diff the fresh description against the spec — a re-derivation, not
a self-assessment, and the natural input to the next critique round. Explicitly NOT a
whole-roadmap code-diff review (stages merged separately; code quality was reviewed
per-stage). Sanctioned human checkpoints: approve the stage partition before stage 1; the
between-stages go/no-go is honestly USER-INITIATED via "resume the roadmap". Hard stop:
the skill ends at the approved roadmap + first-stage handoff (or the completion review);
it never brainstorms or plans a stage itself. Routes to creative-thinking by bare name
when improvement directions are diffuse.

### Rollout and housekeeping

**Req 12 — Listing-budget precondition.** Before deployment: set
`skillListingBudgetFraction: 0.025` in `~/.claude/settings.json` (chosen, combined with
Req 7's lean description; either measure alone rejected as insufficient). The listing is
measured at 2.11× the ~2K default budget with whole-description drop-by-rank eviction,
and unranked new skills evict first — residency is a correctness precondition, not a
cost line. Deployment checklist ends with a `/context` check confirming both new
descriptions are resident and no existing skill dropped out. Plugin-namespace poaching
(product-management:roadmap-update, engineering:documentation) is mitigated by scripted
bare-name invocation at every handoff — recorded as load-bearing, not incidental.

**Req 13 — Development process.** One spec (this file), two plans (chosen; two spec
cycles and one combined plan rejected). Plan `<id>-methodology-pipeline-skills.md` #1
implements Skill A completely (RED→GREEN→REFACTOR→deployment checklist — the
writing-skills STOP gate forbids starting B before A's checklist completes). Between
plans, a scheduled HUMAN step: the user runs one real describe→Chat→critique round-trip
on alt-nfp; that critique is Synthesize mode's RED fixture and the resulting synthesized
spec is derive-roadmap's RED fixture (synthetic fixtures rejected — testing against a
strawman of Research mode). Plan #2 (same spec-name suffix, so this spec stays live
until both plans complete under the existing retirement rule) implements Skill B. RED
baselines for Describe mode: no-skill agents on alt-nfp, expected failures documented in
advance (variable names smuggled in, sections mirroring file layout, code-walkthrough
framing); what RED observes settles the shaping-vs-discipline classification (Req 2).
Micro-tests (5+ fresh-context reps, no-guidance controls, every flagged match read
manually): the decoupling-recipe wording; the Synthesize-mode re-entry utterance against
brainstorming; the cold spec encounter ("here's a spec, plan it") against writing-plans
verifying the Req 4 header holds. The Req 5 harvest core is built before RED. Both lints
(`build/check_frontmatter.py`, `build/check_provenance.py`) green before every commit.

**Req 14 — Provenance and neighbor tweaks.** Both skills enter the NOTICE originals
block (before its terminating blank line) and the CLAUDE.md originals bullet as
backticked names; the count updates Twelve→Fourteen. README skills table gains two rows.
Two one-line neighbor tweaks ship in the same change, neither touching superpowers-derived
files: a dispatch-note exclusion in `agents/docs-writer.md` (methodology descriptions are
out of its lanes), and — only if wording fits its 4 chars of description headroom — a
reciprocal fence in `design-architecture`'s description.

**Req 15 — v1 domain scope.** Statistical/Bayesian/nowcast methodology only (chosen;
conditional slots + a DL RED scenario now, and untested generic slots, rejected). The
single worked example stays Bayesian/nowcast. The DL/NLP extension is recorded at plan
completion in specs/deferred_items.md with the conditional-slot sketches ("if trained →
training objective; if pipeline-assembled → assembly policy") and the known breakage
cases (RAG: no estimation procedure, methodology lives in assembly choices; fine-tuned
classifier: no data-generating story; checkpoint/tokenization/schedule choices need
slots).

## Amendment A — 2026-07-26: gold-master reconciliation (Reqs 3, 4)

Between plan #1 and plan #2 the user ran a real round-trip and hand-built the
synthesized spec themselves (alt-nfp `specs/usable_series_methodology.md`,
`_review.md`, `_roadmap.md`). That artifact is a gold master for Synthesize mode: it
independently reproduced the Req 4 house skeleton, the Req 4 routing header verbatim,
dense inline locators with no orphan requirements, and (chosen)/(rejected) markers —
so the specified design survives contact with reality. Four gaps it exposed amend
Reqs 3 and 4; all four are landed in the skill.

**A1 — a third inline marker, `(open)` (amends Req 4 step 3).** A decision turning on
a matter of fact about a system outside the repo is settled by checking, not by
argument, so it is neither accept nor needs-user-adjudication — that verdict presumes
the user can settle it. In triage such a point is a plain accept whose requirement
carries `(open)`, written self-describing (`open — resolved by verification, not
argument`) and discharged by a named Verification bullet; a blocking one opens the
Rollout note, as the gold master's likelihood question does. No fourth triage verdict
(chosen; adding one rejected — it would route an external lookup into a user debate).

**A2 — first-pass critiques (amends Reqs 3 and 4 step 2).** Req 3 has
`critique-prompt.md` instruct Chat to record adjudications, and Req 4's triage defaults
rejected-by-Chat points to reject. The user's real review was a first pass with no
push-back: zero Chat-side rejections, and the synthesis made all fourteen rejections
itself. Under the rule as specified, that silence would have read as agreement.
Synthesize mode now establishes and announces adjudicated-vs-first-pass before
triaging and carries the adjudication itself in the latter case; the Chat prompt gains
the matching honesty rule ("never dress a first-pass finding as adjudicated") that
makes the detection reliable.

**A3 — the locator scheme is declared, not fixed (amends Req 4 step 3).** `C1..Cn`
stays the default, since Req 3's prompt still mandates it for critiques produced
through this skill. A foreign or pre-skill critique has none — the real one used §1–§10
plus Recommendations 1–9. The spec now opens with a Design provenance paragraph naming
both sources and declaring whichever scheme the critique's structure affords (the gold
master declared **M §n** / **R §n**).

**A4 — mode selection (amends Req 4).** The body rule matched only
`specs/<name>-critique.md` beside `specs/<name>-methodology.md`; the real pair was
`usable_series_methodology.md` / `usable_series_methodology_review.md`, which would not
have fired it. Loosened to a `methodology`-named file with a `critique`- or
`review`-named sibling, hyphens or underscores either way. Body text only — the Req 1
description is untouched, because the 5/5 re-entry routing result was measured on that
wording.

## Verification — observable outcomes

- [x] Both lints exit 0; `name` == directory for both skills; descriptions ≤1024 chars.
      Verified repeatedly across both plans (plan 18 Task 3; plan 19 Task 2 Step 2 —
      description 337 chars — and every commit's pre-commit lint run); re-verified by
      the plan 19 whole-branch reviewer as part of `fbb2d51..0a37288`.
- [ ] `/context` in a fresh session shows both descriptions resident; no existing personal
      skill dropped from the listing. **Genuinely outstanding.** Plan 19 Task 7 verified
      only the mechanical half (30 skills in the repo == 30 installed, zero dangling
      symlinks) — the human-run `/context` confirmation has not happened. See
      specs/deferred_items.md §19-methodology-pipeline-skills.
- [x] RED transcripts exist for Describe mode (no-skill baseline on alt-nfp) with the
      observed failure modes documented verbatim before GREEN was written. Plan 18
      Task 2, 7 no-skill reps, E1/E3/E5 confirmed 7/7, documented before any skill text.
- [x] Micro-test records: decoupling wording, re-entry-vs-brainstorming, cold-spec-vs-
      writing-plans — each with a no-guidance control, ≥5 reps, flagged matches read.
      Decoupling wording and re-entry-vs-brainstorming: plan 18 Tasks 4–6. The cold-spec-
      vs-writing-plans check was run twice — once with derive-roadmap absent (plan 18
      Task 6) and, definitively, with it installed and both live poachers in the listing
      (plan 19 Task 4: A1 5/5 derive-roadmap, 0/5 writing-plans, 0/5 either poacher).
- [ ] One full Describe-mode run on alt-nfp produces a committed
      specs/<name>-methodology.md passing the template-slot self-check, with the Req 2
      routing header. **Genuinely outstanding.** The real run exists
      (`/Users/lowell/Projects/alt-nfp/specs/usable_series_methodology.md`) but remains
      UNCOMMITTED — see specs/deferred_items.md §19-methodology-pipeline-skills.
- [ ] The real round-trip critique file exists with Chat-written adjudications and the
      Req 3 routing header; Synthesize mode's triage table and house-format spec (with
      Req 4 header) verified on it. Left unticked on inspection: the real critique file
      (`usable_series_methodology_review.md`) carries NO routing header at all (it
      predates the skill — confirmed by reading the file), so the Req 3 clause is
      literally false for it; and no house-format spec was ever produced by RUNNING
      Synthesize mode on this critique — the artifact used as the gold master
      (`usable_series_methodology_roadmap.md`) was hand-built by the user. Only the
      triage-table portion was behaviorally checked (Amendment A2's 3-arm check, which
      stops at triage with no file writes). See the plan-18 deferred-items entry
      "Synthesize mode has no scenario verification," which this remains true of.
- [x] derive-roadmap's gap rubric, roadmap artifact (Req 9 header, ROUTING lines,
      stage-spec Rollout lifecycle lines), and single-stage exit verified against the
      round-trip spec. Plan 19's core result: Task 3 verified identical stamp wording
      byte-for-byte; Task 6 ran the skill for real against the gold master and produced a
      12-stage artifact with the header verbatim, matching ROUTING/Consumes/Produces/Exit
      fields, graded 7-agree/1-diverge-with-rationale/0-diverge-without against the gold
      master's own sequencing; Task 5 confirmed the single-stage exit 3/3 against this
      repo's own spec as fixture.
- [x] NOTICE, CLAUDE.md bullet + count, and README updated in the same commits as the
      skills they describe. Plan 18 Task 3 (Skill A) and plan 19 Task 2 Step 9 (Skill B)
      each landed provenance in the same commit as their SKILL.md; check_provenance.py
      green throughout.
- [x] Amendment A2 verified behaviorally (2026-07-26), fresh agents running Synthesize
      mode stopped at triage: the real no-push-back review read as first-pass 2/2; an
      adjudicated variant of it read as adjudicated 1/1; a PRE-SKILL critique carrying
      push-back traces but no routing header and no C-numbers read as adjudicated 2/2,
      both agents citing push-back as the signal and explicitly discounting the absent
      header. The third arm is the discriminating one — the first two share a
      routing-header confound and would have passed a skill keying on the wrong signal.
- [ ] A1, A3 and A4 have no dedicated behavioral check. A3's fallback was exercised
      incidentally (both arm-C agents declared a custom locator scheme unprompted); A1
      and A4 rest on the gold master alone.

## Out of scope

- Any edit to the step-3 chain (brainstorming, writing-plans, subagent-driven-development,
  executing-plans) — the in-artifact carrier (Req 10) exists precisely to avoid it; the
  one-line writing-plans hook is the recorded fallback if the carrier proves fragile.
- DL/NLP generalization — deferred with design sketches (Req 15).
- The in-session lighter-weight SOTA pass (WebSearch + paper-search MCP + llm-wiki query
  as a Chat-alternative for module-level work) — YAGNI'd to deferred_items at plan
  completion; the Chat Research round-trip is the practice.
- Mechanical enforcement of the docs-writer exclusion (hooks) — prose contract only,
  matching the reviewer-agent precedent.
- Wiki schema/format ownership — llm-wiki's SCHEMA.md governs; Req 6 only routes to it.

## Rollout note

Plan #1 (next id at planning time) can go straight to writing-plans — this spec's open
items are settled. The between-plans human round-trip (Req 13) is the gate for plan #2;
do not write plan #2 before its fixtures exist. This spec stays live in specs/ until both
plans complete; it retires with the second plan under the standard protocol. The
superseded working draft (specs/methodology-skills-draft.md, never committed) was deleted
when this spec landed.
