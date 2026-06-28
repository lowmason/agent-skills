# Design — `recommend-probabilistic-model` skill

> **Status:** ✅ Completed — shipped and merged to `main` 2026-06-21 (PR #1, merge `466a9d2`).

-   **Date:** 2026-06-21
-   **Status:** Approved (brainstorm) — pending spec review → `writing-plans`
-   **Author:** Lowell Mason
-   **Repo:** `agent-skills`

## Summary

A Claude Code skill that, given a **modeling problem** and (optionally) **the data that supports it**, diagnoses the task, characterizes the data, and produces a **recommendation memo**: 2–3 candidate methods with trade-offs, a defensible default *with reasons*, exact citations into Kevin Murphy's *Probabilistic Machine Learning* books (Book 1 *An Introduction*, Book 2 *Advanced Topics*), links to the matching [`pyprobml`](https://github.com/probml/pyprobml) notebooks, and a structured handoff.

It is an **advisor / selector**: it recommends and points. It does **not** fit, evaluate, or report on a fitted model — that is `bayesian-workflow`'s job (or the user's, for non-Bayesian methods).

## Decisions (from brainstorming)

| \# | Decision | Choice |
|----------------|-------------------------------|-------------------------|
| 1 | **Scope** | Advisor / selector — emit a recommendation memo + persisted artifact; no execution. |
| 2 | **Knowledge representation** | Hybrid — curated static *decision map* for the common cases + a documented *drill-down* procedure for the long tail. |
| 3 | **Coverage** | Tiered — full breadth at the method-family level (every problem routes somewhere) + curated depth in the user's high-frequency areas. |
| 4 | **Input contract** | Adaptive — data-aware when a dataset is present (reuse `explore-data` profiling); falls back to problem-only. Also treats **external/auxiliary data** (official statistics, benchmarks, related series, domain constraints) as a first-class input that informs priors / pooling / structure. |
| — | **Name** | `recommend-probabilistic-model` |
| — | **Attribution** | Books are **CC-BY-NC-ND** (see Licensing). Ship *summarized* method knowledge (original wording) + §refs; link `pyprobml` (MIT); never reproduce book prose or bundle the PDFs. |
| — | **Performance/size** | Skill stays small and fast: ships only markdown references + a thin script; the common runtime path touches **no PDFs** (see Performance & size model). |

### Depth tiers (decision #3, expanded 2026-06-21)

**Deep curated detail** (specific §refs, defaults, gotchas, notebook links) — **eight families**:

1.  **Regression, GLMs & count models** — linear/robust regression; Poisson / NegativeBinomial / zero-inflated / hurdle; ordinal.
2.  **Hierarchical / multilevel** — partial pooling, varying intercepts/slopes, non-centering.
3.  **Time series & state-space** — structural time series, Kalman / Gaussian filtering & smoothing, HMMs.
4.  **Gaussian processes.**
5.  **Dimensionality reduction & factor models** — PCA, factor analysis, PPCA, and **dynamic factor models** (multi-indicator nowcasting).
6.  **Classification & discriminative models** — logistic / softmax, discriminant analysis, naive Bayes, trees / boosting / ensembles.
7.  **Mixture & latent-variable models / clustering** — GMMs, EM, latent class; regime / break / segment detection.
8.  **Probabilistic graphical models (broadly)** — representation + inference; **structure learning** (Bayes-net structure, Gaussian graphical models / sparse precision / graphical lasso); and **graph neural networks**.

> **Model selection & regularization is *not* a family** — it is a **cross-cutting concern** applied *within* whichever family is chosen (e.g. # factors, K components, kernel/ARD, sparsity prior, structure penalty; partial pooling *is* the regularizer for hierarchical models). It is handled as a dedicated **procedure step** (Step 6, conditional on the chosen family) backed by a shared reference `references/model-selection-regularization.md` (general CV / IC / LOO-ELPD theory + a per-family knobs table). The *post-fit* LOO/ELPD comparison remains `bayesian-workflow`'s job; this skill does the *pre-fit* specification.

**Route-only → drill-down** (family pointer, no curated depth yet): reinforcement learning & sequential decision-making, deep generative models (VAEs / GANs / diffusion / normalizing flows), deep-learning architectures & training beyond the discriminative basics, advanced kernel methods beyond GP, nonparametric Bayes (e.g. Dirichlet processes), pure optimization methods, and causal inference (candidate for later promotion).

## Boundaries — this skill vs. its siblings

Stated explicitly in `SKILL.md` (matching the repo's existing "this vs. siblings" blocks):

-   `explore-data` **discovers** the data's shape (upstream).
-   **`recommend-probabilistic-model`** turns *shape × task* into a modeling **decision**.
-   `bayesian-workflow` **executes** when the recommendation is "fit a Bayesian model."
-   `bls-data-context` supplies **official-statistics / benchmark data** that informs priors & pooling.
-   `validate-data` **gates** the downstream result.

## Architecture

```         
recommend-probabilistic-model/
  SKILL.md                      # hub: when-to-use, boundaries, the 8-step procedure,
                                #   which-book rule, handoff interface
  references/
    decision-map.md             # THIN ROUTER: (task × data signal) → family →
                                #   pointer to families/<x>.md + §ref + notebook
    families/                   # per-family DEEP detail (one file per deep family — 8)
      regression-glm.md         #   summaries, defaults, gotchas, §refs, notebooks
      hierarchical.md
      timeseries-statespace.md
      gaussian-processes.md
      factor-models.md          #   dim. reduction + dynamic factor models
      classification.md
      mixtures-clustering.md
      graphical-models.md       #   PGM repr/inference + structure learning + GNNs
    model-selection-regularization.md  # CROSS-CUTTING (Step 6): general CV/IC/LOO
                                #   theory + per-family knobs table; NOT a family
    pyprobml-index.md           # chapter/§ → VERIFIED pyprobml notebook paths/URLs
    drill-down.md               # long tail: Book 1 via Read; Book 2 via pdftotext/
                                #   pdftoppm; grep pyprobml; how to cite
    external-data-and-priors.md # official stats / benchmarks / domain knowledge →
                                #   informative priors, pooling targets, covariates,
                                #   constraints (bridges bls-data-context + bayesian-workflow)
    reporting.md                # canonical recommendation.md template = the handoff interface
  scripts/
    characterize.py             # THIN: only modeling-relevant signals explore-data omits
```

**Anti-overbuild guardrails (do not violate without evidence):**

-   `taxonomy.md` stays **folded into** `decision-map.md` — the router table *is* the catalog; no separate taxonomy file.
-   **Per-family depth files (`families/*.md`) are justified by the eight-family deep tier** — this is the one split the expanded coverage now warrants. The split is **reversible**: if a family proves thin at build time, fold it back into the router. Do **not** create files for route-only (drill-down) families. `model-selection-regularization.md` is a **cross-cutting** reference, not a `families/` file.
-   `decision-map.md` stays a **thin router** (one scannable table); depth lives in `families/*.md` and loads on demand. The runtime common path reads the router + at most one or two family files (+ the cross-cutting selection ref when relevant), never all eight.
-   `characterize.py` stays **thin** — only modeling-relevant signals `explore-data`'s `profile.py` does *not* already emit (var/mean ratio, zero fraction, n/p ratio, group cardinality, class balance, a basic stationarity/trend hint). If `explore-data` already covers what's needed, **drop the script** and call `explore-data` instead.

## The recommendation procedure (SKILL.md core)

1.  **Frame the problem.** Task type (supervised regression / classification / ordinal / counts / survival; unsupervised clustering / dim-reduction / density; structured time-series / spatial / graph; decision / RL) **and the question being asked** (point prediction vs. uncertainty / inference vs. causal vs. sequential decision).
2.  **Characterize the data.** Profile the primary dataset (reuse `explore-data`; `characterize.py` for modeling signals). **Inventory external/auxiliary information** — official statistics, benchmarks, related series, published aggregates, domain constraints — as candidate informative priors / pooling targets / covariates / hard constraints.
3.  **Route via the decision map.** Match (task × data signals) to candidate method families; pull §refs + pyprobml notebooks. For the long tail, use `drill-down.md`.
4.  **Weigh 2–3 candidates.** Trade-offs: assumptions, fit to the observed data, uncertainty handling, compute cost, interpretability — grounded in the profile, not generic.
5.  **Recommend a default + WHY.** Explicit assumptions; state how external data informs priors / pooling / structure.
6.  **Specify regularization & model selection (conditional on the chosen family).** Only now that a family is fixed: surface *its* complexity-control knobs and the selection strategy to plan — e.g. # factors (factor models), K components (mixtures), kernel / ARD / lengthscale priors (GP), sparsity prior (ridge/lasso/horseshoe) & which predictors (regression/GLM), structure penalty / graphical-lasso λ (graphical models); partial pooling *is* the regularizer for hierarchical models. Name the intended selection criterion (CV / IC / LOO-ELPD). See `references/model-selection-regularization.md`. This is *pre-fit specification* — the *post-fit* LOO/ELPD comparison is `bayesian-workflow`'s job.
7.  **Point & hand off.** Exact §refs + pyprobml links + the handoff payload (see Handoff interface).
8.  **Persist.** Write `<slug>/recommendation.md` from the `reporting.md` template (audit trail, mirroring `bayesian-workflow`'s `report.md`).

## Decision-map entry shape

Two layers. The **router** (`decision-map.md`) is thin and scannable; the **per-family files**
(`families/*.md`) carry the depth.

**Router row** (`decision-map.md`) — keyed on **task × data signal(s)**, just enough to dispatch:

-   the **observed signal** that selects a family (e.g. `var ≫ mean` → NegativeBinomial over Poisson; `zero fraction high` → zero-inflated/hurdle; `group columns present` → hierarchical; `many correlated indicators` → factor models),
-   the **target family** + a **pointer** to its `families/<x>.md`,
-   a primary **§ref** + **pyprobml notebook** for the fast common case.

**Per-family entry** (`families/<x>.md`) — the curated depth for each candidate method:

-   a **1–2 line summary** of what the method is and when to use it — *original wording* (my synthesis, not book prose), so the common path is self-contained and needs no PDF access at runtime,
-   **Book 1 §ref** (standard treatment) and **Book 2 §ref** (advanced/extended) where both exist (C3),
-   the verified **pyprobml notebook(s)**,
-   the **default recommendation** + a one-line rationale, and key **gotchas**,
-   a **Selection & regularization** subsection — *this family's* complexity knobs + the criterion to use (Step 6), specializing the cross-cutting `model-selection-regularization.md`,
-   the **handoff target** (`bayesian-workflow`, sklearn/other, or drill-down).

## Performance & size model

The skill must stay **small and fast**. PDFs are never carried by or searched on every call. There are three phases, and only the common runtime path is hot:

| Phase | When | Touches PDFs? | Cost |
|---------------|---------------|----------------------------|---------------|
| **Build** | Once, offline, on the author's machine | Yes — extract to gitignored scratch, synthesize map, verify citations | One-time; irrelevant to shipped skill |
| **Runtime — common path (\~80–90%)** | Most calls | **No** | Read a few KB of markdown, match a row, emit memo |
| **Runtime — drill-down (rare tail)** | Off-map problems only | Optional, *targeted* `pdftotext -f N -l M` on a page range **if** PDFs are local; else pyprobml/public TOC | Bounded; never a full-book scan |

**Shipped footprint:** markdown references (target: tens of KB total) + one thin script. **No PDFs, no vendored books, no document index.** Same shape as `bls-data-context` (hub + small references).

**Design implications:** - The curated map's *summarized knowledge* must be rich enough that the common path needs **zero** PDF access — recommendations come from the shipped markdown alone. - The tiered-breadth decision (#3) guarantees every problem routes *somewhere* statically, so drill-down (the only PDF-touching runtime branch) stays the exception. - `.gitignore` the build-scratch dir so extracted book text can never be committed.

## Construction constraints (enforced during the build)

-   **C1 — Verified-source rule.** Every §ref and notebook link is verified against the actual source before it ships — **never written from recall**. A plausible-but-wrong citation is worse than no citation. (Same adversarial discipline as the repo's snippet-verification work.)
-   **C2 — Book 2 access (proven 2026-06-21).** Book 2's PDF (`prob_ml_book.pdf`, 144 MB / 1370 pp) **exceeds the Read tool's 100 MB text-extraction cap**. Access it via poppler:
    -   `pdftotext -f N -l M prob_ml_book.pdf out.txt` for text (TOC, section content),
    -   `pdftoppm -png -f N -l M -r 120 prob_ml_book.pdf out` for figures/equations.
    -   **Ruled out:** naive `pdfseparate`+`pdfunite` splitting — it duplicates shared fonts/images per page and produced a **180 MB** file from 20 pages (larger than the source). Do not use it.
    -   Book 1 (`prob_ml_1-book.pdf`, 88 MB) and the supplementary (12 MB) read fine via the Read tool or `pdftotext`.
-   **C3 — Which-book routing.** Topics covered in both books (GPs, hierarchical models, mixtures): **Book 1 = standard treatment** (default pointer); **Book 2 = advanced/extended** (point when the problem needs the extension). Every dual-coverage entry names both.
-   **C4 — Handoff interface.** For a Bayesian recommendation, the memo must carry what `bayesian-workflow` needs to start cold: **likelihood family, candidate priors (incl. any derived from official statistics / external data), structure** (pooling / hierarchy / temporal), **and the regularization & model-selection plan** (family-specific complexity knobs + intended selection criterion, from Step 6). This is the well-defined interface between the two skills; it is specified in `reporting.md`.
-   **C5 — pyprobml index** is built from a **real repo listing** (`gh api` / shallow clone), not from URLs constructed off chapter numbers. Notebook paths do not map 1:1 to sections.
-   **C6 — Attribution & licensing (verified 2026-06-21 from primary sources).**
    -   **Books (Book 1 © 2022 MIT; Book 2 © 2023 K. P. Murphy) are licensed CC-BY-NC-ND.** The **ND (NoDerivatives)** clause permits redistributing *verbatim* copies (attributed, non-commercial) but **forbids distributing derivatives/adaptations** — extracting/reformatting the prose into committed markdown is a prohibited derivative. ND restricts *distribution*, not *use*: local extraction for our own analysis (the build) is fine. Short, attributed *quotations* are fair use. → Ship **summarized** method knowledge in original wording + §refs. Reproduce no book prose; bundle no PDFs.
    -   **`pml-book` repo materials** (figures, in-repo per-chapter supplement `.md`s, `solns-public.pdf`, `toc1.pdf`, `preface1.pdf`) are **MIT** — redistributable with attribution if ever needed (not vendored under the chosen approach; referenced by link).
    -   **`pyprobml`** (notebooks/code) is **MIT** — link (or vendor with attribution) freely.
    -   Update `NOTICE` / `README` to record: books cited under CC-BY-NC-ND; `pyprobml`/`pml-book` materials linked under MIT.

## Source materials (local + remote)

| Source | License | Role | Shipped? |
|-----------------|------------------|-----------------|---------------------|
| `prob_ml_1-book.pdf` (Book 1) | CC-BY-NC-ND | build-time citation source; rare runtime drill-down | **No** |
| `prob_ml_book.pdf` (Book 2, 144 MB) | CC-BY-NC-ND | same; access via `pdftotext`/`pdftoppm` (C2) | **No** |
| `prob_ml_1-solutions.pdf`, `prob_ml_2-supplementary.pdf` | book-family (treat CC-BY-NC-ND) | optional context, cite/link | **No** |
| `pml-book` repo (figures, supp `.md`, `solns-public.pdf`, `toc1.pdf`) | MIT | referenced by link | **No** (linked) |
| `pyprobml` notebooks | MIT | linked from the index | **No** (linked) |

-   Local PDF path on the user's machine: `~/Documents/Bayesian/Probabilistic Machine Learning/`.
-   The skill must **not** hard-depend on those local paths at runtime. The curated map (with summarized knowledge + §refs) is the runtime source of truth; `drill-down` treats the local PDFs as *optional* resources and falls back to `pyprobml` / the public TOC when they're absent.

## Reporting template (`recommendation.md` = handoff interface)

Canonical sections (the C4 interface lives here):

1.  **Problem framing** — task type + question.
2.  **Data characterization** — primary-data signals + external/auxiliary inventory.
3.  **Candidate methods** — 2–3, with trade-offs.
4.  **Recommendation** — default + why; explicit assumptions.
5.  **Regularization & model selection** — family-specific complexity knobs + intended selection criterion (Step 6).
6.  **Specification for handoff** — likelihood family, candidate priors (incl. external-data-derived), structure (pooling/hierarchy/temporal), and the regularization/selection plan from §5.
7.  **References** — verified PML §refs + pyprobml notebook links.
8.  **Next steps / handoff** — which skill or tool runs next.

## Build approach (after spec approval, via `writing-plans`)

The heavy labor — extracting both books' section structure, mapping `pyprobml`, drafting the references, and **verifying every citation** — fits a **Workflow fan-out**:

-   parallel agents extract per-part / per-chapter structure (Book 1 via Read/`pdftotext`; Book 2 via `pdftotext`/`pdftoppm`),
-   parallel agents map `pyprobml` notebooks from the real repo listing,
-   **one agent per deep family (eight)** drafts its `families/<x>.md` (incl. its Selection & regularization subsection) from the extracted structure,
-   one agent drafts the cross-cutting `model-selection-regularization.md` (general CV/IC/LOO criteria + the per-family knobs table),
-   an adversarial verify stage confirms each §ref and notebook link resolves (C1),
-   a synthesis stage assembles the thin `decision-map.md` router over the eight family files.

This stays behind the brainstorming gate until the spec is approved.

## Out of scope (YAGNI)

-   Fitting, evaluating, or reporting on a fitted model (→ `bayesian-workflow` or the user).
-   A separate `taxonomy.md` (the router table is the catalog). *Per-family `families/*.md` files are now IN scope* — the eight-family deep tier is the evidence that forced the split; route-only families get no file.
-   Bundling the PDFs or any copyrighted prose.
-   A general data profiler (reuse `explore-data`).

## Open questions / risks

-   **R1 — Citation drift.** Books and `pyprobml` update; §refs and notebook paths can go stale. Mitigation: cite by section number + title (stable-ish) and record the verification date; keep `drill-down` as the live fallback.
-   **R2 — Coverage honesty.** Until Book 2 curation is actually done and verified, the skill must not *claim* curated Book 2 coverage it doesn't have. The route-only tier is the honest default.