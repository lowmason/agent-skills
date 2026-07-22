# clean-code-family — Design Spec

**Status: PROPOSED (2026-07-22)** — approved in brainstorming; next step
`writing-plans` (plan id: next integer across `specs/plans/` + `specs/plans/completed/`).

## Motivation — the gap

`tech-debt` already covers the **audit angle**: a periodic, read-only sweep of a
codebase that classifies findings, makes the DELETE/HARDEN call, and hands back a
prioritized backlog. It is a batch activity you *invoke* on a repo.

There is no counterpart for the **proactive-cleanup angle** — clean code produced
in the flow of normal work: applying clean-code standards to code as you write it,
and opportunistically improving adjacent code you happen to touch ("leave it a
little cleaner than you found it"), bounded by a consent gate so it never sprawls
into an unrequested refactor. ytran14's dotfiles ship this as a "clean-code family"
(`boy-scout` + `python-clean-code` + five `clean-*` sub-skills) grounded in Robert
C. Martin's *Clean Code* rule catalog.

Separately, the repo's `.claude/rules/python-ml.md` was **deleted**. Its *Style*
section overlapped exactly with clean-code standards; its *ML-Safety*, *Bloomberg*,
and *Data* sections are load-bearing stack guardrails with no other home. Replacing
that file's enforcement role is an explicit goal of this work.

## Goal

Ship a proactive-cleanup complement to `tech-debt`, adapted from ytran14's
clean-code family to this repo's stack (Polars / NumPyro / JAX / BLS-ETL) and
conventions, with honest provenance to both Martin and ytran14; and re-home the
non-style guardrails orphaned by the `python-ml.md` deletion.

## Artifacts

Three artifacts — one behavioral, two reference:

| # | Artifact | Type | Path | Pressure-tested? |
|---|----------|------|------|------------------|
| 1 | `clean-coder` | behavioral discipline skill | `.claude/skills/clean-coder/SKILL.md` | **Yes** |
| 2 | `clean-code` | reference skill | `.claude/skills/clean-code/SKILL.md` + `references/*.md` | No |
| 3 | `python-ml-safety` | path-glob rule | `.claude/rules/python-ml-safety.md` | No |

**Design decisions locked in brainstorming:**
- **C** — build both the behavioral discipline *and* the standards it applies.
- **G1** — two skills (behavior + one reference with `references/`), not ytran14's
  7-skill family and not a single mega-skill. Respects `writing-skills`'
  discipline-vs-reference split and the repo's `SKILL.md + references/` pattern.
- **Decision A** — the orphaned guardrails become a **path-glob rule** (always-on
  injection on `**/*.py`), not a third reference skill.
- **Decision B** — `clean-code` carries a **curated, stack-tuned subset** of
  Martin's catalog, retaining the rule *codes* for citation, not the full catalog.

## Artifact 1 — `clean-coder` (behavioral skill)

Ported from ytran14's `boy-scout`; the only behavioral artifact.

- **Frontmatter:** `name: clean-coder`; a single dense `description` starting
  "Use when…", packed with triggers (editing / fixing / refactoring Python;
  "while you're at it", "any quick wins", "anything else obviously wrong").
  **Drop** ytran14's non-standard `when_to_use:` block — fold its phrases into the
  `description` (repo convention; `build/check_frontmatter.py` enforces the shape).
- **Content:**
  - *Philosophy* — leave each file a little cleaner; proportional to the task; one
    small improvement per edit; never a crusade.
  - **The Confirmation Gate (load-bearing):**
    - *In-scope code* (what you're editing for the task) → apply `clean-code`
      standards directly, no confirmation.
    - *Adjacent / out-of-scope code* → (1) announce clean-coder engaged, (2) list
      each proposed cleanup with `file:line` + rule code, (3) ask, (4) apply only
      on explicit yes; if declined, leave untouched. Never expand scope silently.
  - *Routing table* — task → where to look in `clean-code` (naming → names;
    dead/redundant comment → comments; long or multi-arg function → functions;
    DRY / magic number / Demeter → general; coverage gap → tests).
  - *Report format* — every fix cited by rule code (e.g. "Fixed: extracted
    `SECONDS_PER_DAY` (G25)").
- **Boundary vs `tech-debt` (explicit section):** clean-coder is edit-triggered and
  incremental and **produces no backlog**. When it notices debt beyond an
  opportunistic in-scope/adjacent fix (duplicated-repo ambiguity, a notebook
  needing extraction, a security finding), it **stops and defers to `tech-debt`**
  rather than fixing in-flow. Referenced by bare skill name.
- **Interactions:** honors `test-driven-development` (a cleanup that changes
  behavior gets a test first) and the repo's commit conventions.
- **Pressure-testing:** micro-tested against a no-guidance baseline before
  deployment, per `writing-skills`; the scope-discipline of the Gate is the
  behavior under test. This is an implementation gate, not done at spec time.

## Artifact 2 — `clean-code` (reference skill)

- **Frontmatter:** `name: clean-code`; dense `description` ("Use when writing,
  editing, reviewing, or refactoring Python — naming, functions, comments, DRY,
  tests…"). No `when_to_use:` block. Reference skill → **not** pressure-tested.
- **Layout (`SKILL.md + references/`):**
  - `SKILL.md` = master index — the curated numbered catalog (Martin's
    C/E/F/G/N/P/T codes) as one-liners, a quick-reference table, an anti-patterns
    (Don't → Do) table, and the "cite fixes by rule code" convention.
  - `references/names.md`, `comments.md`, `functions.md`, `general.md`, `tests.md`
    = per-category detail with **bad/good examples in this repo's stack** (Polars,
    NumPyro/JAX, httpx ETL — not generic Java-flavored Python), loaded on demand.
    This collapses ytran14's five `clean-*` skills into one skill's references.
- **Curated scope (Decision B):** keep the high-value rules that bite in
  Polars/NumPyro/ETL work — e.g. G5 (DRY), G23 (polymorphism over if/elif chains),
  G25 (named constants), G30 (one thing), G36 (Law of Demeter); N1–N7; F1–F4;
  C1–C5; the T-rules that matter for pytest — and drop the filler. Rule codes are
  retained so citations stay stable.

## Artifact 3 — `python-ml-safety` (path-glob rule)

Re-homes the non-style content orphaned by the `python-ml.md` deletion.

- **Path:** `.claude/rules/python-ml-safety.md`; glob `**/*.py`.
- **Content:** carry over python-ml.md's **ML-Safety** (fit scalers/encoders on
  train only; seed before training; `torch.no_grad()` in eval; `.item()` when
  logging scalars; `log(x + eps)`; `F.log_softmax`), **Bloomberg Conventions**,
  and **Data** sections — **minus** the *Style* section, which is now `clean-code`'s
  responsibility.

## Provenance

The repo is meticulous about attribution; this content is *not* a Lowell original.

- Cite Martin's rule **codes/structure** and write **original prose + original
  stack examples** — no verbatim *Clean Code* text (same discipline as the PML
  "cite, don't redistribute" rule for `recommend-probabilistic-model`).
- `NOTICE` gets a **new, dedicated block** (not folded into "Lowell's originals"):
  adapted from **ytran14's dotfiles clean-code family**; rule catalog concept from
  **Robert C. Martin's *Clean Code*** (cited by rule code; no prose redistributed).
  Lists `clean-coder` and `clean-code`. Our authored text is MIT.
- Cross-skill references use **bare skill names** (`tech-debt`, `clean-code`), never
  a plugin namespace (repo invariant).

## Repo integration

- **Dangling-reference cleanup (from the python-ml.md deletion):**
  - `.claude/CLAUDE.md` — remove `python-ml` from the `.claude/rules/` inventory;
    add `python-ml-safety`; add `clean-coder`/`clean-code` to the skills line.
  - `README.md` — same inventory fixes + new skill row(s).
  - Apply to the global copy too if synced.
- **Lints / gates (existing, must pass):** `build/check_frontmatter.py` for both
  new skills; `build/check_provenance.py` with the new NOTICE entries.
- **No new build tooling** — these are prose skills, no scripts (matching ytran14
  and unlike the repo's script-bearing skills). No `scan.sh` analogue.

## Out of scope (YAGNI)

- No sweep script, backlog, or scoring (that's `tech-debt`).
- No auto-apply of out-of-scope cleanups without the Confirmation Gate.
- No changes to `tech-debt` beyond a reciprocal cross-reference.
- No resurrection of python-ml.md's *Style* section (superseded by `clean-code`).

## Success criteria

1. `clean-coder` fires on Python edits, applies in-scope cleanups directly, and
   gates every out-of-scope cleanup through announce → list-with-code → ask → apply.
2. `clean-coder` passes its `writing-skills` micro-test vs. a no-guidance baseline.
3. `clean-code` provides the curated, code-cited catalog with stack-specific
   examples in `references/`; auto-loads on Python-writing turns.
4. `python-ml-safety` re-injects the ML-Safety/Bloomberg/Data guardrails on `*.py`.
5. `NOTICE`, `.claude/CLAUDE.md`, and `README.md` are consistent; no dangling
   `python-ml` references; frontmatter + provenance lints pass.
