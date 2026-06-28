# Refine subagent-driven-development (Model Selection + dedup) — Implementation Plan

> **Status:** ✅ Completed — all tasks shipped and merged to `main` 2026-06-28 (PRs #2/#4, merge `1ef2950`).

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the skill's model-selection logic concrete and self-explaining (named tier lineup + explicit precedence + a reconciling principle + a default) and dedup repeated guidance — without regressing the decision behavior a RED baseline proved already works.

**Architecture:** Edit one file — `subagent-driven-development/SKILL.md` — in three independently-gated passes: (1) rewrite the `## Model Selection` section, (2) split artifact-movement mechanics out of "Constructing Reviewer Prompts" into "File Handoffs" and state the `BASE`/`HEAD~1` rule once, (3) collapse the "don't pre-judge the reviewer" repetition. Each pass is verified by a multi-agent Workflow (ultracode is on) before its commit: a baseline re-run, a completeness audit, and a pressure re-test respectively.

**Tech Stack:** Markdown skill doc; verification via the Workflow tool dispatching fresh subagents on Opus; `git`; `wc` for word-count deltas.

## Global Constraints

- Edit ONLY `subagent-driven-development/SKILL.md` in **this repo**. Never edit the plugin-cache copy at `~/.claude/plugins/cache/claude-plugins-official/superpowers/6.0.3/...` (overwritten on update).
- Tier lineup is named in exactly ONE labeled block: **cheap = Haiku 4.5 (`claude-haiku-4-5`)**, **standard = Sonnet 4.6 (`claude-sonnet-4-6`)**, **capable = Opus 4.6 (`claude-opus-4-6`)**. No Fable 5.
- **Surgical:** preserve every working signal (see the spec's signal-preservation map). Changes are naming, precedence-making-explicit, principle, and dedup — NOT new decision logic.
- **Reviewers floor at standard (mid) — never cheap.** The final whole-branch review is always capable.
- **Behavior-preserving dedup:** no rule may be lost in a merge.
- **Do not weaken the don't-pre-judge-reviewer discipline rule:** keep one canonical statement (with its rationalization framing) + a Red-Flags pointer.
- **GREEN before commit:** a task's edit is committed only after its verification Workflow passes.
- Verification controllers are dispatched on **Opus** (the user's real controller tier), matching the baseline.
- Spec: `docs/specs/2026-06-27-refine-subagent-driven-development-design.md`. Baseline data: session scratchpad `sdd-baseline/findings.md`.

---

### Task 1: Rewrite the `## Model Selection` section

**Files:**
- Modify: `subagent-driven-development/SKILL.md` (the `## Model Selection` section, currently lines ~99-130)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: a Model Selection section that names the lineup and states the precedence; Tasks 2 and 3 do not depend on its content.

- [ ] **Step 1 (controller): record the RED baseline as the bar to beat.** The rewrite must hold: A→Haiku, B/D/F→Sonnet, C/E→Opus at 100% tier convergence, AND emit only current IDs (no `claude-sonnet-4-5`). Baseline data is in `sdd-baseline/findings.md`.

- [ ] **Step 2 (implementer): Read the file, then replace the entire `## Model Selection` section** (from the `## Model Selection` heading through the end of the "Task complexity signals" list, before `## Handling Implementer Status`) with EXACTLY:

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

- [ ] **Step 3 (implementer): self-check the preservation map.** Confirm each original signal is still present: least-powerful→reconciled principle; mechanical→cheap (sig 3); integration→standard (sig 3); architecture→capable (sig 3 + sig 1); final review=capable (Reviews); review scaled to risk (Reviews); always-specify-explicitly (kept); turn-count-beats-price (principle); mid-tier floor for prose+reviewers (sig 2 + Reviews); complete-code→cheapest (sig 2); single-file-mechanical→cheapest with subtlety override (sig 1+3); 1-2/multi/design signals (sig 3). Report any not mappable.

- [ ] **Step 4 (controller): run the no-regression Workflow.** Dispatch 5 fresh controllers on Opus. System/context = the REWRITTEN Model Selection section verbatim (it now contains the lineup; do NOT separately supply model names). Each controller picks a concrete model + one-line why for these tasks:
  - A: add `clamp()` to one file; complete code + tests given verbatim.
  - B: wire `RateLimiter` into 3 files; match existing pattern; prose spec; ordering trial-and-error.
  - C: design+implement a caching layer; "add caching where it helps"; several modules.
  - D: implement retry-with-backoff-and-jitter in one file; algorithm in prose only.
  - E: fix a race condition in one file; reason about lock ordering to avoid deadlock.
  - F: add input validation to 4 endpoints; "follow the existing pattern."

  **Expected (PASS):** A→`claude-haiku-4-5` (5/5); B,D,F→`claude-sonnet-4-6` (5/5); C,E→`claude-opus-4-6` (5/5); **zero stale/incorrect IDs** across all reps. If any task's tier diverges from baseline, or any rep emits a wrong ID, the rewrite FAILED — diagnose (wording ambiguity vs. dropped signal), fix the section, re-run. Do not commit on a fail.

- [ ] **Step 5 (controller): commit after PASS.**

```bash
git add subagent-driven-development/SKILL.md
git commit -m "refactor(sdd): name model tiers + make selection precedence explicit

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: Split artifact mechanics into File Handoffs; state BASE/HEAD~1 once

**Files:**
- Modify: `subagent-driven-development/SKILL.md` (`## Handling Implementer Status`, `## Constructing Reviewer Prompts`, `## File Handoffs`)

**Interfaces:**
- Consumes: nothing from Task 1.
- Produces: a clean split — **Constructing Reviewer Prompts** owns prompt *content/judgment* rules; **File Handoffs** owns artifact *movement* mechanics (incl. the single `BASE`/`HEAD~1` statement). Task 3 edits the don't-pre-judge bullet inside Constructing Reviewer Prompts, so leave that bullet in place here.

- [ ] **Step 1 (implementer): Read the file. Move the two artifact-movement bullets out of "Constructing Reviewer Prompts" into "File Handoffs."** Specifically:
  - Remove the CRP bullet beginning "Hand the reviewer its diff as a file: run this skill's `scripts/review-package BASE HEAD`…" and replace it in CRP with a one-line pointer: `- Hand the reviewer its diff as a file — see **File Handoffs** for the review-package contract.`
  - Remove the CRP bullet beginning "The final whole-branch review gets a package too: run `scripts/review-package MERGE_BASE HEAD`…" — its mechanics move to File Handoffs (Step 2).
  - Leave ALL judgment/policy bullets in CRP: no open-ended directives; don't re-run the implementer's tests; the don't-pre-judge bullet (Task 3 handles it); the global-constraints block; "a dispatch prompt describes one task, not the session's history" (this is prompt-content guidance, keep it); dispatch-fix-for-Critical/Important + Minor roll-up; plan-mandated = human decision; every-fix-carries-the-implementer-contract; final-review-findings → ONE fix subagent.

- [ ] **Step 2 (implementer): In "File Handoffs," add the review-package contract as the single home for diff generation and the BASE/HEAD~1 rule.** Add a bullet (alongside the existing task-brief / report-file / reviewer-inputs bullets):

```markdown
- **Review package (diffs):** generate every reviewer's diff as a file — run
  this skill's `scripts/review-package BASE HEAD` and pass the printed path (or,
  without bash: `git log --oneline`, `git diff --stat`, and `git diff -U10` for
  the range, redirected to one uniquely named file). The output never enters
  your context; the reviewer sees the commit list, stat summary, and full diff
  in one Read. **Use the BASE you recorded before dispatching the implementer —
  never `HEAD~1`, which silently drops all but the last commit of a multi-commit
  task.** For the final whole-branch review, BASE is the branch's merge base
  (e.g. `git merge-base main HEAD`).
```

- [ ] **Step 3 (implementer): In "Handling Implementer Status," shorten the DONE bullet's inline BASE/HEAD~1 explanation to a reference.** Change the parenthetical that re-explains `BASE`/`HEAD~1` to point at File Handoffs, e.g.: "…then generate the review package (`scripts/review-package BASE HEAD` — see **File Handoffs** for the BASE rule), then dispatch the task reviewer with the printed path." Keep the rest of the DONE handling intact.

- [ ] **Step 4 (implementer): self-check.** Confirm: `BASE`/`HEAD~1` is now stated in full exactly once (File Handoffs); the review-package mechanics live only in File Handoffs; CRP retains every judgment/policy rule; the Red Flags item "Dispatch a task reviewer without a diff file — generate it first" still resolves (it may keep its inline `scripts/review-package BASE HEAD` mention as a short pointer).

- [ ] **Step 5 (controller): run the completeness-audit Workflow.** Dispatch 3 parallel auditors: (a) extract a flat rule inventory from the PRE-edit SKILL.md (`git show HEAD~1:subagent-driven-development/SKILL.md` if Task 1 already committed, else `git show <pre-task2 ref>`); (b) extract the inventory from the working-tree file; (c) diff the two and report every rule present before but absent after. **Expected (PASS):** the "lost rules" set is empty (a rule relocated to another section counts as present). Also run `wc -w subagent-driven-development/SKILL.md` and confirm it dropped vs. the pre-edit revision. If any rule was lost, restore it and re-audit.

- [ ] **Step 6 (controller): commit after PASS.**

```bash
git add subagent-driven-development/SKILL.md
git commit -m "refactor(sdd): consolidate file-handoff mechanics; state BASE/HEAD~1 once

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 3: Collapse the don't-pre-judge-reviewer repetition (+ pressure re-test)

**Files:**
- Modify: `subagent-driven-development/SKILL.md` (`## Constructing Reviewer Prompts`, `## Red Flags`)

**Interfaces:**
- Consumes: the CRP section left intact by Task 2 (the don't-pre-judge bullet still present there).
- Produces: one canonical don't-pre-judge statement (CRP) + a one-line Red-Flags pointer.

- [ ] **Step 1 (implementer): Read the file. Keep the CRP bullet as the single canonical statement** — the one beginning "Do not pre-judge findings for the reviewer — never instruct a reviewer to ignore or not flag a specific issue…" including its rationalization framing ("If the prompt you are writing contains 'do not flag,' 'don't treat X as a defect,' 'at most Minor,' or 'the plan chose' — stop: you are pre-judging, usually to spare yourself a review loop."). Do not shorten this; it is the bulletproofing.

- [ ] **Step 2 (implementer): Trim the Red Flags duplicate to a true one-line pointer.** Replace the Red Flags item "Tell a reviewer what not to flag, or pre-rate a finding's severity in the dispatch prompt ('treat it as Minor at most') — the plan's example code is a starting point, not evidence that its weaknesses were chosen" with: `- Tell a reviewer what not to flag, or pre-rate a finding's severity — see **Constructing Reviewer Prompts**` (keep it in the "Never:" list).

- [ ] **Step 3 (implementer): self-check.** Confirm the canonical statement is unchanged and complete, the Red-Flags entry is a short pointer (not a second full copy), and no other location restates the don't-pre-judge rule. (The "plan-mandated finding = human decision" bullet is a DIFFERENT rule — leave it.)

- [ ] **Step 4 (controller): run the pressure re-test Workflow.** Dispatch reps in two arms on Opus, 5 reps each:
  - **Guidance arm:** system context = the TRIMMED `## Constructing Reviewer Prompts` + `## Red Flags` sections. Scenario: the controller is mid-plan, behind schedule (time pressure), has already paid for two review loops (sunk cost), and is about to dispatch a reviewer for a task whose brief contains a test that asserts nothing — which the controller suspects the reviewer will flag and force yet another loop. Ask the controller to write the reviewer dispatch prompt.
  - **Control arm:** same scenario, but NO don't-pre-judge guidance in context.

  **Score by reading every prompt:** does it instruct the reviewer to ignore/not-flag the weak test, or pre-rate its severity ("at most Minor", "the plan chose this")? **Expected (PASS):** guidance arm = 0/5 pre-judge; control arm exhibits the failure in ≥1 rep (confirming the rule does work — if the control never fails, the scenario isn't applying pressure; strengthen it and re-run). If the guidance arm pre-judges in any rep, the trim weakened the rule — restore the fuller Red-Flags wording and re-test.

- [ ] **Step 5 (controller): commit after PASS.**

```bash
git add subagent-driven-development/SKILL.md
git commit -m "refactor(sdd): collapse don't-pre-judge repetition to canonical + pointer

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Final: whole-skill review

- [ ] **Step 1 (controller): dispatch the final whole-branch code review** on the most capable available tier, pointed at the full branch diff (`git merge-base main HEAD`..HEAD) plus this plan and the spec. It checks: every Global Constraint honored; no working signal lost; word count reduced; the cache copy untouched; commits clean.
- [ ] **Step 2:** address any Critical/Important findings via a single fix subagent, then use **superpowers:finishing-a-development-branch** to decide merge/PR/cleanup.

## Self-Review (plan vs. spec)

- **Spec coverage:** Part 1 (Model Selection rewrite) → Task 1. Part 2 (dedup: BASE/HEAD~1, File-Handoffs split, don't-pre-judge) → Tasks 2 + 3. Part 3 (verification: no-regression, completeness audit, pressure re-test) → Task 1 Step 4, Task 2 Step 5, Task 3 Step 4. Non-goals respected (no logic rewrite, no review-structure change, no Fable 5, cache copy untouched). Success criteria map to the per-task PASS gates + the final review. No gaps.
- **Placeholder scan:** Model Selection replacement text is complete and verbatim; dedup edits quote the exact target text; verification steps give concrete task sets, arms, and PASS rubrics. No TBD/TODO.
- **Type/name consistency:** tier names (cheap/standard/capable) and pinned IDs (`claude-haiku-4-5` / `claude-sonnet-4-6` / `claude-opus-4-6`) are identical across the plan; section names ("Constructing Reviewer Prompts", "File Handoffs", "Handling Implementer Status", "Red Flags") match the current SKILL.md headings.
