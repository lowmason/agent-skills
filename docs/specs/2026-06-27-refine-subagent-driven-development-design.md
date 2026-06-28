# Design: Refine `subagent-driven-development` (Model Selection + dedup)

**Date:** 2026-06-27
**Skill:** `subagent-driven-development/SKILL.md` (this repo; a namespace-stripped fork of obra/superpowers, MIT)
**Status:** spec — awaiting user review before writing the implementation plan

## Problem

The user wants to refine the skill, with three stated goals: trim bloat/redundancy,
change the process (specifically **model selection**), and improve clarity. The
model-selection concern was the driver: *which* models it uses and *how the controller
decides* which tier a task warrants. The user named four sub-worries — scattered criteria,
abstract tiers with no real model names, defaults skewing wrong, and tension between the rules.

## RED baseline (the evidence that scopes this work)

Per the writing-skills Iron Law, no skill change without a failing test first. Two baselines
were run with fresh controllers dispatched on Opus (the user's real controller tier).

**Baseline #1** — 5 reps, clear boundary tasks, model lineup supplied, current guidance:
100% convergence (A→Haiku, B→Sonnet, C→Opus, 5/5 each).

**Baseline #2** — 4 scored reps, the **real** Model Selection section verbatim (abstract tiers,
no lineup given), with three tasks built to sit *on* the rule conflicts; controllers asked to
name a concrete model:
- A (complete code, 1 file) → Haiku (4/4)
- C (open design) → Opus (4/4)
- D (1 file, **prose-only**) → Sonnet (4/4) — prose floor beats "1-2 files→cheap"
- E (1 file, **subtle concurrency**) → Opus (4/4) — risk beats "single-file→cheap"
- F (4 files, mechanical-after-pattern) → Sonnet (4/4) — integration beats "mechanical→cheap"

**Findings:**
- Tier selection is **not broken** — 100% convergence across 9 reps and 8 tasks, including all
  three fault-lines. Controllers resolve the apparent rule tension with a consistent precedence:
  **risk/subtlety > prose-vs-complete-code > file-count.** This precedence is implicit in the
  skill today (agents infer it; a human reader can't see it).
- The **one measured failure**: with abstract tiers and no named lineup, controllers instantiate
  the tier from their own knowledge, and **1/4 reps emitted a stale model ID**
  (`claude-sonnet-4-5` instead of `claude-sonnet-4-6`). This is the "abstract tiers, no real
  models" complaint — the only one of the four worries with empirical support.

**Verdict on the four worries:** #2 (name real models) — real, fixable. #1 (scattered) and
#3 (defaults wrong) — did not reproduce. #4 (tension) — a *readability* problem, not a behavior
problem.

Full data: `scratchpad/sdd-baseline/findings.md` (session scratchpad).

## Decisions

- **Scope:** surgical rewrite of Model Selection + behavior-preserving dedup elsewhere. (Not a
  full logic rewrite — the logic scores 100%, so a replacement must *match* that, not just read
  cleaner.)
- **Portability:** tier-class + pinned concrete IDs in one labeled block.
- **Lineup (user's work env):** cheap = Haiku 4.5 (`claude-haiku-4-5`), standard = Sonnet 4.6
  (`claude-sonnet-4-6`), capable = Opus 4.6 (`claude-opus-4-6`). No Fable 5.
- **Discipline-rule dedup:** collapse the "don't pre-judge the reviewer" repetition to one
  canonical statement + a Red-Flags pointer, then **pressure-re-test** it still holds.

## Part 1 — rewritten Model Selection section

Keeps every signal the baseline proved works; adds the named lineup, makes the measured
precedence explicit, folds the rule tension into one principle, and states a default.
~250 words (current ~330).

```markdown
## Model Selection

Pick the **cheapest tier that can one-shot the task without a re-loop.** A model
that takes 2-3× the turns, or comes back wrong and needs a re-dispatch, costs
more than the tier above it — so when a task sits between tiers, go up one.
Turn count and rework dominate sticker price.

**Tiers** (update these IDs when the lineup changes):
- **cheap** — Haiku 4.5 (`claude-haiku-4-5`)
- **standard** — Sonnet 4.6 (`claude-sonnet-4-6`)
- **capable** — Opus 4.6 (`claude-opus-4-6`)

**Always specify the model explicitly when dispatching.** An omitted model
inherits your session's model — usually the most capable and most expensive —
silently defeating this section.

**Choosing the tier — read the signals in order; the first that fires wins:**
1. **Risk / subtlety** — concurrency, security, data-loss, broad blast radius,
   or debugging from symptoms → **capable**, regardless of file count or diff size.
2. **Source of the work** — the complete code is in the brief (transcription +
   testing) → **cheap**; behavior is described in prose → **standard floor**
   (prose implementers never get the cheap tier).
3. **Spread** — 1-2 files with a clear spec → **cheap**; multiple files /
   integration / pattern-matching → **standard**; open design judgment or
   broad-codebase understanding → **capable**.

When nothing clearly fires, default to **standard** — the floor that absorbs the
cost of one wrong cheap pick.

**Reviews** floor at **standard** and scale up with the diff: a small mechanical
diff reviews at **standard**, a subtle or risky change at **capable**. The
**final whole-branch review is always capable** — dispatch it explicitly, not on
the session default.
```

The numbered order *is* the precedence baseline #2 measured.

### Signal-preservation map (nothing dropped vs. the current section)
- "least powerful that can handle it" → reconciled into the lead principle (cheapest that one-shots).
- mechanical→cheap / integration→standard / architecture→capable → signal 3.
- final review = most capable → Reviews paragraph.
- review scaled to diff risk → Reviews paragraph.
- always specify explicitly → kept verbatim in intent.
- turn count beats token price (2-3× turns) → lead principle.
- mid-tier floor for prose + reviewers → signal 2 + Reviews.
- complete-code → cheapest → signal 2.
- single-file mechanical → cheapest, with subtlety override → signals 1 + 3.

## Part 2 — dedup sweep (behavior-preserving)

| Repeat | Current locations | Plan |
|---|---|---|
| `BASE` not `HEAD~1` warning | Handling Implementer Status (DONE bullet); Constructing Reviewer Prompts (review-package bullet) | State once in the review-package contract under File Handoffs; reference from Handling Implementer Status |
| File-handoff mechanics (review-package, task-brief, report files, reviewer inputs, fix-report appends) | Split across **Constructing Reviewer Prompts** and **File Handoffs** | Consolidate ALL artifact-movement mechanics into **File Handoffs**; leave **Constructing Reviewer Prompts** to own only the prompt *content/judgment* rules; replace the diff-as-file bullet there with a one-line pointer |
| "Don't pre-judge / tell reviewer what not to flag / pre-rate severity" | Canonical in Constructing Reviewer Prompts; near-duplicate in Red Flags (+ adjacent plan-mandated material) | Keep the canonical (with its "if your prompt contains 'do not flag'… stop" rationalization framing); trim Red Flags to a true one-line pointer; do not weaken |

**Section split after merge:**
- **Constructing Reviewer Prompts** = what goes *in* the prompt (no open-ended directives; don't
  re-run the implementer's tests; don't pre-judge; the global-constraints block; dispatch-fix
  policy; plan-mandated = human decision).
- **File Handoffs** = how artifacts *move* (task-brief; review-package + the single BASE/HEAD~1
  rule; report file naming; the reviewer's three input paths; fix-report appends; final-review
  package).

## Part 3 — verification (GREEN / REFACTOR; run as Workflows, ultracode on)

1. **No-regression on model selection.** Re-run both baselines (clear + fault-line tasks)
   against the rewritten section. Pass criteria:
   - tier convergence stays at 100% and each task lands on the same correct tier as baseline;
   - the mid-tier task yields `claude-sonnet-4-6` (not a stale `4-5`) now that the lineup is named.
2. **Completeness audit of the dedup.** Inventory every rule in the current SKILL.md; confirm
   each survives in the rewrite (the signal-preservation map plus a rule-by-rule diff). Confirm
   word count dropped.
3. **Pressure re-test of the don't-pre-judge rule.** Pressure scenario (time pressure + a finding
   the controller would rather suppress to skip a review loop); confirm the trimmed form still
   refuses to pre-judge. If it weakens, restore the repetition.

## Non-goals / out of scope
- No full rewrite of the decision logic (baseline says it works).
- No change to the per-task two-verdict review structure, the continuous-execution rule, the
  progress-ledger mechanism, or any other section beyond Model Selection and the named dedups.
- No Fable 5 (not in the user's work lineup).
- The cache-copy at `~/.claude/plugins/cache/.../6.0.3/` is not edited — it is overwritten on
  plugin update; this repo is the source of truth.

## Success criteria
- Model Selection names the lineup, states the precedence + principle + default, preserves every
  working signal, and is shorter than the current section.
- Re-run baselines: 100% correct tier convergence maintained; no stale model IDs.
- Dedup: no rule lost (completeness audit passes); SKILL.md word count reduced.
- Don't-pre-judge rule passes its pressure re-test after trimming.
```
