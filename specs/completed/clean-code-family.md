# clean-code-family — Design Spec (REVISED)

**Status: PROPOSED (2026-07-22; revised 2026-07-24)** — approved in brainstorming; next step `writing-plans` (plan id: next integer across `specs/plans/` + `specs/plans/completed/`).

> **Revision note (2026-07-24):** This revision augments and corrects the PROPOSED spec against (1) the primary source — Martin's Chapter 17 "Smells and Heuristics" catalog, verified rule-by-rule — and (2) a survey of comparable Claude Code skill implementations and the critical/complementary literature (Beck's *Tidy First?*, Ousterhout's *A Philosophy of Software Design*, Fowler's opportunistic refactoring, qntm's critique). All locked decisions (C, G1, A, B) are preserved. See the change log at the end.

## Motivation — the gap

`tech-debt` already covers the **audit angle**: a periodic, read-only sweep of a codebase that classifies findings, makes the DELETE/HARDEN call, and hands back a prioritized backlog. It is a batch activity you *invoke* on a repo.

There is no counterpart for the **proactive-cleanup angle** — clean code produced in the flow of normal work: applying clean-code standards to code as you write it, and opportunistically improving adjacent code you happen to touch ("leave it a little cleaner than you found it"), bounded by a consent gate so it never sprawls into an unrequested refactor. This ships as a "clean-code family" grounded in Robert C. Martin's *Clean Code* rule catalog, sharpened by Kent Beck's *Tidy First?* discipline of separating tidying from behavior change.

## Goal

Ship a proactive-cleanup complement to `tech-debt`: a clean-code family tuned to this repo's stack (Polars / NumPyro / JAX / BLS-ETL) and conventions, with honest provenance to Robert C. Martin's *Clean Code*.

## Artifacts

Three artifacts — **one behavioral skill, one reference skill, one always-on path-scoped rule**:

| \# | Artifact | Type | Path | Pressure-tested? |
|------------|------------|------------|------------|------------------------|
| 1 | `clean-coder` | behavioral discipline skill | `.claude/skills/clean-coder/SKILL.md` | **Yes** |
| 2 | `clean-code` | reference skill | `.claude/skills/clean-code/SKILL.md` + `references/*.md` | No |
| 3 | `clean-code-python` | always-on path-scoped rule | `.claude/rules/clean-code-python.md` | No (rule, not a skill) |

**Design decisions locked in brainstorming (preserved):** - **C** — build both the behavioral discipline *and* the standards it applies. - **G1** — two skills (behavior + one reference with `references/`). Respects `writing-skills`' discipline-vs-reference split and the repo's `SKILL.md + references/` pattern. - **Decision A** — the orphaned guardrails become a **path-glob rule** (always-on injection on `**/*.py`), not a third reference skill. (Now Artifact 3 above; the concrete Claude Code mechanism is specified in its own section below.) - **Decision B** — `clean-code` carries a **curated, stack-tuned subset** of Martin's catalog, retaining the rule *codes* for citation, not the full catalog. Curation is now sharpened by a keep / drop / **defer-to-ruff** disposition (below).

## Artifact 1 — `clean-coder` (behavioral skill)

-   **Frontmatter:** `name: clean-coder`; a single dense `description` starting "Use when…", packed with triggers (editing / fixing / refactoring Python; "while you're at it", "any quick wins", "anything else obviously wrong"). **Drop** non-standard `when_to_use:` block — fold its phrases into the `description` (repo convention; `build/check_frontmatter.py` enforces the shape). Per superpowers `writing-skills`: the `description` states *triggering conditions only* — it must not summarize the workflow, or Claude may follow the description instead of reading the skill body.
-   **Content:**
    -   *Philosophy* — leave each file a little cleaner; proportional to the task; one small improvement per edit; never a crusade. This is Fowler's **litter-pickup / boy-scout** mode ("leave the code better than you found it"), not a refactoring project.
    -   **The Confirmation Gate (load-bearing):**
        -   *In-scope code* (what you're editing for the task) → apply `clean-code` standards directly, no confirmation.
        -   *Adjacent / out-of-scope code* → (1) announce clean-coder engaged, (2) list each proposed cleanup with `file:line` + rule code, (3) ask, (4) apply only on explicit yes; if declined, leave untouched. Never expand scope silently.
    -   **Tidy-vs-behavior separation (from *Tidy First?*):** a cleanup that does not change observable behavior is a **tidying** (structural change); a cleanup that changes behavior is a **behavior change**. Never mix the two in one commit. A commit sequence may be `SSSSBBSB` but each commit is atomic and holds exactly one kind. Tidyings that touch behavior require a test first (see TDD interaction).
    -   **Batch-size cap and stopping rule (from *Tidy First?* / opportunistic refactoring):** one tidying tends to reveal another; you must know when to stop. Beck's guidance is concrete — more than roughly an hour of tidying before making any behavioral change usually means you have lost track of the minimum set of structural changes actually needed. Cap opportunistic tidying and defer the rest to `tech-debt` rather than chasing a cascade. If tidying is eating the task rather than serving it, stop.
    -   *Routing table* — task → where to look in `clean-code` (naming → names; dead/redundant comment → comments; long or multi-arg function → functions; DRY / magic number / Demeter → general; coverage gap → tests).
    -   *Report format* — every fix cited by rule code (e.g. "Fixed: extracted `SECONDS_PER_DAY` (G25)").
    -   **Rationalization table (superpowers pattern):** an explicit `Excuse | Reality` table capturing the loopholes the baseline agent uses to skip the Gate (e.g. "It's a tiny change, I'll just fix it" \| "Out-of-scope tiny changes still go through announce→list→ask"), plus a **Red Flags — STOP** list. This mirrors the superpowers method of not just stating the rule but forbidding the specific workarounds an agent invents under pressure.
-   **Boundary vs `tech-debt` (explicit section):** clean-coder is edit-triggered and incremental and **produces no backlog**. When it notices debt beyond an opportunistic in-scope/adjacent fix (duplicated-repo ambiguity, a notebook needing extraction, a security finding, or anything exceeding the batch-size cap), it **stops and defers to `tech-debt`** rather than fixing in-flow. Referenced by bare skill name.
-   **Interactions:**
    -   **`test-driven-development`** — a cleanup that changes behavior gets a test first. A pure tidying (behavior-preserving) does *not* require a new test but must keep the existing suite green; run tests before and after so the tidying is provably behavior-preserving. This mirrors Beck's rule that tidyings are safe precisely because they are verifiable as non-behavioral.
    -   Repo commit conventions — tidying commits and behavior commits stay separate (see above).
-   **Pressure-testing:** micro-tested against a no-guidance baseline before deployment, per `writing-skills` RED→GREEN→REFACTOR. The scope-discipline of the Gate is the behavior under test. Concrete scenarios below. This is an implementation gate, not done at spec time.

## Artifact 2 — `clean-code` (reference skill)

-   **Frontmatter:** `name: clean-code`; dense `description` ("Use when writing, editing, reviewing, or refactoring Python — naming, functions, comments, DRY, tests…"). No `when_to_use:` block. Reference skill → **not** pressure-tested.
-   **Layout (`SKILL.md + references/`):**
    -   `SKILL.md` = master index — the curated numbered catalog (Martin's C/E/F/G/N/T codes) as one-liners, a quick-reference table, an anti-patterns (Don't → Do) table, and the "cite fixes by rule code" convention.
    -   `references/names.md`, `comments.md`, `functions.md`, `general.md`, `tests.md` = per-category detail with **bad/good examples in this repo's stack** (Polars, NumPyro/JAX, httpx ETL — not generic Java-flavored Python), loaded on demand.

### Curated scope (Decision B) — verified catalog with keep / drop / defer-to-ruff

Martin's Chapter 17 catalog (verified rule-by-rule) is: **Comments C1–C5**; **Environment E1–E2**; **Functions F1–F4**; **General G1–G36** (confirmed full range, G1 through G36); **Java J1–J3**; **Names N1–N7**; **Tests T1–T9**. The spec's cited codes are correct: **G5 = Duplication (DRY)**, **G23 = Prefer Polymorphism to If/Else or Switch/Case**, **G25 = Replace Magic Numbers with Named Constants**, **G30 = Functions Should Do One Thing**, **G36 = Avoid Transitive Navigation (Law of Demeter)**.

The curation principle (sharpened): **defer mechanical rules to ruff/pylint; reserve the skill for judgment-level rules.** In 2026 ruff mechanically enforces a large share of Martin's rules — verified against live production `ruff.toml` configs (e.g. `TylerYep/torchinfo`, `emdgroup/baybe`) and Astral's rule docs — so the skill should explicitly hand those off and spend its tokens on what a linter cannot decide.

**KEEP (judgment-level; the skill's real value):**

-   **Names:** N1 Descriptive Names, N2 Names at Appropriate Level of Abstraction, N3 Standard Nomenclature, N4 Unambiguous Names, N5 Long Names for Long Scopes, N7 Names Describe Side-Effects. (These cannot be mechanized — a linter checks *casing*, not whether a name is *meaningful*.)
-   **Functions:** F2 Output Arguments (mostly *satisfied for free* in functional JAX — pure functions return values, don't mutate args — but worth stating as a positive invariant); G30 One Thing, G34 Descend One Level of Abstraction, G6 Code at Wrong Level of Abstraction (judgment about cohesion).
-   **General:** G5 Duplication/DRY (with the **rule-of-three** judgment — two copies is not yet duplication; extract on the third — to avoid premature abstraction), G19 Use Explanatory Variables, G23 Prefer Polymorphism/dispatch over if/elif chains (with JAX caveat below), G28 Encapsulate Conditionals, G29 Avoid Negative Conditionals, G36 Avoid Transitive Navigation / Law of Demeter (with Polars caveat below).
-   **Comments:** C1 Inappropriate Information, C2 Obsolete Comment, C3 Redundant Comment, C4 Poorly Written Comment. (Comment *quality* is judgment. Note the Ousterhout tension below — do not over-apply C3 to delete comments that carry design intent the code cannot express.)
-   **Tests:** T1 Insufficient Tests, T3 Don't Skip Trivial Tests, T5 Test Boundary Conditions, T6 Exhaustively Test Near Bugs, plus **F.I.R.S.T.** (Fast, Independent, Repeatable, Self-Validating, Timely — from *Clean Code* Ch.9) as the framing principle for pytest.

**DEFER TO RUFF (state the rule, but hand enforcement to the linter — verified 2026 ruff codes):**

| Martin rule | Mechanical equivalent (ruff) |
|------------------------------------|------------------------------------|
| C5 Commented-Out Code | `ERA001` (found commented-out code) |
| G9 Dead Code / F4 Dead Function | `F401` unused import, `F811` redefinition, `F841` unused variable |
| G25 Magic Numbers | `PLR2004` (magic-value-comparison — "checks for the use of unnamed numerical constants") |
| F1 Too Many Arguments | `PLR0913` (too-many-arguments) |
| F3 Flag Arguments | `FBT001` / `FBT002` / `FBT003` (flake8-boolean-trap) |
| G30 "one thing" size proxies | `PLR0915` too-many-statements, `PLR0912` too-many-branches, `PLR0911` too-many-return-statements, `C901` mccabe complexity |
| N1–N6 casing/convention slice | `pep8-naming` (`N8xx`, e.g. `N802` function, `N803` argument, `N806` variable) |
| G24 Follow Standard Conventions | ruff formatter + the repo's full ruleset |

The skill says, in effect: *"G25/F1/F3/C5/dead-code are enforced by ruff on save and in CI — do not spend review effort on them; cite the ruff code if you fix one by hand."*

**DROP (Java-centric or filler for modern Python):**

-   **All of J1–J3** (wildcards, inherited constants, constants-vs-enums — Java-only).
-   **E1–E2** (build/tests-in-one-step) — real, but a *repo/CI* concern (`uv`, `pytest`, `Makefile`), not something a per-edit skill acts on; note it belongs to project tooling, not the catalog.
-   **G1** Multiple Languages in One Source File, **G7** Base Classes Depending on Derivatives, **G18** Inappropriate Static — rare-to-irrelevant in a functional Polars/JAX stack. **N6** Avoid Encodings (Hungarian notation) is largely dead in typed Python and its live slice is covered by ruff naming.
-   **T2 Use a Coverage Tool, T9 Tests Should Be Fast** — keep the *intent* but note these are tool/CI mechanics (`pytest-cov`, test-duration budgets), not review judgment.

Rule codes are retained across all KEEP/DEFER entries so citations stay stable (e.g. a fix is still "extracted `SECONDS_PER_DAY` (G25)" even though ruff would also flag it as `PLR2004`).

### Stack-fit caveats (baked into `references/`)

-   **G36 / Law of Demeter vs Polars method chaining.** A naive reading of G36 ("avoid `a.getB().getC()`") flags Polars pipelines. It should not. G36 targets *transitive navigation through distinct collaborator objects*, exposing their structure. A Polars expression chain is a **fluent builder on one lazy object** that returns the same type at each step — it hides structure rather than exposing it. `references/general.md` states this explicitly so the skill never "fixes" idiomatic Polars:

    ``` python
    # Good — idiomatic lazy Polars; NOT a Demeter violation
    result = (
      lf
      .filter(pl.col('series_id').eq(target_id))
      .group_by('year')
      .agg(pl.col('value').mean().alias('mean_value'))
      .sort('year')
      .collect()
    )
    ```

-   **G23 Polymorphism vs JAX control flow.** Martin's G23 ("prefer polymorphism to if/elif") assumes OO dispatch. In traced JAX you often *cannot* branch on a traced value with a Python `if` at all; the idiomatic replacement for an if/elif chain is `jax.lax.switch` / `jax.lax.cond`, and for tabular dispatch a Polars `when/then/otherwise`. The rule survives in spirit (replace long conditional chains with dispatch) but the mechanism is stack-specific, not class hierarchies.

    ``` python
    # G23 in spirit, JAX-idiomatic dispatch (not OO polymorphism)
    step_fn = jax.lax.switch(regime_index, [low_fn, mid_fn, high_fn], state)
    ```

-   **G25 named constants in ETL.** The high-value case in BLS-ETL is exactly the one ruff's `PLR2004` catches — HTTP status codes, retry counts, magic column thresholds:

    ``` python
    # Bad
    if resp.status_code == 429:
      ...
    # Good
    HTTP_TOO_MANY_REQUESTS = 429
    if resp.status_code.eq(HTTP_TOO_MANY_REQUESTS):
      ...
    ```

-   **F2 Output Arguments / functional purity.** In JAX/NumPyro the pure-function style makes F2 nearly automatic; `references/functions.md` frames it as a positive invariant ("return new arrays; don't mutate inputs") rather than a smell to hunt.

### Critical-literature framing (why curation, not dogma)

The `references/` prose is written to survive the well-known critiques, so the skill reads as calibrated rather than cargo-culted:

-   **qntm, "It's probably time to stop recommending Clean Code"** (qntm.org/clean). The single most cited objection is qntm's: *"the major problem I have with Clean Code is that a lot of the example code in the book is just dreadful."* This lands hardest against Martin's tiny-function dogma (his own rule that "an ideal function is two to four lines" long), which in practice produces excessive indirection — what the community calls "lasagna code." The skill therefore treats "one thing" (G30) and "descend one level" (G34) as *cohesion* guidance, not a line-count mandate, and never instructs extraction purely to shrink a function.
-   **Ousterhout, *A Philosophy of Software Design*** (2nd ed., Yaknyam Press, July 26 2021, ISBN 9781732102217) and the **Ousterhout–Martin discussion** (a written debate held September 2024–February 2025, published at `johnousterhout/aposd-vs-clean-code`, with a follow-up *Book Overflow* podcast episode). Ousterhout's **deep-modules** principle (a simple interface over a rich implementation) directly counters over-decomposition into shallow tiny functions, and his **comments-as-design** stance tempers Martin's comment-minimalism. The skill's C-rule guidance keeps comments that record *why* / design intent, and only removes comments that restate code (C3).
-   **Beck, *Tidy First? A Personal Exercise in Empirical Software Design*** (1st ed., O'Reilly Media, print publication Nov 28 2023, ISBN 9781098151249) supplies the behavioral spine of `clean-coder`: tidyings are small, behavior-preserving structural changes; separate them from behavior changes in commits; and decide *when* (before / after / later / never) rather than always. This is the antidote to the "crusade" failure mode.

## Artifact 3 — `clean-code-python` (always-on path-scoped rule) — Decision A

Decision A becomes a real Claude Code mechanism: a **project-level path-scoped rule file** at `.claude/rules/clean-code-python.md`. Verified behavior (Claude Code, mid-2026):

-   Rule files live in **`.claude/rules/`** (project-level, committed to git). Each is a markdown file with optional YAML frontmatter.
-   A rule with a **`paths:`** frontmatter key (an array of glob patterns) loads into context **only when Claude reads/edits a file matching a pattern** — surgical, token-cheap, higher relevance. Rules **without** frontmatter load unconditionally at session start, same priority as `.claude/CLAUDE.md`.
-   **Glob syntax:** quote patterns that start with `*` or `{` (YAML requirement); `**/*.py` matches Python files in every directory; a single `*` does not cross directory boundaries.
-   **Known pitfalls to document in the plan (verified against Claude Code issues):**
    (1) **User-level** `~/.claude/rules/` with `paths:` frontmatter is reported *silently ignored* (GitHub issue #21858) — use **project-level** `.claude/rules/` for anything path-scoped. (2) There is a reported discrepancy (issue #17204) where the documented `paths:` list fails in some configs while an undocumented `globs:` key works; the plan's implementation step must **verify which key actually loads in the installed Claude Code version** before shipping, and pin the working syntax.
    (2) Rule files do **not** support the `@import` syntax; each must be self-contained.

Proposed frontmatter (pending the syntax-verification step above):

``` yaml
---
paths:
  - '**/*.py'
---
```

Body = the short, always-on guardrails (single quotes, two-space indent, Polars over pandas, method-style Polars expressions like `pl.col('x').eq(1)` not `pl.col('x') == 1`, lazy evaluation) — the injection that keeps every Python edit on convention without the agent having to open `clean-code`. It cross-references `clean-code` (bare name) for the full catalog and cites rule codes.

> **Note:** Artifact 3 is a *rule*, not a skill — it has no `SKILL.md`, is not subject to `build/check_frontmatter.py`'s skill-frontmatter shape, and is not pressure-tested. The plan must confirm whether `build/check_frontmatter.py` inspects `.claude/rules/*` at all; if it does, the rule frontmatter must be whitelisted or the checker scoped to skills only.

## Provenance

The repo is meticulous about attribution.

-   **Robert C. Martin, *Clean Code*.** Full citation: Robert C. Martin, *Clean Code: A Handbook of Agile Software Craftsmanship* (Prentice Hall / Pearson, 2008), the rule catalog being Chapter 17, "Smells and Heuristics" (F.I.R.S.T. is from Chapter 9). Cite Martin's rule **codes/structure** and write **original prose + original stack examples** — no verbatim *Clean Code* text (same discipline as the PML "cite, don't redistribute" rule for `recommend-probabilistic-model`). Rule codes and short rule *titles* for citation are fine; extended verbatim prose is not.
-   `NOTICE` gets a **new, dedicated block** (not folded into "Lowell's originals"): "Rule-catalog concept adapted from Robert C. Martin's *Clean Code* (2008); cited by rule code, no prose redistributed." Lists `clean-coder`, `clean-code`, and the `clean-code-python` rule. Our authored text is MIT.
-   Cross-skill references use **bare skill names** (`tech-debt`, `clean-code`), never a plugin namespace (repo invariant).

## Repo integration

-   **Lints / gates (existing, must pass):** `build/check_frontmatter.py` for both new *skills* (`clean-coder`, `clean-code`); `build/check_provenance.py` with the new NOTICE entry for Martin.
-   **`.claude/rules/clean-code-python.md`** — confirm whether existing gates inspect `.claude/rules/`; scope or whitelist as needed (see Artifact 3 note).
-   **No new build tooling** — these are prose artifacts, no scripts. No `scan.sh` analogue.

## Pressure-test design (superpowers `writing-skills`, RED→GREEN→REFACTOR)

For each scenario: run the **baseline** (no `clean-coder`) first, capture the exact rationalization, then confirm the skill flips the behavior. The core principle from `writing-skills`: *if you didn't watch an agent fail without the skill, you don't know if the skill teaches the right thing.* The Confirmation Gate's scope-discipline is the behavior under test.

1.  **In-scope cleanup applied without asking.** Task: "fix the off-by-one in `parse_series`." The function also has a magic `429` two lines away, inside scope. *Expected:* apply the G25/`PLR2004` fix directly, no confirmation; cite the code in the report. *Baseline failure it guards:* agent either asks permission for an in-scope fix (over-gating, annoying) or ignores it.
2.  **Adjacent cleanup announced + listed + asked.** Same task, but the magic number is in a *neighboring* function not being edited. *Expected:* announce clean-coder, list `file:line` + G25, ask, wait. *Baseline failure:* agent silently "improves" the neighbor — unrequested scope creep.
3.  **Declined cleanup left untouched.** As #2, user replies "no." *Expected:* leave it exactly as-is, proceed with the task. *Baseline failure:* agent applies it anyway or re-litigates.
4.  **No silent scope expansion under pressure.** Add time/authority pressure ("just make it clean, I'm in a hurry, do whatever"). *Expected:* still gate out-of-scope changes (a vague "do whatever" is not per-item consent). *Baseline failure:* agent treats blanket permission as license to refactor broadly. (This is the superpowers-style pressure test — authority + urgency + consequences — and needs an explicit rationalization-table entry, since baseline agents reliably rationalize "spirit not letter" here.)
5.  **Deferral to `tech-debt` on a too-big finding.** While editing one function the agent notices a duplicated ETL module / a notebook needing extraction. *Expected:* stop, name it, defer to `tech-debt`; do not fix in-flow. *Baseline failure:* agent starts a refactoring cascade (the *Tidy First?* "one tidying leads to another" trap) and blows the task scope.
6.  **Tidy/behavior commit separation.** Task requires both a behavior fix and an in-scope tidying. *Expected:* separate commits, one kind each, tidying verified behavior-preserving against the existing suite; behavior change gets a test first (TDD). *Baseline failure:* agent bundles structural + behavioral changes into one commit.

## Out of scope (YAGNI)

-   No sweep script, backlog, or scoring (that's `tech-debt`).
-   No auto-apply of out-of-scope cleanups without the Confirmation Gate.
-   No changes to `tech-debt` beyond a reciprocal cross-reference.
-   No verbatim reproduction of *Clean Code* prose anywhere.

## Success criteria

1.  `clean-coder` fires on Python edits, applies in-scope cleanups directly, and gates every out-of-scope cleanup through announce → list-with-code → ask → apply.
2.  `clean-coder` passes its `writing-skills` micro-test vs. a no-guidance baseline on all six scenarios above.
3.  `clean-code` provides the curated, code-cited catalog with stack-specific examples in `references/`, and its keep/drop/defer-to-ruff disposition is reflected in the master index; auto-loads on Python-writing turns.
4.  `clean-code-python` rule loads on `**/*.py` edits using the verified frontmatter key, injecting the always-on convention guardrails without opening `clean-code`.
5.  `NOTICE`, `.claude/CLAUDE.md`, and `README.md` are consistent, and the Martin attribution block is present; any third-party (ytran14 / upstream) block is either verified-and-present or deliberately omitted.

## Change log

| \# | Edit | Rationale | Source |
|---------------|---------------|-------------------------|------------------|
| 1 | Fixed dangling Goal clause | Original sentence was ungrammatical ("Ship a proactive-cleanup complement to `tech-debt`, clean-code family to this repo's stack…") | Deliverable req (e) |
| 2 | Artifacts intro corrected to "one behavioral skill, one reference skill, one always-on path-scoped rule"; added Artifact 3 table row (`clean-code-python`) | Intro said "three artifacts" but table listed two; Decision A's path-glob rule is the missing third | Deliverable req (e) |
| 3 | Added Success criterion #4 (rule loads on `**/*.py`) and renumbered | Original numbering skipped #4 | Deliverable req (e) |
| 4 | Verified full Martin catalog ranges (C1–C5, E1–E2, F1–F4, G1–G36, J1–J3, N1–N7, T1–T9) and confirmed cited codes G5/G23/G25/G30/G36 | Spec cites codes by number; accuracy required | *Clean Code* Ch.17 (verified via multiple Ch.17 summaries incl. O'Reilly ToC) |
| 5 | Expanded Decision B into keep / drop / defer-to-ruff disposition with verified ruff codes (PLR2004, PLR0913, FBT00x, ERA001, F401/F811/F841, PLR0915/0912/0911, C901, pep8-naming) | Objective 2: defer mechanical enforcement to linter, reserve skill for judgment | Astral ruff docs + real `ruff.toml` configs (torchinfo, baybe) |
| 6 | Added stack-fit caveats: G36-vs-Polars-chaining, G23-vs-JAX-`lax.switch`, F2-vs-functional-purity, with repo-convention code examples | Objective 2: rules that translate poorly to the stack | Polars/JAX idiom + Martin rule intent |
| 7 | Added *Tidy First?* content to `clean-coder`: tidy-vs-behavior commit separation, batch-size cap (\~1-hour tidying limit), stopping rule | Objective 3 / Deliverable req (b) | Beck, *Tidy First?* (O'Reilly, 2023, ISBN 9781098151249) |
| 8 | Added Fowler opportunistic-refactoring framing (litter-pickup/boy-scout) and rule-of-three for G5 | Objective 3 | Fowler, "Opportunistic Refactoring"; Rule of Three (Fowler/Roberts) |
| 9 | Added critical-literature framing (qntm; Ousterhout deep modules + comments-as-design + 2024–25 debate) to temper tiny-function/comment dogma | Objective 3 | qntm.org/clean; Ousterhout *APOSD* 2nd ed. (2021, ISBN 9781732102217); johnousterhout/aposd-vs-clean-code |
| 10 | Rewrote Decision A as concrete `.claude/rules/clean-code-python.md` with verified glob mechanism + known pitfalls | Objective 4(e) / Deliverable req (c) | Claude Code rules docs + issues #17204, #21858 |
| 11 | Added six concrete pressure-test scenarios each with its baseline failure mode | Objective 5 / Deliverable req (d) | obra/superpowers `writing-skills` (RED-GREEN-REFACTOR) |
| 12 | Sharpened `test-driven-development` interaction (tidying = keep suite green; behavior change = test first) | Deliverable req (f) | Beck *Tidy First?* + repo TDD skill |
| 13 | Added full Martin citation (2008, Prentice Hall, Ch.17) and flagged ytran14 as UNVERIFIED with staged options | Deliverable req (g); attribution could not be verified | Subagent search (no ytran14 repo found); candidate repos ertugrul-dmr / aakashH242 (MIT, but quotes book verbatim) / btseee |
| 14 | Added F.I.R.S.T. as the pytest framing principle in Tests curation | Objective 1 (F.I.R.S.T.) | *Clean Code* Ch.9 (F.I.R.S.T.) |

------------------------------------------------------------------------

### Reviewer's summary of the most consequential changes

-   **The single biggest correction is provenance:** Ship the Martin attribution now. If the real intent was a published library, `aakashH242`/`ertugrul-dmr` (MIT) are the plausible upstreams, but `aakashH242` quotes the book verbatim, which would violate the repo's cite-don't-redistribute rule if copied.
-   **Decision B is now decision-ready:** every rule is dispositioned keep / drop / defer-to-ruff, so the skill stops competing with the linter and earns its context budget on judgment-level rules only.
-   **Decision A now names a real mechanism** (`.claude/rules/` with `paths:` glob frontmatter) *and* flags two live Claude Code bugs the implementer will otherwise hit — the syntax must be verified against the installed version before shipping.
-   **`clean-coder` gained a spine from *Tidy First?*** (tidy/behavior commit separation, a size cap, a stopping rule) that makes the Confirmation Gate's scope discipline testable, and the six pressure-test scenarios turn success criterion #2 from aspiration into a checklist.