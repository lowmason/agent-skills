# Recommend Causal Design Implementation Plan

**Status: COMPLETE (2026-10-03)** — executed via executing-plans; nothing deferred.

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans for tightly coupled inline execution. Steps use checkbox syntax for tracking.

**Goal:** Deliver a self-contained recommendation-only causal design skill and its validated implementation handoff.

**Architecture:** A small decision procedure links to an identification guide, method-selection reference, memo template, and verified bibliography. Documentation integration and provenance ship with the skill; no estimators or scripts are introduced.

**Tech Stack:** Markdown/YAML; existing Python 3.13 repository validators via uv; fresh agent application tests.

## Global Constraints

- Markdown-only skill: short `SKILL.md`, focused `references/`, and `README.md`.
- No estimator scripts, bundled papers/books, numerical grading thresholds,
  PyMC dependency, or generated runtime-adapter changes.
- Cross-skill handoffs use bare names; the skill is self-contained and reads
  no sibling files. Installer dependency tables need no new edge.
- Preserve unrelated existing work in `specs/jax-deep-learning-skills.md` and
  `specs/plans/32-jax-deep-learning-skills.md`.
- Work starts after commit `3abece1` on `codex/recommend-causal-design`.

### Task 1: Recommendation workflow, references, and memo contract

**Files:** Create `skills/recommend-causal-design/SKILL.md`, `README.md`,
`references/identification.md`, `references/design-map.md`,
`references/reporting.md`, `references/sources.md`, and
`references/worked-example.md`; create evaluation record in
`specs/recommend-causal-design-evaluation.md`.

**Interfaces:** Consumes a question and optional data/metadata; produces
`<analysis-slug>/recommendation.md` with the spec's required fields. Source
references and workflow attribution are self-contained inside the skill.

- [x] Run a no-guidance application baseline before drafting skill text; record exact omissions and strengths.
- [x] Run five fresh-context no-guidance samples; manually score their causal correctness and handoff/DAG completeness.
- [x] Verify primary bibliography and pin upstream source commits/license notices.
- [x] Write a trigger-only description, clear boundaries and the decision procedure; keep method detail in references.
- [x] Add explicit requested/supported estimand fields, status, DAG, assumption/evidence/gap table, candidate comparison, diagnostic plan, and handoff slots.
- [x] Add a worked cutoff-design example that keeps a local effect separate from a national ATE and treats missing outcomes as an identification issue.
- [x] Run five fresh-context guidance samples against the same baseline request and read every result.
- [x] Exercise missing overlap, staggered DiD, and longitudinal confounding; fix actual gaps and rerun affected cases.
- [x] Verify name/description limits, useful keyword coverage, no workflow in description, correct reference links, compact body, quick reference table and common mistakes.

### Task 2: Attribution, registration, installation, and review

**Files:** Modify `NOTICE`, `README.md`, and `CLAUDE.md`; create
`LICENSE-causal-design-sources`. Installer discovery should require no code
change. Keep the existing original-skill count at sixteen because this is an
adapted workflow with its own attribution block.

**Interfaces:** Existing `install.py --skill recommend-causal-design` discovers
the directory; canonical skill text is portable across all three runtimes.

- [x] Register the skill in README's skill table and credits; add a distinct NOTICE entry with adaptation scope and pinned sources; preserve both full MIT notices.
- [x] Run `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py` (expect exit 0).
- [x] Run `uv run --python 3.13 python build/check_provenance.py` (expect exit 0).
- [x] Run `uv run --python 3.13 python build/check_snippets.py skills/` (expect exit 0).
- [x] From `build/`, run `uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py test_check_provenance.py test_runtime_support.py` (expect all pass).
- [x] Verify source/link portability and a selected-skill install into a temporary runtime root; install personal links with the existing installer after validation.
- [x] Run independent whole-change review against this spec and a read-only Codex second opinion; resolve justified findings and rerun relevant checks.
- [x] Commit only this task's files; run the completion protocol, record test evidence, retire spec/plan/evaluation, and deliver the skill and invocation example.

## Authoring checklist decisions

The skill is a technique plus reference guide. Output omissions use required
memo fields, not a discipline rationalization table. Pure bibliographic and
method reference content receives retrieval/application review; workflow
wording receives fresh baseline and guidance samples. There is no meaningful
5–10 line business-code contribution because no code is being authored.

## Completion evidence

Feature commit: `9903950`. Five fresh controls and five fresh guided samples
showed graph/handoff contract uptake; three distinct design cases passed.
Independent review found one RD continuity wording issue, corrected against the
primary source and confirmed resolved on re-review. All three lints and 108
tests passed after the fix. Complete copy installation and personal links were
verified. Evaluation and read-only backlog proposal are retired beside the spec.

> Deviation: execution continued in this approved conversation for a tightly
> coupled markdown deliverable. The spec and plan were saved before authoring
> and committed with the implementation; no extra approval round was introduced
> for the already approved scope.

> Deviation: the Codex second opinion was skipped because the controller is
> Codex, as required by requesting-code-review's Codex review recipe. The
> dedicated code-reviewer role was unavailable; a fresh default agent ran the
> same read-only review contract and a targeted correction re-review.

Deferred backlog: 13 open, 92 ever closed (88% closure), 2 aged >45d; oldest 69d.
No prior item was completed by this scope. A read-only grouped proposal is in
the retired backlog-triage record; no disposition or acknowledgement was made.
